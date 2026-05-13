---
title: "从 Agent 课程谈起：Agent 是啥？"
titleEn: "Starting from Agent Courses: What Actually Is an Agent?"
description: "很多「Agent 开发」课程教出来的是工作流，不是 Agent。本文提炼 Skill 与 Agent 的核心定义：Skill 是能力原子（原生 Skill + 工具 Skill），Agent 的唯一标准是自主性——目标驱动、动态规划、感知反馈调整。附旅游 Agent 真伪对比、当前课程现象解析，以及 AI 时代 Agent 的四种未来形态。"
descriptionEn: "Most 'Agent development' courses teach workflows, not agents. This article distills the core definitions of Skill and Agent: Skill is the capability atom (native Skill + tool Skill); the only standard for Agent is autonomy — goal-driven, dynamic planning, perception-feedback adjustment. Includes travel agent authenticity comparison, analysis of the current course phenomenon, and four future forms of agents in the AI era."
pubDate: "2026-05-13"
updatedDate: "2026-05-13"
category: "Research"
tags: ["Agent", "Skill", "自主性", "工作流", "LLM", "AI时代", "多智能体", "认知自动化"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

**结论先行（BLUF）**：很多人学完「Agent 开发」课程后会发现——把"Agent"换成普通应用名，内容不会有任何变化。原因很简单：**那些课程教的是工作流，不是 Agent。** 而 Agent 与工作流之间唯一的、也是最本质的区别，是**自主性**。

---

## Skill：Agent 的能力原子

理解 Agent 之前，必须先理解 Skill。Skill 分两类：

**原生 Skill（模型内在能力）**：来自 LLM 自身的生成与理解能力，通过提示工程激活。例如文本摘要、情感分析（输出 positive / negative / neutral）、风格翻译（把技术文档改写成 8 岁孩子能懂的故事）。特点是非确定性、灵活，封装它的目的是让它变得可靠、可调用。

**工具 Skill（调用外部世界）**：通过函数调用执行确定性任务，是 Agent 的"手和脚"。例如：

```
search_web(query: str) -> List[SearchResult]
check_flights(origin, destination, date) -> List[FlightInfo]
send_email(to, subject, body) -> bool
```

工具 Skill 的智能不在于操作本身，而在于 **Agent 何时、何地、为何决定调用它**。

两类 Skill 统一打包为 Agent 可规划使用的"能力积木"。"查询宾馆"不是一个 Skill，它背后是调用"酒店 API 工具 Skill"的决策。

---

## Agent：自主性是唯一标准

**传统「旅游 Agent」应用（预编译的逻辑）**：

```
用户输入 → 调地点 API → 调酒店 API → 调交通 API → 硬编码拼结果 → 返回
```

这条路是死的。酒店 API 报错，程序崩溃或返回残缺计划——它不会自己想办法换一家平台查询。

**真正的 AI 旅游 Agent（自主推理循环）**：

用户说"带两个孩子去冷门海滩，预算 1.5 万，5 天"，Agent 自主拆解为多目标约束问题，随后：并行搜索候选地 → 分析结果提炼 3–5 个候选 → 针对每个候选并行查航班和酒店 → **发现某地航班严重超预算后主动反思、排除该地、重新搜索补充候选** → 综合所有数据生成含理由的比较方案。

**感知到预算约束被触发、主动切换策略** —— 这就是自主性。

| 特征 | 传统应用 / 工作流 | 真正的 AI Agent |
|---|---|---|
| 驱动力 | 流程驱动，if-else 逻辑树 | **目标驱动**，理解用户意图 |
| 路径 | 预定义、硬编码，像铁轨 | **动态生成、自主规划**，像在旷野开车 |
| 意外处理 | 脆弱，按预设路径报错或失败 | **感知阻碍后自主反思、切换工具** |
| 工具调用 | 被动执行，程序跑到这步就调 | **主动选择**，自己决定何时用什么工具 |
| 核心价值 | 高效执行已知的重复性任务 | 创造性解决未知的、复杂的开放性任务 |

---

## 对「Agent 培训课程」现象的解析

**当前大多数课程教的是 AI 增强的工作流**——把原来代码写死的逻辑，替换成 LLM 完成其中某个环节（如摘要、分类），但整个流程骨架是固定的。这解决了很多实际问题，但缺乏真正智能体的灵活性。很多课程教的是如何用 LangChain 等框架搭建这种"AI 工作流"，然后把它称为"Agent"。

**真正的自主 Agent 开发难度极高**：不可控性、对提示工程的极端敏感、循环中的错误累积、token 消耗巨大、安全和对齐问题——这不是十几章课程能交付的。能教出来的，必然是一个简化、可控、丧失自主性的"玩具"或"工作流"。

**定义正在被泛化稀释**：就像"云计算""大数据"一样，"Agent"正在成为营销热词。一个脚本都可以被称为"某某 Agent"，因为它"代理"你做了某事。

> **Skill 是手脚，Workflow 是固定流水线，Agent 是一个有脑子、会思考、能自己做决定的学徒。** 你期待的是那个学徒，而你看到的课程，大多是在教你怎么搭一条更智能的流水线。

---

## Agent 在 AI 时代的本质与未来

**本质：认知劳动的封装**。过去，软件封装的是"计算"；Agent 封装的是"决策、规划和执行"这整个认知过程。我们会像委派任务给人类下属一样委派给 Agent，只关注最终结果，中间的认知劳动被代理了。

**未来四种形态**：

- **个人超级助理**：运行在个人设备，融合日程、邮件、记忆、偏好，成为数字分身
- **专家 Agent 网络**：不会有万能 Agent，而是无数垂直专家 Agent 组成协作网络——个人助理 Agent 去和法律顾问 Agent、投资分析 Agent、医疗初筛 Agent 进行多智能体协商，共同完成任务
- **组织里的数字员工**：产品需求、架构、编码、测试 Agent 像人类团队一样自主协作、开会、争论，完成整个项目
- **人机协作新范式**：人类从"流程编排者"转变为"目标制定者和关键决策验收者"，领导一个混合的人类与智能体团队

那些速成的"Agent 开发课"带你看的是 Agent-like 的表象，而真正值得思考的，是 Agent 作为智能体而非工具的真正未来价值。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Most "Agent development" courses, if you swap "Agent" for any ordinary application name, would remain unchanged. The reason is simple: **those courses teach workflows, not agents.** The only essential difference between an agent and a workflow is **autonomy**.

---

## Skill: The Capability Atom

**Native Skills (model's intrinsic abilities)**: Activated from LLM's generative and understanding capabilities via prompt engineering. Examples: text summarization, sentiment analysis (returning positive/negative/neutral), style translation. Characteristics: non-deterministic, flexible. The goal of encapsulating them is to make them reliable and callable.

**Tool Skills (calling the external world)**: Execute deterministic tasks via function calls — the agent's "hands and feet." Examples: `search_web()`, `check_flights()`, `send_email()`. The intelligence isn't in the operation itself but in **when, where, and why the Agent decides to call it**.

Both types unified into "capability building blocks" the Agent can plan with.

---

## Agent: Autonomy Is the Only Standard

**Traditional "travel agent" application (pre-compiled logic)**:
`User input → call location API → call hotel API → call transport API → hardcode results → return`

Dead-end path. If the hotel API errors, the program crashes or returns an incomplete plan — it won't think to try another platform.

**True AI travel agent (autonomous reasoning loop)**:

User says "take two kids to an uncrowded beach, budget ¥15k, 5 days." Agent autonomously decomposes into a multi-constraint optimization problem, then: parallel searches for candidate destinations → analyzes results to extract 3–5 candidates → **discovers one destination's flights severely exceed budget, self-reflects, eliminates it, re-searches for replacements** → synthesizes all data into a comparative plan with reasoning.

**Perceiving the budget constraint was triggered and proactively switching strategy** — that's autonomy.

| Feature | Traditional App / Workflow | True AI Agent |
|---|---|---|
| Driver | Process-driven, if-else logic tree | **Goal-driven**, understands user intent |
| Path | Predefined, hardcoded, like rails | **Dynamically generated**, like off-road driving |
| Handling surprises | Fragile, errors or fails on preset path | **Self-reflects, switches tools** |
| Tool calling | Passive execution | **Active selection** |

---

## Analyzing the "Agent Course" Phenomenon

Most current courses teach **AI-enhanced workflows** — replacing hardcoded logic with LLM completing one step (summarization, classification), while the overall flow skeleton is fixed. True autonomous Agent development is extremely difficult: uncontrollability, error accumulation in loops, massive token consumption, safety and alignment challenges — none of which a dozen-chapter course can deliver.

**"Agent" is becoming a marketing buzzword** — any script can be called "SomeAgent" because it "acts on your behalf."

> **Skill is the hands and feet. Workflow is the fixed assembly line. Agent is an apprentice with a brain who thinks and makes its own decisions.** What you expected was that apprentice. What most courses teach is how to build a smarter assembly line.

---

## The Essence and Future of Agent in the AI Era

**Essence: encapsulation of cognitive labor.** Software used to encapsulate "computation"; Agent encapsulates the entire cognitive process of "decision, planning, and execution." We'll delegate to agents like delegating to human subordinates, caring only about outcomes.

**Four future forms**:
- **Personal super-assistant**: runs on personal devices, integrates calendar, memory, preferences — your digital twin
- **Expert agent networks**: no all-powerful agent; instead, countless vertical expert agents in a collaborative network, conducting multi-agent negotiation
- **Digital employees in organizations**: product, architecture, coding, testing agents autonomously collaborating like a human team
- **New human-AI paradigm**: humans shift from "process orchestrators" to "goal setters and decision validators," leading mixed human-agent teams

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
