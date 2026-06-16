---
title: "SuperPaymaster v5.3.3-beta.3：首次公开发布——让用户永远不用操心 Gas 费"
description: "SuperPaymaster 是 AAStar 生态的去中心化 Gas 赞助基础设施。社区运营者用自己的 xPNTs 代币为用户代付链上 Gas，用户无需持有 ETH。人类与 AI Agent 双通道赞助，8 项安全审计修复，968 条测试全绿，Sepolia 首次公开发布。"
titleEn: "SuperPaymaster v5.3.3-beta.3: First Public Release — Users Never Need to Think About Gas"
descriptionEn: "SuperPaymaster is AAStar's decentralized gas sponsorship infrastructure. Community operators use xPNTs tokens to pay gas on behalf of users — no ETH required. Human + AI agent dual-channel sponsorship, 8 audit fixes, 968 tests passing. First public release on Sepolia."
pubDate: 2026-06-12
category: "Progress-Report"
tags: ["SuperPaymaster", "AccountAbstraction", "GaslessUX", "AAStar", "xPNTs", "AIAgent", "开源", "Sepolia", "智能合约"]
lang: "zh-CN"
heroImage: "../../assets/images/superpaymaster-v5.3.3-beta3-banner.png"
---

> 2026-06-12 · AAStar · Mycelium Protocol

Gas 费是 Web3 最大的使用摩擦。

用户点击一个按钮，系统要求他们持有 ETH、理解 gas price、手动确认——这对普通人来说几乎是劝退设计。

