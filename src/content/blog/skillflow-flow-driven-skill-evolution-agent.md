---
title: "SkillFlow：用流匹配信号驱动 Agent 技能自主进化，14 个基准全面超越"
titleEn: "SkillFlow: Flow-Driven Recursive Skill Evolution That Beats All Baselines on 14 Benchmarks"
description: "来自港中深、南大、南洋理工的研究：SkillFlow 用流匹配训练信号替代启发式 LLM 判断，让 Agent 自主管理技能库，平均提升 41.2% EM，计算成本降低 32-35%。"
descriptionEn: "SkillFlow from CUHK-Shenzhen, NUS, and NTU uses flow-matching training signals instead of heuristic LLM judgments to autonomously manage agent skill libraries, achieving +41.2% average EM with 32-35% lower compute cost."
pubDate: "2026-05-26"
updatedDate: "2026-05-26"
category: "Research"
tags: ["AI Agent", "强化学习", "技能进化", "流匹配", "LLM", "SkillFlow", "arXiv"]
heroImage: "../../assets/banner-personal-growth-ai-skills.jpg"
---

Agent 技能库该怎么管理？靠 LLM 自己判断"何时创建、何时剪枝"，往往退化成拍脑袋。SkillFlow 给出了一个基于流匹配训练信号的数学答案——在 14 个基准上全面超越现有方法，EM 平均提升 41.2%，计算成本反而降低了 32-35%。

> 📌 论文：SkillFlow: Flow-Driven Recursive Skill Evolution for Agentic Orchestration  
> arXiv:2605.14089 全文地址：https://arxiv.org/abs/2605.14089  
> 代码仓库：https://github.com/beita6969/SkillFlow  
> 项目主页：https://skill-flow.org

## 现有方法的三个根本问题

在 SkillFlow 之前，LLM Agent 的技能演化面临三个未被解决的系统性缺陷：

**1. 奖励最大化下的策略坍缩（Strategy Collapse）**  
传统 RL 训练会收敛到单一模式——明明存在多条同样有效的解题路径，但模型只保留了一条。这使得 Agent 对分布外任务非常脆弱。

**2. 梯度方差高 + 功劳归因不透明**  
多步骤任务中，哪一步的决策真正决定了最终成败？现有方法无法回答这个问题，信用分配只能靠模糊的整体奖励反向传播。

**3. 技能进化缺乏原则性信号**  
"何时创建新技能、在哪创建、创建什么"——这三个问题现有方法只能靠启发式 LLM 判断，没有来自训练数据的数学支撑。

## 核心方法：三个流匹配信号

SkillFlow 的架构由三部分组成：**可训练的 Supervisor Agent**（负责动作选择）、**冻结的 Executor**（执行委托推理和工具调用）、**动态技能库**（根据训练诊断自主演化）。

### 回火轨迹平衡（Tempered Trajectory Balance，TTB）

这是 SkillFlow 的核心创新。传统流匹配让轨迹概率等于归一化奖励，TTB 改为让轨迹采样**正比于奖励**而非收敛到单一最优策略。

效果：保留了多条同等有效的解题路径，对抗了策略坍缩。TTB 同时联合训练前向策略（动作选择）和后向策略（基于事后条件的诊断）。

### 步骤重要性 I(t)

从流比率中推导出每一步的重要性分数，直接指向"哪个决策真正驱动了成功"。**关键在于**：后向策略提供这个信号的成本为零——不需要额外推理，信用归因免费附带。

### 技能边际流 F̂(s)

通过累积生成函数对技能的贡献排序，量化每个技能在任务成功中的边际价值。三个诊断信号合并回答：

- **何时**进化（TTB 残差触发）
- **在哪**进化（步骤重要性定位）
- **进化什么**（技能边际流排名）

## 实验结果：14 个基准，全面超越

评测覆盖 7 个域内（IID）+ 7 个域外（OOD）基准，包括问答（HotpotQA）、数学推理（AIME）、代码生成（SWE-bench）、交互决策（WebShop、ALFWorld、ScienceWorld）。

主干模型为 Qwen3.5-9B，对比基线为 FlowSteer：

| 基准 | SkillFlow | FlowSteer | 提升 |
|------|-----------|-----------|------|
| HotpotQA EM | 92.19% | 61.88% | +30.31% |
| WebShop 成功率 | 93.75% | 55.94% | +37.81% |
| ALFWorld 成功率 | 96.09% | 74.22% | +21.87% |
| SWE-bench Resolved | 52.34% | 39.06% | +13.28% |
| **IID 平均 EM** | **94.14%** | **52.94%** | **+41.20%** |

同时，SkillFlow 实现了**所有基线中最低的计算成本**，token 用量和推理时间均下降 32-35%。准确性、多样性、效率三者同步优化，而非相互权衡。

### 消融实验验证了每个组件的独立价值

- **去掉 TTB**：多样性敏感任务（AIME、WebShop、ALFWorld）退化最严重，直接证明了模式坍缩是真实失败原因
- **去掉后向策略**：多步骤任务（AIME、WebShop、ScienceWorld）受损远大于事实类问答
- **去掉三个进化信号中的任意一个**：都独立导致性能下降

## 反直觉的发现

**OOD 优势反而更大**：在分布外任务上，SkillFlow 对 REINFORCE 基线的领先幅度大约是 IID 的 1.5 倍。冻结的进化后技能似乎捕捉到了"可迁移的编排原语"，而不是特定基准的模板。

