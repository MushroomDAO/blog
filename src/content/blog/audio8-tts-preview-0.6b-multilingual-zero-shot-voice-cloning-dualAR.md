---
title: "Audio8 TTS Preview 0.6B：0.6B 参数打赢 4.6B 的 TTS 模型——11 语言零样本声音克隆"
description: "Audio8 TTS Preview 是一个 0.6B 参数的多语言文本转语音模型，采用 DualAR 架构（慢 AR 预测语义 token + 快 AR 预测声学码本），支持 11 种语言（含粤语）零样本声音克隆。Seed-TTS 英语 WER 1.506，以 0.6B 参数规模超越 Fish S2 Pro（4.6B）、Higgs Audio v2（4.7B）。Apache 2.0，HuggingFace 开放权重。"
pubDate: "2026-07-30"
category: "Tech-Experiment"
heroImage: "../../assets/images/audio8-tts-preview-0.6b-multilingual-zero-shot-voice-cloning-dualAR-banner.jpg"
---

TTS 模型的参数量竞赛一直朝着更大走：Fish S2 Pro 4.6B，Higgs Audio v2 4.7B，MOSS-TTS 8.5B。

Audio8 TTS Preview 反着来——**0.6B 参数，在英语 WER 上打赢了所有这些更大的模型**，同时还支持 11 种语言的零样本声音克隆，含粤语。

---

## 一、基本信息

| 属性 | 值 |
|---|---|
| 参数量 | **0.6B**（601,159,424，不含 codec） |
| 架构 | DualAR（慢 AR + 快 AR） |
| 声码器 | 44.1 kHz 神经 codec，10 个码本，每本 4,096 条目 |
| 支持语言 | 11 种（粤语、中文、荷兰语、英语、法语、德语、意大利语、日语、韩语、波兰语、西班牙语） |
| 核心能力 | 零样本声音克隆（提供参考音频即可） |
| 许可证 | Apache 2.0 |
| 发布日期 | 2026-07-28 |

---

## 二、DualAR 架构：慢思考 + 快执行

Audio8 TTS 的核心架构叫 **DualAR**，灵感来自 Fish Audio S2 Pro：

```
输入文本 + 参考音频
    ↓
慢 AR Transformer（24层，宽度896，14个注意力头，2个KV头）
  → 每帧预测 1 个语义 token（内容信息）
    ↓
快 AR Transformer（4层，宽度896）
  → 每帧预测 10 个 codec 码本条目（声学信息，conditioned 在慢 AR 隐状态上）
    ↓
神经 Codec 解码 → 44.1 kHz 波形
```

慢 AR 负责理解语义（"说什么"），快 AR 负责还原声学细节（"怎么说"）。两个分支都使用静态 KV cache 加速推理。

**Codec 内置**：模型 checkpoint 自带神经 codec，参考音频编码和波形解码不需要额外的 codec 模型文件，一个文件搞定所有。

---

## 三、benchmark：0.6B 打赢 4-8B

### Seed-TTS 评测（英文 WER / 中文 CER，越低越好）

| 模型 | 参数量 | EN WER | ZH CER | Hard ZH CER |
|---|---|---|---|---|
| **Audio8 TTS Preview** | **0.6B** | **1.506** | 0.950 | 11.510 |
| Fish S2 Pro | 4.6B | 1.607 | 1.038 | 10.149 |
| Higgs Audio v2 | 4.7B | 1.524 | **0.806** | 10.622 |
| CosyVoice3-1.5B | 1.5B | 2.22 | 1.12 | **5.83** |
| MOSS-TTS | 8.5B | 1.85 | 1.20 | — |
| VoxCPM2 | 2.3B | 1.84 | 0.97 | 8.13 |

英语 WER 第一。中文 CER（0.950）也优于 Fish S2 Pro 和 CosyVoice3。Hard ZH（长句/难句）方面 CosyVoice3 更强，是 Audio8 目前的弱项。

