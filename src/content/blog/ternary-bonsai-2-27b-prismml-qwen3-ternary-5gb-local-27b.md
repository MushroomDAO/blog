---
title: "Ternary Bonsai 2-27B：5.9 GB 跑 27B 模型，三值量化保留 98.2% 性能，比标准 2-bit 强 12 分"
titleEn: "Ternary Bonsai 2-27B: 5.9 GB for a 27B Model, Ternary Quantization Retains 98.2% Performance and Beats Standard 2-bit by 12 Points"
description: "PrismML 基于 Qwen3.8-27B 发布 Ternary Bonsai 2-27B，三值量化（1.72 bits/权重），5.9 GB 跑 27B 参数，M5 Max 47 tok/s，RTX 5090 130 tok/s。14 项基准平均 84.78/86.32（98.2% 保留），比 IQ2_XXS 高 12 分而只用 63% 体积。需要 PrismML 自定义 llama.cpp 分支，非标准版可用。Apache 2.0。"
descriptionEn: "PrismML releases Ternary Bonsai 2-27B from Qwen3.8-27B, ternary quantization (1.72 bits/weight), 5.9 GB for 27B parameters, 47 tok/s on M5 Max, 130 tok/s on RTX 5090. 14-benchmark average 84.78/86.32 (98.2% retention), beats IQ2_XXS by 12 points at 63% of the size. Requires PrismML's custom llama.cpp fork. Apache 2.0."
pubDate: "2026-09-18"
updatedDate: "2026-09-18"
category: "Tech-Experiment"
tags: ["open-source", "local-LLM", "quantization", "Qwen3", "ternary", "Apple-Silicon", "inference", "Apache-2.0"]
heroImage: "../../assets/images/ternary-bonsai-2-27b-prismml-qwen3-ternary-5gb-local-27b-banner.jpg"
---

> 📌 HuggingFace (GGUF)：https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf
> HuggingFace (MLX)：https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-mlx-2bit
> License：Apache 2.0 | Base：Qwen3.8-27B

---

把 27B 参数模型压进 5.9 GB，在 16GB 内存的 Mac 上跑，保留 98.2% 的基准性能——这就是 PrismML 的 Ternary Bonsai 2-27B 做的事。

不过要先说清楚：公司名是 **PrismML**（不是 PrimML），量化方法叫"三值化"（ternary），不是普通的 2-bit 量化。两者同样每权重用约 2 个 bit 存储，但三值化的取值集合是 **{−1, 0, +1}**，加上每 128 个权重共享一个 FP16 缩放因子。这个约束在训练时引入，让模型学会在这套表示下保住能力——而不是训练完再硬压。

---

## 量化对比：为什么三值化比标准 2-bit 强？

把 Bonsai 2 放在三个参照点上看：

| 量化方案 | bits/权重 | 文件大小 | 14 项基准均分 |
|----------|----------|---------|--------------|
| Qwen3.8-27B FP16（原版） | 16.0 | ~54 GB | 86.32 |
| UD-Q4_K_XL（标准 4-bit） | 5.2 | 17.6 GB | 85.18 |
| **Ternary Bonsai 2-27B** | **1.72** | **5.9 GB** | **84.78** |
| IQ2_XXS（标准 2-bit） | 2.8 | 9.4 GB | 72.59 |

三值化在 1.72 bits/权重的情况下，均分 84.78——比标准 2-bit（IQ2_XXS）高 12 分以上，而且体积还比后者小 37%。最关键的数字：和 4-bit 量化的差距只有 0.4 分，但体积只要后者的 1/3。

为什么标准 2-bit 这么差？常见的 IQ2_XXS 是事后压缩，强行把权重映射到 2-bit 离散值，高精度权重损失严重。三值化则是在训练过程中让权重学会"只用三个值"，损失分布不同，关键结构信息保留更好。

---

## 分类别性能拆解

整体 98.2% 这个数字背后，分类别有差异：

| 类别 | FP16 | Bonsai 2 | 差值 |
|------|------|---------|------|
| 数学 | 97.06 | 96.57 | −0.49 |
| 代码 | 89.07 | **89.42** | +0.35 |
| 指令遵循 | 81.25 | **82.66** | +1.41 |
| 工具调用（BFCL v3） | 76.74 | 74.92 | **−1.82** |

数学几乎没掉，代码和指令遵循反而略微高于 FP16（基准测试的波动范围内，不用过度解读），工具调用损失最大（−1.82 分）。如果你的主要用途是 agentic 工具链调用，这个差值值得注意。

---

## 硬件实测速度

两个 GGUF 版本，PQ2_0（2.13 bits/权重，7.21 GB）在 GPU 上更快，PTQ1_0（1.75 bits/权重，5.95 GB）在某些场景下更省内存：

| 平台 | PQ2_0 (tok/s) | 内存 |
|------|--------------|------|
| RTX 5090 (32GB) | 129.9 | VRAM 8GB 起 |
| H100 SXM (80GB) | 113.9 | — |
| RTX 4090 (24GB) | 81.2 | — |
| Apple M5 Max | 47.0 | 统一内存 16-24GB |
| Apple M5 Pro | 28.1 | — |

