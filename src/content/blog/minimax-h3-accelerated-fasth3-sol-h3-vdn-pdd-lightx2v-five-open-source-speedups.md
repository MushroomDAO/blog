---
title: 'MiniMax H3 加速五件套：稀疏注意力、混合注意力、并行解码，15 秒视频压进 6.6 秒'
titleEn: "MiniMax H3 Accelerated: Five Open-Source Speedups — Sparse Attention, Hybrid Attention, Parallel Decoding"
description: "MiniMax 官方 Spotlight 点名五个开源加速方案：FastH3（VSA 4步蒸馏）、Sol-H3（免训练动态稀疏+fused kernel）、VDN（混合线性+softmax注意力）、PDD（并行解码头蒸馏）、LightX2V Turbo（DMD LoRA）。8×B300 将 15 秒视频压进 6.6 秒；DGX Spark 两阶段 Pipeline 在桌面级硬件上完成 1344×768 多模态生成。"
descriptionEn: "MiniMax's official spotlight names five open-source acceleration projects: FastH3 (VSA 4-step distillation), Sol-H3 (training-free dynamic sparse + fused kernels), VDN (hybrid linear+softmax attention), PDD (parallel decoding head distillation), LightX2V Turbo (DMD LoRA). On 8×B300 this compresses a 15-second clip to 6.6s; DGX Spark's two-stage pipeline delivers 1344×768 multimodal generation on desktop-class hardware."
pubDate: "2026-09-15"
updatedDate: "2026-09-15"
category: "Tech-News"
tags: ["MiniMax-H3", "video-generation", "open-source", "sparse-attention", "distillation", "NVIDIA", "acceleration", "AI-video"]
heroImage: "../../assets/images/minimax-h3-accelerated-fasth3-sol-h3-vdn-pdd-lightx2v-five-open-source-speedups-banner.jpg"
---

> 📌 来源：MiniMax "H3, ACCELERATED." Community / Technical Spotlight
> 关联仓库：hao-ai-lab/FastVideo · NVlabs/Sana(sol-engine) · OpenVDN/vdn-minimax-h3 · alibaba-pai/MiniMax-H3-Acc-LoRAs · ModelTC/lightx2v

---

MiniMax 发布了一张社区技术 Spotlight 海报，标题是 **"H3, ACCELERATED."**，副标题是："更少步数、更智能的注意力、更快的系统。"

海报点名五个开源加速项目。这篇文章逐一拆解它们在做什么、为什么快、以及各自的独特之处。

---

## 背景：H3 为什么需要加速

MiniMax H3 是一个同时生成视频和同步立体音频的多模态扩散模型（DiT 架构）。多模态意味着音视频 token 一起参与注意力计算——序列更长、显存压力更大、每步推理开销更高。

加速 H3 的难点和加速纯视频模型不完全一样：不能把音频 branch 随意剪掉，稀疏化要同时覆盖视频 token 和音频 token，蒸馏要保住音视频同步关系。

五个项目分别从不同角度切入这个问题。

---

## 一、FastH3：训练一个"注意力门卫"

**来源**：FastVideo（Hao AI Lab）· Nuva Lab · NVIDIA
**GitHub**：hao-ai-lab/FastVideo · ~4K stars · Apache-2.0

FastH3 的方法是：不让所有 token 都参与注意力，而是训一个轻量评分层，只让"最重要的"token 块参与计算。

**VSA（Video Sparse Attention）的实现**：

给 H3 每个 Transformer block 加入一个 `to_gate_compress` 层——用很小的代价给每个 64-token block 打一个重要性分数，然后只让得分最高的 top-K 个 block 参与完整 attention 计算，其余直接跳过。这样约 **90% 的 attention 计算量被跳过**。

关键区别：这个评分层是**通过蒸馏训出来的**，不是规则或阈值。模型学会了什么位置的信息真正重要，不是靠局部窗口规则猜。

**FastH3 Preview v1**：4步推理，DMD2 蒸馏（Distribution Matching Distillation v2），90% 稀疏注意力。支持的硬件：H100/A100/RTX 4090/DGX Spark/Apple Silicon。

这是五个项目里训练开销最重的——VSA 评分层需要从原始 H3 蒸馏。代价换来的是：稀疏化精准，而不是简单地跳过"离得远的 token"。

---

## 二、Sol-H3：免训练的"运行时稀疏"

**来源**：NVIDIA SANA / Sol-Engine
**GitHub**：NVlabs/Sana，分支 sol-engine
**ComfyUI**：quzopl/ComfyUI-SolAttn-H3

