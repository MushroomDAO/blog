---
title: "GSAP 官方 AI Skill 包：教会 40 个编码 Agent 正确写动画，Webflow 收购后全插件免费"
titleEn: "GSAP Official AI Skill Pack: Teaching 40+ Coding Agents to Write Animations Correctly, All Plugins Free After Webflow Acquisition"
description: "GreenSock 官方在 GitHub 发布 gsap-skills，一套专为 AI 编程助手设计的 Skill 集合，支持 Claude Code、Cursor、Copilot、Codex、Windsurf 等 40+ Agent 工具，覆盖核心 API、时间轴、ScrollTrigger、React 集成、性能优化八大模块。6.3k Star。Webflow 收购后所有付费插件免费开放。"
descriptionEn: "GreenSock officially released gsap-skills on GitHub — an Agent Skill collection for 40+ AI coding tools including Claude Code, Cursor, Copilot, Codex, and Windsurf. Covers core API, timelines, ScrollTrigger, React integration, and performance in 8 skill modules. 6.3k stars. All paid plugins now free after Webflow acquisition."
pubDate: "2026-05-31"
updatedDate: "2026-05-31"
category: "Tech-News"
tags: ["GSAP", "AI Agent", "Claude Code", "动画", "Skill", "前端开发", "ScrollTrigger", "Webflow", "开源"]
heroImage: "../../assets/images/gsap-skills-animation-banner.jpg"
---

AI 写动画代码一直有一个老问题：**它经常用错 GSAP**。

`gsap.set()` 的属性名写成 CSS 写法、ScrollTrigger 的 React 清理逻辑缺失、明明已经免费的插件还在输出"需要 Club GSAP 会员"的警告。这不是模型不聪明，是训练数据里 GSAP 相关代码质量参差不齐。

3 月，GreenSock 官方直接出手了。

> 📌 GitHub：https://github.com/greensock/gsap-skills  
> 安装：`npx skills add https://github.com/greensock/gsap-skills`  
> Claude Code：`claude plugin marketplace add greensock/gsap-skills`  
> Stars：6.3k | License：MIT

## 背景：Webflow 收购，付费插件全部免费

2024 年 10 月，Webflow 在年度大会上宣布收购 GreenSock。这个决定带来了一个直接后果：**原本需要付费 Club GSAP 会员才能使用的全部插件，收购后无条件免费开放**——SplitText、MorphSVG、ScrollSmoother、Flip、Draggable、DrawSVGPlugin……所有插件，包括商业用途，无需任何许可证。

这让 `gsap-skills` 的发布变得更迫切：现有的 AI 训练数据里，大量 GSAP 代码还在引用付费限制，模型不知道这些已经改变。一个官方 Skill 包能直接修正这个偏差。

## 它解决的核心问题

AI 生成 GSAP 代码时最常见的错误：

- 用 CSS 属性名而非 GSAP 的 camelCase（`background-color` vs `backgroundColor`）
- 不知道用 `autoAlpha` 代替 `opacity`（前者同步处理 `visibility`，避免 Flash of Invisible Content）
- ScrollTrigger 在 React 里忘记清理，导致组件卸载后动画继续运行
- 生成不存在的 API 或把旧版本 API 用在新版本上
- 还在提示"该插件需要 Club GSAP 会员"

`gsap-skills` 把这些"坑"和"正确做法"编码成 AI 可读的 Skill 格式，加载后直接注入上下文，让 Agent 在生成代码之前就知道正确答案。

## 8 个技能模块

| 模块 | 覆盖内容 |
|------|---------|
| **gsap-core** | `to/from/fromTo/set`、camelCase 属性规范、`autoAlpha`、`matchMedia` 响应式 |
| **gsap-timeline** | `timeline()` 创建、位置参数（`<` `>` 标签 偏移量）、`.defaults`、`.kill()` |
| **gsap-scrolltrigger** | `pin`、`scrub`、`toggleActions`、横向滚动、`ScrollTrigger.batch()` |
| **gsap-plugins** | 20+ 插件完整列表及用法（含已免费的 SplitText、MorphSVG 等） |
| **gsap-utils** | `clamp`、`mapRange`、`snap`、`quickTo` 工具函数 |
| **gsap-react** | `useGSAP()` hook、`scope` ref 选择器限定、`contextSafe()`、SSR 注意事项 |
| **gsap-performance** | transform/opacity 优先、`quickTo` 鼠标追随、避免 layout 属性动画 |
| **gsap-frameworks** | Vue 3 Composition API、Nuxt 懒加载 composable、Svelte 生命周期集成 |

每个模块是独立的 `SKILL.md` 文件，`skills/llms.txt` 做关键词路由——Agent 根据查询内容按需加载对应子技能，不是一次性把 8 个模块全部塞进上下文。

## 40+ Agent 工具一套安装

```bash
# 通用（任意支持 skills CLI 的 agent）
npx skills add https://github.com/greensock/gsap-skills

# Claude Code 专用
claude plugin marketplace add greensock/gsap-skills
```