### CV3 多语言评测（错误率，越低越好）

| 模型 | 参数 | 中文 | 英语 | 日语 | 韩语 | 德语 |
|---|---|---|---|---|---|---|
| **Audio8 TTS Preview** | **0.6B** | **3.205** | **3.128** | 7.205 | 4.223 | 3.447 |
| Fish S2 Pro | 4.6B | 3.600 | 3.493 | **5.139** | **4.111** | 3.605 |
| Higgs Audio v2 | 4.7B | 3.378 | 3.404 | **4.742** | 4.260 | **3.300** |
| CosyVoice3-1.5B | 1.5B | 3.91 | 4.99 | 7.57 | 5.69 | 6.43 |

在中文和英语两个主要语言上，Audio8 0.6B 都是 CV3 榜首，尽管在日语、韩语上输给了更大的模型。

---

## 四、零样本声音克隆：怎么用

最核心的用法：给一段参考音频，模型克隆这个声音说新内容。

```python
import soundfile as sf
import torch
from transformers import AutoModel, AutoProcessor

model_id = "Audio8/Audio8-TTS-Preview-0.6b"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id,
    trust_remote_code=True,
    dtype=torch.bfloat16,
).eval().cuda()

# 零样本克隆：提供参考音频 + 参考文本（必须与音频内容一致）
inputs = processor(
    text=["你好，这是一段用克隆声音生成的语音。"],
    reference_audio=["reference.wav"],          # 3-10秒音频效果最好
    reference_text=["参考音频里说的内容原文"],   # 必须与音频完全对应
    return_tensors="pt",
)
inputs = {k: v.cuda() for k, v in inputs.items()}

with torch.inference_mode():
    output = model.generate(
        **inputs,
        max_new_tokens=1024,
        temperature=0.8,
        top_p=0.95,
        top_k=50,
        do_sample=True,
        return_dict_in_generate=True,
    )
    waveforms, waveform_lengths = model.decode_audio(output.codes)

audio = waveforms[0, :int(waveform_lengths[0])].float().cpu().numpy()
sf.write("output.wav", audio, 44100)
```

**不用参考音频**（使用默认声音）：省略 `reference_audio` 和 `reference_text` 两个参数即可。

---

## 五、粤语支持是亮点

目前支持粤语 TTS 的开源模型极少，这是 Audio8 的一个差异化亮点。11 种语言里粤语是第一个列出来的，说明这不是事后加进去的：粤语被当作一等公民对待。

未来版本计划扩展更多中文方言支持。

---

## 六、安装和运行

```bash
# 安装依赖（需要 Python 3.10+，推荐 CUDA GPU）
pip install "torch>=2.5.0" "torchaudio>=2.5.0" \
  "transformers>=4.57.0,<5" "soundfile>=0.12" "safetensors>=0.4"

# 加载模型（trust_remote_code=True，需审查仓库代码后使用）
from transformers import AutoModel, AutoProcessor
model = AutoModel.from_pretrained(
    "Audio8/Audio8-TTS-Preview-0.6b",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).eval().cuda()
```

Apple Silicon 运行：`instavar/audio8-tts-lora-finetuning` 仓库有 MPS 适配，但目前官方推荐 CUDA。

---

## 七、现有局限

- 当前是 **Preview** 版本，语言覆盖范围有意受限
- 参考音频需要**精确文本对应**，噪音大或文本不匹配会降低声音相似度
- 粤语/方言支持在未来版本扩展
- Hard 中文场景（复杂长句）输给了 CosyVoice3

---

## 资源

| 资源 | 地址 |
|---|---|
| HuggingFace 模型 | `huggingface.co/Audio8/Audio8-TTS-Preview-0.6b` |
| GitHub | `github.com/Audio8-AI/Audio8_TTS` |
| Demo 页面 | `audio8-ai.github.io/Audio8_TTS/` |
| LoRA 微调 | `github.com/instavar/audio8-tts-lora-finetuning` |
| 许可证 | Apache 2.0 |
| 发布日期 | 2026-07-28 |
| 模型大小 | ~0.6B 参数（不含 codec） |

