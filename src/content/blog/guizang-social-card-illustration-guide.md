---
title: "用 AI 给文章配图：归藏 Social Card Skill 完整指南"
titleEn: "AI Illustrations for Your Articles: Complete Guizang Social Card Skill Guide"
description: "归藏 Social Card Skill（4791★）是一个 Claude Code AI Skill，能把文章自动转换成小红书轮播图和微信公众号封面。本文手把手教你安装、配置，以及如何让普通文章拥有杂志级视觉配图。"
descriptionEn: "Guizang Social Card Skill (4791★) is a Claude Code AI skill that converts articles into Xiaohongshu carousel images and WeChat cover pairs. This guide walks you through installation, visual modes, and generating magazine-quality illustrations for ordinary articles."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-Experiment"
tags: ["AI配图", "小红书", "公众号", "Claude Code", "排版设计", "内容创作", "归藏", "社交媒体"]
heroImage: "../../assets/images/guizang-social-card-illustration-guide-banner.jpg"
---

写完一篇文章，最头疼的事情之一就是配图。找版权图麻烦，AI 生图出来的东西和文章内容对不上，自己做排版又要学一堆设计软件。

**归藏 Social Card Skill** 解决的就是这个问题：把你的文章文字直接扔给 AI，自动输出杂志级别的图文卡片——不需要 Figma，不需要 Canva，甚至不需要你知道什么叫"网格系统"。

GitHub: [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) | 4791★ | AGPL-3.0

---

## 它能做什么

- **小红书轮播图**（3:4 比例，1080×1440）：5-9 张成套，封面 + 内容页，适合「干货」「教程」「旅行」「产品评测」各类内容
- **微信公众号封面对**：21:9 主封面 + 1:1 方形封面，一套视觉一致的封面组合
- **文章封面图**：博客/公众号的 hero 图
- **截图美化卡片**：把 App 截图或代码截图做成好看的展示图

一个 Skill，28 种排版模板，10 套配色主题，Playwright 直接渲染输出 PNG。

---

## 两种视觉风格

这是整个工具最核心的设计决策，弄明白这两种风格，你基本上就知道怎么用了：

### Editorial（杂志叙事风）

灵感来自 *Monocle*、*Kinfolk*、*Cereal* 这类生活方式杂志。特点：

- 衬线字体 + 安静的无衬线正文
- 牛皮纸/墨迹感背景（有动态 WebGL 墨流效果可选）
- 大图 + 边注 + 引用块的杂志版式
- 6 套配色：墨色经典、靛蓝瓷、森林墨、牛皮纸、沙丘、午夜墨（暗色）

**适合**：旅行见闻、生活观察、书影评、个人随笔、有氛围感的干货

### Swiss International（国际瑞士风）

灵感来自 Helvetica 时代的平面设计。特点：

- Inter/Helvetica 大字号但极轻字重，一个高饱和强调色
- 严格的左对齐网格，细线分割，数据感
- KPI 塔、水平条形图、矩阵布局
- 4 个强调色：IKB 克莱因蓝、柠檬黄、草绿、警示橙

**适合**：AI 工具介绍、产品评测、数据对比、教程/攻略、技术干货

两种风格的选择原则很简单：**这篇文章想给人「像在读一本好书」的感觉，还是「像在看一份专业简报」的感觉？** 前者选 Editorial，后者选 Swiss。

---

## 安装

### 方法一：一行命令（推荐）

```bash
npx skills add https://github.com/op7418/guizang-social-card-skill --skill guizang-social-card-skill
```

### 方法二：告诉 AI 帮你装

在 Claude Code 里输入：

```
Install guizang-social-card-skill for me. 
Clone https://github.com/op7418/guizang-social-card-skill into ~/.claude/skills/guizang-social-card-skill, 
then verify that SKILL.md, assets/, and references/ exist.
```

### 更新

```
Update guizang-social-card-skill for me. 
Go to ~/.claude/skills/guizang-social-card-skill, run git pull, then tell me the latest commit.
```

---

## 核心依赖

