---
title: "Vicoa：手机上发任务，电脑同时跑八个 Agent——ADE 全平台开源"
titleEn: "Vicoa: Send Tasks from Your Phone, Run Eight Agents in Parallel on Desktop — ADE Goes Fully Open Source"
description: "vicoa-ai/vicoa 全平台开源 ADE（Agent 开发环境），支持 Claude Code/Codex/OpenCode/Gemini/Cursor/Copilot/Kimi/Hermes 八种 Agent，每个 Agent 独立 Worktree 并行，iOS/Android 原生 App，任务面板+定时任务，Docker 一键自部署。"
descriptionEn: "vicoa-ai/vicoa is a fully open-source ADE (Agent Development Environment) supporting 8 coding agents (Claude Code, Codex, OpenCode, Gemini, Cursor, Copilot, Kimi, Hermes), parallel worktrees per agent, native iOS/Android apps, task board + cron automations, Docker self-hosting."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["agent", "ADE", "Claude Code", "Codex", "open source", "mobile", "worktree", "self-hosted", "Flutter", "Electron"]
heroImage: "../../assets/images/vicoa-ai-agent-orchestrator-desktop-mobile-worktree-claude-codex-banner.jpg"
author: "Mycelium Protocol"
---

## 一个被忽视的需求

你有三个任务要跑：一个给 Claude Code 重构模块，一个给 Codex 写测试，一个给 OpenCode 做文档。现在你需要打开三个终端，切换三个目录，分别跟三个 Agent 说话，还要自己保证它们不会踩同一个 Git 分支。

**Vicoa** 解决的正是这个问题。它的定义很简单：

> **ADE — Agent Development Environment。** 像 IDE 管代码一样，统一管理一支 Coding Agent 团队。

全平台开源刚刚宣布：CLI/守护进程 + Web 前端 + Electron 桌面端 + Flutter 移动端，一套代码，任意设备部署和控制。

---

## 支持哪八个 Agent

| Agent | 集成方式 |
|---|---|
| Claude Code | 原生集成 |
| OpenAI Codex | 原生集成 |
| OpenCode | ACP 协议 |
| Google Gemini | ACP 协议 |
| Cursor | ACP 协议 |
| GitHub Copilot | ACP 协议 |
| Kimi | ACP 协议 |
| Hermes | ACP 协议 |

Claude Code 和 Codex 有专门的原生集成；其余通过 **ACP（Agent Client Protocol）** 接入——这是一个开放协议，意味着以后可以扩展到更多 Agent，而不需要修改 Vicoa 核心。

---

## Worktree 并行：每个 Agent 独立分支

这是 Vicoa 在工程上最关键的设计：**每个 Agent 运行在自己独立的 Git Worktree 上**。

普通方案是多个 Agent 共享一个工作目录——它们会互相覆盖对方的修改，或者争同一个分支锁。Vicoa 给每个 Agent 分配一个 Worktree，天然隔离，互不干扰，同一个项目可以真正地并行开工。

本地守护进程负责 spawn 每个 Agent 进程，通过 FastAPI + WebSocket 把状态推到任意客户端。你在手机上看到的实时进度，和桌面端是同一个状态流。

---

## 移动端：不在电脑旁边也能继续

Vicoa 的 iOS 和 Android 原生 App（Flutter 实现）不是桌面端的简化版——它有几个专门为移动场景设计的功能：

- **推送通知**：Agent 任务完成、出错、需要确认——不用盯着屏幕
- **语音输入（Dictation）**：对着手机说需求，直接发给 Agent
- **Git Diff 查看**：Agent 改完了什么，直接在手机上 review

睡前把任务发出去，早上起来看结果——这是 Vicoa 想支持的工作模式。

---

## 任务面板与定时任务

Vicoa 有一个完整的任务管理层：

- **任务面板**（Task Board）：类似看板，追踪各 Agent 的任务状态
- **自动化**（Automations）：cron 定时任务，比如每晚 23:00 让 Codex 跑测试套件，或者每周一早上让 Claude Code 生成周报草稿
- **Skills 管理**：集中管理各 Agent 可用的 Skill，不需要每台机器单独配置

