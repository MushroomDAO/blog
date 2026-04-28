# Agent C 原始研究：区块链积分项目 + Mycelium 定位

> 来源：研究 Agent C, 2026-04-28
> 范围：Web3 / 区块链 loyalty 项目盘点（含死亡项目）+ Mycelium 协议定位的法律 / 技术 / 商业风险分析

参见 REPORT.md §7-§8 章节。本文为综合报告事实底稿。

## §1 现有 Web3 / 区块链 Loyalty 项目（2018-2026）

### 1.1 企业区块链 Loyalty（B2B SaaS, 许可链）

| 项目 | 状态 | 模型 | 教训 |
|---|---|---|---|
| **Loyyal**（US/UAE, Hyperledger）| **活，已转型**。原 Hyperledger Fabric，与 Emirates Group (Skywards) 签 3 年生产协议 (Feb 2020)。报告"80% 交易成本节省" + "30% 对账成本削减"。ISO/IEC 27001:2022 认证。现自我营销为"区块链 + AI SaaS"而非 token 项目 | B2B blockchain-as-a-service。无公开 token | **去掉 token 才存活**，专注企业 SLA + 对账成本节省，**不是去中心化** |
| **Singapore Airlines KrisPay** (Microsoft + KPMG, 2018) | **被 Kris+ 吸收**（活，不再营销为"区块链"） | 闭环数字钱包 | 区块链成为不可见管道 |
| **Cathay Pacific Asia Miles + Accenture** (2018) | 一次性营销活动，非持续产品 | 营销 PoC | 企业区块链可对账，但不足支撑独立 token 经济 |
| **American Express + Hyperledger + Boxed** (2018) | 安静 PoC，非产品 | Hyperledger 试点 | |
| **IBM Customer Loyalty Program** | **死/归档**。GitHub 2019-05 归档 | Fabric 参考架构 | 大厂参考项目随战略变更而死 |

### 1.2 公开 Token Loyalty 币

| 项目 | 状态 |
|---|---|
| **Qiibee (QBX)** | **僵尸/勉强活**。ATH Jan 2025 ~$0.047，现 $0.001-0.004 |
| **Lympo (LMT)** | **品牌已死**。Animoca Brands 子公司。热钱包 2022-01-10 被黑，165.2M LMT (~$18.7M) 被盗，价格崩 92% |
| **UTU Trust ($UTU)** | **活但小**。ERC-20 多链。"Review-to-earn" |
| **Boba Network (BOBA)** | **活，已转型**。500M 完全解锁 2025-06，转型"AI L2"，不再是 loyalty 网络 |
| **Momentum Protocol** | **死** |
| **SoLoyal** | **死** |

### 1.3 Web3 任务 / Loyalty-as-Marketing 平台

| 项目 | 状态 |
|---|---|
| **Galxe** | **类目最大，活**。34M+ 用户，1.2B+ 任务，6,700+ 合作伙伴 |
| **Layer3 (L3)** | **活，tokenomics 困难**。TGE 2024-07，FDV ~$34.8M (Apr 2026) |
| **Crew3 → Zealy** | 2023 中改名转型 Web2 |
| **RabbitHole** | **活但安静** |
| **Mintbase Loyalty (NEAR)** | **活，loyalty 产品弱化** |

### 1.4 信用卡 / Fintech 邻近

| 项目 | 状态 |
|---|---|
| **Bilt Rewards** | **活，$10.75B 估值 (Jul 2025)，$250M 融资**。loyalty 货币**非链上**；**Raise Network**选 **Solana** 做 SmartCard |
| **Crypto.com Visa** | **活**。最高 8% CRO 返还 |
| **Coinbase One Card** | **2025 秋发布**。2% BTC 基础 |
| **Flexa SPEDN** | **2026-03-31 关闭** |

### 1.5 大牌 Web3 Loyalty 实验

| 项目 | 状态 |
|---|---|
| **Starbucks Odyssey** | **2024-03 关闭**，~18 月后。NFT 市场崩 + 复杂度 + 消费者疲劳 |
| **Nike RTFKT** | **死**。Web3 服务 2025-01 末结束。Nike 于 2025-12-17 出售品牌。CryptoKick NFT 从 ~$8,000 崩到 ~$16 |
| **Adidas (ALTS, Three Stripes Studio)** | **活** |
| **Nissan Japan Web3 Rewards** | **活 (2025 启动)**，仅日本 |
| NFT loyalty 市场崩盘 | NFT 市场 Q1 2025 同比 -63%（$4.1B → $1.5B）。估计 96% 的品牌 NFT 项目"死" |

