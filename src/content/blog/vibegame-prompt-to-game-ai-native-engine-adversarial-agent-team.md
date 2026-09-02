---
title: "VibeGame：用自然语言描述，8个 Agent 协作，直接生成可玩的完整 2D 游戏"
titleEn: "VibeGame: Natural Language → Playable 2D Game, Built by 8 Specialized Agents"
description: "南京大学 + 南洋理工大学联合发布 VibeGame，一个 AI-native 游戏引擎 + 对抗性 Agent 团队框架，能从自然语言 prompt 和参考图片直接生成并持续编辑完整的 2D 网页游戏，支持 IP 迁移、类型迁移和规则重构。"
descriptionEn: "Nanjing University + NTU release VibeGame — an AI-native game engine + adversarial agent team framework that generates and continuously edits complete 2D web games from natural language prompts and reference images, supporting IP transfer, genre transfer, and rule restructuring."
pubDate: 2026-09-03
updatedDate: 2026-09-03
category: Research
tags: ["AI", "游戏开发", "多智能体", "vibe-coding", "Claude", "开源", "game-development"]
heroImage: "../../assets/images/vibegame-prompt-to-game-ai-native-engine-adversarial-agent-team-banner.jpg"
author: "Mycelium Protocol"
---

想象一下：你用几句话描述"做一个像只狼一样的 Boss 战，玩家能格挡、弹刀、秒杀"，然后一队 AI 自动生成游戏设计文档、原画、代码、物理碰撞，反复测试到可以玩，最后交给你一个完整的 2D 网页游戏。

这不是想象——**VibeGame** 已经把这件事做出来了。

来自南京大学 PRLab 和南洋理工大学 S-Lab 的团队刚发布了这个框架，论文日期 2026-08-17，GitHub 仓库也同步开源（Apache-2.0），建立在 Claude Code + Codex 之上运行。

---

## 核心挑战：游戏为什么比普通软件难生成

LLM 生成普通软件已经相当成熟，但生成游戏面临三个额外问题：

1. **项目状态极其复杂**：代码、场景、美术资源、动画、物理配置必须互相一致。改一个地方，其他地方可能悄悄出问题。
2. **正确性只能通过运行验证**：代码在语法上正确不代表游戏能玩，必须真正运行起来测试才知道。
3. **需要持续迭代**：第一个可玩版本不是终点，用户会继续要求改机制、换美术、调平衡——Agent 必须能在不破坏已有功能的前提下做出修改。

VibeGame 针对这三个问题各提出了一个核心机制。

---

## 三层架构

### 第一层：AI-Native 游戏引擎

不是套用 Unity 或 Unreal——VibeGame 基于 Phaser（一个 HTML5 2D 游戏框架）自建了一套"AI 原生"表示层，满足三个属性：

**GUI-Independent（不依赖图形界面）**：游戏项目完全以结构化文本表达。每个场景的配置是 type-checked JSON，每个节点（角色、地形、UI）把外观、碰撞、脚本、配置都打包成一个有明确字段的结构体。Schema 验证可以在运行前就检测到跨文件引用错误（比如缺失的资源文件），而不是等运行时才爆。

**Runtime-Accessible（运行时可控）**：引擎暴露帧同步接口——Agent 可以暂停游戏、按帧推进、查改运行时属性（角色位置/速度）、注入语义动作（"按跳跃键"）、截图。这把一个异步实时系统变成了 Agent 可以按自己节奏检查的同步流程。

**Source-Available（引擎源码可查）**：Phaser 的完整未编译源码被复制进项目目录，Agent 遇到文档说不清楚的 API 行为时，可以直接读源码，而不是靠猜。

### 第二层：对抗性 Agent 团队（AAT）

8 个专职 Agent，分三个阶段运作：

**意图对齐（Intention Alignment）**：
- Designer 把"做一个类魂 Boss 战"展开成完整的游戏设计文档（GDD），包括机制、数值系统、关卡设计
- Artist 基于描述用图像生成模型（gpt-image-2、nano-banana-pro）生成概念图
- 用户确认后，GDD 和概念图成为后续所有开发和评估的"地面真相"

