---
title: "BrowserAct：专为 AI Agent 设计的浏览器层，突破封锁、自动解 CAPTCHA"
titleEn: "BrowserAct: The Browser Layer Built for AI Agents — Break Blocks, Solve CAPTCHAs"
description: "AI Agent 最难跨过的墙不是 LLM，而是网站的反爬机制。BrowserAct 是专为 Agent 设计的浏览器自动化 CLI，3,500+ GitHub Stars，支持 Claude Code/Codex/Cursor/OpenClaw，内置 CAPTCHA 自动解除、真实 Chrome 会话复用、并发多账号隔离、人类接管兜底，已自动化 5 亿+页面。"
descriptionEn: "The hardest wall for AI agents isn't the LLM — it's anti-bot detection. BrowserAct is a browser CLI built specifically for agents: 3,500+ stars, supports Claude Code/Codex/Cursor, auto-solves CAPTCHAs, reuses real Chrome sessions, runs parallel isolated accounts, and hands off to a human when automation gets stuck. 500M+ pages automated."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Tech-News"
tags: ["AI Agent", "浏览器自动化", "爬虫", "开源", "Claude Code", "CAPTCHA", "web scraping", "工具"]
heroImage: "../../assets/images/browseract-ai-agent-browser-automation-guide-banner.jpg"
---

