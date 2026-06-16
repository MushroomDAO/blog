---
title: "Alchemy AgentPay 深度拆解：当 AI Agent 开始花钱，支付基础设施战争打响了"
description: "Alchemy 推出 AgentPay 开放测试版——一个协议无关的 AI Agent 支付代理层，同时支持 x402、ACP、MPP、A2P 四大主流协议。Morgan Stanley 预测 2030 年 AI 代理商务规模将达 3850 亿美元。这篇文章从 AI、Agent、账户三个维度深度拆解 AgentPay 的技术架构、产品定位和行业信号。"
titleEn: "Alchemy AgentPay Deep Dive: The Agent Commerce Infrastructure War Has Started"
descriptionEn: "Alchemy launches AgentPay open beta — a protocol-agnostic payment proxy for AI agents supporting x402, ACP, MPP, and A2P simultaneously. Morgan Stanley projects $385B in agentic commerce by 2030. A deep analysis from AI, Agent, and Account perspectives covering technical architecture, product positioning, and what industry practitioners need to know."
pubDate: 2026-06-15
category: "Research"
tags: ["AgentPay", "Alchemy", "AI Agent", "Web3", "支付", "x402", "AccountAbstraction", "Agent商务", "基础设施"]
lang: "zh-CN"
heroImage: "../../assets/images/alchemy-agentpay-agent-commerce-banner.png"
---

> 2026-06-15 · 技术研究

六个月内，Coinbase、Stripe、Google、Visa、Mastercard、Amex 先后宣布推出 AI Agent 支付基础设施。不是一家在做，而是所有人同时在做。这说明一件事：

**AI Agent 花钱的时代，已经到了。**

