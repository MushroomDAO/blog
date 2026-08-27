---
title: "GLM-5.3-Flash（Ox Alpha）开源：321B MoE 原生多模态，30T token 预训练，稀疏+线性注意力混合架构，MIT"
titleEn: "glm-5-3-flash-ox-alpha-320b-native-multimodal-open-source"
description: "2026-08-26 晚，智谱 z.ai 开源 GLM-5.3-Flash（代号 Ox Alpha）。约 321B 参数、激活 18B 的 MoE 模型，GLM-5 系列首个原生多模态版本，原生支持文字、图片、视频处理，使用 30T 多模态 token 预训练。架构上首次引入稀疏注意力与线性注意力混合（DSA），并配套异步强化学习训练基础设施。权重已上传 HuggingFace（zai-org/GLM-5.3-Flash），MIT 开源，FP8 原生支持。unsloth GGUF 量化版已有 172 likes，社区已在 DGX Spark、Mac Studio M3 Ultra、RTX PRO 6000 Blackwell 等平台完成部署。"
descriptionEn: "On 2026-08-26 evening, Zhipu AI (z.ai) open-sourced GLM-5.3-Flash (codename Ox Alpha). A ~321B-parameter, 18B-activated MoE model, the first native multimodal model in the GLM-5 series — text, image, and video natively. Pretrained on 30T multimodal tokens. Architecture: sparse + linear attention hybrid (DSA) introduced in the main series for the first time, with asynchronous RL post-training. Weights on HuggingFace (zai-org/GLM-5.3-Flash), MIT license, FP8 native. Community already deployed on DGX Spark (GB10), Mac Studio M3 Ultra, and RTX PRO 6000 Blackwell."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Tech-News"
tags: ["开源", "LLM", "智谱", "GLM-5", "多模态", "MoE", "强化学习", "中国AI"]
heroImage: "../../assets/images/glm-5-3-flash-ox-alpha-320b-native-multimodal-open-source-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

模型：zai-org/GLM-5.3-Flash（代号 Ox Alpha）  
发布：2026-08-26 | HuggingFace ⭐ 1,233 likes | MIT | FP8 原生  
参数：321B 总量 / 18B 激活（MoE）| 预训练数据：30T 多模态 token

---

## 背景：从「氛围编码」到「Agent 工程」

GLM-5 的定位在论文标题里说得很清楚：**从 Vibe Coding 到 Agentic Engineering**（arXiv: 2602.15763）。智谱认为 AI 编码的下一阶段不是用模型辅助写代码，而是让模型作为 Agent 独立完成端到端的软件工程任务。

GLM-5.3-Flash 是 GLM-5 系列的 **「Flash」** 版本，也是该系列第一个原生多模态模型。在此之前，GLM-5 系列的多模态能力由单独的 GLM-5V 系列承担；5.3-Flash 把文字、图片、视频处理整合进同一个模型。

---

## 核心参数

| 项目 | 数值 |
|------|------|
| 总参数量 | ~321B（HF safetensors: 321,323,031,390） |
| 激活参数 | ~18B |
| 架构 | MoE（稀疏+线性注意力混合） |
| 预训练数据 | 30T 多模态 token |
| 模态 | 文本、图片、视频（原生处理） |
| 上下文 | 262K（社区实测 FP8 KV 池可扩至 1.26M） |
| 原生量化 | FP8（E4M3） |
| 许可证 | MIT |

---

## 架构亮点：主系列首次引入稀疏+线性注意力混合（DSA）

GLM-5 系列这次在主干模型中引入了**稀疏注意力与线性注意力的混合架构**（论文称 DSA）。这是一个工程权衡：

- **标准注意力**：精确，但计算复杂度 O(n²)，长序列昂贵
- **稀疏注意力**：只关注部分关键 token，降低计算量
- **线性注意力**：把注意力机制近似为线性操作，复杂度降到 O(n)，但精度有损

三者混合的目标是：**在保住长文本精度的前提下，大幅降低训练和推理成本**。论文里把这个能力概括为"维持长上下文保真度的同时显著降低成本"。

结合 MoE（混合专家）架构，每次推理只激活 18B 参数，整体效率远高于同参数规模的密集模型。

---

## 异步强化学习后训练

GLM-5 论文的另一个核心贡献是**异步 RL 训练基础设施**：把生成（rollout）和训练（update）解耦，分别跑在不同进程/节点上，不再相互等待。