Sol-H3 的关键词是"无需重训练"。FastH3 的 VSA 需要蒸馏一个评分层；Sol-Attn 不需要。

**Sol-Attn（Sparsified On-the-fly Attention）**的逻辑：在推理时动态决定哪些 attention block 可以跳过——"on-the-fly"就是实时决策。没有额外的训练步骤，不需要修改模型权重。

但 Sol-H3 的加速不仅来自稀疏注意力——还有：
- **Fused kernels**：把多个 GPU 计算操作合并成一个 kernel 调用，减少 GPU 调度开销
- **Multi-GPU 并行**：在多卡环境下优化通信和计算重叠
- **并行视频解码**：音视频 decode 和推理过程重叠执行

这几个优化叠加在一起，在 NVIDIA 的测试里，8×GB200 比 Diffusers 快 **3.95×**，比 SGLang 快 **2.80×**。

**Spotlight 上展示的关键数字**：同一段 1344×768、24 FPS、4 步推理的 15 秒视频，Sol-H3 在 8×B300 上压进了 **6.6 秒**（warm inference，不含模型加载和编码）。

桌面级别的数字：RTX 5090（SM120）**4.52×**，DGX Spark **3.92×**。

ComfyUI 版本 quzopl/ComfyUI-SolAttn-H3 使用 CuTe DSL 实现 kernel，支持 SM89/90/100/120（Ada 到 Blackwell 全覆盖）。

---

## 三、VDN：把注意力"按距离分工"

**来源**：OpenVDN · Haocheng Xi & collaborators
**GitHub**：OpenVDN/vdn-minimax-h3
**License**：Apache-2.0（代码）+ MiniMax-H3 Community License（权重）

VDN（VideoDeltaNet-H3）解决的是一个具体问题：**softmax attention 在长序列下是二次复杂度的**，这在长视频 clip 里是推理速度的主要瓶颈。

**混合线性+softmax 注意力的分工逻辑**：

- 近帧之间的关系：用**局部滑动窗口 softmax attention**——近帧内容相关性强，需要精确的局部注意力
- 跨帧的长程上下文：用**Delta 线性注意力**——线性复杂度，维护一个随时间更新的状态矩阵，而不是做完整的二次点积

结果是把二次开销转移到线性，只在最需要精度的局部窗口内保留 softmax。

**实现细节**：VDN 以 H3 原始 backbone 为基础，加入独立的线性 attention branch 和两个小 LoRA 适配器。LoRA 权重在推理时可以合并进 backbone，不增加推理路径上的模块数量。

**开源内容**：训练代码和推理代码同时开放——这在加速工作里不常见，大多数只发权重。支持 T2VA / I2VA / FL2VA / L2VA。

已合并入 SGLang（PR #37903），Diffusers 支持也在追踪中（issue #14700）。

---

## 四、PDD：一次前向预测多个时间步

**来源**：NVIDIA method · Alibaba PAI adapters
**HuggingFace**：alibaba-pai/MiniMax-H3-Acc-LoRAs
**arXiv**：2607.26004

PDD（Parallel Decoding Distillation）的思路和前三个不同——前三个都在优化每一步推理的计算量，PDD 在减少总步数的同时还让每步"更值"。

**并行解码头 bank 的原理**：

标准扩散模型每步推理：前向过一次，预测当前时间步的噪声或速度向量。PDD 在模型最后一层加入 **32 个 per-interval 投影头**（head bank），每组头对应不同的时间步区间。一次前向可以同时预测多个时间步的输出，而不需要串行地走完每一步。

无 CFG（Classifier-Free Guidance）——蒸馏版本不需要无条件分支，进一步减少每次前向的计算量。

**Alibaba PAI 的适配器**：把 PDD 方法适配到 H3 的 LoRA 形式，提供 4 步和 8 步两个精度档位。32 个投影头作为轻量 LoRA 挂上原始 H3，不需要修改 backbone 权重。

---

## 五、LightX2V Turbo：DMD LoRA，覆盖全任务类型

**来源**：ModelTC / LightX2V
**GitHub**：ModelTC/lightx2v · ~2.8K stars · Apache-2.0
**HuggingFace**：lightx2v/Minimax-h3-Turbo
**推理框架 repo**：ModelTC/Minimax-H3-Turbo

LightX2V 是一个通用的轻量视频推理框架，LightX2V Turbo 是它专门为 H3 发布的 DMD LoRA 系列。