> **GitHub**: [browser-act/skills](https://github.com/browser-act/skills) · ⭐ 3,509 · Python  
> **官网**: [browseract.ai](https://browseract.ai) · **文档**: [docs.browseract.com](https://docs.browseract.com/agent-cli/)  
> **G2**: 4.8 ⭐ · **AppSumo**: 4.4 ⭐ · **合作伙伴**: AWS / Azure / Google Cloud / 阿里云 / 华为云 / 百度 AI

---

## AI Agent 的致命瓶颈：它不是 LLM

你给 AI Agent 一个任务：「抓取亚马逊电子产品畅销榜 Top 80，导出 CSV。」

10 秒后，Agent 报错：
- `HTTP 403: Access Denied`
- `CAPTCHA verification required`
- `Bot detected by Cloudflare`

这不是 LLM 能力的问题。这是**浏览器层**的问题。

**BrowserAct** 就是为了填这个坑而生的：给 AI Agent 一个能真正穿透现代网站防护的浏览器层。

---

## BrowserAct 是什么？

一句话：**专为 AI Agent 设计的浏览器自动化 CLI**。

普通爬虫用 HTTP 请求模拟浏览器，现代网站一眼就识破。BrowserAct 用**真实 Chrome**——不是 headless 的假装，是带完整指纹、登录态、扩展的真浏览器——让网站以为是真人在操作。

核心数据：
- **500M+** 页面已自动化
- **10M+** CAPTCHA 已自动解除
- **3K+** skills 已生成
- **10K+** 并发会话支持

---

## 三种接入方式

### 方式一：Agent CLI（推荐，最简单）

在你的 AI Agent（Claude Code / Codex / Cursor / OpenClaw 等）里直接安装 browser-act skill：

```bash
# Claude Code / Codex / 任何支持 skill 的 Agent 里
# 安装 browser-act skill
npx browser-act install

# 或让 Claude Code 自动处理
```

安装后，直接给 Agent 发指令，它会自动调用 browser-act：

```
抓取 amazon.com/gp/bestsellers/electronics 的 Top 80 产品，
价格、排名、评论数，导出 bestsellers.csv
```

Agent 的操作日志（Claude Code 真实示例）：

```
⏺ Installing skill (browser-act@1.3)…       ✓
⏺ Launching browser (stealth mode)…          ✓
⏺ Visiting amazon.com/gp/bestsellers/…       ✓
⏺ CAPTCHA detected — auto-solving…           ✓
⏺ Scraping listings (80 items)…              ✓
⏺ Exported → ./bestsellers.csv               ✓

80 products · 2m 14s
```

### 方式二：Cloud Workflow（可视化，无代码）

在 browseract.ai 的工作流画布上用自然语言描述步骤：

```
Step 1: Visit URL → https://news.google.com/
Step 2: Click Button → "Top Stories"  
Step 3: Extract Data → news rows, title, source
```

描述好后点运行，云端的真实浏览器执行并返回结构化数据。

### 方式三：API / MCP

```python
# 通过 API 触发浏览器任务
import requests

response = requests.post("https://api.browseract.com/v1/run", 
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={
        "url": "https://target-site.com",
        "task": "Extract all product names and prices"
    }
)

data = response.json()
```

也支持 MCP 直接接入 Agent 框架，以及通过 Make / n8n / Zapier 集成进自动化流程。

---

## 核心能力详解

### 1. 突破反爬机制

BrowserAct 支持多种浏览器模式：

| 模式 | 说明 | 适用场景 |
|---|---|---|
| `chrome` | 标准 Chrome | 普通网站 |
| `chrome-direct` | 直连，跳过代理 | 低防护网站 |
| `stealth-privacy` | 随机指纹 + 隐私保护 | Cloudflare / 反爬 |
| `stealth-fixed` | 固定身份 + 隐私保护 | 需要登录态的持久会话 |

对付 Cloudflare / hCaptcha / reCAPTCHA 这类主流防护，BrowserAct 内置自动解除，不需要人工干预，不需要第三方打码平台。

### 2. 真实 Chrome 会话复用

这是用户反复提到的杀手功能：

> "Real Chrome session reuse is the feature I didn't know I needed until right now" — @charliejhills

你在 Chrome 里已经登录的账号（邮箱、LinkedIn、电商后台……），BrowserAct 可以**直接复用这个 session**，不需要重新登录，不触发二次验证。

```bash
# 连接本地 Chrome 已登录的 LinkedIn 会话
browser-act connect --mode chrome --reuse-session
# → LinkedIn profile 数据直接可抓，无需 API、无需重登
```

### 3. Remote Assist（人类接管兜底）

自动化遇到真正绕不过去的步骤（比如短信验证码、公司 SSO、复杂的人机判断）：

1. BrowserAct 暂停，向你发送一个远程控制链接
2. 你在手机 / 任意设备上打开链接，完成那个步骤
3. BrowserAct 自动恢复继续运行

这解决了自动化的"最后一公里"问题——不是所有步骤都需要自动化，关键是不能因为一个步骤卡死整个流程。

### 4. 并发 + 多账号隔离

```bash
# 并发 5 个独立会话，账号互不干扰
browser-act run --concurrency 5 --isolated-sessions

# 每个 session 有独立的 Cookie、localStorage、指纹
# 多账号操作不会串味
```

用户评价：
> "Concurrency got much easier. 1000x easier and I was able to run multiple concurrent extractions at once." — AppSumo

### 5. Skill Forge（一次探索，永久复用）

把一次手工完成的网站操作录制成可复用的 skill：

1. 你（或 Agent）在某个网站完成一次完整的抓取流程
2. Skill Forge 把这个流程打包成 Python skill
3. 之后任何 Agent 都可以直接调用这个 skill，不需要重新摸索

目前已有 3,000+ 社区 skills 可以直接用（SkillHub）。

---

## 支持的 Agent 环境

| Agent | 支持状态 |
|---|---|
| Claude Code | ✅ 原生支持 |
| OpenAI Codex | ✅ 原生支持 |
| Cursor | ✅ 原生支持 |
| OpenClaw | ✅ 原生支持 |
| Hermes Agent | ✅ 原生支持 |
| Gemini CLI | ✅ 原生支持 |
| 任意能运行 shell 命令的 Agent | ✅ 通用 |

**操作系统**：Windows / macOS / Linux 全支持。

---

## 实际使用场景

### AI 数据采集 Pipeline

```
Agent 每日任务：
→ BrowserAct 抓取竞品价格（绕过反爬）
→ 清洗结构化数据
→ 存入数据库
→ 生成对比报告
```

### 多平台社交媒体自动化

```
→ 复用已登录的小红书/LinkedIn session
→ 批量评论、点赞、关注（注意平台风控）
→ 抓取互动数据
```

### 自动化测试 + 监控

```
→ 定时抓取关键页面
→ 对比前后差异
→ 异常时 Remote Assist 通知人工介入
```

### 企业数据工程

```
→ 抓取没有 API 的内部系统（ERP/旧系统）
→ 多账号并发，隔离运行
→ 结构化输出给 Agent 进行后续处理
```

---

## 定价

- **7 天免费试用**（无需信用卡）
- 加入 Discord 可获得 **100 credits**（免费）
- 有订阅计划后试用期内有额外 credits

完整定价见 [browseract.ai/pricing](https://browseract.ai/pricing)。

---

## 30 秒快速开始

```bash
# 1. 在你的 Agent 里安装 skill（以 Claude Code 为例）
# 直接告诉 Claude：
"安装 browser-act skill，然后帮我抓取 [目标URL] 的数据"

# Claude 会自动执行：
# ⏺ Installing skill (browser-act@latest)…
# ⏺ Launching browser…
# ⏺ Scraping…
# ⏺ Done → 数据返回

# 2. 或者手动安装 CLI
npm install -g browser-act
browser-act --help
```

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/browser-act/skills |
| 官网 | https://browseract.ai |
| 文档 | https://docs.browseract.com/agent-cli/ |
| SkillHub（社区 skills） | https://skills.browseract.com/ |
| Discord（+100 credits） | https://discord.gg/UpnCKd7GaU |
| AppSumo 页面 | https://appsumo.com/products/browseract/ |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: BrowserAct (3,509 ⭐, Python) is a browser CLI purpose-built for AI agents. It runs real Chrome (not headless impersonation), auto-solves CAPTCHAs, reuses logged-in sessions, isolates concurrent multi-account runs, and hands off to a human via Remote Assist when automation gets stuck. Works with Claude Code, Codex, Cursor, OpenClaw, Hermes, Gemini CLI, and any shell-capable agent. 500M+ pages automated, 10M+ CAPTCHAs solved.

---

## The Real Bottleneck for AI Agents

Give an AI agent a scraping task and it hits the same wall: `403 Forbidden`, Cloudflare challenge, CAPTCHA. This isn't a model problem. It's a browser layer problem.

Standard headless browsers are fingerprinted and blocked immediately. BrowserAct uses a real Chrome with real identity — full fingerprint, logged-in sessions, extensions — so websites see a human.

## Three Ways to Use It

**Agent CLI** (simplest): install the `browser-act` skill inside Claude Code, Codex, or any shell-capable agent. Then just describe the task in natural language — the agent installs the skill, launches the browser, handles CAPTCHAs, and returns clean data.

**Cloud Workflow**: visual no-code canvas on browseract.ai. Describe steps (visit URL, click button, extract data) in plain English; a cloud real browser executes them.

**API / MCP**: call `api.browseract.com` to trigger browser tasks from your own stack, or use MCP to connect agents directly. Make / n8n / Zapier integrations available.

## Core Capabilities

| Feature | What it does |
|---|---|
| Auto CAPTCHA solving | Cloudflare, hCaptcha, reCAPTCHA — automatic, no third-party service |
| Real Chrome session reuse | Connect to your already-logged-in local Chrome, no re-auth |
| Remote Assist | Pause automation → human completes 2FA on any device → resume |
| Stealth modes | stealth-privacy (random fingerprint) / stealth-fixed (persistent identity) |
| Concurrent isolation | N parallel sessions, each with independent cookies + fingerprint |
| Skill Forge | Record one-time site exploration → reusable Python skill |

## Works With

Claude Code, Codex, Cursor, OpenClaw, Hermes, Gemini CLI, and any agent that can run shell commands. Windows / macOS / Linux.

## Get Started

```bash
# In Claude Code or any agent — just tell it:
"Install browser-act skill and scrape [TARGET URL]"
# The agent handles install, launch, CAPTCHA, and returns clean data
```

Or join Discord for 100 free credits: [discord.gg/UpnCKd7GaU](https://discord.gg/UpnCKd7GaU)

**Links**: [GitHub](https://github.com/browser-act/skills) · [Docs](https://docs.browseract.com/agent-cli/) · [browseract.ai](https://browseract.ai)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
