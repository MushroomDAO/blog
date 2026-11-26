"""One native MiniCPM duplex session per GPU, with a real asynchronous backend."""

import argparse
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import json
import logging
import os
import random
from pathlib import Path
import time
import uuid
from collections import deque

import httpx
import numpy as np
import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from sage_demo.protocol import (
    configuration,
    delegate_query,
    ask_backend,
    tool_event,
)
from sage_demo.audio_input import MicrophoneNoiseFilter, PlaybackEchoGuard
from sage_demo.query_routing import SpokenQueryRouter, browser_event

from sage_demo.model import NativeDuplexModel
from sage_demo.streaming_actions import (
    align_voice_prefill,
    configure_speech_completion,
    generate_control_action,
    inject_tool_result,
    observe_tts_termination,
    reset_speech_turn,
)

LOG = logging.getLogger("online.inference")


class SpeechOnset:
    """CPU WebRTC speech onset with a voiced window and silence hysteresis."""

    def __init__(self, cfg):
        import webrtcvad

        self.vad = webrtcvad.Vad(cfg["vad_mode"])
        self.minimum_ms = cfg["vad_min_voiced_ms"]
        self.silence_limit = cfg["vad_end_silence_ms"]
        self.energy_floor = cfg["vad_min_rms"]
        self.window = deque(maxlen=10)
        self.active = False
        self.silence_ms = 0
        self.utterance_id = 0

    def process(self, waveform, echo_frames=None):
        started = time.monotonic()
        pcm = (np.clip(waveform, -1, 1) * 32767).astype("<i2")
        onset, voiced_ms, echo_voiced_ms = False, 0, 0
        for offset in range(0, len(pcm), 320):
            frame = pcm[offset : offset + 320]
            if len(frame) != 320:
                break
            else:
                rms = float(np.sqrt(np.mean((frame.astype(np.float32) / 32768) ** 2)))
            voiced = (
                self.vad.is_speech(frame.tobytes(), 16000) and rms >= self.energy_floor
            )
            if echo_frames is not None and echo_frames[offset // 320] and voiced:
                voiced = False
                echo_voiced_ms += 20
            self.window.append(20 if voiced else 0)
            voiced_ms += 20 if voiced else 0
            self.silence_ms = 0 if voiced else self.silence_ms + 20
            if not self.active and sum(self.window) >= self.minimum_ms:
                self.active = True
                self.utterance_id += 1
                onset = True
            elif self.active and self.silence_ms >= self.silence_limit:
                self.active = False
                self.window.clear()
        return dict(
            speech_started=onset,
            speech_active=self.active,
            utterance_id=self.utterance_id,
            voiced_ms=voiced_ms,
            trailing_silence_ms=self.silence_ms,
            detector="webrtcvad",
            echo_voiced_ms=echo_voiced_ms,
            cpu_seconds=round(time.monotonic() - started, 6),
        )


class VoiceEngine:
    def __init__(self, cfg):
        import torch

        torch.set_num_threads(4)
        if cfg.get("frontend_seed") is not None:
            random.seed(cfg["frontend_seed"])
            np.random.seed(cfg["frontend_seed"])
            torch.manual_seed(cfg["frontend_seed"])
            torch.cuda.manual_seed_all(cfg["frontend_seed"])
        self.model = NativeDuplexModel(
            cfg["frontend_model"], cfg["tts_base_model"], cfg["prompt_wav"]
        )
        base = self.model._base_model
        modules = dict(
            llm=base.llm,
            tts=base.tts,
            audio_encoder=base.apm,
            vocoder_flow=base.tts.audio_tokenizer.flow,
            vocoder_hift=base.tts.audio_tokenizer.hift,
        )
        actual_dtypes = {
            name: sorted(
                {
                    str(parameter.dtype)
                    for parameter in module.parameters()
                    if parameter.is_floating_point()
                }
            )
            for name, module in modules.items()
        }
        self.runtime_details = dict(
            parameter_dtypes=actual_dtypes,
            cuda_allocated_gib=round(torch.cuda.memory_allocated() / 2**30, 3),
            cuda_reserved_gib=round(torch.cuda.memory_reserved() / 2**30, 3),
        )
        LOG.info(
            "Loaded native model %s: %s", cfg["frontend_model"], self.runtime_details
        )
        self.cfg = cfg
        self.prompt = Path(cfg["frontend_prompt_file"]).read_text()
        self.add_timestamps = bool(cfg["frontend_add_timestamps"])
        self.tts_calls = 0
        self.session_generation = 0
        self.pcm_callback = None
        self.pcm_context = None
        self.step_tts_calls = []
        self.step_codec_calls = []
        self.step_codec_waveforms = []
        native_tts = self.model._base_model.tts.generate_chunk

        def _tts(*args, **kwargs):
            if cfg.get("tts_seed") is not None:
                with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
                    torch.cuda.manual_seed(cfg["tts_seed"] + self.tts_calls)
                    tokens, cache, termination = observe_tts_termination(
                        base.tts, native_tts, *args, **kwargs
                    )
            else:
                tokens, cache, termination = observe_tts_termination(
                    base.tts, native_tts, *args, **kwargs
                )
            self.step_tts_calls.append(
                dict(
                    call_index=self.tts_calls,
                    language_turn_ended=bool(self.model._duplex.current_turn_ended),
                    speech_token_ids=tokens.detach().cpu().reshape(-1).tolist(),
                    **termination,
                )
            )
            self.tts_calls += 1
            return tokens, cache

        self.model._base_model.tts.generate_chunk = _tts
        configure_speech_completion(self.model._duplex, cfg["tts_final_max_tokens"])
        codec = base.tts.audio_tokenizer
        native_stream = codec.stream

        def _stream(*args, **kwargs):
            return_waveform = kwargs.pop("return_waveform", False)
            raw = native_stream(*args, **kwargs, return_waveform=True)
            waveform = np.asarray(raw, dtype=np.float32).reshape(-1)
            self.step_codec_waveforms.append(waveform.copy())
            self.step_codec_calls.append(
                dict(
                    samples=int(waveform.size),
                    finite=bool(np.isfinite(waveform).all()),
                    peak=float(np.max(np.abs(waveform))) if waveform.size else 0.0,
                    outside_pcm_range=int(np.count_nonzero(np.abs(waveform) > 1)),
                    last_chunk=bool(kwargs.get("last_chunk", False)),
                )
            )
            if return_waveform:
                return raw
            else:
                pcm = (np.clip(raw, -1, 1) * 32767).astype("<i2").tobytes()
                if self.pcm_callback is not None:
                    duplex = self.model._duplex
                    if self.pcm_context is None:
                        ids = [int(item[0]) for item in duplex.total_hidden[-1]]
                        self.pcm_context = dict(
                            action="speak",
                            text=duplex.tokenizer.decode(ids, skip_special_tokens=True),
                            end_of_turn=bool(duplex.current_turn_ended),
                            speech_complete=False,
                        )
                    # Non-final short output receives native left-padding only after all codec calls.
                    if self.pcm_context["end_of_turn"] or len(pcm) >= self.cfg.get(
                        "subchunk_min_bytes", 38400
                    ):
                        self.pcm_callback(
                            np.frombuffer(pcm, dtype="<i2").astype("<f4") / 32768,
                            dict(self.pcm_context),
                            time.monotonic(),
                        )
                return pcm

        codec.stream = _stream
        self.runtime_details.update(
            batch_size=1,
            model_owner_pid=os.getpid(),
            decoder_class=type(self.model._duplex.decoder).__name__,
            flow_owner_id=id(codec.flow),
            tts_final_max_tokens=cfg["tts_final_max_tokens"],
            tts_temperature=float(self.model._duplex.tts_temperature.item()),
            cache_policy="one_model_one_serial_session_fresh_prepare",
        )
        self.native_prefill = self.model._duplex.streaming_prefill
        self.native_feed = self.model._duplex.decoder.feed

    def begin(self):
        import torch

        started = time.monotonic()
        with torch.inference_mode():
            if self.cfg.get("frontend_seed") is not None:
                random.seed(self.cfg["frontend_seed"])
                np.random.seed(self.cfg["frontend_seed"])
                torch.manual_seed(self.cfg["frontend_seed"])
                torch.cuda.manual_seed_all(self.cfg["frontend_seed"])
            self.tts_calls = 0
            base = self.model._base_model
            base.audio_past_key_values = None
            tokenizer = base.tts.audio_tokenizer
            tokenizer.cache, tokenizer.stream_cache, tokenizer.hift_cache_dict = (
                None,
                None,
                {},
            )
            prompt_started = time.monotonic()
            self.model.begin(self.prompt)
            base.audio_past_key_values = None
            torch.cuda.synchronize()
            prompt_seconds = time.monotonic() - prompt_started
            self.native_prefill = self.model._duplex.streaming_prefill
            self.native_feed = self.model._duplex.decoder.feed
            align_voice_prefill(
                self.model._duplex, self.model._duplex.tokenizer, self.add_timestamps
            )
            self.session_generation += 1
            self.runtime_details["session_generation"] = self.session_generation
        self.runtime_details["session_initialization"] = dict(
            system_and_voice_prefill_seconds=round(prompt_seconds, 4),
            total_seconds=round(time.monotonic() - started, 4),
        )

    def step(self, waveform, text, deliveries, interrupt_speech=False):
        import torch

        duplex = self.model._duplex
        step_started = time.monotonic()
        self.pcm_context = None
        input_rms = float(np.sqrt(np.mean(waveform**2)))
        self.step_tts_calls, self.step_codec_calls, self.step_codec_waveforms = (
            [],
            [],
            [],
        )
        with torch.inference_mode():
            if interrupt_speech:
                reset_speech_turn(duplex, close_language_turn=True)
            for delivery in deliveries:
                inject_tool_result(duplex, delivery["event"], batch=True)
            if text:
                result = self.native_prefill(text_list=[text], max_slice_nums=1)
                if not result.get("success"):
                    raise RuntimeError(f"Native text prefill failed: {result}")
            result = duplex.streaming_prefill(audio_waveform=waveform)
            if not result.get("success"):
                raise RuntimeError(f"Native audio prefill failed: {result}")
            else:
                started = time.monotonic()
            mel = duplex.processor._streaming_mel_processor
            stream = dict(
                mel.get_state(),
                pending_waveform_samples=len(duplex.audio_buffer),
                audio_unit=duplex.audio_chunk_idx,
                prefill_costs={
                    key: round(value, 5)
                    for key, value in result.items()
                    if key.startswith("cost_")
                },
            )
            output = generate_control_action(
                duplex,
                duplex.streaming_generate,
                dict(
                    prompt_wav_path=self.cfg["prompt_wav"],
                    max_new_speak_tokens_per_chunk=self.cfg["max_new_speak_tokens"],
                    decode_mode="greedy",
                    temperature=0.0,
                    top_k=100,
                    top_p=1.0,
                ),
                self.cfg["max_delegate_query_tokens"],
                allow_interruption=self.cfg["allow_speech_interruption"],
                native_action_policy=True,
            )
            generated = time.monotonic()
            audio = output.pop("audio_waveform", None)
            if audio is not None:
                audio = (
                    audio.detach().float().cpu().numpy()
                    if isinstance(audio, torch.Tensor)
                    else np.asarray(audio)
                )
                audio = np.asarray(audio, dtype="<f4").reshape(-1)
                if not np.isfinite(audio).all():
                    raise RuntimeError("Native TTS produced nonfinite samples")
            return dict(
                action=output.get(
                    "action", "listen" if output["is_listen"] else "speak"
                ),
                text=output.get("text", ""),
                end_of_turn=bool(output.get("end_of_turn")),
                speech_interrupted=bool(output.get("speech_interrupted", False)),
                action_scores=output.get("action_scores", {}),
                system_speech_reset=interrupt_speech,
                native_turn_open=not bool(duplex.current_turn_ended),
                audio_frontend=stream,
                tts_calls=self.step_tts_calls,
                codec_calls=self.step_codec_calls,
                speech_complete=bool(output.get("end_of_turn"))
                and bool(self.step_tts_calls)
                and all(
                    call.get("speech_eos_reached", False)
                    for call in self.step_tts_calls
                ),
                _codec_waveforms=self.step_codec_waveforms,
                input_rms=round(input_rms, 6),
                prefill_seconds=round(started - step_started, 4),
                generation_seconds=round(generated - started, 4),
                compute_seconds=round(time.monotonic() - step_started, 4),
            ), audio

    def end(self):
        self.model.end()
        self.model._duplex._reset_streaming_state()
        self.model._base_model.audio_past_key_values = None
        tokenizer = self.model._base_model.tts.audio_tokenizer
        tokenizer.cache, tokenizer.stream_cache, tokenizer.hift_cache_dict = (
            None,
            None,
            {},
        )
        self.model._duplex.streaming_prefill = self.native_prefill
        self.model._duplex.decoder.feed = self.native_feed


def create_app(cfg, device):
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="native-duplex")
    state = dict(
        engine=None,
        busy=False,
        prepared=False,
        preparing=None,
        preparation_seconds=0.0,
        input_filter=None,
    )

    async def _prepare_session():
        started = time.monotonic()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(pool, state["engine"].begin)
        if cfg.get("enable_input_noise_filter", False):
            state["input_filter"] = await loop.run_in_executor(
                pool, MicrophoneNoiseFilter, cfg
            )
        state["preparation_seconds"] = time.monotonic() - started
        state["prepared"] = True

    @asynccontextmanager
    async def _lifespan(app):
        loop = asyncio.get_running_loop()
        state["engine"] = await loop.run_in_executor(pool, VoiceEngine, cfg)
        if cfg.get("preinitialize_sessions", False):
            await _prepare_session()
        yield
        if state["preparing"] is not None:
            await asyncio.gather(state["preparing"], return_exceptions=True)
        pool.shutdown(wait=True)

    app = FastAPI(lifespan=_lifespan)

    @app.get("/health")
    async def _health():
        available = (
            not cfg.get("preinitialize_sessions", False)
            or state["prepared"]
            or state["busy"]
        )
        return dict(
            ready=state["engine"] is not None and available,
            busy=state["busy"],
            gpu=device,
            session_preinitialized=state["prepared"],
            session_prepare_seconds=round(state["preparation_seconds"], 4),
            model=cfg["frontend_model_name"],
            native_audio=True,
            input_format="collator_audio_boundaries_v1",
            system_prompt_source=cfg.get("frontend_prompt_source", "checkpoint"),
            precision=cfg.get("frontend_precision", "bfloat16"),
            duplex_protocol="native_duplex_v1",
            allow_speech_interruption=cfg["allow_speech_interruption"],
            system_barge_in=cfg["enable_system_barge_in"],
            vad="webrtcvad" if cfg["enable_system_barge_in"] else "off",
            input_noise_filter=bool(cfg.get("enable_input_noise_filter", False)),
            playback_echo_guard=bool(cfg.get("enable_playback_echo_guard", False)),
        )

    @app.websocket("/ws")
    async def _conversation(ws: WebSocket):
        await ws.accept()
        if state["busy"]:
            await ws.close(code=1013, reason="This GPU already has a voice session")
            return
        else:
            state["busy"] = True
        session_id = uuid.uuid4().hex
        directory = Path(cfg["run_directory"]) / "sessions" / session_id
        directory.mkdir(parents=True)
        trace = (directory / "events.jsonl").open("w")
        input_audio = sf.SoundFile(
            str(directory / "input.wav"),
            mode="w",
            samplerate=16000,
            channels=1,
            subtype="PCM_16",
        )
        filtered_audio = (
            sf.SoundFile(
                str(directory / "model_input.wav"),
                mode="w",
                samplerate=16000,
                channels=1,
                subtype="PCM_16",
            )
            if cfg.get("enable_input_noise_filter", False)
            else None
        )
        input_filter = None
        output_audio = sf.SoundFile(
            str(directory / "output.wav"),
            mode="w",
            samplerate=24000,
            channels=1,
            subtype="PCM_16",
        )
        codec_audio = sf.SoundFile(
            str(directory / "codec.wav"),
            mode="w",
            samplerate=24000,
            channels=1,
            subtype="FLOAT",
        )
        loop = asyncio.get_running_loop()
        engine = state["engine"]
        queue = asyncio.Queue(maxsize=cfg["max_queued_audio_chunks"])
        deliveries = asyncio.Queue()
        pending = set()
        queries = set()
        started = time.monotonic()
        output_epoch = 0
        playback = dict(
            playing=False, queued_seconds=0.0, epoch=0, received_at=time.monotonic()
        )
        input_units = 0
        received_units = 0
        interrupt_sequence = 0
        reset_pending = False
        query_reset_pending = False
        query_router = SpokenQueryRouter()
        native_speaking = False
        awaiting_ack = False
        speech_complete = True
        output_available_at = 0.0
        speech_onset = SpeechOnset(cfg) if cfg["enable_system_barge_in"] else None
        echo_guard = (
            PlaybackEchoGuard(cfg)
            if cfg.get("enable_playback_echo_guard", False)
            else None
        )
        send_lock = asyncio.Lock()

        def _playback(value):
            if value is None:
                return
            elif not isinstance(value, dict):
                raise ValueError(
                    "playback must contain playing, queued_seconds, and epoch"
                )
            else:
                epoch = int(value["epoch"])
            if epoch != output_epoch:
                return
            else:
                queued = float(value["queued_seconds"])
            if not np.isfinite(queued) or queued < 0:
                raise ValueError(
                    "playback queued_seconds must be finite and nonnegative"
                )
            else:
                playback.update(
                    playing=bool(value["playing"]),
                    queued_seconds=queued,
                    epoch=epoch,
                    received_at=time.monotonic(),
                )

        async def _emit(event):
            async with send_lock:
                if (
                    event["type"] in ("action", "audio")
                    and event["output_epoch"] != output_epoch
                ):
                    return False
                event.update(elapsed_seconds=round(time.monotonic() - started, 3))
                recorded = {key: value for key, value in event.items() if key != "data"}
                trace.write(json.dumps(recorded, ensure_ascii=False) + "\n")
                trace.flush()
                await ws.send_json(browser_event(event))
                return True

        async def _publish_pcm(
            audio,
            step_epoch,
            input_seq,
            text,
            *,
            early=False,
            context=None,
            ready_at=None,
        ):
            nonlocal output_available_at
            sent = await _emit(
                dict(
                    type="audio",
                    sample_rate=24000,
                    data=base64.b64encode(audio.tobytes()).decode(),
                    text=text,
                    output_epoch=step_epoch,
                    input_seq=input_seq,
                    input_sequence=input_seq,
                    dispatch_mode="codec_subchunk" if early else "step_remainder",
                    action_context=context,
                    codec_ready_monotonic=ready_at,
                )
            )
            if sent:
                output_audio.write(audio)
                if step_epoch == output_epoch:
                    output_available_at = (
                        max(output_available_at, time.monotonic() + 0.08)
                        + audio.size / 24000
                    )
                    if echo_guard is not None:
                        echo_guard.add_output(audio, time.monotonic())
            return int(audio.size) if sent else 0

        async def _receive():
            nonlocal \
                received_units, \
                output_epoch, \
                reset_pending, \
                interrupt_sequence, \
                output_available_at
            try:
                while True:
                    message = await ws.receive_json()
                    _playback(message.get("playback"))
                    if message.get("type") == "playback_state":
                        # Apply control feedback even while a native GPU step
                        # is in progress. It must not wait behind audio or
                        # consume one input/audio unit in the model timeline.
                        if "playback" not in message:
                            _playback(message)
                    else:
                        received_units += 1
                        message["_received_sequence"] = received_units
                        if message.get("type") == "audio":
                            data = base64.b64decode(message["data"], validate=True)
                            if len(data) != cfg["chunk_samples"] * 4:
                                raise ValueError(
                                    "Send one second of mono float32 PCM at 16000 Hz"
                                )
                            else:
                                waveform = np.frombuffer(data, dtype="<f4").copy()
                            if (
                                not np.isfinite(waveform).all()
                                or np.max(np.abs(waveform)) > 1.01
                            ):
                                raise ValueError("Invalid PCM samples")
                            else:
                                message["_waveform"] = waveform
                            if input_filter is not None:
                                (
                                    message["_model_waveform"],
                                    message["_input_processing"],
                                ) = input_filter.process(waveform)
                            if speech_onset is not None:
                                queued_playback = max(
                                    0.0,
                                    playback["queued_seconds"]
                                    - (time.monotonic() - playback["received_at"]),
                                )
                                if echo_guard is not None:
                                    echo_frames, echo_evidence = echo_guard.classify(
                                        waveform, queued_playback, time.monotonic()
                                    )
                                    activity = speech_onset.process(
                                        waveform, echo_frames
                                    )
                                    activity["echo_guard"] = echo_evidence
                                else:
                                    activity = speech_onset.process(waveform)
                                message["_vad"] = activity
                                if activity["speech_started"] and (
                                    native_speaking or queued_playback > 0
                                ):
                                    previous_epoch = output_epoch
                                    output_epoch += 1
                                    output_available_at = 0.0
                                    reset_pending = True
                                    interrupt_sequence = received_units
                                    await _emit(
                                        dict(
                                            type="interrupt",
                                            reason="user_speech",
                                            output_epoch=output_epoch,
                                            cancelled_output_epoch=previous_epoch,
                                            native_turn_yielded=False,
                                            speech_started=True,
                                            vad=activity,
                                            input_sequence=message.get(
                                                "input_sequence", received_units
                                            ),
                                            playback_queued_seconds=round(
                                                queued_playback, 4
                                            ),
                                        )
                                    )
                                    playback.update(
                                        playing=False,
                                        queued_seconds=0.0,
                                        epoch=output_epoch,
                                        received_at=time.monotonic(),
                                    )
                                    if echo_guard is not None:
                                        echo_guard.reset()
                        elif (
                            message.get("type") == "drain" and speech_onset is not None
                        ):
                            speech_onset.process(
                                np.zeros(cfg["chunk_samples"], dtype=np.float32)
                            )
                        await queue.put((message, time.monotonic()))
            except (WebSocketDisconnect, ValueError, RuntimeError):
                await queue.put((None, time.monotonic()))

        async def _delegate(task_id, query):
            task_started = time.monotonic()
            try:
                result = await ask_backend(client, cfg, task_id, query)
            except (httpx.HTTPError, ValueError, KeyError) as error:
                payload, event = tool_event(
                    task_id,
                    query,
                    "The reasoning backend is unavailable. Please try again.",
                    "error",
                )
                result = dict(payload=payload, event=event, error=type(error).__name__)
            finally:
                queries.discard(query)
            result["backend_seconds"] = round(time.monotonic() - task_started, 3)
            result["ready_at"] = time.monotonic()
            await _emit(
                dict(
                    type="delegate_result_ready",
                    task_id=task_id,
                    backend_seconds=result["backend_seconds"],
                )
            )
            await deliveries.put(result)

        receiver = None
        preinitialized = False
        ready_wait_started = time.monotonic()
        try:
            if cfg.get("preinitialize_sessions", False):
                if not state["prepared"]:
                    await state["preparing"]
                state["prepared"] = False
                preinitialized = True
                input_filter = state["input_filter"]
            else:
                await loop.run_in_executor(pool, engine.begin)
                input_filter = (
                    MicrophoneNoiseFilter(cfg)
                    if cfg.get("enable_input_noise_filter", False)
                    else None
                )
            await _emit(
                dict(
                    type="ready",
                    session_id=session_id,
                    input_sample_rate=16000,
                    output_sample_rate=24000,
                    chunk_samples=cfg["chunk_samples"],
                    gpu=device,
                    output_epoch=output_epoch,
                    duplex_protocol="native_duplex_v1",
                    model=cfg["frontend_model_name"],
                    precision=cfg.get("frontend_precision", "bfloat16"),
                    session_preinitialized=preinitialized,
                    ready_wait_seconds=round(time.monotonic() - ready_wait_started, 4),
                    session_prepare_seconds=round(state["preparation_seconds"], 4),
                    input_noise_filter=input_filter is not None,
                )
            )
            receiver = asyncio.create_task(_receive())
            async with httpx.AsyncClient(
                trust_env=True, timeout=cfg["backend_timeout_seconds"]
            ) as client:
                async with asyncio.timeout(cfg["max_session_seconds"]):
                    while True:
                        message, received_at = await queue.get()
                        queue_seconds = time.monotonic() - received_at
                        if message is None or message.get("type") == "stop":
                            break
                        elif message.get("type") == "audio":
                            waveform = message.get(
                                "_model_waveform", message["_waveform"]
                            )
                            text = ""
                        elif message.get("type") in ("text", "drain"):
                            text = str(message.get("text", "")).strip()[:3000]
                            waveform = np.zeros(cfg["chunk_samples"], dtype=np.float32)
                        else:
                            raise ValueError("Unknown voice message type")
                        input_units += 1
                        input_seq = message.get(
                            "input_sequence", message.get("input_seq", input_units)
                        )
                        client_queue_seconds = float(
                            message.get("input_queue_seconds", 0)
                        )
                        raw_waveform = message.get("_waveform", waveform)
                        input_audio.write(raw_waveform)
                        if filtered_audio is not None:
                            filtered_audio.write(waveform)
                        received = []
                        playback_seconds = max(
                            0.0,
                            playback["queued_seconds"]
                            - (time.monotonic() - playback["received_at"]),
                        )
                        delivery_safe = (
                            not awaiting_ack
                            and not native_speaking
                            and speech_complete
                            and playback_seconds <= 0.01
                            and time.monotonic() >= output_available_at
                        )
                        while delivery_safe and not deliveries.empty():
                            delivery = deliveries.get_nowait()
                            delivery["delivery_wait_seconds"] = round(
                                time.monotonic()
                                - delivery.pop("ready_at", time.monotonic()),
                                4,
                            )
                            received.append(delivery)
                            await _emit(dict(type="delegate_result", **delivery))
                        step_epoch = output_epoch
                        should_reset = (
                            reset_pending
                            and message["_received_sequence"] >= interrupt_sequence
                        )
                        if should_reset:
                            reset_pending = False
                        query_reset = query_reset_pending
                        query_reset_pending = False
                        if should_reset or query_reset:
                            query_router.reset()
                        early_futures, early_parts = [], []
                        eligible = (
                            cfg.get("enable_subchunk_dispatch", False)
                            and query_router.mode == "speech"
                            and not should_reset
                            and not query_reset
                        )

                        def _pcm_ready(part, context, ready_at):
                            early_parts.append(part.copy())
                            early_futures.append(
                                asyncio.run_coroutine_threadsafe(
                                    _publish_pcm(
                                        part,
                                        step_epoch,
                                        input_seq,
                                        "",
                                        early=True,
                                        context=context,
                                        ready_at=ready_at,
                                    ),
                                    loop,
                                )
                            )

                        engine.pcm_callback = _pcm_ready if eligible else None
                        try:
                            result, audio = await loop.run_in_executor(
                                pool,
                                engine.step,
                                waveform,
                                text,
                                received,
                                should_reset or query_reset,
                            )
                        finally:
                            engine.pcm_callback = None
                        published = await asyncio.gather(
                            *(asyncio.wrap_future(f) for f in early_futures)
                        )
                        early_samples = sum(published)
                        if early_parts and step_epoch == output_epoch:
                            expected = np.concatenate(early_parts)
                            if audio is None or not np.array_equal(
                                audio[: len(expected)], expected
                            ):
                                raise RuntimeError(
                                    "Incremental PCM is not a byte-identical prefix of native step output"
                                )
                            if early_samples != len(expected):
                                raise RuntimeError(
                                    "Incremental dispatch sample accounting differs"
                                )
                        result["early_dispatch_samples"] = early_samples
                        result["early_dispatch_chunks"] = len(early_parts)
                        for raw_codec in result.pop("_codec_waveforms", []):
                            codec_audio.write(raw_codec)
                        result["model_input_rms"] = result["input_rms"]
                        result["input_rms"] = round(
                            float(np.sqrt(np.mean(raw_waveform**2))), 6
                        )
                        native_speaking = (
                            not result["end_of_turn"] and result["action"] == "speak"
                        )
                        cancelled = (
                            step_epoch != output_epoch
                            or message["_received_sequence"] < interrupt_sequence
                        )
                        if cancelled:
                            await _emit(
                                dict(
                                    type="output_cancelled",
                                    cancelled_output_epoch=step_epoch,
                                    output_epoch=output_epoch,
                                    input_sequence=input_seq,
                                    action=result["action"],
                                    compute_seconds=result["compute_seconds"],
                                )
                            )
                            await _emit(
                                dict(
                                    type="consumed",
                                    input_sequence=input_seq,
                                    output_epoch=output_epoch,
                                    queue_seconds=round(queue_seconds, 4),
                                    compute_seconds=result["compute_seconds"],
                                    client_queue_seconds=client_queue_seconds,
                                    queued_audio_chunks=queue.qsize(),
                                )
                            )
                            continue
                        result, audio = query_router.route(result, audio)
                        routing_state = result.get("query_routing", {}).get("state")
                        if routing_state in ("rerouted", "rejected"):
                            query_reset_pending = True
                        if routing_state == "buffering":
                            native_speaking = True
                        elif routing_state in ("rerouted", "rejected"):
                            native_speaking = False
                        action = result["action"]
                        if result["speech_interrupted"] or should_reset or query_reset:
                            awaiting_ack, speech_complete = False, True
                        if action == "delegate":
                            awaiting_ack = True
                        elif action == "speak":
                            awaiting_ack = False
                            speech_complete = result.get(
                                "speech_complete", result["end_of_turn"]
                            )
                        elif awaiting_ack:
                            # Give the native model a unit to decide whether
                            # to acknowledge. A model-selected listen is not
                            # an unfinished spoken confirmation.
                            awaiting_ack = False
                        result["backend_delivery_state"] = dict(
                            awaiting_ack=awaiting_ack,
                            speech_complete=speech_complete,
                            pending_results=deliveries.qsize(),
                        )
                        playback_seconds = max(
                            0.0,
                            playback["queued_seconds"]
                            - (time.monotonic() - playback["received_at"]),
                        )
                        tail_interrupted = (
                            not cfg["enable_system_barge_in"]
                            and action == "listen"
                            and (playback["playing"] or playback_seconds > 0)
                            and result["input_rms"] > cfg["playback_interrupt_rms"]
                        )
                        if result["speech_interrupted"] or tail_interrupted:
                            previous_epoch = output_epoch
                            output_epoch += 1
                            output_available_at = 0.0
                            await _emit(
                                dict(
                                    type="interrupt",
                                    output_epoch=output_epoch,
                                    cancelled_output_epoch=previous_epoch,
                                    input_seq=input_seq,
                                    input_sequence=input_seq,
                                    reason="model_" + action,
                                    playback_queued_seconds=round(playback_seconds, 4),
                                    native_turn_yielded=result["speech_interrupted"],
                                )
                            )
                            playback.update(
                                playing=False,
                                queued_seconds=0.0,
                                epoch=output_epoch,
                                received_at=time.monotonic(),
                            )
                            if echo_guard is not None:
                                echo_guard.reset()
                        await _emit(
                            dict(
                                type="action",
                                input_seq=input_seq,
                                input_sequence=input_seq,
                                output_epoch=output_epoch,
                                client_queue_seconds=client_queue_seconds,
                                queue_seconds=round(queue_seconds, 4),
                                input_type=message["type"],
                                input_processing=message.get("_input_processing"),
                                vad=message.get("_vad"),
                                **result,
                            )
                        )
                        if action == "delegate":
                            query = delegate_query(result["text"])
                            if query in queries:
                                await _emit(
                                    dict(type="delegate_duplicate", query=query)
                                )
                            elif len(queries) >= cfg["max_pending_delegations"]:
                                payload, event = tool_event(
                                    uuid.uuid4().hex,
                                    query,
                                    "Too many tasks are pending; please wait briefly.",
                                    "error",
                                )
                                await deliveries.put(dict(payload=payload, event=event))
                            else:
                                task_id = "task_" + uuid.uuid4().hex[:12]
                                queries.add(query)
                                await _emit(
                                    dict(
                                        type="delegate_request",
                                        task_id=task_id,
                                        query=query,
                                    )
                                )
                                task = asyncio.create_task(_delegate(task_id, query))
                                pending.add(task)
                                task.add_done_callback(pending.discard)
                        elif action == "speak" and audio is not None and audio.size:
                            if early_samples and query_router.mode == "query":
                                raise RuntimeError(
                                    "Spoken-query audio must not be dispatched"
                                )
                            remaining = audio[early_samples:]
                            if remaining.size:
                                await _publish_pcm(
                                    remaining,
                                    step_epoch,
                                    input_seq,
                                    result["text"],
                                    context=dict(
                                        action="speak",
                                        text=result["text"],
                                        end_of_turn=result["end_of_turn"],
                                        speech_complete=result["speech_complete"],
                                    ),
                                )
                        await _emit(
                            dict(
                                type="consumed",
                                input_seq=input_seq,
                                input_sequence=input_seq,
                                output_epoch=output_epoch,
                                client_queue_seconds=client_queue_seconds,
                                queue_seconds=round(queue_seconds, 4),
                                compute_seconds=result["compute_seconds"],
                                queued_audio_chunks=queue.qsize(),
                            )
                        )
        except (WebSocketDisconnect, RuntimeError) as error:
            LOG.info("Session %s closed: %s", session_id, error)
        except Exception as error:
            LOG.exception("Session %s failed", session_id)
            trace.write(json.dumps(dict(type="error", message=str(error))) + "\n")
            try:
                await ws.send_json(
                    dict(type="error", message="Session failed; check the server logs.")
                )
                await ws.close(code=1011)
            except (WebSocketDisconnect, RuntimeError):
                pass
        finally:
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            if receiver is not None:
                receiver.cancel()
                await asyncio.gather(receiver, return_exceptions=True)
            await loop.run_in_executor(pool, engine.end)
            trace.close()
            input_audio.close()
            if filtered_audio is not None:
                filtered_audio.close()
            output_audio.close()
            codec_audio.close()
            metadata = dict(
                session_id=session_id,
                frontend_model=cfg["frontend_model"],
                model_precision=cfg.get("frontend_precision", "bfloat16"),
                runtime_details=engine.runtime_details,
                frontend_seed=cfg.get("frontend_seed"),
                tts_seed=cfg.get("tts_seed"),
                session_preinitialized=preinitialized,
                backend_model=cfg["backend_model_name"],
                gpu=device,
                duration_seconds=time.monotonic() - started,
                input_sample_rate=16000,
                output_sample_rate=24000,
                audio_source="checkpoint_native_tts",
                input_format="collator_audio_boundaries_v1",
                add_timestamps=engine.add_timestamps,
                duplex_protocol="native_duplex_v1",
                output_epoch=output_epoch,
                input_noise_filter=input_filter is not None,
                allow_speech_interruption=cfg["allow_speech_interruption"],
            )
            (directory / "metadata.json").write_text(
                json.dumps(metadata, indent=2) + "\n"
            )
            if cfg.get("preinitialize_sessions", False):
                state["preparing"] = asyncio.create_task(_prepare_session())
            state["busy"] = False

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--device", type=int, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    cfg = configuration(args.config)
    uvicorn.run(
        create_app(cfg, args.device),
        host="127.0.0.1",
        port=cfg["worker_port"] + args.device,
        ws_max_size=1024 * 1024,
        log_level="info",
    )
