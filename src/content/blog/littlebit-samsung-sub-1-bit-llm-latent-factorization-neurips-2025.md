---
title: "LittleBit：三星把 13B 模型压进 1GB 的方法，NeurIPS 2025"
titleEn: "LittleBit: How Samsung Compressed a 13B Model Under 1 GB — NeurIPS 2025"
description: "三星研究院发布 LittleBit（NeurIPS 2025，arXiv 2506.13771），把 LLM 权重压缩到 0.1 位/权重：把权重矩阵分解为低秩二值因子矩阵（{+1, −1}）+ 多尺度 FP16 缩放补偿，推理时直接用位运算代替浮点乘加。Llama2-13B 压到约 0.9 GB（FP16 的 1/31），0.1 BPW 的 Llama2-7B 在 benchmark 上超过 0.7 BPW 的 STBLLM。论文宣称内核级 11.6 倍加速，但这是理论内核吞吐量，不是端到端测量值，需要注意。续作 LittleBit-2（ICML 2026）已合入同一 GitHub 仓库。代码开源：github.com/SamsungLabs/LittleBit。"
descriptionEn: "Samsung Research releases LittleBit (NeurIPS 2025, arXiv 2506.13771): LLM weights compressed to 0.1 bits per weight by decomposing weight matrices into low-rank binary factor matrices ({+1, −1}) with multi-scale FP16 scaling compensation. Inference uses bitwise operations instead of floating-point multiply-accumulate. Llama2-13B compresses to ~0.9 GB (1/31 of FP16). LittleBit-quantized Llama2-7B at 0.1 BPW outperforms STBLLM at 0.7 BPW on benchmarks. The paper claims 11.6x kernel-level speedup — this is theoretical kernel throughput, not measured end-to-end. Follow-up LittleBit-2 (ICML 2026) is merged into the same GitHub repo. Code is open-source: github.com/SamsungLabs/LittleBit."
pubDate: 2026-10-09
heroImage: "../../assets/images/littlebit-samsung-sub-1-bit-llm-latent-factorization-neurips-2025-banner.jpg"
category: "Research"
tags: ["模型压缩", "量化", "本地模型", "开源模型", "三星", "NeurIPS"]
lang: "zh-CN"
wechatTitle: "LittleBit：三星把13B压进1GB的方法"
wechatDigest: "NeurIPS 2025；低秩二值因子分解；0.1位/权重；Llama2-7B超越0.7位模型；GitHub开源"
---

13B 模型，0.9 GB，NeurIPS 2025。这是三星研究院给出的结果，方法叫 LittleBit。

核心思路不是把权重数字变小，而是**把权重矩阵分解掉**——用低秩二值矩阵的组合来近似原始权重，推理时全程位运算，不做浮点乘法。

arXiv: https://arxiv.org/abs/2506.13771 | GitHub: https://github.com/SamsungLabs/LittleBit | Samsung Research | NeurIPS 2025

---

## 方法：低秩二值因子分解

传统量化的思路是把一个浮点数映射到更少的位（INT8、INT4……）。LittleBit 的思路不同：

**不是压缩数字，而是分解矩阵。**

对于权重矩阵 **W**，LittleBit 把它分解成若干对低秩因子矩阵的乘积之和：

```
W ≈ Σ (scale_i × B_i × C_i)
```

其中 **B_i** 和 **C_i** 是二值矩阵（每个元素只有 {+1, −1}），**scale_i** 是 FP16 缩放因子（按行、列、维度三个尺度各存一个）。

这个分解的关键好处：
- **二值矩阵乘法 = 位运算**：{+1, −1} 矩阵的内积可以完全用位运算（popcount）实现，不需要浮点乘法
- **FP16 缩放因子很少**：相对于整个权重矩阵，缩放因子数量极少，不显著增加存储

---

## 两个关键技术细节

