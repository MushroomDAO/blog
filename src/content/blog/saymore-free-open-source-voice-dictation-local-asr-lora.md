---
title: "Saymore：完全本地的免费语音输入工具，Qwen3-ASR + 自训 LoRA 润色，零上传"
titleEn: "Saymore: Free Local Voice Dictation with Qwen3-ASR and Self-Trained Polish LoRA — Zero Cloud"
description: "frankzch/Saymore，MIT，10 stars，Python，Windows 10/11 x64，2026-08-08 创建，v1.1.9。完全本地运行的中文语音输入与口述整理工具：Qwen3-ASR 1.7B GGUF 4bit 做识别，Silero VAD v5 做端点检测，本地自研唤醒词模型（默认「小咪」），自训 LoRA 做四种风格润色（轻度/深度/邮件/00后），llama.cpp Vulkan 做推理引擎。安装包 248.7 MB，首次启动自动下载约 1.5 GB ASR 模型，国内自动切 ModelScope 无需代理。最低 GTX 1650 4GB 显存，也可纯 CPU。ASR 延迟 GPU ~0.5s/CPU ~1-2s，润色 GPU ~2s/CPU ~5s。对比 Typeless（$30/月，云端，8000 词/周限制）和微信输入法（云端，仅识别不润色），Saymore 是完全离线、无字数上限、免费的替代方案。17 个 Release 版本，7 周内迭代积极。"
descriptionEn: "frankzch/Saymore, MIT, 10 stars, Python, Windows 10/11 x64, created 2026-08-08, v1.1.9. A fully local Chinese voice input and dictation polishing tool: Qwen3-ASR 1.7B GGUF 4-bit for transcription, Silero VAD v5 for endpoint detection, local custom wake word model (default: '小咪'), self-trained LoRA for four-style polishing (light/deep/email/Gen-Z), llama.cpp Vulkan as inference engine. Installer 248.7 MB; first launch auto-downloads ~1.5 GB ASR model, auto-selects ModelScope in China. Minimum GTX 1650 4GB VRAM, or CPU-only. ASR latency GPU ~0.5s / CPU ~1-2s, polish GPU ~2s / CPU ~5s. Compared to Typeless ($30/month, cloud, 8000 words/week free tier) and WeChat input (cloud, transcription-only), Saymore is the fully offline, unlimited, free alternative. 17 release versions in 7 weeks of active iteration."
pubDate: 2026-10-05
heroImage: "../../assets/images/saymore-free-open-source-voice-dictation-local-asr-lora-banner.jpg"
category: "Tech-Experiment"
tags: ["语音输入", "ASR", "本地AI", "隐私", "Windows", "开源工具", "Qwen3"]
lang: "zh-CN"
wechatTitle: "Saymore：完全本地免费语音输入+口述润色"
wechatDigest: "MIT 10星；Qwen3-ASR 1.7B+自训LoRA；完全本地零上传；GTX 1650起步；免费无限制"
---

大多数语音输入工具都有一个隐含前提：你的声音需要上传到别人的服务器。Typeless 把音频传到 AWS，微信输入法走腾讯云，OpenWispr 也是网络调用。这个前提对很多场景是不可接受的——会议录音、客户通话、医疗口述，或者只是不想让任何公司拿到你的声音。

Saymore 从这个痛点出发：Qwen3-ASR 本地识别，自训 LoRA 本地润色，VAD 本地检测，唤醒词本地跑。录音不出本机。

GitHub: https://github.com/frankzch/Saymore | ⭐ 10 | MIT | Python | v1.1.9

---

## 技术栈一览

| 组件 | 实现 | 规格 |
|------|------|------|
| ASR 模型 | Qwen3-ASR 1.7B | GGUF IQ4_NL 量化，~1.15 GB |
| 音频编码器 | mmproj-Qwen3-ASR-1.7B | Q8_0 量化，~340 MB |
| 推理引擎 | llama.cpp（Vulkan 版）| GPU 加速或纯 CPU |
| VAD | Silero VAD v5 | 2 MB ONNX，抗噪，fallback RMS |
| 端点检测依赖 | sherpa-onnx | — |
| 唤醒词 | 本地自研 KWS | 默认「小咪」，可配置 |
| 文本润色 | 自训 LoRA（Qwen3-ASR 基座）| 四种风格，打包在仓库 |

