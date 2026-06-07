---
title: "25MB 跑 SOTA：KittenTTS 极致轻量 + Spark TTS 中文零样本克隆，两条路径完全指南"
description: "KittenTTS 14.1k star，15M 参数 int8 量化 25MB，纯 CPU ONNX 推理，树莓派和浏览器可跑——但不支持中文。Spark TTS 0.5B 参数，Qwen2.5 LLM 骨干，中文 CER 仅 1.20，零样本声音克隆，本文给出两个项目的完整使用路径和场景选型指南。"
titleEn: "25MB SOTA TTS: KittenTTS Ultra-Lightweight + Spark TTS Chinese Zero-Shot Voice Cloning — Complete Guide"
descriptionEn: "KittenTTS: 14.1k stars, 15M params, 25MB int8, pure CPU ONNX — runs on Raspberry Pi and in-browser. But no Chinese support. Spark TTS: 0.5B params, Qwen2.5 LLM backbone, Chinese CER 1.20, zero-shot voice cloning. This guide covers full usage paths and a clear decision framework for both."
pubDate: 2026-06-07
category: "Tech-Experiment"
tags: ["TTS", "语音合成", "Edge AI", "KittenTTS", "Spark TTS", "ONNX", "开源", "中文AI"]
lang: "zh-CN"
heroImage: "../../assets/images/kittentts-spark-tts-edge-ai-tts-banner.png"
---

语音合成（TTS）这件事，正在往两个方向同时跑。

一边是**往小跑**：把模型压到极限，在手机、树莓派、甚至浏览器里实时跑，不依赖 GPU，不上云；另一边是**往好跑**：用大语言模型做骨干，把中文合成质量推到接近人声。

这篇文章把两个方向的代表项目都拆开讲清楚：

- **KittenTTS**（`KittenML/KittenTTS`）：25MB，Edge AI 方向的极致
- **Spark TTS**（`SparkAudio/Spark-TTS`）：0.5B 参数，中文方向的实用选择

两个都是 Apache 2.0 开源，都能今天就跑起来。

---

## KittenTTS：25MB 能跑出什么

### 数字先说清楚

| 指标 | 数值 |
|------|------|
| GitHub Star | **14,100+** |
| Fork | 772 |
| 协议 | Apache 2.0 |
| 语言 | Python（ONNX 跨平台） |

**四个型号，选一个就好：**

| 型号 | 参数量 | 磁盘大小 | 适合场景 |
|------|-------|---------|---------|
| Mini | 80M | 80MB | 最高质量，服务器部署 |
| Micro | 40M | 40MB | 质量与速度平衡 |
| **Nano** | **15M** | **56MB（int8: 25MB）** | **边缘设备、嵌入式** |

Nano int8 量化版就是那个 25MB 的版本，24kHz 音频输出，8 个内置音色（Bella、Jasper、Luna、Bruno、Rosie、Hugo、Kiki、Leo）。

### 为什么 CPU 比 GPU 快

KittenTTS 有一个反常识的测试结果：**M4 Pro 上 CPU 推理比 CoreML 快 1.7 倍**。

原因很清楚：模型太小了。15M 参数的模型，GPU/NPU 的调度开销比模型本身的计算量还大，反而成为瓶颈。这是 Edge AI 的一个典型现象——小模型在通用 CPU 上跑往往比在专用硬件上更高效。

**实测推理速度（RTF = 实际耗时/音频时长，越小越快）：**

| 平台 | RTF | 备注 |
|------|-----|------|
| M4 Pro（CPU） | ~0.065 | 快于实时约 15 倍 |
| Rust 版本 | ~0.11 | 快于实时约 9 倍 |
| 树莓派 | 可实时 | 有明显延迟但能跑 |
| 浏览器（WASM） | 可实时 | WebAssembly + ONNX Runtime Web |

### 技术架构

```
输入文本
   ↓
Espeak-ng 音素化（文本 → IPA 音素）
   ↓
ONNX Transformer 编解码器（预测梅尔频谱）
   ↓
声码器解码 → 24kHz WAV 输出
```

