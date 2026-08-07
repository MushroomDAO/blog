---
title: "TRELLIS.2：微软 4B 参数图像转 3D 生成模型，引入原生 O-Voxel 表示"
titleEn: "microsoft-trellis2-native-3d-generation-o-voxel-pbr"
description: "微软开源的 4B 参数 3D 生成模型。引入 O-Voxel（无等值面约束的稀疏体素）解决复杂拓扑问题，支持开放曲面、非流形几何和内部封闭结构。H100 上 512³ 约 3 秒，1024³ 约 17 秒。支持完整 PBR 材质（颜色/粗糙度/金属度/透明度），MIT License，arXiv 2512.14692，当前 10.4k stars。"
descriptionEn: "Microsoft's open-source 4B-parameter image-to-3D generation model. Introduces O-Voxel (field-free sparse voxels) to handle arbitrary topology including open surfaces, non-manifold geometry, and internal enclosed structures. 512³ in ~3s, 1024³ in ~17s on H100. Full PBR material support. MIT License, arXiv 2512.14692, 10.4k stars."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["3D生成", "微软", "O-Voxel", "PBR材质", "图像转3D", "生成模型", "Mycelium"]
heroImage: "../../assets/images/microsoft-trellis2-native-3d-generation-o-voxel-pbr-banner.jpg"
---

*by Mycelium Protocol*

---

3D 资产生成领域长期存在一个结构性障碍：现有方法依赖等值面（iso-surface field）表示，意味着生成结果只能是封闭的、流形的几何体。衣物、树叶、内部中空结构——这些在真实世界中极为常见的物体，传统方法要么无法生成，要么生成后有损转换。

TRELLIS.2 引入了一种不同的表示：**O-Voxel**，一种无等值面约束的稀疏体素结构。4B 参数模型，MIT License，10.4k stars。

GitHub: https://github.com/microsoft/TRELLIS.2 | arXiv: 2512.14692

---

## 核心创新：O-Voxel 表示

传统 3D 生成模型把形状表示为 SDF（有符号距离场）或 NeRF 等隐式字段，从中提取等值面得到 Mesh。这种路径的根本限制是：等值面只能表示封闭的流形曲面。

**O-Voxel（Field-Free 稀疏体素）** 打破了这个约束：

| 几何类型 | 传统方法 | TRELLIS.2 |
|---------|---------|-----------|
| 开放曲面（衣物、叶片） | ❌ 有损 | ✅ 原生支持 |
| 非流形几何 | ❌ 退化 | ✅ 原生支持 |
| 内部封闭结构 | ❌ 丢失 | ✅ 原生支持 |

O-Voxel 不通过等值面提取 Mesh，而是直接在稀疏体素空间中表示和操作几何体，消除了拓扑约束。

转换效率：
- **Textured Mesh → O-Voxel**：< 10 秒（单 CPU）
- **O-Voxel → Textured Mesh**：< 100ms（CUDA）

两个方向的转换都是 rendering-free 和 optimization-free 的，没有迭代优化过程。

---

## 生成速度

在 NVIDIA H100 上，不同分辨率的生成时间：

| 分辨率 | 总时长 | 形状 | 材质 |
|--------|--------|------|------|
| 512³ | **~3 秒** | 2s | 1s |
| 1024³ | **~17 秒** | 10s | 7s |
| 1536³ | **~60 秒** | 35s | 25s |

模型通过 Sparse 3D VAE 进行 16× 空间下采样，把资产编码到紧凑的隐空间中，再用标准 DiT（Diffusion Transformer）做生成。这个路径不需要针对 3D 设计特殊架构——标准 DiT 加上合适的 3D 表示就能运行。

---

## PBR 材质全覆盖

TRELLIS.2 不只生成颜色，而是对四个表面属性建模：

- **Base Color**（基础颜色）
- **Roughness**（粗糙度）
- **Metallic**（金属度）
- **Opacity**（透明度）

