---
title: "Cuti Harness：开源长程视频世界生成器，多轮对话从 15 秒扩展到 3 分钟，本地不需要 GPU"
titleEn: "Cuti Harness: Open-Source Long-Horizon Video World Generator — Multi-Turn Conversation Grows 15s to 3 Minutes, No Local GPU"
description: "VideoVerses/Cuti-Harness，MIT 开源，TypeScript + Python，基于 DeepSeek Harness 的插件化视频世界生成器。多轮对话累积扩展，从 15 秒到 3 分钟+；单次 brief 自动生成 5 分钟视频。本地运行不需要 GPU，只要 Node.js 22+ + Conda。视频生成依赖云端 API（WaveSpeed Seedance 或 Ark，约 $0.81/clip）。开发者预览阶段。"
descriptionEn: "VideoVerses/Cuti-Harness, MIT open source, TypeScript + Python, plugin-based video world generator on DeepSeek Harness. Multi-turn conversation grows from 15s to 3 minutes; single brief auto-generates a 5-minute trailer. No local GPU required — only Node.js 22+ and Conda. Video generation uses cloud APIs (WaveSpeed Seedance or Ark, ~$0.81/clip). Developer preview."
pubDate: "2026-09-17"
updatedDate: "2026-09-17"
category: "Tech-Experiment"
tags: ["open-source", "video-generation", "AI-video", "DeepSeek-Harness", "long-video", "MIT", "TypeScript", "video-world"]
heroImage: "../../assets/images/cuti-harness-open-source-video-world-generator-deepseek-harness-long-video-banner.jpg"
---

> 📌 开源仓库：https://github.com/videoverses/cuti-harness
> 产品页：https://newai.land/cuti-harness
> 在线产品：https://www.cuti.land
> License：MIT | Language：TypeScript + Python

---

大多数 AI 视频工具的工作流是：写提示词 → 生成一个 5 到 10 秒的片段 → 不满意重来。Cuti Harness 想做的事不一样：**用对话一次次延展同一个视频世界**，每一轮对话不会从头来，而是在已有时间线上继续。

Demo 1 展示了五轮对话，从一段 15 秒的液态玻璃城市镜头开始，逐轮加入天使、追踪镜头、历史时代穿越，最终导出一部 3 分钟短片。Demo 2 是另一个极端：从单一创作简报出发，全自动规划镜头、调度生成、拼接导出，产出 5 分钟预告片，全程不需要人工干预时间线编辑。

这个项目是今天（2026-09-17）刚发布的，项目负责人是何颖清（Yingqing He），基于 DeepSeek Harness，MIT 开源。

---

## 架构：三层分工

```
Video Studio (:3000)    ← 浏览器前端，对话界面
       ↓
Video Runtime (:8001)   ← 项目/时间线/Artifact 持久化、增量构建、导出
       ↓
Cuti Harness (:3080)    ← LLM 对话循环 + 视频工具选择
       ↓
Provider/Workflow/Validator 插件  ← 实际视频生成 API 调用
```

Harness 层负责理解你说了什么、规划做什么；Runtime 层负责把做好的 Artifact（片段）持久化，记录依赖关系，每轮完成后更新时间线；Studio 层是你与系统对话的界面。

插件化设计意味着视频生成后端可以换——默认用 WaveSpeed（Seedance）或 Volcengine Ark，也可以接自己的 provider。

---

## 本地运行：不需要 GPU

这是和很多 AI 视频工具最不一样的地方：**Cuti Harness 本地只跑协调层，不在本机做神经网络推理。**

本地环境要求：
- Git
- Node.js 22.19+ 或 24+
- pnpm 11.x（`corepack enable` 安装）
- **Conda**（Miniconda 或 Miniforge 即可）
- Python 3.11（通过 Conda 管理）
- 正常的网络（安装阶段需要下载依赖）
- 不需要 Docker、PostgreSQL、Redis

启动流程：

```bash
# 1. 克隆（浅克隆，快）
git clone --depth 1 --branch deepseek-harness-open \
  https://github.com/VideoVerses/Cuti-Harness.git
cd cuti-video-agent

# 2. Conda 环境
conda env create --file environment.yml
conda activate cuti-video-agent

# 3. 前端构建
pnpm install --frozen-lockfile
pnpm run build

# 4. 配置 API Key（见下一节）
cp config/.env.example .env

# 5. 安装本地依赖（Python 服务 + FFmpeg + HyperFrames 渲染器）
pnpm video:setup -- --data-dir .video-agent-harness-data

# 6. 启动
pnpm video:local -- --data-dir .video-agent-harness-data
```

打开 http://127.0.0.1:3000 进入 Video Studio，没有登录流程，本地用户身份是 `local-user`。

---

## 成本：主要花在云端 API 上

需要配置三类密钥：

