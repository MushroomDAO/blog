---
title: "Scrapling：自适应元素追踪 + Cloudflare 绕过，8.5 万星 Python 爬虫拆解"
titleEn: "Scrapling: Adaptive Element Tracking + Cloudflare Bypass — 85K-Star Python Scraper Teardown"
description: "D4Vinci/Scrapling，85060星，BSD-3-Clause，Python。自适应 Web 爬虫库：CSS/XPath 元素签名在网站改版后自动重定位（auto_save + adaptive），StealthyFetcher 绕过 Cloudflare Turnstile，Spider 框架提供 Scrapy 风格 API 含 AutoThrottle/暂停恢复/流式模式，MCP Server 内置反 Prompt Injection 净化，page.markdown() 一行生成 RAG 语料。"
descriptionEn: "D4Vinci/Scrapling, 85060 stars, BSD-3-Clause, Python. Adaptive web scraping library: CSS/XPath element signatures auto-relocate after site redesigns (auto_save + adaptive), StealthyFetcher bypasses Cloudflare Turnstile, Spider framework with Scrapy-style API including AutoThrottle/pause-resume/streaming, MCP Server with built-in anti-prompt-injection sanitization, page.markdown() generates RAG-ready content in one line."
pubDate: 2026-10-02
heroImage: "../../assets/images/scrapling-adaptive-web-scraper-cloudflare-bypass-mcp-python-banner.jpg"
category: "Tech-Experiment"
tags: ["爬虫", "Python", "Cloudflare", "MCP", "自适应", "开源拆解", "AI工具"]
lang: "zh-CN"
wechatTitle: "Scrapling：自适应爬虫，网站改版也不怕"
wechatDigest: "8.5万星BSD-3；绕Cloudflare开箱；自适应元素追踪；Scrapy风格Spider；MCP接AI"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 背景

爬虫有两个经典痛点：

**网站一改版，所有 selector 就报废**。维护过爬虫的人都知道，目标网站每次改 DOM 结构，就意味着回去找新的 CSS 路径或 XPath，然后重新部署。一个月爬三次的站，可能一年要更新选择器两三次。

**Cloudflare 的防护越来越强**。Turnstile 验证、Interstitial 页面，普通 HTTP 请求根本过不去，Playwright 也常被识别为无头浏览器。

Scrapling 的方向是把这两个问题做成库层面的解决方案，而不是每个项目自己摸索。

仓库：github.com/D4Vinci/Scrapling  
**Stars：85,060 | BSD-3-Clause | Python | 创建：2024-10-13**

---

## 核心能力一：自适应元素追踪

这是 Scrapling 最差异化的功能，值得单独说清楚。

**问题**：网站改版后，原来的 `div.product-title > h2` 可能变成 `section.item-header h3`，selector 失效，爬虫报错。

**Scrapling 的做法**：`auto_save=True` 在第一次成功提取元素时，把元素的**签名**（文本特征、周围结构、相对位置等多个维度）存下来。再次爬取时，如果原始 selector 失败，`adaptive=True` 会根据这个签名在新 DOM 结构里寻找最相似的元素。

```python
from scrapling.fetchers import Fetcher

page = Fetcher(auto_save=True).get('https://example.com', follow_redirects=True)
product_title = page.find('div.product-title h2', auto_save=True)
print(product_title.text)
```

下次网站改版后：

```python
# 即使 selector 不再有效，adaptive=True 会搜索签名匹配的元素
page = Fetcher(auto_save=True).get('https://example.com', follow_redirects=True)
product_title = page.find('div.product-title h2', adaptive=True)  # 自动重定位
print(product_title.text)
```

这个机制不是万能的——签名相似度取决于新旧结构的变化程度。但对于布局微调、class 重命名这类常见改版，它能免去手动维护选择器的工作。

---

## 核心能力二：StealthyFetcher 绕过 Cloudflare

Scrapling 内置四种 Fetcher，各自处理不同场景：

