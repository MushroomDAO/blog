---
title: "LoopX：长任务 Agent 的本地状态内核，目标/门控/待办/证据/配额全管"
titleEn: "loopx-loop-engineering-state-kernel-long-running-agents"
description: "LoopX 是一个轻量状态内核和本地控制平面，让 Codex、Claude Code、Cursor 等 Agent 跑长任务时有持久的目标、门控、可执行待办、证据日志和可验证交接。不替换你的 Agent 运行时，只管它跑多轮任务时不跑偏。Python 3.11+，无额外运行时依赖，MIT，已有 200+ 小时跑通的真实轨迹。"
descriptionEn: "LoopX is a lightweight loop engineering state kernel and local control plane for long-running AI agents: durable goals, human-judgment gates, executable todos, quota-aware auto-wake, evidence logs, and verifiable handoffs — while Codex, Claude Code, or Cursor runs the actual turns. No new runtime. Python 3.11+, zero stdlib-external dependencies, MIT, 2,338 stars."
pubDate: "2026-08-06"
updatedDate: "2026-08-06"
category: "Tech-News"
tags: ["AI Agent", "长任务", "状态管理", "Agent控制平面", "Claude Code", "Codex", "开源工具", "Mycelium"]
heroImage: "../../assets/images/loopx-loop-engineering-state-kernel-long-running-agents-banner.jpg"
---

*by Mycelium Protocol*

---

Agent 跑一个任务最难的部分不是单步执行，而是**跑偏**。

你给 Codex 或 Claude Code 一个持续几天的目标，它每次启动都要重新弄清楚现在做到哪了、接下来要干什么、哪些事需要你来决定、上次跑的结果算不算数。Chat 记忆和一个定时器解决不了这个问题。

