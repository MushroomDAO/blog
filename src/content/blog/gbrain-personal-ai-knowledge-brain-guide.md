---
title: "GBrain：Y Combinator CEO 开源的个人 AI 大脑——25000 星知识图谱系统完整介绍"
titleEn: "GBrain: YC CEO's Open-Source Personal AI Brain — A Complete Guide to the 25K-Star Knowledge Graph System"
description: "GBrain 是 Y Combinator 总裁 Garry Tan 开源的个人 AI 知识大脑系统，25417★，当前 GitHub Trending 榜单。不同于普通知识库，它有两个核心能力：合成层（给你答案而非返回页面列表）和自动接线知识图谱（无需 LLM 提取实体和关系）。支持本地 PGLite（2秒初始化）或 Postgres+pgvector，通过 MCP 接入 Claude Code / Codex / Cursor，43个内置 Skill，夜间自动梦境循环持续丰富知识库。"
descriptionEn: "GBrain is the open-source personal AI brain system built and used by Garry Tan, President and CEO of Y Combinator (25,417★). Unlike keyword search, it has a synthesis layer that writes you the answer (not a page list), and a self-wiring knowledge graph that extracts entities and edges without LLM calls. Local setup: PGLite in 2 seconds. MCP integration with Claude Code / Codex / Cursor. 43 built-in skills, nightly dream cycle for autonomous enrichment."
pubDate: "2026-07-08"
updatedDate: "2026-07-08"
category: "Tech-Experiment"
tags: ["GBrain", "知识图谱", "个人知识库", "Claude Code", "MCP", "RAG", "Garry Tan", "YCombinator", "本地AI大脑"]
heroImage: "../../assets/images/gbrain-personal-ai-knowledge-brain-guide-banner.jpg"
---

