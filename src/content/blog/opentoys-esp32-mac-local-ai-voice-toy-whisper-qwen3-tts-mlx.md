---
title: "OpenToys：ESP32-S3 + Mac，把 AI 语音玩具的推理完全跑在本地，零云端依赖"
titleEn: "opentoys-esp32-mac-local-ai-voice-toy-whisper-qwen3-tts-mlx"
description: "akdeb/OpenToys 是 ElatoAI 的本地优先版本：ESP32-S3 作硬件终端，Apple Silicon Mac 负责全部推理（Whisper Turbo ASR + Qwen3-TTS/Chatterbox + MLX LLM），WebSocket 经由玩具自建 WiFi 热点连接，零云端依赖，MIT 开源，148 stars。桌面端是 Tauri + React + Rust，支持多语言、声音克隆（<10秒音频），可刷入任意 ESP32-S3 设备；WIRED、ArsTechnica、Hackster 均有报道。"
descriptionEn: "akdeb/OpenToys is the local-first version of ElatoAI: ESP32-S3 as the hardware terminal, Apple Silicon Mac handles all inference (Whisper Turbo ASR + Qwen3-TTS/Chatterbox + MLX LLMs) over WebSocket via the toy's own WiFi AP — zero cloud, MIT, 148 stars. Desktop app is Tauri + React + Rust; supports multi-language, voice cloning (<10s audio), and flashing to any ESP32-S3 device. Featured in WIRED, ArsTechnica, Hackster."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["ESP32", "本地AI", "语音玩具", "MLX", "Whisper", "Qwen3", "开源", "儿童AI"]
heroImage: "../../assets/images/opentoys-esp32-mac-local-ai-voice-toy-whisper-qwen3-tts-mlx-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：akdeb/OpenToys  
主页：elatoai.com  
许可证：MIT  
语言：TypeScript + Rust  
Stars：148 · Forks：9  
创建：2026-01-24 | 最近更新：2026-08-21  
报道：WIRED · ArsTechnica · Hackster

---

## 一、它是什么

OpenToys 解决的问题只有一个：**让儿童 AI 语音玩具的所有推理留在家里**。

