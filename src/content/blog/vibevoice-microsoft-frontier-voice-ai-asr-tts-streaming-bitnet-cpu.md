---
title: "VibeVoice：微软开源的前沿语音 AI 家族，ASR 一次跑60分钟，CPU 也能实时推理"
titleEn: "VibeVoice: Microsoft's Open-Source Frontier Voice AI — 60-Minute ASR in One Pass, Real-Time on CPU"
description: "microsoft/VibeVoice ⭐53474，开源前沿语音 AI 模型家族，ASR 单次处理60分钟音频输出「谁/什么时候/说了什么」，Realtime-0.5B 流式 TTS 首字延迟300ms，ASR-BitNet 无需GPU三线程实时推理，MIT 许可。"
descriptionEn: "microsoft/VibeVoice ⭐53474 — open-source frontier Voice AI family: ASR handles 60-minute audio in one pass with Who/When/What output, Realtime-0.5B streaming TTS at 300ms first-audio latency, ASR-BitNet runs real-time on CPU with no GPU needed. MIT."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Research"
tags: ["speech AI", "ASR", "TTS", "Microsoft", "open source", "voice", "BitNet", "streaming", "LLM", "ICLR"]
heroImage: "../../assets/images/vibevoice-microsoft-frontier-voice-ai-asr-tts-streaming-bitnet-cpu-banner.jpg"
author: "Mycelium Protocol"
---

## 三个模型，覆盖语音 AI 的三个核心场景

微软 2025 年 8 月开始陆续开源 **VibeVoice** 系列——一套前沿语音 AI 模型家族，覆盖长文本转语音、长音频识别和边端实时推理三个核心场景。

⭐ **53,474**，MIT 许可，持续更新到 2026 年 9 月。以下按最新进展从大到小介绍。

---

## 最新：ASR-BitNet——无 GPU，三线程，实时

**2026年7月23日**发布的 **VibeVoice-ASR-BitNet** 是目前最值得关注的更新：

> 通过异构量化（I8_S + I2_S），模型从 4.62 GB 压缩到 **1.58 GB**，在 **3 个以上 CPU 线程**上实现 RTF < 1 的实时推理——不需要 GPU。

这意味着完整的长音频识别能力（60 分钟单次处理、说话人识别、时间戳、50+ 语言）可以在普通笔记本 CPU 上跑起来，不需要 CUDA 环境。

