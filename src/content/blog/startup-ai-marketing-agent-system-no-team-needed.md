---
title: "把市场部外包给 Agent：没有市场团队的技术型创业公司增长指南"
titleEn: "Outsource Your Marketing Dept to AI Agents: A Growth Guide for Technical Startups Without a Marketing Team"
description: "两个工程师，没有市场部，用五类 AI Agent（X回复、LinkedIn回复、博客评论、内容生成、意图信号监控）把流量翻倍、MRR 涨 30%。这是一篇市场营销专家视角 + 工程落地方案的实战研究文档，附开源工具地图和可直接复用的 Harness 架构。"
descriptionEn: "Two engineers, no marketing team, five classes of AI agents (X replies, LinkedIn replies, blog comments, content generation, intent-signal monitoring) — doubled traffic and grew MRR 30%. A practitioner-level research guide combining marketing-expert perspective with engineering implementation, including an open-source tool map and a reusable harness architecture."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["AI营销", "创业增长", "Marketing Agent", "LinkedIn自动化", "Twitter Agent", "内容生成", "意图信号", "开源工具", "Harness工程", "无市场团队"]
heroImage: "../../assets/images/startup-ai-marketing-agent-system-no-team-needed-banner.jpg"
---

> **背景**：本文源自一个真实案例——一个两人技术团队，没有任何市场预算，用 AI Agent 系统替代了传统市场部的工作，三个月内流量翻倍，MRR 增长 30%。  
> **读者**：技术型创业公司 founder、独立开发者、小团队工程师。  
> **定位**：既是营销策略分析，也是可落地的工程实现指南。

---

## 问题的本质

技术创业公司最常见的增长瓶颈不是产品，是曝光。

团队里有人能把 PostgreSQL 调优到极致，能写出优雅的分布式系统——但没有人每天发帖子、回评论、写 SEO 文章、追 LinkedIn 上的意向用户。这件事不是不重要，而是**时间不允许**。

市场部外包的传统方案是：雇内容运营、雇增长 Hacker、雇 KOL 做投放。但早期创业公司没钱，而且外部人很难真正理解产品。

AI Agent 提供了第三条路：**把市场工作的执行层交给 Agent，创始人只做策略层和审查层。**

---

## 核心架构原则

### 一个 Agent = 一个渠道 + 一个指标

这是整个系统最重要的设计决策。

**不要做**：一个"营销 Agent"做所有事情——发 X、回 LinkedIn、写博客、监控竞品。

**要做**：每个 Agent 负责一个渠道，跟踪一个指标。

```
X 回复 Agent       → 渠道: X/Twitter       → 指标: 回复带来的 profile visit
LinkedIn 回复 Agent → 渠道: LinkedIn       → 指标: 接受连接 + DM 打开率  
博客评论 Agent      → 渠道: 行业博客/论坛  → 指标: 导流点击
内容生成 Agent      → 渠道: 自有博客/LinkedIn文章 → 指标: 自然搜索流量
意图信号 Agent      → 渠道: LinkedIn Jobs → 指标: 高意向线索数
```

**为什么这样设计**：

- **可追踪**：单指标让你知道哪个 Agent 有效、哪个在浪费算力
- **可迭代**：调一个 Agent 的 prompt，不影响其他人
- **可维护**：每个 Agent 出问题，范围清晰

### Prompt 衰减是系统性风险

**每 30 天重写一次核心 prompt。**

这不是建议，是工程要求。

AI Agent 的回复风格会随时间被平台用户"识别出来"。LinkedIn 用户见过太多 "Great insights! I totally agree with your point about..." 开头的 AI 评论——这种回复现在直接被忽略。

每 30 天，花两小时重新审视：
1. 最近 100 条回复里，哪些得到了正向互动？
2. 哪些被忽略或被负向标记？
3. 当前语气/风格是否还符合平台主流？

把这个重写任务本身也做成一个 Agent：定期从互动数据里提炼有效模式，生成候选 prompt 变体，A/B 测试，胜者晋级。

---

## 五类 Agent 详细设计

### Agent 1：X（Twitter）回复 Agent

**目标**：在潜在用户的对话里出现，展示专业见解，引流到 profile。

**触发逻辑**：
```
搜索词 = 竞品名 OR 行业核心术语 OR "looking for [你解决的问题]"
每天运行 2 次（早 9 点 / 晚 6 点）
过滤条件：发帖者有 500+ 关注者，帖子 6 小时内
```

**Rate limit**：**≤ 50 条/天**。X 的隐性封号阈值在 100，但 50 是安全线。留出缓冲给手动操作。

