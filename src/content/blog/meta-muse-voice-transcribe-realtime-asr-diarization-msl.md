---
title: "Meta Muse Voice Transcribe：MSL 首款实时音频感知模型，单模型做 ASR + 说话人分离 + 端点检测"
titleEn: "Meta Muse Voice Transcribe: MSL's First Real-Time Audio Model — ASR + Diarization + Endpointing in One"
description: "Meta Superintelligence Labs 发布 Muse Voice Transcribe，首款实时音频感知模型，单模型集成流式 ASR、20+ 说话人分离和端点检测，支持多语言无缝切换，通过 RL 训练的自适应延迟机制登顶 Artificial Analysis 流式语音识别和公开说话人分离排行榜。"
descriptionEn: "Meta Superintelligence Labs releases Muse Voice Transcribe, their first real-time audio perception model integrating streaming ASR, 20+ speaker diarization, and endpointing in a single model, with multilingual code-switching and RL-trained adaptive delay for a new Pareto frontier on speed/accuracy."
pubDate: 2026-09-03
updatedDate: 2026-09-03
category: Tech-News
tags: ["AI", "ASR", "Meta", "语音识别", "说话人分离", "实时", "MSL"]
heroImage: "../../assets/images/meta-muse-voice-transcribe-realtime-asr-diarization-msl-banner.jpg"
author: "Mycelium Protocol"
---

2026年9月1日，Zuckerberg 发推：

> "Muse Voice Transcribe is MSL's first real-time audio perception model -- rolling out today. SOTA in streaming speech-to-text, it handles speaker diarization, and endpointing natively in a single model."

**Muse Voice Transcribe**，Meta Superintelligence Labs 在 Muse Spark 系列之后推出的第一款音频模型，正式进入 Meta Muse 产品家族。

---

## 这个模型解决了什么问题

实时语音系统的老大难问题：**ASR（转写）、说话人分离、端点检测通常是三个独立模型，各自优化、相互割裂。**

在真实场景里，一段电话录音、一段会议音频，你需要：
1. 把语音转成文字（ASR）
2. 区分谁在说话（说话人分离 / Diarization）
3. 判断一句话说完了没有（端点检测 / Endpointing）

以前这三件事要串联三个模型，延迟叠加，错误也会传递。Muse Voice Transcribe 把它们合并成一个实时流式模型。

---

## 核心特性

**流式实时 ASR**：不是录音后处理，是边说边出字，支持小时级别的长音频，不截断。

**20+ 说话人分离**：会议、电话、访谈场景中，可以同时区分超过 20 个说话人，每个字都带说话人标签。

**内置端点检测**：模型自己判断"这句话说完了"，无需外部 VAD（语音活动检测）。早期系统把这三件事拼在一起，端点检测的误判会导致 ASR 提前截断或延迟，Muse Voice Transcribe 原生集成，减少了这个误差源。

**多语言 + 无缝语码切换**：支持多语言，同一段音频里中英文混说（code-switching），模型可以无缝跟上，不需要预先指定语言。

**语境偏置（Context Biasing）**：支持语言偏置、关键词偏置、上下文偏置——给模型提示"这段音频大概是关于什么的"或者"注意识别这些专有名词"，可以显著提升特定领域的准确率。

---

## 关键技术：自适应延迟（Adaptive Delay）

这是 Muse Voice Transcribe 最核心的技术创新，也是它在速度/准确率权衡上达到新 Pareto 前沿的原因。

**问题背景**：流式 ASR 的根本矛盾——说话人刚说完半句话，模型要不要现在就输出这一段？

- **太早输出**：可能识别错，因为后续词会改变上下文（"我觉得这件事……很好"和"我觉得这件事……很糟"，前几个字完全一样）
- **太晚输出**：用户体验差，感知延迟高

以前的做法是设一个固定的延迟窗口（比如"总是等 200ms 再输出"），这是静态的，无法区分"简单词"和"困难词"。

Muse Voice Transcribe 通过 **RL 训练自适应延迟**——模型学会了"这个词我已经有足够信心了，现在就输出"和"这个词有歧义，我再等一帧"。结果是：大部分词立刻输出，只在少数困难词上额外等待。**平均延迟没有显著增加，但准确率明显提升。**