**DMD（Distribution Matching Distillation）的逻辑**：让学生模型在少步推理时的输出分布，尽可能匹配教师模型（原始 H3）在完整步数下的输出分布。不需要逐步配对，直接在分布层面对齐。

**技术参数**（4步 768p v1.0）：
```
video_flow_shift=6    # 视频 flow schedule 参数
audio_flow_shift=3    # 音频 flow schedule 参数（与视频不同）
LoRA alpha=128        # LoRA 缩放系数
无 CFG                # 推理时不需要无条件分支
```

音视频 flow shift 参数不同——这是 H3 多模态特性的体现：视频和音频的扩散过程在时间步上的推进速率不一样，蒸馏时要分开设置。

**任务覆盖**：T2AV（文本→音视频）/ I2AV（图像→音视频）/ L2AV（延伸生成）/ FL2AV（首尾帧→中间）/ Ref2AV（参考视频）——五种任务类型全覆盖。

LightX2V 框架本身还支持 block-level offloading（显存受限设备用）、tensor 并行、量化推理，Turbo LoRA 装在这个框架上可以在不同硬件配置下灵活调整。

---

## 两阶段 Pipeline：DGX Spark 上的完整工作流

Spotlight 右下角还展示了一个 DGX Spark 上的两阶段 pipeline：

```
H3 草稿（384p，4 步）→ LTX-2.5 精修（768p，3 步）
```

第一阶段用 H3 生成低分辨率草稿，快速确认构图、内容、音视频对齐；第二阶段用 LTX-2.5 Refine 做分辨率提升和细节精修。

整个流程从 DGX Spark（GB200 桌面工作站）上跑完，不是数据中心专属配置。这是"桌面级多模态视频生成"的一种实现路径。

---

## 四类方法横向对比

| 项目 | 加速思路 | 需要重训练 | 主要适用场景 |
|------|---------|-----------|------------|
| FastH3 VSA | 训练评分层 → 稀疏 attention | 是（蒸馏） | 精准稀疏、长期效果稳定 |
| Sol-H3 Sol-Attn | 运行时动态稀疏 + fused kernel | 否 | 快速部署、多硬件覆盖 |
| VDN | 近帧 softmax + 跨帧线性混合 | 是（轻量 LoRA） | 长 clip、降二次复杂度 |
| PDD | 并行解码头预测多时间步 | 是（head bank LoRA） | 减总步数 × 每步多出 |
| LightX2V Turbo | DMD 分布对齐蒸馏 | 是（LoRA） | 多任务覆盖、灵活框架 |

Sol-H3 是五个里唯一"免训练"的。其余四个都需要某种形式的蒸馏或微调，但都以 LoRA 或轻量头的形式挂上原始 H3，不需要动 backbone。

---

## 拆解结论

这五个项目出现在同一张 Spotlight 上，说明 MiniMax 在 H3 的加速上采取的是"多路并行、社区共赢"策略——没有把加速做成内部专有方案，而是接纳来自 NVIDIA、高校、阿里巴巴 PAI、以及独立开发者的多种路径。

对于使用者来说，这意味着：
- **显存受限、不想改模型**：Sol-H3（免训练，随装随用）
- **追求最精准的稀疏化**：FastH3 VSA（有代价，效果可控）
- **长 clip 推理**：VDN（线性复杂度应对长序列）
- **极致步数减少**：PDD（4步/8步，并行解码头）
- **需要全任务覆盖**：LightX2V Turbo（五种任务类型）

MiniMax H3 的"开放权重 + 社区加速"模式，让同一个基础模型在一个多月内就有了五套可用的加速路径。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Source: MiniMax "H3, ACCELERATED." Community / Technical Spotlight
> Related repos: hao-ai-lab/FastVideo · NVlabs/Sana(sol-engine) · OpenVDN/vdn-minimax-h3 · alibaba-pai/MiniMax-H3-Acc-LoRAs · ModelTC/lightx2v

---

MiniMax published a community technical spotlight titled **"H3, ACCELERATED."** with the tagline: "Fewer steps. Smarter attention. Faster systems."

The spotlight names five open-source acceleration projects. This article breaks down what each one does, why it's faster, and what makes it distinctive.

---

## Background: Why H3 Needs Acceleration

MiniMax H3 is a multimodal diffusion model (DiT architecture) that simultaneously generates video and synchronized stereo audio. Multimodal means audio and video tokens participate in attention together — longer sequences, higher memory pressure, more expensive inference per step.

