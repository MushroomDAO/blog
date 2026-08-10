---
title: "OpenRSI：让「AI 改进 AI」变成可执行、可测量的工程问题"
titleEn: "openrsi-frontis-ma1-recursive-self-improvement-ai4ai-mle"
description: "FrontisAI/OpenRSI，arXiv:2607.28568，CC BY-NC 4.0，Python。把递归自改进（RSI）从哲学概念变成工程实验的开源全栈系统。核心：以机器学习工程（MLE）为首个可执行领域，训练 Frontis-MA1（35B）作为元演化 Agent，用四个原子算子（Draft/Improve/Debug/Crossover）统一后训练和推理。MLE-Bench Lite 上，单张 RTX 4090，Medal Average 从 39.39% 升到 71.21%，超过 GPT-5.5 + Codex（68.18%），逼近 GPT-5.6 Sol 和 2.8T 的 Kimi K3。模型权重、Gym、训练、搜索、评估全部开源。"
descriptionEn: "FrontisAI/OpenRSI, arXiv:2607.28568, CC BY-NC 4.0, Python. An open full-stack system that turns recursive self-improvement (RSI) from a philosophical concept into an executable engineering problem. Core: uses machine learning engineering (MLE) as the first executable domain, trains Frontis-MA1 (35B) as a meta-evolution agent, unifies post-training and inference around four atomic operators (Draft/Improve/Debug/Crossover). On MLE-Bench Lite with a single RTX 4090, Medal Average rises from 39.39% to 71.21%, beating GPT-5.5 + Codex (68.18%) and approaching GPT-5.6 Sol and 2.8T Kimi K3. Weights, gym, training, search, and eval: all released."
pubDate: "2026-08-10"
updatedDate: "2026-08-10"
category: "Research"
tags: ["AI", "RSI", "自改进", "论文", "开源", "MLE", "元演化", "Mycelium"]
heroImage: "../../assets/images/openrsi-frontis-ma1-recursive-self-improvement-ai4ai-mle-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

「AI 改进 AI」这个概念存在了很长时间，但它通常停留在哲学讨论层面——难以定义「改进」是什么，难以测量，更难以验证。

OpenRSI 做的是把它变成一个工程问题：**可执行的、有数值结果的、可重现的**。

第一个工程领域是机器学习工程（MLE）本身——训练模型、调参数、优化流程。这是 AI 研究的核心工作，也是最适合用 AI 来做的域。

arXiv: https://arxiv.org/abs/2607.28568 | GitHub: https://github.com/FrontisAI/OpenRSI | ⭐ 327 | CC BY-NC 4.0 | Python

---

## 核心问题

为什么 RSI（递归自改进）难做？

1. **行动空间不明确**：「改进」可以是无数种操作，边界不清楚
2. **反馈信号难获取**：改进之后好了多少？难以量化
3. **训练和推理脱节**：模型训练的行为和实际搜索中用到的行为不一样

OpenRSI 的答案：**把 MLE 任务设计成可执行的验证环境，定义四个原子算子作为唯一行动空间，用执行结果（代码跑了多好）作为反馈，让训练和推理用同一套算子**。

---

## 四个原子算子

整个系统（训练 + 推理 + 搜索）只有四个操作：

| 算子 | 作用 |
|------|------|
| **Draft** | 从头生成一个程序 |
| **Improve** | 基于执行反馈改进一个父程序 |
| **Debug** | 修复一个出错的程序 |
| **Crossover** | 把两个父程序的优点重组 |

这四个算子是训练数据的结构，也是推理时的动作，也是进化搜索的变异操作。**训练和推理没有断层**——模型学到的东西直接可以在搜索阶段使用。

---

## OpenMLE 全栈

```
┌────────────────────────────────────────────────────┐
│                   OpenRSI 全栈                      │
│                                                    │
│  OpenMLE-Gym                                       │
│   — 可执行的 MLE 任务包（构建、描述、执行、质检）    │
│   — OpenMLE Sandbox：分布式代码执行 + 自动评估      │
│                     ↓                              │
│  OpenMLE-RL                                        │
│   — 执行反馈驱动的 SFT（监督微调）                  │
│   — 在线 RL，学习四个原子算子                       │
│                     ↓                              │
│  Frontis-MA1（35B / 30B）                          │
│   — 后训练的元演化 Agent                            │
│   — 用四个算子做 MLE 任务的 meta-evolution          │
│                     ↓                              │
│  OpenMLE-Evo / Evo-Max                             │
│   — 长视野进化搜索（标准 / 异步多 GPU 版）          │
│   — 经验反哺训练，形成闭环                          │
└────────────────────────────────────────────────────┘
```

