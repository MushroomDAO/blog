---
title: "LongStraw：在固定 GPU 预算下，把 RL 训练推到 200 万 token"
titleEn: "LongStraw: Million-Token RL Post-Training Beyond 2M Tokens on a Fixed GPU Budget"
description: "推理已经支持百万 token，但 RL 后训练卡在 256K 以下。LongStraw 用驻留状态 + 响应回放 + 分布式原生执行三项技术，在 8 张 H20 上完成 2M token 的精确 GRPO 训练。arXiv 2607.14952，已开源。"
descriptionEn: "Inference already handles million-token contexts, but RL post-training is stuck under 256K. LongStraw uses resident state, response replay, and distributed-native execution to achieve exact GRPO training at 2M tokens on 8× H20s. arXiv 2607.14952, open-source."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Research"
tags: ["RL训练", "长上下文", "GRPO", "大模型", "AI Agent", "GPU", "分布式训练", "后训练", "LLM"]
heroImage: "../../assets/images/longstraw-million-token-rl-training-gpu-banner.jpg"
---

> **论文**：arXiv 2607.14952 · cs.LG · 2026-07-16  
> **代码**：MindLab-Research/longstraw · GitHub · Python  
> **作者**：Changhai Zhou、Kieran Liu 等 20 人（MindLab Research）  
> **规模**：8×H20 完成 2,097,152 token GRPO；32×H20 完成 GLM-5.2 的 2M 执行

---

## 一、一个越来越大的差距

推理早就支持百万 token 上下文了。

但 RL 后训练（GRPO）还卡在 256K 以下。

这个差距在 AI Agent 场景里特别致命：Agent 的 observation、tool outputs、document、决策会在轨迹里不断堆积。训练时需要处理的历史长度和推理时一样长，但训练的显存压力远超推理。

根本原因是：**RL 训练不能像推理那样做 KV cache 然后丢图。**

GRPO 需要对同一历史下的多个响应计分，并反向传播。attention + 长时反向状态是主要的 GPU 显存瓶颈——训练图必须存在，不能丢。

LongStraw 解决的就是这个问题：**在固定 GPU 预算下，把 RL 后训练推到百万 token 级别。**

---

## 二、三项核心技术

### 1. Resident State（驻留状态）

> 只保留后续 token 需要的模型原生提示状态，不保留完整图。

推理阶段的 KV cache 可以直接丢图，因为不需要梯度。训练不行。

LongStraw 的解法是：不保存完整的 forward 图，只保存每层后续 token 真正需要的「模型原生提示状态」——这个状态量远小于完整图，但足够后续重建。

### 2. Response Replay（响应回放）

整个 GRPO 的核心循环变成：

```
1. 恢复驻留状态
2. 无图计算旧分支和参考分支（不需要梯度）
3. 在 autograd 下重建一条 policy 响应
4. 反向传播
5. 弹回到提示边界
```

这个设计的关键：只有一条 policy 响应需要 autograd，其余分支无图计算。这把显存需求从「所有响应的完整图」压缩到「一条响应的图 + 驻留状态」。

### 3. Distributed Model-Native Execution（分布式模型原生执行）

状态和梯度按所有权分配：
- context owner 负责上下文状态
- expert owner 负责 MoE 专家状态

同一组内共享状态，更新后按测量的 refresh policy 决定重捕获还是直接复用。

---

## 三、两套架构特化实现

LongStraw 是「objective 和 architecture-aware」的系统——不是一个通用方案，而是针对具体架构做了特化。

### Qwen3.6-27B（8×H20）

| 技术组件 | 说明 |
|---|---|
| Compact GDN state | 紧凑的全局状态表示 |
| CP8-sharded KV pages | 上下文并行 8 路分片的 KV 页 |
| Exact attention composition | 精确 attention 合成（不是近似） |
| Reverse block replay | 反向 block 回放顺序 |

**结果**：
- 2,097,152 positions（2M token）精确 GRPO，G=2 和 G=8 均完成
- 4,456,448-position prefix 支持 8 个 G=8 cycle（64 次回放），每 rank 83.894 GB

### GLM-5.2（32×H20）

