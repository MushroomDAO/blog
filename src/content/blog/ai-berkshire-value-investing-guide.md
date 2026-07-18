---
title: "普通投资者如何用 AI Berkshire 做出专业级投研——以分析腾讯为例"
titleEn: "How Ordinary Investors Can Do Professional-Grade Research with AI Berkshire — Analyzing Tencent as a Case Study"
description: "AI Berkshire（11772★）是一套基于 Claude Code / Codex 的投资研究 Skill 合集，将巴菲特、芒格、段永平、李录四大师方法论系统化，通过多 Agent 并行研究在几分钟内产出专业投研报告。实盘验证：2024年+69.29%、2025年+66.38%，连续两年大幅跑赢标普500。本文面向普通投资者：从安装到用 /investment-team 深度分析一家上市公司的完整操作流程。"
descriptionEn: "AI Berkshire (11,772★) is a Claude Code / Codex skill collection that systematizes the methodologies of Buffett, Munger, Duan Yongping, and Li Lu, producing professional-grade investment research via multi-agent parallel analysis in minutes. Verified live performance: +69.29% (2024), +66.38% (2025) vs S&P 500 +23%/+16%. This guide walks ordinary investors through installation and running a full deep-dive on a listed company."
pubDate: "2026-07-08"
updatedDate: "2026-07-08"
category: "Tech-Experiment"
tags: ["AI投资", "价值投资", "ai-berkshire", "Claude Code", "多Agent", "巴菲特", "投研框架", "上市公司分析"]
heroImage: "../../assets/images/ai-berkshire-investment-guide-banner.jpg"
---

> **仓库**: [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) · 11772★ · MIT · Python  
> **作者公众号**: 复利炼丹炉  
> **兼容**: Claude Code / Codex（OpenAI）

---

## 一个真实的问题

你想认真研究一家上市公司，应该怎么做？

专业投资机构的做法是：3-5个分析师花几周时间，读几十份年报和研报，做竞争格局对比，对管理层做尽职调查，用DCF建模，最后出一份80页的深度报告。

普通人没有这些资源。直接问 AI 呢？ChatGPT、Claude 会给你一篇"一方面……另一方面……"的平衡分析，最后以"投资有风险"收尾——看起来不错，但没法拿来做决策。

**AI Berkshire 解决的正是这个问题**：它不是问答，而是一套迫使 AI 给出可执行结论、使用四大师视角相互对抗、内置反偏见机制的结构化投研框架。

---

## 真实业绩（不是模拟）

这套框架背后是真金白银验证的投资体系：

| 指标 | 2024 全年 | 2025 全年 |
|------|----------|----------|
| **AI Berkshire 实盘** | **+69.29%** | **+66.38%** |
| 标普500 | +23.31% | +16.39% |
| 恒生指数 | +17.67% | +27.77% |
| 沪深300 | +14.68% | +17.66% |
| 纳斯达克 | +28.64% | +20.36% |

连续两年跑赢所有主要指数，两年累计实盘收益超 146 万元（来自作者富途证券真实账户截图）。

> 免责声明：历史收益不代表未来表现。框架是工具，决策责任始终在投资者本人。

---

## 为什么不能直接问 AI？

核心差异有三点：

**1. 强制给结论，不打太极**

普通 AI 会说："拼多多既有增长潜力，也面临竞争压力……"

AI Berkshire 强制输出：

| 策略 | 建议 | 价格区间 |
|------|------|---------|
| 激进型 | 当前价位可建仓20% | $95-105 |
| 稳健型 | 等回购政策明确后建仓 | $85-95 |
| 保守型 | 不符合10年确定性标准，观望 | — |

**2. 四大师视角真实对抗**

以拼多多为例，同一家公司，四个视角：

