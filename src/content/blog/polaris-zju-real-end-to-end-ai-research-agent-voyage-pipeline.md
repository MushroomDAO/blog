---
title: "Polaris：浙大 REAL 实验室开源端到端 AI 科研智能体——从文献调研到论文投稿六阶段全自动"
titleEn: "polaris-zju-real-end-to-end-ai-research-agent-voyage-pipeline"
description: "ZJU-REAL/Polaris 是浙江大学 REAL 实验室开源的端到端 AI 科研平台，六阶段流水线：文献调研 Wiki → 想法生成 → Elo 辩论评审 → GPU 实验执行 → LaTeX 论文写作 → 引用核验。核心设计是确定性代码做繁重工作、LLM 只做判断，Voyage 任务可跨天持久化续跑并设人工审批门禁，Navigator/Helm/Sextant 三引擎驱动，MCP 工具层对外开放，Docker Compose 部署。"
descriptionEn: "ZJU-REAL/Polaris is an open-source end-to-end AI research platform by Zhejiang University's REAL Lab. Six-stage pipeline: literature research wiki → idea generation → Elo debate review → GPU experiment execution → LaTeX paper writing → citation verification. Core design: deterministic code for heavy lifting, LLM reserved for judgment calls; Voyage tasks persist and resume across days with human approval gates; Navigator/Helm/Sextant three-engine agent core; MCP tool layer exposed externally; Docker Compose deployment."
pubDate: "2026-08-18"
updatedDate: "2026-08-18"
category: "Tech-News"
tags: ["AI科研", "科研自动化", "Agent", "浙大", "端到端", "MCP", "论文写作", "实验室工具"]
heroImage: "../../assets/images/polaris-zju-real-end-to-end-ai-research-agent-voyage-pipeline-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：ZJU-REAL/Polaris  
产品文档：zju-real.github.io/Polaris  
团队：浙江大学 REAL 实验室  
许可证：Apache 2.0  
在线演示：101.37.174.109:8080（guest / zjuguest123，只读）

---

AI 辅助科研的工具有很多——文献阅读助手、代码生成、论文润色——但几乎所有工具都只覆盖研究流程的某一个片段，彼此孤立，产出无法流转到下一步。

Polaris 想把这些片段连成一条完整的流水线：从文献调研开始，经过想法生成、同行评审、GPU 实验、论文写作，一直到投稿前的引用核验。**每一步的产出是下一步的输入，整条流水线由智能体驱动，关键决策由人来拍板。**

---

## 一、设计原则：确定性代码做重活，LLM 只做判断

这是 Polaris 最值得注意的设计决策：

> 繁重的工作（爬取、解析、去重、指标解析、引用匹配）是确定性代码。LLM 保留给需要判断的地方：打分、合成、起草、评审。

这个分工让整个系统保持：**便宜**（大量工作不调 LLM）、**可复现**（相同输入稳定输出）、**可审计**（每一步都有代码层面的可检验性）。

与之对比，纯 LLM 驱动的研究 Agent 容易在繁重的数据处理步骤上产生幻觉或不一致——把这些步骤还给确定性代码，LLM 的判断才有可靠的输入。

---

## 二、六阶段研究流水线

```
文献调研 → 想法生成 → 想法评审 → 实验 → 论文写作 → 论文评审 → 投稿
```

每个箭头是一个人工审批门禁，你决定产出是否达标、是否进入下一阶段。

### 阶段一：文献调研 Wiki

从 OpenAlex、Semantic Scholar、arXiv 摄入论文。从「锚论文」开始滚雪球式追踪引用，按「方向库」的纳入配置（通过 AI 结构化访谈建立：陈述、目标、范围、排除条件）打相关性分。

每篇论文编译成一个跨链接的 Wiki 页面：TL;DR、方法、可复用想法、概念回链。

关键设计：**一篇论文全平台共享一个 Wiki 页面**——编译提示不带方向库陈述，同一篇论文对所有用户读出一样的摘要；一个概念在两篇以上论文引用它之后才被提升为条目。新 arXiv 论文通过每日 Feed 进入，是所有库同步的唯一入口。

### 阶段二：想法生成（Idea Forge）

基于文献 Wiki 生成研究想法，关联到具体的文献证据。

### 阶段三：Elo 辩论评审

AI 评审员两两辩论想法，通过 Elo 排名确定优先级。**想法晋级**是一个人工审批门禁——排行供你参考，你拍板哪些进入实验阶段。

### 阶段四：实验执行（连接真实 GPU）

通过 asyncssh 连接实验室 GPU 服务器（SSH 密钥静态加密），在真实硬件上执行实验。智能体生成代码、部署、运行、解析日志指标，失败时切换思路再跑。

**GPU 预算使用**是一个人工审批门禁：智能体会停下来把预算方案摆给你看，不点头就不往下走。

### 阶段五：论文写作（LaTeX）

在线多文件 LaTeX 编辑器，支持 CRDT 协同编辑（Yjs）和服务端 tectonic 编译。智能体起草内容时**绑定真实指标和真实引用**——不是从语言模型的记忆里生成数字，而是从实验记录里读取。一键刷新参考文献，自动更新主 TeX 文件。

