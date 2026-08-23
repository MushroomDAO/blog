---
title: "FreeToken：游戏 PC 本地跑 290B+ MoE 大模型，q* 自适应执行引擎，开源 Apache 2.0"
titleEn: "freetoken-flashml-edge-moe-290b-gaming-pc-deepseek-local-inference"
description: "FlashML-org/FreeToken 是一个边缘原生 MoE 推理引擎，Apache 2.0，Python，2105 stars。核心：在消费级 GPU（RTX 30/40/50）上本地运行 290B+ MoE 模型（DeepSeek-V4-Flash、Qwen3.6-35B、GLM-5.2），通过 q* 带宽自适应 CPU-GPU 协同执行、双缓冲预填充流、全局 LRU Expert 缓存、语义感知 KV 缓存实现交互级速度。兼容 Anthropic/OpenAI API，可直接接入 Claude Code、Codex、OpenCode。来自 Berkeley/MIT 研究团队（Matei Zaharia、Song Han、Kurt Keutzer、Ion Stoica），有 arXiv 论文。"
descriptionEn: "FlashML-org/FreeToken is an edge-native MoE inference engine — Apache 2.0, Python, 2,105 stars. Core: run 290B+ MoE models (DeepSeek-V4-Flash, Qwen3.6-35B, GLM-5.2) locally on consumer GPUs (RTX 30/40/50) at interactive speeds, via q*-policy bandwidth-adaptive CPU-GPU co-execution, double-buffered prefill streaming, global LRU expert caching, and semantic-aware KV caching. Compatible with Anthropic/OpenAI APIs — plugs directly into Claude Code, Codex, and OpenCode. From Berkeley/MIT researchers (Matei Zaharia, Song Han, Kurt Keutzer, Ion Stoica), with an arXiv paper."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["本地推理", "MoE", "DeepSeek", "消费级GPU", "边缘AI", "开源", "大模型"]
heroImage: "../../assets/images/freetoken-flashml-edge-moe-290b-gaming-pc-deepseek-local-inference-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：FlashML-org/FreeToken
论文：arXiv:2608.16157
许可证：Apache 2.0
语言：Python
Stars：2,105 · Forks：185
创建：2026-07-20 | 最近更新：2026-08-23
团队：Berkeley / MIT（Matei Zaharia、Song Han、Kurt Keutzer、Ion Stoica 等）

---

## 一、它做了什么

一句话：**在你手里的游戏 PC 上跑 290B+ 参数的 MoE 大模型，速度达到可交互水平**。

这个数字要有概念。290B 参数是 DeepSeek-V4 量级的模型，正常需要 H100 集群来跑。FreeToken 的目标是让 RTX 4090 的玩家也能本地运行它——不是慢到不可用的那种「能跑」，是真的能当 AI 助手用的交互速度。

它的定位是**边缘原生 MoE 推理引擎**：不假设你有数据中心，把你手里的 GPU、CPU、内存、互联当成一个统一的异构计算平台，弹性调度。

---

## 二、核心技术

### q* 带宽自适应 CPU-GPU 协同执行

MoE 模型的推理瓶颈是 Expert 权重的带宽——模型太大，VRAM 装不下，要频繁在 CPU 内存和 GPU 之间搬运 Expert 参数。

FreeToken 的 **q* 策略**在运行时动态判断：当前的 PCIe 带宽允许从 CPU 内存取这个 Expert 吗？还是让 CPU 直接计算更快？根据实时带宽情况自动切换执行路径。这个动态决策是 FreeToken 能在消费级硬件上跑出高速度的核心原因。

### 双缓冲预填充流

预填充（处理输入 prompt）和 Expert 权重加载并行进行，像流水线一样双缓冲，不让 GPU 干等数据搬运。

### 全局 LRU Expert 缓存

把最近用过的 Expert 权重留在 VRAM 里，下次用到直接命中，不需要从 CPU 内存重新传输。LRU 替换策略在有限 VRAM 下最大化 Expert 复用率。

### 语义感知 KV 缓存

