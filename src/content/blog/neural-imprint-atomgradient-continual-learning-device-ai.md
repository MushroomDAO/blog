---
title: "Neural Imprint：让部署中的 AI 模型真正从经验中学习，而不是每次从零开始"
titleEn: "Neural Imprint: Making Deployed AI Models Actually Learn from Experience Instead of Starting from Scratch Every Time"
description: "质子梯度（AtomGradient）发布 Neural Imprint 白皮书 v2（2026-09-17），提出让已部署 AI 在持续使用中积累经验、更新模型状态，无需重新训练。三个 Gen-1 组件：RPP（激活空间用户建模）、DSR（稀疏注意力缓存管理）、FrogJump（层跳过加速）。实测：90B 模型在手机上跑 200 轮对话峰值 5.5GB，语音合成中位延迟 32.28ms。CC BY-NC-ND 4.0。"
descriptionEn: "AtomGradient releases Neural Imprint whitepaper v2 (2026-09-17), proposing that deployed AI models accumulate experience and update model states during ongoing use without retraining. Three Gen-1 components: RPP (activation-space user modeling), DSR (sparse attention cache management), FrogJump (layer-skip acceleration). Benchmarks: 90B model, 200-turn conversations on a smartphone at 5.5GB peak memory; speech synthesis at 32.28ms median latency. CC BY-NC-ND 4.0."
pubDate: "2026-09-18"
updatedDate: "2026-09-18"
category: "Research"
tags: ["continual-learning", "on-device-AI", "AI-research", "model-personalization", "inference", "memory", "whitepaper"]
heroImage: "../../assets/images/neural-imprint-atomgradient-continual-learning-device-ai-banner.jpg"
---

> 📌 白皮书：https://atomgradient.github.io/whitepapers/neural-imprint/
> 机构：AtomGradient（质子梯度，北京）| License：CC BY-NC-ND 4.0
> 版本：Whitepaper v2，发布日期：2026-09-17

---

现在大多数 AI 应用的工作方式是这样的：你用了一千次，它还是和第一次一样，什么都没有从你这里学到。能记住的，是上下文窗口里放得下的内容；上下文满了或者会话结束，全部清零。

**Neural Imprint（NI）**想解决的正是这个问题：**让已经部署的模型，在持续使用中真正积累经验，把学到的东西写进模型状态，而不是靠外部数据库检索或者不断拼接上下文。**

这是质子梯度（AtomGradient）2026 年 9 月 17 日发布的白皮书 v2，框架核心一句话：**"Intelligence moves toward data"**——让学习发生在数据所在的地方（用户设备），而不是把数据搬到中心服务器再训练。

---

## 问题：现有方法都差在哪里

| 方法 | 能做什么 | 做不到什么 |
|------|---------|-----------|
| 上下文拼接 | 直接访问历史 | 上下文满了就丢，学不进模型参数 |
| 外部检索（RAG） | 保留原始内容，随时查 | 离线时不可用，换设备带不走能力 |
| 语言摘要 | 紧凑表示 | 只剩文字，多维结构信息丢失 |

NI 的路子不同：把学习的"成果"直接写进模型状态（而非外部存储），让状态参与后续的推理。原始数据不用重新输入，迁移设备时带着状态走，即便离线也能用之前学到的东西。

---

## Gen-1 架构：三个核心组件

白皮书当前（v2）描述的是第一代实现，三个组件各管一块：

### RPP — Residual Pattern Projection（残差模式投影）

用主成分分析（PCA）在模型激活空间里分析用户相关的结构。它不直接看用户说了什么，而是看激活向量里"哪个方向和这个用户有关"——类似于在高维空间里给用户画一个特征图，每次新记录进来就更新这张图，产出新的用户状态表示。

### DSR — Dual-Sparse Retention（双稀疏保留）

管理注意力缓存（KV cache）的分配。它用两个维度来决定哪些缓存值得保留：**重要性分数**（这一段信息对当前任务贡献多大）+ **时间邻近度**（越新越可能有用）。两个维度结合，动态裁剪缓存而不是简单地按时间先进先出删。

### FrogJump（蛙跳）

跳过选定的计算层，同时保留关键计算。不是简单地剪枝，而是在推理时判断哪些层可以跳、哪些层必须算，实现速度与质量的平衡。

三个组件配合一套推理运行时：管理模型权重、会话状态、内存分配，以及工具契约（让模型知道能调用哪些函数）和激活引导（让外部输入调整参数方向）。

---

## 学习循环：一次对话后发生了什么

```
观察（用户输入/环境反馈）
    ↓
行动（模型推理、工具调用）
    ↓
反馈（结果、用户评价、隐式信号）
    ↓
状态更新（RPP 分析新记录 → 更新用户状态 → 写入推理状态）
    ↓
下次对话：从更新后的状态恢复，而非从零开始
```

