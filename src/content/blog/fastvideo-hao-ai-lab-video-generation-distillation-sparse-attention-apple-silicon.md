---
title: "FastVideo：视频生成加速框架，稀疏蒸馏 >50x + FastMetal 支持 Apple Silicon 本地推理"
titleEn: "fastvideo-hao-ai-lab-video-generation-distillation-sparse-attention-apple-silicon"
description: "FastVideo 是 hao-ai-lab 开源（Apache 2.0）的统一视频生成后训练与实时推理框架，4K stars。核心技术：Video Sparse Attention（VSA）+ Sparse Distillation 实现 >50x 去噪加速，DMD2 步进蒸馏，Self-Forcing 因果蒸馏；最新 FastWan-QAD 5 秒视频端到端 1.8 秒生成，FastMetal-QAD 支持 Apple Silicon MLX 本地推理（1.3B/5B/14B）；Dreamverse 实时视频生成与「vibe directing」编辑平台；SGLang 扩散推理基于 FastVideo fork。"
descriptionEn: "FastVideo is hao-ai-lab's open-source (Apache 2.0) unified post-training and real-time inference framework for accelerated video generation (4K stars). Core tech: Video Sparse Attention (VSA) + Sparse Distillation for >50x denoising speedup, DMD2 stepwise distillation, Self-Forcing causal distillation. FastWan-QAD: 5s video in 1.8s E2E. FastMetal-QAD: Apple Silicon MLX local inference (1.3B/5B/14B). Dreamverse: real-time video generation and vibe-directing editing platform. SGLang's diffusion inference forked from FastVideo."
pubDate: "2026-08-20"
updatedDate: "2026-08-20"
category: "Tech-News"
tags: ["视频生成", "稀疏注意力", "蒸馏", "Apple Silicon", "推理加速", "开源", "扩散模型", "实时生成"]
heroImage: "../../assets/images/fastvideo-hao-ai-lab-video-generation-distillation-sparse-attention-apple-silicon-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：hao-ai-lab/FastVideo  
文档：hao-ai-lab.github.io/FastVideo  
许可证：Apache 2.0  
语言：Python  
Stars：~4K

---

FastVideo 是 UC Berkeley hao-ai-lab 开源的统一视频生成框架，覆盖从模型后训练到实时推理的完整流水线。在速度上它的记录是：**5 秒视频端到端 1.8 秒生成**（FastWan-QAD），以及**单 GPU 4.5 秒完成 5 秒 1080p 视频**。

---

## 一、两个核心技术方向

### Video Sparse Attention（VSA）

