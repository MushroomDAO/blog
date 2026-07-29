---
title: "Vibe Coding 的正确打开方式：KhazP 的 5 步结构化工作流——从想法到 MVP 不迷路"
description: "GitHub 2700+ Star 的 vibe-coding-prompt-template 不是一套 prompt，而是一套完整的 AI 编程方法论：先在 Chat 里完成市场调研、PRD、技术设计，再进 IDE 生成 AGENTS.md 让 Agent 拥有完整上下文，最后 Plan→Execute→Verify 循环推进到 MVP。支持 Claude Code、Cursor、Codex、Gemini CLI。"
pubDate: "2026-07-29"
category: "Tech-Experiment"
heroImage: "../../assets/images/vibe-coding-prompt-template-khazp-agents-md-prd-mvp-workflow-guide-banner.jpg"
---

大多数人用 vibe coding 的姿势是：打开 Cursor，直接说"帮我做一个 XX 应用"，然后陷入 Agent 改了又改、越改越乱的死循环。

[KhazP/vibe-coding-prompt-template](https://github.com/KhazP/vibe-coding-prompt-template) 解决的正是这个问题。2700+ Star，被用来真实交付了 vibeworkflow.app、moneyvisualiser.com、RealDex App 等项目。它的核心论点只有一句话：

> **先做思考，再给工具干净的上下文，然后保持构建节奏。**

---

## 一、为什么 vibe coding 会失控

AI 编程 Agent 的最大弱点是**上下文衰减**：对话越长，它越忘记最初的约定，越容易偏离方向，越容易在"先完成功能"和"维护代码质量"之间做错误的权衡。

这套工作流的解法是：**在开始编码之前，把所有决策写成文件**，让 Agent 每次都能从文件里重建完整的上下文，而不依赖对话历史。

---

## 二、五步工作流

整个流程分两个阶段：

```
Phase 1（Chat 里完成，不需要代码仓库）
  Step 1: 深度调研 → research-[AppName].md
  Step 2: PRD → PRD-[AppName]-MVP.md
  Step 3: 技术设计 → TechDesign-[AppName]-MVP.md

Phase 2（进 IDE 执行）
  Step 4: 生成 AGENTS.md 等配置文件
  Step 5: Build MVP（Plan → Execute → Verify 循环）
```

### Phase 1：思考阶段（在 ChatGPT、Claude、Gemini 里完成）

**Step 1：深度调研**（`part1-deepresearch.md`，17KB）

这一步的目的是**快速判断想法是否值得做**。把 `part1-deepresearch.md` 整个内容粘贴到任意 AI Chat，AI 会问你关于想法的几个问题，然后生成一份包含需求验证、竞品分析、可行性判断的调研报告。

建议开启 Web Search——让 AI 用实时数据而不是训练数据里的竞品信息。

**Step 2：PRD**（`part2-prd-mvp.md`，28KB）

把 Step 1 的输出粘贴进来，再粘贴 `part2-prd-mvp.md`，生成明确的产品需求文档：

- 必须有的功能（Must-have）
- 暂不做的功能（Out of scope）
- 成功指标（Success metrics）
- UI/UX 要求

这一步最重要的产出是 **Out of scope 列表**。明确不做什么，比明确做什么更能保住 MVP 的边界。

**Step 3：技术设计**（`part3-tech-design-mvp.md`，25KB）

技术方案不是越先进越好，而是越**能实际交付**越好。这一步会讨论：

- 技术栈权衡（全代码 vs no-code builder）
- 预算和时间约束下的合理选择
- 数据模型和项目目录结构
- 部署平台

---

### Phase 2：执行阶段（进 IDE）

**Step 4：生成 Agent 配置文件**（`part4-notes-for-agent.md`，18KB）

这是整个工作流的核心杠杆。把 PRD 和技术设计文档放进 `docs/` 目录，在 IDE 里对 Agent 说：

```
"Read part4-notes-for-agent.md, follow its instructions, and set up my workspace."
```

Agent 会从 `templates/` 目录把以下文件复制到项目根目录并填入所有占位符：

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | AI Agent 的主指令文件（单一事实来源） |
| `MEMORY.md` | Session 记忆：决策、已知问题、当前目标 |
| `REVIEW-CHECKLIST.md` | 定义"完成"的标准 |
| `agent_docs/tech_stack.md` | 技术栈细节 |
| `agent_docs/code_patterns.md` | 架构和代码风格规则 |
| `agent_docs/project_brief.md` | 产品愿景 |
| `agent_docs/product_requirements.md` | 功能列表 |

同时生成对应 IDE 的适配器文件：
- Claude Code → `CLAUDE.md` + `.claude/skills/`（含 `/vibe-*` 斜杠命令）
- Cursor → `.cursor/rules/vibe.mdc`
- Codex → 直接读 `AGENTS.md`（无需额外适配）
- Antigravity → `.agent/rules/vibe.md`

**Step 5：Build MVP**

给 Agent 的第一条命令：

```
"Read AGENTS.md, propose a Phase 1 plan, wait for my approval, and then build it step by step."
```

然后进入推荐循环：

```
Plan → Execute → Review diff → Commit → Repeat
```

把 Agent 当做**需要审查代码的初级开发者**，而不是可以无监督运行的自动机器。每个主要功能做完就 commit，出了问题能回滚。

---

## 三、AGENTS.md 的结构设计

`AGENTS.md` 是这套工作流的灵魂。它不是随便写的 prompt，而是一份**结构化的 Agent 操作手册**：

```markdown
## Project Overview & Stack
# 项目是什么、用什么技术、有什么非协商约束

## Setup & Commands
# 固定的开发/测试/构建命令（禁止 Agent 自己发明）

## Protected Areas 🛡️
# 绝对不能动的区域：.env、migrations、第三方支付配置

## Coding Conventions
# 格式化规则、架构风格、类型安全要求

## How I Should Think 🧠
# Plan → Execute → Verify 循环
# 不确定就问一个问题，不要猜

## What NOT To Do ⛔
# 不删文件、不改数据库 schema 没备份、不加 Phase 以外的功能

## Engineering Constraints 🏗️
# 禁止 any 类型、业务逻辑不进路由层、不随便加依赖

## Current State 📍
# 现在在做什么、刚完成什么、卡在哪里

## Roadmap 🗺️
# Phase 1-4 的任务清单

## Context Files 📚
# 按需加载的细节文档（渐进式上下文披露）
```

**渐进式上下文披露（Progressive Disclosure）** 是一个关键设计：`AGENTS.md` 只放高层摘要，细节放在 `agent_docs/` 子文档里，Agent 按需读取。这样避免一次性把几万字塞进 context window 导致"该记的没记住"。

---

## 四、对 Claude Code 用户的额外支持

`.claude/` 目录里有一套完整的 Claude Code 技能集成：

```bash
# 安装单个技能
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-workflow

# 或者一次安装全部
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-research
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-prd
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-techdesign
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-agents
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-build
```

安装后可以直接用斜杠命令触发：

| 命令 | 功能 |
|---|---|
| `/vibe-workflow` | 从头到尾的完整引导 |
| `/vibe-research` | 深度调研 |
| `/vibe-prd` | 生成 PRD |
| `/vibe-techdesign` | 技术设计 |
| `/vibe-agents` | 生成 AGENTS.md |
| `/vibe-build` | 开始构建 |

---

## 五、核心理念：Context Engineering

这套工作流本质上是**在 AI Agent 时代对"上下文工程"的实践答案**。

传统软件工程里，团队文档（需求文档、设计文档、编码规范）是为人类协作准备的，更新频率低。在 AI Agent 编程范式下，这些文档变成了 Agent 的"操作系统"——它们需要：

1. **结构化**，让 Agent 可以按需读取特定部分
2. **完整**，覆盖 Agent 可能需要做决策的所有维度
3. **持续更新**，随着项目演进同步修改（`MEMORY.md` 负责这一点）
4. **有边界**，明确什么不该做，防止 Agent scope creep

"先思考，后编码"不是新观点——但把它具体化成一套可复用的文件结构和工作流，让每个人都能用，是 KhazP 这个项目的贡献。

---

## 快速开始

```bash
# 克隆模板
git clone https://github.com/KhazP/vibe-coding-prompt-template.git my-project
cd my-project

# 或者直接在 GitHub 点 "Use this template"
```

完整示例在 `examples/reddit-to-ai/` 目录，展示了一个从调研到 AGENTS.md 的完整输出。

**GitHub**：`github.com/KhazP/vibe-coding-prompt-template`（2734 ⭐）
**配套网站**：vibeworkflow.app

---

<!--EN-->

## The Right Way to Vibe Code: KhazP's 5-Step Structured Workflow — From Idea to MVP Without Getting Lost

Most people's vibe-coding pattern: open Cursor, say "build me an XX app," then get trapped in an endless Agent-rewrites-everything death spiral.

[KhazP/vibe-coding-prompt-template](https://github.com/KhazP/vibe-coding-prompt-template) fixes exactly that. 2700+ stars, used to ship real projects including vibeworkflow.app, moneyvisualiser.com, and RealDex App. The core thesis is one sentence:

> **Do the thinking upfront, hand clean context to your tools, then keep the build phase moving.**

---

## Why Vibe Coding Spins Out

AI coding agents have one fundamental weakness: **context decay**. The longer the conversation, the more the agent forgets initial agreements, drifts from goals, and makes wrong tradeoffs between "ship the feature" and "maintain code quality."

The solution: **before writing a single line of code, put all decisions into files** so the agent can rebuild complete context from those files rather than from chat history.

---

## The Five-Step Workflow

Two phases:

```
Phase 1 (in any chat tool — no repo needed yet)
  Step 1: Deep Research → research-[AppName].md
  Step 2: PRD → PRD-[AppName]-MVP.md
  Step 3: Tech Design → TechDesign-[AppName]-MVP.md

Phase 2 (move into your IDE)
  Step 4: Generate AGENTS.md and config files
  Step 5: Build MVP (Plan → Execute → Verify loop)
```

### Phase 1: Thinking (in ChatGPT, Claude, or Gemini)

**Step 1: Deep Research** (`part1-deepresearch.md`, 17KB) — Paste the file into any AI chat; the AI asks questions about your idea and generates a market analysis covering demand, competitors, and feasibility. Enable web search for current data.

**Step 2: PRD** (`part2-prd-mvp.md`, 28KB) — Feed the research output plus the PRD prompt. Generates: must-have features, **out-of-scope list** (the most important output — knowing what NOT to build), success metrics, and UI requirements.

**Step 3: Tech Design** (`part3-tech-design-mvp.md`, 25KB) — Stack selection under real constraints: budget, timeline, complexity tolerance. Outputs data model, folder structure, deployment plan.

### Phase 2: Execution (in your IDE)

**Step 4: Generate Agent Files** — Put PRD and tech design into `docs/`, then tell the agent:

```
"Read part4-notes-for-agent.md, follow its instructions, and set up my workspace."
```

The agent copies from `templates/` and fills in every placeholder, generating: `AGENTS.md`, `MEMORY.md`, `REVIEW-CHECKLIST.md`, `agent_docs/`, plus tool-specific adapters (CLAUDE.md for Claude Code, `.cursor/rules/` for Cursor, native AGENTS.md for Codex).

**Step 5: Build** — First command to the agent:

```
"Read AGENTS.md, propose a Phase 1 plan, wait for my approval, and build step by step."
```

Treat the agent as a junior developer who needs code review, not an autonomous machine. Commit after each feature, review every diff.

---

## The AGENTS.md Structure

AGENTS.md is the soul of this workflow — not a raw prompt, but a structured operations manual covering: project overview, setup commands, protected areas (never touch), coding conventions, **How I Should Think** (Plan → Execute → Verify), **What NOT To Do**, engineering constraints, current state, roadmap phases, and progressive disclosure pointers to detail docs in `agent_docs/`.

**Progressive disclosure** is the key design: AGENTS.md holds high-level summaries; details live in sub-documents the agent loads on demand. This prevents stuffing the full context window upfront and losing what matters.

---

## Claude Code Integration

```bash
npx skills add https://github.com/khazp/vibe-coding-prompt-template --skill vibe-workflow
```

Six slash commands: `/vibe-workflow`, `/vibe-research`, `/vibe-prd`, `/vibe-techdesign`, `/vibe-agents`, `/vibe-build`.

---

## The Core Idea: Context Engineering

This workflow is a practical answer to what "context engineering" means in the AI agent era. Traditional software docs (requirements, design docs, coding standards) were written for human collaboration and updated rarely. In the AI agent paradigm, these documents become the agent's "operating system" — they need to be structured for on-demand lookup, complete enough to cover all decision points, continuously updated as the project evolves, and bounded with explicit "don't do this" constraints.

"Think before coding" isn't a new idea. Making it concrete as a reusable file structure and workflow that anyone can follow is KhazP's contribution here.

---

**GitHub**: `github.com/KhazP/vibe-coding-prompt-template` (2734 ⭐)  
**Web app**: vibeworkflow.app