据 Bowen Cheng（模型负责人）的推文描述："We give full control on when and how long to listen to audio back to the model. And with RL, it learns 'adaptive delay' to wait longer only on a few hard words."

---

## 评测结果

- **Artificial Analysis 流式语音识别排行榜**：第一名
- **公开说话人分离基准测试**：第一名

两个维度同时登顶，这对一个"多合一"模型来说并不容易——通常多任务模型在每个子任务上都会有所妥协。

---

## 与 Qwen3-ASR 的对比

上一篇文章刚介绍了 Qwen3-ASR，两者正好可以做个横向比较：

| 维度 | Muse Voice Transcribe | Qwen3-ASR-1.7B |
|------|----------------------|----------------|
| 开源 | 否（API 服务） | 是（Apache-2.0） |
| 说话人分离 | 内置，20+ 说话人 | 不支持 |
| 端点检测 | 内置 | 不支持 |
| 自适应延迟 | RL 训练，核心创新 | 无 |
| 多语言 | 支持，无缝切换 | 52种语言 |
| 部署方式 | Meta Model API / Meta AI App | 本地 NVIDIA GPU |
| 硬件要求 | 无（云端） | RTX 3060+ |
| 适合场景 | 会议、电话、多说话人场景 | 单说话人转写、批量处理 |

选哪个取决于需求：
- **需要说话人分离 + 端点检测**：Muse Voice Transcribe
- **需要本地部署 + 数据隐私**：Qwen3-ASR
- **需要中文方言**：Qwen3-ASR（22种方言）

---

## 获取方式

目前通过三个渠道访问：

1. **Meta Model API**：面向开发者，API 接入，与 Muse Spark 同平台
2. **Meta AI for Mac**：Mac 桌面客户端内置
3. **Muse Code**：Meta 的代码开发工具集成

---

## 意义：Muse 家族的音频拼图

回顾 Muse 系列的发布时间线：

- **Muse Spark**（Muse 系列首个推理模型）→ 多模态理解和推理
- **Muse Image + Muse Video**（图像/视频生成）→ 视觉创作
- **Muse Spark 1.1**（Agent 增强版）→ 代码、Computer Use、长上下文
- **Muse Voice Transcribe**（今日）→ 音频感知

Meta Superintelligence Labs 正在把视觉、文本、音频逐一补全，向"个人超智能"的完整感知能力推进。音频是最后补上的一块——也是 Meta 的 Ray-Ban 眼镜、AR 眼镜等硬件产品真正需要的实时能力。

---

## 相关链接

