---
title: "JIT-Agent：不再套固定 Prompt，给每个任务动态生成专属 Harness"
titleEn: "JIT-Agent: Stop Hard-Coding Prompts — Dynamically Generate a Task-Specific Harness for Every Request"
description: "bingreeky/JIT 开源项目：给定任务、工具、Skills 和历史 Harness，Agent 即时生成 Memory、Planning、Action、Capability 四模块专属框架，执行过程中 Trace 和反馈可反过来修正 Harness。模型不变，工作方法持续进化。"
descriptionEn: "bingreeky/JIT: given a task plus tools, skills, and historical harnesses, the agent dynamically assembles a four-module framework (Memory, Planning, Action, Capability) tailored to that task. Execution traces and feedback then refine the harness. The model stays fixed; the working method keeps evolving."
pubDate: 2026-09-05
updatedDate: 2026-09-05
category: Tech-Experiment
tags: ["AI", "Agent", "JIT", "Harness", "自进化", "动态生成", "Prompt", "开源", "架构"]
heroImage: "../../assets/images/jit-agent-dynamic-harness-generation-just-in-time-self-evolving-banner.jpg"
author: "Mycelium Protocol"
---

大多数 Agent 框架是静态的：一套固定的系统 Prompt、一套固定的工具调用流程、一套固定的 Memory 结构——不管任务是什么，套同一个框架跑。这在任务类型单一的场景里没问题，但一旦任务多样，框架就成了瓶颈。

**JIT-Agent（Just-In-Time Agent）** 的思路是：不要预定义 Harness，在任务到来的那一刻，**即时生成**一套专属于这个任务的 Agent 框架。

---

## 核心机制：四模块即时组装

JIT-Agent 的输入包含三个来源：
1. **当前任务**：用户的具体请求
2. **可用资源**：工具（Tools）和技能（Skills）的集合
3. **历史 Harness**：过去执行类似任务时积累的框架经验

拿到这三样东西，Agent 即时生成四个模块：

### Memory — 这个任务需要记住什么

不是所有任务都需要长期记忆，也不是所有任务都需要同样的记忆结构。代码调试任务需要记住错误历史和已试过的修复；购物任务需要记住用户偏好和已看过的商品。JIT-Agent 为当前任务动态决定 Memory 的形式和内容。

### Planning — 这个任务应该怎么拆

分解策略因任务而异：需要串行执行的步骤（步骤 B 依赖步骤 A 的结果）和可以并行的步骤（独立的信息收集）应该有不同的计划结构。静态 Prompt 很难同时处理好这两种场景，JIT 为每个任务生成最合适的规划方式。

### Action — 这个任务调用什么工具，按什么顺序

从可用工具和 Skills 中选出这个任务实际需要的子集，决定调用顺序和条件。不相关的工具不会出现在 Harness 里，减少模型选择时的干扰。

### Capability — 这个任务需要什么能力扩展

基于历史 Harness 判断是否需要加载额外的能力模块——比如特定领域的知识、特定格式的输出规则、特定的安全约束。

---

## 执行过程中的 Harness 修正

更关键的设计在执行之后：**Trace 和反馈可以反过来修正 Harness**。

```
任务到来 → 生成 Harness（Memory+Planning+Action+Capability）
    ↓
执行，产生 Trace
    ↓
Trace + 反馈 → 修正 Harness
    ↓
下次类似任务：更好的初始 Harness
```

这个闭环意味着：**模型权重不变，但 Agent 的工作方法在积累经验**。

这跟传统的 Prompt Engineering 有本质区别。手写 Prompt 是静态的，写完就定型了，改进靠人工迭代。JIT-Agent 的 Harness 是动态的，每次执行都是一次学习机会。

---

## 与 Reef 的对比：前端生成 vs 后端学习

