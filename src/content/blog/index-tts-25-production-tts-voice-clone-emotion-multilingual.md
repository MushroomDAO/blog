---
title: "IndexTTS-2.5：生产级零样本 TTS，一段参考音频克隆音色 + 细粒度情感与语速控制"
titleEn: "index-tts-25-production-tts-voice-clone-emotion-multilingual"
description: "index-tts/index-tts，⭐22,615，Python，2026-08-10 发布 IndexTTS-2.5。零样本文本转语音系统，一段参考音频即可克隆音色。支持中文、英文、日语、西班牙语、阿拉伯语五种语言，跨语言音色保持。8维情感向量（愉快/愤怒/悲伤/恐惧/厌恶/忧郁/惊讶/平静），支持情感参考音频、文本情感自动转换、显式情感描述四种控制方式；duration_factor 语速控制（0.5×–2.0×）；拼音/CMU音素/日语假名发音精确控制。推理比 IndexTTS-2 更快，vLLM 生产部署。"
descriptionEn: "index-tts/index-tts, ⭐22,615, Python, IndexTTS-2.5 released 2026-08-10. Zero-shot TTS system that clones a voice from a single reference audio. Supports Chinese, English, Japanese, Spanish, and Arabic with cross-lingual voice preservation. 8-dimension emotion vector (happy/angry/sad/afraid/disgusted/melancholic/surprised/calm), four emotion control modes: reference audio, emotion vector, text-derived, explicit description. duration_factor speaking speed (0.5×–2.0×), Pinyin/CMU phoneme/Japanese Kana pronunciation control. Faster inference than IndexTTS-2, vLLM production deployment."
pubDate: "2026-08-12"
updatedDate: "2026-08-12"
category: "Tech-News"
tags: ["TTS", "语音合成", "零样本", "情感控制", "开源", "Python", "多语言", "Mycelium"]
heroImage: "../../assets/images/index-tts-25-production-tts-voice-clone-emotion-multilingual-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

一段参考音频，文字进去，带有相同音色的语音出来——这是零样本 TTS 的核心承诺。IndexTTS 把这件事从演示级推向了生产级：22,000+ stars，活跃的版本迭代，以及正式的 vLLM 生产部署支持。

2026 年 8 月 10 日，**IndexTTS-2.5** 正式发布。

GitHub: https://github.com/index-tts/index-tts | ⭐ 22,615 | Python  
HuggingFace: IndexTeam/IndexTTS-2.5 | arxiv: 2601.03888

---

## 核心能力：三件事

IndexTTS-2.5 的核心围绕三个轴展开：**音色克隆**、**情感控制**、**发音控制**。

---

## 音色克隆：一段音频搞定

零样本音色克隆是 IndexTTS 的基础能力——不需要训练，不需要大量数据，给一段参考音频就能把音色迁移到任意文本：

```python
from indextts.infer_v2_5 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_bf16=True)

# 音色来自参考音频，文本用任意语言
tts.infer(
    spk_audio_prompt='voice.wav',   # 参考音频（提供音色）
    text="Hello world.",
    lang="EN",                       # ZH / EN / JA / ES / AR
    output_path="gen.wav"
)
```

**跨语言支持**：中文、英文、日语、西班牙语、阿拉伯语。跨语言音色保持——用中文参考音频生成英文，音色仍然一致。

---

## 情感控制：四种方式

IndexTTS-2.5 提供了四种粒度不同的情感控制方式，可以混合使用。

情感由 8 个维度组成：`[愉快, 愤怒, 悲伤, 恐惧, 厌恶, 忧郁, 惊讶, 平静]`

### 方式 1：情感参考音频

最直观的方式。给一段情绪化的参考音频，让模型从中提取情感：

```python
tts.infer(
    spk_audio_prompt='voice.wav',    # 音色来源
    emo_audio_prompt='emo_sad.wav',  # 情感来源（独立于音色）
    emo_alpha=0.9,                   # 情感强度，0.0–1.0，默认 1.0
    text="酒楼丧尽天良，开始借机竞拍房间。",
    lang="ZH",
    output_path="gen.wav"
)
```

`emo_alpha` 控制情感强度，0 = 不受情感音频影响，1 = 完全按情感音频的情绪输出。

### 方式 2：8 维情感向量

