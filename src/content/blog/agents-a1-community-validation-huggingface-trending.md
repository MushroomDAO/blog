---
title: "发布 7 天：Agents-A1 登上 HuggingFace 首页，社区版本超过 50 个"
titleEn: "7 Days After Launch: Agents-A1 Hits HuggingFace Trending, 50+ Community Variants, IFStruct #1"
description: "Agents-A1（上海AI实验室，35B MoE）发布一周后：7K 官方下载、18K 系列合集、60K+ 含社区变体总下载，登上 HuggingFace Trending 首页，MLX Community 上线 Mac 原生版，HLE 基准 <128B 模型 #2，IFStruct 基准 #1。一周社区反应完整记录。"
descriptionEn: "One week after launch: Agents-A1 (Shanghai AI Lab, 35B MoE) hit HuggingFace Trending, accumulated 7K main downloads + 18K collection + 60K+ total with community forks, MLX Community released official Mac support, ranked #2 on HLE among sub-128B models, and #1 on IFStruct. Full one-week community reception."
pubDate: "2026-07-06"
updatedDate: "2026-07-06"
category: "Research"
tags: ["Agents-A1", "HuggingFace", "社区反馈", "MLX", "上海AI实验室", "开源模型", "IFStruct"]
heroImage: "../../assets/images/agents-a1-community-validation-huggingface-trending-banner.jpg"
---

