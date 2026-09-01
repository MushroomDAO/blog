---
title: "4DAnyone：用一段普通竖屏视频，重建任何人的 4D 模型"
titleEn: "4DAnyone: Reconstruct Anyone in 4D from a Casual Portrait Video"
description: "ant-research/4DAnyone ⭐1051，蚂蚁研究院 SIGGRAPH Asia 2026 成果，从单目竖屏视频生成多视角视频，实现 4D Gaussian Splatting 重建，支持 6/24/48 视角全轨道相机，峰值显存 25.4 GiB，Apache 2.0。"
descriptionEn: "ant-research/4DAnyone ⭐1051 — Ant Research, SIGGRAPH Asia 2026. Takes a casual monocular portrait video and generates multi-view videos for 4D Gaussian Splatting reconstruction. 6/24/48-view camera configurations, 25.4 GiB peak GPU memory, Apache 2.0."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Research"
tags: ["4D Gaussian Splatting", "4DGS", "video generation", "multi-view", "SIGGRAPH", "3D reconstruction", "human avatar", "generative AI", "Ant Research"]
heroImage: "../../assets/images/4danyone-monocular-video-4d-gaussian-splatting-multi-view-banner.jpg"
author: "Mycelium Protocol"
---

## 一段普通视频，变成可以从任意角度查看的 4D 人体

拿一段竖屏手机视频——街拍、跳舞、日常走路——把里面的人重建成一个可以在三维空间里自由查看、还保留时间轴的 4D 模型。

这是 **4DAnyone** 做的事。蚂蚁研究院（Ant Research）的成果，被 **SIGGRAPH Asia 2026** 接收，2026 年 8 月 10 日开源，Apache 2.0。

