---
title: "我用 AI Agent 给自己搭了个每日情报看板，现在开源了"
titleEn: "I Built a Local AI Intelligence Dashboard with Daily Agent Digests — Now Open Source"
description: "ai-intel-workbench 是一个本地优先的 AI 每日情报工作台：Agent 每天自动调研 5 个维度（大厂动态、KOL 观点、前沿论文、热门开源、AI×金融），沉淀成可视化 HTML 看板，可选推送到飞书/Lark 机器人，支持 Claude Code 和 Codex。本文手把手教普通人 10 分钟跑起来，以及如何越用越好用。"
descriptionEn: "ai-intel-workbench is a local-first daily AI intelligence workbench: an Agent automatically researches 5 dimensions each day (big-tech moves, KOL insights, frontier papers, trending open-source, AI×finance), builds a visual HTML dashboard, with optional push to Feishu/Lark bot. Works with Claude Code and Codex. This guide helps anyone get it running in 10 minutes and improve over time."
pubDate: "2026-06-30"
updatedDate: "2026-06-30"
category: "Tech-News"
tags: ["AI工具", "开源", "情报工作台", "Claude Code", "每日digest", "Agent自动化", "飞书", "看板"]
heroImage: "../../assets/images/ai-intel-workbench-daily-dashboard-guide-banner.jpg"
---

