---
title: "Crawl4AI：把网页变成 AI 能读懂的文本——完整实践指南"
titleEn: "crawl4ai-open-source-llm-web-crawler-scraper-guide"
description: "unclecode/crawl4ai，77.6k stars，Apache 2.0，Python，GitHub #1 开源爬虫。专为 LLM 和 AI Agent 设计：直接输出干净 Markdown，支持 JS 动态页面、深度爬取（BFS/DFS）、会话保持、代理、CSS/XPath/LLM 结构化提取、Docker API。适用场景：品牌研究、竞品分析、用户评价聚合、论坛舆情、产品情报。本文是真实使用视角的完整指南：原理、安装、核心用法、三个具体案例、适用边界。"
descriptionEn: "unclecode/crawl4ai, 77.6k stars, Apache 2.0, Python, GitHub's #1 open-source crawler. Designed for LLMs and AI agents: outputs clean Markdown directly, supports JS-rendered pages, deep crawl (BFS/DFS), session reuse, proxies, CSS/XPath/LLM structured extraction, Docker API. Use cases: brand research, competitive analysis, user review aggregation, forum sentiment, product intelligence. This is a complete practical guide: how it works, install, core usage, three concrete case studies, and where it breaks."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["爬虫", "AI Agent", "Python", "开源", "数据采集", "LLM", "竞品分析", "Mycelium"]
heroImage: "../../assets/images/crawl4ai-open-source-llm-web-crawler-scraper-guide-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

你让 AI Agent 帮你做竞品研究，它能分析你给的资料，但它无法自己去网上抓数据。你得先把网页内容变成文本，剔除导航栏、广告、脚本，保留正文、评论、结构——然后才能喂给 AI。

Crawl4AI 解决的就是这一步。

GitHub #1 开源爬虫，专为 LLM 和 AI Agent 设计的网页抓取工具。77,000+ stars，50,000+ 开发者在用，输出直接是干净的 Markdown，AI 拿到就能读。

GitHub: https://github.com/unclecode/crawl4ai | ⭐ 77,579 | Apache 2.0 | Python

---

## 为什么是「专为 LLM 设计」

普通爬虫给你 HTML，你得再处理一遍才能用。Crawl4AI 的输出是**智能 Markdown**：

- 保留标题层级、表格、代码块
- 去掉导航、侧边栏、广告、Cookie 弹窗
- 保留引用提示（来源链接、原文位置）
- 支持直接结构化提取：CSS selector、XPath、或者直接让 LLM 按 schema 提取

你把这个 Markdown 扔给 Claude、GPT 或 Codex，它能直接读，不需要你再清洗。

---

## 安装

```bash
# 安装包
pip install -U crawl4ai

# 安装浏览器（Playwright 驱动）
crawl4ai-setup

# 验证安装
crawl4ai-doctor
```

如果浏览器安装有问题：
```bash
python -m playwright install --with-deps chromium
```

---

## 核心用法

### 最简单的用法

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/product")
        print(result.markdown)

asyncio.run(main())
```

三行正文代码，输出就是干净的 Markdown。

### 命令行直接用

```bash
# 抓一个页面，输出 markdown
crwl https://www.nbcnews.com/business -o markdown

# 深度爬取整个文档站，BFS 策略，最多10页
crwl https://docs.example.com --deep-crawl bfs --max-pages 10

# 用 LLM 直接回答问题（基于页面内容）
crwl https://www.example.com/products -q "Extract all product prices"
```

### 动态页面（JS 渲染）

很多评论区、无限滚动页面需要执行 JS 才能加载内容：

```python
result = await crawler.arun(
    url="https://reviews.example.com/product/123",
    js_code="""
        // 点击"加载更多评论"按钮
        const btn = document.querySelector('.load-more-reviews');
        if (btn) btn.click();
    """,
    wait_for="css:.review-item:nth-child(20)",  # 等到第20条评论出现
    delay_before_return_html=2.0,               # 额外等待2秒确保渲染
)
```

### 结构化提取（按 Schema）

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import json

schema = {
    "type": "object",
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rating": {"type": "number"},
                    "text": {"type": "string"},
                    "date": {"type": "string"},
                    "verified": {"type": "boolean"}
                }
            }
        }
    }
}

result = await crawler.arun(
    url="https://www.amazon.com/dp/B08N5WRWNW",
    extraction_strategy=LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        schema=schema,
        instruction="提取所有用户评价，包括评分、文本内容、日期"
    )
)

reviews = json.loads(result.extracted_content)
```

