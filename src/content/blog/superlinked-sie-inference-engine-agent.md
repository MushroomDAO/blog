---
title: "SIE：把 Agent 需要的所有模型装进一个集群——Superlinked 开源的统一推理引擎"
titleEn: "SIE: One Cluster for Every Model Your Agent Needs — Superlinked's Open-Source Unified Inference Engine"
description: "superlinked/sie（2,286 stars，Apache 2.0）是 Superlinked 开源的自托管推理引擎，把 Agent 需要的 5 类任务（搜索/文档转换/结构化提取/内容安全/Agent 循环）统一进一套 OpenAI 兼容 API 和一个集群，100+ 模型按需加载 + LRU 淘汰。支持从本地 pip 安装到 GKE/EKS/AKS 生产集群（Helm + Terraform 全套），还有 MCP 包可以让 Claude 直接调用集群能力。"
descriptionEn: "superlinked/sie (2,286 stars, Apache 2.0) is an open-source self-hosted inference engine that unifies all 5 agent task types (search, document conversion, structured extraction, content safety, agent loop) into a single OpenAI-compatible API and cluster. 100+ models loaded on demand with LRU eviction. Supports local pip install through GKE/EKS/AKS production clusters (full Helm + Terraform). MCP package lets Claude call cluster capabilities directly."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["推理引擎", "AI Agent", "嵌入模型", "RAG", "自托管", "SIE", "Superlinked", "开源", "向量搜索", "MLOps"]
heroImage: "../../assets/images/superlinked-sie-inference-engine-agent-banner.jpg"
---

