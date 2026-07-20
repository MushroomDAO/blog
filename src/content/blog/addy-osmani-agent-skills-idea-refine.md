---
title: "Addy Osmani 开源了 79K stars 的 agent-skills：idea-refine 把乔布斯产品思维包进 AI Agent 工作流"
titleEn: "Addy Osmani's 79K-Star agent-skills: idea-refine Packages Steve Jobs-Style Product Thinking Into an AI Agent Workflow"
description: "addyosmani/agent-skills（79K stars）是一套给 AI 编程 Agent 补充「高级工程师的隐性工作」的 Skill 集合。其中的 idea-refine 最值得单独拆解：三相工作流（发散→收敛→落地）、SCAMPER+JTBD+预验尸等框架、强制输出「不做什么」清单——把 Addy 多年 Google 产品思维包装成 Agent 上下文注入。Agent 默认跳过所有不出现在 diff 里的工作，Skill 把这些工作变成 Agent 绕不过去的检查点。"
descriptionEn: "addyosmani/agent-skills (79K stars) supplements AI coding agents with the 'invisible senior-engineer work' they skip by default. The idea-refine skill is worth its own breakdown: a three-phase workflow (diverge → converge → ship), SCAMPER + JTBD + pre-mortem frameworks, and a mandatory 'Not Doing' list — packaging Addy's Google product thinking into injectable agent context. Agents take shortcuts; skills make those shortcuts impossible."
pubDate: "2026-07-20"
updatedDate: "2026-07-20"
category: "Tech-Experiment"
tags: ["Addy Osmani", "Claude Code", "AI Agent", "Skill", "产品思维", "开源", "工程实践", "idea-refine", "agent-skills"]
heroImage: "../../assets/images/addy-osmani-agent-skills-idea-refine-banner.jpg"
---

