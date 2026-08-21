---
title: "Swift Qwen3 TTS：五种压缩技术让模型从 2.35 GB 缩到 808 MB，Apple Silicon 本地实时语音合成"
titleEn: "swift-qwen3-tts-apple-silicon-compression-token-map-indirection"
description: "AtomGradient 发布的 Qwen3 TTS 端侧压缩论文与工程实现。五种正交压缩技术（词汇剪枝 + ST 编码器剥离 + FP16 转换 + 4-bit 量化 + MLP 神经元/层剪枝）将 Qwen3 TTS 0.6B 从 2.35 GB 压缩到 808 MB（减少 67%），峰值内存从 5.14 GB 降到 2.13 GB，Apple Silicon 上实现 0.68x 实时因子。核心创新：Token Map Indirection 把 1.51 万词的文本嵌入矩阵从 622 MB 压到 194 MB 且完全无损。完整推理引擎用 Swift + MLX 实现，无 Python 依赖。"
descriptionEn: "AtomGradient's compression paper and engineering implementation for Qwen3 TTS edge deployment. Five orthogonal techniques (vocabulary pruning + ST encoder stripping + FP16 + 4-bit quantization + MLP neuron/layer pruning) reduce Qwen3 TTS 0.6B from 2.35 GB to 808 MB (67% reduction), peak memory from 5.14 GB to 2.13 GB, achieving 0.68x RTF on Apple Silicon. Core innovation: Token Map Indirection compresses the text embedding matrix from 622 MB to 194 MB losslessly. Full inference engine in Swift + MLX, no Python dependencies."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["TTS", "语音合成", "Apple Silicon", "模型压缩", "Qwen3", "Swift", "MLX", "边缘推理"]
heroImage: "../../assets/images/swift-qwen3-tts-apple-silicon-compression-token-map-indirection-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

论文页：atomgradient.github.io/swift-qwen3-tts  
GitHub：AtomGradient/swift-qwen3-tts  
HuggingFace：AtomGradient/Qwen3-TTS-0.6B-CustomVoice-*  
技术栈：Swift + Apple MLX（无 Python 依赖）

---

## 一、结果数字

| 指标 | 原始 | 压缩后 | 变化 |
|------|------|--------|------|
| 磁盘体积 | 2,494 MB | **808 MB** | -67.6% |
| 峰值内存 | 5.14 GB | **2.13 GB** | -58.6% |
| 加载时间 | 2.74 s | **2.50 s** | -8.8% |
| 实时因子（RTF） | 0.70 | **0.68** | 快于实时 |

808 MB 的模型，峰值内存不超过 2 GB，在 Apple Silicon 上生成比实时还快的语音（RTF < 1 = 生成速度快于播放速度）。

---

## 二、五种正交压缩技术

这五种技术的设计原则是**正交且可叠加**——互不干扰，顺序无关，可以选择性组合。

### 1. 词汇剪枝（Vocabulary Pruning）——无损，-428 MB

Qwen3 TTS 继承了 Qwen3 的完整多语言词汇表（151,936 个词），但 TTS 任务实际只用到约 47K 个词。

关键发现：**BPE 空格前缀问题**。同一个词在句首和句中会产生不同的 token：

```
encode("my")  = [2408]   # 句首
encode(" my") = [847]    # 句中（空格前缀，不同 token！）
```

如果遗漏空格前缀变体，句中词会映射到零向量，触发提前 EOS（生成提前结束）。正确处理后词汇表从 20K 扩展到 47K，但仍只有原始 152K 的 31%。

**实现方式：Token Map Indirection**

```swift
embed(t) = E'[m[t]]
// m ∈ ℤ^151,936（索引映射数组）
// E'∈ ℝ^{47,427 × 2,048}（精简嵌入矩阵）
```

文本嵌入矩阵从 `[151,936 × 2,048]`（622 MB）缩小到 `[47,427 × 2,048]`（194 MB）。**数学上完全无损**——每个保留的嵌入行都是原矩阵的精确拷贝。

### 2. ST 编码器剥离（Speech Tokenizer Encoder Stripping）——无损，-225 MB

SpeechTokenizer 的编码器（Encoder）仅用于语音克隆（Voice Cloning）功能，标准 TTS 生成中不需要。直接移除，完全无损。

### 3. FP32 → FP16——准无损，-228 MB

语音分词器解码器的权重从 FP32 转为 FP16。检测到最大权重绝对值 `max|w| < 36`，在 FP16 精度范围内安全，舍入误差约 10⁻⁴，感知上不可辨别。

### 4. 4-bit 量化——有损（效果接近原始）

