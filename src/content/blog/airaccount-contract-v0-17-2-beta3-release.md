---
title: "AirAccount 合约 v0.17.2-beta.3：把地基打扎实，为主网做准备"
description: "beta.3 不加新功能，只做一件事：把代码底座整理干净。链上版本自检、消除重复逻辑、错误信息更友好、安全防护更严、测试覆盖更全——679 条 Forge 测试，零失败。这是一个团队认真对待未来的信号。"
titleEn: "AirAccount Contract v0.17.2-beta.3: Solidifying the Foundation for Mainnet"
descriptionEn: "beta.3 adds no new features — it does one thing: cleans up the code foundation. On-chain version detection, eliminating duplicate logic, better error messages, stricter security guards, and broader test coverage. 679 Forge tests, zero failures. A signal that the team takes long-term seriously."
pubDate: 2026-06-12
category: "Progress-Report"
tags: ["AirAccount", "SmartContract", "WebAuthn", "Passkey", "无密码登录", "智能钱包", "开源", "Sepolia"]
lang: "zh-CN"
heroImage: "../../assets/images/airaccount-contract-v0.17.2-beta3-release.png"
---

> 2026-06-12 · AAStar · Mycelium Protocol

有些版本是添砖加瓦，有些版本是重新检查地基。

**beta.3 是后者。**

它不增加任何用户可感知的新功能——现有账户无需迁移，行为完全不变。它做的事情是：找到代码里藏着的结构性问题，在它们有机会变成 bug 之前把它们修掉。

---

## AirAccount 是什么

