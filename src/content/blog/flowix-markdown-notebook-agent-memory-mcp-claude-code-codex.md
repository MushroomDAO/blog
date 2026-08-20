---
title: "Flowix：Markdown 笔记本变成 AI Agent 的持久记忆，MCP 直连 Claude Code / Codex / Hermes"
titleEn: "flowix-markdown-notebook-agent-memory-mcp-claude-code-codex"
description: "Flowix 是一个开源（MIT）的本地优先桌面 Markdown 笔记本，329 stars，基于 Tauri 2 + TypeScript + Rust。核心定位：把用户的笔记变成 AI Agent 的持久上下文。内置 flowix-cli MCP server，Codex、Claude Code、OpenCode、Hermes 等工具通过 MCP 或 CLI 直接读写同一份笔记；附带 dsh-flowix-memory 插件接入 DeepSeek Harness；所有数据本地 Markdown 文件存储，用户控制 Agent 可见范围。"
descriptionEn: "Flowix is an open-source (MIT) local-first desktop Markdown notebook (329 stars) built with Tauri 2 + TypeScript + Rust. Core concept: turn your notes into durable context for AI agents. Ships a bundled flowix-cli MCP server; Codex, Claude Code, OpenCode, and Hermes connect via MCP or CLI to read and write the same notes. Includes a dsh-flowix-memory plugin for DeepSeek Harness. All data stored as plain Markdown locally, with user-controlled agent access."
pubDate: "2026-08-20"
updatedDate: "2026-08-20"
category: "Tech-News"
tags: ["Agent记忆", "MCP", "Markdown", "Claude Code", "Codex", "本地优先", "笔记工具", "开源"]
heroImage: "../../assets/images/flowix-markdown-notebook-agent-memory-mcp-claude-code-codex-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：text2future/flowix  
官网：flowix-memo.com  
许可证：MIT  
技术栈：Tauri 2 + TypeScript + Rust  
平台：macOS 14+ · Windows 10+  
Stars：329

---

「Notes for you, Memory for your agents.」

这是 Flowix 给自己的定义。不是 AI 笔记助手，也不是对话记忆工具——而是一个 Markdown 笔记本，让笔记本身成为 AI Agent 可以持续读写的上下文载体。

---

## 一、核心思路：笔记即上下文

AI 编码 Agent 的一个普遍痛点是上下文遗失：每次新会话都要重新交代背景，项目背景、决策历史、约束条件都散落在对话历史里，下次继续时 Agent 是「失忆」状态。

Flowix 的解法很直接：把这些背景写进 Markdown 笔记，Agent 在开始任务时直接读取笔记获得上下文，任务结束后把结论写回笔记——下次启动时，背景就已经在那里了。

笔记是纯 Markdown 文件，存在本地（`~/.flowix`），不经过任何云端服务。

---

## 二、Agent 连接：MCP + CLI 双通道

Flowix 内置了 `flowix-cli` MCP server，支持以下 Agent 工具直接通过 MCP 协议连接：

- **Codex**（OpenAI Codex CLI）
- **Claude Code**（Anthropic）
- **OpenCode**
- **Hermes**
- **Flowix 内置 Agent**

所有这些工具通过同一个 MCP server 访问同一份笔记库。不需要把上下文复制粘贴到每个工具里——笔记是共享的持久存储层。

### dsh-flowix-memory 插件

对于使用 DeepSeek Harness（dsh）的用户，Flowix 提供了 `dsh-flowix-memory` 插件，将上述能力包装为 Harness 插件格式：

```bash
dsh plugin --profile <name> add ./app/flowix-dsh-host/bundles/dsh-flowix-memory
```

安装后，Agent 获得 `mcp__dsh-flowix-memory__flowix_memo` 工具，可以搜索、读取、创建和编辑 Flowix 笔记（包括思维导图）。需要 `flowix` CLI 在 PATH 上（或通过 `FLOWIX_CLI_PATH` 指定）。

---

## 三、上下文控制：你决定 Agent 看什么

Flowix 不是把整个笔记库暴露给 Agent——用户可以精确控制共享范围：

- **单篇笔记**：只给当前任务相关的那一篇
- **一个文件夹**：给某个项目的全部上下文
- **整个笔记本**：完整知识库访问

这个控制在每次启动任务时确认，不是全局开关。

---

## 四、笔记库功能

Flowix 是一个完整的 Markdown 笔记本，不是单纯的 Agent 中间件：

- **标签和属性系统**：给笔记打标签、设置元数据属性，支持按标签筛选和全文搜索
- **代码文件浏览与编辑**：直接在应用内浏览项目代码文件
- **思维导图**：除普通 Markdown 笔记外支持思维导图格式
- **Agent 预设**：在笔记详情页配置 Agent 参数和模型选择
- **提供者和 MCP 配置界面**：图形界面配置 LLM Provider 和 MCP server

数据格式是标准 Markdown，可以用其他编辑器打开和编辑，也可以用任何工具备份、版本控制、同步——Flowix 不锁定数据。

