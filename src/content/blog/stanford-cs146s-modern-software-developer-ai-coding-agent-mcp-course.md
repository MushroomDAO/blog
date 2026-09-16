---
title: 'Stanford CS146S：《现代软件开发者》，MCP/Claude Code/Warp 十周实战，讲义全开放'
titleEn: "Stanford CS146S: The Modern Software Developer — 10 Weeks of MCP, Claude Code, and Warp, All Materials Open"
description: "斯坦福 2025 秋季本科课程，Mihail Eric 主讲，3 学分，10 周覆盖 LLM 提示工程、Coding Agent 构建、MCP 服务器开发、Claude Code、Warp 终端、AI 安全（SAST/DAST/提示注入）、AI 代码审查、全栈 AI 部署、SRE 可观测性。43 份讲义 PDF 和文章全部开放，每周配作业，Boris Cherny、Zach Lloyd、Martin Casado 等工业界嘉宾亲授。"
descriptionEn: "Stanford Fall 2025 undergrad course taught by Mihail Eric. 3 units, 10 weeks covering LLM prompting, coding agent construction, MCP server development, Claude Code, Warp terminal, AI security (SAST/DAST/prompt injection), AI code review, full-stack AI deployment, SRE observability. All 43 lecture PDFs and articles open; weekly assignments; guest lectures from Boris Cherny, Zach Lloyd, Martin Casado and others."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Research"
tags: ["Stanford", "course", "open-source", "Claude-Code", "MCP", "AI-agents", "software-engineering", "coding-agent", "Warp"]
heroImage: "../../assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-banner.jpg"
---

> 📌 课程官网：https://themodernsoftware.dev
> GitHub（中文课程包）：https://github.com/182han/cs146s-zh-course-pack
> 授课：Mihail Eric ｜ Stanford Fall 2025 ｜ 3 学分 ｜ 教室：420-041

---

斯坦福 2025 年秋季开了一门本科课程：CS146S「The Modern Software Developer」。主讲是 Mihail Eric，TA Febie Lin 和 Brent Ju。

课程问题是：**下一代软件工程师应该怎么用 AI 工具把自己的生产力提升 10 倍？**

它的立场很直接——AI 工具不是辅助，是核心工作流。软件开发已经从"从零写代码"变成"计划 → 用 AI 生成 → 修改 → 重复"的迭代工作流。

---

## 十周课程结构

**第 1 周：LLM 与提示工程基础**
LLM 实际上是什么、如何有效提示。作业：LLM 提示操练场。嘉宾：无。

**第 2 周：Coding Agent 解剖**
工具调用与函数调用、MCP（Model Context Protocol）。覆盖 MCP 官方文档、Server SDK、Authentication。作业：第一步进入 AI IDE。

**第 3 周：AI IDE**
上下文管理和代码理解、PRD 驱动 Agent、IDE 集成。阅读包括 Devin：Coding Agents 101、如何在复杂代码库中让 AI 工作。

**第 4 周：Claude Code**
深度拆解 Claude Code。作业：用 Claude Code 写代码。**嘉宾：Boris Cherny（Claude Code 工程师）**。

**第 5 周：Warp 与 AI 终端**
AI 原生终端开发、Warp 内部架构。作业：用 Warp 做 Agent 开发。**嘉宾：Zach Lloyd（Warp CEO）**。

**第 6 周：AI 安全与漏洞检测**
SAST vs DAST、提示注入攻击、OWASP Top 10、Context Rot（上下文降级）。作业：写安全 AI 代码。**嘉宾：Isaac Evans（Semgrep）**。

**第 7 周：AI 驱动代码审查**
AI 代码审查最佳实践、自动化审查工具。作业：代码审查练习（Code Review Reps）。**嘉宾：Tomas Reimers（Graphite）**。

**第 8 周：全栈 AI 开发与部署**
多栈 Web 应用、AI 辅助部署流水线。作业：多栈 Web App 构建。**嘉宾：Gaspar Garcia（Vercel）**。

**第 9 周：SRE、可观测性与 Agentic On-Call**
Site Reliability Engineering、AI Agent 在值班工程中的应用、多智能体系统。**嘉宾：Mayank Agarwal & Milind Ganjoo（Resolve）**。

**第 10 周：AI 的未来**
最终项目展示。**嘉宾：Martin Casado（a16z）**。

---

## 工具清单

课程覆盖的 AI 开发工具：

| 类别 | 工具 |
|------|------|
| Coding Agent | Claude Code |
| AI 终端 | Warp |
| AI IDE | Cursor / Windsurf |
| 协议层 | MCP（Model Context Protocol） |
| 安全 | Semgrep（SAST） |
| 代码审查 | Graphite |
| 部署 | Vercel |
| LLM API | 各家 API |

