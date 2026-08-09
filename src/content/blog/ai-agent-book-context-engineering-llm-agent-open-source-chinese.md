---
title: "19000 星开源书：《深入理解 AI Agent》，10 章 92 个实验，从上下文工程到多 Agent 协作全覆盖"
titleEn: "19k-Star Open-Source Book: 'AI Agents in Depth' — 10 Chapters, 92 Experiments, From Context Engineering to Multi-Agent Systems"
description: "李博杰著《深入理解 AI Agent：设计原理与工程实践》，bojieli/ai-agent-book，19005 stars，Apache-2.0。围绕「Agent = LLM + 上下文 + 工具」展开，10章92个配套实验（70+可独立运行），7种语言，全部免费开源，PDF/EPUB 可直接下载。"
descriptionEn: "Li Bojie's 'AI Agents in Depth: Design Principles and Engineering Practice', bojieli/ai-agent-book, 19,005 stars, Apache-2.0. Built around the formula Agent = LLM + Context + Tools: 10 chapters, 92 companion experiments (70+ runnable), 7 languages, all free and open source with PDF/EPUB downloads."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Research"
tags: ["AI Agent", "开源书", "上下文工程", "Context Engineering", "LLM", "MCP", "多Agent", "强化学习", "Coding Agent", "学习资源"]
heroImage: "../../assets/images/ai-agent-book-context-engineering-llm-agent-open-source-chinese-banner.jpg"
---

> **仓库**：bojieli/ai-agent-book · Python · Apache-2.0 · 19,005 stars
> **作者**：李博杰
> **在线阅读**：https://bojieli.github.io/ai-agent-book/
> **PDF 下载**：[中文版](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf) · [英文版](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.pdf)

---

## 一、为什么这本书值得认真读

AI Agent 的资料不少，但大多数要么停在原理层面，要么是某个框架的教程。

这本书做的事情不太一样：围绕一个公式把 Agent 从头讲到生产，每章都有配套实验可以跑，全书开源免费。

> **Agent = LLM + 上下文 + 工具**

这个公式看起来简单，但作者的意思是：**这三件事各自做好，是 Agent 能力的真正来源**。Harness 工程（把三者连起来跑起来的脚手架）才是产品竞争力所在，而不是某个模型有多厉害。

19,005 个 star，1,893 个 fork，已经被翻译成 7 种语言（含英文、俄文、日文、越南文），这个热度说明社区对它的认可程度。

---

## 二、10 章，层层递进

全书 10 章，从入门到生产，每章独立又连贯：

| 章 | 主题 | 核心问题 | 实验数 |
|:--:|------|---------|:-----:|
| 1 | **Agent 基础知识** | 什么是 Agent？Harness 怎么搭？ | 4 |
| 2 | **上下文工程** | 如何用好 KV Cache、压缩上下文、写 Agent Skills？ | 9 |
| 3 | **用户记忆和知识库** | 怎么让 Agent 跨会话记住用户？RAG 如何落地？ | 13 |
| 4 | **工具** | MCP 协议是什么？感知/执行/协作三类工具如何设计？ | 7 |
| 5 | **Coding Agent** | 代码是「能创造新工具的工具」，生产级 Coding Agent 的全貌 | 12 |
| 6 | **Agent 的评估** | 如何把表现变成可比较的信号？统计显著性怎么用？ | 11 |
| 7 | **模型后训练** | 什么时候选 SFT？什么时候选 RL？工具调用如何内化？ | 16 |
| 8 | **Agent 的持续进化** | 从运行轨迹获得学习信号，更新知识/指令/参数 | 8 |
| 9 | **多模态与实时交互** | 语音三范式、Computer Use、机器人控制 | 7 |
| 10 | **多 Agent 协作** | 群体如何超过个体？涌现的「Agent 社会」 | 7 |

**92 个配套实验**，70+ 个可以直接 clone 跑起来，不是伪代码示意。

---

## 三、值得重点关注的几章

### 第 2 章：上下文工程（Context Engineering）

