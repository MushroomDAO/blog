---
title: "Semantica：AI 界的开源 Palantir，用知识图谱解决企业 AI 最难的问题——决策溯源"
titleEn: "semantica-graph-native-ai-provenance-enterprise-knowledge-graph"
description: "Semantica（GitHub: semantica-agi/semantica，⭐11,136，MIT，v0.6.7）是一套图原生 AI 基础设施：把企业多源数据自动构建成知识图谱，每一个 AI 决策都作为图节点记录下来，带完整因果链和 W3C PROV-O 溯源，支持 Neo4j/AWS Neptune/RDF 等多种图数据库，原生集成 MCP/Claude Code/CrewAI/Agno，pip 一行安装。核心价值：让 AI 决策可解释、可审计、可追问。"
descriptionEn: "Semantica (GitHub: semantica-agi/semantica, ⭐11,136, MIT, v0.6.7) is a graph-native AI infrastructure layer: auto-builds enterprise knowledge graphs from multi-source data, records every AI decision as a graph node with full causal chains and W3C PROV-O provenance, supports Neo4j/AWS Neptune/RDF backends, native MCP/Claude Code/CrewAI/Agno integration, pip-installable. Core value: make AI decisions explainable, auditable, and traceable."
pubDate: "2026-08-29"
updatedDate: "2026-08-29"
category: "Research"
tags: ["知识图谱", "AI可解释性", "Semantica", "决策溯源", "企业AI", "开源", "合规审计"]
heroImage: "../../assets/images/semantica-graph-native-ai-provenance-enterprise-knowledge-graph-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/semantica-agi/semantica | ⭐ 11,136 | MIT 许可证  
版本：v0.6.7（2026-08-28） | 语言：Python 3.8+ | PyPI：`pip install semantica`  
官网：https://getsemantica.ai | 文档：https://docs.getsemantica.ai

---

## 问题：向量数据库解决不了"为什么"

当前 AI 应用的主流记忆层是**向量数据库 + RAG**。这个方案解决了"找到相似内容"，但有三个在企业场景中致命的盲区：

1. **决策不留痕**——AI 给出结论，但没有记录它为什么这样决定。下次被问起，说不清楚。
2. **冲突静默覆盖**——两个数据源说了矛盾的话？向量库悄悄用新的覆盖旧的，你永远不知道发生了什么。
3. **无法应对"为什么"的追问**——监管机构、审计人员、客户投诉时问的第一句话都是"为什么AI做了这个决定"，嵌入向量给不出答案。

| | 向量DB + RAG | 纯LLM记忆 | **Semantica** |
|---|---|---|---|
| 召回方式 | 嵌入相似度 | Token窗口 | 图遍历 + 语义搜索 |
| 决策历史 | 不存储 | 不存储 | 一等公民，可查询 |
| 溯源 | 无 | 无 | W3C PROV-O，源头追踪 |
| 推理 | 无 | 黑盒 | 前向链、Rete、Datalog、SPARQL |
| 冲突检测 | 静默覆盖 | 静默覆盖 | 检测并标记，不自动覆盖 |
| 时间旅行 | 无 | 无 | 任意时间点图快照 |
| 合规导出 | 无 | 无 | PROV-O、SHACL、OWL、RDF |
| 策略执行 | 无 | 无 | 内置规则引擎 + SHACL |
| 多agent共享上下文 | 各自独立 | 各自独立 | 统一共享智能层 |

Semantica **不替换**你的 LLM、向量库或 agent 框架——它在下面加一层，专门解决"可解释性、可追溯性、可审计性"。

---

## 它是什么

> "Ingest your enterprise data, extract what matters, build a Context Graph and knowledge graph, and run graph analytics and causal reasoning over all of it, with full decision provenance baked in."

一条从数据源到图谱到决策记录的完整流水线，每个阶段都是独立可用的 Python 模块：

```
Sources → Ingest → Parse → Extract → Conflict Detection → Deduplication
  → Knowledge Graph → [Ontology · Reasoning · Provenance · Decisions]
  → Polyglot Graph Store (RDF/LPG) → Export / REST / MCP / CLI
```

---

## 五个核心能力

### 1. 多源数据自动构建知识图谱

不需要手动建图。Semantica 的 `ingest` 模块直接吃进几十种数据源：

