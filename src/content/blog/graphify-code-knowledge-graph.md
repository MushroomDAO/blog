---
title: "Graphify：把整个代码仓库变成一张可查询的知识图谱，87k stars，YC S26"
titleEn: "Graphify: Turn Your Entire Codebase Into a Queryable Knowledge Graph — 87k Stars, YC S26"
description: "Graphify 是一个 AI 编程助手 Skill，用一条命令把任意代码库（含文档、PDF、图片、视频）映射成知识图谱，让 AI 直接查询图谱关系而不是反复重读文件。tree-sitter 本地解析，零 API 调用，支持 Claude Code、Cursor、Codex、Gemini CLI 等 20+ 工具。YC S26 孵化，GitHub 87k stars。"
descriptionEn: "Graphify is an AI coding assistant skill that maps any codebase — plus docs, PDFs, images, videos — into a queryable knowledge graph in one command. AI queries graph relationships instead of re-reading files. Local tree-sitter parsing, zero API calls for code. Supports Claude Code, Cursor, Codex, Gemini CLI, and 20+ tools. YC S26. 87k GitHub stars."
pubDate: "2026-07-18"
updatedDate: "2026-07-18"
category: "Tech-Experiment"
tags: ["知识图谱", "AI编程", "Claude Code", "Cursor", "开源", "YC", "代码理解", "tree-sitter"]
heroImage: "../../assets/images/graphify-code-knowledge-graph-banner.jpg"
---

> **GitHub**：[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) · ⭐ 87,000+  
> **PyPI**：`graphifyy`（双 y）  
> **孵化**：YC S26（有望成为第 5 个突破 100k stars 的 YC 开源项目）

---

## 用一句话说清楚

你的 AI 编程助手（Claude Code、Cursor、Codex……）理解代码库的方式是：**一遍遍重读文件**。

`/graphify .` 之后，它的方式变成：**查询一张图**。

这张图知道 `APIRouter` 连接着哪 47 个节点，知道 `FastAPI` 到 `ModelField` 的最短路径只需 3 跳，知道哪些文件有不为人知的跨模块依赖——而这些关系，在你读文件的时候几乎不可能一次看见。

---

## 不是向量索引，是真正的图

这是 Graphify 和大多数「代码库 RAG」方案的根本区别。

大多数方案：把代码切片、embedding、存进向量库，查询时做相似度搜索。这本质上是**语义搜索**——它能告诉你「这段代码跟你的问题相关」，但不能告诉你「这个函数被哪些模块调用」「改这里会影响什么」。

Graphify：用 tree-sitter AST 解析代码，**在本地**构建一张真正的图（节点 = 概念，边 = 关系）。查询时遍历图路径，不是向量近邻搜索。

每条边都标注了置信标签：
- `EXTRACTED`：关系明确写在源码里（imports、calls、inherits）
- `INFERRED`：由 Graphify 解析推断（隐式依赖、跨文件引用）
- `AMBIGUOUS`：有多种解释，明确标出

你始终知道哪些关系是读出来的，哪些是猜的。

---

## 30 秒开始

```bash
# 安装（推荐 uv，隔离环境）
uv tool install graphifyy

# 注册 Skill 到你的 AI 助手
graphify install

# 在你的 AI 助手里输入
/graphify .
```

完成后，`graphify-out/` 目录里出现三个文件：

| 文件 | 用途 |
|---|---|
| `graph.html` | 在浏览器里打开，力导向图可视化，节点可点击、可过滤、可搜索 |
| `GRAPH_REPORT.md` | 重点摘要：God nodes、意外连接、设计决策、建议问题 |
| `graph.json` | 完整图数据，所有查询都基于它 |

代码解析**完全本地**，零 API 调用，没有任何东西离开你的机器。

---

## 五种查询方式

一旦图建好，你可以用这些方式查询（在 AI 助手里，或直接用 CLI）：

```bash
# 提问（返回相关子图）
/graphify query "authentication 和 database 是怎么连接的？"

# 路径追踪（两个概念之间最短路径）
/graphify path "FastAPI" "ModelField"
# → FastAPI --uses--> DefaultPlaceholder <--references-- get_request_handler() --references--> ModelField

# 概念解释（节点详情 + 所有连接）
/graphify explain "APIRouter"
# → Node: APIRouter, Source: routing.py L2210, Degree: 47, Connections: ...

# 增量更新（只更新改动的文件）
/graphify ./docs --update

# 添加论文/视频
/graphify add https://arxiv.org/abs/1706.03762
/graphify add <youtube-url>
```

