---
title: "免费 Google Trends MCP：小工作室的日常趋势雷达，和收费 MCP 这样搭配最省钱"
titleEn: "The Free Google Trends MCP: A Daily Trend Radar for Small Studios — and How to Pair It With the Paid One"
description: "purahmanian/google-trends-mcp 是一个 MIT 开源、无需 API Key、纯 npx 一行装的 Google Trends MCP，直接吐官方 0–100 数据。它数据源只有 Google，但正因为『官方真值 + 免费无限量（悠着点用）+ 地域下钻』，恰好能当日常主力雷达，把收费的多源 MCP 省着用在关键验证上。本文给小工作室/小公司一套双 MCP 搭配的低成本趋势捕捉流水线，从发现到写分析文章到发布。"
descriptionEn: "purahmanian/google-trends-mcp is an MIT-licensed, no-API-key, one-line-npx Google Trends MCP that returns official 0–100 data. Its only source is Google — but 'official ground truth + effectively free (paced) + regional drill-down' makes it the perfect daily workhorse radar, letting you save the paid multi-source MCP for key validation. This guide gives small studios a low-cost dual-MCP trend-capture pipeline: from discovery to analysis article to publishing."
pubDate: "2026-07-06"
updatedDate: "2026-07-06"
category: "Tech-Experiment"
tags: ["MCP", "Google Trends", "开源", "AI Agent", "内容创作", "小工作室", "趋势分析", "免费工具"]
heroImage: "../../assets/images/free-google-trends-mcp-studio-guide-banner.jpg"
lang: "zh-CN"
---

