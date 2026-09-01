---
title: "TinyFish：AI Agent 的 Web 基础设施，Search + Fetch 免费，一行装进 Claude Code"
titleEn: "TinyFish: Web Infrastructure for AI Agents — Search + Fetch Free, One-Line Skill for Claude Code"
description: "TinyFish 是面向 AI Agent 的 Web 基础设施，提供 Search、Fetch、Agent、Browser 四个端点，Search 和 Fetch 已永久免费。本文是完整的安装与使用指南：Skill 一行安装、MCP Server 配置、CLI/REST API/SDK 示例，以及四个端点的选择逻辑。"
descriptionEn: "TinyFish is web infrastructure for AI agents — Search, Fetch, Agent, and Browser endpoints. Search and Fetch are now free. Complete guide: one-line Skill install, MCP Server config, CLI/REST/SDK examples, and the decision logic for which endpoint to use."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Tech-Experiment"
tags: ["TinyFish", "AI agent", "web scraping", "MCP", "Claude Code", "skill", "REST API", "agent tools", "web search"]
heroImage: "../../assets/images/tinyfish-web-agent-api-search-fetch-mcp-skill-claude-code-banner.jpg"
author: "Mycelium Protocol"
---

## Agent 需要上网，但上网很难

给 AI Agent 提供实时 Web 数据是一个比看起来更难的问题：大多数网页是动态渲染的，有反爬机制，返回的 HTML 里 90% 是导航栏、脚本和广告——直接喂给模型，token 暴涨，信息密度极低。

**TinyFish** 解决这个问题：它是一套专门为 AI Agent 设计的 Web 基础设施，把「搜索」「抓取」「多步骤自动化」「托管浏览器」打包成四个简洁的端点，背后是真实浏览器渲染 + 内置反检测 + 干净的结构化输出。

客户包括 Google Hotels、DoorDash、ClassPass、Amazon。

**好消息：Search 和 Fetch 现在永久免费。**

---

## 四个端点，四个场景

| 端点 | 做什么 | 最适合 | 速度 | 价格 |
|---|---|---|---|---|
| **Search** | 实时结构化网页搜索，返回 JSON | 任何需要检索的场景；Drop-in 替代 RAG 检索层 | < 0.5s | **免费** |
| **Fetch** | 任意 URL → 干净 Markdown/JSON/HTML | 读取特定页面，给模型喂干净内容 | 几秒 | **免费** |
| **Agent** | URL + 自然语言目标 → 结构化 JSON | 多步骤流程、复杂任务、结构化数据提取 | 10s-数分钟 | 按量计费 |
| **Browser** | 托管云浏览器，接入你的 Playwright/Selenium | 深度定制 Agent 和脚本 | 实时 | 按量计费 |

**选择逻辑**（来自官方文档）：
- 需要搜索结果列表 → **Search**
- 已有 URL，要读取页面内容 → **Fetch**
- 需要 Agent 在网站上完成一个工作流 → **Agent**
- 需要直接控制浏览器跑自定义脚本 → **Browser**

---

## 安装方式一：Agent Skill（Claude Code / Codex / Cursor）

一行命令，把 TinyFish 能力装进任何支持 Skill 的 AI 编码工具：

```bash
npx skills add github.com/tinyfish-io/tinyfish-cookbook --skill use-tinyfish
```

安装后，Agent 会：
- 自动知道什么时候该用 Search vs Fetch vs Agent
- 无需用户说「用 TinyFish」——只要请求涉及实时 Web 信息，Skill 就会触发
- 通过 CLI 调用，结果写到文件系统而不是消耗模型 context window

Skill 的触发词（不需要显式说）：
- **搜索/发现类**：search, find, look up, research, compare, latest, current, news, pricing, docs
- **URL/页面类**：fetch, read, summarize, extract from this page, inspect this URL
- **来源支撑类**：answer using web sources, verify a fact, check if something changed
- **网站操作类**：interact with a site, click through, fill forms, collect structured data

