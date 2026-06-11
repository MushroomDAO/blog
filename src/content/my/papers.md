---
title: "论文与研究"
description: "Jason 正在从事的研究方向与相关论文、预印本、技术报告。持续更新中。"
pubDate: 2026-01-01
updatedDate: 2026-06-11
isHub: true
hubIcon: "📄"
category: "Research"
tags: ["论文", "研究", "Web3", "AirAccount", "ERC-4337", "AI身份"]
---

> 本页持续更新，记录正在进行的研究方向以及相关论文、技术报告。

---

## 研究方向

### 1. 去中心化账户抽象（Account Abstraction）

以 ERC-4337 为基础的用户账户基础设施研究。核心问题：如何让普通用户在不理解私钥的前提下，安全地使用区块链应用？

**AirAccount** 是这一方向的实践项目：邮箱即账户，无需助记词，通过 Google OAuth + TEE 托管实现真正的无感账户体验。

相关技术栈：ERC-4337 UserOperation、Paymaster（Gas 代付）、Bundler、Social Recovery、Multi-party Computation。

---

### 2. 可持续协作协议（Sustainable Collaboration Protocol）

Mycelium Protocol 的核心研究：如何设计让贡献者长期受益、而不被平台剥削的协作机制？

从 Spores 协议到 PGL（Public Goods Layer），研究数字公共物品的分配模型：Supplier / Wrapper / Seller 三角色链上自动分账，贡献记录 SBT（不可转让），无 IDO 无投机。

---

### 3. AI Agent 技能系统

研究 AI Agent 技能的层次化管理、技能合并与自演化机制（SkillPyramid）。核心问题：如何让 AI Agent 的技能库随使用自动优化，而不是静态的 prompt 集合？

---

## 论文 / 技术报告

| 标题 | 类型 | 状态 | 链接 |
|------|------|------|------|
| AirAccount: Email-Based Account Abstraction with TEE | 技术报告 | 草稿 | — |
| Spores: A Sustainable Collaboration Protocol for Open Source | 白皮书 | v0.2 | — |
| SkillPyramid: Hierarchical Skill Consolidation for Self-Evolving Agents | 研究笔记 | 已发布 | [blog.mushroom.cv](https://blog.mushroom.cv/blog/skillpyramid-hierarchical-skill-consolidation-self-evolving-agents/) |
| SuperPaymaster: Gasless UX with ERC-4337 AOA Card | 技术文档 | 已发布 | [blog.mushroom.cv](https://blog.mushroom.cv/blog/superpaymaster-aoa-gas-card-erc4337/) |

---

## 相关开源项目

→ 见 [开源作品](/my/open-source/) 页面

---

*最后更新：2026-06-11 | 如有学术合作意向，请通过 [AAStar GitHub](https://github.com/AAStarCommunity) 联系*
