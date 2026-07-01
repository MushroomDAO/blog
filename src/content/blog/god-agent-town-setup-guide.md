---
title: "像上帝一样掌控 AI 小镇：GOD 项目本地搭建完全指南"
titleEn: "Be a God to an Agent Town: Complete Local Setup Guide for the GOD Project"
description: "GOD（Govern·Observe·Direct）是一个开源的 AI Agent 社会实时控制台：暂停时间、向任意居民耳语发问、实时注入指令、一键重置世界。本文为普通开发者提供从零到可交互小镇的完整搭建指南，含 macOS/Linux/Windows 操作步骤、自定义小镇创建、地图扩展方法，以及与 Westworld、Sims 的对比分析。"
descriptionEn: "GOD (Govern·Observe·Direct) is an open-source real-time control room for AI agent societies: pause time, whisper to any resident, inject instructions, reset the world. Complete setup guide for ordinary developers — from zero to a working interactive town — including macOS/Linux/Windows steps, custom town creation, map extensions, and comparison with Westworld and Sims."
pubDate: "2026-07-01"
updatedDate: "2026-07-01"
category: "Tech-Experiment"
tags: ["AI Agent", "开源", "Generative Agents", "本地部署", "Agent社会", "仿真", "像素小镇"]
heroImage: "../../assets/images/god-agent-town-setup-guide-banner.jpg"
---

