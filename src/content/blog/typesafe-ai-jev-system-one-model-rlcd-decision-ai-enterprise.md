---
title: "Jev：TypeSafe AI 的 RLCD 决策模型，输出 Token 免费、最高快 200 倍"
titleEn: "Jev: TypeSafe AI's RLCD Decision Model — Free Output Tokens, Up to 200x Faster"
description: "前 OpenAI 研究员 Diogo Almeida 创立 TypeSafe AI，2026-09-15 发布首个 System One Model「Jev」：RLCD 训练，并行采样非逐 token 生成，输入 $0.042/百万 token，输出免费。不生成文字，专为企业工作流三类决策（判断/选择/打分）设计，峰值快 200 倍、便宜 444 倍。4000 万美元种子轮，DCVC 领投。"
descriptionEn: "Former OpenAI researcher Diogo Almeida launches TypeSafe AI and its System One Model 'Jev' (2026-09-15): RLCD-trained, parallel-sampling, $0.042/M input tokens with free output. Cannot generate text. Built for three enterprise decision structures—binary judgment, selection, scoring. Peak 200x faster and 444x cheaper than frontier LLMs. $40M seed led by DCVC."
pubDate: "2026-09-18"
updatedDate: "2026-09-18"
category: "Tech-Experiment"
tags: ["decision-AI", "RLCD", "enterprise-AI", "structured-output", "TypeSafe-AI", "automation", "workflow"]
heroImage: "../../assets/images/typesafe-ai-jev-system-one-model-rlcd-decision-ai-enterprise-banner.jpg"
---

> 📌 官网：https://typesafe.ai | 控制台：https://console.typesafe.ai
> 发布日期：2026-09-15 | 融资：$40M 种子轮，DCVC 领投

---

Diogo Almeida 在 OpenAI 工作的那些年，参与了 RLHF（来自人类反馈的强化学习）和 ChatGPT 的早期研究。他最后一个离开前的问题是：**"模型已经在聊天上超越人类好几年了，为什么自动化的进展还这么慢？"**

他的答案是：**因为我们一直在用错误的工具**。给 AI 模型回答的问题，是"给我生成一段文字"，但企业真正需要的是"给我一个决策"。两件事不一样，用同一套架构来做，必然是贵又慢。

2026 年 9 月 15 日，TypeSafe AI 宣布从隐身模式出来，发布了首个 System One Model —— **Jev**，同时公布 4000 万美元种子轮融资（DCVC 领投）。

---

## 什么是 System One Model

在 Kahneman 的框架里，System 1 是快速直觉，System 2 是慢速推理。TypeSafe 借用这个命名，但含义有本质区别：

- **传统 LLM（System Two）**：逐 token 自回归生成，慢、成本高，输出是字符串，可以"撒谎"
- **Jev（System One）**：一次并行采样，输出是带概率的类型化决策，不生成字符串，不能幻觉

Jev 的核心定义是：**非结构化状态进入，类型化概率决策输出**。它是一个函数调用，不是一个聊天对象。

你问不了它"帮我写一封邮件"，但你可以问它：
- "这张收据的类别是餐饮/差旅/办公用品还是其他？（概率分布）"
- "这条客服记录，用户满意度是 1-10 的几分？"
- "这个请求应该路由到哪个处理队列？"

它返回的不是字符串，而是确定的类型值 + 置信概率。

---

## 训练方法：RLCD vs RLHF vs RLVR

TypeSafe 的训练方法叫 **RLCD（Reinforcement Learning for Calibrated Decisions）**，和 RLHF 的主要区别在于奖励信号的来源：

| 方法 | 奖励信号 | 优化目标 |
|------|---------|---------|
| RLHF | 人类偏好评分 | 人类认为回答"好" |
| RLVR | 可验证正确性（数学/代码） | 答案正确 |
| **RLCD** | 真值数据 + Brier Score 等专有评分规则 | 决策概率校准（epistemic honesty） |

Brier Score 是气象预报领域用了几十年的概率校准指标——不只是"答对了没有"，而是"你说 80% 概率时，实际发生率是多少"。这是 Jev 能给出"不会幻觉的概率"的数学基础：它从未被优化去生成字符串，所以根本不存在字符串级别的幻觉空间。

---

## 三种决策结构

Jev 支持三种原子决策类型，所有复杂业务流程都可以拆解成这三种的组合：

### 1. 判断（Binary / Multi-label Judgment）
给定一段非结构化文本或数据，返回 true/false 或多标签概率。

```
场景：费用报销审批
输入：一张餐厅收据 OCR 文本 + 员工提交说明
问题：
  - 收据可读性是否合规？（yes/no + 概率）
  - 金额与说明的餐饮场景是否匹配？（yes/no + 概率）
  - 是否超过差旅政策上限？（yes/no + 概率）
```

