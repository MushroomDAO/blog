---
title: "Paperclip：3 个月 69,462 star，匿名创始人，Zero Human Companies 到底是什么"
description: "paperclipai/paperclip 深度调研：不是 Agent 框架，不是工作流构建器，是 AI Agent 团队的组织基础设施——带组织架构图、预算管控、治理审批的公司操作系统。一条命令上手，TypeScript MIT 开源。"
titleEn: "Paperclip: 69,462 Stars in 3 Months, Anonymous Founder — What 'Zero Human Companies' Actually Means"
descriptionEn: "Deep dive into paperclipai/paperclip: not an agent framework, not a workflow builder — it's organizational infrastructure for teams of AI agents: org charts, budgets, governance, goal alignment. One command to start. TypeScript, MIT open source."
pubDate: 2026-06-07
category: "Tech-News"
tags: ["AI Agent", "Zero Human Companies", "Paperclip", "开源", "多智能体", "Agent 编排", "TypeScript"]
lang: "zh-CN"
heroImage: "../../assets/images/paperclip-zero-human-companies-banner.jpg"
---

没有大厂背书。没有融资新闻。没有 KOL 车轮战推广。创始人接受采访全程用 AI Animoji 形象出镜，从不露脸。

这个项目叫 **Paperclip**（`paperclipai/paperclip`）。

从 2026 年 3 月 2 日创建，到今天，**69,462 个 GitHub Star**，12,891 Fork，3 个月。

这不是营销数字，这是开发者用脚投票的结果。

---

## 先说清楚它是什么，以及它不是什么

README 开头第一句：

> **"If OpenClaw is an _employee_, Paperclip is the _company_."**

这一句话把 Paperclip 的定位说清楚了。它不是又一个 AI Agent，不是又一个框架。它是**管理 AI Agent 团队的公司操作系统**。

README 明确列出了 Paperclip **不是**什么：

| 不是 | 原因 |
|------|------|
| 不是聊天机器人 | Agent 有工作，没有聊天窗口 |
| 不是 Agent 框架 | 不告诉你怎么构建 Agent，告诉你怎么运营一家 Agent 公司 |
| 不是工作流构建器 | 没有拖拽 Pipeline |
| 不是 Prompt 管理工具 | Agent 自带 Prompt、模型、运行时 |
| 不是单 Agent 工具 | 为 20+ 个 Agent 设计，不是一个 |
| 不是代码审查工具 | 协调工作，不是审查 PR |

---

## Zero Human Companies：三步跑一家 AI 公司

Paperclip 的工作流是这样的：

```
01 定义目标
   "Build the #1 AI note-taking app to $1M MRR."
   
02 雇佣团队
   CEO、CTO、工程师、设计师、市场人员
   任何 bot，任何模型供应商

03 审批并启动
   审阅策略。设定预算。点击运行。从 Dashboard 监控。
```

你不再是在"提示一个 AI"，你在"管理一个团队"。

这个概念有多认真？社区已经有人写了一本开源书叫 **《Headcount Zero》**，专门探讨零人类公司的商业模式。

---

## 技术架构：12 个子系统

Paperclip 是一个 **Node.js 服务器 + React UI**，内置 12 个互相协调的子系统：

### 1. Identity & Access（身份与访问）
两种模式：本地环回信任模式（最快）+ 认证模式。支持董事会用户、Agent API Key、短期运行 JWT、公司成员管理、邀请流程。

### 2. Work & Task System（工作与任务系统）
Issue 携带公司/项目/目标/父级完整链路，原子检出 + 执行锁，一等公民的依赖阻塞关系，评论、文档、附件、标签、收件箱状态。

**关键**：两个 Agent 不可能同时领到同一个任务——原子锁保证。这个在竞品里很少见。

### 3. Heartbeat Execution（心跳执行）
数据库驱动的唤醒队列，含预算检查、工作区解析、Secret 注入、Skill 加载、Adapter 调用。孤立运行自动恢复。

