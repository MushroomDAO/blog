---
title: "act-combat-design：游戏战斗策划开源 AI Skill，46 元规则 + 70+ 游戏库，三端全兼容"
titleEn: "act-combat-design: Open-Source AI Combat Design Skill — 46 Meta-Rules, 70+ Game Library, Claude/GPT/Cursor Compatible"
description: "资深游戏战斗策划 koisama0411 开源 act-combat-design，一套项目无关的 AI 战斗设计 Skill，覆盖角色/Boss 设计、招式集、数值验证到审阅级 HTML 文档产出。内置 46 条元规则、70+ 游戏借鉴库、两个虚构示例项目，Claude Code 安装后说'设计XXX角色'即自动触发。"
descriptionEn: "Game combat designer koisama0411 open-sources act-combat-design — a project-agnostic AI skill for anime/ACT game combat design. Covers character/boss design, moveset, numerical validation, and review-grade HTML output. Ships with 46 meta-rules, 70+ game cross-reference library, and two example projects. Install in Claude Code and just say 'design character X' to trigger."
pubDate: "2026-06-28"
updatedDate: "2026-06-28"
category: "Tech-News"
tags: ["游戏开发", "战斗设计", "AI Skill", "Claude Code", "游戏策划", "开源工具", "ACT", "二次元游戏"]
heroImage: "../../assets/images/act-combat-design-ai-skill-guide-banner.jpg"
---

> **一句话定位**：一位有商业项目经验的游戏战斗策划，把自己的设计方法论和行业知识库整理成一个 AI Skill 开源了——你可以用它让 Claude / GPT / Cursor 按专业战斗策划的工作方式来做角色和 Boss 设计，而不是靠 AI 凭空发挥。

---

## 项目信息

GitHub：https://github.com/koisama0411/act-combat-design （22 ⭐，MIT 开源）

作者：koisama0411 | 邮件：koisama0411@gmail.com | 微信：HeyKoi0411

---

## 这是什么，为什么值得用

市面上 AI 辅助游戏设计的工具有不少，但 act-combat-design 做了一件其他工具通常做不到的事：

**它不替你定义战斗体系，它按你的战斗体系来工作。**

大多数 AI 设计工具（或者直接用 ChatGPT 做设计）有一个隐藏问题：AI 会把其他游戏（原神、崩铁、鸣潮……）的战斗约定默认投射进来。你说「设计一个雷属性角色」，AI 可能直接按命座体系给你出养成解锁，但你的游戏根本没有命座。

这个 Skill 的解法是 **Project-Agnostic（项目无关）**：

1. 先填 `conventions/TEMPLATE.md`，定义你项目的战斗约定——招式集有几类、视觉预警用什么规则、受击状态怎么分、帧率是多少、有没有配队/抽卡/养成……
2. AI 全程按你填的约定来工作，不从别的游戏借用假设
3. 内置了两个虚构示例项目：买断制《孤刃行》和 gacha《星澜纪》，直接参考

这个设计对两类人特别有价值：
- **在公司做商业项目的策划**：把公司内部规范填进 TEMPLATE，让 AI 按公司标准出稿
- **独立游戏开发者**：让 AI 陪你从零设计一套战斗约定，然后基于它做后续设计

---

## 知识库里有什么

这不只是一个「给 AI 看的提示词」，背后是一座真实的行业知识库：

### 方法论核心

| 内容 | 详情 |
|---|---|
| **46 条元规则** | 覆盖招式设计、节奏控制、视觉反馈、玩家预期管理等核心设计原则 |
| **5 维质量标尺** | 评判一个角色/Boss 设计是否达标的标准化框架 |
| **16 条反模式自检** | 常见设计陷阱清单，防止 AI 输出「看起来合理但实际有问题」的方案 |
| **机制创新 5 步法** | 从借鉴到创新的系统化路径 |

### 设计库

