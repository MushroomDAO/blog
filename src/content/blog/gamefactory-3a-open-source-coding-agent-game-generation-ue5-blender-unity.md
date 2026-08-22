---
title: "GameFactory-3A：让编程 Agent 直接生成 3A 游戏资产，UE5/Blender/Unity/three.js 全支持，Apache 2.0 开源"
titleEn: "gamefactory-3a-open-source-coding-agent-game-generation-ue5-blender-unity"
description: "OpenDCAI/GameFactory-3A 是一个开源的 3A 游戏生成 Skill 和资产框架，Apache 2.0，Python，256 stars。核心思路：把 Claude Code、Codex、Gemini CLI 等编程 Agent 接入一套结构化的 Skill 体系，Agent 读 agent_skills/setting_overview.md 后，自动调用图像生成、3D 对象/场景、动作捕捉、音频、CG 视频、UI/游戏逻辑等完整流水线，产出可直接导入 UE5、Blender、Unity 或 three.js 的引擎就绪代码和资产。项目已有 Unity/UE5/Blender/three.js 四套引擎的游戏 Demo（格斗/FPS/赛车/RPG），CG 视频本地用 MiniMax H3 在 720P 生成。"
descriptionEn: "OpenDCAI/GameFactory-3A is an open-source 3A game-generation skill and asset framework — Apache 2.0, Python, 256 stars. Core approach: connect coding agents (Claude Code, Codex, Gemini CLI) to a structured skill system. The agent reads agent_skills/setting_overview.md and automatically invokes image generation, 3D objects/scenes, motion, audio, CG video, UI, and gameplay pipelines — producing engine-ready code and assets for UE5, Blender, Unity, or three.js. Demos across four engines (fighting/FPS/racing/RPG); CG video generated locally at 720P with MiniMax H3."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["游戏生成", "编程Agent", "3A游戏", "UE5", "Unity", "Blender", "AI资产生成", "开源"]
heroImage: "../../assets/images/gamefactory-3a-open-source-coding-agent-game-generation-ue5-blender-unity-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：OpenDCAI/GameFactory-3A  
许可证：Apache 2.0  
语言：Python  
Stars：256 · Forks：12  
创建：2026-07-06 | 最近更新：2026-08-22

---

## 一、它在做什么

3AGameFactory 的核心命题只有一句话：

> **把游戏需求描述交给编程 Agent，得到可直接导入引擎的游戏资产和游戏代码。**

整个框架不是游戏引擎，也不是单个生成模型——它是一套专门为编程 Agent（Claude Code、Codex、Gemini CLI）设计的 **Skill 和流水线体系**，让 Agent 知道怎么调用哪些生成模型、产出什么格式的资产、如何集成进哪个游戏引擎。

---

## 二、怎么用

```
1. 打开 Claude Code / Codex / Gemini CLI
2. cd GameFactory-3A
3. 告诉 Agent 游戏需求，并让它先读 agent_skills/setting_overview.md
```

`agent_skills/setting_overview.md` 是整个系统的入口文件——Agent 读完它之后，知道可以生成什么、调用哪条流水线、支持哪个引擎。剩下的由 Agent 自己驱动。

---

## 三、能生成什么

| 能力 | 产出 | 流水线目录 |
|------|------|---------|
| 图像和 T-Pose 准备 | 角色源图、Ready-to-rig 输入 | `pipeline/assets_gen/gen_tpose_image/` |
| 3D 对象生成 | 道具、角色、武器、可复用网格 | `pipeline/assets_gen/gen_3d_object/` |
| 3D 场景生成 | 室内重建、环境组装 | `pipeline/assets_gen/gen_3d_scene/` |
| 动作生成 | 骨骼绑定、动作生成、动画重定向 | `pipeline/assets_gen/gen_motion/` |
| 音频生成 | 对白、音效、环境音、WAV 资产 | `pipeline/assets_gen/gen_audio/` |
| CG 视频生成 | 文本/帧/参考图条件的 MP4 片段 | `pipeline/assets_gen/gen_cg_video/` |
| 玩法代码生成 | 引擎原生机制和运行时行为 | `pipeline/code_gen/gen_mechanic/` |
| UI 生成 | HUD、菜单、界面、交互流 | `pipeline/code_gen/gen_ui/` |

