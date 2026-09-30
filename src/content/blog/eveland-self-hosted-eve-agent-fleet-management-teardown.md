---
title: "Eveland：4核16GB托管20个Agent两个月，这是他们的使用记录"
titleEn: "Eveland: Running 20 Agents on 4-Core 16GB for Two Months — A Production Usage Record"
description: "evelandhq/eveland，8星，AGPL-3.0，TypeScript。Eve（Vercel开源Agent框架）的自托管生产平台，五个服务构成：API / Agent Gateway / Dashboard / Worker / Workflow Dispatcher。项目团队在4核16GB机器上托管约20个Agent、内部跑了两个多月，不是压测。核心卖点：多Agent集中管理不用挨个找终端，Playground试用，定时任务，Langfuse可观测性。pre-1.0，生产仅支持Linux（systemd + bubblewrap沙箱），AGPL-3.0商用需开源改动。"
descriptionEn: "evelandhq/eveland, 8 stars, AGPL-3.0, TypeScript. A self-hosted production platform for Eve (Vercel's open-source Agent framework). Five services: API, Agent Gateway, Dashboard, Worker, Workflow Dispatcher. The team behind it ran ~20 agents on a 4-core 16GB machine for two months — real usage, not a benchmark. Core value: centralized multi-agent management without hunting separate terminals, a Playground, cron schedules, and Langfuse observability. Pre-1.0; production requires Linux (systemd + bubblewrap sandbox); AGPL-3.0 requires open-sourcing commercial modifications."
pubDate: 2026-09-30
heroImage: "../../assets/images/eveland-self-hosted-eve-agent-fleet-management-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent运维", "自托管", "Eve", "多Agent管理", "开源拆解", "TypeScript"]
lang: "zh-CN"
wechatTitle: "Eveland：自托管20个Agent的使用记录"
wechatDigest: "8星AGPL-3.0；自托管20个Agent；Gateway+调度+Langfuse；仅Linux生产"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 先说结论，再说细节

项目团队的原话：

> 在一台 4核16GB 的机器上，托管约20个 Agent，内部用了2个多月。这是我们的使用记录，不是20路同时满载的压测。

这句话很值钱。当大多数开源 Agent 平台在 README 里贴基准测试截图时，这里给的是「两个月内部实跑，一台普通 Linux 服务器，约20个 Agent」。

这不是高配场景，也不是演示——是实际工程选型的参考值。

仓库：github.com/evelandhq/eveland  
**Stars：8 | License：AGPL-3.0 | 语言：TypeScript | 文档：eveland.ai/docs**

---

## Eve 是什么，Eveland 是什么

Eve 是 Vercel 的开源 Agent 框架——项目地址在 eve.dev。Eveland 是为 Eve 项目提供的**自托管生产平台**，独立社区维护，非 Vercel 官方。

关系类比：Eve 是 Next.js，Eveland 是 Vercel 平台，但这里是自托管版本——你把 Eveland 装到自己的 Linux 服务器上，然后把 Eve Agent 项目推进去，Eveland 负责部署、路由、调度和观测。

---

## 五个服务，构成完整平台

Eveland 是 pnpm monorepo，核心是五个服务 + 一个文档站，以单一 SemVer 版本号一起发布：

| 服务 | 职责 |
|------|------|
| `apps/api` | Hono 平台 API，Better Auth 会话，团队成员管理，内置 OTLP 数据入口 |
| `apps/gateway` | Agent Gateway——公开的 Agent 数据平面，保留认证/cookie，会话绑定到 Deployment |
| `apps/web` | Dashboard——Next.js App Router 控制台（shadcn + Tailwind v4） |
| `apps/worker` | Docker/systemd 运行时适配器 + Postgres 任务消费（导入/构建/部署/调度） |
| `apps/workflow-dispatcher` | 持久化 Workflow 定时器和唤醒调度，每个安装实例恰好运行一个 |
| `apps/docs` | 双语公开文档站（eveland.ai），Next.js + Fumadocs |

**让项目团队「松一口气」的四件事**（他们原话）：

- 多个 Agent 集中管理，不用挨个找终端
- Playground 直接试用，会话执行过程可追踪
- 定时任务集中查看，执行记录有迹可查
- 用量、日志、实例健康，统一界面可见

---

## 装一条命令，但只能装在 Linux 上

生产安装只需：

```bash
curl -fsSL https://eveland.ai/install.sh | sudo bash
```

安装脚本调用 `eveland-ctl`，自动生成配置、应用数据库迁移、注册五个 systemd 单元。

