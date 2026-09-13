---
title: '人类造的最后一个 AI：递归自我改进的五个自主等级与 HCI 能力轨迹指标'
titleEn: "The Last AI Built by Humans: Five RSI Autonomy Levels and the HCI Capability Trajectory Index"
description: "33 位作者联合提出 HCI（Headroom-Closed Index）和五级递归自我改进框架：数学能力 HCI 86.4，工具 Agent 从 8.2 跳升至 39.9，L5 级 AI 将自主修改控制自身改进过程的机制。arXiv 2609.11873，CC BY-NC-ND 4.0。"
descriptionEn: "33 authors propose HCI (Headroom-Closed Index) and a five-level RSI autonomy framework: math capability HCI 86.4, tool agents surged from 8.2 to 39.9, L5 AI autonomously revises the mechanisms governing its own improvement process. arXiv 2609.11873, CC BY-NC-ND 4.0."
pubDate: "2026-09-13"
updatedDate: "2026-09-13"
category: "Research"
tags: ["recursive-self-improvement", "AI-autonomy", "HCI", "agent", "benchmark", "self-evolution", "frontier-AI"]
heroImage: "../../assets/images/last-ai-built-by-humans-recursive-self-improvement-hci-banner.jpg"
---

> 📌 论文：The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement
> arXiv：https://arxiv.org/abs/2609.11873
> 提交日期：2026-09-10 | 作者：33 人（通讯：Xuanhe Zhou）
> License：CC BY-NC-ND 4.0

---

标题很直白：如果递归自我改进（RSI）真的实现，AI 就会开始改进自己的改进过程——人类就不再是造 AI 的主体了。

这篇 33 位作者的联合论文试图回答两个问题：**我们现在在哪里，以及通往真正 RSI 的路程还有多远。**

---

## 一、HCI：一把能跨基准对比的尺子

现有基准测试是分散的——数学用 MATH，编程用 SWE-bench，知识用 MMLU，它们的满分、难度分布、年份都不一样，无法直接比较"数学能力进步了多少 vs 工具使用能力进步了多少"。

HCI（Headroom-Closed Index，剩余空间封闭指数）是这篇论文提出的统一刻度：

$$H = 100 \times \frac{\bar{s} - F_0}{100 - F_0}$$

- $F_0$：该基准**入场年**的第 90 百分位前沿分数（基线）
- $\bar{s}$：当前模型在该基准上的平均分
- $H = 0$：刚到入场年前沿水平；$H = 100$：满分

这个设计的作用是：把不同量纲、不同难度天花板的基准，全部压缩到同一个 0-100 进度条上，才能说"数学进步快，工具 Agent 进步慢"这样的话。

---

## 二、2023-2026 的能力轨迹：静态认知 vs 动态交互的裂缝

论文用 HCI 测量了 2023-2026 年各能力域的进展：

| 能力域 | HCI |
|-------|-----|
| 高等数学 | **86.4** |
| 研究生级科学 | **85.8** |
| 广泛知识 | **77.2** |
| 软件工程 | 52.6 |
| 搜索 Agent | 56.8 |
| 工具 Agent | 39.9（2026年前为 **8.2**） |

**裂缝很清楚**：静态认知能力（数学、知识）已经接近封顶，但动态交互能力（工具使用、Agent 任务执行）还只跑了一半不到。工具 Agent 的 2026 年加速——从 8.2 到 39.9——说明这条线开始快速追赶。

工业侧的数字给出了训练成本的参照：
- DeepSeek-V3.2 后训练计算量**超过预训练成本的 10%**
- NVIDIA AIMO-2 生成了 **320 万条推理解 + 170 万条工具集成解**
- GPT-5.6 六个月内内部编程推理量**增长 100 倍**

---

## 三、五级 RSI 自主等级

论文把递归自我改进分成五级，每一级对应人类控制权向 AI 转移的程度：

**L1 执行自主（Execution Autonomy）**
AI 执行人类预定义的改进程序。目标、方法、验收标准全部由人类指定。——今天大多数 RLHF/微调流程都在这一级。

