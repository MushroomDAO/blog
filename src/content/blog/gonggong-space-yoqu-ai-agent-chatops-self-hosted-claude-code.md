---
title: "共工空间：让 AI 同事在群里接力干活"
titleEn: "Gonggong Space: AI Agents Taking Turns in a Group Chat"
description: "yoqu 开源了共工空间（gonggong-space）：Apache-2.0，自托管 ChatOps 系统，让团队把各自机器上的 Claude Code / Codex 实例接入同一个群聊。群成员 @ Bot 发任务，任务在那台机器本地执行；任务可在多个 Bot 之间接力传递，全程进度实时回流聊天窗口。Relay 中继负责账号和消息，模型请求直接从本机发出，服务端不持有密钥。Sentinel 三级权限控制，含 MCP 内置插件，零端口开放可穿透 NAT。Rust daemon + TypeScript 全栈，目前仅支持 Claude Code 和 Codex，共 10 stars，2026-09-24 创建，仍处早期阶段。"
descriptionEn: "yoqu open-sourced gonggong-space: Apache-2.0, a self-hosted ChatOps system that connects each team member's local Claude Code or Codex instance to a shared group chat. Group members @ a Bot to assign tasks; tasks execute on that machine locally. Tasks can be handed off between Bots (relay mode). All progress streams back to the group chat in real time. The Relay handles accounts and messages; model API calls go directly from the local machine — the server never touches your keys. Three-level permissions (Sentinel), built-in MCP, zero open ports for NAT traversal. Rust daemon + TypeScript full stack. Currently supports Claude Code and Codex only. 10 stars, created 2026-09-24, very early stage."
pubDate: 2026-10-09
heroImage: "../../assets/images/gonggong-space-yoqu-ai-agent-chatops-self-hosted-claude-code-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent", "协作", "Claude Code", "自托管", "ChatOps"]
lang: "zh-CN"
wechatTitle: "共工空间：AI同事在群里接力干活"
wechatDigest: "Apache-2.0；Rust+TS；群聊@Bot即可在队友机器跑Claude Code；ACP协议；自托管"
---

如果团队有几台跑 Claude Code 或 Codex 的机器，共工空间要解决的问题是：怎么让群里的每个人都能把任务派给任意一台机器，同时看到实时进度——而不是各自开终端、各干各的。

Apache-2.0，10 stars，2026-09-24 创建。GitHub: https://github.com/yoqu/gonggong-space

---

## 核心设计：每台机器就是一个 Bot

每个团队成员把自己的机器注册成一个 Bot，Bot 后面跑的是本机的 Claude Code 或 Codex 实例。群聊里 @ 某个 Bot 发任务，任务就在那台机器本地执行，执行过程（Reasoning、工具调用、命令输出）实时回流到群聊。

Bot 还可以把进行中的任务**移交给另一个 Bot** 继续完成，形成接力——这是"共工"名字的来源。

```
群成员：@Mac-Mini 帮我写一个爬虫，爬一下这个页面
        ↓
Bot (Mac Mini 本机 Claude Code 接单)
        ↓ 执行中，进度实时回流群聊
        ↓ 需要更多算力时移交给 @GPU-Server
Bot (GPU Server 接力)
        ↓
任务完成，结果发回群聊
```

---

## 接入方式

1. Web UI 创建 Bot → 点"绑定新机器" → 获得绑定码
2. 队友机器上：`gg login --server <url> --code <code>`，然后 `gg run`
3. 桌面 App 版粘贴连接链接即可

**关键点**：模型 API 请求从**本机直接发出**，服务端不经手、不持有密钥。Relay 只传消息文本，不转发模型调用。

接入协议：**ACP（Agent Client Protocol）**，目前支持 Claude Code 和 Codex，设计上方便扩展。

---

## 群聊里能看到什么

每轮对话返回：
- 实时输出（Reasoning、工具调用、命令输出）
- Diff / Git 状态 / 文件树视图
- 每轮 token 用量
- Bot 可以发多选题让成员决策

---

## 安全：三级权限 + Sentinel

Bot 操作权限分三级：
1. **只读**：仅能读取文件和输出
2. **工作区写入**：可修改文件，但不能执行命令
3. **完全访问**：完整 Agent 能力

越权操作需 Bot 拥有者批准。开发机建议用工作区写入或完全访问；日常主力机建议别开完全访问，或用专用 VM。

---

## 零端口开放

