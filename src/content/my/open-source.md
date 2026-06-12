---
title: "开源作品"
description: "Jason 参与和主导的开源项目，涵盖 Web3 基础设施、AI Agent 工具、协议层工具。持续更新。"
pubDate: 2026-01-01
updatedDate: 2026-06-11
isHub: true
hubIcon: "💻"
category: "Launch"
tags: ["开源", "GitHub", "Web3", "ERC-4337", "AI", "Mycelium"]
---

> 记录参与和主导的开源项目。按活跃度排列，持续更新。

---

## 主导项目

| 项目 | GitHub | 语言 | 简介 |
|------|--------|------|------|
| **AirAccount** | [AAStarCommunity/AirAccount](https://github.com/AAStarCommunity/AirAccount) | TypeScript / Solidity / Rust | 邮箱即账户的 ERC-4337 账户抽象实现，无助记词，Google OAuth + TEE 托管，Sepolia testnet 可用。[→ KMS Beta2](https://blog.mushroom.cv/blog/airaccount-kms-beta2-v0-20-0-release/) |
| **AirAccount Contract** | [AAStarCommunity/airaccount-contract](https://github.com/AAStarCommunity/airaccount-contract) | Solidity | 核心智能合约层：WebAuthn Passkey 登录、Tiered 多签、Session Key、Social Recovery、ForceExit、EIP-7702 EOA 升级。[→ beta.3 发布说明](https://blog.mushroom.cv/blog/airaccount-contract-v0-17-2-beta3-release/) |
| **SuperPaymaster** | [AAStarCommunity/SuperPaymaster](https://github.com/AAStarCommunity/SuperPaymaster) | Solidity | ERC-4337 Paymaster，支持 AOA Gas 卡模式，让用户免 Gas 交互 |
| **CometENS** | [MushroomDAO/CometENS](https://github.com/MushroomDAO/CometENS) | Solidity / TypeScript | 免费 .comet.eth 子域名服务，L2 OPResolver，ERC-721 子域所有权，进度 65% |
| **Cos72** | [AAStarCommunity/Cos72](https://github.com/AAStarCommunity/Cos72) | TypeScript | 社区操作系统，含 MyTask / MyShop / MyVote 模块 |
| **BroodBrain** | [AAStarCommunity/Brood](https://github.com/AAStarCommunity/Brood) | Markdown | 组织神经系统，上下文管理、任务透明化、协议文档 |
| **Mycelium Blog** | [MushroomDAO/blog](https://github.com/MushroomDAO/blog) | Astro / TypeScript | 本博客，多平台发布系统（Astro + WeChat + 小红书） |
| **Heinu1（黑奴一号）** | [jhfnetboy/Heinu1](https://github.com/jhfnetboy/Heinu1) | TypeScript | 用微信远程控制家里的 Claude Code；iLink 官方 API，零封号风险，SQLite 会话持久化。[→ 介绍文章](https://blog.mushroom.cv/blog/heinu1-wechat-claude-code-remote-control-bot/) |

---

## 参与贡献

| 项目 | GitHub | 贡献类型 | 备注 |
|------|--------|----------|------|
| **OpenPNTs** | [MushroomDAO/OpenPNTs](https://github.com/MushroomDAO/OpenPNTs) | 协议设计 | 社区积分标准，ERC-20 兼容扩展，用于 SuperPaymaster Gas 代付 |
| **agent-speaker-relay** | [MushroomDAO/agent-speaker-relay](https://github.com/MushroomDAO/agent-speaker-relay) | 部署运维 | Nostr Relay（strfry Docker），AuraAI agent 通信基础设施 |

---

## 技术方向分布

```
Web3 基础设施  ████████████  账户抽象 / Gas 代付 / ENS / 智能合约
AI 工具链      ██████        Agent 系统 / 技能管理 / 内容发布
协议层         ████          可持续协作 / 数字公共物品 / 治理
```

---

*最后更新：2026-06-12（新增 Heinu1）| 所有项目均为 Apache 2.0 或 MIT 开源协议*
