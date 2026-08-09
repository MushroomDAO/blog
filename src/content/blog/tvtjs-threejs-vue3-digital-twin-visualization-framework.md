---
title: "TvT.js：把 Three.js + Vue 3 变成数字孪生快速交付框架"
titleEn: "TvT.js: Three.js + Vue 3 as a Plugin-Based Digital Twin Delivery Framework"
description: "IceGL 出品的 TvT.js 把 ThreeJS、Vue 3、TresJS 融为一体，提供插件化架构 + 在线3D编辑器 + 动态组件服务，让数字孪生和工业可视化项目快速落地。2347 stars，永久开源免费商用，支持信创环境。"
descriptionEn: "IceGL's TvT.js merges Three.js, Vue 3, and TresJS into one framework with a plugin architecture, online 3D editor, and dynamic component service for rapid digital-twin and industrial visualization delivery. 2347 stars, permanently open-source, free for commercial use, xinchuang-compatible."
pubDate: "2026-07-23"
updatedDate: "2026-07-23"
category: "Tech-Experiment"
tags: ["Three.js", "Vue3", "数字孪生", "3D可视化", "开源", "工业可视化", "WebGL", "信创", "低代码"]
heroImage: "../../assets/images/tvtjs-threejs-vue3-digital-twin-visualization-framework-banner.jpg"
---

> **仓库**：hawk86104/three-vue-tres · Vue · Apache 2.0 · 2347 stars  
> **官网**：opensource.icegl.cn  
> **在线编辑器**：zone3deditor.icegl.cn  
> **动态组件服务**：dcser.icegl.cn  
> **出品**：ICEGL 团队（冰哥、地虎降天龙、石头web 等）

---

## 一、一句话定位

TvT.js = **ThreeJS + Vue 3 + TresJS**，做的是「让3D可视化项目快速落地」的框架层。

不是一个组件库，也不是一个编辑器——是一套**插件化的交付体系**：场景编辑器生产插件，插件部署到业务系统，业务系统通过动态组件加载服务（dcser）按需组合。

定位人群：做数字孪生、工业可视化、智慧园区的前端团队，不想从零搭 Three.js 脚手架。

---

## 二、技术栈

| 层 | 技术 |
|---|---|
| 3D 渲染 | ThreeJS r18x（2025年10月从 r17x 升级） |
| 声明式封装 | TresJS V5 + Cientos V4 |
| 前端框架 | Vue 3 + Fes V4 |
| 扩展能力 | WebGL / WebGPU，Gaussian Splatting，GIS（高德），物理引擎（Cannon） |
| 部署目标 | Web / 微信小程序 / App 全端 |

---

## 三、两个核心产品

### 在线 3D 场景编辑器（zone3Deditor）

地址：`zone3deditor.icegl.cn`

编辑器是交付链路的起点。用可视化方式搭建3D场景，配置插件，导出源码——「可二次开发」是设计目标，不是黑箱产出。

官方 showcase 里从这个编辑器直接输出的项目：

| 项目 | 内容 |
|---|---|
| 智慧机房 | 服务器机柜可视化，实时状态 |
| 炼化智慧工厂 | 工业4.0场景，流程监控 |
| 智慧仓储管理 | 立体仓库 + 货物追踪 |
| 智慧办公楼层 | 楼层平面图 + 人员分布 |
| 无人机编队 | 低空飞行可视化 |
| 海洋航运 | 船队轨迹 + 货运状态 |

### 动态组件发布加载服务（dcser）

地址：`dcser.icegl.cn`

把插件发布到 dcser，业务系统运行时按需动态加载，不需要重新打包部署。

这解决了大型3D可视化项目的一个真实痛点：场景太多，全部打包进主包体积爆炸；但每次更新场景又需要重新部署。dcser 把场景插件变成独立发布单元。

---

## 四、插件生态

TvT.js 的核心是插件。官方开源库里已有的插件类别：

**基础**：材质展示、控制器、内嵌 DOM、发光/Shine 效果、后期处理

**行业场景**：数字城市、数字园区、工业4.0、医疗、电商

**能力扩展**：
- 高斯泼渐（Gaussian Splatting）—— 支持 `.ply` 点云和 `.splat` 格式，有针对 Web 场景的 splat → glb 压缩方案
- GIS（高德地图集成）
- 热力图、LOD、物理引擎
- 混元3D图生模型集成（hunyuan3D）
- geokit 地理渲染工具（高性能、低复杂度，替代 Cesium 复杂 SDK 路线）
- goView 低代码 UI 集成

---

## 五、信创/国产化适配

这是文档里单独列出来的能力，值得单独说：

- 支持国产硬件平台（龙芯、飞腾、鲲鹏等）
- 支持国产操作系统和浏览器（统信 UOS、麒麟、360 安全浏览器等）
- 软件著作权登记，独立知识产权
- 完全开源依赖栈

对于需要做政府/国企数字化项目的团队，这个清单实际上是采购门槛的直接回应。

---

## 六、生态规模

- GitHub stars：2347 · Forks：177
- Gitee 镜像 + GitCode 镜像同步维护
- 微信小程序版（全量案例可在小程序里浏览）
- Bilibili 教程频道（冰哥 B 站 + 地虎 B 站）
- QQ 群 + 微信群社区
- 插件市场（icegl.cn/tvtstore）付费插件生态

---

## 七、判断

TvT.js 解决的问题很具体：**降低 Three.js 项目从原型到交付的摩擦**。

不是包装一个组件库给人用，而是把整个交付链路（编辑器 → 插件 → 动态加载 → 多端部署）都搭好。对于有批量3D可视化项目需求的团队，这套体系的价值在于复用——每个新项目不需要重新搭架子，只需要开发新插件。

