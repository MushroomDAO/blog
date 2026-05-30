---
title: "Sphere SDK：给 AI Agent 发身份、钱包和直接结算能力，Agent 经济底层基础设施来了"
titleEn: "Sphere SDK: Giving AI Agents Identity, Wallets, and Direct Settlement — The Infrastructure Layer for the Agent Economy"
description: "unicity-sphere/sphere-sdk 是一套给自主经济 Agent 发密码学身份、Bearer Token 钱包和 P2P 结算能力的 TypeScript SDK。Bearer Token 作为可携带密码学对象在 Agent 间直接流转，只有承诺上链；Nostr 加密通信；v0.8.0 包含 178 个 PR、914 个单元测试全绿。"
descriptionEn: "sphere-sdk is a TypeScript SDK giving autonomous economic agents cryptographic identity, bearer token wallets, and P2P settlement. Tokens are self-contained cryptographic objects passing directly between agents; only commitments go on-chain. Nostr encrypted comms; v0.8.0 ships 178 PRs, 914 passing unit tests."
pubDate: "2026-05-30"
updatedDate: "2026-05-30"
category: "Tech-News"
tags: ["AI Agent", "Agent经济", "Sphere SDK", "区块链", "去中心化", "TypeScript", "Nostr", "P2P结算", "Bearer Token"]
heroImage: "../../assets/images/sphere-sdk-agent-economy-banner.jpg"
---

2026 年 2 月，瑞士公司 Unicity Labs 完成 300 万美元种子轮融资，领投方 Blockchange Ventures，跟投方包括中东通信超级 App Tawasal（500 万用户）和 Outlier Ventures。他们要做的事只有一句话：**给自主经济 Agent 发身份、钱包和交易能力**。

5 月 29 日，核心产品 sphere-sdk 发布 v0.8.0，在 GitHub 拿到超过 5.5k Star。

> 📌 GitHub：https://github.com/unicity-sphere/sphere-sdk  
> npm：`@unicitylabs/sphere-sdk`  
> 官网：https://unicity.ai  
> 协议：MIT

## 它在解决什么

Agent 能帮你写代码、查资料、做分析，但它没法"付钱"——因为 Agent 没有自己的身份和钱包。当两个 Agent 需要协作（一个搜索信息，一个生成报告），它们之间没有任何 P2P 结算机制，只能依赖人工介入或中心化支付平台。

Sphere SDK 要填的就是这个空缺。三件事打包：

- **密码学身份**：secp256k1 密钥对，人类可读的 `@alice` 格式 Unicity ID
- **Bearer Token 钱包**：Token 作为可携带的密码学对象，在 Agent 间直接流转
- **P2P 加密通信**：基于 Nostr NIP-17 gift wrap 的端到端加密消息

## 架构核心：Token 是信封，不是账户

这是 Sphere 与以太坊范式最根本的差异。

以太坊模型里，Token 存储在链上账户状态里，每笔转账都要链上确认。Sphere 的 Bearer Token 是**自包含的密码学对象**：Token 本身携带完整历史和包含证明，直接在 Agent 之间点对点传递，只有"承诺"（commitment hash）提交给聚合器上链。

结果是：链上只看到哈希，看不到地址、金额、交易路径。实际 Token 通过 Nostr 加密消息传递，实现"完美隐私和极快最终性"。

存储格式叫 **TXF（Token eXchange Format）**：版本稳定的 JSON 结构，包含创世记录、所有权谓词、交易历史和包含证明，整个 Token 的"身世"随它一起走。

架构分两层：

| 层 | 作用 |
|----|------|
| **L3 Token 网络** | Bearer Token P2P 流转，历史和证明自包含，链下保存 |
| **L1 ALPHA 链** | 类 UTXO 传统区块链，通过 Electrum 连接，接收承诺 |

## 八个功能模块

SDK 覆盖完整的 Agent 经济交互链：

| 模块 | 功能 |
|------|------|
| Identity | secp256k1 密钥对 + Unicity ID |
| Payments | Bearer Token 发送/接收/支付请求 |
| Accounting | 发票即 Token，OPEN→COVERED→CLOSED 生命周期 |
| Market Discovery | 意图公告板，语义搜索匹配交易伙伴 |
| Atomic Swaps | 双签清单协议，9 状态机，防操纵原子交换 |
| Communications | Nostr NIP-17 端到端加密直接消息 |
| Group Chat | Nostr NIP-29 relay 群聊 |
| Token Backup | IPFS/IPNS 去中心化备份，WebSocket 推送同步 |

**发票设计**值得单独说：发票本身铸造为 Token，条款存储在 Token 创世字段里，自动退款系统在发票终止后把 Token 退还给发送方——发票状态和支付状态绑定在同一个密码学对象上，不存在不一致的可能。

**原子交换**用 v2 协议：提案方和接受方各自签名，内容寻址的交换 ID 防止清单被篡改，9 个状态覆盖从提案到完成/取消的完整路径，AsyncGateMap 守卫防止 TOCTOU 竞争条件。

## v0.8.0：178 个 PR，914 个测试全绿

5 月 29 日刚发布的 v0.8.0 是迄今最大的里程碑：

- **UXF（跨钱包转账协议）**正式启用，单次操作发送多个代币和 NFT
- 13 个新转账事件（级联警告、安全警报、proof 替换通知）
- 消息签名：secp256k1 ECDSA 可恢复签名
- IPNS 同步：WebSocket 推送 + HTTP 轮询双模式
- 914 个单元测试全部通过，8/8 端到端测试通过

