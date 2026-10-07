---
title: "Leviathan：让 Agent 在百万行数据集里只花 436 个 token 找到答案"
titleEn: "Leviathan: Agent Deep Memory Over Large Datasets — 436 Tokens at 1M Records"
description: "elstongun/leviathan，Apache-2.0，Rust，656 stars，3 天冲到。单静态二进制 2.5MB，无运行时依赖，把 JSONL/JSON/CSV/SQLite/数据库 CLI 输出建成排序全文索引。核心测试：1M 条记录（678MB），Agent 每次问答中位 token 消耗 436，vs. 最优 grep 策略 107,122（245 倍差距）；99.0% top-5 召回率；中位延迟 33ms。内置 MCP Server（4 个只读工具：search/resolve_group/get/describe），配套 SKILL.md，支持 Claude Code/Codex/Cursor/VSCode 等 Agent 直接调用。"
descriptionEn: "elstongun/leviathan, Apache-2.0, Rust, 656 stars in 3 days. Single static binary at 2.5MB, no runtime dependencies, indexes JSONL/JSON/CSV/TSV/SQLite/database CLI output into a ranked full-text index. Core benchmark at 1M records (678MB): median 436 tokens per agent question vs. 107,122 for the best grep strategy (245× less); 99.0% top-5 relevant record return; median 33ms latency. Built-in MCP server (4 read-only tools: search/resolve_group/get/describe) with SKILL.md for Claude Code/Codex/Cursor/VSCode."
pubDate: 2026-10-07
heroImage: "../../assets/images/leviathan-rust-agent-memory-large-datasets-fts5-single-binary-banner.jpg"
category: "Tech-Experiment"
tags: ["AI Agent", "RAG", "开发工具", "Rust", "MCP", "本地工具"]
lang: "zh-CN"
wechatTitle: "Leviathan：大数据集Agent深度记忆引擎"
wechatDigest: "Apache-2.0；Rust单二进制2.5MB；1M记录仅436 token；33ms；FTS5；MCP"
---

Agent 遇到大型历史数据集时有一个经典困境：直接把所有记录塞进上下文撑爆 token，还是靠 grep 找关键词但不知道找多少才够？

Leviathan 给出了一个不同的答案：**本地建索引，Agent 查询时只返回相关的几条记录卡片，token 控制在几百以内，不管数据集多大。**

GitHub: https://github.com/elstongun/leviathan | ⭐ 656 | Apache-2.0 | Rust

---

## 核心基准（1M 条记录，678MB）

作者提供了一个具体的性能数字，场景是合成的维护日志（一类典型的 Agent 历史数据），数据集规模从 1K 到 1M 条。

| 指标 | Leviathan | 最优 grep 策略 |
|------|-----------|---------------|
| 中位 token 消耗 | **436** | 107,122（差 245×） |
| 最差情况（1200 次问答） | **602 tokens** | 9,700,000 tokens |
| top-5 相关记录召回率 | **99.0%** | 96.0%（30K 字符输出内） |
| rank 1 准确率 | **98.5%** | — |
| 中位延迟 | **33ms** | 92ms |

**需要注意**：这是合成数据集上的结果，作者在文档里明确说明这不是标准 benchmark，测试方法见 `docs/BENCHMARKS.md`，ranking 改动需要附带前后对比数字才能被 merge。

---

## 怎么工作

底层是 **SQLite + FTS5 全文索引 + BM25 排序**。

一次查询的流程：

1. 解析 group 参数（精确匹配 → 名称 → 包含 → 模糊）
2. FTS5 匹配：group 值和 filter 值作为 token 被索引进去（不是查完再过滤），匹配更精确
3. BM25 × boost 排序
4. 只解码 top N 条，输出包含 `shown N of M` 的卡片

Agent 拿到的结果类似：

```text
leviathan search · customer C-ACME "Acme Corp" (7 tickets) · 查询 "sso 登录密码重置后跳回登录页"
[1] T-1001 · 2024-01-08 · rel 16.9
  密码重置后登录页无限循环
  状态: 已关闭 · 优先级: 高
  解决方案: 密码重置时清除了旧 session cookie，已发布在 4.2.1。临时方案：清除站点数据。
```

每张卡片大约 450 tokens，不管数据集是 1K 还是 1M 条。

---

## 数据源支持和配置

Leviathan 本身不持有数据库凭据，通过各数据库自己的 CLI 接入：

```bash
# CSV / JSONL 直接索引
leviathan index tickets.csv --id "Ticket ID" --group customer_id --date created_at

# PostgreSQL
psql "$DATABASE_URL" -At -c "SELECT row_to_json(t) FROM tickets t" | leviathan index - -c tickets.toml

# SQLite
leviathan index app.db --sql "SELECT * FROM tickets" -c tickets.toml

# DuckDB / Parquet
duckdb -json -c "SELECT * FROM 'events/*.parquet'" | leviathan index - -c events.toml
```

支持的格式：JSONL、JSON、CSV/TSV、SQLite、任意数据库 CLI 的 JSON 输出。

字段映射（`leviathan.toml`）：

| 字段 | 作用 |
|------|------|
| `id` | 必填，用于 `get`/`upsert`/`delete` 和引用 |
| `title`/`text` | 卡片标题（权重 2×）/ 被搜索的文本 |
| `group`/`group_name` | `-g` 范围搜索和名称解析 |
| `date` | `--since`/`--until` 时间过滤 |
| `filters`/`display` | `--where` facet 过滤 / 卡片展示字段 |

