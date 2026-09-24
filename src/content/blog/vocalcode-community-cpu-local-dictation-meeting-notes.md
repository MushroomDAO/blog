---
title: "VocalCode Community：CPU 优先的本地听写与会议记录，不上云不激活"
titleEn: "VocalCode Community: CPU-First Local Dictation and Meeting Notes, No Cloud, No Activation"
description: "VocalCode Community，AGPL-3.0，Rust + sherpa-onnx。本地优先的听写与会议记录工具，2026-09-22 开源。Parakeet TDT v3 + Paraformer 双模型，CPU 跑，Apple Silicon 和 Windows x64 双平台。社区版无需账号、无需激活码，所有语音处理本机完成，录音和转录不上传。作者 Daming Wu 用自己的工具给 Claude Code、Cursor 口述提示词，顺便做成了产品开源。"
descriptionEn: "VocalCode Community — AGPL-3.0, Rust + sherpa-onnx. Local-first dictation and meeting notes, open-sourced 2026-09-22. Dual-model: Parakeet TDT v3 + Paraformer, runs on CPU only, Apple Silicon and Windows x64. Community builds require no account, no activation. All speech processing happens on-device; no audio or transcripts are uploaded."
pubDate: 2026-09-24
heroImage: "../../assets/images/vocalcode-community-cpu-local-dictation-meeting-notes-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "speech-recognition", "local-ai", "dictation", "rust", "agpl", "cpu", "meeting-notes", "parakeet", "sherpa-onnx"]
lang: zh-CN
---

`wudaming00/vocalcode-community`，AGPL-3.0-only，Rust + sherpa-onnx，2026-09-22 开源源码预览。本地优先的语音听写与会议记录工具，CPU 跑，不需要 GPU，不需要账号，不上云。

**GitHub**：github.com/wudaming00/vocalcode-community | **License**：AGPL-3.0-only | **平台**：Apple Silicon macOS + Windows x64

---

## 背景：作者的自用工具

作者 Daming Wu 用 AI 编程工具（Claude Code、Cursor）写代码，习惯口述长提示词而不是用键盘逐字打。他想要的很简单：语音转文字，全在本机跑，按键说话松键停，什么都不出设备。

VocalCode 最开始是这个逻辑的产物：付费桌面 App（4.99 美元一次性买断，30 天免费试用），面向日常口述场景。

**Community 版的出现**是把本地功能这部分彻底开源出来：源码 AGPL-3.0 开放，社区构建版无需购买，无需账号，无需激活码，本地特性全部解锁。

---

## 两个核心功能

### 1. 实时听写

推荐的使用方式是「推说停释」（Push-to-talk）：按住快捷键说话，松开立即得到转录文字，插入光标位置。

模型默认选项：
- **Parakeet TDT v3**（NVIDIA 出品，transducer 架构）：CPU 上约 3300× 实时速度，平均词错率 6.32%，25 种语言，静默段不幻觉
- **Paraformer**：阿里达摩院出品，中英混合场景覆盖更好，单通道 CPU 推理

sherpa-onnx 把这两个模型统一包装，不需要 Python 环境，不需要 PyTorch，Rust 二进制直接加载 ONNX 权重。

**为什么 Parakeet TDT 比 Whisper 更适合听写？**

Whisper 是编码器-解码器架构，解码阶段有自由生成能力——这意味着在录音开头/结尾的静默段，模型可能"编"出完全不存在的句子（幻觉）。Parakeet TDT 是流式 transducer，结构上不会在静默段输出。对于听写场景（大量开头结尾静默），这个差异比 benchmark 分数更重要。

### 2. 会议记录

本地录制会议音频 → 转录 → 建立可搜索的文本数据库 → 导出。

整个链路：录音文件在本机 → 模型在本机 → 转录结果在本机 → 搜索索引在本机。VocalCode 的说法是「recognition audio and transcripts are not uploaded by these pipelines」，这是架构保证，不是隐私政策里的承诺。

---

## 个人词汇与纠错学习

这是区分度比较高的一个功能：工具支持用户建立个人词汇表（项目名、人名、专有名词），模型在推理时会优先使用这些词汇修正输出。

对于开发者场景，这个意义在于：代码库里的函数名、模块名、同事名字这类词，通用 ASR 模型经常拼错或识别成同音异义词，个人词汇表可以有效解决这个问题，不需要微调模型。

---

## 技术栈

| 组件 | 内容 |
|------|------|
| 语言 | Rust |
| 推理引擎 | sherpa-onnx（无 Python，无 PyTorch）|
| 语音模型 | Parakeet TDT v3 / Paraformer |
| 平台 | Apple Silicon macOS / Windows x64 |
| 分发 | Homebrew（macOS）/ winget（Windows）|
| 开源协议 | AGPL-3.0-only |

**Homebrew 安装（macOS）：**

```bash
brew install wudaming00/tap/vocalcode
```

**winget 安装（Windows）：**

```powershell
winget install wudaming00.VocalCode
```

---

## Community 版 vs 付费版

Community 版是同一套桌面 App 的源码开放构建，本地特性全部可用，无需激活。付费版（4.99 美元）主要差异集中在云同步、优先技术支持等扩展功能，核心的本地语音处理没有功能锁。

---

## 局限性

