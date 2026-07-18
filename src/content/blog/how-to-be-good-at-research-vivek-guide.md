---
title: "如何真正做好研究：Anthropic 研究员 Vivek 的 7 条核心原则"
titleEn: "How to Be Good at Research: 7 Core Principles from an Anthropic AI Safety Researcher"
description: "Anthropic AI Safety Fellowship 研究员 Vivek 写了一篇爆款文章《How to be good at research》，500 万浏览、3 万书签。本文提炼其 7 条核心原则，并给出博士生和研究人员的具体落地建议：如何建立研究品味、如何避开主流陷阱、如何用 Claude Shannon 的方法缩小难题。"
descriptionEn: "Vivek, an Anthropic AI Safety Fellowship researcher, wrote a viral X article 'How to be good at research' — 5.4M views, 30K bookmarks. This guide distills his 7 core principles for PhD students and researchers: building research taste, avoiding the shared reading list trap, Claude Shannon's problem-shrinking method, and more."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Research"
tags: ["研究方法", "PhD", "学术", "AI安全", "Anthropic", "认知方法", "研究品味", "学习方法"]
heroImage: "../../assets/images/how-to-be-good-at-research-vivek-guide-banner.jpg"
---

> **原文来源**: 作者 Vivek (@itsreallyvivek) · Anthropic AI Safety Fellowship 研究员  
> **原文**: X/Twitter Long Article · 发布于 2026-06-10 · 5.4M 阅读 · 30,394 书签 · 12,449 赞

---

## 背景：一篇爆款研究指南

一篇发在 X/Twitter 的长文，在几天内获得 540 万阅读量和 3 万书签——这不是常见的事。

写这篇文章的 Vivek 是 Anthropic AI Safety Fellowship 的研究员，在一篇诚实的反思帖子里描述了自己的研究方法。文章的核心是**研究品味（research taste）**——这个词在学术界很常见，但很少有人说清楚它是什么、如何培养。

这篇文章试图做到这一点。

---

## 原则一：先倒着走

**原则**：拿到一个问题，先用自己的话把它复述一遍，然后定义"成功的答案"是什么样子，再开始思考。

这来自 John Schulman（OpenAI 联合创始人）的建议：**从期望的结果开始，倒着推路径**，而不是从最显眼的起点出发往前走。

大多数人处理问题的方式是：
```
问题 → 想到什么 → 开始做 → 结果
```

Schulman 建议的方式是：
```
问题 → 定义成功 → 什么路径能到成功 → 开始做
```

**对研究者的意义**：在写第一行代码、跑第一个实验之前，先写下来："这个实验成功了，应该能看到什么结果？"这个习惯会帮你避免大量无效劳动。

---

## 原则二：预测主流答案，然后想它错在哪

**原则**：预测这个问题最常见的答案是什么，然后分析这个答案遗漏了什么、错在哪里。

Vivek 把这称为锻炼**研究品味**的核心方法。

研究品味是什么？是在看到结果之前，能准确预测结果的能力。这个能力不是天生的，是通过大量的"预测 → 观察 → 对比"练出来的。

**具体练法**：
1. 读一篇新论文前，先写下你预测它的主要发现是什么
2. 读完后，对比你的预测和实际结果
3. 重点关注你预测错的地方——那是你的盲点

对主流答案的批判性思考也有另一个价值：**避免被共同的阅读列表困住**。

---

## 原则三：选基础来源，不选热门来源

**原则**：优先读经典文献和基础性工作，而不是最近的热门论文或流行观点。

这个建议出现在 AI 研究界特别重要，因为这个领域的特点是：每周都有"重磅论文"，很多"重磅"三个月后就过时了。

**共同阅读列表的陷阱**：如果所有人都在读相同的 20 篇论文，那所有人都会有相同的思维框架，做出相同类型的工作，提出相同的问题。

突破点往往来自：
- 读 10 年前、20 年前的经典
- 读相邻领域的基础文献
- 读别人不读的东西

老的证明有效的框架往往比新的热门观点更有洞察力。新的热门观点是基于老框架的，理解了老框架才能理解为什么新的有效（或无效）。

---

## 原则四：展示推理链，标出最弱的环节

**原则**：不只给出结论，要显示推理过程，并且主动标出你逻辑里最薄弱的地方。

这来自 Paul Graham 的观察：**一个想法在你脑子里感觉很完整，但当你试图写下来，漏洞就出现了**。

写作是一种发现工具，不只是表达工具。

对研究者的具体操作：
```
在写研究报告时，加一个"弱假设声明"段落：
"这个结论成立的前提是 X。如果 X 不成立，结论会如何变化？"
```

主动暴露自己推理的弱点，比被 reviewer 发现要好得多。这也是高质量研究的标志——作者知道自己的局限在哪里。

---

## 原则五：缩小问题，先做最简单版本

**原则**：把一个复杂问题缩小到它最简单的可能版本，先解决那个，再逐步加回复杂度。

这是 Claude Shannon 在 1952 年提出的研究方法：**把问题缩小到荒谬的程度，直到你能解决它为止**。

Andrej Karpathy 的版本是：**在全规模训练之前，先让模型在单个 batch 上 overfit**。这不是 hack，是一种有效的调试和理解工具。

为什么这有效？
- 复杂问题里往往混杂了多个独立的困难
- 在最简单版本上工作，可以单独隔离每个困难
- 成功解决简单版本给你信心和洞察，然后再加回复杂性

