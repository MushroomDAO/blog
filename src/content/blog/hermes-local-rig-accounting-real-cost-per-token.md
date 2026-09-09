---
title: "本地跑大模型真的更便宜吗？这个插件把每 100 万 token 的成本算到了 0.62 美元"
titleEn: "Is Local LLM Inference Actually Cheaper? This Plugin Prices It at $0.62 per Million Tokens"
description: "本地推理不是免费的——电费、硬件折旧、机会成本都是真金白银。hermes-local-rig-accounting 是一个 Hermes Agent 插件，用一套可审计的公式把这些隐性成本折算成「每百万 token 多少钱」，并直接和云 API 报价放在一起对比。示例配置下算出 0.62 美元/M tokens，全部数据留在本地，无遥测。"
descriptionEn: "Local inference isn't free — electricity, hardware depreciation and opportunity cost are all real money. hermes-local-rig-accounting is a Hermes Agent plugin that folds those hidden costs into a single auditable number: dollars per million tokens. Its worked example lands at $0.62/M tokens. All cost data stays on your machine, no telemetry."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Tech-News"
tags: ["本地推理", "成本核算", "local-first", "开源", "Hermes Agent", "LLM", "电费", "硬件折旧"]
heroImage: "../../assets/images/hermes-local-rig-accounting-real-cost-per-token-banner.jpg"
---

> 📌 项目地址：https://github.com/GumbyEnder/hermes-local-rig-accounting
> 协议：MIT ｜ 语言：Python ｜ Star：24（2026-09-09）

## 一句话结论

**如果你正在用"省钱"说服自己买一台本地推理机，这个插件会给你一个不太舒服但很有用的数字。**

它做的事很简单：把你机器的硬件折旧和电费，除以实测出来的 token 吞吐量，得到一个可以直接和 OpenAI、Anthropic 报价放在同一行比较的单价。作者给的示例配置算下来是 **0.62 美元 / 百万 token**。

## 为什么这件事值得单独做一个插件

"本地推理是免费的"是个很容易脱口而出的说法，因为**花钱的时刻和用模型的时刻是分开的**。

你买显卡的时候刷了一次卡，之后每个月的电费混在家庭账单里，没有任何一个界面会在你按下回车时跳出来说"这次回答花了你 0.003 美元"。而云 API 恰恰相反：每一次调用都在账单上留下一行。

这种**成本可见性的不对称**，会系统性地让人高估本地方案的经济性。

这个插件补的就是这块可见性。它挂在 Hermes Agent 的三个钩子上：

| 钩子 | 干什么 |
|---|---|
| `post_api_request` | 统计本地 provider 返回的 token 数 |
| `on_session_start` | 重置本次会话的累加器 |
| `on_session_finalize` | 把累计推理小时数落盘 |

关键设计：**只统计本地 provider**（localhost、lmstudio、ollama、vllm 等），云 API 调用直接忽略。这样两边的账不会混在一起，你才能真的比较。

## 成本模型：三行公式，可审计

作者没有把公式藏起来，README 里直接给了：

| 成本项 | 公式 |
|---|---|
| **折旧** | `GPU 成本 ÷ (使用年限 × 8766 小时)`，按**实际推理小时**计 |
| **电费** | `(平均功耗瓦数 ÷ 1000) × 每度电价`，按小时计 |
| **每 token** | `每小时总成本 ÷ (TPS × 3600) × 1,000,000` = 每百万 token 单价 |

这里有个容易被忽略的细节：**折旧是按实际推理小时摊，不是按自然时间摊**。也就是说，如果你的机器一天只跑 1 小时推理，那这 1 小时要背的折旧，是"三年总折旧 ÷ 三年总小时数"——机器闲着的时间不算在推理成本里。

这个选择是有争议的。反过来算（按自然日历摊销）会得出高得多的单价，因为一台一天只用 1 小时的机器，剩下 23 小时的折旧也是真实发生的。作者选了对本地方案更有利的那种算法，看的时候心里要有数。

### 作者给的算例

| 参数 | 取值 |
|---|---|
| GPU 成本 | $1,500 |
| 使用年限 | 3 年（26,298 小时）|
| 功耗 | 450W @ $0.12/kWh |
| 实测 TPS | 50 |
| **折旧** | $0.057/小时 |
| **电费** | $0.054/小时 |
| **合计** | $0.111/小时 |
| **单价** | **$0.62 / 百万 token** |

有意思的是折旧和电费**几乎各占一半**。很多人只算电费，那就漏掉了一半的成本。

## 怎么用

安装（作为 Hermes 插件）：

```bash
hermes plugins install GumbyEnder/hermes-local-rig-accounting
```

配置写进 `config.yaml`：

```yaml
plugins:
  enabled:
    - local-rig-accounting

local_rig:
  hardware_cost_usd: 5000        # 整机成本
  lifespan_years: 3              # 预期使用年限
  gpu_only_cost_usd: 2500        # 可选：只用 GPU 成本作折旧基数
  avg_power_watts: 450           # 推理时平均功耗（W）
  electricity_rate_per_kwh: 0.15 # 你当地电价（$/kWh）
  auto_submit: true              # 跑完基准自动提交到社区榜单
```