**1. AGPL-3.0 协议**：如果基于源码构建服务，需要开放相应修改。商用集成需要认真看协议条款。

**2. 语言覆盖**：Parakeet TDT v3 支持 25 种语言（主要欧洲语言 + 英语），不覆盖日语、韩语、阿拉伯语等。Paraformer 针对中英混合有优化，其他语言支持有限。如果主要工作语言不在这个列表里，Whisper 仍然是更安全的选择。

**3. 源码预览阶段**：2026-09-22 的发布标注为 `source-preview`，不是稳定发布。自行构建需要 Rust 工具链，不是开箱即用。预构建二进制仍通过 Homebrew/winget 分发。

**4. Windows 仅 x64**：ARM64 Windows 不在支持列表。

**5. 会议记录功能仍在迭代**：个人词汇学习、会议搜索等功能按项目说明仍处于「探索」阶段，功能成熟度低于听写核心功能。

---

## 怎么看这个项目

VocalCode Community 的核心判断是：**本地 ASR 的质量已经够用，问题是集成和工程包装**。Parakeet TDT 的 CPU 性能和 Whisper 的幻觉问题都是已知的，作者选了 Rust + sherpa-onnx 这条不依赖 Python 生态的路，打包成桌面工具开源出来。

个人词汇修正和无幻觉静默处理，这两个功能在开发者口述场景里是真实的痛点，不是噱头。

AGPL-3.0 是正经的开源协议，社区版的本地功能完整解锁，不是砍掉核心功能的开源引流版。

对于日常需要对 AI 编程工具口述长指令的开发者，值得试用。对于想理解「本地 ASR 怎么做成桌面工具」的技术人，源码是个不错的参考。

> AGPL-3.0-only，开源仅供学习研究参考。

---

<!--EN-->

## VocalCode Community: CPU-First Local Dictation and Meeting Notes

`wudaming00/vocalcode-community` (AGPL-3.0-only, Rust + sherpa-onnx) opened its source on 2026-09-22. It's a local-first dictation and meeting notes tool: CPU only, no GPU needed, no account, no cloud upload.

**GitHub**: github.com/wudaming00/vocalcode-community | **License**: AGPL-3.0-only | **Platforms**: Apple Silicon macOS + Windows x64

---

### Origin

Author Daming Wu uses AI coding tools (Claude Code, Cursor) and prefers to dictate long prompts rather than type them. He wanted push-to-talk speech input that ran entirely on-device. VocalCode started as a paid desktop app (USD 4.99 one-time). Community Edition opens the local-processing code under AGPL-3.0: no purchase, no account, no activation required, all local features unlocked.

---

### Two Core Features

**1. Real-time Dictation (Push-to-talk)**

Hold a hotkey → speak → release → transcription inserted at cursor. Two model options:

- **Parakeet TDT v3** (NVIDIA, transducer architecture): ~3,300× real-time on CPU, 6.32% avg WER, 25 languages, no silence hallucinations
- **Paraformer** (Alibaba DAMO Academy): better Chinese-English code-switching coverage

Why Parakeet TDT beats Whisper for dictation: Whisper's encoder-decoder design can hallucinate fluent text during silence segments. Transducer models like Parakeet are structurally resistant to this — they emit tokens only when acoustic evidence arrives. For dictation (many leading/trailing silence segments), this matters more than benchmark scores.

**2. Meeting Notes**

Local recording → transcription → searchable local database → export. The full pipeline never leaves the device.

---

### Personal Vocabulary

Users can define a personal vocabulary (function names, project names, colleague names). The model applies corrections at inference time — no fine-tuning needed. This directly addresses the common problem of ASR models mangling code-specific proper nouns.

---

### Tech Stack

| Component | Details |
|-----------|---------|
| Language | Rust |
| Inference | sherpa-onnx (no Python, no PyTorch) |
| ASR Models | Parakeet TDT v3 / Paraformer |
| Platforms | Apple Silicon macOS / Windows x64 |
| Distribution | Homebrew (macOS) / winget (Windows) |
| License | AGPL-3.0-only |

```bash
# macOS
brew install wudaming00/tap/vocalcode

# Windows
winget install wudaming00.VocalCode
```

---

### Limitations

1. **AGPL-3.0**: Network service deployments must open-source modifications.
2. **Language coverage**: Parakeet TDT v3 covers 25 (primarily European) languages. No Japanese, Korean, Arabic. Whisper remains the safer choice for broad multilingual needs.
3. **Source preview**: The 2026-09-22 release is tagged `source-preview`, not a stable build. Pre-built binaries via Homebrew/winget are the intended distribution path.
4. **Windows x64 only**: ARM64 Windows not supported.
5. **Meeting features still maturing**: Meeting search and vocabulary learning are listed as exploratory.

---

### Assessment

The core bet: local ASR quality is good enough; the gap is integration and packaging. The Rust + sherpa-onnx stack avoids the Python ecosystem entirely — that's a real engineering choice, not just a preference. Personal vocabulary correction and silence-resistant transcription both address genuine pain points for developer dictation workflows.

The Community Edition isn't a crippled open-core bait — local features are fully unlocked. For developers who regularly dictate long prompts to AI coding tools, it's worth trying. For engineers who want to understand how to ship a desktop local-ASR tool, the source is a solid reference.

> AGPL-3.0-only. For learning and research reference only.