- **角色机制原型库**：从 30+ 商业游戏中抽象出的角色原型（A–E + R 分类，去项目脱敏）+ 业界 F–Q 12 种类型
- **Boss 设计范式库**：30+ 游戏中抽象出的 Boss 设计范式

### 横向知识库

- **跨游戏借鉴库**：70+ 游戏，按主题（锁定节奏、护盾机制、情绪弧线……）索引，设计特定机制时快速找参考
- **配队设计方法论 + 案例库**：适用于有配队系统的游戏
- **2024–2026 二游趋势调研**：行业现状摘要

### 工程基线（最接地气的部分）

| 基线文件 | 包含内容 |
|---|---|
| `hit-feel-tech.md` | 打击感技术参数（帧数、顿帧、特效时序……）|
| `numbers-and-progression.md` | 数值与养成公式（含验证标准）|
| `boss-ai-and-arena.md` | Boss AI 模式 + 双场战场范式 |

---

## 能产出什么

三类设计对象，都走「设计稿（评审用）+ 资源需求（落地用）」两条产出线：

### 玩家角色设计

提供**分稿**和**完整稿**两种规格：

**分稿**（战斗设计稿 + 养成效果稿分开）：
- 适合设计稿和养成稿由不同负责人/时间点交付的团队
- 样板：`output/characters/cang-lan/`（苍岚）

**完整稿**（一份 9 章全 + 三类图表）：
- 章节覆盖：核心机制、招式设计（含逐招帧数）、动作需求、特效需求、程序需求、配队推荐、养成解锁、数值建模验证
- **数值建模验证有硬标准**：必须配 5 张图表 + 三段注解（怎么算 / 为什么 / 过程 / 结果），只写表不配图视为不合格
- 输出格式：Markdown 草稿 → 确认后生成审阅级 HTML（支持 lightbox 图表查看）
- 样板：`output/characters/jin-yu/`（烬羽，延迟引爆型火术者，9 章 + 10 图）

### Boss / 怪物设计

- 阶段化框架（第一阶段 / 第二阶段 / 狂暴过渡）
- 技能详情表（含招式、帧数、伤害系数、冷却、AI 触发条件）
- AI 与连招策略（行为树逻辑、连招优先级）
- 动作 / 特效 / 程序需求清单
- 双场战范式支持
- 样板：`output/bosses/gu-ya/`（孤鸦）

### 效果与养成设计

给已有角色单独补充：
- 技能附带效果 + buff 机制设计
- 命座 / 养成物解锁（gacha 项目适用）
- 属性投放规划
- 数值建模 + 验证图表

---

## 6 步工作流程（Human-in-the-Loop 模式）

Skill 默认以人机协作方式工作，有三个确认节点不会自动跳过：

```
Phase 0：约定确认
  → 读取 conventions/ 或引导你从零填写项目战斗约定

Phase 1：采集设计输入
  → 确认：角色显示名、定位 / 角色类型、核心机制方向
  ⚠️ STOP：等你确认输入，再往下走

Phase 2：高层框架
  → 输出角色定位 + 核心机制概述 + 招式集框架
  ⚠️ STOP：等你确认方向，再展开细节

Phase 3：招式细节展开
  → 逐招展开技能描述、帧数、触发逻辑、特殊状态

Phase 4：三类需求文档
  → 动作需求 / 特效需求 / 程序需求（可分别产出）

Phase 5：整合 + 最终输出
  ⚠️ STOP：等你确认 Markdown 草稿已锁定版本
  → 生成审阅级 HTML / xlsx 资源需求表
```

如果想让 AI 全自动跑完不停下，说「产出完整版 / 全部做完不要问我」即可切换到 **Autonomous 模式**，AI 会自行决策、列出假设、标注为待审稿。

---

## 安装与使用

### Claude Code（推荐，有自动触发）