不知道自己电价多少？它内置了一个区域电价库：

```yaml
local_rig:
  electricity_rate_per_kwh: auto
  electricity_region: Texas
```

常用命令：

```bash
/rig-benchmark qwen3.5-9b   # 先测吞吐——这步必须先做
/rig-summary                # 完整的成本面板
/rig-cost                   # 当前会话花了多少
/rig-rates Texas            # 查区域电价
/rig-submit qwen3.5-9b      # 提交到社区榜单
```

也可以直接作为 LLM 工具调用：`rig_cost`、`rig_summary`、`rig_benchmark`、`rig_rates`、`rig_submit`。

### 多机支持

有多台机器的话，配 `rigs:` 列表加 `hostname:`，插件按主机名自动选对应的配置：

```yaml
local_rig:
  hostname: desktop-server
  hardware_cost_usd: 5000
  avg_power_watts: 450
  electricity_rate_per_kwh: 0.15
  rigs:
    - label: laptop
      hostname: my-laptop
      hardware_cost_usd: 2000
      avg_power_watts: 120
      electricity_rate_per_kwh: 0.12
```

笔记本 120W vs 台式 450W，这个差距会直接反映在单价上——同一个模型在两台机器上的成本可能差好几倍。

## 几个要说清楚的限制

**第一，它只服务于 Hermes Agent。** 这不是一个通用的成本核算工具，是 Hermes 的插件，靠 Hermes 的钩子拿 token 数。你用别的框架就得自己想办法。

**第二，成本模型是简化的。** 它算了折旧和电费，没算：机箱风扇/空调的额外制冷开销、网络和存储成本、你自己花在维护上的时间。最后这项在个人场景里往往是最大的一块——但它确实很难量化，不算也说得过去。

**第三，"机会成本"在 README 的开场白里出现了，但公式里没有。** 开头说"每个 token 都在消耗电力、硬件折旧和机会成本"，实际的三行公式里只有前两项。这不是错，只是宣传语和实现之间有个小落差。

**第四，24 个 Star。** 这是个很新的小项目（2026 年 4 月建库，9 月还在更新），不是经过大规模验证的成熟工具。当成一个**思路**来看比当成一个**结论**来看更合适——公式是透明的，你完全可以照着自己算一遍。

## 它真正的价值：把决策变成可讨论的

我认为这个插件最有用的地方不是那个 0.62 美元，而是**它把一个原本靠感觉的判断变成了一个可以吵架的数字**。

当你说"本地更便宜"的时候，对方可以问你：按几年折旧？电价多少？实测 TPS 是多少？只算 GPU 还是算整机？——这些问题现在都有具体的位置可以填，谁的假设不合理，一眼就能看出来。

对个体开发者和中小组织来说，这正是选型时最缺的东西：不是一个"应该选哪个"的答案，而是**一套能把自己的实际情况代进去的算法**。

顺带一提，它还内置了社区榜单提交功能（`auto_submit: true` 或手动 `/rig-submit`），提交的是基准数据而不是你的成本参数。README 明确写了：**所有成本数据留在本地，无外部调用，无遥测**。这一点对 local-first 的用户很关键——一个算你花了多少钱的工具，本身不应该把你的账本传出去。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/GumbyEnder/hermes-local-rig-accounting
> License: MIT ｜ Language: Python ｜ Stars: 24 (2026-09-09)

## The Short Version

**If you're using "it's cheaper" to justify buying a local inference rig, this plugin will hand you a slightly uncomfortable but genuinely useful number.**

What it does is simple: divide your hardware depreciation plus electricity by your measured token throughput, producing a unit price you can put on the same line as OpenAI's or Anthropic's rate card. The author's worked example lands at **$0.62 per million tokens**.

## Why This Needs a Plugin at All

"Local inference is free" is an easy thing to say, because **the moment you spend the money and the moment you use the model are separated**.

You swiped a card once when you bought the GPU. Since then the electricity has been folded into a household bill, and no interface anywhere pops up when you hit enter to say "that answer cost you $0.003." Cloud APIs are the exact opposite: every call leaves a line on an invoice.

That **asymmetry in cost visibility** systematically inflates how economical the local option feels.

This plugin closes that gap. It hangs off three Hermes Agent hooks:

| Hook | What it does |
|---|---|
| `post_api_request` | Counts tokens returned by local providers |
| `on_session_start` | Resets the per-session accumulators |
| `on_session_finalize` | Persists cumulative inference hours |

The key design decision: **only local providers are tracked** (localhost, lmstudio, ollama, vllm, and so on). Cloud API calls are ignored outright, so the two ledgers never blur together and a comparison stays meaningful.

## The Cost Model: Three Formulas, All Auditable