对主模型 249 个线性层做 4-bit 量化，嵌入层保持 BF16。主模型从 1,384 MB 压到 579 MB，损失表现为平均音频时长略增约 1 秒（随机采样下的自然波动）。

### 5. MLP 神经元剪枝 + 层剪枝（可选）

- **MLP 神经元剪枝**：只移除不活跃神经元，效果接近原始
- **层剪枝（-3 层）**：有轻微韵律退化，适合资源极度受限的场景

---

## 三、模型架构

Qwen3 TTS 0.6B 是 Codec 架构的语音合成模型：

| 组件 | 架构 | 关键参数 |
|------|------|---------|
| **Talker**（主生成器） | 28 层 Transformer | hidden=1024，heads=16（GQA 8 KV），M-RoPE [24,20,20]，SwiGLU MLP |
| **CodePredictor**（码本预测器） | 5 层 Transformer | 16 个码本头，QK-Norm with RMSNorm |
| **SpeechTokenizer**（语音分词器） | Conv Decoder + Split-RVQ | 1 个语义码本 + 15 个声学码本，12.5 Hz，24kHz 输出 |

原始 BF16 版本的存储分布：
- 文本嵌入矩阵：622 MB（34.4%）← 词汇剪枝的主要目标
- MLP 层 ×28：623 MB（34.4%）
- 注意力层 ×28：415 MB（22.9%）

---

## 四、Swift 推理引擎

完整推理流水线用 Swift + Apple MLX 原生实现，**无 Python 依赖**。

```swift
// Token Map Indirection 实现
func embedText(_ ids: MLXArray) -> MLXArray {
    if let tokenMap = model.textTokenMap {
        return model.textEmbedding(tokenMap[ids])  // 映射查找
    }
    return model.textEmbedding(ids)                // 直接查找
}
```

**生成长度控制**（防止随机采样下的失控生成）：

```
T_max = min(T_config, max(75, 6 · |tokens(x)|))
```

---

## 五、快速使用

```bash
git clone https://github.com/AtomGradient/swift-qwen3-tts.git
cd swift-qwen3-tts

swift run Qwen3TTSDemo \
  --model path/to/Qwen3-TTS-0.6B-CustomVoice-4bit-pruned-vocab-lite \
  --speaker Aiden \
  --text "Hello, this is on-device TTS!" \
  --output output.wav
```

### 预构建模型（HuggingFace）

| 模型 | 大小 | 质量 |
|------|------|------|
| `Qwen3-TTS-0.6B-CustomVoice-bf16-pruned-vocab-lite` | 1.5 GB | 无损 |
| `Qwen3-TTS-0.6B-CustomVoice-4bit-pruned-vocab-lite` | **808 MB** | 接近原始 |

两个模型均支持：
- **9 个说话人**：Aiden、Serena、Vivian、Ryan、Uncle Fu、Ono Anna、Sohee、Eric、Dylan
- **12 种语言**
- **情感控制**

---

## 六、技术意义

这篇工作的核心贡献有两个：

**一是方法论**：五种正交压缩技术的组合框架。每种技术针对不同冗余来源（词汇冗余、架构冗余、精度冗余、参数冗余），不互相干扰，可以按实际约束（内存、质量、速度）选择叠加。这套框架对其他大参数量 TTS 模型同样适用。

**二是 Token Map Indirection**：这个技术解决的是「如何在不重新训练分词器、不修改模型架构的情况下，对文本嵌入矩阵做无损压缩」。对于任何继承了大词汇表语言模型的多模态/语音模型，这个思路都有参考价值。

808 MB 在 Apple Silicon 上实时运行，原生 Swift 实现——这是 2026 年端侧 AI 落地的典型样本。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Swift Qwen3 TTS: Five Compression Techniques, 2.35 GB → 808 MB, Real-Time on Apple Silicon

*by Mycelium Protocol*

---

Paper: atomgradient.github.io/swift-qwen3-tts  
GitHub: AtomGradient/swift-qwen3-tts  
HuggingFace: AtomGradient/Qwen3-TTS-0.6B-CustomVoice-*  
Stack: Swift + Apple MLX (no Python dependencies)

---

### Results

| Metric | Original | Compressed | Change |
|--------|----------|------------|--------|
| Disk size | 2,494 MB | **808 MB** | -67.6% |
| Peak memory | 5.14 GB | **2.13 GB** | -58.6% |
| Load time | 2.74 s | **2.50 s** | -8.8% |
| Real-time factor | 0.70 | **0.68** | Faster than real-time |

808 MB total, under 2 GB peak memory, 0.68x RTF on Apple Silicon (RTF < 1 means generation outpaces playback).

