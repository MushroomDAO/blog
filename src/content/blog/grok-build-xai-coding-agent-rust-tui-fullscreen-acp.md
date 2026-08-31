---
title: "Grok Build：xAI 开源 Rust 编码 Agent，全屏 TUI + ACP 协议"
titleEn: "Grok Build: xAI Open-Sources Its Rust Coding Agent — Fullscreen TUI and ACP Protocol"
description: "xai-org/grok-build ⭐26283，SpaceXAI（xAI）开源的终端编码 Agent，Rust 实现，全屏鼠标交互 TUI，支持文件编辑/命令执行/网页搜索/长任务，交互/无头/编辑器嵌入三种模式，ACP 协议，MCP/Skills/插件/沙盒，Apache 2.0。"
descriptionEn: "xai-org/grok-build ⭐26283 — SpaceXAI's open-source terminal coding agent in Rust, fullscreen mouse-interactive TUI, file editing/shell execution/web search/long-task management, interactive/headless/editor-embedded modes, ACP protocol, MCP/Skills/plugins/sandboxing, Apache 2.0."
pubDate: 2026-08-31
updatedDate: 2026-08-31
category: "Tech-News"
tags: ["AI coding agent", "Rust", "TUI", "xAI", "open source", "MCP", "ACP", "terminal", "coding tools"]
heroImage: "../../assets/images/grok-build-xai-coding-agent-rust-tui-fullscreen-acp-banner.jpg"
author: "Mycelium Protocol"
---

## xAI 把自己的编码 Agent 开源了

SpaceXAI（即 Elon Musk 的 xAI）将其内部编码 Agent 工具 **Grok Build**（命令：`grok`）以 Apache 2.0 开源。

一句话描述：**用 Rust 写的、全屏终端界面的 AI 编码 Agent**，理解代码库、编辑文件、执行命令、搜索网页、管理长任务——既可以交互使用，也可以无头运行用于脚本和 CI，还能通过 ACP（Agent Client Protocol）嵌入编辑器。

2026年7月开源以来，⭐ **26,283**，fork **4,935**，是目前 AI 编码 Agent 赛道里开源速度最快的项目之一。

---

## 全屏 TUI：不是 CLI，是界面

大多数编码 Agent 是"对话框式"——你输入问题，它输出回答，像一个增强版的终端。

Grok Build 选了不同的方向：**全屏 TUI（终端用户界面）**，支持鼠标交互，有滚动历史、提示符、模态窗口、渲染层。用起来更接近 IDE 的终端面板，而不是一个 chat 窗口。

代码组织上，TUI 层（`xai-grok-pager`）和 Agent 运行时（`xai-grok-shell`）是分开的——UI 和 Agent 逻辑解耦，各自可以独立开发。

---

## 三种运行模式

| 模式 | 用途 |
|---|---|
| **交互模式** | 全屏 TUI，日常开发使用 |
| **无头模式（Headless）** | 脚本、CI/CD 管道，不需要 UI |
| **编辑器嵌入（ACP）** | 通过 Agent Client Protocol 嵌入 Cursor、VS Code 等编辑器 |

ACP（Agent Client Protocol）是 xAI 实现的开放协议，让 Grok Build 可以作为后端 Agent 被任意支持 ACP 的编辑器调用——就像 LSP 是语言服务器协议，ACP 是 Agent 服务器协议。

---

## Agent 能力

- **文件编辑**：读取、修改、创建文件
- **Shell 命令执行**：在受控环境里跑终端命令
- **网页搜索**：直接从 Agent 里搜索外部信息
- **长任务管理**：追踪和管理运行时间长的任务
- **沙盒隔离**：可配置的沙盒执行环境，限制 Agent 的操作范围

---

## 扩展生态

Grok Build 有完整的扩展机制：

- **MCP Servers**：接入 Model Context Protocol 生态
- **Skills**：可复用的技能包
- **Plugins**：插件系统
- **Hooks**：在操作前后注入自定义逻辑
- **主题（Theming）**：自定义 TUI 外观

