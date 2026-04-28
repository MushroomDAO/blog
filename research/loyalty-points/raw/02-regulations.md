# Agent B 原始研究：全球积分法规

> 来源：研究 Agent B, 2026-04-28
> 范围：6 大司法辖区法规（中/美/欧英/日/韩/新港）+ "积分是否构成货币 / 支付工具 / e-money" 边界分析

## Cross-Jurisdictional Bottom Line

| 司法辖区 | "免费"积分 | "付费/可转/多商家"积分 | 作为支付替代 |
|---|---|---|---|
| **中国** | 一般在支付服务法之外（如视为无偿赠予）；跨组织可转让 / 开放式 → State Council 768 + MOFCOM Order 9 | 单用途：MOFCOM Order 9（备案、托管）；多用途：PBOC 支付牌照 | 多用途预付卡 / 支付工具 |
| **美国** | 联邦：非 e-money；州 UP 法常豁免 | 可重充 / 可换现 / 跨商家 → FinCEN "stored value" 31 CFR 1010.100 | CFPB UDAAP 风险（Circular 2024-07）；州 MTL |
| **欧盟/英国** | PSD2 Limited Network Exclusion (Art 3(k)) + EBA/GL/2022/02 | 多商家：12-mo 量 > EUR 1M 须通报 | EMD2 e-money 牌照，GDPR 同意 |
| **日本** | PSA 之外（无对価 / 无偿里程） | 付费积分 → 前払式支払手段（自家型 > JPY 10M 通报；第三者型注册） | 完整 PSA 注册 + 50% 担保金 |
| **韩国** | 免费里程通常 EFTA 之外 | 付费预付电子支付工具 → 100% 备付金（2024-09 EFTA 修正） | FSC 注册 |
| **新加坡** | "Limited purpose e-money"/"Limited purpose DPT" — Part 3 例外 | 一旦构成支付服务 / SVF → PSA 牌照（MPI/SPI） | MAS PS Act |
| **香港** | Cap. 584 Schedule 8 — bonus point / loyalty SVF 在不可换现时豁免 | 多用途 SVF 牌照（HKD 25M 实缴资本） | HKMA SVF 牌照 |

## §1 中国

