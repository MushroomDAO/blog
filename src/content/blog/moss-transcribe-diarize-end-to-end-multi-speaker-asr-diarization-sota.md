---
title: "MOSS-Transcribe-Diarize 0.9B：端到端多说话人转写+说话人分离，一个模型搞定，INTERSPEECH 2026 冠军"
titleEn: "moss-transcribe-diarize-end-to-end-multi-speaker-asr-diarization-sota"
description: "OpenMOSS 开源的 MOSS-Transcribe-Diarize 0.9B（1.5K stars），SOTA 端到端音频理解模型，一个模型同时完成长音频多说话人转写、说话人分离（diarization）、精确时间戳和声学事件标注。架构：Qwen3-0.6B 解码器 + Whisper-Medium 编码器 + 4x 时序合并 MLP 桥接。支持 50+ 语言。输出格式 [时间戳][S01]文本[时间戳]。在 AISHELL-4/Alimeeting/Podcast/Movies 四个基准上超越 Doubao、ElevenLabs、GPT-4o、Gemini 3 Pro。支持 SGLang Omni / vLLM 推理，H100 单卡 98 audio_s/s。赢得 INTERSPEECH 2026 第二届 MLC-SLM 挑战赛冠军。"
descriptionEn: "OpenMOSS open-source MOSS-Transcribe-Diarize 0.9B (1.5K stars) — SOTA end-to-end audio understanding model that jointly handles long-form multi-speaker transcription, speaker diarization, precise timestamps, and acoustic event annotation in a single pass. Architecture: Qwen3-0.6B decoder + Whisper-Medium encoder + 4x temporal merge MLP bridge. 50+ languages. Output format [timestamp][S01]text[timestamp]. Outperforms Doubao, ElevenLabs, GPT-4o, Gemini 3 Pro on AISHELL-4/Alimeeting/Podcast/Movies. Supports SGLang Omni / vLLM inference at 98 audio_s/s on a single H100. Won 1st place in 2nd MLC-SLM Challenge at INTERSPEECH 2026."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["语音识别", "说话人分离", "多说话人", "转写", "ASR", "开源", "会议纪要", "端到端"]
heroImage: "../../assets/images/moss-transcribe-diarize-end-to-end-multi-speaker-asr-diarization-sota-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：OpenMOSS/MOSS-Transcribe-Diarize  
HuggingFace：OpenMOSS-Team/MOSS-Transcribe-Diarize  
arXiv：2601.01554  
许可证：Apache 2.0  
语言：Python  
Stars：1,578 · Forks：89  
HF 月下载量：278,727 · HF Likes：386  
开源日期：2026-07-09

---

## 一、问题背景

把多人录音转写成结构化文本，传统上需要拼接两个独立系统：

1. **ASR**（自动语音识别）——把语音转成文字
2. **说话人分离（Diarization）**——把音频切分成「谁说了什么」

两个系统各有误差，误差叠加后结果往往一塌糊涂。说话人边界标错了，ASR 文本就乱；ASR 词错了，说话人对齐就偏。更麻烦的是，这两件事的错误不是独立的。

MOSS-Transcribe-Diarize 的做法：**一个模型，一次前向，同时输出转写文本 + 说话人标签 + 精确时间戳**。

---

## 二、输出格式

MTD 的输出是紧凑的时间戳 + 说话人流：

```text
[0.48][S01]Welcome everyone[1.66][12.26][S02]The new transcription pipeline is ready for evaluation[13.81][14.36][S01]Great, include the diarization results in the report[18.76]
```

格式规则：`[开始时间][Sxx]转写文本[结束时间]`，相邻片段首尾相接，不插空白。

- 时间戳单位：秒
- 说话人标签：`[S01]`、`[S02]`……支持任意多个说话人
- 可选输出：声学事件标注（笑声、鼓掌、噪声等）

---

## 三、模型架构