> **GitHub**：[superlinked/sie](https://github.com/superlinked/sie) · ⭐ 2,286 · Python · Apache 2.0  
> **文档**：[superlinked.com/docs](https://superlinked.com/docs)  
> **模型目录**：[superlinked.com/models](https://superlinked.com/models)

---

## Agent 的基础设施碎片化问题

一个典型的 RAG + Agent 系统，背后跑着多少个不同的模型服务？

- 一个**嵌入模型**服务，把文档和查询向量化
- 一个**重排序模型**服务，对检索结果精排
- 一个**OCR 服务**，把 PDF 和扫描件变成可索引的文本
- 一个**实体抽取服务**，从文本里提取结构化信息
- 一个**内容安全服务**，过滤有害输出
- 一个**LLM 服务**，跑 Agent 的推理和工具调用

六个不同的服务，六套部署逻辑，六个监控仪表盘，六种扩缩容策略。任何一个不稳定就影响整个 pipeline。

**SIE（Superlinked Inference Engine）的答案是：把这六件事放进一个集群，用一套 OpenAI 兼容 API 统一暴露出来。**

---

## 五类 Agent 任务，一套 API

SIE 把 Agent 需要的能力归纳成五类任务：

| 任务 | 做什么 | 默认模型 |
|---|---|---|
| **搜索（Search）** | 嵌入 + 匹配 + 重排序 | bge-m3, SPLADE-v3, ColBERT v2, Qwen3-reranker |
| **文档转 Markdown** | PDF/Office/扫描件 → 干净 markdown | GLM-OCR, MinerU, PaddleOCR-VL, Docling |
| **结构化输出** | 模式合法的 JSON，提取或生成 | GLiNER2, NuNER-zero, Qwen3.6-27B |
| **内容安全** | 安全判定 + 概率阈值 | Granite-Guardian-2B |
| **Agent 循环** | 规划步骤 + 工具调用，支持流式 | Qwen3.6-27B |

所有任务用同一套 API 端点：

```
/v1/embeddings         ← OpenAI 兼容，直接替换
/v1/chat/completions   ← 流式支持
/v1/completions
/v1/responses
```

已有 OpenAI 客户端的代码只需要改 `base_url`，其余不动。

---

## 按需加载 + LRU 淘汰

SIE 不是在启动时把所有模型加载进显存，而是**按需加载 + LRU（最近最少使用）淘汰**：

- 调用某个模型时，如果没有加载，自动从 HuggingFace 下载并加载（首次调用需要几分钟下载权重）
- 之后调用毫秒级响应
- 显存不足时，淘汰最久未使用的模型
- 100+ 模型都配置在 `packages/sie_server/models/` 下，传 HuggingFace ID 即可调用

这个设计让一台机器可以"托管"100+ 个模型，同时只有当前用到的加载在显存里。

---

## SDK 示例：三行代码覆盖三种任务

```python
from sie_sdk import SIEClient
from sie_sdk.types import Item

client = SIEClient("http://localhost:8080")

# 生成嵌入
result = client.encode("sentence-transformers/all-MiniLM-L6-v2", Item(text="Hello world"))
print(result["dense"].shape)  # (384,)

# 重排序
scores = client.score(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    Item(text="What is machine learning?"),
    [Item(text="ML learns from data."), Item(text="The weather is sunny.")],
)
print(scores["scores"][0])  # {'item_id': 'item-0', 'score': -7.1, 'rank': 0}

# 实体抽取
result = client.extract(
    "urchade/gliner_multi-v2.1",
    Item(text="Tim Cook is the CEO of Apple."),
    labels=["person", "organization"],
)
print(result["entities"][0])
# {'text': 'Tim Cook', 'label': 'person', 'score': 0.992, ...}
```

SDK 支持 Python 和 TypeScript（`@superlinked/sie-sdk`）。

---

## 从本地到生产：同一套代码

### 本地启动（三行）

```bash
# macOS Apple Silicon 或 Linux
pip install "sie-server[local]" && sie-server serve

# 验证
curl http://localhost:8080/readyz   # → ok
```

Linux + NVIDIA GPU 用 Docker：

```bash
docker run --gpus all -p 8080:8080 \
  -v sie-hf-cache:/app/.cache/huggingface \
  ghcr.io/superlinked/sie-server:latest-cuda12-default
```

需要 LLM 生成能力（SGLang 后端）：

```bash
docker run --gpus all -p 8080:8080 \
  -v sie-hf-cache:/app/.cache/huggingface \
  ghcr.io/superlinked/sie-server:latest-cuda12-sglang
```

### 生产集群（Helm + Terraform）

```bash
# 选择对应云厂商的 values 文件：values-gke.yaml / values-aws.yaml / values-aks.yaml
helm upgrade --install sie-cluster oci://ghcr.io/superlinked/charts/sie-cluster \
  --namespace sie --create-namespace \
  --set hfToken.create=true \
  --set hfToken.value=YOUR_HF_TOKEN \
  -f values-gke.yaml
```

SIE 的生产栈包含：

- **负载均衡网关**（多节点）
- **KEDA 自动扩缩容**（包括缩容到零）
- **Grafana 监控仪表盘**（开箱即用）
- **Terraform 模块**：[GKE](https://github.com/superlinked/terraform-google-sie) / [EKS](https://github.com/superlinked/terraform-aws-sie) / [AKS](https://github.com/superlinked/terraform-azure-sie)

本地开发和生产集群用的是同一套 SDK 代码，只改 `base_url`。**所有组件 Apache 2.0。**

---

## MCP 包：让 Claude 直接调用

`packages/sie_mcp/` 是一个 MCP 服务器实现，可以把 SIE 集群暴露给 Claude Code 或其他 MCP 客户端。用途之一：把文档处理（PDF → Markdown）这类重 token 操作卸载到 SIE 集群，节省 Agent 的上下文 token。

---

## 生态集成

SIE 已经有 9 个框架和向量库的集成：

**框架**：LangChain、LlamaIndex、Haystack、DSPy、CrewAI  
**向量库**：Chroma、Qdrant、Weaviate、LanceDB

配置方式统一：把 LangChain 的 `OpenAIEmbeddings(base_url=...)` 里的 URL 换成 SIE 的地址，模型名换成 SIE 支持的模型 ID，其余代码不变。

---

## 它解决的根本问题

SIE 的核心假设是：**Agent 系统的基础设施碎片化是一个被低估的问题**。

工程团队花大量时间维护多个独立的模型服务——每个服务有自己的部署流程、监控配置、扩缩容规则、依赖管理。当任何一个服务出问题时，需要独立排查。当需要切换模型时，需要修改多处配置。

统一推理引擎的方向不是新的，但 SIE 的差异化在于：
1. **OpenAI 兼容**：现有代码最小改动
2. **任务覆盖全面**：不只是嵌入，还有 OCR、实体抽取、内容安全
3. **生产栈完整**：不只是服务，还有自动扩缩容、监控、Terraform
4. **Apache 2.0**：商业使用无顾虑

对于需要在自己云上运行模型（数据主权、成本控制、延迟优化）的团队，这是一个值得评估的选择。

---

## 数据一览

| 属性 | 值 |
|---|---|
| Stars | 2,286（2026-07-21） |
| 创建时间 | 2023-11-07 |
| 语言 | Python |
| 协议 | **Apache 2.0** |
| API 兼容 | OpenAI |
| 支持模型数 | 100+ |
| 模型加载策略 | 按需 + LRU 淘汰 |
| 生产部署 | Helm + Terraform（GKE/EKS/AKS） |
| 自动扩缩容 | KEDA（含缩容到零） |
| 框架集成 | LangChain, LlamaIndex, Haystack, DSPy, CrewAI |
| 向量库集成 | Chroma, Qdrant, Weaviate, LanceDB |
| SDK | Python + TypeScript |
| MCP 支持 | 有（`packages/sie_mcp/`） |

© 2026 Author: Mycelium Protocol

<!--EN-->

## SIE: One Inference Cluster for Your Entire Agent Stack

**GitHub**: [superlinked/sie](https://github.com/superlinked/sie) · ⭐ 2,286 · Python · Apache 2.0  
**Docs**: [superlinked.com/docs](https://superlinked.com/docs)

### The Problem: Agent Infrastructure Fragmentation

A typical RAG + Agent system runs multiple separate model services: an embedding server, a reranker, an OCR service, an entity extraction service, a content safety filter, and an LLM service. Six services, six deployment pipelines, six monitoring configs, six autoscaling policies. Any one failing affects the whole pipeline.

SIE's answer: put everything into one cluster, expose it all through a single OpenAI-compatible API.

### Five Agent Task Types, One API

| Task | Function | Default Models |
|---|---|---|
| **Search** | Embed + match + rerank | bge-m3, SPLADE-v3, ColBERT v2, Qwen3-reranker |
| **Document to Markdown** | PDF/Office/scans → clean markdown | GLM-OCR, MinerU, PaddleOCR-VL, Docling |
| **Structured Output** | Schema-valid JSON, extracted or generated | GLiNER2, NuNER-zero, Qwen3.6-27B |
| **Guard Content** | Safety verdict + probability threshold | Granite-Guardian-2B |
| **Agent Loop** | Plan steps + tool calling, streaming | Qwen3.6-27B |

All endpoints follow the OpenAI shape: `/v1/embeddings`, `/v1/chat/completions`, `/v1/completions`, `/v1/responses`. Existing code only needs a `base_url` change.

### On-Demand Loading + LRU Eviction

SIE doesn't load all models into VRAM at startup. It loads on first call, caches warm, and evicts the least-recently-used model when VRAM fills. 100+ models configured; first call per model takes minutes to download, subsequent calls return in milliseconds.

### SDK: Three Tasks in Three Lines

```python
from sie_sdk import SIEClient
client = SIEClient("http://localhost:8080")

# Embeddings
result = client.encode("sentence-transformers/all-MiniLM-L6-v2", Item(text="Hello world"))
# → dense vector shape (384,)

# Reranking
scores = client.score("cross-encoder/ms-marco-MiniLM-L-6-v2", query, candidates)
# → ranked list with scores

# Entity extraction
result = client.extract("urchade/gliner_multi-v2.1", Item(text="Tim Cook is CEO of Apple."), labels=["person","organization"])
# → [{'text': 'Tim Cook', 'label': 'person', 'score': 0.992}]
```

SDK available in Python and TypeScript (`@superlinked/sie-sdk`).

### Local → Production: Same Code

**Local (Apple Silicon or Linux)**:
```bash
pip install "sie-server[local]" && sie-server serve
# or Docker for NVIDIA GPU
```

**Production (one Helm command)**:
```bash
helm upgrade --install sie-cluster oci://ghcr.io/superlinked/charts/sie-cluster \
  --namespace sie --create-namespace \
  -f values-gke.yaml  # or values-aws.yaml / values-aks.yaml
```

Full production stack: load-balancing gateway, KEDA autoscaling (scale to zero), Grafana dashboards, Terraform for GKE/EKS/AKS. All Apache 2.0.

### Ecosystem

**Frameworks**: LangChain, LlamaIndex, Haystack, DSPy, CrewAI  
**Vector stores**: Chroma, Qdrant, Weaviate, LanceDB  
**MCP**: `packages/sie_mcp/` exposes cluster capabilities to Claude and other MCP clients (useful for offloading document conversion to save agent tokens)

### What SIE Solves

The core bet: agent infrastructure fragmentation is an underrated problem. Teams spend significant time maintaining separate model services with independent deployment pipelines, monitoring configs, and autoscaling rules. SIE's differentiation: OpenAI-compatible API (minimum code changes), comprehensive task coverage beyond just embeddings (OCR, entity extraction, safety), complete production stack, and Apache 2.0 license. For teams needing self-hosted models (data sovereignty, cost control, latency optimization), worth evaluating.

© 2026 Author: Mycelium Protocol
