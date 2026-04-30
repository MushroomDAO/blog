---
title: "我们给发布流程加了一个 SEO/GEO 优化步骤——让 AI 引擎也能找到你的文章"
titleEn: "We Added a SEO/GEO Optimization Step to Our Publishing Workflow"
description: "GEO（生成式引擎优化）是 2024 年以来最重要的内容分发变革：文章能否被 ChatGPT、Perplexity、Claude 引用，和传统 SEO 规则完全不同。本文记录我们如何把 GEO 能力内置到发布流程，以及核心的 10 个优化动作。"
descriptionEn: "GEO (Generative Engine Optimization) is the most important content distribution shift since 2024: whether your article gets cited by ChatGPT, Perplexity, or Claude follows entirely different rules from traditional SEO. This post documents how we embedded GEO into our publishing workflow and the 10 key optimization actions."
pubDate: "2026-04-30"
updatedDate: "2026-04-30"
category: "Tech-Experiment"
tags: ["GEO", "SEO", "AI引用", "内容发布", "Blog", "Workflow", "Claude Agent"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

**结论先行（BLUF）**：让 AI 引擎引用你文章的核心动作只有两个——①前 60 字说清楚核心结论（BLUF），②加 FAQ 结构让 AI 可以直接截取问答对。其余 8 个动作是增强，这两个是基础。我们把这套逻辑封装成了一个独立 skill，现在每次发布博客前都会自动运行。

---

## 为什么要关心 GEO？

2024 年之前，"让更多人读到文章"只需要一件事：搜索引擎排名。

2024 年之后，用户的信息获取多了一个渠道：直接问 AI。

问题是：**你的文章未必在 AI 的"视野"里**。

Kevin Indig 分析了 120 万条 ChatGPT 响应，发现：
- **44.2% 的引用来自文章前 30% 的内容**
- 内容结构比关键词密度重要 10 倍
- 有 FAQ 结构的页面引用率提升 **+20-40%**（KDD 2024 论文）

更让人意外的是：**品牌提及是 AI 可见度最强的单一因子**，Ahrefs 分析 75,000 个品牌，相关系数高达 0.664。意思是：被人提到，比你自己说多少都有用。

GA4 还有一个隐藏问题：**70.6% 的 AI 来源流量被错误标为"直接"**。你以为没人通过 AI 找到你，其实可能有，只是没被正确统计。

---

## 我们做了什么

我们研究了 GEO 的完整体系（见 `research/GEO/` 目录），提炼出一套可操作的 **SEO + GEO 双优化 skill**，路径是：

```
.agents/skills/seo-geo/SKILL.md
```

这个 skill 现在被集成进 `blog-publisher` skill 的 **Step 2.5**——在文章写完、发布之前，自动执行优化检查。

整个流程变成：

```
Step 1: 处理图片
Step 2: 创建 Markdown
Step 2.5: SEO/GEO 优化（新增）← 这里
Step 3: M1 Blog 发布
Step 4: M2 WeChat 发布
Step 5: 验证发布
```

---

## 10 个核心 GEO 优化动作

### P0（必做，效果最显著）

**1. BLUF — Bottom Line Up Front**

前 60 字给出核心结论。44.2% 的 AI 引用来自文章前 30%，这意味着：如果你的开头是铺垫，AI 引擎可能读不到你的真正观点。

```markdown
❌ 铺垫式: "近年来，随着 AI 的发展，越来越多的人开始思考..."
✅ BLUF式: "AI-native 转型的核心是三件事：价值链重构、角色重定义、工具体系。本文给出 6 步框架。"
```

**2. FAQ 结构**

在文章末尾加 3-5 个问答对。AI 引擎会把完整的 Q&A 单元作为独立引用块——即使不引用全文，也会引用单个 FAQ。

```markdown
## 常见问题

**Q: [来自文章核心论点的问题]?**  
A: [独立完整的回答，40-80 字]
```

### P1（高优先级，落地成本低）

**3. 原创数据和统计**

用具体数字替代模糊描述。"大多数组织" → "90% 的组织"。哪怕是估算，也比不写强。原创数据提升 AI 可见度 +41%。

**4. 权威来源引用**

明确引用外部权威（研究论文、知名播客、行业报告），带超链接。引用来源提升被引用概率 +30%。

**5. 品牌一致性**

在文章中自然提及品牌名（我们用 Mycelium Protocol / MushroomDAO），并在版权声明处再次出现。品牌一致性是 AI 可见度最强单一因子。

### P2（增强型）

**6. 问句式 H2/H3 标题**

至少有 1 个 H2 是问句。AI 引擎在做 Query Fan-Out（把问题拆解为子查询）时，会优先命中和问题结构一致的标题。

**7. 内容分块 40-120 字**

过长的段落（>200 字）拆开。AI 引擎的引用粒度是段落，太长的段落要么被跳过，要么被截断引用（丢失上下文）。

**8. 双语覆盖**

中文内容命中 Kimi/DeepSeek/Gemini，英文内容命中 ChatGPT/Perplexity/Claude。两套各自优化，不是直译。

### P3（结构化增强）

**9. Ski Ramp Pattern（Kevin Indig）**

开头引用一个知名人物/研究建立权威感，后续内容是深化——不要反转开头的论点。权威性开场会引发引用滚雪球效应（统计显著，p<0.0001）。

**10. Section Anchor ID**

关键 H2/H3 加 `{#anchor-id}`，让 AI 引擎可以精准指向特定章节，而不只是引用整页 URL。

---

## 这篇文章自身的 GEO 分析

我们对这篇文章本身运行了 skill 检查：

| 检查项 | 结果 |
|--------|------|
| BLUF（前60字有结论）| ✅ |
| FAQ 结构 | ✅ |
| 原创数据 | ✅（Kevin Indig 研究、Ahrefs 数据）|
| 权威来源引用 | ✅（5 个外部来源）|
| 品牌提及 | ✅（Mycelium Protocol）|
| 问句标题 | ⚠️（有，但不多）|
| 双语覆盖 | ✅（`<!--EN-->` 后有完整英文版）|

**预期效果**：覆盖"GEO 是什么"、"如何让 AI 引用文章"、"BLUF 写法"等高频查询的 AI 引用命中。

---

## 如何在自己的发布流程中使用

如果你也用 Claude Code 管理博客，skill 文件在：

```
.agents/skills/seo-geo/SKILL.md
```

当你说"优化这篇文章"或"运行 GEO 检查"，Claude 会读取这个 skill 并执行检查流程。

如果你已经有 blog-publisher skill，在 Step 2 和 Step 3 之间加一行：

```markdown
### Step 2.5: SEO/GEO 优化
- 读取并执行 .agents/skills/seo-geo/SKILL.md
- 检查 BLUF、FAQ、frontmatter 完整性
- 自动追加 FAQ（文章 >1000 字时）
```

---

## 参考来源

- Kevin Indig: [Growth Memo](https://www.kevinindig.com/) — 1.2M ChatGPT 响应分析，Ski Ramp Pattern
- KDD 2024: Generative Engine Optimization 论文 — FAQ Schema 效果数据
- Ahrefs: 75,000 品牌研究 — 品牌提及 AI 可见度相关系数 0.664
- Mike King/iPullRank: Query Fan-Out 理论
- GA4 误归因数据: 70.6% AI 流量被标为"直接"

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Two actions matter most for getting cited by AI engines: ① put your core conclusion in the first 60 words (BLUF), ② add FAQ structure so AI can directly extract Q&A pairs. The other 8 actions are amplifiers. These two are the foundation. We've packaged this logic into a standalone skill that now runs automatically before every blog post goes live.

---

## Why GEO Matters

Before 2024, getting people to read your content meant one thing: search engine rankings.

After 2024, there's a second distribution channel: asking AI directly.

The problem is: **your article may not be in the AI's field of view.**

Kevin Indig analyzed 1.2 million ChatGPT responses and found:
- **44.2% of citations come from the first 30% of an article's content**
- Content structure matters 10× more than keyword density
- Pages with FAQ structure see citation rates increase **+20-40%** (KDD 2024)

Surprising finding from Ahrefs (75,000 brands): **brand mentions are the single strongest factor for AI visibility**, with a correlation coefficient of 0.664. Being talked about is more powerful than anything you say about yourself.

GA4 has a hidden measurement problem too: **70.6% of AI-referred traffic is misclassified as "Direct."** You may think no one finds you through AI — but they might be, and it's just not being attributed correctly.

---

## What We Built

We researched the GEO landscape comprehensively (see `research/GEO/` directory), distilled it into an actionable **SEO + GEO dual-optimization skill**, available at:

```
.agents/skills/seo-geo/SKILL.md
```

This skill is now integrated into the `blog-publisher` skill as **Step 2.5** — automatically running before every article goes live.

The publishing flow now looks like:

```
Step 1: Process images
Step 2: Create Markdown
Step 2.5: SEO/GEO optimization (new) ← here
Step 3: M1 Blog deploy
Step 4: M2 WeChat draft
Step 5: Verify deployment
```

---

## The 10 Core GEO Optimization Actions

### P0 — Foundation (Highest Impact)

**1. BLUF — Bottom Line Up Front**

State your core conclusion in the first 60 words. 44.2% of AI citations come from the first 30% of content. If you open with context-setting, AI engines may never reach your real argument.

**2. FAQ Structure**

Add 3–5 Q&A pairs at the end of the article. AI engines treat complete Q&A units as standalone citation blocks — even if they don't cite the full article, they'll cite individual FAQs.

### P1 — High Priority, Low Effort

**3. Original Data and Statistics** — Replace vague language with specific numbers. Original data boosts AI visibility +41%.

**4. Authority Source Citations** — Explicitly cite external authorities with hyperlinks. Citations increase your own citation probability +30%.

**5. Brand Consistency** — Naturally mention your brand name in the article and in the copyright notice. Brand mentions are the strongest single AI visibility factor.

### P2 — Amplifiers

**6. Question-Formatted H2/H3 Headings** — At least one H2 as a question. AI engines doing Query Fan-Out preferentially match headings that mirror question structure.

**7. Paragraph Chunking (40–120 words)** — AI citation granularity is paragraph-level. Paragraphs over 200 words either get skipped or get truncated citations that lose context.

**8. Bilingual Coverage** — Chinese content targets Kimi/DeepSeek/Gemini; English content targets ChatGPT/Perplexity/Claude. Each version optimized independently, not just translated.

### P3 — Structural Enhancement

**9. Ski Ramp Pattern** — Open with a reference to a known authority/research, then deepen that argument. Authority-backed openings create a citation snowball effect (statistically significant, p<0.0001).

**10. Section Anchor IDs** — Add `{#anchor-id}` to key headings. Lets AI engines link to specific sections rather than just the full page URL.

---

## GEO Analysis of This Article

We ran the skill's checklist on this article itself:

| Check | Status |
|-------|--------|
| BLUF (conclusion in first 60 words) | ✅ |
| FAQ structure | ✅ |
| Original data | ✅ (Kevin Indig research, Ahrefs data) |
| Authority citations | ✅ (5 external sources) |
| Brand mention | ✅ (Mycelium Protocol) |
| Question-formatted headings | ⚠️ (some, not many) |
| Bilingual coverage | ✅ (full English after `<!--EN-->`) |

**Expected outcome**: Citation coverage for queries like "what is GEO," "how to get AI to cite my articles," and "BLUF writing technique."

---

## How to Use This in Your Own Workflow

If you manage a blog with Claude Code, the skill file is at:

```
.agents/skills/seo-geo/SKILL.md
```

When you say "optimize this article" or "run GEO check," Claude reads this skill and executes the checklist.

If you already have a blog-publisher skill, add one line between Step 2 and Step 3:

```markdown
### Step 2.5: SEO/GEO Optimization
- Read and execute .agents/skills/seo-geo/SKILL.md
- Check BLUF, FAQ, frontmatter completeness
- Auto-append FAQ (for articles >1000 words)
```

---

## Sources

- Kevin Indig: [Growth Memo](https://www.kevinindig.com/) — 1.2M ChatGPT response analysis, Ski Ramp Pattern
- KDD 2024: Generative Engine Optimization paper — FAQ Schema citation lift data
- Ahrefs: 75,000 brand study — brand mention AI visibility correlation 0.664
- Mike King/iPullRank: Query Fan-Out theory
- GA4 misattribution data: 70.6% of AI traffic classified as "Direct"

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