心跳机制意味着：Agent 不是在长进程里阻塞等待，而是"完成一步 → 交回控制权 → 下次心跳继续"，可以在任意节点暂停、审批、恢复。

### 4. Workspaces & Runtime（工作区与运行时）
项目工作区 + 隔离执行工作区（Git Worktree + Operator Branch），支持运行时服务（开发服务器、预览 URL）。

### 5. Governance & Approvals（治理与审批）
董事会审批工作流，含审查/批准多阶段的执行策略，预算硬停止，Agent 暂停/恢复/终止，完整审计日志。

这是 Paperclip 最有意思的设计之一：**人类在流程里的角色从"执行者"变成"审批者"**。

### 6. Budget & Cost Control（预算与成本控制）
按公司/Agent/项目/目标/Issue/供应商/模型分层追踪 Token 和成本。有阈值警告和硬停止。

没有这个，多 Agent 系统会烧掉你的 API 余额。

### 7. Routines & Schedules（例程与调度）
定时任务，支持 Cron、Webhook、API 触发。含并发策略和补跑策略。

### 8. Plugins（插件）
进程外 Worker，能力门控的宿主服务，Job 调度，工具暴露，UI 贡献。不 Fork 主项目可扩展。

### 9. Secrets & Storage（密钥与存储）
实例级和公司级 Secret，加密本地存储，供应商支持的对象存储。

### 10. Company Portability（公司可移植性）
整个组织（含 Scrubbed Secret）的导出/导入，冲突处理。

### 11. Activity & Events（活动与事件）
实时活动流，完整的事件溯源。

### 12. Org Chart & Agents（组织架构与 Agent）
真正的组织架构图，Agent 有职位、汇报关系、职责范围。

---

## 支持的 Agent 类型

**"只要能接收心跳，就能被雇佣。"**

| Agent | 备注 |
|-------|------|
| **OpenClaw** | 主推，深度集成 |
| **Claude Code** | 内置 Adapter |
| **Codex**（OpenAI） | 内置 Adapter |
| **Cursor** | 支持 |
| **Bash 脚本** | CLI 任何命令 |
| **HTTP Webhook** | 任意 REST 服务 |

---

## 快速上手：一条命令

```bash
# 最快启动方式
npx paperclipai onboard --yes

# 局域网访问
npx paperclipai onboard --yes --bind lan

# Tailscale VPN 访问
npx paperclipai onboard --yes --bind tailnet
```

**系统要求**：Node.js 20+，pnpm 9.15+

API 服务启动在 `http://localhost:3100`，内嵌 PostgreSQL 自动创建，无需手动配置数据库。

**手动开发模式：**

```bash
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev          # API + UI 完整开发模式（文件监听）
pnpm dev:server   # 仅服务端
```

**关闭遥测：**

```bash
PAPERCLIP_TELEMETRY_DISABLED=1 npx paperclipai onboard --yes
# 或
DO_NOT_TRACK=1 ...
```

---

## 与竞品的核心差异

| 工具 | 定位 | vs. Paperclip |
|------|------|---------------|
| **AutoGPT** | 单一自主 Agent，自我分配任务循环 | AutoGPT 是一个工人；Paperclip 是雇用和管理工人的公司 |
| **CrewAI** | Python 框架，用代码定义角色团队 | CrewAI 在代码里定义 crew；Paperclip 在运行时管理有组织架构/预算/治理的团队，无需写代码配置 |
| **LangGraph** | 基于状态机图的多 Agent 工作流 | 图定义 vs. 公司/组织隐喻，带持久状态 |
| **n8n / Zapier** | 拖拽 Pipeline 工作流自动化 | Paperclip 明确拒绝"工作流构建器"定位，它建模的是公司，不是 Pipeline |

**Paperclip 声称竞品缺少的东西**：

