---
title: "OhMyGame：一人工作室，从设计文档到发布全靠 AI Agent"
titleEn: "OhMyGame: From Design Doc to Published Game — All with AI Agents"
description: "WhiteTowerAI 开源 OhMyGame（Apache-2.0，457 stars，Beta）：本地优先的 AI 游戏开发全流程工作台，Electron App，内置 Pi Coding Agent 支持 40+ LLM 供应商（BYOK 或 ChatGPT Plus/GitHub Copilot 登录），Canvas 节点图管理设计文档/图片/视频/3D 模型，覆盖 Web 游戏（Three.js/R3F/Phaser）、交互故事/视觉小说、通用游戏（含 Godot 插件），图片/视频生成走 OpenAI/OpenRouter/火山引擎，3D 建模/绑骨/动画走 Meshy，一键构建发布到可分享浏览器链接，项目文件和密钥全留本地，发布功能需注册账号。"
descriptionEn: "WhiteTowerAI open-sourced OhMyGame (Apache-2.0, 457 stars, Beta): a local-first AI game development workstation in an Electron app. Built-in Pi Coding Agent supports 40+ LLM providers via BYOK or ChatGPT Plus/GitHub Copilot login. Canvas node graph manages design docs, images, videos, and 3D models. Covers web games (Three.js/R3F/Phaser), interactive stories/visual novels, and general games (with Godot plugin). Image/video generation via OpenAI/OpenRouter/Volcengine Ark; 3D modeling/rigging/animation via Meshy. One-click build publishes to a shareable browser link. All project files and keys stay local; account needed to publish."
pubDate: 2026-10-10
heroImage: "../../assets/images/ohmygame-whitetower-ai-one-person-game-studio-banner.jpg"
category: "Tech-Experiment"
tags: ["游戏开发", "AI Agent", "Electron", "开源工具", "本地优先"]
lang: "zh-CN"
wechatTitle: "OhMyGame：一人开发工作台，AI全包游戏开发"
wechatDigest: "Apache-2.0 457星；Pi Agent BYOK 40+供应商；Canvas+3D；一键发布"
---

独立游戏开发者的问题不是缺少工具，而是工具太多——引擎、美术、代码、音效、发布，每个环节都是一个独立领域。OhMyGame 想把这条链条压缩进一个本地 Electron App，用 AI Agent 把通常需要整个工作室的事情让一个人做完。

GitHub: https://github.com/WhiteTowerAI/ohmygame

Apache-2.0（名称和 Logo 除外），457 stars，Beta 阶段（v0.0.0-beta.4.3），2026 年 8 月开始开发，两个月 771 commits，目前仍在快速迭代。

---

## 它是什么：游戏制作工作台，不是游戏引擎

OhMyGame **不替代 Unity 或 Godot 的底层物理/渲染能力**，定位是更高一层：把「从零想法到可分享游戏」的整个流程压缩到一个人能独立完成。

核心是一个 **AI Agent 驱动的 Canvas 工作台**：设计文档、图片、视频、3D 模型并排摆在节点图上，节点之间可以互相引用，所有生成物进同一个资产库，Agent 在整个流程里负责起草、生成、写代码、预览。

---

## 支持三类游戏

| 类型 | 技术栈 |
|------|--------|
| **Web 游戏** | Three.js / React Three Fiber / Phaser |
| **交互故事 / 视觉小说** | 内置支持 |
| **通用游戏** | 含 Godot 插件，支持 WebGL 实时预览 |

---

## Agent 层：Pi Coding Agent + BYOK

代码 Agent 核心是 **Pi Coding Agent**（`@earendil-works/pi-coding-agent`），通过 MCP 协议与 App 集成，有持久化 Session 和 GUI。

**语言模型完全 BYOK（Bring Your Own Key）**，支持 40+ 供应商：

- Anthropic（Claude）
- OpenAI / Google / DeepSeek / Qwen / Kimi / GLM / MiniMax / xAI / Mistral / Groq
- OpenRouter / Amazon Bedrock / Vercel AI Gateway
- 也可以直接用 **ChatGPT Plus/Pro** 或 **GitHub Copilot** 订阅登录，免填 API Key

**媒体生成（图片/视频）：** OpenAI、OpenRouter、火山引擎 Ark（BytePlus ModelArk）

**3D 建模/绑骨/动画：** Meshy

---

