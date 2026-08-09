---
title: "ego lite：为 Claude Code 设计的并行浏览器，一次 JS 调用完成整个任务"
titleEn: "ego lite: The Browser Built for Claude Code — Parallel Spaces, Code-Based Automation"
description: "ego lite 不是浏览器自动化框架，是一个 Chromium 浏览器，人类和 AI agent 各自在独立 Space 里工作。ego-browser skill 让 Claude Code 用 JS heredoc 一次性完成浏览器任务，比传统 CLI 方式快 2.5 倍，token 大幅减少。1208 stars，MIT，macOS。"
descriptionEn: "ego lite isn't a browser automation framework — it's a full Chromium browser where humans and AI agents each work in isolated Spaces. The ego-browser skill lets Claude Code complete browser tasks in a single JS heredoc, 2.5× faster than CLI-based tools with far fewer tokens. 1208 stars, MIT, macOS."
pubDate: "2026-07-23"
updatedDate: "2026-07-23"
category: "Tech-Experiment"
tags: ["浏览器自动化", "Claude Code", "AI Agent", "ego lite", "开源", "MCP", "Playwright", "工具"]
heroImage: "../../assets/images/ego-lite-claude-code-browser-automation-spaces-banner.jpg"
---

> **仓库**：citrolabs/ego-lite · JavaScript · MIT · 1208 stars  
> **官网**：lite.ego.app  
> **平台**：macOS（Apple Silicon + Intel），Windows/Linux 在 roadmap  
> **skill 版本**：ego-browser 1.2.6（2026-07-20）

---

## 一、问题：现有浏览器自动化工具的三个根本缺陷

Browser-Use、Vercel agent-browser 这类工具的共同模式是：

1. 需要一个**独立的浏览器**来驱动——不是你平时用的那个
2. **登录状态无法继承**——agent 需要重新登录，或者你需要导出 cookies
3. agent 和你的 tab **争抢同一个浏览器**——互相干扰

ChatGPT Atlas、Perplexity Comet 走另一条路：内置专有 agent，**只有自家 agent 能驱动**，Claude Code、Codex、Cursor 用不了。

ego lite 的切入点：**既然问题是「用什么浏览器」，那就做一个新浏览器。**

---

## 二、ego lite 是什么

一个完整的 Chromium 浏览器，从头开始为人类和 AI agent 并行工作设计。

**你的 tab 是你的，agent 的工作在 Space 里。**

Space 是 ego lite 的隔离工作区概念——每个 agent 任务在自己的 Space 里运行，与你的正常浏览完全分开。你可以看到哪些 Space 有 agent 在跑，随时接管或停止。

**登录状态从第一天起就是你的。**

第一次安装时，ego lite 问你要不要从 Chrome 迁移数据。选 yes，你的 cookies、登录状态、扩展、书签全部继承——agent 马上就能用你的 GitHub、Gmail、任何已登录的服务，不需要再配置任何东西。

---

## 三、与 Claude Code 的集成：ego-browser skill

### 安装

```bash
# 方式 1：npx
npx skills add citrolabs/ego-lite

# 方式 2：让 agent 来
Set up ego lite for me: https://github.com/citrolabs/ego-lite
# agent 会读 skills/ego-browser/references/install.md 并自动安装

# 方式 3：直接下载 macOS app（安装时自动注册 ego-browser skill）
```

### 使用

在 Claude Code 里，直接用自然语言：

```
/ego-browser follow @ego_agent on x.com for me
/ego-browser extract all job listings from hacker news who is hiring
/ego-browser fill out this form with my info and submit
```

ego-browser skill 被触发后，agent 会接管并打开一个 Space 完成任务。

---

## 四、核心架构：Code-base vs CLI-base

这是 ego lite 最值得理解的设计决策。

**传统 CLI-base 方式**（browser-use、agent-browser 等）：

```
call "go to page" → look at result → 
call "find element" → look at result → 
call "click button" → look at result → 
call "extract text" → ... 
```

每一步都是一次工具调用，每次都需要等待结果再决定下一步。

**ego-browser 的 Code-base 方式**：

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpaces.useOrCreate('scrape job listings')
await browser.openOrReuseTab('https://news.ycombinator.com/jobs', { wait: true })

const listings = await page.locator('.athing').evaluateAll((nodes) =>
  nodes.map((n) => ({
    title: n.querySelector('.titleline a')?.textContent?.trim(),
    href:  n.querySelector('.titleline a')?.href,
  }))
)
console.log(JSON.stringify(listings, null, 2))
EOF
```

**agent 写一段 JS，一次执行完整任务。** 所有的「打开页面」「找元素」「点击」「等待」「提取」都在同一个 script 里，内部 await 不是工具调用边界。

结果：复杂任务**完成速度提升至 2.5×**，token 消耗大幅减少。

---

## 五、JS API 速查

ego-browser 的 API 跟随 Playwright 命名规范，但封装在更高层：

```javascript
// 任务空间管理
const task = await taskSpaces.useOrCreate('task name')   // 创建或恢复 Space
await taskSpaces.complete(task.id, { keep: false })       // 完成任务

