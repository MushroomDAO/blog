---
title: "VidDub：手把手教你用 Intel MacBook 给 YouTube 视频自动配音"
titleEn: "VidDub: Step-by-Step Guide to Auto-Dubbing YouTube Videos on a 16GB Intel MacBook"
description: "VidDub 是全开源的 YouTube 视频自动中文配音 + 多平台发布管线：下载 → Whisper 转写 → AI 翻译 → CosyVoice2 配音 → ffmpeg 合成 → 一键发布到 B站/抖音/快手/小红书。本文专为 16GB 内存 Intel MacBook 用户提供完整手把手操作指南，包含 macOS 环境配置、国内网络处理、模型选择建议和常见报错解决方案。"
descriptionEn: "VidDub is a fully open-source pipeline for auto-dubbing YouTube videos into Chinese and publishing to Bilibili/Douyin/Kuaishou/Xiaohongshu. This guide is specifically for 16GB Intel MacBook users: macOS setup, China network handling, Whisper model selection, and common error fixes."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Tech-Experiment"
tags: ["AI配音", "YouTube", "开源", "视频处理", "Whisper", "MacBook", "多平台发布", "内容创作"]
heroImage: "../../assets/images/viddub-intel-mac-youtube-auto-dubbing-guide-banner.jpg"
---

