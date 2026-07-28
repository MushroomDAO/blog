---
title: "一句话调研任意中国城市周末玩法：weekend-city-trip Claude Code Skill 拆解"
description: "weekend-city-trip 是一个 Claude Code/Codex Skill，说一句话触发 anysearch API 11-15 次并行搜索，7-15 分钟产出覆盖演唱会、市集、CityWalk、美食街、5A 景区、地铁路线的标准化 10 节 Markdown/HTML 报告，附带高德交互地图生成。背后是年轻人从「长途远行」转向「城市微沉浸」的消费范式迁移。"
pubDate: "2026-07-28"
category: "Tech-Experiment"
heroImage: "../../assets/images/weekend-city-trip-claude-code-skill-chinese-city-research-micro-immersion-banner.jpg"
---

周末去哪里玩，这个问题越来越难回答——不是因为选项太少，而是因为值得去的地方太分散：小红书上的市集、本地宝的优惠票、大麦上的演唱会、官方文旅公众号的临时活动……每个来源各自为政，手动聚合要花一两个小时。

liangdabiao 做了一个 Claude Code/Codex Skill：`weekend-city-trip`。

说一句话，AI 帮你把所有来源聚合成一份城市周末行动方案。

---

## 一、为什么要做这个 Skill

README 里有一段很直接的表达：

> 核心就是：1 要快，skill 帮你安排好路线，城市最有看点的地方；2 要准，你直接去那些新兴活动、市集、生产力丰富、年轻人聚集点；3 要新，都是最新的城市活动，你去旅游景区全部外地人，没有可能接触到什么真正的城市。

这背后有一个判断：城市调研不是为了走景点，而是**为了看到这座城市现在真正在发生什么**。

演唱会在哪里开？哪个购物中心开了新的喜茶主题店？本周末有什么创意市集？哪条街最近突然成了年轻人聚集地？

这些信息是流动的、即时的、分散的。它们在各个平台的生命周期只有几天。

传统的旅游攻略解决不了这类需求——那些文章解决的是"去哪个景区"，不是"这个城市现在在发生什么"。

---

## 二、使用方式：一句话触发

安装 Skill 后，对 Claude Code/Codex 说：

```
利用 city skill 调研下周末广州有什么好玩的
```

或者：

```
调研下个月深圳有什么活动，并生成地图
```

或者：

```
成都未来一个月旅游调研，情侣向
```

Skill 自动处理时间解析、城市识别、搜索、质量检查、输出格式——用户不需要做任何配置就能得到结果。

**输出物**：

- 20-30 KB 的 Markdown 报告（7-15 分钟生成）
- 可选：HTML 单文件（浏览器打开，可打印为 PDF）
- 可选：高德交互地图（30-70 个地点标注，11 类彩色标记，分类筛选 + 双向联动，无需 http 服务器，双击即开）

---

## 三、11 个调研方向，10 节标准报告

Skill 对每个城市覆盖 11 个方向：

| # | 方向 | 典型内容 |
|---|---|---|
| 1 | 小红书近期活动 | 近期打卡热点、网红地点 |
| 2 | 演唱会 / 演出 | 日期、场馆、票价 |
| 3 | 集市 / 市集 | 创意市集、古着市集、手作摆摊 |
| 4 | 球赛 | 中超 / CBA 主场安排 |
| 5 | 博物馆 / 美术馆 | 必去场馆 + 当前在展内容 |
| 6 | 优惠门票 | 暑期学生特惠、考生免费、半价票 |
| 7 | 喜茶门店 + 购物中心 | LAB / DP / PINK 主题店，城市十大商圈 |
| 8 | 美食街 | 本地人真正会去的，非游客向 |
| 9 | CityWalk 路线 | 经典步行路线 + 拍照节点 |
| 10 | 5A 景区 | 清单 + 票价 + 交通方式 |
| 11 | 地铁路线 | 线网 + 关键站出口 + 直达商场 |

最终整合为 10 节标准报告：