- 原子任务检出（两个 Agent 不会同时领到同一任务）
- 跨心跳持久会话状态（Agent 重启后从断点继续，不是从头开始）
- 真正的成本监控（不是事后统计，是实时预算门控）
- 带回滚的治理（审批门控，配置变更有版本历史）

---

## 插件生态（已有 15 个社区插件）

社区整理了 `awesome-paperclip` 列表，包括：

| 插件 | 功能 |
|------|------|
| paperclip-plugin-hindsight | Agent 持久长期记忆 |
| paperclip-plugin-github-issues | GitHub Issues 同步 |
| paperclip-plugin-linear | Linear 工作区集成 |
| paperclip-plugin-slack/discord/telegram | 双向通知 |
| paperclip-mcp | Claude Code MCP Server 集成 |
| obsidian-paperclip | Obsidian 中管理 Issue |
| paperclip-plugin-avp | Agent 信任与声誉层 |

---

## 路线图里最有意思的几个

**已上线**：Plugin 系统、公司 Export/Import、Scheduled Routines、预算管控、多人类用户

**即将推出**：
- **MAXIMIZER MODE**（全大写，不知道是什么，但开发团队显然认为很重要）
- CEO Chat（自然语言直接管理公司）
- Memory / Knowledge（Agent 记忆系统）
- Self-Organization（自组织）
- Automatic Organizational Learning（组织自动学习）
- Cloud deployments + Desktop App

---

## 数字背后的现象

**69,462 star，3 个月，TypeScript，MIT，无融资，创始人匿名。**

这个增长曲线很不寻常。没有大 V 推广，没有 Product Hunt 头条，靠的是开发者口碑在技术社区扩散。截图里的 star 曲线是陡峭的 S 型上升，3 月底出现一次跳跃（大概是某次 HN 热帖），之后保持高速增长。

**为什么这个概念引起这么大的共鸣？**

可能是因为它说出了很多人对 AI Agent 的真实期望——不是"一个更聪明的助手"，而是"一个能替我把事情做完的团队"。从提示一个 AI，到管理一家公司，这个认知跳跃很大，但 Paperclip 给出了一个具体的系统框架，让这个想象变得可操作。

---

## 我的判断

**理念超前，但现在就能用。**

Paperclip 做的是真正难的事情：多 Agent 协调不是把几个 AI 调用串起来，而是要处理原子性、持久状态、成本控制、审批治理——这些都是分布式系统级别的问题。它把这些问题包装成"管理一家公司"的直觉模型，这个产品思路很高明。

**现实的局限**：

- 还在早期（3 个月，v2026.529.0），生产稳定性需要观察
- MAXIMIZER MODE 这类路线图项还只是承诺，不是现实
- 需要自己的 LLM API Key，成本取决于你雇了多少 Agent 干了多少活
- "Zero Human Companies" 是愿景，不是今天就能实现的

**但以下场景今天就能用**：

- 跨多个 Agent 并行推进一个软件项目（不同 Agent 负责不同模块）
- 需要人工审批节点的自动化工作流
- 想对 AI 工作成本有真实可见的监控和上限控制
- 想让 Claude Code / Codex 等 Agent 有持久的任务状态，重启不丢进度

---

**GitHub**: paperclipai/paperclip（69,462 star）  
**官网**: paperclip.ing  
**文档**: docs.paperclip.ing  
**Discord**: discord.gg/m4HZY7xNG3  
**Twitter**: @papercliping

<!--EN-->

## Paperclip: 69,462 Stars in 3 Months, Anonymous Founder — What "Zero Human Companies" Actually Means

No big company backing. No funding news. No KOL promotion carousel. The founder does interviews as an AI Animoji avatar, never showing their face.

The project is called **Paperclip** (`paperclipai/paperclip`).

Since its creation on March 2, 2026: **69,462 GitHub stars**, 12,891 forks. Three months.

These aren't marketing numbers. Developers voted with their feet.

---

## What It Is — and What It Isn't

The first line of the README:

> **"If OpenClaw is an _employee_, Paperclip is the _company_."**