---

## Agent 接入方式

**CLI + Skill（推荐）**：把 `skills/leviathan/SKILL.md` 复制到 `~/.claude/skills/` 或粘贴进 `AGENTS.md`。不用的时候 0 token，用到时再加载。

**MCP Server**：4 个只读 stdio 工具：

| 工具 | 作用 |
|------|------|
| `search` | 排序全文检索（支持 group/filter/时间范围） |
| `resolve_group` | 解析模糊 group 名称到精确 ID |
| `get` | 通过 ID 获取完整记录 |
| `describe` | 返回数据集摘要（字段/group 列表/示例调用，~640 tokens） |

启动 MCP 服务器并生成对应 Agent 的配置：

```bash
leviathan mcp
leviathan wrap claude     # 生成 Claude Code 配置
leviathan wrap codex      # 生成 Codex 配置
leviathan wrap cursor     # 生成 Cursor 配置
```

---

## 一个实际场景：客服工单记忆

Agent 需要回答「某个客户之前报过什么 bug？」这类问题。传统做法：grep 关键词 → 把命中的几百条原始记录全塞进上下文，平均 10 万+ token。

Leviathan 做法：建索引 → 每次查询返回 3–5 张排好序的卡片 → 不超过 600 tokens，99% 的情况下 rank 1 就是答案。

---

## 工程细节

- **单静态二进制，2.5MB**：`cargo install leviathan-index` 或下载预编译包，无运行时依赖
- **索引是单个 SQLite 文件**：便携，可以 git 追踪或随数据集分发
- **增量更新**：`upsert`/`delete` 保持索引新鲜，内容未变化时跳过重建
- **原子构建**：构建是原子操作，不会出现中间状态
- **Exit code 规范**：0 ok（零结果也是 0）；1 error；2 bad request；3 group 不明确——Agent 可靠判断
- **安全**：只读，离线，无 `unsafe` 代码

---

## 已知边界

- 这是 v0.1.0，3 天前刚发，中文社区暂无实测记录
- Benchmark 基于单一合成数据集（维护日志）——真实场景的泛化能力需要自己验证
- FTS5 是词项匹配，语义相似（embedding 检索）不在这个工具的覆盖范围

---

> Apache-2.0 开源。elstongun 维护，Rust 单二进制，3 天 656 stars。开源仅供学习参考。

---

<!--EN-->

## Leviathan: Agent Deep Memory Over Large Datasets — 436 Tokens at 1M Records

Agents working over large historical datasets face a classic dilemma: stuff everything into context (expensive) or grep for keywords (noisy and token-heavy). Leviathan takes a different approach: build a local full-text index once, and return only ranked result cards at query time — a few hundred tokens regardless of dataset size.

GitHub: https://github.com/elstongun/leviathan | ⭐ 656 | Apache-2.0 | Rust

---

### Core Benchmark (1M records, 678MB)

Tested on a synthetic maintenance log. Dataset scaled from 1K to 1M records.

| Metric | Leviathan | Best grep strategy |
|--------|-----------|-------------------|
| Median tokens/question | **436** | 107,122 (245× more) |
| Worst case (1,200 questions) | **602 tokens** | 9,700,000 tokens |
| Top-5 relevant record return | **99.0%** | 96.0% (within 30K chars) |
| Rank 1 accuracy | **98.5%** | — |
| Median latency | **33ms** | 92ms |

**Caveat**: single synthetic dataset; methodology in `docs/BENCHMARKS.md`; ranking PRs require before/after benchmark numbers.

---

### How It Works

SQLite + FTS5 + BM25 × boost ranking. A query: resolve group → FTS5 match (group/filter values are indexed tokens, not post-filters) → rank → decode top N into capped cards (~450 tokens each). Every response includes `shown N of M` so agents can distinguish "no match" from "no data."

---

### Data Sources

No credentials held by Leviathan — pipe from any database CLI:

```bash
leviathan index tickets.csv --id "Ticket ID" --group customer_id --date created_at
psql "$DATABASE_URL" -At -c "SELECT row_to_json(t) FROM tickets t" | leviathan index -
leviathan index app.db --sql "SELECT * FROM tickets" -c tickets.toml
duckdb -json -c "SELECT * FROM 'events/*.parquet'" | leviathan index -
```

---

### Agent Integration

**Recommended: CLI + SKILL.md** — copy `skills/leviathan/SKILL.md` into `~/.claude/skills/`. Zero tokens until invoked.

**Optional: MCP server** — 4 read-only stdio tools (search, resolve_group, get, describe). `leviathan wrap claude|codex|cursor|...` generates agent config.

---

### Engineering Notes

- Single static binary, 2.5MB, no runtime dependencies
- Index is a single portable SQLite file
- Incremental updates via `upsert`/`delete`; skips rebuild when nothing changed
- Atomic index builds; no intermediate states
- Deterministic exit codes (0/1/2/3) for reliable agent parsing
- Read-only, offline, zero `unsafe` code

---

### Boundaries

- v0.1.0 released 2026-10-06; no real-world validation beyond the synthetic benchmark yet
- FTS5 is term-based; semantic/embedding search is out of scope
- Group resolution fails loudly (exit 3) rather than silently guessing — correct for agent use, requires explicit handling

---

> Apache-2.0. Maintained by elstongun. Single Rust binary, 656 stars in 3 days. For technical reference only.
