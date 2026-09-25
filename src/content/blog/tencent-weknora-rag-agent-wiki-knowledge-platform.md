---
title: "WeKnora：腾讯开源知识库平台，三模式 RAG + Agent + Wiki，Go + pgvector 自托管"
titleEn: "WeKnora: Tencent's Open-Source Knowledge Platform — RAG + Agent + Wiki Tri-Mode, Go + pgvector Self-Hosted"
description: "Tencent/WeKnora，MIT，Go，29,900+ stars。腾讯微信团队 2025 年 7 月开源的 LLM 知识库平台。三个工作模式：RAG 语义检索问答、ReAct 自主 Agent、Wiki 自维护知识图谱。微服务架构：Go 后端 + Vue.js 前端 + Python gRPC 文档解析 + PostgreSQL/pgvector + Redis。支持 10+ 文档格式、Feishu/Notion/Yuque 自动同步、WeCom/Slack/Telegram IM 集成、Ollama 本地部署，Langfuse 可观测性。官方 DeepSeek Harness 插件已上线。附完整 Docker 部署步骤。"
descriptionEn: "Tencent/WeKnora, MIT, Go, 29,900+ stars. LLM knowledge platform open-sourced by Tencent's WeChat team in July 2025. Three modes: RAG semantic retrieval Q&A, ReAct autonomous agent, Wiki self-maintaining knowledge graph. Microservices: Go backend + Vue.js frontend + Python gRPC document parser + PostgreSQL/pgvector + Redis. Supports 10+ document formats, auto-sync from Feishu/Notion/Yuque, WeCom/Slack/Telegram IM integration, Ollama local deployment, Langfuse observability. Official DeepSeek Harness plugin available. Full Docker deployment steps included."
pubDate: 2026-09-25
wechatTitle: "WeKnora：腾讯开源RAG+Agent+Wiki知识库"
wechatDigest: "腾讯开源知识库，RAG/Agent/Wiki三模式，pgvector内置，Ollama本地，飞书企微直接问答"
heroImage: "../../assets/images/tencent-weknora-rag-agent-wiki-knowledge-platform-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "rag", "knowledge-base", "tencent", "go", "agent", "wiki", "self-hosted", "docker"]
lang: zh-CN
---

`Tencent/WeKnora`，MIT，Go，29,953 stars，4,025 forks。腾讯微信团队 2025 年 7 月开源的 LLM 知识库平台——把原始文档变成可查询的 RAG、自主执行的推理 Agent 和自维护的 Wiki，三个模式选其一，也可以同时开。

**GitHub**：github.com/Tencent/WeKnora

---

## 三个工作模式

**模式一：RAG 语义问答**

文档进来 → 解析 → 切块 → 向量化 → 存 pgvector → 检索时做 reranking → 拼进 LLM prompt 回答。是最常见的企业知识库用法，直接问文档里的内容。

**模式二：ReAct 自主 Agent**

Agent 不只是检索——它自主决策：要不要查知识库、要不要调外部工具、要不要开沙盒执行代码。每一步推理和工具调用都被 Langfuse 追踪，可以在可观测面板里看到：推理链、工具调用序列、token 使用量、每步耗时。

**模式三：Wiki 自维护知识图谱**

这个模式比较有特色。开启 Wiki 后，WeKnora 从知识库文档里提取人物、产品、概念，自动生成结构化页面，每个页面带来源引用，按目录组织。知识图谱展示页面之间的关联。页面可以直接编辑，每次变更都可以回滚。

新文档进来时，Wiki 自动更新相关页面——而不是只有一堆原始文件等人查。

---

## 架构：5 个 Docker 容器

```
┌─────────────────────────────────────────────────────────────┐
│                    WeKnora Docker Compose                   │
│                                                             │
│  WeKnora-frontend  ──▶  WeKnora-app (Go, :8080)            │
│   Vue.js + NGINX             │                              │
│                              ├── weknora-docreader          │
│                              │   (Python gRPC, 文档解析)    │
│                              ├── postgres (ParadeDB 17)     │
│                              │   pgvector 内置向量存储       │
│                              └── redis (Asynq 任务队列)     │
└─────────────────────────────────────────────────────────────┘
```

**核心组件说明：**

- **Go 后端**：依赖注入架构，router、handler、agent engine、knowledge pipeline、基础设施服务分层。API 在 `:8080`，健康检查 `/health`。
- **Python docreader**：独立 gRPC 微服务，负责文档解析（PDF OCR、表格提取等）。重 CPU 操作不阻塞主服务。
- **ParadeDB**（PostgreSQL 17）：既是关系型存储，也是默认向量存储（pgvector）。不需要额外部署 Qdrant 就能跑起来。
- **Redis + Asynq**：文档导入是异步的，任务队列防止大批量导入时把服务打挂。