### 深度爬取（批量抓一个网站）

```python
from crawl4ai import DeepCrawlStrategy

result = await crawler.arun(
    url="https://forum.example.com/category/feedback",
    deep_crawl=DeepCrawlStrategy(
        strategy="bfs",        # 广度优先（BFS）或深度优先（DFS）
        max_pages=50,          # 最多抓50页
        include_patterns=["*/feedback/*", "*/review/*"],  # 只跟这些路径的链接
        exclude_patterns=["*/login*", "*/signup*"],       # 不跟这些
    ),
    resume_state="./crawl_state.json",  # 崩溃后断点续爬
)
```

---

## 三个实际案例

### 案例一：抓品牌官网竞品信息

**场景**：你想了解竞争对手最新的产品功能、定价和话术。

```python
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import CSSExtractionStrategy

async with AsyncWebCrawler() as crawler:
    # 抓产品页
    result = await crawler.arun(
        url="https://competitor.com/pricing",
        extraction_strategy=CSSExtractionStrategy(
            schema={
                "name": "pricing_table",
                "baseSelector": ".pricing-card",
                "fields": [
                    {"name": "plan_name", "selector": ".plan-title", "type": "text"},
                    {"name": "price", "selector": ".price", "type": "text"},
                    {"name": "features", "selector": ".feature-list li", "type": "list"},
                ]
            }
        )
    )
    # 把结果扔给 Claude 分析
    # "对比我们的产品，找出对方的核心差异和定价策略"
```

**输出给 AI**：结构化的竞品功能和定价 → AI 直接生成对比分析报告。

---

### 案例二：批量抓用户评价，发现需求点

**场景**：某品牌电商平台有大量用户评价，你想找出用户最常提的场景和痛点。

```python
urls = [
    "https://www.amazon.com/dp/B001/reviews",
    "https://www.amazon.com/dp/B002/reviews",
    # ...更多 ASIN
]

# 并发抓取多个页面
results = await crawler.arun_many(
    urls=urls,
    js_code="""
        // 展开"查看更多"
        document.querySelectorAll('[data-hook="review-collapsed"]')
            .forEach(el => el.click());
    """,
    delay_before_return_html=1.5,
    extraction_strategy=LLMExtractionStrategy(
        schema=review_schema,
        instruction="提取评价文本、评分、用途描述"
    )
)

# 把所有评价文本合并
all_reviews = []
for r in results:
    all_reviews.extend(json.loads(r.extracted_content)["reviews"])

# 再交给 Codex 做聚类
# "把这些评价按使用场景聚类，找出 top5 使用场景和 top5 痛点"
```

**实际效果**：上万条评价 → AI 在几分钟内输出：「主要用户群：35-45岁家庭用户；Top 场景：厨房收纳（42%）、旅行携带（28%）；Top 痛点：材质磨损（35%）、盖子松动（22%）」。

---

### 案例三：论坛/社区舆情监控

**场景**：Reddit、知乎、专业论坛上关于你产品的讨论，定期抓取。

```python
import asyncio
from crawl4ai import AsyncWebCrawler, DeepCrawlStrategy

async def monitor_forum(forum_url: str, keyword: str):
    async with AsyncWebCrawler(
        browser_config={"headless": True, "user_agent": "Mozilla/5.0 ..."}
    ) as crawler:
        result = await crawler.arun(
            url=f"{forum_url}/search?q={keyword}",
            deep_crawl=DeepCrawlStrategy(
                strategy="bfs",
                max_pages=20,
                include_patterns=["*/comments/*", "*/post/*", "*/thread/*"]
            )
        )

        # result.links 包含所有抓到的页面的链接和标题
        # result.markdown 是合并的文本内容

        # 喂给 AI：分析情绪倾向、提取关键意见
        return result

# 可以加进定时任务，每天跑一次
asyncio.run(monitor_forum("https://www.reddit.com/r/ProductCategory", "YourBrand"))
```

