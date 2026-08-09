---
title: "Driver.js：5kb 的零依赖聚焦库，8年 26K stars 说明什么是正确的底层工具"
titleEn: "Driver.js: 5KB Zero-Dependency Focus Library — 8 Years, 26K Stars, Still the Right Primitive"
description: "nilbuild/driver.js，26437 stars，MIT，2018年至今持续维护。5kb gzipped，零依赖，纯 TypeScript，覆盖 product tour、聚焦高亮、上下文 popover、overlay 等所有用户引导场景。最新版 1.8.0（2026-07-17）。"
descriptionEn: "nilbuild/driver.js, 26,437 stars, MIT, maintained since 2018. 5KB gzipped, zero dependencies, pure TypeScript. Covers product tours, focus highlighting, contextual popovers, and overlay needs. Latest v1.8.0 (2026-07-17)."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["前端", "开源", "用户体验", "TypeScript", "产品引导", "工具库", "零依赖"]
heroImage: "../../assets/images/driverjs-lightweight-product-tour-overlay-library-5kb-banner.jpg"
---

> **仓库**：nilbuild/driver.js · TypeScript · MIT · 26437 stars
> **最新版本**：1.8.0（2026-07-17）
> **创建**：2018-03-11（8年持续维护）
> **官网**：driverjs.com

---

## 一、不只是 tour 库

Driver.js 的 README 第一句话就在纠正误解：

> "No, it's more than a tour library. **Tours are just one of the many use-cases.**"

它的核心能力是：**把页面上任何元素聚焦高亮，同时把其他内容 dim 掉**。tour 是这个能力的一种用法，但不是全部。

其他常见用法：
- 用户填表时，高亮当前填写的字段，保持注意力集中
- "暗化灯光"效果（视频播放器上常见）
- 表单字段的上下文 popover 帮助
- 把注意力引导到页面某个组件
- 当简单 modal 用

一个 API，多种语义，按你需要的方式组合。

---

## 二、5kb vs 12kb+：大小差距的实际意义

Driver.js gzip 后 **5kb**，同类库普遍是 12kb+。

这个差距在 2026 年依然重要。原因不只是加载速度——而是你的构建预算。

现代 Web 应用的 bundle 里平均有 40-60 个第三方库。每个库 "就 10kb 而已" 的选择叠加起来，JS 负荷轻松超过 1MB。Driver.js 选择把自己限制在 5kb，是一个明确的设计取舍：**只做核心的事，把复杂度留给使用方**。

零外部依赖是这个取舍的前提。没有 popper.js，没有 animate.css，没有任何隐性依赖——就是一个 TypeScript 文件，能用在任何框架里（React、Vue、Svelte、Vanilla）。

---

## 三、提供 hooks 的 overlay 库

Driver.js 之所以比"写一段高亮逻辑"要好，是因为它处理了你懒得想的边界情况：

- 被高亮元素在视口外 → 自动滚动到位
- 元素在高亮前/高亮时/取消选中时的钩子（`onHighlightStarted` / `onHighlighted` / `onDeselected`）
- 键盘导航（方向键、Escape、Tab 全程可控）
- 跨浏览器的 overlay 渲染一致性
- Popover 位置自动计算（贴近目标元素，不超出视口）

hooks 的存在让它适合复杂场景：比如在某个引导步骤激活时动态加载数据，或在用户跳过 tour 时记录到你的 analytics 系统。

---

## 四、技术实现

纯 Vanilla TypeScript，无框架依赖，构建产物是 ESM + CJS 双格式。

开发环境用 Astro 搭了一个 playground：

```sh
pnpm install
pnpm run playground:install
pnpm dev
```

`playground/src/examples/` 下每个示例是独立文件，修改源码后 playground 热重载——这比"建一个测试 HTML"要干净得多。示例按 `highlight.ts` / `popover.ts` / `tour.ts` / `api.ts` 分组，想加新示例直接加文件。

---

## 五、8 年维护说明什么

Driver.js 创建于 2018 年，现在是 2026 年，v1.8.0 刚在 7 月 17 日发布。

8 年还在迭代的工具库，在前端生态里是罕见的。大多数"好用的前端库"在 2-3 年后要么被作者放弃，要么被框架内置能力替代，要么被更新的轮子取代。

Driver.js 活下来的原因很直接：它做的事情（overlay + 聚焦）在 Web 里是永久需求，而它的实现足够轻量、足够干净，没有让人"不得不换掉它"的理由。

26K stars 里，有很大一部分是今天仍在用它的项目——不是历史积累的数字，而是当前活跃的选择。

---

## 六、在 AI 工具时代的新相关性

2026 年有一个新的角度值得提一下。

随着 AI 生成 UI、动态生成页面结构越来越普遍，**用户引导的需求反而在上升**：用户面对的界面变化更快，不熟悉的元素更多，需要更频繁的上下文提示和功能介绍。

Driver.js 这类工具的 "零依赖 + 任何元素都能高亮" 特性，在 AI 生成 UI 的场景里特别合适——你不知道 AI 会生成什么结构，但只要是 DOM 元素，Driver.js 就能指向它。

---

## 七、什么时候用，什么时候不用

