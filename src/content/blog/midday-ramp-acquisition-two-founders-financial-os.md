---
title: "Midday：两个人的财务 OS，被 Ramp 收购前已服务 2 万家公司"
titleEn: "midday-ramp-acquisition-two-founders-financial-os"
description: "midday-ai/midday，14.7k stars，AGPL-3.0，TypeScript + Rust。两位创始人 Pontus & Viktor 从2023年做起，为「一个人跑一家公司」设计了一套财务操作系统：接入2万家银行、处理170万笔交易、8.12亿美元交易额。2026年5月被 Ramp 收购。它同时戳中了两类人：AI 创业者看到的是 2 人团队能做什么，独立创业者看到的是自己终于有了合适的工具。"
descriptionEn: "midday-ai/midday, 14.7k stars, AGPL-3.0, TypeScript + Rust. Two founders, Pontus & Viktor, built a financial OS for solo founders from 2023 — 20K+ banks, 1.7M transactions, $812M total volume. Acquired by Ramp in May 2026. It hit two audiences at once: AI startup founders who saw what a 2-person team can build, and solo operators who finally found a tool designed for them."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["开源", "SaaS", "财务", "创业", "TypeScript", "收购", "Mycelium"]
heroImage: "../../assets/images/midday-ramp-acquisition-two-founders-financial-os-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

2026年5月7日，Ramp 宣布收购 Midday。Ramp 是美国头部财务 AI 公司，市值数十亿美元，有几百名工程师。Midday 的创始团队只有两个人：Pontus 和 Viktor。

这件事被反复转发，不是因为"又一个创业公司被收购了"，而是因为两类人同时看到了自己关心的东西。

GitHub: https://github.com/midday-ai/midday | ⭐ 14,730 | AGPL-3.0 | TypeScript + Rust

---

## 两类人看到了什么

**AI 创业者看到的**：2 人团队，从 2023 年 9 月做起，没有融资新闻、没有大团队，把一个开源项目做到：

- 接入 20,000+ 银行（覆盖33个国家）
- 服务 20,600+ 企业账户
- 处理 170 万笔交易，总交易额 **8.12 亿美元**
- GitHub 14,700+ stars，1,800+ forks
- 最终被行业龙头以收购结束

这是一个小团队用 AI 能力乘以执行力的极端案例。

**独立创业者/自由职业者看到的**：这个工具是为「一个人跑一家公司」专门设计的。现有工具假设你有团队：时间追踪在一个地方，发票在另一个地方，收据散落在邮件和文件夹里，交易在银行后台。Midday 把这些都连起来，做成一个不需要你守着的系统。被 Ramp 收购、产品将关停的消息传出后，很多用户在 Reddit 和 X 上表示「终于找到一个合适的工具，结果要没了」。

---

## Midday 做了什么

Midday 的定位是**面向独立创始人和自由职业者的财务操作系统**，核心功能：

**发票**：创建、发送、追踪付款状态，支持多货币

**时间追踪**：记录可计费工时，直接关联到发票

**银行对账**：自动拉取账户交易，智能匹配收据和发票，标注异常

**财务概览**：收支汇总、现金流趋势、支出分类，不需要手动整理

**AI 助手**：基于你实际的财务数据回答问题——「这个月净收入多少」「哪些客户还没付款」「最大的支出类别是什么」

**文件存储**：收据、合同、发票统一归档，对账时直接调取

整套产品的核心命题是：**你的生意应该能自己解释自己**。你不需要每天查看仪表盘，系统会在有变化、有问题、有需要关注的事情时主动告诉你。

---

## 技术架构

```
前端：Next.js + Tailwind CSS（TypeScript）
后端：Supabase（PostgreSQL + Auth + Storage）
高性能部分：Rust
部署：Vercel / Supabase 托管
银行接入：Plaid + GoCardless（覆盖33个国家2万家银行）
AI：基于用户财务数据的上下文问答
MCP：支持 Claude、ChatGPT、Perplexity、Cursor、Raycast、Manus
```

代码库以 monorepo 组织，AGPL-3.0 许可证——这意味着商业使用需要开放源码，但完全可以自托管。

---

## 两人全程公开构建

Pontus 和 Viktor 从一开始就选择了「构建过程公开」：每个重要决策、每次重构、每个新功能的上线，都在 X 和 GitHub 上实时分享。这个做法带来了两个效果：

1. 用户和社区从早期就深度参与，问题反馈快，功能迭代有真实需求驱动
2. 产品本身获得了大量来自开发者社区的关注——14K stars 中很大一部分来自对「这两个人在做什么」感兴趣的工程师

收购公告里，两位创始人写道：

> "Viktor 和我做 Midday，是为了做一个我们自己想用的财务工具。我们自己设计、自己工程、自己发布每一次更新。我们把整个过程公开分享，包括每个决策和每个错误，并且能够与真正使用它的人并肩打造。"

---

## Ramp 收购意味着什么

Ramp 收购 Midday 后，Midday 产品将在3个月内关停。用户可以导出数据，符合条件的用户有迁移到 Ramp 的路径。

从 Ramp 的角度：Midday 是一个已经经过市场验证的财务 OS 团队，在小型企业/独立创业者这个市场积累了大量实战经验——20万笔交易、真实的银行对账场景、真实的发票工作流。这些是 Ramp 要往中小企业市场延伸时需要的。

