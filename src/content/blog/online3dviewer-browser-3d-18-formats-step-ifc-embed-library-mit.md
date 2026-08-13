---
title: "浏览器里的全格式 3D 查看器：kovacsv/Online3DViewer，18 种格式，文件从不离开你的设备"
titleEn: "online3dviewer-browser-3d-18-formats-step-ifc-embed-library-mit"
description: "kovacsv/Online3DViewer（3dviewer.net）是一个运行十年的开源浏览器 3D 查看器，MIT 许可，同时也是一个 npm 库（online-3d-viewer，月下载 6 万次）。支持 18 种格式导入（含 STEP/IGES/IFC/FreeCAD/Rhino）、7 种格式导出，工程 CAD 格式依靠 WASM 版 OpenCASCADE（occt-import-js）驱动。所有处理在浏览器内完成，文件永不上传。提供两种嵌入方式：一行 div 自动初始化，或通过 EmbeddedViewer API 完全编程控制。"
descriptionEn: "kovacsv/Online3DViewer (3dviewer.net) is a ten-year-old open-source browser 3D viewer, MIT-licensed, and also an npm library (online-3d-viewer, 60k monthly downloads). Supports 18 import formats including STEP/IGES/IFC/FreeCAD/Rhino via WASM OpenCASCADE (occt-import-js), and 7 export formats. All processing happens in the browser; files never leave the device. Two embedding modes: a one-line div for automatic init, or full programmatic control via the EmbeddedViewer API."
pubDate: "2026-08-13"
updatedDate: "2026-08-13"
category: "Tech-News"
tags: ["3D", "WebGL", "开源", "CAD", "Three.js", "浏览器", "嵌入式库", "工程工具"]
heroImage: "../../assets/images/online3dviewer-browser-3d-18-formats-step-ifc-embed-library-mit-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/kovacsv/Online3DViewer  
Live 站点：https://3dviewer.net  
npm：`online-3d-viewer`（月下载 ~61,000）  
许可证：MIT  
最新版：0.18.0（2025-12），仓库当前 v0.19.0  
Stars：3,644 / Forks：760

---

把一个 STEP 文件拖进浏览器，它直接打开——不需要注册，不需要安装，文件也从未离开你的机器。

这是 `kovacsv/Online3DViewer` 做的事。这个项目从 2014 年起持续维护，十年后仍在活跃迭代，同时是一个线上工具（3dviewer.net）和一个可以嵌进任何网页的 npm 库。

---

## 两层，一套代码

项目由两部分组成，共享同一个代码仓库：

**Engine（引擎层）** — 一个独立的 JavaScript 库，负责格式解析、三维模型抽象、Three.js 渲染和导出。打包成两个产物发布到 npm：
- `o3dv.min.js`：全局变量版，直接用 `<script>` 引入
- `o3dv.module.js`：ES Module 版，附带 TypeScript 类型声明

**Website（网站层）** — 使用引擎的完整前端应用，就是 3dviewer.net。它同时提供工具栏、设置面板、分享链接生成、嵌入代码生成……但这些全部是在引擎之上搭的 UI，不是引擎本身。

这个分层的意义在于：你可以不用 3dviewer.net 的界面，只把渲染能力嵌入自己的产品。

---

## 格式矩阵

### 18 种导入

| 类别 | 格式 | 来源 |
|------|------|------|
| 工程 CAD | STEP, IGES, BREP, FCStd（FreeCAD） | occt-import-js（WASM OpenCASCADE） |
| 建筑 BIM | IFC | web-ifc（WASM） |
| 设计 / 游戏 | glTF / glb, FBX, DAE（Collada）, 3MF, AMF, WRL | Three.js |
| Rhino | 3DM | rhino3dm（WASM） |
| 通用网格 | STL, OBJ, PLY, OFF | Native |
| 3D Studio | 3DS | Native |
| Dotbim | BIM | Native |

工程 CAD 格式（STEP、IGES、BREP、FreeCAD 的 .fcstd）历来是浏览器 3D 查看器的死角——这些格式依赖 OpenCASCADE Technology（OCCT）这个 C++ 内核来解析，在 Web 上实现它的正是 `occt-import-js`，作者和 Online3DViewer 是同一个人（kovacsv）。IFC 是建筑信息模型（BIM）的行业格式，同样靠 WASM（web-ifc）解析。