### 2. 选择（Selection）
从最多 255 个候选项中选择一个，返回选中项及概率分布。

```
场景：客服工单路由
输入：用户描述的问题文本
候选队列：[技术支持, 账单问题, 功能建议, 投诉升级, 一般咨询, ...]
输出：最匹配队列 + 各队列归属概率
```

### 3. 打分（Scoring）
在指定维度上给出连续或离散分数。

```
场景：LLM 输出质量把关
输入：一段 AI 生成内容
问题：
  - 有害内容风险：0-10
  - 与用户意图一致性：0-10
  - 事实准确性置信度：0-10
```

一个业务流程可以用多个 Jev 调用串联，每次调用处理一个决策节点。代码处理路由逻辑，Jev 处理判断逻辑，两者职责分离。

---

## 性能数据

TypeSafe 自己公布的峰值数据和独立测试结果：

| 指标 | TypeSafe 自测（峰值） | 独立测试（Every.to） |
|------|---------------------|-------------------|
| 速度（vs 前沿 LLM） | 193.6x 快 | ~25x 快（vs Claude Fable 5.1） |
| 成本（vs 前沿 LLM） | 444.6x 便宜 | ~580x 便宜（vs Claude Fable 5.1） |
| 端到端响应时间 | 70–500ms | — |

需要注意的是，在 TypeSafe 自己公布的工作流评估基准上，Jev 的准确率是 **67.8%**，而最优对比模型是 **74.1%**。也就是说，Jev 比对手快、便宜，但在整体任务准确率上还有差距——特别是在发票处理类任务上明显落后。

这不是隐藏的信息——TypeSafe 的官方 blog 里明确列出了这些局限性，包括测试集由内部团队制作、参考策略用了竞争对手模型等偏差来源。这种透明度，相对正常。

---

## 价格与获取方式

**定价**：
- 输入：**$0.042 / 百万 token**（约是 GPT-4o 输入价的 1/5）
- 输出：**免费**
- 每次决策调用约 **$0.0004**（按平均请求量估算）

**不开源**。这是 TypeSafe 的商业模式，模型权重不公开。

**如何获取**：
1. 访问 https://typesafe.ai 申请 Early Access 候补名单
2. 审批通过后访问 https://console.typesafe.ai 使用 Playground
3. API 形式集成到应用——发送一段程序状态 + 结构化问题定义，返回类型化概率决策

TypeSafe 也提供一个 **System One LLM Wrapper**，用来把现有 LLM（OpenAI、Anthropic 等）包装成 System One 接口，用于迁移过渡期——先验证流程可行，再替换成 Jev 降成本。

---

## 做不到的事情

这一点必须说清楚，避免错误预期：

- **不能生成文字**：不能写邮件、不能写摘要、不能解释为什么做出某个决策
- **不支持图像输入**（截至 2026-09-15 发布时）
- **不适合需要推理链的任务**：复杂的法律分析、多步数学推导等仍然需要 LLM
- **不替代人类判断**：适合明确规则可编程化的决策节点，边界模糊的场景仍需人工审查

如果你的流程需要"解释结果"或"给用户看一段自然语言"，Jev 不是你的答案。它是一个**不说话的决策引擎**——做判断，不解释。

---

## 我们如何更好地使用 Jev

从工程角度，Jev 最适合的场景是：**高频、结构化、有正确答案参考数据的决策节点**。

几个设计建议：

**1. 把业务流程分解成决策图**

把流程里每个"需要 AI 判断"的节点单独列出来，确认每个节点属于判断/选择/打分中的哪类。对于明确的规则（"金额 > 1000 就需要审批"），用代码写，不要给 Jev。对于需要语义理解的节点（"这条描述是否符合差旅场景"），给 Jev。

**2. 准备训练数据**

Jev 的 API 文档提到，用有标注的真值数据可以进一步微调决策校准。如果你的业务已经有历史判断记录，整理成输入/决策对，是提升准确率的直接路径。

**3. 和 LLM 混用**

工作流里有些节点需要生成解释文本（发给用户的通知），有些节点只需要内部路由决策。Jev 处理后者，LLM 处理前者，按调用量计算成本可以显著降低整体预算。

**4. 先用 Wrapper 迁移**

TypeSafe 的 System One LLM Wrapper 让你在不改接口的情况下切换后端——先跑通逻辑，证明结构化决策可行，再把高频节点迁移到 Jev。

---

## 应用场景预测

考虑到 Jev 的技术特性，以下几类场景未来可能是高价值落地方向：

