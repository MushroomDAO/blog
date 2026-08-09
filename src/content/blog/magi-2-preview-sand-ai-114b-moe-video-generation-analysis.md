---
title: "MAGI-2 Preview 深度解析：114B MoE 视频生成，激活参数仅 6B，完整自部署指南"
titleEn: "MAGI-2 Preview Deep Dive: 114B MoE Video Generation on Only 6B Active Params, with a Full Self-Hosting Guide"
description: "Sand.ai 开源 MAGI-2 Preview：全球首个千亿级 MoE 视频生成模型，114B 总参数，单 token 激活仅 6B，统一音视频生成，Apache 2.0。文章深度拆解 MagiMoE 架构、数据管道哲学与成本逻辑，并给出完整自部署方案：硬件选型、权重下载、环境搭建、推理命令、成本估算全覆盖。"
descriptionEn: "Sand.ai open-sources MAGI-2 Preview: a 114B MoE video generation model that activates only 6B parameters per token, with unified audio-video synthesis. This analysis covers the MagiMoE architecture, data pipeline philosophy, and cost math — plus a complete self-hosting guide: hardware selection, weights download, environment setup, inference commands, and cost estimates."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Research"
tags: ["MAGI-2", "Sand.ai", "视频生成", "MoE", "开源模型", "AI基础设施", "自部署", "Mycelium"]
heroImage: "../../assets/images/magi-2-preview-sand-ai-114b-moe-video-generation-analysis-banner.jpg"
---

*by Mycelium Protocol*

---

一个数字让这件事值得认真对待：**114B 总参数，单次生成只激活 6B**。

这不是压缩，也不是量化，而是架构上的稀疏激活——每次生成调用的计算量只有参数总量的 5.3%。Sand.ai 把这套设计开源了（Apache 2.0），权重放在 Hugging Face，推理代码放在 GitHub。

---

## Sand.ai 是谁

Sand.ai 是一家专注视频生成的 AI 公司，2025 年以 MAGI-1（自回归视频生成）进入公众视野。MAGI-1 把视频切分成时间块，用自回归去噪建模时间因果关系，支持流式生成和视频续写。

MAGI-2 换了一个更根本的问题：**视频生成模型应该怎么扩展规模？**

---

## 架构：为什么 114B 里只激活 6B

### 单流 Transformer：文本 + 视频 + 音频全合并

MAGI-2 的基础是 MagiHuman 验证过的单流设计。文本、视频、音频三个模态合并成一条统一 token 序列，全部走同一个 Transformer backbone，只用 self-attention，没有多模态塔、没有 cross-attention 接口。

这个选择有具体动机：语言、唇形、肢体动作、环境音、音乐、镜头节奏是持续相互依赖的。放在同一序列里，它们可以在整个 backbone 里随时交换信息，而不只在预设的几个接口点相遇。

### MagiMoE：Ultra-Fine-Grained 的专家路由

单流接口确定后，扩展容量的问题来了。直接用密集 Transformer（Dense Transformer）在两个地方碰壁：

1. **训练基础设施**：100B 级别下，每个 token 都要过完整参数，通信开销、显存占用、梯度同步代价急剧上升
2. **推理成本**：视频生成 token 量比文本多得多，每步去噪都要跑完整大模型，延迟和服务成本直接不可用

MoE 给出了一条出路：把 FFN 容量组织成专家池，每个 token 只激活其中一小部分。核心公式：

- 密集模式计算量：`F_dense ∝ N × P_total`
- MoE 模式计算量：`F_MoE ∝ N × P_active`，而 `P_active ≪ P_total`

**MAGI-2 Preview 的具体配置**：

| 组件 | 配置 |
|------|------|
| Backbone | 40 层 Transformer |
| 稀疏核心 | 中间 36 层使用 Multi-Head MoE；边界 4 层保持密集 |
| 模型宽度 | 3,072 |
| 路由表示 | 12 头 × 256 维 |
| 每头专家池 | 256 个专家 |
| 每头激活 | Top-6 |
| 每层总专家单元 | 12 × 256 = 3,072 个 |
| 每 token 激活单元 | 12 × 6 = 72 个 |

