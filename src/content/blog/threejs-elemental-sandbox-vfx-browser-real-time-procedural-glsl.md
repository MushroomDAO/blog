---
title: "浏览器里的 3A 特效工厂：纯 Three.js 打造 10 种游戏技能，938 个参数全部可实时调节"
titleEn: "threejs-elemental-sandbox-vfx-browser-real-time-procedural-glsl"
description: "achrefelouafi 开源的 Elemental Sandbox 用 Three.js + Vite + 手写 GLSL，在浏览器里程序化生成 10 种 3A 游戏级技能特效——冰霜迸裂、枝状闪电、陨石撞击、能量光束、虚空刀刃、凤凰……全部无贴图、无精灵表、无预烘焙网格。938 个参数配有实时滑块，按 P 暂停后仍可继续调整，成为研究游戏 VFX 系统的最佳交互式沙盒。MIT 许可，npm run dev 即跑。"
descriptionEn: "achrefelouafi's Elemental Sandbox uses Three.js + Vite + hand-written GLSL to procedurally generate 10 game-quality skill VFX in the browser — frost, lightning, meteors, energy beams, void blades, phoenixes — all without textures, sprite sheets, or pre-baked meshes. 938 parameters have live sliders. Press P to pause mid-eruption and keep tweaking. MIT license, runs with npm run dev."
pubDate: "2026-08-12"
updatedDate: "2026-08-12"
category: "Tech-News"
tags: ["Three.js", "WebGL", "GLSL", "VFX", "游戏开发", "开源", "前端", "程序化生成"]
heroImage: "../../assets/images/threejs-elemental-sandbox-vfx-browser-real-time-procedural-glsl-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

这不是一个演示 Demo，是一座 VFX 实验室。

**Elemental Sandbox**（`achrefelouafi/LinearAbiltyCastingThreeJS`）用 Three.js + Vite + 手写 GLSL，在浏览器里程序化构建 10 种媲美 Unity / 虚幻引擎的游戏技能特效。效果全部实时生成：没有一张贴图，没有一张精灵表，没有从磁盘加载的烘焙网格——所有形状由 CPU / GPU 当场计算。

GitHub：https://github.com/achrefelouafi/LinearAbiltyCastingThreeJS  
技术栈：Three.js · Vite · 纯 GLSL  
许可证：MIT  
上线时间：2026-08-06，一周内已获 **376 stars / 71 forks**

---

## 10 种技能，两种瞄准方式

按下技能键，地面出现英雄联盟风格的方向箭头，随鼠标旋转，点击释放。4 种远程技能改为圆形范围指示器。10 个技能键绑定如下：

| 键位 | 技能 | 核心效果 |
|------|------|----------|
| **1** | Rift Sever | 虚空刀刃在空中撕开一道高耸裂缝：黑色核心、青紫色边缘、内吸碎片、地面裂痕、折射层，然后合拢 |
| **2** | Solar Phoenix | 火焰羽毛拼合成低飞的完整凤凰，有跳动轮廓和尾焰，俯冲落地变为太阳轮、压力环、灼烧印记 |
| **3** | Gravity Singularity | 压缩弹丸变成真实的暗色视界：两个交叉吸积盘、轨道碎片、引力透镜扭曲，然后逆超新星内爆 |
| **4** | Worldroot Bloom | 分形根系从地面蔓延，然后实例化的树干、枝桠、叶冠向上生长，脉动翡翠金汁，落种，从冠到根溶解 |
| **Q** | Frost Lance | 冰裂前沿沿直线疾驰，身后的冰晶场从地面撕裂而出——脚下细密，终点一堵冰刃墙，撞击点又掀起一簇 |
| **E** | Storm Lance | 闪电从施法者手中跃出，身后拖出一束雷弧丝，颤动、再击，然后炸散。全程飞溅电花，地面留下树状电灼痕 |
| **R** | Cinder Fall | 燃烧的陨石沿抛物线飞行，尾迹是体积渲染的灼热气流，岩浆缝隙落地前越张越亮。落地爆炸，碎块四散，地面开裂成熔岩网格 |
| **F** | Nova Beam | 施法者双手聚光，然后放出一柱能量：白热核心、青色护鞘、螺旋金丝带、沿柱狂奔的冲击盘。它会**持续**燃烧地面、向上反溅，然后收细成一根光线，熄灭 |
| **V** | Voltaic Snare | 一圈紫色电流在落点处弹开超过自身半径再收回，中心紫色光柱拔地而起，电弧沿环边转动，整个电场盘持续放电 |
| **X** | Glacial Crown | 圆形范围冰霜区域技能（与 Frost Lance 共用 cast3 动画） |

---

## 没有一张贴图