---

## 代码库结构

| Crate | 职责 |
|---|---|
| `xai-grok-pager` | TUI 层：滚动历史、提示符、模态窗口、渲染 |
| `xai-grok-shell` | Agent 运行时：leader / stdio / headless 入口 |
| `xai-grok-tools` | 工具实现：终端、文件编辑、搜索等 |
| `xai-grok-workspace` | 宿主文件系统、VCS、执行环境、检查点 |

值得注意的是 `THIRD-PARTY-NOTICES`——其中明确记录了 **openai/codex 和 sst/opencode 的工具实现被移植进了 grok-build**，并附有 Apache §4(b) 变更声明。这说明 xAI 在构建自己的工具层时参考和整合了开源生态里的现有实现。

---

## 安装

```bash
# macOS / Linux / Git Bash
curl -fsSL https://x.ai/cli/install.sh | bash
grok --version

# Windows PowerShell
irm https://x.ai/cli/install.ps1 | iex
```

首次启动会在浏览器打开认证页面。二进制产物原名 `xai-grok-pager`，官方安装脚本把它重命名为 `grok`。

**从源码构建（需要 Rust + DotSlash）**：

```bash
cargo install dotslash              # 前置依赖
cargo run -p xai-grok-pager-bin    # 构建并启动 TUI
cargo build -p xai-grok-pager-bin --release  # 发布版本
```

---

## 注意事项

**不接受外部贡献**（`CONTRIBUTING.md` 明确说明）。这个仓库是从 xAI 内部 monorepo 周期性同步出来的镜像，外部 PR 不会被合并。但代码是完整的、可读的、可构建的，fork 自用没有问题。

---

## 和其他编码 Agent 的定位对比

| 工具 | 底层语言 | 界面 | 来源 |
|---|---|---|---|
| **Grok Build** | Rust | 全屏 TUI + ACP | xAI（SpaceXAI）|
| Claude Code | TypeScript | CLI / TUI | Anthropic |
| OpenAI Codex | TypeScript | CLI | OpenAI |
| OpenCode | Go | TUI | SST |
| Gemini CLI | TypeScript | CLI | Google |

Grok Build 选择 Rust 和全屏 TUI，加上 ACP 作为编辑器集成协议，是几个主流编码 Agent 里技术栈选择最激进的一个。

---

## 总结

Grok Build 是 xAI 把自己内部使用的编码 Agent 工具开源出来的产物。Rust + 全屏 TUI 的技术路线，交互/无头/ACP 三种运行模式，完整的 MCP/Skills 扩展生态——26k Star 说明这个定位有真实需求。不接受外部 PR，但代码完整公开，是一个可以深读和 fork 的参考实现。