这 3,072 个专家不是全宽 FFN——每个专家只在 256 维子空间里操作。不同 token 的不同表示子空间可以独立选择专家组合，而不是把完整 hidden state 发给一个不可分割的大专家。

### Head Parallel：解决标准 MoE 的通信爆炸

标准 MoE 的主导通信项是：`C ∝ N × k × H`——token 越多（视频天然长序列）、激活专家越多、每次通信 payload 越大，开销越高。

MAGI-2 改用 Multi-Head LatentMoE + Head Parallel：跨节点只传 head 分片，通信量变成 `C ∝ N × H`，不再随 k 增长。更重要的是，跨设备的 send/receive shape 由 head 分片静态决定，可以提前分配 buffer，消除了标准 MoE 的动态通信不规则性。

### MagiMuon：理解 Head × Expert 结构的优化器

MAGI-2 的专家权重自然形成一个 `head × expert` 索引的小矩阵批次，而不是一个大矩阵。MagiMuon 保留这个结构布局，对每个小矩阵独立做 Muon 正交化，把矩阵批次分散到不同 rank 上平衡优化器计算。

---

## 数据管道：打破「过滤陷阱」

MAGI-2 在数据端做了一个根本性的方向转变，值得单独说。

### 过滤陷阱

早期小模型（~7B）能力有限，社区为了产出稳定演示，自然倾向于过滤数据：留下主体清晰、运动简单、镜头稳定的视频，删掉模型难以学习的样本。

但这在模型扩大时会反噬：**你训练大模型用的数据，却是根据小模型的能力边界精简过的**。大模型的潜在上限被数据本身封住了。

Sand.ai 把这叫做「数据过滤陷阱」：当训练数据持续被简化以适配当前模型，数据本身成了更强模型的能力天花板。

### 从过滤为主 → 高通量生产 + 精准标注

MAGI-2 转向了另一个逻辑：必要的数据治理（安全、合规、隐私、严重损坏、去重）继续做，但「模型是否容易生成」不再是主要准入标准。

能留的都留：复杂运动、多人交互、镜头切换、长尾主体、字幕、屏幕文字、复杂音频关系。

但只「少过滤」还不够——如果复杂视频只有通用 caption，它包含的身份、动作、镜头、音频关系还是变不成有效监督信号。新管道把主体场景、动作交互、镜头时序、对话和歌唱、环境音与音乐、屏幕文字和字幕都纳入可扩展的多模态标注。

效果：在定性样本里观察到了并未显式引入的能力——多镜头跨画面身份一致性、角色对话配字幕特效同步出现。这些不是独立功能模块的产物，而是联合学习真实数据中存在的关系后浮现的。

---

## 成本逻辑：0.5 元从哪来

用户看到的数字——「蒸馏后 10 秒 1080P 推理成本约 0.5 元」——有几个前提条件需要说清楚。

**第一，这针对的是「蒸馏版本」，当前尚未发布。**

官方 README 明确说明：

| 版本 | 去噪步数 | 状态 |
|------|----------|------|
| MAGI-2 Preview，基础版 | 100 步 preview + 5 步 refiner | 已开源 |
| MAGI-2 Preview，蒸馏版 | 大幅减少（far fewer） | Coming soon |

当前开源的基础版尚未做步骤蒸馏，100 步去噪在 8× H100 上预计耗时 15-30 分钟每条视频，成本远高于 0.5 元。蒸馏后的版本是 Sand.ai 自己线上 API 的成本目标。

**第二，MoE 结构的计算节省是真实的。**

6B 激活参数 vs 同质量密集模型（假设需要 14B-20B 密集参数才能达到相似能力）：
- 激活计算量：MoE 是密集参数对应计算量的 30-40%
- 通信效率：Head Parallel 让跨节点通信不随激活专家数线性增长

**第三，行业主流成本参考。**

