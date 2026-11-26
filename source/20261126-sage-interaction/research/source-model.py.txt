"""Load checkpoint-native MiniCPM-o duplex inference and its speech assets."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import torch

LOGGER = logging.getLogger(__name__)

TOKEN2WAV_FILES = (
    "flow.pt",
    "flow.yaml",
    "hift.pt",
    "campplus.onnx",
    "speech_tokenizer_v2_25hz.onnx",
)


class NativeDuplexModel:
    """One model and native decoder per worker; no cross-session batching."""

    def __init__(self, checkpoint, tts_base, prompt_wav):
        from transformers import AutoModel

        _patch_whisper_attention()
        self._base_model = (
            AutoModel.from_pretrained(
                checkpoint,
                trust_remote_code=True,
                local_files_only=True,
                attn_implementation="sdpa",
                torch_dtype=torch.bfloat16,
                init_tts=True,
            )
            .eval()
            .to("cuda:0")
        )
        # The loader preserves native FP32 buffers, including rotary embeddings.
        # Do not cast the entire model after loading it.
        weights = json.loads(
            (Path(checkpoint) / "model.safetensors.index.json").read_text()
        )["weight_map"]
        checkpoint_tts = {key for key in weights if key.startswith("tts.")}
        if checkpoint_tts:
            expected = {"tts." + key for key in self._base_model.tts.state_dict()}
            if checkpoint_tts != expected:
                raise ValueError(
                    "Checkpoint TTS weights are incomplete or incompatible"
                )
            assets = Path(tts_base) / "assets/token2wav"
        else:
            assets = _load_original_tts_weights(self._base_model, Path(tts_base))
        for name in TOKEN2WAV_FILES:
            if not (assets / name).is_file():
                raise FileNotFoundError("Missing Token2wav asset: " + name)
        original_init = self._base_model.init_tts

        def initialize_speech(**kwargs):
            return original_init(**dict(kwargs, model_dir=str(assets)))

        self._base_model.init_tts = initialize_speech
        try:
            self._duplex = self._base_model.as_duplex(generate_audio=True)
        finally:
            self._base_model.init_tts = original_init
        self._prompt_wav_path = prompt_wav

    def begin(self, instruction):
        self._duplex.prepare(
            prefix_system_prompt=instruction, prompt_wav_path=self._prompt_wav_path
        )

    def end(self):
        self._duplex.set_session_stop()


def _load_original_tts_weights(model: Any, original_model_path: Path) -> Path:
    """Restore the unchanged TTS tower from the original MiniCPM-o model.

    Action-only checkpoints omit TTS weights.  Read just the original TTS
    tensors, one small slice at a time, rather than loading a second 18 GB
    model or a complete safetensors shard into host memory.
    """
    from safetensors import safe_open

    index_path = original_model_path / "model.safetensors.index.json"
    if not index_path.is_file():
        raise FileNotFoundError(
            f"Original model safetensors index not found: {index_path}"
        )
    weight_map = json.loads(index_path.read_text(encoding="utf-8"))["weight_map"]
    source_keys = {key for key in weight_map if key.startswith("tts.")}
    if not source_keys:
        raise RuntimeError(
            f"No TTS weights found in original model index: {index_path}"
        )
    if not hasattr(model, "tts"):
        raise RuntimeError(
            "Checkpoint model has no TTS module; load it with init_tts=True"
        )

    destination = model.tts.state_dict()
    destination_keys = {f"tts.{key}" for key in destination}
    if source_keys != destination_keys:
        missing = sorted(destination_keys - source_keys)
        extra = sorted(source_keys - destination_keys)
        raise RuntimeError(
            "Original TTS weights do not match the checkpoint TTS module: "
            f"missing={missing[:8]}, extra={extra[:8]}"
        )

    asset_dir = original_model_path / "assets" / "token2wav"
    for name in (
        "flow.pt",
        "flow.yaml",
        "hift.pt",
        "campplus.onnx",
        "speech_tokenizer_v2_25hz.onnx",
    ):
        if not (asset_dir / name).is_file():
            raise FileNotFoundError(
                f"Original Token2wav asset not found: {asset_dir / name}"
            )

    shards = sorted({weight_map[key] for key in source_keys})
    copied = 0
    with torch.no_grad():
        for shard_name in shards:
            shard_path = original_model_path / shard_name
            if not shard_path.is_file():
                raise FileNotFoundError(f"Original TTS shard not found: {shard_path}")
            with safe_open(str(shard_path), framework="pt", device="cpu") as source:
                for key in sorted(source_keys):
                    if weight_map[key] != shard_name:
                        continue
                    target = destination[key.removeprefix("tts.")]
                    tensor_slice = source.get_slice(key)
                    shape = tuple(tensor_slice.get_shape())
                    if shape != tuple(target.shape):
                        raise RuntimeError(
                            f"TTS weight shape mismatch for {key}: "
                            f"original={shape}, checkpoint={tuple(target.shape)}"
                        )
                    if not shape:
                        target.copy_(
                            source.get_tensor(key).to(
                                device=target.device, dtype=target.dtype
                            )
                        )
                    else:
                        row_bytes = max(1, target[0].numel() * target.element_size())
                        rows_per_slice = max(1, (32 * 1024 * 1024) // row_bytes)
                        for start in range(0, shape[0], rows_per_slice):
                            end = min(start + rows_per_slice, shape[0])
                            target[start:end].copy_(
                                tensor_slice[start:end].to(
                                    device=target.device, dtype=target.dtype
                                )
                            )
                    copied += 1

    LOGGER.info("Restored %d original TTS tensors from %s", copied, original_model_path)
    return asset_dir


def _patch_whisper_attention() -> None:
    """Bridge the transformers 4.51 Whisper signature used by MiniCPM-o."""
    try:
        import inspect
        from transformers.models.whisper.modeling_whisper import WhisperAttention

        if "past_key_values" in inspect.signature(WhisperAttention.forward).parameters:
            return
        original = WhisperAttention.forward

        def patched(self, *args, past_key_values=None, **kwargs):
            kwargs.setdefault("past_key_value", past_key_values)
            result = original(self, *args, **kwargs)
            return (
                result[:2] if isinstance(result, tuple) and len(result) > 2 else result
            )

        WhisperAttention.forward = patched
        LOGGER.info("Patched WhisperAttention.forward for MiniCPM-o")
    except ImportError as exc:
        raise RuntimeError(
            "The installed transformers package lacks WhisperAttention"
        ) from exc
