---
title: "三足鼎立：读 Codex Harness、DeepSeek Harness 与 AgentScope 2.0 的横评"
titleEn: "deepseek-harness-everything-plugin-cordis-compare-claude-code-codex"
description: "读后感：社媒横评三款开源 Agent 运行时底座——Codex Harness（OpenAI，Apache-2.0，80+ Rust 子模块）、DeepSeek Harness（MIT，Cordis 微内核，一切皆插件）、AgentScope 2.0（阿里，企业全家桶，国内私有化首选）。原文核心论点：你 Demo 跑得好但生产炸锅，缺的不是更聪明的模型，是 Harness。加上我们的补充分析：三强定位差异、LangGraph 的残余价值、以及国内团队的选型建议。"
descriptionEn: "Reading response: a social media three-way comparison of open-source agent runtime harnesses — Codex Harness (OpenAI, Apache-2.0, 80+ Rust submodules), DeepSeek Harness (MIT, Cordis microkernel, everything-as-plugin), and AgentScope 2.0 (Alibaba, enterprise full-stack, best for Chinese private deployment). Core argument: your demo is great but production breaks — what you're missing isn't a smarter model, it's a Harness. Plus our supplementary analysis: positioning differences, LangGraph's residual value, and selection guidance for Chinese teams."
pubDate: "2026-08-23"
updatedDate: "2026-08-23"
category: "Research"
tags: ["Agent运行时", "Harness", "DeepSeek", "AgentScope", "Codex", "开源", "企业AI", "读后感"]
heroImage: "../../assets/images/deepseek-harness-everything-plugin-cordis-compare-claude-code-codex-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

> **原帖来源**：社交媒体横评文章，对比三款开源 Agent 运行时底座。本文是读后感——对原文核心框架的二次整理，加上我们的补充判断。

---

## 一个扎心场景先说清楚

原文开头戳得很准。你做了一个 Agent，Demo 惊艳全场。一上生产，原形毕露：

- 任务跑到第 18 步，上下文爆了
- 昨天教过它的事，今天全忘了
- 用户一句恶意输入，它把 `rm` 命令直接怼到生产服务器上
- 半夜任务挂了，早上来一看：没有断点、没有日志、没有重试，一切从头再来

**你以为该换个更聪明的模型？错。你缺的是 Harness——智能体运行时底座**。模型只负责"想"，干活的是它底下那套工程系统。

上周 OpenAI 和 DeepSeek 一周内先后开源自家 Harness，加上阿里的 AgentScope，开源 Agent 底座已经三足鼎立。

---

## Harness 的真实工作清单（苦活，不是玄学）

一个生产级 Harness 要兜住五件事：

| 能力 | 作用 |
|------|------|
| **任务循环** | 多步规划、失败重试、断点续跑 |
| **上下文管理** | 自动压缩、超大工具结果落盘只留占位符、防 token 爆炸 |
| **记忆持久化** | 跨会话记住用户偏好和任务进度，不是每次失忆重启 |
| **沙箱与审批** | 命令在隔离环境跑，危险操作必须人工点头 |
| **可观测** | 每个动作可追溯，出事了能回放取证 |

OpenAI 给过一组硬数据：同一个 GPT-5.6，裸奔跑分 13.3%，套上优化过的 Harness 直接拉到 38.3%，token 还省 6 倍。钱省在哪？就省在上下文压缩和推理保留这些工程细节上。

---

## 三强分析

### 选手一：Codex Harness（OpenAI）——出厂调校的整车

- **协议**：Apache-2.0
- **规模**：80+ Rust 子模块，9600+ 次提交，从 2025 年迭代至今，百万级用户生产验证
- **三个核心组件**：
  - `codex exec`：面向 CI 的流水线执行器
  - Codex SDK（TypeScript/Python）：让开发者接入 Codex Agent 能力
  - `app-server`（JSON-RPC）：把 Agent 嵌进业务系统——持久化会话、流式事件、任务中断、自定义工具、人工审批；税务工具集成案例把处理时间砍了 1/3
- **核心定位**：别把工作流硬塞进聊天框，把 AI 装进你的业务系统
- **短板**：深度绑定 OpenAI 模型，数据出境到 OpenAI 云

### 选手二：DeepSeek Harness（dsh）——洞洞板组装底盘

- **协议**：MIT（最宽松）
- **架构**：Cordis 微内核，一切皆插件
- **四种运行模式**：
  - 标准模式（全套工具）
  - 极简模式（仅 Bash + 编辑器）
  - PTC 模式（模型写 TypeScript 程序来完成多步操作）
  - Creation 模式（Agent 在运行时写/加载/卸载插件，自我进化）
- **模型无关**：可以把 Claude Code、Codex 调度为子 Agent
- **对话日志**：append-only，支持 fork/resume/replay
- **定位**：给想自己搭底盘的团队用的原材料