### 1.6 联盟 Loyalty 失败（前区块链 — 重要参考）

- **Plenti** (American Express, 2015-2018)：2015-05-04 推出，2018-04-16 关闭。合作伙伴：Macy's, Chili's, AT&T, Hulu, Expedia, Enterprise。**最经常引用的警示故事**

### 1.7 DePIN 类比"硬件运营者的 Loyalty"

| 项目 | 状态 |
|---|---|
| **Helium** | **63,806 活跃热点 (Q1 2025)**。需求侧瓶颈 |
| **Hivemapper / Bee Maps** | **$32M Pantera 主投**。HONEY 代币 |
| **IoTeX** | DePIN 专用 L1 |

**DePIN 教训**："stall at demand bottleneck" — 供应侧激励容易，需求侧飞轮难。

## §2 关键技术方案

### 2.1 ERC-20 vs ERC-1155 用于积分

| 维度 | ERC-20 | ERC-1155 |
|---|---|---|
| **可替代积分契合度** | 原生契合 | 可工作，但增加复杂度 |
| **多商家单合约** | 每商家一合约 | 一合约可托管多商家积分（每个 tokenId = 一个商家）— 联盟的 gas/UX 大胜 |
| **批量转账** | 一次一个 | 原生 `safeBatchTransferFrom` |
| **链上存储成本** | 每商家更高 | 多代币联盟更低 |
| **钱包支持** | 通用 | 较好但稍弱 |
| **DeFi 可组合性** | 最佳 | 有限 |
| **推荐** | 每商家想要可在 AMM 交易的一级可替代代币 | 联盟想要批量操作 + 跨商家兑换的共享多商家账本（理想 Mycelium 联盟模型） |

**Mycelium 实践模式**：每商家 ERC-20 wrapper 用于 DeFi 可组合性 + ERC-1155"联盟账本"用于联盟内批量兑换

### 2.2 多商家互操作 — 跨链选项

- **IBC (Cosmos)**：117 链 (2024-10) — 主权链联盟最成熟
- **LayerZero**：93 链
- **Circle CCTP**：活跃地址领先
- **总互操作 TVL**：~$8B 跨 43 协议 (2024-10)
- **Merkle 证明 / claim 树**：标准模式

### 2.3 隐私：购买记录是否上链？

- **2025 强共识：不**。Loyalty 应用现用 ZK 证明验证"客户做了合格购买"而不披露交易元数据
- **ZK 证明市场**：$75M 收入 2024，预计 2030 $10B+
- **实践模式**：仅承诺哈希上链，原始购买数据在加密链下数据库
- **BIS Working Paper No. 1242**：数字货币的隐私增强技术

### 2.4 Gas 抽象 (ERC-4337 Paymasters)

- **账户抽象采用**：40M+ 智能账户（2023-03 起），100M+ 用户操作
- **Paymasters 可赞助 gas 或让用户用 ERC-20 付 gas**（USDC、品牌代币、**或商家积分**）
- **Dec 2025 OtterSec 审计**：paymaster 合约有隐藏的 DoS、replay、gas 鞭笞向量
- **参考实现**：Pimlico ERC20 paymaster, Circle Paymaster, AAStar SuperPaymaster

### 2.5 反 Sybil / 反欺诈

- **Human Passport** (formerly Gitcoin Passport)：守卫 9 轮 Gitcoin Grant；攻击者影响降 80%+
- **World ID**：生物 Orb 扫描 + ZK 证明
- **TrustaLabs Sybil Identification**：开源 ML 框架
- **Galxe Passport**：SBT 身份层

### 2.6 "商家发行的稳定币"类比

- 经济上 = closed-loop 商家发行 IOU
- FinCEN prepaid-access 规则下 closed-loop ≤ $2,000/day **MSB 豁免**
- **GENIUS Act (2025-07-18 签署)**：限制*支付*稳定币给保险存款机构（银行/信用社）+ 1:1 储备。**不覆盖 loyalty 积分**
- **OCC NPR (2026-03)**：品牌/白标稳定币可能要求单独发行实体。**强化：不要把 loyalty 积分当稳定币**