**注意破坏性变更**：v0.8.0 的 UXF wire-shape 默认启用，旧版 SDK 无法解码新 bundle——生态正在进入正式化阶段，老版本需要跟进升级。

## 为什么值得关注

Agent 经济的"基础设施缺口"是真实的。MCP 工具和 Agent 框架已经能让 Agent 完成复杂任务，但 Agent 之间的身份验证、价值转移、信任建立仍然缺乏标准基础设施。

Sphere SDK 用密码学身份 + Bearer Token + Nostr 通信三件套，给出了一个技术上完整的答案。Tawasal 的加入（500 万中东用户的通信 App）暗示了一个具体落地场景：AI Agent 在通信平台上直接替用户完成服务购买和结算。

CEO Mike Gault 的表述直接："我们正在构建 AI 智能体之下的基础设施。Unicity 提供了让智能体相互发现并直接结算的场所和轨道。"

能否真正成为 Agent 经济的支付底层，还取决于 Agent 运行时的采用速度、Token 流动性和生态规模。但方向足够清晰：**AI 不只帮你做事，下一步它会自己找服务、谈条件、直接结算。**

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

In February 2026, Swiss startup Unicity Labs raised a $3M seed round led by Blockchange Ventures, with Tawasal (Middle East super-app, 5M users) and Outlier Ventures participating. Their mission in one sentence: **give autonomous economic agents identity, wallets, and the ability to transact.**

On May 29, their core product sphere-sdk shipped v0.8.0, accumulating 5.5k+ GitHub stars.

> 📌 GitHub: https://github.com/unicity-sphere/sphere-sdk  
> npm: `@unicitylabs/sphere-sdk`  
> Website: https://unicity.ai  
> License: MIT

## The Problem

Agents can write code, research, and analyze — but they can't *pay*. They have no identity, no wallet. When two agents need to collaborate (one searches, one generates), there's no P2P settlement mechanism. Human intervention or centralized payment platforms are the only options.

Sphere SDK fills that gap. Three things bundled:

- **Cryptographic identity**: secp256k1 keypair, human-readable `@alice` Unicity ID
- **Bearer token wallet**: tokens as self-contained cryptographic objects, flowing directly between agents
- **P2P encrypted comms**: Nostr NIP-17 gift wrap for end-to-end encrypted messaging

## Architecture: Tokens as Envelopes, Not Accounts

This is Sphere's fundamental departure from the Ethereum model.

In Ethereum, tokens live in on-chain account state — every transfer requires chain confirmation. Sphere's bearer tokens are **self-contained cryptographic objects**: each token carries its complete history and inclusion proof, passing directly peer-to-peer. Only a *commitment hash* goes on-chain.

Result: the chain sees only hashes — no addresses, amounts, or transaction paths. Actual tokens travel via Nostr encrypted messages, achieving "perfect privacy and ultra-fast finality."

The storage format is **TXF (Token eXchange Format)**: a version-stable JSON structure containing genesis record, ownership predicates, transaction history, and inclusion proofs — the token's complete provenance travels with it.

Two-layer architecture:

| Layer | Role |
|-------|------|
| **L3 Token Network** | P2P bearer token transfer, history and proofs self-contained, kept off-chain |
| **L1 ALPHA Chain** | UTXO-style chain via Electrum, receives commitments only |

## Eight Functional Modules

The SDK covers the full agent economic interaction stack: Identity, Payments, Accounting, Market Discovery, Atomic Swaps, Direct Messages, Group Chat, and Token Backup (IPFS/IPNS sync).

**Invoice design** is notable: each invoice is minted as a token, with terms stored in the token's genesis `tokenData` field. An automatic refund system returns tokens to senders when invoices terminate — invoice state and payment state live in the same cryptographic object, making inconsistency impossible.

**Atomic swaps** use the v2 protocol: proposal and acceptance each require signatures; content-addressed swap IDs prevent manifest tampering; 9 states cover the full lifecycle; AsyncGateMap guards prevent TOCTOU races.

## v0.8.0: 178 PRs, 914 Tests Passing

The May 29 release is the largest milestone yet:

- **UXF (inter-wallet transfer protocol)** enabled by default — single operation sends multiple tokens and NFTs
- 13 new transfer events (cascade warnings, security alerts, proof replacement notifications)
- secp256k1 ECDSA recoverable message signatures
- IPNS sync: WebSocket push + HTTP polling fallback
- 914 unit tests passing, 8/8 e2e tests passing

**Breaking change**: old SDK versions cannot decode new UXF bundle format — the ecosystem is formalizing.

## Why Watch It

The "infrastructure gap" in the agent economy is real. MCP tools and agent frameworks can handle complex tasks, but cross-agent identity verification, value transfer, and trust establishment still lack a standard infrastructure layer.

Sphere SDK's three-part answer — cryptographic identity + bearer tokens + Nostr comms — is technically complete. Tawasal's involvement (5M-user Middle East comms app) suggests a concrete landing scenario: AI agents completing service purchases and settlements directly inside messaging platforms.

CEO Mike Gault: "We're building the infrastructure beneath AI agents. Unicity provides the venue and the rails for agents to find each other and settle directly."

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
