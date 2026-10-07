---
title: "Naive-N0.5-Flash：AI 自己设计了这个 309B MoE 的注意力架构"
titleEn: "Naive-N0.5-Flash: AI Designed Its Own Attention Architecture in This 309B MoE"
description: "NaiveAI 2026 年 2 月成立，融资 4 亿美元，9 月发布首个模型 Naive-N0.5-Flash。MIT 开源，309B MoE/15.5B 激活，1M 原生上下文，48 层全 SWA+DSA 混合注意力、无一层全注意力。技术报告里最值得注意的不是参数规模，而是 AI4AI 实践：SWA+DSA 混合架构本身由 AI 在研究员设定目标（1M token 高效解码）后自主探索并提出，研究员最终从 AI 的方案中选定最优路径。HuggingFace 174 likes，SWE-bench Pro 73.6，全部为自报数字。"
descriptionEn: "NaiveAI, founded February 2026 with $400M raised, debuted Naive-N0.5-Flash in September. MIT-licensed, 309B MoE with 15.5B active parameters, native 1M-token context, 48 hybrid SWA+DSA layers — no full-attention layers anywhere. The technical report's most notable claim: the SWA+DSA hybrid architecture was designed by AI itself, not predetermined by engineers. Researchers set the objective (efficient 1M-token decoding), AI models ran ablations and proposed candidates, humans selected the best option. HuggingFace 174 likes, SWE-bench Pro 73.6, all self-reported."
pubDate: 2026-10-07
heroImage: "../../assets/images/naive-n05-flash-309b-moe-ai4ai-1m-context-banner.jpg"
category: "Tech-Experiment"
tags: ["大模型", "MoE", "AI Agent", "开源模型", "AI4AI", "注意力机制"]
lang: "zh-CN"
wechatTitle: "Naive-N0.5-Flash：AI自己设计的注意力架构"
wechatDigest: "MIT；309B/15.5B；1M上下文；AI设计SWA+DSA；零全注意力；SWE-bench 73.6"
---

NaiveAI 今年 2 月成立，融资 4 亿美元，7 个月后发布了第一个模型。

309B 参数，在动辄千亿起步的前沿模型里不算最炸。但翻完技术报告，最让人意外的点不是规模，而是他们 AI4AI 实践的深度：这个模型用的 SWA+DSA 混合注意力架构，是 AI 自己探索出来的。

HuggingFace: https://huggingface.co/NaiveAI/Naive-N0.5-Flash | ⭐ 174 | MIT

---

## 先说架构本身

Naive-N0.5-Flash 的核心设计是一个**零全注意力层**的混合架构。

传统大模型处理长上下文时，全注意力（Full Attention）的计算量随序列长度平方增长。DSA 系列工作（DeepSeek 首先提出）是一条替代路径：用一个轻量级 indexer 从完整历史序列里精选 top-K 个 token，再做后续注意力，把平方复杂度压下来。

Naive-N0.5-Flash 的做法是把 SWA 和 DSA 混用，**全程没有任何全注意力层**：

| 层类型 | 数量 | 机制 |
|--------|------|------|
| SWA（滑动窗口注意力） | 39 层 | 128 token 窗口，只看局部 |
| DSA（稀疏注意力） | 9 层 | 16 头 indexer 从全序列选 top-2048 token |

48 层按 8 个模块组织，每个模块 5 层 SWA + 1 层 DSA。底层 KV 用 GQA4（4 个 KV 组）。

整个模型在百万 token 上下文下不需要跟序列长度做平方交换，这是 1M 上下文推理可以跑起来的前提。

---

## AI 怎么设计了这个架构

技术报告里的原文是：

> "AI explored and designed its hybrid attention architecture while optimizing its training, inference, and deployment systems."

具体流程是：研究员设定目标——在百万 token 级上下文下提升解码效率、同时保持模型质量——然后让 AI 实现候选方案、跑 ablation、汇报结果，研究员从 AI 给出的可行方案里选定最优路径。

最终落地的就是这个 5:1 的 SWA-to-DSA 比例，128 token 滑窗 + top-2048 稀疏选择。

这不是 "AI 写了一行代码" 意义上的 AI4AI，也不是 prompt 工程。而是把架构搜索本身外包给了 AI 模型，研究员承担目标设定和最终拍板的角色。

支撑这个流程的基础设施规模：每周约 1000 万个沙盒，峰值 10 万并发操作，通过统一控制面管理算力、环境和安全隔离。

---

## 基本规格

| 项目 | 值 |
|------|-----|
| 总参数 | 309B |
| 激活参数 | 15.5B（每 token） |
| 原生上下文 | 1M token |
| 架构基座 | MiMo-V2.5（小米开源模型） |
| 训练数据 | 3.25T token 续训 |
| 权重大小 | 约 315GB |
| 许可证 | MIT |

续训分三阶段：50B token indexer 热身、3T token 稀疏注意力训练、200B token 学习率衰减，全程以 1M token 原生上下文长度进行。

---

## Benchmark（全部自报）

| Benchmark | 分数 |
|-----------|------|
| DeepSWE v1.1 | 67.8 |
| SWE-bench Pro | 73.6 |
| FrontierSWE v1 | 78.2 |
| Terminal-Bench 2.1 | 86.7 |
| PostTrainBench | 37.5 |
| MLE-bench-30 | 73.7% |
| SOL-ExecBench | 72.81 |

