---
title: "M3E Canvas：先画 UI 再让 AI 写代码，把设计导出成一份 6 段规格书"
titleEn: "M3E Canvas: Sketch the UI First, Then Let AI Write the Code — Design Exported as a Six-Section Spec"
description: "lnkiai/m3e-canvas 开源项目 4 天冲到 4169 星：在浏览器里拖 Material 3 Expressive 组件、连页面跳转和滑动手势，一键导出成配色/形状/屏幕结构/行为跳转/组件样式/整体原则六段固定结构的 prompt，直接交给 Claude Code、Codex、Gemini CLI。真正的增量不是「AI 画 UI」，而是把设计意图变成 prompt 里可校验的结构。纯前端无后端，数据不出浏览器。"
descriptionEn: "lnkiai/m3e-canvas hit 4,169 stars in four days: drag Material 3 Expressive components in the browser, wire up screen transitions and swipe gestures, then export a prompt with six fixed sections — colors, shape/type/motion, layout, behavior and navigation, component styles, general guidance — and hand it to Claude Code, Codex or Gemini CLI. The real gain is not 'AI draws the UI' but turning design intent into verifiable structure inside the prompt. Pure front-end, no backend, data never leaves the browser."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-News"
tags: ["开源", "AI编程", "Vibe Coding", "Material Design", "Claude Code", "Android", "前端", "本地优先", "工作流"]
heroImage: "../../assets/images/m3e-canvas-material3-sketch-to-structured-prompt-ai-coding-banner.jpg"
author: "Mycelium Protocol"
---

用 AI 写 App 最难受的一段，从来不是让它写代码，而是**跟它描述界面**。「这个按钮放右下角、点了跳到详情页、返回时从左边滑出来」——这种话说三句就乱，AI 也只能猜。

M3E Canvas 的解法是把这一段整个换掉：**你在浏览器里把界面画出来，它导出一份结构化的规格书，你把规格书交给 AI。**

它 2026-09-02 才建库，4 天冲到 4169 星。

> 📌 项目地址：https://github.com/lnkiai/m3e-canvas
> 在线可直接试（无需安装）：https://lnkiai.github.io/m3e-canvas/
> 协议 MIT ｜ Next.js 16 + React 19 ｜ 无后端

---

## 它到底做了什么

一句话：**把 Material 3 Expressive 全套组件做成可拖拽画布，再把画布上的一切翻译成一份 AI 能照着实现的规格。**

拆开是三层：

**第一层，画。** 按钮、图标按钮、FAB、分裂按钮、FAB 菜单、chips、应用栏、导航栏、浮动工具栏、标签页、搜索栏、卡片、列表、对话框、snackbar、文本框、下拉框、开关、复选框、单选、滑块、文本、图片、相机与地图占位、徽标、盒子、分隔线——全部按 Material 3 Expressive 规范绘制。两个按钮靠近会**磁性吸附**成一组，接缝处圆角自动软化。

**第二层，连。** 给任何可点元素、应用栏图标或导航栏目标指定跳转屏幕（或「返回」），并选转场：四个方向滑入、淡入、展开或无。画布上用箭头显示流向，预览里能真的点着走一遍，返回时转场反向播放。屏幕之间还能设左右上下**滑动手势**跳转，预览里画面跟着手指走。

**第三层，导出。** 这才是关键的一层。

---

## 为什么说增量在「结构」而不在「画图」

我去读了它的 prompt 生成测试（`lib/prompt.test.ts`），这一段是硬证据：导出的不是一段自由发挥的描述，而是**六个固定小节、顺序写死**的文档。

中文输出的小节标题是：

```
## 配色
## 形状、字体与动效
## 屏幕结构
## 行为与屏幕跳转
## 各组件的样式
## 整体原则
```

开头还有一行明确的平台声明：`实现目标是 Android（原生应用）。` 或 `实现目标是 Web（在浏览器中运行的应用）。`

支持四种语言输出：日语、英语、中文、韩语。连引号风格都按语言区分——中文用 `“Save”`，日语用 `「Save」`。

**这意味着什么**：AI 拿到的不是「帮我做个记事本，按钮放好看点」，而是一份分节的规格书。哪一节缺了、哪一节 AI 没实现，你能逐节对照检查。自由描述做不到这件事——你不知道自己漏说了什么，也不知道 AI 漏做了什么。

它还专门处理了两个最容易在文字描述里丢失的信息：**重叠关系**和**并排关系**。README 里写得很直白——prompt 会显式描述 overlap 和 side-by-side row，好让生成出来的布局保住这些关系。这两样恰恰是人肉描述时最先丢的。

---

## 那它和 Figma 转代码、v0、直接喂截图差在哪？

这是决定你要不要用它的真问题。

