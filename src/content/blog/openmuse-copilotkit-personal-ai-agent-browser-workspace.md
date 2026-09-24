---
title: "OpenMuse：CopilotKit 开源个人 AI 助理，带浏览器、终端、文件，任务后台保持运行"
titleEn: "OpenMuse: CopilotKit's Open-Source Personal AI Agent with Browser, Terminal, Files, and Persistent Background Tasks"
description: "OpenMuse，CopilotKit出品，MIT，2026-09-22开源。个人AI助理模板：持久化Chromium浏览器（跨任务保留Profile）、可选Linux工作区（终端+文件）、持久化后台任务（SQL租约协调）、Gmail/Google Calendar连接器、iOS/Android/Web全平台。Built on CopilotKit + AG-UI，任意Agent后端接入，可自己部署可二次开发。直接对标Meta Muse发布时机。"
descriptionEn: "OpenMuse by CopilotKit — MIT, open-sourced 2026-09-22. Personal AI agent template: persistent Chromium browser (profile retained across tasks), optional Linux workspace (terminal + files), durable background tasks (SQL lease coordination), Gmail/Google Calendar connectors, iOS/Android/Web. Built on CopilotKit + AG-UI, any agent backend, self-hostable and forkable. Launched the same day as Meta Muse."
pubDate: 2026-09-24
heroImage: "../../assets/images/openmuse-copilotkit-personal-ai-agent-browser-workspace-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "ai-agent", "copilotkit", "personal-assistant", "browser", "self-hostable", "mit", "ag-ui", "react-native"]
lang: zh-CN
---

`CopilotKit/openmuse`，MIT，2026-09-22 开源。个人 AI 助理模板，由 CopilotKit CEO Atai Barkai 主导，基于 CopilotKit + AG-UI 构建。

**GitHub**：github.com/CopilotKit/openmuse | **License**：MIT | **平台**：iOS / Android / Web

发布时机不是巧合：CopilotKit 当天直接引用了 Meta 发布 Muse 的推文——「我们的 Muse 是开源的」。

---

## 一句话定位

OpenMuse 是一个可 fork、可自部署的个人 AI 助理应用，内置了 AI 助理该有的工位：持久浏览器、终端、文件系统、后台任务引擎，以及和个人应用（Gmail、日历）的连接。

和 ChatGPT 这类纯对话产品的区别：任务不因为会话结束而停止，浏览器里的登录态可以跨任务保留，助理可以在后台做事，你不需要一直盯着它。

---

## 核心四件套

### 1. 持久化 Chromium 浏览器

Agent 有自己的 Chromium 实例，带持久化 Profile：

- 登录态在任务之间保留（不是每次都从头登录）
- 可以浏览公开页面，也可以操作已登录的站点
- 用户可以随时接管（手动控制 Agent 正在用的浏览器会话）
- 任务结束后可以重新打开同一个浏览器会话，接着上次继续

这对个人助理场景是关键设计：一次性登录各个平台，后续任务直接用，而不是每次任务都要重新验证。

### 2. 可选 Linux 工作区

Agent 的电脑包含一个可选的 Linux 容器：

- 终端（Terminal）：在独立容器里运行命令
- 文件系统：App 和电脑之间可以移动 PDF 等文件
- 与 Chromium 并行，文件可以在浏览器下载后直接进入文件系统

### 3. 持久化后台任务

这是 OpenMuse 和普通聊天助理最大的工程区别：

```
任务创建 → 放入后台任务队列 → 即使你关了 App 也继续运行
```

技术实现：
- **SQL 租约（SQL Leases）**：多个 task worker 通过数据库租约协调，避免重复执行
- **Pause / Resume / Retry**：任务可以暂停、恢复、失败自动重试
- **外部写操作强制审批（mandatory review on external writes）**：发邮件、写日历等操作需要人工确认，不会悄悄执行

部署时 task worker 和 API 可以分开运行，共享同一个 DATABASE_URL 和 DATA_DIR，通过 `TASK_WORKER_ENABLED=false` 分离职责。

### 4. 个人应用连接器

内置 Gmail 和 Google Calendar 连接器，可以读取邮件、创建日历事件。外部写操作（发送邮件、修改日历）需要经过 mandatory review，不是全自动执行。

---

## 架构

```
手机 App（iOS/Android）
网页端（Web）
    ↕ AG-UI 协议
Agent Harness（任意后端：LangGraph / Claude SDK / CrewAI / ...）
    ↕
OpenMuse 服务层
    ├── API Server
    ├── Task Worker（后台任务，SQL 租约协调）
    └── Browser Worker（Chromium 管理）
    ↕
持久化存储
    ├── 数据库（任务状态、租约）
    └── DATA_DIR（文件、浏览器 Profile）
```

前端基于 CopilotKit React Native，Web 和移动共用一套组件。Agent 后端通过 AG-UI 协议解耦，不绑定任何特定模型或框架。

---

## 快速部署

```bash
git clone https://github.com/CopilotKit/openmuse
cd openmuse
cp .env.example .env
# 填入 DATABASE_URL、AI API Key 等
pnpm install
pnpm dev
```

本地开发单进程即可。生产环境建议分离 task worker：

```bash
# API（禁用 task worker）
TASK_WORKER_ENABLED=false pnpm start:api

# 独立 task worker（可横向扩展）
pnpm dev:worker
```

