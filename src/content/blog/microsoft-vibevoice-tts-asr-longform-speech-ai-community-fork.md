---
title: "微软 VibeVoice：54K stars 前沿语音 AI，官方仓库因深度伪造顾虑下架，社区 fork 接棒"
titleEn: "Microsoft VibeVoice: 54K-Star Frontier Voice AI, Official Repo Pulled Over Deepfake Concerns, Community Fork Carries On"
description: "microsoft/VibeVoice，54K stars，MIT，Python。7.5Hz 连续语音 tokenizer + LLM + 扩散头，单次推理 90 分钟 TTS、60 分钟 ASR，4 路说话人。2025-09 官方因深度伪造顾虑主动下架，社区 fork vibevoice-community/VibeVoice 接棒维护，已加 LoRA 微调和 HF Transformers 集成。工程指导：模型选型、API 服务化、BitNet CPU 推理路径。"
descriptionEn: "microsoft/VibeVoice, 54K stars, MIT, Python. 7.5Hz continuous speech tokenizer + LLM + diffusion head; single-pass 90-min TTS and 60-min ASR with up to 4 speakers. Microsoft pulled the official repo in Sep 2025 over deepfake concerns; the community fork vibevoice-community/VibeVoice continues with LoRA fine-tuning and HF Transformers integration. Engineering guide: model selection, API server setup, BitNet CPU inference path."
pubDate: "2026-09-20"
updatedDate: "2026-09-20"
category: "Tech-Experiment"
tags: ["TTS", "ASR", "Microsoft", "voice-AI", "speech-synthesis", "local-AI", "LoRA", "deepfake", "open-source"]
heroImage: "../../assets/images/microsoft-vibevoice-tts-asr-longform-speech-ai-community-fork-banner.jpg"
---

> 📌 官方（已下架）：https://github.com/microsoft/VibeVoice — Stars：54,415 | License：MIT
> 社区 Fork：https://github.com/vibevoice-community/VibeVoice — Stars：1,585 | MIT
> 语言：Python | 官方创建：2025-08-25 | 下架时间：2025-09

---

2025 年 8 月，微软研究院发布 VibeVoice，一个开源前沿语音 AI 框架，54K stars，MIT 协议，一个月内成为 GitHub 上最受关注的语音 AI 项目之一。

然后微软在 2025 年 9 月主动把官方仓库设为 disabled，原因是：担心被用于深度伪造和不在研究范围内的场景，"直到我们确信超出预期范围的使用不再可能发生"。

社区在 9 月 4 日就已经 fork，现在由 `vibevoice-community/VibeVoice` 维护，加了训练代码和 HF Transformers 集成，是目前可访问的工程入口。

---

## 架构：7.5Hz + LLM + 扩散

VibeVoice 的核心设计决策是**超低帧率的连续语音 tokenizer**：以 7.5Hz（每秒 7.5 个 token）而不是传统的 50-100Hz 对语音编码，同时维持音频质量。

这个设计解决了 TTS 长序列生成的根本矛盾——高帧率精度好但序列太长，低帧率序列短但精度差。7.5Hz 通过双路 tokenizer（声学 + 语义）绕过了这个取舍：

```
输入文本
  ↓ LLM（理解语义，预测下一个 token）
  ↓ Diffusion Head（从 token 生成高保真声学细节）
  ↓ Decoder（连续语音 token → 音频波形）
输出音频
```

用 LLM 做序列预测，用扩散头做声学还原——LLM 负责"说什么、怎么说"，扩散负责"听起来怎么样"。

---

## 五款模型，按场景选

| 模型 | 参数量 | 最长单次生成 | 说话人数 | 推理需求 |
|------|--------|------------|--------|---------|
| **VibeVoice-TTS** | 1.5B | ~90 分钟 | 最多 4 人 | GPU |
| **VibeVoice-TTS-7B**（社区） | 7B | ~45 分钟 | 最多 4 人 | GPU（大显存） |
| **VibeVoice-Realtime** | 0.5B | 流式，无上限 | 1 人 | GPU |
| **VibeVoice-ASR** | 7B | ~60 分钟 | 多说话人 | GPU |
| **VibeVoice-ASR-BitNet** | ~1.58GB（量化） | ~60 分钟 | 多说话人 | CPU，≥3 线程 |

