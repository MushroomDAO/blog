---
title: "NVIDIA NemotronLabs VoiceChat 11B：首个支持工具调用的开源全双工语音模型，12.5 Hz 帧率，三通道并行输出"
titleEn: "nvidia-nemotron-voicechat-11b-full-duplex-speech-tool-calling"
description: "NVIDIA NemotronLabs VoiceChat 11B（HF: nvidia/NVIDIA-NemotronLabs-VoiceChat-11B，442 likes，OpenMDW-1.1）是首个开源、全双工、支持工具调用的端到端语音对话模型。不是 ASR→LLM→TTS 的串联流水线，而是单一模型以 12.5 Hz（80ms/帧）同时输出文本、工具调用标记、声学编码三个通道。基于 Nemotron-Nano-9B-v2，架构包含 causal FastConformer 语音编码器 + Nemotron 语言模型 + 功能头 + TTS/编解码器四个模块，总 11B 参数。"
descriptionEn: "NVIDIA NemotronLabs VoiceChat 11B (HF: nvidia/NVIDIA-NemotronLabs-VoiceChat-11B, 442 likes, OpenMDW-1.1) is the first open-source, full-duplex, tool-calling end-to-end speech conversation model. Not an ASR→LLM→TTS cascade — a single model that runs at 12.5 Hz (80ms/frame) and emits three simultaneous channels: text, function-call markers, and acoustic codes. Based on Nemotron-Nano-9B-v2, with a causal FastConformer speech encoder, Nemotron LM, function head, and TTS/codec — 11B total parameters."
pubDate: "2026-08-29"
updatedDate: "2026-08-29"
category: "Tech-News"
tags: ["语音AI", "全双工", "NVIDIA", "Nemotron", "工具调用", "端到端模型", "开源"]
heroImage: "../../assets/images/nvidia-nemotron-voicechat-11b-full-duplex-speech-tool-calling-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

模型：nvidia/NVIDIA-NemotronLabs-VoiceChat-11B | ❤️ 442 | 下载 2,805  
发布：2026-07-29 | 许可证：OpenMDW-1.1 | 语言：英文  
基座：Nemotron-Nano-9B-v2 | 帧率：12.5 Hz（80ms/帧）

---

## 一句话核心

传统语音 Agent = ASR → LLM → TTS（三个模型串联，延迟叠加）。

VoiceChat 11B = **一个模型，一条时间线，同时说话和听话。**

---

## 它解决的是什么问题

当前语音 AI 的主流架构是**瀑布式（Cascaded）流水线**：

```
麦克风输入
  ↓ ASR（语音识别）
  ↓ LLM（文本推理）
  ↓ TTS（文字转语音）
扬声器输出
```

每个模块都有自己的延迟，串联之后端到端延迟往往在500ms-2s之间。更大的问题是：这三个模型之间相互独立，LLM 无法直接感知语音的韵律、停顿、情绪；TTS 也只能合成文字，不知道 LLM 在推理什么。

更麻烦的是**「打断」**——如果你想在 AI 说话时插话，流水线架构需要额外的 VAD（语音活动检测）和 barge-in 逻辑来打断当前的 TTS 播放，而模型本身对此毫无感知。

VoiceChat 11B 的答案：**把这三件事压进一个模型，共享同一套参数，在一条时间线上同步推进。**

---

## 架构：12.5 Hz 的三通道输出

### 帧率机制

VoiceChat 以 **12.5 Hz** 运行——每 80ms 一帧。每帧的计算逻辑：

```
上一帧的 token embedding
    +
当前帧的感知编码器输出（音频）
    ↓
一次前向传播
    ↓
三个并行输出通道：
  [1] 文本通道   → 模型正在「说」的文字
  [2] 功能通道   → 轮次转换信号 + 工具调用 markers
  [3] 声学编码   → 模型自己声音的 codec codes
```

关键点：**音频感知输出不是作为额外 token 插入**，而是直接相加到上一帧的 token embedding 里。这意味着模型在每一帧都能同时感知「我说了什么」和「对方说了什么」，而不需要先把语音转成文字再送进 LLM。

### 「对话是时间线」，不是「消息历史」

传统 LLM 对话有 chat template：`[system][user][assistant][user][assistant]...`，可以把历史消息重新塞进 context window 来继续对话。

VoiceChat 没有 chat template，也没有 history replay。一次对话就是**从第一帧到最后一帧的连续时间线**，每一帧都依赖前一帧的状态。这是为什么社区在为它写 llama.cpp 支持时要重新造一个 `llama-voicechat` 工具——标准的 `llama-mtmd-cli` 把音频作为额外 token 位置插入，而不是相加到帧里，所以根本跑不起来。

