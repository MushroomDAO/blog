---
title: "code-review-graph：给 AI 编程助手建一张本地代码关系图，中位数减少 65 倍 token 用量"
titleEn: "code-review-graph: A Local Code Graph for AI Assistants That Cuts Token Use 65x at the Median"
description: "tirth8205 开源的本地代码智能图工具，29.5k stars，Python，MIT License。用 Tree-sitter 把代码库解析成函数/类/调用/测试的关系图，存储在 SQLite；代码审查时只把受影响的文件和调用链（Blast Radius）交给 AI，而不是整个代码库。六个真实仓库测试：中位数减少 65 倍 token 用量，最大 376 倍（fastapi）。支持 15+ AI 编程平台，30+ 编程语言，增量更新 2.5 秒。"
descriptionEn: "tirth8205's local code intelligence graph, 29.5k stars, Python, MIT License. Tree-sitter parses your codebase into a function/class/call/test graph stored in SQLite. At review time, only the blast-radius files and call chains go to the AI — not the whole repo. Benchmarked across 6 real repositories: median 65× token reduction, up to 376× (fastapi). Supports 15+ AI coding platforms, 30+ languages, incremental updates in 2.5s."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["ClaudeCode", "代码审查", "Token优化", "知识图谱", "MCP", "AI编程", "Mycelium"]
heroImage: "../../assets/images/code-review-graph-tirth8205-blast-radius-token-reduction-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

AI 编程助手在做代码审查的时候有个根本问题：它不知道哪些文件和这次改动有关，所以要么读整个代码库（费 token），要么靠提示词猜（不准）。

code-review-graph 的解法是：**在本地用 Tree-sitter 把代码库解析成一张关系图**，记录函数之间的调用关系、类的继承关系、测试覆盖情况，存在 SQLite 里。代码审查时，MCP 工具查询这张图，计算出这次改动的"爆炸半径"（Blast Radius）——所有可能受影响的调用方、依赖方和测试——只把这个最小集合交给 AI 助手。

GitHub: https://github.com/tirth8205/code-review-graph | ⭐ 29,472 | Python | MIT

---

## Token 减少了多少

六个真实开源仓库的基准测试（每个仓库 5 个样本问题，取均值）：

| 仓库 | 全量 token | 图查询 token | 减少倍数 |
|------|----------:|------------:|---------:|
| fastapi | 948,793 | 2,653 | **375.6x** |
| flask | 143,594 | 2,196 | **71.0x** |
| code-review-graph 自身 | 208,821 | 3,190 | **68.1x** |
| gin | 166,868 | 2,766 | **61.9x** |
| httpx | 142,356 | 2,661 | **60.6x** |
| express | 136,052 | 3,936 | **36.0x** |

**六个仓库中位数：约 65 倍**。范围是 36x–376x，376x 是最佳单例（fastapi），不是典型值。

---

## 工作原理

```
代码库
  ↓ Tree-sitter 解析（函数/类/导入/调用/测试节点）
SQLite 关系图
  ↓ 提交 hook 或 watch mode 触发增量更新
图查询（Blast Radius 计算）
  ↓ MCP 工具
AI 助手只读受影响的最小文件集
```

1. **构建关系图**：解析所有源文件，提取函数、类、导入、调用关系、测试覆盖。
2. **增量更新**：文件保存或 commit 时，只重新解析 SHA-256 哈希变化的文件，3000 文件项目约 2.5 秒（其中 ~1.4 秒是进程启动开销）。
3. **Blast Radius**：某文件改变时，图追踪所有调用方、依赖方和关联测试，计算最小必读集合。
4. **MCP 交付**：通过标准 MCP 协议把结果交给 AI 助手；助手只读需要读的文件。

---

## 安装与使用

```bash
pip install code-review-graph          # 或 pipx install code-review-graph
code-review-graph install              # 自动检测已安装的 AI 平台并配置 MCP
code-review-graph build                # 解析代码库，建图
```

`install` 会自动检测本机有哪些 AI 编程工具，为每个工具写入正确的 MCP 配置，并注入图感知指令。之后打开项目，在 AI 助手里说：

```
Build the code review graph for this project
```

---

## 支持 15+ AI 编程平台

自动检测并配置：Claude Code、Codex、Cursor、Windsurf、Zed、Continue、OpenCode、Gemini CLI、Antigravity、Kiro、Qwen、Qoder、GitHub Copilot（VS Code）、GitHub Copilot CLI、CodeBuddy Code。