**选型建议**：

- 有声书、播客制作（90 分钟内，多角色）→ **TTS 1.5B**
- 实时语音助手、低延迟场景 → **Realtime 0.5B**（~300ms 延迟）
- 长录音转录 + 说话人识别 → **ASR 7B**
- 边缘设备/服务器无 GPU → **ASR-BitNet**（RTF < 1，3 线程 CPU 可实时跑）
- 追求 ASR 最高质量 → **ASR 7B**（精度更高但需 GPU）

---

## ASR 的结构化输出

VibeVoice-ASR 的一个实用设计是把三件事合并进一次推理：

- **Who（谁在说）**：说话人分离（diarization）
- **When（什么时候说）**：时间戳
- **What（说了什么）**：转录内容

单次 60 分钟音频直接出带时间轴、带说话人标签的结构化文本，不需要分段处理或多次推理。这对会议录音、采访转录、多角色有声内容处理很直接。

支持语言：50+ 种，中英文均覆盖。另有流式 ASR 变体用于实时场景。

还有可定制**热词（Hotword）**支持——对产品名、专有名词识别率低的问题可以针对性加强。

---

## 社区 Fork 安装

官方 repo 已下架，走社区 fork：

```bash
git clone https://github.com/vibevoice-community/VibeVoice.git
cd VibeVoice/
uv pip install -e .
```

模型从 HuggingFace 下载（需配置 `HF_TOKEN`）：

```python
from vibevoice import VibeVoice

# TTS 1.5B：长文本多角色
tts = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-1.5B")

# Realtime：流式低延迟
tts_rt = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-Streaming-0.5B")

# ASR：长录音转录
asr = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-ASR-7B")
```

**Gradio Demo（本地测试用）**：

```bash
python demo_gradio.py --model vibevoice-community/VibeVoice-1.5B
```

---

## OpenAI API 兼容服务化

如果需要把 VibeVoice 接进现有的 TTS 工作流，`marhensa/vibevoice-realtime-openai-api`（88 stars）提供了 OpenAI `/v1/audio/speech` 兼容服务器：

```bash
git clone https://github.com/marhensa/vibevoice-realtime-openai-api
cd vibevoice-realtime-openai-api
# Docker 启动（推荐，含模型下载）
docker compose up -d

# 调用方式和 OpenAI TTS API 完全一致
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "vibevoice-realtime", "input": "Hello world", "voice": "alloy"}' \
  --output speech.mp3
```

支持 OpenAI 的 voice 名称别名（alloy、echo、fable 等）映射到 VibeVoice 的声线，零改动接进现有代码。

---

## BitNet CPU 推理路径

对没有 GPU 的环境，`VibeVoice-ASR-BitNet` 是唯一可以 CPU 实时跑的方案：

- 模型体积：1.58GB（量化后）
- RTF（实时率）< 1，即：处理 60 秒音频用时少于 60 秒
- 要求：≥3 个 CPU 线程

```python
from vibevoice import VibeVoice

asr = VibeVoice.from_pretrained(
    "vibevoice-community/VibeVoice-ASR-BitNet",
    device="cpu",
    num_threads=4  # 匹配物理核数
)

result = asr.transcribe("meeting.wav")
# result 包含 text、speakers、timestamps
```

CPU 线程数设到等于物理核数效果最好；超过物理核数通常反而变慢（调度开销）。

---

## LoRA 微调（社区新增）

官方版本没有训练代码，社区 fork 加入了非官方 LoRA 微调支持：

```bash
# 准备数据：音频 + 文本对
# 训练
python train_lora.py \
  --base_model vibevoice-community/VibeVoice-1.5B \
  --data_dir ./my_audio_data \
  --output_dir ./lora_checkpoints \
  --epochs 3

# 推理时加载 LoRA
tts = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-1.5B")
tts.load_lora("./lora_checkpoints/epoch_3")
```

