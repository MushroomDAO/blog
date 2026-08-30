---
title: "Belief Context Graph：把 Agent 记忆从「检索」升级为「置信度感知的信念图」"
titleEn: "Belief Context Graph: Upgrading Agent Memory from Retrieval to Confidence-Aware Belief Graph"
description: "bigai-nlco/belief-context-graph 开源，BCG 用可审计的置信度、证据溯源、冲突检测把 Agent 记忆升级为信念图，解决长程推理中「该不该相信这个事实」的核心问题，MIT 许可，⭐59。"
descriptionEn: "bigai-nlco/belief-context-graph (BCG) upgrades agent memory from retrieval to a probabilistic, evidence-grounded belief graph with auditable deterministic confidence, evidence provenance, and conflict detection. MIT, ⭐59."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Research"
tags: ["agent memory", "knowledge graph", "LLM", "reasoning", "open source", "confidence", "provenance", "BIGAI"]
heroImage: "../../assets/images/belief-context-graph-bcg-agent-memory-confidence-provenance-deterministic-reasoning-banner.jpg"
author: "Mycelium Protocol"
---

## 现有 Agent 记忆的盲区

当前主流 Agent 记忆系统做的事情本质上都是同一件：**检索**。对话记忆保存历史，向量记忆找相似片段，GraphRAG 提取实体关系，Trace 记忆记录工具调用……

它们回答的都是"检索问题"：哪段文字相关？哪些实体有关联？过去发生了什么？

但执行真实任务的 Agent 还需要回答另一类问题——**信念问题**：

> - 我应该相信这个事实吗？
> - 它还有效，还是已经过期？
> - 来源可靠吗？
> - 它和其他证据矛盾吗？
> - 确定性够不够，值得采取行动吗？
> - 结果证明我之前的判断是错的吗？

**Belief Context Graph（BCG）** 是北京通用人工智能研究院（BIGAI）开源的一个 Agent 记忆基础设施，专门回答这类问题。

---

## BCG 的核心：四个能力

### 1. 信念提取（Belief Extraction）

BCG 把 Agent 的执行轨迹切分成片段，从中提取**结构化信念节点**，每个节点记录一个命题（"X 是 Y"、"A 导致 B"……），并把这些节点连接成图。

这和 GraphRAG 的实体提取不同：BCG 提取的是 Agent 推理过程中实际依赖的命题，而不是文本中出现的所有实体。

### 2. 可审计的确定性置信度（Deterministic Confidence）

这是 BCG 与其他系统最大的区别。每个信念节点的置信度由三个组件确定性计算得出：

```
posterior_confidence = f(
    initial_confidence,   // 初始置信度（来源可靠性 + 立场质量）
    evidence_confidence,  // 证据置信度（支持 / 反对证据的累积）
    factor_confidence     // 关系推导置信度（相邻节点的传播权重）
)
```

这个计算是**确定性的**（deterministic），不是 LLM 给出的模糊评分。你可以追溯任何一个信念节点的置信度是怎么算出来的，哪条证据贡献了多少权重。

### 3. 证据溯源（Evidence Provenance）

每个信念节点携带精确的来源引用——具体是哪一轮对话的哪个偏移量产生了这个信念。Agent 可以知道"这个结论来自第 3 轮工具调用返回的第二段文字"。

### 4. 时间感知与关系链接

- **Temporal Awareness**：运行级生命周期，记录每个信念形成的时间戳和演化轨迹
- **Relation Linking**：信念节点之间有前向/后向关系边，形成因果决策图/追踪链

---

## 架构：Agent 和模型之间的可选上下文层

BCG 作为一个**可选的上下文层**插在 Agent 和模型之间：

```
用户输入 + 最近几轮 → [保留在原始上下文]
更早的已完成轮次   → [流入 Graph Construction]
                              ↓
                   Belief Snapshot（信念快照）
                              ↓
                   注入到 system prompt
                              ↓
                    Agent → LLM 推理
```

较旧的已完成轮次不再堆在上下文里，而是被蒸馏成信念图快照，只有被提取为信念节点的内容（附带置信度和来源）才会出现在 system prompt 里。这同时压缩了 token 用量，并提升了推理质量。

HTTP 服务和 Python SDK 使用同一套后端注册表、构建流水线、置信度语义和图产物。

---

## 实测案例：BrowseComp 任务

