---
title: "长视野 Agent 综述：人大团队用两大支柱重新定义 AI Agent 的演化路线图"
titleEn: "A Survey of Long-Horizon Agents: RUC's Two-Pillar Roadmap for How AI Agents Evolve"
description: "RUC-NLPIR 发布 Awesome-Long-Horizon-Agents，配套综述「Towards Long-Horizon Agents: A Survey」。核心框架：Agent = 基础策略 + Harness，两大支柱（外化 Harness 工程 + 内化模型优化）、三层任务难度（H1/H2/H3）、三阶段演化史（Prompt→Context→Runtime）。873 stars，MIT 开源。"
descriptionEn: "RUC-NLPIR releases Awesome-Long-Horizon-Agents with the survey 'Towards Long-Horizon Agents.' Core framework: Agent = base policy + Harness, organized around two pillars (externalized harness engineering + internalized model optimization), three horizon levels (H1/H2/H3), and three evolutionary stages (Prompt → Context → Runtime). 873 stars, MIT."
pubDate: "2026-08-04"
updatedDate: "2026-08-04"
category: "Tech-News"
tags: ["长视野Agent", "综述", "Harness工程", "强化学习", "人民大学", "开源论文列表", "AI研究", "Mycelium"]
heroImage: "../../assets/images/awesome-long-horizon-agents-ruc-nlpir-survey-harness-optimization-banner.jpg"
---

*by Mycelium Protocol*

---

AI Agent 的「时间视野」（time horizon）——它能独立完成任务的时长——正在指数级增长，每隔几个月翻倍。从单轮问答到数分钟的代码调试，到数小时的研究任务，再到跨会话的长期项目……这个边界在快速向外延伸。