这是当前最热的话题之一，书里早已专章覆盖。

「上下文工程」的核心洞察是：**上下文决定能力上限，而不是模型本身**。同一个 LLM，喂给它不同的上下文，表现可以天差地别。

这章讲的具体内容：
- **KV Cache 管理**：怎么高效复用、减少重复计算
- **提示工程**：从原则到具体技巧
- **Agent Skills**：把可复用的能力打包成 skill，而不是每次重新描述
- **上下文压缩**：长对话/长文档怎么在不丢关键信息的前提下缩减 token

### 第 3 章：用户记忆和知识库

记忆是让 Agent 从「工具」变成「助手」的关键。这章从用户记忆（跨会话记住偏好和历史）讲到知识库（RAG、结构化索引、知识图谱），有 13 个实验，是全书实验最多的章节之一。

### 第 7 章：模型后训练

这是通常最难找到好资料的部分。书里把预训练 → SFT → RL 三阶段讲清楚了，并且有 16 个实验，包括：
- 从零训练一个小 LLM（MiniMind）
- 从零训练一个 VLM（MiniMind-V，带视觉投影层）
- 用 RLVP（强化学习视觉策略）控制机器人
- SFT vs RL 的实际效果对比（SFTvsRL 仓库）

### 第 10 章：多 Agent 协作

「群体智能高于个体」——这章讲的是当多个 Agent 协同工作时，如何设计上下文共享/隔离机制，以及涌现行为是怎么产生的。配套实验包括：
- **TalkAct**：双 Agent 边通话边操作电脑的架构（已独立成项目）
- **斯坦福 AI 小镇**（generative_agents）：经典多 Agent 仿真复现

---

## 四、92 个实验，如何使用

书里把实验分成三类：

- ✅ **可运行**：clone 下来直接跑，大部分只需要 API key
- 📖 **复现型**：需要额外克隆外部仓库，README 有详细说明
- 📝 **读者练习**：基于已有实验改造扩展

有 19 个外部仓库（评测基准、训练框架、机器人平台）需要单独克隆，书里提供了一键脚本：

```bash
# 举例：第 6 章评测基准
git clone https://github.com/SWE-bench/SWE-bench.git     chapter6/SWE-bench
git clone https://github.com/xlang-ai/OSWorld.git          chapter6/OSWorld

# 第 7 章训练框架
git clone https://github.com/bojieli/verl.git              chapter7/verl
git clone https://github.com/bojieli/minimind.git          chapter7/MiniMind-pretrain/minimind

# 第 10 章多 Agent 仿真
git clone https://github.com/joonspk-research/generative_agents.git  chapter10/generative_agents
```

---

## 五、推荐的学习路径