> **仓库**: [github.com/purahmanian/google-trends-mcp](https://github.com/purahmanian/google-trends-mcp) · MIT · TypeScript
> **安装**: `claude mcp add google-trends -- npx -y google-trends-mcp` · **无需 API Key**
> **数据源**: Google Trends 官方端点（真值 0–100，非估算） · **速率**: 每分钟几次为宜
> **搭配阅读**: 上一篇讲的收费多源 MCP → [Google Search Trends MCP 实战](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/)

---

## 一、为什么要专门写"免费的那个"

上一篇我们讲了 [TrendsMCP](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/)——25+ 数据源、交叉验证、很强，但**收费**（免费额度只有 100 次/月），而且它返回的是"归一化的**专有估算值**"。

对一个小工作室、或者夫妻店式的小公司来说，100 次/月这个额度，稍微认真做几次多源分析就见底了。这时候你需要一个**能天天跑、不心疼**的主力雷达。

`purahmanian/google-trends-mcp` 正好补上这一格。它的定位和收费 MCP **完全互补**：

| 维度 | 免费 MCP（本文） | 收费 TrendsMCP（上一篇） |
|------|----------------|------------------------|
| 数据源 | **只有 Google**（搜索/热榜/地域） | 25+ 源（YouTube/TikTok/Reddit/Amazon…） |
| 数据性质 | **Google 官方真值** 0–100 | 归一化**专有估算值** |
| 费用 | **免费**（MIT 开源） | 免费 100 次/月，超了收费 |
| 用量 | 悠着点用，几乎无限 | 额度宝贵，要省着用 |
| API Key | **不需要** | 需要注册 |
| 地域下钻 | **有**（`interest_by_region`） | 弱 |
| 稳定性 | 靠非官方端点，可能被 Google 限流 | 服务商托管，相对稳 |

一句话总结这套搭配哲学：

> **免费 MCP 当"广撒网"的日常主力（官方真值、天天跑），收费 MCP 当"精准验证"的关键补刀（多源交叉、省着用）。**

---

## 二、这个免费 MCP 有什么

它是一个 MIT 开源、TypeScript 写的 MCP Server，直接调 Google Trends 官方端点，**不需要任何 API Key**。暴露 5 个工具：

| 工具 | 作用 | 关键参数 |
|------|------|---------|
| `interest_over_time` | 最多 5 个词的周级兴趣曲线（0–100） | `terms`、`timeframe`（如 `today 5-y`） |
| `compare_terms` | 2–5 个词归一化对比，直接点出赢家 | `terms` |
| `related_queries` | 某个词的**热门 + 上升**相关搜索 | `term` |
| `trending_now` | 指定国家的**当日热榜** | `country` / geo code |
| `interest_by_region` | 某个词的**地域分布**（国家或次级地区） | `term`、region scope |

注意两个和收费版不一样的关键能力：

- **`related_queries` 的 "rising"（上升）** = 免费拿到 Google 官方的"正在上涨的相关搜索"，这是选题和 breakout 发现的金矿。
- **`interest_by_region`（地域下钻）** = 一个词在哪个省/州/城市最热。**这对做本地生意的小公司简直是刚需**——收费那个多源 MCP 反而弱在这块。

⚠️ 老实话：它靠的是 Google **非官方端点**，Google 随时可能改结构或限流。速率上，**每分钟几次**比较稳，撞到 HTTP 429 就等 2–5 分钟。它不是企业级 SLA，但对日常捕捉够用。

---

## 三、一行装好（真的只要一行）

**Claude Code（推荐）：**

```bash
claude mcp add google-trends -- npx -y google-trends-mcp
```

**Claude Desktop：** 编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "google-trends": {
      "command": "npx",
      "args": ["-y", "google-trends-mcp"]
    }
  }
}
```

**Cursor / Codex：** 在 `~/.codex/config.toml` 里加同样的 `npx -y google-trends-mcp`。

没有 Key、没有注册、没有配额页面。重启客户端，对 AI 说一句就能验证：

> "用 google-trends 查一下 'City Walk' 过去 12 个月的兴趣曲线，再看看有哪些 rising 相关搜索。"

如果你把上一篇的收费 MCP 也装了，两个可以**同时挂着**——AI 会根据你的指令自己选用哪个。这就是双 MCP 搭配的物理基础。

---

## 四、小工作室的日常趋势捕捉流水线（双 MCP 版）

下面这套流程，是把两个 MCP 的长处拼起来，专为**没有专职数据分析、但需要持续产内容/找选品**的小团队设计的。核心原则：**能用免费的绝不动收费额度，只在"要下注了"那一刻用收费的做最终确认。**

### 阶段 1 · 广撒网（免费 MCP，天天跑）

每天用免费 MCP 做低成本发现，把额度宝贵的收费 MCP 完全按住不动：

1. `trending_now`（你的目标国家）→ 拉当日热榜。
2. 针对你领域的关键大词，`related_queries` 取 **rising** → 捞正在上涨的长尾。
3. 对候选词 `interest_over_time`（`today 3-m` / `today 12-m`）→ 看曲线是不是在**起飞**（还在往上翘，不是见顶）。

**提问模板：**

> "用 google-trends：① trending_now 拉中国当日热榜；② 对 '露营'、'骑行'、'飞盘' 分别取 related_queries 的 rising；③ 把所有正在上升的词用 interest_over_time 查过去 3 个月，只留下曲线还在上涨的。给我一张候选清单。"

### 阶段 2 · 地域下钻（免费 MCP，本地生意专用）

小公司做的往往是**区域生意**。用 `interest_by_region` 看候选词在哪些地区最热：

**提问模板：**

> "用 interest_by_region 查 '露营装备' 在中国各省的兴趣分布，告诉我前 5 个省。如果我要做本地投放/线下活动，应该优先哪几个城市？"

这一步收费 MCP 做不好，是免费 MCP 的独门价值。

### 阶段 3 · 精准验证（收费 MCP，只在这一步花额度）

阶段 1、2 免费筛出的**少数几个真正想下注的候选**，才动用收费 MCP 的多源交叉——确认这个需求不是 Google 一家的"一波流"，而是全网（YouTube/TikTok/Reddit/Amazon）同步在涨的真趋势。

**提问模板：**

> "这几个候选词 [A, B]，我打算投入做内容/选品。用收费的 trends-mcp 在 YouTube、TikTok、Reddit、Amazon 上分别验证一下：是不是多源同步在涨？只有多源都确认的才值得我下注。"

> 💡 **省钱关键**：阶段 1、2 可能查了几十次（全免费），但收费 MCP 只在最后花了 1–2 次。一个月 100 次的免费额度，够你验证几十个真候选——足够小工作室用了。

### 阶段 4 · 产出分析文章（AI 直接写）

数据都在 AI 上下文里了，直接让它成文：

**提问模板：**

> "基于刚才免费 MCP 的曲线 + 地域数据 + 收费 MCP 的多源验证，帮我写一篇 800 字的趋势分析短文：这个趋势是什么、涨得多快、哪些地区最热、多源是否共振、给我们工作室的 3 条可执行建议（选题/选品/投放）。"

---

## 五、把它固化成一个"每日趋势简报"Agent

小工作室最缺的是"每天有人盯趋势"。这套双 MCP 流程可以用 Claude Code 的定时任务固化成一个**每天早上自动跑**的 Agent：

```
每天 09:00：
  [免费 MCP]
    1. trending_now → 当日热榜
    2. 我的 3 个领域大词 → related_queries(rising)
    3. 候选词 interest_over_time → 只留起飞中的
    4. interest_by_region → 标注每个候选的热点地区
  [收费 MCP，仅对 Top 3 候选]
    5. 多源交叉验证 → 真趋势 / 一波流
  [产出]
    6. AI 写成《今日趋势简报》：候选 + 地域 + 验证结论 + 建议
  → 推到工作室群 / 我的手机
