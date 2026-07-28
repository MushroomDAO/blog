---
title: "中国出发特价机票监控的完整方案——从 OTA 逆向到廉价航司直连"
description: "TravelSky 对普通开发者关闭，但中国出发的特价机票监控并非无解。开源项目 JiPiao 已实现携程/飞猪/去哪儿/同程/途牛五平台同时监控；国际航线可叠加 Amadeus 免费 API 和 Kiwi Tequila；东南亚廉价航司则需浏览器自动化直连。本文给出从技术原理到完整部署的可落地方案，包括关键坑点：必须用中国 IP 才能拿到真实国内票价。"
pubDate: "2026-07-28"
category: "Tech-Experiment"
heroImage: "../../assets/images/china-departure-flight-price-monitor-ctrip-fliggy-qunar-southeast-asia-lcc-banner.jpg"
---

上一篇文章介绍了 Amadeus GDS API 可以拿到全球真实机票价格，但有读者马上指出了盲区：**中国出发的航班怎么办？**

这个问题问得很准。中国大陆的 GDS——中航信（TravelSky）——是国家控制的基础设施，普通开发者拿不到授权。Amadeus 的接口里，国内航班数据极度有限，且往往是空的。

但这不意味着没有解。

---

## 一、实际上有几种数据来源

### 情况一：国内航班（如北京→三亚、上海→昆明）

中航信封闭，但中国 OTA 平台（携程、去哪儿、飞猪、同程）本身就是中航信的分销渠道，它们的移动端 H5 接口是可以逆向的。技术上，这相当于**通过 OTA 的 App/网页接口间接获取 GDS 数据**——绕过了你没有授权直连 TravelSky 的问题。

限制：数据属于各 OTA，用于个人出行参考属于灰色地带，商业用途有法律风险。

### 情况二：中国出发国际航班（如上海→曼谷、广州→新加坡）

主要国际航司（国航、东航、南航、泰航、新航等）的国际航班走国际 GDS，Amadeus 可以查到。**但东南亚的廉价航司（亚航、越捷、宿务太平洋、狮航等）大部分不在 Amadeus 里**，需要另外的方案。

### 情况三：东南亚区域内航班（如曼谷→吉隆坡）

廉价航司主场，Amadeus 覆盖有限，Kiwi Tequila API 是目前覆盖最好的第三方数据源。

---

## 二、最实用的开源工具：JiPiao

**`github.com/yangka1212/JiPiao`**（2026年7月仍在更新）

这是目前 GitHub 上最完整的中文机票价格监控项目，同时支持：

| 平台 | 实现方式 | 说明 |
|---|---|---|
| 携程 Ctrip | Playwright 浏览器自动化 | 拦截 `flightListSearchForH5` XHR |
| 去哪儿 Qunar | Playwright | 同上 |
| 同程 Tongcheng | Playwright | 同上 |
| 飞猪 Fliggy（阿里旅行） | **纯 httpx 逆向** | 阿里 MTOP 网关 + MD5 签名，无需浏览器 |
| 途牛 Tuniu | 纯 httpx 逆向 | 接口较简单 |

**飞猪的逆向方案特别有价值**：阿里旅行走 `h5api.m.taobao.com/h5/mtop.trip.flight.flightSearch/1.0/` 网关，签名算法是 `MD5(cookie中的_m_h5_tk首段 + "&" + timestamp + "&" + appKey + "&" + data)`，不需要启动浏览器，响应速度快，反爬压力小。

### 核心功能

```yaml
# config.yaml 示例
routes:
  - from: SHA           # 上海
    to: BKK             # 曼谷
    dates:
      - "2026-08-15"
      - "2026-08-22"
    alert_threshold: 1200   # 低于 1200 元触发提醒

platforms: [ctrip, fliggy, qunar, tongcheng]

schedule:
  interval_minutes: 90      # 监控间隔
  jitter_minutes: 30        # 随机扰动（规避机器人特征）

notifier:
  serverchan:
    enabled: true
    send_key: "SCTxxx"      # Server酱推送到微信
```

- 多平台自动找最低价
- 低价阈值 + 涨价提醒（两个方向都有推送）
- SQLite 历史记录，可画价格走势
- 内置去抖逻辑，价格小波动不重复推送

### 安装

