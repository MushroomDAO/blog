---
title: "框架工程（Harness Engineering）：用确定性执行层替代提示词工程——arXiv:2608.26197 实验全解析"
titleEn: "harness-engineering-llm-agent-deterministic-structured-planning"
description: "arXiv:2608.26197「Harness Engineering for Predictable Agentic Systems」是一篇9页实证研究，作者 Saransh Dhage（独立研究者，非谷歌）用两个模型×两个任务×100次重复跑出了一个反直觉结论：在 LLM Agent 外面套确定性执行层，不一定能提升可复现性——甚至可能变差。真正有效的关键只有一个：结构化规划（Structured Planning）。本文完整拆解实验设计、五个 Harness 组件、两阶段结果、成本数据，以及对 Agent 工程实践的真实启示。"
descriptionEn: "arXiv:2608.26197 'Harness Engineering for Predictable Agentic Systems' is a 9-page empirical study by independent researcher Saransh Dhage showing a counterintuitive finding: wrapping an LLM agent in a deterministic execution harness does not reliably improve reproducibility — it can actively degrade it. The only component that fully closes the gap is Structured Planning. This post traces the full experimental design, five harness components, two-stage results, cost data, and practical implications for agent builders."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Research"
tags: ["Agent工程", "LLM", "框架工程", "确定性系统", "强化学习", "实证研究", "工具调用", "生产可靠性"]
heroImage: "../../assets/images/harness-engineering-llm-agent-deterministic-structured-planning-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

论文：arXiv:2608.26197 | 作者：Saransh Dhage（独立研究者）| 发布：2026-08-25  
9页 | cs.SE | 2模型 × 2任务 × 100次重复 | Qwen-2.5-7B + Gemma-3-27B

---

## 先澄清一个广泛流传的误解

这篇论文在社交媒体上的传播版本里，被冠以「谷歌团队发布」的标签。实际上：

**作者 Saransh Dhage 的机构标注是「Independent Researcher」（独立研究者）**，论文里完全没有任何 Google 的机构署名。「谷歌」的联想来源，很可能是论文使用了 Google 的 `gemma-3-27b-it` 开源模型作为实验对象之一。

同样值得注意：社交媒体传播版本里的「六步框架」（AGENTS.md、感知检测、Agent 循环、外置记忆、权限管控、可观测能力）是对这篇论文核心思想的**实践层扩展解读**，论文本身的核心实验围绕5个 Harness 组件展开，且中心结论和这6步描述的「配方式建议」有本质不同。

论文真正的价值在于：它是一个**受控实验**，不是一份配方，更不是一套最佳实践清单。

---

## 论文要解决的问题

**研究问题**：给 LLM Agent 套上一个确定性执行层（Harness），能不能在不降低任务成功率的前提下，减少运行到运行之间的行为方差？

这个问题来自一个真实的工程痛点：LLM Agent 在相同任务、相同工具、相同提示词的条件下，不同次运行会产生不同的规划、不同的工具调用序列、不同的输出格式。对于**金融合规、合同审查、信贷风险**这类受监管场景，这种不可预测性是硬性部署阻断。

提示词工程能在一定程度上缓解这个问题，但提示词本质上是「建议」，不是「约束」。Harness Engineering 的思路是：在模型层之外、工具层之上，建一个**确定性控制层**，把可以约束的执行维度逐一锁死。

---

## Harness 的5个组件

论文基于 LangGraph 实现了 Harness，每个组件独立可开关：

**1. 有限状态执行（Finite-State Execution）**

把任务分解为固定的命名状态序列（例如：`LOAD_DATA → VALIDATE_DATA → CALCULATE → GENERATE_REPORT`）。Agent 只能按照预定义的状态图转移，不能自行决定「下一步做什么」。

**2. 强制工具选择（Forced Tool Selection）**

