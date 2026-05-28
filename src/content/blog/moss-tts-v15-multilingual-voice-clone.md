---
title: "MOSS-TTS v1.5：31 种语言、显式停顿控制、更稳的声音克隆，Apache 2.0 开源"
titleEn: "MOSS-TTS v1.5: 31 Languages, Explicit Pause Control, Stabler Voice Cloning — Apache 2.0 Open Source"
description: "复旦 NLP、上海创新研究院、模思智能联合的 OpenMOSS 团队发布 MOSS-TTS v1.5：31 种语言、[pause 3.2s] 显式停顿控制、声音克隆方差更小、标点韵律更自然，Apache 2.0 商用友好，PyTorch/GGUF/ONNX/MLX 全部支持。"
descriptionEn: "OpenMOSS (Fudan NLP / Shanghai Innovation Institute / MOSI.AI) releases MOSS-TTS v1.5: 31 languages, [pause X.Ys] inline pause control, lower variance voice cloning, improved punctuation prosody. Apache 2.0, supports PyTorch/GGUF/ONNX/MLX."
pubDate: "2026-05-28"
updatedDate: "2026-05-28"
category: "Tech-News"
tags: ["TTS", "语音合成", "开源", "MOSS-TTS", "声音克隆", "多语言", "AI语音", "OpenMOSS"]
heroImage: "../../assets/banner-ai-personal-assistant.jpg"
---

复旦 NLP、上海创新研究院和模思智能联合的 OpenMOSS 团队把 MOSS-TTS v1.5 推上来了。v1.0 的底子已经在 Seed-TTS-eval 上跑出了开源 SOTA，v1.5 没有大改架构，而是做了一轮开发者真正在意的针对性打磨。

> 📌 GitHub：https://github.com/OpenMOSS/MOSS-TTS  
> HuggingFace v1.5：https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5  
> 技术报告：https://arxiv.org/pdf/2603.18090  
> 协议：Apache 2.0（商用友好）

## v1.5 的四个实质变化

### 多语言扩到 31 种

保留 v1.0 的 20 种语言，新增：粤语、荷兰语、芬兰语、印地语、马其顿语、马来语、罗马尼亚语、斯瓦希里语、他加禄语、泰语、越南语。

调用时显式带上语言标签，几乎所有语言都比 1.0 有提升：

```python
build_user_message(text="Bonjour le monde", language="French")
```

### 声音克隆更稳、方差更小

同一段参考音频反复生成，音色一致性明显提升。更重要的是，以前容易翻车的 **"参考音频远长于目标文本"** 场景（比如用 30 秒音频只克隆一句话）现在更可靠了——这在实际有声书和播客制作中是个高频痛点。

### 显式停顿控制：`[pause 3.2s]`

直接在文本里写停顿标记，精确到 0.1 秒：

```
它的名字是[pause 3.2s]静夜思！
```

朗诵、口播、有声书可以按节奏一字不改地排版，不需要后期剪辑对齐。

### 标点韵律更准

长句里逗号、顿号、句号的停顿时长更贴近真人语感，不再机械地一路平推过去。这个改进对普通话长句影响最明显。

## MOSS-TTS 的技术路线

MOSS-TTS 的技术选型刻意保持克制：**高质量音频 tokenizer + 自回归建模 + 大规模预训练**，跟着 LLM 的范式走，没有堆外挂语义教师、没有多阶段精修流水线。

底层 **MOSS-Audio-Tokenizer** 把 24 kHz 音频压到 12.5 fps，32 层 RVQ 可变码率，参数量 1.6B。上层建模用纯 Causal Transformer（无 CNN），训练语料覆盖播客、有声书、影视、新闻等百万小时量级。

提供两种推理模式：
- **Delay pattern**：更快、长文本更稳定
- **Local**：参数更小，客观指标更好

另有 **MOSS-TTS-Nano**（0.1B 参数），设计目标是 4 核 CPU 端侧部署，不依赖 GPU。

## 部署支持

| 后端 | 场景 |
|------|------|
| PyTorch | 训练/研究/GPU 推理 |
| GGUF（llama.cpp） | CPU 端侧部署 |
| ONNX | 跨平台推理 |
| mlx-audio | Apple Silicon（Mac） |

