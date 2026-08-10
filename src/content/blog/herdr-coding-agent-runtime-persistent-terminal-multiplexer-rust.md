---
title: "Herdr：用牧羊人的方式管理你的 AI Agent 群"
titleEn: "herdr-coding-agent-runtime-persistent-terminal-multiplexer-rust"
description: "herdrdev/herdr，26.5k stars，Apache 2.0，Rust。一个专为多 AI Agent 时代设计的终端持久化运行时：关盖子、断网络、重启机器——Agent 继续跑，session 继续在，随时从任何终端或 SSH 重连。每个 pane 实时标注 working/blocked/idle 状态，Agent 卡住需要人介入时主动告知。单 Rust 二进制，无 Electron，支持 Claude Code/Codex/Cursor/opencode/Grok，有插件市场。"
descriptionEn: "herdrdev/herdr, 26.5k stars, Apache 2.0, Rust. A persistent terminal runtime designed for the multi-agent era: close the lid, drop the network, restart the machine — agents keep working, sessions stay alive, reattach from any terminal or over SSH. Every pane is live-labelled working/blocked/idle; herdr alerts you when an agent is stuck and needs a human. Single Rust binary, no Electron. Supports Claude Code, Codex, Cursor, opencode, Grok. Plugin marketplace included."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["AI Agent", "终端", "Rust", "开源", "多Agent", "工具", "Mycelium"]
heroImage: "../../assets/images/herdr-coding-agent-runtime-persistent-terminal-multiplexer-rust-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

你同时跑多个 AI Agent——Claude Code 在改 bug，Codex 在写测试，另一个在查文档。问题是：你不知道哪个卡住了。你得轮流切窗口检查，或者等不知道哪个 Agent 默默失败了几十分钟。

Herdr 解决这个问题。

名字来自 herder（牧羊人），定位是：**让你管理一群 Agent，而不是在它们之间疲于奔命。**

GitHub: https://github.com/herdrdev/herdr | ⭐ 26,471 | Apache 2.0 | Rust

---

## 核心功能

**永远在跑**

Herdr 是一个后台服务器；终端 pane 活在它里面。关盖子，断网络，重启机器——Agent 继续跑，session 继续在。`ctrl+b q` 从当前终端分离，回来时直接 `herdr` 重连。也可以通过 SSH 从另一台机器接回来。这对「Agent 跑通宵任务」这件事来说是根本性的改变。

**不用找卡住的那个**

Herdr 给每个 pane 打上实时状态标注：**working**（运行中）、**blocked**（卡住，等待输入）、**idle**（空闲）。Agent 停下来需要你回答一个问题的时候，Herdr 会主动告知——你不需要轮流检查每个窗口。

```
Pane 1  [working]  Claude Code: 修复 auth 模块
Pane 2  [blocked]  Codex: 等待确认——要删除 legacy API 吗？
Pane 3  [idle]     opencode: 完成
```

**Agent 原生**

CLI 和 socket API 是同一个接口——Agent 可以直接驱动它：spawn 新 pane，向另一个 Agent 发送提示，等到另一个 Agent 真正 blocked 再介入。这让「Agent 管理 Agent」的工作流成为可能，而不只是人管理 Agent。

**不替换你现有的 Agent**

Herdr 不包装、不替换任何 AI coding agent——它只是持有它们的终端。支持：Claude Code、Codex、Cursor、opencode、Grok，以及任何在终端里跑的 Agent。如果你在用某个 Agent，Herdr 可以直接接管它的 terminal session。

**键盘和鼠标都是一等公民**

tmux 风格的前缀键（`ctrl+b`）+ 点击、拖拽、分割 pane。不是「键盘或鼠标选一个」，是「按情况随意切换」。

**插件市场**

