---
title: "Confucius4-R2T2：网易有道的真流式 ASR——用 LSP 彻底消除文字抖动"
titleEn: "Confucius4-R2T2: NetEase Youdao's True-Streaming ASR — LSP Eliminates Text Flicker Completely"
description: "netease-youdao/Confucius4-R2T2，306 stars，代码 Apache 2.0 / 模型权重单独 NetEase 许可证。2B 参数真流式 ASR，基于 Qwen3-ASR-1.7B，核心创新是最长稳定前缀（LSP）训练范式——输出只追加、绝不修改，从根本上解决假流式 ASR 的文字抖动问题。LibriSpeech-clean WER 2.13% vs Qwen3-ASR 流式模式 22.30%，160ms 默认分块，需 CUDA GPU，技术报告待发布。"
descriptionEn: "netease-youdao/Confucius4-R2T2 — 306 stars, Apache 2.0 code / separate NetEase model weight license. A 2B-parameter true-streaming ASR model based on Qwen3-ASR-1.7B. Core innovation: Longest Stable Prefix (LSP) training paradigm — output is append-only, never modified, fundamentally eliminating the text flickering problem of fake-streaming ASR. LibriSpeech-clean WER 2.13% vs Qwen3-ASR stream mode 22.30%. 160ms default chunk size. CUDA GPU required. Technical report pending."
pubDate: 2026-09-21
heroImage: "../../assets/images/confucius4-r2t2-true-streaming-asr-lsp-netease-youdao-banner.jpg"
category: "Tech-Experiment"
tags: ["asr", "speech-recognition", "streaming", "open-source", "netease", "ai-model"]
lang: zh-CN
---

`netease-youdao/Confucius4-R2T2` 是网易有道发布的开源流式语音识别模型，306 stars。它不是"又一个 ASR"——它试图解决现有流式 ASR 的根本性缺陷：文字抖动。

**GitHub**：github.com/netease-youdao/Confucius4-R2T2 | **Demo**：r2t2.youdao.com/demo | **Stars**：306 | **代码 License**：Apache 2.0 | **⚠️ 模型权重：NetEase 单独许可证**

---

## 假流式 vs 真流式：一个被忽视的本质区别

市面上大多数所谓"流式"ASR 模型，包括 Whisper、Qwen3-ASR 的流式模式，实际上是**假流式**：

```
假流式输出过程示意：
[0.5s] "我想"
[1.0s] "我想去"
[1.5s] "我想取消"     ← 覆盖了之前的输出
[2.0s] "我想取消订单"  ← 又覆盖了
```

模型边听边猜，猜错了就回头改。在屏幕上，你看到的文字在不断修改、跳变，这就是"文字抖动（text flickering）"。

Confucius4-R2T2 的核心主张是：**真流式 ASR 的输出应该像一支笔从左往右写字——写下去的字不会被擦掉**。

---

## LSP：最长稳定前缀

R2T2（Real-to-Text 2）的命名就是在强调"实时转文字"的场景。它的核心训练范式叫做 **LSP（Longest Stable Prefix，最长稳定前缀）**。

LSP 的直觉：在任何时刻，模型已输出的内容，就是迄今为止"能确定不会再改"的最长前缀。

训练时构造了三类数据：

1. **稳定前缀数据**：告诉模型"在音频第 X 秒时，哪些词已经可以确定"
2. **强制时间对齐数据**：让模型学会把词和时间轴精确绑定
3. **Token 级音频分割**：细粒度地对应每个 token 对应的音频帧

结果是模型输出具有严格的单调性——已输出文字只增不改，即使是后续更多音频输入进来。

---

## 性能对比

对比 Qwen3-ASR 官方流式模式（同基座）：

| 指标 | Qwen3-ASR 流式 | R2T2（160ms块） | R2T2（80ms块） |
|------|----------------|-----------------|-----------------|
| LibriSpeech-clean WER | 22.30% | **2.13%** | 2.78% |
| LibriSpeech-other WER | — | **4.88%** | 5.59% |
| Wenet-net CER（中文） | — | **5.87%** | 6.42% |
| 文字抖动 | ✗ 有 | ✅ 无 | ✅ 无 |

Qwen3-ASR 流式 WER 22.30% 的根本原因就是"不断修改历史输出"——统计 WER 时，每次中间修改都计为错误。R2T2 通过 LSP 约束，把实际有效 WER 压到了离线 ASR 的水平。

---

## 技术规格

