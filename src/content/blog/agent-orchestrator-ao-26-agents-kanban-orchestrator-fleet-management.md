---
title: "Agent Orchestrator（AO）：26 个编程 Agent 统一管理，榨干 Claude Code/Codex/Cursor 的实战指南"
titleEn: "agent-orchestrator-ao-26-agents-kanban-orchestrator-fleet-management"
description: "Agent Orchestrator（GitHub: Untrivial-ai/agent-orchestrator，⭐10,439，Apache-2.0）是一个本地桌面 IDE，把 Claude Code、Codex、Cursor 等 26 个编程 Agent 统一放进一个 Kanban 看板管理。每个任务有独立 Worker（独立 branch + worktree）、项目级 Orchestrator 负责规划和拆解任务、实时 Kanban 跟踪 PR/CI/Review 状态、Agent 可控独立浏览器。从想法到 merge 的完整工作流，一个地方搞定。"
descriptionEn: "Agent Orchestrator (GitHub: Untrivial-ai/agent-orchestrator, ⭐10,439, Apache-2.0) is a local desktop IDE that manages Claude Code, Codex, Cursor, and 26 other coding agents in one unified Kanban workspace. Each task gets its own Worker (isolated branch + worktree), a project-level Orchestrator handles planning and task decomposition, live Kanban tracks PR/CI/review state, and each worker gets its own agent-controlled browser. Full workflow from idea to merge, one place."
pubDate: "2026-08-29"
updatedDate: "2026-08-29"
category: "Tech-News"
tags: ["Agent管理", "Claude Code", "Codex", "多Agent", "Kanban", "开发工具", "AO", "榨干软件"]
heroImage: "../../assets/images/agent-orchestrator-ao-26-agents-kanban-orchestrator-fleet-management-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/Untrivial-ai/agent-orchestrator | ⭐ 10,439 | Apache-2.0  
官网：https://aoagents.dev | 文档：https://aoagents.dev/docs  
最新版：v0.12.10-nightly（2026-08-29）| 平台：macOS / Windows / Linux  
支持 Agent 数：**26 个**

---

## 你的 Claude Code 在白白浪费产能

你可能有 Claude Code、Codex、Cursor 三个 agent 的订阅。但你现在的用法是：一次只开一个，等它做完，然后开下一个任务。

这不叫用 AI 工作，这叫给 AI 当助理。

**Agent Orchestrator（AO）的设计目标是反过来：你管项目方向，AI 舰队管执行。**

一个 Orchestrator 把大任务拆成小任务，每个小任务分配一个 Worker（Claude Code、Codex 或任意 agent），每个 Worker 有自己的 branch、worktree、浏览器，同时跑。你坐在一个 Kanban 看板前，关注那些卡在"等你"状态的任务。

---

## 核心概念：三层结构

### 1. Worker（执行层）

一个 Worker = 一个任务 + 一个 Agent + 一个独立工作空间。

Git-backed 任务：Worker 自动拿一个独立 branch 和 worktree，不和其他 Worker 冲突。
Scratch 任务：AO 管理无 branch 的临时目录。

从创建到 merge 的全程，Worker 维护：
- 任务描述和对话（Chat 模式 或 Agent 原生 TUI）
- 变更文件 diff
- Pull Request 状态
- CI 运行状态
- Review 反馈

每个 Worker 完全独立——对话上下文不混，文件不冲，branch 不撞。

### 2. Orchestrator（规划层）

Orchestrator 是项目级的持久规划 Agent，工作在 Worker 上面一层。

它的职责：
- 探索想法、分析 tradeoff、制定技术路线
- 把模糊的目标拆成可执行的具体任务
- 主动 spawn Worker，给每个 Worker 分配正确的上下文
- 跟踪 Worker 进度，协调后续工作
- 综合 repository 上下文 + 所有 Worker 当前状态

**Orchestrator 管规划和分配，Worker 管实现、测试、commit 和 PR。**

### 3. Kanban（可见性层）

所有 Worker 出现在同一张实时看板上，AO 从 session/PR/CI/Review 事实自动推导每张卡的位置：

| 列 | 含义 |
|---|---|
| **Working** | 正在实现，或等待下一条指令 |
| **Needs you** | 被阻塞：缺少输入、CI 失败、Review 要求修改、信号丢失 |
| **In review** | PR 已开，等待检查或 review |
| **Ready to merge** | 已批准或可合并，merged 后保留可见直到归档 |

