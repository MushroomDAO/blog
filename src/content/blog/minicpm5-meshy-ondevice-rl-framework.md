---
title: "MiniCPM5 + Meshy：OpenBMB 的端侧 LLM 与异步 RL 训练框架双开"
titleEn: "MiniCPM5 + Meshy: OpenBMB Launches On-Device SOTA LLMs and an Async RL Training Engine"
description: "OpenBMB 同步发布 MiniCPM5 系列端侧模型（1B/2B 双 SOTA）与 Meshy 异步 RL 引擎。RL+OPD 训练使推理提升 10.96 分，标准 LlamaForCausalLM 架构直接兼容主流推理框架，Meshy 用队列替代 RPC 实现拓扑灵活的分布式 RL。"
descriptionEn: "OpenBMB simultaneously releases MiniCPM5 (1B/2B on-device SOTA) and Meshy async RL engine. RL+OPD training yields +10.96 on reasoning benchmarks, standard LlamaForCausalLM architecture runs on all major inference frameworks, and Meshy replaces RPC with queue-based coordination for flexible distributed RL."
pubDate: "2026-09-08"
updatedDate: "2026-09-08"
category: "Research"
tags: ["端侧LLM", "MiniCPM", "强化学习", "开源模型", "分布式训练", "OpenBMB"]
heroImage: "../../assets/images/minicpm5-meshy-ondevice-rl-framework-banner.jpg"
---

> 📌 MiniCPM GitHub：https://github.com/OpenBMB/MiniCPM
> Meshy GitHub：https://github.com/OpenBMB/Meshy
> HuggingFace 模型集：https://huggingface.co/collections/openbmb/minicpm5

OpenBMB 这次动作不小——**同步开源了 MiniCPM5 系列端侧模型和 Meshy 异步 RL 训练框架**，两个项目相互配套：Meshy 是训练 MiniCPM5 的引擎，MiniCPM5 是 Meshy 的首个公开验证产出。

MiniCPM GitHub 仓库已积累 **10501 stars**，Apache-2.0 协议。

## MiniCPM5：1B 和 2B 的双 SOTA

MiniCPM5 目前有两个主力模型：

**MiniCPM5-1B** — 1B 参数量级开源 SOTA，特别强调 Agentic 工具调用和代码生成能力，已有 **73.7 万次**下载。

**MiniCPM5-2B** — 实际参数 2.5B（非嵌入参数 1.98B），在 2B 量级开源模型中达到 SOTA，平均得分 53.9，在代码推理和数学领域可以与 4B 级模型正面对抗。

架构上选用**标准 LlamaForCausalLM**——这个决策值得单独说一下。不少端侧模型为了性能优化引入自定义算子，代价是要等主流推理框架专门适配。MiniCPM5 用标准架构，vLLM、SGLang、Transformers、llama.cpp、Ollama、MLX、LM Studio 直接支持，不需要等任何人。

上下文窗口 **131K tokens**，通过 GQA（16 查询头 + 2 KV 头）控制推理开销。

## 训练关键：RL + OPD

MiniCPM5 的训练方法叫做 **RL + OPD（On-Policy Distillation）**，把强化学习和在线策略蒸馏结合起来做后训练。

数据上的结果：
- 推理 benchmark 提升 **+10.96 分**
- Agentic 能力提升 **+6.96 分**

对应释放的数据集：
- **UltraX**：预训练数据
- **UltraData-Code**：分层代码管理数据
- **UltraData-SFT-Agent-2609**：50 万条 Agent 样本
- **UltraData-RL-2609**：8 万+ 推理样本

模型家族还包括 DSpark（0.3B 草稿模型，用于 Speculative Decoding 提速）、SFT 版、Base 版、GGUF/GPTQ/MLX 各格式量化版本，覆盖从研究到部署的完整链路。

## Meshy：用队列重新设计分布式 RL

Meshy 是同步开源的**异步 RL 训练引擎**，专门为 LLM 的强化学习训练设计，架构思路与传统方案差异明显。