- **参数量**：2B（基于 Qwen3-ASR-1.7B 微调）
- **支持语言**：中文 + 英文为主，另支持 10+ 种语言
- **分块大小**：80ms～2000ms 可配（默认 160ms，延迟与准确性的最佳平衡点）
- **推理后端**：vLLM（推荐）或 HuggingFace Transformers
- **硬件要求**：CUDA GPU（目前不支持 CPU 推理；社区 PR #604 在为 Apple Silicon Metal 后端开发中）
- **在线 Demo**：r2t2.youdao.com/demo
- **技术报告**："即将发布"（截至调研时尚未公开）

---

## ⚠️ 许可证：代码和模型权重是两个不同许可证

这是使用前必须注意的细节：

- **代码**（训练脚本、推理代码、服务器代码）：Apache 2.0，商用友好
- **模型权重**：NetEase Youdao 自定义许可证，**不是 Apache 2.0**

使用模型权重前，请仔细阅读仓库中的 `MODEL_LICENSE` 文件，确认你的使用场景是否符合网易有道的商业使用条款。个人研究和学术使用通常无问题，商业部署需要确认。

---

## 安装与部署

### Docker（最简单）

```bash
docker pull qwenllm/qwen3-asr:latest
# R2T2 权重会在首次运行时自动下载
```

### conda

```bash
conda create -n confucius python=3.10
conda activate confucius
pip install -r requirements.txt
```

### uv（推荐，速度最快）

```bash
uv venv && uv pip install -r requirements.txt
```

### 启动 vLLM 服务

```bash
python -m vllm.entrypoints.openai.api_server \
    --model netease-youdao/Confucius4-R2T2 \
    --served-model-name Confucius4-R2T2 \
    --host 0.0.0.0 --port 8000
```

### WebSocket 服务（已知有 bug）

官方 WebSocket 实时服务目前存在 bug，社区已有修复版本：

```bash
# 社区修复版（xiaowei-confucius4-r2t2）
# 在仓库 Issues 中可找到对应 fork 链接
```

---

## 实际使用（Python 示例）

```python
import soundfile as sf
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="token")

audio, sr = sf.read("audio.wav")
# 按 chunk_size（秒）切分音频，逐块发送
chunk_size = 0.16  # 160ms

with client.audio.transcriptions.stream(
    model="Confucius4-R2T2",
    file=open("audio.wav", "rb"),
    stream=True,
) as stream:
    for chunk in stream:
        if chunk.type == "transcript.text.delta":
            print(chunk.delta, end="", flush=True)  # 只追加，不修改
```

输出流中的每个 delta 只会追加新词，不会触发前文修改——这就是 LSP 约束在推理层的体现。

---

## 不足之处

**1. 技术报告未发布**：核心创新 LSP 的完整推导和消融实验还没有公开论文，目前的技术细节主要来自 README 和 Issues，独立验证困难。

**2. GPU 硬件要求**：不支持 CPU 推理，Mac / 无 GPU 机器无法本地运行。Apple Silicon 支持尚在社区开发中（PR #604），尚无合并时间表。

**3. WebSocket 服务有 bug**：实时音频流服务目前不稳定，需要用社区 fork 版本，官方尚未修复。

**4. stars 较少（306）**：相对于技术水平而言关注度偏低，可能因为 NetEase 模型权重许可证限制了部分潜在用户。

**5. 模型权重许可证需确认**：商业场景部署前需要仔细阅读 NetEase 的许可证条款，不能直接用"代码是 Apache 2.0"来推断模型权重可以商用。

---

## 怎么看这个工作

R2T2 做的事情有工程价值：**把"只追加不修改"这个直觉约束，变成了可训练的 LSP 范式**，并在基准测试上大幅降低了流式 WER。

对比实验中 Qwen3-ASR 流式模式 22.30% WER，与 R2T2 的 2.13% 相差 10 倍——这个差距不是模型能力的差距，而是训练范式的差距。Qwen3-ASR 本身是强模型，只是其官方流式模式没有 LSP 约束，导致频繁回改产生大量统计错误。

适合场景：实时字幕、同声传译助手、会议记录、语音控制界面——凡是"用户看着文字在生成"的场景，文字抖动都是体验问题，R2T2 的输出模式可以直接解决这个问题。

不适合场景：离线批量转写（没有必要流式）、没有 CUDA GPU 的部署环境、需要完全商业自由使用模型权重的场景（需先确认许可证）。

> 代码 Apache 2.0，模型权重使用前请阅读 NetEase Youdao 许可证条款，仅供学习研究参考。

---

<!--EN-->

## Confucius4-R2T2: True-Streaming ASR from NetEase Youdao

`netease-youdao/Confucius4-R2T2` is NetEase Youdao's open-source streaming speech recognition model (306 stars). Its key contribution is not benchmark numbers, but solving a fundamental flaw in existing streaming ASR: text flickering.