| 服务 | 10 秒 1080P 生成成本（API 定价） |
|------|----------------------------------|
| Runway Gen-3 Alpha | ~¥3.5-7（$0.50-1.00） |
| Kling 1.6 | ~¥3-5 |
| Veo 3 | 未公开 |
| MAGI-2 蒸馏版（Sand.ai 官方 API 目标） | ~¥0.5 |

如果蒸馏版能实现 0.5 元/条，确实约是主流 API 的十分之一量级。这个差距来自架构稀疏性 + 步骤蒸馏 + Sand.ai 自建基础设施的综合效果。

---

## 自部署方案：完整工程指导

**先说结论**：基础版自部署对硬件要求严苛（8× H100）、成本偏高，适合研究和企业内网部署；蒸馏版发布后才有经济性。但架构是开放的，下面给出完整路径。

### 硬件要求

**官方最低要求（README 原文）**：NVIDIA Hopper 架构 GPU，8 张。

即：H100 SXM5（80GB）或 H100 NVL（94GB），必须 8 张，必须 Hopper 架构。原因：

1. 权重总量约 308GB，需要 8 卡合力持有（28.5 GB/卡，加上 KV cache 和激活内存，80GB 卡会进入紧张状态）
2. 多头并行需要 NVLink（节点内）+ InfiniBand（跨节点）的双层带宽，Hopper 代际的 NVLink 4.0 是设计假设
3. MagiMoE 的内核优化针对 Hopper 架构（BF16 + Flash Attention 3 + CUDA Graph）

**权重明细**：

| 组件 | 大小 | 说明 |
|------|------|------|
| preview（主模型） | 228 GB | 56 个 safetensors 分片 |
| text_encoder | 56 GB | Qwen3.5-27B |
| refiner | 14 GB | 精炼阶段 Transformer |
| stable-audio-open-1.0 | 5 GB | 音频 VAE |
| vae | 3 GB | 视频 VAE（Wan2.2） |
| turbo_vae | 2 GB | 蒸馏 VAE 解码器 |
| **合计** | **~308 GB** | |

**三种硬件规模方案**：

#### 方案 A：最小研究配置（8× H100 80GB）

```
8× NVIDIA H100 SXM5 80GB
总 VRAM：640 GB
互连：NVLink 4.0（节点内），InfiniBand HDR 200Gb（跨节点可选）
系统 RAM：512 GB+ ECC（用于 CPU offload 缓冲）
存储：NVMe SSD 1TB+（权重 + 临时文件）
网络带宽：>=25 Gb/s（下载权重用）
```

- 云端租用：AWS p5.48xlarge（8×H100 80GB）约 $98-100/小时（按需）
- 基础版（100步）预计生成时间：**15-25 分钟/视频**
- 云端成本：约 $25-42/视频（基础版，高昂）
- 蒸馏版发布后预计（假设步骤减少到 8 步）：约 $2-4/视频

#### 方案 B：推荐生产配置（8× H200 141GB）

```
8× NVIDIA H200 SXM5 141GB
总 VRAM：1,128 GB（显存更宽裕，减少 offload 压力）
互连：NVLink 4.0 + HBM3e
```

- H200 的 HBM3e 内存带宽（4.8 TB/s vs H100 的 3.35 TB/s）对视频长序列有直接加速
- offload 模式切换更少，生成更流畅
- 云端：约 $130-150/小时（AWS p5e 或 CoreWeave）

#### 方案 C：私有化部署（购买服务器）

```
NVIDIA DGX H100（8×H100 SXM5）
定价：约 $400K-500K（新）/ $200K-280K（二手/整修）
数据中心托管：约 $5K-10K/月（电力 + 冷却 + 网络）
摊销（3年）：约 $5,000-7,000/天
```

在 3 年摊销框架下，以 $6,000/天 / 24 小时 = $250/小时计算：
- 每 GPU 成本：$31/小时
- 基础版：约 $130/视频（不经济）
- 蒸馏版（假设 2 分钟/视频）：约 $8/视频

**结论**：私有化部署只有在**批量并发生产**（多节点同时跑）+ 蒸馏版发布后才有经济性。研究场景用云租用更合理。

---

### 完整部署步骤

#### 1. 系统准备

