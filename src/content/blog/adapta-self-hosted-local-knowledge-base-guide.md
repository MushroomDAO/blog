---
title: "用 Adapta 搭一个完全属于自己的本地知识库：一个诚实的上手指南"
titleEn: "Building a Truly Private Local Knowledge Base with Adapta: An Honest Guide"
description: "Adapta 是一个自托管的私有大模型平台，把 RAG 知识检索和 LoRA 微调塞进同一个 OpenAI 兼容接口。本文带普通个人从零跑通纯 CPU 的本地知识库，同时诚实交代它 2 个 star、单人原型的真实状态和安全红线。"
descriptionEn: "Adapta is a self-hosted private LLM platform combining RAG retrieval and LoRA fine-tuning behind one OpenAI-compatible endpoint. This guide walks an individual through a CPU-only local knowledge base from scratch — and is honest about its 2-star, one-person prototype status and security caveats."
pubDate: "2026-07-10"
updatedDate: "2026-07-10"
category: "Tech-Experiment"
tags: ["本地知识库", "RAG", "自托管", "LoRA", "隐私", "Docker", "开源", "大模型"]
heroImage: "../../assets/images/adapta-self-hosted-local-knowledge-base-guide-banner.jpg"
---

把公司合同、体检报告、几年的读书笔记喂给 ChatGPT，然后指望它帮你查——这件事的别扭之处在于，你其实并不知道这些东西最后躺在谁的硬盘上。

于是"本地知识库"成了一个持续被搜索的关键词。Adapta 是这个方向上一个挺有意思的新项目：它把**知识检索（RAG）**和**行为微调（LoRA）**装进同一个 OpenAI 兼容的接口里，全部跑在你自己的机器上，没有遥测，没有回调。

GitHub: github.com/yielab/adapta
文档: yielab.github.io/adapta
License: MIT

---

## 先说清楚：这个项目现在是什么状态

我得先泼一盆冷水，因为它的官网做得相当漂亮，容易让人误以为这是个成熟产品。

翻开仓库的真实数据：**2 个 star，1 个 fork，132 次提交**，作者是一个人（Santiago Yie），README 里他自己写得很坦白——这是"一个人的、Claude 辅助的项目，处于工作原型阶段"。

他甚至主动列出了不该信任它的地方：

> 完整生命周期是跑通的（RAG、LoRA 训练、评估门禁、多租户服务、图像理解微调），但**没有经过生产环境加固**：GPU 测试覆盖不完整，认证路径和评估门禁在托付敏感数据之前，应该由第三方独立审查。

这是我愿意花时间写它的原因之一。一个作者敢在 README 顶部用加粗写"别直接信我的认证代码"，比一堆刷 star 的项目诚实得多。

所以本文的定位是：**它值得你在一台不联网的旧笔记本或家用 NAS 上玩起来，但今天不要把公司的客户数据放进去，也不要把 8000 端口暴露到公网。**

---

## 它到底解决什么问题

市面上做本地知识库的工具不少（AnythingLLM、Dify、RAGFlow 都能干），Adapta 的差异化在于它把两件通常被拆开的事合在了一起：

| 你想要什么 | Adapta 的机制 | 需要什么硬件 |
|---|---|---|
| 让模型**根据你的文档回答**，并给出引用出处 | Knowledge（RAG） | **CPU 就够** |
| 改变模型**怎么说话**（语气、格式、固定 JSON 输出） | Fine-tuning（LoRA） | 需要 NVIDIA GPU |
| 让模型**看懂你的图片**（发票、表单、截图 → 结构化 JSON） | 视觉模型微调 | 需要 NVIDIA GPU |

作者反复强调的一个区分特别有价值，很多人一上来就搞混：

> **事实归 RAG，行为归微调。** LoRA 适配器是个几 MB 的小文件，它教模型"怎么回答"，而不是"新的知识"。想让模型知道你们的退款政策，那是文档的事；想让它每次都用你的模板和语气回答，那才是微调的事。

对绝大多数个人用户来说，**你需要的只是 RAG 那一行——而它纯 CPU 就能跑。** 这是整篇文章的关键。

---

## 普通个人的可行路径：纯 CPU 的本地知识库

### 你需要准备什么

- 一台装了 Docker 和 Docker Compose 的机器（Linux / macOS / Windows 都行）
- 大约 8GB 内存、10GB 磁盘
- **不需要显卡。** 微调才需要 CUDA，而个人建知识库压根用不上微调

Mac 用户特别注意：Apple Silicon 没有 NVIDIA CUDA，**微调和视觉功能你是用不了的**，但 RAG 完全正常——推理走的是 llama-cpp 的 CPU 路径。

### 第一步：把服务跑起来

