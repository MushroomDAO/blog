---
title: "Yuxi：把 RAG、知识图谱、多 Agent、MCP 装进一个自部署平台"
titleEn: "Yuxi: RAG, Knowledge Graph, Multi-Agent, and MCP in One Self-Hosted Platform"
description: "xerrors/Yuxi ⭐6591，可私有部署的多租户知识智能体平台，统一 RAG、知识图谱（Milvus+Neo4j）、LangGraph 多 Agent 编排、MCP/Skills、沙盒工作区和团队权限管理，FastAPI+Vue3，Docker Compose 一键部署，MIT 许可。"
descriptionEn: "xerrors/Yuxi ⭐6591 — a self-hosted, multi-tenant knowledge agent platform unifying RAG, knowledge graph (Milvus+Neo4j), LangGraph multi-agent orchestration, MCP/Skills, sandbox workspace, and team permission management. FastAPI + Vue 3, Docker Compose, MIT."
pubDate: 2026-08-31
updatedDate: 2026-08-31
category: "Tech-News"
tags: ["RAG", "knowledge graph", "multi-agent", "MCP", "self-hosted", "open source", "LangGraph", "FastAPI", "Vue", "AI platform"]
heroImage: "../../assets/images/yuxi-self-hosted-knowledge-agent-rag-graph-multi-agent-mcp-banner.jpg"
author: "Mycelium Protocol"
---

## 一个已知的困境

企业或团队想用 AI 处理内部知识，会遇到同一批问题：RAG 系统是独立的，知识图谱是另一套，多 Agent 编排又是第三套框架，权限管理和团队协作根本就没有……最终要么拼了七八个工具，要么用 SaaS 但数据不能出门。

**Yuxi**（`xerrors/Yuxi`）把这些能力整合到一个可以私有部署的平台里：知识库检索、知识图谱、多 Agent 编排、MCP 扩展、沙盒工作区、多租户权限——一个工作区，全部打通。

2年多迭代，⭐ **6591**，983 forks，v0.7.1 正式版已发布。

---

## 六个核心模块

### 1. 统一智能体工作台

用户在同一个对话界面里完成提问、知识引用、任务执行和文件交付。

- 用 `@` 快速引入知识库、文件或特定 Skill
- 实时可视化任务拆解步骤、工具调用状态、Token 消耗
- 点击来源溯源核对，或直接预览和下载生成的文件
- 长任务有人工审批卡片——涉及修改文件、调用外部高危接口时等待确认

---

### 2. 知识库与可追溯 RAG

把文档变成 Agent 可以检索的结构化知识，并且让每个答案都能追溯到原文。

- 支持 PDF、Word、PPT、Excel、Markdown 等格式
- 内置 **MinerU、PaddleX、RapidOCR** 深度解析引擎，精准提取图文、表格并切分为高质量 Chunk
- 支持配置 Embedding 和 Rerank 算法，有独立的多路召回测试工作台
- 内置 RAG 效果评估：构建问答评估集，批量跑评测，输出检索召回率、答案相关性指标
- 支持连接 Dify、Notion 等外部知识库，免去二次迁移

---

### 3. 知识图谱与知识导图

从文档里自动抽取"实体-关系"网络，让 Agent 不只检索文本，还能推理关系。

- 文档解析时自动执行实体识别和关系抽取，写入 **Milvus + Neo4j**
- 可按关键词搜索实体，点击节点查看属性，高亮探索关联子图
- 根据文件层级和元数据自动生成结构化知识导图

---

### 4. 多智能体与扩展生态

一个 Agent 可以组合：模型 + 知识库 + MCP + Skills + SubAgents。

- 主 Agent 把复杂任务拆解后，多个 SubAgent **异步并行执行**（分别检索不同领域、撰写报告不同章节）
- 原生兼容 **MCP（Model Context Protocol）**，在线安装 Skills（支持 skills.sh 和魔搭社区）
- Skill 可在线查看和编辑，可配置权限和依赖
- 渐进式工具加载：需要时才解析和加载，不预先把几十个工具全塞进上下文

---

### 5. 沙盒工作区与文件产物

Agent 生成的东西不再只是消息，而是可以继续使用的文件：

- 每个对话有隔离的文件系统沙盒
- 支持文件在线预览和下载
- 适合生成报告、代码、数据分析结果等需要交付的内容

---

### 6. 团队治理与运行管理

面向真实的多人场景：

- **多租户**：按用户、部门和共享范围管理知识库、Agent、Skills 和模型
- 支持 Langfuse Dataset 评估完整 Agent 任务
- 模型配置、API Key 管理、Dashboard 运行监控

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 · Vite · Ant Design · G6（图谱可视化）|
| 后端 | FastAPI · LangGraph · ARQ worker |
| 存储 | PostgreSQL · Redis · MinIO · Milvus · Neo4j |
| 文档处理 | MinerU · PaddleX · RapidOCR |
| 部署 | Docker Compose |

---

## 快速启动

```bash
git clone --branch v0.7.2.beta2 --depth 1 https://github.com/xerrors/Yuxi.git
cd Yuxi

# Linux/macOS
./scripts/init.sh

# Windows PowerShell
.\scripts\init.ps1

# 启动（全量）
docker compose up --build -d

# 轻量模式（不需要知识库/图谱/评估时）
make up-lite
```

