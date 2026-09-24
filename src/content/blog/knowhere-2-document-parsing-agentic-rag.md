---
title: "Knowhere 2.0：双通道文档解析 + 层级原生记忆，让 RAG 读懂文档结构"
titleEn: "Knowhere 2.0: Dual-Track Document Parsing + Hierarchy-Native Memory for Structure-Aware RAG"
description: "Knowhere，Ontos-AI出品，3.5k stars，2026-05-07开源。2026-09版本2.0上线双通道解析：Vision Page（视觉页面）+ Text Track（文本轨）融合为同一层级原生记忆模式，既保留文本结构精度，又让复杂PDF/PPT被视觉模型整页理解。支持超长PDF（数百页）和图纸集路由，输出结果绑定到文档、章节、源页、相关资产，天然适配Agentic RAG。"
descriptionEn: "Knowhere by Ontos-AI — 3.5k stars, open-sourced 2026-05-07. Version 2.0 (September 2026) introduces dual-track parsing: Vision Page + Text Track converge into a hierarchy-native memory schema. Text-native documents retain precise extracted structure; complex PDFs and PowerPoints are processed directly as pages by vision models. Supports ultra-long PDFs (hundreds of pages) and atlas/drawing routing. All output is bound to document, section, source pages, and related assets — native fit for Agentic RAG."
pubDate: 2026-09-24
heroImage: "../../assets/images/knowhere-2-document-parsing-agentic-rag-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "rag", "document-parsing", "agentic-rag", "vector-search", "llm", "python"]
lang: zh-CN
---

`Ontos-AI/knowhere`，3.5k stars，2026-05-07 开源，Python。专做文档解析到 AI 可用记忆的全链路工具：摄取非结构化文档，输出带层级的持久化记忆，直接对接 Agentic RAG 或向量 RAG。

**GitHub**：github.com/Ontos-AI/knowhere | **Stars**：~3.5k | **License**：Apache-2.0

注意不要和 milvus-io/knowhere（Milvus 向量搜索引擎组件，C++）混淆，两者同名但完全不同的项目。

---

## 背景：RAG 的文档结构问题

传统 RAG 管道把文档切块（chunking）然后向量化，损失了文档的层级结构：哪个段落属于哪个章节，图表对应哪段文字，附录跟正文的关系。查询时能找回相关文本，但没有上下文锚点，引用也不精确。

Knowhere 的核心观点是：文档记忆应该保留层级，每个输出结果都应该绑定到它的文档、章节、源页和相关资产，形成可导航的结构，而不是一堆孤立的文本块。

---

## 版本 2.0：双通道解析

2026 年 9 月，Knowhere 发布 Document Parsing 2.0，引入双通道（dual-track）架构：

| 通道 | 适用场景 | 处理方式 |
|------|---------|---------|
| **Text Track（文本轨）** | 文本原生 PDF、Word、Markdown | 精确提取文本结构，保留层级 |
| **Vision Page（视觉页面）** | 复杂 PDF、PPT、图表混排 | 整页送入视觉模型，直接理解 |

两个通道的输出汇合到**同一套层级原生记忆模式（hierarchy-native memory schema）**：相同的检索接口、相同的层级结构、相同的引用模型。

意思是：无论文档原本是能精确提取文字的 Word 文档，还是充满图表的 PowerPoint，最终都能进入同一个可查询的记忆系统，不需要为不同文档类型维护不同的处理逻辑。

---

## 全链路流程

```
非结构化文档（PDF/PPTX/DOCX/HTML/图片）
    ↓
文档摄取 + 格式路由
    ↓
解析（Text Track 或 Vision Page）
    ↓
层级重建（章节 / 段落 / 图表 / 脚注归属）
    ↓
多模态结构化（文本 + 图片 + 表格关联）
    ↓
图构建（文档内交叉引用 + 文档间关系）
    ↓
持久化记忆（每个节点绑定文档/章节/源页/相关资产）
    ↓
RAG 检索 / Agent 调用
```