```bash
git clone https://github.com/yielab/adapta && cd adapta
make up
```

`make up` 会自动检测有没有 GPU，跑数据库迁移，健康检查 Postgres / Redis / ChromaDB，然后打印服务地址。在没有 N 卡的机器上它会自动切到 CPU 模式——RAG 照常工作，LoRA 任务会被干脆地拒绝并提示 "GPU required"，不会把别的东西搞崩。

如果自动检测出问题，可以手动指定 CPU 编排文件：

```bash
docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
```

### 第二步：下载一个基础模型

```bash
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-GGUF \
  qwen2.5-3b-instruct-q4_k_m.gguf \
  --local-dir ./data/models/qwen2.5-3b-instruct
```

模型选型上，官方验证过的清单是这样的（个人建知识库，3B 是甜点）：

| 模型 | 显存/内存（Q4 量化） | 适合谁 |
|---|---|---|
| Qwen2.5-0.5B-Instruct | ~2 GB | 老机器、只想试试 |
| **Qwen2.5-3B-Instruct** | ~4 GB | **默认推荐，从这里开始** |
| Qwen2.5-7B-Instruct | ~8 GB | 质量最好，机器要够 |
| Qwen2.5-VL-3B（视觉） | ~6 GB | 需要 GPU，个人一般用不上 |

中文文档场景我建议直接上 3B 起步，0.5B 的中文理解力对付真实文档会很吃力。

### 第三步：改掉那个致命的默认密码

**这一步不能跳过。**

装好之后控制台在 `http://localhost:8000/console/`，种子管理员账号是 `admin@example.com` / `admin12345`——**这是一个写在公开仓库 README 里的、全世界都知道的凭据。**

在你做任何其他事之前：

```bash
cp .env.example .env
openssl rand -hex 32          # 把结果填进 ADAPTA_SECRET_KEY
```

然后在 `.env` 里：设置真实的 `ADAPTA_SECRET_KEY`、改掉 Postgres 默认密码、把种子管理员关掉（`ADAPTA_SEED_DEFAULT_ADMIN=0`）。

再强调一次作者自己的警告：**在把这套东西暴露到 localhost 之外以前，这三件事必须做完。** 而即便做完了，鉴于认证路径尚未经过独立审计，我的建议依然是——就让它待在局域网里。

### 第四步：建知识库

剩下的部分是纯点击流程，在控制台里：

```
创建 Knowledge（RAG）项目 → 上传文档 → 自动索引 → 创建 endpoint + API key → 完成
```

支持的文档格式是 PDF、DOCX、TXT、MD、HTML。上传后会被解析、切块、嵌入，存进 ChromaDB 里**按项目隔离的**向量集合。整个过程模型权重一个字节都没动——这也是为什么它不需要 GPU。

### 第五步：像调 OpenAI 一样调它

这是 Adapta 设计上最舒服的地方。你的应用不需要学任何新协议：

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="adp_xxxx")

resp = client.chat.completions.create(
    model="my-notes-a1b2c3d4",      # 控制台给你的 endpoint slug
    messages=[{"role": "user", "content": "我去年关于分布式系统的笔记里，提到过哪些一致性模型？"}],
)
print(resp.choices[0].message.content)   # 回答里带引用出处
```

`POST /v1/chat/completions` 是你的应用需要接触的**唯一**外部协议。这意味着任何支持自定义 OpenAI base_url 的客户端——Cherry Studio、NextChat、Obsidian 插件、你自己写的脚本——都可以直接接上去。

---

## 数据放在哪，怎么备份

自托管的意义在于数据是你的，那就得知道它躺在哪。这是官方运维手册里的状态图：

| 存储 | 装了什么 | 位置 |
|---|---|---|
| PostgreSQL | 所有元数据（组织、用户、项目、任务、用量） | `postgres-data` 卷 |
| ChromaDB | 每个项目的向量集合（RAG 的核心） | `chroma-data` 卷 |
| Adapters | 训练出的 LoRA 适配器 | `./data/adapters` |
| Uploads | 你上传的源文档 | `./data/uploads` |
| Models | 基础 GGUF 模型 | `./data/models`（可重新下载） |
| Redis | 任务队列 | 临时数据，不用备份 |

备份不需要停服务：

```bash
# 元数据
docker compose exec -T postgres pg_dump -U adapta adapta | gzip > backup/adapta-$(date +%F).sql.gz

# 向量库
docker run --rm -v adapta_chroma-data:/data -v "$PWD/backup:/out" \
  alpine tar czf /out/chroma-$(date +%F).tgz -C /data .

