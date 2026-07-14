---
title: "训练 AI Agent 的数据配方：OpenThoughts-Agent 100+ 消融实验全拆解"
titleEn: "The SFT Data Recipe for AI Agents: OpenThoughts-Agent's 100+ Ablations Fully Decoded"
description: "UC Berkeley、Stanford、Bespoke Labs 等多机构合作的 OpenThoughts-Agent 论文（arXiv:2606.24855）做了迄今最系统的 Agent SFT 数据配方研究：6 阶段流水线、100+ 消融实验、100K 数据集，微调 Qwen3-32B 达 7 基准均值 44.8%，超越 Nemotron 3.9pp。最有价值的不是模型权重，而是那套可复用的数据选取逻辑。"
descriptionEn: "OpenThoughts-Agent (arXiv:2606.24855) from UC Berkeley, Stanford, and Bespoke Labs delivers the most systematic open study of agent SFT data curation: 6-stage pipeline, 100+ ablations, 100K dataset, Qwen3-32B fine-tune averaging 44.8% across 7 benchmarks (+3.9pp over Nemotron). The real value isn't the model weights — it's the reusable data selection logic."
pubDate: "2026-07-14"
updatedDate: "2026-07-14"
category: "Research"
tags: ["AI Agent", "SFT", "数据配方", "开源"]
heroImage: "../../assets/images/openthoughts-agent-sft-data-recipe-agentic-models-banner.jpg"
---

