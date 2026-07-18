---
title: "BrowserAct：给 AI Agent 装上真实浏览器，4500 stars，10M+ CAPTCHA 已解决"
titleEn: "BrowserAct: A Real Browser Layer for AI Agents — 4,500 Stars, 10M+ CAPTCHAs Solved"
description: "BrowserAct 是专门为 AI Agent 构建的浏览器自动化 CLI——让 Claude Code、Cursor、Codex 等任意 Agent 能穿透反爬防护、复用本地 Chrome 登录状态、自动解 CAPTCHA、多账户并发运行，把任意网站变成 Agent 可调用的 API。三种接入方式：Skill CLI / 云端 Workflow / REST API + MCP。G2 4.8 分，AppSumo 4.4 分，AWS 上架。"
descriptionEn: "BrowserAct is a browser automation CLI built for AI agents. It lets Claude Code, Cursor, Codex, and any shell-capable agent break through anti-bot walls, reuse local Chrome sessions, auto-solve CAPTCHAs, and run multi-account work in parallel. Three modes: Skill CLI, Cloud Workflow, REST API + MCP. G2 4.8, AppSumo 4.4, on AWS Marketplace."
pubDate: "2026-07-18"
updatedDate: "2026-07-18"
category: "Tech-Experiment"
tags: ["AI Agent", "浏览器自动化", "Claude Code", "CAPTCHA", "网页抓取", "Agent工具", "MCP", "开源"]
heroImage: "../../assets/images/browseract-ai-agent-browser-automation-guide-banner.jpg"
---

