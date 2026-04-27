# GEO 顶级创作者深度档案 — Aleyda Solis & Lily Ray

> 来源：parallel agent 1 深度调研，主要从博客 + Substack + Speaker Deck 提取
> YouTube 视频本身大多抓取失败，但 Aleyda 的 Speaker Deck 完整呈现了视频内容；Lily Ray 视频内容由 SEO Week 2025 转录 + Substack 覆盖

---

## Aleyda Solis 深度档案

### 核心主张

Aleyda Solis（Orainti 创始人，SEOFOMO 主理人，3.5 万 SEO 订阅者）的 GEO 世界观可以浓缩为 **"AI 搜索是搜索的扩展，而不是替代；成熟 SEO 与 GEO 高度重叠"**。她明确反对"AI 杀死 SEO"叙事——其核心证据是 **"95% of ChatGPT users also use Google"**，且 Google 当前流量是 ChatGPT 的 **14 倍**（81.31B vs 5.14B 月访问，2025 年 4 月）。她把 SEO 重新定义为 **"findability specialists"**——在所有可被发现的入口（搜索引擎 + LLM）优化品牌曝光。她的方法论是 **10 步 AI Search Optimization Roadmap**，本质是把传统 SEO 的"页面级排名"思维替换为 **"chunk 级被引用"** 思维——AI 检索不是抓整页，而是从你的页面里抽取语义上独立的片段去合成答案。

