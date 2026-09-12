---
title: 'Miles v0.1：SGLang 团队填平学术 RL 和生产系统之间的鸿沟'
titleEn: "Miles v0.1: The SGLang Team Bridges the Gap Between Academic RL and Production Systems"
description: "SGLang 团队发布 Miles v0.1，生产级 LLM/VLM RL 后训练框架。全异步 RL、P2P RDMA 权重同步（万亿参数秒级更新）、TITO 消除 token 往返损耗、R3 修复 MoE 路由不一致、自动容错恢复——每块都是工业级设计。"
descriptionEn: "The SGLang team releases Miles v0.1, a production-grade RL post-training framework for LLMs and VLMs. Fully async RL, P2P RDMA weight sync (trillion-parameter updates in seconds), TITO eliminating token round-trip overhead, R3 fixing MoE routing mismatch, and automatic fault recovery — every component built for production."
pubDate: "2026-09-12"
updatedDate: "2026-09-12"
category: "Tech-News"
tags: ["RL", "post-training", "SGLang", "LLM", "open-source", "LMSYS"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
---

> 📌 论文：Miles v0.1: Production-Level Post-Training
> arXiv 全文：https://arxiv.org/abs/2609.08368
> GitHub：https://github.com/radixark/miles
> 博客：https://www.lmsys.org/blog/2026-08-18-miles-v0-1/
> HuggingFace：https://huggingface.co/papers/2609.08368

---

**BLUF**：Miles 是 SGLang 团队发布的生产级 RL 后训练框架，从 slime 演化而来。它直接瞄准了学术 RL 代码进生产时反复翻车的那些问题：异步调度气泡、万亿参数权重同步延迟、MoE 路由不一致、token 往返损耗、引擎崩溃要重启——每个都给出了系统性解法。支持 DeepSeek-V4、Kimi-K2.6、Qwen3.5 等前沿模型，NVIDIA 和 AMD 全系列硬件，Day-0 支持成为常态。

---

## 学术 RL 代码进生产，会在哪里翻车

在 Miles 出现之前，把 RL 后训练从论文代码搬到生产系统，工程团队通常要自己解决这些问题：

- **rollout 和 training 强耦合**：GPU 资源互等，流水线气泡大
- **权重同步太慢**：大模型每轮更新的权重要传输给推理引擎，几十 GB 在几分钟内传不完
- **MoE 路由不一致**：rollout 时的专家路由和 training forward pass 的路由不同，大规模训练容易发散
- **token 格式往返**：rollout 产生 token → 解码成文本 → 重新编码给 trainer，信息损耗且慢
- **单点故障**：一个推理引擎挂了，整个 run 重头来

Miles 把这五个问题各给了一个系统性答案。

---

## 架构：三层解耦

Miles 的架构分三层：

```
Rollout 层  → SGLang（多轮 agentic，高吞吐量生成）
              ↕ P2P RDMA / NVLink / TCP 权重同步
Trainer 层  → Megatron-LM（万亿参数规模，主力）
              → PyTorch FSDP2（小规模或 HuggingFace 模型）
调度层      → 全异步 RL，rollout 和 training worker 独立运行
```

三种权重同步传输可以按部署拓扑选择：同机 NVLink、跨机 P2P RDMA、TCP 兜底。

---

## 五个关键技术点

### 1. 全异步 RL

Rollout worker 和 training worker 完全解耦，各跑各的，通过可配置的 on-policy / off-policy 调度协调。流水线针对气泡最小化优化，不需要等一方做完再启动另一方。

对比同步 RL：GPU 利用率显著提升，整体吞吐量提高可以是数量级的。

### 2. P2P RDMA 权重更新

每轮训练完成后，新权重要同步给 SGLang 推理引擎，才能跑下一轮 rollout。

Miles 的方案：**P2P RDMA**，直接内存到内存传输，绕过 CPU 和操作系统缓冲区。结果：即使是 Kimi-K2.6 这样的**万亿参数模型**，权重更新也能在**秒级**完成。

这不是调参能达到的效果——是传输协议层面的选择。

### 3. Token-in-Token-Out（TITO）

传统 RL 流水线：rollout 产生 token ID → **解码成文本** → trainer 重新 tokenize 成 token ID。这一来一回有三个问题：
- 速度损耗（每轮都在做无意义的编解码）
- 信息丢失（某些 special token 在解码再编码后会变形）
- 日志难以对齐

TITO 的方案：**token ID 全程不解码**，rollout 产生什么格式，trainer 直接接收什么格式。对所有模型和所有黑盒 harness 都支持。

### 4. Rollout Routing Replay（R3）

MoE 架构（Mixture of Experts）里，专家路由是在 forward pass 中动态计算的。问题在于：rollout 阶段和 trainer 的 forward pass 可能跑出不同的路由决策——因为它们的并行策略、精度、甚至随机种子可能不完全一致。

路由不一致 → 梯度估计不准 → 大规模训练不稳定甚至发散。

R3 的解法：在 rollout 时**记录专家路由决策**，在 trainer forward pass 时**重放**这个记录而不是重新计算。计算和通信开销通过 overlap 控制。

这是 Miles 技术贡献里最细但最重要的一个——MoE 模型（DeepSeek、Kimi 等）全部依赖这个。

### 5. 容错恢复

SGLang 推理引擎挂了，Miles **自动探测、重启引擎、从中断点恢复**，整个训练 run 不需要停止或重启。

对于跑几天的大规模 RL run，这个功能的价值不需要解释。

---

## 支持范围

**算法**：GRPO、GSPO、PPO、REINFORCE++（RL）；SFT；On-policy Distillation

**模型（Day-0 支持）**：
- DeepSeek-V4、DeepSeek-V4 Flash
- Kimi-K3、Kimi-K2.6（万亿参数）
- GLM-5.2、Inkling、Nemotron 3 Ultra、Qwen3.5

**硬件**：
- NVIDIA：GB300、GB200、B300、B200、H200、H100、A100
- AMD：MI300X、MI325、MI350、MI355X（ROCm）

**低精度**：MXFP8（Blackwell 原生）、NVFP4、INT4 QAT、BF16、FP16

**Agentic 环境**：Harbor、HUD、NeMo Gym、OpenEnv、Verifiers；任务沙盒接 AgentENV、Daytona、E2B、Modal

**扩展**：[Miles-Diffusion](https://github.com/radixark/miles_diffusion)——用 Flow-GRPO 和 DiffusionNFT 对扩散模型做 RL 后训练

---

## 和 slime 的关系

Miles 从 THUDM 的 [slime](https://github.com/THUDM/slime) fork 出来，并与其**共同演进**。

slime 是清华大学团队的 RL 训练框架，本身也在积极更新。Miles 在 slime 的基础上加了更多生产级特性（P2P RDMA、R3、TITO、容错等）和更广泛的模型/硬件支持，同时保持双向的代码同步。

---

## 为什么值得关注

过去两年，RL 后训练成为前沿模型能力跃升的核心手段：DeepSeek-R1 的推理突破、各家 o1-style 模型的思维链训练，本质都是 RL 后训练的产物。

但做 RL 后训练一直是大公司的专属——不是因为算法难，而是工程太难。把 rollout 和 training 规模化、稳定化、高效化，需要大量基础设施工作。

Miles 第一次把这套工程完整地开源出来。它不是教程级别的代码，是**已经跑在万亿参数模型上的生产系统**。

对于想做 RL 后训练的团队，这是目前能拿到的最完整的起点。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Paper: Miles v0.1: Production-Level Post-Training
> arXiv: https://arxiv.org/abs/2609.08368
> GitHub: https://github.com/radixark/miles
> Blog: https://www.lmsys.org/blog/2026-08-18-miles-v0-1/
> HuggingFace: https://huggingface.co/papers/2609.08368

---

**BLUF**: Miles is the SGLang team's production-grade RL post-training framework, evolved from slime. It addresses the engineering failures that repeatedly occur when moving academic RL code to production: scheduling bubbles from tight coupling, slow weight sync at trillion-parameter scale, MoE routing mismatch, token round-trip overhead, and crash-requiring restarts. Every problem gets a systematic solution. Supports DeepSeek-V4, Kimi-K2.6, Qwen3.5, and more — Day-0 support is the norm.

---

## Where Academic RL Code Breaks in Production

Before Miles, shipping RL post-training from research code to a production system meant engineering teams solving these themselves:

- **Tightly coupled rollout and training**: GPUs waiting on each other, large pipeline bubbles
- **Slow weight sync**: shipping tens of GB of updated weights to inference engines between rounds
- **MoE routing mismatch**: different routing decisions between rollout and the trainer's forward pass, causing instability at scale
- **Token round-trips**: token IDs → decode to text → re-encode for trainer, with loss and overhead
- **Single-point failures**: one inference engine crashes, the whole run restarts from scratch

Miles gives each of these a systematic answer.

---

## Architecture: Three Decoupled Layers

```
Rollout layer  → SGLang (multi-turn agentic, high-throughput generation)
                 ↕ P2P RDMA / NVLink / TCP weight sync
Trainer layer  → Megatron-LM (trillion-parameter scale, primary)
                 → PyTorch FSDP2 (smaller runs or HuggingFace models)
Scheduling     → Fully async RL, rollout and training workers run independently
```

Three weight-sync transports, chosen by deployment topology: same-node NVLink, cross-node P2P RDMA, TCP fallback.

---

## Five Key Technical Contributions

### 1. Fully Async RL

Rollout and training workers run completely decoupled, coordinated by configurable on-policy/off-policy scheduling. The pipeline is optimized to minimize bubbles — no waiting for one side to finish before the other starts. Compared to synchronous RL, GPU utilization improves dramatically.

### 2. P2P RDMA Weight Updates

After each training step, updated weights must reach the SGLang inference engines before the next rollout. Miles uses **P2P RDMA** — direct memory-to-memory transfer, bypassing the CPU and OS buffers. Result: even at **trillion-parameter scale** (Kimi-K2.6), weight updates complete **in seconds**.

This isn't a tuning result — it's a protocol-layer design choice.

### 3. Token-in-Token-Out (TITO)

Traditional RL pipelines: rollout produces token IDs → **decode to text** → re-tokenize for trainer. Three problems: speed overhead (pointless encode/decode every round), information loss (special tokens can mutate through the round-trip), log misalignment.

TITO's solution: **token IDs stay as token IDs throughout** — whatever format rollout produces, the trainer receives directly. Works for all models and all black-box harnesses.

### 4. Rollout Routing Replay (R3)

In MoE architectures, expert routing is computed dynamically during the forward pass. The problem: rollout and the trainer's forward pass can produce different routing decisions — different parallelism strategies, precision, or random seeds.

Routing mismatch → inaccurate gradient estimates → instability or divergence at scale.

R3's solution: **record routing decisions during rollout**, then **replay** those recorded decisions in the trainer's forward pass instead of recomputing. Compute and communication costs are overlapped to contain overhead.

This is the quietest but most critical contribution — every MoE model (DeepSeek, Kimi, etc.) depends on it.

### 5. Fault Tolerance

When a SGLang inference engine crashes, Miles **automatically detects it, restarts the engine, and resumes from the interruption point** without stopping the training run.

For multi-day large-scale RL runs, this feature's value needs no explanation.

---

## What Miles Supports

**Algorithms**: GRPO, GSPO, PPO, REINFORCE++ (RL); SFT; On-policy distillation

**Day-0 models**: DeepSeek-V4, DeepSeek-V4 Flash, Kimi-K3, Kimi-K2.6 (trillion-parameter), GLM-5.2, Inkling, Nemotron 3 Ultra, Qwen3.5

**Hardware**: NVIDIA GB300/GB200/B300/B200/H200/H100/A100; AMD MI300X/MI325/MI350/MI355X (ROCm)

**Precision**: MXFP8 (Blackwell-native), NVFP4, INT4 QAT, BF16, FP16

**Agentic environments**: Harbor, HUD, NeMo Gym, OpenEnv, Verifiers; sandboxes: AgentENV, Daytona, E2B, Modal

**Extension**: Miles-Diffusion — RL post-training for diffusion models with Flow-GRPO and DiffusionNFT

---

## Why This Matters

Over the past two years, RL post-training has become the central mechanism behind frontier model capability leaps — DeepSeek-R1's reasoning breakthrough, every o1-style chain-of-thought model — all RL post-training at core.

But RL post-training has been exclusive to large organizations — not because the algorithms are hard, but because the engineering is. Scaling, stabilizing, and making rollout + training efficient requires massive infrastructure investment.

Miles is the first time this full engineering stack has been open-sourced in production-ready form. Not tutorial code — a **system already running on trillion-parameter models**.

For teams wanting to do RL post-training, this is the most complete starting point currently available.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
