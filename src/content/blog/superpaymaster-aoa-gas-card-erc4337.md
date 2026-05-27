---
title: "SuperPaymaster：用链上资产抽象替代中心化签名服务，ERC-4337 Gas 代付去中心化的新路径"
titleEn: "SuperPaymaster: On-Chain Asset Abstraction That Removes the Centralized Signer from ERC-4337 Gas Sponsorship"
description: "来自 Mycelium 生态的 SuperPaymaster 论文发布在 arXiv。AOA 资产导向抽象用 Gas Card（灵魂绑定代币）替代中心化签名服务器，在 Optimism 主网实测中 L2 执行 Gas 比 Pimlico 低 49%，彻底移除了链下签名作为合法性关卡。"
descriptionEn: "SuperPaymaster, from the Mycelium ecosystem, is published on arXiv. Asset-Oriented Abstraction (AOA) replaces the centralized signing server with an on-chain Gas Card (Soulbound Token), achieving 49% lower L2 execution gas than Pimlico in Optimism Mainnet measurements while removing off-chain signing as a validity gate."
pubDate: "2026-05-27"
updatedDate: "2026-05-27"
category: "Research"
tags: ["ERC-4337", "Account Abstraction", "Paymaster", "去中心化", "Optimism", "Mycelium", "Web3", "Gas抽象"]
heroImage: "../../assets/banner-cypherpunk-revolution.jpg"
---

ERC-4337 账户抽象让用户不必持有 ETH 也能上链——Gas 由 Paymaster 代付。但几乎所有生产级 Paymaster 的核心都藏着一台中心化服务器：每笔赞助都要向它发请求、等它签名，它随时可以拒绝你的交易。SuperPaymaster 把这台服务器从链上合法性路径中彻底移除了。

> 📌 论文：SuperPaymaster: Eliminating Centralized Signer Authority via Asset-Oriented Abstraction to Reconcile Usability and Decentralization in Account Abstraction  
> 作者：Huifeng Jiao, Nathapon Udomlertsakul  
> arXiv:2605.05774 全文地址：https://arxiv.org/abs/2605.05774  
> PDF：https://arxiv.org/pdf/2605.05774  
> 56 页，13 个图表，Optimism 主网实测（n=50）

## 问题：流程导向抽象的结构性缺陷

论文将现有方案定义为**流程导向抽象（POA，Process-Oriented Abstraction）**：Paymaster 的赞助合法性取决于一个链下进程——中心化签名服务器。

这个架构有明显的结构性问题：

- **审查风险**：服务器可以基于任何标准拒绝签名，用户无申诉途径
- **单点故障**：服务器宕机 = 整个赞助系统瘫痪
- **权威集中**：声称去中心化的 Gas 抽象，实际上把关键决策权交给了链下实体
- **可组合性受限**：赞助有效性依赖链下状态，难以被其他合约或协议可预期地调用

Alchemy Gas Manager 和 Pimlico ERC-20 Paymaster 都属于这一类，也是本论文的对比基线。

## 解决方案：资产导向抽象与 Gas Card

SuperPaymaster 提出**资产导向抽象（AOA，Asset-Oriented Abstraction）**：将支付能力封装进一个用户持有的链上资产，而不是依赖链下签名流程。

这个链上资产叫做 **Gas Card**——一个灵魂绑定代币（Soulbound Token，SBT）。

核心思路的转变：

| | POA（现有方案） | AOA（SuperPaymaster） |
|--|-------------|-------------------|
| 合法性来源 | 链下签名服务器实时签名 | 链上 SBT 状态 + 确定性策略规则 |
| 赞助有效期 | 每笔交易临时授权 | 持久的用户资产 |
| 审查方 | 签名服务器运营者 | 无（规则在链上，不可篡改）|
| 故障点 | 链下服务器 | 无单点故障 |

`validatePaymasterUserOp` 只读取链上状态——这一点通过代码结构分析和链上主网证据同步验证。没有任何链下服务器介入合法性判断。

