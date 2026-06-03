---
title: "GEPA：让 LLM 阅读自己的执行轨迹进化 Prompt，比 GRPO 少用 35x rollout 却赢 20%"
titleEn: "GEPA: LLMs Evolve Prompts by Reading Their Own Traces — 35x Fewer Rollouts Than GRPO, Up to 20% Better"
description: "来自 UC Berkeley、Stanford、MIT、Databricks 的 ICLR 2026 口头报告论文：GEPA 让 LLM 通过阅读自己的执行轨迹，自动反思、进化并合并 prompt 经验，在 HotpotQA 等任务上比 GRPO 平均高 10%，比 MIPROv2 高 12%，同时只需不到 3% 的 rollout 数量。"
descriptionEn: "ICLR 2026 Oral from UC Berkeley, Stanford, MIT, Databricks: GEPA lets LLMs reflect on their own execution traces to automatically evolve and merge prompt knowledge. Outperforms GRPO by 10% on average (up to 20%), beats MIPROv2 by 12%, using under 3% of the rollouts."
pubDate: "2026-06-03"
updatedDate: "2026-06-03"
category: "Research"
tags: ["GEPA", "Prompt优化", "强化学习", "LLM", "GRPO", "进化算法", "AI Agent", "ICLR 2026", "论文", "UC Berkeley", "Stanford", "MIT"]
heroImage: "../../assets/images/gepa-reflective-prompt-evolution-banner.jpg"
---

强化学习（RL）优化 LLM 的主流范式是：跑几千次 rollout，从稀疏的标量奖励里反向传播梯度，让模型慢慢"感受到"什么行为是对的。GEPA 问了一个不同的问题：

> **如果让 LLM 直接阅读自己的执行轨迹，用自然语言说清楚"哪里错了、为什么错、怎么改"，会不会比稀疏奖励信号学得更快、更好？**

答案是肯定的。

> 📌 论文：https://arxiv.org/abs/2507.19457  
> GitHub：https://github.com/gepa-ai/gepa  
> 机构：UC Berkeley、Stanford、MIT、Databricks、BespokeLabs.ai、圣母大学  
> 发表：**ICLR 2026 Oral**（口头报告，顶会最高荣誉档）

## GEPA 是什么

**GEPA（Genetic-Pareto Prompt Optimizer）**是一个 prompt 自动优化系统，核心思路是把遗传算法的"进化+选择"结构，和 LLM 的自然语言反思能力结合起来。

它的优化对象是"复合 AI 系统"——即包含一个或多个 LLM prompt 的 pipeline，比如带工具调用的 Agent、多步推理系统、代码生成流水线。

三个核心动作形成闭环：

```
采样执行轨迹  →  自然语言反思诊断  →  Pareto 选择候选更新
      ↑                                        |
      └────────────────────────────────────────┘
```

## 工作原理：三步闭环

**第一步：采样轨迹（Trajectory Sampling）**

给定当前 prompt 配置，GEPA 让系统在训练样本上运行，完整记录执行轨迹——推理过程、工具调用、工具输出、最终答案。不只是"对还是错"，而是整个执行过程。

如果评测指标本身也提供诊断信息（比如编译器报错、性能 profiling 数据），GEPA 也会一并纳入，称为"评测轨迹（evaluation traces）"。

**第二步：自然语言反思（Reflective Mutation）**

用一个 LLM（通常是更强的模型）读取这些轨迹，结合成功和失败的样本，做三件事：

1. **诊断**：识别当前 prompt 的具体问题
2. **提出修改**：生成针对性的 prompt 更新
3. **合并经验**：把来自不同候选 prompt 的互补经验整合进去

这里的关键洞察是：自然语言反思能提供比标量奖励丰富得多的学习信号。GRPO 看到的是"这次 +0.3 分"，GEPA 看到的是"模型在第二跳检索时用了错误的实体，应该在 prompt 里明确要求先验证实体一致性"。

**第三步：Pareto 候选选择（Pareto-based Selection）**

这是 GEPA 避免陷入局部最优的核心机制。

朴素策略是"一直进化表现最好的候选 prompt"——但这容易让优化树过早收敛到一个局部解。GEPA 的做法：

1. 对每个训练样本，找出在该样本上得分最高的候选 prompt
2. 汇总所有"在至少一个样本上是最优"的候选，构成 Pareto 前沿
3. 移除被完全支配的候选（某候选在所有样本上都不如另一个）
4. 按候选在 Pareto 前沿中出现的频率，概率性采样下一个进化目标