**GitHub**: github.com/netease-youdao/Confucius4-R2T2 | **Demo**: r2t2.youdao.com/demo | **Stars**: 306 | **Code**: Apache 2.0 | **⚠️ Model weights**: Separate NetEase license

---

### Fake Streaming vs. True Streaming

Most "streaming" ASR models — including Whisper and Qwen3-ASR's streaming mode — are actually **fake streaming**:

```
Fake streaming output:
[0.5s] "I want"
[1.0s] "I want to"
[1.5s] "I want to cancel"     ← overwrites prior output
[2.0s] "I want to cancel the" ← overwrites again
```

The model predicts as it listens, and corrects itself by rewriting past output. On-screen, text jumps and flickers — a poor experience for real-time captions or voice control UIs.

R2T2's premise: **true streaming ASR output should only move forward — written text is never erased.**

---

### LSP: Longest Stable Prefix

The core training paradigm is **LSP (Longest Stable Prefix)**: at any point in time, the model's emitted text represents the longest prefix that will not change regardless of future audio input.

Training constructs three types of data:
1. **Stable-prefix data** — teaches the model which words are definitively committed at audio timestamp X
2. **Forced time-alignment data** — binds tokens precisely to audio frames
3. **Token-level audio segmentation** — fine-grained correspondence between tokens and audio frames

The result: outputs are strictly monotonic — emitted tokens are never revised, even as more audio arrives.

---

### Performance

Compared to Qwen3-ASR official streaming mode (same base model):

| Metric | Qwen3-ASR stream | R2T2 @160ms | R2T2 @80ms |
|--------|-----------------|-------------|------------|
| LibriSpeech-clean WER | 22.30% | **2.13%** | 2.78% |
| LibriSpeech-other WER | — | **4.88%** | 5.59% |
| Wenet-net CER (Chinese) | — | **5.87%** | 6.42% |
| Text flickering | ✗ Yes | ✅ None | ✅ None |

Qwen3-ASR's 22.30% WER in streaming mode is largely attributable to constant self-correction — every intermediate rewrite counts as an error in WER calculation. R2T2's LSP constraint brings streaming WER to offline-comparable levels.

---

### Specs

- **Parameters**: ~2B (fine-tuned from Qwen3-ASR-1.7B)
- **Languages**: Chinese + English primary; 10+ others
- **Chunk size**: 80ms–2000ms configurable (default 160ms)
- **Inference backend**: vLLM (recommended) or HuggingFace Transformers
- **Hardware**: CUDA GPU required — no CPU inference; Apple Silicon Metal support in community PR #604 (no merge timeline yet)
- **Technical report**: "coming soon" — not yet published as of this writing

---

### ⚠️ License: Code and Model Weights Are Different

Critical distinction:
- **Code** (training/inference scripts, server): Apache 2.0 — commercial-friendly
- **Model weights**: NetEase Youdao custom license — **not Apache 2.0**

Review the `MODEL_LICENSE` file in the repository before any commercial deployment. Academic and personal research use is generally fine; commercial use needs explicit confirmation.

---

### Installation

```bash
# Docker (simplest)
docker pull qwenllm/qwen3-asr:latest

# uv (fastest)
uv venv && uv pip install -r requirements.txt

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model netease-youdao/Confucius4-R2T2 \
    --served-model-name Confucius4-R2T2 \
    --host 0.0.0.0 --port 8000
```

**Note**: The official WebSocket real-time server has known bugs. Use the community-patched fork (search Issues for `xiaowei-confucius4-r2t2`) until the fix is merged.

---

### Limitations

1. **Technical report unpublished**: LSP theory and ablations are not yet in a public paper — hard to independently verify the mechanism.
2. **CUDA-only**: No CPU inference; Apple Silicon support still in community development.
3. **WebSocket server bugs**: Real-time audio streaming is unstable; community fork needed.
4. **Low star count (306)**: Underrecognized relative to technical quality, possibly because the model weight license restricts some users.
5. **Model weight license ambiguity**: Must explicitly confirm commercial use — Apache 2.0 on the code does not extend to the weights.

---

### Bottom Line

R2T2 makes a technically sound engineering contribution: converting the intuition "only append, never rewrite" into a trainable paradigm (LSP), and achieving ~10x better streaming WER compared to Qwen3-ASR's streaming mode on the same base model.

Best fit for: real-time captioning, simultaneous interpretation assistance, meeting transcription, voice control UIs — any scenario where users watch text being generated and text flickering is a noticeable UX problem.

Not suited for: offline batch transcription (streaming is unnecessary), environments without CUDA GPUs, commercial deployments requiring full model weight freedom (confirm license first).

> Code Apache 2.0. Model weights require reviewing NetEase Youdao's separate license. For learning and research only.
