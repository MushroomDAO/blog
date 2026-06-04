---
title: "SkillPyramid：给 Agent 搭技能树，比 ReAct 多 38% 奖励少 28% 步骤"
titleEn: "SkillPyramid: Hierarchical Skill Trees for Self-Evolving Agents — 38% More Reward, 28% Fewer Steps"
description: "中科院自动化所、国科大、上海人工智能实验室和北京智源研究院联合提出 SkillPyramid：将 Agent 的任务经验整理成三层技能金字塔（原子 → 功能 → 抽象），在 ALFWorld/WebShop/ScienceWorld 上平均奖励提升 38%，交互步骤减少 27.7%。"
descriptionEn: "Chinese Academy of Sciences, UCAS, Shanghai AI Lab, and BAAI propose SkillPyramid: organizing agent task experience into a three-layer skill hierarchy (atomic → functional → abstract), achieving 38% average reward improvement and 27.7% fewer interaction steps on ALFWorld/WebShop/ScienceWorld."
pubDate: 2026-06-04
category: "Research"
tags: ["Agent", "技能系统", "中科院", "智源研究院", "强化学习", "LLM Agent", "自进化", "论文"]
heroImage: "../../assets/images/skillpyramid-agent-skill-tree-banner.jpg"
lang: "zh-CN"
---

## 问题：Agent 每次都在重新发明轮子

想象一个在家庭环境中操作的 Agent：学会"把杯子从桌上拿到洗碗池"之后，下次面对"把苹果从冰箱拿到餐桌"，它又从头摸索——尽管"打开容器"、"抓取物体"、"移动到目标位置"这些基本操作早已被隐含地使用过。

现有的 Agent 技能框架（Voyager、ExpeL、SkillX 等）有一个共同缺陷：**只会堆积技能，不会整理技能**。每次任务产生的经验被保存为独立 skill，随着时间推移形成一个无结构的技能池。新任务来临时，Agent 从池子里捞一把，能用则用，不能用就从头写——没有抽象，没有复用，没有进化。

来自**中国科学院自动化研究所、国科大、上海人工智能实验室和北京智源人工智能研究院**的研究团队提出了 **SkillPyramid**，核心思路是：**与其让 Agent 堆经验，不如让它整理经验**。

