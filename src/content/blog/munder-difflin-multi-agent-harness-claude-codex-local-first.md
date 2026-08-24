---
title: "Munder Difflin：本地优先多 Agent Harness，把 Claude Code / Codex / Grok 包成一群克隆员工"
titleEn: "munder-difflin-multi-agent-harness-claude-codex-local-first"
description: "Munder Difflin（MIT，3888 stars，Electron+React+TypeScript）是一个本地多 Agent Harness 桌面应用，把 Claude Code、OpenAI Codex、xAI Grok、Kimi Code、Qwen、GitHub Copilot CLI 等 12 种 CLI 包成真实 PTY 进程，用像素风 The Office 场景可视化——每个 Agent 是一个在办公室走动的角色，邮件在桌间飞来飞去。GOD Agent（Michael）负责任务路由和协调，你只和 Michael 说话，Michael 调度整个 Agent 舰队。本地优先，支持 BYOK 和 Ollama 本地模型，含快速语义记忆层、Kanban 任务板、内置 Monaco IDE、Slack 集成和 Agent 图库。"
descriptionEn: "Munder Difflin (MIT, 3888 stars, Electron+React+TypeScript) is a local-first multi-agent harness desktop app. It wraps Claude Code, OpenAI Codex, xAI Grok, Kimi Code, Qwen, GitHub Copilot CLI, and 9 other CLIs as real PTY processes, visualized in a pixel-art The Office-themed office floor — each agent walks as an avatar, envelopes fly desk-to-desk. A GOD agent (Michael) handles all routing and coordination; you talk to Michael and Michael orchestrates the fleet. Local-first, BYOK and Ollama support, fast semantic memory, Kanban, Monaco IDE, Slack integration, and an Agent Gallery."
pubDate: "2026-08-24"
updatedDate: "2026-08-24"
category: "Tech-News"
tags: ["多Agent", "Harness", "Claude Code", "开源", "本地优先", "Electron", "Munder Difflin", "Agent协调"]
heroImage: "../../assets/images/munder-difflin-multi-agent-harness-claude-codex-local-first-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：chaitanyagiri/munder-difflin  
Stars：3888 | Forks：437 | Language：JavaScript（Electron + React + TypeScript）  
License：MIT（源码）  
Version：v0.4.5（working prototype）  
平台：macOS / Windows / Linux | Discord：https://discord.gg/SEDzP5ZPk5  
网站：https://munderdiffl.in/ | Agent 图库：https://munderdiffl.in/hires/  
创建：2026-05-31 | 最近更新：2026-08-24

---

## 一句话理解

**把你的所有 AI 编程 CLI 变成一群在同一个办公室工作的员工，你只跟 Michael（总经理 Agent）说话，Michael 调度其他所有人。**

Munder Difflin 名字来自《The Office》里的虚构纸业公司 Dunder Mifflin——项目本身也是这个格调：像素风 2D 办公室，15 个 Agent 头像（The Office 角色风格），邮件在桌间飞，动画反映真实的工作状态。严肃的功能，荒诞的外壳。

---

## 支持的 Agent CLI

目前可以包进来的 CLI（每个都是真实的 PTY 进程，不是 API 调用）：

| CLI | 背后是什么 |
|-----|-----------|
| `claude` | Claude Code（默认） |
| `codex` | OpenAI Codex |
| `grok` | xAI Grok |
| `kimi` | Kimi Code |
| `qwen` | 通义千问 CLI |
| `gemini` | Gemini CLI |
| `agy` | Antigravity（Gemini 另一个入口） |
| `opencode` | OpenCode |
| `crush` | Crush |
| `pi` | pi.dev |
| `copilot` | GitHub Copilot CLI |
| `cursor` | Cursor Agent（cursor-agent） |
| 自定义命令 | 任意 CLI，含 Ollama / LM Studio / vLLM 本地模型 |

**关键点**：这里的每一个都是真实的 CLI 进程（通过 `node-pty` 在 PTY 里运行），不是通过 API 调用，不是轻量包装。你已经有的订阅、已经有的 CLI，直接用，Munder Difflin 只是把它们组织起来一起干活。

---

## 三个核心层

### 1. 办公室（The Floor）

用 Pixi.js 渲染的像素风 2D 办公室。每个 Agent 是一个走动的头像，有自己的桌子和工作站。

- Agent 在工作时走向对应的站台
- 消息传递时信封从一张桌子飞到另一张桌子
- 头像的动作状态反映真实的工作状态（基于 hook 事件）
- 美术风格：Animal Crossing × Earthbound × SNES 菜单 UI