> **GitHub**: [XiaoLuoLYG/GOD](https://github.com/XiaoLuoLYG/GOD) · ⭐ 817 · 🍴 102 · Apache 2.0  
> **定位**: Govern · Observe · Direct — AI Agent 社会的实时控制台  
> **口号**: 🌩️ Be like a god to a town of agents.

---

## 这是什么？

想象你是一个城市模拟游戏里的上帝：你可以随时暂停时间，对任何一个 NPC 说一句话，然后看他们按照你改变的轨迹继续生活——但这里的每个居民，都是由 LLM 驱动的真实 AI Agent。

**GOD** 就是做这件事的工具。

它不只是让你「观察」一座 AI 小镇（那是其他 generative-agent 项目的定位），而是给了你一个**实时操控台**：

- ⏯️ **暂停时间**：随时 pause，按 step 回看每个 Agent 做了什么
- 💬 **耳语发问**：向某一个居民、一组人、或全镇居民发送自然语言问题
- 🎛️ **改写下一步**：注入指令，Agent 下一回合读到后立刻响应
- 🪄 **零代码配置**：浏览器向导完成模型配置、剧本设计、Agent 生成，不用改配置文件
- 🔄 **一键重置**：一条命令清掉历史数据，重新孵化一座干净小镇

---

## 项目实际效果

GOD 项目的实际控制台界面——左侧是像素小镇地图，居民在地图上实时移动；右侧是 Live Console，可以实时看到每个 Agent 的动作、对话和状态，也可以对任意居民发送指令。

![GOD 实时控制台](/screenshots/god-control-room.png)

*实时控制台：PKU 地图、step 控制、定向提问、居民列表全在一个界面里*

内置两个预设实验——The Ville 小镇（10 个有自己生活的居民）和 PKU 校园（特朗普访问事件）：

![The Ville 地图](/screenshots/god-map-the-ville.png)

*The Ville：10 位居民在家、学校、咖啡馆、公园、市场、药房、酒馆、宿舍之间度过普通一天*

---

## 技术栈和架构

在开始搭建之前，先了解 GOD 的架构：

```
你（操作员）
    ↓
浏览器控制台（React + Vite）
    ↕  实时命令 / 更新
本地 FastAPI 后端
    ↓  生成 Prompt
Agent Runtime（独立进程，WebSocket 连接）
    ↓  动作输出
像素小镇世界（结构化状态）
    ↓  每帧记录
本地 SQLite Replay Store
```

**完全本地运行**——控制台、后端、Agent Runtime、实验文件、Replay 数据都在你的电脑上。唯一需要连接外部的是你选择的 LLM 接口（OpenAI API 或任何兼容接口）。

**技术栈**：
- 后端：Python 3.11+ / FastAPI
- 前端：React 18 / Vite 6
- Agent Runtime：独立进程，本地 WebSocket 通信
- 地图格式：Tiled JSON（PNG tileset）

---

## 环境要求

| 条件 | 要求 |
|---|---|
| Python | 3.11 或更高 |
| Node.js | 18 或更高（脚本会自动安装） |
| Git | 任意版本 |
| 磁盘空间 | ~1 GB（含依赖） |
| LLM 接口 | OpenAI API key 或任意兼容接口（如 DeepSeek、本地 Ollama） |
| 网络 | 仅需访问 LLM 接口 |

> 支持 macOS、Linux、Windows（PowerShell）。

---

## 搭建步骤（macOS / Linux）

### 第一步：克隆仓库

```bash
git clone https://github.com/XiaoLuoLYG/GOD.git
cd GOD
```

### 第二步：一键启动

```bash
./scripts/god.sh start
```

**第一次运行**，这个脚本会自动：
1. 检查并安装 Python、Node.js 依赖（`uv`、`pip`、`npm`）
2. 启动 FastAPI 后端
3. 启动 React 前端（Vite）
4. 自动打开浏览器，进入**配置向导**

之后每次运行同样这一条命令，idempotent——已经跑着的服务不会重复启动。

### 第三步：在浏览器配置向导里完成设置

脚本启动后会自动打开浏览器，看到这个界面：

![GOD 配置向导](/screenshots/god-setup-wizard.png)

*配置向导：模型配置、实验选择、自建实验发布，全在浏览器里完成*

向导分 6 步：

**步骤 1：填写模型配置**
```
API Key:      sk-xxxxxxxx（你的 OpenAI API Key 或兼容接口的 Key）
Base URL:     https://api.openai.com/v1（或 DeepSeek、Ollama 等接口地址）
Model:        gpt-4o（或 deepseek-chat 等）
```

> 国内用户推荐填写 DeepSeek API（https://api.deepseek.com/v1）或通过代理访问 OpenAI。

**步骤 2：选择实验**

- 🏘️ **GOD Town（The Ville）**：10 位居民度过普通一天，适合初次体验
- 🏫 **PKU Trump Visit**：北大校园里的公共事件仿真，适合研究社会动态
- ✏️ **新建实验**：完全自定义你自己的小镇

**步骤 3-6**（如果选「新建实验」）：用自然语言描述世界，GOD 自动生成 Agent profile 和 step 计划，你可以编辑调整，然后发布。

### 第四步：进入控制台

配置完成后，终端会打印类似这样的地址：

```
http://127.0.0.1:5174/pixel-replay/god_town/1
```

打开这个链接，就进入了实时控制台——小镇的居民会开始按自己的日程移动、行动、对话。

---

## Windows 用户步骤

流程完全相同，把脚本命令改为 PowerShell：

```powershell
git clone https://github.com/XiaoLuoLYG/GOD.git
cd GOD
.\scripts\god.cmd start
```

其余步骤（浏览器配置向导、控制台操作）与 macOS/Linux 一致。

---

## 常用命令速查

```bash
./scripts/god.sh start      # 启动完整栈（可重复执行，idempotent）
./scripts/god.sh configure  # 重新打开配置向导（切换实验或改模型）
./scripts/god.sh restart    # 停止后重新启动
./scripts/god.sh new-run    # 清空当前实验的历史数据，重新开始
./scripts/god.sh status     # 查看端口、URL、模型连接状态
./scripts/god.sh stop       # 停止所有服务
./scripts/god.sh tail       # 实时跟随日志
./scripts/god.sh open       # 用浏览器打开前端页面
```

> Windows 用户将 `./scripts/god.sh` 替换为 `.\scripts\god.cmd`

---

## 如何使用控制台的核心功能

### 暂停 / 回放

控制台右上角有 step 控制器：Pause（暂停）、Play（继续）、Step（单步）、Fast Forward（快进）。

暂停后可以拖动时间轴回看任意 step——每个 Agent 在每一步做了什么、说了什么，全部有记录。

### 向居民发问

在命令输入框输入 `/ask`，然后用 `@姓名` 指定对象：

```
/ask @Alice 你今天遇到最有趣的事是什么？
/ask #all 镇里有什么新鲜事吗？
```

Agent 会在下一回合回答你的问题，回复显示在 Live Console 里。

### 实时干预

用 `/intervene` 注入一条指令，Agent 下一回合就会读到：

```
/intervene @Bob 你听说了一件令人不安的事情，决定去找 Alice 确认
/intervene #all 广场上发生了一件奇怪的事，大家都很好奇
```

这是 GOD 最有意思的功能——你可以在不中断小镇运行的情况下，悄悄改变某个角色的下一步行动。

### 一键重开

如果觉得当前剧情走偏了，或者想从头测试：

```bash
./scripts/god.sh new-run
```

清掉 replay 数据，重新孵化一座干净的小镇，所有居民回到初始状态重新开始。

---

## 创建你自己的 AI 小镇

GOD 最有趣的部分是**完全自定义**。在配置向导选「新建实验」，用自然语言描述你的世界，剩下的让 GOD Agent 来生成。

### 世界剧本示例

**小镇版本**：
```
一座位于海边的小渔村，2024 年冬天的某个早晨。
天气：阴天，有轻微海风，气温 8°C。
村里大约 50 户人家，以捕鱼和晒海鲜为主要收入。
最近几天有传言说海里出现了一种奇怪的发光生物。
```

**公司版本**：
```
一家 30 人的科技创业公司，2026 年第一季度末。
背景：公司刚刚完成 B 轮融资，正在快速扩张。
今天是全员大会的前一天，大家都有些紧张。
部分工程师听说要进行重组。
```

**学校版本**：
```
一所县城高中，高考倒计时 50 天。
班级：高三 2 班，30 名学生 + 班主任李老师。
今天刚刚发了一模成绩，各人反应不一。
```

GOD Agent 会根据你的描述自动生成：
- 每个居民的完整 profile（年龄、性格、日常作息、人际关系、担忧、秘密）
- 地图上的活动地点
- Step 计划（模拟时间流逝，居民按日程行动）

### 用 Agent Studio 手动编辑居民

如果 GOD 生成的 profile 不满意，可以在 Agent Studio 里逐个编辑：
- 基本身份（姓名、年龄、职业）
- 性格特征（外向/内向、价值观、口头禅）
- 日常作息（几点起床、去哪里、做什么）
- 社交关系（和谁是朋友、有什么矛盾）
- 秘密和隐忧（只有被直接发问才会透露）

---

## 添加自定义地图

GOD 支持**可插拔地图包**——把一个文件夹放到指定位置，刷新配置向导就能选到新地图。

### 快速添加地图的步骤

1. 复制模板文件夹：
```bash
cp -r agentsociety/custom/maps/_template/ agentsociety/custom/maps/my_town/
```

2. 替换以下文件：
   - `map.yaml`：地图名称、尺寸、地点描述
   - `visuals/map.json`：Tiled JSON 格式地图数据
   - `visuals/tileset.png`：地图瓦片图集
   - `characters/`（可选）：角色 sprite

3. 校验地图包：
```bash
cd agentsociety
uv run python scripts/validate_map_package.py custom/maps/my_town/
```

4. 配置向导里会自动列出你的新地图。

> 地图格式要求：Tiled JSON 格式，必须有一个 `Collisions` 碰撞层（`0` = 可行走）。可以用 [Tiled Map Editor](https://www.mapeditor.org/)（免费开源）创建地图。

也可以用 GOD 内置的 **Map Studio**：上传地图草稿或生成图，在浏览器里校准地点锚点和碰撞层，然后直接发布。

---

## 内置实验详解

### 🏘️ The Ville——普通一天

晚春的工作日清晨 8:20，10 位彼此熟识的居民：

| 居民 | 年龄 | 身份 | 日常 |
|---|---|---|---|
| Alice | 34 | 社区协调员 | 处理各种社区事务，联系人 |
| Bob | 45 | 五金店主 | 早开店，招待各类顾客 |
| Charlie | 39 | 历史老师 | 上课、批改作业 |
| Dana | 41 | 药房护理员 | 接待患者、配药、家访 |
| Elena | 36 | 咖啡馆老板 | 开店、接待、聊天 |
| Farah | 16 | 高中生 | 上学、课后活动 |
| George | 68 | 退休邮递员 | 散步、见老友 |
| Hana | 28 | 远程工程师 | 在家办公 |
| Ivan | 52 | 社区安全志愿者 | 巡逻、维持秩序 |
| Mei | 47 | 蔬果摊主 | 早市、讨价还价 |

每个人都有完整的背景故事、秘密和社交关系网。你可以随时 `/ask` 任何一个人，看他们从自己的视角如何描述这一天。

### 🏫 PKU Trump Visit

北大校园里的公共事件仿真。Agent 先在各自的日常地点（教室、图书馆、未名湖、食堂、宿舍）行动，然后在一次高关注度的访问事件中，自发地产生注意、询问、聚集、讨论等行为——不是脚本驱动的，是 Agent 自己的反应。

![PKU 校园地图](/screenshots/god-map-pku.png)

*PKU 校园地图：校门、教学楼、图书馆、未名湖、博雅塔、食堂、宿舍、百周年纪念讲堂*

---

## 使用场景

### 对研究者
- 测试「谣言传播」实验：给一个居民注入一条虚假信息，观察它如何在小镇扩散
- 研究群体决策：创造一个资源短缺场景，看 Agent 如何协作或竞争
- 社会动态仿真：观察不同人格特征的 Agent 在压力事件下的反应差异

### 对开发者
- 测试 Prompt 工程：比较不同 Prompt 策略下 Agent 行为的差异
- 验证 LLM 能力：用结构化场景测试模型的上下文理解和角色扮演能力
- 构建自定义世界：公司模拟、历史情景再现、教育场景等

### 对创作者
- 互动小说原型：设计场景，然后「访谈」你的角色，看看他们自己会怎么说
- 世界观测试：把你的虚构世界放进去，看居民的自然行为是否符合设定
- 剧情生成：让 Agent 自由发挥，从意外的情节走向中获取灵感

---

## 与类似项目的对比

| 项目 | 类型 | 你能做什么 |
|---|---|---|
| Generative Agents（Park et al. 2023） | 学术原型 | 观察，有限干预 |
| OASIS | 社会模拟研究框架 | 大规模运行，数据分析 |
| AgentSociety | 批量仿真框架 | 编程干预，无可视控制台 |
| **GOD** | **可交互操控台** | **暂停、发问、干预、重置，实时看到反应** |

GOD 的独特之处：**它是操作者的「控制室」**，不是研究者的「实验室」。

---

## 常见问题

**Q: 用什么模型比较好？**  
A: GPT-4o 或 GPT-4 效果最佳，角色一致性和对干预指令的响应更准确。DeepSeek-V3 性价比高，也有不错的表现。如果本地跑 Ollama，llama3.1-70b 以上可以尝试，但角色扮演深度会下降。

**Q: 需要多少 API 费用？**  
A: 运行一个 10 居民小镇，跑 50 个 step，GPT-4o 大约消耗 $1-3（取决于每个 step 的对话量）。DeepSeek API 会便宜得多（大约 1/10）。

**Q: 支持中文剧本吗？**  
A: 完全支持。配置向导和控制台支持中英文切换；你的剧本描述、居民对话都可以用中文。

**Q: 我改变了居民信息，重新开始就生效吗？**  
A: 是的。`./scripts/god.sh new-run` 会用最新的 Agent profile 重新开始，之前的 replay 数据会被清空。

**Q: 居民的行为可以存档分享吗？**  
A: 当前版本（alpha）还不支持导出分享，这在 Roadmap 里。本地的 replay 数据在 SQLite 文件里，技术上可以手动备份。

---

## 当前进度与路线图

**已实现（截至 2026 年 6 月）**：
- ✅ 零代码浏览器配置向导
- ✅ 实时控制台（暂停/发问/干预）
- ✅ 两个内置实验（The Ville + PKU Trump Visit）
- ✅ 可插拔地图包
- ✅ Agent Studio（可视化编辑居民）
- ✅ Map Studio（浏览器内地图制作）
- ✅ 中英文双语界面

**规划中**：
- 🔲 多实验并行对照
- 🔲 实时地图演化（建筑、道路随事件变化）
- 🔲 大规模仿真（接入 AgentSociety 批量 Agent）
- 🔲 公开 Demo 和场景分享社区

---

## 致谢与技术来源

GOD 站在多个开源项目的肩膀上：

- **[AgentSociety](https://github.com/tsinghua-fib-lab/AgentSociety)**（清华 FIB Lab）：大规模 generative-agent 仿真框架
- **[JiuwenClaw](https://github.com/openJiuwen-ai/jiuwenclaw)**：进程外 Agent Runtime
- **[Generative Agents](https://arxiv.org/abs/2304.03442)**（Park et al., 2023）：学术原型与灵感来源
- **[OASIS](https://github.com/camel-ai/oasis)**：社会模拟框架

---

## 快速开始总结

```bash
# 1. 克隆
git clone https://github.com/XiaoLuoLYG/GOD.git && cd GOD

# 2. 启动（自动安装依赖 + 打开浏览器向导）
./scripts/god.sh start          # macOS/Linux
.\scripts\god.cmd start         # Windows PowerShell

# 3. 在浏览器向导里：填 API Key → 选实验 → 启动

# 4. 进入控制台，开始你的上帝视角

# 常用操作
./scripts/god.sh new-run        # 清空历史，重新开始
./scripts/god.sh configure      # 切换实验或模型
./scripts/god.sh stop           # 停止所有服务
```

三步，一个可交互的 AI 小镇就跑起来了。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: GOD (Govern·Observe·Direct) is an open-source real-time operator console for AI agent societies. 3 commands to get a running interactive town. Pause time, whisper to any resident, inject instructions, reset the world — all from a browser UI. Built on Python/FastAPI + React/Vite.

---

## Setup in 3 Commands

```bash
git clone https://github.com/XiaoLuoLYG/GOD.git
cd GOD
./scripts/god.sh start        # macOS/Linux
.\scripts\god.cmd start       # Windows PowerShell
```

First run auto-installs dependencies and opens a browser setup wizard. Fill in your API key (OpenAI-compatible), choose an experiment, and you're in the control room.

## What You Can Do

- **⏯️ Pause/replay**: scrub any live step, jump backward, fast-forward
- **💬 Ask any resident**: `/ask @Alice what happened today?` — mid-run, real-time
- **🎛️ Intervene**: `/intervene @Bob you hear unsettling news about the market` — agents read it on their next turn
- **🔄 Reset**: `./scripts/god.sh new-run` — wipe replay, reseed a clean town

## Two Built-in Experiments

- **The Ville**: 10 residents (teacher, café owner, pharmacist, student, retired postman…) on an ordinary Tuesday — 10 locations, 65 location-scoped interactions
- **PKU Trump Visit**: Public event on a stylized PKU campus — agents spontaneously react, cluster, discuss

## Custom Towns

In the browser wizard, click "Create New" and describe your world in plain language. GOD's setup agent drafts agent profiles and a step plan. Edit in Agent Studio, then launch.

## Tech Stack

Python 3.11+ · FastAPI · React 18 · Vite 6 · SQLite · local WebSocket  
Fully local — only the LLM endpoint is external.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
