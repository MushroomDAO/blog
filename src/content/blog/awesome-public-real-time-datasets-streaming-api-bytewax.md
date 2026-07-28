---
title: "构建实时数据流项目的最佳起点：Awesome Public Real-Time Datasets 完整导读"
description: "bytewax/awesome-public-real-time-datasets 是一个 2751 stars 的公开实时数据源合集，覆盖金融加密货币、交通、气象、网络安全、IoT、体育等类别，大量免费 WebSocket/SSE/REST 接口。本文按使用场景整理关键数据源，适合构建流处理管道、AI 训练数据集和实时 Agent 工具的开发者。"
pubDate: "2026-07-28"
category: "Research"
heroImage: "../../assets/images/awesome-public-real-time-datasets-streaming-api-bytewax-banner.jpg"
---

构建实时数据流项目，第一步往往是找数据——哪里有可以用的实时流？协议是什么？免费额度够不够用？

`bytewax/awesome-public-real-time-datasets` 是目前最完整的一份公开实时数据源清单：2751 stars，CC0 公开领域授权，由 bytewax.io 团队维护，按类别分为免费和付费两部分，今天刚更新。

以下按使用场景重新梳理核心数据源。

---

## 一、金融与加密货币（Free）

这是列表里数据源最密集的一类，覆盖股票、加密货币、外汇、衍生品：

**WebSocket 实时流**
- **Coinbase Market Data** — Level 2 orderbook 实时数据，官方 WebSocket，机构级质量
- **Binance** — 加密货币交易数据 + 订单簿更新，流量大、延迟低
- **Yahoo Finance** — `wss://streamer.finance.yahoo.com/`，非官方但可用，用于驱动其网页端
- **CoinCheck** — 日本交易所，WebSocket Beta

**REST/轮询（高频可得实时效果）**
- **Alpaca Markets** — 股票实时 + 历史数据，HTTP + WebSocket，有免费层
- **Polygon.io** — 全美交易所股票和加密货币，REST + WebSocket，文档完善
- **Finnhub** — 有限免费额度，高级数据源付费
- **CoinCap** — 1000+ 加密货币实时定价，免费
- **CoinPaprika** — 7000+ 加密货币，无需 API Key，OHLCV + tickers
- **Pyth Network** — 跨所有资产类别的金融市场数据统一接口

**监管与合规数据**
- **SEC EDGAR** — 美国证监会实时监管文件流（10-K、10-Q、8-K），REST + RSS，完全免费
- **FilingFirehose** — 解析后的 SEC EDGAR 文件，8-K 正文分类（识别被埋的网络事件和高管离职），免费 tier 覆盖过去 72 小时，无需 API Key

**链上数据**
- **Blockchain.com** — 比特币新交易和区块的实时通知，WebSocket
- **DexPaprika** — DEX（去中心化交易所）实时池数据、代币价格，无需注册，无限额
- **Agent Gateway** — 500+ 加密代币实时价格（通过 Hyperliquid），免费 REST，无需 API Key
- **OpenChainBench** — 加密基础设施基准（RPC 提供商、跨链桥、预言机、L1 确定性），每分钟刷新，Hugging Face 上有每日 Parquet 快照（CC-BY-4.0）

---

## 二、交通（Free）

**铁路 / 地铁**
- **MTA GTFS Feed** — 纽约地铁、Caltrain 等，GTFS-Realtime 格式
- **Open Rail Data** — 英国铁路网，包括时刻表和实时服务更新，STOMP 协议
- **Ireland NTA** — 都柏林巴士、Bus Éireann、Go-Ahead Ireland 实时更新流

**公共交通（多模式）**
- **Transport for London (TfL)** — 地铁、公交、等实时数据
- **Swiss Traffic & Public Transport** — 瑞士公路交通、EV 充电站、共享出行、公共交通到站时刻
- **Transport for NSW** — 澳大利亚新南威尔士州巴士、火车、轮渡