```python
from semantica.ingest import FileIngestor, WebIngestor, DBIngestor

# PDF、DOCX、HTML、CSV、JSON 整个目录一次处理
docs = FileIngestor().ingest_directory("./contracts/", recursive=True)

# 数据库整张表
rows = DBIngestor().ingest_database(
    connection_string="postgresql://user:pass@localhost/mydb",
    include_tables=["customer_events"],
)

# 企业数据平台——直接从 Databricks/Snowflake 里的表建图，不需要先导出 CSV
databricks = DatabricksIngestor(host="...", token="...", catalog="main")
customers = databricks.ingest_table("customers", limit=10_000)
lineage   = databricks.get_table_lineage("customers")  # Unity Catalog 血缘
```

**支持的数据源（全）：** PDF/DOCX/PPTX/HTML/TXT/CSV/JSON/Excel · 网页 · RSS/Atom · REST API · PostgreSQL/MySQL/SQLite/Oracle/SQL Server · Parquet · Databricks（Unity Catalog + Delta Lake）· Snowflake · Git 仓库 · Email（IMAP/POP3）· Kafka/RabbitMQ/Kinesis/Pulsar · MCP 资源 · DuckDB · Elasticsearch · Google Drive · MongoDB · HuggingFace · Pandas

然后自动做：命名实体识别（NER）→ 关系抽取 → 事件检测 → RDF 三元组 → 冲突检测 → 语义去重 → 知识图谱。

### 2. 决策溯源引擎

Semantica 里，每个 AI 决策不是一行日志，而是**图节点 + 因果链**：

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)

# 记录贷款审批决策链
app_id = graph.record_decision(
    category="credit_application",
    scenario="Personal loan, $85k income, 31% DTI",
    reasoning="Income meets threshold; clean 36-month credit history",
    outcome="proceed_to_underwriting",
    confidence=0.88,
    metadata={"applicant_id": "A-7291"},
)
uw_id = graph.record_decision(
    category="loan_underwriting",
    outcome="approved",
    reasoning="DTI within policy",
    confidence=0.94,
)

# 链接因果关系
graph.add_causal_relationship(app_id, uw_id, relationship_type="CAUSED")

# 追问"为什么"
chain   = graph.trace_decision_chain(uw_id)       # 完整因果上溯链
similar = graph.find_similar_decisions("31% DTI loan approval")  # 历史先例
impact  = graph.analyze_decision_impact(uw_id)    # 下游影响图
ok      = graph.check_decision_rules({"category": "loan_underwriting"})  # 策略合规门控
```

三种关系类型：`CAUSED`（直接因果）、`INFLUENCED`（间接影响）、`PRECEDENT_FOR`（先例）。

### 3. 冲突检测：不静默覆盖

`semantica.conflicts` 模块是 Semantica 区别于普通 RAG 系统的核心差异点之一：

- 多个数据源对同一实体有矛盾描述时，**标记冲突而不是覆盖**
- 冲突进入图节点，记录来源和时间戳，可追溯是哪个数据源引入的
- 高合规场景（金融、医疗、法律）的数据质量基础

### 4. W3C PROV-O 标准溯源 + 合规导出

```python
from semantica.provenance import ProvenanceManager
from semantica.export import RDFExporter

prov = ProvenanceManager(storage_path="./audit.db")

# 为每个实体追踪来源
prov.track_entity(
    "patient_P4821",
    source="ehr/medication_orders.json",
    metadata={"extractor": "NamedEntityRecognizer"},
)

# 导出审计报告——监管机构可接受的格式
kg = graph.to_kg_dict()
RDFExporter().export(kg, "audit_trail.ttl", format="turtle")  # Turtle RDF
RDFExporter().export(kg, "audit.json",      format="json")    # JSON
# 也支持 CSV、JSON-LD、OWL、Parquet、Cypher
```

W3C PROV-O 是大多数合规框架接受的溯源格式，可直接提交给监管机构审查。

### 5. 可解释推理引擎

四种推理方式，结果路径完全可追踪：

```python
from semantica.reasoning import ReteEngine, Rule, Fact, RuleType

