---
title: "AnySearch：专为 AI Agent 设计的搜索基础设施，打通金融、法律、学术认证数据源"
titleEn: "AnySearch: Search Infrastructure Built for AI Agents — Unlocking Authenticated Vertical Data Sources"
description: "AnySearch 于 2026 年 5 月 11 日上线，定位 AI 时代搜索基础设施：单一 API 接入 22 个垂直领域、9 种内容类型，覆盖金融终端、法律数据库、学术期刊等需要认证的专业数据源。支持 MCP、Claude Code 集成，20 天内 GitHub 1.9k Star。"
descriptionEn: "AnySearch launched May 11, 2026 as search infrastructure for AI agents: a single API covering 22 verticals and 9 content types, including authenticated sources like financial terminals, legal databases, and academic journals. MCP and Claude Code native. 1.9k GitHub stars in 20 days."
pubDate: "2026-05-31"
updatedDate: "2026-05-31"
category: "Tech-News"
tags: ["AI Agent", "搜索基础设施", "AnySearch", "MCP", "RAG", "垂直数据源", "Claude Code", "企业搜索"]
heroImage: "../../assets/images/anysearch-agent-search-banner.jpg"
---

5 月 11 日，一个叫 AnySearch 的产品悄悄上线了。20 天内拿到 GitHub 1.9k Star，和 Tavily、Exa、Perplexity Sonar 这些赛道上的老玩家说了一句不太一样的话：

> "其他人在争公开网页这块蛋糕，我们做的是那 90% 藏在认证墙后面的数据。"

> 📌 官网：https://www.anysearch.com  
> API 文档：https://www.anysearch.com/docs  
> GitHub：https://github.com/anysearch-ai/anysearch-skill  
> npm：`@unicitylabs/sphere-sdk`（无，参考 API 文档）

## AI Agent 搜索的结构性空白

过去两年，AI 搜索基础设施大爆发——Tavily 做了 Agent RAG 专用搜索，Exa 用语义嵌入理解查询意图，Perplexity Sonar 直接生成答案，Brave 提供独立网页索引。它们有一个共同点：**数据源都是公开网页**。

但 Agent 真正需要的信息大多不在公开网页上：

- 金融分析师需要的是彭博终端、EDGAR 财报数据
- 法律 Agent 需要的是 Westlaw、法律法规数据库
- 医疗 Agent 需要的是 PubMed、临床试验数据
- 安全研究 Agent 需要的是 CVE 数据库、漏洞情报

这些数据都在认证墙后面，任何爬虫都拿不到。AnySearch 要做的就是把这些"认证垂直数据源"统一接入，通过单一 API 暴露给 AI Agent。

## 产品架构：一个端点，22 个垂直

**核心设计**：`POST https://api.anysearch.com/v1/search`

一个请求可以指定垂直领域（`domains`）、内容类型（`content_types`）、时效约束（`freshness`），AnySearch 在后端做智能路由，返回带质量评分的结构化 Markdown——格式直接可注入 LLM 上下文窗口，减少 token 消耗。

**22 个垂直领域**涵盖：通用 Web、代码、科技、时尚、旅行、家居、电商、游戏、影视、音乐、**金融**、**学术**、**法律**、商业、知识产权、**网络安全**、教育、健康、宗教、地理、环境、**能源**。

**9 种内容类型**：Web、News、Code、Doc、Academic、Data、Image、Video、Audio。

中国区和国际区通过 `zone=cn/intl` 参数分路由，满足监管要求。

## 三种集成方式

针对不同使用场景提供了三种接入路径：

| 方式 | 场景 |
|------|------|
| **RESTful API** | 直接编程调用，完整参数控制 |
| **MCP Server** | Claude Desktop、Claude Code、Cursor、Windsurf 原生集成 |
| **Skill 包** | `anysearch-skill` GitHub 仓库，跨平台（Python/Node.js/Shell 自动检测） |

MCP Server 支持 Streamable HTTP、SSE、stdio 三种传输协议，符合 MCP spec 2025-03-26。已上架 skills.sh、ClawHub、SkillHub、Glama 等分发渠道。

免费层给出了 **1000 次/天** 的额度，对个人和小团队够用。

## 隐私设计：零留存执行

AnySearch 在隐私承诺上比较明确：**零日志、零数据留存、零知识凭证**。查询在执行后不保留任何记录，凭证通过零知识方式处理，理论上连 AnySearch 自己也看不到用户查询了什么。

