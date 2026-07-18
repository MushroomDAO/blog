---
title: "GraphMind：把代码库变成知识图谱，让 AI 永久记住你的架构"
titleEn: "GraphMind: Turn Your Codebase Into a Knowledge Graph Your AI Can Query, Navigate, and Remember"
description: "GraphMind（aouicher/graphmind，191★，MIT，Rust）是一个本地优先的代码知识图谱工具，通过 25 个 MCP 工具让 Claude Code、Cursor、Windsurf、Cline 等 AI 编程助手直接查询项目结构、调用链、死代码和跨项目依赖——无需重复索引，单次查询比 grep 少用 5700 倍 token。支持 30+ 语言，四层架构（结构图谱 + 语义向量 + 持久化记忆 + 跨项目关联），本地运行，无需上传代码。"
descriptionEn: "GraphMind (aouicher/graphmind, 191★, MIT, Rust) is a local-first code intelligence platform that exposes 25 MCP tools to Claude Code, Cursor, Windsurf, and Cline. Query symbol graphs, call chains, dead code, and cross-project dependencies without re-indexing every session. Up to 5,700× fewer tokens than grep. Four layers: structural graph (tree-sitter, 30+ languages) + semantic embeddings + persistent memory + cross-project links. Runs locally, no code upload."
pubDate: "2026-07-06"
updatedDate: "2026-07-06"
category: "Tech-News"
tags: ["GraphMind", "代码知识图谱", "MCP", "Claude Code", "AI编程", "Rust", "知识库"]
heroImage: "../../assets/images/graphmind-code-knowledge-graph-agent-guide-banner.jpg"
---

