---
title: "OpenBiliClaw：把推荐系统的逻辑反过来——你来决定看什么"
description: "B 站的推荐是黑箱，每天替你决定能看到什么。OpenBiliClaw 是一个本地运行的开源 AI Agent，用五层心理画像跨平台主动帮你找内容，647 star，数据 100% 留在你自己的硬盘。"
titleEn: "OpenBiliClaw: Reversing the Recommendation System — You Decide What You See"
descriptionEn: "Bilibili's recommendation is a black box that decides what you see every day. OpenBiliClaw is a local, open-source AI agent that uses a five-layer psychological profile to proactively find content across platforms for you. 647 stars, data 100% on your own machine."
pubDate: 2026-06-07
category: "Tech-Experiment"
tags: ["Open Source", "Bilibili", "推荐系统", "AI Agent", "隐私", "内容发现", "OpenBiliClaw"]
lang: "zh-CN"
heroImage: "../../assets/images/openbiliclaw-bilibili-open-source-recommendation-banner.png"
---

你刷 B 站的时候，推荐的内容真的是你想看的吗？

推荐系统的本质是一个**中间商**。它站在你和内容之间，用十几个加权指标——点击率、完播率、广告价值、用户留存——压成一个分数来决定你能看到什么。听起来很科学，但这些权重是**平台定的**，最终优化的是平台的利益，不是你的时间。

结果就是：越推越像你已经看过的，信息茧房越来越厚，偶尔的惊喜全靠运气。更糟的是，每个平台都是孤岛——你在 B 站看了三年机械键盘，小红书完全不知道；你在小红书种草的咖啡器具，B 站从来不会推给你。

**OpenBiliClaw 想把这件事反过来。**

## 它是什么

