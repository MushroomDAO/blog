---
title: "一个 5 行的 skill，和 Anthropic 那四个容易搞混的插件仓库"
titleEn: "A Five-Line Skill, and Anthropic's Four Easily-Confused Plugin Repositories"
description: "网上流传「Anthropic 公开了内部员工高频使用的 Claude Code Skill——ELI5」。回查一手源：它确实存在，但不在官方 skills 仓库，而在社区插件市场 anthropics/claude-plugins-community，署名作者 Thariq Shihipar，MIT。「内部员工高频使用」这个说法找不到一手依据。顺着这条线把 Anthropic 的四个插件/skill 仓库理清楚：skills（19 个 Agent Skills）、claude-plugins-official（官方目录）、knowledge-work-plugins（按职能分的 Cowork 插件）、claude-plugins-community（社区提交、目前 4 个）。而 ELI5 本身的 SKILL.md 只有 5 行——这才是它真正值得看的地方。"
descriptionEn: "A widely shared claim: 'Anthropic released ELI5, a Claude Code Skill its own staff use constantly.' Checking the primary source: the skill exists, but not in the official skills repository — it lives in the community plugin marketplace anthropics/claude-plugins-community, credited to Thariq Shihipar under MIT. The 'used constantly by staff' part has no primary source behind it. Following that thread clarifies Anthropic's four plugin/skill repositories: skills (19 Agent Skills), claude-plugins-official, knowledge-work-plugins (Cowork plugins organized by job function), and claude-plugins-community (4 plugins today). And ELI5's own SKILL.md is five lines long — which is the genuinely interesting part."
pubDate: "2026-09-06"
updatedDate: "2026-09-06"
category: "Tech-News"
tags: ["Claude Code", "Agent Skills", "插件市场", "Anthropic", "一手源核查", "极简设计"]
heroImage: "../../assets/images/anthropic-plugin-marketplaces-four-repos-eli5-minimal-skill-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

ELI5 源码：https://github.com/anthropics/claude-plugins-community/tree/main/eli5
社区插件市场：https://github.com/anthropics/claude-plugins-community
官方插件目录：https://github.com/anthropics/claude-plugins-official
Agent Skills 仓库：https://github.com/anthropics/skills
知识工作插件：https://github.com/anthropics/knowledge-work-plugins
授权：MIT（ELI5），署名作者 Thariq Shihipar

---

## 一句话结论

**这篇的起点是一条网上流传的说法，落点是一张把四个仓库理清楚的表。**

流传的说法是："Anthropic 最近公开了一款内部员工高频使用的 Claude Code Skill——ELI5。" 回查一手源的结果是：**skill 确实存在，但位置和性质跟传闻不一样，而"内部员工高频使用"这半句找不到任何一手依据。**

至于 ELI5 本身——它的 `SKILL.md` **一共 5 行**。这反而是它最值得看的地方。

## 先核实

第一次查的时候我查错了地方，也得出了错误结论：在 `anthropics/skills`（官方 Agent Skills 仓库，17.4 万 stars）的 `skills/` 目录下**没有 eli5**，那里只有 19 个：academy-guide、algorithmic-art、brand-guidelines、canvas-design、claude-api、discernment-nudge、doc-coauthoring、docx、frontend-design、internal-comms、mcp-builder、pdf、pptx、skill-creator、slack-gif-creator、theme-factory、web-artifacts-builder、webapp-testing、xlsx。

换个仓库找就有了：它在 **`anthropics/claude-plugins-community`**，路径是 `eli5/skills/eli5/SKILL.md`。

这个仓库自己的定位写得很清楚：

> **社区贡献**的、面向 Claude Cowork 和 Claude Code 的插件。本仓库是社区插件市场的**只读镜像**，每晚从 Anthropic 的内部审核流水线同步。列在这里的每个插件都经由 claude.ai 提交、通过自动安全扫描、并获批分发。

所以准确的表述是：**ELI5 是一个社区提交、经 Anthropic 审核批准分发的插件**，不是 Anthropic 官方出品，`plugin.json` 里署名作者是 Thariq Shihipar，MIT，v1.0.0。

"内部员工高频使用"这半句，在仓库、README、plugin.json 里都没有对应说法。它可能是真的，但**没有一手证据**——本站的规则是这种情况就照实说，不替传闻背书。

## 四个仓库，各是什么

顺着这条线查下去，发现 Anthropic 的插件/skill 生态其实分在**四个仓库**里，名字相近，用途完全不同。这可能是很多人搞混的根源：

| 仓库 | stars | 是什么 | 里面有什么 |
|---|---:|---|---|
| **anthropics/skills** | 17.4 万 | **Agent Skills** 本体，配套 spec 和模板 | 19 个：docx / pdf / pptx / xlsx、mcp-builder、skill-creator、canvas-design、frontend-design、webapp-testing、brand-guidelines… |
| **anthropics/claude-plugins-official** | 3.59 万 | **官方管理**的高质量 Claude Code 插件目录 | `plugins/` 和 `external_plugins/` 两类 |
| **anthropics/knowledge-work-plugins** | 2.39 万 | 面向**知识工作者**的 Cowork 插件，**按职能分类** | bio-research、customer-support、data、design、engineering、enterprise-search、finance、human-resources、legal、marketing、operations、product-management、sales、small-business… |
| **anthropics/claude-plugins-community** | 3,479 | **社区提交**、经安全扫描审核的插件 | 目前只有 4 个：**eli5**、quickdesign、testdino、tres-finance-plugin |

