---
title: "Call.md：把会议变成实时 Agent 循环的 AI 会议助手"
titleEn: "Call.md: An AI Meeting Assistant That Turns a Call into a Real-Time Agent Loop"
description: "VideoDB 开源的 Electron 桌面 AI 会议助手。双声道实时转录（自己 vs 对方），会中 AI 实时建议+MCP 工具自动触发，会后生成结构化纪要+Action Items，一键同步到 n8n/Zapier/CRM。当前 575 stars，TypeScript + React 19 + tRPC 构建。"
descriptionEn: "VideoDB's open-source Electron desktop AI meeting assistant. Dual-channel real-time transcription (you vs them), live AI suggestions + MCP auto-triggering during calls, structured summaries + action items after, with webhook sync to n8n/Zapier/CRM. 575 stars, built on TypeScript + React 19 + tRPC."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["AI会议", "MCP", "实时Agent", "会议纪要", "Electron", "VideoDB", "Mycelium"]
heroImage: "../../assets/images/call-md-videodb-ai-meeting-real-time-mcp-agent-loop-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 AI 会议工具的逻辑是：会议结束后，把录音丢给 AI，得到一份纪要。

Call.md 做的是另一件事：**在会议进行中**，让 AI 实时运行起来——分析对话、生成建议、自动触发 MCP 工具。会议本身变成了一个 Agent 循环。

GitHub: https://github.com/video-db/call.md | ⭐ 575

---

## 会议中的实时智能

**双声道转录（核心差异点）**

Call.md 区分两个音频来源：麦克风（你说的）和系统音频（对方说的）。转录不是一个混合的文字流，而是两条分离的对话轨道。这使得后续分析能明确区分谁说了什么。

**实时会议指标**

在对话进行中持续追踪：

- 发言比例（Talk Ratio）：你 vs 对方各占多少
- 语速（WPM）：说话快慢实时显示
- 提问次数统计
- 独白检测（Monologue Detection）：当一方说得太久，自动提示

**Live Assist（实时建议）**

AI 根据当前对话上下文，实时生成两类输出：

1. **Things to say** — 你现在可以接上什么
2. **Questions to ask** — 哪些问题值得追问

这不是预设的问题模板，而是基于当前对话内容动态生成的。

**Coaching Nudges**

有频率限制的轻提示——当对话需要转向时发出提醒，避免打扰过于频繁。

---

## MCP 自动触发

Call.md 在会议中运行一个 MCP Agent。它监听对话，检测到信息需求时，**自动调用已配置的 MCP 工具**，不需要手动触发。

比如：对方提到了一个公司名，Agent 自动查 CRM；讨论到某个技术问题，Agent 自动搜索相关文档；提到某个人名，Agent 自动拉取联系人信息。

工具返回的结果（Markdown、链接、结构化数据）直接显示在会议界面的 **MCP Results 面板**里，不打断对话。

MCP 服务器配置在 Settings → MCP Servers，支持 stdio（本地）和 http（远程）两种传输方式。

---

## 会后生成

会议结束后，Call.md 并行生成三个维度的内容：

| 输出 | 内容 |
|------|------|
| **Short Overview** | 叙述式纪要（会议整体发生了什么） |
| **Key Points** | 按话题分类，标注发言人 |
| **Action Items** | 具体的下一步行动，指明负责人 |

最终导出为 Markdown 文件，包含完整转录、三部分摘要和会议指标数据。

**Workflow Webhooks** — 会议结束时自动向 n8n、Zapier 或 CRM 发送数据，无需手动导出。

---

## 会前准备

开会之前，Call.md 也有功能：

- **Meeting Setup Wizard** — 根据会议描述，AI 生成针对性的探探式问题（Probing Questions）
- **Dynamic Checklist** — 从会议上下文自动生成讨论清单
- **Google Calendar 同步** — 导入即将到来的会议日程

---

## 架构与数据存储

**Local-First 设计**：SQLite 数据库，所有数据存在本地机器。转录和 AI 功能需要联网调用 VideoDB，但原始录音和对话记录不离开本地。

**技术栈：**

| 层 | 技术 |
|----|------|
| 桌面框架 | Electron 34 |
| 语言 | TypeScript 5.8 |
| 前端 | React 19 + Tailwind CSS + shadcn/ui |
| 进程间通信 | tRPC 11（type-safe IPC） |
| HTTP 层 | Hono |
| 数据库 | Drizzle ORM + SQLite |
| 状态管理 | Zustand |
| 录制/转录 | VideoDB SDK 0.2.4 |
| MCP | MCP SDK 1.0.0 |
| LLM | OpenAI SDK 6.19.0（通过 VideoDB 的兼容 API） |

**进程模型**：Electron 双进程（Main + Renderer），tRPC 作为 type-safe 的 API 层连接两边，避免了传统 Electron 项目里 ipcMain/ipcRenderer 的类型混乱问题。

---

## 快速安装

```bash
# macOS 一键安装
curl -fsSL https://artifacts.videodb.io/call.md/install | bash
```

安装后：
1. 从 Applications 或 Spotlight 启动 Call.md
2. 授权麦克风和屏幕录制权限
3. 注册 VideoDB API Key（免费获取：console.videodb.io）

开发者本地运行：

```bash
git clone https://github.com/video-db/call.md.git
cd call-md
npm install
npm run rebuild   # 为 Electron 重新编译原生模块
npm run dev
```

