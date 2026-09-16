---
title: 'Stanford CS329A：《自我改进 AI Agent》，斯坦福研究生研讨课，9 集视频全公开'
titleEn: "Stanford CS329A: Self-Improving AI Agents — 9 Lectures Now Free on YouTube"
description: "斯坦福 2025 秋季研究生研讨课，Azalia Mirhoseini 和 Aakanksha Chowdhery 联合授课。核心论点：推理时算力制造下一个模型的训练数据。覆盖 Constitutional AI、STaR、DAPO、Search-o1、ReAct、MemGPT 等自我改进技术。9 集视频 2026 年 8 月全公开，GitHub 作业仓库开源。"
descriptionEn: "Stanford's Autumn 2025 graduate seminar taught by Azalia Mirhoseini and Aakanksha Chowdhery. Central thesis: test-time compute manufactures the training data for the next model. Covers Constitutional AI, STaR, DAPO, Search-o1, ReAct, MemGPT. 9 lectures published free on YouTube in August 2026; homework repos open on GitHub."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Research"
tags: ["Stanford", "AI-agents", "self-improvement", "course", "open-source", "reinforcement-learning", "test-time-compute", "LLM"]
heroImage: "../../assets/images/stanford-cs329a-self-improving-ai-agents-course-open-materials-banner.jpg"
---

> 📌 课程官网：https://cs329a.stanford.edu/
> GitHub 组织：https://github.com/stanford-cs329a
> YouTube 全集（9集）：https://www.youtube.com/playlist?list=PLangBM27OtEA
> 社区中文转录：https://github.com/flowioo/stanford-cs329a-self-improving-ai-agents

---

斯坦福 2025 年秋季开了一门研究生研讨课：CS329A「Self-Improving AI Agents」。授课人是 Azalia Mirhoseini 和 Aakanksha Chowdhery，两位都有 Google DeepMind/Brain 背景。

课程 9 集视频在 2026 年 8 月全部公开上线，可以免费看。作业仓库也在 GitHub 开放。

---

## 这门课在讲什么

一句话概括：**Agent 如何利用自己的执行经验，持续改进自身能力。**

课程的核心论点是：

> **"推理时算力，制造下一个模型所需的训练数据。"**
> Test-time compute manufactures the training data that improves the next model.

这不只是一个优化技巧，而是对当前 AI 能力演进路径的一个结构性判断——模型在推理时产生的轨迹数据，正在成为训练更好模型的原材料。

---

## 课程覆盖的核心技术

**自我改进机制**：

| 技术 | 作用 |
|------|------|
| Constitutional AI | 模型根据原则对自身输出进行自我批评和修正 |
| STaR（Self-Taught Reasoner） | 用模型自己生成的推理链条作为训练数据 |
| DAPO | 通过强化学习在训练阶段实现自我改进 |
| 领域特定 verifier | 用可验证的外部信号（代码运行结果、数学验证）提供精准奖励 |

**推理时扩展**：

| 技术 | 作用 |
|------|------|
| Test-time compute scaling | 推理阶段投入更多算力换取更好的输出 |
| Search-o1 类方法 | 把搜索与 LLM 结合，让模型在推理时主动查找信息 |
| Multi-step reasoning | 多步规划和执行，而不是单步生成 |

**工具与记忆**：

| 技术 | 作用 |
|------|------|
| ReAct | 将推理和行动交替进行，工具调用的基础框架 |
| MemGPT | 超出上下文窗口的长期记忆管理 |
| Code execution | 让模型写代码并执行，用结果验证推理 |

**应用领域**：coding agents（代码生成和修复）、STEM 研究助手、机器人控制。

---

## 论文清单

课程公布了完整的论文阅读清单，覆盖：

- **ReAct**（Yao et al. 2022）——工具调用 Agent 的基础
- **Constitutional AI**（Anthropic）——自我对齐与自我批评
- **STaR**（Zelikman et al. 2022）——自我生成推理链作为训练数据
- **DAPO**——基于 RL 的自我改进
- **MemGPT**——外部记忆管理
- **Search-o1**——搜索增强推理
- **AlphaCode**——代码生成的大规模 RL 训练

这份清单是独立学习的一个有价值的入口——按课程顺序读完这些论文，可以建立起 Agent 自我改进方向的完整知识图。

---

## 开放资源

**YouTube 全集（9 集，Autumn 2025）**：
课程 9 集完整视频在 2026 年 8 月上线，全部免费。内容包括每个主题的讲授，格式是研讨课风格，不是传统讲座。

https://www.youtube.com/playlist?list=PLangBM27OtEA

**GitHub 组织**：
https://github.com/stanford-cs329a

有 6 个仓库，含 Fall 2025 和上一学期的作业题目，可以直接 clone 做练习。

**课程网站**：
https://cs329a.stanford.edu/

列出了完整的课程日历和每节课对应的论文，是结构化论文阅读的导航地图。没有公开 slides 或讲义，但论文链接完整。

**社区中文转录**：
https://github.com/flowioo/stanford-cs329a-self-improving-ai-agents

