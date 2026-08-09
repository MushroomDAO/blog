---
title: "Mage-VL 跑在 Mac 上：微软视觉大模型的本地化部署，图片视频实时流式注释"
titleEn: "Mage-VL on a Mac: Running Microsoft's Vision Model Locally with Real-Time Image and Video Annotation"
description: "karlazx 发布了 mage-vl-local-mac，一个让 Microsoft Mage-VL 视觉语言模型在 Apple Silicon 上本地运行的社区项目。双击 setup.command 完成一键安装，FastAPI + React 浏览器界面，支持图片问答、视频问答（DCVC-RT 神经编解码器）和实时分段流式注释，全程本地推理，数据不出 Mac。"
descriptionEn: "karlazx releases mage-vl-local-mac, a community project that runs Microsoft Mage-VL vision-language model locally on Apple Silicon. One-click setup.command install, FastAPI + React browser UI, image Q&A, video Q&A with DCVC-RT neural codec canvases, and real-time segment-by-segment streaming commentary — all local inference, media never leaves the Mac."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-News"
tags: ["Mage-VL", "微软", "Apple Silicon", "本地推理", "视频理解", "多模态", "MPS", "Mycelium"]
heroImage: "../../assets/images/mage-vl-local-mac-apple-silicon-image-video-banner.jpg"
---

*by Mycelium Protocol*

---

微软的 Mage 研究团队做了一个视觉语言模型 **Mage-VL**，能看懂图片和视频，还能对视频内容做实时的分段流式注释——"边看边说"，而不是等视频处理完再输出。

问题是，官方仓库（`microsoft/Mage`）面向的是研究环境：CUDA 优先，命令行推理，需要自己组装完整的研究工具链。

