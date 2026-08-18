---
title: "PipesHub：开源企业 AI 上下文层——把知识图谱、权限感知 RAG、MCP 工具和 Agent 统一到一个自托管系统"
titleEn: "pipeshub-ai-enterprise-context-layer-knowledge-graph-rag-mcp"
description: "pipeshub-ai/pipeshub-ai 是一个开源的企业 AI 上下文层（Context Layer），把企业内部的知识连接、权限管控、知识图谱检索、50+ 数据源连接器、RAG 问答、Agent 构建、MCP 工具、代码执行沙箱统一到一个自托管系统。支持任意 LLM、部署在自己的 VPC 内、数据不出境，同时提供精确块级引用和来源溯源能力。Docker Compose 一键安装。"
descriptionEn: "pipeshub-ai/pipeshub-ai is an open-source Enterprise AI Context Layer that unifies enterprise knowledge connectivity, permission-aware access control, knowledge graph retrieval, 50+ source connectors, RAG Q&A, agent building, MCP tools, and a code execution sandbox into one self-hosted system. Supports any LLM, deploys in your own VPC with zero data egress, and provides precise block-level citations with source provenance. One-command Docker Compose install."
pubDate: "2026-08-18"
updatedDate: "2026-08-18"
category: "Tech-News"
tags: ["企业AI", "RAG", "知识图谱", "开源", "自托管", "MCP", "Agent", "权限管控", "上下文层"]
heroImage: "../../assets/images/pipeshub-ai-enterprise-context-layer-knowledge-graph-rag-mcp-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：pipeshub-ai/pipeshub-ai  
定位：开源企业 AI 上下文层（Context Layer）  
许可证：开源（Apache 2.0）  
部署：Docker Compose，交互式安装脚本

---

企业 AI 应用有一个共性问题：**数据孤岛**。

你有 Slack 里的讨论、Confluence 里的文档、Notion 里的规划、Google Drive 里的文件、Jira 里的 Issue，还有自己的数据库——它们分散在几十个系统里，权限各不相同，格式各不相同。每次构建一个 AI 助手，都要重新解决「怎么把这些数据连起来、怎么控制谁能看什么、怎么让 AI 知道答案来自哪里」这三个问题。

PipesHub 想把这三个问题的答案固化成一个开源基础设施层——一次部署，所有 AI 应用共享。

---

## 一、核心定位：Context Layer，不是 AI 应用

PipesHub 不是一个 AI 问答产品，它是给 AI 应用提供上下文能力的**基础层**。

这个区别很重要。你不是在用 PipesHub 替代 ChatGPT 或 Claude——你是在用 PipesHub 让你的 AI 应用（无论是什么 LLM）能安全地访问企业内部知识。

它提供的能力分四层：

```
[应用层]  你自己的 AI 应用 / Agent / 问答机器人
     ↓ 调用 API / SDK / MCP 工具
[PipesHub]
  ├── 上下文检索（权限感知 RAG + 知识图谱）
  ├── 数据连接（50+ 连接器，实时/定时索引）
  ├── 安全治理（权限继承，块级引用溯源）
  └── 执行能力（Agent 构建，代码沙箱）
     ↑ 接入任意 LLM（OpenAI / Claude / 本地模型）
[你的企业数据]  Confluence / Slack / Drive / Notion / Jira / ...
```

---

## 二、五个核心能力

### 1. 权限感知检索（Permission-Aware Search）

这是 PipesHub 的关键差异点。

大多数 RAG 系统的问题：把所有数据都索引进向量库，然后按语义相关度检索——但没有权限控制。财务文档和 HR 文件和技术文档混在一起，任何有访问权的人都能通过 AI 问到本来不该看到的内容。

PipesHub 的解法：**在检索层继承源数据的访问权限**。Slack 频道的权限、Google Drive 文件的分享权限、Confluence 页面的空间权限——都映射到 PipesHub 的权限模型里。用户通过 AI 能查到的内容，和他们直接去源系统能看到的内容，是一致的。

### 2. 知识图谱检索（Knowledge Graph Retrieval）

纯向量检索的局限：只能找到语义相近的段落，无法理解文档之间的关系。

PipesHub 用 Neo4j 或 ArangoDB 构建知识图谱，把文档之间的引用关系、概念之间的关联、实体之间的连接都建模成图。检索时，不只是找相似段落，还能沿图遍历——「这个决策文档引用了哪个技术规范」「这个 Bug 报告关联了哪些 PR 和测试用例」。