| 密钥 | 用途 | 备注 |
|------|------|------|
| `OPENAI_API_KEY` | Harness 对话与规划（LLM） | 必须；可换其他兼容接口 |
| `WAVESPEED_API_KEY` | 默认视频生成（Seedance 模型） | 不填则进入 Code-to-Video 本地模式 |
| `ARK_API_KEY` | 替代视频生成（Volcengine Ark） | WaveSpeed 的替代方案 |
| `SUNO_API_KEY` | 音乐生成 | 可选 |

**WaveSpeed 定价（Seedance 2.5）**：
- Text-to-video / Image-to-video：约 $0.81/次（10% 折扣后）
- Video-edit / Video-extend：约 $0.99/次

每次调用生成一个片段（通常 5-10 秒）。估算：
- **3 分钟视频**（Demo 1 风格，多轮迭代）：约 18-36 个片段 → **$15-$30**
- **5 分钟一次性生成**（Demo 2 风格）：约 30-60 个片段 → **$25-$50**
- 加上 OpenAI API 规划成本（每次对话约 $0.1-0.5）

LLM 规划的钱不多，主要花在视频生成上。**做一个 5 分钟高质量视频，云端成本约 $25-50。**

**没有视频 API Key 时的 Code-to-Video 模式**：WAVESPEED_API_KEY 为空时，系统默认进入本地 Code-to-Video 路径，有专用合成按钮可以为每个项目单独开关。这个模式依赖本地渲染（HyperFrames），适合调试和低成本测试，质量与神经视频生成有差距。

---

## Demo 实际效果

**Demo 1 — 对话式世界构建（Glass Tide）**

五轮提示词，每轮在前一个版本基础上加内容：

| 轮次 | 操作 | 时长 |
|------|------|------|
| 第 1 轮 | 液态玻璃城市，蓝调黄金时刻，35mm 变形镜头 | 15 秒 |
| 第 2 轮 | 延续 15 秒，动感更强 | 30 秒 |
| 第 3 轮 | 再加 15 秒，加入天使飞入 | 45 秒 |
| 第 4 轮 | 摄像机跟随天使，天堂出现 | 60 秒 |
| 第 5 轮 | 天使飞越史前/古代/近代/现代，导出 3 分钟版 | 3 分钟 |

每一轮不是重新生成，而是在已有时间线上追加——这是传统视频工具做不到的核心能力。

**Demo 2 — 单次 brief 全自动生成（After the Rain）**

一份电影创作简报输入，Harness 自动规划分镜、调度生成、拼接，导出 ~5 分钟预告片，无需人工编辑时间线。文档里有完整的简报原文（after-the-rain.md）。

---

## 项目状态与限制

- **开发者预览阶段**：可能有不向后兼容的变更
- 视频生成依赖付费云 API，**纯本地零成本高质量视频暂时不支持**
- Docker Compose 部署支持 PostgreSQL 和多用户场景，本地 npm 模式是单用户信任环境
- 中文界面：Video Studio 默认打开中文路径 `/#/zh/create`
- 团队：何颖清（项目负责人）、孙凯、王松松、方鹏军、邢亚洲

---

## 总结

Cuti Harness 解决的问题很具体：**让 AI 视频从"生成一个片段"变成"维护一个视频世界"**。多轮对话积累是关键差异——你不需要每次从头来，可以说"在上一段结尾接着往前飞"，系统知道上下文在哪。

对本地硬件的要求极低（只需要 Node + Python）是另一个亮点，但代价是视频生成成本落在云端 API 上，做一个 5 分钟高质量成片大概花 $30-50。适合严肃的视频创作者，对偶尔玩玩的用户来说成本偏高。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/videoverses/cuti-harness
> Product page: https://newai.land/cuti-harness
> Live product: https://www.cuti.land
> License: MIT | Language: TypeScript + Python

---

Most AI video tools work the same way: write a prompt → generate a 5-10 second clip → if you don't like it, start over. Cuti Harness takes a different approach: **extend the same video world through conversation**, where each turn builds on the existing timeline instead of regenerating from scratch.

Demo 1 shows five conversation turns, starting from a 15-second liquid-glass city shot, adding an angel, a tracking follow, and a journey through historical eras, ending with a 3-minute short film export. Demo 2 is the other extreme: from a single cinematic brief, the system automatically plans shots, schedules generation, and assembles a ~5-minute trailer with no manual timeline editing between steps.

This project launched today (2026-09-17), led by Yingqing He, built on DeepSeek Harness, MIT licensed.

---

## Architecture: Three Layers

```
Video Studio (:3000)    ← Browser frontend, conversation UI
       ↓
Video Runtime (:8001)   ← Project/timeline/Artifact persistence, incremental builds, exports
       ↓
Cuti Harness (:3080)    ← LLM conversation loop + video tool selection
       ↓
Provider/Workflow/Validator plugins  ← Actual video generation API calls
```

