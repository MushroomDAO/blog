---
title: 'NeoHorse-1：第一个认真搭递归自我改进原型的开源小模型'
titleEn: "NeoHorse-1: The First Open-Source Small Model Seriously Prototyping Recursive Self-Improvement"
description: "TokenRhythm 用 Routing Harness 让 4B/9B 模型自己观察执行轨迹、估算能力缺口、把反馈注回训练混合——十项基准平均 +5.93 vs Qwen3.5-4B。这不只是一次后训练，是一个闭环的雏形。"
descriptionEn: "TokenRhythm's Routing Harness lets 4B/9B models observe their own execution traces, estimate capability gaps, and inject feedback back into training — +5.93 average across ten benchmarks vs Qwen3.5-4B. Not just a post-training run — a prototype of a closed loop."
pubDate: "2026-09-12"
updatedDate: "2026-09-12"
category: "Research"
tags: ["LLM", "post-training", "recursive-self-improvement", "agent", "open-source", "Qwen3.5"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
---

> 📌 论文：NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness
> arXiv：https://arxiv.org/abs/2609.08183
> GitHub：https://github.com/TokenRhythm/NeoHorse
> HuggingFace：https://huggingface.co/collections/TokenRhythm/neohorse-1
> ModelScope：https://modelscope.cn/collections/TokenRhythm/NeoHorse-1
> License：Apache 2.0 · 发布：2026-09-07

---

**BLUF**：NeoHorse-1 是 TokenRhythm 发布的 4B/9B 开源 Agent 后训练模型，基于 Qwen3.5，Apache 2.0。它的特别之处不在于数字——尽管十项基准平均 +5.93 已经够扎实——而在于它的设计目标：**用一个叫 Routing Harness 的机制，搭出递归自我改进（RSI）的第一个原型闭环**。训练出来的模型可以重新进入 harness，形成评估-选择-更新的循环。这是一个起点，而不是终点。

---

## 递归自我改进：为什么这个方向重要

"递归自我改进"（Recursive Self-Improvement，RSI）是 AI 安全领域多年来反复讨论的概念——一个系统用自己的能力改进自己，改进后的版本再去改进，如此循环。

但大多数讨论停留在假设层面。NeoHorse-1 做了一件有意思的事：**用一个工程化的 harness，把这个概念做成了可以实际运行的东西**。

当然，它现在只是"原型"。但"一个真实运行的原型"和"一个思想实验"之间的距离，远比很多人以为的大。

---

## Routing Harness：核心机制

NeoHorse-1 的核心不是模型本身，而是训练它的 **Routing Harness（路由挽具）**。

这个机制的运作逻辑是：

```
任务进入 → Routing Harness 分发给异构模型池
              ↓
模型执行任务 → 记录工具调用轨迹和结果
              ↓
Harness 估算能力需求缺口
              ↓
把能力级别的反馈注入下一轮训练混合
              ↓
更新后的模型重新进入 Harness → 循环
```

关键设计：反馈不是人工设计的——**是模型自己在执行任务时暴露的能力边界，被 harness 捕获，转化为训练信号**。

这和普通的 SFT 或 RLHF 有本质区别：

- 普通 SFT：人工收集数据 → 训练
- 普通 RLHF：人工或模型打分 → 优化
- **Routing Harness**：让模型在真实 agent 环境里跑任务 → 自动捕获执行轨迹和失败模式 → 直接转化成下一轮训练的信号

---

## 训练方法：两个核心组件

**Routing-guided Curriculum SFT**

不是把所有数据随机混在一起训练，而是根据模型当前的能力边界，**动态决定用什么难度和类型的数据**。Harness 知道模型在哪些任务上容易失败，就把相关数据多塞一点进下一轮训练。

**Routing-guided On-policy Distillation**

在训练时，用的是模型自己生成的轨迹，而不是纯粹的人工数据。这保证了训练分布和实际执行分布的一致性——训练时见过的东西，和推理时遇到的东西，尽量是同一种结构。

**数据质量管道**：精确/近似去重、评估集去污染（防止基准数据泄露）、结构验证、六维语义评估、Scene/Goal/Outcome 三层子场景标注。

---

## 测评结果

测评用 SGLang v0.5.17，thinking 模式开启，十项基准覆盖 Agent 能力、编程、指令遵循三个维度。

### 4B 档（对比 Qwen3.5-4B）

| 基准 | Qwen3.5-4B | NeoHorse-1-4B | Δ |
|------|-----------|--------------|---|
| QwenClawBench | 38.47 | 44.68 | +6.21 |
| WorkBuddy Bench | 24.62 | 34.41 | **+9.79** |
| PinchBench | 71.19 | 77.33 | +6.14 |
| VitaBench | 21.50 | 32.00 | **+10.50** |
| BFCL v4 | 61.02 | 61.79 | +0.77 |
| tau2-Bench | 84.29 | 88.46 | +4.17 |
| HumanEval | 87.20 | 96.95 | **+9.75** |
| LiveCodeBench v6 | 53.71 | 59.43 | +5.72 |
| IFBench | 60.33 | 65.33 | +5.00 |
| IFEval | 87.06 | 88.35 | +1.29 |
| **十项平均** | **58.94** | **64.87** | **+5.93** |

### 9B 档（对比 Qwen3.5-9B）

| 基准 | Qwen3.5-9B | NeoHorse-1-9B | Δ |
|------|-----------|--------------|---|
| QwenClawBench | 44.04 | 48.73 | +4.69 |
| WorkBuddy Bench | 39.60 | 40.15 | +0.55 |
| PinchBench | 74.55 | 82.25 | **+7.70** |
| VitaBench | 31.25 | 42.25 | **+11.00** |
| BFCL v4 | 64.88 | 67.43 | +2.55 |
| tau2-Bench | 88.04 | 90.82 | +2.78 |
| HumanEval | 92.68 | 98.17 | +5.49 |
| LiveCodeBench v6 | 65.14 | 65.14 | +0.00 |
| IFBench | 66.33 | 66.33 | +0.00 |
| IFEval | 89.46 | 89.09 | -0.37 |
| **十项平均** | **65.60** | **69.04** | **+3.44** |

提升最明显的几项都在 Agent 类基准——这和 Routing Harness 的设计目标一致。VitaBench（+10.50/+11.00）的提升尤其大，这个基准测的是复杂 agent 任务的完整流程。

---

## 规格与部署

**模型规格**：
- 上下文长度：原生 262,144 tokens，可扩展到 1,010,000
- 权重格式：Safetensors / BF16
- GGUF 版本：BF16、8-bit、5-bit、4-bit 全提供（本地部署友好）

**SGLang 部署**：

```bash
pip install "sglang==0.5.17"
python3 -m sglang.launch_server \
  --model-path "/path/to/NeoHorse-1-4B" \
  --served-model-name neohorse-1-4B \
  --host 0.0.0.0 --port 30000 \
  --context-length 262144 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder
```

**vLLM 部署**：

```bash
vllm serve "/path/to/NeoHorse-1-4B" \
  --served-model-name neohorse-1-4B \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

---

## 为什么值得关注

NeoHorse-1 有两个地方值得认真看：

**一、RSI 原型是一个新的研究方向起点**

到目前为止，大多数开源模型的后训练都是"一次性的"：收数据、训模型、发布。NeoHorse-1 的 Routing Harness 第一次把"模型进入 harness → 执行 → 能力反馈 → 重新训练"做成了一个可以迭代的循环。现在 NeoHorse-1 是这个循环的第一轮，下一轮会是什么？

**二、Agent 类基准的大幅提升是可解释的**

NeoHorse-1 不是在所有任务上都显著提升——LiveCodeBench 和 IFEval 的提升很小甚至持平。但在 Agent 类任务（WorkBuddy、VitaBench、PinchBench）上的提升格外大。这和 Routing Harness 的设计方向高度一致：它就是为了让模型更好地完成 agent 任务而设计的。结果和设计目标吻合，说明这套方法是在解决真实问题。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Paper: NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness
> arXiv: https://arxiv.org/abs/2609.08183
> GitHub: https://github.com/TokenRhythm/NeoHorse
> HuggingFace: https://huggingface.co/collections/TokenRhythm/neohorse-1
> ModelScope: https://modelscope.cn/collections/TokenRhythm/NeoHorse-1
> License: Apache 2.0 · Released: 2026-09-07

---

**BLUF**: NeoHorse-1 is TokenRhythm's 4B/9B open-source agent post-training model based on Qwen3.5, Apache 2.0. Its significance isn't just the numbers — though +5.93 average across ten benchmarks is solid — but the design goal: **using a mechanism called the Routing Harness to build the first prototype closed loop for recursive self-improvement (RSI)**. The trained model can re-enter the harness, forming an evaluate–select–update cycle. This is a starting point, not an endpoint.

---

## Why Recursive Self-Improvement Matters

"Recursive Self-Improvement" (RSI) has been discussed in AI safety circles for years — a system using its own capabilities to improve itself, with each improved version doing the same, cycling forward.

Most of that discussion stays hypothetical. NeoHorse-1 does something interesting: **it engineers a harness that turns this concept into something that actually runs**.

It's a "prototype" right now. But the distance between "a working prototype" and "a thought experiment" is much larger than most people assume.

---

## The Routing Harness: Core Mechanism

NeoHorse-1's core isn't the model itself — it's the **Routing Harness** used to train it.

The logic:

```
Task arrives → Routing Harness assigns to heterogeneous model pool
                    ↓
Model executes → Records tool interaction traces and outcomes
                    ↓
Harness estimates capability demand gaps
                    ↓
Injects capability-level feedback into next training mixture
                    ↓
Updated model re-enters Harness → Loop
```

Critical design: the feedback isn't manually curated — **it's the model's own capability boundaries exposed during task execution, captured by the harness, and converted into training signal**.

This is fundamentally different from standard SFT or RLHF:

- Standard SFT: humans collect data → train
- Standard RLHF: humans or model score outputs → optimize
- **Routing Harness**: run model on real agent tasks → automatically capture execution traces and failure patterns → convert directly into next training round's signal

---

## Training Methods: Two Core Components

**Routing-guided Curriculum SFT**

Not mixing all data randomly. Instead, based on the model's current capability boundaries, **dynamically decide what difficulty and type of data to use**. The harness knows where the model tends to fail and feeds more relevant data into the next round.

**Routing-guided On-policy Distillation**

Training uses trajectories the model itself generated, not purely human-curated data. This keeps training distribution aligned with actual execution distribution — what the model sees during training stays structurally similar to what it encounters at inference time.

**Data quality pipeline**: exact/near-duplicate removal, evaluation decontamination (preventing benchmark leakage), structural validation, six-dimensional semantic evaluation, Scene/Goal/Outcome three-layer subscene labeling.

---

## Benchmark Results

Evaluated with SGLang v0.5.17, thinking mode enabled, ten benchmarks across agent capability, coding, and instruction following.

### 4B track (vs Qwen3.5-4B)

| Benchmark | Qwen3.5-4B | NeoHorse-1-4B | Δ |
|-----------|------------|--------------|---|
| QwenClawBench | 38.47 | 44.68 | +6.21 |
| WorkBuddy Bench | 24.62 | 34.41 | **+9.79** |
| PinchBench | 71.19 | 77.33 | +6.14 |
| VitaBench | 21.50 | 32.00 | **+10.50** |
| BFCL v4 | 61.02 | 61.79 | +0.77 |
| tau2-Bench | 84.29 | 88.46 | +4.17 |
| HumanEval | 87.20 | 96.95 | **+9.75** |
| LiveCodeBench v6 | 53.71 | 59.43 | +5.72 |
| IFBench | 60.33 | 65.33 | +5.00 |
| IFEval | 87.06 | 88.35 | +1.29 |
| **Average** | **58.94** | **64.87** | **+5.93** |

### 9B track (vs Qwen3.5-9B)

| Benchmark | Qwen3.5-9B | NeoHorse-1-9B | Δ |
|-----------|------------|--------------|---|
| QwenClawBench | 44.04 | 48.73 | +4.69 |
| PinchBench | 74.55 | 82.25 | **+7.70** |
| VitaBench | 31.25 | 42.25 | **+11.00** |
| tau2-Bench | 88.04 | 90.82 | +2.78 |
| HumanEval | 92.68 | 98.17 | +5.49 |
| **Average** | **65.60** | **69.04** | **+3.44** |

The biggest gains are in agent-class benchmarks — exactly what the Routing Harness was designed for. VitaBench's +10.50/+11.00 gains are notable; this benchmark tests complete-pipeline complex agent tasks.

---

## Specs and Deployment

**Model specs:**
- Context length: 262,144 natively, extensible to 1,010,000 tokens
- Format: Safetensors / BF16
- GGUF: BF16, 8-bit, 5-bit, 4-bit all available (local-friendly)

**SGLang deployment:**

```bash
pip install "sglang==0.5.17"
python3 -m sglang.launch_server \
  --model-path "/path/to/NeoHorse-1-4B" \
  --served-model-name neohorse-1-4B \
  --context-length 262144 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder
```

---

## Why This Is Worth Watching

Two things stand out:

**One: RSI prototype as a new research direction starting point**

Most open-source model post-training is a one-shot operation: collect data, train model, release. NeoHorse-1's Routing Harness is the first to make "model enters harness → executes → capability feedback → retrain" an iterable cycle. NeoHorse-1 is round one. What does round two look like?

**Two: Agent benchmark gains are mechanistically explained**

NeoHorse-1 doesn't improve uniformly across all tasks — LiveCodeBench and IFEval show minimal gains. But agent-class tasks (WorkBuddy, VitaBench, PinchBench) improve dramatically. This aligns precisely with the Routing Harness's design purpose. When results match design intent, it's evidence the method is solving a real problem.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
