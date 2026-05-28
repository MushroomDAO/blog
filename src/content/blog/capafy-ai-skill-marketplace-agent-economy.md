---
title: "Capafy：你的 AI 技能可以作为产品出售，在你睡觉时帮你赚钱"
titleEn: "Capafy: Sell Your AI Skills as a Product, Earn While You Sleep"
description: "Capafy 是一个刚上线的 AI 技能市场，开发者可以上传在 Claude Code、Codex 或 OpenClaw 中构建的 Agent 技能，设置按小时、订阅或一次性付费定价，每次有人使用就获得收益，代码和 Prompt 对用户完全不可见。"
descriptionEn: "Capafy is a newly launched AI skills marketplace where developers upload agent skills built in Claude Code, Codex, or OpenClaw, set hourly/subscription/one-time pricing, and earn each time someone uses them — code and prompts invisible to users."
pubDate: "2026-05-28"
updatedDate: "2026-05-28"
category: "Tech-News"
tags: ["AI Agent", "技能市场", "Capafy", "Claude Code", "意义经济", "开发者变现", "Agent技能", "创作者经济"]
heroImage: "../../assets/images/capafy-ai-skill-marketplace-banner.jpg"
---

5 月 26 日，一个叫 Capafy 的平台上线了。它的核心主张只有一句话：**你的 AI 技能可以作为产品运行，每次有人用它，你就拿到钱。**

> 📌 官方网站：https://capafy.ai  
> 技能市场：https://capafy.ai/market

## 它在解决什么问题？

过去两年，开发者在 Claude Code、Codex、OpenClaw 里搭建了大量有价值的 Agent 技能——从病毒式视频脚本生成，到招聘简历筛选，到高转化率冷邮件写作。

这些技能通常以两种方式存在：要么放在 GitHub 开源出去，任何人都可以 fork、复制、再分发，创作者拿不到任何回报；要么就锁在自己电脑里，价值只对自己有用。

Capafy 试图打开第三条路：**闭源上架、服务器端执行、按使用量付费。**

用户看到的只有输出结果，看不到背后的代码、Prompt 或方法论。创作者保留完整的知识产权，同时让技能真正流通起来。

## 运作方式

### 对创作者：上传技能，设定价格

支持从以下工具中上传技能：
- **Claude Code**（Anthropic 的代码型 Agent）
- **Codex**（OpenAI 的代码型 Agent）
- **OpenClaw**（开源 Agent 框架）
- **Hermes**（Capafy 自有格式）

技能格式遵循 **SKILL.md**——这是当前 Agent 生态中已经形成事实标准的技能描述格式。

定价支持三种模式：
| 模式 | 典型价位 |
|------|---------|
| 按小时 | $5.99/小时 |
| 订阅制 | $2.99–$11.99/周（日、周、月可选） |
| 一次性购买 | $4.99–$9.99 |

平台负责托管和执行，创作者不需要维护服务器。每次调用自动结算。

### 对用户：一键调用专家级技能

- 直接在浏览器运行，无需安装任何东西
- 一键集成到 Claude Code、Codex 或 OpenClaw
- 通过代理连接，让你自己的 Agent 直接调用 Capafy 上的专家技能

已有 50+ 技能上线，覆盖：
- **内容创作**：社媒文案、TikTok 脚本、视频钩子优化
- **商业工具**：亚马逊 Listing 生成、PPC 审计、市场分析报告
- **专业服务**：研究综合（10+ 来源、交叉验证）、简历生成、法律文件草拟
- **媒体生成**：婚礼照片合成、天气艺术海报、电商产品视频

## 它的市场定位

当前 Agent 技能市场格局：

| 平台 | 模式 | 特点 |
|------|------|------|
| **Capafy** | 闭源，按执行付费 | 创作者 IP 保护，独立定价 |
| Agensi | 审核制，80/20 分成 | 质量把控较严 |
| SkillsMP | 免费，GitHub 来源 | 80 万+ 技能，零变现 |
| ClawHub | OpenClaw 官方 | 与生态绑定 |
| skills.sh | 快照注册 | 轻量，偏向分发 |
| Anthropic Plugin Marketplace | 官方认证 | 数量有限 |

Capafy 走的是最"重变现"的路线——它的竞争优势不是技能数量，而是**创作者能从中拿到真实收益**这件事本身。

## 值得关注的细节

**闭源执行的商业逻辑**：技能在服务器端运行，用户得到输出但看不到逻辑。这解决了开源生态的一个结构性问题——为什么高质量的私有技能不愿意开放共享？因为开放等于放弃竞争壁垒。Capafy 给了一个不必放弃 IP 就能分发的出口。

**数据政策**：Capafy 明确声明不出售用户数据，也不用用户的输入来训练 AI 模型。每个技能有独立的隐私条款，用户在使用前可以查看。