| 组件 | 规格 |
|------|------|
| 文本骨干 | Qwen3-0.6B 风格因果解码器 |
| 音频编码器 | Whisper-Medium 编码器配置 |
| 音频前端 | WhisperFeatureExtractor，16 kHz，80 mel bins，30 秒分块 |
| 音频-文本桥接 | 4x 时序合并 + MLP 适配器 |
| 融合方式 | 音频特征通过 `masked_scatter` 替换 `<|audio_pad|>` 嵌入 |

两个经典组件（Qwen3 解码器 + Whisper 编码器）通过 MLP 桥接融合，不是从头设计新架构。桥接层做 4x 时序合并，把 Whisper 的帧级特征压缩到更合适的粒度再输入解码器。

模型大小 0.9B，设计目标是可以在单个消费级 GPU 或服务器上高效推理。

---

## 四、评测结果

基准：AISHELL-4（普通话会议）、Alimeeting（会议）、Podcast（播客）、Movies（影视）

指标：CER（字符错误率）、cpCER（拼接最小置换 CER，联合评估转写和分离质量）、Δcp（cpCER - CER，衡量分离误差的额外贡献）。三个指标均越低越好。

| 模型 | AISHELL-4 cpCER | Alimeeting cpCER | Podcast cpCER | Movies cpCER |
|------|----------------|-----------------|--------------|-------------|
| Doubao | 27.86 | 37.57 | 10.54 | 30.88 |
| ElevenLabs | 37.95 | 36.69 | 11.34 | 17.85 |
| GPT-4o | - | - | - | 23.67 |
| Gemini 2.5 Pro | 53.42 | 41.64 | 10.23 | 24.15 |
| Gemini 3 Pro | 27.43 | 32.84 | - | 14.73 |
| **MTD 0.9B** | **15.83** | **22.17** | **7.37** | **12.76** |
| MTD Pro | **14.02** | **13.94** | **6.97** | **11.78** |

MTD 0.9B 在所有有数据的基准上均超过 Doubao、ElevenLabs、GPT-4o 和 Gemini。在 Podcast Δcp（转写质量指标）上以 1.40 拿下最优，说话人分离引入的额外错误最小。

**2026 年 7 月，MTD 赢得 INTERSPEECH 2026 第二届 MLC-SLM 挑战赛冠军**（14 个语言覆盖）。

---

## 五、安装与快速上手

```bash
git clone https://github.com/OpenMOSS/MOSS-Transcribe-Diarize.git
cd MOSS-Transcribe-Diarize
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[torch-runtime]" --torch-backend=auto
```

Python 直接调用：

```python
from moss_transcribe_diarize import parse_transcript
from moss_transcribe_diarize.inference_utils import (
    build_transcription_messages,
    generate_transcription,
    resolve_device,
)
from transformers import AutoProcessor
from moss_transcribe_diarize.attention import load_model_with_attention_fallback

model_id = "OpenMOSS-Team/MOSS-Transcribe-Diarize"
processor = AutoProcessor.from_pretrained(model_id)
model = load_model_with_attention_fallback(model_id)
```

---

## 六、生产服务

### SGLang Omni（推荐，CUDA 13）

```bash
sgl-omni serve \
  --model-path OpenMOSS-Team/MOSS-Transcribe-Diarize \
  --port 8000 \
  --max-running-requests 16 \
  --mem-fraction-static 0.80
```

接口兼容 OpenAI `/v1/audio/transcriptions`：

```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F model=OpenMOSS-Team/MOSS-Transcribe-Diarize \
  -F file=@audio.wav \
  -F response_format=verbose_json \
  -F max_new_tokens=65536
```

单 H100 性能（SGLang Omni）：

| 场景 | 并发 16 audio_s/s | 含义 |
|------|-----------------|------|
| 短音频 | 81.98 | 处理速度是实时的 81x |
| 长音频（多小时） | 98.83 | 处理速度是实时的 98x |

### vLLM（CUDA 12/13）

```bash
vllm serve OpenMOSS-Team/MOSS-Transcribe-Diarize --trust-remote-code
```

---

## 七、字幕 Web 界面

```bash
mtd-subtitle-web \
  --model OpenMOSS-Team/MOSS-Transcribe-Diarize \
  --host 127.0.0.1 --port 7860
```

