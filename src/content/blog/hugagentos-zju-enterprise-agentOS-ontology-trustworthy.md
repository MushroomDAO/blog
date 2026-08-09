---
title: "HugAgentOS：浙大出品的企业级 AgentOS，用领域本体做 Agent 推理的控制平面"
titleEn: "HugAgentOS: ZJU's Enterprise AgentOS Using Domain Ontology as the Agent Reasoning Control Plane"
description: "浙大 REAL 实验室开源 HugAgentOS，把领域本体（Domain Ontology）从知识存储升级为可执行控制平面——三引擎 Harness（技能+编排+记忆）+ 策略门控执行 + 可追溯审计，一行命令本地部署，无需 Docker。"
descriptionEn: "Zhejiang University's REAL Lab open-sources HugAgentOS, upgrading domain ontology from a knowledge store to an executable control plane — a three-engine harness (skills + orchestration + memory), policy-gated execution, and traceable audit. One command to deploy locally, no Docker required."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["企业Agent", "AgentOS", "本体论", "RAG", "MCP", "浙大", "开源", "可信AI", "ReAct", "知识图谱"]
heroImage: "../../assets/images/hugagentos-zju-enterprise-agentOS-ontology-trustworthy-banner.jpg"
---

> **GitHub**：[ZJU-REAL/HugAgentOS](https://github.com/ZJU-REAL/HugAgentOS)  
> **机构**：浙江大学 REAL 实验室  
> **在线体验**：[app.hugagentos.com](https://app.hugagentos.com)  
> **许可**：Apache 2.0 + 附加条款（禁止作为竞争性多租户 SaaS 运营）  
> **安装**：`curl -fsSL https://raw.githubusercontent.com/ZJU-REAL/HugAgentOS/main/install.sh | bash`

---

## 一句话定位

HugAgentOS 是企业 Agent 的操作系统底座，核心思路是：**把领域本体（Domain Ontology）从知识存储升级为可执行的控制平面**——Agent 的每一次推理、每一个行动计划，都要经过本体的语义对齐和策略门控，违规的不是静默失败，而是返回规则 + 证据 + 修复指导。

这不是又一个套 LLM 的聊天应用，也不是简单包装的 RAG 工具。它在解答一个更难的问题：**企业里的 AI Agent 怎么让人信任？**

---

## 为什么"本体"是关键

大多数 Agent 框架对"知识"的处理方式是：放进向量库，检索时拿出来，塞进 prompt。这有个根本问题——模型在做决策时不知道哪些概念是业务红线，哪些行动合不合规，哪些关系跨越了权限边界。

HugAgentOS 的方案是把领域本体（Ontology）做成**编译时和运行时都有效的控制层**：

| 阶段 | 本体的作用 |
|---|---|
| **构建时** | 验证新建的 Skill、Tool、Sub-Agent 是否符合领域概念和行动契约 |
| **启动时** | 语义对齐——把相关领域规则注入 Skill、Memory 引擎 |
| **运行时** | 每个候选计划过确定性规则检查；高风险需证据审查；违规返回具体原因和修复建议 |
| **执后** | 审计和执行记录变成版本化本体提案，需人工审查，可回滚 |

这个治理环不是为了让 Agent 变慢，是为了让 Agent 在企业场景里能被审计、被信任、被监管。

---

## 架构：三引擎 + 本体控制平面

```
用户/渠道
  ↓
ChatRun + 流式工作流
  ↓
三引擎 Harness ───────────────────────────────────────
  Skill Engine ←→ Orchestration Engine ←→ Memory Engine
                        ↓
                  候选计划/行动
                        ↓
          ┌─── 确定性本体规则检查 ←── 领域本体控制平面
          │           │
     低风险合规   检查点/高风险
          ↓           ↓
       门控执行    证据审查 → 批准 → 门控执行
                       ↓
                  违规: 拒绝 + 规则 + 证据 + 修复指导
                        ↓
                  可追溯审计 → 治理本体提案 → 人工审查
```

**Skill Engine**：加载本体验证过的结构化指令和脚本，来自内置 Skill、Marketplace 或个人 Skill。  
**Orchestration Engine**：ReAct 工具编排，Plan Mode 规划，SSE 流式响应，支持深度思考模式。  
**Memory Engine**：三层记忆——L1 关系型（SQLite/PG）+ 可选 Milvus 向量 + 可选 Neo4j 图谱。

---

## 技术栈

| 层 | 技术 |
|---|---|
| Agent 运行时 | AgentScope 2.0, ReAct, MCP |
| 后端 | Python, FastAPI, SQLAlchemy, Alembic |
| 前端 | React 19, TypeScript, Vite, Zustand, Ant Design |
| 数据/状态 | SQLite 或 PostgreSQL 15，进程内状态或 Redis 7，本地文件 |
| 可选记忆 | Milvus 2.4, Neo4j 5 Community, mem0 |
| 部署 | 单命令本地安装、Docker Compose、Nginx |

---

## 核心功能（社区版完整清单）

**Agentic Chat + Plan Mode**：SSE 流式输出，ReAct 工具编排，深度思考，可继续的流，可追溯引用。

**私有知识库 RAG**：文档摄入和分块，混合向量 + 关键词检索，可选重排序，知识隔离。

**个人子 Agent**：创建聚焦角色的子 Agent，通过自动路由或 `@` 提及协作。

**MCP 工具生态**：8 种内置工具——网页搜索、页面抓取、知识检索、图表、报告、批处理、自动化、Skill 管理。

**Agent Skills**：结构化指令 + 脚本扩展 Agent，有内置 Skill、Skill Marketplace 和个人 Skill 三个来源。

**自动化 + 批处理**：自然语言创建定时任务，或把一个工作流批量应用到 Excel/Word/文件列表。

**沙箱 + Artifacts**：本地子进程或轻量容器沙箱，生成图表、报告、Office 文件、网页、数据画布。

**三层个人记忆**：L1 个人档案存关系型数据库，可选 Milvus 向量记忆和 Neo4j 图谱记忆。

**数据画布**：在对话内直接检查和编辑结构化数据，分析和结果留在同一工作区。

---

## 一行命令安装（个人单机，无需 Docker）

```bash
curl -fsSL https://raw.githubusercontent.com/ZJU-REAL/HugAgentOS/main/install.sh | bash
```

安装器做了什么：
1. Clone 到 `~/.hugagent/source`
2. 创建隔离 Python 环境并安装依赖
3. 构建 Web 应用
4. 打开首次运行向导（创建管理员 + 连接 LLM API）

需要：Python 3.11+、Node.js 20+、Git、任意 OpenAI 兼容 API 或本地模型。Linux 无预编译 ripgrep wheel 时还需 Rust toolchain。

```bash
# 再次启动
~/.hugagent/venv/bin/hugagent
# 默认地址 http://127.0.0.1:3001，初始账号密码都是 admin
```

Docker Compose 部署（团队/生产）：见 [docker-compose.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/deployment/docker-compose.md)。

---

## 社区版 vs 企业版

| 社区版（CE）| 企业版新增 |
|---|---|
| Agentic Chat, Plan Mode, 个人子 Agent | 团队、组织 Agent、权限矩阵 |
| 8 种通用 MCP 工具、个人 Skill + Marketplace | 行业数据工具、组织治理、Skill 审查 |
| 私有知识库 + 三层个人记忆 | 公共知识管理、记忆审计 |
| 自动化、批处理、个人数据画布 | 组织计费、用量报告、画布协作 |
| 轻量沙箱、本地文件 | 持久沙箱、云存储、离线交付 |
| 本地账号 + Powered-by 署名 | SSO、合规审计、完整白标 |

CE 已经是个完整的个人 Agent 工作区。CE 的限制是不能以竞争性 SaaS 形式对外运营（Apache 附加条款），自用和企业内部部署不受限制。

---

## 与同类开源平台对比

| | **HugAgentOS** | **Open WebUI** | **AnythingLLM** | **Dify** |
|---|---|---|---|---|
| 机构 | 浙大 REAL | 开源社区 | Mintplex Labs | Langgenius |
| 核心差异 | 本体治理控制平面 | 模型前端 UI | 文档 RAG 工作区 | 工作流可视化 |
| 企业治理 | ✅ 本体门控+审计 | ✗ | 基础 | 基础 |
| 知识图谱记忆 | ✅ Neo4j 可选 | ✗ | ✗ | ✗ |
| Agent 运行时 | AgentScope 2.0 | 基础 | 基础 | LangChain |
| 无 Docker 安装 | ✅ | ✅ | ✅ | 需要 |

HugAgentOS 的独特性在于**本体 + 可信推理**这条线。如果你需要的是"企业合规 + 审计 + 多团队协作 + 知识治理"，它比其他框架更有系统性考虑。如果你只需要一个好用的本地 RAG 聊天，Open WebUI 更轻。

---

## 核心判断

这个项目的赌注是：**企业 AI 落地的核心障碍不是能力，是信任和治理**。当前大多数 Agent 框架把治理当成"事后监控"，HugAgentOS 把本体治理做成了"执行前的确定性检查"——这是架构层面的不同。

浙大 REAL Lab 做这个方向有其学术背景（本体工程、知识图谱是 REAL 的传统方向），但把学术研究做成可部署产品是另一回事。它现在有了 React 19 前端、一键安装脚本、完整文档（中英双语），这是工程化成熟度的标志。

50 Stars，刚开源两天，但架构思路值得关注——尤其是正在经历"AI 怎么满足合规要求"压力的企业场景。

---

## 参考资源

- **GitHub**：[ZJU-REAL/HugAgentOS](https://github.com/ZJU-REAL/HugAgentOS)
- **在线体验**：[app.hugagentos.com](https://app.hugagentos.com)
- **快速开始**：[document/en/getting-started/quick-start.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/getting-started/quick-start.md)
- **架构概览**：[document/en/architecture/overview.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/architecture/overview.md)
- **AgentScope 2.0**：[github.com/modelscope/agentscope](https://github.com/modelscope/agentscope)

© 2026 Author: Mycelium Protocol

<!--EN-->

> **GitHub**: [ZJU-REAL/HugAgentOS](https://github.com/ZJU-REAL/HugAgentOS)  
> **Institution**: Zhejiang University REAL Lab  
> **Live Demo**: [app.hugagentos.com](https://app.hugagentos.com)  
> **License**: Apache 2.0 + Additional Terms (prohibits competitive multi-tenant SaaS operation)  
> **Install**: `curl -fsSL https://raw.githubusercontent.com/ZJU-REAL/HugAgentOS/main/install.sh | bash`

---

## One-Line Summary

HugAgentOS is the operating system foundation for enterprise agents. Its core idea is: **upgrade domain ontology from a knowledge store to an executable control plane** — every inference step and every action plan an agent takes must pass through ontological semantic alignment and policy gating. Violations don't fail silently; they return the rule, evidence, and remediation guidance.

This is not yet another LLM-wrapped chat application, nor a simplistic RAG wrapper. It answers a harder question: **how do you make enterprise AI agents trustworthy?**

---

## Why "Ontology" Is the Key

Most agent frameworks handle "knowledge" this way: dump it into a vector store, retrieve it at query time, stuff it into a prompt. This has a fundamental flaw — the model, when making decisions, has no idea which concepts are business red lines, which actions are out of compliance, or which relationships cross permission boundaries.

HugAgentOS's approach is to turn the domain ontology into a **control layer that is effective at both compile time and runtime**:

| Phase | Role of Ontology |
|---|---|
| **Build time** | Validates that new Skills, Tools, and Sub-Agents conform to domain concepts and action contracts |
| **Startup time** | Semantic alignment — injects relevant domain rules into the Skill and Memory engines |
| **Runtime** | Every candidate plan passes through deterministic rule checks; high-risk actions require evidence review; violations return specific reasons and remediation suggestions |
| **Post-execution** | Audit and execution records become versioned ontology proposals, subject to human review and rollback |

This governance loop is not meant to slow agents down — it exists to make agents auditable, trustworthy, and governable in enterprise contexts.

---

## Architecture: Three-Engine Harness + Ontology Control Plane

```
User / Channel
  ↓
ChatRun + Streaming Workflow
  ↓
Three-Engine Harness ───────────────────────────────────────
  Skill Engine ←→ Orchestration Engine ←→ Memory Engine
                        ↓
                  Candidate Plans / Actions
                        ↓
          ┌─── Deterministic Ontology Rule Check ←── Domain Ontology Control Plane
          │           │
     Low-risk compliant   Checkpoint / High-risk
          ↓           ↓
       Gated Execution    Evidence Review → Approved → Gated Execution
                       ↓
                  Violation: Reject + Rule + Evidence + Remediation Guidance
                        ↓
                  Traceable Audit → Governance Ontology Proposal → Human Review
```

**Skill Engine**: Loads ontology-validated structured instructions and scripts, sourced from built-in Skills, the Marketplace, or personal Skills.  
**Orchestration Engine**: ReAct tool orchestration, Plan Mode planning, SSE streaming responses, supports deep thinking mode.  
**Memory Engine**: Three-tier memory — L1 relational (SQLite/PG) + optional Milvus vector + optional Neo4j graph.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Runtime | AgentScope 2.0, ReAct, MCP |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Frontend | React 19, TypeScript, Vite, Zustand, Ant Design |
| Data / State | SQLite or PostgreSQL 15, in-process state or Redis 7, local file |
| Optional Memory | Milvus 2.4, Neo4j 5 Community, mem0 |
| Deployment | Single-command local install, Docker Compose, Nginx |

---

## Core Features (Community Edition Full List)

**Agentic Chat + Plan Mode**: SSE streaming output, ReAct tool orchestration, deep thinking, resumable streams, traceable citations.

**Private Knowledge Base RAG**: Document ingestion and chunking, hybrid vector + keyword retrieval, optional reranking, knowledge isolation.

**Personal Sub-Agents**: Create focused-role sub-agents, collaborate via auto-routing or `@` mention.

**MCP Tool Ecosystem**: 8 built-in tools — web search, page scraping, knowledge retrieval, charts, reports, batch processing, automation, and Skill management.

**Agent Skills**: Structured instructions + scripts to extend agents, with three sources: built-in Skills, Skill Marketplace, and personal Skills.

**Automation + Batch Processing**: Create scheduled tasks in natural language, or apply a workflow in batch to Excel/Word/file lists.

**Sandbox + Artifacts**: Local subprocess or lightweight container sandbox, generates charts, reports, Office files, web pages, and data canvases.

**Three-Tier Personal Memory**: L1 personal profile stored in relational database, optional Milvus vector memory and Neo4j graph memory.

**Data Canvas**: Inspect and edit structured data directly within the conversation; analysis and results remain in the same workspace.

---

## One-Command Install (Personal / Single Machine, No Docker)

```bash
curl -fsSL https://raw.githubusercontent.com/ZJU-REAL/HugAgentOS/main/install.sh | bash
```

What the installer does:
1. Clones to `~/.hugagent/source`
2. Creates an isolated Python environment and installs dependencies
3. Builds the web application
4. Opens the first-run wizard (create admin account + connect LLM API)

Requirements: Python 3.11+, Node.js 20+, Git, any OpenAI-compatible API or local model. On Linux, a Rust toolchain is also required when no precompiled ripgrep wheel is available.

```bash
# Start again
~/.hugagent/venv/bin/hugagent
# Default address http://127.0.0.1:3001, default username and password are both admin
```

Docker Compose deployment (team/production): see [docker-compose.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/deployment/docker-compose.md).

---

## Community Edition vs Enterprise Edition

| Community Edition (CE) | Enterprise Edition Additions |
|---|---|
| Agentic Chat, Plan Mode, personal sub-agents | Teams, organizational agents, permission matrix |
| 8 general MCP tools, personal Skills + Marketplace | Industry data tools, organizational governance, Skill review |
| Private knowledge base + three-tier personal memory | Public knowledge management, memory audit |
| Automation, batch processing, personal data canvas | Organizational billing, usage reports, canvas collaboration |
| Lightweight sandbox, local files | Persistent sandbox, cloud storage, offline delivery |
| Local accounts + Powered-by attribution | SSO, compliance audit, full white-label |

CE is already a complete personal agent workspace. The CE restriction is that it cannot be operated externally as a competitive SaaS (Apache additional terms); self-use and internal enterprise deployment are unrestricted.

---

## Comparison with Similar Open-Source Platforms

| | **HugAgentOS** | **Open WebUI** | **AnythingLLM** | **Dify** |
|---|---|---|---|---|
| Institution | ZJU REAL | Open-source community | Mintplex Labs | Langgenius |
| Core Differentiator | Ontology governance control plane | Model frontend UI | Document RAG workspace | Workflow visualization |
| Enterprise Governance | ✅ Ontology gating + audit | ✗ | Basic | Basic |
| Knowledge Graph Memory | ✅ Neo4j optional | ✗ | ✗ | ✗ |
| Agent Runtime | AgentScope 2.0 | Basic | Basic | LangChain |
| No-Docker Install | ✅ | ✅ | ✅ | Required |

HugAgentOS's uniqueness lies in the **ontology + trustworthy reasoning** line. If what you need is "enterprise compliance + audit + multi-team collaboration + knowledge governance," it has more systematic consideration than other frameworks. If you just need a good local RAG chat, Open WebUI is lighter.

---

## Core Assessment

This project's bet is: **the core barrier to enterprise AI adoption is not capability — it is trust and governance**. Most current agent frameworks treat governance as "after-the-fact monitoring." HugAgentOS makes ontology governance a "deterministic check before execution" — this is a difference at the architectural level.

ZJU REAL Lab has the academic background for this direction (ontology engineering and knowledge graphs are REAL's traditional research areas), but turning academic research into a deployable product is another matter entirely. It now has a React 19 frontend, a one-click install script, and complete documentation (both Chinese and English) — markers of engineering maturity.

50 Stars, just open-sourced two days ago, but the architectural thinking is worth watching — especially for enterprises under pressure to answer "how does AI meet compliance requirements?"

---

## References

- **GitHub**: [ZJU-REAL/HugAgentOS](https://github.com/ZJU-REAL/HugAgentOS)
- **Live Demo**: [app.hugagentos.com](https://app.hugagentos.com)
- **Quick Start**: [document/en/getting-started/quick-start.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/getting-started/quick-start.md)
- **Architecture Overview**: [document/en/architecture/overview.md](https://github.com/ZJU-REAL/HugAgentOS/blob/main/document/en/architecture/overview.md)
- **AgentScope 2.0**: [github.com/modelscope/agentscope](https://github.com/modelscope/agentscope)

© 2026 Author: Mycelium Protocol
