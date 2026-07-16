---
title: "OpenCut：一周暴涨 7 万 Star，开源 CapCut 替代品的重构之路"
titleEn: "OpenCut: 70K Stars in a Week — Open-Source CapCut Alternative and Its Ground-Up Rewrite"
description: "OpenCut 是一个开源 CapCut 替代方案，一周内涨了 7 万 Star 成为 2025 年 7 月最热 GitHub 项目。文章解析它为什么爆火、正在发生什么重构、Rust 核心 + MCP Server 的新架构意味着什么。"
descriptionEn: "OpenCut is an open-source CapCut alternative that gained 70K GitHub stars in a week. This article analyzes why it went viral, what the ground-up rewrite involves, and what the new Rust core + MCP Server architecture means for video editing."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["开源", "视频编辑", "CapCut", "TypeScript", "Rust", "MCP", "GitHub"]
heroImage: "../../assets/images/opencut-open-source-capcut-banner.jpg"
---

> **GitHub**：[OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) · 73,000+ ⭐ · MIT  
> **官网**：https://opencut.app

---

## 一周 7 万 Star 背后

2025 年 7 月第二周，OpenCut 在 GitHub 单周新增超过 65,000 颗 Star，成为当周全球最热门的开源项目。这个量级在 GitHub 历史上屈指可数，和 ChatGPT 开放时的 openai-cookbook、Stable Diffusion 最初开源时属于同一量级的事件。

爆火的直接原因并不复杂：

**1. CapCut 被下架的时间窗口**  
2025 年初 TikTok/CapCut 在美国的下架风波让大量用户意识到，依赖一个随时可能消失的商业产品来做内容创作有多脆弱。"开源替代方案"的需求被明确激活。

**2. CapCut 功能日益付费化**  
CapCut 的基础功能（多轨道、绿幕、字幕模板）越来越多被锁在 Pro 订阅后面。用户对"我之前免费用的东西现在要付费"这种体验积累了不满。

**3. AI 视频创作浪潮**  
2025 年 AI 视频工具（Runway、Kling、Hailuo）进入主流，大量内容创作者需要快速剪辑 AI 生成片段。一个可以自托管、可以集成 AI 工作流的编辑器需求真实存在。

---

## OpenCut 现在是什么

OpenCut 分为两个阶段：

### 经典版（已归档）

`opencut-app/opencut-classic` 是最初那个爆火的版本，已归档停止维护。它是一个 Next.js + Typescript 的网页视频编辑器，功能完整——多轨道时间线、剪辑、字幕、滤镜、导出 MP4——可以自托管，没有用量限制，没有水印，没有账号要求。

这个版本验证了一件事：**用户确实需要一个浏览器里能跑的、不需要安装的视频编辑器，而且不想花钱。**

### 重写版（进行中）

`opencut-app/opencut`（当前主仓库）是正在进行的完全重写。重写目标不是功能对齐，而是**架构重设计**：

```
opencut/
├── apps/web/         # Next.js 前端（继续存在）
├── apps/desktop/     # GPUI 原生桌面端（进行中）
├── rust/             # 跨平台核心：GPU 合成、特效、遮罩、WASM 绑定
└── docs/             # 架构文档
```

重写的核心思路：**把业务逻辑从 TypeScript 迁移到 Rust**，让核心可以在 Web（WASM）、桌面（原生）和移动端共享同一套渲染和合成代码。

---

## 重写带来的三个能力

### 1. Editor API

重写版暴露一个正式的 Editor API，允许外部调用视频编辑操作。这意味着：
- 可以用脚本批量处理视频
- 可以让 AI 直接操作编辑器（而不是靠 UI 点击）
- 第三方工具可以集成 OpenCut 的编辑能力

### 2. MCP Server

这是对 AI 工具链最友好的部分：OpenCut 计划内置一个 MCP（Model Context Protocol）服务器。

有了 MCP server，Claude Code、Cursor、任何支持 MCP 的 AI 工具都可以直接调用 OpenCut 的剪辑能力：

```
"把这段视频从 00:30 剪到 02:15，加上字幕，导出 1080p"
→ Claude Code → MCP → OpenCut Editor API → output.mp4
```

### 3. 插件系统

重写版采用 plugin-first 架构，核心功能（特效、转场、字幕样式）都是插件，用户和社区可以扩展。

---

## 技术栈现状

| 层 | 当前技术 | 说明 |
|---|---|---|
| 前端 | Next.js + Bun | 网页编辑器界面 |
| 桌面端 | GPUI (Rust) | Zed 编辑器同款 UI 框架 |
| 核心 | Rust + WASM | GPU 合成、特效、遮罩 |
| 构建 | Bun | 比 npm/pnpm 快 |
| 赞助方 | Vercel + fal.ai | 托管 + AI 能力 |

fal.ai 的赞助很有意思——fal 是 AI 图像/视频生成 API 平台，赞助一个视频编辑器意味着未来可能有深度的 AI 生成集成。

