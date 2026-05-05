---
title: "王炸：440MB 翻译模型打赢 Qwen3-32B，腾讯 HunyuanMT 开源了"
titleEn: "Bombshell: Tencent's 440MB HunyuanMT Beats Qwen3-32B in Translation Quality"
description: "腾讯开源 HunyuanMT（Hy-MT 1.5），通过 AngelSlim 压缩后仅 440MB，在 FLORES-200 XCOMET 翻译质量评测中超过 Qwen3-32B（65GB）。支持 33 种语言，可完全离线运行在手机上，专业翻译能力碾压通用大模型。"
descriptionEn: "Tencent open-sources HunyuanMT (Hy-MT 1.5). Compressed via AngelSlim to just 440MB, it outperforms Qwen3-32B (65GB) on FLORES-200 XCOMET translation benchmarks across 33 languages. Runs fully offline on mobile — a purpose-built translation model crushing general-purpose LLMs."
pubDate: "2026-05-05"
updatedDate: "2026-05-05"
category: "Tech-News"
tags: ["腾讯", "HunyuanMT", "翻译模型", "开源", "AngelSlim", "多语言", "本地部署", "模型压缩"]
heroImage: "../../assets/banner-digital-public-goods.jpg"
---

**结论先行（BLUF）**：440MB 的翻译模型，在 FLORES-200 翻译质量评测上打赢了 Qwen3-32B（65GB）。腾讯这次放出的是两件东西：**HunyuanMT**（最强开源翻译模型）+ **AngelSlim**（把它压缩到 440MB 的工具）。支持 33 种语言，可以完全离线跑在手机上，开源免费。

---

## 这件事有多炸

用数字说话：

| 模型 | 大小 | FLORES-200 翻译质量 |
|------|------|-------------------|
| **Hy-MT1.5-1.8B-1.25bit** | **440MB** | **超过 Qwen3-32B** |
| **Hy-MT1.5-1.8B-2bit** | **574MB** | **接近 Qwen3-32B** |
| Qwen3-32B | ~65,000MB（65GB）| 对照组 |
| DeepSeek V32 | ~690,000MB（690GB）| 对照组 |

一个 440MB 的文件，翻译质量比 65GB 的 Qwen3-32B 更强。

这不是魔法，是**专用模型对通用模型的降维打击**。翻译这件事，一个专门为它训练的小模型，比一个什么都会的超大模型做得更好。

---

## 两件事，一起放出来

腾讯这次同时开源了两个项目，配合使用：

### 1. HunyuanMT（Hy-MT 1.5）— 翻译模型本体

GitHub / HuggingFace：`tencent/Hunyuan-MT`

两个尺寸：

| 版本 | 定位 |
|------|------|
| **HY-MT 1.5-1.8B** | 轻量快速，适合本地和边缘部署 |
| **HY-MT 1.5-7B** | 高精度，复杂语言场景 |

支持 **33 种语言**互译（实际条目 38 个，官方将简/繁/粤等方言单独计列）：

> 中文（简体）、中文（繁体）、粤语、英语、日语、韩语、法语、德语、西班牙语、葡萄牙语、意大利语、俄语、波兰语、捷克语、乌克兰语、荷兰语、土耳其语、阿拉伯语、波斯语、希伯来语、印地语、乌尔都语、孟加拉语、古吉拉特语、马拉地语、泰卢固语、泰米尔语、越南语、泰语、印尼语、马来语、菲律宾语、高棉语、缅甸语、蒙古语、藏语、哈萨克语、维吾尔语

四种翻译模式：基础翻译、**术语干预**（自定义词典，专业文档必备）、**上下文感知**、**格式化翻译**（保留 Markdown/HTML 格式）。

### 2. AngelSlim — 模型压缩工具