---

## 五、适用场景

| 场景 | 具体用法 |
|------|---------|
| 产品开发 | 需求、反馈、决策、PRD 放在笔记里，Agent 持续维护更新 |
| 软件开发 | 给编码 Agent 提供项目背景、架构约束、当前进度 |
| 研究 | 来源、分析过程、结论保持关联，下次 Agent 直接接续 |
| 个人知识库 | 笔记、计划、偏好设置变成 Agent 可调用的上下文 |

---

## 六、本地开发

```bash
git clone https://github.com/text2future/flowix.git
cd flowix
npm install

npm run tauri dev    # 开发模式
npm run dev          # 纯前端
npm run tauri build  # 构建桌面包
```

依赖：Node.js 20+，Rust 1.75+，Tauri v2。

---

## 七、定位评估

Flowix 解决的问题是真实存在的：AI Agent 会话间的上下文断裂。它的路径是把笔记本身当作持久存储层，而不是在 Agent 侧维护对话历史——这让上下文可以被人类编辑、审查和版本控制，而不是锁在某个 Agent 工具的数据库里。

支持的 Agent 工具覆盖了当前主流的 CLI-based 编码 Agent（Codex、Claude Code、OpenCode、Hermes），通过 MCP 标准协议接入，理论上任何支持 MCP 的工具都能接进来。

329 stars，活跃开发中（最后更新 2026-08-20），MIT 开源。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Flowix: Markdown Notebook as Durable Agent Memory — MCP Bridge for Claude Code, Codex, and Hermes

*by Mycelium Protocol*

---

GitHub: text2future/flowix  
Site: flowix-memo.com  
License: MIT  
Stack: Tauri 2 + TypeScript + Rust  
Platforms: macOS 14+ · Windows 10+  
Stars: 329

---

"Notes for you, Memory for your agents."

Flowix is not an AI note assistant or conversation memory tool. It's a Markdown notebook where your notes become durable context that AI agents can read and write — continuously, across sessions.

---

### The Problem It Solves

AI coding agents lose context between sessions. Every new conversation starts from scratch: project background, architectural constraints, past decisions, open questions — all have to be re-explained or are simply lost.

Flowix's approach: write that background as Markdown notes. An agent reads the relevant notes at task start, uses them as context, and writes conclusions back when done. Next session, the background is already there.

Notes are plain Markdown files stored locally at `~/.flowix`. No cloud service involved.

---

### Agent Connection: MCP + CLI

Flowix ships a bundled `flowix-cli` MCP server. These tools connect via MCP or CLI to the same note library:

- **Codex** (OpenAI Codex CLI)
- **Claude Code** (Anthropic)
- **OpenCode**
- **Hermes**
- **Flowix built-in Agent**

All tools work from the same notes. No copy-pasting context between tools — the notebook is the shared persistent layer.

**dsh-flowix-memory plugin**: For DeepSeek Harness users, a plugin wraps the MCP capability as a Harness bundle:

```bash
dsh plugin --profile <name> add ./app/flowix-dsh-host/bundles/dsh-flowix-memory
```

Installs the `mcp__dsh-flowix-memory__flowix_memo` tool for searching, reading, creating, and editing Flowix notes including mind maps.

---

### Context Control: You Decide What Agents See

Granular access control per task:

- **Single note**: just what's relevant to this task
- **A folder**: full context for a project
- **Whole notebook**: complete knowledge base access

Confirmed at task launch, not a global setting.

---

### Notebook Features

Flowix is a complete Markdown notebook, not just MCP middleware:

- Tag and property system with full-text and file search
- Code file browsing and editing within the app
- Mind map support alongside standard Markdown notes
- Agent preset configuration per note
- GUI for LLM Provider and MCP server configuration
- Standard Markdown files — open with any editor, version-control with any tool

---

### Use Cases

| Context | How it works |
|---------|-------------|
| Product work | Requirements, decisions, PRDs live in notes; agents keep them current |
| Software development | Give coding agents project background, architecture constraints, current progress |
| Research | Sources, analysis, conclusions stay linked; agents pick up where they left off |
| Personal knowledge | Notes, plans, preferences become callable agent context |

---

### Build from Source

```bash
git clone https://github.com/text2future/flowix.git
cd flowix && npm install
npm run tauri dev    # development
npm run tauri build  # desktop bundle
```

Requires: Node.js 20+, Rust 1.75+, Tauri v2.

---

### Assessment

The problem Flowix addresses is real: context loss between AI agent sessions. Its path — treating the notebook as the persistent storage layer rather than managing conversation history on the agent side — makes context human-editable, auditable, and version-controllable rather than locked in an agent tool's private database.

Supported agents cover the current mainstream CLI-based coding agents (Codex, Claude Code, OpenCode, Hermes). MCP standard protocol means any MCP-compatible tool can plug in. 329 stars, actively developed (last updated 2026-08-20), MIT license.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
