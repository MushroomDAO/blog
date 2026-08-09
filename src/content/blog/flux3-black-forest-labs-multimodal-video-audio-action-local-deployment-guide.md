---
title: "FLUX.3 深度解析：图像+视频+音频+机器人动作，一个模型，本地部署完整指南与硬件成本评估"
titleEn: "FLUX.3 Deep Dive: One Model for Image, Video, Audio & Robot Actions — Complete Local Deployment Guide and Hardware Cost Analysis"
description: "Black Forest Labs 于2026-07-23发布FLUX.3，单一多模态基础模型联合学习图像/视频/音频/动作，Early Access API已上线。本文深度解析FLUX.3架构、能力、评测数据，以及现有FLUX.1/2系列全套本地部署方案：mflux（Apple Silicon）、ComfyUI（NVIDIA）、硬件选配建议和成本对比。"
descriptionEn: "Black Forest Labs released FLUX.3 on 2026-07-23: a single multimodal foundation model jointly trained on images, video, audio, and actions. Early Access API is live. This post deeply analyzes FLUX.3's architecture, capabilities, and benchmarks, plus a complete local deployment guide for the FLUX.1/2 open-weight series: mflux (Apple Silicon), ComfyUI (NVIDIA), hardware tier recommendations, and cost comparison."
pubDate: "2026-07-25"
updatedDate: "2026-07-25"
category: "Tech-Experiment"
tags: ["FLUX", "图像生成", "视频生成", "多模态", "Black Forest Labs", "本地部署", "Apple Silicon", "mflux", "ComfyUI", "AI工具"]
heroImage: "../../assets/images/flux3-black-forest-labs-multimodal-video-audio-action-local-deployment-guide-banner.jpg"
---

> **官网**：blackforestlabs.ai · **GitHub**：github.com/black-forest-labs/flux（25,797 ⭐）
> **发布日期**：2026-07-23 · **状态**：API Early Access，开放权重即将发布
> **Early Access 申请**：tally.so/r/44d9NX

---

## 一、FLUX 模型谱系：从 1 到 3 发生了什么

Black Forest Labs 的 FLUX 系列是当前最被广泛部署的开源图像生成模型之一。在理解 FLUX.3 之前，先看整个谱系的演进：

| 版本 | 发布 | 模态 | 开放权重 | 核心突破 |
|------|------|------|---------|---------|
| **FLUX.1** | 2024年 | 图像 | ✅（schnell/dev）| 高质量文生图，超越SD3/Midjourney |
| **FLUX.2** | 2025年 | 图像 | ✅（Klein，商业授权）| 更强图像编辑（Kontext），4B紧凑版（Klein）|
| **FLUX.3** | 2026-07-23 | **图+视频+音频+动作** | 🔜（FLUX 3 Dev，数月内）| 统一多模态，物理世界建模 |

FLUX.3 不是 FLUX.1 的图像生成升级版——它是一次范式转变：**从单模态生成工具变成理解物理世界的基础模型**。

---

## 二、FLUX.3 的核心架构：Self-Flow

FLUX.3 基于 BFL 自研的 **Self-Flow** 框架构建。传统多模态模型通常先分别训练各模态模型，再用适配器对齐。Self-Flow 的做法是：**从一开始就在同一架构中联合学习图像、视频、音频**。

为什么这样做更好？

用 BFL 自己的话说：

> "图像捕捉某一时刻的空间结构。视频恢复时间维度，揭示运动动态和物理规律。音频揭示视觉单独无法检测到的机械现象与声学之间的因果关系。语言将这些感知与目标、抽象和指令连接起来。"

单独学一个模态，你得到的是那个模态的投影。**同时学全部，各模态的相互约束让模型学到更多**：声音必须匹配碰撞，运动必须服从质量，未来必须从过去推导。这是在学**世界本身**，而不是世界的某个截面。

### 训练计算分配

- **视频**：>95% 的计算量（最难——必须学接触、运动、重量、因果）
- **音频**：<0.5% token 占比（一旦学了视频，音频的因果关系自然习得）
- **动作**：低维表示，类似音频的地位，视频理解是前提