结果是一棵平衡的搜索树，而不是沿单条路径收敛的枯枝。

## 实验结果：对比 GRPO 和 MIPROv2

测试集：HotpotQA（多跳问答）、IFBench（指令遵循）、HoVer（多跳事实验证）、PUPA（隐私感知委托任务）。模型：Qwen3 8B 和 GPT-4.1 Mini。

**主要结果（Qwen3 8B，vs 零样本基线）**：

| 方法 | HotpotQA | IFBench | HoVer | PUPA | 平均提升 |
|------|---------|---------|-------|------|---------|
| 基线 | 42.33 | 36.90 | 35.33 | 80.82 | — |
| MIPROv2 | 55.33 | 36.22 | 47.33 | 81.55 | +6.26% |
| GRPO | 43.33 | 35.88 | 38.67 | 86.66 | +2.29% |
| **GEPA** | **62.33** | **38.61** | **52.33** | **91.85** | **+12.44%** |

**对比 GRPO 的 rollout 效率**：

GRPO 在这些任务上用了 **24,000 次 rollout**（含 LoRA 微调）。GEPA 达到最优性能只需：

| 任务 | GEPA 所需 rollout | GRPO | 节省比 |
|------|-----------------|------|------|
| HotpotQA | 737 | 24,000 | **32x** |
| IFBench | 79 | 24,000 | **303x** |
| HoVer | 558 | 24,000 | **43x** |
| PUPA | 269 | 24,000 | **89x** |

即便如此，GEPA 在 HotpotQA 上比 GRPO 高 **19%**，HoVer 上高 **13.66%**，平均高 **10%**。

## 推理时搜索：NPU/CUDA 内核生成

GEPA 还被用在一个特殊场景：**针对单个问题实例的推理时搜索**——把 prompt 进化当作对单个实例的反复精炼工具。

**AMD XDNA2 NPU 内核生成**：

| 方法 | 向量利用率 |
|------|---------|
| GPT-4o 基线 | 4.25% |
| GEPA 进化后 | **30.52%**（最高单核 70%） |

**CUDA 内核生成（KernelBench，35 个任务）**：

GEPA 利用编译器报错和 profiling 输出作为评测轨迹，动态检索技术手册相关章节注入 prompt，把 fast₁ 得分从接近 0% 提升到 20% 以上。

## 为什么这个结果重要

强化学习的支持者常说"RL 可以让模型学到语言反思覆盖不到的隐式规律"。GEPA 的实验数据显示，至少在 prompt 优化这个层面，情况相反：

- **语言是更丰富的学习介质**。"在第二跳检索时验证实体一致性"比 "+0.1 奖励" 包含更多可操作信息。
- **RL 的 rollout 代价极高**。24,000 次 rollout + LoRA 微调，资源消耗是 GEPA 的几十到几百倍。
- **GEPA 不改变模型权重**。它只修改 prompt，这意味着优化结果可解释、可检查、可迁移。

当然，GEPA 并不是要取代所有 RL——权重级别的学习有 GEPA 触及不到的能力边界。但在"优化 AI 系统的 prompt 配置"这个具体问题上，GEPA 给出了一个更轻量、更高效的答案。

论文被 ICLR 2026 接收为 Oral（口头报告），代码已开源：https://github.com/gepa-ai/gepa

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

The mainstream RL paradigm for optimizing LLMs works like this: run thousands of rollouts, backpropagate gradients from sparse scalar rewards, and let the model slowly sense what behaviors are correct. GEPA asks a different question:

> **What if you let the LLM directly read its own execution traces — and use natural language to articulate "what went wrong, why, and how to fix it"? Would it learn faster and better than sparse reward signals?**

The answer is yes.

> 📌 Paper: https://arxiv.org/abs/2507.19457  
> GitHub: https://github.com/gepa-ai/gepa  
> Institutions: UC Berkeley, Stanford, MIT, Databricks, BespokeLabs.ai, University of Notre Dame  
> Venue: **ICLR 2026 Oral**

## What Is GEPA

**GEPA (Genetic-Pareto Prompt Optimizer)** is an automatic prompt optimization system that combines the evolution-and-selection structure of genetic algorithms with the natural language reflection capabilities of LLMs.

Its optimization target is a **compound AI system** — any pipeline containing one or more LLM prompts: tool-calling agents, multi-step reasoning systems, code generation pipelines.

Three core actions form a closed loop:

```
Sample execution traces  →  Reflect in natural language  →  Pareto-based candidate selection
         ↑                                                              |
         └──────────────────────────────────────────────────────────────┘
```

