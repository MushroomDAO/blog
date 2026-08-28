---
title: "Platypus：自托管多租户 Agent 构建平台，看板只是它给 Agent 用的一个工具"
titleEn: "Platypus: A Self-Hosted, Multi-Tenant Platform for Building Your Own AI Agents"
description: "调研开源项目 Platypus：一个从零构建自定义 AI Agent 的自托管全栈平台——MIT 协议，Next.js + Hono + Docker，69 star。跟本站写过的 Multica（在看板上编排已有 Agent CLI）不是同一类东西：Platypus 的看板只是 Agent 可以调用的一个工具，核心是 Agent/Skill/子 Agent 构建、MCP 接入、可插拔沙箱、自动记忆提取、组织级 Blueprints 模板、多租户隔离，以及不锁定任何模型供应商。本文拆解它跟看板编排类工具的真实差异，以及 Blueprints 这个本站还没写过的设计。"
descriptionEn: "A deep dive into Platypus, an open-source, self-hosted full-stack platform for building custom AI agents from scratch — MIT licensed, Next.js + Hono + Docker, 69 stars. It is not the same category as Multica (covered on this blog previously), which orchestrates existing agent CLIs on a kanban board — Platypus's kanban is just one tool an agent can call. The real substance is agent/skill/sub-agent construction, first-class MCP support, pluggable sandbox backends, automatic memory extraction, org-scoped Blueprints, multi-tenant isolation, and zero model-provider lock-in. This post traces the real difference from kanban-orchestration tools, plus Blueprints — a design pattern this blog hasn't covered yet."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Tech-News"
tags: ["AI Agent", "开源工具", "自托管", "MCP", "多租户", "TypeScript", "Docker", "Agent平台"]
heroImage: "../../assets/images/platypus-self-hosted-multi-tenant-ai-agent-platform-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/willdady/platypus
文档：https://docs.platypus.chat
授权：MIT

---

## 一句话结论

**Platypus 是一个自托管的全栈平台，用来从零构建你自己的 AI Agent 团队**——不是把已有的 Agent CLI（Claude Code、Codex 这类）搬到看板上管理，而是给你原生的 Agent/Skill/子 Agent 构建工具、MCP 接入、可插拔沙箱、自动记忆提取、多租户隔离和组织级配置模板。MIT 协议，TypeScript + Next.js 16 + Hono，Docker Compose 一键起，69 star，20 fork，v3.0.0 刚发不久，最近一次提交是两天前。

先说清楚它跟本站之前写过的 Multica 不是一回事——两者都有"看板"这个词，但看板在两边的角色完全不同。

## 跟 Multica 的真实区别：看板管理什么

Multica（本站此前写过，4.1万 star）的核心机制是：**已有的 Agent CLI 是看板上的卡片和执行者**——你在看板上建 Issue、分配给某个 Agent（Claude Code / Codex / 其他 14 种支持的 CLI 之一），Agent 自主接手执行、报告阻塞、更新状态。它是一层**编排层**，管理的对象是外部已经存在的 Agent 工具。

Platypus 反过来：**看板和 Dashboard 是 Agent 可以调用的工具之一**，不是管理 Agent 的容器。你在 Platypus 里从零定义一个 Agent——选模型、写指令、挂工具、给它 Skill、允许它委派给子 Agent——这个 Agent 自己是被构建出来的产物，看板只是它众多工具里的一个（用来读写任务卡片），跟 MCP 连接器、Sandbox 执行、Schedule 定时任务是平级的能力。

一个类比：Multica 是"任务管理软件，把外部承包商挂上去"；Platypus 是"招聘平台 + 培训体系，从零训练自己的员工，顺便给员工配了个看板工具"。选哪个取决于你是想**编排已经用惯的 Agent CLI**，还是想**按自己的业务逻辑从零定制 Agent**。

## Key Features 拆解

