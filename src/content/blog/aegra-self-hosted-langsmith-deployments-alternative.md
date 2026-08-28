---
title: "Aegra：LangSmith Deployments 的自托管平替，SDK 不用换，代码不用改"
titleEn: "Aegra: A Self-Hosted Drop-In for LangSmith Deployments — Same SDK, Zero Code Changes"
description: "调研 Aegra：LangChain LangSmith Deployments（原 LangGraph Platform）的开源自托管平替。同一套 LangGraph SDK、同一套 API，换成自己的基础设施和 Postgres。核心是 Redis 任务队列的 Worker 架构（单实例 30 并发、租约式崩溃恢复、水平扩展）、Postgres 持久化 checkpoint、Agent Protocol v2 流式传输、pgvector 语义存储。LangSmith 免费版不能自托管、企业版才有自定义鉴权和定时任务，Aegra 全部免费内置。创建一年多，周更发布节奏，1129 star，Apache-2.0。"
descriptionEn: "A deep dive into Aegra, an open-source self-hosted replacement for LangChain's LangSmith Deployments (formerly LangGraph Platform): same LangGraph SDK, same API, running on your own infrastructure and Postgres instead of LangChain's cloud. The core is a Redis-queue worker architecture (30 concurrent runs per instance, lease-based crash recovery, horizontal scaling), Postgres-backed checkpoint persistence, Agent Protocol v2 streaming, and pgvector semantic storage. LangSmith's free tier can't self-host at all, and custom auth plus scheduled cron only exist on the enterprise tier — Aegra ships all of it free. Over a year old, weekly release cadence, 1,129 stars, Apache-2.0."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Tech-News"
tags: ["AI Agent", "开源工具", "LangGraph", "自托管", "本地部署", "FastAPI", "Postgres", "开发工具"]
heroImage: "../../assets/images/aegra-self-hosted-langsmith-deployments-alternative-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/aegra/aegra
文档：https://docs.aegra.dev
授权：Apache-2.0

---

## 一句话结论

**Aegra 是 LangSmith Deployments（原 LangGraph Platform）的开源自托管平替**——同一套 `langgraph_sdk`、同一套 Agent Protocol API，你现有的 LangGraph 代码不用改一行，只是把运行的地方从 LangChain 的云换成自己的 FastAPI + PostgreSQL。项目创建于 2025 年 7 月，到现在一年多，1129 star、236 fork，8 月还在按周发版本（v0.10.2 → v0.10.3 → v0.10.4，一周三个版本），是个已经跑出生产成色的项目，不是刚立起来的玩具仓库。

它解决的问题很具体：如果你用 LangGraph 写 agent，LangSmith 的免费版只能本地跑，想部署就得上付费的 Plus（还是托管在 LangChain 的云上），自定义鉴权和定时任务这类基础功能，官方定价页写的是只有企业版（要单独谈价、要 license key）才有。Aegra 把这些能力搬到自己的基础设施上，全部免费。

## 换的是运行的地方，不是写代码的方式

这一点是 Aegra 存在的全部理由：你的 LangGraph agent 代码原封不动，只是把 `get_client(url=...)` 指向自己的 Aegra 服务器：

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2026")
assistant = await client.assistants.create(graph_id="agent")
thread = await client.threads.create()

async for chunk in client.runs.stream(
    thread_id=thread["thread_id"],
    assistant_id=assistant["assistant_id"],
    input={"messages": [{"type": "human", "content": "Hello!"}]},
):
    print(chunk)
