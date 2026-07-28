---
title: "Kimi K3 技术深析：KDA、Stable LatentMoE 与首个开源 3T 级模型"
description: "Kimi K3 是全球首个开源 2.8T 参数模型，同步发布权重与技术报告。本文结合 GitHub 通讯仓库与 HuggingFace 权重仓库，深析 Kimi Delta Attention（KDA）、Stable LatentMoE（16/896 专家）、MXFP4 量化感知训练等核心架构创新，以及 AgentENV 训练基础设施的技术联系。"
pubDate: "2026-07-28"
category: "Research"
heroImage: "../../assets/images/kimi-k3-technical-analysis-architecture-training-open-frontier-banner.jpg"
---

2026 年 7 月 27 日，Moonshot AI 做了一件事：同步开放 Kimi K3 的模型权重和技术报告。

权重在 HuggingFace（`moonshotai/Kimi-K3`），技术报告在 GitHub（`MoonshotAI/Kimi-K3`）。

这是全球第一个开源的 3T 级模型——2.8T 总参数，104B 激活参数。

本文结合两个仓库，做一次完整的技术解读。

---

## 一、两个仓库

**通讯仓库（GitHub）**：`MoonshotAI/Kimi-K3`  
架构细节、Benchmark 表格、部署指南、技术报告 PDF（`k3_tech_report.pdf`）

**权重仓库（HuggingFace）**：`moonshotai/Kimi-K3`  
正式模型权重，Kimi K3 License，支持 vLLM / SGLang / TokenSpeed 推理

两个仓库的 README 内容基本一致，但 GitHub 侧的技术报告是完整版本。

---

## 二、架构概览

| 参数 | 数值 |
|---|---|
| 总参数量 | 2.8T |
| 激活参数量 | 104B |
| 层数 | 93（1 Dense + 92 MoE） |
| 注意力层构成 | 69 KDA + 24 Gated MLA |
| 注意力隐层维度 | 7168 |
| 注意力头数 | 96 |
| 专家数 | 896，每 token 激活 16 个 |
| 共享专家数 | 2 |
| LatentMoE 维度 | 3584 |
| 每专家隐层维度 | 3072 |
| 词表大小 | 160K |
| 上下文窗口 | 1M token（1,048,576） |
| 视觉编码器 | MoonViT-V2（401M） |
| 量化方式 | MXFP4 权重 / MXFP8 激活（QAT） |
| 激活函数 | SiTU-GLU |

---

## 三、核心架构创新

### 3.1 Kimi Delta Attention（KDA）

KDA 是 K3 的主体注意力机制，承载 93 层中的 69 层。

传统注意力在长序列下的信息流动效率下降是已知问题——每个位置的注意力计算都在"全量竞争"。KDA 的核心思路是引入差分（Delta）机制，改变信息跨序列的流动方式，提高超长上下文下的信息传播效率。

从 GitHub 技术报告中可以看到，KDA 还带来了一个工程难题：**常规的 Prefix Caching 不适用**。为此，Moonshot 向 vLLM 社区贡献了对应实现，即将随权重一起发布。

### 3.2 Attention Residuals（AttnRes）

AttnRes 不是标准的残差连接。它在深度维度上选择性地检索表征，而不是均匀累积。

直觉理解：深层的注意力头不仅看当前层的输出，还可以选择性地"拉取"更早层的表征。这让信息流动从线性的"层叠"变成了带选择性的"跨层检索"。

技术报告的 GPU 内核优化案例有一个细节：Kimi K3 自身在 K3 开发后期，被用于完成大量的 AttnRes 内核优化工作——模型在用自身能力优化自己的运行效率。

### 3.3 Stable LatentMoE：16/896 的极稀疏 MoE

Kimi K3 的专家激活率：16/896 ≈ 1.79%。

这是一个极高的稀疏度。传统 MoE 通常激活 1/8 到 1/4 的专家，K3 把这个比例压到了 1.8%。

稀疏到这个程度会有两个工程挑战：

**挑战一：路由不稳定**  
传统 Top-K 路由在极低激活率下容易出现某些专家被过度选择（热点）而其他专家几乎不被使用的问题。