Accelerating H3 is different from accelerating a pure video model: you can't simply prune the audio branch, sparsification must cover both video and audio tokens, and distillation must preserve audio-video synchronization.

Five projects attack this from different angles.

---

## I. FastH3: Training an "Attention Gatekeeper"

**From**: FastVideo (Hao AI Lab) · Nuva Lab · NVIDIA
**GitHub**: hao-ai-lab/FastVideo · ~4K stars · Apache-2.0

FastH3's approach: don't let all tokens participate in attention. Instead, train a lightweight scoring layer that identifies which 64-token blocks actually matter.

**How VSA (Video Sparse Attention) works:**

Each H3 Transformer block gains a `to_gate_compress` layer — a cheap scoring mechanism that evaluates each 64-token block's importance and only lets the top-K scoring blocks participate in full attention. The rest are skipped, eliminating roughly **90% of attention computation**.

The key difference: the scoring layer is **learned through distillation**, not based on rules or thresholds. The model learns where information actually matters — it doesn't guess based on local windows.

**FastH3 Preview v1**: 4-step inference, DMD2 distillation (Distribution Matching Distillation v2), 90% sparse attention. Hardware support: H100/A100/RTX 4090/DGX Spark/Apple Silicon.

Of the five, this requires the heaviest training investment — the VSA scoring layer needs distillation from the original H3. The payoff: precise sparsification, not just "skip distant tokens."

---

## II. Sol-H3: Training-Free "Runtime Sparsification"

**From**: NVIDIA SANA / Sol-Engine
**GitHub**: NVlabs/Sana, branch sol-engine
**ComfyUI**: quzopl/ComfyUI-SolAttn-H3

Sol-H3's key phrase is "no retraining required." FastH3's VSA needs to distill a scoring layer; Sol-Attn doesn't.

**Sol-Attn (Sparsified On-the-fly Attention):** decides at inference time which attention blocks to skip — "on-the-fly" means real-time decisions. No extra training steps, no model weight modifications.

But Sol-H3's speedup comes from more than just sparse attention:
- **Fused kernels**: combine multiple GPU compute operations into single kernel calls, reducing scheduling overhead
- **Multi-GPU parallelism**: optimized communication and compute overlap across cards
- **Parallel video decoding**: audio/video decode overlaps with the inference process

These optimizations together produce — in NVIDIA's testing — **3.95× over Diffusers** and **2.80× over SGLang** on 8×GB200.

**The Spotlight's headline number**: a 1344×768, 24 FPS, 4-step, 15-second clip completed in **6.6 seconds** on 8×B300 (warm inference, excluding model loading and encoding).

Desktop numbers: RTX 5090 (SM120) **4.52×**, DGX Spark **3.92×**.

The ComfyUI version (quzopl/ComfyUI-SolAttn-H3) implements kernels in CuTe DSL, supporting SM89/90/100/120 — full Ada through Blackwell coverage.

---

## III. VDN: Splitting Attention "by Distance"

**From**: OpenVDN · Haocheng Xi & collaborators
**GitHub**: OpenVDN/vdn-minimax-h3
**License**: Apache-2.0 (code) + MiniMax-H3 Community License (weights)

VDN (VideoDeltaNet-H3) addresses a specific bottleneck: **softmax attention is quadratic in sequence length**, which dominates inference time in long clips.

**The hybrid linear+softmax division of labor:**

- Nearby frame relationships: **local sliding-window softmax attention** — high correlation between nearby frames requires precise local attention
- Long-range cross-frame context: **Delta linear attention** — linear complexity, maintains a state matrix updated over time rather than computing full quadratic dot products

This shifts quadratic cost to linear, keeping softmax only where precision actually matters — within local windows.

**Implementation details**: VDN adds an independent linear attention branch and two small LoRA adapters on top of the original H3 backbone. The LoRA weights can be merged into the backbone at inference time, adding no extra modules to the inference path.

**What's open**: both training code and inference code — unusually, most acceleration work releases only weights. Supports T2VA / I2VA / FL2VA / L2VA.

