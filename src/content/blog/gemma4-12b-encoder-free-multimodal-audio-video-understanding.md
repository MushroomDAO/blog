---
title: "Gemma 4 12B：无编码器多模态，原生音视频理解，16GB 笔记本可跑"
titleEn: "Gemma 4 12B: Encoder-Free Multimodal AI with Native Audio & Video, Runs on 16GB Laptop"
description: "Google DeepMind 发布 Gemma 4 12B Unified——首个中等规模无编码器多模态开源模型，原生支持文本、图像、音频、视频四模态输入，256K 上下文，GPQA Diamond 78.8%，16GB 显存即可本地运行，Apache 2.0 开源。"
descriptionEn: "Google DeepMind releases Gemma 4 12B Unified — the first mid-size encoder-free multimodal open model natively processing text, image, audio, and video. 256K context, 78.8% on GPQA Diamond, runs on 16GB VRAM, Apache 2.0."
pubDate: 2026-06-04
category: "Tech-News"
tags: ["Gemma", "Google DeepMind", "多模态", "音频理解", "视频理解", "开源模型", "本地部署", "LLM"]
heroImage: "../../assets/images/gemma4-12b-multimodal-audio-video-banner.jpg"
lang: "zh-CN"
---

## 第一个原生四模态中等规模开源模型

2026 年 6 月 3 日，Google DeepMind 正式发布 **Gemma 4 12B Unified**——Gemma 系列首个将文本、图像、音频、视频统一纳入同一 LLM backbone 处理的开源模型，参数量 11.95B，256K 上下文窗口，Apache 2.0 协议，16GB 显存的笔记本或 Apple Silicon Mac 即可本地运行。

这不只是参数规模上的更新，而是架构上的根本性改变：**彻底去掉了独立的视觉编码器和音频编码器**。

## 核心架构：为什么去掉编码器

此前 Gemma 系列中等规模模型的架构是：LLM + 550M 视觉编码器 + 300M 音频编码器。三个独立模块增加了延迟、内存开销，也让跨模态交互变得间接。

Gemma 4 12B Unified 用两个极轻量的投影层替代：

- **视觉嵌入（35M 参数）**：原始图像切成 48×48 像素 patch，通过单次矩阵乘法投影成 token，位置编码采用"分解坐标查询"方案
- **音频嵌入**：原始 16 kHz 音频切成 40ms 帧，线性投影到与文本 token 相同的嵌入空间，无需 Conformer 层

两种模态的 token 与文本 token 在同一 transformer 中统一处理，消除了模态转换的信息瓶颈。结果是性能接近参数量两倍以上的 26B MoE 模型，但内存占用不到其一半。

## 音频理解能力

| 能力 | 说明 |
|------|------|
| 自动语音识别（ASR） | 无需外部 ASR 管线，直接输入音频 |
| 说话人区分（Diarization） | 识别"谁在说话" |
| 语音转译文本 | 跨语言翻译，CoVoST 基准得分 38.5% |
| 多语言 | 预训练覆盖 140+ 语言，指令微调支持 35+ |

**使用限制**：单次音频输入最长 30 秒。模态顺序建议：音频放在文本**之后**输入。

快速调用示例：

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "请用中文转录以下音频："},
            {"type": "audio", "audio": "https://example.com/speech.wav"},
        ]
    }
]
```

## 视频理解能力

视频处理本质上是"带时间轴的帧序列 + 可选同步音频"。Gemma 4 12B 的处理方式：

- 按 1 FPS 采样帧，每帧分配 **70 token** 的视觉 token 预算（适合视频的低预算档）
- 单次视频输入最长 **60 秒**（最多 60 帧 × 70 token = 4,200 个视觉 token）
- 支持音视频同步输入，可同时理解画面内容与对话

官方演示：对一段 5 分钟的 Google I/O 主题演讲片段，模型以 313 帧 + 音频的方式输入，能正确回答"某个功能在哪个时间点被介绍"等细粒度问题。

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "video", "video": "https://example.com/keynote.mp4"},
            {"type": "text", "text": "总结这段视频的主要内容，并列出每个功能演示的时间点。"}
        ]
    }
]
```

## 主要基准评测

| 基准 | 得分 | 说明 |
|------|------|------|
| GPQA Diamond | **78.8%** | 博士级科学推理 |
| AIME 2026（无工具） | **77.5%** | 数学竞赛题 |
| MMLU Pro | **77.2%** | 通用知识 |
| LiveCodeBench v6 | **72.0%** | 代码生成 |
| Codeforces ELO | **1659** | 竞技编程 |
| MATH-Vision | **79.7%** | 视觉数学 |
| MMMU Pro（视觉） | **69.1%** | 多模态理解 |
| MRCR v2（128K 长上下文） | **43.4%** | 超长上下文召回 |
| CoVoST（音频翻译） | **38.5%** | 语音翻译 |
| FLEURS（ASR，越低越好） | **0.069 WER** | 语音识别错误率 |

