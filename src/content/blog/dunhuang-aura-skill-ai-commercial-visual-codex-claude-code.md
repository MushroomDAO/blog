---
title: 'Dunhuang Aura Skill：把敦煌矿物美学封装成 AI Skill，装进 Codex 和 Claude Code 直出商业图'
titleEn: "Dunhuang Aura Skill: Encapsulating Dunhuang Mineral Aesthetics as an AI Skill for Codex and Claude Code"
description: "MIT 开源，不是 prompt 模板，而是完整视觉规则体系：炭黑洞窟、朱砂石绿飘带、三层景深、克制赭石金光。安装进 Codex 或 Claude Code，直接生成商业封面、电商主视觉、文章头图、多尺寸延展。106 stars。"
descriptionEn: "MIT open-source. Not a prompt template — a complete visual rule system: charcoal cave backgrounds, cinnabar and malachite ribbons, three-layer depth, restrained ochre gold light. Install in Codex or Claude Code to generate commercial covers, e-commerce visuals, article headers, multi-size extensions. 106 stars."
pubDate: "2026-09-15"
updatedDate: "2026-09-15"
category: "Tech-News"
tags: ["AI-skill", "open-source", "Dunhuang", "commercial-visual", "Claude-Code", "Codex", "image-generation", "design"]
heroImage: "../../assets/images/dunhuang-aura-skill-ai-commercial-visual-codex-claude-code-banner.jpg"
---

> 📌 开源仓库：govin-ai/dunhuang-aura-skill
> GitHub：https://github.com/govin-ai/dunhuang-aura-skill
> License：MIT | Stars：106 | Forks：23

---

大多数"敦煌风 AI 生图"是这样工作的：在 prompt 里加上"敦煌风格"或"壁画风"，然后祈祷模型能理解你想要什么。

Dunhuang Aura Skill 的做法完全不同：**把敦煌矿物美学的视觉规则逐条拆解，编码成结构化的 SKILL.md，让 Codex 或 Claude Code 在生成前先理解这套规则，再执行生图。**

结果的差异是：随机祈祷 vs. 执行规则。

---

## 一、为什么这不是 prompt 模板

普通 prompt 模板的问题：
- 描述风格，但没有约束——模型会自由发挥"敦煌元素"，结果不可控
- 不区分用途——一张商业封面和一张文章头图的构图逻辑完全不同
- 不处理衍生——同一主视觉需要出 5:2、1:1、9:16 三个尺寸时，prompt 无法保证色调和构图一致性

**Dunhuang Aura Skill 做的事**：

把决策流程前置——在开始生图之前，先评估：
1. 这张图的用途（封面/电商图/海报/主视觉）
2. 尺寸比例要求
3. 是否需要嵌入文字，嵌在哪里
4. 构图模式（横版/竖版/方图）

然后用这些判断去**约束**：调色板选择、材质表现、打光方式、敦煌元素密度、质量检查标准。

这是工程化的提示词系统，不是风格描述词。

---

## 二、视觉规则体系拆解

**背景层（炭黑洞窟）**：

主背景使用炭黑色和黑色岩石质感。这是敦煌莫高窟实际的洞窟壁面效果——不是漆黑，而是带有岩石纹理的深暗。这个基底让前景产品和中景壁画都能形成清晰的视觉对比。

**中景层（沙色壁画面板）**：

沙色矿物壁画作为中景——模拟真实壁画的矿物颜料质感，有做旧感和材质厚度，不是平涂的数字纸张色。这一层承载敦煌飞天、图案、装饰元素。

**点缀色（朱砂、石绿、石青飘带）**：

三种矿物颜料色作为点缀，用飘带形态引导视线——朱砂的暖红、石绿的冷绿、石青的深蓝，这是莫高窟实际用的矿物颜料色谱，不是泛化的"中国风"配色。

**光线处理（克制的赭石金光）**：

金光存在，但是"克制的"——不是满版金色渲染，而是局部赭石色光晕，模拟洞窟里油灯照射的氛围感。过度的金色会破坏矿物质感的沉稳。

**材质对比**：

