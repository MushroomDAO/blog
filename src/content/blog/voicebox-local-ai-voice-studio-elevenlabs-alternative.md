---
title: "Voicebox：把 ElevenLabs 和 WisprFlow 装进一个本地运行的开源 App"
titleEn: "Voicebox: Local-First AI Voice Studio — ElevenLabs Output + WisprFlow Input in One Open-Source App"
description: "jamiepine/voicebox 是一个完全本地运行的 AI 语音工作室，集成 7 种 TTS 引擎（Qwen3-TTS、LuxTTS、Chatterbox、TADA、Kokoro）、Whisper 语音输入、MCP Server 和 Claude Code 集成，支持 Apple Silicon / CUDA / ROCm，MIT 开源。"
descriptionEn: "voicebox is a local-first AI voice studio combining 7 TTS engines (Qwen3-TTS, LuxTTS, Chatterbox, TADA, Kokoro), Whisper STT, an MCP server, and Claude Code integration. Runs fully on-device on Apple Silicon/CUDA/ROCm. MIT licensed."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["AI", "语音合成", "TTS", "本地AI", "开源", "MCP", "Tauri", "Whisper"]
heroImage: "../../assets/images/voicebox-local-ai-voice-studio-banner.jpg"
---

> **GitHub**：[jamiepine/voicebox](https://github.com/jamiepine/voicebox) · MIT  
> **MCP Server port**：17493

---

## 它解决的具体问题

现在市场上有两类工具在吃掉语音 AI 这个场景：

- **ElevenLabs**（语音合成输出）：声音质量好，但要联网，有用量限制，API 密钥泄露有风险
- **WisprFlow**（AI 语音输入/听写）：输入端很好用，但同样是云端服务

Voicebox 把这两个方向合并进一个本地 App：**语音输入（STT）+ 语音合成输出（TTS）+ 完整的语音工作室，全部本地跑，零网络依赖。**

---

## 7 种 TTS 引擎

Voicebox 不绑定任何单一 TTS 模型，而是聚合了当前质量最好的开源 TTS 方案：

| 引擎 | 特点 | 适用场景 |
|---|---|---|
| **Qwen3-TTS 0.6B** | 阿里轻量版，速度快 | 实时对话，低延迟 |
| **Qwen3-TTS 1.7B** | 更高质量 | 内容创作，播客 |
| **Qwen CustomVoice** | 自定义音色克隆 | 品牌声音，角色配音 |
| **LuxTTS** | 高保真，风格可控 | 有声书，专业配音 |
| **Chatterbox Multilingual** | 23 种语言，跨语言克隆 | 多语言内容 |
| **Chatterbox Turbo** | 支持副语言标签（叹气、笑声等） | 情感丰富的语音 |
| **TADA (HumeAI)** | 情感感知 TTS | 对话代理，情绪驱动 |
| **Kokoro 82M** | 轻量高速，50 种预设声音 | 快速原型，轻度用例 |

每个引擎都可以在 UI 里直接切换，不需要单独安装。

---

## STT 输入端：Whisper

语音输入（听写）使用 OpenAI Whisper 和 Whisper Turbo：

- **Whisper Turbo** 是 Whisper Large V3 的加速蒸馏版，速度提升约 8×，质量损失极小
- 全局快捷键触发听写：按下 → 说话 → 松开 → 自动粘贴到当前光标位置（macOS）
- 类似 WisprFlow 的使用体验，但完全本地

---

## MCP Server：让 Agent 开口说话

Voicebox 内置一个 MCP Server，运行在 `http://127.0.0.1:17493/mcp`，让任何支持 MCP 的 AI 工具都可以调用语音合成：

**在 Claude Code 里添加 Voicebox MCP：**

```bash
claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp
```

**调用示例：**

```json
{
  "tool": "voicebox_speak",
  "args": {
    "text": "任务已完成，共修改 3 个文件",
    "engine": "qwen3-tts-1.7b",
    "voice": "default"
  }
}
```

这意味着 Claude Code 在跑完一个长任务后可以直接"开口"告诉你结果——不用一直盯着屏幕等进度。

---

## 技术架构

```
Voicebox
├── UI Layer         — Tauri (Rust) + React
├── API Layer        — FastAPI (Python) + SQLite
├── Models Layer
│   ├── TTS         — Qwen3-TTS, LuxTTS, Chatterbox, TADA, Kokoro
│   └── STT         — Whisper, Whisper Turbo
├── Hardware Backend
│   ├── Apple Silicon — MLX + Metal
│   ├── NVIDIA        — CUDA
│   ├── AMD           — ROCm
│   ├── Intel Arc     — DirectML
│   └── CPU           — 通用回退
└── MCP Server      — HTTP 17493 端口
```

**Tauri** 负责原生桌面外壳（比 Electron 轻很多，Rust 写的），**FastAPI** 负责 Python 模型调用，两者通过本地 HTTP 通信。这个架构让 Python ML 生态的所有模型都可以接进来，同时保持桌面 App 的原生体验。

---

## Stories 编辑器：多轨音频

除了单次 TTS 转换，Voicebox 还有一个 Stories 编辑器，支持多轨音频制作：

- 多个角色/声音轨道
- 时间线排列
- 后处理特效（基于 Spotify pedalboard 库）：均衡、混响、压缩等

适合做播客、有声书、AI 语音广告等内容。

---

## 快速上手

```bash
git clone https://github.com/jamiepine/voicebox.git
cd voicebox

# 安装依赖（需要 Rust + Node + Python）
npm install
pip install -r requirements.txt

# 启动（会自动下载所选 TTS 模型）
npm run tauri dev
```

首次运行会根据你选择的引擎下载模型，Kokoro（82M）几秒搞定，Qwen3-TTS 1.7B 需要一分钟。模型下载完成后完全离线运行。

**MCP 集成（Claude Code）：**

```bash
# 先启动 Voicebox（确保 MCP Server 在 17493 端口运行）
# 然后：
claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp

# 验证
claude mcp list
```

---

## 和 ElevenLabs 的对比

| 维度 | Voicebox | ElevenLabs |
|---|---|---|
| 价格 | 免费（开源） | $5-$99/月 |
| 隐私 | 完全本地 | 音频上传云端 |
| 延迟 | 本地推理（Apple M系 约 0.5-2秒） | 网络 + 生成延迟 |
| 语音克隆 | Qwen CustomVoice + Chatterbox | 更成熟 |
| 多语言 | 23 种（Chatterbox） | 30+ 种 |
| API / 集成 | MCP Server + REST API | 完整 API |
| 声音库 | 50 预设（Kokoro）+ 可克隆 | 数千个声音 |

如果你的核心需求是隐私、零成本或 AI Agent 语音输出，Voicebox 是更合适的选择。如果你需要生产级的声音克隆质量或商业授权的 voice library，ElevenLabs 目前还是领先。

---

## 最有意思的使用场景

**Claude Code 语音播报**：跑完大型重构或测试套件，让 Claude Code 通过 Voicebox MCP 说出结果。不用死盯屏幕，可以在另一个屏幕做别的事。

**本地有声书制作**：用 LuxTTS 或 Chatterbox 把长文档/文章直接转为音频，在通勤时听。全流程本地，不受字符限制。

**多语言内容创作**：Chatterbox Multilingual 支持 23 种语言，并且可以在语言间克隆音色，同一个"声音"说英语、中文、西班牙语。

**情感对话代理**：TADA (HumeAI) 和 Chatterbox Turbo 支持副语言标签（叹气、犹豫、笑声），让 AI 的语音输出更接近真实对话。

---

## 一句话总结

Voicebox 是目前开源生态里架构最完整的本地语音 AI 工作室：输入（Whisper）+ 输出（7 种 TTS）+ Agent 集成（MCP Server）三个关键环节都覆盖了。如果你在构建语音驱动的 AI 工作流，这个项目值得认真看一下。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Voicebox: Local-First AI Voice Studio — ElevenLabs + WisprFlow Alternative

**GitHub**: [jamiepine/voicebox](https://github.com/jamiepine/voicebox) · MIT

### What It Is

Voicebox is an open-source, fully local AI voice studio that combines:
- **Speech-to-text input** (Whisper / Whisper Turbo) — like WisprFlow
- **Text-to-speech output** (7 engines) — like ElevenLabs
- **MCP Server** — voice output for AI agents (Claude Code, Cursor)

Everything runs on-device. No API keys, no usage limits, no audio upload.

### 7 TTS Engines

| Engine | Highlight |
|---|---|
| Qwen3-TTS 0.6B / 1.7B | Alibaba models; fast to high-quality |
| Qwen CustomVoice | Voice cloning |
| LuxTTS | High-fidelity, style-controllable |
| Chatterbox Multilingual | 23 languages, cross-lingual voice cloning |
| Chatterbox Turbo | Paralinguistic tags (sighs, laughs) |
| TADA (HumeAI) | Emotion-aware TTS |
| Kokoro 82M | Ultra-light, 50 preset voices |

### MCP Server for AI Agents

Voicebox runs an MCP server at `http://127.0.0.1:17493/mcp`. Add it to Claude Code:

```bash
claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp
```

Claude Code can then speak task results aloud — useful for long-running tasks where you don't want to monitor the terminal.

### Architecture

Tauri (Rust) desktop shell + React frontend + FastAPI (Python) for model inference + SQLite. Hardware backends: MLX (Apple Silicon), CUDA (NVIDIA), ROCm (AMD), DirectML (Intel Arc), CPU fallback.

### Quick Start

```bash
git clone https://github.com/jamiepine/voicebox.git
cd voicebox
npm install && pip install -r requirements.txt
npm run tauri dev
# First launch downloads selected models; Kokoro (82M) takes seconds; Qwen3 1.7B ~1 min
```

### Stories Editor

Multi-track audio production with timeline layout, multiple character voices, and post-processing effects via Spotify pedalboard (EQ, reverb, compression).

### Bottom Line

Voicebox covers the full local voice AI stack: STT input + TTS output + MCP agent integration. If you're building voice-driven AI workflows or want an ElevenLabs alternative that keeps audio on-device, this is the most complete open-source option available.

© 2026 Author: Mycelium Protocol
