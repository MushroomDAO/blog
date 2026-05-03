---
title: "Agent 是什么？从意图到自主：封装了决策、规划和执行的智能体"
titleEn: "What Is an Agent? From Intent to Autonomy: The Intelligence That Encapsulates Decision, Planning, and Execution"
description: "市面上大多数'Agent 课程'教出来的，其实是预设好流程的工作流，不是真正的 Agent。本文深入剖析 Skill 与 Agent 的本质区别：自主性才是 Agent 的灵魂，而不是把 if-else 逻辑接上 LLM 调用。"
descriptionEn: "Most 'Agent courses' on the market teach hardcoded workflows, not real agents. This post goes deep on the essential difference between Skill and Agent: autonomy is the soul of an agent — not if-else logic wired to an LLM call."
pubDate: "2026-05-03"
updatedDate: "2026-05-03"
category: "Research"
tags: ["Agent", "Skill", "AI原理", "自主性", "LLM", "工作流", "多智能体"]
heroImage: "../../assets/images/what-is-agent-skill-autonomy.jpg"
---

> **创作说明**：Jason（Mycelium Protocol 创始人）在观察大量市场上的"Agent 课程"后，对"Agent"这个概念产生了系统性质疑。本文由 Jason 与 AI（Claude）深度讨论后整理输出，问题和洞察来自 Jason，分析框架由 AI 按 Jason 意图整理。

**结论先行（BLUF）**：市面上九成"Agent 课程"教的不是 Agent，是**AI 增强的工作流**。真正的 Agent 核心是**自主性**——能理解目标、自主规划路径、感知环境反馈、动态调整行为。Skill 是手脚，Workflow 是固定流水线，Agent 是一个有脑子、会思考、能自己做决定的学徒。

---

## 一个让人不舒服的观察

看了很多 Agent 课程和教程之后，Jason 发现一件事：

**如果把课程里的"Agent"换成一个应用的名字，没有任何区别。**

比如所谓的"旅游 Agent"——本质还是前端 + 后端，根据设定好的逻辑，按顺序查询地点、宾馆、交通、预算，然后拼成一个旅游计划返回给用户。

这本身没有技术上的错误，但问题在于：**这是设定好的，不是自主的。** 一个真正的 Agent，最核心的能力应该是自主性，而不是把预设逻辑接上 LLM。

那些花了十几章来教"Agent 开发"的课程，交出来的其实不是 Agent。

这个观察是准确的，也指向了当前 AI 领域一个真实存在的问题。

---

## 第一部分：Skill——Agent 的手和脚

要理解 Agent，必须先理解 Skill。

**Skill 是将模型能力或工具功能，封装成标准化、可调用接口的单元。** 它是 Agent 能"做事"的基础。

### 两类 Skill

**原生 Skill（模型内在能力）**

来自大语言模型本身的生成和理解能力，通过提示工程激活：

- **文本摘要 Skill**：模型读一段长文，返回结构化摘要——不是你写了提取算法，是模型自己"理解"后总结的
- **情感分析 Skill**：输入一段评论，返回 `positive / negative / neutral` 标签
- **风格转换 Skill**：把技术文档"翻译"成 8 岁小孩能听懂的语言

这类 Skill 的特点：**非确定性、灵活**，封装它的目的是让模型能力变得可靠、可重复调用。

**工具 Skill（调用外部世界）**

通过函数调用执行具体、确定性的任务：

```python
search_web(query: str) -> List[SearchResult]
check_flights(origin: str, destination: str, date: str) -> List[FlightInfo]
calculate(expression: str) -> float  # LLM做复杂数学不可靠，所以需要这个
send_email(to: str, subject: str, body: str) -> bool
```

这类 Skill 的特点：**确定性、可验证**。它们的智能不在于操作本身，而在于 Agent 决定**何时、为何、用什么方式**调用它们。

### Skill 的核心意义

