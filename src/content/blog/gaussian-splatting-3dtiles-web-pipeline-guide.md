---
title: "高斯泼溅上 Web：3DGS → 3D Tiles 全开源工具链指南"
titleEn: "Gaussian Splatting to Web: Open-Source 3DGS → 3D Tiles Pipeline Guide"
description: "WilliamLiu-1997 整理的三件套开源工具链：把 3DGS PLY 转换为 3D Tiles、本地检查调整、接入 CesiumJS / Three.js，用 2GB 内存处理 20GB 级别扫描数据的完整解决方案。"
descriptionEn: "Three open-source tools by WilliamLiu-1997: convert 3DGS PLY to 3D Tiles, inspect and adjust locally, then load in CesiumJS or Three.js — handling 20GB scans with just 2GB RAM."
pubDate: "2026-07-08"
updatedDate: "2026-07-08"
category: "Tech-Experiment"
tags: ["高斯泼溅", "3DGS", "3D Tiles", "WebGIS", "CesiumJS", "Three.js", "数字孪生", "开源工具链"]
heroImage: "../../assets/images/gaussian-splatting-guide-banner.jpg"
---

高斯泼溅（3D Gaussian Splatting，3DGS）是目前最热门的三维重建技术之一——用数百万个椭球形高斯粒子代替传统网格，在实时渲染中做到了接近照片的视觉质量。但训练完拿到 PLY 文件后，怎么让它在浏览器里流畅地跑起来？这是很多做 WebGIS 和数字孪生的人都绕不开的工程难题。

GitHub 用户 **WilliamLiu-1997** 把自己在做高斯泼溅 WebGIS 项目时踩过的坑整理成了一套完整的开源工具链，三个仓库串起来就是一条从 PLY 到 Web 的完整 pipeline。

---

## 为什么 PLY 直接上 Web 会有问题？

原始 3DGS PLY 文件在本地用 SuperSplat 或 3D Gaussian Splatting 查看器看没问题，但直接进入 WebGIS / 数字孪生项目会遇到四类工程难题：

**01 文件体量和加载方式**：PLY 往往比较大，浏览器一次性加载完整数据会卡死，也不方便根据视角按需释放内容。

**02 缺少 tile 层级**：大场景浏览需要 LOD（多细节层次）、空间划分和按需加载。远处先看低细节，靠近再加载高细节——原始 PLY 没有这套结构。

**03 GIS 放置和坐标**：要把扫描结果放进地理场景，需要处理 WGS84 坐标、root transform、位置朝向和高度等问题，PLY 文件本身并不携带这些信息。

**04 扫描数据清理**：实际扫描数据里经常有漂浮 splats、噪声点、多余背景区域，需要裁剪。

这套工具链的设计目标就是把上述四个问题一次解决。

---

## 完整 Pipeline 一览

```
PLY (input) → 3D Tiles (tileset) → Inspector (debug) → Runtime (run)

convert(scene.ply) -> inspect(tileset.json) -> run(webgis)
```

三个环节对应三个开源仓库，都已发布到 npm，不需要手动编译：

| 项目 | GitHub | Stars | 职责 |
|------|--------|-------|------|
| 3DGS-PLY-3DTiles-Converter | WilliamLiu-1997/3DGS-PLY-3DTiles-Converter | 154⭐ | PLY → 3D Tiles |
| 3DTiles-Inspector | WilliamLiu-1997/3DTiles-Inspector | 16⭐ | 本地检查 & 调整 |
| 3D-Tiles-RendererJS-3DGS-Plugin | WilliamLiu-1997/3D-Tiles-RendererJS-3DGS-Plugin | 107⭐ | Three.js 运行时 |

---

## 工具一：3DGS-PLY-3DTiles-Converter

**把大 PLY 切成可按需加载的 3D Tiles 分层结构。**

