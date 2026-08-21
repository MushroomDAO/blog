---
title: "OpenAI Codex CLI：108K stars 的开源终端编码 Agent，Rust 重写，ChatGPT 账号直接登录"
titleEn: "openai-codex-cli-rust-terminal-coding-agent-chatgpt-open-source"
description: "openai/codex 是 OpenAI 开源（Apache 2.0）的本地终端编码 Agent，108K stars，Rust 实现，16.5K forks。支持 ChatGPT Plus/Pro/Business 账号直连（无需 API Key），四种部署形态（CLI/IDE/桌面应用/云端 Web），内置 Skills 系统、Slash 命令、AGENTS.md 支持、执行策略沙箱。OpenAI 同时设立 100 万美元开源基金，每个项目最高 2.5 万美元 API 额度。背后是 AI 编码 Agent 生态的正面竞争：Claude Code、DeepSeek Harness 之后，OpenAI 用开源回应。"
descriptionEn: "openai/codex is OpenAI's open-source (Apache 2.0) local terminal coding agent — 108K stars, Rust implementation, 16.5K forks. Supports ChatGPT Plus/Pro/Business account login (no API key required), four deployment modes (CLI/IDE/desktop app/cloud web), built-in Skills system, Slash commands, AGENTS.md support, execution policy sandbox. OpenAI launched a $1M open-source fund with grants up to $25K API credits. Context: the coding agent ecosystem's competitive response — Claude Code, DeepSeek Harness, now OpenAI going open-source."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["AI编码Agent", "OpenAI", "Codex", "开源", "Rust", "终端工具", "ChatGPT", "编码工具"]
heroImage: "../../assets/images/openai-codex-cli-rust-terminal-coding-agent-chatgpt-open-source-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：openai/codex  
文档：developers.openai.com/codex  
许可证：Apache 2.0  
语言：Rust  
Stars：108K · Forks：16.5K  
创建：2025-04-13

---

108,598 stars，16,568 forks，13,289 个 open issues。这是 openai/codex 当前的数字。

这个数字是什么量级的参照？GitHub 上同类开发者工具里，这个体量大约在前 50 名之内。而它在 GitHub 上存在的时间只有一年多。

---

## 一、什么是 Codex CLI

Codex CLI 是 OpenAI 开源的本地终端编码 Agent，用 Rust 实现，Apache 2.0 协议。它在你的计算机本地运行，可以读写文件、执行命令、进行多轮对话式编码——这个定位和 Claude Code 基本一致。

四种接入形态：

| 形态 | 入口 |
|------|------|
| **终端 CLI**（主体） | `codex`，在任意目录运行 |
| **IDE 集成** | VS Code / Cursor / Windsurf 插件 |
| **桌面应用** | `codex app`，图形界面 |
| **云端 Web** | chatgpt.com/codex（Codex Web，云端 Agent） |

本文聚焦 CLI 主体。

---

## 二、安装：四条路径

**Mac / Linux（推荐）**
```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

**Windows**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

**npm**
```bash
npm install -g @openai/codex
```

**Homebrew**
```bash
brew install --cask codex
```

安装完成后直接运行 `codex`。

安装脚本默认从 `releases.openai.com/codex` 下载，如果访问有问题可以强制走 GitHub Releases：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false sh
```