整个 pipeline 只有 ONNX 文件，无 Python 运行时依赖（Rust 版），可嵌入任何语言。

---

### 安装和使用

**Python 版（推荐新手）**

```bash
# Linux / macOS 先装 espeak
# Ubuntu/Debian:
sudo apt install espeak-ng

# macOS:
brew install espeak

# 安装 KittenTTS
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl
```

**最简单的用法：**

```python
import soundfile as sf
from kittentts import KittenTTS

# 自动从 Hugging Face 下载模型（首次运行）
model = KittenTTS()

# 生成语音
audio = model.generate(
    text="Hello, this is KittenTTS running entirely on CPU.",
    voice="Bella",
    speed=1.0
)

sf.write("output.wav", audio, 24000)
```

**指定型号（默认 Nano，可切换 Mini/Micro）：**

```python
# 最高质量版
model = KittenTTS("KittenML/kitten-tts-mini-0.8")

# 最小体积版（推荐嵌入式）
model = KittenTTS("KittenML/kitten-tts-nano-0.8")
```

**Rust 版（无 Python 依赖，单二进制 <10MB）**

```bash
# 从 GitHub Releases 下载预编译二进制
# https://github.com/second-state/kitten_tts_rs/releases

# 命令行生成
./kitten_tts_rs --text "Hello from Rust" --voice Bella --output hello.wav

# 作为 HTTP 服务启动（供其他语言调用）
./kitten_tts_rs --server --port 8080
```

**WebAssembly / 浏览器版**

直接引用 `kitten-tts-web` 项目，用 ONNX Runtime Web 在浏览器中运行，无需后端。适合 Web 应用内嵌 TTS。

---

### ⚠️ 中文支持现状：明确不支持

这是 KittenTTS 最重要的限制，必须说清楚：

**当前版本（0.8.1）不支持中文。**

输入中文文本，输出是乱码或重复的单词，不是正常语音。GitHub Issues #97、#15 都有用户反馈，开发团队的回应是：多语言支持在路线图上，但**没有具体时间表**，也没有迹象表明近期会实现。

**如果你的场景是中文 TTS，现在就应该看下一节的 Spark TTS。**

---

## Spark TTS：把 LLM 用来合成语音

### 数字先说清楚

| 指标 | 数值 |
|------|------|
| GitHub Star | **11,000+** |
| Fork | 1,200+ |
| 协议 | Apache 2.0 |
| 参数量 | **0.5B**（5 亿） |
| arXiv | 2503.01710（2025.03） |

Spark TTS 是香港科技大学、出门问问、上海交通大学、南洋理工大学等机构联合研究的成果，背后是工业界和学术界真实合作的项目。

### 核心创新：用 LLM 做 TTS

多数 TTS 系统的架构是：文本编码 → 声学模型（Flow/Diffusion）→ 声码器。需要多个独立模块配合。

Spark TTS 的路子不一样——**直接用 Qwen2.5-0.5B 这个语言模型做骨干**，配合它自研的 BiCodec 音频分词器，整个系统变成：

```
输入文本（+ 可选参考音频）
   ↓
Qwen2.5-0.5B（decoder-only LLM）
   ↓ 预测 BiCodec token 序列
BiCodec 解码器
   ↓
音频波形输出
```

没有独立的声学模型，没有 Flow Matching，单阶段解码。

**BiCodec 是关键**：它把音频信息拆成两类 token：
- **语义 token**：编码语言内容（50 tokens/秒，来自 wav2vec 2.0 特征）
- **全局 token**：编码说话人特征（ECAPA-TDNN + FSQ 量化）

这种分离让模型可以独立控制"说什么"和"谁在说"——零样本声音克隆的基础就在这里。

### 中文质量数据

训练数据：**10 万小时**（VoxBox 数据集，470 万音频文件，来自 29 个开源数据集）

**中文 CER（字符错误率，越低越好）对比：**

