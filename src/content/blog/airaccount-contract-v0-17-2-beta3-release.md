---
title: "AirAccount 合约 v0.17.2-beta.3：代码质量与可观测性强化，679/0/0 Forge 测试全通"
description: "AirAccount 智能合约 beta.3 是一个纯内部质量版本——无行为变更，现有账户无需迁移。新增链上 VERSION 常量、AlgTierLib 单一来源、Factory custom errors 全面替换、ForceExit 安装加固、assembly popcount 优化，以及 8 个新测试路径。679/0/0 Forge，Sepolia E2E 全通。"
titleEn: "AirAccount Contract v0.17.2-beta.3: Code Quality & Observability — 679/0/0 Forge Tests"
descriptionEn: "AirAccount smart contract beta.3 is a pure internal quality release — no behavior changes, no migration needed. Adds on-chain VERSION constants, AlgTierLib single source of truth, Factory custom errors, ForceExit installation guard, assembly popcount optimization, and 8 new test paths. 679/0/0 Forge, Sepolia E2E all pass."
pubDate: 2026-06-12
category: "Progress-Report"
tags: ["AirAccount", "SmartContract", "Solidity", "ERC4337", "ERC7579", "WebAuthn", "SessionKey", "SocialRecovery", "Sepolia", "开源", "安全审计"]
lang: "zh-CN"
heroImage: "../../assets/images/airaccount-contract-v0.17.2-beta3-release.png"
---

> **TL;DR**：beta.3 是一个**纯内部质量版本**——无行为变更，现有账户无需迁移。
> 主要内容：链上版本检测常量、algId→tier 单一来源、factory 全面 custom errors、
> ForceExit 安装加固、assembly popcount 优化，以及 8 个新测试路径。
> 679 / 0 / 0 Forge，Sepolia E2E 全通。

---

## AirAccount 合约是什么