## Optimism 主网实测数据

研究方法：Design Science Research（DSR），在 Optimism 主网对三个系统各执行 50 笔单 UserOp ERC-20 转账，比较 Gas 消耗。

### L2 执行 Gas（txGasUsed）

| 系统 | txGasUsed | 对比 SuperPaymaster |
|------|-----------|-------------------|
| **SuperPaymaster** | **167,830** | — |
| Alchemy Gas Manager | 205,951 | +22.7%（SuperPaymaster 更低）|
| Pimlico ERC-20 | 328,937 | +95.9%（SuperPaymaster 更低）|

SuperPaymaster 比 Alchemy 低 18.5%，比 Pimlico 低 **49%**。

Pimlico 的高 Gas 来自链上代币清算逻辑——每次赞助都要在链上做 ERC-20 兑换。SuperPaymaster 改为内部余额更新，省掉了这部分开销。

### 总计费 Gas（txGasUsed + PVG）

| 系统 | 总计费 Gas |
|------|-----------|
| Alchemy Gas Manager | 257,299 |
| **SuperPaymaster** | **286,818** |
| Pimlico ERC-20 | — |

SuperPaymaster 总计费 Gas 比 Alchemy 高约 32,000，原因不在 Paymaster 架构，而在 Bundler 收取的 PVG（Pre-Verification Gas）更高。这是一个独立于赞助机制设计的开销，属于 Bundler 层的计费策略差异。

### 链上验证开销的来源

SuperPaymaster 相对 Alchemy 多出的 ~32,000 gas 来自链上验证本身：读取 SBT 状态、执行策略规则——这是 AOA 为了消除链下签名服务器而付出的代价，也是让赞助合法性完全可在链上审计的必要成本。

## 为什么这对账户抽象生态有意义

### 可组合性

因为赞助有效性由确定性链上规则决定，其他合约、协议、DAO 可以在构建时就对 Gas 赞助行为做出可靠预测——这在 POA 模式下是做不到的。

### GOMS 认知分析

论文还附带了一份 GOMS 认知负荷分析（Goals-Operators-Methods-Selection rules），对比了用户使用不同系统时的操作复杂度。AOA 的 Gas Card 持有模型在用户认知负荷上优于 POA——"持有资产"比"等待服务器授权"更符合用户对所有权的直觉。

### 局限

论文也诚实地指出了当前实现的局限：SuperPaymaster 的总计费 Gas 因 Bundler PVG 开销在某些场景下仍高于 Alchemy。这是 Bundler 层的商业和工程问题，与 Paymaster 架构设计无关，但对用户体验有实际影响。

## 与 Mycelium 生态的关系

SuperPaymaster 是 Mycelium Protocol 生态的核心基础设施之一，也是 PGL（Public Goods Layer）公约体系中链上角色注册和分账结算的底层依赖。这篇论文的发表，是对 SuperPaymaster 作为"无需链下签名"生产级 Paymaster 的学术级验证。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

ERC-4337 account abstraction lets users transact without holding ETH — a Paymaster covers the gas. But almost every production Paymaster hides a centralized server at its core: each sponsorship requires a real-time request and signature from that server, which can refuse your transaction at any time. SuperPaymaster removes that server from the validity path entirely.

> 📌 Paper: SuperPaymaster: Eliminating Centralized Signer Authority via Asset-Oriented Abstraction to Reconcile Usability and Decentralization in Account Abstraction  
> Authors: Huifeng Jiao, Nathapon Udomlertsakul  
> arXiv:2605.05774 full text: https://arxiv.org/abs/2605.05774  
> PDF: https://arxiv.org/pdf/2605.05774  
> 56 pages, 13 figures, Optimism Mainnet study (n=50 per system)

## The Problem: Structural Fragility of Process-Oriented Abstraction

The paper defines existing systems as **Process-Oriented Abstraction (POA)**: sponsorship validity depends on an off-chain process — a centralized signing server. Each UserOp must be routed to this server, which signs (or refuses) the sponsorship request.