**Dual-SVID 初始化**：不是随机初始化二值因子，而是用一种专为量化感知训练（QAT）设计的 SVD 变体（Dual Sign-Value-Independent Decomposition）来初始化，让起点更接近原始权重分布。

**残差补偿（Residual Compensation）**：二值化因子矩阵后必然有近似误差，残差补偿通过额外的低秩修正项来减小这个误差。两者组合让训练后的量化模型在极低位宽下仍能收敛。

---

## 实测结果

| 模型 | 位宽 | 内存 | 相对 FP16 |
|------|------|------|-----------|
| Llama2-13B FP16 | 16 | ~26 GB | 基准 |
| **LittleBit Llama2-13B** | **0.1 BPW** | **~0.9 GB** | **1/31** |
| STBLLM Llama2-7B | 0.7 BPW | — | — |
| **LittleBit Llama2-7B** | **0.1 BPW** | — | **超过 0.7 BPW** |

最后一行是论文的核心结论之一：极端压缩（0.1 BPW）的 LittleBit 在语言建模任务上超过了保留 7 倍更多位的竞争方法。

---

## 关于 11.6 倍加速：需要打折读

论文宣称相对 FP16 的 **11.6 倍推理加速**，这个数字有几个需要注意的地方：

1. **数字在版本间变化**：v1（2025年5月）写的是约 5 倍，后续版本改为 11.6 倍。数字为什么变，论文没有详细说明。

2. **这是内核级理论吞吐量**，不是端到端测量值。论文没有提供完整的端到端推理 benchmark（显存加载、KV cache、采样等环节的开销不在这个数字里）。

3. **没有独立第三方复现**（截至撰文时）。

合理预期：实际部署中的加速效果会低于 11.6 倍，但内存压缩（~31 倍）是真实的。

---

## 续作：LittleBit-2（ICML 2026）

同一 GitHub 仓库里已经包含了续作 LittleBit-2，通过 `--use_itq` 参数开启，论文发表于 ICML 2026。改进方向是**谱能量增益**和**潜在几何对齐**（Latent Geometry Alignment），进一步优化低秩因子的表示效率。如果你要用这个方法，LittleBit-2 是当前更新的版本。

Samsung Research Blog：
- LittleBit: https://research.samsung.com/blog/LittleBit-Ultra-Low-Bit-Quantization-via-Latent-Factorization
- LittleBit-2: https://research.samsung.com/blog/LittleBit-2-Maximizing-the-Spectral-Energy-Gain-in-Sub-1-Bit-LLMs-via-Latent-Geometry-Alignment

---

## 和其他量化方法的位置

LittleBit 在论文里对比了 RTN、GPTQ、OmniQuant、BiLLM、STBLLM、OneBit、BinaryMoS。它的独特点是**亚 0.5 位区域的鲁棒性**——其他方法在位宽低于 0.5 时会出现明显性能崩塌，LittleBit 在 0.1 BPW 依然维持有意义的输出。

和 GGUF 系列量化（Q2、Q4）的关系：LittleBit 的目标是比任何 GGUF 格式更激进地压缩，代价是需要定制化训练流程，不能对任意模型一键量化（不像 llama.cpp 的 quantize 命令）。目前 LM Studio、Ollama 不支持 LittleBit 格式。

---

## 使用方式

```bash
git clone https://github.com/SamsungLabs/LittleBit
# 参考 README 配置环境和运行量化
# LittleBit-2 通过 --use_itq 参数启用
```

无预训练权重发布（截至撰文），需要自己跑量化流程。代码是三星研究院的官方实现，包含 Dual-SVID 初始化和残差补偿的完整代码。

---

## 一句话说清楚

LittleBit 把权重矩阵分解成低秩二值因子 + 少量 FP16 缩放，推理全程位运算，在 0.1 BPW 下 13B 模型约 0.9 GB，性能超过 7 倍更高位宽的竞争方法。内存压缩是真实的，11.6 倍加速是内核理论值需打折。续作 LittleBit-2 已合入同一仓库。

