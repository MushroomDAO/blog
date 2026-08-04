---
title: "Frontis-MA1：清华 + Horizon Research 开源 AI 改进 AI 的全套配方，35B 单卡超 GPT-5.5"
titleEn: "frontis-ma1-openrsi-ai4ai-recursive-self-improvement-mle"
description: "FrontisAI/OpenRSI 是 Frontis.AI + 清华大学的 AI4AI 开源框架。核心是 Frontis-MA1（35B/30B），通过四个可训练原子算子（Draft/Improve/Debug/Crossover）+ OpenMLE 全栈，在 MLE-Bench Lite 单卡 12h 达到 71.21% Medal Average，超越 GPT-5.5 + Codex。CC BY-NC 4.0，模型+数据+代码全开源。"
descriptionEn: "FrontisAI/OpenRSI is an open AI4AI framework from Frontis.AI and Tsinghua University. Core: Frontis-MA1 (35B/30B) with four trainable atomic operators (Draft/Improve/Debug/Crossover) + the OpenMLE full stack. Achieves 71.21% Medal Average on MLE-Bench Lite with a single RTX 4090 in 12h, surpassing GPT-5.5 + Codex. CC BY-NC 4.0, models + datasets + code all open."
pubDate: "2026-08-04"
updatedDate: "2026-08-04"
category: "Tech-News"
tags: ["AI4AI", "递归自改进", "MLE", "清华大学", "Horizon Research", "强化学习", "开源模型", "Mycelium"]
heroImage: "../../assets/images/frontis-ma1-openrsi-ai4ai-recursive-self-improvement-mle-banner.jpg"
---

*by Mycelium Protocol*

---

「AI 改进 AI」一直是 AI 研究里最诱人、也最模糊的方向——大量论文声称朝着这个目标努力，但很少有工作把它做成可执行、可测量、可复现的工程问题。

