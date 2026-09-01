---
title: "VoiceStudio：本地运行的 ElevenLabs 替代品，16 个 TTS 引擎，646 种语言"
titleEn: "VoiceStudio: Local-First ElevenLabs Alternative — 16 TTS Engines, 646 Languages"
description: "debpalash/VoiceStudio ⭐12712，开源全本地语音工作台，16 个 TTS 引擎、11 个 ASR 引擎、646 语言目录，覆盖声音克隆、声音设计、视频配音、转录、故事和 Audiobook，桌面端 + REST/WebSocket/OpenAI 兼容 API + MCP Server，AGPL-3.0。"
descriptionEn: "debpalash/VoiceStudio ⭐12712 — open-source fully-local voice workstation: 16 TTS engines, 11 ASR engines, 646-language catalogue, covering voice cloning, voice design, video dubbing, dictation, stories, and audiobooks. Desktop app + REST/WebSocket/OpenAI-compatible API + MCP Server, AGPL-3.0."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Tech-News"
tags: ["TTS", "ASR", "voice cloning", "local AI", "open source", "ElevenLabs", "audio", "speech", "MCP", "dubbing", "audiobook"]
heroImage: "../../assets/images/voicestudio-local-elevenlabs-alternative-646-languages-16-tts-11-asr-banner.jpg"
author: "Mycelium Protocol"
---

## 本地运行的语音工作台

ElevenLabs 的核心能力——声音克隆、视频配音、Audiobook 生成——你现在可以在自己的机器上跑，不需要账号、API Key、订阅，也没有用量计费。

**VoiceStudio**（曾用名 OmniVoice-Studio）是一个开源、全本地的语音工作台，把 16 个 TTS 引擎和 11 个 ASR 引擎统一到一个桌面应用里，支持 646 种语言，覆盖语音 AI 的六个核心工作流。

⭐ **12,712**，fork **1,969**，AGPL-3.0，Python + Bun/Tauri 构建，持续更新到 2026 年 8 月。

---

## 六个工作流

| 工作流 | 能做什么 |
|---|---|
| **声音克隆** | 3-15 秒参考片段，零样本克隆目标声音 |
| **声音设计** | 从年龄、口音、音调、风格、表达方式描述生成全新声音 |
| **视频配音** | 转录 → 翻译 → 保持说话人 → 合成 → 导出视频 |
| **转录 / 听写** | 系统全局快捷键，实时转录，可选本地 LLM 润色 |
| **故事与 Audiobook** | 多声音脚本、EPUB/PDF 导入、章节渲染、`.m4b` 导出 |
| **批量队列** | 大规模音频和视频任务并行处理，逐任务进度追踪 |

核心数据路径是本地的——音频和文字不经过任何第三方服务器。联网功能（远程 worker、模型下载）是明确的可选项，不是默认行为。

---

## 引擎生态：16 TTS + 11 ASR

VoiceStudio 的竞争优势不是一个单一模型，而是把当前最好的开源语音模型统一到一个界面里，按需安装、随时切换（`Ctrl/Cmd+E`）。

### TTS 引擎（16 个）

| 引擎 | 语言数 | 声音克隆 | macOS ARM | 许可 |
|---|:---:|:---:|:---:|---|
| **VoiceStudio**（默认，基于 k2-fsa/OmniVoice） | 600+ | ✅ | MPS | AGPL-3.0 / Apache-2.0 |
| **OmniVoice GGUF** | 600+ | ✅ | MPS/CPU | AGPL-3.0 / Apache-2.0 |
| **CosyVoice 3** | 9+18方言 | ✅ | CPU | Apache-2.0 |
| **GPT-SoVITS** | 5 | ✅ | — | MIT |
| **VoxCPM2** | 30 | ✅ | MPS | Apache-2.0 |
| **IndexTTS 2.5** | ZH/EN/JA/ES/AR | ✅ | CPU | Bilibili 模型许可 |
| **MLX-Audio** | 模型相关 | 部分 | MLX | 各异 |
| **MOSS-TTS-Nano** | 20 | ✅ | CPU | Apache-2.0 |
| **Sherpa-ONNX** | 20+ | — | CPU | Apache-2.0 |
| **KittenTTS** | 英语 | — | CPU | MIT |
| **PocketTTS** | 6种欧洲语言 | ✅ | CPU | CC-BY-4.0（需授权） |
| **Supertonic 3** | 31 | — | CPU | OpenRAIL-M |
| **MOSS-TTS-v1.5** | 31 | ✅ | CPU | Apache-2.0 |
| **dots.tts** | 24 | ✅ | CPU | Apache-2.0 |
| **Confucius4-TTS** | 14 | ✅ | CPU | Apache-2.0 |
| **MOSS-TTS-v1.5** | 31 | ✅ | CPU | Apache-2.0 |

