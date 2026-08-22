---
title: "TRELLIS.2：微软图生 3D 续作，O-Voxel 打破拓扑限制，4B 参数，3 秒 512³ 分辨率"
titleEn: "microsoft-trellis2-image-to-3d-o-voxel-pbr-native-compact"
description: "microsoft/TRELLIS.2 是 TRELLIS（CVPR'25 Spotlight）的续作，10745 stars，MIT，Python。核心创新：O-Voxel「无场」稀疏体素结构取代等值面场，天然支持开放表面（衣物/叶片）、非流形几何、内部封闭结构；4B 参数模型 512³ 分辨率 H100 上约 3 秒，1024³ 约 17 秒；完整 PBR 材质（Base Color/Roughness/Metallic/Opacity）；网格→O-Voxel <10 秒（单 CPU），O-Voxel→网格 <100ms（CUDA）；训练代码完整开源，可从头训练或微调；ComfyUI 封装已有社区版本。"
descriptionEn: "microsoft/TRELLIS.2 is the successor to TRELLIS (CVPR'25 Spotlight) — 10745 stars, MIT, Python. Core innovation: O-Voxel 'field-free' sparse voxel structure replaces iso-surface fields, natively handling open surfaces (clothing/leaves), non-manifold geometry, and internal enclosed structures. 4B-parameter model: ~3s for 512³ on H100, ~17s for 1024³. Full PBR materials (Base Color/Roughness/Metallic/Opacity). Mesh→O-Voxel under 10s (CPU), O-Voxel→Mesh under 100ms (CUDA). Full training code released; ComfyUI wrapper available."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["3D生成", "图生3D", "微软", "O-Voxel", "PBR材质", "稀疏体素", "开源模型", "DiT"]
heroImage: "../../assets/images/microsoft-trellis2-image-to-3d-o-voxel-pbr-native-compact-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：microsoft/TRELLIS.2  
论文：arxiv.org/abs/2512.14692  
HF 模型：microsoft/TRELLIS.2-4B  
HF Demo：huggingface.co/spaces/microsoft/TRELLIS.2  
许可证：MIT  
Stars：10,745  
前作：microsoft/TRELLIS（CVPR'25 Spotlight，13,477 stars）

---

## 一、TRELLIS.2 是什么

TRELLIS 是微软研究院 2024 年末发布的结构化 3D 潜空间生成模型，入选 CVPR'25 Spotlight。TRELLIS.2 是它的直接续作，核心改变是**3D 表示方式**——从「有场」的等值面结构，换成「无场」的 O-Voxel 稀疏体素。

这不是参数更大的同一个模型，而是底层表示范式的升级。

---

## 二、为什么要换表示

传统 3D 生成（包括原版 TRELLIS）使用 SDF（有符号距离场）或占用场作为表示，再用 Marching Cubes 等方法提取网格。这套流程有一个根本限制：

**等值面只能提取封闭、可定向、流形的曲面。**

现实物体很多都不是这样的：
- 衣物、叶片、薄壳（**开放表面**）：Marching Cubes 处理后漏洞百出
- 铁丝网、网格结构（**非流形几何**）：完全无法正确表示
- 箱子里的物品（**内部封闭结构**）：直接被丢弃

O-Voxel 绕过了这个问题：**不生成场，直接生成稀疏体素网格**，每个体素携带几何和材质属性，导出时直接转换，没有有损的等值面提取步骤。

---

## 三、O-Voxel 是什么

O-Voxel（Open Voxel）是 TRELLIS.2 团队开发的一套新的 3D 表示方案：

- **稀疏体素结构**：只存非空体素，内存高效
- **无场**：不依赖距离场或占用场，避免拓扑约束
- **携带完整 PBR 属性**：每个体素存储 Base Color、Roughness、Metallic、Opacity
- **双向即时转换**：
  - 网格 → O-Voxel：单 CPU < 10 秒，渲染无关、优化无关
  - O-Voxel → 网格：CUDA < 100ms

Sparse 3D VAE 对 O-Voxel 做 **16× 空间下采样**，将资产编码进紧凑的潜空间，再用 vanilla DiT（扩散变换器）进行生成。

---

## 四、性能

模型：TRELLIS.2-4B（40 亿参数）  
测试硬件：NVIDIA H100

