---
title: "Zvec：嵌入式向量数据库，RAG 和 Agent Memory 不再需要独立服务"
titleEn: "Zvec: Embedded Vector Database — RAG and Agent Memory Without a Separate Server"
description: "阿里开源的 alibaba/zvec 是一个进程内向量数据库，无需启动独立服务，pip install 即可在应用内完成向量+全文+混合检索。v0.7.0 新增 zvec-grep (zg) 统一 ripgrep/BM25/向量搜索，并正式支持 ReMe 作为 Agent Memory 后端。"
descriptionEn: "Alibaba's alibaba/zvec is an in-process vector database — no server needed. pip install it and get dense+sparse vectors, full-text search, and hybrid search inside your app. v0.7.0 adds zvec-grep (zg) unifying ripgrep/BM25/vector search, and official ReMe Agent Memory backend support."
pubDate: 2026-09-03
updatedDate: 2026-09-03
category: Tech-Experiment
tags: ["AI", "向量数据库", "RAG", "Agent Memory", "开源", "阿里", "embedding", "Hybrid Search"]
heroImage: "../../assets/images/alibaba-zvec-in-process-vector-db-rag-agent-memory-banner.jpg"
author: "Mycelium Protocol"
---

做 RAG 或 Agent Memory，第一个问题通常是：向量数据库选什么？

Milvus？要跑一个独立服务，配 etcd 和 MinIO。Elasticsearch？JVM，重。Chroma？轻一些，但还是一个进程外的 HTTP 服务。Qdrant？Rust 写的，性能好，但依然是服务器模式。