- 代码：[microsoft/VibeASR.cpp](https://github.com/microsoft/VibeASR.cpp)
- 模型：[HuggingFace/VibeVoice-ASR-BitNet](https://huggingface.co/microsoft/VibeVoice-ASR-BitNet)
- 论文：[arxiv.org/abs/2607.21075](https://arxiv.org/abs/2607.21075)

---

## ASR-7B：一次处理60分钟，说清楚"谁/什么时候/说了什么"

**VibeVoice-ASR**（7B 参数）解决的是传统 ASR 的一个核心限制：大多数识别模型需要把长音频切成短片段分批处理，丢失跨段的全局上下文，说话人追踪更是挑战。

VibeVoice-ASR 直接接受最多 **60 分钟**连续音频输入（64K token 长度），单次完成三件事：

| 能力 | 说明 |
|---|---|
| **Who**（说话人识别/区分） | 在整段音频里追踪和区分多个说话人 |
| **When**（时间戳） | 每个片段精确定位到对应时间 |
| **What**（内容转录） | 50+ 语言多语言识别 |

还支持用户提供**自定义热词**（专有名词、技术术语、背景信息），提升领域识别准确率。

**集成路径**：
- HuggingFace Transformers 直接使用（2026-03-06 加入）
- vLLM 加速推理（已支持）
- Azure AI Foundry Labs（2026-03-12 上线）

```python
from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="microsoft/VibeVoice-ASR")
result = asr("your_audio.wav")
# 返回结构化输出：说话人 + 时间戳 + 文字
```

---

## Realtime-0.5B：300ms 首字延迟的流式 TTS

**VibeVoice-Realtime-0.5B** 是轻量实时 TTS 模型，定位和 ASR-7B 互补——一个认声音，一个合成声音：

- **首字延迟**：约 **300 毫秒**（文字输入到开始出声）
- **参数量**：0.5B，面向部署友好
- **流式输入**：支持边写边合成，不需要等完整文本
- **长文本**：单次约 10 分钟，超出可流式接续
- **多语言**：9 种语言实验性支持（德、法、意、日、韩、荷、波、葡、西）+ 11 种英语风格声线

2025 年 12 月 16 日更新加入了多语言声音和不同英语风格（新闻播报、讲故事、技术讲解等），可以直接在 [Colab](https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb) 试用。

---

## TTS-1.5B：已下线，原因是滥用

项目的起点是 2025 年 8 月发布的 **VibeVoice-TTS-1.5B**——一个能在单次推理里合成最多 **90 分钟**、最多 **4 个说话人**的长文本多说话人 TTS 模型，并以 **ICLR 2026 Oral** 被接收。

但开源后不久（2025-09-05），微软发现有人以与初衷不符的方式使用这个模型——代码随即从仓库中下线，只保留论文和技术文档。权重仍在 HuggingFace 上，但代码不再提供。

这是语音 AI 开源里一个值得记录的案例：高质量合成声音的滥用风险促使了一次明确的撤库决定。

---

## 核心技术：7.5 Hz 连续声学标记 + 下一个 Token 扩散

VibeVoice 系列的共同技术基础：

**连续语音 Tokenizer**（声学 + 语义）在 **7.5 Hz 超低帧率**下运行——比传统方法低得多——同时保留音频保真度，大幅减少长序列的计算开销。这是处理 60/90 分钟超长音频的关键。

**下一个 Token 扩散框架**：
- **LLM 理解文本上下文和对话流**（基于 Qwen2.5）
- **扩散头生成高保真声学细节**

这一架构把 LLM 的语义理解能力和扩散模型的高质量声学生成结合在同一个框架里。

---

## 模型概览

| 模型 | 参数 | 用途 | 状态 |
|---|---|---|---|
| VibeVoice-ASR | 7B | 长音频识别（60分钟，多说话人，时间戳）| ✅ 可用 |
| VibeVoice-ASR-BitNet | 1.58 GB | 边端 CPU 实时推理 | ✅ 可用 |
| VibeVoice-Realtime | 0.5B | 实时流式 TTS（300ms 延迟）| ✅ 可用 |
| VibeVoice-TTS | 1.5B | 超长多说话人 TTS（90分钟）| ⚠️ 权重保留，代码下线 |

---

## 快速上手

**ASR（标准 GPU）**：
```bash
pip install transformers
```
```python
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
# 详见 docs/vibevoice-asr.md
```

**ASR-BitNet（CPU 无 GPU）**：
```bash
git clone https://github.com/microsoft/VibeASR.cpp
# 详见 README，需要 3+ CPU 线程
```

**Realtime TTS（Colab 一键运行）**：  
直接打开 [Colab 链接](https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb) 即可试用。

---

## 总结

VibeVoice 在语音 AI 里做了三件有实质区分度的事：

1. **ASR** 把"几分钟短音频"升级到"60分钟完整会议/演讲"，同时输出说话人、时间戳、内容三合一；
2. **ASR-BitNet** 把这个能力压进 CPU，让没有 GPU 的环境也能实时跑；
3. **Realtime TTS** 提供 300ms 延迟的流式合成，适合对话和实时场景。

53k Star，微软研究院出品，持续更新。对于需要在生产里处理长音频、或者需要 CPU 部署的语音场景，VibeVoice 是目前开源里覆盖最完整的选项之一。

**GitHub**: [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) ⭐53474  
**项目主页**: [microsoft.github.io/VibeVoice](https://microsoft.github.io/VibeVoice)  
**ASR Playground**: [aka.ms/vibevoice-asr](https://aka.ms/vibevoice-asr)

<!--EN-->

## VibeVoice: Microsoft's Open-Source Frontier Voice AI Family

Microsoft has been open-sourcing **VibeVoice** since August 2025 — a family of frontier Voice AI models covering long-form TTS, long-audio recognition, and edge real-time inference.

⭐**53,474**, MIT license, actively updated through September 2026. Three models, three use cases.

### Latest: ASR-BitNet — Real-Time on CPU, No GPU

The most significant recent update (**July 23, 2026**) is **VibeVoice-ASR-BitNet**:

> Via heterogeneous quantization (I8_S + I2_S), the model is compressed from 4.62 GB to **1.58 GB**, achieving real-time inference (RTF < 1) on **3+ CPU threads — no GPU required**.

The full 60-minute single-pass ASR capability (speaker diarization, timestamps, 50+ languages) now runs on an ordinary laptop CPU without CUDA.

- Code: [microsoft/VibeASR.cpp](https://github.com/microsoft/VibeASR.cpp)
- Model: [HuggingFace/VibeVoice-ASR-BitNet](https://huggingface.co/microsoft/VibeVoice-ASR-BitNet)
- Paper: [arxiv.org/abs/2607.21075](https://arxiv.org/abs/2607.21075)

### ASR-7B: 60 Minutes in One Pass — Who, When, What

**VibeVoice-ASR** (7B) addresses a core limitation of traditional ASR: most models slice long audio into short chunks (losing global context) and struggle with multi-speaker tracking across segments.

VibeVoice-ASR accepts up to **60 minutes** of continuous audio (64K token length) in a single pass and jointly produces:

| Output | Description |
|---|---|
| **Who** | Speaker diarization — tracking and distinguishing speakers across the full recording |
| **When** | Timestamps for each segment |
| **What** | Transcription in 50+ languages |

Plus **customized hotwords**: provide specific names, technical terms, or background info to guide recognition on domain-specific content.

**Integration paths**:
- HuggingFace Transformers (added March 2026)
- vLLM for accelerated inference
- Azure AI Foundry Labs

```python
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="microsoft/VibeVoice-ASR")
result = asr("your_audio.wav")
# Returns structured output: speaker + timestamp + text
```

### Realtime-0.5B: 300ms First-Audio Streaming TTS

**VibeVoice-Realtime-0.5B** is the lightweight real-time TTS counterpart:

- **~300ms first audible latency** from text input to audio start
- **0.5B parameters** — deployment-friendly
- **Streaming text input** — synthesize as you type, no wait for complete text
- **Long-form**: ~10 minutes single pass, streamable for longer
- **Multilingual**: 9 experimental languages (DE, FR, IT, JP, KR, NL, PL, PT, ES) + 11 English style voices

Try it in [Colab](https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb).

### TTS-1.5B: Code Removed Due to Misuse

The series started with **VibeVoice-TTS-1.5B** in August 2025 — a long-form multi-speaker TTS capable of generating up to **90 minutes** with up to **4 distinct speakers** in a single inference pass, accepted as an **ICLR 2026 Oral**.

Shortly after release (September 5, 2025), Microsoft discovered uses inconsistent with the stated research intent. The code was removed from the repository. The weights remain on HuggingFace; the code does not. A notable case study in open-source speech AI: high-quality voice synthesis can be misused, and Microsoft drew a clear line.

### Core Technology: 7.5 Hz Continuous Tokenization + Next-Token Diffusion

Common technical foundation across the VibeVoice family:

**Continuous speech tokenizers** (Acoustic + Semantic) operating at an ultra-low **7.5 Hz frame rate** — far lower than conventional approaches — while preserving audio fidelity and dramatically reducing compute for long sequences. This is what makes 60-90 minute single-pass generation feasible.

**Next-token diffusion framework**: an LLM (Qwen2.5) handles textual context and dialogue flow; a diffusion head generates high-fidelity acoustic details. LLM semantic understanding + diffusion acoustic quality in one architecture.

### Model Summary

| Model | Size | Use | Status |
|---|---|---|---|
| VibeVoice-ASR | 7B | Long-audio recognition (60 min, multi-speaker, timestamps) | ✅ Available |
| VibeVoice-ASR-BitNet | 1.58 GB | Edge CPU real-time inference | ✅ Available |
| VibeVoice-Realtime | 0.5B | Real-time streaming TTS (300ms latency) | ✅ Available |
| VibeVoice-TTS | 1.5B | Ultra-long multi-speaker TTS (90 min) | ⚠️ Weights only, code removed |

### Summary

VibeVoice makes three meaningfully differentiated contributions to open-source Voice AI:

1. **ASR** upgrades from "short audio clips" to "60-minute complete meetings/talks," jointly outputting speaker, timestamp, and content
2. **ASR-BitNet** compresses this capability to CPU, enabling real-time inference without GPU hardware
3. **Realtime TTS** delivers 300ms latency streaming synthesis for conversational and live use cases

53k stars, Microsoft Research, ongoing updates. For production workloads requiring long-audio processing or CPU-only deployment, VibeVoice is one of the most complete open-source options available.

**GitHub**: [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) ⭐53474  
**Project Page**: [microsoft.github.io/VibeVoice](https://microsoft.github.io/VibeVoice)  
**ASR Playground**: [aka.ms/vibevoice-asr](https://aka.ms/vibevoice-asr)