导出为 GLB 格式，带完整 PBR 材质贴图，可以直接在 Blender、Unity、Unreal Engine 中打开和使用。

注意：GLB 默认导出为 `OPAQUE` 模式，透明度通道保留在贴图中但默认未激活。需要在 3D 软件中手动将纹理 Alpha 通道连接到材质的 Opacity 输入，才能启用透明效果。

---

## 使用方式

### 快速安装

```bash
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2

# 创建新 conda 环境并安装所有依赖
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

要求：Linux 系统，NVIDIA GPU（≥24GB 显存），CUDA Toolkit 12.4（推荐），Python 3.8+。

### 代码示例：图像转 3D

```python
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import cv2
import imageio
from PIL import Image
import torch
from trellis2.pipelines import Trellis2ImageTo3DPipeline
from trellis2.utils import render_utils
from trellis2.renderers import EnvMap
import o_voxel

# 环境光贴图
envmap = EnvMap(torch.tensor(
    cv2.cvtColor(cv2.imread('assets/hdri/forest.exr', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB),
    dtype=torch.float32, device='cuda'
))

# 加载模型
pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

# 输入图像，生成 3D
image = Image.open("assets/example_image/T.png")
mesh = pipeline.run(image)[0]
mesh.simplify(16777216)  # nvdiffrast 限制

# 渲染视频
video = render_utils.make_pbr_vis_frames(render_utils.render_video(mesh, envmap=envmap))
imageio.mimsave("sample.mp4", video, fps=15)

# 导出 GLB
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices, faces=mesh.faces,
    attr_volume=mesh.attrs, coords=mesh.coords,
    attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    decimation_target=1000000, texture_size=4096,
    remesh=True, remesh_band=1, remesh_project=0, verbose=True
)
glb.export("sample.glb", extension_webp=True)
```

输出：`sample.mp4`（带 PBR 材质和环境光的渲染视频）+ `sample.glb`（可在 3D 软件中直接打开）。

### Web Demo

```bash
python app.py
```

本地启动 Web 界面，上传图片即可得到 3D 资产。

---

## 模型权重

| 模型 | 参数量 | 分辨率范围 | 获取 |
|------|--------|-----------|------|
| TRELLIS.2-4B | 40 亿 | 512³ - 1536³ | [Hugging Face](https://huggingface.co/microsoft/TRELLIS.2-4B) |

Hugging Face 上同时提供 [在线 Demo](https://huggingface.co/spaces/microsoft/TRELLIS.2)，无需本地部署即可测试。

---

## Roadmap 完成情况

- ✅ 论文发布（arXiv 2512.14692）
- ✅ 图像转 3D 推理代码
- ✅ 4B 预训练权重
- ✅ Hugging Face Spaces Demo
- ✅ 形状条件纹理生成代码
- ✅ 训练代码

全部 Roadmap 条目已完成。

---

## 技术背景

TRELLIS.2 是 Microsoft Research 的 TRELLIS 系列的第二代，相比原版最核心的变化是引入 O-Voxel 表示，从根本上解决了原 TRELLIS 无法处理任意拓扑的限制。原 TRELLIS 同样来自 Microsoft，已在 3D 生成领域被广泛引用；TRELLIS.2 在保留 DiT 骨干和 Sparse VAE 架构的同时，把表示层从字段隐式提取替换为原生稀疏体素，是一次针对表示层的精准升级。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## TRELLIS.2: Microsoft's 4B-Parameter Image-to-3D Model with Native O-Voxel Representation

*by Mycelium Protocol*

---

A structural barrier has long persisted in 3D asset generation: most methods rely on iso-surface field representations, which means generated geometry must be closed and manifold. Clothing, leaves, internally hollow structures — objects common in the real world — either can't be generated or require lossy conversion.

TRELLIS.2 introduces a different representation: **O-Voxel**, a field-free sparse voxel structure. 4B parameters, MIT License, 10.4k stars.

GitHub: https://github.com/microsoft/TRELLIS.2 | arXiv: 2512.14692

---

### Core Innovation: O-Voxel Representation

Traditional 3D generation models represent shapes as SDFs or NeRF-style implicit fields, extracting an iso-surface to get a mesh. The fundamental limit of this approach: iso-surfaces can only represent closed, manifold surfaces.

**O-Voxel (Field-Free sparse voxels)** breaks this constraint:

| Geometry type | Traditional | TRELLIS.2 |
|---------------|-------------|-----------|
| Open surfaces (clothing, leaves) | ❌ Lossy | ✅ Native |
| Non-manifold geometry | ❌ Degenerate | ✅ Native |
| Internal enclosed structures | ❌ Lost | ✅ Native |

O-Voxel doesn't extract a mesh through an iso-surface — it represents and operates on geometry directly in sparse voxel space, eliminating topological constraints.

Conversion efficiency:
- **Textured Mesh → O-Voxel**: < 10s (single CPU)
- **O-Voxel → Textured Mesh**: < 100ms (CUDA)

Both directions are rendering-free and optimization-free — no iterative optimization loop.

---

### Generation Speed

On NVIDIA H100:

| Resolution | Total | Shape | Material |
|-----------|-------|-------|---------|
| 512³ | **~3s** | 2s | 1s |
| 1024³ | **~17s** | 10s | 7s |
| 1536³ | **~60s** | 35s | 25s |

The model uses a Sparse 3D VAE with 16× spatial downsampling to encode assets into a compact latent space, then runs a vanilla DiT for generation. No 3D-specific architecture is needed — a standard DiT with the right 3D representation is sufficient.

---

### Full PBR Material Coverage

TRELLIS.2 doesn't just generate colors — it models four surface attributes:

- **Base Color**
- **Roughness**
- **Metallic**
- **Opacity**

Exports to GLB format with complete PBR material maps, ready to open in Blender, Unity, or Unreal Engine.

Note: GLB exports in `OPAQUE` mode by default. The alpha channel is preserved in the texture map but inactive initially. To enable transparency, manually connect the texture's alpha channel to the material's Opacity input in your 3D software.

---

### Usage

**Installation:**

```bash
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2

