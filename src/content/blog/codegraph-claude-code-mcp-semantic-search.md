---
title: "CodeGraph：给 Claude Code 装一个代码知识图谱，省钱 35%、工具调用减少 70%"
titleEn: "CodeGraph: A Local Knowledge Graph for Claude Code — 35% Cheaper, 70% Fewer Tool Calls"
description: "CodeGraph 通过 MCP 协议为 Claude Code、Cursor 等 AI 编程助手提供本地代码知识图谱，跨 7 个真实项目基准测试显示平均节省 35% API 成本，减少 70% 工具调用次数，全程 100% 本地运行。"
descriptionEn: "CodeGraph delivers a pre-indexed local knowledge graph to AI coding agents via MCP, benchmarked at 35% cost reduction and 70% fewer tool calls across 7 real-world codebases — 100% local, no external APIs."
pubDate: 2026-05-23
updatedDate: 2026-05-23
category: Tech-News
tags: ["Claude-Code", "MCP", "CodeGraph", "AI-Coding", "Developer-Tools", "Knowledge-Graph"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

> **BLUF**：CodeGraph 是一个开源工具，通过 MCP 协议为 Claude Code、Cursor、Codex CLI 等 AI 编程助手构建本地代码知识图谱。基准测试（7 个真实项目，4 次重复取中位数）显示：平均节省 35% API 成本，减少 70% 工具调用，提速 49%，全程 100% 本地运行，零数据外传。

> 📌 GitHub 仓库：
> https://github.com/colbymchenry/codegraph
>
> 📌 npm 包页面：
> https://www.npmjs.com/package/@colbymchenry/codegraph

---

## AI 编程助手为什么会"扫文件扫到破产"？

当你用 Claude Code 问"这个功能是怎么实现的"，它通常会启动 Explore 子代理，依次执行 grep、glob、Read，扫描大量文件，再组合出答案。每一次工具调用都消耗 token，每一次文件读取都在计费。

这不是 Bug，这是当前 AI 代理在没有预索引时的唯一选择——**它必须边探索、边理解代码结构**。

CodeGraph 的思路是：**把这部分工作提前做好，存入本地数据库，让 AI 直接查图谱，而非反复扫文件**。

## CodeGraph 是什么？

CodeGraph 是一个基于 MCP（Model Context Protocol）协议的本地代码知识图谱工具，核心组件：

- **索引引擎**：使用 tree-sitter 解析源码，提取符号（函数、类、变量）、调用关系、引用图，写入本地 SQLite 数据库
- **全文搜索**：基于 FTS5 的符号搜索，按名称即时定位代码位置
- **影响分析**：追踪任意符号的调用者（callers）、被调用者（callees）和完整影响半径
- **框架路由识别**：识别 Django、FastAPI、Express、Rails、Spring 等 14 个框架的路由文件，将 URL pattern 与处理函数关联
- **自动同步**：使用操作系统原生文件监听（FSEvents/inotify/ReadDirectoryChangesW），代码修改后增量更新索引，零配置

支持的编程语言（19+）：TypeScript、JavaScript、Python、Go、Rust、Java、C#、PHP、Ruby、C、C++、Swift、Kotlin、Dart、Lua、Svelte 等。

## 基准测试数据

开发者对 7 个真实开源项目进行了对照测试（Claude Code Opus 4.7，headless 模式，每组 4 次取中位数）：

| 项目 | 语言 | 成本节省 | Token 减少 | 工具调用减少 |
|------|------|---------|-----------|------------|
| VS Code | TypeScript，约 1 万文件 | 35% | 73% | 72% |
| Excalidraw | TypeScript，约 600 文件 | 47% | 73% | 86% |
| Django | Python，约 2700 文件 | 34% | 64% | 81% |
| Tokio | Rust，约 700 文件 | 52% | 81% | 89% |
| OkHttp | Java，约 640 文件 | 17% | 41% | 64% |
| Gin | Go，约 150 文件 | 22% | 23% | 19% |
| Alamofire | Swift，约 100 文件 | 38% | 59% | 77% |

**平均：节省 35% 成本 · 减少 59% token · 提速 49% · 减少 70% 工具调用**

规律很清晰：**项目越大，效果越显著**。Gin（150 个文件）的收益最小（19%），因为原生 grep/find 在小项目上本就廉价；VS Code（1 万文件）的工具调用减少高达 72%，因为文件扫描代价巨大。

## 如何安装？配置是全局的还是项目级的？

这里有一个容易混淆的地方，回答用户实际关心的问题：

**安装 CodeGraph 分两个层次：**

**层次一：MCP 服务器配置（可以全局生效）**

运行安装命令后，CodeGraph 会配置 Claude Code、Cursor 等工具的 MCP 服务器入口。选择"global"模式时，会写入全局配置（Claude Code 的 `~/.claude.json`），此后**所有项目下打开 Claude Code 都能使用 CodeGraph 的 MCP 工具**。

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# 或者有 Node.js 时
npx @colbymchenry/codegraph
```

安装时选择 global，则 MCP 服务器全局有效，无需每个仓库重复安装。

**层次二：项目索引（必须每个项目单独初始化）**

MCP 服务器知道怎么查图谱，但图谱本身存储在各项目的 `.codegraph/` 目录下。**每个项目都需要单独跑一次初始化**，构建该项目的 SQLite 知识图谱：

```bash
cd your-project
codegraph init -i
```

`-i` 是交互模式，会引导你完成索引配置。初始化后，`.codegraph/` 目录会出现在项目根目录（建议加入 `.gitignore`，索引是本地产物）。

**结论**：一次全局安装即可；但每个仓库都需要单独 `codegraph init -i` 建立索引，否则 Claude Code 查图谱时是空的。

## 查询是如何工作的？

有了索引后，Claude Code 在回答代码架构问题时不再"扫文件"，而是直接调用 CodeGraph 提供的 MCP 工具：

- `codegraph_context`：快速定位某个功能区域的入口符号和关联文件
- `codegraph_explore`：获取特定符号的详细信息、调用图和相关代码片段

对比：**没有 CodeGraph** 时，Claude Code 回答"tokio 是如何调度异步任务的"需要 75 次工具调用，用时近 3 分钟，花费 $1.04；**有 CodeGraph** 时，9 次工具调用，65 秒，花费 $0.50。

## 适合哪些场景？

- **中大型代码库**：文件数在几百以上的项目，收益最明显
- **高频问答型使用**：反复询问代码架构、依赖关系、调用链的开发者
- **多语言项目**：19 种语言覆盖面广，混合栈项目同样适用
- **注重隐私/离线开发**：全部 100% 本地，没有任何数据上传

不适合：极小项目（文件数 < 50）或一次性脚本场景，原生搜索已经够快，CodeGraph 的索引开销不划算。

**FAQ**

**Q：CodeGraph 安装后在当前会话之外的仓库能用吗？**
A：能。安装时选择"global"模式，MCP 服务器配置写入全局文件（`~/.claude.json`），此后所有项目的 Claude Code 都能加载 CodeGraph。但每个新项目必须单独运行 `codegraph init -i` 生成该项目的索引，否则 CodeGraph 工具虽然存在，返回的是空结果。

**Q：索引会随代码变化自动更新吗？**
A：会。CodeGraph 使用 OS 原生文件监听事件，代码修改后自动增量更新索引，无需手动重建。

**Q：对 Claude Code 以外的 AI 工具支持吗？**
A：支持 Cursor、Codex CLI、opencode、Hermes Agent。安装时选择对应工具即可，安装脚本会自动检测已安装的工具并配置。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: CodeGraph is an open-source MCP tool that gives AI coding agents (Claude Code, Cursor, Codex CLI) a pre-indexed local knowledge graph of code symbols, call graphs, and relationships. Benchmarked across 7 real-world codebases: 35% cheaper, 70% fewer tool calls, 49% faster — all 100% local.

> 📌 GitHub:
> https://github.com/colbymchenry/codegraph
>
> 📌 npm:
> https://www.npmjs.com/package/@colbymchenry/codegraph

## The Problem: AI Agents "Scan Their Way Through Code"

Without a pre-built index, Claude Code answers architecture questions by spawning Explore agents that run grep, glob, and Read in succession — burning tokens on discovery before they reach the right files. Every tool call costs money and time.

CodeGraph's approach: **index the codebase upfront, store it locally in SQLite, let the agent query the graph instead of scanning files.**

## What CodeGraph Does

CodeGraph is a local MCP server that builds a semantic knowledge graph of your codebase using tree-sitter:

- **Symbol extraction**: functions, classes, variables with full relationship edges
- **Call graphs**: callers, callees, and impact radius for any symbol
- **FTS5 full-text search**: instant symbol lookup by name
- **Framework-aware routing**: links URL patterns to handlers across 14 frameworks (Django, FastAPI, Express, Rails, Spring, NestJS, etc.)
- **Auto-sync**: OS-native file watchers keep the index current as you code

Supports 19+ languages including TypeScript, Python, Go, Rust, Java, C#, Swift, Kotlin, and more.

## Benchmark Results

Tested with Claude Code Opus 4.7 (headless), 4 runs per codebase, median reported:

| Codebase | Cost savings | Token reduction | Tool call reduction |
|----------|-------------|----------------|---------------------|
| VS Code (~10k files) | 35% | 73% | 72% |
| Excalidraw (~600 files) | 47% | 73% | 86% |
| Django (~2.7k files) | 34% | 64% | 81% |
| Tokio (~700 files) | 52% | 81% | 89% |
| Gin (~150 files) | 22% | 23% | 19% |

**Average: 35% cheaper · 59% fewer tokens · 49% faster · 70% fewer tool calls**

The gains scale with codebase size: small repos (< 150 files) see modest improvements because native grep is already fast; large repos (VS Code at 10k files) see the biggest wins.

## Installation: Global vs Per-Project

Two distinct layers:

**Layer 1 — MCP server config (can be global)**: Run the installer and choose "global" mode. CodeGraph writes to `~/.claude.json`, making the MCP tools available across all your projects with no further setup.

```bash
npx @colbymchenry/codegraph
# choose: global installation
```

**Layer 2 — Project index (required per-project)**: The MCP server is ready, but the knowledge graph is stored per-project in `.codegraph/`. Each repo needs its own initialization:

```bash
cd your-project
codegraph init -i
```

**Short answer to the common question**: One global install covers all repos for the MCP server. But every repo needs `codegraph init -i` separately — without a project index, CodeGraph tools return empty results.

## FAQ

**Q: Does the index stay current as I edit code?**
A: Yes — OS-native file watchers (FSEvents on macOS, inotify on Linux) auto-sync changes incrementally. No manual rebuild needed.

**Q: Does it work with agents other than Claude Code?**
A: Yes: Cursor, Codex CLI, opencode, and Hermes Agent are all supported. The installer auto-detects which agents are installed and configures them.

**Q: Any privacy concerns?**
A: No. All processing is local. The SQLite index lives in `.codegraph/` inside your project. No API keys, no cloud services, no data transmission.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
