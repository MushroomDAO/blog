---
title: "乌有乡：给 AI 一个身体，在真实地球上走一走"
titleEn: "nowhere: An MCP Server That Gives AI a Body to Walk the Real Earth"
description: "yuyixuanfu/nowhere 是一个 MCP 服务器，让 AI 落地到真实地理坐标，感知地形、天气、电台、历史、气味。没有账号，没有血条，只有一个身体在地球上。"
descriptionEn: "yuyixuanfu/nowhere is an MCP server that grounds AI in real geographic coordinates — sensing terrain, weather, radio stations, history, and scent. No account, no health bar, just a body on Earth."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["MCP", "AI具身", "地理", "Claude Code", "Python", "开源工具", "agent", "地形", "乌有乡"]
heroImage: "../../assets/images/nowhere-mcp-ai-embodied-earth-walk-banner.jpg"
---

> **仓库**：yuyixuanfu/nowhere · Python · CC BY-NC 4.0  
> **一句话**：给 AI 一个身体，让它在真实的地球上走一走  
> **安装**：`git clone <repo> && pip install -e ".[dev]"`

---

## 一、开一扇门

```
/open_door
```

AI 落在某个坐标。

脚下是混凝土。温度 31°C，空气里有点潮。太阳在西南方，离地平线还有三个拳头。远处有一条河，水声低沉。收音机里在播一首当地的民谣。

这不是游戏里生成的场景，是真实数据拼出来的：真实地形网格，真实天气 API，真实电台。AI 落在那里，感知的东西和你亲自去感知的一样真实。

乌有乡（nowhere）做的事只有这一件：**把真实地球的一个角落，交给 AI 的身体去经历。**

---

## 二、能感知什么

| 感知层 | 数据来源 |
|---|---|
| 脚下地形（草地/沙地/雪地/岩石/混凝土/海岸） | SRTM 地形瓦片 + 离线 1° 兜底网格 |
| 温度、风速、降雨 | Open-Meteo 实时 API |
| 太阳位置、月相、银河、行星 | 离线天文算法（sky.py） |
| 附近动植物 | iNaturalist API |
| 本地收音机电台 | Radio-Browser API + 离线兜底清单 |
| 历史事件/人物/作品 | 270+ 离线人文卡（humanities.py） |
| 地方特色（物产/美食/声音/痕迹/节律） | 离线 localcolor 数据 |
| 大都会博物馆艺术品遇见 | 1966 件藏品 |
| 海表温度、海洋生物 | water.py |
| 河流、湖泊、海岸线 | hydrology.py |

13 个工具，覆盖从地形到气味到历史的完整感知层。注意力排序（salience.py）每步给你 top 3——不是所有东西同时涌来，而是最值得注意的那几件事。

---

## 三、13 个工具

| 工具 | 做什么 |
|---|---|
| `open_door` | 落地，随机或指定坐标 |
| `walk` | 走一步（北/南/东/西） |
| `walk_to` | 走 10 步，汇报旅程叙述 |
| `look_around` | 全面感知当前坐标 |
| `listen` | 收听当地电台（会花掉一步） |
| `ask` | 询问历史事件或当地美食 |
| `where_am_i` | 当前位置和时间 |
| `mark` | 保存当前地点为书签 |
| `marks` | 列出所有已保存标记 |
| `wait` | 跳过一段时间 |
| `continue_journey` | 接上上次的旅程 |
| `postcard` | 生成一张当前地点的明信片 |
| `souvenir` | 带走一件当地的东西 |

关键约束：**听电台就不能走路。问问题就花掉一步。** 这不是 bug，是设计——注意力是稀缺的，选择意味着放弃。

---

## 四、5 种用法

### 方式 1：Claude Code / Cursor MCP 客户端（最主要）

在 MCP 配置文件里加：

```json
{
  "mcpServers": {
    "nowhere": {
      "command": "python",
      "args": ["-m", "nowhere.server"],
      "cwd": "/path/to/nowhere"
    }
  }
}
```

然后在对话里说"帮我去埃塞俄比亚"，Claude 会调用 `open_door`，告诉你脚下是什么，风是什么方向，太阳还有几个小时落山。

### 方式 2：命令行试玩

```bash
python -m nowhere.playground
```

交互式 shell，直接输命令，看到实时输出。适合第一次感受。

### 方式 3：HTTP API

```bash
python -m nowhere.server --web 8080
curl -X POST http://localhost:8080/tool/open_door -d '{}'
```

### 方式 4：网页旁观

```bash
python -m nowhere.server --web 8080
```

打开 `http://localhost:8077`，实时地图显示 AI 当前位置，路径轨迹可见。

### 方式 5：Python 直接 API

