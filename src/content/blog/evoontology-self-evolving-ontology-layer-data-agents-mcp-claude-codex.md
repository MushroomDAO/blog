---
title: "EvoOntology：给 Data Agent 建一个会进化的语义层"
titleEn: "EvoOntology: A Self-Evolving Ontology Layer That Grows With Your Data Agent"
description: "ruc-datalab/EvoOntology，539星，MIT，Python，中国人民大学出品，arXiv 2609.15779。面向 Data Agent 的自进化 Ontology Layer：三层结构（Content/Schema/Tool），通过 MCP 工具按需查询语义，基于执行轨迹持续进化，有门控版本机制防退步。Claude Code / Codex 插件化安装，无需 clone 仓库。DDR-Bench +20.0，BIRD +8.8，InsightBench +1.0。"
descriptionEn: "ruc-datalab/EvoOntology, 539 stars, MIT, Python. From Renmin University of China, arXiv 2609.15779. A self-evolving ontology layer for data agents: three tiers (Content/Schema/Tool), on-demand MCP semantic retrieval (no full-context injection), trajectory-driven evolution with gated versioning to prevent regression. Installable as a Claude Code or Codex plugin — no repo clone needed. DDR-Bench +20.0, BIRD +8.8, InsightBench +1.0."
pubDate: 2026-09-30
heroImage: "../../assets/images/evoontology-self-evolving-ontology-layer-data-agents-mcp-claude-codex-banner.jpg"
category: "Research"
tags: ["Data Agent", "Ontology", "MCP", "Claude Code", "Codex", "自进化", "开源拆解", "arXiv"]
lang: "zh-CN"
wechatTitle: "EvoOntology：给Data Agent建自进化语义层"
wechatDigest: "539星MIT；人大；arXiv 2609.15779；DDR-Bench+20；MCP按需查询非全量注入"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题在哪里

Data Agent 做数据分析时，有一类错误反复出现：Agent 把"营收"和"收入"当成两个不同指标查了两张表，或者把一个字段的口径理解错，导致结论偏差。

这类错误不是模型能力的问题，是**语义缺失**：原始数据本身没有告诉 Agent 指标定义、字段含义、业务约束。Agent 必须靠猜。

已有方案的代价：
- **System Prompt 注入完整文档**：上下文随数据规模爆炸，核心窗口被占用
- **RAG embedding 召回**：什么时候召回什么内容不透明，且静态，数据改了召回不更新
- **人工维护语义层**：需要持续专家投入，数据变化后容易过时

EvoOntology 想做第四条路：**版本化、可进化、按需查询**的 Ontology Layer，和 Agent 执行轨迹联动。

仓库：github.com/ruc-datalab/EvoOntology  
**Stars：539 | MIT | Python | arXiv 2609.15779 | 中国人民大学**

---

## 三层结构

Ontology Layer 由三层组成，层与层之间相互关联：

| 层 | 职责 |
|------|------|
| **Content Layer** | 类型化语义图。四类节点：Terms（概念）、Mappings（数据映射）、Constraints（业务约束）、Evidence（数据证据）。Semantic Relation 连接 Term，Structural Reference 将约束和证据挂到对应对象上 |
| **Schema Layer** | 定义四类节点的字段结构、合法的关系类型、合法的引用模式——即整个 Ontology Layer 的"表达边界" |
| **Tool Layer** | 通过 `browse_semantics`、`resolve_semantics` 和一个轻量 session manifest 向 Agent 暴露语义。会话启动时只注入 manifest，具体记录按需检索 |

**关键设计：主动访问，不是全量注入。** Agent 在执行过程中主动调用 MCP 工具查询所需语义，不是在 System Prompt 里塞入整个 ontology。随着数据规模增长，上下文开销不随之膨胀。

---

## 五步生命周期

```
Build → Use → Evolve → Evaluate → Publish or Reject
```

1. **Build**：从工作负载和底层数据构建候选语义对象，验证后发布 `ontology_v0`
2. **Use**：Data Agent 按需查询，同时记录每次工具调用和任务结果
3. **Evolve**：分析历史交互轨迹，诊断反复出现的语义问题，归因到 Content/Tool/Schema，生成局部 Candidate 补丁
4. **Evaluate**：在相同数据、相同 Agent、相同解码设置和相同交互预算下，配对比较 Parent 和 Candidate
5. **Publish or Reject**：Candidate 可复现地优于 Parent 才发布为 `ontology_vN+1`；否则保留 Parent

**门控版本机制是核心**。Evolve 步骤不是自动的——每一次更新都必须经过配对评估，必须证明可复现的提升，才能推进版本号。这个设计防止了"持续进化"变成"持续退步"。

---

## 安装方式

Claude Code 和 Codex 均以插件形式分发，无需 clone 仓库或单独 `pip install`：

**Claude Code：**
```bash
claude plugin marketplace add ruc-datalab/EvoOntology
claude plugin install evoontology@evoontology
```

新建会话后直接使用：
```
/evoontology:build-ontology
/evoontology:evolve-ontology
/evoontology:explore-ontology
```

