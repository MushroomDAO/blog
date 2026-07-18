---
title: "领域专用小模型：Manning 新书《Domain-Specific SLMs》完整阅读指南"
titleEn: "Domain-Specific Small Language Models: Manning Book Overview and Reading Guide"
description: "Guglielmo Iozzia 的《Domain-Specific Small Language Models》（Manning, 2026, 376 页）完整导读：15 章覆盖 FAISS 向量检索、ONNX 量化、ProtGPT2 蛋白质生成、vLLM 离线推理、Graph RAG、AutoThink 等核心技术。作者来自 Merck & Co.，专攻生物医药 AI。附学习路径建议。"
descriptionEn: "A complete reading guide for Guglielmo Iozzia's Domain-Specific Small Language Models (Manning, 2026, 376pp). Covers all 15 chapters: FAISS embeddings, ONNX/quantization, ProtGPT2 protein generation, FlexGen offloading, vLLM offline serving, LanceDB RAG, Graph RAG, and OptiLLM AutoThink. Author is Director of AI & Applied Mathematics at Merck & Co., biomedical AI specialist."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Research"
tags: ["SLM", "小模型", "Manning", "ONNX", "RAG", "量化", "本地部署", "生物医药AI", "书评", "阅读指南"]
heroImage: "../../assets/images/domain-specific-small-language-models-manning-guide-banner.jpg"
---

