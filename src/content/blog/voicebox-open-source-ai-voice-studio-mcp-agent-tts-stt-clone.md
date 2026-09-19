---
title: "用开源 Voicebox 给 AI Agent 装上嗓子 — MCP 语音层工程实践"
titleEn: "Give Your AI Agent a Voice with Open-Source Voicebox — MCP Voice Layer in Practice"
description: "jamiepine/voicebox，55K stars，MIT，Tauri+Python 桌面应用，内置 MCP server 直连 Claude Code/Cursor/Windsurf。7 款本地 TTS 引擎（Qwen3-TTS、Chatterbox、Kokoro 等）+ Whisper STT + 零样本声音克隆，全程本地推理，完全私有。一行命令让 Agent 开口说话。"
descriptionEn: "jamiepine/voicebox, 55K stars, MIT, Tauri+Python desktop app with a built-in MCP server for Claude Code, Cursor, and Windsurf. Seven local TTS engines (Qwen3-TTS, Chatterbox, Kokoro, etc.) + Whisper STT + zero-shot voice cloning, all running locally. One command to give your agent a voice."
pubDate: "2026-09-19"
updatedDate: "2026-09-19"
category: "Tech-Experiment"
tags: ["voice-AI", "TTS", "MCP", "AI-Agent", "Voicebox", "local-AI", "Whisper", "voice-clone", "Claude-Code"]
heroImage: "../../assets/images/voicebox-open-source-ai-voice-studio-mcp-agent-tts-stt-clone-banner.jpg"
---

> 📌 GitHub：https://github.com/jamiepine/voicebox
> Stars：55,125 | License：MIT | 语言：TypeScript + Python（Tauri 桌面）
> 发布：2026-01-25 | 官网：https://voicebox.sh

---

Agent 在终端里跑任务，你盯着屏幕等结果。如果 Agent 完成了能直接开口说"部署完成，没有报错"，或者你对着麦克风说"帮我看看这个 PR"，Agent 立刻听懂并开干——这不是科幻，是现在可以装上去的工程能力。

Voicebox 是这套语音层最直接的开源实现：55K stars，MIT 协议，本地跑，内置 MCP server，对接 Claude Code/Cursor/Windsurf 只需要一行配置。

---

## 它是什么

Voicebox 是一个**本地优先的 AI 语音工作室**，定位是 ElevenLabs + WisprFlow 的开源替代品，把 TTS、STT、声音克隆、Agent 语音集成打包进一个桌面应用。

核心是两件事：

1. **给 Agent 装嘴（TTS）**：Agent 执行任务时，可以通过 MCP 工具调用，让 Voicebox 用任意克隆声音念出来
2. **给 Agent 装耳朵（STT）**：全局快捷键推送话音，Whisper 转文字，可选 LLM 润色，输入到任意文本框

两者都完全本地推理，音频数据不出本机。

---

## 内置 MCP Server：一行接入

这是 Voicebox 对 AI Agent 最有价值的部分——它内置了一个 HTTP MCP server，跑在 `http://127.0.0.1:17493/mcp`，不需要额外部署。

**接入 Claude Code：**

```bash
claude mcp add voicebox \
  --transport http \
  --url http://127.0.0.1:17493/mcp \
  --header "X-Voicebox-Client-Id: claude-code"
```

**接入 Cursor / Windsurf / VS Code（`mcp.json`）：**

```json
{
  "mcpServers": {
    "voicebox": {
      "url": "http://127.0.0.1:17493/mcp",
      "headers": { "X-Voicebox-Client-Id": "cursor" }
    }
  }
}
```

`X-Voicebox-Client-Id` 是 Voicebox 识别来源客户端的标识，配合**每客户端声音绑定（Per-Client Voice Binding）**使用——可以在 Settings → MCP 里指定"Claude Code 说话用 Morgan 声音，Cursor 用 Jarvis 声音"，各客户端互不干扰。

**MCP 工具清单：**

