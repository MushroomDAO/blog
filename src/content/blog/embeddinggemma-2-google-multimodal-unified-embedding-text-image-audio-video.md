---
title: "EmbeddingGemma 2：Google 把文字、图片、声音、视频放进同一个向量空间"
titleEn: "EmbeddingGemma 2: Google Puts Text, Image, Audio, and Video Into a Single Embedding Space"
description: "Google DeepMind 发布 EmbeddingGemma 2（google/embeddinggemma-2），Apache-2.0，740M 参数（文本基座 270M，视觉编码器 170M，音频编码器 300M），基于 Gemma 4 架构。核心特性：四模态统一到 768 维向量空间，8K 上下文（上一代 4 倍），MRL 支持 128/256/512/768 维截断（最高 6x 存储压缩）。MTEB 代码基准 78.68（上一代 68.76，↑+14.4%）。模块化加载：仅需文本时只加载 270M 基座；量化后 191MB 内存，浏览器 20–70ms 延迟，手机可运行。"
descriptionEn: "Google DeepMind releases EmbeddingGemma 2 (google/embeddinggemma-2), Apache-2.0, 740M parameters (270M text backbone, 170M vision encoder, 300M audio encoder), built on the Gemma 4 architecture. Core features: all four modalities mapped to a shared 768-dimensional space, 8K context (4x previous gen), native MRL support (128/256/512/768d truncation, up to 6x storage reduction). MTEB code benchmark: 78.68 vs 68.76 previous gen (+14.4%). Modular loading: text-only use loads only the 270M backbone; quantized to 191MB, 20–70ms browser latency, mobile-capable."
pubDate: 2026-10-07
heroImage: "../../assets/images/embeddinggemma-2-google-multimodal-unified-embedding-text-image-audio-video-banner.jpg"
category: "Tech-Experiment"
tags: ["嵌入模型", "多模态", "Google", "端侧AI", "RAG", "开源模型"]
lang: "zh-CN"
wechatTitle: "EmbeddingGemma 2：四模态统一嵌入向量"
wechatDigest: "Apache-2.0；740M；四模态768维统一；MTEB代码78.68；端侧191MB；MRL 6x压缩"
---

大多数语义搜索系统都有同一个问题：**文字用一个 embedding 模型，图片用另一个，音频又是另一个，跨模态检索要手动对齐**。你有一段录音，想用一句话去搜相关片段——通常需要先把音频转文字，再嵌入文字，才能和文字库比较。能直接用的媒介就是不一样的。

EmbeddingGemma 2 把这个问题在架构上消掉了：一个模型，四种模态，一个向量空间。

HuggingFace: https://huggingface.co/google/embeddinggemma-2 | ⭐ 759 | Apache-2.0

---

## 架构：四个模态，一个坐标系

模型由三个部分组成，可以按需加载：

| 模块 | 参数量 | 职责 |
|------|--------|------|
| 文本基座（backbone + embedder） | 270M（130M + 140M） | 处理文本和代码 |
| 视觉编码器 | 170M | 处理图片和视频帧 |
| 音频编码器 | 300M | 处理音频 |

所有模态的输出都投影到同一个 **768 维向量空间**。一句话和一张图片、一段录音的语义如果相近，它们的余弦相似度就会高——不需要跨模态转译，不需要把音频先转文字。

---

## 规格

| 项目 | 值 |
|------|-----|
| 总参数 | 740M |
| 输出维度 | 768d（原生），支持 128/256/512d 截断 |
| 上下文长度 | 8,192 tokens（上一代 2K，4 倍提升） |
| 架构基座 | Gemma 4 |
| 支持模态 | 文本（100+ 语言 + 代码）、图片、视频、音频 |
| 许可证 | Apache-2.0，可商用 |

---

## 基准测试

| 模态 | 基准 | EmbeddingGemma 2 | EmbeddingGemma 1 |
|------|------|-------------------|-------------------|
| 文本（多语言） | MTEB multilingual v2 | **61.36** | 61.15 |
| 文本（代码） | MTEB code v1 | **78.68** | 68.76 |
| 图片 | MIEB lite | **64.64** | — |
| 图片+视觉文档 | MMEB v2 Image | **57.28** | — |
| 视频 | MMEB v2 Video | **50.67** | — |
| 音频检索 | MSEB Retrieval | **69.54** | — |

代码检索的提升最显著：78.68 对比 68.76，涨了约 +14.4 个百分点。多语言文本整体略有提升。

图片、视频、音频是新增模态，没有前代可比，但 MIEB 64.64 和 MSEB 69.54 是目前公开 768M 级别里的上游水位。

---

## MRL：向量可以截断

模型原生支持 **Matryoshka Representation Learning（MRL）**——输出的 768 维向量可以截断到更低维度并重新归一化，质量损失在可接受范围内：

| 输出维度 | 压缩比 | MTEB 多语言 | MTEB 代码 |
|---------|--------|------------|----------|
| 768d（完整） | 1:1 | 61.36 | 78.68 |
| 512d | 1:1.5 | 61.17 | 77.24 |
| 256d | 1:3 | 60.41 | 76.18 |
| 128d | 1:6 | 57.89 | 71.41 |