⚠️ 上述数字均为 NaiveAI 自报，尚无第三方独立验证。SWE-bench Pro 73.6 的方法论细节未完整披露。PostTrainBench 37.5 可与近期同类模型横向对比，但仍是公司自测。

---

## 推理和 API

NaiveAI 为这个模型开发了配套推理栈 NaiveRT，结合 mega-kernel 融合、Programmatic Dependent Launch 和推测解码：

- **Ultrafast 模式**：最高 2,000 token/s（批处理场景）
- **标准模式**：约 50 token/s 每用户（API 服务）
- **API 定价**：输入 $0.10/M，输出 $0.40/M，缓存 $0.01/M

本地部署需要下载约 315GB 权重，不是随便一台机器能跑的规格。

---

## 一句话说清楚

Naive-N0.5-Flash 是 NaiveAI 的首发：MIT 开源，309B MoE，1M 上下文，架构由 AI 探索设计，不含任何全注意力层。值得关注的不是 309B 这个数字，而是"研究员设目标、AI 跑实验、人来选方案"这套 AI4AI 流程——如果技术报告描述属实，这是一家七个月新公司在方法论上走出的独特路径。

---

## 边界

- 权重 315GB，本地部署门槛高
- 所有 benchmark 自报，无独立验证
- SWE-bench Pro 73.6 方法论细节不完整
- AI 设计架构的具体过程描述停留在技术报告层面，ablation 细节未公开
- 公司成立仅 7 个月，工程和研究的长期稳定性待观察

---

> MIT 开源。NaiveAI 2026-09-27 发布，HuggingFace 已上线。开源仅供学习参考。

---

<!--EN-->

## Naive-N0.5-Flash: AI Designed Its Own Attention Architecture in This 309B MoE

NaiveAI was founded in February 2026 with $400M in funding, and released its first model seven months later.

At 309B parameters, it's not the largest model around. But the most interesting part of the technical report isn't the scale — it's the depth of their AI4AI practice: the SWA+DSA hybrid attention architecture was explored and proposed by AI itself, not predetermined by engineers.

HuggingFace: https://huggingface.co/NaiveAI/Naive-N0.5-Flash | ⭐ 174 | MIT

---

### The Architecture

Naive-N0.5-Flash uses a hybrid attention design with **zero full-attention layers** anywhere in the stack.

Standard long-context models use full attention — O(n²) compute as sequence length grows. DSA (first introduced by DeepSeek) replaces this: a lightweight indexer selects top-K tokens from the full history for a subsequent sparse attention pass. Naive-N0.5-Flash mixes SWA and DSA throughout:

| Layer Type | Count | Mechanism |
|-----------|-------|-----------|
| SWA (Sliding Window Attention) | 39 | 128-token local window |
| DSA (Sparse Attention) | 9 | 16-head indexer selects top-2,048 tokens from full history |

48 layers organized into eight 6-layer modules, each with 5 SWA + 1 DSA. GQA4 (4 KV groups) for key-value caching. No quadratic scaling with sequence length, which makes native 1M-token inference feasible.

---

### How AI Designed This Architecture

From the technical report:

> "AI explored and designed its hybrid attention architecture while optimizing its training, inference, and deployment systems."

The process: researchers set the objective — improve decoding efficiency at 1M-token context while maintaining quality — then AI models implemented candidate approaches, ran ablations, and presented findings. Researchers selected from the viable options.

The final architecture (5:1 SWA-to-DSA ratio, 128-token window, top-2,048 sparse selection) was the AI's proposal.

This isn't "AI wrote some code." It's architecture search itself delegated to AI, with humans owning goal-setting and final selection.

Infrastructure supporting this: ~10M sandboxes/week, 100K peak concurrent operations, managed through a unified control plane.

---

### Specifications

| Item | Value |
|------|-------|
| Total parameters | 309B |
| Active parameters | 15.5B (per token) |
| Native context | 1M tokens |
| Architecture base | MiMo-V2.5 (Xiaomi open-weight) |
| Training | 3.25T tokens continued training |
| Weights size | ~315GB |
| License | MIT |

Training phases: 50B-token indexer warmup → 3T-token sparse-attention training → 200B-token LR decay, all at native 1M-token context.

---

### Benchmarks (all self-reported)

| Benchmark | Score |
|-----------|-------|
| DeepSWE v1.1 | 67.8 |
| SWE-bench Pro | 73.6 |
| FrontierSWE v1 | 78.2 |
| Terminal-Bench 2.1 | 86.7 |
| PostTrainBench | 37.5 |
| MLE-bench-30 | 73.7% |
| SOL-ExecBench | 72.81 |

⚠️ All numbers are self-reported. No third-party independent verification published. SWE-bench Pro 73.6 methodology is not fully disclosed.

---

### Inference and API

NaiveRT, their custom inference stack (mega-kernel fusion, Programmatic Dependent Launch, speculative decoding):

- **Ultrafast mode**: up to 2,000 tokens/s (batch)
- **Standard mode**: ~50 tokens/s per user
- **API pricing**: $0.10/M input, $0.40/M output, $0.01/M cached

Local deployment requires ~315GB weights — serious hardware required.

---

### Boundaries

- 315GB weight size makes local deployment impractical for most setups
- All benchmarks self-reported, no independent verification
- AI architecture design described at high level; ablation details not released
- 7-month-old company; long-term engineering and research stability unproven

---

> MIT license. Released by NaiveAI on 2026-09-27, available on HuggingFace. For technical reference only.