---

## 和 Meta Muse 的关系

Meta 同天发布了 Muse，定位类似的个人 AI 助理。OpenMuse 的回应是：这个东西是开源的，你可以 fork、改、自部署，不需要把数据交给 Meta 或任何其他大公司。

这是 CopilotKit 自 AG-UI 协议以来一贯的路线：做 Agent 应用的基础设施，开源出来让开发者自己掌控。

---

## 局限性

**1. Alpha 阶段，功能仍在演进**：2026-09-22 才开源，功能模块还在快速迭代，部分细节文档不完整。

**2. 需要自己运维**：自部署意味着你要维护数据库、task worker、Chromium 实例的可靠性。对于普通用户，运维复杂度不低。

**3. Linux 工作区是可选项**：容器化 Linux 环境需要额外配置，默认部署不含。

**4. 浏览器会话的安全性**：Agent 使用持久化 Chromium Profile，该 Profile 里可能存有个人账号登录态。需要认真评估访问控制——谁能调用 Agent、Agent 能操作哪些站点。

**5. 外部写操作的 mandatory review 是好设计但增加摩擦**：每次发邮件都要确认，在高频场景下使用体验会受影响。

**6. AG-UI 依赖**：Agent 后端需要支持 AG-UI 协议。如果现有 Agent 框架不支持，需要适配层。

---

## 怎么看这个项目

OpenMuse 回答了一个很具体的问题：**「如果我想自部署一个带工位的个人助理，不想用闭源产品，最小可行版本长什么样？」**

浏览器持久化 + 后台任务引擎 + SQL 租约这三件事，是区别「会话助理」和「能干活的助理」的关键工程。CopilotKit 把这些打包成一个可 fork 的模板开源出来，是给开发者的礼物，也是 AG-UI 生态的一步棋。

MIT 许可，可 fork 可改可商用，Alpha 阶段的稳定性需要预期管理，但作为起点使用价值是真实的。

> MIT，开源仅供学习研究参考。

---

<!--EN-->

## OpenMuse: CopilotKit's Open-Source Personal AI Agent

`CopilotKit/openmuse` (MIT, open-sourced 2026-09-22) is a self-hostable personal AI agent template built on CopilotKit + AG-UI by CopilotKit CEO Atai Barkai.

**GitHub**: github.com/CopilotKit/openmuse | **Platforms**: iOS / Android / Web

Timing note: CopilotKit launched OpenMuse the same day Meta announced Muse — the quote-tweet was intentional. OpenMuse is the "our Muse is open source" response.

---

### Core Feature Set

**1. Persistent Chromium Browser**
- Login state persists across tasks (no re-auth per session)
- User can take manual control of the browser session the agent is using
- Browser profile survives task completion; reopen and continue where you left off

**2. Optional Linux Workspace**
- Terminal: commands run in an isolated container
- File system: move files (including PDFs) between the app and the computer

**3. Durable Background Tasks**
```
Task created → queued → runs even after you close the app
```
- SQL leases for multi-worker coordination (prevents duplicate execution)
- Pause / Resume / Retry built-in
- **Mandatory review on external writes**: sending email, modifying calendar — requires human confirmation, never silently auto-executes

**4. Personal App Connectors**
Gmail and Google Calendar built-in. External write operations require approval.

---

### Architecture

```
Mobile (iOS/Android) + Web
    ↕ AG-UI protocol
Agent Harness (LangGraph / Claude SDK / CrewAI / any)
    ↕
API Server + Task Worker + Browser Worker
    ↕
Database (task state, SQL leases) + DATA_DIR (files, browser profile)
```

Frontend: CopilotKit React Native (shared Web + mobile codebase). Backend: any AG-UI-compatible agent framework.

---

### Self-Hosting

```bash
git clone https://github.com/CopilotKit/openmuse
cd openmuse && cp .env.example .env  # fill DATABASE_URL, AI API key, etc.
pnpm install && pnpm dev
```

For production, separate the task worker:
```bash
TASK_WORKER_ENABLED=false pnpm start:api   # API process
pnpm dev:worker                            # Task worker (horizontally scalable)
```

Both share the same DATABASE_URL and DATA_DIR.

---

### Limitations

1. **Alpha stage**: Launched 2026-09-22; feature set still evolving, some docs incomplete
2. **Self-ops burden**: You maintain the database, task worker, and Chromium instance reliability
3. **Linux workspace is optional**: Requires extra setup; not included by default
4. **Persistent browser security surface**: The Chromium profile holds personal account sessions — evaluate access controls carefully
5. **Mandatory review adds friction**: Required confirmation on every external write may be cumbersome in high-frequency scenarios
6. **AG-UI dependency**: Agent backends need AG-UI compatibility; existing frameworks may need an adapter

---

### Assessment

OpenMuse answers a concrete question: "If I want to self-host a personal agent with a real workstation, what does the minimum viable version look like?"

Browser persistence + durable task engine + SQL leases are the engineering delta between a "chat assistant" and an "assistant that actually does work." Packaging these into a forkable MIT template is genuinely useful. As an alternative to closed personal AI products, the trade-off is real: you own the data and the stack, but you also own the operations.

> MIT. For learning and research reference only.
