---
title: "Growth Lab：用 Claude Code 或 Codex 跑完整增长闭环，小红书单篇 4000+ 赞"
titleEn: "growth-lab-tsingyuai-claude-code-codex-end-to-end-growth-agent"
description: "tsingyuai/growth-lab 以 Claude Code 或 Codex 为 Runtime，把从理解产品到执行分发再到结果复盘的完整增长闭环变成 Agent 工作流。已实现 SEO 页面增长（点击量 +1000%）和小红书爆款复刻（单篇 4000+ 赞）两个完整闭环。434 stars，Apache-2.0。"
descriptionEn: "tsingyuai/growth-lab uses Claude Code or Codex as the runtime to turn the full growth loop — from understanding the product to executing and reviewing results — into an agent workflow. Two complete loops implemented: SEO page growth (+1000% clicks) and XiaoHongShu viral replication (4000+ likes per post). 434 stars, Apache-2.0."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["增长工具", "Claude Code", "Codex", "SEO", "小红书", "Agent工作流", "开源", "Mycelium"]
heroImage: "../../assets/images/growth-lab-tsingyuai-claude-code-codex-end-to-end-growth-agent-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 AI 增长工具只解决局部问题：有的只生成文案，有的只研究竞品，有的只发布，有的只看数据。产品上下文在不同工具之间反复丢失，真正重要的决策仍然散落在仪表盘、文档、Prompt 和人工交接里。

