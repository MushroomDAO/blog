---
title: "模型可以小，脚手架要聪明——CMU 论文拆解：用 Harness 适配让 SLM 以 4% 成本追平 LLM"
titleEn: "Models Can Be Small if the Scaffold Is Smart: CMU on Closing the SLM–LLM Gap at 4% of the Cost"
description: "卡内基梅隆大学最新论文（arXiv:2607.08938）证明：对于重复性业务任务，小模型（3B~30B active params）配合针对性适配的 harness，可以用 4% 的成本恢复 89.7% 的 LLM 性能。本文深度分析论文框架，提炼 5 条工程上可直接落地的操作指南。"
pubDate: 2026-07-27
heroImage: "../../assets/images/cmu-better-harnesses-smaller-models-slm-agent-cost-reduction-engineering-banner.jpg"
category: "Research"
tags: ["Agent", "SLM", "Harness", "成本优化", "工程实践", "LLM", "CMU"]
---

> "用便宜的模型不够，但围绕模型的脚手架重新适配后，情况就不一样了。"
>
> — Chenyang Yang et al., Carnegie Mellon University, arXiv:2607.08938

2026 年，部署 Agent 的真实成本正在成为一个严肃的工程问题。CMU 团队用 7 个业务任务、3 个 SLM 家族、21 组任务-模型配对做了系统性实验，给出了一个清晰的答案：

**89.7% 的 LLM 性能，4% 的成本。**

代价：需要针对每个任务-模型组合，把 harness 重新适配一遍。

---

## 核心洞察：任务难度可以从模型转移到 harness

传统思路是"换更大的模型"。这篇论文的反向思路是：

> **许多任务的复杂度在实例间是共享的，可以从模型里抽出来，放进 harness 里——通过定制化的指令、工具和编排循环。**

换句话说，大模型做得好，不一定是因为它"更聪明"，而是因为通用 harness 里很多模糊性都靠模型的通用能力硬撑过去了。当你把这些模糊性明确化——写进系统提示、封装成工具、加进 hook——小模型就能跟上来。

**预算审批案例**：

- LLM（gemini-3.1-pro）+ 通用 harness：97.3% 准确率，$0.22/次
- SLM（gemma-4-26b-a4b）+ 通用 harness：75.0%，~~明显不够用~~
- SLM + 适配后的 harness：98.3%，$0.018/次（**8% 的成本，更高的准确率**）

适配内容：系统提示重写成逐步工作流、工具集从 6 个过滤到 5 个、加了一个反循环 Python Hook。23 次迭代，meta-agent 自动完成。

---

## 失败模式分类：知道哪里出错才能对症下药

CMU 把 Agent 失败按能力维度分成 5 类：

| 失败类型 | 典型表现 | 出现频率 |
|---|---|---|
| **指令跟随** | 违反系统提示要求、输出格式错误 | 81% 的成功适配涉及此项 |
| **知识缺口** | 缺少领域知识、环境假设错误 | 81% |
| **工具使用** | 选错工具、调用格式错误、工具组合失败 | 主要来源 |
| **长上下文** | 遗忘早期指令、重复已失败的动作 | 62% |
| **规划推理** | 无法分解目标、遇到新情况不会重规划 | 33% |

关键发现：**指令跟随和知识缺口是主要失败来源，而不是推理能力**。这对工程实践很重要——这两类问题都可以通过 harness 来缓解，不需要更大的模型。

---

## Harness 适配策略三板斧

**① 上下文适配（Context Adaptations）**

出现在 86% 的成功适配中，是最常用、最直接的策略：

- 外化隐式知识（把"你应该知道的"写进系统提示）
- 把高层目标分解成显式的步骤计划
- 为工具调用提供更详细的描述和示例
- 强化关键约束（让模型不容易"忘记"）

但要注意：上下文越多，指令跟随和长上下文问题反而可能恶化。需要主动管理：渐进式展示、压缩摘要、过滤无关观察。

**② 工具适配（Tool Adaptations）**

出现在 43%（创建工具）和 29%（管理工具）的成功适配中：

- **包装工具**：把复杂的工具调用序列包装成单一接口，小模型更容易调用
- **过滤工具集**：从 40+ MCP 工具过滤到 7 个，让选择变简单
- **适配工具 schema**：让工具描述更直观、更贴近模型的理解方式

**工具集越大，小模型越容易选错。** 过滤本身就是性能优化。

**③ Agent Loop 适配（Loop Adaptations）**

