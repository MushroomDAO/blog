---
title: "SuperPaymaster 部署运营指南：从 Sepolia 到主网的完整操作手册"
description: "SuperPaymaster v5.3.3-beta 引入了 UUPS 升级脚本、幂等部署工具链和三维度 audit-core 验证框架。本文是社区 Operator 和开发团队的完整部署参考：合约地址表、deploy-core 流程、Sepolia vs 主网差异、以及主网部署 Checklist。"
titleEn: "SuperPaymaster Deployment & Operations Guide: From Sepolia to Mainnet"
descriptionEn: "SuperPaymaster v5.3.3-beta introduces UUPS upgrade scripts, idempotent deploy toolchain, and a three-dimensional audit-core framework. Complete reference for community operators: contract addresses, deploy-core flow, Sepolia vs mainnet differences, and mainnet deployment checklist."
pubDate: 2026-06-12
category: "Tech-Experiment"
tags: ["SuperPaymaster", "部署指南", "Solidity", "UUPS", "Operator", "Foundry", "Sepolia", "AAStar", "开源"]
lang: "zh-CN"
heroImage: "../../assets/images/superpaymaster-v5.3.3-beta3-banner.png"
---

> 2026-06-12 · AAStar · 适用版本 v5.3.3-beta 及之后

本文是 SuperPaymaster 的运营参考文档，面向：
- 想为社区开启无 Gas 体验的 **Operator**
- 参与合约开发和测试的**贡献者**
- 规划主网部署的**团队成员**

SuperPaymaster 的功能介绍见 [主发布文章](/blog/superpaymaster-v5-3-3-beta3-gasless-infrastructure/)。

---

## 本次变更概览（v5.3.3-beta）

| 合约 | 变化 | 说明 |
|------|------|------|
| **SuperPaymaster** | UUPS 升级（新 impl） | H-1 债务路径修复；configureOperator 移除了 exchangeRate 参数 |
| **Registry** | UUPS 升级（新 impl） | 同步升级，proxy 地址不变 |
| **MicroPaymentChannel** | 首次部署 | 幂等部署 `0xbD1807328Dd654512B13d6320C9Cc78685a405Ed` |
| **xPNTsFactory** | 重新部署 | H-2 紧急停机路径修复，地址已变 |
| 其他合约 | 不动 | GToken / Staking / MySBT / BLSAggregator / DVTValidator 地址不变 |

**工具链变更**（影响所有后续发布）：
- 新增 `contracts/script/v3/UpgradeLive.s.sol`：幂等 UUPS 升级脚本，替代手动升级步骤
- `deploy-core` Phase 2 改为调用独立 `./audit-core` 脚本
- 新增 `audit-core`：三维度验证，per-check 幂等 stamp，RPC 自动重试

---

## Sepolia 当前部署状态

### v5.3.3-beta.3（2026-06-12，当前版本）

| 合约 | 地址 | 备注 |
|------|------|------|
| SuperPaymaster (proxy) | `0xFb090E82bD041C6e9787eDEbE1D3BE55b3c7266a` | ★ 代理不变 |
| SuperPaymaster (impl) | `0xEB2C9Cb434682FB1F3A6B3036358eA10C23Db981` | H-1 修复 |
| Registry (proxy) | `0xB5Fb8920F7AcD8b395934bd1F21222b32A30eF1A` | ★ 代理不变 |
| Registry (impl) | `0x1bd28f89DD80d3d413926C6Dfa0eEd0095E34001` | 同步升级 |
| **xPNTsFactory** | `0xc312CAFcb49dFe3aB76bFB2F3e37CaEdBa65ccd9` | **H-2 修复，地址已变** |
| MicroPaymentChannel | `0xbD1807328Dd654512B13d6320C9Cc78685a405Ed` | 不变 |
| GToken | `0x46B82966f8a40f0Bbb8C13aCfBA746631CC2ec72` | 不变 |
| GTokenStaking | `0x574820E26Acb7D9a1202708C6183d6A8aC957dA6` | 不变 |
| MySBT | `0x754CeB687aCFC72136B02a1cb7cE2F911B63F1f8` | 不变 |

### 历史版本（v5.3.3-beta.2，2026-05-29）

| 合约 | 地址 |
|------|------|
| SuperPaymaster (impl) | `0x8E2d93Bb9176b5796fFA91587BD2a755510C9819` |
| Registry (impl) | `0x24F262702A72Bc5E0255c0ed513b6a2021Ee1129` |
| xPNTsFactory | `0xC4f5A121c426734CC1c0DbE57f6A2Dd764E278e4` |

