---
title: "LTX-2：Lightricks 开源 22B 音视频 DiT，开源视频生成进入三强时代"
titleEn: "ltx-2-lightricks-audio-video-22b-dit-open-source"
description: "Lightricks 开源 LTX-2（内部版本 LTX-2.3），22B 参数，首个基于 DiT 的音视频联合基础模型。一次推理同步生成画面与声音，原生 4K，最高 50fps，单次最长 10 秒。Gemma-3 12B 作为文本编码器，提供 11 条专用 Pipeline（T2V/I2V/A2V/关键帧插值/视频延伸/Dub-It 配音/HDR 等），IC-LoRA 精准控制（深度/姿态/Canny/运动轨迹），支持 ComfyUI 与 LoRA 训练。开源视频生成领域三强格局初现：MiniMax H3、LTX-2，以及即将开源的 FLUX3。"
descriptionEn: "Lightricks open-sources LTX-2 (LTX-2.3, 22B), the first DiT-based audio-video foundation model. Generates synchronized picture and sound in one inference pass — native 4K, up to 50fps, up to 10-second clips. Gemma-3 12B as text encoder. 11 specialized pipelines (T2V/I2V/A2V/keyframe interpolation/video extension/Dub-It/HDR/etc.), IC-LoRA precision control (depth/pose/canny/motion track), ComfyUI and LoRA training support. A new three-way open-source video generation landscape emerges: MiniMax H3, LTX-2, and FLUX3 (coming)."
pubDate: "2026-08-11"
updatedDate: "2026-08-11"
category: "Tech-News"
tags: ["视频生成", "开源", "DiT", "音视频", "LTX", "Lightricks", "22B", "Mycelium"]
heroImage: "../../assets/images/ltx-2-lightricks-audio-video-22b-dit-open-source-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

开源视频生成这条赛道，2026 年下半年正在快速成形。

MiniMax H3 已经出来了，FLUX3 宣布即将开源，现在 Lightricks 把 **LTX-2** 的权重和完整代码推上了 HuggingFace 和 GitHub。

这是三个分量都不轻的玩家在同一个时间窗口里出现，开源视频生成正式进入多强并立的阶段。

GitHub: https://github.com/Lightricks/LTX-2 | ⭐ 8,563 | Python  
HuggingFace: Lightricks/LTX-2.3 | arxiv: 2601.03233

---

## 什么是 LTX-2

LTX-2（HuggingFace 内部版本 LTX-2.3）是 Lightricks 的第二代视频生成基础模型，也是第一个基于 **DiT 架构**的**音视频联合基础模型**——不是先生成视频再拼音频，而是一次推理过程中同步生成画面和声音。

| 参数 | 规格 |
|------|------|
| 参数量 | 22B |
| 架构 | DiT（Diffusion Transformer） |
| 输入 | 文本 / 图像 / 音频 |
| 输出 | 视频 + 同步音频 |
| 分辨率 | 原生 4K |
| 帧率 | 最高 50fps |
| 最长时长 | 10 秒（单次） |
| 文本编码器 | Gemma-3 12B（QAT INT4） |
| 论文 | arxiv: 2601.03233 |

---

## 音视频同步是怎么做到的

LTX-2 不是把视频生成和音频生成拼在一起。它的训练目标就是联合分布：运动、对话、环境音、音乐在同一个 DiT 的去噪过程中被同时建模。

这意味着：

- 说话人的嘴形和音频帧级对齐，不需要后期对口型
- 背景音（脚步声、环境音）和对应的视觉动作同步出现
- 音乐节奏可以反映在镜头节奏上

**Dub-It Pipeline** 把这个能力再推进了一步：给定已有视频和新的对白，模型在保持说话人身份和嘴形的同时重新生成音频——相当于 AI 配音，帧级唇形同步。

---

## 11 条 Pipeline

LTX-2 不是只有一个用法。仓库提供了 11 条专用 Pipeline，覆盖不同的生产需求：

| Pipeline | 用途 |
|----------|------|
| TI2VidTwoStagesPipeline | 主推，文本/图像→视频，2× 空间上采样，生产质量 |
| TI2VidTwoStagesHQPipeline | 同上，使用 res_2s 二阶采样，步数更少质量更高 |
| TI2VidOneStagePipeline | 单阶段，快速原型 |
| DistilledPipeline | 最快，8个预定义 sigma，阶段1 8步，阶段2 4步 |
| ICLoraPipeline | 视频转视频 / 图像转视频，使用蒸馏模型 |
| KeyframeInterpolationPipeline | 关键帧图像之间插值 |
| A2VidPipelineTwoStage | 音频→视频，以输入音频为条件 |
| RetakePipeline | 重新生成现有视频的指定时间段 |
| HDRICLoraPipeline | 视频转视频，HDR 输出（LogC3 反解，适合 EXR 导出和色调映射） |
| DubItPipeline | 配音，保持说话人身份和嘴形，重新生成对白音频 |

