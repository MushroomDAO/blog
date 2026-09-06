---
title: "mdya 实测：871 篇中文笔记索引 8 分钟，但语义检索在中文上是失效的"
titleEn: "mdya Tested: 871 Chinese Notes Indexed in 8 Minutes — but Semantic Search Fails on Chinese"
description: "Rust 写的本地 Markdown 检索原语 mdya，BM25 + 端侧向量 + MCP，单二进制。我拿自己 871 篇笔记（10MB）实测：索引 8 分 01 秒，占 176MB，BM25 查询 30ms、向量 530ms。但对照实验揭穿了一个问题——字面命中的中文查询两条路都准，换成同义改写就全崩，因为默认模型 ruri-v3-30m 是日语的、FTS 分词用的是日语 ipadic 词典。多语言的 EmbeddingGemma 是 gated 模型，直接 401 拉不下来。附可行的修复路径。"
descriptionEn: "mdya is a Rust local Markdown search primitive — BM25, on-device vectors, MCP, single binary. I tested it on my own 871 Chinese notes (10MB): 8m01s to index, 176MB on disk, 30ms BM25 queries, 530ms vector queries. But a controlled experiment exposes the catch: literal Chinese queries hit on both paths, while semantic paraphrases miss entirely — the default model ruri-v3-30m is Japanese, and FTS tokenizes with the Japanese ipadic dictionary. The multilingual EmbeddingGemma is gated and returns 401. Fix paths included."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-Experiment"
tags: ["开源", "Rust", "本地优先", "MCP", "知识库", "向量检索", "本地AI", "实测", "Claude Code"]
heroImage: "../../assets/images/mdya-rust-local-markdown-search-chinese-test-871-docs-banner.jpg"
author: "Mycelium Protocol"
---

**先给结论**：mdya 是个做得很干净的东西——Rust 单二进制、BM25 + 端侧向量 + MCP 服务、全程离线。但如果你的笔记是中文的，**它的向量检索这一半目前基本是白花的算力**：字面能命中的查询 BM25 就够了，需要语义泛化的查询两条路一起崩。

原因不在实现，在默认配置：**默认嵌入模型 `cl-nagoya/ruri-v3-30m` 是日语模型，全文检索的分词器用的是日语 ipadic 词典。** 而那个多语言的 EmbeddingGemma，是 gated 模型，直接拉不下来。

这篇是拿我自己的知识库（871 篇 Markdown，10MB，中文为主）跑出来的实测。

> 📌 项目地址：https://github.com/yoshihirosuzuki/mdya
> Apache-2.0 / MIT 双协议 ｜ Rust ｜ 测试版本 0.4.1
> 一行安装：`curl --proto '=https' --tlsv1.2 -LsSf https://github.com/yoshihirosuzuki/mdya/releases/latest/download/mdya-installer.sh | sh`

---

## 它的定位：一个「检索原语」，不是知识库 App

README 里这句话写得很克制，也是它最大的优点：

> mdya 是一个**检索原语**。它索引本地 Markdown，通过 CLI 和 MCP server 返回检索结果。仅此而已。
>
> mdya 不是检索 agent，不是 LLM 查询改写前端。它没有查询扩展、没有重排器、没有多阶段 agent 流水线。需要那些东西的工作流，应当在 mdya 之上另外叠一层。

这个定位对 Agent 场景是对的。你要的就是一个快、稳、可预测的检索层，改写和重排交给上层的 LLM 去做。

能力清单：
- **BM25 全文检索**（Lance FTS，日语形态分析 lindera/ipadic）
- **向量检索**（端侧嵌入，余弦相似度）
- **混合检索**（RRF 倒数排名融合）
- **Markdown 分块**（按标题和代码围栏边界切）
- **MCP server**（`mdya mcp`，stdio / HTTP）
- `.pdf` 走同一条摄取路径，摄取时转纯文本

存储用 LanceDB，推理用 candle，全程无云端 API 路径。

---

## 实测：871 篇、10MB，跑出来什么数

环境：Apple Silicon Mac，mdya 0.4.1，默认配置（`embed_parallelism: 8`，`memory_limit_mb: 8192`）。

```bash
mdya init
mdya collection add ~/mycelium-kb/content
mdya update-all
```

