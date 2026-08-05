---
title: "Marble 开源儿童课程知识图谱：1590 个微话题 + 3221 条前置关系，对齐主流课标"
titleEn: "marble-os-taxonomy-children-curriculum-knowledge-graph"
description: "withmarbleapp/os-taxonomy 是 Marble 开源的儿童小学阶段学习知识图谱：1590 个可教授微话题（科学/数学/英语等8科）+ 3221 条有向前置依赖边 + 对齐 NGSS/Common Core/英国课程标准。纯 JSON 数据，ODbL 1.0 + CC BY-SA 4.0 双许可，可用于构建 AI 家教、自适应学习路径和课程分析工具。3849 stars。"
descriptionEn: "withmarbleapp/os-taxonomy is Marble's open-source children's learning knowledge graph: 1,590 micro-topics (Science/Math/English and 5 more subjects) + 3,221 directed prerequisite edges + alignment to NGSS/Common Core/UK National Curriculum. Pure JSON, ODbL 1.0 + CC BY-SA 4.0, ready for AI tutors, adaptive learning paths, and curriculum tools. 3,849 stars."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["教育科技", "知识图谱", "课程数据", "AI家教", "开源数据集", "自适应学习", "儿童教育", "Mycelium"]
heroImage: "../../assets/images/marble-os-taxonomy-children-curriculum-knowledge-graph-banner.jpg"
---

*by Mycelium Protocol*

---

儿童课程数据一直存在两个极端：要么是一张平铺的知识点清单（没有关系、没有顺序），要么锁在商业产品里（开放一点 demo，核心数据闭源）。

