---
title: "Agents-A1：35B 追平万亿参数，路走得更长，不是模型堆得更大"
titleEn: "Agents-A1: How a 35B MoE Agent Matches 1T Models — Scale the Horizon, Not the Parameters"
description: "上海人工智能实验室（InternLM 团队）发布 Agents-A1（arXiv:2606.30616）：一个 35B MoE 模型，在长程 Agent 基准上与 Kimi-K2.6、DeepSeek-V4-pro、GPT-5.5 等万亿参数模型持平或超越。核心不是堆参数，而是把知识-行动轨迹拉到 45K tokens 平均长度（KAG 图 + 自博弈扩展），再用三阶段训练蒸馏六个领域专家进一个模型。SEAL-0 56.4、FrontierScience-Research 40.0（SOTA）。已开源 HuggingFace。"
descriptionEn: "Agents-A1 (arXiv:2606.30616, Shanghai AI Lab) is a 35B MoE agentic model that matches trillion-parameter systems (Kimi-K2.6, DeepSeek-V4-pro, GPT-5.5) on long-horizon benchmarks. The core insight: don't scale parameters — scale the agent horizon. A Knowledge-Action Graph (KAG) infrastructure connects evidence, actions, observations, and verifier outcomes into trajectories averaging 45K tokens. A proposer-solver-verifier self-play loop expands the graph into domain-specific supervision. Three-stage training distills six domain-expert teachers into one deployable model. SEAL-0: 56.4 (SOTA). FrontierScience-Research: 40.0 (SOTA). Open-sourced on HuggingFace."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Research"
tags: ["Agents-A1", "Agent训练", "长程Agent", "MoE", "上海AI实验室", "Knowledge-Action Graph", "自博弈"]
heroImage: "../../assets/images/agents-a1-35b-moe-horizon-scaling-guide-banner.jpg"
---

