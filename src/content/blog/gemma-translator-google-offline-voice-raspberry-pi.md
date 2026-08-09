---
title: "Gemma Translator：用树莓派 5 做一台完全离线的双向语音翻译机"
titleEn: "gemma-translator-google-offline-voice-raspberry-pi"
description: "Google Gemma 团队开源的全离线双向语音翻译项目，JavaScript/Python，Apache 2.0。以树莓派 5（8GB）为目标硬件，Gemma 4（gemma4-e2b）通过 LiteRT-LM 本地推理，Moonshine 负责语音识别和 TTS 合成。双通道设计：两个人面对面，各自说母语，实时互译。一键部署为永久 kiosk 服务。源码来自 Google Antigravity 实验。"
descriptionEn: "Google Gemma team's open-source fully-offline bidirectional voice translator, JavaScript/Python, Apache 2.0. Target hardware: Raspberry Pi 5 (8GB). Gemma 4 (gemma4-e2b) runs locally via LiteRT-LM; Moonshine handles STT and TTS. Two-lane design: two people face each other, each speaks their language, real-time mutual translation. One-command kiosk deployment. From Google Antigravity experiments."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["Gemma", "语音翻译", "离线AI", "树莓派", "LiteRT", "本地推理", "Mycelium"]
heroImage: "../../assets/images/gemma-translator-google-offline-voice-raspberry-pi-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

大多数实时翻译方案都依赖云端——连不上网就不工作，隐私问题无法回避，延迟受网络状况左右。

Gemma Translator 用一块树莓派 5 解决这个问题：Gemma 4 模型通过 LiteRT-LM 完全在本地运行，Moonshine 负责语音转文字和文字转语音，整个链路不需要任何外部请求。设备上电就能用，断网照常工作。

GitHub: https://github.com/google-gemma/gemma-translator | Apache 2.0 | JavaScript / Python

---

## 硬件组合

| 组件 | 规格 |
|------|------|
| 主板 | Raspberry Pi 5（**8GB RAM**） |
| 音频输入 | 麦克风或 USB 音频采集卡 |
| 音频输出 | 扬声器或耳机 |
| 显示屏 | 任意屏幕，建议 480×320 小触摸屏（kiosk 场景）|

仓库里附有 STL 文件，可以打印配套外壳，做成完整的独立设备。

---

## 技术栈

```
用户语音（麦克风）
  ↓
Moonshine STT（语音转文字）
  ↓
Gemma 4 (gemma4-e2b) via LiteRT-LM（翻译推理，纯本地）
  ↓
moonshine-voice TTS（文字转语音）
  ↓
扬声器输出
```

- **LiteRT-LM**：Google 的轻量级本地推理引擎，专为边缘设备优化
- **Gemma 4（gemma4-e2b）**：2B 参数的小型多语言模型，在树莓派 5 上可以实时推理
- **Moonshine**：专注低延迟的本地 STT/TTS，不依赖云端

---

## 双通道设计

这是这个项目最有意思的部分：它不是单向翻译，而是**两个人面对面使用同一台设备**。

界面有两个"通道"（Lane），各自对应一个人，各自设置语言。每个人说话，系统识别、翻译，用另一侧的语言在扬声器播放。两侧可以独立操作，也可以用"单人模式"轮流控制。

```
通道 1（Person 1）  ←→  通道 2（Person 2）
  中文 ──────────────────── 英文
  说话 → STT → Gemma 翻译 → TTS → 对方听到
```

两种键盘模式：
- **Landscape 模式**（默认）：Spacebar 切换当前活跃通道，Z 键按住说话
- **Vertical 模式**：两通道各自有独立按键（Z / X），两人可以同时操作

---

## 快速上手

```bash
# 1. 授权脚本
chmod +x setup.sh download_model.sh start.sh deploy-pi.sh

# 2. 安装 Python 依赖（创建 venv）
./setup.sh

# 3. 下载 gemma4-e2b 模型（从 Hugging Face 导入 LiteRT-LM）
./download_model.sh

# 4. 启动（开发模式）
./start.sh

# 或生产模式（跳过 Vite dev server，从 dist/ 直接服务）
./start.sh --prod
```