**并行开发（Parallel Development）**：
代码工作流是四 Agent 流水线：
- Architect 制定技术方案（PRD）
- Programmer 按方案实现
- Auditor 做静态审查（Schema 一致性、设计文档符合度）
- Player 通过帧同步接口实际运行游戏，用 Vision 模型判断渲染结果是否符合预期

美术工作流和设计工作流并行推进。代码子任务之间用 Git worktrees 隔离，验收后合并。

**对抗性修正（Adversarial Correction）**：
独立 Reviewer 从三个维度最终评估：功能性（游戏逻辑是否按设计运行）、视觉质量（资源完整度、风格一致性）、可玩性（操作响应、战斗反馈清晰度）。不过就重新拆成修复任务，继续循环。

实际用的模型搭配：
- Orchestrator / Artist / Architect → Claude Opus 4.7
- Designer / Programmer → Claude Sonnet 4.6
- Auditor → Claude Haiku 4.5
- Player → GPT-5.4-mini（视觉判断）
- Reviewer → GPT-5.5（最终质量门控）

### 第三层：无需训练的自进化

每个被验收的游戏项目，系统会自动提炼出三类可复用经验：

- **Skeleton（骨架）**：去掉项目特定的美术，保留代码架构、调参结果、场景流程——相当于这个游戏类型的可运行模板。同时包含 error notes（常见失败案例和修复方法）和 art pack（美术生成 prompt 和后处理规范）。

- **Module（模块）**：跨游戏类型可复用的节点脚本，可以内嵌自检逻辑，把之前遇到的运行时 Bug 转成静态验证规则，下次游戏启动时就能检测到。

- **Contract（协作契约）**：文档，把通用 AAT 工作流适配到某个特定功能的开发模式——比如地图契约规定了 Designer 怎么写地图需求、Programmer 怎么在项目文件里表示地图、Artist 提供什么资源、Auditor 和 Player 怎么验证。

这和之前分析的 WikiSkill 思路惊人相似——Skeleton 对应 Skills Layer，Module 对应 Raw Layer 中提炼出的模式，Contract 对应 Wiki Layer 的跨项目协作知识。区别在于 VibeGame 的自进化完全针对游戏开发场景，且无需任何模型微调。

---

## 演示效果：能做什么

论文展示了多个类型的游戏创作，都是从自然语言 prompt 生成完整可玩版本：

**文字输入 → Sekiro 像素 Boss 战**：输入几句规则（防御/格挡/弹刀/秒杀），系统从现有横板动作骨架出发，从头构建格挡-架势系统（架势槽、弹刀区分普通格挡、危险攻击标识），输出 12 个脚本、2 套角色资源包、11 个特效实体。

**图文输入 → 空洞骑士风格 Boss 战**：文字描述机制范围，概念图锚定视觉风格和角色设计，生成的游戏完全还原了两侧规格：Boss 依据距离切换近战/远程技能，玩家五种动作覆盖完整移动-攻击循环，命中反馈包含屏幕震动、闪光、粒子，HUD 包含面具风格血量图标和全宽 Boss 血条。

**编辑能力**：
- **IP 迁移**：保持战斗逻辑，把所有美术替换成功夫熊猫风格
- **类型迁移**：把回合制卡牌游戏改成实时 Boss 战，保留赛博朋克视觉风格
- **规则重构**：把玩家和 Boss 角色对调，各自保留原有技能和动画

---

## 怎么用

```bash
git clone https://github.com/tettethu/VibeGame
cd VibeGame
pip install -e .
```

需要配好 Claude Code 或 Codex 的 API 访问（系统支持两者作为 Agent runtime）。

然后启动 Web Dashboard：

```bash
# Chat 界面与 Agent 团队交互
# Assets 界面预览动画和调整精灵边界
# Objects 界面配置角色动画和属性
# Play 界面直接试玩正在构建的游戏
```

当前支持 Phaser 引擎的 2D 网页游戏，Godot 和 Unity 支持在 Roadmap 中。

---

## 局限性（论文自述）

