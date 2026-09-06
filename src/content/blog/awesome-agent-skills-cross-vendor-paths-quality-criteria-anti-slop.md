---
title: "「别提交你三小时前刚做的 skill」：一份跨 8 家 agent 的策展清单，和它的四条质量判据"
titleEn: "\"Don't Submit Skills You Created Three Hours Ago\": A Cross-Vendor Curated List and Its Four Quality Criteria"
description: "1497 个 agent skill 的人工策展清单，33.8k stars，MIT，明确写着 hand-picked not AI-slop generated。真正有用的是两样东西：一张覆盖 Claude Code、Codex、Cursor、Gemini CLI、Copilot、Windsurf、OpenCode、Antigravity 八家的 skill 目录路径对照表；以及四条具体到能照着改的质量判据——描述要用 agent 能匹配的具体关键词、顶层元数据压到 100 token 以内正文控制在 500 行、不许硬编码绝对路径、不许申请全量工具权限。它的投稿须知和免责声明也值得一读。"
descriptionEn: "A hand-curated list of 1,497 agent skills — 33.8k stars, MIT, explicitly billed as hand-picked, not AI-slop generated. Two things make it genuinely useful: a table of skill directory paths across eight agents (Claude Code, Codex, Cursor, Gemini CLI, Copilot, Windsurf, OpenCode, Antigravity), and four quality criteria concrete enough to edit against — descriptions must use keywords agents can match, top-level metadata under ~100 tokens with the body under 500 lines, no hard-coded absolute paths, and no blanket tool permissions. Its submission policy and disclaimer are worth reading too."
pubDate: "2026-09-06"
updatedDate: "2026-09-06"
category: "Tech-News"
tags: ["Agent Skills", "策展", "质量标准", "Claude Code", "跨平台", "开源"]
heroImage: "../../assets/images/awesome-agent-skills-cross-vendor-paths-quality-criteria-anti-slop-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/VoltAgent/awesome-agent-skills
授权：MIT

---

## 一句话结论

**本站刚写过 awesome-copilot，说过 skill 清单类文章的边际价值在递减。这一篇能立住，是因为它给的不是清单，是两样能直接用的东西：一张八家 agent 的路径对照表，和四条具体到能照着改的质量判据。**

项目本身是 1497 个 agent skill 的人工策展合集，33.8k stars、3572 forks，MIT。它的自我定位写得很冲：

> **Hand-picked, not AI-slop generated.**（人工挑的，不是 AI 批量生成的垃圾。）

## 先给最实用的：八家的 skill 放哪儿

这张表本站读者大概率会直接用到。同一个 skill 想在不同 agent 里生效，得放进各自约定的目录：