**SuperPaymaster 的目标是让这个问题消失。** 不是绕开它，而是从根本上解决：社区运营者维护一个 Gas 资金池，用社区自己的代币为用户代付，用户完全不感知 ETH 的存在。这是 [AAStar](https://github.com/AAStarCommunity/SuperPaymaster) 账户抽象技术栈的 Gas 结算层，今天正式在 Sepolia 测试网首次公开发布。

---

## 它是怎么工作的

三个角色，各司其职：

```
用户
  → 发起链上操作（无需 ETH）
      ↓
社区 Operator
  → 维护 xPNTs 代币池，为用户代付 Gas
      ↓
SuperPaymaster
  → 自动识别用户身份，链上完成 Gas 结算
```

用户持有的是社区代币（xPNTs），不是 ETH。SuperPaymaster 在后台完成 ETH 的实际支付，用 xPNTs 记账。整个过程对用户透明。

这不是单个合约，而是一套可组合的基础设施：

| 核心组件 | 作用 |
|---------|------|
| **SuperPaymaster（AOA+）** | 多社区共享 Gas 赞助层，Registry 统一管理注册与信誉 |
| **PaymasterV4（AOA）** | 每社区独立部署，通过最小代理工厂创建，完全自主运营 |
| **Registry** | 社区注册、质押、声誉数据，两种模式共享 |
| **xPNTs / xPNTsFactory** | 每个社区部署自己的社区 Gas 代币 |
| **MicroPaymentChannel** | 链下微支付通道，降低 AI Agent 支付的链上频率 |
| **BLSAggregator + DVTValidator** | 分布式签名聚合与罚没执行 |

---

## 六个核心能力

### 1. 用户完全无 Gas

用户发起操作，系统自动检查：是否持有 SBT（社区成员身份令牌），是否在信用额度内，xPNTs 余额是否足够。满足条件，Gas 自动代付——用户看不到任何 ETH 操作。

### 2. 信用 / 债务系统

xPNTs 余额不足时，SuperPaymaster 临时垫付并记录债务。用户余额恢复后自动还款。

有保障机制：每个用户有信用上限，超过上限自动封锁账户。**封锁只能由 DVT/BLS 分布式共识网络解除，不受合约管理员控制**——这是去中心化的关键设计。

### 3. 人类 + AI Agent 双通道赞助

SuperPaymaster 支持两类"用户"：

- **人类用户**：持有 MySBT（灵魂绑定代币）的社区成员
- **AI Agent**：在 AgentIdentityRegistry 注册的自主 AI 代理

运营者可以为 AI Agent 单独配置赞助策略——按费率比例 + 每日上限组合控制，Agent 的每笔操作都可追溯。

这是 Web3 里 AI Agent 经济的 **Gas 基础层原语**。当 AI Agent 自主发起链上交易时，它需要 Gas；SuperPaymaster 提供了一套标准化的方式来赞助和追踪这些操作。

### 4. x402 微支付结算

x402 是一种让 HTTP API 直接处理链上支付的协议。SuperPaymaster 集成了两条结算路径：
- **USDC 通道**：通过授权签名结算，省约 19% gas
- **xPNTs 通道**：直接转账，社区内快速结算

配合 MicroPaymentChannel，AI Agent 与 Web 服务之间的高频微支付可以先在链下积累，定期批量上链结算。

### 5. 两种部署模式，覆盖不同规模需求

小社区可以直接接入 SuperPaymaster 共享基础设施（AOA+ 模式），不需要自己运维；大社区可以通过工厂合约部署独立 Paymaster（AOA V4 模式），完全控制自己的 Gas 池和策略。

两种模式共用 Registry，数据互通。

### 6. DVT / BLS 两层安全

当运营者出现恶意行为，两层罚没机制依次触发：
- 第一层：罚没运营资金（aPNTs）
- 第二层：罚没治理质押（GToken）

罚没需要多个 DVT 验证节点的 BLS 聚合签名才能执行，不可被单方面操控。

---

## beta.3 修复了什么

这次公开发布是在 beta.2（2026-05-29）的基础上叠加了 2 项 High 级安全修复，共计修复 8 项审计发现：

**H-1：信用额度绕过漏洞（debt-fallback 路径）**

场景：用户在操作执行中途清空 xPNTs，导致 Gas 结算触发 fallback 路径。旧版本的 fallback 路径未检查信用上限，攻击者可借此让运营者积累无限债务。

修复：fallback 路径现在强制验证"现有债务 + 待处理债务 + 本次账单"不得超过信用上限，超限立即封锁，仅分布式网络可解封。

**H-2：xPNTs 紧急停机绕过漏洞（transferFrom 快速路径）**

场景：社区可以触发 `emergencyDisabled` 一键停止所有代币流动。但 `transferFrom` 中有一条"自拉取"快速路径（`to == msg.sender`），跳过了紧急开关检查，攻击者在停机期间仍可转移代币。

修复：自拉取路径现在强制走完整的 emergencyDisabled + 每日限额检查，没有例外。

---

## 成绩单

| 指标 | 结果 |
|------|------|
| Forge 单元测试 | **968 通过 / 0 失败 / 0 跳过** |
| echidna fuzz 不变量 | **4 项全通过** |
| 累计安全修复 | **8 项**（beta.2: 2 Critical + 4 High · beta.3: 2 High） |
| Codex 独立审计 | **全 PR 批准** |
| 主网兼容性 | ⚠️ 当前仅 Sepolia 测试网 |

---

## 合约地址（Sepolia）

| 合约 | 地址 |
|------|------|
| SuperPaymaster (proxy) | `0xFb090E82bD041C6e9787eDEbE1D3BE55b3c7266a` |
| Registry (proxy) | `0xB5Fb8920F7AcD8b395934bd1F21222b32A30eF1A` |
| xPNTsFactory | `0xc312CAFcb49dFe3aB76bFB2F3e37CaEdBa65ccd9` |
| PaymasterFactory (V4) | `0x60B8f728Abca14B82a4EC72f00Ff5437e0702e90` |
| MicroPaymentChannel | `0xbD1807328Dd654512B13d6320C9Cc78685a405Ed` |
| GToken | `0x46B82966f8a40f0Bbb8C13aCfBA746631CC2ec72` |
| GTokenStaking | `0x574820E26Acb7D9a1202708C6183d6A8aC957dA6` |
| MySBT | `0x754CeB687aCFC72136B02a1cb7cE2F911B63F1f8` |
| BLSAggregator | `0x7ec72505220a13040c80EF2B895Bf3405b6ed3e9` |
| DVTValidator | `0xB60C82158734def92D0d2163C93927cf19b86a95` |

*最新地址以 [deployments/config.sepolia.json](https://github.com/AAStarCommunity/SuperPaymaster/blob/main/deployments/config.sepolia.json) 为准。*

---

## AAStar 完整技术栈

SuperPaymaster 是账户抽象三层架构的中间层：

```
用户 / AI Agent
      ↓
AirAccount（账户层）
— Passkey 登录 · Session Key · Social Recovery · Agent 支持
      ↓
SuperPaymaster（Gas 层）   ← 本项目
— xPNTs 赞助 · 信用系统 · x402 · DVT 安全
      ↓
EntryPoint（ERC-4337 标准层）
      ↓
Ethereum / OP Mainnet
```

配套 SDK（`aastar-sdk`）提供三组操作模块：`x402Actions`、`agentActions`、`channelActions`，覆盖完整的 gasless UserOp 构建流程。

---

## 下一步

| 里程碑 | 内容 |
|--------|------|
| **v5.4**（下一 beta）| 信用内核升级、中低级审计修复、x402 Facilitator 拆分 |
| **v6.0**（主网候选）| 外部审计完成 · 主网部署 · 多签治理移交 |

---

## 如果你想参与

**社区 Operator 接入**（5 步开启无 Gas 体验）：
1. 在 Registry 注册社区（需质押 GToken）
2. 通过 xPNTsFactory 部署社区代币
3. 配置 Operator（设置代币地址和资金池地址）
4. 向 SuperPaymaster 存入 xPNTs
5. 用户持有 MySBT，发起的操作自动享受 Gas 赞助

详见 [GitHub Release v5.3.3-beta.3](https://github.com/AAStarCommunity/SuperPaymaster/releases/tag/v5.3.3-beta.3) · [完整审计报告](https://github.com/AAStarCommunity/SuperPaymaster/blob/main/docs/audit/comprehensive-audit-2026-06-11.md)

---

⚠️ **当前为 Sepolia 测试网 Beta，请勿用于主网真实资产。**

🤝 Open source · Apache 2.0 · 🌐 Digital Public Goods

<!--EN-->

## SuperPaymaster v5.3.3-beta.3: First Public Release

Gas fees are the biggest usability friction in Web3. SuperPaymaster eliminates it at the infrastructure layer: community operators maintain xPNTs token pools and pay gas on behalf of users. Users never touch ETH.

### Architecture

```
User → sends UserOperation (no ETH needed)
    ↓
Community Operator → maintains xPNTs pool
    ↓
SuperPaymaster → auto-identifies user, settles gas on-chain
```

### 6 Core Capabilities

- **Gasless UX**: MySBT-verified users get gas sponsored automatically
- **Credit/Debt System**: Temporary credit when xPNTs run low; overlimit = auto-block, unlock via DVT/BLS consensus only
- **Dual-channel (Human + AI Agent)**: SBT holders and ERC-8004 registered AI agents both qualify; per-agent tiered policies
- **x402 Micropayment Settlement**: USDC path (19% gas saved) + xPNTs direct path; MicroPaymentChannel for off-chain batching
- **Two Deployment Modes**: AOA+ (shared multi-community) or AOA V4 (independent per-community via minimal proxy factory)
- **DVT / BLS Security**: Two-tier slashing (operational + governance stake); requires BLS aggregated signatures to execute

### beta.3 Security Fixes

- **H-1**: Credit ceiling bypass in debt-fallback path — now enforces `existingDebt + pendingDebts + bill ≤ creditLimit`
- **H-2**: xPNTs emergency switch bypass in `transferFrom` fast path — self-pull path now always checks `emergencyDisabled` + daily rate limit

### Numbers

- Forge: **968 / 0 / 0** · echidna: 4 invariants passing
- Cumulative audit fixes: **8** (beta.2: 2C + 4H · beta.3: 2H)
- Status: Sepolia testnet only — not for mainnet

**Release**: [v5.3.3-beta.3](https://github.com/AAStarCommunity/SuperPaymaster/releases/tag/v5.3.3-beta.3) · Apache 2.0
