---
title: "RepoCourier：7个频道、24个信息源，一条命令跑出你的每日技术情报"
titleEn: "RepoCourier: 7 Channels, 24 Sources — One Command for Your Daily Tech Intelligence"
description: "RepoCourier 是一个本地运行的每日技术情报工具，从 GitHub Trending、科技新闻、大厂博客、学术论文、产品更新、安全资讯和微信公众号聚合内容，用关键词个性化筛选，没有 AI Key 也能跑，输出 Markdown/HTML/JSON，可推送到飞书、企微、个人微信、QQ。"
descriptionEn: "RepoCourier is a local daily tech intelligence tool that aggregates from GitHub Trending, tech news, big company blogs, academic papers, product updates, security news, and WeChat public accounts. Personalizes by keyword, runs without an AI key, outputs Markdown/HTML/JSON, and pushes to Feishu, WeCom, WeChat, and QQ."
pubDate: "2026-07-17"
updatedDate: "2026-07-17"
category: "Tech-Experiment"
tags: ["开源", "技术情报", "GitHub", "自动化", "RSS", "Python", "信息聚合"]
heroImage: "../../assets/images/repo-courier-daily-tech-intelligence-banner.jpg"
---

> **GitHub**：[jjyaoao/repo-courier](https://github.com/jjyaoao/repo-courier) · MIT  
> **技术栈**：Python 3.10+ · uv · OpenAI-compatible API

---

## 它在解决什么问题

每天技术信息过载是一个真实的问题。GitHub Trending 有好东西但要自己去翻，arxiv 新论文太多不知道哪篇值得看，微信公众号推送的有用有没用，安全资讯不看又怕漏。

大多数人的解法是订阅 RSS 阅读器——但阅读器不做个性化筛选，还是要自己花时间过滤。

RepoCourier 的思路是：**先聚合，再用你自己的关键词去噪，每个频道只保留最值得打开的几条，然后自动推送到你习惯的工具。**

---

## 7 个情报频道

| 频道 | 默认信息源 | 筛选逻辑 |
|---|---|---|
| 🔥 **GitHub Trending** | GitHub Trending 页面 + 仓库元数据 | 关注词 + Star 增长 + Trending 排名 |
| 📰 **科技新闻** | MIT Tech Review、The Verge、WIRED、Ars Technica | 新闻价值、相关性、时效性 |
| 🏢 **大厂博客** | OpenAI、Google DeepMind、Google AI、Hugging Face | 技术贡献、工程实践、影响范围 |
| 🎓 **学术论文** | arXiv AI/NLP/CV/ML | 研究相关性与方法创新性 |
| 🚀 **产品更新** | Gemini CLI、OpenAI Codex、Claude Code、OpenClaw | 功能变化、兼容性、实用影响 |
| 🛡️ **安全资讯** | Krebs on Security、The Hacker News、Google Security、安全客 | 风险等级、受影响范围 |
| 💬 **微信公众号** | 机器之心、量子位、新智元、阿里云、腾讯云、Datawhale | 关注词 + 信息密度 + 技术深度 |

所有信息源都在 `config/config.yaml` 里——不写死在代码里，可以自由增删 RSS/Atom Feed，也可以添加全新频道。

---

## 个性化：关键词决定你看什么

核心配置只有三行：

```yaml
# config/config.yaml
profile:
  interests: [agent, llm, mcp, ai]
  exclude_keywords: [awesome list, interview, tutorial collection]
  daily_picks: 3
```

- `interests`：关注的技术方向，用于在每个频道内候选排序
- `exclude_keywords`：屏蔽不想看的内容类型
- `daily_picks`：每个频道最多保留几条

临时覆盖也很方便：

```bash
export REPO_COURIER_INTERESTS="rust,database,self-hosted,security"
uv run repo-courier --channels all --dry-run
```

不同的关注方向配置，得到的是完全不同的情报报告。

---

## 没有 AI Key 也能运行

这是 RepoCourier 的一个实用设计：**AI 分析是可选的，不是必须的。**

- 未配置 AI Key → 使用本地关键词规则摘要和排序，报告正常生成
- 配置 AI Key → 各频道候选内容会通过 AI 分析相关性和创新性，结果更准确

AI 配置走 OpenAI Chat Completions 兼容接口，支持几乎所有主流模型：

```bash
export REPO_LLM_API_KEY="your-key"
export REPO_LLM_BASE_URL="https://api.openai.com/v1/chat/completions"
export REPO_LLM_MODEL="claude-sonnet-4-6"
```

预设了 OpenAI、Claude、智谱 GLM、Kimi、MiniMax、阶跃星辰的端点，Web Beta 里直接下拉选。

---

## 输出与推送

每次运行输出三个格式：

```
reports/YYYY-MM-DD/daily.md     # 可直接阅读的报告
reports/YYYY-MM-DD/daily.html   # 浏览器渲染版本
reports/YYYY-MM-DD/daily.json   # 机器处理用
```

支持的推送目标：

| 平台 | 配置方式 |
|---|---|
| **飞书群机器人** | `FEISHU_WEBHOOK` |
| **企业微信群机器人** | `WECOM_WEBHOOK` |
| **个人微信（Server酱）** | `SERVERCHAN_SENDKEY` |
| **QQ（OneBot）** | `ONEBOT_URL` + `ONEBOT_USER_ID` |

`--dry-run` 参数只生成报告，不触发任何推送，适合调试和预览。

---

## 5 分钟跑起来

```bash
git clone https://github.com/jjyaoao/repo-courier.git
cd repo-courier
uv sync

# 预览模式（不推送）
uv run repo-courier --channels all --dry-run

# 只看 GitHub + 安全资讯
uv run repo-courier --channels github,security --dry-run

# 指定日期（RSS 频道）
uv run repo-courier --channels news,blogs --date 2026-07-16 --dry-run
```

GitHub 频道获取实时 Daily Trending，RSS 频道检索北京时间当天内容。

---

## Web Beta：浏览器里按需生成

不想跑 CLI？Web Beta 提供了一个最简页面：

```bash
uv sync --extra web
uv run repo-courier-web
# 打开 http://127.0.0.1:8000
```

- 多选频道，每个频道最多精选 3 条
- 流式响应，哪个频道先完成先显示
- 页面里填写 API Key，刷新即清除，不持久化
- 公共 Web 实例只生成预览，不代替用户发消息

---

## GitHub Actions：每天自动跑

仓库内置了 Daily Workflow，fork 后在 Actions Secrets 里填几个变量就能每天自动生成并推送：

```yaml
# .github/workflows/daily.yml — 已内置，开箱即用
# 只需设置对应的 Secrets：
GITHUB_TOKEN          # 提高 API 限额
WECHAT_AUTH_KEY       # 微信公众号数据
REPO_LLM_API_KEY      # AI 分析（可选）
FEISHU_WEBHOOK        # 推送目标（任选其一或多个）
WECOM_WEBHOOK
SERVERCHAN_SENDKEY
```

---

## 项目结构一览

```
src/repo_courier/
├── trending.py       # GitHub Trending 抓取
├── github.py         # 仓库元数据与 README
├── feeds.py          # RSS / Atom 抓取、分析、排序
├── wechat.py         # 微信公众号文章
├── prompts/          # 各频道 AI 分析提示词
├── personalize.py    # GitHub 个性化排序
├── report.py         # Markdown / HTML / JSON 输出
├── pushers/          # 飞书、企微、Server酱、OneBot
├── web.py            # Web Beta API
└── runner.py         # 全流程编排
```

整体设计是"频道插件化"——每个频道独立模块，某个信息源失败不影响其他频道，AI 失败自动回退到关键词规则。

---

## 适合谁

- **独立开发者**：每天花 10 分钟过技术资讯，想要一个比 RSS 阅读器更聚焦的工具
- **技术团队**：推送到飞书/企微群，全团队共享一份过滤后的每日情报
- **安全从业者**：专门跑安全频道，监控 Krebs / The Hacker News / 安全客
- **研究者**：学术论文频道 + arXiv，按关键词每天推一批相关论文摘要

---

## 一句话总结

RepoCourier 做的事情很清楚：**把 7 个技术信息渠道的内容，经过你的关键词过滤后，每天自动送到你的消息工具。** 没有大模型也能用，有大模型结果更准。MIT 开源，开箱即用。

© 2026 Author: Mycelium Protocol

<!--EN-->

## RepoCourier: 7 Channels, 24 Sources — One Command for Your Daily Tech Intelligence

**GitHub**: [jjyaoao/repo-courier](https://github.com/jjyaoao/repo-courier) · MIT  
**Stack**: Python 3.10+ · uv · OpenAI-compatible API

### What It Solves

Tech information overload is real. GitHub Trending needs manual browsing, arXiv papers are too many to filter, WeChat push notifications are hit-or-miss, security news is easy to miss. Most RSS readers don't personalize — you still do all the filtering yourself.

RepoCourier's approach: **aggregate first, then filter with your keywords, keep only the top picks per channel, then auto-push to your preferred messaging tool.**

### 7 Intelligence Channels

| Channel | Default Sources | Selection Logic |
|---|---|---|
| GitHub Trending | GitHub Trending, repo metadata | Keywords + star growth + trending rank |
| Tech News | MIT Tech Review, The Verge, WIRED, Ars Technica | News value, relevance, recency |
| Big Company Blogs | OpenAI, Google DeepMind, Google AI, HuggingFace | Technical contribution, engineering practice |
| Academic Papers | arXiv AI/NLP/CV/ML | Research relevance, method novelty |
| Product Updates | Gemini CLI, OpenAI Codex, Claude Code, OpenClaw | Feature changes, compatibility, practical impact |
| Security News | Krebs, The Hacker News, Google Security, 安全客 | Risk level, affected scope |
| WeChat Public Accounts | 机器之心, 量子位, 新智元, 阿里云, 腾讯云, Datawhale | Keywords + information density |

All sources live in `config/config.yaml` — not hardcoded. Add/remove RSS/Atom feeds, add new channels.

### Personalization

```yaml
profile:
  interests: [agent, llm, mcp, ai]
  exclude_keywords: [awesome list, interview, tutorial collection]
  daily_picks: 3
```

Override on the fly:
```bash
export REPO_COURIER_INTERESTS="rust,database,self-hosted,security"
uv run repo-courier --channels all --dry-run
```

### No AI Key Required

AI analysis is optional — not a prerequisite. Without a key, the tool uses transparent local keyword rules for summarization and ranking. With a key, it runs relevance and novelty analysis through your chosen model.

OpenAI-compatible — works with Claude, GLM, Kimi, MiniMax, or any Chat Completions API.

### Output and Push Targets

Generates: `daily.md` / `daily.html` / `daily.json`

Push targets: Feishu webhook, WeCom webhook, WeChat (Server酱), QQ (OneBot).

`--dry-run` generates reports without sending anything.

### Quick Start

```bash
git clone https://github.com/jjyaoao/repo-courier.git
cd repo-courier && uv sync
uv run repo-courier --channels all --dry-run
```

### GitHub Actions Daily Auto-Run

Fork → set Secrets → runs daily automatically. Built-in workflow file included.

### Bottom Line

RepoCourier delivers a filtered daily intelligence brief from 7 tech channels to your messaging tool. Works without AI, works better with it. MIT licensed. Fork and configure in under 10 minutes.

© 2026 Author: Mycelium Protocol
