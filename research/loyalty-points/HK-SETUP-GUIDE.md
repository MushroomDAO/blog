# 香港设立 Mycelium 积分合规公司：成本、周期、日常运营调研

> 起草：2026-04-28 · 范围：基于 [REPORT.md](./REPORT.md) 中"起步司法管辖 = 香港"决定的实施级调研
> 关键问题：成本？周期？难度？普通小公司能不能办？日常合规要做什么？

---

## 摘要（一页结论）

| 项目 | 数据 |
|------|------|
| **法律实体类型** | 香港私人有限公司（Private Company Limited by Shares） |
| **政府注册费** | **HKD 3,745**（含商业登记证 1 年）|
| **代理服务费** | HKD 6,000-15,000（一次性，含秘书 + 注册地址 1 年） |
| **注册周期** | **3-5 个工作日**（91% 一周内完成）|
| **难度** | **低**（普通小公司可办，无需牌照、无最低资本）|
| **首年总成本** | **HKD 30,000-60,000**（设立 + 法律意见 + 1 年运营） |
| **第 2 年起年运营成本** | **HKD 25,000-50,000**（公司维护 + 审计 + 合规） |
| **是否需要 HKMA 牌照？** | **不需要** — 走 Cap. 584 Schedule 8(3) 豁免（条件：不可换现）|
| **首批商家试点能用吗？** | **可以** — 单商家 PoC 不触发任何牌照 |

**一句话结论**：在香港注册一家普通私人有限公司起步，**法律意见书是最大的一次性投入**（HKD 30K-80K），公司本身设立 1 周内可完成；只要严格保持"积分不可换现 + 限定商家网络"，即可永久在 Schedule 8 豁免下运营，无需 HKMA SVF 牌照（避开 HKD 2,500 万实缴资本要求）。

---

## §1 公司类型选择

### 1.1 决策矩阵

| 选项 | 适用场景 | 资本要求 | 申请周期 | 我们的选择 |
|------|---------|---------|---------|----------|
| **私人有限公司** (Private Company Limited by Shares) | 起步默认 | **HKD 1 起**（无最低）| 3-5 工作日 | ✅ **首选** |
| **股份有限公司** (Public Company) | IPO 准备 | 无强制 | 类似 | ❌ 不必要 |
| **持牌 SVF**（Cap. 584 全牌照） | 真要做支付 | **HKD 2,500 万实缴** | 6-18 个月 | ❌ 起步不必要 |
| **VATP 牌照**（虚拟资产交易平台） | 做加密交易所 | 巨额 | 12-24 个月 | ❌ 我们不是交易所 |

### 1.2 为什么 Schedule 8 豁免就够了

