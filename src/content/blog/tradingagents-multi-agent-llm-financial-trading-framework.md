---
title: "TradingAgents：把交易公司搬进 AI——96k Stars 的多 Agent 金融交易框架"
titleEn: "tradingagents-multi-agent-llm-financial-trading-framework"
description: "TauricResearch 开源的多 Agent LLM 量化交易框架，96k+ stars，Apache 2.0。用 LangGraph 构建 7 种专职角色：基本面/情绪/新闻/技术分析师 + 多空研究员 + 交易员 + 风控/投资组合经理。支持 OpenAI/Claude/Gemini/DeepSeek/Kimi/Qwen/GLM/Ollama 等全系列 LLM，覆盖美股/港股/A股/加密货币，附 arXiv 论文 2412.20138。"
descriptionEn: "TauricResearch's open-source multi-agent LLM trading framework, 96k+ stars, Apache 2.0. Built on LangGraph with 7 specialized roles: Fundamentals/Sentiment/News/Technical Analysts + Bull/Bear Researchers + Trader + Risk/Portfolio Manager. Supports OpenAI/Claude/Gemini/DeepSeek/Kimi/Qwen/GLM/Ollama and covers US/HK/A-shares/crypto markets. arXiv: 2412.20138."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["多Agent", "量化交易", "LangGraph", "LLM金融", "多模型支持", "开源框架", "Mycelium"]
heroImage: "../../assets/images/tradingagents-multi-agent-llm-financial-trading-framework-banner.jpg"
---

*by Mycelium Protocol*

---

真实的交易公司里，一个交易决策背后往往有一个团队：有人负责研究基本面，有人盯着情绪指标，有人跑技术分析，有人做风险管理，最后由投资组合经理拍板。

TradingAgents 把这个结构原样搬进了 AI——用 7 种专职 LLM Agent 分工协作，最终由模拟交易所执行订单。

GitHub: https://github.com/TauricResearch/TradingAgents | ⭐ 96,107 | arXiv: 2412.20138

---

## 角色分工

### 分析师团队（Analyst Team）

四种角色，每种专注一个信息维度：

| 角色 | 职责 |
|------|------|
| **基本面分析师** | 评估公司财务数据和绩效指标，寻找内在价值和潜在风险信号 |
| **情绪分析师** | 聚合新闻标题、StockTwits、Reddit 等社交媒体，生成短期市场情绪读数 |
| **新闻分析师** | 监控全球新闻和宏观指标，解读事件对市场的影响 |
| **技术分析师** | 利用 MACD、RSI 等技术指标，识别交易形态和价格走势预测 |

### 研究员团队（Researcher Team）

多空双方研究员对分析师的结论进行批判性审视，通过结构化辩论平衡潜在收益和固有风险。这个对抗性设计是 TradingAgents 区别于单 Agent 方案的核心——双方必须为各自立场找到足够强的论据。

### 交易员（Trader Agent）

综合分析师和研究员的报告，做出买入/卖出/持有的具体决定，确定交易时机和规模。

### 风控 + 投资组合经理

风控团队持续评估市场波动率、流动性和其他风险因素；投资组合经理基于风控报告批准或否决交易提案，批准后由模拟交易所执行。

---

## LLM 支持矩阵

TradingAgents 支持几乎所有主流 LLM 提供商：

```bash
export OPENAI_API_KEY=...          # OpenAI (GPT)
export ANTHROPIC_API_KEY=...       # Anthropic (Claude)
export GOOGLE_API_KEY=...          # Google (Gemini)
export XAI_API_KEY=...             # xAI (Grok)
export DEEPSEEK_API_KEY=...        # DeepSeek
export DASHSCOPE_API_KEY=...       # Qwen 国际版
export DASHSCOPE_CN_API_KEY=...    # Qwen 国内版
export ZHIPU_API_KEY=...           # GLM 国际版
export ZHIPU_CN_API_KEY=...        # GLM 国内版（open.bigmodel.cn）
export MINIMAX_API_KEY=...         # MiniMax 全球
export MINIMAX_CN_API_KEY=...      # MiniMax 国内
```

v0.3.0 新增了 **Kimi**、Groq、Mistral、Bedrock 和任意 OpenAI 兼容端点（vLLM/LM Studio/llama.cpp）。本地 Ollama 也完全支持。

在代码中配置：

```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"           # 或 anthropic / google / deepseek / kimi / ollama / openai_compatible
config["deep_think_llm"] = "gpt-5.5"       # 复杂推理用的模型
config["quick_think_llm"] = "gpt-5.4-mini" # 快速任务用的模型
config["max_debate_rounds"] = 2             # 多空辩论轮数
```

---

## 市场覆盖

TradingAgents 使用 Yahoo Finance 格式的 ticker，支持所有 Yahoo Finance 覆盖的市场：

- **美股**：`AAPL`、`SPY`
- **港股**：`0700.HK`（腾讯）
- **A 股**：`600519.SS`（贵州茅台/上交所）、`000858.SZ`（五粮液/深交所）
- **东京**：`7203.T`、**伦敦**：`AZN.L`
- **印度**：`RELIANCE.NS`、**加拿大**：`.TO`、**澳大利亚**：`.AX`
- **加密货币**：`BTC-USD`、`ETH-USD`