**3D 模型主要用了两个模型**：Meshy（角色/武器）和 Hunyuan3D（另一部分资产）。动作来源是 Puppeteer + MoMask 链，或 Mixamo。CG 视频本地用 MiniMax H3 生成（720P），也支持接 Seedance 等云端 API 做更高分辨率。

---

## 四、支持的游戏引擎

| 引擎 | Agent Context 文件 | 参考实现 |
|------|---------|---------|
| UE5 | `agent_skills/engine_context/ue5_api.md` | `engine_adapters/ue5/` |
| Blender | `agent_skills/engine_context/blender_api.md` | `engine_adapters/blender/` |
| Unity | `agent_skills/engine_context/unity3d_api.md` | `engine_adapters/unity3d/` |
| three.js | `agent_skills/engine_context/three_js_api.md` | `engine_adapters/three_js/` |

每个引擎都有对应的 Agent Context 文件，让 Agent 了解该引擎的 API 约定，再生成引擎就绪的代码。

---

## 五、Demo 情况

四个引擎都有实际可玩的 Demo 视频（格斗/FPS/赛车/RPG），以及四种 CG 视频（F1 开场、奇幻 RPG 过场、反恐 FPS 预告、格斗游戏大招演出）。

值得注意的几个点：
- **Unity Demo**：格斗角色全流程用 Meshy 生成后，用 Puppeteer + MoMask 链绑定并驱动动作
- **UE5 Demo**：场景全部用开源资产，角色和动作用 Mixamo 或 Meshy，武器用 Hunyuan3D
- **CG 视频**：用本地 MiniMax H3 在 720P 生成；文本生视频（T2V）、帧生视频（F2V/R2V）都有

---

## 六、架构设计

```
GameFactory-3A/
├── agent_skills/      # Agent 可读的工作流、QA Skill、引擎 API 上下文
│   ├── setting_overview.md   # ← Agent 入口
│   ├── asset_qa/
│   ├── code_gen/
│   ├── develop_harness/      # 贡献者契约：模型→算子→流水线
│   └── engine_context/
├── models/            # 本地/云端模型包装层
├── operators/         # 组合模型的任务逻辑
├── pipeline/          # 生成和评估入口
├── engine_adapters/   # 各引擎参考代码和公共 Adapter API
└── test/              # 契约测试、集成测试、冒烟测试
```

分层很清晰：**Skill 层**（告诉 Agent 能做什么）→ **Operator 层**（组合模型，实现任务逻辑）→ **Pipeline 层**（入口和执行）→ **Engine Adapter 层**（引擎特定产出）。

贡献者如果要添加新的生成模型，从 `agent_skills/develop_harness/README.md` 开始，有 CPU-only 冒烟测试，不需要 GPU 也能跑通贡献流程。

---

## 七、这个方向有什么价值

游戏行业一直缺一条路：从「我想做一个格斗游戏」到「可以跑的格斗游戏」。传统路径需要美术、动作、程序、技术美术分工协作，最短也要几个月。

3AGameFactory 的赌注是：如果生成模型（图像、3D、动作、音频、视频）已经够用，缺的是一个**让编程 Agent 能系统性地调用这些模型的框架**。这套 Skill 体系就是那个框架。

256 stars，项目创建才一个半月，Demo 质量已经覆盖了四个引擎、四种类型游戏。对游戏开发者和 AI 工具研究者来说，是值得关注的早期项目。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## GameFactory-3A: Coding Agents That Generate 3A Game Assets — UE5, Blender, Unity, three.js, Apache 2.0

*by Mycelium Protocol*

---

GitHub: OpenDCAI/GameFactory-3A  
License: Apache 2.0  
Language: Python  
Stars: 256 · Forks: 12  
Created: 2026-07-06 | Updated: 2026-08-22

---

### What It Does

3AGameFactory's core proposition in one sentence:

> **Give a game requirement to a coding agent, get engine-ready game assets and game code.**

The framework isn't a game engine and isn't a single generation model — it's a structured **skill and pipeline system designed for coding agents** (Claude Code, Codex, Gemini CLI). The agent learns what generation models to call, what asset formats to produce, and how to integrate outputs into a target engine.

---

### How to Use It