---

<!--EN-->

## Audio8 TTS Preview 0.6B: A 0.6B Model That Beats 4.6B TTS Systems — 11-Language Zero-Shot Voice Cloning

The TTS parameter race has been heading in one direction: Fish S2 Pro at 4.6B, Higgs Audio v2 at 4.7B, MOSS-TTS at 8.5B.

Audio8 TTS Preview goes the other way — **0.6B parameters, best English WER on Seed-TTS, beating all of them** — while supporting zero-shot voice cloning in 11 languages including Cantonese.

---

## Model Overview

| Property | Value |
|---|---|
| Parameters | **0.6B** (601,159,424, codec excluded) |
| Architecture | DualAR (Slow AR + Fast AR) |
| Codec | 44.1 kHz neural codec, 10 codebooks, 4,096 entries each |
| Languages | Cantonese, Chinese, Dutch, English, French, German, Italian, Japanese, Korean, Polish, Spanish |
| Core capability | Zero-shot voice cloning (provide reference audio) |
| License | Apache 2.0 |
| Released | 2026-07-28 |

---

## DualAR Architecture

Inspired by Fish Audio S2 Pro, Audio8 TTS splits generation into two transformers:

- **Slow AR** (24 layers, width 896, 14 attention heads, 2 KV heads): predicts one semantic token per audio frame — the *what to say*
- **Fast AR** (4 layers, width 896): predicts 10 codec codebook entries per frame, conditioned on the slow AR hidden state — the *how it sounds*

The bundled neural codec handles both reference encoding and waveform decoding. No separate codec checkpoint needed.

---

## Benchmarks

**Seed-TTS** (EN WER / ZH CER, lower is better):

| Model | Params | EN WER | ZH CER |
|---|---|---|---|
| **Audio8 TTS Preview** | **0.6B** | **1.506** | 0.950 |
| Fish S2 Pro | 4.6B | 1.607 | 1.038 |
| Higgs Audio v2 | 4.7B | 1.524 | **0.806** |
| CosyVoice3-1.5B | 1.5B | 2.22 | 1.12 |
| MOSS-TTS | 8.5B | 1.85 | 1.20 |

Best English WER. Best Chinese and English scores on CV3 multilingual eval. Japanese and Korean go to the larger models.

---

## Zero-Shot Voice Cloning

```python
from transformers import AutoModel, AutoProcessor
import soundfile as sf, torch

processor = AutoProcessor.from_pretrained("Audio8/Audio8-TTS-Preview-0.6b", trust_remote_code=True)
model = AutoModel.from_pretrained("Audio8/Audio8-TTS-Preview-0.6b",
    trust_remote_code=True, dtype=torch.bfloat16).eval().cuda()

inputs = processor(
    text=["Welcome to Audio8 TTS."],
    reference_audio=["reference.wav"],
    reference_text=["Exact transcript of the reference recording."],
    return_tensors="pt",
)
with torch.inference_mode():
    out = model.generate(**{k: v.cuda() for k, v in inputs.items()},
        max_new_tokens=1024, temperature=0.8, return_dict_in_generate=True)
    waves, lens = model.decode_audio(out.codes)

sf.write("output.wav", waves[0, :int(lens[0])].float().cpu().numpy(), 44100)
```

Omit `reference_audio`/`reference_text` for default voice generation.

---

## Why Cantonese Matters

Cantonese TTS has almost no open-source coverage. Audio8 lists it first among supported languages — it's a first-class citizen, not an afterthought. Future releases plan broader Chinese dialect support.

---

**GitHub**: `github.com/Audio8-AI/Audio8_TTS`  
**HuggingFace**: `huggingface.co/Audio8/Audio8-TTS-Preview-0.6b` (43 ❤️)  
**Demo**: `audio8-ai.github.io/Audio8_TTS/`
