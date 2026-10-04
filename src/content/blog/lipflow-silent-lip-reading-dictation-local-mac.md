---
title: "Lipflow：免麦克风，对着摄像头无声嘴动，文字直接打出来"
titleEn: "Lipflow: Silent Dictation via Lip Reading — No Microphone, Just Your Webcam"
description: "amywork777/lipflow，MIT，458 stars，Python。按住键盘键、对着摄像头无声嘴动，松手后文字直接出现在光标处，不需要麦克风，不发出任何声音。完全本地运行，支持 Apple Silicon Mac / Windows / Linux。AI 流水线：摄像头捕捉嘴型 25fps → VSR 编码器（Apple GPU）→ beam search + 语言模型 → 可选 LLM 修正（Claude / Codex / 本地 Qwen3-0.6B / Ollama）→ 粘贴到光标。纯嘴型词错误率 31.9%；加轻声低语的 Whisper 模式降至 6.9%。支持用户个人化微调：用自己的面部视频和习惯用语优化模型。"
descriptionEn: "amywork777/lipflow, MIT, 458 stars, Python. Hold a key, silently mouth words at your webcam, let go — the text appears at your cursor. No microphone required. Fully local on Apple Silicon Mac, Windows, or Linux. Pipeline: webcam at 25fps → VSR encoder (Apple GPU) → beam search + language model → optional LLM cleanup (Claude, Codex CLI, on-device Qwen3-0.6B, Ollama) → paste. Word error rate: 31.9% lips-only; 6.9% with Whisper mode (soft whisper + lip reading). Supports personalized fine-tuning on your own face and phrasing."
pubDate: 2026-10-04
heroImage: "../../assets/images/lipflow-silent-lip-reading-dictation-local-mac-banner.jpg"
category: "Tech-Experiment"
tags: ["唇读", "语音输入", "本地AI", "Apple Silicon", "无声输入", "开源工具"]
lang: "zh-CN"
wechatTitle: "Lipflow：免麦克风无声嘴型本地输入法"
wechatDigest: "MIT 458星；摄像头读嘴型无需麦克风；本地跑；纯嘴31.9%词错；加低语降至6.9%"
---

开会、夜里、公共场合——很多时候你想用语音输入，但不能出声。

Lipflow 换了一条路：摄像头看嘴型，不需要麦克风，不发出任何声音，文字直接打到光标所在的地方。

GitHub: https://github.com/amywork777/lipflow | ⭐ 458 | MIT | Python

---

## 怎么用

一句话：按住右 Option（Mac）或右 Ctrl（Windows/Linux），对着摄像头无声嘴动你想说的话，松手，文字出现在光标处。

不是语音识别，不是麦克风加降噪，是真正的嘴型识别——摄像头看你嘴唇的运动轨迹，推断你在说什么。

双击按键进入免持模式，Esc 取消。

---

## 技术流水线

```
按住键 → 摄像头 25fps 捕捉 → 面部关键点 → 嘴部裁剪
                                              ↓
        粘贴到光标 ← LLM 修正（可选）← beam search + 语言模型 ← VSR 编码器（Apple GPU）
```

中间有一个实时预览：每 0.45 秒出一次贪心 CTC 结果，你可以看到模型在猜什么，不用等到松手才知道结果。

**VSR 编码器**：视觉语音识别模型，在 Apple Silicon 的 Metal GPU 上跑，M4 Pro 上约 0.16 秒/句。

**Beam search + 语言模型**：候选路径解码，帮助处理视觉上看起来相同的音（p/b/m，f/v，t/d/n 在嘴型上几乎没有区别）。

**LLM 修正（Cleanup）**：把模型的 top-3 猜测 + 你最近几条听写内容发给 LLM，让它选出最合理的一条并修正大小写、标点、数字。可选：
1. **Claude**（默认模型 claude-opus-5-5，低 effort，可用 `LIPFLOW_MODEL` 覆盖）
2. **Codex CLI**（用 ChatGPT Plus 额度，安装后 `codex login` 就能用）
3. **本地 Qwen3-0.6B 4-bit MLX**（约 350MB，完全离线，Apple Silicon 专用，~0.2 秒/句）
4. **Ollama**（`ollama pull qwen3:4b`）
5. **离线规则**（句子大写、数字处理、末尾标点，无需 LLM）

默认 Automatic：有 `ANTHROPIC_API_KEY` 就用 Claude，有本地 MLX 就用本地，否则走离线规则。

---

## 准确率

| 模式 | 词错误率 |
|------|----------|
| 纯嘴型 | 31.9% |
| 嘴型 + 轻声低语（Whisper 模式） | 6.9% |

Whisper 模式：Settings → Whisper mode，同时启用麦克风（只在按住键时），用 Audio-Visual Speech Recognition 模型合并嘴型和音频信号。1.8GB 额外模型，首次使用时下载。

31.9% 的词错误率看起来高，但实际使用效果取决于：
- 加没加 LLM 修正（修正后实际可用性大幅提升）
- 个人化训练做没做
- 使用场景的词汇范围

---

## 个人化训练

Lipflow 会在你的硬件上微调模型——包括两部分：

1. **你的面部**：装好后做一个 5-10 分钟的练习（24 句话），训练嘴型模型适应你的面部特征，保留验证集，只在识别率提升时保存新模型。
2. **你的用词**：从 Wispr Flow 导入听写历史，或从文本文件导入，让语言模型学习你习惯的表达和专有名词。

