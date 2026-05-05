---
title: "腾讯开源 HunyuanMT：33 种语言、双模型、支持术语干预和格式化翻译"
titleEn: "Tencent Open-Sources HunyuanMT: 33 Languages, Dual Models, Terminology Intervention and Formatted Translation"
description: "腾讯混元开源 HY-MT 1.5 翻译模型，提供 1.8B（边缘部署）和 7B（高精度）两个版本，支持 33 种语言互译，具备术语干预、上下文感知、格式化翻译等专业能力，并通过 AngelSlim 压缩到 2-bit/1.25-bit 实现手机端离线翻译。"
descriptionEn: "Tencent Hunyuan open-sources HY-MT 1.5, a dual-model translation system (1.8B for edge, 7B for accuracy) supporting 33 languages with terminology intervention, contextual translation, and formatted translation. Compressed 2-bit/1.25-bit versions via AngelSlim enable offline mobile translation."
pubDate: "2026-05-05"
updatedDate: "2026-05-05"
category: "Tech-News"
tags: ["腾讯", "HunyuanMT", "翻译模型", "开源", "多语言", "本地部署", "LLM"]
heroImage: "../../assets/banner-digital-public-goods.jpg"
---

**结论先行（BLUF）**：腾讯混元开源了 HY-MT 1.5 翻译模型，两个版本：1.8B 适合边缘设备和实时翻译，7B 适合高精度和混合语言场景。支持 33 种语言互译，特色是**术语干预**（专业领域词汇准确率）、**上下文感知**和**格式化翻译**。通过 AngelSlim 工具进一步压缩到 2-bit 和 1.25-bit，实现手机端离线翻译 demo。

---

## 基本情况

腾讯混元（Tencent Hunyuan）团队发布了 **HunyuanMT / HY-MT 1.5** 翻译模型并开源权重。

这不是通用大语言模型，而是专门针对翻译任务训练和优化的模型。两个尺寸满足不同场景需求：

| 版本 | 定位 | 适用场景 |
|------|------|---------|
| **HY-MT 1.5-1.8B** | 轻量快速 | 边缘设备、实时翻译、手机端 |
| **HY-MT 1.5-7B** | 高精度 | 解释性翻译、混合语言、专业场景 |

---

## 支持语言

覆盖 **33 种语言**互译，包括：

**亚洲**：中文（简体/繁体）、粤语、日语、韩语、越南语、泰语、印尼语、菲律宾语、高棉语、缅甸语、蒙古语、维吾尔语、哈萨克语

**欧洲**：英语、法语、西班牙语、德语、俄语、葡萄牙语、意大利语、荷兰语、波兰语、捷克语、乌克兰语、土耳其语

**南亚/中东**：阿拉伯语、波斯语、希伯来语、印地语、孟加拉语、泰米尔语、泰卢固语、古吉拉特语、乌尔都语、马拉地语

---

## 四种翻译模式

这是 HY-MT 1.5 区别于一般翻译模型的关键。它不只是"输入文本→输出译文"，而是提供了四种针对不同需求的翻译模式：

**1. 基础翻译**
标准模式，适合日常文本。

**2. 术语干预（Terminology Intervention）**
支持传入自定义术语表，模型会优先使用指定译法。这对法律、医疗、技术文档翻译至关重要——通用翻译模型的最大痛点之一就是专业术语翻译不稳定。

**3. 上下文感知翻译（Contextual Translation）**
支持传入上下文，帮助模型理解歧义词和长文档中的一致性问题。

**4. 格式化翻译（Formatted Translation）**
保留原文格式（Markdown、HTML、表格等），不破坏文档结构。

---

## 极致压缩：手机离线翻译

通过腾讯自家的 **AngelSlim** 模型压缩工具，HY-MT 1.5-1.8B 进一步压缩到：

- **2-bit** 量化版本
- **1.25-bit** 量化版本（极限压缩）

并配套发布了一个**手机端离线翻译 demo**。这意味着即便在没有网络的情况下，手机也能跑翻译——这对隐私敏感场景（医疗、法律、企业内部文件）有明显价值。

---

## 生态和部署

社区已经围绕 HY-MT 1.5 快速构建了多种部署方式：

