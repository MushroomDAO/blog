---
title: 'CMU 11-768 AI Agents：OpenHands 作者亲授，从零搭 Harness、建评测、用 RL 训 Agent，视频讲义全开放'
titleEn: "CMU 11-768 AI Agents: OpenHands Creator Teaches — Build a Harness From Scratch, Evaluate, Train With RL, All Materials Open"
description: "CMU 语言技术研究所秋季新课，Graham Neubig（OpenHands 核心创始人）+ Daniel Fried 主讲。28 节课三阶段：搭 ReAct Harness→建 LLM-as-judge 评测→SFT+RL 训练 Agent。YouTube 播放列表已上传前 4 讲，3 次作业 starter code 已开放，GitHub 组织 cmu-agents。官网 cmu-agents.com。"
descriptionEn: "CMU Language Technologies Institute fall course taught by Graham Neubig (OpenHands co-founder) and Daniel Fried. 28 lectures in three phases: build a ReAct Harness → design LLM-as-judge evaluation → SFT + RL agent training. YouTube playlist published (first 4 lectures live), assignment starter code open, GitHub org cmu-agents. Official site: cmu-agents.com."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Research"
tags: ["CMU", "AI-agents", "course", "OpenHands", "RL", "SFT", "harness", "evaluation", "open-source", "Graham-Neubig"]
heroImage: "../../assets/images/cmu-11-768-ai-agents-fall-2026-neubig-openhands-harness-rl-course-banner.jpg"
---

> 📌 课程官网：https://www.cmu-agents.com/
> YouTube 播放列表：https://www.youtube.com/playlist?list=PLSN0qpDfUvTM
> GitHub 组织：https://github.com/cmu-agents
> 授课：Graham Neubig + Daniel Fried ｜ CMU LTI ｜ 11-768 ｜ Fall 2026

---

CMU 语言技术研究所（Language Technologies Institute）2026 年秋季开了一门新课：**11-768「AI Agents」**。

主讲是 **Graham Neubig**——CMU LTI 教授，**OpenHands 的核心创始人**（OpenHands 就是之前的 OpenDevin，目前最活跃的开源 AI 软件工程 Agent 框架之一）。联合讲师是 **Daniel Fried**，CMU LTI 教授，曾在 Meta AI 做智能体研究。

这门课的特点：**不是讲 Agent 是什么，是让你从零把 Agent 系统真的搭出来**——Harness、评测、训练三件事全做。

上课时间：周二、周四 3:30–4:50pm ET，Porter Hall 100。

---

## 三阶段课程结构（28 节课）

### 第一阶段：Build / Evaluate / Train（Week 1–4）

**Week 1（L1–L4）**：Agent 总览、工具调用、上下文管理、记忆与技能

**Week 2（L5–L6）**：规划、代码 Agent

**Week 3（L7–L10）**：GUI Agent、SFT（监督微调）、深度研究 Agent

**Week 4（L11–L12）**：高级 RL 算法、RL 系统

### 第二阶段：领域扩展（Week 5–8）

**Week 5（L13–L16）**：沙箱机制、**OpenHands 专场**、LangGraph 专场、可观测性

**Week 6–7（L17–L20）**：工作的未来、多智能体交互、人机协作系统

**Week 8（L21–L23）**：树搜索、客座讲座（Karthik Narasimhan、Sasha Rush）

### 第三阶段：期末（Week 9）

最终 Poster 展示

---

## 三次作业（逐步递进）

**Assignment 1**（截止 9/14）：从零搭 ReAct Harness

内容：
- 实现工具调度循环
- 技能 YAML 发现机制
- 6000-token 上下文压缩
- 在真实 SWE-bench 实例上运行并评分

Starter code：https://github.com/cmu-agents/assignment-1（配套 chess-app bug 靶标应用）

这个作业的要求是：能在 SWE-bench 实例上跑通、得分。不是玩具 Demo，是工业级评测场景。

**Assignment 2**（截止 9/24）：设计评测框架

内容：
- LLM-as-judge 评测框架设计
- FAIL_TO_PASS 指标实现
- 对 Agent 的软件修复能力进行系统性评估

**Assignment 3**（截止 10/22）：训练

内容：
- SFT（监督微调）轨迹收集与训练
- RL 训练（基于奖励信号）
- 对比训练前后 Agent 的行为差异

**团队研究项目**：占总分 50%，选题自定，期末 Poster 展示。

---

## 已公开的材料

**YouTube 播放列表**：https://www.youtube.com/playlist?list=PLSN0qpDfUvTM

目前已上传前 4 讲，约 4.5 小时。L1 视频：https://www.youtube.com/watch?v=UwfjzyLnvMg

**讲义 PDF**：第 1–6 讲已公开。

**GitHub**：https://github.com/cmu-agents — Assignment 1 starter code（50+ stars）已开放。

**官网**：https://www.cmu-agents.com/ — 完整 syllabus、作业说明、讲师信息。

---

## 技术重点拆解

**ReAct Harness**
ReAct（Reasoning + Acting）是目前主流 Coding Agent 的基础框架——交替进行推理和行动（工具调用）。Assignment 1 要求学生从零实现一个完整的 ReAct 循环，包括上下文压缩策略，然后在真实 SWE-bench 实例上验证。

**LLM-as-judge 评测**
用语言模型作为评判器评估 Agent 行为，是当前 Agent 评测的主流做法。Assignment 2 要求学生设计系统性的评测框架，不是跑跑看，而是定义可量化的指标（FAIL_TO_PASS）。

**SFT + RL 训练链路**
Assignment 3 覆盖了目前 Agent 训练的完整链路：先收集成功轨迹做 SFT，再用强化学习信号进一步优化。这是当前 Agent 能力提升的标准路径（类似 Devin、OpenHands 的训练方式）。