---

## 高级功能速览

**会话保持**（登录状态下抓取）：
```python
# 先建立一个保存登录状态的 browser profile
# 之后复用这个 session
result = await crawler.arun(
    url="https://members.forum.com/posts",
    session_id="my_logged_in_session"
)
```

**代理**（绕过 IP 限制）：
```python
result = await crawler.arun(
    url="https://geo-restricted.example.com",
    proxy_config={
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "pass"
    }
)
```

**截图**（调试或存档）：
```python
result = await crawler.arun(
    url="https://example.com",
    screenshot=True
)
# result.screenshot 是 base64 图片
```

**缓存**（避免重复抓取）：
```python
result = await crawler.arun(
    url="https://example.com",
    cache_mode=CacheMode.ENABLED  # 相同 URL 直接用缓存
)
```

**Docker 部署**（API 服务器，支持 JWT 认证）：
```bash
docker pull unclecode/crawl4ai
docker run -p 11235:11235 \
  -e CRAWL4AI_API_TOKEN=your_token \
  unclecode/crawl4ai

# 然后通过 REST API 调用
curl -X POST http://localhost:11235/crawl \
  -H "Authorization: Bearer your_token" \
  -d '{"urls": ["https://example.com"]}'
```

---

## 适用边界

**最适合的场景**：

✅ 公开可见的网页内容（不需要登录就能看到）

✅ 需要 JS 渲染的动态页面（SPA、无限滚动、懒加载评论）

✅ 需要批量遍历一个网站内的多个页面（深度爬取）

✅ 格式规律的结构化内容（商品列表、用户评价、新闻文章）

✅ 需要把抓取结果直接喂给 AI 分析的场景

**容易卡住的情况**：

❌ **必须登录才能看内容**：某些论坛、付费内容平台。可以用 session/browser profile 绕过，但需要手动先登录一次。

❌ **强 CAPTCHA 验证**：reCAPTCHA v3、Cloudflare Turnstile 等——这类验证需要额外的解 CAPTCHA 服务。

❌ **严格的频率限制**：大型平台（Amazon、LinkedIn）会按 IP 封锁高频请求，需要搭配代理轮换。

❌ **仅存在于手机 App 的内容**：App 端独有的帖子和评论，网页端没有对应 URL，无法抓取。

❌ **页面结构经常变化**：用 CSS selector 写的规则，页面改版后需要更新。LLM 提取对结构变化更有弹性，但成本更高。

**关于 robots.txt 和使用合规**：Crawl4AI 本身不强制 robots.txt，但建议遵守目标网站的爬取规则和使用条款，避免对目标服务器造成过大压力（设置合理的 delay）。

---

## 与 AI Agent 的工作流

Crawl4AI 本身有官方 skill 包，可以直接给 Claude/Cursor/Windsurf 等 AI 编程助手安装，让 Agent 直接调用：

```bash
# AI coding assistant 可以在执行任务时直接调用 Crawl4AI
# 无需切换工具，Agent 自己决定何时抓、抓哪里、怎么处理结果
```

典型的 AI 工作流：

```
用户：帮我分析竞品 X 的用户评价
  ↓
Agent 调用 Crawl4AI 抓取评价页面（含动态加载）
  ↓
Agent 用 LLM extraction 结构化评价数据
  ↓
Agent 做聚类分析，生成报告
  ↓
输出：场景 Top5、痛点 Top5、细分人群画像
```

省下来的主要是收集和整理时间。你把精力留给判断。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Crawl4AI: Turn Any Web Page into LLM-Ready Text — A Complete Practical Guide

*by Mycelium Protocol*

---

You tell an AI agent to do competitive research. It can analyze what you give it — but it can't go out and grab data from the web. You first have to turn web pages into text, strip out navigation, ads, and scripts, keep the body content, comments, and structure — then feed it to the AI.

Crawl4AI handles that step.

GitHub's #1 open-source crawler, designed for LLMs and AI agents. 77,000+ stars. Outputs clean Markdown directly — AI picks it up and reads it, no further cleaning needed.

