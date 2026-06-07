---
title: "Video Expert Analyzer 完全指南：Walter Murch 六法则 + Mac MLX 本地模型全路径"
description: "ALBEDO-TABAI/Video-expert-analyzer 深度调研：从场景检测到五维 AI 评分，完整讲透工具架构、云端 API 和 Mac 本地 MLX 模型（oMLX / Rapid-MLX + Qwen-VL / Gemma 4）两条路径的部署全过程。"
titleEn: "Video Expert Analyzer Complete Guide: Walter Murch's Six Rules + Mac MLX Local Model Full Walkthrough"
descriptionEn: "Deep dive into ALBEDO-TABAI/Video-expert-analyzer: from scene detection to 5D AI scoring, covering tool architecture, cloud API path, and full Mac local MLX model deployment via oMLX / Rapid-MLX with Qwen-VL / Gemma 4."
pubDate: 2026-06-07
category: "Tech-Experiment"
tags: ["Video Analysis", "AI Agent", "MLX", "Apple Silicon", "oMLX", "Rapid-MLX", "Walter Murch", "开源工具"]
lang: "zh-CN"
heroImage: "../../assets/images/video-expert-analyzer-mac-mlx-local-banner.png"
---

如果你做视频、剪视频，或者要分析竞品视频，你可能早就想过一个问题：**有没有办法让 AI 帮我看镜头、打分、把好素材挑出来？**

有。而且还挺完整。

这篇文章深度调研了 `ALBEDO-TABAI/Video-expert-analyzer`（v2.2.0，MIT 开源），并重点给出**在 Mac Apple Silicon 上用本地 MLX 模型**完成视觉评分的完整路径——不用花云端 token，离线运行，数据不离本机。

---

## 工具是什么

