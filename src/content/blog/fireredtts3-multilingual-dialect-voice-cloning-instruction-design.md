---
title: "FireRedTTS3：24 语言 + 21 种中文方言零样本声音克隆，指令控制变声和语音编辑"
titleEn: "fireredtts3-multilingual-dialect-voice-cloning-instruction-design"
description: "FireRedTTS3（FireRedTeam，Apache 2.0，Python，183 stars）是基于语义增强连续语音表示的统一语音生成与编辑系统，支持 24 种语言和 21 种中文方言的零样本声音克隆，以及用自然语言描述设计全新声音、语义编辑（插入/删除/替换）和声学编辑（语速/音调/音量）。在 Seed-TTS-eval 上综合 WER/SIM 领先所有开源对手，2026-08-13 发布。"
descriptionEn: "FireRedTTS3 (FireRedTeam, Apache 2.0, Python, 183 stars) is a unified speech generation and editing system built on semantically enriched continuous speech representations. Supports zero-shot voice cloning across 24 languages and 21 Chinese dialects, plus instruction-guided voice design, semantic editing (insert/delete/substitute), and acoustic editing (speed/pitch/volume). Achieves best average WER/SIM on Seed-TTS-eval vs all open-source competitors. Released 2026-08-13."
pubDate: "2026-08-23"
updatedDate: "2026-08-23"
category: "Tech-News"
tags: ["TTS", "声音克隆", "语音合成", "多语言", "方言", "开源", "FireRed", "语音编辑"]
heroImage: "../../assets/images/fireredtts3-multilingual-dialect-voice-cloning-instruction-design-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：FireRedTeam/FireRedTTS3  
HuggingFace：FireRedTeam/FireRedTTS3  
ModelScope：FireRedTeam/FireRedTTS3  
论文：arXiv:2608.17492  
许可证：Apache 2.0  
语言：Python  
Stars：183（FireRedTTS3）· 918（FireRedTTS v1）  
发布：2026-08-13 | 最近更新：2026-08-24

---

## 一、它是什么

FireRedTTS3 是 FireRedTeam 开源的第三代 TTS（文字转语音）系统，核心突破在于把**语音生成和语音编辑统一到同一个模型**里——以前你可能需要一个模型做 TTS，另一个做语音编辑，现在一个 FireRedTTS3-Instruct 全搞定。

系统有两个变体：

| 变体 | 能力 |
|------|------|
| **FireRedTTS3-Base** | 零样本声音克隆，24 种语言 + 21 种中文方言 |
| **FireRedTTS3-Instruct** | Base 的所有能力 + 指令控制声音设计 + 语义编辑 + 声学编辑 |

---

## 二、四大核心能力

### 1. 零样本声音克隆（24 语言）

提供一段参考音频，不需要微调，直接克隆声音风格合成指定文本。

支持语言：`Arabic` · `Cantonese` · `Chinese` · `Czech` · `Dutch` · `English` · `Finnish` · `French` · `German` · `Greek` · `Hindi` · `Indonesian` · `Italian` · `Japanese` · `Korean` · `Polish` · `Portuguese` · `Romanian` · `Russian` · `Spanish` · `Thai` · `Turkish` · `Ukrainian` · `Vietnamese`

最佳实践：用目标语言的参考音频来克隆，比如合成日语就用日语参考音频，合成四川话就用四川话参考音频。

### 2. 21 种中文方言零样本克隆

这是目前开源 TTS 里方言覆盖最全面的：

`安徽话` · `福建话` · `甘肃话` · `贵州话` · `河北话` · `河南话` · `湖北话` · `湖南话` · `江西话` · `辽宁话` · `闽南话` · `宁夏话` · `陕西话` · `山东话` · `上海话` · `山西话` · `四川话` · `天津话` · `温州话` · `吴语` · `云南话`

### 3. 指令控制声音设计（无需参考音频）

