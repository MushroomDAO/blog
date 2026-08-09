---
title: "小红书运营能工作流化吗？6 个 Codex Skills 给出一个答案"
titleEn: "Can Xiaohongshu Operations Become a Workflow? Six Codex Skills Offer an Answer"
description: "《小红书运营手册 · AI工作台》是一组配合《小红书运营手册》使用的开源 Codex Skills，把标题、主页、选题、评论区、成交路径这五件高频运营动作，拆成可检查、可复用、可交给 AI 执行的工作流。本文介绍它的设计逻辑和 6 个 skill 的具体用途。"
pubDate: 2026-07-27
heroImage: "../../assets/images/xiaohongshu-operations-codex-skills-workflow-systematic-banner.jpg"
category: "Tech-Experiment"
tags: ["小红书", "Codex Skills", "内容运营", "工作流", "AI工具", "自动化"]
---

绝大多数人做小红书，靠的是灵感和感觉：今天想到什么发什么，标题临时想，主页从来不看，评论区随手回几条，不知道粉丝是怎么来的，也不知道为什么停止增长。

这种方式的天花板很低——不是因为你不够努力，而是因为**没有把运营动作变成可以检查和复用的流程**。

《小红书运营手册 · AI工作台》是一组专门解决这个问题的开源 Codex Skills。它的核心逻辑只有一句话：

> **手册负责讲判断，AI工作台负责帮你执行。**

---

## 它解决什么问题

做小红书常见的卡点不是"不会写"，而是这些：

- 标题写完才发现像正文摘要，不像标题
- 主页挂了几个月，自己说不清楚第一眼能不能看懂自己是做什么的
- 选题总是即兴想，做了十几篇也没有一个系列能持续
- 有人评论了不知道怎么回，要么太冷漠，要么回完人就消失
- 有产品但内容到转化之间没有路径，流量来了也接不住

这组 Skills 的逻辑是：**先诊断，再生成**。每个 Skill 都从"你现在的情况是什么"入手，而不是直接输出一个公式。

---

## 6 个 Skills，各管一件事

### `xiaohongshu-suite`：母 skill，路由器

不知道该从哪里开始，直接用这个。它会问你几个问题，判断你当前最需要处理的是哪个环节，然后引导你到对应的子 skill。

适合账号刚启动、或者感觉哪里都不对但不知道从哪改的情况。

### `xiaohongshu-title`：标题生成、诊断、优化

一个好标题不是正文的摘要，也不是凑热点关键词，而是让看到它的人在 0.5 秒内决定要不要点进来。

这个 skill 支持三种用法：
- **生成**：输入笔记内容，给出多个方向的标题候选
- **诊断**：输入已有标题，分析为什么点击率低、问题出在哪
- **优化**：基于诊断结果改标题，不是推翻重来，是在原有方向上精准调整

### `xiaohongshu-profile`：主页体检 + 简介改写

主页是小红书的"门面"。大多数人的简介写的是自我介绍，不是用户视角的价值说明。

这个 skill 会从四个维度检查你的主页：
1. 第一眼能不能看清楚你是谁、帮谁、解决什么
2. 简介是否有清晰的受众定位和价值承诺
3. 置顶笔记是否承担了应有的功能（引流、展示、导流）
4. 整体风格是否一致，有没有让人疑惑的信号

检查完给改写建议，不是套模板，而是基于你实际输入的内容重新组织。

### `xiaohongshu-topic-planner`：选题策划和系列规划

做内容最怕的不是没想法，而是想法之间没有连接——每篇都是孤立的，做了三十篇还是没有"系列感"，算法也难以识别。

这个 skill 做两件事：
- **选题池**：基于你的领域、受众和已有内容，规划一批可以做的选题方向
- **系列规划**：把散的选题组织成有发布顺序的内容系列，每个系列解决一个用户问题

### `xiaohongshu-comment-reply`：评论区管理

评论区是小红书里被严重低估的阵地。一条好的置顶评论能让转化率翻倍；一条冷漠或敷衍的回复能让互动率暴跌。

这个 skill 覆盖三类场景：
- **日常互动**：回复普通评论，保持真实感，不像机器人
- **处理质疑**：有边界感地应对负面评论，既不卑微也不强硬
- **引导私信**：在评论区自然地打开对话，把有意向的用户引导到私信

### `xiaohongshu-conversion-path`：成交路径设计

如果你有产品、服务、小程序或付费内容，光有流量不够——你需要一条清晰的路径：内容引发兴趣 → 主页建立信任 → 评论区产生对话 → 私信完成转化。

这个 skill 专门帮你把这条路径设计清楚：每个节点要做什么、说什么、引导去哪里。

---

## 设计原则：三个"不做"

这组 Skills 的设计里有三个明确的边界，值得单独说：

**不内置外部案例**。所有输入来自你自己的真实材料，不引用"爆款账号是怎么做的"，不拿名人语录做背书。案例会过时，方法才能复用。

**不承诺平台结果**。没有"用了涨粉"，没有"保证爆款"。它能做的是帮你把表达整理清楚、路径设计完整，结果由平台算法和用户决定。

**先诊断，后生成**。每个 skill 都从分析现状开始，而不是直接输出一个标题或简介。不诊断就生成，等于不看病就开药。

---

## 安装方式

打开 Codex，直接粘贴这一句话：

```
帮我从 GitHub 仓库 nihe0909/xiaohongshu-ai-workbench 安装全部skills
```

6 个 skills 会一次性安装完成，可以组合使用，也可以单独调用。

---

## 配套手册

Skills 解决的是执行层面的问题：怎么写标题、怎么改简介、怎么规划选题。