每个状态绑定且仅绑定一个授权工具，通过 API 层的 `tool_choice="required"` 强制执行。消除了模型「决定不调用工具」或「调用错误工具」的可能性。

**3. 输出验证（Output Validation）**

每个状态的工具输出在交给下一个状态之前，必须通过 shape/type 验证器。验证失败则不允许状态机前进。

**4. 有界重试与升级（Bounded Retry with Escalation）**

验证失败后，重试次数有上限。超过上限则终止本次运行（Halt），不允许无限制地反复尝试。

**5. 结构化规划（Structured Planning）**

这是论文发现最关键的组件。在任何工具调用之前，Agent 必须先输出一个计划——一个 `{state, intended_tool}` 对象的 JSON 数组，系统用 `validate_structured_plan` 验证这个计划符合有限状态图。**只有计划通过验证，才允许第一个工具调用发生**。不合规的计划触发重提示（默认2次重试），超过则升级。

---

## 实验设计

**两个合成任务**

| 任务 | 描述 |
|------|------|
| `finance_ecl` | 12笔贷款的预期信用损失计算，含4笔无效贷款（测试验证路径处理） |
| `legal_clause` | 10条款合成合同，需要固定优先级关键词分类 |

两个任务都是线性四状态流水线（`load → validate → compute/classify → report`），刻意选线性结构以隔离「执行方差」与「任务难度」。

**两个模型**

- `qwen/qwen-2.5-7b-instruct`（7B）
- `google/gemma-3-27b-it`（27B）

两者均通过 OpenRouter 访问，研究者把 API provider 固定锁死以避免路由混乱产生的噪声，并把 HTTP 429/504 错误的请求丢弃重发，而不是计入失败。

**三个条件**

- **Baseline**：无任何 Harness 组件，原生工具调用
- **Harness**：有限状态执行 + 强制工具选择 + 输出验证 + 有界重试（**不含**结构化规划）
- **Harness+SP**：以上全部 + 结构化规划

**每个 model×task 单元 N = 100 次运行**。

**度量指标**

- **Determinism Index（DI）**：Plan Stability、Tool Path Consistency、State Transition Stability、Output Consistency 四项的等权平均，DI ∈ [0,1]
- **Reproducibility Rate（RR）**：完整执行轨迹与该批次众数轨迹精确匹配的比例（严格版本，任意一个 token 不同就不计）
- **Task Success Rate（TSR）**：正确性对照确定性 ground truth
- Token 数和延迟

---

## 第一阶段结果：第一步 Harness 产生混合效果（包含反向）

| 任务 | 模型 | Baseline RR | Harness RR | 效果 |
|------|------|-------------|-----------|------|
| finance_ecl | Qwen-2.5-7B | 0.91 | 0.93 | 不显著 |
| legal_clause | Qwen-2.5-7B | 0.79 | 0.68 | **显著变差** (p=0.038) |
| finance_ecl | Gemma-3-27B | 0.42 | 0.55 | 显著变好 (p=0.006) |
| legal_clause | Gemma-3-27B | 0.56 | 0.38 | **显著变差** (p<0.001) |

**4个单元里，有2个显著变差。**

这个结果本可以被草率地解读为「Harness 方法无效」或「对特定模型/任务有害」，但作者没有这么做。

### 诊断：不是 Harness 失效，是度量轴失效

作者对执行轨迹做了逐层分解：

- **Tool Path Consistency**（工具调用顺序）：在 Baseline 和 Harness 条件下，对成功运行来说都已经接近天花板
- **State Transition Stability**（状态转移顺序）：同上，已经高度稳定
- **Output Consistency**（输出一致性）：同上

**唯一剩余的自由轴是 Plan Stability——也就是 Agent 在执行前生成的自由文本计划。**

Harness 的有限状态执行和强制工具选择约束了工具序列，但没有约束计划文本的措辞。而 Reproducibility Rate 在严格模式下，**任意一个词的不同就会打破精确匹配**。

