---
title: "Hairline：33 个等距线条动效，零依赖，给网页加一层科技感"
titleEn: "Hairline: 33 Isometric Line Animations, Zero Dependencies, for Web UIs"
description: "lucasmarkes 开源 Hairline（MIT，约 1.4K stars）：零依赖 ESM 等距线条图形库，33 个内置图形按鼠标指针位置实时响应动画，35 kB 全量包，单图形约 6.25 kB。图形按主题分组：界面/数据/机器/设备/编程/安全/连接，命名如 terrain、keyboard、vault、locker、router、hub 等，风格统一——纤细描边、立体等距、极简机械感。支持 React 18+（@lucasmarkes/hairline/react）和原生 JS 两套 API，均有 update()/destroy() 接口。配套 hairline-create Skill：Claude Code/AI Agent 用它按照 Hairline 规则生成新图形，输出一个自包含 HTML 文件，不需要安装任何东西就能直接打开。"
descriptionEn: "lucasmarkes open-sourced Hairline (MIT, ~1.4K stars): a zero-dependency ESM isometric line graphics library with 33 built-in figures that respond to the pointer in real time. Full bundle is 35 kB; single figure ~6.25 kB. Figures are grouped by theme: Interfaces/Data/Machines/Devices/Coding/Security/Connectivity — names like terrain, keyboard, vault, locker, router, hub. Unified style: thin strokes, isometric depth, minimal-mechanical. Two APIs: React 18+ (@lucasmarkes/hairline/react) and vanilla JS. Comes with a hairline-create Skill for Claude Code/AI Agents to generate new figures, outputting a self-contained HTML file with no install required."
pubDate: 2026-10-10
heroImage: "../../assets/images/hairline-lucasmarkes-isometric-line-animation-web-library-banner.jpg"
category: "Tech-Experiment"
tags: ["前端", "动效", "React", "开源工具", "UI组件"]
lang: "zh-CN"
wechatTitle: "Hairline：33个等距线条动效，零依赖库"
wechatDigest: "MIT 约1.4K；零依赖ESM；33图形鼠标交互；35kB全量；hairline-create Skill"
---

在网页上加一块「会动的等距图形」，通常要么引入一个很重的动画库，要么花几天手写 SVG + 动画逻辑。

Hairline 把这件事压缩到一行安装命令：

```bash
npm i @lucasmarkes/hairline
```

MIT，约 1.4K stars，零依赖，35 kB 全量包。GitHub: https://github.com/lucasmarkes/hairline

---

## 33 个内置图形，7 个主题分组

当前版本 0.5.0 有 33 个图形，按主题分组：

| 分组 | 风格 |
|------|------|
| Interfaces | 界面类：地形起伏（terrain）、转盘（turntable）等 |
| Data | 数据类：图表（plot）、查询（query）、滤筛（sieve）等 |
| Machines | 机械类：机柜（cabinet）、保险库（vault）、路由器（router）等 |
| Devices | 设备类：键盘（keyboard）、电话（phone）、笔记本（laptop）等 |
| Coding | 编程类：终端（terminal）、补丁（patch）等 |
| Security | 安全类：锁（padlock）、储物柜（lockers）等 |
| Connectivity | 连接类：天线（dish）、集线器（hub）、中继（relay）等 |

所有图形风格一致：**纤细描边、立体等距、极简机械感**，视觉上同属一套体系，放进一个页面不会互相打架。

---

## 鼠标交互内置

每个图形会跟着鼠标指针位置实时更新动画——倾斜角度、遮挡关系、线条粗细都在动。不需要额外写任何事件监听代码，这个行为是内置的。

---

## 两套 API

**Vanilla JS（原生 DOM）：**

```js
import { terrain } from '@lucasmarkes/hairline'

const fig = terrain(document.getElementById('canvas'), {
  intensity: 0.8,
  theme: 'dark'
})

// 更新参数
fig.update({ intensity: 1.2 })

// 销毁
fig.destroy()
```

**React 18+：**

```tsx
import { Terrain } from '@lucasmarkes/hairline/react'

<Terrain
  intensity={0.8}
  theme="dark"
  label="地形"
  play  // 自动巡游各个展示位置
  onRead={(data) => console.log(data)}
/>
```

React 组件声明为客户端模块，但父 Server Component 不需要加 `"use client"`。

---

## 包体积

| 范围 | 大小 |
|------|------|
| 全部 33 图形（Vanilla） | **35.07 kB** |
| 全部 33 图形（React） | **35.48 kB** |
| 单个图形 | **约 6.25 kB** |

按需引入的话，单图形只有 6.25 kB。

---

## hairline-create：让 AI 画新图形的 Skill

配套有一个 `hairline-create` Skill，供 Claude Code / AI Agent 使用：