M5 Max 跑 47 tok/s，16-24GB 统一内存，在日常对话里足够用。RTX 4090 到 81 tok/s，5090 接近 130 tok/s。

---

## 安装：必须用 PrismML 自定义 llama.cpp

这是目前最大的使用门槛：Ternary Bonsai 2 需要 PrismML 的自定义 llama.cpp 分支，标准 llama.cpp 不兼容（ternary 权重格式还没合并进上游）。

**CUDA（Windows/Linux）**：
```bash
git clone https://github.com/PrismML-Eng/llama.cpp
cmake -B build -DGGML_CUDA=ON && cmake --build build -j
# 下载 GGUF
huggingface-cli download prism-ml/Ternary-Bonsai-2-27B-gguf \
  Ternary-Bonsai-2-27B-PQ2_0.gguf --local-dir .
# 推理
./build/bin/llama-cli -m Ternary-Bonsai-2-27B-PQ2_0.gguf \
  -ngl 99 -fa on --temp 1.0 --top-p 0.95 --top-k 20 -n 256
```

**Metal（macOS）**：
```bash
cmake -B build && cmake --build build -j
./build/bin/llama-cli -m Ternary-Bonsai-2-27B-PQ2_0.gguf \
  -ngl 99 --temp 1.0 --top-p 0.95 --top-k 20 -n 256
```

LM Studio、Jan、Ollama 目前也在路线图上（需要等各工具集成 PrismML 的 ternary 格式），MLX 版本已经单独发布：`prism-ml/Ternary-Bonsai-2-27B-mlx-2bit`。

**生成参数建议**：
- 思考模式（推理/数学）：temperature=1.0，top_p=0.95，top_k=20
- 指令模式（对话/写作）：temperature=0.7，top_p=0.80，top_k=20

---

## 模型规格

- **基础模型**：Qwen3.8-27B（27.36B 参数：24.35B LM 主体 + 2.54B 嵌入/LM head + 0.46B 视觉塔）
- **架构**：混合注意力（~75% 线性注意力 + ~25% 完整注意力），SwiGLU MLP，RoPE，RMSNorm
- **上下文长度**：262K tokens
- **多模态**：内置视觉塔（加载额外 0.63 GB，仅处理图像时才激活）
- **训练硬件**：Google v5 TPU

---

## 需要注意的地方

**自定义分支依赖**：目前必须用 PrismML 的 llama.cpp 分支，ternary 格式还没有合并进上游。等等看会不会有社区集成，现在上手有一定工程成本。

**98.2% 是平均值**：工具调用损失 1.82 分，agentic 场景的实际差距可能更明显。如果你的工作流重度依赖工具链，建议先测试后决定。

**与其他模型的比较**：PrismML 在发布材料里列出了与若干商业模型的对比，这些数字取自特定基准子集，不代表所有任务。建议用自己的实际用例测试，而不是完全依赖发布材料里的排名。

---

## 总结

Ternary Bonsai 2-27B 的核心价值主张：**在 5.9 GB / 16GB 内存的约束下，实现接近 4-bit 量化的质量，同时保持 2-bit 的体积**。这个位置是真实的——标准 IQ2_XXS 在这个压缩比下质量大幅下滑，而 Bonsai 2 通过训练时三值化把损失控制在 1.82 分以内（工具调用）到可忽略（数学/代码）。

对 16GB Mac 或单张消费级 GPU 的用户来说，这是目前在这个体积段内能找到的最强 27B 推理选项。门槛是需要一个自定义 llama.cpp 分支，等主流工具集成后会更容易用。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 HuggingFace (GGUF): https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf
> HuggingFace (MLX): https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-mlx-2bit
> License: Apache 2.0 | Base: Qwen3.8-27B

---

Squeeze a 27B-parameter model into 5.9 GB, run it on a Mac with 16 GB memory, and retain 98.2% of benchmark performance. That's what PrismML's Ternary Bonsai 2-27B does.

First, a clarification: the company is **PrismML**, the method is **ternary quantization** — not ordinary 2-bit quantization. Both use roughly 2 bits per weight for storage, but ternary constrains each weight to {−1, 0, +1} plus one FP16 scale factor per group of 128 weights. This constraint is applied during training, not imposed afterward — the model learns to perform within this representation rather than being crushed into it post-hoc.

---

## Why Ternary Beats Standard 2-bit

Put Bonsai 2 alongside three reference points:

| Quantization | bits/weight | File Size | 14-Benchmark Average |
|-------------|------------|---------|---------------------|
| Qwen3.8-27B FP16 (full) | 16.0 | ~54 GB | 86.32 |
| UD-Q4_K_XL (standard 4-bit) | 5.2 | 17.6 GB | 85.18 |
| **Ternary Bonsai 2-27B** | **1.72** | **5.9 GB** | **84.78** |
| IQ2_XXS (standard 2-bit) | 2.8 | 9.4 GB | 72.59 |

