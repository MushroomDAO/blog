---
title: "Godogen：用 Claude Code 一句话生成完整游戏，支持 Godot/Bevy/Babylon.js"
titleEn: "godogen-ai-game-generator-claude-code-godot-bevy-babylon"
description: "htdt/godogen 是基于 Claude Code / Codex 打造的全链路 AI 游戏生成流水线。描述一个游戏，Agent 自动构建项目、生成资产、运行引擎、并用运行中的游戏证明结果。支持 Godot 4（C#）、Bevy（Rust）、Babylon.js（TypeScript），5.2K stars，MIT 协议。"
descriptionEn: "htdt/godogen is a full-chain AI game generation pipeline built on Claude Code and Codex. Describe a game; the agent builds the project, generates assets, runs the engine, and proves the result from the live running game. Supports Godot 4 (C#), Bevy (Rust), Babylon.js (TypeScript). 5.2K stars, MIT license."
pubDate: "2026-08-03"
updatedDate: "2026-08-03"
category: "Tech-News"
tags: ["AI游戏生成", "Claude Code", "Godot", "Bevy", "Babylon.js", "Codex", "开源", "Mycelium"]
heroImage: "../../assets/images/godogen-ai-game-generator-claude-code-godot-bevy-babylon-banner.jpg"
---

*by Mycelium Protocol*

---

"一句话描述，自动生成游戏"——这个想法本来听起来像 PPT。