### 阶段六：论文评审（含引用核验）

每条引用都逐一核验：存在性和论点支持性，对照方向库、Semantic Scholar、OpenAlex 三重来源；每个数字都对账实验记录。**一条编造引用直接打回**，不会悄悄通过。

---

## 三、Voyage：持久化任务循环

Voyage 是 Polaris 的任务执行单元——一个持久化的、可续跑的、人工审批门禁的智能体任务。

核心特性：
- **跨天不丢状态**：任务可以运行数小时甚至数天，中间可以停止，状态落库，之后从断点继续
- **审批门禁**：任务在关键节点暂停，把预算和方案给你看，等你批准后才继续
- **全程留痕**：每个计划、动作、判定、重试都落库，界面上可见，事后可回放

### 三引擎智能体核心

Voyage 的内部由三个角色驱动：

**Navigator（规划）**：起草并修订步骤清单。计划随证据生长，遇到新信息更新计划，而不是推倒重来——避免了「幻觉计划 → 执行时崩溃」的问题。

**Helm（执行）**：一次执行一个动作，异常不外抛，失败转化为可推理的观察——「这步失败了，怎么继续」，而不是直接中断整个任务。

**Sextant（校验）**：逐步核对验收标准，**确定性检查先行**（退出码、产物存在、指标达标），模型只在规则无法判定时出场。这是「AI 辅助校验」而非「AI 独立校验」的设计——用代码能检查的绝不交给模型。

---

## 四、PolarisBuddy：贯穿全程的 AI 助手

类似 Claude Code 风格的多轮工具循环助手，在每个页面常驻。

- 流式输出（SSE），带工具调用卡片和内联图表
- 三种模式：`chat`（问答）、`plan`（先提议再执行）、`goal`（循环推进直到达成目标）
- 在同样的 Navigator/Helm/Sextant 结构下运行，步骤被校验而非只是生成
- 可以把工作分派给子 Agent
- 问候语从真实 SQL 统计数据里生成，而不是模型凭空编造

---

## 五、技能系统与 MCP 开放接口

**技能系统（两层）**：

*Voyage 技能*：版本化、可组合的 `guidance`（指引）、`rubric`（评分标准）、`persona`（角色）、`workflow`（工作流）包，在智能体提示词的具名位置注入。有发布-审批-安装-评分的市场机制；每个 Voyage 快照它使用的技能版本，保证可复现。

*Agent 技能*：SKILL.md 格式，三层渐进披露——目录里一行描述、模型调用 `skill_load` 工具时才拉取正文、附件按需读取——让模型决定加载什么，提示词前缀保持可缓存。

**MCP 工具层**：

同一套只读工具集（文献、知识、项目状态、手稿、外部搜索）同时对内（智能体循环）和对外（MCP Server，支持 Streamable HTTP 和 stdio）暴露，可以在 Claude Code、Codex、Cursor 里直接调用 Polaris 的研究资产。有自检和在线 playground。严格只读，隔离到项目级别。

---

## 六、技术架构

| 层级 | 技术选型 |
|------|---------|
| 前端 | React 18 + TypeScript 5 + Vite 5，TanStack Query，CodeMirror 6，Yjs（CRDT），react-pdf，KaTeX |
| 桌面客户端 | Electron（macOS / Windows / Linux），通过 `app://` 协议复用 Web Bundle |
| 后端 | FastAPI（全异步）+ SQLAlchemy 2 + Alembic + fastapi-users（JWT） |
| 任务队列 | ARQ（Redis 作为 Broker），长任务脱离请求线程执行 |
| 数据 | PostgreSQL 16（含 pgvector，嵌入空间按模型隔离防混淆）+ Redis 7 |
| 远程执行 | asyncssh 连接 GPU 服务器，SSH 密钥 Fernet 加密存储 |
| LaTeX | tectonic 服务端编译，带缓存宏卷 |
| LLM | 多 Provider 抽象（OpenAI 兼容 + Anthropic），数据库路由表按阶段映射模型和推理强度 |
| 部署 | Docker Compose（postgres / redis / api / worker / frontend） |

LLM 路由设计值得单独说一下：管理员设置全局路由（每个研究阶段用哪个 Provider、哪个模型、什么推理强度），用户可以覆盖自己的设置。内置的 Fake Provider 在生产环境通过结构性限制禁用，不会因配置错误意外打开。

---

## 七、部署与桌面客户端

```bash
# Docker Compose 一键起服务
git clone https://github.com/ZJU-REAL/Polaris.git
cd Polaris
docker compose up -d
```

桌面客户端支持 macOS / Windows / Linux，从 Releases 下载安装包（`.dmg`、`.exe`、`.AppImage`），CI 在每个 `v*` tag 时自动构建。**注意：构建未签名/未公证**——macOS 需要 `xattr -dr com.apple.quarantine`，Windows 需要跳过 SmartScreen，Linux 需要 `libnss3 libgtk-3-0 libasound2`。

---

## 八、为什么值得关注

**科研流水线的完整性**：覆盖了从文献到投稿的全流程，而不是某一环节的点工具。这让「端到端可审计」成为可能。