也可以直接从 [GitHub Releases](https://github.com/openai/codex/releases/latest) 下载对应平台的二进制：

- macOS Apple Silicon：`codex-aarch64-apple-darwin.tar.gz`
- macOS x86_64：`codex-x86_64-apple-darwin.tar.gz`
- Linux x86_64：`codex-x86_64-unknown-linux-musl.tar.gz`
- Linux arm64：`codex-aarch64-unknown-linux-musl.tar.gz`

---

## 三、登录：ChatGPT 账号 vs API Key

**推荐方式：ChatGPT 账号登录**

运行 `codex` 后选 **Sign in with ChatGPT**。这意味着：

- Plus、Pro、Business、Edu、Enterprise 计划用户**无需单独购买 API 额度**
- 直接复用 ChatGPT 订阅，Codex 使用量包含在计划内
- 这个设计与 Claude Code 的「claude.ai 账号登录」策略完全对应

**替代方式：API Key**

需要额外配置，适合没有 ChatGPT 订阅但有 OpenAI API 访问权限的场景。

---

## 四、核心功能

### Skills 系统

Codex CLI 有独立的 Skills 系统（`docs/skills.md`），允许扩展 Agent 的能力集——类似 Claude Code 的 skills 机制。具体文档在 `developers.openai.com/codex/skills`。

### Slash 命令

内置 Slash 命令集（`docs/slash_commands.md`），在对话中用 `/` 触发特定行为。

### AGENTS.md 支持

Codex 读取仓库内的 `AGENTS.md` 文件获取项目级别的 Agent 指导——这是业界正在形成的标准：`CLAUDE.md`（Claude Code）、`AGENTS.md`（Codex / OpenCode）定义各自的指导格式。

### 执行策略与沙箱

`docs/execpolicy.md` 和 `docs/sandbox.md` 对应 Codex 的安全机制：哪些命令需要用户确认（审批流），执行环境如何隔离。

---

## 五、100 万美元开源基金

OpenAI 随 Codex 同步设立了**「Codex Open Source Fund」**：

- 总额：**100 万美元**
- 单项上限：**$25,000 API 额度**
- 申请方式：滚动审核，随时可申请（[申请页](https://openai.com/form/codex-open-source-fund/)）
- 面向：使用 Codex CLI 或其他 OpenAI 模型的开源项目

这个配套动作有明显的生态建设意图：降低独立开发者和开源项目的试用成本，同时建立对 Codex 生态的早期绑定。

---

## 六、生态背景：编码 Agent 的开源竞争

用户的观察很准确：这波开源是有竞争背景的。

2025 年以来，「本地终端编码 Agent」这个品类快速形成：

- **Claude Code**（Anthropic，2025 年初）：claude.ai 账号，命令行，广泛采用
- **DeepSeek Harness（dsh）**（DeepSeek，2025 年下半年起）：插件架构，多 harness，生态迅速扩张，DanceGRPO / SRPO / FastVideo 等大量项目基于它构建
- **OpenCode**：轻量替代，MCP 支持
- **Hermes**：另一个开放 harness

OpenAI 的 Codex 在这个格局里的位置是：**原厂出品 + ChatGPT 账号直连 + 开源**。Rust 重写说明有认真在优化二进制大小和运行速度；Apache 2.0 说明不打算在许可证上设障碍；Skills + AGENTS.md + Slash 命令说明在往「可编程的 Agent 框架」方向走，而不只是一个聊天工具。

108K stars 意味着这条赛道的需求是真实的，而各家都在加速。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenAI Codex CLI: 108K-Star Open-Source Terminal Coding Agent, Rust, ChatGPT Login

*by Mycelium Protocol*

---

GitHub: openai/codex  
Docs: developers.openai.com/codex  
License: Apache 2.0  
Language: Rust  
Stars: 108K · Forks: 16.5K  
Created: 2025-04-13

---

108,598 stars, 16,568 forks, 13,289 open issues. For a developer tool that's been on GitHub just over a year, this puts openai/codex in the top tier of the platform.

---

### What It Is

Codex CLI is OpenAI's open-source local terminal coding agent, implemented in Rust, Apache 2.0. It runs locally, can read/write files, execute commands, and engage in multi-turn conversational coding — the same positioning as Claude Code.

Four deployment modes:

| Mode | Entry |
|------|-------|
| **Terminal CLI** (core) | `codex`, runs in any directory |
| **IDE integration** | VS Code / Cursor / Windsurf plugins |
| **Desktop app** | `codex app` |
| **Cloud Web** | chatgpt.com/codex (cloud agent) |

---

### Install

```bash
# Mac/Linux
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# npm
npm install -g @openai/codex

# Homebrew
brew install --cask codex

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Direct binary downloads available for macOS (arm64/x86_64) and Linux (x86_64/arm64) via GitHub Releases.

---

### Authentication: ChatGPT Account or API Key

**Recommended: ChatGPT account sign-in.** Plus, Pro, Business, Edu, and Enterprise plan users get Codex included in their subscription — no separate API credits required. This mirrors Claude Code's claude.ai account login strategy exactly.

**Alternative: API key** — for users with OpenAI API access but no ChatGPT subscription.

---

### Core Features

**Skills system**: Extensible capability set via `docs/skills.md`. Similar to Claude Code's skills mechanism — documented at `developers.openai.com/codex/skills`.

**Slash commands**: Built-in `/` command set for triggering agent behaviors in conversation.

**AGENTS.md support**: Codex reads `AGENTS.md` from the repo root for project-level agent guidance — one half of the emerging dual-standard alongside `CLAUDE.md`.

**Execution policy and sandbox**: `execpolicy.md` and `sandbox.md` cover which commands require user approval and how the execution environment is isolated.

---

### $1M Open-Source Fund

OpenAI launched the **Codex Open Source Fund** alongside the CLI:

- Total pool: **$1,000,000**
- Per-project grant cap: **$25,000 in API credits**
- Rolling review, [apply here](https://openai.com/form/codex-open-source-fund/)
- For: open source projects using Codex CLI or other OpenAI models

This is ecosystem-building: lower the barrier for independent developers and open source projects, establish early lock-in to the Codex ecosystem.

---

### The Competitive Context

The "local terminal coding agent" category formed fast, and this open-sourcing has a competitive backdrop:

- **Claude Code** (Anthropic, early 2025): claude.ai account, CLI, widely adopted
- **DeepSeek Harness (dsh)** (DeepSeek, H2 2025): plugin architecture, multiple harnesses, ecosystem rapidly expanding — DanceGRPO, SRPO, FastVideo, and many others build on it
- **OpenCode**: lightweight alternative, MCP support
- **Hermes**: another open harness

OpenAI's position in this landscape: **first-party + ChatGPT account login + open source**. Rust rewrite signals investment in binary size and runtime speed. Apache 2.0 means no license friction. Skills + AGENTS.md + slash commands means moving toward "programmable agent framework" rather than just a chat tool.

108K stars confirm the demand is real. All the major players are accelerating.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