Skill 需要 **Playwright** 把 HTML 渲染成 PNG，所以需要安装 Node.js 环境和 Playwright。如果你已经在用 Claude Code，Node 基本上已经有了。Playwright 装法：

```bash
npx playwright install chromium
```

---

## 基本使用——五个最常用的 prompt

### 1. 把文章做成小红书轮播图

```
把下面这篇文章做成 Swiss 风格的小红书轮播图，5 张，IKB 蓝色。

[粘贴你的文章内容]
```

### 2. 生成微信公众号封面对

```
把这篇文章的标题和摘要做成微信公众号封面对：21:9 主封面 + 1:1 方形封面，
用 Editorial 风格，Ink Classic 配色。

标题：[文章标题]
副标题：[副标题或摘要]
```

### 3. 带照片的生活类内容

```
我有 3 张旅行照片，做一套小红书图文：
- 第 1 张作为封面
- 结合照片做图文穿插
- Editorial 风格，用 Forest Ink 配色
- 目的地：泰国清迈老城区

[上传照片]
```

### 4. 干货教程类

```
把这个 AI 工具教程做成小红书卡片，Swiss 风格，6 张：
- 第 1 张：吸引人的封面
- 第 2-5 张：核心步骤
- 第 6 张：总结/CTA

[粘贴教程内容]
```

### 5. 截图展示卡片

```
帮我把这个 App 截图做成一张展示卡片，1080×1440，
Swiss 风格，Safety Orange 配色，突出核心功能区域。

[上传截图]
```

---

## 完整配色列表

**Editorial 配色（6套）**：
| 主题名 | 感觉 | 适用场景 |
|--------|------|----------|
| Ink Classic | 黑墨 + 米白 | 通用，最稳 |
| Indigo Porcelain | 靛蓝 + 白瓷 | 科技、思考类 |
| Forest Ink | 深绿 + 米白 | 自然、生活类 |
| Kraft Paper | 牛皮纸棕 | 复古、手作类 |
| Dune | 沙漠黄褐 | 旅行、户外类 |
| Midnight Ink | 深夜黑（暗色） | 游戏、电影、夜间氛围 |

**Swiss 强调色（4套）**：
| 主题名 | 颜色 | 适用场景 |
|--------|------|----------|
| IKB Klein Blue | 纯蓝 | AI 工具、技术内容 |
| Lemon Yellow | 柠檬黄 | 教育、创意类 |
| Lemon Green | 草绿 | 健康、环保类 |
| Safety Orange | 警示橙 | 重点突出、行动号召类 |

---

## 28 种排版模板速查

**Editorial 模板（M01-M16）**：

- `M01` 大图封面 + 标题
- `M02` 引用块 + 正文
- `M03` Pipeline 流程图（文字版）
- `M04` Before/After 对比
- `M05-M16` 边注、统计数字、照片墙、时间线……

**Swiss 模板（S01-S12）**：

- `S01` KPI 数字塔
- `S02` 水平条形图
- `S03` 矩阵 + Hero 图
- `S04` 特性对比卡片
- `S05-S12` 功能列表、步骤清单、标注截图……

你不需要记这些——告诉 AI 你想表达什么，它会根据内容选合适的模板。

---

## 没有图片怎么办

文章没有配套照片时，Skill 会主动问你：

> 这篇我需要 1-2 张图。三种走法：
> A. 你自己有照片/截图，传给我（推荐）
> B. 我去 Pexels / Unsplash / Flickr 帮你找
> C. 用 AI 生成

- **A（最推荐）**：自己的照片不会有「AI 感」，也不存在版权问题
- **B**：AI 会从 Pexels/Unsplash/Flickr 找图，下载到本地，并告诉你图片来源和版权情况，让你决定是否使用
- **C**：适合需要特定场景的纯图，AI 会生成几张，但生成图比自己拍的视觉效果一般更假

选 B 的时候，Pexels 支持中文关键词搜索，找国内场景特别好用。

---

## 小红书 11 类内容支持情况

Skill 做了诚实的能力圈划分，不是所有类型都适合：

**完整支持（文字 + 结构 + 图片都能搞定）**：
旅行、职场、内容推荐

