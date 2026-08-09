---
title: "StaffDeck：面壁智能 + 清华 THUNLP 开源的企业数字员工平台，状态机 SOP + 多层级知识检索"
titleEn: "StaffDeck: ModelBest + Tsinghua THUNLP Open-Source Enterprise Digital Employee Platform with State-Machine SOPs"
description: "面壁智能联合清华THUNLP、OpenBMB 开源 StaffDeck，把员工经验和业务流程沉淀成可运行的数字员工：状态机驱动的 SOP、文档结构感知的知识检索、完整 Trace 闭环改进，桌面安装包 + 源码双通道，633 Stars，开源 6 天。"
descriptionEn: "ModelBest, Tsinghua THUNLP, and OpenBMB jointly open-source StaffDeck, converting employee expertise and business processes into runnable digital employees: state-machine-driven SOPs, document-structure-aware knowledge retrieval, and full trace-loop improvement. Desktop installer + source code, 633 stars, 6 days since open-source."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["企业Agent", "数字员工", "状态机", "SOP", "RAG", "面壁智能", "清华THUNLP", "OpenBMB", "开源", "AgentOS"]
heroImage: "../../assets/images/staffdeck-openbmb-enterprise-digital-employee-platform-banner.jpg"
---

> **GitHub**：[OpenBMB/StaffDeck](https://github.com/OpenBMB/StaffDeck) · **Stars**：633  
> **机构**：面壁智能 + NEU-ModelBest联合实验室 + 清华THUNLP + OpenBMB + AI9Stars  
> **官网**：[staffdeck.openbmb.cn](https://staffdeck.openbmb.cn/)  
> **许可**：GNU AGPL v3.0 · **开源时间**：2026-07-15

---

## 问题定义：AI 工具 vs 组织资产

大多数企业用 AI 的方式是：给每个员工一个 ChatGPT 账号，让他们自己想提示词。这有个隐患——经验不沉淀。某个人摸索出了一套有效的工作流，离职了，经验就消失了。

StaffDeck 试图解决的是另一个问题：**如何把个人经验、业务流程和判断标准，转化为组织可复用的数字员工**，让这些员工能持续运行、接管重复工作，并且随着时间迭代进化。

这不是"又多了一个 AI 助手"，而是给企业提供了一套**制造和管理数字员工的工厂**。

---

## 四个核心能力

### 1. 数字员工生命周期管理

每个数字员工有完整的"员工档案"：岗位、员工 ID、能力画像、工作记录、权限范围。

关键设计：**能力成长**——员工不是一次性配置好的静态系统，而是通过对话日志、用户反馈、记忆积累持续进化。**权限隔离**——用户可以从 Marketplace 复制资源，但无法修改 Marketplace 原版，保护模板不被污染。**发布与复用**——经过验证的员工可以发布供组织内其他人使用。

### 2. 状态机驱动的 SOP

这是 StaffDeck 最有技术含量的一块。

普通 Agent 的流程控制依赖模型的随机性——同样的输入，不同的运行可能走不同的路径。StaffDeck 用**状态机**来执行 SOP：流程节点是确定的，状态转移条件是明确的，不靠 LLM 猜要走哪条路。

输入方式是自然语言——你描述业务流程，系统生成结构化状态机。生成后可以用**可视化编辑器**调整，支持版本管理和分支演化（同一个 SOP 可以有不同场景的分叉版本）。

```
自然语言描述 → 结构化 SOP → 状态机 → 确定性执行
                            ↓
                   支持实时切换多个流
                   保留跨流的上下文
                   可视化编辑和版本管理
```

这意味着什么：合规性强要求的流程（法务、财务、客服升级路径）终于有了**可审计**的执行记录，不再是黑盒。

### 3. 文档结构感知的知识检索

普通 RAG 的问题：把文档切块，向量检索最相似的块，返回。这在文档结构复杂时效果差——一份 200 页的合同，某个条款的解释需要结合前面的定义章节，切块检索找不到上下文。

StaffDeck 的方案：**多层级导航索引**。

```
文档层
  └── 章节层
        └── 页面层
              └── 段落层 + 摘要层
```

检索时先估算信息可能在哪个层级，然后**逐步定位原文**——不是直接返回相似块，而是先找到大致位置，再精确定位。这类似于人类读书的方式：先看目录估位置，再翻到对应章节找答案。

额外功能：**溯源引用**（返回答案时标注来自哪个文档哪个章节）、**知识桶**（不同数字员工可以绑定不同的知识范围）、**检索调试**（查看检索过程，方便排查为什么没找到正确答案）。

### 4. 持续运营与闭环改进

数字员工的价值不在于"部署完成"那一刻，而在于**持续运营**：

**执行能力**：通过 HTTP API 和 MCP 连接业务系统，通过定时任务让员工主动工作（不用等人 @ 它）。

**可观测性**：每次对话都有完整的**执行记录**——流式展示意图分析、知识检索、技能调用、工具执行、回顾和回复的全过程。这不是日志，是可读的决策轨迹。

**人工接管**：运行中可以随时介入——继续排队的请求、取消当前运行、移交给人工处理、批准待批的答案。

**改进闭环**：对话日志 + 用户反馈 + 长期记忆 → 分析 → 改进员工能力配置。

---

## 快速部署

### 桌面安装包（最简单）

| 平台 | 架构 | 下载 |
|---|---|---|
| macOS | Apple Silicon (arm64) | `.dmg` |
| Windows | x64 | `.exe` installer |
| Linux | x86_64 (Debian/Ubuntu) | `.deb` |

从 [官网](https://staffdeck.openbmb.cn/) 或 GitHub Releases 下载，安装后开箱即用。

### 源码部署（macOS/Linux/WSL）

```bash
git clone https://github.com/OpenBMB/StaffDeck.git
cd StaffDeck
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e "backend[dev]"
npm --prefix frontend-enterprise ci
cp backend/.env.example backend/.env
```

编辑 `backend/.env`：

```dotenv
APP_SECRET="换成一个长随机字符串"
DEMO_MODEL_BASE_URL="https://你的OpenAI兼容端点/v1"
DEMO_MODEL_NAME="你的模型名"
DEMO_MODEL_API_KEY="你的API Key"
```

兼容所有 OpenAI 格式端点——可以是 OpenAI、DeepSeek、Qwen、本地 Ollama，甚至 llama.cpp 的 HTTP 服务。

```bash
# 启动（单端口 5173，前后端合一）
scripts/dev_up.sh --detach

# 验证
curl http://127.0.0.1:5173/api/health
# → {"status":"ok"}
```

打开 [http://127.0.0.1:5173/workspace/gallery](http://127.0.0.1:5173/workspace/gallery)，初始账号密码 `admin`/`admin`，**第一次登录后立刻改密码**。

**Agent 友好的快速部署提示词**（直接粘给 Claude Code/Cursor/Codex）：

```
Read https://raw.githubusercontent.com/OpenBMB/StaffDeck/main/README.md.
Clone the OpenBMB/StaffDeck repository, prepare Python 3.11+ and Node.js 20,
create backend/.venv, install dependencies, copy backend/.env.example to
backend/.env, ask me for the model endpoint and API key, start with
scripts/dev_up.sh --detach, then verify /api/health.
```

---

## 六步标准工作流

```
1. 创建数字员工 → 定义岗位/角色边界/服务风格/权限范围
2. 配置员工能力 → 从 Marketplace 复制或新建知识库/技能/SOP/工具
3. 启动对话     → 从 gallery 或员工列表进入，首条消息后会话持久化
4. 执行观测     → 流式查看意图分析/检索/技能/工具/回复的完整执行记录
5. 必要时介入   → 继续/取消/移交人工/处理待批答案
6. 持续运营     → 记忆积累 + 反馈分析 + 定时任务 → 员工能力持续进化
```

---

## 项目结构

```
StaffDeck/
├── backend/               # FastAPI API、Agent 运行时、存储、任务 worker
├── frontend-enterprise/   # React/TypeScript 工作台
├── docs/                  # 教程、API、Schema、示例流程
├── scripts/               # 服务生命周期管理脚本（单端口）
├── packaging/             # macOS/Linux/Windows 打包资产
├── README.md              # 英文
└── README.zh.md           # 简体中文
```

---

## 路线图

- [ ] 群聊、多数字员工协作与任务分工
- [ ] 更多企业连接器和 Marketplace 资源（经审核）
- [ ] 高风险工具行为的细粒度审批策略

---

## 与同类项目对比

| | **StaffDeck** | **HugAgentOS** | **Dify** | **Open WebUI** |
|---|---|---|---|---|
| 机构 | 面壁+清华THUNLP | 浙大REAL | Langgenius | 开源社区 |
| 核心差异 | 数字员工生命周期+状态机SOP | 本体治理控制平面 | 工作流可视化 | 模型前端UI |
| SOP执行 | ✅ 状态机（确定性） | 基于ReAct | 工作流 | ✗ |
| 知识检索 | ✅ 文档结构感知多层级 | 向量+关键词 | 向量 | 向量 |
| 桌面安装包 | ✅ Win/Mac/Linux | ✗ | ✗ | ✗ |
| Stars（对比日） | 633 | 50 | 数万 | 数万 |

StaffDeck 和 HugAgentOS 解决的是相似问题（企业 Agent 治理），但路线不同：HugAgentOS 从**语义本体**出发做规则门控，StaffDeck 从**员工生命周期管理**出发做流程确定化。两者不互斥，可以组合使用。

---

## 核心判断

StaffDeck 的赌注是：**企业 AI 最终要解决的是知识资产化和流程确定化**，而不是让 LLM 更聪明。

状态机 SOP 这个设计选择特别务实——不是相信模型永远能做对，而是把关键判断节点结构化、可审计、可调试。这在真实企业场景里比"更好的 Prompt"可靠得多。

633 Stars 开源 6 天，出道即巅峰节奏。清华 THUNLP + 面壁智能的背书，加上同时提供桌面安装包（降低部署门槛）和源码（支持企业内部定制），这个项目的走向值得持续关注。

---

## 参考资源

- **GitHub**：[OpenBMB/StaffDeck](https://github.com/OpenBMB/StaffDeck)
- **官网**：[staffdeck.openbmb.cn](https://staffdeck.openbmb.cn/)
- **快速开始**：[staffdeck.openbmb.cn/#/docs/introduce](https://staffdeck.openbmb.cn/#/docs/introduce?lang=en)
- **面壁智能**：[modelbest.cn](https://modelbest.cn/)
- **清华THUNLP**：[nlp.csai.tsinghua.edu.cn](https://nlp.csai.tsinghua.edu.cn/)

© 2026 Author: Mycelium Protocol

<!--EN-->

> **GitHub**: [OpenBMB/StaffDeck](https://github.com/OpenBMB/StaffDeck) · **Stars**: 633  
> **Organizations**: ModelBest + NEU-ModelBest Joint Lab + Tsinghua THUNLP + OpenBMB + AI9Stars  
> **Website**: [staffdeck.openbmb.cn](https://staffdeck.openbmb.cn/)  
> **License**: GNU AGPL v3.0 · **Open-sourced**: 2026-07-15

---

## Problem Definition: AI Tools vs. Organizational Assets

Most companies deploy AI by giving every employee a ChatGPT account and letting them figure out their own prompts. This carries a hidden risk — expertise never accumulates. Someone develops an effective workflow, leaves the company, and the knowledge disappears with them.

StaffDeck addresses a different problem: **how to convert individual expertise, business processes, and judgment criteria into digital employees that the organization can reuse** — employees that run continuously, take over repetitive work, and evolve over time.

This is not "yet another AI assistant." It is a **factory for creating and managing digital employees**.

---

## Four Core Capabilities

### 1. Digital Employee Lifecycle Management

Each digital employee has a complete "employee profile": job role, employee ID, capability portrait, work records, and permission scope.

Key design choices: **Capability growth** — employees are not static systems configured once; they evolve continuously through conversation logs, user feedback, and memory accumulation. **Permission isolation** — users can copy resources from the Marketplace but cannot modify the originals, protecting templates from contamination. **Publishing and reuse** — validated employees can be published for use by others within the organization.

### 2. State-Machine-Driven SOPs

This is StaffDeck's most technically sophisticated component.

Conventional agent flow control relies on the model's stochasticity — the same input may take different paths on different runs. StaffDeck uses a **state machine** to execute SOPs: process nodes are deterministic, state transition conditions are explicit, and the LLM is never left to guess which path to take.

Input is natural language — you describe a business process and the system generates a structured state machine. The result can be adjusted in a **visual editor**, with version management and branching evolution (the same SOP can have forked versions for different scenarios).

```
Natural language description → Structured SOP → State machine → Deterministic execution
                                                       ↓
                                         Supports real-time switching between multiple flows
                                         Retains cross-flow context
                                         Visual editing and version management
```

What this means: compliance-critical processes (legal, finance, customer escalation paths) finally have **auditable** execution records — no more black boxes.

### 3. Document-Structure-Aware Knowledge Retrieval

The problem with conventional RAG: chunk documents, retrieve the most similar chunks via vector search, return results. This performs poorly when document structure is complex — in a 200-page contract, understanding a specific clause may require context from the definitions section at the beginning, which chunk retrieval cannot capture.

StaffDeck's approach: **multi-level navigational indexing**.

```
Document layer
  └── Chapter layer
        └── Page layer
              └── Paragraph layer + Summary layer
```

Retrieval first estimates which layer likely contains the information, then **progressively locates the source text** — rather than directly returning similar chunks, it first finds the approximate location and then pinpoints precisely. This mirrors how humans read: consult the table of contents to estimate location, then turn to the relevant chapter for the answer.

Additional features: **Source attribution** (answers include which document and chapter they came from), **Knowledge buckets** (different digital employees can bind to different knowledge scopes), **Retrieval debugging** (view the retrieval process to diagnose why a correct answer was not found).

### 4. Continuous Operations and Closed-Loop Improvement

The value of a digital employee lies not in the moment of deployment but in **continuous operations**:

**Execution capability**: connect to business systems via HTTP API and MCP; use scheduled tasks to make employees work proactively (no need to wait for someone to ping them).

**Observability**: every conversation has a complete **execution trace** — streaming display of intent analysis, knowledge retrieval, skill invocation, tool execution, review, and reply. This is not a log — it is a readable decision trail.

**Human takeover**: intervene at any time during execution — continue queued requests, cancel the current run, hand off to a human, or approve pending answers.

**Improvement loop**: conversation logs + user feedback + long-term memory → analysis → improved employee capability configuration.

---

## Quick Deployment

### Desktop Installer (Simplest)

| Platform | Architecture | Download |
|---|---|---|
| macOS | Apple Silicon (arm64) | `.dmg` |
| Windows | x64 | `.exe` installer |
| Linux | x86_64 (Debian/Ubuntu) | `.deb` |

Download from the [official website](https://staffdeck.openbmb.cn/) or GitHub Releases; works out of the box after installation.

### Source Deployment (macOS/Linux/WSL)

```bash
git clone https://github.com/OpenBMB/StaffDeck.git
cd StaffDeck
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e "backend[dev]"
npm --prefix frontend-enterprise ci
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```dotenv
APP_SECRET="replace with a long random string"
DEMO_MODEL_BASE_URL="https://your-openai-compatible-endpoint/v1"
DEMO_MODEL_NAME="your-model-name"
DEMO_MODEL_API_KEY="your-api-key"
```

Compatible with all OpenAI-format endpoints — can be OpenAI, DeepSeek, Qwen, local Ollama, or even llama.cpp's HTTP server.

```bash
# Start (single port 5173, frontend and backend combined)
scripts/dev_up.sh --detach

# Verify
curl http://127.0.0.1:5173/api/health
# → {"status":"ok"}
```

Open [http://127.0.0.1:5173/workspace/gallery](http://127.0.0.1:5173/workspace/gallery); default credentials are `admin`/`admin` — **change the password immediately on first login**.

**Agent-friendly quick deployment prompt** (paste directly into Claude Code/Cursor/Codex):

```
Read https://raw.githubusercontent.com/OpenBMB/StaffDeck/main/README.md.
Clone the OpenBMB/StaffDeck repository, prepare Python 3.11+ and Node.js 20,
create backend/.venv, install dependencies, copy backend/.env.example to
backend/.env, ask me for the model endpoint and API key, start with
scripts/dev_up.sh --detach, then verify /api/health.
```

---

## Six-Step Standard Workflow

```
1. Create a digital employee  → Define job role / capability boundaries / service style / permission scope
2. Configure capabilities     → Copy from Marketplace or create new knowledge bases / skills / SOPs / tools
3. Start a conversation       → Enter from gallery or employee list; session persists after the first message
4. Observe execution          → Stream the complete execution trace: intent analysis / retrieval / skills / tools / reply
5. Intervene when needed      → Continue / cancel / hand off to human / handle pending approvals
6. Continuous operations      → Memory accumulation + feedback analysis + scheduled tasks → employee capabilities evolve continuously
```

---

## Project Structure

```
StaffDeck/
├── backend/               # FastAPI API, agent runtime, storage, task worker
├── frontend-enterprise/   # React/TypeScript workbench
├── docs/                  # Tutorials, API, Schema, example workflows
├── scripts/               # Service lifecycle management scripts (single port)
├── packaging/             # macOS/Linux/Windows packaging assets
├── README.md              # English
└── README.zh.md           # Simplified Chinese
```

---

## Roadmap

- [ ] Group chat, multi-digital-employee collaboration, and task allocation
- [ ] More enterprise connectors and Marketplace resources (reviewed)
- [ ] Fine-grained approval policies for high-risk tool actions

---

## Comparison with Similar Projects

| | **StaffDeck** | **HugAgentOS** | **Dify** | **Open WebUI** |
|---|---|---|---|---|
| Organization | ModelBest + Tsinghua THUNLP | Zhejiang Univ. REAL | Langgenius | Open-source community |
| Core differentiator | Digital employee lifecycle + state-machine SOP | Ontology governance control plane | Workflow visualization | Model frontend UI |
| SOP execution | ✅ State machine (deterministic) | ReAct-based | Workflow | ✗ |
| Knowledge retrieval | ✅ Document-structure-aware multi-level | Vector + keyword | Vector | Vector |
| Desktop installer | ✅ Win/Mac/Linux | ✗ | ✗ | ✗ |
| Stars (comparison date) | 633 | 50 | Tens of thousands | Tens of thousands |

StaffDeck and HugAgentOS address similar problems (enterprise agent governance) but take different approaches: HugAgentOS uses **semantic ontologies** as a rule-gating mechanism, while StaffDeck uses **employee lifecycle management** to make processes deterministic. The two are not mutually exclusive and can be used in combination.

---

## Core Assessment

StaffDeck's bet is: **the ultimate challenge for enterprise AI is knowledge asset conversion and process determinism**, not making LLMs smarter.

The state-machine SOP design choice is particularly pragmatic — rather than trusting the model to always get it right, it structures, audits, and makes debuggable the critical decision nodes. In real enterprise scenarios, this is far more reliable than "better prompts."

633 stars in 6 days since open-sourcing — a debut at the top. The backing of Tsinghua THUNLP and ModelBest, combined with simultaneous availability of desktop installers (lowering the deployment barrier) and source code (supporting enterprise customization), makes this project worth watching closely.

---

## Reference Resources

- **GitHub**: [OpenBMB/StaffDeck](https://github.com/OpenBMB/StaffDeck)
- **Website**: [staffdeck.openbmb.cn](https://staffdeck.openbmb.cn/)
- **Quick Start**: [staffdeck.openbmb.cn/#/docs/introduce](https://staffdeck.openbmb.cn/#/docs/introduce?lang=en)
- **ModelBest**: [modelbest.cn](https://modelbest.cn/)
- **Tsinghua THUNLP**: [nlp.csai.tsinghua.edu.cn](https://nlp.csai.tsinghua.edu.cn/)

© 2026 Author: Mycelium Protocol