| Fetcher | 适用场景 |
|---------|---------|
| `Fetcher` | 普通 HTTP 请求；TLS 指纹伪装，HTTP/3 支持 |
| `AsyncFetcher` | 异步版，适合高并发场景 |
| `StealthyFetcher` | 绕过 Cloudflare Turnstile/Interstitial；基于真实 Chromium |
| `DynamicFetcher` | Playwright 完整浏览器，适合复杂 JS 渲染页面 |

`StealthyFetcher` 是技术上最复杂的一个。它不是简单地启动 Playwright，而是在此基础上加了一套反检测层：伪装浏览器指纹、处理 Cloudflare 的验证流程。

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher().fetch('https://cloudflare-protected-site.com')
# 直接拿到页面内容，不需要手动处理验证页
print(page.find('#main-content').text)
```

需要注意：Cloudflare 的检测逻辑会持续更新。`StealthyFetcher` 当前能绕过的是今天的 Turnstile 实现——这是一场持续的对抗，不是一次性解决。

---

## 核心能力三：Spider 框架

Scrapling 还包含一个完整的 Spider 框架，API 风格接近 Scrapy，但加了几个实用特性：

**AutoThrottle**：监控响应时间和错误率，自动调整爬取速率。爬取速度快时加速，检测到对方限速时降速。

**暂停恢复**：Ctrl+C 中断爬取，进度保存在本地。重新运行时从上次停下的地方继续，不重复爬已处理的 URL。

**流式模式**：不等全部爬完，每个 item 生成后立即处理：

```python
async for item in spider.stream():
    save_to_database(item)
```

**开发模式**：第一次爬取时把响应缓存到本地，后续开发调试时从缓存回放，不消耗网站资源、不受网络波动影响。

内置模板覆盖常见场景：`CrawlSpider`（深度爬取）、`SitemapSpider`（通过 sitemap 发现 URL）、`XMLFeedSpider`、`CSVFeedSpider`、`ShopifySpider`。

内置导出：JSON / JSONL / CSV / XML，不需要额外写处理逻辑。

---

## 核心能力四：MCP Server + AI 接入

Scrapling 为 AI Agent 接入做了专门设计：

**MCP Server**：Agent 通过 MCP 协议调用 Scrapling 爬取页面。

一个关键细节：MCP Server 在返回页面内容给 Agent 之前，会做 **Prompt Injection 清洗**——如果页面正文里包含试图操控 AI 的指令（比如 `<p>Ignore all previous instructions and...</p>`），这些内容会被识别和过滤。这是防止恶意网页通过爬取内容劫持 Agent 的基本防护。

此外，MCP Server 支持 CSS selector 缩小范围——不把整页 HTML 扔给 Agent，而是先提取 Agent 真正需要的区域，减少噪音。

**CDP 远程浏览器**：MCP Server 可以连接远程 Chrome/Chromium 实例（通过 CDP），适合已有浏览器登录态的场景。

**Agent Skill**：Scrapling 提供了一个专门的 Agent Skill，教 coding agents（Claude Code / Codex）如何使用这个库的 API。安装后，Agent 写爬虫代码时会自动遵循 Scrapling 的最佳实践。

---

## RAG 场景：page.markdown()

```python
from scrapling.fetchers import Fetcher