于是出现了荒诞的现象：同样的模型、同样的任务、同样的执行结果，仅仅因为某次计划文本里写了 `"load_document"` 而另一次写了 `"Load Document"`，就被判定为「不可复现」。Harness 约束了执行，却把测量集中到了它唯一没有约束的自由文本轴上，在某些单元里反而让 RR 看起来更差。

这是一个**测量层面的假象**，不是 Harness 本身的问题。

---

## 第二阶段结果：结构化规划彻底消除方差

| 任务 | 模型 | Harness+SP RR | Task Success |
|------|------|--------------|-------------|
| finance_ecl | Qwen-2.5-7B | **0.980** | 0.98 |
| legal_clause | Qwen-2.5-7B | **1.000** | 1.00 |
| finance_ecl | Gemma-3-27B | **1.000** | 1.00 |
| legal_clause | Gemma-3-27B | **1.000** | 1.00 |

加入结构化规划后，4个单元中3个达到 RR = DI = 1.000（permutation test p < 0.001 vs Baseline），第4个（Qwen/finance_ecl）达到 0.980，剩余方差来自两次真实的 per-state tool-calling failures（模型耗尽重试次数未调用工具），不是计划文本方差。

原来两个方向相反的「显著」结果（legal_clause 的两个退步），在加入 SP 后完全消失。

### 为什么结构化规划有效

因为它把「自由文本计划」变成了「schema-validated 结构化计划」——系统日志记录的不是模型输出的原始文本，而是通过验证后的 `(state, tool)` 对，从根本上消除了自由文本措辞作为方差来源的可能性。

---

## 成本：token 普遍降低，延迟因模型而异

| 任务 | 模型 | Token vs Baseline | Latency vs Baseline |
|------|------|------------------|-------------------|
| finance_ecl | Qwen-2.5-7B | -14.8% | **-14.2%**（更快）|
| legal_clause | Qwen-2.5-7B | -16.7% | **-24.7%**（更快）|
| finance_ecl | Gemma-3-27B | -15.9% | **+47.0%**（更慢）|
| legal_clause | Gemma-3-27B | -16.5% | **+41.4%**（更慢）|

**Token 节省是普遍的**：结构化规划只增加了 2-5% 的 token（额外的规划验证轮次），但有限状态执行 + 强制工具选择节省的重复调用 token 抵消并超过了这部分开销，整体比 Baseline 低 15-17%。

**延迟是模型依赖的**：Qwen 在大多数运行里第一次就通过计划验证，附加的验证步骤几乎不触发重提示，因此整体更快。Gemma 需要更频繁的计划验证重试，使延迟大幅增加。这个差异在样本量翻倍（N=100）后没有缩小，反而加剧，说明这是一个真实的、模型特有的效应，不是统计噪声。

**实践含义**：「Harness 是否值得部署」不是一个全局 yes/no，而是一个按模型测量的决策。

---

## 论文真正的核心贡献

这篇论文不是在告诉你「应该怎么构建 Agent Harness」，而是在告诉你以下三件事：

**1. 第一步 Harness 可能让你的度量看起来更差，但不代表 Harness 无效**

原因：你的 Harness 约束了工具序列和状态转移，但没有约束计划文本，于是度量集中到了唯一剩余的自由轴上，产生看似随机的效应。诊断方法：把复合指标拆解到每一层（计划层/工具层/输出层），找到哪个轴在驱动方差。

**2. 结构化规划（Structured Planning）是最有杠杆的单一 Harness 组件**

它不仅约束了执行，还约束了计划本身的表示方式，消除了最后一个主要方差来源。

**3. 成本必须按模型测量，不能假设**

延迟收益对 Qwen 是真实的，对 Gemma 是真实的惩罚。不同模型对「计划验证重试」的频率有显著差异，这个差异必须实测而非假设。

---

## 对 Agent 开发的启示

**不要把「添加约束」等同于「提升可靠性」**

