---
title: "juju-content-illustrations：一个 Agent Skill，把你的长文章变成卷卷风格手绘插画"
description: "卷卷整理研究所 × 内容插画 Skill。一句话触发，AI 自动把文章、教程、方法论转成白底轻线稿的手绘卡片——主角是白色比熊卷卷，最多生成 10 张，支持 6 种比例，颜色有语义，场景有隐喻。60 stars，MIT 开源，可装进 Claude Code 或 Codex 直接用。"
titleEn: "juju-content-illustrations: An Agent Skill That Turns Articles into Juju-Style Hand-Drawn Illustrations"
descriptionEn: "Juju Organizing Lab's content illustration skill. One trigger phrase, AI automatically converts articles, tutorials, and methodologies into white-background light-linework illustration cards featuring a white bichon named Juju. Up to 10 images, 6 aspect ratios, semantic color codes, scene metaphors. 60 stars, MIT open source, installs into Claude Code or Codex."
pubDate: 2026-06-15
category: "Tech-News"
tags: ["AgentSkill", "AI生图", "内容创作", "ClaudeCode", "插画", "手绘风格", "创作者工具", "开源", "Skill"]
lang: "zh-CN"
heroImage: "../../assets/images/juju-content-illustrations-skill-overview.jpeg"
---

> 2026-06-15 · 工具观察

如果你做过内容创作，一定有过这样的时刻：

写完一篇方法论文章，知道配一张手绘风格的图会更有传播力，但自己又不会画——找设计太慢，AI 生图又总是出来那种"商业感太强"或者"看不出重点"的结果。

