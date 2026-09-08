---
title: "Nikola：把话题变成手绘讲解视频的 Codex Skill"
titleEn: "Nikola: A Codex Skill That Turns Any Topic Into Hand-drawn Explainer Videos"
description: "中文手绘知识讲解视频 Codex Skill，逐笔故事动画与程序动画双路径，VolcanoEngine TTS 配音，输出真实 MP4+字幕+时间轴，无需本地模型，Apache 2.0 开源。"
descriptionEn: "A Codex skill for Chinese-language hand-drawn explainer videos — stroke-by-stroke narrative and procedural animation paths, VolcanoEngine TTS voiceover, outputs real MP4s with subtitles and editable timelines, no local models required."
pubDate: "2026-09-08"
updatedDate: "2026-09-08"
category: "Tech-News"
tags: ["手绘动画", "Codex Skill", "AI视频", "知识讲解", "开源", "TTS"]
heroImage: "../../assets/images/nikola-hand-drawn-explainer-video-codex-skill-banner.jpg"
---

> 📌 项目地址：https://github.com/hi-nikola/hand-drawn-explainer-video-nikola

**如果你想让 AI 帮你做一段"老师在黑板上边讲边画"的视频，这个项目可能正是你要找的东西。**

`hand-drawn-explainer-video-nikola` 是一个 **Codex Skill**，把话题、脚本或字幕文件（SRT）转成真实可用的手绘讲解动画 MP4，附带字幕、时间轴和可编辑素材。目前已有 134 Stars，Apache 2.0 开源。

## 两条生产路径

Nikola 区分了两种完全不同的动画类型，而不是用一套方案搞定所有场景。

### 路径一：逐笔故事动画

这是"真正的手绘"——每一笔按顺序画出来，而不是静态手绘图片的平移。支持三种场景结构：

- **单场景**：一个连续画面讲完一个知识点
- **多幕故事**：多个场景串联，有起承转合
- **双语义岛**：屏幕左右各一个主题，同步推进对比

视觉风格上可以选：**奇怪小黑**（白底极简线稿）、**Q 版人物**（chibi 角色）、或自定义手绘风格。

### 路径二：程序动画

用 HTML/SVG/GSAP 生成，适合需要精确排版的内容：流程图、关系图、知识卡片、文字动效。当内容是"讲原理"而不是"讲故事"时，程序动画往往比手绘更清晰。

## 技术架构

| 组件 | 说明 |
|------|------|
| Python 3.10+ | 主控流程 |
| FFmpeg/FFprobe | MP4 合成与音视频处理 |
| Node.js + 浏览器 | 程序动画渲染 |
| HyperFrames | 多轨合成 |
| VolcanoEngine LiuFei TTS | 默认配音（`zh_male_liufei_uranus_bigtts`，Seed TTS 2.0） |

**无需本地模型**运行笔触渲染。图像生成和语音合成依赖外部服务，但不在仓库内存储任何 API Key。

项目明确拒绝"系统级低质量 TTS"，默认用火山引擎的流畅男声，这一点在同类项目里比较少见——大多数开源视频生成工具在配音上凑合，Nikola 把它当成一等公民。

## 触发词示例

作为 Codex Skill，通过自然语言触发：

- `边讲边画，讲一下量子纠缠` → 逐笔叙事风格
- `先画左边介绍牛顿，再画右边介绍爱因斯坦` → 双语义岛
- `小黑、怪诞风格，白底，画一个关于 TCP/IP 的短视频` → 奇怪小黑风格
- `做一个流程卡片，展示用户注册流程` → 程序动画

## 已有示例

README 中展示了三个实际产出：

**《约法三章》** — 38.5 秒，16:9，七幕连续场景，展示多幕故事结构
**Steve Jobs 传记** — 57 秒，Q 版人物 + 双语义岛结合
**"What is Skill"** — 14 秒，纯程序动画，流程卡片 + 角色动效

## 为什么值得关注

知识讲解视频的需求一直存在，但生产成本极高——脚本、配音、动画三个环节都需要专业人力。Nikola 的思路是把整条链路交给 Codex Skill 自动化，从一句话输入到可用 MP4 全程不出 agent。

两条路径的区分（故事 vs. 程序）说明作者对场景做了认真思考：不是"万能魔法棒"，而是根据内容类型选对工具。这种克制反而让它更可靠。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/hi-nikola/hand-drawn-explainer-video-nikola

**Nikola is a Codex skill that converts topics, scripts, or SRT files into authentic hand-drawn explainer MP4 videos — subtitles, timelines, and editable assets included.**

134 Stars, Apache 2.0, active since September 2026.

## Two Production Paths

### Stroke-by-Stroke Narrative

Real sequential drawing — each stroke appears in order, not a panned static image. Three scene structures: single scene, multi-act story, and dual semantic islands (two topics drawn side-by-side simultaneously). Visual styles include xiaohei minimalism (white background, clean line art), chibi characters, or custom hand-drawn.

### Procedural Animation

HTML/SVG/GSAP rendering for content requiring precise layout: flowcharts, relationship diagrams, knowledge cards, text animation. Best when the content explains a process rather than tells a story.

## Tech Stack

Python 3.10+, FFmpeg, Node.js + browser renderer, HyperFrames compositing, and VolcanoEngine LiuFei TTS (`zh_male_liufei_uranus_bigtts`, Seed TTS 2.0) for voiceover. No local models required for stroke rendering.

## Why It Matters

Explainer video production is expensive: script, voiceover, and animation each require specialist work. Nikola automates the full pipeline inside a Codex skill — one natural-language prompt to a usable MP4. The two-path design (narrative vs. procedural) shows real thought about when each approach fits, rather than a one-size-fits-all magic wand.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