**索引结果：**

| 指标 | 实测值 |
|---|---|
| 文档数 | **871**（新增 871，失败 0）|
| 源数据体积 | 10 MB |
| **墙钟时间** | **8 分 01 秒** |
| CPU 时间 | 56 分 24 秒（user）+ 5 分 25 秒（sys）|
| 索引体积 | **176 MB** |
| 嵌入模型缓存 | 146 MB（首次自动下载）|

几点解读：

**56 分 CPU / 8 分墙钟 ≈ 7 倍并行**，说明 `embed_parallelism: 8` 是真吃满了。8 核机器上索引期间基本满载，别指望同时干别的。

**176MB 索引 / 10MB 源文件 = 17.6 倍膨胀**。这是向量索引的常态（每个 chunk 一个 256 维 float32 向量），但要有心理准备：你的笔记有多大，磁盘上准备 20 倍。

**首次运行会自动下载 146MB 的嵌入模型**到 `~/.mdya-models/`，之后复用。

**查询延迟：**

| 检索方式 | 延迟 |
|---|---|
| BM25 (`search fts`) | **30 ms** |
| 向量 (`search vector`) | **530 ms** |

530ms 有原因，见下一节的警告。

---

## 索引时冒出来的两条警告，都指向同一个问题

**警告一（索引结束时）：**

```
WARN lance_index::vector::kmeans: KMeans: more than 10% of clusters are empty: 1 of 3.
Help: this could mean your dataset has many duplicate vectors.
```

三个聚类里空了一个。Lance 的提示说这通常意味着「数据集里有很多重复向量」。我的 871 篇笔记内容差异很大，不该出现这种情况——**真正的解释是嵌入模型没能把这些中文文本区分开，向量都挤在一起了。**

**警告二（每次向量查询时）：**

```
WARN lance::dataset::scanner: Requested metric Cosine is incompatible with index metric L2,
falling back to brute-force search
```

向量索引是按 L2 距离建的，查询却用余弦相似度，于是**每次查询都退化成暴力全扫**。530ms 就是这么来的——它没有在用 ANN 索引，是在线性扫过所有向量。

871 篇还能忍，量级上去就是线性恶化。这条是实现层面的问题，跟中文无关，值得给上游提 issue。

---

## 关键实验：中文到底能不能查？

这是我最想搞清楚的。做了两组对照——**同一个意思，一组用原文里出现过的词，一组用同义改写**。

### 对照组 A / B：字面 vs 改写

```bash
# A: 「小红书」——这三个字在文章里大量出现
mdya search hybrid "小红书" -n 3
```
```
content/blog/swe-to-ai-infra-sglang-contribution-guide.md          score=0.031
content/blog/xiaohongshu-operations-codex-skills-workflow-systematic.md  score=0.027   ← 命中
content/blog/guizang-social-card-illustration-guide.md             score=0.017
```

```bash
# B: 「种草笔记平台」——语义等价，字面完全不同
mdya search hybrid "种草笔记平台" -n 3
```
```
content/blog/arle-local-llm-distillation-guide.md          score=0.026
content/blog/hermes-agent-nous-research-self-improving-skill-loop.md  score=0.017
content/blog/multipost-extension-one-click-multi-platform-guide.md    score=0.017
```

**B 组一篇小红书相关的都没有。** 全是无关结果。

### 对照组 C / D：再验一次

```bash
# C: 「知识库」——原文高频词
mdya search vector "知识库" -n 3
```
```
content/blog/anthropic-agent-three-layer-architecture.md   score=0.866
content/blog/clipto-local-memory-ai-content-management...  score=0.859   ← 命中
content/blog/adapta-self-hosted-local-knowledge-base-guide.md  score=0.854  ← 命中
```

```bash
# D: 「怎么把笔记存起来给AI用」——同一个意思，口语改写
mdya search vector "怎么把笔记存起来给AI用" -n 3
```
```
content/blog/ai-intermediary-model-ahacreator-industry-transfer-guide.md  score=0.912
content/mempalace/github-com-yuyixuanfu-nowhere.md         score=0.906
content/blog/yc-internal-ai-data-tools-skills-playbook.md  score=0.906
```

