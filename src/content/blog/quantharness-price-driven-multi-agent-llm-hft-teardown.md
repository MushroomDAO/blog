---
title: "QuantHarness：四专用 Agent 做 K 线技术分析，LLM 看图出信号"
titleEn: "QuantHarness: Four Specialized Agents for Chart Analysis, LLM Reads Candles to Output Signals"
description: "Y-Research-SBU/QuantHarness，2869 星，MIT，Python + LangGraph。把技术分析分解给四个专用 Agent（Indicator/Pattern/Trend/Decision），每个 Agent 调用视觉 LLM 读取图表而不是解析数值。arXiv 2509.09995，在 9 个金融标的上测试了 1 小时和 4 小时周期。核心架构思路有参考价值，但「高频交易」标签对不上——yfinance 延迟数据 + 小时级 K 线，和真实 HFT 的毫秒量级相差四到五个数量级。"
descriptionEn: "Y-Research-SBU/QuantHarness, 2869 stars, MIT, Python + LangGraph. Technical analysis decomposed into four specialized agents (Indicator/Pattern/Trend/Decision), each calling a vision LLM to read charts rather than parsing raw values. arXiv 2509.09995, tested on 9 instruments at 1-hour and 4-hour intervals. Solid multi-agent architecture, but the 'High-Frequency Trading' label doesn't hold: yfinance delayed data plus hourly candles is four to five orders of magnitude away from real HFT millisecond latency."
pubDate: 2026-09-30
heroImage: "../../assets/images/quantharness-price-driven-multi-agent-llm-hft-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["量化交易", "多Agent", "LangGraph", "技术分析", "开源拆解", "LLM应用"]
lang: "zh-CN"
wechatTitle: "QuantHarness：多Agent LLM量化分析拆解"
wechatDigest: "2869星MIT；四专用Agent(指标/形态/趋势/决策)；arXiv 2509.09995；叫HFT但跑的是小时级K线"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究，不构成任何投资建议。

---

## 先把「高频交易」这个标签放一边

仓库名叫 QuantHarness，论文副标题是「Price-Driven Multi-Agent LLMs for High-Frequency Trading」。读完 README 和 arXiv 2509.09995，实际跑的是 **1 小时和 4 小时 K 线**。

专业语境里，HFT（High-Frequency Trading，高频交易）指毫秒到微秒级的市场撮合——需要托管服务器（co-location）、FPGA 硬件、直连交易所的专用数据线路，延迟预算以微秒计量。用 yfinance 拉数据、用 LLM 读图表、出 1 小时信号，和这个定义差了四到五个数量级。

这不影响项目的实际价值。把标签换成「多 Agent LLM 技术分析框架」，它是一个思路清晰、架构完整的工程示范。

仓库：github.com/Y-Research-SBU/QuantHarness  
**Stars：2869 | Forks：619 | License：MIT | Paper：arXiv 2509.09995**

---

## 四个专用 Agent，各司其职

QuantHarness 的核心设计是把技术分析里的四个经典维度分给四个独立 Agent，每个 Agent 拿到原始行情数据后，先生成图表，再调用**视觉 LLM** 读图分析。

### Indicator Agent — 把 OHLC 转换成信号指标

对每一根新 K 线计算五个指标：

- **RSI**（Relative Strength Index）：动量强度，评估超买/超卖状态
- **MACD**（Moving Average Convergence Divergence）：均线收敛/发散程度
- **Stochastic Oscillator**：收盘价在近期价格区间内的位置
- 另外两个指标（Bollinger Bands、ATR 等变体）

输出：每根 K 线对应一组结构化指标值，作为后续 Agent 的输入之一。

### Pattern Agent — 读图识别形态

Pattern Agent 不直接解析数值，而是：

1. 画出近期价格走势图
2. 标注主要高点和低点
3. 对比常见技术形态库（头肩顶、双底、旗形整理等）
4. 输出最匹配形态的文字描述和置信度

这里用到了视觉 LLM——把生成的图表图片喂给模型，让模型「看图说话」，而不是写规则去匹配价格序列。

### Trend Agent — 分析趋势通道

绘制带趋势通道的 K 线图：在最近的高点上方和低点下方各画一条边界线，形成价格通道。输出：市场方向（上行/下行/横盘）、通道斜率、整理区间位置。

### Decision Agent — 合并四路信号，出具操作建议

汇总 Indicator + Pattern + Trend + Risk（风险评估）四个 Agent 的输出，给出结构化决策：

```
方向：LONG / SHORT
入场价：$XX,XXX
目标价：$XX,XXX
止损价：$XX,XXX
理由：[综合四路信号的文字说明]
```

---

## 视觉 LLM 是关键依赖

README 明确说明：**本系统要求使用支持图片输入的 LLM**。Indicator Agent 处理的是数值，但 Pattern Agent 和 Trend Agent 的核心分析靠的是把图表截图送给 LLM 看。

这个设计有实际意义：技术分析中的形态识别（「这是一个头肩顶吗？」）用纯数值规则非常难写，但视觉 LLM 处理这类「看图判断」反而自然。代价是推理延迟和 API 费用。