- **段永平**（商业模式）：好生意，C2M模式难以复制 → 评分 **3.7/5**
- **巴菲特**（财务估值）：扣现金PE仅6.3x，印钞机 → 评分 **4.4/5**
- **芒格**（逆向思考）：护城河比想象中浅，抖音3年做到4万亿GMV → 评分 **3.5/5**
- **李录**（长期确定性）：管理层文化有隐患，10年后不确定 → 评分 **2.0/5**

巴菲特说"真便宜"，李录说"不确定就不买"——这种真实矛盾才是投资决策的核心张力。

**3. 内置反偏见机制**

AI 最危险的输出不是明显的错误，而是"看起来很对但经不起推敲"。框架内置了：

- **信息丰富度评级（A/B/C）**：防止"资料多=确定性高"的幻觉
- **芒格式逆向检验**：强制思考"什么情况下这家公司会死？"
- **快速否决清单**：8条红线一票否决，不管估值多便宜

---

## 19个 Skill 一览

按用途分为五类：

### 深度研究类（最常用）

| Skill | 适合什么时候用 |
|-------|--------------|
| `/investment-research` | 全面分析一家公司，七个模块顺序执行 |
| `/investment-team` | 4个Agent并行研究，最快最全面，适合重要决策 |
| `/management-deep-dive` | 管理层是核心变量时深挖（如新CEO上任） |
| `/private-company-research` | 研究蚂蚁、SpaceX等未上市公司 |
| `/deep-company-series` | 12万字8篇系列深度，适合想彻底搞清一家公司 |

### 财报分析类

| Skill | 适合什么时候用 |
|-------|--------------|
| `/earnings-review` | 只读原始财报，不依赖二手研报 |
| `/earnings-team` | 四大师并行解读 + 可发布为公众号文章 |

### 行业筛选类

| Skill | 适合什么时候用 |
|-------|--------------|
| `/industry-research` | 产业链全景，从一个投资主题找所有机会 |
| `/industry-funnel` | 全市场 → 粗筛10家 → 终选3家深度分析 |
| `/quality-screen` | 快速排除非一流公司（7条硬指标） |
| `/investment-checklist` | 10分钟六关快速判断是否值得深入 |
| `/bottleneck-hunter` | 从超级趋势找产业链瓶颈和套利机会 |

### 持仓管理类

| Skill | 适合什么时候用 |
|-------|--------------|
| `/portfolio-review` | 对整个组合做仓位、集中度、再平衡分析 |
| `/thesis-tracker` | 买入后追踪投资论文是否被证伪 |
| `/news-pulse` | 股价大涨/大跌时10分钟快速归因 |

### 思维工具类

| Skill | 适合什么时候用 |
|-------|--------------|
| `/dyp-ask` | 用段永平的方式思考任何问题 |
| `/financial-data` | 财务数据获取和多源交叉验证 |
| `/wechat-article` | 把投研结果转成可发布的公众号文章 |

---

## 快速开始

### 第一步：安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

验证安装：`claude --version`

### 第二步：克隆并安装 Skills

```bash
git clone https://github.com/xbtlin/ai-berkshire.git
cd ai-berkshire

# macOS / Linux
./scripts/install-claude-commands.sh

# Windows PowerShell
.\scripts\install-claude-commands.bat
```

### 第三步：确认安装

打开 Claude Code，输入 `/investment-checklist` 看到命令提示说明 Skills 安装成功。

> **关于权限确认**：这些 Skills 会频繁调用工具，Claude Code 默认每次都会弹出授权确认。如果觉得频繁，可以用 `claude --dangerously-skip-permissions` 启动。只在你信任当前工作目录和命令时使用。

---

## 实战：用 AI Berkshire 深度分析腾讯

以下是从零到一份完整投研报告的完整流程。

### 第一步：快速预筛

先用 10 分钟判断腾讯是否值得深入研究：

```
/investment-checklist 腾讯
```

输出示例：

