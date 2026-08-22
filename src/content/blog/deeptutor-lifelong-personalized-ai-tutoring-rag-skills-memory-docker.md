---
title: "DeepTutor：终身个性化 AI 家教，真正记住你学到哪了，多 RAG 引擎+长期记忆+Skills 生态，Docker 自托管"
titleEn: "deeptutor-lifelong-personalized-ai-tutoring-rag-skills-memory-docker"
description: "HKUDS/DeepTutor 是香港大学数据科学团队开源的终身个性化 AI 学习工作台，36949 stars，Apache 2.0，Python + Next.js。核心差异：三层长期记忆（L1 轨迹/L2 摘要/L3 综合）真正追踪每个学习者的进度；Chat/Quiz/Research/Visualize/Solve/Mastery Path/沉浸阅读七种模式共用同一个 Agent 循环；多引擎知识库（LlamaIndex/PageIndex/GraphRAG/LightRAG/Obsidian/MarginNote 4）；Skills 社区生态（EduHub/ClawHub）；Partners 系统（Claude Code/Codex/Gemini/Kimi 等 15 个 IM 渠道）；v1.5.16 今日更新；pip 一键安装或 Docker 自托管。"
descriptionEn: "HKUDS/DeepTutor is an open-source lifelong personalized AI learning workspace from Hong Kong University — 36,949 stars, Apache 2.0, Python + Next.js. Key differentiator: three-layer persistent memory (L1 traces / L2 summaries / L3 synthesis) that genuinely tracks each learner's progress. Seven modes (Chat / Quiz / Research / Visualize / Solve / Mastery Path / Immersive Reading) on the same agent loop. Multi-engine knowledge bases (LlamaIndex / PageIndex / GraphRAG / LightRAG / Obsidian / MarginNote 4). Community Skills ecosystem (EduHub / ClawHub). Partners system (Claude Code / Codex / Gemini / Kimi across 15 IM channels). v1.5.16 released today. pip install or Docker self-host."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["AI教育", "个性化学习", "RAG", "长期记忆", "Docker自托管", "Skills", "开源", "多Agent"]
heroImage: "../../assets/images/deeptutor-lifelong-personalized-ai-tutoring-rag-skills-memory-docker-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：HKUDS/DeepTutor  
论文：arxiv.org/abs/2604.26962  
官方文档：deeptutor.info  
许可证：Apache 2.0  
语言：Python 3.11+ + Next.js 16  
Stars：36,949 · Forks：4,632  
最新版本：v1.5.16（2026-08-22）  
机构：香港大学数据科学实验室（HKUDS）

---

## 一、它和通用 AI 问答的本质区别

普通 AI 问答每次对话都从零开始——你问它线性代数，它不知道你上周刚学完矩阵乘法，卡在特征值上。

DeepTutor 的设计核心是**长期记忆**：三层持久化记忆结构让系统真正知道你学到哪一步了，不是靠上下文，而是跨会话的真实追踪。

这就是用户说的「它是真真切切知道你学到哪一步了」的技术底座。

---

## 二、三层记忆体系

| 层级 | 名称 | 内容 |
|------|------|------|
| L1 | 轨迹层 | 每次会话的详细行为记录 |
| L2 | 摘要层 | 从轨迹中提炼的知识状态 |
| L3 | 综合层 | 跨时间的学习模型（你擅长什么、卡在哪里） |

**Memory Graph**：每个记忆声明都能追溯到具体的证据来源，不是黑盒推断，而是可检查、可编辑的知识图谱。

---

## 三、七种学习模式，共用同一个 Agent 循环

DeepTutor 的独特架构：Chat、Quiz、Research、Visualize、Solve、Mastery Path、沉浸阅读这七种模式运行在**同一个 Agent 引擎**上。切换模式时，学习上下文完整保留——不是换了个工具，是换了个目标。

| 模式 | 用途 |
|------|------|
| **Chat** | 对话式问答，结合知识库检索 |
| **Quiz** | AI 出题，自动批改，结果进入 Question Bank |
| **Research / Deep Research** | 多步骤研究，跨文档综合 |
| **Visualize** | 概念可视化（Chart.js/SVG/Mermaid） |
| **Solve** | 解题，带过程展示 |
| **Mastery Path** | 有掌握度门槛的结构化学习路径 |
| **沉浸阅读** | 文档在侧边展开，逐页引用，边读边问 |

---

## 四、多引擎知识库

不同文档类型、不同检索需求，接不同引擎：