**[mage-vl-local-mac](https://github.com/karlazx/mage-vl-local-mac)**（karlazx）解决的就是这个问题：让 Apple Silicon 用户双击两次就能跑起来，在浏览器里用。

---

## 它是什么

mage-vl-local-mac 是 Mage-VL 的 macOS 部署和体验层，不是微软官方项目。社区项目，MIT 授权，2026 年 8 月 1 日发布。

架构：

```
React UI（localhost:3000）
    ↓
FastAPI（localhost:8000）→ 单用户推理队列 → 视觉预处理
                                              ├── 图片缩放（quick/balanced/原始分辨率）
                                              ├── 视频均匀采帧
                                              └── DCVC-RT 神经编解码器（MPS → CPU fallback）
                                                          ↓
                                               Mage-VL（PyTorch + Apple MPS）
                                                          ↓
                                               SSE 流式输出 → 浏览器
```

---

## 三个核心能力

### 图片问答

上传图片，提问，Mage-VL 回答。支持三种视觉预算模式：

- **quick**：快速，低分辨率，省内存
- **balanced**：平衡，适合大多数场景
- **original**：原始分辨率，最精确，内存消耗最高

### 视频问答

上传视频（支持到 150 秒），两种处理路径：

- **均匀采帧**：传统方式，从视频均匀抽帧作为输入
- **DCVC-RT 神经编解码器**：把视频解码为神经"画布"（canvas），是 Mage 研究的核心路径，比传统 H.264/HEVC 帧更适合模型理解

DCVC-RT 优先在 MPS 上运行，不支持时自动退回 CPU。

### 实时分段流式注释（Proactive Streaming）

这是 Mage-VL 的特色能力。对于长视频，模型不会等全部处理完再输出，而是：

1. 处理第一段视频 → 立刻输出这段的注释
2. 处理第二段视频，携带第一段的注释作为上下文 → 输出第二段注释
3. ……以此类推

类似直播主播在"边看边讲"。浏览器通过 SSE（Server-Sent Events）实时接收每个文字 token。

你还可以在运行中编辑"实时注释指令"，比如让模型专注于某类内容，也有重复文字抑制机制，防止连续段落输出相同的句子。

---

## 一键安装

```bash
# 方法 1：下载 Release ZIP，解压后双击
# → setup.command → start.command → 打开 localhost:3000

# 方法 2：克隆源码
git clone https://github.com/karlazx/mage-vl-local-mac.git
cd mage-vl-local-mac
./setup.command   # 安装 Python 3.12、Node.js 22、FFmpeg、模型权重
./start.command   # 启动服务
```

`setup.command` 会自动通过 Homebrew 安装依赖，创建隔离的 Python 环境，构建前端，然后从 Hugging Face 下载 `microsoft/Mage-VL` 权重（约 25 GB）。模型权重不包含在仓库里，首次运行自动下载，支持断点续传。

---

## 硬件要求

- Apple Silicon Mac（M1/M2/M3/M4 均可）
- **推荐 32 GB 统一内存**（完整模型权重 + 视频处理需要）
- 约 25 GB 可用磁盘
- 低内存机器在 quick/balanced 图片模式下可能可用，视频任务可能超出内存限制

MacBook Air 无风扇，长视频推理可能触发热降频。

---

## 隐私

所有推理本地进行。用户上传的媒体文件存在本地 `runtime/` 目录，不发送到任何云端 API 或这个项目的服务器。临时文件在过期后自动清理。

---

## 与官方 microsoft/Mage 的关系

| 方面 | microsoft/Mage（官方） | mage-vl-local-mac（本项目） |
|------|------------------------|---------------------------|
| 目标 | 研究代码，CUDA 环境 | macOS 一键部署，浏览器 UI |
| 硬件路径 | CUDA 优先 | Apple MPS，FP16/BF16 |
| 视频编解码 | 传统 H.264/HEVC + DCVC-RT | DCVC-RT + 均匀采帧 |
| 训练 / Mage-Flow | 包含 | 不包含 |

如果你做研究、需要训练、或者遇到模型问题，应该去官方仓库报 issue。这个项目专注的是"Mac 上好用"这件事。

---

## 本地 API

服务启动后暴露一个 REST + SSE API，绑定在 `127.0.0.1`：

| Endpoint | 用途 |
|----------|------|
| `GET /api/status` | 模型、MPS、DCVC、队列状态 |
| `POST /api/jobs` | 创建图片/视频/流式注释任务 |
| `GET /api/jobs/{id}/events` | SSE 流，获取 token/时间线/最终结果 |
| `GET /api/artifacts/{id}/{file}` | 读取生成的帧和画布 |

单用户推理队列，同时只处理一个任务，适合统一内存的单机场景。

---

## 为什么现在值得关注

Mage-VL 的视频理解能力，特别是 DCVC-RT 神经编解码器路径和实时分段流式注释，在多模态模型里不多见——大多数本地视频理解工具还在用传统采帧的方式。

karlazx 把这个研究能力包成了一个对普通 Mac 用户可以双击运行的工具，这个"最后一公里"的工作本身就有价值。

仓库：[github.com/karlazx/mage-vl-local-mac](https://github.com/karlazx/mage-vl-local-mac)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Mage-VL on Your Mac: Microsoft's Vision Model, One-Click Local Deployment

*by Mycelium Protocol*

Microsoft's Mage research team built **Mage-VL**, a vision-language model that understands images and videos and can produce real-time segment-by-segment streaming commentary — "speaking while watching" rather than waiting until the full video is processed.

The problem: the official repository (`microsoft/Mage`) targets research environments — CUDA-first, command-line inference, requiring the full research toolchain to be assembled manually.

**[mage-vl-local-mac](https://github.com/karlazx/mage-vl-local-mac)** (karlazx) solves that: Apple Silicon users can double-click twice and use it in a browser. Community project, MIT license, released August 2026.

### Architecture

FastAPI backend at `localhost:8000`, React frontend at `localhost:3000`. A single-user inference queue manages jobs; visual preprocessing dispatches to three paths: image resize presets, uniform frame sampling, or DCVC-RT neural codec canvases. All routes feed into Mage-VL via PyTorch + Apple MPS. Results stream to the browser over Server-Sent Events.

### Three Core Capabilities

**Image Q&A** — Upload an image, ask a question, get an answer. Three visual budget modes: quick (low-res, low memory), balanced (general purpose), and original-resolution (maximum detail, highest memory).

**Video Q&A** — Upload a video (up to 150 seconds). Two processing paths:
- *Uniform frame sampling*: traditional approach, uniform frame extraction
- *DCVC-RT neural codec*: decodes video into neural "canvases" — the core research path in Mage, more semantically appropriate for the model than raw H.264/HEVC frames. Runs on MPS; falls back to CPU if unsupported

**Proactive Streaming Commentary** — The distinctive Mage-VL capability. For long videos, the model doesn't wait until all processing is complete:
1. Process segment 1 → immediately publish commentary for segment 1
2. Process segment 2, using segment 1's commentary as context → publish segment 2
3. ...continuing through the video

Think of a commentator narrating live footage. You can edit the live-commentary instruction during playback — redirect the model's focus mid-video — and repeated-text suppression prevents duplicate sentences across consecutive segments.

### One-Click Setup

```bash
git clone https://github.com/karlazx/mage-vl-local-mac.git
cd mage-vl-local-mac
./setup.command   # installs Python 3.12, Node.js 22, FFmpeg; downloads ~25 GB model weights
./start.command   # starts the service
# open http://localhost:3000
```

Or download the Release ZIP, extract, and double-click `setup.command`. The model weights (Microsoft/Mage-VL from Hugging Face) download automatically with resumable support; they're not bundled in the repository.

**Requirements:** Apple Silicon, macOS with Homebrew, 32 GB unified memory recommended, ~25 GB free disk. Works on 8–16 GB machines for image quick/balanced modes; long video jobs may exceed available memory.

### Privacy

All inference is local. Media uploaded through the browser stays under the local `runtime/` directory and is never sent to any cloud API or this project's servers. Temporary artifacts are cleaned up when they go stale.

### vs. Official `microsoft/Mage`

The official repository is the canonical source for Mage research, training, Mage-Flow, and the traditional codec pipeline. Use the official repo for upstream issues, model research, and training. Use this project when the priority is a convenient native Mac deployment and a usable browser-based product surface.

### Why It Matters Now

Most local video understanding tools still rely on traditional frame sampling. Mage-VL's DCVC-RT neural codec path and real-time proactive streaming are less common in local deployments — they come from the research side where inference environments typically require CUDA. karlazx's "last-mile" work — packaging this into a double-click Mac app — makes that research capability accessible to a much wider set of users.

Repository: [github.com/karlazx/mage-vl-local-mac](https://github.com/karlazx/mage-vl-local-mac)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
