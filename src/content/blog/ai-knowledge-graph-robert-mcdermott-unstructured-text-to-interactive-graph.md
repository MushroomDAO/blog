---
title: "AI Knowledge Graph：把任意文本扔进去，LLM 自动生成可交互知识图谱"
titleEn: "ai-knowledge-graph-robert-mcdermott-unstructured-text-to-interactive-graph"
description: "robert-mcdermott/ai-knowledge-graph 用 LLM 把非结构化文本转换成主谓宾三元组，经过实体标准化和关系推断，生成带社区检测的可交互 HTML 知识图谱。支持 Ollama 本地跑，兼容任意 OpenAI 兼容端点，2.7K stars，Apache-2.0。"
descriptionEn: "robert-mcdermott/ai-knowledge-graph uses an LLM to extract Subject-Predicate-Object triplets from unstructured text, runs entity standardization and relationship inference, and generates an interactive HTML knowledge graph with community detection. Works with Ollama locally or any OpenAI-compatible endpoint. 2.7K stars, Apache-2.0."
pubDate: "2026-08-04"
updatedDate: "2026-08-04"
category: "Tech-News"
tags: ["知识图谱", "LLM", "信息提取", "可视化", "Ollama", "Python", "开源", "Mycelium"]
heroImage: "../../assets/images/ai-knowledge-graph-robert-mcdermott-unstructured-text-to-interactive-graph-banner.jpg"
---

*by Mycelium Protocol*

---

把一段非结构化文本喂给 LLM，能直接得到一张有意义的知识图谱吗？