*最新地址以 [deployments/config.sepolia.json](https://github.com/AAStarCommunity/SuperPaymaster/blob/main/deployments/config.sepolia.json) 为准。*

---

## deploy-core 流程

从 v5.3.3-beta 起，所有部署统一通过 `deploy-core` 脚本：

```
./deploy-core <env> [--force] [--fresh-deploy]
        │
        ├─ Phase 1: 合约部署 / 升级
        │   ├─ anvil          → DeployAnvil.s.sol（每次全新）
        │   ├─ 有 registry proxy → UpgradeLive.s.sol（UUPS，保留链上状态）
        │   └─ 无 proxy / --fresh-deploy → DeployLive.s.sol（⚠️ 需确认）
        │
        ├─ Phase 2: ./audit-core <env> --force（三维度验证）
        │   ├─ A) Forge Script 功能检查（7 项）
        │   ├─ B) ABI 选择器对比（本地 ABI vs 链上 bytecode）
        │   └─ C) cast call 接口抽查（6 个关键函数）
        │
        └─ Phase 3: Etherscan 验证（仅 live 网络）
```

### UUPS 升级策略（v5.3.3-beta 起强制）

**任何对 SuperPaymaster 或 Registry 的修改，必须通过 `UpgradeLive.s.sol`，不得重新部署 proxy。**

```bash
# 日常升级（code hash 变了自动触发）
./deploy-core sepolia

# 强制重跑（hash 未变但需要手动执行）
./deploy-core sepolia --force

# ⚠️ 仅限全新网络首次部署（丢失链上状态，需确认）
./deploy-core <new-network> --fresh-deploy
```

---

## audit-core 三维度说明

### A — Forge Script 功能检查（7 项）

| Check | 验证内容 |
|-------|---------|
| `Check04_Registry` | Registry 版本、质押配置、MySBT 绑定、信用等级 |
| `Check01_GToken` | GToken 版本、供应量、owner |
| `Check02_GTokenStaking` | Staking 版本、总质押量 |
| `Check03_MySBT` | SBT 版本、oracle 绑定 |
| `Check07_SuperPaymaster` | SP 版本、EntryPoint 地址、价格预言机、Operator 配置 |
| `Check08_Wiring` | SP ↔ Registry 绑定、Agent Registry 配置 |
| `VerifyV3_1_1` | 跨合约整体验证（部署者 operator 余额等） |

### B — ABI 选择器对比

将本地 `abis/SuperPaymaster.json` 和 `abis/Registry.json` 的每个 public function 计算 4-byte selector，逐一核查链上 bytecode。

失败含义：链上部署的是旧版本，或本地 ABI 与实际部署存在漂移（ABI drift）。

### C — 接口抽查（cast call）

| 调用 | 期望 |
|------|------|
| `SP.version()` | 含 "SuperPaymaster" |
| `SP.entryPoint()` | 含 "0x00000000717" |
| `SP.paused()` | 不 revert |
| `Registry.version()` | 含 "Registry" |
| `Registry.owner()` | 不 revert |
| `MicroPaymentChannel.owner()` | 不 revert（若已部署） |

### 幂等机制

每项 check 有独立 stamp 文件（`deployments/.audit.<env>.<check>.stamp`），内容是 `registryImpl|spImpl|updateTime` 指纹。通过后立刻写 stamp，下次自动跳过；`--force` 清空所有 stamp，全量重跑。每项 check 最多重试 3 次（5s / 10s 退避），应对 RPC burst 限制。

---

## Sepolia vs 主网关键差异

### 签名方式

| 环境 | 方式 |
|------|------|
| Sepolia | `.env.sepolia` 中的 `PRIVATE_KEY`（测试网可接受） |
| 主网 | Foundry keystore（`cast wallet import` 加密导入），**绝对禁止明文私钥** |

### 主网禁止操作

| 操作 | 说明 |
|------|------|
| `./prepare-test <env>` | 注册测试账户，主网禁止 |
| `forge script RegisterEnduser.s.sol` | 测试用户注册，主网禁止 |
| `./deploy-core <env> --fresh-deploy` | 除非全新网络首次部署 |
| `.env.optimism` 含 `PRIVATE_KEY` | 明文私钥，严禁 |

### MicroPaymentChannel 所有权

- Sepolia：部署者 EOA 可接受
- 主网：**constructor 参数必须是多签合约地址**，或部署后立即 `transferOwnership(multisig)`

---

## 主网部署 Checklist

### 部署前

- [ ] `forge test` 全量通过（当前 968 项）
- [ ] Sepolia E2E 全绿（22 项）
- [ ] 合约字节数 < 24,576B（`forge inspect SuperPaymaster bytecode`）
- [ ] `abis/` 目录已更新最新 ABI（`./sync_to_sdk.sh` 或 `forge inspect`）
- [ ] `.env.optimism` 使用 Foundry keystore，无明文私钥
- [ ] `config.optimism.json` 中已存在 registry proxy 地址（UUPS 升级路径）
- [ ] 多签签名人就位（M-of-N 已在线）
- [ ] 测试账户私钥（`PRIVATE_KEY_ANNI` 等）不在 `.env.optimism` 中

### 部署

```bash
source .env.optimism
./deploy-core optimism
# 若需强制重新部署 impl（hash 未变）:
./deploy-core optimism --force
```

### 部署后手动确认

```bash
# 版本号验证
cast call $SP_PROXY  "version()(string)" --rpc-url $OPTIMISM_RPC_URL
cast call $REG_PROXY "version()(string)" --rpc-url $OPTIMISM_RPC_URL

# MicroPaymentChannel owner（若首次部署，需转给多签）
cast call $MC_ADDR "owner()(address)" --rpc-url $OPTIMISM_RPC_URL

# 若 owner 仍是 EOA，立即转移
cast send $MC_ADDR "transferOwnership(address)" $MULTISIG \
  --rpc-url $OPTIMISM_RPC_URL --account $DEPLOYER_ACCOUNT
```

---

## ERC-8004 AgentIdentityRegistry 地址

以下为 ERC-8004（Trustless Agents）三个注册合约的已知地址，已写入所有环境 config：

| 合约 | Sepolia | OP Mainnet |
|------|---------|------------|
| `agentIdentityRegistry` | `0x8004A818BFB912233c491871b3d84c89A494BD9e` | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| `agentReputationRegistry` | `0x8004B663056A597Dffe9eCcC1965A193B7388713` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| `agentValidationRegistry` | `0x8004Cb1BF31DAf7788923b405b754f57acEB4272` | `0x8004Cc8439f36fd5F9F049D9fF86523Df6dAAB58` |

---

**GitHub**: [AAStarCommunity/SuperPaymaster](https://github.com/AAStarCommunity/SuperPaymaster) · Apache 2.0

⚠️ 当前为 Sepolia 测试网 Beta，请勿用于主网真实资产。

<!--EN-->

## SuperPaymaster v5.3.3-beta: Launch Operations Guide

Reference document for community operators and contributors deploying SuperPaymaster.

### Key Changes in v5.3.3-beta

- **New `UpgradeLive.s.sol`**: Idempotent UUPS upgrade script — mandatory for all SP + Registry changes. Never re-deploy proxy.
- **`audit-core`**: Three-dimensional verification (forge checks + ABI selector diff + cast call spot checks), per-check idempotent stamps, 3-retry RPC handling
- **MicroPaymentChannel**: First deployment at `0xbD1807328Dd654512B13d6320C9Cc78685a405Ed`
- **xPNTsFactory**: Redeployed for H-2 fix, address changed

### Sepolia Deploy Flow

```bash
./deploy-core sepolia          # normal upgrade
./deploy-core sepolia --force  # force re-run (hash unchanged)
# --fresh-deploy only for brand new networks (destroys state)
```

### Mainnet Key Rules

- Use Foundry keystore (`cast wallet import`), never plain `PRIVATE_KEY` in `.env.mainnet`
- Never run `./prepare-test` or `RegisterEnduser.s.sol` on mainnet
- MicroPaymentChannel `owner` must be a multisig on mainnet — transfer immediately if deployed with EOA

### Current Sepolia Addresses (beta.3)

SuperPaymaster proxy: `0xFb090E82bD041C6e9787eDEbE1D3BE55b3c7266a`
Registry proxy: `0xB5Fb8920F7AcD8b395934bd1F21222b32A30eF1A`
xPNTsFactory: `0xc312CAFcb49dFe3aB76bFB2F3e37CaEdBa65ccd9` (H-2 fix, address changed)

Full address table: [deployments/config.sepolia.json](https://github.com/AAStarCommunity/SuperPaymaster/blob/main/deployments/config.sepolia.json)