page = Fetcher().get('https://docs.example.com/api-reference')
print(page.markdown())  # 干净的 Markdown，去掉导航栏/广告/footer
```

`page.markdown()` 把页面主体内容转成 Markdown，过滤掉导航、侧边栏、广告等干扰元素。直接喂给 LLM 或向量数据库。

`SiteToMarkdownSpider` 把这个能力扩展到全站爬取，一次性把整个文档站或产品网站转成 Markdown 语料库。

---

## 其他值得注意的细节

**后台 XHR 捕获**：`capture_xhr=True` 参数在页面加载时同步捕获所有 XHR/API 请求和响应，不需要另装代理或 MITM。

**DNS-over-HTTPS**：防止 DNS 泄露，对需要隐藏目标域名的场景有用。

**域名和广告屏蔽**：内置约 3,500 个屏蔽域名，减少爬取时的噪音请求。

**92% 测试覆盖率**：对于爬虫库来说这个覆盖率偏高，说明核心逻辑有比较完整的测试。

**10× JSON 序列化**：比 Python 标准库的 `json` 快 10 倍，对高吞吐量爬取有实际意义。

---

## 需要知道的限制

**BSD-3-Clause，不是 MIT 或 Apache**。BSD-3 基本不限商用，但有一条：不得用原项目名称或作者名为衍生产品背书。实际使用中约束很小，但不是无约束。

**StealthyFetcher 是对抗性功能**，会随 Cloudflare 更新而时效变化。用作关键业务依赖时需要留意版本更新和有时效的绕过状态。

**85K stars 来自约一年的积累**（2024-10-13 创建）。增速很快，但也意味着一些边缘功能可能仍在稳定阶段。

**自适应追踪依赖签名质量**。对于大幅重构的网站（不只是 CSS class 改了，整个结构都不同），自适应可能找不到对应元素，仍需手动更新。

---

## 关键数字

| 指标 | 值 |
|------|----|
| Stars | 85,060 |
| Forks | 8,710 |
| License | BSD-3-Clause |
| 语言 | Python |
| 创建时间 | 2024-10-13 |
| 测试覆盖率 | 92% |
| 内置屏蔽域名 | ~3,500 |
| Spider 模板 | 5 种 |

---

## 综合判断

Scrapling 把两个独立问题打包进了一个库：自适应 selector 和反检测爬取。这两个功能原来都需要各自维护一套工具链，Scrapling 把它们统一了。

对于**长期维护的爬虫项目**，自适应元素追踪是实质性的工程节省——不用每次网站改版都手动更新选择器。

对于**需要绕过防护的场景**，`StealthyFetcher` 提供了一个有效但时效性依赖的方案；`DynamicFetcher` 是更稳定但更重的备选。

MCP Server 的防 Prompt Injection 设计是加分项——不只是"能用"，还考虑了 Agent 的安全边界。

85K stars 在 Python 爬虫库里处于头部，但也说明它不是新出现的项目，而是已经经过市场验证。

---

> 开源仅供学习，BSD-3-Clause 许可证，商业使用限制极少，具体条款见仓库 LICENSE 文件。

---

<!--EN-->

## Scrapling: Adaptive Element Tracking + Cloudflare Bypass — 85K-Star Python Scraper Teardown

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Two Problems, One Library

Web scrapers break for two predictable reasons: the target site redesigns its DOM, and every CSS selector becomes invalid. Or Cloudflare protection blocks the request before you even reach the content.

Scrapling approaches both as library-level problems rather than per-project workarounds.

Repo: github.com/D4Vinci/Scrapling  
**85,060 stars | BSD-3-Clause | Python | Created: 2024-10-13**

---

### Adaptive Element Tracking

When `auto_save=True`, Scrapling stores an element signature on first successful extraction — a multi-dimensional fingerprint based on text characteristics, surrounding structure, and relative position. On subsequent runs with `adaptive=True`, if the original selector fails, Scrapling searches the new DOM for the most structurally similar match.

```python
from scrapling.fetchers import Fetcher

# First run: save the element signature
page = Fetcher(auto_save=True).get('https://example.com', follow_redirects=True)
title = page.find('div.product-title h2', auto_save=True)

# After site redesign: adaptive relocation
page = Fetcher(auto_save=True).get('https://example.com', follow_redirects=True)
title = page.find('div.product-title h2', adaptive=True)  # finds the moved element
```

This handles the common case of class renames and layout shuffles — not complete DOM overhauls. But it eliminates a significant category of maintenance overhead.

---

### Four Fetchers

| Fetcher | Use Case |
|---------|----------|
| `Fetcher` | Plain HTTP with TLS fingerprint spoofing, HTTP/3 support |
| `AsyncFetcher` | Async version for high-concurrency scraping |
| `StealthyFetcher` | Bypasses Cloudflare Turnstile/Interstitial; real Chromium with anti-detection layer |
| `DynamicFetcher` | Full Playwright browser for complex JS-rendered pages |

`StealthyFetcher` is the most technically complex. It adds browser fingerprint spoofing and Cloudflare challenge handling on top of Playwright. Important caveat: Cloudflare's detection logic updates continuously — this is an adversarial function that depends on the current Cloudflare implementation.

---

### Spider Framework

Scrapy-style API with three additions that matter for long-running crawls:

**AutoThrottle**: Monitors response times and error rates; automatically increases or decreases crawl rate. Backs off when the target shows signs of rate limiting.

**Pause/Resume**: Ctrl+C checkpoints progress to disk. Restart and the crawl continues from where it stopped — no duplicate processing of already-handled URLs.

**Streaming mode**: Items are available as they're found, not after the entire crawl completes:

```python
async for item in spider.stream():
    save_to_database(item)