**判断层面的问题——为什么这样写、背后的逻辑是什么——在配套的《小红书运营手册》里**：[xiaobot.net/p/xiaohongshuku](https://xiaobot.net/p/xiaohongshuku)。

两者不是替代关系，而是分工：手册建立判断力，AI工作台帮你把判断变成行动。

---

## 适合谁

有真实产品、服务、工具、课程或经验，但在小红书总是说不清楚的人：

- 自由职业者和独立创作者
- 有小程序或工具产品的开发者
- 想把专业积累变成可持续内容的从业者
- 不想靠热点蹭流量、更想靠表达清晰积累用户的账号

如果你的目标是套公式追热点、凑爆款格式——这组 Skills 不是为这个场景设计的。

---

项目地址：[github.com/nihe0909/xiaohongshu-ai-workbench](https://github.com/nihe0909/xiaohongshu-ai-workbench)  
配套手册：[xiaobot.net/p/xiaohongshuku](https://xiaobot.net/p/xiaohongshuku)  
License：MIT

<!--EN-->

## Can Xiaohongshu Operations Be Systematized? 6 Codex Skills Offer an Answer

Most people run their Xiaohongshu (RED) accounts on instinct: post when inspiration strikes, title whatever comes to mind, never audit the profile, reply to comments haphazardly. The ceiling on this approach is low — not from lack of effort, but because **the work was never turned into repeatable, auditable workflows**.

*Xiaohongshu Operations Handbook · AI Workbench* is a set of open-source Codex Skills built to solve exactly this. Its core principle is one sentence:

> **The handbook teaches judgment. The AI workspace helps you execute.**

---

## What Problem It Solves

Common sticking points aren't "I can't write" — they're these:

- A title that reads like a paragraph summary instead of a hook
- A profile that's been live for months without a clear first-impression answer to "who do you help and how"
- Topics chosen on impulse, never building into a series
- Comments that get awkward replies or no reply, with no follow-through
- Traffic that arrives but has nowhere to go — no conversion path

Every skill in this suite follows the same discipline: **diagnose first, generate second**. It starts from "what does your current situation look like" rather than immediately outputting a formula.

---

## 6 Skills, Each Solving One Thing

### `xiaohongshu-suite`: Parent Skill, Router

Don't know where to start — use this. It asks a few questions, identifies which area needs the most attention, and routes you to the right sub-skill.

Best for: cold-start accounts, or when everything feels off and you're not sure where to begin.

### `xiaohongshu-title`: Title Generation, Diagnosis, Optimization

A good title isn't a summary of the body. It's a decision prompt that works in 0.5 seconds.

Three use modes:
- **Generate**: input your note content, get multiple title directions
- **Diagnose**: input an existing title, get analysis of why it underperforms
- **Optimize**: based on diagnosis, refine the title in-direction — not a full rewrite, a precision adjustment

### `xiaohongshu-profile`: Profile Audit + Bio Rewrite

Most bios are self-introductions. They should be value statements written from the reader's perspective.

The skill audits four dimensions:
1. Can a stranger read your profile and understand who you are, who you help, and what you solve?
2. Does your bio state a clear audience and value promise?
3. Is your pinned note doing its job (traffic capture, trust-building, conversion trigger)?
4. Is the visual and tonal language consistent?

It then produces a rewrite based on your actual inputs — not a template fill.

### `xiaohongshu-topic-planner`: Topic Strategy + Series Planning

The real risk isn't running out of ideas — it's ideas that don't connect. Thirty isolated posts never build authority; a series of eight on a single user problem does.

Two modes:
- **Topic pool**: based on your domain, audience, and existing content, map out candidate directions
- **Series planning**: organize topics into sequenced content series with a publishing order, each series solving one reader problem

### `xiaohongshu-comment-reply`: Comment Management

The comment section is one of the most underutilized growth levers. A well-crafted pinned comment can double conversion. A cold reply can flatline engagement.

Three scenarios:
- **Daily replies**: respond to regular comments with authentic tone — not robotic
- **Handling pushback**: respond to criticism with boundaries — not defensive, not apologetic
- **Private message funnel**: naturally move interested readers into DM conversation

### `xiaohongshu-conversion-path`: Conversion Path Design

Traffic alone doesn't produce revenue. You need a clear path: content creates interest → profile builds trust → comments open conversation → DMs complete conversion.

This skill maps each node: what to do, what to say, where to direct attention.

---

## Three Design Constraints

**No external case library.** All analysis is based on your actual inputs — no "here's how a viral account did it," no celebrity quotes for authority. Cases go stale; methods don't.

**No platform results guaranteed.** No "guaranteed follower growth," no "proven viral formula." What it can do: help you communicate more clearly and design a functional conversion path. What the algorithm does with that is outside the scope.

**Diagnose before generate.** Every skill begins with assessing your current situation, not jumping to output. Generating without diagnosis is prescribing without examining.

---

## Installation

Open Codex, paste this line:

```
帮我从 GitHub 仓库 nihe0909/xiaohongshu-ai-workbench 安装全部skills
```

All 6 skills install in one step. Use them individually or chain them.

---

## The Companion Handbook

The skills handle execution: how to write a title, how to rewrite a bio, how to plan topics.

**The judgment layer — why this approach, what's the underlying logic — lives in the companion handbook**: [xiaobot.net/p/xiaohongshuku](https://xiaobot.net/p/xiaohongshuku).

These aren't substitutes. They're a division of labor: the handbook builds judgment; the AI workspace turns judgment into action.

---

**Project**: [github.com/nihe0909/xiaohongshu-ai-workbench](https://github.com/nihe0909/xiaohongshu-ai-workbench)  
**Handbook**: [xiaobot.net/p/xiaohongshuku](https://xiaobot.net/p/xiaohongshuku)  
**License**: MIT
