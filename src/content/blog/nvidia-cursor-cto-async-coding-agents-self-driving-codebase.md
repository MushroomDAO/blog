---
title: "按头安利：Building Towards Self-Driving Codebases with Long-Running, Asynchronous Agents"
titleEn: "Must Watch: Building Towards Self-Driving Codebases with Long-Running, Asynchronous Agents"
description: "Cursor 联合创始人兼 CTO Aman Sanger 在 NVIDIA GTC 2026 上发表演讲，拆解 AI 编程三个时代的演进：从自动补全 → 同步 Agent → 异步云端 Agent，最终走向「自动驾驶代码库」。30% 的 Cursor 内部 PR 已由云端 Agent 提交，包括一次 8 小时完成的 25× 性能优化重构。"
descriptionEn: "Cursor co-founder and CTO Aman Sanger at NVIDIA GTC 2026 breaks down the three eras of AI-assisted programming: autocomplete → sync agents → async cloud agents → self-driving codebases. 30% of Cursor's internal PRs are now submitted by cloud agents, including an 8-hour 25× performance optimization refactor."
pubDate: "2026-07-14"
updatedDate: "2026-07-14"
category: "Tech-Experiment"
tags: ["AI Agent", "Cursor", "NVIDIA", "编程未来"]
heroImage: "../../assets/images/nvidia-cursor-cto-async-coding-agents-self-driving-codebase-banner.jpg"
---