[juju-content-illustrations](https://github.com/dososo/juju-content-illustrations) 是一个可以直接安装到 Claude Code 或 Codex 的 Agent Skill，专门解决这个问题：把文章内容交给它，它帮你生成卷卷风格的手绘插画——白底、轻线稿、低饱和色彩、主角是一只叫卷卷的白色比熊。

---

## 卷卷是谁

卷卷（Juju）是这个插画体系的固定主角，一只白色比熊，有几个固定的视觉特征：
- 黑色眼睛和鼻子，耳朵自然下垂
- 身体比例小巧，姿态随内容变化
- 在"纸面摄影""方法整理桌""路径地图""复盘修理铺"等不同场景里出现

它不是装饰——它是信息的载体。每张图里卷卷的动作和位置，对应内容里的一个认知动作（发现、整理、选择、复盘……）。

---

## 它能做什么

**输入**：你的文章、教程、方法论、产品说明，任何你想配图的文字内容

**输出**：1 到最多 10 张手绘风格插画

系统会根据内容密度自动判断需要多少张——简单观点出单张，长文教程出"封面 + 正文图"组合。

### 支持的 6 种比例

| 比例 | 尺寸 | 最适合 |
|------|------|--------|
| **16:9** | 1600×900 | 公众号正文图、头图 |
| **5:2** | 1600×640 | 封面横幅 |
| **3:4** | 1200×1600 | 可保存的方法卡、课程系列 |
| **1:1** | 正方形 | 头像配图、知识点卡片 |
| **4:5** | 竖版 | 小红书、Instagram |
| **9:16** | 1080×1920 | 故事帧、竖屏全幅 |

---

## 视觉语言体系

这个 Skill 有一套完整的颜色语义规范，不是随机选色：

| 颜色 | 语义 |
|------|------|
| **红色** | 修正、纠偏、注意点 |
| **蓝色** | 路径、流程、方向 |
| **绿色** | 可复用的方法、正向结果 |
| **橙色** | 行动项、待执行 |

配色之外，每张图的构图也遵循专业摄影/设计原则：中心构图、水平线、三分法、对角线、框景、重复节奏……这套规范来自项目里的构图练习套图（9 种构图方式各一张 3:4 示例）。

**文字处理**：中文直接嵌入画面，以标签、便签、箭头等形式呈现，**不做后期贴字**。

---

## 平行场景世界

内容插画不是把文字配一张"通用背景"——Juju 系统设计了几个"平行世界"：

- **纸面摄影**：白色纸张质感背景，适合方法论、复盘类内容
- **方法整理桌**：有工具、便签、物件的桌面场景，适合流程梳理
- **路径地图**：带方向感的地图隐喻，适合选择框架、决策路径
- **复盘修理铺**：修理工具和问题诊断的隐喻，适合错误分析和改进

每个场景是一套完整的视觉语言，不是单张图的背景——同一篇文章的不同部分，可以在同一个"世界"里展开，保持一致性。

---

## 如何触发

安装到 Claude Code 或 Codex 后，几种方式都可以触发：

```
使用 juju-content-illustrations 技能，给这篇文章生成插画
把这篇文章转成卷卷风格的图片
用卷卷 Skill 给以下内容配图
```

触发后，它会问你想要哪种比例，然后自动决定张数和构图方案。

如果当前环境不支持直接生图，它会生成可以复制到其他生图工具（Midjourney、Firefly 等）的 prompt。

---

## 安装方法

```bash
# 克隆仓库
git clone https://github.com/dososo/juju-content-illustrations

# 把 skill 目录放到 skills 文件夹
cp -r juju-content-illustrations/juju-content-illustrations ~/.claude/skills/
```

重启 Claude Code 后，在任何对话里触发即可。

---

## 项目信息

- **GitHub**：[dososo/juju-content-illustrations](https://github.com/dososo/juju-content-illustrations)
- **作者**：爆裂队长 NEXT（小红书）
- **创建时间**：2026-06-06（约 10 天前）
- **Stars**：60
- **许可证**：MIT（完全免费）
- **兼容**：Claude Code、Codex CLI 及任何支持 Agent Skill 格式的工具

---

## 适合谁

**最适合的内容类型**：
- 公众号方法论长文
- 小红书知识卡片
- 产品/AI 教程的配图
- 学习复盘类文章
- X 平台上需要传播力的观点图

**最适合的使用者**：
- 自己写内容但不擅长配图的创作者
- 需要快速生产视觉化内容的运营
- 想让文章"看起来更清晰"的知识类博主
- 教育/培训内容的制作者

**不太适合的场景**：
- 需要真实摄影风格配图的内容
- 品牌调性完全不同于手绘轻线稿的项目

---

## 一点补充

这个 Skill 是同一个作者（爆裂队长 NEXT）同期开源的两个项目之一，另一个是 [BLCaptain Meta Skill](https://github.com/dososo/blcaptain-meta-skill)——用于把任意工作流打包成可安装的 Agent Skill。

有意思的是，这张小红书截图里提到：**"本笔记图片由另一个开源 skill：juju-content-illustrations 生成"**——也就是说，这个 Skill 的宣传图，是这个 Skill 自己做的。这是一种自我证明的 meta 感。

---

**GitHub**：[dososo/juju-content-illustrations](https://github.com/dososo/juju-content-illustrations) · MIT · 60 stars

<!--EN-->

## juju-content-illustrations: An Agent Skill for Hand-Drawn Visual Content

An Agent Skill that converts articles, tutorials, and methodologies into Juju-style hand-drawn illustration cards. Install into Claude Code or Codex, trigger with one phrase.

**The Visual System**
- White or near-white paper background, light linework, low-saturation colors
- Juju: a white bichon with black eyes/nose, drooping ears, small proportions
- Semantic color coding: red=correction, blue=paths, green=reusable ideas, orange=action
- Chinese text embedded in images as labels/stickies/arrows (no post-processing overlay)

**6 Supported Formats**: 16:9 / 5:2 / 3:4 / 1:1 / 4:5 / 9:16

**Visual Worlds**: Paper field, method desk, route map, repair workshop — each a complete metaphor system, not just a background.

**How to Use**
```bash
git clone https://github.com/dososo/juju-content-illustrations
cp -r juju-content-illustrations/juju-content-illustrations ~/.claude/skills/
```
Then: "Use juju-content-illustrations skill to illustrate this article"

**Best For**: Long-form articles on WeChat/X, knowledge cards for Xiaohongshu, AI/product tutorials, learning retrospectives, opinion pieces.

**Meta Note**: The promotional images on Xiaohongshu for this skill were generated by the skill itself.

**GitHub**: [dososo/juju-content-illustrations](https://github.com/dososo/juju-content-illustrations) · MIT · 60 stars
