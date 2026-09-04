---
title: "Reef：自进化 Agent 的开源工程基础设施，把「用户交互」变成下一轮学习数据"
titleEn: "Reef: Open-Source Infrastructure for Self-Evolving Agents That Turn User Interactions Into Training Data"
description: "MIT、NUS 等机构的 Human-Agent-Society 团队开源 Reef。它的核心判断：真实用户交互可以成为下一轮学习数据。Reef 提供四环学习闭环（Serve→Observe→Grow→Commit），支持模型权重和 Agent Harness 两类更新对象，SkillClaw 配方无需 GPU 即可运行。"
descriptionEn: "Human-Agent-Society team (MIT, NUS) open-sources Reef. Core insight: real user interactions can become training data for the next learning cycle. Reef provides a four-stage loop (Serve→Observe→Grow→Commit), supports both model weight and agent harness updates, and SkillClaw recipe runs without a GPU."
pubDate: 2026-09-04
updatedDate: 2026-09-04
category: Research
tags: ["AI", "Agent", "自进化", "开源", "强化学习", "Self-Improving", "Harness", "持续学习", "MIT", "NUS"]
heroImage: "../../assets/images/reef-self-evolving-agent-open-source-infrastructure-human-agent-society-banner.jpg"
author: "Mycelium Protocol"
---

自进化 Agent 是当前 AI 工程里最热也最难落地的方向之一。热，是因为"让模型自己变强"的叙事吸引人；难，是因为从一个想法到真正跑起来的闭环中间有太多没解决的工程问题：谁产生训练数据？哪些数据够格？候选版本怎么评估？更新怎么上线而不崩掉生产？

MIT、NUS 等机构的 Human-Agent-Society 团队用 Reef 给出了一套具体答案。

---

## 核心判断：用户交互就是训练数据

Reef 的出发点不是"让模型自己训练自己"，而是一个更务实的观察：

> **真实用户交互可以成为下一轮学习数据。**

每一条 Agent 请求、每一段执行轨迹（trajectory）、每一个执行结果和用户反馈，都可以被结构化地沉淀为 **Experience**。学习配方（Recipe）读取这些 Experience，生成对模型权重、Prompt、Memory、Skills、Tools 或 Orchestration 的更新。

这个判断的重要性在于：**它把数据采集问题从"如何构造合成数据"变成了"如何利用已经发生的事情"**。不需要额外标注，不需要专门的数据生产流水线——Agent 在服务用户的过程中自然产生训练素材。

---

## 四环学习闭环

Reef 把整个自进化过程分成四个环节，首尾相连：

### Serve — 接收请求，记录交互

Agent 通过 HTTP 推理接口提供服务。每次服务返回一个 **agent record id**，记录完整的交互过程：输入、轨迹、输出。

### Observe — 匹配反馈，判断学习资格

客户端通过反馈接口提交 score、feedback 和对应的 record id。Observe 环节将交互记录与用户反馈匹配，判断哪些数据**具备学习资格**——并非所有交互都值得学习，低质量、无明确反馈的记录会被过滤掉。

### Grow — 运行学习配方，生成候选更新

通过资格筛选的记录进入 Grow 环节。学习配方在这里运行，生成**候选更新**：可能是新的模型权重，也可能是 Prompt 调整、Skill 新增、Orchestration 规则变化。

### Commit — 评估候选版本，发布或回滚

候选版本不会直接上线。它与当前版本参与**同一组任务评估**——候选版本通过评估，才进入发布流程。通过的更新被保存到版本历史，不通过则丢弃。

```
用户交互 → [Serve] → record_id
用户反馈 → [Observe] → 有资格的 Experience
Experience → [Grow] → 候选更新（权重/Harness）
候选更新 → [Commit] → 评估 → 上线 or 丢弃
    ↓
下一轮 Serve（更强的 Agent）
```

---

## 两类更新对象：模型权重 vs Agent Harness

Reef 明确区分了两类可以被更新的对象：

### 模型权重

通过强化学习或监督微调更新底层模型参数。SAO、OpenClawRL、TTTD 等配方属于这一类，通常需要 GPU。

### Agent Harness

Harness 是 Agent 运行时的"外骨骼"，包含：

| 组件 | 作用 |
|------|------|
| Rules | 行为约束和安全规则 |
| Skills | 工具能力库 |
| Configuration | 运行时配置 |
| Prompts | 系统提示词 |
| Extensions | 扩展模块 |

**SkillClaw** 配方专门针对 Harness 中的 Skill Pool 更新，**不需要 GPU**。这意味着没有训练硬件的团队也可以运行 Reef 的部分自进化能力——Agent 的技能集可以在推理机器上持续演进。

---

## 为什么工程闭环比"自训练"更可靠

许多 Self-improving Agent 方案把"让模型自己训练自己"当作终点。Reef 的定义要具体得多：

```
Agent = Model + Harness
```

这个等式的意义在于：**两侧都可以被学习和更新，两侧共享同一套评估、版本管理和发布流程**。

自进化 Agent 的工程难点不只是"怎么训练"，而是：

1. **反馈结构**：用户反馈怎么跟 record 对应？
2. **更新资格**：哪些数据可以用？哪些该过滤？
3. **候选评估**：新版本真的更好吗？用什么任务集评估？
4. **版本管理**：历史版本怎么存储，回滚怎么做？
5. **线上发布**：更新上线不能破坏正在运行的服务

Reef 为这五个环节都提供了具体的运行基础，而不是只解决训练这一个步骤。

---

## 开发团队

Human-Agent-Society 团队，核心成员 Ao Qu、Han Zheng、Zijian Zhou 等，团队背景涵盖 MIT、NUS 等机构。项目的研究取向偏向工程可用性——不止写 paper，要让闭环真正跑起来。

