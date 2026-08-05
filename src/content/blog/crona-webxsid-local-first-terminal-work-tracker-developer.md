---
title: "Crona：给住在终端里的开发者的本地优先工作追踪器"
titleEn: "crona-webxsid-local-first-terminal-work-tracker-developer"
description: "webxsid/Crona 是一个 Go 编写的本地优先开发者工作追踪工具：后台 daemon 持有 SQLite 状态，TUI（Bubble Tea）和 CLI 作为客户端通过本地 IPC 交互。支持专注会话计时、习惯追踪、健康度看板、.ics 日历导出，数据全部本地存储，无云耦合。28 stars，MIT 开源。"
descriptionEn: "webxsid/Crona is a local-first developer work tracker written in Go: a background daemon owns SQLite state, and the TUI (Bubble Tea) and CLI are clients communicating over local IPC. Focus session timing, habit tracking, wellbeing dashboard, .ics calendar export — all local, zero cloud coupling. 28 stars, MIT."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["开发者工具", "终端工具", "Go", "生产力", "本地优先", "专注计时", "开源", "Mycelium"]
heroImage: "../../assets/images/crona-webxsid-local-first-terminal-work-tracker-developer-banner.jpg"
---

*by Mycelium Protocol*

---

大多数开发者生产力工具有三个问题：要么是 Web App（离开浏览器就没了），要么绑定云账号（你的工作数据在别人服务器上），要么 TUI 漂亮但数据模型一塌糊涂（随便改个设置就乱了）。

