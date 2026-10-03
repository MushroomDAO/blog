---
title: "LWC 拆解：Rust + SQLite，Agent 跨会话越用越懂项目的持久记忆层"
titleEn: "LWC Teardown: Rust + SQLite Persistent Wiki Memory Layer That Lets Agents Learn Your Project Over Time"
description: "JanYork/llm-wiki-cli（LWC），Apache-2.0，Rust + SQLite，v0.19.3。Agent 自驱的持久 Wiki 记忆 CLI：不检索向量、不调 LLM，只用 SQLite 存源→页面→引用→历史结构，让 AI 跨会话积累项目知识而非每次从零翻文档。内置 MCP 服务器，兼容 Claude Code/Codex/Cursor 等主流 Agent；团队空间通过自托管服务器同步。"
descriptionEn: "JanYork/llm-wiki-cli (LWC), Apache-2.0, Rust + SQLite, v0.19.3. An agent-driven persistent Wiki memory CLI: no vector retrieval, no LLM calls in the memory layer — just SQLite storing source→page→citation→history, letting AI agents compound project knowledge across sessions rather than rediscovering it each time. Built-in MCP server; compatible with Claude Code, Codex, Cursor, and other major agents; team spaces via self-hosted server."
pubDate: 2026-10-03
heroImage: "../../assets/images/lwc-llm-wiki-cli-rust-sqlite-agent-memory-persistent-wiki-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent记忆", "Wiki", "Rust", "SQLite", "MCP", "持久化", "开源拆解"]
lang: "zh-CN"
wechatTitle: "LWC：Rust+SQLite，Agent跨会话持久记忆层"
wechatDigest: "Apache-2.0；不用向量/不调LLM；源→页面→引用→历史；MCP接入；Claude Code兼容"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题在哪里

AI Agent 有一个结构性缺陷：每次会话都是从零开始的。你上周让它分析了某个模块，这周再来，它什么都不记得。除非你手动粘贴上下文，否则它每次都要重新翻同样的文档。

现有的解法主要是两种：

1. **RAG（检索增强生成）**：把文档切成 chunk，存向量库，每次查询时检索相关片段。问题是：检索的是"原始块"，而不是"整理过的理解"；每次查询代价高，且不累积。

2. **让 LLM 维护 Markdown 文件**：Karpathy 的 LLM Wiki 概念——每加一份文档，让 LLM 增量更新摘要页、概念页、实体页、索引和日志。问题是：调用 LLM 本身有成本，且实现复杂。

LWC 走了第三条路：**不检索向量，不调 LLM，只用 SQLite 把知识存成结构化的 Wiki**，让 Agent 自己读写、自己维护。

**仓库**：github.com/JanYork/llm-wiki-cli  
**协议**：Apache-2.0  
**语言**：Rust  
**版本**：v0.19.3  
**安装**：`npm install -g @i-xor/lwc`（也可从 crates.io 安装 `lwc`）

---

## 核心设计：不是 RAG，是 Wiki

LWC 实现了一个简单但关键的模型转换：

| 方式 | 每次行为 | 积累效果 |
|------|----------|---------|
| RAG | 从原始文档检索 chunk | 不积累，每次从零找 |
| LWC | Agent 读已整理好的 Wiki | 积累，越用越精准 |

**存储结构**（SQLite + Markdown 文件）：

```
源文档（source）
  └─ 页面（page）
       ├─ 引用（citation）
       ├─ 链接（link）
       ├─ 索引（index）
       └─ 历史（history）
```

每条知识都能溯源——来自哪个文档、哪段原文、什么时候更新的。不是"模糊记忆"，是"带出处的知识图"。

**关键特性**：Agent 不是被动检索，而是**主动维护**这个 Wiki。它读之前的 Wiki、推理、写回验证过的知识。下一次会话时，知识已经在那里了。

---

## 与 Karpathy LLM Wiki 的关系

Karpathy 2026 年 4 月发布的 llm-wiki gist（5000+ stars）描述了这个范式：用 LLM 增量维护一个持久 Wiki，而不是每次从原始文档重头查。

LWC 是这个概念的 **Rust + SQLite 工程化版本**，和之前已有的 Node.js 版本（doum1004/llmwiki-cli）是不同的实现路线：

| 维度 | doum1004/llmwiki-cli | JanYork/LWC |
|------|---------------------|-------------|
| 语言 | Node.js / npm | Rust |
| 存储 | 文件系统 | SQLite |
| 记忆机制 | LLM 驱动更新 Wiki 文件 | Agent 自主读写 SQLite |
| 团队协作 | 无 | 团队空间 + 自托管服务器 |
| MCP 支持 | 无 | 内置 MCP 服务器 |
| 安装 | npm | npm 或 cargo |

