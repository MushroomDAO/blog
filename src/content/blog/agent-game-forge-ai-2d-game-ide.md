---
title: "【开源】Agent Game Forge：用 AI Agent 驱动 2D 游戏开发的本地 IDE"
titleEn: "Agent Game Forge: A Local-First, AI-Driven 2D Game IDE"
description: "123 Star 开源项目 Agent Game Forge（AGF）——本地优先的 2D 游戏 IDE，让 Codex 或 Claude Code 帮你从一句描述生成完整游戏。精灵图、parallax 背景、物理、场景编辑器全部内置，Apache 2.0 协议。"
descriptionEn: "Agent Game Forge (AGF, 123 stars) is a local-first 2D game IDE where Codex or Claude Code builds complete games from a single prompt — sprites, parallax, physics, scene editor included. Apache 2.0 licensed."
pubDate: "2026-05-21"
updatedDate: "2026-05-21"
category: "Tech-News"
tags: ["Agent Game Forge", "AI游戏开发", "Claude Code", "Codex", "本地优先", "开源", "2D游戏", "TypeScript", "Tech-News"]
heroImage: "../../assets/images/agent-game-forge-ai-2d-game-ide-banner.jpg"
---

> **BLUF**：Agent Game Forge（AGF）不是传统游戏引擎，而是**用 AI Agent 驱动游戏开发的本地 IDE**。你描述游戏想法，Codex 或 Claude Code 帮你写代码、生成精灵图、搭场景逻辑——你只需要拖拽调整 agent 没做好的部分。123 Star，Apache 2.0，TypeScript 实现，目前主力输出 vanilla JS + Canvas，Godot 4 和 Unity 在路线图上。

---

## 是什么？

**Agent Game Forge**（简称 **AGF**）是一个开源的桌面 IDE，让 AI coding agent 帮你端到端地构建完整的 2D 游戏：

- 角色 sprite 与多动作动画
- parallax 4 层可平铺背景
- 物理、伤害区、收集物、场景布局
- 可视化编辑器：拖拽调整 agent 没做对的部分

**你选 agent**（Codex CLI 或 Claude Code）**你选 image gen**——自带 API key，或使用 Codex CLI 内置的 GPT-Image2。项目代码留在你的本地，没有强制云服务。

