---
title: "OpenWorker：吴恩达开源的 AI 协作者，交付成品而不是对话"
titleEn: "OpenWorker: Andrew Ng's Open-Source AI Coworker That Delivers Finished Work, Not Conversation"
description: "andrewyng/openworker，13.8k stars，MIT，Python + Rust + React。吴恩达开源的桌面 AI 协作者，核心命题：给你交付完成品（文档、Slack 回复、更新后的日历），而不是下一步待办清单。25+ 应用集成，支持 OpenAI/Anthropic/Gemini/DeepSeek/Kimi/Ollama 等12个供应商，本地优先，写入/发送/运行命令前必须用户审批。基于 aisuite 构建。"
descriptionEn: "andrewyng/openworker, 13.8k stars, MIT, Python + Rust + React. Andrew Ng's open-source desktop AI coworker. Core premise: deliver finished work — a polished document, a Slack reply with the numbers, an updated calendar — not a to-do list. 25+ integrations, 12+ model providers (OpenAI/Anthropic/Gemini/DeepSeek/Kimi/Ollama), local-first, approval-gated writes. Built on aisuite."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["AI助手", "桌面应用", "本地优先", "吴恩达", "aisuite", "MCP", "多模型", "Mycelium"]
heroImage: "../../assets/images/openworker-andrewyng-ai-coworker-25-integrations-local-first-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

AI 对话工具的痛点不是不聪明，是交付不了成品。你问完之后拿到的是"你可以这样做……"，而不是一份写好的文档、一封发出去的邮件、一个整理好的日历。

OpenWorker 是吴恩达（Andrew Ng）开源的桌面 AI 协作者，核心主张只有一句话：**给你交付完成品，不是待办清单**。开源20天，13,800+ stars。

GitHub: https://github.com/andrewyng/openworker | ⭐ 13,829 | MIT | Python + Rust + React

---

## 什么是"完成品"

OpenWorker 的工作方式分四步：

1. 告诉它你想要的结果——"准备一份客户简报"、"整理我的日历冲突"、"草拟一份报告"、"核查这个 Release 在 Jira 和 GitHub 的进度"
2. 它把任务分解成步骤，跨你的桌面、文件和连接的应用来工作
3. 在任何重要操作前（发消息、改日历、执行命令）——**停下来让你审批或调整**
4. 你拿到的是可以打开和分享的文件、发出去的 Slack 回复、更新后的日历——不是"接下来你需要……"

这是一个很清晰的产品定位对比：大多数 AI 工具在第1步和第2步止步（分析、建议），OpenWorker 要做完第4步。

---

## 架构：三层，全在你的机器上

```
┌──────────────────────────────────────────┐
│          OpenWorker 桌面应用              │  原生 shell + GUI（Tauri + React）
├──────────────────────────────────────────┤
│       本地 Agent 服务器（Python）         │  引擎 · 工具 · 连接器 — 基于 aisuite
├──────────────┬───────────────┬───────────┤
│  你的文件     │   你的工具    │  你的模型 │  用你的 key，跑在你的机器上
│  & 终端      │ 25+ 连接器    │ 任意供应商│
└──────────────┴───────────────┴───────────┘
```

- **桌面 shell**：Tauri（Rust）负责窗口管理和进程监督
- **本地 Agent 服务器**：Python，负责 agent 循环、工具调用、连接器、内存、自动化任务
- **React UI**：前端界面，可以在浏览器模式（Vite dev server）或 Tauri 窗口里跑
- **STT 旁路进程**：Rust 写的语音转文字模块，支持语音输入

整个 agent 循环、对话历史、连接器 token、模型 key——全部在本机的本地 secret store 里。唯一的云端部分是一个小型 OAuth 中间件，用于处理第三方应用的授权握手。

---

## 25+ 集成

内置集成覆盖主流工作流工具：

**通讯**：Slack（`@OpenWorker` 直接在频道里调用）、Gmail、Outlook

**项目管理**：GitHub、Jira、Linear、monday.com