### 7 种导出

3DM, BIM, glTF / glb, OBJ, OFF, STL, PLY。

导出时若结果包含多个文件，自动打包成 zip 下载。

---

## 文件从不离开浏览器

这不是噱头，是架构决策。模型解析、格式转换、Three.js 渲染——所有工作都在浏览器的 JavaScript 环境内完成，没有网络请求把模型内容发到外部服务器。

从本地拖进来的文件直接通过 `File` API 读取，放在内存里处理。从 URL 加载的文件会被浏览器直接 fetch，3dviewer.net 的服务器只提供静态资源，模型内容不经过它。

这一点对工程和 BIM 行业有现实意义——设计图档和施工数据通常有严格的信息安全要求，能在浏览器内完成预览，比传文件到第三方 SaaS 要干净。

---

## 两种嵌入方式

### 方式一：自动初始化（最简单）

只需在页面里放一个带特定 class 的 div，然后调用一次 `OV.Init3DViewerElements()`：

```html
<div class="online_3d_viewer"
     style="width: 800px; height: 600px;"
     model="model.obj, model.mtl"
     backgroundcolor="255, 255, 255, 255"
     defaultcolor="200, 200, 200">
</div>

<script src="o3dv.min.js"></script>
<script>
  window.addEventListener('load', () => {
    OV.Init3DViewerElements();
  });
</script>
```

div 属性支持：model（文件路径列表）、camera（9 个数值：eye/center/up）、defaultcolor、backgroundcolor、edgesettings、environmentmap。

### 方式二：EmbeddedViewer API（完全控制）

通过 `EmbeddedViewer` 类编程控制，可以精细配置相机、材质默认值、边缘显示、环境贴图，并注册加载回调：

```js
import * as OV from 'online-3d-viewer';

const viewer = new OV.EmbeddedViewer(document.getElementById('viewer'), {
    camera: new OV.Camera(
        new OV.Coord3D(-1.5, 2.0, 3.0),   // eye
        new OV.Coord3D(0.0, 0.0, 0.0),    // center
        new OV.Coord3D(0.0, 1.0, 0.0),    // up
        45.0                               // fov
    ),
    backgroundColor: new OV.RGBAColor(255, 255, 255, 255),
    defaultColor: new OV.RGBColor(200, 200, 200),
    edgeSettings: new OV.EdgeSettings(false, new OV.RGBColor(0, 0, 0), 1),
    environmentSettings: new OV.EnvironmentSettings([
        'envmaps/px.jpg', 'envmaps/nx.jpg',
        'envmaps/py.jpg', 'envmaps/ny.jpg',
        'envmaps/pz.jpg', 'envmaps/nz.jpg'
    ], false),
    onModelLoaded: () => console.log('loaded'),
    onModelLoadFailed: () => console.error('failed'),
});

// 从 URL 加载（OBJ + MTL）
viewer.LoadModelFromUrlList(['model.obj', 'model.mtl']);

// 或者从 File 对象加载（文件选择器/拖放）
viewer.LoadModelFromFileList(fileList);
```

`projectionMode` 可选透视或正交，在版本 0.17.0 里对 EmbeddedViewer 有专项改进。

---

## 安装

```bash
npm install online-3d-viewer
```

或直接用 CDN（unpkg / jsDelivr）：

```html
<script src="https://unpkg.com/online-3d-viewer/build/engine/o3dv.min.js"></script>
```

环境贴图资源（`website/assets/envmaps/`）包含在 npm 包里，用于正确渲染 PBR 材质。

---

## 3dviewer.net 的典型用法

**分享模型**：把模型文件托管在任何支持 CORS 的服务器（GitHub Raw、Dropbox、自己的 CDN），打开 3dviewer.net，粘贴 URL，工具栏里点「Share」按钮，生成一个包含模型 URL 的永久链接。

**从 GitHub 加载**：直接在 GitHub 上找到模型文件，复制地址栏链接，粘进 3dviewer.net 的 URL 对话框。

**多文件模型**：OBJ + MTL + 贴图，或 glTF + 外部纹理——把所有关联文件一起拖入，或在 URL 对话框里每行填一个文件链接。也可以把整个文件夹打包成 zip 拖进去。

