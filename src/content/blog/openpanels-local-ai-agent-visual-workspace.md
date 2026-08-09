---
title: "OpenPanels：给AI Agent装上本地可视化工作台，5个面板从写作到发布"
titleEn: "OpenPanels: A Local Visual Workspace for AI Agents, Five Panels from Writing to Publishing"
description: "mooqii 开源了 OpenPanels，一个本地优先的 AI Agent 可视化工作台，用 Rust 写成，MIT 授权。5个面板覆盖从知识管理、文档写作到排版发布的全流程，内置微信公众号草稿集成，以 agent skill URL 的方式接入任何 AI Agent。"
descriptionEn: "mooqii open-sources OpenPanels, a local-first visual workspace for AI agents, written in Rust, MIT license. Five panels cover the full pipeline from knowledge management and document writing to typesetting and publishing — including built-in WeChat Official Account draft integration. Install as an agent skill via a single URL."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-News"
tags: ["AI Agent", "Rust", "本地优先", "MCP", "知识库", "微信公众号", "开源工具", "Mycelium"]
heroImage: "../../assets/images/openpanels-local-ai-agent-visual-workspace-banner.jpg"
---

*by Mycelium Protocol*

---

当你让 AI Agent 帮你整理资料、写文章、排版发布，你通常要在至少 4-5 个工具之间来回切换：笔记应用、文档编辑器、图片生成工具、排版工具、各平台发布后台……

**[OpenPanels](https://github.com/mooqii/OpenPanels)**（mooqii）把这几个工具合并成一个本地面板，让 Agent 通过 skill URL 直接操作。Rust 写成，MIT 授权，2026 年 7 月开源。

---

## 五个面板，覆盖从输入到输出

OpenPanels 的工作台由 5 个协作面板组成：

**Wiki — 结构化知识库**

Agent 在这里管理结构化知识，支持 tag、分类、关联，以及从文章自动提取要点。不是 Markdown 文件夹，而是能被 Agent 检索和引用的知识节点。

**Writing — 文档写作**

集成 Writing Skills 的文档编辑器。Agent 可以在这里起草、修改、迭代文章，你可以实时看到编辑过程。

**Canvas — 视觉内容**

生成和管理图表、插图、视觉素材。Agent 在这里放配图，你在这里审视和调整。

**Typesetting — 出版排版**

把写好的内容按目标平台格式处理：微信公众号样式、博客格式、PDF 文档……排版逻辑在 Agent 侧运行，你在面板里预览。

**Publishing — 发布**

把排版好的内容推送到目标平台。内置**微信公众号草稿集成**：Agent 把文章推成草稿，你在后台审核后直接发布，凭据本地存储。

---

## 作为 Skill 接入 Agent

OpenPanels 不需要安装额外工具，它的接入方式是 **agent skill URL**：

```
把 skill URL 粘贴给你的 AI Agent → Agent 自动发现并加载 OpenPanels 的能力
```

加载后，Agent 就能通过 skill 接口打开面板、写入内容、触发发布。你在一旁的 Studio（浏览器界面）里看到完整过程。

对于喜欢命令行的用户，OpenPanels 同时提供原生 CLI：

```bash
myopenpanels --help
```

---

## 本地优先，凭据自己掌管

OpenPanels 不需要云端账号。所有数据本地存储，微信公众号等平台凭据也存在本地，不经过第三方服务器。

这解决了很多 AI 工作流工具的核心痛点：发布到公众号需要把 AppSecret 给第三方服务。OpenPanels 的方式是让 Agent 调用本地的 OpenPanels 进程，由本地进程持有凭据并执行 API 调用。

---

## 支持平台

- macOS
- Windows

Linux 路线图中，未明确发布时间。

---

## 为什么关注这个方向

目前 AI Agent 的"最后一公里"问题是：Agent 能写出好内容，但内容从草稿变成发布态，通常还需要人工干预很多步骤。

OpenPanels 的思路是把这些步骤也纳入 Agent 的可操作范围，同时给人类留一个清晰的预览界面——你知道 Agent 在做什么，你在最终发布前审核，而不是完全盲目授权。

5 个面板的设计对应内容生产的完整流程：
- **输入** → Wiki（知识管理）
- **处理** → Writing + Canvas（写作 + 配图）
- **格式化** → Typesetting（按平台排版）
- **输出** → Publishing（推送到目标平台）

这是一种"Agent 干活，人类审核"的架构，而不是"Agent 直接操作账号"。

---

## 快速开始

仓库：[github.com/mooqii/OpenPanels](https://github.com/mooqii/OpenPanels)

```bash
# 安装 CLI
cargo install myopenpanels

# 启动 Studio（浏览器界面）
myopenpanels studio

# 在你的 AI Agent 里粘贴 skill URL
# → Agent 自动加载 OpenPanels 能力
```

或者直接把仓库 README 里的 skill URL 粘贴给 Claude Code / Codex / 任何支持 skill URL 的 Agent，OpenPanels 会作为本地工具被发现和使用。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenPanels: A Local-First Visual Workspace for AI Agents

*by Mycelium Protocol*

When you ask an AI agent to help you organize research, write an article, format it, and publish — you typically end up switching between 4–5 tools: a note app, a document editor, an image generation tool, a layout tool, and the publishing backend of each platform you're targeting.

**[OpenPanels](https://github.com/mooqii/OpenPanels)** (mooqii) merges those tools into a single local workspace that agents can operate through a skill URL. Written in Rust, MIT license, open-sourced in July 2026.

### Five Panels, Full Content Pipeline

**Wiki** — Structured knowledge base. Agents manage tagged, categorized, interlinked knowledge nodes that can be retrieved and referenced — not a folder of Markdown files, but a searchable graph.

**Writing** — Document editor with integrated Writing Skills. Agents draft and iterate; you watch in real time.

**Canvas** — Visual content: diagrams, illustrations, image assets. Agents generate; you review and adjust.

**Typesetting** — Format the completed content for a target platform: WeChat Official Account styles, blog formats, PDF documents. Layout logic runs on the agent side; you preview in the panel.

**Publishing** — Push formatted content to target platforms. Built-in **WeChat Official Account draft integration**: the agent pushes to draft; you approve and publish from the WeChat backend. Credentials stored locally.

### Install as an Agent Skill

No additional tooling is required. The access method is a **skill URL** you paste to your AI agent. The agent auto-discovers OpenPanels capabilities, opens panels, writes content, and triggers publishing through the skill interface. You watch the full process in the Studio (browser UI).

For CLI preference:

```bash
myopenpanels --help
```

### Local-First, Credentials Stay Yours

No cloud account required. All data is stored locally. Platform credentials — including WeChat AppSecret — stay on your machine and are never passed through a third-party server. The agent calls the local OpenPanels process, which holds credentials and executes API calls.

This addresses one of the core pain points in AI workflow tools: most publication integrations require handing your AppSecret to an external service.

### The Design Philosophy

The five panels correspond to the complete content production flow:

- **Input** → Wiki (knowledge management)
- **Processing** → Writing + Canvas (drafting + illustration)
- **Formatting** → Typesetting (per-platform layout)
- **Output** → Publishing (push to target platforms)

This is an "agent works, human reviews" architecture rather than "agent operates your accounts autonomously." You see what the agent is doing at every stage and have a clear checkpoint before content goes live.

Platforms: macOS, Windows. Linux on the roadmap.

Repository: [github.com/mooqii/OpenPanels](https://github.com/mooqii/OpenPanels)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