K3 的解法：**Quantile Balancing**——从路由器分数的分位数直接推导专家分配，消除了基于启发式的更新规则和敏感的平衡超参数。

**挑战二：专家并行的 shape 不对齐**  
大规模专家并行训练中，不同 batch 激活的专家数量不同，导致静态 shape 的硬件利用率不均。

K3 的解法：**全平衡专家并行训练**——静态 shape，关键路径上无 host 同步，保证吞吐。

### 3.4 Per-Head Muon

传统 Muon 优化器在 attention 维度上做统一优化。Per-Head Muon 为每个注意力头独立优化，在 2.8T 参数规模下实现了更自适应的学习动态。

### 3.5 Gated MLA

24 层 Gated MLA（相对于 K2 的 MLA）引入了门控机制，提升了注意力的选择性。结合 SiTU-GLU 激活函数，在激活控制上比 K2 有所进步。

---

## 四、MXFP4 量化感知训练

K3 从 SFT 阶段开始就使用量化感知训练（QAT）：

- 权重：MXFP4（4-bit MX Float）
- 激活：MXFP8（8-bit MX Float）

这不是后训练量化（PTQ），而是让模型在训练时就学会适应量化带来的精度损失。

意义：开源权重本身就是量化后的版本，部署时不需要额外的量化步骤，硬件兼容性更广。

部署建议：K3 的 KDA 架构推荐在 **64 个加速器以上的 supernode 配置**上运行，这与其超大规模的专家并行设计有关。

---

## 五、与 AgentENV 的技术联系

本月早些时候，Moonshot 开源了 AgentENV（`kvcache-ai/AgentENV`）——驱动 K3 训练的 RL 沙箱基础设施。

K3 的 Agentic RL 训练需要大规模并行的沙箱执行环境：代码解释器、工具调用、终端环境。AgentENV 用 Firecracker microVM + overlaybd + ublk 解决了冷启动（<50ms）、弹性伸缩和资源回收问题。

**重要的时序关系**：先有 AgentENV（RL 训练基础设施），才有 K3 的 Agentic 能力。AgentENV 开源意味着外部团队可以用相同的训练基础设施来复现或改进 K3 的 Agentic RL 训练范式。

---

## 六、Benchmark 关键数据

对比模型：Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5、GLM-5.2

### 长程编码（Kimi K3 的核心优势区）

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol | Opus 4.8 |
|---|---|---|---|---|
| SWE-Marathon | **42.0** | 35.0 | 39.0 | 40.0 |
| Terminal-Bench 2.1 | **88.3** | 88.0 | 88.8 | 84.6 |
| ProgramBench | **77.8** | 76.8 | 77.6 | 71.9 |
| FrontierSWE | 81.2 | **86.6** | 71.3 | 66.7 |
| DeepSWE | 67.5 | **70.0** | **73.0** | 59.0 |

SWE-Marathon 是长程任务（24 小时无监督），K3 以 42.0 领先，Fable 5 fallback 率 35%。

### Agentic 能力

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| BrowseComp | **91.2** | 88.0 | 90.4 |
| DeepSearchQA (F1) | **95.0** | 94.2 | — |
| Agents' Last Exam | 各平台数据 | — | — |

### 多模态

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| Video-MME (w. sub) | **90.0** | — | 89.5 |
| OmniDocBench | **91.1** | 89.8 | 85.8 |
| MathVision (w/ Python) | 97.8 | **98.6** | 97.8 |

### 推理与知识

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| GPQA Diamond | 93.5 | 92.6 | **94.1** |
| AA-LCR | **74.7** | 70.0 | 73.7 |
| HLE-Full (w/ tools) | 56.0 | **63.0** | 58.0 |

---

## 七、部署方案

K3 官方推荐三个推理框架：

```bash
# vLLM（主推，官方配方）
# 见 https://recipes.vllm.ai/moonshotai/Kimi-K3

# SGLang
# 见 https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3

# TokenSpeed（LightSeek 出品）
# 见 https://lightseek.org/tokenspeed/recipes/models#kimi-k3
```

