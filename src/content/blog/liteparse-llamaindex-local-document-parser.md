---
title: "LiteParse：LlamaIndex 团队开源本地文档解析引擎，Rust 核心+四端绑定+精确边界框，8.3k Star"
titleEn: "LiteParse: LlamaIndex's Open-Source Local Document Parser — Rust Core, Four-Platform Bindings, Precise Bounding Boxes — 8.3k Stars"
description: "run-llama/liteparse 是 LlamaIndex 团队推出的开源本地文档解析引擎：Rust 核心，原生支持 Node.js、Python、Browser WASM。基于 PDFium 的空间文本提取 + bounding box，双轨解析（native PDF + selective OCR），为 AI Agent 提供截图和布局信息，无云依赖，无隐私顾虑。v2.0.4，8.3k Stars。"
descriptionEn: "run-llama/liteparse is LlamaIndex's open-source local document parsing engine: Rust core with native Node.js, Python, and Browser WASM bindings. PDFium-based spatial text extraction with bounding boxes, dual-track parsing (native PDF + selective OCR), screenshot generation for AI agents, zero cloud dependencies. v2.0.4, 8.3k stars."
pubDate: "2026-06-01"
updatedDate: "2026-06-01"
category: "Tech-News"
tags: ["LlamaIndex", "LiteParse", "文档解析", "PDF", "OCR", "Rust", "开源", "AI Agent", "RAG", "本地部署"]
heroImage: "../../assets/images/liteparse-document-parsing-banner.jpg"
---

本地部署大模型时，文档预处理是一个长期被低估的环节。把一份 PDF 喂给模型，你需要的不只是"提取出文字"——你需要知道每段文字在页面的哪个位置，哪些是标题哪些是表格，哪些页需要 OCR 哪些不需要，以及生成截图供多模态模型使用。

LlamaIndex 团队开源了 `liteparse`，把这些需求全部打包进一个本地优先、无云依赖的解析引擎里。

> 📌 GitHub：https://github.com/run-llama/liteparse  
> 文档：https://developers.llamaindex.ai/liteparse/  
> npm：`@llamaindex/liteparse` / WASM：`@llamaindex/liteparse-wasm`  
> PyPI：`liteparse` | Crates.io：`liteparse`  
> License：Apache 2.0 | Stars：8.3k | 最新版本：v2.0.4（2026-05-30）

## 核心定位：快、轻、无隐私顾虑

LiteParse 的定位非常明确："专注于**快速、轻量**的解析，提供带 bounding box 的高质量空间文本解析，没有专有 LLM 功能，没有云依赖。"

这直接对应了本地 AI 部署的三个真实痛点：

1. **隐私**：文档不离开本机，没有第三方 API 调用
2. **速度**：Rust 核心，PDFium 直接提取，不走云端往返
3. **结构化**：不只是文本，是带精确坐标的空间文本——每个文字块都有 bounding box

## Rust 核心，四端绑定

技术栈选择直接决定了性能上限。`liteparse` 用 Rust 写核心逻辑，通过三套 FFI 绑定暴露给上层：

| 平台 | 绑定方式 | 安装 |
|------|---------|------|
| **Node.js / TypeScript** | napi-rs | `npm i @llamaindex/liteparse` |
| **Python** | PyO3 | `pip install liteparse` |
| **Browser / WASM** | wasm-bindgen | `npm i @llamaindex/liteparse-wasm` |
| **CLI / Rust lib** | 原生 | `cargo install liteparse` |

语言分布：Rust 73%、Python 19%、JavaScript 4%——核心性能在 Rust，绑定层尽量薄。

## 双轨解析：Native + Selective OCR

解析流程分两条路：

**电子 PDF**：通过 PDFium 直接提取文本，精确到字符级别的 bounding box，速度快、精度高。

**扫描 PDF / 图片**：自动检测无电子文本的页面，触发 **Selective OCR**——只对需要 OCR 的页面调用引擎，不对整个文档做无谓的全量 OCR。

OCR 引擎三选一：

| 引擎 | 特点 |
|------|------|
| **内置 Tesseract** | 零配置，开箱即用 |
| **EasyOCR HTTP** | Docker 启动，多语言质量更好 |
| **PaddleOCR HTTP** | 中文场景推荐 |

三者都遵循同一套 `OCR_API_SPEC.md` 标准接口，可随时切换或自定义接入其他 OCR 服务。

## 支持格式：不只是 PDF

通过 LibreOffice 转换层，还支持：

- **Office 文档**：.docx / .pptx / .xlsx / .odt / .pages / .key / .numbers / .csv 等
- **图片**（via ImageMagick）：.jpg / .png / .tiff / .webp / .svg 等

所有格式经历同一条流水线：格式转换 → Rust 核心 → 文本提取 + OCR 融合 + Grid Projection → JSON / Text 输出。

## Agent 友好：截图 + Bounding Box

这是 `liteparse` 区别于普通解析库的关键设计。

**截图生成**：直接把 PDF 页面渲染成高质量图片，供多模态 LLM 使用。当纯文本提取丢失排版信息（表格、图表、公式）时，截图能完整保留视觉上下文：

