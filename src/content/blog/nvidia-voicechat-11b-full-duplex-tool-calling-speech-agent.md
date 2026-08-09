---
title: "NVIDIA VoiceChat 11B：第一个支持工具调用的开源全双工语音 Agent"
titleEn: "NVIDIA VoiceChat 11B: The First Open-Source Full-Duplex Speech Agent with Tool Calling"
description: "NVIDIA NemotronLabs 开源的 11B 端到端全双工语音模型，2026-08-03 发布，OpenMDW 1.1 研究许可。统一架构同时完成流式语音理解和语音生成，转轮延迟约 450ms，VoiceBench #2（开源全双工），史上第一个支持工具调用的开源全双工模型——边说话边触发工具，工具执行期间模型自动播放占位语音保持对话流畅。"
descriptionEn: "NVIDIA NemotronLabs' open-source 11B end-to-end full-duplex speech model, released 2026-08-03, OpenMDW 1.1 research license. Unified architecture for simultaneous streaming speech understanding and generation. ~450ms turn-taking latency, VoiceBench #2 (open FD). First open full-duplex model to support tool calling — tools are called mid-conversation while the model speaks a hold message to keep the flow natural."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["语音AI", "全双工", "工具调用", "NVIDIA", "VoiceAgent", "实时语音", "Mycelium"]
heroImage: "../../assets/images/nvidia-voicechat-11b-full-duplex-tool-calling-speech-agent-banner.jpg"
---

*by Mycelium Protocol*

---

语音 AI 的主流架构是三段级联：ASR（语音转文字）→ LLM（推理）→ TTS（文字转语音）。这个方案的代价是延迟叠加、状态割裂、真实打断（barge-in）难以实现。

NVIDIA NemotronLabs VoiceChat 11B 用一个统一模型做完了这三件事——同时还实现了一个此前无人做过的功能：**在对话进行中触发工具调用**，工具执行时模型自动说一句占位语音（on-hold message），工具返回后无缝继续，整个过程保持自然的对话流。

HuggingFace: https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B | ⭐ 239 likes  
GitHub: https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat  
发布日期：2026-08-03 | License: OpenMDW 1.1（研究用途）

---

## 核心指标

| 维度 | 数值 |
|------|------|
| 参数量 | **11B** |
| 转轮延迟 | **~450 ms** |
| VoiceBench 排名（开源全双工） | **#2** |
| 工具调用 | ✅ **开源全双工首个** |
| 架构类型 | Hybrid Mamba/Transformer |

---

## 架构：四个模块，一次前向传播

```
用户语音 (16kHz)
      │
      ▼
Fast Conformer 语音编码器
(Nemotron-Speech-Streaming-En-0.6b)
      │
      ▼
Nemotron Nano v2 9B LLM 主干
(Hybrid Mamba/Transformer)
      │
      ├──────────────────────────────────┐
      ▼                                  ▼
NVIDIA TTS 解码器 + 编解码器        工具调用通道（独立输出通道）
Agent 语音 (22.05kHz)              工具调用脚本
```

- **Fast Conformer**：流式语音编码，把原始音频映射为音频 token
- **Nemotron Nano v2 9B**：LLM 主干，预测文本 token
- **TTS 解码器**：把文本 token 转为语音 codec，实时合成
- **独立工具调用通道**：和语音流并行输出，不打断语音生成

传统 ASR→LLM→TTS 三跳延迟约 1-2 秒，这套统一架构做到 ~450ms。

---

## 工具调用：边说话边调工具

这是 VoiceChat 最关键的突破。

传统语音助手触发工具时，通常会有一段"请稍等"的停顿，然后说"我帮你查一下……"——期间对话流被打断，用户体验差。

VoiceChat 的实现方式：

1. LLM 生成触发工具调用的文本时，**独立工具调用通道**立即发出工具调用脚本
2. 与此同时，TTS 通道说出为这个工具预定义的 **on-hold 占位语音**（例如"让我查一下……"）
3. 工具返回结果后，模型无缝衔接继续对话

整个过程从用户角度看是连续的自然对话，没有沉默停顿，没有体验断层。

---

## 全双工能力

**真实打断（Barge-in）**：用户说话时可以直接打断模型，模型立即停止输出并响应。不是"等我说完"，而是真正并发的双向流。

**自然转轮（Turn-taking）**：基于 RNNT 的转轮检测，语音结束时自动触发响应，约 450ms 延迟，接近真实人类对话节奏。

**实时用户转写**：对话过程中同步输出用户语音的文字转写，可用于日志和后处理。

---

## 部署方式

**离线推理（HuggingFace checkpoint）**：

```python
# 加载 HF checkpoint 做批量语音转语音测试
# 详见 GitHub 仓库 nemotron-labs-voicechat 分支
```

**实时交互流（NVIDIA NIM 容器）**：

```bash
# 官方 NIM 容器（amd64，需要 NVIDIA A100/H100/H200/B100/B200/RTX-6000）
docker pull nvcr.io/nim/nvidia/nemotron-labs-voicechat
```

支持的硬件：NVIDIA A100 / H100 / H200 / B100 / B200 / RTX-6000（Linux）