**D 组同样全崩。** 而且注意分数：D 组的分数（0.912、0.906）比 C 组命中项的分数（0.859、0.854）**还高**——模型对着一句它不理解的中文，给出了更高的「相似度」。这正是向量空间坍缩的表现。

### 再补一个 BM25 的例子

```bash
mdya search fts "显卡不够用怎么办" -n 3
```
```
content/blog/pixelle-video-ai-short-video-engine-guide.md   score=25.155
content/blog/awesome-agent-architecture-22-section-...      score=18.177
content/blog/neo-lab-sovereign-ai-endgame-sequoia-...       score=18.115
```

三条全无关。我的库里有大量讲显存、硬件选型、Mac Studio 对比的文章，一篇没进来。

### 结论

| 查询类型 | BM25 | 向量 | 可用性 |
|---|---|---|---|
| 中文字面命中（词在原文里） | ✅ 准 | ✅ 准 | 可用 |
| 中文语义改写 | ❌ 崩 | ❌ 崩 | **不可用** |

**这意味着向量检索那一半在中文上没有产生任何增量**——它能命中的，BM25 用 30ms 就命中了，而且更准。花 530ms 和 176MB 换来的东西，在中文场景里约等于零。

---

## 为什么会这样？翻源码找到了确切原因

两处，都在默认配置里。

**其一，嵌入模型是日语的。** 读 `src/embedding/mod.rs`，它内置三个端侧预设：

| 模型 | 架构 | 语言取向 |
|---|---|---|
| `cl-nagoya/ruri-v3-30m` **（默认）** | ModernBERT | **日语**——检索前缀写死是 `検索クエリ: ` / `検索文書: ` |
| `sentence-transformers/all-MiniLM-L6-v2` | BERT | 英语 |
| `google/embeddinggemma-300m` | Gemma3 | **多语言**——前缀 `task: search result \| query: ` |

默认那个是名古屋大学的 Ruri，日语检索模型。它的检索前缀直接是日语字符串——模型在训练时就是按日语查询/日语文档的分布来对齐的。中文里的汉字它认识一部分（所以「本地推理」这类含共通汉字的查询还能勉强命中），但中文的语义空间它没学过。

**其二，全文检索的分词器也是日语的。** 看 `Cargo.toml`：

```toml
# Embedded IPADIC dictionary for Lance's FTS `lindera/ipadic` tokenizer.
```

IPADIC 是 MeCab 的日语词典。中文和日语虽然共用汉字，但**分词边界完全不同**。用日语词典切中文，切出来的是无意义的碎片——这就是「显卡不够用怎么办」返回三条无关结果的原因：它匹配的是碎片，不是词。

---

## 那怎么修？三条路，两条能走

**路线一：换成 EmbeddingGemma —— 目前走不通。**

配置文件改一行就行：

```yaml
embedding:
  model: google/embeddinggemma-300m
```

然后就撞墙了：

```
Error: model cache: fetch config.json: request error:
HTTP status client error (401 Unauthorized) for url
(https://huggingface.co/google/embeddinggemma-300m/resolve/.../config.json)
```

**EmbeddingGemma 是 gated 模型**，要先在 HuggingFace 上接受许可协议，再带 token 才能下载。

好消息是 mdya 支持这件事——`src/embedding/cache.rs` 里明确读 `HF_TOKEN` 环境变量，也会回退到 `hf auth login` 写的标准 token 文件。所以完整路径是：

1. 去 https://huggingface.co/google/embeddinggemma-300m 接受许可
2. 建一个 read 权限的 access token
3. `export HF_TOKEN=hf_xxx`
4. 改配置、重新 `mdya update-all`

我手上没有 HF token，这条**没有实测**。

**路线二：走 Ollama 后端 —— 最实际。**

源码里写着，除三个内置预设外，`embedding.model` 还接受 `ollama:<model>` 前缀的任意值：

```yaml
embedding:
  model: ollama:bge-m3
```

`bge-m3` 是中文检索上公认好用的多语言嵌入模型。这条路不受 gated 限制，代价是要额外跑一个 Ollama。**同样未实测**（我这台机器上没装 Ollama）。

**路线三：BM25 的中文分词 —— 没有解。**

分词器是 Lance FTS 层的 `lindera/ipadic`，在 mdya 的配置里改不了。除非上游换成支持中文的词典（lindera 本身有 CC-CEDICT 支持），否则中文 BM25 就只能靠汉字子串碰运气。