> 第一关：能力圈 ✅（我理解社交+游戏+广告的商业模式）  
> 第二关：好生意 ✅（高毛利、经常性收入、网络效应）  
> 第三关：护城河 ✅（12亿用户社交关系链，极高转换成本）  
> 第四关：管理层 ✅（Pony Ma低调务实，长期资本配置纪律强）  
> 第五关：安全边际 ❓（需要深入估值后判断）  
> 第六关：决策纪律 ⏸（需要确认不是FOMO驱动）  
>
> **结论：值得深入研究**

六关有一关不通过，就停下来。不浪费时间在不值得深入的公司上。

### 第二步：多Agent并行深度研究

```
/investment-team 腾讯
```

这会启动 4 个独立 Agent 同时工作：
- Agent 1（段永平）：分析生意本质和商业模式
- Agent 2（巴菲特）：财务数据、估值、安全边际
- Agent 3（芒格）：逆向思考、竞争风险、失败场景
- Agent 4（李录）：长期趋势、文明确定性、10年后判断

Team Lead 综合四个Agent的结论，产出：

```
四维评分总表：

| 维度         | 框架   | 评分    | 核心判断                              |
|------------|--------|---------|-------------------------------------|
| 商业模式&护城河 | 段永平 | ★★★★★   | 社交关系链+微信支付，护城河极宽且仍在变宽         |
| 财务&估值    | 巴菲特 | ★★★★☆   | 游戏+广告双引擎，当前PE处历史中低位              |
| 行业&竞争    | 芒格   | ★★★★☆   | 抖音在短视频侵蚀，但微信生态不可替代              |
| 风险&管理层  | 李录   | ★★★★☆   | 监管压力是变量，但Pony Ma长期价值观清晰            |

综合评分：4.6 / 5

投资建议（港元）：
- 激进型：390-420 港元可建仓30%
- 稳健型：360-390 港元建仓
- 保守型：≤350 港元等待更高安全边际
```

### 第三步：读财报验证

在做买入决策前，用 `/earnings-review` 读原始财报，不依赖二手分析：

```
/earnings-review 腾讯 2025Q4
```

技术注意事项：

```python
# 框架内置精确计算，避免AI心算偏差
# 市值手算校验示例（来自 tools/financial_rigor.py）
python3 tools/financial_rigor.py verify-market-cap \
  --price 410 --shares 9.11e9 \
  --reported 3.74e12 --currency HKD
# ✅ 验证通过，偏差仅 0.12%
```

所有关键数据至少2个独立来源交叉验证，避免单位混淆（港币亿 vs 人民币亿）。

### 第四步：持续跟踪

买入后，用 `/thesis-tracker` 建立你的投资论文追踪系统：

```
/thesis-tracker 腾讯
```

每次有重大新闻（监管变化、财报、管理层变动），运行：

```
/news-pulse 腾讯
```

10分钟得到"发生了什么、是否影响原来的投资论文"的结构化归因。

---

## 更多使用场景

### 行业扫描

```
# 从AI算力这个主题，找到整个产业链的投资机会
/industry-funnel AI算力

# 对整个恒生指数做质量筛选，排除非一流公司
/quality-screen 恒生指数成分股
```

### 多公司横向对比

```
# 同一标准一次比较多家
/investment-checklist 茅台, 腾讯, 美团, 拼多多, 美的
```

七家公司用完全相同的评分标准，横向可比。

### 供应链瓶颈猎手

```
# 从一个大趋势出发，找产业链上被忽视的投资机会
/bottleneck-hunter AI基础设施
```

---

## 成本说明

深度研究类 Skill（尤其是 `/investment-team`）会消耗较多 tokens，因为 4 个 Agent 并行工作，每个都做完整研究。

**推荐的成本控制策略**：

1. **先用 `/investment-checklist` 预筛**：10分钟排除不值得深研的公司，不浪费深度研究的成本
2. **不通过就停**：八条否决红线（管理层诚信问题、无法理解的商业模式等）一票否决，不管估值多便宜
3. **只对真正关注的公司用 `/investment-team`**：你愿意投资的公司，花几美元做深度研究是合理的

