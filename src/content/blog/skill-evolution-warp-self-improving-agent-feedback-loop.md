---
title: "Skill Evolution：从 Warp 案例提炼「技能进化」通用范式"
titleEn: "Skill Evolution: A General Paradigm for Self-Improving Agents, Distilled from Warp"
description: "Warp 用两个 skill 文件构建了自我改进的 Agent 闭环——内层 skill 承载领域知识，外层 improver skill 定期拉取人类反馈并提议最小化改动。本文从这个案例提炼出可复用的「技能进化」通用范式，以及如何从零搭建这套机制。"
descriptionEn: "Warp built self-improving agents with two skill files — an inner base skill holding domain knowledge, and an outer improver skill that periodically pulls human feedback and proposes minimal edits. This article distills a reusable Skill Evolution paradigm from that case, with a framework for building it from scratch."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Research"
tags: ["AI agents", "skill evolution", "self-improving agents", "Claude", "Warp", "feedback loop", "agent skills", "paradigm", "Anthropic"]
heroImage: "../../assets/images/skill-evolution-warp-self-improving-agent-feedback-loop-banner.jpg"
author: "Mycelium Protocol"
---

## 问题：反馈总在会话结束时消失

一个 Agent 做了代码 Review，工程师在 PR 里指出它遗漏了一个标签，解释了为什么这个标签重要。Agent 下次启动——什么都不记得了。

这不是上下文窗口的问题，是架构问题：**反馈没有落点，没有载体，就永远无法变成知识。**

Warp——那个 AI 驱动的终端，56% 的 Fortune 500 在用，每周跑 40 万次 Claude Code 会话——用一个非常简单的架构解决了这个问题：**两个 skill 文件，中间夹一个人类反馈节点。**

这篇文章从 Warp 的案例提炼出一套通用范式，以及怎么从零把它搭起来。

---

## Warp 的答案：技能进化闭环

Warp 的创始人 Zach Lloyd 在 Anthropic 的 webinar 上描述了这个架构：

```
┌─────────────────────────────────────────────┐
│                                             │
│  Inner Skill (base)                         │
│  ─ 领域知识 + 任务指令                        │
│                                             │
└──────────────┬──────────────────────────────┘
               │ Agent 执行，产生输出
               ▼
        ┌─────────────┐
        │  人类反馈    │  ← 在工作发生的地方（PR、Issue 评论）
        └──────┬──────┘
               │ 信号积累
               ▼
┌─────────────────────────────────────────────┐
│                                             │
│  Outer Skill (improver)                     │
│  ─ 定期运行（非每次任务）                     │
│  ─ 拉取反馈、比对输出、提议最小化改动          │
│                                             │
└──────────────┬──────────────────────────────┘
               │ 以 PR 形式提议改动 base skill
               ▼
        ┌─────────────┐
        │  人类审查    │  ← 审批、合并
        └──────┬──────┘
               │
               ▼
        base skill 继承改动
        下一次运行自动更好
```

**关键洞察**：skill 文件是纯文本，Agent 极擅长更新它。把 skill 改动纳入普通的 PR 审查流程，既保留了人类控制权，又让改动可追溯、可回滚。

---

## 通用范式：技能进化的五个组件

### 1. 领域技能（Base Skill）

持有任务所需的所有领域知识。**写原则而非规则**：

> ❌ 「变量名使用 camelCase，函数名使用 snake_case」  
> ✅ 「命名应传达意图而非类型；全局变量遵循所在模块的既有惯例」

原则让 Agent 推理，规则让 Agent 死记。当遇到未见过的情况，懂原则的 Agent 能类推；只记规则的 Agent 会出错。

**必须包含的内容**：
- 任务目标和成功标准
- 领域关键概念和约束（解释**为什么**）
- 对模糊情况的处理原则
- 指向外部资源文件的引用（不要把一切塞进 skill 正文）

### 2. 反馈底座（Feedback Substrate）

这是整个循环能否运转的关键变量。三个设计原则：

**在工作发生的地方捕获反馈**  
工程师在 PR 评论里改代码——反馈就在那里收。Issue 讨论里有 triage 建议——反馈就在那里收。额外的反馈表单 = 反馈死亡。