**所以现实的组合是**：中文用户换掉嵌入模型后，能拿回向量这一半；BM25 那一半在中文上仍然是残的。而 hybrid 是 RRF 融合两路结果——一路残着，融合结果也会被拖累。

---

## 那它到底适合谁？

**很适合**：
- 笔记是**英语或日语**的——默认配置直接可用，日语甚至是一等公民
- 想要一个**给 Agent 用的检索层**——MCP 一行接进 Claude Code：`claude mcp add mdya -- mdya mcp`
- 讨厌装一堆 Python 依赖——单二进制，`~/.cargo/bin/mdya`，删掉就干净了
- 数据绝对不能出本机——源码层面没有任何云端 API 路径

**先别急**（如果你的笔记是中文）：
- 默认配置下向量检索白花算力，不如只用 `search fts` 加省下的 146MB
- 想要能用的语义检索，得先解决 HF token 或装 Ollama
- BM25 的中文分词短期内没解

---

## 和我现在用的 basic-memory 比

我的 `mycelium-kb` 目前跑在 basic-memory 上，语义搜索走 jina-zh，在 CPU 上慢——这是我一开始看上 mdya 的原因。

实测下来，**换不了**，至少现在不行：

| | basic-memory + jina-zh | mdya + ruri-v3-30m |
|---|---|---|
| 中文语义检索 | 慢，但准 | 快，但**不准** |
| 索引 871 篇 | —— | 8m01s |
| 查询延迟 | 慢（秒级） | BM25 30ms / 向量 530ms |
| 部署 | Python 栈 | 单二进制 |
| MCP | 有 | 有 |

**快而不准，不如慢而准。** 检索这件事上，错的结果比慢的结果代价大得多——尤其当下游是个会照着结果往下推理的 Agent。

真正值得试的是「mdya + `ollama:bge-m3`」这个组合：拿回中文语义能力，同时保住 Rust 单二进制和 30ms 的 BM25。这是我下一步要做的事。

---

## 缺口

1. **两条修复路径都没实测**——HF_TOKEN + EmbeddingGemma、以及 `ollama:bge-m3`，都只验证到「源码支持」这一层，没跑通。
2. **没测 PDF 摄取**。README 说 `.pdf` 走同一条路径，我的库里没有 PDF。
3. **没测增量更新**。`update-all` 有 `updated / skipped / removed` 计数，说明支持增量，但只跑了首次全量。
4. **没和其他 Rust 检索工具横评**。
5. **1 star 的新项目**，一人维护，README 明说「best-effort，无正式 SLA」。

---

## 一句话总结

mdya 的工程质量是好的——克制的定位、诚实的文档、单二进制、真离线。但它的默认配置是**为日语调的**，中文用户拿到手会得到一个「看起来在工作、实际上语义检索是坏的」的系统，而且不跑对照实验发现不了——因为字面命中的查询看起来一切正常。

**这也是个通用教训**：评估任何带向量检索的本地工具，别只看它「支持中文」，要做一次同义改写的对照测试。分数高不等于命中对。

> 📌 项目地址：https://github.com/yoshihirosuzuki/mdya
> 嵌入模型预设源码（三个内置 + ollama 后端）：https://github.com/yoshihirosuzuki/mdya/blob/main/src/embedding/mod.rs
> EmbeddingGemma（gated，需接受许可）：https://huggingface.co/google/embeddinggemma-300m

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**Conclusion first**: mdya is a cleanly built thing — a Rust single binary with BM25, on-device vectors and an MCP server, fully offline. But if your notes are in Chinese, **its vector-search half is currently wasted compute**: queries that hit literally are already served by BM25, and queries needing semantic generalization fail on both paths.

The cause is not the implementation but the defaults: **the default embedding model `cl-nagoya/ruri-v3-30m` is Japanese, and full-text search tokenizes with the Japanese ipadic dictionary.** The multilingual EmbeddingGemma is a gated model that simply will not download.

This post is measured against my own knowledge base — 871 Markdown files, 10MB, predominantly Chinese.

