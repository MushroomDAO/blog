---
title: 'VoiceStudio：24.8K Stars 的本地 ElevenLabs 替代方案，16 个 TTS 引擎跑在你的机器上'
titleEn: "VoiceStudio: 24.8K-Star Local ElevenLabs Alternative Running 16 TTS Engines on Your Machine"
description: "AGPL-3.0 开源，无账号无订阅无计费，646 种语言，语音克隆 3 秒起步，视频配音、有声书、MCP Server 全齐——这是目前功能最完整的本地语音 AI 工具之一。但默认引擎权重是 CC-BY-NC，商用前必须核查。"
descriptionEn: "AGPL-3.0, no account no subscription no metering, 646 languages, voice cloning from 3 seconds, video dubbing, audiobooks, MCP Server all included — one of the most complete local voice AI tools available. But default engine weights are CC-BY-NC: check before commercial use."
pubDate: "2026-09-13"
updatedDate: "2026-09-13"
category: "Tech-News"
tags: ["TTS", "voice-cloning", "open-source", "local-AI", "ElevenLabs", "audio-AI", "VoiceStudio"]
heroImage: "../../assets/voicestudio-local-elevenlabs-alternative-tts-banner.jpg"
---

> 📌 开源仓库：debpalash/VoiceStudio
> GitHub：https://github.com/debpalash/VoiceStudio
> 官网：https://voicestudio.sh
> License：AGPL-3.0（应用层）| Stars：24.8K+
> 原名：OmniVoice-Studio

---

ElevenLabs 的问题不是技术不行，而是你的声音、你的文本、你的配音项目全部经过他们的服务器。对于需要隐私保护的内容、高频生成场景、或者单纯不想被按 token 计费的用户，这是一个真实的痛点。

VoiceStudio 就是针对这个痛点做的：功能对标 ElevenLabs，全部跑在本地，无账号、无 API key、无订阅、无用量计费。

目前 24.8K stars，2026 年 4 月创建，5 个月到这个量级，说明需求是真实的。

---

## 一、能做什么：六个工作流

**语音克隆**：上传 3 秒以上的参考音频，选语言，输入文字，生成。5-15 秒的参考音频通常效果更好。支持多人对话录音分离后分别克隆不同说话人。

**语音设计**：不需要参考录音，用文字描述声音。"清晰权威的美式播音腔"、"温暖有表现力的英式有声书叙述者"——VoiceStudio 会生成对应特征的声音。这是 ElevenLabs 的 Voice Design 功能的本地复刻。

**视频配音**：上传视频或填 URL → 自动转录 → 翻译 → 保留原始说话人 → 合成新语言的配音 → 导出。Demo 包含西班牙语、法语、日语、中文的输出样本。

**故事与有声书**：多声部脚本编辑器，支持 EPUB/PDF 导入，按章节渲染，导出 `.m4b` 格式（标准有声书格式，支持章节跳转）。

**听写组件**：系统级快捷键触发，实时语音转文字，可选接本地 LLM 做文本清理和纠错。

**批量队列**：大批量音频/视频任务，支持监听本地文件夹（新文件进来自动处理）。

---

## 二、引擎生态：16 TTS + 11 ASR，按硬件选

VoiceStudio 的设计是引擎注册表，不绑定单一模型。16 个 TTS 引擎、11 个 ASR 引擎，按硬件选最合适的：

**Apple Silicon 推荐配置**：
- TTS：MLX-Audio + OmniVoice (MPS)
- ASR：MLX Whisper + Parakeet MLX
- 理由：原生统一内存，macOS 上延迟最低

**NVIDIA GPU 8GB+ 推荐配置**：
- TTS：OmniVoice + CosyVoice 3（9 语言 + 18 方言）
- ASR：WhisperX（词级时间戳 + 说话人分离）
- 理由：高保真零样本克隆，完整 diarization 支持

**CPU 低配 / 低显存**：
- TTS：PocketTTS + Sherpa-ONNX + KittenTTS
- ASR：Moonshine（低功耗 ONNX）+ Faster-Whisper int8
- 理由：内存占用低，CPU 推理有专项优化

---

## 三、架构层：Tauri + FastAPI + 引擎注册表

```
Tauri v2 桌面壳（Rust）
    │ IPC
React + Vite UI
    │ HTTP / SSE / WebSocket（localhost:3900）
FastAPI 后端
    ├── TTS / ASR 引擎注册表
    ├── 配音 / 音频 / 长音频流水线
    ├── OpenAI 兼容音频 API
    ├── MCP Server
    └── SQLite + Alembic → omnivoice_data/
```

几个值得关注的接口：

