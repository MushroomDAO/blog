# 附录：8 位 GEO 顶级创作者深度档案

> 这是对主报告 [REPORT.md](./REPORT.md) §2.1（YouTube 视频清单）的深度补充。
> 4 个并行 agents 系统性深读了 iPullRank、Growth Memo、Backlinko、Aleyda 个站、Lily Ray Substack、Zyppy 等创作者博客 + Ahrefs 数据集 + Search Engine Land 5 篇关键文章。
> 完整原始档案在 [raw/](./raw/) 文件夹。

---

## 速查：8 位创作者立场对照

| 创作者 | 立场 | 核心独特概念 | 立场倾向 |
|-------|------|-------------|---------|
| **Aleyda Solis** | 拥抱式整合 | 10 步 AI Search Optimization Roadmap | "GEO = SEO 工具箱新工具" |
| **Lily Ray** | 反共识批判 | "AI Slop Loop"、Listicle 惩罚案例 | "GEO 是 SEO 延伸+多数 GEO 战术是 grift" |
| **Mike King (iPullRank)** | 工程派 / 政治派 | **Relevance Engineering**、**Query Fan-Out** | "重新定义行业，用 IR 替换 SEO" |
| **Kevin Indig (Growth Memo)** | 实证派 / 数据派 | **Ski Ramp Pattern**、**Ghost Citation Problem** | "用数据打脸营销话术" |
| **Brian Dean (Backlinko)** | 实操叠加派 | **LLM Seeding** + 7 大内容格式 | "GEO 在好 SEO 基础上叠加" |
| **Cyrus Shepard (Zyppy)** | 品牌派 / 反共识 | **"Brand is the play"**、HCU = anti-SEO | "80% 的人不需要单独追踪 AI" |
| **Neil Patel** | 多平台叙事派 | **Search Everywhere Optimization** | "GEO converts like crazy" |
| **Ross Hudgens (Siege)** | 持续输出派 | **2x 内容**（不是 10x）、首页 +10.7% 研究 | "AI Overviews 让首页变成新 SERP" |

---

## 一、关键概念定义（深度补充主报告）

### 1.1 Relevance Engineering（Mike King 标志概念）