直接用数字指定每个情感维度的强度：

```python
tts.infer(
    spk_audio_prompt='voice.wav',
    emo_vector=[0, 0, 0.8, 0, 0, 0, 0, 0],  # 悲伤强度 0.8
    text="对不起，我的记性真的不太好。",
    lang="ZH",
    output_path="gen.wav"
)
```

顺序固定：`[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]`。

### 方式 3：从文本内容自动推断情感

让模型从文本本身推断情感，需要 Qwen 情感理解模块：

```python
tts = IndexTTS2(..., use_qwen_emo=True)  # 初始化时开启

tts.infer(
    spk_audio_prompt='voice.wav',
    text="快躲起来！是他要来了！",
    lang="ZH",
    use_emo_text=True,
    emo_alpha=0.6,    # 推荐用较低强度，更自然
    output_path="gen.wav"
)
```

### 方式 4：显式情感描述文本

文本和情感描述分开，让模型用情感描述来生成语音：

```python
tts.infer(
    spk_audio_prompt='voice.wav',
    text="快躲起来！是他要来了！",
    emo_text="你吓死我了！你是鬼吗？",  # 情感描述，独立于台词
    lang="ZH",
    use_emo_text=True,
    emo_alpha=0.6,
    output_path="gen.wav"
)
```

---

## 语速控制

`duration_factor` 控制语速，大于 1 变慢，小于 1 变快：

```python
# 慢速（1.2× 时长 = 语速降低约 20%）
tts.infer(..., duration_factor=1.2, output_path="slow.wav")

# 快速（0.8× 时长 = 语速加快约 25%）
tts.infer(..., duration_factor=0.8, output_path="fast.wav")
```

有效范围：0.5–2.0。

---

## 发音控制：拼音 / CMU 音素 / 日语假名

对多音字、专业术语、外来词，IndexTTS-2.5 支持在文本里内联标注精确发音。

**中文拼音**（多音字控制）：

```
他在银<行|XING2>里<行|HANG2>走了半天，发现这笔业务办不<行|HANG2>。
```

**英文 CMU 音素**（专业词汇精确发音）：

```
He had a <minute|M IH1 . N AH0 T> to examine the <minute|M AY0 . N UW1 T> details.
```

**日语假名**（汉字多读音控制）：

```
彼は料理が<上手|じょうず>だが、囲碁では<上手|うわて>に負けた。
```

---

## 安装与启动

```bash
git clone https://github.com/index-tts/index-tts.git && cd index-tts

# 安装（uv 自动管理 Python 版本和所有依赖）
pip install -U uv
uv sync --all-extras

# 下载模型
hf download IndexTeam/IndexTTS-2.5 --local-dir=checkpoints

# 启动 WebUI（localhost:7860）
uv run webui.py
```

推理脚本：

```bash
PYTHONPATH="$PYTHONPATH:." uv run indextts/infer_v2_5.py \
  --cfg_path checkpoints/config.yaml \
  --model_dir checkpoints \
  --text "Hello world" \
  --lang EN
```

**BF16 推理**（2.5 版本默认，降低显存占用，质量损失极小）。  
**DeepSpeed**（可选，部分硬件上会加速，需要实测）。  
**FP8/BF16 推理**：国内镜像：`uv sync --default-index "https://hf-mirror.com"`

---

## 生产部署：vLLM

