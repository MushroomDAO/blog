---
title: "LiquidAI d1：不生成一个 token 就给出决策的多模态边缘模型"
titleEn: "LiquidAI d1: Multimodal Edge Decision Models That Return a Result Without Generating a Single Token"
description: "LiquidAI 开源 d1-3B 和实验性 d1-omni-600M，lfm1.0 许可。d1 的核心设计是零输出 token：模型直接读取 logit，不生成任何文字就返回决策结果，延迟恒定不随输出长度变化。d1-3B（3.12B 参数，SigLIP2 视觉编码器）在 Decision Index v0.2.1 的 10B 以下模型中排名第一，得分 48.57，超过 Decider 35B-A3B（47.11）。RTX 4090 单次文本决策约 8ms，Jetson AGX Thor 约 16ms，苹果 M5 Pro 约 30ms，day-one 提供 llama.cpp 支持。d1-omni-600M 进一步支持文本+音频输入，600M 体积适合端侧语音路由和内容审核。"
descriptionEn: "LiquidAI releases d1-3B and experimental d1-omni-600M under the lfm1.0 license. The core design: d1 returns a decision by reading logits directly, generating zero output tokens — latency is constant regardless of answer complexity. d1-3B (3.12B parameters, SigLIP2 vision encoder) ranks #1 under 10B on Decision Index v0.2.1 at 48.57, above Decider 35B-A3B (47.11). ~8ms per text decision on RTX 4090, ~16ms on Jetson AGX Thor, ~30ms on Apple M5 Pro, with day-one llama.cpp support. d1-omni-600M adds text+audio inputs, targeting on-device voice routing and content moderation at 600M parameters."
pubDate: 2026-10-08
heroImage: "../../assets/images/liquidai-d1-3b-omni-600m-decision-model-zero-output-tokens-edge-banner.jpg"
category: "Tech-Experiment"
tags: ["AI Agent", "边缘计算", "决策模型", "多模态", "本地工具", "开源模型"]
lang: "zh-CN"
wechatTitle: "LiquidAI d1：零输出token的多模态决策模型"
wechatDigest: "lfm1.0；d1-3B 3B/omni 600M；零token决策；DI 10B第一；8ms；Jetson"
---

大多数模型的推理过程是：输入 → 思考 → 输出文字。

d1 把最后一步扔掉了。

**d1 直接读 logit，不生成任何 token，就返回决策结果。** 你问"这条内容违规吗"，它不会输出"是"或者"否"，而是直接给你概率分布里的那个选择。延迟不随决策复杂度变化，因为根本没有解码过程。

HuggingFace: https://huggingface.co/LiquidAI/d1-3B | ⭐ 83 | lfm1.0

---

## 两款模型

LiquidAI 这次发布了两个模型：

**d1-3B**（正式发布）
- 3.12B 总参数
- 视觉编码器：SigLIP2 NaFlex shape-optimized 400M
- 上下文：32K token，词表 128K
- 输入：文本 + 图像

**d1-omni-600M**（实验性）
- 600M 参数
- 输入：文本+图像，**或**文本+音频
- 更小体积，面向端侧语音路由和内容审核

---

## 零 token 输出是怎么工作的

传统分类方法：让模型生成"yes"/"no"/"A"/"B"，再解析文字。这有两个问题：一是输出长度不确定，二是有时模型会绕弯子解释而不是直接选。

d1 的做法不同——它的推理头直接输出目标标签的概率分布，不经过自回归解码。好处：

- **延迟恒定**：不论问题多复杂，决策延迟就是一次前向传播
- **不会"解释绕路"**：无法生成文字，只能给答案
- **与 Agent 管道友好**：返回值是结构化分数，不需要后处理解析文字

这和 Jev / TypeSafe AI 的 `/v1/systemone` 接口思路一致，区别是 d1 把这个特性做进了模型架构本身，而不是通过推理技巧实现。

---

## 性能数字

**d1-3B 的 Decision Index v0.2.1 得分：48.57**

| 模型 | 参数量 | DI v0.2.1 |
|------|--------|-----------|
| d1-3B | 3B | **48.57** |
| Decider 35B-A3B | 35B | 47.11 |
| （其他 4B/9B 模型） | — | < 47 |

3B 参数打过 35B-A3B，在 10B 以下模型里排名第一。Decision Index 是 LiquidAI 自己发布的 benchmark（数据集：LiquidAI/d1-decision-index），尚无第三方独立验证。

**d1-3B 文本 benchmark（7 个公开数据集，均值 82.9）**

| Benchmark | 分数 |
|-----------|------|
| SQuAD 2.0 | 85.3 |
| XNLI | 85.0 |
| DecisionBench | 71.8 |

**d1-3B 图像 benchmark**：11 个公开数据集均值 74.1

---

## 延迟实测（d1-3B）

| 硬件 | 文本决策 | 图像决策 |
|------|----------|----------|
| RTX 4090 | **8ms** | 17ms |
| Jetson AGX Thor | ~16ms | — |
| Apple M5 Pro | 30ms | 62ms |
| Jetson Orin Nano | 50ms | 202ms |

边缘侧推理能跑进 50ms 以内，Jetson Orin Nano 的图像延迟 202ms 在实时场景下偏慢，但静态审核或批量检查够用。

---

## 硬件与部署支持

