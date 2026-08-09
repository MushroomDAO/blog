---
title: "World Monitor：一个人几天做出 Palantir 战情室的开源平替，78K stars"
titleEn: "World Monitor: One Person Built an Open-Source Palantir War Room in Days, 78K Stars"
description: "Elie Habib 独自开源了 World Monitor（koala73/worldmonitor），一个对标 Palantir Gotham 政府级战情室的实时全球情报仪表盘。3D 地球仪、500+ 新闻源、15 类 AI 摘要、本地 Ollama 无 API Key，AGPL-3.0。78K stars，Tauri 桌面应用，6 个主题变体。"
descriptionEn: "Elie Habib solo open-sourced World Monitor (koala73/worldmonitor), a real-time global intelligence dashboard that rivals Palantir Gotham's government war room. 3D globe, 500+ news feeds, 15-category AI briefs, local Ollama with no API key required. AGPL-3.0, 78K stars, Tauri desktop app, 6 site variants."
pubDate: "2026-08-04"
updatedDate: "2026-08-04"
category: "Tech-News"
tags: ["情报仪表盘", "开源", "Palantir平替", "3D地球", "AI摘要", "Ollama", "Tauri", "Mycelium"]
heroImage: "../../assets/images/worldmonitor-elie-habib-palantir-gotham-open-source-alternative-3d-globe-banner.jpg"
---

*by Mycelium Protocol*

---

Palantir 卖给政府的 Gotham 战情室系统，一年授权费动辄数百万美元。里面有什么？实时地图、多源数据融合、态势感知、AI 分析——听起来技术上并不神秘，只是工程量大、生态封闭。