**256d 以上截断质量损失很小，128d 更适合纯文本场景**（图片和视频在 128d 时性能下降明显）。对于大规模本地知识库，256d 能把存储需求减到原来的 1/3。

---

## 端侧设计

模块化加载是关键设计决策：

- **纯文本任务**只加载 270M 基座，量化后约 **191MB**
- **浏览器推理**：20–70ms 单次查询（JavaScript）
- 手机/笔记本可直接运行，不需要 GPU

这在实践中意味着：本地知识库索引、设备上 RAG、浏览器插件语义搜索，都不需要向云端发数据。

---

## 多模态统一的实际用法

文本检索的 API 是标准 sentence-transformers：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("google/embeddinggemma-2")

query = "下周会议里讨论预算的部分"
# 可以是文字、图片路径、音频文件路径——同一个 encode() 调用
query_emb = model.encode(query, prompt_name="SearchQuery")
```

**跨模态检索**示例：用一句中文搜几小时录音里的片段——把文字和音频都 encode，直接算余弦相似度，不需要 ASR 中间步骤。

---

## 一句话说清楚

EmbeddingGemma 2 是一个**把文字、图片、声音、视频的"意思"投影到同一张地图上的引擎**。你的问题和相关内容在这张地图上越近，检索就越准——不管它们原来是什么格式。

---

## 和上一代的区别

| 特性 | EmbeddingGemma 1 | EmbeddingGemma 2 |
|------|-----------------|-----------------|
| 模态 | 文本 | 文本 + 图片 + 视频 + 音频 |
| 上下文 | 2K | **8K** |
| MTEB 代码 | 68.76 | **78.68** |
| MRL 截断 | 无 | ✅ 128/256/512/768d |
| 架构基座 | Gemma 2 | **Gemma 4** |

---

> Apache-2.0 开源。Google DeepMind 发布，740M 参数，HuggingFace 已上线，sentence-transformers 直接使用。开源仅供学习参考。

---

<!--EN-->

## EmbeddingGemma 2: Google Puts Text, Image, Audio, and Video Into a Single Embedding Space

Most semantic search systems share a common limitation: text uses one embedding model, images use another, audio requires yet another — and cross-modal retrieval needs manual alignment. A single audio segment is hard to search with a text query without first transcribing it.

EmbeddingGemma 2 eliminates this at the architecture level: one model, four modalities, one vector space.

HuggingFace: https://huggingface.co/google/embeddinggemma-2 | ⭐ 759 | Apache-2.0

---

### Architecture: Four Modalities, One Coordinate System

The model has three loadable components:

| Module | Parameters | Role |
|--------|-----------|------|
| Text backbone (backbone + embedder) | 270M (130M + 140M) | Text and code |
| Vision encoder | 170M | Images and video frames |
| Audio encoder | 300M | Audio |

All modalities project into a shared **768-dimensional vector space**. A sentence and a semantically similar image or audio clip have high cosine similarity — no cross-modal translation, no forced ASR intermediate step.

---

### Specifications

| Item | Value |
|------|-------|
| Total parameters | 740M |
| Output dimension | 768d native; 128/256/512d MRL truncation |
| Context length | 8,192 tokens (4x previous gen's 2K) |
| Architecture base | Gemma 4 |
| Supported modalities | Text (100+ languages + code), images, video, audio |
| License | Apache-2.0 |

---

### Benchmarks

| Modality | Benchmark | EmbeddingGemma 2 | EmbeddingGemma 1 |
|----------|-----------|-------------------|-------------------|
| Text (multilingual) | MTEB multilingual v2 | **61.36** | 61.15 |
| Text (code) | MTEB code v1 | **78.68** | 68.76 |
| Image | MIEB lite | **64.64** | — |
| Image + VisDoc | MMEB v2 | **57.28 / 67.84** | — |
| Video | MMEB v2 Video | **50.67** | — |
| Audio retrieval | MSEB Retrieval | **69.54** | — |

Code retrieval saw the biggest jump: +14.4 percentage points over previous gen. Multilingual text improved marginally.

---

### MRL: Vectors Can Be Truncated

Native Matryoshka Representation Learning (MRL) support lets the 768d output be truncated to 512d, 256d, or 128d with minimal quality loss:

- **256d**: 3x storage reduction, minor quality loss (recommended for mixed-modality workloads)
- **128d**: 6x storage reduction, better suited for text-only workloads

For large local knowledge bases, 256d cuts storage requirements to one-third.

---

### Edge Deployment

- Text-only tasks: load only the 270M backbone, ~**191MB** quantized
- Browser inference: **20–70ms** per query (JavaScript)
- Runs on mobile/laptop without GPU

Local knowledge base indexing, on-device RAG, and browser semantic search become possible without sending data to the cloud.

---

### One-Line Summary

EmbeddingGemma 2 is an engine that maps the *meaning* of text, images, sounds, and video onto the same coordinate system — so your query and the relevant content are geometrically close, regardless of their original format.

---

> Apache-2.0. Released by Google DeepMind, 740M parameters, available on HuggingFace via sentence-transformers. For technical reference only.
