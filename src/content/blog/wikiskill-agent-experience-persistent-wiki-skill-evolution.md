---
title: "WikiSkill：Google Research 提出把 Agent 经验编译成永久知识，Skill 进化终于有了「记忆」"
titleEn: "WikiSkill: Google Research Proposes Compiling Agent Experience into Persistent Knowledge — Skill Evolution Finally Has Memory"
description: "Google Research 最新论文（arXiv:2608.27454）提出 WikiSkill：在原始经验与可执行 Skill 之间插入持久化 Wiki 层，经验永不丢失、知识复利积累。横跨 5 个基准、5 个模型，一致超越 EvoSkill/SkillOpt/Trace2Skill，并详解工程落地方案。"
descriptionEn: "Google Research's latest paper (arXiv:2608.27454) proposes WikiSkill: a persistent Wiki layer between raw experience and executable skills, so insights never scatter and knowledge compounds across iterations. Outperforms EvoSkill/SkillOpt/Trace2Skill across 5 benchmarks and 5 models. Includes full engineering implementation guide."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Research"
tags: ["WikiSkill", "agent skills", "skill evolution", "Google Research", "persistent knowledge", "LLM agent", "EvoSkill", "ReAct", "Anthropic Skills", "AI research"]
heroImage: "../../assets/images/wikiskill-agent-experience-persistent-wiki-skill-evolution-banner.jpg"
author: "Mycelium Protocol"
---

## 问题：经验「用过即散」

Agent Skill 自动进化研究近年来快速发展。EvoSkill、Trace2Skill、SkillOpt 这些方法都有同一个模式：

```
执行任务 → 分析 trajectories → 提案修改 Skill → 验证 → 保留或回滚
```

但它们都有同一个设计缺陷：**每轮迭代学到的洞察散落在提案历史、轨迹文件等临时产物中**，不会被系统性地保留。下一轮迭代无法建立在"至今积累的全部认知"上——每轮都在从头悟，而不是在上一轮的基础上推进。

受 Andrej Karpathy「LLM Wiki」思想的启发——把经验编译成持久、可复利的知识——Google Research 的六位研究员在 2026 年 8 月 27 日发表了 **WikiSkill**（arXiv:2608.27454）。

---

## WikiSkill 的核心思路：三层架构

WikiSkill 把 Agent 的工作空间拆成三个层次：

```
┌─────────────────────────────────────────┐
│  Skills Layer (skills/)                 │ ← 可执行的程序性知识，可回滚
│  SKILL.md + PURPOSE.md                  │
├─────────────────────────────────────────┤
│  Wiki Layer (wiki/)       ← 永不重置    │ ← 结构化知识，跨迭代复利积累
│  patterns/ + logs.md + skill-impact.md  │
├─────────────────────────────────────────┤
│  Raw Layer (raw/)                        │ ← 不可变的执行轨迹，一次写入
│  完整的 agent 交互历史                   │
└─────────────────────────────────────────┘
```

**关键设计决策：Wiki 永不回滚，Skill 可以回滚。**

当一个 Skill 更新被验证集否决时，Skill 会恢复到之前的版本——但 Wiki 不会。这次失败本身会被记录下来，成为下一次提案的参考。

---

## 进化循环的四个角色

每一轮迭代，四个组件按顺序协作：

### 1. Inference Agent（执行者）

用当前 Skill 执行训练任务，产出执行轨迹写入 `raw/`。

**关键约束：Inference Agent 在执行期间不能访问 Wiki Layer。**

论文的消融实验证明，如果 Inference Agent 执行时能读 Wiki，模型会从 Wiki 直接抄答案，导致轨迹质量下降，反而让 Skill 进化效果变差（Table 3 中 63.7% → 60.9%）。

### 2. Wiki Maintainer（知识编译者）

从训练轨迹中提取模式，更新 Wiki：

- **`patterns/`**：每个文件记录一类失败模式或成功策略，含具体的失败案例证据和可操作的 workaround
- **`logs.md`**：按迭代时序记录「本轮做了什么」的演化日志
- **`skill-impact.md`**：记录每个 Skill 提案的内容 diff、验证分数、Accept/Reject 结果

这三个文件构成一个**客观审计链**：Skill Proposer 可以查到哪些方向曾经试过、结果如何，避免重蹈覆辙。

### 3. Skill Proposer（技能改进者）