### 1.1 单用途商业预付卡管理办法 — MOFCOM Order No. 9 (2012)
- 颁布：商务部 2012-09-21；生效：2012-11-01；2016-08 修订
- [国务院公报 2012 年第 35 号](https://www.gov.cn/gongbao/content/2012/content_2292065.htm)
- **核心条款**：
  1. **三类备案**（集团 / 品牌 / 规模）30 日内备案
  2. **有效期**（Art. 18）：记名卡**不得设有效期**；不记名卡**至少 3 年**；过期残值需提供激活/换卡服务
  3. **KYC**（Art. 16 + 国办发〔2011〕25 号）：个人购买记名卡 / 单次不记名卡 ≥ RMB 10,000 须实名；记录保存 ≥ 5 年
  4. **现金购买禁令**：单位一次 ≥ RMB 5,000 或个人 ≥ RMB 50,000 须银行转账
  5. **面值上限**：不记名卡 ≤ RMB 1,000；记名 ≤ RMB 5,000
  6. **资金托管**（Art. 26）：规模 ≥ 20%；集团 ≥ 30%；品牌 ≥ 40%
  7. **资金用途限制**（Art. 23）：仅限主营业务，**禁止房地产 / 股权 / 证券 / 借贷**
  8. **跨组织结算**：限"同一企业 / 集团 / 特许加盟" — 显式禁止第三方（开放式）发行

### 1.2 非金融机构支付服务管理办法 — PBOC Order [2010] No. 2
- 2010-09-01 生效；现已大幅被 State Council Decree 768 (2024) 替代
- [国务院公报](https://www.gov.cn/gongbao/content/2010/content_1730706.htm)
- Art. 2 定义"预付卡"为可在发行机构外（即多用途）使用的预付价值

### 1.3 非银行支付机构监督管理条例 — State Council Decree No. 768 (Dec 2023)
- **生效**：2024-05-01
- [国务院](https://www.gov.cn/zhengce/content/202312/content_6920724.htm)
- PBOC 实施细则：[PBOC Order [2024] No. 4](https://www.pbc.gov.cn/tiaofasi/144941/144957/5414094/index.html)
- **重新分类**：所有支付业务重组为**储值账户运营 I/II + 支付交易处理 I/II**。原"预付卡发行 & 受理" → **储值账户运营 II 类**
- **资本**：基本 RMB 100M；储值账户 II 跨省每省加 RMB 5M（封顶 RMB 100M 全国）
- **Art. 24**：用户预收资金须**及时按额度**转化为支付账户/预付余额。**不得向用户支付利息**
- **Art. 33**：关键信息基础设施数据本地化；跨境出口需用户单独同意

### 1.4 客户备付金存管 — PBOC Order [2021] No. 1
- 2021-03-01 生效，[原文](https://www.pbc.gov.cn/tiaofasi/144941/144957/4168458/index.html)
- Art. 4：100% 客户备付金须存入 PBOC 或合格商业银行；禁止挪用 / 质押 / 借贷

### 1.5 反洗钱法 — 2024-11-08 修正 / 2025-01-01 生效
- 全国人大常委会，替代 2006 年版
- 引入"其他犯罪"兜底（Art. 2）；金融机构 + "特定非金融机构"（含支付机构）受益所有人核实义务
- 配套 [PBOC/NFRA/CSRC Order [2025] No. 11](https://jrj.sh.gov.cn/YWTBZCCX166/20251201/18143bfe9fd14a36b3bc422a2895d593.html)（金融机构客户尽职调查管理办法）2026-01-01 生效

### 1.6 PBOC 关于"积分换购"的立场
PBOC 没有专门规则。事实立场来自公告与执法：
- **纯无偿积分仅在发行方内部使用** → 支付服务法之外
- **若**（a）跨非关联商家自由转让、（b）现金购买、（c）现金兑回、（d）用于第三方义务清偿 → 视为**多用途预付价值**，触发 Decree 768 牌照
- **PBOC 银发〔2017〕281号**（关于规范支付创新业务的通知）明确警告"积分变现"和借积分/优惠券变相支付
- **区块链发行积分**：**没有豁免**。2017 ICO 禁令（PBOC + 6 部委 2017-09-04 公告）+ 2021 加密币 10 部门联合通知（2021-09-15）将"任何可换法币或用于支付的代币"视为非法融资或无证支付服务。**代币形式的积分必须**：(i) 不可交易、(ii) 不可换法币、(iii) 仅在发行方关联商家网络内使用

## §2 美国

### 2.1 FTC §5 - 15 U.S.C. § 45
- "不公平或欺诈做法"
- 无单一 FTC "loyalty rule"，执法集中于：欺诈营销、未披露重大限制、贬值、"doom-loop" 兑换摩擦、Endorsements (16 CFR 255)

### 2.2 CFPB Credit-card 积分（关键）
- **CFPB Circular 2024-07** (Dec 18, 2024) [全文](https://www.consumerfinance.gov/compliance/circulars/consumer-financial-protection-circular-2024-07-design-marketing-and-administration-of-credit-card-rewards-programs/)
  - 法律基础：CFPA 12 U.S.C. § 5531(a) + § 5536(a)(1)(B) (UDAAP)
  - 立场："小字免责或合同条款给运营方调整奖励的权利往往不足以纠正消费者的总体印象"
  - 已获得积分的贬值在 CFPA 下可能构成不公平 / 欺诈
- **Issue Spotlight (May 2024)**：4 类问题（意外条件、贬值、兑换问题、撤销）；2022 年末消费者奖励余额 > USD 33B

### 2.3 CARD Act 2009 — Pub. L. 111-24
- 15 U.S.C. § 1637(i) (TILA)：账户条款"重大变更"前 45 天通知；Reg Z (12 CFR § 1026.9(c)) 实施
- **但 CARD Act 不定义"奖励积分"为受保护账户条款** — 这正是 CFPB Circular 2024-07 用 UDAAP 闭合的口子
- 礼品卡（15 U.S.C. § 1693l-1, Reg E §1005.20）：店内礼品卡至少 5 年有效；忠诚 / 促销 / 奖励卡明确豁免（§1005.20(b)(2)）

### 2.4 GAAP / IFRS 会计
- **ASC 606-10-25** = IFRS 15
- 积分 = "material right"，独立履约义务
- 按独立销售价格分配交易价格 → **递延为合同负债**
- 必须估算 **breakage** （ASC 606-10-55-48）
- 披露：项目性质、SSP/breakage 判断、合同负债余额 / 周期变化

### 2.5 SEC 披露
- Reg S-K Item 303 (MD&A) + Item 101 (业务)：重大忠诚度计划披露关键会计估计 / 或有负债
- 10-K / 10-Q：ASC 606 合同负债滚动；SEC 工作人员曾在评论函中质疑 breakage 假设

### 2.6 各州未认领财产 (Escheat)
- **加州** Civil Code § 1749.5：礼品凭证不得过期、不得收手续费；**忠诚 / 促销 / 奖励** 凭证（无对价）**豁免**；CCP §1500 et seq. 一般不归集礼品卡
- **得州** Property Code §72.1016：储值卡推定弃置 = 过期或第 3 周年使用日（取较早）；无过期 + 仅手续费的卡豁免
- **纽约** Abandoned Property Law §1315 / §1316：未兑换礼品凭证 5 年弃置；忠诚卡（无对价）一般主张在外，但州审计常挑战发行方
- **NAUPA 模型法**：5 年休眠期

### 2.7 FinCEN BSA 预付访问规则
- **31 CFR § 1010.100(ff)(4)** (effective 2011-09-27)
- "**Closed-loop prepaid access**" (31 CFR § 1010.100(kkk)) — 仅在指定商家 / 地点使用 — **MSB 排除**，前提是日加载 ≤ **USD 2,000**
- 销售方若每日 > **USD 10,000** 给一人，须实施 AML 计划
- **纯忠诚奖励**（无现金购买）通常完全在 Prepaid Access Rule 外。**但可重充忠诚储值且可换现金等价 → 触发 MSB 注册**

## §3 欧盟 / 英国

### 3.1 PSD2 — Directive (EU) 2015/2366
- **Article 3(k)** Limited Network Exclusion (LNE)。排除仅限以下使用的支付工具：
  - (i) 发行方场所内
  - (ii) 与专业发行方有直接商业协议的有限服务提供方网络内
  - (iii) 非常有限的商品/服务范围
  - (iv) 单一成员国内特定社会/税务用途
- **Article 37(2)**：依赖 LNE 的发行方任何 12 个月期内总交易量 > **EUR 1M** → 须**通报主管机关**

### 3.2 EBA Guidelines on LNE — EBA/GL/2022/02
- 2022-02-24 通过；2022-06-01 适用
- [EBA 公告](https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-final-guidelines-limited-network-exclusion)
- 7 条指引覆盖 Art 3(k) 子条件评估、"limited network"、"limited range"、专业发行方角色、通报
- BaFin 指引：多商家忠诚度计划（如 Payback、Lufthansa Miles & More、DeutschlandCard）只有在运营方通报且网络保持"有限"时才在 LNE 范围内 — 但若**可换现或一般支付**则成为 **EMD2 e-money**

### 3.3 EMD2 — Directive 2009/110/EC
- E-money：电子存储的货币价值，代表对发行方的索偿，因接收资金而发行用于支付，被发行方以外的人接受
- **积分成为 e-money** 当三者并存：(a) 因资金而发行，(b) 旨在作为支付手段，(c) 被第三方商家接受
- 发行方须取得 **EMI 牌照** + 客户资金保护

### 3.4 GDPR
- Art. 6(1)(a)/(b)/(f) 合法依据
- **EDPB Guidelines 1/2024（合法利益）**（2024-10）：忠诚度计划中的营销分析**通常需要同意**，不是合法利益
- Art. 22：禁止仅自动化决策 - 影响忠诚度等级算法和动态定价

### 3.5 MiCA — Regulation (EU) 2023/1114
- ART/EMT 条款 2024-06-30；全面适用 2024-12-30；现有 CASP 过渡期 2026-07-01 结束
- **Art. 4(3) 例外**：白皮书不要求于：
  - (a) 免费提供
  - (b) 作为区块链维护奖励自动创建
  - (c) **效用代币提供对现有商品/服务的访问**
  - (d) 仅在**有合同协议的有限商家网络**内使用
- **对区块链发行积分的实践含义**：结构为 Art. 4(3)(c)/(d) 效用代币，确保 (i) 仅可兑换发行方/网络商品/服务，(ii) 无募资营销，(iii) 不在加密交易平台上市，(iv) 清晰的 LNE 式商家协议

### 3.6 英国
- Payment Services Regulations 2017 (SI 2017/752) — 实施 PSD2
- Schedule 1 Part 2 paragraph 2(k)：同 PSD2 LNE 措辞
- E-Money Regulations 2011 (SI 2011/99)：EMI 授权
- [FCA PERG 15](https://handbook.fca.org.uk/handbook/PERG/15/3.html) 边界指引；**PERG 15.5** 否定范围 / 排除
- 英国未采纳 MiCA，正开发自己的加密制度（HM Treasury 2024 咨询）

### 3.7 EU AML — 第 6 反洗钱指令 + AML Reg 2024/1624
- AML Regulation (EU) 2024/1624 — 2024-05 通过，2027-07 适用
- E-money 发行方 + CASP 完整 CDD；**匿名预付 e-money 上限**（如店内 EUR 150，在线 EUR 50）

## §4 日本

### 4.1 資金決済法 (PSA)
- Act No. 59 of 2009；2022 主要修正（稳定币）
- [英文翻译](https://www.japaneselawtranslation.go.jp/en/laws/view/3965/en)
- **Article 3 — "前払式支払手段"** 4 个累积要件：
  1. 价值/数量记录在凭证或电子记录上
  2. **以对価（consideration）发行**
  3. 凭证/号码/符号发行
  4. 可用于赎回
- **关键忠诚度边界**：**无偿发行**的积分（景品 / おまけ）**缺少对価要件** → PSA 范围之外。付费充值/购买 = PPI

### 4.2 自家型 vs 第三者型
- **自家型** (Art. 3(4))：仅在发行方使用
  - **无注册**，但 3 月底 / 9 月底**未偿余额首次超过 JPY 10M** 时须通报财务局长（Art. 5 + 内阁令）
- **第三者型** (Art. 3(5))：可与第三方商家使用
  - 必须从内阁总理大臣获得**注册**（授权 FSA / 地方财务局）（Art. 7-8）
  - 资格：仅限法人；资本要求；合规体系；无失格历史

### 4.3 担保金 (Art. 14)
- 未偿余额 > **JPY 10M** → 须存**至少 50%**担保金于法务局，或等价信托协议 / 银行担保
- 信托财产限于现金、银行存款、政府债券（面值 90% 折扣）

### 4.4 6 个月规则
- 预付凭证有效期 **≤ 6 个月** → PSA 未偿余额 / 担保金规则**不适用**
- 许多公司设计**滚动 6 个月过期**的忠诚度 / 预付混合产品

### 4.5 FSA 关于忠诚度积分立场
- FSA 一贯认为**无偿积分（免费里程）非 PPI**（[Japan Payment Service Association FAQ](https://www.s-kessai.jp/businesses/prepaid_means_overview.html)）
- 但当积分 (a) **现金购买 / 与付费 e-money 互兑**、(b) **可有偿转让第三方**、(c) **可与 PPI 互换** → 对価要件重新附着 → PPI 注册触发
- 2022 PSA 修正引入"**电子支付工具（e-money 类稳定币）**"类别 — 若忠诚代币锚定 JPY 则相关

### 4.6 AML
- 犯罪収益移転防止法：PPI 第三者型发行方为"特定业务运营方"；交易 ≥ JPY 100,000（现金等价）须 CDD

## §5 韩国

### 5.1 전자금융거래법 (EFTA)
- [全文 (韩)](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=140289)
- Art. 2(14) "선불전자지급수단"：电子存储可转让货币价值，可用于从第三方购买商品/服务
- **2023 EFTA 修正** — 国会通过 2023-08-24，签署 2023-09-14
- **执行令** — 内阁通过 2024-09-03
- **生效 2024-09-15**

### 5.2 关键改革（2024）
1. **100% 隔离管理**客户预付款（最初 50%，最终 100%）
2. 隔离资金仅限**银行存款、韩国国债、地方政府债券、邮政存款**
3. **折扣 / 奖励发行限制**：仅在债务/股权比 ≤ 200% 时可提供折扣率预付或奖励积分
4. 货币利益金额（折扣 + 奖励）须计入隔离资金计算
5. 范围扩大：原豁免的小量服务商纳入 EFTA

### 5.3 전자상거래법 (E-Commerce Act)
- KFTC 执法（与 FSC/FSS 不同）
- 预付购买的条款披露、退款 / 撤回权

### 5.4 忠诚度里程立场
- FSC 法令解释门户历史上认为**无偿累积里程在 EFTA 预付工具范围之外**
- 但**购买 / 可转让 / 可换现**里程在 EFTA 范围内 → 注册要求
- 2024 改革针对"쿠팡 캐시" / 电商平台积分扩大范围

### 5.5 KYC / AML
- 특정 금융거래정보의 보고 및 이용 등에 관한 법률（特定金融交易信息报告法）
- KFIU（韩国金融情报机构，FSC 下）监督 VASP / 支付机构

## §6 新加坡

### 6.1 Payment Services Act 2019 (PS Act)
- [全文](https://sso.agc.gov.sg/act/psa2019)
- 2020-01-28 生效；2024 主要 DPT 修正
- 定义 7 项支付服务（Art. 6）含 e-money 发行 + DPT 服务

### 6.2 忠诚度积分立场 — MAS 权威声明
- [MAS 官方 Q&A](https://ask.gov.sg/mas/questions/clx8ktis400bzryozdeghrztg)
- "MAS does not intend for loyalty programmes that are common in the retail space to be regulated as payment services."
- 忠诚度积分可能是：
  - "Limited purpose e-money"（PS Act, Part 3 / 第一附表 Part 1）
  - "Limited purpose digital payment token"
- **结果**：相关支付服务**不受规管**

### 6.3 MAS 评估要素
- 计划营销为忠诚度还是支付服务？
- 计划任何部分与忠诚度目标（促进购买发行方/指定商家商品/服务）冲突？
- 范围是否真正有限？

### 6.4 一旦受规管 → MPI / SPI
- **MPI**：储值 > SGD 5M 日均 / 流量阈值。SGD 250K 资本
- **SPI**：阈值以下。SGD 100K 资本
- E-money 发行须**客户资金保护**

### 6.5 AML / CFT
- MAS Notice PSN01 / PSN02：DPT 服务和 e-money 完整 CDD

## §7 香港

### 7.1 Payment Systems and Stored Value Facilities Ordinance — Cap. 584
- 2015-11-13 生效（SVF 牌照制度）
- [全文](https://www.elegislation.gov.hk/hk/cap584)
- [HKMA 解释说明](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/stored-value-facilities-and-retail-payment-systems/regulatory-regime-for-stored-value-facilities/)

### 7.2 SVF 定义 (s.2A)
- 以金钱/货币价值交换价值存储，使该价值可用于支付发行方或他人的商品/服务

### 7.3 Schedule 8 类豁免 — 忠诚度 / 奖励积分豁免
- **Schedule 8(3)** — 奖励积分计划：仅存储**积分或单位（货币价值）**用于兑换商品/服务，**不可兑现金**的 SVF
  - HKMA 指引明确举例：航空里程计划、零售商客户忠诚度计划
- Schedule 8(4) — 单一发行方某些**现金奖励**计划（小规模、单商家）
- Schedule 8(5) — 特定商家的单一用途 SVF

### 7.4 持牌 SVF 要求（豁免不适用时）
- **实缴资本**：**HKD 2,500 万最低**（PSSVFO Schedule 3, Part 1）
- 浮动资金通过信托或与运营资金分离的银行账户保护
- AMLO 合规（Cap. 615）
- 控制人 + 高管 fit-and-proper

### 7.5 HKMA 关于区块链忠诚度积分立场
- 没有专门规则。Schedule 8 豁免无论底层技术，**前提是不可换现金 + 有限用途**
- 2024 e-HKD 试点 Phase 2 含代币化忠诚度 / 商家折扣作为合法"可编程货币"用例
- **稳定币条例**（2025-08-01 生效）将法币锚定稳定币 + 任何作为稳定值支付工具营销的代币纳入 HKMA 牌照

## §8 边界问题综合 — 区块链忠诚度积分合规设计

要在全球范围内保持**支付工具 / e-money / SVF 牌照之外**，区块链忠诚度积分项目至少满足以下：

1. **无对价付款**：积分仅作为对行为（购买、注册、推荐）的无偿奖励发行。避免现金销售或付费充值（重新激活日本 PSA Art. 3、韩国 EFTA Art. 2(14) 的对价要件，全球触发 e-money / 预付卡制度）

2. **有限商家网络 + 与发行方的直接合同协议**（PSD2 Art. 3(k)(ii)；HK Cap. 584 Schedule 8(3)；MAS PS Act limited-purpose；MOFCOM Order 9 single-purpose）。避免开放式商家加入

3. **不可现金兑换 / 法币转换**（HK Schedule 8(3) 的基础测试；新加坡 MAS limited-purpose；韩国 / 中国隐含；FinCEN MSB 定义关键触发）

4. **代币无二级市场交易**（终结 MiCA Art. 4(3) 例外；触发中国 2017 ICO 禁令；触发美国 SEC Howey 暴露；触发 MAS DPT 牌照）

5. **营销为忠诚度，非支付**（明确 MAS 因素；FCA PERG 15.5；BaFin LNE 评估）

6. **量低于 LNE 通报阈值**（EU/UK：12 个月 EUR 1M）— 或超过则通报

7. **透明条款防止贬值 / 单方变更**满足 CFPB Circular 2024-07 / FTC §5 + 英国 CMA 消费者保护

8. **遵守州 escheat 法**（美国）：使用忠诚度计划豁免（如加州 Civ. Code §1749.5(b)；新泽西明确豁免）

9. **GDPR**：忠诚度数据按**同意**处理 profiling/营销

10. **AML**：即使在支付服务牌照之外，受益所有人 + 大额交易监控义务适用：PRC AML Law (2025)、EU AML Reg 2024/1624、Korea SFTRA、Singapore PSN01、HK AMLO Cap. 615、US BSA

## Sources

参见 REPORT.md §11 References。