- **Agents / Skills / Sub-agents**：定义一次 Agent（模型 + 指令 + 工具），配上可复用的 Skill（按需加载，标准的渐进式披露），Agent 还能委派任务给子 Agent。
- **MCP 一等公民**：原生 Model Context Protocol 支持，接本地和远程数据源。
- **Sandbox**：每个 workspace 隔离的 Shell + 文件系统执行环境，后端可插拔，官方参考实现是 Docker 和 SSH 两种。
- **Memory**：后台从对话里自动提取事实和偏好，注入到未来的对话里——不需要手动维护记忆文件。
- **Boards & Dashboards**：拖拽式看板和 widget 化 Dashboard，Agent 可以通过内置工具读写它们（这正是上面说的"看板是工具"）。
- **Schedules & Webhooks**：cron 定时任务或一次性任务，HMAC 签名的 HTTP 回调，按事件过滤，自动重试。
- **Multi-Tenancy**：Organization 和 Workspace 两层隔离，一个团队的数据不会被另一个团队看到。
- **Blueprints**——这是本站目前还没写过的设计，也是我认为 Platypus 里最值得记一笔的部分：定义一组"组织级共享资源"（比如标准工具集、默认 Skill、Sandbox 配置），一次应用到某个 Workspace 就把这些资源整体接入。文档描述是"additive, idempotent, and a snapshot"——增量式（不会覆盖 Workspace 已有的自定义配置）、幂等（重复应用不会出错或重复叠加）、快照式（应用的是那一刻的版本，Blueprint 后续更新不会自动同步过去，除非重新应用）。对于要给多个团队/多个客户批量铺开"标准 Agent 配置"的场景，这个设计比手动一个个 Workspace 配置要靠谱得多。
- **Provider Agnostic**：走 Vercel AI SDK，OpenAI / Anthropic / Google / Bedrock / OpenRouter，加上 Ollama、vLLM 和任何 OpenAI 兼容端点——本地模型和云端模型可以在同一个平台里混用。

## 架构

Turborepo 管理的 monorepo：

- `apps/frontend`：Next.js + ShadCN + Tailwind，用 AI SDK 做流式响应的响应式界面。
- `apps/backend`：Hono.js 跑在 Node.js 上的高性能 REST API，管 Agent 逻辑、工具执行、数据库交互。
- `packages/schemas`：前后端共享的 Zod schema，端到端类型安全。

## 快速开始

```bash
git clone https://github.com/willdady/platypus.git
cd platypus
cp .env.example .env   # 设置 BETTER_AUTH_SECRET 和管理员账号
docker compose up -d   # 打开 http://localhost:3000
```

官方文档特别标注：**首次登录后一定要改掉默认密码**——这条不是客套话，是安全提示，Sandbox 默认开着 Shell 执行能力，默认密码留着等于给外部访问者留了一扇后门。

## 谁该看这个

**适合**：想从零定制 Agent 团队（而不是编排已有 Agent CLI）的场景；需要给多个团队/多个客户做租户隔离部署的场景；想用 Blueprint 这种"标准配置模板一次铺开"的方式管理多个 Workspace，而不是每个都手动配一遍；不想被绑定单一模型供应商、本地云端模型想混着用的场景。

**不适合 / 需要注意**：69 star、v3.0.0 刚发布不久的项目，稳定性和长期维护需要观察；30 个 open issue，说明还在快速迭代期，生产环境部署前建议先跑一遍自己的验收测试；如果你要的只是"把 Claude Code / Codex 这类已有 CLI 挂到看板上管理"，Multica 是更直接的选择，Platypus 的构建型定位对这个需求反而是过度设计。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Project: https://github.com/willdady/platypus
Docs: https://docs.platypus.chat
License: MIT

---

## TL;DR

**Platypus is a self-hosted, full-stack platform for building your own AI agents from scratch** — not a management layer that puts existing agent CLIs (Claude Code, Codex, and the like) onto a kanban board, but native tooling for constructing agents, skills, and sub-agents, with first-class MCP support, pluggable sandboxes, automatic memory extraction, multi-tenant isolation, and org-scoped configuration templates. MIT licensed, TypeScript + Next.js 16 + Hono, one Docker Compose command to stand up, 69 stars, 20 forks, v3.0.0 just shipped, last commit two days ago.

Worth clarifying up front: this is not the same category as Multica, which this blog covered previously. Both use the word "kanban," but the board plays a completely different role in each.

## The real difference from Multica: what the board manages

