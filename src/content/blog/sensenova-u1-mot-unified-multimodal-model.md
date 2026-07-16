---
title: "SenseNova-U1：商汤把理解和生成塞进同一个模型，NEO-unify 架构解析"
titleEn: "SenseNova-U1: SenseTime Unifies Visual Understanding and Generation in One Model — NEO-unify Architecture Explained"
description: "商汤科技开源 SenseNova-U1 系列，包括 8B-MoT 和 A3B-MoT（30B-A3B MoE）两个变体，用 NEO-unify 架构彻底去掉视觉编码器和 VAE，让视觉理解和生成共享同一套 Transformer 权重，在理解和生成双轨 benchmark 上达到开源最优。"
descriptionEn: "SenseTime open-sources SenseNova-U1, including 8B-MoT and 30B-A3B-MoT (MoE) variants. NEO-unify eliminates the visual encoder and VAE entirely, unifying visual understanding and generation in a single Transformer. Reaches open-source state-of-the-art on both understanding and generation benchmarks."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["AI", "多模态", "SenseTime", "商汤", "视觉模型", "开源", "NEO-unify", "MoT"]
heroImage: "../../assets/images/sensenova-u1-mot-unified-model-banner.jpg"
---

> **GitHub**：[OpenSenseNova/SenseNova-U1](https://github.com/OpenSenseNova/SenseNova-U1) · Apache 2.0  
> **论文**：arXiv:2605.12500  
> **HuggingFace**：[sensenova/SenseNova-U1](https://huggingface.co/collections/sensenova/sensenova-u1)  
> **在线 Demo**：https://unify.light-ai.top/

---

## 问题的起点：理解和生成为什么通常是两个模型

过去几年，多模态 AI 形成了一个默认的分工格局：

- **理解模型**（CLIP、LLaVA、Qwen-VL）：视觉编码器（ViT）把图像压缩成特征，接 LLM 做理解/推理
- **生成模型**（SDXL、FLUX、Wan）：VAE 把图像压缩成 latent，Diffusion 模型负责生成

两条线各自成熟，但代价是**理解和生成是两套权重、两套参数、两套推理路径**。如果你想做"看图 → 推理 → 生图"这类需要两种能力交织的任务，要么串联两个模型，要么在同一个模型里同时训练两个能力——后者极其困难。

SenseNova-U1 选择了后者，并且提出了一个全新的架构思路来解决这个问题。

---

## NEO-unify：去掉中间层，直接像素-词元对齐

NEO-unify 的核心思想用一句话说：**去掉视觉编码器（ViT）和变分自编码器（VAE），让像素和词元直接对齐，共享同一套 Transformer 权重。**

传统架构：
```
图像 → [视觉编码器 ViT] → 特征向量 → LLM → 文字输出
                                              ↑
                     [VAE 编码] → latent → 扩散模型 → 图像输出
```

NEO-unify 架构：
```
图像/文字 ──────────────────────────────────────────────────→ 统一 Transformer
           ↑ 像素-词元直接融合，无独立编码器                              │
           └──────────────────────────────────────────────────←
                                                        文字输出 / 图像输出
```

去掉中间层的好处：
1. **无模态冲突**：不存在"视觉特征"和"语言 token"之间的对齐损失
2. **像素级保真**：VAE 压缩会引入图像细节损失，直接处理像素则保留了更高的视觉精度
3. **真正统一**：同一套权重既做理解又做生成，迁移学习效果更好

**MoT（Mixture of Tasks）**是 NEO-unify 的关键机制：通过原生 MoT 在不同任务间高效调度注意力，减少任务间的计算冲突，这是模型能在理解和生成两个方向都不退化的核心原因。

---

## 两个主要模型变体

| 模型 | 参数 | 架构 | 特点 |
|---|---|---|---|
| SenseNova-U1-8B-MoT | 8B 密集 | Transformer + MoT | 全参数，高质量 |
| SenseNova-U1-A3B-MoT | 30B 总参 / 3B 激活 | MoE + MoT | 推理成本低，适合部署 |

A3B 变体是典型的 MoE 策略：30B 总参数保证了模型容量，每次推理只激活 3B，实际 VRAM 需求和 3B 模型相当。

---

## 核心能力

### 多模态理解

- 视觉问答（VQA）
- 图像描述和分析
- 文档 OCR 和表格理解
- 复杂场景推理

### 多模态生成

- 文本到图像（T2I）
- **信息图（Infographic）生成**：这是 SenseNova-U1 的特色能力，专门优化了密集文字排版、复杂布局生成
- 交错图文（Interleaved）生成：一次生成包含多图和说明文字的内容

### 图像编辑

最新版本 `SenseNova-U1-8B-MoT-Infographic-V3`（2026-07-16 发布）：
- 保留 T2I 能力的同时，大幅增强信息图编辑
- 支持局部文字内容编辑
- 支持全局风格编辑
- 支持全局布局编辑

---

## 低 VRAM 推理方案

SenseNova-U1 提供多种低显存运行方案：

**GGUF 量化版本**（8B 模型）：
```bash
# 社区量化版本，感谢 @smthemex
# https://huggingface.co/smthem/SenseNova-U1-8B-MoT-Merger-gguf
```

**层卸载模式**：
```python
# 不同 VRAM 档位的运行模式
# 8GB VRAM：仅推理，使用 layer offload
# 16GB VRAM：正常推理
# 24GB+ VRAM：完整能力
```

**8 步推理蒸馏版**（`8B-MoT-8step-preview`）：
```python
# 8步推理，速度提升约 4× vs 标准 NFE
pipeline(..., cfg_scale=1.0, num_steps=8)
```

---

## 训练代码开源

`2026-05-21` 开源了完整的全参数微调训练代码：

```bash
git clone https://github.com/OpenSenseNova/SenseNova-U1.git
cd SenseNova-U1/training
# 详见 training/README.md
```

这意味着可以基于 SenseNova-U1 微调自定义的理解/生成能力——比如特定行业的视觉 QA、特定风格的 infographic 生成。

---

## 快速推理

```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("sensenova/SenseNova-U1-8B-MoT")
tokenizer = AutoTokenizer.from_pretrained("sensenova/SenseNova-U1-8B-MoT")

# 视觉理解
response = model.chat(
    tokenizer,
    query="这张图片里有什么？",
    image="path/to/image.jpg"
)

# 图像生成
image = model.generate_image(
    prompt="一份现代风格的产品发布会信息图，包含3个核心数据",
    num_steps=20
)
```

---

## 和同类模型的对比定位

| 能力 | SenseNova-U1 | GPT-4o | Gemini 1.5 | LLaVA/Qwen-VL |
|---|---|---|---|---|
| 视觉理解 | ✅ 开源 SoTA | ✅ | ✅ | ✅ |
| 图像生成 | ✅ 同一模型 | ✅（DALL-E 集成） | 有限 | ❌ |
| 信息图生成 | ✅ 专优化 | 一般 | 一般 | ❌ |
| 可微调 | ✅ 训练代码开源 | ❌ | ❌ | ✅ |
| 本地部署 | ✅ | ❌ | ❌ | ✅ |

SenseNova-U1 的差异化在于：**理解和生成真正统一在一个模型里**，加上 Infographic 专项优化，这在开源生态里是稀缺的。

---

## 为什么这个架构方向值得关注

NEO-unify 代表的不只是一个产品，而是一个架构假设：**把视觉编码器和 VAE 都干掉，直接做像素-词元的端到端统一，是可行的且效果更好。**

如果这个假设成立并在更多工作中被验证，未来的多模态模型架构会简化很多——一个模型、一套权重、一次推理，覆盖理解、生成、编辑的完整闭环。

商汤选择把这套研究开源（Apache 2.0），包括训练代码，是这个方向能被学界和工业界更快验证的重要一步。

© 2026 Author: Mycelium Protocol

<!--EN-->

## SenseNova-U1: SenseTime Unifies Visual Understanding and Generation in One Model

**GitHub**: [OpenSenseNova/SenseNova-U1](https://github.com/OpenSenseNova/SenseNova-U1) · Apache 2.0  
**Paper**: arXiv:2605.12500  
**HuggingFace**: [sensenova/SenseNova-U1](https://huggingface.co/collections/sensenova/sensenova-u1)

### The Core Problem

Multimodal AI has historically split into two lineages: understanding models (ViT + LLM) and generation models (VAE + Diffusion). Both are mature, but they're separate pipelines with separate weights. Tasks requiring interleaved understanding and generation require chaining two models — expensive and architecturally awkward.

SenseNova-U1 proposes a different path: eliminate both the Visual Encoder (ViT) and the Variational Auto-Encoder (VAE), and build a single Transformer that processes pixel and word information natively in a unified compound.

### NEO-unify Architecture

Traditional pipeline:
```
Image → [ViT encoder] → feature vectors → LLM → text output
                                                ↑
                [VAE encode] → latent → Diffusion → image output
```

NEO-unify:
```
Image/Text ──→ Unified Transformer → Text output / Image output
              (pixel-word compound, no separate encoder)
```

Benefits:
- No modality alignment loss between "visual features" and "language tokens"
- Pixel-level fidelity preserved (no VAE compression artifacts)
- Same weights for understanding and generation → better transfer learning

**MoT (Mixture of Tasks)** is the key mechanism that enables efficient multi-task routing without task interference — critical for maintaining quality on both understanding and generation tasks simultaneously.

### Models

| Model | Params | Architecture |
|---|---|---|
| SenseNova-U1-8B-MoT | 8B dense | Transformer + MoT |
| SenseNova-U1-A3B-MoT | 30B total / 3B active | MoE + MoT |

The A3B variant uses MoE to activate only 3B parameters per inference while maintaining 30B total capacity — practical VRAM requirements similar to a 3B dense model.

### Key Capabilities

- Visual understanding: VQA, image captioning, OCR, table understanding
- Image generation: T2I with strong infographic/dense-layout specialization
- Interleaved generation: produce documents containing mixed text + images
- Image editing: localized text/content edits, global style/layout edits (V3 model)

### Low-VRAM Options

- GGUF quantized weights available (community-contributed)
- Layer offload modes for 8GB VRAM inference
- 8-step distilled model (`cfg_scale=1.0, num_steps=8`) for ~4× speedup

### Full Training Code Open-Sourced

```bash
git clone https://github.com/OpenSenseNova/SenseNova-U1.git
cd SenseNova-U1/training
# See training/README.md
```

Apache 2.0 license — fine-tunable for domain-specific understanding/generation.

### Why the Architecture Matters

NEO-unify tests a fundamental assumption: eliminating both ViT and VAE and doing end-to-end pixel-word unification is viable and produces better results than adapter-based approaches. If this holds at scale and in follow-on work, future multimodal architectures will converge toward this simpler paradigm — one model, one set of weights, one inference pass for the full understanding-generation loop.

© 2026 Author: Mycelium Protocol
