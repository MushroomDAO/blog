---
title: "Block 开源桌面 Agent 工作台 Berd：不造新 Agent，把你手里所有 Agent 收编进同一个桌面"
titleEn: "berd-block-square-desktop-agent-workbench-tauri-goose-acp-open-source"
description: "block/berd 是 Square 母公司 Block 开源的桌面 Agent 工作台，Tauri 2 + React 19，Apache 2.0，691 stars。核心定位：不是再造一个更强的 Agent，而是把现有 Agent 统一进一个桌面界面——通过 ACP WebSocket 连接 Goose 后端，支持任意模型，内置企业发布通道分离机制（公开源码 + 私有覆盖层），可发布可移植 Agent Skill，第一个官方 Skill 是 buzz-handoff（Buzz 频道上下文导入私有 Agent 对话）。"
descriptionEn: "block/berd is Block's (Square's parent company) open-source desktop agent workbench — Tauri 2 + React 19, Apache 2.0, 691 stars. Core positioning: not building a new and stronger agent, but unifying existing agents under one desktop UI — connects to the Goose backend via ACP WebSocket, supports any model, includes an enterprise distribution seam (public source + private overlay), and publishes portable Agent Skills. First official skill: buzz-handoff (import Buzz channel/thread context into a private agent conversation)."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["桌面Agent", "Block", "Tauri", "开源", "Agent工作台", "Goose", "ACP"]
heroImage: "../../assets/images/berd-block-square-desktop-agent-workbench-tauri-goose-acp-open-source-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：block/berd
许可证：Apache License 2.0
语言：TypeScript（+ Rust via Tauri）
Stars：691 · Forks：77
创建：2026-08-11 | 最近更新：2026-08-22
来自：Block（Square 的母公司）

---

## 一、它在解决什么

现在大家手里都有一堆 Agent——Claude Code、Codex、Goose、各类 MCP 工具。每个 Agent 各自有自己的界面，各自管自己的上下文，切换起来成本极高。

Block 的回答不是「再造一个更强的 Agent」，而是：**给所有 Agent 造一个统一的桌面工作台**。

Berd 的定位只有一句话：

> *a desktop app for getting work done with any model*

关键词是 **any model**。Berd 本身不跑模型，它通过 ACP（Agent Communication Protocol）WebSocket 连接后端 Agent——默认是 Block 自己的 Goose，但接口是开放的。

---

## 二、架构：Tauri + Goose sidecar + ACP

技术栈：Tauri 2（Rust 原生壳）+ React 19 前端。Agent 逻辑不在 Berd 里，而在 Goose 后端（`goose serve` 启动一个 sidecar 进程）。两者通过 ACP WebSocket 通信。

```
Berd（Tauri 桌面 App）
      ↕ ACP WebSocket
Goose sidecar（goose serve）
      ↕
任意模型 Provider
```

这个分层设计有一个重要含义：**前端和后端可以独立迭代**。想换更新的 Goose 版本？更新 `goose-backend.lock.json` 里的锁定 commit，跑一次 `just goose-sync` 拉下来，不需要动 Berd 前端代码。想本地测自己的 Goose 分支？`GOOSE_BIN=/path/to/goose just dev` 直接绕过管理的锁定版本。

---

## 三、企业发布分层

这是 Berd 设计里值得单独说的部分。

公开仓库是一个通用版本，完全自包含，不依赖私有包注册表或企业凭据。但企业方可以在不修改公开源码的情况下，通过「发布通道分离机制（distribution seams）」覆盖：

- 私有 Agent 配置
- 托管 Provider 设置
- 可选的伴侣 CLI（companion CLI）
- 更新通道、签名、发布基础设施

公开构建和企业构建用同一套 `just bundle` 流程，区别只在私有覆盖层。这意味着企业可以分叉一个带内部配置的发布版本，但不用 fork 整个 Berd 源码——公开改进可以直接 pull 进来。

---

## 四、Agent Skill 体系

Berd 在 `skills/` 下发布可移植的 Agent Skill，独立于 App 本身可以安装使用。

第一个官方 Skill：**buzz-handoff**

功能：把 Buzz（Block 内部通讯工具）的频道或线程上下文导入私有 Agent 对话，Agent 处理完之后可以通过 Buzz CLI 发回经过明确审批的回复。

设计哲学：Skill 是跨 Agent 可移植的知识单元——装在 Berd 上能用，装在 Claude Code 或 Codex 上也能用。这和 Heinu1 / Claude Code 生态里的 Skill 体系是同一条路。

---

## 五、参与方式：只接受 issue，不接受 PR

Berd 明确写了：**不接受外部 PR，外部 PR 会被自动关闭**。参与方式只有一个——提一个格式完整的 issue。

文档里甚至给了一个可以直接丢给自己的 coding agent 的 prompt：