# 源文档和适配器
tar czf backup/artifacts-$(date +%F).tgz data/adapters data/uploads data/datasets
```

有一个坑值得记住：**Postgres 和 Chroma 必须在同一个时间窗口备份。** 因为 Postgres 里的记录指向磁盘上的文件，只恢复一半会得到一个指向空气的 endpoint。仓库里有 `scripts/backup.sh` 把这三步合成一条命令，扔进 cron 就行。

---

## 那个"评估门禁"，是这个项目最好的想法

即使你用不上微调（个人基本用不上），Adapta 里有个设计值得单独讲，因为它体现了一种少见的工程克制。

一个训练出来的 LoRA 适配器，**在通过考试之前不允许上线服务**。

具体来说：适配器要在它从没见过的留出样本上考一次，绝对分数 ≥ 0.6，**或者**明显打赢没微调过的原始模型，才能被创建成 endpoint。没学到东西的微调会被门禁挡住，根本没机会碰到你的用户。

作者管这叫"护城河"。在一个人人都在喊"微调很简单"的年代，一个默认阻止你部署烂模型的系统，比一个默认让你部署的系统靠谱得多。顺带一提，他自己的测试里用 36 条样本训了个工单分类器，评估分数 0.67、比基线高 0.099，截图都放在文档里了——这种"我把我的实测数字给你看"的态度也不多见。

如果你确实要微调（比如让模型固定输出某种 JSON），作者给的经验是：**300 条以上样本、一个一致的模式、教行为而不是教事实**。少于 100 条，留出集小到根本测不出东西。

---

## 你到底需不需要它

说点实在的。如果你的需求只是"把我的 PDF 变成能问答的知识库"，那么：

**选 Adapta，如果**你喜欢 OpenAI 兼容接口带来的生态自由、你想要一个未来能长到微调的架子、你不介意自己看代码、你的数据不敏感或者机器不联网。

**别选 Adapta，如果**你需要开箱即用的成熟产品、你要托付真正敏感的资料、你没有能力自己审计认证代码。这种情况下 AnythingLLM 之类经过更多人检验的方案更合适。作者自己在竞品分析里承认得很清楚：AnythingLLM 做 RAG 但不能微调，vLLM 和 LoRAX 能规模化服务适配器但不能训练也不做 RAG，NVIDIA NeMo 覆盖面最全但要 Kubernetes 加十几个微服务。Adapta 的位置是"一个人能装起来的全栈"，代价就是它现在只有一个人在维护。

我的判断是：这个项目的价值现在更多在**读它**，而不是**用它**。它的文档质量、状态图、备份手册、评估门禁的设计思路，对任何想搞明白 RAG 和 LoRA 到底怎么落地的人来说，都是一份写得比大部分教程好的材料。至于生产环境——等它有 200 个 star 和几个独立安全审计的时候再说。

---

## 参考链接

- GitHub: github.com/yielab/adapta — MIT License
- 文档站: yielab.github.io/adapta
- 运维手册: docs/reference/OPERATIONS.md（备份、升级、显存规划、加固清单）
- 竞品对比: docs/reference/COMPETITIVE_LANDSCAPE.md

<!--EN-->

## Building a Truly Private Local Knowledge Base with Adapta: An Honest Guide

Feeding your contracts, medical records, and years of reading notes into ChatGPT has one awkward property: you don't actually know whose disk they end up on.

Hence the perennial search term "local knowledge base." Adapta is an interesting new entrant: it packs **knowledge retrieval (RAG)** and **behavior fine-tuning (LoRA)** behind a single OpenAI-compatible endpoint, running entirely on your own hardware — no telemetry, no callbacks.

GitHub: github.com/yielab/adapta (MIT) · Docs: yielab.github.io/adapta

---

### First, the honest status report

The website is polished enough to mistake this for a mature product. The repository tells a different story: **2 stars, 1 fork, 132 commits**, written by one person (Santiago Yie). His README is refreshingly blunt — this is "a one-person, AI-assisted (Claude) project" at "working prototype" status.

He volunteers the parts you shouldn't trust:

> The full lifecycle works end-to-end (RAG, LoRA training, eval gate, multi-tenant serving, vision fine-tunes), but it is **not production-hardened**: GPU test coverage is partial, and the auth and eval-gate paths should be reviewed independently before being trusted with sensitive data.

An author who bolds "don't trust my auth code" at the top of his README is more honest than a great many star-farmed projects. So: **worth running on an offline laptop or home NAS today; do not put customer data in it, and do not expose port 8000 to the internet.**

---

### What it actually solves

| You want | Mechanism | Hardware |
|---|---|---|
| Answers **from your documents**, with citations | Knowledge (RAG) | **CPU only** |
| Change **how the model speaks** (tone, format, fixed JSON) | Fine-tuning (LoRA) | NVIDIA GPU |
| Make it **read your images** (invoices, forms → JSON) | Vision fine-tuning | NVIDIA GPU |

The distinction the author hammers on is genuinely useful: **facts belong to RAG, behavior belongs to fine-tuning.** A LoRA adapter is a few-megabyte file that teaches *how* to respond, not *what* is true. For nearly every individual user, you only need the first row — and it runs on CPU.

---

### The viable path for an individual

**Prerequisites:** Docker + Docker Compose, ~8GB RAM, ~10GB disk. **No GPU.** Apple Silicon users: fine-tuning and vision are off the table (no CUDA), but RAG works fine via llama-cpp on CPU.

**1. Start the stack**

```bash
git clone https://github.com/yielab/adapta && cd adapta
make up
```

`make up` auto-detects the GPU, runs migrations, healthchecks Postgres/Redis/ChromaDB. Without an NVIDIA card it silently uses the CPU profile — RAG works, LoRA jobs are rejected with a clear "GPU required." To force it: `docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d`.

**2. Download a base model**

```bash
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-GGUF \
  qwen2.5-3b-instruct-q4_k_m.gguf --local-dir ./data/models/qwen2.5-3b-instruct
