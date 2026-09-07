---
title: "Utopia：开源企业世界模型，用双时态知识图谱让「知识如何演变」成为一等公民"
titleEn: "Utopia: Open-Source Enterprise World Model Using Bitemporal Knowledge Graphs to Make 'How Knowledge Changes' a First-Class Citizen"
description: "deeplethe/utopia 自称「世界首个开源企业世界模型」。一个 Rust 二进制 + Postgres，提供双时态知识图谱（两条时间线：事件发生时间 + 系统认知时间）、本体驱动推理、冲突检测、决策账本和 Ontology2SQL（BIRD benchmark SOTA），支持离线部署和 DeepSeek/Qwen/Ollama 等任意兼容 endpoint。"
descriptionEn: "deeplethe/utopia calls itself the world's first open-source enterprise world model. One Rust binary + Postgres delivers a bitemporal knowledge graph (two timelines: when things were true in the world + when the system came to believe them), ontology-driven reasoning, conflict detection, a decision ledger, and Ontology2SQL (BIRD benchmark SOTA) — deployable air-gapped with any OpenAI-compatible endpoint."
pubDate: 2026-09-07
updatedDate: 2026-09-07
category: Tech-Experiment
tags: ["AI", "知识图谱", "企业AI", "Rust", "RAG", "开源", "本体", "双时态", "Agent", "知识工程"]
heroImage: "../../assets/images/utopia-deeplethe-enterprise-world-model-bitemporal-knowledge-graph-banner.jpg"
author: "Mycelium Protocol"
---

大多数知识管理系统只关心一个问题：**现在知道什么？**

deeplethe/utopia 提出了一个不同的问题：**知识是怎么演变到现在这个样子的？**

这个问题的转变不只是哲学态度，它影响了整个系统的底层设计——从存储结构到推理方式到审计能力。