昨天我们写过 [Reef](https://blog.mushroom.cv/blog/reef-self-evolving-agent-open-source-infrastructure-human-agent-society/)，也是自进化 Agent 方向。两者定位不同，可以类比：

| 维度 | JIT-Agent | Reef |
|------|-----------|------|
| 核心机制 | 即时生成专属 Harness | 持续学习后端 |
| 作用时机 | 任务到来时（前端） | 执行结束后（后端） |
| 更新对象 | Harness 结构（Memory/Planning/Action/Capability） | 模型权重 + Harness |
| GPU 依赖 | 无（推理即可） | 视配方而定（SkillClaw 无需 GPU） |
| 核心数据 | 当前任务 + 历史 Harness | 用户交互 Trace + 反馈 |

两者不互斥，理论上可以组合：JIT-Agent 在前端生成任务专属框架，Reef 在后端把执行结果转化为下一轮学习数据。

---

## 静态 Harness 的代价

理解 JIT-Agent 价值的最好方式是列出静态 Harness 的已知问题：

**过度通用**：为覆盖所有任务类型，系统 Prompt 往往又长又模糊。长 Prompt 一方面增加 token 成本，另一方面模型在长上下文中容易忽略关键指令。

**工具噪声**：把所有可用工具都列给模型，模型需要在大量不相关选项里找到正确工具，选错率随工具数量增加而上升。

**记忆浪费**：为所有任务维护同一套记忆结构，短任务背负不需要的长期记忆，复杂任务的关键信息可能被无关记忆淹没。

**僵化规划**：固定的规划步骤在任务类型改变时要么过细（浪费步骤）要么过粗（遗漏关键环节）。

JIT 的即时生成针对的就是这四个问题。

---

## 开发者视角：什么时候考虑 JIT-Agent

适合引入 JIT 思路的场景：

- **任务类型高度多样**：同一个 Agent 需要处理完全不同性质的请求（代码、文档、数据分析、对话……）
- **工具库很大**：可用工具超过 20 个，静态全量列举影响选择准确率
- **希望 Agent 随使用积累改进**：不想每次靠人工更新 Prompt，希望执行经验自动沉淀
- **资源约束**：不想为不同任务维护多套静态 Agent，用 JIT 用一套框架覆盖

不适合的场景：**任务类型极其单一且固定**——这种情况下静态优化过的 Prompt 反而比动态生成更快、更可预测。

---

## 延伸思考：Harness 作为一等公民

JIT-Agent 和 Reef 同时出现，让一个趋势更清晰：**Harness 正在成为 AI 工程里的一等公民**。

过去两年，大家关注的是模型本身——哪个模型更强、怎么微调、怎么 RAG。现在越来越多的工程实践在问另一个问题：**给定一个不变的模型，怎么让 Harness 越来越好？**

```
Agent 能力 = 模型能力 × Harness 质量
```

模型能力由基础设施决定，个人和小团队很难影响。但 Harness——Prompt 的结构、Memory 的设计、Skills 的组合、工具的选择方式——是每个团队都可以优化的变量。

JIT-Agent 做的是让 Harness 的生成和优化也自动化。

---

## 相关链接

- GitHub：[bingreeky/JIT](https://github.com/bingreeky/JIT)
- 延伸阅读：[Reef —— 自进化 Agent 的持续学习后端](https://blog.mushroom.cv/blog/reef-self-evolving-agent-open-source-infrastructure-human-agent-society/)

<!--EN-->

Most agent frameworks are static: one fixed system prompt, one fixed tool-calling flow, one fixed memory structure — the same harness regardless of the task. For narrow, single-task systems this is fine, but as task variety increases, the fixed harness becomes the bottleneck.

**JIT-Agent (Just-In-Time Agent)** takes a different approach: instead of pre-defining a harness, at the moment a task arrives, dynamically assemble a harness tailored specifically to that task.

---

## Core Mechanism: Four-Module Just-In-Time Assembly

JIT-Agent takes three inputs:
1. **The current task**: the user's specific request
2. **Available resources**: the pool of tools and skills
3. **Historical harnesses**: framework experience accumulated from similar past tasks

From these three, it generates four modules on the fly:

### Memory — What does this task need to remember?

Not every task needs long-term memory, and not every task needs the same memory structure. Debugging needs a history of errors and attempted fixes; shopping needs user preferences and viewed items. JIT-Agent dynamically decides the form and content of memory for each task.

### Planning — How should this task be decomposed?

Decomposition strategy depends on the task: serial steps (step B depends on step A's output) and parallel steps (independent information gathering) call for different plan structures. Static prompts struggle to handle both well; JIT generates the most appropriate planning approach for each task.

### Action — Which tools, in what order?

From available tools and skills, select the subset actually needed for this task and decide call order and conditions. Irrelevant tools don't appear in the harness, reducing the noise the model has to navigate when choosing.

### Capability — What capability extensions does this task need?

Based on historical harnesses, decide whether to load additional capability modules — domain knowledge, output formatting rules, specific safety constraints. Only what's needed, when it's needed.

---

## In-Execution Harness Refinement

The more critical design comes after execution: **execution traces and feedback can refine the harness**.

```
Task arrives → generate harness (Memory+Planning+Action+Capability)
     ↓
Execute, produce trace
     ↓
Trace + feedback → refine harness
     ↓
Next similar task: better starting harness
```

This loop means: **model weights don't change, but the agent's working method accumulates experience**.

This is fundamentally different from traditional prompt engineering. Hand-written prompts are static — fixed when written, improved only by manual iteration. JIT-Agent's harness is dynamic; every execution is a learning opportunity.

---

## Comparison With Reef: Front-End Generation vs Back-End Learning

We wrote about [Reef](https://blog.mushroom.cv/blog/reef-self-evolving-agent-open-source-infrastructure-human-agent-society/) yesterday, also in the self-evolving agent space. Their roles are different:

| Dimension | JIT-Agent | Reef |
|-----------|-----------|------|
| Core mechanism | Just-in-time harness generation | Continuous learning backend |
| When it acts | Task arrival (front-end) | Post-execution (back-end) |
| Update target | Harness structure (Memory/Planning/Action/Capability) | Model weights + harness |
| GPU required | No (inference only) | Depends on recipe (SkillClaw: no) |
| Core data | Current task + historical harnesses | Interaction traces + feedback |

They're not mutually exclusive. In theory they compose: JIT-Agent generates task-specific frameworks at the front; Reef transforms execution results into learning data at the back.

---

## The Cost of Static Harnesses

The clearest way to understand JIT-Agent's value is to list the known problems with static harnesses:

**Over-generality**: To cover all task types, system prompts tend to be long and vague. Long prompts increase token cost, and models in long contexts are prone to missing key instructions.

**Tool noise**: Giving the model all available tools forces it to find the right one among many irrelevant options. Selection error rate increases with tool count.

**Memory waste**: Maintaining the same memory structure for all tasks burdens simple tasks with unnecessary long-term memory, while complex tasks can have critical information buried under irrelevant context.

**Rigid planning**: Fixed planning steps are either too granular (wasted overhead) or too coarse (missing critical steps) when task types change.

JIT's dynamic generation targets all four of these problems.

---

## Developer Perspective: When to Consider JIT-Agent

Good fit:
- **High task variety**: The same agent handles requests of fundamentally different types (code, documents, data analysis, conversation...)
- **Large tool libraries**: Available tools exceed ~20; static full listing degrades selection accuracy
- **You want the agent to improve with use**: No desire to manually update prompts; execution experience should accumulate automatically
- **Resource constraints**: Don't want to maintain multiple static agents per task type; JIT covers them with one framework

Not a good fit: **extremely narrow, single-type tasks** — in this case, a statically optimized prompt is faster and more predictable than dynamic generation.

---

## A Bigger Pattern: Harness as a First-Class Citizen

JIT-Agent and Reef appearing in the same week makes a trend clearer: **harnesses are becoming first-class citizens in AI engineering**.

For the past two years, attention was on the model itself — which model is stronger, how to fine-tune, how to RAG. More and more engineering practice is now asking a different question: **given a fixed model, how do we make the harness progressively better?**

```
Agent capability = Model capability × Harness quality
```

Model capability is determined by infrastructure — hard for individuals and small teams to influence. But the harness — prompt structure, memory design, skill composition, tool selection logic — is a variable every team can optimize.

JIT-Agent automates the generation and optimization of that harness.

---

## Links

- GitHub: [bingreeky/JIT](https://github.com/bingreeky/JIT)
- Related: [Reef — Continuous Learning Backend for Self-Evolving Agents](https://blog.mushroom.cv/blog/reef-self-evolving-agent-open-source-infrastructure-human-agent-society/)
