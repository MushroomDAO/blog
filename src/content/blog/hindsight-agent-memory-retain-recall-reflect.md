---
title: "Hindsight：30K stars Agent 记忆框架，五层仿生结构 + 自建 AMB 基准"
titleEn: "Hindsight: 30K Stars Agent Memory Framework — 5-Level Bio-Inspired Architecture + Self-Built AMB Benchmark"
description: "vectorize-io/hindsight，MIT，Python/Rust/TypeScript，30,050 stars。开源 Agent 记忆系统：五层仿生记忆架构（世界事实→经历事实→观测→心智模型→知识页），Retain/Recall/Reflect 三路操作，四路并行检索（语义+BM25+图关系+时序），内置 pg0 嵌入式 PostgreSQL+pgvector，60+ 集成覆盖 Claude Code/LangGraph/CrewAI，自建 AMB 基准测试声称准确率第一。"
descriptionEn: "vectorize-io/hindsight, MIT, Python/Rust/TypeScript, 30,050 stars. Open-source agent memory system: 5-level bio-inspired memory hierarchy (world facts → experience facts → observations → mental models → knowledge pages), Retain/Recall/Reflect operations, 4-way parallel retrieval (semantic + BM25 + graph + temporal), embedded pg0 PostgreSQL+pgvector, 60+ integrations including Claude Code/LangGraph/CrewAI, self-built AMB benchmark claiming top accuracy."
pubDate: 2026-09-26
wechatTitle: "Hindsight：Agent五层仿生记忆框架"
wechatDigest: "MIT 3万星；五层仿生记忆；Retain/Recall/Reflect；60+集成含Claude Code"
heroImage: "../../assets/images/hindsight-agent-memory-retain-recall-reflect-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "agent-memory", "rag", "postgresql", "pgvector", "python", "ai-agents", "benchmark"]
lang: zh-CN
---

`vectorize-io/hindsight`，MIT，Python/Rust/TypeScript，30,050 stars，v0.10.1（2026-09-21），2025-10-30 开源。一个开源 Agent 记忆系统，把「对话历史提炼成持久记忆，下次对话主动调用」这件事拆成了五层仿生架构和三个核心操作。

**GitHub**：github.com/vectorize-io/hindsight

---

## 为什么说 RAG 不够用

标准 RAG（把文档向量化、召回相关段落注入 context）面对 Agent 记忆有两个根本性问题：

1. **无法处理跨对话知识积累**：每次对话独立，Agent 不知道上次和同一个用户说了什么
2. **无法建立高阶理解**：原始事实被检索回来，但事实之间的关系、随时间演变的模式、以及「我对这个人/话题的整体判断」存不了

Hindsight 的核心主张：记忆需要分层。底层存原始事实，上层做推理合成。

---

## 五层仿生记忆结构

| 层级 | 类型 | 说明 |
|------|------|------|
| L1 | World facts | 客观知识（「天空是蓝色的」） |
| L2 | Experience facts | Agent 自身的经历记录 |
| L3 | Observations | 有证据支撑的整合性信念 |
| L4 | Mental models | 从 Observations 合成的高阶理解 |
| L5 | Knowledge pages | 活体 Wiki 风格文档，随新信息持续更新 |

L1/L2 是原始输入层，L3/L4 是推理层，L5 是输出层。这个设计借鉴了认知科学里的记忆分层模型（程序记忆 / 情景记忆 / 语义记忆）。

实际使用时，Agent 不需要手动维护每一层。Retain 操作用 LLM 自动提取实体、关系和时间信息，往对应层级写入。

---

## 三个核心操作

**Retain**

从对话文本中提取结构化记忆并写入：

```python
from hindsight_client import AsyncHindsightClient

client = AsyncHindsightClient()
await client.memory.retain(
    organization_id="default",
    content="Alice is a senior engineer at Google. She prefers Python and hates JavaScript."
)
```

底层：LLM 提取实体（Alice、Google）、属性（senior engineer、Python 偏好）、关系（工作于），写入 L1/L2/L3。

**Recall**