几条实用推论：

- 要找**文档处理、建 MCP、写 skill** 这类基础能力，去 `anthropics/skills`。
- 要找**按岗位组织**的能力包（法务、财务、HR、销售），去 `knowledge-work-plugins`——这个仓库的分类方式很值得看一眼，它本质上是把 Cowork 的目标用户按职能切了一遍。
- 社区市场目前**只有 4 个插件**。3479 stars 对 4 个插件来说很高，说明关注度远超供给——这个市场还非常早期。

安装方式（社区市场）：

```bash
claude plugin marketplace add anthropics/claude-plugins-community
claude plugin install eli5@claude-community
```

有一条流程细节值得注意：**直接对这个仓库提 PR 会被自动关闭**，所有变更都从内部审核流水线流过来，提交入口是 `clau.de/plugin-directory-submission`。也就是说这个"社区市场"是**有守门人的**——经过自动安全扫描和审批。对使用者是好事，对想贡献的人则意味着走表单而不是走 GitHub。

## 那 5 行是什么样

完整的 `SKILL.md`，一个字没删：

```markdown
---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS
```

README 也只有八行，示例就一句 `/eli5 how does DNS work`。

## 为什么 5 行反而是重点

本站写过好几篇 Agent Skills 相关的文章，讨论过渐进式披露标准、skill 灌水、skill 市场。ELI5 提供了一个反方向的样本：**一个被官方审核通过、放进分发市场的 skill，可以只有一句话的指令。**

它做对了三件事：

1. **`description` 写清了触发条件，而不是复述功能。** "Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer" —— 这是给模型判断"什么时候该用我"的信息。很多 skill 的 description 写成了功能介绍，模型看完仍然不知道何时该调用。
2. **正文只约束"输出成什么形态"**：HTML artifact、大图、少字。**不规定怎么想、不给模板、不列步骤**——那些交给模型。
3. **一个 skill 只干一件事。** 没有配置项，没有模式选择，没有可选参数。

对照本站发过的那些动辄几百行、带一堆 references 和 checklist 的 skill，这里有个值得记的判断：**skill 的长度应该取决于模型不知道的东西有多少，而不是取决于任务有多重要。** 模型本来就会"用大白话解释"和"生成 HTML artifact"，那么这个 skill 需要补的信息就只剩"什么时候做"和"做成什么样"——五行足够了。

反过来说，**如果一个 skill 很长，长的部分应该是模型确实不知道的东西**：你们团队的内部约定、某个 API 的怪癖、某个流程里踩过的坑。把模型已经会的东西再写一遍，是在浪费上下文。

![一摞纸和一张纸摆在一起：skill 该写多长取决于模型不知道多少，而不是这件事有多重要；长的部分该是团队约定、API 怪癖、踩过的坑](../../assets/images/anthropic-plugin-marketplaces-four-repos-eli5-minimal-skill-fig-01.png)

## 一点判断

这篇本来只是核实一条 X 上的传闻。核实的结论是传闻**半真半假**——skill 是真的，"官方出品+内部高频使用"是加戏。

但顺着查下去的收获比原本的选题大：**Anthropic 的插件生态分在四个名字相近的仓库里，各有各的定位和准入门槛**，而社区市场目前只有 4 个插件。知道去哪儿找，比知道某一个 skill 有用得多。

至于 ELI5 本身，值得装一个——不是因为它多强，而是因为它是个好的**反面参照**：下次你写 skill 写到第三百行的时候，回头看看这五行，问问自己有多少是模型本来就会的。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

*by Mycelium Protocol*

---

ELI5 source: https://github.com/anthropics/claude-plugins-community/tree/main/eli5
Community marketplace: https://github.com/anthropics/claude-plugins-community
Official plugin directory: https://github.com/anthropics/claude-plugins-official
Agent Skills repository: https://github.com/anthropics/skills
Knowledge-work plugins: https://github.com/anthropics/knowledge-work-plugins
License: MIT (ELI5), credited to Thariq Shihipar

---

## TL;DR

**This post starts with a claim circulating online and ends with a table that sorts out four repositories.**

The claim: "Anthropic just released ELI5, a Claude Code Skill its own staff use constantly." Checking the primary source: **the skill is real, but its location and nature differ from the claim, and the "staff use it constantly" half has no primary source at all.**

As for ELI5 itself — its `SKILL.md` is **five lines long**. That turns out to be the interesting part.

## Verifying first

My first check looked in the wrong place and reached a wrong conclusion: `anthropics/skills` (the official Agent Skills repository, 174k stars) has **no eli5** under `skills/`. It holds 19: academy-guide, algorithmic-art, brand-guidelines, canvas-design, claude-api, discernment-nudge, doc-coauthoring, docx, frontend-design, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing, xlsx.

