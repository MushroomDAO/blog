---
title: "LDtk：一人公司的七年，把工作方法装进免费工具"
titleEn: "LDtk: Seven Years of a One-Person Studio, Packing Craft into a Free Tool"
description: "deepnight/ldtk，MIT，4302 stars，Haxe+Electron 桌面 2D 关卡编辑器。作者 Sébastien Benard 是前 3A 主设计师（Dead Cells 等，千万销量级），现一人公司 Deepnight Games 独立开发者，LDtk 从 2019 年维护至今七年不断更新。技术上：多层类型（Tile/IntGrid/Entity/Auto-layer）、智能自动贴图规则、实体自定义、JSON 导出、Haxe API、可作为 Hide 编辑器插件嵌入。它被游戏开发者大量用于像素风和 2D 关卡设计。"
descriptionEn: "deepnight/ldtk, MIT, 4302 stars, Haxe+Electron desktop 2D level editor. Author Sébastien Benard is a former AAA lead designer (Dead Cells, tens of millions sold), now running one-person studio Deepnight Games. LDtk has been maintained since 2019 — seven continuous years. Technically: multiple layer types (Tile/IntGrid/Entity/Auto-layer), smart auto-tiling rules, entity customization, JSON export, Haxe API, Hide editor plugin support. Widely used by indie developers for pixel art and 2D level design."
pubDate: 2026-10-06
heroImage: "../../assets/images/ldtk-level-designer-toolkit-deepnight-sébastien-benard-banner.jpg"
category: "Tech-Experiment"
tags: ["游戏开发", "开发工具", "开源工具", "独立开发", "关卡设计"]
lang: "zh-CN"
wechatTitle: "LDtk：一人公司的七年免费2D关卡编辑器"
wechatDigest: "MIT 4302星；前3A主设计师；Haxe+Electron；2019至今七年维护"
---

Sébastien Benard 的职业路径在游戏行业里并不多见。

他在 Motion Twin 工作多年，是 Dead Cells 的主要设计师之一——那款游戏首发就卖出了千万份。后来他离开，成立了一人公司 Deepnight Games，开始做自己的独立游戏。然后他做了一件很多人不会做的事：把自己的工具链开源出去。

LDtk 的官网页脚写着「2019–2026」，七年了，还在更新。

GitHub: https://github.com/deepnight/ldtk | ⭐ 4302 | MIT | Haxe + Electron

---

## LDtk 是什么

**Level Designer Toolkit**——一个针对 2D 游戏的关卡编辑器，设计重点是"易用性"。

它不是 Tiled 的替代品，虽然很多人把两者对比。Tiled 更通用，接受门槛低；LDtk 更有主见，对 2D 关卡的工作流有更多内置支持，特别是在 Entity 定义和自动贴图规则上。

核心功能：

**层类型系统**
- **Tile 层**：普通贴图层，从 Tileset 里摆瓦片
- **IntGrid 层**：整数网格，用数字标注格子（比如 0=空气，1=地面，2=水），可以驱动碰撞逻辑，不需要把碰撞和视觉混在同一层
- **Entity 层**：放游戏对象（玩家起点、敌人、宝箱），每个 Entity 类型可以自定义字段（血量、AI类型、对话内容等）
- **Auto-layer**：根据 IntGrid 数据自动渲染贴图，规则可以精细调节（"左边是地面右边是空气时用这个角瓦片"）

**Entity 自定义**
Entity 的字段类型相当完整：整数、浮点数、布尔、字符串、枚举、颜色、文件引用、点、贴图区域选择等。定义好了之后编辑器里直接填值，导出 JSON 里有完整的类型数据。

**多世界支持**
一个 `.ldtk` 文件可以包含多个 World，每个 World 里有多个 Level。适合需要管理大量关卡的项目。

---

## 构建和技术栈

LDtk 的主体用 Haxe 写，打包成 Electron 桌面应用。

```bash
# 安装 Haxe 依赖
haxe setup.hxml

# 安装 Electron 依赖
cd app && npm i

# 编译 Main 进程
haxe main.debug.hxml

# 编译 Renderer 进程
haxe renderer.debug.hxml

# 启动
cd app && npm run start
```

Haxe 是一门多目标编译语言，可以同时编译到 JavaScript、C++、Java 等。LDtk 用它来统一编辑器主体逻辑，再用 Electron 套壳做桌面应用。

也可以在 **NW.js** 里运行（不需要 Electron main 进程）：
```
nw app/nwjs
```

以及作为 **Hide 编辑器插件**嵌入（Hide 是 Heaps.io 游戏引擎的编辑器）——这意味着如果你用 Heaps.io 做游戏，LDtk 可以嵌在你的主编辑器里直接用。

**导出格式**：`.ldtk` 文件本质是 JSON，有完整 schema 文档。官方提供 Haxe API（`deepnight/ldtk-haxe-api`），社区维护有 C#、Rust、Python 等多个语言绑定。

---

## 一个人维护七年

七年，对一个开源工具来说是很长的时间。大多数个人项目在 1-2 年后就进入"偶尔 commit"甚至"停更"状态。LDtk 不是这样。