论文的 Stage 1 结果清楚地显示：不完整的 Harness 可以主动损害度量指标。一个只约束了部分执行轴的 Harness，可能把度量集中到未约束轴上，让系统看起来不稳定。正确的做法是识别所有方差来源，逐轴消除。

**评估框架要分层**

单一的「可复现率」指标不够——它会把计划文本措辞的细微差异和真实的执行路径分歧混为一谈。需要分别追踪计划层、工具层、状态层、输出层的一致性。

**Structured Planning 是低成本高收益的优先实现项**

Token overhead 只有 2-5%，但能彻底消除自由文本计划作为方差来源。对需要可审计性（auditability）的场景，还有一个额外收益：系统日志里记录的是 schema-validated 的结构化计划，不是模型的原始文本，更容易在生产中追溯和审计。

**在生产部署前，按目标模型测延迟，不要泛化**

Qwen 在 SP 下更快，Gemma 更慢。这个差异是真实的、随样本量增加而稳定的。如果你的延迟预算很紧，在选定基础模型之前就要把 Harness 的延迟影响测清楚。

**论文的局限性**

作者在 Section 8 明确列出了三个主要局限：
1. 仅测试了线性四状态流水线，未测试分支型、判断型任务
2. 仅测试了7B和27B两个参数量级的开权重模型，未测试闭源或推理专用模型
3. 实验基于 OpenRouter（第三方路由层），延迟测量有额外噪声

这意味着：在更复杂的任务结构（动态分支、长链条 Agent）和更大规模或推理型模型上，这些结论是否成立需要独立验证。

---

## 关于「6步框架」的说明

社交媒体传播版本里的「6步」（AGENTS.md 指引文件、感知检测模块、Agent 循环、外置记忆、权限管控、可观测能力）是对 Harness Engineering 核心思想的**实践层扩展**，不是论文本身的内容。论文的核心是5个 Harness 组件和3个实验条件的受控对比，没有提及 AGENTS.md、外置记忆或可观测性。

这种实践扩展有其价值——它把学术发现转化为可操作的工程 checklist——但把它和原论文等同起来，会误导对研究质量和研究结论的判断。这篇论文的贡献不是配方，而是**方法论**：找出方差来源，逐轴约束，测量每个约束的实际成本。

---

**论文链接**

- arXiv:2608.26197：https://arxiv.org/abs/2608.26197
- PDF：https://arxiv.org/pdf/2608.26197

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Harness Engineering for LLM Agents: What the Actual arXiv Paper Says (and What Viral Summaries Get Wrong)

*by Mycelium Protocol*

---

Paper: arXiv:2608.26197 | Author: Saransh Dhage (Independent Researcher) | Published: 2026-08-25  
9 pages | cs.SE | 2 models × 2 tasks × 100 runs | Qwen-2.5-7B + Gemma-3-27B

---

### Clearing Up a Widespread Misconception

This paper is circulating on social media under the label "released by Google." In reality:

**Author Saransh Dhage's institutional affiliation is "Independent Researcher"** — there is no Google affiliation anywhere in the paper. The "Google" association almost certainly comes from the paper using Google's open-weight `gemma-3-27b-it` as one of the two experimental models.

The viral "6-step framework" (AGENTS.md, perception checks, agent loops, external memory, permission controls, observability) is also a **practitioner-level extension** of the paper's ideas — not the paper's actual content. The paper is a controlled experiment, not a recipe. Its central finding is more nuanced and more useful than any checklist.

---

### What Problem the Paper Addresses

**Research question**: Does wrapping an LLM agent in a deterministic execution harness reduce run-to-run variance without reducing task success?

This comes from a real engineering blocker: LLM agents running identical tasks with identical tools and prompts produce different plans, different tool call sequences, and different output formats across runs. For regulated domains — financial compliance, contract review, credit risk — this unpredictability is a hard deployment blocker.