把模型的不确定性能力（理解、推理）和工具的确定性能力（查询、执行），统一封装成 Agent 可以"拿来用"的**能力积木**。

Skill 是手脚。Agent 才是做决定的脑子。

---

## 第二部分：Agent——真正的自主决策者

### 自主性是唯一标准

区分传统应用和 AI Agent 的标准只有一个：**自主性**。

一个真正的 AI Agent，能够独立理解目标、自主规划任务路径、灵活运用各种 Skill，并通过感知环境反馈动态调整行为，完成复杂目标。

它不是被预设流程驱动的软件，而是一个**目标导向的决策循环**。

### 对比：工作流 vs 真正的 Agent

用旅游规划来做对比，差异会很具体。

**传统"旅游 Agent"应用（预编译逻辑）**：
```
用户输入 → 第一步查地点 API → 第二步查酒店 API
→ 第三步查交通 API → 硬编码拼凑结果 → 返回
```
这条路是死的。如果酒店 API 报错，程序崩溃或返回残缺计划——它不会自己想办法换一家平台查。

**真正的 AI 旅游 Agent（自主推理循环）**：

假设用户说："我想带两个孩子去能避开人群、有绝美海滩、预算 1.5 万以内的地方，行程 5 天。"

真正的 Agent 会这样运转：

1. **目标拆解**：这是多约束组合问题——人群密度、海滩质量、预算、亲子友好度、时间。

2. **自主规划**：
   - 并行调用 `search_web("全球冷门亲子海滩")` 和 `search_web("东南亚高性价比海滩度假村")`
   - 分析结果，提炼 3-5 个候选地：丽贝岛、停泊岛、巴拉望…
   - 针对每个候选地，并行查询实时机票和酒店价格

3. **感知阻碍、动态调整**：某地机票超预算——Agent 自主反思："地点 A 排除，需要补充候选。"再次搜索，而不是报错崩溃。

4. **整合输出**：把所有成功获取的信息，通过"规划 Skill"生成完整五天方案，包含选择理由、每天预算分配、儿童注意事项。

5. **持续迭代**：用户说"能减少飞行时间吗？"Agent 重新进入循环，加入新约束，再次评估。

### 核心对比表

| 特征 | 传统应用 / 工作流 | 真正的 AI Agent |
|------|-----------------|----------------|
| **驱动力** | 流程驱动，if-else 逻辑树 | 目标驱动，理解用户意图 |
| **路径** | 预定义、硬编码，像铁轨 | 动态生成、自主规划，像在旷野开车 |
| **对意外的处理** | 脆弱，预设路径报错或失败 | 感知阻碍后，自主反思、切换工具或调整策略 |
| **工具调用** | 被动执行，跑到这步就必须调 | 主动选择，为达成目标自己决定何时用什么 |
| **核心价值** | 高效执行已知的重复性任务 | 创造性解决未知的、复杂的开放性任务 |

---

## 第三部分：为什么课程教出来的"不是 Agent"

Jason 的判断是对的。可以这样理解这个现状：

**"工作流 Agent"是市场过渡的产物。**

把原来代码写死的逻辑，替换成"用 LLM 完成其中一个环节"，但整个流程骨架是固定的——这是**AI 增强的工作流**，不是自主 Agent。很多课程教的是如何用 LangChain 等框架搭建这种"AI 工作流"，然后把它叫做 Agent。

**真正的 Agent 开发难度极高。**

真正的自主 Agent 还处于研究前沿和早期探索阶段：
- 不可控性高，提示工程极端敏感
- 决策循环中的错误会累积放大
- Token 消耗巨大
- 安全和对齐问题棘手

这不是十几章课程能教会"开发"出来的。能教出来的，必然是简化、可控、丧失自主性的版本。

**"Agent"这个词被稀释了。**

就像"云计算"、"大数据"一样，Agent 正在成为营销热词。一个脚本都可以被称为"某某 Agent"，因为它"代理"你做了某事。