```
Read https://raw.githubusercontent.com/block/berd/main/CONTRIBUTING.md
and help me file a Berd issue. Interview me for anything the guide
requires that I haven't given you, and tell me if what I'm reporting
is actually two separate issues.
```

这个设计很有意思：用 Agent 帮你整理 issue，再把整理好的 issue 提给维护者。不接受外部代码贡献，但接受高质量的问题报告。

---

## 六、为什么值得关注

Agent 工作台这个方向，大家都在做：Windsurf、Cursor、Claude Code、Codex……但这些大多是「带 Agent 能力的编辑器」，而不是「以 Agent 为核心的通用桌面」。

Berd 的切入点不同——它是一个纯粹的 Agent 界面层，不捆绑特定模型，不捆绑特定工具，只做「把各种 Agent 统一收编进桌面」这一件事。Block 作为金融科技公司做这个，背后有真实的企业内部场景驱动（Buzz 集成就是一个信号）。

691 stars，发布 11 天，Apache 2.0，Tauri 技术栈，有企业发布分层。这是目前开源 Agent 工作台里架构最清晰的一个。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Block Open-Sources Berd: A Desktop Agent Workbench That Unifies All Your Agents, Not Another New One

*by Mycelium Protocol*

---

GitHub: block/berd
License: Apache License 2.0
Language: TypeScript (+ Rust via Tauri)
Stars: 691 · Forks: 77
Created: 2026-08-11 | Updated: 2026-08-22
From: Block (Square's parent company)

---

### What It Solves

Most people now have a pile of agents — Claude Code, Codex, Goose, various MCP tools. Each has its own UI, its own context management, and switching between them carries real friction.

Block's answer isn't "build a stronger agent." It's: **build a unified desktop workbench for all of them**.

Berd's positioning is one line:

> *a desktop app for getting work done with any model*

The key word is **any model**. Berd doesn't run models — it connects to a backend agent over ACP (Agent Communication Protocol) WebSocket. The default is Block's own Goose, but the interface is open.

---

### Architecture: Tauri + Goose Sidecar + ACP

Stack: Tauri 2 (native Rust shell) + React 19 frontend. Agent logic lives in the Goose backend (a `goose serve` sidecar process); Berd communicates with it via ACP WebSocket.

```
Berd (Tauri desktop app)
      ↕ ACP WebSocket
Goose sidecar (goose serve)
      ↕
any model provider
```

This layering has an important implication: **frontend and backend iterate independently**. Want a newer Goose version? Update the commit in `goose-backend.lock.json`, run `just goose-sync`, done — no Berd frontend changes needed. Testing your own Goose fork? `GOOSE_BIN=/path/to/goose just dev` bypasses the managed pinned version entirely.

---

### Enterprise Distribution Seams

This is worth calling out as a distinct design decision.

The public repository is a fully self-contained general-purpose build — no private package registries or enterprise credentials required. But enterprise distributors can overlay their own configuration without touching the public source tree, through "distribution seams":

- Private agent configurations
- Managed provider settings
- Optional companion CLI
- Update channels, signing, publishing infrastructure

Both the public build and enterprise builds run the same `just bundle` flow; the difference is only in the private overlay. This means enterprises can ship their own Berd distribution with internal configuration, without forking the entire source tree — and can pull in public improvements cleanly.

---

### Agent Skill System

Berd publishes portable Agent Skills under `skills/`, installable independently of the app.

First official skill: **buzz-handoff**

What it does: imports Buzz (Block's internal comms tool) channel or thread context into a private agent conversation, and can send an explicitly approved reply back through the public Buzz CLI.

Design philosophy: Skills are portable knowledge units — install them in Berd, Claude Code, or Codex and they work the same. Same path as the Skill ecosystem in Heinu1 and the Claude Code ecosystem.

---

### Participation: Issues Only, No PRs

Berd is explicit: **no outside pull requests are accepted; they are closed automatically**. The only participation path is a well-formed issue.

The docs even include a prompt you can hand to your own coding agent:

```
Read https://raw.githubusercontent.com/block/berd/main/CONTRIBUTING.md
and help me file a Berd issue. Interview me for anything the guide
requires that I haven't given you, and tell me if what I'm reporting
is actually two separate issues.
```

This is an interesting design: use an agent to help structure your issue, then submit the structured issue to the maintainers. No external code contributions, but high-quality problem reports are welcome.

---

### Why It's Worth Watching

Agent workbenches are a crowded space — Windsurf, Cursor, Claude Code, Codex. But most of those are "editors with agent capabilities," not "a desktop built around agents as the primary unit."

Berd's angle is different: a pure agent interface layer, decoupled from any specific model or tool, doing exactly one thing — collecting all your agents into a single desktop. Block's fintech background means there are real enterprise use cases driving this (the Buzz integration is a signal).

691 stars in 11 days, Apache 2.0, Tauri stack, enterprise distribution seams. The clearest architecture of any open-source agent workbench I've seen so far.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