**航空 / 海运 / 其他**
- **Open Sky Flight** — 飞机实时位置，HTTP polling（不是 streaming）
- **Norwegian AIS** — 挪威经济区内船舶 AIS 数据
- **GBFS（共享单车）** — 全球共享单车标准协议，纽约 Citi Bike 有公开端点
- **Open Glider Network** — 滑翔机和轻型飞机实时位置，可推送到 Kafka

---

## 三、气象、环境与地球科学（Free）

- **Open Weather API** — 当前天气，每 90 秒免费 1 次（前 1000 次/天免费）
- **NOAA Weather Data** — 美国国家气象局，完全免费的实时天气 API
- **NOAA Buoy Data** — 海洋浮标实时数据（温度、波高、风速）
- **USGS Earthquake** — 地震实时数据流，FDSN Web Services
- **Seismic Portal** — 欧洲地震门户，WebSocket 实时地震事件
- **EPA Airnow** — 美国 EPA 空气质量数据
- **UK Flood Data** — 英国政府实时洪水监测 API
- **ZipCheckup** — 美国 42000+ ZIP Code 环境安全数据（水质、空气质量、PFAS、氡、铅、洪水风险），免费 REST，无需 API Key，CC BY 4.0
- **US Energy Grid** — gridstatus.io，美国电网实时信息

---

## 四、网络安全（Free）

这部分对威胁情报和安全分析管道很实用：

- **Certstream** — SSL/TLS 证书透明度日志实时流，可检测新域名注册（钓鱼域名早发现）
- **URLhaus** — 社区驱动的恶意 URL 实时数据，可作为黑名单馈入
- **CISA AIS** — 美国政府主导，组织间机器可读威胁指标实时交换
- **OTX（AlienVault）** — 社区威胁情报平台，恶意 IP / 域名 / URL 实时数据
- **Shodan Streaming API** — 互联网设备和 banner 实时发现，有免费 tier
- **GreyNoise Community** — 免费 IP 情报查询，识别互联网背景噪声扫描器

---

## 五、IoT 和传感器（Free）

- **ThingSpeak** — 众包 IoT 传感器数据，REST + MQTT，适合快速原型
- **Sensor.Community** — 全球 15000+ 空气质量传感器，REST API

---

## 六、新闻与社会数据（Free）

- **Wikimedia SSE** — Wikimedia 基金会页面近期变更事件流，SSE 协议
- **GDELT 2.0** — 全球事件数据库，涵盖情感估值和实时翻译，覆盖全球所有新闻事件
- **News API** — 聚合全球数十个新闻来源，近实时头条，有免费 tier（有延迟限制）
- **NY Times Newswire** — 纽约时报发布内容的实时流
- **Hacker News API** — HN 近实时新闻流，技术和创业话题

---

## 七、开发与测试（无需真实数据时）

- **Lenses Datagen** — 开源（Apache 2.0）合成流数据生成器，支持推送到 Kafka/Pulsar，内置 AIS 船舶位置、NYC 出租车、IoT 温度等数据集
- **Mockingbird（Tinybird）** — 开源 mock 流数据生成器
- **SSE.dev** — 公开 SSE 测试端点，可配置间隔，适合管道测试

---

## 八、其他领域亮点

**体育**
- **OpenF1** — F1 实时遥测、圈速、赛事控制消息、天气、进站、车队无线电，完全免费开放
- **World Cup 2026** — 2026 世界杯赛程、赛事 RSS 和日历 Feed，免费 HTTP，无需 API Key

**太空**
- **ISS Live Data** — 国际空间站实时遥测数据
- **Satellite Positions（N2YO）** — 通过 NORAD 目录号追踪卫星位置

**社交**
- **Bluesky Firehose** — AT Protocol 底层的认证事件流，WebSocket，高吞吐量的全平台用户更新

**AI/ML**
- **AI Detector Arena** — AI 生成图像检测器实时排行榜，2038 张图片 + 17 个 AI 生成器的实时评估数据，HTTP API，有 DOI

