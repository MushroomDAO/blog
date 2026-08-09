---
title: "Pi 编程 Agent 缺什么，pi-muselinn-harness 就补什么"
titleEn: "Whatever the Pi Coding Agent Lacks, pi-muselinn-harness Supplies"
description: "pi-muselinn-harness 是一个 TypeScript 扩展包，把 Kimi Code 的核心子系统——Swarm 并行子 Agent、Goal 生命周期、Plan 模式、18 级权限链、Hooks 引擎、7 范围 Skills——移植进 Pi 编程 Agent。架构上做了 core/adapter 分离，23 个测试套件 660+ 断言，CI 覆盖 macOS/Ubuntu/Windows × Node 24/26。"
descriptionEn: "pi-muselinn-harness is a TypeScript extension package that ports Kimi Code's core subsystems — Swarm parallel subagents, Goal lifecycle, Plan mode, 18-level permission chain, Hooks engine, 7-scope Skills — into the Pi coding agent. Core/adapter architecture split, 23 test suites with 660+ assertions, CI on macOS/Ubuntu/Windows × Node 24/26."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["Pi Agent", "Kimi Code", "子Agent", "Agent编排", "开源工具", "TypeScript", "Mycelium"]
heroImage: "../../assets/images/pi-muselinn-harness-kimi-code-subagents-goal-plan-tui-banner.jpg"
---

*by Mycelium Protocol*

---

Pi 是一个有自己主张的编程 Agent：专注、轻量，故意不做子 Agent、不做 Plan 模式、不做 Todo。

