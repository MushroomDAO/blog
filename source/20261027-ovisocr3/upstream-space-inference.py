"""Streaming Transformers inference on Hugging Face ZeroGPU."""
import os
from queue import Empty
import threading
import time

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

import spaces  # ZeroGPU must patch CUDA before torch is imported.

import torch
from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer

MODEL_SOURCE = "ATH-MaaS/OvisOCR3"
MIN_PIXELS = 448 * 448
MAX_PIXELS = 2880 * 2880
GPU_SECONDS = 120
processor = None
model = None


def load_model():
    global processor, model
    if model is not None:
        return
    processor = AutoProcessor.from_pretrained(MODEL_SOURCE, min_pixels=MIN_PIXELS, max_pixels=MAX_PIXELS)
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_SOURCE, dtype=torch.bfloat16,
        attn_implementation="sdpa",
    ).to("cuda").eval()


class Deadline(StoppingCriteria):
    def __init__(self, seconds, cancelled):
        self.end = time.monotonic() + seconds
        self.cancelled = cancelled
        self.expired = False

    def __call__(self, input_ids, scores, **kwargs):
        self.expired = time.monotonic() >= self.end
        return self.expired or self.cancelled.is_set()


class TimedStreamer(TextIteratorStreamer):
    def __init__(self, tokenizer, started):
        super().__init__(tokenizer, skip_prompt=True, skip_special_tokens=True,
                         clean_up_tokenization_spaces=False, timeout=0.5)
        self.started = started
        self.tokens = 0
        self.first_token_seconds = None

    def put(self, value):
        if not self.next_tokens_are_prompt:
            self.tokens += value.numel()
            if self.first_token_seconds is None:
                self.first_token_seconds = time.monotonic() - self.started
        super().put(value)


def infer_stream(images, prompt, max_tokens=8192):
    if model is None or processor is None:
        raise RuntimeError("Model is not loaded.")
    started = time.monotonic()
    yield {"text": "", "finish_reason": None, "phase": "Preparing input", "tokens": 0}
    messages = [{"role": "user", "content": [
        *[{"type": "image", "image": im} for im in images],
        {"type": "text", "text": prompt},
    ]}]
    inputs = processor.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=True,
        return_tensors="pt", enable_thinking=False,
    )
    prepared = time.monotonic()
    yield {"text": "", "finish_reason": None, "phase": "Waiting for ZeroGPU", "tokens": 0,
           "preprocess_seconds": prepared - started}
    stream = generate_gpu(inputs, max_tokens)
    acquired = None
    try:
        for response in stream:
            if acquired is None:
                acquired = time.monotonic()
            yield {**response, "preprocess_seconds": prepared - started,
                   "gpu_wait_seconds": acquired - prepared,
                   "request_seconds": time.monotonic() - started}
    finally:
        stream.close()


@spaces.GPU(duration=GPU_SECONDS)
def generate_gpu(inputs, max_tokens):
    started = time.monotonic()
    yield {"text": "", "finish_reason": None, "phase": "GPU acquired / preparing tensors", "tokens": 0}
    inputs = inputs.to(model.device)
    streamer = TimedStreamer(processor.tokenizer, started)
    cancelled = threading.Event()
    deadline = Deadline(max(1, GPU_SECONDS - 10 - (time.monotonic() - started)), cancelled)
    outcome = {}

    def generate():
        try:
            with torch.inference_mode():
                ids = model.generate(
                    **inputs, max_new_tokens=int(max_tokens), do_sample=False,
                    temperature=None, top_p=None, top_k=None,
                    eos_token_id=processor.tokenizer.eos_token_id,
                    pad_token_id=processor.tokenizer.pad_token_id,
                    streamer=streamer, stopping_criteria=StoppingCriteriaList([deadline]),
                )[0, inputs["input_ids"].shape[1]:]
            outcome["tokens"] = len(ids)
            outcome["finish_reason"] = "timeout" if deadline.expired else (
                "stop" if len(ids) and int(ids[-1]) == processor.tokenizer.eos_token_id else "length"
            )
        except BaseException as exc:
            outcome["error"] = exc
            streamer.on_finalized_text("", stream_end=True)

    worker = threading.Thread(target=generate, daemon=True, name="ovisocr3-generation")
    worker.start()
    text = ""
    sent_text = False
    last_update = time.monotonic()
    try:
        while True:
            try:
                fragment = next(streamer)
            except Empty:
                fragment = ""
            except StopIteration:
                break
            text += fragment
            if time.monotonic() - last_update >= 0.25 or (text and not sent_text):
                elapsed = time.monotonic() - started
                yield {"text": text, "finish_reason": None, "seconds": elapsed,
                       "phase": "Generating" if streamer.tokens else "Prefill / waiting for first token",
                       "tokens": streamer.tokens, "first_token_seconds": streamer.first_token_seconds}
                last_update = time.monotonic()
                sent_text = bool(text)
        worker.join()
        if "error" in outcome:
            raise RuntimeError(str(outcome["error"])) from outcome["error"]
        elapsed = time.monotonic() - started
        decode_seconds = max(0, elapsed - (streamer.first_token_seconds or elapsed))
        yield {"text": text, **outcome, "seconds": elapsed, "phase": "Generated",
               "first_token_seconds": streamer.first_token_seconds,
               "decode_tokens_per_second": max(0, streamer.tokens - 1) / decode_seconds if decode_seconds else None}
    finally:
        cancelled.set()
        worker.join()