这对企业知识的深度问答很重要：企业知识库里大量的价值不在单篇文档里，而在文档与文档的关联里。

### 3. 精确块级引用（Explainable Answers）

AI 给出的答案可以追溯到具体来源的具体段落。不是「来自 Confluence」，而是「来自 Confluence > 产品文档 > 2026-Q2 路线图 > 第 3 段」，并附上原始文本块。

这在企业场景里不是体验优化，而是信任基础——没有可验证的引用，AI 的回答在工作流里没有可信度。

### 4. 50+ 企业连接器

覆盖主流企业协作工具：

**知识库类**：Confluence、Notion、SharePoint、Gitbook  
**文件存储**：Google Drive、OneDrive、Dropbox、S3  
**沟通工具**：Slack、Teams、Gmail  
**项目管理**：Jira、Linear、Asana、GitHub Issues  
**代码托管**：GitHub、GitLab、Bitbucket  
**CRM/销售**：Salesforce、HubSpot  
**数据库**：MySQL、PostgreSQL、MongoDB（直接查询）

支持格式：PDF（含扫描件）、Word、Excel、PPT、CSV、Markdown、HTML、Google Docs/Sheets/Slides、图片（含图表识别）。

连接器支持实时同步（Webhook）和定时索引两种模式。

### 5. Agent 构建 + 代码执行沙箱

除了检索，PipesHub 还提供：

- **No-Code Agent Builder**：可视化构建 Agent，定义工作流和动作，不需要写代码
- **代码执行沙箱**：Agent 可以生成并运行 Python 代码，在安全隔离环境里分析数据、生成报表和图表
- **MCP 工具**：PipesHub 的能力可以暴露为 MCP（Model Context Protocol）工具，让外部 Agent（Claude Code、Cursor 等）调用

---

## 三、技术架构

PipesHub 是一个中等复杂度的微服务系统，关键选型：

### 存储层（可选多种）

| 用途 | 选项 |
|------|------|
| 知识图谱 | Neo4j 或 ArangoDB |
| 向量库 | Qdrant / OpenSearch / Redis |
| 文档存储 | MongoDB |
| 对象存储 | 本地文件系统 / S3 / Azure Blob |
| KV / 缓存 | Redis / etcd |

### 消息与任务层

- **消息队列**：Kafka 或 Redis Streams（用于连接器数据摄入、索引任务）
- **任务调度**：Celery（定时连接器同步、后台处理）

### 应用层

- **后端 API**：FastAPI（Python）
- **前端**：Next.js（App Router）+ TypeScript + Radix UI
- **LLM 接入**：LangChain（多提供商模型接入，OpenAI / Anthropic / Ollama / 任意兼容 OpenAI API 的模型）
- **Embedding**：sentence-transformers / fastembed
- **文档解析**：pdfplumber + selectolax + markdown-it + openpyxl（默认），可选 Docling 作为高质量替代（通过 `PARSER_BACKEND` 环境变量切换）

### 部署

Docker Compose，交互式安装脚本（`./install.sh`）：
1. 检查 Docker、RAM、磁盘前置条件
2. 选择 **slim**（最小配置）或 **full**（完整配置）
3. 自定义图数据库、消息队列、KV store 选型
4. 自动生成随机密钥和 `.env` 文件
5. 拉取镜像、启动服务栈、等待健康检查通过

一个命令完成，开箱即用。

---

## 四、为什么「上下文层」是比「RAG 框架」更准确的描述

「RAG 框架」这个词现在已经被滥用了——从 LangChain 到 LlamaIndex 到各种向量数据库的 SDK，都叫自己 RAG 框架，但大多数只解决了检索部分。

PipesHub 和它们的区别在于**完整性**：

| 能力 | LangChain / LlamaIndex | 专用向量库（Qdrant 等） | PipesHub |
|------|----------------------|----------------------|---------|
| 数据摄入连接器 | 部分（需自建） | ❌ | ✅ 50+ |
| 权限感知检索 | ❌（需自建） | ❌ | ✅ 内置 |
| 知识图谱 | 部分（需接 Neo4j） | ❌ | ✅ 内置 |
| 块级引用溯源 | 部分 | ❌ | ✅ 内置 |
| No-Code Agent Builder | ❌ | ❌ | ✅ |
| 代码执行沙箱 | ❌ | ❌ | ✅ |
| MCP 工具暴露 | ❌ | ❌ | ✅ |
| 完全自托管 | ✅（框架）| ✅（库）| ✅（系统）|

