---
title: "Block3D：浙大 ZIP Lab 开源文本生成 3D，分块扩散实现 5.15× 加速"
titleEn: "block3d-zhejiang-text-to-3d-block-wise-diffusion-efficient"
description: "浙江大学 ZIP Lab 联合莫纳什大学开源 Block3D——一个分块扩散框架，将离散形状 token 序列按块分组，块间自回归保证因果结构，块内所有 token 并行去噪，并引入置信度引导的块内修正机制。与微调自回归基线相比，端到端生成时间从 25.71 秒降至 4.99 秒（5.15 倍加速），几何保真度不降。论文：arXiv 2608.19567。"
descriptionEn: "Zhejiang University's ZIP Lab and Monash University open-source Block3D — a block-wise diffusion framework for text-to-3D. Divides discrete shape tokens into contiguous blocks, generates autoregressively across blocks, denoises all tokens within each block in parallel, and applies confidence-guided intra-block correction. End-to-end generation: 25.71s → 4.99s (5.15× speedup) without sacrificing geometric fidelity. arXiv 2608.19567."
pubDate: "2026-08-25"
updatedDate: "2026-08-25"
category: "Research"
tags: ["开源", "文本生成3D", "扩散模型", "浙大", "ZIP Lab", "Block3D", "3D生成", "加速推理"]
heroImage: "../../assets/images/block3d-zhejiang-text-to-3d-block-wise-diffusion-efficient-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：ziplab/Block3D ⭐ 21 | License: RAIL-MS（仅限研究）  
机构：浙江大学 ZIP Lab · 莫纳什大学 · 阿德莱德大学  
论文：arXiv 2608.19567  
项目页面：https://alexandertsui.github.io/block3d/  
发布：2026-08-24

---

## 问题是什么

文本生成 3D 目前面临一个两难困境：

**自回归方法**（逐 token 生成离散形状序列）：速度慢，一个 1,024 token 的形状序列要顺序生成每一个 token；且无法回头修正错误——提交的 token 就是最终结果。

**扩散/流匹配方法**（迭代精化全局 3D 表示）：每一步都要处理完整的全局表示，计算代价随序列长度线性上升。

Block3D 的思路是：**把两种方法的优点组合起来**。

---

## Block3D 怎么做

核心是**分块扩散（Block-Wise Diffusion）**，四个步骤：

**① 分块（Partition）**  
将 1,024 个离散形状 token 组成的序列切成若干连续的块（contiguous blocks）。

**② 块内并行去噪（Denoise）**  
块间仍然是自回归顺序（左到右），保留因果结构。但在当前活跃块内，**所有 token 同时并行去噪**——从而绕开逐 token 串行的瓶颈。

**③ 置信度引导修正（Correct）**  
提交块之前，对低置信度的 token 进行修正（intra-block correction）。这解决了纯自回归方法无法回头修改的缺陷。具体机制：Mask-to-Token 恢复（M2T）+ Token-to-Token 修正（T2T）联合更新当前块。

**④ 块提交（Commit）**  
修正完成后，块被提交并缓存，进入下一块。所有块处理完毕后，冻结的 Cube 形状解码器将完整序列转换为输出网格。

```
文本 prompt
  → 冻结 Cube 形状编码器 + 文本编码器 → 条件序列
  → Block3D 逐块生成（块间 AR，块内并行去噪 + 修正）
  → 冻结 Cube 形状解码器
  → 输出 .obj 网格
```

---

## 核心结果

在 TRELLIS-500K 的 100 对象固定评估集上，与微调自回归基线对比：

| 指标 | AR 基线 | Block3D（M2T + T2T） |
|------|---------|----------------------|
| 端到端延迟 | 25.71 s | **4.99 s** |
| 加速比 | 1× | **5.15×** |
| CD-L1（越低越好） | — | 0.0775 |
| 法向一致性（NC） | — | 0.6676 |
| F-score @ 1% | — | **0.309** |
| F-score @ 2% | — | 0.551 |

5.15× 加速，几何保真度不降，在单张 A100 80GB 上实现。

**消融对比**（M2T alone vs M2T+T2T）：
- 加上 Token-to-Token 修正后，CD-L1 从 0.0813 降到 0.0775，F@1% 从 0.287 提升到 0.309——修正机制有效。

---

## 技术选型背景

Block3D 构建在 **Cube**（一个已发布的形状 tokenizer + decoder + GPT backbone）之上，训练数据使用 **TRELLIS-500K**（50 万配对文本-网格），语言去噪部分使用 **LLaDA2.1**。

这让 Block3D 能专注于生成效率的架构创新，而不是从头搭整个 3D 生成管线。

训练配置：4× A100 80GB，35K 优化器步，全局 batch size 40，bfloat16，AdamW，lr=1e-4。

---

## 快速试用

```bash
# 安装
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 推理（生成一把木椅）
python -m block3d.generate \
  --config-path block3d/configs/block3d.yaml \
  --gpt-ckpt-path runs/block3d/checkpoints/gpt_final.safetensors \
  --shape-ckpt-path model_weights/shape_tokenizer.safetensors \
  --prompt "a wooden chair" \
  --output-dir outputs/chair \
  --num-diffusion-steps 4 \
  --guidance-scale 3.0 \
  --sampling-strategy block3d
```

输出：`outputs/chair/output.obj`

训练需要 TRELLIS-500K 数据集（数据不含在仓库内，需单独获取）。评估脚本支持几何指标（CD-L1、NC、F-score）和 8 视角 CLIPScore。

---

## 注意：许可证为研究专用

Block3D 采用 **RAIL-MS 研究专用许可证**，不开放商业使用。使用前请仔细阅读 LICENSE 文件。Block3D 是基于 Cube3D-v0.1 及其发布权重的衍生作品。