**内容合规与安全审核**：UGC 平台的高频分类（色情/暴力/垃圾/广告）目前大量用规则 + 小模型，Jev 的准确率和速度组合可能是中间层的替代方案。

**金融风控实时判断**：交易欺诈初筛、异常交易路由，要求亚秒级响应且不能幻觉，Jev 的并行架构正好契合。

**企业流程自动化（ERP/CRM 里的 AI 节点）**：每一个"让 AI 帮我判断"的表单节点，都是潜在的 Jev 调用点，从工单分级到合同条款合规检查。

**Agent 的决策守门人**：多 Agent 系统里，在 LLM Agent 做出动作前先用 Jev 过一遍（"这个工具调用是否符合用户授权？"），比用另一个 LLM 便宜和快 2 个数量级。

---

## 一个命名里的预言

Jev 的命名来自 **William Stanley Jevons** 和 **Jevons Paradox**：让一种资源变便宜，不会减少消耗，反而会催生更多需求。19 世纪，蒸汽机效率提升了，英国的煤炭消耗量反而猛增，因为便宜的效率开启了之前不可行的用法。

TypeSafe 的赌注是：当每次 AI 决策的成本从 $0.10 降到 $0.0004，不只是让现有用法变便宜——它会让此前完全不经济的自动化场景变得可行，催生新的需求量级。

能否实现，取决于准确率能不能追上。目前的 67.8% 和 74.1% 的差距，就是他们最需要填补的护城河。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Website: https://typesafe.ai | Console: https://console.typesafe.ai
> Released: 2026-09-15 | Funding: $40M seed, led by DCVC

---

When Diogo Almeida was at OpenAI, helping build RLHF and the early versions of ChatGPT, he left with a question: **"Models have been superhuman at chat for years — so where is all the automation?"**

His answer: we've been using the wrong tool. Enterprise workflows don't need "generate me some text." They need decisions. Using the same autoregressive architecture for both is why AI-driven automation remains expensive and slow.

On September 15, 2026, TypeSafe AI emerged from stealth with **Jev**, its first System One Model, announcing a $40M seed round led by DCVC.

---

## What Is a System One Model

TypeSafe borrows Kahneman's framing but gives it a different meaning:

- **Traditional LLMs (System Two)**: autoregressive token-by-token generation — slow, costly, outputs are strings, can hallucinate
- **Jev (System One)**: single parallel sampling pass, outputs typed decisions with calibrated probabilities, no string generation, mathematically cannot hallucinate

Jev's core definition: **unstructured state in, typed probabilistic decisions out**. It's a function call, not a chat interface.

You can't ask it to write an email. You can ask it:
- "Is this receipt in the correct expense category? (probability distribution)"
- "Rate this customer service record for satisfaction on a scale of 1-10"
- "Which queue should this request be routed to?"

It returns a typed value plus a confidence probability — not a string.

---

## Training Method: RLCD vs RLHF vs RLVR

TypeSafe's training method is **RLCD (Reinforcement Learning for Calibrated Decisions)**. The key difference from RLHF is the reward signal:

| Method | Reward Signal | Optimized For |
|--------|--------------|---------------|
| RLHF | Human preference ratings | "Good" responses by human standards |
| RLVR | Verifiable correctness (math/code) | Correct answers |
| **RLCD** | Ground-truth data + proper scoring rules (Brier Score) | Epistemically honest calibrated probabilities |

The Brier Score has been used in weather forecasting for decades — it doesn't just ask "were you right?" but "when you said 80%, did it happen 80% of the time?" This is the mathematical foundation for Jev's claim of hallucination-free output: it was never trained to generate strings, so there is no string-level hallucination surface.

---

## Three Decision Structures

Jev supports three atomic decision types. All complex business processes can be decomposed into combinations of these:

### 1. Judgment (Binary / Multi-label)
Given unstructured text or data, return true/false or multi-label probabilities.

```
Use case: expense report approval
Input: OCR text from a restaurant receipt + employee description
Questions:
  - Is the receipt legible and compliant? (yes/no + probability)
  - Does the amount match the described dining context? (yes/no + probability)
  - Does it exceed travel policy limits? (yes/no + probability)
```

### 2. Selection
Choose from up to 255 candidates; returns the selected item with a probability distribution.

```
Use case: customer support ticket routing
Input: user's problem description text
Candidates: [Technical Support, Billing, Feature Request, Escalation, General Inquiry, ...]
Output: best-matching queue + probability for each option
```

### 3. Scoring
Give a continuous or discrete score on a specified dimension.

```
Use case: LLM output quality gate
Input: a piece of AI-generated content
Questions:
  - Harmful content risk: 0-10
  - Alignment with user intent: 0-10
  - Factual accuracy confidence: 0-10
```