```

也因为协议兼容（Agent Protocol），Agent Chat UI、LangGraph Studio、AG-UI / CopilotKit 这些围绕 LangGraph 生态长出来的前端和调试工具，指向 Aegra 也能直接用，不用为了自托管额外换一套周边工具链。

## 架构：Redis 队列 + Postgres 持久化

FastAPI 做 HTTP 层，LangGraph 本身管状态机执行，PostgreSQL 存 checkpoint 和持久化状态，Redis 干三件事：任务队列、SSE 跨实例 pub/sub、崩溃恢复。

**Worker 架构**是这篇最值得记一笔的部分：单实例默认 30 并发 run，用租约（lease）机制做崩溃恢复——一个 worker 挂了，它认领的任务不会丢，租约过期后被其他实例接管重跑，支持水平扩展到多实例。这不是文档里随口一句话，8 月的提交历史里能看到真实的工程打磨：一次是修"优雅关闭时进行中的任务被错误终结"的竞态（SIGTERM 走的清理路径跟用户主动取消混在一起，任务被标记成中断态却又释放了租约，reaper 完全看不到它，只有 SIGKILL 硬重启才能靠租约超时抢救回来）；另一次是修"assistant 创建"在并发下的竞态（先查后插的经典 TOCTOU，两个并发请求都没查到已存在就都去插入，撞索引唯一约束时抛出未处理的 500，而不是按预期返回该有的状态码）。这类修复读起来就是真实生产流量磨出来的坑，不是自己造场景验证的演示代码。

**持久化**走 PostgreSQL 原生 checkpoint（LangGraph 官方支持的后端），语义存储额外挂了 pgvector，做向量检索的 key-value 存储。**流式传输**支持新旧两种协议：旧的按 run 级别流式，新的 Agent Protocol v2 按 thread 级别流式，带内容块事件、子图生命周期事件，原生支持 human-in-the-loop 的恢复——这是目前最新版 LangGraph SDK 和 `useStream()` 定向支持的传输协议，默认开启。

**鉴权**是可插拔的 Python handler：JWT、OAuth、Firebase，或者干脆不启用。**可观测性**走 OpenTelemetry 标准，往任意 OTLP 后端扇出（Langfuse、Phoenix 等），不锁定 LangSmith 自家的 tracing。

## 定价对比：企业版功能，免费自己扛

README 里那张对比表把这件事说得很直白（基于 2026 年 2 月 LangChain 官方定价页）：

| | LangSmith Deployments | Aegra |
|---|---|---|
| 部署 agent | 免费版仅本地开发，付费版才能云端部署 | 免费、无限制 |
| 自定义鉴权 | 免费版不提供，Plus 版才有 | 内置 Python handler（JWT/OAuth/Firebase） |
| 定时任务 | 免费版不提供 | 内置免费 |
| 自托管 | 仅企业版（需 license key） | 一直如此（Apache-2.0） |
| 自己的数据库 | 免费/Plus 版托管，企业版才能自带 | 自带 Postgres |
| Tracing | 仅 LangSmith | 任意 OTLP 后端 |
| 数据落地 | 免费/Plus 版在 LangChain 云，企业版才能落自己基础设施 | 一直落自己基础设施 |

换句话说：LangSmith 商业模式的分层逻辑是"自托管、自定义鉴权、定时任务"这些放到企业合同里谈；Aegra 把它们直接开源免费给了出来，代价是运维责任转移到你自己身上——Postgres、Redis 要自己扛。

## 上手路径

推荐走 CLI（需要 Python 3.12+，Docker 跑 PostgreSQL）：

```bash
pip install aegra-cli   # 注意装 aegra-cli，别装 aegra 这个不支持锁版本的便捷包装
aegra init               # 交互式：选位置、模板、项目名
cd <your-project>
cp .env.example .env     # 填 OPENAI_API_KEY
uv sync
uv run aegra dev         # 起 PostgreSQL + 开发服务器
```

或者直接从源码走 `docker compose up`，起来后 `http://localhost:2026/docs` 就是可交互的 API 文档。生产环境用 `aegra serve`（无热重载），`aegra up`/`aegra down` 管理全套 Docker 服务的启停。

## 谁该看这个

**适合**：已经在用 LangGraph 写 agent、不想被 LangSmith 的付费墙卡住自托管/自定义鉴权/定时任务这些基础能力的团队；愿意自己运维 Postgres + Redis 换取数据不出自己基础设施的场景；在意"迁移成本"的人——SDK 完全不变是这个项目最大的诚意。

**不适合 / 需要注意**：如果你压根没在用 LangGraph（比如自己手写状态机，或者用 CrewAI / AutoGen 这类别的框架），这个项目跟你没关系，它换的是部署层，不是 agent 框架本身；自托管意味着 Postgres/Redis 的可用性和备份是你自己的责任，LangSmith 云托管版本省掉的正是这部分运维负担，这个取舍要想清楚。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

## TL;DR

**Aegra is an open-source, self-hosted drop-in replacement for LangSmith Deployments (formerly LangGraph Platform)** — same `langgraph_sdk`, same Agent Protocol API. Your existing LangGraph code doesn't change; only where it runs does, moving from LangChain's cloud to your own FastAPI + PostgreSQL stack. The project was created in July 2025 and is now over a year old, with 1,129 stars, 236 forks, and a weekly release cadence in August alone (v0.10.2 → v0.10.3 → v0.10.4 in one week) — this has already reached production-grade maturity, not a fresh toy repo.

The problem it solves is specific: if you build agents with LangGraph, LangSmith's free tier only runs locally — deploying requires the paid Plus tier (still hosted on LangChain's cloud), and basics like custom auth and scheduled cron jobs are, per the official pricing page, gated behind the enterprise tier (custom pricing, license key required). Aegra moves all of that onto your own infrastructure, for free.

## What changes is where it runs, not how you write code

This is Aegra's entire reason to exist: your LangGraph agent code stays untouched — you just point `get_client(url=...)` at your own Aegra server:

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2026")
assistant = await client.assistants.create(graph_id="agent")
thread = await client.threads.create()

