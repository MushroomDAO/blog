---
title: "WrenAI：开源 GenBI 引擎，让 AI Agent 生成可信 SQL 和可部署的数据看板"
titleEn: "WrenAI: An Open-Source GenBI Engine for Trustworthy SQL and Deployable Dashboards"
description: "WrenAI（Canner）是开源的 GenBI（Generative BI）引擎：通过开放上下文层（MDL 语义模型 + instructions.md + LanceDB 记忆），让 AI Agent 把自然语言问题转化为受治理的 SQL，并一键部署到 Vercel/Cloudflare Pages 的交互式看板。支持 22+ 数据源，与 Claude Code/Cursor/Codex 原生集成，Apache 2.0，16921 stars。"
descriptionEn: "WrenAI (Canner) is an open-source GenBI engine: through an open context layer (MDL semantic models + instructions.md + LanceDB memory), AI agents turn natural-language questions into governed SQL and deploy interactive dashboards to Vercel/Cloudflare Pages in one command. 22+ data sources, native Claude Code/Cursor/Codex integration, Apache 2.0, 16,921 stars."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["Text-to-SQL", "数据分析", "AI Agent", "商业智能", "语义层", "开源工具", "数据库", "Mycelium"]
heroImage: "../../assets/images/wrenai-text-to-sql-genbi-open-source-context-layer-banner.jpg"
---

*by Mycelium Protocol*

---

Text-to-SQL 项目有一个很高频的失效模式：SQL 生成得头头是道，但结果是错的。

不是模型能力不行，而是模型不知道你的业务。它不知道「销售额」在你们公司到底用哪个字段算，不知道哪些表的 join 逻辑经过了业务验证，不知道某个枚举值的中文名到底映射到数据库里的哪个字符串。Schema 里没有这些信息，模型只能猜。