daemon（`gg run`）只建**出站连接**，不监听入站端口。穿透家用 NAT 或企业防火墙不需要额外配置端口转发。

---

## 内置 MCP 插件

Bot 可调用 `gonggong` MCP 插件（工具函数）做跨设备协作：
- 搜索聊天历史
- 查看团队成员和运行记录
- 向群成员提问（等待人工输入）

---

## 平台支持

| 平台 | 状态 |
|------|------|
| Web | 全功能，演示站 gg.uyoqu.com |
| macOS 桌面 | Tauri App，内置 daemon，菜单栏常驻 |
| CLI（gg） | macOS / Linux（glibc ≥2.31）/ Windows |
| 移动端 | README 未提及 |

---

## 技术栈

- **Rust**：`gg` daemon + `gg-cast`（屏幕直播流，用于一键预览 Web App / 微信小程序模拟器）
- **TypeScript**：React + Vite（Web 客户端）、Fastify + PostgreSQL（服务端）、Tauri（桌面）
- **运行要求**：Node.js 24+，PostgreSQL 17（服务端），Rust 1.95+（自行编译）

---

## 已知边界

- **安全前提**：@Bot 等同于允许群成员在你机器上执行代码；生产环境建议专用机或 VM
- 目前只支持 **Claude Code 和 Codex**，不支持其他 LLM
- 仅 macOS 桌面 App，Linux 需 glibc ≥2.31，无移动端原生 App
- **成熟度极低**：10 stars，2026 年 9 月底才创建，生产稳定性未经大规模验证
- 自托管需要 PostgreSQL 17 + Node.js 24 的部署环境

---

## 一句话说清楚

共工空间是一个自托管 ChatOps 系统：团队在群聊里共享多台机器上的 Claude Code / Codex 实例，@ 一下就能让对方机器接单执行，任务可接力传递，实时进度可见，密钥不过服务器，Relay 可自托管。仍是极早期阶段。

---

> Apache-2.0。yoqu，2026-09-24 创建，10 stars。开源仅供学习参考。

---

<!--EN-->

## Gonggong Space: AI Agents Taking Turns in a Group Chat

If your team has several machines running Claude Code or Codex, gonggong-space solves one problem: how do you let everyone in the group dispatch tasks to any machine and watch the progress live — instead of each person opening their own terminal separately.

Apache-2.0, 10 stars, created 2026-09-24. GitHub: https://github.com/yoqu/gonggong-space

---

### Core Design: Each Machine Is a Bot

Each team member registers their machine as a Bot — behind the Bot is their local Claude Code or Codex instance. Group members @ a Bot to assign a task; the task executes locally on that machine, with execution progress (reasoning, tool calls, command output) streaming back to the group chat in real time.

A Bot can also **hand off an in-progress task to another Bot** — the "relay" design that gives the project its name.

---

### How to Connect

1. Create a Bot in the Web UI → "Bind new machine" → get a bind code
2. On the teammate's machine: `gg login --server <url> --code <code>`, then `gg run`
3. Desktop app: paste the connection link

**Key**: model API calls go from the **local machine directly** — the server never touches or proxies them. The Relay only carries message text.

Protocol: **ACP (Agent Client Protocol)**, currently supports Claude Code and Codex.

---

### What You See in Chat

Each turn returns: real-time output (reasoning, tool calls, command output), diff / git status / file tree view, per-turn token usage. Bots can also post multiple-choice polls for human decisions.

---

### Security: Three-Level Permissions + Sentinel

Permission levels: read-only / workspace-write / full access. Escalations require Bot owner approval. Use full access on dedicated machines; avoid it on your daily driver.

---

### Zero Open Ports

The `gg run` daemon makes only **outbound connections** — no listening port. Works through home NAT or corporate firewalls without port forwarding.

---

### Known Limits

- **Security assumption**: @ a Bot = allowing group members to execute code on your machine; use a dedicated VM in production
- Only **Claude Code and Codex** supported, no other LLMs
- macOS desktop app only; no mobile native app
- **Very early stage**: 10 stars, created September 2026, not production-tested at scale
- Self-hosting requires PostgreSQL 17 + Node.js 24

---

### TL;DR

Gonggong-space is a self-hosted ChatOps system: your team shares Claude Code / Codex instances across multiple machines in a group chat. @-mention a Bot to dispatch tasks, tasks can relay between Bots, progress is live, keys never touch the server. Very early stage.

---

> Apache-2.0. yoqu, created 2026-09-24, 10 stars. For reference only.
