---
title: "depth-anything.cpp：LocalAI 团队把 Depth Anything 3 移植到 C++，CPU 速度超 PyTorch 30%"
titleEn: "depth-anything.cpp: LocalAI Ports Depth Anything 3 to C++/ggml — 30% Faster Than PyTorch on CPU"
description: "LocalAI 团队用 C++17/ggml 从头实现 Depth Anything 3（字节跳动），推理不需要 Python/PyTorch/CUDA 工具链，CPU 速度比 PyTorch 快 1.31x，量化后 99MB，单张图片输出深度图、置信度、相机姿态、3D 点云，支持 glb/COLMAP/PLY 导出，MIT 开源。"
descriptionEn: "The LocalAI team built a from-scratch C++17/ggml port of Depth Anything 3 (ByteDance). No Python/PyTorch/CUDA at inference. CPU is 1.31x faster than PyTorch, 99MB quantized. Single image outputs depth + confidence + camera pose + 3D point cloud with glb/COLMAP/PLY export. MIT licensed."
pubDate: "2026-07-17"
updatedDate: "2026-07-17"
category: "Tech-Experiment"
tags: ["深度估计", "C++", "ggml", "GGUF", "计算机视觉", "3D", "开源", "LocalAI"]
heroImage: "../../assets/images/depth-anything-cpp-ggml-banner.jpg"
---