| 工具 | 功能 |
|------|------|
| `voicebox.speak` | Agent 语音输出，可选 personality 改写 |
| `voicebox.transcribe` | 音频转文字 |
| `voicebox.list_captures` | 浏览历史录音和转录 |
| `voicebox.list_profiles` | 列出可用声音配置 |

Agent 使用示例（Claude Code 里）：

```javascript
await voicebox.speak({
  text: "Tests passing. Ready to merge.",
  profile: "Morgan",      // 可选，默认用该客户端绑定的声音
  personality: true,      // 可选，先过 personality LLM 改写语气再念
});
```

---

## 7 款本地 TTS 引擎

Voicebox 集成了 7 款完全本地跑的 TTS 引擎，各有侧重：

| 引擎 | 语言数 | 特点 |
|------|--------|------|
| **Qwen3-TTS** | 10 | 高质量多语言，支持语调指令（`[laugh]`, `[sigh]`, `[gasp]`） |
| **Qwen CustomVoice** | 10 | 9 款预设声音，自然语言控制表达方式 |
| **LuxTTS** | 英语 | 轻量（~1GB VRAM），48kHz 采样，CPU 150x 实时速度 |
| **Chatterbox Multilingual** | 23 | 覆盖最广（阿拉伯语/印地语/斯瓦希里语等） |
| **Chatterbox Turbo** | 英语 | 350M 快速模型，支持副语言情绪标记 |
| **TADA（HumeAI）** | 10 | 超过 700 秒连贯音频，文本-声学对齐 |
| **Kokoro** | 8 | 50+ 预设声音，82M 小模型，CPU 推理流畅 |

中文支持：Qwen3-TTS、Qwen CustomVoice、Chatterbox Multilingual 均支持中文。

**推荐选型逻辑**：

- Agent 状态播报（英文）→ LuxTTS，速度最快，CPU 即可
- 中文内容 → Qwen3-TTS，质量最好
- 多语言覆盖 → Chatterbox Multilingual
- 资源极度受限 → Kokoro，82M 随处跑

---

## Whisper STT：听懂你说什么

语音输入（STT）侧，Voicebox 用 Whisper，提供五档选项：

- **Base / Small / Medium / Large** — 标准质量梯度
- **Turbo** — 比 Whisper Large 快约 8 倍，质量损失极小（日常使用推荐）

支持**全局热键推送讲话**，推送-说话和切换两种模式都有，可以在 Voicebox 内部任意文本框对着麦克风输入。转录完成后可选接一个本地 LLM（Qwen3 0.6B/1.7B/4B）润色，把口语化的碎片整理成干净的文字。

---

## 零样本声音克隆

声音配置（Voice Profile）可以从一段参考音频零样本克隆，也可以直接在 app 里录制。

- 支持多段参考音频提升克隆质量
- 配置文件可导入导出共享
- 每个 Profile 可绑定独立的效果链（pitch shift、reverb、delay、chorus、compressor 等）
- 内置 50+ 预设声音（Kokoro + Qwen CustomVoice），不录音也能直接用

---

## REST API：接进任何脚本

除了 MCP，Voicebox 还暴露了 HTTP REST API，可以从任何脚本或工具直接调用：

**语音合成：**

```bash
curl -X POST http://127.0.0.1:17493/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "profile_id": "abc123", "language": "en"}'
```

**Agent 播报（带客户端标识）：**

```bash
curl -X POST http://127.0.0.1:17493/speak \
  -H "Content-Type: application/json" \
  -H "X-Voicebox-Client-Id: my-script" \
  -d '{"text": "Deploy complete.", "profile": "Morgan"}'
```

**语音转文字：**

```bash
curl -X POST http://127.0.0.1:17493/transcribe \
  -F "audio=@recording.wav" \
  -F "model=whisper-turbo"
```

完整 API 文档在 `http://127.0.0.1:17493/docs`，Voicebox 运行时自动可访问。

---

## 技术架构

```
桌面层：Tauri（Rust）+ React + TypeScript + Tailwind
推理层：FastAPI（Python）+ MLX（Apple Silicon）/ PyTorch（CUDA/ROCm/DirectML/CPU）
存储层：SQLite
本地 LLM：Qwen3（0.6B/1.7B/4B，用于润色转录 + personality 改写）
```

