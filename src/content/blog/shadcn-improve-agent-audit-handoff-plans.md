---
title: "shadcn /improve：强模型做审计，便宜模型按计划施工"
titleEn: "shadcn Improve: Audit, Handoff Plans and Cheaper Execution"
description: "shadcn/improve 是一套开源编码技能，将代码审计、优先级判断、实施计划和执行复核拆开，让强模型负责界定问题，让低成本模型按明确边界施工。本文核验安装与命令、隔离工作树及宿主要求，并在临时 Git 仓库验证差异检查的两个盲点，说明怎样写出可交接、可验收的计划，以及为何不能把多模型分工直接当成已证明的省费比例。"
descriptionEn: "Audit shadcn/improve's code review and handoff workflow, host requirements, plan verification and Git diff edge cases before delegating work to cheaper agents."
wechatTitle: "shadcn improve：把审计交成施工计划"
wechatDigest: "强模型判断该修什么，低成本模型按计划执行；效果取决于交接质量和真实复核。"
pubDate: "2026-11-14"
updatedDate: "2026-11-14"
category: "Tech-News"
tags: ["Agent Skills", "Code Review", "Multi-Model", "Git", "Developer Tools"]
heroImage: "../../assets/images/shadcn-improve-agent-audit-handoff-plans-banner.jpg"
---

`/improve` 是一套把代码审计变成可执行交接计划的开源技能。它让能力较强的模型判断哪些问题值得修，再把范围、步骤和验收条件写清楚，交给另一位执行者。

项目由 shadcn 发布，采用 MIT 许可。用户给出的短链接已确认指向官方仓库；本文核对版本为提交 `cac56e1ebd3c279aa9153616cfeac7b174ab90f9`，技能元数据版本为 1.0.0。

官方仓库：https://github.com/shadcn/improve

## 它交付的是计划，为什么还有 execute？

技能中的顾问角色负责读代码、筛选问题和制定计划，原则上只写 `plans/`；目录另有用途时改用 `advisor-plans/`。实施修改交给单独的执行器，顾问随后重跑验收并读 diff，给出通过、返修或阻塞结论，合并由用户决定。

因此，“技能不实现代码”和“支持 execute”并不矛盾：前者约束顾问角色，后者调度独立执行角色。支持 Agent Skills 的宿主可以读取技能，Markdown 计划也能手工交接；自动执行则额外要求子代理和隔离 Git worktree 能力。

当前闭环文档默认执行模型为 `sonnet`，也允许指定其他模型。换一个宿主，并不会凭安装这份文本就自动获得同样的模型路由、工具调用或隔离机制。

![小M把审计发现整理成图纸，再交给独立执行者施工](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-01.png)

## 从安装到复核，实际怎么走？

在目标项目中按官方说明安装：

```bash
npx skills add shadcn/improve
```

随后在支持该技能的编码 Agent 中使用：

```text
/improve quick
plan 1, 3 and 5
/improve execute 001
/improve reconcile
```

第一步返回审计发现，你再选择要规划的编号。计划落到 `plans/`，索引记录建议顺序和依赖；`execute 001` 交给隔离工作树中的执行器，顾问复核后报告结论。`reconcile` 用于检查已完成项、刷新漂移计划和处理阻塞。

`quick` 缩小审计到热点及高置信度发现，不是低价格的承诺。提交 PR 前可使用 `/improve branch`，聚焦分支改动及直接调用者；安全、性能、测试也有聚焦入口。本文没有在博客仓库安装它或启动全库审计，这些是已核对的使用入口。

## 什么样的计划，便宜模型才能接得住？

最有价值的部分，是把隐含上下文写进可独立阅读的文件。上一个模型“已经知道”的背景，执行器未必知道；只留下“重构这块代码”，等于把调查成本转给下一轮。

一份可交接计划至少要说明：具体问题及证据、允许修改的文件、当前代码与项目约定、逐步操作、验证命令及预期结果，以及什么情况下必须停下报告。还应记录规划时的 Git 提交，方便先检查代码有没有变化。

这里给一个缩略结构，实际命令必须来自目标项目：