以 **ReAct 风格**自主行动：
- 读取 Wiki 索引（而非全量内容，节省 context）
- 按需用 `read_file` 工具选择查看具体 pattern 页面和原始轨迹
- 每次只提出**一个原子改动**：要么创建新 Skill，要么对某个现有 Skill 做增量 patch

每个 Skill 目录包含两个文件：
- `SKILL.md`：完整的程序性指令
- `PURPOSE.md`：映射回激发这个 Skill 的 Wiki patterns——追踪"为什么这么改"

### 4. Gating & Rollback（质量门卫）

在验证集上评估候选 Skill：
- 比历史最佳分更高 → 接受，更新 `skill-impact.md`
- 否则 → 回滚 Skill，但 Wiki 照常保留这次尝试的记录

---

## 实验结果

### 横跨 5 个基准一致领先

测试覆盖：数学推理（LiveMath）、网页搜索（SealQA）、电子表格操作（SpreadSheet）、长文档问答（OfficeQA）、具身交互任务（ALFWorld）。

| 模型 | No Skill | 最佳基线 | WikiSkill | 相对提升 |
|---|---|---|---|---|
| Qwen-3.5-4B | 26.2 | 35.2（SkillOpt）| **38.5** | +3.3 |
| Qwen-3.5-9B | 29.9 | 42.3（EvoSkill）| **47.4** | +5.1 |
| Qwen-3.6-27B | 39.4 | 53.3（EvoSkill）| **63.3** | +10.0 |
| Gemma-4-31B | 41.3 | 49.1（SkillOpt）| **54.9** | +5.8 |
| Gemini-3.5-Flash | 49.5 | 56.1（EvoSkill）| **68.1** | +12.0 |

### Skill 进化与模型规模互补

在 Qwen 家族中，WikiSkill 带来的提升随规模增大而增大：4B +12.3%、9B +17.5%、27B +23.9%。

更有趣的发现：**Qwen-3.5-9B + WikiSkill（47.4%）> Qwen-3.6-27B 无 Skill（39.4%）**。小模型配合好的 Skill，可以超过大一个档次的裸模型。

### Skill 跨模型迁移

WikiSkill 进化出的 Skill 可以被其他模型使用。在 ALFWorld 上，Qwen-3.5-9B 使用 27B 进化出的 Skill 达到 70.2%，比用自己进化的 Skill（63.4%）还高。

这说明**「发现有用程序性知识」和「执行这些知识」是两种不同能力**，可以解耦——用强模型探索 Skill，再给弱模型使用。

---

## 工程落地：怎么自己实现一套 WikiSkill

论文只给出框架设计，没有开源代码（截至 2026-09-01）。但工程实现其实并不复杂——WikiSkill 的核心是**文件系统 + LLM 工具调用 + 循环编排**。

### 第一步：建立三层目录结构

```bash
mkdir -p workspace/{raw,wiki/patterns,skills}
touch workspace/wiki/logs.md
touch workspace/wiki/skill-impact.md
touch workspace/wiki/index.md
```

`wiki/index.md` 是 pattern 目录的索引，格式：

```markdown
# Wiki Pattern Index

| Pattern File | 类型 | 最后更新迭代 | 简述 |
|---|---|---|---|
| patterns/take-examine-loop.md | 失败模式 | Iter 2 | Agent 把物品取出后反复放回原位 |
| patterns/search-strategy.md | 成功策略 | Iter 3 | 网页搜索的三段式查询策略 |
```

### 第二步：Wiki Maintainer 的 Prompt 设计

```
你是 Wiki Maintainer。你的任务是从 Agent 执行轨迹中提取模式，更新持久知识库。

当前 Wiki 状态：
<wiki_context>{{wiki_index + existing_patterns}}</wiki_context>

本轮新增执行轨迹（成功 N 条，失败 M 条）：
<traces>{{sampled_traces}}</traces>

请完成以下工作：
1. 对失败轨迹做根因分析，识别共同的失败模式
2. 从成功轨迹提取可复用的成功策略
3. 对每个新发现：
   - 如果 wiki/patterns/ 里已有相关文件，追加新证据（写 patch，不要重写全文）
   - 如果是新模式，新建一个 pattern 文件，文件名用小写连字符
4. 更新 wiki/index.md
5. 在 wiki/logs.md 末尾追加本迭代的摘要

Pattern 文件格式：
---
pattern_type: failure_mode | success_strategy
first_seen: iter_N
severity: high | medium | low
---
## 描述
[一句话说明这个模式]

## 证据
- Iter N, task_id 07: [具体行为描述]

## 解决方案/策略
[具体的可操作的指令]
```