```bash
# 操作系统：Ubuntu 22.04 LTS（推荐）
# CUDA 版本：12.4+（Hopper 要求）
# Python：3.12（README 要求）

# 验证 GPU
nvidia-smi
# 应看到 8× H100，Driver 版本 ≥ 535

# 安装 ffmpeg（用于音视频 mux）
sudo apt-get update && sudo apt-get install -y ffmpeg

# 确认 ffmpeg 在 PATH
ffmpeg -version
```

#### 2. 方式一：Docker（推荐，最省心）

```bash
# 拉取官方镜像（已内置所有编译依赖）
docker pull sandai/magi-2-preview:latest

# 准备权重目录（见步骤 3）
mkdir -p /data/magi2-weights

# 运行容器
docker run --gpus all \
  -it \
  -v /data/magi2-weights:/workspace/ckpt \
  sandai/magi-2-preview:latest
```

如果官方 registry 不可达（国内网络），自行构建：

```bash
git clone https://github.com/SandAI-org/MAGI-2-preview
cd MAGI-2-preview
docker build -t magi-2-preview:local .
```

#### 3. 方式二：源码安装

```bash
git clone https://github.com/SandAI-org/MAGI-2-preview
cd MAGI-2-preview

# 安装基础依赖
pip install -r requirements.txt

# 安装 Sand.ai 自研组件（版本号见 Dockerfile）
pip install git+https://github.com/SandAI-org/MagiAttention.git
pip install git+https://github.com/SandAI-org/MagiCompiler.git
```

#### 4. 下载模型权重（~308 GB）

```bash
pip install huggingface_hub

# 默认下载到 ckpt/ 目录
python -c "
from huggingface_hub import snapshot_download
snapshot_download('sand-ai/MAGI-2-preview', local_dir='ckpt')
"

# 或使用 hf 命令行（速度更快，支持断点续传）
pip install -U huggingface_hub[cli]
hf download sand-ai/MAGI-2-preview --local-dir ckpt

# 国内下载可走镜像
HF_ENDPOINT=https://hf-mirror.com hf download sand-ai/MAGI-2-preview --local-dir ckpt
```

权重目录结构验证：

```
ckpt/
├── preview/        # 228 GB：主模型权重（56 个 .safetensors 分片）
├── text_encoder/   # 56 GB：Qwen3.5-27B
├── refiner/        # 14 GB：精炼阶段
├── stable-audio-open-1.0/  # 5 GB：音频 VAE
├── vae/            # 3 GB：视频 VAE（Wan2.2）
└── turbo_vae/      # 2 GB：蒸馏 VAE 解码器
```

#### 5. 推理测试

**方式 A：运行官方 Demo**

```bash
# 生成自带的 3 组示例（I2V + T2V）
bash scripts/run_demo.sh

# 自定义输出目录和 batch
OUTPUT_DIR=output/my_test bash scripts/run_demo.sh
```

**方式 B：单条视频生成**

```bash
# 文字生成视频（T2V），1080P
torchrun --nproc_per_node=8 inference/pipeline/entry.py \
    --prompt "a red fox running through a snowy forest at sunset" \
    --output output/

# 图片+文字生成视频（I2V）
torchrun --nproc_per_node=8 inference/pipeline/entry.py \
    --prompt "the person smiles and waves" \
    --image path/to/first_frame.jpg \
    --output output/

# 自定义 seed 和步数
torchrun --nproc_per_node=8 inference/pipeline/entry.py \
    --prompt "ocean waves crashing at golden hour" \
    --seed 123 \
    --num-inference-steps 100 \
    --refiner-num-inference-steps 5 \
    --output output/
```

**关键环境变量（显存管理）**：

```bash
# 控制各组件的 offload 策略：cpu / gpu / roundtrip
# roundtrip = 两个阶段轮流进出显存（1080P 默认值）
export MAGI2_TEXT_ENC_OFFLOAD_MODE=cpu
export MAGI2_PREVIEW_OFFLOAD_MODE=roundtrip
export MAGI2_REFINER_OFFLOAD_MODE=roundtrip
export MAGI2_VAE_OFFLOAD_MODE=gpu

# 模型权重路径（默认在 ckpt/，不需要改配置文件）
export MAGI2_CKPT_ROOT=/data/magi2-weights

# 确定性推理（Bit-exact，略慢）
export MAGI2_DETERMINISTIC=1
```