```bash
lit screenshot document.pdf -o ./screenshots
lit screenshot document.pdf --dpi 300 --target-pages "1,3,5" -o ./screenshots
```

**Bounding box**：每段文本都附带精确坐标（x、y、width、height），Agent 可以定位原文位置、做文档引用标注、或结合截图实现视觉问答。

仓库根目录有 `AGENTS.md` 和 `CLAUDE.md`——明确写明了如何把 `liteparse` 作为 Agent Skill 使用，这是 LlamaIndex 对当前 AI 工作流的直接适配。

## CLI 快速上手

```bash
# 基本解析
lit parse document.pdf --format json -o output.json

# 指定页码范围
lit parse document.pdf --target-pages "1-5,10,15-20"

# 批量处理整个目录
lit batch-parse ./input-dir ./output-dir

# 从 URL 直接解析
curl -sL https://example.com/report.pdf | lit parse -

# 禁用 OCR（仅电子文本）
lit parse document.pdf --no-ocr
```

## v2.0.4：修复旋转文本 Bounding Box

最新版本（2026-05-30）修复了两个精度问题：旋转页面文本框坐标计算错误、接近 360° 旋转未归一化问题。小修复，清晰的信号：项目在持续打磨解析精度，而非堆功能。

## 和 LlamaParse 云版本的关系

LlamaParse 是 LlamaIndex 的商业云解析服务，`liteparse` 是它的开源本地对应物——"不需要 LLM 功能、不想走云端的场景"。两者可以共存：本地预处理用 `liteparse`，需要 AI 增强解析时走 LlamaParse 云 API。

2026 年 2 月建仓，四个月 8.3k Star，在文档解析这个垂直方向上增速相当快。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

When self-hosting LLMs locally, document preprocessing is a persistently underrated step. Feeding a PDF to a model requires more than "extracting text" — you need to know where each piece of text sits on the page, which sections are headers vs. tables, which pages need OCR and which don't, and how to generate screenshots for multimodal models.

The LlamaIndex team open-sourced `liteparse` to bundle all of these requirements into a local-first, zero-cloud-dependency parsing engine.

> 📌 GitHub: https://github.com/run-llama/liteparse  
> Docs: https://developers.llamaindex.ai/liteparse/  
> npm: `@llamaindex/liteparse` | WASM: `@llamaindex/liteparse-wasm`  
> PyPI: `liteparse` | Crates.io: `liteparse`  
> License: Apache 2.0 | Stars: 8.3k | Latest: v2.0.4 (2026-05-30)

## Core Positioning: Fast, Light, Zero Privacy Concerns

LiteParse is explicit in scope: "focused exclusively on fast and light parsing — high-quality spatial text with bounding boxes, no proprietary LLM features, no cloud dependencies."

Three real pain points for local AI deployment:

1. **Privacy**: documents never leave the machine, no third-party API calls
2. **Speed**: Rust core, PDFium direct extraction, no cloud round-trips
3. **Structure**: spatially-aware text with bounding boxes on every block, not just raw strings

## Rust Core, Four Platform Bindings

| Platform | Binding | Install |
|----------|---------|---------|
| **Node.js / TypeScript** | napi-rs | `npm i @llamaindex/liteparse` |
| **Python** | PyO3 | `pip install liteparse` |
| **Browser / WASM** | wasm-bindgen | `npm i @llamaindex/liteparse-wasm` |
| **CLI / Rust lib** | native | `cargo install liteparse` |

Language breakdown: Rust 73%, Python 19%, JavaScript 4% — performance in Rust, thin binding layers on top.

## Dual-Track Parsing: Native + Selective OCR

**Electronic PDF**: PDFium direct text extraction, character-level bounding boxes, fast and precise.

**Scanned PDF / Images**: auto-detects pages without electronic text, triggers **Selective OCR** only on those pages — not a full-document OCR pass.

Three OCR engines, all sharing the same `OCR_API_SPEC.md` interface — swap or extend at will:
- **Built-in Tesseract** (zero config, works out of the box)
- **EasyOCR HTTP service** (Docker, better multilingual quality)
- **PaddleOCR HTTP service** (recommended for Chinese)

## Agent-Friendly: Screenshots + Bounding Boxes

**Screenshot generation**: renders PDF pages to high-quality images for multimodal LLMs. When pure text loses layout (tables, charts, formulas), screenshots preserve visual context.

**Bounding boxes**: every text block includes precise coordinates (x, y, width, height). Agents can locate source positions, create citations, or combine with screenshots for visual QA.

The repo includes `AGENTS.md` and `CLAUDE.md` in the root — explicit guidance for using `liteparse` as an Agent Skill.

## Relationship to LlamaParse Cloud

LlamaParse is LlamaIndex's commercial cloud parsing service; `liteparse` is its open-source local counterpart — for cases where AI-enhanced parsing and cloud dependencies aren't needed. The two can coexist: local preprocessing with `liteparse`, cloud-enhanced parsing with LlamaParse when needed.

8.3k stars in under 4 months. Fast growth for a document parsing vertical.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
