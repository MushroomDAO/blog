---
title: "输入一句话生成完整短视频：Pixelle-Video 完整使用指南"
titleEn: "Turn One Sentence Into a Complete Short Video: Pixelle-Video Complete Guide"
description: "Pixelle-Video（24456★，AIDC-AI 开源）是一款 AI 全自动短视频引擎，输入主题关键词即可自动生成文案、AI 配图/视频、语音解说、背景音乐和成品视频。Windows 一键包开箱即用，支持 ComfyUI 本地部署或直连 Kling/Seedance/通义万象 API，也支持声音克隆和数字人口播。本文面向零剪辑基础的创作者：三条路径（新手包 / 纯 API / 本地全栈）逐步详解，覆盖硬件要求、依赖安装和完整操作流程。"
descriptionEn: "Pixelle-Video (24,456★, AIDC-AI) is a fully automated short video engine — input a topic, get a complete video with AI script, illustrations, voiceover, and BGM. Windows one-click package needs zero setup. Supports local ComfyUI, direct API calls to Kling/Seedance/Wan, and voice cloning. This guide covers all three deployment paths (beginner package / API-only / full local stack), hardware requirements, software dependencies, and complete workflow."
pubDate: "2026-07-08"
updatedDate: "2026-07-08"
category: "Tech-Experiment"
tags: ["AI视频", "Pixelle-Video", "短视频生成", "ComfyUI", "文字转视频", "TTS", "AIGC", "自动化创作"]
heroImage: "../../assets/images/pixelle-video-ai-short-video-engine-guide-banner.jpg"
---