这个功能专门为 Agent 工作流设计。问题背景：Agent 调用工具后会修改上下文（tool call 结果、thinking block），按传统方式每次修改都要重新计算整段 KV 缓存，成本很高。

FreeToken 用**语义锚点检查点**来解决：把上下文里的「稳定部分」（不会被 Agent 修改的 system prompt、历史对话）和「变化部分」（tool 结果）分开管理，只对变化部分重算，稳定部分的 KV 缓存复用。对长上下文 Agent 任务，这能省掉大量重复计算。

### 弹性 VRAM 管理

Expert 缓存和 KV 内存动态共享 VRAM，**不需要重启引擎或重载权重**就能在运行时重新分配。对于 VRAM 有限的消费级 GPU，这个灵活性至关重要。

---

## 三、支持的模型和硬件

**模型**（当前支持的前沿 MoE）：
- DeepSeek-V4-Flash
- Qwen3.6-35B-A3B
- GLM-5.2
- 支持量化格式：MXFP4、NVFP4、FP8、BF16

**硬件**：NVIDIA RTX 30 / 40 / 50 系列，从消费级笔记本到工作站 GPU 都覆盖。

**API 兼容**：Anthropic 和 OpenAI 格式，意味着可以直接接入 **Claude Code、Codex、OpenCode、OpenClaw、DeepSeek Harness** 这些工具，不需要改客户端配置。

---

## 四、快速上手