**知识库**：Notion

**CRM**：HubSpot

**日历**：Google Calendar

**终端与文件**：本地文件系统 + shell 命令（审批后执行）

**MCP 扩展**：任何通过 MCP 协议暴露的工具都能接入，每个工具可以单独控制权限

---

## 带你自己的模型

不绑定任何供应商，粘贴 API key 就能切换：

**OpenAI · Anthropic · Google Gemini · Inkling（Thinking Machines）· GLM（Z.ai）· DeepSeek · Kimi（Moonshot）· Qwen · MiniMax · Mistral · Grok（xAI）**

加上通过 **Together** 和 **Fireworks** 的开源权重模型，以及通过 **Ollama** 完全本地运行。

内置一份经过工具调用验证的模型推荐列表；手动输入任意模型 ID 也可以，风险自担。

---

## Slack 集成：在频道里调用

在 Slack 频道里 `@OpenWorker`，OpenWorker 在你的桌面上打开一个工作会话，用你本地的工具做完这件事，然后把结果作为回复发回 Slack 线程。

这意味着 OpenWorker 的能力（访问你的本地文件、运行终端命令、查询 GitHub/Jira）可以通过 Slack 触发，而不需要你主动打开桌面应用。

---

## 定时自动化

支持设置定期运行的自动化任务：晨报、周报、对某个频道持续监控。每次运行结束后在应用里保留完整的执行记录（transcript）。

无人值守运行时，需要审批的操作会进入收件箱等待，而不是自行决定。

---

## 审批门控

写入、发送、执行 shell 命令——统一过审批。这是 OpenWorker 区别于"帮你全自动执行"工具的关键设计：**它做事，但在重要操作前停下来问你**。

这个设计对生产场景很重要：AI 工具在"建议"阶段很强，但"执行"阶段的失误代价高。审批门控把决策权留给用户，而不是假设 AI 永远判断正确。

---

## 基于 aisuite