> **GitHub**：[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) · ⭐ 79,331 · MIT  
> **idea-refine skill**：`skills/idea-refine/SKILL.md`  
> **作者博客**：[addyosmani.com/blog/agent-skills](https://addyosmani.com/blog/agent-skills/)

---

## Agent 的默认行为是跑最短的路

Addy Osmani 在博客里说了一句话，我觉得是整个项目的核心：

> "The default behaviour of any AI coding agent is to take the shortest path to 'done.'"

你让它实现一个功能，它实现了这个功能。它不会主动去问你有没有写 spec，不会在动手之前先写测试，不会考虑这个改动是否会影响信任边界，不会关心 PR reviewer 看到这个 diff 会有什么感受。

**它产出代码，宣布完成，然后继续下一个任务。**

这是每一个工作过的高级工程师职业生涯都在学习如何避免的失败模式。但对 Agent 来说这是默认状态，因为「任务完成」是奖励信号，而「写了 spec、留下了验证证据、代码能被 review」这些不出现在 diff 里的东西没有奖励信号。

`agent-skills` 的思路就是：**用 Skill 把这些高级工程师的隐性工作变成 Agent 绕不过去的检查点。**

---

## 79K stars 的结构

仓库里有 24 个 skill，组织成六个生命周期阶段：

```
Define (/spec)  →  Plan (/plan)  →  Build (/build)
     ↓                                     ↓
Review (/review) ←  Verify (/test)  ←  Ship (/ship)
                         ↑
              /code-simplify (贯穿全程)
```

每个 skill 是一个有 frontmatter 的 markdown 文件，不是文档，是**工作流**——有步骤、有检查点、有明确的退出条件。

**安装方式（Claude Code）**：

```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

然后 `/spec`、`/plan`、`/review`、`/ship` 这些斜线命令就可以用了。

---

## idea-refine：最值得单独拆解的那一个

`skills/idea-refine/` 是我觉得设计最精妙的一个——因为它处理的问题在工程环节之前：**这个想法值不值得建？**

### 触发方式

```
"Help me refine this idea"
"Ideate on [concept]"
"Stress-test my plan"
```

### 三相工作流

**Phase 1：理解与展开（发散）**

Agent 把原始想法重新表述成一句「我们如何才能……」（HMW）的问题。然后提 3~5 个锋利的问题：

- 这是为谁建的，具体是谁？
- 成功是什么样的？
- 真实约束是什么（时间、技术、资源）？
- 之前有人试过吗？
- 为什么是现在？

然后从 **7 个视角**生成 5~8 个变体（不是 20 个，是 5~8 个——质量优于数量）：

| 视角 | 问法 |
|---|---|
| 反转（Inversion） | 如果我们做相反的事呢？ |
| 去除约束 | 如果预算/时间/技术不是限制呢？ |
| 换受众 | 如果目标用户是另一类人呢？ |
| 组合 | 如果把这个和 [邻近想法] 合并呢？ |
| 简化 | 简单 10 倍的版本是什么？ |
| 10 倍放大 | 在极大规模下会是什么样子？ |
| 专家视角 | 领域专家会觉得显而易见但外人看不出来的是什么？ |

**如果在一个代码库里运行**，Skill 要求 Agent 先扫描现有架构、模式和历史——把变体落地在真实存在的约束里，而不是在真空里发散。

---

**Phase 2：评估与收敛**

把用户回应中共鸣的想法聚合成 2~3 个方向，每个方向在三个维度上做压力测试：

**用户价值**：止痛药还是维生素？
- 止痛药：解决真实痛点，用户会主动寻找，会从现有方案切换过来
- 维生素：锦上添花，用户点头说「挺好的」但不会改变行为

**可行性**：核心技术存在吗？最难的部分是什么？最小化团队和时间是多少？

**差异化**：这个和别的有什么**本质**上的不同？（不是"更快更便宜"——这是最弱的差异化，竞争对手一周能复制）

差异化的强度从高到低：
1. 新能力（之前做不到的事）
2. 10 倍提升（在关键维度上好到改变行为）
3. 新受众（把已有能力带给被排除在外的人）
4. 新场景（在现有方案失效的情境下能用）
5. 更好的 UX（同样的能力，更简单的体验）
6. 更便宜（最弱，最容易被竞争）

然后**强制做假设审计**：
- 如果错了会直接杀死想法的（必须验证）
- 重要但不致命的（调整方向用）
- 次要的（核心验证后再管）

---

**Phase 3：打磨与落地**

输出一份 markdown 一页纸：

```markdown
# [想法名称]

## 问题陈述
[一句话「我们如何才能……」表述]

## 推荐方向
[选择的方向和原因，最多 2-3 段]

## 需要验证的关键假设
- [ ] [假设 1 — 如何验证]
- [ ] [假设 2 — 如何验证]

## MVP 范围
[最小版本是什么。什么做，什么不做。]

## 不做什么（以及原因）
- [事情 1] — [原因]
- [事情 2] — [原因]

## 待解决的开放问题
- [动手建之前需要回答的问题]
```

**「不做什么」清单是 Addy 强调的最有价值的部分。** 专注意味着对好想法也说不，把取舍变成显式声明。

---

## 三个支撑框架（frameworks.md）

`idea-refine` 带了一份框架参考，Agent 按需选用，不是每个都跑：

**SCAMPER**：对现有想法做七种变形操作（替换/组合/改编/放大或缩小/换用途/消除/反转）。适合改进已有产品。

**JTBD（Jobs to Be Done）**：关注用户真正在完成什么任务，而不是他们说他们想要什么。格式：「当我 [情境] 时，我想要 [动机]，这样我就能 [预期结果]。」关键洞见：Netflix 的竞争对手不只是其他流媒体，而是睡眠。

**预验尸（Pre-mortem）**：想象项目在 12 个月后失败了，从结果往前推失败原因。对每个可能的失败模式问：这能预防吗？这是信号说明想法需要改变吗？

---

## 整个项目最值得学的设计决策

Addy 在博客里列了 5 个设计原则，其中最独特的是**反理性化表格（Anti-rationalization tables）**。

LLM 非常擅长理性化——它们能生成貌似合理的段落来解释为什么这个特定任务不需要 spec，或者为什么这个特定改动不用 review 也没关系。

每个 Skill 里都有一张表，列出 Agent 可能用来跳过工作流的常见借口，以及预先写好的反驳：

- "这个任务太简单了，不需要 spec" → 验收标准依然适用。五行 spec 可以，零行不行。
- "我之后再写测试" → "之后"是最重要的词。没有之后。先写失败的测试。
- "测试通过了，可以发" → 通过测试是证据，不是证明。你检查运行时了吗？用户可见行为验证了吗？有人类读过这个 diff 吗？

**反理性化表格是预先写好的、针对 Agent 还没说出来的谎言的反驳。** 这个模式对人类工程团队同样适用。

---

## 它和你自己的工作流的关系

即使你不安装任何东西，`idea-refine` 的设计本身也有值得借的东西：

**把"值不值得建"做成一个有步骤的工作流，而不是一个直觉判断。** 三相结构——发散、收敛、落地——保证你在收敛之前确实探索过足够多的方向。

**强制显式化假设。** 大多数项目的失败不是执行问题，是没有意识到自己在赌什么。把「必须为真的」「应该为真的」「可能为真的」三类假设分开列出，是一种认知工具，不只是一种 Agent 指令。

**「不做什么」清单比「做什么」清单更难、更重要。** 大多数 ideation 的产出是一堆要做的事，`idea-refine` 的 Phase 3 模板强制要求你把取舍写明。

---

## 一句话

`agent-skills` 给了一个清晰的框架来理解为什么直接用 AI 写代码容易出问题：不是模型的能力问题，是 Agent 的默认激励结构跳过了所有「不出现在 diff 里的工作」。`idea-refine` 是其中最前置的一个 skill——在动手写代码之前，先确认值不值得建、为谁建、假设是什么、什么不做。79K stars 的背后，是这个判断：**给 Agent 补充高级工程师的隐性工作，比给 Agent 更快写代码更重要。**

© 2026 Author: Mycelium Protocol

<!--EN-->

## Addy Osmani's agent-skills: Why idea-refine Matters

**GitHub**: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) · ⭐ 79,331 · MIT  
**Blog post**: [addyosmani.com/blog/agent-skills](https://addyosmani.com/blog/agent-skills/)

### The Core Diagnosis

> "The default behaviour of any AI coding agent is to take the shortest path to 'done.'"

Ask an agent for a feature and it writes the feature. It doesn't ask whether there's a spec, write a test first, consider trust boundaries, or check what the PR will look like to a reviewer. It produces code, declares victory, and moves on.

This is the same failure mode every senior engineer spends their career learning to avoid. The senior version of any task includes invisible work: surfacing assumptions, writing the spec, breaking into reviewable chunks, leaving evidence that the result is correct. Agents skip those steps for the same reason a junior would — the reward signal points at "task complete," not at "task complete and the design doc exists."

`agent-skills` bolts the senior-engineer scaffolding back on. 79K stars says this resonates.

### Structure

24 skills across six SDLC phases, each one a workflow — not documentation. Steps with exit criteria, not essays without them. The router meta-skill (`using-agent-skills`) progressively discloses the right skill for the current phase. Don't load all 24 into context at session start — activate them as needed.

Install in Claude Code:
```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

Slash commands: `/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`, `/code-simplify`.

### idea-refine: The Most Distinctive Skill

`skills/idea-refine/` handles the question before engineering begins: **is this worth building?**

**Trigger**: "Help me refine this idea" / "Ideate on [concept]" / "Stress-test my plan"

**Phase 1 — Understand & Expand (Divergent)**

Restate as a "How Might We" problem. Ask 3-5 sharpening questions (who specifically, what does success look like, real constraints, prior art, why now). Generate 5-8 variations through 7 lenses: Inversion, Constraint removal, Audience shift, Combination, Simplification (10x simpler), 10x scale, Expert lens.

5-8 well-considered variations, not 20 shallow ones. If inside a codebase, scan existing architecture first — ground variations in real constraints.

**Phase 2 — Evaluate & Converge**

Cluster resonant ideas into 2-3 distinct directions. Stress-test each on three dimensions:

*User value*: painkiller or vitamin? Painkillers: users actively seek them, will switch from current workaround, feel the problem with emotion. Vitamins: "that's cool," nods, no behavior change.

*Feasibility*: does the core tech exist, what's the hardest part, what's the minimum team/time for an MVP?

*Differentiation* (strongest to weakest): new capability → 10x improvement → new audience → new context → better UX → cheaper (weakest — easily copied).

Then the assumption audit: dealbreakers (if wrong, kill the idea), important (adjusts approach if wrong), nice-to-have (validate last). Most ideation fails here — assumptions are left implicit.

**Phase 3 — Sharpen & Ship**

A markdown one-pager: Problem Statement, Recommended Direction, Key Assumptions to Validate (with how to test each), MVP Scope, and crucially — **Not Doing (and Why)**. The Not Doing list is the most valuable part. Focus is about explicitly saying no to good ideas.

### The Standout Design Decision: Anti-Rationalization Tables

LLMs are excellent at rationalization. They will produce plausible-sounding text explaining why *this particular* task doesn't need a spec, why *this particular* change is fine without review.

Every skill includes a table of common excuses paired with pre-written rebuttals:
- "This is too simple to need a spec" → Acceptance criteria still apply. Five lines is fine; zero is not.
- "I'll write tests later" → There is no later. Write the failing test first.
- "Tests pass, ship it" → Tests are evidence, not proof. Did a human read the diff?

**Anti-rationalization tables are rebuttals to lies the agent hasn't yet told.** The same practice is worth adopting for human engineering teams.

### Five Transferable Principles

Even if you never install anything, steal these:

1. **Process over prose.** Workflows are agent-actionable; essays are not. Convert your 2,000-word "how we approach X" doc into a 400-word workflow with checkpoints.
2. **Verification as a hard exit criterion.** "Seems right" never closes the loop. Define what evidence means the task is done.
3. **Progressive disclosure.** Don't load everything into context. Route to the right small piece for the situation.
4. **Make assumptions explicit.** Split into dealbreakers / important / nice-to-have before building.
5. **Touch only what you're asked to touch.** The single biggest determinant of whether an agent's PR is mergeable.

### Summary

`agent-skills` is a clear framework for understanding why raw AI coding often fails: it's not a capability problem, it's a default-incentive-structure problem. Agents skip the invisible work. Skills make it impossible to skip. `idea-refine` is the most upstream skill — before writing code, confirm it's worth building, for whom, on what assumptions, and what you're explicitly choosing not to do. The 79K stars reflect a simple bet: supplementing agents with senior-engineer invisible work matters more than making them write code faster.

© 2026 Author: Mycelium Protocol