**OpenMLE-Gym** 提供可验证的 MLE 任务环境。每个任务都有可执行的代码框架和量化验证标准（Medal Average 等）。

**OpenMLE-RL** 把执行结果当作反馈信号训练算子——做了什么、跑出来什么结果、比上一版好了多少，都记录下来作为训练数据。

**OpenMLE-Evo** 把训练好的算子组合成长视野搜索：Draft 一个初始版本，反复 Improve、偶尔 Debug 和 Crossover，每一代的执行结果都进入经验库，影响下一代。

**Evo-Max**（异步版本）：多 GPU 并行搜索，加入 benchmark-independent 的经验先验，是目前最强的配置。

---

## 实验结果

**测试集**：MLE-Bench Lite，每任务 12 小时预算，单张 RTX 4090（显存限制 12GB）

| 配置 | Medal Average |
|------|--------------|
| 基础模型（不加任何搜索） | 39.39% |
| Frontis-MA1-35B + OpenMLE-Evo | 60.61% |
| **Frontis-MA1-35B + OpenMLE-Evo-Max** | **71.21%** |
| GPT-5.5 + Codex（参考） | 68.18% |
| GPT-5.6 Sol（参考） | ~73% |
| Kimi K3（2.8T 参数，参考） | ~73% |

**后训练增益**：同一套搜索框架，基础模型 → Frontis-MA1，提升 +21.22pp（39.39% → 60.61%）

**框架增益**：同一个模型，不加搜索 → OpenMLE-Evo-Max，可以额外提升约 +10pp

两个维度独立可测，说明模型能力和搜索框架是分开起作用的，而不是互相掩盖。

**迁移测试（NatureBench Lite，全新 held-out 数据集）**：

| 实验 | Match-SOTA |
|------|-----------|
| 基础模型，不加框架 | 20% |
| 固定基础模型，换入 OpenMLE-Evo | 50% |
| 固定框架，换入 Frontis-MA1 | 70% |

模型和框架都能独立迁移，说明学到的不是 benchmark 特化的技巧，而是通用的 MLE 能力。

---

## 机制层级

OpenRSI 把自改进分成四个层级：

**L1 演化（Evolution）**：程序在进化，改进算子本身不变。经典的进化算法。

**L2 自演化（Self-Evolution）**：经验流回搜索过程，影响下一代的方向。

**L3 元演化（Meta-Evolution）**：**改进算子本身被训练**。这是 Frontis-MA1 达到的层级——模型学会了如何改进，而不只是执行改进。

**L4 递归自改进（RSI）**：完整的自我改进闭环。OpenRSI 明确表示目前处于 L3，没有声称达到了一般性的 RSI。

这个诚实的定位是这篇论文值得信任的地方之一。

---

## 开放内容

**全部开源**（CC BY-NC 4.0）：

| 内容 | 地址 |
|------|------|
| Frontis-MA1-35B 权重 | HuggingFace |
| Frontis-MA1-30B 权重 | HuggingFace |
| GGUF 版本（35B + 30B） | HuggingFace |
| OpenMLE Tasks 数据集 | HuggingFace |
| OpenMLE SFT Traces | HuggingFace |
| OpenMLE-Gym 代码 | GitHub |
| OpenMLE-RL（SFT + RL）代码 | GitHub |
| OpenMLE-Evo 代码 | GitHub |
| OpenMLE Sandbox（分布式执行后端） | GitHub（2026-08-09 新发布）|

---

## 快速开始

```bash
git clone https://github.com/FrontisAI/OpenRSI
cd OpenRSI

# 安装（建议 uv 或 conda）
pip install -e .

# 运行 OpenMLE-Evo（需要本地 Frontis-MA1 或 API）
# 详见各组件目录下的 README
```

**Sandbox 部署**（分布式执行评估）：
```bash
# 参考 OpenMLE-Gym/openmle-sandbox/README.md
# 支持 CPU/GPU 作业调度 + 可选多控制器路由
```

---

## 为什么这个工作有意义

大模型变大是一种改进 AI 的方式，但它不是自我改进——是人类工程师在做改进。

OpenRSI 问的是另一个问题：**AI 系统能不能主动做 AI 研究本身需要做的事情**——设计实验、写代码、跑出结果、分析失败、改进方案？

在 MLE 这个领域里，一张消费级 GPU（RTX 4090），35B 参数的模型，已经可以超过 GPT-5.5 + Codex 这个组合。

更重要的是，模型能力和搜索框架的增益是可分离的、可测量的、可迁移的。这说明在 MLE 领域，「AI 改进 AI」已经不是假设，而是可以用数字回答的工程问题。

