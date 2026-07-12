---
title: "宅在家也能封神：造个小世界，再备一套末日知识库"
titleEn: "Homebody God Mode: Build a Tiny World + Set Up an Offline Survival Knowledge Base"
description: "两个开源项目送给不想出门的人：tiny-world-builder 让你在浏览器里造一个 3D 体素小世界，Project N.O.M.A.D 让你在断网断电的末日里依然有 AI、有百科全书、有地图。"
descriptionEn: "Two open-source projects for the indoor generation: tiny-world-builder lets you sculpt a 3D voxel world in your browser, while Project N.O.M.A.D gives you AI, Wikipedia, and offline maps when the internet goes dark."
pubDate: "2026-07-12"
updatedDate: "2026-07-12"
category: "Tech-Experiment"
tags: ["开源", "宅男", "末日备灾"]
heroImage: "../../assets/images/zhai-nan-home-lab-tiny-world-project-nomad-banner.jpg"
---

> 本文介绍两个气质截然不同却互补的开源项目：**tiny-world-builder**（1.4k⭐，纯浏览器 3D 体素世界编辑器）和 **Project N.O.M.A.D**（33k⭐，离线末日知识服务器）。一个用来造梦，一个用来防灾。

---

## 先说人设

周六下午，门关上，窗帘拉好。

不是因为有什么不可告人的事，只是外面的世界——那些约饭、堵车、小红书上的"这家必打卡"——和你现在的状态不太匹配。

你想的是：**一台电脑，一杯水，一个下午，不被打扰。**

这篇文章就是给这种状态写的。

---

## 上半场：造一个属于自己的小世界

### tiny-world-builder 是什么

GitHub 仓库：`jasonkneen/tiny-world-builder`，1,428 颗星，2026 年 5 月上线。

作者做了一件极克制的事：把整个 3D 体素世界编辑器，塞进**一个 HTML 文件**里。

不用 npm install，不用 Node.js，不用配置环境。打开浏览器，拖进去，开始玩。

| 功能 | 说明 |
|------|------|
| 地形建造 | 放置地块、小路、农田、树木、建筑、动物 |
| 地形雕刻 | 抬高/压低/涂色地面，凿悬崖、挖河道 |
| 飞行浏览 | 多种相机模式，从鸟瞰到第一人称自由穿梭 |
| 分享导出 | 保存到本地、导出文件、和别人交换世界 |

底层是 Three.js r185，全部自托管，运行时不依赖任何外部 CDN。

### 怎么开始

```bash
# 方案 A：直接下载 HTML 文件，浏览器拖入
# 去 releases 页下载 tiny-world-builder.html → 浏览器打开

# 方案 B：本地开发版（可改代码）
git clone https://github.com/jasonkneen/tiny-world-builder
npm run dev
# → http://localhost:3000/tiny-world-builder
```

界面左侧是工具栏，右侧是 3D 画布，鼠标左键放置，右键删除，滚轮缩放，中键旋转视角。

### 能玩出什么花样

**还原脑子里那个村子**。你想过吗？有个地方你特别想住——可能是小时候看的动漫里的，可能是游戏里路过的，可能是莫名其妙梦到的。tiny-world-builder 就是你拿来还原它的地方。

**给家人造一个家**。体素风格简单易懂，不会画画也能用它做出一个「送给妈妈的像素故乡」。

**一个人的城市规划实验**。放几条路，配几个区块，看看什么样的布局让你觉得舒服——这其实是一种低成本的空间思维训练。

---

## 下半场：防一防你不确定会不会来的末日

### Project N.O.M.A.D 是什么

GitHub 仓库：`Crosstalk-Solutions/project-nomad`，**33,625 颗星，3,374 次 Fork**。

全称 Node for Offline Media, Archives, and Data。

作者是 Chris Sherwood，YouTuber，Crosstalk Solutions 频道 38 万订阅。他做这个的初衷很直接：**网络断了，你手上还有什么？**

N.O.M.A.D 的答案是：一台你自己的服务器，装满了你可能用到的一切。

| 模块 | 说明 |
|------|------|
| 本地 AI 对话 | Ollama 驱动，支持 RAG（文件上传 + 语义搜索），完全离线 |
| 离线百科全书 | Kiwix 提供的维基百科、医学参考书、电子书等 |
| 离线课程 | Khan Academy 完整课程，带学习进度追踪（Kolibri） |
| 离线地图 | ProtoMaps，可下载本地区域地图 |
| 管理界面 | "Command Center"，浏览器访问，Docker 编排 |

### 怎么装

系统要求：Ubuntu/Debian，或 Windows WSL2。一条命令搞定：

```bash
sudo apt-get update && \
sudo apt-get install -y curl && \
curl -fsSL https://raw.githubusercontent.com/Crosstalk-Solutions/project-nomad/refs/heads/main/install/install_nomad.sh \
  -o install_nomad.sh && \
sudo bash install_nomad.sh
```

装完后浏览器访问 `http://localhost:8080`，Command Center 就出来了。

Windows 用户：按官方 WSL2 指南走，社区有完整文档。

树莓派 5 / 旧 NUC / 闲置的 Mac mini：都能装，功耗低，24 小时挂在那里消耗不了多少电费。