**推荐入口**：生产质量用 TI2VidTwoStagesPipeline，追求速度用 DistilledPipeline。

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/Lightricks/LTX-2.git
cd LTX-2

# 下载蒸馏模型（最快上手）
hf auth login
hf download Lightricks/LTX-2.3 \
    ltx-2.3-22b-distilled-1.1.safetensors \
    ltx-2.3-spatial-upscaler-x2-1.1.safetensors \
    --local-dir models/ltx-2.3
hf download google/gemma-3-12b-it-qat-q4_0-unquantized --local-dir models/gemma-3-12b

# 生成（蒸馏 Pipeline，最快）
uv run python -m ltx_pipelines.distilled \
    --distilled-checkpoint-path models/ltx-2.3/ltx-2.3-22b-distilled-1.1.safetensors \
    --spatial-upsampler-path    models/ltx-2.3/ltx-2.3-spatial-upscaler-x2-1.1.safetensors \
    --gemma-root models/gemma-3-12b \
    --seed 42 \
    --output-path output.mp4 \
    --prompt "..."
```

显存不够：`--quantization fp8-cast --offload cpu`（或 `disk`）。

---

## IC-LoRA 控制

LTX-2 提供多个官方 IC-LoRA（图像条件 LoRA），通过 ICLoraPipeline 使用：

- **深度控制**：LTX-2.3-22b-IC-LoRA-Union-Control
- **运动轨迹控制**：LTX-2.3-22b-IC-LoRA-Motion-Track-Control
- **HDR**：LTX-2.3-22b-IC-LoRA-HDR
- **Dub-It**：LTX-2.3-22b-IC-LoRA-DubIt
- **姿态控制**（19B 版本）：LTX-2-19b-IC-LoRA-Pose-Control
- **细节增强**：LTX-2-19b-IC-LoRA-Detailer
- **摄像机运动 LoRA**：Dolly In/Out/Left/Right、Jib Up/Down、Static（各一个 19B LoRA）

---

## 性能优化

**量化**：
- `--quantization fp8-cast`：bf16 权重推断时动态降精度，显存更小
- `--quantization fp8-scaled-mm`：需要 FP8 权重，Hopper+ GPU 原生 FP8 矩阵乘加速

**注意力后端**：
- B200（Blackwell）：手动安装 `flash-attn-4==4.0.0b9`
- Hopper：安装 FlashAttention 3 wheel
- 其他 CUDA：自动使用 PyTorch SDPA

**推理步数**：使用梯度估计可以把步数从 40 降到 20-30，质量基本保持。

---

## 两阶段 Pipeline 是什么意思

LTX-2 的主要生产 Pipeline 是两阶段的：

1. **阶段1**：在较低分辨率生成视频（更快，占用显存少）
2. **阶段2**：通过空间上采样器（x2 或 x1.5）提升到目标分辨率

这两个阶段使用同一个基础模型，通过蒸馏 LoRA 配合工作。蒸馏 Pipeline（DistilledPipeline）是特例，只用蒸馏权重，不需要额外 LoRA，步数最少。

---

## Prompting 技巧

LTX-2 的提示词设计遵循电影分镜逻辑：

- 用一句话描述主要动作
- 详细描述运动和手势
- 精确描述角色/物体外观
- 说明背景和环境
- 指定摄像机角度和运动
- 描述光线和颜色
- 说明变化或突发事件

不超过 200 词，直接描述，不用元语言（比如「一个视频，展示了……」）。

Pipeline 支持 `enhance_prompt` 参数，自动增强提示词。

---

## 背景：开源视频三强

用户提到的三个名字：

| 模型 | 出处 | 状态 |
|------|------|------|
| MiniMax H3 | MiniMax | 已开源 |
| LTX-2 | Lightricks | 已开源（本文） |
| FLUX3 | Black Forest Labs | 即将开源 |

这三个模型的技术路线各有侧重，但都在推动一件事：把专业级视频生成能力下放到可以本地运行或低成本 API 调用的层面。

LTX-2 的独特点在于**音视频联合建模**，这是另外两个目前没有明确宣称的能力。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## LTX-2: Lightricks Open-Sources a 22B Audio-Video DiT — Open-Source Video Generation Gets Three Major Players

*by Mycelium Protocol*

---

The open-source video generation track is rapidly consolidating in the second half of 2026.

MiniMax H3 is already out. FLUX3 is announced and coming soon. Now Lightricks has pushed **LTX-2**'s weights and full code to HuggingFace and GitHub.

Three significant players appearing in the same window. Open-source video generation now has multiple heavy contenders.

GitHub: https://github.com/Lightricks/LTX-2 | ⭐ 8,563 | Python  
HuggingFace: Lightricks/LTX-2.3 | arxiv: 2601.03233

---

### What LTX-2 Is

LTX-2 (internally versioned as LTX-2.3) is Lightricks' second-generation video generation foundation model — and the first **DiT-based audio-video joint foundation model**. Not video first, audio second: a single inference pass generates picture and sound together.

| Spec | Value |
|------|-------|
| Parameters | 22B |
| Architecture | DiT (Diffusion Transformer) |
| Input | Text / image / audio |
| Output | Video + synchronized audio |
| Resolution | Native 4K |
| Frame rate | Up to 50fps |
| Max duration | 10 seconds per clip |
| Text encoder | Gemma-3 12B (QAT INT4) |
| Paper | arxiv: 2601.03233 |

---

### How Synchronized Audio-Video Works

LTX-2 doesn't bolt audio generation onto a video model. Its training target is the joint distribution: motion, dialogue, ambience, and music are all modeled simultaneously in the same DiT denoising process.

In practice:
- Lip movements are frame-aligned with the audio track
- Background sounds (footsteps, ambient noise) appear synchronized with the corresponding visual action
- Music rhythm can influence shot rhythm

**Dub-It Pipeline** takes this further: given an existing video and new dialogue, the model regenerates the audio while preserving speaker identity and lip movements. Frame-accurate dubbing without separate lip-sync post-processing.

---

### 11 Pipelines

LTX-2 ships with 11 specialized pipelines:

| Pipeline | Use case |
|----------|----------|
| TI2VidTwoStagesPipeline | Main: text/image→video with 2× spatial upsampling, production quality |
| TI2VidTwoStagesHQPipeline | Same two-stage flow but uses res_2s second-order sampler |
| TI2VidOneStagePipeline | Single-stage, quick prototyping |
| DistilledPipeline | Fastest: 8 predefined sigmas (8 steps stage 1, 4 steps stage 2) |
| ICLoraPipeline | Video-to-video / image-to-video transformations |
| KeyframeInterpolationPipeline | Interpolate between keyframe images |
| A2VidPipelineTwoStage | Audio-conditioned video generation |
| RetakePipeline | Regenerate a specific time region of an existing video |
| HDRICLoraPipeline | Video-to-video with HDR output (LogC3 inverse decode, EXR-ready) |
| DubItPipeline | Redub dialogue preserving speaker identity and lip movements |

**Recommended entry points**: TI2VidTwoStagesPipeline for production quality; DistilledPipeline for speed.

---

### Quick Start

```bash
git clone https://github.com/Lightricks/LTX-2.git
cd LTX-2

