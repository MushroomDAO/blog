# Sage-Interaction Demo

[English](README.md) | [简体中文](README_zh-CN.md) · [Project overview](../README.md)

## Install

Requires Linux, a BF16-capable NVIDIA GPU, Python 3.12, and a CUDA 12.8 toolkit.

From the repository root:

```bash
cd demo
python3.12 -m venv .venv
source .venv/bin/activate
mkdir -p .cache/tmp
export TMPDIR="$PWD/.cache/tmp" PIP_NO_CACHE_DIR=1
python -m pip install --upgrade pip setuptools wheel packaging ninja
python -m pip install -r requirements.txt
python -m pip install flash-attn==2.8.3 --no-build-isolation
python scripts/prepare_environment.py
```

## Configure

```bash
cp config.example.json config.local.json
```

Edit these fields in `config.local.json`. Model and audio paths are relative to the configuration file.

| Field | Setting |
| --- | --- |
| `checkpoint` | Model directory containing weights, tokenizer, and model code; default: `models/sage-interaction` |
| `tts_base` | Directory containing `assets/token2wav/` and base TTS weights; defaults to the checkpoint |
| `prompt_wav` | Voice-reference WAV; defaults to the checkpoint's `system_ref_audio.wav` |
| `backend_base_url` | Backend API base URL supporting `/models`, `/chat/completions`, and structured JSON output |
| `backend_model_name` | Backend model name |

## Start

```bash
bash start_demo.sh --config config.local.json --gpu 0 --instances 1
```

Enter the backend API key at the hidden prompt, or set `SAGE_BACKEND_API_KEY` in the environment before starting.

When `Demo ready` appears, open [http://127.0.0.1:18080/](http://127.0.0.1:18080/) and allow microphone access. Press **Ctrl+C** in the terminal to stop.

Use `--gpu 0,1 --instances 2` for two workers on two GPUs. Change the browser port with `--port`. For all options:

```bash
bash start_demo.sh --help
```

## Remote access

Run this command on your computer, replacing `demo-host` with your GPU host's SSH alias:

```bash
ssh -NT -L 18080:127.0.0.1:18080 demo-host
```

Then open [http://127.0.0.1:18080/](http://127.0.0.1:18080/) in your browser.