**Codex：**
```bash
codex plugin marketplace add ruc-datalab/EvoOntology
codex plugin add evoontology-codex@evoontology
```

两个平台的工作流名称一样，只是调用语法遵循各自平台约定（`/` vs `$`）。

---

## Benchmark 数字

论文在三个 benchmark 上评估（四 backbone 子集：GPT-5.5 / GPT-5.6-sol / Claude-Sonnet-5 / Claude-Opus-4.8）：

| Benchmark | 任务类型 | ReAct 无本体层 | 初始本体层 | EvoOntology | 提升 |
|-----------|---------|---------------|------------|-------------|------|
| DDR-Bench（10-K） | 异构金融数据开放研究 | 69.5 | 81.8 | **89.5** | **+20.0** |
| BIRD | Text-to-SQL | 63.6 | 68.7 | **72.4** | **+8.8** |
| InsightBench | 业务分析与洞察生成 | 53.2 | 54.0 | **54.2** | **+1.0** |

几点需要注意：

**DDR-Bench +20.0 最亮眼，但这是论文自己设计的 benchmark**（DDR-10K 是他们自己的金融数据集），不是独立第三方验证。

**InsightBench +1.0 很小**。从 53.2 涨到 54.2，与"初始本体层"相比（54.0 → 54.2）只差 0.2。这是作者如实报告的数字，但需要知道这个任务类型对 EvoOntology 的收益有限。

**BIRD +8.8 是独立 benchmark** 上的结果，对 Text-to-SQL 场景相对有说服力。

完整的六 backbone 结果见论文表 1、3、4。以上是论文报告的四 backbone 分析子集数据。

---

## 技术选型注意事项

**两种评估模式的适用场景不同：**

| 模式 | 适用 |
|------|------|
| `fixed_split` | 有固定问题集和 Ground Truth 的 benchmark；Construction 数据用于 Build，Validation Reserve 只用于最终门控 |
| `rolling_trajectory` | 没有固定测试集的生产 workload 或冷启动项目；每个 checkpoint 后持续积累新轨迹，用独立抽样任务或 LLM Judge 门控 |

**AGPL-3.0？不，是 MIT**。License 是 MIT，商用改动不需要开源。

**Python + SQLite 核心**。Ontology Store 是 SQLite，轨迹和 checkpoint 也存在本地。不需要额外数据库。

**只支持 Claude Code 和 Codex**。如果你用其他 Agent 框架，需要自己实现接入层（文档里有 benchmark adapter 的接口规范可以参考）。

---

## 关键数字

| 指标 | 值 |
|------|----|
| Stars | 539 |
| Forks | 44 |
| License | MIT |
| 语言 | Python |
| 论文 | arXiv 2609.15779 |
| 机构 | 中国人民大学 |
| 创建时间 | 2026-09-15 |
| Benchmark | BIRD / DDR-10K / InsightBench |
| 插件支持 | Claude Code / Codex |

---

## 综合判断

EvoOntology 的工作有一个清晰的定位：Data Agent 场景下的"语义理解"不应该每次从零开始，也不应该是静态文档注入，而是一个随 Agent 使用而进化的结构化语义层。

技术路线上的三个选择值得注意：

- **按需 MCP 查询而非全量注入**：解决了静态注入上下文爆炸的问题，代价是 Agent 需要主动调用工具
- **门控版本演进**："进化"不是无监督的，每次更新都有评估闸门，这是和大多数"自适应记忆"方案的显著区别
- **插件化分发**：`claude plugin marketplace add` 直接装，不用 clone 仓库，降低了接入门槛

不确定的地方：
- DDR-10K 是自建 benchmark，数字需要独立验证
- InsightBench 收益极小（+1.0），说明并非所有分析任务都适合这个方案
- 2026-09-15 创建，半个月，非常新，生产稳定性未知

如果你在做专门的数据分析 Agent（金融报告、业务数据查询、Text-to-SQL），且对 Agent 的语义错误有强约束，EvoOntology 提供了一个目前少见的、有论文支撑的工程方案。

---

> 开源仅供学习，MIT 许可证，商业使用前建议核查 arXiv 2609.15779 论文中的评估方法细节。

---

<!--EN-->

## EvoOntology: A Self-Evolving Ontology Layer That Grows With Your Data Agent

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem

Data Agents analyzing databases and file collections run into the same failure mode repeatedly: the agent treats "revenue" and "income" as different tables, or misinterprets a field's definition, leading to wrong conclusions.

This isn't a model capability problem — it's a **semantic gap**. Raw data doesn't tell an agent what metrics mean, what the business rules are, or how entities relate. The agent has to guess.

The existing options each carry a cost:

- **Inject full documentation into the system prompt**: context grows with data complexity; the core window gets crowded
- **RAG embedding retrieval**: opaque about when what gets retrieved; static — updates don't propagate when data changes
- **Human-maintained semantic layers**: require sustained expert effort; go stale as workloads evolve

EvoOntology proposes a fourth path: a **versioned, self-evolving, on-demand** Ontology Layer that stays synchronized with the agent's actual execution behavior.