| 模型 | 中文 CER | 参数量 | 备注 |
|------|---------|-------|------|
| Seed-TTS（商业闭源） | 1.15 | 未知 | 闭源最优 |
| **Spark TTS** | **1.20** | **0.5B** | **开源最优** |
| Llasa | ~2.1 | 8B | 250k 小时训练 |
| CosyVoice | ~2.8 | 300M | 阿里开源 |

**0.5B 的 Spark TTS 打败了 8B 的 Llasa**，用更少参数、更少训练数据取得更好的中文结果。这是论文里最重要的数据点。

---

### 安装和使用

**系统要求：Python 3.12+，PyTorch 2.5+，有 GPU 最好（CPU 也能跑，慢一些）**

```bash
# 克隆项目
git clone https://github.com/SparkAudio/Spark-TTS.git
cd Spark-TTS

# 创建虚拟环境
conda create -n spark-tts python=3.12
conda activate spark-tts

# 安装依赖
pip install -r requirements.txt
```

模型会在首次运行时自动从 Hugging Face 下载（`SparkAudio/Spark-TTS-0.5B`，约 2-3GB）。

---

### 用法一：命令行推理

**中文 TTS：**

```bash
python inference.py \
  --text "你好，这是 Spark TTS 的中文语音合成测试。" \
  --device 0 \
  --output_path output_zh.wav
```

**英文 TTS：**

```bash
python inference.py \
  --text "Hello, this is a Spark TTS English synthesis test." \
  --device 0 \
  --output_path output_en.wav
```

**中英混合（code-switching）：**

```bash
python inference.py \
  --text "今天我们来测试一下 Spark TTS 的 code-switching 能力。" \
  --device 0 \
  --output_path output_mix.wav
```

---

### 用法二：零样本声音克隆

提供一段 3-10 秒的参考音频，Spark TTS 会克隆说话人音色：

```bash
python inference.py \
  --text "这段话将用参考音频的音色合成。" \
  --prompt_speech_path reference_audio.wav \
  --prompt_text "参考音频对应的文字内容" \
  --device 0 \
  --output_path cloned_output.wav
```

参考音频不需要训练，不需要 fine-tune，**零样本即可克隆**，是目前开源中文 TTS 里最好用的声音克隆方案之一。

---

### 用法三：可控生成（调整音色参数）

不使用参考音频，通过参数直接控制：

```bash
python inference.py \
  --text "这是一个语速较慢、音调偏低的合成效果。" \
  --gender female \
  --pitch moderate \
  --speed slow \
  --device 0 \
  --output_path controlled_output.wav
```

| 参数 | 可选值 | 说明 |
|------|------|------|
| `--gender` | male / female | 声音性别 |
| `--pitch` | very_low / low / moderate / high / very_high | 音调 |
| `--speed` | very_slow / slow / moderate / fast / very_fast | 语速 |

---

### 用法四：Web UI（图形界面）

```bash
# GPU 推理
python webui.py --device 0

# CPU 推理（较慢）
python webui.py --device cpu
```

打开 `http://localhost:7860`，有两个 Tab：
- **Voice Clone**：上传参考音频 + 输入文本 → 生成
- **Voice Creation**：通过参数组合创建新音色

---

### GPU 推理性能参考

**L20 GPU，26 条音频，总时长 169 秒：**

| 并发数 | 首包延迟 | RTF |
|-------|---------|-----|
| 1 | 876ms | 0.136 |
| 2 | 921ms | 0.074 |
| 4 | 1611ms | 0.070 |

并发 2-4 时 RTF 约 0.07，即每秒 CPU/GPU 时间生成约 14 秒音频。

**如果没有 GPU**，CPU 推理也可以跑，速度约 RTF 0.5-1.5（接近实时或略慢于实时），取决于机器。

---

## 选型指南

**一句话判断：**

> 英文 + 极度轻量 + 嵌入式/浏览器 → **KittenTTS Nano**  
> 中文 + 声音克隆 + 有 GPU → **Spark TTS**

**详细对比：**

