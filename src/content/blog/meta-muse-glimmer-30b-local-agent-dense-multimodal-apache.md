---
title: "Meta Muse Glimmer 30B：专为本地 Agent 设计的 30B 小钢炮"
titleEn: "meta-muse-glimmer-30b-local-agent-dense-multimodal-apache"
description: "Meta 开源 Muse Glimmer 30B，29.6B 参数 Dense 架构，图像+文本输入，131K 上下文，由 Muse Spark 蒸馏，重点训练 Agent、多步推理、Tool Use、Coding 和失败恢复。4bit 量化不到 20GB，24GB 显存可跑，RTX 5090 配合 DFlash 推测解码达 233 tok/s，M4 Max 约 37.8 tok/s，M5 Max 约 50.2 tok/s。SWE-Bench Verified 76.0，MCP Atlas 75.5。Apache 2.0，权重直接开放。扎克伯格同步确认 Muse Spark 1.2 权重即将开放。"
descriptionEn: "Meta open-sources Muse Glimmer 30B: 29.6B parameters, Dense architecture, image+text input, 131K context, distilled from Muse Spark with focused training on Agent tasks, multi-step reasoning, Tool Use, Coding, and failure recovery. Under 20GB at 4-bit quantization, runs on 24GB VRAM. RTX 5090 + DFlash speculative decoding: 233 tok/s; M4 Max: ~37.8 tok/s; M5 Max: ~50.2 tok/s. SWE-Bench Verified 76.0, MCP Atlas 75.5. Apache 2.0, weights fully open. Zuckerberg confirms Muse Spark 1.2 weights coming soon."
pubDate: "2026-08-11"
updatedDate: "2026-08-11"
category: "Tech-News"
tags: ["Meta", "开源模型", "AI Agent", "本地部署", "多模态", "LLM", "30B", "Mycelium"]
heroImage: "../../assets/images/meta-muse-glimmer-30b-local-agent-dense-multimodal-apache-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

扎克伯格今天在 X 上宣布：

> "Today we're also opening the weights for Muse Glimmer, a great 30B parameter dense model that can run locally. Soon we'll also release the weights for Muse Spark 1.2, our latest foundation model."

Muse Glimmer 30B 不是 Meta 的旗舰模型——Muse Spark 才是。但 Glimmer 做的事情，是把 Agent 能力塞进一个 24GB 显存就能跑的本地模型里，同时把权重完全开放。

HuggingFace: meta-llama/Muse-Glimmer-30B | Apache 2.0

---

## 基本参数

| 项目 | 参数 |
|------|------|
| 参数量 | ~29.6B（Dense） |
| 输入模态 | 图像 + 文本 |
| 上下文长度 | 131K tokens |
| 蒸馏来源 | Muse Spark |
| 训练重点 | Agent、多步推理、Tool Use、Coding、失败恢复 |
| 协议 | Apache 2.0 |

Dense 架构而非 MoE——这对本地推理来说是更好的选择：没有专家路由的额外开销，延迟更稳定，显存占用更可预测。

---

## 本地推理速度

| 硬件 | 量化 | 速度 |
|------|------|------|
| RTX 5090 + DFlash 推测解码 | 4-bit | **233 tok/s** |
| M5 Max | 4-bit | ~50.2 tok/s |
| M4 Max | 4-bit | ~37.8 tok/s |

4-bit 量化后不到 20GB，24GB 显存的消费级 GPU 就能跑完整模型。RTX 5090 配合 Meta 的 DFlash 推测解码达到 233 tok/s，这个速度对 Agent 任务来说已经足够实用——一个需要多步工具调用的 coding task，这个速度基本不会成为瓶颈。

苹果芯片方面，M4 Max 和 M5 Max 都能流畅运行，M5 Max 的 50 tok/s 对于本地 Agent 循环是个舒适的数字。

---

## Benchmark

| 评测 | 分数 |
|------|------|
| SWE-Bench Pro | 51.2 |
| SWE-Bench Verified | 76.0 |
| TerminalBench 2.1 | 51.7 |
| MCP Atlas | 75.5 |
| DeepSearch QA | 74.6 |

SWE-Bench Verified 76.0 是这里最显眼的数字——这个任务要求模型真正修复 GitHub issue，不是问答，不是生成代码片段，是端到端的工程任务。对于一个可以跑在消费级设备上的 30B 模型，这个分数说明训练方向是对的。

MCP Atlas 75.5 直接测 MCP 工具调用能力，这是 Agent 工作流的核心。

---

## 为什么专门强调「本地 Agent」

Glimmer 的训练重点不是通用问答，而是**失败恢复（Failure Recovery）**——Agent 在工具调用失败、环境返回异常、中间步骤出错时，能不能继续推进而不是卡死。这是本地 Agent 和 chatbot 最本质的区别之一。

