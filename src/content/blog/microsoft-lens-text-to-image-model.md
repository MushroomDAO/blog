---
title: "微软开源 38 亿参数文生图模型 Lens，训练成本只要竞品的两成"
titleEn: "Microsoft Open-Sources Lens: 3.8B Text-to-Image Model at 20% the Training Cost"
description: "微软发布开源文生图模型 Lens，仅 3.8B 参数却在多项基准上超越 Stable Diffusion 3 和 Flux，训练成本只要竞品的两成。"
descriptionEn: "Microsoft releases Lens, an open-source 3.8B parameter text-to-image model that outperforms Stable Diffusion 3 and Flux on multiple benchmarks while costing only 20% as much to train."
pubDate: "2026-05-25"
updatedDate: "2026-05-25"
category: "Tech-News"
tags: ["AI", "文生图", "微软", "开源", "Lens", "Stable Diffusion", "Flux"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

微软在 Hugging Face 每日论文榜以第二名登场的 Lens，用 3.8B 参数打败了 8B 的 Stable Diffusion 3 和 12B 的 Flux，而训练成本只有竞品的两成。小模型、高性能、低成本，这是怎么做到的？

## Lens 是什么？

昨天 Hugging Face 的每日论文榜上，排名第二的是一篇叫 Lens 的论文。微软出的，3.8B 参数的文生图模型。

3.8B 就是 38 亿参数。对比一下，Stable Diffusion 3 是 8B，Flux 是 12B。Lens 比它们小很多，但在好几个基准测试上分数更高。

这个组合——更小的模型、更好的效果、更低的成本——就是这篇论文最核心的价值。

## 为什么训练成本只要两成？

### 架构创新

Lens 在设计上有意绕开了大规模参数堆砌的路线。微软的研究团队重新审视了文生图模型的瓶颈，发现更多参数不一定等于更好的图像质量——关键在于训练效率和数据利用率。

Lens 采用了更高效的扩散架构，在注意力机制和去噪路径上做了针对性优化，使得同等质量下所需的计算量大幅下降。

### 数据效率

相比 Stable Diffusion 和 Flux 动辄数十亿张图片的训练规模，Lens 通过更精选的数据集和更有效的数据增强策略，用更少的数据达到了更好的泛化能力。

训练成本只要竞品两成，意味着同样的算力预算下，Lens 可以迭代五次，而竞品只能跑一次。

## 性能对比：小参数，大表现

| 模型 | 参数量 | 相对训练成本 |
|------|--------|------------|
| Flux | 12B | ~500% |
| Stable Diffusion 3 | 8B | ~300% |
| **Lens** | **3.8B** | **100%（基准）** |

在 GenEval、DPGBENCH 等主流文生图基准测试中，Lens 均超越了参数量更大的竞品。这打破了"模型越大越好"的直觉。

## 开源意味着什么？

微软选择将 Lens 完全开源，可在 Hugging Face 上直接获取模型权重和代码。

对于独立开发者和小团队来说，这意味着：

- **本地部署可行**：3.8B 参数在消费级 GPU（16GB 显存）上就能运行
- **微调成本低**：小模型意味着更快的 LoRA/DreamBooth 微调周期
- **商业友好**：开源协议允许在研究和商业场景中使用

Stable Diffusion 当年开源震动了整个 AI 图像领域，Lens 也有类似的潜力——更小、更快、更便宜。

## 这对 AI 图像生成意味着什么？

Lens 的出现再次证明了一个趋势：**效率正在超越规模成为新的竞争维度**。

2023 年前后，模型竞争的主旋律是"谁的参数多"。现在，像 Lens、Phi 系列这样的小而精的模型正在改变游戏规则——在特定任务上，精心设计的小模型可以击败粗暴堆砌的大模型。

对于开发者而言，本地运行、低延迟、可控成本，是商业化落地的核心诉求。Lens 的出现，让这些诉求在文生图领域变得更容易满足。

## 如何获取 Lens？

模型权重和代码已发布在 Hugging Face 上，论文全文可在 arXiv 查阅。

> 📌 论文地址：Lens: Rethinking Text-to-Image Generation at Scale  
> Hugging Face 搜索：microsoft/Lens

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Microsoft's Lens model landed at #2 on Hugging Face's daily paper chart with just 3.8B parameters — beating out Stable Diffusion 3 (8B) and Flux (12B) on multiple benchmarks while costing only 20% as much to train. How is that possible?

## What Is Lens?

Lens is an open-source text-to-image model from Microsoft, introduced in a paper that ranked second on Hugging Face's daily paper leaderboard. At 3.8B parameters, it's dramatically smaller than its main competitors — yet achieves higher scores across several key benchmarks.

This combination of smaller model, better results, and lower cost is the paper's core contribution.

## Why Does It Only Cost 20% to Train?

### Architectural Innovation

Lens deliberately avoids the parameter-stacking approach. Microsoft's team re-examined the bottlenecks in text-to-image generation and found that more parameters don't automatically yield better image quality — training efficiency and data utilization matter more.

Lens uses a more efficient diffusion architecture with targeted optimizations to attention mechanisms and denoising pathways, significantly reducing the compute needed for equivalent quality.

### Data Efficiency

Compared to Stable Diffusion and Flux, which train on billions of images, Lens achieves stronger generalization with a more curated dataset and better data augmentation strategies.

At 20% of the training cost, the same compute budget lets Lens iterate five times where competitors run once — a massive advantage for rapid improvement cycles.

## Performance Comparison

| Model | Parameters | Relative Training Cost |
|-------|------------|----------------------|
| Flux | 12B | ~500% |
| Stable Diffusion 3 | 8B | ~300% |
| **Lens** | **3.8B** | **100% (baseline)** |

Lens outperforms larger models on GenEval, DPGBENCH, and other standard text-to-image benchmarks, challenging the assumption that bigger is always better.

## What Does Open Source Mean Here?

Microsoft has fully open-sourced Lens — weights and code are available directly on Hugging Face.

For independent developers and small teams, this means:

- **Local deployment is feasible**: 3.8B parameters runs on a consumer GPU with 16GB VRAM
- **Low fine-tuning cost**: LoRA and DreamBooth cycles are much faster on a smaller model
- **Commercial-friendly licensing**: usable for research and commercial applications

When Stable Diffusion went open source, it transformed the AI image generation landscape. Lens has similar potential — smaller, faster, cheaper.

## What This Means for AI Image Generation

Lens reinforces a growing trend: **efficiency is overtaking scale as the key competitive dimension**.

Through 2023, the dominant narrative was "who has the most parameters." Now, lean and precise models like Lens and the Phi series are rewriting the rules — on specific tasks, a well-designed small model can beat a brute-force large one.

For developers, local execution, low latency, and controllable costs are the core requirements for commercial deployment. Lens makes those requirements easier to meet in the text-to-image domain.

## How to Get Lens

Weights and code are available on Hugging Face; the full paper is on arXiv.

> 📌 Paper: Lens: Rethinking Text-to-Image Generation at Scale  
> Search on Hugging Face: microsoft/Lens

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