A business process chains multiple Jev calls — code handles routing logic, Jev handles judgment logic. Clean separation of concerns.

---

## Performance Numbers

TypeSafe's own peak figures and independent test results:

| Metric | TypeSafe Internal (peak) | Independent (Every.to) |
|--------|--------------------------|------------------------|
| Speed (vs frontier LLM) | 193.6x faster | ~25x faster (vs Claude Fable 5.1) |
| Cost (vs frontier LLM) | 444.6x cheaper | ~580x cheaper (vs Claude Fable 5.1) |
| End-to-end latency | 70–500ms | — |

One important caveat: on TypeSafe's own workflow evaluation dashboard, Jev scores **67.8%** accuracy versus **74.1%** for the best comparator. Jev is faster and cheaper, but trails on overall task accuracy — particularly on invoice processing.

This isn't hidden: TypeSafe's own blog post lists these limitations explicitly, including the fact that the evaluation workflows were created by their internal team and that reference comparisons favor competitor models. The transparency is notable.

---

## Pricing and Access

**Pricing**:
- Input: **$0.042 per million tokens** (~1/5 of GPT-4o input pricing)
- Output: **free**
- Cost per decision call: approximately **$0.0004**

**Not open source.** The model weights are proprietary.

**How to access**:
1. Visit https://typesafe.ai and join the early access waitlist
2. Once approved, access the Playground at https://console.typesafe.ai
3. Integrate via API — send a block of program state + structured question definitions, receive typed probabilistic decisions

TypeSafe also offers a **System One LLM Wrapper** to wrap existing LLMs (OpenAI, Anthropic, etc.) in a System One interface — validate your pipeline logic first, then migrate high-frequency decision nodes to Jev for cost savings.

---

## What It Cannot Do

This matters enough to state clearly:

- **Cannot generate text**: no emails, no summaries, no explanations of its decisions
- **No image input** (as of the September 15 launch)
- **Not for chained reasoning tasks**: complex legal analysis, multi-step math still require LLMs
- **Not a replacement for human judgment**: suitable for decision nodes with clear rules and reference data; ambiguous cases still need human review

If your workflow needs to "explain the result" or "show users natural language," Jev is not the answer. It is a **silent decision engine** — it judges, it does not explain.

---

## Engineering Guidance: How to Get the Most from Jev

**1. Decompose business processes into decision graphs**

Map every "needs AI judgment" node in your flow. Confirm each belongs to judgment/selection/scoring. Write hard rules as code (never ask Jev "is this over $1000?"). Give Jev the semantic judgment nodes ("does this description fit a travel expense context?").

**2. Prepare labeled ground-truth data**

The API supports calibration fine-tuning with labeled reference data. If you have historical human-approved decisions, organizing them as input/decision pairs is the most direct path to accuracy improvement.

**3. Mix with LLMs strategically**

Some nodes generate explanation text (user-facing notifications). Others are internal routing decisions only. Jev handles the latter; LLMs handle the former. Calculating cost by call volume, this split meaningfully reduces total budget.

**4. Migrate with the Wrapper first**

The System One LLM Wrapper lets you switch backends without changing your interface. Prove the structured decision flow works with LLMs, then migrate high-frequency nodes to Jev to capture the cost savings.

---

## Future Applications

Given Jev's technical profile, these scenarios look like high-value targets:

**Content moderation and safety**: UGC platforms running high-frequency classification (violence/spam/adult content) currently rely on rules + small models. Jev's accuracy-speed combination may be the right middle layer.

**Real-time financial risk**: Transaction fraud screening, anomaly routing — sub-second response required, hallucination unacceptable. Jev's parallel architecture fits this profile.

**Enterprise workflow automation (AI nodes in ERP/CRM)**: Every "let AI judge this" form field is a potential Jev call — from ticket priority to contract clause compliance checks.

**Agent decision guardrails**: In multi-agent systems, running a Jev check before an LLM agent takes an action ("does this tool call fit the user's authorization scope?") costs two orders of magnitude less than using another LLM for the same check.

---

## The Prophecy in the Name

Jev is named after **William Stanley Jevons** and **Jevons Paradox**: making a resource cheaper doesn't reduce consumption — it creates more of it. When steam engines became more efficient, British coal consumption didn't fall; it surged, because cheaper efficiency unlocked uses that were previously uneconomical.

TypeSafe's bet: when the cost of an AI decision drops from $0.10 to $0.0004, it doesn't just make existing use cases cheaper. It makes entire categories of automation economically viable for the first time, creating a new order-of-magnitude demand.

Whether that plays out depends on whether accuracy can catch up to the benchmark leaders. The gap between 67.8% and 74.1% is exactly the moat they need to fill.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