- **插入 Hook**：在特定工具调用前后触发确定性检查，程序化强制约束
- **循环检测**：检测相同操作重复超过阈值，强制触发恢复逻辑
- **多智能体拆分**：把长上下文任务拆成独立 agent，各司其职

注意：在这次实验中，子 agent 方案没有成功案例——SLM 无法可靠地协调和追踪子 agent 的进度。这是一个当前 SLM 的实际限制。

---

## 5 条工程落地指南

以下 5 条来自论文的实验结论，可以直接指导 Agent 工程决策：

### 指南 1：先评估任务多样性，再决定是否值得适配

论文发现任务多样性与适配收益之间存在极强的负相关（Spearman ρ = -0.96）：

| 任务特征 | 适配后准确率 | 典型任务 |
|---|---:|---|
| 低多样性（实例共享固定工作流） | ~89% | 考勤审核、预算审批 |
| 高多样性（实例需要不同策略） | ~68% | 代码重构 |

**落地方式**：用 LLM 先跑 20-30 条样本轨迹，提取工具调用序列，计算两两 Levenshtein 距离的平均值。距离 < 0.3 的任务适合投入适配；距离 > 0.6 的任务，适配的 ROI 可能不够好。

**结论**：适配不是万能药，高度开放的创意任务或分支极多的任务效果有限，先做任务特征评估。

### 指南 2：按失败模式分类，再选对应策略

不要随机加提示或工具。失败有成因，策略有对应：

```
失败: 模型选错工具（工具集太大）
→ 策略: 过滤工具集 + 为常用序列包装高层工具

失败: 模型忘记约束条件（指令跟随）
→ 策略: 添加上下文（强化约束）+ Hook 程序化检查

失败: 模型缺少领域知识（知识缺口）
→ 策略: 外化知识进系统提示 + 工具 schema 内嵌约定

失败: 模型陷入循环（长上下文）
→ 策略: 反循环 Hook + 上下文压缩/剪枝

失败: 模型无法分解复杂目标（规划）
→ 策略: 系统提示里直接给出步骤计划
```

**落地方式**：先收集 20 条失败轨迹，按上述分类手动标注（或用 LLM 辅助标注）。再根据频率最高的 2-3 类失败类型选适配策略。

### 指南 3：程序化 Hook > 依赖模型自我纠正

论文里最漂亮的工程案例是这段 Python hook：

```python
# anti_loop_hook.py
if tool_name == "send_message":
    if recipient in msgs and msgs[recipient] == message:
        return {
            "decision": "deny",
            "reason": "ERROR: 你在给同一个收件人发完全相同的消息。停止。"
        }
```

这个 hook 捕获的失败模式是 SLM 陷入循环——对同一收件人重复发完全相同的消息。

**关键原则**：任何有明确不变式的约束，都应该用代码 enforce，而不是期待模型"意识到"。

常见可以 hook 化的约束：
- 禁止重复操作（同样的输入/输出组合出现 N 次）
- 强制输出格式（正则或 JSON schema 验证）
- 边界检查（金额、数量的合理范围）
- 状态机约束（特定操作只能在特定状态后触发）

### 指南 4：选 MoE 小模型作为 SLM 候选

论文对比了三个 SLM：

| 模型 | Active Params | 适配后平均表现 | 提升幅度 |
|---|---|---|---|
| gemma-4-26b-a4b | ~4B active | 最高 | +48.8% |
| qwen3-coder-30b-a3b | ~3B active | 中等 | 中等 |
| ministral-3-8b | 8B | 最低 | +15.5% |

**MoE（Mixture-of-Experts）架构的 SLM 是最优候选**——active 参数少（推理成本低），total 参数多（能力保留），对 harness 适配的响应度最高。

选模型的实践原则：
1. 优先选有强 tool-use 基础训练的模型（benchmark 分数高的 SLM）
2. MoE 优于 dense，同等 active params 下能力更强
3. 模型要有足够基础能力——能力太弱的模型，harness 无论怎么适配也回天乏力（+15.5% vs +48.8%）

### 指南 5：自动化适配，meta-agent 找 harness

手工调整 harness 成本太高，论文验证了自动化路径：

**优化器架构**：
```
输入: SLM + 任务 + 训练数据（20条）+ 初始 harness
↓
遗传搜索（GEPA 风格）从 Pareto 前沿采样候选
↓
Meta-agent（frontier LLM）分析失败轨迹，提议改动
↓
沙盒验证 → 如果改善则更新候选池
↓
输出: 优化后的 harness（23 次迭代，$20 预算）
```