A different repository has it: **`anthropics/claude-plugins-community`**, at `eli5/skills/eli5/SKILL.md`.

That repository states its own nature plainly:

> **Community-contributed** plugins for Claude Cowork and Claude Code. This repo is a **read-only mirror** of the community plugin marketplace, synced nightly from Anthropic's internal review pipeline. Every plugin listed here has been submitted via claude.ai, passed automated security scanning, and been approved for distribution.

So the accurate phrasing is: **ELI5 is a community-submitted plugin that Anthropic reviewed and approved for distribution** — not an Anthropic product. Its `plugin.json` credits Thariq Shihipar, MIT, v1.0.0.

The "used constantly by internal staff" claim appears nowhere in the repository, README, or plugin.json. It may be true, but there's **no primary source** — and our rule is to say so rather than lend a rumor our credibility.

## The four repositories, and what each is

Following that thread turns up something more useful: Anthropic's plugin/skill ecosystem lives across **four repositories** with similar names and entirely different purposes. That's likely the root of the confusion:

| Repository | Stars | What it is | What's inside |
|---|---:|---|---|
| **anthropics/skills** | 174k | **Agent Skills** proper, with spec and template | 19: docx / pdf / pptx / xlsx, mcp-builder, skill-creator, canvas-design, frontend-design, webapp-testing, brand-guidelines… |
| **anthropics/claude-plugins-official** | 35.9k | **Anthropic-managed** directory of high-quality Claude Code plugins | `plugins/` and `external_plugins/` |
| **anthropics/knowledge-work-plugins** | 23.9k | Cowork plugins for **knowledge workers**, organized **by job function** | bio-research, customer-support, data, design, engineering, enterprise-search, finance, human-resources, legal, marketing, operations, product-management, sales, small-business… |
| **anthropics/claude-plugins-community** | 3,479 | **Community-submitted**, security-scanned and approved | Just 4 today: **eli5**, quickdesign, testdino, tres-finance-plugin |

Practical takeaways:

- For **document handling, building MCP servers, or authoring skills**, go to `anthropics/skills`.
- For capability bundles **organized by role** (legal, finance, HR, sales), go to `knowledge-work-plugins` — its taxonomy is worth a look on its own, essentially slicing Cowork's target users by job function.
- The community marketplace has **only 4 plugins**. 3,479 stars against 4 plugins says interest far exceeds supply — this market is very early.

Installing from the community marketplace:

```bash
claude plugin marketplace add anthropics/claude-plugins-community
claude plugin install eli5@claude-community
```

One process detail worth noting: **pull requests opened directly against that repo are closed automatically.** Everything flows through the internal review pipeline, with submissions going through `clau.de/plugin-directory-submission`. So this "community marketplace" **has a gatekeeper** — automated security scanning plus approval. Good for users; for contributors it means a form, not a PR.

## What those five lines look like

The complete `SKILL.md`, nothing removed:

```markdown
---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS
```

The README is eight lines, and its example is a single `/eli5 how does DNS work`.

## Why the five lines are the point

We've published several posts on Agent Skills — progressive disclosure standards, skill slop, skill marketplaces. ELI5 offers a sample from the opposite direction: **a skill that passed official review and shipped to a distribution marketplace can be one sentence of instruction.**

It does three things right:

1. **The `description` states trigger conditions rather than restating features.** "Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer" tells the model *when I apply*. Many skill descriptions are feature summaries, leaving the model no better informed about when to invoke them.
2. **The body constrains only the output shape**: HTML artifact, big pictures, few words. **No thinking procedure, no template, no step list** — those are left to the model.
3. **One skill, one job.** No configuration, no modes, no optional parameters.

Set against the several-hundred-line skills with reference files and checklists we've covered, there's a judgment worth keeping: **a skill's length should track how much the model doesn't know, not how important the task is.** The model already knows how to explain things plainly and how to produce an HTML artifact, so all that's left to supply is *when* and *in what shape* — five lines suffice.

Conversely, **if a skill is long, the long part should be what the model genuinely doesn't know**: your team's internal conventions, an API's quirks, the potholes in a particular process. Restating what the model already knows just burns context.

![A stack of paper next to a single sheet: how long a skill should be depends on how much the model doesn't know, not on how important the task is — the long part should be team conventions, API quirks, and known potholes](../../assets/images/anthropic-plugin-marketplaces-four-repos-eli5-minimal-skill-fig-01.png)

## A closing judgment

This started as a fact-check on a claim from X. The verdict is **half true** — the skill is real; "official product, used constantly internally" is embellishment.

But the byproduct outgrew the original topic: **Anthropic's plugin ecosystem spans four similarly named repositories with different purposes and different bars to entry**, and the community marketplace currently holds four plugins. Knowing where to look is worth more than knowing any one skill.

As for ELI5, install it — not because it's powerful, but because it's a useful **counter-reference**: next time you're on line three hundred of a skill you're writing, look back at these five lines and ask how much of yours the model already knew.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
