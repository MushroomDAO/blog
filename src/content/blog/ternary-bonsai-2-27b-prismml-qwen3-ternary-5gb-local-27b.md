---
title: "Ternary Bonsai 2 27B：把 27B 模型压进 5.9GB，三值量化怎么做到的"
titleEn: "Ternary Bonsai 2 27B: How PrismML Squeezed a 27B Model Into 5.9GB with Ternary Quantization"
description: "PrismML 发布 Ternary Bonsai 2 27B（Apache 2.0），基于 Qwen3.8-27B 三值量化，每个权重只保留 {-1, 0, +1} 三个状态，PTQ1_0 变体仅 5.95 GB，比同等性能的 Q4_K_XL（17.6 GB）小三倍，比同等体积的 IQ2_XXS 综合得分高 12 分。综合 benchmark 84.78 对比 FP16 的 86.32，性能保留 98.2%。速度：RTX 4090 约 81 tok/s，M5 Max 约 47 tok/s，M5 Pro 约 28 tok/s。关键限制：需要 PrismML 自定义 llama.cpp 分支，标准 LM Studio/Ollama 暂不支持，上游 Issue #29058 仍开放。Mac 用户有 MLX 版本（prism-ml/Ternary-Bonsai-2-27B-mlx-2bit），不受此限制。OpenRouter 已上线，$0.075/M input。"
descriptionEn: "PrismML releases Ternary Bonsai 2 27B (Apache 2.0), a ternary quantization of Qwen3.8-27B where each weight is reduced to {-1, 0, +1}. The PTQ1_0 variant is 5.95 GB — 3× smaller than Q4_K_XL at comparable quality, scoring 12 points higher than IQ2_XXS at smaller size. Overall benchmark: 84.78 vs FP16's 86.32 = 98.2% retention. Speed: RTX 4090 ~81 tok/s, M5 Max ~47 tok/s, M5 Pro ~28 tok/s. Key constraint: requires PrismML's custom llama.cpp fork — stock LM Studio/Ollama don't work yet (upstream Issue #29058 open). Mac users have MLX (prism-ml/Ternary-Bonsai-2-27B-mlx-2bit). Available on OpenRouter at $0.075/M input."
pubDate: 2026-10-08
heroImage: "../../assets/images/ternary-bonsai-2-27b-prismml-qwen3-ternary-5gb-local-27b-banner.jpg"
category: "Tech-Experiment"
tags: ["本地模型", "开源模型", "量化", "Apple Silicon", "AI工具"]
lang: "zh-CN"
wechatTitle: "Ternary Bonsai 2：27B模型压到5.9GB"
wechatDigest: "Apache 2.0；Qwen3.8-27B三值化；5.9GB；比IQ2_XXS高12分；MLX版已发"
---

27B 参数模型，5.9 GB 跑起来。

这不是靠激进降精度做到的——Ternary Bonsai 2 27B 用的方法不一样：把每个权重的数值空间从浮点数压缩到三个整数 **{-1, 0, +1}**。

HuggingFace: https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf | Apache 2.0 | PrismML

---

## 三值量化是什么

传统 2-bit 量化把权重映射到 0/1/2/3 共四个值，而 Ternary 量化只用三个值：{-1, 0, +1}。看起来精度更低，实际上有额外补偿机制：

每 128 个权重共享一个 FP16 缩放因子（scale factor）。核心变换是 **Hadamard 旋转**——在量化之前对权重矩阵做正交变换，把权重分布调整得更均匀，让 {-1, 0, +1} 三个值能够尽量贴近原始浮点值的分布。

结果：权重位宽很低，但信息损失比直接截断要小得多。

---

## 两个 GGUF 变体

| 变体 | 位宽 | 文件大小 | 适用场景 |
|------|------|----------|----------|
| **PTQ1_0**（dense trits） | 1.75 bits/weight | **5.95 GB** | 内存受限，CPU 推理 |
| **PQ2_0**（2-bit slots） | 2.13 bits/weight | **7.21 GB** | GPU 加速，速度更快 |

PTQ1_0 是面积最小的选项，PQ2_0 在 GPU 上跑得更快。