**与 Mycelium PGL 的对比**：Capafy 的变现逻辑和 Mycelium Protocol 的 PGL（Public Goods Layer）有相似的出发点——让内容创作者/技能创作者真正从自己的贡献中获益。区别在于：PGL 倾向于链上透明分账和开源生态，Capafy 走的是闭源保护 + 中心化平台。两种路径代表了同一个问题的不同解法。

## 目前的边界

- **没有开源仓库**：Capafy 本身是闭源平台，目前没有公开 GitHub 组织
- **平台分成比例未公开**：创作者拿多少、平台留多少，官方没有明确披露
- **生态仍处早期**：刚上线两天，50+ 技能，头部效应尚未形成
- **集中化风险**：技能托管在 Capafy 服务器，平台停运或规则变化都影响创作者

## 为什么现在值得关注

Agent 生态正在从"工具"走向"服务"。能力强的开发者已经在用 Claude Code 解决以前需要请人来做的问题——下一步自然是问：**这个能力能卖吗？卖给谁？怎么卖？**

Capafy 给出了一个明确的入口。它刚上线，规则还在跑通的过程中，但方向是清晰的：**专家知识 × Agent 执行 = 可流通的数字产品**。

早期上传优质技能的创作者，有机会在这个市场格局固化之前占据头部位置。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

On May 26, 2026, a platform called Capafy went live. Its core premise is simple: **your AI skills can run as a product, and every time someone uses them, you get paid.**

> 📌 Website: https://capafy.ai  
> Skill Market: https://capafy.ai/market

## What Problem Does It Solve?

Over the past two years, developers have built enormous value inside Claude Code, Codex, and OpenClaw — viral video script generators, resume screeners, high-converting cold email writers. These skills typically exist in two dead ends: open-sourced on GitHub (anyone can fork, copy, redistribute; creator gets nothing), or locked on a local machine (value stays private).

Capafy opens a third path: **closed-source listing, server-side execution, pay-per-use.**

Users see only the output. They never see the underlying code, prompts, or methodology. Creators retain full IP while actually getting their skills into circulation.

## How It Works

### For Creators: Upload and Price

Supports skills built in Claude Code, Codex, OpenClaw, and Hermes. The format is **SKILL.md** — already emerging as the de facto standard in the agent ecosystem.

Three pricing models:
| Model | Typical Price |
|-------|--------------|
| Hourly | $5.99/hour |
| Subscription | $2.99–$11.99/week |
| One-time | $4.99–$9.99 |

The platform handles hosting and execution. Creators don't maintain servers. Every invocation settles automatically.

### For Users: Expert Skills On Demand

Run directly in browser, integrate one-click into Claude Code/Codex/OpenClaw, or connect via agent proxy so your own agent calls Capafy skills directly.

50+ skills live at launch across content creation, e-commerce, professional services, and media generation.

## Market Positioning

| Platform | Model | Differentiator |
|----------|-------|---------------|
| **Capafy** | Closed-source, pay-per-execution | Creator IP protection, independent pricing |
| Agensi | Curated, 80/20 split | Stricter quality control |
| SkillsMP | Free, GitHub-sourced | 800K+ skills, zero monetization |
| ClawHub | OpenClaw official registry | Ecosystem-tied |
| skills.sh | Snapshot registry | Lightweight distribution |

Capafy takes the most monetization-heavy approach. Its competitive edge isn't skill volume — it's that creators can actually earn real income.

## Notable Details

**The closed-source business logic**: Execution happens server-side; users get outputs without seeing logic. This solves a structural problem in open-source ecosystems — why would creators share high-value private skills? Because sharing means giving up competitive advantage. Capafy provides a distribution channel that doesn't require surrendering IP.

**Data policy**: Capafy explicitly states it doesn't sell user data or use inputs to train AI models. Each skill has independent privacy terms reviewable before use.

**Comparison to Mycelium PGL**: Capafy's monetization philosophy shares DNA with Mycelium Protocol's PGL (Public Goods Layer) — both aim to let skill creators earn from their contributions. The difference: PGL favors on-chain transparent revenue splitting in open ecosystems; Capafy uses closed-source protection + centralized platform. Two different solutions to the same problem.

## Current Limitations

- **No open-source repository**: Capafy is a closed platform with no public GitHub organization
- **Platform commission undisclosed**: Revenue split between creators and platform is not publicly stated
- **Early-stage ecosystem**: 50+ skills, two days old, no dominant skills yet
- **Centralization risk**: Skills hosted on Capafy servers; platform changes affect creators

## Why Watch It Now

The agent ecosystem is shifting from "tools" to "services." Capable developers are already using Claude Code to solve problems that previously required hiring specialists. The natural next question is: **can this capability be sold? To whom? How?**

Capafy provides a concrete entry point. It's freshly launched, rules are still being proven out, but the direction is clear: **expert knowledge × agent execution = tradeable digital products**.

Creators who upload quality skills now have a chance to establish top positions before the market structure solidifies.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
