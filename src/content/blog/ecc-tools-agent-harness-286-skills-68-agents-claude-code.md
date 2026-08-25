---
title: "ECC：24万+ Star 的 Agent 工具箱，Claude Code / Codex 的工程操作系统"
titleEn: "ecc-tools-agent-harness-286-skills-68-agents-claude-code"
description: "ECC（Engineer Claude Code）是目前 GitHub 全球 Star 增速最快的 AI 编程工具仓库，累计 24.3 万 Star。它不是一个模型或 IDE，而是一套安装在 Claude Code / Codex / Cursor / OpenCode 之上的工程纪律层：286 个技能、68 个专项 Agent、94 个命令、AgentShield 安全扫描，MIT 开源。"
descriptionEn: "ECC (Engineer Claude Code) is the fastest-growing AI coding repo on GitHub with 243k+ stars. Not a model or IDE — an engineering discipline layer on top of Claude Code, Codex, Cursor, and OpenCode: 286 skills, 68 agents, 94 commands, AgentShield security scanning. MIT open source."
pubDate: "2026-08-25"
updatedDate: "2026-08-25"
category: "Tech-News"
tags: ["开源", "Claude Code", "Agent工具", "技能包", "AgentShield", "ECC", "AI编程", "工程流程"]
heroImage: "../../assets/images/ecc-tools-agent-harness-286-skills-68-agents-claude-code-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：affaan-m/ECC ⭐ 243,000+ | MIT License | JavaScript  
Website：https://ecc.tools  
Discord：https://discord.gg/36yGMHGFbR  
创建：2026-01-18 | 最近更新：2026-08-25

---

## 24 万 Star 说明了什么

ECC 在 GitHub 全球实时趋势榜常驻，7 个月从零长到 24 万+ Star，这个速度在非病毒式内容领域极少见。

它不是因为新奇的模型或者炫酷的界面被传播的。它被传播，是因为每天用 Claude Code 或 Codex 写代码的人发现：**自己的 Agent 开始能按工程流程工作了**，而不只是随机输出代码。

---

## ECC 是什么

一句话：**安装在你的 AI 编程助手之上的工程操作系统**。

你的 Agent 本来能写代码。ECC 给它加上配套的工程系统和工具箱：

```text
plan → test → implement → review → verify → remember → improve
```

不是每次 prompt 里重新描述这个流程，而是安装一次，变成 Agent 的默认工作方式。

> Optimize the context window. Persist everything else.

---

## 三层架构

ECC 不是单一仓库，是一个三层系统：

**第一层：开源工具包（分发层）**
- MIT 永久开源，这里是 ECC 的"前门"
- 286 个技能（TDD、安全、文档、前端、数据、ML、运维……）
- 68 个专项 Agent（规划、Review、构建修复、安全、架构、领域专家）
- 94 个命令快捷入口
- 跨平台适配：Claude Code、Codex、Cursor、OpenCode、Gemini、Zed、GitHub Copilot、Kimi Code……

**第二层：AgentShield（安全保护层）**
- 102 条安全规则，扫描每次 Agent 会话
- 检测范围：恶意 prompt、危险 hook、MCP 配置问题、权限泄露、secrets 暴露、Agent 文件篡改
- 开源扫描器，本地审计，可信透明
- GitHub App 自动化：PR 扫描 + 风险上下文 Review

**第三层：ECC 2.0 控制平面（运营层）**
- 本地优先的跨 Harness 控制平面
- 可观测性、编排、会话管理
- 跨 Claude Code / Codex / Cursor 的统一操作界面

---

## 核心能力一览

| 类别 | 数量 | 说明 |
|------|------|------|
| Agents | 68 | 规划、Review、构建修复、安全、架构、领域专家 |
| Skills | 286 | TDD、研究、安全、文档、前端、数据、ML、运维等 |
| Commands | 94 | 现有命令入口（ECC 正在向 skills-first 迁移） |
| Hooks & Memory | 运行时 | 强制执行、会话摘要、持续学习、本能、上下文控制 |
| Rules | 选装 | 按语言或项目选择的编码标准，每次加载 |
| AgentShield | 内置 | prompt、hook、MCP、权限、secrets、Agent 文件全扫描 |

---

## 安装

### Claude Code（推荐路径）

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

安装后 ECC 的 skills、agents、命令和 plugin-managed hooks 全部就位。选了这条路就停在这里，不要再手动安装。

### npm（跨平台）

```bash
npm i -g ecc-universal
```

支持 Codex、Cursor、OpenCode 等非 Claude Code 平台。

### GitHub App

访问 https://github.com/apps/ecc-tools 安装，适合团队和 CI/CD 场景（私有仓库从 $19/seat/月起）。

---

## 为什么不只是一堆 CLAUDE.md

很多人试过自己写 CLAUDE.md 定义工程流程，效果参差不齐，原因不是 prompt 写得不好，而是：

1. **每次新对话都要重建流程理解**，没有持久化的"本能"
2. **自定义 hook 很难写对**，AgentShield 发现绝大多数自定义 hook 有安全漏洞
3. **缺乏专项 Agent**：规划 Agent 和实现 Agent 不一样，Review Agent 更不能用同一个上下文

