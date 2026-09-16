---
title: "后训练自动化：AIBuildAI 用元搜索在 PostTrainBench 拿第一，46.6 分超过所有 Agent"
titleEn: "Autonomous LLM Post-Training: AIBuildAI's Meta Search Tops PostTrainBench at 46.6, Beating Every Agent"
description: 'AIBuildAI LLM-Post-Train Agent，Apache 2.0 开源，7 stars，Python。核心是「元搜索」：元 Agent 读取任务后自己写搜索程序，而不是走固定拓扑。四个知识库（104 种后训练方法、215 个数据集、108 个框架、34 张工作流卡）通过 MCP 接口查询。在 PostTrainBench 七个任务+四个基座模型上得分 46.6，超过 Locus(45.6)、Claude Code Fable 5(41.8)，只有官方 instruct 模型(51.1)在前面。'
descriptionEn: "AIBuildAI LLM-Post-Train Agent, Apache 2.0, Python. Core is meta search: a meta agent reads each task and writes the search program, instead of committing to a fixed topology. Knowledge base of 104 post-training methods, 215 datasets, 108 frameworks, 34 workflow cards served via MCP. Scores 46.6 on PostTrainBench (7 tasks, 4 base models), beating Locus (45.6) and Claude Code Fable 5 (41.8). Only official instruct models (51.1) score higher."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Research"
tags: ["LLM", "post-training", "SFT", "RLHF", "DPO", "GRPO", "autonomous-training", "meta-search", "PostTrainBench", "open-source"]
heroImage: "../../assets/images/aibuildai-llm-posttrain-agent-autonomous-meta-search-posttrainbench-banner.jpg"
---

> 📌 开源仓库：https://github.com/aibuildai-inc/aibuildai-llm-posttrain-agent
> 技术报告：github.com/aibuildai-inc/aibuildai-llm-posttrain-agent/blob/main/docs/aibuildai-llm-post-train-agent.pdf
> License：Apache 2.0 | Stars：7 | Language：Python | 联系：pengtao.xie@aibuildai.io

---

## 后训练为什么难？

预训练好的语言模型不能直接用。Post-training（后训练）是让模型能听指令、能推理、会拒绝有害请求的那个阶段，它决定了模型在实际使用中是否有用。

但后训练的流水线设计成本高、门槛高。主要原因是**决策之间强耦合**：

- 用哪个偏好对齐算法（SFT → DPO / GRPO / PPO），取决于数据混合比
- 数据混合比，取决于基座模型的特点
- 学习率调度，取决于算法选择
- 任何一个错，要从头重跑——H100 上一次完整训练就要花几小时

PostTrainBench 把这个问题形式化成了一个基准测试：给定基座模型 + 目标能力，Agent 必须在十小时预算内自主完成整个后训练流水线，结果由基准自己的隐藏测试集评分。

---

## AIBuildAI 的方案：元搜索（Meta Search）

以往的思路是把 Claude Code 或 Codex 这类通用编程 Agent 对准任务跑。这能出结果，但有一个根本限制：**Agent 在早期就提交了一个方案，后续所有决策都沿着这条线走，一旦卡住只会在同一条线上优化，不会放弃再换一个方向。**

AIBuildAI 的核心贡献是**元搜索**——让搜索拓扑本身成为 Agent 的输出。

**传统树搜索**（每个节点是一次完整训练实验）：
- 所有任务走同一种树形结构
- 无法表达「多阶段课程」「基于奖励模型的在线 RL」「多模型投票」等结构
- 数据生成阶段与训练阶段捆在一起，不能复用前缀

**元搜索**：
- 元 Agent 先读任务、查知识库，然后**写一个搜索程序**
- 搜索程序由三种原语组成：`Agent`（带工具的 LLM 会话）、`Program`（确定性计算）、`Search`（组合编排）
- 可以生成 DAG、锦标赛、多路融合、迭代循环——不限于树
- 支持「运行时重规划」：一阶段结束后，剩余预算和上一阶段结果交给新的元 Agent，它根据实测结果决定下一阶段的结构

每次运行的拓扑都是任务专属的，而不是固定预设。

---

## 知识系统：四个语料库通过 MCP 检索

元 Agent 和实验 Agent 在做设计决策时，都能查询一个远程检索服务（Kb），通过 MCP 接口访问，按语义嵌入检索。