### 第三步：Skill Proposer 的 ReAct 设计

Skill Proposer 是一个**工具调用 Agent**，给它三个工具：

```python
tools = [
    {
        "name": "read_file",
        "description": "读取 wiki/patterns/ 下的某个 pattern 文件，或 raw/ 下的某条执行轨迹",
        "parameters": {"file_path": "string"}
    },
    {
        "name": "create_skill",
        "description": "在 skills/ 下创建一个新的 Skill，同时创建 PURPOSE.md",
        "parameters": {"skill_name": "string", "skill_md": "string", "purpose_md": "string"}
    },
    {
        "name": "edit_skill",
        "description": "对已有 Skill 做 patch 编辑（增量修改，不要重写全文）",
        "parameters": {"skill_name": "string", "patch": "unified_diff_string"}
    }
]
```

Proposer 的初始 prompt：

```
你是 Skill Proposer。你的任务是基于 Wiki 积累的知识，对 Skill 做一次原子性改进。

本轮训练任务结果摘要（pass/fail 列表）：
<outcomes>{{task_outcomes}}</outcomes>

Wiki 索引（按需读取具体 pattern）：
<wiki_index>{{index.md}}</wiki_index>

Skill 影响追踪（历史接受/拒绝记录）：
<skill_impact>{{skill-impact.md}}</skill_impact>

请：
1. 先用 read_file 读取最相关的 2-3 个 pattern 和失败 trace，诊断根因
2. 确定提案方向（不要重复 skill-impact.md 里已被拒绝过的相同方向）
3. 提出一个原子性改动：创建一个新 Skill，或对某个 Skill 做增量编辑
4. 调用对应工具执行

约束：
- 每次只提一个改动
- edit_skill 只写 unified diff，不要返回全文
- PURPOSE.md 必须明确引用激发此次改动的 wiki pattern 文件名
```

### 第四步：Gating 与 Wiki 更新的编排

```python
def wikiskill_iteration(workspace, train_tasks, val_tasks, model, best_score):
    # Step 1: Inference
    traces = run_inference(model, train_tasks, workspace.skills)
    save_traces(workspace.raw, traces)
    
    # Step 2: Wiki Maintainer
    run_wiki_maintainer(model, workspace.wiki, sample_traces(traces))
    
    # Step 3: Skill Proposer
    proposal = run_skill_proposer(model, workspace, traces)
    apply_proposal(workspace.skills, proposal)
    
    # Step 4: Gate
    val_score = run_inference(model, val_tasks, workspace.skills, score_only=True)
    
    if val_score > best_score:
        best_score = val_score
        acceptance = "Accepted"
    else:
        rollback_skills(workspace.skills, proposal)
        acceptance = "Rejected"
    
    # Wiki ALWAYS gets updated with outcome
    append_skill_impact(workspace.wiki, proposal, val_score, acceptance)
    
    return best_score
```

**最关键的一行**：`append_skill_impact` 无论 accept 还是 reject 都要执行。这就是 Wiki 和 Skill 生命周期不同的地方——失败本身也是知识。

### 第五步：与 Claude Code Skill 系统对接

WikiSkill 论文里的 Skill 格式（`SKILL.md` + frontmatter metadata）与 Anthropic Agent Skill 规范完全兼容。这意味着你可以：

1. **用 WikiSkill 进化 Claude Code Skill**：以真实的 Claude Code 任务执行结果为 raw traces
2. **直接把进化结果放入 `~/.claude/skills/`**：无需格式转换

在 Claude Code 场景下，Inference Agent 就是 Claude Code 本身，traces 就是 session 历史（JSONL 格式），工具是 Claude Code 的工具调用记录。

---

## 最近的开源参考实现

虽然 WikiSkill 本身暂无开源代码，但以下项目可以作为落地参考：

