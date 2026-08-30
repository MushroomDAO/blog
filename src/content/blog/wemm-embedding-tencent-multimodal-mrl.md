---
title: "WeMM-Embedding-9B：腾讯统一多模态嵌入模型，同尺寸全面超越 Qwen3-VL-Embedding"
titleEn: "WeMM-Embedding-9B: Tencent's Unified Multimodal Embedding Beats Qwen3-VL-Embedding at Every Size"
description: "腾讯微信视觉团队开源的多模态嵌入模型，基于 Qwen3.5-9B，把文本、图像、视频、视觉文档统一映射到同一个 4096 维向量空间，支持 MRL 弹性降维（可截断到 256 维甚至更小而不用重新计算）。2B 和 9B 两个尺寸在 MMEB-v2 上都超过同尺寸的 Qwen3-VL-Embedding，Apache 2.0 协议。"
descriptionEn: "Tencent WeChat Vision Team's open-source multimodal embedding model, built on Qwen3.5-9B, maps text, images, video, and visual documents into one 4096-dim vector space with Matryoshka Representation Learning (truncate to 256 dims or smaller without recomputing). Both the 2B and 9B sizes beat same-size Qwen3-VL-Embedding on MMEB-v2. Apache 2.0."
pubDate: "2026-08-30"
updatedDate: "2026-08-30"
category: "Tech-News"
tags: ["多模态", "Embedding", "腾讯", "MRL", "开源", "语义检索"]
heroImage: "../../assets/images/wemm-embedding-tencent-multimodal-mrl-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

HuggingFace：tencent/WeMM-Embedding-9B | Apache-2.0  
GitHub：github.com/Tencent/WeMM-Embedding  
技术报告：arXiv:2608.24053  
基座模型：Qwen3.5-9B | 参数量：9B | 嵌入维度：4096  
三个尺寸：2B / 4B / 9B

---

## 一句话定位

**用一个模型，把文本、图片、视频、带图表的文档都映射进同一个向量空间——不用再分别维护文本 embedding 和图像 embedding 两套模型，还能事后把向量裁到更小的维度而不用重新跑一遍。**

WeMM-Embedding 是腾讯微信视觉团队发布的通用多模态嵌入（embedding）模型，输出 4096 维、L2 归一化的向量，输入可以是纯文本、图片、视频，也可以是文本图片混排的「交错输入」。目前不支持音频。

## 为什么不用分开的图文 embedding 模型？

大部分检索系统（RAG、搜图、搜视频）现在的做法是：文本用一个 embedding 模型，图像/视频再用另一个（比如 CLIP 系），两边分别建索引，查询的时候再想办法把两个向量空间的相似度拉到可比。这带来两个真实的麻烦：

1. **部署成本翻倍**——两套模型、两套索引、两套服务，还要处理版本不同步的问题。
2. **跨模态检索天然别扭**——"用一段文字搜一张图"这种查询，本质上是在比较两个不是同一个训练目标下产生的向量，效果上限低。

WeMM-Embedding 的做法是让所有模态共用一个模型、一个向量空间，查询和被查询的内容不管是什么模态，出来的向量天然可比。

## MRL：弹性降维怎么工作

WeMM-Embedding 支持 Matryoshka Representation Learning（MRL）——训练时就让向量的前几维本身承载最主要的语义信息，所以推理完之后可以直接截断：

```python
# 完整 4096 维向量算好之后，直接截断到想要的维度再重新归一化，
# 不需要重新跑一遍模型
d = 256
truncated = embedding[..., :d]
truncated = truncated / truncated.norm(dim=-1, keepdim=True)
```

官方支持的截断维度：64 / 128 / 256 / 512 / 1024 / 2048。对做大规模向量检索的团队来说，这直接换成了存储和计算成本——同一批向量，线上高精度场景用满 4096 维，海量粗排场景截到 256 维甚至 64 维，索引体积能缩小一到两个数量级，且不用为不同精度需求各跑一遍推理。

## 跑分：同尺寸全面超过 Qwen3-VL-Embedding

在 MMEB-v2（78 个数据集的多模态检索基准）上，WeMM-Embedding 在同参数量档位上全面领先目前另一个开源多模态 embedding 强基线 Qwen3-VL-Embedding：

| 模型 | 参数量 | Average | Image | Video | VisDoc |
|---|---|---|---|---|---|
| Qwen3-VL-Embedding | 2B | 73.2 | 75.0 | 61.9 | 79.2 |
| **WeMM-Embedding** | **2B** | **77.9** | **79.6** | **70.8** | **80.7** |
| Qwen3-VL-Embedding | 8B | 77.8 | 80.1 | 67.1 | 82.4 |
| **WeMM-Embedding** | **9B** | **80.6** | **81.9** | **74.3** | **83.3** |

video 这一项差距最明显（2B 档位 70.8 对 61.9，9B 档位 74.3 对 67.1），说明团队在视频理解这个通常是多模态 embedding 模型短板的方向上投入了更多训练资源。另外在更新、覆盖面更广的 MMEB-v3（190 个任务）上，WeMM-Embedding-9B 整体得分 59.5。

## 怎么用