## §3 Mycelium 定位：先例、风险、合规护城河

### 3.1 "无许可联盟 loyalty"最近先例

| 先例 | Mycelium 启示 |
|---|---|
| **Plenti（中心化联盟）** | 失败 — 合作伙伴议程冲突、UX 摩擦、平行专属计划。**Mycelium 的"临时联盟"答案在原则上正确** — 短联盟避免长期承诺问题 |
| **Loyyal（企业区块链联盟）** | 仅靠**去掉 token** + 卖对账节省给 incumbents 才存活。**教训：开放协议可能需要"无聊的 B2B SaaS"销售面** |
| **Qiibee（开放代币联盟 L1）** | 僵尸。建立了供应但从未解决需求侧飞轮。**教训：分发 > 技术** |
| **Currency Alliance（Web2 SaaS 联盟平台）** | 活，增长 — 证明"API-first 多伙伴 loyalty"在**软件**层有需求。**Mycelium 的开放协议版本差异化于：(a) 无许可加入 (b) gasless UX (c) ZK 隐私** |
| **DePIN (Helium, Hivemapper)** | 需求 > 供应瓶颈。**教训：Mycelium 需要第一天的需求侧吸引，不仅是商家供应** |

### 3.2 最大风险

**法律 / 监管**
1. **证券分类 (Howey)**：SEC + CFTC 2026-03 联合框架仅在代币*通过消费获得*而非*作为投资购买*时排除 loyalty 积分。**一旦你的代币有二级市场价格，就有被认定为投资的风险**
2. **货币转账风险**：联盟内跨商家可转让性可将你从"closed-loop"豁免移到"open-loop"受规管状态。FinCEN $2,000/day 阈值很重要
3. **礼品卡 / 未认领财产法**：州 escheatment 法可能适用
4. **EU MiCA**：loyalty 积分**不是** MiCA 下金融工具，但若代币在二级市场自由交易，MiCA 的"ART"或"EMT"分类可能拉入
5. **GDPR**：用户行为 AI 推断引发 GDPR Art. 22（自动化决策）暴露

**技术**
1. **Paymaster DoS / 鞭笞**：OtterSec Dec 2025 — 非小事。SuperPaymaster 需正式验证或顶级审计
2. **跨商家清算**：链上跨 10+ 商家结算兑换在小票面经济上失败（Currency Alliance 2019 critique：98% 的 loyalty earn-side 交易太小经济上无法证明 L1 gas — **L2/Base/Polygon 必需**）
3. **热钱包黑客先例 (Lympo)**：任何托管组件都将是目标

**商业**
1. **冷启动网络效应**：杀了 Plenti 和阻滞 Qiibee 的同问题
2. **负债会计**：IFRS 15 / ASC 606 下，发行的积分成为商家资产负债表上的递延收入负债。Delta 2015 末 loyalty 负债：$3.9B（10% 总负债）；Marriott：$2.6B（25%）
3. **Forrester 2025 发现**：品牌忠诚度 2025 预计下降 25%；75% 的客户会为更好价格放弃 loyalty 计划。**积分单独不是护城河**

### 3.3 合规护城河借鉴

1. **将积分定义为服务凭证，非货币**。FinCEN closed-loop 豁免在积分仅可兑换发行方自己的商品/服务（或发行方 + 合同关联团体）时维持。Mycelium 的"临时联盟"必须结构为**有定义终止条款的合同关联团体**以保持 closed-loop 安全港
2. **每商家每日发行 + 兑换硬上限**（保持低于 $2,000/day prepaid-access 阈值，避免 MSB 触发）
3. **无二级市场**。代币默认不可转让（兑换前 soulbound）。或仅在联盟白名单内可转让。**这对 SEC"通过消费获得"豁免至关重要**
4. **真实 SKU 支撑**。每个发行的积分必须对应发行方或联盟成员的真实可兑换 SKU，**法律上记录为商家会计中的递延收入义务**
5. **过期 + breakage 政策**
6. **Privacy-by-default**。ZK 证明用于资格，无链上 PII
7. **协议开源 + AI / 优化器闭源**
8. **司法管辖友好基地**：Wyoming（DAO LLC）、Colorado（Digital Token Act）、瑞士（FINMA）、UAE（DIFC）