API 定价：
- Cache hit 输入：$0.30/MTok
- Cache miss 输入：$3.00/MTok
- 输出：$15.00/MTok

Moonshot 声称编码工作负载的 cache hit rate > 90%，这意味着实际平均输入成本远低于 $3.00/MTok。

**保留 reasoning_content 是使用 K3 的关键要求**：K3 使用 Preserved Thinking History 模式训练，多轮对话和工具调用时，历史 `reasoning_content` 必须原样传回——不能只传 `content`。

---

## 八、三个已知局限

**局限 1：思维历史敏感性**  
K3 对 `reasoning_content` 的传递方式有严格要求。切换模型后直接用 K3 接手对话，生成质量会高度不稳定。推荐从会话开始就用 K3，或使用已验证兼容的 Harness（Kimi Code）。

**局限 2：过度主动**  
K3 的训练强调长程任务，遇到模糊指令时倾向于自行决策，而不是暂停询问。受控边界内运行时，需要在 system prompt 或 `AGENTS.md` 里显式约束。

**局限 3：与 Fable 5 / GPT-5.6 Sol 仍有 UX 差距**  
Moonshot 在技术报告里直接承认这一点。整体能力有竞争力，但用户体验层面还差一档。

---

## 九、开源意义

K3 的开源是一个结构性事件，原因不只是参数量。

**技术透明度**：KDA、AttnRes、Stable LatentMoE 的实现细节通过技术报告公开，允许外部复现和改进。

**生态建设**：配套开源了 AgentENV（训练基础设施）+ vLLM KDA prefix caching 贡献，而不只是丢出一个权重文件。

**规模记录**：连续 9 个月在开源模型规模上线 Moonshot 都处于前沿，K3 把这个记录推到了 2.8T。

对研究社区来说，真正有价值的是：**一个验证了 KDA + LatentMoE 在 3T 规模有效的权重文件**，加上解释为什么的技术报告。

---

**参考链接**

- GitHub 通讯仓库：`github.com/MoonshotAI/Kimi-K3`
- HuggingFace 权重仓库：`huggingface.co/moonshotai/Kimi-K3`
- 技术报告 PDF：`github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf`
- AgentENV（RL 训练基础设施）：`github.com/kvcache-ai/AgentENV`
- API 平台：`platform.kimi.ai`（模型 ID：`kimi-k3`）

<!--EN-->

## Kimi K3 Technical Analysis: KDA, Stable LatentMoE, and the First Open 3T-Class Model

On July 27, 2026, Moonshot AI did something notable: they released Kimi K3's model weights and technical report simultaneously.

Weights on HuggingFace (`moonshotai/Kimi-K3`), technical report on GitHub (`MoonshotAI/Kimi-K3`).

This is the world's first open-source 3T-class model — 2.8T total parameters, 104B activated parameters per token.

This post combines both repositories for a comprehensive technical breakdown.

---

## Two Repositories

**Communication repo (GitHub)**: `MoonshotAI/Kimi-K3`  
Architecture details, benchmark tables, deployment guide, full technical report PDF (`k3_tech_report.pdf`)

**Weights repo (HuggingFace)**: `moonshotai/Kimi-K3`  
Official model weights under the Kimi K3 License, supporting vLLM / SGLang / TokenSpeed inference

Both READMEs cover the same ground; the GitHub side has the complete technical report.

---

## Architecture Overview

| Parameter | Value |
|---|---|
| Total Parameters | 2.8T |
| Activated Parameters | 104B |
| Layers | 93 (1 Dense + 92 MoE) |
| Attention Composition | 69 KDA + 24 Gated MLA |
| Attention Hidden Dim | 7168 |
| Attention Heads | 96 |
| Total Experts | 896, 16 activated per token |
| Shared Experts | 2 |
| LatentMoE Dimension | 3584 |
| Per-Expert Hidden Dim | 3072 |
| Vocabulary | 160K |
| Context Window | 1M tokens (1,048,576) |
| Vision Encoder | MoonViT-V2 (401M params) |
| Quantization | MXFP4 weights / MXFP8 activations (QAT) |
| Activation Function | SiTU-GLU |