```bash
# 方式一：全局 skill（所有项目可用）
cd ~/.claude/skills/
git clone https://github.com/koisama0411/act-combat-design

# 方式二：项目级（只在当前项目可用）
cd your-project/.claude/skills/
git clone https://github.com/koisama0411/act-combat-design
```

安装后，在 Claude Code 里说以下任一关键词即**自动触发**：
- `设计 XXX 角色`
- `设计 XXX Boss`
- `做 XXX 战斗设计`
- `战斗策划专家`
- `design [character/boss] XXX`

### GPT / Claude.ai / Cursor（手动加载）

**Custom GPT**：
1. 把 `SKILL.md`、`conventions/` 下的 md、所需 `references/` 上传到 Knowledge
2. 把 USAGE.md 末尾提供的 System Prompt 填进 Instructions

**Claude.ai Projects**：
1. 新建 Project
2. 把 md 文件加入 Project knowledge
3. System Prompt 填进 Project instructions
4. 在 Project 里直接提设计需求

**Cursor**：
1. 把仓库放进工作区
2. 对话时 `@SKILL.md` 引用入口文件，AI 按需读 `references/`

### 填写项目战斗约定

这是最关键的一步——让 Skill 真正按你的项目工作：

```bash
# 复制模板
cp conventions/TEMPLATE.md conventions/my-game-conventions.md

# 打开填写（或让 AI 引导你填）
```

TEMPLATE.md 的核心字段（示例）：

```markdown
## 招式集结构
- 普攻：连段数量、衔接逻辑
- 特殊技：CD 机制、资源消耗
- 闪避 / 位移：是否有无敌帧、帧数
- 大招：触发条件、能量系统

## 视觉预警体系
- 黄色特效 = 可闪避 / 格挡
- 红色特效 = 必须闪避
- （或你项目自己的一套规则）

## 帧率
- 目标帧率：60fps / 30fps

## 配队 / 养成系统
- 是否有配队：是 / 否
- 是否有命座/星魂等解锁：是 / 否
- 养成主线：等级 / 武器 / 圣遗物 / 其他
```

---

## 自我更新（试验性功能）

Skill 有一个「越用越懂你项目」的机制：

- **默认关闭**（因为消耗额外 token）
- 开启：对 AI 说「**开启自我更新**」
- 关闭：对 AI 说「**关闭自我更新**」
- 学到的内容存入 `knowledge-local/`（**本地保留，不进 git**）
  - `self-update/`：自动捕获的可复用洞察、避坑经验、数值结论
  - `project-knowledge/`：你指定给 AI 记住的项目资料（自家公式、角色名册……）

随着项目推进，AI 会越来越熟悉你的项目具体情况，不再需要反复解释背景。

---

## 实际示例样板

仓库内置了三个完整示例，可直接参考：

**苍岚（Cang Lan）** — 分稿样板
- 路径：`output/characters/cang-lan/`
- 规格：战斗设计稿 + 养成与效果稿分开
- 适合参考分稿的文档结构和命名规范

**烬羽（Jin Yu）** — 完整稿样板
- 路径：`output/characters/jin-yu/烬羽-战斗设计及养成效果.html`
- 规格：9 章全文 + 10 张图表（含数值建模可视化）
- 描述：延迟引爆型火术者
- 适合参考完整稿的标准和 HTML 产出质量

**孤鸦（Gu Ya）** — Boss 样板
- 路径：`output/bosses/gu-ya/`
- 包含：审阅级 HTML + 落地资源需求表
- 适合参考 Boss 设计稿结构

---

## 对不同开发者的建议

### 独游开发者 / 个人项目

1. Clone 仓库到 `~/.claude/skills/`（Claude Code 用）或 Claude.ai Project
2. 打开 `上手指南.html` 先读一遍（有图文说明）
3. 让 AI 引导你从零填写 TEMPLATE.md（告诉 AI：「我在做一个 XXX 类型的游戏，帮我设计一套战斗约定」）
4. 约定填好后就可以开始设计角色/Boss