在 BrowseComp 基准测试中，使用 BCG 的 Kimi K3 在任务中途识别出"这个搜索我已经做过了"（通过信念节点的 identity 和置信度），直接跳过重复搜索，而不是重跑一遍。这正是信念图解决"长程 Agent 重复行为"的典型模式。

基准结果：BCG 在准确率和 token 成本两个维度上均有改善（详见 [benchmark overview](https://bigai-nlco.github.io/belief-context-graph/)）。

---

## 与主流方案的对比

| | Mem0 | Zep | LangChain | LlamaIndex | Semantica | **BCG** |
|---|---|---|---|---|---|---|
| 信念原生提取 | ⚡ | ⚡ | ⚡ | ⚡ | ⚡ | ✅ |
| 确定性置信度 | ❌ | ❌ | ❌ | ❌ | ⚡ | ✅ |
| 证据溯源 | ⚡ | ✅ | ⚡ | ⚡ | ✅ | ✅ |
| 冲突检测 | ⚡ | ✅ | ⚡ | ❌ | ✅ | ✅ |
| 本地产物（无外部 DB）| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 合并/去重 | ⚡ | ✅ | ⚡ | ⚡ | ✅ | ✅ |

**BCG 独有**：信念原生提取 + 确定性置信度的组合，在对比表中只有 BCG 同时做到了这两点。

---

## 快速上手

```bash
git clone https://github.com/bigai-nlco/belief-context-graph.git
cd belief-context-graph
make install

# 运行内置参考 Agent（首次运行引导设置模型凭证）
uv run bcg
```

Python 3.11–3.13，依赖通过 `uv` 管理。

**Python SDK（集成到自己的 Agent）**：

```python
from bcg import BCGMemory, BCGRunner

# 构建信念图
runner = BCGRunner(session_id="my-agent-session")
runner.ingest(trajectory)   # 喂入 Agent 执行轨迹

# 查询信念
memory = BCGMemory(session_id="my-agent-session")
beliefs = memory.observe_belief(query="用户的偏好设置")

# 返回：信念节点列表，每个含 content / confidence / evidence_refs / relations
```

文档：[belief-context-graph.docs.buildwithfern.com](https://belief-context-graph.docs.buildwithfern.com/)

---

## 适合哪些场景

**长程 Agent 任务**（Deep Research、多步规划、复杂工作流）：对话轮次多，Agent 需要跨步骤引用之前的结论。BCG 防止 Agent 遗忘已建立的结论，也防止它重复执行已完成的步骤。

**需要可审计推理的场景**（法律/医疗/金融 Agent）：置信度和来源可以被人类检查员追溯——"这个结论置信度 0.73，来自第 5 轮搜索结果的第 2 段，与第 8 轮的新证据有轻微冲突"。

**Agent 开发研究**：BCG 的信念图和置信度传播机制是一个研究 Agent 推理可靠性的工具，可以可视化 Agent 在任务执行中"信什么、信多少、为什么信"的演化过程。

---

## 路线图

BCG 下一阶段有两个方向：

1. **更严格的概率基础**：把当前的置信度计算迁移到 Bayesian 推断或其他有数学保证的不确定性框架，同时保持可审计性。
2. **Deep Research 扩展**：从信念感知的上下文管理，扩展为能规划调查路径、追踪来源时效性、调和矛盾发现、识别缺失证据并输出可审计研究报告的完整工作流。

---

## 总结

BCG 提出了一个简单但重要的区分：Agent 记忆需要回答的不只是"检索问题"（哪些信息相关），还有"信念问题"（这个信息该不该信、还有没有效）。确定性置信度 + 证据溯源 + 冲突检测的组合，是现有主流方案里没有同时做到的。对于构建需要长程推理和可靠性保证的 Agent 系统，BCG 是一个值得认真研究的内存基础设施选项。

**GitHub**: [bigai-nlco/belief-context-graph](https://github.com/bigai-nlco/belief-context-graph) ⭐59  
**文档**: [belief-context-graph.docs.buildwithfern.com](https://belief-context-graph.docs.buildwithfern.com/)  
**联系**: lijiaqi@bigai.ai · zlzheng@bigai.ai

<!--EN-->

## Belief Context Graph: Upgrading Agent Memory from Retrieval to Belief

Current agent memory systems — conversation memory, vector memory, GraphRAG, trace memory — all do the same thing at their core: **retrieval**. They answer retrieval questions: which text is relevant? which entities are related? what happened before?

But agents executing real tasks also need to answer **belief questions**:
- Should I actually believe this fact?
- Is it still valid, or has it expired?
- Did it come from a reliable source?
- Does it conflict with other evidence?
- Is it certain enough to act on?

**Belief Context Graph (BCG)** from BIGAI (Beijing Institute for General Artificial Intelligence) is a memory substrate specifically designed to answer these questions.

### Four Core Capabilities

**Belief Extraction**: BCG segments agent trajectories and extracts structured belief nodes — propositions that the agent's reasoning actually depends on — and links them into a connected graph. Unlike GraphRAG's entity extraction, BCG extracts what the agent *believes*, not what appeared in the text.

**Deterministic Confidence**: The most distinctive feature. Each belief node's confidence is computed deterministically from three components:

```
posterior_confidence = f(
    initial_confidence,   // source reliability + stance quality
    evidence_confidence,  // accumulated supporting/contradicting evidence
    factor_confidence     // propagated weights from related nodes
)
```

This is deterministic — not a fuzzy LLM score. You can trace exactly how any belief's confidence was calculated and which evidence contributed what weight.

**Evidence Provenance**: Every belief node carries exact-offset source references back to the specific conversation turn and position that produced it. The agent can know: "this conclusion came from the second paragraph of the tool call result in turn 3."

**Temporal Awareness + Relation Linking**: Run-based lifecycle with timestamps records when each belief formed and how it evolved. Forward and backward relationship edges between belief nodes form a causal decision graph.

### Architecture

BCG inserts as an optional context layer between the Agent and the model:

```
Recent turns          → [stay in raw context]
Older completed turns → [stream into Graph Construction]
                                  ↓
                       Belief Snapshot
                                  ↓
                       Injected into system prompt
```

Older turns don't pile up in the context window — they're distilled into a belief graph snapshot. Only what was extracted as belief nodes (with confidence and provenance) appears in the system prompt, simultaneously compressing token usage and improving reasoning quality.

### Benchmark Results

In BrowseComp testing, a Kimi K3 agent using BCG recognized mid-task that a search had already been completed (via belief node identity and confidence) and skipped the redundant search — exactly the pattern BCG addresses: preventing long-horizon agents from repeating completed steps.

### Comparison

Among Mem0, Zep, Letta, LangChain Memory, LlamaIndex, TrustGraph, and Semantica — BCG is the only system that combines **belief-native extraction** + **deterministic confidence** + **conflict detection**. Most systems have retrieval; none has all three of these.

### Quick Start

```bash
git clone https://github.com/bigai-nlco/belief-context-graph.git
cd belief-context-graph
make install
uv run bcg   # reference agent with guided first-run setup
```

**Python SDK**:
```python
from bcg import BCGMemory, BCGRunner

runner = BCGRunner(session_id="my-session")
runner.ingest(trajectory)

memory = BCGMemory(session_id="my-session")
beliefs = memory.observe_belief(query="user preferences")
# Returns: belief nodes with content / confidence / evidence_refs / relations
```

### Who It's For

**Long-horizon agent tasks** (Deep Research, multi-step planning): BCG prevents agents from forgetting established conclusions and repeating completed work across many turns.

**Auditable reasoning scenarios** (legal/medical/financial agents): Confidence and provenance are traceable by human reviewers — "confidence 0.73, sourced from turn 5 search result paragraph 2, with minor conflict from turn 8 evidence."

**Agent research**: BCG's belief graph and confidence propagation mechanism visualizes how an agent's beliefs evolve — what it believes, how much, and why — throughout task execution.

### Roadmap

1. More principled probabilistic foundation: migrate confidence computation to Bayesian inference or equivalent mathematically justified uncertainty frameworks
2. Deep Research extension: from belief-aware context management to a full workflow that plans investigations, tracks source provenance and temporal validity, reconciles conflicting findings, and produces auditable research outputs

BCG makes a simple but important distinction: agent memory needs to answer not just retrieval questions but belief questions. Deterministic confidence + evidence provenance + conflict detection is a combination no mainstream alternative currently achieves.

**GitHub**: [bigai-nlco/belief-context-graph](https://github.com/bigai-nlco/belief-context-graph) ⭐59  
**Docs**: [belief-context-graph.docs.buildwithfern.com](https://belief-context-graph.docs.buildwithfern.com/)
