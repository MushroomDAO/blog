---
title: "机票价格不是秘密——从 GDS 到 NDC，开发者如何获取全球真实航班票价"
titleEn: "Airfare Is Not a Secret: How Developers Get Real Global Flight Prices, from GDS to NDC"
description: "携程、Expedia 的底价来自 Amadeus/Sabre/Travelport 三大 GDS，再加服务费卖给你。开发者可以直接接 GDS API 拿到发布票价（Published Fare），Amadeus for Developers 提供每月 2000 次免费生产调用。本文整理了 GDS、NDC、地区差异、中国特殊情况，以及搭建实时价格监控系统的完整技术路径。"
pubDate: "2026-07-28"
category: "Tech-Experiment"
heroImage: "../../assets/images/flight-price-api-gds-ndc-real-price-amadeus-duffel-global-monitoring-banner.jpg"
---

想做一个监控全球机票价格的工具，第一个问题是：价格从哪里来？

去每个航空公司官网查？20 家主要航司的 API 各不相同，维护成本极高。用携程 / Expedia 的 API？他们在底价上加了服务费，你拿不到真实价格。

其实这个行业有一套现成的基础设施，大多数开发者不知道它的存在。

---

## 一、真正的底层结构

航空定价行业的数据流是这样的：

```
航空公司发布票价（Published Fare）
        ↓
GDS 全球分销系统聚合
Amadeus / Sabre / Travelport
        ↓               ↓
OTA（携程/Expedia）    直接 API 接入方
加服务费 → 消费者      真实价格 → 你的应用
```

**GDS（Global Distribution System，全球分销系统）** 是这条链路的核心。三大 GDS：

- **Amadeus**：欧洲最大，全球市场份额约 40%，总部马德里
- **Sabre**：美洲最强，总部达拉斯，服务大量北美航司
- **Travelport**（含 Galileo / Worldspan）：英国，覆盖亚太较好

航空公司把票价发布到 GDS，OTA 从 GDS 拉取后加价卖给消费者。**OTA 收的"服务费"就是中间差价。** 你直接接 GDS 的 API，拿到的就是航司公布的真实价格。

---

## 二、NDC——另一条直连通道

GDS 收取订阅费，所以部分航司开始推广 **NDC（New Distribution Capability，新分销标准）**，这是 IATA 制定的航司直连分发标准。

NDC 的特点：
- **绕过 GDS**，航司直接把内容推给授权分销商
- 有时包含 **GDS 上没有的特价**（航司不想给 GDS 佣金）
- 支持更丰富的附加服务（选座、行李、餐食单独定价）

缺点是覆盖不如 GDS 全面——中小型航司没有 NDC 接口。

---

## 三、最可用的免费 API

### Amadeus for Developers（最重要的入口）

**`developers.amadeus.com`**

这是直接接 GDS 的合法路径，而且有免费层：

| 环境 | 限额 | 数据 |
|---|---|---|
| Test（沙箱） | 无限调用 | 仿真数据（接近真实） |
| Production | 每月 2000 次免费 | 真实 GDS 数据 |

关键 API：

```bash
# 获取 token
curl -X POST "https://test.api.amadeus.com/v1/security/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_KEY&client_secret=YOUR_SECRET"

# 搜索航班报价（北京→伦敦，2026-09-01，1名成人）
curl "https://test.api.amadeus.com/v2/shopping/flight-offers?\
originLocationCode=PEK\
&destinationLocationCode=LHR\
&departureDate=2026-09-01\
&adults=1\
&max=5\
&currencyCode=CNY" \
  -H "Authorization: Bearer {token}"
```

返回的是完整的 GDS 报价结构：航段、换乘、舱位代码、含税总价、行李额、效期限制。**这就是真实发布票价，没有 OTA 加价。**

其他实用 API：
- `Flight Cheapest Date Search` — 给定出发地+目的地，搜哪天最便宜
- `Flight Price Analysis` — 历史价格分析（判断现在的价格贵不贵）
- `Flight Inspiration Search` — 给出发地，搜全球哪个目的地最便宜

### Duffel（NDC 直连聚合器）

**`duffel.com`**

Duffel 是伦敦的初创公司，直连多家航司的 NDC 接口，封装成统一 API：

- 覆盖：British Airways、Lufthansa、Air France、American Airlines、EasyJet 等
- 特点：有时能拿到比 GDS 便宜的 NDC 专属价格
- 计费：有开发者免费沙箱，生产环境按成交量收费
- 适合：欧洲航线、廉价航空

Amadeus 和 Duffel 互补：Amadeus 覆盖广，Duffel 补 NDC 直连价格。