**文字和结构强、需要你提供图片**：
游戏评测、影视推荐、美食食谱、美妆教程、健身、家居、穿搭（精选向）

**不在能力范围内（用了也效果差）**：
美食大片摆盘、日常 OOTD 全身照、情感氛围感、Y2K/Kawaii 装饰风格

---

## 和归藏 PPT Skill 的关系

Social Card Skill 的姐妹项目是 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)，两者共享视觉语言：

- **PPT Skill**：横向翻页演示文稿，解决「需要做 PPT/Slides」的场景
- **Social Card Skill**：静态图文卡片，解决「需要发小红书/公众号图」的场景

同一套配色体系，做完 PPT 的内容可以直接用同一套视觉语言生成社交卡，风格一致。

---

## 实际使用心得

1. **先说清楚目的地**：是小红书还是公众号封面？这决定了画布比例
2. **内容越聚焦，卡片越好看**：一张卡只讲一件事。把一篇 3000 字的文章塞进 5 张卡，每张都会很满
3. **Editorial 的留白不是 bug**：如果觉得空了，是内容本身需要拆分成更多页
4. **Swiss 风格配截图特别好用**：技术类教程 + Swiss 瑞士风 + 截图，是最稳的组合

---

## 资源链接

- [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) — 4791★, AGPL-3.0
- [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) — 姐妹项目，PPT 版本

© 2026 Author: Mycelium Protocol

<!--EN-->

## AI Illustrations for Your Articles: Complete Guizang Social Card Skill Guide

Writing is one thing; finding good images for your article is another painful problem entirely. Stock photos are hard to license, AI-generated images rarely match the content, and learning design software just to make a cover feels like overkill.

**Guizang Social Card Skill** (4791★, AGPL-3.0) solves this directly: hand it your article text, and it outputs magazine-quality image cards — no Figma, no Canva, no knowledge of grid systems required.

GitHub: [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)

---

### What It Produces

- **Xiaohongshu/Rednote carousel sets** (3:4, 1080×1440): 5-9 cards per set — cover + content pages
- **WeChat Official Account cover pairs**: 21:9 main cover + 1:1 square cover, visually consistent
- **Article hero images**: for blogs and public accounts
- **Screenshot showcase cards**: turning app/code screenshots into polished visuals

28 layout templates, 10 color themes, rendered to PNG via Playwright.

---

### Two Visual Systems

**Editorial Magazine × E-ink** — inspired by *Monocle*, *Kinfolk*, *Cereal*:
Serif display type, warm paper+ink palette, WebGL ink-flow background, ledger rows and marginalia. Best for travel, lifestyle, personal essays, film/book reviews, and atmospheric content.

**Swiss International** — inspired by Helvetica-era graphic design:
Light display at extreme sizes, single high-saturation accent, strict left-aligned grid, hairline rules. KPI towers, h-bar charts, matrix layouts. Best for AI tool reviews, product comparisons, tutorials, and data-driven content.

Pick the one that matches the feeling you want: "like reading a great magazine" (Editorial) vs. "like reading a professional brief" (Swiss).

---

### Installation

```bash
npx skills add https://github.com/op7418/guizang-social-card-skill --skill guizang-social-card-skill
```

Or tell your AI agent: *Install guizang-social-card-skill: clone https://github.com/op7418/guizang-social-card-skill into ~/.claude/skills/guizang-social-card-skill.*

You'll also need Playwright for rendering: `npx playwright install chromium`

---

### Core Prompts

```
# Swiss Xiaohongshu carousel
Make me a Swiss-style Xiaohongshu carousel from this article, 5 cards, IKB blue.

# WeChat cover pair
Turn this article's title and description into a WeChat cover pair: 21:9 + 1:1, Editorial style, Ink Classic.

# Photo-led lifestyle post
I have 3 travel photos — make a Xiaohongshu set for a Chiang Mai old city post, Editorial Forest Ink.

# Tutorial carousel
Turn this AI tool tutorial into a Xiaohongshu set, Swiss style, 6 cards.
```

---

### Resources

- [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) — 4791★
- [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) — sister project for horizontal presentations

© 2026 Author: Mycelium Protocol