```text
为什么修：明确触发条件与当前错误
修改范围：只允许两个指定文件
第一步：补可复现错误的检查
第二步：最小修改并运行对应检查
完成条件：原失败消失，相关行为仍正确
停止条件：需要改范围外文件，或现场代码与计划不符
```

计划质量不能只看长度。验收命令存在却没有有效断言，执行器仍可能交付“全绿但没解决问题”的结果。顾问要重跑检查，也要读新测试到底断言了什么。

![小M在交接箱里逐项放入上下文、范围、验收和停止条件](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-02.png)

## 我们验证了哪两个 Git 检查盲点？

我们只在临时仓库运行了两组真实 Git 场景，没有调用付费模型、改动实际项目或执行上游计划。两个检查均通过，脚本与结果随文章保留。

第一组：基线提交以后只修改工作区，不提交。模板中的提交范围检查 `git diff --stat BASE..HEAD -- <范围>` 返回空，而 `git diff --stat HEAD -- <范围>` 看得见变更。原因是前者比较两个提交，不含未提交内容。因此，执行前要把提交漂移与工作区状态分别核对。

第二组：模拟执行器把范围外文件提交到隔离分支。此时普通 `git diff --stat` 为空，但 `git diff --stat BASE..HEAD` 能看见该文件。执行器按文档提交后，复核不能仅检查默认 diff，还要明确比较起点与执行分支。

可组合查看：

```bash
git status --short
git diff --stat HEAD -- path/to/scope
git diff --stat PLANNED_SHA..HEAD -- path/to/scope
git diff --name-only PLANNED_SHA..EXECUTOR_HEAD
```

其中最后一条用于检查已提交的全部改动是否越界；还要查看执行 worktree 的未提交状态。这是我们对模板命令使用条件的验证，不是声称每个宿主的审核器都会漏检，也不是对整套技能做了安全认证。

![小M同时检查提交历史和工作区，避免只看一层差异](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-03.png)

## 它一定能省钱吗？

更准确的假设是：高能力模型用于高判断密度的环节，明确而局部的实施交给较低成本模型。顾问的审计、写计划与复核都要消耗资源；执行器安装依赖、读上下文、测试和返修也有成本。没有实际账单，不能给出节省百分比。

Mycelium Protocol 的建议是先选一个边界明确的真实修复任务，记录审计、规划、执行、复核和返修的总耗时与费用，再与直接使用单个模型的流程比较。跨度很小的改动可能不值得拆分；依赖多、含糊不清的任务，则应先把计划写清楚。

这个项目的可借鉴之处，是把模型之间的交接变成能复查的工程文档。低成本执行能否成立，取决于计划是否消除了歧义，以及复核是否真的执行。

## 常见问题

**任何支持 skills 的 Agent 都能自动执行吗？** 技能文本和计划可移植；自动子代理调度、模型选择与 worktree 隔离取决于宿主。缺少能力时可以手工把计划交给执行者。

**会自动合并代码吗？** 上游约束顾问不向用户分支合并、提交或推送。执行器在隔离工作树中提交，最终合并由用户决定。

**此次实测覆盖了什么？** 只验证两组 Git 命令行为，并核对公开技能、模板与闭环文档。没有运行真实模型审计、执行器、自动修复或成本对比。

执行闭环说明：https://github.com/shadcn/improve/blob/main/skills/improve/references/closing-the-loop.md
计划模板：https://github.com/shadcn/improve/blob/main/skills/improve/references/plan-template.md
相关工程阅读：https://blog.mushroom.cv/blog/jane-street-socratic-tutor-agent-skills-guide/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

`/improve` is an open agent skill that turns code-audit findings into implementation handoff plans. A capable advisor identifies worthwhile work and specifies it so another executor can proceed with less ambiguity.

shadcn publishes it under MIT. The supplied short link resolves to the official repository. Our snapshot is Git commit `cac56e1ebd3c279aa9153616cfeac7b174ab90f9`, with skill metadata version 1.0.0.

Repository: https://github.com/shadcn/improve

## Why can an audit-only skill execute a plan?