### 商业团队 / 公司项目

1. 把公司内部战斗规范转写进 TEMPLATE.md（可让 AI 帮转写）
2. 开启 `project-knowledge/`：把角色名册、公司命名规范、已有角色列表放进去
3. 让 AI 直接对接现有配置管线（Skill 输出的 JSON/xlsx 可直接喂给其他 Agent）

### 已有 AI 配置管线的团队

Skill 的产出格式设计为**可被其他 Agent 读取**：
- Markdown 草稿 → 确认后 → HTML 评审文档
- 资源需求 xlsx → 直接对接美术/程序工作流
- 如果你的配置管线已经 AI 化，可以把这里的交付物作为输入，让下游 Agent 直接进行配置工作

---

## 项目维护状态

最近一次更新（2026-06-23）：
- 新增完整角色稿模板 `blank-character-design-doc.html`（9 章 + 三类图骨架）
- 新增「烬羽」完整稿样板（9 章 + 10 图）
- 新增 4 条元规则（K 组，元规则累计 46 条）
- 明确分稿/完整稿两种规格 + 文件命名规范
- 数值建模新增硬标准（5 图 + 三段注解，是否合格有明确判定）

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **In one line**: A professional game combat designer has open-sourced their design methodology and industry knowledge base as an AI Skill — use it to make Claude/GPT/Cursor work like an actual combat designer, not just make stuff up.

---

## What Makes It Different

Most AI design tools (or raw ChatGPT sessions) carry a hidden problem: the AI projects combat conventions from other games into your design. Say "design a lightning character" and you might get a constellation unlock system — but your game doesn't have constellations.

act-combat-design solves this with a **Project-Agnostic** convention system:

1. Fill in `conventions/TEMPLATE.md` with *your* project's combat rules — moveset structure, telegraph language, hit-react states, frame rate, team model, progression system
2. The AI designs to *your* conventions, never borrowing assumptions from another game
3. Two example projects included: 《孤刃行》 (buy-to-play) and 《星澜纪》 (gacha)

---

## Knowledge Base

**Methodology:**
- 46 meta-rules (moveset design, rhythm, visual feedback, player expectation management)
- 5-dimensional quality scale
- 16 anti-pattern checklist
- 5-step mechanic innovation method

**Design Libraries:**
- Character archetype library (abstracted from 30+ commercial games)
- Boss design paradigm library (30+ games)

**Cross-game Reference:**
- 70+ game cross-reference library, indexed by mechanic theme
- Team comp methodology + case library
- 2024–2026 gacha market trend survey

**Engineering Baselines:**
- Hit-feel tech parameters (frame timing, hitstop, VFX sequencing)
- Numbers and progression formulas (with validation standards)
- Boss AI patterns + dual-arena paradigm

---

## Three Output Types

| Type | What it produces |
|---|---|
| Player character (split spec) | Combat design doc + separate progression doc |
| Player character (full spec) | 9 chapters + 3 diagram types (op/resource/numbers), all in one |
| Boss / enemy | Staged framework + skill table + AI & combo strategy + requirements |
| Effects & progression | Buff mechanics, stat delivery, numerical modeling with verified charts |

All outputs: Markdown draft → confirm → review-grade HTML + xlsx resource requirements.

---

## Install (Claude Code)

```bash
# Global install
cd ~/.claude/skills/
git clone https://github.com/koisama0411/act-combat-design

# Then in Claude Code, say:
"设计 [Character Name] 角色"   # auto-triggers
"设计 [Boss Name] Boss"
"design character [Name]"
```

For GPT/Claude.ai/Cursor: upload the `.md` files to your knowledge base, add the system prompt from `USAGE.md`.

---

## Self-Update (Experimental)

Off by default. Say "开启自我更新" to enable. The skill accumulates project-specific learnings into `knowledge-local/` (never committed to git) — the longer you use it, the better it knows your project.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution.
