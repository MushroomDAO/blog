---
title: "LLM Wiki 的知识更新问题，Tencent 用 Agent Memory 这样解——TencentDB-Agent-Memory 拆解"
titleEn: "How Tencent Solved LLM Wiki's Knowledge Update Problem with Agent Memory — TencentDB-Agent-Memory Teardown"
description: "TencentCloud/TencentDB-Agent-Memory，26.9K stars，TypeScript，团队级 Agent 记忆中枢。在 Karpathy LLM Wiki 模式上加了三件事：异步持续摄取解决知识失效、四种记忆资产（Chat Memory/Skill/LLM-Wiki/CodeGraph）解决单一知识库局限、per-agent 绑定+ACL 解决团队共享权限。PersonaMem 留存率从 48% 升至 76%。"
descriptionEn: "TencentCloud/TencentDB-Agent-Memory, 26.9K stars, TypeScript, team-level Agent memory hub. Builds on Karpathy's LLM Wiki pattern with three key additions: async continuous ingestion for knowledge freshness, four memory asset types (Chat Memory/Skill/LLM-Wiki/CodeGraph) beyond single knowledge bases, and per-agent binding with ACL for team sharing. PersonaMem retention improves from 48% to 76%."
pubDate: "2026-09-19"
updatedDate: "2026-09-19"
category: "Research"
tags: ["agent-memory", "LLM-Wiki", "knowledge-graph", "RAG", "Tencent", "team-AI", "memory-hub", "MCP"]
heroImage: "../../assets/images/tencentdb-agent-memory-llm-wiki-knowledge-update-team-memory-hub-banner.jpg"
---

> 📌 GitHub：https://github.com/TencentCloud/TencentDB-Agent-Memory
> Stars：26,965 | License：Other（Tencent）| 语言：TypeScript
> 创建：2026-04-07 | 更新：2026-09-19

---

LLM Wiki 是 Karpathy 提出的一个概念：不要每次查询都从头 RAG 一遍，而是让 LLM 把文档编译成一个持久、互链的 Wiki，查询直接走 Wiki，速度快、上下文精准。

原版实现（`nashsu/llm_wiki`，19.7K stars）把这个想法做成了一个桌面应用，但有一个没有解决的核心问题：**Wiki 建好了之后怎么保鲜**？文档在更新，代码在演进，知识库很快就会过期。

TencentDB 团队在这个基础上做了 TencentDB-Agent-Memory（26.9K stars）。他的朋友称之为"LLM Wiki v2"——不是官方发版，而是同一个模式的工程化升级：解决更新问题，顺带把记忆类型从一种扩展到四种，从个人工具变成团队级基础设施。

---

## 原版 LLM Wiki：解决了什么，没解决什么

Karpathy 的 LLM Wiki 模式核心是三层结构：

```
原始文档（不可变）
  ↓ LLM 编译
Wiki 页面（结构化、互链）
  ↓ 查询
Agent 得到精确上下文
```

对比传统 RAG：RAG 每次查询都重新从原始文档检索，没有累积；LLM Wiki 把知识编译一次，后续查询直接走 Wiki，效率更高，上下文也更干净。

`nashsu/llm_wiki` 把这套做成了桌面应用，有 SHA256 增量缓存（文件没变就跳过）、Louvain 社区检测、Adamic-Adar 图权重。功能完整，但有一个系统性缺口：**知识更新是手动触发的**。文档改了需要手动重新摄取，没有持续保鲜机制，团队共享也没有解决。

---

## TencentDB-Agent-Memory 加了什么

### 1. 四种记忆资产

原版只有"文档→Wiki"这一种。TencentDB-Agent-Memory 把记忆分成四类：

**Chat Memory（对话记忆）**：四层结构
- L0：原始对话，完整上下文
- L1：从对话中提取的事实、偏好、约束、事件
- L2：围绕项目/场景组织的知识块
- L3：长期画像和稳定模式

**Skill（技能）**：从已完成任务中提取的可复用工作流，包含版本、资源文件、触发边界、执行步骤和验证规则。默认私有，评审后可共享给团队成员——"学一次，团队永久复用"。

**LLM-Wiki（文档知识库）**：把产品文档、设计规范、运维手册编译成带链接图的结构化页面。这就是 Karpathy 模式的直接实现，但加了异步持续摄取。