看板告诉你：什么在推进，什么被卡住，你的注意力放哪里效果最大。

---

## 实战：如何用 AO 榨干你的 Agent 订阅

### 场景 1：并行处理 Sprint 任务清单

```
以前：打开 Claude Code → 做 bug A → 等 → 做 bug B → 等...
现在：
  1. 打开 Orchestrator
  2. 粘入本次 Sprint 的 10 个 issue
  3. Orchestrator 拆解并批量 spawn Worker
  4. 10 个 Worker 同时跑，你去喝咖啡
  5. 回来看 Kanban：4 个 Ready to merge，3 个 In review，2 个 Needs you（CI 失败）
  6. 逐一处理 Needs you：点进去看 CI 错误，发给同一个 Worker 修复
  7. PR 全部 merge，sprint 完成
```

**关键收益**：等待时间从串联变并联，同样 4 小时里完成的任务量线性增长。

### 场景 2：让不同 Agent 竞争同一任务

```
1. 用 Claude Code 建 Worker A：实现新功能方案 A
2. 用 Codex 建 Worker B：实现同一功能的方案 B
3. 两个 Worker 同时运行
4. 在 Kanban 里对比两个 PR 的 diff
5. 选更好的 merge，关掉另一个 worktree
```

适用于：不确定技术方案、想 A/B 测试实现质量的场景。

### 场景 3：把 Review 反馈喂回原 Worker

CI 失败或 reviewer 留了 requested changes？

```
1. 在 Kanban 找到 "Needs you" 状态的 Worker
2. 点进去：PR summary + CI 日志 + review comments 全在旁边
3. 把 CI 错误或 review 意见直接发回给同一个 Worker
4. Worker 接着修，不需要重建上下文
```

**这是 AO 和单独开 terminal 的最大差别**：上下文不会断。

### 场景 4：用 Orchestrator 从 0 到 1 规划新功能

```
你：@Orchestrator 我们要给 API 加速率限制，支持按 user/org 分级，
    可以绕过 Redis，要兼容现有的中间件，给我一个分解后的实施计划

Orchestrator：（分析 repo context → 给出 5 个子任务）
  - Task 1: 设计速率限制数据结构（Worker: Claude Code）
  - Task 2: 实现内存存储后端（Worker: Codex）
  - Task 3: 集成现有 auth 中间件（Worker: Claude Code）
  - Task 4: 写单元测试（Worker: Codex）
  - Task 5: 更新 API 文档（Worker: Claude Code）

你确认后，Orchestrator spawn 5 个 Worker，同时开跑
```

### 场景 5：UI 任务用隔离浏览器

每个 Worker 有**独立的浏览器**（browser profiles 相互隔离），Agent 可以控制它：

```
Worker A：改登录页面 → 在 AO 内置浏览器预览 localhost:3000/login
Worker B：改仪表盘 → 在另一个隔离浏览器预览 localhost:3001/dashboard
```

两个 UI 任务并行，浏览器状态（cookies、登录态）不互相污染。

---

## 支持的 26 个 Agent

| Agent | | Agent | | Agent |
|-------|---|-------|---|-------|
| Claude Code | | Codex | | Cursor |
| opencode | | Aider | | GitHub Copilot |
| Grok | | Kimi | | Pi |
| Amp | | Auggie | | Droid |
| Crush | | Cline | | Goose |
| Qwen | | Continue | | Devin |
| …以及更多 | | | | |

每个 Agent 使用它自己的原生 TUI 或 Chat 模式运行，AO 在外层提供统一的任务上下文、工作空间管理和 Kanban 可见性。

---

## 安装（5分钟上手）

直接下载桌面应用，无需 CLI：