初始化脚本会创建 `.env`、读取 API Key，并为 JWT、API Key 派生和沙盒 provisioner 生成安全密钥。启动后访问 [http://localhost:5173](http://localhost:5173)，按页面引导初始化超级管理员。

**注意**：从 v0.7.1 升级前需先阅读[生产部署与升级文档](https://xerrors.github.io/Yuxi/advanced/deployment)，有备份和迁移步骤。

---

## 为什么值得关注

Yuxi 做的不是"多个工具拼在一起的前端"——RAG、图谱、多 Agent 和 MCP 是在同一个 Agent 执行路径上打通的：Agent 可以在一次任务里同时检索向量知识库、查询图谱关系、调用外部 MCP 工具、派出 SubAgent 并行工作，结果落进沙盒文件系统，可以直接预览和下载。

两年多 6000+ Star，说明这条路线有真实的需求。对于需要掌控数据和权限、又想要完整 Agent 能力的团队，Yuxi 是目前少见的把这些放在一个私有部署平台里的完整选项。

---

**GitHub**: [xerrors/Yuxi](https://github.com/xerrors/Yuxi) ⭐6591  
**文档**: [xerrors.github.io/Yuxi](https://xerrors.github.io/Yuxi/)  
**演示视频**: [Bilibili](https://www.bilibili.com/video/BV1erE26iEgv/)

<!--EN-->

## Yuxi: RAG, Knowledge Graph, Multi-Agent, and MCP in One Self-Hosted Platform

Teams trying to use AI over internal knowledge hit the same wall: the RAG system is one tool, the knowledge graph is another stack, multi-agent orchestration is a third framework, and permissions don't exist anywhere. You either stitch together seven tools or use SaaS and lose data control.

**Yuxi** (`xerrors/Yuxi`) puts these capabilities in one self-deployable platform: knowledge retrieval, knowledge graph, multi-agent orchestration, MCP extensions, sandbox workspace, and multi-tenant permissions — one workspace, all connected.

Two-plus years of iteration, ⭐**6,591**, 983 forks, v0.7.1 stable released.

### Six Core Modules

**Unified Agent Workspace**  
Users complete queries, knowledge lookups, task execution, and file delivery in one conversation interface.

- `@`-mention to pull in knowledge bases, files, or specific Skills
- Real-time visualization of task decomposition, tool call status, and token consumption
- Click any citation to trace back to the source, or preview and download generated files
- Human approval cards for high-risk operations (file writes, external API calls)

**Knowledge Base and Traceable RAG**  
Turn documents into structured knowledge agents can retrieve, with every answer traceable to source.

- PDF, Word, PPT, Excel, Markdown, and more
- Built-in **MinerU, PaddleX, RapidOCR** deep parsing — accurate text/table extraction, high-quality chunking
- Configurable Embedding and Rerank algorithms, with a multi-recall test workbench
- Built-in RAG evaluation: build a QA benchmark, batch run tests, get recall rate and answer relevance metrics
- Connect external knowledge bases (Dify, Notion) without data migration

**Knowledge Graph and Mind Map**  
Automatically extract entity-relationship networks from documents so agents can reason about relationships, not just retrieve text.

- Entity recognition and relation extraction during document parsing, written to **Milvus + Neo4j**
- Search entities by keyword, click nodes for attributes, highlight and explore related subgraphs
- Auto-generate structured mind maps from file hierarchy and metadata

**Multi-Agent and Extension Ecosystem**  
One agent can compose: model + knowledge base + MCP + Skills + SubAgents.

- Main agent decomposes complex tasks, multiple SubAgents run **async in parallel** (separate research threads, parallel report sections)
- Native **MCP (Model Context Protocol)** compatibility, online Skill installation (skills.sh and ModelScope community)
- Skills are editable online with permission and dependency configuration
- Progressive tool loading: tools are parsed and loaded on demand, not pre-stuffed into context

**Sandbox Workspace and File Artifacts**  
Agent outputs are files you can continue using, not just messages.

- Isolated filesystem sandbox per conversation
- Online preview and download of generated files
- Designed for reports, code, data analysis — anything that needs to be delivered

**Team Governance and Operations**  
Built for real multi-person use:

- **Multi-tenancy**: manage knowledge bases, agents, Skills, and models by user, department, and sharing scope
- Langfuse Dataset integration for full agent task evaluation
- Model configuration, API key management, runtime Dashboard

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 · Vite · Ant Design · G6 (graph visualization) |
| Backend | FastAPI · LangGraph · ARQ worker |
| Storage | PostgreSQL · Redis · MinIO · Milvus · Neo4j |
| Doc processing | MinerU · PaddleX · RapidOCR |
| Deployment | Docker Compose |

### Quick Start

```bash
git clone --branch v0.7.2.beta2 --depth 1 https://github.com/xerrors/Yuxi.git
cd Yuxi
./scripts/init.sh          # creates .env, generates security keys

docker compose up --build -d    # full stack
# or
make up-lite                     # lightweight (no graph/evaluation)
```

Open [http://localhost:5173](http://localhost:5173) and follow the setup wizard. API docs at [http://localhost:5050/docs](http://localhost:5050/docs).

**Upgrade note**: upgrading from v0.7.1 requires following the [production deployment guide](https://xerrors.github.io/Yuxi/advanced/deployment) — backup and migration steps are required.

### Why It Matters

Yuxi isn't a UI stitching multiple tools together. RAG, knowledge graph, multi-agent, and MCP are integrated in the same agent execution path: one task can simultaneously retrieve from a vector knowledge base, query graph relationships, call external MCP tools, dispatch SubAgents in parallel, and land results in a sandboxed file system for preview and download.

6,000+ stars over two years shows real demand for this pattern. For teams that need data and permission control alongside full agent capabilities, Yuxi is one of the few complete options that puts all of this in a single self-hosted platform.

**GitHub**: [xerrors/Yuxi](https://github.com/xerrors/Yuxi) ⭐6591  
**Docs**: [xerrors.github.io/Yuxi](https://xerrors.github.io/Yuxi/)  
**Demo video**: [Bilibili](https://www.bilibili.com/video/BV1erE26iEgv/)