Multica (covered here previously, 41k stars) works by making **existing agent CLIs the cards and executors on a board** — you create an issue on the board, assign it to an agent (Claude Code, Codex, or one of 14 supported CLIs), and the agent autonomously takes it over, reports blockers, and updates its own status. It is an **orchestration layer** managing tools that already exist outside it.

Platypus works the other way: **the board and dashboards are tools an agent can call**, not a container that manages agents. In Platypus you define an agent from scratch — pick a model, write instructions, attach tools, give it skills, let it delegate to sub-agents — and that agent is the thing being constructed; the board is just one of its many tools (for reading and writing task cards), on the same footing as MCP connectors, sandboxed execution, and scheduled jobs.

An analogy: Multica is "project-management software with external contractors plugged in"; Platypus is "a hiring platform plus a training system that builds its own employees from scratch, and happens to give them a kanban tool." Which one fits depends on whether you want to **orchestrate agent CLIs you already use**, or **custom-build agents around your own business logic**.

## Key features

- **Agents / Skills / Sub-agents**: define an agent once (model, instructions, tools), attach reusable skills it loads on demand (standard progressive disclosure), and let it delegate to sub-agents.
- **MCP as a first-class citizen**: native Model Context Protocol support for local and remote data sources.
- **Sandbox**: per-workspace isolated shell and filesystem execution, pluggable backends — the reference implementations are Docker and SSH.
- **Memory**: facts and preferences are extracted from conversations in the background and injected into future chats — no manual memory-file maintenance.
- **Boards & Dashboards**: drag-and-drop kanban and widget dashboards that agents read and update through built-in tools — this is exactly the "board as a tool" point above.
- **Schedules & Webhooks**: cron or one-off jobs, HMAC-signed HTTP callbacks with per-event filtering and automatic retries.
- **Multi-Tenancy**: two-layer isolation via Organizations and Workspaces, so one team's data never leaks into another's.
- **Blueprints** — this is the part I think is most worth flagging, since this blog hasn't covered this design pattern before: define a set of org-scoped shared resources (standard toolsets, default skills, sandbox configuration) and apply it to a Workspace in one step to attach them all at once. The docs describe it as "additive, idempotent, and a snapshot" — additive (doesn't overwrite a workspace's existing custom config), idempotent (reapplying doesn't error or duplicate), and a snapshot (applies the version at that moment; later Blueprint updates don't auto-propagate unless reapplied). For rolling out a "standard agent configuration" across many teams or clients, this beats manually configuring each workspace by hand.
- **Provider agnostic**: built on the Vercel AI SDK — OpenAI, Anthropic, Google, Bedrock, OpenRouter, plus Ollama, vLLM, and any OpenAI-compatible endpoint. Local and cloud models can coexist on the same platform.

## Architecture

A Turborepo-managed monorepo:

- `apps/frontend`: a responsive Next.js + ShadCN + Tailwind interface, streaming responses via the AI SDK.
- `apps/backend`: a high-performance Hono.js REST API on Node.js handling agent logic, tool execution, and database interactions.
- `packages/schemas`: shared Zod schemas for end-to-end type safety across frontend and backend.

## Quick start

```bash
git clone https://github.com/willdady/platypus.git
cd platypus
cp .env.example .env   # set BETTER_AUTH_SECRET and admin credentials
docker compose up -d   # then open http://localhost:3000
```

The docs specifically call out: **change the default password immediately after first login.** That's not boilerplate — the sandbox ships with shell execution enabled by default, and a default password left in place is an open door for anyone who finds the instance.

## Who should look at this

**Good fit**: teams that want to custom-build an agent workforce from scratch rather than orchestrate agent CLIs they already use; multi-tenant deployments serving several teams or clients that need real isolation; anyone who wants Blueprints-style "roll out a standard config once" management across many workspaces instead of hand-configuring each one; anyone who doesn't want to lock into a single model provider and wants to mix local and cloud models.

**Not a fit / worth noting**: a 69-star, freshly-v3.0.0 project — stability and long-term maintenance are still unproven; 30 open issues signal active, fast-moving iteration, so run your own acceptance tests before a production deployment; if all you need is "put my existing Claude Code / Codex CLIs on a kanban board," Multica is the more direct choice — Platypus's build-from-scratch orientation is over-engineering for that narrower need.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