One sentence makes the positioning clear. It's not another AI agent. It's not another framework. It's **a company operating system for managing teams of AI agents**.

What Paperclip explicitly is NOT (from the README):

| Not this | Because |
|----------|---------|
| Not a chatbot | Agents have jobs, not chat windows |
| Not an agent framework | Doesn't tell you how to build agents — tells you how to run a company of them |
| Not a workflow builder | No drag-and-drop pipelines |
| Not a prompt manager | Agents bring their own prompts, models, runtimes |
| Not a single-agent tool | Designed for 20+ agents, not one |
| Not a code review tool | Orchestrates work, doesn't review PRs |

---

## Zero Human Companies: Three Steps to Run an AI Company

The Paperclip workflow:

```
01 Define the goal
   "Build the #1 AI note-taking app to $1M MRR."
   
02 Hire the team
   CEO, CTO, engineers, designers, marketers
   Any bot, any provider.

03 Approve and run
   Review strategy. Set budgets. Hit go. Monitor from the dashboard.
```

You're no longer "prompting an AI." You're "managing a team."

How serious is this concept? The community has already written an open-source book called **"Headcount Zero"** exploring zero-human-company business models.

---

## Technical Architecture: 12 Subsystems

Paperclip is a **Node.js server + React UI** with 12 coordinated subsystems:

**Identity & Access** — Two modes: trusted local loopback (fastest) or authenticated. Board users, agent API keys, short-lived run JWTs, company memberships, invite flows.

**Work & Task System** — Issues carry full company/project/goal/parent chain, atomic checkout with execution locks, first-class blocker dependencies, comments, documents, attachments, labels, inbox state. **Critical**: atomic locking means no two agents can simultaneously claim the same task — rare in competing tools.

**Heartbeat Execution** — DB-backed wakeup queue with budget checks, workspace resolution, secret injection, skill loading, adapter invocation. Orphaned runs auto-recover. Agents don't block in a long process — they complete a step, yield control, and continue on next heartbeat. Any step can be paused, approved, and resumed.

**Workspaces & Runtime** — Project workspaces + isolated execution workspaces (git worktrees, operator branches), runtime services (dev servers, preview URLs).

**Governance & Approvals** — Board approval workflows, multi-stage execution policies, budget hard-stops, agent pause/resume/terminate, full audit log. **The key design**: humans shift from "executor" to "approver."

**Budget & Cost Control** — Token and cost tracking by company/agent/project/goal/issue/provider/model. Warning thresholds and hard stops. Without this, multi-agent systems will drain your API balance.

**Routines & Schedules** — Recurring tasks with cron, webhook, and API triggers. Concurrency and catch-up policies.

**Plugins** — Out-of-process workers, capability-gated host services, UI contributions. Extend without forking.

**Secrets & Storage** — Instance and company secrets, encrypted local storage, provider-backed object storage.

**Company Portability** — Export/import entire orgs with secret scrubbing and collision handling.

**Activity & Events** — Real-time activity stream, full event sourcing.

**Org Chart & Agents** — Real org charts: agents have titles, reporting relationships, responsibility scopes.

---

## Supported Agent Types

**"If it can receive a heartbeat, it's hired."**

| Agent | Notes |
|-------|-------|
| **OpenClaw** | Primary, deep integration |
| **Claude Code** | Built-in adapter |
| **Codex** (OpenAI) | Built-in adapter |
| **Cursor** | Supported |
| **Bash scripts** | Any CLI command |
| **HTTP/Webhook** | Any REST service |

---

## Quick Start: One Command

```bash
# Fastest start
npx paperclipai onboard --yes

# LAN access
npx paperclipai onboard --yes --bind lan

# Tailscale VPN
npx paperclipai onboard --yes --bind tailnet
```

**Requirements**: Node.js 20+, pnpm 9.15+

API server at `http://localhost:3100`. Embedded PostgreSQL auto-created — no manual database setup.

**Manual dev mode:**