从 Midday 角度：两个人把一个工具做到了行业龙头愿意为之支付收购价格，然后选择退出。产品关停，但开源仓库留下了。

---

## 自托管

Midday 的开源版本仍然可用，使用 Supabase 自托管：

```bash
git clone https://github.com/midday-ai/midday
cd midday
# 参考 apps/dashboard/.env.example 配置环境变量
# 需要 Supabase 项目 + Plaid/GoCardless API key
pnpm install
pnpm dev
```

AGPL-3.0 许可证：个人和非商业使用完全免费，商业使用需开放修改代码。

---

## 这件事真正有意思的地方

独立创始人市场不缺工具，但缺「设计上真的把你当成一个人在跑一家公司」的工具。Midday 找到了这个位置，用2人团队把它做成了价值数百万美元的资产。

这件事有意思的地方不是「又一个创业公司被收购了」，而是：**在 AI 让单人公司变得可能的时代，专门为单人公司设计的工具，本身也可以是一个单人公司做出来的**。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Midday: Two Founders, One Financial OS, 20K+ Banks — Then Ramp

*by Mycelium Protocol*

---

On May 7, 2026, Ramp — the category-leading AI platform for finance, valued in the billions, with hundreds of engineers — announced it was acquiring Midday. Midday's entire founding team: two people, Pontus and Viktor.

The announcement spread widely, not because of "another startup acquisition," but because two very different groups saw exactly what they cared about.

GitHub: https://github.com/midday-ai/midday | ⭐ 14,730 | AGPL-3.0 | TypeScript + Rust

---

### Two Audiences, One Product

**What AI startup founders saw**: A 2-person team, no funding announcements, no big org chart, shipping since September 2023 until they had:

- 20,000+ banks connected across 33 countries
- 20,600+ business accounts
- 1.7 million transactions processed, **$812M total volume**
- 14,700+ GitHub stars, 1,800+ forks
- A category leader willing to acquire them

This is what a small team with AI leverage looks like at the extreme end.

**What solo founders and freelancers saw**: A tool designed, for once, around the reality of running a company alone. Existing software assumes you have a team: time tracking in one place, invoices in another, receipts scattered across inboxes and folders, transactions buried inside bank dashboards. Midday connected all of it and ran quietly in the background. When the acquisition and shutdown announcement dropped, users on Reddit and X responded with "I finally found the right tool and now it's going away."

---

### What Midday Built

Midday positioned itself as a **financial OS for solo founders and freelancers**. Core features:

**Invoicing**: Create, send, and track payment status across currencies

**Time tracking**: Log billable hours and connect them directly to invoices

**Bank reconciliation**: Auto-sync transactions from connected accounts, smart-match receipts and invoices, flag anomalies

**Financial overview**: Revenue/expense summaries, cash flow trends, spending categories — no manual assembly required

**AI assistant**: Answer questions against your actual financial data — "what's my net revenue this month," "which clients haven't paid," "what's my biggest expense category"

**File storage**: Receipts, contracts, invoices in one place, available when reconciling

The core promise: **your business should explain itself as it runs**. You shouldn't need to check a dashboard daily — the system surfaces changes, problems, and things that need attention.

---

### The Stack

```
Frontend: Next.js + Tailwind CSS (TypeScript)
Backend: Supabase (PostgreSQL + Auth + Storage)
Performance-critical paths: Rust
Deploy: Vercel / Supabase hosted
Bank connectivity: Plaid + GoCardless (20K+ banks, 33 countries)
AI: context-aware Q&A over the user's financial data
MCP: Claude, ChatGPT, Perplexity, Cursor, Raycast, Manus
```

Monorepo structure, AGPL-3.0 license — commercial use requires source-open, but fully self-hostable.

---

### Building in Public

Pontus and Viktor chose to build in public from day one: every major decision, refactor, and feature launch shared on X and GitHub in real time. Two effects:

1. Early users engaged deeply, feedback was fast, iteration was driven by real needs
2. The product built a developer following that tracked "what are these two people building" — a meaningful portion of those 14K stars came from engineers watching the process

From the acquisition announcement:

> "Viktor and I started Midday to build the financial tool we wished existed. We designed it, engineered it, and shipped every update ourselves. We shared the entire process in public, every decision, every mistake, and got to build alongside the people who actually used it."

---

### What the Ramp Acquisition Means

Midday's product winds down over three months. Users can export their data; eligible users get a migration path to Ramp.

From Ramp's perspective: Midday is a team that shipped a validated financial OS in the SMB/solo-founder segment, with real transaction volume and real edge cases — bank reconciliation, invoicing workflows, multi-currency. That's ground truth for Ramp's expansion down-market.

From Midday's perspective: two people built something a category leader wanted to acquire. Product closes. Open-source repo stays.

---

### Self-Host

The open-source version remains available:

```bash
git clone https://github.com/midday-ai/midday
cd midday
# copy apps/dashboard/.env.example and fill in values
# requires a Supabase project + Plaid/GoCardless API keys
pnpm install
pnpm dev
```

AGPL-3.0: free for personal and non-commercial use; commercial deployments must open modifications.

---

### What's Actually Interesting Here

The solo-founder market isn't short on tools. What it lacked was a tool *designed* around the reality of one person running an entire company. Midday found that position and turned it into an asset worth acquiring — with a team of two.

The interesting part isn't "another startup got acquired." It's that **in the era where AI makes the one-person company viable, the tool designed specifically for the one-person company can itself be built by a one-person-equivalent team**.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
