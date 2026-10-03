---
title: "Herdr 多 Agent 工作流最佳实践：从入门用法到 VPS 远程会话"
titleEn: "Herdr Multi-Agent Workflow Best Practices: From First Pane to Remote VPS Session"
description: "herdrdev/herdr 实战配置指南：26.5K stars，Apache-2.0，Rust。从 Supervisor 模式、Parallel 并行模式到 Pipeline 流水线模式，覆盖 pane 状态读取、VPS 远程接管、workspace 组织、常见反模式规避——让多 Agent 协作真正跑通，而不只是塞进同一个终端。"
descriptionEn: "Practical configuration guide for herdrdev/herdr — 26.5K stars, Apache-2.0, Rust. Covers Supervisor, Parallel, and Pipeline multi-agent patterns; pane state reading; VPS remote sessions; workspace organization; and anti-patterns to avoid. How to make multi-agent collaboration actually work, not just coexist in one terminal."
pubDate: 2026-10-03
heroImage: "../../assets/images/herdr-best-practices-multi-agent-workflow-banner.jpg"
category: "Tech-Experiment"
tags: ["AI Agent", "Herdr", "多Agent", "工作流", "终端", "最佳实践", "Rust"]
lang: "zh-CN"
wechatTitle: "Herdr 多Agent工作流最佳实践"
wechatDigest: "Supervisor模式/多Agent并行/VPS远程会话；pane状态读懂就不慌"
---

> **说明**：本文是 Herdr 使用指南，侧重实战配置。技术架构拆解见《Herdr：用牧羊人的方式管理你的 AI Agent 群》（已发布）。

---

## 先转变心态：Herdr 不是更好的 tmux

很多人安装 Herdr 之后把它当 tmux 用——开几个 pane，在里面分别跑命令，不管 Agent 状态，不设 Supervisor，不组织 workspace。这样用，Herdr 比 tmux 也强不了多少。

Herdr 的价值在于 **Agent-aware**：它知道每个 pane 里跑的是不是 AI Agent，知道 Agent 的状态（working / blocked / idle / done），并且可以让 Agent 通过 CLI/socket API 直接操作其他 pane。心态转变之后，几个模式自然就出来了。

---

## 安装与基本上手

```bash
# macOS
brew install herdr

# Linux / Windows (Rust)
cargo install herdr

# 启动
herdr
```

首次启动后按 `ctrl+b ?` 看全部快捷键。`ctrl+b q` 从当前会话分离（session 继续跑），再次输入 `herdr` 重连。

---

## 模式一：Supervisor 模式（推荐作为默认起点）

最常见的多 Agent 场景：**一个 Supervisor Agent 拆任务，三到五个 Worker Agent 并行执行，Supervisor 监控并汇总结果。**

### 典型配置

```
workspace: feature-auth
├── pane 0: Supervisor（Claude Code，持有 plan.md，负责分派任务）
├── pane 1: Worker-API（修改 api/auth 模块）
├── pane 2: Worker-Tests（更新测试套件）
└── pane 3: Worker-Docs（更新文档和迁移说明）
```

### 关键步骤

**1. 给 Supervisor Agent 一个清晰的 plan.md**

Supervisor 的第一个 prompt 应该包含：整体任务边界、每个 worker 的职责范围、何时等待 worker 完成再继续。不要让 Supervisor 自己拆，给它一个预制的拆分方案效率更高。

**2. 利用 HERDR_ENV=1 让 Supervisor 感知环境**

当 Agent 运行在 Herdr 管理的 pane 里，环境变量 `HERDR_ENV=1` 会自动设置。配合 `herdr skill`（如果你用了 using-herdr Skill），Supervisor Agent 可以：

- 检查邻居 pane 的状态（`herdr pane list`）
- 等待某个 pane 进入 `blocked` 或 `done` 状态再介入
- 向其他 pane 发送提示（`herdr pane send <pane-id> "<prompt>"`）

**3. 处理 blocked Worker**

当某个 Worker pane 显示 `[blocked]` 时，Herdr 会侧边栏高亮提示。Supervisor 可以检查 blocked 的原因，决定：
- 直接发一条确认指令解除阻塞
- 把这个 sub-task 标记为 pending，先完成其他任务再回来处理

**实战提示**：Supervisor pane 永远不应该跑高负载任务。它是 orchestrator，不是 executor——一个 blocked Supervisor 会卡住整个流程。

---

## 模式二：Parallel 并行模式（多项目独立任务）

适合的场景：**你同时有多个独立仓库或任务，彼此之间没有依赖关系，只需要让它们同时跑。**

### 配置要点

```
workspace: daily-tasks
├── pane 0: Project-A（Claude Code，仓库 A 的 bug fix）
├── pane 1: Project-B（Codex，仓库 B 的文档更新）
└── pane 2: Project-C（opencode，仓库 C 的代码审查）
```

这里不需要 Supervisor——你就是 Supervisor。Herdr 的侧边栏让你一眼看到哪个 pane 需要你介入（blocked），而不是让你三个窗口来回切。