The Harness layer understands your instructions and plans what to do. The Runtime layer persists the resulting Artifacts (clips), tracks dependencies, and updates the timeline after each turn. Studio is your conversation interface.

The plugin architecture means video generation backends are swappable — default is WaveSpeed (Seedance) or Volcengine Ark; you can wire in your own provider.

---

## Local Setup: No GPU Required

This is the biggest difference from most AI video tools: **Cuti Harness only runs coordination logic locally — it doesn't do neural inference on your machine.**

Local requirements:
- Git
- Node.js 22.19+ or 24+
- pnpm 11.x (`corepack enable` to install)
- **Conda** (Miniconda or Miniforge)
- Python 3.11 (managed via Conda)
- Internet access during setup for dependency downloads
- No Docker, PostgreSQL, or Redis needed

Setup flow:

```bash
git clone --depth 1 --branch deepseek-harness-open \
  https://github.com/VideoVerses/Cuti-Harness.git
cd cuti-video-agent
conda env create --file environment.yml && conda activate cuti-video-agent
pnpm install --frozen-lockfile && pnpm run build
cp config/.env.example .env   # then add your API keys
pnpm video:setup -- --data-dir .video-agent-harness-data
pnpm video:local -- --data-dir .video-agent-harness-data
```

Open http://127.0.0.1:3000. No login flow; local identity is `local-user`.

---

## Cost: Mostly Cloud API Spend

Three categories of API keys:

| Key | Purpose | Notes |
|-----|---------|-------|
| `OPENAI_API_KEY` | Harness conversation and planning (LLM) | Required; compatible endpoints work |
| `WAVESPEED_API_KEY` | Default video generation (Seedance model) | Empty = Code-to-Video local mode |
| `ARK_API_KEY` | Alternative video generation (Volcengine Ark) | Swap for WaveSpeed |
| `SUNO_API_KEY` | Music generation | Optional |

**WaveSpeed pricing (Seedance 2.5):**
- Text-to-video / Image-to-video: ~$0.81/call (after 10% discount)
- Video-edit / Video-extend: ~$0.99/call

Each call generates one clip (typically 5-10 seconds). Estimated costs:
- **3-minute video** (Demo 1 style, multi-turn iteration): ~18-36 clips → **$15-$30**
- **5-minute one-shot** (Demo 2 style): ~30-60 clips → **$25-$50**
- Plus OpenAI API for planning (~$0.1-0.5 per conversation)

Planning costs are modest; the spend is on video generation. **Expect $25-50 in cloud API costs for a high-quality 5-minute video.**

**Code-to-Video mode (no video API key):** When `WAVESPEED_API_KEY` is empty, projects default to local rendering via HyperFrames. A dedicated toggle button controls this per-project. Useful for testing and debugging at zero cost; quality differs from neural video generation.

---

## Demo Results

**Demo 1 — Interactive world building (Glass Tide)**

Five turns, each building on the previous export:

| Turn | Action | Duration |
|------|--------|----------|
| 1 | Liquid glass city, blue hour, 35mm anamorphic | 15 seconds |
| 2 | Extend 15 more seconds, faster and more dynamic | 30 seconds |
| 3 | Add 15 more seconds, angel flies in | 45 seconds |
| 4 | Camera follows the angel forward, heaven appears | 60 seconds |
| 5 | Angel flies through prehistoric/ancient/early-modern/contemporary eras, export 3-minute version | 3 minutes |

Each turn appends to the existing timeline — not a regeneration. This is the core capability traditional video tools can't replicate.

**Demo 2 — One-shot automated trailer (After the Rain)**

One cinematic brief in → Harness plans shots, schedules generation, assembles a ~5-minute trailer automatically, with no manual timeline editing required. The full brief document is included in the repo.

---

## Current State and Limitations

- **Developer preview**: breaking changes are possible
- Video generation requires paid cloud APIs; **local zero-cost high-quality video is not currently supported**
- Docker Compose deployment supports PostgreSQL and multi-user scenarios; local npm mode is single-user, trusted environment only
- Chinese UI by default: Video Studio opens `/#/zh/create`
- Team: Yingqing He (project lead), Kai Sun, Songsong Wang, Pengjun Fang, Yazhou Xing

---

## Summary

Cuti Harness addresses a specific problem: **moving AI video from "generate a clip" to "maintain a video world."** Multi-turn accumulation is the key difference — you don't start over each time; you can say "keep following the angel forward" and the system knows where the timeline is.

Minimal local hardware requirements (Node + Python only) is a real plus, but the tradeoff is that video generation costs live in cloud APIs. Expect $30-50 to produce a high-quality 5-minute film. A good fit for serious video creators; cost will feel high for casual exploration.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