---

## 性能对比：和竞品比

| 模型 | 综合得分 | 文件大小 |
|------|----------|----------|
| Qwen3.8-27B FP16 | 86.32 | 54 GB |
| **Ternary Bonsai 2（PTQ1_0）** | **84.78** | **5.9 GB** |
| Q4_K_XL | 85.18 | 17.6 GB |
| IQ2_XXS | 72.59 | 9.4 GB |

几个值得注意的数字：

- **vs FP16**：损失 1.54 分，体积缩小 9 倍，性能保留 98.2%
- **vs Q4_K_XL**：分数差 0.4 分（几乎打平），体积是它的 1/3
- **vs IQ2_XXS**：比它高 **12 分**，体积还比它小 37%

IQ2_XXS 是当前常用的激进 2-bit 量化方案之一。Bonsai 2 不只是"和它差不多"，而是在更小体积下明显更好。

---

## 速度参考（PQ2_0 变体，tok/s）

| 硬件 | 生成速度 |
|------|----------|
| RTX 5090 | 130 tok/s |
| H100 | 114 tok/s |
| RTX 4090 | 81 tok/s |
| Apple M5 Max | 47 tok/s |
| Apple M5 Pro | 28 tok/s |

M5 Pro 28 tok/s 对话完全够用。RTX 3060 12GB 也有社区测试报告，能跑但速度未公布。

---

## 分类损失：哪里扣分了

量化不均匀——有的任务受影响更大：

| 类别 | 相对 FP16 变化 |
|------|---------------|
| 指令遵循 | **+1.41**（反而更好） |
| 代码生成 | **+0.35** |
| 数学推理 | -0.49 |
| 工具调用 | **-1.82** |

工具调用损失最大（-1.82 分）。如果你的主要用途是 AI Agent / Function Calling，这个数字需要注意。

---

## 基础模型：Qwen3.8-27B 不是简单的 27B

底层是 Qwen3.8-27B（27.36B 参数总计：24.35B LM 主体 + 2.54B 嵌入 + 0.46B 视觉塔）。架构：混合注意力（75% 线性注意力 + 25% 完整注意力），SwiGLU 激活，RoPE 位置编码，RMSNorm，支持 **262K 上下文**。

三值量化在这个架构上量化的是 LM 主体权重，视觉塔通常保持更高精度。

---

## 部署现实：标准工具暂时用不了

⚠️ **LM Studio 和 Ollama 目前无法原生运行这个模型。**

原因：PTQ1_0 和 PQ2_0 是 PrismML 自定义的张量类型（type 142/143），标准 llama.cpp 不认识，也没有 Hadamard 旋转的实现。上游 Issue #29058（"Support Prism PQ2_0 type 142 and PTQ1_0 type 143"）仍处于开放状态。

**可以运行的路径：**

**1. PrismML 自定义 llama.cpp fork**（推荐）
```bash
git clone https://github.com/PrismML-Eng/llama.cpp
cd llama.cpp && cmake -B build && cmake --build build -j
# 然后按 Bonsai-demo 的 README 操作
```
参考仓库：https://github.com/PrismML-Eng/Bonsai-demo

**2. MLX（Mac 专用，无需特殊配置）**
```bash
# 无需自定义工具，标准 mlx-lm 运行
pip install mlx-lm
mlx_lm.generate --model prism-ml/Ternary-Bonsai-2-27B-mlx-2bit \
  --prompt "你好"
```
Mac M 系列用户推荐这条路，正常的 mlx-lm 就能跑。

**3. OpenRouter（不想自己部署）**
模型 ID：`prism-ml/ternary-bonsai-2-27b`，$0.075/M input，$0.50/M output。

---

## WebGPU 版本

PrismML 还发布了一个 WebGPU Kernels HuggingFace Space，理论上可以在支持 WebGPU 的浏览器里直接跑，但社区反馈有在测试 prompt 下循环卡死的问题，稳定性待观察。

---

## 一句话说清楚

