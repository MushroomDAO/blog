---
title: "字节开源 Lance：3B 参数搞定图像视频六合一，VBench 登顶统一模型榜"
titleEn: "ByteDance Open-Sources Lance: 3B Parameters, Six Tasks, VBench Top Among Unified Models"
description: "字节跳动智能创作实验室开源 Lance：3B 激活参数，统一支持图像理解/生成/编辑与视频理解/生成/编辑六项任务。GenEval 0.90 并列第一，VBench 85.11 登顶统一模型，Apache 2.0 开源。"
descriptionEn: "ByteDance Intelligent Creation Lab open-sources Lance: 3B active parameters unifying image understanding/generation/editing and video understanding/generation/editing. GenEval 0.90 tied first, VBench 85.11 tops unified models. Apache 2.0."
pubDate: "2026-05-29"
updatedDate: "2026-05-29"
category: "Tech-News"
tags: ["多模态", "字节跳动", "Lance", "图像生成", "视频生成", "开源", "3B", "统一模型"]
heroImage: "../../assets/images/lance-bytedance-banner.jpg"
---

字节跳动智能创作实验室开源了 Lance——一个用 3B 参数同时拿下六项多模态任务的统一模型。

> 📌 GitHub：https://github.com/bytedance/Lance  
> HuggingFace：https://huggingface.co/bytedance-research/Lance  
> 论文：http://arxiv.org/abs/2605.18678  
> 项目主页：https://lance-project.github.io  
> 协议：Apache 2.0

## 六项能力，一个模型

Lance 把以下六件事塞进了同一套权重：

| 任务 | 说明 |
|------|------|
| 图像理解 | 看图说话、VQA、视觉推理 |
| 图像生成 | 文本→图像，最高 768×768 |
| 图像编辑 | 换背景、改内容、去水印 |
| 视频理解 | 视频字幕、视频问答 |
| 视频生成 | 文本/图像→视频，480p / 12fps / 最长 121 帧 |
| 视频编辑 | 改场景、换人物、加特效 |

以前需要 6 个专用模型分别完成的事，Lance 一套搞定。

## 基准成绩

- **GenEval（图像生成）**：0.90，与 7B 模型并列统一模型第一
- **VBench（视频生成）**：85.11，统一模型榜第一
- **GEdit-Bench（图像编辑）**：7.30，统一模型最高
- **MVBench（视频理解）**：62.0，统一模型最高，领先第二名十几个点
- **DPG-Bench（图像生成）**：84.67

## 技术要点

Lance 采用**双流 MoE 架构**，配合自研的 **MaPE（Modality-Aware Rotary Positional Encoding）**，将理解路径和生成路径解耦，同时共享多模态上下文。分阶段多任务训练策略让各能力互相增益而非干扰。

激活参数仅 3B，训练用了最多 128 张 A100。部署门槛：Python 3.10+，CUDA 12.4+，最低 40GB 显存。

目前以研究预览形式开放，Fine-tuning 代码和图像转视频功能在路线图上，尚未发布。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

ByteDance's Intelligent Creation Lab has open-sourced Lance — a unified model that handles six multimodal tasks with just 3B active parameters.

> 📌 GitHub: https://github.com/bytedance/Lance  
> HuggingFace: https://huggingface.co/bytedance-research/Lance  
> Paper: http://arxiv.org/abs/2605.18678  
> Project page: https://lance-project.github.io  
> License: Apache 2.0

## Six Capabilities, One Model

Lance packs all of the following into a single set of weights: image understanding (VQA, visual reasoning), image generation (up to 768×768), image editing, video understanding (captioning, VQA), video generation (480p / 12fps / up to 121 frames), and video editing.

## Benchmark Highlights

- **GenEval** (image gen): 0.90 — tied first among unified models alongside 7B models
- **VBench** (video gen): 85.11 — tops all unified models
- **GEdit-Bench** (image edit): 7.30 — highest among unified models
- **MVBench** (video understanding): 62.0 — highest among unified models, double-digit lead over second place
- **DPG-Bench**: 84.67

## Architecture

Lance uses a **dual-stream MoE design** with **MaPE (Modality-Aware Rotary Positional Encoding)** that decouples understanding and generation pathways while sharing interleaved multimodal context. Staged multi-task training lets the six capabilities reinforce rather than interfere with each other.

Requirements: Python 3.10+, CUDA 12.4+, minimum 40GB VRAM. Fine-tuning code and image-to-video support are on the roadmap, not yet released.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
