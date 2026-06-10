---
title: "70 万人看过的 Agentic Engineering 心得：Matt Van Horn 22 条实战技巧全解析"
description: "last30days（2.7 万星）作者 Matt Van Horn 在 X 发布《我所知道的所有 Agentic Engineering 技巧》，70 万次浏览。本文汇编他的完整方法论：从 /ce-plan 规划范式、语音驱动开发、并行会话管理到 Compound Engineering，帮助 AI 工程师从 Vibe Coding 进化为真正的 Agentic Engineering。"
titleEn: "700K Views: Matt Van Horn's Complete Agentic Engineering Hacks — All 22 Techniques Analyzed"
descriptionEn: "Matt Van Horn (author of last30days, 27k stars) published 'Every Agentic Engineering Hack I Know' on X to 700k views. This article synthesizes his complete methodology: /ce-plan planning paradigm, voice-driven development, parallel session management, and Compound Engineering — the full progression from Vibe Coding to real Agentic Engineering."
pubDate: 2026-06-10
category: "Research"
tags: ["AgenticEngineering", "ClaudeCode", "MattVanHorn", "last30days", "CompoundEngineering", "VibeCoding", "AI工程师", "效率工具"]
lang: "zh-CN"
heroImage: "../../assets/images/matt-van-horn-agentic-engineering-hacks.jpg"
---

## 这篇文章的来源

