---
title: "God's Eye View：浏览器里的卫星侦察视角，数据全是真实的，MIT 开源，35K Stars"
titleEn: "God's Eye View: Spy Satellite Simulator in Your Browser — All Real Data, MIT Open Source, 35K Stars"
description: 'bilawalsidhu/gods-eye-view，35K stars，MIT 开源，JavaScript + CesiumJS + WebGL + Google 3D Tiles。浏览器里的地理空间情报平台：15 个实时数据层，包括 11,000+ 架飞机、全球船只、838 颗卫星轨道、地震、CCTV、NASA 火灾探测。支持语音控制、座舱视角、热成像传感器模拟。无需 API Key 即可启动。'
descriptionEn: "bilawalsidhu/gods-eye-view, 35K stars, MIT open source, JavaScript + CesiumJS + WebGL + Google 3D Tiles. A browser-based geospatial intelligence platform with 15 live data layers: 11,000+ aircraft, global vessels, 838 satellite orbits, earthquakes, public CCTV, NASA fire detections. Voice control, cockpit mode, thermal sensor simulation. No API key required to start."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Tech-News"
tags: ["open-source", "geospatial", "OSINT", "satellite-tracking", "CesiumJS", "WebGL", "3D-globe", "real-time-data", "MIT"]
heroImage: "../../assets/images/gods-eye-view-browser-geospatial-intelligence-real-data-3d-globe-banner.jpg"
---

> 📌 开源仓库：https://github.com/bilawalsidhu/gods-eye-view
> License：MIT | Stars：35,238 | Forks：7,053 | Language：JavaScript

---

God's Eye View 的定义是：**浏览器里的间谍卫星模拟器，但数据全是真实的。**

它把 15 种公开实时数据流渲染在一个照片级真实感 3D 地球上，不需要 API Key 就能跑起来，用普通 MacBook 浏览器打开，1.86 秒冷启动。GitHub 上线以来 35K+ Stars，2026 年 8 月登上 Trending 第一。

---

## 15 层实时数据

| 数据层 | 来源 | 说明 |
|--------|------|------|
| 民航飞机 | OpenSky + adsb.lol | 11,000+ 架实时追踪，含 3D 机型模型 |
| 军事飞机 | adsb.lol | 军用航班 ADS-B |
| 船只 | AISStream | 全球 AIS 船舶信号 |
| 卫星 | CelesTrak | 838 个在轨目标，SGP4 轨道传播 |
| 地震 | USGS | 24 小时窗口实时震情 |
| 交通 | OSM + TomTom | 道路车辆，可选实时速度 |
| 公共摄像头 | 公开 CCTV 数据库 | 约 3,600 个公开摄像机投影进 3D 空间 |
| 电台 | 地理定位电台 | 模拟调频旋钮收听 |
| 公共交通 | GTFS-Realtime | 公交、列车、渡轮实时位置 |
| 共享单车 | 各城市开放接口 | 站点实时剩余量 |
| 火灾 | NASA FIRMS | 卫星热点探测 |
| 太空任务 | 发射日历 API | 30 天发射计划 + 回放 |
| 导航路径 | OSRM | 地形贴合路线规划 |

---

## 玩法

**座舱模式**：选一架正在飞的客机，切换到座舱视角，跟着飞机实时飞越真实地形。

**传感器风格**：CRT 显示风格、夜视仪、FLIR 热成像、黑色电影风格、暴雪滤镜——纯视觉效果，按自己喜好切换。

**语音控制**：接入 OpenAI Realtime API 后可以说话控制，28 个可调用工具（找飞机、切视角、量距离等）。每分钟约 $0.04，不想花钱也可以不开。

**Whiteboard 标注**：在地球表面画自定义标注，持久保存，可分享 URL（摄像机状态编码进 URL）。

**场景导演**：设置关键帧，导出电影感镜头切换序列。

---

## 技术架构

**核心技术**：原生 JavaScript（无框架）、CesiumJS 地球引擎、WebGL 渲染、Vite 构建工具。

**底图**：Google Photorealistic 3D Tiles——也就是 Google 地图那个照片级 3D 建筑渲染，可选 Cesium ion 或 Esri 卫星影像（不需要任何 Key）。

**卫星轨道**：SGP4 两行轨道根数传播算法，来自 CelesTrak 公开 TLE 数据，本地磁盘缓存避免频繁请求。

**数据补偿**：OpenSky 等接口更新间隔 15–30 秒，代码用内插和航位推测（dead reckoning）填补空隙，飞机不会在地图上跳格子。

**安全设计**：
- 服务端凭证代理 + SSRF 防护
- 请求预算 + 缓存（OpenSky credit governor）
- 只绑定本地端口，不暴露网络
- 所有数据来自公开渠道，无人脸识别，无个人追踪

---

## 安装