GPU 支持覆盖：
- macOS Apple Silicon → MLX，Neural Engine 加速，4-5x 速度
- NVIDIA → CUDA 自动下载
- AMD → ROCm（需配置 `HSA_OVERRIDE_GFX_VERSION`）
- Intel Arc → IPEX/XPU
- 全平台 → DirectML（Windows）
- 无 GPU → CPU 推理，LuxTTS 和 Kokoro 依然跑得动

**安装方式：**

- macOS (Apple Silicon / Intel)：DMG
- Windows：MSI
- Docker：`docker compose up`

开发环境：

```bash
git clone https://github.com/jamiepine/voicebox.git
cd voicebox
just setup   # 创建 Python venv，安装依赖
just dev     # 启动后端 + 桌面端
```

---

## 工程实践建议

**场景一：给 CI/CD 加语音通知**

在 CI 脚本末尾加一句 curl，部署成功或失败都能开口汇报，不用盯着日志：

```bash
curl -s -X POST http://127.0.0.1:17493/speak \
  -H "Content-Type: application/json" \
  -H "X-Voicebox-Client-Id: ci-notify" \
  -d "{\"text\": \"Deploy to production completed in ${ELAPSED}s.\"}"
```

**场景二：Claude Code + 语音反馈**

装好 MCP 后，在系统提示或 CLAUDE.md 里加一行约定："任务完成或遇到需要用户确认的问题时，调用 voicebox.speak 播报摘要"。Claude Code 跑耗时任务时会主动开口，不用一直看屏幕。

**场景三：多 Agent 声音区分**

多个 Agent 实例并行工作时，给每个绑定不同声音（Settings → MCP），出结果一听声音就知道是哪个 Agent 在汇报。

**已知局限：**

- Voicebox 桌面端必须保持运行，MCP server 才能被访问；没有独立 daemon 模式
- 声音克隆质量受参考音频影响大，1-2 秒的短片段效果有限，建议 10 秒以上干净人声
- Windows/Linux 的自动粘贴（STT 输出后自动填入光标所在文本框）尚在 Roadmap，macOS 已实现

---

## 同类方案对比

| 方案 | MCP | 本地 | 声音克隆 | 主要用途 |
|------|-----|------|----------|----------|
| **jamiepine/voicebox** | ✅ 内置 | ✅ | ✅ | Agent 语音层 + 桌面工作流 |
| agjs/voicebox | ❌ | ✅ | ❌ | OpenAI 兼容 API 替代，自托管 |
| ElevenLabs | ❌ | ❌ | ✅ | 云端 TTS/克隆，付费 |
| WisprFlow | ❌ | 部分 | ❌ | 桌面语音输入，付费 |

---

jamiepine/voicebox 和同类工具最大的差别不在音质，而在**架构定位**：它是专门为 AI Agent 工作流设计的语音层，MCP server 是一等公民，声音绑定、personality 改写、captures 历史都是围绕 Agent 场景设计的。55K stars 和 MIT 协议保证了它不会突然消失或变收费。

如果你的工作流里已经有 Claude Code 或 Cursor，接入 Voicebox 的成本就是一行 `claude mcp add` 命令。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/jamiepine/voicebox
> Stars: 55,125 | License: MIT | Language: TypeScript + Python (Tauri desktop)
> Released: 2026-01-25 | Website: https://voicebox.sh

---

AI agents run tasks in the terminal while you stare at the screen waiting for results. What if your agent could just say "deploy complete, no errors" — or you could speak "check this PR" into a mic and have the agent start immediately? This isn't futuristic; it's an engineering capability you can install today.

Voicebox is the most direct open-source implementation of this voice layer: 55K stars, MIT license, fully local, with a built-in MCP server that connects to Claude Code, Cursor, and Windsurf with a single line of configuration.

---

## What It Is