---

## 四、地区差异与中国特殊情况

| 地区 | 推荐方案 | 说明 |
|---|---|---|
| 欧洲 | Amadeus + Duffel | Amadeus 欧洲最强；Duffel 补 NDC 价格 |
| 北美 | Amadeus / Sabre | Sabre 在美洲更完整，但商业化程度高 |
| 东南亚 | Amadeus + AirAsia 合作 API | AirAsia 有合作伙伴直连接口 |
| 日韩 | Amadeus 基本够用 | — |
| 中国大陆 | **特殊情况，见下** | — |

**中国大陆是例外**。国内的 GDS 是**中航信（TravelSky）**，由国资委控制，普通开发者无法接入，必须有 CAAC 授权资质。这意味着：

- 国内航班真实底价对普通开发者封闭
- 替代方案：接携程/去哪儿的分销 API（有加价）
- 技术上可以解析航司 App 接口，但法律上是灰色地带
- **务实建议**：如果主要关注国际航班，Amadeus 够用；国内航班不要试图绕过 TravelSky

---

## 五、实时价格监控架构

如果你想做的是持续追踪特定航线的价格变化，推荐以下架构：

```
定时任务（每 15 分钟 / 每小时）
    ↓
Amadeus Flight Offers API  ── 国际航线
Duffel API                 ── NDC 直连补充
    ↓
时序数据库（TimescaleDB / InfluxDB）
    ↓
价格异常检测（相比 7 日均价下降 X%）
    ↓
推送告警（Telegram / Email / Webhook）
```

**关键考量**：

- Amadeus 免费层 2000 次/月，按 15 分钟间隔监控一条航线约需 2880 次/月——需要升级计划或减少频率
- 生产级别建议：合并监控多条航线，批量查询减少调用次数
- 历史数据：用 `Flight Price Analysis API` 获取过去 11 个月的价格区间，建立"便宜/正常/贵"的判断基准

---

## 六、可参考的开源项目

| 项目 | 语言 | 技术栈 | 说明 |
|---|---|---|---|
| `vasadasa0304-sudo/flight-fare-monitor` | Python | Amadeus + PostgreSQL + Streamlit | 完整的数据管道 |
| `arifaqyl/flight-fare-monitor` | Python | Amadeus + SQLite + Telegram | 轻量，带告警 |
| `onceingen/flight-scout-agent` | TypeScript | 15分钟扫描 + 邮件通知 | Agent 架构 |
| `achyutjoshi/Flight-Prices-Scraper` | Python | 通用抓取 | 入门参考 |

这些项目都以 Amadeus API 为数据源，可以作为基础直接修改。

---

## 七、结论

**直接上手**：注册 `developers.amadeus.com`，拿免费 API key，调 `Flight Offers Search API`。你拿到的就是 GDS 里的真实发布票价，和 OTA 看到的同一份数据，只是没有中间商加价。

这个基础设施一直都在，只是大多数想做机票工具的开发者不知道有这个路径。

---

<!--EN-->

## Flight Prices Aren't a Secret — GDS, NDC, and How Developers Can Access Real Airfare Data

If you want to build a global flight price monitoring tool, the first question is: where do the prices come from?

Query each airline's website directly? Twenty major carriers, twenty different APIs, enormous maintenance overhead. Use Expedia's or Ctrip's API? They've marked up the base price and you won't see the real fare.

There's an existing infrastructure for exactly this that most developers don't know about.

---

## The Real Underlying Structure

Here's how airfare data actually flows:

```
Airline publishes fares (Published Fares)
           ↓
GDS (Global Distribution System) aggregates
Amadeus / Sabre / Travelport
           ↓                    ↓
OTA (Ctrip/Expedia)       Direct API access
adds service fee → user   real price → your app
```

**GDS (Global Distribution Systems)** are the core of this chain. The three majors:

- **Amadeus**: Largest globally (~40% market share), headquartered in Madrid, dominant in Europe
- **Sabre**: Strongest in the Americas, headquartered in Dallas
- **Travelport** (Galileo/Worldspan): UK-based, strong Asia-Pacific coverage

Airlines publish fares to the GDS. OTAs pull those fares and sell them with a markup. **The "service fee" OTAs charge is the markup on top of the GDS price.** Call the GDS API directly and you get the airline's published price.

---

## NDC — The Direct Channel

Because GDS charges subscription fees, some airlines have started distributing via **NDC (New Distribution Capability)**, an IATA standard for direct airline-to-agency distribution.

NDC characteristics:
- **Bypasses the GDS** — airlines distribute directly to authorized parties
- Sometimes includes **fares not available on GDS** (airlines avoiding GDS commissions)
- Supports richer ancillary services (seat selection, baggage, meals priced individually)