> 视频：**Building Towards Self-Driving Codebases with Long-Running, Asynchronous Agents**  
> 主讲：Aman Sanger，Cursor 联合创始人兼 CTO  
> 来源：NVIDIA Developer / NVIDIA GTC 2026  
> 时长：37 分 48 秒  
> YouTube：[youtube.com/watch?v=2Fp3jIrFTMo](https://www.youtube.com/watch?v=2Fp3jIrFTMo)

---

## 为什么值得看

过去一年，"AI 编程"从一个新鲜词变成了日常工具——但几乎没有人在系统性地问：**接下来呢？**

这场演讲是 Cursor CTO 在 NVIDIA GTC 2026 上给出的答案。它不是产品发布，不是 demo 秀，是一次对 AI 编程未来路线图的清晰、诚实的推演。

---

## AI 编程的三个时代

### 时代一（2021–2022）：Tab 自动补全

IntelliSense 级别的补全。模型看过去几分钟的编辑历史，预测下几个改动的位置。Cursor 在这个时代登上历史舞台。

### 时代二（2025，当下）：同步 Coding Agent

你给一句自然语言需求，Agent 自主实现整个功能。这已经成为主流——Cursor 内部数据显示，现在**绝大多数的代码**来自 Agent，而不是 Tab 补全。这个数字增速之快，连 Aman 自己都说"这张图令我震惊"。

### 时代三（进行中）：异步云端 Agent → 自动驾驶代码库

同步 Agent 在本地跑，受制于资源，同时跑十几个 Agent 不现实。

异步 Agent 运行在云端，有完整的 VM、桌面环境、测试能力，可以并行扩展。工程师下班，Agent 继续工作。

---

## Cursor 内部的数据

这不是 PPT 上的愿景，是已经在跑的系统：

> **30% 的合并 PR 来自云端 Agent。**

两个代表性案例：

- **25× 视频渲染性能优化**：Agent 独立完成了从 React 到 Rust 的迁移重构，耗时 8 小时。关键是 Agent 有一台"电脑"可以实际运行代码、测量延迟、迭代改进——人工根本不可能这么快。
- **10,000 行 PR**：为 Sandbox 进程实现网络策略控制。这不是"帮你写几个函数"，是完整的工程交付。

---

## 为什么 Agent 会在长任务中"崩"

Aman 在演���中谈到一个被很多人忽视的问题：**训练分布 vs. 部署分布不匹配**。

当前模型用 RL 训练，轨迹长度上限大约在几十万 token。但一个真实的长期任务可能会延伸到几百万、甚至几千万 token。超出训练分布后，Agent 开始失去追踪、重复动作、在细节处错误——这是你现在用长时间运行的 Agent 肯定见过的现象。

**解法：多 Agent 系统。**

外层 Orchestrator 保持相对短的上下文，把复杂任务拆解成子任务，分发给 Sub-Agent。每个 Sub-Agent 处理的任务复杂度都在训练分布之内，完成后汇报结果。

```
外层 Orchestrator（规划，数十万 token）
    ├── Sub-Agent A（实现功能 X）
    ├── Sub-Agent B（跑测试 + 验证）
    └── Sub-Agent C（录制功能 demo 视频）
```

---

## 模型分工：不同模型干不同的活

Cursor 云端 Agent 的多模型策略，也是本场演讲里最有信息量的实战细节之一：

| 角色 | 擅长模型 | 原因 |
|------|---------|------|
| **高层规划 + Orchestration** | OpenAI 模型 | 更强的规划和组织能力 |
| **Computer Use + 多模态** | Gemini / Anthropic | 更好的视觉理解和界面操作 |
| **UI 实现** | Anthropic 模型 | 生成的 UI 代码质量更高 |
| **简单子任务** | 小模型 | 响应更快，性能一样，成本更低 |

---

## "Artifacts"：让工程师不用读代码就能审查 Agent 的输出

随着 Agent 吞吐量上涨，手动 code review 变得不可持续。Cursor 的方案是引入**可审查的 Artifacts（产出物）**：

- **功能 Demo 视频**：Agent 实现完一个功能之后，自动录一段真实运行的视频。你看视频就知道做对没有，不用去读代码。有 bug → 直接 reprompt → Agent 修完再录。
- **ML 实验报告**：小规模研究实验，Agent 去做、跑、汇总，交给你的是一份结构化报告，而不是一堆 Python 脚本。
- **架构图 / 变更方案**（未来）：后端和基础设施场景，先审图、审方案，确认方向对了再看代码。

这背后有一个有趣的哲学转变：**工程师开始审查 Agent 的"意图"而不是"实现"。**

---

## 自动驾驶代码库：工程师的角色会变成什么

Aman 的最后一部分，也是最让人思考的一部分。

自动驾驶代码库不等于"工程师消失"，而是**工程师的工作层级上移**：

- 写详细的、可验证的 **Spec（规格说明）**，作为 Agent 的"实现方案"和"评估套件"
- 审查 Artifacts（视频、报告、图表），确认 Agent 方向对了
- 处理 Agent 真的搞不定的问题——而不是亲自写每一行代码

用他的话说：

> *"Software engineering is quickly shifting to async agents that work independently and report back like colleagues."*

---

## 为什么在 NVIDIA GTC 讲这个

这场演讲在 NVIDIA GTC 上，背景并不微妙：异步 Agent 大规模跑在云端，需要 GPU 算力。Cursor 云端 Agent 在 NVIDIA 硬件上运行，每个 Agent 实例都在消耗 GPU 资源。

NVIDIA 的视角：Coding Agent 的普及 = 持续增长的 GPU 需求。这场演讲对双方都有价值。

---

## 值得关注的相关演讲（NVIDIA GTC 2026 同系列）

如果这场演讲让你感兴趣，NVIDIA Developer 频道还有几个同期相关演讲：

- [Agentic AI 101 | NVIDIA GTC](https://www.youtube.com/watch?v=ETq3ZTqxFlo) — Agent 基础概念
- [Practical Context Engineering: Eliminate Bugs with High-Signal AI Code Reviews](https://www.youtube.com/watch?v=Kz-i33toG2g) — 高质量上下文工程实践
- [Securing Long-Running AI Agents: From Setup to Sandboxing](https://www.youtube.com/watch?v=rLjQDi-hHk4) — 长时运行 Agent 的安全隔离
- [Continual Learning for Long-Running Agents](https://www.youtube.com/watch?v=SVWmuJx0hHM) — Agent 持续学习

---

**主视频**：[youtube.com/watch?v=2Fp3jIrFTMo](https://www.youtube.com/watch?v=2Fp3jIrFTMo)  
**NVIDIA Developer 频道**：[@NVIDIADeveloper](https://www.youtube.com/@NVIDIADeveloper)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Must Watch: Building Towards Self-Driving Codebases with Long-Running, Asynchronous Agents

> Video: NVIDIA GTC 2026 | Speaker: Aman Sanger, Co-founder & CTO at Cursor  
> Duration: 37m 48s | [YouTube](https://www.youtube.com/watch?v=2Fp3jIrFTMo)

---

### The Three Eras of AI-Assisted Programming

Cursor CTO Aman Sanger lays out a clear roadmap for where AI coding is headed:

**Era 1 (2021–2022): Tab Autocomplete** — IntelliSense-level suggestions, predicting the next few keystrokes.

**Era 2 (2025, current): Synchronous Coding Agents** — You prompt in natural language, the agent implements whole features. The vast majority of code written in Cursor now comes from agents, not tab — a graph Aman calls "astounding."

**Era 3 (emerging): Async Cloud Agents → Self-Driving Codebases** — Agents run in cloud VMs with full developer tooling, execute overnight, and report back like colleagues.

---

### What's Actually Working at Cursor

Not slides — production data:

- **30% of merged PRs** are submitted by cloud agents
- A cloud agent completed a **React → Rust migration (25× perf improvement)** in 8 hours — possible because it could actually run the code, measure latency, and iterate
- **10,000-line PR** implementing network policy controls for sandbox processes

---

### Why Long-Running Agents Break (And the Fix)

Models are RL-trained with trajectory lengths of hundreds of thousands of tokens. Real long-running tasks span millions. This mismatch causes agents to lose context, repeat actions, and fail on details.

**Fix: multi-agent decomposition.** An outer orchestrator stays within a short context window; it fans out work to sub-agents, each handling a task well within training distribution. Cursor's cloud agent uses OpenAI models for high-level planning and Anthropic/Gemini models for computer use and UI work.

---

### Artifacts: Review Intent, Not Code

As agent throughput grows, manual code review stops scaling. Cursor's solution: **reviewable artifacts**.

- After implementing a feature, the agent records a working demo video. Engineers review the video, not the code.
- For ML experiments, agents produce structured research reports.
- Architecture diagrams and change plans come before the diff.

The shift: engineers review what the agent *intended*, then confirm with spot-checks on the code.

---

### Engineer Role in a Self-Driving Codebase

- Write detailed, verifiable **specs** (implementation plan + evaluation suite)
- Review artifacts to confirm correctness
- Handle the edge cases agents genuinely can't solve

*"Software engineering is quickly shifting to async agents that work independently and report back like colleagues."*

---

**Video**: [youtube.com/watch?v=2Fp3jIrFTMo](https://www.youtube.com/watch?v=2Fp3jIrFTMo)  
**Channel**: NVIDIA Developer

© 2026 Author: Mycelium Protocol