仓库还为不同 Agent 提供了专用配置目录：`.claude-plugin/`、`.cursor-plugin/`、`.github/copilot-instructions.md`，以及专门的 `CLAUDE.md`（Claude Code）、`AGENTS.md`（通用）、`GEMINI.md`。前端开发者不需要关心这些细节，装完即用。

也提供了框架示例：`examples/` 目录下有 React（JSX + Vite）、Vue 3、Nuxt、Vanilla JS 四套完整示例代码。

## 为什么这个思路值得关注

`gsap-skills` 本质上是一个信号：**主流开源库开始主动为 AI 生态优化自己的"可被使用方式"**。

以前，开源库的维护者只需要写好 README 和文档站，等人类来读。现在，他们还需要考虑 AI Agent 会如何理解和使用这个库——训练数据里的错误代码、文档里的废弃 API、需要上下文才能理解的隐式规则，这些都会成为 AI 生成错误代码的来源。

一个 `SKILL.md` 文件，就是库维护者对 AI 时代用法规范的主动声明。GreenSock 是其中做得最系统的之一：官方发布、8 个模块分类、40+ Agent 适配、持续更新（最新版 3.15.0，2026 年 4 月发布）。

**6.3k Star，0 open issue**——说明前端社区对这个方向的认可程度相当高。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

AI writing GSAP animation code has had a persistent problem: **it often gets GSAP wrong**.

Wrong attribute naming conventions, missing ScrollTrigger cleanup in React, generating "requires Club GSAP membership" warnings for plugins that have been free since the Webflow acquisition. It's not that the models are unintelligent — the GSAP-related code in training data is inconsistent in quality.

In March 2026, GreenSock stepped in directly.

> 📌 GitHub: https://github.com/greensock/gsap-skills  
> Install: `npx skills add https://github.com/greensock/gsap-skills`  
> Claude Code: `claude plugin marketplace add greensock/gsap-skills`  
> Stars: 6.3k | License: MIT | Supported agents: Claude Code, Cursor, Copilot, Codex, Windsurf, Gemini

## Background: Webflow Acquisition, All Plugins Now Free

In October 2024, Webflow announced the acquisition of GreenSock at their annual conference. The immediate result: **all plugins previously behind a paid Club GSAP membership are now unconditionally free** — SplitText, MorphSVG, ScrollSmoother, Flip, Draggable, DrawSVGPlugin, and more. Commercial use, no license required.

This made releasing `gsap-skills` more urgent: most existing AI training data still references the paid restrictions. An official Skill pack can correct that bias at query time.

## What It Solves

The most common AI mistakes when generating GSAP code:

- CSS property names instead of GSAP's camelCase (`background-color` vs `backgroundColor`)
- Not using `autoAlpha` instead of `opacity` (the former handles `visibility` synchronously, preventing Flash of Invisible Content)
- Missing ScrollTrigger cleanup in React, leaving animations running after component unmount
- Hallucinating APIs or using v2 syntax in v3
- Still warning "this plugin requires Club GSAP membership"

`gsap-skills` encodes these pitfalls and correct patterns into an AI-readable Skill format. Once loaded, it injects directly into the Agent's context before code generation begins.

## 8 Skill Modules

| Module | Coverage |
|--------|----------|
| **gsap-core** | `to/from/fromTo/set`, camelCase conventions, `autoAlpha`, `matchMedia` responsive |
| **gsap-timeline** | `timeline()`, position parameters (`<` `>` labels offsets), `.defaults`, `.kill()` |
| **gsap-scrolltrigger** | `pin`, `scrub`, `toggleActions`, horizontal scroll, `ScrollTrigger.batch()` |
| **gsap-plugins** | 20+ plugins with usage (including newly free SplitText, MorphSVG, etc.) |
| **gsap-utils** | `clamp`, `mapRange`, `snap`, `quickTo` |
| **gsap-react** | `useGSAP()` hook, `scope` ref, `contextSafe()`, SSR notes |
| **gsap-performance** | Prioritize transform/opacity, `quickTo` for mouse-follow, avoid animating layout properties |
| **gsap-frameworks** | Vue 3 Composition API, Nuxt lazy-load composable, Svelte lifecycle integration |

A `skills/llms.txt` file handles keyword routing — agents load only the relevant sub-skill for a given query, not all 8 modules at once.

## Why This Pattern Matters

`gsap-skills` is a signal: **mainstream open-source libraries are starting to actively optimize how they're consumed by AI agents**.

Previously, library maintainers only needed to write good READMEs and docs sites — for humans. Now they also need to consider how AI agents will interpret and use their library. Incorrect code in training data, deprecated APIs in docs, implicit conventions that require context — all of these become sources of AI-generated bugs.

A `SKILL.md` file is a library maintainer's proactive declaration of correct usage for the AI era. GreenSock is among the most systematic: official release, 8 categorized modules, 40+ agent support, ongoing updates (latest v3.15.0, April 2026).

**6.3k stars, 0 open issues** — clear community validation for the direction.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
