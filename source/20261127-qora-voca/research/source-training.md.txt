# Training recipe — qora-voca-zh

Everything below runs on a single consumer GPU (we used an RTX 3060 12 GB). CPU-only machines can do annotation/prepare slowly; training needs CUDA.

## 0. Install

```bash
pip install -e ".[prepare,annotate,generate,evaluate,onnx,dev]"
python scripts/download_assets.py     # Mandarin CTC aligner weights (ModelScope / hf-mirror)
```

The aligner is `lyonlu13/wav2vec2-large-zh-singing-phoneme-ctc`. If your network throttles single-stream downloads, `scripts/download_aligner_parallel.py` does ranged parallel fetching and `scripts/register_aligner.py` registers the files into the local HF cache layout.

## 1. Corpus

```bash
python scripts/build_corpus.py        # -> data/corpus/sentences.jsonl (10,696 sentences, seed 20261116)
```

## 2. Voice references (Qwen3-TTS)

```bash
python scripts/design_voices.py       # F2 + M2 via VoiceDesign -> data/voices/{F2,M2}.wav + voices.json
python scripts/design_voice_m3.py     # M3 candidates, screened by faster-whisper CER + spectral clarity
```

Requires a local Qwen3-TTS installation (VoiceDesign + 1.7B Base). The selected M3 design is recorded in `data/voices/voices.json` (`design: 1, seed: 20261131`).

## 3. Generate teacher audio

```bash
python scripts/generate_audio_zh.py   # per-sentence audio, one voice reference per utterance
python scripts/split_manifest.py      # train / validation / test feature inputs
```

Generation is resumable; transient failures can be retried with `scripts/retry_transient_rejects.py`.

## 4. Annotate (CTC forced alignment + QC)

```bash
python -m tiny_voca.annotate \
  --features data/features --output data/annotated \
  --config config-zh.json --device cuda \
  --stage ctc \
  --max-weak-phone-fraction 0.25 --min-token-probability 0.5 \
  --max-phone-frames 70 --min-vowel-voiced 0.35 \
  --min-phones-per-second 4 --max-phones-per-second 30 \
  --resume
```

QC gates and rejection statistics land in `data/annotated/summary.json`. Diagnostics: `scripts/plot_alignments.py` (per-recording PNG), `scripts/calibrate_aligner_timing.py` (where CTC emissions sit inside a phone).

## 5. Prepare acoustic features

```bash
python -m tiny_voca.prepare --inputs data/annotated --output data/features-acoustic --config config-zh.json --resume
```

Mel / F0 / voicing / energy per frame. `--resume` skips completed items.

## 6. Train

Base run (two voices, 100,000 steps):

```bash
python -m tiny_voca.train \
  --train data/features-acoustic/train --validation data/features-acoustic/validation \
  --output runs/base --config config-zh.json --device cuda \
  --steps 100000 --batch-frames 9000 --max-batch 32 \
  --learning-rate 3e-4 --warmup 1000 --lr-half-life 100000 --grad-clip 10 \
  --gan-start 8000 --gan-ratio 0.7 --gan-ramp 3000 --feature-matching 30 --gan-scale-max 2000 \
  --crop-samples 8192 --crops 2 \
  --teacher-hold 3000 --teacher-ramp 7000 --teacher-final 0 \
  --validation-size 32 --seed 20261113
```

Continuation with a new voice (three voices, +60,000 steps → 160,000 total):

```bash
python -m tiny_voca.train \
  --train data/features-acoustic-3v/train --validation data/features-acoustic-3v/validation \
  --output runs/zh-3v --config config-zh-3v.json --device cuda \
  --init-from runs/base/last.pt --new-data \
  --steps 160000 ...   # same recipe as above
```

Key mechanics:

- `--steps` is the **total** step counter, not additional steps.
- `--init-from` branches a new run from another checkpoint (weights, step counter, trained critics carried over). `--new-data` accepts a different annotation run / front end with the same symbol inventory.
- **Speaker expansion:** if the new config's `speakers` list extends the old one as a prefix, the embedding tables grow by the new rows and every previously learned voice is preserved bit-exactly. This is how F2/M2 survived the two→three→four-voice continuations unchanged.
- `scripts/merge_features_3v.py` / `consolidate_features_3v.py` merge per-voice feature manifests into one root (train.py forbids feature paths escaping the acoustic root; hard-link consolidation avoids copying).

## 7. Export

```bash
python scripts/export_checkpoint.py --checkpoint runs/zh-3v/last.pt --output runs/zh-3v/inference.pt
python -m tiny_voca.export --checkpoint runs/zh-3v/inference.pt --output release/onnx/model.onnx
python scripts/check_onnx_zh.py       # parity + CPU timing (expect PARITY_OK, ~50x realtime)
```

To publish a subset of voices, drop the unwanted speaker's embedding rows:

```bash
python scripts/strip_voice.py --input runs/zh-3v/inference.pt --output release/qora-voca-zh.pt --drop VOICE_ID
```

The remaining voices are bit-identical to the full checkpoint (verified by same-seed waveform comparison).

## 8. Evaluate

```bash
python -m tiny_voca.evaluate --checkpoint release/qora-voca-zh.pt --split test   # faster-whisper CER
PYTHONPATH=src python -m pytest tests -q                                        # 69 tests
```

## Logged results (step 160,000)

Validation (86 utterances, predicted durations/pitch): mel 0.539, STFT 1.211, pause accuracy 97.3%, voicing accuracy 96.0%, duration ratio 0.975, pitch error 1.26 semitones. Continuation phase wall clock 75,471 s (~21 h) on RTX 3060, 0.79 steps/s, 65.7 audio-seconds per wall-second.