**回复质量规则**：
- 回复长度 80-180 字符（太长=AI，太短=无价值）
- 第一句不能以"Great"/"Interesting"/"I agree"开头
- 至少包含一个具体事实或数字
- 最多每 10 条回复里有 1 条提到自家产品，其他都纯价值输出

**工程实现**：

```python
# 伪代码结构
class XReplyAgent:
    def run_cycle(self):
        tweets = self.search_relevant_tweets(
            queries=self.config.search_terms,
            min_followers=500,
            max_age_hours=6
        )
        for tweet in tweets[:self.daily_limit_remaining()]:
            if self.already_replied(tweet.id):
                continue
            if not self.passes_quality_filter(tweet):
                continue
            reply = self.generate_reply(tweet, self.prompt_template)
            self.post_reply(reply, tweet.id)
            self.log_action(tweet.id, reply)
            time.sleep(random.uniform(180, 420))  # 3-7 分钟间隔
```

**关键点**：随机间隔，不要固定节奏。固定每 5 分钟发一条是最快触发封号的行为。

---

### Agent 2：LinkedIn 回复 Agent

**目标**：在技术 founder、DevRel、工程 VP 的帖子下建立可见度，触发连接邀请。

**触发逻辑**：
```
目标人群 = 标题含 "Founder" OR "CTO" OR "VP Engineering" OR "Developer Relations"
帖子话题 = 你的产品解决的问题领域
每天 ≤ 30 条回复
```

**Rate limit**：**≤ 30 条/天**。LinkedIn 对第三方 API 的监控比 X 严格，而且封号处理更慢。宁可保守。

**回复策略**：

LinkedIn 回复和 X 不同——LinkedIn 上人们期待更长、更专业的回应。但不能是作文。

有效模式：
- **加数据**：帖子说"我们的转化率提升了"，你回复"我们做了类似实验，A/B 测试后发现 X 因素贡献了大部分提升，主要是因为Y"
- **提问题**：真实的问题。"你们在 [具体场景] 里是怎么处理的？我们遇到了 Z 挑战。"
- **分享对应案例**：不推销产品，分享自己遇到同类问题的解法

**不要做**：提到你的产品名。在 LinkedIn，这会直接被视为垃圾营销。

---

### Agent 3：博客评论 Agent

**目标**：在行业高流量博客 / 技术论坛留下有价值的评论，引导感兴趣的读者点击进来。

**目标平台**（根据你的行业调整）：
- Hacker News（寻找你行业相关的 Show HN / Ask HN 帖）
- Reddit（r/startups, r/SaaS, r/devops 等）
- 行业 newsletter 评论区
- Medium / Substack 技术文章

**评论质量门槛比 X/LinkedIn 更高**：这类平台的社区会主动标记"营销评论"，一旦被标就是负面曝光。

规则：
- 每条评论必须基于文章实际内容（Agent 需要先读全文，再回复）
- 禁止任何形式的产品 mention（纯价值输出）
- 字数 150-400（太短=水帖，太长=广告）
- 每个平台每天 ≤ 5 条

---

### Agent 4：内容生成 Agent

**目标**：把每天的信息输入（行业新闻、竞品动态、用户反馈）转化为可发布内容。

**内容流水线**：

```
每日输入 →
  ├── RSS feeds（竞品/行业媒体）
  ├── 用户支持 ticket（本周高频问题）
  └── 你自己的产品更新日志

内容生成 Agent →
  ├── 平日博客文章（技术深度，搜索友好）
  ├── LinkedIn 长文（2-3 次/周）
  └── X 线程（1 次/周，高价值主题）
```

**编辑原则**：Agent 生成草稿，人类 30 分钟审阅 + 微调，然后发布。不要让 Agent 完全自动发布——特别是早期，人的判断还是必要的把关层。

**搜索优化**：
- 每篇博文针对一个长尾关键词
- 结构化数据（FAQ schema）帮助在 AI 搜索（ChatGPT/Perplexity）里被引用
- 把已有博文的要点转化为 LinkedIn 帖子（内容复用，不是复制）

---

### Agent 5：意图信号监控 Agent

这是五类 Agent 里**ROI 最高**的一个，也是最容易被忽视的。

**核心洞察**：公司在 LinkedIn 上发布特定职位招聘，是一个强烈的意图信号——他们正在经历你解决的那个问题。

**示例**：
- 如果你卖 CI/CD 工具，公司发 "DevOps Engineer" 招聘 → 他们的部署流程可能有问题
- 如果你卖数据分析工具，公司发 "Data Analyst" + "Data Engineer" → 他们在搭数据基础设施
- 如果你卖客服 AI，公司发 "Customer Support Manager" → 他们的客服规模在增长

**实现方案**：