**Elie Habib**（GitHub: [@koala73](https://github.com/koala73））花了几天时间，把这件事做成了开源：**[World Monitor](https://github.com/koala73/worldmonitor)**，78,000+ stars，AGPL-3.0，一行命令本地跑。

---

## 核心功能

### 3D 实时地球仪 + 56 种地图图层

双引擎地图：
- **3D 地球仪**：globe.gl（WebGL，Three.js）
- **WebGL 平面地图**：deck.gl + MapLibre GL

56 种叠加图层，覆盖冲突区域、航班轨迹、船只 AIS、NASA 火点、赛博威胁攻击弧线、卫星图像（NASA GIBS、哨兵 Copernicus）……

### 500+ 新闻源，15 个类别 AI 摘要

500+ 精选新闻源，**AI 自动合成**每类情报简报。15 个类别跨越：

**军事与安全** · **地缘政治** · **经济** · **灾害** · **能源** · **技术** · **健康** · **气候** · **航空** · **网络安全** · **基础设施** · **赛博威胁** · **商品** · **金融市场** · **社会稳定**

跨流关联分析——军事、经济、灾害信号同步出现时，系统会标注"升级信号"。

### 本地 AI，无需任何 API Key

支持 **Ollama**（完全本地）、Groq、OpenRouter。

```bash
# 本地 Ollama，零 API 费用
ollama pull llama3.2
# 然后在 World Monitor 配置里选 Ollama
```

也支持 Transformers.js（直接在浏览器端跑，不需要任何服务器）。

### 国家不稳定指数（CII v8）

31 个一级国家的**服务端权威不稳定压力打分**，综合多维度信号实时更新。

### 金融雷达

29 个证交所 + 大宗商品 + 加密货币，7 信号市场综合指数，实时滚动。

---

## 快速启动

```bash
git clone https://github.com/koala73/worldmonitor.git
cd worldmonitor
npm install
npm run dev
# 打开 localhost:3000，无需配置任何环境变量即可运行
```

不需要 API Key 就能跑通基础版，高级数据源（卫星、航班专业数据）才需要对应 key，`.env.example` 里有完整列表。

### 6 个主题变体

从同一个代码库：

| 变体 | 侧重 |
|------|------|
| world | 全球情报（默认） |
| tech | 科技动态 |
| finance | 金融市场 |
| commodity | 大宗商品 |
| happy | 正向新闻 |
| energy | 能源与气候 |

```bash
npm run dev:tech       # tech.worldmonitor.app
npm run dev:finance    # finance.worldmonitor.app
```

---

## 桌面应用

Tauri 2（Rust），一键下载：

- macOS Apple Silicon / Intel
- Windows（.exe）
- Linux（AppImage）

直接从 [worldmonitor.app](https://www.worldmonitor.app/api/download?platform=macos-arm64) 下载，对应平台一键安装，应用内切换 6 个变体。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vanilla TypeScript + Vite |
| 3D 地球 | globe.gl + Three.js |
| 地图 | deck.gl + MapLibre GL |
| 桌面 | Tauri 2（Rust）|
| AI | Ollama / Groq / OpenRouter / Transformers.js |
| API 协议 | Protocol Buffers（290 protos，35 服务）|
| 部署 | Vercel Edge Functions（60+）、Railway、PWA |
| 缓存 | Redis（Upstash）、三级缓存 |

---

## 程序化接入

World Monitor 不只是一个看板，它是一个可以接入 Agent 的数据层：

- **MCP Server**：`https://worldmonitor.app/mcp`（Streamable HTTP），列出所有工具无需 Key，调用需要认证
- **REST API**：`https://api.worldmonitor.app`，OpenAPI spec 公开
- **CLI**：`npx worldmonitor tools`
- **SDK**：Python（`pip install worldmonitor-sdk`）、Ruby、Go

```bash
npx worldmonitor tools          # 列出所有 MCP 工具，无需 Key
worldmonitor risk IR --api-key wm_xxx
```

---

## 为什么值得关注

Palantir Gotham 的护城河从来不是技术——是生态封闭、客户绑定和政府合规。World Monitor 用一个开源项目证明：**同样的数据融合和态势感知能力，不需要百万美元授权**。

78K stars、11K forks、26 种语言支持、覆盖 65+ 数据提供商——这不是概念验证，是一个已经在运转的生产级系统。AGPL-3.0 开源，自托管合规，可以直接在自己的基础设施上跑。

如果你是政府数字化、应急管理、地缘政治研究、OSINT 分析方向的从业者，或者只是想要一个免费的实时全球动态大屏，World Monitor 是目前最完整的开源选择。

仓库：[github.com/koala73/worldmonitor](https://github.com/koala73/worldmonitor) · 在线体验：[worldmonitor.app](https://www.worldmonitor.app/) · 作者：[Elie Habib](https://github.com/koala73)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## World Monitor: One Developer's Open-Source Answer to Palantir's $1M Government War Room — 78K Stars

*by Mycelium Protocol*

Palantir's Gotham system sells to governments for millions per year. What's inside? Real-time maps, multi-source data fusion, situational awareness, AI analysis — technically not mysterious, just a lot of engineering in a closed ecosystem.

**Elie Habib** (GitHub: [@koala73](https://github.com/koala73)) built the open-source answer in a matter of days: **[World Monitor](https://github.com/koala73/worldmonitor)**, 78,000+ stars, AGPL-3.0, runs with one command.

### Core Capabilities

**3D real-time globe + 56 map layers**

Dual map engine:
- **3D globe**: globe.gl (WebGL + Three.js)
- **WebGL flat map**: deck.gl + MapLibre GL

56 overlay layer types covering conflict zones, flight tracking, ship AIS, NASA fire data, cyber threat attack arcs, satellite imagery (NASA GIBS, Sentinel Copernicus), and more.

**500+ news feeds, 15-category AI briefs**

500+ curated feeds, AI-synthesized into intelligence briefs across 15 categories spanning military, geopolitics, economics, disaster, energy, technology, health, climate, aviation, cybersecurity, infrastructure, cyber threats, commodities, financial markets, and social stability.

Cross-stream correlation: when military, economic, and disaster signals converge, the system flags escalation patterns.

**Local AI, zero API key required**

Supports **Ollama** (fully local), Groq, and OpenRouter. Also runs Transformers.js directly in the browser — no server needed.

```bash
# Fully local, zero API cost
ollama pull llama3.2
# Then select Ollama in World Monitor settings
```

**Country Instability Index (CII v8)**

Server-authoritative stress scoring for 31 Tier-1 countries, updated in real time from multi-dimensional signals.

**Finance radar**

29 stock exchanges + commodities + crypto, 7-signal market composite, live scrolling ticker.

### Quick Start

```bash
git clone https://github.com/koala73/worldmonitor.git
cd worldmonitor
npm install
npm run dev
# Open localhost:3000 — no environment variables required
```

No API key needed for the base version. Premium data sources (satellite, professional flight data) require specific keys; `.env.example` has the complete list.

### Six Site Variants from One Codebase

| Variant | Focus |
|---------|-------|
| world | Global intelligence (default) |
| tech | Technology news |
| finance | Financial markets |
| commodity | Commodities |
| happy | Positive news |
| energy | Energy and climate |

### Desktop App

Tauri 2 (Rust) — one-click download for macOS (Apple Silicon / Intel), Windows (.exe), and Linux (AppImage). Switch all six variants from within the app.

### Programmatic Access (Agents + APIs)

World Monitor is built as a data layer for agents as well as a dashboard:

- **MCP Server**: `https://worldmonitor.app/mcp` (Streamable HTTP)
- **REST API**: `https://api.worldmonitor.app`, public OpenAPI spec
- **CLI**: `npx worldmonitor tools` (list every MCP tool, no key needed)
- **SDKs**: Python (`worldmonitor-sdk`), Ruby, Go

```bash
npx worldmonitor tools
worldmonitor risk IR --api-key wm_xxx
```

### Why This Matters

Palantir Gotham's moat was never the technology — it was ecosystem lock-in, customer binding, and government compliance capture. World Monitor proves with one open-source project that **the same data fusion and situational awareness capabilities don't require a million-dollar license**.

78K stars, 11K forks, 26-language support, 65+ data providers — this isn't a proof of concept. It's a production-grade system already running. AGPL-3.0, self-hostable, deployable on your own infrastructure.

For anyone in government digitization, emergency management, geopolitical research, OSINT analysis — or anyone who just wants a free real-time global situation display — World Monitor is the most complete open-source option available.

Repository: [github.com/koala73/worldmonitor](https://github.com/koala73/worldmonitor) · Live app: [worldmonitor.app](https://www.worldmonitor.app/) · Author: [Elie Habib](https://github.com/koala73)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