同步宣布的 Muse Code（8月5日）是一个由 Muse Spark 1.2 驱动的终端 coding agent，能处理大型代码库的完整任务规划、代码编写和结果验证。Glimmer 的定位是把类似的 Agent 能力带到完全本地运行的场景——不依赖云端 API，不需要大型 GPU 集群。

---

## Muse Spark 1.2 即将开放

扎克伯格在同一条推文里确认：Muse Spark 1.2 的权重很快也会开放。

Muse Spark 是 Meta 的旗舰基础模型，Muse Glimmer 就是从它蒸馏出来的。如果 Spark 1.2 的权重也开放，这意味着开源社区将同时拥有：

- 本地可跑的 Agent 专用模型（Glimmer 30B）
- 背后的完整旗舰模型权重（Spark 1.2）

这是一个完整的开放组合，而不只是一个精简的发布版本。

---

## 与当前 30B 级别开源模型的位置

现有 30B 级别的开源模型（Qwen、Mistral、DeepSeek 等）大多是通用模型，Agent 能力通过 prompt 和 fine-tune 叠加。Glimmer 从训练目标上就是面向 Agent——131K 上下文、多模态输入、失败恢复训练、MCP 工具调用——这是一个不同的出发点。

对于想在本地跑完整 Agent 工作流的开发者，Glimmer 目前是参数量这个级别里最明确的选择。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Meta Muse Glimmer 30B: A 30B Dense Agent Model Built for Local Deployment

*by Mycelium Protocol*

---

Zuckerberg announced on X today:

> "Today we're also opening the weights for Muse Glimmer, a great 30B parameter dense model that can run locally. Soon we'll also release the weights for Muse Spark 1.2, our latest foundation model."

Muse Glimmer 30B isn't Meta's flagship — Muse Spark is. What Glimmer does is pack Agent capabilities into a model that fits in 24GB of VRAM, with fully open weights.

HuggingFace: meta-llama/Muse-Glimmer-30B | Apache 2.0

---

### Specs

| | |
|---|---|
| Parameters | ~29.6B (Dense) |
| Input | Image + text |
| Context | 131K tokens |
| Distilled from | Muse Spark |
| Training focus | Agent tasks, multi-step reasoning, Tool Use, Coding, failure recovery |
| License | Apache 2.0 |

Dense architecture, not MoE — better for local inference: no expert-routing overhead, more predictable latency and memory.

---

### Local Inference Speed

| Hardware | Quantization | Speed |
|----------|-------------|-------|
| RTX 5090 + DFlash speculative decoding | 4-bit | **233 tok/s** |
| M5 Max | 4-bit | ~50.2 tok/s |
| M4 Max | 4-bit | ~37.8 tok/s |

Under 20GB at 4-bit — a 24GB consumer GPU runs the full model. The RTX 5090 number (233 tok/s with Meta's DFlash speculative decoding) is fast enough that generation speed stops being the bottleneck for multi-step agent loops. M5 Max at 50 tok/s is comfortable for local agent work.

---

### Benchmarks

| Benchmark | Score |
|-----------|-------|
| SWE-Bench Pro | 51.2 |
| SWE-Bench Verified | 76.0 |
| TerminalBench 2.1 | 51.7 |
| MCP Atlas | 75.5 |
| DeepSearch QA | 74.6 |

SWE-Bench Verified at 76.0 is the headline number: this task requires the model to actually fix GitHub issues end-to-end — not Q&A, not generating a snippet, but a complete engineering loop. For a model that runs on consumer hardware, that score indicates the training direction worked.

MCP Atlas at 75.5 directly tests MCP tool-call capability — the core of agentic workflows.

---

### Why "Local Agent" Specifically

Glimmer's training focus includes **failure recovery** — the ability to keep pushing forward when a tool call fails, an environment returns an unexpected value, or an intermediate step goes wrong. This is one of the sharpest differences between a real agent and a chatbot, and it's relatively rare to see it as an explicit training objective at this scale.

Also announced: Muse Code (released in beta Aug 5), a terminal coding agent powered by Muse Spark 1.2 for full engineering tasks across large repos — plan, write, validate. Glimmer is the local, open-weight version of that capability direction.

---

### Muse Spark 1.2 Weights Also Coming

Zuckerberg confirmed in the same post: Muse Spark 1.2 weights will be released soon.

Muse Spark is Meta's flagship foundation model — Glimmer is distilled from it. If Spark 1.2 ships open, the open-source community will have both pieces:

- A local-capable agent-specialized model (Glimmer 30B)
- The full flagship model weights it was distilled from (Spark 1.2)

That's a complete open stack, not just a compressed derivative.

---

### Where Glimmer Sits Among 30B Open Models

Most existing 30B-class open models (Qwen, Mistral, DeepSeek family) are general-purpose, with Agent capabilities added via prompting and fine-tuning. Glimmer's training target is Agent from the start: 131K context, multimodal input, failure recovery training, MCP tool-call focus. That's a different starting point.

For developers who want to run a full agent workflow locally, Glimmer is currently the clearest option at this parameter count.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
