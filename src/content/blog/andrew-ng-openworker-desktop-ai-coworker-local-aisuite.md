---
title: "OpenWorker：吴恩达开源的桌面 AI 协作者，本地运行 + 批准门 + 25+ 工具集成"
titleEn: "OpenWorker: Andrew Ng's Open-Source Desktop AI Coworker — Local, Approval-Gated, 25+ Integrations"
description: "andrewyng/openworker，4天前刚开源。MIT，Python + TypeScript + Tauri + Rust，本地运行，BYOK（带自己的 key 或跑 Ollama），25+ 工具集成，批准门机制保留人类最终审批权。吴恩达 aisuite 的实战参考实现。"
descriptionEn: "andrewyng/openworker, open-sourced 4 days ago. MIT, Python + TypeScript + Tauri + Rust, runs locally, BYOK (bring your own key or run Ollama), 25+ integrations, approval-gate keeps humans in final control. The reference implementation of Andrew Ng's aisuite in production."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI Agent", "开源", "桌面应用", "本地优先", "吴恩达", "aisuite", "工作流", "自托管"]
heroImage: "../../assets/images/andrew-ng-openworker-desktop-ai-coworker-local-aisuite-banner.jpg"
---

> **仓库**：andrewyng/openworker · Python + TypeScript + Rust · MIT · 2202 stars
> **最新版本**：v0.1.6（2026-07-23）
> **开源时间**：2026-07-20（4天前）
> **官网**：openworker.com

---

## 一、它是什么

OpenWorker 是吴恩达（Andrew Ng）4天前开源的桌面 AI 协作者工具。定位比"AI 聊天"高一档：

> "AI that gets your everyday tasks done."

不是给你建议，是直接交付成品：一份写好的文档、一条带数字的 Slack 回复、整理好的日历、分类完的收件箱。

它运行在你的机器上，不锁定任何模型——带自己的 API key，或者接 Ollama 完全本地运行。

---

## 二、架构：三层

```
┌──────────────────────────────────────────┐
│          OpenWorker 桌面应用             │  React + Tauri shell
├──────────────────────────────────────────┤
│       本地 Agent 服务器（Python）        │  引擎 · 工具 · 连接器（基于 aisuite）
├─────────────┬──────────────┬─────────────┤
│  本地文件   │  25+ 工具    │  你的模型   │
│  和终端     │   连接器     │  你的 key   │
└─────────────┴──────────────┴─────────────┘
```

**Python 后端**（`coworker/`）：Agent 引擎、模型接入层、连接器、MCP 客户端、记忆、自动化

**桌面壳**（`surfaces/gui/`）：React UI + Tauri，窗口管理和服务器监督

**语音输入**（`stt/`）：Rust 写的 STT 侧车进程

---

## 三、核心机制：批准门

这是 OpenWorker 和"全自主 Agent"最重要的设计差异。

**写入、发送、执行 shell 命令——所有后果性操作，都要你先批准**。

无人值守运行（定时自动化）时，它把需要批准的操作停放在收件箱，而不是自己做主。等你回来，你决定要不要放行。

这个设计在当前 Agent 工具的光谱里很有意思：Claude Desktop 等工具往往要么完全自主（容易出问题），要么完全对话（不落地）。OpenWorker 选了一条中间路：**Agent 做所有的调研和草稿，人保留最后一道审批权**。

---

## 四、支持什么

**模型（Bring Your Own Key）**：

OpenAI · Anthropic · Google Gemini · GLM（Z.ai）· DeepSeek · Kimi（Moonshot）· Qwen · MiniMax · Mistral · Grok（xAI）· Together · Fireworks · **Ollama（完全本地）**

**25+ 工具集成**：

GitHub、Slack、Jira、Notion、Linear、HubSpot、Outlook、monday.com、Gmail、Google Calendar、本地文件、终端，加上任何 **MCP 协议**兼容工具

**Slack 集成的特殊用法**：

在频道里 `@OpenWorker`，一个 session 在你桌面打开，工作在你的工具里完成，答案作为线程回复发回频道。这是"桌面 Agent 接管 Slack 工作流"的有意思实现。

**定时自动化**：

早报、周报、频道监控——定时任务，完整执行记录存档。