Google 内部测试：在 Google AI Edge Eloquent 应用中部署后，整体质量提升 **60%+**。

## 模型系列对比

Gemma 4 共有五个规模档：

| 模型 | 总参数 | 上下文 | 音频 | 视频 |
|------|--------|--------|------|------|
| E2B | 5.1B | 128K | ✓ | ✓ |
| E4B | 8B | 128K | ✓ | ✓ |
| **12B Unified** | **11.95B** | **256K** | **✓** | **✓** |
| 31B | 30.7B | 256K | ✗ | ✓ |
| 26B A4B MoE | 25.2B（激活 3.8B） | 256K | ✗ | ✓ |

注意：31B 和 26B MoE **不支持音频输入**，音视频需求应优先选 12B Unified 或 E2B/E4B。

## 模型地址

| 版本 | HuggingFace 链接 |
|------|-----------------|
| 基础模型 | [google/gemma-4-12B](https://huggingface.co/google/gemma-4-12B) |
| 指令微调版 | [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) |
| 助手版 | [google/gemma-4-12B-it-assistant](https://huggingface.co/google/gemma-4-12B-it-assistant) |
| Unsloth（GGUF 量化） | [unsloth/gemma-4-12b-it-GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF) |
| Unsloth（原格式） | [unsloth/gemma-4-12b](https://huggingface.co/unsloth/gemma-4-12b) |

## 本地部署

**安装依赖：**

```bash
pip install -U transformers torch accelerate
```

**基础调用模板（推荐参数）：**

```python
from transformers import AutoProcessor, AutoModelForMultimodalLM

MODEL_ID = "google/gemma-4-12B-it"
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID, dtype="auto", device_map="auto"
)

inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    add_generation_prompt=True,
    enable_thinking=False,  # 改为 True 开启推理思考模式
).to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=1024,
    temperature=1.0,
    top_p=0.95,
    top_k=64,
)
```

**图像 token 预算选择（影响精度与速度）：**

| token 预算 | 适用场景 |
|-----------|---------|
| 70 / 140 | 视频帧、图像分类、图像描述 |
| 280 / 560 | 通用图像理解 |
| 1120 | OCR、文档解析、小字体识别 |

**兼容的推理框架：** llama.cpp、MLX（Apple Silicon）、vLLM、Ollama、SGLang、Unsloth、LM Studio

**Apple Silicon 一键体验：** Google AI Edge Gallery 或 Eloquent 应用（macOS）

## 为什么值得关注

Gemma 4 12B Unified 的意义在于三个"第一次并发"：

1. **开源 + 中等规模 + 原生四模态**——此前的多模态开源模型要么参数更大，要么不支持原生音频，要么需要多个独立模块拼接
2. **真正的消费级硬件可跑**——16GB 统一内存（M3 Pro MacBook Pro 或 RTX 4080 笔记本均可），不再是"开源但需要 A100"
3. **Apache 2.0 + 商业可用**——没有 NC 限制，可以直接用于产品构建

对于想做本地音视频 AI 应用的开发者：Gemma 4 12B 是目前开源生态里硬件门槛最低、模态最完整的选择。

---

**资源链接：**
- GitHub/HuggingFace：[google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it)
- 官方介绍：[Google DeepMind Releases Gemma 4 12B](https://www.marktechpost.com/2026/06/03/google-deepmind-releases-gemma-4-12b-an-encoder-free-multimodal-model-with-native-audio-that-runs-on-a-16-gb-laptop/)
- 开发者博客：[Gemma 4 12B: The Developer Guide](https://developers.googleblog.com/gemma-4-12b-the-developer-guide/)

<!--EN-->

## The First Mid-Size Encoder-Free Four-Modality Open Model

On June 3, 2026, Google DeepMind released **Gemma 4 12B Unified** — the first open model in the Gemma family to process text, images, audio, and video through a single unified LLM backbone. At 11.95B parameters with a 256K context window, Apache 2.0 licensed, it runs locally on a 16GB VRAM laptop or Apple Silicon Mac.

This isn't just a parameter count update. It's a fundamental architectural change: **complete elimination of separate vision and audio encoders**.

## Architecture: Why Remove the Encoders

Previous mid-size Gemma models used three separate modules: LLM + 550M vision encoder + 300M audio encoder. This introduced latency, memory overhead, and indirect cross-modal interaction.

Gemma 4 12B Unified replaces them with two ultra-lightweight projection layers:

- **Vision embedder (35M params)**: Raw images split into 48×48 pixel patches, projected via a single matrix multiplication with "factorized coordinate lookup" for position encoding
- **Audio embedder**: Raw 16 kHz audio sliced into 40ms frames, linearly projected into the same embedding space as text tokens — no Conformer layers needed

Both modalities' tokens are processed alongside text tokens in a unified transformer, eliminating the information bottleneck of modality conversion. The result: performance approaching the 26B MoE model at less than half the memory footprint.

## Audio Understanding

| Capability | Description |
|-----------|-------------|
| ASR | Direct audio input, no external ASR pipeline |
| Speaker Diarization | Identifies "who is speaking" |
| Speech-to-Translation | Cross-language translation; CoVoST score: 38.5% |
| Multilingual | Pre-trained on 140+ languages, instruction-tuned on 35+ |

**Limits**: Maximum 30 seconds of audio per input. Recommended order: audio placed **after** text.

## Video Understanding

Video processing treats video as a timestamped frame sequence with optional synchronized audio:

- Sampled at 1 FPS, with **70 tokens** per frame (low-budget tier suited for video)
- Maximum **60 seconds** per video input (60 frames × 70 tokens = 4,200 visual tokens)
- Supports synchronized audio+video input for joint understanding of visuals and dialogue

Official demo: a 5-minute Google I/O keynote segment was input as 313 frames + audio, enabling fine-grained Q&A like "at what timestamp was feature X introduced."

## Key Benchmarks

| Benchmark | Score | Domain |
|-----------|-------|--------|
| GPQA Diamond | **78.8%** | Graduate-level science reasoning |
| AIME 2026 (no tools) | **77.5%** | Math competition |
| MMLU Pro | **77.2%** | General knowledge |
| LiveCodeBench v6 | **72.0%** | Code generation |
| Codeforces ELO | **1659** | Competitive programming |
| MATH-Vision | **79.7%** | Visual math |
| MMMU Pro (Vision) | **69.1%** | Multimodal understanding |
| MRCR v2 (128K long context) | **43.4%** | Long-context recall |
| CoVoST (Audio) | **38.5%** | Speech translation |
| FLEURS (ASR, lower is better) | **0.069 WER** | Speech recognition error rate |

Internal testing: **60%+ quality improvement** in Google AI Edge Eloquent app deployment.

## Model Variants

| Model | Total Params | Context | Audio | Video |
|-------|-------------|---------|-------|-------|
| E2B | 5.1B | 128K | ✓ | ✓ |
| E4B | 8B | 128K | ✓ | ✓ |
| **12B Unified** | **11.95B** | **256K** | **✓** | **✓** |
| 31B | 30.7B | 256K | ✗ | ✓ |
| 26B A4B MoE | 25.2B (3.8B active) | 256K | ✗ | ✓ |

Note: 31B and 26B MoE **do not support audio input**. For audio+video tasks, use 12B Unified or E2B/E4B.

## Model Links

| Version | HuggingFace |
|---------|-------------|
| Base model | [google/gemma-4-12B](https://huggingface.co/google/gemma-4-12B) |
| Instruction-tuned | [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) |
| Assistant | [google/gemma-4-12B-it-assistant](https://huggingface.co/google/gemma-4-12B-it-assistant) |
| Unsloth GGUF | [unsloth/gemma-4-12b-it-GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF) |

## Why It Matters

Gemma 4 12B Unified achieves three "firsts simultaneously":

1. **Open source + mid-size + native four-modality** — prior multimodal open models were either much larger, lacked native audio, or required multiple stitched modules
2. **Genuinely consumer-hardware capable** — 16GB unified memory (M3 Pro MacBook Pro or RTX 4080 laptop), not "open source but needs an A100"
3. **Apache 2.0 + commercial use** — no NC restrictions, build products directly

For developers building local audio/video AI applications: Gemma 4 12B is currently the lowest-barrier, most modality-complete option in the open-source ecosystem.

---

**Resources:**
- HuggingFace: [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it)
- MarkTechPost coverage: [Google DeepMind Releases Gemma 4 12B](https://www.marktechpost.com/2026/06/03/google-deepmind-releases-gemma-4-12b-an-encoder-free-multimodal-model-with-native-audio-that-runs-on-a-16-gb-laptop/)
- Developer Guide: [developers.googleblog.com](https://developers.googleblog.com/gemma-4-12b-the-developer-guide/)
