---
title: "SenseNova U1.5：看图、生图、改图，一个模型全搞定"
titleEn: "sensenova-u15-unified-image-understand-generate-edit-mot"
description: "商汤 SenseNova-U1.5-8B-MoT 把图像理解、图像生成、图像编辑三项能力统一进同一个 8B 参数模型，基于自研 NEO-unify 架构与 MoT（Mixture of Tokens）范式，在不增加推理开销的前提下原生支持 4K 输出，Apache 2.0 开源，GitHub 5.4k Star。"
descriptionEn: "SenseNova-U1.5-8B-MoT from SenseTime unifies image understanding, generation, and editing in a single 8B-parameter model via NEO-unify architecture and MoT (Mixture of Tokens). Native 4K output, Apache 2.0, 5.4k GitHub stars."
pubDate: "2026-08-24"
updatedDate: "2026-08-24"
category: "Tech-News"
tags: ["开源", "多模态", "图像生成", "图像编辑", "MoT", "NEO-unify", "SenseNova", "商汤"]
heroImage: "../../assets/images/sensenova-u15-unified-image-understand-generate-edit-mot-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：OpenSenseNova/SenseNova-U1 ⭐ 5,436 | Forks 446 | Apache 2.0  
HuggingFace：sensenova/SenseNova-U1.5-8B-MoT  
ModelScope：SenseNova/SenseNova-U1.5-8B-MoT  
论文：arXiv 2605.12500  
Demo：https://unify.light-ai.top/  
发布日期：2026-08-20

---

## 一句话理解

**以前，看图是看图模型的事，生图是扩散模型的事，改图要搭一套 inpainting pipeline。SenseNova U1.5 把这三件事塞进同一个 8B 参数的模型里，权重一份，推理一次。**

---

## 这件事为什么难

多模态统一的难点不在于"接入"，而在于"原生"。

把一个视觉编码器插在 LLM 前面，再接一个扩散解码器，三个模块各自保留原有的权重空间——这是"拼装"，不是"统一"。拼装方案在推理时要分别过三个模型，共享信息靠中间向量，理解和生成之间的特征对齐难以端到端优化。

SenseNova 团队的做法是从架构层就做统一，提出 **NEO-unify** 范式：不引入单独的视觉 tokenizer 或扩散解码器，而是在统一的 token 序列上同时完成理解与生成，靠 **MoT（Mixture of Tokens）** 机制处理离散文本 token 和连续图像 patch 之间的异构性。核心论点是：理解和生成共享同一套表征，才能真正互相增强，而不是互相干扰。

---

## U1.5 比 U1 改了什么

U1 在 2026-04-27 发布（8B MoT）。U1.5 在 2026-08-20 发布，是在 NEO-unify 架构不变的基础上，针对用户最直接感知的质量维度做了定向优化：

| 维度 | 改进重点 |
|------|----------|
| **图像生成质量** | 构图、色彩协调更自然；材质渲染、光照更真实；局部细节更锐利 |
| **文字与信息图** | 中英文文字可读性提升；海报、品牌资产、数据图中信息层级更清晰 |
| **原生 4K 生成** | 全局结构与色彩在高分辨率下更稳定；生成效率同步提升 |
| **图像编辑可靠性** | 局部编辑、文字替换、多参考插入、替换操作对未编辑区域的保护更强 |
| **复杂指令跟随** | 数量、空间关系、布局、风格等多约束的执行一致性提升 |
| **视觉控制精度** | 边界框、视觉标记、单/多图参考的区域级控制更准确 |

U1.5 还同步发布了 **LoRA-8step** 变体，8 步推理在大多数场景下质量接近完整模型，适合对延迟敏感的场景。

---

## MoT：混合 Token 如何工作

传统视觉-语言模型用两条路：离散化图像（VQ-VAE 把图像变成离散 token）或者连续嵌入（patch embedding 插入 LLM，但生成时还要回到扩散模型）。两种路各有损耗。

MoT 在同一个注意力序列里混合两种 token：
- **文本/理解 token**：离散，走普通 embedding
- **图像/生成 patch**：连续，直接参与注意力运算

模型在训练时同时见到"读图 → 答文字"和"读文字 → 生成图像"两类任务，强制对齐两类 token 的语义空间。编辑任务（"把左边那个人的夹克改成亮黄色，保留背景和姿势"）则同时需要理解能力（定位目标）和生成能力（渲染新纹理），在统一空间里天然衔接。

---

## 能力范围

U1.5 在一套推理端点下支持：

**图像生成**
```bash
python examples/t2i/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --prompt "A cinematic mountain lake at sunrise, realistic photography." \
  --width 2048 --height 2048 --output output.png
```

**图像编辑**
```bash
python examples/editing/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --image input.png \
  --prompt "Change the jacket to cobalt blue. Preserve the face, pose, background, lighting." \
  --output edited.png
```

