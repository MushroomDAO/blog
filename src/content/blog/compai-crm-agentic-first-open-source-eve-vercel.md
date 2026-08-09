---
title: "Comp AI CRM：CRM 不是产品，是 AI Agent 的笔记本"
titleEn: "compai-crm-agentic-first-open-source-eve-vercel"
description: "Trycompai/crm，7.9k stars，MIT，TypeScript。一个设计哲学完全颠倒的 CRM：不是给人用、在里面配 AI 的，而是给 Agent 用、人去里面看 Agent 记了什么的。基于 Vercel 的 eve 框架（持久化 Agent 运行时），18个工具、4个 skill、1个调度器，自己决定下一步看谁、记什么、什么时候回来复查。核心原则：Agent 永远不猜——工具只报告观察到的，不接受置信度评分。"
descriptionEn: "Trycompai/crm, 7.9k stars, MIT, TypeScript. A CRM with its design inverted: not built for humans with AI bolted on, but built for an agent, with humans going in to see what it recorded. Built on Vercel's eve framework (durable agent runtime): 18 tools, 4 skills, 1 scheduler. The agent decides what to look at next, books its own rechecks, and runs on its own schedule — close the browser and it keeps going. Core rule: the agent never guesses. Tools report what they observed; no tool accepts a confidence score."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["CRM", "AI Agent", "开源", "TypeScript", "Vercel", "eve", "销售", "Mycelium"]
heroImage: "../../assets/images/compai-crm-agentic-first-open-source-eve-vercel-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

大多数 CRM 的本质是一个带表单的数据库。「AI CRM」通常是在这个表单旁边加一个聊天框。

Comp AI CRM 把这个方向翻了过来：**Agent 不是 CRM 的功能；CRM 是 Agent 记笔记的地方。**

你不需要打开它来触发 Agent。关掉浏览器，Agent 还在跑——按照自己的调度，从自己的任务队列里取工作，决定下一步看谁，记下看到的，预约什么时候再回来看。你打开 CRM，是去看它已经做了什么，而不是去指挥它做什么。

GitHub: https://github.com/Trycompai/crm | ⭐ 7,904 | MIT | TypeScript

---

## 设计反转

传统 CRM 的工作流是：**人输入 → 数据库保存 → AI 分析**。

Comp AI CRM 的工作流是：**Agent 研究 → Agent 记录 → 人审核**。

README 里的这句话是关键：

> "A confidently wrong fact about a customer is worse than a blank field, because nobody can tell it is wrong."（关于客户的一个自信但错误的事实，比一个空字段更糟糕——因为没人能看出来它是错的。）

所以有一条 Agent 从不打破的规则：**什么都不猜**。工具只报告它「观察到」的东西——`crm.signature-block`（邮件签名块）、`github.account-identity`（GitHub 账户身份）。没有任何工具接受置信度评分，因为一个被要求给自己的确信度打分的模型会打，而且会往让自己显得有用的方向偏。强证据直接写入记录。弱证据变成「建议」等人来判断。

---

## Agent 怎么运行

`apps/agent` 是独立部署的，基于 **eve**——Vercel 的文件系统优先的持久化 Agent 框架：工具是一个文件，skill 是一个 markdown 文件，调度是一个文件，运行时处理持久化部分（session 在重新部署后存活，任务从中断处恢复）。

**18 个工具**，包括：

```
read_crm_history     — 读取已有的线程、会议记录、签名块
search_crm           — 搜索现有联系人和公司
identify_contact     — 识别一个人是谁
research_person      — 对一个人做外部研究
enrich_company       — 补充公司信息
record_fact          — 把观察到的事实写入记录
schedule_recheck     — 预约下一次复查（并说明原因）
```

**4 个 skill**（Agent 读的散文，像代码一样版本控制）：

- `evidence.md` — 如何评估证据
- `identity-matching.md` — 如何判断两个记录是否是同一个人
- `data-boundaries.md` — 什么可以记，什么不能记
- `writing-a-brief.md` — 如何写摘要

**1 个调度器**：`dispatch.ts` 什么都不决定——它只是租出到期的行，每行启动一个 session。「每 N 分钟看最老的十个联系人」这样的逻辑属于任务的 `dueAt` 字段，而不是 cron 表达式。