这对企业客户来说是关键——把公司财务数据或法律文件扔给第三方 API 搜索，前提是你要相信这个 API 不会泄露或留存你的数据。

## 和竞品的本质差异

| 产品 | 数据源 | 定位 |
|------|--------|------|
| Tavily | 公开网页 | Agent RAG，简单快速 |
| Exa | 自建网页索引 | 语义搜索，技术文档 |
| Perplexity Sonar | 公开网页+LLM | 对话式搜索答案 |
| Brave Search API | 公开网页（独立索引） | 不依赖 Google |
| **AnySearch** | **公开+认证垂直库** | **覆盖非公开专业数据** |

差异不是"谁的公开网页搜索更准"，而是 AnySearch 进入了一个其他人还没有竞争的市场——**把认证专业数据变成 API**。

## 目前的边界

- **公司透明度低**：创始团队未披露，香港注册，融资背景未公开
- **认证数据来源不透明**："聚合金融终端"是核心卖点，但具体与哪些数据提供商合作未公示
- **无独立第三方 benchmark**：官方自测显示整体准确率 76.4%，尚未进入 AIMultiple 等主流评测
- **定价未公开**：1000次/天免费额度之外的付费方案无价格表
- **上线仅 20 天**：生态和稳定性仍处于验证阶段

## 为什么值得关注

AI Agent 的能力边界最终取决于它能访问什么数据。公开网页是所有人都能爬到的，没有竞争壁垒；认证专业数据是有护城河的——合规许可、数据接口、行业关系，这些都是壁垒。

AnySearch 的赌注是：**当 Agent 真正进入企业工作流，需要查金融数据、法律条文、学术文献的那一天，这套基础设施会成为刚需**。这个逻辑成不成立，6-12 个月后会更清楚。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

On May 11, 2026, a product called AnySearch quietly launched. In 20 days it accumulated 1.9k GitHub stars — and said something different from Tavily, Exa, and Perplexity Sonar:

> "Everyone else is fighting over the public web. We're building access to the 90% locked behind authentication walls."

> 📌 Website: https://www.anysearch.com  
> API docs: https://www.anysearch.com/docs  
> GitHub: https://github.com/anysearch-ai/anysearch-skill

## The Structural Gap in AI Agent Search

The past two years produced an explosion of AI search infrastructure — Tavily for agent RAG, Exa for semantic embedding, Perplexity Sonar for answer synthesis, Brave for an independent web index. They share one thing: **the data source is the public web.**

But the information AI agents actually need is mostly not on the public web:

- Financial analysts need Bloomberg terminals, EDGAR filings
- Legal agents need Westlaw, regulatory databases
- Medical agents need PubMed, clinical trial data
- Security agents need CVE databases, threat intelligence

All of it sits behind authentication walls that no crawler can reach. AnySearch's proposition: aggregate these authenticated vertical sources and expose them through a single API.

## Architecture: One Endpoint, 22 Verticals

**Core design**: `POST https://api.anysearch.com/v1/search`

A single request can specify verticals (`domains`), content types (`content_types`), and freshness constraints. AnySearch handles intelligent routing on the backend and returns structured, quality-scored Markdown — formatted to inject directly into LLM context windows, minimizing token overhead.

**22 verticals**: General, Code, Tech, Fashion, Travel, Home, Ecommerce, Gaming, Film, Music, **Finance**, **Academic**, **Legal**, Business, IP, **Security**, Education, Health, Religion, Geo, Environment, **Energy**.

**9 content types**: Web, News, Code, Doc, Academic, Data, Image, Video, Audio.

`zone=cn/intl` routing separates Chinese domestic and international sources for regulatory compliance.

## Three Integration Paths

| Method | Use Case |
|--------|----------|
| RESTful API | Direct programmatic access, full parameter control |
| MCP Server | Native integration with Claude Desktop, Claude Code, Cursor, Windsurf |
| Skill package | `anysearch-skill` repo, auto-detects Python/Node.js/Shell runtime |

Free tier: **1,000 requests/day**.

## Privacy: Zero Retention

AnySearch claims zero logs, zero data retention, and zero-knowledge credential handling — the service can't see what you queried. For enterprise agents passing financial or legal data through a third-party API, this matters.

## Competitive Positioning

The distinction isn't "who searches public web better" — it's that AnySearch is competing in a market the others haven't entered yet: **turning authenticated professional data into an API**.

Whether enterprise agent adoption reaches the point where financial terminals and legal databases become routine search targets is the bet AnySearch is making. The answer will be clearer in 6-12 months.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
