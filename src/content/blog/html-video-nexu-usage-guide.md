---
title: "html-video：丢一个链接，本地生成 MP4，全程不碰剪辑软件"
titleEn: "html-video: Paste a Link, Get an MP4 — No Video Editor Needed"
description: "nexu-io/html-video 是一个本地视频生成工具，3744 Stars，Apache-2.0。丢入文章链接或 GitHub 仓库，AI 自动拆场景、套模板、渲染成 MP4。21 套商用 License 清理过的模板，底层用 HeyGen 开源的 HyperFrames 引擎，支持 Claude Code、Cursor、Codex 等 14 个 AI Agent。普通人快速上手指南。"
descriptionEn: "nexu-io/html-video (3.7k★, Apache-2.0) turns a URL or GitHub repo into a real MP4 — locally, no cloud fees, no video editor. AI agent fetches the content, builds a multi-scene storyboard, applies one of 21 license-clean templates, renders via HyperFrames + headless Chromium + ffmpeg. Supports 14 coding agents including Claude Code, Cursor, and Codex. Quick-start guide for non-technical users."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-News"
tags: ["视频生成", "html-video", "HyperFrames", "本地AI", "开源工具", "MP4", "Claude Code", "内容创作"]
heroImage: "../../assets/images/html-video-nexu-usage-guide-banner.jpg"
---