[Video Expert Analyzer](https://github.com/ALBEDO-TABAI/video-expert-analyzer) 是一个基于 **Walter Murch 剪辑六法则** 的 AI 视频分析工具。

**Walter Murch 是谁？** 奥斯卡最佳剪辑奖得主，《现代启示录》《英国病人》剪辑师，理论著作《眨眼之间》的作者。他提出的六法则优先级：

> 情感 (Emotion) > 故事 (Story) > 节奏 (Rhythm) > 视线追踪 (Eye-trace) > 2D 平面 (2D Plane) > 3D 空间 (3D Space)

一句话总结：**一个情感真挚但画面略抖的镜头，优于一个画面完美但内容空洞的镜头。**

工具把这套理论转化成五维打分体系，配合 AI 视觉模型对每个场景逐帧评估，自动输出精选镜头。

### 支持的平台和模型

| 视频来源 | 状态 |
|---------|------|
| B 站 (Bilibili) | ✅ 完全支持，含字幕 API |
| YouTube | ✅ 完全支持 |
| 抖音 (Douyin) | ✅ 专用下载器，无需登录 |
| 小红书 | ✅ 专用下载器 |

| AI 评分模型 | Agent 模式 | API 模式 |
|------------|-----------|---------|
| Gemini 3.0 Flash / Pro | ✅ 推荐 | ✅ 推荐 |
| Kimi 2.5 | ✅ | ✅（中文优秀） |
| Claude Sonnet/Opus | ✅ | ❌ 无 OpenAI 兼容 API |
| **本地 MLX 视觉模型** | ✅ | ✅（本文重点） |
| 纯文本模型 | ❌ | ❌ |

---

## 核心工作流程

工具分两个阶段，理解这个是关键：

```
阶段 1：数据处理 Pipeline（pipeline_enhanced.py）
────────────────────────────────────────────────
📥 下载视频         → video.mp4
🎵 提取音频         → video.m4a
🎞️  场景检测         → scenes/*.mp4（精准切割镜头）
🎤 智能字幕提取     → video.srt
    B站API → 内嵌字幕 → RapidOCR → FunASR（四级降级）
🖼️  提取代表帧       → frames/*.jpg
📊 生成评分模板     → scene_scores.json

阶段 2：AI 视觉评分（ai_analyzer.py）
────────────────────────────────────────────────
🤖 多模态模型逐帧分析画面
🧮 五维打分 × 动态权重 = 加权总分
⭐ 高分镜头复制到 best_shots/
📄 输出完整分析报告（*_complete_analysis.md）
```

**关键点**：阶段 1 不依赖 AI 大模型，ffmpeg + PySceneDetect 在本地完成。阶段 2 才需要**有视觉能力的多模态模型**——这是 Mac 本地 MLX 的用武之地。

---

## 五维评分体系

| 维度 | 基础权重 | 评估要点 |
|------|---------|---------|
| **美感 (Aesthetic)** | 20% | 构图三分法、光影、色彩和谐 |
| **可信度 (Credibility)** | 20% | 表演自然度、物理逻辑真实感 |
| **冲击力 (Impact)** | 20% | 视觉显著性、第一眼吸引力 |
| **记忆度 (Memorability)** | 20% | 独特视觉符号、冯·雷斯托夫效应 |
| **趣味度 (Fun/Interest)** | 20% | 参与感、社交货币潜力 |

权重还会根据场景类型动态调整：

| 场景类型 | 调整后权重 | 典型场景 |
|---------|---------|---------|
| TYPE-A Hook 钩子型 | 冲击 40% + 记忆 30% | 开场、高能时刻 |
| TYPE-B Narrative 叙事型 | 可信 40% + 记忆 30% | 对话、情感 |
| TYPE-C Aesthetic 氛围型 | 美感 50% + 节奏 30% | 空镜、慢动作 |
| TYPE-D Commercial 商业型 | 可信 40% + 记忆 40% | 产品展示、广告 |

筛选结果：≥ 8.5 → MUST KEEP，7.0-8.5 → USABLE，< 7.0 → DISCARD。

---

## 安装（通用前置步骤）

### 系统依赖

```bash
# macOS (Apple Silicon / Intel 均可)
brew install ffmpeg

# 验证
ffmpeg -version
```

### 克隆仓库 + 安装 Python 依赖

```bash
git clone https://github.com/ALBEDO-TABAI/video-expert-analyzer.git
cd video-expert-analyzer

# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 检查环境
python3 scripts/check_environment.py
```

`requirements.txt` 核心依赖：

```
yt-dlp          # 视频下载
scenedetect[opencv]  # 场景检测
funasr          # 中文语音识别（字幕提取降级方案）
modelscope
torch, torchaudio
openai          # API 模式评分客户端
rapidocr-onnxruntime  # 烧录字幕 OCR
requests
```

### 首次配置输出目录

```bash
python3 scripts/pipeline_enhanced.py --setup
# 按提示输入你希望存放分析结果的目录，如 ~/Downloads/video-analysis
```

---

## 路径 A：云端 API 模式（快速上手）

适合网络好、有 API Key、不介意消耗云端 token 的场景。

```bash
# Gemini（推荐，免费额度较大）
export VIDEO_ANALYZER_API_KEY="your-gemini-key"
export VIDEO_ANALYZER_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
export VIDEO_ANALYZER_MODEL="gemini-2.0-flash"

# 或 Kimi（中文场景优选）
export VIDEO_ANALYZER_API_KEY="your-kimi-key"
export VIDEO_ANALYZER_BASE_URL="https://api.moonshot.cn/v1"
export VIDEO_ANALYZER_MODEL="moonshot-v1-vision-8k"
```

分析一条视频：

```bash
# 步骤 1：处理视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# 步骤 2：进入输出目录运行 AI 评分
cd ~/Downloads/video-analysis/BV1xxxxx
python3 /path/to/video-expert-analyzer/scripts/ai_analyzer.py scene_scores.json --mode api
```

---

## 路径 B：Mac 本地 MLX 模型（完整指南）

**为什么要用本地 MLX？**

- 零 API 费用：评分一个 30 分钟视频可能切出 50-100 个场景，云端视觉模型成本不低
- 数据离机不出：竞品分析、商业机密视频，本地运行放心
- 离线可用：没网或网络慢的场合完全不受影响
- M 系列 Mac 的 Neural Engine 非常适合跑 4B-12B 的视觉模型

**核心原理**：Video Expert Analyzer 的 API 模式通过 `VIDEO_ANALYZER_BASE_URL` 指向任意 OpenAI 兼容端点。我们只需要在本机起一个能接收图片输入的视觉模型服务，把这个变量指向它就够了。

---

### 方案 B-1：oMLX（推荐，macOS 原生体验）

oMLX（`jundot/omlx`）是一个为 Apple Silicon 深度优化的推理服务，16,000+ star，支持 VLM，菜单栏管理，SSD 分页 KV 缓存，即使上下文切换缓存仍然有效。

#### 安装 oMLX

**方式 1：DMG（最省事）**

从 [Releases](https://github.com/jundot/omlx/releases) 下载最新 `.dmg`，拖入 Applications，完成。内置自动更新。

**方式 2：Homebrew**

```bash
brew tap jundot/omlx https://github.com/jundot/omlx
brew install omlx

# 后台运行
omlx start
```

要求：macOS 15.0+ (Sequoia)，Apple Silicon (M1/M2/M3/M4)，Python 3.10+

#### 下载一个视觉语言模型（VLM）

oMLX 支持自动发现 `~/.omlx/models/` 目录下的 VLM。推荐选项：

| 模型 | 显存需求 | 推荐程度 | 说明 |
|------|---------|---------|------|
| **Qwen2.5-VL-7B** | ~8GB | ⭐⭐⭐ 强推 | 视觉能力强，中文优秀 |
| **Gemma-4-12B** | ~14GB | ⭐⭐⭐ 强推 | 视觉理解全面，M3 Max/M4 Pro 以上 |
| **LLaVA-v1.6-7B** | ~8GB | ⭐⭐ 可用 | 经典视觉模型，稳定 |
| **Qwen2.5-VL-3B** | ~4GB | ⭐⭐ 可用 | 低显存 Mac 首选 |

在 oMLX 管理界面（`http://localhost:8888/admin`）或 CLI 搜索并下载：

```bash
# 通过 CLI 下载（在 oMLX 中搜索并拉取 mlx-community 版本）
omlx model pull mlx-community/Qwen2.5-VL-7B-Instruct-4bit
```

或者直接在 Admin Dashboard → Models → Search 里搜 `Qwen2.5-VL` 并点击下载。

#### 确认 VLM 已启动

oMLX 启动后，API 端点默认在：

```
OpenAI 兼容 API: http://localhost:8888/v1
```

测试 VLM 是否工作（需要先在 Admin → Models 里激活模型）：

```bash
curl http://localhost:8888/v1/models | python3 -m json.tool
# 应能看到你下载的 VLM 出现在列表里
```

#### 配置 Video Expert Analyzer 使用 oMLX

```bash
export VIDEO_ANALYZER_API_KEY="ollama"  # oMLX 不验证 key，随便填
export VIDEO_ANALYZER_BASE_URL="http://localhost:8888/v1"
export VIDEO_ANALYZER_MODEL="Qwen2.5-VL-7B-Instruct-4bit"  # 填你下载的模型名
```

或者在输出目录创建 `.env` 文件：

```bash
# ~/Downloads/video-analysis/.env
VIDEO_ANALYZER_API_KEY=local
VIDEO_ANALYZER_BASE_URL=http://localhost:8888/v1
VIDEO_ANALYZER_MODEL=Qwen2.5-VL-7B-Instruct-4bit
```

---

### 方案 B-2：Rapid-MLX（开发者友好，极速推理）

Rapid-MLX（`raullenchai/Rapid-MLX`）宣称比 Ollama 快 4.2 倍，0.08s 缓存首 token 延迟，适合需要高吞吐量场景。

#### 安装 Rapid-MLX（含视觉支持）

```bash
# 安装含视觉依赖的版本（多约 322MB：mlx-vlm + opencv + torch）
pip install 'rapid-mlx[vision]'
```

#### 启动视觉模型服务

```bash
# 使用 Qwen3-VL-4B（最轻量的多模态模型之一）
rapid-mlx serve qwen3-vl-4b --mllm --port 8000

# 或使用 Gemma 4（视觉能力更强）
rapid-mlx serve gemma-4-12b --mllm --port 8000
```

服务起来后端点：`http://localhost:8000/v1`

推荐视觉模型：

| 模型 | 命令关键词 | 显存 | 特点 |
|------|----------|------|------|
| Qwen3-VL-4B | `qwen3-vl-4b` | ~5GB | 最轻量，16GB Mac 可跑 |
| Gemma-4-12B | `gemma-4-12b` | ~14GB | 视觉全面，需 M3 Max/M4 |
| Qwen2.5-VL-7B | `qwen2.5-vl-7b` | ~9GB | 性价比最高 |

#### 配置 Video Expert Analyzer 使用 Rapid-MLX

```bash
export VIDEO_ANALYZER_API_KEY="rapid-mlx"
export VIDEO_ANALYZER_BASE_URL="http://localhost:8000/v1"
export VIDEO_ANALYZER_MODEL="qwen3-vl-4b"  # 填你启动的模型
```

---

### 本地模型选型建议

| Mac 配置 | 推荐模型 | 服务 | 预期速度 |
|---------|---------|------|---------|
| M1/M2 16GB | Qwen2.5-VL-3B 或 Qwen3-VL-4B | Rapid-MLX | ~3-5 tok/s |
| M2 Pro/M3 24GB | Qwen2.5-VL-7B | oMLX 或 Rapid-MLX | ~8-15 tok/s |
| M3 Max/M4 Pro 48GB | Gemma-4-12B 或 Qwen2.5-VL-7B | oMLX | ~20-40 tok/s |
| M4 Max/Ultra 64GB+ | Gemma-4-26B | oMLX | ~30-60 tok/s |

---

## 完整本地运行流程（端到端）

以下是一次完整的分析过程，使用 oMLX + Qwen2.5-VL-7B，以一条 B 站视频为例：

### 步骤 0：启动本地视觉模型服务

```bash
# oMLX 已在菜单栏运行，或：
omlx start
# 在 Admin 界面激活 Qwen2.5-VL-7B-Instruct-4bit 模型

# 设置环境变量
export VIDEO_ANALYZER_API_KEY="local"
export VIDEO_ANALYZER_BASE_URL="http://localhost:8888/v1"
export VIDEO_ANALYZER_MODEL="Qwen2.5-VL-7B-Instruct-4bit"
```

### 步骤 1：处理视频（Pipeline）

```bash
cd video-expert-analyzer
source .venv/bin/activate

# 分析 B 站视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# 分析抖音视频（短链更稳定）
python3 scripts/pipeline_enhanced.py "https://v.douyin.com/xxxxx"

# 调整场景切割灵敏度（默认 27，值越小切越细）
python3 scripts/pipeline_enhanced.py URL --scene-threshold 20
```

完成后查看输出：

```bash
ls ~/Downloads/video-analysis/BV1xxxxx/
# 应看到：video.mp4, video.srt, scenes/, frames/, scene_scores.json
```

### 步骤 2：AI 视觉评分

```bash
cd ~/Downloads/video-analysis/BV1xxxxx

# 运行 API 模式（指向本地 oMLX）
python3 /path/to/video-expert-analyzer/scripts/ai_analyzer.py \
  scene_scores.json --mode api
```

如果场景超过 10 个，工具会自动分批处理（5-10 个/批），每批完成后报告进度，最后做 100% 覆盖率校验。

### 步骤 3：查看结果

```bash
# 完整分析报告
open BV1xxxxx_complete_analysis.md

# 精选镜头目录
open scenes/best_shots/

# 原始评分数据（JSON）
cat scene_scores.json | python3 -m json.tool | head -50
```

输出结构：

```
BV1xxxxx/
├── BV1xxxxx.mp4              ← 完整视频
├── BV1xxxxx.srt              ← 字幕
├── scene_scores.json         ← AI 评分原始数据 ⭐
├── BV1xxxxx_complete_analysis.md  ← 完整报告 ⭐
├── scenes/
│   ├── BV1xxxxx-Scene-001.mp4
│   ├── ...
│   └── best_shots/           ← 精选镜头（自动复制）⭐
│       ├── 01_MUST_KEEP_Scene-003.mp4
│       ├── 02_MUST_KEEP_Scene-007.mp4
│       └── README.md
└── frames/
    ├── BV1xxxxx-Scene-001.jpg
    └── ...
```

---

## 实际效果参考

官方 CHANGELOG 里有实测数据可参考：

- **GPT-5.4（云端）**：127 个镜头连续分析，预热后 **11 分 48 秒** 完成
- **Kimi 2.5（云端）**：>30 个镜头时出现偷懒行为（推测服务端限制）
- **本地 Qwen2.5-VL-7B（M3 Max）**：约 25-40 tok/s，50 个镜头预计 15-25 分钟

字幕提取速度参考：
- B站字幕 API：**秒级**
- FunASR（10分钟音频）：**约 22 秒**（CPU/GPU 本地推理）

---

## 常见问题

### FunASR 首次下载很慢

FunASR 需要下载约 2-3GB 的 Paraformer 语音模型。如果下载缓慢：

```bash
# 设置 ModelScope 缓存目录
export MODELSCOPE_CACHE=~/.cache/modelscope

# 或优先使用 B站 API 字幕（B站视频一般都有），跳过 FunASR
# Pipeline 会自动降级，无需手动干预
```

### 本地 VLM 返回不含图片的回复

说明模型没有收到图片或 API 不支持 `image_url`。检查：

```bash
# 测试本地 API 是否支持图片输入
curl http://localhost:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "你的模型名",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "describe this image"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/..."}}
      ]
    }]
  }'
```

如果报错，说明模型未启用多模态能力，需要：
- oMLX：确认下载的是 VLM 版本（名字里有 VL/Vision/Instruct-VL）
- Rapid-MLX：确认用了 `--mllm` 参数启动

### 抖音下载失败

```bash
# 优先使用分享短链（从抖音 App 复制）
python3 scripts/pipeline_enhanced.py "https://v.douyin.com/xxxxx"

# 不要走浏览器 Cookie 路线，脚本有专用下载器
# 不要在 WSL 里尝试，可能读不到 cookie
```

### 场景切割太碎/太少

```bash
# 切割更少（默认 27，调高）
python3 scripts/pipeline_enhanced.py URL --scene-threshold 35

# 切割更多（调低）
python3 scripts/pipeline_enhanced.py URL --scene-threshold 15
```

### 精选阈值调整

```bash
# 更严格（只要最顶尖的）
python3 scripts/ai_analyzer.py scene_scores.json --mode api 9.0

# 更宽松（多保留一些素材）
python3 scripts/ai_analyzer.py scene_scores.json --mode api 6.5
```

---

## 我的判断

**值得用，尤其是做内容或视频的开发者和创作者。**

工具有几个设计决策做得很对：

1. **Pipeline 和评分彻底解耦**：下载和切割本地完成，视觉评分可以插拔任意模型，对 Mac 本地 MLX 方案非常友好。
2. **分批 + 覆盖率校验**：v2.2.0 强制要求 100% 覆盖率，防止 AI 偷懒抽样。这是工程严谨性的体现。
3. **Walter Murch 框架有说服力**：不是随便定义的打分维度，背后有认知科学和影视理论支撑（Von Restorff 效应、Visual Saliency 等）。
4. **四级字幕降级很实用**：B站 API → 内嵌字幕 → OCR → 语音识别，几乎覆盖所有情况。

**主要局限**：

- 视觉模型的分析质量直接决定评分准确性——本地 7B 模型和 Gemini 3.0 Pro 之间确实有差距
- FunASR 模型比较大，网络不好首次安装比较痛苦
- 抖音下载依赖逆向解析接口，稳定性取决于抖音是否改接口

---

**GitHub**: ALBEDO-TABAI/video-expert-analyzer  
**oMLX**: jundot/omlx（Mac 本地推理，菜单栏管理）  
**Rapid-MLX**: raullenchai/Rapid-MLX（4.2x 速度，开发者友好）

<!--EN-->

## Video Expert Analyzer Complete Guide: Walter Murch's Six Rules + Mac MLX Local Model Full Walkthrough

If you make videos, edit videos, or analyze competitor content, you've probably wondered: **is there an AI tool that can watch scenes, score them, and pull out the best clips automatically?**

Yes. And it's fairly complete.

This article deep-dives into `ALBEDO-TABAI/Video-expert-analyzer` (v2.2.0, MIT license) with a focus on the full path for running **local MLX vision models on Mac Apple Silicon** — no cloud token cost, offline capable, data stays on your machine.

---

## What the Tool Does

[Video Expert Analyzer](https://github.com/ALBEDO-TABAI/video-expert-analyzer) applies **Walter Murch's Six Rules of Editing** to AI-powered video analysis.

**Walter Murch's priority order:**

> Emotion > Story > Rhythm > Eye-trace > 2D Plane > 3D Space

A shot with genuine emotion but slight camera shake beats a technically perfect but emotionally empty frame.

The tool translates this into a five-dimension scoring system, uses multimodal AI to evaluate each extracted scene frame, and outputs ranked clips automatically.

**Supported platforms:** Bilibili, YouTube, Douyin (no login required), Xiaohongshu

**Supported AI backends:** Gemini 3.0, Kimi 2.5, GPT-4o, **and local MLX vision models via OpenAI-compatible API** (the focus of this guide)

---

## How It Works

Two completely decoupled phases:

```
Phase 1: Data Pipeline (pipeline_enhanced.py) — no AI model needed
─────────────────────────────────────────────────────────────────
📥 Download video         → video.mp4
🎵 Extract audio          → video.m4a
🎞️  Scene detection       → scenes/*.mp4 (accurate cut-point splitting)
🎤 Smart subtitle extract → video.srt
    Bilibili API → Embedded → RapidOCR → FunASR (4-tier fallback)
🖼️  Extract preview frames → frames/*.jpg
📊 Generate scoring template → scene_scores.json

Phase 2: AI Vision Scoring (ai_analyzer.py) — needs multimodal model
─────────────────────────────────────────────────────────────────
🤖 Multimodal model analyzes each frame
🧮 5D scoring × dynamic weights = weighted total
⭐ High-score clips copied to best_shots/
📄 Full analysis report (*_complete_analysis.md)
```

Phase 1 runs entirely on-device (ffmpeg + PySceneDetect). Phase 2 is where a **vision-capable model** is needed — this is where local MLX fits in.

---

## Installation (Universal Prerequisites)

```bash
# macOS system dependency
brew install ffmpeg

# Clone repo and install
git clone https://github.com/ALBEDO-TABAI/video-expert-analyzer.git
cd video-expert-analyzer

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Check environment
python3 scripts/check_environment.py

# First-time output directory setup
python3 scripts/pipeline_enhanced.py --setup
```

---

## Path A: Cloud API Mode (Quick Start)

```bash
# Gemini (recommended, generous free tier)
export VIDEO_ANALYZER_API_KEY="your-gemini-key"
export VIDEO_ANALYZER_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
export VIDEO_ANALYZER_MODEL="gemini-2.0-flash"

# Analyze a video
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx
cd ~/Downloads/video-analysis/BV1xxxxx
python3 /path/to/scripts/ai_analyzer.py scene_scores.json --mode api
```

---

## Path B: Mac Local MLX Model (Full Guide)

**Why local MLX?**
- Zero API cost: scoring 50-100 scenes from a 30-minute video adds up fast
- Data never leaves your machine: competitor videos, commercial content
- Offline capable: no network dependency
- M-series Neural Engine handles 4B-12B vision models efficiently

**Core principle:** `VIDEO_ANALYZER_BASE_URL` can point to any OpenAI-compatible endpoint. Run a local vision model server, point the variable at it, done.

---

### Option B-1: oMLX (Recommended for macOS Users)

oMLX (`jundot/omlx`, 16,000+ stars) is a native macOS inference server with paged SSD KV caching, menu bar management, and VLM support since v0.2.0.

**Install:**

```bash
# Option 1: DMG from Releases (drag to Applications)
# Option 2: Homebrew
brew tap jundot/omlx https://github.com/jundot/omlx
brew install omlx
omlx start
```

Requires: macOS 15.0+ (Sequoia), Apple Silicon (M1+), Python 3.10+

**Download a vision model** (in Admin Dashboard → Models, or via CLI):

```bash
omlx model pull mlx-community/Qwen2.5-VL-7B-Instruct-4bit
```

| Model | VRAM | Recommendation |
|-------|------|----------------|
| Qwen2.5-VL-3B | ~4GB | 16GB Mac baseline |
| Qwen2.5-VL-7B | ~9GB | Best value, M2 Pro+ |
| Gemma-4-12B | ~14GB | Strong vision, M3 Max+ |

**Configure Video Expert Analyzer:**

```bash
export VIDEO_ANALYZER_API_KEY="local"
export VIDEO_ANALYZER_BASE_URL="http://localhost:8888/v1"
export VIDEO_ANALYZER_MODEL="Qwen2.5-VL-7B-Instruct-4bit"
```

---

### Option B-2: Rapid-MLX (Developer-Friendly, High Speed)

Rapid-MLX claims 4.2x faster than Ollama, 0.08s cached TTFT.

```bash
# Install with vision support
pip install 'rapid-mlx[vision]'

# Start a vision model server
rapid-mlx serve qwen3-vl-4b --mllm --port 8000
# or
rapid-mlx serve gemma-4-12b --mllm --port 8000
```

Endpoint: `http://localhost:8000/v1`

```bash
export VIDEO_ANALYZER_API_KEY="rapid-mlx"
export VIDEO_ANALYZER_BASE_URL="http://localhost:8000/v1"
export VIDEO_ANALYZER_MODEL="qwen3-vl-4b"
```

---

### Local Model Selection Guide

| Mac Config | Recommended Model | Server | Expected Speed |
|-----------|------------------|--------|----------------|
| M1/M2 16GB | Qwen3-VL-4B | Rapid-MLX | ~3-5 tok/s |
| M2 Pro/M3 24GB | Qwen2.5-VL-7B | oMLX or Rapid-MLX | ~8-15 tok/s |
| M3 Max/M4 Pro 48GB | Gemma-4-12B | oMLX | ~20-40 tok/s |
| M4 Max/Ultra 64GB+ | Gemma-4-26B | oMLX | ~30-60 tok/s |

---

## Full End-to-End Local Run

```bash
# 0. Start local vision model
omlx start  # (oMLX already running in menu bar)
export VIDEO_ANALYZER_API_KEY="local"
export VIDEO_ANALYZER_BASE_URL="http://localhost:8888/v1"
export VIDEO_ANALYZER_MODEL="Qwen2.5-VL-7B-Instruct-4bit"

# 1. Process video
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# 2. Run AI scoring
cd ~/Downloads/video-analysis/BV1xxxxx
python3 /path/to/scripts/ai_analyzer.py scene_scores.json --mode api

# 3. Review results
open BV1xxxxx_complete_analysis.md
open scenes/best_shots/
```

For 10+ scenes, the tool automatically batches (5-10 per batch), reports progress after each batch, and does a 100% coverage check at the end.

---

## Key Troubleshooting

**Local VLM not receiving images:** Test the endpoint directly with a base64 image. If it fails, the model may not have vision enabled — check that oMLX is running a VLM (not a text-only model), or that Rapid-MLX was started with `--mllm`.

**FunASR first-run is slow:** It downloads a ~2-3GB Paraformer model. Use Bilibili API subtitles first (instant, automatic fallback) — FunASR only kicks in when no subtitles are found.

**Douyin download fails:** Use the share short-link from the Douyin app (`https://v.douyin.com/...`). Do not attempt browser cookie extraction — the tool has a dedicated downloader that works without login for public videos.

**Scene detection too coarse/fine:** Adjust `--scene-threshold` (default 27). Higher = fewer scenes, lower = more scenes.

---

**GitHub:** ALBEDO-TABAI/video-expert-analyzer  
**oMLX:** jundot/omlx — Mac-native inference, menu bar managed  
**Rapid-MLX:** raullenchai/Rapid-MLX — 4.2x speed, developer-first