当前支持 macOS（Apple Silicon + Intel），Windows 支持中，Linux 计划中。

---

## 和其他 AI 会议工具的核心差异

大多数工具（Otter.ai、Fireflies、Grain）的工作流是：**录制 → 上传 → 事后分析**。

Call.md 的工作流是：**录制 + 实时分析 + 实时 Agent 工具调用**——三件事同时发生，不等到会议结束。

关键是 MCP 那一层：会议中的 Agent 不是在会后批量处理数据，而是在对话发生的当下实时响应，结果实时可见。对于需要在会议中快速查找信息、做决策的场景，这个时序差异是决定性的。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Call.md: An AI Meeting Assistant That Turns Calls into Live Agent Loops

*by Mycelium Protocol*

---

Most AI meeting tools follow the same logic: wait for the meeting to end, feed the recording to AI, get a summary.

Call.md does something different: it runs AI **during the meeting itself** — analyzing conversation in real time, generating live suggestions, and automatically triggering MCP tools. The meeting becomes an agent loop.

GitHub: https://github.com/video-db/call.md | ⭐ 575

---

### Real-Time Intelligence During the Meeting

**Dual-Channel Transcription (the core differentiator)**

Call.md separates two audio sources: the microphone (what you say) and system audio (what they say). Transcription isn't a blended text stream — it's two distinct conversation tracks. This makes downstream analysis unambiguous about who said what.

**Live Conversation Metrics**

Tracked continuously throughout the call:

- Talk Ratio: your share vs theirs
- Speaking Pace (WPM): real-time
- Question count
- Monologue Detection: alerts when one party has been talking too long

**Live Assist**

AI generates two types of output based on what's being said right now:

1. **Things to say** — natural next lines for you to pick up
2. **Questions to ask** — follow-up questions worth raising

These aren't preset templates — they're generated dynamically from the current conversation.

**Coaching Nudges**

Rate-limited gentle alerts when the conversation needs steering, designed to stay non-intrusive.

---

### MCP Auto-Triggering

Call.md runs an MCP agent throughout the meeting. It monitors the conversation, detects information needs, and **automatically calls configured MCP tools** — no manual trigger needed.

Examples: a company name is mentioned → agent queries the CRM automatically; a technical question comes up → agent searches relevant docs; a contact is referenced → agent pulls up their profile.

Tool outputs (Markdown, links, structured data) appear in the **MCP Results panel** inline on the meeting screen, without interrupting the call.

MCP servers are configured under Settings → MCP Servers, supporting both stdio (local) and http (remote) transports.

---

### Post-Meeting Output

When the call ends, Call.md generates three parallel extractions:

| Output | Content |
|--------|---------|
| **Short Overview** | Narrative summary of what happened |
| **Key Points** | Organized by topic, attributed to participants |
| **Action Items** | Concrete next steps with owners |

Exported as Markdown with full transcript, summaries, and meeting metrics.

**Workflow Webhooks** — automatically sends meeting data to n8n, Zapier, or CRMs when the meeting ends. No manual export step.

---

### Pre-Meeting Preparation

Before the call even starts:

- **Meeting Setup Wizard** — AI generates targeted probing questions based on the meeting description
- **Dynamic Checklist** — auto-generates a discussion checklist from meeting context
- **Google Calendar sync** — imports upcoming meetings

---

### Architecture and Storage

**Local-First**: SQLite database, all data stored on your local machine. Transcription and AI features require internet access to VideoDB, but raw recordings and conversation history don't leave your device.

**Tech stack:**

| Layer | Technology |
|-------|-----------|
| Desktop framework | Electron 34 |
| Language | TypeScript 5.8 |
| Frontend | React 19 + Tailwind CSS + shadcn/ui |
| IPC | tRPC 11 (type-safe between main/renderer) |
| HTTP | Hono |
| Database | Drizzle ORM + SQLite |
| State | Zustand |
| Recording/transcription | VideoDB SDK 0.2.4 |
| MCP | MCP SDK 1.0.0 |
| LLM | OpenAI SDK 6.19.0 (via VideoDB's compatible API) |

The two-process Electron model with tRPC as the IPC bridge eliminates the type-unsafe ipcMain/ipcRenderer pattern common in Electron projects.

---

### Quick Install

```bash
# macOS one-liner
curl -fsSL https://artifacts.videodb.io/call.md/install | bash
```

After install:
1. Launch from Applications or Spotlight
2. Grant Microphone and Screen Recording permissions
3. Register your VideoDB API key (free at console.videodb.io)

For developers:

```bash
git clone https://github.com/video-db/call.md.git
cd call-md
npm install
npm run rebuild   # rebuild native modules for Electron
npm run dev
```

Currently available for macOS (Apple Silicon + Intel). Windows in progress, Linux planned.

---

### What Makes This Different

Most AI meeting tools (Otter.ai, Fireflies, Grain) follow a workflow of: **record → upload → analyze later**.

Call.md's workflow is: **record + analyze in real time + call MCP tools in real time** — all three happening simultaneously, not after the meeting ends.

The critical piece is the MCP layer: the agent doesn't batch-process data after the call — it responds at the moment conversations happen, and results are visible immediately. For situations where you need to look up information or make decisions during the meeting itself, that timing difference is decisive.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