## §4 AI 在 Loyalty 解决什么

### 4.1 市场规模
- **Loyalty management 市场**：$12.89B (2025) → $20.36B (2030)，9.6% CAGR
- **AI in eCommerce**：$7.57B (2024) → $8.65B (2025)，14.6% CAGR

### 4.2 个性化 & 参与
- **71% 的消费者期望个性化**
- **Albertsons (案例)**：AI 主导的 loyalty 重设计 2024 → 会员 +15% 至 44.3M
- **Starbucks Rewards (案例)**：AI offer 引擎早 2024 多 4M 访问，活跃成员 +13%
- **AI loyalty ROI**：90% 报告正 ROI，平均 4.9x；顶级 7.2x

### 4.3 最优发行率 / 定价
- NBER paper "redeemable loyalty token design" (Dec 2024)：形式模型

### 4.4 欺诈检测
- ML 比规则更好抓新攻击

### 4.5 跨联盟清算自动化
- Loyyal-Emirates：80% 对账成本削减。**联盟 loyalty 中 AI 单一最高 ROI**

## §5 综合：Mycelium 精确定位是否被尝试过？

**简答：部分是，组合否**。

| 组件 | 最近先例 | 结果 |
|---|---|---|
| 开放协议 + 无许可商家加入 | Qiibee | 僵尸（无需求侧）|
| 多商家联盟 + 临时形成 | Plenti | 失败（中心化、永久伙伴、无联盟生命周期）|
| Gasless UX via paymaster | Circle Paymaster, Pimlico ERC-20 paymaster | 活（USDC），尚未应用于 loyalty |
| AI 驱动发行优化 | Albertsons, Starbucks（闭源）| 内部强 ROI，从未作为开放服务给 SMB |
| Privacy-first via ZK | 学术理论；生产中萌芽 | 尚未为 loyalty 产品化 |
| 区块链上联盟对账 | Loyyal-Emirates | 技术上工作；需要 B2B 销售动作 |

**Mycelium 提议的独特组合 — 开放协议 + 临时联盟 + gasless + AI 优化器 + 隐私优先，针对 SMB 而非企业 — 没有直接先例**。

**最可能的失败模式（必须设计避免）**：
1. SMB 不会为他们不理解的东西付钱 → 必须**默认 gasless 和 AI-on-rails**，不是"配置你的代币经济"
2. 需求侧冷启动 → **以一两家高客流商家为锚**（Plenti/Helium 教训）
3. 监管漂移 → **服务凭证框架必须在协议中执行**（caps、过期、联盟白名单），不仅在营销
4. 投机 → **兑换前不可转让**默认，无 AMM 上市

**最强护城河设计**：
1. Gasless + paymaster 用积分本身付（关闭循环，移除商家对 ETH 依赖）
2. AI 每商家发行优化器证明性增加兑换率
3. 时间限制联盟智能合约（"flash coalitions"）— 文献中真正新颖
4. ZK 兑换证明（链上无 PII）— 抢占 GDPR

## 关键元观察

1. **每个存活的 Web3 loyalty 项目都卖对账节省，不是"去中心化"**。Loyyal → Emirates B2B。KrisPay → 不可见管道。**将 Mycelium 框架为"SMB 联盟开放协议对账基础设施"**，而非"Web3 loyalty"
2. **代币投机比任何东西更快杀死 loyalty 项目**。Lympo, Starbucks Odyssey, Nike RTFKT, 甚至 Layer3 — 都因代币-价格-作为-loyalty-价值耦合受苦。**兑换前不可转让 + 无 AMM 上市是单一最强存活设计**
3. **合规护城河比技术护城河更有价值**。三个竞争者一周可复制你的智能合约。没有人在 18 个月内复制你的"服务凭证法律意见 + 联盟关联条款 + 协议级每商家上限执行"
4. **AI 在这里的杀手用例不是个性化 — 是每商家发行优化**。"我是面包店，我的最优积分/美元比是什么？" — 几乎没有 SMB 今天能访问到
5. **"OpenPNTs" 名称在 2026-04 公共足迹除 Mycelium 内部外为零**。要么发布规范以 ENS 引用，要么改名以与现有标准对齐