---

## 能处理什么文件

Graphify 的「代码库」定义非常宽泛：

**代码（36 种 tree-sitter 语法）**：Python、TypeScript、JavaScript、Go、Rust、Java、C/C++、CUDA、Metal、Ruby、C#、Kotlin、Scala、PHP、Swift、Lua、Zig、PowerShell、Elixir、Julia、Vue、Svelte、Astro、SQL 等。跨文件的 `calls`/`imports`/`inherits`/`mixes_in` 关系全部自动解析。

**配置与 Schema**：Terraform/HCL、SQL Schema（含 PostgreSQL 实时内省）、MCP 配置（`mcp.json`、`claude_desktop_config.json`）、包清单（`pyproject.toml`、`go.mod`、`pom.xml`）。

**文档与媒体**：Markdown、HTML、RST、YAML、PDF、Word/Excel、图片（PNG/JPG/WebP）、视频/音频（`faster-whisper` 转录）、YouTube 链接。

**Google Workspace**：Google Docs、Sheets、Slides（需要 `gws` 认证）。

> **注意**：代码用 tree-sitter 本地解析，不调用 API。文档和媒体需要调用你 AI 助手的模型 API（或自配 API Key）。

---

## 基准测试

在 LOCOMO（300 个问题的长期记忆 QA）和 LongMemEval-S（50 个问题）上的结果：

| 测试集 | 指标 | Graphify | mem0 | supermemory | dense RAG |
|---|---|---|---|---|---|
| LOCOMO (n=300) | recall@10 | **0.497** | 0.048 | 0.149 | — |
| LOCOMO (n=300) | QA 准确率 | 45.3% | 27.3% | 49.7% | — |
| LongMemEval-S (n=50) | QA 准确率 | **76%** | — | — | 76% |
| 图构建 | LLM 费用 | **0** | 按 token | 按 token | 按 token |

两个关键发现：
1. 图遍历在 recall@10 上远超向量方案（0.497 vs 0.048/0.149）
2. QA 准确率与 dense RAG 持平，但构建图不需要 LLM 费用

（评测方法：两位 judge 独立评分，Cohen's kappa 0.81，确保客观性。）

---

## 20+ 平台一键接入

```bash
# 自动检测当前环境并安装
graphify install

# 指定平台
graphify install --platform codex
graphify cursor install
graphify install --platform gemini
graphify install --platform kimi
```

支持的平台（完整列表）：Claude Code、Cursor、Codex、OpenCode、Gemini CLI、GitHub Copilot CLI、VS Code Copilot Chat、Aider、OpenClaw、Kilo Code、Amp、Trae、Kimi Code、Factory Droid、Hermes、Pi、Devin CLI、Google Antigravity……

每个平台安装后，AI 助手会优先查图而不是反复读文件——Claude Code 和 Codex 用 PreToolUse hook 拦截文件读取操作，Cursor 用 `alwaysApply: true` 规则。

---

## 团队使用：把图提交进 git

Graphify 的设计理念是图应该被 commit 进版本库，让整个团队共享：

```bash
# 一次性构建，提交
/graphify .
git add graphify-out/
git commit -m "init: graphify knowledge graph"

# 之后每次 commit 自动重建（只重建改动的文件，零 API 费用）
graphify hook install
```

多人同时修改代码时，git merge 会自动 union-merge 两份 `graph.json`（不会出现 conflict markers）。

---

## PR 看板：图辅助代码审查

这是一个有意思的功能：

```bash
# PR 看板（CI 状态、Review 状态、Worktree 映射）
graphify prs

# 深入分析 PR #42 的图影响范围
graphify prs 42

# AI 排序你的 Review 队列（按重要性）
graphify prs --triage

# 找出共享图社区的 PR（合并顺序风险）
graphify prs --conflicts
```

`graphify prs 42` 会告诉你这个 PR 改动的代码节点，在知识图谱里会影响哪些其他节点——这是比「看 diff」更立体的代码审查视角。

---

## 进阶：Neo4j / FalkorDB 推送 + MCP Server

```bash
# 推送到 Neo4j（可视化、Cypher 查询）
uv tool install "graphifyy[neo4j]"
graphify export neo4j --uri bolt://localhost:7687

# 启动 MCP stdio server（让任何 MCP 客户端都能查询图）
uv tool install "graphifyy[mcp]"
graphify mcp serve
```