| 分辨率 | 总耗时 | 形状 + 材质分解 |
|--------|--------|----------------|
| 512³ | **~3 秒** | 2s + 1s |
| 1024³ | **~17 秒** | 10s + 7s |
| 1536³ | **~60 秒** | 35s + 25s |

512³ 分辨率 3 秒是非常快的速度，足以支持交互式工作流。

---

## 五、快速上手

**安装**（需要 NVIDIA GPU ≥ 24GB，CUDA 12.4，Linux）：

```bash
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

**图生 3D**（最简示例）：

```python
from PIL import Image
from trellis2.pipelines import Trellis2ImageTo3DPipeline

pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

image = Image.open("your_image.png")
mesh = pipeline.run(image)[0]
mesh.simplify(16777216)  # nvdiffrast 上限

# 导出 GLB（WebP 纹理，支持透明度）
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices, faces=mesh.faces,
    attr_volume=mesh.attrs, coords=mesh.coords,
    attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5,-0.5,-0.5],[0.5,0.5,0.5]],
    decimation_target=1000000,
    texture_size=4096, remesh=True,
)
glb.export("output.glb", extension_webp=True)
```

**Web Demo**（本地运行）：

```bash
python app.py
```

不想自己部署的话，可以直接用 Hugging Face Spaces 上的演示。

---

## 六、与原版 TRELLIS 的对比

| | TRELLIS（v1） | TRELLIS.2 |
|---|---|---|
| 发布时间 | 2024-12 | 2025-11 |
| 会议 | CVPR'25 Spotlight | Tech Report |
| 3D 表示 | SLAT（稀疏结构化潜空间 + 等值面） | O-Voxel（无场稀疏体素） |
| 开放表面 | ❌ | ✅ |
| 非流形几何 | ❌ | ✅ |
| 内部结构 | ❌ | ✅ |
| PBR 材质 | 基础 | 完整（Base/Roughness/Metallic/Opacity） |
| 参数量 | 未公开（多规格） | 4B |
| 训练代码 | 未完整公开 | ✅ 完整开放 |

---

## 七、训练代码完整开放

TRELLIS.2 开放了完整的训练流水线，包括：

1. **数据预处理**：原始 3D 资产 → O-Voxel 格式（`data_toolkit/`）
2. **SC-VAE 训练**（形状和材质各一个）
3. **Flow 模型训练**（稀疏结构流 + 形状流 + 材质流）
4. **高分辨率微调**（512 → 1024）

训练数据使用 **Objaverse-XL**（Sketchfab 子集）。这意味着可以用私有 3D 资产数据集微调一个垂直领域的模型——比如游戏资产、工业零件、家具。

---

## 八、社区生态

| 项目 | 说明 |
|------|------|
| visualbruno/ComfyUI-Trellis2 | ComfyUI 封装，直接拖拽工作流 |
| UNES97/trellis-3d-docker | Docker 化部署方案 |
| microsoft/TRELLIS.2-4B（HF） | 官方模型权重 |
| HF Spaces demo | 无需本地环境，在线试用 |

---

图生 3D 的主要障碍一直是「拓扑限制」——生成的网格不干净，开放表面和复杂结构出问题。O-Voxel 在底层绕过了这个问题，而不是打补丁。训练代码全开让垂直领域微调成为可能。值得关注的方向。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## TRELLIS.2: Microsoft's Image-to-3D Successor — O-Voxel Breaks Topology Limits, 4B Params, 3-Second 512³

*by Mycelium Protocol*

---

GitHub: microsoft/TRELLIS.2  
Paper: arxiv.org/abs/2512.14692  
HF Model: microsoft/TRELLIS.2-4B  
HF Demo: huggingface.co/spaces/microsoft/TRELLIS.2  
License: MIT  
Stars: 10,745  
Predecessor: microsoft/TRELLIS (CVPR'25 Spotlight, 13,477 stars)

---

### What TRELLIS.2 Is

TRELLIS was Microsoft Research's structured 3D latent generation model, released late 2024 and accepted as a CVPR'25 Spotlight. TRELLIS.2 is its direct successor, with one fundamental change: **the 3D representation** — from iso-surface fields to O-Voxel (Open Voxel), a "field-free" sparse voxel structure.

This isn't a larger version of the same model. It's an upgrade in the underlying representation paradigm.

---

### Why Change the Representation

Traditional 3D generation — including the original TRELLIS — uses SDF or occupancy fields, then extracts meshes via Marching Cubes or similar. This has a hard topological limit:

**Iso-surfaces can only extract closed, orientable, manifold surfaces.**

Most real objects violate this:
- Clothing, leaves, thin shells (**open surfaces**): Marching Cubes produces artifacts and holes
- Wire frames, mesh structures (**non-manifold geometry**): can't be correctly represented
- Objects inside boxes (**internal enclosed structures**): silently discarded

O-Voxel sidesteps this entirely: **skip the field, generate sparse voxel grids directly**, each voxel carrying geometry and material attributes, with no lossy iso-surface extraction step at export.

---

### What O-Voxel Is

O-Voxel is a new 3D representation developed by the TRELLIS.2 team:

- **Sparse voxel structure**: only non-empty voxels stored, memory-efficient
- **Field-free**: no SDF or occupancy field, no topological constraint
- **Full PBR per voxel**: Base Color, Roughness, Metallic, Opacity
- **Instant bidirectional conversion**:
  - Mesh → O-Voxel: <10s on a single CPU, rendering-free and optimization-free
  - O-Voxel → Mesh: <100ms on CUDA

A Sparse 3D VAE applies **16× spatial downsampling** to encode assets into a compact latent space, then vanilla DiTs (diffusion transformers) handle generation.

---

### Performance

Model: TRELLIS.2-4B (4 billion parameters)  
Hardware: NVIDIA H100

| Resolution | Total time | Shape + Material |
|-----------|------------|-----------------|
| 512³ | **~3s** | 2s + 1s |
| 1024³ | **~17s** | 10s + 7s |
| 1536³ | **~60s** | 35s + 25s |

3 seconds at 512³ is fast enough for interactive workflows.

---

### Quickstart

**Install** (NVIDIA GPU ≥ 24GB VRAM, CUDA 12.4, Linux):

```bash
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

