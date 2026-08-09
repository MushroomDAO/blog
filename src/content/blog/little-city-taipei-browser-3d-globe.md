---
title: "little-city：把每座城市做成浏览器里的小星球"
titleEn: "little-city: Every City as a Tiny Explorable Planet in Your Browser"
description: "craftmygame/little-city 把台北做成了浏览器里可探索的卡通小星球：夜市、庙宇、台北 101，按真实方位角和距离放置。目标是为世界上每座城市都做一个版本，已有台北和巴黎。three.js + Antics 多人，AI 可直接贡献地标。"
descriptionEn: "craftmygame/little-city turns Taipei into an explorable cartoon globe in the browser — night markets, temples, and Taipei 101 placed at real bearings and distances. The goal is one version for every city on Earth; Taipei and Paris are live. Built on three.js + Antics multiplayer; AI can contribute landmarks directly."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["three.js", "浏览器游戏", "开源", "城市建设", "3D", "多人游戏", "AI贡献", "地图", "JavaScript"]
heroImage: "../../assets/images/little-city-taipei-browser-3d-globe-banner.jpg"
---

> **仓库**：craftmygame/little-city · JavaScript · Apache 2.0  
> **已有城市**：little-taipei（台北）、little-paris（巴黎）  
> **运行**：`git clone ... && python3 -m http.server 4173`，打开 `http://localhost:4173/little-taipei/`

---

## 一、一个很大的野心，从台北开始

> "We want to build a little planet for every city in the world, and we're starting here."

台北，变成了一个可以在浏览器里探索的小星球。

卡通渲染（cel-shaded），手工放置的 3D 地球仪。夜市、庙宇、台北 101、淡水河——每一个地标的位置都按真实的方位角和距离放置，相对台北 101 为原点，以公里为单位。**感觉就像真的城市，因为地理关系是真的。**

这是 little-city 的第一座城市。目标：为世界上每一座城市都做一个这样的小星球版本。

---

## 二、怎么玩

```bash
git clone https://github.com/craftmygame/little-city.git
cd little-city && python3 -m http.server 4173
```

打开 `http://localhost:4173/little-taipei/`。

- **WASD**：移动
- **Space**：跳
- **E**：交互