**图文交错生成**（教程、故事插图）
```bash
python examples/interleave/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --prompt "I want to learn how to cook tomato and egg stir-fry. Please give me a beginner-friendly illustrated tutorial." \
  --resolution "16:9" --output_dir outputs/interleave/
```

**视觉问答**
```bash
python examples/vqa/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT ...
```

环境要求：Python 3.11，PyTorch 2.8，CUDA 12.8；支持 GGUF 量化和 VRAM 层卸载，低显存单 GPU 可跑。

---

## 已知局限

官方文档列出了几个目前仍存在的挑战，值得在生产中注意：

- **颜色过饱和**：部分 prompt 会产生过度高频细节或颜色过饱和，降低 `cfg_scale` 通常有效
- **密集文字错误**：长段密集或中英混排小号文字仍有误差
- **严格约束布局**：精确计数、对齐、层级在高度约束的版式中仍不稳定
- **人物细节**：小脸、手部、四肢、精细物体结构有时不稳定
- **复杂编辑漂移**：多轮、多区域保留的复合编辑可能产生漂移

---

## 周边生态

U1 系列发展时间不到 4 个月，已经形成了相当完整的生态：

- **Infographic 专版**（U1-8B-MoT-Infographic-V3）：专攻信息图生成和编辑，保留完整 T2I 能力
- **Interleaved 专版**（U1-8B-MoT-Interleaved）：优化多页图文叙事的一致性
- **LoRA 加速变体**：8 步推理，质量与基础模型接近
- **GGUF 量化**（社区维护）：Q8 约 19.9GB，低显存可用
- **ComfyUI 工作流**：官方提供 Infographic 系列工作流 JSON
- **SenseNova-Studio**：免费在线体验，无需安装 GPU

---

## 为什么值得关注

图像的"看、生、改"是三件独立的工程任务，行业里长期的解法是三套独立模型加胶水层。SenseNova U1.5 做的事情是把这三层合并成一个权重：不是集成，是融合。

8B 参数在统一范式下完成这三件事，并在 benchmark 上跑出有竞争力的数字，同时 Apache 2.0 开源、支持商用，这个组合在 2026 年 8 月中旬之前几乎没有对手。

对于需要在自己的应用里同时处理图像理解和视觉创作的团队来说，换成一个推理端点就能搞定三件事，工程成本的降幅是实质性的。

---

**相关链接**

- GitHub：https://github.com/OpenSenseNova/SenseNova-U1
- HuggingFace：https://huggingface.co/sensenova/SenseNova-U1.5-8B-MoT
- HuggingFace 合集：https://huggingface.co/collections/sensenova/sensenova-u15
- 论文：https://arxiv.org/abs/2605.12500
- 在线 Demo：https://unify.light-ai.top/
- 架构博客：https://huggingface.co/blog/sensenova/neo-unify
- ModelScope：https://modelscope.cn/models/SenseNova/SenseNova-U1.5-8B-MoT

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## SenseNova U1.5: Image Understanding, Generation, and Editing — One Model

*by Mycelium Protocol*

---

GitHub: OpenSenseNova/SenseNova-U1 ⭐ 5,436 | Forks 446 | Apache 2.0  
HuggingFace: sensenova/SenseNova-U1.5-8B-MoT  
ModelScope: SenseNova/SenseNova-U1.5-8B-MoT  
Paper: arXiv 2605.12500  
Demo: https://unify.light-ai.top/  
Released: 2026-08-20

---

### The One-Line Version

**Until now, image understanding was a VLM's job, generation was a diffusion model's job, and editing required a whole inpainting pipeline. SenseNova U1.5 puts all three into a single 8B-parameter model — one set of weights, one inference call.**

---

### Why This Is Hard

The difficulty of multimodal unification isn't in "connecting" modalities — it's in doing it natively.

Plugging a vision encoder in front of an LLM and tacking on a diffusion decoder is assembly, not unification. The three modules retain separate weight spaces; information sharing happens through intermediate vectors; the feature alignment between understanding and generation can't be end-to-end optimized.

SenseTime's approach is architectural. **NEO-unify** handles understanding and generation on a unified token sequence without separate vision tokenizers or diffusion decoders. **MoT (Mixture of Tokens)** handles the heterogeneity between discrete text tokens and continuous image patches — both live in the same attention sequence. The core argument: understanding and generation share representation space and actually reinforce each other, rather than competing.

---

### What U1.5 Changes Over U1

U1 launched 2026-04-27. U1.5 landed 2026-08-20 — same NEO-unify architecture, targeted improvements on the six dimensions users feel most directly:

| Dimension | Changes |
|-----------|---------|
| **Image generation quality** | Better composition, color harmony, material rendering, lighting, and local detail |
| **Text & infographic generation** | More legible Chinese and English text; cleaner hierarchy in posters, brand assets, data charts |
| **Native 4K generation** | More stable global structure and color at high resolution; improved efficiency |
| **Image editing reliability** | Stronger preservation of unedited regions across local, text, multi-reference, insertion, and replacement edits |
| **Complex instruction following** | More consistent execution of counts, spatial relationships, layouts, styles, and multi-constraint prompts |
| **Visual control precision** | More accurate region- and object-level control via bounding boxes, visual markers, single/multi-image references |

U1.5 also ships a **LoRA-8step** variant — 8-step inference at quality close to the base model for latency-sensitive applications.

---

### MoT: How Mixed Tokens Work

Traditional vision-language models follow one of two paths: discretize images (VQ-VAE into discrete tokens) or use continuous embeddings (patch embedding into an LLM, but then generation requires a separate diffusion pass). Both paths have losses.

MoT mixes two token types in the same attention sequence:
- **Text / understanding tokens**: discrete, processed through standard embeddings
- **Image / generation patches**: continuous, participating directly in attention

Training exposes the model simultaneously to "read image → answer in text" and "read text → generate image" tasks, forcing the alignment of both token types' semantic spaces. Editing tasks ("change the jacket on the left person to bright yellow, preserve background and pose") naturally chain the two: understanding to localize the target, generation to render the new texture — both in the same unified space.

---

### What It Can Do

One model, one inference endpoint, four task types:

**Text-to-Image**
```bash
python examples/t2i/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --prompt "A cinematic mountain lake at sunrise, realistic photography." \
  --width 2048 --height 2048 --output output.png
```

**Image Editing**
```bash
python examples/editing/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --image input.png \
  --prompt "Change the jacket to cobalt blue. Preserve the face, pose, background, lighting." \
  --output edited.png
```

**Interleaved Image-Text Generation** (tutorials, illustrated stories)
```bash
python examples/interleave/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT \
  --prompt "Give me a beginner-friendly illustrated tutorial for tomato and egg stir-fry." \
  --resolution "16:9" --output_dir outputs/interleave/
```

**Visual Question Answering**
```bash
python examples/vqa/inference.py \
  --model_path sensenova/SenseNova-U1.5-8B-MoT ...
```

Requirements: Python 3.11, PyTorch 2.8, CUDA 12.8. GGUF quantization and VRAM layer offloading are supported for low-VRAM single-GPU inference.

---

### Known Limitations

Official documentation flags these remaining challenges:

- **Oversaturated colors**: some prompts produce excessive high-frequency detail or oversaturation — reducing `cfg_scale` usually helps
- **Dense text errors**: long, small, or mixed Chinese-English text at high density still makes mistakes
- **Constrained layouts**: exact counts, alignment, and hierarchy are imperfect under tight layout constraints
- **Human details**: small faces, hands, limbs, and fine-grained object structures remain unstable at times
- **Complex editing drift**: broad, multi-turn, or multi-region edits may drift when many areas must be preserved simultaneously

---

### Ecosystem

The U1 series has built a substantial ecosystem in under four months:

- **Infographic variant** (U1-8B-MoT-Infographic-V3): specialized for infographic generation and editing while retaining full T2I capability
- **Interleaved variant** (U1-8B-MoT-Interleaved): optimized for multi-page image-text narrative coherence
- **LoRA acceleration**: 8-step inference close to base model quality
- **GGUF quantization** (community-maintained by @smthemex): Q8 at ~19.9GB for low-VRAM use
- **ComfyUI workflows**: official Infographic workflow JSON included
- **SenseNova-Studio**: free browser playground, no GPU required

---

### Why It Matters

Image understanding, generation, and editing have been three separate engineering tasks, each requiring its own model and the glue code between them. SenseNova U1.5's contribution is collapsing those three layers into one set of weights — not integration, but fusion.

An 8B model handling all three tasks at competitive benchmark scores, Apache 2.0 licensed and commercially usable, had essentially no equivalent as of mid-August 2026. For teams that need to handle both image understanding and visual creation in the same application, getting it done with a single inference endpoint is a substantial reduction in system complexity.

---

**Links**

- GitHub: https://github.com/OpenSenseNova/SenseNova-U1
- HuggingFace: https://huggingface.co/sensenova/SenseNova-U1.5-8B-MoT
- HuggingFace collection: https://huggingface.co/collections/sensenova/sensenova-u15
- Paper: https://arxiv.org/abs/2605.12500
- Live Demo: https://unify.light-ai.top/
- Architecture blog: https://huggingface.co/blog/sensenova/neo-unify
- ModelScope: https://modelscope.cn/models/SenseNova/SenseNova-U1.5-8B-MoT

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
