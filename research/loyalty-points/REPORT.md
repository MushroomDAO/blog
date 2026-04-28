# 全球商业积分行业深度调研：商业模型、法规边界、与区块链的可能性

> 报告日期：2026-04-28 · 撰写：Mycelium Protocol / Aura AI 研究组
> 类型：可行性调研 · 中文综合报告
> 原始研究材料：`raw/01-industry-overview.md` (行业全景) · `raw/02-regulations.md` (各国法规) · `raw/03-blockchain-mycelium-positioning.md` (区块链 + Mycelium 定位)

---

## 摘要 (Abstract)

商业积分（loyalty points / rewards）是一个**全球数千亿美元规模、却被严重低估的行业**：航空里程的资本化估值常常**超过母航空公司本身**（American AAdvantage 估值约 $26-30B vs. AAL 市值多次低于 $15B）；Starbucks 仅靠未兑换积分余额就在 2021 年获得了**约 $1.55 亿美元**的非应税利润，其本质是"咖啡馆里的银行"。

本报告综合三条调研线索：

1. **行业全景**：覆盖美 / 加 / 中 / 日 / 韩 / 欧 / 澳 / 全球航空联盟的 45+ 头部公司，及其经济模型、用户/商家价值、痛点
2. **法规边界**：6 大司法辖区（中 / 美 / 欧英 / 日 / 韩 / 新港）的核心法规与"积分是否构成货币 / 支付工具 / e-money"的边界判定
3. **区块链可能性**：盘点 2018-2026 期间 Web3 积分项目（含已死项目复盘）、技术方案（ERC-20 vs ERC-1155、ZK 隐私、ERC-4337 Paymaster）、Mycelium Protocol 自组织联盟方案的法律 / 技术 / 商业风险

并回答用户提出的**三个核心论断**：

- **§9.1** 商家为什么需要积分？解决了什么核心问题？
- **§9.2** 商业积分是不是"灰色货币"？监管究竟管不管？
- **§9.3** Mycelium 自组织积分联盟的合规设计与可行性

**核心结论**：积分**确实是有限范围的内部货币**，全球监管的统一边界是"是否对价收款 + 是否跨第三方流通 + 是否可换现 + 是否在二级市场交易"。一旦跨过任意一条线，就触发支付牌照 / e-money / 证券监管。Mycelium 的"无许可、自组织、临时联盟"设计在原则上正确（避免 Plenti 长期承诺问题），但**必须以协议级强制执行 4 道合规栅栏**（service voucher 框架 / 每商家硬上限 / 默认不可转让 / 真实 SKU 支撑）才能跨越中美严监管。

---

## §1 导论：为什么我们关心这个问题？

商业积分是一个**老行业 × 新机会**的交汇点：

- **老行业**：1981 年 American Airlines 推出世界首个 frequent flyer program 以来，loyalty 已是成熟基础设施。麦当劳 2024 年仅 loyalty 计划就驱动 **$30B 系统销售额**（同比 +30%）。
- **新机会**：CFPB 2024-12 Circular 2024-07 把"贬值"和"撤销"列入 UDAAP 红线；Forrester 2025 预测品牌忠诚度下降 25%；"3 ¥10 一杯咖啡折扣 + 邻近 5 家面包店宾馆通用"的小商家联盟在中国 / 东南亚有海量真实需求，却没有合规、低门槛、可信任的协议层供给。

我们做这份调研的目的不是写综述，是为 **Mycelium Protocol** 评估"基于区块链的中小商业组织积分协议 + 自组织临时联盟"这个产品方向。最终输出三个判断：

1. 行业的痛点和机会到底在哪
2. 监管红线在哪，怎么避开
3. 我们的设计是否可行，最大风险是什么

---

## §2 商业积分是什么？为何而生？

### 2.1 历史溯源

| 年份 | 事件 |
|------|------|
| 1981 | American Airlines 推出世界首个 frequent flyer program — AAdvantage |
| 1981 | United Airlines、Delta 同年跟进 |
| 1991 | American Express 推出 Membership Rewards |
| 1995 | Tesco 推出 Clubcard，开启零售 loyalty 时代 |
| 2002 | Nectar (UK)、Aeroplan IPO（世界首个上市 loyalty 公司） |
| 2003 | T-Point (Japan) — 亚洲首个大型联盟 loyalty |
| 2009 | Chase Ultimate Rewards — 银行可转移积分时代 |
| 2018 | Singapore Airlines KrisPay — 首个区块链航空里程 |
| 2024 | CFPB Circular 2024-07 + 韩国 EFTA 100% 备付金修正 |
| 2026 | Bilt Rewards 估值 $10.75B；积分作为独立金融资产被市场重估 |

### 2.2 经济本质：三位一体

商业积分本质是**三个东西的叠加**：

1. **促销工具**（marketing）：吸引客户、增加复购、拉高客单价
2. **财务负债 + 杠杆**（finance）：用未兑换的"未来折扣"换取**今天的现金流**和**0 利率浮存金**
3. **内部货币**（internal currency）：在商家自己的封闭网络内，1 积分代表 X 元服务

**关键洞察**：第 (2)、(3) 点决定了为什么航空 / 信用卡 / 大零售商如此执着于积分 — 它们其实在运营**类银行业务**。

> Delta 2024 年从 American Express 合作中获得 **$7.4B** 现金（注册奖励 + 年费 + 里程销售）。航空公司本质上是把"未来座位"批发给银行，银行再零售给消费者。

### 2.3 行业规模数字（2025-2026）