**导出转格式**：加载一个 FBX，导出成 glTF——纯浏览器内完成，不用装任何本地软件。

---

## 引擎的内部分层

Engine 的 source 目录分 9 个模块：

```
source/engine/
  core/       核心工具（IsDefined, 本地化 Loc()）
  export/     导出器（每种格式独立文件）
  geometry/   三维几何：Coord3D, Direction, BoundingBox
  import/     16 个独立导入器（importer3dm/3ds/bim/gltf/ifc/obj/stl/ply…）
  io/         文件 I/O，URL 处理，zip
  model/      模型抽象（Model, Mesh, Material, Texture）
  parameters/ 参数列表，序列化/反序列化
  threejs/    Three.js 适配层（ThreeModelLoader, three 渲染器集成）
  viewer/     Viewer, EmbeddedViewer, Camera, Navigation, ShadingModel
```

每种格式的导入器（`importerstl.js`, `importerifc.js` 等）都是独立单元，不互相依赖。WASM 重型格式（STEP/IGES/IFC/Rhino）在各自的导入器里懒加载对应的 WASM 模块，不会影响其他格式的初始化速度。

---

## 为什么十年后还值得关注

**格式广度**。18 种格式覆盖了消费级（STL、OBJ、glTF）、影视游戏（FBX、DAE）、工程 CAD（STEP、IGES、BREP）和建筑 BIM（IFC）。很少有单一工具做到这个宽度而不失去深度——它靠专用的 WASM 库处理每个重型格式，而不是自己重写 OCCT。

**嵌入即产品**。`EmbeddedViewer` API 足够简洁，能在任何已有产品里加入 3D 预览，一个 div 搞定或几十行代码完全控制——两条路都通。月 6 万的 npm 下载量说明它已经在被实际项目使用。

**纯浏览器、无服务端**。没有 WebSocket，没有 lambda 函数，没有模型上传流量——前端静态托管就够了。用来做离线工具、内部工具或对数据敏感的 BIM 查看器都是合适的选择。

**十年持续维护**。2014 年建仓，2026 年仍在迭代，CHANGELOG 里每个版本都有实质更新。760 个 fork 表明有相当数量的人在自己的项目里集成或改造它。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## All-Format 3D in the Browser: kovacsv/Online3DViewer — 18 Formats, Files Never Leave Your Device

*by Mycelium Protocol*

---

GitHub: https://github.com/kovacsv/Online3DViewer  
Live site: https://3dviewer.net  
npm: `online-3d-viewer` (~61,000 monthly downloads)  
License: MIT  
Latest: 0.18.0 (Dec 2025), repo at v0.19.0  
Stars: 3,644 / Forks: 760

---

Drop a STEP file into a browser tab. It opens — no signup, no install, the file never leaves your machine.

That's what `kovacsv/Online3DViewer` does. The project has been actively maintained since 2014, still iterating a decade later, and serves two functions at once: a public tool at 3dviewer.net and an npm library you can embed in any webpage.

---

### Two Layers, One Repository

The project has two distinct parts sharing a single codebase:

**Engine** — a standalone JavaScript library handling format parsing, 3D model abstraction, Three.js rendering, and export. Published to npm as two artifacts:
- `o3dv.min.js` — global-variable build, `<script>`-tag ready
- `o3dv.module.js` — ES Module build with TypeScript declarations

**Website** — the full frontend application that powers 3dviewer.net, using the engine plus a toolbar, settings panel, share-link generator, and embed-code generator. The UI is layered on top of the engine, not baked into it.

The split matters: you can take just the rendering capability and embed it in your own product without any of the 3dviewer.net UI.

---

### Format Matrix

**18 imports:**

| Category | Formats | Powered by |
|----------|---------|------------|
| Engineering CAD | STEP, IGES, BREP, FCStd (FreeCAD) | occt-import-js (WASM OpenCASCADE) |
| Architecture BIM | IFC | web-ifc (WASM) |
| Design / Game | glTF/glb, FBX, DAE (Collada), 3MF, AMF, WRL | Three.js |
| Rhino | 3DM | rhino3dm (WASM) |
| General Mesh | STL, OBJ, PLY, OFF | Native |
| 3D Studio | 3DS | Native |
| Dotbim | BIM | Native |