这个设计解决了标准 RLHF 流程的一个瓶颈：生成步骤通常比训练步骤慢很多，导致 GPU 大量空闲。异步化后，后训练效率大幅提升。

同时提出了**异步 Agent RL 算法**，专门针对复杂长链条的 Agent 交互任务——这类任务一次轨迹可能包含几十步工具调用，标准 RL 很难高效处理。

---

## 社区部署情况（发布当天）

权重发布不到24小时，社区已在多种硬件上跑通：

| 硬件 | 框架 | 量化 | 速度 | 上下文 |
|------|------|------|------|--------|
| 2× DGX Spark GB10（TP2） | vLLM | NVFP4 | — | 262K + MTP |
| 4× DGX Spark GB10（TP4） | vLLM | NVFP4 + FP8 KV | 36 tok/s | 1.26M |
| Mac Studio M3 Ultra | oMLX（双 ANE） | oQ4（abliterated） | ~24 tok/s | — |
| 2× RTX PRO 6000 Blackwell（SM120） | SGLang | MXFP4A16 | — | — |

可用的量化版本：
- **NVFP4**：LibertAI/GLM-5.3-Flash-NVFP4（DGX Spark 优化）
- **GGUF**：unsloth/GLM-5.3-Flash-GGUF（172 likes，最广泛）
- **MLX**：orcarouter/GLM-5.3-Flash-MLX（Mac 原生）
- **EXL3**：brandonmusic/GLM-5.3-Flash-EXL3-4bpw

---

## 为什么值得关注

**1. 原生多模态 + MoE 的组合**

把文图视频整合进一个 MoE 模型不是新思路，但真正做出来、公开权重的不多。GLM-5.3-Flash 是目前规模最大的开源原生多模态 MoE 模型之一。

**2. 架构创新上架到了主系列**

稀疏+线性注意力混合之前在一些研究模型里出现过，但被引入一个量产主线模型并开源，会给下游研究和工程实践提供实际可用的参考点。

**3. MIT 开源**

MIT 是目前最宽松的开源许可证之一。商业可用、可修改、可再分发。这对需要私有部署或二次开发的企业来说意义很大。

**4. 社区反应速度**

发布当天，unsloth GGUF 就有 172 likes，多个 DGX Spark 部署 recipe 已经上传 GitHub。跑分讨论早在开源前就已经在社区里传开了（这也是"Ox Alpha"这个代号在圈子里被反复提到的原因）。

---

## 获取

```bash
# 原始 FP8 权重（HuggingFace）
huggingface-cli download zai-org/GLM-5.3-Flash

# GGUF（Mac / CPU 友好）
huggingface-cli download unsloth/GLM-5.3-Flash-GGUF

# MLX（Apple Silicon）
huggingface-cli download orcarouter/GLM-5.3-Flash-MLX
```

---

**相关链接**

- HuggingFace：https://huggingface.co/zai-org/GLM-5.3-Flash
- 论文：https://arxiv.org/abs/2602.15763（GLM-5: from Vibe Coding to Agentic Engineering）
- GitHub：https://github.com/zai-org/GLM-5

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## GLM-5.3-Flash (Ox Alpha) Open-Sourced: 321B MoE, Native Multimodal, 30T Tokens, Sparse+Linear Attention, MIT

*by Mycelium Protocol*

---

Model: zai-org/GLM-5.3-Flash (codename: Ox Alpha)  
Released: 2026-08-26 | HuggingFace ⭐ 1,233 likes | MIT | FP8 native  
Parameters: 321B total / 18B activated (MoE) | Pretrain data: 30T multimodal tokens

---

### Background: From Vibe Coding to Agentic Engineering

The GLM-5 paper's title makes its positioning clear: **GLM-5: from Vibe Coding to Agentic Engineering** (arXiv: 2602.15763). Zhipu's thesis is that the next stage of AI-assisted coding isn't about helping humans write code — it's about models acting as agents that independently complete end-to-end software engineering tasks.

GLM-5.3-Flash is the **Flash** variant of the GLM-5 series, and the first natively multimodal model in the family. Previously, multimodal capability lived in a separate GLM-5V line. 5.3-Flash collapses text, image, and video into a single model.

---

### Core Specs