PipesHub 做的是把这些能力**打包成一个可部署的系统**，而不是一堆需要自己组装的库。对于没有专职 AI 基础设施团队的企业来说，这是更现实的选择。

---

## 五、适用场景

**企业内部知识助手**：员工向 AI 问公司内部的流程、规定、历史决策——AI 答案有来源，有权限控制，不会泄露其他部门的数据。

**技术支持知识库**：产品文档 + Bug 历史 + 工程设计文档，支持工程师或客服快速定位问题。引用具体文档段落，而不是给出模糊答案。

**合规和审计辅助**：金融、医疗等行业需要所有 AI 输出可追溯——「这个答案基于哪个版本的合规文件的哪一条」，PipesHub 的块级引用可以满足这个要求。

**内部 Agent 工作流**：把连接 CRM、写邮件、更新 Jira 等动作组合成 Agent 工作流，在一个有治理的上下文层上执行，不绕过权限控制。

---

## 六、注意事项和局限

**系统复杂度**：完整部署涉及 Neo4j/ArangoDB + MongoDB + Qdrant/Redis + Kafka/Redis Streams + Celery + FastAPI + Next.js，这对运维有一定要求。Slim 模式简化了选型，但仍需要 Docker 环境和足够的内存（建议 16GB+）。

**连接器质量参差不齐**：50+ 连接器是亮点，但各连接器的维护质量和功能完整性差距很大。核心连接器（Google Drive、Slack、Confluence）应该相对稳定，长尾连接器需要社区自己测试。

**图检索的价值依赖数据质量**：知识图谱的优势（跨文档关联检索）需要高质量的文档元数据和一致的结构才能充分发挥。如果企业文档体系本身是混乱的，图检索能做到的有限。

**LangChain 依赖**：LLM 接入层基于 LangChain，这意味着继承了 LangChain 的复杂性和版本迭代包袱。对于需要精确控制 LLM 调用的场景，这一层的抽象可能是障碍。

**Cloud 版本未发布**：完全托管的 PipesHub Cloud 「即将推出」，目前只有自托管方式。对于没有运维能力的小团队，只能等 Cloud 版本或找托管服务。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## PipesHub: Open-Source Enterprise AI Context Layer — Knowledge Graph, Permission-Aware RAG, MCP, and Agents in One Self-Hosted System

*by Mycelium Protocol*

---

GitHub: pipeshub-ai/pipeshub-ai  
Positioning: Open-source Enterprise AI Context Layer  
License: Open-source (Apache 2.0)  
Deployment: Docker Compose with interactive installer

---

Enterprise AI applications share a common problem: **data silos**.

Slack discussions. Confluence docs. Notion plans. Google Drive files. Jira issues. All scattered across dozens of systems with different permissions and different formats. Every time you build an AI assistant, you solve the same three problems from scratch: how to connect all this data, how to control who can see what, and how to tell the AI where its answers actually came from.

PipesHub wants to fix this once — as open-source infrastructure.

---

### Core Positioning: Context Layer, Not an AI App

PipesHub is not an AI Q&A product. It's a **foundation layer** that gives AI applications the ability to access enterprise knowledge safely.

The distinction matters. You don't use PipesHub instead of Claude or GPT — you use PipesHub to let your AI application (whatever LLM) securely access internal knowledge.

```
[Your AI apps / Agents / Chatbots]
         ↓ API / SDK / MCP tools
[PipesHub]
  ├── Context retrieval (permission-aware RAG + knowledge graph)
  ├── Data connectivity (50+ connectors, real-time / scheduled)
  ├── Security governance (permission inheritance, block-level citations)
  └── Execution (agent builder, code sandbox)
         ↑ Any LLM (OpenAI / Claude / local models)
[Enterprise data]  Confluence / Slack / Drive / Notion / Jira / ...
```

---

### Five Core Capabilities

**1. Permission-Aware Search**

Most RAG systems index everything into a vector store and retrieve by semantic similarity — but without access control. HR documents and financial data and engineering specs all pooled together, queryable by anyone with access to the AI.