```bash
git clone https://github.com/yangka1212/JiPiao
cd JiPiao
pip install -r requirements.txt
python -m playwright install chromium   # 携程/去哪儿/同程 需要
cp config.example.yaml config.yaml     # 按需修改
python main.py
```

---

## 三、关键坑：必须用中国 IP

这一点经常被忽略。携程、去哪儿等 OTA **对海外 IP 返回不同（往往更高）的价格**，或者直接封掉请求。原因：国内外定价策略不同，且反爬系统会过滤非常见地区的请求。

**如果你把监控服务部署到海外云（AWS Singapore、HK 等），你监控到的价格可能不是中国用户实际看到的价格。**

解决方案：
- 把监控服务跑在国内云服务器（阿里云 / 腾讯云 / 华为云，选华东或华南节点）
- 或者用家里的电脑/NAS（24小时开机，中国宽带 IP）

---

## 四、国际航线叠加 Amadeus

对于**大型航司的国际航班**（国航、东航、南航、国际段），Amadeus 免费 API 是最省事的方案：

```python
# 例：上海 → 曼谷，搜索便宜日期
import requests

token = get_amadeus_token(client_id, client_secret)
resp = requests.get(
    "https://test.api.amadeus.com/v1/shopping/flight-dates",
    params={
        "origin": "SHA",        # 上海（所有上海机场）
        "destination": "BKK",   # 曼谷
        "oneWay": True,
        "duration": "1-7",
    },
    headers={"Authorization": f"Bearer {token}"}
)
# 返回最低价日期列表
```

Amadeus 的 `Flight Cheapest Date Search` 可以一次拿到未来一段时间内的最低价日期，非常适合监控"什么时候最便宜"而不是"明天多少钱"。

---

## 五、东南亚廉价航司：Kiwi Tequila API

AirAsia、VietJet、宿务太平洋、狮子航空这些廉价航司大多**不在 Amadeus 里**。Kiwi.com（捷克聚合平台）专门做廉价航司覆盖，他们的开发者接口叫 **Tequila**：

**注册：`tequila.kiwi.com`**

```python
import requests

resp = requests.get(
    "https://api.tequila.kiwi.com/v2/search",
    params={
        "fly_from": "SHA",          # 上海
        "fly_to": "BKK",            # 曼谷
        "date_from": "15/08/2026",
        "date_to": "30/08/2026",
        "adults": 1,
        "curr": "CNY",
        "limit": 20,
        "sort": "price",
        "asc_or_desc": "asc",
    },
    headers={"apikey": "YOUR_TEQUILA_KEY"}
)
# 返回按价格排序的航班列表，包含亚航、越捷等廉价航司
```

Tequila 的免费层每月有调用次数限制，够个人项目用。优点是**你不需要处理每个廉价航司的不同接口**，Kiwi 统一聚合了。

---

## 六、特价票的特殊情况：Flash Sale

"特价机票"分两种：

**1. 低价座位（可持续监控）**
航司每个航班都有多个座位等级（Y、Q、K、X……），最低价舱位卖完才显示下一档价格。这种可以通过上述方案定时监控，价格一旦出现就提醒。

**2. Flash Sale（闪购/促销价）**
航司定期推出限时大促，有些价格只在官方 App/小程序里出现几小时。这种很难系统性监控，因为：
- 不在 OTA 正常搜索结果里
- 要有该航司账号且已开启推送
- 有些还要登录状态才能看到

**现实的做法**：
- 订阅各航司官方微信公众号（国航、东航、南航、春秋、亚航中国区）
- 关注飞猪/携程的"特价"频道（有专门的特价 feed）
- 某些聚合信息源：穷游网特价机票频道、航班管家的降价提醒

---

## 七、完整监控架构

针对"中国出发，关注东南亚特价"的场景：

```
定时任务（每 2 小时，随机扰动）
    ↓
┌─────────────────────────────────────────────┐
│           数据采集层（国内 IP！）             │
├─────────────┬───────────────┬───────────────┤
│  JiPiao     │  Amadeus API  │  Kiwi Tequila │
│ 携程/去哪   │  主要国际航司  │  廉价航司     │
│ 飞猪/同程   │  GDS 价格     │  亚航/越捷等  │
└─────────────┴───────────────┴───────────────┘
    ↓
价格去重 & 合并（同一航班多来源取最低）
    ↓
SQLite 历史数据库
    ↓
低价检测（vs 7日均价，vs 设定阈值）
    ↓
推送告警
  ├── Server酱 → 微信
  ├── Bark → iPhone
  └── Telegram Bot
```