**CodeGraph（代码图谱）**：对代码库建立符号、文件、调用关系、影响路径的索引，让 Agent 在修改代码前做影响分析，而不是纯文本搜索。

---

### 2. 知识更新问题的具体解法

原版 LLM Wiki 的知识失效根因在于：摄取是一次性的，没有持续运行的更新管道。

TencentDB-Agent-Memory 的解法：

**后台异步摄取管道**：文档和代码变更在后台持续处理，不需要手动触发。Wiki 和 CodeGraph 资产有处理状态，显示为 `pending → processing → ready`，完成后自动可用。

**按需召回，不是整体注入**：不把整个 Wiki 塞进上下文窗口，而是通过 `/v3/tools/call` API 在需要时按需取。这样知识更新后，下次调用自然拿到新版本。

**源文件联动**：每个 Wiki 页面的 frontmatter 里有 `sources[]` 字段，记录哪些原始文档贡献了这个页面。源文件变更时，相关页面精确重新编译，不用全量重建。

---

### 3. 团队级架构

个人 LLM Wiki 和团队用之间有巨大的工程差距。TencentDB-Agent-Memory 用三层解决：

```
Memory Hub（控制面板）
  ↓ 团队管理、资产评审、绑定配置
Memory Core（资产存储与检索）
  ↓ L0-L3 分层、Fixed Binding + ACL
Memory Proxy（Agent 翻译器）
  ↓ 把任意 Agent 的 base URL 转换成统一协议
  ↓
Claude Code | DeepSeek Harness | Hermes | OpenClaw | CodeBuddy...
```

**per-agent 绑定（Fixed Binding + ACL）**：不同 Agent 拿到不同的记忆组合。例如：Scout Agent 拿市场研究 Wiki + Chat Memory；Builder Agent 拿 CodeGraph + Skill 库。权限默认 private，共享需要显式操作（`team` 可见 或 `restricted` 指定用户/角色/Agent）。

**检索预算**：每次检索有上限（条目数、字符数、超时），防止把整个团队的知识库塞爆上下文窗口。

---

## 安装与启动

三个服务一条命令启动：

```bash
git clone https://github.com/TencentCloud/TencentDB-Agent-Memory.git
cd TencentDB-Agent-Memory/deploy/global-images
cp .env.example .env
# 编辑 .env，填写 LLM 参数
./start-all.sh
# Memory Hub 访问地址：http://localhost:8125
```

接入 Claude Code（通过 Memory Proxy，零代码改动）：

```bash
# 把 Claude Code 的 base URL 指向 Memory Proxy
# Proxy 自动把请求翻译成 Memory Core 的统一协议
```

支持的 Agent 框架：Claude Code、DeepSeek Harness、Hermes、OpenClaw、CodeBuddy，以及任何 OpenAI 兼容接口。

数据迁移：从 v1.x/v2.x 升级到 v3.0+ 有专门的迁移工具。

---

## 基准数据

PersonaMem（用户理解留存率）：

| 配置 | 留存率 |
|------|--------|
| 未使用 Agent Memory | 48% |
| 启用 TencentDB-Agent-Memory | 76% |
| 提升 | **+59%** |

PersonaMem 测量的是 Agent 在多轮对话中能否准确保持对用户偏好、决策历史、项目上下文的理解。从 48% 到 76% 的跳升主要来自 L1-L2 Chat Memory 的持久化——不再依赖上下文窗口内的信息，记忆可以跨会话延续。

---

## 与原版 LLM Wiki 的对比

| 维度 | nashsu/llm_wiki（原版） | TencentDB-Agent-Memory |
|------|------------------------|------------------------|
| **知识范围** | 文档 | 文档 + 代码 + 对话 |
| **更新机制** | 手动触发，增量缓存 | 后台异步持续摄取 |
| **记忆类型** | 1 种（Wiki） | 4 种（Chat/Skill/Wiki/CodeGraph） |
| **团队支持** | 个人 | 团队级、角色权限、资产评审 |
| **跨框架** | 单个 Agent | Claude Code/DSH/Hermes/… 统一 |
| **注入方式** | 整体注入上下文 | 按需 API 召回，有检索预算 |
| **技术栈** | Tauri + React + Rust | TypeScript + Docker |

---

## 核心设计判断