```python
# 意图信号 Agent
class IntentSignalAgent:
    def daily_scan(self):
        # 搜索 LinkedIn Jobs（通过官方 API 或授权第三方）
        jobs = self.search_linkedin_jobs(
            keywords=self.config.intent_keywords,
            company_size=["51-200", "201-500"],  # 目标客户规模
            posted_within_days=3
        )
        
        for job in jobs:
            company = job.company
            if self.already_in_crm(company):
                continue
            
            # 判断意图强度
            intent_score = self.score_intent(job, company)
            if intent_score > self.threshold:
                # 加入 outreach 队列
                self.queue_for_outreach(company, {
                    "signal": job.title,
                    "timing": "now",
                    "approach": self.draft_first_message(company, job)
                })
```

**Outreach 节奏**：发现意图信号 → 48 小时内联系创始人/VP → 不推销，分享相关内容 → 1 周后跟进。

**关键注意**：不要一次联系太多（每天 ≤ 10 家新公司），保持手工审阅，意图信号判断目前还需要人来确认质量。

---

## 开源工具地图

从 GitHub 搜到的可用工具和框架：

### 营销 Agent 框架

| 项目 | 描述 | 适用场景 |
|---|---|---|
| `cgallic/kai-cmo-harness` | Claude Code 的 AI CMO 框架：SEO、内容、邮件、广告、CRO、AEO/GEO 技能集合 | 全栈营销 Agent 起点 |
| `SaigonXIII/evc` | Claude Code 营销工作区：42 个命令、12 个 hooks、4 个行业模板 | 已有 Claude Code 工作流 |
| `unifapi-agent/agents` | 基于 MCP 的营销 Agent：SEO 审计、社交监听、竞品分析 | MCP 集成方案 |
| `Ahil-NS/marketing-agent-teams` | 多平台 Agent 团队：TikTok/Instagram/YouTube/Facebook/Reddit/X/Pinterest 自动化 | 多渠道铺量 |
| `nowork-studio/NotFair` | 目标驱动的 Loop 营销 Agent，24/7 运行 | 自动化循环执行 |

### 数据与分析连接

| 项目 | 描述 |
|---|---|
| `Dataslayer-AI/Marketing-skills` | 通过 Dataslayer MCP 连接 Google Ads、GA4、Search Console、Meta Ads、LinkedIn Ads 等 50+ 平台 |
| `Hk669/AI-Marketing-Agents` | 基于 GenAI 的多 Agent 个性化营销活动生成 |
| `telexintegrations/email-marketing-agent` | Telex 集成的邮件营销 Agent |

### 社区互动

| 项目 | 描述 |
|---|---|
| `lucaswalter/reddit-marketing-agent` | Reddit 营销 Agent（AI Automation Community 出品）|
| `edofransisco011/Smb-Marketing-Agent` | 小企业多 Agent 营销系统（Python + Streamlit）|

---

## 工程落地：Harness 设计

把上面的 5 个 Agent 接成一个系统，核心是**Harness**——控制每个 Agent 的执行循环、工具权限、速率控制和可观测性。

```
┌─────────────────────────────────────────────────────┐
│                  Marketing Harness                   │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Scheduler│  │Rate Limiter│ │ Prompt Registry  │  │
│  │ (cron)   │  │ per-agent │  │ (版本化 prompt)  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │              Agent 执行层                    │    │
│  │  X Agent │ LinkedIn │ 博客评论 │ 内容 │ 意图  │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Logger  │  │ CRM Sync │  │  Alert System    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 核心组件

**1. Scheduler（调度器）**

```yaml
# config.yaml
agents:
  x_reply:
    schedule: "0 9,18 * * 1-5"  # 工作日早9、晚6
    daily_limit: 50
    
  linkedin_reply:
    schedule: "0 10 * * 1-5"     # 工作日上午10点
    daily_limit: 30
    
  blog_comment:
    schedule: "0 14 * * 1-5"     # 工作日下午2点
    daily_limit: 15
    
  content_gen:
    schedule: "0 7 * * 1-5"      # 工作日早7点（给人工审阅留时间）
    
  intent_signal:
    schedule: "0 8 * * 1-5"      # 工作日早8点
    daily_limit: 10
```

**2. Rate Limiter**

```python
class PerAgentRateLimiter:
    def __init__(self, agent_id: str, daily_limit: int):
        self.agent_id = agent_id
        self.daily_limit = daily_limit
        self.db = SQLiteDB("~/.marketing-harness/limits.db")
    
    def check_and_consume(self) -> bool:
        today = date.today().isoformat()
        count = self.db.get_count(self.agent_id, today)
        if count >= self.daily_limit:
            return False
        self.db.increment(self.agent_id, today)
        return True