**关键约束：生产环境只支持 Linux（systemd 运行时）。macOS 只能跑开发模式。**

生产用 systemd + **bubblewrap 沙箱**（每个 Agent 进程被隔离在 bwrap 容器中）。Docker 在 Eveland 里是**开发模式专用**，文档明确说「Docker runtime is for development, not production」——这个立场比较罕见，通常项目会把 Docker 同时推给生产。

---

## 可观测性接 Langfuse

Eveland 内置 OTLP 接入，用 `packages/agent-observer` 在 Release 时自动把 OpenTelemetry 钩子注入 Eve Agent。Managed Collector 会把根 Agent 会话和它的子会话分组到 Langfuse 里统一查看。

这意味着：部署 Eveland 之后，你的 Agent 调用链、token 用量、会话健康状态，都能在 Langfuse 界面里看，不需要自己搭追踪基础设施。

---

## 几个需要知道的点

**AGPL-3.0 的商用含义**

AGPL-3.0 是最严格的开源许可证之一。如果你在商业产品中集成 Eveland、或者在 SaaS 中托管它，必须把你对 Eveland 的所有修改也以 AGPL 开源。内部使用（不对外提供服务）不触发这条要求。

决策前确认：你的使用场景是内部工具还是面向用户的服务。

**pre-1.0，小版本有破坏性变更**

README 明确标注：`0.x` 版本号的小版本（`0.x.0` → `0.y.0`）可能引入不向后兼容的变更，每次都会在 CHANGELOG 里说明。这是正常的 pre-1.0 承诺——不要把它用在不能停机的生产关键路径上，或者做好版本锁定和升级计划。

**Eve 本身的成熟度**

Eveland 的存在价值依赖于 Eve 的普及度。Eve 是 Vercel 推出的 Agent 框架，目前不如 LangChain/LangGraph 体量大。如果你的团队已经在用 Eve，Eveland 是非常自然的配套；如果你还没有选定 Agent 框架，Eveland 不是决策出发点。

**8星很早期**

目前社区很小。遇到问题，GitHub Discussions 是主要支持渠道，没有付费支持选项。

---

## 本地开发起步

```bash
corepack enable
pnpm install --frozen-lockfile
cp .env.example .env           # 设置 BETTER_AUTH_SECRET 和 EVELAND_ADMIN_PASSWORD
pnpm --filter @evelandhq/api db:migrate

# 只跑 Postgres 和 OTLP Collector 在 Docker 里：
docker compose -f docker-compose.yml -f docker-compose.native.yml up -d postgres otel-collector

pnpm dev                       # 启动六个开发进程
```

Dashboard 在 `http://localhost:17300`，文档站在 `http://localhost:17350`。初始 Admin 邮箱默认 `admin@example.com`，密码来自 `EVELAND_ADMIN_PASSWORD`（至少12位）。

开发模式会启动六个进程：API、Agent Gateway、Dashboard、Worker、Workflow Dispatcher、Docs。除 Docs 外其余五个是必须的——缺任何一个，某个功能就会断。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 8 |
| Forks | 4 |
| License | AGPL-3.0 |
| 语言 | TypeScript (pnpm monorepo) |
| 创建时间 | 2026-07-06 |
| 服务数量 | 5（+ 文档站） |
| 生产运行时 | Linux + systemd + bubblewrap |
| 可观测性 | Langfuse (OTLP) |
| Node 版本要求 | ≥ 24 |
| 实际运行记录 | 4核16GB / 约20个Agent / 2个月 |

---

## 综合判断

8 星的数字会让人低估这个项目的工程完成度。翻仓库：完整的 monorepo 结构、双语文档、systemd 单元、bubblewrap 沙箱、OTLP 可观测、Release Please 自动发版——这些不是快速搭出来的。

如果你在用 Eve 框架，且 Agent 数量到了「一台机器上20个、挨个找终端已经很烦」的阶段，Eveland 是对号入座的工具。

如果你还没有选 Eve，先看清楚 Eve 的成熟度；AGPL-3.0 的商用约束也要提前确认——生产前读一遍许可证是必要成本，不是形式。

---

> 开源仅供学习，商业使用请仔细核查许可证条款（AGPL-3.0 要求开源修改）。

---

<!--EN-->

## Eveland: Running 20 Agents on 4-Core 16GB for Two Months — A Production Usage Record

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Start With the Conclusion

The team's own words:

> On a 4-core 16GB machine, we hosted about 20 agents and ran them internally for over two months. This is our usage record — not a stress test with 20 agents running at full capacity simultaneously.