OpenWorker 的 Agent 引擎建在吴恩达团队的另一个开源项目 [**aisuite**](https://github.com/andrewyng/aisuite) 之上——一个提供统一 chat-completions API 的轻量 Python 库，覆盖多个 LLM 供应商，并带有工具调用、toolkit 和 MCP 支持。

OpenWorker 最初在 aisuite 仓库里开发，后来独立为单独的项目。从这个意义上说，openworker 是 aisuite 的一个生产级参考实现，展示了 aisuite 能承载的完整桌面 agent 产品形态。

---

## 从源码运行

```bash
git clone https://github.com/andrewyng/openworker
cd openworker

# 1. 一次性 bootstrap（在 .venv 创建 Python 虚拟环境）
bash packaging/setup_dev_env.sh

# 2. 启动本地 Agent 服务器
.venv/bin/openworker-server --cwd ~/some/project --port 8765

# 3. 另开终端，启动 UI（浏览器模式）
cd surfaces/gui
npm install
npm run dev        # Vite dev server

# 或者启动完整桌面应用（需要 Rust toolchain）
npm run tauri dev
```

系统要求：Python 3.10+、Node 20+、Rust（仅桌面应用需要，通过 rustup 安装）。

---

## 当前状态

Open Beta：完全可用，应用自动更新，团队在主动打磨细节。目前 Windows 版本尚未代码签名，SmartScreen 会弹出警告，签名正在处理中。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenWorker: Andrew Ng's Open-Source AI Coworker That Delivers Finished Work, Not Chat

*by Mycelium Protocol*

---

The problem with most AI tools isn't intelligence — it's delivery. You end the conversation with "here's how you could do this…" instead of a finished document, a sent email, or an organized calendar.

OpenWorker is Andrew Ng's open-source desktop AI coworker. The premise is one sentence: **deliver finished work, not a to-do list**. 13,800+ stars in under 20 days since open-sourcing.

GitHub: https://github.com/andrewyng/openworker | ⭐ 13,829 | MIT | Python + Rust + React

---

### What "Finished Work" Means

Four steps:

1. Tell OpenWorker the outcome you want — "prepare a customer brief," "untangle my calendar," "draft a report," "check where the release stands across Jira and GitHub"
2. It breaks the task into steps and works across your desktop, files, and connected apps
3. Before anything consequential — sending a message, changing a calendar, running a command — **it checks in and you approve or redirect**
4. You get the finished deliverable: a file you can open and share, a Slack reply with the numbers, an updated calendar — not "next, you should…"

Most AI tools stop at step 2 (analyze, suggest). OpenWorker is designed to get to step 4.

---

### Architecture: Three Layers, All Local

```
┌──────────────────────────────────────────┐
│          OpenWorker desktop app          │  native shell + GUI (Tauri + React)
├──────────────────────────────────────────┤
│       local agent server (Python)        │  engine · tools · connectors — built on aisuite
├──────────────┬───────────────┬───────────┤
│  your files  │  your tools   │ your model│  everything runs with your keys,
│  & terminal  │ 25+ connectors│ any vendor│  on your machine
└──────────────┴───────────────┴───────────┘
```

- **Desktop shell**: Tauri (Rust) for window management and process supervision
- **Local agent server**: Python — agent loop, tool calls, connectors, memory, automations
- **React UI**: runs in browser mode (Vite) or Tauri window
- **STT sidecar**: Rust speech-to-text module for voice input

The agent loop, conversation history, connector tokens, and model keys all live in a local secret store on your machine. The only cloud piece is a small OAuth broker for connector handshakes.

---

### 25+ Integrations

Built-in connectors cover the main work tools:

**Communication**: Slack (`@OpenWorker` in any channel), Gmail, Outlook

**Project management**: GitHub, Jira, Linear, monday.com

**Knowledge**: Notion

**CRM**: HubSpot

**Calendar**: Google Calendar

**Terminal & files**: local filesystem + shell commands (approval-gated)

**MCP**: any tool exposed over MCP plugs in, with per-tool permission controls

---

### Bring Your Own Model

No vendor lock-in — paste a key and switch:

**OpenAI · Anthropic · Google Gemini · Inkling · GLM (Z.ai) · DeepSeek · Kimi (Moonshot) · Qwen · MiniMax · Mistral · Grok (xAI)** — plus open-weight models via Together and Fireworks, and fully local models via Ollama.

A curated list marks what the team has verified for tool-calling work. Arbitrary model ID strings work at your own risk.

---

### Slack: Call It from a Channel

Mention `@OpenWorker` in a Slack channel. OpenWorker opens a session on your desktop, does the work using your local tools, and posts the result back as a thread reply.

This means OpenWorker's full capability — local file access, terminal, GitHub/Jira queries — can be triggered from Slack without switching to the desktop app.

---

### Scheduled Automations

Set up recurring tasks: a morning brief, a weekly report, a standing watch on a channel. Every run keeps a full transcript in the app. In unattended mode, writes and sends park in an inbox for your approval instead of firing automatically.

---

### Approval Gates

Writes, sends, shell commands — all gated. This is OpenWorker's key design choice: **it does the work, but stops before consequential actions to ask**. The AI handles the task; the human handles the decisions.

---

### Built on aisuite

OpenWorker's engine is built on [**aisuite**](https://github.com/andrewyng/aisuite), Andrew Ng's lightweight Python library with a unified chat-completions API across LLM providers, tools, toolkits, and MCP. OpenWorker started inside the aisuite repo and moved out; it's a production-grade reference for what aisuite can carry.

---

### Run from Source

```bash
git clone https://github.com/andrewyng/openworker
cd openworker
bash packaging/setup_dev_env.sh               # one-time Python venv bootstrap
.venv/bin/openworker-server --port 8765       # agent server
cd surfaces/gui && npm install && npm run dev  # browser UI (Vite)
# or: npm run tauri dev  (full desktop app, needs Rust)
```

Requirements: Python 3.10+, Node 20+, Rust (desktop app only, via rustup).

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