```bash
npx skills add https://github.com/lucasmarkes/hairline --skill hairline-create
```

这个 Skill 让 AI 按照 Hairline 的规则——等距视角、指针响应、3–6 个巡游展示位——生成一个**自包含 HTML 文件**。

生成出来的文件直接用浏览器打开就能运行，不需要安装任何东西，也不依赖 npm。验证时用 Playwright 截图确认渲染结果。

---

## 适合用在哪里

- **官网首屏**：地形起伏、集线器、保险库这类图形放在 Hero 区有科技感，又不刺眼
- **功能介绍模块**：键盘、电话、路由器等图形直接对应产品类型
- **技术博客 / 文档**：终端、补丁、查询这类 Coding 分组图形适合技术内容场景

---

## 已知边界

- 纯 ESM，CommonJS 项目需要额外处理
- 33 个图形风格固定（等距线条），如果需要其他视觉风格，这个库不适合
- Stars 约 1.4K，独立开发者项目，生产可用性视项目规模自判
- 无内置动画时间线控制（只有 `play` 巡游），复杂脚本化动画需自行实现

---

## 一句话说清楚

Hairline 是一个零依赖的等距线条图形库：33 个内置图形响应鼠标位置，35 kB 全量包，React 和原生 JS 都能用。配套 `hairline-create` Skill 可让 AI 直接生成符合规范的新图形，输出自包含 HTML 文件。

---

> MIT。lucasmarkes，v0.5.0，约 1.4K stars。开源仅供学习参考。

---

<!--EN-->

## Hairline: 33 Isometric Line Animations, Zero Dependencies, for Web UIs

Adding an animated isometric graphic to a web page usually means importing a heavy animation library or spending days hand-writing SVG + animation logic. Hairline compresses this to one install command:

```bash
npm i @lucasmarkes/hairline
```

MIT, ~1.4K stars, zero dependencies, 35 kB full bundle. GitHub: https://github.com/lucasmarkes/hairline

---

### 33 Built-In Figures, 7 Theme Groups

Version 0.5.0 ships 33 figures, grouped by theme:

| Group | Examples |
|-------|---------|
| Interfaces | terrain, turntable, riffle |
| Data | plot, query, sieve |
| Machines | cabinet, vault, router |
| Devices | keyboard, phone, laptop |
| Coding | terminal, patch |
| Security | padlock, lockers |
| Connectivity | dish, hub, relay |

All figures share one visual language: thin strokes, isometric depth, minimal-mechanical. They're designed to coexist on the same page without visual conflict.

---

### Pointer Interaction Is Built In

Every figure updates in real time as the pointer moves — tilt, occlusion, line weight all animate. No event listeners needed; it's baked in.

---

### Two APIs

**Vanilla JS:**

```js
import { terrain } from '@lucasmarkes/hairline'

const fig = terrain(document.getElementById('canvas'), { intensity: 0.8 })
fig.update({ intensity: 1.2 })
fig.destroy()
```

**React 18+:**

```tsx
import { Terrain } from '@lucasmarkes/hairline/react'

<Terrain intensity={0.8} theme="dark" play onRead={(d) => console.log(d)} />
```

React components are declared as client modules but parent Server Components don't need `"use client"`.

---

### Bundle Size

| Scope | Size |
|-------|------|
| All 33 figures (Vanilla) | **35.07 kB** |
| All 33 figures (React) | **35.48 kB** |
| Single figure | **~6.25 kB** |

---

### hairline-create: A Skill to Draw New Figures

```bash
npx skills add https://github.com/lucasmarkes/hairline --skill hairline-create
```

This Skill lets Claude Code / AI Agents generate new Hairline-compatible figures following the library's rules — isometric perspective, pointer response, 3–6 tour stops. The output is a **self-contained HTML file**: open directly in a browser, no npm install required. Playwright screenshots the result to validate rendering.

---

### Good Use Cases

- **Site hero sections**: terrain, hub, vault add tech feel without being aggressive
- **Feature intro blocks**: keyboard, phone, router map naturally to product categories
- **Tech blogs / docs**: terminal, patch, query suit technical content

---

### Known Limits

- ESM-only; CommonJS projects need extra handling
- Style is fixed (isometric line art) — not a general-purpose animation library
- ~1.4K stars, solo developer project
- No animation timeline control (only `play` tour) — complex scripted sequences need custom implementation

---

### TL;DR

Hairline is a zero-dependency isometric line graphics library: 33 figures respond to the pointer, 35 kB full bundle, works with React and plain JS. The `hairline-create` Skill lets AI generate new compliant figures as self-contained HTML files.

---

> MIT. lucasmarkes, v0.5.0, ~1.4K stars. For reference only.
