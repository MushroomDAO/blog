---
title: "LifeOS：从「怎么说」到「要什么」——Daniel Miessler 的 AI 生活操作系统"
titleEn: "danielmiessler-lifeos-ai-harness-intent-engineering-current-ideal-state"
description: "danielmiessler/LifeOS，17.5k stars，MIT，TypeScript。fabric 作者 Daniel Miessler 的新项目：一套运行在 AI coding agent 之上的「生活操作系统」。核心命题是从「提示词工程」转向「意图工程」——不是告诉 AI 怎么做，而是捕获你是谁、你想到哪里去，让系统用你的全部上下文驱动 AI 持续爬向你的 Ideal State。22个核心组件，从 TELOS（使命/目标）到 Cortex（跨会话记忆），装一次，伴随一生。"
descriptionEn: "danielmiessler/LifeOS, 17.5k stars, MIT, TypeScript. A new project from fabric creator Daniel Miessler: a 'life operating system' layered on top of AI coding agents. Core premise: move from prompt engineering to intent engineering — not telling AI how to do things, but capturing who you are and where you're trying to go, then letting the system use that full context to keep climbing toward your Ideal State. 22 core components, from TELOS (mission/goals) to Cortex (cross-session memory). Install once, run for life."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["AI", "harness", "意图工程", "生产力", "开源", "TypeScript", "Claude Code", "Mycelium"]
heroImage: "../../assets/images/danielmiessler-lifeos-ai-harness-intent-engineering-current-ideal-state-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Daniel Miessler 是 [fabric](https://github.com/danielmiessler/fabric) 的作者，那是一个收录了 AI 提示模式的开源工具，目前 80,000+ stars。

LifeOS 是他更野心的项目：**一套运行在 AI coding agent 之上的「生活操作系统」**，不是提示词集合，而是基础设施——让 AI 持续、跨会话地理解你是谁、你想去哪里，然后用这个上下文驱动你所有的工作和生活任务。

GitHub: https://github.com/danielmiessler/LifeOS | ⭐ 17,540 | MIT | TypeScript

---

## 核心命题：意图工程

大多数人用 AI 的方式是「提示词工程」：告诉 AI 怎么做某件事。

LifeOS 的命题是**意图工程（Intent Engineering）**：告诉 AI 你最终想要什么——你的使命、你的目标、你对「完成」的定义——然后让系统在每次任务时把这个意图传达给 AI，并验证结果是否符合它。

区别在于：提示词工程要求你每次都重新解释上下文；意图工程要求你一次性捕获上下文，然后系统帮你持续使用它。

LifeOS 的中心概念只有一句话：**把你从 Current State（当前状态）移动到 Ideal State（理想状态）——朝向 Euphoric Surprise（欣喜若狂的惊喜）**。

每一个功能都是为了缩短这段距离。

---

## 安装方式

LifeOS 的安装本身就是一个设计声明：你不执行脚本，**你把安装指令交给 AI**。

```
Read https://ourlifeos.ai/install and install LifeOS for me.
```

把这句话粘贴进你的 AI coding agent（Claude Code、Cursor、Codex），它自己读安装页面，引导整个设置过程，在触碰任何东西之前征求你的许可。

如果你偏好终端：
```bash
curl -fsSL https://ourlifeos.ai/install.sh | bash
```

---

## 22 个核心组件

这不是一个单一功能的工具，而是一个有内在逻辑的组件系统：

### 基础哲学层

**Current → Ideal State**：命名你现在的位置，命名你想去的位置，然后用可检查的步骤填补中间的差距。这是整个系统的操作模型。

**Intent Engineering**：把你最终想要的东西传达给 AI——提示词工程的「WHAT 层」，产品化。

**General Hill Climbing**：每个目标都变成一座山，系统持续选择下一步最能缩小与理想状态距离的行动。

**Euphoric Surprise**：每个回应追求的指标——9分或10分，「这个绝了」的那一刻。这是质量标准，不是比喻。

### 你的核心数据

**TELOS**：你的使命、目标、信念和挑战。LifeOS 通过访谈来捕获它们，然后在每次任务时对照它们推理。TELOS 是系统「知道你是谁」的基础。

**Cortex（记忆）**：LifeOS 知道的所有东西，跨会话复利积累。你不需要每次对话都重新解释自己。

