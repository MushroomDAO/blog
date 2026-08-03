---
title: "HuggingFace Speech-to-Speech：一行安装本地语音助手，延迟低到像真人，驱动数千台机器人"
titleEn: "huggingface-speech-to-speech-local-voice-agent-robot-pipeline"
description: "huggingface/speech-to-speech 是一个低延迟、全模块化的本地语音 Agent 流水线（VAD → STT → LLM → TTS），兼容 OpenAI Realtime API。10.6K stars，Apache 2.0，`pip install speech-to-speech` 一行启动。已在数千台 Reachy Mini 机器人的对话后端中跑生产。每个组件均可替换，Apple Silicon 原生支持。"
descriptionEn: "huggingface/speech-to-speech is a low-latency, fully modular local voice agent pipeline (VAD → STT → LLM → TTS) with OpenAI Realtime API compatibility. 10.6K stars, Apache 2.0, one-line install. Runs in production as the conversation backend for thousands of Reachy Mini robots. Every component is swappable; Apple Silicon natively supported."
pubDate: "2026-08-03"
updatedDate: "2026-08-03"
category: "Tech-News"
tags: ["语音Agent", "TTS", "STT", "HuggingFace", "本地部署", "机器人", "OpenAI兼容", "Mycelium"]
heroImage: "../../assets/images/huggingface-speech-to-speech-local-voice-agent-robot-pipeline-banner.jpg"
---

*by Mycelium Protocol*

---

用语音和 AI 聊天，延迟是最大的体验杀手。云端 API 的来回往返、各组件串行等待——很难做到真人对话的感觉。

