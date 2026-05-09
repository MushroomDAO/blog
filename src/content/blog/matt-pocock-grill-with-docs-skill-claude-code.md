---
title: "Matt Pocock 新出的 /grill-with-docs：让 AI 真正理解你的项目语言"
titleEn: "Matt Pocock's /grill-with-docs: Make Your AI Agent Actually Understand Your Project Language"
description: "TypeScript 布道者 Matt Pocock 开源 /grill-with-docs skill，融合 /grill-me + /ubiquitous-language + 文档沉淀。AI 边问问题边实时更新 CONTEXT.md 和 ADR，让 Agent 用你项目的专属语言做设计评审。仓库 9K+ star。"
descriptionEn: "TypeScript educator Matt Pocock open-sources /grill-with-docs, merging /grill-me + /ubiquitous-language + live documentation. The AI asks questions one at a time while updating CONTEXT.md and ADRs inline, giving your agent a shared domain language for design reviews. 9K+ stars."
pubDate: "2026-05-07"
updatedDate: "2026-05-07"
category: "Tech-News"
tags: ["Claude Code", "AI Agent", "Skill", "Matt Pocock", "领域驱动", "ADR", "开源", "编程工具"]
heroImage: "../../assets/banner-human-ai-coexistence.jpg"
---

**结论先行（BLUF）**：TypeScript 圈最有影响力的技术布道者 Matt Pocock 把他用了一段时间的两个 Skill 合并成了一个——`/grill-with-docs`。它做一件事：在你开始写代码之前，逼 AI 用你项目的实际语言对你的设计方案进行严格审问，并实时把达成的共识写入文档。GitHub：`mattpocock/skills`（9K+ star）

---

## 背景：两个好 Skill，用起来有割裂感

Matt Pocock 之前发布了两个广受好评的 Skill：

- **`/grill-me`**：AI 扮演严格的审问者，针对你的方案逐一发问，暴露你没想清楚的地方
- **`/ubiquitous-language`**：建立项目专属词汇表（比如"materialization cascade"在你项目里是什么意思），让 AI 和你说同一种语言

问题是，两个 Skill 分开跑，流程不连贯：先建语言，再审问，文档还要自己另外更新。`/grill-with-docs` 把这三件事合成一个连贯动作。

---

## /grill-with-docs 做了什么

**公式**：`/grill-with-docs = /grill-me + /ubiquitous-language + 文档沉淀`

具体流程：

**① 读取 CONTEXT.md**  
这个文件记录项目的共享语言——业务里哪些词有固定含义、哪些概念不能混用。AI 先读懂这个上下文，再开始任何对话。

**② 一次一个问题的严格审问**  
AI 不会一次甩出十个问题，而是一问一等，根据你的回答继续深挖。目标是暴露设计盲点、确认依赖关系，并在实际代码里验证你的假设是否成立，而不是空谈理论。

**③ 术语冲突立即叫停**  
当你用的词和 CONTEXT.md 里的定义有出入，AI 会马上指出来，而不是默默猜测你的意思。如果遇到模糊表达，它会主动提议一个更精确的规范术语。

**④ 实时更新 CONTEXT.md 和 ADR**  
每当对话中产生新的共识，AI 会当场把词汇定义更新进 CONTEXT.md，而不是等会话结束后再批量处理。如果某个决策足够重要（难以撤销、不显而易见、有真实取舍），就自动生成一条 ADR（Architecture Decision Record）。

---

## 为什么这件事重要

AI 写代码最大的失败模式不是代码质量差，而是写出来的东西和你实际想要的不一致。根本原因：**AI 不知道你的项目在这个业务里说的"materialization"是什么意思**。

`/grill-with-docs` 解决的是对齐问题，而不是代码生成问题。在动手写代码之前，先让 AI 真正理解项目的领域语言，之后所有的命名、结构和文档注释才会和现有代码库保持一致。

Oliver Ulvebne（@therealoliuliv）在用了之后说：一开始感觉被各种问题拖慢了，但用一阵子之后觉得它反而在省时间——因为后期的清理和返工少了很多。

---

## 快速安装

```bash
npx skills@latest add mattpocock/skills
# 选择 grill-with-docs，然后执行配置
/setup-matt-pocock-skills
```