**质量 > 数量，但数量也有价值**  
一个高级工程师给出的带理由的反馈，胜过十个 👍/👎。但 Warp 有数百人在开源仓库里贡献，数千次 code review——数量最终也能补质量的不足。

**具体反馈 > 评价性反馈**  
> ❌ 「这个 review 没用」  
> ✅ 「你建议重命名这个变量，但我们代码库里全局变量的惯例是这样的：...」

后者是 Agent 能直接吸收的知识，前者只是一个信号。

### 3. 进化观察者（Improver Skill）

Improver skill 不在每次任务时运行——它**定期运行**（比如每天或每周）。职责：

1. 拉取自上次更新以来积累的反馈
2. 比对 Agent 的输出和人类的反应
3. 识别模式：哪类情况 Agent 系统性地做错了？
4. 提议**最小化**改动到 base skill

「最小化」是关键词。Improver 不重写 base skill，只添加或修改覆盖具体失败点的内容。大的改动 = 难以审查 = 合并率低 = 进化停滞。

**Improver skill 是高度可复用的**：一个写给 code review agent 的 improver，和写给 issue triage agent 的 improver 在结构上几乎相同，只是领域 context 不同。投入时间写好一个通用 improver 模板，收益会跨越所有 Agent。

### 4. 进化门控（Human Review Gate）

Improver 提议改动以 **PR** 的形式呈现，不是直接写入 base skill。原因：

- **反馈可能是错的**：不让 Agent 盲目接受反馈；给它 context 来做合理性检查
- **人类保持控制权**：最终决定什么进入 skill 的是人，不是 Agent
- **可追溯性**：每次 skill 演进都有记录，出了问题能回滚

PR 描述应该包含：是什么反馈触发了这次改动，改动了什么，为什么这么改。

### 5. 继承与扩展（Inheritance and Scale）

一旦 base skill 被更新并合并，**下次运行自动继承新知识**。不需要重启，不需要重新训练，不需要手动传递 context。

扩展时的关键决策：

| 场景 | 策略 |
|---|---|
| **领域可验证**（有标准答案）| 先建验证 harness，让 Agent 对着 reference corpus 调优 |
| **领域不可验证**（主观判断）| 依赖黄金输出集合 + 领域专家反馈，限制反馈来源 |
| **少量 Agent**（<10）| 每个 Agent 一个独立的 improver loop |
| **大量 Agent**（100+）| 共享模板化的 base improver loop + 领域特定权重层 |

---

## 一个可以直接用的 Skill Evolution 搭建清单

```
□ 1. 写 base skill
     ─ 任务目标 + 成功标准
     ─ 领域原则（附理由）
     ─ 模糊情况处理原则
     ─ 外部资源引用（不要把一切塞进正文）

□ 2. 设计反馈落点
     ─ 确定反馈在哪里自然产生（PR、Issue、Slack 评论...）
     ─ 自动收集，无额外提交步骤
     ─ 结构化存储：{反馈内容, 反馈者, 对应的 Agent 输出, 时间戳}

□ 3. 写 improver skill
     ─ 拉取 N 天内的反馈（脚本化，可复用）
     ─ 比对 Agent 输出 vs 人类反应，识别系统性失败
     ─ 提议最小化改动（单次 PR 只改一件事）
     ─ 在 PR 描述里解释触发原因和改动内容

□ 4. 接入 PR 审查流程
     ─ Improver 开 PR → 人类审查 → 合并 → 继承
     ─ 设置合理的运行频率（开始时周频，稳定后降低）

□ 5. 追踪全局指标
     ─ 找到人类已经在看的指标（合并时间、错误率、处理时长...）
     ─ 把这些指标作为额外 context 喂给 improver
     ─ 不要只追踪单次任务质量，要看长期趋势
```

---

## Skills vs Memory：容易混淆的边界

Warp 团队特别强调这个区别：

| | **Skills** | **Memory** |
|---|---|---|
| **本质** | 过程知识（「如何做 X」）| 事实记录（「发生了什么」）|
| **稳定性** | 稳定，刻意修改 | 动态，推理时自动写入 |
| **生命周期** | 跨任务持久，显式版本化 | 会话内或短期 |
| **用于** | 编码领域规则和原则 | 记录对话 context 和事实 |