```

**3. Prompt Registry（版本化 Prompt 管理）**

```
~/.marketing-harness/prompts/
├── x_reply/
│   ├── v1_2026-05-15.md    ← 已归档
│   ├── v2_2026-06-20.md    ← 已归档  
│   └── v3_2026-07-22.md    ← current
├── linkedin_reply/
│   └── v1_2026-07-01.md    ← current
└── content_gen/
    └── v2_2026-07-10.md    ← current
```

每个 prompt 文件头部记录：版本号、生效日期、主要变更、上一版本的问题。30 天到期提醒基于文件创建时间自动触发。

**4. 可观测性**

最低可行的监控方案：

```python
# 每个 Agent 在 SQLite 里记录每条动作
class ActionLog:
    agent_id: str
    platform: str
    action_type: str   # "reply" | "comment" | "post" | "outreach"
    target_id: str     # tweet_id / post_id / company_id
    content_hash: str  # 防重复
    outcome: str       # "sent" | "rate_limited" | "filtered" | "error"
    timestamp: datetime
    engagement: dict   # 7天后回填：likes, replies, clicks
```

每周五运行一次 analytics Agent，从 log 里提取：
- 每类 Agent 的执行量 vs 限额使用率
- 回复的 7 日互动率（喜欢 / 回复 / profile visit）
- 哪条 prompt 版本表现最好

---

## 反模式：这些事情不要做

**1. 发现效果好就撤掉速率限制**

结果：平台封号，所有历史积累归零。速率限制是保险丝，不是性能瓶颈。

**2. 让 Agent 直接发布，不过审**

至少在前三个月保持人工审阅。Agent 会犯奇怪的错误——比如在竞品的 CEO 帖子下发一条"我们的产品比你们好多了"的回复。

**3. 用同一套 prompt 在所有平台**

X 的语气和 LinkedIn 完全不同。LinkedIn 上适合 professional 语气，X 上适合直接表达观点，Hacker News 上则必须技术扎实、不含糊。

**4. 忽略平台的服务条款更新**

LinkedIn 和 X 的自动化条款都在变。建议每季度检查一次 ToS，不要假设去年允许的今年还允许。

**5. 把意图信号 Agent 当成批量发垃圾邮件工具**

意图信号的价值在于精准，不在于量。每天联系 10 家真正符合画像的公司，远比批量 500 家强。

---

## 实战结果参考

基于上述架构，一个两人技术团队在三个月内的结果：

| 指标 | 初始 | 三个月后 |
|---|---|---|
| 网站自然流量 | 基准 | **2x** |
| 月度新增 MRR | 基准 | **+30%** |
| LinkedIn 连接接受率 | — | ~18% |
| X 回复互动率 | — | ~4.2% |
| 意图线索月度新增 | 0 | 约 40-60 家 |

**时间投入**：每天 30-45 分钟（主要是内容审阅 + 每周数据复盘），其余由 Agent 执行。

**成本**：LLM API 费用约 $30-50/月（Claude Sonnet 调用，每天几百次 API 调用），加上工具 license（如 LinkedIn 官方 API 或授权第三方），总成本远低于一个市场专员的月薪。

---

## 从零开始的行动清单

**第 1 周：先建 X 回复 Agent**

X 是最容易开始的平台（API 相对开放，社区容忍度高，反馈快）。目标是搞清楚你的核心搜索词，跑通第一个完整循环。

```bash
# 最小可行实现
gh repo clone cgallic/kai-cmo-harness
# 或者直接用 Claude Code + 简单 Python 脚本
```

**第 2 周：加 LinkedIn 回复 Agent**

在 X 建立节奏后，加 LinkedIn。注意语气调整。

**第 3 周：加内容生成 Agent**

博客产能是长期 SEO 的基础。这一步会在 3-6 个月后看到回报。

**第 4 周：加意图信号 Agent**

如果你做 B2B，这是最快看到直接销售线索的 Agent。

**持续：每 30 天 prompt 审查**

把这个放进日历。30 天到了，不管有没有明显衰退，都重写一遍核心 prompt。

---

## 核心判断

这套方案的本质是：**把人类市场工作中的"执行层"机械化，保留"策略层"和"审查层"给人**。

Agent 不能替你想清楚"我的目标客户是谁"、"我的差异化是什么"——这些是策略，必须是人来定。但一旦策略清楚了，Agent 可以每天不知疲倦地执行：找对话、参与对话、监控信号、生成内容。

技术型创业公司最大的比较优势，是能快速搭起这套系统——而不是最终用它来替代思考。

系统跑起来之后，你的工作从"执行营销"变成了"管理一个 Agent 团队"：看数据、迭代 prompt、调整策略，而不是每天亲自写帖子。这个角色转变，本身就是一种 leverage。

---

## 开源参考与扩展阅读

- **kai-cmo-harness**：cgallic/kai-cmo-harness — Claude Code AI CMO 技能集
- **evc**（marketing workspace）：SaigonXIII/evc — 42 命令营销工作区
- **unifapi-agent**：unifapi-agent/agents — MCP 营销 Agent（SEO/社交监听/竞品分析）
- **marketing-agent-teams**：Ahil-NS/marketing-agent-teams — 多平台 Agent 团队
- **AI-Marketing-Agents**：Hk669/AI-Marketing-Agents — GenAI 个性化营销活动
- **Dataslayer Marketing Skills**：Dataslayer-AI/Marketing-skills — 连接真实广告数据

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Background**: This article is based on a real case — a two-person technical team, with no marketing budget, used an AI Agent system to replace the work of a traditional marketing department, doubling traffic and growing MRR by 30% within three months.  
> **Audience**: Technical startup founders, indie developers, small-team engineers.  
> **Purpose**: Both a marketing strategy analysis and a practical engineering implementation guide.

---

## The Core Problem

The most common growth bottleneck for technical startups is not the product — it is visibility.

The team has people who can tune PostgreSQL to its limits and write elegant distributed systems — but no one is posting every day, replying to comments, writing SEO articles, or chasing intent-signaling users on LinkedIn. This is not unimportant — there is simply **no time for it**.

The traditional outsourcing answer is: hire a content manager, hire a growth hacker, hire KOLs for paid distribution. But early-stage startups lack the budget, and external hires rarely understand the product deeply enough.

AI Agents offer a third path: **hand the execution layer of marketing work to Agents, and keep the strategy layer and review layer for the founders.**

---

## Core Architectural Principles

### One Agent = One Channel + One Metric

This is the single most important design decision in the entire system.

**Don't do this**: one "marketing Agent" that does everything — posts on X, replies on LinkedIn, writes blog posts, monitors competitors.

**Do this**: each Agent owns one channel and tracks one metric.

```
X Reply Agent              → Channel: X/Twitter              → Metric: profile visits from replies
LinkedIn Reply Agent       → Channel: LinkedIn               → Metric: connection acceptance + DM open rate
Blog Comment Agent         → Channel: industry blogs/forums  → Metric: referral clicks
Content Generation Agent   → Channel: own blog/LinkedIn articles → Metric: organic search traffic
Intent Signal Agent        → Channel: LinkedIn Jobs          → Metric: high-intent lead count
```

**Why this design**:

- **Trackable**: a single metric tells you which Agent is working and which is wasting compute
- **Iterable**: tweak one Agent's prompt without affecting the others
- **Maintainable**: when an Agent breaks, the blast radius is clear

### Prompt Decay Is a Systemic Risk

**Rewrite core prompts every 30 days.**

This is not a recommendation — it is an engineering requirement.

AI Agent reply styles get "recognized" by platform users over time. LinkedIn users have seen too many AI comments that start with "Great insights! I totally agree with your point about..." — those replies are now ignored on sight.

Every 30 days, spend two hours reviewing:
1. Of the last 100 replies, which ones received positive engagement?
2. Which were ignored or negatively flagged?
3. Does the current tone/style still match the platform's mainstream?

Turn this rewrite task itself into an Agent: periodically distill effective patterns from engagement data, generate candidate prompt variants, A/B test them, and promote the winner.

---

## Five Agent Types — Detailed Design

### Agent 1: X (Twitter) Reply Agent

**Goal**: Show up in potential users' conversations, demonstrate expertise, and drive traffic to your profile.

**Trigger logic**:
```
Search terms = competitor name OR core industry term OR "looking for [the problem you solve]"
Run twice daily (9 AM / 6 PM)
Filter: poster has 500+ followers, post is within the last 6 hours
```

**Rate limit**: **≤ 50 replies/day**. X's informal ban threshold is around 100, but 50 is the safe line. Leave headroom for manual operations.

**Reply quality rules**:
- Reply length: 80–180 characters (too long = AI, too short = no value)
- First sentence must not start with "Great" / "Interesting" / "I agree"
- Must include at least one concrete fact or number
- No more than 1 out of every 10 replies may mention your product — all others are pure value output

**Engineering implementation**:

```python
# Pseudocode structure
class XReplyAgent:
    def run_cycle(self):
        tweets = self.search_relevant_tweets(
            queries=self.config.search_terms,
            min_followers=500,
            max_age_hours=6
        )
        for tweet in tweets[:self.daily_limit_remaining()]:
            if self.already_replied(tweet.id):
                continue
            if not self.passes_quality_filter(tweet):
                continue
            reply = self.generate_reply(tweet, self.prompt_template)
            self.post_reply(reply, tweet.id)
            self.log_action(tweet.id, reply)
            time.sleep(random.uniform(180, 420))  # 3-7 minute interval
