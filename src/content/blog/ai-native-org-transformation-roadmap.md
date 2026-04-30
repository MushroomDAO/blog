---
title: "普通组织的 AI-native 转型路线：6 步框架"
titleEn: "AI-Native Transformation Roadmap for Regular Organizations: A 6-Step Framework"
description: "借鉴 Anthropic 的 AI-native 组织实践，为普通企业提炼出可操作的 6 步转型路线：从价值链诊断、对齐机制重建、角色分工重构，到能力域定义、工具体系构建、交付节奏压缩。附带角色能力矩阵和工具选型框架，供直接套用。"
descriptionEn: "Drawing on Anthropic's AI-native organizational practices, this post distills a 6-step transformation roadmap for regular organizations: from value chain diagnosis and alignment mechanism rebuilding, to role restructuring, capability domain definition, tooling, and delivery cycle compression. Includes a role capability matrix and tooling framework for direct use."
pubDate: "2026-04-30"
updatedDate: "2026-04-30"
category: "Research"
tags: ["AI Native", "组织转型", "工作流", "角色分工", "Research", "Anthropic", "Product Thinking"]
heroImage: "../../assets/banner-future-is-now.jpg"
---

> **本文是「AI Native 三个层级」的配套操作手册**，聚焦于第二层：**普通组织如何完成结构性转型**。Anthropic 的案例提供参照系，但核心框架适用于任何规模的企业或团队。
>
> **创作说明**：Jason（Mycelium Protocol 创始人）与 AI（Claude）对话讨论后，由 AI 按 Jason 的意图整理输出的原创文章。框架和观点为 Jason 原创，Anthropic 案例注明来源引用。
>
> **转载注明**：Anthropic 案例来源 — Lenny's Podcast [How Anthropic's product team moves faster than anyone else](https://www.lennysnewsletter.com/p/how-anthropics-product-team-moves) · [YouTube](https://www.youtube.com/watch?v=PplmzlgE0kg) · [Twitter](https://x.com/lennysan/status/2047377335406694431) · Cat Wu [@_catwu](https://x.com/_catwu)

---

## 核心前提：先理解 Anthropic 模型的底层逻辑

Anthropic 的 AI-native 组织之所以能跑这么快，不是因为他们更努力，而是因为他们把一件事想清楚了：

**围绕「价值链」组织分工，而不是围绕「职能模块」。**

Anthropic 的价值链长这样：

```
用户反馈 → 模型能力 → 平台基础设施 → 产品 → 企业采用 → 增长
```

他们的 PM 团队，每类人守一个链路节点，而不是"前端 PM"、"后端 PM"、"增长 PM"这种功能切割。

**把这个底层逻辑抽象出来，普通组织的价值链是：**

```
客户信号 → 核心能力 → 支撑基础设施 → 产品/服务交付 → 客户成功 → 规模增长
```

链路节点可能不同，但逻辑一样：**每个人守一个节点，负责节点之间的信息和价值流动。**

---

## 6 步转型路线

### Step 1 · 诊断你的「价值链」

在做任何组织变革之前，先把这张图画出来。

**操作方法：**

| 问题 | 你的答案 |
|------|----------|
| 你的客户信号从哪里来？（投诉、NPS、访谈、数据？） | |
| 你的「核心能力」是什么？（你比别人强在哪里？） | |
| 支撑这个能力运转的基础设施是什么？（系统、工具、数据？） | |
| 你的产品/服务是怎么交付到客户手里的？ | |
| 客户成功的关键指标是什么？ | |
| 增长的主要驱动力是什么？ | |

**目标输出**：一张 6 节点的价值链图，后续所有角色分工都围绕这张图来设计。

> **常见错误**：大多数企业画的是组织架构图，不是价值链图。组织架构图描述的是权力结构，价值链图描述的是价值流动。AI-native 转型围绕的是后者。

---

### Step 2 · 建立两套「对齐机制」，取代 PRD

Anthropic 用两件事替代了传统的 PRD 审批体系：**每周全团队指标解读会 + 团队原则清单**。

对普通组织来说，这两件事的意义是：**把对齐前置，把反复确认的成本压掉。**

#### 机制一：全团队指标解读会（Weekly Metrics Review）

| 要素 | 说明 |
|------|------|
| **参与者** | 所有人，不只是管理层和 PM |
| **频率** | 每周，固定时间，不超过 30 分钟 |
| **内容** | 核心指标的变化 + 背后的驱动因素分析 |
| **目的** | 让每个人都能自己判断"这个问题重不重要"，不需要层层请示 |

这件事的本质是：**把决策上下文下发给执行层**。当工程师或一线员工理解业务数字的时候，他们就能在没有需求文档的情况下，判断自己要做什么。

#### 机制二：团队原则清单（Principles Document）

| 要素 | 说明 |
|------|------|
| **核心用户是谁** | 明确，不模糊。"25-35岁的独立设计师"比"创意从业者"好 |
| **为什么是这群人** | 写出选择理由，避免未来反复论证 |
| **团队愿意做的取舍** | 当速度和完整性冲突时选哪个？新用户和老用户冲突时优先谁？ |
| **不做什么** | 明确的边界比模糊的范围更有用 |

**两套机制的效果**：工程师自己能判断，设计师自己能取舍，不需要每次都找 PM 确认。Cat Wu 说的"把反复确认的成本压掉"，指的就是这个。

---

### Step 3 · 围绕价值链重构角色分工

这是整个框架里改动最大、阻力最强的一步。

**Anthropic 的 5 类 PM 对应到普通组织的 5 类角色：**

| Anthropic PM 类型 | 核心职责 | 普通组织对应角色 | 核心职责（通用化） |
|------------------|---------|----------------|------------------|
| 研究型 PM | 用户反馈 → 模型团队 | **信号收集者** | 客户反馈 → 核心能力团队 |
| 平台型 PM | 底层 API 和开发者工具 | **基础设施建设者** | 内部工具和数据平台 |
| 产品型 PM | 核心产品交付 | **核心交付者** | 主产品/服务的打磨和迭代 |
| Enterprise PM | 企业采用和合规 | **规模化推进者** | 降低采用门槛、合规管控 |
| 增长 PM | 驱动整体增长 | **增长驱动者** | 获客、留存、扩张 |

**重要说明**：这 5 类不是 5 个独立岗位，而是 5 种**职责方向**。在小团队里，一个人可以兼多个。关键是：**每个节点有人负责，没有真空地带**。

#### 角色分工表（可直接套用）

| 角色 | 守的链路节点 | 主要输出 | 与相邻节点的接口 |
|------|------------|---------|----------------|
| 信号收集者 | 客户信号 | 结构化洞察报告、反馈优先级 | 上游：客户；下游：核心交付者 |
| 基础设施建设者 | 支撑基础设施 | 内部工具、数据接口、自动化流程 | 上游：核心交付者；下游：所有角色 |
| 核心交付者 | 产品/服务交付 | 可用的产品/服务版本 | 上游：信号收集者、基础设施；下游：规模化推进者 |
| 规模化推进者 | 客户成功 | 客户落地方案、合规文档、成本优化 | 上游：核心交付者；下游：增长驱动者 |
| 增长驱动者 | 规模增长 | 增长数据、获客渠道、传播内容 | 上游：规模化推进者；下游：信号收集者（形成闭环） |

> **注意**：这张表构成的是一个**环形闭环**，不是单向流水线。增长驱动者带来的新用户反馈，流回信号收集者，驱动下一轮迭代。

---

### Step 4 · 为每个角色定义 AI 能力域

这是 AI-native 组织和传统组织最本质的区别：**每个角色都需要具备 AI 能力，而不只是 AI 团队。**

Cat Wu 提炼出的关键能力有两个：**Product Taste（产品品味）**和**第一性原理思维**。把这两个加上 AI 工具能力，构成四维能力模型：

#### 四维 AI 能力模型

| 能力维度 | 定义 | 具体表现 | 谁最需要 |
|---------|------|---------|---------|
| **Skill 流利度** | 熟练使用 AI 工具完成本职工作 | 用 AI 写报告、分析数据、生成内容、写代码 | 所有人 |
| **Agent 流利度** | 能设计任务、指挥 Agent、验收结果 | 能写清楚任务范围、评估 Agent 输出质量、迭代 Prompt | 核心交付者、基础设施建设者 |
| **产品品味** | 判断"什么值得做"的能力 | 面对 100 个需求知道先做哪 3 个；看出用户真正要的是什么 | 核心交付者、信号收集者 |
| **第一性原理思维** | 技术变化时不依赖旧模式重新推导 | 新工具出来能快速判断是否值得切换；不被"我们一直这么做"困住 | 基础设施建设者、增长驱动者 |

#### 各角色能力优先级矩阵

| 角色 | Skill 流利度 | Agent 流利度 | 产品品味 | 第一性原理 |
|------|:-----------:|:-----------:|:-------:|:---------:|
| 信号收集者 | ★★★ | ★★ | ★★★ | ★★ |
| 基础设施建设者 | ★★★ | ★★★ | ★★ | ★★★ |
| 核心交付者 | ★★★ | ★★★ | ★★★ | ★★★ |
| 规模化推进者 | ★★★ | ★★ | ★★ | ★★ |
| 增长驱动者 | ★★★ | ★★ | ★★ | ★★★ |

**最核心的稀缺点**：Cat Wu 原话——代码越来越便宜，真正稀缺的是"谁知道该写什么"。在普通组织里，对应的是：**谁知道该优先做什么**。这个判断力就是产品品味，它不是 PM 的专属技能，是 AI-native 组织里每个人都要有的底色。

---

### Step 5 · 构建专属工具体系

Anthropic 的工具体系有一个特点：**不是通用工具，是专为他们的工作流打造的**。比如固定发布协作群、研究型 PM 专用的反馈路由机制。

对普通组织来说，工具体系分三层：

#### 工具体系三层架构

| 层级 | 作用 | 典型工具/机制 | 构建优先级 |
|------|------|-------------|-----------|
| **对齐层** | 替代 PRD，让全员共享决策上下文 | 共享数据看板、原则文档、指标周会 | 第一优先 |
| **Harness 层** | 让 Agent 可以稳定执行任务 | 任务模板库、Prompt 规范、输出验收标准 | 第二优先 |
| **交付层** | 让发布成为常规动作 | 固定发布协作群/频道、发布检查清单、版本标记规范 | 第三优先 |

#### 各角色工具建议

| 角色 | 对齐工具 | Harness 工具 | 交付工具 |
|------|---------|-------------|---------|
| 信号收集者 | 客户反馈看板（Notion/Linear） | 访谈分析 Agent、NPS 综合 Agent | 洞察报告模板 |
| 基础设施建设者 | 技术债/工具地图 | CI/CD Agent、代码审查 Agent | 部署检查清单 |
| 核心交付者 | 产品路线图（围绕原则清单） | 功能原型 Agent、设计审查 Agent | Research Preview 发布流 |
| 规模化推进者 | 客户落地追踪表 | 合规文档生成 Agent、培训内容 Agent | 客户成功 SOP |
| 增长驱动者 | 增长指标实时看板 | 内容生成 Agent、数据分析 Agent | 内容发布自动化流水线 |

> **关于工具选型的原则**：不要先选工具再设计流程。先把流程（Step 1-4）想清楚，再选工具。工具是流程的载体，不是流程的起点。

---

### Step 6 · 压缩交付节奏，让发布成为常规动作

Anthropic 的发布逻辑值得完整复制：

**传统模式**：需求 → PRD → 评审 → 排期 → 开发 → 测试 → 发布准备 → 上线

**AI-native 模式**：功能 ready → 内部试用 → 发到固定发布群 → 同步跟进 → 下一天公告

差距来自两个地方：
1. **对齐前置**：因为原则清单和指标周会已经让所有人对目标有共识，不需要在发布前再拉齐
2. **发布本身是固定动作**：不需要每次重新组织

**普通组织的发布 SOP（6 步标准动作）：**

| 步骤 | 内容 | 负责人 | 完成标准 |
|------|------|-------|---------|
| 1. 内部验收 | 核心交付者确认功能/服务达到发布标准 | 核心交付者 | 通过验收清单 |
| 2. 内部试用 | 相关团队内部使用 24-48 小时 | 所有相关方 | 无阻塞性问题 |
| 3. 发布群通知 | 发到固定发布协作群，抄送相关方 | 核心交付者 | 通知已送达 |
| 4. 同步跟进 | 文档、市场、客户成功同时更新各自材料 | 各角色自行负责 | 各自材料就绪 |
| 5. 对外发布 | 以 research preview 或正式版形式发出 | 增长驱动者 | 已触达目标用户 |
| 6. 反馈收集 | 发布后 72 小时内收集真实反馈 | 信号收集者 | 反馈进入下一个迭代 |

**关键原则**：步骤 1-2 是核心交付者的事，步骤 3-6 是标准动作，相关人自己接上，不需要任何人去"拉齐"。这就是 Cat Wu 说的"把对齐前置了"——发布时的成本已经在平时的指标周会和原则清单里还掉了。

---

## 全流程总览

```
Step 1: 画出你的价值链（6 节点）
   ↓
Step 2: 建立两套对齐机制（指标周会 + 原则清单）
   ↓
Step 3: 围绕价值链重构角色分工（5 类角色 × 链路节点）
   ↓
Step 4: 为每个角色定义 AI 能力域（4 维矩阵）
   ↓
Step 5: 构建 3 层工具体系（对齐层 + Harness 层 + 交付层）
   ↓
Step 6: 压缩交付节奏（6 步标准发布 SOP）
```

---

## 几个常见的坑

**坑一：先买工具，后想流程**

大多数组织的 AI 转型，从采购 AI 工具开始。但工具解决不了对齐问题——如果原则清单没有，指标周会没有，再好的 AI 工具也只是让个别人变快，不会让组织变快。

**坑二：只让"AI 负责人"懂 AI**

AI 能力不是一个部门的事。只有全员都有 Skill 流利度，组织才能进入 AI-native 节奏。一个不会用 AI 的工程师等需求，一个不会用 AI 的设计师等反馈，都是整条价值链上的速度瓶颈。

**坑三：把 AI 转型当成技术项目**

Step 1-3 全是组织设计决策，不是技术决策。价值链怎么画、角色怎么分、原则清单写什么——这些事情没有办法用 AI 来做，只能由领导层和核心团队坐下来想清楚。技术（Step 4-5）是在组织设计想清楚之后才能发挥作用的。

**坑四：跳过 Step 6，以为慢是正常的**

发布慢通常不是因为开发慢，而是因为发布流程没有标准化。每次上线都要重新拉会、重新对齐、重新解释背景——这些成本是可以通过 SOP 和对齐前置消掉的。

---

## 适用于不同类型组织的调整建议

| 组织类型 | 价值链重点 | 最优先的 Step | 最大阻力 |
|---------|----------|-------------|---------|
| 互联网产品公司 | 用户反馈→产品迭代→增长 | Step 3（角色重构） | 岗位边界保护 |
| 传统制造企业 | 供应链→生产→销售→服务 | Step 2（对齐机制） | 信息不透明 |
| 咨询/服务公司 | 客户洞察→方案交付→客户成功 | Step 4（能力域定义） | 依赖个人经验 |
| 小型创业团队 | 全链路，每人兼多个角色 | Step 1（价值链诊断） | 资源有限、顾不上设计 |
| 非营利组织/社区 | 成员信号→能力建设→影响力 | Step 6（交付节奏） | 志愿者体制，难以约束 |

---

> **最后一句话**：Anthropic 的模型不能直接复制，但它的底层逻辑可以。那个逻辑是：**围绕价值流动组织人，而不是围绕职能边界**。这是 AI-native 转型的起点，其他的都是执行。

---

## 附：深入理解「谁知道该写什么」

Cat Wu 原话里的"写"，就是字面意思——**写代码**。她说的是：AI 能写大多数代码了，所以"会写代码"这件事越来越不稀缺，真正稀缺的变成了"该写什么"的判断力。

但"该写什么"不等于愿景、规划、方向这些宏观词汇，要更精确一些。

理解这个概念，需要先看清楚 AI 正在往上吃一个**能力栈**：

```
愿景 / 价值观（Why — 目前 AI 无法替代）
    ↓
方向 / 规划（Where to go）
    ↓
设计 / 目标（What to build）
    ↓
产品品味（此刻选哪 3 件事 ← 当前稀缺点）
    ↓
具体设计（UI、原型 → AI 正在接管）
    ↓
执行 / 写代码（How → AI 已大量接管）
```

AI 从栈底往上吃。写代码被吃掉了，具体设计（UI 生成、原型生成）正在被吃。**目前还吃不动的，是中间那层「产品品味」——此刻该做哪 3 件事的判断。**

这个判断之所以难被替代，是因为它需要同时掌握三件事：

1. **用户真正要什么**（不是他说的，是他用脚投票的）
2. **这件事和目标的距离有多近**（价值校准）
3. **现在做还是以后做，差别有多大**（时机判断）

光有愿景是策略家，光会执行是工具人。**真正稀缺的，是既有方向感、又能把方向感转化成每天具体判断的人。** 这就是 Cat Wu 说的 product taste，也是 AI-native 时代每个角色都需要建立的核心能力。

对应回本文的 Step 4：四维能力矩阵里，**产品品味**是唯一一个 AI 目前无法提供的维度——因为它依赖真实的上下文、真实的用户理解、以及做出判断后承担结果的责任感。

<!--EN-->

> **This post is the companion operations manual for "Three Layers of AI-Native Transformation," focused on Layer 2: how regular organizations complete structural transformation.** The Anthropic case provides the reference model; the framework here is designed for any organization at any scale.
>
> **About this article**: Original work by Jason (Mycelium Protocol founder), developed through discussion with AI (Claude) and organized by AI per Jason's intent. The 6-step framework is Jason's original synthesis. The Anthropic case is cited as a reference.
>
> **Citation**: Anthropic case source — Lenny's Podcast [How Anthropic's product team moves faster than anyone else](https://www.lennysnewsletter.com/p/how-anthropics-product-team-moves) · [YouTube](https://www.youtube.com/watch?v=PplmzlgE0kg) · [Twitter](https://x.com/lennysan/status/2047377335406694431) · Cat Wu [@_catwu](https://x.com/_catwu)

---

## Core Premise: The Underlying Logic of the Anthropic Model

Anthropic's AI-native organization runs fast not because they work harder, but because they got one thing right:

**Organize roles around the value chain, not around functional silos.**

Anthropic's value chain:
```
User Feedback → Model Capability → Platform Infrastructure → Product → Enterprise Adoption → Growth
```

Their PM team assigns each person to a chain node, not to a functional module. The generalized version:

```
Customer Signal → Core Capability → Supporting Infrastructure → Product/Service → Customer Success → Scale Growth
```

---

## 6-Step Transformation Roadmap

### Step 1 · Diagram Your Value Chain

Before any organizational change, draw this map.

| Question | Your Answer |
|----------|-------------|
| Where do your customer signals come from? (complaints, NPS, interviews, data?) | |
| What is your "core capability"? (what do you do better than anyone?) | |
| What infrastructure supports that capability? (systems, tools, data?) | |
| How does your product/service reach customers? | |
| What are your key customer success metrics? | |
| What drives growth? | |

**Target output**: A 6-node value chain map. All role assignments are designed around this map.

> **Common mistake**: Most companies draw org charts, not value chain maps. Org charts describe power structures. Value chain maps describe value flow. AI-native transformation follows the latter.

---

### Step 2 · Build Two Alignment Mechanisms to Replace PRDs

Anthropic replaced the traditional PRD approval system with two mechanisms:

**Mechanism 1: Weekly All-Team Metrics Review**

| Element | Description |
|---------|-------------|
| Participants | Everyone — not just management and PMs |
| Frequency | Weekly, fixed time, under 30 minutes |
| Content | Core metric changes + drivers behind them |
| Purpose | Everyone can judge "does this matter?" without escalating |

**Mechanism 2: Team Principles Document**

| Element | Description |
|---------|-------------|
| Core users | Specific, not vague. "Independent designers 25-35" beats "creative professionals" |
| Why these users | Write the reasoning — prevents relitigating it later |
| Tradeoffs the team will make | When speed conflicts with completeness, which wins? |
| What we won't do | Explicit boundaries are more useful than fuzzy scope |

---

### Step 3 · Restructure Roles Around the Value Chain

**Anthropic's 5 PM types mapped to generic organizational roles:**

| Anthropic PM Type | Generic Role | Core Responsibility |
|------------------|-------------|---------------------|
| Research PM | **Signal Collector** | Customer feedback → core capability team |
| Platform PM | **Infrastructure Builder** | Internal tools and data platforms |
| Product PM | **Core Deliverer** | Primary product/service iteration |
| Enterprise PM | **Scale Enabler** | Reduce adoption friction, compliance |
| Growth PM | **Growth Driver** | Acquisition, retention, expansion |

**Role interface map (circular, not linear):**

| Role | Chain Node | Primary Output | Upstream From | Downstream To |
|------|-----------|---------------|---------------|--------------|
| Signal Collector | Customer signal | Structured insights, prioritized feedback | Customers | Core Deliverer |
| Infrastructure Builder | Supporting infrastructure | Internal tools, automation, data APIs | Core Deliverer | All roles |
| Core Deliverer | Product/service delivery | Usable product/service versions | Signal Collector, Infra Builder | Scale Enabler |
| Scale Enabler | Customer success | Onboarding, compliance, cost optimization | Core Deliverer | Growth Driver |
| Growth Driver | Scale growth | Growth data, acquisition, content | Scale Enabler | Signal Collector (closes the loop) |

---

### Step 4 · Define AI Capability Domains Per Role

**Four-Dimension AI Capability Model:**

| Capability | Definition | Signals | Who Needs It Most |
|-----------|-----------|---------|-------------------|
| **Skill Fluency** | Using AI tools to execute daily work | Can write reports, analyze data, generate content with AI | Everyone |
| **Agent Fluency** | Designing tasks, directing Agents, evaluating outputs | Can write clear task scope, evaluate Agent output quality, iterate prompts | Core Deliverer, Infra Builder |
| **Product Taste** | Judging "what's worth doing" | Knows which 3 of 100 requests to do first; sees what users actually need | Core Deliverer, Signal Collector |
| **First-Principles Thinking** | Re-deriving from scratch when old patterns fail | Can rapidly assess new tools; not trapped by "we've always done it this way" | Infra Builder, Growth Driver |

**Priority matrix by role:**

| Role | Skill Fluency | Agent Fluency | Product Taste | First-Principles |
|------|:------------:|:------------:|:------------:|:---------------:|
| Signal Collector | ★★★ | ★★ | ★★★ | ★★ |
| Infrastructure Builder | ★★★ | ★★★ | ★★ | ★★★ |
| Core Deliverer | ★★★ | ★★★ | ★★★ | ★★★ |
| Scale Enabler | ★★★ | ★★ | ★★ | ★★ |
| Growth Driver | ★★★ | ★★ | ★★ | ★★★ |

---

### Step 5 · Build a Three-Layer Tooling System

| Layer | Purpose | Typical Tools/Mechanisms | Build Priority |
|-------|---------|--------------------------|----------------|
| **Alignment Layer** | Replace PRDs; give everyone shared decision context | Shared dashboards, principles docs, metrics reviews | First |
| **Harness Layer** | Let Agents execute tasks reliably | Task template library, prompt standards, output acceptance criteria | Second |
| **Delivery Layer** | Make releases a routine action | Fixed release coordination channel, release checklist, version labeling | Third |

---

### Step 6 · Compress Delivery Cycles

**Standard 6-step release playbook:**

| Step | Content | Owner | Done When |
|------|---------|-------|-----------|
| 1. Internal acceptance | Core Deliverer confirms release criteria met | Core Deliverer | Checklist passed |
| 2. Internal trial | Relevant team uses it for 24-48h | All stakeholders | No blocking issues |
| 3. Release channel notification | Post to fixed release coordination channel | Core Deliverer | Notification sent |
| 4. Parallel follow-up | Docs, marketing, customer success update their materials | Each role, self-directed | Materials ready |
| 5. External release | Research preview or formal release | Growth Driver | Reached target users |
| 6. Feedback collection | Collect real feedback within 72h of release | Signal Collector | Feedback enters next iteration |

**Key principle**: Steps 1-2 are the Core Deliverer's job. Steps 3-6 are standard playbook — stakeholders pick it up themselves. This is what "alignment front-loaded" means: the alignment cost has already been paid down through weekly metrics reviews and the principles document.

---

## Common Failure Modes

| Failure Mode | What It Looks Like | Root Cause |
|-------------|-------------------|------------|
| Tools before process | Buying AI subscriptions before designing workflows | Mistaking capability for strategy |
| AI is one team's job | Only the "AI team" uses AI tools | Misunderstanding where the bottleneck is |
| Treating transformation as a tech project | Steps 1-3 delegated to engineers | Steps 1-3 are organizational design, not technology |
| Not compressing release | "Slow releases are normal for us" | Release process isn't standardized; each launch re-aligns from scratch |

---

> **One sentence**: The Anthropic model can't be copied directly, but its underlying logic can — **organize people around value flow, not around role boundaries**. That's where AI-native transformation starts. Everything else is execution.

---

## Appendix: What "Who Knows What to Write" Actually Means

In Cat Wu's original statement, "write" means exactly that — **write code**. Her point: AI can now write most code, so "knowing how to code" becomes less scarce. What becomes scarce instead is the judgment of "what should be written."

But "what should be written" isn't the same as vision, planning, or direction — those high-level words. It needs to be more precise.

To understand this concept, it helps to see AI as eating its way up a **capability stack**:

```
Vision / Values        (Why — not replaceable by AI today)
    ↓
Direction / Planning   (Where to go)
    ↓
Design / Goals         (What to build)
    ↓
Product Taste          (which 3 things right now ← current scarcity point)
    ↓
Specific Design        (UI, prototypes → AI is taking over)
    ↓
Execution / Code       (How → AI has largely taken over)
```

AI is eating from the bottom up. Code execution is largely consumed. Specific design (UI generation, prototyping) is being consumed now. **What AI still can't do is the middle layer — product taste: deciding which 3 things to do right now.**

This judgment resists replacement because it requires simultaneously holding three things:

1. **What users actually want** (not what they say — what they vote for with their behavior)
2. **How close this thing is to the goal** (value calibration)
3. **Whether doing it now vs. later makes a meaningful difference** (timing judgment)

Having vision alone makes you a strategist. Having execution alone makes you a tool. **The truly scarce person is the one who has both directional clarity AND can translate that direction into concrete daily judgment calls.** That's product taste — and it's the one dimension in the Step 4 capability matrix that AI cannot currently supply, because it requires real context, real user understanding, and accountability for the results of the choice.