```
1. Open Claude Code, Codex, or Gemini CLI
2. cd GameFactory-3A
3. Describe your game and ask the agent to read agent_skills/setting_overview.md first
```

`agent_skills/setting_overview.md` is the system entry point — once the agent reads it, it knows what it can generate, which pipeline to call, and which engine to target. The agent drives the rest.

---

### What It Can Generate

| Capability | Output | Pipeline |
|------------|--------|----------|
| Image & T-pose prep | Character source images, rig-ready inputs | `pipeline/assets_gen/gen_tpose_image/` |
| 3D object generation | Props, avatars, weapons, reusable meshes | `pipeline/assets_gen/gen_3d_object/` |
| 3D scene generation | Reconstructed interiors, assembled environments | `pipeline/assets_gen/gen_3d_scene/` |
| Motion | Rigs, generated motion, retargeted clips | `pipeline/assets_gen/gen_motion/` |
| Audio | Dialogue, SFX, ambience, WAV assets | `pipeline/assets_gen/gen_audio/` |
| CG video | Text/frame/reference-conditioned MP4 clips | `pipeline/assets_gen/gen_cg_video/` |
| Gameplay code | Engine-native mechanics and runtime behavior | `pipeline/code_gen/gen_mechanic/` |
| UI | HUDs, menus, interaction flows | `pipeline/code_gen/gen_ui/` |

**Primary 3D models**: Meshy (characters/weapons) and Hunyuan3D. Motion via Puppeteer + MoMask chain or Mixamo. CG video generated locally with MiniMax H3 (720P) or via Seedance cloud API for higher resolution.

---

### Supported Engines

| Engine | Agent Context | Reference Implementation |
|--------|--------------|--------------------------|
| UE5 | `agent_skills/engine_context/ue5_api.md` | `engine_adapters/ue5/` |
| Blender | `agent_skills/engine_context/blender_api.md` | `engine_adapters/blender/` |
| Unity | `agent_skills/engine_context/unity3d_api.md` | `engine_adapters/unity3d/` |
| three.js | `agent_skills/engine_context/three_js_api.md` | `engine_adapters/three_js/` |

Each engine has a dedicated context file so the agent understands the engine's API conventions and generates engine-compatible code.

---

### Demos

All four engines have playable game demos (fighting/FPS/racing/RPG) plus four CG video types (F1 race opening, fantasy RPG cutscene, counter-terrorism FPS promo, fighting game ultimate cinematic).

Notable details:
- **Unity demo**: fighting characters fully generated with Meshy, then rigged and animated via Puppeteer + MoMask chain
- **UE5 demo**: all scenes are open-source assets; characters and motion from Mixamo or Meshy; weapons from Hunyuan3D
- **CG video**: MiniMax H3 locally at 720P; text-to-video (T2V), frame-to-video (F2V/R2V) both covered

---

### Architecture

```
GameFactory-3A/
├── agent_skills/      # Agent-readable workflows, QA skills, engine API context
│   ├── setting_overview.md   # ← Agent entry point
│   ├── asset_qa/
│   ├── code_gen/
│   ├── develop_harness/      # Contributor contracts: model → operator → pipeline
│   └── engine_context/
├── models/            # Local/cloud model wrappers
├── operators/         # Task logic composing loaded models
├── pipeline/          # Generation and evaluation entry points
├── engine_adapters/   # Engine reference code and public adapter APIs
└── test/              # Contract, integration, and smoke checks
```

The layering is clear: **Skill layer** (tells the agent what's possible) → **Operator layer** (task logic composing models) → **Pipeline layer** (entry and execution) → **Engine Adapter layer** (engine-specific outputs).

Contributors adding new generation models start from `agent_skills/develop_harness/README.md`, which provides a CPU-only smoke harness — no GPU required to validate contributions.

---

### Why This Direction Matters

The game industry has always lacked a direct path from "I want a fighting game" to "a running fighting game." Traditional paths require art, animation, engineering, and technical art working together for months at minimum.

3AGameFactory's bet: if the generation models (image, 3D, motion, audio, video) are already capable enough, what's missing is a **framework that lets a coding agent systematically call all of them**. This skill system is that framework.

256 stars, project created six weeks ago, demos already covering four engines and four game types. Worth watching for game developers and AI tooling researchers.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