| | 输入 | 输出 | 适合什么 |
|---|---|---|---|
| **M3E Canvas** | 你拖出来的画布 | 六段结构化 prompt（文本） | 你已经知道界面长什么样，要 AI 照着实现；目标是 Android / Web |
| **Figma → code** | 完整设计稿 | 代码或代码片段 | 已有专业设计稿，团队协作场景 |
| **v0 之类** | 一句话 | 直接出代码和预览 | 你还不知道要什么，想让 AI 先给方案 |
| **喂截图给 AI** | 一张图 | 代码 | 临时抄一个已有界面 |

分界线其实很清楚：**M3E Canvas 解决的是「我知道要什么但说不清」，不是「我不知道要什么」。** 如果你连界面长什么样都还没想好，画布只会让你卡在拖组件上；这时候直接跟 AI 聊反而快。

另一条边界是设计体系。它整个建立在 Material 3 Expressive 上——七套配色预设、或者给一个种子色自动生成完整 Material 3 方案，明暗两套、三档对比度、动态取色（跟手机壁纸）。形状、字体（Roboto / Roboto Flex / Roboto Serif / 系统字体）、动效（标准或 expressive 弹簧曲线）四个轴都在一个面板里。

**代价是**：你想要一个不像 Material Design 的界面，它帮不上忙。它导出的 prompt 里塞满了 M3 的规范细节，AI 会照着做。

---

## 它同时是个「数据不出本机」的例子

README 的徽章里有一条容易被忽略：`backend: none (localStorage)`。

整个工具是纯前端，没有服务端，你画的东西存在浏览器的 localStorage 里。这有两面：

- **好的一面**：你的产品设计不上传任何地方。做商业项目的原型时这不是小事。GitHub Pages 上那个在线版和你本地跑起来的效果完全一致，因为根本没有服务端参与。
- **代价**：没有协作、没有版本历史、换浏览器就没了。清一下站点数据，设计就没了。

这是很典型的本地优先取舍——用协作能力换隐私和零依赖。要长期维护的设计，还是得导出存盘。

---

## 什么时候用它，什么时候别用

**值得用**：
- 你要做 Android 原生 App，且接受 Material Design 风格
- 界面有多个屏幕、有跳转关系——这正是文字描述最容易崩的地方
- 你已经在用 Claude Code / Codex / Gemini CLI / Cursor，缺的只是把界面说清楚

**别用**：
- 界面只有一屏两个按钮——画布的开销比直接说还大
- 你要的是非 Material 风格
- 你需要多人协作改设计

---

## 缺口：我还没验证的部分

按本站规矩，把没跑过的部分明说：

1. **一次成功率没实测**。导出的 prompt 交给 Claude Code，第一次生成能到什么程度、要返工几轮，这个数我没有。README 里有段 GIF 演示从画布到 Android 跑起来的全流程，但演示不等于你自己的项目。
2. **web target 的输出质量存疑**。prompt 支持 Android 和 Web 两个目标，但整套组件是按 Material 3 Expressive 画的。导到 Web 时 AI 用什么技术栈实现这些 M3 组件、还原度多少，没验证。
3. **项目太新**。4 天 4169 星意味着热度，不意味着稳定。一人维护、`v0` 阶段、GitHub Sponsors 链接已经挂上——维护节奏还看不出来。

---

## 一句话总结

M3E Canvas 值得装，但要清楚它换掉的是哪一段：**它不替你想界面，也不替你写代码，它把「界面长什么样」这件事从口头描述变成了一份可以逐条核对的规格书。**

对经常用 AI 写 App 的人，这一段恰好是最容易出错、也最难 debug 的一段。

> 📌 项目地址：https://github.com/lnkiai/m3e-canvas
> 在线试用：https://lnkiai.github.io/m3e-canvas/
> Prompt 生成逻辑（六段结构的硬证据）：https://github.com/lnkiai/m3e-canvas/blob/main/lib/prompt.ts

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

The hardest part of building an app with AI has never been getting it to write code — it is **describing the interface to it**. "Put this button bottom-right, tapping it opens the detail screen, going back slides in from the left" — three sentences in, it falls apart, and the AI is left guessing.

M3E Canvas replaces that step entirely: **you sketch the interface in the browser, it exports a structured spec, and you hand the spec to the AI.**

The repo was created on 2026-09-02 and hit 4,169 stars in four days.

> 📌 Repository: https://github.com/lnkiai/m3e-canvas
> Live demo, nothing to install: https://lnkiai.github.io/m3e-canvas/
> MIT ｜ Next.js 16 + React 19 ｜ no backend

---

## What it actually does

In one line: **it turns the full Material 3 Expressive component set into a drag-and-drop canvas, then translates everything on that canvas into a spec an AI can implement against.**

Three layers:

**Sketch.** Buttons, icon buttons, FABs, split buttons, FAB menus, chips, app bars, navigation bars, floating toolbars, tabs, search bars, cards, lists, dialogs, snackbars, text fields, dropdowns, switches, checkboxes, radio buttons, sliders, text, images, camera and map placeholders, badges, boxes and dividers — all drawn to Material 3 Expressive. Bring two buttons close and they magnetically fuse into a group, with the corners softening where they meet.