---

## 开放资源

**课程官网**：https://themodernsoftware.dev
课程主页提供每周阅读列表、作业、讲义 Slides 链接和嘉宾信息。

**43 份讲义与文章（全部开放）**
包含 15 份 PDF 讲义 + 31 篇指定阅读文章，覆盖 10 周全部主题。社区已将这 43 份内容批量翻译成中文（GitHub：182han/cs146s-zh-course-pack，包含可复跑的翻译流水线）。

**YouTube**
每周讲座的视频链接在课程主页提供，部分讲座（如 Boris Cherny、Zach Lloyd 嘉宾课）有录像。

---

## 适合谁

- 有基础编程经验（CS111 等效），想系统学 AI 辅助开发的工程师
- 想理解 MCP 协议和 Coding Agent 架构的开发者
- 想了解 Claude Code 和 Warp 这类工具内部逻辑的人

课程强调"理解 AI 工具原理 + 实际上手"，不是单纯工具使用教程，而是有理论基础支撑的工程实践课。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Course website: https://themodernsoftware.dev
> GitHub (Chinese course pack): https://github.com/182han/cs146s-zh-course-pack
> Instructor: Mihail Eric | Stanford Fall 2025 | 3 units | Room 420-041

---

Stanford's Fall 2025 undergraduate course CS146S "The Modern Software Developer" was taught by Mihail Eric, with TAs Febie Lin and Brent Ju.

The course's central question: **how should the next generation of software engineers leverage AI tools to 10x their productivity?**

The stance is direct — AI tools aren't optional supplements; they're the core workflow. Software development has shifted from "write code from scratch" to "plan → generate with AI → modify → repeat."

---

## Ten-Week Course Structure

**Week 1: LLMs and Prompt Engineering**
What an LLM actually is, how to prompt effectively. Assignment: LLM Prompting Playground.

**Week 2: Anatomy of Coding Agents**
Tool use, function calling, MCP (Model Context Protocol). Assignment: First Steps in the AI IDE.

**Week 3: The AI IDE**
Context management and code understanding, PRD-driven agents, IDE integrations.

**Week 4: Claude Code**
Deep dive into Claude Code. Assignment: coding with Claude Code. **Guest: Boris Cherny (Claude Code engineer).**

**Week 5: Warp and AI Terminal**
AI-native terminal development, Warp's internal architecture. Assignment: agentic development with Warp. **Guest: Zach Lloyd (Warp CEO).**

**Week 6: AI Security and Vulnerability Detection**
SAST vs DAST, prompt injection attacks, OWASP Top 10, Context Rot. Assignment: Writing Secure AI Code. **Guest: Isaac Evans (Semgrep).**

**Week 7: AI-Powered Code Review**
AI code review best practices, automated review tooling. Assignment: Code Review Reps. **Guest: Tomas Reimers (Graphite).**

**Week 8: Full-Stack AI Development and Deployment**
Multi-stack web app development, AI-assisted deployment pipelines. Assignment: Multi-stack Web App Builds. **Guest: Gaspar Garcia (Vercel).**

**Week 9: SRE, Observability, and Agentic On-Call**
SRE fundamentals, observability, AI agents in on-call engineering, multi-agent systems. **Guests: Mayank Agarwal & Milind Ganjoo (Resolve).**

**Week 10: The Future of AI in Software Engineering**
Final project presentations. **Guest: Martin Casado (a16z).**

---

## Tool Stack

| Category | Tools |
|----------|-------|
| Coding Agent | Claude Code |
| AI Terminal | Warp |
| AI IDE | Cursor / Windsurf |
| Protocol Layer | MCP (Model Context Protocol) |
| Security | Semgrep (SAST) |
| Code Review | Graphite |
| Deployment | Vercel |

---

## Open Materials

**Course website:** https://themodernsoftware.dev

**43 lecture PDFs and articles (all open):** 15 PDF lecture slides + 31 assigned reading articles, covering all 10 weeks. A community project has translated all 43 items into Chinese with a reproducible translation pipeline (GitHub: 182han/cs146s-zh-course-pack).

**YouTube:** lecture video links are provided on the course page; guest lectures from Boris Cherny and Zach Lloyd have recordings.

---

## Who It's For

- Engineers with basic programming experience (CS111-equivalent) who want to systematically learn AI-assisted development
- Developers who want to understand MCP protocol and coding agent architecture
- Anyone who wants to understand the internal logic of tools like Claude Code and Warp

The course combines theory with hands-on practice — not just a tool tutorial, but engineering practice grounded in how the tools actually work.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