**四个子语料库**：

| 类别 | 规模 | 内容 |
|------|------|------|
| 工作流（Workflow） | 1 个技能文档，34 张参考卡 | 后训练流程的 13 个顺序研究步骤，每步说明要做的判断、可选方向、不可迁移的情况 |
| 方法论（Methodology） | 104 张方法卡，30 个有代码实现 | 每张卡含原始论文、数学推导、数值样例、各库默认参数、理论与实际成本、训练信号监控 |
| 数据集（Dataset） | 215 张数据集卡，13 个推荐，34 个须隔离 | 每张卡含许可证、列定义、版本锁定加载代码、真实样本行、采纳证据、筛查记录 |
| 框架（Framework） | 108 张库卡，16 个推荐 | 何时选这个库、如何启动训练、监控什么指标、如何保存可被加载的结果 |

每张技能文档同时记录「什么在什么条件下有效」和「什么在什么条件下失败」，Agent 可以从正负两个方向检索。

---

## PostTrainBench 结果

**七个任务**：AIME 2025（竞赛数学）、GSM8K（数学）、ArenaHard Writing（创意写作）、GPQA Main（问答）、HealthBench（医疗建议）、HumanEval（代码生成）、BFCL（函数调用）

**四个基座模型**：Qwen3-1.7B-Base、Qwen3-4B-Base、SmolLM3-3B-Base、gemma-3-4b-pt

**每次运行**：单张 H100 GPU，10 小时上限，全自主，无人工介入，所有 Agent 角色跑在 Claude Opus 5 上

| 方法 | AIME | ArenaHard | BFCL | GPQA | GSM8K | HealthBench | HumanEval | 总分 |
|------|------|-----------|------|------|-------|-------------|-----------|------|
| **AIBuildAI（本文）** | **15.8** | 65.5 | **95.8** | 31.4 | 82.3 | 42.6 | **69.0** | **46.6** |
| Locus (Opus 5) | 9.4 | **66.3** | 94.3 | **33.1** | 82.9 | **44.3** | 66.6 | 45.6 |
| Claude Code (Fable 5) | 13.3 | 61.5 | 73.0 | 28.3 | **83.5** | 40.1 | 58.4 | 41.8 |
| Claude Code (Opus 5) | 9.2 | 53.4 | 1.5 | 31.4 | 80.3 | 38.7 | 59.8 | 35.0 |
| Official instruct（参考基线） | 29.2 | 70.2 | 85.0 | 36.2 | 87.0 | 43.3 | 71.5 | 51.1 |

*每格为四个基座模型的平均值；加粗为 Agent 类最高*

**三个领先任务的原因分析**（来自报告）：

**BFCL（函数调用，95.8）**：任务核心是让模型输出符合 schema 的函数调用格式，是一个「输出契约」问题——学会了契约就接近满分，学不会就接近零分。元搜索能精准定位并针对这个契约设计流水线，而通用 Agent 容易绕开这一步。

**HumanEval（代码生成，69.0）**：在全部四个基座模型上都领先。代码任务有明确的自动化验收标准（单元测试通过率），奖励信号清晰，适合迭代优化。

**AIME 2025（竞赛数学，15.8）**：数学推理对格式要求严格（整数输出），且 SFT + GRPO 的叠加策略在小模型上效果差异很大。元搜索能根据中间结果调整策略，而固定拓扑在早期做了错误决策后难以纠正。

**唯一在前面的是 Official instruct（51.1）**——这是各模型官方开发团队发布的指令微调版本，属于「参考基线」而非竞争 Agent，使用的算力和时间预算不受约束。

---

## 和竞争方案的核心区别

**Locus**（外部提交，Intology，也跑在 Opus 5）：总分 45.6，在 ArenaHard、GPQA、HealthBench 三个任务上领先。根据报告描述，Locus 是目前外部提交中最强的单一 Agent 方案。AIBuildAI 在这三个任务上与它的差距都在 2 分以内。

**Claude Code + Fable 5**（41.8）：Claude Code 在 BFCL 上出现了 73.0 ± 28.0 的高标准差，说明在函数调用任务上不稳定。这与前文的分析一致——Claude Code 是通用代码 Agent，不针对后训练知识设计。

**Claude Code + Opus 5**（35.0）：BFCL 只有 1.5 分，是明显的格式输出失败——说明同一模型（Opus 5）在不同架构下差距巨大。知识系统 + 元搜索的组合在这里发挥了关键作用。

