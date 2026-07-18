---
title: "用 Stock SDK 建立自己的股票信息源：从命令行到 AI 看盘"
titleEn: "Build Your Own Stock Data Feed with Stock SDK: From CLI to AI-Powered Dashboard"
description: "Stock SDK（1649★，ISC）是一个零依赖的 JavaScript/TypeScript 股票行情库，无需 Python、无需后端，直接在浏览器或 Node.js 里拉 A 股/港股/美股/公募基金数据。本文带你从一条命令行开始，一步步建立属于自己的股票信息源，并接入 Claude/Cursor 等 AI 工具。"
descriptionEn: "Stock SDK (1649★, ISC) is a zero-dependency JavaScript/TypeScript stock data library. No Python, no backend server — pull A-share, HK, US stocks, and mutual fund data directly in browser or Node.js. This guide takes you from a single CLI command to building your own personalized stock feed and connecting it to Claude/Cursor."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-Experiment"
tags: ["股票", "JavaScript", "TypeScript", "MCP", "AI工具", "数据可视化", "量化", "信息源"]
heroImage: "../../assets/images/stock-sdk-personal-stock-feed-guide-banner.jpg"
---

大多数人看股票行情，要么依赖东方财富/同花顺 App，要么打开各种财经网站，信息散落各处，而且广告满天飞。

如果你懂一点点 JavaScript，或者愿意花 15 分钟跑几条命令，完全可以建一个属于自己的股票信息源——想看什么就看什么，可以接 AI，可以做自动提醒，还能连进你自己的工具链。

**Stock SDK** 就是做这件事的工具：一个专门为前端和 Node.js 设计的股票行情 SDK，零依赖，A股/港股/美股/公募基金全覆盖，自带命令行工具和 MCP server。