---

## 内置 Skill 和 MCP

LWC 附带 `using-lwc` Skill，这是关键的工程决策——记忆层本身是工具，但如何让 Agent 正确使用这个工具，需要专门的 Skill 定义。

`using-lwc` Skill 的作用：
- 让 Agent 以"有界上下文"模式召回知识（不加载全部 Wiki）
- 区分项目知识和全局知识
- 整合来源，保留引用
- 只写回**经过验证、值得复用**的知识（过滤噪声）

MCP 服务器内置，可以直接通过 MCP 协议接入：

```json
{
  "mcpServers": {
    "lwc": {
      "command": "lwc",
      "args": ["serve", "--mcp"]
    }
  }
}
```

---

## 兼容的 Agent 工具

LWC 可以接入的 Agent 环境：

- Claude Code / Codex
- Cursor / Kiro
- OpenCode
- Gemini CLI
- GitHub Copilot（VS Code / JetBrains / CLI）
- Hermes / Antigravity
- pi

几乎覆盖了目前主流的 AI 编程助手生态。

---

## 团队空间（Team Spaces）

LWC 不只是个人工具。团队空间功能让多人共享同一个持久 Wiki：

- 核心记忆存在本地 SQLite + Wiki 文件中
- 通过自托管服务器同步团队成员之间的知识
- 每个成员的 Agent 都能从共享 Wiki 中读取，写回更新

这是 RAG 方案很难做到的：向量库更新代价高，语义变化难以增量追踪；LWC 的 SQLite 结构增量更新天然友好。

---

## 需要知道的限制

**完全依赖 Agent 主动写入**。Wiki 的质量取决于 Agent 有没有正确执行 `using-lwc` Skill，如果 Agent 不回写或回写错误知识，Wiki 会退化。

**没有向量搜索**。LWC 的查询是基于结构化索引，不支持语义搜索——如果你需要"找和这段代码语义类似的内容"，LWC 不适合。

**团队同步依赖自托管服务器**。没有现成的云端托管方案，需要自行搭建同步服务。

**v0.19.3 仍在快速迭代**。API 可能变化，大版本升级前注意兼容性。

**Apache-2.0 协议**，商用无限制。

---

## 关键数字

| 字段 | 值 |
|------|----|
| 仓库 | JanYork/llm-wiki-cli |
| 版本 | v0.19.3 |
| 语言 | Rust |
| 存储 | SQLite |
| License | Apache-2.0 |
| 安装方式 | npm (`@i-xor/lwc`) 或 cargo (`lwc`) |
| MCP 支持 | ✅ 内置 |
| 团队空间 | ✅ 自托管同步 |
| 兼容 Agent | 10+ 主流工具 |

---

## 综合判断

LWC 切入的是 Agent 记忆问题的一个具体角度：不是所有场景都需要向量检索，很多"项目知识"其实是结构化的——模块职责、接口约定、历史决策——这类知识用关系型存储（SQLite）比向量库更自然，更容易追溯来源。

"不调 LLM，只用 SQLite"的决策是有代价的：知识更新完全依赖 Agent 的主动写入，质量上限取决于 Agent 的判断能力。但代价也是优势——轻量、无 token 成本、随时离线可用。

内置 Skill 和 MCP 服务器说明这不是一个"原型项目"——它在认真对待 Agent 集成工作流。v0.19.3 的版本迭代速度也表明作者在持续推进。

适合的场景：长期维护同一个代码库、需要 Agent 积累项目特定知识、不想每次都重新解释同样的架构决定。

---

> 开源仅供学习，Apache-2.0 协议，商业使用无限制。

---

<!--EN-->

## LWC Teardown: Rust + SQLite Persistent Wiki Memory for AI Agents

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem

AI agents have a structural limitation: every session starts from zero. You had it analyze a module last week — this week, it remembers nothing. Unless you manually paste context, it rediscovers the same documents every time.

Current solutions fall into two camps:

1. **RAG (Retrieval-Augmented Generation)**: Chunk documents into vectors, retrieve relevant pieces per query. Problem: you're retrieving raw chunks, not organized understanding. Every query is expensive. Nothing accumulates.

2. **LLM-maintained Markdown files**: Karpathy's LLM Wiki concept — every time a document is added, an LLM incrementally updates summary, concept, entity, index, and log pages. Problem: LLM calls cost tokens, and implementation is complex.

LWC takes a third path: **no vector retrieval, no LLM calls in the memory layer — just SQLite storing structured knowledge**, with the agent reading and writing it directly.