---

## 九、付费但值得了解

| 类别 | 数据源 | 特点 |
|---|---|---|
| 金融 | Data Bento | 多交易所低延迟市场数据，Rust/Python/C++ 客户端 |
| 金融 | NYSE Cloud | 实时纽约证券交易所数据，Kafka 格式 |
| 金融 | Bloomberg B-PIPE | 机构级全球市场数据 |
| 交通 | FlightAware Firehose | 全球飞机实时位置和飞行状态 |
| 交通 | Spire | 卫星 AIS 海事 + 航空数据 |
| 新闻 | Reuters API | 低延迟路透社新闻流 |
| 安全 | Kaspersky Feeds | 持续更新的威胁情报数据 |

---

## 十、按协议分类

| 协议 | 代表数据源 |
|---|---|
| **WebSocket** | Coinbase、Binance、Yahoo Finance、Seismic Portal、Bluesky、CoinCheck |
| **SSE（Server-Sent Events）** | Wikimedia、SSE.dev |
| **STOMP** | Open Rail Data |
| **MQTT** | ThingSpeak |
| **REST（需轮询）** | Open Sky、NOAA、EPA、大部分免费数据源 |
| **TCP binary（专有）** | Data Bento、FlightAware Firehose |

---

这个列表的实际价值在于：**它把"我需要实时数据，但不知道从哪拿"这个问题压缩成了一次查表**。很多列出的免费数据源无需注册即可直接访问（CoinPaprika、DexPaprika、Agent Gateway、OpenChainBench、ZipCheckup 等），适合快速原型。

项目链接：`github.com/bytewax/awesome-public-real-time-datasets`（2751 ⭐，CC0，Bytewax 团队维护）

<!--EN-->

## The Best Starting Point for Real-Time Data Projects: Awesome Public Real-Time Datasets

When building a real-time data pipeline, the first question is usually: where do I get the data? What protocols are available? Is the free tier usable?

`bytewax/awesome-public-real-time-datasets` is the most comprehensive public list of real-time data sources available: 2,751 stars, CC0 (public domain) license, maintained by the bytewax.io team, split into free and paid categories, updated today.

Here's a breakdown by use case.

---

## Finance & Crypto (Free)

The densest category, covering stocks, crypto, forex, and derivatives:

**WebSocket real-time streams**
- **Coinbase Market Data** — Level 2 orderbook, official WebSocket, institutional-quality
- **Binance** — Crypto trade data + order book updates, low latency
- **Yahoo Finance** — `wss://streamer.finance.yahoo.com/` — unofficial but functional, drives their own website
- **CoinCheck** — Japanese exchange, WebSocket (beta)

**REST / polling (high-frequency = near-realtime)**
- **Alpaca Markets** — Stock real-time + historical, HTTP + WebSocket, free tier available
- **Polygon.io** — All US exchanges, stocks + crypto, REST + WebSocket, well-documented
- **CoinPaprika** — 7,000+ cryptocurrencies, no API key required, OHLCV + tickers
- **DexPaprika** — DEX pool data, token prices, OHLCV, cross-chain, no signup, no limits
- **Agent Gateway** — 500+ crypto token prices via Hyperliquid, free REST, no API key

**Regulatory & compliance**
- **SEC EDGAR** — Real-time US regulatory filings stream (10-K, 10-Q, 8-K), REST + RSS, free
- **FilingFirehose** — Parsed SEC EDGAR filings with body-text classification (catches buried cyber/officer events), 8-K alerts, free tier covers 72h, no API key

**On-chain**
- **Blockchain.com** — Bitcoin new transaction/block notifications, WebSocket
- **OpenChainBench** — Crypto infrastructure benchmarks (RPC providers, bridges, oracles, L1 finality), refreshed every minute, daily Parquet snapshots on Hugging Face (CC-BY-4.0)

---

## Transportation (Free)