#### 6. 生产级配置：Prompt Enhancement

MAGI-2 训练时的 caption 格式是结构化的长描述，直接用短 prompt 会欠驱动模型。官方提供了 Prompt Enhancement（PE）流程：

```bash
# 在 inference/prompt_enhancement/enhancer.py 中设置
API_KEY = "your-openai-compatible-api-key"

# PE 会把 "a red fox running" 扩写成
# 结构化 JSON caption（含主体、动作、镜头、音频描述），
# 再渲染成 Markdown 传给模型
```

如果不想调用外部 API，用 `--prompt` 直接传入 PE 增强过的长描述也可以（`assets/sample_000.txt` 有示例格式）。

#### 7. 视频质量输出规格

- 生成分辨率：512×896（preview 阶段）→ 1088×1920（refiner 阶段）
- 写出文件前可以重缩放：`--output-width 1080 --output-height 1920`
- 时长：固定 10 秒（当前版本唯一支持的时长）
- 音频：与视频同步生成，ffmpeg 混流进 mp4

---

### 成本对比总结

| 场景 | 硬件 | 视频生成时间（当前基础版） | 每视频云端成本 |
|------|------|--------------------------|---------------|
| 研究验证 | 8× H100（AWS p5） | ~20 分钟 | ~$33 |
| 生产（蒸馏版，预计） | 8× H100（AWS p5） | ~2 分钟 | ~$3.3 |
| 私有化（蒸馏版） | 8× H100（DGX，3年摊销） | ~2 分钟 | ~$1-2 |
| Sand.ai 官方 API（蒸馏版目标） | — | 实时 | ~¥0.5（$0.07） |

**结论**：私有化部署在以下条件下才有经济意义：
1. 蒸馏版权重发布
2. 自建数据中心 GPU 集群（摊销成本 <$5/GPU-hour）
3. 日均视频生成量 ≥ 200 条（规模效应）

如果视频需求量不大（每天几十条），调用 Sand.ai API 比自部署划算得多。

---

## 这套开源的真实意义

MAGI-2 Preview 是研究预发布，官方明确说了不是最终产品版本。但开源了什么是关键：

**已开放**：
- 推理代码（Apache 2.0）
- 完整权重（Apache 2.0）
- MAGICompiler（推理加速编译器）
- MAGIAttention（长序列注意力）
- 完整技术博客（架构/系统/数据的详细论证）

**未开放**：
- 训练代码
- 完整数据管道
- 蒸馏训练方案（蒸馏版权重 coming soon，但训练代码不开源）

这个组合——推理开放、训练保留——是商业开源的标准模式（参考 Mistral、DeepSeek）。你能研究它、跑它、在它上面做应用，但无法复制训练过程。

对于想用视频生成建产品的团队：Apache 2.0 意味着商业使用合法，不需要额外授权。在自己的基础设施上跑这套模型，API 调用费降到接近零。等蒸馏版发布后，这才是真正的窗口期。

---