| 引擎 | 特点 |
|------|------|
| **LlamaIndex** | 通用文档 RAG，支持多模态 |
| **PageIndex** | 按页检索，可推理，支持自托管 |
| **GraphRAG** | 知识图谱结构检索 |
| **LightRAG / LightRAG Server** | 轻量高速，支持远程服务 |
| **Obsidian Vault** | 直接链接本地笔记库 |
| **Tencent IMA** | 腾讯 IMA 库集成 |
| **MarginNote 4** | 读书笔记库（v1.5.16 新增）|

文档解析引擎可插拔：LiteParse、Apache Tika（v1.5.15 新增）、PyMuPDF4LLM、MinerU。

---

## 五、Skills 生态

```bash
deeptutor skill install <skill-name>
```

技能来自 **EduHub**（ClawHub 社区），用户也可以自己写技能。v1.2.2 起支持用户创作技能，v1.4.4 起支持从社区安装。

内置工具之外还有：
- **MCP 服务器**：任意 MCP 工具接入
- **CLI Apps**：101 个内置命令行工具可供 Agent 调用
- 图片/视频/语音生成模型

---

## 六、Partners 系统

Partners 是带独立记忆和技能的持久化 AI 同伴，可以在任意对话轮次召唤：

```
Claude Code / Codex CLI / Gemini CLI / Kimi Code / opencode / MiMo ...
```

支持 15 个 IM 渠道实时串流，也可以把 Partners 的历史对话导入当前会话。

---

## 七、安装

**方式一：pip（最快）**

```bash
mkdir -p my-deeptutor && cd my-deeptutor
pip install -U deeptutor
deeptutor init     # 配置端口、LLM、Embedding
deeptutor start    # 启动后访问 http://127.0.0.1:3782
```

**方式二：Docker**

```bash
docker pull hkuds/deeptutor:latest
docker run -p 3782:3782 -p 8001:8001 \
  -v $(pwd)/data:/app/data \
  hkuds/deeptutor:latest
```

**方式三：源码开发**

```bash
git clone https://github.com/HKUDS/DeepTutor.git && cd DeepTutor
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cd web && npm ci --legacy-peer-deps && cd ..
deeptutor init && deeptutor start --dev
```

---

## 八、最近更新（一周内 4 个版本）

**v1.5.16（2026-08-22，今日）**：MarginNote 4 库集成；修复工具调用 ID、Embedding 和网关温度限制问题。

**v1.5.15（2026-08-20）**：PageIndex OSS 自托管版（带推理检索）；Question Bank 文件归档；第三方工具/能力插件；Apache Tika 文档解析。

**v1.5.14（2026-08-19）**：沉浸阅读（文档侧边展开，逐页引用）；从聊天直接配置 DeepTutor；Tencent IMA 库；Notebook 控制台。

**v1.5.13（2026-08-17）**：Book 流式编译 + 进度追踪 + 导出 Markdown；审批前费用预估；首页建议从记忆中生成。

---

## 九、成长轨迹

- 2025-12-29 首发
- 2026-02-06：**10K stars，仅用 39 天**
- 2026-04-19：**20K stars，111 天**
- 2026-08-22：**36,949 stars**

香港大学 HKUDS 实验室出品，有论文（arXiv 2604.26962）支撑，不是纯工程项目。

---

DeepTutor 的核心赌注是：**真正的个性化学习需要跨会话的持久化记忆，而不是更大的上下文窗口。** 三层记忆 + 可视化记忆图谱 + Mastery Path 的组合，让「AI 真的知道你学到哪了」从口号变成可验证的系统行为。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## DeepTutor: Lifelong Personalized AI Tutoring — Multi-RAG Engines, Three-Layer Memory, Skills Ecosystem, Docker Self-Host

*by Mycelium Protocol*

---

GitHub: HKUDS/DeepTutor  
Paper: arxiv.org/abs/2604.26962  
Docs: deeptutor.info  
License: Apache 2.0  
Stack: Python 3.11+ + Next.js 16  
Stars: 36,949 · Forks: 4,632  
Latest: v1.5.16 (2026-08-22, today)  
Institution: HKU Data Science Lab (HKUDS)

---

### The Core Difference from Generic AI Q&A

Generic AI Q&A starts fresh every session — it doesn't know you spent last week stuck on eigenvalues after learning matrix multiplication.

DeepTutor's design is centered on **long-term memory**: a three-layer persistent memory structure that genuinely tracks where each learner is — not through context windows, but through real cross-session state.

