---
title: "AirAccount KMS Beta2（v0.20.0）发布：私钥永不出 TEE，NXP 真机 34/34 端测通过"
description: "AirAccount KMS Beta2 完成完整安全审计（P0/High 全修）、RPMB 硬件反回滚、SuperPaymaster 三个便利签名端点、NXP FRDM-IMX93 真机 34/34 E2E 覆盖。私钥永不出 TEE，每次签名需要实时防重放的 WebAuthn ceremony。"
titleEn: "AirAccount KMS Beta2 (v0.20.0): Keys Never Leave TEE, 34/34 E2E on Real NXP Hardware"
descriptionEn: "AirAccount KMS Beta2 ships complete security audit (all P0/High fixed), RPMB hardware anti-rollback, three SuperPaymaster convenience signing endpoints, and 34/34 end-to-end test coverage on real NXP FRDM-IMX93 hardware. Private keys never leave the TEE — every signature requires a live, replay-protected WebAuthn ceremony."
pubDate: 2026-06-12
category: "Progress-Report"
tags: ["AirAccount", "KMS", "TEE", "WebAuthn", "OP-TEE", "ERC-4337", "SuperPaymaster", "NXP", "FRDM-IMX93", "区块链", "安全", "开源"]
lang: "zh-CN"
heroImage: "../../assets/images/airaccount-kms-beta2-v0.20.0-release.png"
---

> 2026-06-12 · Mycelium Protocol 生态 · AAStar