**[MineDojo/Voyager](https://github.com/MineDojo/Voyager)** — 最经典的开源 Skill 进化系统（Minecraft 场景），包含：自动课程、Skill 库、迭代 prompt 机制。结构上与 WikiSkill 最相似，区别是没有 Wiki 持久化层。

**[anthropics/skills](https://github.com/anthropics/skills)** — Anthropic 官方 Skill 格式参考，WikiSkill 的 `SKILL.md` 规范与此兼容。

**实现 WikiSkill 需要的关键组件：**
- 任何支持工具调用的 LLM API（Claude/GPT/Gemini）
- 文件系统（本地即可，无需向量数据库）
- 一个外层编排脚本（Python 50-100 行）

---

## 三个值得关注的发现

**1. Wiki 访问位置反直觉**

你可能认为给执行者（Inference Agent）也看 Wiki 会更好——结果相反。给 Inference Agent 看 Wiki 后性能下降：因为 Agent 会从 Wiki 直接抄答案，而不是真正执行 Skill，导致 traces 信息量降低，反而让进化更难。

**2. 知识发现与知识执行可以解耦**

让一个强模型来"探索并提炼"Skill，再让弱模型来"使用"这些 Skill，效果往往好于弱模型自我进化。这给出了一种实用的成本控制策略：用 27B 模型做 Skill 探索，用 4B 模型做推理服务。

**3. 复利的时间效应**

论文 Figure 3 的案例显示，Iteration 0 提出的 `goal-directed-action` 被拒绝了——但这个拒绝记录保存在 `skill-impact.md` 里。Iteration 1 的提案正是因为看到了这个失败历史，才提出了更具体的 `break-repetition-loop`，结果通过。**失败不会浪费，它成了下一次成功的先决条件。**

---

## 论文信息

**论文**：WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution  
**机构**：Google Research + Virginia Tech  
**作者**：Liyan Tang, Cyrus Rashtchian, Chun-Sung Ferng, Andrew Tomkins, Da-Cheng Juan, Tu Vu  
**arXiv**：[2608.27454](https://arxiv.org/abs/2608.27454)  
**发布时间**：2026 年 8 月 27 日

<!--EN-->

## The Problem: Experience Scatters After Every Run

Agent skill auto-evolution has advanced rapidly. Methods like EvoSkill, Trace2Skill, and SkillOpt share a common loop:

```
Execute tasks → Analyze trajectories → Propose skill edits → Validate → Keep or rollback
```

But they all share the same design flaw: **insights from each iteration remain scattered across proposal histories and temporary artifacts**. The next iteration can't build on "everything learned so far" — it rediscovers rather than compounds.

Inspired by Andrej Karpathy's "LLM Wiki" idea — compile experience into persistent, compounding knowledge — six Google Research researchers published **WikiSkill** (arXiv:2608.27454) on August 27, 2026.

---

## WikiSkill's Core Idea: Three-Layer Architecture

WikiSkill structures the agent workspace into three layers:

```
┌─────────────────────────────────────────┐
│  Skills Layer (skills/)                 │ ← Executable procedural knowledge. Reversible.
│  SKILL.md + PURPOSE.md                  │
├─────────────────────────────────────────┤
│  Wiki Layer (wiki/)    ← NEVER RESET    │ ← Structured knowledge. Compounds across iterations.
│  patterns/ + logs.md + skill-impact.md  │
├─────────────────────────────────────────┤
│  Raw Layer (raw/)                        │ ← Immutable execution traces. Write-once.
│  Complete agent interaction history      │
└─────────────────────────────────────────┘
```

**Key design decision: Wiki never rolls back. Skills can.**

When a skill update fails validation, the skill reverts — but the Wiki retains the failed attempt as a record that informs the next proposal.

---

## Four Roles in the Evolution Loop

### 1. Inference Agent (Executor)

Runs tasks using current skills, writes traces to `raw/`.

**Critical constraint: the Inference Agent cannot access the Wiki during training rollouts.**

The ablation (Table 3) shows that if the Inference Agent reads the Wiki during execution, it shortcuts answers through the Wiki rather than actually exercising the skills, degrading trace quality and hurting skill evolution (63.7% → 60.9%).

### 2. Wiki Maintainer (Knowledge Compiler)

Extracts patterns from traces, updates the Wiki:

- **`patterns/`**: One markdown file per failure mode or success strategy, with concrete evidence and actionable workarounds
- **`logs.md`**: Chronological record of "what happened this iteration"
- **`skill-impact.md`**: Per-proposal record of the diff, validation score, and Accept/Reject outcome

These three files form an **objective audit chain**: the Skill Proposer can see what directions were tried, with what result, and avoid repeating failed interventions.

### 3. Skill Proposer (Skill Improver)

Operates in **ReAct style**:
- Reads the Wiki index (not the full Wiki — preserves context budget)
- Selectively uses `read_file` to inspect specific pattern pages and raw traces on demand
- Proposes **one atomic change per iteration**: create a new skill or apply an incremental patch to an existing one

Each skill directory contains:
- `SKILL.md`: Full procedural instructions
- `PURPOSE.md`: Maps back to the Wiki patterns that motivated the change — tracing "why"

### 4. Gating & Rollback (Quality Gate)

Evaluates candidate skill on the validation split:
- Better than historical best → Accept; update `skill-impact.md`
- Otherwise → Rollback skill; Wiki still records the attempt

---

## Results

### Consistent Wins Across 5 Benchmarks

Benchmarks: mathematical reasoning (LiveMath), web search (SealQA), spreadsheet manipulation (SpreadSheet), long-context document QA (OfficeQA), embodied interactive tasks (ALFWorld).

| Model | No Skill | Best Baseline | WikiSkill | Gain |
|---|---|---|---|---|
| Qwen-3.5-4B | 26.2 | 35.2 (SkillOpt) | **38.5** | +3.3 |
| Qwen-3.5-9B | 29.9 | 42.3 (EvoSkill) | **47.4** | +5.1 |
| Qwen-3.6-27B | 39.4 | 53.3 (EvoSkill) | **63.3** | +10.0 |
| Gemma-4-31B | 41.3 | 49.1 (SkillOpt) | **54.9** | +5.8 |
| Gemini-3.5-Flash | 49.5 | 56.1 (EvoSkill) | **68.1** | +12.0 |

### Skill Evolution Complements Model Scaling

Within the Qwen family, WikiSkill gains increase with scale: 4B +12.3%, 9B +17.5%, 27B +23.9%.

More interesting: **Qwen-3.5-9B + WikiSkill (47.4%) > Qwen-3.6-27B without skills (39.4%)**. A smaller model with good skills can outperform a model three times larger.

### Cross-Model Skill Transfer

WikiSkill skills transfer across models. On ALFWorld, Qwen-3.5-9B using a 27B-evolved skill reaches 70.2%, compared to 63.4% with its own self-evolved skill.

This shows that **discovering procedural knowledge and executing it are two distinct capabilities** — you can decouple them: use a strong model to explore skills, then deploy them on a smaller inference model.

---

## Engineering Implementation: How to Build WikiSkill Yourself

No official open-source code yet (as of 2026-09-01). But the engineering is straightforward — WikiSkill is **filesystem + LLM tool calls + an outer loop**.

### Step 1: Set Up the Three-Layer Directory Structure

```bash
mkdir -p workspace/{raw,wiki/patterns,skills}
touch workspace/wiki/logs.md workspace/wiki/skill-impact.md workspace/wiki/index.md
```

`wiki/index.md` is the pattern directory index:

```markdown
# Wiki Pattern Index
| Pattern File | Type | Last Updated | Description |
|---|---|---|---|
| patterns/take-examine-loop.md | failure_mode | Iter 2 | Agent repeatedly returns items to origin |
| patterns/search-strategy.md | success_strategy | Iter 3 | Three-phase query strategy for web search |
```

### Step 2: Wiki Maintainer Prompt Design

```
You are the Wiki Maintainer. Extract patterns from agent traces and update the persistent knowledge base.

Current wiki state:
<wiki_context>{{wiki_index + existing_patterns}}</wiki_context>

New execution traces this iteration (N success, M failures):
<traces>{{sampled_traces}}</traces>

Tasks:
1. Root-cause analysis on failing traces — identify shared failure patterns
2. Extract reusable strategies from successful traces
3. For each finding:
   - If a related pattern file already exists: append new evidence (write a patch, don't rewrite)
   - If new: create a new pattern file (lowercase kebab-case name)
4. Update wiki/index.md
5. Append this iteration's summary to wiki/logs.md

Pattern file format:
---
pattern_type: failure_mode | success_strategy
first_seen: iter_N
severity: high | medium | low
---
## Description
[One sentence]

## Evidence
- Iter N, task_id 07: [specific behavior]

## Workaround / Strategy
[Concrete, actionable instructions]
```

### Step 3: Skill Proposer as a ReAct Agent

Give the Skill Proposer three tools:

```python
tools = [
    {"name": "read_file", "description": "Read a wiki pattern or raw trace file"},
    {"name": "create_skill", "description": "Create a new skill with SKILL.md and PURPOSE.md"},
    {"name": "edit_skill", "description": "Apply a patch to an existing skill (unified diff only)"}
]
```

Proposer's initial prompt:

```
You are the Skill Proposer. Make one atomic improvement to the skill set, informed by accumulated wiki knowledge.

Training task outcomes (pass/fail summary):
<outcomes>{{task_outcomes}}</outcomes>

Wiki index (read specific patterns on demand):
<wiki_index>{{index.md}}</wiki_index>

Skill impact tracker (history of accepted/rejected proposals):
<skill_impact>{{skill-impact.md}}</skill_impact>

Instructions:
1. Use read_file to inspect 2-3 most relevant patterns and failure traces
2. Identify root cause — check skill-impact.md to avoid repeating rejected directions
3. Propose one atomic change: create a new skill or incrementally edit an existing one
4. Call the appropriate tool

Constraints:
- One change per invocation
- edit_skill must use unified diff format, not full file rewrite
- PURPOSE.md must explicitly reference the wiki pattern files that motivated this change
```

### Step 4: The Outer Loop

```python
def wikiskill_iteration(workspace, train_tasks, val_tasks, model, best_score):
    traces = run_inference(model, train_tasks, workspace.skills)  # No wiki access!
    save_traces(workspace.raw, traces)

    run_wiki_maintainer(model, workspace.wiki, sample_traces(traces))
    
    proposal = run_skill_proposer(model, workspace, traces)
    apply_proposal(workspace.skills, proposal)
    
    val_score = evaluate(model, val_tasks, workspace.skills)
    
    if val_score > best_score:
        best_score = val_score
        acceptance = "Accepted"
    else:
        rollback_skills(workspace.skills, proposal)
        acceptance = "Rejected"
    
    append_skill_impact(workspace.wiki, proposal, val_score, acceptance)  # ALWAYS runs
    
    return best_score
```

The critical line: `append_skill_impact` runs regardless of accept or reject. Failure is knowledge.

### Step 5: Integration with Claude Code Skills

WikiSkill's `SKILL.md` format is fully compatible with Anthropic's Agent Skill spec. This means:

1. **Use WikiSkill to evolve Claude Code Skills**: Claude Code session histories (JSONL) are your raw traces
2. **Drop evolved skills directly into `~/.claude/skills/`**: no format conversion needed

In the Claude Code context, the Inference Agent *is* Claude Code, traces are session histories, and tools are Claude Code's tool-call records.

---

## Open-Source References

No official WikiSkill code yet. The closest open-source references:

**[MineDojo/Voyager](https://github.com/MineDojo/Voyager)** — The most well-known open skill evolution system (Minecraft). Has automatic curriculum, skill library, and iterative prompting. Architecturally closest to WikiSkill; the key missing piece is the persistent Wiki layer.

**[anthropics/skills](https://github.com/anthropics/skills)** — Anthropic's official Skill format reference. WikiSkill's `SKILL.md` spec is compatible.

**What you need to implement WikiSkill:**
- Any LLM API with tool calls (Claude/GPT/Gemini)
- A filesystem (local is fine; no vector database needed)
- An outer orchestration loop (~100 lines Python)

---

## Three Non-Obvious Findings

**1. Wiki access for the Inference Agent hurts**

Intuition says giving the executor access to all accumulated knowledge helps. The ablation says the opposite: the Inference Agent with wiki access shortcuts answers through the wiki instead of actually exercising skills, degrading trace quality and making skill evolution harder (63.7% → 60.9%).

**2. Skill discovery and execution can be decoupled**

Use a strong model to explore and distill skills; use a weaker model to run them. This often outperforms self-evolution by the weaker model — and gives a concrete cost-control strategy: 27B for skill discovery, 4B for serving.

**3. Failures compound into future success**

The case study (Figure 3) shows that iteration 0's `goal-directed-action` proposal was rejected. But that rejection was recorded in `skill-impact.md`. Iteration 1's proposal was informed by seeing that failure, leading to the more concrete `break-repetition-loop` — which was accepted. **Failed attempts don't disappear; they become prerequisites for the next success.**

---

**Paper**: WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution  
**Institution**: Google Research + Virginia Tech  
**Authors**: Liyan Tang, Cyrus Rashtchian, Chun-Sung Ferng, Andrew Tomkins, Da-Cheng Juan, Tu Vu  
**arXiv**: [2608.27454](https://arxiv.org/abs/2608.27454)  
**Published**: August 27, 2026