[OpenBiliClaw](https://github.com/whiteguo233/OpenBiliClaw)（`whiteguo233/OpenBiliClaw`）是一个**本地运行、完全开源的跨平台内容发现 AI Agent**。

它不优化平台指标，它先深度理解你这个人，然后根据对你的理解，跨平台主动去找你会喜欢的内容。

- **GitHub**: 647 star，MIT 开源
- **支持平台**: B 站 / 小红书 / 抖音 / YouTube（持续扩展）
- **数据**: 100% 留在你本机的 SQLite 文件，无云端，无账号
- **入口**: Chrome 插件 + 本地 Python 后端 + 桌面/移动 Web

## 核心原理：先懂你，再找内容

这是与传统推荐最根本的差异。

传统推荐的逻辑是："你点了这个，所以给你更多这个。" 协同过滤靠的是和你相似的人的行为，本质上永远推已知领域的已知内容。

OpenBiliClaw 的逻辑是：先构建一个**五层灵魂画像**，然后用心理学桥接逻辑主动猜测你可能感兴趣但从未接触过的领域。

```
事件层  →  你具体做了什么（看了什么、怎么反应的）
偏好层  →  从行为归纳出你的内容口味
觉察层  →  你的认知风格、信息处理方式
洞察层  →  推断 MBTI、核心特质、深层心理需求
灵魂层  →  整体人格素描，你是什么样的人
```

举个例子：一个关注机械表的人，可能对建筑美学感兴趣；一个看量子物理科普的人，可能对哲学有共鸣。系统会主动往这些方向探测，猜对了升级为正式兴趣，猜错了安静退出，不影响你。

**协同过滤永远不会推给你"没人从这条路径走过"的内容，但 OpenBiliClaw 会。**

## 和其他方案的对比

| | B站等平台官方推荐 | 关键词过滤插件 | OpenBiliClaw |
|---|---|---|---|
| 推荐逻辑 | 协同过滤 + 平台权重 | 标签匹配 | 五层心理画像 |
| 内容来源 | 单一平台 | 单一平台 | 跨平台（B站·小红书·抖音·YouTube） |
| 信息茧房 | 越推越窄 | 不解决 | 主动猜测兴趣破茧 |
| 数据归属 | 平台所有 | 通常云端 | 100% 本地 |
| 推荐解释 | "猜你喜欢" | 无 | 像朋友一样告诉你为什么 |
| 可定制 | 不可以 | 低 | 换 LLM / 改画像 / 写 Skill |

## 普通用户怎么用：三步上手

### 第一步：装浏览器插件（2 分钟）

插件是主要入口，负责在 B 站/小红书/抖音/YouTube 页面显示侧边栏、采集反馈，并把登录态安全地交给本地后端。

👉 **[Chrome 应用商店一键安装](https://chromewebstore.google.com/detail/cdfjfkdjjhdaccbldipkjhpibnfbiamg)** — 点「添加至 Chrome」即可。

支持 Chrome、Edge、Brave、Arc 等所有 Chromium 内核浏览器。

### 第二步：启动本地后端（5-10 分钟）

**推荐方式：Docker（最省事）**

```bash
git clone https://github.com/whiteguo233/OpenBiliClaw.git
cd OpenBiliClaw

# 启动后端
docker compose up -d --build

# 交互式初始化（选 LLM、配置 Embedding、登录 B 站）
python3 scripts/agent_bootstrap.py --mode docker --interactive-confirm --wait-for-extension-cookie
```

**没有 Docker 的用户：Python 直接运行**

```bash
# 安装依赖
uv sync  # 或 pip install -e ".[dev]"

# 复制配置文件
cp config.example.toml config.toml

# 交互式初始化
openbiliclaw init
```

初始化时需要选择一个 LLM：

| LLM 方案 | 推荐程度 | 说明 |
|---------|---------|------|
| DeepSeek API | ⭐⭐⭐ 推荐 | 便宜，效果好，默认首选 |
| 本地 Ollama | ⭐⭐ 可用 | 完全离线，效果稍弱 |
| Gemini API | ⭐⭐ 可用 | 云端，效果好，需要科学上网 |
| OpenAI 兼容接口 | ⭐⭐ 可用 | 任意兼容 v1 接口皆可 |

Embedding 模型（用于记忆检索）：
- 有 Ollama → 选 `bge-m3`（完全免费离线）
- 没有 Ollama → 选 Gemini Embedding（需要 API key）

### 第三步：开始使用（日常）

后端启动后，打开浏览器访问 `http://127.0.0.1:8420/web`，就是你的个人推荐首页。

**桌面 Web**：惊喜推荐 Hero + 为你推荐的内容网格，每张卡片都有"为什么推荐给你"的朋友式解释。

**手机使用**：访问 `http://127.0.0.1:8420/m`（需要手机和电脑在同一局域网）。

**日常操作**：
- 看到推荐 → 点「喜欢 / 多来点 / 少来点 / 没兴趣」给反馈
- 想调教画像 → 点「聊一聊」，直接告诉它你想看什么方向
- 看 B 站时 → 插件侧边栏会出现，你在平台上的行为自动被学习

## 它真正有价值的地方

**信息茧房破壁**：绝大多数"反茧房"工具本质上是换了个茧房。OpenBiliClaw 是少数真正从心理学角度出发、主动在你未知领域探索的工具。

**跨平台记忆整合**：你的 B 站喜好会影响小红书的推荐，你在 YouTube 看的内容会反哺整体画像。这在任何单一平台上都做不到。

**数据主权是真的**：不是说说而已。所有画像数据存在本机 SQLite，没有云端同步，关掉后端就什么都访问不到。你可以随时导出、修改甚至删除自己的画像。

**可解释性**：每条推荐都会告诉你为什么。不是"猜你喜欢"的黑盒，是"因为你上周看了 X，我推测你对 Y 领域有潜在兴趣"的逻辑链。

## 需要注意的地方

- **需要自己的 LLM API Key**（或本地 Ollama），每次推荐会消耗少量 token
- **冷启动有个过程**：前几天的推荐可能不准，它需要观察你的行为才能建立画像
- **目前 B 站支持最完整**，小红书/抖音/YouTube 功能仍在扩展中
- **不是 B 站官方工具**，使用涉及浏览器 Cookie，需要对此有基本了解

---

如果你觉得 B 站越刷越无聊、推荐越来越同质化，或者想把散落在各平台的兴趣真正整合起来，OpenBiliClaw 值得花一个下午认真试一试。

**GitHub**: whiteguo233/OpenBiliClaw  
**Chrome 插件**: chromewebstore.google.com/detail/cdfjfkdjjhdaccbldipkjhpibnfbiamg  
**项目主页**: whiteguo233.github.io/OpenBiliClaw/

<!--EN-->

## OpenBiliClaw: Reversing the Recommendation System — You Decide What You See

When you scroll Bilibili, are the recommendations actually what you want to watch?

A recommendation system is fundamentally a **middleman**. It stands between you and content, weighing a dozen metrics — click-through rate, completion rate, ad value, user retention — compressed into a score that decides what you get to see. It sounds scientific, but those weights are **set by the platform**, ultimately optimizing for the platform's interests, not your time.

The result: recommendations converge on what you've already watched, the information bubble thickens, and genuine surprises are just luck. Even worse, every platform is an island — three years of mechanical keyboard videos on Bilibili means nothing on Xiaohongshu; your coffee gear wishlist on Xiaohongshu never influences your Bilibili feed.

**OpenBiliClaw wants to reverse this.**

## What It Is

[OpenBiliClaw](https://github.com/whiteguo233/OpenBiliClaw) (`whiteguo233/OpenBiliClaw`) is a **locally-running, fully open-source cross-platform content discovery AI agent**.

It doesn't optimize platform metrics. It first deeply understands you as a person, then uses that understanding to proactively search for content you'd love — across platforms.

- **GitHub**: 647 stars, MIT license
- **Supported platforms**: Bilibili / Xiaohongshu / Douyin / YouTube (expanding)
- **Data**: 100% stays in a local SQLite file — no cloud, no account
- **Interface**: Chrome extension + local Python backend + desktop/mobile web

## Core Principle: Understand First, Then Find Content

This is the fundamental difference from traditional recommendation.

Traditional recommendation: "You clicked this, so here's more of this." Collaborative filtering relies on people similar to you — it can only surface known content in known domains.

OpenBiliClaw: build a **five-layer soul portrait**, then use psychological bridging to actively probe interests you've never encountered.

```
Events    → What you actually did (what you watched, how you reacted)
Preferences → Content tastes inferred from behavior
Awareness → Cognitive style, information processing patterns
Insights  → Inferred MBTI, core traits, deep psychological needs
Soul      → Overall personality sketch — who you are as a person
```

Example: someone interested in mechanical watches might resonate with architectural aesthetics; someone who watches quantum physics videos might connect with philosophy. The system probes these directions — if it guesses right, the interest gets promoted; if wrong, it quietly retreats.

**Collaborative filtering will never recommend "no one has taken this path before" content. OpenBiliClaw will.**

## Three-Step Setup for Regular Users

### Step 1: Install the Browser Extension (2 minutes)

👉 **[Chrome Web Store — one-click install](https://chromewebstore.google.com/detail/cdfjfkdjjhdaccbldipkjhpibnfbiamg)** — click "Add to Chrome."

Works with Chrome, Edge, Brave, Arc, and all Chromium-based browsers.

### Step 2: Start the Local Backend (5-10 minutes)

**Recommended: Docker**

```bash
git clone https://github.com/whiteguo233/OpenBiliClaw.git
cd OpenBiliClaw

docker compose up -d --build

python3 scripts/agent_bootstrap.py --mode docker --interactive-confirm --wait-for-extension-cookie
```

**Without Docker: Python directly**

```bash
uv sync
cp config.example.toml config.toml
openbiliclaw init
```

During setup, choose an LLM:

| LLM Option | Recommendation | Notes |
|-----------|---------------|-------|
| DeepSeek API | ⭐⭐⭐ Best | Cheap, effective, default choice |
| Local Ollama | ⭐⭐ Works | Fully offline, slightly weaker |
| Gemini API | ⭐⭐ Works | Cloud, needs VPN outside China |
| Any OpenAI-compatible | ⭐⭐ Works | Any v1-compatible endpoint |

### Step 3: Daily Use

After the backend starts, open `http://127.0.0.1:8420/web` for your personal recommendation homepage — content grid with friend-style explanations for every recommendation.

- See a recommendation → click "Like / More of this / Less of this / Not interested" to give feedback
- Want to adjust your profile → click "Chat," tell it what you want
- Browse Bilibili normally → the extension's sidebar appears and learns from your behavior automatically

## Why It's Genuinely Valuable

**Real bubble-breaking**: Most "anti-bubble" tools just replace one bubble with another. OpenBiliClaw is one of the few that genuinely probes unknown territory using psychological inference.

**Cross-platform memory**: Your Bilibili preferences influence Xiaohongshu recommendations. Your YouTube viewing feeds back into your overall portrait. No single platform can do this.

**Real data sovereignty**: All profile data lives in local SQLite. No cloud sync — shutting down the backend means zero access to your data from the outside.

**Explainability**: Every recommendation tells you why. Not a "you might like this" black box — it's "because you watched X last week, I suspect you have latent interest in Y."

## Things to Know

- **Requires your own LLM API key** (or local Ollama) — each recommendation cycle uses a small amount of tokens
- **Cold start takes time**: the first few days of recommendations may not be accurate — it needs to observe your behavior to build a portrait
- **Bilibili support is most complete**; Xiaohongshu/Douyin/YouTube features are still expanding
- **Not an official Bilibili tool** — uses browser cookies; requires basic comfort with that

---

If Bilibili feels increasingly repetitive, or you want to genuinely integrate interests scattered across multiple platforms, OpenBiliClaw is worth a serious afternoon experiment.

**GitHub**: whiteguo233/OpenBiliClaw  
**Chrome extension**: chromewebstore.google.com/detail/cdfjfkdjjhdaccbldipkjhpibnfbiamg  
**Project page**: whiteguo233.github.io/OpenBiliClaw/