---

## 超长文档和图纸集支持

2.0 新增两类特殊场景处理：

**超长 PDF（Ultra-long PDF）**：数百页的技术文档、报告、书籍。解析管道不截断，能处理全长文档并维持跨页的层级连贯。

**图纸集（Atlas-style Documents）**：工程图纸、建筑蓝图、设计图集这类文档，通过专用的布局感知解析器（layout-aware parser）路由。文字少、视觉信息密集的文档，单纯文本提取效果差，视觉通道在这类场景有明显优势。

---

## 输出结构的差异

传统 RAG 切块器输出：
```json
{"text": "某段文字内容", "metadata": {"source": "doc.pdf", "page": 3}}
```

Knowhere 输出（简化示意）：
```json
{
  "chunk_id": "...",
  "text": "某段文字内容",
  "hierarchy": {
    "document": "doc.pdf",
    "section": "第三章 · 系统设计",
    "subsection": "3.2 · 数据层",
    "source_pages": [3, 4]
  },
  "related_assets": ["figure_3_2.png", "table_3_1"],
  "citations": ["section_3_1", "appendix_a"]
}
```

检索时不只返回文本，还返回该文本在文档中的完整位置和关联资产，Agent 可以据此进行精确引用，或追溯上下文。

---

## 安装与基本使用

```bash
pip install knowhere-ai
```

基本文档解析：

```python
from knowhere import DocumentParser

parser = DocumentParser()
memory = parser.parse("report.pdf")

# 按层级检索
results = memory.search("数据层设计方案", top_k=5)

for r in results:
    print(r.text)
    print(f"  来源: {r.hierarchy.section} / {r.hierarchy.source_pages}")
    print(f"  关联资产: {r.related_assets}")
```

---

## 与同类工具对比

| 工具 | 核心聚焦 | 层级保留 | 视觉通道 | 多模态关联 |
|------|---------|---------|---------|-----------|
| **Knowhere** | 文档 → 层级记忆 | ✅ 原生 | ✅ 2.0 新增 | ✅ |
| LlamaIndex Doc Parser | 通用管道 | 部分 | 需外部模型 | 有限 |
| Unstructured | 文档解析 | 扁平化 | 有限 | 无 |
| PyMuPDF | PDF 文字提取 | 无 | 无 | 无 |

Knowhere 的差异点是层级是一等公民，不是事后添加的 metadata。

---

## 局限性

**1. Apache-2.0 但需关注企业版边界**：核心开源，但 Ontos-AI 是商业公司，企业级功能（SLA、支持合同、云托管）走付费通道。

**2. 视觉通道的模型依赖**：Vision Page 通道需要调用外部视觉模型（frontier vision model），涉及 API 费用和延迟，本地离线场景受限。

**3. 解析质量取决于文档质量**：扫描件、低质量 PDF（无嵌入文字层）在 Text Track 效果差，Vision Page 通道虽可处理但对视觉模型能力有要求。

**4. 图构建的计算开销**：文档内跨引用图的构建对大型文档库有性能影响，需要根据实际数据量评估。

**5. Python 生态**：目前主要是 Python SDK，其他语言接入通过 REST API，生态覆盖不如 LlamaIndex 广。

---

## 怎么看这个项目

Knowhere 的核心赌注是：**文档结构本身就是 RAG 质量的核心变量**，而不是 embedding 模型或向量库的选择。这个判断对很多企业知识库场景是成立的——技术文档、合同、报告，层级和引用关系携带了大量语义，切块后丢弃是真实的损耗。

双通道 2.0 解决的是「复杂 PDF 无法精确提文字」这个已知痛点，让视觉理解和文本提取各走各的优势路径，最终汇合到同一记忆模式，是工程上合理的设计。