---

## Core Architectural Innovations

### Kimi Delta Attention (KDA)

KDA is K3's primary attention mechanism, spanning 69 of its 93 layers.

The known problem with standard attention at long sequences: information flow efficiency degrades because every position competes across the full sequence. KDA introduces a delta (differential) mechanism that changes how information propagates across sequence length, improving efficiency in very long contexts.

A notable engineering consequence: **standard prefix caching doesn't work with KDA**. Moonshot contributed a corresponding vLLM implementation to the open-source community, to be released alongside the weights.

### Attention Residuals (AttnRes)

AttnRes is not a standard residual connection. It selectively retrieves representations across depth rather than uniformly accumulating them layer by layer.

Intuition: deeper attention heads can optionally "pull" representations from earlier layers, not just the immediately preceding one. This transforms information flow from linear stacking into selective cross-layer retrieval.

A telling detail from the technical blog: in Kimi K3's late development stages, an early version of K3 itself handled much of the team's AttnRes kernel optimization work — the model optimizing its own execution efficiency.

### Stable LatentMoE: 16/896 Expert Sparsity

K3's expert activation rate: 16/896 ≈ 1.79%.

This is extreme sparsity. Traditional MoE systems typically activate 1/8 to 1/4 of experts. K3 compresses this to under 2%.

At this sparsity level, two engineering challenges emerge:

**Challenge 1: Routing instability**  
Standard Top-K routing at very low activation rates tends to create "hot" experts that are perpetually selected while others go idle.

K3's solution: **Quantile Balancing** — deriving expert allocation directly from router-score quantiles, eliminating heuristic update rules and sensitive balancing hyperparameters.

**Challenge 2: Expert-parallel shape misalignment**  
At large scales, different batches activate different expert subsets, breaking static shapes in hardware-efficient implementations.

K3's solution: **fully balanced expert-parallel training** — static shapes, no host synchronization on the critical path, consistent throughput across batches.

### Per-Head Muon

Standard Muon optimizer applies uniform optimization across attention dimensions. Per-Head Muon optimizes each attention head independently, enabling more adaptive learning dynamics at 2.8T parameter scale.

### Gated MLA

The 24 Gated MLA layers introduce gating into the MLA (Multi-head Latent Attention) mechanism from K2, improving attention selectivity. Combined with SiTU-GLU activation, this provides better activation control than K2.

---

## MXFP4 Quantization-Aware Training

K3 applies QAT from the SFT stage onward:

- Weights: MXFP4 (4-bit MX Float)
- Activations: MXFP8 (8-bit MX Float)

This is not post-training quantization (PTQ) — the model learns to accommodate quantization-induced precision loss during training itself.

Significance: the open-source weights are already quantized. No additional quantization step required at deployment, with broad hardware compatibility.

Deployment note: K3's KDA architecture is recommended for **supernode configurations with 64+ accelerators**, consistent with its large-scale expert-parallel design.

---

## Connection to AgentENV

Earlier this month, Moonshot open-sourced AgentENV (`kvcache-ai/AgentENV`) — the RL sandbox infrastructure that powered K3's training.

K3's Agentic RL training requires large-scale parallel sandbox execution environments: code interpreters, tool calls, terminal environments. AgentENV solves cold-start (<50ms), elastic scaling, and resource reclamation using Firecracker microVMs + overlaybd + ublk.

**The critical sequence**: AgentENV (RL training infrastructure) came first, then K3's agentic capabilities. Open-sourcing AgentENV means external teams can use the same training infrastructure to reproduce or improve on K3's Agentic RL training paradigm.

---

## Benchmark Results

Comparison: Claude Fable 5, GPT-5.6 Sol, Claude Opus 4.8, GPT-5.5, GLM-5.2