这是 FireRedTTS3-Instruct 独有的能力：**不需要任何参考音频，只用自然语言描述就能生成全新声音**。

```python
instruction = "一个年轻女性的温柔嗓音，语速稍慢，带一点俏皮。"
text = "今天天气很好，我们一起去公园散步吧。"
gen_audio, gen_audio_sr, gen_text = instruct.generate_voice_design(
    instruction=instruction,
    text=text,
)
# gen_text 是模型写出的声音属性规划，可以查看
```

模型会先生成一个「声音属性规划」（性别、年龄、音色、情感、语速、口音……），然后基于这个规划渲染音频。

### 4. 语音编辑（语义 + 声学）

**语义编辑**：对已有音频做内容级修改——插入、删除、替换，用自然语言描述操作：

```python
gen_audio, gen_audio_sr, gen_text = instruct.generate_semantic_edit(
    instruction="Replace 'cats' with 'dogs'.",
    audio_in=audio_in,
    audio_in_sr=audio_in_sr,
)
```

**声学编辑**：调整语速、音调、音量，用结构化指令：

```python
# 语速调慢到 0.5x
instruct.generate_acoustic_edit(instruction="adjust the speed to 0.5x", ...)

# 升调 3 个半音
instruct.generate_acoustic_edit(instruction="shift the pitch by 3 step(s)", ...)

# 音量调到 1.5x
instruct.generate_acoustic_edit(instruction="adjust the volume to 1.5", ...)
```

声学编辑目前支持：语速（0.5-2.0，步长 0.1）、音调（-6 到 +6 个半音）、音量（0.3-2.0）。

---

## 三、性能基准（Seed-TTS-eval）

在业界标准 Seed-TTS-eval 上与主流开源 TTS 对比，指标越低越好（WER/CER），越高越好（SIM）：

| 模型 | Test-EN WER | Test-ZH CER | Test-Hard CER | Avg WER/SIM |
|------|:---:|:---:|:---:|:---:|
| CosyVoice3-1.5B | 2.22 | 1.12 | 5.83 | 3.06 / 75.3 |
| F5-TTS | 2.00 | 1.53 | 8.67 | 4.10 / 71.4 |
| Qwen3-TTS | 1.23 | 1.22 | 6.76 | 3.07 / 74.5 |
| dots.tts (Pretrain) | 1.80 | 0.97 | 6.65 | 3.14 / 78.7 |
| **FireRedTTS3-Base** | **1.64** | 1.01 | **6.50** | **3.04 / 78.8** |

FireRedTTS3-Base 在综合 WER（3.04%，最低）和说话人相似度（78.8%，最高）上均领先。英文测试集的说话人相似度（77.2%）也是所有对比模型中最高的。

在 MiniMax-MLS-Test（24 语言多语种测试集）上：
- 平均 WER/CER：**3.754%**（最低）
- 平均说话人相似度：**84.8%**（最高）

---

## 四、架构基础

FireRedTTS3 的技术栈站在一批优秀开源项目的肩膀上：

- **语言模型基础**：Qwen3 + Qwen2-Audio（语言理解和音频理解）
- **扩散自回归框架**：DiTAR（patch-level diffusion autoregressive）
- **判别器设计**：X-Codec（用于 RedAE 训练）
- **说话人特征提取**：CAM++
- **语言识别**：Meta FastText（lid.176 模型）
- **文本归一化**：WeTextProcessing（wetext，中英文），LLM-based TN（全语言，需要兼容 OpenAI API 的大模型端点）

---

## 五、快速上手

### 安装

```bash
pip install -r requirements.txt

# 下载模型（需要 hf CLI）
pip install "huggingface_hub[cli]"
hf download FireRedTeam/FireRedTTS3 --local-dir pretrained_models/

# 可选：下载 FastText 语言识别模型（自动检测语言）
curl -L -o fireredtts3/utils/llm_tn/models/lid.176.ftz \
  https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
```

### 基础声音克隆