---

## 八、各方案对比

| 方案 | 适用场景 | 数据质量 | 合规性 | 部署复杂度 |
|---|---|---|---|---|
| JiPiao OTA 逆向 | 国内航班，国际仓 | ★★★★ | ⚠️ 灰色 | 中等 |
| Amadeus 免费 API | 国际主流航司 | ★★★★★ | ✅ 合规 | 低 |
| Kiwi Tequila | 国际廉价航司 | ★★★★ | ✅ 合规 | 低 |
| 直接刷各航司官网 | 特定航司 | ★★★★★ | ⚠️ 灰色 | 高 |
| 订阅官方推送 | Flash Sale | ★★★★★ | ✅ 合规 | 零 |

---

## 九、最小可用系统（直接能跑）

如果你只想快速开始，最小的组合是：

1. **JiPiao** 监控国内 + 国际仓（关注东南亚主要航线）
2. **Amadeus** 补充查国际大航司的便宜日期
3. **Server酱** 推送到微信
4. 部署在国内家用机器或低配国内云服务器（2核2G 够用）

不需要复杂基础设施，SQLite 就能存历史，Python + Playwright 足够跑，每月云服务器成本在 30-50 元人民币。

对于国际廉价航司，用 Kiwi Tequila 补上，加几十行 Python 就能叠加到 JiPiao 的告警管道里。

---

**参考项目**

- `yangka1212/JiPiao` — 最完整的中国出发机票监控工具
- `xanthichi/ctrip-flight-alter` — 更轻量的携程单平台版
- Amadeus for Developers: `developers.amadeus.com`
- Kiwi Tequila API: `tequila.kiwi.com`

<!--EN-->

## Complete Flight Price Monitoring for China-Departing Travelers: From OTA Reverse Engineering to LCC Direct Access

The previous article covered Amadeus GDS API for global real airfare data — but readers immediately flagged the blind spot: **What about flights departing China?**

This is the right question. China's domestic GDS — TravelSky (中航信) — is government-controlled infrastructure, inaccessible to ordinary developers. Amadeus returns near-empty data for China domestic routes.

But this doesn't mean there's no solution.

---

## The Three Data Scenarios

**Domestic China flights** (e.g., Beijing → Sanya)
TravelSky is closed, but Chinese OTAs (Ctrip, Qunar, Fliggy, Tongcheng) are all TravelSky distribution channels. Their mobile H5 APIs can be reverse-engineered — effectively getting GDS data via the OTA layer rather than directly. Gray area legally; fine for personal use.

**China-originating international flights** (e.g., Shanghai → Bangkok)
Major international carriers (Air China, China Eastern, Thai Airways, Singapore Airlines) appear on international GDS. Amadeus free API covers these. **But Southeast Asia's budget carriers (AirAsia, VietJet, Cebu Pacific, Lion Air) are mostly absent from Amadeus** — a separate solution is needed.

**Southeast Asia regional flights** (e.g., Bangkok → Kuala Lumpur)
Budget carrier territory. Kiwi's Tequila API has the best third-party coverage here.

---

## The Key Open Source Tool: JiPiao

**`github.com/yangka1212/JiPiao`** (still updated as of July 2026)

The most comprehensive Chinese flight monitoring project on GitHub. Covers five platforms simultaneously:

| Platform | Implementation | Notes |
|---|---|---|
| Ctrip 携程 | Playwright browser automation | Intercepts `flightListSearchForH5` XHR |
| Qunar 去哪儿 | Playwright | Same approach |
| Tongcheng 同程 | Playwright | Same approach |
| Fliggy 飞猪 (Alibaba Travel) | **Pure httpx reverse** | Alibaba MTOP gateway + MD5 sign — no browser needed |
| Tuniu 途牛 | Pure httpx | Simpler API |

Fliggy's reverse engineering is particularly valuable: Alibaba routes through `h5api.m.taobao.com/h5/mtop.trip.flight.flightSearch/1.0/` with `MD5(token + "&" + timestamp + "&" + appKey + "&" + data)` signing. No Playwright needed, faster, less anti-bot pressure.