---

## 技术细节：三个用树搜索无法表达的场景

报告明确列举了为什么树搜索不够，这三个场景展示了元搜索的必要性：

**1. 数据生成阶段**
树节点必须是已训练并评分的 pipeline，但数据语料只有在模型训练完成后才能评分。要比较 k 种数据生成方案，树搜索必须跑 k 次完整训练。元搜索可以把数据生成作为独立阶段，用廉价的代理指标（验证器通过率、去重率）筛选语料，再把好的语料传入训练阶段。

**2. 多阶段课程学习**
SFT → 偏好对齐 → 拒绝采样微调（Rejection Fine-Tuning）的顺序未知。树搜索每个候选都要从头训练共享前缀。元搜索可以缓存前缀，只搜索后续阶段。

**3. 在线强化学习**
奖励模型和策略模型需要在一次连续训练中交替更新（策略更新 → 奖励模型重拟合 → 继续训练）。树搜索只能在训练完成后评分，无法在训练中介入。元搜索可以把这表达成一个迭代循环。

---

## 产品定位与局限

AIBuildAI 的市场定位是：**帮企业把专有数据转化为高性能定制 LLM，降低人力、时间和试错成本。**

从技术报告来看，当前系统的实际限制：

- 需要 Linux x86_64 + systemd + cgroup-v2，不能跑在 macOS 上
- 每次运行需要单张 H100（十小时预算），硬件成本不低
- 所有 Agent 运行在 Claude Opus 5 上，API 成本叠加在训练成本上
- 仓库刚开放（2026-09-16），Stars 只有 7，代码成熟度待验证
- PostTrainBench 上的结果是「当前快照」，报告明确说系统仍在开发中

技术路线本身是清晰的：元搜索 + 领域知识库 + 自动化实验 = 比通用 Agent 更高效的后训练探索。这与「人意图 + Agent 执行」的当前 AI 工程方向高度一致。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/aibuildai-inc/aibuildai-llm-posttrain-agent
> Technical report: github.com/aibuildai-inc/aibuildai-llm-posttrain-agent/blob/main/docs/aibuildai-llm-post-train-agent.pdf
> License: Apache 2.0 | Stars: 7 | Contact: pengtao.xie@aibuildai.io

---

## Why Is Post-Training Hard?

A pretrained language model isn't ready to use. Post-training is the stage that makes a model follow instructions, reason about its outputs, and decline harmful requests — it determines whether a model is actually useful in practice.

But designing post-training pipelines is expensive and expertise-intensive. The core reason: **decisions are tightly coupled**.

- Which preference alignment algorithm to use (SFT → DPO / GRPO / PPO) depends on the data mixture
- The effective data mixture depends on the base model's characteristics
- The learning rate schedule depends on the algorithm choice
- Any mistake means a full rerun — one complete training run on an H100 takes hours

PostTrainBench formalizes this as a benchmark: given a base model and a target capability, an agent must autonomously complete the entire post-training pipeline within a ten-hour budget, scored by the benchmark's own held-out evaluation.

---

## AIBuildAI's Approach: Meta Search

The prior approach was to point a general coding agent (Claude Code, Codex) at the task and let it run. This produces results, but has a fundamental limitation: **the agent commits to one approach early and every subsequent decision is conditioned on its existing trajectory — when it stalls, it refines the same line rather than abandoning it for something different.**

AIBuildAI's core contribution is **meta search**: making the search topology itself the output of an agent.

**Traditional tree search** (each node is one complete training experiment):
- Every task goes through the same tree structure
- Cannot express multi-stage curricula, online RL against a learned reward model, multi-model voting
- Data generation and training are bundled — no prefix caching

**Meta search**:
- A meta agent reads the task, consults the knowledge base, then **writes a search program**
- The program is composed from three primitives: `Agent` (LLM session with tools), `Program` (deterministic computation), `Search` (composite orchestration)
- Can generate DAGs, tournaments, fan-ins, iterative loops — not just trees
- Supports "runtime replanning": at each stage boundary, the remaining budget and stage results are handed to a new meta agent, which decides the next stage's structure based on measured outcomes

Each run's topology is task-specific rather than fixed in advance.

---

## Knowledge System: Four Corpora via MCP