Repo: github.com/ruc-datalab/EvoOntology  
**539 stars | MIT | Python | arXiv 2609.15779 | Renmin University of China**

---

### Three-Tier Architecture

The Ontology Layer has three interconnected tiers:

| Tier | Role |
|------|------|
| **Content Layer** | Typed semantic graph with four node families: Terms, Mappings, Constraints, Evidence. Semantic Relations connect Terms; Structural References attach Constraints and Evidence to the objects they govern or support |
| **Schema Layer** | Defines the fields of the four node families, allowed Semantic Relation types, and permitted Structural Reference patterns — the representational boundaries of the ontology |
| **Tool Layer** | Exposes semantics via `browse_semantics`, `resolve_semantics`, and a compact session manifest. Only the manifest is injected at session start; detailed records are fetched on demand |

**The key design principle: active retrieval, not full injection.** The agent calls MCP tools during execution to fetch only the semantics it needs for the current step — the system prompt doesn't grow with data scale.

---

### Five-Stage Lifecycle

```
Build → Use → Evolve → Evaluate → Publish or Reject
```

1. **Build**: Derive candidate semantic objects from the workload and underlying data; publish `ontology_v0` after verification
2. **Use**: Data Agent queries the ontology on demand; tool calls and outcomes are recorded
3. **Evolve**: Diagnose recurring patterns in historical trajectories; attribute issues to Content, Tool, or Schema; generate a localized Candidate patch
4. **Evaluate**: Compare Parent and Candidate with the same data, agent, decoding settings, and interaction budget
5. **Publish or reject**: Promote to `ontology_vN+1` only when the Candidate shows reproducible improvement; retain the Parent otherwise

**The gated versioning is the core safeguard.** Evolution isn't autonomous — every update must pass a paired evaluation and prove reproducible gain before incrementing the version number. This is what separates "self-evolution" from "self-corruption."

---

### Installation

Both plugins install without cloning the repository:

```bash
# Claude Code
claude plugin marketplace add ruc-datalab/EvoOntology
claude plugin install evoontology@evoontology

# Then in a new session:
/evoontology:build-ontology
/evoontology:evolve-ontology
/evoontology:explore-ontology
```

---

### Benchmark Results

Results on three benchmarks, four-backbone analysis subset (GPT-5.5, GPT-5.6-sol, Claude-Sonnet-5, Claude-Opus-4.8):

| Benchmark | Task | Without Ontology | Initial Ontology | EvoOntology | Gain |
|-----------|------|-----------------|------------------|-------------|------|
| DDR-Bench (10-K) | Open-ended financial data research | 69.5 | 81.8 | **89.5** | **+20.0** |
| BIRD | Text-to-SQL | 63.6 | 68.7 | **72.4** | **+8.8** |
| InsightBench | Business analysis & insight generation | 53.2 | 54.0 | **54.2** | **+1.0** |

Key caveats:

**DDR-Bench is the authors' own benchmark** (their proprietary DDR-10K financial dataset). The +20.0 is striking, but it's not independently validated.

**InsightBench +1.0 is very small.** The gap between the initial ontology layer (54.0) and EvoOntology (54.2) is 0.2. The authors reported this honestly, but it signals limited benefit for that task type.

**BIRD is an independent benchmark** — the +8.8 on Text-to-SQL is the more externally validated result.

Full six-backbone results are in the paper (Tables 1, 3, 4).

---

### Things to Know Before Using

**Two evaluation modes for different contexts:**

- `fixed_split`: For benchmarks with fixed question sets and ground truth
- `rolling_trajectory`: For production workloads without fixed test sets; gates candidates using independent sampled tasks or LLM Judge

**MIT license** — no copyleft constraints on commercial modifications.

**Python + SQLite core.** No external database required. Ontology store, trajectories, and checkpoints all live locally.

**Claude Code and Codex only.** Other agent frameworks aren't supported out of the box — you'd need to implement an adapter following the benchmark `EvolutionAdapter` interface.

**Created 2026-09-15.** Two weeks old at time of writing — production stability is unknown.

---

### Verdict

EvoOntology has a clear thesis: Data Agents shouldn't re-derive domain semantics from scratch on every task, and they shouldn't rely on static injected documents either. A structured semantic layer that evolves with actual usage is the right abstraction.

Three technical choices stand out:

- **On-demand MCP retrieval**: Solves the context explosion problem of static injection, at the cost of requiring agents to actively query
- **Gated versioning**: "Self-evolving" doesn't mean "self-modifying without oversight" — every update requires paired evaluation
- **Plugin distribution**: `claude plugin marketplace add` lowers the adoption bar significantly compared to typical research repos

Where to be cautious: DDR-10K is a self-built benchmark, InsightBench gains are minimal, and the project is two weeks old.

If you're building a specialized data analysis agent (financial reports, business data queries, Text-to-SQL), and semantic errors are a hard constraint, EvoOntology offers one of the few paper-backed engineering solutions currently available for this specific problem.

---

> Open source for learning only. MIT license. Review the evaluation methodology in arXiv 2609.15779 before production deployment.