```
〇、一图速览（表格）
一、活动全清单
二、优惠门票
三、喜茶门店热点
四、美食街
五、CityWalk 路线
六、地铁路线
七、周末组合路线（A/B/C 三条主题路线）
八、时效可靠性说明
九、API 调用统计
十、引用源
```

---

## 四、10 步执行流程

Skill 内部是一个透明的 10 步工作流：

**Step 1-4：准备阶段**
时间解析（"下周末"对应具体日期）→ 用户确认 → 建工作目录 → 为 11 个方向各写 query

关键设计：query 关键词强制带时效标记（`2026年7月` / `本周末` / `暑期`），但同时理解"发布时间 ≠ 举办时间"——一篇 6/26 发布的文章可能在介绍 7/4 的活动。

**Step 5：3 路并行批次执行**
anysearch `batch_search` 上限 5 个 query 并行，11 次调用拆成 **5+4+2** 三批，总耗时 30-60 秒。

```bash
# anysearch JSON-RPC 2.0，batch_search 并行
python anysearch_cli.py batch_search --queries '[
  {"query":"广州 周末活动 展览 演出 市集 演唱会 2026年7月","max_results":10},
  {"query":"小红书 广州 打卡 网红 同城活动 暑期","max_results":10},
  ...
]'
```

**Step 6-7：解析 + 整合**
anysearch 返回纯文字 snippet（无 thumbnailUrl、无 AI 摘要），Skill 用 emoji + 表格 + 粗体强调替代图片，保持信息密度。

**Step 8：质量检查闭环（核心差异化）**

这是 Skill 最重要的设计。报告生成完不等于任务结束——必须经过质量检查才能交付。

5 个检查维度：

- **完整性**：11 个方向是否全部覆盖
- **准确性**：时间 / 地点 / 票价是否真实（无编造）
- **丰富度**：每节信息密度是否达最低标准
- **可执行性**：三条周末路线时间是否有冲突
- **信源多样性**：关键信息是否 ≥ 2 个来源验证

最低信息密度要求（部分）：

| 章节 | 最低 |
|---|---|
| 演唱会 / 演出 | 3 场，含时间 / 场馆 / 票价 |
| 博物馆 | 3 个，含当前展览 |
| 5A 景区 | 2 个，含票价 / 交通 |
| 优惠门票 | 3 个景区，含原价 / 现价 / 规则 |

不达标自动补查询，最多迭代 2 轮。总 API 调用上限 15 次（初始 11 + 补救 4）。

**Step 9：HTML 输出（可选）**
Markdown → HTML 单文件，三档优先级（python-markdown → markdown2 → 内置兜底），不装库也能用。

**Step 10：高德交互地图（可选）**
AI 从报告中提取地点 → 高德 Web 服务批量地理编码（60-90% 成功率）→ 注入地图模板 → 验证输出。

地图特性：11 类水滴形标记 + 分类筛选 + 关键词搜索 + 双向联动（点卡片飞至地图 / 点 marker 高亮卡片）。坐标预编码，**无需 http 服务器，双击 HTML 即开**。

---

## 五、技术设计判断

**为什么用 anysearch 而不是 Google/Bing？**

中文城市活动信息高度集中在本地媒体（腾讯新闻、网易、本地宝、官方文旅公众号），anysearch 对中文索引的覆盖比国际搜索引擎更好。JSON-RPC 2.0 接口也支持 batch_search 并行，减少总耗时。

**反幻觉设计**

Skill 的核心承诺是：不编造任何未出现在 snippet 里的信息。单源可疑数据要么标注要么删除，报告末尾要求"出行前二次确认"（票价 / 演出嘉宾可能变动）。信源清单完全公开，按任务分类列引用。

**失败优雅降级**

- 没有 anysearch API Key → anonymous 模式（低 QPS 仍可用）
- markdown 库没安装 → 三档兜底转换器
- 高德 Key 缺失 → 打印帮助信息，退出码 2，不崩溃

---

## 六、安装