---

## 快速安装

```bash
# 克隆并安装
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
conda create -n tradingagents python=3.12
conda activate tradingagents
pip install .

# 或 Docker
cp .env.example .env   # 填入 API Key
docker compose run --rm tradingagents
```

启动交互式 CLI：

```bash
tradingagents
```

会看到选择 ticker、分析日期、LLM 提供商、研究深度的界面，选好后 Agent 开始工作并实时显示进度。

### Python API

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

---

## 技术架构

基于 **LangGraph** 构建，用有向图表示 Agent 之间的信息流和决策流转。每个 Agent 是一个 LangGraph 节点，边表示信息传递方向。

v0.3.1 的主要修复：
- Alpha Vantage 前瞻性过滤（防止数据泄露）
- 图路由崩溃安全
- 图形状感知的检查点恢复
- 加密货币情绪数据源修复
- 可配置 LLM 重试预算
- Claude Sonnet 5 / Fable 5 支持

---

## 研究背景

arXiv 论文 2412.20138 详细描述了框架设计。2026 年 1 月还发布了 [Trading-R1 技术报告](https://arxiv.org/abs/2509.11420)——这是一个为交易推理任务进行强化学习微调的模型研究方向。

> **免责说明**：TradingAgents 是研究工具。交易表现受 LLM 选择、模型温度、数据质量、时间周期等多种因素影响，不构成任何投资建议。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## TradingAgents: A 96k-Star Multi-Agent LLM Framework That Replicates a Trading Firm

*by Mycelium Protocol*

---

Inside a real trading firm, a single decision involves a team: someone researches fundamentals, someone tracks sentiment, someone runs technical analysis, someone manages risk, and a portfolio manager makes the final call.

TradingAgents replicates this structure in AI — seven specialized LLM agents collaborate, and a simulated exchange executes the orders.

GitHub: https://github.com/TauricResearch/TradingAgents | ⭐ 96,107 | arXiv: 2412.20138

---

### Role Architecture

**Analyst Team** — four roles, each focused on one information dimension:

| Role | Responsibility |
|------|---------------|
| **Fundamentals Analyst** | Evaluates company financials and metrics, identifies intrinsic value and risk flags |
| **Sentiment Analyst** | Aggregates news, StockTwits, Reddit into a single short-term mood read |
| **News Analyst** | Monitors global news and macro indicators, interprets market impact |
| **Technical Analyst** | Uses MACD, RSI, and other indicators to detect patterns and forecast movements |

**Researcher Team** — a bullish and a bearish researcher critique the analysts' conclusions through structured debate. This adversarial design is the core differentiator from single-agent approaches — both sides must build strong cases for their positions.

**Trader Agent** — synthesizes analyst and researcher reports into buy/sell/hold decisions, setting timing and trade size.

**Risk Management + Portfolio Manager** — the risk team continuously evaluates volatility, liquidity, and risk factors; the portfolio manager approves or rejects trade proposals, which are then executed by the simulated exchange.

---

### LLM Support

TradingAgents works with nearly every major provider:

```python
config["llm_provider"] = "openai"        # GPT family
# Also: anthropic, google, xai, deepseek, kimi,
#        qwen, glm, minimax, groq, mistral, bedrock,
#        ollama, openai_compatible
config["deep_think_llm"] = "gpt-5.5"        # complex reasoning
config["quick_think_llm"] = "gpt-5.4-mini"  # fast tasks
config["max_debate_rounds"] = 2
```

v0.3.0 added **Kimi**, Groq, Mistral, Bedrock, and any OpenAI-compatible endpoint (vLLM, LM Studio, llama.cpp). Local Ollama is fully supported.

---

### Market Coverage

Uses Yahoo Finance ticker format — any market Yahoo covers works:

- **US**: `AAPL`, `SPY`
- **Hong Kong**: `0700.HK`
- **China A-shares**: `600519.SS` (Kweichow Moutai), `000858.SZ`
- **Tokyo**: `7203.T` · **London**: `AZN.L` · **India**: `RELIANCE.NS`
- **Crypto**: `BTC-USD`, `ETH-USD`

---

### Quick Start

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
conda create -n tradingagents python=3.12 && conda activate tradingagents
pip install .

tradingagents   # interactive CLI
```

Or with Docker:

```bash
cp .env.example .env   # add API keys
docker compose run --rm tradingagents
```

Python API:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

---

### Technical Foundation

Built on **LangGraph** — each agent is a node, edges represent information flow. The graph structure allows checkpointing and recovery mid-run (added in v0.2.4).

v0.3.1 fixes include: Alpha Vantage look-ahead filtering (prevents data leakage), graph-router crash safety, working crypto sentiment sources, configurable LLM retry budget, and Claude Sonnet 5 / Fable 5 support.

A companion research track: [Trading-R1](https://arxiv.org/abs/2509.11420) explores RL fine-tuning specifically for trading reasoning tasks.

> **Disclaimer**: TradingAgents is a research framework. Trading performance varies based on LLM choice, temperature, data quality, and other factors. Not financial advice.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
