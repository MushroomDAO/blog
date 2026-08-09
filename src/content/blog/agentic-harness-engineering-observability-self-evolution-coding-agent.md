---
title: "Agentic Harness Engineering：用可观测性让 Coding Agent 自动进化自己的运行时"
titleEn: "agentic-harness-engineering-observability-self-evolution-coding-agent"
description: "复旦+北大+奇迹智风，arXiv:2604.25850，MIT，Python。AHE 提出一个闭环：不动模型权重，只进化 harness——通过三层可观测性（组件/经验/决策），让 Evolve Agent 自动分析 trace、提出修改、预测效果，下一轮自动验证。10次迭代把 GPT-5.4 在 Terminal-Bench 2 上从 69.7% 提升到 77.0%，超过手写 Codex-CLI（71.9%）。冻结后的 harness 迁移到 SWE-bench-Verified，在三个其他模型族获得 +5.1~+10.1pp 跨模型增益。"
descriptionEn: "Fudan+PKU+Qiji Zhifeng, arXiv:2604.25850, MIT, Python. AHE proposes a closed loop that evolves the harness — not the model weights — using three observability pillars (component / experience / decision) to let an Evolve Agent automatically analyze traces, propose edits, predict effects, and be auto-falsified the next round. Ten iterations lift GPT-5.4 from 69.7% to 77.0% on Terminal-Bench 2, surpassing hand-written Codex-CLI (71.9%). The frozen harness transfers to SWE-bench-Verified and delivers +5.1–10.1pp cross-family gains on three alternate model families."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Research"
tags: ["AI", "coding-agent", "harness", "可观测性", "自动进化", "论文", "Terminal-Bench", "Mycelium"]
heroImage: "../../assets/images/agentic-harness-engineering-observability-self-evolution-coding-agent-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Coding agent 的性能竞赛，大多数时候聚焦在模型本身：更大的模型、更好的训练数据、更多的算力。但模型和任务之间有一层很少被讨论的东西——**harness**：系统提示、工具定义、中间件、技能、子 Agent、长期记忆。

这层东西现在主要靠人工设计，而且效果很大程度上决定了模型能发挥出多少。

AHE（Agentic Harness Engineering）提出一个问题：**能不能让 harness 自己进化？**

arXiv: https://arxiv.org/abs/2604.25850 | GitHub: https://github.com/china-qijizhifeng/agentic-harness-engineering | ⭐ 810 | MIT | Python

复旦大学 · 北京大学 · 上海奇迹智风

---

## 核心思路

**不动模型权重，只进化运行时。**

AHE 的做法是：把 harness 拆解成可编辑的文件级组件，让一个「Evolve Agent」分析每次运行的 trace，找出问题，提出修改，并预测修改效果——然后在下一轮自动被结果验证（或推翻）。

这个闭环跑10次，在 Terminal-Bench 2 上把 GPT-5.4 的 pass@1 从 **69.7% 提升到 77.0%**，超过了手工精心设计的 Codex-CLI（71.9%），也超过了现有的自进化基线 ACE 和 TF-GRPO。

---

## 三层可观测性

AHE 把「为什么自动进化会失败」分析成三个核心问题，然后为每个问题设计了一层可观测性：

### 1. 组件可观测性（Component Observability）

**问题**：harness 的哪些部分可以修改？修改边界在哪里？

AHE 使用 **NexAU** 框架，把 harness 分解为 7 个正交的文件级组件：

```
系统提示 / 工具描述 / 工具实现 / 中间件 / 技能 / 子 Agent / 长期记忆
```

每个组件都有独立的文件表示，并通过 git 跟踪。这意味着：
- 动作空间是明确的（只能改这7类）
- 每次修改都可以撤销
- 每次修改的范围都是清晰的

### 2. 经验可观测性（Experience Observability）

**问题**：一次 agent 运行会产生几千万 token 的 trace，有用的信号淹没在噪音里。

**Agent Debugger** 把原始 trace（约 10M token）蒸馏成分层的、带来源索引的报告。Evolve Agent 默认读摘要，需要细节时可以下钻到具体的 rollout。

这解决了「信息太多反而什么都看不到」的问题。

### 3. 决策可观测性（Decision Observability）

**问题**：修改是否有效？为什么有效？如果错了，错在哪里？

Evolve Agent 提出修改时，必须同时声明一个**预测**：「我认为这个改动会让哪些类型的任务通过率提高」。下一轮运行结束后，这个预测会被自动对照真实结果验证——不管是对了还是错了，都会记录下来，成为下次迭代的上下文。