**[WrenAI](https://github.com/Canner/WrenAI)** 的思路是在 Agent 和数据库之间放一个**开放的上下文层**：把这些业务知识显式化、版本控制化、Git 友好化，然后让 Agent 通过这层上下文来生成受治理的 SQL，再一键把结果变成可分享的看板。

16921 stars，Apache 2.0，2024 年 3 月开源，由 Canner 开发。

---

## 三个节拍：Generate · Deploy · Know

WrenAI 把 GenBI（Generative BI）拆成三步：

**Generate（生成）**：Agent 把自然语言问题转化为**受治理的 SQL** 和图表。背后有 schema 感知检索、MDL 规划、dry-plan 验证和带提示的结构化错误——保持正确，而不是"看起来有理但其实错了"。

**Deploy（部署）**：把任何答案变成可分享的浏览器端看板，由 `wren-core-wasm` 驱动，一条命令部署到你自己的 Vercel 或 Cloudflare Pages 账户。

**Know（知道）**：让这一切正确的知识，存在可版本控制、有证据链接的文件里：MDL 语义模型、公司定义（`instructions.md`）、以及过去有效的查询记忆。可审查、Git 友好、永远不锁在别人家的 UI 里。

---

## 核心：上下文层（Context Layer）

大多数 Text-to-SQL 方案把上下文问题推给 prompt engineering。WrenAI 把它变成一层可管理的基础设施：

### MDL（建模定义语言）

```yaml
# 示例：在 MDL 里定义「有效销售」的语义
models:
  - name: orders
    columns:
      - name: revenue
        expression: "CASE WHEN status = 'completed' THEN amount ELSE 0 END"
        description: "有效销售额，只计已完成订单"
    relationships:
      - name: customer
        joinType: MANY_TO_ONE
        condition: "orders.customer_id = customers.id"
```

MDL 覆盖：模型、列、关系、视图、Cube、指标、行级/列级访问控制（RLAC/CLAC）。

### instructions.md

业务定义、审批过的 join 逻辑、枚举值映射、单位换算——**所有 schema 里没有的信息**，都在这里显式写清楚，而不是藏在 prompt 里。Agent 每次查询前会读取这些指令。

### LanceDB 记忆（Memory）

混合检索：过去有效的查询（`queries.yml`）被存入本地 LanceDB 索引。下次问相似问题时，Agent 先召回相关的历史查询，而不是从零开始猜。

---

## 引擎：Rust + Apache DataFusion，22+ 数据源

WrenAI 的引擎层（`core/`）基于 Apache DataFusion 用 Rust 实现：

```
core/
  wren-core/         Rust 语义引擎（Apache DataFusion）
  wren-core-base/    共享 manifest 类型 + MDL builder
  wren-core-py/      Python 绑定（PyPI: wren-core）
  wren-core-wasm/    WebAssembly 构建（npm: wren-core-wasm）
  wren/              Python SDK + CLI（PyPI: wrenai）
  wren-mdl/          MDL JSON schema
```

支持的数据源（22+）：
**BigQuery、Snowflake、PostgreSQL、ClickHouse、Amazon Redshift、Databricks、DuckDB**（内置）、MySQL、MS SQL Server、Oracle、Athena、Trino、Presto、Hive，以及更多通过社区 connector 接入的数据源。

---

## 与竞品的核心差异

| 方案 | 生成 SQL | 知道业务定义 | 生成并部署看板 | 通过 Agent 集成 | 开放可审查上下文 |
|------|---------|------------|--------------|--------------|----------------|
| 原始 LLM Agent | ✅（经常错） | ❌ | ❌ | ✅ | ❌ |
| 传统 BI 工具 | ❌ | 部分，锁在工具里 | ✅（手动）| ❌ | ❌ |
| 纯语义层 | ❌ | ✅（schema 层面）| ❌ | ❌ | 部分 |
| **WrenAI** | **✅ 受治理** | **✅ + 非 schema 知识** | **✅ Agent 驱动** | **✅** | **✅** |

---

## 快速上手

### 1. 安装 CLI

```bash
pip install wrenai                            # core（DuckDB 内置）
pip install "wrenai[postgres,memory]"         # 按数据源和功能加 extra
```

国内加速：
```bash
pip install wrenai -i https://pypi.tuna.tsinghua.edu.cn/simple
# HuggingFace 模型下载超时时：
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. 给 AI 客户端安装 skill stub

```bash
npx skills add Canner/WrenAI    # 自动检测 Claude Code、Cursor、Cline、Codex
```

这个 stub 约 50 行。它教 Agent 通过 `wren skills get <name>` 获取工作流指南，通过 `wren ask "<问题>" --guided|--direct` 发起查询。

### 3. 让 Agent 配置

打开 Agent，在项目目录里说：

> "用 Wren 连接我的 Postgres 数据库。"

Agent 运行 `wren skills get onboarding`，逐步完成：检查环境 → 建立连接 profile → 脚手架项目 → 运行第一个查询。

### 4. 充实上下文（Know 节拍）

> "用 raw/ 目录里的业务文档丰富 Wren 项目的上下文。"

Agent 运行 `wren skills get enrich-context`，有两种模式：
- **Grill 模式**：一问一答，逐步确认业务定义
- **Auto-pilot 模式**：Agent 自动读取 `<project>/raw/` 并提案

两种模式都写入 MDL、instructions、queries 和 memory，全部可审查、Git 友好。

### 5. 问问题（Generate 节拍）

> "本季度销售额前 10 名的客户是谁？"

Agent 获取 MDL 上下文 → 召回相似历史查询 → 生成受治理 SQL → 通过 `wren query` 执行。

### 6. 生成并部署看板（Deploy 节拍）

> "把这个做成可以过滤和分享的交互式看板，部署到 Vercel。"

Agent 运行 `wren skills get genbi` → 从项目上下文构建 GenBI 看板 → 本地预览 → 推送到你的 Vercel/Cloudflare Pages 账户，返回可分享的在线 URL。

---

## 正确性保障

WrenAI 把几个关键的正确性原语做成了内置功能：

| 机制 | 作用 |
|------|------|
| MDL 规划 | SQL 在语义层上规划，而不是直接在原始 schema 上猜 |
| Dry-plan 验证 | 执行前验证 SQL 结构合法性，不等到运行报错 |
| Schema 感知检索 | 根据问题内容精确检索相关表和列 |
| 结构化错误 + 提示 | 错误信息包含修复提示，Agent 可以自我纠正 |
| 值剖析（Value profiling） | 检查列的实际值分布，防止枚举值错配 |
| Eval runner | 运行评估套件，持续验证查询质量 |

---

## Agent SDK

- **wren-langchain**：LangChain / LangGraph 参考集成
- **wren-pydantic**：Pydantic 模型集成
- 其他 Agent 框架的 Python 参考实现

MCP 支持：WrenAI 作为 MCP 工具接入任意支持 MCP 的 Agent。

---

## 为什么值得关注

Text-to-SQL 是一个被严重低估了工程复杂度的问题。表面上的问题是「怎么让模型写出正确的 SQL」，但背后的真正问题是「模型怎么知道你的业务语义」。

Schema 里没有「这个表只有当 `status = completed` 时才算有效数据」，没有「这两个表的 join 必须走 customer_type = B2B 的 filter」，没有「Q3 在我们公司是 7-9 月不是 7-9 月财年」——这些是活在业务人员头脑里的隐性知识。

WrenAI 的核心贡献是把「上下文层」做成一个可管理的基础设施层，而不是分散在每个 prompt 里的临时修复。MDL + instructions.md + 记忆索引，全部开放可读、版本控制、可迁移。

16921 stars，2024 年 3 月开源，持续活跃（今日仍有 push）。

仓库：[github.com/Canner/WrenAI](https://github.com/Canner/WrenAI)  
文档：[docs.getwren.ai](https://docs.getwren.ai)  
网站：[getwren.ai](https://getwren.ai)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## WrenAI: Open-Source GenBI Engine — Governed Text-to-SQL and Agent-Deployed Dashboards

*by Mycelium Protocol*

Text-to-SQL projects have a common failure mode: the SQL looks reasonable but the results are wrong. Not because the model is incapable — because the model doesn't know your business. It doesn't know which field counts as "revenue," which joins are approved, or what an enum value maps to in your database. None of that is in the schema. The model guesses.

**[WrenAI](https://github.com/Canner/WrenAI)** (Canner) puts an open context layer between the agent and the database: business knowledge made explicit, version-controlled, and Git-friendly — so agents can generate governed SQL and deploy shareable dashboards, not just plausible guesses. 16,921 stars, Apache 2.0, active development since March 2024.

### Three Beats: Generate · Deploy · Know

**Generate** — natural language → governed SQL + charts. Schema-aware retrieval, MDL planning, dry-plan validation, and structured errors with hints keep output correct rather than confidently wrong.

**Deploy** — any answer becomes a shareable, browser-side interactive dashboard powered by `wren-core-wasm`, shipped to your own Vercel or Cloudflare Pages account with one command.

**Know** — what makes everything correct lives in versionable, evidence-linked files: semantic models (MDL), company definitions (`instructions.md`), and a LanceDB memory index of past successful queries. Reviewable. Git-friendly. Never locked in a vendor UI.

### The Context Layer

**MDL (Modeling Definition Language)** defines models, columns, relationships, views, cubes, metrics, and row-/column-level access control — not just schema, but the business logic that makes queries correct:

```yaml
columns:
  - name: revenue
    expression: "CASE WHEN status = 'completed' THEN amount ELSE 0 END"
    description: "Valid sales revenue, completed orders only"
```

**`instructions.md`** captures the knowledge that lives outside the database: approved join logic, enum mappings, unit conventions, fiscal year definitions — everything schema doesn't carry, written explicitly instead of scattered across prompts.

**LanceDB memory** (hybrid retrieval): past successful queries stored in `queries.yml` and indexed locally. Similar questions recall relevant history rather than starting from zero.

### Engine: Rust + Apache DataFusion, 22+ Data Sources

```
core/wren-core/        Rust semantic engine (Apache DataFusion)
core/wren-core-wasm/   WebAssembly build for browser-side GenBI
core/wren/             Python SDK + CLI (PyPI: wrenai)
sdk/wren-langchain/    LangChain / LangGraph integration
```

Data sources: **BigQuery, Snowflake, PostgreSQL, ClickHouse, Amazon Redshift, Databricks, DuckDB** (bundled), MySQL, MS SQL Server, Oracle, Athena, Trino, Presto, Hive, and more via community connectors.

### Quickstart (Agent-Driven)

```bash
# Install
pip install "wrenai[postgres,memory]"

# Install skill stub for your agent (Claude Code, Cursor, Cline, Codex…)
npx skills add Canner/WrenAI

# Then tell your agent:
# "Use Wren to set up my Postgres database."
# Agent runs: wren skills get onboarding → connects, scaffolds project, runs first query

# Enrich with business context:
# "Enrich my Wren project with the docs in raw/"
# Agent runs: wren skills get enrich-context → writes MDL, instructions, memory

# Deploy a dashboard:
# "Turn this into a shareable dashboard and deploy to Vercel."
# Agent runs: wren skills get genbi → builds, previews, ships live URL
```

### Correctness Primitives

| Mechanism | What it prevents |
|-----------|-----------------|
| MDL planning | SQL planned at the semantic layer, not guessed at raw schema |
| Dry-plan validation | Structure validated before execution |
| Schema-aware retrieval | Precise table/column lookup per question |
| Structured errors + hints | Agent self-corrects on failure |
| Value profiling | Catches enum value mismatches before they reach results |
| Eval runner | Continuous quality regression for queries |

### Why This Matters

The real problem in text-to-SQL isn't model capability — it's context. Business semantics live in analysts' heads, not database schemas: which records count, which joins are safe, what a fiscal quarter means in your organization. Every text-to-SQL tool without a context layer is prompting the model to guess.

WrenAI's contribution is treating the context layer as a manageable infrastructure layer rather than a collection of prompt patches. MDL + instructions + memory: open, reviewable, version-controlled, portable to every agent you already run.

16,921 stars, Apache 2.0, consistently active (pushed today).

Repository: [github.com/Canner/WrenAI](https://github.com/Canner/WrenAI) · Docs: [docs.getwren.ai](https://docs.getwren.ai) · Site: [getwren.ai](https://getwren.ai)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