Engineering CAD formats (STEP, IGES, BREP, FreeCAD's .fcstd) have historically been the blind spot of browser 3D viewers — they require OpenCASCADE Technology (OCCT), a C++ kernel, to parse. The `occt-import-js` WASM library brings OCCT to JavaScript; notably, it's by the same author (kovacsv). IFC, the building information modeling industry format, is similarly handled via WASM (web-ifc).

**7 exports:** 3DM, BIM, glTF/glb, OBJ, OFF, STL, PLY. Multi-file exports are automatically zipped.

---

### Files Never Leave the Browser

This isn't marketing language — it's an architectural decision. Model parsing, format conversion, and Three.js rendering all happen inside the browser's JavaScript environment. No network request sends model content to an external server.

Local files are read via the `File` API and held in memory. URL-loaded files are fetched directly by the browser; the 3dviewer.net server only serves static assets. Model content never passes through it.

For engineering and BIM work this has practical importance — design drawings and construction data often carry strict information security requirements. In-browser preview keeps data cleaner than pushing files to a third-party SaaS.

---

### Two Embedding Modes

**Automatic initialization (simplest):**

```html
<div class="online_3d_viewer"
     style="width: 800px; height: 600px;"
     model="model.obj, model.mtl"
     backgroundcolor="255, 255, 255, 255"
     defaultcolor="200, 200, 200">
</div>

<script src="o3dv.min.js"></script>
<script>
  window.addEventListener('load', () => {
    OV.Init3DViewerElements();
  });
</script>
```

div attributes: `model` (comma-separated file paths), `camera` (9 values: eye/center/up), `defaultcolor`, `backgroundcolor`, `edgesettings`, `environmentmap`.

**EmbeddedViewer API (full control):**

```js
import * as OV from 'online-3d-viewer';

const viewer = new OV.EmbeddedViewer(document.getElementById('viewer'), {
    camera: new OV.Camera(
        new OV.Coord3D(-1.5, 2.0, 3.0),
        new OV.Coord3D(0.0, 0.0, 0.0),
        new OV.Coord3D(0.0, 1.0, 0.0),
        45.0
    ),
    backgroundColor: new OV.RGBAColor(255, 255, 255, 255),
    defaultColor: new OV.RGBColor(200, 200, 200),
    edgeSettings: new OV.EdgeSettings(false, new OV.RGBColor(0, 0, 0), 1),
    onModelLoaded: () => console.log('loaded'),
    onModelLoadFailed: () => console.error('failed'),
});

viewer.LoadModelFromUrlList(['model.obj', 'model.mtl']);
// or from file picker / drag-and-drop:
viewer.LoadModelFromFileList(fileList);
```

---

### Engine Module Structure

Nine modules under `source/engine/`:

```
core/       Utilities, localization
export/     Per-format exporters
geometry/   Coord3D, Direction, BoundingBox
import/     16 independent importers (STL, OBJ, glTF, IFC, STEP…)
io/         File I/O, URL handling, zip
model/      Model, Mesh, Material, Texture abstractions
parameters/ Parameter lists, serialization
threejs/    Three.js adapter layer
viewer/     Viewer, EmbeddedViewer, Camera, Navigation, ShadingModel
```

Each format importer is an independent unit. WASM-heavy formats (STEP/IGES/IFC/Rhino) lazy-load their WASM module inside their respective importer — they don't delay initialization of lighter formats.

---

### Why It Still Matters After Ten Years

**Format breadth.** 18 formats spanning consumer (STL, OBJ, glTF), media/game (FBX, DAE), engineering CAD (STEP, IGES, BREP), and architecture BIM (IFC). Few single tools cover this range without losing depth — this one delegates the heavy lifting to specialized WASM libraries rather than reimplementing OCCT itself.

**Embed-ready.** The `EmbeddedViewer` API is lean enough to drop into any existing product — one div for the simple case, a few dozen lines for full control. 60k npm monthly downloads suggests it's in active production use.

**Zero server-side.** No WebSocket, no lambda, no model-upload traffic. A static frontend host is enough. Suitable for offline tools, internal tooling, or privacy-sensitive BIM viewers.

**Ten years of maintenance.** Created 2014, still iterating in 2026. Every release in the changelog has substantive changes. 760 forks indicate a meaningful population of people integrating or adapting it.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