关键是"状态更新"这一步：系统识别哪些新记录是有变化的（增量更新），对这部分做表示提取，再通过 RPP 更新用户画像，最后把更新后的状态注入到下次推理里。原始数据不用重播，更新代价和新增信息量正比。

---

## 实测数据

白皮书列出三个已在真实设备上验证的指标：

| 场景 | 数据 |
|------|------|
| 90B 参数模型，手机，200 轮对话 | 峰值内存 5.5 GB |
| 多图像会话状态保留 | 延迟降低约 1.5 秒 |
| 语音合成（非苹果平台） | 中位延迟 32.28ms |

90B 模型在手机上跑 200 轮、峰值 5.5 GB，是目前最直接的 on-device 大模型内存管理数据之一。这个数字如果可靠，说明 FrogJump + DSR 组合的内存控制效果是实质性的，不只是理论。

---

## 为什么这件事难

白皮书诚实地列出了六个核心挑战，这部分读起来比大多数论文更有价值，因为它指出了"做不到"的边界：

1. **表示泛化**：为还没见过的任务形成有效的内部表示
2. **状态到能力的转化**：状态改变了，能力真的提升了吗？怎么验证？
3. **行动后果推断**：从相关性走向因果，模型需要预测"我做 X 之后会发生 Y"
4. **可塑性与稳定性平衡**：接受真正有价值的新信息，同时抵抗噪声和遗忘
5. **设备约束内化**：不是在算法外面加硬件约束，而是把约束内嵌进算法本身
6. **异构迁移**：在不同架构的设备间，什么真的能带走、什么带不走

这六个问题每一个都是独立的研究方向，而且是目前学术界还没有公认答案的问题。

---

## 下一代研究方向

白皮书明确列出了 Gen-2 要做的事，可以理解为一份公开的研究议程：

- **更细粒度的增量更新**：成本只和新增信息量正比，而不是全量重算
- **能力巩固**：区分"快速适应"（当下有用）和"长期记忆"（跨任务稳定）
- **多时间尺度学习**：不同的学习率对应不同深度的知识
- **世界模型集成**：把行动预测和后果理解连起来
- **跨设备连续性**：在异构设备间保留习得的能力
- **可控学习**：用户对"AI 学了什么"有真正的控制权

最后一条在当前 AI 发展语境下特别值得关注：模型在使用中自主学习，同时用户能审查和撤销学到的内容，这是用户主权和能力积累之间的平衡问题。

---

## 这件事为什么重要

现在的 AI 个性化主要靠两种方式：要么把用户数据传回中心服务器做微调，要么在上下文里塞历史记录。前者有隐私风险和成本问题，后者遇到上下文长度上限就失效。

Neural Imprint 指向第三条路：**模型在本地积累，状态随设备走，不用联网，不用把数据传到别处**。这和"数据主权"、"边缘计算"这些趋势方向一致，但是落到了一个具体的技术实现层面——不是泛泛的架构理念，而是带着三个已实现的 Gen-1 组件和六个已明确的研究挑战。

白皮书框架的比喻很有意思：把经验类比为"在高维空间里贴便利贴"，选择性叠加而不互相干扰，越重要的越稳，越边缘的越易被覆盖。这个比喻其实是对 RPP 工作方式的直觉描述——在激活空间的特定方向上，只更新和用户相关的那些维度。

质子梯度（AtomGradient）是北京的 AI 研究机构，这是他们的第二版白皮书。技术路线和他们之前的工作（推理运行时优化）一致。目前没有开源代码，白皮书本身用 CC BY-NC-ND 4.0 授权，可以引用不能商业化。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Whitepaper: https://atomgradient.github.io/whitepapers/neural-imprint/
> Organization: AtomGradient (质子梯度, Beijing) | License: CC BY-NC-ND 4.0
> Version: Whitepaper v2, published 2026-09-17

---

Most AI applications today work like this: use them a thousand times and they're the same as on day one — nothing learned from you. What they "remember" is limited to what fits in the context window; when the context is full or the session ends, everything resets.

**Neural Imprint (NI)** addresses exactly this: **making deployed models genuinely accumulate experience through ongoing use, writing what's learned into model states — not into an external database, not by concatenating more context.**