This is the technical foundation behind the claim that "it actually knows where you are in your learning."

---

### Three-Layer Memory

| Layer | Name | Content |
|-------|------|---------|
| L1 | Trace | Detailed per-session behavior records |
| L2 | Surface | Knowledge state distilled from traces |
| L3 | Synthesis | Cross-time learning model (strengths, blockers) |

**Memory Graph**: every memory claim traces back to specific evidence. Not a black box — inspectable and editable.

---

### Seven Learning Modes, One Agent Loop

Chat, Quiz, Research, Visualize, Solve, Mastery Path, and Immersive Reading all run on **the same agent engine**. Switching modes preserves learning context — you're changing the objective, not the tool.

| Mode | Purpose |
|------|---------|
| **Chat** | Conversational Q&A with RAG retrieval |
| **Quiz** | AI-generated questions, auto-graded, saved to Question Bank |
| **Research / Deep Research** | Multi-step synthesis across documents |
| **Visualize** | Concept visualization (Chart.js / SVG / Mermaid) |
| **Solve** | Step-by-step problem solving |
| **Mastery Path** | Structured learning with a hard mastery gate |
| **Immersive Reading** | Document open beside the thread, cited page by page |

---

### Multi-Engine Knowledge Base

Different document types and retrieval needs get different engines:

| Engine | Strength |
|--------|---------|
| **LlamaIndex** | General-purpose RAG, multimodal |
| **PageIndex** | Page-level retrieval with reasoning; self-hostable |
| **GraphRAG** | Knowledge graph structure |
| **LightRAG / LightRAG Server** | Lightweight, fast, remote-capable |
| **Obsidian Vault** | Direct link to local note vault |
| **Tencent IMA** | IMA library integration |
| **MarginNote 4** | Reading annotation library (v1.5.16) |

Pluggable document parsing: LiteParse, Apache Tika (v1.5.15), PyMuPDF4LLM, MinerU.

---

### Skills Ecosystem

```bash
deeptutor skill install <skill-name>
```

Skills come from **EduHub** (ClawHub community), and users can author their own. Community install available since v1.4.4.

Beyond built-in tools:
- **MCP servers**: any MCP tool
- **CLI Apps**: 101 built-in command-line apps the agent can invoke
- Image / video / voice generation models

---

### Partners

Partners are persistent AI companions with their own memory and skills, callable from any conversation turn:

```
Claude Code / Codex CLI / Gemini CLI / Kimi Code / opencode / MiMo ...
```

15 IM channels with live streaming; Partners' conversation history can be imported into the current session.

---

### Install

**Option 1: pip (fastest)**

```bash
mkdir -p my-deeptutor && cd my-deeptutor
pip install -U deeptutor
deeptutor init     # configure ports, LLM, embedding
deeptutor start    # open http://127.0.0.1:3782
```

**Option 2: Docker**

```bash
docker pull hkuds/deeptutor:latest
docker run -p 3782:3782 -p 8001:8001 \
  -v $(pwd)/data:/app/data \
  hkuds/deeptutor:latest
```

**Option 3: source**

```bash
git clone https://github.com/HKUDS/DeepTutor.git && cd DeepTutor
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cd web && npm ci --legacy-peer-deps && cd ..
deeptutor init && deeptutor start --dev
```

---

### Recent Velocity (4 releases in 7 days)

**v1.5.16 (2026-08-22, today)**: MarginNote 4 library; tool-call ID, embedding, and gateway temperature fixes.

**v1.5.15 (2026-08-20)**: Self-hosted PageIndex OSS with reasoning retrieval; Question Bank filing; third-party capability plugins; Apache Tika parsing.

**v1.5.14 (2026-08-19)**: Immersive Reading (document beside thread, page-by-page citations); chat-driven self-configuration; Tencent IMA library; notebook console.

**v1.5.13 (2026-08-17)**: Books stream while compiling, progress tracking, Markdown export; cost estimate before approval; memory-driven home suggestions.

---

### Growth

- 2025-12-29: first release
- 2026-02-06: **10K stars in 39 days**
- 2026-04-19: **20K stars in 111 days**
- 2026-08-22: **36,949 stars**

From HKU's Data Science Lab with a peer-reviewed paper (arXiv 2604.26962) — research-backed, not just engineering.

---

DeepTutor's core bet: **real personalized learning needs persistent cross-session memory, not a larger context window.** Three-layer memory + inspectable Memory Graph + Mastery Path gate turns "the AI knows where you are" from a tagline into verifiable system behavior.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