> **GitHub**: [nexu-io/html-video](https://github.com/nexu-io/html-video) · **3,744 Stars** · **Apache-2.0**  
> **底层引擎**: [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) · 25,000 Stars

---

## 它在解决什么问题

做内容的人都会遇到这个困境：想给项目、文章、或产品做一条介绍视频，但：

- 专业剪辑软件学习成本太高
- 调 AI 视频 API 贵且输出不稳定
- 每次生成结果不一样，调整没有抓手

html-video 的思路很直接：**HTML 文件就是视频，写完渲染成 MP4，同一个 HTML 永远出同一个视频**。

你不需要学剪辑。你需要的是：丢一个链接，让 AI 帮你把内容变成视频。

---

## 核心概念：两行话说清楚

**HyperFrames**（HeyGen 开源，25K Stars）：把 HTML+CSS+动画渲染成 MP4 的底层引擎——Headless Chromium 逐帧录制，ffmpeg 编码输出。

**html-video**：在 HyperFrames 上加了一层「智能层」——你不需要写 HTML，AI Agent 读你的内容、选模板、写每个场景的 HTML，然后调 HyperFrames 渲染。

```
你丢的内容（链接/文章/仓库/提示词）
        ↓
① 抓取内容（服务器端拉取，支持微信公众号文章）
        ↓
② AI Agent 分析内容，拆分场景，写多帧 HTML
        ↓
③ HyperFrames：Headless Chromium 录制动画 → ffmpeg 编码
        ↓
      你的 MP4
```

全程在本地跑，没有云端上传，没有按次收费。

---

## 快速上手（3 条命令）

### 前置环境

| 需要 | 版本 | 检查方式 |
|---|---|---|
| Node.js | 20+ | `node --version` |
| pnpm | 9+ | `pnpm --version` |
| ffmpeg | 任意近期版本 | `ffmpeg -version` |
| Chromium（Playwright）| — | `npx playwright install chromium` |

> macOS 用户可以用 Homebrew：`brew install ffmpeg node`，然后 `npm install -g pnpm`

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/nexu-io/html-video
cd html-video

# 2. 安装依赖 + 编译
pnpm install
pnpm -r build

# 3. 安装 Playwright 的 Chromium（用于渲染）
npx playwright install chromium
```

### 启动 Studio

```bash
node packages/cli/dist/bin.js studio
# → 浏览器自动打开 http://127.0.0.1:3071
```

Studio 是一个本地浏览器界面，打开就能用。

---

## 三种使用方式

### 方式一：丢一个链接（最常用）

在 Studio 的对话框里直接发：

```
做一个解读视频  https://github.com/nexu-io/html-video
```

或者中文文章链接：

```
帮我把这篇文章做成介绍视频  https://mp.weixin.qq.com/s/...
```

Studio 服务端会抓取内容（支持微信公众号文章，不需要你手动复制文章），AI 读完内容后自动拆场景、选模板、生成多帧动画视频。

**实际效果（作者试用 GitHub 仓库链接）**：
- AI 读取了 README 和仓库结构
- 自动拆成 4 个场景：项目概述 → 核心特性 → 使用示例 → 总结
- 每个场景套不同模板
- 输出一条完整的项目介绍 MP4

不算惊艳，但比从零剪省了大量时间。

### 方式二：从头描述一个视频

```
帮我做一个 30 秒的产品介绍视频，主题是：一个帮助独立开发者管理 SSH 连接的工具
```

AI 会从零写内容，选模板，渲染输出。适合自己描述创意但不想写脚本的场景。

### 方式三：选模板手动编辑

在 Studio 的模板画廊里选一个，直接改文字、调数据，然后导出。适合想精确控制内容的场景。

---

## 21 套模板，分类浏览

所有模板均已清理版权，商用无顾虑（每个模板都有 SPDX license 标注和 `commercial_use: true` 标记）。

| 分类 | 代表模板 | 适合场景 |
|---|---|---|
| **数据可视化** | frame-data-chart-nyt | 指标趋势、数字增长故事 |
| **标题/VFX** | frame-glitch-title | 开场、宣传片头 |
| **Hero 展示** | frame-liquid-bg-hero | 产品发布、大标题展示 |
| **电影风格** | frame-light-leak-cinema | 品牌宣传片、情绪片段 |
| **代码/终端风** | vfx-text-cursor | 开源项目介绍、CLI demo |
| **结尾** | frame-logo-outro | 品牌署名、视频结尾 |
| **产品宣传** | 多场景模板 | 15s/30s 标准产品视频 |
| **解说/图表** | 决策树模板 | 流程解释、教程视频 |

查看所有 21 套：Studio 启动后在左侧画廊里实时预览。

---

## AI Agent 支持哪些？

html-video 自动检测你电脑上装了什么 CLI：

| 你装了这个 | 会被自动用上 |
|---|---|
| Claude Code (`claude`) | ✅ 自动检测 |
| Codex CLI (`codex`) | ✅ 自动检测 |
| Cursor Agent | ✅ 自动检测 |
| Gemini CLI (`gemini`) | ✅ 自动检测 |
| Aider | ✅ 自动检测 |
| 没装任何 CLI | ✅ 用 Anthropic API（填 key 即可）|

没有任何 CLI？在 Studio 的 Settings 里填一个 Anthropic API Key，就能通过官方 API 驱动。

---

## 可选：给视频加配音和背景音乐

在 **Settings → Audio** 里填 MiniMax API Key，然后在项目的 **Soundtrack** 面板里：

- **背景音乐**：描述一个情绪（`calm cinematic ambient`），MiniMax 生成纯音乐
- **旁白**：输入解说词，MiniMax TTS 朗读

两个音轨会自动混入最终 MP4（音乐会在有旁白时自动降低音量）。不配置这个的话，其他功能照常使用。

---

## 几个 CLI 工具命令

```bash
# 检测哪些 Agent 和渲染引擎可用
node packages/cli/dist/bin.js doctor

# 根据你的意图搜索合适的模板
node packages/cli/dist/bin.js search-templates --intent "github stars race" --top 3
```

`doctor` 命令很实用，特别是第一次启动如果遇到问题，先跑一下确认环境。

---

## 现在能做什么，还不能做什么

**现在能做的**：
- 丢链接 → 自动生成多场景介绍视频
- 21 套模板，商用可用
- 本地渲染，不上云
- 支持微信公众号文章直接抓取
- 可选配音（MiniMax）

**还在计划中**（架构已预留，还没实现）：
- Remotion（React 组件驱动）引擎
- Motion Canvas / Revideo（更适合解说视频）
- Manim（数学/3D 动画）

**效果说明**：适合标准化内容（项目介绍、产品展示、文章解读），不适合需要精细创意控制的专业视频。它的核心价值是**速度**，不是极致质量。

---

## 和它相关的两个仓库

- **html-video**: [github.com/nexu-io/html-video](https://github.com/nexu-io/html-video) — 本文介绍的工具（3.7K★）
- **HyperFrames**: [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) — 底层渲染引擎（25K★），HeyGen 开源
- **Open Design**: [github.com/nexu-io/open-design](https://github.com/nexu-io/open-design) — 同团队的设计工具，html-video 是它的视频版本

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: html-video (nexu-io/html-video, 3.7k★, Apache-2.0) turns a URL, GitHub repo, or plain prompt into a locally-rendered MP4 — no cloud, no per-render fees, no video editor. Paste a link in the browser studio, an AI agent fetches the content, builds a multi-scene storyboard, applies one of 21 license-clean templates, and renders via HyperFrames (HeyGen's open-source HTML→video engine). Supports 14 AI agents including Claude Code, Codex, and Gemini CLI.

---

## What It Does

Paste any article URL, GitHub repo, or plain description → the local Studio fetches the content (WeChat 公众号 articles work out of the box), an AI agent builds a multi-scene storyboard, applies a template, and outputs a real MP4. The render pipeline: headless Chromium records each animated HTML frame, ffmpeg encodes to libx264. Everything runs locally.

## Quick Start (3 Commands)

**Prerequisites**: Node.js 20+, pnpm 9+, ffmpeg, Chromium (via Playwright).

```bash
git clone https://github.com/nexu-io/html-video && cd html-video
pnpm install && pnpm -r build
npx playwright install chromium
node packages/cli/dist/bin.js studio   # opens at http://127.0.0.1:3071
```

In the Studio: paste a link or describe a video in the chat box, let the agent generate frames, preview in the gallery, and export MP4.

## Three Ways to Use It

1. **Paste a link** (most common): Drop a GitHub repo URL or article link. The studio fetches content server-side (no copy-pasting), the agent builds the storyboard from actual content.

2. **Describe from scratch**: "Make a 30-second product intro for an SSH management tool." Agent writes content + storyboard from your description.

3. **Manual template editing**: Pick a template in the gallery, edit text/data directly, export.

## 21 Templates, All License-Clean

Categories: data viz (NYT-style charts, Swiss/Vignelli grids), titles & VFX (glitch, kinetic type, typewriter cursor), heroes & cinematics (liquid gradients, light-leak, warm grain), product promos (15s/30s multi-scene), explainer scaffolds. All carry SPDX license IDs with `commercial_use: true` — usable in commercial work without an audit.

## AI Agent Support

Auto-detected from your PATH: Claude Code, Codex CLI, Cursor Agent, Gemini CLI, Aider, Grok, Qwen, OpenCode, GitHub Copilot CLI, and more (14 total). No CLI installed? Set an Anthropic API key in Settings and it talks directly to the Messages API.

## What Works Today vs. What's Planned

**Working**: HyperFrames engine (HTML → real MP4 via headless Chromium + ffmpeg), 21 templates, 14 agent backends, local Studio + CLI, WeChat article fetching, optional MiniMax soundtrack.

**Planned**: Remotion (React components), Motion Canvas/Revideo, Manim — the adapter interface is built, the engines aren't wired yet.

**Honest assessment**: Output quality won't replace professional editing. The value is speed — standardized content like project intros and product demos that would otherwise require a full editing workflow.

**Links**: [GitHub](https://github.com/nexu-io/html-video) · [HyperFrames](https://github.com/heygen-com/hyperframes) · [Open Design](https://github.com/nexu-io/open-design)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