# Rete 网络：AML 反洗钱规则引擎示例
rete = ReteEngine()
rete.build_network([
    Rule(
        rule_id="aml_flag",
        name="高风险交易",
        conditions=[
            {"field": "amount",  "operator": ">",  "value": 10_000},
            {"field": "country", "operator": "in", "value": ["IR", "KP", "SY"]},
        ],
        conclusion="flag_for_compliance_review",
        rule_type=RuleType.IMPLICATION,
    ),
])
rete.add_fact(Fact("tx_001", "transaction", [{"amount": 15_000, "country": "IR"}]))
flagged = rete.match_patterns()
# → [{"rule": "aml_flag", "conclusion": "flag_for_compliance_review", ...}]
```

支持：Rete 网络 · 前向链（Forward Chaining）· Datalog · SPARQL。每一步推理都有 `ExplanationGenerator` 生成结构化解释路径。

---

## 图数据库支持（多后端，代码无感切换）

**RDF 三元组存储：** 嵌入式 Oxigraph（零依赖，默认）· Blazegraph · Apache Jena · Eclipse RDF4J

**有标签属性图（LPG）：** Neo4j · FalkorDB · Apache AGE · AWS Neptune

**向量存储：** FAISS · Qdrant · Weaviate · Milvus · Pinecone · PgVector · SQLite · 内存

换后端只需改一行配置，其余代码不动：

```python
# 本地开发用嵌入式
graph = ContextGraph(backend="oxigraph")

# 生产环境接 Neo4j
graph = ContextGraph(backend="neo4j", uri="bolt://neo4j:7687", user="neo4j", password="...")

# 云端接 AWS Neptune
graph = ContextGraph(backend="neptune", endpoint="wss://your-cluster.neptune.amazonaws.com/gremlin")
```

---

## 生态集成

| 接入方式 | 说明 |
|---------|------|
| MCP Server | `semantica mcp` 启动，30秒接入 Claude Code / Cursor / Cursor Agent |
| Claude Code | 原生集成，作为工具使用 |
| CrewAI | `from semantica.integrations.crewai import SemanticaTool` |
| Agno | 多 agent 团队共享一个 ContextGraph |
| LangChain | 作为知识图谱 retriever |
| REST API | 标准 HTTP API，任何语言可调用 |
| CLI | `semantica ingest` / `semantica build-kg` / `semantica query` / `semantica export` |

**MCP 30秒上手：**

```bash
pip install semantica
semantica mcp  # 启动 MCP 服务
# 在 Claude Code / Cursor 里 mcp add semantica http://localhost:8765
```

---

## 企业落地建议：四个场景

### 场景 1：金融风控决策溯源（最典型）

**问题：** 贷款 AI 拒了一笔申请，借款人投诉，监管要求解释。

**Semantica 的做法：**
1. 每次风控决策记为图节点（`record_decision`）+ 因果链（`add_causal_relationship`）
2. 所有依据数据（征信、收入证明、历史记录）作为 PROV-O 溯源附在节点上
3. 投诉时：`trace_decision_chain(decision_id)` 一行代码，输出完整因果链
4. 导出为 Turtle RDF 提交监管：`RDFExporter().export(kg, "audit.ttl")`

**落地要点：**
- 使用 SHACL 约束验证每个决策节点的必填字段
- 开启双时态（bi-temporal）记录：有效时间 vs. 录入时间分开追踪
- Rete 规则引擎写死合规规则（黑名单国家、阈值），与 LLM 决策层解耦

### 场景 2：医疗 AI 药物相互作用审计

```python
# 记录药物冲突检测决策链
d1 = graph.record_decision(
    category="drug_interaction_check",
    scenario="患者 P-4821：华法林 + 胺碘酮联合用药",
    reasoning="胺碘酮增强华法林抗凝效果，存在出血风险",
    outcome="flag_for_review",
    confidence=0.91,
)
d2 = graph.record_decision(
    category="dosage_adjustment",
    reasoning="按交互严重度减少华法林剂量 30%，5天后复查 INR",
    outcome="dose_reduced_30pct",
    confidence=0.87,
)
graph.add_causal_relationship(d1, d2, relationship_type="CAUSED")