官方 NIM 容器仅支持 amd64。在 NVIDIA DGX Spark（aarch64/GB10）上运行需要自行重建服务栈——`jxlarrea/nvidia-voicechat-spark` 仓库记录了一次完整的 DGX Spark 移植实验，结论是最优配置 RTF ~1.13，尚未达到实时（<1.0），供研究参考。

---

## 技术背景

VoiceChat 11B 基于以下组件：

- **基底模型**：[NVIDIA Nemotron Nano 9B v2](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2)
- **语音编码器**：[Nemotron-Speech-Streaming-En-0.6b](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b)（Fast Conformer）
- **训练数据**：~550k 小时音频，含真实语音（Fisher/LibriVox/LibriTTS）+ 合成语音 + Nemotron 5.5 文本数据
- **相关论文**：arXiv 2410.17196 / 2503.04721 / 2604.04847 / 2505.15670 / 2507.08128

---

## 注意事项

- License 为 **OpenMDW 1.1**，仅限研究用途，不适合商业部署
- 目前为 v1 版本，NVIDIA 定性为"研究就绪"，非生产就绪
- RNNT 转轮检测对非语音瞬态（键盘声等）有误触发
- EarTTS 语音质量当前为研究级，和商业 TTS 有差距

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## NVIDIA VoiceChat 11B: The First Open Full-Duplex Voice Agent with Tool Calling

*by Mycelium Protocol*

---

The mainstream architecture for voice AI is a three-stage cascade: ASR (speech-to-text) → LLM (reasoning) → TTS (text-to-speech). The cost: stacked latency, split state, and true barge-in is hard to implement.

NVIDIA NemotronLabs VoiceChat 11B does all three in a single unified model — and adds a capability no open model has offered before: **tool calling mid-conversation**. When a tool is triggered, the model speaks a predefined on-hold message while the tool executes, then seamlessly continues — the conversation never stops.

HuggingFace: https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B  
GitHub: https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat  
Released: 2026-08-03 | License: OpenMDW 1.1 (research only)

---

### Core Metrics

| Dimension | Value |
|-----------|-------|
| Parameters | **11B** |
| Turn-taking latency | **~450 ms** |
| VoiceBench (open FD models) | **#2** |
| Tool calling | ✅ **First open FD model** |
| Architecture | Hybrid Mamba/Transformer |

---

### Architecture: Four Modules, One Forward Pass

```
User audio (16kHz)
        │
        ▼
Fast Conformer Speech Encoder
(Nemotron-Speech-Streaming-En-0.6b)
        │
        ▼
Nemotron Nano v2 9B LLM backbone
(Hybrid Mamba/Transformer)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
NVIDIA TTS Decoder + Codec        Tool-calling channel (separate output)
Agent speech (22.05kHz)           Tool-calling scripts
```

- **Fast Conformer**: streaming speech encoding, maps raw audio to audio tokens
- **Nemotron Nano v2 9B**: LLM backbone, predicts text tokens
- **TTS decoder**: converts text tokens to speech codec, real-time synthesis
- **Separate tool-calling channel**: runs parallel to speech output, no interruption

Traditional ASR→LLM→TTS cascades accumulate ~1-2s of latency. This unified architecture achieves ~450ms.

---

### Tool Calling: Tools Fire While the Model Speaks

This is VoiceChat's key breakthrough.

Traditional voice assistants pause when a tool is triggered — a "please wait" silence, then "let me check…" — breaking the conversational flow.

VoiceChat's approach:
1. When the LLM generates text that triggers a tool call, the **independent tool-calling channel** emits the tool script immediately
2. Simultaneously, the TTS channel speaks the tool's predefined **on-hold message** ("Let me look that up…")
3. When the tool returns, the model continues the conversation seamlessly

From the user's perspective: no silence, no broken flow — a continuous, natural conversation.

---

### Full-Duplex Capabilities

**True barge-in**: the user can interrupt at any time; the model immediately stops and responds. Not "wait for me to finish" — genuinely concurrent bidirectional streams.

**Natural turn-taking**: RNNT-based turn detection, ~450ms response latency, close to natural human conversation rhythm.

**Live user transcription**: real-time text output of user speech alongside the conversation, usable for logs and post-processing.

---

### Deployment

**Offline inference** (HuggingFace checkpoint): batch speech-to-speech testing.

**Interactive streaming** (NVIDIA NIM container):

```bash
docker pull nvcr.io/nim/nvidia/nemotron-labs-voicechat
```

Supported hardware: NVIDIA A100 / H100 / H200 / B100 / B200 / RTX-6000 (Linux, amd64).

The official NIM container is amd64-only. Running on NVIDIA DGX Spark (aarch64/GB10) requires rebuilding the serving stack — the `jxlarrea/nvidia-voicechat-spark` repository documents a full Spark porting experiment, concluding that the best configuration reaches RTF ~1.13 (real-time requires < 1.0), for research reference.

---

### Notes

- License: **OpenMDW 1.1** — research use only, not suitable for commercial deployment
- v1 is "research-ready," not production-ready per NVIDIA's own characterization
- RNNT turn detection can hallucinate from non-speech transients (keyboard clicks, etc.)
- EarTTS voice quality is currently research-grade, below commercial TTS

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