PipesHub enforces source-level permissions at retrieval time. Slack channel permissions, Google Drive sharing permissions, Confluence space permissions — all mapped into PipesHub's access model. What a user can find through the AI matches exactly what they can see in the source system.

**2. Knowledge Graph Retrieval**

Pure vector search finds semantically similar passages but can't understand document relationships. PipesHub builds a knowledge graph (Neo4j or ArangoDB) that models references between documents, concept associations, entity connections. Retrieval traverses the graph — "which technical spec does this decision doc reference?" — not just find similar paragraphs.

**3. Precise Block-Level Citations**

Every AI answer traces back to the specific paragraph in the specific document. Not "from Confluence" — "from Confluence > Product Docs > 2026-Q2 Roadmap > Paragraph 3," with the original text block. In enterprise workflows, unverifiable AI answers have no credibility. Citations are the trust foundation.

**4. 50+ Enterprise Connectors**

Knowledge bases (Confluence, Notion, SharePoint), file storage (Google Drive, OneDrive, S3), communication (Slack, Teams, Gmail), project management (Jira, Linear, GitHub Issues), code hosting (GitHub, GitLab), CRM (Salesforce, HubSpot), databases (MySQL, PostgreSQL, MongoDB).

File formats: PDF (including scanned), Word, Excel, PowerPoint, CSV, Markdown, HTML, Google Workspace formats, images (with diagram understanding). Audio/video coming soon.

**5. Agent Builder + Code Execution Sandbox**

- No-code visual agent builder for workflow automation
- Safe code execution sandbox for data analysis, report generation, charts
- MCP tool exposure: PipesHub capabilities as MCP tools, callable by external agents (Claude Code, Cursor, etc.)

---

### Tech Stack

| Layer | Options |
|-------|---------|
| Knowledge Graph | Neo4j / ArangoDB |
| Vector Store | Qdrant / OpenSearch / Redis |
| Document Store | MongoDB |
| Blob Storage | Local / S3 / Azure Blob |
| Message Broker | Kafka / Redis Streams |
| Cache / KV | Redis / etcd |
| Task Queue | Celery |
| Backend | FastAPI (Python) |
| Frontend | Next.js + TypeScript + Radix UI |
| LLM Interface | LangChain (multi-provider) |
| Document Parsing | pdfplumber + selectolax (default) / Docling (opt-in) |

Deploy: `git clone → cd deployment/docker-compose → ./install.sh` — interactive wizard handles everything (DB selection, secrets generation, health check wait).

---

### Why "Context Layer" Rather Than "RAG Framework"

Most "RAG frameworks" solve only retrieval. PipesHub packages retrieval + connectors + permissions + knowledge graph + agents + citations into **one deployable system**:

| Capability | LangChain/LlamaIndex | Vector DBs | PipesHub |
|------------|---------------------|-----------|---------|
| 50+ source connectors | partial | ❌ | ✅ |
| Permission-aware retrieval | ❌ (DIY) | ❌ | ✅ |
| Knowledge graph | partial (DIY) | ❌ | ✅ |
| Block-level citations | partial | ❌ | ✅ |
| No-code agent builder | ❌ | ❌ | ✅ |
| Code execution sandbox | ❌ | ❌ | ✅ |
| MCP tool exposure | ❌ | ❌ | ✅ |
| Fully self-hosted | ✅ | ✅ | ✅ |

For enterprises without a dedicated AI infra team, an assembled-for-you system beats a collection of libraries to integrate yourself.

---

### Caveats

**Operational complexity**: Full deployment involves Neo4j + MongoDB + Qdrant + Kafka + Celery + FastAPI + Next.js. Minimum 16 GB RAM recommended. The slim mode simplifies choices but still requires Docker.

**Connector quality variance**: 50+ connectors is impressive, but maintenance quality differs significantly across the long tail. Core connectors (Google Drive, Slack, Confluence) are likely robust; others need testing.

**Graph value requires data quality**: Knowledge graph relationship retrieval only delivers its promise when documents have consistent structure and good metadata. Chaotic document repositories reduce the graph advantage.

**LangChain coupling**: LLM interface layer is LangChain — inherits its complexity and version churn. For fine-grained LLM call control, this abstraction layer may be an obstacle.

**Cloud managed version not yet released**: PipesHub Cloud is "coming soon." Self-hosted only for now.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