### 四个模块

| 模块 | 大小（Q4_0） | 作用 |
|------|------------|------|
| `nemotron_voicechat_11b-stt-llm-Q4_0.gguf` | 4.67 GiB | 语言模型主干（`nemotron_h` 架构） |
| `nemotron_voicechat_11b-stt-llm-Q4_0-function-head.gguf` | 315 MiB | 轮次转换 + 工具调用头 |
| `mmproj-voicechat-perception-Q4_0.gguf` | 435 MiB | Causal FastConformer 语音编码器 |
| `voicechat-tts-Q4_0.gguf` | 686 MiB | 语音生成器 + 音频 codec |

---

## 关键能力：工具调用

这是 NVIDIA 强调的差异点——**首个开源全双工语音模型，支持 function calling**。

功能通道（第二个输出通道）专门用于：
- **轮次边界检测**（turn-taking）：模型知道什么时候该停、什么时候该让对方说
- **工具调用 markers**：可以在语音对话过程中触发外部 API

这意味着语音 Agent 可以在对话流里直接调用工具，而不需要先把语音转成文字、再让 LLM 判断是否要用工具、再把结果合成语音——全部在一个模型的前向传播里完成。

---

## 社区实现（发布后一个月）

模型 2026-07-29 发布，社区已经快速出现了多个平台适配：

| 仓库 | 平台 | 关键特性 |
|------|------|---------|
| `sansamour/llama-voicechat.cpp` | CPU/CUDA（Windows） | llama.cpp 适配，支持 push-to-talk，正确实现 12.5 Hz 时间线 |
| `pipecat-ai/nemotron-voicechat-dgx-spark` | DGX Spark（GB10） | GPTQ W8 量化，Pipecat WebRTC，Smart Turn 检测 |
| `boxwrench/Nemotron-VoiceChat-ROCm` | AMD ROCm / Radeon | Q8 量化，AMD GPU 适配 |
| `zichenzhang04/nemotron-voicechat-modal` | Modal 云端 | 安全全双工浏览器客户端 |
| `Nikki1404/nemotron_voicechat_11B` | Docker | WebSocket + OpenAI 兼容 API |

**pipecat-ai 的 DGX Spark 实现**值得单独说：为了在单台 DGX Spark（GB10）上跑实时推理，他们把 Nano 和 EarTTS 权重做了 GPTQ 量化，把音频 codec 卸载到专用 CPU 核，用 Pipecat Smart Turn 做端点检测，重建了整个服务循环。Bootstrap 下载约 65 GiB，冷启动约 7 分钟，之后完全离线运行。

**llama-voicechat.cpp 的技术细节**最有教育价值：它解释了为什么普通 llama.cpp 跑不了这个模型，并实现了正确的 80ms 帧处理。关键 flag：`VC_NO_BARGE=1` 和 `VC_FORCE_BOS=1`——如果不设，模型会在音频约一秒处就自动「插嘴」回答（这是 full-duplex 行为），对 push-to-talk 场景来说是 bug 而非特性。

---

## 部署快速参考

**基于 Docker（最简路径）**

```bash
# 用 Nikki1404 的实现
docker build -t nemotron-voicechat:latest .
docker run --rm -it --gpus all --ipc=host --shm-size=8g -p 8000:8000 nemotron-voicechat:latest

# WebSocket 语音交互
python client.py --mode ws \
  --server ws://localhost:8000/ws/speech_to_speech/ \
  --mic --seconds 5 --output response.wav --play

# OpenAI 兼容接口
curl -X POST http://localhost:8000/openai-compatible/v1/audio/speech-to-speech \
  -F "file=@sample.wav"
```

**基于 llama-voicechat.cpp（Windows CPU/CUDA）**

```bash
# 下载转换好的 llama.cpp 格式权重
hf download hoidhxd/NVIDIA-NemotronLabs-VoiceChat-11B-GGUF --include "llamacpp/*" --local-dir .

# 问答（WAV 输入 → WAV 输出）
llama-voicechat \
  -m llamacpp/nemotron_voicechat_11b-stt-llm-Q4_0.gguf \
  --mmproj llamacpp/mmproj-voicechat-perception-Q4_0.gguf \
  --tts llamacpp/voicechat-tts-Q4_0.gguf \
  --audio question.wav --tts-out answer.wav

# Push-to-talk 必须加这两个 flag
export VC_NO_BARGE=1 VC_FORCE_BOS=1
```

---

## 许可证注意

VoiceChat 11B 使用 **OpenMDW-1.1**（NVIDIA 自定义许可证），**不是** Apache/MIT 等标准开源许可证。商业使用需要仔细阅读条款。