**工程关键点**：
- Meta-agent **必须用 frontier LLM**（gemini-3.1-pro 级别），用便宜模型诊断质量太差
- 给 meta-agent 喂**原始 JSON 轨迹**，不要处理成 markdown（会丢失有效信息）
- 保留**搜索记忆**（已试过什么、效果如何），防止 meta-agent 反复尝试同样无效的改法
- 跑**多次独立搜索**（3 次）而不是一次长搜索，覆盖更大的设计空间

**成本测算**：$20 优化一个任务-模型对，平均 13 次使用后摊销回来。高频业务任务第一天就能回本。

---

## 论文中重要的两个边界条件

**边界 1：子 agent 路线目前走不通**

在 21 组实验里，没有一组成功的适配包含多子 agent 编排——因为 SLM 无法可靠地追踪和协调子 agent 的工作。这不代表这个方向永远不行，但它是现阶段 SLM 的实际上限。

**边界 2：harness 不能跨模型复用**

qwen3-coder 的最优 harness 对 ministral-3-8b 无效，反之亦然。每个模型有自己的失败模式（qwen3 偶尔发 XML 而不是 JSON，ministral 在文件编辑工具上有问题）。迁移到新模型，优化要重跑。

---

## 总结

这篇论文的价值不只是一个"可以用小模型省钱"的结论，而是提供了一个**系统性的分析框架**：

- 把失败按能力维度分类
- 把适配策略按 harness 组件分类
- 把二者之间的映射关系明确化

然后再用 meta-agent 自动搜索这个空间。

**核心迁移给工程师的判断逻辑**：

> 在你的任务里，有多少"困难"是重复出现的，可以被写死在 harness 里的？越多，小模型越有机会。越少（每个实例都是全新挑战），就老老实实用大模型。

---