可以单独指定平台：

```bash
code-review-graph install --platform claude-code
code-review-graph install --platform codex
code-review-graph install --platform cursor
```

---

## 支持 30+ 编程语言

Python、JavaScript/TypeScript/TSX、Go、Rust、Java、C/C++、C#、VB.NET、Ruby、Kotlin、Swift、PHP、Scala、Solidity、Dart、R、Perl、Lua/Luau、Objective-C、Shell、Elixir、Zig、PowerShell、Julia、GDScript、Nix、Verilog/SystemVerilog、SQL、Terraform/HCL、Ansible、Vue/Svelte SFC、Astro、Jupyter/Databricks Notebook（.ipynb）等。

需要额外语言可以在 `.code-review-graph/languages.toml` 里自定义配置：

```toml
[languages.erlang]
extensions = [".erl"]
grammar = "erlang"
function_node_types = ["function_clause"]
```

---

## GitHub Action（CI PR 审查）

在 CI 里对每个 PR 做 Blast Radius 分析，在 PR 页面自动评论风险评分和受影响的执行流，每次 push 更新评论（sticky comment）。代码图在 CI Runner 本地构建，源代码不发往外部服务。

```yaml
on:
  pull_request:
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: tirth8205/code-review-graph@v2.3.6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

可选 `fail-on-risk` 把审查结果变成合并门控。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## code-review-graph: A Local Code Relationship Graph That Cuts AI Token Usage by 65× Median

*by Mycelium Protocol*

---

AI coding assistants have a fundamental problem on review tasks: they don't know which files are relevant to a change, so they either read the whole codebase (expensive) or guess from the prompt (imprecise).

code-review-graph's solution: **parse the codebase locally with Tree-sitter into a relationship graph** — functions, classes, call sites, imports, test coverage — stored in SQLite. At review time, an MCP tool queries this graph to compute the "blast radius" of the change: every caller, dependent, and test that could be affected. Only this minimal set goes to the AI assistant.

GitHub: https://github.com/tirth8205/code-review-graph | ⭐ 29,472 | Python | MIT

---

### How Much Does It Help

Benchmarked across 6 real open-source repositories (5 sample questions each):

| Repo | Whole-corpus tokens | Graph tokens | Reduction |
|------|--------------------:|------------:|----------:|
| fastapi | 948,793 | 2,653 | **375.6×** |
| flask | 143,594 | 2,196 | **71.0×** |
| code-review-graph (self) | 208,821 | 3,190 | **68.1×** |
| gin | 166,868 | 2,766 | **61.9×** |
| httpx | 142,356 | 2,661 | **60.6×** |
| express | 136,052 | 3,936 | **36.0×** |

**Median across 6 repos: ~65×.** Range is 36×–376×; 376× is the single best case (fastapi), not the typical result.

---

### How It Works

1. **Build the graph** — Tree-sitter parses every source file into nodes (functions, classes, imports, calls, tests) and edges (call relationships, inheritance, test coverage), stored in SQLite.
2. **Incremental updates** — On file save or commit hook, only files whose SHA-256 hash changed are re-parsed. On a ~3,000-file project, a 2-file edit re-indexes in about 2.5 seconds (of which ~1.4s is process startup).
3. **Blast radius** — When a file changes, the graph traces every caller, dependent, and associated test to compute the minimal set the AI actually needs to read.
4. **MCP delivery** — Results are delivered to the AI assistant via standard MCP protocol. The assistant reads only what matters.

---

### Install

```bash
pip install code-review-graph       # or: pipx install code-review-graph
code-review-graph install           # auto-detects AI tools, writes MCP config for each
code-review-graph build             # parse codebase and build graph
```

Then open your project and tell your AI assistant: `Build the code review graph for this project`

---

### 15+ Supported Platforms

Auto-detects and configures: Claude Code, Codex, Cursor, Windsurf, Zed, Continue, OpenCode, Gemini CLI, Antigravity, Kiro, Qwen, Qoder, GitHub Copilot, GitHub Copilot CLI, and CodeBuddy Code.

---

### GitHub Action — CI PR Reviews

On each pull request, posts a sticky comment with risk-scored functions, affected execution flows, and test gaps — updated on every push. The graph is built on your CI runner; no source code leaves your environment.

```yaml
- uses: tirth8205/code-review-graph@v2.3.6
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

Optional `fail-on-risk` input turns the review into a merge gate.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
