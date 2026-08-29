---
title: "FastVideo：统一的视频生成推理与后训练框架，5秒视频 1.8 秒出图"
titleEn: "FastVideo: Unified Video Generation Inference & Post-Training Framework — 5s Video in 1.8s"
description: "hao-ai-lab 开源 FastVideo，端到端统一视频生成框架，稀疏蒸馏实现 >50× 去噪加速，支持 Apple Silicon MLX、H100/A100/4090，全平台覆盖。"
descriptionEn: "hao-ai-lab's FastVideo unifies inference and post-training for accelerated video generation, achieving >50× denoising speedup via sparse distillation, supporting Apple Silicon MLX and NVIDIA H100/A100/4090."
pubDate: 2026-08-29
updatedDate: 2026-08-29
category: "Tech-News"
tags: ["video generation", "AI", "open source", "inference", "post-training", "MLX", "Apple Silicon", "diffusion"]
heroImage: "/assets/images/fastvideo-hao-ai-lab-unified-video-generation-inference-training-banner.jpg"
author: "Mycelium Protocol"
---

## 视频生成进入"实时"时代

视频生成领域在过去一年经历了爆炸式增长，但大多数开源框架要么只管推理、要么只管训练，切换模型或做定制微调需要东拼西凑多个工具链。**FastVideo** 是 [hao-ai-lab](https://github.com/hao-ai-lab/FastVideo) 推出的统一框架，把推理加速、后训练（微调/蒸馏）和实时生成集成在同一个代码库里，目前已获 ⭐4,100+。

最新数据点：**FastWan-QAD 可在 1.8 秒内生成 5 秒视频**，FastH3 Preview v0.2 还支持同步生成视频和音频。

---

## 核心技术亮点

### 1. 稀疏蒸馏（Sparse Distillation）→ >50× 去噪加速

FastVideo 引入了 **Video Sparse Attention（VSA，arXiv:2505.13389）**，结合 Distribution Matching Distillation（DMD2）把多步扩散蒸馏为少步推理，最终实现去噪步骤 >50× 的速度提升。关键模型：

| 模型 | 尺寸 | 速度 |
|---|---|---|
| FastWan-QAD-FP8-1.3B | 1.3B | 5s 视频 ≈ 1.8s E2E |
| FastWan2.2-TI2V-5B | 5B | 720P 文本+图像转视频 |
| FastH3 Preview v0.2 | MiniMax-H3 | 4 步 DMD2，视频+音频同步 |
| FastMetal-QAD（Apple Silicon） | 1.3B/5B/14B | 本地 Mac 运行 |

### 2. 全平台硬件覆盖

- **NVIDIA**：H100、A100、4090，支持 CUDA 12/13，FP8 量化
- **Apple Silicon**：M1/M2/M3/M4 通过 MLX 运行 FastMetal-QAD，3 种参数规格（1.3B→14B）
- **DGX Spark**（ARM64 + CUDA 13）：提供专属安装指南
- **OS**：Linux、Windows、macOS 全覆盖

### 3. 后训练工具链（Post-Training）

FastVideo 不只是推理库，它覆盖从数据到部署的完整训练链路：

- **全量微调 + LoRA 微调**：支持主流开源视频 DiT
- **数据预处理流水线**：视频、图像、文本多模态数据
- **Sparse Distillation 配方**：开箱即用的蒸馏 Recipe + 合成数据集
- **分布式训练**：FSDP2、序列并行（Sequence Parallelism）、选择性激活检查点
- **Self-Forcing 因果蒸馏**：支持自回归模型的流式生成

### 4. Dreamverse — 实时"氛围导演"

[Dreamverse](https://dreamverse.fastvideo.org/) 是 FastVideo 内置的实时视频生成与编辑平台，允许用户在视频流式生成的同时进行交互调整（"vibe directing"），支持本地 GPU、B200 自托管服务器、Docker 和 Modal Serverless 部署。

---

## 快速上手（5 分钟跑起来）

### 安装

```bash
# 推荐使用 uv 创建干净环境
uv venv --python 3.12 --seed
source .venv/bin/activate

# NVIDIA CUDA 12
UV_TORCH_BACKEND=cu126 uv pip install fastvideo

# Apple Silicon Mac
uv pip install -e '.[mlx]'
```

### 第一个视频（Python API）

```python
import os
from fastvideo import VideoGenerator

os.environ["FASTVIDEO_ATTENTION_BACKEND"] = "VIDEO_SPARSE_ATTN"

generator = VideoGenerator.from_pretrained(
    "FastVideo/FastWan2.1-T2V-1.3B-Diffusers",
    num_gpus=1,
)

video = generator.generate_video(
    "A curious raccoon peers through a vibrant field of yellow sunflowers.",
    output_path="my_videos/",
    save_video=True,
)
```

### Apple Silicon 用户

```bash
# 下载 1.3B 量化模型
mdt download FastVideo/FastMetal-1.3B-QAD

# 参考官方 MPS 安装指南
# https://hao-ai-lab.github.io/FastVideo/getting_started/installation/mps/
```

---

## 企业与组织落地建议

### 场景 1：视频内容批量生产

使用 FastWan-QAD-FP8-1.3B + 序列并行，在单台 A100 服务器上实现近实时批量生成。配合 FastVideo 的数据预处理流水线，可以构建从文案→视频的全自动流水线。

### 场景 2：品牌视频微调

利用 LoRA 微调在少量品牌素材上训练，让模型学习特定的视觉风格（色调、构图、logo 呈现方式），成本远低于从头训练。FastVideo 提供开箱即用的微调配方（Recipe）。

### 场景 3：本地私有化部署（苹果设备）

对于数据隐私要求高的企业（医疗、法律、金融），FastMetal-QAD 系列可以完全在 M 系列 Mac 上运行，无需云端 GPU，数据不出本地。14B 版本质量接近云端大模型。

### 场景 4：产品内嵌实时视频

基于 Dreamverse 架构自建实时视频生成服务，结合 Modal Serverless 按需弹性扩缩容，用户交互延迟可控在秒级以内。

---

## 生态影响力

FastVideo 的研究成果已被多个顶级项目采用：

- **SGLang**（2025-09-24）：基于 FastVideo fork 构建了 SGLang 的扩散推理功能
- **Hunyuan Video 1.5**（腾讯）：引入 SSTA（基于 Sliding Tile Attention）
- **SRPO**（腾讯混元）：基于 FastVideo 对扩散轨迹做人类偏好对齐
- **Kandinsky-5.0**：视频+图像生成，NABLA attention 包含 STA 分支
- **DanceGRPO**、**DCM**：视觉生成 GRPO 和双专家一致性模型均基于 FastVideo

---

## 总结

FastVideo 是目前覆盖最全面的开源视频生成框架：从 Apple Silicon 的 1.3B 本地模型到多卡 H100 的 14B 级训练，从 5 步蒸馏推理到 Dreamverse 实时流式生成，一个框架搞定。对于想在视频 AI 上有所布局的团队，FastVideo 是当前最值得深入的开源选择。

**GitHub**: [hao-ai-lab/FastVideo](https://github.com/hao-ai-lab/FastVideo) ⭐4,147  
**文档**: https://hao-ai-lab.github.io/FastVideo  
**实时演示**: https://dreamverse.fastvideo.org

---

## FastVideo: Unified Video Generation Framework — 5s Video in 1.8s

The video generation landscape has exploded over the past year, but most open-source frameworks handle either inference or training in isolation — never both. **FastVideo** from hao-ai-lab unifies inference acceleration, post-training (fine-tuning/distillation), and real-time generation into a single codebase, now at ⭐4,100+.

The headline benchmark: **FastWan-QAD generates a 5-second video in 1.8 seconds end-to-end.** FastH3 Preview v0.2 goes further by generating synchronized video *and* audio.

### Core Technical Highlights

**Sparse Distillation → >50× Denoising Speedup**

FastVideo introduces Video Sparse Attention (VSA, arXiv:2505.13389) combined with Distribution Matching Distillation (DMD2) to compress multi-step diffusion into few-step inference. The result: >50× denoising speedup over standard diffusion sampling.

Key models:
- **FastWan-QAD-FP8-1.3B**: 5s video ≈ 1.8s end-to-end
- **FastWan2.2-TI2V-5B**: 720P text+image-to-video
- **FastH3 Preview v0.2**: 4-step DMD2 distilled MiniMax-H3, video + audio sync
- **FastMetal-QAD (Apple Silicon)**: 1.3B/5B/14B optimized for Mac via MLX

**Full Hardware Coverage**

- NVIDIA: H100, A100, 4090, CUDA 12/13, FP8 quantization
- Apple Silicon: M1 through M4, MLX runtime, three model sizes
- DGX Spark: ARM64 + CUDA 13, dedicated install guide
- OS: Linux, Windows, macOS

**Complete Post-Training Pipeline**

FastVideo is not just an inference library. It provides the full training-to-deployment stack: full fine-tuning, LoRA, data preprocessing for video/image/text, off-the-shelf distillation recipes with synthetic datasets, FSDP2 distributed training, sequence parallelism, selective activation checkpointing, and causal distillation via Self-Forcing.

**Dreamverse — Real-Time "Vibe Directing"**

[Dreamverse](https://dreamverse.fastvideo.org/) is FastVideo's real-time video generation and editing platform where users can interact with a video *as it streams*. Deployable on local GPU, a B200 self-hosted server, Docker, or serverless Modal.

### Quick Start

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate

# NVIDIA CUDA 12
UV_TORCH_BACKEND=cu126 uv pip install fastvideo

# Apple Silicon
uv pip install -e '.[mlx]'
```

```python
from fastvideo import VideoGenerator
import os

os.environ["FASTVIDEO_ATTENTION_BACKEND"] = "VIDEO_SPARSE_ATTN"
generator = VideoGenerator.from_pretrained(
    "FastVideo/FastWan2.1-T2V-1.3B-Diffusers",
    num_gpus=1,
)
video = generator.generate_video(
    "A curious raccoon peers through a vibrant field of yellow sunflowers.",
    output_path="my_videos/",
    save_video=True,
)
```

### Enterprise Deployment Scenarios

**Batch video production**: FastWan-QAD-FP8-1.3B + sequence parallelism on a single A100 server delivers near-real-time throughput. Combine with FastVideo's data preprocessing pipeline for a fully automated copy-to-video workflow.

**Brand-style fine-tuning**: LoRA fine-tuning on a small set of brand assets teaches the model specific visual styles (color palette, composition, logo placement) at a fraction of the cost of training from scratch.

**On-premise private deployment**: For privacy-sensitive industries (healthcare, legal, finance), FastMetal-QAD runs entirely on M-series Macs — no cloud GPU, no data egress. The 14B variant approaches cloud-model quality.

**Real-time video products**: Build a streaming video generation service on the Dreamverse architecture with Modal Serverless elastic scaling. User-facing latency stays in the single-digit seconds range.

### Ecosystem Impact

FastVideo's research has been adopted by: **SGLang** (diffusion inference), **Hunyuan Video 1.5** (Tencent, SSTA), **SRPO** (Tencent Hunyuan, trajectory alignment), **Kandinsky-5.0** (NABLA attention), **DanceGRPO** and **DCM**.

FastVideo is the most comprehensive open-source video generation framework available today — spanning 1.3B local inference on Apple Silicon to multi-GPU 14B-scale training on H100 clusters. For any team serious about video AI, it is the first stop.

**GitHub**: [hao-ai-lab/FastVideo](https://github.com/hao-ai-lab/FastVideo) ⭐4,147  
**Docs**: https://hao-ai-lab.github.io/FastVideo  
**Live Demo**: https://dreamverse.fastvideo.org