```bash
# 导入 Wispr Flow 历史
uv run lipflow import-wispr

# 或者从文本文件导入
uv run lipflow import-wispr --from-text my-writing.txt
```

当你纠正 Lipflow 打出的错误（松手后 30 秒内），它会把那条视频片段存下来，下次训练时用上。

---

## 安装

**Mac（Apple Silicon，macOS 13+）**：

```bash
git clone https://github.com/amywork777/lipflow.git ~/code/lipflow
cd ~/code/lipflow && ./setup.sh
open /Applications/Lipflow.app
```

脚本自动安装依赖、下载约 1.2GB 模型、构建 .app。首次启动需要授权摄像头、辅助功能和输入监控（系统设置里授权一次就行），然后做练习和训练，约 8 分钟。

**Windows**：`setup.ps1`，需要 Windows 10/11 64-bit，约 3GB。Cleanup 只能用 Claude API 或 Codex CLI（本地 MLX 是 Mac only）。

**Linux**：`uv sync` + `./scripts/download-models.sh`，需要 v4l2 摄像头 + wl-clipboard / wtype 等粘贴工具。

---

## 局限

- **纯嘴型模式准确率有上限**：视觉同形词（p/b/m 等）在任何视觉模型上都难区分，LLM 修正是实际上最大的精度来源
- **个人化训练是 Mac-only**：Windows/Linux 的纠错学习、上下文读取目前不支持或功能有限
- **本地 MLX Cleanup 是 Apple Silicon 专属**：Windows/Linux 用 Ollama 或 Claude API
- **需要好光线**：嘴型识别依赖清晰的摄像头画面，光线差或遮挡会明显降低准确率
- **每次启动约 8 分钟初始化**（首次）：之后约 1-2 分钟

---

## 一句话定位

Lipflow = 「摄像头版语音输入，专为不能出声的场景设计，完全本地运行」。

如果你经常在不方便发声的环境里需要快速输入，并且有 Apple Silicon Mac，值得装上试一试——个人化训练 8 分钟，之后准确率会比默认模型好不少。

---

> MIT 开源，商业使用无限制。开源仅供学习参考，词错误率为测试集数据，实际效果因硬件和使用习惯而异。

---

<!--EN-->

## Lipflow: Silent Lip-Reading Dictation — No Microphone Required

Meetings, late nights, public spaces — there are many situations where you want to dictate but can't make a sound.

Lipflow takes a different approach: it reads your lip movements via webcam, with no microphone and no sound. Text appears at your cursor when you let go of the key.

GitHub: https://github.com/amywork777/lipflow | ⭐ 458 | MIT | Python

---

### How It Works

Hold right Option (Mac) or right Ctrl (Windows/Linux), silently mouth what you want to say, release — the text appears at your cursor. Double-tap for hands-free mode, Esc to cancel.

**Pipeline:**

```
Hold key → webcam 25fps → face landmarks → mouth crops
                                            ↓
paste at cursor ← LLM cleanup (optional) ← beam search + LM ← VSR encoder (Apple GPU)
```

A live preview fires every 0.45 seconds during capture — you can see the model's guesses in real time rather than waiting for the final result.

**VSR encoder**: Visual Speech Recognition model on Apple Silicon Metal GPU. ~0.16s per sentence on M4 Pro.

**LLM cleanup options**: Claude (claude-opus-5-5, low effort), Codex CLI (ChatGPT Plus quota), on-device Qwen3-0.6B 4-bit MLX (~350MB, offline, Mac-only, ~0.2s/sentence), Ollama (qwen3:4b), or offline rules (casing + punctuation + number formatting).

---

### Accuracy

| Mode | Word Error Rate |
|------|-----------------|
| Lips only | 31.9% |
| Lips + soft whisper (Whisper mode) | 6.9% |

The 31.9% raw WER is high, but with LLM cleanup and personal fine-tuning, real-world usability improves substantially — especially when your vocabulary is narrower than the full test set.

---

### Personalized Fine-Tuning

Two layers of personalization:

1. **Your face**: a ~24-sentence practice session (8 minutes) fine-tunes the lip-reading model on your specific face geometry. The fine-tuned model is only kept if it improves accuracy on a held-out validation set.

2. **Your vocabulary**: import from Wispr Flow dictation history or a text file to teach the language model your phrasing and names. Corrections made within 30 seconds are saved as training clips for the next round.

---

### Setup

**Mac (Apple Silicon, macOS 13+):**

```bash
git clone https://github.com/amywork777/lipflow.git ~/code/lipflow
cd ~/code/lipflow && ./setup.sh
open /Applications/Lipflow.app
```

Downloads ~1.2GB of models, builds the .app. First launch: authorize camera + accessibility + input monitoring, then ~8 minutes of practice and training.

**Windows / Linux**: see README — `setup.ps1` or `uv sync` + model download. On-device MLX cleanup is Mac-only; use Ollama or Claude API instead.

---

### Constraints

- Visually ambiguous phonemes (p/b/m, f/v, t/d/n) are fundamentally hard for any lip-reading model — LLM cleanup is the biggest practical accuracy lever
- Personal training, in-field correction learning, and on-device MLX cleanup are currently Mac-only
- Requires good camera lighting; occlusion or low light significantly hurts accuracy
- First-time setup ~8 minutes; subsequent launches are faster

---

> MIT, no commercial restrictions. Word error rates are from test-set benchmarks — real performance varies by hardware, vocabulary, and lighting. For technical reference only.
