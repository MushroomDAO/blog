---
title: "blender-threejs-product-skills：四个 Skill 把工程模型变成 Web 3D"
titleEn: "blender-threejs-product-skills: Four Skills to Turn Engineering Models into Web-Ready 3D"
description: "doofly/blender-threejs-product-skills，MIT，AI agent skill 集合，定义了「工程模型 → Three.js/WebGL 产品资产」四步流水线：$threejs-product-lowpoly（高模降面）、$threejs-product-basecolor（UV + Base Color 烘焙）、$threejs-product-lighting（中性产品布光）、$threejs-product-light-bake（漫反射预烘焙）。适用于 CAD 导出模型、工业机械、工程产品转成浏览器/移动/嵌入式实时可视化资产。每个 Skill 都是 Markdown 指令，告诉 AI Agent 具体的 Blender 操作顺序、参数设置和检查点。"
descriptionEn: "doofly/blender-threejs-product-skills, MIT. AI agent skill collection defining a four-step Blender → Three.js/WebGL product asset pipeline: $threejs-product-lowpoly (high-poly reduction), $threejs-product-basecolor (UV + Base Color bake), $threejs-product-lighting (neutral product lighting), $threejs-product-light-bake (diffuse pre-bake). Designed for CAD-exported, scanned, or high-poly product/industrial models targeting browser/mobile/embedded real-time visualization. Each skill is a Markdown instruction document telling the AI agent exact Blender operation sequences, parameter settings, and checkpoints."
pubDate: 2026-10-06
heroImage: "../../assets/images/blender-threejs-product-skills-cad-to-webgl-pipeline-banner.jpg"
category: "Tech-Experiment"
tags: ["游戏开发", "3D资产", "Blender", "AI工具", "WebGL", "开发工具"]
lang: "zh-CN"
wechatTitle: "blender-threejs-product-skills四步管线"
wechatDigest: "MIT；CAD→低模→UV→预烘焙→Three.js；AI Agent Blender操作Skill"
---

CAD 工程模型导入 Blender 之后想跑进浏览器，通常要经历：几何体清理（CAD 面片混乱，布线不适合实时渲染）→ UV 展开 → 贴图烘焙 → Three.js 场景布光 → 导出 GLB。每一步都有坑，加在一起对不熟悉 Blender 的人来说门槛很高。

`blender-threejs-product-skills` 把这四步封装成了四个 AI agent skill 文件——告诉 AI Agent 在 Blender 里应该按什么顺序做什么、用什么参数、检查什么。

GitHub: https://github.com/doofly/blender-threejs-product-skills | MIT

---

## 四个 Skill 构成一条流水线

设计意图非常明确：**四个 Skill 不是四个独立提示词，而是一条 Blender → Three.js 产品资产流水线的四个阶段**，每一步以上一步的输出为前提。

### Skill 1：`$threejs-product-lowpoly` — 几何降面

**输入**：高模 / CAD 导出 / 扫描模型  
**输出**：适合实时渲染的低多边形几何体

核心思路：
- 优先**重建**简单机械零件（比平铺 Decimate 好），而不是全局一刀切降面
- 保留产品轮廓、比例、机械关系、层级结构和动画轴心点
- 删除低价值 CAD 特征（小圆角、装饰细节），清理拓扑
- 全局 Decimate 是最后手段，优先用共面溶解 + 局部 Decimate

输出结果是一个"几何检查点"，经过下游 UV、贴图、glTF 和 Three.js 工作前可以在此锁定。

```text
Use $threejs-product-lowpoly to optimize the current Blender product model for Three.js.
```

---

### Skill 2：`$threejs-product-basecolor` — UV + Base Color 烘焙

**输入**：已通过 lowpoly 检查点的几何体  
**输出**：干净的 UV 展开 + 无光照 Base Color 贴图

关键点：
- **只有在拓扑稳定之后才创建最终 UV**（lowpoly 阶段可能改变布线）
- 烘焙的是实际材质颜色，不含光照/阴影/AO/反射
- 烘焙设置：`Color: ON, Direct: OFF, Indirect: OFF`
- 严格控制 UV atlas padding，检查 mip 级别下的颜色渗漏

```text
Use $threejs-product-basecolor to rebuild UVs and bake a clean Base Color texture for the approved low-poly asset.
```

---

### Skill 3：`$threejs-product-lighting` — 产品中性布光