```

成本核算：免费 MCP 部分**零成本**；收费 MCP 每天只碰 Top 3 候选、约 3–9 次请求，一个月约 90–270 次——如果只做工作日、只验证最强候选，**免费额度 100 次/月甚至可能刚好够**，真需要再升 $19 的 Starter。一个每天帮你盯全网趋势的"分析助理"，成本从 0 到 20 刀封顶。

---

## 六、什么时候用哪个：一张决策表

| 你的需求 | 用哪个 MCP |
|---------|-----------|
| 每天扫热榜、找上升长尾 | 免费（`trending_now` + `related_queries` rising） |
| 看一个词是不是在起飞 | 免费（`interest_over_time`） |
| 这个词在哪个地区最热（本地生意） | **免费独门**（`interest_by_region`） |
| 要 Google 官方真值、不接受估算 | **免费独门** |
| 确认多源共振、避免一波流 | **收费独门**（YouTube/TikTok/Reddit/Amazon…） |
| 要下重注前的最终验证 | 收费 |
| 追求端点稳定性、企业级 | 收费（托管服务） |

---

## 七、边界与老实话

- **只有 Google**：免费 MCP 看不到 TikTok/Reddit/Amazon 的独立信号，这正是它需要收费 MCP 补位的原因。
- **非官方端点**：Google 可能限流或改结构，作者说"通常改个 URL 或参数就能修"，但没有 SLA 保证。
- **速率限制**：每分钟几次，别写脚本狂刷；429 就等几分钟。
- **免费 ≠ 零维护**：端点变动时可能要更新 npm 包版本。

但对绝大多数小工作室来说，这套"**免费打底 + 收费补刀**"的组合，几乎是**用最低成本换来一双持续盯全网趋势的眼睛**。趋势捕捉从来不是大公司的专利——现在一个两人小团队，用一行 `npx` 加最多 20 刀/月，就能拥有过去只有专职分析师才做得到的日常趋势雷达。

---

## 参考资料

- 免费 MCP 仓库: https://github.com/purahmanian/google-trends-mcp
- 收费多源 MCP（搭配阅读）: [Google Search Trends MCP 实战](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/) · [apify.com/trendsmcp](https://apify.com/trendsmcp/google-search-trends-mcp)
- MCP 协议: https://modelcontextprotocol.io

<!--EN-->

> **Repo**: [github.com/purahmanian/google-trends-mcp](https://github.com/purahmanian/google-trends-mcp) · MIT · TypeScript
> **Install**: `claude mcp add google-trends -- npx -y google-trends-mcp` · **No API key**
> **Source**: Google Trends official endpoints (real 0–100 values, not estimates) · **Rate**: a few req/min
> **Companion read**: the paid multi-source MCP → [Google Search Trends MCP guide](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/)

---

## 1. Why write up "the free one" specifically

Last time we covered [TrendsMCP](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/) — 25+ sources, cross-validation, powerful, but **paid** (free tier is just 100 req/mo), and its values are "normalized **proprietary estimates**".

For a small studio or a mom-and-pop company, 100 req/mo runs dry after a few serious multi-source analyses. You need a workhorse radar you can **run every day without flinching.**

`purahmanian/google-trends-mcp` fills exactly that slot. It's **perfectly complementary** to the paid one:

| Dimension | Free MCP (this post) | Paid TrendsMCP (last post) |
|-----------|---------------------|---------------------------|
| Sources | **Google only** (search/board/region) | 25+ (YouTube/TikTok/Reddit/Amazon…) |
| Data nature | **Google official ground truth** 0–100 | normalized **proprietary estimates** |
| Cost | **Free** (MIT) | 100 free/mo, then paid |
| Usage | Pace it, effectively unlimited | Precious quota, spend sparingly |
| API key | **None** | Required |
| Regional drill-down | **Yes** (`interest_by_region`) | Weak |
| Stability | Unofficial endpoints, may be throttled | Hosted service, steadier |

The pairing philosophy in one line:

> **Free MCP = the daily "wide net" workhorse (official values, run daily); Paid MCP = the "precision confirm" finisher (multi-source, spend sparingly).**

---

## 2. What the free MCP offers

An MIT-licensed TypeScript MCP server hitting Google Trends' official endpoints, **no API key**. Five tools:

| Tool | Function | Key params |
|------|----------|-----------|
| `interest_over_time` | Weekly interest (0–100) for up to 5 terms | `terms`, `timeframe` (e.g. `today 5-y`) |
| `compare_terms` | Normalized comparison of 2–5 terms, winner callout | `terms` |
| `related_queries` | **Top + rising** related searches for a term | `term` |
| `trending_now` | Today's trending searches for a country | `country` / geo code |
| `interest_by_region` | Regional breakdown of interest | `term`, region scope |

Two capabilities that differ from the paid version:

- **`related_queries` "rising"** = Google's official "rising related searches" for free — a goldmine for topics and breakout discovery.
- **`interest_by_region`** = where a term is hottest by province/state/city. **A must-have for local small businesses** — and the paid multi-source MCP is actually weak here.

⚠️ Honest note: it rides Google's **unofficial endpoints**; Google can change structure or throttle anytime. **A few requests per minute** is safe; on HTTP 429, wait 2–5 minutes. Not enterprise SLA, but plenty for daily capture.

---

## 3. One-line install (really)

**Claude Code (recommended):**

```bash
claude mcp add google-trends -- npx -y google-trends-mcp
```

**Claude Desktop** — edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-trends": {
      "command": "npx",
      "args": ["-y", "google-trends-mcp"]
    }
  }
}
```