```

**Key point**: use random intervals — do not use a fixed cadence. Posting one reply every fixed 5 minutes is the fastest way to trigger a ban.

---

### Agent 2: LinkedIn Reply Agent

**Goal**: Build visibility under posts by technical founders, DevRel leads, and engineering VPs, and trigger connection invitations.

**Trigger logic**:
```
Target audience = title contains "Founder" OR "CTO" OR "VP Engineering" OR "Developer Relations"
Post topic = the problem domain your product solves
≤ 30 replies per day
```

**Rate limit**: **≤ 30 replies/day**. LinkedIn monitors third-party API usage more strictly than X, and account bans take longer to resolve. Err on the side of caution.

**Reply strategy**:

LinkedIn replies differ from X — on LinkedIn, people expect longer and more professional responses. But they should not read like essays.

Effective patterns:
- **Add data**: the post says "our conversion rate improved" — you reply "We ran a similar experiment; A/B testing showed that factor X contributed most of the improvement, primarily because of Y."
- **Ask a genuine question**: a real question. "How do you handle [specific scenario]? We ran into challenge Z."
- **Share a parallel case**: don't sell the product — share how you solved a similar problem

**Don't do this**: mention your product name. On LinkedIn this is immediately perceived as spam marketing.

---

### Agent 3: Blog Comment Agent

**Goal**: Leave valuable comments on high-traffic industry blogs and technical forums, drawing interested readers back to your site.

**Target platforms** (adjust for your industry):
- Hacker News (find Show HN / Ask HN threads relevant to your space)
- Reddit (r/startups, r/SaaS, r/devops, etc.)
- Industry newsletter comment sections
- Medium / Substack technical articles

**Comment quality bar is higher than X/LinkedIn**: these communities actively flag "marketing comments" — once flagged, it becomes negative exposure.

Rules:
- Each comment must be grounded in the actual content of the article (the Agent must read the full piece first, then reply)
- No product mentions of any kind (pure value output only)
- Length: 150–400 words (too short = filler; too long = ad)
- ≤ 5 comments per platform per day

---

### Agent 4: Content Generation Agent

**Goal**: Convert daily information inputs (industry news, competitor updates, user feedback) into publishable content.

**Content pipeline**:

```
Daily inputs →
  ├── RSS feeds (competitors / industry media)
  ├── User support tickets (high-frequency issues this week)
  └── Your own product changelog