> **仓库**: [garrytan/gbrain](https://github.com/garrytan/gbrain) · 25417★ · TypeScript  
> **作者**: Garry Tan，Y Combinator 总裁 & CEO  
> **30分钟安装，2秒本地初始化**

---

## 它解决什么问题

你在某处读过一篇文章，记得说了某个观点，但想不起来在哪。你上个月见了某人，谈了些什么，但不记得细节。你的想法、会议记录、阅读笔记散落在 Notion、Obsidian、微信、浏览器书签里，没有一个地方可以统一查询。

普通知识管理工具解决的是"找到页面"的问题——给你一个关键词匹配的结果列表，然后你还要自己去读、去综合。

**GBrain 解决的是"得到答案"的问题**。

同样的问题，问一个普通知识库：

```
搜索"Alice 会议"，返回：
1. people/alice
2. meetings/2026-03-15-alice-q1
3. meetings/2026-01-08-acme-kickoff
4. customers/acme
5. notes/2026-04-22

→ 你还要自己打开5个文件去读
```

问 GBrain：

```
"明天见 Alice 之前我需要了解什么？"

→ Alice 是 Acme 的工程主管（Series B 金融科技公司）。
   你们上次在 4月22日有一次简短通话，聊到了定价问题。
   目前有3件未完成的事：
   1. 她欠你新产品层级的安全审查（截止日期5月1日，尚无更新）
   2. 你承诺提供500席定价方案（4月25日已发，但尚无回复）
   3. 她提到要招聘CISO，你说要介绍圈内的人

   注意：自4月22日起已有6周没有关于Alice或Acme的新内容
   进入大脑。可能她通过邮件或Slack DM回复了，那些渠道
   大脑看不到，建议直接问她。
```

每条主张都有来源页面。末尾的"注意"告诉你大脑的盲区，让你不会被意外惊到。

这就是搜索引擎和大脑的区别。搜索引擎找页面，大脑替你读，替你写答案。

---

## 谁在用它

**Garry Tan**，Y Combinator 总裁兼 CEO，是 GBrain 的作者和第一个用户。

他的个人大脑规模：**146,646 页、24,585 个人物、5,339 家公司**，66个定时任务在后台持续运行。他的 AI Agent 在他睡觉时自动摄取会议记录、邮件、推文、通话记录和原始想法，对遇到的每个人和公司做信息丰富，修复引用，整合记忆。

"我醒来比睡前更聪明——你也可以。"

---

## 两个核心能力

### 1. 合成层：给你答案，而非列表

`gbrain search`（原始检索）返回向量+关键词混合搜索的最相关页面列表。  
`gbrain think`（合成层）做同样的检索，但接着把结果综合成带引用的完整答案，并且**显式标注大脑不知道的内容**（gap analysis）。

差距分析是区分其他系统的关键：它不会假装大脑什么都知道。

### 2. 自动接线知识图谱

每次写入一个页面，GBrain 自动从 Markdown 中提取实体引用，创建类型化的关系边——`attended`、`works_at`、`invested_in`、`founded`、`advises`……

**零 LLM 调用**。纯粹的模式匹配，写入即完成。

效果：在 240 页语料上测试，图谱激活模式的 P@5 = 49.1%，比禁用图谱的纯向量 RAG 高出 +31.4 个百分点。

你可以问："Bob 这个季度投资了什么？" "谁在 Acme AI 工作？" 这些问题向量搜索无法回答，因为它们需要关系推理，不只是语义相似度。

---

## 架构简览

```
你的大脑 = git 仓库（Markdown 文件）
           + Postgres（向量+图谱索引）
           + GBrain（检索、合成、技能、定时任务）
           + AI Agent（Claude Code / Codex / Cursor / OpenClaw）
```

**两个存储引擎，一套接口**：
- **PGLite**（默认）：Postgres 17 via WASM，零配置，2秒初始化，适合个人大脑（≤5万页）
- **Postgres + pgvector**（Supabase 或自托管）：适合团队/大规模/多机器部署

**知识仓库**：你的知识以 Markdown 文件存在一个 git 仓库里，GBrain 把它同步进数据库做检索。文件是真实数据，数据库是索引。版本控制、公开子集分享、团队挂载都天然支持。

---

## 快速安装

### 最快路径：Claude Code 本地大脑（2分钟）

```bash
# 安装 GBrain CLI
bun install -g github:garrytan/gbrain

# 初始化本地大脑（PGLite，无需 Docker，2秒）
gbrain init --pglite

# 连接到 Claude Code
claude mcp add gbrain -- gbrain serve

# 验证
gbrain doctor
```

完成。Claude Code 现在有了一个持久记忆层。

### 代理人安装（推荐完整功能）

如果你想要完整功能——43个技能、夜间梦境循环、自动丰富——可以让 AI Agent 帮你安装：

把这段话发给 Claude Code 或 Codex：

```
Retrieve and follow the instructions at:
https://raw.githubusercontent.com/garrytan/gbrain/master/INSTALL_FOR_AGENTS.md
```

Agent 会自动安装 GBrain、创建大脑、询问 API keys、加载 43 个技能、配置梦境循环、端到端验证安装。约 30 分钟，你回答问题，它做事。

### 已有远程大脑（OpenClaw / Hermes 部署）

```bash
# 连接远程大脑到 Claude Code
gbrain connect https://your-host/mcp --token gbrain_xxx --install

# 连接到 Codex
gbrain connect https://your-host/mcp --token gbrain_xxx --agent codex --install
```

---

## 核心操作

### 把内容加入大脑

```bash
# 录入想法
gbrain capture "这个季度要关注的三个趋势：..."

# 导入文件
gbrain capture --file ./notes/meeting-2026-07.md

# 管道输入
echo "从命令行来的笔记" | gbrain capture --stdin

# 批量导入整个目录
gbrain import ~/notes/
```

页面落地在数据库 + 磁盘，默认路径 `inbox/YYYY-MM-DD-<hash8>`。

### 查询大脑

```bash
# 原始检索：返回最相关页面列表（快，无 LLM 成本）
gbrain search "Alice 最近的会议"

# 合成层：返回综合答案 + 引用 + 盲区说明
gbrain think "我明天和 Alice 开会前需要了解什么？"

# 多步骤推理
gbrain think "这家公司的营收趋势和竞争格局变化"
```

### 图谱查询

```bash
# 多跳图谱查询
gbrain graph-query "Bob 投资过的所有公司"
gbrain graph-query "谁参加过 2026 年 Q1 的战略会议"
```

### 大脑健康检查

```bash
gbrain doctor    # 检查索引状态、embedding 维度一致性、图谱健康
gbrain search stats  # 搜索命中统计
```

---

## 夜间梦境循环

这是 GBrain 最有价值的功能之一：它在你睡觉时持续工作。

66个定时任务在 Garry Tan 的大脑里运行，每晚自动：
- 对今天摄取的所有内容提取实体和关系
- 对已有页面做信息丰富（发现新关联、补充背景）
- 修复引用问题（链接失效、引用不一致）
- 发现矛盾（两个页面对同一事实有不同描述）
- 为明天的任务评分优先级
- 整合重复内容（同一个人的多个碎片记录合并）

配置夜间运行：

```bash
# 查看当前 cron 作业
gbrain jobs list

# 手动触发丰富（模拟夜间循环）
gbrain jobs submit enrich-all

# 配置每日凌晨 2 点自动运行
gbrain cron schedule "0 2 * * *" enrich-all
```

---

## Schema 包：大脑的形状

大多数知识管理工具强制你用它们的布局。GBrain 不强迫——它根据你的实际内容推断结构：

```bash
# 分析你的文件系统，提议合适的内容类型
gbrain schema detect

# LLM 精炼提议
gbrain schema suggest

# 人工确认，应用 Schema
gbrain schema review-candidates --apply
```

内置类型包括：`person`（人）、`company`（公司）、`meeting`（会议）、`media`（媒体）、`tweet`（推文）、`analysis`（分析）、`deal`（交易）等 15 种。你也可以定义自己的类型。

---

## 与 Claude Code 协作的最佳姿势

连接 GBrain 后，在你的 `CLAUDE.md` 里加入：

```markdown
## Brain-first Protocol
在回答任何问题或开始任何任务之前，先查询 GBrain：
1. `gbrain think "<相关问题>"` 获取合成答案
2. `gbrain search "<关键词>"` 获取相关页面
3. 如果大脑说信息不足，才去外部搜索

在每次会话结束时，把重要的新信息存入大脑：
`gbrain capture "今天了解到：..."`
```

这样你的 Claude Code 就有了一个持续学习、越用越聪明的记忆层。

---

## 团队大脑（公司 Brain）

GBrain 也支持多人团队使用——每个人看到自己的分片，绝不看到其他人的笔记（作者在 240 页语料上进行了模糊测试，零信息泄漏）。

Garry Tan 在 YC 的 Request for Startups 里把这个模式叫做 "company brain"——这是 GBrain 已经实现的原型。

```bash
# 以 HTTP 模式启动（支持 OAuth 2.1，适合团队）
gbrain serve --http

# 团队成员连接
gbrain connect https://your-brain-server/mcp --token <个人 token> --install
```

---

## 支持的 MCP 客户端

| 客户端 | 接入方式 |
|--------|---------|
| **Claude Code** | `claude mcp add gbrain -- gbrain serve`（本地）或 `gbrain connect <url>` |
| **Codex** | `gbrain connect <url> --agent codex --install` |
| **Cursor / Windsurf** | 添加 `{"command": "gbrain", "args": ["serve"]}` 到 MCP 配置 |
| **Claude Desktop** | Settings → Integrations → 添加 HTTP server URL |
| **Perplexity** | `gbrain connect <url> --agent perplexity --oauth --register` |
| **ChatGPT** | OAuth 2.1 + PKCE，从 admin dashboard 注册 `chatgpt` 客户端 |

---

## 总结

GBrain 是目前开源世界里最接近"真正的个人 AI 大脑"的系统。它不是又一个笔记应用，也不是又一个 RAG 框架——它是一个持续运行、自我丰富、能回答问题（而不只是返回搜索结果）的知识智能体。

25000 星的背后是 Garry Tan 两年多亲自用、亲自维护的工程沉淀。你看到的每一个功能都经过他的真实 14 万页大脑的验证。

**给想开始的人**：从 `gbrain init --pglite` 开始，把它接到 Claude Code。用两周时间养成 `gbrain capture` 的习惯——每次有值得记住的想法，一句话录进去。两周后你会有一个开始真正有用的大脑。

---

> **相关链接**
> - [garrytan/gbrain](https://github.com/garrytan/gbrain) — 主仓库
> - [gbrain-evals](https://github.com/garrytan/gbrain-evals) — 评测基准（BrainBench）
> - [OpenClaw](https://github.com/openclawagents/openclaw) — 配套 AI Agent 平台
> - [Hermes](https://github.com/openclawagents/hermes) — 另一个配套 Agent（Railway 一键部署）
> - [FalAI LuxTTS](https://fal.ai/models/fal-ai/lux-tts) — 可与 GBrain 集成的语音摄取

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: GBrain (25,417★, TypeScript) is Garry Tan's (YC President/CEO) production personal AI brain — 146,646 pages, 24,585 people, 5,339 companies in his live deployment, 66 autonomous cron jobs running overnight. Two core differentiators over typical RAG/PKM tools: (1) synthesis layer that writes an actual answer with citations and explicit gap analysis (not a page list), (2) self-wiring knowledge graph with typed edges extracted from every page write with zero LLM calls (+31.4 P@5 over vector-only RAG). Local setup: PGLite in 2 seconds. MCP interface for Claude Code, Codex, Cursor, Claude Desktop, Perplexity, ChatGPT. 43 built-in skills. Overnight dream cycle: enrichment, citation repair, contradiction detection, priority scoring — all while you sleep.

---

## What Makes GBrain Different

Most personal knowledge tools do keyword/vector search and return a list of pages — then you read them yourself. GBrain adds two things nobody else ships together:

**1. Synthesis layer** (`gbrain think`):
```
"What do I need to know before my meeting with Alice tomorrow?"
→ Alice runs engineering at Acme (Series B fintech). 
   Three open items from your last call (April 22):
   1. She owes you a security review (deadline May 1, no update)
   2. You sent 500-seat pricing April 25 (no reply yet)
   3. You said you'd intro a CISO candidate from your network
   Gap: nothing entered the brain about Alice since April 22 — email/Slack not visible.
```
Every claim has a source page. The gap analysis tells you what the brain doesn't know.

**2. Self-wiring knowledge graph** (zero LLM calls):
Every `gbrain capture` extracts entity refs and writes typed edges (`works_at`, `invested_in`, `attended`, `advises`). Enables multi-hop queries: "What did Bob invest in this quarter?" — impossible for pure vector search.

Benchmark: **P@5 49.1%, R@5 97.9%** on a 240-page corpus, **+31.4 points P@5** over graph-disabled variant.

## Quick Start (2 Minutes)

```bash
bun install -g github:garrytan/gbrain
gbrain init --pglite             # 2-second local brain, no Docker
claude mcp add gbrain -- gbrain serve   # wire into Claude Code
gbrain doctor                    # verify health
```

## The Overnight Dream Cycle

66 cron jobs run while you sleep: enrich new pages, fix citations, detect contradictions, score priorities, consolidate duplicate records. Your brain is smarter when you wake up than when you went to bed. Configure with `gbrain cron schedule "0 2 * * *" enrich-all`.

## Using It With Claude Code

Add to `CLAUDE.md`:
```markdown
Brain-first protocol: before answering or starting a task, run:
  gbrain think "<question>" for synthesized answers
  gbrain search "<keywords>" for raw retrieval
After each session, capture new knowledge:
  gbrain capture "Learned today: ..."
```

**Links**: [GitHub](https://github.com/garrytan/gbrain) · [BrainBench evals](https://github.com/garrytan/gbrain-evals) · [Agent tutorial](https://raw.githubusercontent.com/garrytan/gbrain/master/INSTALL_FOR_AGENTS.md)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
