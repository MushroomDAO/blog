---
title: "Wake：macOS 原生 Agent 会话管理器，Rust + GPUI，把 Claude Code/Codex/13 个 Agent 的历史汇聚一处"
titleEn: "wake-gpui-coding-agent-session-browser-claude-codex-macos-native"
description: "iAmCorey/Wake 是 macOS 原生 Agent 会话浏览器，387 stars，MIT，Rust + GPUI（gpui 0.2 + gpui-component 0.5），2026-08-18 发布。读取 13 个 Agent 的本地会话数据（Claude Code、Codex CLI、OpenCode、Kiro、Gemini CLI、Grok Build 等），统一浏览/全文搜索/一键恢复。SQLite FTS5 三元组索引，CJK + 代码子串搜索均在 1ms 内返回。tree-sitter 代码高亮（30+ 语言）、工具调用折叠、Thinking 摘要。所有操作只读，零网络请求，数据完全本地。"
descriptionEn: "iAmCorey/Wake is a native macOS coding-agent session browser — 387 stars, MIT, Rust + GPUI (gpui 0.2 + gpui-component 0.5), released 2026-08-18. Reads local session data from 13 agents (Claude Code, Codex CLI, OpenCode, Kiro, Gemini CLI, Grok Build, etc.), providing unified browse/full-text search/one-click resume. SQLite FTS5 trigram index returns results in under 1ms including CJK and code substrings. Tree-sitter code highlighting (30+ languages), collapsible tool-call clusters, thinking summaries. Read-only, zero network requests, fully local."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["macOS", "Rust", "GPUI", "Claude Code", "Codex", "AI工具", "会话管理", "本地优先"]
heroImage: "../../assets/images/wake-gpui-coding-agent-session-browser-claude-codex-macos-native-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：iAmCorey/Wake  
许可证：MIT  
语言：Rust  
技术栈：GPUI 0.2 + gpui-component 0.5  
Stars：387 · Forks：21  
平台：macOS 14+  
发布日期：2026-08-18（3 天前）

---

## 一、解决的问题

你用 Claude Code 开了 50 个会话，用 Codex 开了另外 30 个，偶尔还用 OpenCode 跑了几个。这些会话分散在 `~/.claude`、`~/.codex`、`~/.local/share/opencode` 等目录里，各有各的格式。

你想找三周前那个「重构认证模块」的会话，或者想接着上次未完成的任务继续——没有统一入口，只能挨个翻目录。

**Wake 做的事**：把这些会话数据全部读进来，给你一个快的、原生的、本地的窗口。

---

## 二、支持的 Agent（13 个）

| Agent | 数据来源 | 模型信息 | 启动方式 |
|-------|---------|---------|---------|
| **Claude Code** | `~/.claude/projects/**/*.jsonl` | ✅ | — |
| **Codex CLI** | `~/.codex/sessions` + `state_5.sqlite` | ✅ | ✅ |
| Copilot CLI | `~/.copilot/session-store.db` | — | — |
| Cursor（CLI 转写） | `~/.cursor/projects/**/agent-transcripts` | — | — |
| **OpenCode** | `~/.local/share/opencode/opencode.db` | ✅ | — |
| **OpenCode 2**（beta） | 同 v1，新 `session_v2` 表 | ✅ | — |
| **Kiro** | `~/.kiro/sessions/cli` | ✅ | — |
| Gemini CLI | `~/.gemini/tmp/**/chats` | — | — |
| **Pi** | `~/.pi/agent/sessions/**/*.jsonl` | ✅ | — |
| **Oh My Pi** | `~/.omp/agent/sessions/**/*.jsonl` | ✅ | — |
| **Grok Build** | `~/.grok/sessions/**/updates.jsonl` | ✅ | — |
| Kimi Code | `~/.kimi-code/sessions/**/wire.jsonl` | — | — |
| Antigravity CLI | `~/.gemini/antigravity-cli/conversation_summaries.db`（仅元数据） | — | — |

**不支持**：Cursor IDE 对话、Windsurf、Trae（加密本地数据）；Amp、Factory、Warp（会话在云端）。

---

## 三、核心功能

### 统一浏览
会话按 Agent / 项目分组，文件系统监听实时增量更新——新会话自动出现，不需要刷新。

### 全文搜索（⌘K）
SQLite FTS5 三元组索引，**搜索结果在 1ms 内返回**。