Content Generation Agent →
  ├── Weekday blog posts (technical depth, search-friendly)
  ├── LinkedIn long-form posts (2–3 times/week)
  └── X threads (1 time/week, high-value topics)
```

**Editorial principle**: the Agent generates a draft; a human spends 30 minutes reviewing and tweaking; then publish. Do not let the Agent publish fully autonomously — especially in the early stages, human judgment is still the necessary quality gate.

**Search optimization**:
- Each blog post targets one long-tail keyword
- Structured data (FAQ schema) helps get cited in AI search (ChatGPT/Perplexity)
- Convert key points from existing blog posts into LinkedIn posts (content repurposing, not copying)

---

### Agent 5: Intent Signal Monitoring Agent

This is the **highest-ROI** of the five Agent types — and the most commonly overlooked.

**Core insight**: when a company posts a specific job listing on LinkedIn, that is a strong intent signal — they are experiencing the very problem you solve.

**Examples**:
- If you sell CI/CD tooling, a company posts "DevOps Engineer" → their deployment pipeline likely has pain points
- If you sell data analytics tooling, a company posts "Data Analyst" + "Data Engineer" → they are building data infrastructure
- If you sell customer service AI, a company posts "Customer Support Manager" → their support function is scaling

**Implementation**:

```python
# Intent Signal Agent
class IntentSignalAgent:
    def daily_scan(self):
        # Search LinkedIn Jobs (via official API or authorized third party)
        jobs = self.search_linkedin_jobs(
            keywords=self.config.intent_keywords,
            company_size=["51-200", "201-500"],  # target customer size
            posted_within_days=3
        )
        
        for job in jobs:
            company = job.company
            if self.already_in_crm(company):
                continue
            
            # Score intent strength
            intent_score = self.score_intent(job, company)
            if intent_score > self.threshold:
                # Add to outreach queue
                self.queue_for_outreach(company, {
                    "signal": job.title,
                    "timing": "now",
                    "approach": self.draft_first_message(company, job)
                })