**Synapse（输入路由）**：接收任何输入，评分、路由、永久保存。你扔进去的东西不会丢失，会被分类处理。

**Atlas（资产图谱）**：你拥有的所有东西的实时图谱——API key、账户、凭证。可以查询某个 key 能解锁什么，以及某个单点被攻破会波及哪里。

**Ledger（变更账本）**：所有变更都版本化、记录、可验证——一个地方回答「什么变了、什么时候变的、在哪个版本」。

### 执行层

**The Algorithm**：把模糊的需求转化为可测试的规格，然后爬向它的统一思维系统。

**Arbol（执行层）**：由小型 Unix 风格可组合单元构成——Actions 做一件事，Pipelines 组合它们，Flows 把它们放进调度。

**Bunker（应用脚手架）**：每个应用从一个共享底座获得安全性、正常运行时间监控、测试和部署。

**ISA System**：一个捕获「完成看起来是什么样」的文档——Algorithm 爬向的可测试规格。

### 扩展层

**The Skill System**：自动激活、可组合的专业知识单元库。安装 LifeOS 即获得研究、安全、写作、艺术等一整套 skill。

**The Hook System**：不是好意图，是代码写就的护栏——在固定节点强制执行的规则。

**Pulse**（仪表盘）：你观看系统运行的实时界面。

**Voice**：语音通知——系统主动跟你说话，所以你可以保持专注不被打断。

**Learning**：每次运行都反思自身，把学到的东西喂回系统。

**Security**：由确定性门控（不是假设）执行的隐私和安全。

**Hermes Sidecar**：第二个入口——把 LifeOS 作为 Agent 与之对话；同一个大脑，同样的规则，新的通道（比如通过 WeChat 或 Slack）。

---

## 与直接用 Claude Code 的区别

FAQ 里有一段把这件事说得很清楚：

> "Your harness is the engine. LifeOS is everything else that makes it *your* car."（你的 harness 是引擎。LifeOS 是让它成为*你的*车的所有其他部分。）

具体差异：

| | 裸 harness（Claude Code） | LifeOS on Claude Code |
|---|---|---|
| 记忆 | 每次对话从零开始 | Cortex 跨会话积累 |
| 上下文 | 你每次解释 | TELOS 持续提供 |
| 任务路由 | 手动选工具/提示 | Synapse 自动路由 |
| 质量标准 | 主观判断 | Euphoric Surprise 定义 |
| 自我改进 | 需要手动调整 | Learning 系统自动反馈 |

---

## 与 fabric 的区别

fabric 是「要问 AI 什么」的集合——特定任务的提示模式库。

LifeOS 是「DA（Digital Assistant）如何运作」的基础设施——记忆、skill、路由、上下文、自我改进。它们是互补的：很多 LifeOS 用户把 fabric 的模式集成进 LifeOS 的 skill 里。

---

## 技术实现

LifeOS 是 **harness-agnostic** 的——基于通用原语（hooks、skills、context files、agentic routing）构建，而不是某个供应商的特定功能。代码是 TypeScript 和 Bash。Daniel 在 Claude Code 上构建和运行它（所以这是测试最充分的路径），但整个系统可以移植到任何有能力的 agent 上。

核心概念——TELOS、the Algorithm、skills、memory——会随着 AI agent 技术的演进而演进，而不是绑定在某个特定 harness 的 API 上。

---

## 这件事的意义

人们现在有了非常强大的 AI 工具，但大多数人用它的方式仍然是：每次想起来就打开，输入当前的需求，得到一个回答，然后关掉。AI 知道的只有这次对话。

LifeOS 代表一种不同的使用模式：**AI 作为一个持续运作的 Digital Assistant，而不是一个随用随开的工具**。它积累关于你的知识，它按照你的目标分配注意力，它在你不盯着它的时候也在推进你关心的事情。

17,000+ stars 说明很多人在寻找这个。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## LifeOS: From Prompt Engineering to Intent Engineering

*by Mycelium Protocol*

---