> **GitHub**: [aouicher/graphmind](https://github.com/aouicher/graphmind) · **191 Stars** · **MIT** · **Rust** · **主页**: [getgraphmind.com](https://getgraphmind.com)

---

## 每次新会话，AI 都从零开始

这是 AI 编程助手的根本性缺陷，不是 bug，是设计：每次你打开 Claude Code 或 Cursor，它从零开始重新理解你的代码库。上次解释过的架构决策、上次找到的关键依赖关系、上次调试时发现的隐藏耦合——全部丢失。

于是你要：
- 重新解释项目结构
- 重新找到关键文件
- 重新提供上下文让 AI 理解「为什么这样设计」
- 在大型项目里把整个目录树 dump 给模型，消耗大量 token

**GraphMind** 解决的就是这个问题。它不是一个 prompt 技巧，而是一个本地运行的代码智能平台：把整个代码库解析成结构化知识图谱，通过 25 个 MCP 工具暴露给你的 AI 助手，跨会话持久化。

---

## 核心数字

| 指标 | 数值 |
|---|---|
| Token 节省（vs grep） | **最多 5,700×** |
| 支持语言数 | **30+** |
| MCP 工具数 | **25 个** |
| 支持 AI 助手 | Claude Code、Cursor、Windsurf、Cline、Zed、Continue |
| 运行方式 | 本地，无需上传代码 |
| 核心技术 | Rust + tree-sitter + SQLite |

---

## 四层架构

GraphMind 用四层叠加解决不同维度的问题：

```
┌─────────────────────────────────────────────┐
│  Claude Code / Cursor / Windsurf / Cline     │
│  ↕ MCP（25 个工具，stdio，无需开端口）        │
├─────────────────────────────────────────────┤
│  Layer 1: 结构图谱（SQLite + FTS5）          │
│  符号 · 边 · 调用点 · AST 解析               │
├─────────────────────────────────────────────┤
│  Layer 2: 语义向量（SQLite）                 │
│  余弦搜索 · 图扩展 · RRF 融合排名            │
├─────────────────────────────────────────────┤
│  Layer 3: 持久化记忆（JSONL）                │
│  决策 · 模式 · 约定 · 跨会话保留             │
├─────────────────────────────────────────────┤
│  Layer 4: 跨项目关联（JSONL）               │
│  共享符号 · 推断关系 · 多 repo 联查          │
└─────────────────────────────────────────────┘
```

### Layer 1：结构图谱

用 tree-sitter 对代码做 AST 解析，提取函数、类、变量、模块的定义和调用关系，存入 SQLite（带 FTS5 全文搜索）。不是文本搜索，是真正的代码结构——「谁调用了这个函数」「这个文件依赖哪些模块」「改这个符号会影响哪些地方」。

### Layer 2：语义向量

支持三种 embedding 提供商：
- **本地 ONNX**（`nomic-embed-text-v1.5`）：无 API key，离线运行
- **OpenAI**（`text-embedding-3-small`）：支持自定义 base URL（Azure、代理）
- **Voyage AI**（`voyage-code-3`）：代码专用，官方推荐

搜索时三路融合（FTS5 精确匹配 + 语义向量 + 1-hop 图扩展），用 RRF（Reciprocal Rank Fusion）排名。结果来源标注清楚：`[FTS]`、`[SEM]`、`[GRAPH]`、`[FTS+SEM+G]`。

### Layer 3：持久化记忆

这是让 AI 「记住」而不是「每次重新理解」的关键层。

记忆类型：

| 类型 | 内容 |
|---|---|
| `decision` | 架构选择、技术决策、权衡结论 |
| `pattern` | 重复出现的方案、代码模式 |
| `convention` | 命名规则、工作流约定、风格指南 |
| `bug` | 已知问题、临时方案、已踩的坑 |
| `context` | 业务背景、项目目标、用户偏好 |

记忆**全自动**工作：
- **自动回调**：每次 prompt 时，hook 搜索相关记忆并注入对话
- **自动保存**：Claude 主动保存重要事实，不需要你提醒

存储路径：
- `~/.graphmind/memory/global.jsonl` — 跨项目全局知识
- `~/.graphmind/memory/<project-slug>.jsonl` — 项目专属记忆

### Layer 4：跨项目关联

注册多个 repo 后，GraphMind 自动推断它们之间的依赖关系：共享的符号、互相引用的接口、隐式的耦合。`gm_cross_query` 一次搜索跨所有项目，`gm_cross_deps` 显示哪些项目依赖当前 repo。

---

## 安装：两分钟上手

### macOS 桌面端（推荐）

从 [Releases 页面](https://github.com/aouicher/graphmind/releases) 下载 `.dmg`，安装后引导配置 MCP、hooks、skill 和 embedding——不需要终端操作。

| 平台 | 文件 |
|---|---|
| macOS Apple Silicon | `GraphMind-macos-arm64.dmg` |
| macOS Intel | `GraphMind-macos-x64.dmg` |

### CLI 一键安装（macOS/Linux）

```bash
curl -fsSL https://raw.githubusercontent.com/aouicher/graphmind/main/scripts/install.sh | bash
```

### Homebrew

```bash
brew install aouicher/graphmind/graphmind        # CLI
brew install --cask aouicher/graphmind/graphmind # 桌面端（macOS）
```

---

## 两步接入 AI 助手

```bash
graphmind setup          # 全局一次：配置 Claude Code、Cursor、hook、skill
cd ~/projects/myapp
graphmind init           # 每个项目一次：注册、git hooks、构建图谱
```

`graphmind setup` 做了什么：
1. Shell PATH 配置
2. Claude Code hooks（拦截 grep/find，注入会话上下文，预取图谱）
3. Claude Code skill（`/gm` + 19 个子 skill）
4. Claude Desktop MCP 配置
5. Claude Code MCP 配置（`~/.claude/settings.json`）
6. Cursor 全局 MCP 配置（`~/.cursor/mcp.json`）
7. CLAUDE.md 注入图谱说明

`graphmind init` 做了什么：
1. 注册当前目录到 graphmind 注册表
2. 写入 MCP 项目配置（`~/.claude.json` per-project scope，VS Code `.vscode/mcp.json`）
3. 安装 git hooks（commit 后自动增量重建，push 前检查影响范围）
4. 构建代码图谱

两条命令都是**幂等的**，重复运行安全。

---

## 25 个 MCP 工具：Agent 开发者的完整工具箱

### 结构查询

| 工具 | 用途 |
|---|---|
| `gm_query` | 查找符号及其连接关系 |
| `gm_fn` | 函数完整详情（源码 + 调用方 + 被调用方） |
| `gm_outline` | 文件的层级符号树 |
| `gm_file` | 文件原始内容 |
| `gm_who_calls_chain` | 传递性调用链（BFS 遍历） |
| `gm_dead_code` | 找出没有入边的符号 |
| `gm_similar` | 结构相似的符号 |
| `gm_listeners` | 按事件名找监听器 |

### 依赖与影响

| 工具 | 用途 |
|---|---|
| `gm_deps` | 文件级依赖图 |
| `gm_impact` | 传递性反向依赖 |
| `gm_fn_impact` | 修改某符号的波及范围 |
| `gm_diff_impact` | 当前 git 变更的影响范围 |
| `gm_map` | 连接度最高的文件 |
| `gm_cycles` | 循环依赖检测 |
| `gm_export` | 导出子图（Mermaid / DOT / JSON） |

### 搜索

| 工具 | 用途 |
|---|---|
| `gm_search` | 混合搜索（FTS + 语义 + 图） |

### 持久化记忆

| 工具 | 用途 |
|---|---|
| `gm_memory_search` | 搜索已存储的决策/模式 |
| `gm_memory_add` | 存储一条事实（需确认） |
| `gm_memory_list` | 列出记忆条目 |

### 跨项目

| 工具 | 用途 |
|---|---|
| `gm_cross_query` | 跨所有项目搜索符号 |
| `gm_cross_deps` | 跨项目依赖图 |
| `gm_cross_links` | 所有跨项目关联 |

### 状态

| 工具 | 用途 |
|---|---|
| `gm_status` | 项目健康状态和统计 |
| `gm_context` | 会话开始时的完整项目上下文 |
| `gm_list_projects` | 所有已注册的项目 |

---

## 实际使用场景

### 场景 1：Agent 开发中的知识图谱查询

你在构建一个 Coding Agent，需要让它理解目标代码库。传统方式是让 Agent 反复 grep 和 cat 文件——每次都消耗大量 token，还容易漏掉深层关联。

接入 GraphMind 后，Agent 可以直接调用 `gm_query`、`gm_fn`、`gm_deps` 等 MCP 工具，一次调用返回精确的结构信息，而不是原始文本流。

**实测对比**：在 10 万行代码库上，`grep -r` 返回 1.5M+ tokens；同等查询 `graphmind search` 返回不到 300 tokens，结构化、已排序、带来源标注。

### 场景 2：大型项目的改动影响评估

接到一个改动需求，不知道会影响多少地方？

```bash
graphmind diff-impact          # 当前工作区的改动影响
graphmind fn-impact <symbol>   # 改这个函数会波及哪些地方
graphmind impact <file>        # 改这个文件的所有传递性依赖
```

或者在 Claude Code 里直接问：「如果我修改 `AuthService.validateToken`，会影响哪些模块？」——`gm_fn_impact` 会给出精确的调用链和影响范围。

### 场景 3：死代码排查与技术债清理

```bash
graphmind dead-code --kind function    # 找出没有调用者的函数
graphmind cycles                       # 找循环依赖
graphmind map                          # 找连接度最高（最脆弱）的文件
```

### 场景 4：跨项目的 Monorepo 分析

```bash
cd ~/projects/api && graphmind init
cd ~/projects/web && graphmind init
cd ~/projects/shared-lib && graphmind init

graphmind cross query "AuthService"    # 三个 repo 里的 AuthService 都找出来
graphmind cross deps shared-lib        # 谁依赖了 shared-lib？
graphmind cross links                  # 所有跨项目关联一图展示
```

### 场景 5：决策记忆，跨会话保留

重要的架构决策告诉 Claude Code 一次，GraphMind 自动保存，之后每次会话自动注入：

```bash
graphmind memory add "我们选择 Redis 而不是 Memcached，因为需要 pub/sub 支持，且部分数据需要持久化" --global
```

下次会话时，只要话题涉及缓存选型，这条记忆就会自动出现在上下文里——不需要你重新解释。

---

## Token 优化机制

GraphMind 的 MCP 响应专门为 LLM 消费优化：

**紧凑格式**：每个符号一行，而不是冗长 JSON：
```
>> 5 result(s) for "auth" [FTS+semantic+graph]:

  AuthService [Class] src/services/auth.ts:3 (0.95) [FTS+SEM]
    implements Service
  validate_token [Function] src/services/auth.ts:15 (0.82) [FTS+G]
    (token: string, scope?: string) -> TokenResult
```

**字段剪枝**：不返回 id、null 字段、冗余统计。只有有用的信息。

**内容按需**：符号源码默认不返回，需要时传 `include_content: true`。

**Hook 缓存去重**：5 分钟内同一查询直接跳过（0 token 消耗），缓存存在 `/tmp/graphmind-hook-cache.txt`。

**智能搜索拦截**：Claude Code hook 自动把 `grep`、`find`、`rg` 等命令重写为 `graphmind search`，但会识别「需要完整输出」的模式（如 `grep -c`、管道到 `wc`）并放行。

---

## 安全设计

- **无开放端口**：MCP 通过 stdio，不监听任何端口
- **路径限制**：所有文件操作限制在注册路径 + `~/.graphmind/`
- **默认无网络**：本地运行，embedding API 调用需显式配置
- **API key 本地存储**：在 `~/.graphmind/config.json`，不发送到任何地方（除配置的 provider）
- **原子写入**：memory JSONL 写入用 tmp+rename，防止损坏

---

## 导出：把图谱可视化

```bash
graphmind export -f mermaid           # 当前项目的 Mermaid 图
graphmind export -f dot               # Graphviz dot 格式
graphmind export -f json              # JSON 图（供其他工具消费）
graphmind export --cross -f mermaid   # 跨项目关联图
graphmind export --obsidian ~/vault/  # Obsidian vault（[[wikilinks]] 格式）
```

Obsidian 导出特别适合需要把代码知识管理整合进个人知识库的开发者：每个符号变成一个 Obsidian 节点，依赖关系变成 wikilinks。

---

## 和 CodeGraph MCP 的关系

如果你已经在用 `codegraph`（本项目的 CLAUDE.md 里配置的 MCP），GraphMind 的定位有所不同：

| | CodeGraph | GraphMind |
|---|---|---|
| 实现语言 | TypeScript/Python | **Rust** |
| 持久化记忆 | 无 | **有（跨会话）** |
| 跨项目 | 无 | **有** |
| 向量搜索 | 无 | **有（本地/OpenAI/Voyage）** |
| 安装方式 | MCP 配置 | CLI + 桌面端 |
| 开放源码 | 视具体实现 | **MIT** |

两者 API 设计理念相近（都是给 AI 的代码图谱），但 GraphMind 功能更全、层次更多，代价是需要独立安装和初始化。

---

> **相关链接**
> - [GitHub 仓库](https://github.com/aouicher/graphmind)
> - [官方网站](https://getgraphmind.com)
> - [Releases / 下载](https://github.com/aouicher/graphmind/releases)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: GraphMind (aouicher/graphmind, 191★, MIT, Rust) is a local-first code intelligence platform that turns any codebase into a queryable knowledge graph. It exposes 25 MCP tools to Claude Code, Cursor, Windsurf, Cline, and other MCP-compatible assistants — returning structured symbol graphs, call chains, dependency maps, blast-radius analysis, and cross-project links. Up to 5,700× fewer tokens than raw grep. Four layers: structural graph (tree-sitter AST, 30+ languages, SQLite+FTS5) + semantic embeddings (local ONNX / OpenAI / Voyage AI, RRF fusion) + persistent memory (decisions, patterns, conventions survive across sessions) + cross-project links (shared symbols, inferred relationships). Everything runs locally. No cloud, no open ports, no telemetry.

---

## Why It Matters for Agent Builders

Every AI coding assistant starts each session with no memory of prior work. GraphMind fixes this with four layers of persistent code intelligence. The key for agent developers: instead of having your agent loop through file reads and grep commands (expensive, slow, incomplete), it calls a single MCP tool and gets back structured graph data — callers, callees, dependency chains, impact analysis — in under 300 tokens per query.

## Install in Two Commands

```bash
# Global (once)
curl -fsSL https://raw.githubusercontent.com/aouicher/graphmind/main/scripts/install.sh | bash
graphmind setup

# Per project
cd ~/projects/myapp && graphmind init
```

That's it. Claude Code, Cursor, and VS Code pick up the MCP server automatically.

## Key MCP Tools

- **`gm_search`** — Hybrid FTS + semantic + graph search. Returns ranked results with source tags: `[FTS]`, `[SEM]`, `[GRAPH]`, `[FTS+SEM+G]`.
- **`gm_fn`** — Full function detail: source code + all callers + all callees. One call, one token-efficient response.
- **`gm_fn_impact`** / **`gm_diff_impact`** — Blast radius for a symbol or for current git changes.
- **`gm_dead_code`** — Find unreachable symbols. Useful for cleanup before a refactor.
- **`gm_memory_search`** / **`gm_memory_add`** — Search and store decisions/patterns/conventions that survive across sessions.
- **`gm_cross_query`** — Search across all registered repos in one call.
- **`gm_export`** — Export subgraph as Mermaid, DOT, JSON, or Obsidian vault.

## Token Comparison

On a ~100K LOC codebase: `grep -r` for a single query returns 1.5M+ tokens. `graphmind search` for the same query returns under 300 tokens — ranked, structured, with source attribution.

**Links**: [GitHub](https://github.com/aouicher/graphmind) · [Website](https://getgraphmind.com) · [Releases](https://github.com/aouicher/graphmind/releases)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