### Long-Horizon Coding (K3's Core Advantage)

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol | Opus 4.8 |
|---|---|---|---|---|
| SWE-Marathon | **42.0** | 35.0 | 39.0 | 40.0 |
| Terminal-Bench 2.1 | **88.3** | 88.0 | 88.8 | 84.6 |
| ProgramBench | **77.8** | 76.8 | 77.6 | 71.9 |
| FrontierSWE | 81.2 | **86.6** | 71.3 | 66.7 |
| DeepSWE | 67.5 | **70.0** | **73.0** | 59.0 |

SWE-Marathon is a long-horizon benchmark (24-hour unsupervised runs). K3 leads at 42.0; Fable 5 had a 35% fallback rate in K3's evaluation.

### Agentic Capabilities

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| BrowseComp | **91.2** | 88.0 | 90.4 |
| DeepSearchQA (F1) | **95.0** | 94.2 | — |

### Multimodal

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| Video-MME (w. sub) | **90.0** | — | 89.5 |
| OmniDocBench | **91.1** | 89.8 | 85.8 |
| MathVision (w/ Python) | 97.8 | **98.6** | 97.8 |

### Reasoning & Knowledge

| Benchmark | K3 | Fable 5 | GPT-5.6 Sol |
|---|---|---|---|
| GPQA Diamond | 93.5 | 92.6 | **94.1** |
| AA-LCR | **74.7** | 70.0 | 73.7 |
| HLE-Full (w/ tools) | 56.0 | **63.0** | 58.0 |

---

## Deployment

K3 officially supports three inference frameworks:

```bash
# vLLM (recommended, official recipes)
# See: https://recipes.vllm.ai/moonshotai/Kimi-K3

# SGLang
# See: https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3

# TokenSpeed (by LightSeek)
# See: https://lightseek.org/tokenspeed/recipes/models#kimi-k3
```

API pricing:
- Cache-hit input: $0.30/MTok
- Cache-miss input: $3.00/MTok
- Output: $15.00/MTok

Moonshot claims a >90% cache hit rate on coding workloads, meaning effective average input cost is significantly below $3.00/MTok.

**Preserving `reasoning_content` is a hard requirement** for multi-turn K3 usage. K3 was trained in Preserved Thinking History mode — historical `reasoning_content` must be passed back exactly as returned, not just `content`. Switching mid-session from another model to K3 will cause unstable generation.

---

## Three Known Limitations

**Limitation 1: Thinking history sensitivity**  
K3 requires strict `reasoning_content` preservation in multi-turn conversations. Switching to K3 mid-session with another model's history causes highly unstable generation. Start sessions with K3, or use a verified-compatible harness (Kimi Code).

**Limitation 2: Excessive proactiveness**  
K3's training emphasizes long-horizon tasks. When encountering ambiguous intent, it tends to make decisions on the user's behalf rather than pausing to ask. Applications requiring bounded behavior need explicit constraints in the system prompt or `AGENTS.md`.

**Limitation 3: UX gap vs. Fable 5 / GPT-5.6 Sol**  
Moonshot acknowledges this directly in the technical report. Competitive overall capability, but a noticeable gap in user experience at the top tier.

---

## What the Open-Source Release Actually Means

K3's open release is structurally significant for reasons beyond parameter count.

**Technical transparency**: KDA, AttnRes, and Stable LatentMoE implementation details are published in the technical report, enabling external reproduction and improvement.

**Ecosystem building**: Moonshot didn't just release a weight file. They simultaneously open-sourced AgentENV (training infrastructure) and contributed KDA prefix-caching support to vLLM.

**Scale record**: For 9 of the past 12 months, Moonshot models have held the upper bound of open-model scale. K3 pushes that record to 2.8T.

For the research community, the real value is: **a weight file that validates KDA + LatentMoE at 3T scale**, paired with a technical report that explains why it works.

---

**References**

- GitHub communication repo: `github.com/MoonshotAI/Kimi-K3`
- HuggingFace weights repo: `huggingface.co/moonshotai/Kimi-K3`
- Technical report PDF: `github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf`
- AgentENV (RL training infrastructure): `github.com/kvcache-ai/AgentENV`
- API platform: `platform.kimi.ai` (model ID: `kimi-k3`)