**Rail / metro**
- **MTA GTFS Feed** — NYC subway, Caltrain, GTFS-Realtime format
- **Open Rail Data** — UK rail network, STOMP protocol, real-time service updates
- **Ireland NTA** — Dublin Bus, Bus Éireann, Go-Ahead Ireland real-time update stream

**Multi-modal public transit**
- **Transport for London (TfL)** — Tube, buses, more
- **Swiss Transport Data** — Road traffic, EV charging, shared mobility, live arrivals/departures
- **Transport for NSW** — Buses, trains, ferries across New South Wales, Australia

**Aviation / maritime / other**
- **Open Sky Flight** — Aircraft real-time positions, HTTP polling (not streaming)
- **Norwegian AIS** — Vessel AIS data in Norwegian economic zone
- **Open Glider Network** — Gliders and light aircraft positions, can feed into Kafka

---

## Weather, Environment & Earth Science (Free)

- **NOAA Weather** — US National Weather Service, completely free real-time API
- **NOAA Buoy Data** — Ocean buoy data (temperature, wave height, wind speed)
- **USGS Earthquake** — Seismological real-time data feed
- **Seismic Portal** — European seismic events, WebSocket
- **EPA Airnow** — US air quality data
- **UK Flood Data** — UK government real-time flood monitoring API
- **ZipCheckup** — 42,000+ US ZIP codes, 13 environmental safety verticals (water quality, air quality, PFAS, radon, lead, flood risk), free REST, no API key, CC BY 4.0
- **US Energy Grid** — gridstatus.io, real-time US grid information

---

## Cybersecurity (Free)

Useful for threat intelligence pipelines and security analytics:

- **Certstream** — SSL/TLS certificate transparency log real-time feed (early detection of phishing domains)
- **URLhaus** — Community-driven malicious URL feed, actionable threat intelligence
- **CISA AIS** — US government machine-readable threat indicator sharing
- **OTX (AlienVault)** — Community threat intelligence, malicious IPs/domains/URLs via DirectConnect API
- **Shodan Streaming** — Internet device/banner real-time discovery, free tier
- **GreyNoise Community** — Free IP intelligence for identifying background noise scanners

---

## Development & Testing (No Real Data Needed)

- **Lenses Datagen** — Open-source (Apache 2.0) synthetic streaming data generator, publishes to Kafka/Pulsar, includes AIS vessel positions, NYC taxi trips, IoT temperature datasets
- **Mockingbird (Tinybird)** — Open-source mock streaming data generator
- **SSE.dev** — Public SSE test endpoint with configurable intervals

---

## Other Notable Sources

**Sports**
- **OpenF1** — F1 real-time telemetry, lap timings, race control messages, weather, pit stops, team radio, standings. Completely free and open.
- **World Cup 2026** — 2026 FIFA World Cup fixtures, RSS, calendar feeds, free HTTP, no API key

**Space**
- **Bluesky Firehose** — AT Protocol authenticated WebSocket event stream, high-throughput global user updates

**AI/ML**
- **AI Detector Arena** — Live leaderboard for AI-generated image detectors, 2,038 images × 17 AI generators, HTTP API, DOI-indexed

---

## By Protocol

| Protocol | Representative sources |
|---|---|
| **WebSocket** | Coinbase, Binance, Yahoo Finance, Seismic Portal, Bluesky, CoinCheck |
| **SSE** | Wikimedia EventStreams, SSE.dev |
| **STOMP** | Open Rail Data |
| **MQTT** | ThingSpeak |
| **REST (polling)** | Open Sky, NOAA, EPA, most free sources |
| **TCP binary (proprietary)** | Data Bento, FlightAware Firehose |

---

The practical value: **this list collapses "I need real-time data but don't know where to get it" into a single lookup**. Many free sources require no registration and can be hit immediately (CoinPaprika, DexPaprika, Agent Gateway, OpenChainBench, ZipCheckup, etc.), suitable for rapid prototyping.

Project: `github.com/bytewax/awesome-public-real-time-datasets` (2,751 ⭐, CC0, maintained by Bytewax)