The structural issues:

- **Censorship risk**: the server can reject transactions by any criteria, with no appeal path
- **Single point of failure**: server downtime = sponsorship system offline
- **Concentrated authority**: systems marketed as decentralized gas abstraction hand critical decisions to an off-chain entity
- **Limited composability**: off-chain state makes sponsorship validity hard for other contracts to reason about reliably

Alchemy Gas Manager and Pimlico ERC-20 Paymaster — the two baselines in this paper — both follow this pattern.

## The Solution: Asset-Oriented Abstraction and the Gas Card

SuperPaymaster proposes **Asset-Oriented Abstraction (AOA)**: payment capability is encapsulated in a user-owned on-chain asset rather than an off-chain signing process.

That asset is the **Gas Card** — a Soulbound Token (SBT).

The key shift:

| | POA (existing) | AOA (SuperPaymaster) |
|--|-------------|-------------------|
| Validity source | Real-time off-chain signing | On-chain SBT state + deterministic policy rules |
| Authorization lifetime | Per-transaction | Persistent user asset |
| Who can censor | Signing server operator | Nobody (rules are on-chain, immutable) |
| Failure point | Off-chain server | None |

`validatePaymasterUserOp` reads only on-chain state — confirmed via code structural analysis and Mainnet evidence. No off-chain server participates in validity determination.

## Optimism Mainnet Measurements

Methodology: Design Science Research (DSR). 50 single-UserOp ERC-20 transfers per system on Optimism Mainnet.

### L2 Execution Gas (txGasUsed)

| System | txGasUsed | vs. SuperPaymaster |
|--------|-----------|-------------------|
| **SuperPaymaster** | **167,830** | — |
| Alchemy Gas Manager | 205,951 | +22.7% higher |
| Pimlico ERC-20 | 328,937 | +95.9% higher |

SuperPaymaster is 18.5% lower than Alchemy and **49% lower than Pimlico** in pure L2 execution gas.

Pimlico's high gas comes from on-chain token liquidation logic — each sponsorship performs an ERC-20 swap on-chain. SuperPaymaster replaces this with an internal balance update, eliminating that overhead.

### Total Billed Gas (txGasUsed + PVG)

| System | Total Billed Gas |
|--------|-----------------|
| Alchemy Gas Manager | 257,299 |
| **SuperPaymaster** | **286,818** |

SuperPaymaster's total billed gas exceeds Alchemy by ~32,000. The cause is **not** paymaster architecture — it's higher bundler Pre-Verification Gas (PVG), a separate billing layer independent of the sponsorship mechanism.

### The On-Chain Verification Trade-Off

The ~32,000 gas overhead relative to Alchemy comes from on-chain verification itself: reading SBT state, executing policy rules. This is the cost of eliminating the off-chain signing server — the price of making sponsorship validity fully on-chain auditable.

## Why This Matters for the Account Abstraction Ecosystem

### Composability

Because sponsorship validity is determined by deterministic on-chain rules, other contracts, protocols, and DAOs can make reliable predictions about gas sponsorship behavior at build time — impossible under POA.

### GOMS Cognitive Analysis

The paper includes a GOMS (Goals-Operators-Methods-Selection rules) cognitive load analysis comparing user interaction complexity across systems. The Gas Card ownership model scores better than POA's server-authorization model — "owning an asset" matches user intuitions about control more closely than "waiting for server approval."

### Honest Limitations

The paper acknowledges that SuperPaymaster's total billed gas exceeds Alchemy in some scenarios due to bundler PVG overhead. This is a bundler-layer engineering and commercial issue, not a paymaster architecture issue — but it has real user experience implications.

## Connection to the Mycelium Ecosystem

SuperPaymaster is core infrastructure in the Mycelium Protocol ecosystem and the on-chain settlement layer for role registration and revenue distribution in the PGL (Public Goods Layer) charter system. This paper provides academic-grade validation of SuperPaymaster as a production-ready Paymaster that requires no off-chain signing server.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
