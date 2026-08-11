---
title: "huggingface/speech-to-speech：一行命令跑起本地语音 Agent 完整管道"
titleEn: "huggingface-speech-to-speech-voice-agent-vad-stt-llm-tts-local"
description: "huggingface/speech-to-speech，12,080 stars，Apache-2.0，Python。低延迟、完全模块化的语音 Agent 管道：VAD → STT → LLM → TTS，通过 OpenAI Realtime 兼容的 WebSocket API 暴露。每个组件可独立替换，LLM 槽位支持 OpenAI 兼容协议——可以指向云端提供商、HF Inference Providers，或者本地 vLLM/llama.cpp，实现完全本地、完全开源的语音 Agent 栈。已在数千台 Reachy Mini 机器人上生产运行。一行 pip 安装，三行命令启动。"
descriptionEn: "huggingface/speech-to-speech, 12,080 stars, Apache-2.0, Python. A low-latency, fully modular voice-agent pipeline: VAD → STT → LLM → TTS, exposed through an OpenAI Realtime-compatible WebSocket API. Every component is swappable; the LLM slot speaks OpenAI-compatible protocols — point it at a hosted provider, HF Inference Providers, or a local vLLM/llama.cpp server for a fully local, fully open stack. Running in production as the conversation backend for thousands of Reachy Mini robots. One pip install, three commands to start."
pubDate: "2026-08-11"
updatedDate: "2026-08-11"
category: "Tech-News"
tags: ["语音AI", "本地部署", "Voice Agent", "开源", "Python", "HuggingFace", "LLM", "Mycelium"]
heroImage: "../../assets/images/huggingface-speech-to-speech-voice-agent-vad-stt-llm-tts-local-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

把一个能说话、能听话的 AI Agent 跑起来，通常需要把 VAD、STT、LLM、TTS 四个部分分别找好、接好、调好——每一步都有自己的依赖、延迟和格式问题。

`huggingface/speech-to-speech` 把这件事压缩成了三行命令：

```bash
pip install speech-to-speech
export OPENAI_API_KEY=...
speech-to-speech serve
```

GitHub: https://github.com/huggingface/speech-to-speech | ⭐ 12,080 | Apache-2.0 | Python

---

## 管道结构

整条语音 Agent 管道是四个组件，每个运行在自己的线程里，通过队列连接：

```
VAD（语音活动检测）
    ↓
STT（语音转文字）
    ↓
LLM（语言模型）
    ↓
TTS（文字转语音）
```

通过一个 **OpenAI Realtime 兼容的 WebSocket API** 对外暴露，地址是 `ws://localhost:8765/v1/realtime`。任何支持 OpenAI Realtime 协议的客户端都可以直接接入，不需要任何改动。

---

## 每个组件可独立替换

这是这个项目最重要的设计决策：**每个槽位都可以换**。

| 组件 | 默认 | 可选 |
|------|------|------|
| VAD | Silero VAD v5 | — |
| STT | Parakeet TDT（NVIDIA） | Whisper、Faster Whisper、Lightning Whisper MLX、Paraformer（FunASR） |
| LLM | OpenAI Responses API（gpt-5.4-mini） | 任意 OpenAI 兼容端点、Transformers、mlx-lm |
| TTS | Qwen3-TTS（GGML/mlx-audio） | Kokoro-82M、Pocket TTS、ChatTTS、MMS TTS |

LLM 槽位接受任何 OpenAI 兼容协议——可以指向 OpenAI、HF Inference Providers，或者指向本地的 vLLM、llama.cpp，实现完全本地运行：

```bash
# 用 llama.cpp 在本地跑 Gemma 4
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF -np 2 -c 65536 -fa on --swa-full

# 把 LLM 后端指向本地服务
speech-to-speech serve \
    --model_name "ggml-org/gemma-4-E4B-it-GGUF" \
    --responses_api_base_url "http://127.0.0.1:8080/v1" \
    --responses_api_api_key ""
```

---

## 三种运行方式

| 命令 | 行为 | 适合场景 |
|------|------|---------|
| `serve` | 启动 Realtime WebSocket 服务器 | 你在开发 App 或设备，需要 API 接口 |
| `talk --url <url>` | 启动麦克风/扬声器客户端 | 连接到已有的 Realtime 服务器 |
| `local` | `serve` + `talk` 合并，一个命令搞定 | 快速本地体验 |

Mac 上一键最优配置：

```bash
speech-to-speech local --mac-optimal-settings
```

这个预设会自动选择：
- Parakeet TDT 做 STT（通过 MLX）
- MLX LM 做 LLM 后端
- Qwen3-TTS 做 TTS（mlx-audio，6bit 量化）

然后从第二个终端连接：

```bash
speech-to-speech talk --url ws://127.0.0.1:8765/v1/realtime
```

---

## 默认组件选择

**VAD**：Silero VAD v5——检测语音边界和轮次转换。

**STT 默认：Parakeet TDT**（NVIDIA）——在 CUDA/CPU 上通过 nano-parakeet 运行，在 Apple Silicon 上通过 MLX 运行。支持实时部分转录。

**LLM 默认**：通过 OpenAI Responses API 调用 gpt-5.4-mini。用 `--model_name` 覆盖模型，用 `--responses_api_base_url` 指向其他 OpenAI 兼容提供商。