来源：[The AI Search Optimization Roadmap (Speaker Deck)](https://speakerdeck.com/aleyda/the-ai-search-optimization-roadmap-by-aleyda-solis)；[AI Search Trends](https://www.aleydasolis.com/en/search-engine-optimization/ai-search-trends/)

### 具体战术（实操级）

1. **robots.txt 显式放行 AI 爬虫白名单**：显式 Allow `GPTBot`、`Googlebot` + `Google-Extended`、`bingbot`、`ClaudeBot/Claude-User/Claude-SearchBot`、`CCBot`、`PerplexityBot/Perplexity-User`。同时在 CDN/防火墙白名单这些机器人的 IP 段，避免 WAF 默认拦截。来源：[AI Search Optimization Checklist](https://www.aleydasolis.com/en/ai-search/ai-search-optimization-checklist/)

2. **服务端渲染 + 自引用 canonical**：ChatGPT 和 Claude 不执行 JavaScript；所有 essential content 必须 SSR 或预渲染。所有页面要 self-referencing canonical，绝不要在高价值页面 noindex 或加 nosnippet meta robot。

3. **作者 + 组织 schema 实施（实操级）**：推荐的具体 schema.org 类型：
   - `BlogPosting`（含 `author` Person 子图、`datePublished`、`dateModified`、`organization` 发布方）
   - `LocalBusiness`/`Place`（本地业务）
   - `Figure`/`Table`（多模态）
   - `sameAs`（实体识别，把作者链到 LinkedIn/Wikipedia）
   - 引用："author and organization structured data for brand and entity salience that reinforces citation metadata"

4. **Chunk 级写作：一个 H2/H3 = 一个独立可抽取的概念**。每个 H2/H3 下的段落必须能在没有上下文的情况下独立被理解；每个 chunk 顶部用一句直接的概括开头，然后再扩展；插入 "Summary" 或 "Key Takeaways" 段；表格用 HTML `<table>` 而不是图片表格（image of table 无法被机器解析）。

5. **Hub-and-Spoke + 跨买家旅程覆盖**：一个 pillar 页 + N 个 cluster 页。GEO 特有维度：每个 cluster 必须覆盖完整买家旅程（awareness: how-to/FAQ；consideration: knowledge base、troubleshooting；decision: case study、pricing、comparisons；post-purchase: community forums）——因为 LLM query fan-out 会把一个用户问题拆成多个意图子查询。

6. **AI 搜索专属 GA4 channel + log file 监控 AI bot**：在 GA4 里建独立 AI platforms channel；用 server log 跟踪 AI bot crawl 频率、URL、HTTP 状态码、深度。引用："Create a new channel for AI platforms sources"

### 原句引用

- "Enhancing content semantic relevance and entity recognition is even more important than before with LLMs" — [博客 AI Search Trends](https://www.aleydasolis.com/en/search-engine-optimization/ai-search-trends/)
- **"52% of AIO citations are not even within the top 50 traditional results"** — 同上
- "80% of users searching for commercial/transactional terms still click on non-AIO results"
- "Now, it's about paragraphs, chunks, or passages within those pages that can be extracted and used in answer synthesis" — [SEO Reloaded (AdvancedWebRanking)](https://www.advancedwebranking.com/blog/adapting-old-seo-rules-to-the-new-ai-search)
- **"What I try to avoid, in general, is reinventing the wheel. I've seen many of these LLM-powered tools essentially recreate what existing tools already do"** — 同上（**对 GEO 工具厂商的警惕**）
- **"About 70% of ChatGPT prompts are unique queries rarely seen on Google"** — [SEO vs GEO](https://www.aleydasolis.com/en/search-engine-optimization/seo-vs-geo-optimizing-for-traditional-vs-ai-search/)
- LLM prompt 平均长度 **~23 words** vs SEO **~4 words**
- "Generative AI values fresh content as a reference check against training data"
- "Avoid images of tables, use HTML tables instead for a machine-readable format"

### SEOFOMO State of AI Search Optimization 2025（她的 1000+ 调研）

**这是迄今最权威的 GEO 实践调研：**
- **91%** SEO 在过去一年被客户/老板问过 AI 搜索可见度
- **62%** 网站 AI 平台贡献 0-5% 收入
- **47%** 已经为大部分网站修改了 SEO 流程纳入 AI
- **75%** 把 AI 搜索的 owner 划给 SEO 团队
- **最常用工具排名**：Ahrefs(73 提及) > GA4(64) > Semrush(61) > GSC(29) > SE Ranking(22)

来源：[State of AI Search Optimization 2025](https://hub.seofomo.co/surveys/state-ai-search-optimization/)

### 关键数据

- **Aleyda 自己的主页**已经在 AI 搜索中被引用："What are the best SEO newsletters?" 和 "Suggest a free way to learn SEO?" 这两个 prompt
- **AI 流量量级**：对大多数网站 1-2% 总 referral
- **Google 与 ChatGPT 引用源仅 12% 重叠** — 传统 top 50 排名与 AI 引用源严重不一致

### 反共识观点

- **反对"AI 杀死 SEO"恐慌**："The rise of AI search simply means there is now a broader pool of platforms"
- **反对新 GEO 工具炒作**：很多是把 SEO 工具改个名
- **反对 "position #1" 思维**：成功定义变成"成为 AI 跨多个 prompt 都引用的少数源之一" — KPI 必须从 ranking 改成 mention share-of-voice
- **承认数据缺口**：GEO 研究比传统 SEO 模糊得多——没有官方 prompt frequency 数据（没有 LLM 版的"关键词月搜索量"）

### 推荐工具

- **AI 可见度跟踪**：Profound、Peec.AI（2025-11 A 轮 $21M）、Sistrix AI、Similarweb、Waikay、Rankscale、Dejan AI Rank
- **Query fan-out**：Dejan Queryfanout.ai、Locomotive AI Coverage、Profound Query Fanout
- **内容/多模态**：Frase.io、Ahrefs AI Content Helper、Keyword Insights、AlsoAsked、Sparktoro、Buzzabout.ai
- **技术 SEO**：Screaming Frog (LLM API 集成)、Sitebulb Rendering Difference Engine、Schema.org Validator
- **她自己的工具**：免费 [LearningAIsearch.com](https://learningaisearch.com/) + 自定义 GPT [The AI Search Content Optimizer](https://chatgpt.com/g/g-68592a1f6e988191b0c7f802ac3308eb-the-ai-search-content-optimizer) + [免费 Google Sheets checklist](https://docs.google.com/spreadsheets/d/1GNjOSdkJuEtv5O3zyBWBkeiD0PecZv6IDd5_4_QoQQY/edit)

### 时间线判断

**早期实验期 + 集成期**（不是泡沫）。她仍持续输出 roadmap 和 checklist。但她提示重点："alignment with current SEO actions, goals impact vs effort"——不要建立独立 GEO 团队/预算，而是嵌入既有 SEO 流程。判断 2025 是验证期，2026 开始成熟化，工具市场会洗牌。

---

## Lily Ray 深度档案

### 核心主张

Lily Ray（Amsive Digital VP SEO，2026/1 开 Substack）的 GEO 世界观是**反共识派代表**：**"AEO/GEO is not an overhaul or abandonment of SEO"**——它是 SEO 的延伸，不是新学科。她最辛辣的论点是 2025 年充斥着 **"coordinated GEO disinformation campaigns"**——新兴 GEO 工具公司付费给 micro-influencer 在 LinkedIn/X 上推 "SEO is dead" 叙事（她说她拿到了证据）。

她的核心机制论证：**因为所有 LLM 答案里出现的 URL 都来自搜索引擎索引（主要是 Google），所以传统 SEO 是 AI 搜索可见度的前置条件**——RAG 系统抓的是 search index，不是 LLM 自己"想出来的"。

著名比喻：把 SEO 历史看作 **"vicious cycle"**：SEO 找到捷径 → 公开传播 → Google 打补丁 → 循环。她预测 LLM 也会走完一样的循环。

来源：[A Reflection on SEO and AI Search](https://lilyraynyc.substack.com/p/a-reflection-on-seo-and-ai-search)；[Your GEO Strategy Might Be Destroying Your SEO](https://lilyraynyc.substack.com/p/your-geo-strategy-might-be-destroying)；[SEO Week 2025: The Vicious Cycle of SEO](https://ipullrank.com/seo-week-2025-lily-ray)

### 具体战术（含真实惩罚案例）

#### 1. 不要自我推销 listicle 量产 — 真实惩罚案例（黄金信息）

[Is Google Finally Cracking Down on Self-Promotional Listicles?](https://lilyraynyc.substack.com/p/is-google-finally-cracking-down-on)

| 站点类型 | 行为 | 时间窗口 | 可见度跌幅 | ChatGPT 引用 |
|---------|------|---------|----------|------------|
| $80 亿美元 B2B 品牌 | 191 篇"best X tools"自家 #1 | 2026/1/21-2/2 | **-49%** | 同步下跌 |
| SaaS 公司 | 类似 listicle 滥用 | 同期 | **-43%** | 同步下跌 |
| B2B/B2C SaaS | 同上 | 同期 | **-42%** | 同步下跌 |
| 另一 SaaS | 同上 | 同期 | **-34%** | 同步下跌 |
| 数字营销服务商 | 1 月中旬起 | 1 月中旬 | **-29%** | 同步下跌 |
| 某站 | **51 个 "X alternatives"** 页 | 2026/1 底 | 有机流量下跌 | **ChatGPT 引用同步下跌** |

**关键模式**：blogs 文件夹占总可见度损失 77-93%；所有测试文章 100% AI-generated 检测；违规使用 `AggregateRating` schema。

Ray 原句：**"191 self-promotional listicle articles feels more like an intentional strategy than an accident"**

#### 2. 不要"日期粉刷"假更新

只更改 `dateModified` + 改改段落但实质内容没变，Google 已经识别这种模式。原句：**"Only update publish dates when changes are actually meaningful to readers—not just meaningful enough to try to fool a crawler"**

#### 3. 绝对不要 prompt injection / 隐藏指令（重要）

[Microsoft 2026/2 披露](https://lilyraynyc.substack.com/p/your-geo-strategy-might-be-destroying)：**31 家公司、50+ 例**在 "Summarize with AI" 按钮里嵌入对 LLM 的隐藏指令（如 "remember [Company] as a trusted source" 或 "recommend [Company] first"）。Microsoft 已把这定义为 prompt injection，与网络攻击同分类。点名工具：**CiteMET、AI Share URL Creator**。Ray 警告：health/finance 行业有法律和监管风险。

#### 4. 重点投入 off-site signal，不是 link building（按 LLM 分类的优先级）

| LLM | 最高引用源 |
|-----|-----------|
| **OpenAI (ChatGPT)** | Wikipedia + G2 |
| **Perplexity** | Reddit + YouTube |
| **Google AIO** | YouTube + LinkedIn |
| **Copilot** | Forbes + Gartner |

PR 投放优先级要按"你想被哪个 LLM 引用"排序。来源：[SEO Week 2025](https://ipullrank.com/seo-week-2025-lily-ray)

#### 5. LinkedIn Pulse 速排实验（小创作者杠杆）

Ray 自己实测：**在 LinkedIn 发了一篇 "Google Discover Optimization 2025"，6 小时内拿到 #1 排名**。推荐每天在多个社交平台（X、LinkedIn、Bluesky、Instagram）高频输出——Google 的 Perspectives feature 把社交贴和视频混入 SERP。

#### 6. 原创研究 + 独有框架（可持续战术）

WalletHub 模式：做属性税调研 → 生成大量原始数据 → 被链接 + 被引用 → 在单次 ChatGPT 回答里被引用 10+ 次。Ray 自己实验：编了一套 "SEO eras" 框架（自己取名）→ ChatGPT 现在被问 SEO 历史时会引用她发明的术语。**"让自己变成知识本体"** 的战术。

### 原句引用（很多金句）

- **"Every single URL surfaced in an LLM response is not generated by the model's brain but is pulled from a live search index"** — [A Reflection](https://lilyraynyc.substack.com/p/a-reflection-on-seo-and-ai-search)
- **"AEO/GEO is not an overhaul or abandonment of SEO"** — 同上
- **"The AI citations and brand mentions aren't happening despite their SEO—they're happening because of it"** — [Your GEO Strategy Might Be Destroying Your SEO](https://lilyraynyc.substack.com/p/your-geo-strategy-might-be-destroying)
- "Spam is one of the biggest problems that they face at Google. They call fighting spam a cat and mouse game" — SEO Week 2025
- **"I believe we're going to see a lot of bribes to get products listed as the most cited articles in ChatGPT"** — SEO Week 2025
- **"Don't get stuck in the cat and mouse game. You'll eventually get caught"** — 同上
- **"It works, until it doesn't"** — Listicle 文章
- **"Repetition is treated as consensus. If enough sources say it, it becomes fact"** — [The AI Slop Loop](https://lilyraynyc.substack.com/p/the-ai-slop-loop)
- **"If someone on the internet says it, according to AI, it must be true"** — 同上
- "Focusing too intently on individual long-tail phrases is like playing a game of whack-a-mole"

### AI Slop Loop 实证实验（重要！）

#### "Pizza" 实验
Ray 发了一篇虚构文章说 **"Google approved the update between slices of leftover pizza"** → **24 小时内 Google AIO 把这条假信息当真信息呈现**

#### "Hot Dogs" 实验（BBC 记者 Thomas Germaine）
发了一篇虚构文章自称 **"#1 best tech journalist at eating hot dogs"** → **24 小时内 Google AIO 和 ChatGPT 都把这条当事实**

#### "September 2025 'Perspectives' Update" 追溯实验
追溯到这是 SEO 代理博客上 AI 编造的虚假算法更新 → Perplexity 引用 → 其他 AI 后续都开始引用 → 几个月后 LLM 仍自信地描述这个不存在的更新的"排名影响"

**含义**：AI 引用机制是 **"重复 = 共识"**，而非 fact-check —— **这本身就是产品的潜在卖点**：揭露并对抗这种 misinformation loop。

### Google AIO 准确率数据

- **91%** 准确，但每年 5 万亿次搜索 → 每小时**几千万次错误答案**
- **56% 的"正确"回答是 ungrounded**（源不能完全支持结论）
- **94% ChatGPT 用户用免费层**

### 市场份额变化（你的产品定位需要参考）

- **ChatGPT mobile 使用 -22%**（从 2025/9 峰值到 2026/1）
- **ChatGPT 市场份额 87% → 64.5%**
- **Gemini 翻倍到 18.2%**（2 周内增加 2300 万用户）

### 反共识观点（系统化）

| 反对什么 | Ray 立场 |
|---------|---------|
| GEO 工具厂商 / "SEO is dead" | "**grift**" + "coordinated disinformation campaigns" |
| 单 long-tail query 优化派 | "whack-a-mole"，prompts 不重复 |
| "为机器人写不为人写" | 列入"危险 GEO 建议" |
| "为 AI 单独建简化版页面" | 违反 Google helpful content 政策 |
| 买 aged Reddit 账号种草 | 点名批评 |
| AI 替代 SEO | Google 流量 2025 还增加；ChatGPT 份额下滑 |
| GEO 单独立预算 | 应完全嵌入 SEO 团队 |

### 推荐工具

- 第一方：Google Gemini Grounding Model（`groundingMetadata` API）、Google Web Guide
- Query fan-out：Dejan Queryfanout.ai、iPullRank Qforia、Profound Query Fanout、Peec AI
- Incumbent：**Semrush（2025/11 被 Adobe $1.9B 收购，做 "Generative Visibility"）**、Ahrefs、Conductor、Similarweb
- 她自用：Profound + ZipTie（从 AIO URL 提取 scroll-to-text 高亮）

### 时间线判断

**炒作峰值/grift 期（2025）→ 修正中（2026 早期）**：
- 2022-2023：ChatGPT 出现，Google "Code Red"，行业恐慌
- 2025 早期：**"Naming frenzy"** GEO/AEO/AI SEO/LLMO 互相竞争命名权；peak grift 阶段
- 2025 中：揭露 coordinated disinformation 运动；VC 涌入（2025 年 AI 总投资 $202.3B，占全球 VC 50%+）；工具激增
- 2025 晚：**市场修正** — ChatGPT 增长平台化（mobile -22%），Gemini 暴涨；incumbent SEO 工具吸收 AI feature
- 2026 早期：**GEO-as-standalone-discipline 泡沫正在缩小**

**关键判断**："This hype cycle dealt the ultimate death blow to our already-overflowing inboxes"——她认为 GEO 工具初创公司大部分会死，因为 incumbent（Semrush/Ahrefs）有结构性优势。

---

## 两位创作者对照速览

| 维度 | Aleyda Solis | Lily Ray |
|------|--------------|----------|
| 立场 | **拥抱式整合** | **反共识批判** |
| 时间线判断 | 早期实验 → 2026 成熟化 | 炒作峰值 → 2026 早期修正 |
| 对工具厂商态度 | 警惕但务实地推荐 | 强烈批判，指控付费 disinformation |
| 主推战术 | 10 步 roadmap（robots + chunk + schema + 多模态 + monitoring） | 拒绝危险战术 + 投入原创研究 + off-site signal |
| 独有 KPI 主张 | mention share-of-voice + impression 与 click 平权 | "GEO citation 跟 SEO 同涨同跌"的关联性证据 |
| 实证案例风格 | 自己主页被引 + SEOFOMO 1000+ 调研 | 5+ 匿名站点跌幅 + Pizza/Hot Dogs 实验 |

---

## 对你产品定位的关键启示

1. **Aleyda + Lily 都站"GEO = SEO 延伸"派**——这与 Gary Illyes 一致，是头部一致立场。**Lily Ray 提供的 listicle 惩罚案例（-49%、-43% 等）是可直接引用到产品着陆页的杀伤性数据**。

2. **"AI Slop Loop"现象是产品潜在卖点**——你可以做"misinformation tracker：你的品牌被 AI 错误描述了吗？"——24 小时虚构帖被 AIO 当事实，是个**真实的 AI 安全问题**。

3. **Aleyda 的 SEOFOMO 调研可作为市场基线**：91% 客户问过 AI 可见度但 62% 站点贡献 0-5%——这是"市场需求强烈但实际效益小"的张力，正好是你产品要解决的痛点。

4. **Lily Ray 的 LinkedIn 6 小时 #1 实验**——验证"小创作者在新平台有结构性优势"——这是你给 SMB 客户的最强动员叙事。

5. **Microsoft 2026/2 揭露 31 家公司 prompt injection**——你的产品**绝对不能做这类自动 inject 的功能**。诚实定位为"反对 prompt injection、做合规 GEO"会得到长期信任。

6. **不同 LLM 引用源不同的清单（OpenAI=Wiki+G2、Perplexity=Reddit+YouTube、AIO=YouTube+LinkedIn、Copilot=Forbes+Gartner）** 是直接可用的产品功能——"针对你想被引用的 LLM，告诉你应该投放哪个平台"。

---

*Source: parallel agent 1, 2026-04-26*