技能进化用的是 **Skills**。Memory 是另一套机制，不要混用。

---

## 总结：为什么这个范式重要

大多数团队部署一个 Agent，看它运行，然后继续别的事。Warp 做了不同的事：**把 Agent 的每次失败变成下次运行的养分。**

两个 skill 文件 + 人类在中间的闭环，不需要重新训练模型，不需要复杂的 RAG 基础设施，不需要专门的 ML 团队。只需要：
- 一个写得好的 base skill（原则而非规则）
- 一个在工作流里自然发生反馈的节点
- 一个定期观察并提议改动的 improver skill
- 一个正常的 PR 审查流程

任何 Agent，无论它的任务是什么，只要在设计时把这个循环内置进去，就会随着时间推移自动变好。

**参考来源**:  
- [How Warp builds self-improving agents on Claude](https://claude.com/blog/how-warp-builds-self-improving-agents-on-claude) · Claude Blog, Aug 26, 2026  
- [Webinar: How Warp builds self-improving agents on Claude](https://www.anthropic.com/webinars/how-warp-builds-self-improving-agents-on-claude) · Anthropic, May 13, 2026  
- [Warp issue triage agent demo](https://github.com/warpdotdev/warp-agents-demo-github-issue-triage) · GitHub

<!--EN-->

## The Problem: Feedback Always Disappears When the Session Ends

An agent runs a code review. An engineer leaves a comment on the PR explaining why a specific label was missed and what it should mean. The agent starts its next session — and remembers nothing.

This isn't a context window problem. It's an architecture problem: **feedback has no landing place, no carrier, so it can never become knowledge.**

Warp — the AI-powered terminal used by 56% of the Fortune 500, running 400K Claude Code sessions per week — solved this with something remarkably simple: **two skill files, with a human feedback node in between.**

This article distills a general paradigm from that case, with a framework for building it from scratch.

---

## The Warp Answer: A Skill Evolution Loop

Warp founder Zach Lloyd described the architecture in an Anthropic webinar:

```
Inner Skill (base)
─ Domain knowledge + task instructions
        │
        ▼ Agent runs, produces output
        
Human Feedback  ← captured where work happens (PR, issue comments)
        │ signal accumulates
        ▼
        
Outer Skill (improver)
─ Runs on a schedule (not per-task)
─ Pulls feedback, compares output, proposes minimal edit to base skill
        │ proposes edit as PR
        ▼
        
Human Review  ← approves and merges
        │
        ▼
Base skill inherits the change
Next run is automatically better
```

**Key insight**: skill files are plain text, and agents are extremely good at editing them. Routing skill edits through a normal PR review workflow preserves human control while making every change traceable and reversible.

---

## The General Paradigm: Five Components of Skill Evolution

### 1. Domain Skill (Base Skill)

Holds all the domain knowledge required for the task. **Write principles, not rules:**

> ❌ "Variables use camelCase, functions use snake_case"  
> ✅ "Names should communicate intent over type; global variables follow the naming convention already used in their module"

Principles let agents reason; rules make them memorize. When an agent encounters a novel situation it hasn't seen before, a principle-based agent can generalize; a rule-following agent will fail.

**Must include**: task goal and success criteria, domain concepts and constraints (with *why*), principles for ambiguous cases, references to external resource files (don't dump everything into the skill body).

### 2. Feedback Substrate

This is the critical variable for whether the loop runs at all. Three design principles:

**Capture feedback where work happens**  
Engineers comment on PRs — capture it there. Issue discussion contains triage suggestions — capture it there. An extra feedback form = feedback death.

**Quality > volume, but volume helps**  
A senior engineer's reasoned feedback beats ten thumbs up/down. But Warp has hundreds of contributors across thousands of code reviews — volume eventually compensates.

**Specific > evaluative feedback**  
> ❌ "That review wasn't useful"  
> ✅ "You suggested renaming this variable, but our convention for global variables in this module is: ..."

The second is knowledge an agent can directly absorb.

### 3. Evolution Observer (Improver Skill)

The improver skill doesn't run per task — it **runs on a schedule** (daily or weekly). Its job:

1. Pull feedback accumulated since the last update
2. Compare agent output against human responses
3. Identify patterns: what types of situations does the agent systematically get wrong?
4. Propose a **minimal** edit to the base skill

"Minimal" is the operative word. The improver doesn't rewrite the base skill — it adds or modifies content that addresses specific failure points. Large edits = hard to review = low merge rate = evolution stalls.

**Improver skills are highly reusable**: the improver for a code review agent is structurally nearly identical to the improver for an issue triage agent. Invest in writing one good improver template and the returns compound across all your agents.

### 4. Evolution Gate (Human Review)

The improver proposes changes as a **PR**, not a direct write to the base skill. Why:

- **Feedback might be wrong**: don't let the agent accept feedback blindly; give it context to sanity-check
- **Humans stay in control**: what enters the skill is decided by humans, not agents
- **Traceability**: every skill evolution step is recorded, reversible if something breaks

The PR description should include: what feedback triggered this, what changed, and why.

### 5. Inheritance and Scale

Once the base skill is updated and merged, **the next run automatically inherits the new knowledge**. No restart, no retraining, no manual context passing.

Key decisions when scaling:

| Scenario | Strategy |
|---|---|
| **Verifiable domain** (objective answers) | Build a verification harness first; let the agent tune against a reference corpus |
| **Non-verifiable domain** (subjective judgment) | Rely on golden output sets + domain expert feedback; restrict who can provide feedback |
| **Few agents** (<10) | One independent improver loop per agent |
| **Many agents** (100+) | Shared templated base improver loop + domain-specific weight layers |

---

## A Skill Evolution Setup Checklist

```
□ 1. Write the base skill
     ─ Task goal + success criteria
     ─ Domain principles (with rationale)
     ─ Principles for ambiguous cases
     ─ References to external resources (don't inline everything)

□ 2. Design the feedback substrate
     ─ Identify where feedback naturally occurs (PR, issue, Slack...)
     ─ Collect automatically, no extra submission step
     ─ Store structured: {content, author, agent output, timestamp}

□ 3. Write the improver skill
     ─ Pull N days of feedback (scripted, reusable)
     ─ Compare agent output vs human response, identify systemic failures
     ─ Propose minimal edits (one thing per PR)
     ─ Explain trigger and change in the PR description

□ 4. Wire the PR review flow
     ─ Improver opens PR → human reviews → merge → inherit
     ─ Start with weekly runs, reduce cadence once stable

□ 5. Track global metrics
     ─ Find metrics humans already watch (time to merge, error rate, processing time...)
     ─ Feed these as extra context to the improver
     ─ Track long-term trends, not just per-task quality
```

---

## Skills vs Memory: An Easy Confusion

| | **Skills** | **Memory** |
|---|---|---|
| **Nature** | Procedural knowledge ("how to do X") | Factual records ("what happened") |
| **Stability** | Stable, deliberately modified | Dynamic, auto-written at inference time |
| **Lifecycle** | Cross-task persistent, explicitly versioned | Session-scoped or short-lived |
| **Used for** | Encoding domain rules and principles | Recording conversation context and facts |

Skill evolution uses **Skills**. Memory is a separate mechanism — don't conflate the two.

---

## Summary: Why This Paradigm Matters

Most teams deploy an agent, watch it run, and move on. Warp did something different: **turned every agent failure into fuel for the next run.**

Two skill files plus a human-in-the-loop requires no model retraining, no complex RAG infrastructure, no dedicated ML team. Just:

- A well-written base skill (principles, not rules)
- A natural feedback node already in the workflow
- A scheduled improver skill that observes and proposes
- A normal PR review process

Any agent, whatever its task, will improve over time if you build this loop in from the start.

**Sources**:  
- [How Warp builds self-improving agents on Claude](https://claude.com/blog/how-warp-builds-self-improving-agents-on-claude) · Claude Blog, Aug 26, 2026  
- [Webinar: How Warp builds self-improving agents on Claude](https://www.anthropic.com/webinars/how-warp-builds-self-improving-agents-on-claude) · Anthropic, May 13, 2026  
- [Warp issue triage agent demo](https://github.com/warpdotdev/warp-agents-demo-github-issue-triage) · GitHub