本地运行是单人模式。部署到 [Antics](https://antics.gg) 后解锁多人：房间、同步玩家、表情、排行榜——不需要自己维护服务器。

---

## 三、三层架构

城市由三层组成，分工清晰：

| 层 | 文件 | 内容 |
|---|---|---|
| **位置数据** | `city/taipei.js` | 地标在哪里、有多大（真实公里坐标） |
| **建筑几何** | `buildings/*.js` | 每个地标长什么样（three.js builder 函数） |
| **渲染引擎** | `main.js` | 渲染和游戏逻辑（城市贡献几乎不需要改它） |

**坐标系**：`[eastKm, northKm]`，相对台北 101 为原点。负值 = 西或南。

### 地标数据格式

```js
{
  id: 'example-library',
  name: 'Example Library',
  builder: 'buildExampleLibrary',
  at: [-2.4, 1.1],              // 相对台北 101 的公里坐标
  placement: {
    foot: 3.2,                  // 地基占地大小
    ar: 2.4,                    // 碰撞圆半径
    labelY: 5,                  // 浮动标签高度
    face: 90,                   // 朝向（顺时针度数）
    base: '#d8d2c4'             // 广场铺地颜色
  },
}
```

### 地面自动平整

有一个很聪明的系统：建筑模型不需要适配星球曲率。

运行时会在每个地标的脚印下**自动抬起地面**成为一个平台（用 `base` 颜色铺成广场地砖），超出脚印后平滑过渡回球面曲率。墙壁、地板、门口全都落在真正水平的地面上，星球的弧度从广场边缘开始弯走。

---

## 四、路网和公园

不只是地标，城市数据还包含道路和公共空间。

**道路**：一条路的定义生成完整的人行道、柏油路面、中心线、建筑退缩区、行道树和路灯。

```js
{
  id: 'example-road',
  name: 'Example Road',
  widthKm: 0.22,
  path: [[-3.0, 1.0], [-1.0, 1.1], [1.5, 0.9]],
}
```

**公园**：影响地面颜色、程序化建筑密度和绿植生成。

```js
{ id: 'example-park', name: 'Example Park', at: [-1.2, -0.8], radiusKm: 0.45 }
```

---

## 五、AI 可以直接贡献地标

这个项目的设计里有一个有意思的细节：

> 🧋 **Come help make Taipei more real.** Got some Claude Code or Codex tokens? Add a landmark, improve a building, and send a PR. No 3D experience needed.

每个地标是独立的 builder 函数，有明确的接口约定（base at `y=0`，`+Y` up，`+Z` 朝正面）。CONTRIBUTING.md 里有完整的配方可以复制。

官方提供的 AI 贡献 prompt：

```
Follow little-taipei/CONTRIBUTING.md. Add the Dragon Mountain / a new landmark
in the appropriate buildings/ file, place it in city/taipei.js, run npm run check,
then serve the city and confirm it renders without console errors.
```

把这段话发给 Claude Code 或 Codex，它可以直接找到文件、写 builder 函数、加坐标数据、跑验证、确认渲染正常——一个完整的地标贡献，不需要你懂 three.js。

一个 PR 一个地标，恰好匹配 AI agent 的工作粒度。

---

## 六、已经有两座城市

仓库里已经有：

- **little-taipei**：台北，夜市、庙宇、台北 101、淡水河
- **little-paris**：巴黎

每座城市是一个独立目录，自成一体。第三座、第四座在路上。

---

## 七、多人：Antics

本地运行是单人模式，部署到 Antics 解锁多人——这个选择值得单独说一下。

Antics（antics.gg）是一个专为浏览器游戏设计的多人中间件，它处理房间创建、玩家状态同步、表情、排行榜——**不需要你维护任何服务器**。

对 little-city 来说，这意味着城市建造者可以只关注城市本身（three.js 模型和地理数据），多人基础设施完全外包出去。

---

## 八、判断

little-city 的核心想法是：**城市是可以被社区拼出来的。**

不是一个游戏公司把城市做进游戏里，而是每个人贡献一个地标——自己家附近的庙，自己常去的夜市摊，自己知道的那个公园——慢慢把真实的空间关系还原成一个可以走进去的小星球。

AI 贡献的设计更有意思：当每个地标都是一个符合接口的独立模块，当坐标系是真实地理，当 CONTRIBUTING.md 足够清楚——AI agent 可以从 Google 地图或 Wikipedia 里找到地标的位置、根据照片生成大致的 three.js 几何、写进 city/taipei.js，然后开 PR。这不是辅助贡献，是可以作为主力的贡献模式。

**every city in the world**——这是一个需要整个社区来完成的目标，也是唯一能完成它的方式。

---

*数据来源：GitHub craftmygame/little-city，2026-07-22 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: craftmygame/little-city · JavaScript · Apache 2.0  
> **Cities available**: little-taipei (Taipei), little-paris (Paris)  
> **Run**: `git clone ... && python3 -m http.server 4173`, open `http://localhost:4173/little-taipei/`

---

## 1. A Very Big Ambition, Starting with Taipei

> "We want to build a little planet for every city in the world, and we're starting here."

Taipei has become an explorable little planet in the browser.

A cel-shaded, hand-crafted 3D globe. Night markets, temples, Taipei 101, the Tamsui River — every landmark placed at its true bearing and distance, using Taipei 101 as the origin, measured in kilometers. **It feels like the real city, because the geography is real.**

This is little-city's first city. The goal: a little planet version like this for every city in the world.

---

## 2. How to Play

```bash
git clone https://github.com/craftmygame/little-city.git
cd little-city && python3 -m http.server 4173
```

Open `http://localhost:4173/little-taipei/`.

- **WASD**: Move
- **Space**: Jump
- **E**: Interact

Running locally is single-player mode. Deploying to [Antics](https://antics.gg) unlocks multiplayer: rooms, synchronized players, emotes, leaderboards — no need to maintain your own server.

---

## 3. Three-Layer Architecture

A city is composed of three layers with a clear division of responsibilities:

| Layer | File | Contents |
|---|---|---|
| **Position data** | `city/taipei.js` | Where landmarks are and how large (real kilometer coordinates) |
| **Building geometry** | `buildings/*.js` | What each landmark looks like (three.js builder functions) |
| **Rendering engine** | `main.js` | Rendering and game logic (city contributions rarely need to touch this) |

**Coordinate system**: `[eastKm, northKm]`, relative to Taipei 101 as origin. Negative values = west or south.

### Landmark Data Format

```js
{
  id: 'example-library',
  name: 'Example Library',
  builder: 'buildExampleLibrary',
  at: [-2.4, 1.1],              // 相对台北 101 的公里坐标
  placement: {
    foot: 3.2,                  // 地基占地大小
    ar: 2.4,                    // 碰撞圆半径
    labelY: 5,                  // 浮动标签高度
    face: 90,                   // 朝向（顺时针度数）
    base: '#d8d2c4'             // 广场铺地颜色
  },
}
```

### Automatic Ground Leveling

There is a clever system: building models do not need to adapt to the planet's curvature.

At runtime, the ground is **automatically raised** beneath each landmark's footprint into a platform (paved as a plaza in the `base` color), then smoothly transitions back to the spherical curvature beyond the footprint. Walls, floors, and entrances all sit on truly level ground; the planet's curve resumes from the plaza's edge.

---

## 4. Road Network and Parks

Not just landmarks — city data also includes roads and public spaces.

**Roads**: A single road definition generates complete sidewalks, asphalt surface, center line, building setback zones, street trees, and streetlights.

```js
{
  id: 'example-road',
  name: 'Example Road',
  widthKm: 0.22,
  path: [[-3.0, 1.0], [-1.0, 1.1], [1.5, 0.9]],
}
```

**Parks**: Affect ground color, procedural building density, and vegetation generation.

```js
{ id: 'example-park', name: 'Example Park', at: [-1.2, -0.8], radiusKm: 0.45 }
```

---

## 5. AI Can Contribute Landmarks Directly

There is an interesting detail in this project's design:

> 🧋 **Come help make Taipei more real.** Got some Claude Code or Codex tokens? Add a landmark, improve a building, and send a PR. No 3D experience needed.

Each landmark is an independent builder function with a clear interface contract (base at `y=0`, `+Y` up, `+Z` facing front). CONTRIBUTING.md contains a complete recipe to copy.

The official AI contribution prompt:

```
Follow little-taipei/CONTRIBUTING.md. Add the Dragon Mountain / a new landmark
in the appropriate buildings/ file, place it in city/taipei.js, run npm run check,
then serve the city and confirm it renders without console errors.
```

Send this to Claude Code or Codex, and it can find the files, write the builder function, add coordinate data, run validation, and confirm the rendering is error-free — a complete landmark contribution without any three.js knowledge required.

One PR per landmark, matching exactly the working granularity of an AI agent.

---

## 6. Two Cities Already

The repository already includes:

- **little-taipei**: Taipei — night markets, temples, Taipei 101, the Tamsui River
- **little-paris**: Paris

Each city is a self-contained independent directory. A third and fourth are on the way.

---

## 7. Multiplayer: Antics

Running locally is single-player mode; deploying to Antics unlocks multiplayer — this choice deserves a closer look.

Antics (antics.gg) is a multiplayer middleware designed specifically for browser games. It handles room creation, player state synchronization, emotes, and leaderboards — **no server maintenance required on your part**.

For little-city, this means city builders can focus solely on the city itself (three.js models and geographic data), with multiplayer infrastructure fully outsourced.

---

## 8. Assessment

The core idea of little-city is: **a city can be assembled by the community.**

Not a game company building a city into a game, but every person contributing one landmark — the temple near their home, the night market stall they frequent, the park they know — gradually restoring real spatial relationships into a little planet you can walk through.

The AI contribution design is even more interesting: when every landmark is an independent module with a clear interface, when the coordinate system is real geography, when CONTRIBUTING.md is clear enough — an AI agent can find a landmark's location from Google Maps or Wikipedia, generate approximate three.js geometry from photos, write it into city/taipei.js, and open a PR. This is not auxiliary contribution — it is a contribution mode that can serve as the primary driver.

**every city in the world** — this is a goal that requires the entire community to accomplish, and it is the only way it can be accomplished.

---

*Data source: GitHub craftmygame/little-city, collected 2026-07-22.*

© 2026 Author: Mycelium Protocol