> **GitHub**: [yaoyue123/VidDub](https://github.com/yaoyue123/VidDub) · MIT 协议 · 喜欢的话给个 ⭐  
> **适合人群**: 想把英文 YouTube 视频搬运到国内平台的内容创作者  
> **本机环境**: 16GB 内存 Intel MacBook（macOS 12+）

---

## 这是什么？一分钟说清楚

**VidDub** 做一件很具体的事：**把英文 YouTube 视频自动变成中文配音视频，然后一键发布到 B站、抖音、快手、小红书。**

整个流程全自动：
```
YouTube URL
  ↓ yt-dlp 下载视频
  ↓ Whisper（本地跑）语音转文字
  ↓ SiliconFlow API 翻译成中文字幕
  ↓ CosyVoice2 TTS 合成中文语音
  ↓ ffmpeg 替换音轨、嵌入字幕
  ↓ AI 自动生成 5 个标题候选 + 8 个标签
  ↓ 一键发布到多个平台
```

你输入一个 YouTube 链接，等一段时间，拿到一个带中文配音的视频，顺便帮你发布好了。

---

## Intel MacBook 能跑吗？——先说结论

**可以，但要做几个设置。**

VidDub 的关键组件分两类：

| 组件 | 在哪里跑 | Intel Mac 情况 |
|---|---|---|
| Whisper 语音转文字 | **本地 CPU** | ✅ 可跑，速度慢一些，选小模型 |
| 翻译（DeepSeek/Qwen） | **云端 API** | ✅ 无关本机性能 |
| CosyVoice2 TTS 配音 | **云端 API** | ✅ 无关本机性能 |
| ffmpeg 合成视频 | **本地 CPU** | ✅ 完全没问题 |
| Web UI 前端 | **本地** | ✅ 完全没问题 |

**Intel Mac 的唯一限制**：Whisper 在 Intel CPU 上跑，没有 GPU 加速（Apple Silicon 有 MPS，Intel 没有）。所以要选 `tiny` 或 `base` 模型来控制时间。

**16GB 内存够用**：Whisper `tiny` 约占 500MB，`base` 约占 1GB，整个服务运行时大约 2-3GB，16GB 绰绰有余。

---

## 开始之前：你需要准备什么

### 1. 注册 SiliconFlow 账号，获取 API Key（免费）

VidDub 的翻译和配音都通过 **SiliconFlow** 云端 API 实现，新用户有免费额度。

1. 访问 https://cloud.siliconflow.cn 注册账号
2. 进入「API 密钥」页面：https://cloud.siliconflow.cn/account/ak
3. 创建一个新的 API Key，复制保存好（格式：`sk_xxxxxxxxxx`）

> 免费额度用于测试完全够，后续如果高频使用可以充值，价格很便宜。

### 2. 代理配置（国内用户必看）

VidDub 需要能访问 YouTube，国内需要代理。

你有代理软件的话，记下它的本地端口（通常是 7890、1080 或 7897），后面配置 `.env` 时会用到。

---

## 安装步骤（Intel MacBook 专版）

### 第零步：安装 Homebrew（如果没有的话）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 第一步：安装必要的软件

```bash
# 安装 ffmpeg（视频处理核心工具）
brew install ffmpeg

# 安装 Python 3.11（推荐版本）
brew install python@3.11

# 安装 Node.js 20（Web UI 需要）
brew install node@20

# 验证安装
ffmpeg -version | head -1
python3.11 --version
node --version
```

如果 `python3.11` 命令不识别，试试：
```bash
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 第二步：克隆仓库

```bash
git clone https://github.com/yaoyue123/VidDub.git
cd VidDub
```

### 第三步：一键启动（自动安装所有依赖）

```bash
chmod +x start.sh
./start.sh
```

这个脚本会自动做完以下事情（第一次约 5-10 分钟）：
- 安装 `uv`（Python 包管理器）
- 创建虚拟环境 `.venv`，安装所有 Python 依赖
- 安装 Playwright Chromium（发布到平台时用）
- 安装前端 npm 依赖
- 创建数据库
- 复制 `.env.example` 到 `backend/.env`

启动成功后，终端会显示类似：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
VITE v5.x.x  ready in xxx ms
Local:   http://localhost:5173/
```

### 第四步：配置 API Key 和关键参数

用文本编辑器打开 `backend/.env`：

```bash
open -e backend/.env   # 用 TextEdit 打开
# 或
nano backend/.env       # 用终端编辑
```

**必填项**：
```dotenv
# 必填：你的 SiliconFlow API Key
SILICONFLOW_API_KEY=sk_你的key在这里

# Intel Mac 必设：用小模型，速度快
WHISPER_MODEL=base

# 如果需要代理访问 YouTube（替换成你的代理端口）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

**保存后重启服务**：
```bash
# Ctrl+C 停止，然后重新启动
./start.sh
```

### 第五步：下载 Whisper 模型（只需一次）

首次运行时，Whisper 需要下载模型文件。国内下载可能很慢，先设置镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

然后手动触发下载：
```bash
cd backend
.venv/bin/python -c "import whisper; whisper.load_model('base'); print('下载完成')"
```

- `tiny` 模型：约 75MB，速度最快（精度较低）
- `base` 模型：约 145MB，速度与精度平衡（**Intel Mac 推荐**）
- `small` 模型：约 480MB，精度好但慢（16GB Intel 勉强可用）

> 下载一次后缓存在 `~/.cache/whisper/`，后续不需要重下。

---

## 实际使用：配音一个 YouTube 视频

### 打开 Web UI

浏览器访问：http://localhost:5173

Web UI 主要包含：
- **Dashboard**：任务列表，查看进度
- **New Task**：输入 YouTube URL，开始配音任务
- **Settings**：修改模型、语速、发布设置等
- **Platform Login**：登录各平台账号用于发布

### 提交第一个配音任务

1. 点击「New Task」或「开始配音」
2. 粘贴 YouTube 视频链接，例如：`https://www.youtube.com/watch?v=xxxxx`
3. 确认设置：
   - Whisper 模型：`base`（Intel Mac 用这个）
   - 翻译模型：`DeepSeek-V4-Flash`（默认，快且准）
   - TTS 声音：可选 alex、anna 等
4. 点击「开始」

### 等待处理（时间参考）

以一个 **10 分钟的视频**为例，在 16GB Intel MacBook 上：

| 阶段 | 耗时估算 | 说明 |
|---|---|---|
| 下载视频 | 1-3 分钟 | 取决于网速和代理 |
| Whisper 转写（base） | 8-15 分钟 | Intel CPU 约 0.8-1.5x 实时 |
| AI 翻译 | 1-3 分钟 | SiliconFlow API，和本机无关 |
| CosyVoice2 配音 | 2-5 分钟 | SiliconFlow API |
| ffmpeg 合成 | 1-2 分钟 | CPU 处理，Intel 完全没问题 |
| **总计** | **约 13-28 分钟** | 视频越短越快 |

> 如果嫌慢，改成 `WHISPER_MODEL=tiny`，转写时间减半，精度略降。

### 查看结果和编辑

任务完成后：
1. Dashboard 状态变为「完成」
2. 点击任务可以**预览配音视频**
3. 查看 AI 生成的 5 个标题候选，选一个或自己改
4. 查看 8 个标签建议，可以编辑

### 发布到平台

**第一次发布需要登录各平台**：

进入 Settings → Platform Login，会弹出浏览器窗口让你手动登录（Playwright 自动化）。登录一次后，登录态保存在本地，后续不需要重复登录。

支持的平台：
- 🎬 **B站 (Bilibili)**
- 🎵 **抖音 (Douyin)**
- ▶️ **快手 (Kuaishou)**
- 📺 **腾讯视频**
- 🌺 **小红书 (Xiaohongshu)**

选好平台，点击「发布」即可。

---

## Intel Mac 专属优化建议

### Whisper 模型选择指南

| 模型 | 大小 | 10 分钟视频转写时长 | 推荐场景 |
|---|---|---|---|
| `tiny` | 75MB | ~5-8 分钟 | 快速测试，短视频，精度要求不高 |
| `base` | 145MB | ~10-15 分钟 | **日常使用推荐，精度够用** |
| `small` | 480MB | ~25-40 分钟 | 精度要求高，可以接受等待 |
| `medium` | 1.5GB | ~60-90 分钟 | 不推荐 Intel Mac 使用 |

**结论**：日常用 `base`，赶时间用 `tiny`。

### 减少等待时间的技巧

1. **批量提交**：同时提交多个视频，让 VidDub 并发处理（Settings 里设置 `max_concurrent_downloads`）
2. **夜间运行**：晚上提交任务，早上起来视频就处理完了
3. **选短视频先练手**：5 分钟以内的视频整个流程 10-15 分钟搞定

### 降低 API 费用

SiliconFlow 有使用量限制，优化配置：
- 翻译模型用 `DeepSeek-V4-Flash`（比大模型便宜，质量够用）
- `translation_context_window` 设为 `2`（窗口越小 token 越少）
- 如果遇到 429 限流错误，等 60 秒后点「重试」

---

## 常见报错解决

### 报错：`SILICONFLOW_API_KEY is required`
```bash
# 确认 .env 文件存在
ls backend/.env

# 确认 key 不为空
grep SILICONFLOW_API_KEY backend/.env
```
修复：在 `backend/.env` 里填入正确的 `sk_xxx` 格式 API Key，然后重启服务。

### 报错：`ffmpeg not found`
```bash
brew install ffmpeg
# 安装完验证
ffmpeg -version
```

### Whisper 下载极慢或卡住
```bash
# 设置镜像源
export HF_ENDPOINT=https://hf-mirror.com
# 重新下载
cd backend && .venv/bin/python -c "import whisper; whisper.load_model('base')"
```

### YouTube 无法访问（下载失败）
检查 `backend/.env` 里是否配置了代理：
```dotenv
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```
端口号换成你代理软件的实际端口。

### 429 限流错误
SiliconFlow 请求频率太高。解决：
1. 等 60 秒，点 Web UI 的重试按钮
2. 把 `max_concurrent_downloads` 改为 1
3. 错峰使用（避开高峰期）

### 转写质量差、错字多
从 `tiny` 换成 `base` 模型：
```dotenv
WHISPER_MODEL=base
```
重启服务后重新提交任务。

### start.sh 执行报错：`permission denied`
```bash
chmod +x start.sh
./start.sh
```

---

## 命令行快速使用（不打开浏览器）

如果你更喜欢命令行操作：

```bash
cd backend

# 给单个视频配音
.venv/bin/python -m app.cli dub "https://www.youtube.com/watch?v=你的视频ID"

# 查看所有任务状态
.venv/bin/python -m app.cli status

# 恢复中断的任务
.venv/bin/python -m app.cli resume
```

---

## 版权和合规说明

> **重要**：搬运视频前请注意版权问题。

- 只搬运创作者明确授权（CC 协议）或本人所有的视频
- 发布时注明原视频出处和作者
- 不要搬运未经授权的受版权保护内容
- 各平台对搬运内容都有审核，频繁发布可能被限流

VidDub 本身是工具，合规使用与否由用户负责。

---

## 快速上手总结

```bash
# 1. 安装依赖
brew install ffmpeg python@3.11 node@20

# 2. 克隆并启动
git clone https://github.com/yaoyue123/VidDub.git
cd VidDub && chmod +x start.sh && ./start.sh

# 3. 配置（必填）
nano backend/.env
# 填入：SILICONFLOW_API_KEY=sk_你的key
# 填入：WHISPER_MODEL=base
# 如需代理：HTTP_PROXY=http://127.0.0.1:7890

# 4. 重启
./start.sh

# 5. 打开 Web UI
open http://localhost:5173

# 6. 粘贴 YouTube URL，开始！
```

喜欢这个项目的话，去 GitHub 给作者点个 ⭐：https://github.com/yaoyue123/VidDub

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: VidDub auto-dubs YouTube videos into Chinese and publishes to Bilibili/Douyin/Kuaishou/Xiaohongshu. This guide is for 16GB Intel MacBook users — Whisper runs locally on CPU (use `base` model), everything else (translation, TTS) uses SiliconFlow cloud API.

---

## Pipeline Overview

```
YouTube URL → yt-dlp download → Whisper STT (local CPU) → 
SiliconFlow translate → CosyVoice2 TTS → ffmpeg compose → 
AI title generation → 1-click publish to 5 platforms
```

## Intel Mac Setup

```bash
# Prerequisites
brew install ffmpeg python@3.11 node@20

# Clone and start
git clone https://github.com/yaoyue123/VidDub.git
cd VidDub && ./start.sh

# Configure backend/.env
SILICONFLOW_API_KEY=sk_your_key    # Get from cloud.siliconflow.cn
WHISPER_MODEL=base                  # Use base for Intel Mac (not tiny or medium)
HTTP_PROXY=http://127.0.0.1:7890   # If you need proxy for YouTube
```

## Intel Mac Performance (10-min video)

| Whisper Model | Transcription Time | Recommendation |
|---|---|---|
| `tiny` (75MB) | ~5-8 min | Fast tests, short videos |
| `base` (145MB) | ~10-15 min | **Recommended for daily use** |
| `small` (480MB) | ~25-40 min | High accuracy, patience required |

Total pipeline for 10-min video: **~15-30 minutes** on 16GB Intel Mac.

## Open in Browser

http://localhost:5173 — paste YouTube URL, click Start, wait.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
