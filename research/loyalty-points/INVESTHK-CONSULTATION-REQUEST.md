# InvestHK 咨询需求清单 — Mycelium Loyalty Protocol

> 用途：在与 [InvestHK](https://www.investhk.gov.hk/) 首次免费咨询会议中使用
> 形式：可直接作为邮件预约或会议前发送给对方的 briefing 文档
> 目标：单次会议获得 5-7 项具体可执行的下一步（资源对接 / 监管指引 / 律所推荐）
> 起草：2026-04-28

---

## How to Use This Document（使用说明）

1. **预约邮件**：通过 [InvestHK Contact](https://www.investhk.gov.hk/en/contact-us.html) 发邮件，正文用本文 §1-§3 的中英对照版（精简）
2. **会议前 24 小时**：把完整版（§1-§7）作为附件发给被分配的 Investment Promotion Officer
3. **会议中**：按 §4-§5 提问，让对方记下 action items
4. **会议后**：用 §7 模板写感谢邮件 + 跟进清单

---

## §1 项目一句话介绍（Elevator Pitch）

### 中文
**Mycelium Loyalty Protocol** 是基于区块链的开放协议，让香港及亚太的中小商家可以低成本发行合规积分（airline mile / café stamp 同类），并在自愿、临时的"商家联盟"中互通使用。我们的合规设计自动符合 [Cap. 584 Schedule 8(3)](https://www.elegislation.gov.hk/hk/cap584) 的奖励积分豁免，无需申请 SVF 牌照。计划 2026 Q3 在港注册公司、Q4 上线首批商家试点。

### English
**Mycelium Loyalty Protocol** is an open blockchain protocol that lets Hong Kong and APAC SMBs issue compliant loyalty points (airline-mile / café-stamp class) and interoperate inside voluntary, time-bounded merchant coalitions. Our protocol-level compliance is designed to qualify for the [Cap. 584 Schedule 8(3)](https://www.elegislation.gov.hk/hk/cap584) bonus-point exemption without requiring an SVF license. We plan to incorporate in HK in Q3 2026 and launch a merchant pilot in Q4 2026.

---

## §2 立项假设（请协助校验是否准确）

我们目前的合规理解（**希望 InvestHK 协助校验或转介相应监管对接人**）：

| # | 假设 | 我们的依据 | 待校验 |
|---|------|----------|-------|
| **A1** | 我们的业务在 Cap. 584 Schedule 8(3) 豁免范围内（不可换现金的 bonus point 计划） | [HKMA SVF 监管页](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/stored-value-facilities-and-retail-payment-systems/regulatory-regime-for-stored-value-facilities/) | ✅ 是否需要 HKMA 主动登记？ |
| **A2** | 区块链发行不影响 Schedule 8 豁免（技术中性） | [Lexology — SVF Licensing](https://www.lexology.com/library/detail.aspx?g=809b664b-5c67-4f0a-900c-c4de357e5a25) | ✅ 是否有最新政策变动？ |
| **A3** | 临时联盟（time-bounded smart contract coalition）满足 LNE 要求 | PSD2 LNE 类比 | ✅ 香港的等效规则是什么？ |
| **A4** | ZK 证明 + 链上无 PII 满足 [PDPO](https://www.pcpd.org.hk/) | PCPD 公开指引 | ✅ 是否有专项指引？ |
| **A5** | SuperPaymaster 让用户用积分付 gas 不构成支付服务 | Pimlico ERC20 paymaster 类比 | ✅ 是否触发 MSO 牌照？ |
| **A6** | 不接受中国大陆早期用户 + 数据不出港 = 避免长臂监管 | 法律常识 | ✅ 香港政府是否有立场？ |
| **A7** | 离岸收入豁免（offshore claim）适用于全球 SaaS | IRD 现有制度 | ✅ 我们的业务模型是否合资格？ |

---

## §3 核心咨询问题（按优先级）

### 🟢 P0：必须当场获得明确答案

1. **Schedule 8 豁免的实操确认**：我们的业务模型（链上发行 + 临时联盟 + soulbound + 不可换现）是否需要主动向 HKMA 登记或仅自动适用？是否有 HKMA fintech 联络组的对接邮箱？
2. **稳定币条例（2025-08-01 生效）的边界**：我们的"积分不锚定法币、不可换现"设计是否安全在条例之外？是否需要任何主动声明？
3. **公司注册推荐路径**：[InvestHK 是否有合作的代理列表](https://www.investhk.gov.hk/en/setup-business/company-formation.html) 给到优惠？最快多久能完成注册 + 银行账户开设？

### 🟡 P1：希望获得指引或转介

4. **法律意见书：HK 律所的"reliance letter" 实操**
   - 哪几家律所有 Cap. 584 + 区块链的复合经验？
   - 一份 reliance letter 的合理价位是多少？
   - 监管沟通是否能由律所代为前置？
5. **Cyberport / HKSTP 申请的窗口与节奏**
   - [Cyberport 孵化计划](https://www.cyberport.hk/en/digital_tech/blockchain/)（HK$500K）下一轮申请截止？
   - [HKSTP](https://www.hkstp.org/) 是否更适合我们的偏开源协议路径？
   - 两者能否同时申请？
6. **HKMA FinTech Sandbox 3.1 的适用时机**
   - 我们 Phase 2（多商家临时联盟）阶段是否合适进 [Sandbox](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/fintech/fintech-supervisory-sandbox/)？
   - 是否有非牌照机构进 Sandbox 的先例？
7. **银行账户**：HSBC / Standard Chartered / 中银的 Web3 友好程度排名？哪些虚拟银行（ZA / Welab）会接受我们这种业务？
8. **GenAI Sandbox**：iDoris（我们的本地 AI 模型）是否合资格？

### ⚪ P2：长期合作可能

9. 香港 Web3 生态：哪些商业 / 学术伙伴值得首批接触？（推荐："港大 / 港中大 / 港科大 区块链研究组" + "Cyberport Fintech 中 4-5 个互补项目"）
10. **税务**：离岸收入豁免（offshore claim）的实操律所推荐？
11. **签证 / 人才**：[QMAS](https://www.immd.gov.hk/eng/services/visas/quality_migrant_admission_scheme.html) / [TechTAS](https://www.investhk.gov.hk/en/talent-attraction/tech-talent-admission-scheme.html) 哪个更适合我们的核心研发人员（中国 / 海外）？
12. 香港政府是否有发起公共部门 loyalty 项目的需求（智慧城市 / 社区货币）？

---

## §4 我们想申请 / 了解的资源

| 资源 | 申请意向 | 优先级 |
|------|---------|-------|
| Cyberport 孵化计划（HK$500K） | 强 | P1 — 计划 Q3 2026 申请 |
| HKSTP Co-Acceleration | 中 | P2 — 评估中 |
| HKMA FinTech Sandbox 3.1 | 中 | P1 — Phase 2 阶段（M4-M9） |
| GenAI Sandbox | 中 | P2 — iDoris 上线后 |
| InvestHK 后续 SaaS 引荐 | 强 | P0 — 银行 / 律所 / 会计师 |
| 离岸收入豁免认定 | 强 | P1 — 注册后 6 个月内 |
| QMAS / TechTAS 人才计划 | 中 | P2 — 团队扩张时 |

---

## §5 我们能提供的（Reciprocity）

不是单方面索取。我们对香港生态的承诺：

1. **公开技术规范**：OpenPNTs 协议规范以 Apache 2.0 开源，作为香港 fintech 生态的公共物品
2. **本地优先合作**：首批 5 家试点商家、首批 SaaS 客户、首批合作律所 / 会计师 — 都优先选香港本地
3. **案例研究公开化**：愿意配合 [HK FinTech Week](https://www.hongkongfintechweek.com/) / Cyberport / HKSTP 出案例研究 + 公开演讲
4. **税务驻港**：注册公司 → 持续运营 → 创造就业（即使部分研发离岸）
5. **协议治理透明**：未来若有 token / 治理结构，主动符合香港 FATF 透明度要求

---

## §6 我们的关键数据 / 项目背景

| 项目 | 数据 |
|------|------|
| **创始团队** | Aura AI / Mycelium Protocol / MushroomDAO（已运营生态） |
| **既有产品** | Cos72 (Community OS, Apache 2.0) / Sin90 (Personal OS) / iDoris (Local AI) / SuperPaymaster (ERC-4337 gasless) |
| **现有 GitHub Org** | [github.com/AAStarCommunity](https://github.com/AAStarCommunity) / [github.com/MushroomDAO](https://github.com/MushroomDAO) / [github.com/AuraAIHQ](https://github.com/AuraAIHQ) |
| **既有调研** | [research/loyalty-points/REPORT.md](./REPORT.md)（43KB 全球行业 + 6 国法规调研） |
| **资金方案** | [launch.mushroom.cv](https://launch.mushroom.cv) 冷启动模式（非 VC） |
| **Phase 1 预算** | HKD 80,000-130,000（已就绪） |
| **Phase 1 时间** | 2026 Q3 注册 → 2026 Q4 首批 1-2 商家试点 |

---

## §7 期望的 5 项具体后续动作

会议结束时，希望 InvestHK 帮助确认：

1. ✅ **HKMA fintech 联络组邮箱 / 联系方式**（用于 Schedule 8 主动备案）
2. ✅ **2-3 家律所推荐**（Cap. 584 + 区块链经验，附 reliance letter 标准价）
3. ✅ **Cyberport 孵化对接人**（下一轮申请准备会议）
4. ✅ **2-3 家银行 / 虚拟银行**（Web3 友好的开户路径）
5. ✅ **会议纪要 + 后续 follow-up 邮件**（含 InvestHK 内部分配的 contact officer）

---

## §8 邮件预约模板（直接可发）

### 主题（Subject）
```
Inquiry on HK Setup for Loyalty Protocol — Cap. 584 Schedule 8 Pathway
```

### 正文（中文版）

> 您好 InvestHK 团队，
>
> 我们是 **Mycelium Loyalty Protocol** 团队，正计划 2026 Q3 在香港注册公司，启动一个面向亚太中小商家的开放协议积分服务。
>
> 我们的合规设计自动符合 Cap. 584 Schedule 8(3) 奖励积分豁免（不可换现 + 限定商家网络），不需要 HKMA SVF 牌照即可起步。
>
> 希望预约一次 1 小时的免费咨询，议题包括：
> 1. 公司注册路径与时间表
> 2. Schedule 8 豁免的实操确认
> 3. Cyberport / HKSTP 等扶持计划的衔接
> 4. 律所 / 银行 / 会计师推荐
>
> 详细 briefing 文档已附件，期待您的时间安排。
>
> 此致
> [姓名]
> Mycelium Protocol / Aura AI
> [联系方式]

### 正文（English）

> Dear InvestHK Team,
>
> We are **Mycelium Loyalty Protocol**, planning to incorporate in Hong Kong in Q3 2026 to launch an open-protocol loyalty service for SMBs across APAC.
>
> Our compliance design is engineered to qualify for the Cap. 584 Schedule 8(3) bonus-point exemption (non-cash-redeemable + limited merchant network) — no SVF license required to start.
>
> We would like to schedule a 1-hour free consultation covering:
> 1. Incorporation path and timeline
> 2. Confirmation of Schedule 8 applicability
> 3. Cyberport / HKSTP / FinTech Sandbox pathways
> 4. Introductions to law firms, banks, and accountants
>
> Full briefing attached. Looking forward to scheduling.
>
> Best,
> [Name]
> Mycelium Protocol / Aura AI
> [Contact]

---

## §9 会议中要带的资料（打印 / 数字版）

- [ ] [REPORT.md](./REPORT.md) — 全球行业调研（PDF 版）
- [ ] [RECOMMENDATION.md](./RECOMMENDATION.md) — 8 个具体决策
- [ ] [HK-SETUP-GUIDE.md](./HK-SETUP-GUIDE.md) — 香港运营深度调研
- [ ] [Mycelium Protocol PROFILE.md](https://github.com/HyperCapitalHQ/mycelium-protocol)
- [ ] 个人简介 / 团队简介（1 页）
- [ ] [launch.mushroom.cv](https://launch.mushroom.cv) 截图
- [ ] 现有 GitHub repos 链接清单
- [ ] 商业模型一页 PPT（可选）

---

## §10 会后跟进模板

### 24 小时内发感谢邮件

> 您好 [InvestHK Officer Name]，
>
> 感谢今天的咨询。会议中讨论的关键 action items 我整理如下，请协助确认：
>
> | # | 行动 | 负责方 | 时间表 |
> |---|------|-------|-------|
> | 1 | [InvestHK 提供 HKMA fintech 邮箱] | InvestHK | 1 周内 |
> | 2 | [律所推荐 X、Y、Z] | InvestHK | 1 周内 |
> | 3 | [Cyberport 引荐 NN officer] | InvestHK | 2 周内 |
> | 4 | [我们提交 Cyberport 申请草稿给您 review] | Mycelium | 2 周内 |
> | 5 | [4 周后回访同步进展] | 双方 | 2026-05-XX |
>
> 期待持续合作。
>
> [姓名]

### 14 天后回访

如果没收到 follow-up，主动发：

> Hi [Officer Name],
>
> Following up on our [date] meeting. We've made progress on:
> - [...]
> - [...]
>
> Could you confirm status on items #1, #3 from the action list?
>
> Thanks,

---

## 附录 A：InvestHK 联系方式

- 官网：[https://www.investhk.gov.hk/](https://www.investhk.gov.hk/)
- Fintech 团队：[https://www.investhk.gov.hk/en/key-industries/financial-services-fintech.html](https://www.investhk.gov.hk/en/key-industries/financial-services-fintech.html)
- 总联系邮箱：enquiry@investhk.gov.hk
- 香港办事处地址：25/F, Fairmont House, 8 Cotton Tree Drive, Central, Hong Kong
- 推荐：直接邮件 enquiry 或填表 — 通常 3-5 工作日回复并安排 fintech officer 对接

## 附录 B：备选预约渠道（如 InvestHK 排队长）

1. **Cyberport** — [direct enquiry](https://www.cyberport.hk/en/contact)（更专注 fintech / blockchain）
2. **HKSTP** — [contact form](https://www.hkstp.org/contact-us/)（更专注 deep tech）
3. **HK FinTech Association** — 行业会员，会员制
4. **HKMA FintechFacilitation Office (FFO)** — fintech@hkma.gov.hk（监管侧直接）

**建议优先级**：InvestHK → Cyberport → HKMA FFO（按门槛由低到高，每个都是 1 小时免费起步）

---

*本文档可直接复制粘贴用作 InvestHK 邮件预约，或发送给对方 officer 作会前 briefing。建议保留版本控制，每次修订后版本 +0.1。*

*v0.1 · 2026-04-28 · Mycelium Protocol*
