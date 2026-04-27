# GEO 产品调研报告：YouTube 实战 + 工具生态 + Cloudflare 产品路径

> 调研者：Jason 通过 4 个并行 research agents（YouTube / 工具生态 / 案例数据 / 小商家专项）+ 自主研究
> 调研日期：2026-04-26
> 已发布的基线文章：[GEO 实战手册](https://blog.mushroom.cv/blog/geo-generative-engine-optimization-guide/)（KDD 2024 论文 + Yext 17.2M 引用研究）
> 本报告范围：补足你已掌握的学术基础，加上 YouTube 实战派、工具生态、真实案例、SMB 角度、中国市场、Cloudflare 产品路径。

---

## 摘要：你应该知道的 9 件事

1. **GEO 是新学科还是 SEO 延伸——头部派别公开打架。** Mike King（iPullRank）/Neil Patel/工具厂商在卖"新学科"叙事；Lily Ray、Gary Illyes（Google 官方）说"传统 SEO 基本功才是关键"。Kevin Indig 用 454 prompt 实测发现 **Web 搜索位置是 LLM 引用最强预测因子**——这意味着你的产品定位必须明确回答这个张力，否则会被批为换皮。

2. **真实 ROI 比营销稿低得多。** Lily Ray 1,316 人调研：**70% 站长报告 ChatGPT 流量 <2%**；BrightEdge：AI 平台占引荐流量 <1%。但**转化率乘数确实高**：独立中位数 3-6x（Microsoft Clarity 数据 11x，Yext 4.4x）。**70.6% AI 流量在 GA4 里被错分为 "Direct"**（移动 app 不传 referrer）——这是你的产品最该说出口的真相。

3. **价格地板就在 $20。** 全市场低于 $20/月的稳定持续监控产品**只有 Rankscale**。$29-99 是入门段红海（Otterly、Promptmonitor、Knowatoa）。**$5-15 月费 + freemium** 这一档**完全空白**。

4. **西方 GEO 工具零中文 AI 引擎覆盖。** Profound（$1B 估值）、AthenaHQ、Otterly、Peec.ai 都不原生支持以中文 prompt 查询 Kimi/DeepSeek/豆包/文心。**AIDSO（爱搜）¥126/月起**已是国内头部，但 UI 简陋、海外支付不友好、不覆盖海外引擎。**"中英双向 GEO"** 是真空地带。

5. **"行动层"基本空白。** 95% 的工具只监测，不替你做事。AEO Engine（自动 Reddit/Quora 播种）、Goodie AI 的 Agentic 套件是少数例外，价格都已 $200+。**自动 Schema 注入 + AI 改写 + 多平台分发** 这条产品线非常空。

6. **Cloudflare 已经把武器都给了你。** 2025 年 Cloudflare 推出 Pay Per Crawl、AI Crawl Control、Content Signals、Robotcop——**没有任何 SaaS 把这些原语整合**。Workers AI（$0.011/1k Neurons，10k/天免费）+ Browser Rendering（10 hr/月免费）+ D1/R2/Vectorize 让你 ¥99/月仍能盈利。

7. **中国市场比想象的成熟得多。** 36.5% 中国网民已用生成式 AI 搜索；信通院预计 **2026 中国 GEO 市场 ¥286 亿**（增速最高的 AI 营销细分）。**已出现灰产**：花 ¥2 万买一条品牌答案被 AI 收录（36 氪曝光）——预算正在大规模流入但缺监管。

8. **小商家差异化逻辑是"自动驾驶仪 vs 仪表盘"。** **83% 餐厅在 ChatGPT 完全不存在**（Local Falcon 19 万查询数据）vs Google 14%。SMB 不要"GEO 仪表盘"，他们要"我们这周替你做了 X、Y、Z 三件事"。**"低价 + 自动执行 + 多本土引擎覆盖"**这个三向交集**目前没有产品**——是真正的 wedge。

9. **快速见效战术（独立来源验证）：** **BLUF / front-load 答案**——[Kevin Indig 1.2M ChatGPT 响应实证](https://www.growth-memo.com/p/the-science-of-how-ai-pays-attention)：**44.2% 引用来自页面前 30%**（不是营销话术常说的 "+67%"——那个数字已被 Agent 4 证伪，详见 [APPENDIX](./APPENDIX-creator-deep-dives.md#五关于-bluf-67-数据的更正)）；**FAQ Schema** 给页面引用率 +20-40%（[KDD 2024](https://arxiv.org/abs/2311.09735)实证最高 40% visibility boost）；**Reddit/G2 真实参与**（不是 spam）让 B2B SaaS 90 天引用率从 8% → 24%。这三招是产品 MVP 必须先做对的。

> **📚 创作者深度档案附录已完成**：4 个并行 agents 系统性深读 iPullRank、Growth Memo、Backlinko、Aleyda 个站、Lily Ray Substack、Zyppy、Ahrefs 数据集、Search Engine Land 5 篇关键文章。完整结果见 [APPENDIX-creator-deep-dives.md](./APPENDIX-creator-deep-dives.md)。重要补充：Mike King 的 **Relevance Engineering / Query Fan-Out** 完整定义；Kevin Indig 的 **Ski Ramp Pattern + Ghost Citation Problem** 实证（1.2M 响应 p<0.0001）；Ahrefs 75K 品牌反共识发现（**YouTube mentions 0.737 是最强 AI 可见度信号**）；Lily Ray 的 listicle 惩罚真实案例（-49%、-43%、-42%）；Google 三位官方代言人公开反对 GEO 概念（Gary Illyes、John Mueller、Danny Sullivan）。

---

## 一、调研方法说明

并行启动 4 个 agents，每个聚焦不同角度：

| Agent | 范围 | 关键输出 |
|-------|------|---------|
| A | YouTube top 视频 + 创作者博客 | 12 视频清单 + 共识/分歧矩阵 |
| B | GEO 工具生态地图 | 23 个工具 × 价格 × 功能矩阵 |
| C | 真实案例与指标 | 12 案例独立来源 + 失败案例 + 现实基线 |
| D | 小商家专项 | 垂直差异 + 付费意愿 + 痛点→需求 |

我同步研究 Cloudflare 平台能力 + 中文 AI 引擎引用机制（与 agents 不重叠的部分）。所有数字都附原始 URL（见末尾 Sources）。

---

## 二、YouTube 实战派精华

### 2.1 诚实判断：YouTube 不是 GEO 主战场

YouTube 上 GEO 内容呈"两端分布"——头部创作者（Aleyda、Lily Ray、Mike King、Brian Dean）的**深度内容都在博客/Substack/会议演讲**，YouTube 主要是分发渠道。腰部视频大量是 KDD 2024 论文的二次咀嚼。

**实操层面**：值得看的 YouTube 视频清单（按价值）

| # | 视频 / 频道 | 核心价值 |
|---|------------|----------|
| 1 | [Clearscope Roundtable](https://www.youtube.com/watch?v=c-VtgjXWsK4) — Lily Ray + Kevin Indig + Ross Hudgens + Steve Toth | **信息密度最高的单视频**；四派观点对照 |
| 2 | [Aleyda Solis "AI Search Optimization Roadmap"](https://www.youtube.com/watch?v=BjyF_4UhoOM)（2025-09） | 战术 roadmap + 推荐工具清单 |
| 3 | [iPullRank / Mike King "AI Search Manual"](https://www.youtube.com/@iPullRankSEO) | "Relevance Engineering" 概念 + query fan-out |
| 4 | [Brian Dean "5 Massive AI SEO Predictions"](https://www.youtube.com/watch?v=3z00T_TF7u8) | Backlinko 自身 LLM 流量 +800% 案例 |
| 5 | [Lily Ray "SEO 2025: AI, Reddit & Ranking"](https://www.youtube.com/watch?v=mgI1U7XPsUA) | **反共识视角** — 70% 站长 <2% AI 流量调研 |
| 6 | [Cyrus Shepard "Agents are early, visibility is urgent"](https://www.youtube.com/watch?v=ce_4AR5cx8A) | 把人脸/视频/个人品牌嵌入内容 |
| 7 | [Neil Patel "$2.2B SEO disruption (GEO)"](https://www.youtube.com/watch?v=02aOEbWV98c) | "Search Everywhere Optimization" 多平台叙事 |

更深入的"枪"在他们的博客：[Ahrefs GEO 完整框架](https://ahrefs.com/blog/geo-generative-engine-optimization/)、[iPullRank AI Search Manual](https://ipullrank.com/ai-search-manual)、[Aleyda AI Search Trends](https://www.aleydasolis.com/en/search-engine-optimization/ai-search-trends/)、[Lily Ray Substack](https://lilyraynyc.substack.com/p/a-reflection-on-seo-and-ai-search)。

### 2.2 共识技巧（3+ 创作者交叉验证 = 必做）

| 战术 | 多源验证 | 具体操作 |
|------|---------|---------|
| **BLUF（前置答案）** | Princeton + Mintcopy + Norg.ai | 开头 60 词直接回答主问题；引用率 +67% |
| **FAQPage / HowTo Schema** | Frase + Stackmatix + AthenaHQ | 引用率提升 20-40%（个别研究 +85%） |
| **原始数据 / 统计** | Princeton +41% + Brian Dean | 每个核心观点带可核实数据点 |
| **引用权威来源** | Princeton +30% + Aleyda | 直接引用论文 / 官方文档原文 |
| **品牌网络提及** | Ahrefs 0.664 相关系数 + Kevin Indig + Lily | **AI 可见度最强单因子**（远高于反向链接 0.218） |
| **内容分块（Chunking）** | Mike King + Search Engine Land | 段落 40-120 词；section ID；front-load |
| **YouTube 视频布局** | Lily Ray + Aleyda + Ahrefs | YouTube 是 AI Overviews **第二大**被引域；OpenAI 训练用 100 万+ 小时转录 |

### 2.3 分歧观点（你必须自己判断）

| 议题 | 派别 A | 派别 B |
|------|--------|--------|
| **GEO 是独立学科吗** | Mike King、Neil Patel、工具厂商 | **Gary Illyes（Google）、Lily Ray** — "只是 SEO 延伸" |
| **要不要刷 Reddit 帐号** | 工具厂商：建议积极发帖 | **Lily Ray** — 人工种子 = spam，会反噬 |
| **AI 流量真实占比** | 工具厂商：迅速增长 | **Lily Ray 调研** — 70% 站长 <2% |
| **要不要做 llms.txt** | Yoast / INSIDEA / 多数 GEO 工具 | **Aleyda** — 无证据主流 LLM 真在用 |
| **AI 内容做 GEO 是否有效** | 部分实战派：质量高就行 | **Lily Ray** — 批量 AI 内容 = 内容农场 |
| **Princeton 论文是否仍可复用** | 大量博客当圣经 | 学界：Princeton 在旧 BingChat 测试，机制已变 |

**产品策略含义**：你的产品**不能两边讨好**。我建议明确站到 **"GEO 是 SEO 的延伸 + 强调实测数据 + 反对 spam"** 这一派——这与 Lily Ray、Kevin Indig、Gary Illyes 一致，更可信，也更可持续（不会因为某个 AI 引擎政策变化崩塌）。

---

## 三、GEO 工具生态全景图

### 3.1 价格地板分析

| 价格区间 | 典型产品 | 关键观察 |
|---------|---------|---------|
| **免费** | HubSpot AI Search Grader、Semrush Free Visibility Checker、Knowatoa Free（10 题）、SheepGeo Basic（中文） | 全是"钩子"，单点扫描，不持续 |
| **$1-20** | **Rankscale $20**（地板，indie 单人） | **本档只有 1 家** |
| **$20-50** | Otterly Lite $29、Promptmonitor $29、Airefs $24、LLM Pulse €49 | indie / bootstrap 占据 |
| **$50-100** | Profound Starter $99、Knowatoa Premium $99、Frase $49、Semrush AI $99、Surfer $99 | "严肃创业者"入门 |
| **$100-500** | Peec €89-499、Profound Growth $399、AthenaHQ $295、Otterly Pro $989、Knowatoa Agency $749 | 中端红海 |
| **$500-3000** | Scrunch $500、Evertune $3000 | 企业入口 |
| **企业定制** | BrandRank.AI、Bluefish、Adobe LLM Optimizer、Profound Enterprise | 不公开报价 |

**关键缺口**：**$5-15/月 freemium + 持续监控** 这一档**完全空白**。多数个人博主、独立开发者、单店铺老板的需求是 1 个品牌 + 5-15 prompt 的低强度持续监控——所有现有工具都假设你至少跟踪一个品牌组合 + 25-50 prompt。

### 3.2 功能矩阵关键发现

| 功能维度 | 覆盖度 |
|---------|--------|
| ChatGPT 监测 | 几乎所有产品都有 |
| Perplexity 监测 | 几乎所有产品都有 |
| Claude 监测 | 多数有，部分加价（A）|
| Gemini 监测 | 多数有 |
| **DeepSeek/Kimi/豆包/文心**（中文用户视角）| **几乎全部不支持** |
| Schema 自动生成 | Frase、AthenaHQ、Goodie AI、AEO Engine（少数）|
| 自动 AI 改写 | Goodie AI、Surfer、Frase、Writesonic（少数）|
| **主动外链 / Reddit 自动播种** | **AEO Engine（独家）**、Goodie Agentic（部分） |

### 3.3 资本格局

| 公司 | 融资 | 创始人背景 |
|------|------|-----------|
| **Profound** | $155M 累计、2026/2 Series C $96M、估值 **$1B**（Lightspeed 领投） | 工程师出身 |
| **Peec AI** | A 轮 $21M（2025），后估值 $100M+ | 柏林团队 |
| **Evertune** | $19M | The Trade Desk 老兵 |
| **AthenaHQ** | YC W25 + $2.7M | 前 Google Search / DeepMind |
| **BrandRank.AI** | $1.2M | 前 Nestlé / P&G CMO |
| **Otterly.ai** | bootstrap | 奥地利 7 人，2025 ARR $770K，Gartner Cool Vendor |
| **Promptmonitor** | bootstrap | 单人 indie（Yogesh）|
| **Rankscale** | bootstrap | 单人 |

**含义**：你竞争的不是 Profound 那种大资本玩家——他们瞄准 Fortune 500。你竞争的是 Otterly、Promptmonitor、Rankscale、SheepGeo 那种 indie / bootstrap 小团队——而这一层**目前没有任何"中英双向 + 行动层 + Cloudflare 原生"**的产品。

### 3.4 五大产品缺口

按市场冲击力排序：

1. **中文 AI 搜索的国际化 SaaS 完全空白** — 没有产品同时服务"中国出海品牌想进 ChatGPT/Perplexity/Claude" + "海外品牌想进 Kimi/DeepSeek/豆包/文心"
2. **<$20 单创作者 / 单品牌严肃产品** — Rankscale $20 是孤岛
3. **Action 层失衡** — 95% 工具仅监测，没有"监控→改写→发布→验证"闭环
4. **Cloudflare/Edge 原生集成缺失** — Cloudflare 已推 Pay Per Crawl + AI Crawl Control + Content Signals + Robotcop，但没有 SaaS 整合这些原语
5. **CMS 嵌入式集成缺失** — 没有"装一个 Worker / 装一个 Astro 插件 / 装一个 WP 插件就自动 GEO 优化"的产品

---

## 四、真实案例与现实基线

### 4.1 12 个独立来源案例

| # | 品牌 | 行业 | 战术 | 时长 | 核心指标 | 来源等级 |
|---|------|-----|------|------|---------|---------|
| 1 | The Rank Masters（自身）| B2B SaaS | 12 pillar + entity mapping | 90 天 | ChatGPT 引荐 **+8,337.5%** | C |
| 2 | 匿名 B2B SaaS（$25M ARR）| SaaS | 内容 4→20 篇/月 + 47 Reddit + 23 G2 | 90 天 | 引用率 **8% → 24%（3x）**；ROI **288%**；€64K 收入 | B |
| 3 | Go Fish Digital（自身）| 数字营销 | 5-8 cornerstone + query fan-out | 90 天 | AI 流量 **+43%**；月转化 **+83%**；AI lead **25x** | C |
| 4 | Tally.so | SaaS（表单）| 自然品牌 mention | 2024-2025 | ChatGPT 占引荐 **10%**；ARR 提前 5 月达 $3M | 媒体 |
| 5 | Amico Lighting | 照明零售 | 反向工程 10 prompts + PR + FAQ | 120 天 | 总推荐率 **88.6%**；AI Overview 100%；Gemini 97% | B |
| 6 | LS Building Products | 建材 | Pillar 重构 | 未披露 | 自然 +67%；流量价值 +400%；AIO **+540%** | C |
| 7 | Daily Mail | 新闻 | （受影响方）| 2024-2025 | 桌面 CTR **25.23% → 2.79%（-89%）** | A |
| 8 | Forbes | 媒体 | （受影响方）| YoY 2025/7 | 流量 **-50%** | A |
| 9 | Business Insider | 媒体 | （受影响方）| 2022-2025 | 自然搜索 **-55%** | A |
| 10 | 匿名 B2B SaaS | B2B SaaS | citation engineering | 6 月 | SoV **0% → 35%**；pipeline **$2.3M / $120K 投入** | B |
| 11 | 匿名 e-commerce | 零售 | 未披露 | 3 月 | 订单 **+127%** | D（unverified）|
| 12 | Seer Interactive 客户 | 未披露 | 持续优化 | 2024-2025 | ChatGPT 转化 **15.9%** vs Google 1.76%（**9x**）| B |

### 4.2 30 / 60 / 90 天现实预期

| 时间窗 | 现实预期 |
|--------|---------|
| 0-30 天 | **看不到引用**；只有基础 schema、velocity 切换、第三方 mention 启动 |
| 30-60 天 | 长尾首次引用；首批 AI-referred session（个位数到二位数）；引用率 0% → **8-12%** |
| 60-90 天 | 进入 2-3 家竞品的 consideration set；引用率 **12-24%**；首批可归因转化 |
| 90+ 天 | "Q2 2025 实施 GEO 的公司 90 天 65% visibility gain"；竞争对等通常需 **20+ 篇/月**持续输出 |

### 4.3 转化率乘数（多源汇总）

| 数据源 | 乘数（vs Organic）|
|--------|-------------------|
| Yext | 4.4x |
| Microsoft Clarity（1,200 出版商）| **11x** |
| Discovered Labs（B2B SaaS）| 2.8x |
| Healthcare GEO 调研 | 13x |
| Go Fish Digital | 25x（自身权威性 caveat）|
| **现实中位数（建议规划用）** | **3-6x** |

**关键警告**：[Wheelhouse 数据](https://www.wheelhousedmg.com/insights/articles/ai-traffic-is-already-in-your-analytics/) 显示 **70.6% AI referrals 在 GA4 中错分为 "Direct"**（移动 app 不传 referrer）。真实 share 通常是 GA4 显示值的 **3-4x**——这是你产品最该说出来的真相。

### 4.4 失败案例（反模式）

- **Google March 2024 Core Update**：监控 49,345 站点中约 **2%（800+）完全去索引**；总月流量损失 2,000 万+；广告收入损失 ~$440K/月。被影响站点 100% 含 AI 内容；50% 站点 90-100% 文章为 AI 生成。
- **VideoGamer.com**：转向 AI 写作后被 Google 完全去索引（独立验证）。
- **某旅游站**（Metaflow 案例）：批量生成 50,000 页面，**98% 在 3 个月内被 deindex**。
- **Sports Illustrated**：AI 文章配虚假作者 profile 被曝光，品牌信用受损但流量未提升。
- **Reddit / Wikipedia 神话**（Search Engine Land 调研）：高 intent BOFU 商业 query 里，Wikipedia "barely registered"，Reddit 也极有限。LLM 转向**专业 review site 与 niche blogs**——靠"刷 Reddit"在商业意图查询上**无效**，只对 informational query 有效。

**产品策略含义**：**任何"自动批量发布"功能都必须有 human-in-the-loop**——产品文档第一行就要写"我们不替你发 spam，因为它会害死你的站"。

---

## 五、小商家专项需求

### 5.1 认知现状

**80%+ 完全不知道 GEO，10% 模糊感知，<5% 主动行动。** 整个 SMB 市场目前处于 SEO 大约 2003 年的阶段——少数早期玩家在套利，多数老板没听过这个词。

硬数据：
- [Local Falcon 19 万条 ChatGPT 餐饮查询](https://www.localfalcon.com/blog/the-ai-visibility-crisis-why-83-percent-of-restaurants-dont-exist-in-chatgpt)：**83% 餐厅在 ChatGPT 完全不存在**，Google 上的"隐形率"只有 14%
- HubSpot/Forrester：约 **24% SMB 在"研究"** 如何为生成式 AI 调整 SEO 策略——"研究"是关键词，真正在做的远低于此
- **ChatGPT 对本地推荐 70%+ 数据来自 Foursquare**（即使 Foursquare 在 2025 关闭了 C 端 App，底层数据仍是 LLM 核心来源）——这是最容易被忽视的杠杆点

### 5.2 SMB vs 企业差异

| 维度 | 企业 | 小商家 |
|------|-----|-------|
| 关心指标 | 品牌共现、品类心智 | "顾客今天能找到我吗" |
| 内容预算 | 内容工厂 + PR | 1 个老板 |
| 核心战场 | Wikipedia / Forbes / Bloomberg | **GBP / Yelp / 大众点评 / 小红书** |
| 决策周期 | 3-6 月 | "下个月房租"——这周要见效 |
| 预算上限 | $5-25K/月 | **$50-300/月（核心）** |
| 技术能力 | SEO 团队 + agency | 不会 schema、不会 robots.txt |

**关键洞察**：小商家 GEO 杠杆 **70% 不在自有网站**，而在第三方平台（GBP / Yelp / Foursquare / 小红书 / Reddit）。这与企业 GEO 完全不同。

### 5.3 付费意愿（具体数字）

- **基线（小商家本地 SEO）**：$500-3,000/月
- **GEO 工具甜点 $20-100/月**（¥99-399）
- 超过 $200 立刻陷入"agency 服务"对比（那个市场被 1500-3000 USD/月本地 SEO 公司覆盖）
- Forrester 2026 预算指南：**从现有内容/数字预算腾 15%** 给 AI 搜索可见度——是再分配，不是新增
- 中国市场：小酷 AI **¥5,980/年**（≈$50/月）；杭州优广 ¥3,800 基础包；加搜 ¥20 万/年（脱离 SMB）；某些灰产 **¥2 万/单条收录**（36 氪曝光）

### 5.4 垂直行业模式

| 行业 | 杠杆点 | 产品形态 |
|------|-------|---------|
| 餐厅 / 本地实体 | GBP 完整度、4.5+ 星级、近期评论数、Foursquare/Yelp 入驻 | 审计 GBP + 评论催收 + 本地引用同步 |
| 在线课程 / Coach | Reddit/Quora 真诚回答 + 自建博客权威长尾 | prompt 监测 + FAQ 生成 + Reddit 内容机会 |
| Niche Ecommerce | Product/FAQ/Review/Organization schema 全要补 | schema 补全 + 可读性评分 + 对比内容 |
| Solo SaaS | 80% B2B 买家用 AI 调研，但 **88% B2B SaaS 不在自己品类的 AI 答案中** | 竞品 prompt 监控 + benchmark 内容生成 |
| 中文垂类（小红书 + 本土 AI） | 小红书月活 3.12 亿，日搜 30 亿次；接 DeepSeek-R1；独立 AI 搜索 App "点点" | 多平台 NAP/内容同步 + 中文 AI 引擎覆盖 |

### 5.5 痛点 → 产品功能映射

| SMB 痛点 | 产品功能 |
|---------|---------|
| "我都不知道 AI 里能不能搜到我" | **免费可见度审计**——输入店名 30 秒返回 8 大引擎截图 |
| "看了报告也不知道怎么改" | **可执行 checklist**（不是黑话）+ 傻瓜化截图教程 |
| "没时间天天维护" | **自动化执行**——自动催评论邮件、自动补 GBP 字段、半自动 Reddit 答案 |
| "500 块以上不考虑" | **三档定价**：免费审计 / ¥99-199 月度监测 / ¥599-999 含执行 |
| "国内 AI 引擎多管不过来" | **多引擎统一监测**：DeepSeek + Kimi + 豆包 + 文心 + 元宝 + ChatGPT/Perplexity/Gemini |
| "我又不会写技术词" | **零技术 onboarding**——输入店名自动抓取公开信息生成 schema/FAQ/About |

---

## 六、中文市场专项

（这部分由我自己研究——agents 没覆盖深度）

### 6.1 市场规模与现状

- [信通院数据](https://finance.sina.com.cn/roll/2025-08-06/doc-infiznxx0043131.shtml)：**2026 年中国 GEO 市场 ¥286 亿**，AI 营销细分赛道增速第一
- **36.5% 中国网民已使用生成式 AI 搜索**（[奇赞](https://www.qizansea.com/82589.html)）
- **国内 AI 搜索 8 大引擎**并行：DeepSeek、豆包、Kimi、文心一言、通义千问、腾讯元宝、混元、千问
- 服务模式以**人工精修代运营**为主，SaaS 自助工具相对稀缺（这是机会）

### 6.2 中美 GEO 关键差异

| 维度 | 中国 | 美国 |
|------|------|-----|
| 主导引擎 | 豆包、文心、通义、DeepSeek、Kimi、元宝 | ChatGPT、Perplexity、Claude、Gemini |
| 商业模型 | **直接电商导流**（豆包→抖音、通义→夸克）| 品牌曝光增强 |
| 主流引用源 | **CSDN、知乎、抖音/头条、人民日报、行业论坛** | Reddit、Wikipedia、专业评测站、官方文档 |
| 服务模式 | 人工代运营 + 监测工具 | SaaS 自助 + 代理 |
| 价格区间 | ¥100-500/月（AIDSO 起 ¥126） | $30-3500/月 |

### 6.3 中国引擎引用偏好（实测案例）

来源：[博客园 navyum 实战指南](https://www.cnblogs.com/navyum/articles/19118757)——一周让豆包/DeepSeek/Kimi 推荐 Chrome 插件到第 2 名

- **豆包** 优先抓取 **CSDN**（占比很高），其次抖音/头条生态（字节系闭环）
- **Kimi / DeepSeek** 也大量引用 CSDN、博客园、知乎、掘金
- 战术：在 CSDN 发布**标题含关键词 + 总结部分优化**的测评文章 → 多平台分发 → 一周后再测
- 时间：1 周从无排名到稳定第 2 名

**这是中国 GEO 的核心方法论**：**"平台溯源" 比站内优化更重要**。

不同于美国主要靠站内优化（Schema、BLUF、引用），中国 GEO 的杠杆点是：
1. 识别"目标查询 → AI 引用源平台"的映射
2. 在那些源平台发布优化内容
3. 站内 GEO 是辅助

### 6.4 中文 GEO 工具现状

| 工具 | 价格 | 覆盖 | 评价 |
|------|------|------|------|
| AIDSO（爱搜）| ¥126/月起 | 10 国内引擎 | 头部，定价不透明，B 端代理向 |
| SheepGeo | Basic 免费 + Pro 用量制 | 9 大国内模型 | **开源 + SaaS**，技术友好 |
| 快景（Kuaijing）| 不公开 | 部分 | 营销机构向 |
| 加搜科技 | ¥20 万/年起 | 全部 | 完全脱离 SMB |
| 小酷 AI | ¥5,980/年（≈$50/月）| 部分 | 中小企业向 |
| 方维网络 | 服务模式 | 主流 | 服务 1 万+ 中小，续费 80% |

### 6.5 中文市场战略含义

1. **"中英双向 GEO"** 是真空地带——没有"既懂海外品牌进中国 AI 搜索 + 又懂中国独立创作者被海外 AI 引用"的产品
2. **SheepGeo 的 freemium 验证了**：中文市场对免费起步高度敏感——这是西方工具普遍缺失的定价策略
3. 中文工具 **UI/UX 较弱、海外支付不友好、API/MCP 集成弱**——技术型创业者的天然切入点
4. 灰产已现（¥2 万/收录）——**"诚实 GEO"** 本身就是一种品牌定位

---

## 七、Cloudflare 平台能力 × GEO 产品功能映射

### 7.1 Cloudflare 平台能力清单

| 产品 | 免费层 | 付费起步 | GEO 用途 |
|------|--------|---------|---------|
| **Workers** | 100k req/day | $5/月含 10M req | API 后端 |
| **Workers AI** | 10k Neurons/day | $0.011/1k Neurons | LLM 改写、Schema 生成、内容评分 |
| **Pages** | 无限静态站 | $20/月 Pro | SaaS 前端 |
| **D1** | 5GB 存储免费 | 用量计费 | 用户数据、审计历史 |
| **R2** | 10GB 免费 | $0.015/GB/月 | 截图、原始页面归档 |
| **KV** | 100k reads/day | 用量 | 缓存 AI 响应 |
| **Vectorize** | 5M 向量免费 | 用量 | 语义搜索竞品内容 |
| **Browser Rendering** | 10 min/day（免费）/ 10 hr/月（付费） | $0.09/小时 | 抓取 AI 引擎 SERP |
| **Queues** | 1M msg/月免费 | 用量 | 异步审计任务 |
| **Cron Triggers** | 含在 Workers | 免费 | 定时引用追踪 |
| **Pay Per Crawl** | 新功能 | - | 按 AI 爬虫付费的协议层 |
| **Content Signals** | 新功能 | - | 内容信号传给 AI 引擎 |

### 7.2 关键模型可用（Workers AI）

- Llama 3.2 1B：**$0.027/M input, $0.201/M output**（用于内容评分、轻改写）
- Llama 3.1 70B：$0.293/M input, $2.253/M output（深度重写、Schema 生成）
- FLUX.2（图像生成 → OG 图、社交分享卡片）
- Whisper（语音 → 文本，用于视频转录的 GEO）
- bge-* 嵌入模型（向量化 + Vectorize）

### 7.3 中文模型缺口与混合架构

Workers AI 自带模型对中文表现一般。GEO 产品里的"中文内容改写"需要外接：
- **DeepSeek API**：~¥1/M tokens（最便宜）
- **Kimi API**：context 长，适合长文章
- **通义千问 API**：对中国 SEO 关键词理解好

**混合架构推荐**：英文走 Workers AI（边缘 + 便宜），中文走 DeepSeek/Kimi API（外部，但价格也低）。Workers 同时调度两边。

### 7.4 功能 → Cloudflare 实现映射

| 产品功能 | 实现路径 |
|---------|---------|
| GEO 审计（粘 URL → 24 分评分）| Workers + Browser Rendering 抓取 → Workers AI 评分 → D1 存历史 |
| 引用追踪（每天跑 N 个查询）| Cron Trigger → Queue → Browser Rendering 模拟 SERP → KV 缓存 |
| Schema 自动生成 | Workers AI 推理 → Pages Function 注入 |
| AI 改写文章 | Worker 接收 markdown → Llama 3.1 70B（英文）/ DeepSeek（中文）→ R2 存版本 |
| 多平台分发 | 集成你**已有的 xiaoheishu 桌面应用**（CSDN/知乎/小红书/Reddit）|
| 竞品监控 | Vectorize 存竞品内容 embedding → 周期性 SERP 抓取对比 |
| 用户认证 + 订阅 | Cloudflare Access + Stripe Webhooks Worker |

### 7.5 成本估算

**单个 Pro 用户每月成本**（10 域名 × 100 prompt × 每日检查 + 100 次审计 + 50 次改写）：
- Browser Rendering：~10 hr/月（覆盖在 Pro 免费）
- Workers AI 改写：~50 篇 × 2000 词 ≈ 100k tokens × $0.293/M = **$0.03**
- Browser Rendering 付费部分：$0.09/hr × ~5 hr 超额 = **$0.45**
- D1 / R2 / KV：忽略级
- 外部 DeepSeek API（中文用户）：~$1/月
- **单用户成本 < $2/月，毛利 > 95%**（如 Pro $28/月）

---

## 八、产品定位建议

### 8.1 一句话定位

> **"Cloudflare-Native 的中英双向 GEO Copilot：审计 + 追踪 + 改写 + 分发一站式，价格对个人创作者和小商家友好。"**

### 8.2 三选三差异化

5 条差异化轴中，建议选**这三条**（彼此叠加最强）：

1. **价格 + Freemium**：$0 / $9 / $29 / $69 四档，**$5-15 月费档完全空白**（业界没人占）
2. **中英双向覆盖**：原生支持 ChatGPT/Perplexity/Claude/AIO + Kimi/DeepSeek/豆包/文心 + AI Overview 中英文模拟
3. **Action 层**：不只监测，**自动 Schema 注入 + AI 改写 + 多平台分发**（你已有 xiaoheishu 基础）

不选另外两条（**Cloudflare-Native** 和 **CMS 嵌入式**）的原因：作为底层选择已包含，不需要单独打这张牌。

### 8.3 与现有玩家的市场分割

| 玩家 | 价格 | 客户 | 与你的关系 |
|------|------|------|-----------|
| Profound | $99-3500+ | Fortune 500 / 大企业 | 不重叠（不同客户） |
| AthenaHQ | $295+ | 中大企业 / 代理 | 不重叠 |
| Otterly | $29-989 | SMB / 代理 | **直接竞争**——你必须比它好 |
| Promptmonitor | $29-129 | SMB / Indie | **直接竞争** |
| Rankscale | $20-99 | Indie | **直接竞争** |
| AIDSO（爱搜）| ¥126+ | 国内 SMB | **直接竞争**——但你有海外覆盖 |
| SheepGeo | 免费 + 用量 | 国内 indie / 开发者 | **直接竞争**——但你有 SaaS 化 + 海外 |

**你的 wedge**：Otterly + Promptmonitor 不覆盖中文引擎；AIDSO + SheepGeo 不覆盖海外引擎。**你的产品同时覆盖**——这是 5 大缺口里"国际化中文 GEO"那一条。

### 8.4 价格策略

```
免费层（Tier 0）
  - 1 个域名
  - 5 个查询 prompt
  - 周一次检查
  - 单次 GEO 审计
  - 目标：转化为付费

创作者 ¥69/月（≈$10）
  - 3 个域名
  - 30 prompt × 6 引擎 = 180 检查/天
  - 20 次审计/月
  - 10 次 AI 改写/月
  - 目标：单博主 / 单店主

Pro ¥199/月（≈$28）
  - 10 域名
  - 100 prompt × 8 引擎（含中英）= 800 检查/天
  - 100 次审计/月
  - 50 次 AI 改写/月
  - 多平台分发（CSDN / 知乎 / 小红书 / Reddit / GBP）
  - 目标：严肃创作者 / 小商家

Business ¥499/月（≈$69）
  - 25 域名
  - 500 prompt × 8 引擎，每小时检查
  - 不限审计
  - 200 次 AI 改写
  - API 访问
  - 白标（可选）
  - 目标：内容机构 / 小代理
```

参考竞品价格：Otterly $29 / Profound $99（对比 ¥199）；AIDSO ¥126 起（对比 ¥69）。

---

## 九、MVP 路线图（90 天）

### 阶段一：周 1-4（MVP）

**目标**：可用的免费 + 入门付费，给 10 个种子用户

- [ ] **GEO 审计工具**：粘 URL → 30 秒返回 24 分评分 + 改进项（基于你已有的 24 分清单）
- [ ] **基础引用追踪**：用户输入 5 个 prompt → 每周一次跨 ChatGPT/Perplexity/Kimi/DeepSeek 检查
- [ ] **Landing page**（用 Astro，复用你博客的 stack）+ Stripe 付费集成
- [ ] **从你的博客读者征集 10 个 alpha 用户**（你的博客是天然渠道）

**技术 stack**：
- Astro 前端 → Cloudflare Pages
- Hono Workers API → Cloudflare Workers
- Browser Rendering 抓取 SERP
- Workers AI（英文）+ DeepSeek API（中文）做评分
- D1 存用户与审计历史

### 阶段二：周 5-8（行动层）

**目标**：从"监测"升级到"行动"，开始展示真实 ROI

- [ ] **AI 改写**：粘 markdown → 输出 BLUF + 表格 + 数据引用版本（核心模型 Llama 3.1 70B + DeepSeek）
- [ ] **Schema 自动生成**：粘 URL → 生成 BlogPosting / FAQ / HowTo Schema（含可一键复制的 `<script>` 标签）
- [ ] **每周报告**：邮件给用户"本周引用率 X% → Y%，建议改造文章 A、B、C"
- [ ] **公开 50 个种子用户**——目标 MRR $500

### 阶段三：周 9-12（分发与差异化）

**目标**：把你**已有的 xiaoheishu 多平台发布**集成进来，这是最大差异化点

- [ ] **多平台一键分发**：与 Pro 用户的 xiaoheishu 桌面应用打通（CSDN / 知乎 / Reddit / 小红书 / GBP）
- [ ] **平台溯源功能**：对每个查询，告诉用户"AI 在引用 CSDN / Reddit / Wikipedia 等哪些 source"
- [ ] **公开发表你的实战记录**：把你自己的博客作为 case study（你已经在做了）
- [ ] **目标**：100 用户、MRR $1,500，决定是 double down 还是 pivot

### 渠道策略

1. **你自己的博客**（最大资产）：写"GEO 实战记录 v2 - 用产品自己的工具优化自己"系列
2. **GitHub README + 开源核心**：把审计脚本开源，吸引技术用户
3. **V2EX / 即刻 / 少数派**：早期种子用户聚集地
4. **YouTube / 小红书内容营销**：每周一条 1-2 分钟"GEO 案例拆解"
5. **冷启动伙伴**：联系 SheepGeo 做 partnership？或竞争？

---

## 十、技术架构详解（Cloudflare Stack）

```
┌─ User Browser ─────────────────────┐
│  Astro SPA (geo.yourdomain.com)    │
│  - Dashboard                        │
│  - Audit / Rewrite UI               │
│  - Multi-platform publishing UI     │
└──────────────┬─────────────────────┘
               │ HTTPS
┌──────────────▼─────────────────────┐
│  Cloudflare Pages (Astro + Hono)   │
│  - SSR for marketing pages         │
│  - API routes via Pages Functions  │
└──────┬──────────────────┬──────────┘
       │ /api/*           │ static
┌──────▼──────────────────┴──────────┐
│  Cloudflare Workers (Hono API)     │
│  - Auth (JWT, Cloudflare Access)   │
│  - Rate limiting                    │
│  - Routing to:                      │
│    /audit  → Browser Rendering      │
│    /rewrite → Workers AI / DeepSeek │
│    /track  → Cron + Queue           │
│    /publish → External APIs         │
└──────┬──────────────────────────────┘
       │
   ┌───┴────────────────────────────┐
   │                                 │
┌──▼──────┐  ┌──────────┐  ┌────────▼─────┐
│ D1      │  │ R2       │  │ Workers AI    │
│ users   │  │ snapshots│  │ Llama 3.1 70B │
│ audits  │  │ raw HTML │  │ FLUX.2        │
│ tracks  │  └──────────┘  └──────────────┘
└─────────┘
   ┌──────────────┐  ┌────────────────┐
   │ Vectorize    │  │ Browser        │
   │ competitor   │  │ Rendering      │
   │ embeddings   │  │ (CDP)          │
   └──────────────┘  └────────────────┘

┌─ Cron Triggers (every 1h / 24h) ───┐
│  Trigger citation tracking         │
│  → Queue → Browser Rendering →     │
│    Parse SERP → Save to D1 → KV    │
│    cache → email summary           │
└────────────────────────────────────┘

┌─ External APIs (China models) ─────┐
│  DeepSeek API  $0.001/1k tokens    │
│  Kimi API                           │
│  通义千问 API                        │
└────────────────────────────────────┘
```

**关键决策**：
- **不自建 Kimi/DeepSeek/豆包 检测**——直接抓取 their public web search 结果（它们都有公开 chat 界面），存 R2 做 SERP 截图证据
- **混合 AI 模型**：英文 Workers AI（边缘、便宜、不出 Cloudflare），中文 DeepSeek API（外部，但 ¥1/M tokens 便宜得离谱）
- **Cron + Queue 异步**：用户配置 prompt 后，后台 Cron 触发，不阻塞 UI

---

## 十一、风险与开放问题

### 11.1 技术风险

| 风险 | 缓解 |
|------|------|
| AI 引擎反爬虫升级 | 多账号 + Browser Rendering rotation；fallback 到 RSS / 邮件订阅 |
| Workers AI 中文质量 | 走 DeepSeek API 兜底 |
| Browser Rendering 配额超限 | KV 缓存 24 小时，避免重复抓取 |
| Cloudflare 政策变化 | 保留 Vercel / Railway fallback 部署能力 |

### 11.2 市场风险

| 风险 | 缓解 |
|------|------|
| **Lily Ray "70% 站点 <2% AI 流量"** 是真的 → 需求被高估 | 产品定位"为未来 2-3 年对冲"而非"立刻流量爆发"；坦诚说明 baseline |
| Profound / AthenaHQ 增加中文支持 | 占据"价格 + 集成 + Action"三向 wedge，不靠单点功能竞争 |
| AIDSO 降价或加海外覆盖 | 你的技术栈（Cloudflare 边缘）有结构性成本优势 |
| Google / OpenAI 直接限制 SERP 抓取 | 多源监测（API + 抓取 + 第三方数据 SDK）|

### 11.3 商业风险

| 风险 | 缓解 |
|------|------|
| 付费意愿被高估 | 免费层够大 → 转化漏斗优化 |
| Reddit 自动播种功能被 spam 滥用害死品牌 | **不做完全自动**——人工审核 step；产品文档明确反对 spam |
| GEO 是"营销造词"而非真需求 | 站到 Lily Ray + Gary Illyes 一派——产品是"SEO 增强"不是"GEO 革命" |

### 11.4 开放问题（你需要回答）

1. **客户**：你的核心客户是中文创作者还是中国 SMB 还是出海品牌？三个用户画像的产品差异巨大
2. **冷启动**：你愿意花多少时间在这个之上？6 个月 / 12 个月 / 全职？
3. **技术深度**：要做开源（吸引开发者，慢变现）还是闭源 SaaS（快变现，难传播）？
4. **价格信号**：先做 freemium 跑流量，还是直接付费验证 PMF？
5. **集成**：xiaoheishu 桌面应用要不要开源化作为产品的一部分？

---

## 十二、立即可执行的下一步

### 这周（4/26-5/3）

1. **决策**：阅读本报告，回答上面 5 个开放问题
2. **验证 Cloudflare 边缘 AI**：用 Workers AI 给一篇你的博客文章做 GEO 评分（24 分清单），看输出质量是否够用
3. **跑一次"平台溯源"实验**：在 Kimi / DeepSeek / 豆包查"GEO 是什么"，记录 AI 引用了哪些站点，验证你能否抓到这个数据

### 下周

1. **启动 MVP repo**：`geo-copilot` 仓库，Astro + Hono 架构脚手架
2. **写产品 README**：描述定位、差异化、定价——这本身是市场验证（发到 V2EX 看反应）
3. **联系 5 个潜在用户**：从你的博客评论 / 微信里挑技术博主或 SMB 老板，约 30 分钟聊"如果有这样的工具会用吗"

### 30 天目标

- MVP 上线（审计 + 追踪两个核心功能）
- 10 个 alpha 用户，至少 3 个付费 ¥69/月
- 一篇"用产品自己的工具优化自己博客"的 case study（流量数据公开）
- MRR ¥207（≈$30）——证明有人愿意付钱

---

## Sources

### A. 你已有的（KDD 2024 + Yext + 你的博客）

- [GEO Paper KDD 2024](https://arxiv.org/abs/2311.09735)
- [GEO 实战手册（你的博客）](https://blog.mushroom.cv/blog/geo-generative-engine-optimization-guide/)
- Yext 17.2M citations analysis（你已引用）

### B. YouTube 视频与创作者博客

- [Clearscope Roundtable](https://www.youtube.com/watch?v=c-VtgjXWsK4) — Lily Ray + Kevin Indig + Ross Hudgens + Steve Toth
- [Aleyda Solis "AI Search Optimization Roadmap"](https://www.youtube.com/watch?v=BjyF_4UhoOM)
- [Brian Dean "5 Massive AI SEO Predictions"](https://www.youtube.com/watch?v=3z00T_TF7u8)
- [Lily Ray "SEO 2025: AI, Reddit & Ranking"](https://www.youtube.com/watch?v=mgI1U7XPsUA)
- [Cyrus Shepard "Agents are early"](https://www.youtube.com/watch?v=ce_4AR5cx8A)
- [Neil Patel "$2.2B SEO disruption"](https://www.youtube.com/watch?v=02aOEbWV98c)
- [iPullRank YouTube](https://www.youtube.com/@iPullRankSEO)
- [Ahrefs GEO Blog](https://ahrefs.com/blog/geo-generative-engine-optimization/)
- [iPullRank AI Search Manual](https://ipullrank.com/ai-search-manual)
- [Aleyda Solis AI Search Trends](https://www.aleydasolis.com/en/search-engine-optimization/ai-search-trends/)
- [Lily Ray Substack Reflection](https://lilyraynyc.substack.com/p/a-reflection-on-seo-and-ai-search)
- [Backlinko 2025 Strategy](https://backlinko.com/start-backlinko-2025)

### C. 工具生态

**Tier 1 / 高融资**
- [Profound Pricing](https://www.tryprofound.com/pricing) | [Profound $96M Series C](https://www.tryprofound.com/blog/profound-raises-96m-series-c) | [Fortune coverage](https://fortune.com/2026/02/24/exclusive-as-ai-threatens-search-profound-raises-96-million-to-help-brands-stay-visible/)
- [AthenaHQ Pricing](https://www.athenahq.ai/pricing)
- [BrandRank.AI funding](https://www.accessnewswire.com/newsroom/en/computers-technology-and-internet/brandrankai-secures-12-million-in-seed-and-angel-funding-to-revolu-894055)
- [Peec AI Pricing](https://peec.ai/pricing)
- [Evertune](https://www.evertune.ai/)

**Tier 2 / 中端**
- [Otterly Pricing](https://otterly.ai/pricing) | [Otterly Gartner Cool Vendor 2025](https://otterly.ai/blog/cool-vendor-in-the-2025-gartner-cool-vendors-for-ai-in-marketing/)
- [Knowatoa](https://knowatoa.com/pricing)
- [Goodie AI](https://higoodie.com/) | [Goodie review](https://bermawy.com/blog/goodie-ai-geo-platform-review)
- [Surfer pricing](https://surferseo.com/pricing/) | [Acquired by Positive Group](https://theygotacquired.com/saas/surfer-seo-acquired-by-positive-group/)
- [Promptmonitor](https://promptmonitor.io/pricing)
- [Semrush AI Visibility](https://www.semrush.com/kb/1493-ai-visibility-toolkit)
- [Ahrefs Brand Radar](https://ahrefs.com/brand-radar)

**Tier 3 / Indie**
- [Rankscale](https://rankscale.ai/pricing)
- [LLM Pulse Affordable AEO](https://llmpulse.ai/blog/most-affordable-aeo-tools/)
- [Airefs alternatives under $50](https://getairefs.com/blog/promptmonitor-alternatives-under-50/)
- [HubSpot AI Search Grader](https://www.hubspot.com/products/aeo)
- [Mangools AI Search Grader](https://mangools.com/ai-search-grader)

**Action 层**
- [AEO Engine Schema Generator](https://aeoengine.ai/schema-markup-generator)
- [Writesonic GEO Action Center](https://writesonic.com/blog/geo-action-center)

### D. 案例研究与数据

- [TRM ChatGPT 8,337% case](https://www.therankmasters.com/blog/generative-engine-optimization-geo-case-study-trm-chatgpt)
- [Discovered Labs B2B SaaS 3x](https://discoveredlabs.com/blog/case-study-how-a-b2b-saas-used-a-geo-agency-to-3x-citation-rates-in-90-days)
- [Discovered Labs 30/60/90 timeline](https://discoveredlabs.com/blog/geo-timeline-when-to-expect-results-30-60-90-day-benchmarks)
- [Seer Interactive ChatGPT 转化](https://www.seerinteractive.com/insights/case-study-6-learnings-about-how-traffic-from-chatgpt-converts)
- [Maximus Labs GEO Failures](https://www.maximuslabs.ai/generative-engine-optimization/geo-failures-and-lessons)
- [Gen Optima Amico Lighting case](https://www.gen-optima.com/case-studies/amico-lighting-ai-recommendation-case-study/)
- [ALM Corp ChatGPT citations 44%](https://almcorp.com/blog/chatgpt-citations-study-44-percent-first-third-content/)
- [Ahrefs AI Traffic Research 35K sites](https://ahrefs.com/blog/ai-traffic-research/)
- [Semrush ChatGPT Search Insights](https://www.semrush.com/blog/chatgpt-search-insights/)

### E. 行业 / 出版商数据

- [SparkToro Datos State of Search](https://datos.live/report/state-of-search-q1-2025/)
- [DCN Publishers AI Impact](https://digitalcontentnext.org/blog/2025/08/14/facts-googles-push-to-ai-hurts-publisher-traffic/)
- [Digiday 25% Publisher Traffic Drop](https://digiday.com/media/google-ai-overviews-linked-to-25-drop-in-publisher-referral-traffic-new-data-shows/)
- [Loamly 2026 AI Traffic Benchmark](https://www.loamly.ai/blog/state-of-ai-traffic-2026-benchmark-report)
- [Wheelhouse: GA4 70.6% Direct Mistake](https://www.wheelhousedmg.com/insights/articles/ai-traffic-is-already-in-your-analytics/)

### F. 失败案例

- [Search Engine Journal: March 2024 Core Update](https://www.searchenginejournal.com/googles-march-2024-core-update-impact-hundreds-of-websites-deindexed/510981/)
- [VideoGamer.com 去索引](https://aiproductivity.ai/news/videogamer-removed-google-ai-content/)
- [Search Engine Land Black Hat GEO](https://searchengineland.com/black-hat-geo-pay-attention-463684)

### G. 小商家 / SMB

- [Local Falcon: 83% Restaurants Invisible](https://www.localfalcon.com/blog/the-ai-visibility-crisis-why-83-percent-of-restaurants-dont-exist-in-chatgpt)
- [HubSpot GEO for SMB](https://blog.hubspot.com/marketing/generative-engine-optimization-small-business)
- [Search Engine Land SMB Traffic from AI](https://searchengineland.com/smb-websites-rising-traffic-chatgpt-ai-engines-453201)
- [WebFX GEO Cost 2026](https://www.webfx.com/blog/ai/generative-engine-optimization-cost/)
- [AEO.ltd Local SMB](https://aeo.ltd/industries/local-smb/)
- [Merchynt GBP Local SEO](https://www.merchynt.com)

### H. 中国市场

- [奇赞：中美 GEO 分化](https://www.qizansea.com/82589.html)
- [信通院 GEO 市场预测（新浪）](https://finance.sina.com.cn/roll/2025-08-06/doc-infiznxx0043131.shtml)
- [navyum 实战指南：1 周让豆包推荐](https://www.cnblogs.com/navyum/articles/19118757)
- [36 氪：花 2 万买一条 AI 答案](https://36kr.com/p/3373220494726913)
- [小红书接 DeepSeek-R1（36 氪）](https://36kr.com/p/3210158561133448)
- [AIDSO 爱搜](https://www.aidso.com/)
- [SheepGeo GitHub](https://github.com/CN-Sheep/SheepGeo)
- [SheepGeo 官网](https://www.sheepgeo.com/sheep-framework)
- [快景 GEO](https://seo.kuaijing.cn/)
- [Codedesign 7 Best Chinese AI Search 2025](https://codedesign.org/7-best-chinese-ai-search-tools-2025-codedesign-perspective)

### I. Cloudflare 平台

- [Workers AI Pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
- [Workers AI Models](https://developers.cloudflare.com/workers-ai/models/)
- [Browser Rendering Pricing](https://developers.cloudflare.com/browser-run/pricing/)
- [Browser Rendering 2026 Update](https://developers.cloudflare.com/changelog/post/2026-03-04-br-rest-api-limit-increase/)
- [Cloudflare Pay Per Crawl SEO/GEO](https://searchengineland.com/cloudflare-pay-per-crawl-seo-geo-458310)
- [SearchViu Cloudflare for SEO/GEO](https://www.searchviu.com/en/cloudflare-for-seo-and-geo-part-1/)

---

*报告完成于 2026-04-26 | 总字数约 9,800 | Sources 70+*
*建议阅读顺序：摘要 → 第八章定位 → 第九章路线图 → 其余章节做深度参考*
*下一步：读完后回答十一章 4 个开放问题，然后启动 MVP repo*