**论文**: arXiv:2607.08938  
**代码**: [github.com/malusamayo/migration-analysis](https://github.com/malusamayo/migration-analysis)  
**作者**: Chenyang Yang, Xinran Zhao, Tongshuang Wu, Christian Kästner（CMU）

<!--EN-->

## Small Models Can Work — But the Harness Has to Be Smart: CMU's 90% Cost Reduction Framework

> "Swapping a small model in is not enough. Adapting the harness around the model is what changes the equation."
>
> — Chenyang Yang et al., Carnegie Mellon University, arXiv:2607.08938

**89.7% of LLM performance. 4% of LLM cost.**

This is the headline from CMU's new paper on automated harness adaptation across 7 business tasks and 21 task-model pairs. The paper gives a clear, systematic answer to a question every serious agent deployment team is asking: can we replace frontier LLMs with cheaper models without destroying performance?

Yes — but the harness has to be adapted first.

---

## The Core Insight

> **Much of task difficulty is shared across instances and can be lifted from the model into the harness via tailored instructions, tools, and orchestration loops.**

Frontier LLMs perform well on general-purpose harnesses because they use raw reasoning ability to handle ambiguity. But for routine business tasks, that ambiguity is predictable — you can make it explicit in the harness (system prompt structure, tool design, loop constraints), and suddenly the small model can keep up.

**Budget approval example:**

- LLM (gemini-3.1-pro) + generic harness: 97.3% accuracy, $0.22/run
- SLM (gemma-4-26b-a4b) + generic harness: 75.0% — not good enough
- SLM + **adapted harness**: 98.3% at $0.018/run — **8% cost, higher accuracy**

Adaptation: system prompt rewritten as step-by-step workflow, tool set filtered from 6 → 5, anti-loop Python hook added. 23 iterations. Meta-agent automated the whole search.

---

## Five Failure Modes, Mapped to Fixes

| Failure Type | What It Looks Like | % of Successful Adaptations |
|---|---|---:|
| Instruction-following | Violates constraints, wrong output format | 81% |
| Knowledge gaps | Missing domain knowledge, wrong assumptions | 81% |
| Tool-use | Wrong tool, malformed call, bad composition | Primary source |
| Long-context | Forgets earlier instructions, repeats failed actions | 62% |
| Planning/reasoning | Can't decompose goals, fails to replan | 33% |

Key finding: **instruction-following and knowledge gaps dominate, not reasoning ability**. Both are addressable through the harness.

---

## Three Categories of Harness Adaptation

**Context adaptations (86% of successful adaptations)**
- Externalize implicit knowledge into prompts
- Turn high-level goals into explicit step-by-step plans
- Add detailed tool descriptions and examples
- Reinforce key constraints that models tend to forget

Trade-off: more context can worsen long-context and instruction-following failures. Manage with progressive reveal, compression, pruning.

**Tool adaptations (43% create, 29% manage)**
- Wrap complex tool sequences into simpler high-level interfaces
- Filter the tool set aggressively (40+ tools → 7 in one case)
- Adapt tool schemas to be more model-friendly

**Loop adaptations**
- Insert hooks: deterministic Python checks before/after specific tool calls
- Loop detection: detect repeated identical actions → force recovery
- Multi-agent split: isolate long-context burden into sub-agents (note: SLMs currently struggle with sub-agent coordination)

---

## 5 Engineering Guidelines

### Guideline 1: Measure Task Diversity Before Committing to Adaptation

The paper found a nearly perfect negative correlation (Spearman ρ = -0.96) between task diversity and adaptation gains:

- Low-diversity tasks (instances share a stable workflow): adapted SLMs reach ~89% accuracy
- High-diversity tasks (instances require distinct strategies): drops to ~68%

**How to measure**: run 20-30 LLM trajectories on sample instances, extract tool-call sequences, compute average pairwise normalized Levenshtein distance. Low distance = good candidate for adaptation.

### Guideline 2: Diagnose First, Adapt Second

```
Tool-use failures (large tool set) → Filter tools + wrap sequences
Instruction-following failures    → Reinforce in prompt + add hooks
Knowledge gaps                    → Externalize into system prompt
Long-context failures             → Anti-loop hook + context pruning
Planning failures                 → Prescribe step-by-step workflow in prompt
```

Collect 20 failure trajectories. Label them by type. Prioritize the top 2-3 failure modes. Don't guess — diagnose.

### Guideline 3: Hook > Trust the Model to Self-Correct

The budget approval task's anti-loop hook:

```python
# anti_loop_hook.py
if tool_name == "send_message":
    if recipient in msgs and msgs[recipient] == message:
        return {"decision": "deny", "reason": "Identical repeat. Stop."}
```

**Principle**: any constraint that has an unambiguous invariant should be enforced in code, not left to model judgment.

Common hook targets: duplicate action detection, output format validation, value range checks, state machine constraints.

### Guideline 4: Use MoE SLMs as Your Candidate Models

| Model | Active Params | Avg Improvement |
|---|---|---:|
| gemma-4-26b-a4b (MoE) | ~4B active | +48.8% |
| qwen3-coder-30b-a3b (MoE) | ~3B active | Medium |
| ministral-3-8b (dense) | 8B | +15.5% |

MoE models: low inference cost (few active params), high capability (many total params), best response to harness adaptation. Use benchmark scores (Artificial Analysis) as a proxy for "harness compatibility."

Models with weak base capabilities see poor adaptation gains (+15.5%) — the harness can't compensate for missing core abilities.

### Guideline 5: Automate with a Meta-Agent Optimizer

Manual harness engineering doesn't scale. The paper's optimizer loop:

```
Input: SLM + task + 20 training examples + initial harness
→ Genetic search (GEPA-style) samples from Pareto front
→ Meta-agent (frontier LLM) inspects trajectories, proposes edits
→ Sanity check → Evaluate → Update pool if improved
→ Output: optimized harness (~23 iterations, $20 budget)
```

Critical implementation notes:
- **Meta-agent must be a frontier LLM** — cheaper models produce poor diagnoses, net negative
- **Feed raw JSON traces** to the meta-agent, not processed markdown (information loss hurts)
- **Maintain search memory** so the meta-agent doesn't rediscover the same failed fixes
- **Run 3 independent searches** rather than one long one — covers more of the design space

Cost math: $20 to optimize one task-model pair, recovered after 13 agent runs on average. High-frequency business tasks pay back on day one.

---

## Two Hard Limits

**Sub-agent orchestration doesn't work yet.** Zero successful adaptations used multi-agent coordination — current SLMs can't reliably track sub-agent progress. This may improve with future models, but it's an active ceiling today.

**Harnesses don't transfer across models.** The optimized harness for qwen3-coder fails for ministral-3-8b and vice versa — each model has different failure signatures. Migrating to a new model means re-running the optimizer.

---

## What to Take Away

The paper's core transfer for engineering teams:

> How much of your task's difficulty repeats predictably across instances? If most of it does — you can encode it in the harness. If each instance is a unique open-ended challenge — stick with the frontier LLM.

The framework is: characterize failures → map to harness strategies → automate the search. The SLM is the executor. The harness is where the intelligence lives.

**Paper**: arXiv:2607.08938  
**Code**: [github.com/malusamayo/migration-analysis](https://github.com/malusamayo/migration-analysis)  
**Authors**: Chenyang Yang, Xinran Zhao, Tongshuang Wu, Christian Kästner (CMU)