> GitHub: [weishao831/ai-intel-workbench](https://github.com/weishao831/ai-intel-workbench)
> 
> 作者的初衷说得很直白：*"不是'知道更多资讯'，而是把每天杂乱的信息流，变成可追踪、可回看、可复用的情报库。"*

---

## 这是什么？用一句话说

**一个住在你电脑本地的 AI 研究助手**，每天帮你自动扫描 AI 行业动态，整理成一张结构清晰的网页看板，可以选择同步推送到飞书/Lark 机器人。

它不是新闻聚合器（RSS 阅读器），也不是某个平台的订阅功能——它是一套**让 AI Agent 主动替你调研、过滤、整理**的本地工作流。

---

## 为什么你需要它？

信息过载是真实问题。每天刷完 Twitter、公众号、GitHub Trending、Hacker News……你得到的是碎片，不是洞察。

ai-intel-workbench 解决的是另一个层次的问题：

| 痛点 | 工具的解法 |
|---|---|
| 不知道昨天 OpenAI/Anthropic/字节 发了什么 | Agent 每天主动抓官方 newsroom 摘要 |
| KOL 太多，不知道谁在说什么有价值的 | 配置 KOL 名单，Agent 每天提炼观点 |
| arXiv 每天几十篇，看不完 | 筛出 6-10 篇重要论文，每篇给「大白话版」 |
| GitHub Trending 刷了，但不知道项目在干嘛 | 每个项目：做什么 + 亮点 + 上手难度 |
| AI×加密/金融方向消息太散 | 专门维度追踪 DeFAI、AI 量化、AI 投研 |

而且**有记忆**：每天的 digest 按日期存本地，历史可以回看，可以追踪哪些话题是持续热点。

---

## 五个维度，Agent 每天给你做这些

这是工作台的核心：**五维度并行调研**。

### 🏢 AI 大厂动态
追踪：OpenAI、Anthropic、Google、Nvidia、Meta、xAI、Mistral、字节、阿里、DeepSeek 等

Agent 抓什么：产品发布 / 研究论文 / 战略动作——抽象内容配案例解释。

### 🗣️ KOL 观点
信源：X/Twitter + Latent Space + Hacker News + The Batch 等

产出：KOL 名单可自定义更新 + 当天讨论热点 + **可借鉴实践清单**（不只是列意见，告诉你怎么用）。

### 📄 前沿论文
信源：HuggingFace Papers + arXiv（cs.AI / cs.CL / cs.LG）

过滤后 6-10 篇，每篇给：小白版摘要 + 核心创新点 + 落地启发。

### 🧩 热门开源项目
信源：GitHub Trending + Hacker News + Product Hunt

每个项目：做什么 + 内部逻辑 + 亮点 + 价值 + 上手难度评估。

### 💰 AI × 金融 / 加密
覆盖四个子方向：加密 / 泛金融 / 股票 / AI 交易策略 + 大盘情绪

---

## 长什么样？（看板界面）

工作台是一个**零依赖的本地 HTML 文件**（`index.html`），直接在浏览器打开，不需要安装 Node.js 或任何框架。

打开后能看到：
- 今日速览（五维度卡片式布局）
- 跨维度热点（多维度同时出现的话题自动关联）
- 市场情绪（AI×金融维度的大盘判断）
- 历史 digest 回看（日历导航）
- ⭐ 标记功能（标记感兴趣的条目，数据沉淀到偏好库）

本地 Python 起一个静态服务：
```bash
python3 scripts/serve.py --port 4318
# 浏览器访问 http://127.0.0.1:4318/
```

---

## 10 分钟上手教程

### 前提条件
- Python 3（macOS 自带，Windows/Linux 需安装）
- 有 Claude Code 或 Codex 之一（用来执行 Agent 调研）
- 可选：飞书 Webhook（用于推送到群机器人）

### 第一步：克隆仓库

```bash
git clone https://github.com/weishao831/ai-intel-workbench.git
cd ai-intel-workbench
```

### 第二步：初始化配置

```bash
python3 scripts/init.py
```

交互式向导会问你：
- **行业锚定**：选 `ai-crypto`（AI+加密）、`ai-finance`（AI+金融），或自定义
- **推送机器人**：有飞书 Webhook 就填，没有先跳过
- **产出语言**：`zh`（中文）/ `en`（英文）/ `bilingual`（双语）
- **端口**：默认 4318

如果不想交互，一行命令搞定：
```bash
python3 scripts/init.py --anchors ai-crypto,ai-finance --language zh --bot none
```

### 第三步：先看内置样例（不需要 Agent）

```bash
python3 scripts/run_daily.py --date today --sample
python3 scripts/serve.py --port 4318
```

浏览器打开 http://127.0.0.1:4318 就能看到工作台界面了，用内置的示例数据验证看板没问题。

### 第四步：生成今天的真实调研

```bash
python3 scripts/run_daily.py --date today
```

这步会在 `.daily-intel/runs/YYYY-MM-DD/research_prompt.md` 生成一个调研提示文件。

然后把这个 prompt 交给你的 Agent 执行：

**如果用 Claude Code：**
```bash
claude -p "$(cat .daily-intel/runs/$(date +%Y-%m-%d)/research_prompt.md)"
```

**如果用 Codex：**
```bash
codex exec "$(cat .daily-intel/runs/$(date +%Y-%m-%d)/research_prompt.md)"
```

Agent 会读取 skill 说明完成调研，结果写入 `data/YYYY/MM/DD/digest.js`。

**更简单的方式**——直接对 Claude Code 说：
```
帮我初始化每日资讯工作台，关注 AI+加密和 AI+金融，产出中文；
如果没有推送机器人，就先只更新本地看板；每天早上 08:30 自动运行。
```

Claude Code 会读取 CLAUDE.md 和 skill 说明，自动完成初始化、配置和定时任务设置。

### 第五步：设置定时任务（一次性操作）

```bash
# 每天 08:30 自动运行
python3 scripts/install_schedule.py install --time 08:30

# 如果有飞书 Webhook，也可以同时推送
python3 scripts/install_schedule.py install --time 08:30 --push
```

- **macOS**：自动安装 LaunchAgent（类似 launchd 定时服务）
- **Linux**：自动写入 crontab

之后每天早上打开工作台，就能看到昨晚 Agent 跑完的今日情报了。

---

## 配合飞书机器人推送

如果你的团队用飞书/Lark，可以配置群机器人，每天把摘要推送到群里：

1. 在飞书群里创建「自定义机器人」，获取 Webhook 地址
2. 编辑 `config/push.yaml`：
   ```yaml
   enabled: true
   bot_type: lark
   webhook: https://open.larksuite.com/open-apis/bot/v2/hook/你的webhook
   ```
3. 之后运行时加 `--push` 参数即可：
   ```bash
   python3 scripts/run_daily.py --date today --push
   ```

---

## 越用越好用：「反馈闭环」是关键

这是 ai-intel-workbench 与普通 RSS 阅读器最大的设计区别——它有**自我优化**机制。

### 每天使用时：⭐ 标记感兴趣的条目

在工作台点 ⭐，偏好信号会被记录下来：哪些来源、哪些话题、哪些 KOL 真正吸引你。

### 每周一次：根据标记调整配置

```
你的标记数据 → 哪些信源高命中？哪些 KOL 你一直不关注？→ 更新 config/*.yaml
```

具体调什么：
- **`config/sources.yaml`**：高命中的信源升权，连续没贡献的降权/删除
- **`config/kol.yaml`**：两周没被你标记的 KOL 移入观察池；频繁出现的新账号升级
- **`config/keywords.yaml`**：噪音太多就收紧关键词；漏掉重要内容就放宽时间窗口
- **维度配比**：如果你 80% 的标记都在论文维度，就调大论文的抓取数量上限

这套机制的哲学是：**不是优化某一次调研，而是优化调研这件事本身的策略**。

---

## 系统架构（给想深入的人）

```
触发（定时/手动）
    ↓
生成调研 Prompt → Agent 执行（Claude Code / Codex）
    ↓
五维度并行 fan-out（各自抓取 → 过滤 → 翻译 → 小白化）
    ↓
写入 data/YYYY/MM/DD/digest.js + 更新 manifest.js
    ↓
刷新 index.html 工作台
    ↓
（可选）推送到飞书/Lark 机器人
    ↓
你标记感兴趣的条目 → 偏好信号回流 → 下周更新 config/*.yaml
```

### 核心文件

| 文件 | 用途 |
|---|---|
| `config/industry.yaml` | 行业锚定（ai-crypto / ai-finance / 自定义） |
| `config/sources.yaml` | 信源权重配置 |
| `config/kol.yaml` | KOL 名单 |
| `config/keywords.yaml` | 搜索词 + 噪音过滤词 |
| `config/push.yaml` | 飞书机器人配置 |
| `config/runtime.yaml` | 端口 / agent 命令 / 语言 / 定时 |
| `data/YYYY/MM/DD/digest.js` | 每天的 digest 数据 |
| `index.html` | 零依赖本地工作台 |
| `skills/` | Claude Code / Codex 可读的 skill 说明 |

### X/Twitter 数据源设计

开源版不依赖个人 Cookie，默认用公共网页源。如果想接 Twitter 数据：
- 选项 1：本地 Chrome 扩展（复用你自己的登录态）
- 选项 2：X API Key
- 选项 3：用户导出的书签/CSV

安全原则：不读 Cookie，不做写操作（点赞/发帖），不绕过验证码。

---

## 如何自定义行业方向

目前内置了 `ai-crypto`（AI+加密）和 `ai-finance`（AI+金融），但完全可以改成其他方向：

```yaml
# config/industry.yaml
anchors:
  - ai-healthcare   # AI+医疗
  - ai-robotics     # AI+机器人
```

或者关注特定地区：
```yaml
anchors:
  - ai-china        # 国产 AI 动态
  - ai-enterprise   # AI+企业软件
```

然后在 `config/keywords.yaml` 里配置对应的搜索词，Agent 就会按新方向调研。

---

## 跟其他工具的本质区别

| 工具类型 | 做什么 | 局限 |
|---|---|---|
| RSS 阅读器 | 订阅信源，你来读 | 信息量大，没有过滤和整理 |
| 新闻聚合 App | 算法推送热门内容 | 不可控，容易娱乐化，有平台锁定 |
| 搜索引擎每日通知 | 关键词有新结果时推送 | 碎片化，没有结构和关联 |
| **ai-intel-workbench** | **Agent 主动调研 + 结构化 + 本地存储 + 自我优化** | 需要本地 Agent（Claude Code / Codex） |

核心差异：**它不是给你推送内容，而是替你完成「研究者」的工作，然后给你一份经过清洗和结构化的情报报告。**

---

## 上手路径建议

**第一天**：克隆 → 初始化 → 跑 sample 看看界面长什么样
**第三天**：让 Claude Code 跑一次真实调研，看看质量
**第一周末**：看看哪些条目你点了 ⭐，调整 KOL 名单和关键词
**第二周**：安装定时任务，让它自动跑，你只需要每天早上打开看
**第一个月**：做第一次深度复盘，调整维度配比和信源权重

---

## 目前路线图

已完成：
- ✅ 本地 HTML 工作台（零依赖）
- ✅ 五维度调研框架
- ✅ 飞书/Lark 机器人推送
- ✅ Claude Code + Codex skill
- ✅ macOS launchd / Linux cron 定时任务
- ✅ 历史 digest 回看 + ⭐ 标记

开发中：
- 🔲 完整公共网页采集器
- 🔲 Chrome provider 示例（复用登录态）
- 🔲 X API provider 示例
- 🔲 标记数据回流自动调权

---

## 写在最后

ai-intel-workbench 解决的不是「怎么知道更多」，而是「怎么把信息流变成情报库」。

它假设你已经有信息过载的问题——收到的内容太多，真正记住和用到的太少。

它的设法是：**让 Agent 每天替你做一遍「信息研究员」该做的事**，你只需要每天早上花 10 分钟看结果，标记有价值的内容，然后系统慢慢学习你关心什么。

开源地址：https://github.com/weishao831/ai-intel-workbench

MIT 协议，可以直接 fork 改成自己的版本。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: ai-intel-workbench is a local-first daily AI intelligence workbench. Agent auto-researches 5 dimensions (big-tech moves, KOL insights, frontier papers, trending OSS, AI×finance), outputs a local HTML dashboard, and optionally pushes digests to Feishu/Lark bots. Works with Claude Code and Codex.

---

## What It Does

An open-source local AI research assistant that auto-scans the AI landscape every day and organizes findings into a structured web dashboard. Agent does the research; you review the digest.

**5 research dimensions per day**:
- 🏢 Big-tech moves (OpenAI, Anthropic, Google, Nvidia, Meta, ByteDance, Alibaba, DeepSeek)
- 🗣️ KOL insights (X/Twitter, Hacker News, Latent Space, The Batch)
- 📄 Frontier papers (HuggingFace Papers, arXiv cs.AI/CL/LG) — 6-10 per day with plain-English summaries
- 🧩 Trending open-source (GitHub Trending, Hacker News, Product Hunt)
- 💰 AI × Finance/Crypto (DeFAI, AI trading, AI investment research, market sentiment)

## 10-Minute Setup

```bash
git clone https://github.com/weishao831/ai-intel-workbench.git
cd ai-intel-workbench

# Interactive setup wizard
python3 scripts/init.py

# Or non-interactive
python3 scripts/init.py --anchors ai-crypto,ai-finance --language zh --bot none

# View sample dashboard (no agent needed)
python3 scripts/run_daily.py --date today --sample
python3 scripts/serve.py --port 4318
# Open http://127.0.0.1:4318

# Schedule daily at 08:30
python3 scripts/install_schedule.py install --time 08:30
```

## Self-Optimization Loop

⭐ mark interesting items → signal what sources/KOLs/topics matter → weekly config update → better research next week.

The system learns what you actually read, not what you think you want.

## Works With

- **Claude Code**: reads `CLAUDE.md` + `skills/daily-intelligence-workbench/SKILL.md`
- **Codex**: reads `.codex-plugin/plugin.json` + `skills/`
- **Plain Python 3**: scripts work standalone, no npm/node needed

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
