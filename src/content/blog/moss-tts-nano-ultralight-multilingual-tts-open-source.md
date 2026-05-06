---
title: "0.1B 参数跑满 20 种语言：MOSS-TTS-Nano 超轻量 TTS 开源"
titleEn: "0.1B Parameters, 20 Languages: MOSS-TTS-Nano Ultra-Lightweight TTS Is Open Source"
description: "OpenMOSS 开源 MOSS-TTS-Nano，0.1B 参数，纯 CPU 运行，48kHz 双声道输出，支持 20 种语言零样本声音克隆。单核 CPU（M4 MacBook Air）流畅推理，ONNX 运行无需 PyTorch，可嵌入浏览器扩展与边缘设备。"
descriptionEn: "OpenMOSS open-sources MOSS-TTS-Nano: 0.1B parameters, CPU-only, 48kHz stereo output, 20-language zero-shot voice cloning. Runs smoothly on a single CPU core (M4 MacBook Air), ONNX inference without PyTorch — embeddable in browser extensions and edge devices."
pubDate: "2026-05-06"
updatedDate: "2026-05-06"
category: "Tech-News"
tags: ["TTS", "语音合成", "开源", "MOSS", "ONNX", "声音克隆", "轻量模型", "本地部署"]
heroImage: "../../assets/images/moss-tts-nano-hero.jpg"
---

**结论先行（BLUF）**：0.1B 参数的 TTS 模型，纯 CPU 运行，输出 48kHz 双声道音频，支持 20 种语言零样本声音克隆。OpenMOSS 开源的 MOSS-TTS-Nano 不需要 GPU，不需要 PyTorch，M4 MacBook Air 单核跑起来没有压力。GitHub：`OpenMOSS/MOSS-TTS-Nano`

---

## 项目背景

MOSS-TTS-Nano 是 MOSI.AI 和 OpenMOSS 团队开发的语音合成模型，定位是 MOSS-TTS 系列的"微缩版"——解决 TTS 落地中的两个痛点：计算资源消耗大、部署复杂。目标是在保持实用音质的同时，做到极小资源占用 + 极低推理延迟。

---

## 核心技术架构

模型采用纯自回归（Autoregressive）架构，基于 **Audio Tokenizer + LLM** 流水线设计：

- **参数量**：0.1B（约 1 亿），彻底脱离 GPU 依赖
- **音频输出**：**48kHz 采样率双声道**，高保真，细节还原出色
- **推理效率**：比原始版本提升近 2 倍，支持流式推理，首包速度极快

---

## 核心功能

### 极致轻量化 + 低延迟
- 0.1B 参数，单核 CPU（MacBook Air M4）流畅运行
- 流式推理，首包音频几乎即时生成
- ONNX Runtime CPU 运行，**无需安装 PyTorch**

### 零样本声音克隆
- Voice Clone 模式：提供一段参考音频，即可高相似度复刻声线
- 内置自动分句克隆机制，稳定处理长篇幅文本

### 多语言支持
支持 **20 种语言**：中文、英文、日语、韩语、法语、德语、西班牙语、葡萄牙语、俄语、阿拉伯语、意大利语、荷兰语、波兰语、土耳其语、越南语、泰语、印尼语、马来语、捷克语、匈牙利语

---

## 部署方式

| 方式 | 适用场景 |
|------|---------|
| Python 推理脚本 | 本地快速测试 |
| FastAPI 本地 Web Demo | 可视化调试 |
| CLI 命令行工具 | 批量处理 |
| ONNX 推理方案（全套） | 无 PyTorch 生产部署 |
| MOSS-TTS-Nano-Reader | 浏览器扩展集成 |

ONNX 方案是亮点：**不依赖 PyTorch 即可运行**，适合嵌入浏览器扩展、本地助手、边缘计算设备。

---

## 实际意义

这个模型的价值不在于音质压倒一切——而在于**让 TTS 彻底脱离 GPU 算力门槛**。

几个典型应用场景：
- **本地 AI 助手语音输出**：和 Ollama、LM Studio 搭配，本机闭环无需云 TTS
- **浏览器阅读插件**：ONNX 直接在浏览器侧运行，无需后端服务
- **内容创作工作流**：文案 → 口播音频，全链路本地
- **边缘设备**：树莓派级硬件跑 TTS，传统需要云端的场景全部离线化

---

## 快速开始

```bash
git clone https://github.com/OpenMOSS/MOSS-TTS-Nano
cd MOSS-TTS-Nano
pip install -r requirements.txt
python inference.py --text "你好，世界" --language zh
```

ONNX 无 PyTorch 版本：
```bash
pip install onnxruntime
python onnx_inference.py --text "Hello world" --language en
```

---

## 常见问题

**Q：0.1B 的 TTS 音质能实用吗？**  
A：对于播客、旁白、工具语音提示等场景足够用。48kHz 双声道输出比大多数云端 TTS 的采样率更高。要求极高拟人度的场景（情感配音、有声书）建议搭配 7B 以上的模型。