**Wire.** Give any tappable part, app bar icon or navigation destination a target screen (or "back") and a transition: slide from any of four sides, fade, expand or none. Arrows show the flow on the canvas; the preview lets you tap through it, and back plays the transition in reverse. Screens can also open one another on left/right/up/down swipes, with the screen following your finger in preview.

**Export.** This is the layer that matters.

---

## Why the gain is in the structure, not the drawing

I read its prompt-generation test (`lib/prompt.test.ts`), and that file is the hard evidence: the export is not a freeform description but a document with **six fixed sections in a locked order**.

In English the headings are:

```
## Colors
## Shape, type and motion
## Layout
## Behavior and navigation
## Component styles
## General guidance
```

An explicit platform line opens it: `Build it for Android, as a native app.` or `Build it for the web, as an app that runs in the browser.`

Four output languages are supported — Japanese, English, Chinese, Korean — down to per-language quoting conventions (`"Save"` in English, `「Save」` in Japanese, `“Save”` in Chinese).

**Why this matters**: the AI receives a sectioned spec, not "make me a notes app, and make the buttons look nice." You can check section by section what was omitted — by you or by the AI. Freeform description cannot do that: you do not know what you failed to say, and you cannot tell what the AI failed to build.

It also explicitly handles the two things that vanish first in prose: **overlap** and **side-by-side rows**. The README states plainly that the prompt describes both so the generated layout preserves them.

---

## How is this different from Figma-to-code, v0, or just pasting a screenshot?

This is the question that decides whether you need it.

| | Input | Output | Good for |
|---|---|---|---|
| **M3E Canvas** | Your sketched canvas | Six-section structured prompt (text) | You know what the UI looks like and want AI to build it, targeting Android/Web |
| **Figma → code** | A finished design file | Code or fragments | You already have professional design files; team workflows |
| **v0 and similar** | One sentence | Code and preview directly | You do not yet know what you want |
| **Screenshot to AI** | An image | Code | Copying an existing interface quickly |

The dividing line is clean: **M3E Canvas solves "I know what I want but cannot say it," not "I do not know what I want."** If you have not settled on the interface yet, the canvas just traps you in component-dragging; talking to the AI directly is faster.

The other boundary is the design system. Everything is built on Material 3 Expressive — seven color presets, or one seed color expanded into a full Material 3 scheme, light/dark, three contrast levels, dynamic color matching the phone wallpaper. Shape, type (Roboto, Roboto Flex, Roboto Serif, system) and motion (standard or expressive spring) sit on the same panel.

**The cost**: if you want something that does not look like Material Design, this will not help. The exported prompt is dense with M3 specifics, and the AI will follow them.

---

## It is also a clean example of "data never leaves the machine"

One README badge is easy to miss: `backend: none (localStorage)`.

The whole tool is front-end only. There is no server; what you sketch lives in your browser's localStorage. That cuts both ways:

- **Upside**: your product design is uploaded nowhere. When prototyping commercial work, that is not a small thing. The GitHub Pages build behaves identically to a local one, because no server is involved at all.
- **Cost**: no collaboration, no version history, gone if you switch browsers. Clear site data and the design is gone.

A textbook local-first trade: collaboration exchanged for privacy and zero dependencies. Anything you need to keep, export and save.

---

## When to use it, when not to

**Worth it**:
- You are building a native Android app and accept Material Design
- The interface has several screens with navigation between them — exactly where prose breaks down
- You already use Claude Code / Codex / Gemini CLI / Cursor and only lack a way to state the UI precisely

**Skip it**:
- The interface is one screen with two buttons — the canvas costs more than talking
- You want a non-Material aesthetic
- You need several people editing the design

---

## Gaps: what I have not verified

Stated plainly, per this site's rules:

1. **First-pass success rate is untested.** How close the exported prompt gets on the first Claude Code run, and how many rounds of rework follow, is a number I do not have. The README has a GIF of the full canvas-to-Android flow, but a demo is not your project.
2. **Web target quality is unproven.** The prompt supports Android and Web targets, but the whole component set is drawn to Material 3 Expressive. Which stack an AI picks to realize M3 components on the web, and how faithful it lands, is unverified.
3. **The project is very new.** Four days and 4,169 stars means heat, not stability. One maintainer, `v0`-stage, GitHub Sponsors already up — the maintenance cadence is not yet legible.

---

## In one line

M3E Canvas is worth installing, as long as you are clear about which step it replaces: **it does not design the interface for you and does not write the code; it turns "what the interface looks like" from spoken description into a spec you can check line by line.**

For anyone building apps with AI regularly, that step happens to be both the most error-prone and the hardest to debug.

> 📌 Repository: https://github.com/lnkiai/m3e-canvas
> Live demo: https://lnkiai.github.io/m3e-canvas/
> Prompt-building logic (the hard evidence for the six sections): https://github.com/lnkiai/m3e-canvas/blob/main/lib/prompt.ts

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