这把每次编辑都变成了一个**可证伪的契约**，而不是黑盒调整。

---

## 实验结果

**主实验（Terminal-Bench 2，GPT-5.4）**：

| 方法 | pass@1 |
|------|--------|
| 初始种子 harness | 69.7% |
| Codex-CLI（手工设计） | 71.9% |
| ACE（自进化基线） | 71.2% |
| TF-GRPO（自进化基线） | 70.8% |
| **AHE（10次迭代）** | **77.0%** |

**Terminal-Bench 2 排行榜（GPT-5.5 + AHE）**：84.7% ± 2.1%，排名第3（2026年5月）。

**跨模型迁移**：冻结 AHE 进化出的 harness，不做任何再进化，直接在3个不同模型族上测试，获得 **+5.1 到 +10.1pp** 的提升。这说明进化出来的 harness 编码的是通用的工程经验，而不是 benchmark 特化的技巧。

**SWE-bench-Verified 迁移**：同一套冻结 harness，在 SWE-bench-Verified 上，以比种子少 12% 的 token 数取得更好的结果。

**消融实验关键结论**：增益主要来自**工具、中间件和长期记忆**，而不是系统提示。这暗示了一个有趣的模式：结构性的 harness 知识（工具实现、数据结构、调用协议）可以迁移，而文字层面的策略指令不行。

---

## 架构：evaluate → analyze → improve

```
┌──────────────────────────────────────────────────┐
│                   AHE 迭代循环                    │
│                                                  │
│  [evaluate]                                      │
│   NexAU 在任务集上跑 coding agent                 │
│   收集原始 trajectory（~10M token/轮）            │
│                     ↓                            │
│  [analyze]                                       │
│   Agent Debugger 蒸馏 trace → 分层报告            │
│   标注失败模式、工具使用异常、记忆访问瓶颈          │
│                     ↓                            │
│  [improve]                                       │
│   Evolve Agent 读报告 → 提出 harness 编辑          │
│   声明预测 → git commit 进组件仓库                 │
│                     ↓                            │
│  回到 evaluate，验证预测，记录结果                  │
└──────────────────────────────────────────────────┘
```

---

## 快速上手

```bash
# 环境要求：Python ≥ 3.13 + uv + tmux
brew install uv tmux   # macOS

git clone https://github.com/china-qijizhifeng/agentic-harness-engineering.git
cd agentic-harness-engineering
uv sync

# 配置环境变量
cp .env.example .env
# 至少需要设置：
# LLM_API_KEY / LLM_BASE_URL  — 主 LLM 接口
# E2B_API_KEY                  — 沙箱执行环境
# SERPER_API_KEY               — evolve_agent 用的 web search
```

E2B 支持 SaaS 版（直接用 API key）或自托管版（Docker）。自托管版对完全离线的实验环境很有用。

---

## 这个工作有趣在哪里

**harness 是现在 coding agent 性能的隐藏变量。** 同一个模型，换一套 harness，分数可以差10个百分点。但 harness 工程到目前为止基本是人工手艺——有经验的工程师一点一点调，没有系统方法。

AHE 把这个过程变成了可以机器驱动的东西，而且用「可证伪的契约」来保证进化不退化成随机试错。

更有意思的是迁移结果：10次迭代在 GPT-5.4 上进化出来的 harness，直接给 GPT-5.5、Claude、Gemini 用，还是有 5-10pp 的增益。这说明 harness 工程和模型工程是两个相对独立的维度——好的 harness 结构是跨模型的。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Agentic Harness Engineering: Automatic Coding-Agent Evolution via Observability

*by Mycelium Protocol*

---

Most coding agent performance research focuses on the model: bigger weights, better training data, more compute. But there's a layer between the model and the task that rarely gets systematic attention — the **harness**: system prompt, tool definitions, middleware, skills, sub-agents, long-term memory.

This layer is currently hand-crafted. And it accounts for double-digit performance swings.

AHE (Agentic Harness Engineering) asks: **can the harness evolve itself?**

arXiv: https://arxiv.org/abs/2604.25850 | GitHub: https://github.com/china-qijizhifeng/agentic-harness-engineering | ⭐ 810 | MIT | Python

Fudan University · Peking University · Shanghai Qiji Zhifeng

---

### The Core Idea

**Freeze the model weights. Evolve the runtime.**