在 [skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish](https://skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish) 可以预览完整 Skill 内容。

---

## 安装方式二：MCP Server

在 Claude Code、Cursor、Codex、ChatGPT Desktop 或任何 MCP-aware 客户端里添加配置：

```json
{
  "mcpServers": {
    "tinyfish": { "url": "https://mcp.tinyfish.ai" }
  }
}
```

配置后，Claude 可以直接通过 MCP 工具调用 Search 和 Fetch，无需任何额外代码。

---

## 安装方式三：CLI

```bash
npm install -g @tiny-fish/cli
tinyfish auth login

# 搜索
tinyfish search query "latest Claude model benchmarks"

# 抓取页面
tinyfish fetch content get https://anthropic.com/news

# 搜索学术论文
tinyfish search query "4D Gaussian Splatting 2026" --domain research_paper
```

CLI 把结果写到文件系统而不是 stdout，token 使用效率更高。

---

## 安装方式四：REST API

先拿 API Key：[agent.tinyfish.ai](https://agent.tinyfish.ai/sign-up)（Search + Fetch 永久免费，无需信用卡）

```bash
# Search
curl "https://api.search.tinyfish.ai?query=AI+agent+tools+2026" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# Fetch — 单 URL
curl -X POST https://api.fetch.tinyfish.ai \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://github.com/trending"]}'

# Agent — 多步骤任务（SSE 流式）
curl -N -X POST https://agent.tinyfish.ai/v1/automation/run-sse \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "goal": "Find the top 5 AI-related stories today. Return JSON with title, URL, and points."
  }'
```

---

## 安装方式五：SDK

```bash
# Python
pip install tinyfish

# TypeScript
npm install @tiny-fish/sdk
```

```python
from tinyfish import TinyFish

client = TinyFish(api_key="YOUR_API_KEY")

# Search
results = client.search("best AI coding tools 2026")
for r in results:
    print(r.title, r.url)

# Fetch
pages = client.fetch(["https://anthropic.com/news"])
print(pages[0].markdown)
```

两个 SDK 完整覆盖 Search、Fetch、Browser、Agent 和 Vault（Agent 级别的认证凭证和会话内存）。

---

## Search API 的高级参数

Search 不只是简单检索，有几个实用的进阶参数：

```bash
# 地理定向（中文结果，针对中国市场）
curl "https://api.search.tinyfish.ai?query=AI工具&location=CN&language=zh-CN" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# 新鲜度过滤（最近 24 小时）
curl "https://api.search.tinyfish.ai?query=claude+model+update&recency_minutes=1440" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# 学术论文搜索
curl "https://api.search.tinyfish.ai?query=4DGS+reconstruction&domain_type=research_paper&pub_year_min=2025" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# 新闻搜索
curl "https://api.search.tinyfish.ai?query=Anthropic+Claude&domain_type=news&after_date=2026-08-01" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# 附加搜索意图（帮助系统更准确理解需求）
curl "https://api.search.tinyfish.ai?query=tinyfish+SDK&purpose=Find+installation+guide+for+Python" \
  -H "X-API-Key: $TINYFISH_API_KEY"
```

---

## 实用场景

**竞品价格监控**：Fetch 定期抓取竞品定价页 → 结构化 JSON → 送进数据库

**研究 Pipeline**：Search 检索 ArXiv 论文 → Fetch 获取摘要全文 → 模型总结

**GitHub 趋势追踪**：每天跑 Fetch 抓 GitHub Trending → 对比昨日结果，提取新上榜项目

**多步骤表单填写**：Agent 端点处理需要登录和点击的工作流，直接返回结果 JSON

**Cookbook 里的现成 demo**：
- `lego-hunter` — 跨 15+ 零售商追踪稀有乐高库存
- `silicon-signal` — 半导体供应链 + 交货期信号
- `research-sentry` — 语音优先的学术研究助手，扫描 ArXiv 和 PubMed
- `tinyskills` — 从文档、GitHub 和博客生成 SKILL.md（正是 TinyFish 的自指 demo）

---

## 总结

TinyFish 做了一件对 AI Agent 开发者很实际的事：**把访问 Web 从「需要自己搭」变成「API 调用」**，内置真实浏览器渲染、反检测、token 效率优化。Search 和 Fetch 永久免费，意味着大多数使用场景（检索 + 读页面）零成本。

对于 Claude Code 用户，一行 `npx skills add` 就能让 Agent 在需要时自动拿到实时 Web 数据，不需要手动触发，不需要写额外代码。

**官网**: [tinyfish.io](https://tinyfish.io)  
**文档**: [docs.tinyfish.ai](https://docs.tinyfish.ai)  
**Cookbook**: [github.com/tinyfish-io/tinyfish-cookbook](https://github.com/tinyfish-io/tinyfish-cookbook)  
**Skill**: [skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish](https://skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish)  
**Discord**: [discord.gg/tinyfish](https://discord.gg/tinyfish)

<!--EN-->

## AI Agents Need the Web — But the Web Is Hard

Giving AI agents real-time web data is harder than it looks: most pages are dynamically rendered, have anti-bot measures, and return HTML where 90% is nav bars, scripts, and ads — feed that directly to a model and tokens spike while information density collapses.

**TinyFish** solves this: web infrastructure purpose-built for AI agents, packaging "search," "fetch," "multi-step automation," and "managed browser" into four clean endpoints, backed by real browser rendering, built-in stealth, and structured clean output.

Customers include Google Hotels, DoorDash, ClassPass, and Amazon.

**Key news: Search and Fetch are now permanently free.**

---

## Four Endpoints, Four Scenarios

| Endpoint | Does | Best for | Speed | Price |
|---|---|---|---|---|
| **Search** | Real-time structured web search → JSON | Any retrieval task; drop-in for RAG retrieval | < 0.5s | **Free** |
| **Fetch** | Any URL → clean Markdown/JSON/HTML | Reading specific pages, token-efficient LLM input | Seconds | **Free** |
| **Agent** | URL + natural language goal → structured JSON | Multi-step flows, complex tasks, data extraction | 10s–minutes | Metered |
| **Browser** | Managed cloud browser for your Playwright/Selenium | Deep-custom agents and scripts | Real-time | Metered |

**Decision logic:**
- Need a list of search results → **Search**
- Have the URL, want to read the page → **Fetch**
- Need an agent to complete a workflow on a site → **Agent**
- Need direct browser control for custom scripts → **Browser**

---

## Install Option 1: Agent Skill (Claude Code / Codex / Cursor)

One command, TinyFish capabilities installed into any Skill-aware AI coding tool:

```bash
npx skills add github.com/tinyfish-io/tinyfish-cookbook --skill use-tinyfish
```

After install, the agent will:
- Know when to use Search vs Fetch vs Agent automatically
- Trigger without the user saying "use TinyFish" — any request involving live web info activates it
- Write results to the filesystem instead of consuming model context window tokens

Skill auto-triggers on: search/find/research/compare/latest/news/pricing, fetch/read/summarize/extract from URL, answer using web sources, interact with a site.

Browse the full Skill at [skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish](https://skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish).

---

## Install Option 2: MCP Server

Add to Claude Code, Cursor, Codex, ChatGPT Desktop, or any MCP-aware client:

```json
{
  "mcpServers": {
    "tinyfish": { "url": "https://mcp.tinyfish.ai" }
  }
}
```

Claude can then call Search and Fetch directly as MCP tools, no extra code needed.

---

## Install Option 3: CLI

```bash
npm install -g @tiny-fish/cli
tinyfish auth login

tinyfish search query "latest Claude benchmarks"
tinyfish fetch content get https://anthropic.com/news
tinyfish search query "4D Gaussian Splatting" --domain research_paper
```

CLI writes results to the filesystem rather than stdout — better for token efficiency.

---

## Install Option 4: REST API

Get a free API key at [agent.tinyfish.ai](https://agent.tinyfish.ai/sign-up) (no credit card for Search + Fetch):

```bash
# Search
curl "https://api.search.tinyfish.ai?query=AI+agent+tools+2026" \
  -H "X-API-Key: $TINYFISH_API_KEY"

# Fetch
curl -X POST https://api.fetch.tinyfish.ai \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://github.com/trending"]}'

# Agent (streaming SSE)
curl -N -X POST https://agent.tinyfish.ai/v1/automation/run-sse \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "goal": "Find top 5 AI stories today. Return JSON with title, URL, points."
  }'
```

---

## Install Option 5: SDK

```python
from tinyfish import TinyFish

client = TinyFish(api_key="YOUR_API_KEY")

results = client.search("best AI coding tools 2026")
for r in results:
    print(r.title, r.url)

pages = client.fetch(["https://anthropic.com/news"])
print(pages[0].markdown)
```

Both Python and TypeScript SDKs cover all four endpoints plus Vault (agent-grade credential storage and encrypted session reuse).

---

## Advanced Search Parameters

```bash
# Geo-targeted (Chinese results for China market)
?query=AI工具&location=CN&language=zh-CN

# Freshness filter (last 24 hours)
?query=claude+update&recency_minutes=1440

# Academic papers
?query=4DGS+reconstruction&domain_type=research_paper&pub_year_min=2025

# News with date range
?query=Anthropic+Claude&domain_type=news&after_date=2026-08-01

# Search intent (helps system understand the goal behind the query)
?query=tinyfish+SDK&purpose=Find+Python+installation+guide
```

---

## Cookbook Demos Worth Running

- **tinyskills** — generates a SKILL.md from docs, GitHub, and blogs — TinyFish's self-referential demo
- **silicon-signal** — semiconductor supply chain + lead-time signals
- **research-sentry** — voice-first academic research assistant scanning ArXiv and PubMed
- **competitor-analysis** — live competitive pricing intelligence dashboard

---

## Summary

TinyFish does one practically useful thing for AI agent developers: **turns accessing the web from "build it yourself" into an API call**, with real browser rendering, stealth, and token efficiency built in. Search and Fetch are permanently free, which covers the majority of use cases (retrieval + page reading) at zero cost.

For Claude Code users, one `npx skills add` line gives the agent automatic access to live web data whenever it needs it — no explicit trigger required, no extra code.

**Website**: [tinyfish.io](https://tinyfish.io)  
**Docs**: [docs.tinyfish.ai](https://docs.tinyfish.ai)  
**Cookbook**: [github.com/tinyfish-io/tinyfish-cookbook](https://github.com/tinyfish-io/tinyfish-cookbook)  
**Skill**: [skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish](https://skills.sh/tinyfish-io/tinyfish-cookbook/use-tinyfish)  
**Discord**: [discord.gg/tinyfish](https://discord.gg/tinyfish)