系统支持四家 LLM：

| 提供商 | 默认模型配置 |
|--------|------------|
| OpenAI | gpt-4o-mini（Agent）/ gpt-4o（图决策） |
| Anthropic | claude-haiku-4-5-20251001 |
| Qwen | qwen3-max / qwen3-vl-plus |
| MiniMax | MiniMax-M3（204K 上下文） |

---

## 30 根 K 线：工程上的权衡

系统设定每次分析取最近 **30 根 K 线**，README 描述这是「最优 LLM 分析精度」的经验值。

这个决定背后有两个张力：

- **太少**：LLM 看不到足够的形态上下文，容易误判
- **太多**：提示词图片面积变大，token 消耗增加，同时 LLM 在长上下文里识别细节的准确率会下降

30 根对于 1 小时 K 线 = 30 小时数据窗口，对于 4 小时 K 线 = 5 天数据窗口。这是一个合理的摆渡点，但「最优」的说法是工程经验，不是严格推导出的结论。

---

## LangGraph 编排，Flask 前端

整个多 Agent 流水线用 LangGraph 编排——每个 Agent 是图中的一个节点，状态在节点间传递：

```python
from trading_graph import TradingGraph

trading_graph = TradingGraph()
final_state = trading_graph.graph.invoke({
    "kline_data": your_dataframe_dict,
    "time_frame": "4hour",
    "stock_name": "BTC"
})

print(final_state.get("final_trade_decision"))
```

前端是 Flask Web 应用，数据源是 Yahoo Finance（yfinance），支持股票、加密货币、大宗商品、指数，时间周期从 1 分钟到日线。

---

## 论文声称的结果

arXiv 2509.09995 在九个金融标的（包括 BTC、纳斯达克期货）上做了测试，结论是 QuantHarness 在 1 小时和 4 小时周期上「一致优于基线方法，在多个评估指标上取得更高的预测准确率」。

几个需要注意的点：

**标的选取**：论文选了九个流动性较好的品种，选择本身可能存在对系统有利的偏向。

**基线对比**：对比的是「现有 LLM 金融系统」（TradingAgent、FINMEM 等），而这些系统本来就是为长周期投资设计的，用来对比 1 小时信号准确率并不算同类对比。

**回测 vs 实盘**：论文测的是预测方向准确率，没有接入实盘交易。真实交易还涉及滑点、手续费、流动性、持仓管理等变量。

**yfinance 数据**：Yahoo Finance 数据有延迟，适合研究和回测，不适合用于任何实时交易系统。

---

## 可以借鉴什么

撇开「HFT」标签，这个项目的工程设计有几个地方值得参考：

**专用 Agent 的分工思路**：把一个复杂任务拆分成 Indicator/Pattern/Trend/Risk 四个专用节点，各节点只做自己擅长的事，最后由 Decision Agent 综合。这是 LangGraph 多 Agent 架构的一个清晰实践。

**视觉 LLM 用于形态识别**：让 LLM「看图」来判断形态，而不是写数值规则，这在其他需要视觉推理的场景（文档解析、图表 QA、设计稿审查）同样适用。

**状态机设计**：`TradingGraph` 把 `kline_data`、`analysis_results`、`messages`、`time_frame`、`stock_name` 封进统一状态，在 LangGraph 节点间传递——这是处理多步推理任务时一种干净的状态管理方式。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 2,869 |
| Forks | 619 |
| License | MIT |
| Paper | arXiv 2509.09995 |
| 测试标的数 | 9 |
| 测试周期 | 1h / 4h K 线 |
| 分析窗口 | 30 根 K 线 |
| LLM 支持 | OpenAI / Anthropic / Qwen / MiniMax |
| 数据源 | Yahoo Finance (yfinance) |
| 编排框架 | LangChain + LangGraph |

---

## 综合判断

QuantHarness 是一个架构完整的多 Agent 技术分析框架，用视觉 LLM 处理图表分析是一个有意思的工程选择，LangGraph 多节点流水线的设计也值得参考。

用它作为技术研究工具、理解多 Agent 架构的具体实现——2869 星的热度有其道理。

但「高频交易」的标签是需要主动忽略的营销用词。yfinance 延迟数据 + LLM 推理延迟 + 无实盘接口，系统的实际定位是量化技术分析的研究原型，不是生产级交易系统。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。本文不构成任何投资建议。

---

<!--EN-->

## QuantHarness: Four Specialized Agents for Chart Analysis, LLM Reads Candles to Output Signals

> **Open source for learning only**: All projects discussed are from public repositories. This article does not constitute investment advice.

---

### First, Set the "High-Frequency Trading" Label Aside

The repo is named QuantHarness. The paper subtitle is "Price-Driven Multi-Agent LLMs for High-Frequency Trading." Reading through the README and arXiv 2509.09995, it actually runs on **1-hour and 4-hour candles**.

In professional context, HFT (High-Frequency Trading) means millisecond-to-microsecond market execution — requiring co-location servers, FPGA hardware, and direct exchange data feeds, with latency budgets measured in microseconds. Using yfinance for data, LLM chart reading, and hourly signals is four to five orders of magnitude away from that definition.