**OpenAI 兼容音频 API**：意味着任何接受 OpenAI TTS API 的客户端或工具，直接把 base_url 指向 localhost:3900，就能用本地引擎生成语音，不需要改代码。

**MCP Server**：暴露合成和转写工具给 MCP 客户端。可以在 Claude Code、Cursor 等 MCP 支持的工具里直接调用 VoiceStudio 的语音功能，不需要打开桌面 App。

---

## 四、许可证的真实情况（必读）

应用层是 AGPL-3.0，这是开源的。但**模型权重各有各的授权**：

- **默认引擎 OmniVoice（k2-fsa）**：代码 Apache-2.0，权重 **CC-BY-NC**——非商业使用
- **CosyVoice 3**：Apache-2.0，商用友好
- **GPT-SoVITS**：MIT，商用友好
- **IndexTTS 2.5**：Bilibili 商业许可——月活 1 亿以上或年收入 10 亿元以上需要另签协议
- **PocketTTS**：CC-BY-4.0，首次使用前有 gated 确认

OmniVoice 还包含一个音频分词器，分别是 Boson Higgs Audio 2 和 Meta Llama 社区协议。

**结论**：个人使用和学习，AGPL-3.0 + 主流引擎都没问题。商业场景，逐个核查你打算用的引擎的权重协议。

---

## 五、安装

**macOS（Apple Silicon，推荐）**：

从 GitHub releases 下载 DMG，首次启动需要右键→打开（绕过 Gatekeeper）。首次启动会自动创建 Python 环境并下载默认模型。

Intel Mac 不能跑本地 Python 后端，需配远程后端。

**从源码跑**：

```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run desktop  # 桌面 App
# 或
bun run dev  # 浏览器 UI
```

需要 Node 20+/Bun 和 Python 3.11+。Python 依赖首次运行由 `uv` 自动安装。

**Docker（Linux/AMD64 only）**：

```bash
docker run -d -p 127.0.0.1:3900:3900 \
  -v omnivoice-data:/app/omnivoice_data \
  --name voicestudio \
  palashdeb/omnivoice-studio:stable
```

Docker 镜像仅 `linux/amd64`，Apple Silicon 用宿主机原生 App。

---

## 六、几个值得关注的细节

**Electron 重写中**：README 顶部有警告——桌面端正在从 Tauri 迁移到 Electron，桌面 App 相关的 issue 和 PR 暂停接收。这个阶段如果遇到桌面端问题，先确认是否是重写期间的已知问题。

**之前叫 OmniVoice-Studio**：Docker 镜像名还是 `palashdeb/omnivoice-studio`，不是 `voicestudio`。用 Docker 的时候注意镜像名。

**Google Colab 可以先试**：仓库提供了 Colab notebook，不用本地安装就能体验输出效果。先试效果再决定要不要本地部署。

---

## 拆解结论

VoiceStudio 的覆盖面是目前本地语音 AI 工具里最宽的之一：克隆、设计、配音、有声书、听写、MCP、OpenAI 兼容 API，都在同一个工具里。五个月 24.8K stars 不是靠噱头，是因为功能填补了一个真实的空缺——ElevenLabs 能做的事情，大部分可以本地跑。

不足：默认引擎权重是 CC-BY-NC，这是商用的硬约束。桌面端架构还在重写中，这个阶段稳定性存疑。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: debpalash/VoiceStudio
> GitHub: https://github.com/debpalash/VoiceStudio
> Website: https://voicestudio.sh
> License: AGPL-3.0 (application layer) | Stars: 24.8K+
> Formerly: OmniVoice-Studio

---

ElevenLabs' limitation isn't technical quality — it's that your voice samples, your text, your dubbing projects all pass through their servers. For privacy-sensitive content, high-volume generation, or simply not wanting to be charged per token, that's a real pain point.

VoiceStudio targets exactly that: feature-comparable to ElevenLabs, running entirely local, with no account, no API key, no subscription, no usage meter.

24.8K stars, created April 2026, reaching this scale in five months signals genuine demand.

---

## I. Six Workflows

**Voice Cloning**: Upload 3+ seconds of reference audio, pick a language, enter text, generate. 5–15 seconds usually gives better results. Multi-party recordings can be separated by speaker and cloned independently.

**Voice Design**: No reference recording needed — describe the voice in text. "Clear, authoritative American broadcast tone." "Warm, expressive British audiobook narrator." VoiceStudio generates a voice matching those characteristics. This is a local reproduction of ElevenLabs' Voice Design feature.

**Video Dubbing**: Upload a video or paste a URL → auto-transcribe → translate → preserve original speakers → synthesize in the target language → export. Demo samples include Spanish, French, Japanese, and Chinese outputs.

**Stories and Audiobooks**: Multi-voice script editor, EPUB/PDF import, chapter-level rendering, `.m4b` export (standard audiobook format with chapter navigation).