```bash
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev       # Full dev (API + UI, watch mode)
```

**Disable telemetry:**

```bash
PAPERCLIP_TELEMETRY_DISABLED=1 npx paperclipai onboard --yes
```

---

## How It Differs from Competitors

| Tool | What It Is | vs. Paperclip |
|------|------------|---------------|
| **AutoGPT** | Single autonomous agent in a self-tasking loop | AutoGPT is one worker; Paperclip is the company that manages workers |
| **CrewAI** | Python framework, role-based agent teams defined in code | CrewAI defines crews in code; Paperclip manages teams at runtime — no code needed for org configuration |
| **LangGraph** | State-machine graph for multi-agent workflows | Graph-based workflow definition vs. company/org metaphor with persistent state |
| **n8n / Zapier** | Drag-and-drop pipeline workflow automation | Paperclip explicitly rejects the "workflow builder" frame — it models companies, not pipelines |

**What Paperclip claims competitors miss:**
- Atomic task checkout (no two agents work the same task simultaneously)
- Persistent session state across heartbeats (agents resume from breakpoints, not from scratch)
- Real cost monitoring (runtime budget gates, not post-hoc statistics)
- Governance with rollback (approval gates, versioned config changes)

---

## Community Plugin Ecosystem

15 community plugins in the `awesome-paperclip` list:

| Plugin | Function |
|--------|----------|
| paperclip-plugin-hindsight | Persistent long-term memory for agents |
| paperclip-plugin-github-issues | GitHub Issues sync |
| paperclip-plugin-linear | Linear workspace integration |
| paperclip-plugin-slack/discord/telegram | Bidirectional notifications |
| paperclip-mcp | Claude Code integration via MCP Server |
| obsidian-paperclip | Manage issues from Obsidian |
| paperclip-plugin-avp | Agent trust and reputation layer |

---

## Most Interesting Roadmap Items

**Already shipped:** Plugin system, company export/import, Scheduled Routines, budget control, multi-human users

**Coming next:**
- **MAXIMIZER MODE** (all caps — the team clearly thinks this is significant)
- CEO Chat (natural language company management)
- Memory / Knowledge (agent memory system)
- Self-Organization
- Automatic Organizational Learning
- Cloud deployments + Desktop App

---

## The Phenomenon Behind the Numbers

**69,462 stars, 3 months, TypeScript, MIT, no funding, anonymous founder.**

This growth curve is unusual. No influencer push, no Product Hunt headline. Pure developer word-of-mouth. The star history shows a steep S-curve with a jump around late March (probably an HN frontpage hit) followed by sustained high-velocity growth.

**Why does this concept resonate so strongly?**

Probably because it articulates what many people actually want from AI agents — not "a smarter assistant," but "a team that gets things done." The jump from "prompting an AI" to "managing a company" is a big cognitive leap, but Paperclip provides a concrete system framework that makes the vision operationally real.

---

## My Assessment

**Conceptually ahead of the field. Practically usable today.**

Paperclip tackles genuinely hard problems: multi-agent coordination isn't just chaining API calls — it requires atomicity, persistent state, cost control, and approval governance. These are distributed-systems-level challenges. Wrapping them in the intuitive "running a company" model is smart product design.

**Current limitations:**
- Three months old (v2026.529.0) — production stability still accumulating
- MAXIMIZER MODE and other roadmap items are promises, not shipped features
- Requires your own LLM API keys — cost scales with how many agents you run
- "Zero Human Companies" is a vision, not today's reality

**What works today:**
- Running multiple agents in parallel on a software project, each owning different modules
- Automated workflows that require human approval gates
- Real visibility and hard caps on AI work costs
- Persistent task state for Claude Code / Codex — progress survives restarts

---

**GitHub**: paperclipai/paperclip (69,462 stars)  
**Website**: paperclip.ing  
**Docs**: docs.paperclip.ing  
**Discord**: discord.gg/m4HZY7xNG3  
**Twitter**: @papercliping