## Canvas：节点图管理资产

Canvas 是核心工作界面，节点类型包括：
- 设计文档（GDD）
- 图片 / 视频 / 3D 模型
- AI 表格编辑 + CSV 导入导出（2026-10-10 新增）
- 节点可调节大小，互相引用，生成物进统一资产库

Agent 在 Canvas 上直接操作：读取设计文档→生成资产→写代码→跑 WebGL 实时预览，整个流程不需要切出 App。

---

## 一个 Agent 做了哪些角色

| 传统角色 | Agent 替代方式 |
|---------|--------------|
| 游戏设计师 | 起草 GDD（游戏设计文档） |
| 美术 | 调用图片/视频/3D 生成 API |
| 程序员 | Pi Coding Agent 写游戏代码 + WebGL 实时预览 |
| QA | 自动 Playtest（运行游戏并输出测试报告，roadmap 中） |
| 发布/运营 | 一键构建 + 发布到公开 URL |

---

## 安装与使用

**下载预编译包（推荐）：**
- macOS（Apple Silicon）
- Windows x64（暂未代码签名）
- 从 GitHub Releases 或官网 ohmygame.ai 下载

**源码构建：**

```bash
git clone https://github.com/WhiteTowerAI/ohmygame.git
cd ohmygame
bun install --frozen-lockfile
bun run dev          # web renderer + 后台守护进程
bun run dev:desktop  # 完整 Electron App
```

环境要求：Bun 1.4.2+，Node.js ≥ 22.19.0

初次使用先在 Settings 里接入语言模型 Provider，媒体 Provider 可选配。

---

## 发布机制

构建完成后生成一个**可分享的浏览器链接**——不需要对方安装任何东西，直接打开就能玩。更新后同一个链接继续有效。发布到内置社区广场后，其他用户可以浏览和 Remix。

发布功能需要注册账号；**项目文件和所有密钥完全留在本地**。

---

## Tech Stack 一览

| 层 | 技术 |
|----|------|
| 桌面壳 | Electron 43 + electron-builder + electron-updater |
| 前端 | React 19 + Vite 7 + @xyflow/react（节点图）|
| 3D/资产 | Three.js + glTF Transform + @google/model-viewer |
| 后台 | Fastify 5（本地守护进程） |
| 云服务 | Supabase（账号/发布）、PostHog（匿名统计）、Sentry（崩溃上报）|
| Agent | @earendil-works/pi-coding-agent + pi-mcp-adapter（MCP 协议）|

---

## 已知边界

- **Beta 阶段**，v0.0.0-beta.4.3，粗糙感存在，API 随时可能变
- **不替代游戏引擎**——深度物理/渲染仍需 Unity/Godot
- **自动 Playtest 仍在 Roadmap** 中，未正式落地
- **Windows 包未代码签名**，需手动信任
- 457 stars，两个月新项目，生产稳定性待观察
- License 名称和 Logo 不在 Apache-2.0 范围内

---

## 一句话说清楚

OhMyGame 是一个本地优先的 AI 游戏制作全流程工作台：Canvas 节点图管理所有游戏资产，Pi Coding Agent 写代码和运行预览，BYOK 支持 40+ LLM 供应商，图片/视频/3D 生成接主流 API，一键构建发布到浏览器链接。一个人的游戏工作室，不换引擎，加一层 AI 流程。

---

> Apache-2.0（名称/Logo 除外）。WhiteTowerAI，Beta v0.0.0-beta.4.3，457 stars。开源仅供学习参考，Beta 阶段 API 随时变动。

---

<!--EN-->

## OhMyGame: From Design Doc to Published Game — All with AI Agents

Independent game developers don't suffer from a lack of tools — they suffer from too many separate ones: engine, art, code, audio, publishing. OhMyGame tries to compress that entire chain into one local Electron app, letting a single person use AI agents to do what normally takes a whole studio.

GitHub: https://github.com/WhiteTowerAI/ohmygame

Apache-2.0 (name and logo excluded), 457 stars, Beta (v0.0.0-beta.4.3). Development started August 2026; 771 commits in two months, still in fast iteration.

---

### What It Is: A Game Making Workstation, Not a Game Engine

OhMyGame does **not replace Unity or Godot's physics/rendering depth** — it sits one layer higher. The goal is to compress "zero idea → shareable game" into something one person can complete alone.