**可选扩展（通过 Compose profile 按需开）：**

| 扩展组件 | 用途 |
|---------|------|
| Qdrant / Milvus | 替换 pgvector，做高性能向量检索 |
| Neo4j | 图数据库，增强知识图谱关系存储 |
| SearXNG | 自托管搜索引擎，Agent 联网搜索 |
| MinIO | 对象存储，大文件和文档归档 |
| Langfuse | Agent 推理可观测性 |

---

## 支持的文档格式和数据源

**文档格式（10+ 种）：**

PDF、Word（.docx）、Excel（.xlsx）、PowerPoint、图片（含 OCR）、XMind、Markdown、TXT、HTML 等。

**自动同步来源：**

- 飞书（文档、知识库）
- GitLab（仓库文档）
- 腾讯 IMA
- Notion
- Yuque（语雀）

**IM 渠道直接问答：**

WeKnora 可以挂到 IM 渠道里作为知识库机器人：WeCom（企业微信）、飞书、Slack、Telegram。配置后用户直接在聊天里@就能问文档。

---

## LLM 支持

全部通过配置切换，不需要改代码：

| 类型 | 支持的提供商/模型 |
|------|----------------|
| **云端 API** | OpenAI、DeepSeek、Qwen（阿里云）、智谱、混元、Gemini、MiniMax、NVIDIA |
| **本地部署** | Ollama（推荐 qwen2.5 对话 + bge-m3 Embedding） |

默认配置用 Ollama，完全本地运行，不需要 API key，数据不出机器。

---

## 部署步骤

**最简路径（Docker Compose + Ollama）：**

```bash
# 前置：安装 Docker、Docker Compose，并准备好 Ollama
ollama pull qwen2.5          # 对话模型
ollama pull bge-m3            # Embedding 模型

# 部署 WeKnora
git clone https://github.com/Tencent/WeKnora.git
cd WeKnora
cp .env.example .env

# 在 .env 里配置：
# LLM_BASE_URL=http://host.docker.internal:11434   (Ollama)
# LLM_MODEL=qwen2.5
# EMBEDDING_MODEL=bge-m3

docker compose up -d
```

打开 http://localhost（默认 80 端口），注册管理员账户，创建第一个知识库，上传文档，等待解析完成就能开始问答。

**硬件建议（从架构推算，官方未给出具体数字）：**

| 场景 | 建议配置 |
|------|---------|
| 纯云端 LLM（OpenAI/DeepSeek 等） | 8GB RAM、2 核 CPU、50GB+ 存储 |
| 本地 Ollama（qwen2.5 7B） | 16GB RAM（MacBook Pro M 系列 / 16GB 内存 PC 勉强） |
| 本地 Ollama（qwen2.5 14B+） | 32GB RAM |
| 生产环境（多用户、大文档库） | 32GB RAM、SSD、考虑 Qdrant 替换 pgvector |

---

## 官方 DeepSeek Harness 插件

WeKnora 上线了官方的 DeepSeek Harness 插件，支持把 WeKnora 的知识库能力接入 DeepSeek Harness 工作流。这意味着你可以在 DSH 的 Agent 里直接调 WeKnora 的 RAG 检索，不需要自己搭接口。

---

## 和同类产品的定位

国内外同类开源知识库平台（RAGflow、MaxKB、Dify 等）基本都在做「RAG + 聊天」这个核心场景。WeKnora 的差异化在 Wiki 模式——自动从文档里提取知识构建结构化页面，并保持和原始文档同步更新，更接近一个「活的企业 Wiki」而不只是一个问答机器人。

另一个差异是腾讯出品的背书——飞书自动同步、企业微信 IM 集成、Hunyuan 模型支持，这些对腾讯生态里的用户是直接可用的。

---

## 局限性

**1. 文档解析质量**：Python docreader 处理复杂 PDF 的效果取决于文档质量，扫描件 OCR 准确率可能不稳定。社区有第三方优化版（xiaohuangpin/WeKnora-pro）专门针对扫描件和表格提取做了改进。

**2. Wiki 的自动更新**：文档变更后 Wiki 页面需要重新索引，大知识库时更新延迟取决于文档解析队列。

**3. 本地硬件门槛**：完整功能（带 Langfuse、Milvus 等可选服务）内存需求可能超过 16GB，消费级机器上的精简部署可能要关闭一些服务。

**4. 社区活跃度**：4,025 forks，PR 频率较高，但企业级功能（细粒度权限、审计日志）文档还在补充中。

---

## 怎么看这个项目

29,953 stars，多数知识库平台在拿到这个数字时都已经是成熟产品了。WeKnora 的 stars 更多来自「腾讯 + 开源」的效应，实际功能的成熟度需要自己在场景里验证。