> **GitHub**：[browser-act/skills](https://github.com/browser-act/skills) · ⭐ 4,504  
> **官网**：[browseract.ai](https://browseract.ai/) · G2 4.8 · AppSumo 4.4  
> **规模**：500M+ 页面已自动化 · 10M+ CAPTCHA 已解决 · 3K+ Skills 已生成 · 10K+ 并发会话  
> **合作伙伴**：AWS · Azure · Google Cloud · Alibaba Cloud · Huawei Cloud · BytePlus · Baidu AI Cloud

---

## AI Agent 的浏览器盲区

你的 Agent 很聪明，能推理、能规划、能写代码。但一遇到「去网上查一下这个价格」「登录我的后台导出这份报告」「在这个网站上监控竞品」——它就卡住了。

不是因为它不够聪明，而是因为它**没有浏览器**——或者说，它用的那个「浏览器」不够真实：被 Cloudflare 拦、被 CAPTCHA 挡、登录状态丢失、多任务并发时账户串了。

BrowserAct 要解决的就是这个问题：**为 AI Agent 提供一个真实的、能绕过反爬的、状态可持久化的浏览器层。**

---

## 一句话演示

在 Claude Code 里对话：

```
> Scrape the top 80 Amazon Electronics bestsellers — price, rank, reviews — export a clean CSV.
```

Claude Code 的响应：

```
⏺ Installing skill (browser-act@1.3)…     ✓
⏺ Launching browser (stealth mode)…       ✓  
⏺ Visiting https://www.amazon.com/gp/bestsellers/electronics… ✓
⏺ CAPTCHA detected — auto-solving…        ✓
⏺ Scraping listings (80 items)…           ✓
⏺ Exported → ./bestsellers.csv

80 products · 2m 14s · 0 credits used
```

这就是 BrowserAct 的工作方式：Agent 调用一个 Skill，Skill 驱动真实浏览器，完成任务，返回干净的数据。

---

## 三种接入方式

### 1. Agent CLI Skill — 30 秒上手

直接对着你的 Agent 粘贴安装命令：

```bash
# 无需注册，复制到 Agent 即用
```

安装后，Agent 可以驱动你的**本地 Chrome**，复用已登录的会话状态（cookies、SSO、浏览器扩展）。这是最关键的点：不是启动一个全新的无头浏览器，而是在你已经登录好的真实 Chrome 上直接行动。

支持的 Agent 环境：**Claude Code、Cursor、VS Code、OpenCode、OpenClaw、Codex、Gemini CLI**，以及任何能运行 shell 命令和加载 Skill 的 Agent。

### 2. Cloud Workflow — 可视化 + 无代码

用画布编辑器描述你想要的流程（自然语言），BrowserAct 把它变成可重复运行的自动化工作流：

```
01 Visit URL  →  https://news.google.com/
02 Click Button  →  "Top Stories"
03 Extract Data  →  news rows · title · source
```

适合不想写代码的场景，或者需要把步骤展示给团队的场景。

### 3. API / MCP — 嵌进你的产品栈

通过 REST API 或 MCP 协议触发浏览器任务、运行工作流、把结构化网页数据返回给你的系统。与 Make、n8n、Zapier 直接集成。

---

## 四层技术防线

BrowserAct 之所以能在大多数真实网站上正常工作，靠的是四层堆叠的能力：

### 环境层：像真人一样浏览

- **隐身指纹**（Stealth fingerprints）：每个浏览器会话都有匹配的 UA、Canvas、WebGL、字体指纹
- **TLS 轮换**：TLS 握手特征匹配真实 Chrome
- **住宅代理**（Residential proxies）：出口 IP 是真实住宅宽带，不是机房 IP
- 结果：大多数反机器人检测在触发前就被绕过

### 执行层：自动过 CAPTCHA

`solve-captcha` 自动处理：
- **reCAPTCHA**（Google）
- **Cloudflare Turnstile**
- **DataDome**
- **HUMAN Security**
- 以及更多主流人机验证方案

### 人类层：卡住时叫人来

有些步骤确实无法自动完成（短信 2FA、某些判断题验证码、需要人工审批的操作）。`remote-assist` 会生成一个临时链接，你在手机或电脑上打开，完成那一步，然后控制权自动还给 Agent 继续执行。

这是「Agent + Human in the loop」最干净的实现方式之一。

### 并发层：多账户、多任务不串

每个浏览器会话有独立的身份（fingerprint profile）和独立的 IP 出口，多个 Agent、多个任务、多个账户可以同时运行，互不干扰，不会出现 session 污染。

---

## Skill Forge：把探索变成可复用的技能

这是一个独特功能：你手动浏览一个网站一次，BrowserAct 记录你的操作，然后生成一个**可复用的 Skill**——下次 Agent 可以直接调用这个 Skill，而不是每次从头摸索。

**SkillHub**（skills.browseract.com）是社区 Skill 库，目前已有 3,000+ 个 Skill 可以直接复用。常见场景：LinkedIn 数据提取、电商价格监控、社交媒体多账户管理、SaaS 后台数据导出……

---

## 真实用户说了什么

> "It allows me to turn virtually any website into an API, which has saved me hundreds—if not thousands—of hours."  
> —— braydenmatsko, AppSumo

> "This is the missing layer for AI research workflows. Persistent browser context changes everything."  
> —— asiahussain51, Twitter

> "Real Chrome session reuse is the feature I didn't know I needed until right now."  
> —— charliejhills, Twitter

> "Not having to constantly update selectors when they change and surprisingly not being blocked by bot detectors has saved me a lot."  
> —— darkleech, AppSumo

> "Web scraping was one of the reasons I rented a VPS. But now I'm almost forgetting about it since I discovered BrowserAct."  
> —— st.bellucci3, AppSumo

用户描述的核心价值：**用一个实际的、可登录的、能过反爬的浏览器，把任意网站变成 Agent 可以操作的界面**。

---

## 技术规格速查

| 能力 | 支持 |
|---|---|
| 操作系统 | Windows / macOS / Linux |
| 浏览器模式 | Chrome / chrome-direct / stealth privacy / stealth fixed identity |
| CAPTCHA 类型 | reCAPTCHA · Cloudflare Turnstile · DataDome · HUMAN Security |
| Agent 环境 | Claude Code · Cursor · VS Code · OpenCode · OpenClaw · Codex · Gemini CLI |
| 运行时对象 | browser · session · profile · stealth browser · network capture · HAR · cookies |
| 集成方式 | Agent Skill · REST API · MCP · Make · n8n · Zapier |
| 云合作 | AWS · Azure · Google Cloud · Oracle · Alibaba · Huawei · BytePlus · Baidu |

---

## 和传统爬虫/浏览器自动化的区别

传统方案（Playwright / Selenium / Puppeteer）给的是**工具**——你需要自己写代码控制浏览器、自己处理反爬、自己维护 selector、自己实现并发。

BrowserAct 给的是**能力层**——Agent 用自然语言描述目标，BrowserAct 处理所有底层细节：指纹、代理、CAPTCHA、会话管理、并发隔离。Agent 不需要知道「怎么爬」，只需要知道「要什么」。

这个区别在 AI 时代是根本性的：**Agent 不应该是一个爬虫工程师，它应该是一个会用浏览器的助手。**

---

## 开始使用

```bash
# 方式一：直接对 Agent 说（推荐）
# 把下面这句话粘给 Claude Code / Cursor：
Read https://github.com/browser-act/skills and help me install BrowserAct.

# 方式二：免费试用
# 访问 browseract.ai，7 天免费试用，加入 Discord 获得 100 积分
```

**GitHub**：github.com/browser-act/skills（4,504 stars，212 forks）  
**官网**：browseract.ai · G2 4.8 · AppSumo 4.4 · AWS Marketplace 上线

---

## 一句话总结

BrowserAct 是 AI Agent 的浏览器客户端：真实 Chrome、自动过 CAPTCHA、复用登录会话、多任务并发不串账。把任意网站变成 Agent 可用的工具，30 秒接入 Claude Code/Cursor/Codex。4,500 stars，500M+ 页面已自动化。

© 2026 Author: Mycelium Protocol

<!--EN-->

## BrowserAct: A Real Browser Layer for AI Agents

**GitHub**: [browser-act/skills](https://github.com/browser-act/skills) · ⭐ 4,504  
**Website**: [browseract.ai](https://browseract.ai/) · G2 4.8 · AppSumo 4.4  
**Scale**: 500M+ pages automated · 10M+ CAPTCHAs solved · 3K+ skills generated · 10K+ concurrent sessions

### The Problem

AI agents are blocked on the web. Not because they lack intelligence — but because the browser layer beneath them is either missing or too fragile: detected by anti-bot systems, blocked by CAPTCHAs, losing login state, and leaking sessions when multiple tasks run in parallel.

BrowserAct is a browser automation CLI built specifically for agents. It gives any agent — Claude Code, Cursor, Codex, Gemini CLI — a real, stealthy, session-aware browser.

### Three Ways to Use It

**Agent CLI Skill**: Install the skill once. The agent drives your local Chrome — your logged-in sessions, cookies, SSO, and extensions — and returns structured data. No new browser login required.

**Cloud Workflow**: Visual canvas editor. Describe a workflow in natural language (Visit URL → Click → Extract). Runs on cloud infrastructure.

**API / MCP**: Trigger browser tasks via REST API or MCP protocol. Integrates directly with Make, n8n, Zapier, and any MCP-capable agent host.

### Four Technical Layers

**Environment layer**: Stealth fingerprints (UA, Canvas, WebGL, font), TLS rotation matching real Chrome, residential proxy routing. Most checks don't trigger.

**Execution layer**: Auto-solve reCAPTCHA, Cloudflare Turnstile, DataDome, HUMAN Security.

**Human layer**: `remote-assist` creates a live takeover link for 2FA or judgment-heavy steps. Human completes it; agent continues.

**Concurrency layer**: Each session gets its own fingerprint profile and IP. Multiple agents, tasks, accounts run in parallel without state leaks.

### Skill Forge

Record yourself navigating a site once → BrowserAct generates a reusable Skill. Community SkillHub has 3,000+ ready-to-use skills: LinkedIn scraping, e-commerce monitoring, SaaS data export, multi-account social management.

### Compatibility

| Area | Support |
|---|---|
| Operating systems | Windows, macOS, Linux |
| Agent environments | Claude Code, Cursor, VS Code, OpenCode, OpenClaw, Codex, Gemini CLI |
| CAPTCHA types | reCAPTCHA, Cloudflare Turnstile, DataDome, HUMAN Security |
| Browser modes | Chrome, chrome-direct, stealth privacy, stealth fixed identity |
| Integrations | REST API, MCP, Make, n8n, Zapier |

### Why It Matters

Traditional automation tools (Playwright, Selenium, Puppeteer) give you primitives — you write the scraping logic, handle detection, maintain selectors, manage concurrency. BrowserAct gives agents a capability: describe what you want in natural language, get structured data back.

The shift: agents shouldn't be scraping engineers. They should be assistants that know how to use a browser.

© 2026 Author: Mycelium Protocol