AirAccount 是 [Mycelium Protocol](https://www.mushroom.cv) 生态的**身份与密钥底层** —— TEE 私钥管理 + WebAuthn 无密码认证 + AWS KMS 兼容 API。SuperPaymaster 依赖它做账户验证，SuperRelay 依赖它做 TEE 双签。今天发布 **Beta2（v0.20.0）**。

---

## 一句话

私钥永不出 TEE，每次签名都需要一次**实时、防重放的 WebAuthn ceremony**；以太坊 secp256k1 钱包密钥 + RPMB 硬件反回滚。

---

## Beta2 的核心

### 🔒 安全加固

完成一轮完整安全审计，**P0/High 全部修复**（命令 ID 唯一性、TEE 调用超时+熔断、passkey 强制、submodule 锁定）。

**TA 侧 WebAuthn 独立验签**（rpId + User-Presence）—— 被攻陷的 host 无法绕过用户在场证明。这是核心安全边界：即使 REE（Rich Execution Environment）被完全攻陷，攻击者也无法在没有用户物理参与的情况下触发签名。

**RPMB 硬件反回滚** + 钱包存储（REE-FS fallback）；新增 `ReadRollbackCounter` + `GET /RollbackCounter`。RPMB（Replay Protected Memory Block）是 eMMC 内置的防回滚硬件，计数器只能递增，物理上不可回退。

WebAuthn ceremony 覆盖全部签名路径，旧的可重放 passkey 路径已下线。

---

### 🔗 SuperPaymaster 对齐（gasless 支付）

不用自己拼 EIP-712 —— KMS 直接提供三个便利签名端点，内部构造合约级正确的 typed-data，走同样的 ceremony 鉴权：

| 端点 | 用途 |
|------|------|
| **SignMicropaymentVoucher** | 微支付通道凭证（高频小额、按用量付费） |
| **SignGTokenAuthorization** | EIP-3009 `TransferWithAuthorization`（无 gas 转账） |
| **SignX402Payment** | x402 协议支付载荷（API 按调用付费、agent 机器支付） |

对集成方的意义：一行 API 调用就能拿到合约级正确、私钥不出 TEE 的签名，不需要自己处理 EIP-712 结构体和踩坑。

---

### 🛠️ 真机生产部署（NXP FRDM-IMX93）

ARM Cortex-A55 + OP-TEE 4.8 完整部署。

**CAAM-bypass**：i.MX93 的 CAAM TRNG 不稳定？CA 侧用 OsRng 生成熵注入 TA，绕过硬件卡死。

gap key（无效 P-256 pubkey）的 TEE 强制清理、自动备份系统、dirf.db 自愈。

修复了一个真机才暴露的 TA panic：`create-agent-key` 路径用 `std::time::SystemTime::now()` 在 OP-TEE 崩溃（错误码 0xffff3024）——改用 `TEE_GetREETime`。这个 bug 在模拟器上完全不出现，只有上了真实 ARM TrustZone 硬件才会触发。

*关于 NXP FRDM-IMX93 的 eMMC 变砖与恢复经历，见：[NXP FRDM-IMX93 eMMC 变砖全记录](/my/nxp-frdm-imx93-emmc-brick-recovery/)*

---

### ✅ 质量

**真机端到端测试 100% 端点覆盖：FRDM-IMX93 上 34/34 通过**（含注册/认证 ceremony 全流程、agent key、grant session、p256 session、EIP-712）。

单元测试：proto 39 + host 56（交叉编译 aarch64 上板运行）。

---

### ⚖️ 合规

Apache 2.0 license 合规（NOTICE / TRADEMARK / 中文 license）+ CLA workflow。

---

## 对生态伙伴意味着什么

- **SuperPaymaster**：gasless 支付的 TEE 双签端点已齐全，可直接对接。
- **SDK 集成方**：`@aastar/sdk` 可调用新便利端点，免去 EIP-712 拼装与踩坑。
- **开发者**：一行 API 拿到合约级正确、私钥不出 TEE 的签名。

---

## 路线图

**Beta3（下一步）：**
- WebAuthn challenge binding（[#49](https://github.com/AAStarCommunity/AirAccount/issues/49)）
- 密钥生命周期管理（[#42](https://github.com/AAStarCommunity/AirAccount/issues/42)）
- 便利签名器 from 校验（[#52](https://github.com/AAStarCommunity/AirAccount/issues/52)）

**主网前必须：**
- RPMB 生产编程（[#50](https://github.com/AAStarCommunity/AirAccount/issues/50)）
- TEE 远程证明（[#37](https://github.com/AAStarCommunity/AirAccount/issues/37)）

完整变更见 [CHANGELOG 0.20.0](https://github.com/AAStarCommunity/AirAccount/blob/main/kms/CHANGELOG.md)。

---

**GitHub**：[AAStarCommunity/AirAccount](https://github.com/AAStarCommunity/AirAccount) · Apache 2.0 · OP-TEE TrustZone

<!--EN-->

## AirAccount KMS Beta2 (v0.20.0) Release

> 2026-06-12 · Mycelium Protocol · AAStar

AirAccount is the **identity and key management layer** of the Mycelium Protocol ecosystem — TEE-based private key management + WebAuthn passwordless authentication + AWS KMS-compatible API. Today we ship **Beta2 (v0.20.0)**.

### One Line

Private keys never leave the TEE. Every signature requires a **live, replay-protected WebAuthn ceremony**. Ethereum secp256k1 wallet keys + RPMB hardware anti-rollback.

---

### Core Changes

**🔒 Security Hardening**

Complete security audit pass — all P0/High findings fixed: command ID uniqueness, TEE call timeouts + circuit breakers, passkey enforcement, submodule pinning.

**TA-side WebAuthn independent verification** (rpId + User-Presence): a compromised host cannot bypass the user-presence proof. Even if the entire REE is compromised, an attacker cannot trigger a signature without the user physically present.

**RPMB hardware anti-rollback** + wallet storage (REE-FS fallback). New: `ReadRollbackCounter` + `GET /RollbackCounter`. All signing paths now require WebAuthn ceremony; the old replayable passkey path is removed.

---

**🔗 SuperPaymaster Alignment (gasless payments)**

Three new convenience signing endpoints — internally constructs contract-correct EIP-712 typed-data, authenticated via the same ceremony:

| Endpoint | Purpose |
|----------|---------|
| **SignMicropaymentVoucher** | Micropayment channel vouchers (high-frequency, pay-per-use) |
| **SignGTokenAuthorization** | EIP-3009 `TransferWithAuthorization` (gasless transfers) |
| **SignX402Payment** | x402 protocol payment payload (API metering, agent machine payments) |

---

**🛠️ Production Deployment on NXP FRDM-IMX93**

Full ARM Cortex-A55 + OP-TEE 4.8 deployment on real hardware.

**CAAM-bypass**: i.MX93's CAAM TRNG is unstable — CA generates entropy via OsRng and injects into TA.

Fixed a real-hardware-only TA panic: `create-agent-key` path used `std::time::SystemTime::now()` which crashes in OP-TEE (0xffff3024) — fixed with `TEE_GetREETime`. This bug is invisible on emulators; only surfaces on real TrustZone silicon.

---

**✅ Quality**

**Real-hardware E2E: 34/34 endpoints pass on FRDM-IMX93** (WebAuthn registration/authentication ceremony full flow, agent key, grant session, p256 session, EIP-712). Unit tests: proto 39 + host 56 (cross-compiled aarch64, run on board).

---

### Roadmap

**Beta3**: WebAuthn challenge binding, key lifecycle management, convenience signer `from` verification.

**Pre-mainnet**: RPMB production programming, TEE remote attestation.

**GitHub**: [AAStarCommunity/AirAccount](https://github.com/AAStarCommunity/AirAccount) · Apache 2.0