ECC 解决的是这三个问题：通过 hooks + memory + instincts 把工程流程持久化，内置 AgentShield 扫描，拆分专项 Agent 角色。

---

## 商业模式

OSS 层永久 MIT 免费。ECC Pro（GitHub App）面向私有仓库团队，$19/seat/月，含自动 PR 扫描、策略包和企业级报告。赞助商包括 CodeRabbit、Greptile、Atlas Cloud、Moonshot AI（Kimi）等。

---

**相关链接**

- GitHub：https://github.com/affaan-m/ECC
- 官网：https://ecc.tools
- 技能目录：https://ecc.tools/skills
- 安全层：https://ecc.tools/security
- Discord：https://discord.gg/36yGMHGFbR
- GitHub App：https://github.com/apps/ecc-tools

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## ECC: The 243k-Star Agent Harness OS for Claude Code, Codex, and Cursor

*by Mycelium Protocol*

---

GitHub: affaan-m/ECC ⭐ 243,000+ | MIT License | JavaScript  
Website: https://ecc.tools  
Discord: https://discord.gg/36yGMHGFbR  
Created: 2026-01-18 | Updated: 2026-08-25

---

### What 243k Stars Tells You

ECC has held a place on GitHub's global trending list for months, growing from zero to 243k+ stars in seven months. That velocity is rare outside of viral meme repos.

It spread because people using Claude Code or Codex every day found something unexpected: **their agent started working like a trained engineer**, not just randomly emitting code.

---

### What ECC Is

One sentence: **an engineering operating system installed on top of your AI coding assistant**.

Your agent can already write code. ECC gives it the coordination, process, and toolbox to do it like an engineer:

```text
plan → test → implement → review → verify → remember → improve
```

Instead of re-describing this process in every prompt, you install it once and it becomes the default.

> Optimize the context window. Persist everything else.

---

### Three Layers

ECC is not one repo. It's a three-layer system:

**Layer 1: Open-source toolkit (distribution)**
- MIT-licensed forever — this is ECC's front door
- 286 skills: TDD, research, security, docs, frontend, data, ML, operations, and more
- 68 specialized agents: planning, review, build repair, security, architecture, domain work
- 94 command shims as convenient entry points
- Cross-harness adapters: Claude Code, Codex, Cursor, OpenCode, Gemini, Zed, Copilot, Kimi Code

**Layer 2: AgentShield (protection)**
- 102 security rules scanning every agent session
- Scans: malicious prompts, dangerous hooks, MCP config issues, permission leakage, secret exposure, agent file tampering
- Open-source scanner for auditable trust; no automatic telemetry
- GitHub App automation: PR scanning and risky-context review

**Layer 3: ECC 2.0 (control plane)**
- Local-first cross-harness control plane
- Observability, orchestration, and session management above the underlying tools
- Unified operations surface across Claude Code, Codex, and Cursor

---

### Core Inventory

| Category | Count | What it gives you |
|----------|-------|--------------------|
| Agents | 68 | Planning, review, build repair, security, architecture, domain work |
| Skills | 286 | TDD, research, security, docs, frontend, data, ML, operations, more |
| Commands | 94 | Entry points while ECC moves to skills-first surface |
| Hooks & Memory | Runtime | Enforcement, session summaries, continuous learning, instincts, context controls |
| Rules | Selective | Always-loaded language or project standards you choose |
| AgentShield | Included | Prompt, hook, MCP, permission, secret, and agent-file scanning |

---

### Install

**Claude Code (recommended):**

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

This installs ECC's skills, agents, commands, and plugin-managed hooks. Pick this path and stop — don't also run a manual install.

**npm (cross-platform):**

```bash
npm i -g ecc-universal
```

Works with Codex, Cursor, OpenCode, and other harnesses.

**GitHub App:**

Install at https://github.com/apps/ecc-tools for team and CI/CD use. Private repos from $19/seat/month.

---

### Why Not Just Write a Better CLAUDE.md

Many people have tried. Results are inconsistent for three reasons:

1. **Processes don't persist across sessions** — without hooks, instincts, and memory, every new conversation re-learns the process from scratch
2. **Custom hooks are hard to write securely** — AgentShield finds security issues in the vast majority of hand-written hooks
3. **Planning and implementation agents are different roles** — a single shared context can't do both well

ECC addresses all three: persistent process via hooks + memory + instincts, built-in security scanning, and specialized agent roles that don't share context.

---

### Business Model

The OSS layer is MIT-licensed forever. ECC Pro (GitHub App) serves private-repo teams at $19/seat/month, with automated PR scanning, policy packs, and enterprise reporting. Sponsors include CodeRabbit, Greptile, Atlas Cloud, Moonshot AI (Kimi), and Itô Markets.

---

**Links**

- GitHub: https://github.com/affaan-m/ECC
- Website: https://ecc.tools
- Skills directory: https://ecc.tools/skills
- Security layer: https://ecc.tools/security
- Discord: https://discord.gg/36yGMHGFbR
- GitHub App: https://github.com/apps/ecc-tools

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