**弱模型获益更多**：基础能力较弱的 LLM 从显式信用归因和多样性保留采样中获益比例更高。这意味着 SkillFlow 对算力受限场景特别有价值——它在某种程度上弥补了基础推理能力的不足。

## 资源与使用

项目代码已在 GitHub 开源，支持 Python 3.10 + LoRA 高效微调，提供与 OpenAI 兼容的本地推理接口。训练数据（3500 条，跨 7 个基准家族）和 Qwen3.5-9B 监督检查点均可在 Hugging Face 获取。

**作者团队**：Mingda Zhang（港中深）、Tiesunlong Shen（新加坡国立大学）、Haoran Luo（南洋理工大学）、Wenjin Liu（南洋理工大学）、Zikai Xiao（浙江大学）、Erik Cambria（南洋理工大学）、Xiaoying Tang（港中深）

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

How should an agent's skill library be managed? Letting an LLM decide heuristically when to create or prune skills often amounts to guesswork. SkillFlow provides a mathematically principled answer using flow-matching training signals — beating all baselines on 14 benchmarks with +41.2% average EM while simultaneously cutting compute costs by 32-35%.

> 📌 Paper: SkillFlow: Flow-Driven Recursive Skill Evolution for Agentic Orchestration  
> arXiv:2605.14089 full text: https://arxiv.org/abs/2605.14089  
> Code: https://github.com/beita6969/SkillFlow  
> Project: https://skill-flow.org

## Three Fundamental Problems with Existing Approaches

**1. Strategy Collapse Under Reward Maximization**  
Traditional RL training converges to a single mode. Multiple equally valid solution paths exist, but the model retains only one — making agents fragile on out-of-distribution tasks.

**2. High Gradient Variance and Opaque Credit Assignment**  
In multi-step tasks, which decision actually determined success? Existing methods can't answer this; credit assignment relies on blurry whole-trajectory reward backpropagation.

**3. Unguided Skill Evolution**  
When to create a new skill, where to focus, what to add — current methods rely on heuristic LLM judgments with no grounding in training-derived signals.

## Core Method: Three Flow-Matching Signals

SkillFlow's architecture combines a **trainable Supervisor Agent** (action selection), a **frozen Executor** (delegated reasoning and tool calls), and a **dynamic skill library** that evolves based on training diagnostics.

### Tempered Trajectory Balance (TTB)

TTB is the central innovation. Standard flow matching sets trajectory probability equal to normalized reward, converging to a single optimum. TTB instead samples trajectories **proportional to reward**, preserving multiple equally effective solution paths and countering strategy collapse.

TTB jointly trains a forward policy (action selection) and a backward policy (hindsight-conditioned diagnostics).

### Step Importance I(t)

Derived from flow ratios, this score identifies which specific decisions drove success. The key: the backward policy provides this signal **at zero additional inference cost** — transparent credit attribution comes for free.

### Skill Marginal Flow F̂(s)

Ranks each skill's contribution to task success via cumulant generating functions. The three diagnostics together answer:

- **When** to evolve (TTB residual floor triggers)
- **Where** to focus (step importance signals)
- **What** to add (skill marginal flow rankings)

## Results: 14 Benchmarks, Across the Board

Evaluation covers 7 in-distribution (IID) + 7 out-of-distribution (OOD) benchmarks including HotpotQA, AIME, SWE-bench, WebShop, ALFWorld, and ScienceWorld. Backbone: Qwen3.5-9B. Baseline: FlowSteer.

| Benchmark | SkillFlow | FlowSteer | Gain |
|-----------|-----------|-----------|------|
| HotpotQA EM | 92.19% | 61.88% | +30.31% |
| WebShop Success | 93.75% | 55.94% | +37.81% |
| ALFWorld Success | 96.09% | 74.22% | +21.87% |
| SWE-bench Resolved | 52.34% | 39.06% | +13.28% |
| **Average IID EM** | **94.14%** | **52.94%** | **+41.20%** |

SkillFlow also achieves **the lowest compute cost of all baselines** — 32-35% fewer tokens and less inference time. Accuracy, diversity, and efficiency improve simultaneously rather than trading off against each other.

### Ablations Validate Each Component

- **Removing TTB**: Largest degradation on diversity-sensitive tasks (AIME, WebShop, ALFWorld) — confirms mode collapse as the real failure mode
- **Removing the backward policy**: Multi-step tasks (AIME, WebShop, ScienceWorld) suffer more than factual QA
- **Removing any of the three evolution signals**: Each independently degrades performance

## Counterintuitive Findings

**OOD advantage widens**: SkillFlow's lead over REINFORCE baselines is roughly 1.5× larger on out-of-distribution tasks than on IID. The frozen evolved skills appear to capture transferable orchestration primitives rather than benchmark-specific templates.

**Weaker models gain more**: LLMs with weaker base reasoning benefit disproportionately from explicit credit attribution and diversity-preserving sampling — making SkillFlow particularly valuable for compute-constrained deployments.

## Resources

Code is open-sourced on GitHub, supporting Python 3.10 with LoRA fine-tuning and OpenAI-compatible local inference. Training data (3,500 records across 7 benchmark families) and the Qwen3.5-9B supervisor checkpoint are on Hugging Face.

**Authors**: Mingda Zhang (CUHK-Shenzhen), Tiesunlong Shen (NUS), Haoran Luo (NTU), Wenjin Liu (NTU), Zikai Xiao (Zhejiang University), Erik Cambria (NTU), Xiaoying Tang (CUHK-Shenzhen)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
