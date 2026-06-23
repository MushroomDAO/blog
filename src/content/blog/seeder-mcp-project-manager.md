---
title: "Seeder：自托管项目管理工具，原生支持 MCP，让 AI 直接读写你的任务"
titleEn: "Seeder: Self-Hosted Project Manager with Native MCP Support"
description: "Seeder 是一个开源自托管项目管理工具，运行在 Cloudflare Workers 上，原生内置 MCP 服务器，让 Claude、Cursor 等 AI 助手直接读写任务和客户请求，所有操作完整记录在活动流中。"
descriptionEn: "Seeder is an open-source self-hosted project manager running on Cloudflare Workers, with a native built-in MCP server that lets AI assistants like Claude and Cursor read and edit tasks directly — every action logged in an auditable activity feed."
pubDate: "2026-06-23"
updatedDate: "2026-06-23"
category: "Tech-News"
tags: ["项目管理", "MCP", "Claude Code", "Cloudflare Workers", "开源工具", "AI Agent"]
heroImage: "../../assets/images/seeder-mcp-project-manager-banner.jpg"
---

> **一句话结论（BLUF）**：Seeder 不是要替代 Jira，而是给"Jira 太重、看板又太轻"的小团队一个刚刚好的自托管起点——加上原生 MCP 支持，AI 助手从提建议变成直接执行任务。

GitHub：https://github.com/danielsyauqi/Seeder  
文档：https://seederpm.xyz/docs  
⭐ 53 Stars · 🍴 8 Forks · MIT 开源 · TypeScript · 发布于 2026-06-07

---

## 项目管理工具为什么总让人不满意？

开发团队在协作工具上长期面临一个两极困境：

- **Jira** 功能完备，但配置繁琐，小团队用起来像拿大炮打蚊子；
- **Trello / 简单看板** 上手快，但三个月后就开始捉襟见肘——没有权限体系、客户管理、日志追踪。

**Seeder** 由马来西亚开发者 Daniel Syauqi 与 Thaqif Rosdi 共同创建，目标是给 5-20 人的小团队一个"刚刚好"的选项。整套用 TypeScript 写就，部署在 Cloudflare Workers（D1 + R2）或单台 Node VM 上，MIT 开源。

---

## Seeder 能做什么？

### 项目与看板

任务支持分类、多标签、阶段、优先级、负责人、截止日期，每个项目有独立编号体系。比 Trello 细，比 Jira 轻。

### 客户请求队列

独立的需求收口，流程为 `new → reviewed → converted → closed`，一键将需求转换为任务。接外包、服务企业客户的团队会对这种模式很熟悉。

### 公开客户看板

Token 鉴权的只读视图——生成链接给客户，他们能看进度，不需要账号，也碰不到内部数据。

### 每日计划器

支持拖拽排序的每日任务队列，临时任务和项目任务混排，适合晨会前快速整理当天工作。

### 活动流（审计日志）

所有变更自动记录，包含前后对比 diff。无论是人工操作还是 AI 操作，全部可追溯。

### 白标支持

可定制系统名称、Logo、Favicon 和主题色，部署出来直接是你自己的工具品牌。

---

## 最值得关注的部分：原生 MCP 服务器

这是 Seeder 区别于同类工具最关键的设计决策。

Seeder 在 `/api/mcp` 路径自带一个 Model Context Protocol 服务器，部署即可用，无需额外配置。

MCP 全称 Model Context Protocol，是 Anthropic 推动的开放协议，让 AI 助手（Claude、Cursor、ChatGPT 等）能以统一方式调用外部工具和数据——类似给 AI 定义了一套标准接口。

### 接入方式

1. 在 **Settings → API tokens** 生成 Token（只读或读写权限）；
2. 在 Claude Desktop 或 Cursor 中配置 MCP Server：
   - Server URL：`https://<你的域名>/api/mcp`
   - 认证方式：`Bearer <你的 Token>`

配置完成后，你可以对 Claude 说："帮我查一下本周哪些任务超期了，优先级改成 High。"Claude 直接操作，不需要你手动点界面。所有 AI 操作同样出现在活动流里，完整可审计，不是黑盒。

> Token 权限不超过创建它的用户权限，安全边界清晰。

---

## 为什么这在 2026 年很重要？

项目管理工具从"你用 AI 辅助管理"到"AI 可以直接管理"，是一个不小的跨越。

大多数工具的 AI 集成路径是：导出数据 → 粘贴到 ChatGPT → 让它分析 → 再手动更新系统。这个循环效率低，而且 AI 无法感知实时状态。

MCP 原生支持打破了这个循环：AI 助手拿到读写权限，能查询当前状态、直接修改任务、创建客户请求，而每一步都有日志。这是"AI 作为执行者"而不是"AI 作为建议者"的基础设施层。

---

## 如何在 5 分钟内跑起来？

```bash
npm install
npm run setup   # 交互向导：选 dev / Cloudflare / Node VM
npm run dev     # 本地开发，Miniflare 模拟 D1+R2，无需 Cloudflare 账户
```

首次运行访问 `/sign-in`，用配置的 `OWNER_EMAIL` 创建 Owner 账户；之后注册关闭，全部走邀请制加入。