GitHub：[deeplethe/utopia](https://github.com/deeplethe/utopia)

---

## 一句话定位

Utopia 自称"世界首个开源企业世界模型"（World's first open-source enterprise world model），是 DeepLethe 构建的**知识治理基础设施**：

> "Where a knowledge graph or a vector store works to hold present knowledge, Utopia puts time awareness and ontology in the base layer."

向量存储和知识图谱解决"当前知识怎么存"的问题，Utopia 把**时间感知**和**本体**放在基础层——知识系统随材料到来自动演进，冲突检测、推理和决策都在这个本体之上运行。

官方特意说明：**这不是开源版 Palantir**，而是从知识治理向上构建企业智能，路径完全不同。

---

## 核心设计：双时态知识图谱

这是整个系统最重要的概念，值得仔细理解。

传统知识库只记录一条时间线：**当前认知**。一个事实被更新，旧版本就消失了。

Utopia 维护**两条时间线**：

| 时间线 | 含义 |
|--------|------|
| **Valid time** | 事件在现实世界中实际发生的时间（"什么时候是真的"） |
| **Transaction time** | 系统什么时候得知这个事实（"系统什么时候开始相信它"） |

举个例子：公司 A 在 2024 年 1 月收购了公司 B，但相关文件在 2024 年 3 月才被上传到系统。

- Valid time：2024-01-15（收购实际发生）
- Transaction time：2024-03-20（系统录入时间）

当一个决策在事后被审查，Utopia 可以**重现**：在那个决策时刻，系统实际上相信什么（基于 transaction time），以及现实世界当时是什么状态（基于 valid time）。这对合规审计、法律举证、决策回溯意义重大。

**修正事实不是覆盖**：修正一个错误事实会关闭旧版本并链接到新版本，旧版本保留在图谱里。没有 `DELETE`，只有 `CLOSE`。

---

## 技术栈：极简部署

Utopia 有一个强烈的工程主张：**最小化运维复杂度**。

```
一个 Rust 二进制
一个 Postgres（+ pgvector 扩展）
```

全文搜索内嵌于二进制（Tantivy），向量存在 pgvector，任务队列是数据库里的一张表。没有 Redis、没有独立的消息队列、没有专用向量数据库。

```bash
git clone https://github.com/deeplethe/utopia.git
cd utopia
docker compose --profile app up -d
# 打开 http://localhost:1516 注册
```

支持任意 OpenAI 兼容 endpoint：DeepSeek、Qwen、GLM、Ollama、vLLM——整个系统可以**完全离线运行**，无需接触外部 API。

---

## 六个核心能力

### 1. 知识摄取

支持格式：PDF、DOCX、PPTX、XLSX、XLS、ODS、CSV、TSV、Markdown、HTML、纯文本。

定时同步来源：网页、RSS、GitHub、Jira、Notion、WebDAV、S3 兼容存储桶。其他来源通过 API 接入。

### 2. 搜索与对话

Tantivy 全文检索 + pgvector 向量检索，通过 RRF（倒数排名融合）混合。答案流式输出，内联引用可点击打开原文段落。

### 3. Agent Harness 与 Agentic RAG

内置 Agent 可以搜索文档、遍历知识图谱（任意日期的实体事实，或特定时间段内的变化），并查询挂载的数据库。同样的只读工具**通过 MCP 暴露**，可以被外部 Agent 调用。

### 4. 本体与冷启动

新知识库没有自己的词汇体系，从你选择的本体包起步。系统内置五个：schema.org、W3C Org、PROV-O、FOAF 和 IOF Core。本体以外的术语会被计数，确认常见的就加入本体。

### 5. 实体消解与审查

三阶段消重：精确名称/别名匹配 → Embedding 相似度 → 模型判断可疑对。每次合并可撤销。低置信度提取、疑似重复和基数冲突进入审查队列。

### 6. 推理与导出

本体公理编译成规则：传递性、对称性、逆关系、关系层级通过前向链推导出新事实。导出事实带有来源标记，与已断言事实冲突时已断言的优先。

---

## Ontology2SQL：BIRD benchmark SOTA

Utopia 内置的 **Ontology2SQL** 方法——把数据库表挂载到知识本体上，通过自然语言对话查询——在 BIRD Mini-Dev（SQLite 和 PostgreSQL）上达到 SOTA，并已提交 leaderboard。

用法：把 Postgres、MySQL、Trino（支持 Iceberg/Delta Lake/Hive）、Databricks、Snowflake 挂载到某个知识库，Agent 提议表到本体的映射，确认后就可以用自然语言跨文档和数据库联合查询。

---

## 冲突检测：三种冲突，三套处理

Utopia 定义了三类知识冲突，并为每种提供了选择路径：

**新旧事实冲突**
- 关闭旧事实（新覆盖旧）
- 保留两个（存在分歧）
- 拒绝新事实

**公理违反**（自环、反对称、传递环、基数）
- 撤回事实
- 放宽公理
- 接受两者（容忍例外）

**本体自身矛盾**：先检查本体，因为违反自相矛盾本体的结果是噪声，不是知识。

---

## 决策账本

每个操作——确认/拒绝事实、合并/撤销实体、重建图谱——都留下一条记录：谁操作、什么时间、对象在那个时刻是什么状态。账本只追加，记录的生命周期比对象更长，甚至比对象所属的知识库更长。

---

## 路线图亮点

- **决策推理**：约束计算，事后重演决策
- **执行门**：对 Agent 调用进行本体规则和符号逻辑检查（相当于 Agent 的"安全护栏"）
- **Agent 记忆（MCP）**：情节写入、检索 endpoint、MCP server
- **更多连接器**：ClickHouse、飞书
- **企业功能**：OIDC SSO、备份恢复、10万文档规模基准

---

## 与常见方案的定位差异

| 维度 | 向量数据库（Milvus等） | 知识图谱（Neo4j等） | Utopia |
|------|---------------------|---------------------|--------|
| 时间感知 | 无 | 有限 | 双时态（两条时间线） |
| 推理能力 | 无 | 有（Cypher/SPARQL） | 本体公理 + 前向链 |
| 冲突检测 | 无 | 无 | 内置三类冲突处理 |
| 决策审计 | 无 | 无 | 决策账本（append-only） |
| 部署复杂度 | 高（独立服务） | 高 | 极低（1 binary + 1 Postgres） |
| 离线支持 | 部分 | 部分 | 完全支持 |

---

## 当前状态

v0.1，仍在早期阶段。Schema 在版本间会演进，迁移只前滚不回滚。生产环境建议 pin 特定版本（`UTOPIA_IMAGE`）并在升级前备份数据库和 `data` 目录。

Apache-2.0 开源许可。

---

## 相关链接

- GitHub：[deeplethe/utopia](https://github.com/deeplethe/utopia)
- 哲学文档：[utopia.bi/philosophy](https://utopia.bi/philosophy)
- Ontology2SQL：[deeplethe/ontology2sql](https://github.com/deeplethe/ontology2sql)

<!--EN-->

Most knowledge management systems answer one question: **What do we know right now?**

deeplethe/utopia asks a different question: **How did knowledge evolve to reach its current state?**

This shift isn't just philosophical — it changes the entire system's design, from storage structure to reasoning to audit capability.

GitHub: [deeplethe/utopia](https://github.com/deeplethe/utopia)

---

## One-Line Positioning

Utopia calls itself the "World's first open-source enterprise world model," built by DeepLethe as a **knowledge governance substrate**:

> "Where a knowledge graph or a vector store works to hold present knowledge, Utopia puts time awareness and ontology in the base layer."

Vector stores and knowledge graphs solve "how to store current knowledge." Utopia puts **time awareness** and **ontology** in the base layer — the knowledge system evolves as material arrives, and conflict detection, reasoning, and decision-making all run against that ontology.

The team explicitly notes: **this is not an open-source Palantir** — it's a different route to enterprise intelligence, built bottom-up from knowledge governance.

---

## Core Design: Bitemporal Knowledge Graph

The most important concept in the system.

Traditional knowledge bases maintain one timeline: **current belief**. When a fact is updated, the old version disappears.

Utopia maintains **two timelines**:

| Timeline | Meaning |
|----------|---------|
| **Valid time** | When events actually occurred in the real world |
| **Transaction time** | When the system came to know about the fact |

Example: Company A acquired Company B in January 2024, but the documents were uploaded to the system in March 2024.
- Valid time: 2024-01-15 (acquisition occurred)
- Transaction time: 2024-03-20 (system learned it)

When a decision is reviewed later, Utopia can **reproduce**: what the system actually believed at that decision moment (transaction time), and what the real-world state was (valid time). This is significant for compliance auditing, legal evidence, and decision replay.

**Correcting a fact doesn't overwrite it**: correcting an erroneous fact closes the old version and links to the new one. No `DELETE`, only `CLOSE`.

---

## Tech Stack: Minimal Operations

One strong engineering position:

```
One Rust binary
One Postgres (+ pgvector)
```

Full-text search embedded in the binary (Tantivy), vectors in pgvector, job queue as a database table. No Redis, no separate message queue, no dedicated vector database.

```bash
git clone https://github.com/deeplethe/utopia.git
cd utopia
docker compose --profile app up -d
# Open http://localhost:1516
```

Works with any OpenAI-compatible endpoint: DeepSeek, Qwen, GLM, Ollama, vLLM — the whole system can run **fully air-gapped**.

---

## Six Core Capabilities

**Knowledge ingest**: PDF, DOCX, PPTX, XLSX, CSV, Markdown, HTML, plain text. Scheduled sync from web, RSS, GitHub, Jira, Notion, WebDAV, S3.

**Search and chat**: Tantivy full-text + pgvector vector, fused with RRF. Answers stream with inline citations that open the source passage.

**Agent harness and agentic RAG**: Built-in agent searches documents, walks the graph (entity facts as of any date, or what changed in a period), queries mounted databases. Same read-only tools exposed over **MCP**.

**Ontology and cold start**: Ships five built-in packs (schema.org, W3C Org, PROV-O, FOAF, IOF Core). Unknown terms are counted as they appear — confirm the common ones and they join the ontology.

**Entity resolution**: Three stages — exact name/alias match → embedding similarity → model judgment on doubtful pairs. Every merge is undoable.

**Reasoning and derivation**: Ontology axioms compile into rules — transitivity, symmetry, inverses, relation hierarchy — derived via forward chaining. Derived facts are marked as such and trace to their sources.

---

## Ontology2SQL: BIRD Benchmark SOTA

Utopia's built-in **Ontology2SQL** — mounting database tables onto the knowledge ontology for natural-language querying — reaches SOTA on BIRD Mini-Dev (SQLite and PostgreSQL). Supports Postgres, MySQL, Trino (Iceberg/Delta Lake/Hive), Databricks, Snowflake.

---

## Decision Ledger

Every operation — confirming/rejecting a fact, merging/reverting an entity, rebuilding the graph — leaves a record: who, when, and what the object looked like at the time. The ledger is append-only. A record outlives its object, even the knowledge base it belonged to.

---

## Links

- GitHub: [deeplethe/utopia](https://github.com/deeplethe/utopia)
- Philosophy: [utopia.bi/philosophy](https://utopia.bi/philosophy)
- Ontology2SQL: [deeplethe/ontology2sql](https://github.com/deeplethe/ontology2sql)