```bash
# 一句话告诉 Claude Code 帮你安装：
# "帮忙安装skill: github.com/liangdabiao/weekend-city-trip"

# 或手动 clone 到全局 skills 目录
git clone https://github.com/liangdabiao/weekend-city-trip \
  ~/.claude/skills/weekend-city-trip
```

API Key 配置（`.env` 文件，skill 目录下）：

```bash
ANYSEARCH_API_KEY=as_sk-xxx    # 调研报告必需（anonymous 也可用）
AMAP_KEY=xxx                   # 地图生成用，Web 服务 Key
AMAP_JS_KEY=xxx                # 地图生成用，JS API Key
AMAP_SECURITY=xxx              # 地图生成用，安全密钥
```

---

## 七、背后的消费趋势

这个 Skill 的选题有一个背景：**年轻人正在从"景区式旅行"向"城市微沉浸"迁移**。

告别长途远行，告别装备内卷——不是每次出门都要飞去一个陌生城市，不是每次郊游都要备齐装备。最有价值的探索，往往发生在自己所在城市的一个角落：

一个突然出现的周末市集、一个博物馆的临时展览、一个老街区里新开的咖啡馆、一场球赛或演唱会。

这些活动的共同特征是：**本地居民聚集、时效性强、信息分散、不在传统旅游攻略的覆盖范围内**。

`weekend-city-trip` 的 Skill 设计，恰好匹配了这个需求结构：11 个方向几乎都是动态活动而不是静态景点，每次调研强制带时效标记，信源优先级也倾向于本地媒体而不是国家级旅游平台。

---

**项目信息**

- GitHub：`github.com/liangdabiao/weekend-city-trip`（62 ⭐，MIT）
- 语言：HTML / Python
- 依赖：Claude Code 或 Codex CLI + anysearch API（地图可选高德 API）
- 适用城市：中国大陆任意城市（海外城市召回偏低）
- 适用时间范围：周末 / 一个月内短期旅游

<!--EN-->

## Weekend City Trip: A Claude Code Skill That Researches Any Chinese City in 5 Minutes

Finding something worthwhile to do on the weekend is harder than it sounds — not because there's too little to choose from, but because the best options are scattered: a pop-up market on Xiaohongshu, a discount ticket on Bendibao, a concert on Damai, a last-minute event from the local tourism bureau. Aggregating all that manually takes one to two hours.

liangdabiao built a Claude Code/Codex Skill for exactly this: `weekend-city-trip`.

One sentence. AI researches, structures, and delivers a weekend action plan for any Chinese city.

---

## Why This Skill Exists

The README is direct:

> The core is: 1. Fast — the skill arranges the routes, the best parts of the city; 2. Precise — you go straight to the emerging events, markets, places where productive and young people gather; 3. Fresh — these are the latest city events. If you go to tourist sites, it's all out-of-towners; you can't encounter the real city. I arrange the spots where locals actually gather.

The underlying premise: city research isn't for hitting scenic spots — it's for seeing what's actually happening in a city right now.

Where is the next concert? Which mall just opened a new Heytea concept store? What weekend market is running this week? Which street has become the new local gathering spot?

This information is fluid, immediate, and dispersed. Its shelf life on any single platform is a few days. Traditional travel guides don't solve this — they tell you which scenic area to visit, not what's happening in the city this weekend.

---

## Usage: One Sentence

After installing the Skill, tell Claude Code or Codex:

```
Use city skill to research what's fun to do in Guangzhou this weekend
```

Or:

```
Research activities in Shenzhen next month and generate a map
```

Or:

```
Chengdu one-month travel research, couples focus
```

The Skill handles time parsing, city identification, searching, quality checks, and output format — no manual configuration needed.

**Output:**

- 20-30 KB Markdown report (7-15 minutes to generate)
- Optional: HTML single-file (browser-ready, printable as PDF)
- Optional: Amap interactive map (30-70 locations pinned, 11 marker categories, filtering + bidirectional linking, double-click to open — no http server needed)