默认引擎 VoiceStudio（OmniVoice）支持 600+ 语言、声音克隆、指令式合成，是开箱即用的最全能选项。没有克隆能力的引擎在视频配音和固定声音批量任务里会被直接拒绝（而不是悄悄换引擎），确保输出的可预期性。

### ASR 引擎（11 个）

涵盖 Whisper 系列、WhisperX、Pyannote 说话人分离、实时流式识别等，配合 TTS 引擎构成完整的语音处理管线。

---

## 技术架构

| 层 | 技术 |
|---|---|
| 前端 / 桌面 | Tauri + Bun（TypeScript） |
| 后端 | Python（uv 管理依赖） |
| 计算 | CUDA · Apple Silicon MPS/MLX · ROCm · CPU |
| 接口 | 本地 REST/SSE/WebSocket API · OpenAI 兼容音频 API · MCP Server |
| 模型管理 | 内置 Model Catalogue，在线安装/卸载/路由，支持远程 Worker |

**MCP Server** 是一个值得关注的细节：VoiceStudio 暴露合成和转录工具给任何 MCP 客户端（Claude、Cursor 等），意味着你可以在 AI 编码工具里直接调用本地语音合成——不用离开工作区。

---

## 对比 ElevenLabs

| | **VoiceStudio** | **ElevenLabs** |
|---|---|---|
| **数据路径** | 本地（音频和文字不出机器） | 经过 ElevenLabs 服务器 |
| **费用** | 免费（你提供算力） | 订阅 / 按用量计费 |
| **离线使用** | ✅（模型下载后） | ❌ |
| **引擎选择** | 16 个 TTS + 11 个 ASR | 闭源，固定 |
| **语言支持** | 646 种（取决于引擎） | 32 种 |
| **定制性** | 开源、可改引擎、可改路由 | 有限 |
| **维护** | 你自己管更新和算力 | 供应商管基础设施 |

适合 VoiceStudio 的场景：**私有数据（法律/医疗/企业内容）、离线环境、高频批量生产（不想按量付费）、自研工作流集成**。

---

## 硬件需求

| | 最低 | 推荐 |
|---|---|---|
| **OS** | Windows 10 x64 · macOS 13.3+ Apple Silicon · Linux x86_64 | 当前系统版本 |
| **RAM** | 8 GB | 16 GB+ |
| **磁盘** | 10 GB | 20 GB+ SSD |
| **GPU** | 可选（支持纯 CPU 模式）| NVIDIA CUDA 或 Apple Silicon |
| **VRAM** | 4 GB（使用 GPU 时）| 8 GB+（大型引擎更多）|

注意：**Intel Mac 无法运行本地 Python 后端**，只能连接远程 Worker。Apple Silicon 是 macOS 上的原生平台。

---

## 安装与快速开始