这个组合的关键决策是：**ASR 基座和润色 LoRA 共用同一个 Qwen3-ASR-1.7B，共用同一个 llama.cpp 进程**，不额外开进程，不额外占显存。

---

## 为什么用 Qwen3-ASR 而不是 Whisper

主流本地 ASR 方案大多基于 Whisper 系列。Saymore 选 Qwen3-ASR 有两个实际原因：

1. **中文识别质量**：Qwen3-ASR 是面向中文优化的多模态 ASR 模型，中文识别准确率高于同量级 Whisper，特别是口语、方言词和专有名词。

2. **同一基座做润色**：Qwen3-ASR 基于 Qwen3 语言模型架构，可以接 LoRA 做文本生成任务（润色/改写），而 Whisper 只是纯编码器-解码器结构，不支持这样扩展。一套推理引擎两用，是核心效率决策。

---

## 文本整理 LoRA：四种风格

LoRA 权重打包在 `polish_lora/` 目录里，克隆仓库即用，不需要自己训练。

四种风格靠 system 提示词切换，用的是同一份 adapter：

| 风格 | 场景 | 效果 |
|------|------|------|
| 轻度整理 | 日常记录 | 保留口语感，修错别字、加标点 |
| 深度润色 | 正式内容 | 口语→书面语，改结构 |
| 邮件模式 | 工作邮件 | 整理成可直接发出去的邮件格式 |
| 00后风格 | 社交内容 | 保留网络语气，适合小红书/朋友圈 |

这里有一个准确性说明：用户原文里说「说出一封能直接发出去的邮件」——邮件模式确实会改写口述内容成邮件格式，但结果质量取决于你的 GPU 性能和口述清晰度，实际使用中复杂句子仍然需要检查。

---

## 安装步骤

**前提**：Windows 10/11，x64，建议有 4GB+ VRAM 的 GPU（GTX 1650 起步），也可纯 CPU

1. 进入 GitHub Releases 页面（`github.com/frankzch/Saymore/releases`），下载最新版 `.exe` 安装包（v1.1.x 约 248.7 MB）

2. 双击安装，默认安装到 `%LocalAppData%`，**不需要管理员权限**，可选桌面快捷方式和开机自启

3. 第一次打开时，程序自动下载 ASR 主模型（约 1.5 GB）：
   - 自动检测网络，优先 HuggingFace，失败则切 ModelScope
   - **国内用户通常直接走 ModelScope，不需要额外设置网络**

4. 下载完成后自动重启，重启后直接可用

安装包已打包：唤醒词模型 + Silero VAD + LoRA 权重 + llama.cpp 推理引擎。首次下载只有 ASR 主模型是动态获取的。

---

## 性能参考

| 场景 | GPU（Vulkan）| CPU |
|------|-------------|-----|
| ASR 转录 | ~0.5 秒 | ~1-2 秒 |
| 文本润色（LoRA）| ~2 秒 | ~5 秒 |

实测硬件：开发者 README 给出的基准是 GTX 1650 级别 GPU。高端 GPU（RTX 3090/4090）实际更快，低端 CPU（i5/i7 无 GPU）会慢一些但仍可用。

---

## 和主流产品对比

| | Saymore | Typeless | 微信输入法 |
|---|---|---|---|
| 价格 | 免费 | $30/月 或 $144/年 | 免费 |
| 字数限制 | **无** | 免费版 8000 词/周 | 无 |
| 隐私 | **100% 本地** | 音频上传 AWS | 云端 |
| 中文识别 | Qwen3-ASR（中文 SOTA）| 英文强，中文一般 | 好 |
| 文本润色 | 本地 LoRA，四风格 | 云端 LLM | ❌ 仅识别 |
| 唤醒词 | 本地 KWS，可自定义 | 仅快捷键 | 长按按钮 |
| 平台 | Windows（macOS/Linux 计划）| Windows/macOS | Windows/macOS/手机 |

微信输入法不做润色这个点是用户原文里提到的真实差距：微信输入法只做识别和加标点，不会把「那个，这件事呢我觉得吧……」改写成能发出去的句子。

---

## 局限

**仅 Windows**：目前只有 Windows 10/11 x64 版本，macOS 和 Linux 在计划中但未发布。

**10 颗星的早期项目**：7 周内 17 个 Release 版本说明迭代快，但 100 来次累计下载量意味着用户基础极小，边角 case 没有被大量真实用户测试到。

