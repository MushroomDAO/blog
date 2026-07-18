---
title: "OpenMontage：33K Stars，把 AI 助手变成视频工作室，$1.33 出一条 60 秒动画"
titleEn: "OpenMontage: 33k Stars — Turn Your AI Coding Assistant Into a Video Studio for $1.33"
description: "calesthio/OpenMontage（33K★，AGPLv3）是世界首个开源 Agentic 视频制作系统，12 个管线、52 个工具、500+ Agent Skills。你用自然语言描述视频，Claude Code/Cursor/Copilot 帮你从研究、脚本、素材生成到配音配乐剪辑渲染全流程搞定。零 API key 可用，$1.33 出一条 60 秒 Pixar 风格动画。普通人完整使用指南。"
descriptionEn: "OpenMontage (calesthio/OpenMontage, 33k★, AGPLv3) — the world's first open-source agentic video production system. 12 pipelines, 52 tools, 500+ agent skills. Describe a video in plain language, your AI coding assistant handles research, scripting, asset generation, voice, music, editing, and rendering. Works with Claude Code, Cursor, Copilot, Windsurf, Codex. Zero-key demo works out of the box. Real outputs: $1.33 for a 60-second Pixar-style animation, $0.02 for a 70-second history documentary."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Tech-News"
tags: ["OpenMontage", "AI视频", "开源", "视频制作", "Claude Code", "agentic", "普通人入门"]
heroImage: "../../assets/images/openmongage-ai-video-studio-guide-banner.jpg"
---

> **GitHub**: [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) · **33,174 Stars** · **AGPLv3** · GitHub Trending 第一

---

## 一块钱三毛钱，一条 60 秒动画

想象一下：你打开电脑，对着 AI 助手说一句话——

> "帮我做一条 60 秒的动画，讲神经网络是怎么学习的，Pixar 风格。"

四十分钟后，你得到一条配好旁白、背景音乐、字幕、分镜剪辑的完整视频。
花费：**1.33 美元**。

这不是概念演示，也不是某个收费订阅服务的广告。这是 GitHub 上一个叫 **OpenMontage** 的开源项目的 README 里，作者 calesthio 贴出来的真实账单。

项目上线当天，33,174 颗 Star，冲上 GitHub Trending 第一。

---

## 它到底是什么

用一句话说：**OpenMontage 是一套让你的 AI 编程助手帮你完整制作视频的开源系统。**

但这里有一个关键点需要说清楚——它**不是**那种"把图片拼在一起抖动一下"的工具。

OpenMontage 能处理**真实视频素材**：它可以去 Archive.org、NASA 开放档案、Wikimedia 这些公共素材库里调取真实的视频片段，剪辑、排列、配音、配乐、加字幕，最终渲染成一条完整的成片。

整套系统包含：
- **12 种生产管线（pipelines）**：覆盖动画短片、历史纪录片风格、产品广告、Ghibli 风格等不同类型
- **52 个工具**：从素材搜索、脚本生成，到语音合成、视频渲染，逐一拆解并自动调度
- **500+ Agent Skills**：AI 助手能调用的细粒度技能单元

你不需要学会这些技术名词。你只需要知道：**你用中文或英文描述你想要的视频，Claude Code、Cursor、Copilot、Windsurf 或 Codex 这类 AI 助手会帮你把剩下的事全做了。**

---

## 安装：比你想象的简单

### 第一步：安装前置工具

**Python 3.10 或更新版本**
- macOS / Linux：`brew install python@3.10` 或 python.org 下载
- Windows：python.org 下载 .exe，安装时勾选"Add Python to PATH"

**FFmpeg**（视频处理核心库）
- macOS：`brew install ffmpeg`
- Ubuntu / Debian：`sudo apt install ffmpeg`
- Windows：ffmpeg.org 下载，解压后把 `bin` 文件夹加入系统 PATH

**Node.js 18 或更新版本**
- 所有平台：nodejs.org 下载 LTS 版安装包

**AI 编程助手**（选一个）：Claude Code、Cursor、GitHub Copilot、Windsurf 或 Codex

### 第二步：克隆并安装

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

`make setup` 自动处理所有 Python 和 Node.js 依赖，约 3–10 分钟。安装完成后，用你的 AI 助手打开这个文件夹开始工作。

---

## 硬件：什么样的电脑够用

### 零 API 模式（完全免费）：最低配置

- CPU：近三年 Intel Core i5 / AMD Ryzen 5 以上
- 内存：8GB（16GB 更顺畅）
- 硬盘：留出 10GB 空间
- 网络：能访问 Archive.org 和 GitHub

这个配置可以用 Piper TTS 配旁白 + Archive.org 素材 + Remotion 渲染，**零成本**。