**输入**：低模 + 材质  
**输出**：适合任意视角旋转的产品布光方案，以及对应的 Three.js 运行时布光策略

核心要求：
- 支持产品任意角度旋转（不能只对一个视角好看）
- 检查多个视点，控制过曝高光和死黑阴影
- 保持形体轮廓和曲率可读性
- 同时输出等效的 Three.js 运行时布光方案文档

```text
Use $threejs-product-lighting to create neutral multi-angle product lighting suitable for Three.js.
```

---

### Skill 4：`$threejs-product-light-bake` — 光照预烘焙

**输入**：通过 basecolor + lighting 两步的资产  
**输出**：Base Color + 直接光 + 间接光 合并到一张贴图

适用场景：**固定展示的产品**（不需要动态照明），比如电商产品页、工业说明文档、嵌入式展示屏。

烘焙设置：`Color: ON, Direct: ON, Indirect: ON`

这条路径支持使用 `Unlit glTF` 或 Three.js 的 `MeshBasicMaterial`，运行时几乎不需要 GPU 算力，跨设备显示稳定。

```text
Use $threejs-product-light-bake to bake Diffuse Color + Direct + Indirect lighting into the final presentation texture.
```

---

## 适用场景

这套流水线明确针对以下类型的资产：
- **CAD 导出模型**（SolidWorks/Fusion360/CATIA 出来的网格）
- **工业机械和设备**
- **工程产品展示**（网站/嵌入式屏/VR 展厅）
- **高面数产品扫描**

不适合：游戏角色、有机体、需要精细骨骼动画的资产。

---

## 如何使用

将这四个 `.md` Skill 文件配置到支持 SKILL.md 格式的 AI Agent 工具里（如 AI Art Engine、DSH 等），然后按顺序在聊天窗口里调用对应的 Skill 命令。每个 Skill 会指导 AI Agent 完成对应阶段的 Blender 操作。

---

> MIT 开源。doofly 维护，适用于 CAD/工程模型的 Three.js 实时可视化资产准备。开源仅供学习参考。

---

<!--EN-->

## blender-threejs-product-skills: Four Skills to Turn Engineering Models into Web-Ready 3D

Getting a CAD engineering model from Blender into a browser requires: geometry cleanup (CAD meshes have messy topology unsuitable for real-time rendering) → UV unwrap → texture bake → Three.js lighting → GLB export. Each step has pitfalls; combined, they're a steep barrier for anyone not fluent in Blender.

`blender-threejs-product-skills` encapsulates these four steps into four AI agent skill files — each tells the AI agent exactly what to do in Blender, in what order, with what parameters, and what to check.

GitHub: https://github.com/doofly/blender-threejs-product-skills | MIT

---

### Four Skills, One Pipeline

**These four skills are not four independent prompts — they are four stages of a Blender → Three.js product asset pipeline**, each taking the previous stage's output as its input.

**Skill 1: `$threejs-product-lowpoly`** — High-poly/CAD/scanned model → optimized low-poly geometry. Prefers reconstruction over global Decimate; preserves silhouette, proportions, mechanical relationships, hierarchy, and animation pivots; removes low-value CAD features.

**Skill 2: `$threejs-product-basecolor`** — Approved geometry → UV + Base Color atlas. UV creation happens only after topology is stable. Bake settings: `Color: ON, Direct: OFF, Indirect: OFF` — pure diffuse color, no lighting baked in.

**Skill 3: `$threejs-product-lighting`** — Neutral multi-angle product lighting + equivalent Three.js runtime lighting strategy. Must look correct from any rotation angle; documents the Three.js equivalent setup.

**Skill 4: `$threejs-product-light-bake`** — Base Color + Direct + Indirect → one pre-lit texture. Bake settings: `Color: ON, Direct: ON, Indirect: ON`. Supports Unlit glTF or Three.js `MeshBasicMaterial` for stable cross-device appearance at minimal runtime GPU cost.

---

### Target Use Cases

CAD-exported models (SolidWorks/Fusion360/CATIA), industrial machinery, engineering product visualization (websites, embedded displays, VR showrooms), high-poly product scans. Not designed for game characters, organic meshes, or assets requiring skeletal animation.

---

### Usage

Add these four `.md` skill files to any AI agent tool supporting the SKILL.md format (AI Art Engine, DSH, etc.), then call the corresponding skill commands in chat in sequence.

---

> MIT. Maintained by doofly, designed for CAD/engineering model preparation for Three.js real-time visualization. For technical reference only.