// 页面导航
await browser.openOrReuseTab('https://example.com', { wait: true, timeout: 20000 })

// 元素操作（Playwright 风格）
await page.getByRole('button', { name: /submit/i }).click()
await page.getByLabel('Email').fill('user@example.com')
await page.locator('article').evaluateAll((nodes) => nodes.map(...))

// 等待
await page.waitForURL((url) => url.href !== before, { timeout: 15000 })
await page.waitForResponse((r) => r.url().includes('/api/') && r.ok(), { timeout: 15000 })

// 页面信息
const info = await page.info()     // { url, title, ... }
const snap = await page.snapshot() // semantic HTML snapshot
```

---

## 六、并行：10 个 Space = 10 个并行任务

ego lite 的 Space 支持真正的并行：

```
Claude Code 在 Space 1 里搜集 10 条线索的详情
Claude Code 在 Space 2 里同时跑竞品价格监控
你自己在前台正常浏览
三件事同时进行，互不干扰
```

这不是排队执行，是真正的并行。每个 Space 是独立的，有自己的状态、tab、登录会话。

---

## 七、Page Snapshot 质量

ego lite 号称有「市场上最强的 page snapshot」——基于内核级定制，能正确处理深度嵌套 iframe。

这个细节重要：大量真实网页（后台管理系统、内嵌 iframe 的支付页面、复杂 SPA）依赖 iframe 来隔离内容。传统方式经常在这类页面上「看不见」关键元素，导致 agent 操作失败。ego lite 的 kernel-level 定制在这类场景下更可靠。

---

## 八、对比

| | ego lite | browser-use | agent-browser | ChatGPT Atlas |
|---|:---:|:---:|:---:|:---:|
| 并行多任务 | ✓ | — | — | — |
| 继承 Chrome 数据 | ✓ | — | — | ✓ |
| 用户/Agent 独立工作区 | ✓ | — | — | — |
| Claude Code 可驱动 | ✓ | ✓ | ✓ | — |
| 日常用的浏览器 | ✓ | — | — | ✓ |
| 免费 | ✓ | ✓ | ✓ | — |
| 可复用 skill | ✓ | — | — | — |

---

## 九、判断

ego lite 的核心判断是对的：**浏览器自动化的瓶颈不是 API，是浏览器本身**。

给 agent 一个独立的、继承你登录状态的、基于代码而非 CLI 的浏览器环境，很多问题自然消失——不需要配置 cookie 导出，不需要重新登录，不需要在多次调用里维护中间状态。

Code-base 方案（一次 JS 执行完整任务）比 CLI-base 快 2.5× 这个数字是可信的：CLI 方案的开销主要在模型每次工具调用之间的序列化、传输、上下文重建；code 方案把这些都省掉了，只有一次往返。

目前只支持 macOS 是最大的限制。Windows/Linux 开发团队显示在 roadmap 里，但没有时间线。

---

*数据来源：GitHub citrolabs/ego-lite，lite.ego.app，2026-07-23 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: citrolabs/ego-lite · JavaScript · MIT · 1208 stars  
> **Website**: lite.ego.app  
> **Platform**: macOS (Apple Silicon + Intel), Windows/Linux on roadmap  
> **Skill version**: ego-browser 1.2.6 (2026-07-20)

---

## 1. The Problem: Three Fundamental Flaws in Existing Browser Automation Tools

The common pattern with tools like Browser-Use and Vercel agent-browser is:

1. They need a **separate browser** to drive — not the one you normally use
2. **Login state cannot be inherited** — the agent has to log in again, or you need to export cookies
3. The agent and your tabs **compete for the same browser** — interfering with each other

ChatGPT Atlas and Perplexity Comet take a different approach: built-in proprietary agents, **only their own agents can drive them** — Claude Code, Codex, and Cursor can't use them.

ego lite's entry point: **since the problem is "which browser to use," just build a new browser.**

---

## 2. What ego lite Is

A complete Chromium browser, built from the ground up for humans and AI agents to work in parallel.

**Your tabs are yours; the agent's work happens in Spaces.**

Space is ego lite's isolated workspace concept — each agent task runs in its own Space, completely separate from your normal browsing. You can see which Spaces have agents running, and take over or stop them at any time.

**Your login state is yours from day one.**

On first installation, ego lite asks if you want to migrate data from Chrome. Say yes, and your cookies, login state, extensions, and bookmarks are all inherited — the agent can immediately use your GitHub, Gmail, or any already-logged-in service, with no additional configuration required.

---

## 3. Integration with Claude Code: The ego-browser Skill

### Installation

```bash
# Method 1: npx
npx skills add citrolabs/ego-lite