The advisor reads, prioritizes and writes plans. A separate executor changes code in an isolated worktree; the advisor then checks the result. The role boundary explains why the advisor remains read-only while the workflow supports implementation.

A host can read Agent Skills and exchange Markdown plans without necessarily supporting automatic execution. Subagent dispatch and isolated worktrees are additional requirements. The current closing-loop documentation defaults to `sonnet` for execution and permits another requested model; installation alone does not provision a universal model router.

![Little M turns findings into plans and hands them to an independent executor](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-01.png)

## How do you use it?

The documented installation command is:

```bash
npx skills add shadcn/improve
```

A typical interaction is:

```text
/improve quick
plan 1, 3 and 5
/improve execute 001
/improve reconcile
```

Select findings before writing plans. The index records order and dependencies. The executor works separately; review produces a verdict, while merging remains the user's decision. Reconciliation refreshes drifted plans and investigates blocked work. `branch` scopes an audit to branch changes and their callers.

Quick mode reduces audit scope and seeks high-confidence findings. It does not guarantee a particular bill. We did not install or invoke the skill against this Blog repository.

## What makes a plan transferable?

An executor needs the problem, exact paths, current-state evidence, relevant conventions, ordered steps, verification commands and expected results. It also needs explicit scope boundaries, the planning commit and conditions that require stopping rather than improvising.

This is a contract between agents. Length is a weak proxy for quality: a long plan with guessed commands or meaningless tests still fails. A reviewer should execute the checks and inspect their assertions, rather than accepting an executor's claim that everything passed.

![Little M packs context, scope, acceptance and stop conditions into a handoff](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-02.png)

## What did our two local Git checks establish?

We used an isolated temporary repository, not a paid model or a production project. Both mechanical checks passed.

First, an uncommitted edit was invisible to `git diff --stat BASE..HEAD -- <scope>` but visible to `git diff --stat HEAD -- <scope>`. A commit-range comparison does not include working-tree edits. Check committed drift and dirty state separately.

Second, after a simulated executor committed an out-of-scope file, plain `git diff --stat` was empty. Comparing the baseline to HEAD revealed that file. Review of an executor that commits work requires an explicit baseline comparison as well as a working-tree check.

```bash
git status --short
git diff --stat HEAD -- path/to/scope
git diff --stat PLANNED_SHA..HEAD -- path/to/scope
git diff --name-only PLANNED_SHA..EXECUTOR_HEAD
```

The final command checks all committed paths for scope compliance. Also inspect uncommitted work in the executor's worktree. These cases establish limitations of individual template commands; they do not prove that every host reviewer misses them or certify the whole workflow.

![Little M inspects both commit history and working-tree changes](../../assets/images/shadcn-improve-agent-audit-handoff-plans-fig-03.png)

## Is lower total cost guaranteed?

The economic hypothesis is sensible: reserve expensive reasoning for judgment-heavy work and delegate well-specified implementation. However, audit, planning, review, context transfer, dependency installation and revision all cost time or tokens. We measured no model-cost savings.

Mycelium Protocol recommends a bounded real task first. Record end-to-end cost and elapsed time, including review and rework, then compare against a single-model workflow. Tiny edits may not justify the coordination; ambiguous changes need a better specification before delegation.

The useful engineering idea is a reviewable handoff contract. Cheaper execution becomes plausible when context and acceptance criteria are explicit, not merely when a cheaper model is selected.

## FAQ

**Does every skills-compatible agent support automatic execution?** No. Reading the skill and handing over plans are portable; dispatch, model choice and isolation depend on host capabilities. Manual handoff remains possible.

**Does it merge automatically?** The advisor is instructed not to merge, push or commit to the user's branch. Executor commits stay in an isolated worktree until the user decides to merge.

**What was tested here?** Two Git command scenarios and a source review. We did not run an LLM audit, executor, automated repair or cost benchmark.

Execution reference: https://github.com/shadcn/improve/blob/main/skills/improve/references/closing-the-loop.md
Plan template: https://github.com/shadcn/improve/blob/main/skills/improve/references/plan-template.md
Related: https://blog.mushroom.cv/blog/jane-street-socratic-tutor-agent-skills-guide/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