> **仓库**: [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) · 24456★ · Apache-2.0 · Python  
> **官方文档**: [aidc-ai.github.io/Pixelle-Video](https://aidc-ai.github.io/Pixelle-Video/zh)  
> **视频教程**: [Bilibili 教程](https://www.bilibili.com/video/BV1WzyGBnEVp/)

---

## 它能做什么

输入「为什么要养成阅读习惯」，几分钟后你拿到一个：

- 有 AI 自动写好的解说词
- 每段话都配了风格统一的 AI 生成插图
- 用 TTS 或克隆你自己声音配音
- 有背景音乐
- 已经剪辑合成好的完整视频

全程你不需要打开 Premiere、剪映，不需要写一个字的脚本，不需要录音。

这就是 Pixelle-Video 做的事：**把"一句话 → 完整视频"这个流程完全自动化**。

它来自 AIDC-AI（阿里达摩院 AI 研究团队），24456 颗星，持续更新。

---

## 整个生成流程

```
① 你输入主题（或自己的文案）
        ↓
② LLM 生成视频脚本（分镜文案）
        ↓
③ 逐镜生成配图或视频片段（ComfyUI / API）
        ↓
④ TTS 合成语音（或克隆你的声音）
        ↓
⑤ ffmpeg 合成：配图 + 语音 + BGM + 字幕 → 成品视频
        ↓
⑥ 输出到 output/ 文件夹，浏览器直接预览
```

每个环节都是独立模块，可以按需替换：LLM 换成 DeepSeek 或 Ollama，配图换成 Kling 或本地 ComfyUI，TTS 换成 Index-TTS 做声音克隆——不换也完全能用。

---

## 三条部署路径：按你的情况选

### 路径一：Windows 一键整合包（★ 零基础推荐）

**适合谁**：Windows 用户，没有编程经验，只想快速出视频。

**优点**：不需要安装 Python、uv、ffmpeg，所有依赖已打包，双击开始。  
**前提**：Windows 10/11，至少一个 LLM API key。

```
1. 下载最新整合包：
   https://github.com/AIDC-AI/Pixelle-Video/releases/latest

2. 解压到任意目录（建议英文路径，避免中文路径问题）

3. 双击 start.bat

4. 浏览器自动打开 http://localhost:8501

5. 在「⚙️ 系统配置」填入 LLM API Key，点保存

6. 输入主题，生成视频
```

**费用说明**：整合包本身免费。LLM 费用取决于你用什么模型：
- **通义千问**（推荐）：成本极低，生成一个视频通常不到 1 分钱
- **DeepSeek**：国内性价比最高的选项之一
- **GPT-4o**：功能强但贵，非必须

---

### 路径二：源码 + 纯 API（无显卡方案）

**适合谁**：macOS / Linux 用户，或没有独立显卡但想用云端图像 API 的用户。

**优点**：不需要 GPU，图像和视频生成全靠云端 API，按量付费。  
**前提**：需要安装 Git、uv、ffmpeg。

#### 安装依赖

**第一步：安装 uv**（Python 包管理器，比 pip 快几十倍）

```bash
# macOS / Linux（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows（PowerShell）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装后验证：`uv --version`  
完整文档：https://docs.astral.sh/uv/getting-started/installation/

**第二步：安装 ffmpeg**（视频合成必需）

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# Windows（手动下载）
# 下载地址：https://ffmpeg.org/download.html
# 解压后将 bin/ 目录加入系统 PATH
```

验证：`ffmpeg -version`

#### 克隆并启动

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video

# uv 会自动创建虚拟环境并安装所有 Python 依赖
uv run streamlit run web/app.py
```

浏览器打开 http://localhost:8501

#### 配置纯 API 方案

在「⚙️ 系统配置」→「API 媒体模型配置」里选择图像/视频供应商：

| 供应商 | 支持能力 | 申请地址 |
|--------|---------|---------|
| DashScope（通义万象） | 图像生成、视频生成 | dashscope.aliyuncs.com |
| Kling AI（可灵） | 视频生成（国产高质量） | klingai.com |
| Volcengine ARK（Seedance） | 字节视频/图像生成 | volcengine.com/ark |
| OpenAI / GPT Image | GPT 图像生成 | platform.openai.com |

TTS 方面，无显卡时用 **Edge-TTS**（默认工作流），完全免费，无需任何配置。

---

### 路径三：本地全栈（有 NVIDIA 显卡）

**适合谁**：有 NVIDIA 独立显卡，想完全免费、不依赖外部 API 的用户。

**显卡要求**：

| 用途 | 最低显存 | 推荐显存 |
|------|---------|---------|
| 仅图像生成（FLUX / SD） | 6GB VRAM | 8GB+ |
| 图像 + 视频生成（WAN 2.1） | 16GB VRAM | 24GB+ |
| Index-TTS 声音克隆 | 4GB VRAM | 8GB+ |

**不满足显存要求怎么办**：选路径二，图像/视频走 API，TTS 用 Edge-TTS，只有 LLM 需要 key（通义千问极便宜）。

#### 安装 ComfyUI（本地图像/视频/TTS 生成引擎）

```bash
# Windows 用户——下载官方整合包（最省事）
# 下载地址：https://github.com/comfyanonymous/ComfyUI/releases
# 解压后双击 run_nvidia_gpu.bat 启动

# macOS / Linux 用户——从源码安装
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
python main.py
```

ComfyUI 启动后默认运行在 http://127.0.0.1:8188。

Pixelle-Video 配置：系统配置 → ComfyUI URL → `http://127.0.0.1:8188` → 点「测试连接」。

#### 下载 ComfyUI 所需模型

Pixelle-Video 默认工作流使用 **FLUX** 系列图像模型，下载后放到 ComfyUI 的 `models/checkpoints/` 目录：

| 模型 | 推荐版本 | 下载地址 | 大小 |
|------|---------|---------|------|
| FLUX 图像（快速） | FLUX.1-schnell | huggingface.co/black-forest-labs | ~12GB |
| FLUX 图像（高质量） | FLUX.1-dev | huggingface.co/black-forest-labs | ~24GB |
| Index-TTS（声音克隆） | IndexTeam/IndexTTS | huggingface.co/IndexTeam/IndexTTS | ~4GB |
| WAN 2.1（视频生成） | Wan2.1-T2V-14B | huggingface.co/Wan-AI | ~28GB |

> 模型文件较大，下载前确认磁盘空间充足（建议至少预留 50GB 给模型）。

---

## 完整操作流程（以「为什么要养成阅读习惯」为例）

### 第一步：填写系统配置

打开 http://localhost:8501，展开「⚙️ 系统配置」：

1. **LLM 配置**：选择预设（如「通义千问」）→ 填入 API Key → 保存
2. **图像方案（二选一）**：
   - 有 ComfyUI：填 `http://127.0.0.1:8188`，点「测试连接」
   - 无显卡：在「API 媒体模型配置」填入 DashScope 或 Kling 的 key
3. 点击「**保存配置**」

### 第二步：内容输入（左栏）

- **生成模式**：选「AI 生成内容」
- **主题**：输入「为什么要养成阅读习惯」
- **BGM**：选「内置音乐」（可点「试听 BGM」预览）

### 第三步：语音设置（中栏）

- **TTS 工作流**：
  - 普通语音：选「edge-tts」（免费，无需显卡）
  - 声音克隆：选「index-tts」，上传一段你自己的录音（3-10秒，安静环境）

### 第四步：视觉设置（中栏）

- **图像工作流**：
  - 本地 ComfyUI：选 `image_flux.json`（FLUX 模型）
  - API 方案：选 `api/dashscope_image` 或 `api/kling_image`
- **图像尺寸**：
  - 抖音/快手竖屏：720 × 1280
  - YouTube/B站横屏：1280 × 720
- **提示词前缀**（可选，控制配图风格，需英文）：
  - 水墨插画：`minimalist ink wash illustration style, clean brushwork`
  - 科技感：`futuristic tech illustration, glowing neon accent lines, dark background`
  - 默认留空即可
- **视频模板**：
  - 纯配图（稳定）：选 `image_default.html`
  - 动态视频背景：选 `video_default.html`（需要视频生成 API 或本地 WAN 模型）

### 第五步：生成视频（右栏）

点击「**🎬 生成视频**」，实时看到进度：

```
✅ 生成视频文案...（约 10-30 秒）
✅ 分镜 1/5 - 生成插图...（约 30-90 秒/张）
✅ 分镜 2/5 - 生成插图...
✅ 分镜 3/5 - 生成插图...
✅ 分镜 4/5 - 生成插图...
✅ 分镜 5/5 - 生成插图...
✅ 合成语音解说...（约 10 秒）
✅ 合成视频...（约 10-30 秒）
🎉 完成！视频保存到 output/ 目录
```

生成完成后浏览器直接预览，`output/` 文件夹里可以找到 MP4 文件。

---

## 扩展功能

### 数字人口播

让 AI 生成真人口播视频，嘴型与语音同步：

**操作**：左栏选「数字人口播」模式 → 上传人物参考图（或用预置数字人）→ 正常填写主题和 TTS 设置 → 生成

**依赖**：ComfyUI + 数字人相关插件（ComfyUI-MuseTalk），显存建议 8GB+

### 图生视频

先用 AI 生成一张图，再把图变成有动态的视频片段：

**操作**：视觉设置里选支持图生视频的工作流（如 `api/wan_i2v` 或 `api/kling_i2v`）

**依赖**：Kling 或通义万象 API key，按次计费

### 自定义素材

上传你自己拍的照片或视频，让 AI 分析内容并生成配套文案：

**操作**：选「自定义素材」模式 → 上传图片/视频 → AI 自动识别内容 → 生成解说词 → 合成成片

---

## 费用对比

| 方案 | LLM | 图像生成 | TTS | 月估算（100个视频） |
|------|-----|---------|-----|------------------|
| **完全免费** | Ollama 本地 | ComfyUI + FLUX 本地 | Edge-TTS | ¥0（需要 8GB+ 显卡） |
| **轻量付费** | 通义千问 API | DashScope API | Edge-TTS | ≈ ¥5-20 |
| **全 API 云端** | GPT-4o | Kling 视频 | Index-TTS API | ≈ ¥100-500 |

> **推荐「轻量付费」方案**：通义千问文案成本约 ¥0.01-0.05 / 视频，DashScope 图像按张计费，Edge-TTS 免费，100个视频合计不超过 ¥20。

---

## 常见问题

**Q：生成一个视频需要多久？**

- 纯文字模板（static_*）：约 1-2 分钟
- 图片模板（API）：约 3-8 分钟（含网络延迟）
- 图片模板（本地 ComfyUI）：约 5-15 分钟（每张图 30-90 秒）
- 视频模板（API 视频生成）：约 10-30 分钟（视频生成较慢）

**Q：有水印吗？**

本地方案（ComfyUI + Edge-TTS）完全无水印。部分云端 API 免费额度有水印，付费后去除。

**Q：支持中文吗？**

完全支持。文案、TTS、字幕全中文。Edge-TTS 有普通话、粤语等多种中文音色。

**Q：Mac 用户可以用吗？**

可以，走路径二（纯 API 方案）。ComfyUI 也支持 Apple Silicon MPS 加速，但图像生成比 NVIDIA 慢。

**Q：可以批量出视频吗？**

支持，通过 HTTP API 接口批量提交任务，适合矩阵账号批量生产场景。

---

## 推荐工具链

### 「快速出片」配置（最高性价比）

```yaml
LLM: 通义千问 qwen-turbo（API，每个视频 < ¥0.05）
图像: DashScope 通义万象（API）
TTS: Edge-TTS（免费，无需显卡）
模板: image_default.html（稳定快速）
预计时间: 3-5 分钟/个
预计成本: < ¥0.5/个
```

### 「高质量本地」配置（有 NVIDIA 8GB+ 显卡）

```yaml
LLM: 通义千问 qwen-plus 或 Ollama 本地
图像: ComfyUI + FLUX.1-dev（12GB 磁盘）
TTS: Index-TTS 声音克隆（4GB VRAM）
模板: image_premium.html
预计时间: 10-20 分钟/个
预计成本: ≈ ¥0.05/个（仅 LLM）
```

---

> **相关链接**
> - [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) — 主仓库
> - [官方使用文档](https://aidc-ai.github.io/Pixelle-Video/zh) — 详细操作文档
> - [Bilibili 视频教程](https://www.bilibili.com/video/BV1WzyGBnEVp/) — 可视化操作演示
> - [Windows 整合包下载](https://github.com/AIDC-AI/Pixelle-Video/releases/latest)
> - [uv 安装文档](https://docs.astral.sh/uv/getting-started/installation/) — Python 包管理器
> - [ComfyUI 仓库](https://github.com/comfyanonymous/ComfyUI) — 本地图像/视频生成引擎
> - [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) — 类似项目参考

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Pixelle-Video (24,456★, Apache-2.0, Python, AIDC-AI) is a fully automated short video engine — input a topic keyword, get a complete video with AI-written script, AI-generated illustrations/clips, TTS voiceover (with optional voice cloning), BGM, and final MP4 output. Three deployment paths: (1) Windows one-click package — zero setup, just add an LLM API key; (2) source code + cloud APIs — needs `uv` + `ffmpeg`, no GPU required, uses DashScope/Kling/Seedance for images and video; (3) full local stack with ComfyUI + NVIDIA GPU (6GB+ VRAM for images, 16GB+ for WAN 2.1 video). Modular: swap any component independently. Cost estimate for path 2: < ¥0.50/video using Qwen API + DashScope + Edge-TTS (free).

---

## Pipeline

```
Topic → LLM script → per-shot image/video generation → TTS voice → ffmpeg merge → MP4
```

Each module is independently replaceable. The web UI (Streamlit, localhost:8501) configures everything with dropdowns and API key fields — no config files to edit.

## Three Deployment Paths

### Path 1 — Windows One-Click Package (Beginners)

[Download from GitHub Releases](https://github.com/AIDC-AI/Pixelle-Video/releases/latest), extract, run `start.bat`. No Python, no ffmpeg, no setup. Add LLM API key (Qwen/DeepSeek recommended) in Settings and start generating.

### Path 2 — Source + Cloud APIs (No GPU Required)

**Install dependencies**:
```bash
# uv (Python package manager): https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# ffmpeg
brew install ffmpeg              # macOS
sudo apt install ffmpeg          # Ubuntu
# Windows: https://ffmpeg.org/download.html → add bin/ to PATH
```

**Launch**:
```bash
git clone https://github.com/AIDC-AI/Pixelle-Video.git && cd Pixelle-Video
uv run streamlit run web/app.py
```

**Configure**: LLM key (Qwen turbo recommended) + image API key (DashScope/Kling) + Edge-TTS (free, built-in, no GPU).

### Path 3 — Full Local Stack (NVIDIA GPU)

Install [ComfyUI](https://github.com/comfyanonymous/ComfyUI) → download models → set ComfyUI URL to `http://127.0.0.1:8188` in Pixelle-Video settings.

**VRAM requirements**:
- Image only (FLUX.1-schnell): 6GB minimum, 8GB+ recommended
- Video generation (WAN 2.1-14B): 16GB minimum, 24GB+ recommended
- Voice cloning (Index-TTS): 4GB minimum

**Model downloads** (HuggingFace):
- `black-forest-labs/FLUX.1-schnell` — ~12GB, fast image gen
- `black-forest-labs/FLUX.1-dev` — ~24GB, higher quality
- `IndexTeam/IndexTTS` — ~4GB, voice cloning
- `Wan-AI/Wan2.1-T2V-14B` — ~28GB, video generation

## Cost Comparison

| Setup | LLM | Image | TTS | Per 100 Videos |
|-------|-----|-------|-----|---------------|
| Fully free | Ollama local | ComfyUI FLUX local | Edge-TTS | ¥0 (needs 8GB+ GPU) |
| Light paid | Qwen turbo API | DashScope API | Edge-TTS | ≈ ¥5-20 |
| Full cloud | GPT-4o | Kling video | Index-TTS API | ≈ ¥100-500 |

**Recommended**: Qwen turbo + DashScope + Edge-TTS → < ¥0.50/video, 3-5 minutes per video, no GPU needed.

**Links**: [GitHub](https://github.com/AIDC-AI/Pixelle-Video) · [Docs](https://aidc-ai.github.io/Pixelle-Video/zh) · [Bilibili tutorial](https://www.bilibili.com/video/BV1WzyGBnEVp/) · [Windows package](https://github.com/AIDC-AI/Pixelle-Video/releases/latest) · [uv docs](https://docs.astral.sh/uv/)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