At 1.72 bits/weight, Bonsai 2 scores 84.78 — 12+ points ahead of standard 2-bit (IQ2_XXS), at 63% of the size. The most important number: the gap versus 4-bit quantization is just 0.4 points, at one-third the file size.

Why does standard 2-bit perform so poorly? Methods like IQ2_XXS compress after training, forcing weights into 2-bit discrete values and losing high-precision structure. Ternary quantization trains the model to only use three values from the start — the distribution of losses is different, and structurally important weight patterns survive better.

---

## Per-Category Breakdown

The aggregate 98.2% masks category-level variance:

| Category | FP16 | Bonsai 2 | Delta |
|----------|------|---------|-------|
| Math | 97.06 | 96.57 | −0.49 |
| Coding | 89.07 | **89.42** | +0.35 |
| Instruction following | 81.25 | **82.66** | +1.41 |
| Tool calling (BFCL v3) | 76.74 | 74.92 | **−1.82** |

Math is nearly unchanged. Coding and instruction following are slightly higher than FP16 (within benchmark variance — don't over-read this). Tool calling has the most meaningful loss (−1.82 points). If your workflow depends heavily on agentic tool chains, that's the number to watch.

---

## Hardware Speed

Two GGUF variants: PQ2_0 (2.13 bits/weight, 7.21 GB) is faster on GPU; PTQ1_0 (1.75 bits/weight, 5.95 GB) has a smaller footprint.

| Platform | PQ2_0 (tok/s) | Memory |
|----------|--------------|--------|
| RTX 5090 (32GB) | 129.9 | 8+ GB VRAM |
| H100 SXM (80GB) | 113.9 | — |
| RTX 4090 (24GB) | 81.2 | — |
| Apple M5 Max | 47.0 | 16-24 GB unified |
| Apple M5 Pro | 28.1 | — |

47 tok/s on M5 Max with 16-24 GB unified memory is comfortable for conversation. RTX 4090 reaches 81 tok/s; the 5090 is close to 130 tok/s.

---

## Installation: Custom llama.cpp Required

The main friction point right now: Ternary Bonsai 2 requires PrismML's custom llama.cpp fork — standard llama.cpp doesn't support the ternary weight format yet (upstream merge is pending).

**CUDA (Windows/Linux):**
```bash
git clone https://github.com/PrismML-Eng/llama.cpp
cmake -B build -DGGML_CUDA=ON && cmake --build build -j
huggingface-cli download prism-ml/Ternary-Bonsai-2-27B-gguf \
  Ternary-Bonsai-2-27B-PQ2_0.gguf --local-dir .
./build/bin/llama-cli -m Ternary-Bonsai-2-27B-PQ2_0.gguf \
  -ngl 99 -fa on --temp 1.0 --top-p 0.95 --top-k 20 -n 256
```

**Metal (macOS):**
```bash
cmake -B build && cmake --build build -j
./build/bin/llama-cli -m Ternary-Bonsai-2-27B-PQ2_0.gguf \
  -ngl 99 --temp 1.0 --top-p 0.95 --top-k 20 -n 256
```

An MLX variant is already published (`prism-ml/Ternary-Bonsai-2-27B-mlx-2bit`). LM Studio, Jan, and Ollama support is on the roadmap pending integration of PrismML's ternary format.

**Recommended generation parameters:**
- Thinking mode (reasoning/math): temperature=1.0, top_p=0.95, top_k=20
- Instruct mode (conversation/writing): temperature=0.7, top_p=0.80, top_k=20

---

## Model Specs

- **Base**: Qwen3.8-27B (27.36B params: 24.35B LM backbone + 2.54B embedding/LM head + 0.46B vision tower)
- **Architecture**: Hybrid attention (~75% linear + ~25% full), SwiGLU MLP, RoPE, RMSNorm
- **Context**: 262K tokens
- **Multimodal**: Vision tower included (+0.63 GB, loaded only when processing images)
- **Training hardware**: Google v5 TPUs

---

## Caveats

**Custom fork dependency**: The ternary format isn't merged upstream yet. There's some engineering overhead to build from the fork until mainstream tools integrate it.

**98.2% is an average**: Tool calling drops 1.82 points. For heavy agentic workloads, test on your actual tasks before committing.

**Model comparisons in the release**: PrismML's marketing compares against specific commercial models on specific benchmarks. Treat these numbers as directional — run your own evaluation on your use case.

---

## Summary

Ternary Bonsai 2-27B's core claim is real: **5.9 GB at near-4-bit quality, with 2-bit file size.** Standard IQ2_XXS at this compression level loses 14 points of benchmark quality; Bonsai 2 holds the loss to under 2 points (on tool calling) and nearly zero on math and coding.

For users on a 16 GB Mac or a single consumer GPU, this is the strongest 27B inference option available at this footprint right now. The friction is a custom llama.cpp fork — once mainstream tooling catches up, the on-ramp will be much smoother.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