---

## 与 Moshi / GPT-4o 语音的对比定位

| | VoiceChat 11B | Moshi（Kyutai） | GPT-4o 语音 |
|---|---|---|---|
| 开源权重 | ✅（OpenMDW-1.1） | ✅（CC-BY） | ❌ |
| 全双工 | ✅ | ✅ | ✅ |
| 工具调用 | ✅（首个） | ❌ | ✅（闭源） |
| 参数量 | 11B | 7B | 未知 |
| 帧率 | 12.5 Hz（80ms） | — | — |
| 语言 | 英文 | 英文/法文 | 多语言 |
| 架构 | 单一端到端模型 | 单一端到端模型 | 未知（推测流水线） |

---

**相关链接**

- HuggingFace：https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B
- GGUF 版本：https://huggingface.co/hoidhxd/NVIDIA-NemotronLabs-VoiceChat-11B-GGUF
- llama.cpp 适配：https://github.com/sansamour/llama-voicechat.cpp
- DGX Spark 部署：https://github.com/pipecat-ai/nemotron-voicechat-dgx-spark

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## NVIDIA NemotronLabs VoiceChat 11B: The First Open-Source Full-Duplex Speech Model with Tool Calling

*by Mycelium Protocol*

---

Model: nvidia/NVIDIA-NemotronLabs-VoiceChat-11B | ❤️ 442 | 2,805 downloads  
Published: 2026-07-29 | License: OpenMDW-1.1 | Language: English  
Base: Nemotron-Nano-9B-v2 | Frame rate: 12.5 Hz (80ms/frame)

---

### The One-Sentence Core

Traditional voice agent = ASR → LLM → TTS (three models in series, latencies stacked).

VoiceChat 11B = **one model, one timeline, speaking and listening simultaneously.**

---

### What Problem It Solves

Today's dominant voice AI architecture is the **cascaded pipeline**:

```
Microphone input
  ↓ ASR (speech recognition)
  ↓ LLM (text reasoning)
  ↓ TTS (text-to-speech)
Speaker output
```

Each module has its own latency; stacked together, end-to-end latency runs 500ms–2s. The bigger issue: these three models are independent — the LLM never perceives prosody, pauses, or emotion in the audio; TTS only synthesizes text, unaware of the LLM's reasoning state.

And **interruption** is painful. If you want to speak while the AI is responding, the cascade needs separate VAD (voice activity detection) and barge-in logic to interrupt the TTS stream, while the model itself is oblivious.

VoiceChat 11B's answer: **compress all three tasks into one model, share parameters, advance on a single timeline.**

---

### Architecture: Three-Channel Output at 12.5 Hz

**Frame mechanism**

VoiceChat runs at **12.5 Hz** — one frame every 80ms. Each frame:

```
Previous frame's token embedding
    +
Current frame's perception encoder output (audio)
    ↓
One forward pass
    ↓
Three simultaneous output channels:
  [1] Text channel     → what the model is "saying"
  [2] Function channel → turn-taking signals + tool-call markers
  [3] Acoustic codes   → codec codes for the model's own voice
```

Key point: **audio perception output is not inserted as extra token positions** — it is summed into the previous frame's token embedding. This means the model simultaneously perceives "what I said" and "what the other person said" every 80ms, without converting speech to text first.

**"Conversation is a timeline," not a "message history"**

Traditional LLM chat has a chat template: `[system][user][assistant][user]...`. You can replay the history into the context window to continue a conversation.

VoiceChat has no chat template, no history replay. A conversation is **a continuous timeline from frame one to the last frame**, each frame depending on the previous frame's state. This is exactly why the community had to build a separate `llama-voicechat` tool for llama.cpp — the standard `llama-mtmd-cli` inserts audio as extra token positions instead of summing it into the frame, so it silently ignores the audio. That's the entire reason the fork exists.

**Four modules**

| Module | Size (Q4_0) | Role |
|--------|------------|------|
| `nemotron_voicechat_11b-stt-llm-Q4_0.gguf` | 4.67 GiB | Language model backbone (`nemotron_h`) |
| `nemotron_voicechat_11b-stt-llm-Q4_0-function-head.gguf` | 315 MiB | Turn-taking + tool-call head |
| `mmproj-voicechat-perception-Q4_0.gguf` | 435 MiB | Causal FastConformer speech encoder |
| `voicechat-tts-Q4_0.gguf` | 686 MiB | Speech generator + audio codec |

---

### Key Capability: Tool Calling

This is NVIDIA's stated differentiator — **the first open-source full-duplex speech model to support function calling**.