IndexTTS-2.5 正式支持 vLLM 生产部署，见 [vLLM recipe for IndexTTS](https://github.com/vllm-project/recipes/pull/772)。

---

## 版本演进

| 版本 | 时间 | 关键能力 |
|------|------|---------|
| IndexTTS 1.0 | 2025-03 | 零样本 TTS，基础版 |
| IndexTTS 1.5 | 2025-05 | 英文稳定性大幅提升 |
| IndexTTS 2 | 2025-09 | 首个自回归 TTS + 精确时长控制 + 情感控制 |
| IndexTTS 2.5 | 2026-08 | 五语言 + 语速控制 + 发音标注改进 + 推理提速 + vLLM |

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## IndexTTS-2.5: Production-Grade Zero-Shot TTS with Fine-Grained Emotion and Speed Control

*by Mycelium Protocol*

---

One reference audio clip. Text goes in. Speech in the same voice comes out. That's the zero-shot TTS promise. IndexTTS has taken this from demo-quality to production-grade: 22,000+ stars, active versioning, and now vLLM deployment support.

On August 10, 2026, **IndexTTS-2.5** was released.

GitHub: https://github.com/index-tts/index-tts | ⭐ 22,615 | Python  
HuggingFace: IndexTeam/IndexTTS-2.5 | arxiv: 2601.03888

---

### Core Capabilities: Three Axes

IndexTTS-2.5 centers on three axes: **voice cloning**, **emotion control**, and **pronunciation control**.

---

### Voice Cloning: One Audio Clip

Zero-shot voice cloning is the foundation — no training, no dataset, just a reference audio:

```python
from indextts.infer_v2_5 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_bf16=True)

tts.infer(
    spk_audio_prompt='voice.wav',
    text="Hello world.",
    lang="EN",                       # ZH / EN / JA / ES / AR
    output_path="gen.wav"
)
```

**Languages**: Chinese, English, Japanese, Spanish, Arabic. Cross-lingual voice preservation — clone a Chinese voice and generate English, the timbre carries over.

---

### Emotion Control: Four Modes

The 8-dimension emotion space: `[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]`

**Mode 1 — Emotion reference audio**: provide a separate emotional audio clip; `emo_alpha` (0.0–1.0) controls how strongly it affects the output.

```python
tts.infer(
    spk_audio_prompt='voice.wav',
    emo_audio_prompt='emo_sad.wav',
    emo_alpha=0.9,
    text="...", lang="ZH", output_path="gen.wav"
)
```

**Mode 2 — 8-float emotion vector**: specify each dimension directly.

```python
tts.infer(
    spk_audio_prompt='voice.wav',
    emo_vector=[0, 0, 0.8, 0, 0, 0, 0, 0],  # sad=0.8
    text="...", lang="ZH", output_path="gen.wav"
)
```

**Mode 3 — Text-derived emotion** (`use_emo_text=True`): the model infers emotion from the script itself. Requires `use_qwen_emo=True` at initialization. Recommended `emo_alpha` ≈ 0.6 for naturalness.

**Mode 4 — Explicit emotion description** (`emo_text`): provide a separate description of the desired emotion, independent of the speech script.

---

### Speaking Speed Control

```python
tts.infer(..., duration_factor=1.2, ...)  # slower (~20%)
tts.infer(..., duration_factor=0.8, ...)  # faster (~25%)
```

Valid range: 0.5×–2.0×. Default: 1.0.

---

### Pronunciation Control

Inline annotations directly in the text:

**Chinese Pinyin** (polyphone disambiguation):
```
他在银<行|XING2>里<行|HANG2>走了半天，发现这笔业务办不<行|HANG2>。
```

**English CMU phonemes** (technical terms, loanwords):
```
He had a <minute|M IH1 . N AH0 T> to examine the <minute|M AY0 . N UW1 T> details.
```

**Japanese Kana** (kanji multiple readings):
```
彼は料理が<上手|じょうず>だが、囲碁では<上手|うわて>に負けた。
```

---

### Install and Run

```bash
git clone https://github.com/index-tts/index-tts.git && cd index-tts

pip install -U uv
uv sync --all-extras

# Download weights
hf download IndexTeam/IndexTTS-2.5 --local-dir=checkpoints

# WebUI at localhost:7860
uv run webui.py
```

CLI inference:

```bash
PYTHONPATH="$PYTHONPATH:." uv run indextts/infer_v2_5.py \
  --cfg_path checkpoints/config.yaml \
  --model_dir checkpoints \
  --text "Hello world" \
  --lang EN
```

BF16 inference is the default for 2.5 — lower VRAM, minimal quality loss. DeepSpeed is optional; test on your hardware.

---

### Production Deployment

IndexTTS-2.5 supports production deployment via [vLLM](https://github.com/vllm-project/recipes/pull/772).

---

### Version History

| Version | Date | Key additions |
|---------|------|--------------|
| 1.0 | 2025-03 | Initial zero-shot TTS |
| 1.5 | 2025-05 | English stability improvements |
| 2 | 2025-09 | Autoregressive architecture + duration control + emotion control |
| 2.5 | 2026-08 | 5 languages + speed control + pronunciation improvements + faster inference + vLLM |

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
