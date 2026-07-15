---
title: "健身 App 的数据底座：exercises-dataset 1324 个动作数据集拆解与集成指南"
titleEn: "The Data Foundation for Fitness Apps: exercises-dataset — 1,324 Exercises, GIFs, and 9-Language Instructions"
description: "exercises-dataset 是一个包含 1,324 个健身动作的开源数据集（14k+ ⭐），每个动作配有动画 GIF、180×180 缩略图、肌肉分组数据、9 种语言的分步说明。本文拆解数据结构，并给出从导入数据库到搭建 REST API 的完整集成路径，适合快速落地健身 App 的运动库功能。"
descriptionEn: "exercises-dataset is an open-source fitness data collection with 1,324 exercises (14k+ stars), each with an animation GIF, 180×180 thumbnail, muscle group data, and step-by-step instructions in 9 languages. This article breaks down the schema and walks through database import, REST API setup, and the exercise-filter logic needed for a fitness app's movement library."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Research"
tags: ["数据集", "健身App", "开源", "后端开发", "运动数据"]
heroImage: "../../assets/images/exercises-dataset-fitness-app-data-layer-banner.jpg"
---

> GitHub：[hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset) · ⭐ 14,036 · 🍴 1,679 · MIT（代码/数据）+ Gym visual 媒体条款  
> 数据规模：1,324 个动作 · 1,324 张 GIF · 1,324 张缩略图 · 9 种语言说明  
> 驱动应用：[LogPress](https://github.com/hasaneyldrm/logpress-public)（AI 辅助训练记录 App）

---

## 这是什么

做健身 App，最费时间的不是界面，而是**运动库的内容**：每个动作叫什么名字、用什么器械、练哪块肌肉、具体怎么做——这些内容需要专业知识，手写一个靠谱的数据集要几个月。

exercises-dataset 把这件事做好了，直接拿来用：

- **1,324 个动作**，按身体部位和器械分类
- **每个动作一张动画 GIF**，180×180，来自 Gym visual，可视化展示完整动作轨迹
- **9 种语言**的分步操作说明（英、西、意、土、俄、中、印地、波、韩）
- **结构化元数据**：目标肌肉、协同肌肉、器械类型，可直接用于筛选和推荐逻辑

---

## 数据覆盖范围

### 按身体部位

| 部位 | 动作数 |
|------|--------|
| 上臂 | 292 |
| 大腿 | 227 |
| 背部 | 203 |
| 腰腹 | 169 |
| 胸部 | 163 |
| 肩部 | 143 |
| 小腿 | 59 |
| 前臂 | 37 |
| 有氧 | 29 |
| 颈部 | 2 |

### 按器械

| 器械 | 动作数 |
|------|--------|
| 自重（无器械） | 325 |
| 哑铃 | 294 |
| 绳索 | 157 |
| 杠铃 | 154 |
| 器械架 | 81 |
| 弹力带 | 54 |
| 史密斯架 | 48 |
| 壶铃 | 41 |
| 其他 | 167 |

**25% 的动作不需要任何器械**——纯自重动作数据充足，无器材健身 App 完全可以单独用这个子集。

---

## 数据结构

每条记录的字段：

```json
{
  "id": "0025",
  "name": "Barbell Bench Press",
  "category": "chest",
  "body_part": "chest",
  "equipment": "barbell",
  "target": "pectoralis major",
  "muscle_group": "triceps",
  "secondary_muscles": ["triceps brachii", "anterior deltoid"],
  "instructions": {
    "en": "Lie on a flat bench...",
    "zh": "躺在平凳上，双手抓住杠铃，宽度略宽于肩..."
  },
  "instruction_steps": {
    "en": ["Step 1: ...", "Step 2: ..."],
    "zh": ["第一步：...", "第二步：..."]
  },
  "image": "images/0025-EIeI8Vf.jpg",
  "gif_url": "videos/0025-EIeI8Vf.gif",
  "media_id": "EIeI8Vf",
  "attribution": "© Gym visual — https://gymvisual.com/",
  "created_at": "2026-03-18T12:31:32.854798+00:00"
}
```

两个细节值得注意：
- `instructions` 是完整文本（适合展示详情页），`instruction_steps` 是按步骤切分的数组（适合做步骤卡片 UI 或语音播报）
- `secondary_muscles` 是数组，可以用来做「练背部顺带会练到的动作」这类推荐逻辑

---

## 仓库自带的两个工具

克隆下来不用任何服务器，直接在浏览器打开就能用：

### `index.html`——运动库浏览器

- 1,324 个动作的可搜索、可筛选卡片网格
- 实时过滤：按部位、器械、目标肌肉
- 无限滚动
- 点击任意卡片展示 GIF + 分步说明，可切换 9 种语言

调研数据集结构、选取动作子集、给产品经理演示，都可以直接用这个页面。

### `setup.html`——开发者集成向导

这个页面比较有用：

1. **数据库建表 SQL**：支持 SQL Server、PostgreSQL、MySQL、SQLite，在浏览器里选数据库类型，直接生成包含 1,324 条 INSERT 的 `.sql` 文件
2. **API 客户端代码**：填入你的后端 base URL，自动生成 JavaScript / Python / C# / Java / PHP / Go / cURL 的调用示例
3. **LLM Prompt**：选框架（Express.js / FastAPI / ASP.NET Core / Spring Boot / Laravel / Gin）和数据库，生成一段结构化 prompt，粘贴给 Claude 或 ChatGPT，直接得到完整的 REST API 代码

---

## 如何用这个数据集做健身 App

### 第一步：把数据导入数据库

以 SQLite 为例（移动端最常见的选择）：

打开 `setup.html`，选择 SQLite，点「Generate SQL File」，下载 `exercises_sqlite.sql`。

```bash
sqlite3 exercises.db < exercises_sqlite.sql
```

建好后验证：

```sql
SELECT COUNT(*) FROM exercises;          -- 应返回 1324
SELECT name, equipment FROM exercises WHERE body_part = 'chest' LIMIT 5;
```

PostgreSQL / MySQL 同理，建表 SQL 也在 `setup.html` 里生成。

### 第二步：搭建 REST API

以 FastAPI 为例（Python）——直接用 `setup.html` 生成的 prompt 贴给 Claude，它会生成完整的 API 代码。核心接口设计：

```
GET /exercises                          # 全列表（分页）
GET /exercises?body_part=chest          # 按部位筛选
GET /exercises?equipment=body+weight    # 按器械筛选
GET /exercises?target=biceps            # 按目标肌肉筛选
GET /exercises/{id}                     # 单条详情
GET /exercises/{id}/gif                 # 返回 GIF（或重定向到静态文件）
```

媒体文件（GIF 和缩略图）放到 CDN 或对象存储，API 返回的 `image` / `gif_url` 字段直接指向 CDN URL。

### 第三步：App 里的几个核心功能模块

**运动库搜索页**

最基础的功能，对应 `index.html` 的逻辑：

```typescript
// 前端过滤逻辑示例（React Native）
const filteredExercises = exercises.filter(ex => {
  const matchPart = selectedPart ? ex.body_part === selectedPart : true;
  const matchEquip = selectedEquipment ? ex.equipment === selectedEquipment : true;
  const matchQuery = query ? ex.name.toLowerCase().includes(query) : true;
  return matchPart && matchEquip && matchQuery;
});
```

**动作详情页**

关键 UI 元素：
- 顶部：GIF 动画（`gif_url`）
- 下方：目标肌肉标签（`target`）+ 协同肌肉（`secondary_muscles`）
- 分步说明：用 `instruction_steps.zh`（或用户选择的语言）渲染步骤卡片
- 可切换语言的按钮（9 种语言数据都在 JSON 里）

**训练计划生成**

数据库里有足够的维度做个简单的计划生成器：

```python
def generate_workout(goal: str, equipment: list[str], duration_min: int):
    # 根据目标选部位组合
    body_parts = GOAL_TO_PARTS[goal]  # e.g. "增肌上肢" → ["chest", "back", "upper arms", "shoulders"]
    
    # 筛选有可用器械的动作
    available = db.query(
        "SELECT * FROM exercises WHERE body_part = ANY(%s) AND equipment = ANY(%s)",
        [body_parts, equipment + ["body weight"]]
    )
    
    # 按部位均衡选取
    selected = []
    for part in body_parts:
        candidates = [e for e in available if e["body_part"] == part]
        selected.extend(random.sample(candidates, min(2, len(candidates))))
    
    return selected
```

**自重居家训练模式**

25% 的动作是纯自重，筛选一下就是一个完整的「无器材健身」功能模块：

```sql
SELECT * FROM exercises 
WHERE equipment = 'body weight'
ORDER BY body_part, name;
```

### 第四步：多语言支持

数据里的 9 种语言说明开箱即用，不需要额外翻译成本：

```typescript
// 根据用户语言选择说明文字
const lang = userLocale.startsWith('zh') ? 'zh' 
           : userLocale.startsWith('es') ? 'es'
           : 'en';  // 默认英文

const steps = exercise.instruction_steps[lang] ?? exercise.instruction_steps['en'];
```

---

## 许可证说明

这个仓库分两层许可：

- **代码和元数据（exercises.json 等）**：MIT 许可，可商用
- **媒体文件（GIF 和缩略图）**：© Gym visual，使用条款见 `NOTICE.md`

具体来说：GIF 和缩略图可以在 App 内展示，但不能二次销售媒体本身、修改版权声明，或把媒体单独打包再发布。在 App 里显示运动教学图是允许的，只需要保留 `attribution` 字段对应的版权说明。

生产环境建议：把媒体文件上传到自己的 CDN，而不是直接引用 GitHub raw 链接（CDN 速度更快，也不会受 GitHub 速率限制影响）。

---

## 和 LogPress 的关系

这个数据集是 [LogPress](https://github.com/hasaneyldrm/logpress-public) App（AI 辅助训练记录）的运动数据层。LogPress 是一个实际在用的应用，这意味着数据集经过了实际产品验证——动作分类、说明文字的质量都是经过用户反馈打磨过的。

如果你在做类似的训练记录 App，可以参考 LogPress 的实现方式；如果只需要数据层，exercises-dataset 单独使用就够。

---

## 适合接这个数据集的 App 类型

- **训练记录 App**（最直接，LogPress 本身就是这个）
- **AI 训练计划生成器**：数据结构化程度高，很适合作为 RAG 数据源或 LLM 的工具调用参数
- **运动科普 / 教学 App**：9 种语言说明 + GIF，内容层直接覆盖
- **康复 / 物理治疗辅助工具**：有肌肉分组数据，可以做「这块肌肉受伤了，推荐相关替代动作」的逻辑
- **健康穿戴设备配套 App**：运动识别后对应到数据集里的动作 ID，展示说明和动画

---

GitHub：[github.com/hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset)  
在线浏览：克隆后打开 `index.html`  
集成向导：克隆后打开 `setup.html`

© 2026 Author: Mycelium Protocol

<!--EN-->

## The Data Foundation for Fitness Apps: exercises-dataset

> GitHub: [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset) · ⭐ 14,036 · MIT (code/data) + Gym visual media terms

---

### What It Is

Building a fitness app, the hardest part isn't the UI — it's the exercise content. exercises-dataset solves that: 1,324 exercises, each with a 180×180 animation GIF, thumbnail, structured muscle-group metadata, and step-by-step instructions in 9 languages (English, Spanish, Italian, Turkish, Russian, Chinese, Hindi, Polish, Korean).

It's the exercise data layer powering the [LogPress](https://github.com/hasaneyldrm/logpress-public) AI workout tracker — so it's production-tested, not just a research dump.

---

### What's in the Data

**Coverage:**
- 1,324 exercises across all major body parts and equipment types
- ~25% body-weight-only exercises — full coverage for no-equipment apps
- 9-language instructions, both as full text and as step arrays

**Per-exercise fields:**

| Field | Use |
|---|---|
| `id`, `name` | Identifier and display name |
| `body_part`, `category` | Filter by muscle area |
| `equipment` | Filter by available gear |
| `target` | Primary muscle targeted |
| `secondary_muscles[]` | For "exercises that also work X" recommendations |
| `instructions.{lang}` | Full text for detail pages |
| `instruction_steps.{lang}[]` | Steps array for cards / voice playback |
| `image`, `gif_url` | 180×180 thumbnail and animation |

---

### Getting Started

**The repo ships two browser tools — no server needed:**

- **`index.html`** — full exercise browser with search, filter by body part / equipment / target, infinite scroll, 9-language instruction toggle
- **`setup.html`** — generates a ready-to-run `.sql` file (PostgreSQL, MySQL, SQLite, SQL Server) with all 1,324 INSERT statements; generates copy-paste API client code in JS/Python/C#/Java/PHP/Go; generates an LLM prompt for one-shot REST API scaffolding

---

### Integration Path

**1. Database import (SQLite example)**

```bash
# Open setup.html in browser → select SQLite → download exercises_sqlite.sql
sqlite3 exercises.db < exercises_sqlite.sql
sqlite3 exercises.db "SELECT COUNT(*) FROM exercises;"  # → 1324
```

**2. Core API endpoints**

```
GET /exercises?body_part=chest&equipment=barbell
GET /exercises?target=biceps
GET /exercises/{id}
```

Use `setup.html`'s LLM prompt (select framework + database → copy → paste to Claude) to generate the full REST API in one shot. Supported: Express.js, FastAPI, ASP.NET Core, Spring Boot, Laravel, Gin.

**3. Key feature modules**

**Exercise search/filter** — `body_part`, `equipment`, `target` fields map directly to filter UI. The `secondary_muscles` array enables "exercises that also train X" cross-recommendations.

**Step-by-step detail view** — use `instruction_steps.{lang}` arrays for step cards or voice playback. Language switching is just changing the key; all 9 languages are in the JSON.

**Workout plan generator** — structured metadata makes it easy to sample exercises by body part and equipment availability.

**No-equipment mode** — `WHERE equipment = 'body weight'` returns 325 exercises, a complete standalone home workout library.

---

### License Notes

- **Code and data** (exercises.json, schema, HTML tools): MIT — commercial use permitted
- **Media** (GIFs and thumbnails): © Gym visual — permitted for in-app display; cannot be resold or redistributed as a standalone media pack

In production, host media on your own CDN rather than linking to GitHub raw URLs.

---

GitHub: [github.com/hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset)

© 2026 Author: Mycelium Protocol
