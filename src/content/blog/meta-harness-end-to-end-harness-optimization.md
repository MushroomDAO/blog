---
title: "别再手搓 Agent 脚手架了：Stanford Meta-Harness 让 AI 自己搜索最优 harness"
titleEn: "Stop Hand-Crafting Agent Scaffolds: Stanford's Meta-Harness Searches for the Optimal Harness Automatically"
description: "Stanford IRIS Lab 的 Meta-Harness（arXiv:2603.28052，Chelsea Finn、Omar Khattab 等）把决定「给模型存什么、取什么、喂什么」的 harness 代码本身变成可自动优化的对象：用一个能读源码、分数和执行轨迹的 agentic proposer 做外层搜索。文本分类 +7.7 分且省 75% token，IMO 级数学 +4.7 分，TerminalBench-2 上自动发现的 harness 超过手工基线。"
descriptionEn: "Stanford IRIS Lab's Meta-Harness (arXiv:2603.28052; Chelsea Finn, Omar Khattab, et al.) makes the harness code — what to store, retrieve, and present to the model — an automatically optimizable object, via an agentic proposer that reads source, scores, and traces. +7.7 pts on text classification with 75% fewer tokens, +4.7 on IMO-level math, and discovered harnesses beat hand-engineered baselines on TerminalBench-2."
pubDate: "2026-06-19"
updatedDate: "2026-06-19"
category: "Research"
tags: ["AI Agent", "Harness优化", "Meta-Harness", "Stanford", "Chelsea Finn", "DSPy", "TerminalBench"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
---

> **BLUF**：一个 LLM 应用能力的高低，越来越不取决于模型本身，而取决于**包在模型外面的那层代码——harness**：决定给模型存什么、取什么、在每一步喂什么上下文。问题是，这层 harness 今天几乎全靠人手工调。Stanford IRIS Lab 的 **Meta-Harness**（论文 arXiv:2603.28052，作者含 Chelsea Finn、Omar Khattab）提出：**把 harness 本身变成可自动优化的对象**——用一个能访问历史候选的源码、分数和执行轨迹的 **agentic proposer**，在外层循环里系统地搜索更好的 harness 实现。结果很硬：文本分类比 SOTA 上下文管理系统高 **7.7 分**且省 **75%** 的 token；IMO 级数学在 5 个 held-out 模型上平均 **+4.7 分**；在 **TerminalBench-2** 上自动发现的 harness 超过手工调优的基线。这篇文章拆解它，并把它和我们刚写过的 Bayesian-Agent 接到同一条主线上。

---

## 一、"harness" 是什么？为什么它成了胜负手

先说清楚这个词。**Harness（脚手架）= 模型外面那层管控信息流的代码。** 同一个 GPT-5.2 或 Claude，套上不同的 harness，能力可以差出一大截。harness 决定的是：

- 该**存**什么进记忆、存多久；
- 该从历史/文档里**取**什么出来；
- 每一步该把什么上下文**喂**给模型、喂多少。

2026 年大家逐渐形成共识:模型权重 θ 你动不了(尤其闭源),真正能调的是**推理环境**——而 harness 正是推理环境的工程化核心。RAG 怎么检索、记忆怎么压缩、prompt 怎么组织、工具结果怎么回填……这些 harness 决策,常常比"换个更大的模型"影响更大。

但现状是:**harness 几乎全靠人手工设计和反复试错。** 工程师凭直觉调上下文窗口、写检索逻辑、改 prompt 模板,改一版跑一遍,慢且不可复现。Meta-Harness 想问的是:**这件事能不能让 AI 自己来搜?**

---

## 二、Meta-Harness 怎么做:让 Agent 去搜索更好的 Agent 脚手架

它的核心是一个**外层优化循环 + 一个 agentic proposer(提案器)**。

和那些"把反馈压缩成一句话再优化 prompt"的文本优化方法(比如部分 prompt 自动优化器)不同,Meta-Harness 认为**那种压缩对 harness 这种复杂对象损失太大**。它的提案器通过一个**文件系统接口**,能直接访问此前每个候选 harness 的:

1. **源代码**——不是抽象描述,是真实的实现;
2. **性能分数**——它在任务上跑得怎么样;
3. **执行轨迹**——它具体在哪一步、怎么做的、哪里出了问题。

提案器拿着这些"完整的实验档案",像一个工程师读代码 + 看日志 + 对分数那样,推理出下一个该怎么改,然后生成新的 harness 实现去跑。一轮轮迭代,**搜索的不是 prompt 一句话,而是整个 harness 的代码结构。**

论文一个很关键的发现:**给自动系统越丰富的历史实验数据访问权,它做 harness 工程就越有效。** 这和"把反馈狠狠压缩"的主流做法正好相反——信息不是越精简越好,对优化器而言,完整的源码 + 轨迹 + 分数才是最有价值的燃料。

---

## 三、结果:三个领域都打过手工基线

Meta-Harness 在三类差异很大的任务上验证:

| 任务 | 结果 |
|------|------|
| **文本分类** | 比 SOTA 上下文管理系统高 **7.7 分**,同时 context token 用量降 **75%** |
| **检索增强数学** | 200 道 IMO 级题目、5 个 held-out 模型上,平均准确率 **+4.7 分** |
| **Agentic 编程** | 在 **TerminalBench-2** 上,自动发现的 harness **超过手工调优基线** |

两点特别值得说:

1. **又涨分又省 token**:文本分类涨 7.7 分的同时砍掉 75% 上下文——这说明手工 harness 里塞了大量冗余上下文,而搜索出来的 harness 更"懂"该喂什么;
2. **跨模型泛化**:数学任务是在 **held-out(没参与搜索的)模型**上验证的,说明搜出来的 harness 不是过拟合到某个模型,而是学到了通用的信息流结构。

### 配套开源:TerminalBench-2 上的具体实现

仓库(stanford-iris-lab/meta-harness-tbench2-artifact)放出了在 TerminalBench-2 上的具体 agent。它在 Terminus-KIRA 架构基础上,加了一个很巧的 **"环境自举"(environment bootstrapping)** 技巧:**与其让 agent 花好几轮去 `ls`、`which` 摸清环境,不如在初始 prompt 里直接注入一份沙箱快照**(工作目录、文件清单、可用语言/工具、包管理器、内存)。光这一招就省掉 2-5 个早期探索步骤。用 Claude Opus 4.6 跑 89 个任务、5 轮,总成功率 **76.4%**(简单 100%、中等 81.1%、困难 64.7%)。

这个"环境自举"正是 Meta-Harness 那套自动搜索能发现的那类 harness 改进的一个具体样本——一个人类也想得到、但需要系统化搜索才能稳定找出并验证的优化点。

---

## 四、接上主线:这是"优化 C 而非 θ"的又一块拼图

如果你读过我们今天那篇 **Bayesian-Agent**,会发现 Meta-Harness 和它指向同一个底层范式转换。

任何 Agent 系统都在从 `P(X | θ, C)` 采样:θ 是冻结的模型,C 是推理环境(harness、技能、SOP、记忆、工具)。两篇工作,殊途同归地把功夫下在 **C** 上:

- **Bayesian-Agent**:用后验概率治理**技能/SOP** 的留改删——C 里的"知识与流程"层;
- **Meta-Harness**:用 agentic 搜索优化 **harness 代码本身**——C 里的"信息流控制"层。

再往上追溯,这条线还连着 **DSPy**(Omar Khattab 正是 DSPy 作者,也在 Meta-Harness 作者名单里)——DSPy 把 prompt 和 pipeline 变成可编译、可优化的程序;Meta-Harness 相当于把优化的对象从 prompt/pipeline 进一步抬升到**整个 harness 的代码结构**。

一句话概括 2026 年的这股潮流:**模型越来越像不可改的 CPU,真正的工程红利在「编译器和操作系统」——也就是 harness 这一层。谁能把这层自动化、可搜索、可治理,谁就能在不换模型的前提下持续榨出性能。**

---

## FAQ

**Q：Meta-Harness 需要训练或微调模型吗？**
A：不需要。它优化的是模型外的 harness 代码,模型权重全程冻结。数学任务还专门在 held-out 模型上验证了泛化性。

**Q：它和普通的 prompt 自动优化(如 prompt 搜索)有什么区别？**
A：普通 prompt 优化往往把反馈压缩成精简信号,且只动 prompt 文本。Meta-Harness 让提案器读完整源码 + 执行轨迹 + 分数,搜索的是**整个 harness 的代码实现**,粒度和信息量都大得多。

**Q：普通团队能用上吗？**
A：论文方法偏研究性质,但配套仓库给出了 TerminalBench-2 上可复现的 agent 实现,里面的"环境自举"等技巧可以直接借鉴到自己的 Agent 脚手架里。代码见 GitHub。

---

> 📌 原文与资源(请直接复制访问):
> 论文 arXiv:2603.28052 —— https://arxiv.org/pdf/2603.28052
> GitHub —— https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用,须注明作者姓名及原文链接,不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: An LLM application's capability increasingly depends not on the model itself but on the **harness** wrapped around it — the code deciding what to store, retrieve, and present to the model at each step. The problem: that harness is almost entirely hand-tuned today. Stanford IRIS Lab's **Meta-Harness** (paper arXiv:2603.28052; authors include Chelsea Finn and Omar Khattab) proposes making **the harness itself an automatically optimizable object** — via an **agentic proposer** that accesses prior candidates' source code, scores, and execution traces in an outer-loop search. The results are concrete: **+7.7 points** on text classification with **75% fewer** tokens; **+4.7** average on IMO-level math across five held-out models; and on **TerminalBench-2**, discovered harnesses beat hand-engineered baselines. We break it down and connect it to today's Bayesian-Agent piece.

---

## 1. What Is a "Harness," and Why Is It the Decider?

A **harness is the code outside the model that controls information flow.** The same GPT-5.2 or Claude, under different harnesses, varies wildly in capability. The harness decides what to *store* in memory and for how long, what to *retrieve* from history/documents, and what context to *present* at each step.

The 2026 consensus: you can't touch weights θ (especially closed models); what you *can* tune is the inference environment — and the harness is its engineering core. How RAG retrieves, how memory compresses, how prompts are organized, how tool results are fed back — these harness decisions often matter more than "use a bigger model." Yet today the harness is hand-designed via trial and error: slow, intuition-driven, irreproducible. Meta-Harness asks: **can AI search for it automatically?**

## 2. How Meta-Harness Works: An Agent Searching for Better Agent Scaffolds

The core is an **outer optimization loop + an agentic proposer**. Unlike text-optimization methods that compress feedback into a one-liner before optimizing the prompt — too lossy for an object as complex as a harness — Meta-Harness's proposer accesses, via a filesystem interface, each prior candidate's **source code**, **performance scores**, and **execution traces**.

Holding these complete "experimental dossiers," the proposer reasons like an engineer reading code + logs + scores, then generates a new harness implementation to run. Iteration by iteration, **it searches over the harness's code structure, not a single prompt sentence.** A key finding: **the richer the access to prior experimental data, the more effective the automated harness engineering** — the opposite of "compress feedback hard." For an optimizer, full source + traces + scores is the most valuable fuel.

## 3. Results: Beating Hand-Engineered Baselines in Three Domains

| Task | Result |
|------|--------|
| **Text classification** | **+7.7 pts** over a SOTA context-management system, with **75% fewer** context tokens |
| **Retrieval-augmented math** | **+4.7 pts** average across 200 IMO-level problems on five held-out models |
| **Agentic coding** | Discovered harnesses **beat hand-engineered baselines** on **TerminalBench-2** |

Two highlights: (1) **higher score *and* fewer tokens** — the hand-built harness was stuffed with redundant context the searched one trims; (2) **cross-model generalization** — math was validated on **held-out** models, so the discovered harness learned general information-flow structure rather than overfitting one model.

### Companion open-source: the TerminalBench-2 artifact

The repo (stanford-iris-lab/meta-harness-tbench2-artifact) releases the concrete TerminalBench-2 agent. Built on the Terminus-KIRA architecture, it adds a clever **environment bootstrapping** trick: rather than spending turns running `ls`/`which` to discover system state, it **injects a sandbox snapshot** (working dir, file listing, available languages/tools, package managers, memory) into the initial prompt — eliminating 2-5 early exploration steps. With Claude Opus 4.6 over 89 tasks × 5 trials, it hits **76.4%** overall (easy 100%, medium 81.1%, hard 64.7%). This bootstrapping is exactly the kind of harness improvement the automated search is built to find and verify systematically.

## 4. The Through-Line: Another Piece of "Optimize C, Not θ"

If you read today's **Bayesian-Agent** piece, Meta-Harness points at the same paradigm shift. Any agent samples from `P(X | θ, C)` — θ frozen, C the inference environment (harness, skills, SOPs, memory, tools). Both works put the effort into **C**: Bayesian-Agent governs **skills/SOPs** via posterior probabilities (the "knowledge & procedure" layer); Meta-Harness optimizes the **harness code itself** via agentic search (the "information-flow control" layer).

Trace it further and the line connects to **DSPy** (Omar Khattab, a DSPy author, is on the Meta-Harness byline) — DSPy turns prompts and pipelines into compilable, optimizable programs; Meta-Harness lifts the optimization target from prompt/pipeline up to the **whole harness code structure**.

One sentence for the 2026 trend: **the model is increasingly an unchangeable CPU; the real engineering dividend is in the "compiler and OS" — the harness layer. Whoever automates, searches, and governs that layer keeps extracting performance without swapping models.**

## FAQ

**Q: Does Meta-Harness train or fine-tune the model?**
A: No. It optimizes the harness code outside the model; weights stay frozen. Math results were validated on held-out models to confirm generalization.

**Q: How is it different from ordinary prompt auto-optimization?**
A: Prompt optimizers usually compress feedback and only edit prompt text. Meta-Harness lets the proposer read full source + traces + scores and searches the entire harness implementation — far more granular and information-rich.

**Q: Can ordinary teams use it?**
A: The method is research-grade, but the companion repo offers a reproducible TerminalBench-2 agent whose tricks (e.g., environment bootstrapping) you can borrow directly into your own scaffolds. Code on GitHub.

---

> 📌 Source & resources (copy to visit):
> Paper arXiv:2603.28052 — https://arxiv.org/pdf/2603.28052
> GitHub — https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