This doesn't undermine the project's actual value. Relabel it as "multi-agent LLM technical analysis framework" and it's a well-structured, architecturally coherent engineering reference.

Repo: github.com/Y-Research-SBU/QuantHarness  
**2,869 stars | 619 forks | MIT | Paper: arXiv 2509.09995**

---

### Four Specialized Agents, Each With a Role

QuantHarness decomposes technical analysis into four specialized agents. Each receives raw market data, generates a chart, then calls a **vision LLM** to read and interpret it.

**Indicator Agent** — Computes five technical indicators per K-line: RSI (momentum extremes), MACD (convergence-divergence dynamics), Stochastic Oscillator (closing price vs. recent range), plus two more. Output: structured signal metrics per candle.

**Pattern Agent** — Rather than parsing raw values, it:
1. Draws the recent price chart
2. Marks major highs and lows
3. Compares the shape against known patterns (head & shoulders, double bottom, flag consolidation, etc.)
4. Returns a plain-language description of the best match

Pattern recognition uses vision LLM — the generated chart image is fed to the model for visual interpretation, not rule-based number-crunching.

**Trend Agent** — Draws annotated K-line charts with fitted trend channels (upper and lower boundary lines tracing recent highs and lows). Outputs: market direction, channel slope, consolidation zones.

**Decision Agent** — Synthesizes Indicator + Pattern + Trend + Risk outputs into a structured trade directive:

```
Direction: LONG / SHORT
Entry: $XX,XXX
Target: $XX,XXX
Stop-loss: $XX,XXX
Rationale: [text grounded in all four agents' findings]
```

---

### Vision LLM Is the Key Dependency

The README is explicit: **this system requires a vision-capable LLM**. Pattern and Trend agents work by sending chart screenshots to the model for analysis.

This design choice has practical merit: identifying chart patterns from raw values (Is this a head-and-shoulders?) is notoriously hard to encode as numeric rules, but vision LLMs handle "look at this image and describe what you see" naturally. The trade-off is inference latency and API cost.

Four providers supported: OpenAI (gpt-4o), Anthropic (claude-haiku-4-5-20251001), Qwen (qwen3-vl-plus), MiniMax (MiniMax-M3, 204K context).

---

### The 30-Candle Window

The system analyzes the most recent **30 candlesticks** — described as optimal for LLM analysis accuracy. This is a practical balance: too few and there's insufficient context for pattern identification; too many and token costs rise while LLM accuracy on fine-grained details tends to fall.

30 candles at 1-hour = 30 hours of data. At 4-hour = 5 trading days. A reasonable empirical value, though "optimal" is an engineering heurism, not a rigorously derived conclusion.

---

### What the Paper Claims

arXiv 2509.09995 tested on nine instruments including Bitcoin and Nasdaq futures. The conclusion: QuantHarness "consistently outperforms baseline methods" at 1-hour and 4-hour intervals.

A few caveats worth flagging:

**Baseline selection**: The comparison is against TradingAgent and FINMEM — systems designed for long-horizon investment, not intraday analysis. Comparing directional accuracy at 1-hour intervals against a long-horizon system isn't an apples-to-apples benchmark.

**Backtesting only**: Predictive direction accuracy was measured; no live execution. Real trading adds slippage, fees, liquidity constraints, and position management.

**yfinance data**: Yahoo Finance data is delayed. Unsuitable for any real-time trading use.

---

### What's Worth Borrowing

Setting aside the HFT label, there are useful engineering patterns here:

**Specialized agent decomposition**: Splitting a complex analytical task into Indicator/Pattern/Trend/Risk nodes, each doing what it's specifically good at, with a Decision agent synthesizing them — this is a clean LangGraph multi-agent implementation.

**Vision LLM for pattern recognition**: Having the LLM "look at" a chart rather than encoding visual patterns as numeric rules applies to other domains too: document parsing, chart Q&A, design review.

**State machine design**: Encapsulating `kline_data`, `analysis_results`, `messages`, `time_frame`, and `stock_name` into a unified state passed between LangGraph nodes is a clean pattern for multi-step reasoning tasks.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 2,869 |
| Forks | 619 |
| License | MIT |
| Paper | arXiv 2509.09995 |
| Test instruments | 9 |
| Test intervals | 1h / 4h candles |
| Analysis window | 30 candles |
| LLM providers | OpenAI / Anthropic / Qwen / MiniMax |
| Data source | Yahoo Finance (yfinance) |
| Orchestration | LangChain + LangGraph |

---

### Verdict

QuantHarness is a structurally complete multi-agent technical analysis framework. Using vision LLM for chart interpretation is an interesting engineering choice; the LangGraph multi-node pipeline design is worth referencing.

As a research tool for understanding multi-agent architectures — the 2,869-star traction is warranted.

But the "HFT" label is marketing to consciously ignore. Delayed yfinance data + LLM inference latency + no live execution interface puts the actual positioning squarely in research prototype territory, not a production trading system.

---

> Open source for learning only. Verify license terms before commercial use. This article does not constitute investment advice.