社区整理的 9 集视频转录 + 中文导读，对不适应英文听力速度的学习者更友好。

---

## 和 CS329Z 的区别

斯坦福还有另一门相近的课 CS329Z「AI Agent Engineering」，两者容易混淆：

| 维度 | CS329A（本课） | CS329Z |
|------|--------------|--------|
| 核心问题 | Agent 如何持续自我改进 | 如何工程化地构建和部署 Agent |
| 侧重 | 自我改进机制、强化学习、推理时扩展 | 系统设计、可靠性、部署、工具链 |
| 受众 | 研究向 | 工程向 |

CS329A 是在问"Agent 能变多好"，CS329Z 是在问"怎么把 Agent 做出来"。

---

## 适合谁

- 想系统理解 Agent 自我改进方向的研究者或工程师
- 想了解 test-time compute scaling 为什么重要的人
- 需要一份结构化论文阅读清单的人

9 集视频加上论文清单，是目前这个方向上结构最完整的公开材料之一。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Course website: https://cs329a.stanford.edu/
> GitHub org: https://github.com/stanford-cs329a
> YouTube playlist (9 lectures): https://www.youtube.com/playlist?list=PLangBM27OtEA
> Community Chinese transcription: https://github.com/flowioo/stanford-cs329a-self-improving-ai-agents

---

Stanford's Autumn 2025 graduate seminar CS329A "Self-Improving AI Agents" is taught by Azalia Mirhoseini and Aakanksha Chowdhery, both with Google DeepMind/Brain backgrounds.

All 9 lecture videos went public on YouTube in August 2026 — free to watch. Homework repos are open on GitHub.

---

## What This Course Covers

One sentence: **how AI agents use their own execution experience to continuously improve their capabilities.**

The course's central thesis:

> **"Test-time compute manufactures the training data that improves the next model."**

This isn't just an optimization trick — it's a structural claim about how AI capability evolves. The trajectories models generate during inference are becoming the raw material for training better models.

---

## Core Techniques

**Self-improvement mechanisms:**

| Technique | Role |
|-----------|------|
| Constitutional AI | Model self-critiques and revises its outputs against principles |
| STaR (Self-Taught Reasoner) | Uses model-generated reasoning chains as training data |
| DAPO | Self-improvement through RL at train time |
| Domain-specific verifiers | Precise reward signals from verifiable external feedback (code execution, math verification) |

**Inference-time scaling:**

| Technique | Role |
|-----------|------|
| Test-time compute scaling | More inference compute → better outputs |
| Search-o1-style methods | Combines search with LLMs for active information retrieval during reasoning |
| Multi-step reasoning | Multi-step planning and execution rather than single-shot generation |

**Tools and memory:**

| Technique | Role |
|-----------|------|
| ReAct | Interleaves reasoning and action — the foundation for tool-calling agents |
| MemGPT | Long-term memory management beyond the context window |
| Code execution | Model writes and runs code, using results to validate reasoning |

**Applications:** coding agents, STEM research assistants, robotics.

---

## Paper List

The course publishes a complete reading list including:

- **ReAct** (Yao et al. 2022) — foundation of tool-calling agents
- **Constitutional AI** (Anthropic) — self-alignment and self-critique
- **STaR** (Zelikman et al. 2022) — self-generated reasoning chains as training data
- **DAPO** — RL-based self-improvement
- **MemGPT** — external memory management
- **Search-o1** — search-augmented reasoning
- **AlphaCode** — large-scale RL training for code generation

Reading through these papers in course order provides a complete knowledge map of the agent self-improvement landscape.

---

## Open Materials

**YouTube playlist (9 lectures, Autumn 2025):**
All 9 sessions published free in August 2026. Seminar-style format rather than traditional lectures.

https://www.youtube.com/playlist?list=PLangBM27OtEA

**GitHub organization:**
https://github.com/stanford-cs329a

6 repositories including homework assignments from Fall 2025 and the previous quarter — available to clone and work through.

**Course website:**
https://cs329a.stanford.edu/

Complete course calendar with linked papers for each session. No public slides or lecture notes, but the paper links are complete — it's a structured reading map.

**Community Chinese transcription:**
https://github.com/flowioo/stanford-cs329a-self-improving-ai-agents

Community-compiled transcriptions + Chinese summaries for all 9 lectures.

---

## CS329A vs. CS329Z

Stanford also offers CS329Z "AI Agent Engineering" — easy to confuse with this one:

| Dimension | CS329A (this course) | CS329Z |
|-----------|---------------------|--------|
| Core question | How do agents keep improving themselves? | How do you engineer and deploy agents reliably? |
| Focus | Self-improvement, RL, inference-time scaling | Systems design, reliability, tooling |
| Audience | Research-oriented | Engineering-oriented |

CS329A asks "how good can agents get," CS329Z asks "how do you actually build them."

---

## Who It's For

- Researchers or engineers who want a systematic grounding in agent self-improvement
- Anyone trying to understand why test-time compute scaling matters
- People who need a structured research reading list in this area

9 lectures plus a curated paper list — currently one of the most complete publicly available resources on this topic.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