**人工门禁设计**：Polaris 不是一个「全自动」幻想——它在真正需要人判断的地方（想法晋级、GPU 预算、论文投稿）强制停下来等人。这是一个更现实的「AI-人协作」模型。

**确定性先行**：LLM 只在代码无法判断的地方出场，这让系统在文献处理和数字核验上有可信度，而不只是「看起来对」。

**MCP 开放**：研究资产（文献库、项目状态、手稿）通过 MCP 对外暴露，让 Claude Code 等工具可以调用 Polaris 的知识，是 AI 工具互联的一个实际案例。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Polaris: ZJU-REAL's Open-Source End-to-End AI Research Agent — Six Stages from Literature to Submission

*by Mycelium Protocol*

---

GitHub: ZJU-REAL/Polaris  
Docs: zju-real.github.io/Polaris  
Team: Zhejiang University REAL Lab  
License: Apache 2.0  
Live demo: 101.37.174.109:8080 (guest / zjuguest123, read-only)

---

AI research tools abound — literature readers, code generators, paper polishers — but almost all cover only one fragment of the research lifecycle, isolated from the next step.

Polaris connects these fragments: literature survey → idea generation → peer review → GPU experiments → paper writing → citation verification → submission. **Each stage's output feeds the next; the agent drives the pipeline; humans make the calls that matter.**

---

### Core Design Principle: Deterministic Code Does the Heavy Lifting

> The heavy lifting (crawling, parsing, deduplication, metric parsing, citation matching) is deterministic code. LLMs are reserved for judgment calls: scoring, synthesis, drafting, and review.

This keeps runs cheap, reproducible, and auditable. Pure LLM-driven research agents tend to hallucinate or produce inconsistent results in data-heavy processing steps — returning those to deterministic code gives the LLM reliable inputs and verifiable outputs.

---

### The Six-Stage Pipeline

**Stage 1: Literature Research Wiki** — Ingests papers from OpenAlex, Semantic Scholar, arXiv. Snowballs from anchor papers, scores relevance against a direction library (built through a structured AI interview: statement, goals, scope, exclusions). Each paper compiles to a cross-linked wiki page: TL;DR, method, reusable ideas, concept backlinks. One wiki per paper, shared platform-wide — the compile prompt carries no library statement, so the same paper reads identically regardless of who opened it.

**Stage 2: Idea Generation (Idea Forge)** — Generates research ideas grounded in literature evidence.

**Stage 3: Elo Debate Review** — AI reviewers debate ideas pairwise; Elo ranking surfaces priorities. Idea promotion is a human approval gate.

**Stage 4: Experiment Execution** — Connects to real GPU servers via asyncssh (SSH keys Fernet-encrypted at rest). Agent generates code, deploys, runs, parses metrics, switches strategy on failure. GPU budget approval is a human gate.

**Stage 5: Paper Writing (LaTeX)** — Online multi-file LaTeX with collaborative CRDT editing (Yjs) and server-side tectonic compilation. Agent drafts content **bound to real metrics and real citations from experiment records**, not hallucinated from model memory.

**Stage 6: Paper Review** — Each citation verified for existence and argument support against the library, Semantic Scholar, and OpenAlex. Each number fact-checked against the experiment record. **One fabricated citation fails the review.**

---

### Voyage: Persistent Agent Runs

Voyage is Polaris's execution unit — a persisted, resumable, human-gated agent task that can span hours or days without losing state. Every plan, action, judgment, and retry is logged, visible in the UI, and replayable after the fact.

**Three-engine agent core:**

- **Navigator (Planning)**: Drafts and revises step lists. Plans grow with evidence — update on new information, don't restart from scratch.
- **Helm (Execution)**: One action at a time. Exceptions don't propagate — failures become observable facts for the next step.
- **Sextant (Verification)**: Checks acceptance criteria step by step. **Deterministic checks first** (exit codes, artifact existence, metric thresholds); LLM only for what code can't judge.

---

### MCP Integration and Skills

**MCP tool layer**: The same read-only tool set (literature, knowledge, project state, manuscripts, external search) is exposed internally to the agent loop and externally as an MCP server (Streamable HTTP and stdio). Claude Code, Codex, and Cursor can call Polaris's research assets directly. Strictly read-only, isolated per project.

**Skills system (two layers)**: Voyage skills are versionable, composable guidance/rubric/persona/workflow packs injected into agent prompts; each Voyage snapshots the skill versions it used. Agent skills follow SKILL.md's three-level progressive disclosure — one-line description in catalog, body fetched on demand via `skill_load`, keeping the prompt prefix cacheable.

---

### Why This Matters

**Full lifecycle coverage**: Literature to submission, not just one fragment. Makes end-to-end auditability possible.

**Human gates at the right moments**: Not "fully automatic" — forced pauses at idea promotion, GPU budget, and submission. A realistic AI-human collaboration model.

**Deterministic-first verification**: LLM only where code can't judge. This gives the system credible citations and numbers, not just plausible-looking output.

**MCP openness**: Research assets exposed as MCP tools, connectable to Claude Code and other agents — a practical case of AI tool interoperability.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
