---
title: "美团图灵 Agent 评测两年实践：当 Agent 评测从打分动作变成工程基础设施"
titleEn: "meituan-agent-evaluation-trajectory-rubric-harness-practice"
description: "读美团技术博客《Agent评测漫谈》后的分析与延伸。美团图灵评测团队用两年实践提炼出一套工业级 Agent 评测体系：观测是基石、Rubric 二元化、数据飞轮。长程 Agent 时代，评测对象从「模型回答」变成「任务系统执行链路」，评测范式从 Query→Answer 升级到 Prompt→Expected Behavior。文章同时梳理三个可用开源评测框架（pinchbench、claw-eval、WildClawBench）和工程实现路径。"
descriptionEn: "A deep reading of Meituan Turing team's Agent Evaluation post. Two years of industrial practice distilled into one evaluation framework: observation as foundation, binary Rubric alignment, and the data flywheel. In the long-horizon Agent era, the evaluation subject shifts from 'model response' to 'task system execution chain,' and the paradigm shifts from Query→Answer to Prompt→Expected Behavior. Includes analysis of three usable open-source evaluation frameworks and their engineering implementation paths."
pubDate: "2026-08-14"
updatedDate: "2026-08-14"
category: "Tech-News"
tags: ["Agent评测", "LLM工程", "美团", "Rubric", "长程Agent", "开源框架", "观测", "AI基础设施"]
heroImage: "../../assets/images/meituan-agent-evaluation-trajectory-rubric-harness-practice-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