GitHub: https://github.com/unclecode/crawl4ai | ⭐ 77,579 | Apache 2.0 | Python

---

### Why "Designed for LLMs"

A regular crawler gives you HTML. You have to process it again before it's useful. Crawl4AI outputs **smart Markdown**:

- Heading hierarchy, tables, code blocks — preserved
- Navigation, sidebars, ads, cookie banners — stripped
- Citation hints (source links, original positions) — kept
- Structured extraction: CSS selectors, XPath, or LLM-based with a schema

Hand this Markdown to Claude, GPT, or Codex and it reads it directly.

---

### Install

```bash
pip install -U crawl4ai
crawl4ai-setup      # installs Playwright browser
crawl4ai-doctor     # verify install
```

---

### Core Usage

**Simplest case:**
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/product")
        print(result.markdown)

asyncio.run(main())
```

**CLI:**
```bash
crwl https://www.nbcnews.com/business -o markdown
crwl https://docs.example.com --deep-crawl bfs --max-pages 10
crwl https://www.example.com/products -q "Extract all product prices"
```

**Dynamic pages (JS-rendered, infinite scroll, "load more" buttons):**
```python
result = await crawler.arun(
    url="https://reviews.example.com/product/123",
    js_code="""
        const btn = document.querySelector('.load-more-reviews');
        if (btn) btn.click();
    """,
    wait_for="css:.review-item:nth-child(20)",
    delay_before_return_html=2.0,
)
```

**Structured extraction by LLM schema:**
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

result = await crawler.arun(
    url="https://www.amazon.com/dp/B08N5WRWNW",
    extraction_strategy=LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        schema=review_schema,
        instruction="Extract all user reviews with rating, text, date"
    )
)
```

**Deep crawl (multiple pages in one site):**
```python
from crawl4ai import DeepCrawlStrategy

result = await crawler.arun(
    url="https://forum.example.com/category/feedback",
    deep_crawl=DeepCrawlStrategy(
        strategy="bfs",
        max_pages=50,
        include_patterns=["*/feedback/*", "*/review/*"],
        exclude_patterns=["*/login*"],
    ),
    resume_state="./crawl_state.json",   # crash recovery
)
```

---

### Three Practical Case Studies

**Case 1: Competitor product and pricing intel**

Crawl the competitor's pricing page with CSS extraction → structured plan/feature/price table → feed to Claude: "Compare against our product, identify their core differentiation and pricing strategy."

**Case 2: User review aggregation (10,000+ records)**

Batch-crawl product review pages with JS click-to-expand → LLM extraction into structured schema → feed all reviews to Codex: "Cluster by use scenario, surface top 5 use cases and top 5 pain points."

Real output: "Primary users: 35-45 year old families. Top scenarios: kitchen storage (42%), travel (28%). Top pain points: material wear (35%), loose lid (22%)."

**Case 3: Forum and community sentiment monitoring**

Deep crawl Reddit/specialized forums for mentions → batch markdown → AI sentiment analysis: positive/negative ratio, key opinion threads, emerging issues.

---

### Where It Breaks

**Works well:**
✅ Publicly visible content (no login required)
✅ JS-rendered pages — SPAs, infinite scroll, lazy-loaded comments
✅ Bulk traversal of a site's pages
✅ Structured content with regular patterns

**Where it struggles:**
❌ **Login-gated content**: Need session/browser profile reuse — manual first login required
❌ **Strong CAPTCHA**: reCAPTCHA v3, Cloudflare Turnstile — needs a separate CAPTCHA service
❌ **Strict rate limits**: Amazon, LinkedIn block high-frequency IPs — needs rotating proxies
❌ **App-only content**: Mobile app posts with no web URL can't be reached
❌ **Frequently changing page structure**: CSS rules break on redesigns — LLM extraction is more resilient but costs more

---

### Workflow with AI Agents

```
User: Analyze competitor X's user reviews
  ↓
Agent calls Crawl4AI → scrapes review pages (with dynamic loading)
  ↓
Agent uses LLM extraction → structured review data
  ↓
Agent clusters data → generates report
  ↓
Output: Top 5 scenarios, Top 5 pain points, user segment profiles
```

What you save: collection and organization time. What you keep: judgment.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