VSA 是 FastVideo 的核心注意力机制，发表为 [arxiv:2505.13389](https://arxiv.org/pdf/2505.13389)。视频扩散模型中的注意力计算随帧数二次增长，VSA 通过可学习的稀疏注意力模式大幅降低计算量，同时保持视频质量。

已被多个主流项目采用：
- **HunyuanVideo 1.5**（腾讯）：基于 Sliding Tile Attention，参考了 FastVideo 的 VSA 工作
- **Kandinsky-5.0**（基于 NABLA attention，含 Sliding Tile Attention 分支）
- **LongCat Video**（13.6B 参数，使用块稀疏注意力，类似 VSA）

### Sparse Distillation

Sparse Distillation 实现 **>50x 去噪步数加速**，把通常需要数十步的扩散推理压缩到极少步数，同时保持视觉质量。支持的蒸馏方法：

| 方法 | 说明 |
|------|------|
| DMD2（Distribution Matching Distillation） | 步进蒸馏，端到端质量对齐 |
| Sparse Distillation | 结合 VSA 稀疏模式的蒸馏 |
| Self-Forcing 因果蒸馏 | 用于自回归视频模型（CausalWan） |

---

## 二、最新模型系列

### FastWan-QAD：5 秒视频 1.8 秒生成

2026 年 6 月发布，QAD（量化感知蒸馏）系列中的速度旗舰。在 NVIDIA GPU 上，5 秒视频端到端生成时间降到 1.8 秒。

可用模型：
- FastWan2.1-T2V-1.3B（文生视频，480P）
- FastWan2.2-TI2V-5B（文图生视频，720P）

### FastMetal-QAD：Apple Silicon 本地推理

2026 年 8 月 19 日发布，通过 MLX 运行时支持 Mac 本地推理：

- **1.3B、5B、14B** 三个规格，适配不同 Mac 配置
- 在 Apple Silicon 上本地生成 5 秒 480p 视频，无需云端，无需独立 GPU
- 安装：`uv pip install -e '.[mlx]'`

```bash
# Apple Silicon 安装
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install -e '.[mlx]'
```

### CausalWan 系列

CausalWan2.2 I2V A14B 是图生视频（Image-to-Video）的自回归模型，通过 Self-Forcing 因果蒸馏训练，已有 Preview 版本开放。

---

## 三、Dreamverse：实时视频生成与编辑

Dreamverse 是 FastVideo monorepo 内的独立应用（`apps/dreamverse/`），实现「vibe directing」——视频在生成过程中实时流式输出，用户可以在视频流过程中动态引导方向。

部署选项：
- 本地 GPU
- 自托管 B200 服务器（SSH）
- Docker
- Serverless Modal

[在线 Demo](https://dreamverse.fastvideo.org/) 可直接体验。

---

## 四、后训练支持矩阵

FastVideo 支持双向扩散模型和自回归模型的完整后训练流程：

- **全量微调 + LoRA 微调**：支持主流开源视频 DiT 模型
- **数据预处理流水线**：视频、图像、文本三种数据类型
- **训练基础设施**：FSDP2 + Sequence Parallelism + 选择性激活检查点，支持大规模分布式训练

支持硬件：H100、A100、RTX 4090；平台：Linux、Windows、macOS（Apple Silicon）。

---

## 五、推理接口

### Python API

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
    save_video=True
)
```

### 安装

```bash
# NVIDIA GPU（CUDA 12）
uv venv --python 3.12 --seed && source .venv/bin/activate
UV_TORCH_BACKEND=cu126 uv pip install fastvideo

# CUDA 13（DGX Spark / GB10）
UV_TORCH_BACKEND=cu130 uv pip install -e .

# Apple Silicon
uv pip install -e '.[mlx]'
```

FastVideo 还提供了专门给 AI 编码 Agent 安装的 prompt 模板（`AGENTS.md`），Claude Code、Cursor 等工具可以直接粘贴使用，自动检测平台并选择对应安装路径。

---

## 六、生态影响

FastVideo 作为基础框架被多个重要项目采用：

- **SGLang**：扩散推理功能基于 FastVideo fork（2025 年 9 月）
- **DanceGRPO**：GRPO 迁移到视觉生成的统一框架，代码基于 FastVideo
- **SRPO**（腾讯混元）：扩散轨迹偏好对齐方法，代码基于 FastVideo
- **HY-WorldPlay**（腾讯混元）：动作条件世界模型，使用 FastVideo 训练框架

---

FastVideo 解决的是视频生成领域的计算效率问题：稀疏注意力 + 蒸馏的组合让原来需要高端多卡才能跑的任务下沉到单卡甚至 Mac 本地，同时保持生产级视频质量。4K stars、Apache 2.0 协议、活跃开发（最后更新 2026-08-20），是目前视频扩散模型加速方向最系统的开源框架之一。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## FastVideo: Accelerated Video Generation — Sparse Distillation >50x, FastMetal for Apple Silicon, Dreamverse Real-Time Editing

*by Mycelium Protocol*

---

GitHub: hao-ai-lab/FastVideo  
Docs: hao-ai-lab.github.io/FastVideo  
License: Apache 2.0  
Language: Python  
Stars: ~4K

---

FastVideo is UC Berkeley hao-ai-lab's open-source unified framework for video generation post-training and real-time inference. Speed records: **5-second video generated end-to-end in 1.8 seconds** (FastWan-QAD), and **5-second 1080p video in 4.5 seconds on a single GPU**.

---

### Two Core Technical Directions

**Video Sparse Attention (VSA)**: Published as [arxiv:2505.13389](https://arxiv.org/pdf/2505.13389). Attention in video diffusion models scales quadratically with frames. VSA applies a learnable sparse attention pattern that cuts compute while maintaining video quality. Adopted by HunyuanVideo 1.5, Kandinsky-5.0, and LongCat Video.

**Sparse Distillation**: Achieves **>50x denoising step speedup** — compressing tens of diffusion steps into very few while preserving visual quality. Three supported distillation methods:

| Method | Purpose |
|--------|---------|
| DMD2 (Distribution Matching Distillation) | Stepwise distillation with end-to-end quality alignment |
| Sparse Distillation | Combines VSA sparse patterns with distillation |
| Self-Forcing causal distillation | For autoregressive video models (CausalWan) |

---

### Model Releases

**FastWan-QAD** (June 2026): Quantization-Aware Distillation. 5-second video E2E in 1.8 seconds on NVIDIA GPU. Available as FastWan2.1-T2V-1.3B (text-to-video, 480P) and FastWan2.2-TI2V-5B (text+image-to-video, 720P).

**FastMetal-QAD** (August 19, 2026): MLX runtime for Apple Silicon. 1.3B, 5B, and 14B variants optimized for Mac. Generates a 5-second 480p clip locally — no cloud, no discrete GPU.

```bash
uv pip install -e '.[mlx]'
```

**CausalWan series**: Image-to-video autoregressive model (CausalWan2.2 I2V A14B), trained with Self-Forcing causal distillation.

---

### Dreamverse: Real-Time Video Generation and Editing

Dreamverse lives in the monorepo at `apps/dreamverse/` — a "vibe directing" platform where video streams in real-time as it's generated, and users can dynamically steer the direction during generation.

Deploy on: local GPU, self-hosted B200 server (SSH), Docker, or serverless Modal. [Live demo available.](https://dreamverse.fastvideo.org/)

---

### Post-Training Support

- Full finetuning and LoRA finetuning for state-of-the-art open video DiTs
- Data preprocessing pipeline for video, image, and text
- FSDP2 + sequence parallelism + selective activation checkpointing for scalable distributed training
- Hardware: H100, A100, RTX 4090; Platforms: Linux, Windows, macOS

---

### Python API

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
    save_video=True
)
```

FastVideo also ships `AGENTS.md` — a prompt template that lets Claude Code, Cursor, or any coding agent detect the platform and auto-follow the correct install guide.

---

### Ecosystem Impact

- **SGLang**: diffusion inference functionality forked from FastVideo (Sept 2025)
- **DanceGRPO**: GRPO adapted to visual generation, codebase on FastVideo
- **SRPO** (Tencent HunyuanVideo): diffusion trajectory preference alignment, based on FastVideo
- **HY-WorldPlay** (Tencent): action-conditioned world model, trained with FastVideo

---

FastVideo's core achievement: combining sparse attention and distillation to bring video generation from high-end multi-GPU clusters down to a single GPU or a local Mac, without sacrificing production-quality output. ~4K stars, Apache 2.0, actively developed. The most systematic open-source framework in the video diffusion acceleration space.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