Already merged into SGLang (PR #37903). Diffusers support tracked in issue #14700.

---

## IV. PDD: One Forward Pass, Multiple Timestep Predictions

**From**: NVIDIA method · Alibaba PAI adapters
**HuggingFace**: alibaba-pai/MiniMax-H3-Acc-LoRAs
**arXiv**: 2607.26004

PDD (Parallel Decoding Distillation) takes a different approach from the first three. Those optimize computation per step; PDD reduces total steps while making each step "worth more."

**How the parallel decoding head bank works:**

Standard diffusion: one forward pass predicts one timestep's noise or velocity vector. PDD adds **32 per-interval projection heads** (a head bank) to the model's final layer. Each head set corresponds to a different timestep interval. One forward pass simultaneously predicts outputs for multiple timesteps — eliminating the need to run each serially.

No CFG (Classifier-Free Guidance) — the distilled version doesn't need an unconditional branch, further reducing per-step cost.

**Alibaba PAI's adapters**: adapt the PDD method to H3 in LoRA form, with 4-step and 8-step accuracy tiers. The 32 projection heads attach as lightweight LoRAs on the original H3 without touching the backbone.

---

## V. LightX2V Turbo: DMD LoRA Across All Task Types

**From**: ModelTC / LightX2V
**GitHub**: ModelTC/lightx2v · ~2.8K stars · Apache-2.0
**HuggingFace**: lightx2v/Minimax-h3-Turbo

LightX2V is a general-purpose lightweight video inference framework. LightX2V Turbo is its H3-specific DMD LoRA series.

**DMD (Distribution Matching Distillation):** trains the student model so that its output distribution at few steps matches the teacher model's (original H3) distribution at full steps. No step-by-step pairing needed — alignment happens directly at the distribution level.

**Technical parameters** (4-step 768p v1.0):
```
video_flow_shift=6    # video flow schedule parameter
audio_flow_shift=3    # audio flow schedule (differs from video)
LoRA alpha=128        # LoRA scaling factor
no CFG                # no unconditional branch at inference
```

The different video/audio flow shift values reflect H3's multimodal design: the diffusion processes for video and audio advance at different rates through timesteps, so distillation requires separate scheduling.

**Task coverage**: T2AV (text-to-audio-video) / I2AV (image-to-audio-video) / L2AV (extend generation) / FL2AV (first-last frame to middle) / Ref2AV (reference video) — five task types covered.

The LightX2V framework also supports block-level offloading (for memory-constrained devices), tensor parallelism, and quantized inference. The Turbo LoRA on this framework adapts flexibly across different hardware configurations.

---

## Two-Stage Pipeline: DGX Spark Workflow

The Spotlight also shows a two-stage pipeline running on DGX Spark:

```
H3 draft (384p, 4 steps) → LTX-2.5 refine (768p, 3 steps)
```

Stage one: H3 generates a low-resolution draft quickly — confirming composition, content, and audio-video alignment. Stage two: LTX-2.5 Refine handles upscaling and detail refinement.

The full workflow runs on DGX Spark (a GB200 desktop workstation) — not a data-center-only configuration. This represents one viable implementation path for "desktop-class multimodal video generation."

---

## Four Approaches, Side by Side

| Project | Acceleration approach | Needs training | Best for |
|---------|----------------------|---------------|---------|
| FastH3 VSA | Trained scoring layer → sparse attention | Yes (distillation) | Precise sparsification, stable quality |
| Sol-H3 Sol-Attn | Runtime dynamic sparse + fused kernels | No | Fast deployment, multi-hardware |
| VDN | Local softmax + long-range linear hybrid | Yes (lightweight LoRA) | Long clips, quadratic → linear complexity |
| PDD | Parallel decoding head predicts multi-step | Yes (head bank LoRA) | Fewer total steps, each step predicts more |
| LightX2V Turbo | DMD distribution matching distillation | Yes (LoRA) | Full task coverage, flexible framework |

Sol-H3 is the only training-free option. The other four require some form of distillation or fine-tuning, but all attach as LoRA or lightweight heads — none require touching the H3 backbone.

---

## Teardown Summary

These five projects appearing on the same Spotlight reflects MiniMax's strategy for H3 acceleration: multi-path community collaboration rather than keeping acceleration proprietary. The contributors span NVIDIA, academic labs, Alibaba PAI, and independent developers.

For users, this translates to real choices:
- **Memory-constrained, don't want to modify the model**: Sol-H3 (training-free, ready immediately)
- **Best sparsification precision**: FastH3 VSA (has training cost, controllable output)
- **Long-clip inference**: VDN (linear complexity for long sequences)
- **Minimum step count**: PDD (4- or 8-step parallel decoding heads)
- **Need full task type coverage**: LightX2V Turbo (five task types)

MiniMax H3's "open weights + community acceleration" model produced five usable acceleration paths for the same base model within about one month of release.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