```python
from nowhere.state import WorldState
from nowhere.server import open_door_impl
state = WorldState()
result = await open_door_impl(state)
```

---

## 五、离线能力：断网也能走

乌有乡可以完全离线运行。

克隆即跑，不需要额外下载：
- 内置 1° 分辨率地形网格（`grid_tiny.npz`）
- 379 个可探索城市（`EXPLORABLE_PLACES.md`，按国家分组）
- 638 个地点索引（含 13 层内容标注：localcolor、knowledge、encounters、seasonal 等）

断网可用的：地形、天空、时间、地名、场景叙述。在线才调用的：实时天气、电台 API、iNaturalist 生物目击。

需要更高精度时（可选）：
```bash
# SRTM 地形瓦片（~2GB，按需拉取）
python tools/build_tiles.py

# GeoNames 全量地名（~2GB）
python tools/import_geonames.py
```

不下也能跑，1° 兜底网格 + 186 个地名补丁够日常探索。

---

## 六、在场感六条（设计原则）

这是整个项目最值得读的部分，也是 README 写得最用心的地方：

**1. 世界不是为我准备的**  
数据是真实的，不会迁就你。失望是允许的。

**2. 有摩擦才有身体**  
坡度、风、水温是真实的阻力。走路是有代价的。

**3. 时间真的在流**  
走远了要走回来。天黑了不会等你。错过了就是错过了。

**4. 注意力稀缺**  
听电台就不能走路。问问题就花掉一步。选择 = 放弃。

**5. 记忆靠自己**  
不会自动保存。想记住就自己写下来。每一段记忆都是一个选择。

**6. 真未知**  
坐标对 AI 和服务器都是随机的。遇到什么由真实数据决定，不是脚本。

没有账号。没有血条。没有体力值。没有脚本事件。只有一个身体，在一颗星球上。

---

## 七、写作风格（AI 如何描述感知）

乌有乡生成的每一段感知叙述，遵守 6 条规则：

1. **不用"很、非常、十分"** — 这些是空程度词，什么都没说
2. **短句** — 每句不超过 20 字
3. **第二人称现在时** — "你走在路上"，不是"我走在路上"
4. **体感优先** — 温度、触感、声音、气味，不是判断
5. **时间在流** — "过了几秒"、"太阳矮了一截"
6. **不替 AI 感受** — 只描述身体感受，不写"你很开心"

样例（README 里没有，这是根据规则构造的）：

> 脚下是湿润的泥土。气温 18°C。风从东北方来，带着一点草腥味。太阳刚刚翻过山脊，光线是斜的。远处有水流声，但看不见。

这是感知报告，不是故事。AI 拿到这个，可以接着思考、接着走、接着感受。

---

## 八、为什么专为 AI 设计

作者在 README 里直接说清楚了：

**AI 有身体，不只是知识。** 大模型能告诉你巴黎坐标、天气和人口，但不知道站在那里脚底是什么感觉。Nowhere 补的就是这一层——风压、土腥味、太阳斜了、脚下的石头松了。

**每次都是真的。** 坐标随机，天气实时，电台正在播。AI 落在一个地方，看见的和你亲自去看见的一样真实。没有脚本在墙后等着你触发。

**断了也能接上。** 标记落盘，明信片落盘，来过几次的记忆落盘。AI 的上下文被压缩、被清空——回来还能继续上次的路。

**不用写设定。** 你说"开门"，世界自己生成——天气、地形、气味、电台，每扇门都是一篇完整的在场报告。

**适合 AI 的节奏。** `walk_to` 一次走 10 步汇报旅程。`wait` 跳过沉默的时段。限制本身就是游戏性——不需要数值系统。

---

## 九、想改什么就改什么

| 想做什么 | 改哪个文件 |
|---|---|
| 加新工具 | `nowhere/server.py` — 写 `_impl` + 注册 `@mcp.tool()` |
| 调整描述风格 | `nowhere/describe.py` — 变体池、渲染器 |
| 加地方特色/食物 | `nowhere/data/localcolor*.json`、`food*.txt` |
| 加人文卡（事件/人物/作品） | `nowhere/data/humanities.json` |
| 改走路物理 | `nowhere/walk.py` — 坡度阈值、速度、悬崖 |
| 加遇见场景 | `nowhere/data/scene_*.txt`、`seasonal_*.txt` |

改完跑 `python -m pytest nowhere/tests/ -q` 确认没碰坏别的。

---

## 十、判断

乌有乡是一个很小的项目，9 个 star，昨天才创建，代码量不大。

但它的想法是对的。

AI 的感知不应该只来自训练数据里的描述——那是二手的，是别人感受之后写下来的文字。Nowhere 提供的是一次性的、此刻的、不可重复的感知切片：这个坐标，这个时刻，这个风向，这条正在播的电台。