**适合用的场景**：
- SaaS 产品的功能 onboarding（初次登录引导、新功能提示）
- 管理后台的操作提示
- 需要引导用户注意力到特定区域的任何场景
- 任何需要 overlay + popover 组合效果的需求

**不适合用的场景**：
- 需要非常复杂的动画效果（Driver.js 的动效相对简单）
- 需要视频 / 图片嵌入到 popover 里（需要自定义渲染）
- 移动端复杂手势配合（键盘导航是主要输入方式）

**安装**：

```bash
npm install driver.js
# 或
pnpm add driver.js
```

**最小示例**：

```typescript
import Driver from 'driver.js';
import 'driver.js/dist/driver.min.css';

const driver = new Driver();
driver.highlight('#my-element');
```

---

*数据来源：GitHub nilbuild/driver.js，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: nilbuild/driver.js · TypeScript · MIT · 26,437 stars
> **Latest Release**: 1.8.0 (2026-07-17)
> **Created**: 2018-03-11 (8 years of active maintenance)
> **Homepage**: driverjs.com

---

## 1. More Than a Tour Library

Driver.js opens its README with a correction:

> "No, it's more than a tour library. **Tours are just one of the many use-cases.**"

Its core capability is: **focus-highlight any element on the page while dimming everything else.** Product tours are one application of that capability — not the whole story.

Other common uses:
- Highlighting the active form field while the user fills it in, keeping focus sharp
- "Turn off the lights" effect (common on video players)
- Contextual popover help while filling forms
- Drawing attention to a specific page component
- Serving as a lightweight modal substitute

One API, multiple semantics — compose however your use case demands.

---

## 2. 5KB vs. 12KB+: Why Size Still Matters

Driver.js is **5KB gzipped**. Comparable libraries are typically 12KB+.

That gap still matters in 2026 — not just for load speed, but for bundle budgets.

The average modern web app includes 40–60 third-party libraries. Every library that's "only 10KB anyway" stacks up. JS payloads above 1MB are common. Driver.js deliberately caps itself at 5KB: **do only the core thing, leave complexity to the caller.**

Zero external dependencies makes this possible. No popper.js, no animate.css, no hidden transitive dependencies — just one TypeScript file that works in any framework (React, Vue, Svelte, Vanilla).

---

## 3. An Overlay Library With Hooks

What makes Driver.js better than writing your own highlight logic is that it handles all the edge cases you'd forget about:

- Target element is outside the viewport → auto-scroll to it
- Lifecycle hooks: `onHighlightStarted` / `onHighlighted` / `onDeselected`
- Full keyboard navigation (arrow keys, Escape, Tab all work)
- Cross-browser overlay rendering consistency
- Automatic popover positioning (stays close to target, doesn't overflow viewport)

The hooks make it viable for complex scenarios — dynamically loading data when a tour step activates, or logging skip events to your analytics system.

---

## 4. Technical Implementation

Pure Vanilla TypeScript, no framework dependencies, output in ESM + CJS dual format.

The dev environment uses Astro for a live playground:

```sh
pnpm install
pnpm run playground:install
pnpm dev
```

Each example under `playground/src/examples/` is an independent file with hot-reload from source. Examples are grouped as `highlight.ts` / `popover.ts` / `tour.ts` / `api.ts` — adding a new example is as simple as dropping in a file.

---

## 5. What 8 Years of Maintenance Signals

Driver.js was created in 2018. It's now 2026. v1.8.0 shipped July 17th.

A frontend utility library still actively iterating after 8 years is genuinely rare. Most "great frontend libraries" are abandoned by their authors within 2–3 years, subsumed by framework built-ins, or displaced by a newer wheel.

Driver.js survived because what it does — overlay + focus — is a permanent Web requirement, and the implementation is light enough and clean enough that there's no compelling reason to replace it.

Of its 26K stars, a large fraction represent projects actively using it today — not historical accumulation but current active choice.

---

## 6. New Relevance in the AI Tooling Era

2026 adds a new angle worth noting.

As AI-generated UIs and dynamically generated page structures become more common, **the need for user onboarding and guidance is actually increasing**: interfaces change faster, unfamiliar elements appear more frequently, and users need more contextual cues and feature introductions.

Driver.js's "zero-dependency, highlight any element" property is particularly well-suited to AI-generated UI — you don't know what structure an AI will generate, but as long as it's a DOM element, Driver.js can point to it.

---

## 7. When to Use It, When Not To

**Good fit:**
- SaaS product onboarding (first-login tours, new feature highlights)
- Admin dashboard operation hints
- Any scenario requiring guided attention to a specific area
- Any need for an overlay + popover combination

**Not the best fit:**
- Complex animation requirements (Driver.js animations are relatively simple)
- Popover content that embeds video or images (requires custom rendering)
- Mobile-heavy touch gesture workflows (keyboard navigation is the primary input model)

**Install:**

```bash
npm install driver.js
# or
pnpm add driver.js
```

**Minimal example:**

```typescript
import Driver from 'driver.js';
import 'driver.js/dist/driver.min.css';

const driver = new Driver();
driver.highlight('#my-element');
```

---

*Data source: GitHub nilbuild/driver.js, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
