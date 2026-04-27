---
title: "告别静态技能库！阿里发布 SkillClaw，开启 AI Agent「集体进化」时代"
titleEn: "Beyond Static Skill Libraries: Alibaba's SkillClaw Brings Collective Evolution to AI Agents"
description: "阿里 AMAP-ML 团队发布 SkillClaw 框架，通过 Agentic Evolver 自动聚合用户交互轨迹、更新共享技能库，让 AI Agent 实现集体进化。论文于 4 月登顶 HuggingFace 论文榜，6 轮进化后 Creative Synthesis 任务相对提升 88.41%。"
descriptionEn: "Alibaba AMAP-ML released SkillClaw, a framework using Agentic Evolver to auto-aggregate user trajectories and update shared skill libraries — enabling collective skill evolution in AI agents. After 6 rounds, the framework achieved 88.41% relative improvement on Creative Synthesis tasks."
pubDate: "2026-04-27"
updatedDate: "2026-04-27"
category: "Tech-News"
tags: ["SkillClaw", "AI Agent", "Alibaba", "AMAP-ML", "技能进化", "Skill Evolution", "Agentic", "Open Source"]
heroImage: "../../assets/images/skillclaw-collective-evolution.jpg"
---

## 核心概述（30-50 字）

SkillClaw 是阿里 AMAP-ML 开发的 AI Agent 技能进化框架，通过自动聚合用户交互轨迹并利用 Agentic Evolver 持续更新共享技能库，实现 AI 能力的集体进化。

## 新闻概述