值得真正关注的是三点：pgvector 内置让最简部署不需要额外向量数据库、Wiki 模式的自动更新机制是同类里少见的、官方 DeepSeek Harness 插件打通了和 DSH 生态的集成。

对于已经在用飞书、企业微信、Yuque 的团队，把 WeKnora 架起来做内部知识库助手的路径是最短的。

> 开源仅供学习研究参考。商用前请核实 LICENSE 文件中关于第三方组件的条款。

---

<!--EN-->

## WeKnora: Tencent's Open-Source Knowledge Platform — RAG + Agent + Wiki

`Tencent/WeKnora` — MIT, Go, 29,953 stars. LLM knowledge platform open-sourced by Tencent's WeChat team (July 2025). Three working modes: RAG Q&A, ReAct autonomous agent, Wiki self-maintaining knowledge graph.

**GitHub**: github.com/Tencent/WeKnora

---

### Three Modes

**RAG Q&A**: Documents → parse → chunk → embed → pgvector → rerank → LLM answer. Standard semantic retrieval over your document corpus.

**ReAct Agent**: Autonomous orchestration — decides whether to query the knowledge base, call external tools, or run sandboxed code. Every reasoning step and tool call traced by Langfuse.

**Wiki**: WeKnora extracts people, products, and concepts from knowledge base documents into structured pages with source citations. Knowledge graph shows page relationships; pages are editable with full rollback. Auto-updates when source documents change.

---

### Architecture

Five Docker containers:

| Container | Role |
|-----------|------|
| `WeKnora-app` | Go backend (:8080), API + RAG pipeline + agent engine |
| `WeKnora-frontend` | Vue.js SPA + NGINX |
| `weknora-docreader` | Python gRPC document parser (PDF OCR, table extraction) |
| `postgres` | ParadeDB (PostgreSQL 17) — relational + default pgvector store |
| `redis` | Asynq async task queue |

Optional via Compose profiles: Qdrant/Milvus (vector DB), Neo4j (graph), SearXNG (web search), MinIO (object storage), Langfuse (observability).

---

### Document Formats and Sources

**Formats (10+)**: PDF, Word, Excel, PowerPoint, images (OCR), XMind, Markdown, TXT, HTML.

**Auto-sync sources**: Feishu, GitLab, Tencent IMA, Notion, Yuque.

**IM channels**: WeChat Work (WeCom), Feishu, Slack, Telegram — query the knowledge base directly from chat.

---

### LLM Support

All switchable via config, no code changes: OpenAI, DeepSeek, Qwen (Alibaba Cloud), Zhipu, Hunyuan, Gemini, MiniMax, NVIDIA, Ollama (local).

Default: Ollama with `qwen2.5` (chat) + `bge-m3` (embeddings) — fully local, no API key needed.

---

### Deployment

```bash
# Prerequisites: Docker, Docker Compose, Ollama
ollama pull qwen2.5 && ollama pull bge-m3

git clone https://github.com/Tencent/WeKnora.git
cd WeKnora && cp .env.example .env
# Configure: LLM_BASE_URL, LLM_MODEL, EMBEDDING_MODEL in .env
docker compose up -d
# Open http://localhost
```

Estimated hardware (not officially specified):
- Cloud LLM (OpenAI/DeepSeek): 8GB RAM, 2 CPU cores, 50GB+ storage
- Local Ollama 7B: 16GB RAM
- Local Ollama 14B+: 32GB RAM
- Production (multi-user, large corpus): 32GB RAM + SSD

---

### Official DeepSeek Harness Plugin

Tencent released an official DSH plugin for WeKnora, enabling WeKnora RAG retrieval to be called directly from DeepSeek Harness agent workflows without building a custom integration.

---

### Limitations

1. **Document parsing quality**: Python docreader OCR accuracy varies for scanned PDFs; a community fork (xiaohuangpin/WeKnora-pro) addresses this
2. **Wiki update latency**: Re-indexing on document changes queued async — delays on large corpora
3. **Hardware for full stack**: Full feature set with optional services may exceed 16GB RAM
4. **Enterprise features**: Fine-grained permissions and audit logs documentation is still catching up

---

### Assessment

29,953 stars largely reflects the "Tencent + open source" announcement effect. Actual production readiness needs evaluation in your specific context. Three genuinely differentiating points: built-in pgvector eliminates the need for a separate vector database on simple deployments; the Wiki auto-update mechanism is rare among similar platforms; the official DSH plugin provides a pre-built integration path for DeepSeek Harness users. Teams already using Feishu, WeCom, or Yuque have the shortest path to standing up an internal knowledge assistant.

> For learning and research reference only. Review the LICENSE file for third-party component terms before commercial use.