**[HuggingFace Speech-to-Speech](https://github.com/huggingface/speech-to-speech)**（10.6K stars）换了一个思路：把整条流水线搬到本地，每个阶段跑在独立线程、通过队列连接，结果是延迟低到可以真正"对话"的程度。

这不是一个演示项目——它现在是**数千台 Reachy Mini 机器人的生产级对话后端**。

---

## 一行启动

```bash
pip install speech-to-speech
export OPENAI_API_KEY=...
speech-to-speech
```

启动之后，你得到一个运行在 `ws://localhost:8765/v1/realtime` 的 WebSocket 服务——**完全兼容 OpenAI Realtime API**。任何已经对接了 OpenAI Realtime 的客户端，改一个端点地址就能切过来，不用改任何代码。

---

## 四阶段流水线

```
麦克风输入
    ↓
[VAD] Silero VAD v5 — 检测说话边界和轮换时机
    ↓
[STT] 语音转文字 — Parakeet TDT（默认）/ Whisper 系列 / Paraformer
    ↓
[LLM] 语言模型 — OpenAI API / Transformers / mlx-lm（本地）
    ↓
[TTS] 文字转语音 — Qwen3-TTS（默认）/ Kokoro / Pocket TTS / ChatTTS
    ↓
扬声器输出（流式）
```

四个阶段各自跑在独立线程，通过队列传数据，**并发流水作业**——上一阶段的输出还在生成，下一阶段已经开始处理。这是延迟低的关键。

---

## 每个组件都能换

| 类别 | 默认 | 其他选项 |
|------|------|---------|
| VAD | Silero VAD v5 | — |
| STT | Parakeet TDT 0.6B v3 | Whisper（Transformers）、Faster Whisper、Lightning Whisper MLX、Paraformer（FunASR） |
| LLM | OpenAI Responses API（gpt-5.4-mini） | Transformers、mlx-lm、llama.cpp、vLLM、任意 OpenAI 兼容端点 |
| TTS | Qwen3-TTS 1.7B（GGML） | Kokoro-82M、Pocket TTS、ChatTTS、MMS TTS |

切换方式：`--stt`、`--llm_backend`、`--tts` 三个 CLI 参数。

---

## Apple Silicon 一键最优配置

```bash
speech-to-speech --local_mac_optimal_settings
```

自动设置：
- 所有模型用 MPS 加速（`--device mps`）
- STT：Parakeet TDT
- LLM：MLX LM（本地推理，无需 API key）
- TTS：Qwen3-TTS，mlx-audio 后端，6bit 量化

指定 LLM：

```bash
speech-to-speech \
    --local_mac_optimal_settings \
    --model_name mlx-community/Qwen3-4B-Instruct-2507-bf16
```

完全本地，完全开源，不需要任何云端 API。

---

## 四种运行模式

| 模式 | 传输 | 适用场景 |
|------|------|---------|
| `realtime`（默认） | OpenAI Realtime 协议 / WebSocket + WebRTC | 对接标准 Realtime 客户端或应用 |
| `local` | 本机麦克风和扬声器 | 直接和流水线说话，无需客户端 |
| `raw-websocket` | 原始 PCM / WebSocket | 自定义轻量客户端 |
| `socket` | 原始 PCM / TCP | 模型跑在远程服务器，本地做音频输入输出 |

### 本地 LLM（llama.cpp 示例）

```bash
# 本地起 Gemma 4
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF -np 2 -c 65536 -fa on --swa-full

# 指向本地端点
speech-to-speech \
    --model_name "ggml-org/gemma-4-E4B-it-GGUF" \
    --responses_api_base_url "http://127.0.0.1:8080/v1" \
    --responses_api_api_key ""
```

### Docker（开箱即用）

```bash
docker compose up
```

compose 文件自动启动 llama.cpp + Gemma 4 + TCP socket 服务，开放 8080、12345、12346 端口。

---

## 已在生产中跑数千台机器人

Speech-to-Speech 是 **[Reachy Mini](https://huggingface.co/blog/reachy-mini)** 的对话后端。Reachy Mini 是 HuggingFace 推出的开源桌面机器人，这套流水线在数千台设备上跑生产流量——不是实验室演示。

---

## 可选扩展

```bash
pip install "speech-to-speech[kokoro]"         # Kokoro-82M TTS
pip install "speech-to-speech[pocket]"         # Pocket TTS
pip install "speech-to-speech[faster-whisper]" # Faster Whisper STT
pip install "speech-to-speech[whisper-mlx]"    # Lightning Whisper MLX（macOS）
pip install "speech-to-speech[paraformer]"     # Paraformer STT（FunASR，中文友好）
pip install "speech-to-speech[mlx-lm]"         # mlx-vlm 支持视觉模型（macOS）
```

中文用户注意：`paraformer` 后端来自 FunASR，对中文语音识别支持更好。

---

## 为什么值得关注

**低延迟语音 Agent 一直是"理论上可行，工程上难落地"的领域**。Speech-to-Speech 把这件事做成了一个 `pip install` 就能跑的工具，还兼容 OpenAI Realtime API（意味着你用 OpenAI 写的 Realtime 客户端代码直接复用）。

组件化设计意味着你可以渐进式替换：先用云端 LLM 快速验证，再换本地模型降成本；STT 和 TTS 也可以按语言、延迟、资源限制分别选型。

10.6K stars，生产验证，Apache 2.0，没有比这更低的上手门槛了。

仓库：[github.com/huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech) · PyPI：[speech-to-speech](https://pypi.org/project/speech-to-speech/)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## HuggingFace Speech-to-Speech: One-Line Local Voice Agent, Human-Like Latency, Powers Thousands of Robots

*by Mycelium Protocol*

Latency is the biggest experience killer in voice AI. Cloud API round trips, sequential stage waiting — it's hard to achieve the feel of real human conversation.

**[HuggingFace Speech-to-Speech](https://github.com/huggingface/speech-to-speech)** (10.6K stars) takes a different approach: move the entire pipeline local, run each stage in its own thread connected by queues, and achieve latency low enough for genuine back-and-forth conversation.

This isn't a demo project — it runs in production as the **conversation backend for thousands of Reachy Mini robots**.

### One-Line Start

```bash
pip install speech-to-speech
export OPENAI_API_KEY=...
speech-to-speech
```

This starts a WebSocket service at `ws://localhost:8765/v1/realtime` that is **fully compatible with the OpenAI Realtime API**. Any client already integrated with OpenAI Realtime can switch over by changing a single endpoint URL — no code changes required.

### The Four-Stage Pipeline

```
Microphone input
    ↓
[VAD] Silero VAD v5 — speech boundary detection and turn-taking
    ↓
[STT] Speech to text — Parakeet TDT (default) / Whisper family / Paraformer
    ↓
[LLM] Language model — OpenAI API / Transformers / mlx-lm (local)
    ↓
[TTS] Text to speech — Qwen3-TTS (default) / Kokoro / Pocket TTS / ChatTTS
    ↓
Speaker output (streaming)
```

The four stages run in separate threads connected by queues, processing **concurrently in pipeline fashion**: while one stage is still generating output, the next stage is already consuming it. This is the key to the low latency.

### Every Component Is Swappable

| Category | Default | Alternatives |
|----------|---------|--------------|
| VAD | Silero VAD v5 | — |
| STT | Parakeet TDT 0.6B v3 | Whisper (Transformers), Faster Whisper, Lightning Whisper MLX, Paraformer (FunASR) |
| LLM | OpenAI Responses API (gpt-5.4-mini) | Transformers, mlx-lm, llama.cpp, vLLM, any OpenAI-compatible endpoint |
| TTS | Qwen3-TTS 1.7B (GGML) | Kokoro-82M, Pocket TTS, ChatTTS, MMS TTS |

Switch with `--stt`, `--llm_backend`, and `--tts` CLI flags.

### Apple Silicon One-Command Optimal Setup

```bash
speech-to-speech --local_mac_optimal_settings
```

Automatically configures: MPS acceleration for all models, Parakeet TDT for STT, MLX LM for local inference (no API key), Qwen3-TTS with mlx-audio at 6-bit quantization.

Specify a local LLM:

```bash
speech-to-speech \
    --local_mac_optimal_settings \
    --model_name mlx-community/Qwen3-4B-Instruct-2507-bf16
```

Fully local, fully open-source, no cloud API required.

### Four Run Modes

| Mode | Transport | When to use |
|------|-----------|-------------|
| `realtime` (default) | OpenAI Realtime protocol over WebSocket/WebRTC | Building against a standard voice API |
| `local` | Machine's microphone and speakers | Talk directly to the pipeline, no client needed |
| `raw-websocket` | Raw PCM over WebSocket | Minimal custom client without Realtime protocol |
| `socket` | Raw PCM over TCP | Models on remote server, audio in/out on local client |

**Fully local LLM with llama.cpp:**

```bash
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF -np 2 -c 65536 -fa on --swa-full

speech-to-speech \
    --model_name "ggml-org/gemma-4-E4B-it-GGUF" \
    --responses_api_base_url "http://127.0.0.1:8080/v1" \
    --responses_api_api_key ""
```

### Production: Thousands of Robots

Speech-to-Speech runs in production as the conversation backend for [Reachy Mini](https://huggingface.co/blog/reachy-mini), HuggingFace's open-source desktop robot. Thousands of devices, real production traffic — not a lab demo.

### Why This Matters

**Low-latency voice agents have long been "theoretically possible, practically hard."** Speech-to-Speech makes it a `pip install` away, with OpenAI Realtime API compatibility so existing Realtime client code just works.

The modular design enables progressive substitution: start with a cloud LLM for quick validation, swap in a local model to cut costs; choose STT and TTS independently based on language requirements, latency targets, and hardware constraints.

10.6K stars, production-validated, Apache 2.0. No lower barrier to entry exists.

Repository: [github.com/huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech) · PyPI: [speech-to-speech](https://pypi.org/project/speech-to-speech/)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
