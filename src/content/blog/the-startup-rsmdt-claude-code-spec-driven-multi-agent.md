---
title: "The Agentic Startup：给 Claude Code 装一套创业团队工作流"
titleEn: "The Agentic Startup: A Startup Team Workflow for Claude Code"
description: "rsmdt 开源的 Claude Code 多智能体框架，367 stars，MIT License，Shell。核心思路：先写规格再写代码（spec-driven development）。10 个 slash command 覆盖从需求到交付的全流程，三级复杂度自动分发（Direct/Incremental/Factory），v3 新增实验性 Agent Teams 多智能体协作。两个 Marketplace 插件，一行安装。"
descriptionEn: "rsmdt's open-source multi-agent framework for Claude Code, 367 stars, MIT License, Shell. Core idea: spec before code. 10 slash commands cover requirements through delivery; three-tier complexity dispatch (Direct / Incremental / Factory); v3 adds experimental Agent Teams. Two Marketplace plugins, one-line install."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["ClaudeCode", "多智能体", "规格驱动", "开发工具", "AI编程", "AgentTeams", "Mycelium"]
heroImage: "../../assets/images/the-startup-rsmdt-claude-code-spec-driven-multi-agent-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Claude Code 很强，但没有结构的时候很容易跑偏：直接开始写代码，需求没讲清楚，多轮对话之后上下文丢失，实现和最初想法越来越远。

The Agentic Startup 的回答是：**先写规格，再写代码**（spec-driven development）。它把 Claude Code 改造成一个「创业团队」——需求分析师、架构师、工程师、QA、文档工程师各司其职，按阶段流转，有质量门控。

GitHub: https://github.com/rsmdt/the-startup | ⭐ 367 | MIT License | Shell

---

## 10 个命令，3 个阶段

```
SETUP（可选）
  /constitution ──► 建立项目治理规则（在 BUILD 全程自动执行）

BUILD（主流程）
  /specify     ──► 生成规格（需求文档 + 解决方案设计）
  /validate    ──► 校验质量（3C 框架）
  /implement   ──► 按复杂度分级执行
  /test        ──► 运行测试，强制所有权
  /review      ──► 多智能体代码评审
  /document    ──► 生成/同步文档

MAINTAIN（按需）
  /analyze     ──► 发现代码模式和规律
  /refactor    ──► 安全重构（保留行为）
  /debug       ──► 根因分析式调试
```

---

## 三级复杂度自动分发

`/specify` 执行完会自动分类复杂度，`/implement` 按分类选择执行策略：

| 级别 | 场景 | 执行方式 |
|------|------|----------|
| **Direct** | 修复/重构/单一验收标准功能 | 直接读 requirements + solution，无分解产物 |
| **Incremental** | 单一功能，1-2 个组件 | 生成 `plan/` 目录，按 phase-N.md 分阶段循环 |
| **Factory** | 多功能/并行工作 | 生成 `manifest.md` + `units/*.md`，并行执行原子单元 |

规格存储结构：

```
.start/specs/001-feature-name/
├── requirements.md     # 构建什么，为什么
├── solution.md         # 技术上怎么构建
├── plan/               # (Incremental) README.md + phase-N.md
└── manifest.md + units/ + scenarios/  # (Factory)
```

---

## 关键机制

**跨会话恢复**：规格写到磁盘。上下文用完了重开对话，`/specify 001` 或 `/implement 001` 接着上次的继续——Claude 读规格文件恢复状态。

**漂移检测**：`/implement` 执行过程中自动对比实现和规格，发现不一致时提示：更新规格还是改代码。

**代码所有权强制**：`/test` 发现失败测试，不接受「这是预存的」借口——碰了代码库就要修。

**自适应代码评审**：`/review` 根据改动内容自动追加专项评审视角——有 async 代码→并发评审，有依赖变更→供应链检查，有 UI 变更→可访问性审计。5 个基础视角 + 条件专项。

---

## 安装

```bash
# 一行安装（推荐）
curl -fsSL https://raw.githubusercontent.com/rsmdt/the-startup/main/install.sh | sh

# 或通过 Marketplace 手动安装
/plugin marketplace add rsmdt/the-startup
/plugin install start@the-startup      # 核心工作流（必装）
/plugin install team@the-startup       # 专项智能体（可选）
```

---

## 两个插件

**start@the-startup**（核心）：10 个用户命令 + 5 个自主技能 + 2 种输出风格

**team@the-startup**（可选）：8 个角色，20 个活动专项智能体