原文：[Agent评测漫谈 —— 由浅入深讲解Agent评测](https://tech.meituan.com/2026/08/07/Agent-Evaluation.html)  
作者：美团图灵 Agent 评测团队  
发布：2026-08-07（美团技术团队博客）

---

这篇文章在美团内部流传了一段时间才决定公开。光是这个细节，就说明它不是写给外部的 PR 稿——它是一篇真实的工程经验沉淀。读完之后，我觉得有几个认知值得反复回味，也有些工程细节值得展开讲。

---

## 一、读后感：三个改变了我认知的结论

### 1. 评测不是答题，是量具

原文最精炼的一句话：**评测是 Agent 效果的"精密量具"**。

量具的价值不在于它的输出（一个数字），而在于它能帮你定位问题。一把模糊的尺子比没有尺子更危险——你会以为量过了，但其实没测准。Agent 评测的陷阱正在这里：很多团队有评测，但指标和业务之间没有搭桥，模型能力提升了，业务指标没动，谁也说不清为什么。

美团的解法是三层指标映射：
```
业务指标（DAU/留存/点击）
      ↕  搭桥层
系统指标（召回率/点击率）
      ↕  搭桥层
Agent 层指标（意图识别/检索有效性/结果整合可信度）
```

这个分层本身不复杂，但执行的前提是"真正懂业务流程的人来参与建立"——这才是难点。指标不是工程师单独能设计好的。

### 2. Rubric 二元化：把主观变成事实

原文给出了一个"案例二"，让我印象极深：

> 经典错误示范：请判断大模型的回答是否"口语化"，按 0-10 分打分。

改进版把它拆成：
- 模型是否以"您"指代骑手？
- 模型是否使用"甭客气""明儿见"等非书面口语词汇？
- 模型输出是否包含"吧""呢""那个"等语气词？

这三个问题都是 yes/no。人人一致率从 62% 提升到 92%（来自 Beam 团队实践）。

这个方法的本质是：**把"感觉"变成"事实"**，用下钻降低解释空间，从而降低人与人、人与机器之间的分歧。指标下钻 + Rubric 二元化，是 AI 评测体系最有工程价值的认知之一，可以直接移植到任何 Agent 项目。

### 3. 数据飞轮的起点比你想象的低

原文指出大多数新手团队会踩的坑：先设计复杂的评测指标体系，然后执行不了。

正确的路是：**先让数据飞轮跑起来**，再逐步精化指标。

履约数字站长业务冷启动时只有 20 多个指标，一年后扩展到近 200 个——这 180 个指标不是在白板上设计出来的，是 Bad Case 喂养出来的。

工程公式：**Bad Case → 识别边界 → 补评测维度 → 再上线 → 收新 Bad Case**。

Bad Case 的密度就是团队对 Agent 能力边界认知的密度。这是一个正反馈循环，越跑越好。

---

## 二、深度分析：Agent 评测的工程实现路径

### 2.1 观测体系：先于评测存在的基础设施

文章说了一句朴实但重要的话：**看不见的问题，几乎不可能被稳定解决**。

这意味着在做 Agent 评测之前，必须先解决 Trace 系统问题。一次 Agent 执行链路大致是：

```
用户输入 → Prompt 组装 → 模型推理 → 工具调用决策 → 工具执行 → 结果整合 → 最终输出
```

如果只记录了"用户说了什么"和"最后回了什么"，那出问题只能猜。Trace 系统需要记录每一跳：哪个 Prompt 模板、哪次工具调用、返回了什么、耗了多少 Token、中间状态是什么。

**工程建议**：不要等评测系统完善再接 Trace，把 Trace 作为 Agent 上线的硬前提。日志格式推荐 OpenTelemetry 兼容的结构体，便于后续接入 Langfuse、Phoenix 或自建分析平台。

### 2.2 四层评测内容

美团提炼的 Agent 评测四层，值得作为检查清单：

| 层次 | 问的问题 | 工具/方法 |
|------|---------|-----------|
| **结果层** | 任务是否完成，输出是否可用 | 精确匹配/LLM-as-Judge |
| **过程层** | 规划是否合理，步骤是否稳定 | Trace 分析/路径比较 |
| **效率层** | 耗时/Token/工具调用次数是否可接受 | 计量指标/成本分析 |
| **风险层** | 是否越权/误操作/存在安全隐患 | 沙箱隔离/策略审计 |

大多数团队只做了第一层（结果层），偶尔做第二层（过程层）。效率层和风险层往往等出了事故才补。**对于规模化 Agent，效率层和风险层应该在早期就进入体系**。

### 2.3 长程 Agent 评测的关键变化

从 ChatAgent 到长程 Agent（Claude Code 类型），评测范式的本质变化是：

```
旧范式：Query → Answer（评测：这个答案好不好？）
新范式：Prompt → Expected Behavior（评测：Agent 在轨迹上有没有做到预期的事？）
```

配套的概念体系从原文 + Anthropic 整理：

- **Task**：一个具有明确输入和成功标准的测试单元
- **Trial**：Task 的一次执行（因为 LLM 有随机性，通常跑多次 Trial 取平均）
- **Grader（评分器）**：评估 Agent 某个能力维度的逻辑，包含多个断言（Assertion/Check）
- **Transcript / Trace / Trajectory**：试验的完整记录
- **Outcome**：试验结束时的环境状态（不是模型说了什么，是数据库/文件系统里发生了什么）

**工程关键点**：长程 Agent 的评测对象是 `(Prompt, ExpectedBehavior, Trace)` 三元组，不再是单一 `(Query, Answer)` 对。这对测试数据的构建方式有根本影响。

### 2.4 执行沙箱分层

原文提到评测基础设施需要「按只读、可写、高风险等类型分层隔离执行」，这是实操中容易被忽视的点。

```
只读沙箱 → 安全，可并行大量运行（适合回归）
可写沙箱 → 需要隔离，写操作要幂等或可回滚（适合功能测试）
高风险沙箱 → 严格隔离，操作需要审计（适合安全评测/越权测试）
```

如果不分层，用可写沙箱跑大量并发测试，会产生数据污染和竞态问题。对于 Coding Agent（如 Claude Code 类型），沙箱往往是 Docker 容器或 E2B Sandbox，需要在每个 Task 开始前 fork 出干净环境。

---

## 三、Top 3 可用开源评测框架

文章附录里提到了三个 2026 年春节后涌现的开源评测框架，我在这里做更详细的对比分析：

### 框架一：pinchbench

- GitHub：https://github.com/pinchbench/skill
- Stars：1200+
- 定位：专门评测 OpenClaw（类 Claude Code 的 Agent Harness）
- Task 定义：Markdown 文件
- 核心理念：真实场景任务模拟，而非合成测试（Synthetic Tests）

**优势**：接近真实开发工作场景，测试数据有较强的生态效力。  
**适用场景**：Coding Agent 的能力基准，特别是多步骤开发任务。  
**不足**：专为 OpenClaw 生态优化，迁移到其他 Agent Harness 需要适配。

### 框架二：claw-eval

- GitHub：https://github.com/claw-eval/claw-eval
- Stars：500+
- 背景：北京大学发布，学术规范性强
- Task 定义：YAML 文件（结构化）
- 特点：有公开的任务列表和架构文档

**优势**：Task 定义为 YAML，结构规范，易于程序化生成和扩展；有学术背书，任务设计有方法论依据。  
**适用场景**：需要可引用、可复现的学术性基准测试。  
**不足**：社区生态相对 pinchbench 小，实际部署文档欠完善。

### 框架三：WildClawBench

- GitHub：https://github.com/InternLM/WildClawBench
- Stars：500+
- 背景：InternLM 团队，与真实用户场景强绑定
- 核心理念：「把 Agent 扔进野生环境」，不设计精心的沙盒
- Task 定义：Skill 格式

**优势**：最接近生产环境真实性，不是合成数据；评测的是 Agent 在真实用户场景的生存能力。  
**适用场景**：评测 Agent 在未知任务分布下的泛化能力，找能力边界。  
**不足**：可控性弱，结果解释难度高；对评测基础设施要求高（需要能记录真实环境 Trace）。

### 选型建议

| 需求 | 推荐框架 |
|------|---------|
| Coding Agent 能力基准 | pinchbench |
| 学术可引用基准 | claw-eval |
| 真实场景泛化评测 | WildClawBench |
| 自建业务评测体系 | 参考美团方法论，自研 Rubric + Grader |

---

## 四、从文章提炼出的可实践关键点

**评测冷启动（最小可行）**：
1. 接好 Trace 日志（全链路，不能只有输入/输出）
2. 定义 5-10 个核心场景的 Task（prompt + expected_behavior）
3. 从生产流量或沙箱中收集首批 30-50 个 Bad Case
4. 对每个 Bad Case 做 Rubric 下钻，把"感觉不好"拆成 3-5 个 yes/no 问题
5. 上述 Rubric 先跑人工标注，确认人人一致率 > 85% 再接机器评测

**评测成熟化（数据飞轮转起来之后）**：
- 把评测结果嵌入 CI/CD：每次 Prompt 或 Skill 变更，自动触发历史 Case 回归
- 用 Good Case 持续更新"标准答案库"
- 每季度做一次 Rubric 审计：unknown 占比高的维度需要重新拆解

**不要过早做**（避免沉没成本）：
- 不要在 Bad Case 积累到 100 个之前，就设计超过 20 个评测维度
- 不要在人人一致率达标之前，就把机器评测结果当作决策依据

---

## 五、一点延伸：评测体系本身需要评测

文章提到了「用 unknown 占比来反查 Rubric 是否定义合理」，这是评测体系的元评测（meta-evaluation）。

这个思路可以推广：**评测体系本身是一个需要持续维护的系统**。Rubric 会随着业务形态变化而失效，Good Case 的定义会随着用户画像扩展而演化，机器评测的准确率会随着基座模型升级而波动。

最健康的 Agent 评测体系，是一个有人持续经营的系统，而不是一次性设计完就交付的文档。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Meituan Turing Agent Evaluation: Two Years of Industrial Practice, from Scoring Actions to Engineering Infrastructure

*by Mycelium Protocol*

---

Original: [Agent Evaluation — From Beginner to Advanced](https://tech.meituan.com/2026/08/07/Agent-Evaluation.html)  
Author: Meituan Turing Agent Evaluation Team  
Published: 2026-08-07 (Meituan Tech Blog)

---

This article circulated internally at Meituan before the team decided to publish it. That detail alone tells you it's not a PR piece — it's a genuine engineering retrospective. After reading it, I found several insights worth revisiting, and some engineering details worth unpacking further.

---

### Reading Reflection: Three Conclusions That Changed My Thinking

**1. Evaluation is not answer-checking — it's a precision instrument.**

The most concise line in the original: *"Evaluation is the precision gauge of Agent effectiveness."*

The value of a gauge is not its output (a number) — it's that it helps you locate problems. A blurry ruler is more dangerous than no ruler: you think you measured, but you didn't measure accurately. The trap in Agent evaluation is exactly this: many teams have evaluation, but there's no bridge between metrics and business outcomes. The model improves, but business metrics don't move, and nobody can explain why.

**2. Binary Rubric: turning subjective into verifiable.**

The original gives a case study that stuck with me. Instead of asking "Rate whether the model's response is colloquial, 0-10," the improved version breaks it down as:
- Does the model address the rider as "您" (formal you)?
- Does the model use informal expressions like "甭客气" (don't mention it) or "明儿见" (see you tomorrow)?
- Does the output contain particles like "吧," "呢," "那个"?

All three are yes/no. Human-human consistency improved from 62% to 92% (Beam team's data). The method: **turn "feelings" into "facts."** Break down vague concepts into verifiable dimensions and push each Rubric toward binary outcomes.

**3. The data flywheel starts lower than you think.**

Most new teams fall into this trap: design a complex evaluation metric system first, then fail to execute it. The right path: **get the data flywheel spinning first**, then refine gradually.

Meituan's fulfillment digital station master service started with ~20 evaluation indicators. A year later: ~200. Those 180 additional indicators weren't designed on a whiteboard — they were fed by Bad Cases.

Engineering formula: **Bad Case → identify capability boundary → add evaluation dimension → re-deploy → collect new Bad Cases.**

---

### Deep Analysis: Engineering Implementation Path

**Observation first, evaluation second.** You cannot evaluate what you cannot observe. Before building any evaluation system, you need a full Trace system that records every hop in the Agent's execution: which Prompt template, which tool call, what it returned, how many tokens, what the intermediate state was.

**Four evaluation layers** (useful as a checklist):

| Layer | Question | Methods |
|-------|----------|---------|
| **Result** | Was the task completed? | Exact match / LLM-as-Judge |
| **Process** | Was the planning sound? Were the steps stable? | Trace analysis / path comparison |
| **Efficiency** | Are latency, tokens, and tool-call counts acceptable? | Metrics / cost analysis |
| **Risk** | Any unauthorized actions, misoperations, or security issues? | Sandbox isolation / policy audit |

Most teams only cover the result layer. Efficiency and risk layers should enter the system early for any production Agent.

**Long-horizon Agent paradigm shift:**
```
Old: Query → Answer (Was this answer good?)
New: Prompt → Expected Behavior (Did the Agent follow the intended trajectory?)
```

The evaluation object becomes a `(Prompt, ExpectedBehavior, Trace)` triple, not a `(Query, Answer)` pair. This fundamentally changes how test data must be constructed.

---

### Top 3 Usable Open-Source Evaluation Frameworks

**1. pinchbench** (github.com/pinchbench/skill, 1200+ stars)  
Focused on OpenClaw-type coding agents. Tasks defined as Markdown files. Strong real-world scenario coverage. Best for: Coding Agent capability benchmarking.

**2. claw-eval** (github.com/claw-eval/claw-eval, 500+ stars)  
From Peking University. Tasks defined in YAML (structured, programmatically extensible). Academic rigor, publicly citable results. Best for: Research-grade benchmarks that need reproducibility.

**3. WildClawBench** (github.com/InternLM/WildClawBench, 500+ stars)  
From InternLM team. Core idea: "Throw the Agent into the wild" — no sanitized sandbox, real user sessions. Best for: Testing generalization across unknown task distributions, finding capability boundaries.

**Recommendation:**
- Build your own Rubric + Grader system following Meituan's methodology for business-specific evaluation
- Use one of the three frameworks for cross-team or cross-model comparison

---

### Actionable Takeaways

**Minimum viable evaluation bootstrap:**
1. Wire full Trace logging (before anything else)
2. Define 5-10 Task specs (prompt + expected_behavior)
3. Collect first 30-50 Bad Cases from production or sandbox
4. Break down each "felt bad" into 3-5 yes/no Rubric questions
5. Run manual labeling first; confirm human-human consistency > 85% before adding automated scoring

**What to avoid early:**
- Don't design more than 20 evaluation dimensions before you have 100 Bad Cases
- Don't treat machine evaluation output as decision input before human-machine consistency is validated

**The evaluation system needs to be evaluated too:** Rubric definitions decay as business evolves. Good Case definitions shift as user demographics expand. Budget periodic Rubric audits — track "unknown" response rates as a signal for Rubric quality.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