2026 年 6 月，[Matt Van Horn](https://x.com/mvanhorn)（[@mvanhorn](https://x.com/mvanhorn)）在 X 发布了一篇长文：

> **[Every Agentic Engineering Hack I Know（June 2026）](https://x.com/mvanhorn/article/2061877533885473181)**

他的 TL;DR 推文原文：

> *"TL;DR of my new article: every Agentic Engineering hack I know. This used to be vibe coding. Around last Thanksgiving it got good enough to become something real.*
> *📝 The moment you have an idea → /ce-plan a plan.md, with Compound Engineering by @kieranklaassen + @trevin."*

这篇文章获得了超过 **70 万次浏览**——他上一篇同类文章（2026 年 3 月）获得了 **90 万次浏览**。

---

## Matt Van Horn 是谁

Matt Van Horn 不是一个典型的 KOL，他是一个真正在用 AI 写代码的人：

- **June 联合创始人兼 CEO**（被 Weber 收购），做了一个"自动驾驶烤箱"
- **Lyft 早期员工**，参与了 Lyft 的创业期
- **[last30days](https://github.com/mvanhorn/last30days-skill)**（**2.7 万颗星**，GitHub 日榜 #1）：AI 智能体技能，跨 Reddit/X/YouTube/HN/TikTok/Polymarket 并行搜索，按真实互动权重排序，输出人们实际关心的内容
- **[Printing Press](https://github.com/mvanhorn/printing-press)**（4.2k 星）：为任何 API 自动生成 agent-first CLI
- **agentcookie**：通过 Tailscale 跨机器同步加密的 agent 浏览器 session

他为什么有说服力？因为他在开源社区（Python、Go、OpenCV、Vercel Agent Browser、OpenClaw）有大量真实贡献，他的方法论来自实际 commit，不是观点文章。

---

## 核心转折：从 Vibe Coding 到 Agentic Engineering

Matt 的判断："**这曾经是 Vibe Coding，去年感恩节前后它变得足够好，成了真正有价值的东西。**"

这句话很重要。Vibe Coding 的定义是：把代码所有权交给 AI，自己不理解也不检查。而他所说的 Agentic Engineering 是：**工程判断力还在你手里，AI 智能体负责执行，你负责规划、架构和验收**。

两者最根本的区别：
- Vibe Coding：我描述，AI 交付，我不管对不对
- Agentic Engineering：我设计结构，AI 执行细节，我验证结果

---

## 技巧全解析：他的完整方法论

### 第一层：规划驱动（Planning First）

**① 有想法时立刻 `/ce-plan` 生成 plan.md**

这是整个方法论的核心。不要直接让 AI 写代码——先让 AI 研究你的代码库、查阅文档、搜索社区经验，然后把所有发现整合进一个 `plan.md`。

plan.md 的结构：
```
- 问题是什么
- 采用什么方案（及为什么）
- 要触碰哪些文件
- 验收标准
- 从你的代码库中参考的模式
```

**为什么这很重要**：plan.md 是"跨会话存活的检查点"。会话断了，换工具了，换模型了，plan.md 都在。

---

**② `/ce-plan` 的背后是并行研究智能体**

`/ce-plan` 不是单个对话，而是多个并行 agent 同时运行：
- Agent A：读你的代码库
- Agent B：搜索相关框架文档和已知 bug
- Agent C：用 `/last30days` 搜索社区最近 30 天的讨论

所有发现汇聚到 plan.md，这个计划是被现实数据支撑的，不是 AI 的训练集幻觉。

---

**③ `/ce-work` 从 plan 执行**

执行阶段：`/ce-work` 读取 plan.md，拆解任务，实现代码，跑测试，打勾验收。

关键：**plan 和执行是分开的**。你可以在计划阶段暂停和修改，确认方向正确再开始执行。

---

### 第二层：研究驱动（Research Before Planning）

**④ `/last30days` 是规划前的必要步骤**

在开始 `/ce-plan` 之前，先用 `/last30days` 研究这个话题：

```
/last30days 选 agent-browser 还是 Playwright
```

输出：78 个 Reddit 讨论、76 条 X 帖子、22 个 YouTube 视频、15 个 HN 故事——以及它们的综合结论。

**这解决了一个核心问题**：LLM 的训练数据有截止日期，而工程决策需要基于当前社区实践，不是 6 个月前的主流观点。

---

**⑤ 用会议录音 + `/ce-plan` 做产品提案**

用 Granola 记录会议/对话，然后：

```
/ce-plan 把这段录音变成一份产品提案
```

Claude Code 会把会议录音和现有代码库交叉对比，生成结构化的产品文档——不需要你手动整理笔记。

---

### 第三层：并行开发（Parallel Sessions）

**⑥ 4-6 个 Ghostty 窗口同时运行**

Matt 的标配：同时跑 4-6 个 Claude Code 会话，每个负责不同任务：
- 窗口 1：在 `/ce-plan` 研究下一个任务
- 窗口 2：在 `/ce-work` 执行当前计划
- 窗口 3：在处理 bug
- 窗口 4：在处理另一个独立模块

本质是**装配线工作流**：每个会话像独立的生产线，你作为监督者，不是流水线工人。

---

**⑦ 音频完成信号——让 AI 叫你**

配置任务完成时播放系统声音：
```json
// ~/.claude/settings.json
{
  "completionSound": true
}
```

效果：你同时管 4-6 个会话，不需要盯着屏幕。AI 完成时会叫你，你去 review 再启动下一步。

---

**⑧ Zed 500ms 自动保存**

Zed 编辑器配置 500ms 自动保存，实现 AI 写的内容和你的编辑实时同步——人类和 AI 在同一个文件上协作而不互相覆盖。

---

### 第四层：配置优化（Configuration）

**⑨ Bypass 权限：这是不可妥协的**

```json
// ~/.claude/settings.json
{
  "skipDangerousModePermissionPrompt": true
}
```

每次弹出"允许？"都打断会话节奏。4-6 个并行会话时，这个提示是致命的瓶颈。开启后，你从"审批员"变成"监督者"——整体看方向，不看每一步。

---

**⑩ 语音作为主要输入**

工具：Monologue 或 WhisperFlow。用语音向 Claude Code 发指令，现代 LLM 能从不完美的语音转写中重建意图。

Matt 描述：他曾在开车时用语音口述了文章的多个段落。

适合场景：
- 离开键盘时发指令
- 需要快速说清楚上下文时
- 复杂想法用口语表达比打字快时

---

### 第五层：远程与移动工作流

**⑪ Mac Mini + OpenClaw + tmux：会话永远不死**

架构：
- Mac Mini 持续运行 OpenClaw（本地 Claude Code 服务器）
- tmux 会话持久化，网络断开不丢失状态
- SSH 连接断开后 tmux 继续运行

**⑫ Telegram → `/ce-plan`：离桌时也在工作**

手机发 Telegram 消息给 Mac Mini 上的 bot：
```
/ce-plan 研究下 Rust 异步运行时的最新社区实践
```

计划在后台执行，你回到桌子时 plan.md 已经准备好了。

---

**⑬ tmux over 飞机 WiFi：在 11,000 米高空 ship 功能**

飞机 WiFi 连接不稳定，直接 SSH 会断。用 tmux：连接断了，会话在服务器上继续运行；重新连上，继续从断点看。Matt 声称在长途飞行时用这个工作流交付过功能。

---

### 第六层：成本控制

**⑭ Claude Max + Codex 双账号**

- **Claude Max**（$200/月）：Opus 复杂推理任务、规划、架构决策
- **Codex**（$200/月）：实现任务、执行细节

策略：复杂、需要判断的任务给 Opus，大量执行任务路由给 Codex。不是一个账号打天下。

---

### 第七层：产品化方法论（Agent-Native CLI）

**⑮~⑲ 10 条 Agent-Native CLI 原则**

Matt 发布了"构建 Agent-Native CLI 的 10 条原则"，分为两层：

**Tier 1：Table Stakes（基础要求，不做会崩）**
1. 跨 CLI 统一词汇（`--format json` 在所有命令一致）
2. 三层自检（`cli info`/`cli health`/`cli debug`）
3. 异步感知执行（长任务给 job ID，可轮询状态）
4. 结构化输出（JSON 优先，不是 grep 文本）
5. 幂等操作（重复运行不产生副作用）

**Tier 2：Compounding（让 CLI 越用越好）**
6. 操作历史（agent 可查"我上次做了什么"）
7. 能力发现（`cli capabilities` 返回机器可读的功能列表）
8. 上下文传递（`--context` 参数让 agent 携带状态）
9. 错误语义（错误码有含义，agent 能决策重试还是放弃）
10. 向后兼容语义版本（`cli version` + changelog 让 agent 知道 API 变了）

---

### 第八层：记忆与上下文

**⑳ CLAUDE.md 是 agent 的长期记忆**

CLAUDE.md 的价值不是"告诉 Claude 用什么框架"，而是把你的工程判断持久化：

```markdown
# 构建命令
pnpm run build

# 测试：运行 pnpm test 后必须全绿才算完成

# 这个项目的架构约定
- 所有 API 调用都通过 src/api/ 层，不直接在组件里 fetch
- 错误处理统一在 middleware/error.ts
```

CLAUDE.md 让每个新会话都不需要重新解释项目上下文。

---

**㉑ plan 里加"参考你自己的代码模式"**

plan.md 里专门有一节：让 AI 搜索你的代码库里已有的实现模式，新功能要和已有风格一致。这解决了 AI 总是引入新的"最新最好"方案、导致代码风格碎片化的问题。

---

**㉒ 用 subagent review plan 本身**

计划写完后，再启动一个 subagent：

```
review 这个 plan.md，确认：
1. 每个需求都有对应的实现步骤
2. 边界情况都有测试覆盖
3. 没有遗漏的依赖
```

在执行前用独立视角检查计划。

---

## 给 Agent 工程师的学习路径

### 从 Vibe Coding 进化的三个阶段

**阶段一（Vibe Coding）**：直接问 AI "帮我写这个功能"，AI 给什么用什么，不懂也不管。

**阶段二（结构化 Prompting）**：学会写好的 CLAUDE.md，拆分任务，检查输出。但本质上还是单线程、单会话。

**阶段三（Agentic Engineering）**：有规划范式（plan.md），有并行会话，有研究工具（/last30days），有自主触发机制（Telegram/cron），把 AI 当成一个需要管理的工程团队，而不是一个对话伙伴。

### 从今天就能用的三件事

**① 从 CLAUDE.md 开始**：如果你的项目没有 CLAUDE.md，这是最高 ROI 的起点。加上构建命令、测试命令、核心架构约定。

**② 建立 plan.md 习惯**：下次有任何非 trivial 任务，先让 AI 写一个 plan，review 计划之后再开始执行。

**③ 安装 last30days**：
```
/plugin marketplace add mvanhorn/last30days-skill
/plugin install last30days
```
在做任何重要技术决策前，先跑一次 `/last30days [你的问题]`，看社区最近 30 天真实怎么说。

---

## Matt 的核心观点（原文摘要）

> **"The moment you have an idea → /ce-plan a plan.md"**

> **"This used to be vibe coding. Around last Thanksgiving it got good enough to become something real."**

> **"Structure, planning, and parallel execution matter more than which specific tools appear in your dock."**

> **"You don't need the latest agentic harness. You need to spend more time doing than speculating."**（来自他的其他采访）

---

## 资源汇总

| 资源 | 链接 |
|------|------|
| X 原文（June 2026 文章） | [Every Agentic Engineering Hack I Know](https://x.com/mvanhorn/article/2061877533885473181) |
| TL;DR 推文 | [@mvanhorn](https://x.com/mvanhorn/status/2061978364391592110) |
| last30days GitHub | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)（27k ⭐） |
| Printing Press | [mvanhorn/printing-press](https://github.com/mvanhorn/printing-press) |
| Compound Engineering | [@kieranklaassen](https://x.com/kieranklaassen) |
| Matt Van Horn X | [@mvanhorn](https://x.com/mvanhorn) |

---

*注：X 原文需要付费账号访问。本文综合了 Matt Van Horn 的 TL;DR 推文、March 2026 文章（gu-log 摘要）和多个来源的技术分析，完整呈现其方法论体系。部分技巧在他的两篇文章中均有提及。*

<!--EN-->

## 700K Views: Matt Van Horn's Complete Agentic Engineering Hacks

In June 2026, [Matt Van Horn](https://x.com/mvanhorn) published **[Every Agentic Engineering Hack I Know](https://x.com/mvanhorn/article/2061877533885473181)** on X to over 700,000 views. His March 2026 edition had 900,000 views. This article synthesizes his complete methodology.

**His TL;DR tweet:**
> *"TL;DR of my new article: every Agentic Engineering hack I know. This used to be vibe coding. Around last Thanksgiving it got good enough to become something real.*
> *📝 The moment you have an idea → /ce-plan a plan.md, with Compound Engineering by @kieranklaassen + @trevin."*

---

## Who Is Matt Van Horn

- Co-founder & CEO of **June** (acquired by Weber) — built a "self-driving oven"
- Early team member at **Lyft**
- Creator of **[last30days](https://github.com/mvanhorn/last30days-skill)** (27k ⭐, GitHub trending #1): AI agent skill searching Reddit/X/YouTube/HN/TikTok/Polymarket in parallel, ranked by real engagement
- Creator of **Printing Press** (4.2k ⭐): auto-generates agent-first CLIs for any API
- Active open-source contributor across Python, Go, OpenCV, Vercel Agent Browser, OpenClaw (200+ repos)

---

## The Core Shift: Vibe Coding → Agentic Engineering

**Vibe Coding**: delegate code ownership to AI, don't understand or review the output.

**Agentic Engineering**: your engineering judgment stays in the driver's seat. AI agents handle execution; you handle planning, architecture, and acceptance.

The evolution happened around Thanksgiving 2025 — the tools got reliable enough that it stopped being a curiosity and became a real workflow.

---

## The Complete Technique Stack

### Layer 1: Planning-First

**① `/ce-plan` a plan.md the moment you have an idea**

Don't code first — research first. `/ce-plan` launches parallel agents that examine your codebase, search framework docs, query community experience, and consolidate everything into a structured `plan.md`:

```
- What is wrong
- What approach to take (and why)
- What files to touch
- Acceptance criteria
- Patterns to follow from your own codebase
```

The plan is "the checkpoint that survives everything" — session breaks, tool changes, model switches.

**② `/ce-work` executes from the plan**

`/ce-work` reads `plan.md`, breaks it into tasks, implements, runs tests, checks off acceptance criteria. Planning and execution are explicitly separated — you verify direction before work begins.

### Layer 2: Research-Driven

**③ `/last30days` before planning**

```
/last30days agent-browser vs Playwright
```

Returns: 78 Reddit threads, 76 X posts, 22 YouTube videos, 15 HN stories — synthesized by what people actually engaged with. LLM training data has a cutoff; engineering decisions need current community signal.

**④ Meeting recordings → product proposals**

Record conversations with Granola, then:
```
/ce-plan turn this into a product proposal
```
Claude Code cross-references the transcript against your existing codebase, producing structured output without manual note-taking.

### Layer 3: Parallel Sessions

**⑤ 4-6 Ghostty windows simultaneously**

- Window 1: `/ce-plan` researching next task
- Window 2: `/ce-work` executing current plan
- Window 3: debugging
- Window 4: independent module

Assembly-line workflow — you're the supervisor, not the worker.

**⑥ Audio completion signals**

Configure task-completion sounds so sessions notify you when done. You manage 4-6 sessions without staring at screens.

**⑦ Zed 500ms autosave**

Real-time collaboration between human and AI editing on the same file without overwriting each other.

### Layer 4: Configuration

**⑧ Bypass permissions — non-negotiable**

```json
// ~/.claude/settings.json
{
  "skipDangerousModePermissionPrompt": true
}
```

Every "Allow?" prompt breaks flow across 4-6 parallel sessions. With bypass: you shift from approver to supervisor.

**⑨ Voice as primary input**

Tools: Monologue or WhisperFlow. Modern LLMs reconstruct intent from imperfect transcription. Matt dictated article sections while driving.

### Layer 5: Remote Workflow

**⑩ Mac Mini + OpenClaw + tmux**

Persistent sessions that survive network drops. SSH reconnects pick up exactly where you left off.

**⑪ Telegram → `/ce-plan`**

Send plan commands from your phone while away. Plans develop in background; they're ready when you return.

**⑫ tmux over airplane WiFi**

Unreliable connections don't kill sessions. Ship features on long-haul flights.

### Layer 6: Cost Control

**⑬ Claude Max + Codex dual accounts**

- **Claude Max** ($200/mo): complex reasoning, planning, architecture
- **Codex** ($200/mo): implementation, execution

Route by complexity, not convenience.

### Layer 7: Agent-Native CLI Principles

**Tier 1 (Table Stakes):**
- Consistent cross-CLI vocabulary (`--format json` works the same everywhere)
- Three-layer introspection (`info`/`health`/`debug`)
- Async-aware execution (job IDs for long tasks)
- Structured output (JSON-first)
- Idempotent operations

**Tier 2 (Compounding):**
- Operation history (agents can query "what did I do last time")
- Capability discovery
- Context passing
- Error semantics
- Semantic versioning

### Layer 8: Memory & Context

**⑭ CLAUDE.md as persistent engineering judgment**

Not just "what framework to use" — encode your architectural decisions, patterns, and conventions so every new session starts context-aware.

**⑮ Plan.md includes "follow your own code patterns"**

Prevents AI from introducing new approaches that fragment code style.

**⑯ Subagent reviews the plan before execution**

```
Review this plan.md: is every requirement covered? 
Are edge cases tested? Are dependencies complete?
```

Independent perspective before work begins.

---

## Three Things to Start Today

**① Write a CLAUDE.md** — highest ROI starting point. Add build/test commands and core architectural conventions.

**② Build the plan.md habit** — for any non-trivial task, have AI write a plan first, review it, then execute.

**③ Install last30days:**
```
/plugin marketplace add mvanhorn/last30days-skill
/plugin install last30days
```
Run `/last30days [your question]` before any significant technical decision.

---

## Resources

| Resource | Link |
|----------|------|
| Original X Article (June 2026) | [Every Agentic Engineering Hack I Know](https://x.com/mvanhorn/article/2061877533885473181) |
| TL;DR tweet | [x.com/mvanhorn](https://x.com/mvanhorn/status/2061978364391592110) |
| last30days | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) (27k ⭐) |
| Compound Engineering | [@kieranklaassen](https://x.com/kieranklaassen) |
| Matt Van Horn | [@mvanhorn](https://x.com/mvanhorn) |

*Note: The full X article requires a paid subscription. This synthesis draws from Matt Van Horn's TL;DR tweet, his March 2026 article (via gu-log summary), and multiple community sources documenting his methodology.*