| 角色 | 负责领域 |
|------|----------|
| Chief | 复杂度评估、活动路由、并行执行 |
| Analyst | 需求分析、优先级、项目协调 |
| Architect | 系统设计、技术研究、质量评审、文档 |
| Software Engineer | API、组件、领域建模、性能 |
| QA Engineer | 测试策略、探索性测试、负载测试 |
| Designer | 用研、交互设计、设计系统、无障碍 |
| Platform Engineer | IaC、容器、CI/CD、监控、数据管道 |
| Meta Agent | 智能体设计与生成 |

---

## v3 新增：Agent Teams（实验性）

专项智能体之间可以自主协作，共同处理复杂任务：

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

安装脚本会自动询问是否配置。

---

## 两种输出风格

**The Startup**：高能量执行风格，YC 路演氛围，「现在就交付」
**The ScaleUp**：冷静专业风格，教育深度，「可持续的速度」

任何时候切换：`/output-style start:The Startup` 或 `/output-style start:The ScaleUp`

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## The Agentic Startup: A Full Startup-Team Workflow for Claude Code

*by Mycelium Protocol*

---

Claude Code is powerful, but without structure it drifts easily: you jump straight to code before requirements are clear, context gets lost across turns, and what you build keeps diverging from what you intended.

The Agentic Startup's answer: **spec before code**. It turns Claude Code into a startup team — analyst, architect, engineer, QA, and doc writer each playing their role, flowing through stages with quality gates at every step.

GitHub: https://github.com/rsmdt/the-startup | ⭐ 367 | MIT License | Shell

---

### 10 Commands, 3 Phases

```
SETUP (optional)
  /constitution ──► Project governance rules (auto-enforced throughout BUILD)

BUILD (primary flow)
  /specify     ──► Generate spec (requirements + solution design)
  /validate    ──► Quality check (3C framework)
  /implement   ──► Auto-dispatched by complexity tier
  /test        ──► Run tests, enforce code ownership
  /review      ──► Multi-agent code review
  /document    ──► Generate / sync documentation

MAINTAIN (as needed)
  /analyze     ──► Discover patterns and rules
  /refactor    ──► Safe refactor (preserve behavior)
  /debug       ──► Root-cause analysis debugging
```

---

### Three-Tier Complexity Dispatch

`/specify` classifies complexity automatically; `/implement` routes to the matching strategy:

| Tier | When | Execution |
|------|------|-----------|
| **Direct** | Fixes, refactors, single-AC features | Reads requirements + solution directly, no decomposition artifacts |
| **Incremental** | Single feature, 1–2 components | Generates `plan/` with phase-N.md files, executed loop per phase |
| **Factory** | Multi-feature, parallel work | Generates `manifest.md` + `units/*.md`, parallel atomic unit execution |

Specs persist on disk in `.start/specs/001-feature-name/` — this is what makes resumption work.

---

### Key Mechanisms

**Resume across sessions**: Specs live on disk. When context runs out, start a new session and `/implement 001` picks up exactly where you left off.

**Drift detection**: During `/implement`, the framework auto-compares implementation against spec. When they diverge, you choose: update the spec or update the code.

**Code ownership mandate**: `/test` finds a failing test — "pre-existing failure" is not an acceptable response. You touched the codebase, you own it.

**Adaptive code review**: `/review` reads what changed and adds specialist perspectives automatically. Async code triggers concurrency review. Dependency changes trigger supply-chain checks. UI changes trigger accessibility audits.

---

### Install

```bash
# One-line install (recommended)
curl -fsSL https://raw.githubusercontent.com/rsmdt/the-startup/main/install.sh | sh

# Or via Marketplace
/plugin marketplace add rsmdt/the-startup
/plugin install start@the-startup      # core workflow (required)
/plugin install team@the-startup       # specialist agents (optional)
```

---

### Two Plugins

**start@the-startup** (core): 10 user skills + 5 autonomous skills + 2 output styles

**team@the-startup** (optional): 8 roles, 20 activity-based agents covering Chief, Analyst, Architect, Software Engineer, QA Engineer, Designer, Platform Engineer, and Meta Agent.

---

### v3: Agent Teams (Experimental)

Specialist agents can now coordinate autonomously on complex tasks. Enable via:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

The installer configures this automatically if you opt in.

---

### Two Output Styles

**The Startup**: High-energy, Y Combinator intensity, "let's ship this NOW"
**The ScaleUp**: Calm confidence, engineering excellence, "sustainable speed at scale"

Switch anytime: `/output-style start:The Startup` or `/output-style start:The ScaleUp`

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
