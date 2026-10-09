---
title: "Kandinsky 6.0 Video：双流 CrossDiT，音视频同步生成开源了"
titleEn: "Kandinsky 6.0 Video: Dual-Stream CrossDiT for Synchronized Audio-Video Generation"
description: "Kandinsky Lab（Sber）发布 Kandinsky 6.0 Video（MIT，arXiv 2610.05608），双流 CrossDiT 架构同时生成视频和音频——不是先出画面再配音，而是视频流和音频流通过双向交叉注意力联合生成。Lite（3B）和 Pro（29B）两个尺寸，输出 5 秒 24fps，44 kHz 音频，支持唇形同步。两种输入模式：T2AV（文本生成音视频）和 I2AV（给一张参考图让模型往下演并配音）。Pro 在 Kling 2.6、Veo 3.1 Fast、MiniMax H3、Seedance 2.0 的对比评测中，在语音质量、唇形同步、音视频对齐方面排首位。配套 Kandinsky 6.0 VSR（1.4B）超分辨率模块可升至 Full HD。可通过 Sber GigaChat 免费体验。"
descriptionEn: "Kandinsky Lab (Sber) releases Kandinsky 6.0 Video (MIT, arXiv 2610.05608) — a dual-stream CrossDiT architecture that generates video and audio jointly, not sequentially. A video stream and audio stream connect via bidirectional cross-attention. Two sizes: Lite (3B) and Pro (29B). Output: 5-second clips at 24 fps, 44 kHz audio, with lip-sync. Two input modes: T2AV (text-to-audio-video) and I2AV (image-to-audio-video, using a reference first frame). Pro ranks first on speech quality, lip-sync, and audio-video alignment against Kling 2.6, Veo 3.1 Fast, MiniMax H3, and Seedance 2.0 per vendor evaluation. Companion Kandinsky 6.0 VSR (1.4B) upscales to Full HD."
pubDate: 2026-10-09
heroImage: "../../assets/images/kandinsky-6-video-crossdit-audio-video-sync-t2av-i2av-banner.jpg"
category: "Tech-News"
tags: ["视频生成", "音频生成", "开源模型", "多模态", "AI工具"]
lang: "zh-CN"
wechatTitle: "Kandinsky 6.0：音视频同步生成开源了"
wechatDigest: "MIT；29B CrossDiT；T2AV/I2AV；5秒24fps 44kHz；唇形同步；GigaChat免费试"
---

一句话同时出画面和声音，不是先渲视频再配音。

Kandinsky Lab（隶属 Sber）在 2026 年 10 月 4 日发布 Kandinsky 6.0 Video，底层架构叫 **CrossDiT**：视频流和音频流同时推理，通过双向交叉注意力在每个时间步交换信息，最终输出的画面和声音是共同生长出来的，而不是拼接出来的。

arXiv: https://arxiv.org/abs/2610.05608 | MIT | Kandinsky Lab (Sber)

---

## 两种生成模式

**T2AV（文生音视频）**：一句文字提示，直接出 5 秒带声音的视频。提示里写的内容——场景、动作、音效——会同时在画面和音轨里体现。

**I2AV（图生音视频）**：给一张图作为第一帧，模型推测接下来会发生什么，自动生成画面运动和配套音频。适合从静态图或参考概念图出发做创作。

不需要声音时可以单独关闭音频输出，只要画面。

---

## CrossDiT 架构

传统音视频生成的做法是把两个独立模型串联：先视频，再配音。CrossDiT 做的是**并行双流**：

- **视频流**：从预训练的 Kandinsky 5.0 视频基础模型初始化，不从零训练
- **音频流**：全新从零构建，先在大规模音频语料上预训练，再与视频流联合优化
- **双向交叉注意力**：视频流的每一层可以"看到"音频流当前状态，反之亦然——帧和声音互相影响，保持同步

这是训练设计上的选择，不是推理时做的后期对齐。

---

## 规格

| 项目 | 参数 |
|------|------|
| 视频时长 | 5 秒（121 帧） |
| 帧率 | 24 fps |
| 音频采样率 | 44 kHz |
| 唇形同步 | ✅ 原生支持 |
| 输出分辨率 | 训练分辨率（+VSR 可升 Full HD） |

每个尺寸都有三种变体：
- **base**：基础检查点
- **pretrained**：更长训练周期版本
- **distilled**：10 步蒸馏版，推理更快

---

## 两个尺寸

**Lite（3B）**：面向本地部署和快速迭代，计算要求低。

**Pro（29B）**：面向质量优先场景，Sber 内部人工评测结果是：在语音质量、唇形同步准确率、音视频对齐度上压过了 Kling 2.6、Veo 3.1 Fast、MiniMax H3、Seedance 2.0。评测基准是 **VABench**（专门针对音视频联合生成的评测集）。

⚠️ 这是 Sber 自己发布的对比数据，未经独立第三方复现。评测框架 VABench 也是 Kandinsky Lab 配套发布的，方法论中立性待社区验证。

---

## 训练流程

