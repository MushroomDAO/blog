---
title: "ai-memory：让 AI 编程助手真正记住「上次做到哪了」，跨工具无缝交接，Rust 实现，Wiki 存 Git"
titleEn: "ai-memory-long-term-memory-coding-agents-claude-codex-handoff-rust"
description: "akitaonrails/ai-memory 是一个 Rust 实现的 AI 编程助手长期记忆方案，3953 stars，MIT 许可证。核心能力：用生命周期 Hook 自动捕获每次 Claude Code/Codex/Cursor 等会话的精华，会话结束时编译为结构化 Wiki 页面存入 Git 仓库（纯 Markdown，可 grep、可 Obsidian 同步）；下次无论用哪个工具打开同一目录，都能收到「上次做到哪里」的交接块。支持 Claude Code、Codex、Command Code、Cursor、Gemini CLI、Devin CLI、Kiro CLI、Kimi Code 等 20+ 客户端；零 LLM 模式可用（FTS5+实体匹配）；本地或 homelab 服务器均可运行。"
descriptionEn: "akitaonrails/ai-memory is a Rust-based long-term memory solution for AI coding agents — 3,953 stars, MIT license. Core capability: lifecycle hooks auto-capture the essence of each Claude Code/Codex/Cursor session; at session end, observations are compiled into structured wiki pages stored in a git repo (plain Markdown, grep-able, Obsidian-compatible). The next agent in the same directory receives a 'where you left off' handoff block — regardless of which tool picks up the work. Supports 20+ clients including Claude Code, Codex, Command Code, Cursor, Gemini CLI, Devin CLI, Kiro CLI, Kimi Code. Zero-LLM mode available (FTS5 + entity matching). Runs locally or on a homelab server."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["AI工具", "编程助手", "长期记忆", "跨工具", "Claude Code", "Codex", "Rust", "开源"]
heroImage: "../../assets/images/ai-memory-long-term-memory-coding-agents-claude-codex-handoff-rust-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：akitaonrails/ai-memory  
许可证：MIT  
语言：Rust  
Stars：3,953 · Forks：298  
创建：2026-05-21 | 最近更新：2026-08-22

---

## 一、它解决的核心问题

AI 编程助手的上下文是会话级的——关掉 Claude Code，下次打开要重新讲一遍背景；换用 Codex 接着干，要再把架构、失败过的方案、当前卡点都解释一遍。

ai-memory 直接解决这个问题：

> 「关掉 Claude Code，在同一个目录开 Codex，继续工作——不用重新解释架构、走过的弯路、还开着的问题。」

---

## 二、工作机制

### 生命周期 Hook 自动捕获

安装后，ai-memory 为每个支持的客户端配置生命周期钩子（MCP config + 事件钩子）。钩子以「发出即忘」的方式，捕获有界、脱敏的提示词、工具调用事件和会话边界观察——不是完整的原始日志，而是精选的结构化快照。

### 会话结束时编译为 Wiki

会话结束（`SessionEnd`）或手动执行 `ai-memory finalize-session` 时，系统把当次会话的观察编译成一批 Markdown 页面，写入一个 Git 仓库。超版本链 + Git 历史意味着可以用 `ai-memory checkpoints` 或 `restore-page` 时间旅行。

### 下次开工时收到交接块

下次在同一个目录打开任何支持的客户端，会话开始前自动注入一个「从这里继续」的交接块，包含上次的进度、待解决的问题、未完成的决策——不管上次用的是哪个工具。

### Wiki 是普通 Git 仓库

存储格式是纯 Markdown，按 `<wiki_root>/<workspace_id>/<project_id>/` 组织。可以 `grep`、在 Obsidian 里打开、用 `rsync` 备份。**没有向量数据库需要维护。**

---

## 三、支持的客户端（20+）

| 客户端 | 支持程度 |
|--------|---------|
| Claude Code | 完整（MCP + 生命周期钩子）|
| OpenAI Codex | 完整（MCP + 生命周期钩子）|
| Command Code | 完整（4 种钩子事件）|
| Cursor | 完整 |
| Gemini CLI | 完整 |
| Devin CLI | 完整 |
| Kiro CLI | 完整（v2 + 实验性 v3）|
| Kimi Code | 完整（10 种钩子事件）|
| OpenCode | 完整（生成 TypeScript 插件）|
| Oh My Pi / OMP | 完整 |
| VS Code Copilot | 仅 MCP（无生命周期钩子）|
| Zed | 仅 MCP |
| Claude Desktop | 仅 MCP（via `mcp-remote`）|
| Grok Build CLI | 完整 |
| Antigravity CLI | 完整 |

