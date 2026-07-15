---
title: "一句话生成完整短视频：Pixelle-Video 开源引擎上手指南"
titleEn: "One Prompt, Full Short Video: Getting Started with Pixelle-Video Open-Source Engine"
description: "Pixelle-Video 是一款 AI 全自动短视频引擎（25k+ GitHub ⭐），输入一个主题，自动完成文案撰写、AI 配图生成、语音合成（支持声音克隆）、背景音乐、视频合成全流程。本文从环境搭建到第一条视频导出，完整走一遍。"
descriptionEn: "Pixelle-Video is a fully automated AI short video engine (25k+ GitHub stars). Give it a topic, and it writes the script, generates AI images, synthesizes voice (with voice cloning), adds background music, and renders the final video — all automatically. This guide covers setup to your first exported video."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Tech-Experiment"
tags: ["AI工具", "短视频", "内容创作", "开源", "本地部署"]
heroImage: "../../assets/images/pixelle-video-ai-short-video-generator-banner.jpg"
---

> GitHub：[AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) · ⭐ 25,000+ · 🍴 3,600+ · Apache-2.0  
> 文档：[aidc-ai.github.io/Pixelle-Video/zh](https://aidc-ai.github.io/Pixelle-Video/zh)

---

## 它做什么

输入一个主题关键词，Pixelle-Video 自动完成：

1. **文案撰写** — LLM 根据主题生成分镜解说词
2. **AI 配图** — 每句旁白自动生成一张对应配图（支持 FLUX、Qwen、GPT Image 2、Seedream 等）
3. **语音合成** — Edge-TTS / Index-TTS 合成人声解说，支持上传参考音频做声音克隆
4. **背景音乐** — 内置 BGM 库，可自定义导入
5. **视频合成** — 图文音乐一键合成 MP4，支持竖屏（1080×1920）、横屏、方形多种尺寸

整个过程不需要任何视频剪辑经验。你唯一需要决定的是「这条视频讲什么」。

---

## 生成的视频长什么样

仓库里有十几种模板，风格覆盖面很广：

- **极简墨线**（image_default）：白底水墨插图 + 黑体标题，适合人文纪实、知识科普
- **霓虹赛博**（image_neon）：深色背景 + 荧光边框，适合科技话题
- **现代紫调**（image_modern）：渐变紫色 + 卡片布局，适合个人成长、情感类
- **疗愈风**（image_healing）：柔和色调插图，适合生活方式内容
- **电影横屏**（video_default）：宽画幅 + 动态视频背景，适合故事叙述类

已验证可跑通的主题覆盖：旅行、历史（资治通鉴）、科学（外星文明）、小说解说（斗破苍穹）、养生、副业、个人成长类——基本上「能写成文章的话题」都可以做成视频。

---

## 架构和模型支持

Pixelle-Video 采用模块化设计，每个环节可独立替换：

```
输入主题
   ↓
LLM 生成分镜文案（GPT / 通义千问 / DeepSeek / Ollama）
   ↓
图像生成（ComfyUI 工作流 / 直连 API）
   ├── 本地：FLUX、SD 系列（ComfyUI selfhost）
   ├── 云端工作流：RunningHub
   └── 直连 API：DashScope / GPT Image 2 / Seedream / Kling
   ↓
TTS 语音合成
   ├── Edge-TTS（免费，无需部署）
   └── Index-TTS（支持声音克隆）
   ↓
视频合成（FFmpeg + HTML 模板渲染）
   ↓
输出 MP4
```

没有本地 GPU 的用户选「LLM + 直连 API 图像模型 + Edge-TTS」这条路，全程跑在云端，本地只需要有 Python 和 ffmpeg。

---

## 安装

### Windows 整合包（推荐 Windows 用户）

直接从 [GitHub Releases](https://github.com/AIDC-AI/Pixelle-Video/releases/latest) 下载最新整合包，解压后双击 `start.bat`，浏览器自动打开 `http://localhost:8501`。不需要安装 Python、uv 或 ffmpeg。

### macOS / Linux 源码安装

**第一步：安装 uv 和 ffmpeg**

```bash
# uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# ffmpeg
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Ubuntu/Debian
```

**第二步：克隆并启动**

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video
uv run streamlit run web/app.py
```

首次运行 `uv` 会自动安装所有 Python 依赖，不需要手动 `pip install`。浏览器自动打开 `http://localhost:8501`。

---

## 第一条视频：从主题到 MP4 全流程

### 第一步：配置 LLM

打开 Web 界面，点击展开「⚙️ 系统配置」→「LLM 配置」。

下拉菜单选择模型预设（通义千问、GPT-4o、DeepSeek 都有），选完后自动填入 base_url 和 model 名称，只需要粘贴你的 API Key。

**最省钱的路线**：DeepSeek（文案生成）+ DashScope Wan（图像生成）+ Edge-TTS（语音），全程费用一条视频通常在 0.1–0.5 元人民币区间。

### 第二步：配置图像生成

有两种路线，选其中一种：

**路线 A：直连 API（无需 GPU，推荐）**

在「API 媒体模型配置」里选择供应商，填入 API Key：

| 供应商 | 服务 | 备注 |
|--------|------|------|
| DashScope | Wan 图像生成 | 阿里云通义，国内访问稳定 |
| OpenAI | GPT Image 2 | 图像质量高，费用略贵 |
| Kling / 可灵 | 图像/视频生成 | 国内，支持视频片段 |
| Seedream | 字节系图像 | 高分辨率 |

配置完成后，在视觉设置里的「图像生成工作流」下拉菜单选择 `api/dashscope`（或对应供应商）。

**路线 B：本地 ComfyUI（有 GPU）**

如果本地已经跑了 ComfyUI，在「ComfyUI URL」里填入地址（默认 `http://127.0.0.1:8188`），点「测试连接」。工作流下拉菜单会自动列出 `workflows/` 文件夹里的所有工作流。

### 第三步：配置语音

在「🎤 语音设置」里选择 TTS 工作流：

- **Edge-TTS**：零配置，免费，多种中文音色可选。适合快速出片。
- **Index-TTS**（需 ComfyUI + 模型）：支持声音克隆。上传 5–30 秒的参考音频，合成出来的旁白和参考音频音色一致。

没有特殊需求就选 Edge-TTS，先跑通再说。

### 第四步：选模板

在「视觉设置」→「视频模板」下拉菜单选择，按尺寸分组：

- 竖屏（1080×1920）：适合抖音、小红书、Instagram Reels
- 横屏（1920×1080）：适合 B 站、YouTube
- 方形（1080×1080）：适合微信视频号

模板命名规律：
- `static_*` — 纯文字，不需要 AI 生成配图
- `image_*` — 每帧用 AI 生成的图片作背景
- `video_*` — 每帧用 AI 生成的视频片段作背景（费用更高）

点「预览模板」可以看渲染效果，选定后继续。

### 第五步：输入主题，生成视频

在左侧「📝 内容输入」里：

- **生成模式**选「AI 生成内容」
- 在输入框里填主题，例如：

  ```
  为什么我们还没有找到外星文明？
  ```

  或者更具体一点：

  ```
  费米悖论：宇宙如此广阔，却为何一片寂静
  ```

- BGM 选「内置音乐」或「无 BGM」

点右侧「🎬 生成视频」。界面实时显示进度：

```
生成文案 → 分镜 1/5 生成插图 → 分镜 2/5 生成插图 → ... → 合成语音 → 合成视频
```

一条 60–90 秒的竖屏视频，Edge-TTS + 直连 API 图像，通常 3–8 分钟出片（取决于图像 API 响应速度）。

生成完成后直接在界面预览，右键视频可以下载 MP4。

---

## 几个实用技巧

**用固定文案跳过 AI 创作**

已经有现成稿子的话，「生成模式」切换到「固定文案内容」，直接粘贴文本。AI 只负责配图和配音，不改你的稿子。

**用自己的声音**

选 Index-TTS 工作流，上传 5–30 秒干净的参考录音（安静环境、无背景音乐）。生成的视频旁白会模仿这个音色。适合想建立个人声音 IP 的创作者。

**调整图像风格**

在「提示词前缀（Prompt Prefix）」里填英文风格描述，所有分镜配图都会按这个风格生成。比如：

```
Minimalist black-and-white ink illustration, brush strokes, Japanese aesthetic
```

或：

```
Cyberpunk neon cityscape, dark background, glowing particles, digital art
```

点「预览风格」先看单张效果再批量生成。

**自定义模板**

如果懂 HTML，可以在 `templates/` 文件夹新建 `.html` 模板，WebUI 会自动识别。模板里可以用变量 `{{content}}`、`{{image}}`、`{{author}}` 等引用生成内容，定制空间很大。

---

## 扩展功能

除了基础的「主题 → 视频」流水线，Pixelle-Video 还有几个扩展模块：

**数字人口播**：上传数字人模型，生成带虚拟形象出镜的视频，支持多语言（包括韩语等）。

**图生视频**：上传一张图片，AI 生成这张图片「动起来」的视频片段，再合并进流水线。

**动作迁移**：上传参考视频（比如一段舞蹈动作），把这个动作迁移到指定角色图像上。

**自定义素材**：上传自己的照片或视频，AI 分析内容自动生成脚本，配图部分直接用你的素材。

---

## 费用估算

| 配置 | 单条视频成本 |
|------|-------------|
| DeepSeek + DashScope Wan + Edge-TTS | ~0.1–0.3 元 |
| GPT-4o + GPT Image 2 + Edge-TTS | ~0.5–2 元 |
| 本地 LLM + 本地 ComfyUI + Edge-TTS | 接近零成本（电费） |

图像 API 是主要费用，通常每张图 0.02–0.1 元区间，一条 5 分镜视频大约 5 张图。

---

## 注意事项

- Pixelle-Video 本身是 Apache-2.0 开源项目，可商用，但调用的第三方 API（DashScope、OpenAI、Kling 等）各有自己的使用条款
- 声音克隆功能仅用于克隆你自己的声音或有明确授权的声音
- 「数字人」等高级功能需要配合 ComfyUI 工作流，有一定配置门槛

---

GitHub：[github.com/AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video)  
Windows 整合包：[最新 Release](https://github.com/AIDC-AI/Pixelle-Video/releases/latest)  
文档：[aidc-ai.github.io/Pixelle-Video/zh](https://aidc-ai.github.io/Pixelle-Video/zh)

© 2026 Author: Mycelium Protocol

<!--EN-->

## One Prompt, Full Short Video: Getting Started with Pixelle-Video

> GitHub: [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) · ⭐ 25,000+ · Apache-2.0

---

### What It Does

Give Pixelle-Video a topic, and it produces a complete short video automatically:

1. **Script writing** — LLM generates storyboard narration from the topic
2. **AI image generation** — one illustration per narration segment (FLUX, Qwen, GPT Image 2, Seedream, etc.)
3. **Voice synthesis** — Edge-TTS or Index-TTS with voice cloning support
4. **Background music** — built-in BGM library, custom upload supported
5. **Video rendering** — combines everything into MP4, supports portrait (1080×1920), landscape, and square

No video editing experience required.

---

### Setup

**Windows**: Download the all-in-one package from [GitHub Releases](https://github.com/AIDC-AI/Pixelle-Video/releases/latest), extract, run `start.bat`. No Python or ffmpeg installation needed.

**macOS / Linux:**

```bash
# Install uv and ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
brew install ffmpeg   # or: sudo apt install ffmpeg

# Clone and run
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video
uv run streamlit run web/app.py
```

Browser opens at `http://localhost:8501` automatically.

---

### First Video: Step by Step

**Step 1 — Configure LLM**: In Settings → LLM, pick a preset (Qwen, GPT-4o, DeepSeek) and add your API key.

**Step 2 — Configure image generation**: Two paths:
- **No GPU**: In "API Media Model Config", add a key for DashScope, Seedream, or GPT Image 2. Select `api/dashscope` (or equivalent) in the image workflow dropdown.
- **Local GPU**: Run ComfyUI locally, point Pixelle-Video to `http://127.0.0.1:8188`.

**Step 3 — Voice**: Select Edge-TTS for zero-setup. For voice cloning, select Index-TTS (requires ComfyUI) and upload a 5–30s clean reference recording.

**Step 4 — Template**: Choose from portrait/landscape/square templates. Naming convention: `static_*` = text only, `image_*` = AI-generated image backgrounds, `video_*` = AI-generated video backgrounds.

**Step 5 — Generate**: Enter a topic (e.g. "Why haven't we found alien civilizations?"), click 🎬 Generate Video. Progress displays in real time. Typical time for a 60–90s portrait video with API images: 3–8 minutes.

---

### Cost Estimate

| Configuration | Cost per video |
|---|---|
| DeepSeek + DashScope Wan + Edge-TTS | ~¥0.1–0.3 |
| GPT-4o + GPT Image 2 + Edge-TTS | ~¥0.5–2 |
| Local LLM + local ComfyUI + Edge-TTS | Near zero |

Image API calls are the main cost — typically ¥0.02–0.1 per image, ~5 images per 5-segment video.

---

### Useful Features

- **Fixed script mode**: paste your own narration, skip the AI writing step
- **Voice cloning**: upload a 5–30s reference clip, Index-TTS matches the timbre across all segments
- **Style prompt prefix**: add an English style description (e.g. "Minimalist ink illustration, Japanese aesthetic") applied to all generated images
- **Custom templates**: add `.html` files to `templates/` with `{{content}}`, `{{image}}` variables — WebUI auto-discovers them
- **Custom media**: upload your own photos/videos; AI generates a script from them instead of generating images from scratch

---

GitHub: [github.com/AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video)  
Docs: [aidc-ai.github.io/Pixelle-Video/zh](https://aidc-ai.github.io/Pixelle-Video/zh)

© 2026 Author: Mycelium Protocol