**Cursor / Codex:** add the same `npx -y google-trends-mcp` to `~/.codex/config.toml`.

No key, no signup, no quota page. Restart and verify: *"Use google-trends to pull 12 months of interest for 'City Walk' and show rising related queries."*

If you also installed the paid MCP from last post, **run both at once** — the AI picks which to use per your instruction. That's the physical basis of the dual-MCP pairing.

---

## 4. A daily trend-capture pipeline for small studios (dual-MCP)

This stitches both MCPs' strengths together, built for **small teams with no dedicated analyst but a constant need to produce content / find products.** Core rule: **never touch paid quota when free will do — spend paid only at the moment you're about to bet.**

### Stage 1 · Wide net (free MCP, daily)

1. `trending_now` (your country) → today's board.
2. For your niche's big terms, `related_queries` → take **rising** long-tails.
3. On candidates, `interest_over_time` (`today 3-m` / `today 12-m`) → is the curve **lifting off** (still rising, not peaked)?

**Prompt:**

> "Using google-trends: ① trending_now for the US; ② related_queries 'rising' for 'camping', 'cycling', 'pickleball'; ③ interest_over_time (3-m) on all rising terms, keep only those still climbing. Give me a candidate list."

### Stage 2 · Regional drill-down (free MCP, for local business)