### 本地 GPU 视频生成（可选进阶）

NVIDIA RTX 3080 / 3090 / 4080 / 4090（显存 10GB 以上）

```bash
make install-gpu
# .env 里加：VIDEO_GEN_LOCAL_ENABLED=true
```

支持：wan2.1-1.3b、wan2.1-14b、hunyuan-1.5、ltx2-local、cogvideo-5b

---

## 零成本路径：一分钱不花能做什么

| 你想要的能力 | 用什么工具 | 费用 |
|---|---|---|
| 旁白配音 | Piper TTS（本地离线运行） | 免费 |
| 真实视频素材 | Archive.org、NASA 开放存档、Wikimedia | 免费 |
| 图片素材 | Pexels、Unsplash、Pixabay（免费开发者 key） | 免费 |
| 文字动画 / 字幕 / 弹性动效 | Remotion（React 渲染引擎） | 免费 |
| 动感排版 / 产品宣传片渲染 | HyperFrames（HTML 渲染引擎） | 免费 |

---

## 付费路径：加 Key 能得到什么

**真实成本案例（README 中）**：

| 视频 | 描述 | 花费 |
|---|---|---|
| "THE LAST BANANA" | 60 秒 Pixar 风格动画，6 个 Kling v3 片段 + Google 旁白 | **$1.33** |
| "The Library at Alexandria" | 70 秒历史主题纪录片，5 个手工场景 + OpenAI 旁白 | **$0.02** |
| "VOID - Neural Interface" | 产品广告，仅 OpenAI key | **$0.69** |
| "Afternoon in Candyland" | Ghibli 风格动画，12 张 FLUX 图 + 音乐 | **$0.15** |

---

## 创意方向：三个你现在就能开始的场景

### 产品介绍视频

```
"Make a 45-second product video for a reusable water bottle brand. 
Modern lifestyle tone, no narration, with upbeat background music 
and text overlays. Use clean stock footage of outdoor activities."
```

### 学习解说视频

```
"Make a 60-second animated explainer about how neural networks learn. 
Use simple visual metaphors, friendly narration, include subtitles."
```

### 参考风格复刻

```
"Here's a YouTube Short I love. Make something like this, 
but about quantum computing."
```

---

## 发布平台建议

| 平台 | 推荐比例 | 时长建议 |
|---|---|---|
| 抖音 / TikTok / Reels | 9:16 竖版 | 15–60 秒 |
| 小红书 | 9:16 或 1:1 方形 | 30–90 秒 |
| YouTube / B 站 | 16:9 横版 | 60 秒以上 |
| Twitter / X | 16:9 横版 | 30–60 秒 |

在提示词里直接说明比例，渲染管线会自动适配输出尺寸。

---

> **AGPLv3 授权**：免费使用、修改、自部署。商业服务必须开源修改部分。  
> **仓库**：[github.com/calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) · **作者**：[@calesthioailabs](https://x.com/calesthioailabs)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: OpenMontage is the world's first open-source agentic video production system. 33k stars, AGPLv3. Describe a video in plain language — Claude Code, Cursor, Copilot, Windsurf, or Codex handles everything: research, scripting, asset sourcing, voice synthesis, music, editing, and rendering. Real costs: $1.33 for a 60-second Pixar-style animation, $0.02 for a 70-second history documentary, $0.69 for a full product ad. Zero-API mode works out of the box.

---

## Setup

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

Requirements: Python 3.10+, FFmpeg, Node.js 18+, any AI coding assistant. `make setup` handles all dependencies automatically.

## Zero-Cost Path

Free tier gives you: Piper TTS (offline voice), Archive.org + NASA + Wikimedia footage, Pexels/Unsplash/Pixabay images (free keys), Remotion (React video renderer), HyperFrames (HTML/CSS/GSAP). Total API cost: $0.

## Paid Path

Add API keys to `.env` to unlock AI-generated images (FLUX via fal.ai), AI video clips (Kling, Veo, Runway), premium TTS (ElevenLabs, OpenAI), and AI music (Suno). Costs are per-output and very low — see the README for the exact breakdown.

## Hardware

Zero-API: any laptop from the last 3 years, 8GB RAM. Local GPU video generation (optional): NVIDIA RTX 3080+ with 10GB+ VRAM, `make install-gpu`.

## Example Prompts

```
"Make a 60-second animated explainer about how neural networks learn"
"Make a 75-second documentary montage about city life in the rain. Use real footage only."
"Here's a YouTube Short I love. Make something like this, but about quantum computing."
```

**Links**: [GitHub](https://github.com/calesthio/OpenMontage) · [YouTube @OpenMontage](https://www.youtube.com/@OpenMontage)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