GitHub: [WilliamLiu-1997/3DGS-PLY-3DTiles-Converter](https://github.com/WilliamLiu-1997/3DGS-PLY-3DTiles-Converter) | Apache-2.0 | Node.js 18+

### 安装和基本用法

```bash
npm install 3dgs-ply-3dtiles-converter
```

最简单的一行命令：

```bash
npx 3dgs-ply-3dtiles-converter scene.ply out_tiles
```

输出目录结构：

```
out_tiles/
  tileset.json        # 3D Tiles 描述文件，直接给 CesiumJS 加载
  build_summary.json  # 转换参数、坐标、调试信息
  tiles/.../*.glb     # SPZ 压缩的 GLB 瓦片内容
```

### 核心能力

**大文件支持**：使用临时文件管线，2GB 内存可以处理 20GB 级别的 3DGS 数据。大 PLY 转换时自动分批写入 `output_dir/.tmp-ply-partitions`，失败后用 `--continue` 接续。

**LOD 层级树**：把单个大 PLY 拆成多级可按需加载的 tile，生成父级和子级 LOD——远距离先看低细节，靠近再加载更多内容。

**SPZ 压缩**：输出 SPZ-compressed GLB 内容（`KHR_gaussian_splatting` + `KHR_gaussian_splatting_compression_spz_2`），后续可以给 CesiumJS 或 Three.js 使用。

**WGS84 地理放置**：支持 root transform 或 WGS84 坐标，方便接入地理场景。例如把扫描结果放到上海某个坐标：

```bash
npx 3dgs-ply-3dtiles-converter scene.ply out_tiles --coordinate "[31.2304,121.4737,30]"
```

**转换完成后默认自动打开 3DTiles-Inspector** 检查结果，批处理时用 `--no-open-inspector` 关掉。

### 常用参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--memory-budget <gb>` | 内存预算 | 3 GB |
| `--max-depth <int>` | LOD 最大深度 | 自动 |
| `--coordinate "[lat,lng,h]"` | WGS84 地理放置 | 无 |
| `--opacity-filter <0-1>` | 过滤透明 splats | 0.05 |
| `--no-open-inspector` | 不自动打开检查器 | - |
| `--continue` | 断点续传 | - |

---

## 工具二：3DTiles-Inspector

**转换后在浏览器里调整和保存。**

GitHub: [WilliamLiu-1997/3DTiles-Inspector](https://github.com/WilliamLiu-1997/3DTiles-Inspector) | Apache-2.0 | Node.js 18+

```bash
npm install 3dtiles-inspector
npx 3dtiles-inspector out_tiles/tileset.json
```

命令自动启动本地 HTTP 服务器并打开浏览器。`<tileset_json>` 可以是文件路径，也可以是包含 `tileset.json` 的目录。

### 检查和调整功能

- **位置和朝向**：Translate / Rotate / Scale，以及 `Move Tiles`（输入 WGS84 坐标）和 `Set Position`（直接点击地球放置）
- **LOD 调整**：`Geometric Error` 缩放（1/16x 到 16x），调整远近切换门槛
- **地形参考**：输入 Cesium ion Token 后可叠加真实地形和卫星底图，检查 GIS 场景里的对齐情况
- **保存**：把调整后的 root transform、geometric error scale 写回磁盘，更新 `build_summary.json`

### 3DGS 区域裁剪（Crop Regions）

这是处理扫描噪声的核心功能——加载的 tileset 包含 Gaussian Splat 内容时自动出现：

**屏幕区域裁剪**（去掉背景或漂浮噪声）：
1. 点击 `Draw Region`，拖拽框选需要删除的 splats 区域
2. 调整边角控制点，旋转视角固定深度
3. 点击 `Confirm` 确认，再点击 `Save` 写回文件

**球形裁剪**（保留感兴趣区域）：
1. 点击 `Create Sphere`，在 tileset 中心放置球体
2. 调整半径，用 `Confirm` 预览效果
3. `Save` 删除球外的 splats

裁剪保存会直接重写本地 `.glb` 文件（`KHR_gaussian_splatting_compression_spz_2` 编码），完全被裁空的 tile 会从 tileset 中删除。

---

## 工具三：3D-Tiles-RendererJS-3DGS-Plugin

**在 Three.js 里流式加载和渲染 3DGS 内容。**

GitHub: [WilliamLiu-1997/3D-Tiles-RendererJS-3DGS-Plugin](https://github.com/WilliamLiu-1997/3D-Tiles-RendererJS-3DGS-Plugin) | Apache-2.0

```bash
npm install 3d-tiles-rendererjs-3dgs-plugin three 3d-tiles-renderer @sparkjsdev/spark
```

依赖：`three@^0.180.0` + `3d-tiles-renderer@^0.4.25` + `@sparkjsdev/spark@^2.1.0`

### 基本接入

```ts
import { TilesRenderer } from '3d-tiles-renderer';
import { TilesFadePlugin } from '3d-tiles-renderer/plugins';
import { GaussianSplatPlugin } from '3d-tiles-rendererjs-3dgs-plugin';

const tiles = new TilesRenderer('https://example.com/tileset.json');
tiles.setCamera(camera);
tiles.setResolutionFromRenderer(camera, renderer);
tiles.registerPlugin(new TilesFadePlugin());
tiles.registerPlugin(
  new GaussianSplatPlugin({
    renderer,
    scene,
    minRaycastOpacity: 0.1,
  })
);

scene.add(tiles.group);

function frame() {
  tiles.update();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
frame();
```

### 渲染特性

- 支持显式和隐式 3D Tiles 分层方案
- 解析含 `KHR_gaussian_splatting_compression_spz_2` 的 GLB tile 内容
- 通过 **Spark Renderer** 渲染高斯 splats（同一 scene/renderer 对共享一个 Spark 实例）
- 支持 tile fade 动画（与 `TilesFadePlugin` 配合）
- 支持 WebXR / VR 场景

### 与地球底图叠加的注意事项

Spark splats 以透明几何体渲染。如果地球底图（如 CesiumJS 的卫星图）也以透明 Three.js 材质渲染，两者都会进入 Three.js 的透明排序队列，可能在地平线视角出现地球遮挡整片 splat 的问题。

解决方式：
- 地球材质设 `transparent = false`，或
- splats 和地球使用独立 scene，分开 render pass（共享 depth buffer）

---

## 运行时选择：CesiumJS vs Three.js

| | CesiumJS | Three.js |
|---|---|---|
| 加载方式 | 原生 3D Tiles 加载（无需额外插件） | 需要 3D-Tiles-RendererJS-3DGS-Plugin |
| 适合场景 | WebGIS、城市级场景、数字孪生 | 自定义三维应用、WebXR |
| 坐标系 | 自带 WGS84 + 地形 | 手动配置 ECEF 对齐 |
| 地球底图 | 内置 Bing/OSM/Cesium ion 影像 | 需要 GeneratedSurfacePlugin + XYZTilesOverlay |

**CesiumJS 用法最简单**：转换和 Inspector 调好之后，把 `tileset.json` 路径丢进去直接加载。

**Three.js 更灵活**：适合已有 Three.js 渲染管线、需要和其他 3D 对象深度集成的项目。

---

## 完整工作流总结

```bash
# 第一步：转换 PLY → 3D Tiles
npx 3dgs-ply-3dtiles-converter scene.ply out_tiles \
  --coordinate "[纬度,经度,高度]" \
  --memory-budget 4

# 第二步：浏览器里检查和调整（自动打开）
npx 3dtiles-inspector out_tiles/tileset.json

# （可选）在 Inspector 里：
# - 调整 Translate / Rotate 对齐地面
# - 设置 Geometric Error 优化远近切换
# - Draw Region → Confirm → Save 裁掉噪声

# 第三步（CesiumJS）：
# viewer.scene.primitives.add(new Cesium.Cesium3DTileset({ url: 'out_tiles/tileset.json' }))

# 第三步（Three.js）：
npm install 3d-tiles-rendererjs-3dgs-plugin three 3d-tiles-renderer @sparkjsdev/spark
# 参考上文代码接入 GaussianSplatPlugin
```

---

## 资源链接

- [3DGS-PLY-3DTiles-Converter](https://github.com/WilliamLiu-1997/3DGS-PLY-3DTiles-Converter) — npm: `3dgs-ply-3dtiles-converter`
- [3DTiles-Inspector](https://github.com/WilliamLiu-1997/3DTiles-Inspector) — npm: `3dtiles-inspector`
- [3D-Tiles-RendererJS-3DGS-Plugin](https://github.com/WilliamLiu-1997/3D-Tiles-RendererJS-3DGS-Plugin) — npm: `3d-tiles-rendererjs-3dgs-plugin`
- [NASA-AMMOS/3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS) — 底层 3D Tiles 加载库

© 2026 Author: Mycelium Protocol

<!--EN-->

## Gaussian Splatting to Web: Open-Source 3DGS → 3D Tiles Pipeline Guide

3D Gaussian Splatting (3DGS) has become one of the most exciting 3D reconstruction techniques — millions of ellipsoidal Gaussian primitives replace traditional meshes to achieve near-photorealistic quality in real-time rendering. But once you have a trained PLY file, how do you make it run smoothly in a browser? This is an engineering challenge that everyone building WebGIS or digital twin applications eventually faces.

GitHub user **WilliamLiu-1997** distilled his own hard-won experience building 3DGS WebGIS projects into a complete open-source toolchain — three repositories that chain together into a full pipeline from PLY to the web.

---

### Why You Can't Just Put a PLY File on the Web

Raw 3DGS PLY files work fine locally in viewers like SuperSplat, but drop them into a WebGIS or digital twin project and you'll hit four engineering problems:

1. **File size and loading**: PLY files are often large. Loading the entire dataset in the browser at once is impractical, and there's no way to stream content by viewport.

2. **No tile hierarchy**: Large-scene browsing requires LOD (Level of Detail), spatial partitioning, and on-demand loading. Raw PLY has none of this.

3. **GIS placement and coordinates**: Putting scan data into a geographic scene requires handling WGS84 coordinates, root transforms, position, orientation, and elevation — information PLY files don't carry.

4. **Scan data cleanup**: Real-world scans often contain floating splats, noise points, and unwanted background regions that need cropping.

---

### The Complete Pipeline

```
PLY (input) → 3D Tiles (tileset) → Inspector (debug) → Runtime (run)
```

Three stages, three npm packages — no manual compilation needed:

| Project | Stars | Role |
|---------|-------|------|
| 3DGS-PLY-3DTiles-Converter | 154⭐ | PLY → 3D Tiles |
| 3DTiles-Inspector | 16⭐ | Local inspect & adjust |
| 3D-Tiles-RendererJS-3DGS-Plugin | 107⭐ | Three.js runtime |

---

### Tool 1: 3DGS-PLY-3DTiles-Converter

Converts large PLY files into a hierarchical 3D Tiles structure for on-demand streaming.

```bash
npx 3dgs-ply-3dtiles-converter scene.ply out_tiles
```

Key capabilities:
- **Large file support**: 2 GB RAM can process 20 GB–scale 3DGS data via a temporary file pipeline
- **LOD tree**: Splits the PLY into multi-level tiles; parent LODs show simplified content at distance, children load full detail up close
- **SPZ compression**: Outputs SPZ-compressed GLB content (`KHR_gaussian_splatting` + `KHR_gaussian_splatting_compression_spz_2`)
- **WGS84 placement**: Anchor the tileset at a geographic coordinate with one flag:
  ```bash
  --coordinate "[31.2304,121.4737,30]"
  ```

### Tool 2: 3DTiles-Inspector

A browser-based inspector to check, adjust, and save your converted tileset before deploying it.

```bash
npx 3dtiles-inspector out_tiles/tileset.json
```

Key features:
- Translate, Rotate, Scale root transform; place by WGS84 coordinate or by clicking the globe
- Geometric Error scaling (1/16× to 16×) to tune LOD transitions
- Optional Cesium World Terrain + satellite imagery overlay for GIS alignment checks
- **Crop Regions**: Draw screen-space rectangles or a sphere to remove floating splats and background noise, then save the changes back to the `.glb` files

### Tool 3: 3D-Tiles-RendererJS-3DGS-Plugin

Adds Gaussian splat tile support to Three.js via `3d-tiles-renderer`.

```bash
npm install 3d-tiles-rendererjs-3dgs-plugin three 3d-tiles-renderer @sparkjsdev/spark
```

```ts
import { GaussianSplatPlugin } from '3d-tiles-rendererjs-3dgs-plugin';

tiles.registerPlugin(new GaussianSplatPlugin({ renderer, scene }));
```

Renders through Spark Renderer with tile streaming, disposal, byte accounting, and fade transitions fully integrated into the 3d-tiles-renderer lifecycle.

---

### CesiumJS vs Three.js

- **CesiumJS**: Load the `tileset.json` directly as a `Cesium3DTileset` — no plugin needed. Best for WebGIS, city-scale scenes, and digital twin workflows.
- **Three.js**: Use `GaussianSplatPlugin` for full control over the rendering pipeline. Best for custom 3D apps and WebXR.

---

### Resources

- [3DGS-PLY-3DTiles-Converter](https://github.com/WilliamLiu-1997/3DGS-PLY-3DTiles-Converter)
- [3DTiles-Inspector](https://github.com/WilliamLiu-1997/3DTiles-Inspector)
- [3D-Tiles-RendererJS-3DGS-Plugin](https://github.com/WilliamLiu-1997/3D-Tiles-RendererJS-3DGS-Plugin)

© 2026 Author: Mycelium Protocol