**[Growth Lab](https://github.com/tsingyuai/growth-lab)**（tsingyuai）把增长闭环变成了一个 Coding Agent 工作流——以 Claude Code 或 Codex 为 Runtime，把理解产品、研究市场、执行内容、收集结果、调整策略这整条链放进同一个工作区。434 stars，Apache-2.0，两周前刚开源。

---

## 核心闭环

Growth Lab 的设计围绕一个持续的学习闭环：

```
理解产品
→ 判断用户与市场
→ 研究渠道与内容
→ 制定策略
→ 生成与分发
→ 收集真实结果
→ 学习并调整下一步行动
```

这个闭环不是一次性的——每个 Model 都是一个独立的「观察—行动—复盘」单元，有自己的持久化 Memory，积累按时间采集的运营数据、分析结果、行动记录和下一步建议。下一轮工作在开始前读取这些 Memory，保证每次迭代都站在前一次的结果上。

---

## 产品模型

```
会话         = 控制面（你说话的地方）
Codex / Claude Code = Runtime（执行一切的 Agent）
Skill        = 增长方法与工作指引（告诉 Runtime 怎么做）
Client       = 外部执行能力（浏览器、API、内容平台）
文件系统     = 长期 Memory（产品上下文、数据、决策、产物）
```

三个系统组件：

- **Collector**：面向需求、竞品、内容与产品增长数据的采集器
- **Model Skill**：协调闭环与持久化 Memory 的核心方法层
- **Executor Skill**：负责创作、发布、人类协作与结果复盘

---

## 现有两个完整闭环

### 1. SEO 页面增长闭环

**做什么**：分析用户在什么场景下会需要这个产品，调研这些场景里用户实际会搜索什么，生成有信息量、能解决问题、同时引流到产品的 SEO 页面。

**实测结果**（真实数据）：
- 新页面执行后 **1–2 天被搜索引擎收录**
- 按 7 日平均口径：整体 CTR 降低 50%（新页面进入，稀释了高 CTR 旧页面的权重比例）
- 页面曝光量和点击量均提高 **1000%**

### 2. 小红书爆款复刻与复盘闭环

**做什么**：采集高表现内容 → 选择可迁移结构 → 创作 → 降 AI 味处理 → 截图 → 生图 → 卡片渲染 → 合规检查 → 真实发布（人工边界）→ 结果复盘。

**实测结果**（单篇最高）：
- **4000+ 赞/收藏**
- **700+ 评论**

发布仍保持人工边界——Agent 准备好内容，最后由人决定是否发出。

---

## 用法：自然语言驱动

不需要学新命令或配置界面。用 Claude Code 或 Codex 打开工作目录，然后直接说：

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
# 用 Codex 或 Claude Code 打开目录
```

然后在对话里：

```
你能做什么？

理解这个产品，并运行它的第一个增长闭环。

采集小红书上与这个产品相关的高表现内容，选择可迁移的结构，完成一篇图文稿和配图。

复盘最近的结果，然后执行下一步增长行动。
```

**接入自己的产品**：直接用自然语言告诉 AI 你的产品仓库链接，或者现有资料放在哪里。AI 先读取能确认的产品事实，未被证据支持的假设保留为「待验证项」，在后续闭环里逐步验证。

**配置检查**：

```
检查 Growth Lab 现在还缺哪些配置。
帮我配置小红书采集和生图；SEO 相关能力暂时跳过。
```

onboarding Skill 会检查 API key、第三方 Client、外部仓库、浏览器与登录态，解释每个缺失配置从哪里获取，再让你决定现在配还是绕过。小红书用 `xiaohongshu-mcp`（本机浏览器），AI 生图用 OpenAI 或 Gemini 凭据。

---

## 数据主权设计

Growth Lab 完全开源，产品资料、运营数据、Memory 和生成产物都保存在**用户自己的工作区文件系统**里。它不持有用户数据，不依赖云端存储，没有私有格式制造迁移壁垒。密钥、cookie 和认证 profile 不进入 Memory。

---

## 为什么值得关注

**增长工作一直有一个工程化难题**：信息在报表里，方法在专家脑子里，执行在各种零散工具里，三者永远对不齐。Growth Lab 的解法是把 Coding Agent 的能力（读代码、搜网络、操作工具、跨上下文推理）组织成增长方法论，用文件系统做持久 Memory，用自然语言做控制界面。

SEO 闭环（+1000% 曝光）和小红书闭环（4000+ 赞）这两个实测结果不是演示数据——是作者在自己产品上真实跑出来的，用作下一轮迭代的基准。

Topics 里有 `claude-code`、`codex`、`xiaohongshu`、`seo`——这个方向本质上是「Coding Agent 从写代码延伸到做增长」的一次具体实现。

434 stars，刚开源两周，Apache-2.0 可商用。

仓库：[github.com/tsingyuai/growth-lab](https://github.com/tsingyuai/growth-lab) · 主页：[growthlab.tsingyuai.com](https://growthlab.tsingyuai.com)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Growth Lab: Run a Full Growth Loop with Claude Code or Codex — 4000+ Likes on a Single XiaoHongShu Post

*by Mycelium Protocol*

Most AI growth tools solve one piece of the problem: some generate copy, some research competitors, some handle publishing, some display metrics. Product context gets lost between tools, and the decisions that actually matter remain scattered across dashboards, documents, prompts, and handoffs.

**[Growth Lab](https://github.com/tsingyuai/growth-lab)** (tsingyuai) turns the growth loop into a Coding Agent workflow — using Claude Code or Codex as the runtime to put understanding the product, researching the market, executing content, collecting results, and adjusting strategy into a single workspace. 434 stars, Apache-2.0, open-sourced two weeks ago.

### The Core Loop

```
Understand product
→ Assess users and market
→ Research channels and content
→ Form strategy
→ Generate and distribute
→ Collect real results
→ Learn and adjust next actions
```

This isn't a one-shot pipeline. Each Model is a standalone "observe-act-review" unit with its own persistent Memory that accumulates time-series operational data, analysis, action outcomes, and next-step recommendations. Each new run reads this Memory before starting to observe — so every iteration builds on the last.

### Product Model

```
Session         = control panel (where you talk)
Codex/Claude Code = Runtime (the agent that executes everything)
Skill           = growth methodology and work instructions
Client          = external execution capabilities (browser, APIs, content platforms)
File system     = long-term Memory (product context, data, decisions, artifacts)
```

Three system components:
- **Collector**: data collection for demand, competitors, content, and growth metrics
- **Model Skill**: the core methodology layer coordinating the loop and persistent Memory
- **Executor Skill**: handles creation, publishing, human collaboration, and review

### Two Fully Implemented Growth Loops

**1. SEO Page Growth Loop**

The agent analyzes what scenarios would lead a user to need the product, researches what users actually search in those scenarios, and generates informative SEO pages that solve user problems and drive product traffic.

Real results:
- New pages **indexed in 1–2 days**
- 7-day average: overall CTR down 50% (new pages dilute the ratio of high-CTR older pages)
- Page impressions and clicks both up **1000%**

**2. XiaoHongShu Viral Replication Loop**

Collect high-performing content → select transferable structure → create → reduce AI-tell → screenshot → image generation → card rendering → compliance check → real publish (human boundary) → post-review.

Real results (single-post peak):
- **4000+ likes/favorites**
- **700+ comments**

Publishing keeps a human boundary — the agent prepares the content, a human decides whether to post it.

### Natural Language Control

No new commands to learn:

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
# Open with Codex or Claude Code
```

Then in the conversation:

```
What can you do?

Understand this product and run its first growth loop.

Collect high-performing XiaoHongShu content related to this product, select a transferable structure, and produce a complete post with images.

Review the recent results and execute the next growth action.
```

**Connecting your product**: tell the AI your repo link or where your existing materials are in natural language. The agent reads confirmed product facts first; unverified assumptions about users, problems, and value are flagged as pending validation items and filled in progressively.

**Configuration check**: ask the agent to audit what's missing. One onboarding Skill checks API keys, third-party clients, external repos, browser state, and login status, explains where to get each missing piece, and lets you decide what to configure or skip. XiaoHongShu uses local browser-first `xiaohongshu-mcp`; image generation requires OpenAI or Gemini credentials.

### Data Sovereignty

Fully open-source. Product materials, operational data, Memory, and generated artifacts are stored in the user's own workspace file system. No cloud dependency, no proprietary format lock-in, no credential capture — keys, cookies, and auth profiles never enter Memory.

### Why This Matters

Growth has a persistent engineering problem: information lives in reports, methodology lives in experts' heads, and execution is spread across disconnected tools — never aligned. Growth Lab's approach is to organize Coding Agent capabilities (read repos, search the web, operate tools, reason across context) into growth methodology, use the file system for persistent Memory, and natural language as the control interface.

The SEO (+1000% impressions) and XiaoHongShu (4000+ likes) numbers aren't demo data — they're real results from the author's own product, used as baselines for the next iteration.

Topics include `claude-code`, `codex`, `xiaohongshu`, `seo` — this is essentially "Coding Agent extending from writing code to running growth," as a concrete implementation.

434 stars, two weeks after open-source, Apache-2.0 for commercial use.

Repository: [github.com/tsingyuai/growth-lab](https://github.com/tsingyuai/growth-lab) · Homepage: [growthlab.tsingyuai.com](https://growthlab.tsingyuai.com)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