---

## 11 Research Directions, 10-Section Report

The Skill covers 11 directions for every city:

| # | Direction | Typical content |
|---|---|---|
| 1 | Xiaohongshu recent activities | Current check-in spots, trending locations |
| 2 | Concerts / performances | Date, venue, ticket price |
| 3 | Markets / bazaars | Creative markets, vintage, handmade stalls |
| 4 | Sports | CSL / CBA home game schedules |
| 5 | Museums / galleries | Must-visit venues + current exhibitions |
| 6 | Discount tickets | Student discounts, gaokao promotions, half-price deals |
| 7 | Heytea + malls | LAB / DP / PINK concept stores, top 10 shopping centers |
| 8 | Food streets | Where locals actually eat, not tourist-facing |
| 9 | CityWalk routes | Classic walking routes + photo spots |
| 10 | 5A scenic areas | List + ticket prices + transit |
| 11 | Metro routes | Network overview + key station exits + direct mall access |

Synthesized into a 10-section standard report:

```
§0. Quick overview (table)
§1. Full activity list (concerts/markets/sports/museums/5A)
§2. Discount tickets
§3. Heytea hot spots
§4. Food streets
§5. CityWalk routes
§6. Metro routes
§7. Weekend combo routes (A/B/C themed itineraries)
§8. Reliability notes
§9. API call stats
§10. References
```

---

## The 10-Step Workflow

The Skill runs a transparent 10-step process:

**Steps 1-4: Preparation**
Parse time ("next weekend" → specific dates) → user confirmation → create work directory → write a query for each of the 11 directions.

Key design: query keywords are forced to include recency markers (`July 2026` / `this weekend` / `summer`), while also understanding that "publication date ≠ event date" — an article published June 26 may be covering a July 4 event.

**Step 5: 3-batch parallel execution**
anysearch `batch_search` supports up to 5 parallel queries. 11 calls split into **5+4+2** batches, total 30-60 seconds.

**Steps 6-7: Parse + synthesize**
anysearch returns plain-text snippets (no thumbnailUrl, no AI-generated summaries). The Skill uses emoji + tables + bold emphasis instead of images to maintain information density.

**Step 8: Quality check loop (core differentiator)**
Report generation ≠ task complete. Before delivery, five dimensions are checked: completeness, accuracy, richness, executability, source diversity. If any section falls below minimum density requirements, the Skill issues supplementary queries — up to 2 rounds, max 15 total API calls.

**Step 9: HTML output (optional)**
Markdown → HTML single file. Three-tier fallback (python-markdown → markdown2 → built-in converter). Works even without installing any external library.

**Step 10: Amap interactive map (optional)**
AI extracts locations from the report → Amap Web Service batch geocoding (60-90% success rate) → inject into map template → validate output. Pre-encoded coordinates; open by double-clicking the HTML file — no server needed.

---

## The Cultural Shift Behind This Tool

`weekend-city-trip` addresses a genuine shift in how younger Chinese urbanites think about leisure.

Away from long-distance travel and gear-intensive outdoor trips — toward low-cost daily micro-immersion. A weekend market. A temporary museum exhibition. An old street neighborhood with a recently-opened café. A concert or a local sports match.

The common characteristics of these activities: locals-focused, time-sensitive, information-scattered, not covered by conventional travel guides.

The Skill's design matches this demand structure: 11 research directions that favor dynamic events over static attractions, forced recency markers on every search, and source prioritization toward local media rather than national tourism platforms.

This isn't just convenience tooling — it's tooling built around a specific model of urban exploration: the city as a living system, not a set of fixed destinations.

---

**Project**

- GitHub: `github.com/liangdabiao/weekend-city-trip` (62 ⭐, MIT)
- Language: HTML / Python
- Dependencies: Claude Code or Codex CLI + anysearch API (Amap optional for maps)
- Supported cities: Mainland Chinese cities (lower coverage for overseas)
- Time range: weekends / short trips within one month