The function channel (second output channel) handles:
- **Turn-taking detection**: the model knows when to stop and let the other person speak
- **Tool-call markers**: triggers external API calls during the voice conversation flow

A voice agent can invoke tools within the conversation stream without converting speech to text first, deciding whether to use a tool, then synthesizing the result as speech — all in a single model's forward pass.

---

### Community Implementations (One Month Post-Release)

Model published 2026-07-29; the community has already shipped multiple platform adaptations:

| Repo | Platform | Key detail |
|------|----------|-----------|
| `sansamour/llama-voicechat.cpp` | CPU/CUDA (Windows) | llama.cpp adaptation, push-to-talk, correct 12.5 Hz timeline |
| `pipecat-ai/nemotron-voicechat-dgx-spark` | DGX Spark (GB10) | GPTQ W8 quantization, Pipecat WebRTC, Smart Turn endpointing |
| `boxwrench/Nemotron-VoiceChat-ROCm` | AMD ROCm / Radeon | Q8 quantization, AMD GPU adaptation |
| `zichenzhang04/nemotron-voicechat-modal` | Modal cloud | Secure full-duplex browser client |
| `Nikki1404/nemotron_voicechat_11B` | Docker | WebSocket + OpenAI-compatible API |

**pipecat-ai's DGX Spark implementation** deserves a closer look: to sustain real-time inference on a single DGX Spark (GB10), they GPTQ-quantized the Nano and EarTTS weights, offloaded the audio codec to dedicated CPU cores, used Pipecat Smart Turn for endpointing, and rebuilt the entire serving loop. Bootstrap downloads ~65 GiB, cold start takes ~7 minutes, then runs fully offline.

**llama-voicechat.cpp** is the most technically instructive: it explains exactly why standard llama.cpp cannot run this model (audio as additive frame state, not extra token positions), and implements the correct 80ms frame processing. Critical flags: `VC_NO_BARGE=1` and `VC_FORCE_BOS=1` — without them, the model barges in ~1 second into the clip and answers the first second of the question, causing the rest of the turn to degenerate. This is full-duplex behavior, which is correct for continuous conversation but wrong for push-to-talk.

---

### Deployment Quick Reference

**Docker (simplest path)**

```bash
docker build -t nemotron-voicechat:latest .
docker run --rm -it --gpus all --ipc=host --shm-size=8g -p 8000:8000 nemotron-voicechat:latest

# WebSocket voice interaction
python client.py --mode ws \
  --server ws://localhost:8000/ws/speech_to_speech/ \
  --mic --seconds 5 --output response.wav --play

# OpenAI-compatible endpoint
curl -X POST http://localhost:8000/openai-compatible/v1/audio/speech-to-speech \
  -F "file=@sample.wav"
```

**llama-voicechat.cpp (Windows CPU/CUDA)**

```bash
# Download converted llama.cpp weights
hf download hoidhxd/NVIDIA-NemotronLabs-VoiceChat-11B-GGUF --include "llamacpp/*" --local-dir .

# WAV in → WAV out
llama-voicechat \
  -m llamacpp/nemotron_voicechat_11b-stt-llm-Q4_0.gguf \
  --mmproj llamacpp/mmproj-voicechat-perception-Q4_0.gguf \
  --tts llamacpp/voicechat-tts-Q4_0.gguf \
  --audio question.wav --tts-out answer.wav

# Required for push-to-talk
export VC_NO_BARGE=1 VC_FORCE_BOS=1
```

---

### License Note

VoiceChat 11B uses **OpenMDW-1.1** (NVIDIA's custom license), not Apache/MIT. Read the terms carefully before commercial use.

---

### Positioning vs. Moshi / GPT-4o Voice

| | VoiceChat 11B | Moshi (Kyutai) | GPT-4o Voice |
|---|---|---|---|
| Open weights | ✅ (OpenMDW-1.1) | ✅ (CC-BY) | ❌ |
| Full-duplex | ✅ | ✅ | ✅ |
| Tool calling | ✅ (first open) | ❌ | ✅ (closed) |
| Parameters | 11B | 7B | Unknown |
| Frame rate | 12.5 Hz (80ms) | — | — |
| Language | English | English/French | Multilingual |
| Architecture | Single end-to-end | Single end-to-end | Unknown (likely cascade) |

---

**Links**

- HuggingFace: https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B
- GGUF version: https://huggingface.co/hoidhxd/NVIDIA-NemotronLabs-VoiceChat-11B-GGUF
- llama.cpp fork: https://github.com/sansamour/llama-voicechat.cpp
- DGX Spark deployment: https://github.com/pipecat-ai/nemotron-voicechat-dgx-spark

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