Ternary Bonsai 2 27B 把每个权重压成 {-1, 0, +1}，Hadamard 旋转补偿精度损失，5.9GB 保留 98.2% 性能——这是目前在 8-16GB 内存上能跑的质量最好的 27B 量化模型之一。部署门槛：需要 PrismML 自定义 llama.cpp，Mac 用 MLX 无此限制。工具调用场景慎用（-1.82 分损失）。

---

> Apache 2.0 许可。PrismML 2026-09-17 发布，Google v5 TPU 训练。开源仅供学习参考。

---

<!--EN-->

## Ternary Bonsai 2 27B: How PrismML Squeezed a 27B Model Into 5.9GB with Ternary Quantization

A 27B parameter model running in 5.9 GB. Not through aggressive precision reduction — through a different approach: compressing each weight's value space to just three integers: **{-1, 0, +1}**.

HuggingFace: https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf | Apache 2.0 | PrismML

---

### What Ternary Quantization Does

Standard 2-bit quantization maps weights to {0, 1, 2, 3}. Ternary uses only {-1, 0, +1} — seemingly less precision, but with a compensation mechanism: every 128 weights share one FP16 scale factor.

The key transformation is a **Hadamard rotation** — an orthogonal transform applied to the weight matrix before quantization, redistributing weight values so the three-state approximation fits the distribution better.

Result: very low bit-width, but significantly less information loss than naive truncation.

---

### Two GGUF Variants

| Variant | Bit-width | File size | Best for |
|---------|-----------|-----------|---------|
| **PTQ1_0** (dense trits) | 1.75 bits/weight | **5.95 GB** | Memory-constrained, CPU |
| **PQ2_0** (2-bit slots) | 2.13 bits/weight | **7.21 GB** | GPU acceleration |

PTQ1_0 for minimum footprint, PQ2_0 for speed on GPU.

---

### Performance Against Competitors

| Model | Score | Size |
|-------|-------|------|
| Qwen3.8-27B FP16 | 86.32 | 54 GB |
| **Ternary Bonsai 2 (PTQ1_0)** | **84.78** | **5.9 GB** |
| Q4_K_XL | 85.18 | 17.6 GB |
| IQ2_XXS | 72.59 | 9.4 GB |

Key comparisons:
- **vs FP16**: -1.54 points, 9× smaller, 98.2% retained
- **vs Q4_K_XL**: nearly tied (-0.4 pts), at one-third the size
- **vs IQ2_XXS**: **+12 points** with a 37% smaller file

---

### Speed (PQ2_0, tok/s)

| Hardware | Speed |
|----------|-------|
| RTX 5090 | 130 tok/s |
| H100 | 114 tok/s |
| RTX 4090 | 81 tok/s |
| Apple M5 Max | 47 tok/s |
| Apple M5 Pro | 28 tok/s |

M5 Pro at 28 tok/s is comfortable for conversation.

---

### Category-Level Losses

| Category | vs FP16 |
|----------|---------|
| Instruction following | **+1.41** (better) |
| Code generation | **+0.35** |
| Math reasoning | -0.49 |
| Tool calling | **-1.82** |

Tool calling takes the biggest hit (-1.82). Flag this if your use case is AI agent / function calling.

---

### Deployment Reality: Standard Tools Don't Work Yet

⚠️ **LM Studio and Ollama cannot run this model natively.**

PTQ1_0 and PQ2_0 are custom tensor types (type 142/143) that stock llama.cpp doesn't recognize. Upstream Issue #29058 is still open.

**Working paths:**

**1. PrismML's custom llama.cpp fork** (recommended for non-Mac)
```bash
git clone https://github.com/PrismML-Eng/llama.cpp
cd llama.cpp && cmake -B build && cmake --build build -j
# follow Bonsai-demo README
```

**2. MLX (Mac only, works with standard tools)**
```bash
pip install mlx-lm
mlx_lm.generate --model prism-ml/Ternary-Bonsai-2-27B-mlx-2bit \
  --prompt "hello"
```
No custom tooling needed for Mac M-series.

**3. OpenRouter** (no local setup): `prism-ml/ternary-bonsai-2-27b`, $0.075/M input, $0.50/M output.

---

> Apache 2.0 license. Released by PrismML on 2026-09-17, trained on Google v5 TPU. For technical reference only.