此外还有 OpenClaw、Zero、Swival CLI、Pi（通过生成的 bridge extension）等。

---

## 四、检索不依赖 LLM

零 LLM 模式下，ai-memory 提供三种检索通道：

- **FTS5 全文搜索**：SQLite FTS5，响应快，无需 API Key
- **实体辅助召回**：每个 Wiki 页面存储最多 10 个规范实体名词（`entities:` 前置数据），支持精确/前缀/复合词匹配
- **图邻居 RRF**：基于知识图谱边的相关性评分

加了 LLM/Embedding 提供者之后，可以额外做语义检索和页面综合。支持 OpenAI、Voyage、Google Gemini 及任意 OpenAI 兼容端点（Ollama、LM Studio、vLLM）。

---

## 五、权威感知检索

检索结果有分层优先级：`_rules/`、`decisions/`、`procedures/`、`gotchas/` 目录的页面在截断前会被上调权重。历史会话证据仍然可以被精确搜索到，不会因为优先级低而消失。

**重要设计原则**：这些优先级只影响检索排序，不赋予 Wiki 内容指令权威——从 Wiki 里读出来的代码主张在行动前仍然需要对照实际代码库验证。

---

## 六、opt-in 托管工作流

除了 Hook 捕获外，还有可选的「托管工作流」模式：

```bash
ai-memory run claude      # 启动 Claude Code（带完整上下文）
ai-memory run codex --yolo  # 无缝切换到 Codex
ai-memory run command-code  # 再切 Command Code
```

三者之间共享一个逻辑工作流，带有原生的每客户端会话恢复和完整的可见事件账本。

---

## 七、安装（macOS 原生二进制）

```bash
# 下载 macOS Apple Silicon 原生二进制
curl -L https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-macos-aarch64.tar.gz \
  | tar -xz
sudo mv ai-memory /usr/local/bin/

# 启动服务器（本地模式，无 LLM）
ai-memory start

# 为 Claude Code 安装 MCP 配置 + 钩子
ai-memory install-mcp --client claude
ai-memory install-hooks --agent claude
```

x86_64 Mac：把 `aarch64` 换成 `x86_64`。Linux 用 Docker：

```bash
docker run -d \
  -v ~/.ai-memory:/data \
  -p 3579:3579 \
  akitaonrails/ai-memory:latest
```

---

## 八、与 MemPalace、DeepTutor 等的定位区别

| 工具 | 核心记忆内容 | 适用场景 |
|------|------------|---------|
| **ai-memory** | 编码会话的进度、决策、失败尝试、悬而未决的问题 | 多工具协作的编程工作流 |
| **MemPalace** | 结构化知识条目（用户主动归档） | 个人知识管理 |
| **DeepTutor** | 学习轨迹、知识掌握度 | 个性化学习 |

ai-memory 的记忆是**被动的、会话级的、面向工程决策的**，不需要用户手动写知识。

---

ai-memory 的核心赌注是：**AI 编程助手的真正痛点不是单次会话的上下文长度，而是跨会话、跨工具的状态丢失。** 把每次会话的精华编译成 Git 里的 Markdown，是目前最轻量、最可靠的解法——没有供应商锁定，没有黑盒向量库，随时可以 `grep`。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## ai-memory: Long-Term Memory for AI Coding Agents — Cross-Tool Handoff, Git-Backed Wiki, Rust

*by Mycelium Protocol*

---

GitHub: akitaonrails/ai-memory  
License: MIT  
Language: Rust  
Stars: 3,953 · Forks: 298  
Created: 2026-05-21 | Updated: 2026-08-22

---

### The Core Problem

AI coding agents are session-scoped — close Claude Code and you start fresh; switch to Codex mid-task and you have to re-explain the architecture, the dead ends, and the open questions.

ai-memory directly addresses this:

> "Quit Claude Code mid-task, start OpenAI Codex in the same directory, continue without re-explaining the architecture, the failed approaches, or the open questions."

---

### How It Works