# 导出完整审计轨迹
RDFExporter().export(graph.to_kg_dict(), "medical_audit.ttl", format="turtle")
```

**注意：** Semantica 解释的是系统外部行为（输入数据、决策记录、溯源链），**不是** LLM 内部的思维链。这是系统级可解释性，不是模型级。

### 场景 3：企业知识管理（内部知识库升级）

现状：企业文档存在向量库里，RAG 给出答案但不知道依据哪份文件哪个版本。

**升级方案：**
```python
# 建图
sources = FileIngestor().ingest_directory("./internal-docs/", recursive=True)
kg = GraphBuilder(merge_entities=True, enable_temporal=True).build(sources)

# 查知识来源
answer = ctx.retrieve("Q3 销售政策变更是什么时候生效的？")
# → 返回结果 + 源文档 + 生效日期 + 溯源链
```

关键收益：
- 版本追踪：同一条政策的历史演变全部在图里，点-时间快照可回溯
- 冲突检测：旧版政策和新版政策描述矛盾时自动标记，不会混用
- 多部门共享：多个 agent/系统共享同一个 ContextGraph，上下文不割裂

### 场景 4：多 Agent 系统共享上下文

```python
from semantica.context import ContextGraph, AgentContext
from semantica.vector_store import VectorStore

# 所有 agent 共享同一个 graph
shared_graph = ContextGraph(advanced_analytics=True)
vs = VectorStore(backend="qdrant")

# Agent A 的决策
ctx_a = AgentContext(vector_store=vs, knowledge_graph=shared_graph)
ctx_a.store("Agent A 完成了市场分析报告，结论：Q3 重点押注东南亚", conversation_id="task_001")

# Agent B 可以查到 Agent A 的上下文
ctx_b = AgentContext(vector_store=vs, knowledge_graph=shared_graph)
result = ctx_b.retrieve("Q3 市场策略是什么？")
# → 命中 Agent A 的结论，带完整因果链
```

---

## 快速上手（5分钟）

```bash
pip install semantica

# 验证安装
semantica doctor
# Python 3.11.9        pass
# semantica 0.6.7      pass
# faiss vector store   pass
# Config file          pass   ~/.semantica/config.yaml
```

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)

# 记录第一个决策
decision_id = graph.record_decision(
    category="vendor_selection",
    scenario="选择 HIPAA 工作负载的云服务商",
    reasoning="AWS 提供 BAA 协议，医疗合规工具成熟，团队已有经验",
    outcome="selected_aws",
    confidence=0.93,
)

# 追问
chain = graph.trace_decision_chain(decision_id)
print(chain)
```

**MCP 接入 Claude Code：**

```bash
semantica mcp  # 本地启动 MCP 服务（默认 localhost:8765）
# 在 Claude Code 里
claude mcp add semantica http://localhost:8765
```

---

## 关键模块一览

| 模块 | 功能 |
|------|------|
| `semantica.ingest` | 多源数据摄入（40+ 数据源） |
| `semantica.semantic_extract` | NER、关系抽取、事件检测、三元组生成 |
| `semantica.kg` | 图构建、中心性分析、社区检测、链接预测 |
| `semantica.reasoning` | 前向链、Rete、Datalog、SPARQL 可解释推理 |
| `semantica.vector_store` | 8 种向量后端 + 混合检索 |
| `semantica.split` | GraphRAG 原生文档分块（实体感知/关系感知） |
| `semantica.provenance` | W3C PROV-O 血缘追踪 |
| `semantica.ontology` | OWL 生成、SHACL 验证、SKOS 词汇管理 |
| `semantica.conflicts` | 跨源冲突检测与解决 |
| `semantica.deduplication` | 大规模实体解析 |
| `semantica.pipeline` | 声明式并行 Pipeline DSL |
| `semantica.export` | RDF / OWL / Parquet / Cypher / JSON-LD 导出 |
| `semantica.visualization` | 交互式图谱、本体层级、时间轴浏览器 |

---

## 适合和不适合 Semantica 的场景

**适合：**
- 监管要求 AI 决策可审计的行业（金融、医疗、法律、政府）
- 多数据源 + 多 agent 系统，需要共享、去冲突的知识层
- 需要"决策历史 + 先例搜索"功能的系统
- 自托管优先、不愿意数据出服务器的团队

**不适合：**
- 纯粹需要高速语义搜索（直接用 Qdrant/Weaviate 就够了）
- 小型个人项目、对可解释性没有要求
- 需要解释 LLM 内部推理过程（那是模型内部问题，Semantica 处理不了）