**Image to 3D** (minimal example):

```python
from PIL import Image
from trellis2.pipelines import Trellis2ImageTo3DPipeline

pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

image = Image.open("your_image.png")
mesh = pipeline.run(image)[0]
mesh.simplify(16777216)

glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices, faces=mesh.faces,
    attr_volume=mesh.attrs, coords=mesh.coords,
    attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5,-0.5,-0.5],[0.5,0.5,0.5]],
    decimation_target=1000000,
    texture_size=4096, remesh=True,
)
glb.export("output.glb", extension_webp=True)
```

For a web UI: `python app.py`. Or try the Hugging Face Spaces demo without any local setup.

---

### vs Original TRELLIS

| | TRELLIS (v1) | TRELLIS.2 |
|---|---|---|
| Released | 2024-12 | 2025-11 |
| Venue | CVPR'25 Spotlight | Tech Report |
| Representation | SLAT (structured latent + iso-surface) | O-Voxel (field-free sparse voxel) |
| Open surfaces | ❌ | ✅ |
| Non-manifold geometry | ❌ | ✅ |
| Internal structures | ❌ | ✅ |
| PBR materials | Basic | Full (Base/Roughness/Metallic/Opacity) |
| Parameters | Multiple sizes (undisclosed) | 4B |
| Training code | Partially available | ✅ Fully open |

---

### Full Training Code Released

TRELLIS.2 opens its complete training pipeline:

1. **Data preprocessing**: raw 3D assets → O-Voxel format (`data_toolkit/`)
2. **SC-VAE training** (separate shape and texture VAEs)
3. **Flow model training** (sparse structure flow + shape flow + texture flow)
4. **High-resolution fine-tuning** (512 → 1024)

Training data: **Objaverse-XL** (Sketchfab subset). This makes domain-specific fine-tuning possible — game assets, industrial parts, furniture — with private 3D asset collections.

---

### Community

| Project | Description |
|---------|-------------|
| visualbruno/ComfyUI-Trellis2 | ComfyUI wrapper for drag-and-drop workflows |
| UNES97/trellis-3d-docker | Dockerized deployment |
| microsoft/TRELLIS.2-4B (HF) | Official model weights |
| HF Spaces demo | Try online without local setup |

---

The persistent blocker for image-to-3D has been topology — generated meshes aren't clean, open surfaces break, complex structures get mangled. O-Voxel addresses this at the representation level, not as a post-processing fix. With full training code open, vertical fine-tuning is now on the table.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
