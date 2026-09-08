---
title: "LEANN：省掉 97% 向量存储，让 RAG 跑在本地设备上"
titleEn: "LEANN: 97% Vector Storage Savings, Bringing RAG to Personal Devices"
description: "Berkeley 出品的 MLsys2026 最佳论文，用图结构+按需重计算替代全量向量存储，6GB 索引 6000 万文本块（传统方案需 201GB），支持 PDF/邮件/微信/浏览器历史/Claude 对话等全个人数据，零遥测本地运行，Stars 12913。"
descriptionEn: "MLsys2026 Best Paper from Berkeley Sky Computing Lab. Graph-based selective recomputation replaces full embedding storage — 6GB to index 60M text chunks vs 201GB traditionally (97% reduction, no accuracy loss). Supports PDF, email, WeChat, browser history, Claude chat archives, and live MCP sources. Zero telemetry, local-only. 12913 Stars."
pubDate: "2026-09-08"
updatedDate: "2026-09-08"
category: "Research"
tags: ["RAG", "向量数据库", "本地AI", "隐私", "开源", "MLsys"]
heroImage: "../../assets/images/leann-rag-97-percent-storage-savings-graph-recompute-banner.jpg"
---

> 📌 项目地址：https://github.com/StarTrail-org/LEANN
> 论文：arXiv:2506.08276 — https://arxiv.org/abs/2506.08276

**传统 RAG 处理百万级文档时，向量索引常常膨胀到几百 GB，普通本地设备根本跑不起来。**

LEANN 跳出"全量向量存储"这个思路，只维护精简的图结构，检索阶段再按需计算嵌入，直接省下 **97% 的存储**——60 万条文本块的索引从传统方案的 201GB 压缩到 6GB，精度没有损失。

这是 UC Berkeley Sky Computing Lab 的研究成果，获 **MLsys2026 最佳论文**奖，开源后 Stars 已达 **12913**，MIT 协议。

## 核心技术：图结构 + 按需重计算

普通向量数据库（FAISS、Pinecone、Chroma）的做法：先把所有文档嵌入向量算好，全部存在磁盘或内存里，检索时直接比对。存储占用 = 文档数量 × 向量维度 × 4 字节，百万文档动辄几十 GB。

LEANN 的做法不同：

1. **只存图结构**：维护文档之间的近邻关系图（类似 HNSW 的导航结构），但不持久化嵌入向量本身
2. **检索时按需重计算**：搜索时沿图遍历，只对访问到的候选节点实时计算嵌入向量
3. **高度保留剪枝**：在图构建阶段用 high-degree preserving pruning 保留关键连接，确保遍历路径不退化

结果：索引大小只取决于图的边，与向量维度无关，存储大幅压缩。

## 两种索引后端

| 后端 | 适用场景 | 原理 |
|------|---------|------|
| **HNSW**（默认）| 最大化存储节省 | 完全重计算，嵌入不落盘 |
| **DiskANN** | 追求搜索速度 | PQ 压缩索引 + 实时 reranking |

HNSW 模式下存储节省最彻底；DiskANN 模式适合对延迟敏感、存储稍宽裕的场景。

## 数据源覆盖范围

LEANN 的定位是"个人数据全面 RAG 化"，已内置支持：

- **文件**：PDF、文本文档
- **邮件**：Apple Mail
- **浏览器**：Chrome 历史记录
- **即时通讯**：微信、iMessage
- **AI 对话存档**：ChatGPT、Claude 历史记录
- **实时数据**：通过 MCP（Model Context Protocol）接入 Slack、Twitter 等

全部本地运行，零遥测，不联网，不上传任何数据。

## Benchmark 数据

| 数据集 | 传统方案 | LEANN | 节省比例 |
|--------|---------|-------|---------|
| Wikipedia（6000 万块） | 201 GB | 6 GB | **97%** |
| 邮件数据 | — | — | 91% |
| 微信记录 | — | — | 95% |

精度（Recall@K）与全量存储方案持平，无损压缩。

## 安装与使用

```bash
pip install leann
```

```python
from leann import LEANN

# 建索引
index = LEANN()
index.add_documents(["your", "documents", "here"])

# 检索
results = index.search("query", top_k=5)
```

兼容 LangChain 和 LlamaIndex，现有 RAG 管道直接替换向量数据库即可。

## 为什么这件事重要

**本地 RAG 的核心瓶颈一直是存储，不是算力。** 一台 MacBook 有足够的 CPU 算 embedding，但磁盘放不下几百 GB 的索引。LEANN 把这个约束打掉了——个人设备现在可以检索自己全部的本地数据，包括多年的聊天记录、邮件、文档，而不需要把任何数据传到云端。

从学术角度看，"不存向量，检索时重算"听起来像是用时间换空间的老方案，但高度保留剪枝使得实际需要重算的节点数极少，延迟可控。这是 Berkeley Sky Computing Lab 的核心工程贡献。

> 📌 论文：arXiv:2506.08276 — https://arxiv.org/abs/2506.08276

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/StarTrail-org/LEANN
> Paper: arXiv:2506.08276 — https://arxiv.org/abs/2506.08276

**The biggest obstacle to local RAG isn't compute — it's storage.** A MacBook has enough CPU to run embeddings, but not enough disk for hundreds of gigabytes of vector indexes.

LEANN (MLsys2026 Best Paper, Berkeley Sky Computing Lab) eliminates this constraint: graph-based selective recomputation reduces index size by **97%** — 60M text chunks fit in 6GB instead of 201GB — with no accuracy loss. 12,913 Stars, MIT license.

## How It Works

Traditional vector databases store every document's embedding on disk. LEANN stores only the neighbor graph (navigation structure), computing embeddings on demand during search traversal. High-degree preserving pruning keeps graph paths efficient, so the number of nodes requiring recomputation during any query stays small.

Two backends: **HNSW** (default, maximum storage savings via full recomputation) and **DiskANN** (PQ-based traversal + real-time reranking for latency-sensitive workloads).

## What It Indexes

PDF, Apple Mail, Chrome history, WeChat, iMessage, ChatGPT and Claude conversation archives, plus live sources via MCP (Slack, Twitter). Everything runs locally — zero telemetry, no cloud dependency.

## Why It Matters

"Recompute instead of store" sounds like a time-for-space tradeoff, but high-degree preserving pruning makes the actual recomputation minimal. The result: personal RAG across years of chat history, email, and documents — entirely on-device, entirely private.

```bash
pip install leann
```

Drops into LangChain and LlamaIndex as a vector store replacement.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