---

**相关链接**

- GitHub：https://github.com/semantica-agi/semantica
- 官网：https://getsemantica.ai
- 文档：https://docs.getsemantica.ai
- PyPI：https://pypi.org/project/semantica/
- Discord：https://discord.gg/sV34vps5hH
- Twitter：https://x.com/BuildSemantica

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

<!--EN-->

## Semantica: Open-Source Palantir for AI — Making Every AI Decision Traceable and Auditable

*by Mycelium Protocol*

---

GitHub: https://github.com/semantica-agi/semantica | ⭐ 11,136 | MIT License  
Version: v0.6.7 (2026-08-28) | Language: Python 3.8+ | PyPI: `pip install semantica`  
Website: https://getsemantica.ai | Docs: https://docs.getsemantica.ai

---

### The Problem: Vector Databases Can't Answer "Why"

The dominant AI memory architecture today is vector database + RAG. This solves "find similar content" but has three fatal blind spots for enterprise use:

1. **No decision trail** — the AI produced a conclusion but left no record of why. When challenged, you can't reconstruct the reasoning.
2. **Silent conflict overwrite** — two sources contradict each other? The vector store quietly uses the newer one, and you never know it happened.
3. **Unresponsive to "why"** — regulators, auditors, and complainants ask "why did the AI do that?" Embedding vectors give no answer.

| | Vector DB + RAG | Plain LLM Memory | **Semantica** |
|---|---|---|---|
| Recall method | Embedding similarity | Token window | Graph traversal + semantic search |
| Decision history | Not stored | Not stored | First-class queryable objects |
| Provenance | None | None | W3C PROV-O, source-linked |
| Reasoning | None | Black box | Forward chain, Rete, Datalog, SPARQL |
| Conflict detection | Silent overwrite | Silent overwrite | Detected, flagged, resolved |
| Time travel | No | No | Point-in-time graph snapshots |
| Compliance export | None | None | PROV-O, SHACL, OWL, RDF |
| Multi-agent shared context | Separate per agent | Separate per agent | Single shared intelligence layer |

Semantica **complements** rather than replaces your LLM, vector store, or agent framework — it adds the decision records, causal reasoning, provenance, conflict detection, and audit trails underneath.

---

### What It Is

```
Sources → Ingest → Parse → Extract → Conflict Detection → Deduplication
  → Knowledge Graph → [Ontology · Reasoning · Provenance · Decisions]
  → Polyglot Graph Store (RDF/LPG) → Export / REST / MCP / CLI
```

Every stage is an independently importable Python module.

---

### Five Core Capabilities

**1. Multi-Source Knowledge Graph Auto-Construction**

```python
from semantica.ingest import FileIngestor, DBIngestor

# Ingest entire directory of contracts (PDF, DOCX, HTML, TXT)
docs = FileIngestor().ingest_directory("./contracts/", recursive=True)

# Pull directly from Databricks — no CSV export needed
databricks = DatabricksIngestor(host="...", token="...", catalog="main")
customers = databricks.ingest_table("customers", limit=10_000)
```

Sources: PDF/DOCX/Excel · Web pages · PostgreSQL/MySQL/Oracle/SQL Server · Databricks (Unity Catalog) · Snowflake · Kafka/Kinesis · Email · Git repos · MCP resources · Google Drive · MongoDB · 40+ more.

Then automatically: NER → relation extraction → event detection → RDF triplets → conflict detection → semantic deduplication → knowledge graph.

**2. Decision Provenance Engine**

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)

# Record the full loan decision chain
app_id = graph.record_decision(
    category="credit_application",
    scenario="Personal loan, $85k income, 31% DTI",
    reasoning="Income meets threshold; clean 36-month credit history",
    outcome="proceed_to_underwriting",
    confidence=0.88,
    metadata={"applicant_id": "A-7291"},
)
uw_id = graph.record_decision(
    category="loan_underwriting",
    outcome="approved",
    reasoning="DTI within policy",
    confidence=0.94,
)

graph.add_causal_relationship(app_id, uw_id, relationship_type="CAUSED")