| 工具 | 项目级路径 | 全局路径 |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` |

有两处值得注意：

- **Codex 和 Antigravity 的项目级路径都是 `.agents/skills/`**，跟 Claude Code 的 `.claude/skills/` 不同。这解释了为什么有些项目会同时存在 `.agents/` 和 `.claude/` 两个目录——前者是提交进仓库的源，后者是某个 agent 实际加载的位置。
- **Antigravity 的全局路径挂在 `~/.gemini/config/skills/` 下**，跟 Gemini CLI 的 `~/.gemini/skills/` 只差一层，很容易放错。

## 四条质量判据

这是本篇真正的干货。仓库的 "Skill Quality Standards" 给了四条，每条都具体到能拿去改自己的 skill：

**1. Description 要写成 agent 能匹配的样子**

用第三人称，说清**做什么**和**什么时候用**，关键词要具体。原文给的对比很到位：写 **"PostgreSQL migration"，不要写 "database stuff"**。

理由很直接：description 是模型判断"该不该调用我"的唯一依据。写得模糊，模型就匹配不上；模型匹配不上，这个 skill 写得再好也不会被用到。

**2. 渐进式披露要落到具体数字**

- 顶层元数据压到 **~100 token 以内**
- skill 正文保持在 **500 行以下**
- 大文档、schema 这类资源**按需加载，不要内联**

本站写过好几次渐进式披露这个概念，但很少见到有人给出可执行的数字。100 token / 500 行这两个数，比任何原则性描述都有用。

**3. 不许硬编码绝对路径**

别写 `/Users/alice/` 这种机器专属路径，用相对路径或 `$HOME` / `$PROJECT_ROOT` 这类通用变量。

这条看着基础，但恰恰是 AI 批量生成的 skill 最容易犯的错——生成时的上下文里有某台机器的路径，就直接写进去了。

**4. 工具权限要收紧**

只申请这个 skill 真正需要的工具，**别用 `"tools": ["*"]`**，依赖要显式声明。

这条有安全含义：一个只需要读文件的 skill 申请了全量工具权限，等于给了它执行命令和访问网络的能力。本站写 AgentSight 和 tnk 时反复讲过同一件事——agent 的权限边界要显式画出来，而不是默认全开。

## 它怎么对付灌水

CONTRIBUTING 里那句话写得毫不客气：

> **请不要提交你三小时前刚创建的 skill。** 我们现在专注于社区已经采用的 skill，尤其是开发团队发布、在真实使用中被验证过的。质量优先于数量。

这是个明确的**准入门槛**：不看你写得多快，看有没有人真的在用。

对照本站刚写的 awesome-copilot——那边靠的是分类学和 llms.txt 让 931 个资源可被检索；这边靠的是**收窄入口**让清单本身不膨胀。两种治理思路，针对的是同一个问题：skill 生态正在被 AI 批量生成的东西淹没。

![在窄门前伸手拦住涌来的一大片卡片：skill 已经从稀缺变成过剩，生态的关键问题从「怎么造」变成了「怎么筛」](../../assets/images/awesome-agent-skills-cross-vendor-paths-quality-criteria-anti-slop-fig-01.png)

## 它的免责声明值得一读

很多 awesome list 不说这个，它说了：

> 这是一份策展清单。列出的 skill 由各自作者和团队创建维护，**不是我们做的**。我们挑选社区已采纳、经过验证的 skill，但**不审计、不背书、不保证**其安全性或正确性。它们没有经过安全审计，**生产使用前应当自行审查**。

配合上面第 4 条（工具权限），这段话的分量就出来了：**你从任何清单里装一个 skill，本质上是在自己的 agent 里执行陌生人写的指令。** 策展降低了筛选成本，但没有也不可能替你承担审查责任。

装之前至少看一眼两件事：它申请了哪些工具权限，以及正文里有没有让 agent 去访问外部地址。

## 一点判断

坦白说，1497 个 skill 里你会用的可能不超过十个，清单本身的价值有限。**这篇值得写的是那两样跟清单无关的东西：**

1. **八家路径对照表** —— 纯实用信息，做跨 agent 分发的时候会反复查。
2. **四条质量判据** —— 100 token 元数据、500 行正文、无绝对路径、工具权限收紧。这四条可以直接拿去审自己写的 skill，跟你用哪家 agent 无关。

再加一条本站的观察：**awesome-copilot 用分类学和机器可读索引解决"太多找不到"，VoltAgent 用准入门槛解决"太多且质量差"。** 两边都是在应对同一个转折——skill 从"稀缺资源"变成了"过剩供给"，生态的关键问题从**怎么造**变成了**怎么筛**。

下一篇同类清单出现时，本站的判断标准也会是这个：它有没有拿出筛选机制，还是只是又数了一遍。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

*by Mycelium Protocol*

---

Repository: https://github.com/VoltAgent/awesome-agent-skills
License: MIT

---

## TL;DR

**We just covered awesome-copilot and said the marginal value of skill-list posts is dropping fast. This one holds up because what it offers isn't a list — it's two directly usable things: a path table across eight agents, and four quality criteria concrete enough to edit against.**

The project itself is a hand-curated collection of 1,497 agent skills — 33.8k stars, 3,572 forks, MIT. Its self-description doesn't hedge:

> **Hand-picked, not AI-slop generated.**

## The most useful part first: where skills go, per vendor

Readers here will likely use this table directly. The same skill needs to sit in a different directory for each agent to pick it up:

| Tool | Project path | Global path |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` |

Two things to watch:

- **Codex and Antigravity both use `.agents/skills/` at the project level**, unlike Claude Code's `.claude/skills/`. That explains why some repositories carry both `.agents/` and `.claude/` — the former is the committed source, the latter is where a particular agent actually loads from.
- **Antigravity's global path lives under `~/.gemini/config/skills/`**, one level off Gemini CLI's `~/.gemini/skills/`. Easy to get wrong.

## The four quality criteria

This is the substance. The repo's "Skill Quality Standards" gives four, each specific enough to apply to your own skills today:

**1. Write the description so an agent can match on it**

Third person, stating *what* it does and *when* to use it, with specific keywords. The README's own contrast lands well: write **"PostgreSQL migration," not "database stuff."**

The reasoning is direct: the description is the model's only basis for deciding whether to invoke this skill. Write it vaguely and the model won't match; if it doesn't match, the quality of everything below is irrelevant.

**2. Progressive disclosure, expressed as actual numbers**

- Top-level metadata under **~100 tokens**
- Skill body under **500 lines**
- Large docs and schemas **loaded on demand, not inlined**

We've written about progressive disclosure several times, but rarely seen anyone put executable numbers on it. Those two figures are worth more than any statement of principle.

**3. No hard-coded absolute paths**

Don't write machine-specific paths like `/Users/alice/`; use relative paths or well-known variables (`$HOME`, `$PROJECT_ROOT`).

It looks basic, and it's exactly what bulk-generated skills get wrong most often — a path from the generating machine's context ends up baked into the file.

**4. Scope the tool permissions**

Request only the tools the skill genuinely needs, **avoid blanket `"tools": ["*"]`**, and declare dependencies explicitly.

This one carries security weight: a skill that only reads files but requests every tool has just been handed command execution and network access. It's the same point we made writing about AgentSight and tnk — an agent's permission boundary should be drawn explicitly, not left wide open by default.

## How it handles the slop problem

The contributing note is blunt:

> **Please don't submit skills you created 3 hours ago.** We're now focusing on community-adopted skills, especially those published by development teams and proven in real-world usage. Quality over quantity.

That's an explicit **bar for entry**: not how fast you wrote it, but whether anyone actually uses it.

Compare with awesome-copilot from our last post: that project makes 931 resources findable through taxonomy and an llms.txt index; this one keeps the list from bloating by **narrowing the entrance**. Two governance strategies aimed at the same problem — the skill ecosystem is being flooded with bulk-generated material.

![A raised hand at a narrow gate holding back a flood of cards: skills have gone from scarce to oversupplied, and the ecosystem's key question shifted from how to make them to how to filter them](../../assets/images/awesome-agent-skills-cross-vendor-paths-quality-criteria-anti-slop-fig-01.png)

## Its disclaimer is worth reading

Most awesome lists skip this. This one doesn't:

> This is a curated list. Skills listed here are created and maintained by their respective authors and teams, **not by us**. We select community-adopted, proven skills and **do not audit, endorse, or guarantee** the security or correctness of listed projects. They are not security-audited and **should be reviewed before production use**.

Read alongside criterion 4 above, that paragraph carries real weight: **installing a skill from any list means executing a stranger's instructions inside your own agent.** Curation lowers your filtering cost; it does not and cannot assume your review responsibility.

Before installing, at minimum check two things: which tool permissions it requests, and whether the body sends the agent to any external address.

## A closing judgment

Honestly, you'll use maybe ten of the 1,497 skills, so the list itself is of limited value. **What earns this post are the two things that have nothing to do with the list:**

1. **The eight-vendor path table** — pure practical reference you'll consult repeatedly when distributing across agents.
2. **The four quality criteria** — 100-token metadata, 500-line body, no absolute paths, scoped tool permissions. Apply them to your own skills regardless of which agent you use.

One observation to add: **awesome-copilot solves "too many to find" with taxonomy and a machine-readable index; VoltAgent solves "too many and low quality" with a bar for entry.** Both are responses to the same turn — skills have gone from scarce to oversupplied, and the ecosystem's key question has shifted from *how to make them* to *how to filter them*.

When the next list of this kind appears, that's the standard we'll judge it by: does it offer a filtering mechanism, or has it merely counted again.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