**Pinokio 图形界面（推荐）**：安装 Pinokio 8.2+，在里面打开 God's Eye View，点 Install → Start，完成。

**命令行**：

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
npm ci
npm run doctor
npm run dev
```

访问 http://localhost:4173，需要 Node.js 24.14+ 或 26.x。

**API Key 可选**：
- 不需要任何 Key 就能启动——底图用 Esri 卫星影像
- Cesium ion（免费配额）接入后升级到 Google 3D Tiles
- AISStream（免费注册）接入船只数据
- OpenAI Realtime API（~$0.04/分钟）开启语音控制

---

## 适合谁

说是"间谍卫星模拟器"，实际上它是一个**把公开数据做了极致视觉整合的工具**。

对普通用户：打开坐进某架飞机的座舱看实时飞行，或者盯着地球看一会儿自动刷新的实时火灾和地震点，五分钟内就能上瘾。

对开发者和 GIS 从业者：这是一套完整的实时地理空间可视化参考实现，CesiumJS + 多源数据融合 + 性能优化的完整示例。Issues 里有不少坐标系、渲染和 API 限速的技术讨论。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/bilawalsidhu/gods-eye-view
> License: MIT | Stars: 35,238 | Forks: 7,053 | Language: JavaScript

---

God's Eye View defines itself as: **a spy satellite simulator in your browser, except the data is real.**

It renders 15 live public data feeds on a photorealistic 3D globe. No API key required to start. Opens in an ordinary MacBook browser with a 1.86-second cold start. Hit GitHub Trending #1 in August 2026, now at 35K+ stars.

---

## 15 Real-Time Data Layers

| Layer | Source | Notes |
|-------|--------|-------|
| Commercial aircraft | OpenSky + adsb.lol | 11,000+ live tracked, per-class 3D models |
| Military traffic | adsb.lol | ADS-B military flights |
| Vessels | AISStream | Global AIS ship signals |
| Satellites | CelesTrak | 838 tracked objects, SGP4 orbit propagation |
| Earthquakes | USGS | 24-hour rolling window |
| Traffic | OSM + TomTom | Road vehicles, optional live speeds |
| Public cameras | Public CCTV database | ~3,600 cameras projected into 3D space |
| Radio | Geolocated stations | Analog tuner interface |
| Transit | GTFS-Realtime | Live buses, trains, ferries |
| Bikeshare | City open APIs | Station availability |
| Active fires | NASA FIRMS | Satellite hotspot detections |
| Space missions | Launch calendar | 30-day calendar with replay |
| Directions | OSRM | Terrain-draped routing |

---

## Things to Do With It

**Cockpit mode**: Pick any airborne aircraft and ride along in cockpit view over real terrain — live.

**Sensor styles**: CRT display, night vision, FLIR thermal, film noir, snowstorm filter — all aesthetic overlays.

**Voice control**: With OpenAI Realtime API connected (~$0.04/min), 28 voice tools are available — find aircraft, switch views, measure distances. Skip it to keep it free.

**Whiteboard annotations**: Draw on the globe surface, persistent storage, shareable URL encoding camera state.

**Scene director**: Set keyframes, export cinematic camera transitions.

---

## Technical Architecture

**Core**: Vanilla JavaScript (no framework), CesiumJS globe engine, WebGL rendering, Vite build tool.

**Basemap**: Google Photorealistic 3D Tiles — the same photo-realistic 3D building rendering from Google Maps — with Cesium ion or Esri satellite imagery as no-key fallbacks.

**Satellite orbits**: SGP4 propagation from CelesTrak public TLE data, disk-cached to rate-limit requests.

**Data smoothing**: OpenSky and similar feeds update every 15–30 seconds. The code uses interpolation and dead reckoning to fill gaps — aircraft don't teleport.

**Security**: Server-side credential brokering with SSRF protection, request budgeting, localhost-only binding, public data sources only, no facial recognition, no individual tracking.

---

## Installation

**Pinokio GUI (recommended)**: Install Pinokio 8.2+, open God's Eye View in Pinokio, click Install → Start.

**Command line**:

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
npm ci
npm run doctor
npm run dev
```

Open http://localhost:4173. Requires Node.js 24.14+ or 26.x.

**API keys are all optional**: Esri satellite imagery works with no keys at all. Cesium ion (free quota) upgrades to Google 3D Tiles. AISStream (free signup) adds ship data. OpenAI Realtime API adds voice.

---

## Who It's For

It bills itself as a "spy satellite simulator" but really it's **a reference implementation of real-time geospatial visualization built from public data**.

For casual users: ride a live flight in cockpit view, or watch earthquake dots and fire hotspots update in real time — it's genuinely absorbing in five minutes.

For developers and GIS practitioners: complete CesiumJS + multi-source data fusion reference implementation with performance optimization. The issues tracker has substantial technical discussion on coordinate systems, rendering, and API rate limiting.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