| 指标 | 数值 | 来源 |
|------|------|------|
| 全球 Loyalty Management Market 2025 | **$12.89B → $20.36B by 2030** (CAGR 9.6%) | [MarketsandMarkets](https://www.marketsandmarkets.com/PressReleases/loyalty-management.asp) |
| Loyalty Programs Market（更广口径）2024 → 2029 | **$80.92B → $155.22B** (CAGR 13.4%) | [Research and Markets](https://www.researchandmarkets.com/report/loyalty-card) |
| 全球未兑换积分等价递延收入 | **~$360B+** | [Stanford / MIT 学术研究](https://web.stanford.edu/~daniancu/Papers/Working/loyalty_pricing.pdf) |
| 美国未使用礼品卡余额 | ~$23B (2025) | [Hubifi](https://www.hubifi.com/blog/breakage-gift-card-revenue) |
| 美国 loyalty 欺诈年损失 | ~$3.1B/yr | [Loyalty Security Association via DataDome](https://datadome.co/learning-center/loyalty-fraud/) |
| 北美区域营收占比 | 36.5% | [Grand View Research](https://www.grandviewresearch.com/industry-analysis/loyalty-management-market-report) |
| 亚太区域占比 | 31.3% | 同上 |

---

## §3 全球 Top 公司图谱

### 3.1 美国（信用卡 + 航空 + 零售联盟）

| 公司 | 类型 | 核心数据 | 来源 |
|------|------|---------|------|
| **American Express Membership Rewards** | 银行信用卡可转移积分 | FY2024 营收 $66B (+9% YoY)，奖励支出反映在 $47.9B 总支出中 | [Amex 10-K](https://www.sec.gov/Archives/edgar/data/4962/000000496225000016/axp-20241231.htm) |
| **Chase Ultimate Rewards** | 银行可转移积分 | JPMC 卡服务部嵌入披露 | [JPMC](https://www.jpmorganchase.com/ir/annual-report) |
| **Citi ThankYou** | 银行积分 | 2026-05-16 起停止账户间互转 | [Citi FAQ](https://www.citi.com/credit-cards/money-management/citi-thankyou-rewards-faqs) |
| **Capital One Miles** | 银行可转移里程 | FY2024 ~$53.9B；FY2025 后并入 Discover ~$69B | [Capital One IR](https://ir-capitalone.gcs-web.com/financial-results/annual-reports/) |
| **Delta SkyMiles** | 航空里程 | **全球 #1 估值 $31B**（On Point Loyalty 2026）；2024 Amex 合作金额 **$7.4B**；premium+loyalty = Q3 营收 57% | [On Point Loyalty 2026](https://www.prnewswire.com/news-releases/deltas-skymiles-ranked-worlds-most-valuable-airline-loyalty-program-at-31-billion-302729276.html) |
| **United MileagePlus** | 航空里程 | 2020 内部估值 **$22B at 12× EBITDA**；2019 里程销售 $5.3B、EBITDA $1.8B（航空公司总营收的 12%、利润率 34%） | [Skift](https://skift.com/2020/06/15/how-is-united-airlines-loyalty-program-worth-22-billion/) |
| **American AAdvantage** | 全球首个 FFP (1981) | 估值 ~$26-30B（多次超过 AAL 市值 <$15B）；2024 co-brand 现金 $6.1B (+17% YoY)；75% 高端舱位营收来自会员 | [AAL 2024](https://americanairlines.gcs-web.com/news-releases/news-release-details/american-airlines-reports-fourth-quarter-and-full-year-2024) |
| **Bilt Rewards** | 房租 + 抵押贷款积分 | **2026 估值 $10.75B**，融资 $250M；>200 万套住房；预计 Q1 2026 营收 ~$1B；Wells Fargo 因持卡人全额还款丧失利息收入每月 $10M，导致拆伙 | [Bilt 新闻室](https://newsroom.biltrewards.com/bilt-raises-250-million-at-over-10-billion-valuation) |
| **Awardco** | B2B 员工奖励 | Series B $165M @ >$1B（2025-05）；6M 用户、3,000 客户；2024 营收 $75.2M | [Awardco](https://www.awardco.com/newsroom/awardco-raises-165-million-surpasses-1-billion-valuation) |
| **Plenti** *(已倒闭)* | 联盟（多商家） | Amex 2015-2018 试错；合作伙伴流失（Macy's, AT&T, Hulu, Expedia, Enterprise）→ 2018-04 关闭 | [Plenti Wikipedia](https://en.wikipedia.org/wiki/Plenti) |
| **McDonald's Rewards** | 餐饮 loyalty | 2024 活跃用户 175M (+15%)；2024 系统销售贡献 **$30B (+30% YoY)**；目标 2027 年 $45B | [PYMNTS](https://www.pymnts.com/earnings/2025/mcdonalds-sees-boost-in-loyalty-amid-challenges-in-q4-earnings/) |
| **Starbucks Rewards** | 餐饮 + 浮存 | 35.5M 美国活跃；Q2 2024 客户押金负债 **$1.872B**（不付利息！）；2021 浮存利润 $155M | [Travel Marketing Insights](https://medium.com/travel-marketing-insights/the-1-8-billion-latte-how-starbucks-turned-loyalty-into-a-banking-business-fe76ae8bcd9e) |

### 3.2 加拿大

| 公司 | 数据 |
|------|------|
| **Aeroplan** | 1984 起；2019-01 由 AC/TD/CIBC/Visa 以 **CAD 2.4B** 重新收购；全球估值 #8 |
| **Air Miles** | 1992 起；2023-06 BMO 以 $160M 收购；**2026 夏天关闭，被 BMO Blue Rewards 取代**；Shell 加拿大 2026-03 离开转投 Scene+，结束 34 年合作 |
| **PC Optimum** (Loblaw) | 17M+ 会员；2024 兑换 >CAD 1B；**Q4 2024 计入 CAD 1.29 亿非现金费用** 提升兑换率假设 |
| **Scene+** (Cineplex/Scotiabank/Empire) | >10M 会员；2026-03 接入 Shell 加拿大 |

### 3.3 中国

中国市场结构与西方差异显著：**国家队 + 超级 App 主导**，少有航空里程之外的纯第三方平台。

| 公司 | 数据 |
|------|------|
| **银联 U Rewards** | 国内 45% 使用率；境外 200M+ 卡；与 IBM Research 合作的区块链跨行积分互兑试点 |
| **Alipay 集分宝** (Ant Group) | 100 集分宝 = 1 RMB 兑换；3 年有效期 |
| **京东京豆** | 100 京豆 = 1 RMB；JD Plus 付费会员（年费 ¥149）消费量是非会员的 **10×** |
| **招行掌上生活** | 2018 统一积分账户；与星巴克中国合作（2011 起）；19M 持卡人参与，累计 **1 亿杯**饮品兑换 |
| **Air China PhoenixMiles** | **>9300 万会员**（2024-11，30 周年） |
| **南航明珠俱乐部 / 东航东方万里行** | SkyTeam 联盟 |

### 3.4 日本（联盟 loyalty 最成熟市场）

| 公司 | 数据 |
|------|------|
| **T-Point / V-Point** | 2003 起，日本首个大型联盟；2024-04-22 与 SMFG V-Point 合并 |
| **Rakuten Super Points** | **>1 亿会员**；累计已发行 **>4 万亿积分**（2024）；Rakuten 集团 FY2024 营收 ¥2.3 万亿（~$15B）创纪录 |
| **Ponta** | **117.4M 会员**（2024-04）；30 万家店；40.5% 消费者覆盖率 |
| **d POINT** (NTT DOCOMO) | >9000 万会员 |
| **PayPay Points** (SoftBank) | >6000 万用户；**无过期日期**（市场独特） |

### 3.5 韩国（与日本类似的联盟生态）

| 公司 | 数据 |
|------|------|
| **OK Cashbag** (SK Planet) | 1999 起；约 3800 万订阅；6 万家商户；过期 60 个月 |
| **L.POINT** (Lotte) | ~3800-3900 万（覆盖韩国人口 70%）；45 个关联企业 |
| **CJ ONE / Olive Young** | Olive Young 自身 14M+ 活跃 loyalty 会员 |

### 3.6 英国 / 欧洲

| 公司 | 数据 |
|------|------|
| **Tesco Clubcard** | 1995 起；**2300 万家庭**（占英国 2830 万的 >80%）；**英国店内销售 82% 来自 Clubcard 会员**；FY24/25 零售调整后 OP **£28.31 亿**（+12.3% YoY） |
| **Nectar** (Sainsbury's) | >2400 万会员；500+ 合作品牌（含 Argos, Esso, BA, Amex, Uber） |
| **Avios / IAG Loyalty** | **>7000 万全球会员**；BA / Iberia / Aer Lingus / Vueling / Loganair / Qatar / Finnair 共同货币 |
| **Payback** (德国, Amex) | >2000 万；600+ 合作伙伴 |
| **Flying Blue** (法航 + 荷航) | ~3000 万；40 家伙伴航司；Point.me 评为 "world's best airline rewards program" |

### 3.7 澳洲

| 公司 | 数据 |
|------|------|
| **Qantas Frequent Flyer** | 16.4M 会员 (2024-06)；FY24 loyalty 营收 ~AUD 25 亿（占总营收 ~11%） |
| **Flybuys** | **>900 万**；Coles + Wesfarmers 各占一半；覆盖 Coles, Liquorland, Kmart, Target, Bunnings, Officeworks 等 |

### 3.8 全球酒店与航空联盟

| 类别 | 备注 |
|------|------|
| **Marriott Bonvoy** | 9,000 物业 / 140 国；**2025 年贬值后积分价值 ~$0.007**（The Points Guy 估算） |
| **World of Hyatt** | ~63M；积分价值 **~$0.018**（主要酒店中最高） |
| **Hilton Honors / IHG One** | 积分价值 $0.004-0.006 |
| **Star Alliance / Oneworld / SkyTeam** | 跨航司**赎回**通用；**直接里程互转几乎全部禁止或汇率惩罚性**；Avios 子网络是 Oneworld 内的例外 |

### 3.9 第三方积分平台（B2B 行业基础设施）

| 公司 | 商业模式 |
|------|---------|
| **Plusgrade**（前 Points.com 母公司） | 2022-06 以 $385M 收购 Points.com；2024-03 General Atlantic 入主估值 **>$2B**；250+ 旅游 / loyalty 客户；140+ 计划用户；累计 $3.5B 新营收机会 |
| **Currency Alliance** | API-first 多伙伴 loyalty SaaS；公开报价 ~2% 的积分兑换值 |
| **Loyyal**（Dubai, Hyperledger） | 与 Emirates Skywards 签 3 年生产协议；**靠去掉 token、改卖企业 SaaS 才存活** |

### 3.10 大科技公司的 Loyalty

| 公司 | 数据 |
|------|------|
| **Amazon Prime** | 美国 167.2M / 全球 >200M；FY24 会员费收入 **$44.374B (+10.4%)**；占 Amazon 营收 6.96%；会员人均消费 $1,170 vs 非会员 $570 |
| **Costco** | 76.2M 付费会员；FY24 会员费 $4.8B（占总营收 ~2%，但**贡献 65% 经营利润**）；北美续费率 >93%；2024-09 7 年来首次涨价 |
| **Microsoft Rewards** | 3 级别（Member/Silver/Gold） |
| **Sephora Beauty Insider** | >40M（美加）；3 级；80% 销售来自计划 |

### 3.11 关键失败案例：Plenti

**Plenti**（American Express, 2015-2018）是**美国最经常引用的联盟 loyalty 警示故事**：

- 2015-05-04 推出，2018-04-16 关闭
- 合作伙伴：Macy's, Direct Energy, Hulu, Nationwide, Enterprise, Expedia, Chili's
- **失败根本原因**：
  1. UI 笨拙
  2. 合作伙伴议程冲突（"放牧猫"）
  3. 现有专属计划蚕食承诺
  4. 品牌认知度低（一半消费者不熟，<50% 自称会员从未兑换）
  5. 不对称的兑换池（加油 / 杂货容易赚分，难花掉）

**对 Mycelium 的启示**：长期承诺联盟在美国市场结构上失败 — 这正是 Mycelium 提出"**临时联盟**"的核心理由。

---

## §4 经济模型与会计本质

### 4.1 积分负债（Loyalty Liability）— IFRS 15 / ASC 606

国际会计准则 IFRS 15 与美国 ASC 606 趋同要求：

- 积分 = "**material right**"，构成**独立履约义务**
- 销售点的交易价格须按**独立销售价格**（standalone selling price, SSP）分配给积分部分
- 分配给积分的部分作为**合同负债**（递延收入），仅在兑换或过期时确认为收入
- 必须估算 **breakage**（破损率）— ASC 606-10-55-48
- 披露要求：项目性质、SSP 判断、兑换率假设、合同负债余额 + 周期变化

详见 [PwC ASC 606/IFRS 15 loyalty guide](https://www.pwc.com/us/en/industries/financial-services/library/loyalty-program-managers-asc606-ifrs15.html)。

### 4.2 破损率（Breakage）行业基准

| 行业 | 典型破损率 |
|------|----------|
| Cashback 计划 | **~5%**（最低 — 现金等价、立即兑换） |
| 一般零售 / CPG | **20-30%** |
| 航空里程 / 旅行 | **>40%**（部分来源 70-85%） |
| B2B 激励 | **70-85%** |

**健康程序目标 10-20%。** 1% 的破损率误判，对 $1B 负债意味着 **$10M 损益冲击**。

**真实案例**：Loblaw（PC Optimum 母公司）2024 Q4 因兑换率假设上调，**计入 CAD 1.29 亿非现金费用** — 这是会员"参与度提升"如何在资产负债表上反噬的教科书案例。

### 4.3 Float 经济：积分 = 类银行存款

> "Starbucks 是一家咖啡馆里的银行业务"

- Starbucks 2021 年仅靠未兑换 loyalty + 礼品卡余额获得 **~$1.55 亿非应税利润**
- Q2 2024 持有 **~$18.72 亿** 客户存款负债（不付利息、无 FDIC 保险、用户无提款权）
- 美国礼品卡市场 2025：营收 **$447B**；**$23B 未使用**（43% 美国成年人持有未使用礼品卡）— 破损部分接近 **100% 利润率**

[来源](https://medium.com/travel-marketing-insights/the-1-8-billion-latte-how-starbucks-turned-loyalty-into-a-banking-business-fe76ae8bcd9e)

### 4.4 第三方平台盈利模式（Plusgrade 案例）

三条收入流：

1. **积分购买 / 充值**：会员从程序购买额外里程（Plusgrade 收 take-rate）
2. **积分兑换 / 转移**：跨程序转换；Plusgrade 赚买卖价差
3. **SaaS / 平台费**：托管能力收费

可比平台 [Currency Alliance](https://www.currencyalliance.com/) 公开收 **~2%** 的积分兑换值。

### 4.5 航空里程为何"值钱过母公司"

机制：银行（Amex/Chase/Citi/Cap One/Wells Fargo）**预付批发**里程 ~2 ¢/英里 → 航空公司兑换时按 <1 ¢ 实际成本结算 → **价差 × 规模 = 高利润、抗周期**的业务嵌入低利润、强周期的业务里。

| 公司 | 数据 |
|------|------|
| Delta | 2024：80%+ 营收与 loyalty + 高端舱产品挂钩 |
| United | 2020 MileagePlus 债务交易隐含 >$22B 估值 |
| American | AAdvantage 估值多次 ~$30B vs AAL 市值 <$15B |

[IdeaWorks 2024 Loyalty + Co-Branding 报告 (PDF)](https://ideaworkscompany.com/wp-content/uploads/2024/04/Airline-Loyalty-and-Co-Branding.pdf)

### 4.6 商家发行积分的经济激励：CAC vs LTV

| 数据 | 来源 |
|------|------|
| +5% 客户保留 = +25-95% 利润 | Harvard Business School |
| 推荐客户 +25% 利润率 | Wharton |
| 行业基准 LTV:CAC ≥ 3:1 | 通用 |
| 平均消费者拥有 **19 个**程序 | Bond Loyalty Report 2024 |
| 80% 消费者会从有 loyalty 计划的品牌更频繁购买 | 通用 |
| 顶级程序提升兑换者营收 **15-25%** 年化 | McKinsey |
| 高度个性化程序提升购买 **+110%**、消费 **+40%** | BCG |

来源：[McKinsey](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/customer-experience-and-loyalty)、[BCG](https://www.bcg.com/publications/2024/loyalty-programs-customer-expectations-growing)、[Bond](https://info.bondbrandloyalty.com/the-loyalty-report-2024-press-release)

---

## §5 用户和商家的痛点

### 5.1 用户侧痛点

**单方面贬值** — CFPB 2024 年 5 月 Issue Spotlight + 12 月 Circular 2024-07 明确针对：
- 营销宣传 vs 实际可获奖励的落差
- 隐藏的"小字条款"使促销变 "bait-and-switch"
- 关账户时撤销已赚奖励无通知
- 给首选兑换方式设置障碍（如取消 statement-credit 兑换）

CFPB 已报告**奖励投诉数量暴增**。[CFPB Issue Spotlight 2024-05 PDF](https://files.consumerfinance.gov/f/documents/cfpb_credit-card-rewards_issue-spotlight_2024-05.pdf)

**跨程序摩擦**：除 Avios 子网络和少数银行 → 航司转移路径外，绝大多数跨航司里程转移都会被拒或汇率惩罚性。

**过期焦虑**：Bond Loyalty Report 第一大投诉是"赚取奖励耗时太长"（约 50% 受访者）。

**欺诈**：每年 ~$3.1B 美国 loyalty 偷盗损失；72% 的程序遭遇过盗窃 / 欺诈；2024 年同比 +89%（部分研究）。loyalty 欺诈是 2024 第 4 大增长最快的欺诈类型。[EY Loyalty Fraud 白皮书](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-ca/insights/financial-services/documents/ey-designed-loyalty-fraud-whitepaper-sw.pdf)

### 5.2 商家侧痛点

**会员参与度 → 负债膨胀**：PC Optimum CAD $129M 费用就是写实标本。这是商家不愿大量发行积分的隐形天花板。

**联盟协调失败**：Plenti 2018 案例已成警示故事。美国市场结构（强专属计划 + 弱联盟传统）使联盟尤其难。

**Co-brand 银行盈利压力**：Wells Fargo-Bilt 每月 $10M 亏损因为持卡人全额还款 — 银行原以利息为生的模式被高净值用户的"免息融资"行为颠覆。

**数据孤岛**：每个发行方持有自己的会员数据；跨程序洞察须通过 Plusgrade 类经纪人或昂贵数据合作（带反垄断关注）。

**监管收紧**：CFPB Circular 2024-07 把 UDAAP 风险摆到任何含有"小字条款 + 突然贬值 + 撤销"程序面前。澳大利亚 ACCC 也在 Flybuys 披露上同样积极。

**Escheatment（未认领财产法）**：美国部分州，礼品卡余额最终须上缴州府 — 限制"100% 破损利润"的下限。

### 5.3 行业系统性问题

- **过度饱和**：人均 19 个程序，仅一小部分活跃使用
- **个性化缺口**：71% 消费者期望个性化，仅 22% 品牌做到（McKinsey）
- **货币过剩**：全球 ~$360B 未兑换；部分行业来源估全部未结余值高达 $48 万亿（**此数字方法学不透明，建议视为数量级估计**）
- **信任赤字**：CFPB 2024 工作 + 病毒式贬值事件（Marriott Bonvoy 2024-25, Delta SkyMiles 2023, Hyatt 周期性图表变更）共同强化"发行方可任意改写规则"的认知

---

## §6 各国法规深度对比

> **核心边界问题**：积分什么时候**变成了货币 / 支付工具 / e-money / 受支付机构监管**？
> 全球答案的统一最小公约数：**对价 + 跨第三方流通 + 可换现 + 二级市场交易**，4 个维度任意一个跨线就触发监管。

### 6.1 中国（最严的司法辖区之一）

**核心法规**（按时间序）：

| 法规 | 颁布机构 | 时间 | 核心规定 |
|------|---------|------|---------|
| **单用途商业预付卡管理办法（试行）** [MOFCOM Order No. 9](https://www.gov.cn/gongbao/content/2012/content_2292065.htm) | 商务部 | 2012-09-21 颁布 / 2012-11-01 生效 / 2016-08 修订 | **三类备案**（集团/品牌/规模）；**不记名卡 ≥ 3 年有效期**；**记名卡不得有过期日**；**资金托管 20-40%**；面值上限 RMB 1,000-5,000；**禁止跨第三方结算** |
| **非金融机构支付服务管理办法** [PBOC Order [2010] No. 2](https://www.gov.cn/gongbao/content/2010/content_1730706.htm) | PBOC | 2010-09-01 生效 | 区分单用途（商务部）vs 多用途（PBOC）预付卡 |
| **非银行支付机构监督管理条例** [State Council Decree No. 768](https://www.gov.cn/zhengce/content/202312/content_6920724.htm) | 国务院 | 2023-12 颁布 / **2024-05-01 生效** | 重新分类为**储值账户运营 I/II + 支付交易处理 I/II**；预付卡 → 储值账户运营 II；基本资本 RMB 1 亿；**不得向用户支付利息** |
| **客户备付金存管办法** [PBOC Order [2021] No. 1](https://www.pbc.gov.cn/tiaofasi/144941/144957/4168458/index.html) | PBOC | 2021-03-01 生效 | **100% 客户备付金须存入 PBOC 或合格商业银行**；禁止挪用 / 质押 |
| **反洗钱法（2024 修订）** | 全国人大常委会 | **2025-01-01 生效** | 引入"其他犯罪"兜底；金融 + 特定非金融机构（含支付机构）须核实**受益所有人**；配套 [PBOC/NFRA/CSRC Order [2025] No. 11](https://jrj.sh.gov.cn/YWTBZCCX166/20251201/18143bfe9fd14a36b3bc422a2895d593.html) **2026-01-01 生效** |

**PBOC 关于"积分换购"的事实立场**（无单一规则，从执法 + 公告推断）：
- 纯无偿积分仅在发行方内部使用 → 支付服务法之外
- 一旦满足以下任一项 → 视为多用途预付价值，触发 Decree 768：
  - (a) 跨非关联商家自由转让
  - (b) 现金购买
  - (c) 现金兑回
  - (d) 用于第三方义务清偿
- **PBOC 银发〔2017〕281 号** 明确警告"积分变现"和借积分变相支付

**关于区块链积分（中国大陆）**：**没有豁免**。
- 2017 ICO 禁令（PBOC + 6 部委 2017-09-04 公告）+ 2021 加密币 10 部门联合通知（2021-09-15）将"任何可换法币或用于支付的代币"视为非法支付服务
- **代币形式的积分必须**：(i) 不可交易、(ii) 不可换法币、(iii) 仅在发行方关联商家网络内使用

### 6.2 美国（监管中等强度，CFPB 最近收紧）

**核心法规**：

| 法规 | 机构 | 时间 / 核心规定 |
|------|------|----------------|
| **FTC §5** [15 U.S.C. § 45](https://www.law.cornell.edu/uscode/text/15/45) | FTC | 不公平 / 欺诈做法。无单一 loyalty 规则，但执法集中于贬值、隐藏限制、"doom-loop" 兑换摩擦 |
| **CFPB Circular 2024-07** [全文](https://www.consumerfinance.gov/compliance/circulars/consumer-financial-protection-circular-2024-07-design-marketing-and-administration-of-credit-card-rewards-programs/) | CFPB | **2024-12-18** 发布。法律基础 CFPA 12 U.S.C. § 5531(a) + § 5536(a)(1)(B) (UDAAP)。立场："小字免责或合同条款给运营方调整奖励的权利往往不足以纠正消费者的总体印象" |
| **CARD Act 2009** Pub. L. 111-24 | 国会 | 15 U.S.C. § 1637(i)：账户条款"重大变更"前 45 天通知。**但 CARD Act 不定义"奖励积分"为受保护账户条款** — Circular 2024-07 用 UDAAP 闭合此口子 |
| **ASC 606 / IFRS 15** | FASB | 积分 = "material right" 独立履约义务；分配 SSP 后递延为合同负债；估算 breakage |
| **31 CFR § 1010.100** [FinCEN BSA 预付访问规则](https://www.fincen.gov/resources/statutes-regulations/guidance/final-rule-definitions-and-other-regulations-relating) | FinCEN | "**Closed-loop prepaid access**"（仅在指定商家使用）**MSB 排除**，前提日加载 ≤ **$2,000**；销售方每日 > $10,000 给一人须 AML |

**各州 escheat（未认领财产）法**：
- **加州** [Civil Code § 1749.5](https://codes.findlaw.com/ca/civil-code/civ-sect-1749-5/)：礼品凭证不得过期；**忠诚 / 促销凭证（无对价）豁免**
- **得州** Property Code §72.1016：储值卡推定弃置 = 过期或第 3 周年；**忠诚卡豁免**
- **纽约** Abandoned Property Law §1315 / §1316：5 年弃置；忠诚卡通常主张在外但州审计常挑战
- **NAUPA 模型法**：5 年休眠期

### 6.3 欧盟 / 英国

**核心法规**：

| 法规 | 机构 | 核心规定 |
|------|------|---------|
| **PSD2** [Directive (EU) 2015/2366](https://eur-lex.europa.eu/eli/dir/2015/2366/oj/eng) | EU | **Article 3(k)** "Limited Network Exclusion (LNE)"：限于发行方 / 有限服务提供方网络 / 非常有限商品范围内的支付工具排除适用。**Art. 37(2)：12 个月超过 EUR 1M 须通报** |
| **EBA/GL/2022/02** [全文](https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-final-guidelines-limited-network-exclusion) | EBA | 2022-06-01 适用。7 条 LNE 评估指引。BaFin 立场：多商家忠诚度（Payback、Lufthansa Miles & More）只在通报且网络保持"有限"时在 LNE；**若可换现 → 成为 EMD2 e-money** |
| **EMD2** [Directive 2009/110/EC](https://eur-lex.europa.eu/eli/dir/2009/110/oj) | EU | E-money = 因接收资金而发行的支付电子价值。积分**满足三者**（因资金发行 + 支付意图 + 第三方接受）→ **触发 EMI 牌照** |
| **GDPR** [Regulation 2016/679](https://gdpr-info.eu/) | EU | Art. 22 禁止仅自动化决策 — 影响 loyalty 等级算法 + 动态定价；**EDPB Guidelines 1/2024**：忠诚度营销分析通常需要同意，不是合法利益 |
| **MiCA** [Regulation 2023/1114](https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng) | EU | 2024-12-30 全面适用。**Art. 4(3) 例外**：(c) 效用代币提供现有商品/服务访问，(d) 仅在有合同协议的有限商家网络内使用 — 可豁免白皮书 |
| **AML Reg 2024/1624** | EU | 2027-07 适用。**匿名预付 e-money 上限**（店内 EUR 150，在线 EUR 50） |

**英国**：
- Payment Services Regulations 2017 (SI 2017/752)：实施 PSD2，同 LNE 措辞
- E-Money Regulations 2011 (SI 2011/99)：EMI 授权
- [FCA PERG 15](https://handbook.fca.org.uk/handbook/PERG/15/3.html) 边界指引
- 英国未采纳 MiCA，正开发自己的加密制度

### 6.4 日本（PSA 框架清晰，对价是核心边界）

| 法规 | 核心规定 |
|------|---------|
| **資金決済法（PSA）** [英文](https://www.japaneselawtranslation.go.jp/en/laws/view/3965/en) | **Article 3** 4 个累积要件定义"前払式支払手段"：(1) 价值/数量记录、(2) **以対価发行**、(3) 凭证发行、(4) 可赎回。**关键边界：无偿发行积分（景品/おまけ）缺对価要件 → PSA 范围之外**。付费充值/购买 = PPI |
| **自家型 vs 第三者型** | 自家型（仅发行方使用）：未偿余额首次超 JPY 10M 时**通报**财务局；第三者型（与第三方商家使用）：**注册要求** + 资本 + 合规体系 |
| **担保金 (Art. 14)** | 未偿 > JPY 10M → **至少 50% 担保金**于法务局，或等价信托/银行担保 |
| **6 个月规则** | 有效期 ≤ 6 个月 → PSA 未偿/担保金规则**不适用**。许多公司设计**滚动 6 个月过期**忠诚度产品 |

[Japan Payment Service Association FAQ](https://www.s-kessai.jp/businesses/prepaid_means_overview.html)：FSA 一贯认为无偿积分非 PPI；但若积分可购买/转让/换 PPI → 对価重新附着 → PPI 注册触发

### 6.5 韩国（2024 改革后非常严格）

[전자금융거래법 (EFTA)](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=140289) **2023-09-14 签署，2024-09-15 生效的修正**：

1. **100% 隔离管理客户预付款**（最初 50%，最终 100%）
2. 隔离资金仅限银行存款、韩国国债、地方政府债券、邮政存款
3. **折扣 / 奖励发行限制**：仅在债务/股权比 ≤ 200% 时可提供
4. 货币利益金额（折扣 + 奖励）须计入隔离资金计算
5. 范围扩大：原豁免的小量服务商纳入 EFTA

**对忠诚度立场**：
- 无偿累积里程在 EFTA 范围之外
- 购买 / 可转让 / 可换现里程 → EFTA 范围内 → 注册要求
- 2024 改革针对"쿠팡 캐시"等电商平台积分扩大范围

### 6.6 新加坡（最友好之一）

[Payment Services Act 2019 (PS Act)](https://sso.agc.gov.sg/act/psa2019)

**MAS 权威立场**（[MAS 官方 Q&A](https://ask.gov.sg/mas/questions/clx8ktis400bzryozdeghrztg)）：

> "MAS does not intend for loyalty programmes that are common in the retail space to be regulated as payment services."

忠诚度积分可能是：
- "Limited purpose e-money"（PS Act, Part 3 / 第一附表 Part 1）
- "Limited purpose digital payment token"

**结果：相关支付服务不受规管**。

MAS 评估要素：营销定位、是否冲突 loyalty 目标、范围真正有限。

### 6.7 香港（最友好之二）

[Cap. 584](https://www.elegislation.gov.hk/hk/cap584)（2015-11-13 生效）

**Schedule 8 类豁免** — 忠诚度 / 奖励积分豁免：

- **Schedule 8(3)** — 奖励积分计划：仅存储**积分或单位**，**不可兑现金**的 SVF
- HKMA 指引明确举例：航空里程计划、零售商客户忠诚度计划
- Schedule 8(4) — 单一发行方某些现金奖励
- Schedule 8(5) — 特定商家的单一用途 SVF

**HKMA 关于区块链忠诚度立场**：Schedule 8 豁免**不论底层技术**，前提是不可换现金 + 有限用途。**2024 e-HKD 试点 Phase 2** 含代币化忠诚度 / 商家折扣作为合法"可编程货币"用例。

**注意**：[稳定币条例](https://www.elegislation.gov.hk/hk/cap656)（**2025-08-01 生效**）将法币锚定稳定币 + 任何作为稳定值支付工具营销的代币纳入 HKMA 牌照。

### 6.8 边界问题综合表

| 行为 | 中国 | 美国 | 欧盟/英国 | 日本 | 韩国 | 新加坡 | 香港 |
|------|------|------|----------|------|------|--------|------|
| 无偿发行 + 仅发行方使用 | ✅ 安全 | ✅ 安全 | ✅ LNE | ✅ 无对価非 PPI | ✅ 安全 | ✅ Limited Purpose | ✅ Schedule 8 |
| 跨第三方商家流通 | ⚠️ 多用途 → 牌照 | ⚠️ MSB 风险 | ⚠️ EMD2 风险 | 🚨 第三者型注册 | 🚨 EFTA 注册 | ⚠️ MPI/SPI 牌照 | ⚠️ 完整 SVF |
| 现金购买 / 兑回 | 🚨 支付牌照 | 🚨 MTL + MSB | 🚨 EMD2 | 🚨 完整 PSA | 🚨 完整 EFTA | 🚨 MPI | 🚨 完整 SVF |
| 二级市场可交易 | 🚨 ICO 禁令 | 🚨 SEC Howey | 🚨 MiCA ART/EMT | 🚨 PSA + 加密资产法 | 🚨 加密资产法 | 🚨 DPT 牌照 | 🚨 稳定币条例 |

> **统一规则**：保持 (a) 无对价 + (b) 闭环商家网络 + (c) 不可现金兑回 + (d) 无二级市场交易 — 全球范围内通常豁免支付服务监管。**任何一条破坏都会触发牌照要求**。

---

## §7 区块链 + AI 的可能性

### 7.1 已有 Web3 积分项目盘点（2018-2026）

#### 企业区块链 Loyalty（B2B SaaS, 许可链）

| 项目 | 状态 | 教训 |
|------|------|------|
| **[Loyyal](https://loyyal.com/)**（US/UAE, Hyperledger） | **活，已转型**。与 Emirates Skywards 3 年生产协议（2020-02），报告 80% 交易节省 + 30% 对账成本削减 | **去掉 token 才存活**，专注企业 SLA + 对账，**不是去中心化** |
| **Singapore Airlines KrisPay** (Microsoft + KPMG, 2018) | 被 Kris+ 吸收（活，不再营销为"区块链"） | 区块链成为不可见管道 |
| **Cathay Pacific Asia Miles + Accenture** (2018) | 一次性营销活动 | |
| **American Express + Hyperledger + Boxed** (2018) | 安静 PoC，非产品 | |
| **[IBM Customer Loyalty Program](https://github.com/IBM/customer-loyalty-program)** | **死/归档**（2019-05） | 大厂参考项目随战略变更而死 |

#### 公开 Token Loyalty 币

| 项目 | 状态 |
|------|------|
| **[Qiibee (QBX)](https://qiibeefoundation.org/token-utilities/)** | **僵尸**。ATH Jan 2025 ~$0.047，现 $0.001-0.004。瑞士；试图做"loyalty L1"，被冷启动问题阻滞 |
| **Lympo (LMT)** | **死**。Animoca Brands 子公司；2022-01-10 热钱包被黑 165.2M LMT (~$18.7M)，价崩 92% [Cointelegraph](https://cointelegraph.com/news/animoca-brands-lympo-nft-platform-hacked-for-18-7-million) |
| **Boba Network (BOBA)** | **活，已转型**。500M 全解锁 2025-06；现定位"AI L2"，不再是 loyalty |
| **Momentum Protocol / SoLoyal** | **死** |

#### Web3 任务 / Loyalty-as-Marketing 平台

| 项目 | 状态 |
|------|------|
| **[Galxe](https://www.galxe.com/)** | **类目最大**。34M+ 用户，1.2B+ 任务，6,700+ 合作伙伴；Galxe Passport SBT 身份层 |
| **Layer3 (L3)** | **活但 tokenomics 困难**。FDV ~$34.8M (2026-04) |
| **Crew3 → Zealy** | 2023 中改名转型 Web2 |

#### 大牌 Web3 Loyalty 实验（96% 失败率）

| 项目 | 状态 |
|------|------|
| **Starbucks Odyssey** | **2024-03 关闭**，~18 月后。NFT 市场崩 + 复杂度过高 + 消费者疲劳 |
| **Nike RTFKT** | **死**。2025-01 Web3 服务结束；2025-12 Nike 出售品牌；CryptoKick 从 ~$8,000 崩到 ~$16 |
| **Adidas (ALTS)** | 活 |
| NFT loyalty 整体 | Q1 2025 同比 -63%（$4.1B → $1.5B），96% 项目"死" |

#### 信用卡 / Fintech 邻近

| 项目 | 状态 |
|------|------|
| **Bilt Rewards** | **活，$10.75B 估值**。但 loyalty 货币**非链上**；Raise Network 选 Solana 做 SmartCard 是邻近故事 |
| **Crypto.com Visa / Coinbase One Card / Nexo Card** | 活，加密返还 |
| **Flexa SPEDN** | **2026-03-31 关闭** 7 年消费者 app，转纯 B2B 商家基础设施 |

#### DePIN（硬件运营者的 Loyalty）

| 项目 | 关键数据 |
|------|---------|
| **Helium** | 63,806 活跃热点（Q1 2025）；需求侧瓶颈 |
| **Hivemapper / Bee Maps** | $32M Pantera 主投融资 |
| **IoTeX** | DePIN 专用 L1 |

**DePIN 教训对 Mycelium 至关重要**：网络在**需求瓶颈**而非供应瓶颈处停滞。"Mycelium 需要第一天的需求侧吸引，不仅是商家供应"。

### 7.2 关键技术方案

#### ERC-20 vs ERC-1155 用于积分

| 维度 | ERC-20 | ERC-1155 |
|------|--------|----------|
| **可替代积分契合度** | 原生契合 | 可工作但增加复杂度 |
| **多商家单合约** | 每商家一合约 | **一合约托管多商家积分**（每个 tokenId = 一个商家）— 联盟的 gas/UX 大胜 |
| **批量转账** | 一次一个 | 原生 `safeBatchTransferFrom` |
| **DeFi 可组合性** | 最佳 | 有限 |

**Mycelium 实践模式**：每商家 ERC-20 wrapper 用于 DeFi 可组合性 + ERC-1155"联盟账本"用于联盟内批量兑换。

#### 跨链多商家互操作

- **IBC (Cosmos)**：117 链（2024-10）— 主权链联盟最成熟
- **LayerZero**：93 链
- **Circle CCTP**：活跃地址领先
- **Merkle 证明 / claim 树**：标准模式

#### 隐私（购买记录是否上链？）

**2025 强共识：不**。Loyalty 应用现用 ZK 证明验证"客户做了合格购买"而不披露交易元数据。

- ZK 证明市场：$75M (2024) → $10B+ (2030)
- 实践模式：仅承诺哈希上链，原始购买数据在加密链下数据库
- [BIS Working Paper No. 1242](https://www.bis.org/publ/work1242.pdf)：数字货币的隐私增强技术

#### Gas 抽象（ERC-4337 Paymasters）

- 账户抽象采用：40M+ 智能账户（2023-03 起），100M+ 用户操作
- Paymasters 可赞助 gas 或让用户用 ERC-20（USDC、品牌代币、**或商家积分**）付 gas
- **风险**：[OtterSec 2025-12 审计](https://osec.io/blog/2025-12-02-paymasters-evm/) 揭示 paymaster 合约有隐藏 DoS、replay、gas 鞭笞向量
- 参考实现：[Pimlico ERC20 paymaster](https://github.com/pimlicolabs/erc20-paymaster), Circle Paymaster, **AAStar SuperPaymaster**（与 Mycelium 同生态）

#### 反 Sybil / 反欺诈

- **[Human Passport](https://human.tech/blog/human-passport-proof-of-personhood-and-sybil-resistance-for-web3)**（前 Gitcoin Passport）：守卫 9 轮 Gitcoin Grant；攻击者影响降 80%+
- **World ID**：生物 Orb 扫描 + ZK 证明
- **[TrustaLabs](https://github.com/TrustaLabs/Airdrop-Sybil-Identification)**：开源 ML Sybil 框架

### 7.3 区块链能解决什么 / 不能解决什么

**区块链能解决**：

✅ **跨商家联盟清算**（Loyyal-Emirates 80% 节省案例验证）
✅ **反单方面贬值**（合约可固化兑换规则，CFPB UDAAP 风险消除）
✅ **商家欺诈检测**（链上可审计）
✅ **数据主权**（用户拥有积分而非寄存在商家）
✅ **联盟自组织**（智能合约定义 alliance lifecycle）
✅ **Gas 抽象消除入门门槛**

**区块链不能解决**：

❌ **"用户对品牌不信任"本身**（这是品牌问题，不是技术问题）
❌ **冷启动需求侧**（Plenti/Qiibee 都死在这里）
❌ **自动符合 KYC/AML**（仍需链下身份层）
❌ **诱发购买行为**（积分本身不创造需求，只放大已有需求）

---

## §8 AI 在积分领域的杀手用例

### 市场规模

- Loyalty management 市场：$12.89B (2025) → $20.36B (2030)，9.6% CAGR
- AI in eCommerce：$7.57B (2024) → $8.65B (2025)，14.6% CAGR

### 真实案例数据

| 案例 | 数据 |
|------|------|
| **Albertsons (杂货)** | AI 主导的 loyalty 重设计 2024 → 会员 +15% 至 44.3M |
| **Starbucks Rewards** | AI offer 引擎早 2024 多 4M 访问，活跃成员 +13% |
| **行业 ROI** | 90% 的 AI loyalty 程序报告正 ROI；平均 4.9×；顶级 7.2× |
| **个性化提升** | 高度个性化程序提升购买 +110%、消费 +40%（BCG） |

### Mycelium 视角的 AI 杀手用例

**不是个性化**（个性化是入门券）—**是中小商家从未拥有过的"每商家发行率优化"**：

> "我是面包店，我的最优积分/美元比是什么？"

几乎没有 SMB 今天有这种能力。把 Albertsons / Starbucks 级的优化能力开放给 200 客户的小面包店 — 这是 Mycelium 真正可以差异化的产品点。

辅助 AI 用例：
- 跨联盟自动清算（Loyyal-Emirates 80% 对账成本削减）
- 欺诈检测（ML > 规则在新攻击上）
- 个性化兑换推荐（提升使用率）

---

## §9 三个核心论断

### 9.1 商家为什么需要积分？解决了什么核心问题？

**直接答案**：积分是**营销 / 财务杠杆 / 数据采集**三合一工具。

**底层经济学**：
- HBS：+5% 客户保留 = +25-95% 利润
- 客户获取成本 (CAC) 远高于现有客户的复购成本
- 积分将"未来折扣"换成"今天的现金流 + 锁客 + 数据"
- **本质上：积分是商家用 surplus capacity（剩余库存 / 闲置产能 / 边际成本接近零的服务）换取流动性的工具**

**三层价值**：

| 层 | 商家收益 | 真实数据 |
|----|---------|---------|
| **L1 营销** | 提升复购、客单价 | 80% 消费者从有 loyalty 计划的品牌更频繁购买 |
| **L2 财务** | 0 利率浮存金 + 破损率利润 | Starbucks 持有 $1.872B 客户押金不付利息；2021 浮存利润 $1.55 亿 |
| **L3 数据** | 用户行为数据资产 | Tesco Clubcard 82% 英国店内销售来自会员 — 这等于完整的购物画像 |

**为什么航空 / 信用卡是终极玩家**：
- 银行预付批发里程 ~2 ¢/英里 → 航空兑换实际成本 <1 ¢
- 价差 × 规模 = 高利润、抗周期业务嵌入低利润周期业务
- Delta 2024 年 80%+ 营收与 loyalty + premium 挂钩
- **航空里程的资本化估值多次超过母航空公司本身**

> **核心问题陈述**：商家不是"为了奖励顾客"才发行积分。商家是为了把暂时无法变现的剩余产能（航空空座位、酒店空房、面包店 4 点后的剩余面包）通过未来兑换权抵押给银行 / 用户，**今天换取现金流 + 锁客 + 数据 + 浮存利润**。这是会计上"递延收入负债"的真正经济意义。

### 9.2 商业积分是不是"灰色货币"？

**是。** 但全球监管已经清晰地划出了**安全港**与**红线**。

**经济本质**：积分 = 商家发行的 closed-loop IOU（封闭式欠条）。这一定性已被监管承认：
- **美国 FinCEN 31 CFR 1010.100**：closed-loop ≤ $2,000/day 显式 MSB 豁免 — 默认承认了"如果突破闭环或上限就是货币"
- **中国 PBOC**：单用途 vs 多用途分类即"在多用途时构成支付工具"
- **欧盟 EMD2**：满足三要素（资金发行 + 支付意图 + 第三方接受）→ 触发 e-money 牌照
- **日本 PSA**：核心要件是"対価"（consideration）— 一旦从无偿变成有偿 → 触发 PPI 注册

**全球统一边界（4 道红线，跨任意一条 → 触发牌照）**：

| 维度 | 安全港 | 红线 |
|------|-------|------|
| **对价** | 无偿赠予 | 现金购买 / 充值 |
| **流通范围** | 仅发行方 + 合同关联团体 | 跨非关联第三方流通 |
| **现金兑换** | 仅可换商品/服务 | 可换法币 |
| **二级市场** | 不可转让（或仅在白名单内） | AMM / 交易所交易 |

**历史教训**：
- 中国 2017 ICO 禁令 + 2021 加密币 10 部门联合通知明确："任何可换法币或用于第三方支付的代币 = 非法支付服务"。这关闭了任何尝试"积分代币 + 二级市场"的路径
- 美国 SEC + CFTC 2026-03 联合框架：loyalty 积分仅在*通过消费获得*而非*作为投资购买*时排除证券分类
- 韩国 EFTA 2024 修正：100% 备付金 — 把"小公司游戏"变成大资本玩法

**对 Mycelium 的直接含义**：
- **不能上 AMM**
- **不能允许法币购买积分**
- **不能允许积分自由转让到联盟外**
- **必须设置每商家每日发行 / 兑换硬上限**（保持低于 FinCEN $2,000/day 阈值）

> **结论性陈述**：商业积分的"灰色"不是法律灰色 — 全球监管已经清楚地说明了什么时候它构成货币（有偿 + 多商家 + 可换现 + 二级交易）什么时候是营销工具。**真正的灰色是大多数中小商家不知道这条线在哪，更不知道自己在哪侧**。Mycelium 提供合规化的积分协议 = 把这条线嵌入到协议里，让商家自动在安全港一侧。

### 9.3 Mycelium 自组织积分联盟的合规设计与可行性

**我们的设计**（继承自既有 Mycelium 架构）：
- **OpenPNTs** ERC-20 兼容的中小商业组织积分协议
- **SuperPaymaster** ERC-4337 gasless（让用户免 gas 用积分）
- **临时联盟智能合约**（面包店 + 宾馆 + 旅行社可为某活动临时组成联盟）
- **iDoris AI** 帮商家分析最优发行率、识别欺诈
- **隐私优先**（不上传用户身份和购买细节，ZK 证明）

**全球先例分析**：

| 我们想做的 | 最近先例 | 结果 | 启示 |
|----------|---------|------|------|
| 开放协议 + 无许可商家加入 | Qiibee | 僵尸（无需求侧）| 分发 > 技术 |
| 多商家联盟 + 临时形成 | Plenti | 失败（中心化 + 永久伙伴）| **临时联盟避免长期承诺问题，方向正确** |
| Gasless UX via paymaster | Circle Paymaster | 活（USDC），尚未应用于 loyalty | 可行但需谨慎审计 |
| AI 驱动发行优化 | Albertsons / Starbucks（闭源）| 内部强 ROI | **从未作为开放服务给 SMB — 我们的差异点** |
| 区块链上联盟对账 | Loyyal-Emirates | 80% 对账节省 | 必须有 boring B2B 销售面 |
| Privacy-first via ZK | 学术理论 | 尚未为 loyalty 产品化 | 我们可以是第一个 |

**结论**：**Mycelium 提议的精确组合（开放协议 + 临时联盟 + gasless + AI 优化器 + 隐私优先 + 服务于 SMB）没有直接先例**。

**最大风险**：

法律：
1. **证券分类（Howey）**：代币有二级市场价格 → SEC 风险
2. **货币转账（MSB）**：跨商家可转让 → MSB 牌照触发
3. **EU MiCA**：自由交易代币 → ART/EMT 分类
4. **GDPR Art. 22**：AI 推断用户行为 → 自动化决策暴露
5. **中国 ICO 禁令**：任何可换现 / 第三方支付 → 非法支付服务

技术：
1. **Paymaster DoS / 鞭笞**（OtterSec 2025-12 警告）
2. **跨商家清算 gas 经济**（98% loyalty earn 交易太小不能用 L1，**L2/Base/Polygon 必需**）
3. **热钱包黑客先例**（Lympo 2022 损失 $18.7M）

商业：
1. **冷启动**（Plenti / Qiibee 都死在这里）
2. **负债会计**（IFRS 15 / ASC 606 让小商家头疼）
3. **品牌忠诚度普遍下降**（Forrester 2025 预测 -25%）

**8 道合规护城河（必须以协议级强制执行）**：

| # | 设计 | 解决的风险 |
|---|------|----------|
| 1 | **将积分定义为服务凭证（service voucher），非货币** | FinCEN closed-loop 豁免 / SEC Howey / 中国 ICO 禁令 |
| 2 | **每商家每日发行 + 兑换硬上限**（< $2,000/day） | FinCEN MSB 阈值 / 中国预付卡面值上限 |
| 3 | **代币默认不可转让（兑换前 soulbound），无 AMM 上市** | SEC "通过消费获得"豁免 / MiCA Art. 4(3) 例外 |
| 4 | **真实 SKU 兑付能力，会计计入递延收入义务** | IFRS 15 合规 / 防"庞氏积分" |
| 5 | **过期 + breakage 政策**（标准会计） | 防止永久浮存看似"存款" |
| 6 | **Privacy-by-default**（ZK 证明 + 链上无 PII） | GDPR Art. 22 / BIS 隐私推荐 |
| 7 | **协议开源 + AI 商业化封闭** | 监管友好"基础设施"框架 + 商业护城河 |
| 8 | **司法管辖友好基地**：Wyoming DAO LLC / 香港 / 新加坡 / UAE DIFC | 避开中美严监管 |

**起步司法管辖建议**：

| 司法辖区 | 法律风险 | 启动难度 | 推荐顺序 |
|----------|---------|---------|---------|
| 香港 | 低（Schedule 8 loyalty 豁免） | 低 | **#1 推荐** |
| 新加坡 | 低（MAS Limited Purpose） | 低 | **#2 推荐** |
| UAE DIFC | 低（创新执照） | 中 | #3 |
| 美国 (Wyoming) | 中（CFPB UDAAP + 各州 escheat） | 中 | #4 |
| 日本 | 中（PSA 第三者型注册） | 高 | #5 |
| 欧盟 | 中（PSD2 LNE EUR 1M 阈值） | 中 | #6 |
| 韩国 | 高（EFTA 2024 100% 备付金） | 高 | #7 |
| 中国大陆 | **极高**（PBOC 2017 ICO + 2021 加密币禁令） | 极高 | **不推荐起步** |

---

## §10 风险评估与建议

### 10.1 起步建议

**第一阶段（M1-M3）**：
- **司法管辖**：香港 / 新加坡注册（[Cap. 584 Schedule 8](https://www.elegislation.gov.hk/hk/cap584) / [MAS PS Act Limited Purpose](https://ask.gov.sg/mas/questions/clx8ktis400bzryozdeghrztg)）
- **技术栈**：OP Stack L2 + ERC-4337 + ERC-1155 联盟账本 + ZK 兑换证明
- **首批商家**：找 1-2 家高客流 SMB（咖啡店连锁 / 城市民宿群）作为种子节点
- **AI 卖点**：让普通面包店能用上 Albertsons / Starbucks 级的发行优化
- **绝对不做**：AMM 上市 / 投机性二级市场 / 邀请中国大陆用户参与早期

**第二阶段（M4-M9）**：
- 第一个 2-3 商家临时联盟（试点）— 比如咖啡店 + 健身房在节假日联合营销
- 联盟智能合约模板开源
- iDoris AI 发行率优化器 MVP

**第三阶段（M10-M18）**：
- 跨地区扩张（东南亚 → 日本 → 欧盟）
- 联盟 marketplace（自发现 / 自组织）
- 与 Loyyal 类企业链对接（B2B 通道）

### 10.2 关键不确定性

1. **商家数据可信度**：商家自报的"剩余库存"如何上链？需要 SKU oracle
2. **用户冷启动**：Plenti/Qiibee 都死在这里 — 我们怎么破？
3. **AI 优化器实际效果**：Albertsons 案例是闭源企业级；中小商家数据稀疏，AI 是否仍然有效？
4. **法规快速变化**：2024-2026 全球都在收紧 stablecoin / e-money 监管，2 年后窗口可能关闭

### 10.3 与 Mycelium 现有产品体系的协同

| Mycelium 组件 | 在积分协议中的角色 |
|--------------|-----------------|
| **Cos72 - MyShop** | 已有 ERC-1155 积分商店合约 + Slither 审计 — 可直接复用作为联盟账本 |
| **Cos72 - MyTask** | 任务-积分桥接：商家可以把"完成 X 任务奖励 Y 积分"作为发行渠道 |
| **OpenPNTs** | ERC-20 兼容社区积分协议 — 作为 SuperPaymaster 替代 ETH 付 Gas 的工具（**关键：闭环但有用**） |
| **SuperPaymaster** | ERC-4337 gasless — 让用户**用积分本身付 gas**（关闭循环，移除 ETH 依赖）|
| **AirAccount** | TEE + WebAuthn 身份层 — 让普通用户无助记词参与 |
| **iDoris** | 本地 AI — 商家个性化发行率优化 + 欺诈检测，保护商家数据隐私 |
| **agent-speaker** | Nostr 通信层 — 联盟形成 / 解散 / 协调消息 |
| **Sin90** | 个人 OS — 用户钱包 + 积分管理界面 |
| **CometENS** | 免费子域名 — 每个商家可以是 `bakery.points.cv` |

**核心洞察**：**Mycelium 已有的所有组件凑起来就是一个完整的积分协议** — 我们不是要做新东西，是要把已有的拼成一条产品线。

---

## §11 结论与下一步

### 关键结论

1. **商业积分是一个数千亿美元的成熟行业，但商业模型本质是"商家发行的有限货币 + 财务浮存 + 数据资产"三合一**。它远不止"奖励忠诚客户"那么简单。

2. **全球监管的边界已经清晰**：无对价 + 闭环 + 不可换现 + 不可二级交易 → 安全港；任何一条破坏 → 触发支付牌照。Mycelium 设计必须以**协议级强制**保持在安全港内。

3. **Web3 积分项目的失败率 > 95%**。生存者（Loyyal）都靠"去 token 化 + B2B 卖对账"。Mycelium 必须吸取教训：**框架为"开放协议对账基础设施"而非"Web3 loyalty"**。

4. **Mycelium 的精确组合（开放协议 + 临时联盟 + gasless + AI 优化器 + 隐私优先 + 针对 SMB）没有直接先例**。这是机会也是风险。

5. **AI 的杀手用例是"每商家发行率优化"** — 不是个性化（那是入门券）。让小面包店用上 Albertsons 级能力是真正的差异化。

6. **首选起步司法管辖：香港 + 新加坡**。中国大陆不可能起步；美国 / 欧盟 / 日本中等难度；韩国高风险。

### 下一步建议

| # | 行动 | 时间 |
|---|------|------|
| **A1** | 把这份报告作为 Mycelium 内部讨论起点，征询法律意见（建议：**香港 / 新加坡持牌律师**） | 本周 |
| **A2** | 启动 OpenPNTs 公开规范文档（解决 Agent C 提到的"无公开足迹"问题） | 本月 |
| **A3** | 在 Cos72 既有 MyShop 基础上做 PoC：单商家发行积分 → SuperPaymaster gasless 兑换 → ZK 兑换证明 | 下月 |
| **A4** | 物色 1-2 家高客流 SMB 作为种子节点（建议：Mycelium 团队的本地咖啡店 / 民宿） | 下月 |
| **A5** | 写一篇 Progress-Report 类博客文章，把这份调研的关键观点公开化（SEO + 早期商家招募） | 本月内 |

### 一句话结论

> **商业积分是一个被严重低估、高度受规制、技术上可被区块链改善但已死过 95% 项目的行业。Mycelium 的临时联盟 + 服务凭证 + AI 优化的组合在原则上正确，但必须以协议级强制执行 8 道合规护城河，从香港或新加坡起步，靠为 SMB 提供 Albertsons 级的发行优化能力作为差异化卖点 — 不靠"去中心化"叙事。**

---

## §12 参考资料

### 行业数据 / 公司披露

- [American Express 2024 Annual Report (PDF)](https://s26.q4cdn.com/747928648/files/doc_financials/2024/ar/v2/American-Express-2024-Annual-Report.pdf)
- [American Express 10-K 2024 (SEC)](https://www.sec.gov/Archives/edgar/data/4962/000000496225000016/axp-20241231.htm)
- [Delta IR Q3 2024 release](https://ir.delta.com/news/news-details/2024/Delta-Air-Lines-Announces-September-Quarter-2024-Financial-Results/default.aspx)
- [American Airlines 2024 results](https://americanairlines.gcs-web.com/news-releases/news-release-details/american-airlines-reports-fourth-quarter-and-full-year-2024)
- [AAdvantage 2024 Press Release](https://news.aa.com/news/news-details/2024/The-American-Airlines-AAdvantage-program-continues-to-lead-the-travel-rewards-industry-in-2024-AADV-01/default.aspx)
- [Bilt $250M / $10.75B Raise](https://newsroom.biltrewards.com/bilt-raises-250-million-at-over-10-billion-valuation)
- [Plusgrade Closes $385M Points Acquisition](https://www.prnewswire.com/news-releases/ancillary-revenue-leader-plusgrade-completes-us385-million-acquisition-of-loyalty-commerce-platform-points-301578796.html)
- [Plusgrade General Atlantic $2B+ Deal](https://www.theglobeandmail.com/business/article-general-atlantic-buys-control-of-montreal-travel-upgrade-service/)
- [Tesco Prelim 2024/25 (PDF)](https://www.tescoplc.com/media/mxfjrk4x/tesco-plc-preliminary-results-2425-press-release.pdf)
- [Loblaw PC Optimum CAD 129M Charge](https://www.cbc.ca/news/business/loblaw-pc-optimum-redeem-points-1.7465415)
- [Qantas FY24 Results](https://www.qantasnewsroom.com.au/media-releases/qantas-group-posts-strong-result-while-delivering-for-customers-in-fy24)
- [Costco FY24 Fee Hike](https://investor.costco.com/news/news-details/2024/Costco-Wholesale-Corporation-Reports-June-Sales-Results-and-Announces-Quarterly-Cash-Dividend-and-Plans-for-Membership-Fee-Increase/default.aspx)
- [McDonald's Loyalty 175M / $30B](https://www.pymnts.com/earnings/2025/mcdonalds-sees-boost-in-loyalty-amid-challenges-in-q4-earnings/)
- [Starbucks Q1 FY24 (34.3M, $3.6B)](https://investor.starbucks.com/news/financial-releases/news-details/2024/Starbucks-Reports-Q1-Fiscal-2024-Results/default.aspx)
- [On Point Loyalty 2026 Valuations](https://www.prnewswire.com/news-releases/deltas-skymiles-ranked-worlds-most-valuable-airline-loyalty-program-at-31-billion-302729276.html)
- [IdeaWorks Airline Loyalty + Co-Branding 2024 (PDF)](https://ideaworkscompany.com/wp-content/uploads/2024/04/Airline-Loyalty-and-Co-Branding.pdf)
- [Bond Loyalty Report 2024](https://info.bondbrandloyalty.com/the-loyalty-report-2024-press-release)

### 学术 / 研究

- [Stanford / MIT Loyalty Liability Paper (PDF)](https://web.stanford.edu/~daniancu/Papers/Working/loyalty_pricing.pdf)
- [PwC ASC 606 / IFRS 15 Loyalty Guide](https://www.pwc.com/us/en/industries/financial-services/library/loyalty-program-managers-asc606-ifrs15.html)
- [IFRS 15 Standard Page](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/)
- [NBER: Optimal Redeemable Loyalty Token Design (Dec 2024)](https://www.nber.org/papers/w33201)
- [BIS Working Paper No. 1242 (Privacy-Enhancing for Digital Currencies)](https://www.bis.org/publ/work1242.pdf)
- [EY Loyalty Fraud Whitepaper](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-ca/insights/financial-services/documents/ey-designed-loyalty-fraud-whitepaper-sw.pdf)
- [McKinsey Customer Experience and Loyalty](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/customer-experience-and-loyalty)
- [BCG Loyalty Programs Customer Expectations 2024](https://www.bcg.com/publications/2024/loyalty-programs-customer-expectations-growing)

### 法规：中国

- [国务院公报 2012 — 单用途商业预付卡管理办法](https://www.gov.cn/gongbao/content/2012/content_2292065.htm)
- [PBOC Order [2010] No. 2 — 非金融机构支付服务管理办法](https://www.gov.cn/gongbao/content/2010/content_1730706.htm)
- [PBOC Order [2021] No. 1 — 客户备付金存管办法](https://www.pbc.gov.cn/tiaofasi/144941/144957/4168458/index.html)
- [State Council Decree No. 768 — 非银行支付机构监督管理条例](https://www.gov.cn/zhengce/content/202312/content_6920724.htm)
- [PBOC Order [2024] No. 4 — 实施细则](https://www.pbc.gov.cn/tiaofasi/144941/144957/5414094/index.html)
- [国办发〔2011〕25 号 — 关于规范商业预付卡管理](https://www.gov.cn/gongbao/content/2011/content_1874904.htm)
- [PBOC/NFRA/CSRC Order [2025] No. 11 — 客户尽职调查](https://jrj.sh.gov.cn/YWTBZCCX166/20251201/18143bfe9fd14a36b3bc422a2895d593.html)

### 法规：美国

- [CFPB Circular 2024-07 — Credit Card Rewards](https://www.consumerfinance.gov/compliance/circulars/consumer-financial-protection-circular-2024-07-design-marketing-and-administration-of-credit-card-rewards-programs/)
- [CFPB Issue Spotlight May 2024 (PDF)](https://files.consumerfinance.gov/f/documents/cfpb_credit-card-rewards_issue-spotlight_2024-05.pdf)
- [Credit CARD Act of 2009 (FTC)](https://www.ftc.gov/sites/default/files/documents/statutes/credit-card-accountability-responsibility-and-disclosure-act-2009-credit-card-act/credit-card-pub-l-111-24_0.pdf)
- [FinCEN Final Rule: Prepaid Access (31 CFR 1010.100)](https://www.fincen.gov/resources/statutes-regulations/guidance/final-rule-definitions-and-other-regulations-relating)
- [California Civil Code §1749.5](https://codes.findlaw.com/ca/civil-code/civ-sect-1749-5/)
- [Texas Property Code §72.1016](https://law.justia.com/codes/texas/property-code/title-6/chapter-72/subchapter-b/section-72-1016/)
- [New York Abandoned Property Law §1315](https://law.justia.com/codes/new-york/abp/article-13/1315/)

### 法规：欧盟 / 英国

- [PSD2 — Directive (EU) 2015/2366](https://eur-lex.europa.eu/eli/dir/2015/2366/oj/eng)
- [EBA Guidelines on Limited Network Exclusion EBA/GL/2022/02](https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-final-guidelines-limited-network-exclusion)
- [EMD2 — Directive 2009/110/EC](https://eur-lex.europa.eu/eli/dir/2009/110/oj)
- [MiCA — Regulation (EU) 2023/1114](https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng)
- [EU AML Regulation 2024/1624](https://eur-lex.europa.eu/eli/reg/2024/1624/oj)
- [EDPB Guidelines 1/2024 on Legitimate Interest (Oct 2024) (PDF)](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf)
- [UK Payment Services Regulations 2017 (SI 2017/752)](https://www.legislation.gov.uk/uksi/2017/752)
- [FCA PERG 15 — Payment Services Perimeter](https://handbook.fca.org.uk/handbook/PERG/15/3.html)

### 法规：日本 / 韩国 / 新加坡 / 香港

- [Japan Payment Services Act (English)](https://www.japaneselawtranslation.go.jp/en/laws/view/3965/en)
- [Japan PPI FAQ (Payment Service Association)](https://www.s-kessai.jp/businesses/prepaid_means_overview.html)
- [Korea EFTA (Korean Law Information Center)](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=140289)
- [FSC EFTA Amendment Cabinet Decision Sept 2024](https://fsc.go.kr/eng/pr010101/83006)
- [Singapore PSA 2019](https://sso.agc.gov.sg/act/psa2019)
- [MAS Q&A — Loyalty Programmes Regulation](https://ask.gov.sg/mas/questions/clx8ktis400bzryozdeghrztg)
- [Hong Kong PSSVFO Cap. 584](https://www.elegislation.gov.hk/hk/cap584)
- [HKMA Regulatory Regime for SVF](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/stored-value-facilities-and-retail-payment-systems/regulatory-regime-for-stored-value-facilities/)

### Web3 / 区块链 Loyalty

- [Loyyal-Emirates 3-Year Production Agreement](https://loyyal.com/press/loyyal-signs-three-year-production-agreement-with-the-emirates-group-for-use-of-blockchain-loyalty-and-rewards-platform/)
- [Singapore Airlines KrisPay (Ledger Insights)](https://www.ledgerinsights.com/singapore-airlines-extends-its-blockchain-based-reward-digital-wallet/)
- [IBM Customer Loyalty Program (archived)](https://github.com/IBM/customer-loyalty-program)
- [Qiibee Foundation](https://qiibeefoundation.org/token-utilities/)
- [Lympo Hack (Cointelegraph 2022-01)](https://cointelegraph.com/news/animoca-brands-lympo-nft-platform-hacked-for-18-7-million)
- [Galxe 2025 Year in Review](https://www.galxe.com/blog/galxe-2025-year-in-review)
- [Bilt $10.75B Valuation (Bloomberg)](https://www.bloomberg.com/news/articles/2025-07-10/bilt-rewards-triples-valuation-to-10-8-billion-in-mortgage-push)
- [Starbucks Odyssey Closure (TechCrunch)](https://techcrunch.com/podcast/starbucks-odysseys-nfts-brand-loyalty/)
- [Nike RTFKT Sold (Sole Retriever)](https://www.soleretriever.com/news/articles/nike-quietly-sold-web3-brand-rtfkt-in-december-2025)
- [Plenti Failure (Coleman Insights)](https://colemaninsights.com/coleman-insights-blog/why-the-plenti-loyalty-program-failed)
- [Currency Alliance — Reality Check 5 Roadblocks](https://www.currencyalliance.com/insights/reality-check-5-roadblocks-blockchain-loyalty-tech)

### 技术标准

- [Chainstack — Token Standards (ERC20/777/1155)](https://chainstack.com/token-standards-intro-erc20-erc777-erc1155/)
- [Pimlico ERC20 Paymaster](https://github.com/pimlicolabs/erc20-paymaster)
- [OtterSec — EVM Paymaster Audit Blog (Dec 2025)](https://osec.io/blog/2025-12-02-paymasters-evm/)
- [Human Passport — Sybil Resistance](https://human.tech/blog/human-passport-proof-of-personhood-and-sybil-resistance-for-web3)
- [TrustaLabs Airdrop Sybil Identification](https://github.com/TrustaLabs/Airdrop-Sybil-Identification)
- [IBC Protocol Interoperability Report 2024](https://ibcprotocol.dev/interoperability-report-2024)

### Mycelium 内部参考

- [Mycelium Protocol GitHub](https://github.com/HyperCapitalHQ/mycelium-protocol)
- [MushroomDAO](https://github.com/MushroomDAO)
- [AAStarCommunity / Cos72](https://github.com/AAStarCommunity/Cos72)
- [AAStarCommunity / Brood (协议神经系统)](https://github.com/AAStarCommunity/Brood)
- [Cold Launch (launch.mushroom.cv)](https://launch.mushroom.cv)

---

*本报告由 Mycelium Protocol / Aura AI 研究组撰写，基于 2026-04-28 时点公开信息。原始研究材料保存在 `raw/` 目录。报告将随监管动态和项目进展持续更新。*