**Q：和 CosyVoice、Fish-Speech 比怎么样？**  
A：MOSS-TTS-Nano 的差异化是资源极限——0.1B + 纯 CPU + ONNX。CosyVoice 和 Fish-Speech 音质更优但对算力要求高。两者定位不同，不是同一赛道。

**Q：ONNX 版本能在 Windows 上跑吗？**  
A：ONNX Runtime 跨平台，Windows/Linux/macOS 均支持。CPU-only 不挑硬件。

**Q：零样本克隆的相似度如何？**  
A：0.1B 参数量下零样本克隆的相似度有上限，适合"风格接近"而非"完全还原"。参考音频越清晰（低噪，单人），相似度越高。

**Q：能集成到 Claude Code 的语音输出流水线吗？**  
A：可以。通过 ONNX REST API 或 FastAPI demo 暴露 HTTP 接口，Claude Code 调用时对接即可，无需任何 GPU 资源。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: A 0.1B-parameter TTS model, CPU-only, outputting 48kHz stereo audio with 20-language zero-shot voice cloning. MOSS-TTS-Nano from OpenMOSS requires no GPU, no PyTorch, and runs comfortably on a single CPU core of an M4 MacBook Air. GitHub: `OpenMOSS/MOSS-TTS-Nano`

---

## Background

MOSS-TTS-Nano is developed by MOSI.AI and OpenMOSS as the "nano" variant of the MOSS-TTS series. The goal: solve the two practical blockers for TTS deployment — high compute requirements and complex setup. Keep usable audio quality while minimizing resource footprint and inference latency.

---

## Architecture

Pure autoregressive design based on an **Audio Tokenizer + LLM** pipeline:

- **Parameters**: 0.1B — no GPU required
- **Audio output**: **48kHz stereo**, high-fidelity
- **Inference speed**: ~2× faster than the base version, with streaming support for near-instant first-chunk delivery

---

## Key Features

### Ultra-lightweight + Low Latency
- Runs on a single CPU core (tested on M4 MacBook Air)
- Streaming inference — first audio chunk is near-instant
- **ONNX Runtime CPU inference — no PyTorch needed**

### Zero-Shot Voice Cloning
- Voice Clone mode: provide a reference audio clip → high-similarity voice replication
- Built-in sentence-splitting for stable long-text generation

### Multilingual Support
**20 languages**: Chinese, English, Japanese, Korean, French, German, Spanish, Portuguese, Russian, Arabic, Italian, Dutch, Polish, Turkish, Vietnamese, Thai, Indonesian, Malay, Czech, Hungarian

---

## Deployment Options

| Method | Use Case |
|--------|----------|
| Python inference script | Local quick test |
| FastAPI local web demo | Visual debugging |
| CLI tool | Batch processing |
| Full ONNX inference suite | PyTorch-free production deployment |
| MOSS-TTS-Nano-Reader | Browser extension integration |

The ONNX path is the standout: **runs without PyTorch**, suitable for browser extensions, local assistants, and edge devices.

---

## Why It Matters

The value isn't about competing with large TTS models on voice quality — it's about **removing the GPU compute barrier entirely**.

Key use cases:
- **Local AI assistant voice output**: pair with Ollama or LM Studio for fully offline TTS
- **Browser reading extension**: ONNX runs client-side, no backend needed
- **Content production pipeline**: copy → audio, fully local
- **Edge devices**: TTS on Raspberry Pi-class hardware, formerly cloud-only scenarios moved offline

---

## Quick Start

```bash
git clone https://github.com/OpenMOSS/MOSS-TTS-Nano
cd MOSS-TTS-Nano
pip install -r requirements.txt
python inference.py --text "Hello world" --language en
```

ONNX (no PyTorch):
```bash
pip install onnxruntime
python onnx_inference.py --text "Hello world" --language en
```

---

## FAQ

**Q: Is 0.1B TTS audio quality actually usable?**  
A: Yes, for podcasts, narration, tool voice prompts, and similar use cases. 48kHz stereo output actually exceeds the sample rate of most cloud TTS APIs. For high-fidelity emotional dubbing or audiobooks, larger models (7B+) are better suited.

**Q: How does it compare to CosyVoice or Fish-Speech?**  
A: MOSS-TTS-Nano's differentiation is extreme resource efficiency — 0.1B + CPU-only + ONNX. CosyVoice and Fish-Speech produce higher quality audio but require significant compute. Different target use cases, not direct competitors.

**Q: Does the ONNX version work on Windows?**  
A: Yes. ONNX Runtime is cross-platform — Windows, Linux, macOS all supported. CPU-only means hardware-agnostic.

**Q: How good is zero-shot voice cloning at 0.1B?**  
A: There's a ceiling at this parameter count — expect "stylistically close" rather than "exact replica." Quality improves significantly with clean, single-speaker reference audio (low noise).

**Q: Can this integrate into a Claude Code voice output pipeline?**  
A: Yes. Expose the ONNX inference or FastAPI demo as an HTTP endpoint, and Claude Code can call it via tool use — no GPU resources required.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
