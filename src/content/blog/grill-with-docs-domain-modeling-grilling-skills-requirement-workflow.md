---
title: "需求整理三连击：grilling + domain-modeling + grill-with-docs，把模糊需求变成可执行文档"
titleEn: "The Requirements Triage Triple: grilling + domain-modeling + grill-with-docs — Turn Fuzzy Requirements into Executable Documentation"
description: "Matt Pocock 在 skills.sh 发布的三个 Claude Code Skill：grilling 负责连续追问、domain-modeling 统一项目语言、grill-with-docs 整合两者并沉淀文档。特别适合客户项目、复杂产品需求和多人协作开发。本文介绍三个 skill 的工作原理和安装方式。"
descriptionEn: "Three Claude Code skills by Matt Pocock on skills.sh: grilling for relentless interrogation, domain-modeling for unified project language, and grill-with-docs combining both with documentation output. Ideal for client projects, complex product requirements, and multi-person development."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["Claude Code", "Skill", "需求整理", "领域建模", "AI工程", "开发工作流", "Matt Pocock"]
heroImage: "../../assets/images/grill-with-docs-domain-modeling-grilling-skills-requirement-workflow-banner.jpg"
---

> **作者**：Matt Pocock（Total TypeScript 作者）
> **来源**：[skills.sh/mattpocock](https://www.skills.sh/mattpocock) · 平台安装数 11M+
> **三个 skill**：grilling · domain-modeling · grill-with-docs

---

## 一、一个你遇到过的场景

客户发来一段需求描述，里面有"用户"、"账号"、"成员"三个词交替出现，不知道是不是同一个东西。产品经理和工程师对"订单"和"交易"的理解不一样，直到联调阶段才发现。接了一个新项目，上来就写代码，两周后发现方向偏了。

这三个问题有一个共同点：**在开始执行之前，没有足够的澄清和对齐**。

Matt Pocock 在 skills.sh 上发布了三个 Claude Code Skill，专门解决这类问题。

---

## 二、三个 Skill 各自做什么

### grilling — 连续追问，逼出每一个决策

核心指令只有四句话，但执行起来很有力：

> "对当前话题进行无情追问，直到我们对每个方面都建立了共识。沿着决策树的每个分支走下去，一个接一个解决决策间的依赖关系。每次只问一个问题。能查环境的事自己查，决策是你的——我来问，你来答。"

关键设计细节：

**1. 每次只问一个问题**。一次问多个问题会让对方陷入并行思考，每个问题都答得不彻底。一次一个，等回答，再问下一个。

**2. 对每个问题给出推荐答案**。不是空洞地提问，而是"我推荐 A，理由是 X，你同意吗？"这样用户只需要确认或修正，成本低得多。

**3. 能查就不问**。代码库里有的信息（现有的 API 结构、数据库 schema、配置文件）自己去查，不占用用户的认知带宽。只把真正的决策问题摆给用户。

**4. 确认了才行动**。所有问题走完后，Claude 会总结一遍共识，用户确认后才开始执行。

触发词：`/grill`、"追问我"、"帮我想清楚这个方案"

---

### domain-modeling — 统一项目语言，沉淀成文档

这个 skill 做的是**主动改变领域模型**，而不只是读取已有的词汇表。

它维护两类文件：

**`CONTEXT.md`——领域词汇表**

```markdown
## 术语表

### Order（订单）
定义：用户完成支付后生成的记录。
区别于：Cart（购物车）是支付前的临时状态，Order 是不可变的历史记录。
代码中的体现：数据库表 `orders`，TypeScript 类型 `Order`

### Transaction（交易）
定义：一次支付行为，一个 Order 可能包含多个 Transaction（分期/补差价）。
```

**`docs/adr/`——架构决策记录（ADR）**

当你们决定"用 event sourcing 而不是直接写数据库"，这是一个值得记录的架构决策。六个月后的新成员需要知道当时为什么做这个选择，而不只是看到现在的代码。ADR 就是这类决策的档案。

格式：背景 → 决策 → 理由 → 正面后果 → 负面权衡。

触发词：`/domain`、"统一术语"、"写 ADR"、"这两个词有什么区别"

---

### grill-with-docs — 两者合一，追问即是整理

这是三个 skill 里最强的一个，也是最适合客户项目的那个。

它做三件事：

**先探索，不凭空讨论**

```bash
cat CONTEXT.md      # 看现有词汇表
ls docs/adr/        # 看现有 ADR
grep -r "class\|interface" src/ -l  # 看核心领域对象实现
```

所有讨论都扎根在现有代码里，而不是在空白上建新东西。

**追问中实时对齐术语**

发现术语混用时，不是记一个"待办"，而是**立刻暂停追问，处理术语冲突，更新 CONTEXT.md，然后继续**。澄清和文档同步进行，不留债。

**用边界情况压测每个决策**

> "如果用户中途断网，会发生什么？"
> "如果同时有 1000 个并发请求，这个设计还成立吗？"
> "如果这个字段是 null，下游怎么处理？"

每个重要的设计决策都要经过具体场景的压测，提前暴露边界情况，比上线后才发现便宜得多。

**只在值得时才写文档**

原则很克制：如果六个月后的新成员**不需要**这个文档来理解系统，就不写。文档不是越多越好，没有价值的文档只是噪音。

触发词：`/grill-docs`、"需求整理"、"帮我整理客户需求"、"审方案并出文档"

---

## 三、三个 Skill 的协作关系

```
检查方案（grilling 或 grill-with-docs 追问）
       ↓
  找出漏洞（边界情况压测）
       ↓
  统一术语（domain-modeling 更新 CONTEXT.md）
       ↓
  生成文档（ADR 记录关键决策）
```

实际使用时，大多数情况直接用 **grill-with-docs** 就够了——它已经把另外两个包含在内。

`grilling` 单独用的场景：快速澄清一个具体问题，不需要涉及文档。
`domain-modeling` 单独用的场景：已经有了方案，只需要整理术语或补一个 ADR。

---

## 四、安装

skills.sh 的 GitHub 仓库是私有的，暂时需要手动安装。原始 skill 内容可在 [skills.sh/mattpocock](https://www.skills.sh/mattpocock) 查看，或者用 `npx skills add mattpocock/grilling`（需要 skills CLI 和 GitHub 访问权限）。

本地手动安装（已完成）：

```
~/.claude/skills/grilling/SKILL.md
~/.claude/skills/domain-modeling/SKILL.md
~/.claude/skills/grill-with-docs/SKILL.md
```

安装后在任意 Claude Code 会话里说触发词即可激活对应 skill。

---

## 五、什么时候用

| 场景 | 推荐 skill |
|------|-----------|
| 接到模糊需求，需要快速澄清 | `grilling` |
| 团队里同一个概念叫法不统一 | `domain-modeling` |
| 客户项目启动会、需求整理 | `grill-with-docs` |
| 架构评审，需要记录决策 | `grill-with-docs` |
| 新成员接手老项目 | `domain-modeling`（补 CONTEXT.md）|
| 复杂功能设计，有多个方案 | `grill-with-docs`（边界情况压测）|

---

Matt Pocock 这三个 skill 的思路来自软件工程里的领域驱动设计（DDD）实践，但去掉了 DDD 的仪式感，保留了最核心的两件事：**在动手前把问题想清楚，在想清楚的同时把结论写下来**。

---

*来源：skills.sh/mattpocock，2026-07-24 采集整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Author**: Matt Pocock (Total TypeScript)
> **Source**: [skills.sh/mattpocock](https://www.skills.sh/mattpocock) · 11M+ installs on the platform
> **Three skills**: grilling · domain-modeling · grill-with-docs

---

## 1. A Scene You've Seen Before

A client sends a requirements document that alternates between "user," "account," and "member" — you have no idea if they're the same thing. The product manager and the engineer have different mental models of "order" vs. "transaction," and nobody catches it until integration testing. You start coding a new project immediately, and two weeks later you realize you went in the wrong direction.

These three problems share a root cause: **not enough clarification and alignment before execution began.**

Matt Pocock published three Claude Code skills on skills.sh that address exactly this.

---

## 2. What Each Skill Does

### grilling — Relentless interrogation until every decision is surfaced

The core instruction is four sentences, but they're precise:

> "Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. Ask the questions one at a time. If a fact can be found by exploring the environment, look it up. The decisions are mine — you ask, I answer."

Key design choices:

**One question at a time.** Multiple simultaneous questions split attention — every answer ends up shallow. One at a time, wait for the response, then ask the next.

**Provide a recommended answer for every question.** Not empty interrogation: "I'd recommend A, because X — do you agree?" The user just confirms or corrects. Far lower cognitive load.

**Look it up if you can.** Information that exists in the codebase (API structure, database schema, config files) gets fetched directly — not asked about. Only true decision points go to the user.

**Don't act until consensus is confirmed.** After all branches are walked, Claude summarizes the shared understanding. Execution begins only after the user confirms.

Trigger: `/grill`, "interview me", "help me think through this plan"

---

### domain-modeling — Unify project language, crystallize it into docs

This skill **actively changes the domain model**, rather than just consuming an existing glossary.

It maintains two file types:

**`CONTEXT.md` — the domain glossary**

```markdown
## Glossary

### Order
Definition: A record generated after the user completes payment.
Distinct from: Cart (pre-payment temporary state); Order is an immutable historical record.
In code: database table `orders`, TypeScript type `Order`

### Transaction
Definition: A single payment event. One Order may contain multiple Transactions (installments, top-ups).
```

**`docs/adr/` — Architecture Decision Records**

When you decide "use event sourcing instead of direct writes," that's a decision worth recording. A new team member six months from now needs to know *why* — not just *what* the code does. ADRs are the archive for these decisions.

Format: Background → Decision → Rationale → Positive consequences → Trade-offs.

Trigger: `/domain`, "unify terminology", "write an ADR", "what's the difference between these two terms"

---

### grill-with-docs — Both combined; the interrogation IS the documentation

This is the most powerful of the three, and the most suited for client projects.

It does three things:

**Explore first — don't discuss in a vacuum**

```bash
cat CONTEXT.md      # read existing glossary
ls docs/adr/        # read existing ADRs
grep -r "class\|interface" src/ -l  # find core domain object implementations
```

Every discussion is grounded in existing code, not built on empty air.

**Resolve terminology conflicts inline during interrogation**

When a terminology conflict appears, the skill doesn't log a "TODO" — it **pauses the interrogation, resolves the conflict, updates `CONTEXT.md`, and continues**. Clarification and documentation happen simultaneously. No accumulated debt.

**Stress-test every decision with edge cases**

> "What happens if the user loses network halfway through?"
> "Does this hold up with 1,000 concurrent requests?"
> "If this field is null, what does the downstream system do?"

Every significant design decision gets challenged with concrete scenarios. Catching these problems before launch is orders of magnitude cheaper than after.

**Only write documentation when it earns its place**

The principle is restrained: if a new team member six months from now **doesn't need** this document to understand the system, don't write it. More documentation is not always better. Documentation without value is just noise.

Trigger: `/grill-docs`, "requirements triage", "help me organize client requirements", "review this plan for gaps"

---

## 3. How the Three Skills Relate

```
Review the plan (grilling or grill-with-docs interrogation)
         ↓
    Find the gaps (edge case stress testing)
         ↓
   Unify terminology (domain-modeling updates CONTEXT.md)
         ↓
   Generate documentation (ADR records key decisions)
```

In practice, **grill-with-docs** covers most situations on its own — it already includes the other two.

Use `grilling` alone when: you need to quickly clarify one specific question without any documentation output.
Use `domain-modeling` alone when: you already have a plan and just need to tighten terminology or add an ADR.

---

## 4. Installation

skills.sh GitHub repos are private, requiring manual installation for now. The original skill content is viewable at [skills.sh/mattpocock](https://www.skills.sh/mattpocock), or via `npx skills add mattpocock/grilling` (requires skills CLI and GitHub access).

Manual local install (already done):

```
~/.claude/skills/grilling/SKILL.md
~/.claude/skills/domain-modeling/SKILL.md
~/.claude/skills/grill-with-docs/SKILL.md
```

After installation, say the trigger word in any Claude Code session to activate the corresponding skill.

---

## 5. When to Use Which

| Scenario | Recommended skill |
|----------|------------------|
| Ambiguous requirement needs fast clarification | `grilling` |
| Team using different terms for the same concept | `domain-modeling` |
| Client project kickoff, requirements triage | `grill-with-docs` |
| Architecture review, need to record decisions | `grill-with-docs` |
| New team member inheriting a legacy project | `domain-modeling` (build out CONTEXT.md) |
| Complex feature design with multiple options | `grill-with-docs` (edge case stress testing) |

---

The thinking behind these three skills draws from Domain-Driven Design (DDD) practice in software engineering — but strips away DDD's ceremony and keeps only the two things that matter most: **think clearly before acting, and write down what you figured out while you figure it out.**

---

*Source: skills.sh/mattpocock, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