- **Docker 一键部署**（[neosun100/hy-mt](https://github.com/neosun100/hy-mt)）：含 Web UI + REST API + **MCP Server 支持**，38 种语言，流式翻译
- **ComfyUI 插件**（[freeyaers/ComfyUI-HY-MT](https://github.com/freeyaers/ComfyUI-HY-MT)）：接入工作流
- **Pinokio 一键安装包**（[PierrunoYT/Tencent-HY-MT1.5-Pinokio](https://github.com/PierrunoYT/Tencent-HY-MT1.5-Pinokio)）：Gradio 界面，普通用户友好
- **RAG 翻译引擎**（结合 Google Gemma 3）：面向文档智能翻译场景

MCP Server 支持意味着可以直接把 HY-MT 接入 Claude Code 或其他支持 MCP 的 AI 工具——翻译变成一个本地调用的能力。

---

## 为什么值得关注

翻译这件事长期被 Google Translate、DeepL 垄断，开源模型质量一直是短板。HY-MT 1.5 几个点值得注意：

1. **专业化设计**：术语干预、格式保留这类功能，说明它在瞄准企业和专业用户，不只是消费级翻译
2. **双尺寸策略**：1.8B 做边缘，7B 做质量，覆盖面宽
3. **极限压缩**：1.25-bit 离线翻译 demo 是一个技术验证，证明专用翻译模型可以极度压缩
4. **开源 + 生态**：发布不到多久社区已有 Docker、ComfyUI、MCP 等多种集成，说明有真实需求

---

## 常见问题

**Q: 1.8B 和 7B 翻译质量差多少？**  
A: 1.8B 定位快速和边缘部署，7B 适合需要更高精度的解释性翻译和混合语言场景。官方没有公开具体 BLEU/COMET 对比数据，从架构来看 7B 在复杂场景下会更稳定。

**Q: 和 Google Translate、DeepL 相比如何？**  
A: 目前没有官方公开的对照 benchmark。术语干预和格式化翻译是差异化能力，在专业文档场景可能优于通用翻译服务；日常对话翻译质量待社区验证。

**Q: MCP Server 怎么用？**  
A: 通过 Docker 部署（neosun100/hy-mt）后，MCP Server 会暴露翻译 API，可以在 Claude Code 的 MCP 配置中直接添加，让 AI 工具调用本地翻译能力。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Tencent Hunyuan has open-sourced HY-MT 1.5, a translation model in two sizes — 1.8B for edge/real-time use and 7B for high-accuracy scenarios. It supports 33 languages and ships four translation modes: basic, terminology intervention, contextual, and formatted. Compressed to 2-bit and 1.25-bit via AngelSlim, it can run offline on mobile devices.

---

## Overview

Tencent Hunyuan released **HunyuanMT / HY-MT 1.5** as an open-source translation model. Not a general-purpose LLM — purpose-built and tuned for translation.

| Version | Positioning | Best For |
|---------|-------------|----------|
| **HY-MT 1.5-1.8B** | Lightweight, fast | Edge devices, real-time translation, mobile |
| **HY-MT 1.5-7B** | High accuracy | Explanatory translation, mixed-language, professional |

---

## 33 Languages

Covers mutual translation across 33 languages including Chinese (Simplified/Traditional), Cantonese, Japanese, Korean, Vietnamese, Thai, Indonesian, Filipino, Arabic, French, Spanish, German, Russian, Portuguese, Italian, Dutch, Polish, Czech, Ukrainian, Turkish, Persian, Hebrew, Hindi, Bengali, Tamil, Telugu, Gujarati, Urdu, Marathi, Mongolian, Uyghur, Kazakh, Khmer, Burmese.

---

## Four Translation Modes

This is what distinguishes HY-MT 1.5 from generic translation models:

**Basic translation** — Standard mode for everyday text.

**Terminology Intervention** — Pass a custom term dictionary; the model prioritizes specified translations. Critical for legal, medical, and technical documents where generic models fail on specialized vocabulary.

**Contextual Translation** — Provide surrounding context to resolve ambiguity and maintain consistency across long documents.

**Formatted Translation** — Preserves original formatting (Markdown, HTML, tables) without breaking document structure.

---

## Extreme Compression: Offline Mobile Translation

Via Tencent's own **AngelSlim** compression toolkit, HY-MT 1.5-1.8B is further compressed to 2-bit and 1.25-bit quantized versions — with an offline mobile translation demo. On-device, offline translation for privacy-sensitive contexts (medical, legal, internal enterprise documents) becomes viable.

---

## Ecosystem

Community deployments appeared quickly:

- **Docker all-in-one** (neosun100/hy-mt): Web UI + REST API + **MCP Server support**, 38 languages, streaming translation
- **ComfyUI plugin** (freeyaers/ComfyUI-HY-MT): Integrates translation into ComfyUI workflows
- **Pinokio one-click installer** (Gradio interface, user-friendly)
- **RAG translation engine** combining HY-MT + Google Gemma 3 for document intelligence

The MCP Server support means HY-MT can be added directly to Claude Code or any MCP-compatible AI tool — local translation as a callable capability.

---

## FAQ

**Q: How much quality difference is there between 1.8B and 7B?**  
A: 1.8B is optimized for speed and edge deployment; 7B targets complex, explanatory, and mixed-language scenarios. No official BLEU/COMET benchmarks have been published, but the architecture gap suggests 7B will be noticeably more stable in complex cases.

**Q: How does it compare to Google Translate or DeepL?**  
A: No public head-to-head benchmarks yet. Terminology intervention and formatted translation are differentiating capabilities that may outperform general translation services in professional document workflows. Everyday conversational quality remains to be validated by the community.

**Q: How does the MCP Server integration work?**  
A: Deploy via Docker (neosun100/hy-mt), then add the exposed MCP endpoint to Claude Code's MCP config. Local translation becomes a directly callable tool for AI workflows — no API key, no cloud, no quota.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