前景产品使用现代真实材质——陶瓷、玻璃、铜器、石材——与古代壁画背景形成时代感的碰撞。这是"商业敦煌美学"区别于"文物复原"的关键：产品是现代的，美学是古典的。

**三层景深**：

| 层 | 内容 | 作用 |
|----|------|------|
| 前景 | 产品/主体 | 视觉锚点，最清晰 |
| 中景 | 壁画面板 | 文化背景，适度清晰 |
| 背景 | 洞窟/山脉 | 空间纵深，虚化处理 |

三层景深让画面有真实摄影的空间感，不是平面拼贴。

---

## 三、生成能力范围

**按用途分类**：

```
商业封面
├── 5:2 Twitter/X 长图封面
├── 文章头图（带标题文字位）
└── 活动/发布会主视觉

电商图
├── 产品主图（产品 + 敦煌背景）
├── 展示图（手机/器物放置场景）
└── 多产品对比图

延展
├── 多尺寸（5:2 / 1:1 / 9:16 / 16:9）
├── 多材质（同构图，换产品材质）
└── 局部修改（去文字、重新构图）
```

**无文字版 vs 带文字版**：

Skill 区分两种模式——无文字版用于后期排版叠字，带文字版在生成时就把标题位置和字体空间纳入构图规划，不是事后硬叠。

---

## 四、安装和使用

**Codex 安装**：

```bash
git clone https://github.com/govin-ai/dunhuang-aura-skill ~/.codex/skills/dunhuang-aura
```

**Claude Code 安装**：

```bash
git clone https://github.com/govin-ai/dunhuang-aura-skill .claude/skills/dunhuang-aura
```

安装后，在 Codex 或 Claude Code 会话里直接使用 Skill 名调用。Skill 遵循 `SKILL.md` 约定——这是 Claude Code 和 Codex 的标准 Skill 格式，装进去就能识别。

**典型调用示例**：

```
生成一张产品主视觉，产品是一款陶瓷茶杯，
尺寸 16:9，不要文字，用 dunhuang-aura 风格
```

Skill 会在执行前走决策流程：确认尺寸 → 判断无文字 → 选择陶瓷材质的前景处理方案 → 约束背景层和点缀色 → 生图。

---

## 拆解结论

这个项目有意思的地方不只是"又一个中式风格生图工具"，而是它展示了一种**把复杂审美规则工程化**的路径。

敦煌壁画的美学是有体系的——颜料、光线、构图、材质都有历史来源——Dunhuang Aura Skill 做的事是把这套体系翻译成 AI 能执行的决策规则，而不是用一两个形容词去祈祷模型自己理解。

这个方法可以迁移：赛博朋克、侘寂、包豪斯、魏晋水墨——只要能把风格规则拆解到足够具体，就能封装成 Skill。

106 stars，刚创建三天，MIT 开源。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: govin-ai/dunhuang-aura-skill
> GitHub: https://github.com/govin-ai/dunhuang-aura-skill
> License: MIT | Stars: 106 | Forks: 23

---

Most "Dunhuang-style AI image generation" works like this: add "Dunhuang style" or "mural style" to a prompt, then hope the model understands what you want.

Dunhuang Aura Skill works completely differently: **it decomposes the visual rules of Dunhuang mineral aesthetics one by one, encodes them into a structured SKILL.md, so that Codex or Claude Code understands this rule system before generating anything.**

The difference in output: random guessing vs. executing rules.

---

## I. Why This Isn't a Prompt Template

The problem with ordinary prompt templates:
- They describe a style without constraints — the model freely interprets "Dunhuang elements" with unpredictable results
- They don't distinguish use cases — a commercial cover and an article header need completely different composition logic
- They can't handle derivations — when you need 5:2, 1:1, and 9:16 versions of the same visual, a template can't guarantee consistent tone and composition across all three

**What Dunhuang Aura Skill does:**

It front-loads the decision process — before any generation begins, it evaluates:
1. The image's intended use (cover/e-commerce/poster/hero visual)
2. Aspect ratio requirements
3. Whether text needs to be embedded, and where
4. Composition mode (landscape/portrait/square)