四路并行检索：
1. **语义向量**：pgvector 余弦相似度
2. **关键词**：BM25 全文检索
3. **图关系**：实体链和时序链遍历
4. **时间过滤**：优先最近记忆，按时间衰减

四路结果合并后用 reranker 排序，返回最相关的记忆片段：

```python
memories = await client.memory.recall(
    organization_id="default",
    query="What does Alice prefer for backend work?"
)
# 返回：Alice prefers Python, works at Google as senior engineer, dislikes JavaScript
```

**Reflect**

深度分析操作，跨记忆形成新连接，回答复杂推理问题：

```python
answer = await client.memory.reflect(
    organization_id="default",
    query="Based on Alice's history, what kind of project would she enjoy most?"
)
```

Reflect 不是简单检索，而是让 LLM 对已有记忆做推理合成，生成新的 L3/L4 层记忆。代价是延迟更高，适合非实时的深度分析场景。

---

## 存储层

**主存储：PostgreSQL + pgvector**

Hindsight 随包附带 `pg0`（vectorize-io/pg0，126 stars，Rust 实现）——一个零配置嵌入式 PostgreSQL，开箱就带 pgvector，无需单独安装数据库服务。单机场景直接用 Docker 一条命令起来：

```bash
docker run -it --pull always --name hindsight --restart unless-stopped \
  -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY=$OPENAI_API_KEY \
  -v hindsight-data:/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:latest
```

企业级部署支持 Oracle AI Database 23ai（功能对等）。

**本地 ML 组件**（`[local-ml]` extra）

- Embedding：sentence-transformers + transformers + torch
- Reranker：flashrank（通用）+ jina-mlx（Apple Silicon via MLX）
- ONNX 推理：onnxruntime，不依赖 Ollama sidecar
- 完全离线：llama-cpp-python

---

## 部署方式

| 方式 | 命令 / 说明 |
|------|-------------|
| Docker 单容器 | 含内嵌 pg0 PostgreSQL，一条命令 |
| Docker Compose | 含外部 PostgreSQL、监控 |
| Kubernetes | 官方 Helm Chart，标准 readiness probe |
| Python embedded | `pip install hindsight-embed`，自动管理后台 daemon，无需手动起服务器 |
| Hindsight Cloud | 托管版，按用量计费，SLA 99.9% |

**Python embedded 最简路径**：

```bash
pip install hindsight-embed
export OPENAI_API_KEY=sk-...
hindsight-embed memory retain default "Alice works at Google"
hindsight-embed memory recall default "Where does Alice work?"
```

首次运行会下载 ML 模型，冷启动约 1–3 分钟；5 分钟无活动自动退出。

---

## 60+ 集成

Hindsight 重点集成了 Coding Agent 生态：

**AI 编程工具**：Claude Code、Cursor、GitHub Copilot、Aider、Cline、Roo Code、Codex、Devin、OpenHands、Zed、Continue

**框架**：LangGraph、CrewAI、Pydantic AI、LlamaIndex、Haystack、AutoGen/AG2、Google ADK、Composio

**无代码**：n8n、Zapier、Flowise、Dify

**语音 Agent**：Pipecat、Vapi

**其他**：Obsidian 插件、游戏 NPC

配套项目 `self-driving-agents`（3,038 stars）提供 179 个预制 Agent 模板，覆盖 13 个业务部门，全部基于 Hindsight 记忆层。

---

## AMB 基准：自建赛道，自家出题

Hindsight 的 README 声称「最准确的 Agent 记忆系统」，依据是他们自建的 **AMB（Agent Memory Benchmark）**。

他们为什么要自建 benchmark？README 的说法：LongMemEval 和 LoComo 等现有基准是为 32k 上下文设计的，在百万 token 上下文时代已失去区分度。

**Hindsight AMB 自报分数**：

| Benchmark | 分数 |
|-----------|------|
| LongMemEvalS | **94.6%** |
| LoComo10 | 92.0% |
| PersonaMem32K | 86.6% |
| BEAM100K | 75.0% |
| BEAM1M | 73.9% |
| BEAM10M | 64.1% |

几个需要注意的地方：