```yaml
# config.yaml
routes:
  - from: SHA
    to: BKK
    dates:
      - "2026-08-15"
      - "2026-08-22"
    alert_threshold: 1200  # alert if price drops below 1200 CNY

platforms: [ctrip, fliggy, qunar, tongcheng]

notifier:
  serverchan:
    enabled: true
    send_key: "SCTxxx"  # pushes WeChat notifications via Server酱
```

---

## Critical Trap: You Need a China IP

This is consistently overlooked. Chinese OTAs **return different (usually higher) prices to overseas IPs**, or block the requests outright. Domestic vs. international pricing differs; anti-bot systems filter unusual geographic sources.

**If you deploy to a non-China server (AWS Singapore, Alibaba HK), you may monitor prices that Chinese users never actually see.**

Fix: run on a mainland China cloud server (Aliyun / Tencent Cloud, East China or South China regions), or a home machine on Chinese residential broadband.

---

## Layer 2: Amadeus for Major International Carriers

For Air China, China Eastern, China Southern international routes — and all major global carriers — Amadeus free API is the cleanest option:

```python
# Find cheapest date to fly SHA → BKK
resp = requests.get(
    "https://test.api.amadeus.com/v1/shopping/flight-dates",
    params={"origin": "SHA", "destination": "BKK", "oneWay": True},
    headers={"Authorization": f"Bearer {token}"}
)
```

`Flight Cheapest Date Search` returns the lowest-price day across a date range in one call — ideal for "when is the cheapest time to fly" rather than checking a single date repeatedly.

---

## Layer 3: Kiwi Tequila for Budget Carriers

AirAsia, VietJet, Cebu Pacific, Lion Air are mostly absent from Amadeus. Kiwi.com specializes in aggregating budget carriers; their developer API is called **Tequila** (`tequila.kiwi.com`):

```python
resp = requests.get(
    "https://api.tequila.kiwi.com/v2/search",
    params={
        "fly_from": "SHA", "fly_to": "BKK",
        "date_from": "15/08/2026", "date_to": "30/08/2026",
        "curr": "CNY", "sort": "price", "asc_or_desc": "asc",
        "limit": 20,
    },
    headers={"apikey": "YOUR_KEY"}
)
# Returns flights including AirAsia, VietJet, sorted by price
```

Tequila's free tier fits personal projects. You don't need to handle each LCC's separate API — Kiwi aggregates them.

---

## The Flash Sale Problem

"Cheap tickets" in Chinese travel context means two different things:

**1. Low fare buckets (systematically monitorable)**: Every flight has multiple booking classes; the cheapest seats show up in normal OTA search until sold out. JiPiao + Amadeus + Kiwi covers this.

**2. Flash Sales (promotional prices)**: Airlines run periodic limited-time promotions that appear only in official apps for a few hours. Hard to monitor because: they're outside normal OTA search results, require logged-in airline accounts, and sometimes only visible with push notifications enabled.

**Practical approach for flash sales**:
- Follow official WeChat accounts: 国航、东航、南航、春秋、AirAsia China
- Subscribe to Fliggy/Ctrip "special price" channels (they have dedicated flash sale feeds)
- 穷游 (Qyer) special ticket channel, 飞常准 (VariFlight) price drop alerts

---

## Minimum Viable Setup

If you just want to start quickly — the smallest practical combination:

1. **JiPiao** watching 3-5 routes across Ctrip + Fliggy (covers domestic + international on Chinese OTAs)
2. **Amadeus** to check cheapest dates on major international carriers
3. **Kiwi Tequila** to fill in LCC pricing
4. **Server酱** for WeChat alerts
5. Cheap mainland China VPS (2 core / 2GB RAM, ~30-50 CNY/month)

A hundred lines of Python to glue the data into a single SQLite database, one cron job, and you have a functional multi-source price monitor that covers what Chinese travelers actually need.

---

**References**
- `yangka1212/JiPiao` — the most complete China-departing flight monitor
- `xanthichi/ctrip-flight-alter` — lighter single-platform Ctrip version
- Amadeus for Developers: `developers.amadeus.com`
- Kiwi Tequila API: `tequila.kiwi.com`