> "Relevance engineering is the confluence of artificial intelligence, information retrieval, content strategy, ux, and digital pr." — [BuzzStream Podcast](https://www.buzzstream.com/blog/relevance-engineering-podcast/)

**5 学科融合**（不是 SEO 换皮）：
1. Information Retrieval（信息检索）— 向量空间、cosine similarity、dense retrieval
2. User Experience — 信息架构、可扫描性
3. Artificial Intelligence — embeddings、LLM 推理、RAG pipeline
4. Content Strategy — passage-level 设计
5. Digital PR — 基于语义相关性的链接建设

**iPullRank 主页口号**：**"We Don't Offer SEO. We offer Relevance Engineering."**

### 1.2 Query Fan-Out（AI 搜索的"暗机制"）

来源：[Tech SEO Connect 2025 演讲](https://speakerdeck.com/techseoconnect/michael-king-everything-you-mfs-should-know-about-query-fan-out)

**机制**：用户的一个 prompt → Google AI Mode 内部 Gemini 重写成 **8-28 个合成子查询** → 并行检索 → 合成最终答案

**关键数据**：
- Gemini 平均生成 **10.7 queries per prompt**（峰值 28）
- **95% 的合成子查询零月度搜索量** — 传统 SEO 工具完全看不到
- iPullRank 内部测试：单查询出现引用率 **9.7%**，**7+ 出现引用率 80%+**
- ChatGPT 引用中 **62% 来自非 Google 源**
- **28.3% 的被引用页面没有自然排名**

**"Raffle"（彩票）类比**：
> "AI search is like a raffle. We don't control the synthesis pipeline—all we control is the inputs. The more synthetic subqueries you rank for, the more raffle tickets you have."

**6 类合成子查询**：Related / Implicit / Comparative-Recent / Personalized / Reformulation / Entity-Expanded

### 1.3 Ski Ramp Pattern（Kevin Indig 实证）

来源：[The Science of How AI Pays Attention](https://www.growth-memo.com/p/the-science-of-how-ai-pays-attention) — **1.2M ChatGPT 响应分析，p < 0.0001**

- **44.2% 引用来自页面前 30%**（intro）
- 31.1% 来自中段
- 24.7% 来自最后 1/3
- **段落内：53% 引用在段落中部**，24.5% 首句，22.5% 末句

### 1.4 Ghost Citation Problem（Indig 454 prompt 实验）

来源：[The Ghost Citation Problem](https://www.growth-memo.com/p/the-ghost-citation-problem)

- **61.7% 的引用是"ghost citation"**（链接存在但品牌名不出现）
- 只有 13.2% 同时获得引用 + 提及

**LLM 行为差异**（极重要）：
- **Gemini**: 83.7% 提及率 / 21.4% 引用率（**爱提名字，不爱给链接**）
- **ChatGPT**: 87.0% 引用率 / 20.7% 提及率（**爱给链接，不爱提名字**）

**核心洞察**：
> "Comparative content gets brands named. Informational content feeds the machine anonymously."

→ 实操含义：**目标是品牌提及（不只流量），内容策略要偏向 evaluation/comparison，不是纯 informational**

### 1.5 LLM Seeding（Brian Dean 标志方法论）

来源：[LLM Seeding](https://backlinko.com/llm-seeding)

> "LLM seeding is the practice of publishing content in the formats and places LLMs are most likely to scrape, summarize, and cite."

**7 大内容格式**：
1. 结构化 "Best Of" 清单（含选择方法论 + "best for" 评级）
2. 第一人称产品评论（"tested 40+ adjustable desks since 2013"——Wirecutter 案例）
3. 品牌 vs 品牌对比表
4. FAQ 风内容
5. 观点性文章 + 清晰要点
6. 带清晰说明的视觉
7. 工具/模板/框架（免费资源）

---

## 二、关键数据（独立交叉验证）

### 2.1 各 LLM 引用源偏好（终极对照）

| LLM | 最高引用源 | 引用 vs 提及偏好 | 占比 |
|-----|-----------|----------------|------|
| **ChatGPT** | Wikipedia 16.3% | 爱链接（87%）、不爱名字（20.7%） | 检索的 **85%** 从未被引 |
| **Perplexity** | Reddit + YouTube（YT 16.1%）| 中性 | 偏好 30 天内更新 (+38%) |
| **Google AI Overviews** | YouTube 9.5% + Reddit 7.4% + Quora 3.6% | 偏链接 | 76.10% 引用页在 Google top 10 |
| **AI Mode** | "consensus engine" — 所有品牌信号 | 比 ChatGPT 多 17% 提及 | 与 AIO **0.821** 重叠 |
| **Claude** | UGC（社区验证内容） | 偏第一人称 | (Anthropic 数据未公开) |
| **Copilot** | Forbes + Gartner | (低样本) | (低样本) |

**Ahrefs 75K 品牌相关性研究的反共识发现**：
- **YouTube mentions 0.737 是绝对最强信号**（高于品牌网络提及 0.664）
- **内容数量与 AI 可见度几乎无关**（~0.194）
- **品牌网络提及 vs 反向链接：3:1 优势**（0.664 vs 0.218）

### 2.2 Cyrus Shepard 5 大流量赢家特征研究（400 站点，2026/4）

| 特征 | Spearman r | Winners% | Losers% |
|------|-----------|---------|---------|
| Offering Product/Service | **0.391** | 70.2% | 34.6% |
| Allowing Task Completion | **0.381** | 83.7% | 50.2% |
| Proprietary Assets | **0.357** | 92.9% | 57.1% |
| Tight Topical Focus | 0.250 | 75.9% | 61.3% |
| Strong Brand | 0.206 | 32.6% | 16.1% |

**叠加效应**（关键阈值）：
- 0 特征：13.5% 胜率
- 3 特征：30.7%
- **4 特征：68.1%**（**关键阈值**）
- 5 特征：69.7%

### 2.3 Lily Ray Listicle 惩罚案例（独立来源真实数据）

来源：[Is Google Finally Cracking Down on Self-Promotional Listicles?](https://lilyraynyc.substack.com/p/is-google-finally-cracking-down-on)

| 站点 | 行为 | 时间 | 跌幅 | ChatGPT 引用 |
|------|------|------|------|------------|
| $80 亿 B2B 品牌 | 191 篇"best X tools"自家 #1 | 2026/1/21-2/2 | **-49%** | 同步下跌 |
| SaaS | 类似 listicle 滥用 | 同期 | **-43%** | 同步 |
| B2B/B2C SaaS | 同上 | 同期 | **-42%** | 同步 |
| 另一 SaaS | 同上 | 同期 | **-34%** | 同步 |
| 数字营销服务商 | 1 月中旬起 | 1 月中旬 | **-29%** | 同步 |
| 某站 | **51 个 "X alternatives"** 页 | 2026/1 底 | 流量下跌 | **同步下跌** |

**关键模式**：blogs 文件夹占总损失 77-93%；100% AI-generated 检测；违规 `AggregateRating` schema。

### 2.4 Zyppy 写作风格研究（4,000 站点 HCU 分析）

| Winners | Losers |
|---------|--------|
| **22 personal pronouns/页** | **9 personal pronouns/页** |
| ~20% intrusive mobile ads | >50% scrolling ads |
| 原创人物图片 | 库存图 |
| 紧凑话题聚焦 | 全球覆盖 |

→ **"用 22 个 I/we/us 取代 9 个"** 是可立即落地的简单战术。

### 2.5 Kevin Indig 1.2M 响应研究的语言学特征（黄金细节）

- **Definitive language**: 引用胜方 36.2% vs 落败方 20.2%（**"X is Y" 句式提升 14% 引用率**）
- **问号在 H2 中**: 频率高 2x（18% vs 8.9%）
- **Question 引用：78.4% 来自 headings**
- **Entity density**: 引用文本 **20.6% 命名实体** vs. 标准英文 5-8%（**~2.5x 富集**）
- **Subjectivity score**: 0.47（事实+分析平衡）
- **Flesch-Kincaid grade level**: 16（college level）vs. 落败方 19.1（**避免 PhD-level 复杂度**）
- **Big brand penalty**: 大品牌 **0.81x 引用率**（负向信号！）

### 2.6 Aleyda SEOFOMO 2025 调研（最权威 GEO 实践调研）

- **91%** SEO 在过去一年被客户/老板问过 AI 搜索可见度
- **62%** 网站 AI 平台贡献 **0-5% 收入**
- **47%** 已经为大部分网站修改了 SEO 流程纳入 AI
- **75%** 把 AI 搜索的 owner 划给 SEO 团队
- **最常用工具**：Ahrefs(73) > GA4(64) > Semrush(61)

---

## 三、**Google 官方反对 GEO 的三声明**（产品风险）

| 来源 | 时间 | 声明 |
|------|------|------|
| **Gary Illyes** | 多次 | "AI Overviews 用同样的爬虫、同样的索引、同样的排名系统"；"We are not trying to differentiate based on origin" |
| **John Mueller** | 2025/8/14 Bluesky | **"The higher the urgency, and the stronger the push of new acronyms, the more likely they're just making spam and scamming"** |
| **Danny Sullivan** | 2026/1/8 Search Off the Record E102 | **"So we don't want you to do that"**（指 chunking） |

**含义**：你的产品**绝对不能用"GEO"作为唯一卖点**——否则 Google 三位官方代言人都站对立面。建议**用 "Search Optimization for AI Era" 或 "AI Visibility Engineering"** 这类对中性叙事，避免直接撞上"GEO is grift"的公开判断。

---

## 四、AI Slop Loop 实证实验（Lily Ray）

**这本身可以做成产品**——揭露 AI 信息生态自污染。

#### "Pizza" 实验
Ray 发了一篇虚构文章说 **"Google approved the update between slices of leftover pizza"** → **24 小时内 Google AIO 把这条假信息当真信息呈现**

#### "Hot Dogs" 实验（BBC 记者）
发了一篇虚构文章自称 **"#1 best tech journalist at eating hot dogs"** → **24 小时内 Google AIO 和 ChatGPT 都把这条当事实**

#### "September 2025 'Perspectives' Update" 追溯实验
追溯到这是 SEO 代理博客上 AI 编造的虚假算法更新 → Perplexity 引用 → 其他 AI 后续都开始引用 → **几个月后 LLM 仍自信地描述这个不存在的更新**

**机制结论**：**"重复 = 共识"**，AI 没有 fact-check —— 这是产品潜在卖点（揭露并对抗 misinformation loop）。

**Google AIO 准确率**：
- **91% 准确**，但每年 5 万亿次搜索 → 每小时**几千万次错误回答**
- **56% 的"正确"回答是 ungrounded**（源不能完全支持结论）

---

## 五、**关于 BLUF +67% 数据的更正**

主报告 [REPORT.md](./REPORT.md) 第 9 项摘要中提到 "BLUF 改写让页面引用率 +67%" —— **这个数据已被证伪**：

**深度调研结论**：
- Mintcopy 原文（"BLUF: The Ski Ramp Content Strategy"）**没有任何具体百分比**
- Norg.ai 援引的 "Growth Marshal n=730 study" **在所有公开数据库（Google Scholar、PubMed、arXiv）中找不到任何痕迹** — 强烈暗示伪造或包装话术
- 真实的 67% 来源是 Indig 数据：**top 30 domains 占据 67% 的话题级引用**（域名集中度，跟 BLUF 无关）

**应使用的可信替代数据**：
1. **Aggarwal et al. (ACM SIGKDD 2024)**：GEO 优化 visibility 提升至多 **40%**（学界唯一可信数字）
2. **Kevin Indig 1.2M 研究**：**44.2% 引用来自前 30%**（这是真正的"BLUF 杠杆"实证）
3. **Indig 排名因子**：top-1 Google 页面被 ChatGPT 引用 **43.2%**，是 rank 20+ 页面的 **3.5x**

**产品启示**：用真实数据建立信任，**远离营销话术二次失真的"+67%"**。

---

## 六、Agentic Commerce Protocol（GEO 下半场最大变量）

### 6.1 OpenAI ACP（已 5 个版本迭代到稳定版）

- 2025-09-29 → 2025-12-12（fulfillment）→ 2026-01-16（capability negotiation）→ 2026-01-30（扩展）→ **2026-04-17 当前稳定版**
- **Apache 2.0 开源**，OpenAI + Stripe 维护
- 双 API：Checkout API + Delegate Payment API
- 支付 token 通过 agent 中介流动；商家不直接接触买家凭证

### 6.2 Google UCP

- **联合开发者**：Shopify、Etsy、Wayfair、Target、Walmart + 20+ 生态伙伴
- 接入面：Google AI Mode + Gemini
- 商家保留 Merchant of Record + 客户关系/数据/售后所有权
- 入口：Google Merchant Center 现有 shopping feeds

### 6.3 对内容创作者/SMB 的实际影响（重大）

1. **"流量" 概念被重定义**：不再是访问网站，而是 "agent 调取你的产品 feed 完成交易"
2. 传统 SEO/GEO ROI 模型部分失效
3. **Schema/Feed 投资优先级上升**：JSON-LD Product schema 成为 agent 可执行的购买数据源
4. **品牌站结构性放大效应**：UCP 把 AI 流量直接钩在 Merchant Center
5. **小博客/内容站的危机**：如果不接入 ACP/UCP feed，可能完全脱离交易闭环

### 6.4 SMB 实际行动建议

- 必须接入 Merchant Center / Stripe + ACP
- 内容站考虑 affiliate 升级到 ACP-aware product feed
- 监控自家品牌在 ChatGPT/Gemini 的 product carousel 出现频率（**新 KPI**）

---

## 七、对你产品定位的关键启示总结

### 7.1 直接可用的产品功能（来自创作者反复强调的市场缺口）

| 功能 | 出处 | 业界缺口验证 |
|------|------|-------------|
| **Passage-level embedding 工具** | Mike King 直接说"there is no SEO software" | iPullRank 自己开源了 Qforia 但功能简单 |
| **Brand mention vs Citation 区分追踪** | Indig "Ghost Citation Problem" | 多数工具只看 citation，不看 mention |
| **跨 LLM 行为差异追踪** | Indig 数据：Gemini 提及/ChatGPT 引用 | 用户视角追踪几乎空白 |
| **Topic centroid drift 检测** | Mike King 自己用 Python | 无现成工具 |
| **Pairwise LLM ranking 评估** | Mike King "head-to-head LLM evaluations" | 业界几乎没有 |
| **AI 引用源平台映射**（"为查询 X 推荐发布平台"） | 中文市场 navyum 案例（CSDN） | **中国独有杠杆**，西方工具无 |
| **Ghost Citation 报告** | Indig 61.7% 引用是 ghost | 提醒"被引用但没被提名"是新产品角度 |

### 7.2 直接可用的产品**叙事弹药**（用反共识打信任）

| 数据 | 用途 |
|------|------|
| **70% 站点 AI 流量 <2%**（Lily Ray 1316 人调研） | 反对"AI 流量爆发"营销话术 |
| **70.6% AI 流量被 GA4 错分为 Direct**（Wheelhouse） | 你产品的"暴露真相"叙事 |
| **YouTube mentions 0.737 > 任何其他因素**（Ahrefs 75K 品牌） | 反共识：YouTube 是 AI 引用最强信号 |
| **内容数量 0.194 ≈ 无关**（Ahrefs） | 反对"内容农场"营销 |
| **26% 品牌 AI Overview 零提及**（Ahrefs） | 提醒客户问题严重性 |
| **Ahrefs 自身 AI 流量转化 23x**（dogfooding） | 行业最高质量数据点 |
| **Listicle 量产惩罚 -49%**（Lily Ray 案例） | 警示客户什么不能做 |

### 7.3 三方共识核心战术清单（产品 MVP 必做）

1. **品牌信号建设** — branded mentions、branded anchor text、branded search volume（Ahrefs/Cyrus/Indig 三方共识第一）
2. **YouTube 内容布局** — Ahrefs 0.737 数据 + Aleyda/Lily 强调
3. **Front-load 答案** — Indig 44.2% 引用前 30%、Brian Dean BLUF
4. **可独立的 chunk 化写作** — 100-300 tokens（Toth）、500 tokens 上限（King）
5. **comparison/alternative 内容**（不是纯 informational） — Indig "Ghost Citation"洞察
6. **First-person + 22 personal pronouns** — Cyrus Zyppy 实证
7. **Schema markup**（FAQPage / BlogPosting / Organization） — 全员共识
8. **多平台分发**（Reddit / YouTube / Quora / GBP / 知乎 / CSDN / 抖音） — 全员强调
9. **保持新鲜度**（Perplexity +38% 引用率） — Aleyda/Indig
10. **避免黑帽**（listicle 量产、AI 内容农场、prompt injection） — Lily Ray 警示

### 7.4 三方分歧 → 产品定位选择

| 议题 | 派别 | 你应该选 |
|------|------|---------|
| 单独追踪 AI 必要吗 | Brian/Ahrefs：是 vs Cyrus：80% 不需要 | **混合**：默认 SEO 视角，付费版加 AI 追踪 |
| GEO 是否独立学科 | Mike King/Neil：是 vs Lily/Aleyda/Cyrus：不是 | **不是独立**——避免与 Google 官方对抗 |
| 内容数量是否重要 | Brian：高质量优先 vs Ahrefs 0.194：无关 | **质量+广度，不是数量** |

---

## 八、给你的最强 5 条具体建议

### 1. 把"Ghost Citation Problem"做成产品免费功能
Indig 的 454 prompt 实验发现 61.7% 引用是 ghost（链接存在但品牌名不出现）。你的产品可以提供"Ghost Citation 报告"——告诉用户"AI 引用了你 X 次，但只在 Y 次提到了你的品牌名"。这个洞察现有工具普遍缺失。

### 2. YouTube 引用追踪是真正的差异化
Ahrefs 数据：YouTube mentions 0.737 是绝对最强 AI 可见度信号——但**多数 GEO 工具忽略 YouTube**。如果你的产品集成 YouTube 视频引用追踪 + 转录优化建议，是**独家**功能。

### 3. 用 Lily Ray 的 listicle 惩罚案例做产品着陆页
**$80 亿品牌 -49%、SaaS -43%、-42%、-34%、-29%** 这套数据是市场上最强的"不要做 listicle 量产"警示——可作为你产品的"我们不做 spam"诚实定位锚点。

### 4. 中文市场的"平台溯源"功能要单独做
中国 GEO 与海外最大差异是**字节系闭环（豆包-CSDN-抖音-头条）**和百度系（文心-百家号）—— 你的产品要把"目标查询 → AI 引用源平台"映射可视化，告诉用户"豆包对'X 查询'当前引用了 CSDN 5 篇、知乎 3 篇，建议你在 CSDN 发布 Y 主题"。这是 AIDSO 没做出来的、西方工具完全没有的差异化。

### 5. 构建你自己的 "1.2M 响应"研究——用你的博客做 case study
Kevin Indig 用 1.2M ChatGPT 响应建立信任。你不需要这个量级，但可以**用你自己的博客在 Kimi/DeepSeek/豆包/ChatGPT 中的引用追踪**做月度连载——把 6-12 个月的真实数据曲线公开。这本身就是：
- 产品的最强 case study
- 反 GEO 灰产的最强声音
- 中文 GEO 实证研究的稀缺资产
- 个人品牌建设（Layer 2）

---

## 九、完整 Sources Index（80+ URL）

详见各 raw 档案：
- [raw/01-aleyda-lily-ray.md](./raw/01-aleyda-lily-ray.md)
- [raw/02-mike-king-kevin-indig.md](./raw/02-mike-king-kevin-indig.md)
- [raw/03-brian-dean-cyrus-ahrefs.md](./raw/03-brian-dean-cyrus-ahrefs.md)
- [raw/04-neil-patel-roundtable-sel.md](./raw/04-neil-patel-roundtable-sel.md)

每个 raw 档案包含 15-30 个原始 URL + 原句引用 + 实测数据点。

---

*附录撰写于 2026-04-26 | 基于 4 并行 agents × 800K+ tokens 的深度调研*