打开 `http://127.0.0.1:7860`，上传音频或视频，查看解析后的字幕片段，导出 JSON / SRT / ASS，或用 FFmpeg 烧录到 MP4。

批量处理：

```bash
mtd-subtitle /path/to/input.mp4 \
  --model OpenMOSS-Team/MOSS-Transcribe-Diarize \
  --out-dir runs/example \
  --render
```

---

## 八、自定义提示词与热词

默认提示词：

```text
请将音频转写为文本，每一段需以起始时间戳和说话人编号（[S01]、[S02]、[S03]…）开头，
正文为对应的语音内容，并在段末标注结束时间戳，以清晰标明该段语音范围。
```

加热词（在末尾追加）：

```text
热词提示：热词1, 热词2, 热词3
```

---

## 九、生态

**端侧与边缘部署：**
- `localai-org/moss-transcribe.cpp`：C++17 ggml 全量重写，无 Python 依赖
- `yongyizang/tinymoss-diarize`：2.911-bit ARM NEON 内核，面向移动端/嵌入式

**工作流集成：**
- `T8mars/Comfyui-MOSS-Transcribe-Diarize-T8`：ComfyUI V3 节点，本地视频字幕工作流

**微调与蒸馏：**
- `vieenrose/distil-vibevoice-asr`：在 MTD 基础上继续微调 + ONNX/sherpa-onnx 端侧部署

---

端到端的价值在于：当 ASR 和 diarization 在同一个模型里联合训练时，错误不再叠加——模型同时学习「谁在说话」和「说了什么」，两个任务可以互相纠正。MTD 0.9B 的评测数字验证了这一点：在多个基准上，它用 0.9B 参数做到了比 GPT-4o 和 Gemini 系列更低的联合错误率。

iPhone 一键录音 → iCloud 同步 → MTD 转写分离 → AI 纪要/分析 → 知识沉淀，这条流水线已经在实际使用中跑通。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## MOSS-Transcribe-Diarize 0.9B: End-to-End Multi-Speaker Transcription and Diarization, Single Model, INTERSPEECH 2026 Champion

*by Mycelium Protocol*

---

GitHub: OpenMOSS/MOSS-Transcribe-Diarize  
HuggingFace: OpenMOSS-Team/MOSS-Transcribe-Diarize  
arXiv: 2601.01554  
License: Apache 2.0  
Language: Python  
Stars: 1,578 · Forks: 89  
HF monthly downloads: 278,727 · HF Likes: 386  
Open-sourced: 2026-07-09

---

### The Problem

Converting multi-speaker recordings into structured text traditionally requires stitching two separate systems:

1. **ASR** — speech to text
2. **Speaker Diarization** — segmenting audio into "who said what"

Errors compound. A wrong speaker boundary corrupts the transcript. An ASR error misaligns the speaker label. These failures are correlated, not independent.

MOSS-Transcribe-Diarize: **one model, one forward pass, simultaneous transcript + speaker labels + timestamps.**

---

### Output Format

```text
[0.48][S01]Welcome everyone[1.66][12.26][S02]The new transcription pipeline is ready[13.81][14.36][S01]Great, include the diarization results[18.76]
```

Format: `[start_time][Sxx]transcribed speech[end_time]`, segments concatenated without gaps. Speaker labels `[S01]`, `[S02]`… scale to any number of speakers. Optional acoustic event annotations are also available.

---

### Architecture

| Component | Specification |
|-----------|--------------|
| Text backbone | Qwen3-0.6B style causal decoder |
| Audio encoder | Whisper-Medium encoder configuration |
| Audio frontend | WhisperFeatureExtractor, 16 kHz, 80 mel bins, 30s chunks |
| Audio-text bridge | 4x temporal merge + MLP adaptor |
| Fusion | Audio features replace `<|audio_pad|>` embeddings via `masked_scatter` |

Two proven components (Qwen3 decoder + Whisper encoder) fused via MLP bridge. The 4x temporal merge in the bridge compresses Whisper's frame-level features to a granularity the decoder can process efficiently. Total size: 0.9B.