⭐ **1,051**，arXiv 论文 [2608.20335](https://arxiv.org/abs/2608.20335)。

---

## 技术路径：单目视频 → 多视角视频 → 4DGS 重建

4DAnyone 的核心是一个两步管线：

```
输入：单目竖屏视频（一个摄像头，一个人）
      ↓
Step 1: 运动恢复（GVHMR，可复用缓存）
      ↓
Step 2: 多视角视频生成
        —— 并行化姿态编码 + VAE 处理（跨 GPU）
        —— 生成目标视角的视频帧
      ↓
输出：N 个视角的多视角视频 + 相机参数
      ↓
下游：4D Gaussian Splatting 重建（nerfstudio）
```

**关键点**：4D = 3D 空间 + 时间维度。普通 3DGS 是静态的；4DGS 保留了人物的运动，重建的结果是可以播放的、在三维空间里自由查看的动态人体，而不只是一个静止的扫描。

---

## 灵活的相机配置

4DAnyone 支持自定义目标视角数、仰俯角层数和偏航角范围，内置四种典型配置：

### 6 视角全轨道

360° 均匀分布的 6 个视角，适合快速测试：

```bash
python inference.py \
    --video_path "data/source/your_video.mp4" \
    --views_per_layer 6
```

### 24 视角全轨道

更密集的 360° 覆盖，**推荐用于 4DGS 重建**：

```bash
python inference.py \
    --video_path "data/source/your_video.mp4" \
    --views_per_layer 24
```

### 48 视角三层仰俯

分布在三个仰俯角环上，适合自由视点渲染：

```bash
python inference.py \
    --video_path "data/source/your_video.mp4" \
    --views_per_layer 16 --layer_pitches '[-10,15,35]'
```

### 24 视角前向弧（两层）

正面 180° 范围内的密集双层覆盖：

```bash
python inference.py \
    --video_path "data/source/your_video.mp4" \
    --views_per_layer 12 --layer_pitches '[0,30]' --start_yaw -90 --yaw_span 180
```

主要参数：

| 参数 | 含义 |
|---|---|
| `views_per_layer` | 每个仰俯层的均匀视角数（须能被 4 或 6 整除）|
| `layer_pitches` | 每层的仰俯角（正值 = 摄像机在人上方）|
| `start_yaw` | 第一个视角的水平角（0° = 正面）|
| `yaw_span` | 每层覆盖的水平角度范围 |
| `gpu_ids` | 用于并行化的 GPU，默认用全部可见 GPU |

---

## 输出结构

```text
data/
├── gvhmr/results/<clip>/          # 运动恢复结果（可跨任务复用）
└── fdanyone/<clip>/
    ├── metadata.json              # 运行设置、时间、资源消耗
    ├── cameras.json               # 最终 N 视角相机参数
    ├── skeletons/                 # 骨骼视频
    └── videos/
        ├── sparse/                # 默认 24 视角 RCP 稀疏提案
        └── dense/                 # 生成的目标视角视频
```

---

## 性能与硬件要求

截至 2026-08-28 的最新优化：

- **峰值显存**：**25.4 GiB**（通过姿态预计算和显存高效算子降低）
- **端到端加速**：比原始版本快 **1.42×**（通过跨 GPU 并行化姿态编码和 VAE 处理）

已在 H20-3E、H200、RTX 5880 Ada、RTX A6000 等 GPU 上测量。可选安装 FlashAttention-3 或 SageAttention 进一步提速（按 FA3 > SageAttention > PyTorch SDPA 顺序自动选择）。

**输入视频要求**：
- 分辨率：720p 或更高（推荐 1080p）
- 比例：9:16 竖屏
- 内容：一个人，全身或半身
- 帧数：至少 121 帧
- 摄像机运动：轻微

---

## Roadmap

| 状态 | 目标 |
|---|---|
| ✅ 已完成 | 峰值显存降至 32 GiB 以下（现已 25.4 GiB）|
| ✅ 已完成 | 1.42× 端到端加速 |
| ✅ 已完成 | nerfstudio 3DGS 重建支持 |
| 🔲 计划中 | Sol-Engine 集成（预计再提速 **2×**）|
| 🔲 计划中 | 模型蒸馏用于少步推理（预计提速 **5×**）|
| 🔲 计划中 | 开源 4DGS 重建支持 |

---

## 安装与运行

```bash
git clone https://github.com/ant-research/4DAnyone.git
cd 4DAnyone
git submodule update --init third_party/GVHMR

conda create -n 4danyone python=3.11 -y
conda activate 4danyone
pip install -r requirements.txt

# 首次运行会自动下载模型，也可手动下载
python scripts/download_smplx.py
python scripts/download_model.py
python scripts/download_example.py
```

---

## 为什么值得关注

现有生成任意人物 4D 模型的方案通常需要多摄像机同步拍摄，或者高质量结构光扫描设备。4DAnyone 把这个门槛降到一段普通手机视频——约束条件是竖屏、一个人、轻微摄像机运动。

从研究角度，这是 video world model 和 4D Gaussian Splatting 两个方向的交汇：用生成模型补全单目视频中缺失的视角信息，然后用 4DGS 把这些多视角视频变成可渲染的 4D 表示。SIGGRAPH Asia 是计算机图形学顶会，被接收说明技术已经通过严格同行评审。

从应用角度，能想到的场景包括：虚拟试衣（从一段走秀视频直接建模）、影视特效（从普通拍摄素材恢复 4D 角色）、游戏（从玩家视频生成可动角色）、VR/AR（实时场景重建）。

**GitHub**: [ant-research/4DAnyone](https://github.com/ant-research/4DAnyone) ⭐1051  
**论文**: [arXiv:2608.20335](https://arxiv.org/abs/2608.20335) · SIGGRAPH Asia 2026  
**项目页**: [4danyone.github.io](https://4danyone.github.io)  
**许可**: Apache 2.0

<!--EN-->

## 4DAnyone: Reconstruct Anyone in 4D from a Casual Portrait Video

Take a portrait-mode phone video — street footage, a dance clip, someone walking — and reconstruct the person as a 4D model: freely viewable in 3D space, with the time axis preserved.

That's what **4DAnyone** does. It's a result from **Ant Research** (Ant Group), accepted at **SIGGRAPH Asia 2026**, open-sourced on August 10, 2026, under Apache 2.0.

⭐**1,051** · arXiv [2608.20335](https://arxiv.org/abs/2608.20335)

---

## Pipeline: Monocular Video → Multi-View Videos → 4DGS Reconstruction

4DAnyone is a two-stage pipeline:

```
Input: monocular portrait video (one camera, one person)
      ↓
Stage 1: Motion recovery via GVHMR (cached and reusable)
      ↓
Stage 2: Multi-view video generation
         — Parallel pose encoding + VAE across GPUs
         — Generate target-view video frames
      ↓
Output: N-view multi-view videos + camera parameters
      ↓
Downstream: 4D Gaussian Splatting reconstruction (nerfstudio)
```

**The key insight**: 4D = 3D space + time. Standard 3DGS produces a static scan. 4DGS preserves the person's motion — the output is a dynamic human model you can play back and view from any angle, not just a frozen mesh.

---

## Flexible Camera Configurations

4DAnyone supports configurable target-view counts, pitch layers, and yaw coverage. Four common setups:

**6-View Full Orbit** — compact 360° for quick tests  
**24-View Full Orbit** — dense 360°, recommended for 4DGS reconstruction  
**48-View, 3 Pitch Layers** — distributes views across three elevation rings for free-viewpoint rendering  
**24-View Frontal Arc (2 layers)** — dense coverage of the frontal 180°

Key arguments:

| Argument | Meaning |
|---|---|
| `views_per_layer` | Evenly spaced views per pitch layer (must be divisible by 4 or 6) |
| `layer_pitches` | Pitch angles in degrees; positive = camera above subject |
| `start_yaw` | Horizontal angle of first view (0° = front) |
| `yaw_span` | Horizontal range covered per layer |
| `gpu_ids` | GPUs for parallel processing (defaults to all visible) |

---

## Performance

As of August 28, 2026:

- **Peak GPU memory**: **25.4 GiB** (via pose precomputation and memory-efficient operators)
- **End-to-end speedup**: **1.42×** over the original (via parallel pose encoding and VAE processing across GPUs)

Measured on H20-3E, H200, RTX 5880 Ada, and RTX A6000. Optionally install FlashAttention-3 or SageAttention for further acceleration (auto-selected in order: FA3 → SageAttention → PyTorch SDPA).

**Input requirements**: 720p+ (1080p recommended), 9:16 portrait, one person (full or upper body), 121+ frames, mild camera motion.

---

## Roadmap

| Status | Target |
|---|---|
| ✅ Done | Peak GPU memory below 32 GiB (now 25.4 GiB) |
| ✅ Done | 1.42× end-to-end speedup |
| ✅ Done | 3DGS reconstruction with nerfstudio |
| 🔲 Planned | Sol-Engine integration (expected **2× additional speedup**) |
| 🔲 Planned | Distillation for few-step inference (expected **5× speedup**) |
| 🔲 Planned | Open-source 4DGS reconstruction support |

---

## Install

```bash
git clone https://github.com/ant-research/4DAnyone.git
cd 4DAnyone
git submodule update --init third_party/GVHMR

conda create -n 4danyone python=3.11 -y
conda activate 4danyone
pip install -r requirements.txt

# Models download automatically on first run, or manually:
python scripts/download_smplx.py
python scripts/download_model.py
python scripts/download_example.py
```

---

## Why It Matters

Existing approaches to building 4D human models typically require multi-camera synchronized rigs or high-quality structured-light scanning. 4DAnyone drops the hardware requirement to a casual phone video — constrained to portrait orientation, one person, and mild camera motion.

Technically, this is the intersection of video world models and 4D Gaussian Splatting: use a generative model to fill in missing viewpoints from a monocular video, then use 4DGS to turn those multi-view videos into a renderable 4D representation. SIGGRAPH Asia is the top venue in computer graphics; acceptance signals rigorous peer review.

Application directions: virtual try-on (build from a runway walk), VFX (recover 4D characters from standard footage), games (generate playable characters from player video), VR/AR (real-time scene reconstruction).

**GitHub**: [ant-research/4DAnyone](https://github.com/ant-research/4DAnyone) ⭐1051  
**Paper**: [arXiv:2608.20335](https://arxiv.org/abs/2608.20335) · SIGGRAPH Asia 2026  
**Project page**: [4danyone.github.io](https://4danyone.github.io)  
**License**: Apache 2.0