### 它解决的其实不只是「末日」问题

说末日有点夸张，但它解决的场景比你想象的常见：

- **出差去没 VPN 的地方** → 带着 N.O.M.A.D 的 IP，你有本地 AI
- **家里网络限速/断线** → 维基百科、Khan Academy 照常用
- **想学一门技能但不想分心刷社交媒体** → 把 Kolibri 开着，课程就在那里，干扰源不在
- **给孩子做一个干净的学习环境** → 离线课程 + 离线百科，没有推荐算法

---

## 怎么把两个结合起来玩

一台普通主机，两件事同时做：

```
主屏                      副屏（或同一屏分窗）
────────────────────────  ────────────────────────
tiny-world-builder        N.O.M.A.D Command Center
浏览器建造小世界            本地 AI 陪你聊世界设定
```

比如你在 tiny-world-builder 里造了一个中世纪小镇，然后切到 N.O.M.A.D 的本地 AI，问它：「一个中世纪小镇的集市通常有哪些行业？铁匠和面包师的工作坊怎么布局？」

AI 根据你上传的参考文档（历史书、世界观设定笔记）给你回答，你再回到体素编辑器，按照它说的布局去建。

这其实是一个极低摩擦的「沉浸式创作循环」：**造世界 → 问 AI → 改世界 → 再问**。

---

## 硬件清单（可选）

不是非买不可，但如果你想把这套玩得更认真：

| 设备 | 用途 | 参考价 |
|------|------|--------|
| 树莓派 5 8GB | 跑 N.O.M.A.D 24h 节点 | ~¥800 |
| 500GB SSD | 存离线维基百科、地图 | ~¥300 |
| 旧 Mac mini / NUC | 如果已有，直接用 | ¥0 |
| UPS 不间断电源 | 真末日用（也防停电） | ¥200–600 |

只想试试效果，直接在 MacBook 或 Windows 本地装就行，不需要额外硬件。

---

## 总结

| 项目 | 适合谁 | 门槛 |
|------|--------|------|
| tiny-world-builder | 想造个小世界、有创作欲望的人 | 零门槛，打开 HTML 就开始 |
| Project N.O.M.A.D | 想备份知识、不想完全依赖云服务的人 | 会用命令行即可 |

宅在家不是在逃避什么，而是在认真对待一种生活方式：**减少噪声，增加密度**。

一个给你造梦的工具，一个给你储粮的工具，够了。

---

GitHub：
- tiny-world-builder：github.com/jasonkneen/tiny-world-builder
- Project N.O.M.A.D：github.com/Crosstalk-Solutions/project-nomad
- N.O.M.A.D 官网：projectnomad.us

© 2026 Author: Mycelium Protocol

<!--EN-->

## Homebody God Mode: Build a Tiny World + Set Up an Offline Survival Knowledge Base

> Two open-source tools for people who prefer staying in: **tiny-world-builder** (1.4k⭐, browser-based 3D voxel editor) and **Project N.O.M.A.D** (33k⭐, offline survival knowledge server). One for making worlds, one for surviving them.

---

### Part 1: Build Your Own World

**tiny-world-builder** (github.com/jasonkneen/tiny-world-builder) packs an entire 3D voxel world editor into a single HTML file. No npm install. No config. Open it in a browser and start placing terrain, buildings, animals, and crops.

The builder runs on self-hosted Three.js r185 — zero runtime CDN dependencies. It also deploys as a static site on Vercel or Netlify if you want to share your worlds.

**What you can do:**
- Sculpt terrain: raise cliffs, dig rivers, paint ground textures
- Place objects: houses, paths, crops, trees, props, animals
- Fly through your world in multiple camera modes
- Export and share world files with others

```bash
# Zero-install path
open index.html  # drag the HTML file into any browser

# Dev path (for editing the source)
git clone https://github.com/jasonkneen/tiny-world-builder && npm run dev
```

---

### Part 2: Prepare for the Offline Era

**Project N.O.M.A.D** (33,625 stars) is a Docker-based offline knowledge server: AI chat with RAG, Wikipedia via Kiwix, Khan Academy courses, and downloadable maps — all running on `localhost:8080`, no internet required.

**One-line install (Ubuntu/Debian):**
```bash
curl -fsSL https://raw.githubusercontent.com/Crosstalk-Solutions/project-nomad/refs/heads/main/install/install_nomad.sh -o install_nomad.sh && sudo bash install_nomad.sh
```

**Practical offline use cases:**
- Local AI that works when your VPN doesn't
- Wikipedia and reference books when your ISP throttles
- A distraction-free learning environment for kids (no recommendation algorithms)
- Raspberry Pi 5 as a 24/7 low-power knowledge node

---

### The Creative Loop

Open tiny-world-builder in one tab and N.O.M.A.D's local AI in another. Build a medieval village, ask the AI about guild hall layouts and market square conventions, then go back and build them in. Low-friction, high-immersion creative loop.

---

**GitHub:**
- tiny-world-builder: github.com/jasonkneen/tiny-world-builder
- Project N.O.M.A.D: github.com/Crosstalk-Solutions/project-nomad
- N.O.M.A.D website: projectnomad.us

© 2026 Author: Mycelium Protocol