# Create new conda env and install all dependencies
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

Requirements: Linux, NVIDIA GPU (≥24GB VRAM), CUDA Toolkit 12.4 (recommended), Python 3.8+.

**Image-to-3D (minimal example):**

```python
from trellis2.pipelines import Trellis2ImageTo3DPipeline
from PIL import Image

pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

image = Image.open("your_image.png")
mesh = pipeline.run(image)[0]
```

**Web demo:**

```bash
python app.py
```

Launches a local web interface — upload an image, get a 3D asset.

---

### Pretrained Weights

| Model | Parameters | Resolution range | Access |
|-------|-----------|-----------------|--------|
| TRELLIS.2-4B | 4 Billion | 512³ – 1536³ | [Hugging Face](https://huggingface.co/microsoft/TRELLIS.2-4B) |

An [online demo](https://huggingface.co/spaces/microsoft/TRELLIS.2) is available on Hugging Face Spaces — no local setup needed to test.

---

### Full Roadmap Completed

All roadmap items are now shipped:

- ✅ Paper (arXiv 2512.14692)
- ✅ Image-to-3D inference code
- ✅ Pretrained 4B weights
- ✅ Hugging Face Spaces demo
- ✅ Shape-conditioned texture generation
- ✅ Training code

---

### Context

TRELLIS.2 is the second generation of Microsoft Research's TRELLIS series. The most significant change from TRELLIS.1 is the introduction of O-Voxel representation, which addresses the original's inability to handle arbitrary topology. The original TRELLIS retained the same DiT backbone and Sparse VAE architecture; TRELLIS.2 replaces the representation layer — swapping implicit field extraction for native sparse voxels. It's a precise, targeted upgrade at the representation layer while keeping the rest of the architecture unchanged.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
