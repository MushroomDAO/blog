---
title: "awesome-rsi：AI 递归自我改进资源精选库——从哥德尔机到 2026 年自我修改 Agent 的完整图谱"
titleEn: "awesome-rsi-recursive-self-improvement-curated-survey-godel-agents-benchmarks"
description: "pinkbubblebubble/awesome-rsi 是一个高信噪比的递归自我改进（RSI）资源精选库，覆盖理论基础、自我修改 Agent、评估基准和安全研究。关键洞察：RSI 比普通迭代更强——系统必须改进那个产生后续改进的机制本身，而不只是修改一次答案。2026 年已有 MOSS、Ouroboros、Red Queen Gödel Machine 等系统达到真正 RSI 级别。"
descriptionEn: "pinkbubblebubble/awesome-rsi is a high-signal curated index of recursive self-improvement (RSI) in AI, covering theoretical foundations, self-modifying agents, evaluation benchmarks, and safety research. Key insight: RSI is stronger than ordinary iteration — the system must improve the mechanism that produces further improvements, not just revise a single answer. In 2026, systems like MOSS, Ouroboros, and Red Queen Gödel Machine have reached genuine RSI-level recursion."
pubDate: "2026-08-18"
updatedDate: "2026-08-18"
category: "Tech-News"
tags: ["RSI", "递归自我改进", "自我修改Agent", "哥德尔机", "AI安全", "Agent进化", "自动化AI研究", "评估基准"]
heroImage: "../../assets/images/awesome-rsi-recursive-self-improvement-curated-survey-godel-agents-benchmarks-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：pinkbubblebubble/awesome-rsi  
定位：递归自我改进（RSI）研究、Agent、框架、基准和安全工作的精选资源库  
最后更新：2026-08-18（与本文同日）

---

「AI 会自我改进吗？」这个问题已经从科幻场景变成了 2026 年 AI 研究的核心工程问题。

但这个问题本身就有陷阱：几乎所有 AI 系统都在「改进」——每次对话都在优化答案，每次 RL 迭代都在调整权重。这些算吗？

awesome-rsi 这个精选库的核心贡献，是给出一个**精确的区分标准**：什么算 RSI，什么只是「普通的迭代」。

---

## 一、核心区分：RSI 比想象中的门槛更高

这个列表开篇就立了一个重要的界定：

> **RSI 比普通迭代更强。** 一个递归系统不只是改进自己——它还必须改进（或反复复用）那个产生后续改进的机制本身。目前大多数系统是有界或部分 RSI，而不是开放式的智能爆炸。

于是列表用三个标签区分：

**RSI（递归自我改进）**：系统改变自身的持久组件，评估该变化，并用同样的或改进后的流程再做一次。改进者本身也在演化的圈子里。

**Self-improvement（自我改进）**：系统持久地改进模型权重、提示词、记忆、工具、技能或脚手架，但改进算子本身保持固定。

**Enabler（使能器）**：自动化研究、优化、评估或安全工作，可以支持 RSI 但本身并不是 RSI。

这个三分法的重要性在于：它把「LLM 在对话里自我批评并修改答案」（不算）和「Agent 编辑了自己的改进逻辑，下一轮用改进后的改进器再来一次」（算）区分开来。

### 纳入标准一览

| 行为 | 纳入？ | 标签 |
|------|--------|------|
| 只修改当前答案，没有可复用状态 | 通常不纳入 | 输出精炼 |
| 生成/过滤/修复数据并用于后续训练 | 是（若循环由系统驱动）| Self-improvement |
| 存储经验并改变后续行为 | 是（若复用可证明）| Self-improvement 或 Enabler |
| 更新提示词/记忆/工具/技能/路由/权限/可执行控制逻辑 | 是 | Self-improvement |
| 改进后续轮次使用的「改进器/评估器/变异策略/脚手架工程师」| 是 | RSI 候选 |
| 优化外部产物而 Agent 本身保持固定 | 在相邻章节 | Enabler |

分析单元是**已部署的 Agent 系统整体**，不只是神经网络权重。模型、数据、提示词、记忆、工具、工作流、脚手架、评估器、环境都是合法的更新面——但改变一个面不自动等于递归改进。

---

## 二、理论基础：从 Good 1965 到 Gödel 机

awesome-rsi 的「基础」章节梳理了 RSI 的思想谱系：