Daniel Miessler is the creator of [fabric](https://github.com/danielmiessler/fabric) — a curated library of AI prompt patterns with 80,000+ stars. LifeOS is his more ambitious project: a **life operating system layered on top of AI coding agents** — not a prompt collection, but infrastructure. A system that persistently understands who you are and where you're trying to go, then uses that full context to drive all your work and life tasks.

GitHub: https://github.com/danielmiessler/LifeOS | ⭐ 17,540 | MIT | TypeScript

---

### The Core Premise: Intent Engineering

Most people use AI through prompt engineering: telling AI how to do something.

LifeOS's premise is **intent engineering**: telling AI what you ultimately want — your mission, your goals, your definition of done — and having the system convey that intent to the AI on every task, then verify the result against it.

The difference: prompt engineering requires you to re-explain context every time. Intent engineering requires you to capture it once, and the system keeps using it.

The central concept: **moving from your Current State to your Ideal State — in pursuit of Euphoric Surprise**. Every feature exists to close that gap.

---

### Installation

The install itself is a design statement. You don't run a script — **you hand the install instruction to your AI**:

```
Read https://ourlifeos.ai/install and install LifeOS for me.
```

Paste that into Claude Code, Cursor, or Codex. The AI reads the install page, walks the setup, and asks permission before touching anything.

Or from terminal:
```bash
curl -fsSL https://ourlifeos.ai/install.sh | bash
```

---

### 22 Core Components

This isn't a single-feature tool. It's a component system with internal logic:

**Philosophy layer:**

- **Current → Ideal State**: Name where you are, name where you want to be, close the gap with checkable steps
- **Intent Engineering**: Convey what you ultimately want — the WHAT layer of prompting, productized
- **General Hill Climbing**: Every goal becomes a hill; the system keeps picking the next move that closes the gap
- **Euphoric Surprise**: The 9 or 10, the "this is brilliant" moment — a quality standard, not a metaphor

**Your core data:**

- **TELOS**: Your mission, goals, beliefs, and challenges — captured via interview, reasoned against on every task
- **Cortex**: Everything LifeOS knows, compounding across sessions. You never re-explain yourself
- **Synapse**: Input router — catches anything, grades it, routes it, keeps it forever
- **Atlas**: A live graph of everything you own — API keys, accounts, credentials — with blast-radius queries
- **Ledger**: Every change versioned, recorded, and verified — one place answers what changed, when, at what version

**Execution layer:**

- **The Algorithm**: Turns a vague ask into a testable spec and climbs toward it
- **Arbol**: Actions do one thing, Pipelines compose them, Flows schedule them
- **Bunker**: Every app built on LifeOS gets security, uptime, testing, and deployment from one chassis
- **ISA System**: The testable "done" document the Algorithm climbs toward

**Extension layer:**

- **Skill System**: Self-activating, composable expertise units — research, security, writing, art, and more
- **Hook System**: Guardrails that are code, not good intentions — enforced at fixed points
- **Pulse**: The live dashboard where you watch the system run
- **Voice**: Spoken notifications so you stay in flow
- **Learning**: Every run reflects on itself and feeds what it learned back in
- **Security**: Privacy and safety enforced by deterministic gates, not assumptions
- **Hermes Sidecar**: A second front door — talk to your LifeOS as an agent through any channel

---

### How It Differs from a Raw Harness

From the FAQ:

> "Your harness is the engine. LifeOS is everything else that makes it *your* car."

| | Raw harness (Claude Code) | LifeOS on Claude Code |
|---|---|---|
| Memory | Resets every session | Cortex accumulates across sessions |
| Context | You re-explain every time | TELOS persists |
| Task routing | Manual selection | Synapse auto-routes |
| Quality bar | Subjective | Euphoric Surprise defined |
| Self-improvement | Manual tuning | Learning system feeds back |

---

### How It Differs from fabric

fabric is "what to ask AI" — a library of specific-task prompt patterns.

LifeOS is "how your DA operates" — memory, skills, routing, context, self-improvement. They're complementary: many LifeOS users integrate fabric patterns into LifeOS skills.

---

### The Idea Worth Paying Attention To

Most people use AI the same way: open it when you remember, type the current need, get an answer, close it. The AI knows only this conversation.

LifeOS represents a different mode: **AI as a continuously operating Digital Assistant, not an on-demand tool**. It accumulates knowledge about you. It allocates attention according to your goals. It keeps advancing what you care about even when you're not watching.

17,000+ stars suggests a lot of people are looking for exactly this.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