> 论文：**SkillPyramid: A Hierarchical Skill Consolidation Framework for Self-Evolving Agents**
> arXiv：[arxiv.org/abs/2606.03692](https://arxiv.org/abs/2606.03692)
> 作者：Yuan Xiong, Ziqi Miao, Qian Chen, Lijun Li, Yequan Wang, Shizhu He, Jun Zhao, Kang Liu

---

## SkillPyramid 的核心架构

SkillPyramid 把 Agent 积累的技能组织成**三层金字塔**：

```
         ┌─────────────────────────┐
         │   Abstract Skills（抽象层）│   高层解题模式 / 跨任务策略
         └────────────┬────────────┘
                      │ 组合
         ┌────────────▼────────────┐
         │   Functional Skills（功能层）│   任务级技能（如"做一杯咖啡"）
         └────────────┬────────────┘
                      │ 调用
         ┌────────────▼────────────┐
         │   Atomic Skills（原子层）  │   最小可复用操作（如"开门"/"抓取"）
         └─────────────────────────┘
```

**原子层（Atomic）**：跨多个任务共享的最小操作单元。不可再分，被功能层 skill 显式引用。

**功能层（Functional）**：任务级技能，由原子 skill 组合而成，处理一个具体的任务类型。

**抽象层（Abstract）**：从多个功能 skill 中归纳出来的高层解题模式，指导新任务的 skill 生成。

---

## 四个核心组件

### 1. Relation Analyzer（关系分析器）

两阶段分析现有技能之间的关系：
- **粗粒度**：用 skill 名称和描述进行粗分组
- **细粒度**：对组内 skill 做精细分析，生成"关系构建指令"

### 2. Relation Builder（关系构建器）

执行两个方向的操作：

**向下原子抽取（Downward Atomic Extraction）**：
从多个 skill 中提取共享的最小操作，然后重写源 skill，让它们通过显式引用调用这些原子组件。原来冗余的"开门"逻辑不再散落在 50 个 skill 里，而是集中在一个原子 skill 中。

**向上抽象归纳（Upward Abstract Induction）**：
将若干功能 skill 共享的高层解题模式归纳为抽象父 skill，形成树状继承结构。

### 3. Skill Creator（技能生成器）

新任务到来时，不再从头生成 skill，而是：
1. 从金字塔中检索相关的原子 skill 和抽象 skill
2. 以抽象 skill 为战略指引
3. 以原子 skill 为具体操作积木
4. 组合生成新的功能 skill

这让新 skill 天然具备可复用性，因为它的组件就是整个系统已经测试过的原子单元。

### 4. Self-Evolution 机制

每次生成新 skill 后，系统不需要从头重建整个金字塔，而是**增量吸收**：
- 对新 skill 分析它与现有原子 skill 的关系
- 维护并更新依赖关系图
- 在不破坏现有结构的前提下扩展金字塔

---

## 实验结果

### 测试环境与 Backbone 模型

- **环境**：ALFWorld（家庭任务）、WebShop（电商购物）、ScienceWorld（科学实验）
- **Backbone**：DeepSeek-V3.2、GPT-4.1、Gemini 2.5 Pro、Qwen3-235B（四种主流模型全覆盖）

### 主要对比结果

| 方法 | 平均奖励 | 说明 |
|------|---------|------|
| ReAct | 53.4 | 基础 Agent 范式 |
| Reflexion | 59.6 | 加反思机制 |
| ExpeL | 61.3 | 经验积累 |
| ReAct + Skills（平铺） | 65.8 | 有技能库但无层级 |
| **SkillPyramid** | **73.7** | 层级化技能金字塔 |

- **平均奖励提升 38.0%**（对比基线方法）
- **交互步骤减少 27.7%**（更少步骤完成相同任务）

### ALFWorld 细节（DeepSeek-V3.2 backbone）

| 任务类型 | ReAct+Skills | SkillPyramid | 说明 |
|---------|-------------|-------------|------|
| 未见任务奖励 | 73.9 | **84.8** | +10.9 |
| 未见任务步骤 | 14.7 步 | **10.6 步** | -27.9% |

### GAIA-Lite（噪声网络技能测试）

从 150K 个候选中过滤出 2,271 个网络挖掘技能，测试层级整合对噪声 skill 的鲁棒性：

| 组织方式 | 准确率 | 平均步骤 |
|---------|--------|---------|
| 平铺技能库 | 56.0% | 5.9 步 |
| **SkillPyramid** | **62.7%** | **4.8 步** |

即使面对从互联网批量挖掘的嘈杂技能，层级整合依然带来显著提升。

### 消融实验

| 变体 | 奖励 | 关键发现 |
|-----|------|---------|
| 完整 SkillPyramid | 73.7 | baseline |
| 去掉原子 skill | 67.2–71.7 | -2 到 -6.5，影响原子密集型任务 |
| 去掉抽象 skill | ~65.7 | -8，对多步组合任务影响最大 |
| 去掉自进化 | 显著下降 | 无法适应新任务分布 |
| 从头生成 skill | 64.3 | 比平铺技能库更差，证明层级结构的价值 |

---

## 分析与见解

### 1. 这篇论文在解决什么本质问题

Agent 的能力积累方式长期有一个隐含假设：**"更多经验 = 更强能力"**。但实际上，无结构的经验堆积只是在增加"检索噪声"——技能库越大，找到合适 skill 的概率反而可能下降，生成新 skill 时的参考也更混乱。

SkillPyramid 提出的是另一条路：**"更有结构的经验 = 更强能力"**。用原子抽取把通用操作下沉到底层，用抽象归纳把解题模式上升到顶层，两个方向同时压缩冗余、提炼规律。

这和人类学习技能的方式非常接近：一个有经验的厨师不是记住了 1000 道菜的具体做法，而是掌握了"火候控制"、"调味原则"、"食材组合逻辑"等底层技能，加上"中餐炒法"、"西餐烤法"等风格模板。

### 2. 与 Voyager 的本质区别

Minecraft 里的 Voyager 也在积累技能，但它的技能库本质上是平铺的 JavaScript 函数列表——找到了就用，找不到就写新的。SkillPyramid 的层级结构让每个新 skill 都可以"站在巨人肩上"：不是重复实现"开门"，而是调用原子层已有的 `open_door()` 组件。

### 3. GAIA-Lite 测试的意义

从 150K 技能中过滤 2,271 个，这个测试场景模拟了真实世界的"互联网规模技能挖掘"——数量巨大、质量参差。在这种噪声条件下，层级整合依然从 56% 提升到 62.7%，说明 SkillPyramid 的结构不仅帮助生成新技能，也帮助鉴别和组织外部技能。

### 4. 局限性与待解问题

**层级构建成本**：Relation Analyzer + Relation Builder 每次需要对现有技能库做分析，这在技能量大时可能带来显著的计算开销。论文没有充分讨论金字塔规模增长时的时间复杂度。

**层级边界的模糊性**：什么算"原子"、什么算"功能"，取决于任务粒度。在不同领域（家庭任务 vs. 代码生成 vs. 网页操作）这个边界会有很大差异，通用性有待验证。

**测试环境局限**：ALFWorld/WebShop/ScienceWorld 是相对结构化的环境。在更开放的现实世界任务（如开放式代码开发、长篇文章写作）中，技能可复用性是否依然成立，需要更多实验。

### 5. 对 AI Agent 工程实践的启示

SkillPyramid 的思路对工程实践有直接价值：当我们为 Agent 构建 skill library 时，不应该只考虑"加什么技能"，还应该考虑"如何组织技能"。

具体来说：
- 识别跨任务的原子操作，提取为独立的底层 skill
- 为同类任务归纳出解题模式，作为新 skill 生成的模板
- 建立 skill 之间的显式依赖关系，而不是让每个 skill 都是孤立的黑盒

这与当前流行的 Agent Skills 标准（如 Claude Code 的 SKILL.md、Open Design 的技能层）有很好的契合点——层级化组织可以作为这些标准的一个扩展维度。

---

**论文信息：**
- arXiv：[arxiv.org/abs/2606.03692](https://arxiv.org/abs/2606.03692)
- 机构：中国科学院自动化研究所、国科大、上海人工智能实验室、北京智源人工智能研究院
- 作者：Yuan Xiong, Ziqi Miao, Qian Chen, Lijun Li, Yequan Wang, Shizhu He, Jun Zhao, Kang Liu

<!--EN-->

## The Problem: Agents That Keep Reinventing the Wheel

Imagine an agent operating in a household environment. After learning to "move a cup from the table to the sink," the next task — "move an apple from the fridge to the dining table" — requires it to start over from scratch, even though the underlying operations (open a container, grasp an object, navigate to a target) were already implicitly used.

Existing agent skill frameworks — Voyager, ExpeL, SkillX — share a common flaw: **they accumulate skills but don't organize them**. Each task generates a new skill entry; the skill pool grows flat. When a new task arrives, the agent retrieves whatever seems closest and, when nothing fits, generates from scratch. No abstraction, no reuse, no evolution.

A joint team from the **Institute of Automation at the Chinese Academy of Sciences, UCAS, Shanghai AI Lab, and BAAI (Beijing Academy of Artificial Intelligence)** proposes **SkillPyramid**: rather than having agents pile up experience, make them *organize* it.

> **Paper:** SkillPyramid: A Hierarchical Skill Consolidation Framework for Self-Evolving Agents
> **arXiv:** [arxiv.org/abs/2606.03692](https://arxiv.org/abs/2606.03692)
> **Authors:** Yuan Xiong, Ziqi Miao, Qian Chen, Lijun Li, Yequan Wang, Shizhu He, Jun Zhao, Kang Liu

## The Three-Layer Skill Pyramid

SkillPyramid organizes agent skills into a three-level hierarchy:

```
         ┌──────────────────────────┐
         │   Abstract Skills        │   High-level solving patterns / cross-task strategies
         └────────────┬─────────────┘
                      │ compose
         ┌────────────▼─────────────┐
         │   Functional Skills      │   Task-level skills ("make coffee", "book a flight")
         └────────────┬─────────────┘
                      │ invoke
         ┌────────────▼─────────────┐
         │   Atomic Skills          │   Minimal reusable operations ("open door", "grasp")
         └──────────────────────────┘
```

**Atomic Layer**: Minimal operations shared across multiple tasks. Explicitly referenced by functional skills.

**Functional Layer**: Task-level skills composed of atomic skills.

**Abstract Layer**: High-level patterns induced from multiple functional skills, guiding new skill generation.

## Four Core Components

**Relation Analyzer**: Two-stage analysis of existing skill relationships — coarse grouping by name/description, then fine-grained analysis generating relation-construction assignments.

**Relation Builder**: Two-directional operations:
- *Downward Atomic Extraction*: Extract shared minimal operations, rewrite source skills to reference them explicitly (consolidating redundant "open door" logic from 50 skills into one atomic component)
- *Upward Abstract Induction*: Summarize shared high-level patterns into abstract parent skills

**Skill Creator**: For new tasks, instead of generating from scratch, retrieves relevant atomic and abstract skills from the pyramid, uses abstract skills as strategic guidance and atomic skills as concrete building blocks, then composes a new functional skill.

**Self-Evolution Mechanism**: Incrementally absorbs new skills without full pyramid reconstruction — analyzes new skills' relationships with existing atomics, maintains dependency graphs, and extends the pyramid non-destructively.

## Experimental Results

Tested on ALFWorld (household), WebShop (e-commerce), and ScienceWorld (scientific experiments), with four backbone models: DeepSeek-V3.2, GPT-4.1, Gemini 2.5 Pro, Qwen3-235B.

| Method | Average Reward |
|--------|---------------|
| ReAct | 53.4 |
| Reflexion | 59.6 |
| ExpeL | 61.3 |
| ReAct + Skills (flat) | 65.8 |
| **SkillPyramid** | **73.7** |

- **38.0% average reward improvement** over baselines
- **27.7% fewer interaction steps**
- Unseen task reward: **84.8** vs 73.9 for flat ReAct+Skills

**Web-mined skills (GAIA-Lite):** 2,271 skills filtered from 150K noisy candidates. SkillPyramid achieves **62.7%** accuracy in **4.8 steps** vs. 56.0% accuracy in 5.9 steps for flat organization.

## Key Insights

**The real innovation is structural, not additive.** The hidden assumption in most agent skill research is "more experience = more capability." SkillPyramid challenges this: *more structured experience = more capability*. Atomic extraction compresses redundancy downward; abstract induction compresses it upward. Both directions simultaneously reduce noise and distill patterns.

This mirrors how human experts actually learn. An experienced chef doesn't memorize 1,000 specific recipes — they master heat control, seasoning principles, and ingredient combinations (atomic skills), plus style templates like Chinese stir-frying or French roasting (abstract skills).

**The GAIA-Lite test is the most practically significant result.** Real-world skill libraries will come from noisy internet-scale sources, not curated lab data. The fact that hierarchical consolidation improves even noisy web-mined skills suggests SkillPyramid's structure helps not just generate new skills but also *curate* external ones.

**Open questions for future work:** Computational cost as pyramid scales; domain-specific definitions of "atomic" (grain size varies across coding, web navigation, and household tasks); validation on open-ended real-world tasks beyond structured benchmarks.

**Practical implication for Agent engineering:** When building skill libraries, don't only ask "what skills to add" — ask "how to organize the skills you already have." Identify cross-task atomic operations, extract them to a bottom layer, induce solving patterns across task families, and establish explicit dependency relationships between skills rather than treating each as an isolated black box.

---

**Paper:**
- arXiv: [arxiv.org/abs/2606.03692](https://arxiv.org/abs/2606.03692)
- Affiliations: Institute of Automation CAS, UCAS, Shanghai AI Lab, BAAI
- Authors: Yuan Xiong, Ziqi Miao, Qian Chen, Lijun Li, Yequan Wang, Shizhu He, Jun Zhao, Kang Liu