**L2 策略自主（Strategy Autonomy）**
AI 能诊断自身弱点、在固定的基准和晋升规则内**选择**改进方法。人类设定规则，AI 选择路径。

**L3 经验自主（Experience Autonomy）**
AI 能**决定**自己在当前改进轮次需要什么训练经验——不只是执行，而是规划数据收集。

**L4 部署自主（Deployment Autonomy）**
改进循环利用**真实部署中的用户交互**来修改持久系统状态，外部治理结构仍然存在，但 AI 在它的边界内自主运行。

**L5 递归继承（Recursive Inheritance）**
AI 能持久修改控制**未来改进本身**的机制——包括改进器、验证器和策略规则。这才是标题意义上的"最后一个由人类建造的 AI"：从 L5 开始，AI 改进 AI，不再需要人类设计下一版训练流程。

---

## 四、三个核心挑战

论文没有回避 RSI 的困难，点出了三个技术上尚未解决的问题：

**安全继承**：持久化本身不等于持续收益。一次改进跑得好，不代表这个改进能传递给下一代模型——迁移测试和回滚机制是必要的，但当前缺乏标准。

**自主归因**：AI 的决策和"人类写死的固定程序"之间的边界很难划清。如果说 L2 是"AI 选方法"，那当方法选项是人类枚举的，它算不算真自主？归因模糊导致等级判断主观。

**可靠验证**：AI 改进完后怎么验证改进是真实的？如果 AI 反复访问评估器，它会学会"刷分"而不是"真正提高"。验证器和被改进系统的计算预算不匹配也是一个开放问题。

---

## 五、六个工业案例

论文对六个已部署系统做了结构分析：

| 系统 | 特点 |
|------|------|
| **Theseus** | 环境-数据-模型三者协同进化 |
| **Lark** | 企业级数据基础设施可靠性 |
| **Humanlaya** | 交付驱动的数据质量保证 |
| **ModelBest** | 零人工干预的工业 AI 工程 |
| **腾讯混元** | 经验驱动的自我改进循环 |
| **Agent-Native Research Lab** | 可验证 RSI 基础设施 |

这些系统都没有达到 L5，但每个都代表了 L2-L4 的不同实现路径。

---

## 拆解结论

HCI 是这篇论文最实用的贡献——它解决了"如何比较跨域能力进展"这个一直没有统一答案的问题。五级 RSI 框架更像是一张地图：我们现在在 L1-L2 之间的某处，L3-L4 是接下来几年的目标区域，L5 还是理论边界。

工具 Agent 从 8.2 跳到 39.9 是 2026 年最值得关注的单点信号——动态交互能力的追赶速度在加快，而这正是 RSI 成立的前提之一。

---

*arXiv 论文，CC BY-NC-ND 4.0，仅供学习阅读。*

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Paper: The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement
> arXiv: https://arxiv.org/abs/2609.11873
> Submitted: 2026-09-10 | Authors: 33 researchers (corresponding: Xuanhe Zhou)
> License: CC BY-NC-ND 4.0

---

The title is direct: if recursive self-improvement (RSI) is genuinely achieved, AI will start improving its own improvement process — and humans will no longer be the ones building AI.

This 33-author joint paper attempts to answer two questions: **where are we now, and how far is the road to genuine RSI?**

---

## I. HCI: A Ruler for Cross-Benchmark Comparison

Existing benchmarks are fragmented — math uses MATH, coding uses SWE-bench, knowledge uses MMLU. Their perfect scores, difficulty distributions, and baseline years all differ, making it impossible to directly compare "how much math capability improved vs. how much tool-use capability improved."

HCI (Headroom-Closed Index) is the unified scale proposed in this paper:

$$H = 100 \times \frac{\bar{s} - F_0}{100 - F_0}$$

- $F_0$: the 90th-percentile frontier score in the benchmark's **entry year** (baseline)
- $\bar{s}$: current model's average score on that benchmark
- $H = 0$: just reached entry-year frontier level; $H = 100$: perfect score

The value of this design: compress benchmarks with different units and difficulty ceilings onto the same 0-100 progress bar — making statements like "math improved fast, tool agents improved slowly" coherent.