这不是装饰——它让你在一个页面里就能看到所有 Agent 在干什么，不需要盯着多个终端。

### 2. 蜂巢（The Hive）

Agent 之间的协调机制，基于本地 git 仓库的纯文件系统：

```
你 → Michael（GOD Agent）
           │
    ┌──────┼──────┐
   A 桌   B 桌   C 桌
  Agent  Agent  Agent
    └──────────────┘
    共享：memory · mailbox · blackboard · log
```

- **每个 Agent 有自己的 outbox**，harness 的路由器负责投递到对应 inbox
- **单 committer 设计**：只有 harness 主进程提交 git，避免 `index.lock` 冲突
- **GOD Agent（Michael）** 读每一个请求，自主解决常规任务，只有关键操作（花费超限、破坏性操作、需要改变范围）才升级给你审批
- **黑板（Blackboard）**：Agent 间的共享状态，不需要通过消息传递

### 3. 记忆层（Memory）

- Markdown 优先的记忆系统，和 MemPalace 共享格式
- 语义索引，召回速度毫秒级
- 记忆压缩（condensation），不会无限增长
- **企业知识图谱**：你自己的文档和策略，所有 Agent 可查询
- 之前版本 Apple Silicon 上语义召回全部返回 NaN（CoreML 溢出），v0.4.5 已修复，强制 CPU 推理

---

## 安全与控制

**HITL 人工审批门**：

| 操作类型 | 处理方式 |
|---------|---------|
| 常规任务 | Michael 自主解决，不打扰你 |
| 花费超限 | 升级到审批队列 |
| 破坏性操作 | 需要人工确认 |
| 范围变更 | 需要人工确认 |

**熔断器（Circuit Breaker）**：三级响应——引导（steer）→ 约束（constrain）→ 停止（stop）。Agent 陷入循环、持续报错或超过 token 预算时自动触发。

**per-agent git worktrees**：可选开启，并行 Agent 不会在分支上冲突。

---

## Command Center

在 Michael 的控制台（CommandCenterPanel）里有：

| 功能 | 说明 |
|------|------|
| **Kanban 任务板** | 支持依赖关系的任务管理 |
| **Triggers（触发器）** | 按工作日、时间点执行的计划任务和心跳检测 |
| **Skills 浏览器** | 227 个技能，可搜索/过滤/安装/卸载 |
| **内置 Monaco IDE** | 文件树、编辑器标签、git 轨道（commit 图、diff、分支对比） |
| **记忆搜索** | 跨 Agent、跨会话的语义记忆查询 |
| **Activity Log** | 完整的活动历史 |
| **工具瀑布图** | 每个 Agent 的工具调用 span，可观测性视图 |
| **Prerequisites** | 一个页面显示哪些依赖工具已安装，一键让 Michael 安装缺失的 |

---

## 集成与分发

**Slack & Webhook 集成**：往 Slack 频道发消息，Michael 接收 → 生成临时 Agent → 在线程里回复 → 任务完成后销毁。

**可分享的 hire 链接**：导出 `munderdifflin://hire` 格式的链接，其他人导入后只是预填表单，还需要人工启动——不支持自动静默部署。

**Agent 图库**：https://munderdiffl.in/hires/，浏览社区共享的角色配置。

**BYOK + 本地模型**：Settings → AI Engines 里配置各供应商的 API Key，或接入 Ollama / LM Studio / vLLM 的本地端点。密钥存在 write-only 的 secret broker 里，不明文暴露。

**一键更新**：标题栏角标提示新版本，检测到更新后下载对应平台的构建包，安装后显示 release notes 设计页（不只是版本号）。

---

## 安装

```bash
git clone https://github.com/chaitanyagiri/munder-difflin.git
cd munder-difflin
npm install        # 自动 rebuild node-pty 适配 Electron ABI
npm run dev        # 启动 Electron 应用（热重载）
```

首次启动有引导向导，完成后进入办公室。点 **Add agent** 添加第一个会话——GOD Agent 会自动坐进 Michael 的办公室。