- Meta AI Blog：[ai.meta.com/blog](https://ai.meta.com/blog/)
- Zuckerberg 原推：[@finkd](https://x.com/finkd)
- Meta Model API：[developer.meta.com/ai](https://developer.meta.com/ai/)
- 上一篇：Qwen3-ASR 小企业双语语音 AI 部署指南

<!--EN-->

On September 1, 2026, Zuckerberg posted:

> "Muse Voice Transcribe is MSL's first real-time audio perception model -- rolling out today. SOTA in streaming speech-to-text, it handles speaker diarization, and endpointing natively in a single model."

**Muse Voice Transcribe**, Meta Superintelligence Labs' first audio model following the Muse Spark series, now officially joins the Muse family.

---

## The Problem It Solves

Real-time voice systems have always had a core pain point: **ASR (transcription), speaker diarization, and endpointing are typically three separate models — each optimized independently, combined awkwardly.**

In practice, for a phone call or meeting recording, you need to:
1. Convert speech to text (ASR)
2. Identify who said what (Speaker Diarization)
3. Detect when a sentence ends (Endpointing)

Previously, these required three models in sequence, stacking latency and compounding errors. Muse Voice Transcribe merges all three into a single real-time streaming model.

---

## Core Capabilities

**Streaming real-time ASR**: Not post-processing — characters stream out as the speaker talks. Supports hour-long audio without truncation.

**20+ speaker diarization**: In meetings, calls, and interviews, distinguishes 20+ simultaneous speakers, each word labeled by speaker identity.

**Native endpointing**: The model judges "this sentence is complete" internally — no external VAD (Voice Activity Detection) needed. Early systems combined these three components externally; endpointing misclassification would truncate or delay ASR output. Native integration reduces this error source.

**Multilingual + seamless code-switching**: Supports multiple languages; mid-sentence language switches (Chinese ↔ English) are handled natively without pre-specifying the language.

**Context biasing**: Language biasing, keyword biasing, and context biasing are all supported — give the model hints about domain or specific terms to significantly boost accuracy in specialized scenarios.

---

## Key Innovation: Adaptive Delay

This is Muse Voice Transcribe's core technical contribution — what puts it at a new Pareto frontier on the speed/accuracy tradeoff.

**The background problem**: Streaming ASR faces a fundamental tension — when the speaker is mid-sentence, should the model output now?

- **Output too early**: Risk of errors, since upcoming words change context ("I think this is... great" vs. "I think this is... terrible" — the early words are identical)
- **Output too late**: Poor UX, high perceived latency

Prior systems used a fixed delay window (e.g., "always wait 200ms before output") — static, unable to distinguish easy from hard words.

Muse Voice Transcribe uses **RL-trained adaptive delay** — the model learns "I'm confident enough about this word, output now" vs. "this word is ambiguous, wait one more frame." Result: most words output immediately; only a few hard words trigger extra waiting. **Average latency doesn't increase significantly, but accuracy improves meaningfully.**

From Bowen Cheng (model lead) on Twitter: "We give full control on when and how long to listen to audio back to the model. And with RL, it learns 'adaptive delay' to wait longer only on a few hard words."

---

## Benchmark Results

- **Artificial Analysis streaming speech-to-text leaderboard**: #1
- **Public diarization benchmarks**: #1

Topping both simultaneously is notable for a "multi-task in one" model — typically multi-task models trade off each sub-task against each other.

---

## Comparison with Qwen3-ASR

Our previous article covered Qwen3-ASR — a useful side-by-side:

| Dimension | Muse Voice Transcribe | Qwen3-ASR-1.7B |
|-----------|----------------------|----------------|
| Open source | No (API service) | Yes (Apache-2.0) |
| Speaker diarization | Built-in, 20+ speakers | Not supported |
| Endpointing | Built-in | Not supported |
| Adaptive delay | RL-trained, core innovation | None |
| Multilingual | Yes, seamless code-switching | 52 languages |
| Deployment | Meta Model API / App | Local NVIDIA GPU |
| Hardware | None (cloud) | RTX 3060+ |
| Best for | Meetings, calls, multi-speaker | Single-speaker, batch |

Which to choose depends on needs:
- **Need diarization + endpointing**: Muse Voice Transcribe
- **Need local deployment + data privacy**: Qwen3-ASR
- **Need Chinese dialects**: Qwen3-ASR (22 dialects)

---

## Access

Currently available via three channels:

1. **Meta Model API**: Developer access, same platform as Muse Spark
2. **Meta AI for Mac**: Built into the Mac desktop client
3. **Muse Code**: Integrated in Meta's developer coding tool

---

## Significance: The Audio Piece of the Muse Puzzle

The Muse family release timeline:

- **Muse Spark** → Multimodal reasoning
- **Muse Image + Muse Video** → Visual creation
- **Muse Spark 1.1** → Agentic coding, Computer Use, long context
- **Muse Voice Transcribe** (today) → Audio perception

Meta Superintelligence Labs is completing vision, text, and audio one by one — building toward "personal superintelligence" with full perceptual coverage. Audio was the last piece — and also the real-time capability that Meta's Ray-Ban glasses and future AR hardware actually need in the field.

---

## Links

- Meta AI Blog: [ai.meta.com/blog](https://ai.meta.com/blog/)
- Zuckerberg's announcement: [@finkd on X](https://x.com/finkd)
- Meta Model API: [developer.meta.com/ai](https://developer.meta.com/ai/)
- Previous article: Qwen3-ASR Small Business Bilingual Voice AI Guide