它的前身是 [ElatoAI](https://github.com/akdeb/ElatoAI)——一个接 OpenAI Realtime、Gemini、ElevenLabs 等云端 API 的 ESP32 方案。作者 Akshat 之前在做云端语音玩具创业，发现家长对儿童数据上传高度敏感，于是把整套推理链移到本地，推出 OpenToys。两个项目的硬件和通信层完全相同，区别只在推理运行在哪：ElatoAI 在云端，OpenToys 在你的 Mac 上。

项目在 Pi Day（2026-03-14）发布，148 stars，MIT。

---

## 二、架构：玩具自己开热点，Mac 来连

最反直觉的设计在网络层：**不是 Mac 连路由器，而是 ESP32 自己开 WiFi 热点**。

```
ESP32-S3 开机
      ↓
广播 AP「ELATO」（无密码，192.168.4.1）
      ↓
Mac 加入 ELATO（macOS 会提示「无互联网」，正常）
      ↓
ESP32 检测到 Mac，主动建立 WebSocket
      ↓
LED 变白，App 显示「Ready on device」
      ↓
按 Play，开始说话
```

好处：零路由器配置，零捕获门户，玩具带到哪家里都能用，不依赖家庭网络拓扑。代价是：Mac 加入 ELATO 期间没有互联网，下载模型和声音要提前做好。

---

## 三、推理链：全部在 Mac 上

一句话讲完 App 的作用：**STT + LLM + TTS 全跑在 Apple Silicon，只把语音和文字通过 WebSocket 传给 ESP32**。

| 组件 | 模型 | 说明 |
|------|------|------|
| ASR | Whisper Turbo | 语音识别，本地 MLX 推理 |
| LLM | mlx-community 任意模型 | Gemma 4、Qwen3.8、Llama、Mistral3 等 |
| TTS | Qwen3-TTS / Chatterbox-turbo | 文字转语音，支持声音克隆 |
| App 框架 | Tauri + React + Rust | macOS 桌面应用 |
| 硬件 | ESP32-S3 | 采集麦克风音频，播放 TTS 输出 |

LLM 选择完全开放——任何 `mlx-community` 上的模型都能接进来，从轻量的 Mistral3 到 Qwen3 系列都行。推理走 MLX，Apple Silicon 的统一内存和 Metal 加速直接用上。

---

## 四、硬件

ESP32-S3 方案，配件清单：

- **主控**：ESP32-S3（无 PSRAM 版本即可）
- **麦克风**：INMP441（I2S 数字麦克风）
- **功放**：MAX98357A（I2S DAC + D 类功放，直驱小喇叭）
- **电源**：3.7V 锂电池

项目提供 PCB 设计文件和固件。刷机流程集成在 App 里——进设置，选串口，点 Flash，等完成，拔线。以后更新固件重新刷一次就行。

固件烧录后，玩具上电自动开热点，不需要配任何网络凭据。

---

## 五、声音和角色

App 内置多套角色卡（personalities.json），每个角色有独立系统 prompt 和声音。支持功能：

- **多语言**：英语、中文、西班牙语、法语、日语、韩语、葡萄牙语、德语、意大利语
- **声音克隆**：不到 10 秒的参考音频即可克隆声音，用于 TTS 输出
- **自定义角色**：修改 personalities.json 添加新角色、新故事线

从内置卡看，定位是儿童陪伴：讲故事、做游戏、教育对话。但因为是本地 LLM，换个系统 prompt 可以变成任何形态。

---

## 六、安全说明

项目在 README 里明确写了三条限制：

1. **幻觉**：LLM 和 TTS 模型会输出错误内容，不能作为事实来源
2. **不当输出**：对抗性 prompt 仍可能触发不安全回复
3. **情感依赖**：AI 不能替代真人互动，尤其对儿童

> 「与儿童一起使用时，请家长在场，把这当作探索工具，不是权威来源。」

这段话值得注意——愿意在 README 里主动写出这些边界的硬件 AI 项目不多。

---

## 七、为什么这个方向重要

儿童语音 AI 玩具是个敏感领域：孩子说的话、问的问题、在家里的时间规律，全部会进云端数据库。家长不安是合理的。

OpenToys 的路线是技术上的直接回应——不是隐私政策文件，而是**物理上不可能上传**：推理在本地，WebSocket 只在家庭热点内，没有任何外网请求路径。

从 ElatoAI（云端）到 OpenToys（本地）的转变，也展示了一条可以复制的路径：用 MLX + Apple Silicon 替换云端 API，把延迟和隐私问题一起解决掉。148 stars，MIT，对想做本地 AI 硬件的人来说是值得 fork 的起点。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenToys: ESP32-S3 + Mac, Running AI Voice Toy Inference Entirely Locally

*by Mycelium Protocol*

---

GitHub: akdeb/OpenToys  
Homepage: elatoai.com  
License: MIT  
Language: TypeScript + Rust  
Stars: 148 · Forks: 9  
Created: 2026-01-24 | Updated: 2026-08-21  
Press: WIRED · ArsTechnica · Hackster

---

### What It Is

OpenToys solves one problem: **keep all inference for a children's AI voice toy inside the home**.

Its predecessor is [ElatoAI](https://github.com/akdeb/ElatoAI) — an ESP32 platform that connects to cloud APIs like OpenAI Realtime, Gemini, and ElevenLabs. Author Akshat was building a cloud voice toy startup, noticed parents were deeply uncomfortable with children's audio being uploaded to external servers, and moved the entire inference stack local. OpenToys is the result. Both projects share identical hardware and transport layers; the only difference is where inference runs: ElatoAI in the cloud, OpenToys on your Mac.

Launched on Pi Day (2026-03-14), 148 stars, MIT.

---

### Architecture: The Toy Hosts Its Own Hotspot

The most counterintuitive design choice is in networking: **it's not the Mac connecting to a router — the ESP32 opens its own WiFi access point**.

```
ESP32-S3 boots
      ↓
Broadcasts AP "ELATO" (no password, 192.168.4.1)
      ↓
Mac joins ELATO (macOS warns "no internet" — expected)
      ↓
ESP32 detects the Mac, opens WebSocket proactively
      ↓
LED turns white, app shows "Ready on device"
      ↓
Press Play, start talking
```

Upside: zero router config, no captive portal, the toy works identically at any home without touching network settings. Tradeoff: while joined to ELATO, the Mac has no internet — download models and voices before joining.

---

### Inference Chain: All on Mac

The app's job in one sentence: **STT + LLM + TTS all run on Apple Silicon; only audio and text travel over WebSocket to the ESP32**.

| Component | Model | Notes |
|-----------|-------|-------|
| ASR | Whisper Turbo | Speech-to-text, local MLX inference |
| LLM | Any mlx-community model | Gemma 4, Qwen3.8, Llama, Mistral3, etc. |
| TTS | Qwen3-TTS / Chatterbox-turbo | Voice synthesis with voice cloning support |
| App framework | Tauri + React + Rust | macOS desktop app |
| Hardware | ESP32-S3 | Captures mic audio, plays TTS output |

LLM selection is fully open — any model on `mlx-community` plugs in, from lightweight Mistral3 to the Qwen3 series. Inference uses MLX, taking full advantage of Apple Silicon's unified memory and Metal acceleration.

---

### Hardware

ESP32-S3 build, parts list:

- **MCU**: ESP32-S3 (no PSRAM variant works fine)
- **Microphone**: INMP441 (I2S digital mic)
- **Amplifier**: MAX98357A (I2S DAC + Class-D amp, drives small speakers directly)
- **Power**: 3.7V LiPo battery

PCB design files and firmware are included. Flashing is integrated into the app: Settings → select serial port → Flash → wait → unplug. Re-flash for firmware updates.

After flashing, the toy boots into hotspot mode automatically — no network credentials to configure.

---

### Voices and Characters

The app ships with multiple character cards (personalities.json), each with its own system prompt and voice. Supported features:

- **Multilingual**: English, Chinese, Spanish, French, Japanese, Korean, Portuguese, German, Italian
- **Voice cloning**: under 10 seconds of reference audio is enough to clone a voice for TTS
- **Custom characters**: edit personalities.json to add new characters, story lines, interaction styles

The built-in cards target children: storytelling, games, educational conversations. But since it's a local LLM, swapping the system prompt transforms it into any format.

---

### Safety Notes

The README explicitly lists three limitations:

1. **Hallucinations**: LLM and TTS models produce incorrect content; do not treat as authoritative
2. **Inappropriate outputs**: adversarial prompts can still produce unsafe responses
3. **Emotional dependency**: AI should not replace real human interaction, especially for children

> "When using with children, use with parental awareness and treat this as a tool for exploration, not authority."

Worth noting — few hardware AI projects volunteer these boundaries up front in the README.

---

### Why This Direction Matters

Children's AI voice toys are a sensitive category: everything a child says, asks, or reveals about their home routine can end up in cloud databases. Parental discomfort is rational.

OpenToys is a direct technical response — not a privacy policy document, but a system where **uploading is physically impossible**: inference is local, WebSocket traffic stays within the toy's AP, there is no outbound network path.

The shift from ElatoAI (cloud) to OpenToys (local) also demonstrates a reproducible path: replace cloud APIs with MLX + Apple Silicon, solve latency and privacy in the same move. 148 stars, MIT, a solid fork starting point for anyone building local AI hardware.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
