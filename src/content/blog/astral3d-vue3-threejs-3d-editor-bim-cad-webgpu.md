---
title: "Astral3D：Vue3 + Three.js 打造的免费开源 Web 3D 编辑器，支持 BIM/CAD/30+ 格式"
titleEn: "astral3d-vue3-threejs-3d-editor-bim-cad-webgpu"
description: "mlt131220/Astral3D 是基于 Vue3 + Three.js 的现代 Web 3D 编辑器，支持 30+ 模型格式（GLTF/OBJ/FBX/RVT/IFC/DWG），内置 BIM 轻量化、CAD 解析、粒子系统、插件系统、动画编辑器。在线可用，2.4K stars，WebGPU 支持在路上。"
descriptionEn: "mlt131220/Astral3D is a modern web 3D editor built on Vue3 + Three.js. Supports 30+ model formats (GLTF/OBJ/FBX/RVT/IFC/DWG), with built-in BIM lightweighting, CAD parsing, particle system, plugin system, and animation editor. Available online. 2.4K stars. WebGPU support coming."
pubDate: "2026-08-04"
updatedDate: "2026-08-04"
category: "Tech-News"
tags: ["3D编辑器", "Three.js", "Vue3", "BIM", "CAD", "WebGL", "开源", "Mycelium"]
heroImage: "../../assets/images/astral3d-vue3-threejs-3d-editor-bim-cad-webgpu-banner.jpg"
---

*by Mycelium Protocol*

---

