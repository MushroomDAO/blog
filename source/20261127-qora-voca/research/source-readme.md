# qora-voca-zh

**4.5M 参数、三音色、纯中文普通话 TTS，从零训练，CPU 可实时推理。**

A 4.5M-parameter, three-voice Mandarin Chinese text-to-speech model, trained from scratch. Runs on CPU. Fork of [tiny-voca](https://github.com/n4ze3m/tiny-voca) (Apache-2.0).

> 中文文档见下方；English summary at the bottom.

**🔊 试听样本**：[F2 女声](https://github.com/ValueMoonLab/qora-voca-zh/releases/download/v1.0.0/F2-1.wav) · [M2 男声](https://github.com/ValueMoonLab/qora-voca-zh/releases/download/v1.0.0/M2-1.wav) · [M3 年轻男声](https://github.com/ValueMoonLab/qora-voca-zh/releases/download/v1.0.0/M3-1.wav) · [v1.0.0 Release（权重+ONNX 下载）](https://github.com/ValueMoonLab/qora-voca-zh/releases/tag/v1.0.0)

---

## 这是什么

一个**极小**的中文语音合成模型：

| | |
|---|---|
| 参数量 | **4,532,299**（4.5M） |
| 音色 | **F2**（年轻女声，清亮温柔）/ **M2**（成熟男声，低沉浑厚）/ **M3**（年轻男声，清亮突出） |
| 语言 | 普通话（仅中文；拉丁/假名文本会被拒绝并提示） |
| 采样率 | 24 kHz 单声道 |
| 权重 | PyTorch checkpoint **17.3 MB** / ONNX **21.4 MB** |
| 推理 | **CPU 即可**，无需 GPU、无需神经声码器 |
| 训练 | 单张 **RTX 3060 12G**，160,000 步，约 21 小时 |
| 数据 | **25.25 小时**合成语音（28,231 条通过质检），全部由 Qwen3-TTS 生成 |

模型本体**不加载任何预训练权重**。预训练模型只出现在两个离线环节：标注（中文 CTC 音素识别器做强制对齐）和评测（ASR 打分）。推理时两者都不需要。

## 快速开始

```bash
pip install -e .

# 合成一句话（CPU）
qora-voca-speak \
  --checkpoint release/qora-voca-zh.pt \
  --text "今天天气真不错，我们一起去公园散步吧。" \
  --voice F2 \
  --output hello.wav

# 朗读长文本文件（自动分句、超长自动切分、峰值限制）
qora-voca-speak --checkpoint release/qora-voca-zh.pt \
  --text-file story.txt --voice M3 --output story.wav
```

Python API：

```python
from tiny_voca.infer import load_model, speak_text

model = load_model("release/qora-voca-zh.pt", device="cpu")
wave, phones = speak_text(model, "你好，世界。", "F2")   # 24 kHz float tensor
```

ONNX（CPU 部署，无 PyTorch 依赖）：

```bash
python scripts/check_onnx_zh.py --onnx release/onnx/model.onnx \
  --text "今天天气真不错。" --voice M2 --output out.wav
```

试听样本：`release/samples/{F2,M2,M3}-1.wav`（同一句话「今天天气真不错，我们一起去公园散步吧。」）。

## 架构

沿用 tiny-voca 的**源-滤波器合成器**（25,862 参数，直接输出波形，无神经声码器）：

```
中文文本 → pypinyin+jieba 前端 → 45 符号表（声调复用 stress 通道，6 级）
  → 文本编码器（4 层 / 192 通道 / 4 头 RoPE pre-norm）
  → 时长 + 停顿预测 → 按帧展开
  → 帧级 Transformer A（2 层：音高 / 浊音 / 能量）
  → 帧级 Transformer B（5 层）
  → 源-滤波器合成器 → 24 kHz 波形
```

与上游的差异（详见 `docs/model-card.md`）：

1. **中文前端** `zh_text.py`：pypinyin（带词级 jieba 分词消歧）→ POLYGLOT 风格音素集（z→dz、c→ts、x→sh、ai→a+i、eng→a+ng、ian→i+a+n…），声调 1–5 + 轻声映射到 6 级 stress 通道，只挂在元音上。
2. **中文 CTC 对齐器**：标注用 `lyonlu13/wav2vec2-large-zh-singing-phoneme-ctc`，一 token 一标签，Viterbi 强制对齐 + 能量/浊音质检。
3. **增量音色扩展**：`train.py` 支持在已有 checkpoint 上新增 speaker（嵌入表扩行、旧音色权重逐位保留），用于从双音色续训到三/四音色。
4. **Windows 兼容**：`prepare.py` 的 fcntl 文件锁降级。

## 训练数据

- 语料 **10,696 句**，全部自建（模板生成 + 古诗改写），无第三方版权文本。
- 三个音色的参考音频由 **Qwen3-TTS VoiceDesign / 1.7B Base** 按文字描述合成（`data/voices/voices.json` 记录了每个音色的设计指令与 ASR 校验 CER=0）。
- 每句用对应音色合成语音 → CTC 强制对齐 → 质检（元音浊音率、对齐置信度、音素时长、语速）→ 通过 **28,231 条 / 25.25 小时**（F2 10,101 / M2 8,339 / M3 9,791，含验证/测试集）。
- 数据卡：`docs/dataset-card.md`。语料文本以 CC BY 4.0 发布；合成音频与特征不随仓库分发（体积原因），可用 `scripts/` 完整复现。

## 复现训练

```bash
pip install -e ".[prepare,annotate,generate]"

python scripts/build_corpus.py          # 1. 语料
python scripts/design_voices.py         # 2. 音色参考（Qwen3-TTS）
python scripts/generate_audio_zh.py     # 3. 逐句合成
python -m tiny_voca.annotate ...        # 4. CTC 对齐 + 质检
python -m tiny_voca.prepare ...         # 5. 声学特征
python -m tiny_voca.train ...           # 6. 训练（见 docs/training.md）
python -m tiny_voca.export ...          # 7. ONNX 导出
```

完整命令与超参见 `docs/training.md`。`scripts/strip_voice.py` 演示了如何从多音色 checkpoint 剥离某个音色（发布版即用此法从四音色内部版裁出三音色，其余权重逐位不变）。

## 评测

验证集（86 条，预测时长/音高，非 teacher-forced）：

| 指标 | 值 |
|---|---|
| mel L1 | 0.539 |
| STFT L1 | 1.211 |
| 停顿准确率 | 97.3% |
| 浊音准确率 | 96.0% |
| 时长比 | 0.975 |
| 音高误差 | 1.26 半音 |

ASR 可懂度（faster-whisper 转写 vs 原文 CER）见 `docs/model-card.md`。

## 测试

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest tests -q     # 69 passed
```

测试覆盖：中文前端（符号表/声调/多音字/零声母/UNK）、模型前向与 padding 不变性、数据加载、CTC 对齐、ONNX 导出一致性、长文本分句与峰值限制、CLI。

## 许可

- 代码：**Apache-2.0**（沿用上游 tiny-voca，Copyright 2026 Muhammed Nazeem；本 fork 修改 Copyright 2026 ValueMoonLab）。见 `LICENSE` / `NOTICE`。
- 语料文本：**CC BY 4.0**。
- 模型权重：Apache-2.0。
- 第三方模型（CTC 对齐器、Qwen3-TTS、faster-whisper）仅用于离线标注/生成/评测，**不随仓库分发，推理不需要**，各自遵循其原许可。

## 局限

- 仅普通话；不支持英文/方言/代码切换（会明确拒绝）。
- 合成数据训练，音色是「设计出来的」而非真人克隆；自然度不及大模型 TTS，但体积极小、CPU 实时、可完全离线。
- 数字/日期按 pypinyin 默认读法，未做复杂文本归一化（TN）。
- 单句上限 512 token / 3000 帧；长文本由 `speak_text` 自动分句拼接。

---

## English summary

**qora-voca-zh** is a 4.5M-parameter, three-voice (F2 young female / M2 mature male / M3 young male) Mandarin Chinese TTS model trained from scratch on 25.25 h of Qwen3-TTS-generated speech, on a single RTX 3060. It uses a source-filter synthesizer (no neural vocoder) and runs in real time on CPU. Weights: 17.3 MB PyTorch / 21.4 MB ONNX. Apache-2.0, forked from [tiny-voca](https://github.com/n4ze3m/tiny-voca). The Chinese front end is pypinyin + jieba mapped to a POLYGLOT-style phone inventory with tones on the stress channel; alignment uses a Mandarin CTC phoneme recogniser offline. No pretrained weights are loaded by the speech model itself. See `docs/` for the model card, dataset card, and training recipe.