---

## 架构

```
本地守护进程（Python FastAPI）
  ├── spawn Claude Code 进程（Worktree A）
  ├── spawn Codex 进程（Worktree B）
  └── spawn OpenCode 进程（Worktree C）
        ↓ WebSocket
┌──────────────────────────────────┐
│  Web（Next.js 15 + React 19）    │
│  Desktop（Electron）             │
│  Mobile（Flutter iOS/Android）   │
└──────────────────────────────────┘
        ↓ PostgreSQL
  持久化：任务/会话/Agent 状态/Automation 规则
```

守护进程是核心——它是跑在你本地机器（或 VPS）上的那个进程，管理所有 Agent 子进程。客户端只是界面，可以是浏览器、Electron 窗口、或者手机 App，都连接到同一个守护进程。

---

## 安装

### CLI（推荐入口）

```bash
# Node
npm i -g @vicoa/cli

# 或 Python
pip install vicoa
```

### 自部署（Docker Compose）

```bash
git clone https://github.com/vicoa-ai/vicoa.git
cd vicoa
docker compose up -d
```

Docker Compose 包含守护进程 + PostgreSQL + Web 前端，一条命令拉起完整服务。自部署意味着你的 Agent session、任务历史和 API Key 全部留在自己的机器上。

---

## 谁需要 Vicoa

**同时用多个 Agent 的开发者**：你已经在 Claude Code、Codex、Cursor 之间切换——Vicoa 把这些工具统一到一个控制面板里，不再需要手动管理多个终端窗口和分支。

**远程/外出工作**：任务跑起来之后离开电脑，手机上继续监控和交互，Agent 完成了推通知告诉你。不需要保持 SSH 连接或者 VPN 隧道。

**团队 Agent 协作**：自部署到内网服务器，团队成员通过 Web 界面共享同一个 Agent 环境，不用每个人各自配置一套本地环境。

**Agent 工作流研究**：Vicoa 的 Worktree 并行 + ACP 协议栈是一个研究多 Agent 协同的实验平台，可以直接在上面测试不同 Agent 的分工策略。

---

## 当前状态

刚刚宣布全平台开源（1 ⭐，初期）。CLI/守护进程、Web 前端、Electron 桌面端、Flutter 移动端均已开源。Claude Code 和 Codex 原生集成就绪；其余 Agent 通过 ACP 接入。自部署文档和 Docker Compose 配置随仓库一起发布。

早期项目，API 和协议有可能变动，但整体架构已经稳定。

---

## 总结

Vicoa 做的事情是把"使用 AI Coding Agent"从单个终端操作，升级为一个可以跨设备、多 Agent 并行的完整工作环境。关键设计决策是三个：Worktree 隔离保证并行不冲突；本地守护进程 + 多客户端保证随处可用；ACP 开放协议保证 Agent 可扩展。如果你已经在多个 Agent 之间来回切换，Vicoa 提供了一个统一的控制层。