AirAccount 是 [Mycelium Protocol](https://www.mushroom.cv) 生态的**无密码智能账户合约**。

用一句话说：用指纹/面部识别/PIN 就能控制一个链上账户，不需要助记词，不需要管私钥。私钥从不离开安全硬件。这是一套在真实硬件上经过验证的账户体系，目前部署在 Sepolia 测试网。

它有 8 个核心能力，beta.3 完整保留，没有任何变化：

| 能力 | 简单说 |
|------|--------|
| **WebAuthn / Passkey 登录** | 指纹/面部/PIN 即账户，私钥链上验证 |
| **分级多签验证** | 小额单人确认，大额需要多重保障，金额上限写进合约 |
| **Session Key + Agent** | 给 AI Agent 授权一段时间内代你操作 |
| **Agent 经济系统** | 链上 agent 身份与信誉注册 |
| **Social Recovery** | 3 个监护人，2-of-3 阈值，72 小时时间锁找回账户 |
| **ForceExit 紧急提取** | 极端情况下从 L2 提款到 L1 |
| **EOA 账户升级** | 已有的普通钱包地址，一笔交易获得全部智能账户能力 |
| **模块化标准** | 遵循 ERC-4337 + ERC-7579，可按需插拔功能模块 |

---

## beta.3 做了什么

### 合约现在会"自报家门"了

以前，如果你想知道某个链上地址运行的是哪个版本的 AirAccount，只能靠外部维护一张"地址→版本"的对照表。这张表一旦漏更新，就会出问题。

现在每个合约都有一个 `VERSION` 常量，可以直接读取：

```
account.ACCOUNT_VERSION()  →  "0.17.2"
factory.FACTORY_VERSION()  →  "0.17.2"
```

就像给每个合约挂了一块名牌——不用猜，问它自己。

---

### 一个"必须保持同步"的注释，被彻底消灭了

在 beta.3 之前，代码里有一处注释写着 **"must stay in sync"**——意思是有两个地方做同一件事（把算法 ID 转换成安全等级），如果改了一个忘了改另一个，就会出现安全漏洞。

这种"靠人记住"的约定是代码债务，也是审计员的噩梦。

beta.3 把这段逻辑提取成了独立的工具库 `AlgTierLib`，两处都引用同一份代码。**改一个地方，全部自动同步。** 而且是编译时内联，不增加任何运行时开销。

---

### 报错信息从"天书"变成了"说人话"

当一笔交易因为参数错误被拒绝，智能合约会返回一个错误原因。

旧的方式是一段字符串，比如 `"Guardians required"`——简单粗暴，但存储这段文字本身就要消耗 gas，而且 SDK 开发者只能做字符串匹配，脆弱易碎。

新的方式是 **typed custom errors**：每种错误都有自己的类型，比如 `GuardiansRequired`、`DuplicateDefaultToken`，不存储文字，gas 更少，SDK 也能做精准的类型匹配。

beta.3 在 Factory 合约里替换了 15+ 个旧式报错，新增 16 种具名错误类型。

**如果你在集成 SDK**，`catch` 块里用字符串匹配错误信息的代码需要更新为类型匹配——这是本版本唯一需要 SDK 开发者注意的变化。

---

### 一个"装上就坏"的场景，在安装时被拦下了

ForceExit 是 AirAccount 的紧急提款模块。但在 beta.3 之前，存在一个边缘情况：

如果一个不符合规范的合约（比如没有 `guardians()` 函数，或者 guardian 全是零地址）安装了 ForceExit 模块，这个模块会变成"僵尸"——装进去了，但 approve 流程永远无法走完，账户卡死。

现在 `onInstall` 会在安装时检查兼容性，不符合条件直接拒绝，返回 `IncompatibleAccount` 错误。**装之前先验，而不是装完再发现问题。**

---

### 计算 guardian 投票数的代码，快了 5-8 倍

Social Recovery 和 ForceExit 都需要统计"有多少个 guardian 已经投票同意"。这个计数操作看起来微小，但它在每次验证时都会执行。

beta.3 把这个操作改成了一种叫做 "Hamming weight"（汉明重量）的并行位运算——一次计算同时处理多个位，操作码约减少 5-8 倍。结果完全等价，已在所有可能的输入上验证过。

---

### 8 条新测试，填上了之前没有明确覆盖的场景

测试不只是"功能能跑通"，更重要的是"边界情况和安全假设被明确验证"。

beta.3 新增的 8 个测试路径包括：
- **重入攻击**：验证重入防护在刻意构造的攻击场景下确实生效
- **签名重放**：同一个 nonce 下，旧签名无法被重用
- **不兼容安装**：没有 guardian 的合约安装 ForceExit 会被正确拒绝
- **过期 deadline**：超过截止时间的操作会被拒绝
- **AlgTierLib 边界**：所有算法 ID 到安全等级的映射都经过独立验证

这些场景以前可能在心里默认"应该没问题"，现在每一条都有明确的测试保障。

---

## 成绩单

| 指标 | 结果 |
|------|------|
| Forge 单元测试 | **679 通过 / 0 失败 / 0 跳过** |
| Sepolia E2E 测试 | **79 / 79 通过** |
| Codex 对抗审计（第 4 轮） | **所有 PR 批准** |
| 行为变更 | **无** |
| 现有账户迁移需求 | **无** |

---

## 下一步：v0.18

beta.3 关闭了可观测性和代码质量的缺口。接下来是 v0.18，重点回到功能层：

- **紧急资产一键提取**：多种代币 + 全部余额，L1 和 L2 都支持
- **ForceExit 二次验证**：执行时再次确认 guardian 状态是否仍然有效
- **模块操作防重放**：防止模块的安装/卸载操作被重放
- **BLS/DVT 绑定修复**：这是主网上线的最后阻塞项

完整路线图见 [GitHub Issue #67](https://github.com/AAStarCommunity/airaccount-contract/issues/67)。

---

## 一点关于这次发布的感想

一个团队对代码质量的态度，往往在"没有外部压力"的时候最真实。

beta.3 的改动没有一项是用户能直接看到的。没有新功能，没有性能突破，没有能发推文的"大新闻"。但正是这些改动——把注释"must stay in sync"变成架构保障，把字符串错误变成类型系统，把"应该没问题"变成"测试证明没问题"——决定了一个系统在真实压力下是否可靠。

主网上线前，我们宁愿在测试网上把这些问题找完。

---

**Tag**：[v0.17.2-beta.3](https://github.com/AAStarCommunity/airaccount-contract/releases/tag/v0.17.2-beta.3) · Apache 2.0

🤝 Open source · 🌐 Public goods · 🔐 Privacy first

<!--EN-->

## AirAccount Contract v0.17.2-beta.3: Solidifying the Foundation

Some releases add features. This one checks the foundation.

beta.3 makes zero user-visible changes. Existing accounts are unaffected. What it does instead: fixes structural problems in the code before they have a chance to become bugs.

### What AirAccount Does

AirAccount is a **passwordless smart account contract** — fingerprint/Face ID/PIN controls a blockchain account, no seed phrase, no private key management. Keys never leave secure hardware. Currently live on Sepolia testnet.

### What Changed in beta.3

**Contracts now self-report their version**
Every contract now exposes a VERSION constant. Query it directly — no more maintaining an external address→version mapping table.

**Eliminated a "must stay in sync" comment**
Two independent implementations of the same algId→tier logic. One comment saying "keep these in sync." beta.3 extracts it into `AlgTierLib` — one file, zero runtime overhead (compile-time inline), one place to audit.

**Error messages are now typed, not strings**
15+ `require("string")` calls in the Factory replaced with typed custom errors. Less gas, precise SDK error matching. SDK developers using string matching in catch blocks need to switch to selector matching.

**ForceExit rejects incompatible accounts at install time**
Previously, a non-standard contract could install ForceExit and produce a zombie module — installed but the approve flow can never complete. Now `onInstall` verifies compatibility upfront. Fail early, fail clearly.

**Vote counting is ~5-8x more efficient**
Guardian vote counting replaced with Hamming weight assembly. Same semantics, verified across all possible inputs, fewer opcodes.

**8 new test paths**
Reentrancy guard, signature replay protection, incompatible install rejection, expired deadline handling, AlgTierLib boundary values — all now explicitly covered.

### The Numbers

- Forge: **679 / 0 / 0**
- Sepolia E2E: **79 / 79**
- Codex adversarial audit round 4: **All PRs approved**

**Tag**: [v0.17.2-beta.3](https://github.com/AAStarCommunity/airaccount-contract/releases/tag/v0.17.2-beta.3) · Apache 2.0