```python
import torchaudio
from fireredtts3.core import FireRedTTS3

tts = FireRedTTS3("pretrained_models", use_wetext=True)

prompt_audio, sr = torchaudio.load("prompt.wav")
gen_audio, gen_sr = tts.generate(
    language=None,          # None = 自动检测语言
    prompt_text="<参考音频的文字>",
    prompt_audio=prompt_audio,
    prompt_audio_sr=sr,
    text="今天天气很好，我们一起去公园散步吧。",
    do_tn=True,
)
torchaudio.save("output.wav", gen_audio.cpu(), gen_sr)
```

### LLM 文本归一化（可选，支持所有语言）

在 `.env` 里配置任意 OpenAI 兼容端点：

```
LLM_TN_API_URL=https://api.deepseek.com/chat/completions
LLM_TN_API_KEY=sk-xxxxxxxx
LLM_TN_MODEL=deepseek-v4-flash    # ≥30B 参数的模型
```

然后初始化时加 `use_llm_tn=True`，即可为任意语言处理数字、日期、单位、货币等的文本归一化。

---

## 六、为什么值得关注

**对于开发者**：Apache 2.0 协议，可商用。目前在综合评测上超过 CosyVoice3、F5-TTS、Qwen3-TTS，是开源 TTS 里最强的综合方案之一。21 种中文方言支持，是真正的中文本地化 TTS。

**对于产品**：「指令控制声音设计」这个能力意味着不需要录音就能生成新声色——有声书、配音、客服语音都可以用自然语言描述来定制声音风格。

**对于研究者**：把语音生成和语音编辑统一到同一个模型，而不是两个独立系统，这个架构路线值得关注。语义表示（semantic representation）作为中间层同时驱动生成和编辑，思路清晰。

---

## 七、注意事项

项目在 README 里明确限制：

- 声音克隆功能**仅限学术研究**使用
- **禁止**用于任何非法活动
- 如果发现滥用或欺诈行为，请立即向团队举报

这个声明有必要看认真——声音克隆技术在诈骗场景里有明显滥用风险，合规使用是前提。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## FireRedTTS3: Zero-Shot Voice Cloning for 24 Languages and 21 Chinese Dialects, with Instruction-Guided Voice Design and Speech Editing

*by Mycelium Protocol*

---

GitHub: FireRedTeam/FireRedTTS3  
HuggingFace: FireRedTeam/FireRedTTS3  
ModelScope: FireRedTeam/FireRedTTS3  
Paper: arXiv:2608.17492  
License: Apache 2.0  
Language: Python  
Stars: 183 (FireRedTTS3) · 918 (FireRedTTS v1)  
Released: 2026-08-13 | Updated: 2026-08-24

---

### What It Is

FireRedTTS3 is FireRedTeam's third-generation open-source TTS system. Its core achievement: **unifying speech generation and speech editing inside a single model** — previously requiring separate systems for each.

Two variants:

| Variant | Capabilities |
|---------|-------------|
| **FireRedTTS3-Base** | Zero-shot voice cloning; 24 languages + 21 Chinese dialects |
| **FireRedTTS3-Instruct** | All of Base + instruction-guided voice design + semantic editing + acoustic editing |

---

### Four Core Capabilities

**1. Zero-shot voice cloning (24 languages)**

Provide a reference audio clip — no fine-tuning required — and clone the voice style for any target text. Supported languages span Arabic, Cantonese, Chinese, English, French, German, Japanese, Korean, Spanish, and 15 more.

Best practice: use reference audio in the target language. For Japanese synthesis, use a Japanese reference. For Sichuanese, use a Sichuanese reference.

**2. 21 Chinese dialect voice cloning**

The most comprehensive open-source Chinese dialect coverage available: Anhui, Fujian, Gansu, Guizhou, Hebei, Henan, Hubei, Hunan, Jiangxi, Liaoning, Minnan, Ningxia, Shaanxi, Shandong, Shanghai, Shanxi, Sichuan, Tianjin, Wenzhou, Wu, Yunnan.