Then uses these judgments to **constrain**: palette selection, material rendering, lighting approach, density of Dunhuang elements, quality check standards.

This is an engineered prompt system, not a style descriptor.

---

## II. Visual Rule System Breakdown

**Background layer (charcoal cave):**

The primary background uses charcoal black and black stone textures — the actual cave wall appearance of Dunhuang's Mogao Grottoes. Not pure black, but dark with rock texture. This base lets the foreground product and mid-ground murals both read clearly against it.

**Mid-ground layer (sand-colored mural panel):**

Sand-colored mineral murals serve as the middle layer — simulating the authentic mineral pigment quality of real murals, with aged character and material depth, not flat digital paper color. This layer carries the flying apsaras, patterns, and decorative elements.

**Accent colors (cinnabar, malachite, azurite ribbons):**

Three mineral pigment colors as accents, using ribbon forms to guide the eye — the warm red of cinnabar, the cool green of malachite, the deep blue of azurite. These are the actual mineral pigment colors used in the Mogao Caves, not a generalized "Chinese style" palette.

**Lighting (restrained ochre gold):**

Gold light is present, but restrained — not full-frame gold rendering, but localized ochre halos that simulate the atmosphere of lamp light inside a grotto. Excessive gold would destroy the composed quality of the mineral aesthetic.

**Material contrast:**

Foreground products use modern real materials — ceramic, glass, copper, stone — creating a temporal collision with the ancient mural background. This is what separates "commercial Dunhuang aesthetics" from "cultural relic restoration": the product is contemporary, the aesthetic is classical.

**Three-layer depth:**

| Layer | Content | Function |
|-------|---------|----------|
| Foreground | Product/subject | Visual anchor, sharpest |
| Mid-ground | Mural panel | Cultural context, moderately sharp |
| Background | Cave/mountains | Spatial depth, defocused |

Three-layer depth gives the image the spatial feel of real photography, not flat collage.

---

## III. Generation Capabilities

**By use case:**

```
Commercial covers
├── 5:2 Twitter/X long covers
├── Article headers (with title text zone)
└── Event/launch primary visuals

E-commerce
├── Product hero shots (product + Dunhuang background)
├── Showcase imagery (phone/object placement scenes)
└── Multi-product comparison images

Extensions
├── Multi-size (5:2 / 1:1 / 9:16 / 16:9)
├── Multi-material (same composition, different product materials)
└── Local modifications (remove text, rebalance composition)
```

**Text-free vs. text-embedded:**

The skill distinguishes two modes — text-free for later typographic overlay, text-embedded where title placement and typography space are planned into the composition from the start rather than forced on top afterwards.

---

## IV. Installation and Use

**Codex:**

```bash
git clone https://github.com/govin-ai/dunhuang-aura-skill ~/.codex/skills/dunhuang-aura
```

**Claude Code:**

```bash
git clone https://github.com/govin-ai/dunhuang-aura-skill .claude/skills/dunhuang-aura
```

After installation, invoke the Skill by name in a Codex or Claude Code session. The skill follows the `SKILL.md` convention — the standard skill format for both tools. Install and it's recognized.

**Typical invocation:**

```
Generate a product hero visual for a ceramic teacup,
16:9 aspect ratio, no text, using dunhuang-aura style
```

The skill runs its decision process first: confirm dimensions → identify no-text mode → select ceramic-appropriate foreground treatment → constrain background layer and accent colors → generate.

---

## Teardown Summary

What's interesting about this project isn't just "another Chinese-style image tool" — it demonstrates a path for **engineering complex aesthetic rules**.

Dunhuang mural aesthetics have a real system: pigments, lighting, composition, materials all have historical grounding. Dunhuang Aura Skill translates that system into decision rules an AI can execute, rather than hoping two adjectives are enough for the model to understand.

The method is transferable: cyberpunk, wabi-sabi, Bauhaus, Wei-Jin ink painting — any aesthetic that can be decomposed into specific rules can be packaged as a Skill.

106 stars, created three days ago, MIT open-source.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