AHE decomposes the harness into editable file-level components, then runs an Evolve Agent that reads distilled traces, proposes edits, declares predictions about what will improve — and gets auto-falsified by the next round's results. Ten iterations of this loop lift GPT-5.4 from **69.7% to 77.0%** pass@1 on Terminal-Bench 2, surpassing hand-designed Codex-CLI (71.9%) and self-evolving baselines ACE and TF-GRPO.

---

### Three Observability Pillars

AHE diagnoses why automated harness evolution fails as three distinct problems, then designs one observability layer for each.

**1. Component Observability**

*Problem*: What parts of the harness can be changed, and what are the boundaries?

AHE uses the **NexAU** framework to decompose the harness into 7 orthogonal file-level components:

```
system prompt / tool descriptions / tool implementations /
middleware / skills / sub-agents / long-term memory
```

Each component has an independent file representation and is git-tracked. The action space is explicit and every edit is revertible.

**2. Experience Observability**

*Problem*: A single agent run produces tens of millions of tokens of raw trajectory. The useful signal is buried.

**Agent Debugger** distills ~10M-token raw traces into layered, source-indexed reports. The Evolve Agent reads digests by default and drills down to raw rollouts when needed. This solves "too much information to see anything."

**3. Decision Observability**

*Problem*: Did an edit work? Why? If it failed, what went wrong?

When the Evolve Agent proposes an edit, it must simultaneously declare a **prediction**: "I expect this change to improve pass rate on tasks of type X." The next iteration auto-verifies that prediction against real outcomes — right or wrong, the result becomes context for the following round.

This turns every edit into a **falsifiable contract** instead of a black-box adjustment.

---

### Results

**Main experiment (Terminal-Bench 2, GPT-5.4)**:

| Method | pass@1 |
|--------|--------|
| Seed harness | 69.7% |
| Codex-CLI (hand-designed) | 71.9% |
| ACE (self-evolving baseline) | 71.2% |
| TF-GRPO (self-evolving baseline) | 70.8% |
| **AHE (10 iterations)** | **77.0%** |

**Terminal-Bench 2 leaderboard (GPT-5.5 + AHE)**: 84.7% ± 2.1%, ranked #3 (May 2026).

**Cross-model transfer**: The frozen AHE-evolved harness, without any re-evolution, delivers **+5.1 to +10.1pp** gains across three alternate model families. The evolved components encode general engineering experience, not benchmark-specific tuning.

**SWE-bench-Verified transfer**: Same frozen harness, better results than the seed at 12% fewer tokens.

**Ablation key finding**: Gains localize to **tools, middleware, and long-term memory** — not the system prompt. Structural harness knowledge (tool implementations, data layouts, call protocols) transfers; prose-level strategy instructions don't.

---

### Architecture

```
┌────────────────────────────────────────────────┐
│              AHE Iteration Loop                │
│                                                │
│  [evaluate]                                    │
│   NexAU runs coding agent on task set          │
│   Collects raw trajectories (~10M tok/round)   │
│                    ↓                           │
│  [analyze]                                     │
│   Agent Debugger distills traces → layered     │
│   reports: failure patterns, tool anomalies,   │
│   memory access bottlenecks                    │
│                    ↓                           │
│  [improve]                                     │
│   Evolve Agent reads reports → proposes edits  │
│   Declares prediction → git-commits to harness │
│                    ↓                           │
│  Back to evaluate — verify prediction, log     │
└────────────────────────────────────────────────┘
```

---

### Quick Start

```bash
# Requires: Python ≥ 3.13 + uv + tmux
brew install uv tmux   # macOS

git clone https://github.com/china-qijizhifeng/agentic-harness-engineering.git
cd agentic-harness-engineering
uv sync

cp .env.example .env
# Minimum required:
# LLM_API_KEY / LLM_BASE_URL  — main LLM endpoint
# E2B_API_KEY                  — sandbox execution
# SERPER_API_KEY               — web search for evolve_agent
```

E2B supports SaaS (direct API key) or self-hosted Docker — the latter is useful for air-gapped experiment environments.

---

### Why This Is Interesting

**Harness is the hidden variable in coding agent performance.** Same model, different harness, and the score can shift by 10 percentage points. But harness engineering has been purely a manual craft — experienced engineers tuning by feel, with no systematic method.

AHE turns this into a machine-drivable process, with falsifiable contracts keeping the evolution from collapsing into random search.

The transfer results are the most interesting part: a harness evolved over 10 iterations on GPT-5.4 delivers 5-10pp gains when handed directly to GPT-5.5, Claude, and Gemini. This suggests that harness engineering and model engineering are two relatively independent dimensions — good harness structure is cross-model.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