### 选手三：AgentScope 2.0（阿里）——最完整的企业全家桶

- **架构**：分布式部署，OpenTelemetry 埋点，对接 Higress/Nacos 的 MCP 生态
- **核心定位**：国内企业私有化部署的最优解候选，Qwen 生态亲儿子，但也接 DeepSeek、OpenAI 兼容模型
- **多语言支持**：Python / Java / TypeScript / Go（原来的 Workspace 抽象使 AGENTS.md 编辑等于升级 Agent）

---

## 三强速览对比

| 维度 | Codex Harness | DeepSeek Harness | AgentScope 2.0 |
|------|:---:|:---:|:---:|
| 开箱即用 | 🥇 | △ | ○ |
| 灵活度/换模型自由 | △ | 🥇 | ○ |
| 私有化 + 多租户 | △ | ○ | 🥇 |
| 协议宽松度 | Apache | **MIT 🥇** | Apache |

- **开箱即用**：Codex Harness > AgentScope > DeepSeek Harness
- **灵活度**：DeepSeek Harness > AgentScope > Codex Harness
- **私有化 + 多租户**：AgentScope > DeepSeek Harness > Codex Harness
- **协议**：DeepSeek（MIT）> AgentScope、Codex（Apache 系）

---

## LangGraph 们还有价值吗？

原文的判断是：**有价值，但战场换了**。用分层视角看就清楚了：

- **传统框架**（LangGraph / AutoGen / CrewAI）解决的是"多 Agent 怎么编排协作"——图结构、角色分配、消息路由。这个问题没消失
- **Harness** 解决的是"单个 Agent 怎么在生产里活下去"——上下文、记忆、沙箱、可观测性

两层不冲突，但优先级变了：没有稳定的 Harness 底座，LangGraph 编排得再漂亮也是沙上建塔。**先把 Harness 选对，再谈编排层**。

---

## 我们的补充：国内团队选型建议

**优先考虑 AgentScope 2.0 的情况**：
- 数据不能出境（医疗、金融、政务）
- 已在用 Qwen 系列模型
- 需要多租户隔离和 OpenTelemetry 接入现有监控体系

**优先考虑 DeepSeek Harness 的情况**：
- 想自己掌控底层，不接受黑盒
- 需要切换多家模型（DeepSeek / Claude / 本地 Qwen）
- 团队有 Cordis/插件生态经验，或愿意投入工程定制
- MIT 协议有商业授权优势

**优先考虑 Codex Harness 的情况**：
- 主力用 OpenAI 模型，不打算换
- 需要把 Agent 嵌进现有业务系统（app-server JSON-RPC 最省事）
- 看重百万用户生产验证和 9600+ 次提交的工程成熟度

**一句话选型口诀**：出境无所谓 + 用 OpenAI → Codex；不出境 + 用阿里云 → AgentScope；什么都想自己控 → DeepSeek Harness。

---

## 一句话总结

原文验证了这个时代的核心判断：Agent 能力瓶颈不在模型，在 Harness。三家开源底座各有侧重——Codex 是出厂整车、DeepSeek Harness 是原材料底盘、AgentScope 是企业全家桶。选哪个，看你的数据出境容忍度、模型绑定意愿和工程定制能力。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## The Three-Way Harness Race: Codex, DeepSeek, and AgentScope 2.0

*by Mycelium Protocol*

---

> **Source**: A social media comparison post reviewing three open-source agent runtime harnesses. This piece is a reading response — a second-pass synthesis of the original framework, plus our own supplementary analysis.

---

### The Painful Production Scenario

The original post opens with something every agent builder recognizes:

Your agent demo was stunning. Then you shipped it to production:

- Task reached step 18 and the context window exploded
- Knowledge taught yesterday was completely forgotten today
- A single adversarial user input caused an `rm` command to fire on a production server
- A task hung overnight — no checkpoint, no logs, no retry. Start over from scratch

**Think you need a smarter model? Wrong. What you need is a Harness — an agent runtime foundation.** The model handles "thinking." The engineering system underneath handles everything else.

Last week, OpenAI and DeepSeek each open-sourced their Harness within the same week. Add Alibaba's AgentScope, and the open-source agent runtime landscape is now a three-way standoff.

---

### The Harness Job List (Engineering Reality, Not Magic)

A production-grade Harness must handle five things:

| Capability | Function |
|-----------|---------|
| **Task loop** | Multi-step planning, failure retry, checkpoint resume |
| **Context management** | Auto-compression, oversized tool results stored to disk with placeholders, anti-token explosion |
| **Memory persistence** | Cross-session retention of user preferences and task state — not a fresh start every time |
| **Sandbox & approval** | Commands run in isolation; dangerous operations require human sign-off |
| **Observability** | Every action traceable; can replay events to investigate failures |