在项目根目录创建 `CONTEXT.md`，写入你的业务术语表。第一次跑 `/grill-with-docs` 时 AI 会帮你把后续内容填充进去。

---

## 常见问题

**Q：不用 CONTEXT.md 也能跑吗？**  
A：可以，但效果打折。没有 CONTEXT.md 时 AI 无法做术语校验，只是做通用的设计审问。第一次用时哪怕写几行领域词汇进去，效果差异就很明显。

**Q：ADR 会自动创建吗，还是需要手动触发？**  
A：由 AI 判断。只有符合三个条件的决策才会被记录：难以撤销、对未来读者不显而易见、存在真实的方案取舍。不是每次对话都会生成 ADR。

**Q：和直接问 Claude "你觉得这个方案怎么样"有什么区别？**  
A：结构化程度完全不同。临时提问得到的是即兴反馈，`/grill-with-docs` 得到的是基于你项目实际代码和既有语言约定的系统性审问，结论直接写入文档可供团队复用。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: TypeScript educator Matt Pocock merged two of his most popular skills into one: `/grill-with-docs`. It does one thing — before you write any code, forces the AI to rigorously question your design using your project's actual domain language, while writing the agreed-upon decisions into your docs in real time. GitHub: `mattpocock/skills` (9K+ stars)

---

## Background: Two Good Skills, One Awkward Workflow

Matt Pocock previously released two well-received skills:

- **`/grill-me`**: AI plays strict interrogator, asking pointed questions about your plan to surface gaps in your thinking
- **`/ubiquitous-language`**: Builds a project-specific vocabulary (e.g. what "materialization cascade" means in your codebase), so AI and developer share a common language

The problem: running them separately was disjointed. Build the language first, then audit, then update docs separately. `/grill-with-docs` collapses all three into one fluid session.

---

## What /grill-with-docs Does

**Formula**: `/grill-with-docs = /grill-me + /ubiquitous-language + live documentation`

**① Reads CONTEXT.md first**  
This file records the project's shared language — fixed-meaning terms, concepts that can't be conflated. The AI internalizes this context before any conversation begins.

**② One question at a time**  
No ten-question dumps. One question, wait for the answer, then go deeper based on the response. The goal is to surface design blind spots and verify assumptions against actual code — not theoretical discussion.

**③ Terminology conflicts flagged immediately**  
When your words diverge from CONTEXT.md definitions, the AI calls it out on the spot rather than silently guessing. Fuzzy language gets a proposed canonical term.

**④ CONTEXT.md and ADRs updated inline**  
Every time the conversation produces consensus, the AI writes the new definition into CONTEXT.md immediately. Decisions that are hard to reverse, non-obvious, and represent genuine trade-offs automatically generate an ADR (Architecture Decision Record).

---

## Why This Matters

The biggest failure mode in AI-assisted coding isn't poor code quality — it's misalignment. The AI doesn't know what "materialization cascade" means in your specific domain. `/grill-with-docs` solves the alignment problem before the coding problem. Once the AI understands your domain language, all naming, structure, and inline comments will stay consistent with the existing codebase.

Oliver Ulvebne (@therealoliuliv) said after using it: it felt like it slowed him down at first with all the questions, but after using it a bit he honestly thinks it saves time overall — because the clean-up and polishing afterward shrinks dramatically.

---

## Quick Start

```bash
npx skills@latest add mattpocock/skills
/setup-matt-pocock-skills
```

Create `CONTEXT.md` at your project root with a few domain terms. On the first `/grill-with-docs` run, the AI will help fill in the rest.

---

## FAQ

**Q: Does it work without CONTEXT.md?**  
A: Yes, but with reduced effectiveness. Without it, the AI skips terminology validation and just runs a generic design review. Even a few lines of domain vocabulary in CONTEXT.md makes a noticeable difference.

**Q: Are ADRs created automatically or manually triggered?**  
A: AI-decided. Only decisions meeting three criteria get recorded: hard to reverse, non-obvious to future readers, and representing a genuine trade-off between alternatives. Not every session produces an ADR.

**Q: How is this different from just asking Claude "what do you think of this plan?"**  
A: Entirely different structure. Ad-hoc feedback is improvised. `/grill-with-docs` produces systematic interrogation grounded in your actual codebase and established language conventions — with conclusions written to documentation for team reuse.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