> **论文**: [arXiv:2606.30616](https://arxiv.org/abs/2606.30616) · **GitHub**: [InternScience/Agents-A1](https://github.com/InternScience/Agents-A1) · **HuggingFace**: [InternScience/Agents-A1](https://huggingface.co/collections/InternScience/agents-a1) · 上海人工智能实验室

---

## 一个直觉，一篇反驳

当前做通用 AI Agent 有一个流行直觉：**继续堆知识参数**。让模型更大，记住更多，推理能力更强，Agent 能力自然提升。

上海人工智能实验室的 Agents-A1 团队提出了一个不同的问题：

> 如果不堆更大的模型，而是把它经历的**知识-行动轨迹**拉得更长、更完整，会发生什么？

结果是 Agents-A1——一个 **35B MoE（专家混合）模型**，在 SEAL-0、HiPhO、FrontierScience-Olympiad/Research、IFBench 等长程 Agent 基准上，**追平甚至超越 Kimi-K2.6、DeepSeek-V4-pro、GPT-5.5 等万亿参数模型**。

---

## 核心论点：Horizon Scaling vs Parameter Scaling

论文标题说得很直接——**Scaling the Horizon, Not the Parameters**。

这里的"Horizon"不是视野，而是 **Agent 执行任务的轨迹长度**。传统训练数据里，一条训练样本可能是一个问答对，或者几轮对话。Agents-A1 的训练数据里，一条样本是一段完整的**长程 Agent 执行轨迹**，平均长度 **45K tokens**——包含：

- 搜索和检索操作
- 代码编写与执行结果
- 工具调用和返回
- 中间推理状态
- 最终答案和验证结果

这个长度是普通 SFT 数据的数十倍。问题是：**这样的数据从哪来？**

---

## Knowledge-Action Graph（KAG）：把"知道什么"和"做什么"连起来

传统知识图谱记录的是实体-关系三元组：`北京 → 首都 → 中国`。

KAG（知识-行动图）记录的是完整的行动过程——**证据是什么、动作是什么、观察到了什么、验证结果如何**。

形式化定义：KAG 是一个四元组 **G_d = (C_d, A_d, O_d, V_d)**：

| 分量 | 含义 | 具体内容 |
|---|---|---|
| **C_d** | 领域语料（domain corpus） | 证据片段、实体、事实、约束、上下文资源 |
| **A_d** | 动作空间（action space） | 工具调用、检索查询、代码编辑执行、推理步骤 |
| **O_d** | 观察空间（observation space） | 工具返回、检索到的证据、执行状态、中间产物 |
| **V_d** | 验证集（verifier set） | 正确性检查、证据支持、约束满足、目标完成度 |

图里的每一个节点是一条行动记录 `(s_t, a_t, o_t, v_t)`，边编码了"支持、依赖、产生、验证"关系。

**这和普通知识图谱的关键区别**：KAG 保留的是答案**如何被获取、验证、修正**的过程，而不只是最终结论。这意味着它同时保留了成功路径和失败路径——两者都是训练信号。

### 五种原子能力

KAG 里的能力按五种**原子能力（Atomic Abilities）**组织：

1. **信息获取**（information acquisition）
2. **工具调用**（tool calling）
3. **可执行迭代**（executable iteration）
4. **证据验证**（evidence verification）
5. **约束追踪**（constraint tracking）

长程任务是这五种原子能力的组合序列。把任务分解到这个粒度，才能对每一步做信用分配（credit assignment）——知道哪一步做对了、哪一步做错了。

---

## 自博弈扩展：Proposer-Solver-Verifier 三方博弈

静态的 KAG 只能覆盖已有数据。要让训练数据"自我生长"，Agents-A1 引入了**自博弈（self-play）图搜索与扩展**机制：三个 Agent 角色相互博弈，不断在 KAG 上生成新的训练样本。

| 角色 | 功能 |
|---|---|
| **π_P（Proposer）** | 在 KAG 中采样图区域，提出新的约束性任务 |
| **π_S（Solver）** | 用检索和工具解决这些任务，生成执行轨迹 |
| **π_V（Verifier）** | 验证答案、证据、轨迹、是否存在捷径风险 |

Verifier 的验收标准很严：一个新生成的任务 `x` 必须同时满足五条：
1. **可验证**：能对应到某个 V_d 里的验证器
2. **有效**：轨迹最终到达被验证器接受的答案
3. **过程信息量足够**：轨迹包含有意义的中间决策，不能是直接一步查出来的
4. **证据覆盖**：所需证据在轨迹中被实际使用
5. **无歧义**：任务表述清晰，没有捷径解法

只有通过验收的任务才会写回 KAG，失败的任务路由回去再做自博弈扩展。这个机制保证了**数据质量自动筛选**——不是人工标注，而是 Verifier 把关。

---

## 三阶段训练：六个领域专家，一个可部署模型

KAG 基础设施提供了六个领域的长程轨迹数据：

1. **长程搜索**（Web 信息检索，多跳推理）
2. **机器学习工程**（Kaggle 式代码优化，迭代提交）
3. **科学推理与研究**
4. **指令遵循**
5. **工具调用**
6. **通用 Agent 任务**

但六个领域直接混合训练会导致领域间互相干扰。Agents-A1 的解法是**三阶段训练**：

### 第一阶段：全领域 SFT

用六个领域的数据混合做监督微调，让模型对所有 Agent 行为有基础对齐。

### 第二阶段：领域级教师模型训练

每个领域单独训练一个**专家教师模型**，最大化领域内的专业能力：
- 搜索任务：强化学习（奖励多跳推理质量）
- ML 工程任务：强化学习（奖励代码执行分数）
- 科学推理：增强 SFT
- 指令遵循：强化学习（奖励精确约束满足）
- 工具调用：强化学习

### 第三阶段：多教师领域路由蒸馏 + 显著词汇对齐（SVA）

最关键的创新在这里。六个专家教师需要蒸馏进**一个**可部署的学生模型，而且蒸馏效果要足够好。

传统 on-policy distillation（OPD）只对"已采样到的 token"做损失，但这个单 token 近似存在问题——附近高概率的替代词不受约束，导致蒸馏不稳定。

**显著词汇对齐（Salient Vocabulary Alignment, SVA）** 的做法：不只对当前采样的 token 对齐，而是对教师模型认为"重要"的整个局部词汇表做对齐。配合**领域路由**——每次输入根据领域标签选择对应的专家教师来指导——蒸馏效率大幅提升。

---

## 基准表现：数字对比

Agents-A1 与 ~35B 量级的竞品和更大规模模型的对比（🥇= 全体 SOTA，🟢= 同量级最优）：

| 基准 | 类型 | Qwen3.6-35B | Kimi-K2.6 | DeepSeek-V4-pro | GPT-5.5 | **Agents-A1** |
|---|---|---|---|---|---|---|
| SEAL-0 | 长程搜索 | 38.74 | 50.45 | 54.95 | 42.34 | 🥇 **56.36** |
| GAIA | 长程搜索 | 78.64 | 80.58 | 98.06 🥇 | 87.38 | 🟢 **96.04** |
| HiPhO | 科学研究 | 37.7 | 41.1 | 38.7 | 43.3 | 🥇 **46.4** |
| FrontierScience-Olympiad | 科学研究 | 60.3 | 73.0 | 76.0 | 78.0 | 🥇 **79.0** |
| FrontierScience-Research | 科学研究 | 2.9 | 17.9 | 13.3 | 26.7 | 🥇 **40.0** |
| IFBench | 指令遵循 | 64.4 | 71.77 | 73.47 | 75.9 | 🥇 **80.61** |
| IFEval | 指令遵循 | 91.3 | 94.45 | 93.35 | 93.35 | 🥇 **94.82** |
| BrowseComp | 长程搜索 | 67.93 | 83.2 | 83.4 | 84.4 🥇 | 🟢 **75.51** |
| MolBench-Bind | 科学 Agent | 48.7 | 21.6 | 37.8 | 62.2 🥇 | 🟢 **56.8** |

特别值得注意的是 **FrontierScience-Research（40.0）**——这是一个要求真正执行科学研究任务的基准，Agents-A1 比 GPT-5.5（26.7）高出 50%，比 Kimi-K2.6（17.9）高出 1 倍以上。这一项最能体现"轨迹长度"的价值——真实科研任务需要多轮迭代、验证、修正，正是 KAG 训练数据的优势场景。

---

## 怎么用

模型已开源，在 HuggingFace 可直接下载：

```bash
# SGLang（推荐，速度最快）
uv pip install sglang
python -m sglang.launch_server \
  --model-path InternScience/Agents-A1 \
  --port 8000 \
  --tp-size 1 \
  --context-length 262144 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder    # 启用工具调用
```

```bash
# vLLM
uv pip install vllm --torch-backend=auto
vllm serve InternScience/Agents-A1 \
  --port 8000 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

上线后走标准 OpenAI API 接口。量化版本（4-bit、6-bit 等）已由 mlx-community 发布，Mac 可以直接跑。

**262K context 长度**——对应 KAG 训练数据 45K 平均轨迹，生产场景的长程任务有足够空间。

---

## 为什么这个方向值得关注

Agents-A1 的技术路线有一个工程含义：**Agent 能力的瓶颈可能不在模型参数量，而在训练数据的"过程密度"**。

当前主流的 SFT 数据大多是结果导向的——给问题，给答案。KAG 的思路是把**整个解题过程**——包括中间失败、验证、修正——全部作为训练信号。这和人类学习的方式更接近：不只是看答案，而是经历整个解题过程。

对做 Agent 的开发者来说，这意味着：如果你在构建一个特定领域的 Agent（代码、科研、法律、医疗），不一定要去找更大的基础模型，也可以考虑为你的任务领域构建更高质量的**过程级轨迹数据**。

---

> **下载**：[HuggingFace: InternScience/Agents-A1](https://huggingface.co/collections/InternScience/agents-a1) · **ModelScope** · [GitHub](https://github.com/InternScience/Agents-A1)  
> **论文**：[arXiv:2606.30616](https://arxiv.org/abs/2606.30616) · Agents-A1 Team, 上海人工智能实验室

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Agents-A1 (arXiv:2606.30616, Shanghai AI Lab) is a 35B MoE model that matches trillion-parameter systems on long-horizon agent benchmarks. The key: don't scale parameters, scale the agent horizon. A Knowledge-Action Graph (KAG) infrastructure structures evidence, actions, observations, and verifier outcomes into trajectories averaging 45K tokens. A proposer-solver-verifier self-play loop generates and validates new training tasks from the graph. Three-stage training (full-domain SFT → domain-level teacher training → multi-teacher on-policy distillation with salient vocabulary alignment) compresses six domain experts into one model. SEAL-0: 56.4 SOTA. FrontierScience-Research: 40.0 SOTA (vs GPT-5.5 26.7, Kimi-K2.6 17.9). Open-sourced on HuggingFace with quantized MLX variants for Mac.

---

## What Is Horizon Scaling?

The claim: agent capability is bottlenecked not by model parameters but by the *density* of process-level supervision in training data. A typical SFT sample is a (question, answer) pair. A KAG trajectory is a full execution trace — evidence retrieved, tools called, code executed, intermediate states observed, verifications run — averaging 45K tokens per sample. Training on processes rather than just outcomes is what lets a 35B model match 1T.

## The Knowledge-Action Graph

KAG = G_d = (C_d, A_d, O_d, V_d): domain corpus × action space × observation space × verifier set. Each node is an action record (state, action, observation, verification outcome). Edges encode support, dependency, production, and verification relations. Unlike a conventional knowledge graph (entity-relation triples), a KAG preserves both successful and failed trajectories — both are training signal, enabling cross-step credit assignment.

Five atomic abilities: information acquisition, tool calling, executable iteration, evidence verification, constraint tracking.

## Proposer-Solver-Verifier Self-Play

Three agents expand the KAG automatically. The Proposer samples graph regions and proposes constrained tasks. The Solver executes with tools and retrieval. The Verifier rejects any sample that fails five criteria: verifiable, valid, process-informative (no single-step shortcut), evidence-covering, unambiguous. Rejected tasks route back to self-play. Only accepted tasks enter the training pipeline.

## Three-Stage Training

Stage 1: Full-domain SFT across all six domains. Stage 2: Independent RL/SFT teacher models per domain (search: RL; ML engineering: RL; science: enhanced SFT; instruction following: RL; tool calling: RL). Stage 3: Multi-teacher domain-routed on-policy distillation with Salient Vocabulary Alignment (SVA) — align student to a compact teacher-supported local vocabulary rather than a single sampled token, improving distillation stability across heterogeneous domains.

## Run It

```bash
python -m sglang.launch_server \
  --model-path InternScience/Agents-A1 \
  --context-length 262144 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder
```

Quantized MLX variants available for Mac via mlx-community.

**Links**: [arXiv:2606.30616](https://arxiv.org/abs/2606.30616) · [GitHub](https://github.com/InternScience/Agents-A1) · [HuggingFace](https://huggingface.co/collections/InternScience/agents-a1)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
