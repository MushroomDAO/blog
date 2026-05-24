---
title: "Stable Audio 3.0：6分20秒完整歌曲，四模型开源，本地 MacBook 就能跑"
titleEn: "Stable Audio 3.0: 6-Minute Songs, Four Open-Weight Models, Runs Locally on MacBook"
description: "Stability AI 于 2026 年 5 月 20 日发布 Stable Audio 3.0，最长生成 6 分 20 秒音乐，推出 Small/SFX/Medium/Large 四档模型，中小模型完全开源，支持音频修复续写，训练数据 100% 授权，与华纳、环球音乐集团达成合作。"
descriptionEn: "Stability AI released Stable Audio 3.0 on May 20, 2026 — up to 6:20 of music generation, four model tiers (Small/SFX/Medium/Large) with open weights for the smaller models, audio inpainting and continuation, and 100% licensed training data."
pubDate: 2026-05-24
updatedDate: 2026-05-24
category: Tech-News
tags: ["AI-Music", "Stable-Audio", "Stability-AI", "Open-Source", "Audio-Generation", "Local-AI"]
heroImage: "../../assets/banner-human-ai-coexistence.jpg"
---

> **BLUF**：Stability AI 于 2026 年 5 月 20 日正式发布 Stable Audio 3.0，一次推出四个模型：Small（手机可跑）、SFX（音效专用）、Medium（1.4B 参数，开源最强）、Large（2.7B，闭源顶配）。最长生成 6 分 20 秒完整歌曲，支持音频修复、续写、可变长度生成，训练数据 100% 已授权，MacBook M4 本地即可运行中小模型。

> 📌 官方公告：
> https://stability.ai/news-updates/meet-stable-audio-3-the-model-family-built-for-artistic-experimentation-with-open-weight-models
>
> 📌 GitHub 仓库（含推理 + 微调代码）：
> https://github.com/Stability-AI/stable-audio-3
>
> 📌 Hugging Face 模型合集：
> https://huggingface.co/collections/stabilityai/stable-audio-3
>
> 📌 在线体验 Demo：
> https://huggingface.co/spaces/stabilityai/stable-audio-3

---

## 以前 AI 作曲是"听个响"，现在是一首完整歌

早期 AI 音乐生成工具的输出基本在 30 秒以内——够一段旋律动机，但称不上"歌曲"。Stable Audio 2.0 把上限提到了约 3 分钟，已经算是突破。

Stable Audio 3.0 直接干到 **6 分 20 秒（380 秒）**，Medium 和 Large 模型均达到这个上限。这是一首完整歌曲的标准体量：前奏、主歌、副歌、间奏、尾段全都容得下。更重要的是，官方测试显示在这个长度下旋律结构仍然稳定，不会跑调或重复崩坏。

## 四个模型，各司其职

| 模型 | 参数量 | 开源 | 最长生成 | 定位 |
|------|--------|------|---------|------|
| Small Music | 459M | ✅ | 2 分钟 | 手机/边缘设备可跑 |
| Small SFX | 459M | ✅ | 2 分钟 | 专注音效生成 |
| Medium | 1.4B | ✅ | 6:20 | 开源最强，本地运行首选 |
| Large | 2.7B | ❌ | 6:20 | 闭源，API/企业版顶配 |

**推理速度**（H200 GPU）：
- Small：生成 2 分钟音频仅需 **0.44 秒**
- Medium：生成 6:20 音频仅需 **1.31 秒**

MacBook Pro M4 可以在几秒内本地运行 Small 和 Medium 模型，无需云端 API。

## 不只是"生成"：像修图一样修音频

Stable Audio 3.0 引入了三种**音频编辑能力**，这是与前代最明显的功能扩展：

**1. 音频修复（Inpainting）**
指定音频片段的起止时间，用文字提示替换这段内容。类似 Photoshop 的内容感知填充——删掉一段错误，AI 填入符合上下文的新内容。

**2. 因果续写（Causal Continuation）**
给定一段已有音频，AI 在保持风格和旋律走向的基础上自动续写后续部分。

**3. 可变长度生成**
精确到秒级设置生成时长，不是固定输出固定长度，而是按需指定。

这三个能力组合起来，实际上构成了一个**音频编辑工作流**，而不只是一个"输入 prompt → 输出音频"的生成器。

## 本地运行方法

```bash
# 安装（使用 uv 包管理器）
uv sync --extra ui

# 启动 Gradio 界面，运行 Medium 模型
uv run python run_gradio.py --model medium

# 命令行生成（30 秒，流行风格）
stable-audio --model small-music -p "upbeat pop song, guitar, drums" --duration 30

# 音频续写
stable-audio -p "continue this melody" --init-audio input.wav

# 指定时间段修复（替换第 4-8 秒）
stable-audio -p "add piano fill" --inpaint-audio file.wav --inpaint-start 4 --inpaint-end 8
```

Medium 模型需要 Flash Attention 2，Apple Silicon 上需要额外配置。Small 模型对硬件要求更低，M 系列芯片直接可用。

## 训练数据与授权：正面硬刚 Suno/Udio

AI 音乐生成领域最大的争议一直是版权问题。Suno 和 Udio 都面临唱片公司的集体诉讼，核心指控是未经授权使用受版权保护的音乐训练模型。

Stable Audio 3.0 在这个问题上采取了完全不同的策略：

- **训练数据总量**：127 万余条音频录音
- **来源 1**：AudioSparx 平台授权的 80 万余条（商业授权）
- **来源 2**：Freesound 的 47 万余条（Creative Commons 授权）
- **0 条**未经授权的版权内容

