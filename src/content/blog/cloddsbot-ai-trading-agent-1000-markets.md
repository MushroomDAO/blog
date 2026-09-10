---
title: 'CloddsBot：基于 Claude 的开源 AI 交易 Agent，自主横扫 1000+ 市场'
titleEn: "CloddsBot: Open-Source AI Trading Agent Built on Claude, Running Autonomously Across 1000+ Markets"
description: "开源 AI 交易 Agent，跨 Polymarket、Kalshi、Binance、Hyperliquid、5 条 EVM 链等 1000+ 市场自主操作，内置 118+ 策略和机器对机器支付协议，自托管，基于 Claude 驱动。"
descriptionEn: "Open-source AI trading agent running autonomously across 1000+ markets including Polymarket, Kalshi, Binance, Hyperliquid, and 5 EVM chains. 118+ strategies, agent commerce protocol for machine-to-machine payments, self-hosted, built on Claude."
pubDate: "2026-09-10"
updatedDate: "2026-09-10"
category: "Tech-News"
tags: ["AI-agent", "trading-bot", "Claude", "DeFi", "agent-economy", "open-source"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
---

> 📌 开源仓库：CloddsBot — Open Source AI trading agent
> GitHub：https://github.com/alsk1992/CloddsBot
> Skills 注册表：https://tessl.io/registry/skills/github/alsk1992/CloddsBot

---

**BLUF**：CloddsBot 是一个完全自主运行的开源 AI 交易 Agent，基于 Claude 驱动，无需人工干预就能在 Polymarket、Kalshi、Binance、Hyperliquid、Solana DEX、5 条 EVM 链等 1000+ 市场里扫描机会、下单执行、管理风险——还内置了「机器对机器支付协议」，让 Agent 之间可以直接结算，不经过人类审批。

---

## 这不只是交易机器人

过去几年出现了大量 DeFi 机器人，大多是脚本级别的自动化：策略写死、遇到异常停摆、换个市场就得重写。CloddsBot 走的是另一条路。

它的核心是 Claude 作为推理引擎——市场数据进来，Agent 判断机会、评估风险、决定仓位、执行交易。策略不是硬编码的规则集，而是由 LLM 在运行时做判断。

更关键的一点是它的 **Agent Commerce Protocol**：机器对机器（M2M）支付。这意味着 Agent 可以：
- 自主向数据供应商支付费用换取市场数据
- 和其他 Agent 协商并结算交易费用
- 在无人工审批的情况下完成完整的经济闭环

这是 Agent Economy 的基础设施原型，不只是"更聪明的脚本"。

## 覆盖范围：1000+ 市场，118+ 策略

**预测市场**：
- Polymarket、Kalshi、Manifold、Metaculus、PredictIt、Betfair、Smarkets
- 支持 BTC/ETH/SOL 的 5 分钟 / 15 分钟 / 1 小时 / 4 小时 / 日线二元期权

**现货和衍生品**：
- Binance、Bybit、Hyperliquid、MEXC、Drift 等 7 家交易所
- 最高 200x 杠杆（风险由 Agent 的止损策略控制）
- Solana DEX + 5 条 EVM 链（ETH、Polygon、ARB、Base、OP）

**内置策略（118+）**：
- 动量、均值回归、鲸鱼跟踪、DCA
- 期权到期衰减（Expiry Fade）、智能路由
- 跨市场套利、集群交易（Swarm Trading）

## 模块化 Skill 架构

CloddsBot 在 Tessl.io 的 Skills Registry 上注册了独立的技能包——`feeds`（数据源）、`smarkets`（博彩市场）、`markets`（市场数据）、`onchainkit`（链上操作）等都是可以单独安装、版本化、组合的 skill。

这个架构意味着：
- 社区可以开发并发布新 skill，不需要 fork 整个仓库
- 不同 Agent 可以共用同一套市场数据 skill
- skill 质量可以在 Registry 层面评分和筛选

这和软件工程里的包管理器是同一个逻辑，只是应用在 AI Agent 上。

## 自托管，Claude API 驱动

部署非常直接：

```bash
git clone https://github.com/alsk1992/CloddsBot.git
cd CloddsBot
npm install && cp .env.example .env
# 填入 ANTHROPIC_API_KEY
npm run build && npm start
```

启动后本地 WebChat 界面在 `http://localhost:18789/webchat`，无需第三方依赖。

支持的通信渠道包括 Telegram、Discord、Slack、WhatsApp、Teams、Matrix、Signal、iMessage、LINE、Nostr、Twitch——可以在任意渠道接收交易播报或发送指令。

## 为什么值得关注

不是每个人都会拿它去跑实盘（也不应该在没有充分测试前这么做）。但 CloddsBot 代表了一个值得记住的设计范式：

**Agent 作为经济主体**，不只是工具。它可以自主发现机会、做决策、执行、结算——全程没有人在中间做审批。M2M 支付协议是这个范式里最关键的一块：Agent 需要花钱买数据、支付手续费、和其他 Agent 协作，所有这些都在自动运转。

当 Agent 能自主管理资金流动时，「AI 助手」这个定位就不够用了。CloddsBot 是一个早期的、可以真实部署的 Agent Economy 节点。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: CloddsBot — Open Source AI trading agent
> GitHub: https://github.com/alsk1992/CloddsBot
> Skills Registry: https://tessl.io/registry/skills/github/alsk1992/CloddsBot

---

**BLUF**: CloddsBot is a fully autonomous open-source AI trading agent built on Claude. Without human intervention, it scans for opportunities, executes trades, and manages risk across 1000+ markets — Polymarket, Kalshi, Binance, Hyperliquid, Solana DEXs, and 5 EVM chains. It also ships with an Agent Commerce Protocol for machine-to-machine payments, letting agents settle transactions without human approval.

---

## More Than a Trading Bot

Most DeFi bots from the past few years are script-level automation: hardcoded strategies, crashing on edge cases, requiring a full rewrite for each new market. CloddsBot takes a different approach.

The core is Claude as the reasoning engine — market data comes in, the agent judges the opportunity, assesses risk, sizes the position, and executes. The strategy isn't a fixed ruleset; it's an LLM making runtime judgments.

The more important piece is the **Agent Commerce Protocol**: machine-to-machine (M2M) payments. This means the agent can:
- Autonomously pay data providers for market feeds
- Negotiate and settle transaction fees with other agents
- Complete a full economic loop without human sign-off

This is an infrastructure prototype for the Agent Economy — not just "a smarter script."

## Coverage: 1000+ Markets, 118+ Strategies

**Prediction markets**: Polymarket, Kalshi, Manifold, Metaculus, PredictIt, Betfair, Smarkets — binary options on BTC/ETH/SOL across 5-minute, 15-minute, hourly, 4-hour, and daily rounds.

**Spot and derivatives**: Binance, Bybit, Hyperliquid, MEXC, Drift, and more (7 exchanges), up to 200x leverage, Solana DEX + 5 EVM chains (ETH, Polygon, ARB, Base, OP).

**Built-in strategies (118+)**: momentum, mean reversion, whale tracking, DCA, expiry fade, smart routing, cross-market arbitrage, swarm trading.

## Modular Skill Architecture

CloddsBot registers independent skill packages on the Tessl.io Skills Registry — `feeds`, `smarkets`, `markets`, `onchainkit`, and others are installable, versionable, and composable modules.

This means the community can publish new skills without forking the entire repo, different agents can share the same market-data skill, and skill quality can be rated and filtered at the registry level. It's the package-manager logic applied to AI agents.

## Self-Hosted, Claude API-Driven

```bash
git clone https://github.com/alsk1992/CloddsBot.git
cd CloddsBot
npm install && cp .env.example .env
# add ANTHROPIC_API_KEY
npm run build && npm start
```

Local WebChat interface at `http://localhost:18789/webchat`, no third-party dependencies. Notification/command channels: Telegram, Discord, Slack, WhatsApp, Teams, Matrix, Signal, iMessage, LINE, Nostr, Twitch.

## Why This Matters

Not everyone will run it with real money (nor should they without thorough testing). But CloddsBot represents a design paradigm worth paying attention to.

**Agent as economic actor**, not just tool. It discovers opportunities autonomously, makes decisions, executes, and settles — no human in the approval loop. The M2M payment protocol is the critical piece: agents need to buy data, pay fees, and collaborate with other agents, all running automatically.

When an agent can autonomously manage cash flows, "AI assistant" is no longer the right frame. CloddsBot is an early, actually-deployable node in the Agent Economy.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