> **HuggingFace 模型**: [InternScience/Agents-A1](https://huggingface.co/InternScience/Agents-A1) · **系列合集**: [collections/InternScience/agents-a1](https://huggingface.co/collections/InternScience/agents-a1) · **论文**: [arXiv:2606.30616](https://arxiv.org/abs/2606.30616) · 上海人工智能实验室

---

[上一篇文章](https://blog.mushroom.cv/blog/agents-a1-35b-moe-horizon-scaling-guide/)介绍了 Agents-A1 的技术架构——35B MoE 如何通过 Horizon Scaling（而不是参数堆叠）追平万亿参数模型。发布一周之后，这篇文章记录社区发生了什么。

---

## 数字：7 天的社区反应

| 指标 | 数值 |
|---|---|
| 主模型 HuggingFace 下载量 | **7,000+** |
| 系列合集（Collections）下载量 | **18,000+** |
| 含社区变体的总下载量 | **60,000+** |
| HuggingFace Trending | **登上首页** |
| 社区扩展版本数 | **50+** |
| MLX Mac 原生版 | **已上线（MLX Community 官方）** |

从官方发布到 60K 总下载，7 天。

---

## 排行榜：正式进入竞争序列

社区做了独立评测，结果在两个主要基准上已有定论：

**HLE（Humanity's Last Exam）基准**：在所有参数 < 128B 的公开模型中排名 **第 2**。

HLE 是一个专为测试模型在"超出人类平均水平的专业领域"中推理能力而设计的基准，覆盖数学、物理、化学、生物、医学等多个学科的专家级题目。< 128B 级别排第 2，在当前开放模型竞争格局中属于头部。

**IFStruct（结构化指令遵循）基准**：**第 1**。

这个基准直接评测模型对复杂格式约束、嵌套指令、多步骤任务规范的遵循能力——恰好是 Agents-A1 SVA（显著词汇对齐）对齐策略的强项领域。第一名在这里不是意外。

---

## MLX Community：Mac 原生支持

**MLX Community** 是 Apple 官方机器学习框架 MLX 生态的社区组织，专为 Apple Silicon（M1/M2/M3/M4 芯片）提供模型移植和优化。MLX Community 为 Agents-A1 发布官方 Mac 版，意味着这个模型可以在本地 MacBook Pro 或 Mac Studio 上运行，无需 NVIDIA GPU。

对于在苹果生态工作的开发者来说，这是从"值得关注"到"可以直接跑"的门槛转变。

---

## 开发者社区的反应

发布后，多位研究者和从业者在社交媒体上做了评测和评论。几个有代表性的视角：

**HuggingFace 官方 Paper 账号**，6 月 30 日，110 赞，5844 浏览：

> "Agents-A1: 35B MoE agent reaches trillion-parameter performance. By scaling the agent horizon—not the parameters. It unifies 6 heterogeneous domains via multi-teacher distillation with 45K-token trajectories."

**ModelScope（阿里云）**，6 月 30 日，950 赞，152K 浏览，书签 830：

> "Introducing Agents-A1, A 35B MoE agentic model built for long-horizon tasks across search, engineering, scientific research, instruction following, and tool calling. 256K context length + Agentic reasoning. Reaches SOTA results on long-horizon search, scientific research, and instruction-following benchmarks."

ModelScope 转发+评测是国内开源社区的典型验证节点，152K 浏览和 830 书签说明实际关注度不只是算法圈。

**研究者 Gorden Sun**，7 月 2 日，中文：

> "Agents-A1：针对长任务强化的Agent模型。由上海AI实验室开源，能在复杂流程中边做边自我纠错，原生多模态模型、原生支持工具调用，在同级别模型中长时任务最佳。"

**研究者 Vivek Kotecha**，7 月 4 日：

> "Everyone is chasing trillion-parameter models. Shanghai AI Lab went smaller. Agents-A1 is 35B, open-source, and hits 96.0 on GAIA by training on longer task horizons instead of bigger size. The next scaling law is not parameters. It is persistence."

社区自发基准测试说明模型已经进入实际评测循环，而不只是停留在论文引用阶段。

---

## 与同级别模型的对比测试

第三方 **MiaAI Lab** 发布了 Agents-A1 vs Qwen3.6-35B-A3B 的 agentic workflow 对比测试（108 赞，8867 浏览）。结论是 Qwen3.6 在这轮测试中胜出。

这个结果本身不必然说明 Agents-A1 更弱——选择的评测任务类型会显著影响结果——但它说明了一件更重要的事：**社区已经把 Agents-A1 当作同级别竞品纳入正式比较**。不进入对比，才是被忽视。

---

## 50+ 社区变体意味着什么

60K 下载里有 50 多个社区扩展版本——量化版（GGUF、4-bit、8-bit）、合并微调版、多模态适配版、专域精调版。

这个数字有一个具体的含义：这些版本的作者需要投入时间，在自己的算力上跑完整的推理测试，然后写好 model card 发布。每一个版本都是一次独立的社区信任投票。

50 个社区变体在 7 天内出现，说明模型的基础质量达到了"值得投入适配成本"的门槛。

---

## 接下来关注什么

目前仍在进展中的几个方向：

- **长程 Agent 基准更多结果**：GAIA、WebArena、SWE-bench 等标准评测的完整数据尚未全部公开
- **多模态能力的系统评测**：原生多模态声称已经有人验证，但更系统的覆盖还在社区进行中
- **中文长程任务**：现有评测多为英文，中文长程 Agent 性能的独立评测暂未看到完整报告

---

> **相关链接**
> - [技术架构介绍（上一篇）](https://blog.mushroom.cv/blog/agents-a1-35b-moe-horizon-scaling-guide/) — KAG、Horizon Scaling、三阶段训练
> - [HuggingFace 模型页](https://huggingface.co/InternScience/Agents-A1)
> - [HuggingFace Collections](https://huggingface.co/collections/InternScience/agents-a1)
> - [ModelScope 模型页](https://www.modelscope.ai/models/InternScience/Agents-A1)
> - [arXiv 论文](https://arxiv.org/abs/2606.30616)
> - [GitHub 仓库](https://github.com/InternScience/Agents-A1)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Seven days after launch, Agents-A1 (InternScience/Shanghai AI Lab, 35B MoE, arXiv:2606.30616) hit HuggingFace Trending, accumulated 7K main downloads, 18K collection downloads, and 60K+ total across 50+ community variants. MLX Community released official Apple Silicon support. Independent benchmarks: #2 on HLE among models under 128B parameters, #1 on IFStruct. ModelScope's announcement post reached 152K views and 830 bookmarks. Third-party evaluations comparing Agents-A1 against Qwen3.6-35B-A3B have appeared — a signal the model entered the competitive evaluation cycle, not just citation lists.

---

## One-Week Snapshot

**Downloads**: 7K main model, 18K collection, 60K+ total (community forks included).

**Community variants**: 50+ versions — quantized (GGUF, 4-bit, 8-bit), merged fine-tunes, multimodal adapters. Each represents an independent investment of compute and time. 50 variants in 7 days is a community confidence signal.

**Leaderboard results**:
- HLE (Humanity's Last Exam): **#2 among sub-128B open models**
- IFStruct (structured instruction following): **#1**

IFStruct #1 aligns directly with the SVA (Salient Vocabulary Alignment) training strategy described in the paper — the model is trained to surface and respect format constraints explicitly. The leaderboard result validates the design choice.

**Mac support**: MLX Community published official Apple Silicon builds. Local inference on M-series hardware without NVIDIA hardware is now available.

**Community reaction** (selected):

- **@ModelScope2022**: "SOTA results on long-horizon search, scientific research, and instruction-following benchmarks." — 152K views, 830 bookmarks
- **@vbkotecha**: "The next scaling law is not parameters. It is persistence."
- **@HuggingPapers**: "35B MoE agent reaches trillion-parameter performance." — 110 likes, 60 bookmarks
- **@MiaAI_lab**: Agents-A1 vs Qwen3.6-35B-A3B head-to-head evaluation (Qwen3.6 won in their specific test) — signals Agents-A1 entered the legitimate comparison bracket

**Links**: [HuggingFace](https://huggingface.co/InternScience/Agents-A1) · [Collections](https://huggingface.co/collections/InternScience/agents-a1) · [arXiv](https://arxiv.org/abs/2606.30616) · [GitHub](https://github.com/InternScience/Agents-A1) · [Technical deep-dive](https://blog.mushroom.cv/blog/agents-a1-35b-moe-horizon-scaling-guide/)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