浏览器里跑一个 3D 编辑器，支持 BIM 模型、CAD 图纸、30+ 文件格式、粒子系统、动画编辑器——这听起来像是桌面软件的功能列表，但 **[Astral3D](https://github.com/mlt131220/Astral3D)** 用 Vue3 + Three.js 把它做成了开源 Web 应用。

2.4K stars，Apache-2.0，在线 Demo 可以直接体验：[editor.astraljs.com](https://editor.astraljs.com/)。

---

## 它解决什么问题

建筑、工业、城市数字化场景里，3D 模型的 Web 端预览和编辑一直是痛点：

- **BIM 模型**（Revit `.rvt`、`.ifc`）体积大，格式闭源，浏览器里跑需要转换和轻量化处理
- **CAD 图纸**（`.dwg`、`.dxf`）需要专门的解析器
- **多格式协同**：GLTF、OBJ、FBX、GLB 各有差异，统一一套编辑器来处理很难

Astral3D 在 Three.js 基础上封装了这些能力，提供了一个完整的 Web 编辑环境，不需要安装任何桌面软件。

---

## 核心能力

### 30+ 模型格式支持

一个编辑器处理所有主流格式：

```
GLTF / GLB / OBJ / FBX / STL / DAE / 3DS / USDZ
RVT / IFC（BIM）
DWG / DXF（CAD）
PCD（点云）
……30+ 种
```

### BIM 轻量化展示

Revit（`.rvt`）和 IFC 格式的 BIM 模型在 Web 端通常体积巨大、渲染慢。Astral3D 做了轻量化处理，实现在线预览和基本属性查看，不需要装 Revit 或专用 BIM 软件。

### CAD 图纸解析（DWG/DXF）

直接在浏览器里解析 CAD 图纸并预览，支持 DWG 和 DXF 两种格式。不依赖 AutoCAD，纯 Web 端完成。

### 场景分包存储与加载

大型场景按区域分包，按需加载——解决了一次性加载整个复杂场景时的性能瓶颈。

### 动画编辑器

内置时间轴动画编辑，支持对场景中的物体设置动画关键帧。

---

## 扩展能力

Astral3D 的架构是可扩展的：

| 能力 | 说明 |
|------|------|
| **插件系统** | 自定义功能模块，官方和社区插件生态 |
| **脚本运行时** | 在编辑器内运行自定义脚本逻辑 |
| **粒子系统** | 可视化粒子效果配置 |
| **天气系统** | 场景天气效果（雨、雪、雾等） |
| **云存储集成** | 资产和场景数据的云端存储 |
| **资源中心** | 统一管理模型、材质、贴图等资产 |

---

## 即将到来

路线图上已有的计划：

- 🚧 **物理引擎支持**：Three.js 场景内的刚体/碰撞模拟
- 🚧 **WebGPU 支持**：下一代图形 API，性能大幅提升
- 🚧 **数据组件**：API 和 WebSocket 数据源直连 3D 场景
- 🚧 **低代码数据大屏**：面向可视化大屏场景
- 🚧 **WebSocket 多人协作**：实时协同编辑

---

## 技术栈

| 层 | 技术 |
|----|------|
| 3D 引擎 | Three.js r176 |
| 前端框架 | Vue 3.5.22 |
| UI 组件 | Naive UI 2.43.1 |
| CSS 方案 | UnoCSS 0.46.5 |
| 后端（可选） | Java（[astral-service](https://github.com/yx8663/astral-service)） |

---

## 快速上手

```bash
git clone https://github.com/mlt131220/Astral3D.git
cd Astral3D

# Node.js ≥ 23.11.x + PNPM
pnpm install
pnpm run sdk:build  # 先构建 SDK
pnpm run editor:dev # 启动编辑器开发服务
```

生产构建：

```bash
pnpm run editor:build
```

在线直接用：[editor.astraljs.com](https://editor.astraljs.com/)

---

## 关于许可证

Apache-2.0，但附有补充条款：

- ✅ 允许个人学习和二次开发
- ⚠️ 使用需要版权声明
- ⚠️ **商业用途需要授权**（联系杭州星孪数字科技）
- ❌ 禁止用于与杭州星孪数字科技有竞争性的业务

用于商业产品前注意确认授权。

---

## 为什么值得关注

**Web 3D 编辑能力的覆盖范围**是 Astral3D 的核心优势。大多数开源 3D Web 项目要么只做通用 3D（不处理 BIM/CAD 特殊格式），要么只做 BIM 展示（不提供完整的编辑器 UX）。Astral3D 把两者合在一套编辑器里，并叠加了粒子、天气、动画、插件扩展——这个组合在 Web 端是稀缺的。

WebGPU 支持在路上。当 WebGPU 成熟后，浏览器端渲染大型 BIM 模型的性能上限会大幅提升，Astral3D 这类基础设施的价值会进一步凸显。

2.4K stars，485 forks，持续更新中（最近更新 2026-08-04）。国内作者，有 QQ 群（1040320579）和中文社区。

仓库：[github.com/mlt131220/Astral3D](https://github.com/mlt131220/Astral3D) · 在线体验：[editor.astraljs.com](https://editor.astraljs.com/) · 文档：[editor-doc.astraljs.com](http://editor-doc.astraljs.com/)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Astral3D: Free Open-Source Web 3D Editor Built on Vue3 + Three.js — BIM, CAD, 30+ Formats

*by Mycelium Protocol*

A 3D editor running in the browser, supporting BIM models, CAD drawings, 30+ file formats, a particle system, and an animation editor — that sounds like a desktop software feature list. **[Astral3D](https://github.com/mlt131220/Astral3D)** makes it an open-source web application with Vue3 + Three.js. 2.4K stars, Apache-2.0, live demo at [editor.astraljs.com](https://editor.astraljs.com/).

### The Problem It Solves

In architecture, industrial, and urban digitization contexts, web-based 3D model viewing and editing has long been painful:

- **BIM models** (Revit `.rvt`, `.ifc`) are large, use closed formats, and require conversion and lightweighting to render in a browser
- **CAD drawings** (`.dwg`, `.dxf`) need dedicated parsers
- **Multi-format compatibility**: GLTF, OBJ, FBX, GLB each have their quirks; building a unified editor for all is hard

Astral3D wraps these capabilities over Three.js into a complete web editing environment — no desktop software installation required.

### Core Capabilities

**30+ model formats in one editor:**

```
GLTF / GLB / OBJ / FBX / STL / DAE / 3DS / USDZ
RVT / IFC (BIM)
DWG / DXF (CAD)
PCD (point cloud)
...and 30+ total
```

**BIM lightweighting**: Revit (`.rvt`) and IFC files are typically huge and slow to render on the web. Astral3D applies lightweighting to enable in-browser preview and basic property inspection — no Revit or dedicated BIM software needed.

**CAD parsing (DWG/DXF)**: Parse and preview CAD drawings directly in the browser, both DWG and DXF. No AutoCAD dependency, pure web.

**Scene chunked loading**: Large scenes are partitioned and loaded on demand, solving the performance bottleneck of loading entire complex scenes at once.

**Animation editor**: Built-in timeline animation with keyframe support for scene objects.

### Extension Capabilities

| Feature | Description |
|---------|-------------|
| **Plugin system** | Custom function modules, official and community plugin ecosystem |
| **Script runtime** | Run custom scripting logic within the editor |
| **Particle system** | Visual particle effect configuration |
| **Weather system** | Scene weather effects (rain, snow, fog, etc.) |
| **Cloud storage integration** | Cloud-backed asset and scene data |
| **Resource center** | Unified management of models, materials, and textures |

### On the Roadmap

- 🚧 **Physics engine**: Rigid body / collision simulation inside Three.js scenes
- 🚧 **WebGPU support**: Next-generation graphics API for significantly better performance
- 🚧 **Data components**: API and WebSocket data sources wired directly to 3D scenes
- 🚧 **Low-code data dashboard**: Targeted at visualization display screens
- 🚧 **WebSocket multi-user collaboration**: Real-time collaborative editing

### Tech Stack

| Layer | Tech |
|-------|------|
| 3D engine | Three.js r176 |
| Frontend | Vue 3.5.22 |
| UI components | Naive UI 2.43.1 |
| CSS | UnoCSS 0.46.5 |
| Backend (optional) | Java ([astral-service](https://github.com/yx8663/astral-service)) |

### Quick Start

```bash
git clone https://github.com/mlt131220/Astral3D.git
cd Astral3D

# Node.js ≥ 23.11.x + PNPM
pnpm install
pnpm run sdk:build   # build SDK first
pnpm run editor:dev  # start editor dev server
```

Or use it directly online: [editor.astraljs.com](https://editor.astraljs.com/)

### License Note

Apache-2.0 with supplementary terms: commercial use requires authorization from 杭州星孪数字科技 (Hangzhou Xingluan Digital Technology). Verify before embedding in a commercial product.

### Why This Matters

**Coverage** is Astral3D's core differentiator. Most open-source 3D web projects either cover general 3D (without BIM/CAD special formats) or focus on BIM display (without a full editor UX). Astral3D combines both in one editor, and stacks particle effects, weather, animation, and plugin extensibility on top — that combination is rare on the web.

WebGPU support is incoming. When WebGPU matures, the performance ceiling for rendering large BIM models in the browser rises sharply, and infrastructure like Astral3D becomes significantly more valuable.

2.4K stars, 485 forks, actively maintained (last update 2026-08-04).

Repository: [github.com/mlt131220/Astral3D](https://github.com/mlt131220/Astral3D) · Live demo: [editor.astraljs.com](https://editor.astraljs.com/) · Docs: [editor-doc.astraljs.com](http://editor-doc.astraljs.com/)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