**处理频率建议**：  
- `working` 状态 → 不用管  
- `idle` 状态（Agent 完成等待新任务）→ 每 15–30 分钟检查一次  
- `blocked` 状态（Agent 需要确认）→ 优先级最高，立刻处理  
- `done` 状态 → 下次切换到该 pane 时 review 并 commit

---

## 模式三：Pipeline 流水线模式（A 的输出喂给 B）

适合的场景：**任务之间有明确的串行依赖，前一个 Agent 的产出是下一个 Agent 的输入。**

典型例子：
1. Agent-Research 搜集资料、生成 outline（→ `research.md`）
2. Agent-Write 读取 `research.md`，写完整草稿（→ `draft.md`）
3. Agent-Review 读取 `draft.md`，输出修改意见和最终版（→ `final.md`）

### 关键机制

Pipeline 模式依赖文件作为交接点，而不是直接 pane 间通信：

```bash
# Agent-Research 完成后写入文件
# Agent-Write 启动时指定从文件读入
claude --print "读取 research.md 并写出完整草稿，保存到 draft.md" 
```

**Herdr 的作用**：给每个 Agent 一个独立 pane，清晰显示当前哪一步在跑、哪一步完成了，而不是把三个 Agent 的输出混在同一个终端里。

---

## VPS 远程会话：「跑通宵任务」的正确姿势

这是 Herdr 相对 tmux 最大的实际优势场景。

### 基本配置

```bash
# 在 VPS 上启动 Herdr（后台常驻）
herdr

# 从本地机器接管 VPS 上的 Herdr session
herdr --remote ssh://you@your-vps:22

# 如果 VPS 在 Tailscale 内网
herdr --remote ssh://you@100.x.x.x
```

`--remote` 模式让本地终端成为远程 Herdr server 的客户端——粘贴图片、终端宽度自适应这类细节都能正常工作，这是 `ssh + tmux` 经常出问题的地方。

### 多机器管理（v0.9.0+）

```bash
# 添加命名机器
herdr machine add workbox ssh://you@workbox.tailscale.net
herdr machine add vps-1 ssh://you@vps1.example.com

# 从同一个 Herdr 窗口管理多台机器
herdr  # 启动后通过侧边栏切换机器
```

一台机器断连不会影响其他机器的 Agent——这是 Herdr 比纯 tmux 更可靠的关键点。

### Named Session（隔离多项目）

```bash
# 按项目隔离会话
herdr --session blog-pipeline    # 博客发布流水线
herdr --session code-review      # 代码审查任务

# 重连
herdr --session blog-pipeline
```

不同 session 之间完全独立，不会互相干扰。

---

## Workspace 组织建议

```
workspace → 项目/领域
  tab → 任务类型（feature/bugfix/research）
    pane → 单个 Agent 或工具
```

**具体建议**：
- 每个 workspace 对应一个代码仓库或一个独立项目
- 同一 workspace 内的 tab 按任务类型分（不按 Agent 分）
- pane 数量：Supervisor 模式下不超过 5 个 Worker pane（更多的话 Supervisor 管理成本也上来了）

---

## 常见反模式（避免这些）

**反模式 1：所有 Agent 用同一个 workspace**  
把完全不相关的任务混在一起，侧边栏状态混乱，blocked 通知没有优先级。**修正**：按项目开 workspace。

**反模式 2：让 Supervisor 也做大量实际编码工作**  
Supervisor pane 一旦 busy，就失去了监控和协调能力。**修正**：Supervisor 只做 plan、split、monitor、aggregate。

**反模式 3：不用 named session，所有任务堆在默认 session**  
几天后你根本不知道哪个 pane 在干什么。**修正**：每个独立任务集用 `--session <name>` 启动。

**反模式 4：VPS 上直接用 ssh + tmux 再在里面跑 Herdr**  
两层 session 管理叠加，快捷键冲突，体验差。**修正**：VPS 上只跑 Herdr，本地用 `--remote` 接进去。

**反模式 5：blocked Agent 等很久才处理**  
Agent 被 blocked 通常意味着它遇到了决策点——时间越长，上下文丢失越多。**修正**：把 Herdr 的 blocked 通知当成高优先级信号，收到就处理。

---

## 快捷键速查

| 操作 | 快捷键 |
|------|--------|
| 新 pane（水平分割） | `ctrl+b "` |
| 新 pane（垂直分割） | `ctrl+b %` |
| 切换 pane | `ctrl+b` + 方向键 |
| 分离 session | `ctrl+b q` |
| 查看全部快捷键 | `ctrl+b ?` |
| 关闭当前 pane | `ctrl+b x` |
| 新建 tab | `ctrl+b c` |
| 切换 tab | `ctrl+b n / p` |

---

## 综合建议

Herdr 最大的价值不是功能列表，而是**让多 Agent 协作从"混乱的多窗口" 变成"可观测的流水线"**。