3.5k stars，4 个月内增长，Apache-2.0，阶段性验证了市场对这个定位的认可。

> Apache-2.0，开源仅供学习研究参考。

---

<!--EN-->

## Knowhere 2.0: Dual-Track Document Parsing + Hierarchy-Native Memory

`Ontos-AI/knowhere` (~3.5k stars, Apache-2.0, Python) was open-sourced on 2026-05-07. Version 2.0 (September 2026) introduces dual-track document parsing with a hierarchy-native memory schema.

**GitHub**: github.com/Ontos-AI/knowhere | **Note**: Not to be confused with milvus-io/knowhere (a C++ vector search engine component — entirely different project).

---

### The Core Problem

Standard RAG pipelines chunk documents and vectorize the chunks, discarding document structure: which paragraph belongs to which section, which figure belongs to which text, how appendices relate to the main body. Retrieval finds relevant text, but loses the anchor context needed for precise citation and coherent agent reasoning.

Knowhere's premise: document memory should preserve hierarchy. Every output chunk should be bound to its document, section, source pages, and related assets — a navigable structure, not a pile of isolated text fragments.

---

### Version 2.0: Dual-Track Parsing

| Track | Best For | How |
|-------|---------|-----|
| **Text Track** | Text-native PDFs, Word, Markdown | Precise structural extraction with hierarchy |
| **Vision Page** | Complex PDFs, PPT, chart-heavy docs | Full pages sent to a vision model for direct understanding |

Both tracks converge into the **same hierarchy-native memory schema**: identical retrieval interface, identical hierarchy, identical citation model. The document type becomes an internal routing decision, not a separate processing silo.

---

### Pipeline

```
Unstructured document (PDF/PPTX/DOCX/HTML/images)
    ↓
Ingestion + format routing
    ↓
Parsing (Text Track or Vision Page)
    ↓
Hierarchy reconstruction (chapter / section / figure / footnote attribution)
    ↓
Multi-modal structuring (text + image + table linking)
    ↓
Graph construction (cross-references, inter-document relations)
    ↓
Persistent memory (each node bound to document / section / source pages / related assets)
    ↓
RAG retrieval / agent queries
```

---

### Structured Output

Instead of `{"text": "...", "metadata": {"source": "doc.pdf", "page": 3}}`, Knowhere outputs nodes with full hierarchy context:

```json
{
  "text": "...",
  "hierarchy": {
    "document": "report.pdf",
    "section": "Chapter 3 · System Design",
    "subsection": "3.2 · Data Layer",
    "source_pages": [3, 4]
  },
  "related_assets": ["figure_3_2.png", "table_3_1"],
  "citations": ["section_3_1", "appendix_a"]
}
```

---

### Special Cases in 2.0

- **Ultra-long PDFs**: Hundreds of pages processed without truncation, maintaining cross-page hierarchy coherence
- **Atlas/drawing collections**: Dedicated layout-aware parser for engineering drawings and blueprint collections — high visual density, minimal text

---

### Limitations

1. **Vision track has external model dependency**: API costs and latency; limited offline/air-gapped use
2. **Scan quality matters**: Low-quality scanned PDFs degrade Text Track; Vision Page helps but still requires capable vision models
3. **Graph construction overhead**: Cross-reference graph building adds compute cost for large document collections
4. **Python-first**: Other languages access via REST API; ecosystem breadth is narrower than LlamaIndex

---

### Assessment

The bet: document structure is a first-class variable in RAG quality — not the embedding model or vector library. For enterprise knowledge bases (technical docs, contracts, reports), hierarchy and cross-references carry real semantic weight that flat chunking discards. Dual-track 2.0 addresses the well-known "complex PDF text extraction" pain point by routing vision-heavy documents through a dedicated path, converging everything into the same memory schema.

~3.5k stars over 4 months post-open-source, Apache-2.0: market validation that the positioning resonates.

> Apache-2.0. For learning and research reference only.