**[OpenRSI](https://github.com/FrontisAI/OpenRSI)**（Frontis.AI + 清华大学 + Horizon Research）是一个直接冲着这件事去的开源框架。首个发布是 **Frontis-MA1**：一个专门为机器学习工程（MLE）后训练的 AI4AI 模型（35B/30B），配套 OpenMLE 全栈，在单张 RTX 4090、12 小时预算内，把 MLE-Bench Lite Medal Average 从 39.39% 跑到了 **71.21%**——超越 GPT-5.5 + Codex，接近 GPT-5.6 Sol 和 2.8T 参数的 Kimi K3。

论文：[arXiv 2607.28568](https://arxiv.org/abs/2607.28568)

---

## 四个字概括：训练「改进者」

**递归自改进（RSI）**的核心不是让模型改进自身，而是让模型成为「能改进 AI 开发过程」的 Agent。Frontis 的路线是把这件事分层：

```
Evolution → Self-Evolution → Meta-Evolution（当前）→ RSI（目标）
```

当前 OpenRSI 做到的是 **Meta-Evolution**：在有界可执行域（MLE）里，训练能改进 AI 程序的 Agent，让每一代 AI R&D 更快、更高效、更可归因。

---

## 四个原子算子：Draft / Improve / Debug / Crossover

Frontis-MA1 的行动空间只有四个**可训练的原子算子**，同时用于训练和推理：

| 算子 | 功能 |
|------|------|
| **Draft** | 从零生成程序 |
| **Improve** | 利用执行反馈精化父程序 |
| **Debug** | 修复失败程序 |
| **Crossover** | 重组两个父程序 |

这四个算子贯穿整个系统——SFT 数据用它们标注，RL 训练用它们采样，长视野搜索（OpenMLE-Evo）用它们组合。同一套算子在训练和推理里语义一致，不存在"训练时学一套，推理时用另一套"的脱节。

---

## OpenMLE 全栈

OpenRSI 的基础设施由四个模块构成：

### OpenMLE-Gym：任务环境

构建、描述、执行和质量检查**可验证的 MLE 任务包**。每个任务有独立的执行环境和程序化验证器，执行反馈是训练信号的来源。

### OpenMLE-RL：算子学习

两阶段训练：

1. **执行反馈 SFT**：用 pass@k 成功的轨迹做监督冷启动
2. **在线 RL**：以执行结果为奖励信号，在线强化学习

开源数据集：
- **OpenMLE-SFT-Traces**：SFT 阶段的监督轨迹
- **OpenMLE-Tasks**：经过审计的可执行任务包

### Frontis-MA1：AI4AI 模型

在 OpenMLE 上后训练的元演化 Agent：
- **35B**（BF16 + GGUF）：旗舰模型
- **30B**（BF16 + GGUF）：备选尺寸

### OpenMLE-Evo：长视野搜索

把四个算子组合成迭代搜索：
- **标准 Evo**：单 GPU、顺序演化
- **Evo-Max**：多 GPU 异步搜索 + 独立于 benchmark 的经验先验

---

## 结果：严格控制对比

这个项目的结果报告方式值得专门说一下——他们明确区分了**模型收益**和**搜索系统收益**：

### MLE-Bench Lite（12h/任务，1x RTX 4090 12GB）

| 配置 | Medal Average |
|------|--------------|
| 基础模型（base） | 39.39% |
| + Frontis-MA1 后训练，Evo 固定 | **60.61%** |
| + OpenMLE-Evo-Max（模型+系统全开） | **71.21%** |

71.21% 的结果包含了搜索系统改进（异步多 GPU + 经验先验），**不是纯模型分数**，README 里明确标注了这一点——这是少见的诚实。

### NatureBench Lite（未见评测，迁移验证）

| 配置 | Match-SOTA |
|------|-----------|
| 基础模型 + 固定 adapter | 50% |
| **Frontis-MA1 + 固定 adapter**（模型改善，框架不变） | **70%** |
| 基础模型 + **OpenMLE-Evo**（框架改善，模型不变） | **50%** |
| 基础模型 + 固定 adapter（对照） | 20% |

模型贡献和框架贡献都在 held-out benchmark 上分别验证——这是做 RSI 研究必须要有的实验设计。

---

## 快速上手

```bash
git clone https://github.com/FrontisAI/OpenRSI.git
cd OpenRSI
```

按目标选入口：

| 目标 | 入口 |
|------|------|
| 构建或评测可执行任务包 | `OpenMLE-Gym/README.md` |
| 生成 SFT 数据并启动监督训练 | `OpenMLE-ERL/SFT/README.md` |
| 配置并启动执行反馈 RL | `OpenMLE-ERL/RL/README.md` |
| 运行 Evo 或 benchmark 适配器 | `OpenMLE-Evo/README.md` |

模型权重直接从 HuggingFace 拉：[FrontisAI/Frontis-MA1-35B](https://huggingface.co/FrontisAI/Frontis-MA1-35B)（BF16）或 [GGUF](https://huggingface.co/FrontisAI/Frontis-MA1-35B-GGUF)。

---

## 为什么值得关注

**可执行性**是 OpenRSI 的核心主张。AI4AI 领域不缺概念框架，缺的是能在真实机器上跑通、有程序化验证器、结果可复现的端到端系统。OpenRSI 把整条链——任务环境、训练数据生成、SFT、RL、长视野搜索——都开源出来，研究者可以在 OpenMLE 任务上复现，也可以贡献新任务、新算子、新搜索策略。

「改进者自身也是可训练的」这个定位和 TMax（AllenAI 终端 Agent）、EvoScientist 等方向形成互补：TMax 聚焦终端命令执行，OpenRSI 聚焦 ML 程序演化；前者 outcome-only RL，后者 SFT warm-start + 在线 RL + 演化搜索。

CC BY-NC 4.0，非商业可用。188 stars（2026-07-31 才发布），还在快速增长。

仓库：[github.com/FrontisAI/OpenRSI](https://github.com/FrontisAI/OpenRSI) · 论文：[arXiv 2607.28568](https://arxiv.org/abs/2607.28568) · 模型：[HuggingFace FrontisAI](https://huggingface.co/collections/FrontisAI/frontis-ma1)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Frontis-MA1: Tsinghua + Horizon Research Open-Source the Full Recipe for AI That Improves AI — 35B Beats GPT-5.5 on a Single GPU

*by Mycelium Protocol*

"AI improving AI" has always been one of the most tempting — and most vague — directions in AI research. Plenty of papers claim to work toward it, but few turn it into an executable, measurable, reproducible engineering problem.

**[OpenRSI](https://github.com/FrontisAI/OpenRSI)** (Frontis.AI + Tsinghua University + Horizon Research) is an open-source framework that tackles this directly. Its first release is **Frontis-MA1**: an AI4AI model (35B/30B) post-trained specifically for machine learning engineering (MLE), with the full OpenMLE stack. On a single RTX 4090 with a 12-hour budget, it pushes MLE-Bench Lite Medal Average from 39.39% to **71.21%** — surpassing GPT-5.5 + Codex and approaching GPT-5.6 Sol and 2.8T-parameter Kimi K3.

Paper: [arXiv 2607.28568](https://arxiv.org/abs/2607.28568)

### The Core Idea: Training the Improver

**Recursive self-improvement (RSI)** isn't about a model rewriting itself — it's about making a model that can improve the AI development process. Frontis's approach is layered:

```
Evolution → Self-Evolution → Meta-Evolution (current) → RSI (goal)
```

OpenRSI's current stage is **Meta-Evolution**: training an agent that can improve AI programs in a bounded, executable domain (MLE), making each generation of AI R&D faster, more efficient, and more attributable.

### Four Atomic Operators: Draft / Improve / Debug / Crossover

Frontis-MA1's action space consists of four **trainable atomic operators**, used consistently across both training and inference:

| Operator | Function |
|----------|----------|
| **Draft** | Generate a program from scratch |
| **Improve** | Refine a parent program using execution feedback |
| **Debug** | Repair a failing program |
| **Crossover** | Recombine two parent programs |

These four operators run through the entire system — SFT data is labeled with them, RL trains over them, long-horizon search (OpenMLE-Evo) composes them. The same operator semantics at training time and inference time, no representation gap.

### The OpenMLE Stack

**OpenMLE-Gym** builds, describes, executes, and quality-checks verifiable MLE task packages. Each task has its own isolated execution environment and a programmatic verifier — execution feedback is the training signal.

**OpenMLE-RL** trains operators in two stages:
1. **Execution-grounded SFT**: successful pass@k trajectories as supervised cold-start
2. **Online RL**: execution results as reward signal, online reinforcement learning

Open datasets: **OpenMLE-SFT-Traces** (supervised trajectories) and **OpenMLE-Tasks** (audited task artifacts).

**Frontis-MA1** is the post-trained meta-evolution agent — 35B and 30B in BF16 with GGUF derivatives.

**OpenMLE-Evo** composes the operators into iterative search:
- **Standard Evo**: single GPU, sequential evolution
- **Evo-Max**: multi-GPU async search + benchmark-independent experience priors

### Results: Controlled Comparisons

The results section is worth highlighting for its methodology — they explicitly separate **model gain** from **search-system gain**:

**MLE-Bench Lite (12h per task, 1× RTX 4090 12GB):**

| Configuration | Medal Average |
|---------------|---------------|
| Base model | 39.39% |
| Frontis-MA1 post-trained, Evo fixed | **60.61%** |
| OpenMLE-Evo-Max (model + system) | **71.21%** |

The 71.21% result includes search-system improvements (async multi-GPU + experience priors) and is clearly not presented as a pure model score — a level of honesty rarely seen.

**NatureBench Lite (held-out, transfer validation):**

| Configuration | Match-SOTA |
|---------------|------------|
| Base model + fixed adapter | 50% |
| Frontis-MA1 + fixed adapter (model improved, framework fixed) | **70%** |
| Base model + OpenMLE-Evo (framework improved, model fixed) | **50%** |

Model contribution and framework contribution are each validated separately on a held-out benchmark — the experimental design RSI research actually requires.

### Quick Start

```bash
git clone https://github.com/FrontisAI/OpenRSI.git
cd OpenRSI
```

| Goal | Start here |
|------|------------|
| Build or evaluate executable task packages | `OpenMLE-Gym/README.md` |
| Generate SFT data and launch supervised training | `OpenMLE-ERL/SFT/README.md` |
| Configure and launch execution-grounded RL | `OpenMLE-ERL/RL/README.md` |
| Run OpenMLE-Evo or a benchmark adapter | `OpenMLE-Evo/README.md` |

Model weights: [FrontisAI/Frontis-MA1-35B](https://huggingface.co/FrontisAI/Frontis-MA1-35B) (BF16) or [GGUF](https://huggingface.co/FrontisAI/Frontis-MA1-35B-GGUF).

### Why This Matters

**Executability** is OpenRSI's core claim. The AI4AI space isn't short on conceptual frameworks — what's rare is an end-to-end system that runs on real hardware, has programmatic verifiers, and produces reproducible results. OpenRSI open-sources the entire chain: task environments, training data generation, SFT, RL, long-horizon search. Researchers can reproduce results on OpenMLE tasks, or contribute new tasks, operators, and search strategies.

"The improver itself is trainable" positions OpenRSI as a complement to projects like TMax (AllenAI's terminal agent RL) and EvoScientist: TMax focuses on terminal command execution; OpenRSI focuses on ML program evolution. The training approaches differ too — outcome-only RL vs. SFT warm-start + online RL + evolutionary search.

CC BY-NC 4.0, non-commercial use. 188 stars (published 2026-07-31), growing fast.

Repository: [github.com/FrontisAI/OpenRSI](https://github.com/FrontisAI/OpenRSI) · Paper: [arXiv 2607.28568](https://arxiv.org/abs/2607.28568) · Models: [HuggingFace FrontisAI](https://huggingface.co/collections/FrontisAI/frontis-ma1)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