支持：
- CJK 中文文本（按字搜索，无需分词）
- 代码子串（如 `useEffect(`、`impl Trait for`）
- 直接跳到匹配消息在 transcript 里的位置

### Transcript 视图
- 用户/助手气泡分开渲染
- 工具调用折叠成簇（避免大量工具调用撑满屏幕）
- Thinking 块折叠成摘要
- tree-sitter 代码高亮，支持 30+ 语言

### 一键恢复
点击会话 → 在 Terminal 或 iTerm 里用原项目目录打开（AppleScript 驱动）：

```bash
claude --resume <session-id>
codex resume <session-id>
```

### 管理
- 星标/置顶（存在 Wake 自己的数据库，不改动原始文件）
- 导出为 Markdown
- 删除（移入系统废纸篓 + tombstone，删除的会话不会在下次扫描时重新出现）

---

## 四、性能

作者机器上（约 310 个会话，~800 MB JSONL）：
- 首次全量索引：~5 秒
- 后续启动：即时（基于 mtime 的增量扫描）
- 搜索响应：< 1ms

---

## 五、安装

从源码构建（需要 Rust 工具链）：

```bash
git clone https://github.com/iAmCorey/Wake && cd Wake
scripts/make-app.sh   # 构建 dist/Wake.app（图标 + Info.plist，ad-hoc 签名）
open dist/Wake.app
```

如果从 Releases 下载预构建版本，macOS Gatekeeper 会拦截首次启动——右键点击选「打开」，或：

```bash
xattr -d com.apple.quarantine Wake.app
```

---

## 六、隐私承诺

- Agent 数据目录**只读打开**，Wake 从不写入其他工具的文件
- 从不读取凭据文件（`auth.json` 等）
- **零网络请求**——Wake 不构造也不调用 HTTP 客户端（GPUI 依赖树里有 HTTP 客户端，但 Wake 不使用它）
- Wake 自己的索引在 `~/Library/Application Support/wake/wake.db`，随时可以删除重建（星标/置顶在单独的表里，重建后保留）

---

## 七、技术架构

```
crates/
├── wake-core        # 纯数据层，无 UI 依赖
│   ├── adapters/    #   13 个 Agent 的解析器（AgentAdapter trait）
│   ├── scanner.rs   #   单次扫描：元数据 + FTS 索引，mtime 增量
│   ├── watcher.rs   #   notify 文件监听 → 逐文件增量更新
│   ├── db.rs        #   rusqlite（WAL）：sessions / messages / FTS / 用户数据 / tombstones
│   └── services/    #   Terminal 恢复（AppleScript）/ 导出 / 废纸篓
└── wake             # GPUI 应用（三栏 workbench + ⌘K 搜索面板）
```

`AgentAdapter` trait 的设计值得注意：**新增 Agent 只需实现一个 adapter，整个 UI 对这个 Agent 就立即可用**，不需要改 UI 层。

GPUI 是 Zed 编辑器的 UI 框架，同样是 Rust + GPU 渲染，macOS 原生，无 Electron 依赖。

---

## 八、发布 3 天，387 stars

Wake 创建于 2026-08-18，本文写作时是 2026-08-21，3 天 387 stars。

这个速度说明需求是真实的：用多个 AI 编码工具的人越来越多，会话散落各处的问题越来越痛。Wake 切入的角度不是「又一个 AI 工具」，而是「管理你已有的所有 AI 工具的历史」。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Wake: Native macOS Coding-Agent Session Browser — Rust + GPUI, 13 Agents in One Window

*by Mycelium Protocol*

---

GitHub: iAmCorey/Wake  
License: MIT  
Language: Rust  
Stack: GPUI 0.2 + gpui-component 0.5  
Stars: 387 · Forks: 21  
Platform: macOS 14+  
Released: 2026-08-18 (3 days ago)

---

### The Problem

You have 50 Claude Code sessions, 30 Codex sessions, and a handful of OpenCode runs. They live in `~/.claude`, `~/.codex`, `~/.local/share/opencode`, each with a different format. To find that session from three weeks ago where you refactored the auth module, you're grepping through directories.

Wake reads all of them, gives you a single native window, and gets out of the way.

---

### 13 Supported Agents