The author doesn't hide the math — it's right there in the README:

| Component | Formula |
|---|---|
| **Depreciation** | `gpu_only_cost / (lifespan_years × 8766 hrs)` per **actual inference hour** |
| **Energy** | `(avg_power_watts / 1000) × electricity_rate_per_kwh` per hour |
| **Per-token** | `total_hourly_cost / (TPS × 3600) × 1,000,000` = $/M tokens |

One detail that's easy to skim past: **depreciation is amortized over actual inference hours, not calendar time**. If your machine runs inference one hour a day, that hour carries "three years of depreciation ÷ three years of hours" — the idle time isn't charged to inference.

That choice is debatable. Amortizing over the calendar instead yields a much higher unit price, because the other 23 hours of depreciation on a machine you use one hour a day are just as real. The author picked the accounting more favorable to local. Know that going in.

### The Author's Worked Example

| Parameter | Value |
|---|---|
| GPU cost | $1,500 |
| Lifespan | 3 years (26,298 hrs) |
| Power | 450W @ $0.12/kWh |
| Measured TPS | 50 |
| **Depreciation** | $0.057/hr |
| **Energy** | $0.054/hr |
| **Total** | $0.111/hr |
| **Unit cost** | **$0.62/M tokens** |

Note that depreciation and electricity come out **almost exactly equal**. Plenty of people only count the power bill — that misses half the cost.

## Using It

Install as a Hermes plugin:

```bash
hermes plugins install GumbyEnder/hermes-local-rig-accounting
```

Configure in `config.yaml`:

```yaml
plugins:
  enabled:
    - local-rig-accounting

local_rig:
  hardware_cost_usd: 5000        # whole-rig cost
  lifespan_years: 3              # expected useful life
  gpu_only_cost_usd: 2500        # optional: use GPU cost as the depreciation base
  avg_power_watts: 450           # average draw during inference (W)
  electricity_rate_per_kwh: 0.15 # your local rate ($/kWh)
  auto_submit: true              # auto-submit benchmarks to the community leaderboard
```

Don't know your rate? There's a built-in regional lookup:

```yaml
local_rig:
  electricity_rate_per_kwh: auto
  electricity_region: Texas
```

The commands:

```bash
/rig-benchmark qwen3.5-9b   # measure throughput first — this step is mandatory
/rig-summary                # full economics dashboard
/rig-cost                   # what this session has cost so far
/rig-rates Texas            # regional electricity lookup
/rig-submit qwen3.5-9b      # publish your benchmark
```

They're also exposed as LLM tools: `rig_cost`, `rig_summary`, `rig_benchmark`, `rig_rates`, `rig_submit`.

### Multiple Machines

Add a `rigs:` list with a `hostname:` per entry and the plugin auto-selects the matching profile:

```yaml
local_rig:
  hostname: desktop-server
  hardware_cost_usd: 5000
  avg_power_watts: 450
  electricity_rate_per_kwh: 0.15
  rigs:
    - label: laptop
      hostname: my-laptop
      hardware_cost_usd: 2000
      avg_power_watts: 120
      electricity_rate_per_kwh: 0.12
```

A 120W laptop versus a 450W desktop shows up directly in the unit price — the same model can cost several times more per token on one than the other.

## Limits Worth Stating Plainly

**One: it only serves Hermes Agent.** This is not a general-purpose cost tool; it's a plugin that gets its token counts from Hermes hooks. On any other framework you're on your own.

**Two: the model is deliberately simplified.** It counts depreciation and electricity. It does not count cooling overhead, network and storage, or the time you personally spend maintaining the thing. That last one is often the largest item in a personal setup — but it's genuinely hard to quantify, so leaving it out is defensible.

**Three: "opportunity cost" appears in the opening line but not in the formulas.** The README says every token costs "electricity, hardware depreciation, and opportunity cost," while the three formulas only cover the first two. Not wrong, just a small gap between the pitch and the implementation.

**Four: 24 stars.** This is a young, small project (repo created April 2026, still being updated in September), not a battle-tested tool. Treat it as **an approach** rather than **a verdict** — the formulas are transparent, and you can absolutely run the numbers yourself.

## What It's Actually Good For

The most valuable thing here isn't the $0.62. It's that **a judgment previously made on vibes is now a number people can argue about**.

When you claim "local is cheaper," someone can now ask: amortized over how many years? At what electricity rate? What measured TPS? GPU only or whole rig? Every one of those has a slot to fill in, and an unreasonable assumption becomes visible immediately.

For individuals and small organizations picking a stack, that's exactly what's usually missing: not an answer about which option to choose, but **a method you can plug your own situation into**.

Worth noting: it ships a community leaderboard submission feature (`auto_submit: true`, or a manual `/rig-submit`), which publishes benchmark data rather than your cost parameters. The README is explicit that **all cost data stays local — no external calls, no telemetry**. That matters for local-first users: a tool that calculates what you're spending shouldn't be shipping your ledger anywhere.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