```

Qwen2.5-3B (~4GB) is the sweet spot. The 0.5B struggles with real documents.

**3. Kill the default password — do not skip this**

The console at `http://localhost:8000/console/` seeds an admin of `admin@example.com` / `admin12345` — **a credential published in a public repo.** Before anything else:

```bash
cp .env.example .env
openssl rand -hex 32     # → ADAPTA_SECRET_KEY
```

Set a real `ADAPTA_SECRET_KEY`, change the Postgres password, and disable the seeded admin (`ADAPTA_SEED_DEFAULT_ADMIN=0`). Even then, given the unaudited auth path, keep it on your LAN.

**4. Build the knowledge base**

```
Create a Knowledge (RAG) project → upload documents → auto-indexed
→ create endpoint + API key → done
```

PDF, DOCX, TXT, MD, HTML are parsed, chunked, and embedded into a per-project ChromaDB collection. Model weights are never touched — which is why no GPU is needed.

**5. Call it like OpenAI**

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="adp_xxxx")
resp = client.chat.completions.create(
    model="my-notes-a1b2c3d4",
    messages=[{"role": "user", "content": "Which consistency models did my notes mention?"}],
)
```

`POST /v1/chat/completions` is the only protocol your app touches — so any client accepting a custom base_url (Cherry Studio, NextChat, Obsidian plugins, your own scripts) plugs straight in.

---

### Where your data lives

| Store | Contents | Location |
|---|---|---|
| PostgreSQL | metadata (orgs, users, projects, jobs) | `postgres-data` volume |
| ChromaDB | per-project vectors (the RAG core) | `chroma-data` volume |
| Adapters / Uploads / Datasets | trained adapters, source docs | `./data/*` bind mounts |
| Models | base GGUF files | `./data/models` (re-downloadable) |

Back up Postgres and Chroma **in the same window** — a Postgres row pointing at a missing adapter file yields an endpoint pointing at nothing. `scripts/backup.sh` does all three; cron it.

---

### The eval gate is the best idea here

Even if you never fine-tune, one design deserves attention. A trained LoRA adapter **cannot serve until it passes an exam** on held-out examples: score ≥ 0.6 in absolute terms, *or* clearly beat the un-adapted base model. A fine-tune that learned nothing is blocked from production entirely.

In an era where everyone insists fine-tuning is easy, a system that refuses to deploy a bad model by default is more trustworthy than one that lets you. The author's own run — a 36-example ticket classifier scoring 0.67, +0.099 over baseline — is screenshotted in the docs. Showing your real numbers is rarer than it should be.

If you do fine-tune: **300+ examples, one consistent pattern, teach a behavior not a fact.** Below ~100 the held-out split is too small to measure anything.

---

### Should you use it?

**Yes, if** you want OpenAI-compatible freedom, a scaffold that can grow into fine-tuning, and you're comfortable reading the code — with non-sensitive data or an offline machine.

**No, if** you need a battle-tested product for genuinely sensitive material and can't audit auth code yourself. AnythingLLM and friends have far more eyes on them. The author's own competitive analysis concedes the landscape honestly: AnythingLLM does RAG but can't fine-tune; vLLM and LoRAX serve adapters at scale but neither train nor retrieve; NVIDIA NeMo covers everything but demands Kubernetes and 10+ microservices. Adapta's niche is "a full stack one person can install" — and the cost is that one person maintains it.

My verdict: right now this project is more valuable to **read** than to **run**. Its documentation, state map, backup runbook, and the reasoning behind the eval gate are a better education in how RAG and LoRA actually ship than most tutorials. Production? Revisit it at 200 stars and an independent security audit.

© 2026 Author: Mycelium Protocol