从 [GitHub Releases](https://github.com/debpalash/VoiceStudio/releases/latest) 下载对应平台的安装包（DMG / MSI / AppImage），首次启动自动创建 Python 环境并下载默认模型，后续启动复用缓存。

**首次声音克隆三步**：
1. 打开 VoiceStudio → **Voice Cloning**
2. 上传干净的参考音频（3 秒可用，5-15 秒效果更好）
3. 输入文字，选语言，点 **Generate**

**从源码运行**：
```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run desktop       # 桌面端
# bun run dev         # 浏览器 UI
```

---

## 总结

VoiceStudio 做了一件看起来简单但执行门槛很高的事：把语音 AI 的主流开源模型（16 个 TTS、11 个 ASR）统一到一个本地桌面应用里，覆盖从声音克隆到 Audiobook 生产的完整工作流，并暴露 OpenAI 兼容 API 和 MCP Server 给工具链集成。

12k Star，1.9k Fork，ElevenLabs 的替代品——不是功能对等，而是本地优先、数据自控、不按量计费。

**GitHub**: [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) ⭐12712  
**官网**: [voicestudio.sh](https://voicestudio.sh)  
**Discord**: [discord.gg/bzQavDfVV9](https://discord.gg/bzQavDfVV9)  
**许可**: AGPL-3.0

<!--EN-->

## VoiceStudio: Local-First ElevenLabs Alternative

ElevenLabs' core capabilities — voice cloning, video dubbing, audiobook generation — can now run on your own machine, with no account, API key, subscription, or usage meter.

**VoiceStudio** (formerly OmniVoice-Studio) is an open-source, fully-local voice workstation that unifies 16 TTS engines and 11 ASR engines in a single desktop app, supports 646 languages, and covers six core voice AI workflows.

⭐**12,712**, **1,969** forks, AGPL-3.0, Python + Bun/Tauri, actively updated through August 2026.

---

## Six Workflows

| Workflow | What it does |
|---|---|
| **Voice Cloning** | Zero-shot clone from a 3–15 second reference clip |
| **Voice Design** | Generate a new voice from age, accent, pitch, style, and delivery instructions |
| **Video Dubbing** | Transcribe → translate → preserve speakers → synthesize → export video |
| **Dictation** | System-wide shortcut, live transcription, optional local LLM cleanup |
| **Stories & Audiobooks** | Multi-voice scripts, EPUB/PDF import, chapter rendering, `.m4b` export |
| **Batch Queue** | Large-scale audio and video job processing with per-job progress tracking |

The core data path is local — audio and text never reach a third-party server. Network-backed features (remote workers, model downloads) are explicit opt-ins, not defaults.

---

## Engine Ecosystem: 16 TTS + 11 ASR

VoiceStudio's competitive advantage isn't a single model — it's unifying the best open-source voice models into one interface with on-demand installation and instant switching (`Ctrl/Cmd+E`).

### TTS Engines (16)

The default engine — VoiceStudio (powered by k2-fsa/OmniVoice) — supports 600+ languages, voice cloning, and instruction-driven synthesis. Engines without cloning support are rejected rather than silently swapped in dubbing and pinned-voice batch jobs, keeping outputs predictable.

Key highlights:
- **OmniVoice / OmniVoice GGUF** — 600+ languages, clone + instruct, Apple Silicon MPS support
- **CosyVoice 3** — 9 languages + 18 Chinese dialects, clone + instruct
- **GPT-SoVITS** — MIT, 5 languages, popular for high-quality clone
- **IndexTTS 2.5** — Chinese/English/Japanese/Spanish/Arabic
- **MLX-Audio** — MLX native on Apple Silicon
- **Sherpa-ONNX** — lightweight, 20+ languages, CPU-first

### ASR Engines (11)

Covers Whisper variants, WhisperX with speaker diarization (Pyannote), real-time streaming recognition, and more — a full audio processing pipeline alongside TTS.

---

## Technical Architecture

| Layer | Technology |
|---|---|
| Frontend / Desktop | Tauri + Bun (TypeScript) |
| Backend | Python (uv-managed) |
| Compute | CUDA · Apple Silicon MPS/MLX · ROCm · CPU |
| Interfaces | Local REST/SSE/WebSocket API · OpenAI-compatible audio API · MCP Server |
| Model management | Built-in Model Catalogue: install/remove/route, remote worker support |

**MCP Server** is worth highlighting: VoiceStudio exposes synthesis and transcription tools to any MCP client (Claude, Cursor, etc.), letting you call local voice synthesis directly from within AI coding tools — without leaving your workspace.

---

## Compared to ElevenLabs

| | **VoiceStudio** | **ElevenLabs** |
|---|---|---|
| **Data path** | Local by default | Processed by ElevenLabs servers |
| **Cost** | Free (you supply compute) | Subscription or metered API |
| **Offline** | ✅ after model download | ❌ |
| **Engine choice** | 16 TTS + 11 ASR | Closed-source, fixed |
| **Language support** | 646 (engine-dependent) | 32 |
| **Customization** | Open source, swap engines, modify routing | Provider-limited |
| **Maintenance** | You manage updates and compute | Provider manages infrastructure |

Best fit for VoiceStudio: **private data (legal, medical, enterprise), offline environments, high-volume batch production (no per-character billing), and custom toolchain integration.**

---

## Hardware Requirements

| | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10 x64 · macOS 13.3+ Apple Silicon · Linux x86_64 | Current supported OS release |
| **RAM** | 8 GB | 16 GB+ |
| **Disk** | 10 GB | 20 GB+ SSD |
| **GPU** | Optional (CPU mode supported) | NVIDIA CUDA or Apple Silicon |
| **VRAM** | 4 GB if using GPU | 8 GB+ (large engines need more) |

Note: **Intel Macs cannot run the local Python backend** — connect a remote worker instead. Apple Silicon is the native macOS platform.

---

## Install and Quick Start

Download the installer for your platform from [GitHub Releases](https://github.com/debpalash/VoiceStudio/releases/latest) (DMG / MSI / AppImage). First launch creates a managed Python environment and downloads the default model; subsequent launches reuse the cache.

**First voice clone in three steps:**
1. Open VoiceStudio → **Voice Cloning**
2. Add a clean reference clip (3 seconds works; 5–15 seconds usually better)
3. Enter text, choose a language, click **Generate**

**Run from source:**
```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run desktop    # desktop app
# bun run dev      # browser UI
```

---

## Summary

VoiceStudio does something that sounds simple but has a high execution bar: it unifies the major open-source voice models (16 TTS, 11 ASR) into a local desktop app covering the complete workflow from voice cloning to audiobook production, then exposes an OpenAI-compatible API and MCP Server for toolchain integration.

12k stars, 1.9k forks. An ElevenLabs alternative — not feature-parity in every edge case, but local-first, data-controlled, and no per-character billing.

**GitHub**: [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) ⭐12712  
**Website**: [voicestudio.sh](https://voicestudio.sh)  
**Discord**: [discord.gg/bzQavDfVV9](https://discord.gg/bzQavDfVV9)  
**License**: AGPL-3.0