**Dictation Widget**: System-wide keyboard shortcut, live transcription, optional local LLM for text cleanup and correction.

**Batch Queue**: Large audio/video job sets with per-job progress; local folder watching processes new files automatically.

---

## II. Engine Ecosystem: 16 TTS + 11 ASR, Pick by Hardware

VoiceStudio uses an engine registry architecture — no single model binding. 16 TTS engines, 11 ASR engines. Recommended configurations:

**Apple Silicon:**
- TTS: MLX-Audio + OmniVoice (MPS)
- ASR: MLX Whisper + Parakeet MLX
- Why: native unified memory, lowest latency on macOS

**NVIDIA GPU 8GB+:**
- TTS: OmniVoice + CosyVoice 3 (9 languages + 18 dialects)
- ASR: WhisperX (word-level timestamps + diarization)
- Why: high-fidelity zero-shot cloning, full diarization support

**CPU / Low VRAM:**
- TTS: PocketTTS + Sherpa-ONNX + KittenTTS
- ASR: Moonshine (low-power ONNX) + Faster-Whisper int8
- Why: low memory footprint, CPU-optimized inference

---

## III. Architecture: Tauri + FastAPI + Engine Registry

```
Tauri v2 desktop shell (Rust)
    │ IPC
React + Vite UI
    │ HTTP / SSE / WebSocket (localhost:3900)
FastAPI backend
    ├── TTS / ASR engine registries
    ├── dubbing / audio / long-form pipelines
    ├── OpenAI-compatible audio API
    ├── MCP Server
    └── SQLite + Alembic → omnivoice_data/
```

Two interfaces worth calling out:

**OpenAI-compatible audio API**: Any client or tool that accepts OpenAI's TTS API can point its base_url at localhost:3900 and use local engines — no code changes needed.

**MCP Server**: Exposes synthesis and transcription tools to MCP clients. You can invoke VoiceStudio voice functions from Claude Code, Cursor, or any MCP-enabled tool without opening the desktop app.

---

## IV. License Reality Check (Read This)

The application is AGPL-3.0 — that's open source. But **model weights have their own terms**:

- **Default engine OmniVoice (k2-fsa)**: code Apache-2.0, weights **CC-BY-NC** — non-commercial only
- **CosyVoice 3**: Apache-2.0 — commercial-friendly
- **GPT-SoVITS**: MIT — commercial-friendly
- **IndexTTS 2.5**: Bilibili commercial license — written agreement required above 100M MAU or ¥1B annual revenue
- **PocketTTS**: CC-BY-4.0, gated confirmation on first use

OmniVoice also bundles an audio tokenizer under separate Boson Higgs Audio 2 and Meta Llama community terms.

**Bottom line**: personal use and learning, AGPL-3.0 + mainstream engines are fine. Commercial use: check the weight license for each engine you intend to deploy.

---

## V. Install

**macOS (Apple Silicon, recommended):**

Download the DMG from GitHub releases. First launch requires right-click → Open (bypasses Gatekeeper). The Python environment and default model download automatically on first run.

Intel Macs can't run the local Python backend — use a remote backend instead.

**From source:**

```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run desktop  # desktop app
# or
bun run dev      # browser UI
```

Requires Node 20+/Bun and Python 3.11+. Python dependencies are auto-installed by `uv` on first run.

**Docker (Linux/AMD64 only):**

```bash
docker run -d -p 127.0.0.1:3900:3900 \
  -v omnivoice-data:/app/omnivoice_data \
  --name voicestudio \
  palashdeb/omnivoice-studio:stable
```

Docker images are `linux/amd64` only — Apple Silicon users should use the native app.

---

## VI. Details Worth Noting

**Electron rewrite in progress**: The README has a warning at the top — the desktop is migrating from Tauri to Electron. Desktop app issues and PRs are currently on hold. If you hit desktop problems, check whether it's a known mid-rewrite issue first.

**Formerly OmniVoice-Studio**: The Docker image is still `palashdeb/omnivoice-studio`, not `voicestudio`. Keep that in mind if you're using Docker.

**Try on Colab first**: The repo includes a Colab notebook — test output quality without local setup before deciding whether to deploy.

---

## Teardown Summary

VoiceStudio's coverage is among the widest of any local voice AI tool right now: cloning, design, dubbing, audiobooks, dictation, MCP, OpenAI-compatible API — all in one tool. 24.8K stars in five months isn't hype; it fills a real gap. Most of what ElevenLabs does can run locally.

Limitations: default engine weights are CC-BY-NC — a hard constraint for commercial use. The desktop architecture is mid-rewrite, which means stability during this period is an open question.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
