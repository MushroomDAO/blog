---
title: "Shaders：把 WebGPU 封装成组件的特效库开源了"
titleEn: "Shaders: A WebGPU Effect Component Library Just Went Open Source"
description: "Shader Effects Inc. 于 2026-10-06 开源了 Shaders（MIT），这是一套把 WebGPU 能力封装成语义化组件的前端特效库。199 个效果组件，覆盖渐变、噪点、玻璃、金属、光效、扭曲、转场、模糊、光标特效，支持 React、Vue、Svelte、Solid、JavaScript 和 Framer，props 跨框架完全一致。嵌套、混合、蒙版全部在 GPU 上完成。核心（渲染引擎+组件+框架绑定）MIT 开源；Shaders Pro（1,000+ 预设、55+ 预制 Section、无水印视频渲染）继续付费。2.5K stars，需要浏览器 WebGPU 支持。注：此库为 Shader Effects Inc.（founder: Simon）开发，与 Evan You 无关，Evan You 支持 Vue 生态但不是此项目的作者。"
descriptionEn: "Shader Effects Inc. open-sourced Shaders (MIT) on 2026-10-06 — a frontend effect library that wraps WebGPU capabilities into semantic components. 199 effect components covering gradients, noise, glass, metal, light effects, distortion, transitions, blur, cursor effects; supports React, Vue, Svelte, Solid, JavaScript, and Framer with identical props across frameworks. Nesting, mixing, and masking all happen on the GPU. Core (rendering engine + components + framework bindings) is MIT; Shaders Pro (1,000+ presets, 55+ pre-built Sections, watermark-free video rendering) remains paid. 2.5K stars, requires browser WebGPU support. Note: built by Shader Effects Inc. (founder: Simon), not Evan You."
pubDate: 2026-10-08
heroImage: "../../assets/images/shaders-webgpu-component-library-react-vue-svelte-solid-banner.jpg"
category: "Tech-Experiment"
tags: ["前端工具", "WebGPU", "开源工具", "React", "Vue", "开发工具"]
lang: "zh-CN"
wechatTitle: "Shaders：WebGPU效果组件库开源了"
wechatDigest: "MIT；2.5K stars；199个GPU效果；React/Vue/Svelte/Solid；嵌套混合蒙版"
---

**先纠正一个流传的误属：Shaders 不是 Evan You（Vue.js 作者）的作品。** 开发方是 Shader Effects Inc.，创始人叫 Simon。Evan You 的核心工作是 Vue.js，Shaders 支持 Vue 作为框架之一，这可能是误读的来源。

正确归属之后，这个库本身值得介绍。

GitHub: https://github.com/shader-effects-inc/shaders | ⭐ 2,500 | MIT

---

## 它做什么

WebGPU 是浏览器访问 GPU 的新标准，比 WebGL 更低层次、更强大，但直接写 WGSL 着色器代码的门槛很高。

Shaders 把这个能力封装成**语义化组件**：你不需要写任何 WGSL，引入组件、传 props，GPU 特效就附着在你的 DOM 元素上。

```jsx
// React 示例
import { GlassEffect } from '@shaders/react'

<GlassEffect blur={12} tint={0.3} saturation={1.5}>
  <YourCard />
</GlassEffect>
```

Vue、Svelte、Solid 的用法和 props 完全一致，不需要为不同框架学习不同 API。

---

## 199 个效果，分门别类

| 类别 | 效果举例 |
|------|----------|
| 渐变 | 线性、径向、网格渐变，带噪点的渐变 |
| 噪点 | 柏林噪声、单纯形噪声、分形噪声 |
| 玻璃 / 折射 | 毛玻璃、色散、液体折射 |
| 金属 | 金属光泽、彩虹色、镀铬效果 |
| 光效 | 光晕、辉光、镜头耀光、体积光 |
| 扭曲 | 波纹、漩涡、鱼眼、液化 |
| 转场 | 像素化解散、光流转场、溶解 |
| 模糊 | 运动模糊、景深、径向模糊 |
| 光标 | 磁力跟随、流体拖尾、粒子扩散 |

这些效果**嵌套、混合、蒙版**都在 GPU 上完成，不经过 CSS filter 或 canvas 绕路。