> **GitHub**：[mudler/depth-anything.cpp](https://github.com/mudler/depth-anything.cpp) · MIT  
> **作者**：LocalAI 团队（[@mudler](https://github.com/mudler) Ettore Di Giacinto）  
> **GGUF 模型**：[mudler/depth-anything.cpp-gguf](https://huggingface.co/mudler/depth-anything.cpp-gguf)

---

## 它做了什么

Depth Anything 3 是字节跳动 Seed 团队开源的单目深度估计模型——给一张普通照片，它能估算出每个像素到相机的距离，还能推算出相机的姿态（位置和朝向）。这类能力是 3D 重建、自动驾驶感知、AR 空间定位的基础。

问题在于：官方实现依赖 Python + PyTorch + CUDA 工具链，这在部署时是一个不小的负担。

`depth-anything.cpp` 做的事情是：**用 C++17 和 ggml 从头重写整个推理路径**，推理时不再需要任何 Python、PyTorch 或 CUDA——只需要一个自包含的 GGUF 文件和一个小型原生库。

---

## 数字对比

在 AMD Ryzen 9 9950X3D（16核/32线程）上，`threads=16`，504×336 分辨率，持续运行 25 次取均值：

| 引擎 | 量化 | 模型大小 | 加载时间 | 推理时间 | 峰值内存 | vs PyTorch |
|---|---|---|---|---|---|---|
| PyTorch | f32 | 516 MB | 749 ms | 416.9 ms | 1328 MB | 1.00x |
| **C++/ggml** | f32 | 393 MB | **112 ms** | **346.4 ms** | **614 MB** | **1.20x** |
| **C++/ggml** | q8_0 | 142 MB | **40 ms** | **319.4 ms** | **363 MB** | **1.31x** |
| **C++/ggml** | q4_k | **99 MB** | **25 ms** | 395.2 ms | **320 MB** | 1.05x |

几个值得注意的数字：
- **加载速度**：q8_0 比 PyTorch 快 **18.7x**，q4_k 比 PyTorch 快 **30x**
- **内存**：q8_0 峰值内存是 PyTorch 的 **27%**（363 vs 1328 MB）
- **精度**：每种量化格式的端到端深度输出与参考 PyTorch 实现相关系数 **1.0**（逐组件验证）

速度超过 PyTorch 的关键在于缓存了两个位置编码（DPT head UV embedding 和 backbone bicubic pos-embed），这两个编码只依赖于输入分辨率，每次前向传播都重新计算是不必要的。缓存后每次前向节省了约 95ms。

GPU 上（NVIDIA GB10/Grace Blackwell），CUDA 路径与 PyTorch tuned cuDNN 推理速度相当（47.3 vs 47.3 ms），但加载速度快 1.75-2.9x。

---

## 输出什么

给一张图，depth-anything.cpp 能输出：

- **密集深度图**：每像素深度（metric 或相对深度），PFM 格式（无损浮点）+ PNG 可视化
- **置信度图**：每像素预测置信度
- **天空掩码**（mono/metric 模型）
- **相机外参（3x4 矩阵）+ 内参（3x3 矩阵）**：相机在世界坐标系中的位置和朝向
- **光线姿态**：从辅助光线场求解的相机姿态
- **3D 点云**：从深度图反投影到三维空间
- **3D 高斯**（giant 模型）

导出格式：**glb**（glTF 2.0）、**COLMAP**（cameras/images/points3D）、**PLY**，全部不依赖 trimesh/pycolmap。

---

## 支持的模型家族

所有 DA3 官方 checkpoint 都可以用 Python 脚本转换成 GGUF 后使用：

| 模型 | 骨干 | 输出 |
|---|---|---|
| DA3-SMALL | ViT-S | 深度 + 置信度 + 姿态 |
| DA3-BASE | ViT-B | 深度 + 置信度 + 姿态 |
| DA3-LARGE | ViT-L | 深度 + 置信度 + 姿态 |
| DA3-GIANT | ViT-g | 深度 + 置信度 + 姿态 + 3D 高斯 |
| DA3MONO-LARGE | ViT-L | 深度 + 天空掩码 |
| DA3METRIC-LARGE | ViT-L | metric 深度 + 天空 |
| DA3NESTED-GIANT-LARGE | ViT-g + ViT-L | 对齐 metric 深度 + 姿态（双分支） |

同样支持 **Depth Anything V2**（相对深度 + metric 深度，indoor/outdoor 各自量程）。

---

## 5 分钟跑起来

```bash
git clone --recursive https://github.com/mudler/depth-anything.cpp
cd depth-anything.cpp
cmake -B build -DDA_BUILD_CLI=ON
cmake --build build -j
# 产出：build/examples/cli/da3-cli
```

**用预转换 GGUF（最快路径）**：

```bash
# 直接下载 HuggingFace 上已有的 GGUF
# https://huggingface.co/mudler/depth-anything.cpp-gguf

CLI=build/examples/cli/da3-cli
M=models/depth-anything-base-q8_0.gguf

# 基本深度估计
$CLI depth --model $M --input photo.jpg --pfm depth.pfm --png depth.png

# 深度 + 相机姿态
$CLI depth --model $M --input photo.jpg --pose pose.json

# 3D 导出（glb + COLMAP）
$CLI depth --model $M --input photo.jpg --glb scene.glb --colmap colmap_out/

# 多视角深度 + 姿态
$CLI depth --model $M --input a.jpg --input b.jpg --out-prefix scene
```

**GPU 加速**（CUDA）：

```bash
cmake -B build -DDA_GGML_CUDA=ON
cmake --build build -j
```

**Apple Silicon（Metal）**：

```bash
cmake -B build -DDA_GGML_METAL=ON
cmake --build build -j
```

---

## C API：嵌入到你自己的项目

`libdepthanything.so` 提供了一个扁平的 C ABI（`include/da_capi.h`），可以从 C、C++、Go、Rust 调用：

```c
da_ctx* ctx = da_capi_load("model.gguf", /*threads*/ 8);

int h, w, is_metric;
float *depth, *conf, *sky, ext[12], intr[9];

// 稠密深度 + 相机姿态
da_capi_depth_dense(ctx, "photo.jpg", &h, &w, &depth, &conf, &sky, ext, intr, &is_metric);

// 3D 点云
int n; float *xyz; unsigned char *rgb;
da_capi_points(ctx, "photo.jpg", 1.0f, &n, &xyz, &rgb);

// 导出 glb
da_capi_export_glb(ctx, "photo.jpg", "scene.glb");

da_capi_free_floats(depth);
da_capi_free(ctx);
```

编译时加 `-DDA_SHARED=ON` 生成共享库。这个 C API 是 LocalAI 深度估计后端的底层实现。

---

## 和 LocalAI 集成

depth-anything.cpp 作为 LocalAI 的原生后端（Go gRPC + purego），暴露 `POST /v1/depth` REST 接口：

```bash
# 启动 LocalAI with 深度估计模型
local-ai run depth-anything-3-base
```

```bash
# 请求：全量输出（深度 + 姿态 + 点云）
curl http://localhost:8080/v1/depth \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "depth-anything-3-base",
    "src": "photo.jpg",
    "include_depth": true,
    "include_pose": true,
    "include_points": true
  }'
```

这意味着可以通过 LocalAI 的 OpenAI 兼容接口，在任何硬件上运行深度估计，不需要 Python 环境。

---

## 为什么 C++/ggml 而不是直接用 PyTorch

几个关键优势：

| | PyTorch | depth-anything.cpp |
|---|---|---|
| 推理依赖 | Python + PyTorch + CUDA toolkit | 无（纯 C++ 二进制） |
| 模型格式 | 多文件 `.pth` | 单文件 GGUF（含所有元数据） |
| 冷启动（f32） | 749 ms | 112 ms |
| 嵌入方式 | 通过子进程/微服务 | 直接链接 .so，C ABI |
| 量化 | 需要额外工具 | 内置 q4/q5/q6/q8 |

对于需要**在生产环境部署单目深度估计**的场景（机器人、AR、3D 重建管线），depth-anything.cpp 提供了 PyTorch 方案无法提供的部署简洁性。

---

## 进行中的 PR

当前活跃 PR（#2）：`feat: Demo server, Video, Voxels and elements of VSLAM`——视频流处理、体素重建和视觉 SLAM 元素，这意味着下一阶段目标是实时 3D 场景重建流水线。

---

## 一句话总结

depth-anything.cpp 把字节跳动的 Depth Anything 3 从 PyTorch 移植到了纯 C++/ggml：不需要 Python 环境，推理比 PyTorch 快 30%，模型压缩到 99MB，单张图片出完整的深度 + 相机姿态 + 3D 点云。如果你在做 3D 重建、AR 或机器人感知，这个库值得认真考虑。

© 2026 Author: Mycelium Protocol

<!--EN-->

## depth-anything.cpp: C++/ggml Port of Depth Anything 3 — 30% Faster Than PyTorch on CPU

**GitHub**: [mudler/depth-anything.cpp](https://github.com/mudler/depth-anything.cpp) · MIT  
**By**: LocalAI team ([@mudler](https://github.com/mudler), Ettore Di Giacinto)

### What It Is

A from-scratch C++17/ggml port of Depth Anything 3 (ByteDance Seed) for inference without Python, PyTorch, or CUDA. One self-contained GGUF file, one native library — and now faster than PyTorch on CPU.

### Performance

On AMD Ryzen 9 9950X3D, 504×336, 25-run sustained average:

| Engine | Quant | Size | Load | Infer | RAM | vs PyTorch |
|---|---|---|---|---|---|---|
| PyTorch | f32 | 516 MB | 749 ms | 416.9 ms | 1328 MB | 1.00× |
| C++/ggml | f32 | 393 MB | 112 ms | 346.4 ms | 614 MB | **1.20×** |
| C++/ggml | q8_0 | 142 MB | 40 ms | 319.4 ms | 363 MB | **1.31×** |
| C++/ggml | q4_k | 99 MB | 25 ms | 395.2 ms | 320 MB | 1.05× |

Key insight: two positional embeddings were recomputed every forward even though they only depend on input geometry. Caching them saves ~95 ms/forward.

### What It Outputs

From a single image: dense depth map, per-pixel confidence, sky mask, camera extrinsics (3×4) + intrinsics (3×3), ray-based pose, 3D point cloud, 3D Gaussians (giant model). Exports: glb (glTF 2.0), COLMAP, PLY.

### Supported Models

Full DA3 family: Small/Base/Large/Giant, MONO-LARGE (depth+sky), METRIC-LARGE, NESTED-GIANT-LARGE (two-branch aligned metric). Also runs Depth Anything V2 (relative + metric, indoor/outdoor).

### Quick Start

```bash
git clone --recursive https://github.com/mudler/depth-anything.cpp
cmake -B build -DDA_BUILD_CLI=ON && cmake --build build -j

# Run inference
./build/examples/cli/da3-cli depth --model model.gguf --input photo.jpg --png depth.png --pose pose.json --glb scene.glb
```

GPU: `-DDA_GGML_CUDA=ON` or `-DDA_GGML_METAL=ON`

### C API for Embedding

Flat C ABI (`include/da_capi.h`, ABI version 4) — embed from C, C++, Go, or Rust. Build with `-DDA_SHARED=ON`. Powers the LocalAI backend.

### LocalAI Integration

Exposed as `POST /v1/depth` via LocalAI — full output (depth + pose + point cloud) through an OpenAI-compatible REST endpoint, on any hardware, no Python.

### Bottom Line

If you need monocular depth estimation without a Python runtime — for 3D reconstruction, AR, or robotics — depth-anything.cpp gives you PyTorch-quality output at 30% faster CPU speed, in a 99 MB file, with a flat C API for easy embedding.

© 2026 Author: Mycelium Protocol