The core is an **AI Agent-driven Canvas workstation**: design docs, images, videos, and 3D models sit side by side on a node graph; nodes can reference each other; all generated assets go into a shared asset library; the Agent handles drafting, generation, coding, and real-time preview across the entire flow.

---

### Three Game Types

| Type | Stack |
|------|-------|
| **Web games** | Three.js / React Three Fiber / Phaser |
| **Interactive stories / visual novels** | Built-in support |
| **General games** | Godot plugin + optional WebGL live preview |

---

### The Agent Layer: Pi Coding Agent + BYOK

The coding Agent core is **Pi Coding Agent** (`@earendil-works/pi-coding-agent`), integrated via MCP protocol with persistent sessions and a GUI.

**Language models are fully BYOK**, supporting 40+ providers:

- Anthropic, OpenAI, Google, DeepSeek, Qwen, Kimi, GLM, MiniMax, xAI, Mistral, Groq
- OpenRouter, Amazon Bedrock, Vercel AI Gateway
- Can also log in directly with **ChatGPT Plus/Pro** or **GitHub Copilot** subscription — no API key required

**Media generation (image/video):** OpenAI, OpenRouter, Volcengine Ark (BytePlus ModelArk)

**3D modeling/rigging/animation:** Meshy

---

### Canvas: Node Graph for Asset Management

Canvas is the primary workspace. Node types include: design documents (GDD), images, videos, 3D models, AI table editing + CSV import/export (added 2026-10-10). Nodes can reference each other; generated outputs go into a unified asset library.

The Agent works directly on Canvas: reads design docs → generates assets → writes code → runs WebGL live preview, all without leaving the app.

---

### One Agent, Multiple Studio Roles

| Traditional role | Agent replacement |
|-----------------|------------------|
| Game designer | Drafts GDD (game design document) |
| Artist | Calls image/video/3D generation APIs |
| Programmer | Pi Coding Agent writes game code + runs WebGL preview |
| QA | Automated Playtest (run game + output test report, on roadmap) |
| Publisher | One-click build + publish to public URL |

---

### Installation

**Pre-built packages (recommended):**
- macOS (Apple Silicon)
- Windows x64 (not yet code-signed)
- Download from GitHub Releases or ohmygame.ai

**Build from source:**

```bash
git clone https://github.com/WhiteTowerAI/ohmygame.git
cd ohmygame
bun install --frozen-lockfile
bun run dev          # web renderer + daemon
bun run dev:desktop  # full Electron app
```

Requirements: Bun 1.4.2+, Node.js ≥ 22.19.0. Start by connecting a language model provider in Settings; media providers are optional.

---

### Publishing

After build, a **shareable browser link** is generated — no install required for players, just open and play. Updating keeps the same link. Publish to the built-in community gallery for others to browse and Remix.

Publish requires an account; **all project files and API keys stay entirely local**.

---

### Tech Stack

| Layer | Tech |
|-------|------|
| Desktop shell | Electron 43 + electron-builder + electron-updater |
| Frontend | React 19 + Vite 7 + @xyflow/react (node graph) |
| 3D/assets | Three.js + glTF Transform + @google/model-viewer |
| Backend daemon | Fastify 5 (local) |
| Cloud services | Supabase (accounts/publish), PostHog (anonymous analytics), Sentry (crash reporting) |
| Agent | @earendil-works/pi-coding-agent + pi-mcp-adapter (MCP) |

---

### Known Limits

- **Beta stage** — v0.0.0-beta.4.3; rough edges exist, APIs may change at any time
- **Not a game engine replacement** — deep physics/rendering still needs Unity/Godot
- **Automated Playtest is still roadmap**, not yet shipped
- **Windows package is unsigned** — manual trust required
- 457 stars, two-month-old project; production stability unproven
- License name and logo are not covered by Apache-2.0

---

### TL;DR

OhMyGame is a local-first AI game development workstation: a Canvas node graph manages all game assets, Pi Coding Agent writes code and runs previews, BYOK covers 40+ LLM providers, image/video/3D generation hooks into mainstream APIs, one-click build publishes to a browser link. A one-person game studio — not a new engine, just a whole new AI-powered workflow layer on top.

---

> Apache-2.0 (name/logo excluded). WhiteTowerAI, Beta v0.0.0-beta.4.3, 457 stars. For reference only — Beta stage, APIs may change at any time.