GitHub：[github.com/Tencent/AngelSlim](https://github.com/Tencent/AngelSlim)

这是让 1.8B 模型变成 440MB 的工具。核心算法是腾讯自研的 **Sherry**——一种硬件高效的 1.25-bit 量化算法（有论文，有代码）。

压缩结果：
- **Hy-MT1.5-1.8B-2bit**：574MB，含权重文件和 GGUF 格式
- **Hy-MT1.5-1.8B-1.25bit**：440MB，同上，极限压缩

还配了一个 **Android APK 离线翻译 demo**——下载即用，无需网络，33 种语言本地跑。

---

## 为什么专用小模型能赢通用大模型

这个结果反直觉，但有清晰的解释：

通用大模型（Qwen3-32B、DeepSeek）要同时做代码、推理、写作、数学……翻译只是它们的一个次要能力。

HunyuanMT 的全部参数都用来做翻译这一件事：语言对齐、术语一致性、句法结构转换。同等参数量下，专用模型的翻译能力天然更强。

而 AngelSlim 的 Sherry 1.25-bit 算法证明了：**在特定任务上，模型可以被压缩到极致而不明显损失任务精度**。

---

## 实际意义

**能不能开发个 App 替代翻译机？**

技术上完全可行。440MB 的模型 + 33 种语言 + 离线运行，已经超过市面上大多数专用翻译设备（科大讯飞翻译机等）的能力范围。

差的只是：
1. 一个好用的手机 App 界面（目前只有 APK demo）
2. 语音输入/输出（需要对接 ASR + TTS）

社区已经有人在做：Docker 部署版（含 MCP Server）、ComfyUI 插件、Pinokio 一键安装包都出来了。手机 App 版本估计不远。

---

## 快速使用

**在线试用（Docker 一键部署）**：
```bash
# neosun100/hy-mt：包含 Web UI + REST API + MCP Server
docker run ...  # 见 github.com/neosun100/hy-mt
```

**离线手机端**：
- 下载 APK：[Hy-MT-demo.apk](https://huggingface.co/AngelSlim/Hy-MT1.5-1.8B-1.25bit/blob/main/Hy-MT-demo.apk)
- 安装即用，无需网络，无需账号

**本地 Python 使用**：
```bash
pip install angelslim
# 量化压缩参考 AngelSlim 文档
```

---

## 常见问题

**Q: 440MB 能真的超过 Qwen3-32B 吗？不是通用能力，是翻译专项？**  
A: 是的，仅限翻译任务。FLORES-200 是专门的多语言翻译质量评测基准（XCOMET 分数），Hy-MT1.5 在这个专项评测上超过了 Qwen3-32B。通用能力（代码、推理、写作）肯定不如 32B 模型。

**Q: 和 Google Translate、DeepL 比怎么样？**  
A: 官方 benchmark 主要对比的是开源模型，没有直接与 Google/DeepL 的对比数据。从语言覆盖（33 种）和术语干预能力来看，专业文档场景有优势；日常对话翻译的对比有待社区验证。

**Q: MCP Server 是什么意思？**  
A: 社区部署版（neosun100/hy-mt）提供了 MCP Server 接口，可以在 Claude Code 的 MCP 配置里直接添加，让 AI 工具把本地翻译作为一个可调用的能力使用——不用任何 API key，完全本地。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: A 440MB translation model that outperforms Qwen3-32B (65GB) on FLORES-200 translation benchmarks. Tencent released two things simultaneously: **HunyuanMT** (the translation model) and **AngelSlim** (the compression toolkit that shrinks it to 440MB). 33 languages, fully offline on mobile, open-source.

---

## The Numbers That Matter

| Model | Size | FLORES-200 Translation Quality |
|-------|------|-------------------------------|
| **Hy-MT1.5-1.8B-1.25bit** | **440MB** | **Beats Qwen3-32B** |
| **Hy-MT1.5-1.8B-2bit** | **574MB** | Near Qwen3-32B |
| Qwen3-32B | ~65,000MB (65GB) | Baseline |
| DeepSeek V32 | ~690,000MB (690GB) | Baseline |

A 440MB file with higher translation quality than a 65GB model. This is purpose-built vs. general-purpose — and purpose wins.

---

## Two Projects, Released Together

### 1. HunyuanMT (Hy-MT 1.5) — The Translation Model

Two sizes: 1.8B (lightweight, local deployment) and 7B (high accuracy, complex scenarios). Supports **33 languages** (38 entries — dialects counted separately):

> Chinese (Simplified), Chinese (Traditional), Cantonese, English, Japanese, Korean, French, German, Spanish, Portuguese, Italian, Russian, Polish, Czech, Ukrainian, Dutch, Turkish, Arabic, Persian, Hebrew, Hindi, Urdu, Bengali, Gujarati, Marathi, Telugu, Tamil, Vietnamese, Thai, Indonesian, Malay, Filipino, Khmer, Burmese, Mongolian, Tibetan, Kazakh, Uyghur

Four translation modes: basic, **terminology intervention** (custom glossary, essential for professional docs), **contextual** (disambiguates with surrounding context), **formatted** (preserves Markdown/HTML structure).

### 2. AngelSlim — The Compression Toolkit

GitHub: [github.com/Tencent/AngelSlim](https://github.com/Tencent/AngelSlim)

The tool that compresses 1.8B → 440MB. Core algorithm: **Sherry**, Tencent's proprietary 1.25-bit hardware-efficient quantization (published paper + open code).

Results:
- **Hy-MT1.5-1.8B-2bit**: 574MB (weights + GGUF format)
- **Hy-MT1.5-1.8B-1.25bit**: 440MB (extreme compression)
- **Android APK offline demo**: download and run — no network, no account, 33 languages locally

---

## Why a 440MB Specialist Beats a 65GB Generalist

General-purpose models (Qwen3-32B, DeepSeek) allocate parameters across code, reasoning, writing, math, translation... Translation is one of many tasks.

HunyuanMT dedicates all parameters to one thing: language alignment, terminology consistency, syntactic transfer. Same parameter count → better translation.

And Sherry's 1.25-bit algorithm proves that **on specific tasks, models can be compressed to extremes without significant accuracy loss on that task**.

---

## Could This Replace a Dedicated Translation Device?

Technically, yes. 440MB + 33 languages + offline = capabilities exceeding most dedicated translation hardware on the market.

What's missing:
1. A polished mobile app UI (currently just an APK demo)
2. Voice input/output (needs ASR + TTS integration)

The community is already building: Docker deployment with MCP Server, ComfyUI plugin, Pinokio one-click installer. A full mobile app isn't far off.

---

## Quick Start

**Offline mobile**: Download [Hy-MT-demo.apk](https://huggingface.co/AngelSlim/Hy-MT1.5-1.8B-1.25bit/blob/main/Hy-MT-demo.apk) — install and use immediately, no network required.

**Docker (Web UI + REST API + MCP Server)**:
```bash
# github.com/neosun100/hy-mt
# Includes streaming translation, dark/light theme, batch API
```

---

## FAQ

**Q: Does 440MB actually beat Qwen3-32B in translation — not just on some narrow metric?**  
A: Yes, specifically on FLORES-200 XCOMET, a standard multilingual translation quality benchmark. General capabilities (code, reasoning, writing) are not claimed — this is translation-specific. But translation is exactly the task.

**Q: How does it compare to Google Translate or DeepL?**  
A: Official benchmarks compare against open-source models only. No direct Google/DeepL comparison data. Terminology intervention and formatted translation are differentiating capabilities for professional documents; everyday conversational quality awaits community validation.

**Q: What does MCP Server mean in practice?**  
A: The community Docker deployment (neosun100/hy-mt) exposes an MCP endpoint. Add it to Claude Code's MCP config and you get local translation as a directly callable tool — no API key, no quota, no cloud.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