# Download distilled model (fastest path)
hf auth login
hf download Lightricks/LTX-2.3 \
    ltx-2.3-22b-distilled-1.1.safetensors \
    ltx-2.3-spatial-upscaler-x2-1.1.safetensors \
    --local-dir models/ltx-2.3
hf download google/gemma-3-12b-it-qat-q4_0-unquantized --local-dir models/gemma-3-12b

# Generate
uv run python -m ltx_pipelines.distilled \
    --distilled-checkpoint-path models/ltx-2.3/ltx-2.3-22b-distilled-1.1.safetensors \
    --spatial-upsampler-path    models/ltx-2.3/ltx-2.3-spatial-upscaler-x2-1.1.safetensors \
    --gemma-root models/gemma-3-12b \
    --seed 42 \
    --output-path output.mp4 \
    --prompt "..."
```

Low VRAM: `--quantization fp8-cast --offload cpu` (or `disk`).

---

### IC-LoRA Control

| LoRA | Capability |
|------|-----------|
| LTX-2.3-22b-IC-LoRA-Union-Control | Depth + structure control |
| LTX-2.3-22b-IC-LoRA-Motion-Track-Control | Motion trajectory control |
| LTX-2.3-22b-IC-LoRA-HDR | HDR video-to-video |
| LTX-2.3-22b-IC-LoRA-DubIt | Dialogue dubbing with lip sync |
| LTX-2-19b-IC-LoRA-Pose-Control | Pose control |
| LTX-2-19b-IC-LoRA-Detailer | Detail enhancement |
| Camera motion LoRAs (19B) | Dolly In/Out/Left/Right, Jib Up/Down, Static |

---

### Performance Optimization

**Quantization**:
- `fp8-cast`: on-the-fly downcast of bf16 checkpoints — lower VRAM
- `fp8-scaled-mm`: native FP8 matrix multiplication on Hopper+ GPUs (use with fp8 checkpoints)

**Attention backends**:
- B200 (Blackwell): install FlashAttention 4 (`flash-attn-4==4.0.0b9`, verified against torch 2.9.1+cu128)
- Hopper: FlashAttention 3 wheel
- Other CUDA: PyTorch SDPA automatically

**Steps reduction**: gradient estimation can cut inference steps from 40 to 20-30 with minimal quality loss.

---

### Context: The Three-Way Open-Source Landscape

| Model | Source | Status |
|-------|--------|--------|
| MiniMax H3 | MiniMax | Open |
| LTX-2 | Lightricks | Open (this release) |
| FLUX3 | Black Forest Labs | Coming soon |

LTX-2's differentiator is **joint audio-video modeling** — generating synchronized sound as a first-class output, not a post-processing step. That's not something the other two have explicitly claimed.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