| 技术组件 | 说明 |
|---|---|
| CPU-resident MLA/DSA state | MLA/DSA 状态放 CPU，不占 GPU 显存 |
| IndexShare-aware selection | 针对 IndexShare 的选择策略 |
| Top-8 MoE replay over CP32/EP32 | 32 路上下文并行 + 32 路专家并行的 top-8 回放 |

**结果**：
- 确定性 2M 执行 + 两次 78 层反向传播
- 与 vLLM-DAPO-Tinker/Megatron 真实训练循环的初步验证

---

## 四、数字

| 指标 | 数值 |
|---|---|
| 最大训练上下文 | 2,097,152 tokens（精确 GRPO） |
| 最大 prefix 长度 | 4,456,448 positions |
| Qwen 实验 GPU 数 | 8×H20 |
| GLM 实验 GPU 数 | 32×H20 |
| 每 rank 显存（Qwen 最大配置） | 83.894 GB |
| 回放次数（64 replays 实验） | 64 |
| 论文篇幅 | 46 页，10 图，11 表 |

---

## 五、设计判断

**关键洞察**：实际训练上下文的上限，**由驻留状态生命周期、回放策略和分布式所有权决定，而不是 attention kernel。** 过去优化长上下文训练主要在 attention 上做文章，LongStraw 指出真正的瓶颈在训练图管理层面。

**测量目标的边界**：论文明确说，测量目标是「response-only 执行」，不是「全序列梯度等价」。这是工程上的诚实表述——把反向传播限制在 response 部分，而不是整个序列，这在大多数 GRPO 场景下是合理的。

**架构感知而不是通用方案**：Qwen3.6-27B 和 GLM-5.2 的实现完全不同。MLA/DSA vs GDN，CP8 vs CP32/EP32，exact attention vs IndexShare-aware。不是一个放之四海而皆准的方案，而是根据每个架构的具体特性做特化——这是正确的工程取向。

**为什么现在重要**：AI Agent 的训练需求和对话模型不同，Agent 轨迹天然很长。如果 RL 训练只能处理 256K token，那针对长轨迹 Agent 的 RL 对齐实际上做不了。LongStraw 打开了这个大门。

---

## 六、局限

论文自己承认的几个点：

- GLM-5.2 实验的 vLLM-DAPO 集成部分是「初步验证」，真实大规模训练循环的稳定性还需要验证
- 测量目标是 response-only，不是全序列梯度等价——在某些场景下可能需要完整等价
- 实验在 H20 上，不同 GPU 架构的结果可能不同

---

## 七、代码

```bash
git clone https://github.com/MindLab-Research/longstraw
```

24 stars（2026-07-17 开源），Python 实现，无许可证声明。