用 `sentence-transformers` 直接调，跟其他 SentenceTransformer 模型的用法一致：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("tencent/WeMM-Embedding-9B", trust_remote_code=True)
embeddings = model.encode_document(["一段文字", "一张图片路径", "一段视频路径"])
```

需要 `transformers>=5.2.0`、`qwen-vl-utils`、`sentence-transformers>=5.7.0`。也可以用官方仓库里的 `transformers_inference.py` 脚本直接跑，或者通过 vLLM / SGLang 部署成服务。

## 适合谁

如果你在做的检索系统本来就要同时处理文本和图片/视频（比如带截图的技术文档库、电商图文商品库、视频素材库），WeMM-Embedding 值得替换掉现在分开维护的两套 embedding 方案试一试——尤其是 MRL 这个特性，对已经在为向量索引存储成本发愁的团队是直接能落地的收益。9B 版本适合追求上限的场景，2B 版本已经能在同参数量下打赢对手，资源有限时是更现实的起点。

---

**链接**

- GitHub：https://github.com/Tencent/WeMM-Embedding
- HuggingFace：https://huggingface.co/tencent/WeMM-Embedding-9B
- 技术报告：https://arxiv.org/abs/2608.24053

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

## WeMM-Embedding-9B: Tencent's Unified Multimodal Embedding Beats Qwen3-VL-Embedding at Every Size

*by Mycelium Protocol*

---

HuggingFace: tencent/WeMM-Embedding-9B | Apache-2.0  
GitHub: github.com/Tencent/WeMM-Embedding  
Technical report: arXiv:2608.24053  
Base model: Qwen3.5-9B | Parameters: 9B | Embedding dimension: 4096  
Three sizes: 2B / 4B / 9B

---

## The gist

**One model maps text, images, video, and visual documents into the same vector space — no more running separate text and image embedding models, and you can shrink the embedding dimension after the fact without recomputing anything.**

WeMM-Embedding is Tencent WeChat Vision Team's general-purpose multimodal embedding model, producing 4,096-dimensional, L2-normalized vectors from plain text, images, video, or interleaved text-and-image input. Audio is not supported.

## Why not just use separate embedding models for text and images?

Most retrieval systems today (RAG, image search, video search) run one embedding model for text and a different one (usually a CLIP-family model) for images/video, with separate indexes on each side. That creates two real problems: doubled deployment cost (two models, two indexes, two services to keep in sync), and awkward cross-modal search — comparing vectors that were never trained toward the same objective caps how good "search an image with a text query" can actually get.

WeMM-Embedding puts every modality through the same model into the same vector space, so query and target vectors are naturally comparable regardless of what modality either one is.

## MRL: elastic dimensionality that just works

WeMM-Embedding is trained with Matryoshka Representation Learning (MRL) — the earliest dimensions of the vector are trained to carry the most important semantic signal, so you can truncate after inference:

```python
# Compute the full 4096-dim vector once, then truncate to whatever
# dimension you need and renormalize — no re-inference required
d = 256
truncated = embedding[..., :d]
truncated = truncated / truncated.norm(dim=-1, keepdim=True)
```

Officially supported truncation sizes: 64 / 128 / 256 / 512 / 1024 / 2048. For teams running large-scale vector search, this translates directly into storage and compute cost — the same batch of vectors can serve high-precision lookups at full 4096 dimensions and cheap first-pass ranking at 256 or even 64 dimensions, cutting index size by one to two orders of magnitude without a separate inference pass per precision tier.

## Benchmarks: beats Qwen3-VL-Embedding at matched size

On MMEB-v2 (78 multimodal retrieval datasets), WeMM-Embedding outperforms Qwen3-VL-Embedding — currently the other strong open multimodal embedding baseline — at every matched parameter size:

| Model | Params | Average | Image | Video | VisDoc |
|---|---|---|---|---|---|
| Qwen3-VL-Embedding | 2B | 73.2 | 75.0 | 61.9 | 79.2 |
| **WeMM-Embedding** | **2B** | **77.9** | **79.6** | **70.8** | **80.7** |
| Qwen3-VL-Embedding | 8B | 77.8 | 80.1 | 67.1 | 82.4 |
| **WeMM-Embedding** | **9B** | **80.6** | **81.9** | **74.3** | **83.3** |

The video column shows the widest gap (70.8 vs 61.9 at 2B; 74.3 vs 67.1 at 9B), suggesting the team put extra training effort into video understanding — usually the weak point for multimodal embedding models. On the newer, broader MMEB-v3 (190 tasks), WeMM-Embedding-9B scores 59.5 overall.

## How to use it

Works directly through `sentence-transformers`, same interface as any other SentenceTransformer model:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("tencent/WeMM-Embedding-9B", trust_remote_code=True)
embeddings = model.encode_document(["a piece of text", "path/to/image", "path/to/video"])
```

Requires `transformers>=5.2.0`, `qwen-vl-utils`, and `sentence-transformers>=5.7.0`. You can also run the repo's `transformers_inference.py` script directly, or serve it via vLLM / SGLang.

## Who this is for

If your retrieval system already needs to handle text alongside images or video — technical docs with screenshots, e-commerce product catalogs with photos, video asset libraries — WeMM-Embedding is worth trying in place of a separate text/image embedding setup. MRL in particular is an immediately actionable win for any team already worried about vector index storage cost. The 9B model is for teams chasing the ceiling; the 2B model already beats its same-size competitor and is the more realistic starting point when resources are limited.

---

**Links**

- GitHub: https://github.com/Tencent/WeMM-Embedding
- HuggingFace: https://huggingface.co/tencent/WeMM-Embedding-9B
- Technical report: https://arxiv.org/abs/2608.24053

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