第三方插件可以扩展 pane 行为和工作流。[herdr.dev/plugins](https://herdr.dev/plugins/) 可以浏览。

---

## 安装

```bash
# macOS/Linux
curl -fsSL https://herdr.dev/install.sh | sh

# 或者 Homebrew
brew install herdr

# 或者 mise
mise use -g herdr

# Windows（beta）
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

装好后，在工作目录里直接运行：

```bash
herdr
```

然后跑你的 Agent，分 pane，关浏览器——Herdr 接管剩下的事。

```bash
# 分离（保持后台运行）
ctrl+b q

# 重新连接
herdr
```

---

## 技术细节

**单 Rust 二进制，无 Electron**：herdr 不需要 Node、不需要浏览器内核，跑在你已经有的任何终端里。体积小，启动快，不占额外内存。

**Socket API**：除了 CLI，herdr 还暴露一个 socket API——Agent 可以用程序方式控制 pane，查询状态，发送输入。这是「Agent 之间协调」的基础。

**会话持久化**：session 状态可以远程同步，在不同机器之间共享（[远程持久化文档](https://herdr.dev/docs/persistence-remote/)）。

**开发**：

```bash
git clone https://github.com/herdrdev/herdr
cd herdr
cargo build --release

just test    # 单元测试
just check   # 格式化、测试、维护检查
```

---

## 为什么现在

多 Agent 工作流是 2026 年 coding 的方向——不是一个 Agent 做所有事，而是多个专门化的 Agent 并行跑，互相等待，互相触发。

这件事以前没有专门的运行时：你要么自己写 tmux 脚本，要么用 screen，要么开一堆终端窗口靠肉眼盯。Herdr 是第一个把「管理 Agent 群」作为核心设计目标的终端运行时。

26,500+ stars（从 2026 年 3 月到现在）说明这个需求是真实的，而且 Rust 写的单二进制方案降低了使用门槛到几乎为零。

---

## 快速体验

```bash
# 安装
brew install herdr

# 启动（在你的项目目录）
herdr

# 在第一个 pane 里跑 Claude Code
claude

# ctrl+b " 水平分割，在第二个 pane 里跑 Codex
codex

# ctrl+b q 分离——两个 Agent 继续跑
# 明天回来：herdr 重连，看状态
```

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Herdr: A Persistent Runtime for Your Herd of AI Agents

*by Mycelium Protocol*

---

You're running multiple AI agents simultaneously — Claude Code fixing a bug, Codex writing tests, another one searching documentation. The problem: you don't know which one is stuck. You cycle through windows, or wait for an agent that silently failed thirty minutes ago.

Herdr fixes this.

The name comes from "herder." The position: **let you manage a herd of agents, rather than scrambling between them**.

GitHub: https://github.com/herdrdev/herdr | ⭐ 26,471 | Apache 2.0 | Rust

---

### Core Features

**Always running**

Herdr is a background server; terminal panes live inside it. Close the lid, drop the network, restart the machine — agents keep working, sessions stay alive. `ctrl+b q` detaches from the current terminal; `herdr` reattaches. Also works over SSH from another machine. This fundamentally changes "agents running overnight tasks."

**Never hunt for the stuck one**

Herdr live-labels every pane: **working**, **blocked** (waiting for input), **idle**. When an agent stops and needs a human answer, Herdr tells you — you don't need to check each window in rotation.

```
Pane 1  [working]  Claude Code: fixing auth module
Pane 2  [blocked]  Codex: waiting for confirmation — delete legacy API?
Pane 3  [idle]     opencode: done
```

**Agent-native**

The CLI and socket API are the same surface — agents can drive it programmatically: spawn panes, send prompts to other agents, wait until another agent is genuinely blocked before intervening. This makes "agents managing agents" workflows possible.

**Runs what you already run**

Herdr doesn't wrap or replace any AI coding agent — it just owns their terminals. Supported: Claude Code, Codex, Cursor, opencode, Grok, and anything else running in a terminal. If you're using an agent, Herdr can take over its terminal session directly.

**Keyboard and mouse, both first-class**

tmux-style prefix keys (`ctrl+b`) plus click, drag, and split. Not "choose keyboard or mouse" — switch between them per moment.

**Plugin marketplace**

Third-party plugins extend pane behavior and workflows. Browse at [herdr.dev/plugins](https://herdr.dev/plugins/).

---

### Install

```bash
# macOS/Linux
curl -fsSL https://herdr.dev/install.sh | sh

# Homebrew
brew install herdr

# mise
mise use -g herdr

# Windows (beta)
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

Then start it in your working directory:

```bash
herdr
```

Run your agents, split panes, close the browser — Herdr handles the rest.

```bash
ctrl+b q   # detach (keeps running in background)
herdr      # reattach
```

---

### Technical Details

**Single Rust binary, no Electron**: herdr doesn't need Node or a browser engine. It runs in whatever terminal you already have — small, fast, no extra memory overhead.

**Socket API**: Beyond the CLI, herdr exposes a socket API so agents can programmatically control panes, query status, and send input. This is the foundation for inter-agent coordination.

**Session persistence**: Session state can sync remotely and be shared across machines ([remote persistence docs](https://herdr.dev/docs/persistence-remote/)).

**Build from source**:

```bash
git clone https://github.com/herdrdev/herdr
cd herdr
cargo build --release
just test    # unit tests
just check   # formatting, tests, maintenance checks
```

---

### Why Now

Multi-agent workflows are the direction of coding in 2026 — not one agent doing everything, but multiple specialized agents running in parallel, waiting on each other, triggering each other.

There was no runtime for this before. You'd write tmux scripts, use screen, or open a pile of terminal windows and watch them by eye. Herdr is the first terminal runtime with "managing a herd of agents" as the core design goal.

26,500+ stars since March 2026 shows the demand is real, and a single Rust binary with zero extra dependencies brings the barrier to entry close to zero.

---

### Quick Start

```bash
brew install herdr

# In your project directory
herdr

# In pane 1 — run Claude Code
claude

# ctrl+b " — horizontal split, run Codex in pane 2
codex

# ctrl+b q — detach; both agents keep running
# Tomorrow: herdr to reattach, check status
```

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