---

> 论文 CC BY-NC-ND 4.0。Samsung Research，Banseok Lee 等，arXiv 2506.13771，NeurIPS 2025。开源仅供学习参考。

---

<!--EN-->

## LittleBit: How Samsung Compressed a 13B Model Under 1 GB — NeurIPS 2025

13B model, 0.9 GB, NeurIPS 2025. That's Samsung Research's result, using a method called LittleBit.

The core idea isn't making the weight numbers smaller — it's **decomposing the weight matrices** into low-rank binary matrix pairs, then running inference entirely with bitwise operations instead of floating-point multiply-accumulate.

arXiv: https://arxiv.org/abs/2506.13771 | GitHub: https://github.com/SamsungLabs/LittleBit | Samsung Research | NeurIPS 2025

---

### Method: Low-Rank Binary Factor Decomposition

Traditional quantization maps a float to fewer bits (INT8, INT4, …). LittleBit works differently:

**Don't compress numbers. Decompose matrices.**

For a weight matrix **W**, LittleBit decomposes it into a sum of low-rank binary factor matrix products:

```
W ≈ Σ (scale_i × B_i × C_i)
```

Where **B_i** and **C_i** are binary matrices (each element is {+1, −1}), and **scale_i** are FP16 scaling factors (one per row, column, and latent dimension).

Why this helps:
- **Binary matrix multiply = bitwise ops**: {+1, −1} inner products reduce to popcount instructions — no floating-point needed
- **Very few FP16 scale factors**: Relative to the full weight matrix, the scale factors add minimal storage overhead

---

### Two Key Technical Details

**Dual-SVID initialization**: Rather than random initialization, the binary factors are initialized using a QAT-aware SVD variant (Dual Sign-Value-Independent Decomposition) designed to start close to the original weight distribution.

**Residual Compensation**: Binarizing factor matrices introduces approximation error. Residual compensation adds a low-rank correction term to reduce this error. Together they allow training to converge at extreme bit widths.

---

### Results

| Model | BPW | Memory | vs FP16 |
|-------|-----|--------|---------|
| Llama2-13B FP16 | 16 | ~26 GB | baseline |
| **LittleBit Llama2-13B** | **0.1** | **~0.9 GB** | **1/31** |
| **LittleBit Llama2-7B at 0.1 BPW** | **0.1** | — | **beats STBLLM at 0.7 BPW** |

The last row is the paper's headline claim: a model at 0.1 BPW outperforming a competitor that retains 7× more bits.

---

### About the 11.6× Speedup Claim

The paper claims **11.6× inference speedup** vs FP16. A few important caveats:

1. **The number changed between versions**: v1 (May 2025) said ~5×; later versions say 11.6×. No explanation provided.
2. **This is kernel-level theoretical throughput**, not end-to-end benchmark. Memory loading, KV cache, and sampling overhead are not included.
3. **No independent third-party reproduction** found as of this writing.

Realistic expectation: actual end-to-end speedup will be lower than 11.6×, but the ~31× memory reduction is real.

---

### LittleBit-2 (ICML 2026)

The follow-up paper LittleBit-2 is already merged into the same GitHub repo via `--use_itq`. It focuses on **spectral energy gain** and **Latent Geometry Alignment** to further improve the efficiency of the low-rank factorization. If deploying this method, LittleBit-2 is the current state of the art from this group.

---

### TL;DR

LittleBit decomposes weight matrices into low-rank binary factors + minimal FP16 scaling, runs inference with bitwise ops, and achieves ~0.9 GB for a 13B model at 0.1 BPW — outperforming competitors at 7× higher bit widths. Memory compression is real; 11.6× speedup is kernel-level theory, needs discounting. LittleBit-2 is in the same repo.

---

> Paper CC BY-NC-ND 4.0. Samsung Research, Banseok Lee et al., arXiv 2506.13771, NeurIPS 2025. For technical reference only.