OpenAI published hard numbers: the same GPT-5.6 scores 13.3% bare, 38.3% with an optimized Harness — and uses 6× fewer tokens. The savings come entirely from context compression and reasoning preservation engineering.

---

### The Three Contenders

#### Codex Harness (OpenAI) — The Factory-Tuned Complete Car

- **License**: Apache-2.0
- **Scale**: 80+ Rust submodules, 9,600+ commits, iterating since 2025, million-user production verified
- **Three core components**:
  - `codex exec`: pipeline runner for CI
  - Codex SDK (TypeScript/Python): developer integration layer
  - `app-server` (JSON-RPC): embed agent in business systems — persistent conversations, streaming events, mid-task interruption, custom tools, human approval; a tax tool integration cut processing time by one-third
- **Positioning**: Don't stuff workflows into a chat box — embed AI inside your business systems
- **Weakness**: Deep OpenAI model lock-in; all data exits to OpenAI cloud

#### DeepSeek Harness (dsh) — The Breadboard Chassis

- **License**: MIT (most permissive)
- **Architecture**: Cordis microkernel, everything-as-plugin
- **Four run modes**:
  - Standard (full tool suite)
  - Minimal (Bash + editor only)
  - PTC mode (model writes TypeScript programs for multi-step operations)
  - Creation mode (agent writes, loads, and unloads plugins at runtime — self-evolution)
- **Model-agnostic**: can schedule Claude Code and Codex as sub-agents
- **Conversation logs**: append-only, supports fork/resume/replay
- **Positioning**: raw material chassis for teams that want to build their own stack

#### AgentScope 2.0 (Alibaba) — The Complete Enterprise Suite

- **Architecture**: distributed deployment, OpenTelemetry instrumentation, MCP ecosystem via Higress/Nacos
- **Positioning**: the leading candidate for enterprise private deployment in China — native to the Qwen ecosystem, but also supports DeepSeek and OpenAI-compatible models
- **Multi-language**: Python / Java / TypeScript / Go (Workspace abstraction means editing AGENTS.md = upgrading the agent)

---

### Head-to-Head Comparison

| Dimension | Codex Harness | DeepSeek Harness | AgentScope 2.0 |
|-----------|:---:|:---:|:---:|
| Out-of-box readiness | 🥇 | △ | ○ |
| Model flexibility | △ | 🥇 | ○ |
| Private deployment + multi-tenant | △ | ○ | 🥇 |
| License permissiveness | Apache | **MIT 🥇** | Apache |

- **Out-of-box**: Codex Harness > AgentScope > DeepSeek Harness
- **Model flexibility**: DeepSeek Harness > AgentScope > Codex Harness
- **Private + multi-tenant**: AgentScope > DeepSeek Harness > Codex Harness
- **License**: DeepSeek (MIT) > AgentScope, Codex (Apache family)

---

### Are LangGraph and Friends Still Relevant?

The original post's verdict: **yes, but the battlefield shifted.** A layered view makes it clear:

- **Traditional frameworks** (LangGraph / AutoGen / CrewAI) answer "how do multiple agents collaborate" — graph structures, role assignment, message routing. That problem hasn't disappeared.
- **Harness** answers "how does a single agent survive in production" — context, memory, sandboxing, observability.

The two layers don't conflict, but priority has shifted: without a stable Harness foundation, LangGraph orchestration on top is a house of cards. **Choose the right Harness first, then worry about orchestration.**

---

### Our Supplement: Selection Guidance

**Choose AgentScope 2.0 if**:
- Data cannot leave the country (healthcare, finance, government)
- You're already on the Qwen model family
- You need multi-tenant isolation and OpenTelemetry integration with existing monitoring

**Choose DeepSeek Harness if**:
- You want full control over the stack with no black boxes
- You need to switch between models (DeepSeek / Claude / local Qwen)
- Your team is comfortable with Cordis/plugin ecosystem investment
- MIT licensing matters for commercial use

**Choose Codex Harness if**:
- OpenAI is your primary model provider and you're not switching
- You need to embed agents inside existing business systems (app-server JSON-RPC is the most turnkey path)
- You value million-user production verification and 9,600+ commits of engineering maturity

**One-line decision rule**: Data egress OK + using OpenAI → Codex. No data egress + Alibaba cloud → AgentScope. Want to control everything yourself → DeepSeek Harness.

---

### One-Sentence Summary

The original post validates the central insight of this era: agent capability bottlenecks aren't in the model — they're in the Harness. The three open-source runtimes each have distinct positioning: Codex is the factory-tuned car, DeepSeek Harness is the raw chassis, AgentScope is the enterprise full-stack. Which to pick depends on your data egress tolerance, model lock-in appetite, and engineering customization capacity.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