> 📌 Repository: https://github.com/yoshihirosuzuki/mdya
> Apache-2.0 / MIT dual ｜ Rust ｜ tested at 0.4.1
> One-line install: `curl --proto '=https' --tlsv1.2 -LsSf https://github.com/yoshihirosuzuki/mdya/releases/latest/download/mdya-installer.sh | sh`

---

## Its positioning: a search primitive, not a knowledge-base app

The README is admirably restrained, and this is its greatest strength:

> mdya is a **search primitive**. It indexes local Markdown, and returns search results over a CLI and an MCP server. That is all it does.
>
> mdya is not a search agent and not an LLM query-rewriting front-end. It has no query expansion, no reranker, and no multi-stage agent pipeline.

That framing is right for agent workloads. What you want is a fast, stable, predictable retrieval layer, with rewriting and reranking left to the LLM above it.

Capabilities:
- **BM25 full-text search** (Lance FTS with lindera/ipadic Japanese morphological analysis)
- **Vector search** (on-device embeddings, cosine similarity)
- **Hybrid** (Reciprocal Rank Fusion)
- **Markdown chunking** along heading and code-fence boundaries
- **MCP server** (`mdya mcp`, stdio / HTTP)
- `.pdf` shares the ingest path, converted to plain text at ingest

Storage is LanceDB, inference is candle, and there is no cloud API path in the source at all.

---

## Measured: 871 files, 10MB

Environment: Apple Silicon Mac, mdya 0.4.1, defaults (`embed_parallelism: 8`, `memory_limit_mb: 8192`).

```bash
mdya init
mdya collection add ~/mycelium-kb/content
mdya update-all
```

**Indexing:**

| Metric | Measured |
|---|---|
| Documents | **871** (new 871, failed 0) |
| Source size | 10 MB |
| **Wall clock** | **8m 01s** |
| CPU time | 56m 24s user + 5m 25s sys |
| Index size | **176 MB** |
| Model cache | 146 MB (downloaded on first run) |

Reading those numbers:

**56 minutes of CPU in 8 minutes of wall clock ≈ 7× parallelism**, so `embed_parallelism: 8` genuinely saturates. Expect the machine to be busy throughout.

**176MB index from 10MB of source = 17.6× expansion.** Normal for a vector index (a 256-dim float32 vector per chunk), but budget roughly 20× your notes on disk.

**First run downloads a 146MB embedding model** into `~/.mdya-models/`, reused afterwards.

**Query latency:**

| Method | Latency |
|---|---|
| BM25 (`search fts`) | **30 ms** |
| Vector (`search vector`) | **530 ms** |

That 530ms has a cause — see the next section.

---

## Two warnings during indexing, both pointing at the same thing

**Warning one, at the end of indexing:**

```
WARN lance_index::vector::kmeans: KMeans: more than 10% of clusters are empty: 1 of 3.
Help: this could mean your dataset has many duplicate vectors.
```

One of three clusters came out empty. Lance suggests this usually means "many duplicate vectors." My 871 notes differ widely in content, so that should not happen — **the real explanation is that the embedding model failed to separate these Chinese texts, leaving the vectors bunched together.**

**Warning two, on every vector query:**

```
WARN lance::dataset::scanner: Requested metric Cosine is incompatible with index metric L2,
falling back to brute-force search
```

The vector index is built on L2 distance while queries use cosine similarity, so **every query degrades to a brute-force scan**. That is where 530ms comes from — no ANN index in play, just a linear pass over every vector.

Tolerable at 871 documents, linearly worse as the corpus grows. This one is an implementation issue unrelated to Chinese and worth filing upstream.

---

## The key experiment: does Chinese search actually work?

Two controlled pairs — **same meaning, one phrased with words present in the corpus, one paraphrased**.

### Pair A / B: literal vs paraphrase

```bash
# A: "小红书" (Xiaohongshu) — appears constantly in the corpus
mdya search hybrid "小红书" -n 3
```
```
content/blog/swe-to-ai-infra-sglang-contribution-guide.md          score=0.031
content/blog/xiaohongshu-operations-codex-skills-workflow-systematic.md  score=0.027   ← hit
content/blog/guizang-social-card-illustration-guide.md             score=0.017
```

