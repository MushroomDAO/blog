---
title: "Loop Engineering：别再逐条写 Prompt，设计让 Agent 自己跑的循环系统"
titleEn: "Loop Engineering: Stop Prompting Agents One by One — Design the Loop That Runs Them"
description: "cobusgreyling/loop-engineering 是一套受 Boris Cherny（Anthropic Claude Code 负责人）启发的 AI Agent 循环工程框架，提供 loop-init、loop-audit、loop-gate 等工具，帮助开发者从「手动写 Prompt」转向「设计自主循环」。"
descriptionEn: "loop-engineering is an AI agent loop design toolkit inspired by Boris Cherny (Anthropic Claude Code lead) and Addy Osmani. It provides loop-init, loop-audit, loop-gate, and other tools to shift developers from hand-prompting to designing autonomous coding loops."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["AI", "Agent", "Claude Code", "开发工具", "自动化", "开源", "MCP"]
heroImage: "../../assets/images/loop-engineering-ai-agent-loop-banner.jpg"
---

> **GitHub**：[cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering) · MIT  
> **快速初始化**：`npx @cobusgreyling/loop-init .`

---

## 起点：一句改变工作方式的话

> "I don't prompt Claude anymore. I have loops running that prompt Claude."  
> — Boris Cherny，Anthropic Claude Code 负责人

这句话在开发者社区里流传很广，但很少有人把它真正落地成可操作的工程实践。loop-engineering 做的就是这件事：**把"设计循环来驱动 Agent"从一个理念变成一套工具和规范。**

---

## 什么是 Loop Engineering

Loop Engineering 的核心观点是：

**与其每次手动告诉 AI Agent 做什么，不如设计一个系统——这个系统自动知道什么时候触发 Agent、给 Agent 什么上下文、以什么标准判断 Agent 做没做好。**

Addy Osmani（Chrome DevTools 负责人）在讨论 AI 编程时也说过类似的话：高效使用 AI 的关键不在于写好的 prompt，而在于设计好的**反馈循环**——让 Agent 能自我校正、持续推进、在有人监督的边界内自主运行。

这个框架就是把这些理念具体化：

- **Automations / Scheduling**：什么条件触发 Agent 工作？（Cron、Git hook、文件变化、CI 事件）
- **Worktrees**：Agent 在隔离环境里工作，不污染主分支
- **Skills**：给 Agent 领域知识包（`.claude/skills/`），让它在任务前就知道项目规范
- **Plugins / MCP**：Agent 可以调用的工具集（数据库、浏览器、API）
- **Sub-agents + Memory**：子 Agent 处理并行任务，Memory 保持跨 session 上下文

---

## 工具集

### `loop-init`：初始化一个自主编码循环

```bash
npx @cobusgreyling/loop-init .
```

在你的项目根目录运行后，它会创建：

```
.claude/
├── CLAUDE.md          # Agent 工作规范和项目上下文
├── skills/
│   └── domain.md      # 领域知识包
├── loops/
│   └── default.yaml   # 循环配置（触发条件、质量门、上下文注入）
└── memory/            # 跨 session 记忆
```

### `loop-audit`：循环健康评分

```bash
npx @cobusgreyling/loop-audit .
```

输出一个 0-100 的循环成熟度分数，检查项目包括：
- CLAUDE.md 是否存在且内容质量如何
- Skills 是否配置
- Memory 系统是否有效
- 质量门（lint/test）是否配置
- 自动化触发是否就绪

### `loop-gate`：质量门

质量门是循环里的关键卡点：Agent 完成工作后，必须通过质量门才能合入主分支。

```yaml
# .claude/loops/default.yaml
gates:
  - lint: "pnpm lint"
  - test: "pnpm test"
  - typecheck: "npx tsc --noEmit"
```

质量门失败 → Agent 自动重试修复 → 再次通过质量门 → 合入。

### `loop-cost`：Token 预算估算

```bash
npx @cobusgreyling/loop-cost .
```

在运行循环前估算 token 消耗，避免意外账单。

### `loop-sync`：漂移检测

检测 Agent 工作是否和预期方向发生了"漂移"：
- Worktree 是否和主分支出现了未预期的分叉
- CLAUDE.md 里的规范是否还和实际代码匹配

### `loop-context`：记忆管理

管理跨 session 的上下文记忆，确保 Agent 在重启后还能保持连续性。

### `loop-mcp-server`：MCP 协议服务器

把 loop-engineering 的能力暴露为 MCP 工具，让 Claude Code 可以直接调用循环管理能力。

### `loop-worktree`：Git Worktree 管理

Agent 每个任务在独立 worktree 里工作，完成后 merge 或丢弃，不污染主分支状态。

---

## 一个完整的循环是什么样的

假设你在做一个 Web 项目，配置一个覆盖"每天自动优化代码质量"的循环：