启动后访问：
- 开发模式 UI：`http://localhost:5173`
- 生产模式 / API：`http://localhost:3000`
- LiteRT-LM：`http://localhost:9379`

---

## 树莓派一键永久部署

```bash
./deploy-pi.sh
```

这个脚本在 Raspberry Pi OS / Debian 上自动完成：安装系统依赖、创建 Python 环境、构建生产前端、下载 LiteRT 模型、注册 systemd 服务，并配置 LXDE 自动启动 Chromium kiosk 模式（指向 `http://localhost:3000`）。重启后设备直接进入翻译界面，不需要登录或手动操作。

---

## 背景

这个项目是 Google Antigravity 实验（antigravity.google）的产物——一个专门做硬件+AI 边缘计算实验的项目组。代码在 Apache 2.0 下开源，仓库里附有 STL 外壳文件，整个设计对社区完全开放。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Gemma Translator: A Fully Offline Bidirectional Voice Translator on a Raspberry Pi 5

*by Mycelium Protocol*

---

Most real-time translation solutions depend on the cloud — they stop working offline, raise privacy concerns, and are subject to network latency.

Gemma Translator solves this with a Raspberry Pi 5: Gemma 4 runs entirely locally via LiteRT-LM, Moonshine handles speech-to-text and text-to-speech, and the entire pipeline makes no external requests. Power it on and it works — no internet required.

GitHub: https://github.com/google-gemma/gemma-translator | Apache 2.0 | JavaScript / Python

---

### Hardware

| Component | Spec |
|-----------|------|
| Board | Raspberry Pi 5 (**8GB RAM**) |
| Audio input | Microphone or USB audio capture interface |
| Audio output | Speaker or headphone output |
| Display | Any screen; 480×320 kiosk touchscreen recommended |

STL files for a 3D-printed enclosure are included in the repo — the whole design is open hardware.

---

### The Pipeline

```
User voice (microphone)
  ↓
Moonshine STT (speech-to-text)
  ↓
Gemma 4 (gemma4-e2b) via LiteRT-LM (translation inference, fully local)
  ↓
moonshine-voice TTS (text-to-speech)
  ↓
Speaker output
```

- **LiteRT-LM**: Google's lightweight local inference engine for edge devices
- **Gemma 4 (gemma4-e2b)**: 2B-parameter multilingual model that runs in real time on a Pi 5
- **Moonshine**: Low-latency local STT/TTS — no cloud dependency

---

### Two-Lane Design

The most interesting design choice: this isn't one-way translation. **Two people face the same device**, each on their own lane with their own language set. Each person speaks, the system transcribes, translates, and plays back through the speaker in the other person's language.

```
Lane 1 (Person 1) ←→ Lane 2 (Person 2)
  Chinese ─────────────── English
  Speak → STT → Gemma → TTS → other person hears
```

Two keyboard modes:
- **Landscape (default)**: Spacebar switches the active lane, Z (hold) records active person
- **Vertical ("two-hand")**: Each lane has its own dedicated keys — Z for Person 1, X for Person 2

---

### Quick Start

```bash
chmod +x setup.sh download_model.sh start.sh deploy-pi.sh
./setup.sh            # create Python venv, install dependencies
./download_model.sh   # fetch gemma4-e2b from HuggingFace → LiteRT-LM
./start.sh            # launch LiteRT-LM + Python API + Vite frontend
./start.sh --prod     # production: serve compiled assets from dist/
```

- Dev UI: `http://localhost:5173`
- Prod / API: `http://localhost:3000`
- LiteRT-LM: `http://localhost:9379`

---

### One-Command Permanent Kiosk Deployment

```bash
./deploy-pi.sh
```

On Raspberry Pi OS / Debian, this script automatically: installs system packages, sets up the Python environment, builds production frontend, downloads the LiteRT model, registers a systemd service, and configures LXDE autostart to launch Chromium in kiosk mode pointing at `http://localhost:3000`. After reboot, the device goes straight into the translator interface — no login, no manual steps.

---

### Background

This project came out of **Google Antigravity** (antigravity.google) — Google's hardware + edge AI experimental group. The code is Apache 2.0, the STL enclosure files are in the repo, and the full design is open to the community.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
