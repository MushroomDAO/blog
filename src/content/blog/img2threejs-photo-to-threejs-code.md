---
title: "img2threejs：给AI一张图，拿回一个可动的Three.js 3D代码"
titleEn: "img2threejs-photo-to-threejs-code"
description: "16天 8591 星。img2threejs 给 Claude Code 加了一个 /img2threejs 技能：输入一张参考图，输出的不是 mesh 文件，而是纯 TypeScript 代码，从几何基元和程序化着色器重新建造这个物体，带运行时层级、可以直接动画。"
descriptionEn: "8591 stars in 16 days. img2threejs adds /img2threejs to Claude Code: input one reference image, get back not a mesh file but pure TypeScript code — rebuilding the object from primitives and procedural shaders, with a runtime hierarchy ready to animate."
pubDate: "2026-07-31"
updatedDate: "2026-07-31"
category: "Tech-News"
tags: ["Three.js", "3D生成", "WebGL", "Claude Code", "AI工具", "程序化生成", "generative", "Mycelium"]
heroImage: "../../assets/images/img2threejs-photo-to-threejs-code-banner.jpg"
---

*by Mycelium Protocol*

---

一个 16 天前才建的 GitHub 仓库，今天 8591 颗星。

**[img2threejs](https://github.com/img2threejs/img2threejs)** 做了一件事：给 Claude Code 或 Codex 一张参考图，让 AI 重建这个物体——但输出不是 3D 模型文件，不是 OBJ，不是 GLTF，而是一段 **TypeScript 代码**，在浏览器里实时构造出来。

---

## 核心区别：代码，不是网格

现有的图片转 3D 工具，大多数输出的是某种 mesh——提取点云、重建表面、生成 GLB。你得到的是"捕捉到的形状"。

img2threejs 的方向相反：

> 重新建造它，而不是捕获它。

输出是一个 `THREE.Group` 工厂函数，用 TypeScript 写的，从基本几何体（BoxGeometry、LatheGeometry、自定义 BufferGeometry）和程序化着色器从零搭建目标物体。结果：

- **零文件依赖**：没有 mesh 文件，没有贴图文件，代码即物体
- **可读、可改**：生成的 TypeScript 是真实的代码，每个 mesh 都有命名，每层都有注释
- **可动画**：层级里包含 pivot、socket 和 `userData.tick`，直接可以接动画系统
- **运行在浏览器里**：Three.js 场景，不需要后端，embed 进任何 web 项目

[Demo 画廊](https://img2threejs.github.io/img2threejs-showcase/)里的每个模型，包括 CS2 武器、BMX 自行车、索尼耳机、哆啦A梦小屋——全是生成的代码，在浏览器里实时运行。

---

## 8 阶段流水线：细节驱动的雕刻

技术思路是分阶段"雕刻"，每一步都过质量关卡：

```
blockout → structural → form → material → surface → lighting → interaction → optimization
```

**关键创新：detail inventory（细节清单）**

在生成代码之前，系统先强制枚举这个物体的"身份定义细节"：

> 哑光 vs 光泽分区、倒角和圆角、面板接缝、螺丝/铆钉、雕刻或绘制线条、污迹和磨损痕迹……

每一个细节必须映射到实际的组件或材质条目。细节清单没有完成，生成就不能进行。

这个设计的效果：AI 不能靠"看起来像"蒙混过关，必须真的把结构分析清楚再动手。

---

## CS2 武器：极端质量测试

项目里最有意思的部分，是 CS2 武器专项适配（v1.4 The Weapon Update）。

Glock-18、M9 刺刀、Fade 刀……这些物体的特点是：玩家对它们太熟悉了，任何一个细节不对都会被立刻发现。

为此，img2threejs 加了 CS2 专用审查门：

- **组件覆盖率检查**：明确检查枪管/刀柄/护手等每个子组件
- **Map-stripped blockout**：在没有贴图的情况下单独验证几何结构，防止精美贴图掩盖结构错误
- **每区域置信度报告**：对图片中看不清楚的地方如实报告不确定性，而不是强行猜测

这个严格程度远超"够用就行"的水平。把 CS2 武器当成测试用例，恰好是因为它们能暴露流水线的任何弱点。

---

## 用法：Claude Code 技能

安装就是 clone 到技能目录：

```bash
git clone https://github.com/img2threejs/img2threejs.git ~/.claude/skills/img2threejs
```

使用：

```
/img2threejs Rebuild this object as a Three.js model, keep the proportions, angles, and colours.
```

附上参考图片，剩下的——细节分析、流水线执行、每阶段的渲染对比——都自动跑。

Python 脚本是纯 stdlib（3.10+），不需要额外安装依赖。如果想手动跑：

```bash
python3 forge/stage1_intake/probe_image.py <image>
python3 forge/stage2_spec/new_sculpt_spec.py "Name" --image <image> --out spec.json
python3 forge/stage3_build/generate_threejs_factory.py spec.json --out src/createObjectModel.ts
```

---

## 版本进化：16天的速度

| 版本 | 主题 | 时间 |
|------|------|------|
| v1.0 | 物体流水线，分阶段雕刻 | 2026-07-15 |
| v1.1 | 细节清单，严格质量门 | - |
| v1.2 | 人形角色生成，解剖比例轨道 | - |
| v1.3 | Divine Eye 确定性审查框架，CIEDE2000 色彩数学 | - |
| v1.4 | The Weapon Update：CS2 武器专项 | - |
| **v1.4.3** | CS2 强化，组件覆盖验证 | 2026-07-31 |

16 天从 v1.0 到 v1.4.3，速度说明社区热度相当高（653 个 fork）。

---

## 路线图：从资产到可玩世界

官方 roadmap 的弧线很清楚：

- **v1.5** — The Character Update（进行中）：角色重建、面部特征、可绑骨拓扑
- **v1.6** — The Environment Update：建筑、房间、街道、植被
- **v1.7** — The Game Pipeline Update：Unity/Unreal 导出器、Blender 桥接、LOD 和碰撞体生成
- **v1.8** — The Animation Update：自动绑骨、蒙皮权重、Mixamo 兼容
- **v1.9** — The AI Studio Update：Web UI、批处理、可视化提示构建器
- **v2.0** — The Procedural World Update：多视角重建、程序化城市生成、AI 游戏资产平台

总体方向：**资产（v1.x） → 世界（v1.6-1.7） → 制作流程（v1.8-1.9） → 从参考图生成可玩世界（v2.0）**

---

## 为什么这个方向有意思

主流 3D 生成思路是"让 AI 理解三维空间，输出点云或 NeRF 或 mesh"。img2threejs 的思路是"让 AI 理解物体结构，然后重新写代码把它造出来"。

代码生成的好处是：可审查、可修改、零运行时依赖、可以直接用在前端项目里。代价是：不如 mesh 直接，对复杂有机形态的支持需要更多工作（路线图里 v1.5 才开始做角色）。

但对硬表面物体——产品展示、游戏道具、工业设计——这个方向的适配度非常高。

Apache 2.0，可以直接用在商业项目里。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## img2threejs: Give AI One Image, Get Back Runnable Three.js Code

*by Mycelium Protocol*

A GitHub repository that didn't exist 16 days ago. Today: 8,591 stars.

**[img2threejs](https://github.com/img2threejs/img2threejs)** does one thing: given a reference image and a Claude Code (or Codex) agent, it rebuilds the object in that image — not as a mesh file, not as OBJ or GLTF, but as **TypeScript code** that constructs the object live in the browser.

### The Core Distinction: Code, Not Mesh

Most image-to-3D tools output captured geometry — point clouds, reconstructed surfaces, GLB files. You get a frozen shape.

img2threejs goes the opposite direction:

> Rebuild it, don't capture it.

The output is a `THREE.Group` factory function in TypeScript, constructing the target object from geometric primitives (BoxGeometry, LatheGeometry, custom BufferGeometry) and procedural shaders. This means:

- **Zero file dependencies**: no mesh files, no texture files — code is the object
- **Readable and modifiable**: the generated TypeScript is real code, every mesh named, every layer commented
- **Animation-ready**: the hierarchy includes pivots, sockets, and `userData.tick` for idle animations
- **Browser-native**: embed into any web project, no backend required

Every model in the [demo gallery](https://img2threejs.github.io/img2threejs-showcase/) — CS2 weapons, a BMX bike, Sony earbuds, a Doraemon house diorama — is generated code, running live in your browser.

### The Pipeline: Detail-First Sculpting in 8 Stages

```
blockout → structural → form → material → surface → lighting → interaction → optimization
```

The critical innovation is the **detail inventory**: before any code is generated, the system enumerates the object's identity-defining details:

> Gloss vs. matte zones, bevels and rounding, panel seams, screws and rivets, engraved or painted linework, stains and wear patterns...

Each detail must map to a real component or material entry. If the inventory isn't complete, generation is blocked. The AI can't fake its way through "looks approximately right" — it has to actually analyze the structure first.

### CS2 Weapons as Extreme Quality Test

The most interesting part of the project is the CS2 weapon adapter (v1.4, "The Weapon Update"). Glock-18, M9 Bayonet, Classic Knife — these objects are familiar enough that any missed detail gets spotted immediately. The pipeline runs specialized review gates:

- **Component coverage check**: explicit verification of every subcomponent (barrel, grip, guard)
- **Map-stripped blockout**: geometry verified in the absence of textures, preventing attractive materials from hiding structural errors
- **Per-region confidence reporting**: uncertain areas are declared, not faked

Using CS2 weapons as a test case is intentional — they surface every weak point in the pipeline at maximum fidelity demand.

### Usage: Claude Code Skill

```bash
git clone https://github.com/img2threejs/img2threejs.git ~/.claude/skills/img2threejs
```

```
/img2threejs Rebuild this object as a Three.js model, keep the proportions, angles, and colours.
```

Attach a reference image; the pipeline handles detail analysis, staged generation, and render comparisons automatically.

### Roadmap: From Assets to Playable Worlds

The planned arc is clear: **v1.5** (characters) → **v1.6** (environments) → **v1.7** (game pipeline: Unity/Unreal exporters, Blender bridge) → **v1.8** (animation: auto-rigging, Mixamo) → **v1.9** (web UI studio) → **v2.0** (procedural world generation, AI game-asset platform from reference images).

The conceptual bet is that "generate code that builds the thing" is a more useful output format than "generate a mesh of the thing" for real production pipelines. Apache 2.0; commercial use allowed.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