---

## 总结

AI Berkshire 的核心价值不是"用AI帮你分析"，而是把四大价值投资大师的决策框架系统化，通过多Agent对抗消除单一视角的盲点，通过内置机制防止AI给出那种"看起来对但没法拿来决策"的平衡分析。

两年实盘验证的业绩说明这套方法论是可行的——当然，执行质量和选时能力同样重要。

**给普通投资者的建议**：从 `/investment-checklist` 开始，用它筛选你已经在关注的公司。当一家公司六关全部通过时，再投入 `/investment-team` 的深度研究。

---

> **相关链接**
> - [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) — 完整仓库（19个 Skills）
> - [作者公众号：复利炼丹炉](https://github.com/xbtlin/ai-berkshire#精选研究首发于公众号) — 精选深度研究首发
> - [快速开始文档](https://github.com/xbtlin/ai-berkshire#快速开始)

---

> ⚠️ **投资风险提示**：本文仅介绍开源工具的使用方法，不构成任何投资建议。投资决策请基于自身研究和风险承受能力独立判断。历史收益不代表未来表现。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: AI Berkshire (11,772★, MIT, Python) is a Claude Code / Codex skill collection that forces investment analysis to produce actionable conclusions rather than balanced non-answers. Its framework systematizes four value investing masters (Buffett on financials/valuation, Munger on adversarial thinking, Duan Yongping on business quality, Li Lu on long-term civilizational trends) as parallel agents that independently research a company then synthesize. The framework's author published a live account track record: +69.29% (2024), +66.38% (2025) vs S&P 500's +23%/+16%. 19 skills covering single-stock deep dives, earnings analysis, industry screening, portfolio management, and thesis tracking.

---

## Getting Started (5 Minutes)

```bash
npm install -g @anthropic-ai/claude-code
git clone https://github.com/xbtlin/ai-berkshire.git
cd ai-berkshire && ./scripts/install-claude-commands.sh
```

Then in Claude Code: `/investment-checklist Tencent`

## The Core Workflow: Analyzing a Listed Company

**Step 1 — Quick pre-screen (10 min)**:
```
/investment-checklist 腾讯
```
Six gates: circle of competence → business quality → moat → management → margin of safety → decision discipline. Any gate fails → stop. Don't waste deeper research on companies that don't clear the basics.

**Step 2 — Multi-agent deep dive**:
```
/investment-team 腾讯
```
Four independent agents run parallel research. Each searches the web independently, scores the company from their master's framework, identifies risks. Team Lead synthesizes into a composite score + tiered buy recommendations (aggressive/conservative/pass).

**Step 3 — Primary source earnings read**:
```
/earnings-review 腾讯 2025Q4
```
Raw annual report only — no sell-side research summaries. Key numbers cross-verified against 2 independent sources. Market cap hand-calculated (price × shares) to catch unit errors (HKD bn vs RMB bn).

**Step 4 — Track the thesis post-buy**:
```
/thesis-tracker 腾讯   # establish and monitor the investment thesis
/news-pulse 腾讯       # rapid attribution on any big price move
```

## The Anti-Hallucination Layer

The framework's most important feature isn't the analysis — it's the discipline mechanisms that prevent plausible-but-wrong outputs:

- **Information richness rating (A/B/C)**: flags when data is thin so confidence estimates stay honest
- **Munger reverse test**: "Under what circumstances does this company fail?" — required for every analysis
- **8-item veto checklist**: management integrity issue → automatic reject regardless of valuation
- **5-sentence mirror test**: "I'm buying X at $Y because…" If you can't complete it coherently in 5 sentences, don't buy

**Links**: [GitHub](https://github.com/xbtlin/ai-berkshire) · [Author's WeChat: 复利炼丹炉]

---

> ⚠️ **Risk Disclaimer**: This article covers open-source tooling only. Nothing here constitutes investment advice. Past performance does not predict future returns.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