---

## II. 2023–2026 Capability Trajectories: The Static Cognition vs. Dynamic Interaction Gap

The paper measures progress across domains using HCI over 2023–2026:

| Domain | HCI |
|--------|-----|
| Advanced mathematics | **86.4** |
| Graduate-level science | **85.8** |
| Broad knowledge | **77.2** |
| Software engineering | 52.6 |
| Search agents | 56.8 |
| Tool agents | 39.9 (was **8.2** before 2026) |

**The gap is clear**: static cognitive abilities (math, knowledge) are approaching saturation, while dynamic interactive capabilities (tool use, agent tasks) are barely halfway there. The tool-agent acceleration in 2026 — from 8.2 to 39.9 — signals this line is catching up fast.

Industrial-scale numbers provide a cost reference:
- DeepSeek-V3.2 post-training compute **exceeded 10% of pretraining cost**
- NVIDIA AIMO-2 generated **3.2M reasoning solutions + 1.7M tool-integrated solutions**
- GPT-5.6 saw **100× increase** in internal coding inference over six months

---

## III. Five RSI Autonomy Levels

The paper defines five levels, each corresponding to a further transfer of control from humans to AI:

**L1 Execution Autonomy**
AI executes human-predefined improvement procedures. Goals, methods, and acceptance criteria are all human-specified. — Most RLHF/fine-tuning pipelines today operate at this level.

**L2 Strategy Autonomy**
AI can diagnose its own weaknesses and **choose** improvement approaches within fixed benchmarks and promotion rules. Humans set the rules; AI picks the path.

**L3 Experience Autonomy**
AI can **decide** what training experience it needs for the current improvement round — not just executing, but planning data collection.

**L4 Deployment Autonomy**
The improvement loop uses **real user interactions from production deployment** to revise persistent system state. External governance structures remain, but AI operates autonomously within them.

**L5 Recursive Inheritance**
AI can persistently revise the mechanisms that govern **future improvement itself** — including improvers, verifiers, and policy rules. This is the "last AI built by humans" in the title's sense: from L5 onward, AI improves AI, without humans designing the next training pipeline.

---

## IV. Three Core Challenges

The paper doesn't dodge the hard problems. Three remain technically unsolved:

**Safe Inheritance**: persistence doesn't guarantee sustained gains. A successful improvement round doesn't mean that improvement transfers to the next model generation — transfer tests and rollback mechanisms are necessary but currently unstandardized.

**Autonomy Attribution**: the boundary between AI decisions and "human-hardcoded fixed procedures" is hard to draw. If L2 means "AI selects methods" but the method options are human-enumerated, does that count as genuine autonomy? Blurry attribution makes level classification subjective.

**Reliable Verification**: after improvement, how do you verify it's real? If AI repeatedly accesses an evaluator, it learns to "game the score" rather than genuinely improve. Compute budget mismatches between verifier and subject are also an open problem.

---

## V. Six Industrial Cases

The paper analyzes six deployed systems:

| System | Characteristic |
|--------|---------------|
| **Theseus** | Co-evolution of environment, data, and model |
| **Lark** | Enterprise data infrastructure reliability |
| **Humanlaya** | Delivery-driven data quality assurance |
| **ModelBest** | Zero-human industrial AI engineering |
| **Tencent Hunyuan** | Experience-driven self-improvement loops |
| **Agent-Native Research Lab** | Verifiable RSI infrastructure |

None have reached L5, but each represents a different implementation path through L2–L4.

---

## Teardown Summary

HCI is the most practically useful contribution here — it solves the "how to compare cross-domain capability progress" problem that has never had a unified answer. The five-level RSI framework is more like a map: we're somewhere between L1 and L2 today, L3–L4 is the target zone for the next few years, and L5 remains a theoretical boundary.

The tool-agent jump from 8.2 to 39.9 is the single most notable signal from 2026 — dynamic interactive capability is catching up fast, and that's exactly one of the prerequisites for RSI to become real.

---

*arXiv paper, CC BY-NC-ND 4.0, for reading and learning only.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
