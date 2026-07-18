---
title: "Agent eval 的六代迭代：从看答案到看分布"
titleEn: "Six Generations of Agent Eval: From Final Answer to Distribution"
description: "转载整理自 BrainTrust 原文《The six generations of AI agents and how to eval them》：Agent 从 Prompt→Chain→ReAct Loop→Workflow Graph→Modern Agent Loop→AI Harness 六代演进，eval 对象也从最终答案扩展到 trace、分布、分层系统。核心：正确但太贵不算成功；Production-to-Eval 飞轮才是团队最长期的资产。"
descriptionEn: "Adapted from BrainTrust's 'The six generations of AI agents and how to eval them': as Agent architectures evolved from Prompt to AI Harness, eval must evolve from final-answer grading to trace inspection, distribution metrics, and layered test systems. Key insight: correct-but-expensive is not success. The Production-to-Eval flywheel is the team's most durable asset."
pubDate: "2026-07-06"
updatedDate: "2026-07-06"
category: "Research"
tags: ["Agent eval", "BrainTrust", "AI Harness", "Production-to-Eval", "ReAct", "observability", "AI测评"]
heroImage: "../../assets/images/brainstrust-agent-eval-six-generations-guide-banner.jpg"
---

> **转载说明**：本文内容整理自小红书博主「可乐同学别卷了」对 BrainTrust 原文的拆解笔记，原文为 BrainTrust《[The six generations of AI agents and how to eval them](https://www.braintrust.dev/blog/six-generations-of-agents)》。图文来源：[小红书原帖](https://www.xiaohongshu.com/discovery/item/6a4b513100000000150243b4)。版权归原作者所有，本站仅做学习整理与传播。

---

## 三句话先记住

1. **eval 对象跟着架构长**：从「最后答案对不对」，到 trace、到分布、到分层系统；Agent 每复杂一层，eval 就要扩一层。
2. **正确不等于成功**：正确但太贵 / 不稳定 / 不安全都不算成功；要看 pass^k、p95 成本延迟、是否在预算内安全完成。
3. **生产失败要回流成 eval**：生产 trace 是 eval 的原材料，eval 是发布的门禁。

---

## 为什么要重新定义 eval？

2022 年，一个 AI 功能往往就是一个 prompt：给模型一段指令，让它分类、总结、改写、抽取。那时评测也简单——看最终回答对不对、完不完整、有没有幻觉。

但今天，Agent 早已不是「一个 prompt + 一个模型」。它可能有工具调用、检索、记忆、代码沙箱、权限审批、长期状态、技能系统、外部集成，甚至能在真实环境里执行操作。

> **Agent 的架构每复杂一层，评测对象也必须扩大一层——不能再只问「最后答案对不对」。**

要问的变成：它查了什么、用了什么工具、参数对不对、有没有绕圈 / 超预算 / 调危险操作、记忆有没有污染判断、生产环境稳不稳、新版比旧版好在哪。

BrainTrust 把 Agent 演进分成六代，对应讲清每一代该怎么 eval。

---

## 六代架构，六代 eval

### 第一代：Prompt

还算不上真正的 Agent：一个 prompt、一次调用，没工具、没检索、没记忆。

**eval 重点：最终答案质量**
- 有没有编造事实？
- 有没有覆盖关键排查步骤？
- 优先级是否合理？
- 有没有在没证据时就建议危险操作？

这时 eval 像传统的回答质量评测。

---

### 第二代：Chain

引入固定流程：解析告警 → 查最近部署 → 查日志 → 读 dashboard → 把 evidence 塞给模型生成报告。

模型开始接触真实上下文，但流程是写死的——比如系统只查过去 60 分钟，而真正肇事的部署在 75 分钟前，模型拿到的上下文就是错的，还会自信地给出错误判断。

**eval 重点：中间步骤正确性**
- parse alert 是否提取了正确的 service？
- retrieval 是否找到了关键 evidence？
- 检索结果有没有太多噪音？
- 最终回答是否忠实于上下文？

> eval 的形状开始跟系统结构一致：系统有几步，eval 就要能定位每一步。

---

### 第三代：ReAct Loop

接近今天大家说的 Agent：模型在循环里自己决定下一步——调哪个工具、传什么参数、什么时候停。能力更强，也更危险。新问题冒出来：选错工具、参数错误、一直循环不停、太早停止、早期误判污染后续推理、成本 / 延迟失控、误调危险工具。

**eval 单位从 final answer 变成了 trace**，不仅看它最后说什么，还看它一路怎么做：
- 是否调用了必要工具？
- 是否避开了 forbidden tools？
- 工具参数是否正确？
- trace 是否在合理步数内？
- destructive action 的前置条件是否满足？
- 是否在预算内完成？

> 从这一代起，eval 更像行为测试，而不是简单打分。

---

### 第四代：Workflow Graph

第三代太自由，很多团队又把控制权收回来，做成 workflow graph / 状态机：classify incident → gather evidence → propose hypotheses → decide action → render report。模型仍然参与，但只在受控节点里工作，runtime 负责流程、分支、重试和 guardrails。

好处是更稳定、更可测；坏处是灵活性下降、长尾容易掉出 graph（被硬塞进错误分支）。

**eval 很像软件工程测试：**
- **node-level eval** — 像单元测试
- **contract eval** — 检查节点之间的数据结构和约束
- **branch coverage** — 确认关键路径都被测到
- **policy compliance** — 确认高风险分支按规则处理
- **end-to-end eval** — 检查整体结果

> 关键变化是：Agent 开始像正常软件系统一样被测试。

---

### 第五代：Modern Agent Loop（回归）

模型变强，loop 又回来了。现代 Agent 本质上还是「模型 + 工具 + while loop」，但模型强很多：能长期调查、修正查询、维护假设列表、从弱证据里恢复。这时 graph 的限制反而成了成本——流程太硬、长尾太多、维护复杂。

但强模型带来新难题：同一个任务可以有多条合理路径，你不能再假设只有一个正确 trajectory。

**eval 要从「单次结果」转向「分布」：**
- 同一个 case 跑多次
- **pass@k**：多次尝试里至少成功一次
- **pass^k**：每次都稳定成功
- **p95 tool calls / p95 latency / p95 cost**
- 看结果方差、是否在预算内成功

> **一个很重要的判断：正确但太贵，也不算真正成功。** 一个 SEV3 小事故，如果 Agent 用了 35 次工具调用才解决，它不是成功案例，而是成本事故。

---

### 第六代：AI Harness

今天最值得关注的阶段。Agent 不再只是一个 loop，而是被完整 harness 包起来：memory、sandbox、skills、tool discovery、permissions、approvals、durable state、integrations、replay、event log。它已经不是「能调用工具的 LLM」，而是一个真实运行系统。

失败也可能不来自模型，而来自 harness：加载了错误 memory、tool registry 给了错误工具、memory 被污染、sandbox 权限过大、加了危险工具但 approval policy 没更新、外部系统 schema 变了、生产出现 offline eval 覆盖不到的问题。

**第六代 eval 必须是分层系统：**
- **smoke tests** — 先确认 harness 接线正常
- **offline evals** — 评已知 cases
- **simulations** — 模拟动态环境、噪音、用户补充信息、stale memory、prompt injection
- **replays** — 用历史生产 trace 测新版本
- **shadow runs** — 新版本旁路跑真实流量，但不真正执行动作
- **online scoring** — 生产中持续抽样评分、监控漂移

> 这一代最重要的问题不是「这次回答对不对」，而是：我们是否信任这个 Agent 下一次继续在真实世界里运行？

---

## 真正的核心：Production-to-Eval 飞轮

全文最有价值的不是六代分类，而是它提出的工作飞轮。成熟的 Agent 团队应该持续做这件事：

1. **记录**生产中的输入、输出、工具调用、上下文、模型选择、成本、延迟和人工修正
2. **复盘**失败和 near miss
3. **把失败聚类**成模式：retrieval miss、bad tool choice、unsafe action、cost blowup、poor handoff……
4. **把重要失败转成 eval case**
5. **每次改** prompt / model / tool / workflow / harness **都跑 eval**
6. 新版本只有在质量更好、成本可控、安全不回归时才**发布**
7. 上线后继续用 **online scoring** 捕捉新失败

> **一句话：生产 trace 是未来 eval 的原材料，eval 是未来发布的门禁。**

---

## 一句话理解

Agent 产品不能只靠 demo 判断。一个 Agent 如果只展示「它最后完成了任务」，却没有 trace、没有 replay、没有 online scoring、没有 budget、没有 policy、没有失败回流，那它很可能还停留在 demo 阶段。

真正可生产化的 Agent，要能回答更硬的问题：
- 它为什么成功/失败在哪里？
- 它是否稳定成功？是否在预算内成功？是否安全地成功？
- 新版本是否比旧版本更好？
- 生产中的失败，能不能回到 eval 里？

> 未来 Agent 的竞争，可能不只是模型能力的竞争，而是 eval、observability、harness 和 release governance 的竞争。模型、prompt、工具、架构都会变，但一个团队对「什么叫好」的定义、以及把真实失败持续转成 eval 的能力，会成为更长期的资产。

---

> **原文来源**：BrainTrust《The six generations of AI agents and how to eval them》  
> **小红书整理**：可乐同学别卷了（AI版）· [原帖链接](https://www.xiaohongshu.com/discovery/item/6a4b513100000000150243b4)  
> 本站转载整理，版权归原作者所有。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: BrainTrust's framework for evaluating AI agents across six architectural generations: Prompt → Chain → ReAct Loop → Workflow Graph → Modern Agent Loop → AI Harness. As architecture complexity grows, eval must grow with it — from final-answer grading to step-level trace inspection, to distribution metrics (pass@k, pass^k, p95 cost), to layered test systems (smoke → offline → simulation → replay → shadow → online scoring). Key insight: correct-but-expensive is not success. A SEV3 incident resolved with 35 tool calls is a cost incident, not a win. The Production-to-Eval flywheel — logging production traces, clustering failures, converting them to eval cases, gating releases on eval — is the team's most durable long-term asset.

---

**The Six Generations at a Glance**

| Gen | Architecture | Eval focus |
|---|---|---|
| 1 | Prompt | Final answer quality |
| 2 | Chain | Step-level correctness |
| 3 | ReAct Loop | Trace behavior (tools, params, budget) |
| 4 | Workflow Graph | Unit + branch + policy coverage |
| 5 | Modern Agent Loop | Distribution (pass@k, p95 cost, variance) |
| 6 | AI Harness | Layered: smoke → offline → simulation → replay → shadow → online scoring |

**The Production-to-Eval Flywheel**

Log → Review failures → Cluster patterns → Convert to eval cases → Run eval on every change → Gate releases → Catch new failures with online scoring → repeat.

One sentence: production traces are the raw material for future evals; evals are the gate for future releases.

**Source**: BrainTrust «The six generations of AI agents and how to eval them» · Original XHS post by 可乐同学别卷了

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