Alchemy 上周宣布 [AgentPay](https://agentpay.alchemy.com) 进入开放测试版。这是我见过定位最清晰的 Agent 支付产品——不是又一个协议，而是一个协议翻译层。这篇文章从 AI、Agent、账户三个维度把它拆开来看。

---

## 背景：为什么现在？

### Morgan Stanley 的预测

Morgan Stanley 预测 AI 代理商务（Agentic Commerce）到 2030 年将达到 **3850 亿美元**规模。

这个数字背后的逻辑：AI Agent 已经在真实环境里花钱了——调用付费 API、预订服务、购买计算资源。它们不是未来，它们是现在。

### 六个协议同时出现，这是问题

| 协议 | 发起方 | 机制 |
|------|--------|------|
| **x402** | Coinbase | HTTP 402 状态码 + 链上支付，无需订阅，按请求付费 |
| **ACP** | Stripe | Agent Commerce Protocol，面向 AI Agent 的商业交易标准 |
| **MPP** | Mastercard | 面向代理的支付协议，结合 Mastercard 信用网络 |
| **A2P** | Google | Agent-to-Pay，与 Google 支付生态和 Android 集成 |

多协议并存带来的直接问题：**商家面临碎片化**。

接入一个协议，就把使用其他协议的 Agent 排除在外；维护多套集成，成本极高且容易出错。Alchemy 看到了这个缝隙。

---

## AgentPay 是什么

一句话：**协议无关的 AI Agent 支付代理层（Protocol-Agnostic Payment Proxy）**。

它不是一个新的支付协议，而是坐在所有协议和商家 API 之间的翻译层。

```
AI Agent (使用任意协议: x402 / ACP / MPP / A2P)
         ↓
    AgentPay (检测协议 → 翻译)
         ↓
  商家 API (不需要改动，不需要新 SDK)
```

商家只需要注册一个端点、配置定价、获得一个代理 URL——无论哪个 Agent 用什么协议来调用，AgentPay 自动处理翻译。

---

## 技术架构拆解

### 核心设计：中间件，不碰钱

AgentPay 的技术定位有一个关键声明：

> **"AgentPay never holds funds and does not handle settlement or payment validation."**

这句话非常重要。它明确了产品边界：
- ✅ 协议检测和翻译
- ✅ 请求代理和路由
- ✅ 交易日志和协议分析
- ❌ 资金托管
- ❌ 结算处理
- ❌ 支付验证

这是一个聪明的架构选择：**把最复杂、最高风险的部分（资金流转）留给底层协议处理，自己只做路由层**。这样可以快速接入所有协议，同时规避监管和安全风险。

### 工作流程

**注册阶段（商家侧）**：
1. 注册 API 端点
2. 配置定价（按请求/按量）
3. 获得 AgentPay 代理 URL

**调用阶段（Agent 侧）**：
1. Agent 用自己支持的协议（x402/ACP/MPP/A2P）调用代理 URL
2. AgentPay 自动检测协议类型
3. 翻译并转发到商家原始 API
4. 返回结果，记录日志

**监控（商家侧）**：
- 仪表盘显示交易日志
- 按协议类型的流量分析

### 基础设施数据

Alchemy 的基础设施支撑着全球顶级 Web3 公司：

| 指标 | 数值 |
|------|------|
| 年链上交易量 | **$1T+** |
| 正常运行时间 | **99.995%** |
| 响应时间 | **< 50ms** |
| 合规认证 | **SOC 2 Type II** |
| 架构 | 多区域冗余 + 预测性扩容 |

客户包括：Robinhood、Stripe、Coinbase、Circle、Chainlink。

---

## 从 AI Agent 视角看：Agent 需要什么样的支付能力？

这是这篇分析最重要的部分。

### Agent 和人类付款的本质差异

| 维度 | 人类付款 | AI Agent 付款 |
|------|---------|-------------|
| **身份** | 有账户、有 KYC | 程序身份，无传统账户 |
| **授权** | 手动确认 | 自主决策，需策略控制 |
| **频率** | 低频大额 | 高频小额（按 API 调用）|
| **时机** | 人工触发 | 实时触发，无人值守 |
| **跨境** | 受限制 | 原生跨境（稳定币轨道）|
| **货币** | 法币 | 法币 + 稳定币 + 链上资产 |

AI Agent 的支付需求本质上是：**高频、自主、可编程、无摩擦**。这是信用卡网络和传统银行账户设计时完全没有考虑过的场景。

### x402 协议：最接近「HTTP Native 支付」的方案

x402 值得单独说一下，因为它的设计思路最接近开发者直觉。

HTTP 协议里有个 `402 Payment Required` 状态码，定义于 1996 年，但几十年来从未有人真正实现过。Coinbase 的 x402 协议把它真正用起来了：

```
Agent 发请求 → 服务器返回 402 + 支付信息 
→ Agent 完成链上支付 → 重新请求 → 服务器验证并响应
```

整个流程无需订阅账户，无需 API Key，按次付费，天然适合 Agent 场景。这也是为什么 Alchemy AgentPay 首先支持了 x402。

### Agent 支付的「账户」问题

这是我认为整个 Agent Commerce 生态目前最大的未解问题：

**AI Agent 的钱从哪来？**

几种可能的模型：
1. **用户委托**：Agent 代用户花钱，使用用户的钱包/账户，需要授权和限额
2. **Agent 自持**：Agent 有自己的链上账户（EOA 或 AA 账户），独立持有资金
3. **预付信用**：用户给 Agent 充值信用额度，Agent 在额度内自主使用
4. **即时结算**：每次 Agent 调用完毕，系统自动向用户账户结算

AgentPay 目前不回答这个问题（它说"不持有资金、不做结算"），但这个问题必须被某个层面的基础设施解决。

---

## 从 Web3 基础设施视角看：和 Account Abstraction 的关系

这是我认为 Mycelium 生态最需要关注的角度。

### ERC-4337 Account Abstraction 与 Agent 账户的天然契合

ERC-4337（Account Abstraction）的核心能力：
- **可编程授权**：智能合约控制的账户，可以设定支出策略
- **批量操作**：一笔交易执行多个操作
- **Gas 抽象**：用 ERC-20 Token 付 Gas，无需持有 ETH
- **社交恢复**：账户恢复不依赖私钥

这些能力和 Agent 支付需求高度重合：
- Agent 需要可编程授权 → AA 的 Session Key 机制
- Agent 需要高频小额 → AA 的批量操作降低成本
- Agent 不会管理 Gas → AA 的 Gas 抽象
- Agent 账户需要人类控制 → AA 的权限控制

SuperPaymaster（AAstar 生态）正在做的 Gas 赞助和 xPNTs 信用系统，是 Agent 支付基础设施里的 Gas 层解决方案。x402 等协议解决的是应用层，AA 解决的是账户层，两个层次不冲突，反而互补。

### Agent 支付的协议栈（我的理解）

```
应用层: x402 / ACP / MPP / A2P（商家接入协议）
       ↕  AgentPay 做协议翻译
路由层: AgentPay（协议聚合代理）
       ↕
账户层: AA 账户（ERC-4337）/ EOA / 托管账户
       ↕
Gas 层: SuperPaymaster / Paymaster（Gas 赞助）
       ↕
结算层: 稳定币 / 链上资产 / 法币通道
```

---

## 产品定位分析：Alchemy 为什么要做这个？

Alchemy 是 Web3 基础设施提供商，核心业务是 RPC 节点服务和开发者工具。做 AgentPay 对他们来说有战略意图：

### 1. 防御护城河

Alchemy 的竞争对手（Infura、QuickNode、Ankr）在 RPC 服务上差异越来越小。Agent 支付是一个新的战场，先建生态的人有网络效应优势。

### 2. 流量入口

AgentPay 是商家和 Agent 的连接器。如果商家的所有 Agent 流量都经过 Alchemy 的代理层，Alchemy 就获得了对整个 Agent 商务流量的可见性——这是极其有价值的数据资产。

### 3. 扩大 TAM

从「给开发者提供 RPC」扩展到「给所有商家提供 Agent 接入」，目标市场从 Web3 开发者扩展到所有 SaaS/API 提供商。

---

## 对行业从业者的 5 个关键信号

### 信号 1：「支付协议战争」已经开打

x402、ACP、MPP、A2P 四个协议都在争夺成为 AI Agent 支付的默认标准。历史上每次这种战争（HTTP vs Gopher、TCP/IP vs OSI），最终赢的标准往往是最开发者友好、最容易集成的那个，而不是功能最完整的那个。

**关注 x402**：它基于 HTTP 标准，最接近开发者直觉，Coinbase 生态背书，目前看来集成成本最低。

### 信号 2：「不持有资金」是正确的架构选择

AgentPay 明确声明不碰资金，只做路由。这不只是风险规避，更是正确的产品设计：支付基础设施的价值在于减少摩擦，持有资金会引入监管复杂度，让整个产品重心偏移。

**学习点**：构建 Agent 支付类产品时，找清楚自己在协议栈的哪一层，不要试图解决所有层的问题。

### 信号 3：Agent 支付和 Account Abstraction 必然融合

Agent 花钱需要账户，而普通 EOA 账户的私钥管理和权限控制完全不适合 Agent 场景。AA 账户（ERC-4337）天然适合成为 Agent 的链上账户——可编程授权、Gas 抽象、Session Key 机制。

**关注方向**：谁能做出「Agent 原生的 AA 账户」，谁就拿到了这个市场的账户层入口。

### 信号 4：稳定币是 Agent 支付的天然结算货币

法币跨境结算需要 3-5 天、手续费 2-5%、营业时间限制。AI Agent 的支付需要：即时、7x24、低手续费、可编程。稳定币（USDC、USDT）在链上满足全部条件。

不是「Web3 的稳定币」——是「AI Agent 的最优支付媒介」。

### 信号 5：监控 Alchemy AgentPay 的开放接口

AgentPay 目前是 Open Beta，接口和协议都还在演化。

**现在可以做的事**：
- 注册 [agentpay.alchemy.com](https://agentpay.alchemy.com) 测试账号
- 研究 x402 协议规范（[github.com/coinbase/x402](https://github.com/coinbase/x402)）
- 追踪 Alchemy 的开发者文档（[docs.alchemy.com](https://docs.alchemy.com)）

---

## 公开资源清单

| 资源 | 链接 | 说明 |
|------|------|------|
| AgentPay 入口 | [agentpay.alchemy.com](https://agentpay.alchemy.com) | 注册商家账号，Open Beta 免费 |
| Alchemy 文档 | [docs.alchemy.com](https://docs.alchemy.com) | 完整开发者文档 |
| x402 协议 | [github.com/coinbase/x402](https://github.com/coinbase/x402) | Coinbase 开源，HTTP 原生支付协议 |
| Alchemy SDK | [github.com/alchemyplatform/alchemy-sdk-js](https://github.com/alchemyplatform/alchemy-sdk-js) | JavaScript SDK |
| Stripe ACP | [stripe.com/docs/agents](https://stripe.com/docs/agents) | Stripe 的 Agent Commerce Protocol |

---

## 我的判断

AgentPay 是今年 Agent 基础设施里少有的「把具体问题解决好」的产品。它没有试图颠覆支付协议，而是认清楚了自己是翻译层，做了正确的减法。

但它还没回答最难的问题：**Agent 的身份和账户从哪来？**

当 Agent 调用 AgentPay 发起支付，谁来验证这个 Agent 的身份？谁来控制它的支出限额？当 Agent 越权消费，责任在谁？

这些问题不在 AgentPay 的范围里，但它们是整个 Agentic Commerce 生态里真正的基础设施空白。

从 Mycelium 协议和 AAstar 的视角看，这正是 Account Abstraction、AirAccount、SuperPaymaster 可以发挥价值的地方——不是在协议层竞争 x402，而是在**账户层、Gas 层、身份层**提供 Agent 原生的基础设施。

---

**相关链接**

- [AgentPay 官网](https://agentpay.alchemy.com) — 注册 Open Beta
- [x402 GitHub](https://github.com/coinbase/x402) — Coinbase 开源支付协议
- [Alchemy 开发者文档](https://docs.alchemy.com)
- [原文：Introducing AgentPay](https://www.alchemy.com/blog/agentpay-openbeta)

<!--EN-->

## Alchemy AgentPay: The Agent Commerce Infrastructure War Has Started

**Key Facts:**
- Alchemy launched AgentPay open beta — a protocol-agnostic payment proxy for AI agents
- Morgan Stanley projects agentic commerce will reach $385B by 2030
- 6 major players (Coinbase/x402, Stripe/ACP, Google/A2P, Mastercard/MPP, Visa, Amex) launched agent payment infrastructure simultaneously
- AgentPay bridges the fragmentation: one endpoint registration, supports all protocols

**Technical Architecture — The "Never Touch Money" Design:**

AgentPay is a middleware layer, not a payment processor:
- Detects incoming protocol (x402/ACP/MPP/A2P)
- Translates and proxies to merchant's unchanged API
- Provides dashboard with transaction logs and protocol breakdown
- **Explicitly does NOT hold funds, handle settlement, or validate payments**

This is the right architecture choice: take the routing complexity, leave the financial complexity to the underlying protocols.

**The x402 Protocol — HTTP-Native Payments:**

The HTTP spec has had a `402 Payment Required` status code since 1996, never implemented. Coinbase's x402 actually uses it: Agent requests → server returns 402 + payment info → Agent pays on-chain → re-requests → server validates. No subscriptions, no API keys, pure per-request billing. Most developer-friendly of the four protocols.

**The Unsolved Problem: Agent Identity and Accounts**

AgentPay deliberately sidesteps the hardest question: *Where does the Agent's money come from and who controls it?*

This is where ERC-4337 Account Abstraction fits:
- Programmable authorization (Session Keys for agents)
- Gas abstraction (agents don't manage ETH)
- Spending limits and policy enforcement
- Human oversight without private key management

The emerging Agent payment stack:
```
Application layer: x402/ACP/MPP/A2P
    ↕ AgentPay (protocol translation)
Routing layer: AgentPay
    ↕
Account layer: ERC-4337 AA accounts
    ↕
Gas layer: SuperPaymaster / Paymaster
    ↕
Settlement: Stablecoins / on-chain assets
```

**5 Key Signals for Practitioners:**
1. Watch x402 — it's HTTP-native, lowest integration cost, Coinbase-backed
2. "Don't touch money" is correct product architecture — find your layer, solve it well
3. AA accounts (ERC-4337) will converge with Agent payments — this is inevitable
4. Stablecoins are the natural settlement currency for agents — 24/7, instant, programmable
5. Register for AgentPay beta now, study x402 spec — this market is forming in real time

**Open Resources:**
- [agentpay.alchemy.com](https://agentpay.alchemy.com) — Open Beta registration
- [github.com/coinbase/x402](https://github.com/coinbase/x402) — Open source HTTP payment protocol
- [docs.alchemy.com](https://docs.alchemy.com) — Alchemy developer docs