| Agent | Data source | Model info | Resume |
|-------|-------------|-----------|--------|
| **Claude Code** | `~/.claude/projects/**/*.jsonl` | ✅ | — |
| **Codex CLI** | `~/.codex/sessions` + `state_5.sqlite` | ✅ | ✅ |
| Copilot CLI | `~/.copilot/session-store.db` | — | — |
| Cursor (CLI transcripts) | `~/.cursor/projects/**/agent-transcripts` | — | — |
| **OpenCode** | `~/.local/share/opencode/opencode.db` | ✅ | — |
| **OpenCode 2** (beta) | same DB, new `session_v2` tables | ✅ | — |
| **Kiro** | `~/.kiro/sessions/cli` | ✅ | — |
| Gemini CLI | `~/.gemini/tmp/**/chats` | — | — |
| **Pi** | `~/.pi/agent/sessions/**/*.jsonl` | ✅ | — |
| **Oh My Pi** | `~/.omp/agent/sessions/**/*.jsonl` | ✅ | — |
| **Grok Build** | `~/.grok/sessions/**/updates.jsonl` | ✅ | — |
| Kimi Code | `~/.kimi-code/sessions/**/wire.jsonl` | — | — |
| Antigravity CLI | `~/.gemini/antigravity-cli/...db` (metadata only) | — | — |

Not supported: Cursor IDE chats, Windsurf, Trae (encrypted local data); Amp, Factory, Warp (cloud sessions).

---

### Features

**Unified browsing**: sessions grouped by agent/project, live file-watching for incremental updates — new sessions appear automatically.

**Full-text search (⌘K)**: SQLite FTS5 trigram index. Results in under 1ms. Works equally well for CJK text and code substrings like `useEffect(` or `impl Trait for`. Jumps directly to the matched message in the transcript.

**Transcript view**: user/assistant bubbles, collapsible tool-call clusters (prevents long tool sequences from dominating the view), thinking summaries, tree-sitter code highlighting for 30+ languages.

**One-click resume**: opens the session in Terminal/iTerm at the original project directory via AppleScript:

```bash
claude --resume <session-id>
codex resume <session-id>
```

**Manage**: star/pin (stored in Wake's own DB, original files untouched), export to Markdown, delete (system Trash + tombstone so deleted sessions don't reappear after a rescan).

---

### Performance

On the author's machine (~310 sessions, ~800 MB JSONL):
- First full index: ~5 seconds
- Subsequent launches: instant (mtime-based incremental scan)
- Search: under 1ms

---

### Install

Build from source (Rust toolchain required):

```bash
git clone https://github.com/iAmCorey/Wake && cd Wake
scripts/make-app.sh   # builds dist/Wake.app (icon + Info.plist, ad-hoc signed)
open dist/Wake.app
```

For prebuilt releases, Gatekeeper blocks the first launch — right-click → Open, or:

```bash
xattr -d com.apple.quarantine Wake.app
```

---

### Privacy

- Agent data directories opened **read-only** — Wake never writes to another tool's files
- Credential files never read
- **Zero network requests** — GPUI's dependency tree includes an HTTP client; Wake never touches it
- Wake's own index at `~/Library/Application Support/wake/wake.db` can be deleted and rebuilt at any time; stars/pins survive rebuilds

---

### Architecture

```
crates/
├── wake-core       # pure data layer, no UI dependencies
│   ├── adapters/   #   13 agent parsers (AgentAdapter trait)
│   ├── scanner.rs  #   single-pass scan: meta + FTS, mtime incremental
│   ├── watcher.rs  #   notify file watching → per-file incremental updates
│   ├── db.rs       #   rusqlite (WAL): sessions/messages/FTS/user_data/tombstones
│   └── services/   #   terminal resume (AppleScript) / export / Trash
└── wake            # GPUI app (three-pane workbench + ⌘K palette)
```

`AgentAdapter` trait: add a new adapter, get the full UI for free — no UI layer changes needed.

GPUI is Zed's UI framework — Rust + GPU rendering, macOS native, no Electron.

---

### 387 Stars in 3 Days

Wake launched 2026-08-18. Three days later: 387 stars.

The problem is real and growing: as more developers use multiple coding agents simultaneously, session history scatters across more directories in incompatible formats. Wake's angle isn't "another AI tool" — it's "manage the history of every AI tool you already use." The `AgentAdapter` trait means new agents can be added without touching the UI.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