---

## 为什么重要

文本生成 3D 的工程瓶颈一直是推理速度。25 秒生成一个网格，在实时预览、游戏资产批量生成、设计迭代等场景里都是不可接受的延迟。

Block3D 提出的分块扩散不是一个工程技巧，而是对"自回归 vs 扩散"二元对立的直接回应：**块间保持序列因果性（准确），块内并行处理（快），加上修正机制（可修错）**。5.15 倍加速的背后是架构层的机制重组，而非蒸馏或量化带来的近似加速。

---

**相关链接**

- GitHub（代码）：https://github.com/ziplab/Block3D
- 论文页（demo + 演示）：https://alexandertsui.github.io/block3d/
- arXiv：https://arxiv.org/abs/2608.19567
- 联系：wangweijie@zju.edu.cn（浙大 ZIP Lab）

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Block3D: Zhejiang University's Open-Source Text-to-3D, 5.15× Faster via Block-Wise Diffusion

*by Mycelium Protocol*

---

GitHub: ziplab/Block3D ⭐ 21 | License: RAIL-MS (research only)  
Institution: ZIP Lab, Zhejiang University · Monash University · University of Adelaide  
Paper: arXiv 2608.19567  
Project page: https://alexandertsui.github.io/block3d/  
Released: 2026-08-24

---

### The Problem

Text-to-3D generation faces a genuine dilemma:

**Autoregressive methods** (generating discrete shape tokens one by one): slow — a 1,024-token sequence generates sequentially. No error correction — committed tokens are final.

**Diffusion/flow-matching methods** (iteratively refining global 3D representations): every step processes the full global representation; compute scales with sequence length.

Block3D's answer: **combine the strengths of both**.

---

### How It Works

The core mechanism is **block-wise diffusion** in four steps:

**① Partition** — Divide the 1,024 discrete shape tokens into contiguous blocks.

**② Denoise** — Blocks are generated autoregressively left-to-right (preserving causal structure). But within each active block, **all tokens are denoised jointly in parallel** — bypassing the sequential token-by-token bottleneck.

**③ Correct** — Before committing a block, confidence-guided intra-block correction revises low-confidence tokens. This fixes the core flaw of pure autoregression. Mechanism: Mask-to-Token recovery (M2T) + Token-to-Token correction (T2T) jointly update the active block.

**④ Commit** — The corrected block is committed and cached. Repeat for the next block. When the full sequence is complete, the frozen Cube shape decoder converts it to an output mesh.

```
text prompt
  → frozen Cube shape encoder + text encoder → condition sequence
  → Block3D: block-by-block (AR across blocks, parallel denoise + correct within each)
  → frozen Cube shape decoder
  → output .obj mesh
```

---

### Core Results

On the fixed 100-object evaluation set from TRELLIS-500K, vs. fine-tuned autoregressive baseline:

| Metric | AR baseline | Block3D (M2T + T2T) |
|--------|------------|----------------------|
| End-to-end latency | 25.71 s | **4.99 s** |
| Speedup | 1× | **5.15×** |
| CD-L1 (lower is better) | — | 0.0775 |
| Normal Consistency | — | 0.6676 |
| F-score @ 1% | — | **0.309** |
| F-score @ 2% | — | 0.551 |

5.15× speedup with no degradation in geometric fidelity. Single A100 80GB.

**Ablation (M2T only vs M2T + T2T):** Adding Token-to-Token correction drops CD-L1 from 0.0813 to 0.0775 and raises F@1% from 0.287 to 0.309. The correction mechanism is earning its keep.

---

### Technical Context

Block3D builds on **Cube** (a released shape tokenizer + decoder + GPT backbone), trains on **TRELLIS-500K** (500K text-mesh pairs), and uses **LLaDA2.1** for language denoising. This lets the paper focus purely on the generation efficiency architecture rather than building the full 3D pipeline from scratch.

Training: 4× A100 80GB, 35K optimizer steps, global batch size 40, bfloat16, AdamW, lr=1e-4.

---

### Quick Start

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Generate a wooden chair
python -m block3d.generate \
  --config-path block3d/configs/block3d.yaml \
  --gpt-ckpt-path runs/block3d/checkpoints/gpt_final.safetensors \
  --shape-ckpt-path model_weights/shape_tokenizer.safetensors \
  --prompt "a wooden chair" \
  --output-dir outputs/chair \
  --num-diffusion-steps 4 \
  --guidance-scale 3.0 \
  --sampling-strategy block3d
```

Output: `outputs/chair/output.obj`

Training requires the TRELLIS-500K dataset (not included; must be obtained separately). The evaluation script supports geometric metrics (CD-L1, NC, F-score) and 8-view CLIPScore.

---

### License Note

Block3D uses the **RAIL-MS research-only license**. Commercial use is not permitted. It is a derivative work based on Cube3D-v0.1 and its released weights — review the LICENSE file before use.

---

### Why It Matters

Inference speed is the core engineering bottleneck in text-to-3D. A 25-second generation time is unacceptable for real-time preview, batch game asset generation, or design iteration.

Block3D's block-wise diffusion isn't a trick — it's a direct architectural response to the "autoregression vs. diffusion" dichotomy: **causal ordering across blocks (accurate), parallel processing within blocks (fast), correction before commit (recoverable)**. The 5.15× speedup comes from restructuring the mechanism, not approximation via distillation or quantization.

---

**Links**

- GitHub (code): https://github.com/ziplab/Block3D
- Project page (demo + video): https://alexandertsui.github.io/block3d/
- arXiv: https://arxiv.org/abs/2608.19567
- Contact: wangweijie@zju.edu.cn (ZIP Lab, Zhejiang University)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