书里有专门的[学习建议文档](https://bojieli.github.io/ai-agent-book/)，总结几个关键原则：

**按顺序读，跳过熟悉的**：章节有依赖关系，但每章开头都有前置知识说明，有基础的读者可以直接跳到感兴趣的部分。

**实验优先**：「把实验跑一遍」比「把章节读三遍」学到的多。特别是第 2 章（上下文工程）和第 3 章（记忆）的实验，直接跑一遍会对原理的理解完全不同。

**API Key 准备**：国内推荐 Kimi（月之暗面）/ 智谱 GLM / SiliconFlow / DeepSeek。一般实验只需要文本 API，第 9 章（多模态）会用到视觉 API。

**难度分级**：第 1-4 章适合零基础，第 5-8 章需要一些 LLM 基础，第 9-10 章有部分实验需要硬件（机器人）或特定环境。

---

## 六、这本书和其他资料的区别

已经有很多 LLM/Agent 教程，为什么还值得读这本？

**不绑定框架**：绝大多数教程以某个框架（LangChain/AutoGen/CrewAI）为核心，容易学到框架用法而不是 Agent 原理。这本书从原理出发，框架是例子不是主角。

**实验是真实验**：配套代码不是示意性伪代码，而是可以真实运行的项目，覆盖从 RAG 到 RL 训练的完整链路。

**中文原版**：不是翻译，没有术语翻译不准的问题，作者本身的工程背景保证了「落地」视角一直在线。

**持续更新**：GitHub 仓库每天都有更新（最后更新：2026-07-24 当天），社区已翻译成 7 种语言并在持续修订。

---

## 七、如何获取

**在线阅读**（免费，自动同步最新）：
https://bojieli.github.io/ai-agent-book/

**PDF / EPUB 下载**（免费，推荐离线阅读）：
- 中文：[PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.epub)
- 英文：[PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.epub)

**配套代码**：
```bash
git clone https://github.com/bojieli/ai-agent-book
```

Apache-2.0 许可证，商业使用无限制。

---

*数据来源：GitHub bojieli/ai-agent-book，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: bojieli/ai-agent-book · Python · Apache-2.0 · 19,005 stars
> **Author**: Li Bojie
> **Read online**: https://bojieli.github.io/ai-agent-book/
> **PDF Download**: [Chinese](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf) · [English](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.pdf)

---

## 1. Why This Book Is Worth Your Time

There's no shortage of AI Agent resources — but most of them either stay at the conceptual level or are really tutorials for a specific framework.

This book does something different: it builds the entire Agent picture around a single formula and backs every chapter with runnable experiments, all free and open source.

> **Agent = LLM + Context + Tools**

The formula looks simple, but the author's point is more specific: **each of the three components has to be engineered well — that's where agent capability actually comes from.** The harness (the scaffolding that connects these three and keeps them running) is where product competitiveness lives, not in which model you pick.

19,005 stars, 1,893 forks, and community translations into 7 languages (English, Russian, Japanese, Vietnamese, Tamil, Traditional Chinese, and the original Simplified Chinese) — those numbers reflect a clear signal of practical value.

---

## 2. Ten Chapters, Layer by Layer

The book covers 10 chapters in a deliberate progression from fundamentals to production:

| Ch | Topic | Core Question | Labs |
|:--:|-------|--------------|:----:|
| 1 | **Agent Fundamentals** | What is an agent? How do you build the harness? | 4 |
| 2 | **Context Engineering** | How do you manage KV Cache, compress context, write Agent Skills? | 9 |
| 3 | **User Memory & Knowledge Bases** | How does an agent remember across sessions? How does RAG work in practice? | 13 |
| 4 | **Tools** | What is the MCP protocol? How do you design perception / action / collaboration tools? | 7 |
| 5 | **Coding Agents** | Code is "the tool that creates tools" — the full picture of production-grade coding agents | 12 |
| 6 | **Agent Evaluation** | How do you turn performance into comparable signals? When does statistical significance matter? | 11 |
| 7 | **Post-Training** | When do you choose SFT vs RL? How do you internalize tool use into the model? | 16 |
| 8 | **Continuous Evolution** | How do you extract learning signals from runtime traces to update knowledge, instructions, and parameters? | 8 |
| 9 | **Multimodal & Real-Time** | Three voice paradigms, Computer Use, robot control | 7 |
| 10 | **Multi-Agent Collaboration** | How does a group surpass the individual? What is an emergent "agent society"? | 7 |

**92 companion experiments**, with 70+ directly runnable — not pseudocode illustrations.

---

## 3. Chapters Worth Special Attention

### Chapter 2: Context Engineering

This is one of the most actively discussed topics in AI right now, and the book dedicated a full chapter to it early on.

The core insight of context engineering: **context sets the capability ceiling, not the model.** The same LLM, given different contexts, can perform orders of magnitude differently.

Specific topics covered:
- **KV Cache management**: how to reuse efficiently, reduce redundant computation
- **Prompt engineering**: from principles to specific techniques
- **Agent Skills**: packaging reusable capability as skills, not re-describing from scratch each time
- **Context compression**: how to reduce tokens in long conversations and documents without losing critical information

### Chapter 3: User Memory and Knowledge Bases

Memory is the difference between an agent that is a "tool" and one that is an "assistant." This chapter goes from user memory (remembering preferences and history across sessions) to knowledge bases (RAG, structured indexing, knowledge graphs), with 13 experiments — the most of any single chapter.

### Chapter 7: Post-Training

This is one of the areas where good material is hardest to find. The book walks through pre-training → SFT → RL in three stages and includes 16 experiments:
- Train a small LLM from scratch (MiniMind)
- Train a VLM from scratch (MiniMind-V, with visual projection layer)
- Robot control using RLVP (Reinforcement Learning Visual Policy)
- Real SFT vs RL comparison (the SFTvsRL repo)

### Chapter 10: Multi-Agent Collaboration

"The group surpasses the individual" — this chapter addresses how to design context sharing and isolation when multiple agents work together, and how emergent behavior arises. Companion experiments include:
- **TalkAct**: a dual-agent architecture that simultaneously makes a phone call and operates a computer (now an independent project)
- **Stanford AI Town** (generative_agents): the classic multi-agent simulation, reproduced

---

## 4. 92 Experiments — How to Use Them

Experiments come in three types:

- ✅ **Runnable**: clone and run immediately, most only require an API key
- 📖 **Reproducible**: requires cloning external repos, with detailed README instructions
- 📝 **Reader exercises**: extend and adapt from existing experiments

19 external repositories (evaluation benchmarks, training frameworks, robotics platforms) require separate clones; the book provides a one-liner script:

```bash
# Chapter 6: evaluation benchmarks
git clone https://github.com/SWE-bench/SWE-bench.git     chapter6/SWE-bench
git clone https://github.com/xlang-ai/OSWorld.git          chapter6/OSWorld

# Chapter 7: training frameworks
git clone https://github.com/bojieli/verl.git              chapter7/verl
git clone https://github.com/bojieli/minimind.git          chapter7/MiniMind-pretrain/minimind

# Chapter 10: multi-agent simulation
git clone https://github.com/joonspk-research/generative_agents.git  chapter10/generative_agents
```

---

## 5. Recommended Learning Paths

The book includes a dedicated [learning guide](https://bojieli.github.io/ai-agent-book/). A few key principles worth highlighting:

**Read in order, skip what you know**: chapters have dependencies, but each opens with prerequisite notes so experienced readers can jump in where they need to.

**Experiments first**: running an experiment once teaches more than reading a chapter three times. Chapters 2 (Context Engineering) and 3 (Memory) especially — after you run the experiments, your understanding of the principles shifts completely.

**API key prep**: For China-accessible APIs, Kimi (Moonshot AI), Zhipu GLM, SiliconFlow, and DeepSeek all work. Most experiments only need text APIs; Chapter 9 (Multimodal) uses vision APIs.

**Difficulty tiers**: Chapters 1-4 are beginner-friendly; Chapters 5-8 assume some LLM background; Chapters 9-10 have some experiments requiring dedicated hardware (robots) or specific environments.

---

## 6. How This Compares to Other Resources

There are already many LLM/Agent tutorials. What makes this one different?

**Not framework-bound**: most tutorials center on a framework (LangChain / AutoGen / CrewAI) and you end up learning framework API rather than agent principles. This book starts from principles — frameworks are examples, not the subject.

**Real experiments, not demos**: the companion code isn't illustrative pseudocode — it's projects that actually run, covering the full chain from RAG to RL training.

**Chinese-native, not translated**: no translation artifacts or imprecise terminology. The author's engineering background keeps the "production perspective" present throughout.

**Actively updated**: the GitHub repo receives daily updates (last updated: 2026-07-24, the day this was written). Community translations are being actively revised in 7 languages.

---

## 7. How to Get It

**Read online** (free, auto-synced to latest):
https://bojieli.github.io/ai-agent-book/

**PDF / EPUB download** (free, recommended for offline reading):
- Chinese: [PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.epub)
- English: [PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.epub)

**Code**:
```bash
git clone https://github.com/bojieli/ai-agent-book
```

Apache-2.0 license — unrestricted commercial use.

---

*Data source: GitHub bojieli/ai-agent-book, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