> 论文：**OpenThoughts-Agent: Data Recipes for Agentic Models**  
> arXiv：[2606.24855](https://arxiv.org/abs/2606.24855)  
> 发布：2026 年 6 月 23 日  
> 机构：UC Berkeley、Stanford、Bespoke Labs、UT Austin、NYU、UCLA 等  
> 开放资源：[openthoughts.ai](https://openthoughts.ai)

---

## 这篇论文在解决什么问题

DeepSeek V4 发布时，论文超过 50 页，详细描述了架构和训练过程——但训练数据只有两段话。

这是整个 AI Agent 领域的缩影：最前沿的 Agent 模型（Claude Code、Codex、OpenClaw）能力越来越强，但「如何为 Agent 构造训练数据」这个问题几乎完全是个黑盒。现有的开源数据工作——SWE-Smith、SERA、Nemotron-Terminal——都只针对单一 Benchmark，没有人回答「怎么训出一个在多种 Agent 任务上都强的模型」。

OpenThoughts-Agent 项目（OT-Agent）正面回答这个问题。不是发布一个更强的模型，而是做了**迄今最系统的 Agent SFT 数据配方研究**，把 100+ 控制变量实验的结论全部开放。

---

## 核心数字

| 指标 | 数值 |
|---|---|
| 消融实验数量 | 100+ |
| SFT 流水线阶段 | 6 个 |
| 最终训练集规模 | 100K 条 |
| 基础模型 | Qwen3-32B |
| 7 基准均值 | **44.8%** |
| 超越 Nemotron-Terminal-32B | **+3.9pp**（40.9% → 44.8%） |
| SWE-Bench Verified | **54.0%**（vs 41.9%） |
| Terminal-Bench 2.0 | **26.2%**（vs 25.1%） |

---

## 6 阶段 SFT 数据流水线

每一个阶段都被**独立消融**：控制其他所有变量不变，只改这一个。评价指标是三个 Benchmark 的 z-score 均值，保证不同精度区间的任务有相同权重。

### 阶段 1：任务来源（Sourcing Tasks）

**这是整个流水线里最重要的一步。**

论文测试了 95 种任务生成策略，涵盖不同的初始来源、生成方式（合成 vs 人工），以及领域。结论是：

- **任务来源的选择可以让 SWE-Bench Verified-100 的精度差距高达 30pp，Terminal-Bench 2.0 差距高达 10pp**
- 最终 Top-4 来源：`swe-smith`（合成 GitHub Issue）、`stackexchange-superuser`（人工 Linux 问题）、`stackexchange-tezos`（人工加密货币问题）、`issue-tasks`（合成 Issue）
- 领域知识覆盖影响很大：以代码为主的数据集能提升 SWE-Bench，以运维/基础设施为主的能提升 Terminal-Bench

### 阶段 2：任务混合（Mixing Tasks）

拿到 95 种策略的排名后，论文测试了 Top-1、Top-2……Top-N 的混合效果。

**结论：Top-4 到 Top-8 的混合最优，比只用 Top-1 更好。**

原因是过于专注单一来源会导致「只在 SWE-Bench 上强」，混合带来泛化能力。但超过 Top-16 反而下降——低质来源引入噪声。

### 阶段 3：任务增强（Task Augmentation）

一个自然的假设：能否通过 LLM 改写任务描述（加约束、升难度、合并任务）来提升数据质量？

**所有的 LLM 增强策略都没有提升**，甚至略有下降。原始任务描述保持不变是最好的策略。

（注意：这里指的是在 10K 实验阶段的人工写任务增强。后面扩规模时的合成增强是另一回事，那个有效。）

### 阶段 4：任务过滤（Filtering Tasks）

**LLM 任务过滤器有效：+3pp 均值。**

具体做法：用 GPT-5 生成任务解答时，保留需要 GPT-5 消耗更多 token 才能解决的任务——这些「更难的」任务对模型训练更有价值。这个信号可以作为过滤阈值，也可以作为后续扩规模时的**上采样权重**。

### 阶段 5：教师模型（Teacher Model）

这是论文里最反直觉的发现之一。

论文在 TerminalBench 2.0 表现最好的几个模型之间做消融：GPT-5.3-Codex、Kimi K2.5、GLM-4.7-AWQ、GLM 5、GLM-4.6-AWQ。

**结论：GLM-4.7-AWQ 是最好的教师，比 GPT-5.3-Codex 好约 5%（Terminal-Bench 2.0）。**

也就是说，**评测时表现最好的模型，不一定能生成最好的训练轨迹**。这个反直觉结论在推理数据领域也曾出现，现在在 Agent 数据领域得到了证实。

### 阶段 6：轨迹过滤（Filtering Agent Rollouts）

对 Agent 交互轨迹本身做过滤，几个策略：
- 移除超时的 trace
- 移除子 Agent trace
- **过滤掉少于 5 轮的 trace**（效果最大）

**更长的 trace = 更好的质量**，这个结论在 compute-controlled（等 token 预算）的对照实验里仍然成立，确认是质量提升而非计算量增加带来的收益。

---

## 扩规模时发现的关键瓶颈

6 阶段流水线确定后，论文把数据集从 10K 扩到 100K。

有 4 种扩规模策略：

| 方法 | 做法 | 结果 |
|---|---|---|
| Method 1 | 同任务描述，生成更多轨迹 | **31.6K→100K 平台效应，不再增长** |
| Method 2 | 原始来源取更多任务描述 | 受限于来源数量（Tezos 只有 997 个任务） |
| Method 3 | 合成增强任务描述 | **继续增长，突破平台** |
| Method 4 | 扩展到更多来源（Top-8、Top-16） | 不可靠，Top-16 全面下降 |

**核心结论：任务描述多样性是瓶颈。多轮采样同一批任务的效用会枯竭，合成增强才能持续 Scale。**

具体做法：把 Tezos 的 997 道题用 LLM 改写（注意：这里的合成增强指扩展任务的表面形式，不是生成新任务类型），把独特表述从 902 种扩展到超过 21,000 种，然后用 GPT-5 token 长度信号做**概率上采样权重**（而非 hard filter），保留全部任务覆盖。

最终 100K 数据集命名为 **OpenThoughts-Agent-v2**，数据来源：
- SWE-Smith（合成 GitHub Issues）
- StackExchange SuperUser（人工 Linux 任务）
- StackExchange-Tezos（人工加密货币问题 + 合成增强）
- IssueTasks（合成 Issues）

---

## RL 阶段：来源同样重要

论文在 8B 规模做了 RL 消融（RLOO 算法，binary reward）。测试了 6 个数据来源：

- `pymethods2test`（竞技编程 → Python 合约）
- `inferredbugs`（真实仓库 Bug 修复）
- `code-contests`（竞技编程环境）
- `nemotron-code-oracle`（LLM 过滤的 Nemotron 代码）
- `llm-verifier-freelancer`（LLM 验证的自由职业任务）
- `nl2bash`（自然语言 → Bash）

**`pymethods2test` 是意外的赢家**，论文对此做了详细的行为分析。使用这个数据源，8B 模型展现出「真正的探索行为」——它尝试多种不同的方法，即使前几次失败；而用 LLM verifier 数据训练的模型表现出「压缩行为」，遇到难题时倾向于停止而不是继续探索。

最终 SFT→RL 的两阶段 8B 模型超越了单阶段 SFT 8B 以及同规模最强基线。

---

## 四个最值得记住的反直觉结论

**1. 更好的模型 ≠ 更好的教师**

GPT-5.3-Codex 在评测上比 GLM-4.7 强，但 GLM-4.7 生成的训练轨迹更有效。原因尚不完全明确，但这意味着「用最强模型蒸馏」不是最优策略。

**2. 更多来源 ≠ 更好**

Top-4 mix 最优。Top-16 反而全面下降。噪声来源会稀释高质量信号。

**3. LLM 增强任务描述没用**

所有「让 LLM 改写、增加约束、升难度」的策略，在 10K 规模的消融中都没有提升。原始任务胜出。

（但注意区分：这里是在固定任务集上做风格增强；后续扩规模时的合成增强是针对稀缺任务用更多种表述形式，目标不同。）

**4. 合成才是 Scale 的唯一出路**

在已有任务上多采样只能到 31.6K，之后平台。合成扩展任务描述的多样性才能突破上限，在 100K 仍然保持增长曲线。

---

## 7 个评测基准

论文的 7 基准覆盖面很广，不只是 SWE-Bench：

| 基准 | 类型 |
|---|---|
| SWE-Bench Verified | GitHub Issue 修复（Python） |
| Terminal-Bench 2.0 | 终端任务（SWE、生物、安全、系统管理、ML） |
| OpenThoughts-TBLite | Terminal-Bench 风格快速代理（100 任务） |
| Aider Polyglot | 多语言代码编辑 |
| BFCL-Parity | 函数调用 |
| GAIA-127 | 通用 Agent 能力 |
| FinanceAgent-Terminal | 金融领域 Agent |

OT-Agent 在所有 7 个基准上都优于 Nemotron-Terminal-32B，不是在某一两个上强而在其他上弱。

---

## 开放资源

论文配套的全部资源已发布在 [openthoughts.ai](https://openthoughts.ai)：

- **模型**：[open-thoughts/OpenThinker-Agent-v1](https://huggingface.co/open-thoughts/OpenThinker-Agent-v1)（SFT+RL）
- **SFT-only 模型**：[OpenThinker-Agent-v1-SFT](https://huggingface.co/open-thoughts/OpenThinker-Agent-v1-SFT)
- **SFT 数据（轨迹）**：[OpenThoughts-Agent-v1-SFT](https://huggingface.co/datasets/open-thoughts/OpenThoughts-Agent-v1-SFT)
- **RL 数据（环境）**：[OpenThoughts-Agent-v1-RL](https://huggingface.co/datasets/open-thoughts/OpenThoughts-Agent-v1-RL)
- **新基准**：[OpenThoughts-TBLite](https://huggingface.co/datasets/open-thoughts/OpenThoughts-TBLite)
- **代码**：[github.com/open-thoughts/OpenThoughts-Agent](https://github.com/open-thoughts/OpenThoughts-Agent)

---

## 这篇论文为什么值得读

能发一个比别人强 3.9pp 的模型的论文很多。能把「100+ 消融实验的每个决策节点」全部开放、可复述、可迁移的论文，非常少。

如果你在做任何规模的 Agent 训练，这 6 个阶段的流水线和那几个反直觉发现，是可以直接拿来用的工程知识，而不只是「又一篇 SOTA 论文」。

---

论文：[arxiv.org/abs/2606.24855](https://arxiv.org/abs/2606.24855)  
资源：[openthoughts.ai](https://openthoughts.ai)

© 2026 Author: Mycelium Protocol

<!--EN-->

## The SFT Data Recipe for AI Agents: OpenThoughts-Agent's 100+ Ablations Fully Decoded

> Paper: **OpenThoughts-Agent: Data Recipes for Agentic Models**  
> arXiv: [2606.24855](https://arxiv.org/abs/2606.24855) | June 23, 2026  
> Institutions: UC Berkeley, Stanford, Bespoke Labs, UT Austin, NYU, UCLA, and more  
> Resources: [openthoughts.ai](https://openthoughts.ai)

---

### The Problem

DeepSeek V4 shipped a 50+ page technical report — two paragraphs on training data. Existing open agent training efforts (SWE-Smith, SERA, Nemotron-Terminal) each target a single benchmark. Nobody had published how to train a model that generalizes broadly across diverse agentic tasks.

OpenThoughts-Agent (OT-Agent) answers this directly: a fully open, systematic study of how to curate SFT training data for agents — 100+ controlled ablation experiments, every decision point documented.

---

### Key Numbers

- **6-stage pipeline**, each stage ablated independently
- **95 task generation strategies** compared in Stage 1
- **100K training examples** in the final dataset
- **Qwen3-32B SFT fine-tune**: 44.8% avg across 7 agentic benchmarks
- **+3.9pp over Nemotron-Terminal-32B** (40.9% → 44.8%)
- SWE-Bench Verified: 54.0% | Terminal-Bench 2.0: 26.2%

---

### The 6-Stage Pipeline

**Stage 1 — Sourcing Tasks** (most important): 95 strategies tested. Source choice alone changes SWE-Bench by up to 30pp. Top-4 sources: SWE-Smith (synthetic GitHub issues), StackExchange SuperUser (human Linux tasks), StackExchange-Tezos (human crypto questions), IssueTasks (synthetic).

**Stage 2 — Mixing Tasks**: Top-4 to Top-8 mix beats Top-1. Mixing prevents over-specialization. Top-16 hurts — noisy sources dilute signal.

**Stage 3 — Task Augmentation**: All LLM augmentation strategies (rewriting, adding constraints, hardening) fail to improve the baseline. Keep task descriptions as-is.

**Stage 4 — Filtering Tasks**: LLM-based task filter yields +3pp avg. Use GPT-5 token length as a signal — tasks that require more tokens to solve produce better training data.

**Stage 5 — Teacher Model**: Counter-intuitive finding: **GLM-4.7-AWQ outperforms GPT-5.3-Codex as teacher by ~5% on Terminal-Bench 2.0**. Best benchmark performance ≠ best teacher.

**Stage 6 — Filtering Rollouts**: Filter out traces with fewer than 5 turns. Longer traces = higher quality, confirmed in compute-controlled ablations (not just a compute artifact).

---

### Scaling: Synthetic Is the Only Way Forward

- 10K → 31.6K: strong gains from upsampling
- 31.6K → 100K: **plateau with upsampling alone** — task diversity is the bottleneck
- **Synthetic augmentation breaks the plateau**: expand Tezos from 997 tasks to 21K+ surface forms via instruction rewriting → performance keeps improving at 100K

The lesson: data diversity, not data volume, is the real scaling axis. More rollouts of the same tasks has diminishing returns. More *distinct* task formulations keeps compounding.

---

### Four Counter-Intuitive Findings

1. **Better model ≠ better teacher.** GLM-4.7 (weaker on benchmarks) beats GPT-5.3-Codex as a SFT data generator.
2. **More sources ≠ better.** Top-4 is optimal; Top-16 hurts.
3. **LLM task augmentation doesn't help.** In ablations at 10K scale, all rewriting strategies fail to improve over the original task description.
4. **Synthetic augmentation is the only scaling lever.** Upsampling plateaus; synthetic diversity doesn't.

---

### RL Findings (8B)

Compared 6 RL data sources. Unexpected winner: `pymethods2test` (competitive programming recast as Python contracts). Models trained on it exhibit genuine exploration — trying multiple approaches when early attempts fail. Models trained with LLM-verified data show "compaction" behavior — they give up earlier on hard tasks.

SFT → RL two-stage 8B outperforms single-stage SFT 8B and the strongest ≤8B baselines averaged across all 7 benchmarks.

---

### Why This Paper Matters

Many papers ship a model that's 3.9pp better. Very few papers open-source all 100+ ablation decisions in a format you can actually transfer to your own pipeline. If you're training any kind of agent model, this 6-stage framework and its counter-intuitive findings are directly actionable engineering knowledge.

Paper: [arxiv.org/abs/2606.24855](https://arxiv.org/abs/2606.24855)  
Resources: [openthoughts.ai](https://openthoughts.ai)

© 2026 Author: Mycelium Protocol