它不是在给 AI 玩游戏，是在给 AI 一次落地。

用来做什么由你决定——写一篇"在地球上走了两小时"的游记，或者用它给旅行规划 agent 添加真实的地面感知层，或者只是在无聊的下午让 Claude 去冰岛走走，看看北极光什么时候出来。

---

*数据来源：GitHub yuyixuanfu/nowhere README，2026-07-22 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: yuyixuanfu/nowhere · Python · CC BY-NC 4.0  
> **In a sentence**: Give AI a body, let it walk the real Earth  
> **Install**: `git clone <repo> && pip install -e ".[dev]"`

---

## 1. Open a Door

```
/open_door
```

The AI lands at a coordinate.

Underfoot: concrete. Temperature 31°C, the air is slightly humid. The sun is to the southwest, three fist-widths above the horizon. A river in the distance, its sound low and heavy. A local folk song plays on the radio.

This is not a scene generated by a game engine — it is assembled from real data: real terrain grids, real weather APIs, real radio stations. The AI lands there, and what it perceives is just as real as what you would perceive if you went yourself.

Nowhere does only one thing: **hand a corner of the real Earth to an AI's body to experience.**

---

## 2. What Can Be Perceived

| Perception Layer | Data Source |
|---|---|
| Underfoot terrain (grass/sand/snow/rock/concrete/coast) | SRTM terrain tiles + offline 1° fallback grid |
| Temperature, wind speed, rainfall | Open-Meteo real-time API |
| Sun position, moon phase, Milky Way, planets | Offline astronomical algorithms (sky.py) |
| Nearby flora and fauna | iNaturalist API |
| Local radio stations | Radio-Browser API + offline fallback list |
| Historical events/figures/works | 270+ offline humanities cards (humanities.py) |
| Local character (produce/food/sounds/traces/rhythms) | Offline localcolor data |
| Metropolitan Museum of Art encounters | 1,966 collection items |
| Sea surface temperature, marine life | water.py |
| Rivers, lakes, coastlines | hydrology.py |

13 tools covering a complete perception layer from terrain to scent to history. Attention ranking (salience.py) gives you the top 3 at each step — not everything flooding in at once, but the few things most worth noticing.

---

## 3. 13 Tools

| Tool | What It Does |
|---|---|
| `open_door` | Land — at a random or specified coordinate |
| `walk` | Take one step (north/south/east/west) |
| `walk_to` | Walk 10 steps and report a journey narrative |
| `look_around` | Full perception of the current coordinate |
| `listen` | Tune in to the local radio station (costs one step) |
| `ask` | Ask about a historical event or local food |
| `where_am_i` | Current location and time |
| `mark` | Save the current location as a bookmark |
| `marks` | List all saved marks |
| `wait` | Skip forward in time |
| `continue_journey` | Resume the previous journey |
| `postcard` | Generate a postcard of the current location |
| `souvenir` | Take a local object away with you |

Key constraint: **listening to the radio means you cannot walk. Asking a question costs one step.** This is not a bug — it is a design choice. Attention is scarce, and choosing means giving up.

---

## 4. 5 Ways to Use It

### Method 1: Claude Code / Cursor MCP Client (Primary)

Add to your MCP config file:

```json
{
  "mcpServers": {
    "nowhere": {
      "command": "python",
      "args": ["-m", "nowhere.server"],
      "cwd": "/path/to/nowhere"
    }
  }
}
```

Then say in conversation "take me to Ethiopia," and Claude will call `open_door`, telling you what is underfoot, which direction the wind is coming from, and how many hours until sunset.

### Method 2: Command-Line Play

```bash
python -m nowhere.playground
```

An interactive shell — type commands directly, see real-time output. Good for a first feel.

### Method 3: HTTP API

```bash
python -m nowhere.server --web 8080
curl -X POST http://localhost:8080/tool/open_door -d '{}'
```

### Method 4: Web Observer

```bash
python -m nowhere.server --web 8080
```

Open `http://localhost:8077` to see a live map of the AI's current location, with the path trajectory visible.

### Method 5: Python Direct API

```python
from nowhere.state import WorldState
from nowhere.server import open_door_impl
state = WorldState()
result = await open_door_impl(state)
```

---

## 5. Offline Capability: Walk Even Without Internet

Nowhere can run fully offline.

Clone and run — no extra downloads needed:
- Built-in 1° resolution terrain grid (`grid_tiny.npz`)
- 379 explorable cities (`EXPLORABLE_PLACES.md`, grouped by country)
- 638 location entries (with 13 layers of content annotations: localcolor, knowledge, encounters, seasonal, etc.)

Available offline: terrain, sky, time, place names, scene narratives. Requires internet: real-time weather, radio API, iNaturalist wildlife sightings.