# Method 2: Let the agent handle it
Set up ego lite for me: https://github.com/citrolabs/ego-lite
# The agent will read skills/ego-browser/references/install.md and install automatically

# Method 3: Download the macOS app directly (ego-browser skill is auto-registered on install)
```

### Usage

In Claude Code, just use natural language:

```
/ego-browser follow @ego_agent on x.com for me
/ego-browser extract all job listings from hacker news who is hiring
/ego-browser fill out this form with my info and submit
```

Once the ego-browser skill is triggered, the agent takes over and opens a Space to complete the task.

---

## 4. Core Architecture: Code-based vs CLI-based

This is the most important design decision in ego lite worth understanding.

**Traditional CLI-based approach** (browser-use, agent-browser, etc.):

```
call "go to page" → look at result → 
call "find element" → look at result → 
call "click button" → look at result → 
call "extract text" → ... 
```

Each step is a separate tool call; you must wait for the result before deciding the next step.

**ego-browser's Code-based approach**:

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpaces.useOrCreate('scrape job listings')
await browser.openOrReuseTab('https://news.ycombinator.com/jobs', { wait: true })

const listings = await page.locator('.athing').evaluateAll((nodes) =>
  nodes.map((n) => ({
    title: n.querySelector('.titleline a')?.textContent?.trim(),
    href:  n.querySelector('.titleline a')?.href,
  }))
)
console.log(JSON.stringify(listings, null, 2))
EOF
```

**The agent writes a JS script and executes the entire task in one shot.** All the "open page," "find element," "click," "wait," and "extract" steps are in the same script; internal awaits are not tool-call boundaries.

Result: complex tasks complete **up to 2.5× faster**, with significantly fewer tokens consumed.

---

## 5. JS API Quick Reference

ego-browser's API follows Playwright naming conventions, but wrapped at a higher level:

```javascript
// Task space management
const task = await taskSpaces.useOrCreate('task name')   // Create or resume a Space
await taskSpaces.complete(task.id, { keep: false })       // Complete the task

// Page navigation
await browser.openOrReuseTab('https://example.com', { wait: true, timeout: 20000 })

// Element interaction (Playwright style)
await page.getByRole('button', { name: /submit/i }).click()
await page.getByLabel('Email').fill('user@example.com')
await page.locator('article').evaluateAll((nodes) => nodes.map(...))

// Waiting
await page.waitForURL((url) => url.href !== before, { timeout: 15000 })
await page.waitForResponse((r) => r.url().includes('/api/') && r.ok(), { timeout: 15000 })

// Page information
const info = await page.info()     // { url, title, ... }
const snap = await page.snapshot() // semantic HTML snapshot
```

---

## 6. Parallelism: 10 Spaces = 10 Parallel Tasks

ego lite's Spaces support true parallelism:

```
Claude Code in Space 1 collecting details for 10 leads
Claude Code in Space 2 simultaneously running competitor price monitoring
You browsing normally in the foreground
Three things happening at once, none interfering with the others
```

This is not queued execution — it is true parallelism. Each Space is independent, with its own state, tabs, and login session.

---

## 7. Page Snapshot Quality

ego lite claims to have "the best page snapshot on the market" — based on kernel-level customization, it correctly handles deeply nested iframes.

This detail matters: a large number of real-world pages (admin dashboards, payment pages with embedded iframes, complex SPAs) rely on iframes to isolate content. Traditional approaches frequently "miss" critical elements on these pages, causing agent operations to fail. ego lite's kernel-level customization is more reliable in these scenarios.

---

## 8. Comparison

| | ego lite | browser-use | agent-browser | ChatGPT Atlas |
|---|:---:|:---:|:---:|:---:|
| Parallel multi-tasking | ✓ | — | — | — |
| Inherits Chrome data | ✓ | — | — | ✓ |
| Independent user/agent workspaces | ✓ | — | — | — |
| Claude Code can drive it | ✓ | ✓ | ✓ | — |
| Usable as a daily browser | ✓ | — | — | ✓ |
| Free | ✓ | ✓ | ✓ | — |
| Reusable skill | ✓ | — | — | — |

---

## 9. Assessment

ego lite's core thesis is correct: **the bottleneck in browser automation is not the API — it's the browser itself.**

Give the agent an isolated browser environment that inherits your login state and operates via code rather than CLI, and many problems simply disappear — no cookie export configuration, no re-logging in, no need to maintain intermediate state across multiple tool calls.

The claim that the code-based approach (executing an entire task in a single JS run) is 2.5× faster than CLI-based is credible: CLI-based overhead comes primarily from serialization, transmission, and context reconstruction between each model tool call; the code-based approach eliminates all of that, leaving only a single round trip.

macOS-only support is currently the biggest limitation. Windows/Linux development is listed on the roadmap, but with no timeline.

---

*Data source: GitHub citrolabs/ego-lite, lite.ego.app, collected 2026-07-23.*

© 2026 Author: Mycelium Protocol