---

## 开源范围

MIT 开源的部分：
- **渲染引擎**：Shaders 的 WebGPU 渲染核心
- **所有 199 个效果组件**
- **框架绑定**：React、Vue、Svelte、Solid、JavaScript、Framer

**继续付费的 Shaders Pro**：
- 1,000+ Pro 预设（高级参数组合）
- 55+ 预制 Sections（整页效果模板）
- 无水印视频和图片渲染
- 专属 Discord 频道和优先支持

---

## 使用边界

**浏览器支持**：WebGPU 目前在 Chrome 和 Edge 全面支持，Firefox 和 Safari 仍在推进中。如果你的目标用户需要全浏览器覆盖，WebGPU 现在还不是安全选择——需要做降级处理。

**性能**：GPU 渲染对于少量复杂效果比 CSS 更高效，但大量叠加效果的显存占用需要实测。

**复杂度**：199 个组件是选择丰富，但也意味着 bundle size 需要按需引入（tree-shaking）来控制。

---

## 一句话说清楚

Shaders 把 WebGPU 封装成组件：引入一个标签、传几个 props，GPU 特效就出来了，不需要写任何着色器代码。MIT 开源，框架覆盖面广，但 WebGPU 的浏览器兼容性仍然是上线前必须评估的限制。

---

> MIT 许可。Shader Effects Inc. 开发，2026-10-06 宣布开源，GitHub 已上线。开源仅供学习参考。

---

<!--EN-->

## Shaders: A WebGPU Effect Component Library Just Went Open Source

**First, a correction on a widely-shared misattribution: Shaders was not made by Evan You (Vue.js creator).** The developer is Shader Effects Inc., founded by Simon. Evan You's work is Vue.js; Shaders supports Vue as a target framework, which is likely the source of the confusion.

With that settled — the library itself is worth covering.

GitHub: https://github.com/shader-effects-inc/shaders | ⭐ 2,500 | MIT

---

### What It Does

WebGPU is the new browser GPU API — more powerful and lower-level than WebGL, but raw WGSL shader code has a steep learning curve.

Shaders wraps this into **semantic components**: no WGSL needed, just import a component, pass props, and GPU effects attach to your DOM element.

```jsx
// React example
import { GlassEffect } from '@shaders/react'

<GlassEffect blur={12} tint={0.3} saturation={1.5}>
  <YourCard />
</GlassEffect>
```

Vue, Svelte, Solid — identical props across all frameworks.

---

### 199 Effects

| Category | Examples |
|----------|---------|
| Gradients | Linear, radial, mesh, noisy gradients |
| Noise | Perlin, simplex, fractal noise |
| Glass / refraction | Frosted glass, chromatic dispersion, liquid refraction |
| Metal | Metallic sheen, iridescence, chrome |
| Light | Halo, glow, lens flare, volumetric light |
| Distortion | Ripple, swirl, fisheye, liquify |
| Transitions | Pixelate dissolve, optical flow, dissolve |
| Blur | Motion blur, depth of field, radial blur |
| Cursor | Magnetic follow, fluid trail, particle burst |

All nesting, blending, and masking happens on the GPU — no CSS filter or canvas workarounds.

---

### Open Source Scope

MIT open source:
- **Rendering engine**: the WebGPU core
- **All 199 effect components**
- **Framework bindings**: React, Vue, Svelte, Solid, JavaScript, Framer

**Shaders Pro (paid)**:
- 1,000+ Pro presets
- 55+ pre-built Sections (full-page effect templates)
- Watermark-free video and image rendering
- Priority support and Discord access

---

### Boundaries

**Browser support**: WebGPU has full support in Chrome and Edge; Firefox and Safari are still catching up. Full browser coverage requires fallback handling — not a safe default yet for production sites targeting all audiences.

**Performance**: GPU rendering is more efficient than CSS for a few complex effects, but stacking many effects needs real-world VRAM testing.

**Bundle size**: 199 components means tree-shaking is required to keep bundle sizes reasonable.

---

> MIT license. Built by Shader Effects Inc., announced open source 2026-10-06, on GitHub. For technical reference only.