起步建议：先用 Parallel 模式（你做 Supervisor），熟悉 pane 状态信号之后，再引入 Supervisor Agent 自动化协调。不要一开始就搭最复杂的 Supervisor + Pipeline 组合——先把基础的「多个 Agent 同时跑、blocked 及时处理」这个习惯建立起来。

VPS 远程会话是 Herdr 的杀手级场景：跑通宵任务、关电脑、第二天用 `--remote` 接回来查结果——这件事用 tmux 也能做，但 Herdr 的 Agent 状态感知让你一眼知道昨晚每个 Agent 跑到哪了。

---

> 本文所涉软件均来自公开仓库，Apache-2.0 开源，商用无限制。

---

<!--EN-->

## Herdr Multi-Agent Workflow Best Practices

> **Context**: This is a practical usage guide. For architecture teardown, see the earlier article "Herdr: Herding Your AI Agent Swarm."

---

### Mindset First: Herdr Is Not a Better tmux

Many people install Herdr and use it like tmux — open some panes, run commands, ignore agent state, no Supervisor, no workspace organization. Used this way, Herdr offers little over tmux.

Herdr's value is **Agent-awareness**: it knows whether each pane is running an AI agent, tracks agent state (working / blocked / idle / done), and lets agents drive other panes through CLI or socket API. Once you internalize this, the patterns follow naturally.

---

### Pattern 1: Supervisor Mode (Recommended Default)

The most common multi-agent scenario: **one Supervisor Agent splits the work, three to five Worker Agents execute in parallel, the Supervisor monitors and consolidates.**

```
workspace: feature-auth
├── pane 0: Supervisor (Claude Code — owns plan.md, dispatches tasks)
├── pane 1: Worker-API  (modifies api/auth module)
├── pane 2: Worker-Tests (updates test suite)
└── pane 3: Worker-Docs  (updates docs and migration notes)
```

**Key setup points:**

Give the Supervisor a clear `plan.md` upfront. Don't have it decompose the task itself — a pre-decomposed plan is faster.

When an agent runs inside a Herdr pane, `HERDR_ENV=1` is set automatically. With the `using-herdr` Skill, the Supervisor can:
- Check neighboring pane states (`herdr pane list`)
- Wait for a pane to reach `blocked` or `done` before intervening
- Send prompts to other panes (`herdr pane send <pane-id> "<prompt>"`)

**The Supervisor pane should never do heavy work.** A blocked Supervisor stalls the whole pipeline. Keep it as pure orchestrator.

---

### Pattern 2: Parallel Mode (Independent Tasks Across Projects)

When multiple repositories or tasks have no dependencies — you're the Supervisor, and Herdr shows you which panes need attention without forcing you to check each window manually.

**Handling frequency:**
- `working` → leave it alone
- `idle` → check every 15–30 minutes
- `blocked` → highest priority, handle immediately
- `done` → review and commit next time you switch to that pane

---

### Pattern 3: Pipeline Mode (A's Output Feeds B)

For sequential dependencies, use files as handoff points:

```bash
# Agent-Research → research.md → Agent-Write → draft.md → Agent-Review → final.md
```

Herdr gives each stage its own pane, making it clear which step is running and which has completed, rather than mixing three agents' outputs in one terminal.

---

### VPS Remote Sessions: The Killer Use Case

```bash
# Start Herdr on the VPS
herdr

# Connect from local machine
herdr --remote ssh://you@your-vps:22

# Multi-machine management (v0.9.0+)
herdr machine add workbox ssh://you@workbox.tailscale.net
```

The `--remote` mode makes your local terminal a client of the remote Herdr server. Image pasting, terminal resizing, and other things that break with plain ssh+tmux all work correctly. One disconnected machine doesn't interrupt the others.

**Named sessions** for project isolation:

```bash
herdr --session blog-pipeline
herdr --session code-review
```

---

### Anti-Patterns to Avoid

1. **All agents in one workspace** — blocked notifications have no priority, state is unreadable. Fix: one workspace per project.
2. **Supervisor doing heavy coding work** — a busy Supervisor loses coordination capacity. Fix: Supervisor is plan/split/monitor/aggregate only.
3. **No named sessions** — within days you don't know which pane is doing what. Fix: `--session <name>` for each independent task group.
4. **SSH + tmux wrapping Herdr on VPS** — double session management, keybinding conflicts. Fix: only Herdr on the VPS, connect with `--remote`.
5. **Leaving blocked agents waiting** — the longer you wait, the more context is lost. Treat `blocked` notifications as high-priority signals.

---

### Summary

Herdr transforms multi-agent work from "chaos of multiple windows" into "an observable pipeline." Start with Parallel mode (you as Supervisor), build the habit of responding to `blocked` signals promptly, then graduate to Supervisor Agent automation.

The VPS remote session is the killer scenario: start overnight tasks, close the laptop, connect back in the morning with `--remote` and immediately see every agent's state. tmux can do the same persistence, but Herdr's agent-state awareness tells you what actually happened while you were away.

---

> Apache-2.0 open source. Commercial use unrestricted.