| Spec | Value |
|------|-------|
| Total parameters | ~321B (HF safetensors: 321,323,031,390) |
| Active parameters | ~18B |
| Architecture | MoE, sparse + linear attention hybrid |
| Pretraining data | 30T multimodal tokens |
| Modalities | Text, image, video (natively) |
| Context | 262K (community FP8 KV pool: up to 1.26M) |
| Native quantization | FP8 (E4M3) |
| License | MIT |

---

### Architecture: Sparse + Linear Attention Hybrid (DSA) Enters the Main Series

GLM-5.3-Flash introduces a **sparse + linear attention hybrid** architecture (called DSA in the paper) into the main model line for the first time:

- **Standard attention**: accurate, but O(n²) — expensive at long context
- **Sparse attention**: attends only to key tokens, lower compute cost
- **Linear attention**: approximates attention as linear operations, O(n) complexity, some precision loss

Mixing all three targets: **maintaining long-context fidelity while significantly reducing training and inference cost**. Combined with MoE (only 18B parameters activated per forward pass), the model's effective efficiency far exceeds a dense model at the same scale.

---

### Asynchronous RL Post-Training

The GLM-5 paper's other core contribution is an **async RL training infrastructure** that decouples generation (rollout) from training (update) — they run concurrently on separate processes/nodes, no longer waiting on each other.

This solves a persistent bottleneck in standard RLHF: generation is much slower than the training update, leaving GPUs idle during rollout. Async decoupling significantly improves post-training throughput.

They also introduce **async agent RL algorithms** specifically for complex long-horizon agent interactions — tasks where one trajectory may involve dozens of tool calls that standard RL struggles to handle efficiently.

---

### Community Deployments (Day Zero)

Within 24 hours of release, the community had the model running on multiple hardware configurations:

| Hardware | Framework | Quantization | Speed | Context |
|----------|-----------|-------------|-------|---------|
| 2× DGX Spark GB10 (TP2) | vLLM | NVFP4 | — | 262K + MTP |
| 4× DGX Spark GB10 (TP4) | vLLM | NVFP4 + FP8 KV | 36 tok/s | 1.26M |
| Mac Studio M3 Ultra | oMLX (dual ANE) | oQ4 (abliterated) | ~24 tok/s | — |
| 2× RTX PRO 6000 Blackwell (SM120) | SGLang | MXFP4A16 | — | — |

Available quantized builds:
- **NVFP4**: LibertAI/GLM-5.3-Flash-NVFP4 (DGX Spark optimized)
- **GGUF**: unsloth/GLM-5.3-Flash-GGUF (172 likes, widest coverage)
- **MLX**: orcarouter/GLM-5.3-Flash-MLX (Apple Silicon)
- **EXL3**: brandonmusic/GLM-5.3-Flash-EXL3-4bpw

---

### Why It Matters

**1. Native multimodal + MoE together**

Combining text/image/video into a single MoE model is not a new idea, but actually shipping it with open weights is rare. GLM-5.3-Flash is one of the largest open-source native multimodal MoE models available.

**2. Architectural innovation lands in the main series**

Sparse + linear attention hybrids have appeared in research models before, but being deployed in a production mainline model and open-sourced gives downstream research and engineering a concrete, usable reference.

**3. MIT license**

MIT is among the most permissive open-source licenses. Commercial use, modification, and redistribution are all permitted — significant for enterprises that need private deployment or derivative builds.

**4. Community velocity**

The unsloth GGUF hit 172 likes on day one. Multiple DGX Spark deployment recipes were on GitHub before the first full day was over. Benchmark results were circulating in the community under the "Ox Alpha" codename before the official open-source announcement — which explains the attention on launch day.

---

### How to Get It

```bash
# Original FP8 weights (HuggingFace)
huggingface-cli download zai-org/GLM-5.3-Flash

# GGUF (Mac / CPU-friendly)
huggingface-cli download unsloth/GLM-5.3-Flash-GGUF

# MLX (Apple Silicon)
huggingface-cli download orcarouter/GLM-5.3-Flash-MLX
```

---

**Links**

- HuggingFace: https://huggingface.co/zai-org/GLM-5.3-Flash
- Paper: https://arxiv.org/abs/2602.15763 (GLM-5: from Vibe Coding to Agentic Engineering)
- GitHub: https://github.com/zai-org/GLM-5

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