[Cap. 584 Schedule 8](https://www.elegislation.gov.hk/hk/cap584) 列出 5 类豁免，与我们最相关的是：

> **Schedule 8(3)** — 奖励积分计划：仅存储**积分或单位**（货币价值），SVF 用户**仅可使用积分或单位购买商品/服务**（或临时存储积分+金钱混合用于支付的组合）。**储存价值不得兑换为现金**。

[HKMA 解释说明](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/stored-value-facilities-and-retail-payment-systems/regulatory-regime-for-stored-value-facilities/)：

> "SVFs exempt under Schedule 8 include bonus point schemes, **i.e. airline mileage scheme or customer loyalty schemes that provide non-cash points to customers**."

**关键点**：
- 豁免**自动适用**（不需要主动申请）
- HKMA 也可以基于个案批准额外豁免（如风险微不足道）
- **底层技术中性**：链上发行 vs 链下数据库不影响豁免

### 1.3 触发持牌 SVF 的场景（避免）

下列任一发生 → 失去 Schedule 8 豁免，需要申请完整 SVF 牌照（HKD 2,500 万实缴）：

| 触发条件 | Mycelium 的应对 |
|---------|----------------|
| 积分可兑换为现金 / 法币 | 协议级禁止（智能合约不开放此功能） |
| 用户付现金购买积分 | 协议级禁止 |
| 积分跨非合同关联商家流通 | 联盟智能合约白名单强制 |
| 积分上 AMM / DEX | 协议级 soulbound |
| 被 HKMA 认定"风险重大" | 保持低规模 + 主动信息披露 |

---

## §2 注册成本与周期（详细）

### 2.1 政府费用（[Companies Registry + IRD](https://www.cr.gov.hk/)）

| 项目 | 金额 (HKD) | 说明 |
|------|-----------|------|
| 公司注册费（电子）| 1,545 | Companies Registry，[Sleek 2026 数据](https://sleek.com/hk/resources/company-registration-cost-hong-kong/) |
| 商业登记证（1 年）| 2,200 | IRD（PWIF levy 2026 暂免）|
| **政府小计** | **3,745** | |
| 商业登记证（3 年，可选）| 5,650 | 长期更省 |

### 2.2 代理服务费（一次性，可自行办理省）

| 项目 | 金额 (HKD) | 说明 |
|------|-----------|------|
| 公司秘书（1 年） | 1,500-3,000 | 法定要求 |
| 注册地址（1 年） | 1,200-2,500 | 法定要求 |
| 章程起草 + 申请代办 | 2,000-5,000 | 一次性 |
| **代理小计** | **4,700-10,500** | |

### 2.3 总成本

| 项目 | 自助 | 委托代理 |
|------|------|---------|
| 设立成本 | HKD 3,745 | **HKD 6,000-15,000** |
| 时间 | 5-7 工作日 | **3-5 工作日**（91% 一周内）|

**推荐路径**：委托靠谱代理（如 Sleek、Statrys、Osome、Atomos）— **HKD 10,000 左右一周内办完**，省事。

### 2.4 银行账户开设（关键瓶颈）

公司注册后真正的卡点：**开企业银行账户**。

| 银行 | 开户难度 | 周期 | 实地见面 |
|------|---------|------|---------|
| 汇丰 / 中银 / 渣打（传统大行） | 高 | 4-12 周 | 必须本人到港 |
| 众安虚拟银行（ZA Bank） | 中 | 1-2 周 | 全在线 |
| Welab Bank | 中 | 1-2 周 | 全在线 |
| Statrys（持牌支付机构）| 低 | 3-5 天 | 全在线 |
| Wise Business / Airwallex | 低 | 1-3 天 | 全在线 |

**建议**：先用 Statrys 或 Airwallex 起步（多币种 + 收 USDC 友好），后续规模上来再开汇丰 / 渣打。

---

## §3 难度评级：低

### 3.1 普通中小公司能办吗？

**能**。香港是全球公司注册门槛最低的司法管辖区之一：

- ✅ 无最低注册资本（HKD 1 都行）
- ✅ 无国籍 / 居留要求（创始人不必香港居民）
- ✅ 1 个董事 + 1 个股东即可（同一人可兼）
- ✅ 全程电子化（[Statrys 8 步在线指南](https://statrys.com/hk/guides/company-registration-guide)）
- ✅ 与中国大陆陆港通跨境联系便利
- ✅ 英语 + 中文双语法律体系（合同 / 章程可中英文）

### 3.2 难度对比

| 司法辖区 | 起步难度 | 关键障碍 |
|----------|---------|---------|
| **香港** | ⭐ 低 | 无 — 一周可办 |
| 新加坡 | ⭐⭐ 低-中 | 至少 1 名本地居民董事 |
| 美国 Wyoming | ⭐⭐ 低 | EIN 申请 + IRS / 各州 escheat 复杂 |
| UAE DIFC | ⭐⭐⭐ 中 | 需要 DIFC 实际办公地 |
| 日本 | ⭐⭐⭐⭐ 高 | 需要本地代表 + 资本注资 |
| **中国大陆** | ⭐⭐⭐⭐⭐ 极高 | 几乎不可行（区块链积分） |

### 3.3 不需要的（节省成本）

- ❌ HKMA SVF 牌照（HKD 2,500 万实缴 + 12-18 个月申请）
- ❌ VATP 牌照（虚拟资产交易平台，巨额成本）
- ❌ MSO 牌照（Money Service Operator，we don't 收 cash）
- ❌ TCSP 牌照（Trust or Company Service Provider，we don't 提供 trust 服务）
- ❌ 律师行 / 会计师行专业牌照

---

## §4 关键合规要素

### 4.1 公司层面（法定，每年）

| 项目 | 频率 | 成本 (HKD) | 备注 |
|------|------|-----------|------|
| **商业登记证续期** | 每年 | 2,200 | IRD |
| **Annual Return** (NAR1) | 每年（成立日 ±42 天）| 105 + 代理费 | Companies Registry |
| **审计师审计** | 每年 | **5,000-30,000** | 全部公司必须，HKICPA 注册会计师签字 |
| **报税（Profits Tax Return）** | 每年 | 含在审计中 | IRD |
| **股东会 / 董事会决议** | 法定 | 内部成本 | 公司秘书协助 |

**首 18 个月**：可申请第一份审计延期到注册满 18 个月时（HK 惯例），节省一次审计成本。

### 4.2 业务层面（Cap. 584 Schedule 8 维持条件）

**协议级保持的硬条件**（违反任一即失豁免）：

```
1. 积分不可兑换为现金 / 法币
2. 积分仅在发行方 + 关联团体（合同关联）内使用
3. 用户不可用现金购买积分
4. 不在 AMM / DEX 上市
5. 不被 HKMA 认定"用户或金融系统风险重大"
```

**建议主动措施**：
- 第一年完成后主动给 HKMA 发 1 页"业务说明信"（不是申请，是声明），确认我们是 Schedule 8(3) 业务
- 保持小规模（年发行量 < HKD 1,000 万）期间几乎不会被审计
- 规模扩张前提前 6 个月联系 HKMA fintech 联络组（[fintech@hkma.gov.hk](mailto:fintech@hkma.gov.hk)）

### 4.3 数据层面（[PDPO](https://www.pcpd.org.hk/)，香港个保法）

| 要求 | Mycelium 应对 |
|------|--------------|
| 收集前明确通知 | Sin90 钱包 onboarding 同意流程 |
| 仅收集必要数据 | 不上链 PII，仅哈希承诺 + ZK 证明 |
| 安全存储 | 加密 SQLite + 端到端加密同步 |
| 用户可取出 / 删除 | OpenPNTs 支持本地数据导出 |
| 数据出境通知 | 如有跨境同步功能（Nostr）须公示 |

PDPO 比 GDPR 宽松（无 Art. 22 自动化决策禁令），但**保护意识不能降低** — 一旦欧盟用户加入，GDPR 适用。

### 4.4 AML/CFT 层面（[Cap. 615](https://www.elegislation.gov.hk/hk/cap615)）

**好消息**：纯 loyalty 业务（无现金、无支付、无第三方汇款）**不在 AMLO 第 2 部 + 附表 1 的 FI 范畴内**。

**但**，下列行为会把我们拉入 AMLO 监管：
- 给商家提供托管服务（→ TCSP）
- 给用户提供加密资产交换（→ VASP）
- 让积分跨用户大额转移（>HKD 8,000 单笔，可能被认定为 "remittance"）

**Mycelium 的姿态**：
- 主动声明业务为 "non-remittance loyalty point service"
- 不做用户间积分转账（仅商家发行 + 用户兑换）
- 联盟内积分流动用 ZK 证明掩盖具体身份（ZK 证明 ≠ 反洗钱黑名单豁免，但确实减少 PII 暴露）
- 内部建立 [JFIU 可疑交易报告](https://www.jfiu.gov.hk/) 通道（即使不强制）— 主动姿态

### 4.5 税务层面（[IRD](https://www.ird.gov.hk/)）

| 税种 | 税率 | 备注 |
|------|------|------|
| **Profits Tax**（利得税） | 8.25% (首 200 万 HKD) / 16.5% (超出) | **离岸收入可豁免** |
| 薪俸税 | 累进 | 仅雇佣员工时 |
| 销售 / 增值税 | **0%** ✨ | 香港无 VAT/GST |
| 资本利得税 | **0%** ✨ | 香港无资本利得税 |

**离岸收入豁免**（Offshore Claim）：如果 Mycelium 的 SaaS 客户主要在香港以外、服务器在香港以外、合同在香港以外签订 → 可申请利得税豁免。**这对全球性 SaaS 是巨大优势**。需要保留充足证据（合同、邮件、流水），律师协助申请，第一次申请约 HKD 50,000 律师费 + 6-12 个月审核。

---

## §5 日常运行合规清单

### 5.1 月度（30 分钟）

- [ ] 月度交易流水记录（用 Xero / Statrys 自动）
- [ ] 商家 onboarding 文档归档（KYC 商家身份）
- [ ] OpenPNTs 智能合约状态检查（出问题日志）
- [ ] 检查 [HKMA SVF 公告](https://www.hkma.gov.hk/eng/regulatory-resources/registers/register-of-svf-licensees/) 是否有政策变化

### 5.2 季度（半天）

- [ ] 联盟形成 / 解散记录归档（合同 PDF + 链上交易 hash）
- [ ] AML 自查（疑似异常交易记录）
- [ ] 财务总账核对
- [ ] 用户反馈 / 客服记录
- [ ] 隐私政策 / 服务条款年度版本检查

### 5.3 年度（2-4 周累计）

- [ ] **Annual Return (NAR1) 提交** — 成立日 ±42 天
- [ ] **审计师审计 + Profits Tax Return** — 财年结束后
- [ ] **商业登记证续期**
- [ ] 公司秘书 / 注册地址服务续期
- [ ] 律师 + 会计师年度评估
- [ ] **HKMA Schedule 8 业务说明信**（自愿，但建议）
- [ ] 重大政策变化梳理（PDPO / AMLO / Cap. 584）

### 5.4 触发性合规事件

| 事件 | 应对 |
|------|------|
| 单月发行 > HKD 1M | 内部审计 + 评估是否触发 SVF 牌照 |
| 单笔商家发行 > HKD 100K | 商家增强 KYC |
| 跨境用户 > 30% | GDPR / 中国个保法重新评估 |
| 用户欺诈事件 | 24 小时内决定是否上报 JFIU |
| 联盟成员退出 | 智能合约自动结算 + 通知用户 |

---

## §6 香港政府扶持资源（可申请）

### 6.1 [Cyberport 孵化计划](https://www.cyberport.hk/en/digital_tech/blockchain/)

- 资金：**HK$500,000** 现金 + 办公空间
- 周期：24 个月
- 适用：Fintech / Blockchain / AI 早期项目
- 数据：Cyberport 现有 440+ Fintech 公司，**香港最大区块链生态**
- 申请：年度多轮，公开线上提交
- **强烈建议申请** — 与我们 Schedule 8 豁免方案完美契合

### 6.2 [HKSTP](https://www.hkstp.org/)

- 资金：累计 **HK$21.5M** 资金管道
- 周期：长期生态
- 适用：偏 Deep Tech、AI / Web3 基础设施
- 优势：2,400+ 科技公司、16,000+ 研发人员

### 6.3 [HKMA FinTech Sandbox 3.1](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/fintech/fintech-supervisory-sandbox/)

- **目的**：在监管指导下测试创新方案
- **特别**：2024 增加 Generative AI Sandbox
- **适用**：当我们规模到达需要更明确监管立场时（Phase 2-3）
- **不需要起步就申请**

### 6.4 [InvestHK](https://www.investhk.gov.hk/)

- 政府投资促进局，免费支持
- 提供：开公司咨询、办事处选址、政府对接
- **首次咨询免费**，强烈建议立项前接触

### 6.5 税务优惠

- **首 HKD 200 万利润 8.25% 税率**（标准 16.5% 的一半）
- **离岸收入豁免**（如客户和服务器都在港外）
- **R&D 加计扣除**：合资格 R&D 开支 200% 或 300% 扣除

---

## §7 启动 Timeline 与预算

### Phase 1：法律基础（M1-M2）

| 任务 | 周期 | 成本 (HKD) |
|------|------|-----------|
| InvestHK 免费咨询 | 1 周 | 0 |
| 选定代理：Sleek / Statrys / Atomos | 1 周 | 0 |
| 提交注册材料 | 1 周 | 6,000-15,000（含首年代理）|
| 公司成立 + 商业登记证 | 1 周 | 3,745（含税）|
| 委托律所写法律意见书（核心！） | 4-6 周 | **30,000-80,000**（一次性）|
| 银行账户（Statrys / Airwallex）| 1-2 周 | 1,000-3,000 |
| **Phase 1 小计** | **6-10 周** | **约 HKD 50,000-100,000** |

**关键**：法律意见书要明确确认：
1. OpenPNTs 协议在 Schedule 8(3) 豁免内
2. 临时联盟（contractual affiliation）满足"limited network"要件
3. ZK 证明 + soulbound 设计满足 PDPO + AMLO 要求
4. SuperPaymaster 支付 gas 不构成支付服务

**律所推荐**（优先级排序）：
1. [Hogan Lovells HK](https://www.hoganlovells.com/en/locations/hong-kong) — 国际所，区块链经验丰富
2. [Linklaters HK](https://www.linklaters.com/en/locations/hong-kong) — 强金融监管业务
3. [Deacons](https://www.deacons.com/) — 香港本土所，性价比高
4. [ONC Lawyers](https://www.onc.hk/) — 中型本土所，曾发表 Cap. 584 分析

### Phase 2：业务运营（M3-M9）

| 任务 | 周期 | 成本 (HKD/年) |
|------|------|--------------|
| 公司维护（秘书 + 地址）| 持续 | 3,000-5,500 |
| 第一年审计 | 12 月底 | 5,000-15,000 |
| 报税（含审计）| 4 月 | 含上 |
| AML 内训 + 流程 | 季度 | 5,000 |
| 法律 retainer（按需）| 月 / 季 | 10,000-30,000 |
| **Phase 2 年成本** | **HKD 25,000-55,000** | |

### Phase 3：规模扩张（M10+）

| 选项 | 触发条件 | 时间 / 成本 |
|------|---------|------------|
| 申请 HKMA SVF 牌照 | 年发行 > HKD 5M 或现金兑回需求 | 12-18 个月 + HKD 25,000,000 实缴资本 |
| 进入 HKMA FinTech Sandbox | 想测试新合规边界 | 3-6 个月免费 |
| 跨境扩张（新加坡） | 东南亚商家增多 | 类似香港，HKD 50,000-100,000 |
| 美国设立子公司（Wyoming） | 北美商家进入 | USD 2,000-10,000 |

### 三年总预算

| 项目 | 第 1 年 | 第 2 年 | 第 3 年 |
|------|--------|--------|--------|
| 法律 / 注册 | 50,000-100,000 | 10,000 | 10,000 |
| 公司维护 | 30,000 | 30,000 | 30,000 |
| 审计 + 税务 | - | 15,000 | 25,000 |
| 法律 retainer | 含上 | 30,000 | 50,000 |
| **年小计 (HKD)** | **80,000-130,000** | **85,000** | **115,000** |
| **三年累计** | | | **HKD 280,000-330,000** |

**对比 SVF 持牌路径**：HKD 25,000,000 实缴资本 + 12-18 个月 + 每年 HKD 1-3M 合规费用。Schedule 8 豁免路径成本约 **1% of SVF 持牌路径**。

---

## §8 风险与应对

### 8.1 主要风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| HKMA 改变 Schedule 8 解释 | 低-中 | 高 | 主动 Sandbox 申请 + 律师 retainer |
| 业务规模触发 SVF 牌照 | 中 | 高（HKD 25M 资本壁垒）| 协议级硬上限保持小规模 |
| 中国监管"长臂"针对香港业务 | 低 | 中 | 不接受中国大陆用户 + 香港数据本地化 |
| 银行账户被拒 / 关闭 | 中 | 中 | 多备用账户（Statrys + Airwallex + 传统行）|
| 律师意见书与 HKMA 实际理解不一 | 低 | 高 | 找有 Cap. 584 案例的律所，要求"reliance letter" |

### 8.2 退出 / 转型路径

如果香港路径走不通：
- **降级到深圳前海合作区**（仍在中国但有特殊政策） — 但区块链积分仍受限
- **升级到新加坡** — 法律环境类似但成本高 30-50%
- **撤至 UAE DIFC** — Loyyal 走过这条路，证可行
- **完全去中心化（无主体）** — Mycelium 协议托管在 ENS + IPFS，不需要法律实体（但失去 SaaS 收费能力）

### 8.3 不能做的事（红线）

| 红线 | 触发后果 |
|------|---------|
| 接受现金购买积分 | 失去 Schedule 8 豁免 → 须 HKD 25M SVF 牌照 |
| 让积分换现金 | 失去 Schedule 8 豁免 |
| 上 AMM / 让代币自由交易 | 触发 [VATP](https://www.sfc.hk/en/Regulatory-functions/Intermediaries/Licensing/Virtual-Asset-Trading-Platform-Operators) 监管 + SFC 牌照 |
| 给用户提供 1:1 法币锚定积分 | 触发 2025-08 [稳定币条例](https://www.elegislation.gov.hk/hk/cap656) |
| 跨用户大额积分转账 | 可能触发 MSO 牌照要求 |

---

## §9 行动清单（创始人版）

### 本周（决策）
- [ ] 阅读本文档 + REPORT.md + RECOMMENDATION.md
- [ ] 决定是否启动香港路径
- [ ] 联系 [InvestHK](https://www.investhk.gov.hk/) 申请免费 1 小时咨询

### 下周（启动）
- [ ] 与 2-3 家代理（Sleek / Statrys / Atomos）询价
- [ ] 与 2-3 家律所（Hogan Lovells / Deacons / ONC）初步沟通法律意见书报价
- [ ] 内部确认资金（首年 HKD 80,000-130,000）

### 第 3-4 周（执行）
- [ ] 签订代理 + 律所合同
- [ ] 提交公司注册材料
- [ ] 起草 Schedule 8 合规说明（法律意见书的输入）

### 第 5-10 周
- [ ] 公司成立 + 商业登记证
- [ ] 银行账户开设（Statrys / Airwallex 起步）
- [ ] 法律意见书完成
- [ ] [Cyberport](https://www.cyberport.hk/) 孵化计划申请（如时机合适）

### 第 11+ 周（业务启动）
- [ ] 单商家 PoC 上线（Mycelium 团队咖啡店伙伴 / 香港或东南亚）
- [ ] iDoris AI 发行率优化器 MVP
- [ ] 公开发布博客 + 寻找种子商家

---

## §10 关键参考资料

### 香港监管（一手）
- [Companies Registry](https://www.cr.gov.hk/) — 公司注册
- [Inland Revenue Department (IRD)](https://www.ird.gov.hk/) — 税务局
- [HKMA — SVF 监管页](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/stored-value-facilities-and-retail-payment-systems/regulatory-regime-for-stored-value-facilities/)
- [Cap. 584 — Payment Systems and Stored Value Facilities Ordinance](https://www.elegislation.gov.hk/hk/cap584)
- [Cap. 615 — AML/CTF Ordinance](https://www.elegislation.gov.hk/hk/cap615)
- [PCPD — Privacy Commissioner](https://www.pcpd.org.hk/)
- [JFIU — Joint Financial Intelligence Unit](https://www.jfiu.gov.hk/)
- [SFC — Securities and Futures Commission](https://www.sfc.hk/)

### 注册成本与流程
- [Sleek 2026 注册成本指南](https://sleek.com/hk/resources/company-registration-cost-hong-kong/)
- [Statrys 8 步在线指南](https://statrys.com/hk/guides/company-registration-guide)
- [Athenasia 2026 完整成本明细](https://www.athenasia.com/post/the-complete-2026-cost-breakdown-for-hong-kong-company-incorporation)
- [Osome 商业登记费指南](https://osome.com/hk/guides/business-registration-fees/)

### Schedule 8 法律分析
- [Lexology — SVF Licensing and Loyalty](https://www.lexology.com/library/detail.aspx?g=809b664b-5c67-4f0a-900c-c4de357e5a25)
- [Mayer Brown — SVF Licensing and Privacy](https://www.mayerbrown.com/-/media/files/news/2016/10/stored-value-facilities-licensing-and-privacy-in-h/files/pfl_october2016_pg18-19/fileattachment/pfl_october2016_pg18-19.pdf)
- [ONC Lawyers — PSSVFO 解析](https://www.onc.hk/uploads/publications/11236/en/pdf/Payment_Systems_and_Stored_Value_Facilities_Ordinance.pdf)

### 政府扶持
- [Cyberport](https://www.cyberport.hk/)
- [HKSTP](https://www.hkstp.org/)
- [HKMA FinTech Sandbox](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/fintech/fintech-supervisory-sandbox/)
- [InvestHK](https://www.investhk.gov.hk/)

### Mycelium 内部
- [REPORT.md — 行业全景调研](./REPORT.md)
- [RECOMMENDATION.md — 8 个具体决策](./RECOMMENDATION.md)
- [Mycelium Protocol GitHub](https://github.com/HyperCapitalHQ/mycelium-protocol)

---

*本文档基于 2026-04-28 时点的法规与市场数据。香港监管环境相对稳定但稳定币条例（2025-08）和 VATP 制度（2024-06）等新规仍在演进，建议每年由律师评估最新合规状态。*