## How It Works: Three-Step Loop

**Step 1: Trajectory Sampling**

Given the current prompt configuration, GEPA runs the system on training examples and records the complete execution trace — reasoning steps, tool calls, tool outputs, final answers. Not just "right or wrong" — the entire execution process.

If the evaluation metric itself provides diagnostic information (compiler errors, profiling results), GEPA captures those too as "evaluation traces."

**Step 2: Reflective Mutation**

A (typically stronger) LLM reads these traces, reviews successful and failed examples, and does three things:

1. **Diagnose**: Identify specific problems in the current prompt
2. **Propose updates**: Generate targeted prompt modifications
3. **Merge insights**: Integrate complementary lessons from different candidate prompts

The key insight: natural language reflection provides a far richer learning signal than scalar rewards. GRPO sees "+0.3 points." GEPA sees: "the model retrieved the wrong entity on the second hop — the prompt should explicitly require verifying entity consistency before proceeding."

**Step 3: Pareto-Based Candidate Selection**

This is GEPA's mechanism for avoiding local optima.

The naive strategy is to always evolve the best-performing candidate prompt — but this causes the optimization tree to converge prematurely to a local solution. GEPA's approach:

1. For each training instance, find the highest-scoring candidate prompt
2. Collect all candidates that are optimal on at least one instance — the Pareto frontier
3. Remove dominated candidates (a candidate strictly worse than another on all instances)
4. Sample the next candidate to evolve with probability proportional to its Pareto frontier frequency

The result is a balanced search tree, not a branch that collapses toward a single path.

## Results: vs. GRPO and MIPROv2

Benchmarks: HotpotQA (multi-hop QA), IFBench (instruction following), HoVer (multi-hop fact verification), PUPA (privacy-aware delegation). Models: Qwen3 8B and GPT-4.1 Mini.

**Main results (Qwen3 8B, vs. zero-shot baseline)**:

| Method | HotpotQA | IFBench | HoVer | PUPA | Avg Improvement |
|--------|---------|---------|-------|------|-----------------|
| Baseline | 42.33 | 36.90 | 35.33 | 80.82 | — |
| MIPROv2 | 55.33 | 36.22 | 47.33 | 81.55 | +6.26% |
| GRPO | 43.33 | 35.88 | 38.67 | 86.66 | +2.29% |
| **GEPA** | **62.33** | **38.61** | **52.33** | **91.85** | **+12.44%** |

**Rollout efficiency vs. GRPO**:

GRPO used **24,000 rollouts** (with LoRA fine-tuning) across these tasks. GEPA reaches optimal performance with:

| Task | GEPA rollouts | GRPO | Savings |
|------|-------------|------|---------|
| HotpotQA | 737 | 24,000 | **32x** |
| IFBench | 79 | 24,000 | **303x** |
| HoVer | 558 | 24,000 | **43x** |
| PUPA | 269 | 24,000 | **89x** |

Despite this, GEPA beats GRPO by **+19%** on HotpotQA, **+13.66%** on HoVer, **+10%** on average.

## Inference-Time Search: NPU and CUDA Kernel Generation

GEPA was also applied to **instance-level inference-time search** — using prompt evolution as an iterative refinement tool targeting a single problem instance.

**AMD XDNA2 NPU kernel generation**:

| Method | Vector utilization |
|--------|------------------|
| GPT-4o baseline | 4.25% |
| GEPA-evolved | **30.52%** (individual kernels up to 70%) |

**CUDA kernel generation (KernelBench, 35 tasks)**:

Using compiler errors and profiling output as evaluation traces, GEPA dynamically retrieves relevant technical manual sections to inject into the prompt — improving the fast₁ score from near 0% to above 20%.

## Why This Result Matters

RL proponents often argue that "RL can learn implicit patterns that language reflection can't reach." GEPA's data suggests that in prompt optimization specifically, the opposite is true:

- **Language is a richer learning medium**. "Verify entity consistency before the second hop" carries more actionable information than "+0.1 reward."
- **RL rollouts are expensive**. 24,000 rollouts + LoRA fine-tuning costs tens to hundreds of times more compute than GEPA.
- **GEPA doesn't change model weights**. Prompt-level optimization produces interpretable, inspectable, transferable results.

GEPA isn't claiming to replace all RL — weight-level learning has capabilities beyond any prompt's reach. But for the specific problem of optimizing prompt configurations in AI systems, it offers a lighter, more efficient answer.

ICLR 2026 Oral. Code: https://github.com/gepa-ai/gepa

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