**为什么用"编译"而不是"检索"**：RAG 每次查询都在原始文档里找，没有累积，也没有知识之间的关系。LLM Wiki 的"编译"思路是：让 LLM 先把知识组织成结构化形态，建立实体关系图，后续查询走这个已经组织好的知识图谱。代价是首次建库时间，收益是后续查询质量和效率。

**为什么四种资产必须分开**：Chat Memory、Skill、Wiki、CodeGraph 的遗忘速度和更新频率完全不同。对话偏好更新快（每轮对话都在变），代码图谱更新中等（每次提交），运维文档更新慢（月度）。把它们合并进一个池子会导致快更新频率干扰慢更新频率的资产。

**知识更新的真正难点不是技术**：是判断"哪个旧页面需要重新编译"。TencentDB-Agent-Memory 通过 `sources[]` frontmatter 反向映射解决：源文件变了，系统知道哪些页面依赖它，精确触发重建，不需要全量扫描。

---

## 局限

- License 是 Tencent 自有，不是标准 OSI 认证开源协议，商业使用前需确认条款
- PersonaMem +59% 是内部基准，测试场景和数据集未完全公开
- MongoDB 后端是实验性的（默认禁用），生产环境只经过有限测试
- 团队功能需要自托管完整 Memory Hub，运维成本高于个人工具

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/TencentCloud/TencentDB-Agent-Memory
> Stars: 26,965 | License: Other (Tencent) | Language: TypeScript
> Created: 2026-04-07 | Updated: 2026-09-19

---

LLM Wiki is a pattern Karpathy proposed: instead of running RAG from scratch on every query, have the LLM compile documents into a persistent, interlinked Wiki once. Queries then go against the Wiki directly — faster, and with cleaner context.

The original implementation (`nashsu/llm_wiki`, 19.7K stars) built this into a desktop app, but left one core problem unsolved: **how do you keep the Wiki fresh?** Documents evolve, code changes — a compiled knowledge base goes stale fast.

TencentDB's team built TencentDB-Agent-Memory (26.9K stars) on this foundation. Some have called it "LLM Wiki v2" — not an official release, but an engineering upgrade of the same pattern: solving the update problem, extending memory types from one to four, and evolving from a personal tool to team-level infrastructure.

---

## Original LLM Wiki: What It Solved and What It Didn't

Karpathy's LLM Wiki pattern has a three-layer structure:

```
Raw documents (immutable)
  ↓ LLM compilation
Wiki pages (structured, interlinked)
  ↓ query
Agent gets precise context
```

Compared to RAG: RAG re-retrieves from raw documents on every query with no accumulation; LLM Wiki compiles knowledge once, then queries go against the organized structure — higher efficiency, cleaner context.

`nashsu/llm_wiki` realized this as a desktop application with SHA256 incremental caching, Louvain community detection, and Adamic-Adar graph weighting. Functionally complete, but with one systemic gap: **knowledge updates are manually triggered.** Changed documents require manual re-ingestion, there's no continuous freshness mechanism, and team sharing isn't addressed.

---

## What TencentDB-Agent-Memory Adds

### 1. Four Memory Asset Types

The original has one type: documents → Wiki. TencentDB-Agent-Memory defines four:

**Chat Memory**: Four-layer structure
- L0: Raw conversations with full context
- L1: Extracted facts, preferences, constraints, events
- L2: Knowledge blocks organized around projects/scenarios
- L3: Long-term profiles and stable patterns

**Skill**: Reusable workflows extracted from completed tasks, with versions, resource files, trigger boundaries, execution steps, and validation rules. Private by default, shareable after review — "learn once, the team uses forever."

**LLM-Wiki**: Product docs, design specs, and ops runbooks compiled into structured pages with link graphs. This is the direct Karpathy-pattern implementation, now with async continuous ingestion.

**CodeGraph**: An indexed representation of codebases with symbols, files, call relationships, and impact paths. Lets agents perform impact analysis before modifying code rather than relying on text search.

---

### 2. Solving the Knowledge Update Problem

The original LLM Wiki's staleness problem comes from a fundamental design: ingestion is one-shot, with no continuous update pipeline.

TencentDB-Agent-Memory's solution:

**Background async ingestion pipeline**: Document and code changes are processed continuously in the background without manual triggering. Wiki and CodeGraph assets have processing states: `pending → processing → ready`, automatically available after completion.