Prompt engineering can partially mitigate this, but prompts are suggestions, not constraints. Harness Engineering wraps a deterministic control layer around the model, above the tool layer, and locks down every constrainable execution dimension.

---

### The Five Harness Components

The paper implements the harness as a LangGraph control layer with five independently toggleable components:

**1. Finite-State Execution**  
The task is decomposed into a fixed named-state sequence (e.g., `LOAD_DATA → VALIDATE_DATA → CALCULATE → GENERATE_REPORT`). The agent may only transition through the predefined graph — it cannot decide "what to do next."

**2. Forced Tool Selection**  
Each state is bound to exactly one authorized tool, enforced at the API level via `tool_choice="required"`. Eliminates unauthorized or omitted tool calls.

**3. Output Validation**  
Each state's tool output is checked against a shape/type validator before the state machine advances. Validation failure blocks progress.

**4. Bounded Retry with Escalation**  
On validation failure, the state retries up to a fixed bound before the run is halted — no silent infinite loops.

**5. Structured Planning**  
Before any tool is called, the agent must emit a plan as a JSON array of `{state, intended_tool}` objects. The system validates this plan against the finite-state graph (`validate_structured_plan`). A non-conforming plan triggers a re-prompt (default: 2 retries). **No tool call occurs until a valid plan exists.** What gets logged is the canonical, schema-validated `(state, tool)` pairs — not the model's raw text.

---

### Experimental Design

**Two synthetic tasks**

| Task | Description |
|------|-------------|
| `finance_ecl` | 12-loan Expected Credit Loss calculation (4 deliberately invalid loans to test validation-path handling) |
| `legal_clause` | 10-clause synthetic contract requiring fixed-priority keyword classification |

Both are linear four-state pipelines, chosen deliberately to isolate execution variance from task difficulty.

**Two models**: `qwen/qwen-2.5-7b-instruct` and `google/gemma-3-27b-it`, accessed via OpenRouter with provider explicitly pinned.

**Three conditions**: Baseline (no harness), Harness (without Structured Planning), Harness+SP (full harness).

**N = 100 runs per model×task cell.**

**Metrics**: Determinism Index (DI, composite of Plan Stability + Tool Path Consistency + State Transition Stability + Output Consistency), Reproducibility Rate (strict exact-trace match), Task Success Rate, tokens, latency.

---

### Stage 1: First-Pass Harness Produces a Mixed Result

| Task | Model | Baseline RR | Harness RR | Effect |
|------|-------|------------|-----------|--------|
| finance_ecl | Qwen-2.5-7B | 0.91 | 0.93 | Not significant |
| legal_clause | Qwen-2.5-7B | 0.79 | 0.68 | **Significant degradation** (p=0.038) |
| finance_ecl | Gemma-3-27B | 0.42 | 0.55 | Significant improvement (p=0.006) |
| legal_clause | Gemma-3-27B | 0.56 | 0.38 | **Significant degradation** (p<0.001) |

**Two of four cells significantly degraded.** This could be reported as evidence that harness engineering is unreliable. The author instead traced it to its source.

**Diagnosis**: A per-layer trace inspection showed that Tool Path Consistency, State Transition Stability, and Output Consistency were already at or near ceiling under both Baseline and Harness conditions. **The only remaining unconstrained axis was the free-text planning step** — the plan the agent emits before execution. The harness constrained the execution but not the plan wording, and since Reproducibility Rate matches exact traces, a single differing token in the plan text breaks an exact match. The harness concentrated measurement onto the one axis it had not yet constrained, producing apparently random direction effects — not genuine execution instability.

---

### Stage 2: Structured Planning Eliminates Variance Completely

| Task | Model | Harness+SP RR | Task Success |
|------|-------|--------------|-------------|
| finance_ecl | Qwen-2.5-7B | **0.980** | 0.98 |
| legal_clause | Qwen-2.5-7B | **1.000** | 1.00 |
| finance_ecl | Gemma-3-27B | **1.000** | 1.00 |
| legal_clause | Gemma-3-27B | **1.000** | 1.00 |