这背后有一个结构性原因：LDtk 是 Sébastien 自己做游戏时用的工具，不是专门做给别人的。他在用它，所以他有动力更新它。他遇到了什么痛点，就修什么。这和"为了维护而维护"是不同的动力结构。

4302 颗星不是推广来的，是游戏开发者在用过之后告诉别人的。

---

## 职业复利

用户给了一个观察，我觉得很准确：

> 一个人职业生涯里最有复利的东西，可能不是 title 和项目流水，而是沉淀下来的工作方法和审美。这些东西装进一个免费工具里，能被几十万人天天摸到。

Sébastien 在 Motion Twin 积累的那些年，不只是做出了 Dead Cells——他同时在磨一套关卡设计工作流。那套工作流最终具化成了 LDtk：多层类型的分工逻辑、Entity 字段系统的设计决策、Auto-layer 的规则引擎……这些都是真实设计问题的产物，不是从零设计出来的。

从 3A 主设计师到一人公司工具匠人，表面上是降维，实际上是一种载体的转换：从"参与某个项目"到"影响所有用游戏工具的人"。影响范围反而更大了。

---

## 和 Tiled 的关系

用 LDtk 还是 Tiled，取决于你要做什么。

- **Tiled** 更通用，支持更多引擎（几乎所有 2D 框架都有 Tiled 导入器），功能也更杂，历史包袱更重
- **LDtk** 对 2D 游戏做了更多主观决策，IntGrid + Auto-layer 的工作流特别适合像素风 platformer 和 roguelike，Entity 字段系统更完整；但生态相对更小

两者都是 MIT 开源，都可以免费用。如果你用的引擎对两者都支持，LDtk 的现代化程度更高，值得尝试。

---

> MIT 开源。deepnight/ldtk，4302 stars，作者 Sébastien Benard（Deepnight Games），2019 年起持续维护。开源仅供学习参考。

---

<!--EN-->

## LDtk: Seven Years of a One-Person Studio, Packing Craft into a Free Tool

Sébastien Benard's career path is uncommon in the games industry.

He spent years at Motion Twin as a lead designer on Dead Cells — a game that sold tens of millions of copies. Then he left, founded one-person studio Deepnight Games, started making his own indie games, and did something most people don't: open-sourced his tooling.

LDtk's website footer reads "2019–2026." Seven years, still actively maintained.

GitHub: https://github.com/deepnight/ldtk | ⭐ 4302 | MIT | Haxe + Electron

---

### What LDtk Is

**Level Designer Toolkit** — a 2D game level editor built around usability. It's often compared to Tiled but has stronger opinions about 2D level workflows, particularly in Entity definitions and auto-tiling rules.

**Layer types:**
- **Tile layers**: place tiles from a tileset
- **IntGrid layers**: integer-tagged cells (0=air, 1=ground, 2=water) to drive collision logic independently of visuals
- **Entity layers**: game objects (spawn points, enemies, chests) with fully customizable fields (int/float/bool/string/enum/color/file/point/tileset region)
- **Auto-layers**: render tiles automatically from IntGrid data via configurable rules ("when left=ground and right=air, use this corner tile")

**Multi-world support**: one `.ldtk` file can contain multiple Worlds, each with multiple Levels — useful for large projects.

**Export**: `.ldtk` files are JSON with a full schema spec. Official Haxe API at `deepnight/ldtk-haxe-api`; community bindings for C#, Rust, Python, and others.

---

### Tech Stack

Haxe (multi-target compiled language) + Electron desktop shell. Can also run in NW.js without the Electron main process, or as a plugin embedded inside the Hide game editor (Heaps.io's editor). Build steps: install Haxe libs via `haxe setup.hxml`, install Electron deps via `npm i` in `app/`, compile main and renderer processes, then `npm run start`.

---

### Seven Years of Solo Maintenance

Most personal open-source projects enter low-activity mode within 1–2 years. LDtk hasn't. The structural reason: Sébastien uses it himself to build his own games. He's not maintaining it for others — he's maintaining it because he needs it. That's a different motivation, and it shows in consistency.

4302 stars came from developers recommending it to each other, not from marketing.

---

### Career Compound Interest

The most compounding thing in a career may not be titles or project credits — it's the accumulated craft and working methods. Those get embedded in a free tool that tens of thousands of developers touch every day.

The years at Motion Twin produced more than Dead Cells. They produced a distilled 2D level design workflow. That workflow materialized into LDtk: the layer type separation, the Entity field system design, the auto-layer rule engine — all products of solving real design problems, not abstract API design. From AAA lead designer to solo tool author looks like a step down in status. The actual influence radius went up.

---

### LDtk vs Tiled

- **Tiled**: more universal, wider engine support (almost every 2D framework has a Tiled importer), more features, more historical baggage
- **LDtk**: stronger opinions, especially the IntGrid + Auto-layer workflow for pixel platformers and roguelikes, more complete Entity field system; smaller ecosystem

Both are MIT, both free. If your engine supports both, LDtk's more modern design is worth trying.

---

> MIT. deepnight/ldtk, 4302 stars, by Sébastien Benard (Deepnight Games), maintained since 2019. For technical reference only.