---

## 三、FLUX.3 的能力清单

### 3.1 视频生成（FLUX 3 Video，已上线）

每条视频均**原生带音频**，不是后期合成：

- **文本生成视频**：最长 20 秒，720p
- **图像转视频**：从起始帧继续动画，或以图像为视觉参考
- **视频转视频**：保留源视频的核心元素（同一角色）移入新场景
- **视频+音频延续**：从输入的视频和音频继续生成
- **关键帧转视频**：在定义的关键时刻之间生成受控过渡
- **多语言对话**：音频支持多种语言
- **多样风格**：从手持摄像机纪实风到动画、电影叙事全覆盖
- **强文字生成**：多语言文字渲染，包括在视频中

### 3.2 图像生成（FLUX 3 Image，数周内）

- 比 FLUX.1/2 更强的复杂提示词理解
- 多语言文字渲染
- 更宽的风格范围

### 3.3 动作预测（FLUX-mimic，机器人，合作伙伴）

这是 FLUX.3 最反直觉的能力：**同一个内容生成模型驱动机器人**。

BFL 与 mimic robotics 合作，基于 FLUX.3 backbone 开发了 **FLUX-mimic**，已在奥迪工厂的真实生产线上部署：

- 零件装盘
- 电子控制单元插入精密夹具
- 柔性材料（密封件、线缆）处理——传统自动化从未能解决

关键数据：**单 NVIDIA RTX 5090，从输入到世界表示 <80ms**，完整系统响应时间 101ms（接近人类视觉反应时间）。

---

## 四、评测数据

文字转视频，10 秒，720p，preliminary 结果：

| 对比对象 | FLUX.3 胜出比例 |
|--------|--------------|
| Luma Ray 3.2 | **93%** |
| Runway Gen-4.5 | **77%** |
| Grok Imagine Video | **69%** |
| Kling v3 Pro | **60%** |
| Happy Horse v1 | **59%** |
| Happy Horse 1.1 | **57%** |
| Seedance 2.0 | **52%** |
| Gemini Omni Flash | **52%** |

特别强的维度：**捕捉人类面部表情**、**声音与物理事件关联**、**多语言能力**。

> ⚠️ BFL 明确标注这是训练中期的 preliminary 结果，正式发布前预计还会有提升。

---

## 五、发布路线图

```
2026-07-23  ─── FLUX 3 Video（API Early Access，现在可申请）
    │
    ├── 数周内 ─── FLUX 3 Image（API Early Access）
    │
    ├── 数月内 ─── FLUX 3 Dev（开放权重，社区本地部署）
    │
    └── 持续  ─── FLUX 3 Action（研究/商业合作伙伴）
```