微调场景：特定说话人声线适配、特定领域专有词汇发音优化、语调风格迁移。

---

## 官方下架：技术与治理的张力

微软在发布后约两周把仓库设为 disabled，官方说明是："我们在确认超出预期范围的使用不再可能发生之前，暂时禁用该仓库。"

这类决策背后的工程逻辑：MIT 协议发布 → 无法控制使用方式 → 高质量 TTS 本质上降低了制造高可信度伪造音频的门槛。

几个技术事实值得如实说清楚：
1. 社区 fork 在官方下架前就存在，MIT 协议允许这样做
2. 代码和模型权重已经流通，下架不能收回已经发布的内容
3. 官方仓库虽然 disabled，54K stars 计数仍然可见

这个事件展示了开源 AI 发布的一种典型困境：发布意味着失去控制，不发布意味着错失社区价值。VibeVoice 的处理方式（事后下架）无法真正解决这个矛盾，但至少表达了明确的立场。

---

## 局限

- **不建议商用**：官方文档明确写"不推荐在没有进一步测试的情况下用于商业或真实世界应用"
- **社区 fork 的训练代码是非官方的**，质量和稳定性未经原团队验证
- **ASR-BitNet 精度低于 ASR-7B**，量化有损失，高要求场景不适用
- **深度伪造风险**是真实的工程和伦理考量，使用前需要明确应用场景合规性
- **官方不再维护**，社区 fork 的长期活跃度取决于社区贡献

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Official (disabled): https://github.com/microsoft/VibeVoice — Stars: 54,415 | MIT
> Community Fork: https://github.com/vibevoice-community/VibeVoice — Stars: 1,585 | MIT
> Language: Python | Official created: 2025-08-25 | Pulled: 2025-09

---

In August 2025, Microsoft Research released VibeVoice, an open-source frontier voice AI framework. 54K stars, MIT license — it became one of GitHub's most-watched voice AI projects within a month.

Then Microsoft disabled the official repository in September 2025, citing concerns about deepfake use and applications outside the intended research scope: "we have disabled the repo until we are confident that out-of-scope use is no longer possible."

The community had already forked it on September 4th. `vibevoice-community/VibeVoice` now maintains the codebase with LoRA fine-tuning and HF Transformers integration added — the practical engineering entry point.

---

## Architecture: 7.5Hz + LLM + Diffusion

VibeVoice's core design choice is an **ultra-low frame-rate continuous speech tokenizer**: 7.5Hz (7.5 tokens per second) instead of the typical 50-100Hz, while maintaining audio quality.

This resolves the fundamental tension in long-sequence TTS generation — high frame rates give better fidelity but produce excessively long sequences; low frame rates are efficient but lose precision. VibeVoice sidesteps this with dual tokenizers (acoustic + semantic):

```
Input text
  ↓ LLM (understands semantics, predicts next token)
  ↓ Diffusion Head (generates high-fidelity acoustic detail from tokens)
  ↓ Decoder (continuous speech tokens → audio waveform)
Output audio
```

The LLM handles "what to say and how," the diffusion head handles "what it sounds like."

---

## Five Models — Select by Use Case

| Model | Params | Max Single-Pass | Speakers | Hardware |
|-------|--------|----------------|----------|----------|
| **VibeVoice-TTS** | 1.5B | ~90 min | Up to 4 | GPU |
| **VibeVoice-TTS-7B** (community) | 7B | ~45 min | Up to 4 | GPU (large VRAM) |
| **VibeVoice-Realtime** | 0.5B | Streaming, unlimited | 1 | GPU |
| **VibeVoice-ASR** | 7B | ~60 min | Multi-speaker | GPU |
| **VibeVoice-ASR-BitNet** | ~1.58GB (quantized) | ~60 min | Multi-speaker | CPU, ≥3 threads |