async for chunk in client.runs.stream(
    thread_id=thread["thread_id"],
    assistant_id=assistant["assistant_id"],
    input={"messages": [{"type": "human", "content": "Hello!"}]},
):
    print(chunk)
```

Because it's protocol-compatible (Agent Protocol), the front-end and debugging tools that grew up around the LangGraph ecosystem — Agent Chat UI, LangGraph Studio, AG-UI / CopilotKit — point at Aegra just as they would at LangSmith, no extra tooling swap required to go self-hosted.

## Architecture: a Redis queue plus Postgres persistence

FastAPI handles the HTTP layer, LangGraph itself manages state-machine execution, PostgreSQL stores checkpoints and persistent state, and Redis does three jobs: the task queue, cross-instance SSE pub/sub, and crash recovery.

The **worker architecture** is the part most worth noting: 30 concurrent runs per instance by default, with a lease-based mechanism for crash recovery — if a worker dies, the runs it claimed aren't lost; once the lease expires, another instance picks them up and resumes, and the whole thing scales horizontally across multiple instances. This isn't just documentation copy — August's commit history shows real engineering scar tissue: one fix addresses in-flight runs being incorrectly finalized during graceful shutdown (SIGTERM's drain path shared the same cancellation code path as a user-initiated cancel, so a run got marked interrupted and had its lease released — invisible to the reaper, recoverable only via a hard SIGKILL restart racing the lease timeout). Another fixes a race in assistant creation under concurrency (a classic check-then-insert TOCTOU: two concurrent requests both miss the existence check, both insert, and the loser's unique-constraint violation surfaced as an unhandled 500 instead of the expected status code). These read like fixes pulled out of real production traffic, not demo code validated against a contrived test case.

**Persistence** runs through native PostgreSQL checkpoints (an officially supported LangGraph backend), with pgvector bolted on for semantic key-value storage. **Streaming** supports both the legacy run-scoped mode and the newer Agent Protocol v2, which streams at the thread level with content-block events, per-subgraph lifecycle events, and native human-in-the-loop resume — the exact wire format the latest LangGraph SDK and `useStream()` target, enabled by default.

**Auth** is pluggable via Python handlers — JWT, OAuth, Firebase, or none at all. **Observability** runs on the OpenTelemetry standard, fanning out to any OTLP backend (Langfuse, Phoenix, etc.) rather than locking you into LangSmith's own tracing.

## Pricing comparison: enterprise-tier features, self-hosted for free

The README's comparison table (based on LangChain's official pricing as of February 2026) states this plainly:

| | LangSmith Deployments | Aegra |
|---|---|---|
| Deploy agents | Free tier: local dev only. Paid tier for cloud deploy | Free, unlimited |
| Custom auth | Not on free tier; available on Plus | Built-in Python handlers (JWT/OAuth/Firebase) |
| Scheduled cron jobs | Not on free tier | Built-in, free |
| Self-hosted | Enterprise tier only (license key required) | Always (Apache 2.0) |
| Bring your own database | Free/Plus: managed only. Enterprise: bring your own | Bring your own Postgres |
| Tracing | LangSmith only | Any OTLP backend |
| Data residency | LangChain's cloud (Free/Plus); your infra (Enterprise) | Always your infrastructure |

In other words: LangSmith's commercial tiering puts self-hosting, custom auth, and scheduled jobs behind an enterprise contract. Aegra open-sources all of it for free — the trade is that operational responsibility for Postgres and Redis moves onto you.

## Getting it running

The recommended path is the CLI (needs Python 3.12+ and Docker for PostgreSQL):

```bash
pip install aegra-cli   # install aegra-cli specifically — the "aegra" convenience package doesn't support version pinning
aegra init               # interactive — asks for location, template, project name
cd <your-project>
cp .env.example .env     # add your OPENAI_API_KEY
uv sync
uv run aegra dev         # starts PostgreSQL + dev server
```

Or run `docker compose up` straight from a source clone; once it's up, `http://localhost:2026/docs` is an interactive API doc. `aegra serve` runs the production server (no hot reload), and `aegra up`/`aegra down` manage the full Docker stack.

## Who should look at this

**Good fit**: teams already building agents on LangGraph who don't want LangSmith's paywall blocking basics like self-hosting, custom auth, or scheduled cron; anyone willing to operate their own Postgres + Redis in exchange for keeping data on their own infrastructure; anyone who weighs migration cost heavily — an unchanged SDK is this project's biggest selling point.

**Not a fit / worth noting**: if you're not already on LangGraph (hand-rolled state machines, or a different framework like CrewAI or AutoGen), this doesn't apply to you — it replaces the deployment layer, not the agent framework itself. Self-hosting means Postgres/Redis uptime and backups become your responsibility, which is exactly the operational burden LangSmith's managed cloud absorbs — worth thinking through that trade before switching.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