**Lifecycle hooks capture automatically.** After installation, ai-memory configures lifecycle hooks (MCP config + event hooks) for each supported client. Hooks fire-and-forget bounded, sanitized observations of prompts, tool events, and session boundaries — not raw logs, but curated structured snapshots.

**Session end compiles a wiki.** On `SessionEnd` (or manual `ai-memory finalize-session`), the session's observations are compiled into Markdown pages and written to a git repository. Supersession chains + git history mean you can time-travel with `ai-memory checkpoints` or `restore-page`.

**Next session receives a handoff.** The next agent in the same directory gets a "where you left off" block before its first prompt — regardless of which tool picks up the work.

**The wiki is a plain git repo.** Storage is pure Markdown organized under `<wiki_root>/<workspace_id>/<project_id>/`. Grep it, open it in Obsidian, back it up with rsync. **No vector database to maintain.**

---

### 20+ Supported Clients

| Client | Support |
|--------|---------|
| Claude Code | Full (MCP + lifecycle hooks) |
| OpenAI Codex | Full (MCP + lifecycle hooks) |
| Command Code | Full (4 hook events) |
| Cursor | Full |
| Gemini CLI | Full |
| Devin CLI | Full |
| Kiro CLI | Full (v2 + experimental v3) |
| Kimi Code | Full (10 hook events) |
| OpenCode | Full (generated TypeScript plugin) |
| Oh My Pi / OMP | Full |
| VS Code Copilot | MCP-only (no lifecycle hooks) |
| Zed | MCP-only |
| Claude Desktop | MCP-only (via `mcp-remote`) |
| Grok Build CLI | Full |
| Antigravity CLI | Full |

Plus OpenClaw, Zero, Swival CLI, Pi (generated bridge extension), and more.

---

### Retrieval Without LLM

Zero-LLM mode provides three retrieval channels:

- **FTS5 full-text search**: SQLite FTS5, fast, no API key required
- **Entity-assisted recall**: Each wiki page stores up to 10 canonical entity nouns (`entities:` frontmatter); exact, prefix, and compound-word matches form a project-scoped RRF stream
- **Graph-neighbor RRF**: Relevance scoring via knowledge graph edges

LLM/embedding providers (OpenAI, Voyage, Gemini, or any OpenAI-compatible endpoint including Ollama) are opt-in additions for semantic retrieval and page consolidation.

---

### Authority-Aware Retrieval

Retrieval has tiered priority: `_rules/`, `decisions/`, `procedures/`, and `gotchas/` pages are bumped above session evidence before truncation. Historical session records remain findable via targeted search — they're not filtered out.

**Key design principle**: priority affects ranking, not authority. Wiki content is historical evidence — verify code claims against the actual checkout before acting on them.

---

### Opt-In Managed Workstreams

Beyond hook capture, an optional managed mode:

```bash
ai-memory run claude       # start Claude Code with full context
ai-memory run codex --yolo  # seamlessly switch to Codex
ai-memory run command-code  # switch again
```

All three share one logical workstream with native per-harness session resume and a portable visible-event ledger.

---

### Install (macOS native binary)

```bash
# Apple Silicon
curl -L https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-macos-aarch64.tar.gz \
  | tar -xz
sudo mv ai-memory /usr/local/bin/

# Start server (local mode, no LLM required)
ai-memory start

# Install MCP config + hooks for Claude Code
ai-memory install-mcp --client claude
ai-memory install-hooks --agent claude
```

For x86_64 Mac: replace `aarch64` with `x86_64`. For Linux, use Docker:

```bash
docker run -d \
  -v ~/.ai-memory:/data \
  -p 3579:3579 \
  akitaonrails/ai-memory:latest
```

---

### Positioning vs. MemPalace, DeepTutor

| Tool | Core Memory Content | For |
|------|---------------------|-----|
| **ai-memory** | Session progress, decisions, dead ends, open questions | Multi-tool coding workflows |
| **MemPalace** | Structured knowledge entries (user-curated) | Personal knowledge management |
| **DeepTutor** | Learning traces, mastery state | Personalized learning |

ai-memory's memory is **passive, session-scoped, engineering-decision-focused** — no manual knowledge writing required.

---

ai-memory's core bet: **the real pain for AI coding agents isn't context length within a session — it's state loss across sessions and across tools.** Compiling each session's essence into Markdown in a git repo is the lightest, most reliable solution available today: no vendor lock-in, no black-box vector store, always grep-able.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