### 核心设计：服务化 + 队列驱动

传统分布式训练框架通常用 RPC 做服务间通信，有一个中心化的协调器来调度推理、训练、rollout 三个环节。

Meshy 的做法：**把这三个环节变成独立服务，通过统一的 TransferQueue 通信**。没有中心协调器，数据可用了就驱动下一步，不需要显式握手。

好处是拓扑变得非常灵活：
- 三个服务可以跑在同一张 GPU 上（低资源场景）
- 也可以跨多卡完全分离（大规模场景）
- 通过调整**单个参数**"pacing window"，同一套 recipe 可以在 on-policy、bounded off-policy、完全异步三种模式之间切换

### 技术底座

Meshy 由三个成熟项目组合而成：
- **torchtitan** — 分布式训练
- **SGLang** — LLM serving
- **TransferQueue** — 分布式数据传输

扩展新任务只需要提供数据集类和 reward function，不需要改框架代码。启动一条命令：

```bash
python scripts/launch.py --recipe recipe.justrl
```

仓库里内置了 MiniCPM5（1B 和 2.6B）在 DAPO-Math-17k 数据集上的训练 recipe，可以直接跑通。

## 为什么值得关注

两件事合在一起看更有意思：

**MiniCPM5 证明端侧模型的天花板还没到**。2B 参数挑战 4B、1B 参数拿 SOTA，核心不是架构创新，而是训练方法（RL+OPD）和数据工程（百万级高质量样本）。标准架构 + 强训练的路子，比定制架构 + 普通训练更实用。

**Meshy 把训练基础设施做成了可复现的开源资产**。以前这类分布式 RL 训练框架基本都是各家内部系统，现在 OpenBMB 把它开出来，意味着外部团队可以用同样的工具复现甚至超越这个训练路径。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 MiniCPM: https://github.com/OpenBMB/MiniCPM
> Meshy: https://github.com/OpenBMB/Meshy
> HuggingFace: https://huggingface.co/collections/openbmb/minicpm5

OpenBMB simultaneously open-sourced two projects: **MiniCPM5** (on-device LLMs) and **Meshy** (async RL training engine). Meshy trained MiniCPM5; MiniCPM5 validates Meshy at scale. MiniCPM's GitHub has 10,501 stars, Apache-2.0.

## MiniCPM5: Dual SOTA at 1B and 2B

**MiniCPM5-1B** is the 1B-class open-source SOTA with 737K HuggingFace downloads, excelling at agentic tool use and code generation.

**MiniCPM5-2B** (2.5B actual parameters, 1.98B non-embedding) achieves 2B-class SOTA with an average score of 53.9, competing with 4B models on code and math. Standard **LlamaForCausalLM** architecture means vLLM, SGLang, Transformers, llama.cpp, Ollama, MLX, and LM Studio all load it without patches. Context: 131K tokens via GQA (16 query / 2 KV heads).

## Training: RL + OPD

Post-training combines reinforcement learning with on-policy distillation (RL+OPD), delivering **+10.96 points on reasoning** and **+6.96 on agentic benchmarks**. Released datasets include UltraData-SFT-Agent-2609 (500K agent samples) and UltraData-RL-2609 (80K+ reasoning samples).

## Meshy: Queue-Based Distributed RL

Meshy is an async RL engine that replaces RPC coordination with a queue-driven architecture. Inference, training, and rollout run as independent services communicating through **TransferQueue** — no central coordinator, data availability drives progression. A single `pacing window` parameter switches the same recipe between on-policy, bounded off-policy, and fully async modes. Built on torchtitan + SGLang + TransferQueue. Adding new tasks requires only a dataset class and reward function.

## Why It Matters

MiniCPM5 shows that standard architecture + strong training (RL+OPD + curated data) beats exotic architecture + average training for on-device models. Meshy turns the training infrastructure that produced these results into a reproducible open-source asset — external teams can now run the same pipeline.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