Voicebox is a **local-first AI voice studio** — an open-source alternative to ElevenLabs and WisprFlow bundled into one desktop app. It packages TTS, STT, voice cloning, and agent voice integration in a single application that runs entirely on your machine.

Two core capabilities:

1. **Voice output for agents (TTS)**: When an agent completes a task, it can call a Voicebox MCP tool to speak the result in any cloned voice
2. **Voice input for agents (STT)**: A global hotkey captures your speech, Whisper transcribes it, an optional LLM cleans it up, and the text lands in whatever field your cursor is in

Both run entirely local. Audio never leaves your machine.

---

## Built-in MCP Server: One-Line Integration

This is Voicebox's most valuable feature for AI agent workflows — a built-in HTTP MCP server running at `http://127.0.0.1:17493/mcp`, no separate deployment needed.

**For Claude Code:**

```bash
claude mcp add voicebox \
  --transport http \
  --url http://127.0.0.1:17493/mcp \
  --header "X-Voicebox-Client-Id: claude-code"
```

**For Cursor / Windsurf / VS Code (`mcp.json`):**

```json
{
  "mcpServers": {
    "voicebox": {
      "url": "http://127.0.0.1:17493/mcp",
      "headers": { "X-Voicebox-Client-Id": "cursor" }
    }
  }
}
```

The `X-Voicebox-Client-Id` header identifies the calling client, enabling **per-client voice binding** — in Settings → MCP you can configure "Claude Code uses the Morgan voice, Cursor uses Jarvis" with each client independently routed.

**Available MCP Tools:**

| Tool | Function |
|------|----------|
| `voicebox.speak` | Agent voice output, with optional personality rewrite |
| `voicebox.transcribe` | Convert audio to text |
| `voicebox.list_captures` | Browse recorded audio and transcripts |
| `voicebox.list_profiles` | List available voice profiles |

Usage inside Claude Code:

```javascript
await voicebox.speak({
  text: "Tests passing. Ready to merge.",
  profile: "Morgan",       // optional — falls back to per-client binding
  personality: true,        // optional — rewrites through personality LLM first
});
```

---

## Seven Local TTS Engines

Voicebox bundles seven fully local TTS engines with different strengths:

| Engine | Languages | Strengths |
|--------|-----------|-----------|
| **Qwen3-TTS** | 10 | High-quality multilingual, delivery tags (`[laugh]`, `[sigh]`, `[gasp]`) |
| **Qwen CustomVoice** | 10 | 9 preset voices, natural-language delivery control |
| **LuxTTS** | English | Lightweight (~1GB VRAM), 48kHz, 150x real-time on CPU |
| **Chatterbox Multilingual** | 23 | Widest coverage (Arabic, Hindi, Swahili, etc.) |
| **Chatterbox Turbo** | English | Fast 350M model, paralinguistic emotion tags |
| **TADA (HumeAI)** | 10 | 700+ seconds coherent audio, text-acoustic alignment |
| **Kokoro** | 8 | 50+ preset voices, 82M model, smooth CPU inference |

**Selection heuristic:**
- English status announcements → LuxTTS (fastest, CPU-friendly)
- Chinese content → Qwen3-TTS (best quality)
- Multilingual coverage → Chatterbox Multilingual
- Constrained hardware → Kokoro (82M runs anywhere)

---

## Whisper STT: Capturing Your Voice

For speech input, Voicebox uses Whisper in five configurations:

- **Base / Small / Medium / Large** — standard quality ladder
- **Turbo** — ~8x faster than Whisper Large with minimal quality loss (recommended for daily use)

The global hotkey supports both push-to-talk and toggle modes. After transcription, an optional local LLM (Qwen3 0.6B/1.7B/4B) can refine the raw transcript — converting spoken fragments into clean written text.

---

## Zero-Shot Voice Cloning

Voice profiles can be created from a reference audio sample (zero-shot cloning) or recorded directly in the app:

- Multi-sample support for higher clone quality
- Profile import/export for sharing
- Per-profile effects chains (pitch shift, reverb, delay, chorus, compressor, etc.)
- 50+ built-in preset voices (Kokoro + Qwen CustomVoice) if you'd rather not record