MCP server 让你可以把整个代码库的知识图谱作为工具暴露给任何 AI 工具——不只是 coding assistants，也可以是自定义 Agent。

---

## 为什么 87k stars？

Graphify 在 7 月中旬单日 trending 1,623 stars，总 stars 87k+，几乎肯定要成为 YC 史上第 5 个突破 100k stars 的开源项目。

驱动力是一个**真实痛点**被真实解决了：

AI 编程助手的瓶颈不是模型能力，而是上下文。一个 10 万行的代码库，模型无法在一个对话窗口里全部读完——所以它只能每次读你给它的几个文件，靠猜来填补空白。

Graphify 把「读文件」换成「查图」：图一次构建，永久可查；每次对话只需要传相关子图，不是整个代码库。这是根本性的效率提升，解释了为什么开发者会第一次用完就去 GitHub 点 star。

---

## 一句话总结

输入 `/graphify .`，30 秒后你的 AI 助手就有了整个代码库的知识图谱。查关系不用 grep，问路径不用读文件，改代码知道影响范围。tree-sitter 本地解析，代码零 API 费用，支持 20+ AI 工具。87k stars，YC S26。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Graphify: Your Codebase as a Queryable Knowledge Graph

**GitHub**: [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) · ⭐ 87k+  
**Install**: `uv tool install graphifyy` (double-y on PyPI)  
**Backed by**: YC S26

### The Core Shift

AI coding assistants understand your codebase by re-reading files. Graphify changes that to querying a graph.

One command: `/graphify .`  
Result: three files — `graph.html` (interactive browser visualization), `GRAPH_REPORT.md` (key findings), `graph.json` (full graph for querying).

### Not a Vector Index

This is the key differentiator. Most "codebase RAG" tools: chunk → embed → vector store → similarity search. They find semantically related code but can't tell you "what calls this function" or "what would break if I change this."

Graphify: tree-sitter AST parsing → real graph (nodes = concepts, edges = relationships). Graph traversal, not nearest-neighbor search. Every edge tagged `EXTRACTED` (explicit in source) or `INFERRED` (resolved). You always know what was found vs. inferred.

### Zero API Calls for Code

Code is parsed entirely locally with tree-sitter — no LLM, nothing leaves your machine. Only docs/PDFs/images/video need an API call.

### Query Examples

```bash
/graphify query "how does auth connect to the database?"
/graphify path "FastAPI" "ModelField"
# → FastAPI --uses--> DefaultPlaceholder <--references-- get_request_handler() --references--> ModelField (3 hops)
/graphify explain "APIRouter"
# → Source: routing.py L2210 · Degree: 47 · Connections: ...
```

### Benchmarks

| Test | Metric | Graphify | mem0 | supermemory |
|---|---|---|---|---|
| LOCOMO (n=300) | recall@10 | **0.497** | 0.048 | 0.149 |
| LongMemEval-S (n=50) | QA accuracy | **76%** | — | — |
| Build cost | LLM credits | **0** | per-token | per-token |

### 20+ Platforms

```bash
graphify install           # auto-detect Claude Code
graphify cursor install    # Cursor
graphify install --platform codex  # Codex
graphify install --platform gemini # Gemini CLI
```

Claude Code and Codex use PreToolUse hooks to intercept file reads and redirect to graph queries. Cursor uses `alwaysApply: true` rules.

### Team Setup

```bash
git add graphify-out/ && git commit   # share graph with team
graphify hook install                  # auto-rebuild on every commit (zero API cost)
```

Two devs committing in parallel: `graph.json` gets union-merged automatically, no conflict markers.

### PR Dashboard

```bash
graphify prs 42         # graph impact of PR #42
graphify prs --triage   # AI-ranked review queue
graphify prs --conflicts  # PRs sharing graph communities (merge-order risk)
```

### Why 87k Stars

The bottleneck for AI coding assistants isn't model capability — it's context. A 100k-line codebase doesn't fit in one context window. Graphify replaces "read files" with "query graph": built once, queryable forever, only relevant subgraphs passed per conversation. That's a fundamental efficiency win, which is why developers star it immediately after first use.

On track to become the 5th YC open-source project ever to hit 100k stars.

© 2026 Author: Mycelium Protocol