- NVIDIA：DGX、RTX 系列、Jetson 全系
- Apple：M5 Pro（llama.cpp 路径）
- AMD：MI325X
- **Day-one llama.cpp 支持**（官方提供 GGUF）

不需要专有推理框架，标准 llama.cpp 可直接运行。

---

## d1-omni-600M 的多模态组合

d1-omni-600M 是首个同时支持**图像**和**音频**输入的 600M 级决策模型。官方标注为"实验性"，目标场景：

- **语音指令路由**：音频 → 直接路由到对应工具，无需先 ASR 转文字
- **端侧内容审核**：文本+图像联合判断，600M 在手机/边缘设备上可运行
- **意图分类**：多模态输入 → 分类标签，无文字生成开销

⚠️ d1-omni-600M 目前是实验版本，不适合直接用于生产。

---

## 许可证说明

两款模型使用 **lfm1.0**（LiquidAI Foundation Model License 1.0），不是 Apache-2.0 或 MIT。lfm1.0 允许研究和非商业使用，商业部署超过一定规模需要另行授权。在集成进产品前，建议仔细阅读许可证条款。

---

## 一句话说清楚

d1 是 LiquidAI 的决策模型系列：3B 视觉模型打过 35B 竞品，600M 实验版支持音频，核心设计是零 token 输出——不生成文字，直接读概率，RTX 4090 上 8ms 一个决策。许可证是 lfm1.0，商业用途注意。

---

> lfm1.0 许可。LiquidAI 2026-10-07 发布，HuggingFace 已上线。开源仅供学习参考。

---

<!--EN-->

## LiquidAI d1: Multimodal Edge Decision Models That Return a Result Without Generating a Single Token

Most models work by: input → reasoning → text output. d1 drops the last step.

**d1 reads logits directly and returns a decision without generating any tokens.** Ask "is this content violating policy?" and instead of outputting "yes" or "no", it returns the result from the probability distribution directly. Latency doesn't scale with answer complexity because there's no decoding step.

HuggingFace: https://huggingface.co/LiquidAI/d1-3B | ⭐ 83 | lfm1.0

---

### Two Models

**d1-3B** (released)
- 3.12B total parameters
- Vision encoder: SigLIP2 NaFlex shape-optimized 400M
- Context: 32K tokens, vocab 128K
- Inputs: text + image

**d1-omni-600M** (experimental)
- 600M parameters
- Inputs: text+image, **or** text+audio
- Targets on-device voice routing and content moderation

---

### How Zero Output Tokens Works

Standard classification: prompt the model to generate "yes"/"no"/"A"/"B", then parse the text. Problems: variable latency and occasional "explanation detours."

d1's inference head outputs the target label's probability distribution directly, bypassing autoregressive decoding. Result:

- **Constant latency**: one forward pass regardless of decision complexity
- **No explanation detours**: can't generate text, only returns an answer
- **Pipeline-friendly**: returns structured scores, no text parsing needed

This matches the TypeSafe AI Jev `/v1/systemone` interface philosophy, but d1 bakes it into the model architecture rather than achieving it through inference tricks.

---

### Performance Numbers

**d1-3B Decision Index v0.2.1: 48.57**

| Model | Parameters | DI v0.2.1 |
|-------|-----------|-----------|
| d1-3B | 3B | **48.57** |
| Decider 35B-A3B | 35B | 47.11 |
| (Other 4B/9B models) | — | < 47 |

3B outperforms 35B-A3B, ranking #1 under 10B. Decision Index is LiquidAI's own benchmark (dataset: LiquidAI/d1-decision-index) — no third-party independent verification yet.

**d1-3B text benchmarks (7 public datasets, mean 82.9)**

| Benchmark | Score |
|-----------|-------|
| SQuAD 2.0 | 85.3 |
| XNLI | 85.0 |
| DecisionBench | 71.8 |

**d1-3B vision benchmarks**: mean 74.1 across 11 public datasets.

---

### Latency (d1-3B)

| Hardware | Text decision | Image decision |
|----------|--------------|----------------|
| RTX 4090 | **8ms** | 17ms |
| Jetson AGX Thor | ~16ms | — |
| Apple M5 Pro | 30ms | 62ms |
| Jetson Orin Nano | 50ms | 202ms |

Edge inference fits within 50ms for text decisions. Jetson Orin Nano's 202ms image latency is slow for real-time use but acceptable for batch processing.

---

### Hardware & Deployment

- NVIDIA: DGX, RTX series, full Jetson lineup
- Apple: M5 Pro (via llama.cpp)
- AMD: MI325X
- **Day-one llama.cpp support** (official GGUF provided)

No proprietary inference framework required.

---

### d1-omni-600M: Multimodal Combinations

d1-omni-600M is the first 600M-class decision model supporting both image and audio inputs. Labeled "experimental," target scenarios:

- **Voice command routing**: audio → route directly to tools without ASR transcription first
- **On-device content moderation**: combined text+image judgement at 600M, mobile-deployable
- **Intent classification**: multimodal input → class label, no generation overhead

⚠️ d1-omni-600M is experimental — not recommended for production yet.

---

### License

Both models use **lfm1.0** (LiquidAI Foundation Model License 1.0), not Apache-2.0 or MIT. lfm1.0 permits research and non-commercial use; commercial deployment above a certain scale requires separate authorization. Read the license terms before integrating into products.

---

> lfm1.0 license. Released by LiquidAI on 2026-10-07, available on HuggingFace. For technical reference only.