This is AtomGradient's whitepaper v2, published September 17, 2026. The framework's thesis in one phrase: **"Intelligence moves toward data"** — learning happens where the data lives (the user's device), rather than shipping data to a central server for retraining.

---

## The Problem: What Existing Methods Miss

| Method | What it does | What it can't do |
|--------|-------------|-----------------|
| Context stacking | Direct access to history | Context fills up; nothing internalizes into model parameters |
| External retrieval (RAG) | Preserves original content | Offline unavailable; capabilities don't migrate across devices |
| Language summarization | Compact representation | Loses multi-dimensional structure; only text survives |

NI takes a different path: learning outcomes are written directly into model states (not external storage), and those states participate in subsequent reasoning. The original data doesn't need to be replayed, the state migrates with you across devices, and it works offline using what was already learned.

---

## Gen-1 Architecture: Three Core Components

The current whitepaper (v2) describes the first-generation implementation with three components:

### RPP — Residual Pattern Projection

Uses PCA to analyze user-related structure inside model activations. Rather than looking at what the user said, it identifies which directions in the activation space correlate with this user — effectively drawing a feature map of the user in high-dimensional space. Each new record updates the map; the output is an updated user state representation.

### DSR — Dual-Sparse Retention

Manages KV cache allocation along two dimensions: **importance score** (how much does this segment contribute to the current task) + **temporal proximity** (more recent = more likely relevant). Together these dynamically prune the cache rather than simple FIFO eviction.

### FrogJump

Skips selected computation layers while preserving critical ones. Not simple pruning — at inference time it judges which layers can be skipped and which must be computed, trading off speed against quality.

These three components operate alongside a specialized inference runtime: managing model weights, session state, memory allocation, plus tool contracts (what functions the model can call) and activation steering (external inputs that adjust parameter direction).

---

## The Learning Cycle: What Happens After One Conversation

```
Observation (user input / environment feedback)
    ↓
Action (model reasoning, tool calls)
    ↓
Feedback (results, user evaluation, implicit signals)
    ↓
State update (RPP analyzes new records → updates user state → writes into inference state)
    ↓
Next conversation: restores from updated state, not from zero
```

The key is the state update step: the system identifies which new records have changed (incremental update), extracts representations for those, updates the user profile via RPP, then injects the updated state into the next inference. No data replay needed; the update cost scales proportionally with new information.

---

## Benchmark Data

Three metrics verified on actual devices:

| Scenario | Result |
|----------|--------|
| 90B model, smartphone, 200-turn conversation | 5.5 GB peak memory |
| Multi-image session state preservation | ~1.5 second latency reduction |
| Speech synthesis (non-Apple platform) | 32.28ms median latency |

A 90B model running 200 turns on a smartphone at 5.5 GB peak is one of the more direct on-device memory management data points available. If these numbers are reproducible, the FrogJump + DSR combination represents real, not just theoretical, memory efficiency.

---

## Why This Is Hard

The whitepaper honestly lists six core challenges — more valuable to read than most papers because it marks where "we can't yet":

1. **Representation generalization**: forming useful internal representations for tasks not yet encountered
2. **State-to-ability translation**: the state changed — did the capability actually improve? How to verify?
3. **Action consequence inference**: moving from correlation toward causality — predicting "if I do X, Y happens"
4. **Plasticity–stability balance**: accepting genuinely valuable new information while resisting noise and forgetting
5. **Device constraint internalization**: not adding hardware constraints around algorithms, but embedding them inside the algorithm itself
6. **Heterogeneous migration**: across architecturally different devices, what genuinely transfers and what doesn't

Each of these is an independent research direction with no settled answer in the current literature.

---

## Next-Generation Research Agenda

The whitepaper's Gen-2 directions function as a public research agenda:

- **Finer-grained incremental updates**: cost proportional to new information volume, not full recomputation
- **Capability consolidation**: distinguishing rapid adaptation (useful now) from long-term stable knowledge
- **Multi-timescale learning**: different learning rates for different depths of knowledge
- **World model integration**: connecting action prediction with consequence understanding
- **Cross-device continuity**: preserving acquired capabilities across heterogeneous devices
- **Controllable learning**: users have genuine authority over what the AI learns and retains

The last point is particularly relevant in the current AI moment: a model that autonomously learns through use, while users can audit and revoke what was learned, sits at the intersection of user sovereignty and capability accumulation.

---

## Why This Matters

Current AI personalization takes two paths: either ship user data to a central server for fine-tuning (privacy risk, cost), or stuff history into context (hits the length limit and fails). Neural Imprint points toward a third: **models accumulate locally, states travel with the device, no cloud dependency, no data leaving the user's control.**

This aligns with data sovereignty and edge computing trends — but at a specific technical implementation level, not as a vague architectural philosophy. Three Gen-1 components already built, six research challenges already named.

The whitepaper's metaphor is worth noting: experiences as "sticky notes layered across dimensional spaces, selectively overlapping without interfering." This is an intuition pump for how RPP works — in the activation space's specific directions, only the dimensions relevant to the user get updated.

AtomGradient (质子梯度) is a Beijing AI research organization; this is their second whitepaper. The technical approach is consistent with their prior work on inference runtime optimization. No open-source code currently. The whitepaper itself is CC BY-NC-ND 4.0 — citable, not commercially adaptable.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