AirAccount 是 [Mycelium Protocol](https://www.mushroom.cv) 生态的**无密码智能账户合约层**。

核心特点：指纹/面部/PIN 即账户，无密码无助记词，私钥从不离开安全硬件。P-256 直接通过 EIP-7212 链上验证，符合 ERC-4337 v0.7 和 ERC-7579 模块化标准。

**GitHub**：[AAStarCommunity/airaccount-contract](https://github.com/AAStarCommunity/airaccount-contract) · Apache 2.0

---

## 8 大核心能力（v0.17.x 累积，beta.3 无变化）

| # | 能力 | 说明 |
|---|------|------|
| 1 | **WebAuthn / Passkey 登录** | 指纹/面部/PIN 即账户，无密码无助记词。P-256 EIP-7212 链上验证 |
| 2 | **Tiered 多签验证** | 单 WebAuthn（<$100）→ 双因子（<$1K）→ 多签共识（>$1K），链上强制金额上限 |
| 3 | **Session Key + Agent 系统** | 单一 `SessionKeyValidator` 同时支持 classic session 和 agent 模式 |
| 4 | **ERC-8004 Agent 经济** | 官方 Identity / Reputation / Validation registries + factory 白名单 |
| 5 | **Social Recovery（3-2-72h）** | 3 监护人，2-of-3 阈值，72 小时时间锁 |
| 6 | **ForceExit 紧急提取** | L2→L1 桥接提款，beta.3 新增：安装时拒绝不兼容账户 |
| 7 | **EIP-7702 EOA 升级** | 现有 EOA 一笔 type-4 tx 获得 AirAccount 全部能力 |
| 8 | **ERC-4337 v0.7 + ERC-7579 模块化** | 标准 paymaster 接口、validator/executor/hook 三类模块按需装卸 |

---

## beta.3 新增：代码质量 + 可观测性

### 🔢 VERSION 常量 — 链上版本检测

每个主要合约现在暴露一个 `string public constant VERSION`：

```solidity
await account.read.ACCOUNT_VERSION()            // → "0.17.2"
await factory.read.FACTORY_VERSION()            // → "0.17.2"
await forceExitModule.read.MODULE_VERSION()     // → "0.17.2"
await sessionKeyValidator.read.MODULE_VERSION() // → "0.17.2"
```

**为什么重要**：Sepolia 上同时存在 beta.1/beta.2/beta.3 地址。SDK 之前需要维护一张地址→版本映射表。现在可以直接问合约："你是哪个版本？"

ABI 影响：`abi/AAStarAirAccountV7.full.json` 更新至 **64 functions**（比 beta.2 多 1 个 `ACCOUNT_VERSION` getter）。

---

### 🏗 AlgTierLib — algId→tier 单一来源

```solidity
// src/utils/AlgTierLib.sol（新文件）
library AlgTierLib {
    function algTier(uint8 algId) internal pure returns (uint8) {
        if (algId == 0x05 || algId == 0x01) return 3;
        if (algId == 0x04) return 2;
        if (algId == 0x02 || algId == 0x03 || algId == 0x06 || algId == 0x08) return 1;
        return 0;
    }
}
```

**变化前**：`AAStarAirAccountBase` 和 `AAStarGlobalGuard` 各自独立实现 `_algTier()`，注释写着 "must stay in sync"。

**变化后**：两者都引用 `AlgTierLib`。增加新 algId？改一个文件，审计员也只需看一处。

gas 影响：`internal pure` library 是编译时内联，**零运行时开销**。

---

### 🚨 Factory custom errors — 全面替换 require(string)

`AAStarAirAccountFactoryV7` 的 15+ 个 `require(msg)` 全部替换为 typed custom errors：

```solidity
// ❌ 之前
require(_guardians.length >= 2, "Guardians required");

// ✅ 之后
if (_guardians.length < 2) revert GuardiansRequired();
```

新增 custom errors：`GuardiansRequired`、`GuardiansMustBeDistinct`、`DailyLimitRequired`、`AgentKeyRequired`、`TokenConfigLengthMismatch`、`DuplicateDefaultToken(address)` 等 16 个。

**SDK 升级提示**：如果你在 `catch` 里做字符串匹配，需要改为 selector 匹配：

```typescript
import { decodeErrorResult } from 'viem';
const err = decodeErrorResult({ abi: factoryAbi, data: e.data });
if (err.errorName === 'GuardiansRequired') { ... }
```

---

### 🛡 ForceExit 安装加固 — 拒绝不兼容账户

```solidity
function onInstall(bytes calldata data) external override {
    (bool ok, bytes memory ret) = msg.sender.staticcall(
        abi.encodeWithSignature("guardians(uint256)", uint256(0))
    );
    if (!ok || ret.length < 32) revert IncompatibleAccount();
    if (abi.decode(ret, (address)) == address(0)) revert IncompatibleAccount();
    _initialized[msg.sender] = true;
}
```

**修复的场景**：没有 `guardians()` getter 的合约，或 guardian 全零的合约安装 ForceExit 后变成"僵尸模块"——装进去但 approve 流程永远无法完成。beta.3 在安装时提前检测并 revert。

---

### ⚡ Assembly Popcount — 并行位运算

`_popcount()`（guardian 投票计数）和 `_countBits()`（ForceExit approve 计数）替换为标准 Hamming weight 汇编：

```solidity
function _popcount(uint256 x) internal pure returns (uint256 count) {
    assembly {
        x := sub(x, and(shr(1, x), 0x5555...))
        x := add(and(x, 0x3333...), and(shr(2, x), 0x3333...))
        x := and(add(x, shr(4, x)), 0x0f0f...)
        count := shr(248, mul(x, 0x0101...))
    }
}
```

3-guardian bitmap 约减少 **5-8x 操作码**，语义完全等价（已验证 0..255 范围全覆盖）。

---

### 🧪 新增 8 个测试路径

| 测试 | 验证点 |
|------|--------|
| `test_reentrancy_guard_preventsReentrancy` | Reentrancy guard 正常工作 |
| `test_modifyTierLimitsWithGuardians_replaySameNonce_reverts` | 同一 nonce 下旧签名不可重放 |
| `test_onInstall_incompatibleAccount_reverts` | 无 `guardians()` getter 的合约触发 `IncompatibleAccount` |
| `test_onInstall_zeroGuardian_reverts` | `guardians(0) == address(0)` 触发 `IncompatibleAccount` |
| `test_modifyTierLimits_deadlineExpired_reverts` | deadline 过期拒绝 |
| AlgTierLib 独立 5 测试 | 所有 algId 映射 + 边界值 |

---

## beta.2 → beta.3 升级指南

**合约层**：无行为变更，现有账户不受影响，无需迁移。4 个合约有新地址（重新部署带 VERSION 常量），其余 7 个合约地址不变。

| 合约 | 状态 |
|------|------|
| `AAStarAirAccountV7` (impl) | 新地址（ACCOUNT_VERSION） |
| `AAStarAirAccountFactoryV7` | 新地址（FACTORY_VERSION + custom errors） |
| `ForceExitModule` | 新地址（MODULE_VERSION + IncompatibleAccount） |
| `SessionKeyValidator` | 新地址（MODULE_VERSION） |
| 其余 7 个合约 | 地址不变 |

---

## Sepolia 地址

| 合约 | 地址 |
|------|------|
| AirAccount Factory | `0xfc6234bbd6283610659211347c6309904be86b0a` |
| AirAccount Impl (V7) | `0xe33EeCF21AAC2B776b49A4dd52BA8b7e683dE9C3` |
| ForceExitModule | `0xdb396ca2dc279f9bcb95fa3d8275f77c9f0c8702` |
| SessionKeyValidator | `0x655ca2e9a2d1178f7fbcea1856560d1e0c657ebf` |
| AAStarValidator (router) | `0x3c2b06f50300912794f29de031b33dd37bb8d6c6` |
| AgentRegistry | `0x9e8f576cad8a8f949181fd10d9ad1c49a7b0bc17` |

---

## 安全记录

本轮 Codex 对抗审计（第 4 轮）：
- **PR #73 — AlgTierLib + 5 tests**：✅ APPROVE
- **PR #85 — quick-wins**：✅ APPROVE

成绩单：Forge **679 / 0 / 0**，Sepolia E2E **79 / 79 PASS**

---

## v0.18 Roadmap

- **Emergency Asset Sweep**：多 ERC20 + 全 ETH 一键提取，L1+L2 都支持
- **ForceExit TOCTOU re-verify**：`executeForceExit` 再次验证 guardian freshness
- **Module install nonce**：防止模块 install/uninstall 操作重放
- **BLS/DVT binding fix**：mainnet 上线阻塞项

---

**Tag**：[v0.17.2-beta.3](https://github.com/AAStarCommunity/airaccount-contract/releases/tag/v0.17.2-beta.3) · Apache 2.0 · 🤝 Open source · 🌐 Public goods

<!--EN-->

## AirAccount Contract v0.17.2-beta.3

> A pure code quality release — no behavior changes, no migration required.

**GitHub**: [AAStarCommunity/airaccount-contract](https://github.com/AAStarCommunity/airaccount-contract)

### What's New

| Change | Impact |
|--------|--------|
| **VERSION constants** on all 4 contracts | SDK detects on-chain version directly — no address→version mapping table |
| **AlgTierLib** single source of truth | algId→tier logic in one file, zero runtime overhead (compiled inline) |
| **Factory custom errors** (16 new) | Replace `require(string)`, SDK must switch to selector matching |
| **ForceExit install guard** | Rejects incompatible accounts at install time, prevents zombie modules |
| **Assembly popcount** | ~5-8x fewer opcodes for guardian vote counting |
| **8 new test paths** | Reentrancy, replay protection, incompatible install, AlgTierLib boundaries |

### Test Results

- **Forge**: 679 / 0 / 0
- **Sepolia E2E**: 79 / 79 PASS
- **Codex adversarial audit (Round 4)**: All PRs ✅ APPROVED

### SDK Migration (beta.2 → beta.3)

```typescript
// Update ABI to 64 functions (was 63)
// Switch factory error handling to selector matching:
const err = decodeErrorResult({ abi: factoryAbi, data: e.data });
if (err.errorName === 'GuardiansRequired') { ... }

// Optional: verify on-chain version
const version = await publicClient.readContract({
    address: accountAddress,
    abi: accountAbi,
    functionName: 'ACCOUNT_VERSION'
}); // → "0.17.2"
```

**Tag**: [v0.17.2-beta.3](https://github.com/AAStarCommunity/airaccount-contract/releases/tag/v0.17.2-beta.3) · Apache 2.0