**Selection guide:**
- Audiobooks, podcasts (90 min, multiple characters) → **TTS 1.5B**
- Real-time voice assistant, low-latency → **Realtime 0.5B** (~300ms latency)
- Long recording transcription + speaker identification → **ASR 7B**
- Edge devices / no GPU → **ASR-BitNet** (RTF < 1, runs real-time on 3 CPU threads)

---

## ASR's Structured Output

VibeVoice-ASR bundles three tasks into a single inference pass:
- **Who**: speaker diarization
- **When**: timestamps
- **What**: transcription

A 60-minute audio file produces structured text with timeline and speaker labels — no chunking, no multiple passes. This is immediately practical for meeting recordings, interviews, and multi-character audio content.

50+ languages supported, including Chinese and English. A streaming ASR variant handles real-time scenarios. Customizable **hotword** support addresses proper noun recognition gaps.

---

## Community Fork Installation

The official repo is disabled; use the community fork:

```bash
git clone https://github.com/vibevoice-community/VibeVoice.git
cd VibeVoice/
uv pip install -e .
```

Download models from HuggingFace (requires `HF_TOKEN`):

```python
from vibevoice import VibeVoice

# TTS 1.5B: long-form multi-speaker
tts = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-1.5B")

# Realtime: streaming low-latency
tts_rt = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-Streaming-0.5B")

# ASR: long recording transcription
asr = VibeVoice.from_pretrained("vibevoice-community/VibeVoice-ASR-7B")
```

Local Gradio demo for testing:

```bash
python demo_gradio.py --model vibevoice-community/VibeVoice-1.5B
```

---

## OpenAI-Compatible API Server

To integrate VibeVoice into existing TTS workflows, `marhensa/vibevoice-realtime-openai-api` provides an OpenAI `/v1/audio/speech`-compatible server:

```bash
git clone https://github.com/marhensa/vibevoice-realtime-openai-api
cd vibevoice-realtime-openai-api
docker compose up -d

# Same call signature as OpenAI TTS API
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "vibevoice-realtime", "input": "Hello world", "voice": "alloy"}' \
  --output speech.mp3
```

OpenAI voice name aliases (alloy, echo, fable, etc.) map to VibeVoice voices — zero code changes to existing integrations.

---

## BitNet CPU Inference

For GPU-less environments, `VibeVoice-ASR-BitNet` is the only real-time-capable CPU option:

- Model size: 1.58GB (quantized)
- RTF (real-time factor) < 1: processing 60 seconds of audio takes under 60 seconds
- Requirement: ≥3 CPU threads

```python
asr = VibeVoice.from_pretrained(
    "vibevoice-community/VibeVoice-ASR-BitNet",
    device="cpu",
    num_threads=4  # match physical core count
)
result = asr.transcribe("meeting.wav")
# result: text, speakers, timestamps
```

Set thread count to match physical cores; oversubscribing physical cores usually increases latency from scheduling overhead.

---

## The Repo Pull: Technology and Governance Tension

Microsoft disabled the repository roughly two weeks after release, with the stated reason of preventing out-of-scope use.

The engineering logic: MIT license release → no control over downstream use → high-quality TTS fundamentally lowers the barrier for convincing synthetic audio.

A few technical facts worth stating accurately:
1. The community fork existed before the official pull; MIT license permits this
2. Code and model weights were already distributed; pulling the repo can't recall released artifacts
3. The official repo is disabled but its 54K star count remains visible

This event illustrates a recurring tension in open-source AI releases: publishing means losing control; not publishing means losing community value. Microsoft's approach (post-hoc pull) doesn't resolve the underlying tension, but it does establish a clear position.

---

## Limitations

- **Not recommended for production**: the official documentation explicitly states "we do not recommend using VibeVoice in commercial or real-world applications without further testing"
- **Community fork training code is unofficial** and hasn't been validated by the original team
- **ASR-BitNet has lower accuracy than ASR-7B** — quantization has quality costs
- **Deepfake risk is real** — clarify compliance for your use case before deploying
- **Official maintenance has stopped**; the community fork's longevity depends on contributor activity

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