**任务队列**：`lib/tasks.ts` 使用 `claimDue`，带 `FOR UPDATE SKIP LOCKED`，保证两个 dispatcher 取到不同的行，一个 session 崩掉后锁超时自动释放。

---

## 沙箱安全设计

Agent 有一个沙箱：`bash`、`grep`、`glob` 加一个 `/workspace`。但沙箱有两个约束：

**`deny-all` 出站网络**：这不是说 Agent 没有网——`web_fetch` 在应用运行时里跑，`web_search` 在模型提供商那边跑。`deny-all` 移除的是唯一一条能让客户邮件内容通过 shell 命令泄露出去的路径。

**沙箱里没有 `DATABASE_URL`**：一个有凭证和出站的 shell，就算在内部工具里，也是「数据泄露形状」的。一个两者都没有的 shell，只是一个文本处理器。

---

## 零 API key 也能跑

每一个外部数据源都是可选的。一个 key 都没有的情况下，Agent 仍然可以工作：`read_crm_history` 读取你自己的线程、会议和签名块，这是免费的，也是最好的证据——没有任何数据供应商能卖给你一封来自客户自己邮箱的回复。每加一个 key，就多一个可以查的地方。Agent 在每个 session 开始时会被告知这个安装有哪些 key，所以它会根据实际拥有的资源来规划，而不是在执行中一个一个发现缺口：

```
[agent] on   LinkedIn (RAPIDAPI_KEY)
[agent] off  Web research (PERPLEXITY_API_KEY)
[agent] off  Company brand data (Settings → General)
```

---

## 技术栈

```
框架：Turborepo monorepo，运行时 Bun，部署 Vercel
Agent：eve（Vercel 的持久化 Agent 框架）
模型：Vercel AI Gateway（无供应商 SDK，OIDC 认证，无需管理 API key）
沙箱：Vercel Sandbox（生产）/ Docker 或 microsandbox（本地）
前端：Next.js App Router + shadcn/ui + nuqs（URL 状态）
API：NestJS + nestjs-trpc（HTTP/Auth/tRPC/邮箱同步）
数据：Prisma + Postgres（Neon）+ 可选 Redis（Upstash）
Auth：Better Auth（Google/Microsoft/自定义 IdP）
文件：Vercel Blob（镜像头像，防止源消失）
工具链：Biome + TypeScript 全栈
```

---

## 快速启动

```bash
git clone https://github.com/trycompai/crm.git
cd crm
bun install

# 复制环境变量
cp .env.example .env
# 最少需要：DATABASE_URL（Postgres）+ AGENT_BRIDGE_SECRET

# 数据库迁移
bun run db:migrate

# 开发
bun run dev
```

Agent 进程和前端是分开部署的。本地开发时两个进程各自跑；Vercel 部署时，Agent 在 `apps/agent` 目录下独立部署。

---

## 这个东西有意思在哪里

CRM 市场有几十年的历史，每一代 CRM 都在同一个基座上迭代：数据库 + 表单 + 越来越多的集成。AI 来了之后，大多数产品选择在这个基座上加一层——「AI 帮你填字段」「AI 帮你写邮件」。

Comp AI CRM 问了一个不同的问题：**如果 Agent 才是主要操作者，这个系统应该长什么样？**

答案不是把 Agent 嵌入现有的 CRM 流程，而是从 Agent 的需求倒推：持久化任务队列、可审计的工具调用、文件级的 skill 定义、永不猜测的证据模型——然后让「人去看 Agent 记了什么」这件事变得好用。

这个思路本身比代码更值得关注。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Comp AI CRM: The Database Is for the Agent, Not the Human

*by Mycelium Protocol*

---

Most CRMs are a database with a form in front of it. The AI ones bolt a chat box onto the side of that form.

Comp AI CRM flips the design: **the agent is not a feature of the CRM; the CRM is where the agent keeps its notes.**

You don't open it to trigger the agent. Close the browser and the agent keeps running — on its own schedule, pulling from its own work queue, deciding what to look at next, writing down what it finds, booking its own follow-ups. You open the CRM to see what it already did, not to tell it what to do.

GitHub: https://github.com/Trycompai/crm | ⭐ 7,904 | MIT | TypeScript

---

### The Inversion

Traditional CRM workflow: **human inputs → database saves → AI analyzes**.

Comp AI CRM workflow: **agent researches → agent records → human reviews**.

The README puts it plainly:

> "A confidently wrong fact about a customer is worse than a blank field, because nobody can tell it is wrong."

So there's one rule the agent never breaks: **nothing is guessed**. Tools only report what they *observed* — `crm.signature-block`, `github.account-identity`. No tool accepts a confidence score, because a model asked to grade its own certainty will, and it will be wrong in the direction that makes it look useful. Strong evidence writes to the record. Weak evidence becomes a suggestion a human resolves.

---

### How the Agent Runs

`apps/agent` is its own deployment, built on **eve** — Vercel's filesystem-first framework for durable agents: a tool is a file, a skill is a markdown file, a schedule is a file, and the runtime handles the durable part (sessions survive redeploys, work resumes where it stopped).

**18 authored tools**, including:

```
read_crm_history     — reads your own threads, meetings, signature blocks
search_crm           — searches existing contacts and companies
identify_contact     — resolves who a person is
research_person      — external research on a person
enrich_company       — fills in company data
record_fact          — writes an observed fact to the record
schedule_recheck     — books a future look and states the reason
```

**4 skills** (prose the agent reads, versioned like code):

- `evidence.md` — how to weigh evidence
- `identity-matching.md` — how to decide two records are the same person
- `data-boundaries.md` — what can be recorded, what can't
- `writing-a-brief.md` — how to write a summary

**1 schedule**: `dispatch.ts` decides nothing — it leases due rows and starts a session per row. "Every N minutes, the oldest ten contacts" belongs in a task's `dueAt`, not a cron expression.

**Work queue**: `lib/tasks.ts` uses `claimDue` with `FOR UPDATE SKIP LOCKED` — two dispatchers take disjoint work; a session that dies frees its row when the lease expires.

---

### Sandbox Security

The agent has a sandbox: `bash`, `grep`, `glob`, and a `/workspace`. Two constraints:

**`deny-all` egress**: `web_fetch` runs in the app runtime; `web_search` runs at the model provider. `deny-all` removes the only path by which a customer's email body could leave through a shell command.

**No `DATABASE_URL` in the sandbox**: A shell with credentials and egress is exfiltration-shaped, even in an internal tool. A shell with neither is a text processor.

---

### Works with Zero API Keys

Every external source is optional. With no keys at all, `read_crm_history` reads your own threads, meetings, and signature blocks — free, and the best evidence there is. No data vendor can sell you a reply from the person's own address. Each key opens one more place to look. The agent is told at session start which sources this install has, and plans accordingly:

```
[agent] on   LinkedIn (RAPIDAPI_KEY)
[agent] off  Web research (PERPLEXITY_API_KEY)
[agent] off  Company brand data (Settings → General)
```

---

### Stack

```
Monorepo: Turborepo, runtime Bun, deployed Vercel
Agent: eve (Vercel's durable agent framework)
Model: Vercel AI Gateway (no provider SDK; OIDC on Vercel = no key to manage)
Sandbox: Vercel Sandbox (prod) / Docker or microsandbox (local)
Frontend: Next.js App Router + shadcn/ui + nuqs (URL state)
API: NestJS + nestjs-trpc (HTTP, auth, tRPC, mailbox sync)
Data: Prisma + Postgres (Neon) + optional Redis (Upstash)
Auth: Better Auth (Google, Microsoft, or custom IdP)
Files: Vercel Blob (mirrors profile pictures so they survive the source)
Tooling: Biome + TypeScript everywhere
```

---

### Quick Start

```bash
git clone https://github.com/trycompai/crm.git
cd crm
bun install
cp .env.example .env
# minimum: DATABASE_URL (Postgres) + AGENT_BRIDGE_SECRET
bun run db:migrate
bun run dev
```

The agent process and the frontend are separate deployments. On Vercel, `apps/agent` deploys independently.

---

### Why This Is Interesting

CRM has decades of history and every generation iterated on the same base: database plus form plus more integrations. When AI arrived, most products added a layer on top — "AI fills in the fields," "AI writes the email."

Comp AI CRM asks a different question: **if the agent is the primary operator, what should the system look like?**

The answer isn't embedding an agent into existing CRM workflows. It's working backwards from what an agent needs — a durable work queue, auditable tool calls, file-level skill definitions, a never-guess evidence model — and then making "a human goes in to see what the agent recorded" actually usable.

The thinking is worth more attention than the code.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