**I. J. Good（1965）**：在《Speculations Concerning the First Ultraintelligent Machine》里第一次提出「智能爆炸」论证——一台足够聪明的机器可以设计出更聪明的机器，然后更聪明的机器设计出再更聪明的……这是现代 RSI 讨论的起点。

**Gödel 机（Schmidhuber, 2003）**：形式化的 RSI 架构——一个搜索证明的 Agent，在能证明自我改写会带来效用增益之后才允许改写任意自身部分。这是「可证明有用的自我改写」的经典设计。

**Stephen Omohundro（2008）**：提出足够强大的目标导向系统会出现的工具性驱动，包括自我改进冲动——RSI 安全讨论的基础文献之一。

**Yudkowsky 和 Yampolskiy** 在 2013-2015 年之间进一步分析了收益、瓶颈和动态特性。

这些基础文献让 awesome-rsi 的收录框架有历史深度，而不只是罗列 2025-2026 年的新论文。

---

## 三、2025-2026 年：真正意义上的 RSI Agent 涌现

这是整个列表最引人注目的部分——近两年出现的多个系统，开始越过「自我改进」门槛，向「递归自我改进」靠近。

### Gödel Agent（ACL 2025）

论文：arxiv.org/abs/2410.04444  
代码：Arvid-pku/Godel_Agent

一个自指的 LLM Agent，**动态修改自己的任务求解逻辑和优化逻辑**，而不是遵循固定的手写优化器。核心突破：Agent 不只改进任务执行，它改进的对象包括「它如何改进自己」这一层。

### Darwin Gödel Machine（2025）

论文：arxiv.org/abs/2505.22954  
代码：jennyzzt/dgm

基于存档的进化循环：修改编程 Agent 代码 → 实证评估变体 → 保留有用的后代 → 复用。Archive 机制让改进不依赖单条进化路径，而是维护一个多样性种群，下一轮的 Agent 代码从「改进后的 Agent 代码库」里产生。

### Gödel Agent → Huxley-Gödel Machine（2026）

论文：arxiv.org/abs/2510.21614  
代码：metauto-ai/HGM

Gödel 机的经验近似实现：一个 Agent 自己开发出它自己的编程 Agent 实现。不依赖形式证明，改用经验评估作为接受门控。

### MOSS（2026）

论文：arxiv.org/abs/2605.22794  
代码：hkgai-official/Moss

一个 Agent **重写自己的 TypeScript 源代码**，重放失败批次，并通过批准和回滚门将容器镜像提升到生产环境。这是目前最接近「工程实践可用的 RSI 系统」的设计——改写代码 + 评估 + 回滚保护 + 再次改写。

### Ouroboros（2026）

论文：arxiv.org/abs/2608.08311  
代码：razzant/ouroboros

经过审核的工具、提示词、上下文组装和核心代码变更，成为后续工作的运行时，并可以调度另一个进化周期。名字来自衔尾蛇符号，寓意不言而喻。

### Red Queen Gödel Machine（2026）

论文：arxiv.org/abs/2606.26294

Agent 和**评估器一起共同进化**——改进标准本身也在循环里。这解决了 RSI 的一个深层问题：如果评估器是固定的，改进者可能只是在优化评估器的盲点，而不是真正在「变好」。红皇后动力学（评估者和被评估者互相追逐）让改进和评估同步演化。

### HyperAgents（2026, Meta FAIR）

论文：arxiv.org/abs/2603.19461  
代码：facebookresearch/HyperAgents

任务 Agent 和元 Agent 角色整合：**Agent 可以修改自己的改进者**。这是在 MOSS/Ouroboros 之外另一条路径——不依赖源代码编辑，而是通过角色整合实现改进者的演化。

---

## 四、自动化 AI 研究：RSI 的近邻

列表中的「Automated AI research」章节收录了一类相关但不完全等同于 RSI 的工作：优化外部产物（训练配方、实验设计、论文复现），而 Agent 自身保持固定。

代表性系统：
- **PostTrainBench**：给 Agent 一个基础模型、一张 H100、十小时，让它自主研究和执行训练策略
- **OpenRSI / OpenMLE / Frontis-MA1**（2026, 清华联合发布）：可执行任务环境 + 学习改进算子 + 长期程序进化 + 保留集迁移评估的全栈 AI4AI 发布

这类工作和 RSI 的边界很微妙：当 Agent 在自动化 AI 研究过程中改进了自己的「研究如何做研究」的能力，它就滑入了 RSI 领域。

---

## 五、评估框架：怎么证明一个系统真的在「自我改进」