| 需求 | KittenTTS | Spark TTS |
|------|-----------|-----------|
| 中文支持 | ❌ 不支持 | ✅ 优秀（CER 1.20） |
| 英文支持 | ✅ SOTA 水平 | ✅ 良好 |
| 模型大小 | ✅ 25MB（Nano int8） | ❌ ~2-3GB |
| CPU 推理 | ✅ 极快（RTF 0.065） | ⚠️ 可用，较慢 |
| GPU 推理 | 不需要 | ✅ RTF 0.07-0.14 |
| 零样本声音克隆 | ❌ 固定 8 个音色 | ✅ 支持 |
| 可控生成 | 速度、音量 | ✅ 性别/音调/语速 |
| 嵌入式设备 | ✅ 树莓派可跑 | ❌ 太大 |
| 浏览器运行 | ✅ WASM 支持 | ❌ 不支持 |
| Rust 版（无 Python） | ✅ <10MB 单二进制 | ❌ 无 |
| 流式推理 | ❌ | ✅ TensorRT-LLM |

**场景对应：**

| 场景 | 推荐 |
|------|------|
| 语音助手嵌入到 iOS/Android app | KittenTTS Nano |
| 树莓派或嵌入式硬件设备 | KittenTTS Nano（Rust 版） |
| 纯浏览器 Web 应用 TTS | KittenTTS（WASM 版） |
| 有声书、播客中文生成 | Spark TTS |
| 中文客服/配音自动化 | Spark TTS |
| 声音克隆（用自己声音读文章） | Spark TTS |
| 多语言混合（中英切换） | Spark TTS |
| 离线英文阅读器（手机） | KittenTTS Nano |

---

## 我的判断

**两个项目各自在自己的赛道上做到了顶尖，但赛道完全不同。**

KittenTTS 解决的是"在不可能跑大模型的地方，怎么还能有像样的 TTS"——25MB、CPU、ONNX、Rust 单二进制，这是工程上的极致压缩，不是研究 demo，是真正的边缘部署方案。**中文不支持是硬伤，但这本来就不是它的战场。**

Spark TTS 的价值在于它证明了 0.5B 的 LLM 骨干能够在中文 TTS 上打败 8B 的同类——用更少的参数、更少的数据，取得更好的结果。零样本声音克隆加上 10 万小时中文训练数据，是目前开源社区里中文 TTS 最有实用价值的选项之一。

如果你做中文内容、中文产品，Spark TTS 是今天最值得认真试的开源方案。如果你做 Edge AI 或浏览器端语音，KittenTTS 目前没有竞争对手。

---

**KittenTTS GitHub**: KittenML/KittenTTS（14.1k star）  
**KittenTTS Demo**: huggingface.co/spaces/KittenML/KittenTTS-Demo  
**Spark TTS GitHub**: SparkAudio/Spark-TTS（11k star）  
**Spark TTS 论文**: arxiv.org/abs/2503.01710  
**Spark TTS Demo**: sparkaudio.github.io/spark-tts/

<!--EN-->

## 25MB SOTA TTS: KittenTTS Ultra-Lightweight + Spark TTS Chinese Zero-Shot Voice Cloning — Complete Guide

Text-to-speech is racing in two directions at once.

One direction is **smaller**: compress models to the absolute limit so they run on phones, Raspberry Pis, or even browsers — no GPU, no cloud. The other direction is **better**: use large language models as the backbone and push Chinese synthesis quality toward human-level naturalness.

This article covers the best representative of each direction:

- **KittenTTS** (`KittenML/KittenTTS`): 25MB — the edge AI extreme
- **Spark TTS** (`SparkAudio/Spark-TTS`): 0.5B parameters — the practical Chinese choice

Both Apache 2.0. Both runnable today.

---

## KittenTTS: What 25MB Can Actually Do

### The Numbers

| Metric | Value |
|--------|-------|
| GitHub Stars | **14,100+** |
| Forks | 772 |
| License | Apache 2.0 |

**Four model variants:**

| Variant | Params | Disk | Best For |
|---------|--------|------|----------|
| Mini | 80M | 80MB | Highest quality, server |
| Micro | 40M | 40MB | Balanced |
| **Nano** | **15M** | **56MB (int8: 25MB)** | **Edge / embedded** |