**评估方法**：AMB 用 Gemini 同时做答案生成和评分（既是裁判又是选手的同款模型族）。这个设计存在方法论争议——用 Gemini 评 Gemini 优化的结果。

**竞品分数来源不对等**：README 里竞品分数标注「由厂商自报」，而 Hindsight 自己的分数声称「由 Virginia Tech Sanghani AI 中心独立复现」。《华盛顿邮报》也被提及为「合作方」。独立验证和厂商自报放在同一张表格里比较，不是公平对比。

**benchmark 工具已开源**：agent-memory-benchmark（vectorize-io，84 stars），有兴趣可以自己复跑。

---

## 已知问题和限制

**Kubernetes 3 分钟冷启动盲窗期**（issue #4374）：embedding 和 reranker 模型在进程 lifespan 内加载，启动约 3 分钟内 `/health/live` 不可达，需要额外配置 initialDelaySeconds。

**Intel Mac 不支持完整版**：`hindsight-all` 的 MLX 依赖仅限 `darwin arm64`，Intel Mac 用户必须用 `hindsight-all-slim` 变体。

**litellm 版本钉死**：litellm 1.92.0+ 停止发布 macOS wheels，Hindsight 把 Mac 用户固定在 1.91.x，等上游修复。

**per-fact 删除未实现**（issue #3509）：错误记忆只能被「纠正」（写入新事实覆盖），不能精确删除单条。已有 feature request，v0.10.1 未解决。

**reflect 在低 token 预算下性能陷阱**（issue #4566）：coding agents hook 内做 reflect，低预算下大量时间耗在预填充 30–90k token 工具结果上，实际 hook 时间窗口内完不成。

**PII 扫描误判修复**：v0.10.1 修复了把技术数字（端口号、哈希值）误判为信用卡号码并脱敏的 bug。

---

## 怎么看这个项目

30,050 stars、10 个月到 v0.10.1，说明 Hindsight 在 Agent 记忆赛道建立了真实的社区。

技术亮点是五层记忆 + Reflect 操作——这让 Agent 不只是「记住」原始对话，还能随时间形成对用户或任务的「心智模型」。对于长期运行的 Coding Agent、客服 Agent 或个人助理 Agent，这是比 RAG 更自然的记忆模型。

自建 AMB 这步棋值得关注：它一方面回避了现有 benchmark 的弱点，另一方面也让「第一名」的说法变得很难被独立验证。开源了 benchmark 工具是诚意，但评估方法（Gemini 自评）和竞品数据来源不对等是真实存在的方法论问题。

pg0 这个嵌入式 PostgreSQL 组件是个意外收获——零配置、自带 pgvector，单独拿出来用于其他需要向量存储的项目也是可行的。

> 开源仅供学习研究参考。商用前核实许可证条款及各依赖组件的商业使用限制。

---

<!--EN-->

## Hindsight: 30K Stars Agent Memory Framework — 5-Level Architecture + Self-Built AMB Benchmark

`vectorize-io/hindsight` — MIT, Python/Rust/TypeScript, 30,050 stars, v0.10.1 (2026-09-21). Open-source agent memory system solving the core problem: agents forget everything between sessions. The approach is a 5-level bio-inspired memory hierarchy with three operations: Retain, Recall, and Reflect.

**GitHub**: github.com/vectorize-io/hindsight

---

### The Problem with Standard RAG for Agent Memory

Standard RAG (vectorize docs, retrieve relevant chunks, inject into context) has two fundamental limits for agent memory:

1. **No cross-session knowledge accumulation**: each conversation starts fresh
2. **No higher-order understanding**: raw facts are retrieved but relationships, patterns over time, and high-level judgments can't be stored

---

### 5-Level Bio-Inspired Memory

| Level | Type | Description |
|-------|------|-------------|
| L1 | World facts | Objective knowledge |
| L2 | Experience facts | Agent's own recorded experiences |
| L3 | Observations | Evidence-backed integrated beliefs |
| L4 | Mental models | High-order understanding synthesized from Observations |
| L5 | Knowledge pages | Living wiki-style documents, continuously updated |

L1/L2 are input layers; L3/L4 are inference layers; L5 is output. Modeled on cognitive science memory taxonomy (procedural / episodic / semantic memory).