**GitHub**：[0x0funky/agent-game-forge](https://github.com/0x0funky/agent-game-forge) · ⭐ 123 · TypeScript · Apache 2.0

---

## 核心能力

### Bring Your Own Agent（BYOA）

不绑定特定 AI 服务，在 Settings 里实时切换：

| Agent | 说明 |
|---|---|
| **Codex CLI** | OpenAI 出品，内置 GPT-Image2 图片生成，无需额外 API key |
| **Claude Code** | Anthropic 出品，需要 Gemini 或 OpenAI API key 用于图片生成 |

两条路径出来的效果等价，API key 全部存在本地 `~/.ogf/secrets.json`（mode 600），不进 git，不出现在日志。

### 正规 Asset Pipeline

不是简单调 AI 生图，而是完整的游戏资源处理流程：

- **sprite-sheet chroma-key**：自动去背景、多动作动画切分
- **parallax 4 层 tileable + despill**：生成无缝滚动背景
- **多 image gen 路由**：按供应商分类显示今天的调用次数和预估花费

### 可视化场景编辑器

Agent 生成场景 JSON 后，你可以直接在编辑器里：

- 拖拽 platform、hazard、pickup、collider
- hitbox 红色虚线可视化
- 修改后 Play tab 实时 reload

Agent 读写同一份 JSON，你拖一个 platform，agent 下次迭代也能看到这个变更。

### 本地优先，零 Framework 绑定

生成的游戏是纯 JS + Canvas：
- `index.html`、`src/*.js`、`data/*.json`、`assets/`
- 推到 GitHub Pages 直接跑，不依赖任何 framework
- Daemon 绑定 `127.0.0.1`，代码不离开你的机器

---

## 工作原理

```
        ┌──────────────┐    ┌──────────────────────────┐    ┌─────────────┐
你 ─→   │  Web UI      │ ←→ │  Daemon (Node + SQLite)  │ ←→ │  Agent CLI  │
        │  React canvas│    │  /api/runs, /api/scenes  │    │  (Codex /   │
        │  Scene editor│    │  /api/gen-image (router) │    │   Claude    │
        └──────────────┘    └──────────────┬───────────┘    │   Code)     │
                                           │                 └─────┬───────┘
                                           ↓                       │
                                    ┌──────┴──────┐                │
                                    │ Gemini /    │ ←──────────────┘
                                    │ OpenAI API  │  （图片生成走
                                    │ (你的 key)  │    daemon HTTP）
                                    └─────────────┘
```

1. **你在 chat 描述游戏**：Web UI 通过 SSE 实时 stream agent 的每个 token 和工具调用
2. **Agent 读 AGF 的 conventions 和 skills**：每个项目都 vendor 一份规则文件（通用 + per-genre），agent 跟着 recipe 走，不会随机发明流程
3. **图片生成走 daemon**：`/api/gen-image` 路由到你选的 Gemini 或 OpenAI，Codex 用户可直接用内置 `image_gen`
4. **场景编辑器和 agent 共享同一份 JSON**：agent 生成，你拖拽微调，互不打架
5. **Runtime 就是项目本身**：直接推 GitHub Pages 跑

---

## 如何上手？

**环境需求**：Node ≥ 20、npm ≥ 10，至少安装一个 agent：

```bash
# 安装 Codex CLI（可选）
npm i -g @openai/codex

# 安装 Claude Code（可选）
npm i -g @anthropic-ai/claude-code
```

**启动 AGF**：

```bash
git clone https://github.com/0x0funky/agent-game-forge.git
cd agent-game-forge
npm install
npm run dev
```

启动后：
- **Daemon**：`http://localhost:7621`
- **Web UI**：`http://localhost:7620`

打开 Web UI，右上角齿轮 → Settings，选好 agent 和 API key，然后输入 prompt：

> *"横版卷轴平台游戏，主角是要回家的狗狗，有屋顶和公园大门两关。"*

发送，等 agent 构建，按 **Play**。

---

## 项目当前状态

| 游戏类型 | 状态 | 备注 |
|---|---|---|
| **横版卷轴平台** | ✅ 已发布 | parallax、hazard、pickup、多关卡、sprite chroma-key 完整 |
| 俯视角 RPG | 🟡 部分支持 | 基础 seed + recipe 存在，部分 recipe 仍在完善 |
| 塔防 / 竞技场 | 🟡 部分支持 | 早期分支继承，需要打磨 |
| Roguelike / Metroidvania | 🟡 部分支持 | 规划在正式发布后 |

| 引擎目标 | 状态 | 备注 |
|---|---|---|
| **Web**（vanilla JS + Canvas） | ✅ 默认输出 | 零 framework 依赖，GitHub Pages 直跑 |
| **Godot 4** | 🟡 历史支持 + 路线图 | 现有 Godot 项目可加载编辑，一类支持在发布后规划 |
| **Unity** | 🚧 规划中 | Godot 一类支持落地后再做 |

---

## 为什么值得关注？

### AI 游戏开发的新范式

这正是 a16z 等机构看好的方向——**用 AI Agent 做游戏开发**。传统游戏开发需要团队协作和大量时间，而 AI 驱动后，一个人就能完成相当规模的工作。AGF 是这个方向最完整的开源实践之一：

- 不只是 AI 写代码，而是 AI 驱动完整的开发流水线
- Agent 遵循项目内置的 conventions 和 recipes，而非随机生成
- 人保留可视化编辑权，agent 负责繁琐的代码和资源生成

### Apache 2.0 协议的商业价值

项目采用 Apache 2.0，对商业使用友好：
- 不像 GPL 有传染性
- 企业可以自由集成和修改
- 只需保留 copyright 和 license 声明

---

## 常见问题

**Q：本地运行需要什么硬件？**
A：主要靠云端 API（Codex/Claude Code + Gemini/OpenAI），本地只跑 Node.js daemon 和 Web UI，对硬件要求不高。

**Q：生成的游戏可以商用吗？**
A：生成的游戏代码归你所有，但注意你使用的 AI 服务（Codex、Claude Code、OpenAI、Gemini）各自有服务条款，商用前需自行确认。

**Q：和 Godogen 有什么区别？**
A：Godogen 专注于 Godot/Bevy 引擎，从描述到可运行游戏的完整自动化，有截图驱动的自我修复。AGF 的定位更像一个**可交互的 IDE**——agent 构建，人拖拽微调，更强调人机协作而非全自动。

**Q：能在 Windows / Linux 上运行吗？**
A：主要开发环境是 Windows，macOS/Linux 跨平台问题可能存在，欢迎在 issue 里报告。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: Agent Game Forge (AGF) is not a traditional game engine — it's a **local-first 2D game IDE driven by AI agents**. Describe your game idea; Codex or Claude Code writes the code, generates sprites, and builds the scene logic. You just drag-tweak whatever the agent got wrong. 123 stars, Apache 2.0, TypeScript — vanilla JS + Canvas output today, Godot 4 and Unity on the roadmap.

---

## What Is It?

**Agent Game Forge** (AGF) is an open-source desktop IDE that lets an AI coding agent build complete 2D games end-to-end:

- Character sprites with multi-action animation
- Parallax 4-layer tileable backgrounds
- Physics, hazards, pickups, scene layouts
- Visual scene editor to drag-tweak whatever the agent got wrong

**You pick the agent** (Codex CLI or Claude Code) and **you pick the image gen** — bring your own API key, or use Codex CLI's built-in GPT-Image2. Your project files stay on your disk with no mandatory cloud dependency.

**GitHub**: [0x0funky/agent-game-forge](https://github.com/0x0funky/agent-game-forge) · ⭐ 123 · TypeScript · Apache 2.0

---

## Core Features

### Bring Your Own Agent (BYOA)

No vendor lock-in — switch agents live in Settings:

| Agent | Notes |
|---|---|
| **Codex CLI** | OpenAI-built, GPT-Image2 image gen built in |
| **Claude Code** | Anthropic-built, bring your own Gemini or OpenAI key for image gen |

API keys are stored locally at `~/.ogf/secrets.json` (mode 600), never in git, never in logs.

### Production-Grade Asset Pipeline

More than just AI image generation — a complete game asset workflow:

- **Sprite-sheet chroma-key**: auto background removal, multi-action animation splitting
- **Parallax 4-layer tileable + despill**: seamless scrolling backgrounds
- **Cost-transparent**: Settings panel shows today's image-gen call count and estimated spend per provider

### Visual Scene Editor

After the agent generates scene JSON, you can directly:

- Drag platforms, hazards, pickups, colliders
- View hitbox overlays
- Live-reload to the Play tab

Agent and editor share the same JSON files — your drag-tweaks are visible to the next agent iteration.

### Local-First, Zero Framework Lock-In

Generated games are pure JS + Canvas:
- `index.html`, `src/*.js`, `data/*.json`, `assets/`
- Push to GitHub Pages and it runs — no framework dependency
- Daemon binds to `127.0.0.1`; your code never leaves your machine

---

## How It Works

```
        ┌──────────────┐    ┌──────────────────────────┐    ┌─────────────┐
You ─→  │  Web UI      │ ←→ │  Daemon (Node + SQLite)  │ ←→ │  Agent CLI  │
        │  React canvas│    │  /api/runs, /api/scenes  │    │  (Codex /   │
        │  Scene editor│    │  /api/gen-image (routed) │    │   Claude    │
        └──────────────┘    └──────────────┬───────────┘    │   Code)     │
                                           │                 └─────┬───────┘
                                           ↓                       │
                                    ┌──────┴──────┐                │
                                    │ Gemini /    │ ←──────────────┘
                                    │ OpenAI API  │   (image gen via
                                    │ (your key)  │    daemon HTTP)
                                    └─────────────┘
```

1. **You describe your game in chat** — Web UI streams every token and tool call via SSE
2. **Agent reads AGF conventions and skills** — vendored `.ogf/conventions/` + `.agents/skills/` per project; agent follows recipes instead of reinventing the pipeline
3. **Images go through daemon `/api/gen-image`** — routes to your Gemini or OpenAI; Codex users can use the built-in `image_gen` tool instead
4. **Scene editor and agent share the same JSON** — you drag-tweak, agent sees the update
5. **Runtime is the project itself** — pure JS + Canvas, push to GitHub Pages

---

## Quick Start

**Requirements**: Node ≥ 20, npm ≥ 10, and at least one agent CLI:

```bash
# Install Codex CLI (optional)
npm i -g @openai/codex

# Install Claude Code (optional)
npm i -g @anthropic-ai/claude-code
```

**Launch AGF**:

```bash
git clone https://github.com/0x0funky/agent-game-forge.git
cd agent-game-forge
npm install
npm run dev
```

Opens:
- **Daemon**: `http://localhost:7621`
- **Web UI**: `http://localhost:7620`

Open the Web UI, click the gear icon → Settings, pick your agent and API key, then send a prompt like:

> *"Side-scroll platformer about a dog going home, with rooftop and park gate levels."*

Hit send. Watch the agent build it. Press **Play**.

---

## Project Status

| Genre | Status | Notes |
|---|---|---|
| **Side-scroll platformer** | ✅ Shipped | Full parallax pipeline, hazards, pickups, multi-level, sprite chroma-key |
| Top-down RPG | 🟡 Partial | Foundation seed + recipes; some recipes still maturing |
| Tower defense / arena | 🟡 Partial | Inherited from earlier branches; needs polish |
| Roguelike / Metroidvania | 🟡 Partial | Planned post-launch |

| Engine | Status | Notes |
|---|---|---|
| **Web** (vanilla JS + Canvas) | ✅ Default | Zero framework dependency; push to GitHub Pages, it runs |
| **Godot 4** | 🟡 Legacy + Roadmap | Existing projects load + edit; first-class re-investment post-launch |
| **Unity** | 🚧 Planned | Targeted after Godot first-class lands |

---

## Why It Matters

### A New Paradigm for Game Development

This is exactly the direction firms like a16z are watching — **AI agents driving game development**. Traditional game dev requires teams and months. AI-driven, one person can ship a substantial game. AGF is one of the most complete open-source implementations of this approach:

- Not just AI writing code, but AI driving the full dev pipeline
- Agent follows vendored conventions and recipes, not random generation
- Humans retain visual editing control; agent handles the tedious code and asset work

### Apache 2.0 — Enterprise-Friendly

- No copyleft contagion unlike GPL
- Companies can integrate and fork freely
- Just keep the copyright + license notice

---

## FAQ

**Q: What hardware do I need?**
A: AI computation runs in the cloud (Codex/Claude Code + Gemini/OpenAI API). The local daemon and Web UI are lightweight Node.js processes — no special hardware required.

**Q: Can I sell games built with AGF?**
A: The generated game code is yours. But check the terms of the AI services you use (Codex, Claude Code, OpenAI, Gemini) for commercial use rights.

**Q: How does this differ from Godogen?**
A: Godogen focuses on Godot/Bevy with full end-to-end automation and screenshot-driven self-repair. AGF is more of an **interactive IDE** — agent builds, you drag-tweak, emphasizing human-AI collaboration over full automation.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
