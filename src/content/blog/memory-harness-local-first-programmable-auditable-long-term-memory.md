---
title: "Memory Harness：本地优先、可编排、可审计的 AI 长期记忆工作台"
titleEn: "Memory Harness: Local-First, Programmable & Auditable Long-Term Memory for AI Agents"
description: "luoyif/memory-harness 开源，六层可追溯记忆架构（Evidence→能力资产），本地混合 RAG，24 个 MCP 工具，多 AI 协作但草稿彼此隔离，完全本地无云依赖。"
descriptionEn: "luoyif/memory-harness open-sources a six-layer auditable memory workspace (Evidence → Agent Asset), local hybrid RAG, 24 MCP tools, multi-AI collaboration with isolated drafts — all fully local, no cloud dependency."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["AI memory", "MCP", "local-first", "RAG", "agents", "open source", "long-term memory", "knowledge management"]
heroImage: "../../assets/images/memory-harness-local-first-programmable-auditable-long-term-memory-banner.jpg"
author: "Mycelium Protocol"
---

## AI 的记忆问题一直没有被认真解决

每次对话结束，上下文就消失了。聊天记录越堆越长，却很难回答"这条结论从哪来、现在还有效吗、哪个 AI 看过它"。RAG 做了部分弥补，但大多数实现把"原始对话"和"提炼结论"混在一起，来源不可追溯，有效期无法区分，多个 AI 共用一个索引也没有权限边界。

**Memory Harness**（luoyif/memory-harness）是今天开源的一个本地优先长期记忆工作台，试图正面解决这个问题。它的核心主张只有一句话：**记忆不是黑盒，每层都能回到来源。**

---

## 六层可追溯记忆架构

Memory Harness 把"从原材料到可复用能力"的完整链路拆成六层，每层都保持来源链接：

```
Evidence（原材料，不可变）
  ↓
Knowledge Unit（从 Evidence 提取的知识单元）
  ↓
Episode（情节记录，跨 Evidence 的事件脉络）
  ↓
Memory（沉淀后的长期记忆）
  ↓
Living Knowledge（持续有效的知识产品）
  ↓
Agent Asset（可复用能力资产）
```

**关键设计**：原材料（Evidence）永远不被改写，所有派生结果可以从来源重建。这意味着当你几个月后回头看一条"记忆"时，你能看到它是从哪些对话、文件、AI 建议里沉淀出来的。

---

## 混合 RAG，完全本地无依赖

2.2.0 的检索引擎是可离线运行的混合 RAG，四层融合：

1. **英文/代码**：SQLite FTS5 `unicode61` BM25
2. **中文**：FTS5 trigram BM25
3. **本地嵌入**：384 维 `local-feature-hash-v1`，无需下载模型，不调外部服务
4. **RRF 融合**：关键词 + 嵌入相似度 + 时间相关性 + 新近度，综合排序

返回结果包含项目来源、时间戳、评分和可精确读取的 Evidence 标识。没有独立向量数据库，没有云端 Embedding API，SQLite + JSONL + FTS 全在本地设备。

---

## 多 AI 协作，但草稿彼此隔离

这是 Memory Harness 设计里最值得注意的部分：

- 每个 Agent（Codex、ChatGPT、Claude 等）有**独立身份、项目授权和最小权限**
- AI 的行动项先进入**建议区**，必须由用户确认才能执行
- 私密草稿彼此隔离，只有主动提交的内容才会共享
- 受保护内容必须由 Owner 审核才能写入

支持混合协议：OpenAI Responses、OpenAI-compatible Chat Completions、Anthropic Messages、OpenCode Go，可以同时接入多个不同厂商的模型。

---

## 24 个 MCP 工具，可编程记忆流程

Memory Harness 通过 `memoryosd` 伴侣程序暴露 **24 个受权限控制的 MCP 工具**，让 AI Coding Agent 可以直接读写记忆空间，并记录完整审计日志。

除此之外，它的记忆处理流程本身是可 DIY 的：

- **Blueprint**：整套记忆方案可替换（内置主流方案开箱即用）
- **Pipeline**：自定义导入、提取、验证、写入步骤
- Dry Run 后发布不可变版本，流程变更有记录

---

## 快速上手

### 下载（v2.2.0 Public Preview）

```bash
# macOS
Memory-Harness-2.2.0-macos-universal.zip

# Windows x64
Memory-Harness-2.2.0-windows-x64.zip

# Linux x64 无界面服务器
Memory-Harness-2.2.0-linux-x64.tar.gz

# Linux ARM64
Memory-Harness-2.2.0-linux-arm64.tar.gz
```

### 首次使用五步走

```
1. 在"记忆总览"新建记忆空间
2. 导入一份对话（支持 ChatGPT、Claude、DeepSeek 导出格式）或文件
3. 处理新增原材料（只跑新增/失败的，不会隐式全量重跑）
4. 在"待我审核"确认 AI 建议
5. 在"检索"里搜索并点开来源
```

### Linux 服务器部署

```bash
# 解压后
sudo ./install.sh
./healthcheck.sh
# 默认监听 127.0.0.1:19777，不直接暴露公网
```

---

## 适合谁用

**个人知识工作者**：把每天读到的文章、AI 对话、自己的思考沉淀成可追溯的长期记忆，而不是堆在聊天记录里。