---

### Evaluation

Benchmarks: AISHELL-4 (Mandarin meetings), Alimeeting (meetings), Podcast, Movies  
Metrics: CER (character error rate), cpCER (concatenated minimum-permutation CER — jointly evaluating transcription and diarization quality), Δcp (cpCER − CER, measuring how much diarization adds to the error). Lower is better on all three.

| Model | AISHELL-4 cpCER | Alimeeting cpCER | Podcast cpCER | Movies cpCER |
|-------|----------------|-----------------|--------------|-------------|
| Doubao | 27.86 | 37.57 | 10.54 | 30.88 |
| ElevenLabs | 37.95 | 36.69 | 11.34 | 17.85 |
| GPT-4o | — | — | — | 23.67 |
| Gemini 2.5 Pro | 53.42 | 41.64 | 10.23 | 24.15 |
| Gemini 3 Pro | 27.43 | 32.84 | — | 14.73 |
| **MTD 0.9B** | **15.83** | **22.17** | **7.37** | **12.76** |
| MTD Pro | **14.02** | **13.94** | **6.97** | **11.78** |

MTD 0.9B beats Doubao, ElevenLabs, GPT-4o, and Gemini on every benchmark with available data. On Podcast Δcp (1.40, best overall), it adds the least diarization error on top of transcription quality.

**July 2026: MTD won 1st place in the 2nd MLC-SLM Challenge at INTERSPEECH 2026, covering 14 languages.**

---

### Install and Quickstart

```bash
git clone https://github.com/OpenMOSS/MOSS-Transcribe-Diarize.git
cd MOSS-Transcribe-Diarize
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[torch-runtime]" --torch-backend=auto
```

---

### Production Serving

**SGLang Omni** (recommended, CUDA 13):

```bash
sgl-omni serve \
  --model-path OpenMOSS-Team/MOSS-Transcribe-Diarize \
  --port 8000 --max-running-requests 16 --mem-fraction-static 0.80
```

OpenAI-compatible `/v1/audio/transcriptions`:

```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F model=OpenMOSS-Team/MOSS-Transcribe-Diarize \
  -F file=@audio.wav \
  -F response_format=verbose_json \
  -F max_new_tokens=65536
```

Single H100 throughput (SGLang Omni, concurrency 16):

| Scenario | audio_s/s | Meaning |
|----------|----------|---------|
| Short audio | 81.98 | Processes at 81× real-time |
| Long audio | 98.83 | Processes at 98× real-time |

**vLLM** (CUDA 12/13):

```bash
vllm serve OpenMOSS-Team/MOSS-Transcribe-Diarize --trust-remote-code
```

---

### Subtitle Web App

```bash
mtd-subtitle-web --model OpenMOSS-Team/MOSS-Transcribe-Diarize --host 127.0.0.1 --port 7860
```

Upload audio/video, review speaker-segmented subtitles, export JSON/SRT/ASS or FFmpeg-burn to MP4. Supports Chinese and English UI.

---

### Ecosystem

- **`localai-org/moss-transcribe.cpp`**: C++17 ggml from-scratch port, no Python
- **`yongyizang/tinymoss-diarize`**: 2.911-bit ARM NEON kernels for mobile/edge
- **`T8mars/Comfyui-MOSS-Transcribe-Diarize-T8`**: ComfyUI V3 nodes for local video subtitle workflows
- **`vieenrose/distil-vibevoice-asr`**: Fine-tuning on MTD + ONNX/sherpa-onnx for on-device deployment

---

### Why End-to-End Matters

When ASR and diarization train jointly in the same model, errors stop compounding — the model simultaneously learns "who is speaking" and "what they said," and each task corrects the other. MTD 0.9B's benchmarks confirm this: 0.9B parameters, lower joint error rate than GPT-4o and Gemini across multiple benchmarks.

iPhone one-tap recording → iCloud sync → MTD transcription + diarization → AI summary/analysis → knowledge capture. This pipeline runs in production today.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
