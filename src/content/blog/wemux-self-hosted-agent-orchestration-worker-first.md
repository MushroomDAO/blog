---
title: "Wemux：把 AI Agent 的活儿放回你自己的机器上跑，控制面不碰你的代码"
titleEn: "Wemux: Run Your AI Agents on Your Own Machines — the Control Plane Never Touches Your Code"
description: "云端 Agent 平台的通行做法是把你的仓库拉进它们的沙箱。Wemux 反着来：控制面只做规划、路由和评审，真正的编码执行发生在你自己的 worker 机器上，跑在隔离的 Git worktree 里，用你自己的凭据。Apache-2.0，TypeScript 占 16.2 MB，69 stars、13 forks、58 次提交——2026-08-25 才建仓，13 天大的新项目。自托管社区版包含控制面、worker、BYOK、飞书/Slack/钉钉/企微/微信/WhatsApp 六个 IM 通道和 Electron + React Native 客户端；托管模型网关、计费和云节点池是单独的商业服务，不在这个仓库里。"
descriptionEn: "Cloud agent platforms pull your repo into their sandbox. Wemux inverts that: the control plane only plans, routes and reviews, while the actual coding runs on worker machines you own, in isolated Git worktrees, with your own credentials. Apache-2.0, 16.2 MB of TypeScript, 69 stars, 13 forks, 58 commits — the repo was created on 2026-08-25, making it 13 days old. The self-hosted community edition includes the control plane, worker daemon, BYOK, six IM channels (Feishu/Slack/DingTalk/WeCom/WeChat/WhatsApp) and Electron + React Native clients; the hosted model gateway, billing and cloud-node pool are separate commercial services outside this repo."
pubDate: "2026-09-07"
updatedDate: "2026-09-07"
category: "Tech-News"
tags: ["AI Agent", "自托管", "开源", "Agent 编排", "Claude Code", "BYOK", "TypeScript", "本地优先"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/wemux-ai/wemux
中文 README：https://github.com/wemux-ai/wemux/blob/main/README.zh-CN.md
自托管文档：https://github.com/wemux-ai/wemux/blob/main/docs/SELF-HOSTING.md
托管服务：https://wemux.ai
授权：Apache-2.0

---

## 一句话结论

**几乎所有云端 Agent 平台的第一步都是"把你的仓库拉进我们的沙箱"。Wemux 把这一步删掉了。** 它的控制面（control plane）只负责理解需求、拆任务、选 agent、路由和收结果，**从不执行你的代码**；真正干活的是跑在你自己机器上的 worker 守护进程，在隔离的 Git worktree 和分支里，用你自己的模型密钥和你自己的凭据。

代价也直白：**这是一个 13 天大的项目。** 仓库 2026-08-25 建立，到今天 69 stars、13 forks、58 次提交。架构方向对，但还没经过时间。

## 它到底把什么东西倒过来了

值得先说清楚"worker-first"具体指什么，因为这个词现在被用得很松。

Wemux 的分工是这样的：

```text
┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐
│  web        │──▶│  server      │──▶│  worker (daemon)    │
│  console    │   │  control     │   │  ├─ repo prepare    │
│  (React)    │   │  plane       │   │  ├─ worktree        │
│             │   │  (Hono)      │   │  ├─ agent runtime   │
└─────────────┘   │  Postgres    │   │  └─ git delivery    │
                  │  S3/R2       │   └─────────────────────┘
                  └──────────────┘
```

左边两个盒子可以放在云上（Railway、你的 VPS、随便），右边那个盒子**必须**在你控制的机器上。跨过中间那道箭头传回去的只有 diff、日志和产物——不是你的代码库。

五步流程：

1. **Describe** — 用自然语言在主对话、看板、或者干脆在飞书/Slack 里创建任务
2. **Plan** — 主 agent 把话变成结构化任务，选 agent、选工作区，路由到空闲 worker
3. **Execute** — worker 在你机器上开一个隔离的 Git worktree，agent runtime（OpenCode / Claude Code / Codex）用你的凭据干活
4. **Review** — worker 把 diff 和结果报回来，**你审过才合并**
5. **Deliver** — 批准的改动落地，每一步在工作区会话里可追溯

第 3 步是全部重点。模型推理仍然发生在你的模型提供方（Anthropic、OpenAI、OpenRouter、本地模型都行），但**代码的读写发生在你的磁盘上**。README 的 FAQ 里问得很直接："Does my code ever leave my machine?" 答案是 No。

## 那 worker 机器需要多强？

这是我看到架构图后的第一个疑问，README 也预判到了：**不需要 GPU，不需要强机器**。

worker 干的事只是跑一个 agent CLI——推理在模型提供方那边发生。所以任何一台笔记本或者小服务器都能当 worker。这跟"本地跑模型"是两回事，别混淆：Wemux 本地化的是**执行**，不是**推理**。

顺带一个实际的好处：worker 不必和控制面在同一台机器上。在控制台的 **Execution → Add Executor** 里能生成一条安装命令：

```bash
curl -fsSL https://<server>/install | bash -s -- \
  --pairing-code '<PAIRING_CODE>' \
  --server-url 'https://<server>'
```

一条命令完成安装、配对、注册、起服务。Windows/WSL 和 Docker 的版本在同一个对话框里。

## 上手：本地全套跑起来

前置：Node.js 20+、pnpm 10+、Docker（跑 Postgres）。

```bash
git clone https://github.com/wemux-ai/wemux.git
cd wemux
pnpm install

# 1. 起基础设施（Postgres + 对象存储）
pnpm dev:infra:up

# 2. 配环境变量
cp .env.development.local.example .env.development.local
#   改 DATABASE_URL / OBJECT_STORAGE_* 指向你的实际配置

# 3. 起控制面 + 控制台
pnpm dev:server    # API 在 :8989
pnpm dev:client    # web 控制台

# 4. 起一个 worker（本机或任意机器）
pnpm dev:worker
#   把 worker 和控制面配对，然后创建任务
```

嫌麻烦的话，`pnpm dev` 一条命令在一个 TUI 里同时拉起 server、console 和 worker。

存储是 PostgreSQL（Drizzle 迁移）+ S3 兼容对象存储（R2/MinIO 都行）。

**想要生产部署**，仓库里有 `deploy/docker/docker-compose.production.yml` + `.env.production.example` 的一键栈，以及 Railway 的 IaC 脚本（`.railway/railway.ts`）：

```bash
railway login
railway init          # 已有项目用 railway link
railway config apply  # 建 Postgres + Bucket + 控制面，自动接好 DATABASE_URL
railway up
```

这里有个**踩坑警告值得单独拎出来**，README 自己标了 heads-up：Railway 已经废弃了 Config-as-Code（`railway.json`），新服务不再读它。如果你走 **New Project → Deploy from GitHub repo** 这条路，Railway 会把这个仓库误判成 TanStack Start 应用，启动时崩在 `srvx: command not found`。**必须用上面的 IaC 流程**，或者官方模板，或者手动设置 build/start/healthcheck 命令。

生产环境必填的几个密钥，别漏：`BETTER_AUTH_SECRET`、`TOKEN_SECRET`、`SECRET_ENCRYPTION_KEY`（都用 `openssl rand -hex 32` **分别**生成，不要复用同一个值），以及 `WEMUX_PUBLIC_BASE_URL` 和 `BETTER_AUTH_URL` 指向最终公网 origin。`PORT` **不要**写死——Railway 会自己注入。

## 开源到哪儿为止？

这是我对任何"开源 + 托管"双轨项目都会先查的一件事，因为这里最容易埋雷。Wemux 的边界划得比大多数同类项目清楚，而且明说了**社区版里的商业功能是中性空实现（no-op stub），不是收费闸门**：

| 能力 | 开源（本仓库） | 仅商业托管 |
|---|---|---|
| 核心平台——web 控制台、控制面、worker 守护进程 | ✅ | — |
| Worker 执行（配对、worktree、agent runtime） | ✅ | — |
| BYOK 模型配置 | ✅ | — |
| 主对话 / 任务 / 工作区编排与群聊 | ✅ | — |
| Drive（工作区级文件存储与共享） | ✅ | — |
| 六个 IM 通道（飞书/Slack/钉钉/企微/微信/WhatsApp） | ✅ | — |
| 多节点组网（easytier） | ✅ | — |
| 用量看板与用户自设配额 | ✅ | 平台强制配额 |
| 管理后台（用户/反馈/运维） | ✅ | 计费、积分、网关、云节点、合作商面板 |
| 原生客户端（Electron + React Native 安卓/iOS） | ✅ | — |
| 托管模型网关（官方模型目录） | — | ✅ |
| 托管云节点池 | **自托管运行时已开源**（docker-cli / boxlite / ascii-box / CF sandbox） | 托管池 |
| 订阅计费、积分与支付 | — | ✅ |

翻译成人话：**围绕"本地 worker + 自带模型密钥"这条主线，社区版是完整自洽的**，核心编排、执行、协作一个不缺。你放弃的是"不想自己管基础设施"这份省心。

一个容易忽略的细节：平台本身 Apache-2.0，但它编排的那些 agent CLI 各有各的授权——OpenCode 是 Apache-2.0，**Claude Code 和 Codex 是 Anthropic 和 OpenAI 的专有工具**，你用自己的账号认证，受它们各自的条款约束。Wemux 开源不代表你这条链路上全都是开源的。

## 遥测这块处理得挺体面

自托管实例默认每天上报一次匿名聚合用量：版本号、操作系统，和五个累计计数器（用户 / 组织 / 任务 / 会话 / agent 启动次数）。

明确**不采集**：仓库名、任务标题、会话内容、用户名、邮箱、IP、代码——任何内容或身份数据。字段白名单在源码里可审计（`packages/shared/src/types/community-usage.ts`），schema 文档在 `docs/TELEMETRY.md`。

关掉是一个环境变量的事：

```bash
WEMUX_USAGE_REPORTING_DISABLED=1
```

而且上报是 best-effort，不阻塞任何东西，关掉不影响任何功能。**能把白名单提交进源码让人查，这个做法应该成为默认，可惜现在还不是。**

## 该不该现在上手

先说不该的理由，因为它比较硬：

- **13 天大的仓库。** 2026-08-25 建仓，58 次提交，5 个 open issue。这个体量的平台（16.2 MB TypeScript，覆盖 web / server / worker / desktop / mobile 五个应用）在两周内成型，意味着它大概率是内部开发一段时间后才开源的——但公开可验证的运行历史就是只有 13 天。
- **69 stars。** 不是社区已经验证过的东西，你会是早期用户，遇到问题得自己读源码。
- 生产部署要你自己管 Postgres、对象存储、密钥轮换。

该上手的理由：

- 如果你的**约束条件是"代码不能出本机"**——受监管行业、客户代码、内部仓库——那市面上大部分云端 Agent 平台你根本用不了，Wemux 的架构是直接为这个约束设计的，不是事后打补丁。
- 六个 IM 通道进站是真的少见。"在飞书群里说一句话 → 落到你自己机器上的 worktree → 回来一个 diff 给你审"，这条链路对国内团队的价值不用多解释。
- Apache-2.0 + 完整自托管，最坏情况是你 fork 自己维护。

**我的判断：现在适合起一个自托管实例试真实任务，不适合直接放进关键路径。** 先用它跑那些"做错了也不心疼"的任务，观察一两个月的提交节奏和 issue 响应，再决定要不要往深了用。

## FAQ

**我的代码会离开我的机器吗？**
不会。任务在你的 worker 上、隔离的 Git worktree 里执行，只有 diff、日志和产物报回控制面。agent runtime 用你的凭据在你机器上跑，BYOK 模型密钥不出 worker。控制面从不执行你的代码。

**需要很强的机器或者 GPU 吗？**
不需要。worker 只是在本地跑 agent CLI，模型推理发生在你的模型提供方那边。任何笔记本或服务器都能当 worker。

**能用哪些 agent runtime 和模型？**
OpenCode、Claude Code、Codex 三种 runtime，模型是你的 runtime 支持的任何一个——自带密钥（BYOK）。

**必须自托管吗？**
不必须。同样的产品有托管版（wemux.ai），带托管云节点和计费。本仓库是可自托管的社区版。

**真的免费吗？**
仓库里的一切都是 Apache-2.0，包括自托管云节点运行时。只有单独运营的托管服务——模型网关、托管云节点池、计费、合作商系统——是商业的，而且都不在这个仓库里。

**它和云端 Agent 平台的区别到底在哪？**
Worker-first 执行：代码跑在你控制的机器上，在隔离 worktree 里，合并前有人工 diff 评审。再加上多节点组网、IM 通道集成和工作区级协作——而且全部可自托管。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

*by Mycelium Protocol*

---

Repository: https://github.com/wemux-ai/wemux
Self-hosting guide: https://github.com/wemux-ai/wemux/blob/main/docs/SELF-HOSTING.md
Hosted service: https://wemux.ai
License: Apache-2.0

---

## The Short Version

**Almost every cloud agent platform starts by pulling your repository into its sandbox. Wemux deletes that step.** Its control plane understands requirements, splits tasks, picks agents, routes and collects results — but **never executes your code**. The actual work happens on worker daemons running on your own machines, in isolated Git worktrees and branches, with your own model keys and your own credentials.

The catch is equally plain: **this is a 13-day-old project.** The repo was created on 2026-08-25; as of today it has 69 stars, 13 forks and 58 commits. The architecture points the right way, but it has not been through time yet.

## What Exactly Gets Inverted

"Worker-first" is a loosely used term, so it is worth pinning down.

```text
┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐
│  web        │──▶│  server      │──▶│  worker (daemon)    │
│  console    │   │  control     │   │  ├─ repo prepare    │
│  (React)    │   │  plane       │   │  ├─ worktree        │
│             │   │  (Hono)      │   │  ├─ agent runtime   │
└─────────────┘   │  Postgres    │   │  └─ git delivery    │
                  │  S3/R2       │   └─────────────────────┘
                  └──────────────┘
```

The two boxes on the left can live in the cloud — Railway, your VPS, wherever. The box on the right **must** live on a machine you control. What crosses that arrow on the way back is diffs, logs and artifacts — not your codebase.

The five-step flow:

1. **Describe** — create a task in natural language from the main chat, a kanban board, or an inbound IM channel (Feishu / Slack / …)
2. **Plan** — a main agent turns your words into a structured task, picks an agent and workspace, routes it to an available worker
3. **Execute** — the worker opens an isolated Git worktree on your machine; the agent runtime (OpenCode / Claude Code / Codex) works with your credentials
4. **Review** — the worker reports a diff and results; **nothing merges until you approve**
5. **Deliver** — approved changes land, every step traceable in the workspace session

Step 3 is the whole point. Model inference still happens at your provider (Anthropic, OpenAI, OpenRouter, local models — your choice), but **reads and writes of your code happen on your disk**. The README's FAQ asks it bluntly: "Does my code ever leave my machine?" The answer is no.

## How Powerful Does the Worker Need to Be?

This was my first question after seeing the architecture diagram, and the README anticipates it: **no GPU, no beefy machine required.**

The worker only runs an agent CLI — inference happens at your model provider. So any laptop or small server can be a worker. Don't confuse this with running models locally: Wemux localizes **execution**, not **inference**.

A practical bonus: the worker need not sit on the same machine as the control plane. **Execution → Add Executor** in the console generates an install command:

```bash
curl -fsSL https://<server>/install | bash -s -- \
  --pairing-code '<PAIRING_CODE>' \
  --server-url 'https://<server>'
```

One command installs, pairs, registers and starts the service. Windows/WSL and Docker variants come from the same dialog.

## Getting Started

Requirements: Node.js 20+, pnpm 10+, Docker (for Postgres).

```bash
git clone https://github.com/wemux-ai/wemux.git
cd wemux
pnpm install

# 1. Start infrastructure (Postgres + object storage)
pnpm dev:infra:up

# 2. Configure environment
cp .env.development.local.example .env.development.local
#   edit DATABASE_URL / OBJECT_STORAGE_* to match your setup

# 3. Run control plane + console
pnpm dev:server    # API on :8989
pnpm dev:client    # web console

# 4. Run a worker (same machine or any machine)
pnpm dev:worker
```

Prefer one command? `pnpm dev` brings up server, console and worker together in a TUI.

Storage is PostgreSQL (Drizzle migrations) plus S3-compatible object storage (R2/MinIO both fine).

For **production**, the repo ships a one-command stack (`deploy/docker/docker-compose.production.yml` + `.env.production.example`) and Railway IaC (`.railway/railway.ts`):

```bash
railway login
railway init          # or railway link for an existing project
railway config apply  # creates Postgres + Bucket + control plane, wires DATABASE_URL
railway up
```

One **trap worth pulling out** — the README flags it as a heads-up: Railway deprecated Config-as-Code (`railway.json`) and new services no longer read it. Going through **New Project → Deploy from GitHub repo** makes Railway misdetect this repo as a TanStack Start app, and it crashes at startup with `srvx: command not found`. **Use the IaC flow above**, the official template, or set build/start/healthcheck commands manually.

Do not skip the production secrets: `BETTER_AUTH_SECRET`, `TOKEN_SECRET` and `SECRET_ENCRYPTION_KEY` (generate each **separately** with `openssl rand -hex 32` — do not reuse one value), plus `WEMUX_PUBLIC_BASE_URL` and `BETTER_AUTH_URL` pointing at the final public origin. Do **not** pin `PORT` — Railway injects it.

## Where Does Open Source Stop?

This is the first thing I check on any open-core project, because it is where the landmines usually are. Wemux draws the line more clearly than most, and explicitly states that the commercial capabilities appear in the community edition as **neutral no-op stubs — never gates, never paywalls**:

| Capability | Open source (this repo) | Commercial hosted only |
|---|---|---|
| Core platform — console, control plane, worker daemon | ✅ | — |
| Worker execution (pairing, worktrees, agent runtime) | ✅ | — |
| BYOK model configuration | ✅ | — |
| Main chat / tasks / workspaces orchestration & group chat | ✅ | — |
| Drive (workspace file storage & sharing) | ✅ | — |
| Six IM channels (Feishu/Slack/DingTalk/WeCom/WeChat/WhatsApp) | ✅ | — |
| Multi-node mesh (easytier) | ✅ | — |
| Usage dashboard & user-set quota | ✅ | platform-enforced quota |
| Admin console (users / feedback / ops) | ✅ | billing, credits, gateways, cloud nodes, partners |
| Native clients (Electron + React Native Android/iOS) | ✅ | — |
| Hosted model gateway (official model catalog) | — | ✅ |
| Managed cloud nodes | **self-hosted runtime included** (docker-cli / boxlite / ascii-box / CF sandbox) | hosted pool |
| Subscription / usage billing, credits & payments | — | ✅ |

In plain terms: **around the core line of "local workers + BYOK models", the community edition is fully self-contained.** What you give up is the convenience of not running infrastructure yourself.

One detail that is easy to miss: the platform is Apache-2.0, but the agent CLIs it orchestrates carry their own licenses — OpenCode is Apache-2.0, while **Claude Code and Codex are proprietary tools of Anthropic and OpenAI**. You authenticate with your own accounts and are subject to their terms. Wemux being open source does not make the whole chain open source.

## Telemetry Is Handled Decently

Self-hosted instances report anonymous aggregate usage once a day: version, OS, and five cumulative counters (users / orgs / tasks / sessions / agent starts).

Explicitly **never collected**: repository names, task titles, session content, usernames, emails, IPs, code — any content or identity data. The field whitelist is auditable in source (`packages/shared/src/types/community-usage.ts`), with the schema documented in `docs/TELEMETRY.md`.

Turning it off is one environment variable:

```bash
WEMUX_USAGE_REPORTING_DISABLED=1
```

Reporting is best-effort and never blocks anything; disabling it affects no feature. **Committing the whitelist to source so anyone can audit it should be the default. It still isn't.**

## Should You Adopt It Now?

The reasons against, because they are the harder ones:

- **A 13-day-old repository.** Created 2026-08-25, 58 commits, 5 open issues. A platform of this size — 16.2 MB of TypeScript spanning web / server / worker / desktop / mobile — coming together in two weeks means it was almost certainly developed internally before being opened. But the publicly verifiable track record is 13 days.
- **69 stars.** This is not community-validated yet. You would be an early user, reading source when things break.
- Production deployment means you own Postgres, object storage and key rotation.

The reasons for:

- If your **binding constraint is "code cannot leave the machine"** — regulated industry, client code, internal repos — most cloud agent platforms are simply unusable for you. Wemux's architecture is designed for that constraint rather than patched for it after the fact.
- Six inbound IM channels is genuinely rare. "Say something in a Feishu group → it lands in a worktree on your own machine → a diff comes back for review" needs little explanation as a workflow.
- Apache-2.0 plus full self-hosting means the worst case is forking and maintaining it yourself.

**My read: it is worth standing up a self-hosted instance and throwing real tasks at it now, but not worth putting on a critical path yet.** Run the tasks you would not mind getting wrong, watch the commit cadence and issue responsiveness for a month or two, then decide how deep to go.

## FAQ

**Does my code ever leave my machine?**
No. Tasks execute on your workers in isolated Git worktrees; only diffs, logs and artifacts go back to the control plane. Agent runtimes run with your credentials on your machine, and BYOK keys never leave the worker. The control plane never executes your code.

**Do I need a powerful machine or GPU?**
No. The worker just runs the agent CLI locally — inference happens at your model provider. Any laptop or server can be a worker.

**Which agent runtimes and models can I use?**
OpenCode, Claude Code and Codex, with any model your runtime supports — bring your own keys.

**Do I have to self-host?**
No. The same product is offered as a hosted service (wemux.ai) with managed cloud nodes and billing. This repo is the self-hostable community edition.

**Is it really free?**
Everything in the repository is Apache-2.0, including the self-hosted cloud-node runtime. Only separately operated hosted services — model gateway, hosted cloud-node pool, billing, partner systems — are commercial, and none is part of this repo.

**How is it different from cloud agent platforms?**
Worker-first execution: code runs on machines you control, in isolated worktrees, with human-in-the-loop diff review before merge — plus multi-node mesh, IM channel integrations and workspace-level collaboration, all self-hostable.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