同时，Stability AI 还与**华纳音乐集团**和**环球音乐集团**达成合作协议（具体合作内容未完全披露，但标志着头部唱片公司对开放式 AI 音乐工具态度的转变）。

## 授权与商用

| 授权类型 | 适用对象 | 条件 |
|---------|---------|------|
| Community License | 个人、年收入 < $1M 的组织 | 免费，生成内容归用户所有，可商用 |
| Enterprise License | 年收入 ≥ $1M 的组织 | 付费，含版权侵权法律赔偿保障 |

这意味着：**个人创作者和中小团队可以免费商用 Stable Audio 3.0 的输出内容**，这是相比 Suno/Udio 等商业平台的明确优势。

## 商业化策略分析

Stability AI 这次的产品矩阵设计值得细看：

- **开源小模型和中模型**：获取开发者生态，推动工具链、插件、集成的繁荣
- **闭源大模型走 API 和企业合作**：Large 模型走商业化路线，配合版权保障吸引专业机构
- **LoRA 微调支持**：允许用户基于中模型训练专属风格模型，创造垂直场景价值

这套"开源引流 + 闭源变现 + 企业授权"的组合，是当前 AI 基础设施公司的主流商业模式，Stable Audio 3.0 把它运用在音乐生成这个新赛道上。

**FAQ**

**Q：Stable Audio 3.0 和 Suno、Udio 相比怎么样？**
A：生成质量目前处于同一量级，但核心差异在于授权。Suno/Udio 是闭源商业服务，存在版权争议，且用户对模型无控制权。Stable Audio 3.0 提供开源权重、本地运行能力、100% 授权训练数据，对于需要商用且重视合规的场景有明显优势。

**Q：Small 模型真的能在手机上跑吗？**
A：官方说法是 Small 模型（459M 参数）针对移动端和边缘设备优化，但具体的移动端部署方案（Android/iOS SDK）尚未发布，目前主要是 MacBook 等桌面设备本地运行。

**Q：LoRA 微调需要多少数据和算力？**
A：官方文档暂未给出详细要求，但基于 1.4B 参数的 Medium 模型做 LoRA 微调，通常几十到几百条训练样本配合消费级 GPU（RTX 3090/4090）即可完成，具体参数需参考官方 GitHub 仓库的训练文档。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: Stability AI released Stable Audio 3.0 on May 20, 2026 — four model tiers (Small Music/SFX at 459M, Medium at 1.4B open-weight, Large at 2.7B closed-source), up to 6:20 generation length, audio inpainting/continuation, and 100% licensed training data. Runs locally on MacBook M4.

> 📌 Official announcement:
> https://stability.ai/news-updates/meet-stable-audio-3-the-model-family-built-for-artistic-experimentation-with-open-weight-models
>
> 📌 GitHub (inference + LoRA fine-tuning):
> https://github.com/Stability-AI/stable-audio-3
>
> 📌 Hugging Face models:
> https://huggingface.co/collections/stabilityai/stable-audio-3

## What Changed

Previous AI music tools topped out at 30 seconds to 3 minutes. Stable Audio 3.0 reaches **6 minutes 20 seconds** (380 seconds) with stable melodic structure throughout. This is actual song length — enough for intro, verse, chorus, bridge, and outro.

## Four Models

- **Small Music / Small SFX** (459M): Open-weight. Up to 2 minutes. Runs on consumer hardware, designed for mobile/edge devices. SFX variant specialized for sound effects.
- **Medium** (1.4B): Open-weight. Up to 6:20. The best open-source option — runs locally on MacBook M4 in seconds.
- **Large** (2.7B): Closed-source. API/enterprise only. Highest quality.

Inference speed on H200: Small generates a 2-minute track in 0.44s. Medium generates a 6:20 track in 1.31s.

## New Editing Capabilities

Beyond generation, version 3.0 adds genuine audio editing:
- **Inpainting**: Replace a specific time segment with AI-generated content matching the surrounding context
- **Causal continuation**: Extend existing audio while preserving style and melodic direction
- **Variable-length generation**: Specify exact duration in seconds, not just fixed presets

## Local Setup

```bash
uv sync --extra ui
uv run python run_gradio.py --model medium
```

CLI usage: `stable-audio --model small-music -p "your prompt" --duration 30`

## Training Data and Licensing

1.27M total recordings — all licensed. 806K from AudioSparx (commercial license), 473K from Freesound (Creative Commons). No unlicensed copyrighted material. Stability AI has also announced partnerships with Warner Music Group and Universal Music Group.

Commercial use is free for individuals and organizations under $1M annual revenue (Community License). Enterprise license covers organizations above that threshold with copyright indemnification.

## The Business Model

Stability AI's strategy: open-source Small and Medium to build the developer ecosystem, keep Large closed for API/enterprise revenue, support LoRA fine-tuning to enable vertical specialization. This is standard open-core AI infrastructure playbook, applied to music generation.

**FAQ**

**Q: How does this compare to Suno and Udio?**
A: Comparable generation quality, but fundamentally different in licensing. Suno and Udio face copyright litigation over training data. Stable Audio 3.0 is fully licensed, open-weight, and locally runnable — clear advantages for teams that need commercial use and compliance certainty.

**Q: Can Small models actually run on phones?**
A: Optimized for mobile/edge, but mobile SDKs (Android/iOS) haven't shipped yet. Current local deployment is primarily Mac and PC.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