awesome-rsi 的评估章节解决一个根本问题：**下游任务得分不足以证明 RSI**——它可能只是在某次 checkpoint 评估时碰巧更好。真正的 RSI 评估需要：

- **跨情节/生成/checkpoint 的变化**，不是单次得分
- **匹配的非改进控照组**，排除训练数据的混淆
- **可复现的执行反馈**，不依赖人工标注

2026 年出现的几个重要评估框架：

**RSIBench-Data**：只开放数据生成策略，固定目标模型、训练栈、评估器和预算。Agent 跨六个下游基准合成数据、训练 checkpoint、检查执行反馈、选最终候选。

**PAST-Bench**：用「持久化开/关」的配对条件，跨顺序新鲜会话任务，把后续增益归因到保存的经验和意图的检索或更新路径。

**EvoAgentBench**：测量从轨迹派生的程序性能力是否能跨 Web 研究、算法推理、软件工程和知识工作的保留集任务迁移。

**SEAGym**：把 Harbor 兼容任务转为训练、冻结验证、保留内/外分布、重放和成本视图，用于评估脚手架更新。

---

## 六、安全、边界与治理

「Safety, limits, and governance」章节是整个列表中最值得重点关注的部分之一。

这里涉及几个关键问题：

**递归改进有界吗？** 当系统在改进自己的改进能力时，什么约束让这个过程不会失控？Schmidhuber 的 Gödel 机答案是「需要形式证明」，但实证近似系统（MOSS、Ouroboros 等）依赖的是「批准门控 + 回滚」——这是否足够？

**评估器和 Agent 共同进化时谁来裁判？** Red Queen Gödel Machine 提出了这个问题但没有完全解决它。

**工具性压力（Instrumental Convergence）**：Omohundro 的分析——任何足够强大的 RSI 系统都会在工具层面出现「抵抗关闭」「获取资源」「保持一致性」等驱动——在真正的 RSI 系统里如何被遏制，是目前研究的空白。

---

## 七、为什么现在是追踪这个领域的关键时刻

2023 年之前，RSI 主要还是理论讨论（Gödel 机的形式框架）加上有限的实验（RLHF 可以算一种有界自我改进）。

2025-2026 年的跃变：Gödel Agent、Darwin Gödel Machine、MOSS、Ouroboros、Red Queen Gödel Machine 在同一年集体出现，意味着**从「讨论 RSI 是否可能」到「测量不同 RSI 设计的性能」**的转变已经发生。

awesome-rsi 作为一个精选库的价值，不只在于收录了哪些论文，更在于它的**纳入标准**——它是目前我找到的对「什么算 RSI」解释最严格、最有可操作性的文档。

如果你在做 Agent 工程、AI 安全研究、或者只是想理解「AI 自我改进」这个词到底在说什么，这个列表是目前最好的单一入口。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## awesome-rsi: The Curated Map of Recursive Self-Improvement — From Gödel Machines to 2026's Self-Modifying Agents

*by Mycelium Protocol*

---

GitHub: pinkbubblebubble/awesome-rsi  
Type: Curated index of RSI research, agents, harnesses, benchmarks, and safety work  
Last reviewed: 2026-08-18

---

"Will AI self-improve?" has shifted from a science fiction question to a live engineering problem. But the question itself contains a trap: almost every AI system "improves" in some sense — every conversation optimizes an answer, every RL iteration adjusts weights. Does that count?

awesome-rsi's central contribution is a **precise discrimination criterion**: what qualifies as RSI, and what is merely ordinary iteration.

---

### The Core Distinction: RSI Has a Higher Bar Than You Think

The list opens with a critical clarification:

> **RSI is stronger than ordinary iteration.** A recursive system must also improve, or repeatedly reuse, the mechanism that produces later improvements. Most current systems are bounded or partial RSI — not open-ended intelligence explosions.

Three labels sort the landscape:

**RSI (Recursive Self-Improvement)**: The system changes a persistent part of itself, evaluates the change, and applies the same or an improved process again. The improver itself is inside the loop.

**Self-improvement**: The system persistently improves model weights, prompts, memory, tools, skills, or scaffolding — but the improvement operator stays fixed.

**Enabler**: Automated research, optimization, evaluation, or safety work that could support RSI but is not itself RSI.

The unit of analysis is the **deployed agent system**, not only its neural weights. Model, data, prompt, memory, tool, workflow, harness, evaluator, and environment are all legitimate update surfaces — but changing a surface is not automatically recursive improvement.

---

### Theoretical Roots: From Good (1965) to Gödel Machines