Downside: coverage is narrower than GDS — smaller carriers often have no NDC capability.

---

## The Best Free APIs

### Amadeus for Developers (the most important entry point)

**`developers.amadeus.com`**

This is the legitimate path to GDS data, with a free tier:

| Environment | Quota | Data |
|---|---|---|
| Test (sandbox) | Unlimited | Simulated (close to real) |
| Production | 2,000 calls/month free | Real GDS data |

Key API — Flight Offers Search:

```bash
# Get token
curl -X POST "https://test.api.amadeus.com/v1/security/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_KEY&client_secret=YOUR_SECRET"

# Search flights (Beijing → London, 2026-09-01, 1 adult)
curl "https://test.api.amadeus.com/v2/shopping/flight-offers?\
originLocationCode=PEK&destinationLocationCode=LHR\
&departureDate=2026-09-01&adults=1&max=5" \
  -H "Authorization: Bearer {token}"
```

The response includes full GDS fare structure: segments, connections, booking class, total price with taxes, baggage allowance, fare validity. **This is the real published fare — no OTA markup.**

Other useful APIs:
- `Flight Cheapest Date Search` — find the cheapest day for a given route
- `Flight Price Analysis` — historical price analysis (is the current price cheap or expensive?)
- `Flight Inspiration Search` — given a departure city, find the cheapest destinations globally

### Duffel (NDC aggregator)

**`duffel.com`**

A London startup connecting directly to airline NDC endpoints with a unified API:

- Covers: British Airways, Lufthansa, Air France, American Airlines, EasyJet, and more
- Advantage: sometimes cheaper NDC-exclusive fares unavailable on GDS
- Pricing: free developer sandbox, production billed per booking volume
- Best for: European routes, low-cost carriers

Amadeus and Duffel are complementary: Amadeus for breadth, Duffel for NDC direct prices.

---

## Regional Differences and China's Special Case

| Region | Recommended | Notes |
|---|---|---|
| Europe | Amadeus + Duffel | Amadeus strongest here; Duffel adds NDC coverage |
| North America | Amadeus / Sabre | Sabre stronger in Americas but more commercial |
| Southeast Asia | Amadeus + AirAsia partner API | AirAsia has a direct partner API |
| Japan/Korea | Amadeus sufficient | — |
| Mainland China | **Special case — see below** | — |

**Mainland China is the exception.** The domestic GDS is **TravelSky (中航信)**, state-owned and controlled by SASAC. Standard developers cannot access it without CAAC authorization. This means:

- Real domestic fare data is closed to ordinary developers
- Alternatives: Ctrip/Qunar distribution APIs (with markup), or parsing airline app APIs (technically feasible, legally grey)
- **Practical advice**: For international routes, Amadeus is sufficient. For domestic China flights, don't try to bypass TravelSky.

---

## Real-Time Price Monitoring Architecture

For continuously tracking price changes on specific routes:

```
Scheduler (every 15 min / hourly)
        ↓
Amadeus Flight Offers API  — international routes
Duffel API                 — NDC supplement
        ↓
Time-series DB (TimescaleDB / InfluxDB)
        ↓
Anomaly detection (X% below 7-day average)
        ↓
Alerts (Telegram / Email / Webhook)
```

**Key considerations**:

- Amadeus free tier is 2,000 calls/month. Monitoring one route at 15-minute intervals requires ~2,880 calls/month — you'll need to upgrade or reduce frequency
- Production approach: batch multiple routes per query to minimize API calls
- Historical baseline: use `Flight Price Analysis API` to get 11-month price ranges, establish "cheap/normal/expensive" thresholds

---

## Open Source References

| Project | Lang | Stack | Notes |
|---|---|---|---|
| `vasadasa0304-sudo/flight-fare-monitor` | Python | Amadeus + PostgreSQL + Streamlit | Full data pipeline |
| `arifaqyl/flight-fare-monitor` | Python | Amadeus + SQLite + Telegram alerts | Lightweight, alerting included |
| `onceingen/flight-scout-agent` | TypeScript | 15-min scans + email | Agent architecture |
| `achyutjoshi/Flight-Prices-Scraper` | Python | General scraper | Good starting reference |

All use Amadeus API as their data source and can be forked as a starting point.

---

## Conclusion

**Getting started**: Register at `developers.amadeus.com`, get a free API key, call `Flight Offers Search`. What you'll receive is the same GDS data OTAs see — just without the middleman's markup.

This infrastructure has existed for decades. Most developers who want to build flight tools simply don't know the path exists.