**AI Agent 开发者**：通过 MCP 工具让 Agent 有持久记忆，同时保持权限边界和审计链路，防止不同 Agent 的数据互相污染。

**对数据隐私要求高的团队**：完全本地，没有云端依赖，适合医疗、法律、金融等场景。私有化部署只需一个 Linux 服务器。

**重度 Claude Code / Codex 用户**：Memory Harness 的多 AI 协作架构天然契合"多个 Coding Agent 共用一个项目记忆"的使用场景，同时 AI 的建议必须经过人工确认才能执行。

---

## 总结

Memory Harness 的核心是一个朴素但重要的判断：AI 记忆需要可审计、可追溯、有权限边界，而不是一个大的向量索引黑盒。六层架构 + 本地混合 RAG + MCP 工具链 + 多 AI 权限隔离，是目前开源方案里把这几件事同时做到的少数选择之一。

**GitHub**: [luoyif/memory-harness](https://github.com/luoyif/memory-harness)  
**文档**: [中文使用手册](https://github.com/luoyif/memory-harness/blob/main/docs/USER_GUIDE.zh-CN.md) · [MCP 接入](https://github.com/luoyif/memory-harness/blob/main/docs/MCP.md)

<!--EN-->

## Memory Harness: Local-First, Programmable & Auditable Long-Term Memory

AI memory has never been properly solved. Every conversation ends, context vanishes, and logs pile up with no way to answer: where did this conclusion come from? Is it still valid? Which AI has seen it?

**Memory Harness** (luoyif/memory-harness) is a newly open-sourced local-first long-term memory workspace that takes this problem head-on. Its core premise: **memory is not a black box — every layer traces back to its source.**

### Six-Layer Auditable Memory Architecture

Memory Harness decomposes the full chain from raw material to reusable capability into six traceable layers:

```
Evidence (immutable raw material)
  ↓
Knowledge Unit (extracted from Evidence)
  ↓
Episode (event timeline across Evidence)
  ↓
Memory (distilled long-term memory)
  ↓
Living Knowledge (actively maintained knowledge product)
  ↓
Agent Asset (reusable capability asset)
```

Evidence is never rewritten — all derived results can be rebuilt from source. When you revisit a "memory" months later, you can see exactly which conversations, files, and AI suggestions it was distilled from.

### Local Hybrid RAG, Zero Cloud Dependencies

The 2.2.0 retrieval engine is a fully offline hybrid RAG with four-layer fusion:

1. **English/code**: SQLite FTS5 `unicode61` BM25
2. **Chinese**: FTS5 trigram BM25
3. **Local embeddings**: 384-dim `local-feature-hash-v1`, no model download, no external API calls
4. **RRF fusion**: keyword + embedding similarity + temporal relevance + recency

Results include project source, timestamp, score, and a precise Evidence identifier. No separate vector database, no cloud Embedding API — SQLite + JSONL + FTS entirely on-device.

### Multi-AI Collaboration with Isolated Drafts

Each Agent (Codex, ChatGPT, Claude, etc.) gets an **independent identity, project authorization, and minimum permissions**. AI action items land in a **suggestion queue** — they cannot execute without user confirmation. Private drafts are isolated across agents; only explicitly submitted content is shared. This prevents one AI's changes from silently polluting another's data.

Supports mixed protocols: OpenAI Responses, OpenAI-compatible Chat Completions, Anthropic Messages, OpenCode Go.

### 24 MCP Tools, Programmable Memory Pipelines

The `memoryosd` companion exposes **24 permission-controlled MCP tools** letting AI Coding Agents read/write memory spaces with full audit logging. The memory processing pipeline is itself DIY-able via **Blueprints** and **Pipelines** — import, extract, validate, and write steps are all customizable, with Dry Run before publishing an immutable version.

### Who It's For

- **Personal knowledge workers**: Distill daily reading, AI conversations, and your own thinking into traceable long-term memory rather than chat history
- **AI Agent developers**: Give agents persistent memory via MCP while maintaining permission boundaries and audit trails
- **Privacy-sensitive teams**: Fully local, no cloud dependency — healthcare, legal, finance; single Linux server for self-hosted deployment
- **Heavy Claude Code / Codex users**: Multi-AI architecture fits "multiple Coding Agents sharing a project memory" naturally, with AI suggestions always requiring human confirmation before execution

### Getting Started

```bash
# macOS: download Memory-Harness-2.2.0-macos-universal.zip
# Windows: Memory-Harness-2.2.0-windows-x64.zip
# Linux x64: Memory-Harness-2.2.0-linux-x64.tar.gz

# Linux server deploy
sudo ./install.sh
./healthcheck.sh  # listens on 127.0.0.1:19777
```

Five steps: create a memory space → import a conversation or file → process new materials → confirm AI suggestions → search with source links.

Memory Harness makes a simple but important bet: AI memory needs auditability, traceability, and permission boundaries — not a large vector index black box. The six-layer architecture, local hybrid RAG, MCP toolchain, and multi-AI permission isolation make it one of the few open-source options that addresses all of these simultaneously.

**GitHub**: [luoyif/memory-harness](https://github.com/luoyif/memory-harness)  
**Docs**: [User Guide (ZH)](https://github.com/luoyif/memory-harness/blob/main/docs/USER_GUIDE.zh-CN.md) · [MCP Setup](https://github.com/luoyif/memory-harness/blob/main/docs/MCP.md)