环境要求：Python 3.12 + Transformers 5.0.0+，可选 FlashAttention 2 加速。

```bash
conda create -n moss-tts python=3.12
pip install -r requirements.txt
```

权重通过 `AutoModel.from_pretrained()` 加载，推理接口支持批量处理。

## 基准表现

在 Seed-TTS-eval 零样本 TTS 评估中，MOSS-TTS v1.0 已经超越所有开源模型，接近最强闭源系统的水平（WER + 说话人相似度双指标）。v1.5 在此基础上进一步提升多语言和克隆稳定性。

## 适合的场景

- **有声书 / 播客**：停顿控制 + 韵律改进直接上手可用
- **虚拟人 / 数字人**：多语言 + 稳定克隆是基础要求
- **配音工具**：Apache 2.0 协议，商用无障碍
- **端侧部署**：Nano 版本 + GGUF 支持设备端运行

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

OpenMOSS — a joint team from Fudan NLP, Shanghai Innovation Institute, and MOSI.AI — has released MOSS-TTS v1.5. The v1.0 foundation already achieved open-source SOTA on Seed-TTS-eval; v1.5 keeps the architecture intact and delivers targeted improvements developers actually care about.

> 📌 GitHub: https://github.com/OpenMOSS/MOSS-TTS  
> HuggingFace v1.5: https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5  
> Technical report: https://arxiv.org/pdf/2603.18090  
> License: Apache 2.0 (commercial-friendly)

## Four Substantive Changes in v1.5

### Multilingual Support Expanded to 31 Languages

Retains all 20 languages from v1.0, adds 11 new ones: Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, Vietnamese.

With explicit language tags, v1.5 outperforms v1.0 on almost every supported language:

```python
build_user_message(text="Bonjour le monde", language="French")
```

### Stabler Voice Cloning, Lower Variance

Repeated generation from the same reference audio produces much more consistent voice characteristics. The previously unreliable **"long reference, short target"** scenario — e.g., cloning from 30 seconds of audio to synthesize a single sentence — is now significantly more reliable.

### Explicit Pause Control: `[pause 3.2s]`

Insert pauses directly in the text, precise to 0.1 seconds:

```
Its name is[pause 3.2s]Jing Ye Si!
```

Useful for narration, podcasts, and audiobooks where timing matters — no post-processing required.

### More Natural Punctuation Prosody

Pause durations for commas, enumeration pauses, and periods in long sentences now closely match natural human speech patterns. No more mechanical flat delivery through multi-clause sentences.

## Technical Architecture

MOSS-TTS takes a deliberately minimal approach: **high-quality audio tokenizer + autoregressive modeling + large-scale pretraining** — following the LLM paradigm without stacking semantic teacher models or multi-stage refinement pipelines.

The underlying **MOSS-Audio-Tokenizer** compresses 24 kHz audio to 12.5 fps with 32-layer variable-bitrate RVQ (1.6B parameters). The upper modeling layer uses pure Causal Transformer blocks (no CNN). Training data covers podcasts, audiobooks, film/TV, and news at million-hour scale.

Two inference modes:
- **Delay pattern**: faster, more stable for long-form synthesis
- **Local**: smaller model, better on objective metrics

**MOSS-TTS-Nano** (0.1B parameters) targets CPU-only deployment on 4 cores, no GPU required.

## Deployment Options

| Backend | Use Case |
|---------|----------|
| PyTorch | Training / research / GPU inference |
| GGUF (llama.cpp) | CPU edge deployment |
| ONNX | Cross-platform inference |
| mlx-audio | Apple Silicon (Mac) |

Requirements: Python 3.12 + Transformers 5.0.0+, optional FlashAttention 2 for speed.

## Benchmark Results

On Seed-TTS-eval zero-shot TTS evaluation, MOSS-TTS v1.0 already outperformed all open-source models and rivaled the strongest closed-source systems (WER + speaker similarity). v1.5 builds further on multilingual quality and cloning stability.

## Target Use Cases

- **Audiobooks / podcasts**: pause control and prosody improvements are immediately useful
- **Virtual avatars / digital humans**: multilingual + stable cloning are baseline requirements
- **Dubbing tools**: Apache 2.0 means no commercial restrictions
- **Edge deployment**: Nano + GGUF enables on-device inference

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