```bash
# B: "种草笔记平台" — semantically equivalent, lexically disjoint
mdya search hybrid "种草笔记平台" -n 3
```
```
content/blog/arle-local-llm-distillation-guide.md          score=0.026
content/blog/hermes-agent-nous-research-self-improving-skill-loop.md  score=0.017
content/blog/multipost-extension-one-click-multi-platform-guide.md    score=0.017
```

**Not one Xiaohongshu article in B.** All irrelevant.

### Pair C / D: confirming

```bash
# C: "知识库" (knowledge base) — high-frequency in the corpus
mdya search vector "知识库" -n 3
```
```
content/blog/anthropic-agent-three-layer-architecture.md   score=0.866
content/blog/clipto-local-memory-ai-content-management...  score=0.859   ← hit
content/blog/adapta-self-hosted-local-knowledge-base-guide.md  score=0.854  ← hit
```

```bash
# D: "怎么把笔记存起来给AI用" ("how do I store notes for an AI to use") — colloquial paraphrase
mdya search vector "怎么把笔记存起来给AI用" -n 3
```
```
content/blog/ai-intermediary-model-ahacreator-industry-transfer-guide.md  score=0.912
content/mempalace/github-com-yuyixuanfu-nowhere.md         score=0.906
content/blog/yc-internal-ai-data-tools-skills-playbook.md  score=0.906
```

**D fails identically.** Note the scores: D's misses (0.912, 0.906) rank *higher* than C's genuine hits (0.859, 0.854). The model assigns higher "similarity" to a Chinese sentence it does not understand — the signature of a collapsed vector space.

### One more, on BM25

```bash
mdya search fts "显卡不够用怎么办" -n 3   # "what do I do when the GPU isn't enough"
```
```
content/blog/pixelle-video-ai-short-video-engine-guide.md   score=25.155
content/blog/awesome-agent-architecture-22-section-...      score=18.177
content/blog/neo-lab-sovereign-ai-endgame-sequoia-...       score=18.115
```

All three irrelevant. The corpus is full of posts on VRAM, hardware selection and Mac Studio comparisons; none surfaced.

### Verdict

| Query type | BM25 | Vector | Usable? |
|---|---|---|---|
| Chinese literal (term appears verbatim) | ✅ accurate | ✅ accurate | Yes |
| Chinese paraphrase | ❌ fails | ❌ fails | **No** |

**Which means the vector half contributes nothing on Chinese** — whatever it can find, BM25 already found in 30ms and more accurately. The 530ms and 176MB buy approximately zero in a Chinese corpus.

---

## Why? The source gives the exact reason

Two places, both in the defaults.

**One: the embedding model is Japanese.** From `src/embedding/mod.rs`, three on-device presets ship:

| Model | Architecture | Language orientation |
|---|---|---|
| `cl-nagoya/ruri-v3-30m` **(default)** | ModernBERT | **Japanese** — retrieval prefixes hard-coded as `検索クエリ: ` / `検索文書: ` |
| `sentence-transformers/all-MiniLM-L6-v2` | BERT | English |
| `google/embeddinggemma-300m` | Gemma3 | **Multilingual** — prefix `task: search result \| query: ` |

The default is Nagoya University's Ruri, a Japanese retrieval model whose prefixes are literally Japanese strings; it was aligned on a Japanese query/document distribution. It recognizes some Han characters — which is why a query like "本地推理" with shared characters still lands — but it never learned the Chinese semantic space.

**Two: the full-text tokenizer is Japanese too.** From `Cargo.toml`:

```toml
# Embedded IPADIC dictionary for Lance's FTS `lindera/ipadic` tokenizer.
```

IPADIC is MeCab's Japanese dictionary. Chinese and Japanese share Han characters but **segment along entirely different boundaries**. Running Chinese through a Japanese dictionary yields meaningless fragments — which is exactly why "显卡不够用怎么办" returned three unrelated results: it matched fragments, not words.

---

## How to fix it: three paths, two viable

**Path one: switch to EmbeddingGemma — currently blocked.**

One config line:

```yaml
embedding:
  model: google/embeddinggemma-300m
```

Then it hits a wall:

```
Error: model cache: fetch config.json: request error:
HTTP status client error (401 Unauthorized) for url
(https://huggingface.co/google/embeddinggemma-300m/resolve/.../config.json)
```