---

## 第四部分：Agent 在 AI 时代的本质与未来

### 本质：认知劳动的分离与封装

软件发展史上，每次关键演进都是在封装更高层的能力：
- 算法封装了**计算**
- 应用封装了**功能**
- Agent 封装了**决策、规划和执行**这整个认知过程

我们会像委派任务给人类员工一样委派给 Agent："帮我策划一场市场活动。"只关注结果，中间的认知劳动被 Agent 代理了。

### 未来形态：多智能体社会

**个人超级助理**：深度个人化，运行在个人设备上，融合你的日程、邮件、记忆、偏好，成为你的数字分身。

**专家智能体网络**：不会有一个万能 Agent。未来是垂直领域专家 Agent 组成的网络。你的个人助理 Agent，会和"法律顾问 Agent"、"投资分析 Agent"、"医疗初筛 Agent"进行多智能体协商，共同完成任务。

**组织里的数字员工**：产品需求 Agent、架构 Agent、编码 Agent、测试 Agent 像人类团队一样自主协作、开会、争论，完成完整项目。

**人机协作新范式**：人类成为**目标制定者**和**关键决策验收者**，而不再是流程编排者。我们从使用软件工具，转变为**领导一个混合的人类与智能体团队**。

---

## 一句话区分三者

> **Skill 是手脚，Workflow 是固定流水线，Agent 是一个有脑子、会思考、能自己做决定的学徒。**

你期待的是那个学徒。大多数课程教的，是怎么搭一条更智能的流水线。

这两者之间的距离，不是技术上的，而是**设计哲学**上的。

---

## 常见问题

**Q: 现在市面上有没有真正的 Agent 产品？**  
A: 有，但大多处于早期阶段。比较接近真正 Agent 的方向包括：Anthropic 的 Claude 使用计算机（computer use）、OpenAI 的 Deep Research、以及一些自主编程 Agent（如 Devin 的早期概念）。它们都还不成熟，但代表了方向。大多数市面上号称 Agent 的产品，更准确的叫法是"AI 工作流"。

**Q: 学习 LangChain 等框架有没有价值？**  
A: 有，但要清楚自己在学什么。这些框架让你更方便地搭建 AI 工作流——这很有实用价值，能解决很多真实业务问题。只是不要误以为掌握了这些框架就掌握了"真正的 Agent 开发"。

**Q: 普通人什么时候能用上真正的 Agent？**  
A: 局部的自主 Agent 现在已经存在。完整意义上的"有记忆、能自主、跨任务持续学习"的个人 Agent，预计在未来 3-5 年内会有实质性突破。苹果的 Apple Intelligence、Google 的 Project Astra 都在这个方向上推进。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **About this article**: Jason (Mycelium Protocol founder) observed a systematic pattern in the market's "Agent courses" and developed a principled critique of how the term is being misused. This post is organized from a deep discussion between Jason and AI (Claude). Insights and observations are Jason's; the analytical framework is organized by AI per Jason's intent.

**BLUF**: Nine out of ten "Agent courses" on the market teach AI-enhanced workflows, not Agents. A real Agent's core is **autonomy** — understanding goals, self-planning execution paths, sensing environmental feedback, and dynamically adjusting behavior. Skill is the hands and feet. Workflow is a fixed assembly line. An Agent is an apprentice with a brain that thinks and decides on its own.

---

## An Uncomfortable Observation

After going through many Agent courses and tutorials, Jason noticed something:

**If you replace "Agent" with any regular app name, nothing changes.**

The so-called "Travel Agent" is still frontend + backend, following preset logic to query locations, hotels, transit, budget in sequence, then assemble and return a travel plan.

Nothing is technically wrong with that. But the problem is: **it's predetermined, not autonomous.** A real Agent's most essential capability should be autonomy — not just wiring if-else logic to an LLM call.