**桌面 App**（推荐入门）：在 [flashml.ai](https://www.flashml.ai) 下载 Windows 或 Linux 版本，GUI 管理模型、对话、引擎参数调整。

**CLI**：

```bash
uv pip install "freetoken[accel]"
```

装好之后配 API 端点，把 Claude Code 或 Codex 指向本地跑的 FreeToken，就变成了一个零成本的本地 Agent 后端。

---

## 五、团队背景

来自 Berkeley 和 MIT 的研究团队，作者名单里有几个 ML 系统领域的重量级名字：

- **Matei Zaharia**：Apache Spark 联合创始人，LangChain 早期参与者
- **Ion Stoica**：Berkeley RISELab 主任，Ray 项目发起人
- **Song Han**（韩松）：MIT，量化/剪枝/高效推理领域代表人物，TinyML 方向核心研究者
- **Kurt Keutzer**：Berkeley，深度学习编译和加速领域老兵

这不是普通的开源项目，是有顶级研究支撑的技术。arXiv 论文 2608.16157 是技术细节的权威来源。

---

## 六、为什么值得关注

本地大模型推理一直有一道墙：MoE 架构的前沿模型（DeepSeek-V4 量级）太大，消费级硬件装不下，只能用蒸馏或量化后的小版本。FreeToken 的路线不是把模型缩小，而是**把消费级硬件的资源用得更聪明**——CPU 和 GPU 协同，动态决策，缓存复用。

如果它的实测速度兑现论文里的数字，意味着一台配了 RTX 4090 的普通工作站，可以本地运行和数据中心同等质量的 MoE 模型。这对本地 AI 隐私、成本和离线场景的含义不言而喻。

2,105 stars，7 月 20 日发布，一个月出头，增速在本地推理项目里属于快的。Apache 2.0 开源，可商用。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## FreeToken: Run 290B+ MoE Models on a Gaming PC Locally — q*-Adaptive Execution Engine, Apache 2.0

*by Mycelium Protocol*

---

GitHub: FlashML-org/FreeToken
Paper: arXiv:2608.16157
License: Apache 2.0
Language: Python
Stars: 2,105 · Forks: 185
Created: 2026-07-20 | Updated: 2026-08-23
Team: Berkeley / MIT (Matei Zaharia, Song Han, Kurt Keutzer, Ion Stoica, et al.)

---

### What It Does

One sentence: **run 290B+ parameter MoE models locally on a gaming PC at interactive speeds**.

That number needs context. 290B parameters is the scale of DeepSeek-V4 — normally requiring an H100 cluster. FreeToken's goal is to let an RTX 4090 owner run it locally — not the "technically runs but unusably slow" kind, but actual interactive speed suitable as an AI assistant.

Its positioning: **edge-native MoE inference engine** — no datacenter assumed, treating your GPU, CPU, host memory, and interconnects as a unified, heterogeneous elastic compute platform.

---

### Core Technology

#### q* Bandwidth-Adaptive CPU-GPU Co-Execution

MoE inference bottleneck is expert weight bandwidth — the model is too large to fit in VRAM, requiring constant movement of expert parameters between CPU memory and GPU.

The **q* policy** makes real-time decisions: given current PCIe bandwidth, is it faster to fetch this expert from CPU memory, or have the CPU compute it directly? The execution path switches dynamically based on live bandwidth conditions. This runtime decision logic is the core reason FreeToken achieves high speeds on consumer hardware.

#### Double-Buffered Prefill Streaming

Prefilling (processing the input prompt) and expert weight loading run in parallel via double-buffering — keeping the GPU from stalling while data transfers happen.

#### Global LRU Expert Cache

Recently used expert weights stay in VRAM; the next hit returns immediately without re-transfer from CPU memory. LRU replacement maximizes expert reuse under constrained VRAM.

#### Semantic-Aware KV Cache

Designed specifically for agent workflows. The problem: when an agent modifies context (tool call results, thinking blocks), traditional approaches recompute the entire KV cache for every edit — expensive for long contexts.

FreeToken uses **semantic anchor checkpoints**: stable context segments (system prompt, fixed history — the parts agents don't modify) and volatile segments (tool results) are managed separately. Only the volatile part gets recomputed; the stable KV cache is reused. For long-context agent tasks, this eliminates substantial redundant computation.

#### Elastic VRAM Management

Expert cache and KV memory share VRAM dynamically, **without engine restarts or weight reloading**. For VRAM-constrained consumer GPUs, this runtime flexibility is critical.

---

### Supported Models and Hardware

**Models** (current frontier MoE support):
- DeepSeek-V4-Flash
- Qwen3.6-35B-A3B
- GLM-5.2
- Quantization formats: MXFP4, NVFP4, FP8, BF16

**Hardware**: NVIDIA RTX 30 / 40 / 50 series — consumer laptops through workstation GPUs.

**API compatibility**: Anthropic and OpenAI formats — plugs directly into **Claude Code, Codex, OpenCode, OpenClaw, and DeepSeek Harness** without any client configuration changes.

---

### Getting Started

**Desktop app** (recommended for beginners): download Windows or Linux at [flashml.ai](https://www.flashml.ai). GUI for model management, chat, and engine tuning.

**CLI**:

```bash
uv pip install "freetoken[accel]"
```

After installation, point Claude Code or Codex at the local FreeToken endpoint and you have a zero-cost local agent backend.

---

### Team Background

From Berkeley and MIT — the author list includes heavy names in ML systems:

- **Matei Zaharia**: co-founder of Apache Spark, early LangChain contributor
- **Ion Stoica**: director of Berkeley RISELab, creator of Ray
- **Song Han**: MIT, central figure in quantization/pruning/efficient inference, core TinyML researcher
- **Kurt Keutzer**: Berkeley, veteran in deep learning compilation and acceleration

This isn't a typical open-source project — it has top-tier research backing. arXiv paper 2608.16157 is the authoritative technical reference.

---

### Why It Matters

Local large-model inference has always had a hard wall: frontier MoE models (DeepSeek-V4 scale) are too large for consumer hardware, so users fall back to distilled or heavily quantized smaller versions. FreeToken's approach isn't to shrink the model — it's to **use consumer hardware resources more intelligently**: CPU-GPU co-execution, dynamic bandwidth-aware routing, cache reuse.

If the real-world speeds match the paper's numbers, it means a standard workstation with an RTX 4090 can run datacenter-quality MoE models locally. The implications for local AI privacy, cost, and offline scenarios are obvious.

2,105 stars, launched July 20th, just over a month old — fast growth for a local inference project. Apache 2.0, commercially usable.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