```

**Dev mode**: First run caches responses locally. Subsequent development iterations replay from cache — no network load, no rate-limit interference while debugging parsing logic.

Built-in templates: `CrawlSpider`, `SitemapSpider`, `XMLFeedSpider`, `CSVFeedSpider`, `ShopifySpider`. Built-in export: JSON / JSONL / CSV / XML.

---

### MCP Server and AI Integration

**Prompt injection sanitization**: Before passing page content to an AI agent, the MCP Server strips constructs that attempt to override LLM instructions. A page with `<p>Ignore all previous instructions and...</p>` in the body won't be able to hijack the agent through scraped content.

**CSS selector narrowing**: Rather than sending full raw HTML to the agent, the MCP Server can be configured to extract only the relevant DOM section first — less noise, less context window usage.

**CDP remote browsers**: Connects to existing Chrome/Chromium instances via Chrome DevTools Protocol, useful when you need to reuse a logged-in browser session.

**Agent Skill**: A packaged skill for Claude Code / Codex that teaches the agent how to use Scrapling's API. When installed, agents writing scraping code default to Scrapling patterns.

---

### RAG-Ready Output

```python
from scrapling.fetchers import Fetcher

page = Fetcher().get('https://docs.example.com/api-reference')
markdown = page.markdown()  # clean content, navigation/ads/footers stripped
```

`page.markdown()` extracts page body content as clean Markdown. `SiteToMarkdownSpider` extends this to full-site crawls — one run produces a Markdown corpus from an entire documentation site.

---

### Other Details Worth Knowing

**Background XHR capture** (`capture_xhr=True`): Captures all XHR/API requests and responses during page load — no proxy or MITM required.

**DNS-over-HTTPS**: Prevents DNS leakage for scenarios where the target domain needs to remain private.

**Domain and ad blocking**: ~3,500 built-in blocked domains, reducing noise in crawl sessions.

**92% test coverage**: High for a scraping library; the core element tracking and adaptive logic has meaningful test coverage.

**10× JSON serialization**: Faster than the Python standard library, relevant for high-throughput crawls generating large output volumes.

---

### Limitations

**BSD-3-Clause, not MIT.** The main restriction: don't use the project name or author names to endorse derivative products. For most practical use cases, there's no meaningful constraint — but it's not Apache-2.0 permissive.

**StealthyFetcher is adversarial.** Cloudflare updates its detection; what bypasses today may not bypass in three months. Don't treat it as a guaranteed capability for critical production workloads.

**Adaptive tracking depends on structural similarity.** Major redesigns (not just class renames, but full layout restructuring) may produce zero match. Manual selector updates are still needed in those cases.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 85,060 |
| Forks | 8,710 |
| License | BSD-3-Clause |
| Language | Python |
| Created | 2024-10-13 |
| Test coverage | 92% |
| Blocked domains | ~3,500 |
| Spider templates | 5 |

---

### Verdict

Scrapling packages two independently useful capabilities into one library: adaptive selectors that survive site redesigns, and anti-detection fetching that handles modern bot protection. Both existed as fragmented per-project solutions before.

For **long-lived scraping projects**, adaptive element tracking is real maintenance savings. For **sites with Cloudflare protection**, `StealthyFetcher` is effective but time-sensitive — `DynamicFetcher` is the heavier, more stable fallback.

The MCP Server's prompt injection sanitization is an unusual detail for a scraping library — it treats Agent security as a first-class concern, not an afterthought.

85K stars in one year puts it in the top tier of Python scraping libraries. The codebase is better-tested than average for this category.

---

> Open source for learning only. BSD-3-Clause license — minimal commercial restrictions; see the repository LICENSE file for exact terms.