**[Marble Skill Taxonomy](https://github.com/withmarbleapp/os-taxonomy)**（withmarbleapp）把这两个问题都解决了：一个完整的**儿童小学阶段学习知识图谱**，1590 个微话题，3221 条有向前置依赖边，对齐 NGSS / Common Core / 英国国家课程等主流课标，以纯 JSON 格式开放，双许可（数据库 ODbL 1.0，文本内容 CC BY-SA 4.0）。

3849 stars，由 EdTech 公司 [Marble](https://withmarble.com/) 发布。

---

## 它是什么

一个面向**小学阶段**（幼儿园到约 12 岁）的、结构化的**学习知识图谱**，有三个核心部分：

### 1. 1590 个微话题（Micro-Topics）

每个微话题是一个「可单独教授的最小概念单元」，包含：

```json
{
  "id": "mt_N8CpN1EJrP",
  "type": "CONCEPTUAL",
  "subject": "English",
  "domain": "Grammar & Punctuation",
  "name": "Building sentences",
  "description": "Understand that words combine to make sentences...",
  "ageRangeStart": 4,
  "ageRangeEnd": 6,
  "centrality": 0.257,
  "evidence": [
    "Distinguish between complete sentences and fragments",
    "Compose a complete sentence with a subject and verb"
  ],
  "assessmentPrompt": "If {{name}} says something like \"The dog\", can they tell you that's not a complete sentence?",
  "standards": ["ccss-ela:L.K.1f", "uk-nc-2013:Eng.App2.Y1.Sent.1"]
}
```

字段解释：
- `type`：`CONCEPTUAL`（概念）/ `PROCEDURAL`（程序性）/ `REPRESENTATIONAL`（表征）/ `LANGUAGE`（语言）/ `META`（元认知）
- `centrality`：在整个图里的重要性权重（越高越基础）
- `evidence`：判断这个微话题是否真正掌握的可观察证据
- `assessmentPrompt`：自然语言形式的检测题，含 `{{name}}` 占位符
- `standards`：对齐的课标代码（格式 `<课标slug>:<代码>`）

### 2. 3221 条前置依赖边（Prerequisite Graph）

有向无环图，每条边有理由：

```json
{
  "topicId": "mt__00ZSLnB7p",
  "prerequisiteId": "mt_VBl1T1sFCM",
  "strength": "hard",
  "reason": "Must understand vibrations make sound before finding volume patterns"
}
```

- `strength: "hard"`：强依赖，不满足前置就无法理解当前话题
- `strength: "soft"`：软依赖，有了更好，没有也可以学

反转边方向即得「解锁图」：掌握 X 之后，能开启哪些新话题。

### 3. 课标对齐

- **NGSS**（Next Generation Science Standards，美国）
- **Common Core**（美国英语/数学标准）
- **英国国家课程**（UK National Curriculum）
- 及其他主流课标

---

## 8 个学科分布

| 学科 | 话题数 |
|------|--------|
| 科学 | 547 |
| 数学 | 503 |
| 英语 | 286 |
| 历史 | 90 |
| 个人与社会发展 | 88 |
| 生活技能 | 37 |
| 计算机 | 21 |
| 学会学习 | 18 |
| **合计** | **1590** |

科学和数学加起来占了 66%，也是逻辑前置关系最密集的两个学科。

---

## 数据文件结构

```
data/
├── topics.json              # 微话题节点（1590 个）
├── dependencies.json        # 前置依赖边（3221 条）
├── curriculum-standards.json # 源课标，按课标分组
├── clusters.json            # 183 个域集群摘要（家长友好的一段话说明）
└── manifest.json            # 计数、各科分布、文件 SHA-256
schema/
└── *.json                   # JSON Schema，可用于验证数据
```

加载方式，纯 JavaScript，零依赖：

```javascript
import topics from './data/topics.json' with { type: 'json' };
import deps from './data/dependencies.json' with { type: 'json' };

const byId = new Map(topics.topics.map(t => [t.id, t]));

// 查某个话题的所有前置
const prereqs = deps.dependencies
  .filter(d => d.topicId === 'mt_N8CpN1EJrP')
  .map(d => byId.get(d.prerequisiteId).name);

// 验证数据完整性
node scripts/validate.mjs
```

---

## 可视化

Marble 提供了一个 3D 旋转可视化：每个点是一个微话题，颜色按学科区分，高度代表年龄，线条是前置关系。

可以在 [withmarble.com/curriculum](https://withmarble.com/curriculum) 交互探索——点击任意概念，追溯学习这个概念之前必须掌握的所有内容。

---

## 它能用来做什么

### 1. AI 家教 / 自适应学习系统

前置图天然支持「诊断 → 定位 → 推荐下一步」的循环：

```python
def get_unlocked_topics(mastered_ids, all_deps):
    """找出所有前置都已掌握的话题（即可以开始学的）"""
    unlocked = []
    for dep in all_deps:
        prereqs = [d for d in all_deps if d['topicId'] == dep['topicId']]
        if all(p['prerequisiteId'] in mastered_ids for p in prereqs):
            unlocked.append(dep['topicId'])
    return list(set(unlocked))
```

结合 `centrality` 字段，可以优先推荐高中心性（基础性强）的话题，构建最优学习路径。

### 2. 给 LLM 构建教育 RAG

每个微话题有 `description` + `evidence` + `assessmentPrompt`，直接可以向量化入库，用作 AI 家教的知识来源，而且每条内容天然带着年龄范围和学科标签，检索时可以精准过滤。

### 3. 课程分析和可视化工具

183 个域集群摘要（`clusters.json`）是家长友好的模块说明，适合做课程展示页。前置图可以用 D3.js / Cytoscape 做交互可视化，定位课程里的「关键节点」（中心性高但被依赖多的话题）。

### 4. 课标差异分析

每个话题都有 `standards` 字段，可以跨课标对比同一个概念的覆盖情况：Common Core 要求 K 年级学这个，英国课标是哪一年？差异在哪里？

---

## 许可证：商业友好但有条件

这个项目用了双许可，要在使用前认真读一下：

| 层 | 许可证 | 实际意义 |
|----|--------|---------|
| 数据库结构（ID、关系、图结构） | ODbL 1.0 | 可商业使用，**必须署名**；派生**数据库**必须开源；但你的产品不需要开源 |
| 文本内容（名称/描述/evidence/prompt/原因） | CC BY-SA 4.0 | 可商业使用，**必须署名**，衍生内容需相同方式共享 |
| `curriculum-standards.json`（第三方课标） | 各自的上游许可证 | 见 PROVENANCE.md，用之前需单独确认 |

**关键点**：ODbL 的「share-alike」针对的是**衍生数据库**，而不是你的产品。你可以用这个数据集构建商业产品而不开源你的产品；只有当你**修改了这份分类数据本身**并重新发布时，才需要以 ODbL 开放。

**必须注明的署名**：

> Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com · licensed under ODbL 1.0 (database) and CC BY-SA 4.0 (content).

---

## 刻意不包含的内容

值得注意的是，Marble 有意排除了：
- **语义嵌入向量**（说明可以自己重新计算）
- **任何用户/儿童数据**（这部分永远不会发布）

---

## 为什么值得关注

**教育数据的开放程度一直远低于其他领域**。医学有 MIMIC，法律有 CourtListener，代码有 GitHub——教育数据里真正有结构的、有关系的、可被机器直接用的，几乎没有。

Marble 这份数据集的稀缺性不在于话题数量（1590 个），而在于**前置关系**（3221 条有理由的有向边）——这是最难众包、最难从现有数据里提取的部分，也是让这个图真正可用于自适应学习的核心。

AI 家教方向最近几年在资本侧重新热起来，但大多数产品没有严肃的知识结构——它们只是把 GPT 接上了课本。一个有前置依赖图的数据集，在这个方向上是基础设施级别的资产。

3849 stars，2026 年 7 月开源，ODbL 1.0 可商用。

仓库：[github.com/withmarbleapp/os-taxonomy](https://github.com/withmarbleapp/os-taxonomy) · 交互可视化：[withmarble.com/curriculum](https://withmarble.com/curriculum)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Marble Open-Sources a Children's Curriculum Knowledge Graph: 1,590 Topics, 3,221 Prerequisite Edges, Aligned to Major Standards

*by Mycelium Protocol*

Curriculum data has always existed at two extremes: flat lists of standards (no relationships, no order), or locked inside commercial products. **[Marble Skill Taxonomy](https://github.com/withmarbleapp/os-taxonomy)** (withmarbleapp) addresses both problems: a complete knowledge graph of children's learning through primary school — 1,590 micro-topics, 3,221 directed prerequisite edges, aligned to NGSS / Common Core / UK National Curriculum, released as pure JSON under ODbL 1.0 + CC BY-SA 4.0. 3,849 stars, published by EdTech company [Marble](https://withmarble.com/).

### What It Is

A structured learning knowledge graph covering the primary years (roughly kindergarten through age 12), with three core components:

**1,590 micro-topics** — each a single teachable idea, with:
- `type`: CONCEPTUAL / PROCEDURAL / REPRESENTATIONAL / LANGUAGE / META
- `ageRangeStart` / `ageRangeEnd`: the developmental window
- `centrality`: importance weight in the full graph (higher = more foundational)
- `evidence`: observable criteria for genuine mastery
- `assessmentPrompt`: a natural-language check with `{{name}}` placeholder
- `standards`: aligned standard codes (format: `<curriculum-slug>:<code>`)

**3,221 prerequisite edges** — a directed acyclic graph:
```json
{
  "topicId": "mt__00ZSLnB7p",
  "prerequisiteId": "mt_VBl1T1sFCM",
  "strength": "hard",
  "reason": "Must understand vibrations make sound before finding volume patterns"
}
```
`strength: "hard"` = cannot understand the topic without the prerequisite.  
Reverse the edge direction to get an "unlocks" graph.

**Curriculum alignment** — each topic links to the standards it was distilled from, across NGSS, Common Core, UK National Curriculum, and more.

### Subject Distribution

| Subject | Topics |
|---------|--------|
| Science | 547 |
| Mathematics | 503 |
| English | 286 |
| History | 90 |
| Personal & Social Development | 88 |
| Life Skills | 37 |
| Computing | 21 |
| Learning to Learn | 18 |

### What You Can Build

**AI tutors and adaptive learning systems** — the prerequisite graph supports a diagnose → locate → recommend-next loop. `centrality` lets you prioritize foundational topics and build optimal learning paths.

**Educational RAG for LLMs** — each micro-topic has `description` + `evidence` + `assessmentPrompt`, ready for vector embedding. Each entry carries age range and subject labels for precise retrieval filtering.

**Curriculum visualization** — 183 parent-friendly domain cluster summaries (`clusters.json`) plus the prerequisite graph, ready for D3.js or Cytoscape interactive visualization.

**Cross-standard analysis** — compare how Common Core and the UK National Curriculum handle the same concept, when each introduces it, and where they diverge.

### Loading the Data

Pure JSON, zero runtime dependencies:

```javascript
import topics from './data/topics.json' with { type: 'json' };
import deps from './data/dependencies.json' with { type: 'json' };

const byId = new Map(topics.topics.map(t => [t.id, t]));
const prereqs = deps.dependencies
  .filter(d => d.topicId === 'mt_N8CpN1EJrP')
  .map(d => byId.get(d.prerequisiteId).name);
```

### License: Commercial-Friendly, With Conditions

| Layer | License | What it means |
|-------|---------|--------------|
| Database (structure, IDs, relationships) | ODbL 1.0 | Commercial OK; attribution required; derivative *databases* must stay open — but your *product* doesn't |
| Text content (names, descriptions, evidence, prompts) | CC BY-SA 4.0 | Commercial OK; attribution + share-alike on derivative content |
| `curriculum-standards.json` | Upstream licenses | Check PROVENANCE.md before using |

The ODbL share-alike applies to *derivative databases*, not to products built on the data. You can ship a commercial product without open-sourcing it; only improvements to the taxonomy itself must come back.

### Why This Matters

Educational data is far less open than other domains — medicine has MIMIC, law has CourtListener, code has GitHub. Structured, relationship-rich, machine-usable curriculum data barely exists.

The scarce part of this dataset isn't the 1,590 topics — it's the 3,221 prerequisite edges with stated reasons. That's the part that can't be crowdsourced easily and can't be extracted from existing flat standards lists. It's also what makes the graph actually usable for adaptive learning rather than just being another content catalog.

AI tutoring has attracted renewed investment recently, but most products lack serious knowledge structure. A dataset with a prerequisite dependency graph is infrastructure-level for this space.

3,849 stars, open-sourced July 2026, ODbL 1.0 for commercial use.

Repository: [github.com/withmarbleapp/os-taxonomy](https://github.com/withmarbleapp/os-taxonomy) · Interactive: [withmarble.com/curriculum](https://withmarble.com/curriculum)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