**On-demand recall, not wholesale injection**: Rather than injecting the entire Wiki into the context window, knowledge is retrieved on demand via the `/v3/tools/call` API. When knowledge updates, the next call naturally gets the new version.

**Source traceability**: Every Wiki page's frontmatter carries a `sources[]` field recording which documents contributed to it. When a source changes, dependent pages are precisely recompiled without full rebuilds.

---

### 3. Team-Level Architecture

Personal LLM Wiki and team use require different engineering entirely. TencentDB-Agent-Memory solves this in three layers:

```
Memory Hub (Control Panel)
  ↓ team management, asset review, binding config
Memory Core (Asset Storage & Retrieval)
  ↓ L0-L3 layering, Fixed Binding + ACL
Memory Proxy (Agent Translator)
  ↓ converts any agent's base URL to unified protocol
  ↓
Claude Code | DeepSeek Harness | Hermes | OpenClaw | CodeBuddy...
```

**Per-agent binding (Fixed Binding + ACL)**: Different agents get different memory combinations. Scout Agent gets market research Wiki + Chat Memory; Builder Agent gets CodeGraph + Skill library. Permissions default to private; sharing requires explicit action.

**Retrieval budgets**: Each retrieval call is capped by item count, character limits, and timeout to prevent flooding the context window with an entire team's knowledge base.

---

## Installation

Three services start with one command:

```bash
git clone https://github.com/TencentCloud/TencentDB-Agent-Memory.git
cd TencentDB-Agent-Memory/deploy/global-images
cp .env.example .env
# Edit .env with LLM parameters
./start-all.sh
# Memory Hub at http://localhost:8125
```

Claude Code integration is zero-code: point the base URL to the Memory Proxy, which automatically translates requests into the unified Memory Core protocol.

Supported agent frameworks: Claude Code, DeepSeek Harness, Hermes, OpenClaw, CodeBuddy, and any OpenAI-compatible interface.

---

## Benchmark

PersonaMem (user understanding retention rate):

| Configuration | Retention |
|--------------|-----------|
| Without Agent Memory | 48% |
| With TencentDB-Agent-Memory | 76% |
| Improvement | **+59%** |

PersonaMem measures whether agents can accurately maintain understanding of user preferences, decision history, and project context across multi-turn conversations. The jump from 48% to 76% primarily comes from L1-L2 Chat Memory persistence — no longer dependent on in-window context, memory persists across sessions.

---

## Comparison with Original LLM Wiki

| Dimension | nashsu/llm_wiki | TencentDB-Agent-Memory |
|-----------|----------------|------------------------|
| **Knowledge scope** | Documents | Docs + code + conversations |
| **Update mechanism** | Manual, incremental cache | Background async continuous ingestion |
| **Memory types** | 1 (Wiki) | 4 (Chat/Skill/Wiki/CodeGraph) |
| **Team support** | Individual | Team-level, roles, asset review |
| **Multi-framework** | Single agent | Claude Code/DSH/Hermes/… unified |
| **Injection style** | Wholesale context injection | On-demand API recall with retrieval budgets |
| **Tech stack** | Tauri + React + Rust | TypeScript + Docker |

---

## Design Rationale

**Why "compile" instead of "retrieve"**: RAG re-searches raw documents on every query with no accumulation and no inter-knowledge relationships. LLM Wiki's compilation approach: let the LLM organize knowledge into structured form first, building entity relationship graphs. The cost is initial build time; the gain is query quality and efficiency afterward.

**Why four asset types must stay separate**: Chat Memory, Skill, Wiki, and CodeGraph have completely different staleness and update frequencies. Conversation preferences update every turn; code graphs update per commit; ops documentation updates monthly. Merging them into one pool lets high-frequency updates pollute low-frequency assets.

**The real difficulty of knowledge update isn't technical**: it's deciding which old pages need recompilation. TencentDB-Agent-Memory solves this through `sources[]` frontmatter reverse mapping: when a source file changes, the system knows exactly which pages depend on it and triggers precise rebuilds without full scans.

---

## Limitations

- License is Tencent's own — not a standard OSI-approved open-source license; verify terms before commercial use
- PersonaMem +59% is an internal benchmark; test scenarios and datasets are not fully public
- MongoDB backend is experimental (disabled by default) with limited production testing
- Team features require self-hosting the full Memory Hub, with significantly higher operational overhead than personal tools

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