**[Godogen](https://github.com/htdt/godogen)**（htdt，@alex_erm）把它变成了一个 MIT 开源项目：基于 Claude Code / Codex 打造的全链路 AI 游戏自动生成流水线，5.2K stars，支持三个主流引擎（Godot 4、Bevy、Babylon.js），从提示词到跑起来的游戏，Agent 全程自主完成。

---

## 它不是一个游戏，是一台游戏工厂

Godogen 的定位非常清晰：

```
godogen → game repo → game
```

你给它一段描述，它生成一个**新的游戏仓库**，Agent 在那个仓库里从头构建游戏——项目脚手架、代码、资产、编译运行、结果验证，全部自主完成。

`publish.sh` 是入口，渲染出选定引擎 + Agent 的运行环境：

```bash
# 选引擎 + 选 Agent
./publish.sh --engine godot   --agent claude --out ~/my-game  # 输出 CLAUDE.md + skills/
./publish.sh --engine babylon --agent codex  --out ~/my-game  # 输出 AGENTS.md + skills/
./publish.sh --engine bevy    --agent claude --out ~/my-game
```

发布出去的 game repo 结构有意保持精简：一个 runtime manifest（`prompts/runtime.md`）、一页引擎指南、以及资产生成 skill。其他所有东西——项目脚手架、截图工具——都由 Agent 从引擎指南里重新推导出来。

---

## 三引擎，各有专长

| 引擎 | 语言 | 特点 |
|------|------|------|
| **Godot 4** | C# / .NET | 构建时场景生成、运行时脚本、Jolt 物理 |
| **Bevy** | Rust | 代码优先 ECS 场景、离屏捕获 |
| **Babylon.js** | TypeScript / Vite | 浏览器游戏，直接输出可访问的 live URL |

---

## 资产生成：三个 AI 服务分工合作

Agent 自己搞定美术资产，按类型分派给不同的 AI 服务：

| 资产类型 | 服务 |
|---------|------|
| 精准参考图、角色 | Gemini（Google AI Studio）|
| 纹理、简单物件 | xAI Grok |
| 图片转 3D、带绑定的双足动画 | Tripo3D |
| 动态精灵（带循环检测和背景去除） | Grok 视频 |

---

## "用跑起来的游戏证明结果"

Godogen 有一个很有意思的设计原则：**Proof over claims**。

Agent 不看编译是否成功，不看代码是否整洁——它从**运行中的游戏**里判断结果：Babylon.js 是一个 live URL，Godot/Bevy 是一段截屏录像。可见的缺陷才驱动下一轮迭代。

这和大多数 AI 代码生成工具"生成完就结束"的逻辑完全不同——它把验证环节也包进了自主循环里。

---

## 两种运行模式

**交互模式**：你打开 live URL（Babylon.js）或运行本地项目（Godot/Bevy），实时看到游戏，可以在 Agent 的决策节点介入和引导。

**无人值守模式**：留 Agent 自己跑，结束后给你一段 15-20 秒的证明录像。

Agent 根据你提任务的方式自动判断走哪条路——不需要你显式指定。

---

## 快速上手

### 依赖

```bash
# 引擎
# Godot 4 (.NET build) 加入 PATH
# Rust/Cargo（Bevy 项目）
# Node.js 22.12+、npm（Babylon.js）

# 系统包
apt install vulkan-tools xvfb ffmpeg imagemagick  # Ubuntu/Debian

# Python 3 + pip

# API keys
export GOOGLE_API_KEY=...   # Gemini 图像生成（Google AI Studio）
export XAI_API_KEY=...       # Grok 图像/视频生成
export TRIPO3D_API_KEY=...   # 3D 生成
```

### 发布 game repo，然后让 Agent 跑

```bash
# 克隆 godogen
git clone https://github.com/htdt/godogen
cd godogen

# 发布到新的 game repo
./publish.sh --engine babylon --agent claude --out ~/my-game

# 进入 game repo，启动 Claude Code
cd ~/my-game
claude
# 然后在 Claude Code 里描述你的游戏…
```

长时间跑的任务建议在服务器上用 `tmux` 保持会话，Claude Code 和 Codex 都有官方远程控制接口，可以随时查看进度。

---

## 为什么值得关注

Godogen 做了一件"纵向整合"的事情：它不只是让 AI 写游戏代码，而是把**整条制作链**——代码生成、资产生成、引擎运行、结果验证、缺陷驱动迭代——全部纳入同一个 Agent 循环里。

用 Claude Code 的 skill 系统做交付，让 Agent 可以跨越代码和工具之间的边界直接操作引擎，这是当前 Vibe-coding 工具大多做不到的事。

MIT 开源，支持 Claude Code 和 Codex 双 Agent，三引擎覆盖了 2D/3D 游戏和浏览器游戏的主流技术栈。如果你在做 AI 游戏生成或者 Agent 自动化工程方向的研究，Godogen 是目前最完整的开源参考实现。

仓库：[github.com/htdt/godogen](https://github.com/htdt/godogen) · Demo 视频：[youtu.be/eUz19GROIpY](https://youtu.be/eUz19GROIpY) · 作者：[@alex_erm](https://x.com/alex_erm)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Godogen: Describe a Game, Claude Code Builds It — Godot, Bevy, and Babylon.js

*by Mycelium Protocol*

"Describe a game and have it built automatically" — that used to sound like slide-deck vaporware.

**[Godogen](https://github.com/htdt/godogen)** (htdt, @alex_erm) ships it as an open-source project: a full-chain AI game generation pipeline built on Claude Code and Codex, 5.2K stars, supporting three engines (Godot 4, Bevy, Babylon.js). From a short prompt to a running game — the agent handles everything autonomously.

### It's Not a Game. It's a Game Factory.

The positioning is explicit:

```
godogen → game repo → game
```

You provide a description; Godogen generates a fresh **game repository**, and the agent builds the complete game inside that repo — scaffolding, code, assets, compilation, execution, and result verification — all autonomously.

`publish.sh` is the entry point, rendering the runtime environment for a chosen engine and host agent:

```bash
./publish.sh --engine godot   --agent claude --out ~/my-game  # CLAUDE.md + skills/
./publish.sh --engine babylon --agent codex  --out ~/my-game  # AGENTS.md + skills/
./publish.sh --engine bevy    --agent claude --out ~/my-game
```

The published game repo is intentionally thin: a runtime manifest (`prompts/runtime.md`), a one-page engine guide, and the asset-generation skill. Everything else — project scaffold, capture tooling — the agent recreates from the engine guide.

### Three Engines, Each With Its Strengths

| Engine | Language | Capabilities |
|--------|----------|--------------|
| **Godot 4** | C# / .NET | Build-time scene generation, runtime scripts, Jolt physics |
| **Bevy** | Rust | Code-first ECS scenes, offscreen capture |
| **Babylon.js** | TypeScript / Vite | Browser games, outputs a live accessible URL |

### Asset Generation: Three AI Services, Divided by Task

The agent handles all art assets by routing to the right service by type:

| Asset Type | Service |
|------------|---------|
| Precise references and characters | Gemini (Google AI Studio) |
| Textures and simple objects | xAI Grok |
| Image-to-3D and rigged biped animation | Tripo3D |
| Animated sprites (with loop detection and background removal) | Grok video |

### "Proof Over Claims"

Godogen has an interesting design principle: the agent doesn't judge results from whether the code compiles cleanly. It judges from the **running game** — a live Babylon.js URL, or a recorded clip for Godot/Bevy. Visible defects drive the next iteration.

This is a fundamentally different loop from most AI code generators that stop at "generation complete." Verification is part of the autonomous cycle.

### Two Execution Modes

**Interactive**: Open the live Babylon.js URL or run the local project, watch the game in real time, and steer the agent at decision points.

**Unattended**: Let the agent run solo; receive a 15–20 second proof recording at the end.

The agent infers which mode you want from how you frame the task — no explicit flag needed.

### Quick Start

```bash
# Install system deps (Ubuntu/Debian)
apt install vulkan-tools xvfb ffmpeg imagemagick

# Set API keys
export GOOGLE_API_KEY=...   # Gemini image gen
export XAI_API_KEY=...       # Grok image/video gen
export TRIPO3D_API_KEY=...   # 3D gen

# Publish game repo
git clone https://github.com/htdt/godogen
cd godogen
./publish.sh --engine babylon --agent claude --out ~/my-game

# Enter game repo, start Claude Code, describe your game
cd ~/my-game && claude
```

Long runs benefit from `tmux` on a server. Both Claude Code and Codex have official remote-control interfaces for checking in and steering while the run is underway.

### Why This Matters

Godogen does vertical integration: it doesn't just make AI write game code. It puts the **entire production chain** — code generation, asset generation, engine execution, result verification, defect-driven iteration — inside a single agent loop.

Using Claude Code's skill system for delivery lets the agent operate across the code/tool boundary to directly drive the engine — something most current AI coding tools can't do.

MIT license, dual-agent support (Claude Code and Codex), three engines covering 2D/3D and browser games. If you're researching AI game generation or autonomous agent engineering, Godogen is the most complete open-source reference implementation available today.

Repository: [github.com/htdt/godogen](https://github.com/htdt/godogen) · Demo: [youtu.be/eUz19GROIpY](https://youtu.be/eUz19GROIpY) · Author: [@alex_erm](https://x.com/alex_erm)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