| 平台 | 下载 |
|------|------|
| macOS Apple Silicon | [DMG](https://github.com/Untrivial-ai/agent-orchestrator/releases/latest/download/agent-orchestrator-darwin-arm64.dmg) |
| macOS Intel | [DMG](https://github.com/Untrivial-ai/agent-orchestrator/releases/latest/download/agent-orchestrator-darwin-x64.dmg) |
| Windows | [EXE](https://github.com/Untrivial-ai/agent-orchestrator/releases/latest/download/agent-orchestrator-win32-x64.exe) |
| Linux (Debian/Ubuntu) | [DEB](https://github.com/Untrivial-ai/agent-orchestrator/releases/latest/download/agent-orchestrator-linux-x64.deb) |
| Linux (AppImage) | [AppImage](https://github.com/Untrivial-ai/agent-orchestrator/releases/latest/download/agent-orchestrator-linux-x64.AppImage) |

```
1. 下载并安装
2. 打开 AO，点 "Add repository"，选你的 git 仓库
3. 点 "New task"，描述任务，选 Agent（Claude Code / Codex / 任意）
4. Worker 启动，出现在 Kanban 的 Working 列
```

---

## AO vs. Superset：两个定位不同的产品

*（Superset 也是我们之前写过的类似定位产品）*

| | Agent Orchestrator | Superset |
|---|---|---|
| 核心差异点 | **项目级 Orchestrator** 负责规划和任务分配 | 并行 worktree 执行 |
| Kanban | ✅ 全生命周期跟踪 PR/CI/Review | ❌ 无 |
| 规划 Agent | ✅ 项目级 Orchestrator | ❌ 无 |
| 支持 Agent 数 | 26 | 20+ |
| 浏览器隔离 | ✅ 每 Worker 独立 browser profile | ✅ 内置浏览器 |
| 平台 | macOS / Windows / Linux | macOS（主要）+ Linux 实验性 |
| 价格 | 免费（Apache-2.0） | 免费 + Pro 付费 |
| 定位 | 项目管理 + Agent 舰队调度 | 并行 Agent 执行 + 自动化 |

**一句话区别：** Superset 是"并行跑 Agent 的调度器"，AO 是"带规划能力的 Agent 项目管理工具"。

---

## 一点点透明度问题

AO 的遥测收集：函数名、版本、OS、以及 GitHub 仓库的 **owner 字段**（个人仓库等于用户名，不匿名）。

关闭遥测：目前无官方关闭文档（`docs/telemetry.md` 提到了但没给具体环境变量）。如果数据隐私很重要，建议阅读[遥测文档](https://github.com/Untrivial-ai/agent-orchestrator/blob/main/docs/telemetry.md)后再决定。

---

## 链接

- GitHub：https://github.com/Untrivial-ai/agent-orchestrator
- 官网文档：https://aoagents.dev/docs
- Discord：https://discord.com/invite/UZv7JjxbwG
- Twitter：https://x.com/aoagents

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

<!--EN-->

## Agent Orchestrator (AO): Manage 26 Coding Agents from One Kanban — A Practical Guide to Maxing Out Claude Code and Codex

*by Mycelium Protocol*

---

GitHub: https://github.com/Untrivial-ai/agent-orchestrator | ⭐ 10,439 | Apache-2.0  
Website: https://aoagents.dev | Docs: https://aoagents.dev/docs  
Latest: v0.12.10-nightly (2026-08-29) | Platforms: macOS / Windows / Linux  
Supported agents: **26**

---

### Your Claude Code Subscription Is Underutilized

You probably have Claude Code, Codex, and Cursor subscriptions. But you're likely using them one at a time: open one, wait for it to finish, start the next task.

That's not AI-assisted work — that's you being the AI's assistant.

**Agent Orchestrator (AO) is designed to reverse this: you manage project direction, an AI fleet manages execution.**

A project Orchestrator breaks large goals into focused tasks, each task gets a Worker (Claude Code, Codex, or any agent), each Worker runs in its own branch and worktree simultaneously. You watch a Kanban board and attend only to the things blocked on you.

---

### Three-Layer Architecture

**1. Worker (Execution layer)**

One Worker = one task + one agent + one isolated workspace.

Git-backed workers get their own branch and worktree — no collisions. From creation to merge, the Worker carries: task description and conversation, file diffs, pull request state, CI run state, and review feedback. Context doesn't bleed between workers.

**2. Orchestrator (Planning layer)**

The project Orchestrator is a persistent planning agent working one level above Workers. It:
- Explores ideas, reasons through tradeoffs, sets technical direction
- Breaks ambiguous goals into concrete, focused tasks
- Spawns or redirects Workers with relevant context
- Tracks Worker progress and coordinates follow-up work
- Combines repository context with live AO state (active workers, PRs, CI, reviews)

**Orchestrator owns planning and delegation. Workers own implementation, tests, commits, and PRs.**

**3. Kanban (Visibility layer)**

AO derives each card's position from session, PR, CI, and review facts — no manual drag-and-drop:

| Column | Meaning |
|--------|---------|
| **Working** | Actively implementing or ready for next instruction |
| **Needs you** | Blocked: missing input, failed CI, requested changes, lost signal |
| **In review** | PR open, waiting on checks or review |
| **Ready to merge** | Approved or mergeable; merged sessions stay visible until archived |

The board shows what's moving, what's blocked, and where your attention has the most leverage.

---

### Practical Guide: How to Max Out Your Agent Subscriptions

**Pattern 1: Parallel sprint task execution**

```
Before: Open Claude Code → wait → finish → open next task → wait...

Now:
  1. Open Orchestrator, paste your 10 sprint issues
  2. Orchestrator decomposes and spawns 10 Workers simultaneously
  3. All 10 run in parallel while you do other things
  4. Come back to Kanban: 4 Ready to merge, 3 In review, 2 Needs you (CI failures)
  5. Handle Needs you: click in, read CI error, send it back to the same Worker
  6. All PRs merged — sprint done
```

**Pattern 2: A/B compete two implementations**

```
Worker A (Claude Code): implement feature using approach A
Worker B (Codex): implement same feature using approach B
Both run simultaneously → compare diffs → merge the winner
```

**Pattern 3: Close the CI/review feedback loop**

When CI fails or a reviewer leaves requested changes:
1. Find the "Needs you" card on Kanban
2. CI logs + review comments are right beside the worker — no context-switching
3. Send the failure or review comments back to the same Worker
4. Worker continues without rebuilding context from scratch

This is the biggest practical difference from opening isolated terminals: **context doesn't break.**

**Pattern 4: Orchestrator-planned feature from scratch**

```
You: @Orchestrator Add rate limiting to the API, user/org tiers,
     Redis-optional, backward-compatible with existing middleware.
     Give me a decomposed plan.

Orchestrator: [analyzes repo context] → 5 tasks:
  Task 1: Design data structures (Claude Code)
  Task 2: Implement in-memory backend (Codex)
  Task 3: Integrate auth middleware (Claude Code)
  Task 4: Write unit tests (Codex)
  Task 5: Update API docs (Claude Code)

[You confirm → Orchestrator spawns 5 Workers simultaneously]
```

**Pattern 5: Isolated browsers for parallel UI work**

Each Worker gets its own isolated browser profile. Two UI tasks can run in parallel without their cookies or login state interfering.

---

### Supported Agents (26)

Claude Code · Codex · Cursor · opencode · Aider · GitHub Copilot · Grok · Kimi · Pi · Amp · Auggie · Droid · Crush · Cline · Goose · Qwen · Continue · Devin · and more

Each runs in its native TUI or Chat mode; AO provides task context, workspace isolation, and Kanban visibility on top.

---

### Install (5 minutes)

Download the desktop app — no CLI required:

```
macOS (Apple Silicon): agent-orchestrator-darwin-arm64.dmg
macOS (Intel):         agent-orchestrator-darwin-x64.dmg
Windows:               agent-orchestrator-win32-x64.exe
Linux (Debian/Ubuntu): agent-orchestrator-linux-x64.deb
```

All at: https://github.com/Untrivial-ai/agent-orchestrator/releases/latest

```
1. Install and open AO
2. Add repository → select your git repo
3. New task → describe task, choose agent
4. Worker appears in Kanban "Working" column
```

---

### AO vs. Superset

| | Agent Orchestrator | Superset |
|---|---|---|
| Key difference | **Project Orchestrator** for planning & delegation | Parallel worktree execution |
| Kanban | ✅ Full lifecycle: PR/CI/review | ❌ None |
| Planning agent | ✅ Project-level Orchestrator | ❌ None |
| Supported agents | 26 | 20+ |
| Browser isolation | ✅ Per-worker browser profiles | ✅ Built-in browser |
| Platform | macOS / Windows / Linux | macOS (primary) + Linux experimental |
| Price | Free (Apache-2.0) | Free + Pro paid |

**One-line difference:** Superset is a parallel agent scheduler; AO is an agent project management tool with a planning layer.

---

**Links**

- GitHub: https://github.com/Untrivial-ai/agent-orchestrator
- Docs: https://aoagents.dev/docs
- Discord: https://discord.com/invite/UZv7JjxbwG
- Twitter: https://x.com/aoagents

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