**GitHub**: [vicoa-ai/vicoa](https://github.com/vicoa-ai/vicoa)  
**安装**: `npm i -g @vicoa/cli` 或 `pip install vicoa`  
**自部署**: `docker compose up -d`

<!--EN-->

## Vicoa: Send Tasks from Your Phone, Run Eight Agents in Parallel on Desktop

You have three tasks to run: one for Claude Code to refactor a module, one for Codex to write tests, one for OpenCode to generate docs. Today that means three terminals, three directories, three separate conversations — and manually ensuring they don't collide on the same Git branch.

**Vicoa** is built for this problem. Its definition:

> **ADE — Agent Development Environment.** Manage a team of coding agents the way an IDE manages code.

The full-platform open-source release was just announced: CLI/daemon + Web + Electron desktop + Flutter mobile, one stack, deployable and controllable from any device.

### Eight Supported Agents

| Agent | Integration |
|---|---|
| Claude Code | Native |
| OpenAI Codex | Native |
| OpenCode | ACP protocol |
| Google Gemini | ACP protocol |
| Cursor | ACP protocol |
| GitHub Copilot | ACP protocol |
| Kimi | ACP protocol |
| Hermes | ACP protocol |

Claude Code and Codex have dedicated native integrations. The rest connect via **ACP (Agent Client Protocol)** — an open protocol that makes future agents addable without changes to Vicoa's core.

### Worktree Parallelism: Every Agent on Its Own Branch

This is the key engineering decision. **Each agent runs in its own isolated Git worktree.** The typical alternative — multiple agents sharing a working directory — means overwrites and branch collisions. Vicoa gives each agent its own worktree: naturally isolated, genuinely parallel, no locks to manage.

A local daemon spawns each agent subprocess and pushes state via FastAPI + WebSocket to any connected client. The real-time progress you see on your phone is the same state stream as the desktop.

### Mobile: Keep Going When You're Away from the Desk

Vicoa's native iOS and Android apps (Flutter) aren't simplified desktop ports — they have features designed specifically for mobile:

- **Push notifications**: task completed, errored, needs input — no need to watch a screen
- **Dictation**: speak your requirements, send directly to the agent
- **Git diff review**: see what the agent changed, on your phone

Send tasks before sleep, review results in the morning — that's the workflow Vicoa is designed for.

### Task Board and Automations

Vicoa has a complete task management layer:

- **Task Board**: kanban-style tracking of all agent task states
- **Automations**: cron schedules — e.g., run the test suite every night at 23:00, or generate a weekly draft every Monday morning
- **Skills management**: centrally manage which skills are available to each agent, no per-machine setup needed

### Architecture

```
Local daemon (Python FastAPI)
  ├── spawn Claude Code (Worktree A)
  ├── spawn Codex (Worktree B)
  └── spawn OpenCode (Worktree C)
        ↓ WebSocket
┌───────────────────────────────┐
│  Web (Next.js 15 + React 19)  │
│  Desktop (Electron)           │
│  Mobile (Flutter iOS/Android) │
└───────────────────────────────┘
        ↓ PostgreSQL
  Persist: tasks / sessions / agent state / automation rules
```

The daemon runs on your local machine or a VPS and manages all agent subprocesses. Clients — browser, Electron window, phone app — are just views connected to the same daemon.

### Install

```bash
# Node
npm i -g @vicoa/cli

# Python
pip install vicoa
```

### Self-Host

```bash
git clone https://github.com/vicoa-ai/vicoa.git
cd vicoa
docker compose up -d
```

Docker Compose brings up the daemon + PostgreSQL + web frontend in one command. Self-hosting means your agent sessions, task history, and API keys stay on your own infrastructure.

### Who It's For

**Developers already switching between multiple agents**: Claude Code, Codex, Cursor — Vicoa unifies them in one control plane, no more managing separate terminal windows and branches.

**Remote/away-from-desk work**: Start tasks and walk away. Monitor on your phone, get notified when agents finish. No need to keep an SSH connection alive.

**Team agent collaboration**: Self-host on an internal server, share one agent environment across a team via the web UI — no per-person local setup.

**Multi-agent workflow research**: Vicoa's worktree parallelism + ACP protocol stack is a ready-made experimental platform for testing agent division-of-labor strategies.

### Current Status

Just announced full open-source release (early, ⭐1). CLI/daemon, web frontend, Electron desktop, and Flutter mobile are all open-sourced. Claude Code and Codex native integrations are ready; other agents connect via ACP. Self-hosting docs and Docker Compose ship with the repo.

Early-stage project — APIs and protocol may evolve — but the architecture is solid.

### Summary

Vicoa upgrades "using AI coding agents" from a single-terminal operation to a multi-device, multi-agent parallel environment. Three key design decisions: worktree isolation for collision-free parallelism; local daemon + multi-client for ubiquitous access; ACP open protocol for extensible agent support. If you're already switching between multiple agents, Vicoa provides a unified control layer.

**GitHub**: [vicoa-ai/vicoa](https://github.com/vicoa-ai/vicoa)  
**Install**: `npm i -g @vicoa/cli` or `pip install vicoa`  
**Self-host**: `docker compose up -d`