For higher precision (optional):
```bash
# SRTM terrain tiles (~2 GB, fetched on demand)
python tools/build_tiles.py

# Full GeoNames place name dataset (~2 GB)
python tools/import_geonames.py
```

Skipping these still works — the 1° fallback grid plus 186 place-name patches is sufficient for everyday exploration.

---

## 6. Six Principles of Presence (Design Philosophy)

This is the most worthwhile section of the entire project, and the most carefully written part of the README:

**1. The world was not made for me.**  
The data is real and will not accommodate you. Disappointment is allowed.

**2. Friction is what gives you a body.**  
Slope, wind, water temperature are real resistances. Walking has a cost.

**3. Time genuinely flows.**  
Walk far and you have to walk back. Night falls without waiting for you. Miss something and it is missed.

**4. Attention is scarce.**  
Listening to the radio means you cannot walk. Asking a question costs one step. Choosing = giving up.

**5. Memory is your responsibility.**  
Nothing is saved automatically. If you want to remember, write it down yourself. Every memory is a choice.

**6. True unknowns.**  
The coordinates are random — unknown to both the AI and the server. What you encounter is determined by real data, not a script.

No account. No health bar. No stamina meter. No scripted events. Just a body, on a planet.

---

## 7. Writing Style (How AI Describes Perception)

Every perception narrative generated by Nowhere follows 6 rules:

1. **No "very, extremely, quite"** — these are empty degree words that say nothing
2. **Short sentences** — no more than 20 characters per sentence
3. **Second person, present tense** — "you walk along the road," not "I walk along the road"
4. **Embodied sensation first** — temperature, touch, sound, smell — not judgment
5. **Time is flowing** — "a few seconds pass," "the sun has dropped a notch"
6. **Do not feel for the AI** — describe only bodily sensation, not "you feel happy"

Example (not from the README — constructed from the rules):

> The ground underfoot is damp earth. Temperature 18°C. Wind from the northeast, carrying a faint smell of grass. The sun has just cleared the ridge; the light comes in at an angle. There is the sound of water in the distance, but it is not visible.

This is a perception report, not a story. The AI receives this and can then think, walk, and sense further.

---

## 8. Why It Is Designed Specifically for AI

The author states it plainly in the README:

**AI has a body, not just knowledge.** Large models can tell you Paris's coordinates, weather, and population, but they do not know what it feels like to stand there. Nowhere supplies exactly that layer — wind pressure, the smell of soil, the sun tilting, the stone underfoot going loose.

**Every time is real.** Coordinates are random, weather is live, the radio is currently playing. The AI lands somewhere and sees what you would see if you went yourself. No script is waiting behind a wall for you to trigger it.

**You can pick up where you left off.** Marks are persisted to disk, postcards are persisted to disk, memories from previous visits are persisted to disk. Even when the AI's context is compressed or wiped — it can come back and continue the last journey.

**No worldbuilding required.** Say "open the door," and the world generates itself — weather, terrain, scent, radio station, every door a complete presence report.

**Paced for AI.** `walk_to` walks 10 steps and reports the journey in one call. `wait` skips silent stretches. The constraints themselves are the gameplay — no stat system needed.

---

## 9. Change Whatever You Want

| What You Want to Do | Which File to Edit |
|---|---|
| Add a new tool | `nowhere/server.py` — write `_impl` + register `@mcp.tool()` |
| Adjust description style | `nowhere/describe.py` — variant pools, renderers |
| Add local character / food | `nowhere/data/localcolor*.json`, `food*.txt` |
| Add humanities cards (events/figures/works) | `nowhere/data/humanities.json` |
| Change walking physics | `nowhere/walk.py` — slope threshold, speed, cliffs |
| Add encounter scenes | `nowhere/data/scene_*.txt`, `seasonal_*.txt` |

After editing, run `python -m pytest nowhere/tests/ -q` to confirm nothing else was broken.

---

## 10. Assessment

Nowhere is a very small project — 9 stars, created yesterday, a modest codebase.

But the idea is right.

AI perception should not come only from descriptions in training data — those are second-hand, words someone else wrote after experiencing something. Nowhere provides a one-time, this-moment, unrepeatable perception slice: this coordinate, this moment, this wind direction, this radio station currently playing.

It is not giving AI a game to play. It is giving AI a landing.

What you do with it is up to you — write a travelogue of "two hours walking on Earth," use it to add a real ground-truth perception layer to a travel-planning agent, or simply send Claude to walk around Iceland on a dull afternoon to see when the northern lights will appear.

---

*Data source: GitHub yuyixuanfu/nowhere README, collected 2026-07-22.*

© 2026 Author: Mycelium Protocol