**[alibaba/zvec](https://github.com/alibaba/zvec)** 的答案是：这些都不需要。

直接嵌进你的应用里，一行 `pip install zvec`，完成。

---

## 什么是 In-Process 向量数据库

传统的向量数据库是**客户端-服务器架构**：你的应用和数据库是两个独立进程，通过网络或 socket 通信。

Zvec 的模式是**进程内（in-process）**：数据库就是一个库，和你的代码运行在同一个进程里。没有网络跳数，没有序列化/反序列化，没有守护进程，没有配置文件。

类比：SQLite 和 PostgreSQL 的关系。PostgreSQL 是服务器，SQLite 是进程内数据库。Zvec 是向量世界的 SQLite。

阿里内部已经在生产环境跑了它，15,600+ stars，Apache 2.0，C++ 核心，多语言 SDK：Python / Node.js / Go / Rust / Dart（Flutter）。

---

## 核心能力

### 向量检索：Dense + Sparse

支持密集向量（text-embedding-3-large、bge-m3 这类）和稀疏向量（BM25、SPLADE 这类），可以在同一个 collection 里混用。

索引类型：
- **HNSW**：内存索引，低延迟，适合中小规模（千万量级以下）
- **DiskANN**：磁盘索引，v0.7.0 新增 macOS ARM64 / Linux ARM64 支持 + io_uring 异步 IO，适合亿级别数据
- **IVF-RaBitQ**：v0.7.0 新增，支持 AVX2 / AVX512 运行时自动分发
- **PQ-INT8**：量化压缩，降低内存占用

### 全文检索（FTS）

内置全文搜索，v0.7.0 新增 N-gram tokenizer，更适合代码、短文本、词组搜索。不需要 Elasticsearch，不需要 Lucene。

### Hybrid Search

一次查询同时做向量相似度 + 全文检索 + 结构化过滤，结果融合后返回。这是 RAG 场景里最有价值的特性——纯向量搜索容易遗漏精确关键词，纯全文搜索找不到语义相关内容，混合检索是两者之间的最佳实践。

### WAL 持久化

Write-ahead logging，进程崩溃或断电不丢数据。不是"轻量所以不可靠"，是轻量且可靠。

---

## v0.7.0 的两个 AI-Native 新特性

### zvec-grep（zg）：给人和 Agent 的本地搜索 CLI

```bash
pip install zvec-grep
# 或
cargo install zg
```

`zg` 把三种搜索合并成一个 CLI：
- **ripgrep**：精确字符串匹配，搜代码、日志
- **BM25**：全文关键词搜索，搜文档
- **向量搜索**：语义搜索，搜"意思相近的内容"

一个命令，三种搜索，结果融合返回。既是给人用的，也是给 AI Agent 用的——Agent 搜索工作区不再需要分别调用三个不同的工具。

### ReMe 集成：Agent Memory 的文件存储后端

**[ReMe](https://github.com/agentscope-ai/ReMe)** 是 AgentScope 团队的 Agent 记忆管理套件。v0.7.0 起，ReMe 可以用 Zvec 作为文件存储后端，提供进程内 HNSW 近似最近邻搜索。

这意味着：Agent 的 Memory 存储不需要独立的向量数据库服务，可以直接嵌在 Agent 进程里，记忆随进程启动，不需要额外运维。

---

## 快速上手：5 分钟搭一个 RAG 向量库

```python
import zvec
from your_embedding_model import embed  # 任意 embedding 函数

# 定义 schema
schema = zvec.CollectionSchema(
    name="docs",
    vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, 1536),
    texts=["content", "title"],
)

# 创建 / 打开 collection（文件存在则打开，不存在则创建）
col = zvec.create_and_open(path="./my_rag_db", schema=schema)

# 插入文档
docs = [
    {"id": "doc_1", "content": "Zvec 是阿里开源的嵌入式向量数据库", "title": "介绍"},
    {"id": "doc_2", "content": "向量检索支持 HNSW 和 DiskANN", "title": "索引"},
]
col.insert([
    zvec.Doc(
        id=d["id"],
        vectors={"embedding": embed(d["content"])},
        texts={"content": d["content"], "title": d["title"]},
    )
    for d in docs
])

# 向量检索
results = col.query(
    zvec.Query(field_name="embedding", vector=embed("什么是嵌入式向量数据库")),
    topk=5
)

# Hybrid Search（向量 + 全文融合）
results = col.hybrid_query(
    vector_query=zvec.Query(field_name="embedding", vector=embed("向量数据库")),
    text_query=zvec.TextQuery(field="content", text="HNSW"),
    topk=5
)
```

和 Milvus / Chroma 不同，整个过程没有网络请求，没有服务进程，数据文件就在 `./my_rag_db/` 目录下。

---

## 什么场景适合 Zvec

**适合**：
- **单机 RAG 应用**：一个 Python 脚本 / 一个 API 服务，向量数据在本地，不需要扩展到多机
- **本地 AI 工具**：IDE 插件、桌面 App、CLI 工具，不想让用户运行数据库服务
- **开发 / 测试阶段**：团队早期快速验证 RAG 效果，不想先花时间部署基础设施
- **Agent Memory**：Agent 进程的持久记忆，随进程生死，不需要独立运维
- **Edge 部署**：树莓派、移动设备、IoT 场景，支持 Linux ARM64 / Android / iOS

**不适合**：
- **多机分布式**：Zvec 是单节点的，写操作是单进程独占的，多机横向扩展需要 Milvus 这类分布式方案
- **多写场景**：多个进程同时写同一个 collection 不支持（多读 OK）
- **超大规模**：百亿向量 + 高 QPS 的场景，Zvec 的 DiskANN 有上限，分布式系统更合适

---

## 和 ChromaDB 的对比

| 维度 | Zvec | ChromaDB |
|------|------|----------|
| 架构 | 进程内库 | 可进程内 / 可客户端-服务器 |
| 核心语言 | C++ | Python |
| 稀疏向量 | 支持 | 不支持 |
| 全文检索 | 内置 | 不支持 |
| Hybrid Search | 支持 | 不支持 |
| DiskANN（磁盘索引）| 支持 | 不支持 |
| 生态 SDK | Python/Node/Go/Rust/Dart | Python（主）/JS |
| 阿里生产验证 | 是 | 否 |

对于需要 Hybrid Search 或稀疏向量的场景，Zvec 的功能覆盖明显更完整。

---

## 安装和资源

```bash
# Python
pip install zvec

# Node.js
npm install @zvec/zvec

# Rust
cargo add zvec-rust

# Flutter
flutter pub add zvec
```

- GitHub：[alibaba/zvec](https://github.com/alibaba/zvec)
- 文档：[zvec.org/en/docs/db/quickstart/](https://zvec.org/en/docs/db/quickstart/)
- zvec-grep：[github.com/zvec-ai/zvec-grep](https://github.com/zvec-ai/zvec-grep)
- Zvec Studio（GUI）：[github.com/zvec-ai/zvec-studio](https://github.com/zvec-ai/zvec-studio)
- Benchmarks：[zvec.org/en/docs/db/benchmarks/](https://zvec.org/en/docs/db/benchmarks/)
- ReMe（Agent Memory 套件）：[github.com/agentscope-ai/ReMe](https://github.com/agentscope-ai/ReMe)

<!--EN-->

The first question when building RAG or Agent Memory is usually: which vector database?

Milvus? Needs a separate service, etcd, and MinIO. Elasticsearch? JVM overhead. Chroma? Lighter, but still an out-of-process HTTP server. Qdrant? Great performance, still server-mode.

**[alibaba/zvec](https://github.com/alibaba/zvec)** answers with: you need none of that.

Embed it directly in your app — `pip install zvec`, done.

---

## What Is an In-Process Vector Database

Traditional vector databases follow a **client-server architecture**: your app and the database are two separate processes communicating over network or sockets.

Zvec is **in-process**: the database is a library running in the same process as your code. No network round-trips, no serialization overhead, no daemon to manage, no config files.

The analogy: SQLite versus PostgreSQL. PostgreSQL is a server; SQLite is an in-process database. Zvec is SQLite for the vector world.

Battle-tested inside Alibaba's production systems. 15,600+ stars. Apache 2.0. C++ core with multi-language SDKs: Python / Node.js / Go / Rust / Dart (Flutter).

---

## Core Capabilities

### Dense + Sparse Vectors

Supports both dense vectors (text-embedding-3-large, bge-m3, etc.) and sparse vectors (BM25, SPLADE, etc.), mixable within the same collection.

Index types:
- **HNSW**: In-memory index, low latency, optimal for tens of millions of vectors
- **DiskANN**: Disk-based index. v0.7.0 adds macOS ARM64 / Linux ARM64 + io_uring async I/O; suited for billion-scale data
- **IVF-RaBitQ**: v0.7.0 addition; runtime AVX2 / AVX512 dispatch — same binary selects the best path per CPU
- **PQ-INT8**: Quantized compression to reduce memory footprint

### Full-Text Search (FTS)

Built-in full-text search. v0.7.0 adds an N-gram tokenizer, better for code, short text, and phrase matching. No Elasticsearch, no Lucene.

### Hybrid Search

One query combines vector similarity + full-text keyword + structured filters, with fused results returned. This is the most valuable feature for RAG — pure vector search misses exact keyword hits; pure full-text search misses semantic relevance. Hybrid is the production best practice.

### WAL Persistence

Write-ahead logging. Process crash or power loss does not lose data. Lightweight AND reliable.

---

## v0.7.0's Two AI-Native Features

### zvec-grep (`zg`): A Local Search CLI for Humans and Agents

```bash
pip install zvec-grep
# or
cargo install zg
```

`zg` merges three search modes into one CLI:
- **ripgrep**: Exact string match — code and logs
- **BM25**: Full-text keyword — documents
- **Vector search**: Semantic — conceptually related content

One command, three search modes, fused results. Designed for both humans and AI agents — an agent searching a workspace no longer needs to call three separate tools.

### ReMe Integration: Agent Memory File Store Backend

**[ReMe](https://github.com/agentscope-ai/ReMe)** is the AgentScope team's memory management kit for agents. As of v0.7.0, ReMe can use Zvec as its file-store backend, providing in-process HNSW ANN search.

Practically: an agent's long-term memory no longer requires a separate vector database service. Memory lives in the agent's own process, starts with it, and needs zero additional infrastructure.

---

## Quick Start: RAG Vector Store in 5 Minutes

```python
import zvec
from your_embedding_model import embed  # any embedding function

# Define schema
schema = zvec.CollectionSchema(
    name="docs",
    vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, 1536),
    texts=["content", "title"],
)

# Create / open collection (opens if exists, creates if not)
col = zvec.create_and_open(path="./my_rag_db", schema=schema)

# Insert documents
docs = [
    {"id": "doc_1", "content": "Zvec is Alibaba's open-source embedded vector DB", "title": "Intro"},
    {"id": "doc_2", "content": "Vector retrieval supports HNSW and DiskANN", "title": "Index"},
]
col.insert([
    zvec.Doc(
        id=d["id"],
        vectors={"embedding": embed(d["content"])},
        texts={"content": d["content"], "title": d["title"]},
    )
    for d in docs
])

# Vector search
results = col.query(
    zvec.Query(field_name="embedding", vector=embed("what is an embedded vector db")),
    topk=5
)

# Hybrid Search (vector + full-text fused)
results = col.hybrid_query(
    vector_query=zvec.Query(field_name="embedding", vector=embed("vector database")),
    text_query=zvec.TextQuery(field="content", text="HNSW"),
    topk=5
)
```

No network requests. No service process. Data files sit in `./my_rag_db/`.

---

## When to Use Zvec

**Good fit**:
- **Single-node RAG apps**: a Python script or API service where all vector data is local and multi-machine scaling isn't needed
- **Local AI tooling**: IDE plugins, desktop apps, CLI tools where you don't want users running a database service
- **Development and testing**: quickly validate RAG quality before committing to infrastructure
- **Agent Memory**: persistent memory embedded in the agent process, lives and dies with the process, zero additional ops
- **Edge deployment**: Raspberry Pi, mobile, IoT — supports Linux ARM64 / Android / iOS

**Not the right fit**:
- **Multi-node distributed**: Zvec is single-node; writes are exclusive to one process; horizontal scale-out needs Milvus-class distributed systems
- **Multi-writer scenarios**: concurrent writes from multiple processes to the same collection are not supported (concurrent reads are fine)
- **Massive scale**: tens of billions of vectors at high QPS — DiskANN has limits; distributed systems win here

---

## vs ChromaDB

| Dimension | Zvec | ChromaDB |
|-----------|------|----------|
| Architecture | In-process library | In-process or client-server |
| Core language | C++ | Python |
| Sparse vectors | Yes | No |
| Full-text search | Built-in | No |
| Hybrid Search | Yes | No |
| DiskANN (disk index) | Yes | No |
| SDKs | Python/Node/Go/Rust/Dart | Python (main) / JS |
| Alibaba production validated | Yes | No |

For hybrid search or sparse vector requirements, Zvec's feature coverage is substantially more complete.

---

## Install and Resources

```bash
# Python
pip install zvec

# Node.js
npm install @zvec/zvec

# Rust
cargo add zvec-rust

# Flutter
flutter pub add zvec
```

- GitHub: [alibaba/zvec](https://github.com/alibaba/zvec)
- Docs: [zvec.org/en/docs/db/quickstart/](https://zvec.org/en/docs/db/quickstart/)
- zvec-grep: [github.com/zvec-ai/zvec-grep](https://github.com/zvec-ai/zvec-grep)
- Zvec Studio (GUI): [github.com/zvec-ai/zvec-studio](https://github.com/zvec-ai/zvec-studio)
- Benchmarks: [zvec.org/en/docs/db/benchmarks/](https://zvec.org/en/docs/db/benchmarks/)
- ReMe (Agent Memory kit): [github.com/agentscope-ai/ReMe](https://github.com/agentscope-ai/ReMe)