**[Awesome-Long-Horizon-Agents](https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents)**（RUC-NLPIR，中国人民大学）是配套综述 [Towards Long-Horizon Agents: A Survey](https://openreview.net/pdf?id=HyhfhlbWGh) 的论文列表，873 stars，MIT 开源。

这不只是一个论文收集仓库——它提出了一套用于理解「长视野 Agent」的系统性框架。

---

## 核心定义：Agent = 策略 + Harness

综述给出一个形式化定义：

```
Agent = π_θ ⊕ H
```

其中 `π_θ` 是基础语言模型策略，`H` 是围绕它的 **Harness**（硬件/软件基础设施：循环、记忆、工具、编排……）。

这个定义把「长视野 Agent 研究」拆成了两条互补的路线：

- **外化路线**：通过工程手段在 Harness 层实现长视野能力
- **内化路线**：通过训练把这些能力压进模型策略本身

两条路线通过经验和反馈**共同演化**：今天在 Harness 里显式实现的能力，明天可能被内化进模型；更强的模型反过来让 Harness 能做更复杂的事。

---

## 三层任务难度

「长视野」不是一个二值概念，综述把它分成三个嵌套层级：

| 层级 | 任务时间跨度 | 要求的能力 |
|------|------------|-----------|
| **H1** | 单上下文窗口内（分钟级） | C1：上下文内交互推理 |
| **H2** | 跨上下文/跨会话（小时-天） | C2：跨上下文状态与记忆管理 |
| **H3** | 跨任务开放流（无限期） | C3：跨任务经验积累与复用 |

METR 用「在固定成功率下能完成的任务时长」来量化 Agent 能力——这个指标把「长视野 Agency」和「长时间运行」、「自主性」区分开来，给出了一个可测量的标尺。

---

## 两大支柱

### Pillar I：Harnesses（外化长视野能力）

Harness 有六个核心组件：

**1. Loops and Workflows（循环与工作流）**

三种形态：
- **线性**：ReAct、Reflexion、Self-Refine——感知→推理→行动的迭代循环
- **计划-执行**：Plan-and-Solve、ReWOO——先规划再执行，减少中间干扰
- **分支**：Tree of Thoughts、LATS、Graph of Thoughts——搜索树探索多路径

**2. Context and Memory（上下文与记忆）**

两类：
- **工作记忆**（丢弃/压缩/选择）：HiAgent、MEM1、MemAgent——如何在有限上下文窗口里保留关键信息
- **持久记忆**（事实/经验）：Mem0、HippoRAG、Voyager——跨会话的长期记忆系统

**3. Tools, MCP, and Skills（工具、MCP 与技能）**

从 Toolformer 到 Model Context Protocol（MCP）——标准化的工具接口让 Agent 能调用外部能力，技能库让经验可复用。

**4. Orchestration（编排）**

多 Agent 协调：MetaGPT、AutoGen、Magentic-One——把复杂任务分配给专业子 Agent 并协调结果。

**5. Hooks and Middleware（钩子与中间件）**

动作前授权、执行边界安全（AgentBound）、步骤级数据中间件（Claw-R1）——让 Agent 的每一步都可审计、可控制。

**6. Verification（验证）**

程序化验证器、执行反馈——让 Agent 能判断自己的输出是否正确，驱动下一轮迭代。

---

### Pillar II：Optimization（内化长视野能力）

七个子方向：

| 子方向 | 代表工作 |
|--------|---------|
| **架构基础** | FlashAttention、长上下文架构 |
| **数据与环境合成** | 可执行任务环境、轨迹生成 |
| **预训练/中训练** | 长视野感知的预训练目标 |
| **微调** | 指令遵循、轨迹监督 |
| **Agent 强化学习** | 执行反馈奖励、在线 RL |
| **在线蒸馏** | 从强模型到弱模型的策略蒸馏 |
| **自进化** | Darwin Gödel Machine、ReasoningBank |

---

## 三阶段演化史

综述把 Agent 研究的演化分成三个阶段，每阶段都扩大了「能放进一次调用里的信息密度」：

**Stage I — Prompt Engineering（2020-2023）**

CoT、Zero-Shot CoT、Self-Consistency、ReAct、ToT——这一阶段的核心是「怎么写 prompt 让模型更好地推理」。

**Stage II — Context Engineering（2023-2025）**

RAG、Toolformer、ToolLLM、MemGPT、Generative Agents——这一阶段把记忆、工具、长上下文都带进了模型的上下文空间里。

**Stage III — Runtime Harnesses（2025-至今）**

OpenHands、SWE-agent、MCP、Darwin Gödel Machine——这一阶段的核心是「整条轨迹」：一个运行时基础设施持续地推进任务，跨越多次调用甚至多个会话。

---

## 应用领域

综述覆盖五个主要应用方向：

- **软件工程**：SWE-bench 系列、代码 Agent（OpenHands、SWE-agent、Claude Code）
- **信息检索**：Deep Research 类系统，搜索+综合+迭代
- **计算机操作**：GUI Agent、Computer Use
- **多模态 Agent**：UI-TARS 系列、视觉-语言 Agent
- **通用 Agent**：跨任务、跨域的广谱 Agent

---

## 为什么值得关注

**框架本身的价值超过论文列表。** Agent = π_θ ⊕ H 这个定义给了研究者一个清晰的坐标系：每项工作都可以问「它是在改进 Harness（外化）还是改进模型策略（内化）？」「它解决的是 H1、H2 还是 H3 问题？」有了这套语言，不同路线的工作就能被比较和定位。

三阶段演化史也是一个重要的历史叙事：从 prompt 工程，到上下文工程，再到运行时工程——每一步都是在把「隐式能力」变成「可工程化的模块」。按这个逻辑推断，下一步是把 Harness 里的能力内化进模型，形成新的循环。

873 stars，MIT 开源，正在持续更新（最近更新 2026-08-04）。

仓库：[github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents](https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents) · 综述论文：[OpenReview HyhfhlbWGh](https://openreview.net/pdf?id=HyhfhlbWGh)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Long-Horizon Agents Survey: RUC Team Proposes a Two-Pillar Roadmap for AI Agent Evolution

*by Mycelium Protocol*

The "time horizon" of AI agents — the duration of tasks they can complete unaided — is growing exponentially, roughly doubling every few months. From single-turn Q&A to minutes-long debugging, to hours-long research tasks, to open-ended cross-session projects — that boundary is moving fast.

**[Awesome-Long-Horizon-Agents](https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents)** (RUC-NLPIR, Renmin University of China) is the paper list accompanying the survey [Towards Long-Horizon Agents: A Survey](https://openreview.net/pdf?id=HyhfhlbWGh). 873 stars, MIT license.

This isn't just a paper collection. It proposes a systematic framework for understanding long-horizon agents.

### Core Definition: Agent = Policy + Harness

The survey formalizes:

```
Agent = π_θ ⊕ H
```

Where `π_θ` is the base language model policy and `H` is the surrounding **harness** (loops, memory, tools, orchestration...). This splits long-horizon agent research into two complementary routes:

- **Externalization**: implementing long-horizon capability in the harness layer through engineering
- **Internalization**: compressing these capabilities into the model policy through training

The two routes **co-evolve** through experience and feedback: capabilities implemented explicitly in the harness today may be internalized into the model tomorrow; stronger models in turn enable more capable harnesses.

### Three Horizon Levels

"Long horizon" isn't binary. The survey defines three nested levels:

| Level | Task duration | Required capability |
|-------|--------------|---------------------|
| **H1** | Intra-context, one window (minutes) | C1: Intra-context interactive reasoning |
| **H2** | Cross-context, across windows/sessions (hours–days) | C2: Cross-context state and memory |
| **H3** | Cross-task, open-ended stream | C3: Cross-task experience accumulation |

METR measures this as the task length an agent can complete at a fixed success rate — a concrete empirical yardstick that distinguishes long-horizon agency from long-running execution or autonomy.

### Two Pillars

**Pillar I: Harnesses (Externalizing Long-Horizon Capability)**

Six components:

1. **Loops and Workflows**: linear (ReAct, Reflexion), plan-execute (ReWOO), branching (Tree of Thoughts, LATS)
2. **Context and Memory**: working memory (compress/select/discard) + persistent memory (factual/experiential)
3. **Tools, MCP, and Skills**: Toolformer → Model Context Protocol → skill libraries
4. **Orchestration**: multi-agent coordination (MetaGPT, AutoGen, Magentic-One)
5. **Hooks and Middleware**: pre-action authorization, execution boundaries, step-level data pipelines
6. **Verification**: programmatic verifiers, execution feedback for iterative refinement

**Pillar II: Optimization (Internalizing Long-Horizon Capability)**

Seven directions: Architectural Substrate → Data and Environment Synthesis → Pre-/Mid-Training → Fine-tuning → Agentic RL → On-Policy Distillation → Self-Evolution.

### Three-Stage Evolution

The survey traces three stages, each expanding the information density per LLM call:

**Stage I — Prompt Engineering (2020–2023)**: CoT, ReAct, Tree of Thoughts — "how to write a prompt for better reasoning."

**Stage II — Context Engineering (2023–2025)**: RAG, Toolformer, MemGPT — bringing memory, tools, and long context into the model's context space.

**Stage III — Runtime Harnesses (2025–present)**: OpenHands, SWE-agent, MCP, Darwin Gödel Machine — a sustained runtime infrastructure that advances a task across many calls and sessions.

### Why This Matters

**The framework is worth more than the paper list.** Agent = π_θ ⊕ H gives researchers a coordinate system: every piece of work can be asked "does it improve the Harness (external) or the model policy (internal)? Does it address H1, H2, or H3?" This vocabulary makes it possible to compare and position work across very different research lines.

The three-stage history is also a useful narrative: from prompt engineering to context engineering to runtime engineering — each step turns an implicit capability into an engineerable module. The logical next step is internalizing harness capabilities back into the model, creating a new cycle.

873 stars, MIT, actively updated (last update 2026-08-04).

Repository: [github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents](https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents) · Survey: [OpenReview HyhfhlbWGh](https://openreview.net/pdf?id=HyhfhlbWGh)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