GitHub: [chengzuopeng/stock-sdk](https://github.com/chengzuopeng/stock-sdk) | 1649★ | TypeScript | ISC 协议

---

## 它解决的核心问题

大多数股票数据工具是 **Python 生态**。`akshare`、`tushare`、`baostock`——对前端工程师和 JavaScript 用户来说，这些工具要额外搭 Python 环境，要跑后端服务，门槛不低。

Stock SDK 的定位很清楚：

> 让 JavaScript 用户，用最熟悉的方式，直接取到股票数据。

- **无需 Python**，无需后端服务
- **浏览器 + Node.js** 双端运行
- **零依赖**，安装体积极小
- 自带 **CLI 命令行**（终端直接取行情）
- 自带 **MCP server**（一行接入 Claude/Cursor/Codex）

---

## 第一步：零代码上手——命令行取行情

不写代码也能用。安装 Node.js（18+）之后，用 `npx` 直接运行：

```bash
# 取贵州茅台的实时行情
npx stock-sdk quote 600519

# 同时看 A 股 + 港股 + 美股
npx stock-sdk quote 600519 00700 AAPL

# 周 K 线（最近 30 根）
npx stock-sdk kline 600519 --period weekly --limit 30

# 带 MACD + 均线的 K 线
npx stock-sdk indicators 600519 --ma 5,10,20 --macd

# 搜索关键词
npx stock-sdk search 茅台
```

输出默认是 JSON，加 `--format table` 变成表格，加 `--pretty` 格式化。

**适合场景：** 临时查一下股价，不想打开 App；或者在脚本里取数据做自动化。

---

## 第二步：建立自己的自选股监控脚本

15 分钟建一个「每天早上发给自己的行情播报」。

### 安装

```bash
npm install stock-sdk
```

### 最简脚本：查看自选股

```ts
import { StockSDK } from 'stock-sdk';

const sdk = new StockSDK();

// 你的自选股列表（A 股/港股/美股写法都兼容）
const watchlist = ['sh600519', 'sz000858', 'hk00700', 'AAPL', 'sh000001'];

const quotes = await sdk.quotes.cnSimple(['sh600519', 'sz000858', 'sh000001']);

quotes.forEach((q) => {
  const sign = q.changePercent >= 0 ? '▲' : '▼';
  console.log(`${q.name.padEnd(8)} ${q.price}  ${sign}${Math.abs(q.changePercent).toFixed(2)}%`);
});
```

输出大概长这样：

```
贵州茅台     1680.00  ▲1.23%
五粮液       158.50   ▼0.45%
上证指数     3321.08  ▲0.67%
```

### 进一步：加上港股和美股

```ts
const [aShares, hkShares, usShares] = await Promise.all([
  sdk.quotes.cnSimple(['sh600519', 'sz000858']),
  sdk.quotes.hk(['00700', '09988']),
  sdk.quotes.us(['AAPL', 'NVDA']),
]);

// 汇总输出
[...aShares, ...hkShares, ...usShares].forEach((q) => {
  console.log(`${q.name}: ${q.price} (${q.changePercent}%)`);
});
```

---

## 第三步：接入 Claude/Cursor 等 AI 工具（MCP）

这是 Stock SDK 最亮眼的功能之一。v2 内置了零依赖的 **MCP server**，不需要额外安装任何依赖，一条命令启动：

```bash
npx stock-sdk mcp
```

然后在你的 Claude Desktop / Cursor / Codex 等工具的配置文件里加：

```json
{
  "mcpServers": {
    "stock-sdk": {
      "command": "npx",
      "args": ["-y", "stock-sdk", "mcp"]
    }
  }
}
```

配置完成后，你可以直接在 Claude 对话框里问：

```
帮我看一下贵州茅台今天的走势，MACD 有没有金叉信号？
```

Claude 会自动调用 Stock SDK 的 MCP 工具拉取数据并分析。这就是「把 AI 接上真实市场数据」。

**MCP 工具范围控制：**

```bash
# 只开核心工具（默认）
STOCK_SDK_MCP_TOOLS=core npx stock-sdk mcp

# 开全部工具（包括龙虎榜、北向资金、大宗交易等）
STOCK_SDK_MCP_TOOLS=full npx stock-sdk mcp
```

---

## 第四步：筛选股票——链式选股器

Stock SDK 内置了一个纯本地运行的链式选股器，不走网络，速度很快：

```ts
import { StockSDK } from 'stock-sdk';
import { screen } from 'stock-sdk/screener';

const sdk = new StockSDK();

// 拉全市场 A 股行情（5000+ 只，内置并发控制）
const allQuotes = await sdk.batch.cn({ concurrency: 5 });

// 链式筛选：PE < 20，涨幅 > 2%，按成交额排序，取前 20
const picks = screen(allQuotes)
  .where((q) => q.pe != null && q.pe < 20)
  .where((q) => q.changePercent > 2)
  .sortBy((q) => q.amount, 'desc')
  .top(20);

console.log('今日符合条件的股票：');
picks.forEach((q) => {
  console.log(`${q.name} (${q.code}): ${q.price} PE=${q.pe} 涨幅=${q.changePercent}%`);
});
```

这相当于自己做了一个简单的量化选股器——条件完全自定义，数据本地计算，没有平台会员墙。

---

## 第五步：技术指标 + 信号识别

```ts
import { StockSDK } from 'stock-sdk';
import { calcSignals } from 'stock-sdk/signals';

const sdk = new StockSDK();

// 获取 K 线 + 技术指标（一次调用，返回带指标的 K 线）
const kline = await sdk.kline.withIndicators('600519', {
  period: 'daily',
  indicators: {
    ma: { periods: [5, 10, 20] },
    macd: {},
    kdj: {},
    rsi: {},
  },
});

// 识别信号：金叉/死叉/超买/超卖等
const signals = calcSignals(kline, {
  ma: { fast: 5, slow: 20 },
  rsi: { overbought: 70, oversold: 30 },
});

// 最近的信号
const recent = signals.filter((s) => s.type !== 'hold').slice(-5);
recent.forEach((s) => {
  console.log(`${s.date}: [${s.type}] ${s.indicators.join(', ')}`);
});
```

支持的技术指标：MA / MACD / BOLL / KDJ / RSI / WR / BIAS / CCI / ATR / OBV / ROC / DMI / SAR / KC，共 14 种。

---

## 第六步：定时行情播报（Node.js 脚本 + cron）

把上面的脚本保存成 `daily-report.mjs`，然后用系统定时任务（cron）每天开盘前自动运行：

```js
// daily-report.mjs
import { StockSDK } from 'stock-sdk';

const sdk = new StockSDK();
const watchlist = ['sh600519', 'sz000858', 'sh000001', 'hk00700'];
const quotes = await sdk.quotes.cnSimple(watchlist.filter(s => s.startsWith('sh') || s.startsWith('sz')));
const hkQuotes = await sdk.quotes.hk(['00700']);

[...quotes, ...hkQuotes].forEach(q => {
  const arrow = q.changePercent >= 0 ? '↑' : '↓';
  console.log(`${q.name}: ¥${q.price} ${arrow}${q.changePercent.toFixed(2)}%`);
});
```

```bash
# crontab -e 加入（每天早上 9:25 A 股开盘前运行）
25 9 * * 1-5 node /path/to/daily-report.mjs >> /tmp/stock-report.log
```

---

## 覆盖范围：能用和不能用的

用之前最好先看这张表：

| 能力 | A 股 | 港股 | 美股 | 基金 |
|------|:----:|:----:|:----:|:----:|
| 实时行情 | ✅ | ✅ | ✅ | ✅ |
| 历史 K 线（日/周/月）| ✅ | ✅ | ✅ | 场内 ETF |
| 分钟 K 线 | ✅ | ✅ | ✅ | 场内 ETF |
| 技术指标 | ✅ | ✅ | ✅ | — |
| 选股器 | ✅ | ✅ | ✅ | — |
| 资金流向 | ✅ | ❌ | ❌ | — |
| 北向/南向 | ✅ | ✅ | — | — |
| 龙虎榜 | ✅ | — | — | — |
| 涨停板 | ✅ | — | — | — |
| 筹码分布 | ✅ | ✅ | ✅ | — |

**重要提醒**：数据来自东方财富/腾讯财经等公开接口，有数十秒到数分钟延迟，**不适合高频交易或实盘决策**。适合做信息整合、策略研究、学习Demo，不是实时撮合系统。

---

## 三种信息源建设路线

根据你的需求和技术背景，有三条路可以走：

### 路线 A：纯命令行（0 代码）

```bash
npx stock-sdk quote 600519 00700 AAPL
```

每天开盘后在终端里跑一次，或者接个 cron 自动跑。适合：**不想写代码，只想快速查数据**。

### 路线 B：Node.js 脚本（基础 JS 能力）

写一个 `.mjs` 脚本，定时运行，输出到文件、发邮件、或推送到 Telegram/企业微信。适合：**有基本 JavaScript 能力，想定制信息源格式**。

### 路线 C：接入 AI（MCP）

配置 MCP server，直接在 Claude 或 Cursor 里问行情。适合：**已经在用 Claude Code 或 Cursor，想让 AI 有实时股票数据**。

---

## 安装和资源

```bash
npm install stock-sdk
```

- [GitHub：chengzuopeng/stock-sdk](https://github.com/chengzuopeng/stock-sdk) — 1649★，ISC 协议
- [官方文档](https://stock-sdk.linkdiary.cn) — 完整 API + CLI/MCP 指南 + 在线 Playground
- [Stock Dashboard 演示站](https://chengzuopeng.github.io/stock-dashboard/) — 基于 stock-sdk 搭建的示例大盘

© 2026 Author: Mycelium Protocol

<!--EN-->

## Build Your Own Stock Data Feed with Stock SDK: From CLI to AI-Powered Dashboard

Most people check stock prices through dedicated apps or financial websites — fragmented information, full of ads, and no way to integrate it into your own workflow.

If you know a bit of JavaScript — or are willing to run a few commands — you can build your own stock data feed in about 15 minutes. Show exactly what you want, hook it into AI tools, set up automated alerts, and keep it all inside your own toolchain.

**Stock SDK** (1649★, ISC) is the tool for this: a zero-dependency JavaScript/TypeScript stock data library designed for frontend and Node.js. No Python, no backend server required. A-shares, HK stocks, US stocks, and mutual funds all covered. Built-in CLI and MCP server.

GitHub: [chengzuopeng/stock-sdk](https://github.com/chengzuopeng/stock-sdk)

---

### Why It Matters

Most stock data tooling is **Python-only** — `akshare`, `tushare`, `baostock`. For JavaScript developers, that means spinning up a Python environment and running a separate backend service.

Stock SDK's goal: let JavaScript users pull stock data the same way they pull anything else.

- Zero dependencies, browser + Node.js 18+
- A-share / HK / US stocks / mutual funds in one SDK
- Built-in CLI — `npx stock-sdk quote 600519` in your terminal
- Built-in MCP server — one config line to hook into Claude/Cursor

**Important caveat**: data comes from public endpoints (Eastmoney, Tencent Finance). Delays of seconds to minutes are normal. Not suitable for high-frequency or live trading decisions. Great for research, learning, dashboards, and AI tool integrations.

---

### Step 1: CLI — No Code Required

```bash
# Real-time quote
npx stock-sdk quote 600519 00700 AAPL

# Weekly K-line
npx stock-sdk kline 600519 --period weekly --limit 30

# K-line + indicators
npx stock-sdk indicators 600519 --ma 5,10,20 --macd

# Search by keyword
npx stock-sdk search 茅台
```

---

### Step 2: Node.js Watchlist Script

```bash
npm install stock-sdk
```

```ts
import { StockSDK } from 'stock-sdk';

const sdk = new StockSDK();

const quotes = await sdk.quotes.cnSimple(['sh600519', 'sz000858', 'sh000001']);
quotes.forEach((q) => {
  const sign = q.changePercent >= 0 ? '▲' : '▼';
  console.log(`${q.name}: ${q.price}  ${sign}${Math.abs(q.changePercent).toFixed(2)}%`);
});
```

Add HK and US stocks:

```ts
const [a, hk, us] = await Promise.all([
  sdk.quotes.cnSimple(['sh600519']),
  sdk.quotes.hk(['00700']),
  sdk.quotes.us(['AAPL', 'NVDA']),
]);
```

---

### Step 3: Connect to AI via MCP

Start the built-in MCP server:

```bash
npx stock-sdk mcp
```

Add to your Claude Desktop / Cursor config:

```json
{
  "mcpServers": {
    "stock-sdk": {
      "command": "npx",
      "args": ["-y", "stock-sdk", "mcp"]
    }
  }
}
```

Now ask Claude directly: *"What's the MACD signal on Kweichow Moutai today?"* — Claude pulls live data and answers.

---

### Step 4: Screener + Signals

```ts
import { screen } from 'stock-sdk/screener';
import { calcSignals } from 'stock-sdk/signals';

// Full market scan — all 5000+ A-shares
const all = await sdk.batch.cn({ concurrency: 5 });

// Filter: PE < 20, gain > 2%, sort by volume
const picks = screen(all)
  .where((q) => q.pe != null && q.pe < 20)
  .where((q) => q.changePercent > 2)
  .sortBy((q) => q.amount, 'desc')
  .top(20);

// Signal detection on K-line
const kline = await sdk.kline.withIndicators('600519', {
  period: 'daily',
  indicators: { ma: { periods: [5, 20] }, macd: {}, rsi: {} },
});
const signals = calcSignals(kline, { ma: { fast: 5, slow: 20 }, rsi: {} });
```

14 indicators supported: MA / MACD / BOLL / KDJ / RSI / WR / BIAS / CCI / ATR / OBV / ROC / DMI / SAR / KC.

---

### Three Build Paths

| Path | Requirement | Best For |
|------|-------------|----------|
| **A: CLI only** | Just Node.js installed | Quick lookups, no code |
| **B: Node.js script** | Basic JavaScript | Custom data feed, automated alerts |
| **C: AI + MCP** | Claude/Cursor configured | AI with real market data |

---

### Resources

- [GitHub: chengzuopeng/stock-sdk](https://github.com/chengzuopeng/stock-sdk) — 1649★, ISC
- [Official docs](https://stock-sdk.linkdiary.cn) — full API + CLI/MCP guide + Playground
- [Stock Dashboard demo](https://chengzuopeng.github.io/stock-dashboard/)

© 2026 Author: Mycelium Protocol