[pi-muselinn-harness](https://github.com/MuseLinn/pi-muselinn-harness) 做的事情是：**把 Kimi Code 的核心子系统，一个包完整移植进来**。

---

## Pi 故意不做的事，harness 来补

| 你想要的 | harness 提供的 |
|---------|--------------|
| 并行子 Agent | `agent_swarm` / `agent` — 真实 `max_concurrency`，实时 braille 进度 TUI，`run_in_background` |
| 先规划再执行 | `enter_plan_mode` — 只读探索，审批门控，Kimi Code 权限模型 |
| 任务不失控 | `/goal` — 生命周期、预算、队列、完成标准门控 |
| 安全防护 | 18 级权限链（`auto` / `yolo` / `manual`），破坏性命令 + `.env` 守卫 |
| 跨会话持久化 | `run_background` + `cron_create` — 持久任务和定时提示词 |
| Agent 好好问问题 | `ask_user_question` — 多问题标签化对话，支持多选和自由文本 |
| 任务追踪 | `/todo` — 分阶段计划，内联面板和提醒 |
| 更好的终端界面 | `╭─╮ │ ╰─╯` 闭合边框 TUI，顶栏嵌入 spinner + 模型名 |
| 生命周期自动化 | `[[hooks]]` 引擎 — 16 个事件，可阻断的 PreToolUse/Stop/UserPromptSubmit |

安装只需一行：

```bash
pi install npm:pi-muselinn-harness
```

---

## Swarm：真并发，不是假多线程

`agent_swarm` 工具背后是一个 worker pool：

- **真实 `max_concurrency` 上限**——不是「提交 N 个任务然后全部同时跑」，而是有一个 worker pool，超过上限的任务排队等
- **指数退避重试**
- **每个子 Agent 30 分钟超时**（对齐 Kimi Code）
- **`run_in_background`**——整个 swarm 进后台，立即返回 task ID，报告写到 `output_path`
- **三种子 Agent 类型**：`coder`（读写+bash）、`explore`（只读）、`plan`（只读，无 shell）
- **Braille 进度条**——由真实的 tool-call 进度驱动，250ms 帧率，状态指纹门控（没变化不渲染）

子 Agent 的权限不是「继承然后放宽」，而是所有 worker 的工具调用都通过**同一个策略链**走一遍，`/mode` 切换实时传播到运行中的子 Agent。

---

## Goal：有生命周期的目标，不是便利贴

`/goal` 不是给 Agent 写一张便利贴——它有完整的状态机：

```
active → paused → blocked → complete
                          → usage_limited
                          → budget_limited
```

几个设计细节值得注意：

**Active Guard**：`create_goal` 拒绝静默覆盖一个活跃目标，必须显式 `replace=true` 或 `/goal replace`。

**Blocked 3-turn 阈值**：连续三次被同一个原因 block 才真正进入 blocked 状态，避免误判。

**完成标准门控**：声明了 criterion 的目标，必须在同一个 `update_goal` 调用里带 `verified=true` 才能标记完成，不能自己说「我做完了」就算。

**三重预算检查**：tokenBudget + turnBudget + wallClockBudgetMs，支持 `turns/tokens/ms/s/minutes/hours` 单位。

**单调恢复**：持久化的 counter 按 goalId 取最大值合并，旧条目不能把 turns/tokens 往回拉。

---

## Plan 模式：探索与执行分离

进入 Plan 模式后，Engineer 只能读，不能写：

```
/plan                   → 进入只读探索
                          LLM 探索代码，写方案
                          用户审批
                          审批通过 → 退出 Plan 模式，开始执行
```

技术上：Write/Edit（plan 文件本身除外）、TaskStop、CronCreate、CronDelete 在 Plan 模式下被 block。Bash **不** block——沿用正常权限模式，不额外限制。

一个实用的细节：`revise`（修改方案）和 `cancel`（取消审核）都会带着原来的 plan 对象重新进入 Plan 模式，不会丢失已写的方案。

---

## 权限链：18 级，真的在用

权限设计直接对标 Kimi Code：

- **18 级策略链**，短路顺序：破坏性命令检测 → 敏感文件守卫 → 策略模式（auto/yolo/manual）
- **破坏性命令检测**：`rm -rf` / `git push --force` / `drop table` / `git reset --hard`，这些永远询问，不被 session 审批覆盖
- **敏感文件守卫**：`.env` / `id_rsa` / `*.key` 的读写，即使在 auto 模式下也拦截
- **Session 审批指纹**：每次审批记 `sessionId + input fingerprint`，不会退化成「永久允许」
- **子 Agent 门控**：worker 的工具调用走同一个策略链，`ask` 结果在无人值守时降级为 block，不会静默批准

---

## Hooks：16 个事件，配置式拦截

读 `~/.kimi-code/config.toml` 或项目 `.kimi-code/config.toml`，零依赖 TOML 迷你解析器：

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "bash ~/.hooks/check-destructive.sh"
timeout = 5000
```

退出码语义：
- `0` — 允许（stdout 追加进上下文）
- `2` — block（stderr 作为原因）
- 其他 / 超时 / 崩溃 — fail-open（不 block）

**安全网**：Stop 事件连续 block 3 次后自动禁用（防止 Agent 卡死在 Stop 循环里）。

---

## TUI：Kimi Code 风格的闭合边框

默认样式：

```
╭─── ⠼ Thinking · claude-sonnet-4-6 ────────╮
│❯ 帮我重构一下 auth 模块                      │
╰────────────────────────────────────────────╯
```

三种样式可以热切换：

```
/tui style boxed    # 默认，Kimi Code 风格闭合边框
/tui style plain    # 纯文本
/tui style compact  # pi-spark 风格信息边框
```

Plan 模式下顶栏显示 `plan` 标记。支持 `PI_MUSELINN_SPINNER=braille|pulse|bounce|moon`（moon 对应 Kimi Code 的月相动画）。

还有一个 shimmer 效果：border 里的 working label 有一个时钟驱动的光带扫过：

```
/tui shimmer classic   # 余弦光带
/tui shimmer kitt      # K.I.T.T 扫描器
/tui shimmer disabled
```

---

## 架构：core/adapter 干净分离

```
packages/core/     ← 纯 TypeScript 逻辑，零 pi 依赖
├── goal/          Goal 状态机
├── plan/          Plan 模式工具白名单 + 路径守卫
├── permission/    18 级权限链
├── hooks/         TOML 解析 + 16 事件执行器
├── skills/        7 范围扫描器
├── swarm/         并发控制 + braille 进度
├── task/          Cron + Task 持久化
└── tui/           TUI chrome 纯逻辑

swarm/ task/ tui/ ask/ todo/ ...  ← pi adapter 层
```

所有核心逻辑不依赖 pi，可以独立测试：

```bash
npm test    # 23 个测试套件，660+ 断言，不消耗 model quota
```

CI 矩阵：macOS + Ubuntu + Windows × Node 24/26。

---

## 和 Kimi Code 的对齐情况

| 能力 | 状态 | 备注 |
|------|------|------|
| 三种内置子 Agent 类型 | ✅ | coder/explore/plan |
| 上下文隔离 | ✅ | 独立 session，只有最终结果回流 |
| 并行分发 + max_concurrency | ✅ | 真实 worker pool |
| 30 分钟超时 | ✅ | 每个子 Agent AbortSignal |
| run_in_background | ✅ | 早期 task ID 返回 |
| 嵌套子 Agent | ❌ | 故意关闭，防止递归分发 |
| wire.jsonl session 持久化 | ❌ | 子 Agent 用内存 session |
| Hooks（16 事件） | ✅ | 完整覆盖 |
| Skills（7 范围） | ✅+ | 比 Kimi Code 4 个范围更多 |

---

项目地址：https://github.com/MuseLinn/pi-muselinn-harness

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## pi-muselinn-harness: Everything Pi Deliberately Skips, in One Package

*by Mycelium Protocol*

---

Pi is a focused coding agent with its own philosophy: stay lean, stay focused, deliberately skip subagents, plan mode, and todo management.

[pi-muselinn-harness](https://github.com/MuseLinn/pi-muselinn-harness) takes a different view: **port Kimi Code's core subsystems into Pi, one package, complete.**

---

### What Pi Skips, Harness Provides

| You want | You get |
|----------|---------|
| Parallel subagents | `agent_swarm` / `agent` — real `max_concurrency`, live braille TUI, `run_in_background` |
| Plan before execution | `enter_plan_mode` — read-only exploration, approval gate, Kimi Code permission model |
| Stay on task | `/goal` — lifecycle, budgets, queue, completion-criterion gate |
| Safety rails | 18-level permission chain (`auto` / `yolo` / `manual`), destructive-command + `.env` guards |
| Work outliving the session | `run_background` + `cron_create` — persistent tasks and scheduled prompts |
| The agent asking properly | `ask_user_question` — tabbed multi-question dialog, multi-select, free-text Other |
| Task tracking | `/todo` — phased plan with inline panel and reminders |
| Better terminal UI | `╭─╮│╰─╯` closed-box TUI, spinner + model name in the top border |
| Lifecycle automation | `[[hooks]]` engine — 16 events, blockable PreToolUse/Stop/UserPromptSubmit |

One-line install:

```bash
pi install npm:pi-muselinn-harness
```

---

### Swarm: Real Concurrency, Not Fake Parallelism

`agent_swarm` runs a proper worker pool:

- **True `max_concurrency` cap** — tasks above the limit queue; they don't all run simultaneously
- **Exponential backoff retries**
- **30-minute timeout per subagent** (aligned with Kimi Code)
- **`run_in_background`** — whole swarm goes async, immediate task ID, report written to `output_path`
- **Three subagent types**: `coder` (read/write+bash), `explore` (read-only), `plan` (read-only, no shell)
- **Braille progress bars** — driven by real tool-call progress, 250ms frames, state-fingerprint gated (unchanged frames cost nothing)

All worker tool calls go through the **same shared permission policy chain**. `/mode` changes propagate to in-flight subagents. Ask results degrade to blocks in unattended mode — never silent approval.

---

### Goal: A State Machine, Not a Sticky Note

`/goal` has a proper state machine:

```
active → paused → blocked → complete
                          → usage_limited
                          → budget_limited
```

Design details worth noting:

**Active Guard**: `create_goal` refuses to silently overwrite an active goal. You need explicit `replace=true` or `/goal replace`.

**Blocked 3-turn threshold**: three consecutive blocks for the same reason before actually entering the blocked state — prevents false positives.

**Completion-criterion gate**: if a goal declares a criterion, the same `update_goal` call that marks it complete must include `verified=true`. Engineer can't declare its own output done.

**Triple budget checks**: tokenBudget + turnBudget + wallClockBudgetMs, supporting `turns/tokens/ms/s/minutes/hours` units.

**Monotonic restore**: persisted counters merge by taking the max per goalId — a stale entry can never pull turns/tokens backwards.

---

### Plan Mode: Exploration Separated From Execution

In plan mode, the agent can only read — not write:

```
/plan               → enter read-only exploration
                      LLM explores code, writes a plan
                      user reviews and approves
                      approved → exit plan mode, begin execution
```

Technically: Write/Edit (outside the plan file itself), TaskStop, CronCreate, CronDelete are blocked in plan mode. Bash is **not** blocked — it follows the normal permission mode, no additional restriction.

Practical detail: both `revise` and `cancel` re-enter plan mode carrying the same plan object (id/path/content). No lost work, no traps.

---

### Permission: 18 Levels, Actually Enforced

Short-circuit order: destructive command detection → sensitive file guard → mode policy (auto/yolo/manual).

- **Destructive commands**: `rm -rf`, `git push --force`, `drop table`, `git reset --hard` — always ask, never overridden by session approvals
- **Sensitive file guard**: `.env` / `id_rsa` / `*.key` read/write intercepted even in auto mode
- **Session approval fingerprints**: recorded as `sessionId + input fingerprint`, never degrades into "permanent allow"
- **Subagent gating**: worker calls go through the shared chain; ask verdicts degrade to blocks; `/mode` propagates by construction

---

### Hooks: 16 Events, Config-Driven

Reads `~/.kimi-code/config.toml` or project `.kimi-code/config.toml` via a zero-dependency built-in TOML parser:

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "bash ~/.hooks/check-destructive.sh"
timeout = 5000
```

Exit code semantics:
- `0` — allow (stdout appended as context)
- `2` — block (stderr as reason)
- anything else / timeout / crash — fail-open

Safety net: Stop hooks that block 3 consecutive times auto-disable to prevent the agent getting stuck in a Stop loop.

---

### Architecture: Clean Core/Adapter Split

```
packages/core/     ← pure TypeScript logic, zero pi imports
├── goal/          Goal state machine
├── plan/          Plan mode tool whitelist + path guard
├── permission/    18-level policy chain
├── hooks/         TOML parser + 16-event executor
├── skills/        7-scope scanner
├── swarm/         concurrency control + braille progress
├── task/          Cron + Task persistence
└── tui/           TUI chrome pure logic

swarm/ task/ tui/ ask/ todo/ ...  ← pi adapter layer
```

All core logic is independent of pi and testable in isolation:

```bash
npm test    # 23 suites, 660+ assertions, no model quota consumed
```

CI matrix: macOS + Ubuntu + Windows × Node 24/26, on every push and PR.

---

### Kimi Code Alignment

| Capability | Status | Notes |
|-----------|--------|-------|
| Three built-in subagent types | ✅ | coder/explore/plan |
| Context isolation | ✅ | Independent sessions, only final results flow back |
| Parallel dispatch + max_concurrency | ✅ | Real worker pool |
| 30-minute timeout | ✅ | Per-subagent AbortSignal |
| run_in_background | ✅ | Early task ID return |
| Nested subagents | ❌ | Deliberately closed — no recursive dispatch |
| wire.jsonl session persistence | ❌ | Subagents use in-memory sessions |
| Hooks (16 events) | ✅ | Full coverage |
| Skills (7 scopes) | ✅+ | Extends Kimi Code's 4 scopes |

---

Repository: https://github.com/MuseLinn/pi-muselinn-harness

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