**Repo**: github.com/JanYork/llm-wiki-cli  
**License**: Apache-2.0  
**Language**: Rust  
**Version**: v0.19.3  
**Install**: `npm install -g @i-xor/lwc` (or `cargo install lwc`)

---

### Core Design: Wiki, Not RAG

LWC implements a simple but important model shift:

| Approach | Per-session behavior | Accumulation |
|----------|---------------------|--------------|
| RAG | Retrieves from raw document chunks | Doesn't accumulate — rediscovers each time |
| LWC | Agent reads the already-organized Wiki | Accumulates — gets better with use |

**Storage structure** (SQLite + Markdown files):

```
source document
  └─ page
       ├─ citation
       ├─ link
       ├─ index
       └─ history
```

Every piece of knowledge is traceable — which document it came from, which passage, when it was last updated. Not "fuzzy memory" — a knowledge graph with provenance.

**Key behavioral difference**: Agents aren't passively retrieving — they're **actively maintaining** this Wiki. They read prior Wiki state, reason about it, write back verified knowledge. Next session, the knowledge is already there.

---

### Relationship to Karpathy's LLM Wiki

Karpathy's April 2026 llm-wiki gist (5,000+ stars) described this paradigm: use an LLM to incrementally maintain a persistent Wiki instead of re-querying raw documents each time.

LWC is the **Rust + SQLite engineering version** of this concept, distinct from the Node.js implementation (doum1004/llmwiki-cli):

| Dimension | doum1004/llmwiki-cli | JanYork/LWC |
|-----------|---------------------|-------------|
| Language | Node.js / npm | Rust |
| Storage | File system | SQLite |
| Memory mechanism | LLM-driven Wiki file updates | Agent-native SQLite read/write |
| Team collaboration | None | Team spaces + self-hosted server |
| MCP support | None | Built-in MCP server |
| Install | npm | npm or cargo |

---

### Built-in Skill and MCP

LWC ships a `using-lwc` Skill — a critical engineering decision. The memory layer is a tool, but how agents correctly use that tool requires a dedicated Skill definition.

The `using-lwc` Skill provides:
- Bounded context recall (doesn't load the full Wiki)
- Separation of project vs. global knowledge
- Source integration with citation preservation
- Writes back only **verified, reusable knowledge** (filters noise)

MCP server is built in:

```json
{
  "mcpServers": {
    "lwc": {
      "command": "lwc",
      "args": ["serve", "--mcp"]
    }
  }
}
```

---

### Agent Compatibility

LWC integrates with: Claude Code, Codex, Cursor, Kiro, OpenCode, Gemini CLI, GitHub Copilot (VS Code / JetBrains / CLI), Hermes, Antigravity, pi.

Coverage across the major AI coding assistant ecosystem.

---

### Team Spaces

LWC is also a team tool. Team Spaces let multiple people share a persistent Wiki:

- Core memory stays in local SQLite + Wiki files
- A self-hosted server synchronizes across team members
- Every member's agent reads from and writes to the shared Wiki

This is hard to do with RAG: vector stores are expensive to update, and semantic drift is difficult to track incrementally. LWC's SQLite structure handles incremental updates naturally.

---

### Limitations

**Entirely dependent on agent write-back.** Wiki quality depends on agents correctly executing the `using-lwc` Skill. If the agent doesn't write back or writes incorrect knowledge, the Wiki degrades.

**No semantic search.** LWC queries rely on structured indexing — it doesn't support "find content semantically similar to this snippet." For that use case, RAG is more appropriate.

**Team sync requires a self-hosted server.** No managed hosting option — you run your own sync infrastructure.

**v0.19.3 is still iterating rapidly.** API may change; check compatibility before major version upgrades.

**Apache-2.0 license** — commercial use unrestricted.

---

### Verdict

LWC targets a specific angle on the agent memory problem: not all knowledge needs vector retrieval. Much "project knowledge" is inherently structured — module responsibilities, interface contracts, historical decisions — and structured storage (SQLite) is more natural for this than vectors, with better provenance tracking.

"No LLM calls, just SQLite" comes with a tradeoff: knowledge quality depends entirely on the agent's judgment about what's worth writing back. But the tradeoff is also the advantage — lightweight, zero token cost, fully offline.

The bundled Skill and MCP server signal this isn't a prototype — it's taking agent integration seriously. v0.19.3 iteration speed confirms active development.

Best fit: long-term codebases where you want agents to accumulate project-specific knowledge without re-explaining the same architectural decisions session after session.

---

> Open source for learning only. Apache-2.0 license — commercial use unrestricted.