论文 PDF：[arxiv.org/pdf/2607.14952](https://arxiv.org/pdf/2607.14952)

---

*数据来源：arXiv 2607.14952，2026-07-22 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: arXiv 2607.14952 · cs.LG · 2026-07-16  
> **Code**: MindLab-Research/longstraw · GitHub · Python  
> **Authors**: Changhai Zhou, Kieran Liu, and 20 others (MindLab Research)  
> **Scale**: 8×H20 for 2,097,152-token GRPO; 32×H20 for GLM-5.2 2M execution

---

## 1. A Growing Gap

Inference already supports million-token contexts.

But RL post-training (GRPO) is still stuck below 256K.

This gap is particularly fatal in AI Agent scenarios: an agent's observations, tool outputs, documents, and decisions accumulate continuously in the trajectory. The history length that must be processed during training is just as long as during inference, but the GPU memory pressure during training far exceeds that of inference.

The root cause is: **RL training cannot discard the computation graph after KV caching the way inference does.**

GRPO requires scoring multiple responses under the same history and backpropagating. Attention plus the long-lived backward state is the primary GPU memory bottleneck — the training graph must be retained, not discarded.

LongStraw solves precisely this problem: **pushing RL post-training to the million-token scale on a fixed GPU budget.**

---

## 2. Three Core Techniques

### 1. Resident State

> Retain only the model-native prompt state that subsequent tokens require — not the full computation graph.

During inference, the KV cache allows the graph to be discarded because no gradients are needed. Training does not permit this.

LongStraw's solution: instead of saving the complete forward graph, save only the "model-native prompt state" that subsequent tokens in each layer genuinely need — this state is far smaller than the full graph, yet sufficient for subsequent reconstruction.

### 2. Response Replay

The core GRPO loop becomes:

```
1. Restore resident state
2. Compute old branch and reference branch without graph (no gradients needed)
3. Reconstruct one policy response under autograd
4. Backpropagate
5. Pop back to the prompt boundary
```

The key insight of this design: only one policy response requires autograd; all other branches are computed without a graph. This compresses memory requirements from "full graphs for all responses" to "graph for one response + resident state."

### 3. Distributed Model-Native Execution

State and gradients are allocated by ownership:
- context owner is responsible for context state
- expert owner is responsible for MoE expert state

Within the same group, state is shared; after updates, a measured refresh policy determines whether to recapture or reuse directly.

---

## 3. Two Architecture-Specific Implementations

LongStraw is an "objective- and architecture-aware" system — not a general-purpose solution, but one specialized for specific architectures.

### Qwen3.6-27B (8×H20)

| Technical Component | Description |
|---|---|
| Compact GDN state | Compact global state representation |
| CP8-sharded KV pages | Context-parallel 8-way sharded KV pages |
| Exact attention composition | Exact attention composition (not approximate) |
| Reverse block replay | Reverse block replay ordering |

**Results**:
- 2,097,152 positions (2M tokens) exact GRPO, completed for both G=2 and G=8
- 4,456,448-position prefix supports 8 G=8 cycles (64 replays), 83.894 GB per rank

### GLM-5.2 (32×H20)

| Technical Component | Description |
|---|---|
| CPU-resident MLA/DSA state | MLA/DSA state on CPU, not occupying GPU memory |
| IndexShare-aware selection | Selection strategy targeting IndexShare |
| Top-8 MoE replay over CP32/EP32 | Top-8 replay with 32-way context parallelism + 32-way expert parallelism |

**Results**:
- Deterministic 2M execution + two 78-layer backpropagation passes
- Preliminary validation with vLLM-DAPO-Tinker/Megatron real training loop

---

## 4. Numbers

| Metric | Value |
|---|---|
| Maximum training context | 2,097,152 tokens (exact GRPO) |
| Maximum prefix length | 4,456,448 positions |
| Qwen experiment GPU count | 8×H20 |
| GLM experiment GPU count | 32×H20 |
| Memory per rank (Qwen max config) | 83.894 GB |
| Replay count (64-replays experiment) | 64 |
| Paper length | 46 pages, 10 figures, 11 tables |

---

## 5. Design Judgment

**Key insight**: The upper bound on practical training context is **determined by resident state lifetime, replay policy, and distributed ownership — not the attention kernel.** Prior efforts to optimize long-context training have focused primarily on attention; LongStraw identifies the real bottleneck as the training graph management layer.

**Boundaries of the measurement objective**: The paper explicitly states that the measurement objective is "response-only execution," not "full-sequence gradient equivalence." This is an honest engineering statement — restricting backpropagation to the response portion rather than the entire sequence is reasonable in most GRPO scenarios.

**Architecture-aware, not a universal solution**: The implementations for Qwen3.6-27B and GLM-5.2 are entirely different. MLA/DSA vs. GDN, CP8 vs. CP32/EP32, exact attention vs. IndexShare-aware. This is not a one-size-fits-all solution, but one specialized according to the specific characteristics of each architecture — and that is the correct engineering orientation.

**Why this matters now**: AI Agent training requirements differ from those of dialogue models; agent trajectories are inherently long. If RL training can only handle 256K tokens, RL alignment for long-trajectory agents is essentially impossible in practice. LongStraw opens this door.

---

## 6. Limitations

Points the paper itself acknowledges:

- The vLLM-DAPO integration portion of the GLM-5.2 experiment is "preliminary validation"; the stability of real large-scale training loops still requires verification
- The measurement objective is response-only, not full-sequence gradient equivalence — in certain scenarios, full equivalence may be required
- Experiments were conducted on H20s; results on different GPU architectures may differ

---

## 7. Code

```bash
git clone https://github.com/MindLab-Research/longstraw
```

24 stars (open-sourced 2026-07-17), Python implementation, no license declaration.

Paper PDF: [arxiv.org/pdf/2607.14952](https://arxiv.org/pdf/2607.14952)

---

*Data source: arXiv 2607.14952, collected 2026-07-22.*

© 2026 Author: Mycelium Protocol