Both the meta agent and experimenter agents query a remote retrieval service (Kb) via MCP, using semantic embedding search when making design decisions.

| Corpus | Scale | Coverage |
|--------|-------|----------|
| Workflow | 1 skill doc, 34 reference cards | 13 ordered research actions per run, each explaining the judgment it settles, options available, and non-transferable cases |
| Methodology | 104 method cards, 30 with code | Defining paper, math, numerical example, per-library defaults, theory/practice cost, signals to watch during training |
| Dataset | 215 cards, 13 recommended, 34 held-out | License, column definitions, version-pinned load line, real sample row, adoption evidence, screening record |
| Framework | 108 library cards, 16 recommended | When to pick, how to start, what to monitor, how to save a loadable result |

Each skill document records both what works under what conditions, and what fails and why — both positive and negative evidence are available.

---

## PostTrainBench Results

**Seven tasks**: AIME 2025 (competition math), GSM8K (math), ArenaHard Writing (creative writing), GPQA Main (QA), HealthBench (health advice), HumanEval (code generation), BFCL (function calling)

**Four base models**: Qwen3-1.7B-Base, Qwen3-4B-Base, SmolLM3-3B-Base, gemma-3-4b-pt

**Each run**: Single H100 GPU, 10-hour budget, fully autonomous, no human intervention; all agent roles running on Claude Opus 5

| Method | AIME | ArenaHard | BFCL | GPQA | GSM8K | HealthBench | HumanEval | Overall |
|--------|------|-----------|------|------|-------|-------------|-----------|---------|
| **AIBuildAI (ours)** | **15.8** | 65.5 | **95.8** | 31.4 | 82.3 | 42.6 | **69.0** | **46.6** |
| Locus (Opus 5) | 9.4 | **66.3** | 94.3 | **33.1** | 82.9 | **44.3** | 66.6 | 45.6 |
| Claude Code (Fable 5) | 13.3 | 61.5 | 73.0 | 28.3 | **83.5** | 40.1 | 58.4 | 41.8 |
| Claude Code (Opus 5) | 9.2 | 53.4 | 1.5 | 31.4 | 80.3 | 38.7 | 59.8 | 35.0 |
| Official instruct (reference) | 29.2 | 70.2 | 85.0 | 36.2 | 87.0 | 43.3 | 71.5 | 51.1 |

*Each cell is the average across four base models; bold = highest agent score*

**Analysis of three leading tasks**:

**BFCL (function calling, 95.8)**: The task is gated by a single output contract — the emitted call must parse and match the expected schema. Learn the contract, score high; miss it, score near zero. Meta search can precisely design a pipeline for this contract.

**HumanEval (code generation, 69.0)**: Leads on all four base models. Code tasks have clear automated acceptance criteria (test pass rates), providing clean reward signals that reward iterative optimization.

**AIME 2025 (competition math, 15.8)**: Math reasoning requires strict output formatting (integer answers), and the SFT + GRPO stacking strategy varies dramatically across small models. Meta search can adjust strategy based on intermediate results; fixed topologies can't course-correct after early wrong decisions.

---

## Core Technical Differences

**Locus** (external submission by Intology, also runs on Opus 5): 45.6 overall, leads on ArenaHard, GPQA, HealthBench. The current strongest single-agent external submission. AIBuildAI trails by less than 2 points on each of those three tasks.

**Claude Code + Fable 5** (41.8): High variance on BFCL (73.0 ± 28.0 std dev), indicating inconsistent handling of function-calling format — Claude Code is a general coding agent, not designed around post-training domain knowledge.

**Claude Code + Opus 5** (35.0): BFCL score of 1.5 — a near-complete formatting failure. The same underlying model (Opus 5) produces dramatically different results depending on the surrounding architecture.

---

## Current Limitations

- Requires Linux x86_64 + systemd + cgroup-v2 — no macOS support
- Needs a single H100 per run (10-hour budget) — hardware costs are real
- All agents run on Claude Opus 5 — API costs stack on top of training costs
- Repository just opened (2026-09-16), 7 stars — production maturity is unknown
- PostTrainBench results are described as a "snapshot of a system still under construction"

The technical direction is clear: meta search + domain knowledge base + automated experimentation = more efficient post-training exploration than general-purpose agents. This aligns directly with the "human intent + agent execution" pattern that defines current AI engineering practice.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