# Ask "why" and get a structured answer
chain   = graph.trace_decision_chain(uw_id)
similar = graph.find_similar_decisions("31% DTI loan approval")
ok      = graph.check_decision_rules({"category": "loan_underwriting"})
```

**3. Conflict Detection: No Silent Overwrite**

When multiple sources contradict each other on the same entity, `semantica.conflicts` flags the contradiction instead of silently discarding the older fact. Both versions persist in the graph with source attribution and timestamps, auditable by design.

**4. W3C PROV-O Provenance + Compliance Export**

```python
from semantica.provenance import ProvenanceManager
from semantica.export import RDFExporter

prov = ProvenanceManager(storage_path="./audit.db")
prov.track_entity("patient_P4821", source="ehr/medication_orders.json")

# Export in regulator-accepted format
RDFExporter().export(graph.to_kg_dict(), "audit_trail.ttl", format="turtle")
```

W3C PROV-O is the provenance format accepted by most compliance frameworks for regulator submission.

**5. Explainable Reasoning Engine**

```python
from semantica.reasoning import ReteEngine, Rule, Fact, RuleType

rete = ReteEngine()
rete.build_network([
    Rule(
        rule_id="aml_flag",
        conditions=[
            {"field": "amount",  "operator": ">",  "value": 10_000},
            {"field": "country", "operator": "in", "value": ["IR", "KP", "SY"]},
        ],
        conclusion="flag_for_compliance_review",
        rule_type=RuleType.IMPLICATION,
    ),
])
rete.add_fact(Fact("tx_001", "transaction", [{"amount": 15_000, "country": "IR"}]))
flagged = rete.match_patterns()
```

Supports: Rete network · Forward chaining · Datalog · SPARQL. Every inference step generates a structured explanation path.

---

### Enterprise Deployment: Four Scenarios

**Scenario 1: Financial Risk Decision Audit**

Deploy Semantica as the decision provenance layer under your credit/risk AI. Every approval or rejection becomes a graph node with `record_decision()`. When a regulator or complainant asks "why was this loan declined?", `trace_decision_chain(decision_id)` returns the full causal ancestry in one call, exportable as Turtle RDF directly for submission.

Key setup: SHACL constraints on required decision fields; Rete rules for hard compliance gates (blacklisted countries, threshold amounts); bi-temporal recording to separate valid time from recorded time.

**Scenario 2: Medical AI Drug Interaction Audit**

Record drug interaction flagging and dosage adjustment decisions as a causally-linked chain. Export as PROV-O for medical record audit. Important: Semantica explains the *system's external behavior* (input data, decision records, provenance chain) — not the LLM's internal chain-of-thought.

**Scenario 3: Enterprise Knowledge Management**

Upgrade from vector RAG to a graph-backed knowledge layer. Policies, contracts, and documentation become graph nodes with provenance and version tracking. Conflicting versions of the same policy are flagged, not merged silently. Point-in-time snapshots let you reconstruct what the system "knew" on any past date.

**Scenario 4: Multi-Agent Shared Context**

All agents in a team share a single `ContextGraph`. When Agent A records an analysis result, Agent B can retrieve it with full provenance — who produced it, from what data, when. Eliminates the fragmented-context problem in multi-agent pipelines.

---

### Quick Start

```bash
pip install semantica
semantica doctor  # verify install
```

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)
decision_id = graph.record_decision(
    category="vendor_selection",
    scenario="Cloud provider for HIPAA workload",
    reasoning="AWS offers BAA, mature HIPAA tooling",
    outcome="selected_aws",
    confidence=0.93,
)
chain = graph.trace_decision_chain(decision_id)
```

**MCP integration with Claude Code:**
```bash
semantica mcp  # starts MCP server at localhost:8765
claude mcp add semantica http://localhost:8765
```

---

### What Semantica Is Not

- It does **not** explain what happens inside the LLM (internal reasoning stays opaque, as it does for any external system)
- It is **not** a replacement for your vector store if all you need is fast semantic search
- It is **not** suitable if you have no auditability or compliance requirements

---

**Links**

- GitHub: https://github.com/semantica-agi/semantica
- Website: https://getsemantica.ai
- Docs: https://docs.getsemantica.ai
- PyPI: https://pypi.org/project/semantica/
- Discord: https://discord.gg/sV34vps5hH

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