```
音频流预训练（大规模音频语料）
        ↓
视频+音频联合训练（配对音视频数据）
        ↓
有监督微调（SFT）
        ↓
强化学习后训练（RL）
        ↓
蒸馏（10步快速版本）
```

音频流不依赖任何现有的开源音频模型——这是完全自研的新流，专门针对音视频联合生成优化。

---

## 超分辨率模块：VSR

**Kandinsky 6.0 VSR**（1.4B 独立模型）：将生成的视频升分辨率到 Full HD（1920×1080）。可以在 CrossDiT 主生成结束后单独调用，也可以集成进端到端流水线。

---

## 部署和体验

**免费体验**：通过 Sber 的 **GigaChat** 服务，不需要部署，直接在线试用。

**本地部署**：
- GitHub（参考）：https://github.com/kandinskylab/kandinsky-6
- HuggingFace 检查点：`kandinskylab/Kandinsky-6.0-Pro-5s-Diffusers`
- ComfyUI 集成已有社区支持

---

## 一句话说清楚

Kandinsky 6.0 Video 不是音频条件视频生成，也不是视频条件音频生成——是两者联合生成，CrossDiT 在扩散过程里让音频流和视频流互相影响，最终输出的声画是共同演化出来的。MIT 开源，Pro 29B 在 VABench 上排首位（供应商自测）。本地可用 Lite 3B，追求质量走 Pro，免部署直接去 GigaChat。

---

> MIT 许可。Kandinsky Lab（Sber）2026-10-04 发布，arXiv 2610.05608。开源仅供学习参考。

---

<!--EN-->

## Kandinsky 6.0 Video: Dual-Stream CrossDiT for Synchronized Audio-Video Generation

One text prompt. Video and audio at the same time — not sequenced, but jointly generated.

Kandinsky Lab (Sber) released Kandinsky 6.0 Video on October 4, 2026. The architecture, called **CrossDiT**, runs a video stream and an audio stream in parallel, connected at every timestep via **bidirectional cross-attention**. The audio and video literally evolve together during diffusion — they're not stitched together in post-processing.

arXiv: https://arxiv.org/abs/2610.05608 | MIT | Kandinsky Lab (Sber)

---

### Two Input Modes

**T2AV (Text-to-Audio-Video)**: A text prompt generates a 5-second clip with synchronized audio. Whatever the prompt describes — the scene, the motion, the ambient sound — appears in both the visual track and the audio track.

**I2AV (Image-to-Audio-Video)**: A reference image becomes the first frame. The model infers what happens next and generates both the motion and the audio track. Good for starting from a concept image or storyboard.

Audio can be disabled to output video-only.

---

### CrossDiT Architecture

Most audio-video generation pipelines chain two independent models: generate video, then dub audio. CrossDiT uses **parallel dual streams**:

- **Video stream**: initialized from the pretrained Kandinsky 5.0 video foundation model
- **Audio stream**: built from scratch, first pretrained on large audio corpora, then jointly optimized with the video stream
- **Bidirectional cross-attention**: every layer in the video stream can "see" the audio stream state, and vice versa — frames and sound influence each other, maintaining sync

This sync is a training design choice, not post-hoc alignment.

---

### Specs

| Item | Value |
|------|-------|
| Clip length | 5 seconds (121 frames) |
| Frame rate | 24 fps |
| Audio sample rate | 44 kHz |
| Lip sync | ✅ Native |
| Base resolution | Training resolution (VSR optional for Full HD) |

Three variants per size:
- **base**: standard checkpoint
- **pretrained**: extended training
- **distilled**: 10-step fast inference

---

### Two Sizes

**Lite (3B)**: For local deployment and fast iteration.

**Pro (29B)**: Quality-first. Per Sber's human evaluation on **VABench**, Pro ranks first on speech quality, lip-sync accuracy, and audio-video alignment — ahead of Kling 2.6, Veo 3.1 Fast, MiniMax H3, and Seedance 2.0.

⚠️ This comparison data comes from the model's authors. VABench was also released by Kandinsky Lab, so the methodology hasn't been independently verified yet.

---

### Training Pipeline

```
Audio stream pretrain (large-scale audio corpora)
        ↓
Joint video+audio training (paired AV data)
        ↓
Supervised fine-tuning (SFT)
        ↓
RL post-training
        ↓
Distillation (10-step fast variant)
```

The audio stream doesn't depend on any existing open-source audio model — it's purpose-built for joint AV generation.

---

### VSR Super-Resolution Module

**Kandinsky 6.0 VSR** (1.4B standalone model): upscales generated video to Full HD (1920×1080). Can run after CrossDiT or be integrated into an end-to-end pipeline.

---

### TL;DR

Kandinsky 6.0 Video isn't audio-conditioned video generation or video-conditioned audio generation — it's joint generation: CrossDiT runs both streams in parallel through the diffusion process, cross-attending at every step. MIT license. Pro 29B leads VABench (vendor self-test). Lite 3B for local use, GigaChat for zero-setup demo.

---

> MIT license. Released by Kandinsky Lab (Sber) on 2026-10-04. arXiv 2610.05608. For technical reference only.