**3. Instruction-guided voice design (no reference audio needed)**

FireRedTTS3-Instruct's unique capability: **generate a completely new voice from a natural-language description alone — no reference recording required**.

```python
instruction = "A gentle young woman's voice, slightly slow pace, a bit playful."
gen_audio, gen_audio_sr, gen_text = instruct.generate_voice_design(
    instruction=instruction,
    text="The weather is great today. Let's take a walk in the park.",
)
# gen_text shows the voice attribute plan the model wrote before rendering
```

The model first writes a voice attribute plan (gender, age, timbre, emotion, pace, accent…), then renders audio from that plan.

**4. Speech editing (semantic + acoustic)**

*Semantic editing*: content-level changes — insert, delete, or substitute words in existing audio via natural-language instruction.

*Acoustic editing*: adjust speed (0.5–2.0×), pitch (±6 semitones), or volume (0.3–2.0×) via structured instructions.

---

### Performance on Seed-TTS-eval

FireRedTTS3-Base achieves the **best average WER (3.04%)** and **best speaker similarity (78.8%)** among all open-source models evaluated:

| Model | Test-EN WER | Test-ZH CER | Avg WER/SIM |
|-------|:-----------:|:-----------:|:-----------:|
| CosyVoice3-1.5B | 2.22 | 1.12 | 3.06 / 75.3 |
| F5-TTS | 2.00 | 1.53 | 4.10 / 71.4 |
| Qwen3-TTS | 1.23 | 1.22 | 3.07 / 74.5 |
| dots.tts (Pretrain) | 1.80 | 0.97 | 3.14 / 78.7 |
| **FireRedTTS3-Base** | **1.64** | 1.01 | **3.04 / 78.8** |

On MiniMax-MLS-Test (24-language multilingual benchmark): **3.754% avg WER/CER** (lowest) and **84.8% avg speaker similarity** (highest).

---

### Architecture

Built on top of strong open-source foundations:
- **LLM backbone**: Qwen3 + Qwen2-Audio
- **Diffusion AR framework**: DiTAR (patch-level)
- **Discriminator design**: X-Codec
- **Speaker embedding**: CAM++
- **Language ID**: Meta FastText (lid.176)
- **Text normalization**: WeTextProcessing (zh/en) or LLM-based TN (all languages, needs any OpenAI-compatible endpoint ≥30B)

---

### Quick Start

```bash
pip install -r requirements.txt
pip install "huggingface_hub[cli]"
hf download FireRedTeam/FireRedTTS3 --local-dir pretrained_models/
```

```python
from fireredtts3.core import FireRedTTS3
import torchaudio

tts = FireRedTTS3("pretrained_models", use_wetext=True)
prompt_audio, sr = torchaudio.load("prompt.wav")
gen_audio, gen_sr = tts.generate(
    language=None,
    prompt_text="<reference audio transcript>",
    prompt_audio=prompt_audio,
    prompt_audio_sr=sr,
    text="Hello, this is FireRedTTS3.",
    do_tn=True,
)
torchaudio.save("output.wav", gen_audio.cpu(), gen_sr)
```

---

### Why It Matters

**For developers**: Apache 2.0, commercially usable. Best combined WER + speaker similarity among open-source TTS models evaluated. 21 Chinese dialect variants make it the most comprehensive Chinese-local TTS available.

**For products**: Instruction-guided voice design means no recording session needed to create a new voice profile — audiobooks, dubbing, customer service, all configurable from a text description.

**For researchers**: Unifying generation and editing in one model via semantic representations is an architecture direction worth tracking. The semantic intermediate representation drives both synthesis and editing coherently rather than treating them as separate problems.

---

### Usage Note

The project README explicitly restricts voice cloning to **academic research purposes only**. Do not use for illegal activities. Voice cloning carries real fraud risk — responsible use is the prerequisite.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