---

## 五、技术底层：aisuite

OpenWorker 的 Agent 引擎建在 [aisuite](https://github.com/andrewyng/aisuite) 上——吴恩达此前开源的轻量级 Python 库，提供统一的 LLM chat-completions API + Agent 层（工具、工具包、MCP 支持）。

OpenWorker 最早是在 aisuite 仓库里开发的，后来拆出来独立。README 里有一句话说清楚了关系：

> "如果你想自己搭 Agent 引擎而不是用我们的，从 aisuite 开始；这个仓库是 aisuite 能承载什么的一个实战参考。"

**从源码跑起来**：

```bash
git clone https://github.com/andrewyng/openworker
cd openworker

# 一次性 bootstrap（创建 .venv）
bash packaging/setup_dev_env.sh

# 启动本地 Agent 服务器
.venv/bin/openworker-server --cwd ~/some/project --port 8765

# 第二个终端，启动 UI
cd surfaces/gui && npm install && npm run dev

# 或者跑完整桌面应用（Tauri）
npm run tauri dev
```

---

## 六、数字和背景

- 2202 stars，298 forks
- **2026-07-20 开源，4天**——没有产品 Hunt 或大型 HN 帖子的冷启动，这个增速是健康的
- v0.1.6，说明迭代节奏很快（一周内从 0.1.0 到 0.1.6）
- 31 open issues，38 open PRs——社区已经在积极贡献

---

## 七、判断

OpenWorker 踩在几个真实矛盾的交叉点上：

**矛盾一**：全自主 Agent 太危险，纯聊天又不落地。批准门机制是合理的工程折中——让 Agent 做脏活，让人保留审批权。在实际工作场景里，这可能比"让 Claude 完全自主操作我的 Gmail"更容易被接受。

**矛盾二**：SaaS 省事，但数据和 key 都在别人那。本地优先直接绕开这个矛盾。

**不确定的地方**：

- 2202 stars 在 4 天内是体面的，但对比吴恩达发布 aisuite（几天内 6k+ stars）显得克制。原因可能是桌面应用的分发摩擦比库大得多——下载安装远比 `pip install` 重。
- BYOK 模式意味着推理成本全在用户身上。对个人友好，对企业采购是额外的运营考量。
- 25+ 工具集成的深度，还需要实际跑起来才知道。列名字容易，集成质量差异很大。

**最值得跟进的演化**：Slack 的 `@OpenWorker` 集成。如果这个体验真的流畅——在频道里 at 一下，桌面 Agent 开始工作，答案发回来——这可能是"Agent 如何融入现有工作流"的一个有说服力的范式。

本地优先 + 批准门 + 25+ 工具 + Bring Your Own Model——四个选择组合在一起，定位是明确的：**给想要控制权的技术用户用的 AI 工作助手**。

---

*数据来源：GitHub andrewyng/openworker，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: andrewyng/openworker · Python + TypeScript + Rust · MIT · 2,202 stars
> **Latest Release**: v0.1.6 (2026-07-23)
> **Open-sourced**: 2026-07-20 (4 days ago)
> **Homepage**: openworker.com

---

## 1. What It Is

OpenWorker is a desktop AI coworker that Andrew Ng open-sourced four days ago. Its ambition sits a step above "AI chat":

> "AI that gets your everyday tasks done."

Not suggestions — finished work: a polished document, a Slack reply with the actual numbers, a tidied calendar, a triaged inbox.

It runs on your machine and doesn't lock you into any model — bring your own API key, or run fully local with Ollama.

---

## 2. Architecture: Three Layers

```
┌──────────────────────────────────────────┐
│        OpenWorker desktop app            │  React + Tauri shell
├──────────────────────────────────────────┤
│     local agent server (Python)          │  engine · tools · connectors (aisuite)
├─────────────┬──────────────┬─────────────┤
│ your files  │  25+ tool    │ your model  │
│ & terminal  │  connectors  │  your keys  │
└─────────────┴──────────────┴─────────────┘
```

**Python backend** (`coworker/`): agent engine, model providers, connectors, MCP client, memory, automations

**Desktop shell** (`surfaces/gui/`): React UI + Tauri, window management and server supervision

**Voice input** (`stt/`): a Rust STT sidecar for speech-to-text

---

## 3. Core Mechanism: Approval Gates

This is the most important design distinction between OpenWorker and fully autonomous agents.

**Writes, sends, and shell commands — all consequential actions require your approval before they execute.**

In unattended (scheduled automation) mode, pending approvals are parked in an inbox rather than acted on unilaterally. You come back, you decide whether to let them through.

This sits at an interesting point on the current agent-tool spectrum: tools tend to swing either toward fully autonomous (error-prone) or fully conversational (nothing actually ships). OpenWorker picks a middle path: **agents do all the research and drafting; humans hold the final approval checkpoint.**

---

## 4. What It Supports

**Models (Bring Your Own Key):**

OpenAI · Anthropic · Google Gemini · GLM (Z.ai) · DeepSeek · Kimi (Moonshot) · Qwen · MiniMax · Mistral · Grok (xAI) · Together · Fireworks · **Ollama (fully local)**

**25+ tool integrations:**

GitHub, Slack, Jira, Notion, Linear, HubSpot, Outlook, monday.com, Gmail, Google Calendar, local files, terminal — plus anything reachable over **MCP**

**Special Slack integration:**

Mention `@OpenWorker` in a channel; a session opens on your desktop, the work happens with your tools, and the answer comes back as a thread reply. This is an interesting implementation of "desktop agent taking over the Slack workflow."

**Scheduled automations:**

Morning briefs, weekly reports, channel monitoring — recurring tasks with full execution transcripts archived.

---

## 5. Built on aisuite

OpenWorker's agent engine is built on [aisuite](https://github.com/andrewyng/aisuite) — Andrew Ng's own previously open-sourced lightweight Python library providing a unified LLM chat-completions API plus an agent layer (tools, toolkits, MCP support).

OpenWorker was originally developed inside the aisuite repository before spinning out independently. The README makes the relationship explicit:

> "If you want to build your own agent harness rather than use ours, start there; this repo is a working reference for what aisuite can carry."

**Running from source:**

```bash
git clone https://github.com/andrewyng/openworker
cd openworker

# One-time bootstrap (creates .venv)
bash packaging/setup_dev_env.sh

# Start the local agent server
.venv/bin/openworker-server --cwd ~/some/project --port 8765

# Second terminal: start the UI
cd surfaces/gui && npm install && npm run dev

# Or run the full desktop app (Tauri)
npm run tauri dev
```

---

## 6. Numbers and Context

- 2,202 stars, 298 forks
- **Open-sourced 2026-07-20 — 4 days ago** — healthy cold start without a Product Hunt launch or major HN post
- v0.1.6 already — fast iteration cadence (0.1.0 → 0.1.6 within a week)
- 31 open issues, 38 open PRs — community engagement already active

---

## 7. Assessment

OpenWorker sits at the intersection of several real tensions in the AI tooling landscape:

**Tension 1**: Fully autonomous agents are risky; pure chat never ships anything. The approval gate is a reasonable engineering compromise — let the agent do the grunt work, keep a human checkpoint for consequential actions. In real work environments, this may be more adoptable than "let Claude operate my Gmail autonomously."

**Tension 2**: SaaS tools are convenient but take your data and keys. Local-first sidesteps this entirely.

**Open questions:**

- 2,202 stars in 4 days is respectable, but compare with Andrew Ng's aisuite launch (6k+ stars within days). Desktop apps carry significantly more distribution friction than libraries — download-and-install vs. `pip install` is a real gap.
- BYOK means all inference costs land on the user. Fine for individuals; extra operational overhead for enterprise procurement.
- The depth of those 25+ integrations remains to be tested. Listing names is easy; integration quality varies enormously in practice.

**Most interesting thing to watch**: the Slack `@OpenWorker` integration. If the experience is genuinely smooth — at-mention in a channel, desktop agent starts working, answer comes back as a thread reply — this could be a compelling pattern for how agents integrate into existing workflows without disrupting them.

Local-first + approval gates + 25+ tools + Bring Your Own Model — four choices that together define a clear position: **an AI work assistant built for technical users who want to stay in control.**

---

*Data source: GitHub andrewyng/openworker, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
