# Mike King (iPullRank) + Kevin Indig (Growth Memo) 深度档案

> Agent 2 输出，2026-04-26

---

## Mike King / iPullRank 深度档案

### 身份 & 背景
- iPullRank CEO，自封 "Chief Relevance Engineer"
- 连续两年 Search Engine Land "Search Marketer of the Year / AI Search Marketer of the Year"
- 2025/4 首次举办 SEO Week 大会（NYC）
- 客户：Target、Adidas、CoinDesk、MLB、Wall Street Journal、American Express
- iPullRank 主页声称 **"$4B+ in organic search results for our clients"**

### 1. Relevance Engineering——标志性概念（完整定义）

> "Relevance engineering is the confluence of artificial intelligence, information retrieval, content strategy, ux, and digital pr." — [BuzzStream Podcast](https://www.buzzstream.com/blog/relevance-engineering-podcast/)

**关键**："**notice I didn't say SEO as one of those things**" — 他刻意把 SEO 替换为 Information Retrieval。这是语义站位选择。

iPullRank 主页口号：**"We Don't Offer SEO. We offer Relevance Engineering."**

**5 学科融合**（来源 [Relevance Engineering Introduction](https://ipullrank.com/relevance-engineering-introduction)）：
1. Information Retrieval（信息检索）
2. User Experience（用户体验）
3. Artificial Intelligence
4. Content Strategy
5. Digital PR——"focusing on **getting relevant placements rather than just random ones**"（基于语义相关性的链接建设）

**5 阶段流程**：Identify Relevant Audience → Configure Platforms → Create Relevant Experiences → Develop Co-Relevant Experiences → Measure Performance

### 2. Query Fan-Out——LLM 检索内部机制（黄金）

来源：[Tech SEO Connect 2025 演讲](https://speakerdeck.com/techseoconnect/michael-king-everything-you-mfs-should-know-about-query-fan-out)

**核心定义**：
> "QUERY/PROMPT IS A STARTING POINT IN AI SEARCH...the query you type is not the query the system uses to gather information."

**机制**：用户的一个 prompt 被 Google AI Mode 内部 Gemini 重写成 **8-28 个合成子查询**，并行检索、相关性排序、LLM 合成最终答案。

**关键数据**：
- Gemini 平均生成 **10.7 queries per prompt**（峰值 28）
- 子查询平均 **6.7 words**（峰值 13）
- **95% 的合成子查询零月度搜索量** — 传统 SEO 工具完全看不到
- iPullRank 内部测试：**single domain appearance** 引用率 9.7%，**7+ appearances** 引用率 **80%+**
- ChatGPT 引用中 **~62% 来自非 Google 源**
- **28.3% 的被引用页面没有自然排名**

**子查询 6 类**（源自 Google 专利 WO2024064249A1）：
1. Related Queries
2. Implicit Queries
3. Comparative/Recent Queries
4. Personalized Queries
5. Reformulation Queries
6. Entity-Expanded Queries

**"Raffle"（彩票）类比**（金句）：
> "AI search is like a raffle. We don't control the synthesis pipeline—all we control is the inputs. The more of these synthetic subqueries you rank for, the more raffle tickets you have."

**收益递减**（iPullRank 自家测试）：单查询 22.5% → 加第二查询 31.7%（+9.2pp）→ 加第三查询 38.7%（+7.0pp）—— 应该聚焦头部 fan-out 变体而不是穷举尾部。

### 3. AI Mode 5 阶段管线

来源：[How AI Mode Works](https://ipullrank.com/how-ai-mode-works)

1. **Expansion** — 查询分解、意图挖掘、向量空间投影
2. **Routing** — 子查询映射到对应内容形式（文本/结构化/视频/转录）
3. **Retrieval** — 稀疏/稠密/混合策略 + 预算控制
4. **Selection** — passage 抽取、相关性打分（**pairwise LLM ranking**）
5. **Synthesis** — LLM 推理生成最终响应

**Pairwise LLM Ranking**（关键概念）：
> "Dense retrieval surfaces a pool of candidate passages. Pairwise LLM prompting selects which passages are most valuable."

意思：系统不再给每段固定分数，而是问 LLM "Given this query, which of these two passages is better?" — **head-to-head 评估**。落地："**You must engineer passages that can outperform competing content head-to-head in LLM evaluations.**"

### 4. 4 支柱内容框架（实操级）

**(1) Fit the Reasoning Target** — answer-first 句式、比较显式化
> "The Tesla Model Y offers 330 miles of range, advanced driver assistance, and spacious interior. Compared to the Ford Mustang Mach-E, it provides more range but less trunk space."

**(2) Be Fan-Out Compatible** — 包含具体实体名 + 反映用户意图
> "The Hyundai Ioniq 5, classified as a compact crossover SUV, is built on Hyundai's E-GMP platform"

**(3) Be Citation-Worthy** — 量化数据 + 命名来源
> "The 2024 Ioniq 5 has an EPA-estimated range of 303 miles. Source: U.S. Department of Energy, March 2024."

**(4) Be Composition-Friendly** — 列表/bullet/heading + FAQ + TL;DR + 单 chunk **~500 tokens 上限**

**写作战术**：
- Semantic Triple Structure（主语-谓语-宾语）
- 精确语言："SEO increases organic traffic by 15% in 6 months" not "helps get traffic"
- 独家洞察："Our analysis of 1M queries shows..."
- Active voice
- Heading hierarchy（H1-H3 都进入 chunk 评估）

### 5. iPullRank 客户案例（量化）

来自主页 [iPullRank](https://ipullrank.com/)：
- **$2.4 Billion** 增量营收（一家大型银行因 content engineering 暂停付费广告）
- **$290 Million** 营收（全球 eCommerce，AI 驱动 category pages）
- **130% 流量恢复**（汽车出版商，5 年算法影响后恢复）

**内容修剪案例**（[Relevance Engineering at Scale](https://ipullrank.com/relevance-engineering-at-scale)）：
- 评估 1,000+ 篇博客文章
- **45% 内容被标记为修剪/合并候选**（500+ 文章）
- 修剪后**站点级语义相关性提升 2-3%**（mega embedding 前后对比）

### 6. 反共识观点

1. **传统 SEO 工具完全过时**："95% of SEO tools operate on lexical (keyword-counting) models, not semantic understanding"——业界落后 Google 至少 10 年
2. **EAT ≠ author bios** — 主流误读
3. **应该删除分散主题的内容**（contrarian to "more content is better"）
4. **品牌 vs 流量是二选一**
5. **零点击是机会，不是危机**
6. > "Do you all really want to stay the janitors of the web?"

### 7. iPullRank 开源工具（产品空白指引！）

- **Qforia** ([link](https://ipullrank.com/tools/qforia))——Gemini 驱动 query fan-out 模拟器，生成 20-50 子查询
- **Orbitwise** ([link](https://ipullrank.com/tools/orbitwise/))——查询/文档转 512 维 embedding，cosine similarity 2D 可视化
- **Chunk Daily**——chunk 级表现分析器
- **Relevance Doctor**——passage-level 相关性打分
- **Gemini Grounding Detector**
- **AI Overview Simulator** — LlamaIndex + Gemini 2.5 + Vertex embeddings

**他推荐的实现 stack**：
- Screaming Frog + Ollama（本地生成 embeddings）
- Google Text Embeddings API
- LlamaIndex（RAG pipeline 模拟）
- Python (Pandas, NumPy, Scikit-learn)
- Ollama (mxbai-embed-large) — 本地 embedding 模型
- Gephi — 链接图可视化

**relevanceengineering.org 4 个开源项目**（SEO Week 2025）：
1. Gateway Specification — SEO 工具数据可移植性标准
2. Distributed Vector Database — P2P web 向量化
3. Search Telemetry Project
4. Open Search Initiative

### 8. **市场缺口（你产品的最大暗号）**

> "There is no SEO software that will get you passage-level embeddings...you'd have to write your own code to do what I just walked you through." ([How AI Mode Works](https://ipullrank.com/how-ai-mode-works))

**明确点出的市场缺口**：
- ❌ **Passage-level embedding 工具** — 业界没有
- ❌ **Query fan-out 模拟器** — 只有 Qforia + 几家小厂（Profound、DemandSphere、PromptWatch、MarketBrew）
- ❌ **Pairwise LLM ranking 评估** — 几乎没有产品
- ❌ **Brand mention vs citation tracking 区分** — 大多数工具只看 ranking
- ❌ **Topic centroid drift 检测** — 自己写 Python，没有现成工具

> "There's no SEO tool out there that does that. All the existing tools are still focused on pages." (BuzzStream)

### 9. 关键金句（带 URL）

1. > "We Don't Offer SEO. We offer Relevance Engineering." — [iPullRank](https://ipullrank.com/)
2. > "You don't want to beat the algorithm—you want to crush the competition." — [AI Search Manual](https://ipullrank.com/ai-search-manual)
3. > "It's such a disconnect between what Google does and what SEO software does. At the very least, we're 10 years behind." — [SMX Advanced 2025](https://searchengineland.com/mike-king-smx-advanced-2025-interview-456186)
4. > "Most of our industry does not know what it's doing right now."
5. > "Our own community has continued to say that page titles should only be 70 characters. That's not true. It's 100% not true."
6. > "It's quite shocking that our SEO tools have still been just counting words all this time when such a leap forward [Word2Vec] has been available open source for 10 years."
7. > "We are no longer aligned with what Google is trying to accomplish. We want visibility and traffic. Google wants to help people meet their information needs and they look at traffic as a 'necessary evil.'"
8. > "SEO irrevocably changed. We can keep calling it SEO and make less money, or call it something else and make a lot more."

---

## Kevin Indig / Growth Memo 深度档案

### 身份
- Growth Memo 创始人（订阅者 23,358，2026-01-05）
- 前 Shopify Director of SEO、G2 VP of SEO、Atlassian SEO 顾问
- 自称 "Organic Growth Advisor"
- **实证主义风格** — 大量基于数据集的实验，文章带置信区间和 p 值

### 1. **1.2M ChatGPT 响应分析（黄金研究）**

**两篇核心文章**：
- [The Science of How AI Pays Attention](https://www.growth-memo.com/p/the-science-of-how-ai-pays-attention) — 位置/语言学
- [The Science of How AI Picks Its Sources](https://www.growth-memo.com/p/the-science-of-how-ai-picks-its-sources) — 域名集中度/内容长度

**完整方法论**：
- 数据源：**Gauge 平台**提供 ~3M ChatGPT answers + 30M citations
- Citation matching：**all-MiniLM-L6-v2 sentence-transformer** 把回答和源文本句句转成 384-维向量
- 相似度阈值：**cosine similarity ≥ 0.55**
- 验证：四个随机批次重复
- 最终样本：**~98,000 citation rows**，**18,012 verified citations**
- 7 个垂直：B2B SaaS / Finance / Healthcare / Education / Crypto / HR Tech / Product Analytics
- 统计显著性：**P-Value: 0.0**（p < 0.0001）

**核心发现**：

#### (1) 位置发现（"Ski Ramp" Pattern）
- **44.2% 引用来自页面前 30%**（intro）
- 31.1% 来自中段（30-70%）
- 24.7% 来自最后 1/3
- 段落内：**53% 引用在段落中部**，24.5% 在首句，22.5% 在末句

#### (2) 域名集中度（极重要）
- **~30 domains own 67% of citations per topic**
- Top 10 域名：46% 引用份额
- ChatGPT **检索的页面数 ~6x 实际引用的页面数** — **85% 的检索页面从未被引用**
- **67% 被引用 URL 只在一个 prompt 中出现一次**（"one-hit"）
- 顶部 4.8% URL 被引用 10+ 次的，**全部是 category-level comparisons or guides**
- CRM/SaaS one-hit 率最高（84.7%）

#### (3) 内容长度（垂直依赖）
- 5K-10K 词 → "近 2x 引用率提升"
- **20K+ 字符页面：平均 10.18 citations vs. 500 字以下的 2.39**
- **Finance 反转** — 高引用 1,783 词 vs. 低引用 2,084 词（短反而强）
- B2B SaaS：长内容 1.59x 优势
- Crypto：10K-20K 词最优
- Healthcare：结构 > 字数，0-5 个 heading 最佳
- **"3-4 heading dead zone"** — 所有垂直都表现差

#### (4) Google 排名 → ChatGPT 引用
- 排名 #1 页面：**43.2% 引用率**（是排名 20 之外页面的 **3.5x**）

#### (5) 语言学特征（黄金细节）
- **Definitive language**: 36.2% 引用胜方 vs. 20.2% 落败方（**"X is Y" 句式提升 14% 引用率**）
- **问号在 H2 中**: 出现频率高 2x（18% vs 8.9%）
- **Question 引用：78.4% 来自 headings**
- **Entity density**: 引用文本 **20.6% 命名实体** vs. 标准英文 5-8%（**~2.5x 富集**）
- **Subjectivity score**: 0.47（事实+分析平衡）
- **Flesch-Kincaid grade level**: **16（college level）vs. 落败方 19.1**（避免 PhD-level 复杂度）
- **Big brand penalty**: 大品牌 0.81x 引用率（**负向信号**！）
- **High-cited pages**: 平均 2.1 named entities vs. 低引用 1.75

### 2. **Ghost Citation Problem**（454 prompt 实验）

来源：[The Ghost Citation Problem](https://www.growth-memo.com/p/the-ghost-citation-problem)

**方法论**：
- 454 prompt + domain 组合，跨 4 个 AI 引擎（ChatGPT / AIO / Gemini / AI Mode）
- 数据集：3,981 domains × 115 prompts × 14 countries × Semrush AI Toolkit
- **22%（100 案例）中 LLMs 在"是否提及品牌名"上产生分歧**

**核心发现**：
- 74.9% 域名被引用，但只有 38.3% 被提及
- **61.7% 的引用是"ghost citation"**（链接存在但品牌名不出现）
- 只有 13.2% 同时获得引用 + 提及

**LLM 行为差异**（极重要）：
- **Gemini**: 83.7% 提及率 / 21.4% 引用率（**爱提名字，不爱给链接**）
- **ChatGPT**: 87.0% 引用率 / 20.7% 提及率（**爱给链接，不爱提名字**）
- Google AI Overviews：中间地带
- Google AI Mode：比 ChatGPT 多 17% 提及

**地域差异**：
- 印度、瑞典：50% 提及率
- 意大利、巴西、荷兰：18-22% 提及率，82-94% 引用率

**关键洞察**：
> "Consumer brands with strong public identity get mentioned in the output at near 100%. The AI doesn't feel the need to cite."

> "Comparative content gets brands named. Informational content feeds the machine anonymously."

实操含义：**目标是品牌提及（不只流量），内容策略要偏向 evaluation/comparison/recommendation，不是纯 informational**。

### 3. E-GEO 实验（"How Much Can We Influence AI Responses"）

来源：[link](https://www.growth-memo.com/p/how-much-can-we-influence-ai-responses)

引用 Bagga et al. **E-GEO testbed**（GPT-4o + 7,000 Reddit queries × 50,000 Amazon listings）：
- 重写描述获得 **~90% win rate** vs. baseline
- 跨品类迁移：home goods 训练 → electronics 88% 胜率，clothing 87%
- 通用胜出策略："**Longer descriptions with a highly persuasive tone and fluff**" — 单纯让产品听起来更厉害（不加新事实）就有效
- Aggarwal et al. 2023：**factual density boosted visibility by ~40%**
- Kumar et al.: vendor 可"insert an optimized sequence of tokens"显著提升 LLM Visibility

**Indig 警告**：LLM 可见性具有 "**extreme fragility** vulnerable to manipulation"——预测会出现"**endless arms race with 'optimizers'**"，最终 LLM 厂商出 Panda/Penguin 类反作弊。

### 4. 最大预测因子

> "**The biggest predictor of AI Chatbot visibility? Brand popularity.**" — [LinkedIn 2025/3](https://www.linkedin.com/posts/kevinindig_the-biggest-predictor-or-ai-chatbot-visibility-activity-7306408942442598402-WOrp)

**最强预测器组合**：brand search volume + Google ranking position + topic coverage breadth

排名 #1 vs 排名 #20 之外引用率差距 **3.5x（43.2% vs ~12%）**

### 5. 反共识观点 / 对 GEO 工具厂商的批评

1. **"Best answer for a single keyword" 已死**：
   > "If you think writing the 'best answer' for a single keyword will get you cited by ChatGPT, the data says otherwise. After analyzing 1.2 million ChatGPT responses, the reality is much more consolidated."

2. **"Ultimate guide" 风格反而扣分** — 传统"故事化"输给"briefing-style / bottom-line-up-front"

3. **关键词中心思维过时**：
   > "We need to shut this off, right? We need to evolve."

4. **CTR 已死，需要新指标**：
   > "When are we going to adopt something like agentic completion rate as a metric?"
   > "It's changing from a click game to an influence game."

5. **2024 是流量峰值年** — Clearscope 圆桌明确说

6. **隐含批评 GEO 工具厂商** — 真正预测因子是 brand volume + Google rank + content breadth，没有捷径

### 6. AI 时代 SEO 三层框架

来源：[Beyond Old SEO Models](https://www.advancedwebranking.com/blog/beyond-old-seo-models-ai-search)

1. **Topic & Entity Focus**（不是关键词）— prompts 比搜索查询长 5x
2. **From Clicks to Influence** — 用 "agentic completion rate" 替代 CTR
3. **Internal Context as Competitive Moat** — 把 Confluence、help docs、developer guides 喂给 LLM 建立权威（"context engineering"）

### 7. 关键金句（带 URL）

1. > "44.2% of all citations come from the first 30% of text (the intro)"
2. > "ChatGPT pays disproportionate attention to the top 30% of your content."
3. > "If you bury your key product features in paragraph 12...the AI is 2.5x less likely to cite it."
4. > "The AI reads like a journalist. It grabs the 'Who, What, Where' from the top."
5. > "Generic advice is risky and vague, but a specific entity is grounded and verifiable."
6. > "~30 domains own 67% of citations per topic"
7. > "The domains that own citation share didn't get there by writing better sentences."
8. > "**One well-structured comparison page can still outperform the entire domain portfolio of a well-known brand.**" — 给小创作者的最强信号
9. > "Brand search volume is the single biggest predictor of how often an AI mentions your brand in answers."
10. > "Comparative content gets brands named. Informational content feeds the machine anonymously."
11. > "It's changing from a click game to an influence game."

### 8. 对独立创作者的建议

1. **建 topical hubs，不是单页面**
2. **追求引用 reach，不是引用 count** — "Citation reach (the number of distinct prompts a domain answers) is a more useful strategic metric"
3. **小作者也能赢一类内容**：举例 "learn.g2.com: 65 unique prompts, 495 citations" 跑赢整个大品牌组合
4. **建立 brand search volume** — 最强预测因子
5. **不要刷 prompt 排名** — 单 prompt 数据噪音大，应追踪**主题群覆盖率**
6. **Self-attribution survey**：在 onboarding 加 "How did you hear about us?" — 传统 attribution 在 AI 时代失效

### 9. 具体写作建议（来自 1.2M 研究）

- **H2 用问题句式**："When did SEO start? SEO started in..."
- **Entity echoing**：在答案开头复述问题里的关键实体
- **20.6% entity density** 目标
- **Flesch-Kincaid 16** 目标
- **Subjectivity 0.47**（事实+分析平衡）
- **替换模糊短语**：Bad: "In this fast-paced world..." → Good: "Demo automation is the process of..."
- **命名实体替代品类词**：不说 "the leading CRM"，说 "Salesforce, HubSpot, and Pipedrive"

### 10. **B2B 必备页面类型**（Clearscope 2026 圆桌共识）

- ICP mapping pages（按行业、公司规模、角色）
- Comparison/alternative pages
- Use-case pages
- **Homepage 必须明确写**：ICP、primary category、use cases、地理范围、信任标志

---

## 两人对比与共同信号

| 维度 | Mike King | Kevin Indig |
|------|-----------|-------------|
| 风格 | 框架派 / 工程派 / 政治派 | 实证派 / 数据派 / 测量派 |
| 标志概念 | Relevance Engineering, Query Fan-Out | Ghost Citation, Citation Reach, Ski Ramp Pattern |
| 数据来源 | 客户案例 + 自家工具测试 | 第三方数据集（Gauge, Semrush）+ 学术论文 |
| 量化深度 | 框架优先，数据辅助 | 数据优先，p<0.0001 级别 |
| 工具贡献 | 大量开源（Qforia, Orbitwise, Chunk Daily） | 几乎无开源工具，主要是 Substack 内容 |
| 对工具厂商 | 批评但建工具填补 | 批评但不建工具 |

## **两人共同信号（独立工具构建者最该听）**

1. **Passage-level / chunk-level 测量是巨大空白**
2. **Brand mention vs. citation 区分是新指标层**
3. **跨 LLM 行为差异追踪**（Gemini 偏 mention vs ChatGPT 偏 citation）是新维度
4. **Google ranking 仍然是 AI 引用的最强可控预测因子**（不要丢传统 SEO 基础）
5. **Topic centroid drift / 内容主题相关性自动评估**是普遍痛点
6. **现有 SaaS 工具大多是 ChatGPT overlay，不是底层重设计**——市场缺真正基于 RAG pipeline mental model 的产品

---

*Source: parallel agent 2, 2026-04-26*