**[LoopX](https://github.com/Huangruiteng/loopx)** 做的事是把「控制状态」从 Agent 的对话上下文里分离出来，存进一个轻量的本地内核：目标（objective）、门控（gates）、待办（todos）、证据（evidence）、配额（quota）——这五件事始终处于一个可持续恢复、可跨 Agent 交接的形态。

2338 stars，MIT，Python 3.11+，无额外运行时依赖，v0.4.x，今日仍有 push。

---

## 核心问题

LoopX 把长任务控制平面压缩成五个问题，每个都有对应的持久化状态：

| 问题 | LoopX 保持可见的内容 |
|------|---------------------|
| 目标是什么？ | 活跃目标、显式范围、当前授权 |
| 下一步是什么？ | 有序的用户和 Agent 待办、所有权、声明、租约 |
| 哪些事需要人决定？ | 具体的用户门控，而不是含糊的「等待 owner」 |
| 证据有什么变化？ | 紧凑的运行历史、验证、阻塞、已接受的回写 |
| 这轮循环可以继续吗？ | 配额、能力、安全回退、调度提示、停止条件 |

---

## 架构：状态内核在 Agent 和工具之间

```text
objective / issue / project
   │
   ▼
LoopX 状态内核：目标 + 门控 + 待办 + 范围 + 证据 + 配额
   │
   ├─ 需要人判断？ ──是──▶ 提一个具体问题，等待
   │
   ├─ 有安全回退？ ────────▶ 运行一个有界的 Agent 切片
   │
   ▼
Codex / Claude Code / Cursor / shell agent 执行一轮
   │
   ▼
写入证据 + 交接 + 下一个待办 ─▶ 配额决定下次触发
```

执行路径是 `Agent → Capability → Provider`；控制路径返回 `Provider readback → Capability transition → Kernel`。内核拥有持久的待办、门控、监控、已接受的回写、配额、恢复和调度——Agent 只负责在一轮里实际执行。

---

## 五个核心原语

这五条命令构成了 LoopX 循环的主干：

```bash
loopx quota should-run      # 这个注册 Agent 现在应该行动吗？
loopx todo claim            # 谁拥有这个切片？
loopx todo update           # 发生了什么变化？
loopx refresh-state         # 下一轮应该看到什么？
loopx quota spend-slot      # 为一个已验证的切片计费
```

安静跳过、预检失败、dry-run 预览不消耗配额。自动轮次必须先检查配额，只有在验证过的回写之后才 spend-slot。

---

## 五个控制平面面

| 面 | 作用 | 入口 |
|----|------|------|
| **目标状态和状态报告** | 跟踪活跃状态、待办、声明、门控、证据、第一屏注意力 | `loopx status`, `loopx diagnose`, `loopx review-packet` |
| **配额和交互契约** | 决定这轮该交付、提问、等待、自我修复还是保持安静 | `loopx quota should-run`, [配额分配](https://huangruiteng.github.io/loopx/docs/) |
| **Agent 运行时桥接** | 让 Codex App/CLI、Claude Code、通用 worker 都对齐同一个门控 | `loopx heartbeat-prompt`, `loopx worker-bridge` |
| **运营者面** | 不让浏览器成为状态权威，渲染紧凑状态 | `loopx serve-status` |
| **外部投影** | 把待办和门控投影进协作工具，LoopX 仍然是权威 | `loopx lark-kanban` |

域能力（domain capabilities）已包含：`issue-fix`、`content-ops`、`value-connectors`、`ml-experiment`、`benchmark`、`explore`——把可复用的工作泳道封装成 LoopX 子命令。

---

## 与主流 Agent 运行时集成

| 运行时 | 推荐启动方式 | 循环驱动 |
|--------|------------|---------|
| **Codex App** | 让 Agent 连接项目、跑 `loopx doctor`、报告当前门控和下一个待办 | Codex App heartbeat 自动化，从 `quota should-run.scheduler_hint` 刷新 |
| **Codex CLI** | 在项目里启动 Codex，连接并诊断 LoopX，用 `$loopx <任务>` 或 `/skills` | 可见的 `/goal <task_body>` |
| **Claude Code** | 安装 opt-in 适配器，然后 `/loopx <task>` 配合 `/loop` | 原生 Claude Code `/loop` 由 LoopX 门控 |
| **Cursor / shell** | `loopx doctor` 后手动连接或从 runner 调用 LoopX | 你自己的 shell / 调度器 / runner |

---

## 真实证据：200+ 小时的轨迹

LoopX 不是演示项目。README 里附了三条公开可查的真实轨迹：

**OpenViking 开源贡献弧线**：200+ 小时跨越多次有界轮次、决策和证据更新，覆盖完整的 PR 交付流程，Issue-Fix 能力在其中持续维护滚动仓库上下文和修复知识。

**Auto ML 实验弧线**：200+ 小时，假设、匹配证据、无效谱系、运行中的复制品、promote/stop 门控在一张图里全部可见，脱敏后公开。

**Auto Research 多 Agent**：Proposer、Executor、Evaluator/Promoter 并行迭代，待办/配额/证据/目标唤醒同时可见——这是内核协调对等 Agent 的典型结构。

---

## 快速安装

Python 3.11+，`curl`，`tar`，macOS 或 Linux：

```bash
# 不需要 clone，直接安装
curl -fsSL https://raw.githubusercontent.com/huangruiteng/loopx/main/scripts/install-from-github.sh | bash
export PATH="$HOME/.local/bin:$PATH"
loopx doctor

# 连接项目
cd /path/to/your-project
loopx connect
loopx status

# 首次初始化（如果没有现有状态）
loopx start-goal --guided --project . --goal-text "你的长期目标"
```

clone 方式仅供贡献者使用：

```bash
git clone https://github.com/huangruiteng/loopx ~/loopx
~/loopx/scripts/install-local.sh
loopx doctor
```

---

## 配额感知的调度

每个注册 Agent 的调度遵循 `quota should-run.scheduler_hint`；Codex App 自动化通过返回的 `ack_hint.cli_args` 应答当前提示。对等 Agent 在交付前用 `loopx todo claim` 声明所有权，在验证后用 `loopx todo update` 更新，让所有权和证据始终可见。

当用户门控阻断一条泳道时，另一条独立审计过的安全回退可以继续，但不能绕过这个门控。

---

## 为什么值得关注

长任务 Agent 失败的方式不是「模型答错了」，而是「Agent 不知道现在该做什么、哪些事已经决定了、哪些需要等人来判断、上次跑到哪了」。这些是控制平面的问题，不是模型能力的问题。

LoopX 把这层控制状态从对话上下文里剥离出来，变成一个可以被任意 Agent 读写的本地内核，不替换你的运行时，也不要求你换模型。五个原语、一个本地文件系统、零额外运行时依赖——内核的边界非常干净。

和 LongHorizon-Harness（三角色执行框架）、Kiro Crew（持久 IDE 工作区）不同，LoopX 的目标是成为 Agent-agnostic 的状态基础设施：不管你跑的是 Codex、Claude Code 还是自定义 runner，同一套状态内核都适用。

仓库：[github.com/Huangruiteng/loopx](https://github.com/Huangruiteng/loopx)  
文档：[huangruiteng.github.io/loopx/docs](https://huangruiteng.github.io/loopx/docs/)  
用户手册：[my.feishu.cn/wiki](https://my.feishu.cn/wiki/CaL5wMk9ui17ngkWzeUcMlAYnZg)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## LoopX: The State Kernel for Long-Running AI Agents

*by Mycelium Protocol*

Single-turn agent work is hard but tractable. Long-running work is harder in a different way: objectives drift, decisions appear, evidence goes stale, agents hand work to peers, and a scheduler keeps spending tokens after no useful progress remains. Chat memory and a timer are not enough to govern that.

**[LoopX](https://github.com/Huangruiteng/loopx)** separates the control state from the agent's conversation context and keeps it in a lightweight local kernel: goal, gates, todos, evidence, quota — five things that stay persistent, recoverable, and handoff-ready across any number of bounded turns. It doesn't replace Codex, Claude Code, or Cursor; it gives them a stable floor to return to.

2,338 stars, MIT, Python 3.11+, zero runtime dependencies outside the standard library, v0.4.x, pushed today.

---

### The Five Control-Plane Questions

| Question | What LoopX keeps visible |
|----------|--------------------------|
| What is the objective? | Active goal, explicit scope, current authority |
| What happens next? | Ordered user and agent todos, ownership, claims, leases |
| What needs human judgment? | Concrete user gates — not "waiting for owner" |
| What evidence changed? | Run history, validation, blockers, accepted writeback |
| May the loop continue? | Quota, capabilities, safe fallback, scheduler hints, stop conditions |

---

### Architecture: Kernel Between Agent and Tools

```text
objective / issue / project
   │
   ▼
LoopX kernel: goal + gates + todos + scope + evidence + quota
   │
   ├─ human judgment needed? ── yes ─▶ ask a concrete question and wait
   │
   ├─ safe fallback available? ──────▶ run one bounded agent slice
   │
   ▼
Codex / Claude Code / Cursor / shell agent executes one turn
   │
   ▼
write evidence + handoff + next todo ─▶ quota decides the next tick
```

The execution path is `Agent → Capability → Provider`; the control path returns `Provider readback → Capability transition → Kernel`. The kernel owns durable todos, gates, monitors, writeback, quota, recovery, and scheduling — the agent's only job is to perform the actual work in each bounded turn.

---

### Five Core Primitives

```bash
loopx quota should-run      # should this registered agent act now?
loopx todo claim            # who owns this slice?
loopx todo update           # what changed?
loopx refresh-state         # what should the next turn see?
loopx quota spend-slot      # account for a completed, validated slice
```

Quiet skips, preflight failures, and dry-run previews don't spend quota. Automatic turns must check quota first and spend only after validated writeback.

---

### Runtime Integration

| Runtime | Start | Loop driver |
|---------|-------|-------------|
| **Codex App** | Ask agent to connect, run `loopx doctor`, report gate and next todo | Codex heartbeat automation, reads `quota should-run.scheduler_hint` |
| **Codex CLI** | Start Codex, connect and diagnose, use `$loopx <task>` or `/skills` | Visible `/goal <task_body>` |
| **Claude Code** | Install opt-in adapter, then `/loopx <task>` + `/loop` | Native `/loop` gated by LoopX |
| **Cursor / shell** | `loopx doctor` + manual connect or runner call | Your scheduler or runner |

---

### Evidence: Real 200+ Hour Trajectories

These are not demos. The README links three public-safe trajectories:

**OpenViking issue-fix arc** — 200+ elapsed hours across many bounded turns, decisions, and evidence updates; the Issue-Fix capability maintains rolling repository context and revision-stamped fix knowledge throughout.

**Auto ML experiment arc** — 200+ elapsed hours; hypotheses, matched evidence, invalid lineages, running replicates, and promote/stop gates visible in one redacted graph.

**Auto Research** — Proposer, Executor, and Evaluator/Promoter run in parallel while todo, quota, evidence, and targeted wake remain visible simultaneously.

---

### Quick Install

```bash
# No clone needed
curl -fsSL https://raw.githubusercontent.com/huangruiteng/loopx/main/scripts/install-from-github.sh | bash
export PATH="$HOME/.local/bin:$PATH"
loopx doctor

# Connect to your project
cd /path/to/project
loopx connect
loopx status

# First-time guided setup
loopx start-goal --guided --project . --goal-text "Your long-running objective"
```

---

### Why This Matters

Long-running agent work fails not because models are wrong but because there is no durable place to keep the control state: what's the current objective, which decisions are already made, what needs a human, where did the last run leave off. These are control-plane problems, not model-capability problems.

LoopX carves that control state out of the conversation context into a local kernel any agent can read and write — without replacing your runtime, switching your model, or adding runtime dependencies. Five primitives, one local filesystem, clean kernel boundaries.

Unlike LongHorizon-Harness (which provides a three-role execution architecture) or Kiro Crew (which is a persistent workspace layer for a specific IDE), LoopX aims to be agent-agnostic state infrastructure: the same kernel works whether you're running Codex, Claude Code, a custom shell runner, or a peer-agent team.

Repository: [github.com/Huangruiteng/loopx](https://github.com/Huangruiteng/loopx) · Docs: [huangruiteng.github.io/loopx/docs](https://huangruiteng.github.io/loopx/docs/) · Manual: [Feishu wiki](https://my.feishu.cn/wiki/CaL5wMk9ui17ngkWzeUcMlAYnZg)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