The foundations section traces the intellectual lineage:

- **I. J. Good (1965)**: The original intelligence explosion argument — a sufficiently smart machine designs a smarter one, which designs an even smarter one...
- **Gödel Machines (Schmidhuber, 2003)**: A proof-searching agent that rewrites any part of itself after proving a utility gain. The canonical formal architecture.
- **Omohundro (2008)**: Instrumental convergence — capable goal-directed systems develop pressures toward self-improvement, resource acquisition, and shutdown resistance.
- **Yudkowsky / Yampolskiy (2013–2015)**: Returns, bottlenecks, and convergence dynamics in recursive improvement.

---

### 2025–2026: Genuine RSI Systems Emerge

This is the most striking part of the list — multiple systems have crossed the threshold from self-improvement into recursive self-improvement in the past two years.

**Gödel Agent (ACL 2025)**: An LLM agent that dynamically modifies its own task-solving and optimization logic. Not just improving task execution — it modifies how it modifies itself.

**Darwin Gödel Machine (2025)**: Archive-based evolution: modify coding-agent code → empirically evaluate variants → keep improved descendants → reuse. The archive maintains a diverse population; next-round agent code is produced from the improved agent codebase.

**Huxley-Gödel Machine (2026)**: An empirical approximation of the Gödel machine — an agent that develops its own coding-agent implementation. Replaces formal proof with empirical evaluation as the acceptance gate.

**MOSS (2026)**: An agent rewrites its TypeScript source, replays failure batches, and promotes container images through an approval-and-rollback gate. The closest current system to a production-ready RSI design.

**Ouroboros (2026)**: Reviewed changes to tools, prompts, context assembly, and core code become the runtime for later work and can schedule another evolution cycle. Named after the snake eating its own tail — intentionally.

**Red Queen Gödel Machine (2026)**: Agents and their evaluators co-evolve — the improvement criterion itself is inside the loop. This addresses RSI's deepest problem: if the evaluator is fixed, the improver may only optimize the evaluator's blind spots.

**HyperAgents (2026, Meta FAIR)**: Task and meta-agent roles integrated so the agent can modify its own improver — not through source code editing, but through role composition.

---

### Evaluation Benchmarks: How to Prove a System Is Actually Improving

A downstream task score does not by itself prove RSI — it may just be a lucky checkpoint. Real RSI evaluation requires:

- Cross-episode / cross-generation / cross-checkpoint change measurements
- Matched non-improving controls to rule out training data confounds
- Executable, reproducible feedback without human labeling at each step

Notable 2026 evaluation frameworks:

**RSIBench-Data**: Opens only the data-generation strategy; holds target model, training stack, evaluator, and budget fixed. Agents synthesize data, train checkpoints, and inspect execution feedback across six downstream benchmarks.

**PAST-Bench**: Persistence-on/off paired conditions to attribute gains to saved experience and its retrieval pathway.

**EvoAgentBench**: Tests whether trace-derived procedural abilities transfer to held-out tasks across web research, algorithmic reasoning, software engineering, and knowledge work.

**SEAGym**: Converts Harbor-compatible tasks into train/frozen-validation/held-out/replay/cost views for evaluating harness updates.

---

### Safety and Limits

The safety section raises questions that current RSI systems have not fully resolved:

**Is recursive improvement bounded?** MOSS and Ouroboros rely on approval gates + rollback. Is that sufficient when the system being gated is the one that generates its own improvements?

**Who judges when evaluators co-evolve?** Red Queen Gödel Machine raises this — doesn't answer it.

**Instrumental convergence**: Omohundro's analysis predicts that sufficiently capable RSI systems will develop drives toward shutdown resistance, resource acquisition, and goal preservation. How these pressures are contained in practical RSI systems is an open research gap.

---

### Why This Matters Right Now

Before 2025, RSI was mostly theoretical (Gödel machine formalisms) with limited experiments (RLHF as bounded self-improvement). The 2025–2026 transition: Gödel Agent, Darwin Gödel Machine, MOSS, Ouroboros, and Red Queen Gödel Machine all appearing within one year marks a shift from "debating whether RSI is possible" to "measuring different RSI designs' performance."

awesome-rsi's value is not just in what it lists, but in its **inclusion criteria** — the most rigorous and operationally precise definition of "what counts as RSI" I've seen documented in one place. If you're doing agent engineering, AI safety research, or just want to understand what "AI self-improvement" actually means in 2026, this is the best single starting point.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