**现在可以做的**：申请 Early Access → [tally.so/r/44d9NX](https://tally.so/r/44d9NX)

---

## 六、本地部署指南：现有 FLUX.1/2 系列

FLUX.3 的开放权重还需等待，但 FLUX.1/2 系列已完全可以本地运行。掌握这套部署能力，FLUX 3 Dev 一旦发布，迁移成本几乎为零。

### 6.1 模型版本选择

| 模型 | 授权 | 最适用场景 |
|-----|------|---------|
| `FLUX.1 [schnell]` | Apache-2.0 ✅ | 快速迭代、商业项目，4步生成 |
| `FLUX.1 [dev]` | 非商业 | 个人研究、高质量样本 |
| `FLUX.1 Kontext [dev]` | 非商业 | **图像编辑**（替换元素、风格迁移）|
| `FLUX.1 Fill [dev]` | 非商业 | 局部重绘（inpainting/outpainting）|
| `FLUX.2 [klein]` | 商业授权 💰 | 4B紧凑版，Apple Silicon 最佳选择 |

**商业项目**：用 FLUX.1 [schnell]（Apache-2.0）或购买 FLUX.2 商业授权。

---

### 6.2 方案 A：Apple Silicon（mflux）

**mflux** 是 Apple Silicon 的 MLX 原生实现，无需 NVIDIA GPU：

```bash
# 安装（需要 Python 3.10+ 和 ~/venvs/ml）
source ~/venvs/ml/bin/activate
pip install mflux

# 生成图像（FLUX.1 schnell，4步，最快）
mflux-generate \
  --model black-forest-labs/FLUX.1-schnell \
  --prompt "a photorealistic mountain at sunset, cinematic" \
  --steps 4 \
  --seed 42 \
  --width 1024 --height 1024

# 生成图像（FLUX.2 Klein，低显存模式，20步）
mflux-generate-flux2 \
  --model ~/.omlx/models/FLUX.2-klein-4B-mflux-4bit \
  --base-model flux2-klein-4b \
  --prompt "..." \
  --steps 20 \
  --low-ram \
  --width 1200 --height 624 \
  --output output.png
```

**首次运行会自动下载模型权重**（约 23GB for FLUX.1 dev，约 7GB for 4-bit 量化）。

---

### 6.3 方案 B：NVIDIA GPU（官方推理）

```bash
# 克隆仓库
git clone https://github.com/black-forest-labs/flux
cd flux
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

# 文生图（FLUX.1 [schnell]）
python -m flux text_to_image \
  --name flux-schnell \
  --prompt "a cyberpunk city at night, neon reflections" \
  --width 1024 --height 1024 \
  --output output.png

# 图像编辑（FLUX.1 Kontext，需参考图）
python -m flux kontext \
  --prompt "replace the car with a red sports car" \
  --image reference.jpg

# TensorRT 加速（需 enroot，速度提升 2-3x）
pip install -e ".[tensorrt]" --extra-index-url https://pypi.nvidia.com
```

---

### 6.4 方案 C：ComfyUI（推荐给非工程师）

ComfyUI 是可视化节点工作流，适合不想写代码的用户：

```bash
# 安装 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt

# 下载 FLUX.1 dev 模型权重
# 放入 models/unet/ 目录
# 从 HuggingFace 手动下载：
# https://huggingface.co/black-forest-labs/FLUX.1-dev

# 启动
python main.py --listen
# 打开浏览器访问 http://localhost:8188
```

优质工作流资源：
- civitai.com（搜索 FLUX workflow）
- comfyworkflows.com

---

## 七、硬件配置建议

### FLUX.1/2 本地运行硬件需求

| 层级 | 硬件 | 显存/内存 | 推理速度（1024px）| 推荐场景 |
|------|------|---------|----------------|--------|
| **入门** | RTX 3070 / RTX 4060 | 8GB VRAM | 60–120 秒 | 个人实验，FLUX.1 schnell |
| **标准** | RTX 3090 / RTX 4080 | 24GB VRAM | 15–30 秒 | 日常创作，dev 模型 |
| **专业** | RTX 4090 / A6000 | 24–48GB VRAM | 8–15 秒 | 高频生产，批量任务 |
| **Apple Silicon 入门** | M2 Pro / M3 (16GB) | 16GB 统一内存 | 90–180 秒 | mflux + low-ram 模式 |
| **Apple Silicon 标准** | M2 Max / M3 Max (32GB) | 32GB 统一内存 | 45–90 秒 | mflux 全速 |
| **Apple Silicon 高配** | M4 Max / M4 Ultra (64-128GB) | 64–128GB 统一内存 | 20–40 秒 | 接近 RTX 4090 |

**重要说明**：
- Apple Silicon 统一内存的带宽比 PCIe GPU 内存带宽低，但胜在无传输开销，且 mflux 的 MLX 优化已相当成熟
- FLUX 3 Dev（即将发布的多模态版）预计对显存需求更高，推荐 24GB+ VRAM 或 48GB+ Apple Silicon

---

## 八、成本分析：API vs 本地

### API 调用成本（BFL 官方，当前 FLUX.2 定价，FLUX.3 TBD）

| 分辨率 | 约等于 MP | API 价格 |
|--------|----------|---------|
| 512×512 | 0.25 MP | ~$0.008 |
| 1024×1024 | 1 MP | ~$0.030 |
| 1920×1080 | ~2 MP | ~$0.060 |
| 2048×2048 | 4 MP | ~$0.120 |

**视频定价（FLUX.3）**：尚未公布，参考竞品：Runway 约 $0.05/秒，Kling 约 $0.03–0.10/秒，预计 FLUX.3 Video 在 $0.05–0.15/秒范围。

### 云 GPU 成本（自托管）

| 供应商 | GPU | 小时价 | 适合 |
|--------|-----|--------|------|
| RunPod | RTX 4090 | ~$0.69/hr | 快速原型 |
| RunPod | A100 80GB | ~$1.89/hr | 批量生成 |
| Vast.ai | RTX 3090 | ~$0.25–0.40/hr | 低成本实验 |
| Lambda | A10 24GB | ~$0.60/hr | 稳定生产 |

**收支平衡分析（FLUX.1 dev，1024px）**：
- API：每张 $0.03
- RunPod RTX 4090：约 15 秒/张 → 240 张/小时 → 每张 $0.0029（节省 90%）
- 本地 RTX 4090（约 $1,800）：如果每月生成 2000 张，API 成本 $60/月，硬件约 30 个月回本

**推荐策略**：
- 每月 < 500 张：直接用 API，省事
- 每月 500–5000 张：云 GPU 性价比更好
- 每月 > 5000 张 / 有隐私需求 / 需要定制微调：本地硬件

---

## 九、FLUX.3 Dev 本地部署前瞻

基于 BFL 的一贯发布模式（FLUX.1 dev、FLUX.2 klein 均有开放权重），FLUX 3 Dev 发布后，本地部署路径预计如下：

```bash
# 届时的完整本地部署（预估）
# 1. 从 HuggingFace 下载权重（预计 30–80GB for full precision）
# 2. 安装更新后的 mflux / ComfyUI 适配版
# 3. 推理

# Apple Silicon 示例（预计命令格式）
mflux-generate-flux3 \
  --model black-forest-labs/FLUX.3-dev \
  --prompt "..." \
  --modality video \
  --duration 10 \
  --low-ram \
  --output output.mp4

# NVIDIA 示例
python -m flux text_to_video \
  --name flux-3-dev \
  --prompt "..." \
  --duration 10 \
  --output output.mp4
```

**预计显存需求**（估算）：
- 图像生成：24–32GB VRAM（全精度），量化后 12–16GB
- 视频生成（10秒720p）：40–80GB VRAM，量化后 20–40GB
- Apple Silicon：M3 Max (96GB) 或 M4 Ultra (192GB) 才能流畅跑视频

---

## 十、现在能做什么

**立即可用**：
1. **申请 FLUX.3 Video Early Access**：[tally.so/r/44d9NX](https://tally.so/r/44d9NX)
2. **用 API 测试 FLUX.2**：[dashboard.bfl.ai](https://dashboard.bfl.ai)（图像生成，FLUX.3 同等入口）
3. **本地跑 FLUX.1 schnell**：Apache-2.0，完全免费商用，现在就能用

**等待发布**：
- FLUX 3 Image API（数周内）
- FLUX 3 Dev 开放权重（数月内，届时更新本文）

---

## 十一、为什么 FLUX.3 值得认真关注

视频生成工具很多，但 FLUX.3 的逻辑和其他工具不同：

**其他工具**：图像模型 + 视频扩展 + 单独的音频模型，三者拼在一起。

**FLUX.3**：从一开始就是一个模型，视频训练 >95% 计算量，音频和动作是这个世界模型的自然延伸。

这让 FLUX.3 在**物理一致性**上有结构性优势——声音和画面对齐，运动遵循物理规律，不是靠后处理缝合，而是模型天然的输出。能在奥迪工厂驱动真实机器人，就是这个世界模型质量的最直接证明。

$3 亿 Series B、Martin Scorsese 担任顾问、已在真实生产线验证——这不是另一个 demo。

---

*数据来源：blackforestlabs.ai/blog/flux-3，blackforestlabs.ai/blog/flux-3-mimic，github.com/black-forest-labs/flux，2026-07-25 整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Website**: blackforestlabs.ai · **GitHub**: github.com/black-forest-labs/flux (25,797 ⭐)
> **Released**: 2026-07-23 · **Status**: API Early Access; open weights coming
> **Apply for Early Access**: tally.so/r/44d9NX

---

## 1. The FLUX Model Lineage: What Changed from 1 to 3

Black Forest Labs' FLUX series is one of the most widely deployed open-source image generation model families in existence. Before diving into FLUX.3, the progression:

| Version | Release | Modalities | Open Weights | Core Advance |
|---------|---------|------------|-------------|-------------|
| **FLUX.1** | 2024 | Image | ✅ (schnell/dev) | High-quality text-to-image, surpassing SD3/Midjourney |
| **FLUX.2** | 2025 | Image | ✅ (Klein, commercial) | Stronger image editing (Kontext), 4B compact model (Klein) |
| **FLUX.3** | 2026-07-23 | **Image + Video + Audio + Actions** | 🔜 (FLUX 3 Dev, months out) | Unified multimodal, physical world modeling |

FLUX.3 is not an upgraded image generator — it's a paradigm shift: **from a single-modality generation tool to a foundation model that understands the physical world.**

---

## 2. FLUX.3's Core Architecture: Self-Flow

FLUX.3 is built on **Self-Flow**, BFL's in-house framework for multimodal flow matching. Where conventional multimodal approaches train separate models per modality and align them with adapters, Self-Flow **jointly learns image, video, and audio within a single architecture from the start.**

Why does this matter?

BFL's own framing:

> "Images capture spatial structure at a single point in time. Video restores the dimension of time and reveals temporal dynamics and physical laws. Audio reveals causal relationships between mechanical phenomena and acoustics that vision alone cannot detect. Language links these perceptions to goals, abstractions, and instructions."

Learn from one modality: you get a good model of that projection. **Learn from all at once: their mutual constraints tell you more.** The sound has to match the impact. The motion has to obey the mass. The future has to follow from the past. That's not learning projections — that's learning **the world itself.**

### Training compute allocation

- **Video**: >95% of compute (hardest — must learn contact, motion, weight, cause, effect)
- **Audio**: <0.5% of token count (once video physics is learned, audio causality follows naturally)
- **Actions**: low-dimensional representation, same story as audio — video understanding is the prerequisite

---

## 3. What FLUX.3 Can Do

### 3.1 Video Generation (FLUX 3 Video — live now)

Every output includes **native audio** — not post-composed:

- **Text-to-video**: up to 20 seconds, native audio, 720p
- **Image-to-video**: continue from a starting frame, or use images as visual references
- **Video-to-video**: carry core elements of a source video (same character) into a new scene
- **Video+audio continuation**: generate continuation from input video and audio
- **Keyframe-to-video**: controlled transitions between defined moments
- **Multilingual dialogue**: audio in multiple languages
- **Wide style range**: candid camcorder footage to animation to cinematics
- **Strong typography**: multi-language text rendering, including in video

### 3.2 Image Generation (FLUX 3 Image — weeks away)

- Significantly improved complex prompt comprehension vs FLUX.1/2
- Multi-language text rendering
- Wider style range

### 3.3 Action Prediction (FLUX-mimic — partner access)

The most counterintuitive capability: **the same content generation model drives robots.**

BFL partnered with mimic robotics to develop **FLUX-mimic**, deployed on real Audi production lines:

- Parts kitting into structured trays
- Electronic control unit insertion into precision fixtures
- Flexible material handling (seals, cables) — impossible for conventional automation

Key figure: **on a single NVIDIA RTX 5090, input-to-world-representation in <80ms.** Full system response time: 101ms — on the order of human visual reaction time.

---

## 4. Benchmark Results

Text-to-video, 10-second clips, 720p, preliminary results:

| Competitor | FLUX.3 Preferred |
|-----------|-----------------|
| Luma Ray 3.2 | **93%** |
| Runway Gen-4.5 | **77%** |
| Grok Imagine Video | **69%** |
| Kling v3 Pro | **60%** |
| Happy Horse v1 | **59%** |
| Happy Horse 1.1 | **57%** |
| Seedance 2.0 | **52%** |
| Gemini Omni Flash | **52%** |

Particularly strong dimensions: **capturing human facial expressions**, **audio-physical event alignment**, **multilingual capability**.

> ⚠️ BFL explicitly labels these as preliminary mid-training results; further improvements expected before official release.

---

## 5. Release Roadmap

```
2026-07-23  ─── FLUX 3 Video (API Early Access — apply now)
    │
    ├── Weeks  ─── FLUX 3 Image (API Early Access)
    │
    ├── Months ─── FLUX 3 Dev (open weights — local deployment)
    │
    └── Ongoing ── FLUX 3 Action (research/commercial partners)
```

**What you can do now**: Apply for Early Access → [tally.so/r/44d9NX](https://tally.so/r/44d9NX)

---

## 6. Local Deployment Guide: Current FLUX.1/2 Open Weights

FLUX.3's open weights are still coming. The FLUX.1/2 series can run locally right now. Learn the deployment stack now, and migration when FLUX 3 Dev drops will be nearly zero effort.

### 6.1 Model Version Selection

| Model | License | Best for |
|-------|---------|---------|
| `FLUX.1 [schnell]` | Apache-2.0 ✅ | Fast iteration, commercial projects, 4-step generation |
| `FLUX.1 [dev]` | Non-commercial | Personal research, high-quality samples |
| `FLUX.1 Kontext [dev]` | Non-commercial | **Image editing** (element replacement, style transfer) |
| `FLUX.1 Fill [dev]` | Non-commercial | Inpainting / outpainting |
| `FLUX.2 [klein]` | Commercial license 💰 | 4B compact, best for Apple Silicon |

**Commercial projects**: use FLUX.1 [schnell] (Apache-2.0 free) or purchase a FLUX.2 commercial license.

---

### 6.2 Option A: Apple Silicon (mflux)

**mflux** is a native MLX implementation for Apple Silicon — no NVIDIA GPU required:

```bash
# Install (requires Python 3.10+ and a virtualenv)
pip install mflux

# Generate (FLUX.1 schnell, 4 steps, fastest)
mflux-generate \
  --model black-forest-labs/FLUX.1-schnell \
  --prompt "a photorealistic mountain at sunset, cinematic" \
  --steps 4 \
  --seed 42 \
  --width 1024 --height 1024

# Generate (FLUX.2 Klein, low-RAM mode, 20 steps)
mflux-generate-flux2 \
  --model ~/.omlx/models/FLUX.2-klein-4B-mflux-4bit \
  --base-model flux2-klein-4b \
  --prompt "..." \
  --steps 20 \
  --low-ram \
  --width 1200 --height 624 \
  --output output.png
```

First run auto-downloads weights (~23GB for FLUX.1 dev, ~7GB for 4-bit quantized FLUX.2 Klein).

---

### 6.3 Option B: NVIDIA GPU (official repo)

```bash
# Clone the repo
git clone https://github.com/black-forest-labs/flux
cd flux
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

# Text-to-image (FLUX.1 schnell)
python -m flux text_to_image \
  --name flux-schnell \
  --prompt "a cyberpunk city at night, neon reflections" \
  --width 1024 --height 1024 \
  --output output.png

# Image editing (FLUX.1 Kontext, requires reference image)
python -m flux kontext \
  --prompt "replace the car with a red sports car" \
  --image reference.jpg

# TensorRT acceleration (2–3x speedup, requires enroot)
pip install -e ".[tensorrt]" --extra-index-url https://pypi.nvidia.com
```

---

### 6.4 Option C: ComfyUI (recommended for non-engineers)

ComfyUI is a visual node workflow editor — no code required:

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt

# Download FLUX.1 dev weights from HuggingFace
# Place in models/unet/

python main.py --listen
# Open browser: http://localhost:8188
```

Community workflow resources: civitai.com, comfyworkflows.com

---

## 7. Hardware Tier Recommendations

| Tier | Hardware | VRAM / RAM | Speed (1024px) | Use Case |
|------|----------|-----------|---------------|---------|
| **Entry** | RTX 3070 / RTX 4060 | 8GB VRAM | 60–120s | Personal experiments, schnell only |
| **Standard** | RTX 3090 / RTX 4080 | 24GB VRAM | 15–30s | Daily creative work, dev models |
| **Pro** | RTX 4090 / A6000 | 24–48GB VRAM | 8–15s | High-frequency production, batch |
| **Apple Entry** | M2 Pro / M3 (16GB) | 16GB unified | 90–180s | mflux + low-RAM mode |
| **Apple Standard** | M2 Max / M3 Max (32GB) | 32GB unified | 45–90s | Full mflux throughput |
| **Apple High-End** | M4 Max / M4 Ultra (64–128GB) | 64–128GB unified | 20–40s | Near RTX 4090 equivalent |

**For FLUX 3 Dev (upcoming estimate)**: 24GB+ VRAM or 48GB+ Apple Silicon for images; 40–80GB VRAM (or M4 Ultra) for video.

---

## 8. Cost Analysis: API vs. Local

### BFL API pricing (current FLUX.2 basis; FLUX.3 TBD)

| Resolution | Approx MP | API Price |
|-----------|----------|-----------|
| 512×512 | 0.25 MP | ~$0.008 |
| 1024×1024 | 1 MP | ~$0.030 |
| 1920×1080 | ~2 MP | ~$0.060 |
| 2048×2048 | 4 MP | ~$0.120 |

**Video pricing (FLUX.3)**: Not yet announced. Competitor reference: Runway ~$0.05/sec, Kling ~$0.03–0.10/sec. FLUX.3 Video likely in the $0.05–0.15/sec range.

### Cloud GPU self-hosting

| Provider | GPU | Per Hour | Best for |
|----------|-----|---------|---------|
| RunPod | RTX 4090 | ~$0.69/hr | Rapid prototyping |
| RunPod | A100 80GB | ~$1.89/hr | Batch generation |
| Vast.ai | RTX 3090 | ~$0.25–0.40/hr | Low-cost experimentation |
| Lambda | A10 24GB | ~$0.60/hr | Stable production |

**Break-even (FLUX.1 dev, 1024px)**:
- API: $0.03/image
- RunPod RTX 4090: ~15s/image → 240 images/hr → $0.0029/image (**90% cheaper**)
- Own RTX 4090 (~$1,800): at 2,000 images/month, API would cost $60/mo → hardware pays back in 30 months

**Recommended strategy**:
- <500 images/month: use API, no hassle
- 500–5,000 images/month: cloud GPU wins on cost
- >5,000 images/month, privacy requirements, or fine-tuning needs: own hardware

---

## 9. Why FLUX.3 Is Worth Watching

There are many video generation tools. FLUX.3's logic is structurally different from all of them.

**Others**: image model + video extension + separate audio model, stitched together in post.

**FLUX.3**: one model from the start, with video prediction consuming >95% of training compute. Audio and action prediction are natural extensions of a world model that already learned physics.

This gives FLUX.3 a structural advantage in **physical consistency** — audio-visual alignment, motion that obeys physical laws — not from post-processing, but because it was never separating these things to begin with.

That the same model can drive robots on an Audi production line is the most direct proof of that world model quality.

$300M Series B. Martin Scorsese as an advisor. Real factory deployment. This isn't another demo.

---

*Sources: blackforestlabs.ai/blog/flux-3, blackforestlabs.ai/blog/flux-3-mimic, github.com/black-forest-labs/flux. Compiled 2026-07-25.*

© 2026 Author: Mycelium Protocol