All four cells: p < 0.001 vs Baseline (permutation test). The one remaining non-perfect cell (Qwen/finance_ecl at 0.980) traces to two genuine per-state tool-calling failures — the model exhausted retries without calling the tool — a different failure mode unrelated to plan-text variance.

Both Stage 1 reversals (both `legal_clause` cells that degraded under plain Harness) vanish entirely under Harness+SP.

**Why it works**: Structured Planning converts free-text plan wording into a schema-validated structured representation. What gets logged is the canonical `(state, tool)` pairs, not raw model text. Free-text plan wording is mechanically removed as a variance source.

---

### Cost: Token Savings Are Universal, Latency Is Model-Dependent

| Task | Model | Tokens vs Baseline | Latency vs Baseline |
|------|-------|--------------------|---------------------|
| finance_ecl | Qwen-2.5-7B | -14.8% | **-14.2%** (faster) |
| legal_clause | Qwen-2.5-7B | -16.7% | **-24.7%** (faster) |
| finance_ecl | Gemma-3-27B | -15.9% | **+47.0%** (slower) |
| legal_clause | Gemma-3-27B | -16.5% | **+41.4%** (slower) |

**Token savings are universal** (−15–17% vs Baseline). The small planning overhead (2–5% extra tokens for the validation round trip) is dominated by the savings from structured tool selection reducing redundant calls.

**Latency is genuinely model-dependent**. Qwen mostly conforms to the plan schema on the first attempt, so Structured Planning adds minimal latency overhead — the model becomes faster overall. Gemma requires more frequent plan-validation retries, compounding its already higher base latency. This split strengthened when the sample size doubled, confirming it's a robust, model-specific effect, not noise.

**Practical implication**: "Should I deploy a harness?" is not a global yes/no. It's a per-model measurement decision.

---

### What the Paper Actually Contributes

**1. A first-pass harness can make your metrics look worse without being ineffective**  
Reason: the harness constrained tool sequences and state transitions — driving them to their ceiling — but left plan text unconstrained. Measurement then concentrated on the only free axis, producing apparently random effects. Fix: trace metrics per layer (plan / tools / state / output) to find which axis is driving variance, then constrain that axis.

**2. Structured Planning is the highest-leverage single harness component**  
It constrains not just execution but the representation of the plan itself, eliminating the last major variance source. For auditable systems, it also produces structured, schema-validated plan records rather than raw text.

**3. Latency cost must be measured per model, not assumed**  
Qwen gets faster; Gemma gets slower. The paper doubles the sample size to confirm this isn't noise. Any harness deployment decision on a tight latency budget requires empirical measurement before selecting the base model.

---

### Implications for Agent Builders

**Don't equate "adding constraints" with "improving reliability."** An incomplete harness can actively harm measured metrics. The correct approach: identify all variance sources, constrain axis by axis, measure the cost of each constraint.

**Evaluation frameworks need per-layer decomposition.** A single "reproducibility" metric conflates plan wording differences with genuine execution path divergences. Track plan-layer, tool-layer, state-layer, and output-layer consistency separately.

**Structured Planning is the priority implementation.** Token overhead is only 2–5%, but it eliminates free-text plan wording as a variance source and produces auditable structured logs.

**Limitations the author explicitly states**: Only linear four-state pipelines tested (not branching or judgment-based tasks); only 7B and 27B open-weight models (not closed-source or reasoning-specialized); latency measured through OpenRouter (third-party aggregation layer adds noise). Findings from this setting should not be assumed to generalize to complex branching agents or larger-scale models without independent validation.

---

**Links**

- arXiv:2608.26197: https://arxiv.org/abs/2608.26197
- PDF: https://arxiv.org/pdf/2608.26197

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