官方仓库：[github.com/SandAI-org/MAGI-2-preview](https://github.com/SandAI-org/MAGI-2-preview)  
技术博客：[sand.ai/blog/magi-2-preview](https://sand.ai/blog/magi-2-preview)  
模型权重：[huggingface.co/sand-ai/MAGI-2-preview](https://huggingface.co/sand-ai/MAGI-2-preview)  
API 平台：[platform.sand.ai](https://platform.sand.ai)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## MAGI-2 Preview: 114B MoE for Video Generation — Architecture Analysis and Full Self-Hosting Guide

*by Mycelium Protocol*

---

One number makes this worth taking seriously: **114B total parameters, 6B activated per token**.

Not compression. Not quantization. Sparse activation by architecture — each generation invokes only 5.3% of the total parameter count. Sand.ai has open-sourced the full stack: Apache 2.0, weights on Hugging Face, inference code on GitHub.

---

### What Sand.ai Is

Sand.ai is a video generation AI company. MAGI-1 (2025) established their position with autoregressive video generation — splitting video into temporal chunks and modeling their causal relationships through autoregressive denoising.

MAGI-2 changes the foundational question. Not "how should video be generated?" but **"how should a video generation model scale?"**

---

### Architecture: Why Only 6B of 114B Activates

**Single-stream Transformer: text + video + audio unified**

MAGI-2 builds on the single-stream design validated in MagiHuman: text, video, and audio tokens processed together in one unified token sequence using self-attention only. No multi-modal towers. No cross-attention interfaces.

The reason is concrete: language, lip movements, body motion, environmental sound, music, and camera rhythm are continuously interdependent. A single sequence lets them exchange information throughout the entire backbone, not only at a handful of predefined interfaces.

**MagiMoE: Ultra-Fine-Grained sparse routing**

Scaling capacity with a dense Transformer hits two walls at 100B scale:
1. Training infrastructure — all parameters compute for every token at every step
2. Inference cost — long video sequences through a 100B dense model is impractical

MoE decouples total capacity from per-token computation:

- Dense: `F ∝ N × P_total`
- MoE: `F ∝ N × P_active`, where `P_active ≪ P_total`

**MAGI-2 Preview configuration:**

| Component | Value |
|-----------|-------|
| Layers | 40 Transformer layers |
| Sparse core | Middle 36 use Multi-Head MoE; 4 boundary layers dense |
| Model width | 3,072 |
| Routed representation | 12 heads × 256 dimensions |
| Expert pool | 256 experts per head |
| Active experts | Top-6 per head |
| Total expert units per layer | 12 × 256 = 3,072 |
| Activated units per token | 12 × 6 = 72 |

These are not full-width FFN experts. Each expert operates in a 256-dimensional subspace. Different subspaces of the same token can form different expert combinations — not a large indivisible expert that must fire as a unit.

**Head Parallel: solving MoE's communication explosion**

Standard MoE communication: `C ∝ N × k × H` — expensive when video sequences are long.

MAGI-2 uses Multi-Head LatentMoE + Head Parallel. Cross-node communication carries head slices, not dynamic token copies: `C ∝ N × H`. Send and receive shapes are determined statically by the head partition, so buffers can be pre-allocated and communication is regular, not data-dependent.

**MagiMuon: optimizer that understands head × expert structure**

MAGI-2's expert weights form a large batch of small matrices indexed by head × expert, not one large matrix. MagiMuon performs Muon orthogonalization independently for each matrix, distributing the matrix batch across ranks for optimizer parallelism — rather than flattening everything into an artificial large matrix.

---

### Data Pipeline: Breaking the Filtering Trap

MAGI-2 makes a fundamental shift in data strategy that deserves attention.

**The trap:** small models (~7B) have limited representational capacity. To produce stable outputs, the community naturally filtered training data: keep simple, stable, clear-subject videos, discard samples the model struggles with. This works for small models — but when you later scale up, the large model still sees a simplified world. The data filtering criteria were set by the small model's capability boundary.

Sand.ai calls this **the data filtering trap**: when training data is continually simplified to fit the current model, the data itself becomes the capability ceiling of a stronger model.

**The alternative:** necessary data governance stays (safety, compliance, privacy, corruption, dedup). But whether a sample is easy for the current model is no longer the admission criterion. Complex motion, multi-person interactions, shot transitions, subtitles, on-screen text, complex audio relationships — keep them. Then accurately annotate the complexity that was preserved.

The result: qualitative samples show capabilities that were never introduced through dedicated modules. Multi-shot identity consistency. Dialogue appearing alongside corresponding subtitle effects. These aren't isolated features — they emerge from jointly learning the relationships present in real data.

---

### The Cost Math: Where 0.5 RMB Comes From

Two important caveats before trusting this number:

**Caveat 1: This applies to the distilled version, which is not yet released.**

The README is explicit:

| Release | Denoising steps | Status |
|---------|-----------------|--------|
| MAGI-2 Preview, base | 100 preview + 5 refiner | Open-sourced |
| MAGI-2 Preview, distilled | far fewer | Coming soon |

The current open-sourced base model has not been step-distilled. At 100 denoising steps on 8× H100, generation takes roughly 15-30 minutes per clip. The distilled version is the cost target for Sand.ai's own API.

**Caveat 2: The compute savings from MoE are real, but not alone sufficient.**

6B active parameters vs. a comparable dense model (roughly 14-20B dense to match equivalent capability):
- Active compute: ~30-40% of an equivalent dense model
- Communication efficiency: Head Parallel makes cross-node traffic not grow with number of active experts

**Industry cost reference:**

| Service | 10-second 1080P cost |
|---------|---------------------|
| Runway Gen-3 Alpha | ~$0.50-1.00 |
| Kling | ~$0.40-0.70 |
| Sand.ai API (distilled target) | ~¥0.5 (~$0.07) |

If the distilled version achieves ¥0.5 per clip, that's roughly 1/7 to 1/10 of competitor API pricing. The gap combines architecture sparsity + step distillation + Sand.ai's own infrastructure efficiency.

---

### Self-Hosting Guide: Complete Engineering Instructions

**Bottom line first:** base version self-hosting requires 8× H100 and is expensive; wait for the distilled version for economic viability. But the architecture is open — here's the full path.

#### Hardware Requirements

**Official minimum (from README):** NVIDIA Hopper architecture GPUs, 8 of them.

H100 SXM5 (80GB) or H100 NVL (94GB), exactly 8, Hopper architecture required. Why:

1. Total weights ~308GB — 8 cards share the load (28.5 GB/card plus KV cache and activations, leaving 80GB cards tight)
2. Multi-head parallelism requires NVLink (intra-node) + InfiniBand (inter-node bandwidth) — Hopper's NVLink 4.0 is the design assumption
3. MagiMoE kernels are optimized for Hopper architecture (BF16 + Flash Attention 3 + CUDA Graph)

**Weight breakdown:**

| Component | Size | Notes |
|-----------|------|-------|
| preview (main) | 228 GB | 56 safetensors shards |
| text_encoder | 56 GB | Qwen3.5-27B |
| refiner | 14 GB | Refiner-stage Transformer |
| stable-audio-open-1.0 | 5 GB | Audio VAE |
| vae | 3 GB | Video VAE (Wan2.2) |
| turbo_vae | 2 GB | Distilled VAE decoder |
| **Total** | **~308 GB** | |

**Three hardware configurations:**

**Option A — Minimum research (8× H100 80GB)**
- Cloud: AWS p5.48xlarge, ~$98-100/hour on-demand
- Base model generation time: ~15-25 min/video
- Cloud cost per video (base): ~$25-42 (expensive)
- Projected after distilled release (assume 8× step reduction): ~$2-4/video

**Option B — Recommended production (8× H200 141GB)**
- HBM3e memory bandwidth (4.8 TB/s vs 3.35 TB/s on H100) benefits long video sequences directly
- Fewer offload roundtrips, smoother generation
- Cloud: ~$130-150/hr (AWS p5e or CoreWeave)

**Option C — Private infrastructure (purchase)**
- DGX H100 (8× H100 SXM5): ~$400-500K new, ~$200-280K refurbished
- Datacenter hosting: ~$5-10K/month
- 3-year amortized: ~$250/hour for the full node
- Economic only at scale with distilled model + parallel workloads

#### Setup

**Option 1: Docker (recommended)**

```bash
docker pull sandai/magi-2-preview:latest
mkdir -p /data/magi2-weights
docker run --gpus all -it \
  -v /data/magi2-weights:/workspace/ckpt \
  sandai/magi-2-preview:latest
```

**Option 2: From source**

```bash
git clone https://github.com/SandAI-org/MAGI-2-preview
cd MAGI-2-preview
pip install -r requirements.txt
pip install git+https://github.com/SandAI-org/MagiAttention.git
pip install git+https://github.com/SandAI-org/MagiCompiler.git
```

#### Download Weights (~308 GB)

```bash
pip install -U huggingface_hub[cli]
hf download sand-ai/MAGI-2-preview --local-dir ckpt

# Mirror for restricted network
HF_ENDPOINT=https://hf-mirror.com hf download sand-ai/MAGI-2-preview --local-dir ckpt
```

#### Run Inference

```bash
# Text-to-video, 1080P
torchrun --nproc_per_node=8 inference/pipeline/entry.py \
    --prompt "a red fox running through a snowy forest at sunset" \
    --output output/

# Image-to-video
torchrun --nproc_per_node=8 inference/pipeline/entry.py \
    --prompt "the person smiles and waves" \
    --image path/to/first_frame.jpg \
    --output output/

# Official demo batch (I2V + T2V examples)
bash scripts/run_demo.sh
```

**Key environment variables (VRAM management):**

```bash
# Offload modes: cpu / gpu / roundtrip
# roundtrip = stage in/out between phases (required for 1080P on 80GB cards)
export MAGI2_TEXT_ENC_OFFLOAD_MODE=cpu
export MAGI2_PREVIEW_OFFLOAD_MODE=roundtrip
export MAGI2_REFINER_OFFLOAD_MODE=roundtrip
export MAGI2_VAE_OFFLOAD_MODE=gpu

# Point to weights if not in default ckpt/
export MAGI2_CKPT_ROOT=/data/magi2-weights

# Bit-exact reproducibility (slightly slower)
export MAGI2_DETERMINISTIC=1
```

#### Production: Prompt Enhancement

MAGI-2 was trained on long structured captions. Short prompts underutilize the model. The official prompt enhancement pipeline rewrites short prompts through an LLM to structured JSON captions before encoding:

```bash
# Set API_KEY in inference/prompt_enhancement/enhancer.py
# for any OpenAI-compatible endpoint
# Leave empty to skip PE and pass prompts directly
```

#### Output Specs

- Generation resolution: 512×896 (preview stage) → 1088×1920 (refiner)
- Rescale to standard: `--output-width 1080 --output-height 1920`
- Duration: fixed 10 seconds (only supported duration currently)
- Audio: generated alongside video, muxed into mp4 via ffmpeg

---

### Cost Summary

| Scenario | Hardware | Time (base model) | Cost per video |
|----------|----------|-------------------|----------------|
| Research | 8× H100 (AWS p5) | ~20 min | ~$33 |
| Production (distilled, projected) | 8× H100 (AWS p5) | ~2 min | ~$3.30 |
| Private (distilled) | 8× H100 DGX (3yr amortized) | ~2 min | ~$1-2 |
| Sand.ai API target (distilled) | — | near-realtime | ~¥0.5 ($0.07) |

Self-hosting only makes economic sense with: the distilled weights, your own GPU cluster at datacenter pricing, and volume ≥ 200 clips/day. Below that threshold, Sand.ai's API is cheaper.

---

### What the Open-Source Actually Covers

**Available under Apache 2.0:**
- Inference code
- Full model weights
- MAGICompiler (inference acceleration)
- MAGIAttention (long-sequence attention)
- Complete technical blog (architecture + systems + data)

**Not available:**
- Training code
- Full data pipeline
- Distillation training recipe (distilled weights coming, training code not)

This is standard commercial open-source (same pattern as Mistral, DeepSeek): you can run it, study it, build products on it, but can't replicate the training. Apache 2.0 means commercial use is legal with no additional licensing.

The real window opens when the distilled weights ship. That's when self-hosting unit economics shift — and when the $0.07/clip cost story becomes testable against real hardware.

---

Repository: [github.com/SandAI-org/MAGI-2-preview](https://github.com/SandAI-org/MAGI-2-preview)  
Technical blog: [sand.ai/blog/magi-2-preview](https://sand.ai/blog/magi-2-preview)  
Weights: [huggingface.co/sand-ai/MAGI-2-preview](https://huggingface.co/sand-ai/MAGI-2-preview)  
API: [platform.sand.ai](https://platform.sand.ai)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