> **书名**: Domain-Specific Small Language Models: Efficient AI for Local Deployment  
> **作者**: Guglielmo Iozzia（Merck & Co. AI & Applied Mathematics 总监）  
> **出版**: Manning Publications，2026 年 5 月，376 页  
> **ISBN**: 9781633436701 · **定价**: $59.99 纸质 / $47.99 电子书  
> **配套代码**: [github.com/virtualramblas/Domain-Specific-Small-Language-Models](https://github.com/virtualramblas/Domain-Specific-Small-Language-Models)（Ch2–15 全部 Colab 笔记本）

---

## 这本书是给谁看的

作者 Guglielmo Iozzia 在 Merck & Co.（默克制药）担任 AI 与应用数学总监，同时是美国人工智能学会（AAAI）杰出会员，长期做生物医药领域的 AI 落地。

这个背景直接决定了这本书的调性：**它不是在讲怎么用 ChatGPT 写邮件，而是在讲怎么在受监管行业、离线环境、边缘设备上部署一个真正可用的小模型**。

适合读这本书的人：
- 想在本地跑模型（笔记本/手机/IoT 设备），不想依赖云 API
- 在医疗、法律、金融等有合规要求的行业做 AI 应用
- 想彻底搞懂 ONNX 量化、RAG 集成、vLLM 部署这条链路
- Python 有基础，读过 HuggingFace Transformers 文档但没有系统学过模型优化

---

## 全书结构：15 章 4 条主线

配套代码仓库里有 Ch2–15 的所有 Colab 笔记本（Ch1 是纯理论导读，Ch12 应为部署架构章节，无代码）。把 15 章按主题整理：

### 第一条线：基础与工具链（Ch1–4）

**Ch1：为什么是小模型，为什么要领域专用**

预览章可以在 Manning 官网免费阅读。核心论点：

- SLM 的定义不是一个精确数字，通常指 1B–10B 参数范围，能在消费级硬件上推理
- Transformer 架构回顾：注意力机制、BERT 双向编码器 vs GPT 自回归解码器，以及两类模型分别适合什么任务
- 为什么不直接用 GPT-4o / Claude：数据隐私（医疗数据不能出网络边界）、推理成本（按 token 计费在高频任务上不可持续）、延迟（本地 0.6B 比云端 API 快一个数量级）
- 领域专用的核心优势：通用大模型对领域术语、数据格式的理解往往不如针对性微调过的小模型

**Ch2：FAISS 向量检索**

FAISS（Facebook AI Similarity Search）是后续 RAG 章节的基础。本章用实际代码做了：
- SentenceTransformers 把文本转成向量
- FAISS 建索引、查相似
- 对大规模语料做 embedding 聚类

即使你最终用的是 LanceDB 或 Pinecone，理解 FAISS 的工作原理会让你对向量数据库的索引结构有更好的直觉。

**Ch3：端到端微调——用 SLM 生成 Manim 动画代码**

这一章选了一个非常具体的目标任务：用微调后的小模型来写 Manim（Python 数学动画库）代码。具体的是一个从零开始的微调流程：数据准备 → 训练配置 → 在 Colab free tier 上跑完整个 fine-tuning。

**Ch4：GPT-Neo 推理——HuggingFace Transformers 基础**

GPT-Neo 是 EleutherAI 开源的 GPT 风格模型，这章是在打基础：用 `transformers` 库加载、推理、处理生成文本。看起来基础，但后续量化和部署章节都建立在这个基础上。

---

### 第二条线：优化与量化（Ch5–10）

这是全书最有工程密度的部分，直接对应「怎么在资源受限环境跑模型」的核心问题。

**Ch5：ONNX 转换——BERT Base Uncased**

ONNX（Open Neural Network Exchange）是一个跨框架模型交换格式，可以把 PyTorch 模型转成能在更多推理引擎（ONNX Runtime、CoreML、TensorRT）上运行的格式。这章做的是把 BERT Base Uncased 导出为 ONNX，并测量推理性能。

这是模型从训练环境走向生产的第一步。

**Ch6：GPT-2 Small 量化**

量化把模型权重从 FP32 或 FP16 压缩到 INT8 或 INT4，内存占用和推理速度都有显著改善，但会有精度损失。这章用 GPT-2 Small 演示了量化的完整流程和精度-速度权衡。

**Ch7：CodeGen 三方案对比基准测试**

这章是一个完整的评估实验：
- 原始 CodeGen 模型（Vanilla）
- ONNX 转换后的 CodeGen
- ONNX + 量化后的 CodeGen

三种方案在同一 Python 代码生成任务上跑基准，输出延迟、吞吐量、精度指标对比。这对于「我到底应该做量化吗」这个决策很有参考价值。

**Ch8：ProtGPT2 蛋白质序列生成（本地运行）**

这是全书最有特色的章节之一——也最能体现作者的生物医药背景。ProtGPT2 是 HuggingFace 上专门用于生成新型蛋白质序列的模型，在本地运行这个模型不需要生物学背景就能跑起来，但它展示了领域专用模型的典型形态：在大量蛋白质序列数据上预训练，生成的输出可以直接用于下游生物实验筛选。

**Ch9：FlexGen——把 OPT 模型权重 offload 到 RAM 和磁盘**

OPT（Meta 开源的 GPT 风格模型）参数量比一般个人设备能放进 GPU 内存的要大得多。FlexGen 通过把模型权重分层放到 GPU VRAM / CPU RAM / 磁盘，让在单机上运行超出内存容量的模型成为可能。延迟会上升，但可行性打开了。

**Ch10：ONNX 模型性能剖析**

Ch5 做了转换，这章做测量。用 ONNX Runtime 的 Profiling API 分析各层的执行时间和内存使用，找到推理瓶颈。生产优化的必要工具。

---

### 第三条线：部署与服务（Ch11–12）

**Ch11：vLLM 离线批量推理**

vLLM 是目前生产环境中最常用的 LLM 推理框架，核心技术是 PagedAttention（把 KV cache 管理类比操作系统的内存分页）。这章用 vLLM 做离线批量推理，适合不需要实时交互、但需要高吞吐量的场景（如批量文档处理、数据标注）。

**Ch12：（部署架构，无代码）**

仓库里没有 Ch12 笔记本，推测是讲模型服务的系统架构、安全 API 设计、边缘部署场景（树莓派/手机/IoT）。这部分内容在 Ch1 的简介里有提到。

---

### 第四条线：RAG 与 Agentic（Ch13–15）

**Ch13：用开源 SLM + LanceDB 搭 RAG 系统**

LanceDB 是一个嵌入式向量数据库（类似 SQLite 在向量数据库里的定位），适合本地部署不想跑外部服务的场景。这章做了完整的 RAG 管线：文档切分 → embedding → 存 LanceDB → 检索 → 用开源 SLM 生成回答。

**Ch14：Custom Graph RAG——开源 SLM + Ollama**

Graph RAG 是在标准 RAG 之上加了知识图谱结构：先从文档里抽取实体和关系，建图，检索时除了向量相似度，还可以沿图结构找到关联信息。Ollama 是本地运行各种开源模型（Llama、Mistral、Qwen 等）最简单的方式。

这一章组合了：图结构的语义检索 + Ollama 本地推理 + 开源 SLM，全程没有外部 API 调用。

**Ch15：AutoThink——OptiLLM + Qwen 2.5 0.5B**

OptiLLM 是一个推理时优化库，AutoThink 是它的其中一个功能：根据任务难度动态调整推理策略（类似于「简单问题直接答，复杂问题多想几步」）。这章用 Qwen 2.5 0.5B（仅 0.5B 参数）演示了如何让极小的模型在某些任务上有接近大模型的表现。这和 PAW（Program-as-Weights）的思路有相似之处：不是追求更大的模型，而是更聪明地使用小模型。

---

## 学习路径建议

### 路径一：完全没做过模型部署（从零开始）

**建议按序读完**，但可以略过 Ch8（生物医药领域的读者价值更高）：

```
Ch1（理论基础）→ Ch4（HF Transformers 入门）→ Ch2（向量检索）→
Ch3（微调实战）→ Ch5（ONNX 转换）→ Ch6（量化）→ Ch11（vLLM 服务）→
Ch13（RAG 入门）→ Ch14（Graph RAG）→ Ch15（推理优化）
```

### 路径二：想快速上量化 + 部署

跳过理论和微调部分，直接进优化链路：

```
Ch1（略读，了解概念）→ Ch5（ONNX）→ Ch6（量化）→ Ch7（基准测试，决定是否量化）→
Ch10（性能剖析）→ Ch11（vLLM 服务）
```

预计时间：2–3 周，每周 2–3 章 + 跑对应笔记本。

### 路径三：想做 RAG 本地化

```
Ch2（FAISS 基础）→ Ch4（模型推理基础）→ Ch13（RAG + LanceDB）→ Ch14（Graph RAG + Ollama）
```

这条路径最短，4 章可以在 1–2 周内走完，产出可以是一个跑在本地的文档问答系统。

---

## 配套代码怎么用

所有笔记本都为 **Colab free tier** 设计，不需要本地 GPU：

1. 打开 [github.com/virtualramblas/Domain-Specific-Small-Language-Models](https://github.com/virtualramblas/Domain-Specific-Small-Language-Models)
2. 找到对应章节目录（如 `Chapter 5/CH05_NB01_Iozzia.ipynb`）
3. 在 GitHub 打开 `.ipynb` 文件 → 右上角点「Open in Colab」
4. 笔记本第一个 cell 通常是 `pip install` 安装缺失的包，直接运行即可

注意：某些章节用到较大模型（如 GPT-Neo、OPT），Colab free tier 可能有内存限制，必要时换 Colab Pro 或本地机器运行。

---

## 这本书的定位

和市面上两类常见 AI 书相比：

| 类型 | 特点 | 这本书 |
|---|---|---|
| 入门教程型 | 手把手用 API 调 ChatGPT | 不是，需要有 Python 和 ML 基础 |
| 学术论文级 | 讲数学推导，轻落地 | 不是，每章都有可运行代码 |
| **本书** | 工程实践导向，覆盖从微调到 RAG 部署全链路 | 偏向于「怎么在有约束的环境里真正用上模型」|

特别值得关注的是作者的视角：来自制药行业，在数据合规、模型审计、边缘设备部署这些「大公司 AI 团队才会遇到的问题」上有真实经验，而不是假设你有无限的云资源。

这是 2026 年 5 月才出版的新书，内容覆盖了 vLLM、LanceDB、Ollama、OptiLLM 这些近两年才成熟的工具，时效性比较好。

---

> **购买链接**: [manning.com/books/domain-specific-small-language-models](https://www.manning.com/books/domain-specific-small-language-models)  
> **配套代码**: [github.com/virtualramblas/Domain-Specific-Small-Language-Models](https://github.com/virtualramblas/Domain-Specific-Small-Language-Models)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: *Domain-Specific Small Language Models* (Manning, 2026) by Guglielmo Iozzia — Director of AI & Applied Mathematics at Merck & Co. — is a 376-page engineering guide to deploying small models in constrained, regulated, or offline environments. 15 chapters with Colab notebooks covering FAISS embeddings, ONNX conversion, quantization, ProtGPT2 protein generation, FlexGen weight offloading, vLLM offline serving, LanceDB RAG, Graph RAG with Ollama, and AutoThink inference optimization.

---

## What's Actually in Each Chapter

All 13 code chapters have companion Colab notebooks (free tier compatible) at the linked GitHub repo.

**Foundations (Ch1–4)**
- Ch1: SLM definition, Transformer recap (BERT vs GPT), open-source rationale, domain-specific advantages in regulated industries. Free preview on Manning.
- Ch2: FAISS for text — SentenceTransformers embeddings, similarity search, large-corpus clustering.
- Ch3: End-to-end fine-tuning — target task is generating Manim (Python math animation) code. Full pipeline from data prep to Colab training run.
- Ch4: GPT-Neo inference via HuggingFace Transformers — baseline inference patterns used throughout the book.

**Optimization (Ch5–10)**
- Ch5: ONNX export of BERT Base Uncased — framework-agnostic model exchange format.
- Ch6: Quantization of GPT-2 Small — FP32 → INT8/INT4, accuracy-speed tradeoff measurement.
- Ch7: CodeGen benchmark — Vanilla vs ONNX vs Quantized on Python code generation. The "should I quantize?" decision chart.
- Ch8: ProtGPT2 protein sequence generation locally — the biomedical flagship chapter.
- Ch9: FlexGen with OPT — offloading model weights to CPU RAM and disk to run models larger than GPU VRAM.
- Ch10: ONNX model profiling — layer-by-layer latency and memory analysis.

**Deployment (Ch11–12)**
- Ch11: vLLM offline batch inference — PagedAttention, high-throughput offline document processing.
- Ch12: (No code notebook — deployment architecture, secure APIs, edge deployment.)

**RAG and Agentic (Ch13–15)**
- Ch13: RAG pipeline with open-source SLMs + LanceDB (embedded vector DB, no external server).
- Ch14: Custom Graph RAG + Ollama — entity extraction, knowledge graph, semantic + graph retrieval, fully local.
- Ch15: AutoThink with OptiLLM + Qwen 2.5 0.5B — dynamic reasoning strategy based on task complexity.

## Reading Path for the RAG/Local Deployment Track

Shortest path to a locally-running document QA system:

```
Ch2 (FAISS foundations) → Ch4 (inference basics) → Ch13 (RAG + LanceDB) → Ch14 (Graph RAG + Ollama)
```

1–2 weeks, 4 chapters, no external APIs.

**Links**: [Book (Manning)](https://www.manning.com/books/domain-specific-small-language-models) · [Companion Code (GitHub)](https://github.com/virtualramblas/Domain-Specific-Small-Language-Models)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