OpenRSI 把这条路的起点开源了出来。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenRSI: Making "AI Improving AI" an Executable Engineering Problem

*by Mycelium Protocol*

---

"AI improving AI" has been a concept for a long time, but it usually stays at the philosophical level — hard to define what "improvement" means, hard to measure, harder to verify.

OpenRSI turns it into an engineering problem: **executable, measurable, reproducible**.

The first executable domain is machine learning engineering (MLE) itself — training models, tuning hyperparameters, optimizing pipelines. This is the core work of AI research, and also the domain most suited for AI to tackle.

arXiv: https://arxiv.org/abs/2607.28568 | GitHub: https://github.com/FrontisAI/OpenRSI | ⭐ 327 | CC BY-NC 4.0 | Python

---

### The Core Problem

Why is RSI (recursive self-improvement) hard?

1. **Unclear action space**: "Improvement" could be any of infinite operations
2. **Hard to get feedback**: How much better did an improvement actually make things?
3. **Training-inference disconnect**: What the model is trained on differs from what it does at inference

OpenRSI's answer: **design MLE tasks as executable verified environments, define four atomic operators as the entire action space, use execution results as feedback, and align training and inference around the same operators**.

---

### Four Atomic Operators

The entire system — training, inference, and search — uses only four operations:

| Operator | Function |
|----------|----------|
| **Draft** | Generate a program from scratch |
| **Improve** | Refine a parent program using execution feedback |
| **Debug** | Repair a failing program |
| **Crossover** | Recombine two parent programs |

These operators are the structure of training data, the actions at inference time, and the mutation operations in evolutionary search. **No gap between training and inference** — what the model learns is directly usable in the search phase.

---

### The OpenMLE Stack

- **OpenMLE-Gym**: Executable, verified MLE task packages (build, describe, execute, quality-check). Includes OpenMLE Sandbox: distributed code execution + automatic evaluation
- **OpenMLE-RL**: Execution-grounded SFT + online RL to learn the four operators
- **Frontis-MA1 (35B / 30B)**: Post-trained meta-evolution agent using the four operators for MLE tasks
- **OpenMLE-Evo / Evo-Max**: Long-horizon evolutionary search (standard / async multi-GPU)

---

### Results

**Test: MLE-Bench Lite, 12h/task budget, single RTX 4090 (12GB VRAM cap)**

| Configuration | Medal Average |
|---------------|--------------|
| Base model (no search) | 39.39% |
| Frontis-MA1-35B + OpenMLE-Evo | 60.61% |
| **Frontis-MA1-35B + OpenMLE-Evo-Max** | **71.21%** |
| GPT-5.5 + Codex (reference) | 68.18% |
| GPT-5.6 Sol / 2.8T Kimi K3 (reference) | ~73% |

**Post-training gain**: Same search framework, base → Frontis-MA1: +21.22pp

**Framework gain**: Same model, no search → Evo-Max: ~+10pp additional

Both dimensions are independently measurable — model capability and search framework contribute separately, neither masking the other.

**Transfer (NatureBench Lite, fully held-out):**
- Base model, no framework: 20%
- Fixed base model + OpenMLE-Evo: 50%
- Fixed framework + Frontis-MA1: 70%

Both model and framework transfer independently — learned capabilities are general MLE knowledge, not benchmark-specific tuning.

---

### Mechanism Hierarchy

- **L1 Evolution**: Programs evolve; the improver operator is frozen
- **L2 Self-Evolution**: Experience feeds back into search
- **L3 Meta-Evolution**: **The improver is itself trained** — what Frontis-MA1 achieves
- **L4 RSI**: Full self-improvement loop. OpenRSI explicitly states it currently operates at L3, without claiming general RSI

This honest positioning is one of the reasons the paper is credible.

---

### What's Actually Released

Weights (35B + 30B, BF16 + GGUF), OpenMLE-Tasks dataset, OpenMLE SFT Traces dataset, and the complete OpenMLE-Gym / RL / Evo code — all under CC BY-NC 4.0. OpenMLE Sandbox (distributed execution backend) was released on 2026-08-09.

---

### Why This Matters

Scaling models up is one way to improve AI — but it's not self-improvement, it's human engineers doing the improving.

OpenRSI asks a different question: **can an AI system actively do what AI research requires** — design experiments, write code, observe results, analyze failures, and improve the approach?

In the MLE domain, on a single consumer GPU (RTX 4090), a 35B model already exceeds GPT-5.5 + Codex. More importantly, the model's contribution and the search framework's contribution are separable, measurable, and transferable.

In MLE, "AI improving AI" is no longer a hypothesis. It's an engineering question with a numerical answer.

OpenRSI released the starting point for that path.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