Small companies often run **regional businesses.** Use `interest_by_region`:

**Prompt:**

> "Use interest_by_region for 'camping gear' across US states; give me the top 5. If I run local ads/events, which cities first?"

This is the free MCP's exclusive value — the paid one can't do it well.

### Stage 3 · Precision validation (paid MCP, spend quota only here)

Only the **few candidates you actually want to bet on** get the paid multi-source cross-check — confirming the demand isn't a Google-only spike but rises across YouTube/TikTok/Reddit/Amazon too.

**Prompt:**

> "Candidates [A, B] — I plan to invest in content/products. Use the paid trends-mcp to validate across YouTube, TikTok, Reddit, Amazon: are they rising in sync? Only multi-source-confirmed ones are worth betting on."

> 💡 **The money-saver**: Stages 1–2 may run dozens of queries (all free), but paid MCP fires only 1–2 times at the end. 100 free/mo covers dozens of real candidates — enough for a small studio.

### Stage 4 · Produce the analysis article (AI writes it)

Data's already in context — let it write:

**Prompt:**

> "From the free-MCP curves + regional data + paid-MCP multi-source validation, write an 800-word trend analysis: what the trend is, how fast it's rising, hottest regions, whether sources resonate, and 3 actionable moves for our studio (topic / product / ad)."

---

## 5. Freeze it into a "Daily Trend Brief" agent

What small studios lack most is "someone watching trends daily." Freeze this dual-MCP flow into a scheduled Claude Code agent that **runs every morning:**

```
Daily 09:00:
  [Free MCP]
    1. trending_now → board
    2. my 3 niche terms → related_queries(rising)
    3. candidates interest_over_time → keep lifting-off only
    4. interest_by_region → tag hot regions per candidate
  [Paid MCP, Top 3 only]
    5. multi-source cross-check → real trend / one-hit spike
  [Output]
    6. AI writes "Today's Trend Brief": candidates + regions + verdict + moves
  → pushed to studio chat / my phone
```

Cost math: the free part is **zero**; the paid part touches only Top-3 candidates, ~3–9 req/day, ~90–270/mo — weekdays-only on strongest candidates, **the 100 free/mo may even suffice**; upgrade to the $19 Starter only if needed. A "daily analyst" watching the whole web, capped at $0–20.

---

## 6. Which one when: a decision table

| Your need | Which MCP |
|-----------|-----------|
| Daily board scan, find rising long-tails | Free (`trending_now` + `related_queries` rising) |
| Is a term lifting off? | Free (`interest_over_time`) |
| Where is it hottest (local business)? | **Free-only** (`interest_by_region`) |
| Need Google official ground truth, no estimates | **Free-only** |
| Confirm multi-source resonance, avoid one-hit spikes | **Paid-only** (YouTube/TikTok/Reddit/Amazon…) |
| Final check before a big bet | Paid |
| Want endpoint stability, enterprise-grade | Paid (hosted) |

---

## 7. Boundaries & honesty

- **Google only**: the free MCP can't see independent TikTok/Reddit/Amazon signals — exactly why the paid one complements it.
- **Unofficial endpoints**: Google may throttle or change structure; author says "usually a URL/param tweak fixes it", but no SLA.
- **Rate limits**: a few per minute; don't hammer it; on 429, wait a few minutes.
- **Free ≠ zero maintenance**: you may need to bump the npm package version when endpoints shift.

Still, for most small studios, this "**free base + paid finisher**" combo buys, at the lowest possible cost, a pair of eyes on the whole web's trends. Trend capture was never a big-company privilege — now a two-person team, with one `npx` line plus at most $20/mo, owns a daily trend radar that used to require a full-time analyst.

---

## References

- Free MCP repo: https://github.com/purahmanian/google-trends-mcp
- Paid multi-source MCP (companion read): [Google Search Trends MCP guide](https://blog.mushroom.cv/blog/google-search-trends-mcp-guide/) · [apify.com/trendsmcp](https://apify.com/trendsmcp/google-search-trends-mcp)
- MCP protocol: https://modelcontextprotocol.io

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