The 25MB figure is Nano with int8 quantization, 24kHz audio output, 8 built-in voices: Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo.

### Why CPU Beats GPU Here

KittenTTS has a counterintuitive benchmark: **CPU inference on M4 Pro is 1.7x faster than CoreML**.

The reason is straightforward: the model is too small. At 15M parameters, GPU/NPU scheduling overhead exceeds the actual compute cost. This is a classic edge AI phenomenon — tiny models often run faster on general-purpose CPUs than on specialized hardware.

**Real-Time Factor (RTF — lower is faster):**

| Platform | RTF | Meaning |
|----------|-----|---------|
| M4 Pro (CPU) | ~0.065 | ~15x faster than real-time |
| Rust binary | ~0.11 | ~9x faster than real-time |
| Raspberry Pi | ~1.0 | Near real-time |
| Browser (WASM) | ~1.0 | Near real-time |

### Installation and Usage

```bash
# Linux/macOS: install espeak-ng first
sudo apt install espeak-ng   # Ubuntu
brew install espeak           # macOS

# Install KittenTTS
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl
```

**Basic Python usage:**

```python
import soundfile as sf
from kittentts import KittenTTS

model = KittenTTS()  # auto-downloads Nano from Hugging Face

audio = model.generate(
    text="Hello, this is KittenTTS running entirely on CPU.",
    voice="Bella",
    speed=1.0
)

sf.write("output.wav", audio, 24000)
```

**Select a specific variant:**

```python
model = KittenTTS("KittenML/kitten-tts-mini-0.8")   # highest quality
model = KittenTTS("KittenML/kitten-tts-nano-0.8")   # smallest (recommended for edge)
```

**Rust binary (no Python required, single binary <10MB):**

```bash
# Download from https://github.com/second-state/kitten_tts_rs/releases

./kitten_tts_rs --text "Hello from Rust" --voice Bella --output hello.wav

# Run as HTTP server for other languages to call
./kitten_tts_rs --server --port 8080
```

**Browser/WebAssembly:** Use the `kitten-tts-web` project — ONNX Runtime Web runs the model entirely client-side, no backend required.

### ⚠️ Chinese Support: Explicitly Not Supported

This is the most important limitation. **KittenTTS 0.8.1 does not support Chinese.**

Feeding Chinese text produces garbled output or repeated individual words. GitHub Issues #97 and #15 both request Chinese support; the dev team's response is that multilingual TTS is on the roadmap but with no timeline or near-term commitment.

**If your use case requires Chinese TTS, go directly to Spark TTS.**

---

## Spark TTS: Using an LLM as a Speech Synthesizer

### The Numbers

| Metric | Value |
|--------|-------|
| GitHub Stars | **11,000+** |
| Forks | 1,200+ |
| License | Apache 2.0 |
| Parameters | **0.5B** |
| Paper | arXiv 2503.01710 (March 2025) |

Spark TTS is a joint project from HKUST, Mobvoi, SJTU, NTU, and NPU — genuine industry-academia collaboration.

### Core Innovation: LLM as TTS Backbone

Most TTS systems: text encoder → acoustic model (Flow/Diffusion) → vocoder. Multiple independent modules.

Spark TTS takes a different path: **use Qwen2.5-0.5B directly as the backbone**, paired with a custom BiCodec audio tokenizer:

```
Input text (+ optional reference audio)
   ↓
Qwen2.5-0.5B (decoder-only LLM)
   ↓ predicts BiCodec token sequence
BiCodec decoder
   ↓
Audio waveform
```

No separate acoustic model. No flow matching. Single-stage decoding.

**BiCodec splits audio into two token types:**
- **Semantic tokens**: encode linguistic content (50 tokens/sec from wav2vec 2.0)
- **Global tokens**: encode speaker characteristics (ECAPA-TDNN + FSQ quantization)

This separation is what makes zero-shot voice cloning possible — you can independently control *what* is said and *who* says it.

### Chinese Quality Data

Training: **100,000 hours** (VoxBox dataset, 4.7M audio files, 29 open-source datasets)