---

### Five Orthogonal Compression Techniques

Designed to be orthogonal and stackable — each targets a distinct source of redundancy, they compose without interference and can be applied in any order.

**1. Vocabulary Pruning — Lossless, -428 MB**

Qwen3 TTS inherits Qwen3's full 151,936-token multilingual vocabulary, but TTS only uses ~47K tokens in practice.

Critical finding — **BPE space-prefix problem**: the same word produces different tokens depending on sentence position:

```
encode("my")  = [2408]   # sentence-initial
encode(" my") = [847]    # mid-sentence (space-prefix, different token!)
```

Missing space-prefixed variants causes mid-sentence words to map to zero vectors, triggering premature EOS. Correct handling expands from 20K to 47K tokens — still only 31% of the original 152K vocabulary.

**Token Map Indirection** implementation:
```swift
embed(t) = E'[m[t]]   // m ∈ ℤ^151,936, E' ∈ ℝ^{47,427 × 2,048}
```

Text embedding matrix: 622 MB → 194 MB. **Mathematically lossless** — every preserved row is an exact copy from the original.

**2. ST Encoder Stripping — Lossless, -225 MB**

The SpeechTokenizer encoder is only needed for voice cloning, not standard TTS generation. Remove it: completely lossless.

**3. FP32 → FP16 — Quasi-lossless, -228 MB**

Speech tokenizer decoder weights. `max|w| < 36` confirms FP16 safety. Rounding error ~10⁻⁴, imperceptible.

**4. 4-bit Quantization — Lossy (near-identical)**

249 linear layers in the main model, embeddings kept in BF16. Main model: 1,384 MB → 579 MB. Quality impact: ~1s longer average audio under stochastic sampling (temperature 0.9).

**5. MLP Neuron Pruning + Layer Pruning (optional)**

Neuron pruning targets only inactive neurons — near-identical quality. Layer pruning (-3 layers) introduces minor prosody degradation; suitable for extreme resource constraints.

---

### Model Architecture

Qwen3 TTS 0.6B is a codec-based speech synthesis model:

| Component | Architecture | Key Params |
|-----------|-------------|------------|
| **Talker** | 28-layer Transformer | hidden=1024, heads=16 (GQA 8 KV), M-RoPE [24,20,20], SwiGLU MLP |
| **CodePredictor** | 5-layer Transformer | 16 codebook heads, QK-Norm with RMSNorm |
| **SpeechTokenizer** | Conv Decoder + Split-RVQ | 1 semantic + 15 acoustic codebooks, 12.5 Hz, 24kHz output |

Original storage: text embedding 622 MB (34.4%), MLP layers 623 MB (34.4%), attention layers 415 MB (22.9%) — vocabulary pruning attacks the single largest chunk.

---

### Swift Inference Engine

Full pipeline in native Swift + Apple MLX, no Python dependencies.

```swift
func embedText(_ ids: MLXArray) -> MLXArray {
    if let tokenMap = model.textTokenMap {
        return model.textEmbedding(tokenMap[ids])  // mapped lookup
    }
    return model.textEmbedding(ids)                // direct lookup
}
```

Generation length control (prevents runaway generation under stochastic sampling):
```
T_max = min(T_config, max(75, 6 · |tokens(x)|))
```

---

### Quick Start

```bash
git clone https://github.com/AtomGradient/swift-qwen3-tts.git
cd swift-qwen3-tts

swift run Qwen3TTSDemo \
  --model path/to/Qwen3-TTS-0.6B-CustomVoice-4bit-pruned-vocab-lite \
  --speaker Aiden \
  --text "Hello, this is on-device TTS!" \
  --output output.wav
```

**Pre-built models** (HuggingFace: AtomGradient/):

| Model | Size | Quality |
|-------|------|---------|
| bf16-pruned-vocab-lite | 1.5 GB | Lossless |
| **4bit-pruned-vocab-lite** | **808 MB** | Near-identical |

Both support 9 speakers, 12 languages, emotion control.

---

### Why It Matters

Two core contributions:

**Methodology**: The five-technique framework shows how to decompose compression into orthogonal dimensions — vocabulary redundancy, architecture redundancy, precision redundancy, parameter redundancy. Each addressed independently; stack them to meet specific constraints. Applicable to other large-vocabulary TTS models.

**Token Map Indirection**: Solves "how to losslessly compress the text embedding matrix without retraining the tokenizer or modifying the architecture." Any multimodal or speech model that inherits a large LM vocabulary faces this problem; this technique is directly transferable.

808 MB running faster than real-time on Apple Silicon, native Swift — a clean example of 2026 edge AI deployment done right.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