```yaml
# .claude/loops/code-quality.yaml
name: daily-code-quality
trigger:
  cron: "0 9 * * 1-5"   # 工作日早上 9 点
context:
  - CLAUDE.md            # 项目规范
  - skills/typescript.md # TypeScript 领域知识
  - memory/recent.md     # 近期 context
task: |
  检查最近 7 天修改的文件：
  1. 找出 TODO 注释并创建对应 issue
  2. 找出明显的性能问题（不必要的重渲染、未使用的 import）
  3. 修复 lint 警告
  不要修改业务逻辑，只做代码质量改进。
gates:
  - "pnpm lint"
  - "pnpm test"
worktree: true           # 在隔离 worktree 里工作
pr: true                 # 完成后自动开 PR 等待 review
```

每个工作日早上，这个循环自动：
1. 拉取最新代码，创建 worktree
2. 给 Claude Code 注入项目 context 和领域知识
3. 让 Claude Code 执行质量改进任务
4. 跑质量门（lint + test）
5. 通过后自动开 PR，供人工 review

你不需要每天记得去查"今天有没有 lint 警告"，循环帮你记住了。

---

## 为什么这个模式重要

手动写 prompt 的问题在于：**它是一次性的，无法积累。** 今天写了一个好 prompt，明天换个任务全部重来。你的经验没有沉淀进系统，只沉淀在你的大脑里。

Loop Engineering 模式的不同在于：
- **Skills 文件**积累了领域知识，每次 Agent 工作都会读取
- **Memory 系统**记住了跨 session 的决策和上下文
- **CLAUDE.md** 把团队规范编码成 Agent 每次都会遵循的约束
- **质量门**把"什么叫做完成"变成可验证的标准，而不是靠人来检查

随着时间推移，系统越来越聪明——不是因为模型变了，而是因为你给 Agent 准备的上下文和约束越来越完整。

---

## 快速体验

```bash
# 在任意有 CLAUDE.md 的项目里
npx @cobusgreyling/loop-init .

# 查看当前循环健康度
npx @cobusgreyling/loop-audit .

# 估算一次循环的 token 消耗
npx @cobusgreyling/loop-cost .
```

---

## 和 Claude Code 原生功能的关系

loop-engineering 不是替代 Claude Code，而是在 Claude Code 的基础上加了一层调度和规范层：

- **Claude Code** 负责执行具体编码任务
- **loop-engineering** 负责决定什么时候触发、给什么 context、用什么标准验收

这两层分开的好处是：你可以在不改变 Claude Code 行为的情况下，改变循环的触发逻辑和质量标准。

---

## 一句话总结

Loop Engineering 把 "AI 编程助手" 从一个随叫随到的工具，变成一个在你睡觉时也在持续改进代码的自主系统。Boris Cherny 说"我不再给 Claude 写 prompt，我让循环来给 Claude 写 prompt"——loop-engineering 就是这句话的工程实现。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Loop Engineering: Stop Prompting Agents — Design the System That Prompts Them

**GitHub**: [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering) · MIT  
**Quick start**: `npx @cobusgreyling/loop-init .`

### The Starting Point

> "I don't prompt Claude anymore. I have loops running that prompt Claude."  
> — Boris Cherny, Head of Claude Code at Anthropic

Loop Engineering takes this idea and turns it into an operational toolkit.

### What the Toolkit Does

| Tool | Function |
|---|---|
| `loop-init` | Scaffold `.claude/` structure (CLAUDE.md, skills, loops, memory) |
| `loop-audit` | Score loop maturity (0-100), identify missing pieces |
| `loop-cost` | Estimate token budget before running |
| `loop-gate` | Quality gates (lint/test/CI) that block Agent completion until passing |
| `loop-sync` | Detect drift between Agent work and expected direction |
| `loop-context` | Cross-session memory manager |
| `loop-mcp-server` | Expose loop management as MCP tools |
| `loop-worktree` | Git worktree isolation per Agent task |

### The 5 Building Blocks

Loop Engineering structures autonomous coding around five pillars:

1. **Automations / Scheduling**: When does the loop trigger? (Cron, Git hooks, file changes, CI events)
2. **Worktrees**: Agent works in isolation, doesn't pollute the main branch
3. **Skills**: Domain knowledge packages (`.claude/skills/`) — the Agent knows your project conventions before starting
4. **Plugins / MCP**: Tool access (databases, browsers, APIs)
5. **Sub-agents + Memory**: Parallel task handling + cross-session context continuity

### Why This Matters

Hand-prompting AI is episodic — each session starts from scratch. Loop Engineering makes the system accumulate: Skills carry domain knowledge forward, Memory preserves decisions across sessions, CLAUDE.md encodes team standards as invariants the Agent always follows, and quality gates define "done" as a verifiable standard rather than a human judgment call.

The system gets smarter over time — not because the model improves, but because the context and constraints you give the Agent keep getting richer.

### Quick Start

```bash
npx @cobusgreyling/loop-init .   # scaffold the loop structure
npx @cobusgreyling/loop-audit .  # check loop readiness score
npx @cobusgreyling/loop-cost .   # estimate token budget
```

### Relationship to Claude Code

Loop Engineering doesn't replace Claude Code — it adds a scheduling and standards layer on top. Claude Code handles task execution; loop-engineering handles when to trigger, what context to inject, and how to verify completion.

### Bottom Line

Loop Engineering is the engineering implementation of "having loops that prompt Claude." Instead of a tool you query, you build a system that continuously improves your codebase while you're doing other things.

© 2026 Author: Mycelium Protocol