**Chinese CER (Character Error Rate, lower = better):**

| Model | Chinese CER | Params | Note |
|-------|-------------|--------|------|
| Seed-TTS (closed) | 1.15 | Unknown | Proprietary best |
| **Spark TTS** | **1.20** | **0.5B** | **Best open-source** |
| Llasa | ~2.1 | 8B | 250k hours training |
| CosyVoice | ~2.8 | 300M | Alibaba open-source |

**0.5B Spark TTS outperforms 8B Llasa** with fewer parameters and less training data. The most important data point in the paper.

### Installation and Usage

```bash
git clone https://github.com/SparkAudio/Spark-TTS.git
cd Spark-TTS

conda create -n spark-tts python=3.12
conda activate spark-tts
pip install -r requirements.txt
```

Model downloads automatically from Hugging Face on first run (~2-3GB).

**Chinese TTS:**

```bash
python inference.py \
  --text "你好，这是 Spark TTS 的中文语音合成测试。" \
  --device 0 \
  --output_path output_zh.wav
```

**Zero-shot voice cloning (3-10s reference audio):**

```bash
python inference.py \
  --text "This will be synthesized in the reference speaker's voice." \
  --prompt_speech_path reference_audio.wav \
  --prompt_text "The transcript of the reference audio." \
  --device 0 \
  --output_path cloned_output.wav
```

No training, no fine-tuning — zero-shot.

**Controllable generation (no reference audio):**

```bash
python inference.py \
  --text "这是一个语速较慢、音调偏低的合成效果。" \
  --gender female \
  --pitch moderate \
  --speed slow \
  --device 0 \
  --output_path controlled_output.wav
```

**Web UI:**

```bash
python webui.py --device 0   # GPU
python webui.py --device cpu  # CPU (slower)
# Open http://localhost:7860
```

**GPU inference (L20, 169 seconds total audio):**

| Concurrency | Latency | RTF |
|-------------|---------|-----|
| 1 | 876ms | 0.136 |
| 2 | 921ms | 0.074 |
| 4 | 1611ms | 0.070 |

---

## Decision Guide

**One-line rule:**

> English + ultra-lightweight + embedded/browser → **KittenTTS Nano**  
> Chinese + voice cloning + GPU available → **Spark TTS**

**By use case:**

| Use Case | Recommendation |
|----------|----------------|
| iOS/Android embedded voice assistant | KittenTTS Nano |
| Raspberry Pi / embedded hardware | KittenTTS Nano (Rust binary) |
| Pure browser web app TTS | KittenTTS (WASM build) |
| Chinese audiobook / podcast generation | Spark TTS |
| Chinese customer service / dubbing automation | Spark TTS |
| Voice cloning (read in your own voice) | Spark TTS |
| Chinese-English code-switching | Spark TTS |
| Offline English reading app (mobile) | KittenTTS Nano |

---

## My Assessment

**Two projects each at the top of their own track — which happen to be completely different tracks.**

KittenTTS solves "how do you have decent TTS where large models are impossible to run" — 25MB, CPU, ONNX, Rust single binary. Engineering compression taken to the extreme. Not a research demo — a real edge deployment solution. **No Chinese support is a hard limitation, but Chinese was never its battlefield.**

Spark TTS proves that a 0.5B LLM backbone can beat 8B competitors in Chinese TTS — better results with fewer parameters and less training data. Zero-shot voice cloning plus 100,000 hours of Chinese training data makes it the most practically valuable open-source Chinese TTS option available today.

If you work in Chinese content or Chinese products, Spark TTS is the most worth-trying open-source option right now. If you work in edge AI or browser-side voice, KittenTTS has no real competitors.

---

**KittenTTS GitHub**: KittenML/KittenTTS (14.1k stars)  
**KittenTTS Demo**: huggingface.co/spaces/KittenML/KittenTTS-Demo  
**Spark TTS GitHub**: SparkAudio/Spark-TTS (11k stars)  
**Spark TTS Paper**: arxiv.org/abs/2503.01710  
**Spark TTS Demo**: sparkaudio.github.io/spark-tts/