在 AI Agent 领域，技能（Skill）通常被视为 Agent 执行任务的"工具书"。然而，传统的技能库在部署后往往是静态的，导致不同用户在相似场景下反复"踩坑"，系统缺乏持续积累经验的能力。针对这一痛点，阿里巴巴 AMAP-ML 团队近日发布了名为 **SkillClaw** 的创新性研究，论文于 4 月登顶 HuggingFace 当日论文榜，并获得社区广泛关注（[arXiv:2604.08377](https://arxiv.org/abs/2604.08377)，[HuggingFace 论文页](https://huggingface.co/papers/2604.08377)）。

### 核心创新：从"个人经验"到"集体智慧"

SkillClaw 的核心理念是 **"集体技能进化"**（Collective Skill Evolution）。它不再依赖开发者手动维护代码，而是将所有用户的交互过程视为学习信号。系统会自动收集脱敏后的交互轨迹，并交由一个名为 **"Agentic Evolver"** 的自主智能体进行处理。

这个"进化器"扮演了高级专家的角色：它能识别用户在实际使用中重复出现的行为模式，分析成功与失败的原因。通过 **"精炼（Refine）"** 现有技能或 **"新建（Create）"** 缺失技能，SkillClaw 能将零散的经验转化为可重复利用的标准化技能，并同步回共享库。这意味着，只要有一名用户探索出了更高效的路径，整个系统的所有用户都能立即受益。

### 实战表现：性能的单调显著增长

在专门针对真实 Agent 场景设计的测试集 **WildClawBench** 上，SkillClaw 展现了极强的进化能力。实验数据显示，即使在有限的交互反馈下，该框架也能显著提升 Qwen3-Max 等大模型的执行效率。更重要的是，随着交互轮数的增加，技能库表现出"单调增长"的特性，有效避免了遗忘或性能倒退。

根据 [36kr 报道](https://eu.36kr.com/en/p/3767753692201481)，**6 轮进化后，SkillClaw 在 Creative Synthesis（创意合成）任务类别上获得了 88.41% 的相对提升**——这是该框架最显著的成果之一。

目前，SkillClaw 的代码已在 GitHub 开源（[AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw)）。这一突破标志着 AI Agent 正式从"预设技能"阶段步入"实战自进化"阶段，极大降低了复杂任务下 Agent 的运维门槛。

### Agentic Evolver 工作原理（简要）

根据论文（[arXiv:2604.08377v1](https://arxiv.org/abs/2604.08377v1)）的描述，Agentic Evolver 是一个 **配备结构化 Harness 的 LLM Agent**：

1. 接收聚合后的会话证据（grouped session evidence）
2. 读取当前技能定义（current skill definition）
3. 通过开放式推理（open-ended reasoning）决定如何行动
4. 输出对技能集的更新（refine 或 create）

这与传统"训练 → 部署 → 静态运行"的 Agent 范式形成鲜明对比。

### 与本地 AI 路线的对照思考

SkillClaw 的"集体进化"思路，与我们 [iDoris 立项思考](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/) 中讨论的 **"个人 → 社区 → 城市"联邦聚合**有相似的底层动机：单点经验有限，集体聚合产生超额价值。

差异在于：

- **SkillClaw**：聚焦 Agent 的**技能层**（工具调用与流程定义），通过 Agentic Evolver 在云端共享技能库
- **iDoris（联邦 LoRA 路线）**：聚焦**模型权重层**，通过 DP-SGD + 联邦 LoRA 让多用户的偏好在保护隐私的前提下聚合

两者可以正交并存：你的 Agent 调用的"技能"由 SkillClaw 类机制集体进化，而调用这些技能的"决策模型"由 iDoris 类机制持续学你。这是 AI Agent 时代下"集体智能 × 个人主权"的两条互补路径。

---

## 参考资料

- 论文：[SkillClaw: Let Skills Evolve Collectively with Agentic Evolver, arXiv:2604.08377](https://arxiv.org/abs/2604.08377)
- HuggingFace 论文页：[huggingface.co/papers/2604.08377](https://huggingface.co/papers/2604.08377)
- 开源代码：[github.com/AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw)
- 论文 PDF：[arXiv PDF](https://arxiv.org/pdf/2604.08377)
- 相关报道：[36kr: Stop Reinventing the Wheel — 88% Improvement after 6 Rounds](https://eu.36kr.com/en/p/3767753692201481)
- alphaXiv 概述：[alphaxiv.org/overview/2604.08377v1](https://www.alphaxiv.org/overview/2604.08377v1)

<!--EN-->

## TL;DR (30-50 words)

SkillClaw, developed by Alibaba's AMAP-ML team, is an AI Agent skill evolution framework. It auto-aggregates user interaction trajectories and uses an "Agentic Evolver" to continuously update a shared skill library, enabling collective evolution of AI capabilities.

## Story Overview

In the AI Agent field, "skills" are commonly viewed as the toolkit an agent uses to execute tasks. However, traditional skill libraries are static after deployment — different users repeatedly "trip on the same rocks" in similar scenarios, and systems lack the ability to continuously accumulate experience. To address this pain point, Alibaba's AMAP-ML team recently published **SkillClaw**, an innovative research effort. The paper topped HuggingFace's daily paper rankings in April and received broad community attention ([arXiv:2604.08377](https://arxiv.org/abs/2604.08377), [HuggingFace paper page](https://huggingface.co/papers/2604.08377)).

### Core Innovation: From "Individual Experience" to "Collective Wisdom"

SkillClaw's core concept is **"Collective Skill Evolution"**. Instead of relying on developers to manually maintain code, it treats all user interactions as learning signals. The system automatically collects redacted trajectories and routes them to an autonomous agent called the **"Agentic Evolver"**.

This "evolver" plays the role of a senior expert: it identifies recurring behavioral patterns in actual usage and analyzes the reasons for success and failure. By **"Refining"** existing skills or **"Creating"** missing ones, SkillClaw transforms scattered experiences into reusable standardized skills, then synchronizes them back to the shared repository. This means: as soon as one user discovers a more efficient path, all users in the system benefit immediately.

### Performance: Monotonic Improvement in Real Tests

On **WildClawBench**, a test set designed specifically for real-world Agent scenarios, SkillClaw demonstrated strong evolutionary capability. Experiments show that even with limited interaction feedback, the framework significantly improves the execution efficiency of large models like Qwen3-Max. More importantly, as interaction rounds increase, the skill library exhibits "monotonic growth", effectively avoiding forgetting or performance regression.

According to [36kr's coverage](https://eu.36kr.com/en/p/3767753692201481), **after 6 rounds of evolution, SkillClaw achieved 88.41% relative improvement on the Creative Synthesis task category** — one of the framework's most striking results.

The SkillClaw code is now open-source on GitHub ([AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw)). This breakthrough marks AI Agents moving formally from the "preset skills" stage into "battle-tested self-evolution", significantly lowering the operational threshold for complex agent tasks.

### How the Agentic Evolver Works (Brief)

According to the paper ([arXiv:2604.08377v1](https://arxiv.org/abs/2604.08377v1)), the Agentic Evolver is **an LLM Agent equipped with a structured Harness**:

1. Receives grouped session evidence
2. Reads the current skill definition
3. Decides how to act through open-ended reasoning
4. Outputs updates to the skill set (refine or create)

This stands in sharp contrast to the traditional "train → deploy → run statically" Agent paradigm.

### Cross-Reference: The Local AI Track

SkillClaw's "collective evolution" idea shares a similar underlying motivation with the **"Personal → Community → City" federated aggregation** discussed in our [iDoris project launch](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/): single-point experience is limited, collective aggregation produces excess value.

The differences:

- **SkillClaw**: focuses on the Agent's **skill layer** (tool calls and workflow definitions), with cloud-shared skill libraries via the Agentic Evolver
- **iDoris (federated LoRA track)**: focuses on the **model weight layer**, using DP-SGD + federated LoRA to aggregate multi-user preferences while preserving privacy

The two are orthogonal and can coexist: your Agent's "skills" evolve collectively via SkillClaw-class mechanisms, while the "decision model" calling those skills learns you continuously via iDoris-class mechanisms. These are two complementary paths in the AI Agent era of "collective intelligence × personal sovereignty".

---

## References

- Paper: [SkillClaw: Let Skills Evolve Collectively with Agentic Evolver, arXiv:2604.08377](https://arxiv.org/abs/2604.08377)
- HuggingFace paper: [huggingface.co/papers/2604.08377](https://huggingface.co/papers/2604.08377)
- Open-source code: [github.com/AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw)
- arXiv PDF: [arxiv.org/pdf/2604.08377](https://arxiv.org/pdf/2604.08377)
- Related coverage: [36kr: Stop Reinventing the Wheel — 88% Improvement after 6 Rounds](https://eu.36kr.com/en/p/3767753692201481)
- alphaXiv overview: [alphaxiv.org/overview/2604.08377v1](https://www.alphaxiv.org/overview/2604.08377v1)