**EmbeddingGemma is gated** — you must accept the license on HuggingFace and supply a token.

The good news is mdya supports that: `src/embedding/cache.rs` explicitly reads `HF_TOKEN` and falls back to the standard token file written by `hf auth login`. The full path:

1. Accept the license at https://huggingface.co/google/embeddinggemma-300m
2. Create a read-scope access token
3. `export HF_TOKEN=hf_xxx`
4. Update the config and re-run `mdya update-all`

I have no HF token on hand, so this is **untested**.

**Path two: the Ollama backend — the practical one.**

Beyond the three presets, the source accepts any `ollama:<model>` value for `embedding.model`:

```yaml
embedding:
  model: ollama:bge-m3
```

`bge-m3` is a well-regarded multilingual embedding model for Chinese retrieval. No gating, at the cost of running Ollama alongside. **Also untested** — Ollama is not installed on this machine.

**Path three: Chinese BM25 tokenization — no fix.**

The tokenizer lives in Lance's FTS layer as `lindera/ipadic` and is not exposed in mdya's config. Unless upstream switches to a Chinese-capable dictionary (lindera does support CC-CEDICT), Chinese BM25 will keep relying on lucky character substrings.

**So realistically**: a Chinese user who swaps the embedding model recovers the vector half; the BM25 half stays crippled. And since hybrid is RRF over both, a crippled path drags the fused result down too.

---

## Who is it for?

**A good fit**:
- Notes in **English or Japanese** — defaults work out of the box, and Japanese is a first-class citizen
- Wanting a **retrieval layer for an agent** — one line into Claude Code: `claude mcp add mdya -- mdya mcp`
- Allergic to Python dependency stacks — one binary at `~/.cargo/bin/mdya`, delete it and it's gone
- Data that must not leave the machine — there is no cloud API path in the source

**Hold off** (if your notes are Chinese):
- Vector search burns compute for nothing under defaults; use `search fts` and save the 146MB
- Usable semantic search requires solving the HF token or installing Ollama
- Chinese BM25 tokenization has no near-term fix

---

## Versus what I currently use

My `mycelium-kb` runs on basic-memory with jina-zh for semantic search, which is slow on CPU — the reason mdya caught my eye.

Measured, **I cannot switch**, at least not yet:

| | basic-memory + jina-zh | mdya + ruri-v3-30m |
|---|---|---|
| Chinese semantic search | Slow but accurate | Fast but **inaccurate** |
| Indexing 871 files | —— | 8m01s |
| Query latency | Slow (seconds) | BM25 30ms / vector 530ms |
| Deployment | Python stack | Single binary |
| MCP | Yes | Yes |

**Fast and wrong loses to slow and right.** In retrieval, a wrong result costs far more than a slow one — especially when the consumer downstream is an agent that will reason onward from whatever it gets.

The combination actually worth trying is mdya plus `ollama:bge-m3`: Chinese semantics recovered while keeping the Rust single binary and 30ms BM25. That is my next step.

---

## Gaps

1. **Neither fix path was tested** — HF_TOKEN + EmbeddingGemma and `ollama:bge-m3` were verified only to the level of "the source supports it."
2. **PDF ingest untested.** The README says `.pdf` shares the path; my corpus has none.
3. **Incremental update untested.** `update-all` reports `updated / skipped / removed` counts, implying incremental support, but I only ran a first full pass.
4. **No comparison against other Rust search tools.**
5. **A 1-star project** with one maintainer whose README states plainly: best-effort, no formal SLA.

---

## In one line

mdya's engineering quality is good — restrained scope, honest documentation, single binary, genuinely offline. But its defaults are **tuned for Japanese**, and a Chinese user ends up with a system that looks like it is working while its semantic search is broken — undetectable without a controlled test, because literal queries appear perfectly fine.

**The general lesson**: when evaluating any local tool with vector search, do not settle for "it supports Chinese." Run a paraphrase control. A high score is not a correct hit.

> 📌 Repository: https://github.com/yoshihirosuzuki/mdya
> Embedding presets in source (three built-in plus the Ollama backend): https://github.com/yoshihirosuzuki/mdya/blob/main/src/embedding/mod.rs
> EmbeddingGemma (gated, license acceptance required): https://huggingface.co/google/embeddinggemma-300m

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