**给 PhD 学生的操作**：当你的实验不工作，先问："有没有一个更简单的版本，在这个版本上它应该工作？" 从那里开始，一步步加回复杂性。

---

## 原则六：主动寻找自己的最强反对意见

**原则**：给出答案之后，列出对自己这个答案最强的 3 个反对意见，并指出哪个是最有力的。

这是一种**对抗性的自我审查**方法。

大多数人（包括研究者）有一种心理偏见：一旦得出结论，倾向于寻找支持它的证据，而非反对它的证据（confirmation bias）。

主动寻找自己结论的漏洞，可以在对话中先于批评者找到问题，然后要么修正结论，要么做好解释准备。

**具体操作**：
```
写完一段研究结论后，用 10 分钟回答：
1. 最强的反驳是什么？
2. 这个反驳下我的结论还成立吗？
3. 如果不成立，结论应该如何修正？
```

---

## 原则七：培养「研究品味」是主业，不是副业

**原则**：持续积累对"什么是好研究"的判断力，把这当成和做研究本身同等重要的事。

综合 Vivek 文章的所有内容，这是一个贯穿始终的主题：**研究品味不是读完几篇论文就有的，而是通过持续的预测、观察、反思积累的**。

具体体现：
- **预测实验结果**（原则 2 的练习）
- **选择读什么**（原则 3 的习惯）
- **知道好研究和差研究的区别**（通过大量阅读积累）

一个有品味的研究者能在跑实验之前，大致判断这个方向是否值得追。这节省的时间比任何效率工具都多。

---

## 给中国 PhD 学生的额外一点

这篇文章的背景是英美的 AI 研究体系，但几个原则在任何研究环境下都适用。

特别需要注意的是**原则 3（选基础来源）**：在中国 AI 圈，跟热点的压力很大——什么热就追什么。但真正的研究突破往往来自读别人不读的东西，和思考别人不思考的问题。

如果你在做 AI Safety、对齐、或 interpretability 方向的研究，Vivek 的文章值得去找英文原版读（X/Twitter Article）。

---

## 总结：7 条原则速查

| # | 原则 | 核心操作 |
|---|---|---|
| 1 | 先定义成功 | 倒着推：成功是什么样，再开始 |
| 2 | 预测主流答案 | 预测最常见答案，然后找它的漏洞 |
| 3 | 选基础来源 | 读经典而非热门，避开共同阅读陷阱 |
| 4 | 展示推理链 | 标出自己推理的最弱环节 |
| 5 | 缩小问题 | 先解决最简单版本，再加复杂度 |
| 6 | 寻找反对意见 | 主动列出最强的 3 个反驳 |
| 7 | 培养研究品味 | 持续预测、观察、反思，把品味当主业 |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。  
> 基于 Vivek (@itsreallyvivek) 的 X/Twitter 文章《How to be good at research》（2026-06-10）整理

<!--EN-->

> **TL;DR**: Vivek, an Anthropic AI Safety Fellowship researcher, published a viral article "How to be good at research" (5.4M views, 30K bookmarks). This guide distills his 7 core principles into actionable guidance for PhD students and researchers. Key ideas: define success before starting, build research taste through prediction, avoid the shared reading list trap, use Claude Shannon's problem-shrinking technique.

---

## The Article's Core Thesis

Research "taste" — the ability to predict what will work before you try it — is a trainable muscle, not a natural gift. Everything in the article is about how to train it.

## 7 Core Principles

### 1. Define Success Before You Start
*From John Schulman: reason backwards from the outcome you want, not forwards from the obvious starting point.*

Before running any experiment, write: "If this succeeds, I should see ___." This forces success criteria to be explicit, preventing wasted work on experiments that can't tell you anything.

### 2. Predict the Common Answer, Then Find What It Misses
The core taste-training exercise: before reading a paper or running an experiment, predict what you'll find. Compare predictions to outcomes. Your wrong predictions reveal your blind spots.

### 3. Prioritize Foundational Sources
Shared reading lists produce shared ideas. If everyone reads the same 20 papers, everyone builds the same mental models and asks the same questions. Breakthroughs come from reading what others don't — older proven frameworks, adjacent field foundations.

### 4. Show the Reasoning Chain and Flag the Weakest Link
*From Paul Graham: an idea feels complete in your head; gaps appear when you write it down.*

Don't just present conclusions. Show the reasoning, and explicitly mark where your logic is weakest. This is how high-quality researchers write — they know their limitations before reviewers find them.

### 5. Shrink the Problem Until It's Trivial
*Claude Shannon's 1952 technique: reduce until solvable, then reintroduce complexity.*
*Karpathy's version: overfit one batch before training at scale.*

Complex problems mix multiple independent difficulties. Solving the simplest version isolates each one, builds insight, and provides a foundation to add complexity back incrementally.

### 6. List the Three Strongest Objections to Your Own Answer
Active adversarial self-review. Confirmation bias is real — once you have a conclusion, you look for supporting evidence. Explicitly searching for your strongest counterarguments finds problems before critics do.

### 7. Treat Taste-Building as Core Work
Research taste accumulates through repeated predict → observe → compare loops. A researcher with good taste can estimate — before running an experiment — whether a direction is worth pursuing. That judgment is worth more than any efficiency tool.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
> Based on Vivek (@itsreallyvivek)'s X article "How to be good at research" (2026-06-10)