```

**Outreach cadence**: detect intent signal → contact founder/VP within 48 hours → don't pitch, share relevant content → follow up after 1 week.

**Critical note**: don't reach out to too many at once (≤ 10 new companies per day); maintain manual review; intent signal scoring still needs human confirmation of quality.

---

## Open-Source Tool Map

Usable tools and frameworks found on GitHub:

### Marketing Agent Frameworks

| Project | Description | Use Case |
|---|---|---|
| `cgallic/kai-cmo-harness` | AI CMO framework for Claude Code: SEO, content, email, ads, CRO, AEO/GEO skill set | Starting point for full-stack marketing Agent |
| `SaigonXIII/evc` | Claude Code marketing workspace: 42 commands, 12 hooks, 4 industry templates | Existing Claude Code workflow |
| `unifapi-agent/agents` | MCP-based marketing Agent: SEO audit, social listening, competitor analysis | MCP integration solution |
| `Ahil-NS/marketing-agent-teams` | Multi-platform Agent teams: TikTok/Instagram/YouTube/Facebook/Reddit/X/Pinterest automation | Multi-channel distribution |
| `nowork-studio/NotFair` | Goal-driven loop marketing Agent, runs 24/7 | Automated loop execution |

### Data and Analytics Connectors

| Project | Description |
|---|---|
| `Dataslayer-AI/Marketing-skills` | Connect to 50+ platforms including Google Ads, GA4, Search Console, Meta Ads, LinkedIn Ads via Dataslayer MCP |
| `Hk669/AI-Marketing-Agents` | GenAI-based multi-Agent personalized marketing campaign generation |
| `telexintegrations/email-marketing-agent` | Email marketing Agent with Telex integration |

### Community Engagement

| Project | Description |
|---|---|
| `lucaswalter/reddit-marketing-agent` | Reddit marketing Agent (from AI Automation Community) |
| `edofransisco011/Smb-Marketing-Agent` | Small business multi-Agent marketing system (Python + Streamlit) |

---

## Engineering Implementation: Harness Design

Connecting the five Agents above into a single system requires a **Harness** — controlling each Agent's execution loop, tool permissions, rate control, and observability.

```
┌─────────────────────────────────────────────────────┐
│                  Marketing Harness                   │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Scheduler│  │Rate Limiter│ │ Prompt Registry  │  │
│  │ (cron)   │  │ per-agent │  │ (versioned prompts)│ │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │              Agent Execution Layer           │    │
│  │  X Agent │ LinkedIn │ Blog Comment │ Content │ Intent │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Logger  │  │ CRM Sync │  │  Alert System    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Core Components

**1. Scheduler**

```yaml
# config.yaml
agents:
  x_reply:
    schedule: "0 9,18 * * 1-5"  # weekdays at 9 AM and 6 PM
    daily_limit: 50
    
  linkedin_reply:
    schedule: "0 10 * * 1-5"     # weekdays at 10 AM
    daily_limit: 30
    
  blog_comment:
    schedule: "0 14 * * 1-5"     # weekdays at 2 PM
    daily_limit: 15
    
  content_gen:
    schedule: "0 7 * * 1-5"      # weekdays at 7 AM (leaves time for human review)
    
  intent_signal:
    schedule: "0 8 * * 1-5"      # weekdays at 8 AM
    daily_limit: 10
```

**2. Rate Limiter**

```python
class PerAgentRateLimiter:
    def __init__(self, agent_id: str, daily_limit: int):
        self.agent_id = agent_id
        self.daily_limit = daily_limit
        self.db = SQLiteDB("~/.marketing-harness/limits.db")
    
    def check_and_consume(self) -> bool:
        today = date.today().isoformat()
        count = self.db.get_count(self.agent_id, today)
        if count >= self.daily_limit:
            return False
        self.db.increment(self.agent_id, today)
        return True
```

**3. Prompt Registry (Versioned Prompt Management)**

```
~/.marketing-harness/prompts/
├── x_reply/
│   ├── v1_2026-05-15.md    ← archived
│   ├── v2_2026-06-20.md    ← archived  
│   └── v3_2026-07-22.md    ← current
├── linkedin_reply/
│   └── v1_2026-07-01.md    ← current
└── content_gen/
    └── v2_2026-07-10.md    ← current
```

Each prompt file has a header recording: version number, effective date, major changes, and the problem with the previous version. The 30-day expiry reminder is triggered automatically based on the file creation timestamp.

**4. Observability**

Minimum viable monitoring setup:

```python
# Each Agent logs every action to SQLite
class ActionLog:
    agent_id: str
    platform: str
    action_type: str   # "reply" | "comment" | "post" | "outreach"
    target_id: str     # tweet_id / post_id / company_id
    content_hash: str  # deduplication
    outcome: str       # "sent" | "rate_limited" | "filtered" | "error"
    timestamp: datetime
    engagement: dict   # backfilled after 7 days: likes, replies, clicks
```

Run an analytics Agent every Friday to extract from the log:
- Execution volume vs. quota utilization per Agent type
- 7-day engagement rate for replies (likes / replies / profile visits)
- Which prompt version performed best

---

## Anti-Patterns: What Not to Do

**1. Remove rate limits when results look good**

Result: platform ban, all accumulated history wiped out. Rate limits are fuses, not performance bottlenecks.

**2. Let Agents publish without review**

Maintain human review for at least the first three months. Agents make strange mistakes — for example, posting "Our product is way better than yours" under a competitor CEO's post.

**3. Use the same prompt across all platforms**

The tone on X is entirely different from LinkedIn. LinkedIn calls for a professional register; X calls for direct opinion; Hacker News requires technical rigor with no ambiguity.

**4. Ignore platform Terms of Service updates**

LinkedIn's and X's automation terms are evolving. Check ToS every quarter — do not assume what was permitted last year is still permitted today.

**5. Use the Intent Signal Agent as a bulk spam tool**

The value of intent signals lies in precision, not volume. Reaching out to 10 companies per day that genuinely match your ICP is far more effective than blasting 500.

---

## Real-World Results Reference

Using the architecture above, a two-person technical team achieved the following results within three months:

| Metric | Baseline | After Three Months |
|---|---|---|
| Organic website traffic | baseline | **2x** |
| Monthly new MRR | baseline | **+30%** |
| LinkedIn connection acceptance rate | — | ~18% |
| X reply engagement rate | — | ~4.2% |
| New intent leads per month | 0 | ~40–60 companies |

**Time investment**: 30–45 minutes per day (primarily content review + weekly data retrospective); the rest is executed by Agents.

**Cost**: LLM API costs approximately $30–50/month (Claude Sonnet calls, a few hundred API calls per day), plus tool licenses (e.g., LinkedIn official API or authorized third parties). Total cost is far below one marketing hire's monthly salary.

---

## From-Zero Action Checklist

**Week 1: Build the X Reply Agent first**

X is the easiest platform to start with (relatively open API, higher community tolerance, fast feedback loops). The goal is to identify your core search terms and complete the first full cycle end-to-end.

```bash
# Minimum viable implementation
gh repo clone cgallic/kai-cmo-harness
# Or build directly with Claude Code + a simple Python script
```

**Week 2: Add the LinkedIn Reply Agent**

Once you have a rhythm on X, add LinkedIn. Pay attention to tone adjustment.

**Week 3: Add the Content Generation Agent**

Blog output is the foundation of long-term SEO. This step pays off 3–6 months later.

**Week 4: Add the Intent Signal Agent**

If you are doing B2B, this is the Agent that produces direct sales leads fastest.

**Ongoing: Prompt review every 30 days**

Put it on the calendar. When 30 days are up — whether or not there is obvious decay — rewrite the core prompt.

---

## Core Judgment

The essence of this approach is: **mechanize the "execution layer" of human marketing work, and preserve the "strategy layer" and "review layer" for humans.**

Agents cannot figure out for you "who is my target customer" or "what is my differentiation" — those are strategy, and they must be defined by humans. But once the strategy is clear, Agents can execute tirelessly every day: find conversations, participate in conversations, monitor signals, generate content.

The greatest comparative advantage technical startups have is the ability to build this system quickly — not to ultimately use it as a substitute for thinking.

Once the system is running, your job shifts from "doing marketing" to "managing an Agent team": reviewing data, iterating prompts, adjusting strategy — rather than personally writing posts every day. That role transition is itself a form of leverage.

---

## Open-Source References and Further Reading

- **kai-cmo-harness**: cgallic/kai-cmo-harness — Claude Code AI CMO skill set
- **evc** (marketing workspace): SaigonXIII/evc — 42-command marketing workspace
- **unifapi-agent**: unifapi-agent/agents — MCP marketing Agent (SEO / social listening / competitor analysis)
- **marketing-agent-teams**: Ahil-NS/marketing-agent-teams — multi-platform Agent teams
- **AI-Marketing-Agents**: Hk669/AI-Marketing-Agents — GenAI personalized marketing campaigns
- **Dataslayer Marketing Skills**: Dataslayer-AI/Marketing-skills — connect to real ad data

© 2026 Author: Mycelium Protocol