**GitHub**: [xai-org/grok-build](https://github.com/xai-org/grok-build) ⭐26283  
**官网**: [x.ai/cli](https://x.ai/cli)  
**文档**: [docs.x.ai/build/overview](https://docs.x.ai/build/overview)

<!--EN-->

## Grok Build: xAI Open-Sources Its Rust Coding Agent

SpaceXAI (Elon Musk's xAI) has open-sourced **Grok Build** (`grok`) — their internal coding agent — under Apache 2.0.

One sentence: a **Rust-built, fullscreen-terminal AI coding agent** that understands codebases, edits files, executes shell commands, searches the web, and manages long-running tasks — interactive for daily use, headless for scripts and CI, or embedded in editors via ACP (Agent Client Protocol).

Since opening in July 2026: ⭐**26,283**, **4,935** forks — among the fastest-growing open-source coding agent repos.

### Fullscreen TUI: Not a Chat Window

Most coding agents are chat-style — you type, it outputs, like an enhanced terminal prompt. Grok Build takes a different approach: a **fullscreen TUI** with mouse interaction, scrollback, prompt, modal windows, and a dedicated rendering layer. It feels closer to an IDE's terminal panel than a chat box.

The TUI layer (`xai-grok-pager`) and the agent runtime (`xai-grok-shell`) are separate crates — UI and agent logic decoupled for independent development.

### Three Run Modes

| Mode | Use |
|---|---|
| **Interactive** | Fullscreen TUI for daily development |
| **Headless** | Scripts, CI/CD pipelines, no UI needed |
| **Editor-embedded (ACP)** | Via Agent Client Protocol into Cursor, VS Code, etc. |

ACP (Agent Client Protocol) is xAI's open protocol for embedding Grok Build as a backend agent in any ACP-compatible editor — the way LSP is a server protocol for language tooling, ACP is a server protocol for agents.

### Agent Capabilities

- **File editing**: read, modify, create files
- **Shell command execution**: run terminal commands in a controlled environment
- **Web search**: search external information from within the agent
- **Long-task management**: track and manage extended-duration tasks
- **Sandboxed execution**: configurable sandboxing to constrain the agent's action scope

### Extension Ecosystem

- **MCP Servers**: Model Context Protocol integration
- **Skills**: reusable skill packages
- **Plugins**: plugin system
- **Hooks**: inject custom logic before/after operations
- **Theming**: custom TUI appearance

### Codebase Layout

| Crate | Responsibility |
|---|---|
| `xai-grok-pager` | TUI: scrollback, prompt, modals, rendering |
| `xai-grok-shell` | Agent runtime: leader / stdio / headless entry points |
| `xai-grok-tools` | Tool implementations: terminal, file edit, search, … |
| `xai-grok-workspace` | Host filesystem, VCS, execution environment, checkpoints |

Notable: `THIRD-PARTY-NOTICES` explicitly records that **openai/codex and sst/opencode tool implementations were ported into grok-build**, with Apache §4(b) change notices. xAI integrated and built on top of existing open-source implementations in the tool layer.

### Install

```bash
# macOS / Linux / Git Bash
curl -fsSL https://x.ai/cli/install.sh | bash
grok --version

# Windows PowerShell
irm https://x.ai/cli/install.ps1 | iex
```

First launch opens your browser for authentication. The binary is built as `xai-grok-pager`; the install script renames it to `grok`.

**Build from source (requires Rust + DotSlash)**:

```bash
cargo install dotslash
cargo run -p xai-grok-pager-bin           # build and launch TUI
cargo build -p xai-grok-pager-bin --release
```

### Important: No External Contributions

`CONTRIBUTING.md` explicitly states external contributions are not accepted. This repo is a periodic mirror from xAI's internal monorepo — external PRs won't be merged. But the code is complete, readable, and buildable — forking for personal use is fine.

### Positioning vs. Other Coding Agents

| Tool | Language | Interface | Origin |
|---|---|---|---|
| **Grok Build** | Rust | Fullscreen TUI + ACP | xAI (SpaceXAI) |
| Claude Code | TypeScript | CLI / TUI | Anthropic |
| OpenAI Codex | TypeScript | CLI | OpenAI |
| OpenCode | Go | TUI | SST |
| Gemini CLI | TypeScript | CLI | Google |

Grok Build's bet on Rust, fullscreen TUI, and ACP as an editor integration protocol is the most technically distinct choice among the major coding agents.

### Summary

Grok Build is xAI's open-sourced internal coding agent. Rust + fullscreen TUI, three run modes (interactive / headless / ACP), and a complete MCP/Skills extension ecosystem. 26k stars confirms the positioning has real demand. External PRs aren't accepted, but the code is fully public — a readable, buildable reference implementation.

**GitHub**: [xai-org/grok-build](https://github.com/xai-org/grok-build) ⭐26283  
**Website**: [x.ai/cli](https://x.ai/cli)  
**Docs**: [docs.x.ai/build/overview](https://docs.x.ai/build/overview)