预编译版本（macOS 已签名公证、Windows、Linux）在 [releases 页面](https://github.com/chaitanyagiri/munder-difflin/releases/latest)。

---

## v0.4.5 修了什么

这个版本有三个「静悄悄在出错的 bug」：

1. **花费统计**：每次重启 app 就重置计数器，但 session id 没变，导致长期少报实际费用。现在从 ledger 折叠累积，另外单独显示本 session 数字。

2. **Apple Silicon 语义记忆**：CoreML 量化 embedding 图溢出，所有向量返回 NaN，所有 upsert 被拒绝。现在 macOS 上强制 CPU 推理。

3. **Agent 间通信**：邮件可能堆在 inbox 里没人唤醒处理。现在加了 inbox wake watchdog，废弃 nudge，不存在的 inbox 收到邮件会弹回并记录日志，不再静默丢失。

---

## 架构

```
┌─────────────────────────────────────────┐
│           Electron Renderer (React)      │
│   ┌──────────────┐  ┌─────────────────┐ │
│   │ Pixi.js 办公室│  │ xterm.js 终端   │ │
│   └──────▲───────┘  └────────▲────────┘ │
└──────────┼────────────────────┼──────────┘
           │ IPC (window.cth)
  ┌────────┴────────┐   ┌───────┴─────────┐
  │ Event Plane      │   │ Terminal Plane  │
  │ hive · hooks     │   │ node-pty PTYs   │
  │ router · GOD     │   │ + fs + git      │
  └────────▲────────┘   └───────▲─────────┘
           │ hook payloads      │ stdin/stdout
           └──────┬─────────────┘
           ┌──────┴──────────────┐
           │ claude / codex / …  │  真实 CLI 进程
           └─────────────────────┘
```

主进程不直接建模上游行为，只做：spawn PTY → 流式传输字节 → 注入 hook 事件。

---

## 路线图

已完成（v0.4.5）：12 种 Agent 引擎、声音指挥（Talk 按钮）、完整 Hive 机制、Command Center、Monaco IDE、集成注册表和 secret broker、Slack 集成、可分享 hire 和 Agent 图库、可观测性和熔断器、持久化存储、Skills 浏览器。

下一步：
- Telegram 和更多 chat 集成
- 更多 Agent 引擎和集成模板
- 更全的头像覆盖（基于真实 hook 事件驱动动画）
- 持久化的布局和命令历史

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Munder Difflin: Local-First Multi-Agent Harness — Turns Your CLIs Into a Coordinated Office of Clones

*by Mycelium Protocol*

---

GitHub: chaitanyagiri/munder-difflin  
Stars: 3888 | Forks: 437 | Language: JavaScript (Electron + React + TypeScript)  
License: MIT (source code)  
Version: v0.4.5 (working prototype)  
Platform: macOS / Windows / Linux | Discord: https://discord.gg/SEDzP5ZPk5  
Site: https://munderdiffl.in/ | Agent Gallery: https://munderdiffl.in/hires/  
Created: 2026-05-31 | Updated: 2026-08-24

---

### One Line

**Turn all your AI coding CLIs into a team of employees working in the same office. You talk to Michael (the GOD agent manager). Michael dispatches the whole fleet.**

The project name riffs on Dunder Mifflin from *The Office* — and the aesthetic matches: pixel-art 2D office, 15 avatar characters, envelopes flying between desks, animations driven by real work events. Serious functionality, absurd shell.

---

### Supported Agent CLIs

Every entry below runs as a real PTY process — not an API call, not a thin wrapper:

| CLI | Backend |
|-----|---------|
| `claude` | Claude Code (default) |
| `codex` | OpenAI Codex |
| `grok` | xAI Grok |
| `kimi` | Kimi Code |
| `qwen` | Qwen CLI |
| `gemini` | Gemini CLI |
| `agy` | Antigravity (Gemini) |
| `opencode` | OpenCode |
| `copilot` | GitHub Copilot CLI |
| `cursor` | Cursor Agent |
| custom | Any CLI, incl. Ollama / LM Studio / vLLM |

The subscriptions you already pay for. The agents you already run. Munder Difflin just organizes them into a coordinated fleet.

---

### Three Core Layers

**The Floor**

Pixi.js pixel-art 2D office. Each agent is a walking avatar with its own desk and workstation. Agents walk to stations when working; envelopes fly desk-to-desk when passing messages. Avatar state reflects real work (driven by hook events). One screen shows you what everyone is doing without juggling terminals.

**The Hive**

Coordination mechanism built on a local git repo of plain files:

```
You → Michael (GOD agent)
         │
   ┌─────┼─────┐
  Desk A  B    C
  Agent Agent Agent
    └────────────┘
    shared: memory · mailbox · blackboard · log
```

- Each agent has its own `outbox`; the harness router delivers into recipients' `inbox`
- Single-committer design: only the harness main process commits to git, preventing `index.lock` corruption
- The GOD agent (Michael) reads every request, resolves routine ones autonomously, escalates only critical items (spend, destructive ops, scope changes) to a human approvals queue
- Shared blackboard for cross-agent state, no message-passing required

**Memory**

- Markdown-first memory layer, shared format with MemPalace
- Semantic index with millisecond recall
- Condensation keeps memory from growing forever
- Enterprise Knowledge Graph: your own documents and policies, queryable by any agent
- Apple Silicon bug fixed in v0.4.5: CoreML quantized embedding graph overflowed, all vectors came back NaN. Now pinned to CPU on macOS.

---

### Safety and Control

**Human-in-the-loop gates**:

| Operation | Handling |
|-----------|---------|
| Routine tasks | Michael resolves autonomously |
| Spend limits | Escalated to approval queue |
| Destructive operations | Require human confirmation |
| Scope changes | Require human confirmation |

**Circuit breaker**: three-level response ladder — steer → constrain → stop. Triggers on runaway loops, error storms, or budget overruns.

**Per-agent git worktrees**: optional, prevents parallel agents from colliding on branches.

---

### Command Center

Inside Michael's control surface:

| Feature | Description |
|---------|-------------|
| **Kanban with dependencies** | Task board with dependency-aware scheduling |
| **Triggers** | Weekday-time scheduled missions and heartbeat monitoring |
| **Skills browser** | 227 skills with search, filters, install/uninstall |
| **Monaco IDE** | File tree, editor tabs, git rails (commit graph, diffs, branch compare) |
| **Memory search** | Cross-agent, cross-session semantic memory query |
| **Tool waterfall** | Per-agent tool-span observability view |
| **Prerequisites page** | Shows which supporting tools are installed; one button asks Michael to install what's missing |

---

### Integrations and Distribution

**Slack & webhooks**: message a channel → Michael receives → spawns an ephemeral worker → replies in-thread → tears it down when done.

**Shareable hire links**: export a `munderdifflin://hire` link; import only pre-fills the form — a human still spawns the agent. No silent auto-deployment.

**Agent Gallery**: https://munderdiffl.in/hires/ — browse community-shared role configurations.

**BYOK + local LLMs**: configure provider API keys in Settings → AI Engines, or connect Ollama / LM Studio / vLLM local endpoints. Keys stored in a write-only secret broker.

---

### Install

```bash
git clone https://github.com/chaitanyagiri/munder-difflin.git
cd munder-difflin
npm install        # postinstall rebuilds node-pty against Electron's ABI
npm run dev        # launches Electron app with hot reload
```

Pre-built binaries (macOS signed & notarized, Windows, Linux) at the [releases page](https://github.com/chaitanyagiri/munder-difflin/releases/latest).

---

### What v0.4.5 Fixed

Three bugs that were "quietly wrong":

1. **Cost reporting**: counter reset on every app restart while session ID stayed the same, silently under-reporting real spend. Now folded from the durable ledger.

2. **Apple Silicon semantic memory**: CoreML quantized embedding graph overflowed, every vector returned NaN, every upsert was rejected. Embeddings now pinned to CPU on macOS.

3. **Agent-to-agent mail delivery**: mail could sit in an inbox nobody woke up to drain. Inbox wake watchdog added; missing inboxes bounce mail with a log entry instead of silently dropping.

Also in this release: weekday-time triggers, clickable paths in every terminal, one editor instead of two, one-click updates, sandboxed renderer.

---

### Architecture

```
┌──────────────────────────────────────────┐
│          Electron Renderer (React)        │
│  ┌──────────────┐  ┌───────────────────┐ │
│  │  Pixi.js     │  │  xterm.js + tabs  │ │
│  │  office floor│  │  files, git rails │ │
│  └──────▲───────┘  └─────────▲─────────┘ │
└─────────┼───────────────────┼────────────┘
          │ IPC (window.cth)
  ┌───────┴────────┐  ┌───────┴────────┐
  │ Event Plane    │  │ Terminal Plane │
  │ hive/hooks/    │  │ node-pty PTYs  │
  │ router/GOD     │  │ + fs + git     │
  └───────▲────────┘  └───────▲────────┘
          │            hook payloads / stdin
          └──────────┬─────────────────────
             ┌───────┴──────────────┐
             │  claude/codex/grok/… │  real CLI processes
             └──────────────────────┘
```

The main process does not model upstream behavior — it spawns PTY, streams bytes, injects hook events. That's it.

---

### Roadmap

Coming next: Telegram and richer chat bridges, more agent engines, fuller avatar coverage from real hook events, durable layout and per-session command history.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