**[AI Knowledge Graph](https://github.com/robert-mcdermott/ai-knowledge-graph)**（robert-mcdermott）给出了一个干净的答案：可以，而且是四阶段、全自动、输出可以直接在浏览器里交互的 HTML。2.7K stars，Apache-2.0，Python 3.11+，Ollama 本地就能跑。

---

## 它做的事

输入一个文本文件，输出一个可交互的知识图谱 HTML。中间的 LLM 可以是你本机的 Ollama，也可以是 OpenAI、vLLM、LM Studio、LiteLLM（后者还能桥接 AWS Bedrock、Azure OpenAI、Anthropic）——只要是 OpenAI 协议兼容的端点就行。

效果参考：[工业革命知识图谱 demo](https://robert-mcdermott.github.io/ai-knowledge-graph/)（161 个节点，564 条边，9 个社区）。

---

## 四阶段处理流程

### Phase 1：三元组提取

文本先被切成带重叠的 chunk（默认 200 词，20 词重叠），每个 chunk 单独送给 LLM，提取 **Subject-Predicate-Object（主谓宾）三元组**：

```
"瓦特改进了蒸汽机" → (瓦特, 改进了, 蒸汽机)
"蒸汽机推动了工业化" → (蒸汽机, 推动了, 工业化)
```

13 个 chunk，提取 216 条三元组——这是原始的、碎片化的关系网络。

### Phase 2：实体标准化

同一个概念在不同 chunk 里可能有不同写法："AI"、"人工智能"、"AI system"——在图里会是三个节点，连接断裂。

LLM 审阅所有唯一实体，识别同义词组，统一命名：

```
201 个原始实体 → 标准化为 181 个标准形式 → 最终 160 个唯一实体
```

这一步让图从碎片拼接变成连贯网络。

### Phase 3：关系推断

即使标准化之后，图里还会有互相孤立的子社区——文本没有直接提到它们的关联。这一阶段做三件事：

1. **Louvain 社区检测**：识别图内的独立子图
2. **LLM 推断跨社区关系**：分析社区代表节点，推断合理的新关系
3. **传递推理 + 词法相似度推理**：规则层的自动补全

```
原始 216 条三元组 → 推断补充 → 最终 564 条（增加 370 条）
实线 = 原始关系；虚线 = 推断关系
```

### Phase 4：可视化

[PyVis](https://pyvis.readthedocs.io/) 生成单文件 HTML，内嵌 vis.js 物理引擎：

- **社区着色**：Louvain 检测结果，不同社区不同颜色
- **节点大小**：度中心性 + 介数中心性 + 特征向量中心性加权
- **实线/虚线**：区分原始关系和推断关系
- **交互控制**：缩放、平移、悬停查详情、物理引擎参数调节
- **Light / Dark 主题**

---

## 快速上手

```bash
git clone https://github.com/robert-mcdermott/ai-knowledge-graph
cd ai-knowledge-graph
uv sync
```

编辑 `config.toml`，接入本地 Ollama：

```toml
[llm]
model = "gemma3"
api_key = "sk-1234"
base_url = "http://localhost:11434/v1/chat/completions"
max_tokens = 8192
temperature = 0.2

[chunking]
chunk_size = 200
overlap = 20

[standardization]
enabled = true
use_llm_for_entities = true

[inference]
enabled = true
use_llm_for_inference = true
apply_transitive = true
```

运行：

```bash
uv run generate-graph.py --input your_text.txt --output graph.html
```

浏览器打开 `graph.html`，完成。

也可以作为包安装：

```bash
pip install --upgrade -e .
generate-graph --input your_text.txt --output graph.html
```

---

## 参数速查

| 参数 | 说明 |
|------|------|
| `--input FILE` | 输入文本文件 |
| `--output FILE` | 输出 HTML（默认 knowledge_graph.html） |
| `--config FILE` | 配置文件路径（默认 config.toml） |
| `--no-standardize` | 跳过实体标准化（更快，质量略低） |
| `--no-inference` | 跳过关系推断（更省 token） |
| `--debug` | 打印 LLM 原始响应，排查用 |
| `--test` | 用内置样例数据测试可视化 |

---

## 为什么值得关注

知识图谱构建一直是 NLP 里门槛比较高的方向——以前需要训练专门的 NER + 关系抽取模型，还要处理实体链接。LLM 的出现让 SPO 抽取变成了"写一个好的 prompt"，而这个项目把 prompt 工程、实体消歧、关系推断和可视化全部打包成了一个 `uv run` 能跑的工具。

兼容任意 OpenAI 协议端点意味着你可以完全本地（Ollama + Gemma3），也可以接 Claude/GPT——隐私敏感的文档不出本机，公开文档选最强模型，配置一行切换。

三阶段的处理设计（提取 → 标准化 → 推断）每一步都可以独立关闭，方便在速度和质量之间做取舍。

2.7K stars，382 forks，仍在活跃更新（最近更新 2026-08-04）。Apache-2.0 开源，可以直接嵌商业产品。

仓库：[github.com/robert-mcdermott/ai-knowledge-graph](https://github.com/robert-mcdermott/ai-knowledge-graph) · Demo：[robert-mcdermott.github.io/ai-knowledge-graph](https://robert-mcdermott.github.io/ai-knowledge-graph/)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## AI Knowledge Graph: Feed Any Text to an LLM, Get an Interactive Knowledge Graph

*by Mycelium Protocol*

Can you feed unstructured text to an LLM and get a meaningful knowledge graph out? **[AI Knowledge Graph](https://github.com/robert-mcdermott/ai-knowledge-graph)** (robert-mcdermott) answers that cleanly: yes — four phases, fully automated, output as interactive HTML you can explore in a browser. 2.7K stars, Apache-2.0, Python 3.11+, runs locally with Ollama.

### What It Does

Input: a text file. Output: an interactive knowledge graph HTML file. The LLM in the middle can be local Ollama, OpenAI, vLLM, LM Studio, or LiteLLM (which bridges AWS Bedrock, Azure OpenAI, Anthropic, and more) — any OpenAI-protocol-compatible endpoint works.

See it live: [Industrial Revolution knowledge graph demo](https://robert-mcdermott.github.io/ai-knowledge-graph/) — 161 nodes, 564 edges, 9 communities.

### Four-Phase Pipeline

**Phase 1: Triple Extraction**

Text is split into overlapping chunks (default: 200 words with 20-word overlap). Each chunk goes to the LLM to extract **Subject-Predicate-Object (SPO) triplets**:

```
"Watt improved the steam engine" → (Watt, improved, steam engine)
"Steam engines drove industrialization" → (steam engine, drove, industrialization)
```

13 chunks, 216 extracted triplets — raw and fragmented at this point.

**Phase 2: Entity Standardization**

The same concept can appear multiple ways across chunks: "AI", "artificial intelligence", "AI system" — creating three separate nodes with broken connections. The LLM reviews all unique entities, identifies synonym groups, and unifies naming:

```
201 raw entities → standardized into 181 forms → 160 unique entities
```

This turns a fragmented patchwork into a coherent network.

**Phase 3: Relationship Inference**

Even after standardization, isolated sub-communities remain — text didn't explicitly connect them. This phase does three things:

1. **Louvain community detection**: identifies disconnected sub-graphs
2. **LLM-assisted cross-community inference**: analyzes representative nodes and infers plausible new relationships
3. **Transitive inference + lexical similarity rules**: rule-based automatic completion

```
216 original triplets → inference adds 370 more → 564 total
Solid lines = original; dashed lines = inferred
```

**Phase 4: Visualization**

[PyVis](https://pyvis.readthedocs.io/) generates a self-contained HTML file with an embedded vis.js physics engine:

- **Community coloring**: Louvain results, distinct color per community
- **Node size**: weighted by degree, betweenness, and eigenvector centrality
- **Solid vs. dashed lines**: original vs. inferred relationships
- **Interactive controls**: zoom, pan, hover for details, physics controls
- **Light / dark themes**

### Quick Start

```bash
git clone https://github.com/robert-mcdermott/ai-knowledge-graph
cd ai-knowledge-graph
uv sync
```

Configure `config.toml` for local Ollama:

```toml
[llm]
model = "gemma3"
api_key = "sk-1234"
base_url = "http://localhost:11434/v1/chat/completions"
temperature = 0.2

[standardization]
enabled = true
use_llm_for_entities = true

[inference]
enabled = true
use_llm_for_inference = true
```

Run:

```bash
uv run generate-graph.py --input your_text.txt --output graph.html
```

Open `graph.html` in a browser. Done.

### Key Flags

| Flag | Effect |
|------|--------|
| `--no-standardize` | Skip entity standardization (faster, slightly lower quality) |
| `--no-inference` | Skip relationship inference (saves tokens) |
| `--debug` | Print raw LLM responses for debugging |
| `--test` | Test visualization with built-in sample data |

### Why This Matters

Knowledge graph construction used to require training dedicated NER + relation extraction models plus entity linking pipelines. LLMs make SPO extraction a prompt-engineering problem, and this project packages the prompt engineering, entity disambiguation, relationship inference, and visualization into a single `uv run` command.

Compatibility with any OpenAI-protocol endpoint means you can go fully local (Ollama + Gemma3) for sensitive documents or use the strongest available model for public content — one config line to switch.

The three-phase design (extract → standardize → infer) lets each step be disabled independently, making it easy to trade quality for speed or token budget.

2.7K stars, 382 forks, actively maintained (last update 2026-08-04). Apache-2.0, embeddable in commercial products.

Repository: [github.com/robert-mcdermott/ai-knowledge-graph](https://github.com/robert-mcdermott/ai-knowledge-graph) · Demo: [robert-mcdermott.github.io/ai-knowledge-graph](https://robert-mcdermott.github.io/ai-knowledge-graph/)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