---

### Three Core Operations

**Retain**: LLM extracts entities, attributes, relationships, and temporal info from conversation → writes to appropriate memory level.

**Recall**: 4-way parallel retrieval — semantic vectors (pgvector) + keywords (BM25) + graph traversal (entity/temporal chains) + time filtering. Results merged and reranked.

**Reflect**: Deep analysis across stored memories to form new connections and answer complex reasoning queries. Generates new L3/L4 layer memories as output. Higher latency, suited for non-realtime analysis.

---

### Storage

**PostgreSQL + pgvector** as primary store. Ships with `pg0` (vectorize-io/pg0, 126 stars, Rust) — a zero-config embedded PostgreSQL with pgvector built in. Enterprise deployment supports Oracle AI Database 23ai.

**Local ML** (`[local-ml]` extra): sentence-transformers + torch for embedding, flashrank + jina-mlx (Apple Silicon) for reranking, ONNX inference, llama.cpp for fully offline mode.

**Deployment options**: Docker single container, Docker Compose, Kubernetes Helm chart, Python embedded daemon (`pip install hindsight-embed`), or Hindsight Cloud (managed, 99.9% SLA).

---

### 60+ Integrations

Coding agents: Claude Code, Cursor, GitHub Copilot, Aider, Cline, Roo Code, Codex, Devin, OpenHands, Zed, Continue.

Frameworks: LangGraph, CrewAI, Pydantic AI, LlamaIndex, Haystack, AutoGen/AG2, Google ADK.

Companion project `self-driving-agents` (3,038 stars): 179 pre-built agent templates across 13 business departments, all running on Hindsight memory.

---

### AMB Benchmark: Self-Built, Self-Scored

Hindsight claims "most accurate agent memory system" based on their own **AMB (Agent Memory Benchmark)** — because existing benchmarks (LongMemEval, LoComo) were designed for 32k context and lose discriminating power in the million-token era.

**Hindsight AMB self-reported scores**: LongMemEvalS 94.6%, LoComo10 92.0%, BEAM1M 73.9%.

**Methodology caveats to note**: AMB uses Gemini as both the answer generator and judge (same model family). Competitor scores are labeled "vendor self-reported" while Hindsight's are claimed "independently reproduced by Virginia Tech Sanghani AI Center" — asymmetric sourcing on the same comparison table. The Washington Post is listed as a collaborator; that's unusual for benchmark validation and the nature of the collaboration isn't fully explained.

The benchmark tool is open-source (agent-memory-benchmark repo, 84 stars) and can be re-run independently.

---

### Known Issues

- **Kubernetes 3-min cold start** (issue #4374): health endpoint unreachable during model load; needs `initialDelaySeconds` config
- **Intel Mac**: `hindsight-all` requires `darwin arm64`; use `hindsight-all-slim` on Intel
- **litellm version pinned on Mac**: 1.91.x ceiling until upstream publishes macOS wheels for 1.92+
- **No per-fact deletion** (issue #3509): wrong memories can only be "corrected" (overwritten), not precisely deleted
- **Reflect in low-token-budget hooks** (issue #4566): performance trap when coding agent hooks run reflect with small token budgets
- **Embed daemon cold start**: 1–3 min model download on first run; auto-exits after 5 min idle

---

### Assessment

30K stars in 10 months shows genuine community traction. The technical differentiation is real: the 5-level hierarchy + Reflect operation lets agents build mental models over time, not just retrieve raw facts — a meaningfully better fit for long-running coding agents, customer service agents, or personal assistants than standard RAG.

The self-built AMB benchmark is a calculated strategic move: it avoids existing benchmark weaknesses while making the "first place" claim very hard to independently verify. Gemini self-evaluation and asymmetric competitor sourcing are real methodological issues, but open-sourcing the benchmark tool is genuine transparency.

The `pg0` embedded PostgreSQL component is a useful side project: zero-config, ships with pgvector, usable independently for any project needing vector storage without running a separate database service.

> For learning and research reference only. Verify license terms and commercial use restrictions for all dependency components before production deployment.