Cloudflare Workers 方案零服务器运维，免费额度对小团队基本够用。

技术栈：**Next.js + Drizzle ORM + Better Auth + Tailwind**，全 TypeScript，看代码毫无障碍。

---

## 适合谁用？

| 场景 | 原因 |
|---|---|
| 独立开发者 / 自由职业者 | 多客户项目管理 + 进度共享，无需额外工具 |
| 5-20 人研发团队 | 介于 Jira 和简单看板之间，立即可用 |
| AI 工作流重度用户 | 让 Claude/Cursor 直接接管任务执行 |
| 折腾派开发者 | MIT 开源，Fork 随便改，不受上游路线图限制 |

---

## FAQ

**Q：Seeder 和 Linear 比怎么样？**  
Linear 是托管服务，功能更完整；Seeder 是自托管，数据在自己手里，且有原生 MCP 支持。两者定位不同。

**Q：MCP 服务器是否需要额外部署？**  
不需要。Seeder 内置在 `/api/mcp`，随 app 一起部署，零额外配置。

**Q：Cloudflare Workers 免费额度够用吗？**  
D1（SQLite）免费 10 万次写 / 天，R2 免费 10GB 存储。小团队日常使用基本不会触线。

**Q：可以只用 Seeder 的 MCP 服务器不用其他功能吗？**  
不行，MCP 服务器是 Seeder 的内置组件，没有独立版本。但部署完整 Seeder 本身也很轻量。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: Seeder fills the gap between "too heavy" (Jira) and "too light" (basic Kanban) for small teams — and with a native MCP server built in, AI assistants move from suggesting to actually executing tasks.

GitHub: https://github.com/danielsyauqi/Seeder  
Docs: https://seederpm.xyz/docs  
⭐ 53 Stars · 🍴 8 Forks · MIT · TypeScript · Released 2026-06-07

---

## Why Are Project Management Tools Always Disappointing?

Small teams have been stuck between two extremes for years:

- **Jira** — powerful, but the setup overhead makes it feel like overkill for a 10-person team.
- **Trello / simple boards** — quick to start, but you outgrow them fast: no permissions, no client management, no audit trail.

**Seeder**, built by Daniel Syauqi and Thaqif Rosdi, is an open-source self-hosted project manager that targets teams of 5–20. It's written in TypeScript, runs on Cloudflare Workers (D1 + R2) or a single Node VM, and is MIT-licensed.

---

## What Does Seeder Do?

**Projects & Kanban** — tasks with categories, multi-tag labels, phases, priorities, assignees, due dates, and per-project code numbers.

**Client request queue** — a separate inbound queue (new → reviewed → converted → closed) that converts directly into tasks.

**Public client board** — a token-gated read-only view for sharing progress with clients, no account needed.

**Daily planner** — a drag-to-reorder daily task queue mixing adhoc and project tasks.

**Activity feed** — every change logged with before→after diffs, from both human and AI operations.

**White-labeling** — customize system name, logo, favicon, and accent color.

---

## The Key Feature: Native MCP Server

Seeder ships a built-in Model Context Protocol server at `/api/mcp`. Deploy the app, and the MCP endpoint is ready — no separate setup.

### How to connect

1. Generate a token at **Settings → API tokens** (read-only or read+write).
2. Point your AI client at `https://<your-domain>/api/mcp` with `Bearer <token>` auth.

After that, you can tell Claude: "Find all overdue tasks this week and set their priority to High." Claude executes directly. Every AI action appears in the activity feed — fully auditable, not a black box.

Token permissions are scoped to the user who created them, so the security boundary is clear.

---

## Why Does This Matter in 2026?

The typical AI + project management workflow today: export data → paste into ChatGPT → get suggestions → manually update the system. Slow, and the AI has no awareness of real-time state.

Native MCP support breaks that loop. The AI gets live read/write access, can query current state, update tasks, and handle client requests — with a complete log of every action. This is the infrastructure layer for "AI as executor" rather than "AI as advisor."

---

## Quick Start

```bash
npm install
npm run setup   # interactive wizard: dev / Cloudflare / Node VM
npm run dev     # local dev with Miniflare — no Cloudflare account needed
```

On first run, go to `/sign-in` and create the owner account with your configured `OWNER_EMAIL`. After that, signup is closed and new members join by invite only.

The Cloudflare Workers deploy is serverless — free tier covers most small-team workloads easily.

---

## FAQ

**Q: How does Seeder compare to Linear?**  
Linear is a hosted SaaS with more polish; Seeder is self-hosted (your data stays yours) with native MCP support. Different trade-offs.

**Q: Does the MCP server need a separate deploy?**  
No. It's built into the app at `/api/mcp`, ready to use immediately after deployment.

**Q: Will the Cloudflare free tier hold up?**  
D1 (SQLite): 100k writes/day free. R2: 10GB free. Small teams won't get close to the limits.

**Q: Can I run just the MCP server without the rest of Seeder?**  
No — the MCP server is a built-in component, not a standalone service. But the full Seeder deployment is lightweight enough that this shouldn't be a concern.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
