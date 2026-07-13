---
title: "网页爬虫的范式革命：PixelRAG 不读 HTML，它看截图"
titleEn: "The Web Crawler Revolution: PixelRAG Reads Screenshots, Not HTML"
description: "Berkeley SkyLab 开源的 PixelRAG（6.5k⭐）彻底改变网页检索方式——不解析 HTML，直接对网页截图做视觉嵌入，让表格、图表、信息图在 RAG 里第一次真正可检索。"
descriptionEn: "PixelRAG (6.5k⭐) from Berkeley SkyLab rewrites web retrieval: instead of parsing HTML to text, it renders pages to screenshot tiles and retrieves over images directly — tables, charts, and infographics finally survive the RAG pipeline."
pubDate: "2026-07-13"
updatedDate: "2026-07-13"
category: "Research"
tags: ["RAG", "开源", "AI搜索", "Berkeley"]
heroImage: "../../assets/images/pixelrag-visual-web-crawler-screenshot-rag-banner.jpg"
---

> 本文基于开源项目 **StarTrail-org/PixelRAG**（6,579⭐，546 Fork），出自 Berkeley SkyLab、BAIR 和 Berkeley NLP 的联合团队，对应论文 [arXiv:2606.28344](https://arxiv.org/abs/2606.28344)。

---

## 传统 RAG 爬虫的死穴

你有没有碰到过这种场景：让 AI 回答"这张表格里第三季度的数字是多少"，结果它给你一堆废话，就是不给数字？

原因很简单。传统 RAG 流水线是这样工作的：

1. 爬取网页 → 解析 HTML → 提取文本
2. 把文本切块、向量化
3. 检索相关文本块 → 喂给语言模型

**问题出在第一步**。HTML 解析会把页面「拍平」成纯文本流，过程中：

- 表格的行列关系被打散
- 图表变成没有意义的 alt 文字或直接消失
- 信息图、排版结构、视觉层级——全没了

剩下的是一堆碎片文字，AI 读了也不知道那个数字在哪里。

---

## PixelRAG 的做法：直接截图

Berkeley SkyLab 的团队换了一个思路：**既然视觉模型能直接看图，为什么要先把图变成文字再看？**

PixelRAG 的核心流水线：

```
网页 / PDF / 图片
     ↓
pixelshot（截图，切成 tiles）
     ↓
Qwen3-VL-Embedding（图片→向量）
     ↓
FAISS 索引
     ↓
检索 → 视觉模型直接读取对应截图 tile → 回答
```

传统方式：「解析文本 → 检索文本 → 回答」  
PixelRAG：「截图 → 检索截图 → 回答」

**表格就是表格，图表就是图表，布局就是布局**——没有东西在这个过程里消失。

---

## 两个核心组件

### 1. pixelshot：截图引擎

`pixelshot` 是个独立的 CLI，用 Playwright/CDP 驱动 headless Chrome，把任何 URL 或 PDF 切成等比例的截图 tiles：

```bash
pip install pixelrag

# 网页 → tiles
pixelshot https://en.wikipedia.org/wiki/Python -o ./tiles

# PDF → tiles（需要 poppler）
pixelshot paper.pdf -o ./tiles --dpi 200

# 混合使用
pixelshot https://arxiv.org/abs/2606.28344 paper.pdf -o ./tiles
```

macOS/Windows 上会自动找系统的 Chrome；Linux 上内置了优化过的 `headless_shell`。每次渲染在独立的临时 Chrome 实例里跑，不影响你正在用的浏览器。

### 2. Qwen3-VL-Embedding：视觉嵌入模型

这是论文里最核心的创新。团队用截图数据 LoRA 微调了 `Qwen3-VL-Embedding-2B`，让它能把网页截图嵌入到一个语义空间里，使得：

- 文字查询 `"第三季度销售额"` 能匹配到那个包含表格的截图 tile
- 图片查询（直接上传一张截图）也能做相似图检索

训练数据、权重、LoRA adapters 全部开源：
- 模型：[Chrisyichuan/wiki-screenshot-embedding-lora](https://huggingface.co/Chrisyichuan/wiki-screenshot-embedding-lora)
- 训练集：[Chrisyichuan/screenshot-training-natural-filtered-v2](https://huggingface.co/datasets/Chrisyichuan/screenshot-training-natural-filtered-v2)

---

## 三种使用方式

### 方式一：免费 API，零配置体验

团队已经用 PixelRAG 索引了维基百科的 **828 万篇文章**，提供无需 API key 的公开搜索端点：

```bash
# 文字查询
curl -X POST https://api.pixelrag.ai/search \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"text": "法国的首都是什么？"}], "n_docs": 5}'

# 图片查询（搜索视觉上相似的页面）
# 见 pixelrag.ai/docs 里的 visual search 接口
```

也可以直接去 [pixelrag.ai](https://pixelrag.ai) 在浏览器里试。

### 方式二：索引自己的文档

有一份 PDF、一堆内部网页、或者公司知识库？自建索引，在自己的机器上跑：

```bash
pip install 'pixelrag[index]'

cat > pixelrag.yaml << 'EOF'
source:
  type: local
  path: ./my_docs          # 可以是目录、PDF、URL 列表

embed:
  model: Qwen/Qwen3-VL-Embedding-2B
  device: auto             # CUDA / Apple MPS / CPU 自动选

output: ./my_index
EOF

pixelrag index build       # 建索引
pixelrag serve --index-dir ./my_index --port 30001   # 启动本地 API
```

Apple M 系列芯片上大约 3 分钟能索引一份普通 PDF；GPU 上约 1 分钟。

**实测体验：索引一份 PDF 找一个图表里的数字**

```bash
# 下载示例 PDF
curl -L -o paper.pdf https://raw.githubusercontent.com/StarTrail-org/PixelRAG/main/assets/pixelrag-paper.pdf

# 建索引
pixelrag index build

# 搜索
curl -X POST http://localhost:30001/search \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"text": "PixelRAG 的流水线总览图"}], "n_docs": 1}'
# → 返回包含那张流程图截图的 tile
```

### 方式三：给 Claude Code 装上眼睛

这是这个项目里让我最感兴趣的应用：**pixelbrowse skill**，让 Claude Code 直接通过截图"看"网页，而不是读 HTML。

```bash
# 安装（pixelshot 要在 PATH 里）
uv tool install pixelrag
claude plugin marketplace add StarTrail-org/PixelRAG
claude plugin install pixelbrowse@pixelrag-plugins

# 然后直接问 Claude
claude -p "screenshot https://news.ycombinator.com and summarize the top stories"
claude -p "screenshot https://arxiv.org/abs/2606.28344 and explain the key findings"

# 或者在交互模式里
/screenshot https://example.com
```

不需要 MCP server，不需要后端——`pixelshot` 在本地跑，截图直接喂给 Claude 的视觉能力。意味着 Claude 现在能看到那些传统爬虫会丢掉的东西：图表里的趋势线、信息图里的数字、表格里的对比数据。

---

## 流水线各阶段独立可用

如果只需要某一步，可以单独安装和调用：

| 阶段 | 命令 | 作用 |
|------|------|------|
| 截图 | `pixelshot <url>` | URL/PDF → 截图 tiles |
| 分块 | `pixelrag chunk` | tiles → 规范化分块 |
| 向量化 | `pixelrag embed` | 截图 → 向量，支持多 GPU |
| 建索引 | `pixelrag build-index` | 向量 → FAISS 索引 |
| 服务 | `pixelrag serve` | FAISS 搜索 API（FastAPI） |
| 一键全流程 | `pixelrag index` | 上面全部串起来 |

训练部分（LoRA 微调 Qwen3-VL-Embedding）在 `train/` 目录，是独立的 uv 项目，需要 CUDA GPU，不影响使用。

---

## 这件事为什么重要

**当前 AI 对视觉内容的盲区**，比大多数人意识到的更大。

大量有价值的信息藏在表格、图表、信息图、PDF 版式里——这是网页和文档的原始形态。传统 RAG 流水线的 HTML 解析层把这些东西抹掉了，本质上是在用残缺的信息回答问题。

PixelRAG 的思路是绕过这个问题而不是修补它：**不再试图把视觉信息转化成文字，而是直接在视觉信息上建立检索系统**。

这个方向有几个有意思的延伸：

1. **多模态知识库**：企业知识库里的 PPT、报告、图表，都可以直接进入 PixelRAG 索引，不需要先做 OCR 或者人工提取数据
2. **网页监控**：监控竞争对手页面的布局变化、价格表更新，这些传统爬虫很难稳定抓到
3. **文档问答的质量跃升**：任何有视觉结构的文档（财报、研报、技术规格书），基于截图的 RAG 比文本 RAG 准确率应该有明显提升

论文里给出了基准数据：在包含视觉内容（表格、图表）的问答任务上，PixelRAG 显著优于文本 RAG，具体数字可以去读 [arXiv:2606.28344](https://arxiv.org/abs/2606.28344)。

---

## 硬件要求

| 场景 | 要求 |
|------|------|
| 使用公共 API | 任何有网络的机器 |
| 本地截图（pixelshot） | Python 3.10+，Chrome 或 Playwright |
| 本地建索引 | macOS Apple Silicon 或 Linux CUDA，Python 3.10+ |
| 下载预建索引 | 217GB 磁盘空间（Wikipedia base 索引） |
| LoRA 训练 | CUDA GPU，cuDNN 9.20 |

注：公开 API 免费且无需注册，用来体验最方便。自建索引在 Apple M 系列上可用，不强制需要 GPU。

---

## 快速开始

```bash
# 体验公共 API（零安装）
curl -X POST https://api.pixelrag.ai/search \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"text": "Python programming language"}], "n_docs": 3}'

# 本地安装
pip install pixelrag

# 截图一个网页
pixelshot https://github.com/StarTrail-org/PixelRAG -o ./tiles

# 索引一份文档（需要额外依赖）
pip install 'pixelrag[index]'
# → 建索引 → 本地搜索（见上文完整示例）
```

---

GitHub：[github.com/StarTrail-org/PixelRAG](https://github.com/StarTrail-org/PixelRAG)  
论文：[arxiv.org/abs/2606.28344](https://arxiv.org/abs/2606.28344)  
在线 Demo：[pixelrag.ai](https://pixelrag.ai)  
API：[api.pixelrag.ai](https://api.pixelrag.ai/status)

© 2026 Author: Mycelium Protocol

<!--EN-->

## The Web Crawler Revolution: PixelRAG Reads Screenshots, Not HTML

> Based on **StarTrail-org/PixelRAG** (6,579⭐, 546 Forks) from Berkeley SkyLab, BAIR, and Berkeley NLP. Paper: [arXiv:2606.28344](https://arxiv.org/abs/2606.28344).

---

### The Problem with Text-Based RAG

Traditional RAG pipelines parse HTML to text, losing tables, charts, infographics, and visual layout in the process. The reader model then tries to answer questions about a table that no longer exists as a table — it's just scattered numbers in a text blob.

PixelRAG cuts this problem off at the root: **render the page to screenshot tiles and retrieve over images directly.** Visual structure survives intact.

---

### How It Works

```
URL / PDF / image
     ↓
pixelshot (Playwright/CDP → screenshot tiles)
     ↓
Qwen3-VL-Embedding-2B (LoRA fine-tuned on screenshot data)
     ↓
FAISS index
     ↓
Search → vision model reads the matching tile → answer
```

The key innovation is the embedding model: LoRA fine-tuning on screenshot data teaches `Qwen3-VL-Embedding-2B` to embed page images into a space where text queries ("Q3 revenue") retrieve the right visual tile — the one that actually contains the table.

---

### Three Ways to Use It

**1. Free hosted API — zero setup, 8.28M Wikipedia pages pre-indexed:**
```bash
curl -X POST https://api.pixelrag.ai/search \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"text": "Python programming language"}], "n_docs": 3}'
```

**2. Index your own documents:**
```bash
pip install 'pixelrag[index]'

cat > pixelrag.yaml << 'EOF'
source:
  type: local
  path: ./my_docs

embed:
  model: Qwen/Qwen3-VL-Embedding-2B
  device: auto   # CUDA / Apple MPS / CPU

output: ./my_index
EOF

pixelrag index build
pixelrag serve --index-dir ./my_index --port 30001
```

**3. Give Claude eyes — the pixelbrowse skill:**
```bash
uv tool install pixelrag
claude plugin marketplace add StarTrail-org/PixelRAG
claude plugin install pixelbrowse@pixelrag-plugins

# Claude now sees charts, tables, and layout, not just scraped text
claude -p "screenshot https://arxiv.org/abs/2606.28344 and explain the key findings"
```

---

### Why This Matters

A huge amount of valuable web content is locked in visual structure — tables in reports, charts in research papers, data in infographics. Text-based RAG pipelines systematically destroy this structure. PixelRAG doesn't try to recover it; it avoids losing it in the first place.

Practical implications:
- **Enterprise knowledge bases**: PDFs, slide decks, and reports go directly into the index without OCR preprocessing
- **Document Q&A**: Earnings reports, research papers, technical specs — any document with visual structure should see accuracy improvements over text RAG
- **Web monitoring**: Track layout changes, price tables, or chart updates that text scrapers miss

---

### Quick Start

```bash
# Try the free API instantly
curl -X POST https://api.pixelrag.ai/search \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"text": "machine learning frameworks"}], "n_docs": 3}'

# Install locally
pip install pixelrag
pixelshot https://en.wikipedia.org/wiki/Python -o ./tiles
```

GitHub: [github.com/StarTrail-org/PixelRAG](https://github.com/StarTrail-org/PixelRAG)  
Paper: [arxiv.org/abs/2606.28344](https://arxiv.org/abs/2606.28344)  
Demo: [pixelrag.ai](https://pixelrag.ai)

© 2026 Author: Mycelium Protocol