Those courses spending fifteen chapters on "Agent development" are producing something that isn't an Agent.

---

## Part 1: Skill — The Agent's Hands and Feet

To understand Agents, you have to understand Skills first.

**A Skill encapsulates a model's capability or a tool's function into a standardized, callable interface unit.** It's the foundation of what an Agent can "do."

### Two Types of Skills

**Native Skills (Model's Inherent Capabilities)**

Activated from the LLM itself through prompt engineering:

- **Summarization Skill**: Feed it a long text, get a structured summary — not a hand-written extraction algorithm, but the model genuinely "understanding" and condensing
- **Sentiment Analysis Skill**: Input a review, return `positive / negative / neutral`
- **Style Translation Skill**: Convert technical documentation into language an 8-year-old can follow

Key trait: **non-deterministic, flexible.** The purpose of wrapping them is reliability and repeatability.

**Tool Skills (Accessing the External World)**

Calling concrete, deterministic functions:

```python
search_web(query: str) -> List[SearchResult]
check_flights(origin: str, destination: str, date: str) -> List[FlightInfo]
calculate(expression: str) -> float  # LLMs aren't reliable at complex math
send_email(to: str, subject: str, body: str) -> bool
```

Key trait: **deterministic, verifiable.** Their intelligence isn't in the operation itself — it's in the Agent deciding *when, why, and how* to invoke them.

### The Core Point of Skills

Packaging the model's uncertain capabilities (understanding, reasoning) and tools' deterministic capabilities (querying, executing) into **capability building blocks** the Agent can reach for.

Skills are hands and feet. The Agent is the brain doing the deciding.

---

## Part 2: Agent — The True Autonomous Decision-Maker

### Autonomy Is the Only Standard

There is one criterion that distinguishes traditional applications from AI Agents: **autonomy.**

A real AI Agent independently understands goals, autonomously plans execution paths, flexibly deploys Skills, and dynamically adjusts behavior by sensing environmental feedback — to accomplish complex objectives.

It isn't software driven by a preset process. It's a **goal-directed decision loop.**

### The Comparison: Workflow vs. Real Agent

Travel planning makes the difference concrete.

**Traditional "Travel Agent" App (Pre-compiled logic):**
```
User input → Step 1: Query location API → Step 2: Query hotel API
→ Step 3: Query transit API → Hard-code result assembly → Return
```
This path is rigid. If the hotel API errors out, the program crashes or returns an incomplete plan. It won't figure out an alternative on its own.

**A Real AI Travel Agent (Autonomous Reasoning Loop):**

User: "I want to take two kids somewhere with stunning beaches that avoids crowds, budget under ¥15,000, 5 days."

A real Agent runs like this:

1. **Goal decomposition**: This is a multi-constraint optimization — crowd density, beach quality, budget, child-friendliness, duration.

2. **Autonomous planning**:
   - Parallel calls: `search_web("underrated child-friendly beaches worldwide")` and `search_web("Southeast Asia high-value beach resorts")`
   - Analyze results, distill 3-5 candidates: Koh Lipe, Perhentian Islands, Palawan...
   - Parallel-query real-time flights and hotels for each candidate

3. **Sense obstacles, adapt dynamically**: One destination's flights massively exceed budget — Agent self-reflects: "Candidate A eliminated. Need more options." Searches again rather than throwing an error.

4. **Integrate output**: Combine all successfully retrieved data through a "planning Skill" to generate a full five-day itinerary with reasoning, daily budget breakdown, and child-specific notes.

5. **Continuous iteration**: User says "can we reduce flight time?" Agent re-enters the loop, adds the new constraint, re-evaluates.

### The Core Comparison Table

| Feature | Traditional App / Workflow | Real AI Agent |
|---------|--------------------------|---------------|
| **Driving force** | Process-driven, if-else logic tree | Goal-driven, understands user intent |
| **Path** | Predefined, hardcoded — like train tracks | Dynamically generated, self-planned — like driving off-road |
| **Handling surprises** | Fragile; errors or fails along preset path | Senses obstacles; self-reflects, switches tools, adjusts strategy |
| **Tool invocation** | Passive execution — hits this step, must call it | Active selection — decides when and what tool based on the goal |
| **Core value** | Efficiently executing *known* repetitive tasks | Creatively solving *unknown*, complex, open-ended tasks |

---

## Part 3: Why Courses Produce "Not Quite Agents"

**"Workflow Agents" are a market transition artifact.**

Replacing hard-coded logic with "use an LLM for one step" while keeping the overall skeleton fixed is **AI-enhanced workflow**, not autonomous Agent. Many courses teach how to use LangChain and similar frameworks to build this pattern — then call it "Agent development."

**Real Agent development is extremely hard.**

Truly autonomous Agents are still in research and early exploration:
- High unpredictability, extreme sensitivity to prompt engineering
- Errors in the decision loop compound and amplify
- Massive token consumption
- Safety and alignment challenges remain unsolved

This can't be taught in fifteen chapters. What can be taught in fifteen chapters is necessarily simplified, controlled, and stripped of real autonomy.

**"Agent" is being diluted as a term.** Like "cloud computing" and "big data," it's becoming a marketing buzzword. Any script can be called "SomeX Agent" because it "acts on your behalf."

---

## Part 4: The Nature and Future of Agents in the AI Era

### Essence: The Encapsulation of Cognitive Labor

Every key inflection in software history encapsulated a higher-level capability:
- Algorithms encapsulated **computation**
- Applications encapsulated **function**
- Agents encapsulate the entire cognitive process: **decision, planning, and execution**

We'll delegate to Agents the way we delegate to human colleagues: "Plan a product launch." Only care about the outcome. The cognitive labor in between is proxied by the Agent.

### Future Forms: A Multi-Agent Society

**Personal superintelligent assistant**: Deeply personal, running on your device, integrated with your calendar, email, memory, preferences — your digital twin.

**Expert agent network**: There won't be one omniscient Agent. The future is a network of vertical specialist Agents. Your personal assistant Agent negotiates with "legal advisor Agent," "investment analysis Agent," "medical triage Agent" to complete tasks collaboratively.

**Digital employees inside organizations**: Product requirement Agent, architecture Agent, coding Agent, testing Agent collaborating autonomously like a human team — holding meetings, debating, shipping projects.

**New human-machine collaboration paradigm**: Humans become **goal setters** and **final decision validators**, no longer process orchestrators. We shift from using software tools to **leading a mixed team of humans and agents**.

---

## One Line to Distinguish All Three

> **Skill is hands and feet. Workflow is a fixed assembly line. Agent is an apprentice with a brain that thinks and decides on its own.**

What you're looking for is that apprentice. Most courses teach you how to build a smarter assembly line.

The distance between those two things isn't technical — it's a gap in **design philosophy.**

---

## FAQ

**Q: Are there real Agent products available today?**  
A: Yes, but most are early-stage. The closest to true Agents include Anthropic's Claude computer use, OpenAI's Deep Research, and early autonomous coding agents (like early Devin). None are fully mature, but they represent the direction. Most products on the market calling themselves Agents are more accurately called "AI workflows."

**Q: Is learning LangChain and similar frameworks worthwhile?**  
A: Yes — but be clear about what you're learning. These frameworks make it easier to build AI workflows, which has genuine practical value and solves real business problems. Just don't mistake mastering these frameworks for mastering "real Agent development."

**Q: When will regular people have access to truly autonomous Agents?**  
A: Partial autonomous Agents exist now. For fully realized "persistent memory, autonomous, continuously learning across tasks" personal Agents, expect meaningful breakthroughs within 3–5 years. Apple Intelligence and Google Project Astra are both pushing in this direction.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