---

## 和 CapCut 的差距

坦白说，**重写版目前还没达到经典版的功能完整度**。这是一个正在建设中的项目，不是一个可以直接替代 CapCut 的成品。

实际差距：
- CapCut 的 AI 功能（一键字幕、背景移除、数字人）目前 OpenCut 没有
- 移动端 CapCut 的体验明显优于桌面浏览器的 OpenCut
- CapCut 有大量精品模板，OpenCut 基本没有

**但 OpenCut 做到了 CapCut 做不到的事：**
- 完全自托管，数据不出本地
- 开源，可以 fork 改造
- 正在构建 MCP + Editor API，可以接 AI 工作流
- 没有用量限制，没有水印，没有订阅

---

## 本地跑起来

经典版（功能最完整）：

```bash
git clone https://github.com/OpenCut-app/opencut-classic.git
cd opencut-classic
bun install
bun dev
# 访问 http://localhost:3000
```

重写版（尝鲜）：

```bash
git clone https://github.com/OpenCut-app/OpenCut.git
cd OpenCut
cp apps/web/.env.example apps/web/.env.local
# 启动数据库（可选）：
docker compose up -d
# 启动前端：
bun install && bun dev
```

---

## 为什么值得关注

OpenCut 这次的爆火本质上是**一个时机问题**：CapCut 的不确定性 + 开源社区的基础设施成熟 + AI 视频创作的爆发，三个因素在同一时间点撞上了。

更有意思的是重写版的架构方向：Rust 核心 + Editor API + MCP Server = **一个可以被 AI 工具调用的视频编辑引擎**。这不是在和 CapCut 竞争剪辑 UI，而是在构建一个 AI 视频工作流的基础设施层。

如果你是 AI 视频工作流的开发者，值得跟着这个项目的 MCP Server 进展。

© 2026 Author: Mycelium Protocol

<!--EN-->

## OpenCut: 70K Stars in a Week — Open-Source CapCut Alternative and Its Ground-Up Rewrite

**GitHub**: [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) · 73,000+ ⭐ · MIT  
**Website**: https://opencut.app

### Why It Went Viral

OpenCut gained over 65,000 GitHub stars in a single week in July 2025 — one of the fastest star accumulation events in GitHub history. Three factors converged:

1. **CapCut's availability scare**: The TikTok/CapCut US ban scare made creators realize the risk of depending on a commercial tool that can vanish overnight.
2. **CapCut's expanding paywalls**: Core features (multi-track, green screen, subtitle templates) have been progressively moving behind Pro subscriptions.
3. **AI video creation surge**: Runway, Kling, and similar tools created demand for a fast editor that can integrate with AI generation workflows — ideally self-hosted and scriptable.

### Two Phases

**Classic version** (`opencut-app/opencut-classic`) — now archived. A working Next.js + TypeScript browser-based video editor: multi-track timeline, cuts, subtitles, filters, MP4 export. Self-hostable, no watermark, no account required. Proved the demand was real.

**Rewrite** (`opencut-app/opencut`) — the current active repo, a ground-up rebuild with a different architecture:

```
opencut/
├── apps/web/         # Next.js frontend
├── apps/desktop/     # GPUI native desktop (in progress)
├── rust/             # Cross-platform core: GPU compositing, effects, masks, WASM bindings
└── docs/             # Architecture docs
```

The rewrite migrates core logic to Rust — enabling the same rendering engine to run on web (WASM), desktop (native), and eventually mobile.

### Three New Capabilities

**Editor API**: External tools can call video editing operations programmatically — enables batch processing and AI-driven editing.

**MCP Server**: OpenCut will expose an MCP (Model Context Protocol) server, meaning Claude Code, Cursor, or any MCP-compatible AI tool can call OpenCut's editing functions directly:
```
"Clip this video from 00:30 to 02:15, add captions, export 1080p"
→ Claude Code → MCP → OpenCut Editor API → output.mp4
```

**Plugin system**: Plugin-first architecture — effects, transitions, and caption styles are all plugins; community-extendable.

### Honest Gap vs. CapCut

The rewrite isn't a CapCut replacement yet. CapCut's AI features (auto-captions, background removal, avatars), mobile experience, and template library are all ahead of OpenCut's current state.

What OpenCut does that CapCut can't: fully self-hosted, open-source, no usage limits, no watermark, no subscription — and the MCP + Editor API architecture enables AI workflow integration that CapCut will never expose.

### Quick Start (Classic Version)

```bash
git clone https://github.com/OpenCut-app/opencut-classic.git
cd opencut-classic && bun install && bun dev
# Open http://localhost:3000
```

### Bottom Line

OpenCut's virality was timing. Its long-term relevance is the rewrite: a Rust-core, MCP-server, plugin-first video editing engine that AI tools can script directly. Worth watching for AI video workflow developers.

© 2026 Author: Mycelium Protocol