Gaussian Splatting + 混元3D 的集成说明方向：从纯手建3D场景，往「用真实数据/AI 生成内容」演进。这是数字孪生行业当前的真实趋势，TvT.js 在框架层跟上了。

geokit 的出现有意思：直接说「是否在为 Cesium 复杂的 SDK 烦恼」——这是在明确抢 Cesium 的用户。高性能 + 低复杂度的 GIS 渲染，如果质量过关，对中小项目团队是很好的替代选项。

---

*数据来源：GitHub hawk86104/three-vue-tres，docs.icegl.cn，opensource.icegl.cn，2026-07-23 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: hawk86104/three-vue-tres · Vue · Apache 2.0 · 2347 stars
> **Official site**: opensource.icegl.cn
> **Online editor**: zone3deditor.icegl.cn
> **Dynamic component service**: dcser.icegl.cn
> **By**: ICEGL Team (Bingg, Dihu Jiangtianlong, Shitou Web, et al.)

---

## 1. In One Sentence

TvT.js = **ThreeJS + Vue 3 + TresJS**, a framework layer designed to "get 3D visualization projects shipped fast."

Not a component library, not an editor — it is a **plugin-based delivery system**: the scene editor produces plugins, plugins deploy to business systems, and business systems compose them on demand via the dynamic component loading service (dcser).

Target audience: frontend teams building digital twins, industrial visualization, and smart campuses who do not want to scaffold Three.js from scratch.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| 3D Rendering | ThreeJS r18x (upgraded from r17x in October 2025) |
| Declarative Wrapper | TresJS V5 + Cientos V4 |
| Frontend Framework | Vue 3 + Fes V4 |
| Extended Capabilities | WebGL / WebGPU, Gaussian Splatting, GIS (Amap), Physics Engine (Cannon) |
| Deployment Targets | Web / WeChat Mini Program / App (all platforms) |

---

## 3. Two Core Products

### Online 3D Scene Editor (zone3Deditor)

URL: `zone3deditor.icegl.cn`

The editor is the starting point of the delivery pipeline. It builds 3D scenes visually, configures plugins, and exports source code — "secondary development" is a design goal, not a black-box output.

Projects directly output from this editor in the official showcase:

| Project | Content |
|---|---|
| Smart Data Center | Server rack visualization, real-time status |
| Refinery Smart Factory | Industry 4.0 scenario, process monitoring |
| Smart Warehouse Management | Multi-tier warehouse + cargo tracking |
| Smart Office Floor | Floor plan + personnel distribution |
| Drone Swarm | Low-altitude flight visualization |
| Ocean Shipping | Fleet tracking + cargo status |

### Dynamic Component Publishing & Loading Service (dcser)

URL: `dcser.icegl.cn`

Publish plugins to dcser; business systems load them dynamically at runtime on demand, with no repackaging or redeployment required.

This addresses a genuine pain point in large-scale 3D visualization projects: too many scenes inflate the main bundle to an unmanageable size, yet every scene update requires redeployment. dcser turns scene plugins into independent publishing units.

---

## 4. Plugin Ecosystem

The core of TvT.js is its plugins. Categories already available in the official open-source repository:

**Fundamentals**: material showcase, controllers, embedded DOM, glow/Shine effects, post-processing

**Industry Scenarios**: digital city, digital campus, Industry 4.0, healthcare, e-commerce

**Capability Extensions**:
- Gaussian Splatting — supports `.ply` point clouds and `.splat` format, with a splat → glb compression pipeline for web scenarios
- GIS (Amap integration)
- Heatmap, LOD, physics engine
- Hunyuan3D image-to-model integration (hunyuan3D)
- geokit geospatial rendering tool (high performance, low complexity — an alternative to Cesium's heavy SDK)
- goView low-code UI integration

---

## 5. Xinchuang / Domestic Adaptation

This capability is listed separately in the documentation and merits separate discussion:

- Supports domestic hardware platforms (Loongson, Phytium, Kunpeng, etc.)
- Supports domestic operating systems and browsers (UnionTech UOS, Kylin, 360 Secure Browser, etc.)
- Software copyright registration, independent intellectual property
- Fully open-source dependency stack

For teams delivering government or state-enterprise digitalization projects, this list is a direct response to procurement requirements.

---

## 6. Ecosystem Scale

- GitHub stars: 2347 · Forks: 177
- Gitee mirror + GitCode mirror, both actively maintained
- WeChat Mini Program version (full case library browsable in the Mini Program)
- Bilibili tutorial channels (Bingg's channel + Dihu's channel)
- QQ group + WeChat community groups
- Plugin marketplace (icegl.cn/tvtstore) with paid plugin ecosystem

---

## 7. Assessment

TvT.js solves a specific problem: **reducing friction in taking Three.js projects from prototype to delivery**.

It does not wrap a component library for end users; it builds out the entire delivery pipeline (editor → plugins → dynamic loading → multi-platform deployment). For teams with a steady stream of 3D visualization projects, the value of this system lies in reuse — each new project requires no new scaffolding, only new plugin development.

The Gaussian Splatting + Hunyuan3D integrations signal a direction: moving from purely hand-crafted 3D scenes toward "real-data / AI-generated content." This is the current actual trajectory of the digital twin industry, and TvT.js has kept pace at the framework level.

The emergence of geokit is notable: it openly asks "are you tired of Cesium's complex SDK?" — a direct play for Cesium's user base. High-performance, low-complexity GIS rendering, if quality holds, is a compelling alternative for small-to-mid-size project teams.

---

*Data source: GitHub hawk86104/three-vue-tres, docs.icegl.cn, opensource.icegl.cn, collected 2026-07-23.*

© 2026 Author: Mycelium Protocol