---

## REST API: Integrate from Any Script

Beyond MCP, Voicebox exposes a REST API for direct integration from scripts and tools:

**Speech synthesis:**

```bash
curl -X POST http://127.0.0.1:17493/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "profile_id": "abc123", "language": "en"}'
```

**Agent announcement (with client ID):**

```bash
curl -X POST http://127.0.0.1:17493/speak \
  -H "Content-Type: application/json" \
  -H "X-Voicebox-Client-Id: my-script" \
  -d '{"text": "Deploy complete.", "profile": "Morgan"}'
```

**Speech-to-text:**

```bash
curl -X POST http://127.0.0.1:17493/transcribe \
  -F "audio=@recording.wav" \
  -F "model=whisper-turbo"
```

Full API docs are at `http://127.0.0.1:17493/docs` when Voicebox is running.

---

## Architecture

```
Desktop:    Tauri (Rust) + React + TypeScript + Tailwind
Inference:  FastAPI (Python) + MLX (Apple Silicon) / PyTorch (CUDA/ROCm/DirectML/CPU)
Storage:    SQLite
Local LLM:  Qwen3 (0.6B/1.7B/4B) for transcript refinement + personality rewrite
```

GPU support covers the full spectrum: Apple Silicon (MLX, Neural Engine, 4-5x speedup), NVIDIA (CUDA), AMD (ROCm), Intel Arc (IPEX/XPU), and universal DirectML on Windows. CPU fallback works on LuxTTS and Kokoro.

**Installation:**
- macOS (Apple Silicon / Intel): DMG
- Windows: MSI
- Docker: `docker compose up`

**Development:**

```bash
git clone https://github.com/jamiepine/voicebox.git
cd voicebox
just setup   # creates Python venv, installs deps
just dev     # starts backend + desktop app
```

---

## Engineering Patterns

**Pattern 1: Voice notifications in CI/CD**

Add a curl at the end of your CI script — successful or failed deploys announce themselves:

```bash
curl -s -X POST http://127.0.0.1:17493/speak \
  -H "Content-Type: application/json" \
  -H "X-Voicebox-Client-Id: ci-notify" \
  -d "{\"text\": \"Deploy to production completed in ${ELAPSED}s.\"}"
```

**Pattern 2: Claude Code with voice feedback**

Add a line to your CLAUDE.md or system prompt: "when a task completes or needs user confirmation, call voicebox.speak with a summary." Claude Code will announce results on long-running tasks without you staring at the terminal.

**Pattern 3: Multi-agent voice differentiation**

When running multiple agent instances in parallel, bind each to a distinct voice in Settings → MCP. You can tell which agent is reporting by sound alone.

**Known limitations:**

- The Voicebox desktop app must stay running — there's no standalone daemon mode for headless servers
- Clone quality depends heavily on reference audio quality; short clips (<10s) produce weaker results
- Auto-paste after STT (inserting transcribed text into the focused field) is macOS-only for now; Windows/Linux is on the roadmap

---

## Alternative Comparison

| Option | MCP | Local | Voice Cloning | Primary Use |
|--------|-----|-------|---------------|-------------|
| **jamiepine/voicebox** | ✅ Built-in | ✅ | ✅ | Agent voice layer + desktop workflow |
| agjs/voicebox | ❌ | ✅ | ❌ | Self-hosted OpenAI-compatible API |
| ElevenLabs | ❌ | ❌ | ✅ | Cloud TTS/cloning, paid |
| WisprFlow | ❌ | Partial | ❌ | Desktop voice input, paid |

---

The biggest differentiator from comparable tools isn't audio quality — it's architectural intent. Voicebox is designed specifically as an AI agent voice layer: the MCP server is a first-class citizen, per-client voice binding is built in, and captures/personality features are built around agent use cases. 55K stars and MIT licensing mean it won't vanish or go behind a paywall.

If you already have Claude Code or Cursor in your workflow, the integration cost is one `claude mcp add` command.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