---

## 对开发者意味着什么

如果你在构建需要持续改进能力的 Agent 服务，Reef 提供了几个值得借鉴的思路：

**1. 把 record id 设计进你的 API**
从第一天起就记录每一次 Agent 交互，而不是事后补日志。有 record id 才有办法后续匹配反馈。

**2. 反馈接口和推理接口同等重要**
用户的 score 和 feedback 是你最便宜的训练数据。让客户端能方便地提交反馈，比设计精密的合成数据流水线性价比高得多。

**3. 先跑 SkillClaw，不用等 GPU**
没有训练资源的团队可以先从 Skill Pool 的演进开始——让 Agent 的能力集在真实使用中自动扩展，成本最低，效果可量化。

**4. 候选版本上线前必须评估**
Reef 的 Commit 环节强制评估不是可选项。自进化的风险在于候选版本可能"进化歪了"。没有评估关的自进化不是进化，是漂移。

---

## 相关链接

- GitHub：[Human-Agent-Society/Reef](https://github.com/Human-Agent-Society/Reef)（开源）
- 延伸阅读：Awesome RSI（Recursive Self-Improvement）研究综述

<!--EN-->

Self-improving agents are one of the most-hyped and hardest-to-ship directions in AI engineering right now. The vision of "models that make themselves smarter" is compelling; the engineering gap between that vision and a working production loop is enormous: Where does training data come from? Which data qualifies? How do you evaluate candidates? How do you deploy updates without breaking production?

The Human-Agent-Society team (MIT, NUS, and others) gives concrete answers with Reef.

---

## Core Insight: User Interactions Are Training Data

Reef doesn't start from "let the model train itself." It starts from a more pragmatic observation:

> **Real user interactions can become training data for the next learning cycle.**

Every agent request, every execution trajectory, every result and user feedback can be structured and stored as **Experience**. Learning recipes read these Experiences and generate updates to model weights, prompts, memory, skills, tools, or orchestration.

This framing matters: **it turns the data acquisition problem from "how do we construct synthetic data" into "how do we use what's already happening."** No extra annotation, no dedicated data pipelines — the agent generates training material while serving users.

---

## Four-Stage Learning Loop

Reef structures the self-evolution process into four linked stages:

### Serve — Accept requests, record interactions

The agent serves requests over an HTTP inference interface. Each response returns an **agent record id** that captures the full interaction: input, trajectory, output.

### Observe — Match feedback, assess learning eligibility

Clients submit score, feedback, and record id via the feedback interface. Observe matches interactions with user feedback and decides which records **qualify for learning** — not every interaction is worth training on; low-quality or unfeedback-free records are filtered out.

### Grow — Run learning recipes, generate candidate updates

Qualified records enter the Grow stage. A learning recipe runs and generates a **candidate update**: new model weights, a prompt change, a new skill, an orchestration rule adjustment.

### Commit — Evaluate candidates, publish or discard

Candidate updates don't go live automatically. The candidate and the current version compete on **the same evaluation task set**. Candidates that pass get published and versioned; failures are discarded.

```
User interaction → [Serve] → record_id
User feedback   → [Observe] → qualified Experience
Experience      → [Grow] → candidate update (weights/harness)
Candidate       → [Commit] → evaluate → ship or discard
     ↓
Next Serve (stronger agent)
```

---

## Two Update Targets: Model Weights vs Agent Harness

Reef cleanly separates two kinds of things that can be updated:

### Model Weights

Underlying model parameters updated via reinforcement learning or supervised fine-tuning. SAO, OpenClawRL, and TTTD recipes fall here, typically requiring GPU.

### Agent Harness

The harness is the agent's runtime "exoskeleton":

| Component | Role |
|-----------|------|
| Rules | Behavioral constraints and safety rules |
| Skills | Tool capability library |
| Configuration | Runtime configuration |
| Prompts | System prompts |
| Extensions | Extension modules |

The **SkillClaw** recipe targets the Skill Pool within the harness and **runs without a GPU**. Teams without training hardware can still run part of Reef's self-evolution capability — the agent's skill set can evolve continuously on inference hardware.

---

## Why Engineering Loops Beat "Self-Training" Narratives

Most self-improving agent proposals stop at "let the model train itself." Reef's definition is more specific:

```
Agent = Model + Harness
```

Both sides can be learned and updated, and both sides share the same evaluation, versioning, and deployment pipeline.

The engineering difficulty of self-improving agents isn't just "how to train" — it's:

1. **Feedback structure**: How does user feedback map back to a record?
2. **Update eligibility**: What data qualifies? What gets filtered?
3. **Candidate evaluation**: Is the new version actually better? On what task set?
4. **Version management**: How are historical versions stored? How does rollback work?
5. **Live deployment**: How do updates ship without disrupting running services?

Reef provides infrastructure for all five, not just the training step.

---

## For Developers

If you're building agent services that need to continuously improve:

**1. Design record ids into your API from day one**
Log every agent interaction from the start. You can't match feedback to a record that wasn't captured.

**2. Treat your feedback interface as seriously as your inference interface**
User scores and feedback are the cheapest training data you have. A good feedback collection path beats a sophisticated synthetic data pipeline for most teams.

**3. Start with SkillClaw, no GPU required**
Skill Pool evolution is the lowest-cost entry point into self-improvement. Let the agent's capabilities expand through real usage before investing in weight updates.

**4. Evaluation before deployment is non-negotiable**
Reef's Commit stage enforces this. Self-improving systems without evaluation gates don't improve — they drift.

---

## Links

- GitHub: [Human-Agent-Society/Reef](https://github.com/Human-Agent-Society/Reef)
- Related: Awesome RSI (Recursive Self-Improvement) survey