**[Crona](https://github.com/webxsid/crona)**（webxsid）选择了一条不同的路：后台守护进程持有全部状态，TUI 和 CLI 只是客户端，数据在本地 SQLite，架构像 git 一样思考工作状态。

28 stars，刚起步，但设计思路在这个方向上是目前最清晰的之一。

---

## 它解决什么问题

开发者追踪工作的方式通常是这样的：
- Notion/Linear 记任务（在 Web 里，切换上下文）
- 手动记时间（容易忘，不准确）
- 番茄钟 App（和任务系统完全独立）
- 会议记录散落在各处
- 周复盘靠记忆

Crona 把这些整合进终端：**规划工作 → 追踪专注会话 → 回顾数据 → 导出结构化产物**，全部在命令行里，全部存在你的机器上。

---

## 架构：daemon 是唯一的真相来源

Crona 的架构设计值得专门说一下，因为这直接决定了它的可靠性。

```
crona-daemon（后台守护进程）
   ├── SQLite 存储（唯一真相来源）
   ├── 计时器
   ├── 定时提醒
   ├── 更新检查
   └── IPC（Unix socket）
         ├── crona-tui（Bubble Tea 交互界面）
         └── crona（CLI + 脚本接口）
```

**关键原则**：TUI 和 CLI 是**客户端**，不是控制器。所有状态变更经过 daemon。本地通知由 daemon 发出，不是 TUI 进程——这意味着你关了终端，提醒还会来。专注会话的非活动警报也是 daemon 在跑：如果你开了专注计时器然后去摸鱼，daemon 会在超过配置阈值后提醒你。

技术栈：
- 语言：**Go**（monorepo，四个模块：kernel / tui / cli / shared）
- UI：**Bubble Tea**（charmbracelet，Go 的 TUI 框架）
- 存储：**SQLite**（本地，确定性）
- IPC：**Unix socket**（Socket API 有文档，可接第三方客户端）

---

## 核心概念：五层工作结构

Crona 用结构化对象而非松散笔记来组织工作，层级是：

```
Repository（仓库）
  └── Stream（流）
        └── Issue（工作项）
              └── Session（专注会话）
                    └── Segment（work / short_break / long_break / rest）
```

**Repository**：最顶层的工作桶。比如 `Office`、`Personal`、`Research`。

**Stream**：Repository 内部的长期分支。比如 `main`、`backend`、`experiments`。

**Issue**：最小的有意工作单元。可以有标题、估时、备注、生命周期状态。这是类 git 心智模型的体现——每项工作是一个可追踪的对象，不是日历上的一个格子。

**Session**：绑定到 Issue 的专注工作区间。用计时器开始和停止，以「提交风格的摘要消息」结束——就像 git commit message 一样，给这段工作留下一个说明。

**Segment**：一个 Session 由多个 Segment 构成：`work`、`short_break`、`long_break`、`rest`。计时器管理 Segment 的切换，强制执行结构化边界。

**Active Context**：TUI 和 CLI 共享的 `{ repo → stream → issue }` 当前选择。所有客户端看到的是同一个上下文，不会出现「TUI 里开着任务 A，命令行里执行的是任务 B」这种错乱。

---

## 四个主要视图

### Daily（每日交互面板）

规划当天、更新 Issue 状态、管理计时器驱动的工作、处理工作中随时冒出的小决策。这是主要工作入口。

宽屏和窄屏都有适配：宽终端保留多窗格展示，窄终端折叠成紧凑列表，标题/截止日期/状态始终可读。

### Summary（只读摘要）

回答「今天或这段时间看起来怎么样」，不进入编辑流程。CLI 里对应 `crona summary`：

```bash
crona summary              # 今天
crona summary --week       # 本周
crona summary --last-x-days 7   # 过去7天
```

### Rollup / Wellbeing（健康度看板）

**这是 Crona 里最有意思的部分**。它不只追踪你工作了多久，还追踪你的状态：

| 指标 | 说明 |
|------|------|
| 心情（Mood） | 每日 check-in 记录 |
| 精力（Energy） | 主观精力水平 |
| 睡眠（Sleep） | 睡眠质量 |
| 屏幕时间 | 记录过度使用 |
| 倦怠风险（Burnout） | 综合指标 |
| 专注质量（Focus） | 专注会话分析 |
| 习惯打卡（Habits） | 自定义习惯汇总 |

**Momentum（势头）**是 Wellbeing 里的核心模块：追踪你在不同时间维度上的连续性——

```
Daily streak:  1d → 3d → 7d → 14d → 30d → 60d → 100d
Weekly:        1w → 2w → 4w → 8w → 13w → 26w → 52w
Monthly:       1mo → 2mo → 3mo → 6mo → 12mo → 24mo
```

Momentum 可以针对习惯或工作上下文（repo + stream 组合）定义，支持 `any`（任一目标完成即计）和 `all`（全部目标才计）两种模式。当前连续天数和历史最佳并排展示。

### Export

可以导出 PDF 报告和确定性 `.ics` 日历文件。`.ics` 设计为本地自动化友好：

```
Crona 写入 .ics → 本地自动化监听目录 → 外部工具导入
```

不需要直接接入 Google Calendar 或 iCloud API，你的本地脚本或第三方工具决定怎么用。

---

## 快速上手

### 安装

```bash
# macOS / Linux（Homebrew）
brew install webxsid/tap/crona

# Windows（Scoop）
scoop bucket add webxsid https://github.com/webxsid/scoop-bucket
scoop install crona
```

或者从 [GitHub Releases](https://github.com/webxsid/crona/releases) 直接下载二进制。

### 启动

```bash
crona           # 启动 TUI（同时确保 daemon 在运行）

crona summary   # 快速查看今天
crona summary --week

# daemon 管理
crona daemon status --json
crona daemon attach --json
crona daemon info --json

# Shell 补全
crona completion zsh    # 或 bash / fish
```

### 运行时注意事项

- **本地通知由 daemon 发出**，不是 TUI——关了终端，提醒还在
- **定时提醒**只在 daemon 运行时生效
- **Summary 视图是只读的**，要规划或修改要进 Daily 视图
- PDF 导出依赖本地渲染工具（见 [install.md](https://github.com/webxsid/crona/blob/main/docs/install.md)）

---

## 设计原则

Crona 的 README 里列的设计原则，也是它和大多数同类工具的区别：

| 原则 | 含义 |
|------|------|
| **本地优先** | 数据在你的机器上，没有网络就能完整工作 |
| **权威数据优于派生状态** | daemon 是唯一真相，其他客户端不保存状态 |
| **可重放操作** | 类 git，可以重建状态历史 |
| **无隐藏后台作业** | 所有运行中的进程都可被 inspect |
| **确定性本地产物** | `.ics` / PDF 输出行为可预测 |
| **类 git 的工作状态心智模型** | Issue 有生命周期状态，Session 有「提交消息」 |

这套原则的现实意义：不会有「我的数据在哪个服务器上」「这个设置改了会不会影响之前的记录」「App 出问题了我的数据还在吗」这类问题。

---

## 为什么值得关注

**这个细分赛道一直有个空洞**：一端是轻量番茄钟（没有工作结构），另一端是全功能项目管理（太重、不在终端），中间缺少一个「住在终端的开发者的工作追踪系统」。

Crona 的 daemon-first 架构比大多数 TUI 工具更扎实——状态不在 TUI 进程里，不会因为你 `Ctrl+C` 了就丢。Socket API 有文档，意味着可以写脚本和第三方集成，而不是等作者加功能。

28 stars，2026 年 2 月刚起步，MIT 许可。适合喜欢「数据在自己手里 + 不离开终端 + 有结构的工作记录」的开发者。

仓库：[github.com/webxsid/crona](https://github.com/webxsid/crona)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Crona: Local-First Work Tracking for Developers Who Live in the Terminal

*by Mycelium Protocol*

Most developer productivity tools have one of three problems: they're web apps (disappear when you leave the browser), they're cloud-tied (your work data lives on someone else's server), or their TUI looks nice but the data model falls apart under real use.

**[Crona](https://github.com/webxsid/crona)** (webxsid) took a different approach: a background daemon owns all state, the TUI and CLI are just clients, data lives in local SQLite, and the architecture thinks about work state the way git thinks about code. 28 stars, early stage, MIT license.

### The Architecture: Daemon as the Single Source of Truth

```
crona-daemon (background daemon)
   ├── SQLite storage (single source of truth)
   ├── Timer
   ├── Scheduled reminders
   ├── Update checks
   └── IPC (Unix socket)
         ├── crona-tui (Bubble Tea interactive UI)
         └── crona (CLI + scripting interface)
```

TUI and CLI are **clients, not controllers**. All state changes go through the daemon. Local notifications are emitted by the daemon, not the TUI process — close the terminal, reminders still fire. Focus inactivity alerts also run in the daemon: if you start a focus timer and go idle, the daemon notifies you once you've exceeded the configured threshold.

Tech stack: **Go** monorepo (kernel / tui / cli / shared modules), **Bubble Tea** TUI, **SQLite** storage, **Unix socket** IPC (Socket API is documented — third-party clients are possible).

### Five-Layer Work Structure

```
Repository
  └── Stream
        └── Issue
              └── Session
                    └── Segment (work / short_break / long_break / rest)
```

**Repository**: top-level work bucket (Office, Personal, Research).  
**Stream**: long-lived subdivision inside a repo (main, backend, experiments).  
**Issue**: the smallest intentional unit of work — title, estimate, notes, lifecycle state. Git-like: each work item is a trackable object, not a calendar slot.  
**Session**: a focused interval tied to an issue, started and stopped via timer, ending with a commit-style summary message.  
**Segment**: what a session is made of — structured work and break intervals.  
**Active Context**: the shared `{ repo → stream → issue }` selection across all clients. TUI and CLI see the same context.

### The Four Views

**Daily** — interactive working surface: plan the day, update issue state, manage the timer, handle small decisions as work unfolds. Adapts to terminal width; compact rendering on narrow terminals.

**Summary** — read-only at-a-glance surface:
```bash
crona summary
crona summary --week
crona summary --last-x-days 7
```

**Rollup / Wellbeing** — the most interesting part. Tracks not just how long you worked but how you're doing:

| Metric | Description |
|--------|-------------|
| Mood | Daily check-in |
| Energy | Subjective energy level |
| Sleep | Sleep quality |
| Screen time | Overuse flag |
| Burnout risk | Composite indicator |
| Focus | Session quality analysis |
| Habits | Custom habit rollups |

**Momentum** is the core sub-module: tracks streaks across time dimensions —

```
Daily: 1d → 3d → 7d → 14d → 30d → 60d → 100d
Weekly: 1w → 2w → 4w → 8w → 13w → 26w → 52w
Monthly: 1mo → 2mo → 3mo → 6mo → 12mo → 24mo
```

Momentum can target habits or work contexts (repo + stream), with `any` (any selected target counts) or `all` (all must contribute) matching modes. Current streak and all-time best are shown side by side.

**Export** — PDF reports and deterministic `.ics` calendar files. The `.ics` flow is designed for local automation:

```
Crona writes .ics → local automations watch the directory → external tools import or react
```

No direct Google Calendar or iCloud API required. Your local scripts decide what to do with the files.

### Quick Start

```bash
# macOS / Linux
brew install webxsid/tap/crona

# Windows
scoop bucket add webxsid https://github.com/webxsid/scoop-bucket
scoop install crona
```

```bash
crona                    # launch TUI (also starts daemon)
crona summary            # read-only today summary
crona daemon status --json
crona completion zsh     # shell completions
```

### Design Principles

| Principle | What it means in practice |
|-----------|--------------------------|
| Local-first | Full functionality without network; your data, your machine |
| Authoritative data over derived state | Daemon is the only source of truth |
| Replayable operations | State history is reconstructable (git-like) |
| No hidden background jobs | Every running process is inspectable |
| Deterministic local artifacts | .ics / PDF output is predictable |
| Git-like mental model | Issues have lifecycle state; sessions have commit messages |

### Why It Matters

There's a gap in this category: lightweight Pomodoro timers (no work structure) on one end, full project management (too heavy, not terminal-native) on the other. Nothing in between for developers who want structured work tracking without leaving the terminal or giving their data to a cloud service.

Crona's daemon-first architecture is more robust than most TUI tools — state doesn't live in the TUI process, so `Ctrl+C` doesn't lose anything. The Socket API is documented, meaning scripts and third-party integrations are possible without waiting for the author to add features.

28 stars, started February 2026, MIT license.

Repository: [github.com/webxsid/crona](https://github.com/webxsid/crona)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