**中文识别仍有边界**：Qwen3-ASR 对标准普通话准确率高，但强方言口音、大量专业术语（医学/法律）场景仍需建立热词词典（v1.1.x 新增了热词切词模型支持）。

**润色需要 GPU 才流畅**：CPU 模式下润色需要 5 秒，连续口述场景会感觉到延迟。

---

> MIT 开源。10 颗星的早期项目，API 可能随版本变化。录音音频完全本地处理，不上传任何服务器。开源仅供学习参考。

---

<!--EN-->

## Saymore: Free Local Voice Dictation with Qwen3-ASR Polish LoRA

Most voice input tools share an unstated assumption: your audio goes to someone's server. Typeless sends audio to AWS, WeChat input uses Tencent Cloud. For meetings, client calls, medical dictation, or just personal privacy, this isn't acceptable.

Saymore's premise: Qwen3-ASR recognition locally, self-trained LoRA polishing locally, VAD endpoint detection locally, wake word locally. Audio never leaves your machine.

GitHub: https://github.com/frankzch/Saymore | ⭐ 10 | MIT | Python | v1.1.9

---

### Tech Stack

**ASR**: Qwen3-ASR 1.7B, GGUF IQ4_NL quantization (~1.15 GB) + audio encoder mmproj (~340 MB)  
**Inference engine**: llama.cpp Vulkan (GPU accelerated or CPU-only)  
**VAD**: Silero VAD v5 (2 MB ONNX), fallback RMS energy threshold  
**Wake word**: local custom KWS, default "小咪", configurable  
**Polish LoRA**: self-trained on Qwen3-ASR-1.7B base, bundled in `polish_lora/`, four styles via system prompt switching  

Key architectural decision: ASR base model and polish LoRA share the same Qwen3-ASR-1.7B and the same llama.cpp process — no extra process, no extra VRAM allocation.

---

### Why Qwen3-ASR Instead of Whisper

Two practical reasons: (1) Qwen3-ASR is optimized for Chinese, with better accuracy than same-scale Whisper on Mandarin, spoken language, and proper nouns. (2) The Qwen3 architecture supports LoRA fine-tuning for text generation tasks — Whisper's encoder-decoder structure doesn't, so you can't do polishing with the same model.

---

### Four Polish Styles

Light, deep, email, and Gen-Z styles all share a single LoRA adapter, switched by system prompt:

- **Light**: preserve spoken tone, fix typos and add punctuation
- **Deep**: convert spoken → written, restructure sentences  
- **Email**: format dictation into a sendable email
- **Gen-Z**: keep internet tone for social media posts

The four styles use the same 1.7B model and the same llama.cpp instance — no additional resource cost per style change.

---

### Installation

Windows 10/11, x64. Minimum GTX 1650 (4GB VRAM), or CPU-only.

1. Download `.exe` from GitHub Releases (~248.7 MB, v1.1.x)
2. Install to `%LocalAppData%` — **no admin rights required**
3. First launch auto-downloads ASR model (~1.5 GB): prefers HuggingFace, falls back to ModelScope automatically (China users typically land on ModelScope with no proxy needed)
4. Auto-restarts after download; ready to use

---

### Performance

| Task | GPU (Vulkan) | CPU |
|------|-------------|-----|
| ASR transcription | ~0.5s | ~1-2s |
| LoRA polish | ~2s | ~5s |

---

### Comparison

| | Saymore | Typeless | WeChat Input |
|--|--|--|--|
| Price | Free | $30/month or $144/year | Free |
| Word limit | **None** | 8K words/week (free tier) | None |
| Privacy | **100% local** | Audio → AWS | Cloud |
| Chinese ASR | Qwen3-ASR (SOTA) | Good English, weaker Chinese | Good |
| Text polish | Local LoRA, 4 styles | Cloud LLM | ❌ Transcription only |
| Wake word | Local KWS, customizable | Keyboard shortcut only | Hold button |
| Platform | Windows (Mac/Linux planned) | Windows/macOS | Cross-platform |

---

### Constraints

Windows-only currently. 10-star early-stage project with ~100 cumulative downloads — rapid iteration (17 releases in 7 weeks) but minimal real-world stress testing. CPU polish mode (5s) creates noticeable lag in continuous dictation. Strong accents and dense technical terminology may need custom hotword dictionaries (added in v1.1.x).

---

> MIT. 10 stars, 7-week-old project. Audio processing fully local; no audio ever uploaded. For technical reference only.