**OpenHands 专场**
Week 5 有一节专门讲 OpenHands 内部架构，由 Neubig 本人主讲，相当于官方拆解。

---

## 客座讲师

- **Karthik Narasimhan** — Princeton 教授，AI Agent 领域核心研究者，TextWorld 环境作者
- **Sasha Rush** — Cornell Tech 教授，Hugging Face 研究员，Annotated Transformer 作者

---

## 适合谁

- 想从工程角度系统掌握 Agent 构建的工程师
- 想了解 OpenHands 架构设计的开发者
- 需要系统理解 Agent 评测和训练的研究者

这门课的价值不在于"介绍 Agent 概念"——那类内容网上很多。价值在于：**从零写、从零评、从零训**，每个环节都有对应作业强制落地，而且用的是真实评测集（SWE-bench），不是玩具问题。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Course website: https://www.cmu-agents.com/
> YouTube playlist: https://www.youtube.com/playlist?list=PLSN0qpDfUvTM
> GitHub org: https://github.com/cmu-agents
> Instructors: Graham Neubig + Daniel Fried | CMU LTI | 11-768 | Fall 2026

---

CMU's Language Technologies Institute opened a new course in Fall 2026: **11-768 "AI Agents."**

The primary instructor is **Graham Neubig** — CMU LTI professor and **core co-founder of OpenHands** (formerly OpenDevin, currently one of the most active open-source AI software engineering agent frameworks). The co-instructor is **Daniel Fried**, CMU LTI professor and former Meta AI agent researcher.

This course's defining characteristic: **it's not about explaining what an agent is — it's about actually building one** from scratch. Harness, evaluation, and training: all three, hands-on.

---

## Three-Phase Course Structure (28 Lectures)

### Phase 1: Build / Evaluate / Train (Weeks 1–4)

**Week 1 (L1–L4)**: Agent overview, tool-calling, context management, memory and skills

**Week 2 (L5–L6)**: Planning, coding agents

**Week 3 (L7–L10)**: GUI agents, SFT (supervised fine-tuning), deep research agents

**Week 4 (L11–L12)**: Advanced RL algorithms, RL systems

### Phase 2: Domain Extensions (Weeks 5–8)

**Week 5 (L13–L16)**: Sandboxing, **OpenHands deep dive**, LangGraph session, observability

**Weeks 6–7 (L17–L20)**: Future of work, multi-agent interaction, human-agent collaborative systems

**Week 8 (L21–L23)**: Tree search, guest lectures (Karthik Narasimhan, Sasha Rush)

### Phase 3: Finals (Week 9)

Final poster presentations

---

## Three Assignments (Progressive)

**Assignment 1** (due 9/14): Build a ReAct Harness from scratch

Requirements:
- Implement a tool dispatch loop
- Skill YAML discovery mechanism
- 6000-token context compression
- Run and score on real SWE-bench instances

Starter code: https://github.com/cmu-agents/assignment-1 (includes chess-app as the bug target application)

The requirement: get it working and scored on a SWE-bench instance — not a toy demo, but an industrial evaluation scenario.

**Assignment 2** (due 9/24): Design an evaluation framework

Requirements:
- LLM-as-judge evaluation framework design
- FAIL_TO_PASS metric implementation
- Systematic evaluation of agent software repair capability

**Assignment 3** (due 10/22): Training

Requirements:
- SFT trajectory collection and training
- RL training (reward signal-based)
- Compare agent behavior before and after training

**Team research project**: 50% of the final grade; topic open; final poster presentation.

---

## Published Materials

**YouTube playlist**: https://www.youtube.com/playlist?list=PLSN0qpDfUvTM — first 4 lectures uploaded (~4.5 hours). Lecture 1: https://www.youtube.com/watch?v=UwfjzyLnvMg

**Lecture PDFs**: Lectures 1–6 available.

**GitHub**: https://github.com/cmu-agents — Assignment 1 starter code (50+ stars) open.

**Official site**: https://www.cmu-agents.com/ — full syllabus, assignment details, instructor information.

---

## Technical Deep Dives

**ReAct Harness**
ReAct (Reasoning + Acting) is the foundation of most current coding agents — alternating between reasoning and action (tool calls). Assignment 1 requires implementing a complete ReAct loop from scratch, including a context compression strategy, then validating on real SWE-bench instances.

**LLM-as-Judge Evaluation**
Using a language model as a judge to evaluate agent behavior is the current mainstream approach for agent evaluation. Assignment 2 requires designing a systematic evaluation framework with quantifiable metrics (FAIL_TO_PASS) — not just "run it and see."

**SFT + RL Training Pipeline**
Assignment 3 covers the complete current agent training pipeline: collect successful trajectories for SFT, then optimize further with reinforcement learning signals. This is the standard path for improving agent capabilities (similar to how Devin and OpenHands are trained).

**OpenHands Deep Dive**
Week 5 includes a dedicated session on OpenHands' internal architecture, taught by Neubig himself — essentially an official walkthrough.

---

## Guest Lecturers

- **Karthik Narasimhan** — Princeton professor, core researcher in AI agents, author of the TextWorld environment
- **Sasha Rush** — Cornell Tech professor, Hugging Face researcher, author of The Annotated Transformer

---

## Who It's For

- Engineers who want to systematically build agent systems from an engineering perspective
- Developers who want to understand OpenHands' architectural design
- Researchers who need to systematically understand agent evaluation and training

This course's value isn't in "explaining agent concepts" — that content is everywhere. The value is: **build from scratch, evaluate from scratch, train from scratch**, with every step enforced through assignments using real evaluation sets (SWE-bench), not toy problems.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