That sentence is worth a lot. When most open-source Agent platforms lead with benchmark screenshots, this gives you a real number: two months of internal production on a commodity Linux server, roughly 20 agents.

Not a high-spec scenario. Not a demo. An actual engineering reference point.

Repo: github.com/evelandhq/eveland  
**8 stars | AGPL-3.0 | TypeScript | Docs: eveland.ai/docs**

---

### Eve vs. Eveland

Eve is Vercel's open-source Agent framework (eve.dev). Eveland is the self-hosted production platform for it — independently community-maintained, not affiliated with Vercel.

Analogy: Eve is to Next.js as Eveland is to Vercel, except here you host it yourself. Install Eveland on your Linux server, push an Eve Agent project, and Eveland handles deployment, routing, scheduling, and observability.

---

### Five Services, One Platform

Eveland is a pnpm monorepo. Five services plus a docs site ship as a single SemVer-versioned product:

| Service | Role |
|---------|------|
| `apps/api` | Hono platform API, Better Auth sessions, team membership, built-in OTLP ingest |
| `apps/gateway` | Agent Gateway — public Agent data plane; preserves auth/cookies, pins sessions to deployments |
| `apps/web` | Dashboard — Next.js App Router console (shadcn, Tailwind v4) |
| `apps/worker` | Docker/systemd runtime adapters + Postgres job consumer (import/build/deploy/schedule) |
| `apps/workflow-dispatcher` | Durable workflow timers and wake; exactly one instance per installation |

The four things the team said finally gave them peace of mind:

- All agents managed centrally — no hunting through separate terminals
- Playground for direct testing, with session execution traces
- Scheduled tasks in one view with execution history
- Usage, logs, and instance health visible in a single interface

---

### One Install Command — Linux Only

Production install:

```bash
curl -fsSL https://eveland.ai/install.sh | sudo bash
```

The installer calls `eveland-ctl`, which generates config, applies migrations, and registers five systemd units.

**Critical constraint: production is Linux-only (systemd runtime). macOS is development only.**

Production uses systemd + **bubblewrap sandboxing** — each Agent process runs isolated in a bwrap container. Docker is explicitly development-only. The docs say: "Docker runtime is for development, not production" — an unusual stance, since most projects push Docker for both.

---

### Observability via Langfuse

Eveland includes built-in OTLP ingestion. `packages/agent-observer` injects OpenTelemetry hooks into Eve Agents at release time. The Managed Collector groups root Agent conversations and their descendant sessions together in Langfuse.

Practical result: after deploying Eveland, your Agent call chains, token usage, and session health are visible in Langfuse without building your own tracing infrastructure.

---

### Four Things to Know Before Using

**AGPL-3.0 and commercial use**

AGPL-3.0 is among the most restrictive open-source licenses. Integrating Eveland into a commercial product, or hosting it as a service, requires open-sourcing all your modifications under AGPL. Internal use (not serving external users) does not trigger this requirement.

Confirm your use case — internal tooling vs. user-facing service — before committing.

**Pre-1.0 means minor versions break**

The README is clear: `0.x` minor releases may include breaking changes, documented in the CHANGELOG each time. Standard pre-1.0 practice — don't put it on a zero-downtime critical path, or version-lock and plan upgrades carefully.

**Eve's maturity**

Eveland's value depends on Eve's adoption. Eve is Vercel's Agent framework, currently smaller in community than LangChain/LangGraph. If your team is already using Eve, Eveland is a natural fit. If you haven't chosen a framework yet, Eveland isn't the starting point for that decision.

**8 stars = very small community**

GitHub Discussions is the primary support channel. No paid support option. Expect to dig into the codebase when things go wrong.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 8 |
| License | AGPL-3.0 |
| Services | 5 (+ docs site) |
| Production runtime | Linux + systemd + bubblewrap |
| Observability | Langfuse (OTLP) |
| Node requirement | ≥ 24 |
| Actual production record | 4-core 16GB / ~20 agents / 2 months |

---

### Verdict

8 stars undersells the engineering completeness here. The repo shows: full monorepo structure, bilingual documentation, systemd units, bubblewrap sandboxing, OTLP observability, automated releases via Release Please — none of this is built quickly.

If you're using the Eve framework and you've hit the "20 agents on one machine, hunting through separate terminals is exhausting" stage, Eveland is purpose-built for that problem.

If Eve isn't already your framework choice, understand Eve's maturity first. And read the AGPL-3.0 terms before committing to production use — it's a necessary five minutes, not a formality.

---

> Open source for learning only. Verify AGPL-3.0 terms before commercial use — modifications must be open-sourced.