- 目前没有定量评估，只有定性演示
- 只支持 2D 网页游戏，3D 扩展面临空间物理、相机控制等额外挑战
- 视觉验证仍然不完美，Vision 模型的判断可能出错，需要迭代作为安全网
- 自进化机制有"知识污染"风险：错误经验一旦被采纳会影响后续项目

---

## 为什么值得关注

VibeGame 不只是"AI 生成游戏"的又一个演示——它建立了一套可以推广的工程方法：**结构化项目表示 + 可控运行时 + 对抗性评估 + 经验自积累**。

这四件事拼在一起，才让 Agent 真正能做"持续开发"而不是"一次性生成"。这个思路对游戏以外的软件工程场景同样适用。

仓库才建了三周（2026-08-12），181 stars，还很早期，值得关注后续进展。

---

## 相关链接

- GitHub：[tettethu/VibeGame](https://github.com/tettethu/VibeGame)
- 论文：[technical_report.pdf](https://vibegame.tettet.org/technical_report.pdf)
- 项目主页：[vibegame.tettet.org](https://vibegame.tettet.org)
- 演示视频：[vibegame.tettet.org/#demos](https://vibegame.tettet.org/#demos)
- Discord：[discord.gg/Ec6d9wx8sU](https://discord.gg/Ec6d9wx8sU)

<!--EN-->

Imagine: you describe "make a Sekiro-style boss fight — player can block, deflect, and execute a deathblow" in a few sentences. A team of AI agents automatically generates the game design document, concept art, code, and physics, iterates until it's playable, then hands you a complete 2D web game.

This isn't imagination — **VibeGame** has made it real.

A joint team from Nanjing University PRLab and NTU S-Lab just released this framework. Technical report dated 2026-08-17, GitHub repo open-sourced simultaneously (Apache-2.0), built on Claude Code + Codex as agent runtimes.

---

## The Core Challenge: Why Games Are Harder Than Regular Software

LLM-based software generation is fairly mature, but game generation faces three additional problems:

1. **Project state is enormously complex**: Code, scenes, art assets, animations, and physics configs must all stay consistent. Change one thing and something else silently breaks.
2. **Correctness can only be verified by actually running**: Syntactically correct code doesn't mean the game is playable — you have to run it and test it.
3. **Continuous iteration is required**: The first playable version isn't the endpoint. Users keep requesting new mechanics, visual changes, balance tweaks — agents must make changes without breaking existing functionality.

VibeGame addresses each of these with a dedicated mechanism.

---

## Three-Layer Architecture

### Layer 1: AI-Native Game Engine

Not a wrapper around Unity or Unreal — VibeGame builds its own "AI-native" representation layer on top of Phaser (an HTML5 2D game framework), with three core properties:

**GUI-Independent**: The entire game project is expressed as structured text. Each scene's config is type-checked JSON; each node (character, terrain, UI) packages its appearance, collision, scripts, and configuration into a struct with explicit fields. Schema validation catches cross-file reference errors (like missing assets) before execution, not at runtime.

**Runtime-Accessible**: The engine exposes a frame-synchronous interface — agents can pause, step frame-by-frame, read/write runtime properties (character position/velocity), inject semantic actions ("press jump"), and capture screenshots. This converts an asynchronous real-time system into a process agents can inspect at their own pace.

**Source-Available**: Phaser's complete uncompiled source is copied into the project directory. When agents encounter API behavior the docs don't explain, they read the source directly rather than guessing.

### Layer 2: Adversarial Agent Team (AAT)

Eight specialized agents operate in three phases:

**Intention Alignment**:
- Designer expands "make a soulslike boss fight" into a full Game Design Document (mechanics, numbers, progression rules)
- Artist uses image generation (gpt-image-2, nano-banana-pro) to create concept art that anchors visual direction
- After user confirmation, the GDD and concept art become the ground truth for all downstream development and evaluation

**Parallel Development**:
Code workflow is a four-agent pipeline: Architect → Programmer → Auditor → Player. The Player actually runs the game via the frame-synchronous interface and uses a vision model to assess whether the rendered result matches intent. Git worktrees isolate parallel sub-tasks; changes merge after validation.

**Adversarial Correction**:
An independent Reviewer evaluates the complete project on three dimensions: functionality (does game logic match the spec?), visual quality (asset completeness, stylistic consistency), and playability (control responsiveness, combat feedback clarity). Failures become repair tasks that re-enter the loop.

Actual model assignments:
- Orchestrator / Artist / Architect → Claude Opus 4.7
- Designer / Programmer → Claude Sonnet 4.6
- Auditor → Claude Haiku 4.5
- Player → GPT-5.4-mini (visual judgment)
- Reviewer → GPT-5.5 (final quality gate)

### Layer 3: Training-Free Self-Evolution

Each accepted game project is automatically distilled into three forms of reusable experience:

- **Skeletons**: Project templates for a particular game type — art removed, code architecture / tuning values / scene flow preserved. Includes error notes (recurring failures + verified fixes) and an art pack (asset generation prompts and post-processing conventions).
- **Modules**: Encapsulated node scripts reusable across game types, potentially including self-checking logic that converts observed runtime failures into static validation rules.
- **Contracts**: Documents that adapt the general AAT workflow to a specific recurring feature — specifying role inputs/outputs, dependencies, and verification criteria.

This mirrors WikiSkill's thinking almost exactly: Skeletons ≈ Skills Layer, Modules ≈ distilled Raw Layer patterns, Contracts ≈ Wiki Layer cross-project knowledge. The key difference: VibeGame's self-evolution is entirely game-specific and requires zero model fine-tuning.

---

## What It Can Actually Build

**Text only → Pixel Sekiro boss fight**: A few sentences of rules (block/deflect/deathblow), starting from an existing side-scrolling skeleton, the system builds the entire deflection-posture system from scratch (posture gauges, blocking vs. frame-perfect deflection, perilous attack indicators). Output: 12 scripts, 2 character asset packs, 11 visual effect entities.

**Text + image → Hollow Knight-style boss fight**: Text specifies mechanics, concept image anchors visual identity. Delivered game realizes both: boss switches between melee/ranged based on distance, player's five actions cover the full movement-attack loop, hit feedback includes screen shake/flash/particles, HUD includes mask-style health icons and a full-width boss bar.

**Editing capabilities**:
- **IP transfer**: Keep combat logic, replace all art with Kung Fu Panda theme
- **Genre transfer**: Convert a turn-based card game to a real-time boss fight, preserving the cyberpunk visual style
- **Rule transfer**: Swap player and boss roles, each keeping their existing abilities and animations

---

## Getting Started

```bash
git clone https://github.com/tettethu/VibeGame
cd VibeGame
pip install -e .
```

Requires Claude Code or Codex API access (the system supports both as agent runtimes).

The web dashboard provides four panels: Chat (interact with the agent team), Assets (preview animations), Objects (configure character properties), and Play (playtest the game being built).

Currently supports Phaser-based 2D web games. Godot and Unity support are on the roadmap.

---

## Limitations (Self-Reported)

- No quantitative evaluation yet — only qualitative demonstrations
- 2D web games only; 3D extension faces additional challenges (spatial physics, camera, etc.)
- Visual verification is still imperfect; vision model judgments can be wrong, and iteration is the safety net
- Self-evolution carries contamination risk: incorrect experience, once adopted, affects subsequent projects

---

## Why It Matters

VibeGame isn't just another "AI generates a game" demo — it establishes a reusable engineering method: **structured project representation + controllable runtime + adversarial evaluation + accumulated experience**. These four pieces together are what allow agents to do genuine continuous development rather than one-shot generation. The pattern applies well beyond game development.

The repo launched three weeks ago (2026-08-12) with 181 stars — early days, worth watching.

---

## Links

- GitHub: [tettethu/VibeGame](https://github.com/tettethu/VibeGame)
- Technical Report: [vibegame.tettet.org/technical_report.pdf](https://vibegame.tettet.org/technical_report.pdf)
- Project Page: [vibegame.tettet.org](https://vibegame.tettet.org)
- Demos: [vibegame.tettet.org/#demos](https://vibegame.tettet.org/#demos)
- Discord: [discord.gg/Ec6d9wx8sU](https://discord.gg/Ec6d9wx8sU)