> *"Everything you can see is generated. There are no textures, no sprite sheets and no meshes on disk except the character."*

每种效果的实现手段各不相同：

- **冰晶**：程序化几何体，形状由 CPU 计算
- **闪电弧**：顶点着色器里用参数化路径排列的 Ribbon Strip
- **陨石**：CPU 对 icosphere 做裂面切割，模拟陨坑
- **能量光束**：同一参数化圆管以三个半径各绘制一次
- **Voltaic Snare 的笼**：相同 Ribbon Strip 沿四条不同参数化路径穿插
- **瞄准箭头、冰痕、灼痕、熔岩缝**：SDF 和噪声着色器
- **雾气、电花、碎片、闪光**：GPU 粒子

---

## 938 个参数，实时可调

`src/config/settings.js` 是整个项目唯一的配置真相。着色器、粒子系统、灯光、后处理管线**每帧直接读这个对象**——移动滑块立刻改变正在站立的冰场、下一次施法，以及环境光和后处理效果，无需重新构建。

**暂停编辑**是这套系统最实用的设计：按 **P** 冻结画面，滑块依然生效。可以在一次冰霜喷发的定格中调整晶体密度、颜色梯度、裂面扩散速度，然后按 P 恢复，确认调整有没有破坏时序感。

预设支持导出：文件里同时保存了当前质量配置和各个滑块的已写入值，换质量档不会覆盖精调结果。

---

## 技术架构速览

```
src/
  abilities/      技能基类 + 10 个程序化技能 + 对象池管理
  animation/      FBX 角色加载、AnimationMixer、每技能施法动画
  assets/         程序化晶体/陨石几何、Ribbon Strip、参数化光束管
  config/         settings.js — 所有参数的单一来源
  core/           App / Renderer / CameraRig / Time / Layers
  effects/        瞄准箭头、远程圆圈、地面贴花、裂缝、光源池、震屏
  materials/      IceMaterial / LightningMaterial / MeteorMaterial /
                  VolumetricFireMaterial / BeamMaterial / SnareMaterial
  particles/      GPU 粒子系统（引擎 + 速率发射器）
  postprocessing/ 渲染管线、色调分级着色器、扭曲着色器
  shaders/lib/    共享 GLSL：噪声库 + 通用 helpers
  ui/             HUD / lil-gui 编辑器 / 预设管理器
  world/          舞台灯光 / 地面 / 尘埃 / 接触阴影
  archive/        原版 4 元素沙盒（已归档，含独立 README）
```

GPU 粒子走实例化渲染，世界坐标在顶点着色器内解析，避免 CPU 回读。后处理管线两个 pass：色调分级（曝光 / 对比度 / 饱和度）和基于速度/透明度的扭曲层。

---

## 快速启动

```bash
git clone https://github.com/achrefelouafi/LinearAbiltyCastingThreeJS
cd LinearAbiltyCastingThreeJS
npm install
npm run dev
```

Vite 默认监听 `http://127.0.0.1:5173`。按 **G** 打开编辑器，**P** 暂停，**C** 清空所有效果，**H** 隐藏控制面板。

---

## 为什么值得关注

**技术价值**：这是一套完整的游戏 VFX 分层方法论的浏览器实现——程序几何 + 顶点着色器 + GPU 粒子 + 后处理——每一层都有实际代码对应，可拆可读可改。

**学习价值**：`settings.js` 驱动的架构使得修改任何参数不需要理解整条调用链，适合前端开发者从「改数字看效果」开始建立对 VFX 系统的直觉。

**工程参考**：暂停后编辑器保持生效、预设保留已调值、对象池管理——这三点直接可以搬到游戏或 WebXR 项目里。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## A 3A VFX Factory in the Browser: 10 Game Skills Built in Pure Three.js, 938 Parameters All Live-Editable

*by Mycelium Protocol*

---

This is not a demo. It's a VFX laboratory.

**Elemental Sandbox** (`achrefelouafi/LinearAbiltyCastingThreeJS`) uses Three.js + Vite + hand-written GLSL to procedurally generate 10 game-quality skill effects in the browser. Every effect is computed at runtime: no textures, no sprite sheets, no baked meshes loaded from disk — every shape is calculated live on CPU or GPU.

GitHub: https://github.com/achrefelouafi/LinearAbiltyCastingThreeJS  
Stack: Three.js · Vite · pure GLSL  
License: MIT  
Released: 2026-08-06 — **376 stars / 71 forks** in one week

---

### 10 Abilities, Two Targeting Modes

Press a skill key, and a League-of-Legends-style directional arrow appears on the ground, tracking the mouse. Click to fire. Four long-range skills use a circle instead. Ten keybinds:

| Key | Skill | Core Effect |
|-----|-------|-------------|
| **1** | Rift Sever | A void seam tears open with a black core, cyan-violet edges, inward-pulled debris, a ground fault, and a refraction layer — then zips shut |
| **2** | Solar Phoenix | Fire feathers assemble into a low-flying winged phoenix with a beating silhouette and layered tail, then dive into a sun wheel, pressure ring, and burn mark |
| **3** | Gravity Singularity | A compressed projectile becomes a dark event horizon: crossed accretion discs, orbiting debris, gravitational lensing — then collapses into a reverse supernova |
| **4** | Worldroot Bloom | Fractal roots race across the floor while an instanced trunk, branches, and leaf crown grow upward, pulsing with emerald-gold sap, shedding luminous seeds, then dissolving crown to root |
| **Q** | Frost Lance | A fracture front races out along a line; a field of ice crystals tears up from the floor behind it — dense near your feet, a wall of blades at the far end |
| **E** | Storm Lance | A bolt leaves the caster's hand and lightning filaments are drawn out behind the strike front, hold while guttering and re-striking, then blow out. Sparks off the whole way; floor takes a branching electric burn |
| **R** | Cinder Fall | A burning rock arcs downrange trailing raymarched burning gas, lava seams prising wider and brighter. Detonates on arrival, throws shattered chunks, tears the ground into a network of glowing molten cracks |
| **F** | Nova Beam | The caster winds a ball of light, then releases a column: white-hot core, cyan sheath, gold ribbons spiraling around it, shock discs racing down it. It **holds**, burning into the floor, before collapsing to a thread |
| **V** | Voltaic Snare | A leash of current snaps a ring open past its own radius and pulls back; a violet column tears up out of the middle, tendrils crawl to the boundary, arcs run around the rim |
| **X** | Glacial Crown | Area-cast ice effect (shares cast3 animation with Frost Lance) |

---

### Not a Single Texture

> *"Everything you can see is generated. There are no textures, no sprite sheets and no meshes on disk except the character."*

Each effect uses a different generation technique:

- **Ice crystals**: procedural geometry computed on CPU
- **Lightning bolt**: Ribbon Strip placed entirely by a vertex shader along a parametric path
- **Meteor**: an icosphere cratered and sliced by fracture planes on CPU
- **Energy beam**: the same parametric tube drawn three times at three radii
- **Voltaic Snare cage**: that same Ribbon Strip threaded along four different parametric paths
- **Aim arrow, frost rimes, burns, molten cracks**: signed-distance and noise shaders
- **Mist, sparks, chips, glitter**: GPU particles

---

### 938 Parameters, All Live

`src/config/settings.js` is the single source of truth for every tweakable value. Shaders, particle systems, lights, and post passes **read these objects every frame** — moving a slider immediately changes the ice field already standing, the next cast, the environment, and the post stack. No rebuild needed.

**The key design**: press **P** to pause the simulation. The editor stays fully active. You can freeze mid-frost-eruption, tweak crystal density, color gradients, and fracture velocity, then resume — confirming whether the timing still lands. Preset export preserves both the quality profile and the authored slider values.

---

### Architecture Snapshot

```
src/
  abilities/      Base class + 10 procedural skills + pooling manager
  config/         settings.js — single source for every parameter
  materials/      IceMaterial / LightningMaterial / MeteorMaterial /
                  VolumetricFireMaterial / BeamMaterial / SnareMaterial
  particles/      GPU particle system (engine + rate emitters)
  postprocessing/ Composer pipeline, grade shader, distortion shader
  shaders/lib/    Shared GLSL: noise library, common helpers
```

GPU particles use instanced rendering with world-position resolved in the vertex shader, avoiding CPU readback. The post pipeline runs two passes: tone grading (exposure / contrast / saturation) and a velocity/transparency-based distortion layer.

---

### Quick Start

```bash
git clone https://github.com/achrefelouafi/LinearAbiltyCastingThreeJS
cd LinearAbiltyCastingThreeJS
npm install
npm run dev
```

Vite defaults to `http://127.0.0.1:5173`. Press **G** to open the editor, **P** to pause, **C** to clear all active effects.

---

### Why It Matters

**Technical value**: a complete, layered game VFX methodology running in the browser — procedural geometry + vertex shaders + GPU particles + post-processing — every layer with real, readable, modifiable code.

**Learning value**: the `settings.js`-driven architecture means you can modify any parameter without understanding the full call chain. Ideal for frontend developers building intuition for VFX systems by starting from "change a number, watch the result."

**Engineering reference**: editor stays live during pause, presets preserve authored values, object pooling throughout — three patterns directly portable to game or WebXR projects.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