**TTS 默认：Qwen3-TTS**——在 Linux/CUDA 上用 GGML 后端，在 macOS Apple Silicon 上用 mlx-audio。模型是 `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`，默认说话人 Aiden，支持自动语言检测。

---

## 生产验证

这个管道不只是演示项目——它是数千台 [Reachy Mini](https://huggingface.co/blog/reachy-mini) 机器人的对话后端，在生产环境实际运行。

---

## 多语言支持

设置 `--qwen3_tts_language` 控制 TTS 语言，设置 `--stt` 切换到支持特定语言的 STT 后端（比如中文用 Paraformer）。`language` 设为 `auto` 时自动检测。

---

## 安装

```bash
pip install speech-to-speech

# 按需安装可选组件
pip install "speech-to-speech[kokoro]"          # Kokoro-82M TTS
pip install "speech-to-speech[pocket]"          # Pocket TTS
pip install "speech-to-speech[faster-whisper]"  # Faster Whisper STT
pip install "speech-to-speech[paraformer]"      # Paraformer（FunASR，中文友好）
pip install "speech-to-speech[mlx-lm]"          # Apple Silicon LLM
```

从源码安装：
```bash
git clone https://github.com/huggingface/speech-to-speech.git
cd speech-to-speech
uv sync
```

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## huggingface/speech-to-speech: A Full Local Voice Agent Pipeline in Three Commands

*by Mycelium Protocol*

---

Getting a talking, listening AI agent running typically means wiring together VAD, STT, LLM, and TTS yourself — each with its own dependencies, latency, and format issues.

`huggingface/speech-to-speech` compresses that to three commands:

```bash
pip install speech-to-speech
export OPENAI_API_KEY=...
speech-to-speech serve
```

GitHub: https://github.com/huggingface/speech-to-speech | ⭐ 12,080 | Apache-2.0 | Python

---

### Pipeline Structure

The voice agent pipeline is four components, each running in its own thread, connected by queues:

```
VAD (Voice Activity Detection)
    ↓
STT (Speech to Text)
    ↓
LLM (Language Model)
    ↓
TTS (Text to Speech)
```

Exposed through an **OpenAI Realtime-compatible WebSocket API** at `ws://localhost:8765/v1/realtime`. Any client that supports the OpenAI Realtime protocol connects directly, no changes needed.

---

### Every Component Is Swappable

The most important design decision: **every slot is replaceable**.

| Stage | Default | Alternatives |
|-------|---------|-------------|
| VAD | Silero VAD v5 | — |
| STT | Parakeet TDT (NVIDIA) | Whisper, Faster Whisper, Lightning Whisper MLX, Paraformer (FunASR) |
| LLM | OpenAI Responses API (gpt-5.4-mini) | Any OpenAI-compatible endpoint, Transformers, mlx-lm |
| TTS | Qwen3-TTS (GGML/mlx-audio) | Kokoro-82M, Pocket TTS, ChatTTS, MMS TTS |

The LLM slot accepts any OpenAI-compatible protocol — point it at OpenAI, HF Inference Providers, or a local vLLM or llama.cpp server for a fully local stack:

```bash
# Local Gemma 4 via llama.cpp
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF -np 2 -c 65536 -fa on --swa-full

# Point the LLM backend at it
speech-to-speech serve \
    --model_name "ggml-org/gemma-4-E4B-it-GGUF" \
    --responses_api_base_url "http://127.0.0.1:8080/v1" \
    --responses_api_api_key ""
```

---

### Three Run Modes

| Command | Behavior | Use when |
|---------|----------|---------|
| `serve` | Starts the Realtime WebSocket server | Building an app or device against the API |
| `talk --url <url>` | Starts the microphone/speaker client | Connecting to an existing server |
| `local` | `serve` + `talk` combined | Quick local test |

Mac optimal settings in one command:

```bash
speech-to-speech local --mac-optimal-settings
```

This preset automatically selects Parakeet TDT for STT (via MLX), MLX LM for the LLM backend, and Qwen3-TTS for TTS (mlx-audio, 6-bit quantization).

---

### Default Stack

**VAD**: Silero VAD v5 — speech boundary and turn-taking detection.

**STT default: Parakeet TDT** (NVIDIA) — runs via nano-parakeet on CUDA/CPU, via MLX on Apple Silicon. Supports real-time partial transcripts.

**LLM default**: OpenAI Responses API with gpt-5.4-mini. Override with `--model_name`; redirect with `--responses_api_base_url` for any compatible provider.

**TTS default: Qwen3-TTS** — GGML backend on Linux/CUDA, mlx-audio on macOS Apple Silicon. Model: `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`, default speaker Aiden, auto language detection.

---

### Production-Validated

This pipeline runs in production as the conversation backend for thousands of [Reachy Mini](https://huggingface.co/blog/reachy-mini) robots — not just a demo.

---

### Install

```bash
pip install speech-to-speech

# Optional components
pip install "speech-to-speech[kokoro]"          # Kokoro-82M TTS
pip install "speech-to-speech[pocket]"          # Pocket TTS
pip install "speech-to-speech[faster-whisper]"  # Faster Whisper STT
pip install "speech-to-speech[paraformer]"      # Paraformer (FunASR, Chinese-friendly)
pip install "speech-to-speech[mlx-lm]"          # Apple Silicon LLM
```

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
