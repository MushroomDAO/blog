---
title: "32B 小模型逼近 GPT-5.2：S1-DeepResearch 如何用数据而非参数训练长程研究 Agent"
titleEn: "A 32B Model Closing in on GPT-5.2: How S1-DeepResearch Trains Long-Horizon Research Agents with Data, Not Scale"
description: "ScienceOne 开源 S1-DeepResearch-32B，能连续调用工具 150+ 轮、跨 20 个基准逼近 GPT-5.2/Claude-4.6/GLM-5，却只用 SFT、不用 RL。它的秘密是一套图谱驱动的轨迹构造范式：知识图谱出题、Agent 跑轨迹、五维验证过滤。本文拆解方法、跑分，并梳理业界对深度研究 Agent 的反思。"
descriptionEn: "ScienceOne open-sourced S1-DeepResearch-32B: 150+ consecutive tool calls, approaching GPT-5.2/Claude-4.6/GLM-5 across 20 benchmarks — using SFT only, no RL. Its trick is a graph-grounded trajectory construction paradigm. We break down the method, the numbers, and where the industry's thinking on deep research agents is heading."
pubDate: "2026-06-19"
updatedDate: "2026-06-19"
category: "Research"
tags: ["AI Agent", "Deep Research", "深度研究", "长程任务", "轨迹数据", "Qwen3", "开源模型", "S1-DeepResearch"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

> **BLUF**：ScienceOne 团队开源了 **S1-DeepResearch**（论文 arXiv:2606.15367，模型 32B + 8B-Preview，Apache 2.0）。它最反直觉的一点是：一个 **32B 的小模型，只靠监督微调（SFT）、完全不用强化学习**，就在覆盖 5 大能力、20 个基准的评测里逼近 GPT-5.2、Claude-4.6、GLM-5 这些闭源旗舰，甚至在文本推理上追平了体量大 71 倍的 Qwen3.5-397B。它的核心不是模型架构，而是一套**「知识图谱出题 → Agent 跑轨迹 → 五维验证」的数据构造范式**，以及随之开源的 **15K 高质量 Agent 轨迹数据集**。这篇文章拆解它怎么做到的，并梳理业界对「深度研究 Agent」这条路线的最新反思。

---

## 一、深度研究 Agent 卡在哪？

过去一年，「Deep Research」从 OpenAI、Google 的产品名，变成了一整类 Agent 能力的统称：给一个复杂问题，让模型自己上网搜索、读文件、跑代码、反复推理，最后产出一份带引用的报告。这件事听起来简单，工程上却极难——因为它要求模型在**长程（long-horizon）、多跳（multi-hop）**的任务里持续保持状态、不跑偏、不幻觉。

而真正卡住开源社区的，不是模型不够大，而是**训练数据的形态错了**。S1 团队的判断很直接：现有的 Agent 训练数据**过度集中在「搜索」这一个动作上**（search-centric）。大量数据集本质是「多跳问答」——把答案藏深一点，逼模型多搜几次。但真实的研究工作远不止搜索：

- 你要**读懂一个 PDF、一张表格、一段网页**，而不只是检索关键词；
- 你要**遵守复杂指令**——"只用 2024 年后的一手资料""分三部分""每段不超过 200 字"；
- 你要**写出有据可查的报告**，每个论点都能追溯到引用；
- 你要**调用技能**——画图、跑数据分析、生成文件，而不是把代码塞在聊天框里。

只在「搜索」上训练出来的 Agent，benchmark 分数可能不低，但一碰真实任务就露馅。S1-DeepResearch 想解决的，正是这个**「能力维度太窄」**的根本问题。

---

## 二、S1-DeepResearch 是什么？

一句话：一个**端到端的长程深度研究模型系统**，把上面四类被忽视的能力和「搜索」一起，统一进了训练目标。

关键规格：

| 维度 | 参数 |
|------|------|
| 模型 | S1-DeepResearch-**32B**（旗舰）+ **8B-Preview**（轻量探索版） |
| 基座 | Qwen3 |
| 上下文 | **128K** tokens |
| 连续工具调用 | **150+ 轮** |
| 内置工具 | 9 类（网页搜索、学术搜索、网页浏览、图像/视频分析、文件解析、代码执行、命令行等） |
| 许可证 | **Apache 2.0**（模型 + 15K 轨迹数据集全开源） |

它把深度研究拆成**五个能力维度**，并在每个维度上都构造了训练数据：

1. **长链复杂推理** —— 多文档检索、证据聚合、跨多轮维持状态记忆；
2. **研究指令遵循** —— 解析带多重约束的研究指令；
3. **研究报告写作** —— 产出有引用、可溯源的结构化报告；
4. **文件理解与生成** —— 处理 PDF、表格、网页并生成结构化产物；
5. **技能调用** —— 文献检索、数据分析、可视化等模块化能力。

"150+ 连续工具调用"是个值得停下来体会的数字：它意味着模型要在一条任务里做上百次「观察环境→决策→调工具→读反馈」的循环而不崩溃。这正是「长程」二字的含金量所在。

---

## 三、核心方法：用数据，而不是参数

S1 最大的贡献不在模型，而在**怎么造出那 15K 条高质量轨迹**。整套范式分三步。

### 第一步：知识图谱出题（Graph-Grounded Task Formulation）

不是让 LLM 凭空编题，而是**让知识图谱来保证题目的复杂度可控、可验证**。

- **种子实体**从 Wikipedia 选取，经过拓扑结构、热度、信息密度、可搜索性、安全性五重过滤；
- 围绕每个实体，用 Wikidata 关系 + 网页搜索结果展开成一张**有向无环图（DAG）**，并纳入多模态信息（文本实体、视觉概念）；
- 出题前先注入**九个约束维度**（信息来源、论证方式、推理路径、目标、假设、输出格式、规模、执行、上下文），界定探索边界；
- 对闭式问答，用「实体语义改写 + 条件泛化」反复重写题目，**削弱问题和答案之间的直接关联**，逼模型真去推理而非背答案；
- 最关键的过滤：先**不给工具**让模型裸答一遍（过滤掉靠参数记忆就能答的题），再用信息流、反馈依赖、宽度、深度四个指标度量推理图复杂度，**只保留最难的前 30%**。

这一步解决的是「题目质量」——垃圾进、垃圾出，数据范式的成败首先取决于题出得够不够硬。

### 第二步：Agent 跑轨迹（Agentic Trajectory Rollout）

有了题，让 Agent 在一个**真实的 9 类工具环境**里实际去解，记录下完整轨迹：

> τ = (x, a₁, o₁, a₂, o₂, …, aₜ, oₜ, y)

其中 x 是任务，aₜ 是模型的动作，oₜ 是环境观测（网页、解析后的文件、代码执行结果），y 是最终回答。模型反复「观察→决策→调工具→收反馈」，自然产生长程多步行为。

然后做**场景化精修**，把轨迹改造成更真实的形态：报告类强化证据连贯性；文件类把文本输出转成可执行产物；多模态类插入原生视觉输入；技能类把内联代码转成文件附件。这一步让训练数据贴近真实研究产物，而不是干巴巴的问答对。

### 第三步：五维验证过滤（Multi-Dimensional Verification）

跑出来的轨迹大部分是噪声，必须严格过滤。S1 按五条能力轨道分别验证：

- **复杂推理**：LLM-as-judge 对照参考答案校验逻辑正确性和中间推导；
- **报告生成**：引用校验器检查正文引用是否真实对应参考、是否提供实质支撑；
- **指令遵循**：九维约束检查器逐项核对；
- **文件任务**：验证轨迹与可执行代码的一致性、与任务的语义对齐；
- **技能调用**：追踪技能是否正确激活、是否有效、资源利用率如何。

三步走完，沉淀出 **15,000 条**横跨五大维度的高质量轨迹。

### 一个反直觉的设计：只用 SFT，不用 RL

值得专门点出：S1 的训练**只有监督微调，没有强化学习**。目标函数就是让模型同时模仿中间动作和最终回答：

> ℒ = −Σ log p(aₜ | x, a<t, o<t) − log p(y | x, a≤T, o≤T)

在「人人都在卷 Agentic RL」的 2026 年，这是一个有点逆潮流的选择。它传递的信号是：**当数据质量足够高、能力维度足够全时，SFT 本身就能把一个 32B 模型推到逼近旗舰的水平**——参数效率来自数据,而非堆规模或堆 RL。这对算力有限的团队是个重要的方法论参考。

---

## 四、跑分：32B 追平百亿级旗舰

S1 在覆盖 5 大维度的 **20 个 Agentic 基准**上做了评测（含 GAIA、BrowseComp、BrowseComp-ZH、XBench-DeepSearch、HLE、DeepResearch Bench、ComplexBench、FileSys、GTA、SkillsUse 等）。论文报告的几组关键数字：

**相对基座 Qwen3-32B 的提升（同样 32B，差距全来自训练数据）：**

| 基准 | Qwen3-32B | S1-DeepResearch-32B |
|------|-----------|---------------------|
| GAIA（文本） | 30.2 | **72.8** |
| DeepResearch Bench | 36.0 | **46.5** |
| DeepResearchIF（查询准确率） | 4.1 | **25.2** |
| FileSys（文件系统任务） | 44.7 | **69.3** |

GAIA 文本从 30 分翻到 72 分、指令遵循从 4 分跳到 25 分——这种量级的提升，纯粹来自数据，没有动模型架构。

**相对闭源旗舰：** 论文称整体性能**接近 GPT-5.2、Claude-4.6、GLM-5**——报告生成逼近 GPT-5.2（48.7 vs 51.4），文件任务达到 GLM-5 水平（尽管参数差 23 倍）。更具冲击力的是：在文本推理上，**32B 的 S1 追平了体量大 71 倍的 Qwen3.5-397B**。

> ⚠️ 需要客观看待：这 20 个基准是团队**自己选定**的能力维度，"逼近旗舰"是在这套评测口径下的结论；闭源模型在更开放的真实任务上仍可能有优势。但即便打个折扣，"32B + 纯 SFT 逼近百亿级旗舰"这个结论本身，已经足够说明数据范式的威力。

---

## 五、业界在思考什么？深度研究 Agent 的三条暗线

S1 不是孤例。把它放进 2026 年的大背景里看，会发现整个领域正沿三条暗线推进。

### 暗线一：竞争焦点从「模型」转向「轨迹数据怎么造」

S1 之外，同期还有一批工作在解同一个问题：

- **Tongyi DeepResearch**（通义，技术报告 arXiv:2510.24701）系统性地论证了合成轨迹数据对深度研究能力的决定性作用；
- **OpenResearcher**（arXiv:2603.20278）干脆开源了一整套「长程深度研究轨迹合成」的全流程管线；
- **Marco DeepResearch**（arXiv:2603.28376）则主打「以验证为中心」的设计来提升 Agent 效率。

共识正在形成：**深度研究能力的瓶颈不在基座模型，而在能不能规模化地造出高质量、多维度、可验证的轨迹数据**。S1 的三步范式，是这条路线上一个相当完整的样本。

### 暗线二：评测本身成了战场

当大家都宣称「逼近 GPT-5.2」，怎么评测就变得至关重要。2026 年涌现了一批专门修正评测口径的工作：

- **BrowseComp-Plus**（ACL 2026）用**固定语料库**把「检索器」和「Agent 推理」解耦，让对比公平、可复现——因为开放网络评测里，分数高可能只是因为它搜到了更好的页面，而非推理更强；
- **DeepResearch Bench**（arXiv:2506.11763）、**DeepResearchEval**（arXiv:2601.09688）则在构建更贴近真实研究任务的自动化评测框架。

这背后是一个尖锐的质疑：**刷榜分数 ≠ 真实有用**。

### 暗线三：对「自主性」的祛魅

最值得创业者和研究者警惕的是 arXiv:2512.01948 这篇《How Far Are We from Genuinely Useful Deep Research Agents?》提出的反思。它指出当前深度研究 Agent 普遍存在一个**「性能—效用鸿沟」（performance-utility gap）**：

1. **任务复杂度**：真实研究是细腻、多面的问题，远超简单检索或事实核查；
2. **信息整合**：Agent 擅长检索，但很难把分散来源**综合成推进认知的连贯叙事**；
3. **推理深度**：缺乏迭代式假设检验和实质性分析推理的机制；
4. **用户对齐**：系统倾向于优化「任务完成」，而非满足研究者真正的认知目标。

它的结论很冷静：**当前 Agent 的「自主」宣称可能被高估了，人类的监督和迭代修正仍然不可或缺。**——这是给所有「全自动研究 Agent」叙事的一盆冷水，也是 S1 这类工作下一步真正要跨越的鸿沟。

---

## 六、这对我们意味着什么？

把三条暗线收拢，S1-DeepResearch 的价值有三层：

1. **对开发者**：它和 15K 数据集都是 Apache 2.0 开源的。如果你在做垂直领域的研究 Agent，这套「图谱出题→轨迹→验证」的范式比直接拿模型微调更值得借鉴——**先把数据范式立住，再谈训练**。
2. **对算力有限的团队**："32B + 纯 SFT 逼近旗舰"证明了一条不依赖海量算力和 RL 的可行路径。数据工程的杠杆，可能比想象中大得多。
3. **对整个行业**：深度研究 Agent 正在从「能不能搜到」走向「能不能真正帮人推进认知」。前者已被基本解决，后者——按 arXiv:2512.01948 的判断——我们还在半路上。

S1 是这条半路上一块扎实的路标：它没有解决「自主性」的终极问题，但它把「怎么造数据」这件最脏最累、却最关键的活，做出了一个可复现的开源范本。

---

## FAQ

**Q：S1-DeepResearch 和 OpenAI Deep Research、通义 DeepResearch 有什么不同？**
A：OpenAI Deep Research 是闭源产品；通义 DeepResearch 同样强调合成轨迹，但 S1 的差异化在于**显式地把能力拆成五维**（推理/指令/报告/文件/技能）并各自构造数据，且**完全只用 SFT、不用 RL**，模型和 15K 数据集全部 Apache 2.0 开源。

**Q：为什么是 32B 而不是更大？**
A：论文的核心论点恰恰是「参数效率来自高质量多维度轨迹数据，而非模型规模」。32B 在文本推理上追平 397B、在文件任务上达到 GLM-5 水平，就是为了证明这一点。另有 8B-Preview 供轻量探索。

**Q：普通人现在能用吗？**
A：模型在 HuggingFace（ScienceOne-AI/S1-DeepResearch-32B）可下载，代码在 GitHub（ScienceOne-AI/S1-DeepResearch），需自行部署带 9 类工具的沙箱环境，对工程能力有一定要求，暂非开箱即用的产品。

---

> 📌 原文与资源（请直接复制访问）：
> 论文 arXiv:2606.15367 —— https://arxiv.org/abs/2606.15367
> GitHub —— https://github.com/ScienceOne-AI/S1-DeepResearch
> 模型 —— https://huggingface.co/ScienceOne-AI/S1-DeepResearch-32B
> 数据集 —— https://huggingface.co/datasets/ScienceOne-AI/S1-DeepResearch-15k

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: The ScienceOne team open-sourced **S1-DeepResearch** (paper arXiv:2606.15367; 32B + 8B-Preview, Apache 2.0). Its most counterintuitive claim: a **32B model, trained with supervised fine-tuning only and no reinforcement learning**, approaches closed-source flagships (GPT-5.2, Claude-4.6, GLM-5) across 20 benchmarks spanning five capability dimensions — even matching the 71× larger Qwen3.5-397B on textual reasoning. The secret isn't architecture; it's a **graph-grounded trajectory construction paradigm** — "knowledge graph poses tasks → agent rolls out trajectories → five-track verification filters" — plus the **15K high-quality agent trajectory dataset** released with it. This piece breaks down how it works and where the industry's thinking on deep research agents is heading.

---

## 1. Where Do Deep Research Agents Get Stuck?

Over the past year, "Deep Research" went from an OpenAI/Google product name to shorthand for an entire class of agent capability: hand the model a hard question, let it search the web, read files, run code, reason iteratively, and produce a cited report. Simple to state, brutally hard to build — it demands the model hold state across **long-horizon, multi-hop** tasks without drifting or hallucinating.

The S1 team's diagnosis: the open-source bottleneck isn't model size, it's **the shape of the training data**. Existing agent datasets are overwhelmingly **search-centric** — essentially multi-hop QA that just buries the answer deeper. But real research is far more than search: reading a PDF or table, following multi-constraint instructions, writing traceable reports, invoking skills (plotting, data analysis, file generation). Agents trained only on "search" score fine on benchmarks but collapse on real tasks. S1-DeepResearch targets exactly this **capability-dimension narrowness**.

## 2. What Is S1-DeepResearch?

An end-to-end long-horizon deep research model system that folds those four neglected capabilities — alongside search — into a unified training objective.

| Spec | Value |
|------|-------|
| Model | S1-DeepResearch-**32B** (flagship) + **8B-Preview** |
| Base | Qwen3 |
| Context | **128K** tokens |
| Consecutive tool calls | **150+** rounds |
| Built-in tools | 9 categories (web/academic search, browsing, image/video analysis, file parsing, code execution, bash) |
| License | **Apache 2.0** (model + 15K trajectory dataset) |

Five capability dimensions: long-chain reasoning, research instruction following, report writing, file understanding/generation, and skill usage. The "150+ consecutive tool calls" figure is worth pausing on — it means the model runs hundreds of "observe → decide → call → read feedback" loops in a single task without breaking. That's what "long-horizon" really costs.

## 3. The Core Method: Data, Not Scale

S1's main contribution is **how it builds those 15K trajectories** — a three-stage paradigm.

**Stage 1 — Graph-grounded task formulation.** Rather than having an LLM invent questions, a knowledge graph controls difficulty and verifiability. Seed entities are filtered from Wikipedia (topology, popularity, info density, searchability, safety), expanded into a DAG via Wikidata relations and web search (with multimodal info), then nine constraint dimensions are injected before generation. Closed-form questions are rewritten to **weaken the answer's direct association**, forcing reasoning over recall. Crucially, tasks are first answered *without* tools to filter out anything solvable from parametric memory — then only the **top 30% most complex** (by information flow, feedback dependency, width, depth) survive.

**Stage 2 — Agentic trajectory rollout.** The agent solves tasks in a real 9-tool environment, recording full trajectories τ = (x, a₁, o₁, …, aₜ, oₜ, y). Scenario-specific refinement reshapes outputs into realistic artifacts (coherent cited reports, executable files, native multimodal inputs, file attachments instead of inline code).

**Stage 3 — Multi-dimensional verification.** Five tracks filter noise: LLM-as-judge for reasoning, a citation verifier for reports, a nine-dimensional constraint checker for instruction following, code-consistency checks for file tasks, and skill-activation tracking. The result: **15,000** high-quality trajectories across five dimensions.

**The counterintuitive choice: SFT only, no RL.** The objective simply imitates both intermediate actions and final answers: ℒ = −Σ log p(aₜ | x, a<t, o<t) − log p(y | x, a≤T, o≤T). In a year where everyone is racing on agentic RL, the message is pointed: **with high enough data quality across enough capability dimensions, SFT alone pushes a 32B model to flagship level** — parameter efficiency comes from data, not scale or RL.

## 4. The Numbers: 32B Matching Giants

Across **20 agentic benchmarks** (GAIA, BrowseComp/-ZH, XBench-DeepSearch, HLE, DeepResearch Bench, ComplexBench, FileSys, GTA, SkillsUse, etc.):

**vs. base Qwen3-32B (same size — gap is all data):**

| Benchmark | Qwen3-32B | S1-DeepResearch-32B |
|-----------|-----------|---------------------|
| GAIA (text) | 30.2 | **72.8** |
| DeepResearch Bench | 36.0 | **46.5** |
| DeepResearchIF (query acc.) | 4.1 | **25.2** |
| FileSys | 44.7 | **69.3** |

**vs. closed-source flagships:** overall performance **close to GPT-5.2, Claude-4.6, GLM-5** — report generation near GPT-5.2 (48.7 vs 51.4), file tasks at GLM-5 level (despite a 23× parameter gap), and textual reasoning **matching the 71× larger Qwen3.5-397B**.

> ⚠️ Read with care: these 20 benchmarks are the team's **own chosen** dimensions; "approaching flagships" holds under that evaluation lens, and closed models may still lead on more open real-world tasks. Even discounted, "32B + pure SFT approaching giants" demonstrates the power of the data paradigm.

## 5. What Is the Industry Thinking? Three Undercurrents

**Undercurrent 1 — competition shifts from "the model" to "how you build trajectories."** Tongyi DeepResearch (arXiv:2510.24701) argues synthetic trajectory data is decisive; OpenResearcher (arXiv:2603.20278) open-sourced a full long-horizon synthesis pipeline; Marco DeepResearch (arXiv:2603.28376) pushes verification-centric design. Emerging consensus: the bottleneck is **scalable, high-quality, multi-dimensional, verifiable trajectory data**, not the base model.

**Undercurrent 2 — evaluation becomes the battleground.** When everyone claims "approaching GPT-5.2," how you measure matters. BrowseComp-Plus (ACL 2026) decouples retriever from agent reasoning via a fixed corpus for fair, reproducible comparison; DeepResearch Bench and DeepResearchEval build more realistic automated frameworks. The sharp question underneath: **leaderboard scores ≠ genuine usefulness.**

**Undercurrent 3 — disenchantment with "autonomy."** The most sobering read is arXiv:2512.01948, *How Far Are We from Genuinely Useful Deep Research Agents?*, which names a **performance-utility gap**: agents handle retrieval but struggle to synthesize sources into knowledge-advancing narratives; they lack iterative hypothesis-testing; they optimize task completion over researchers' real epistemic goals. Its verdict: **current autonomy claims are likely overstated; human oversight remains essential.** That's the gap S1-class work must still cross.

## 6. What This Means

1. **For developers**: both model and 15K dataset are Apache 2.0. For vertical research agents, the "graph → trajectory → verification" paradigm is more worth borrowing than the weights themselves — **get the data paradigm right first**.
2. **For compute-constrained teams**: "32B + pure SFT approaching flagships" proves a path that doesn't depend on massive compute or RL. The leverage of data engineering may be larger than assumed.
3. **For the field**: deep research is moving from "can it find it" (largely solved) to "can it genuinely advance human understanding" (per arXiv:2512.01948, still mid-journey).

S1 is a solid signpost on that journey: it doesn't solve autonomy, but it turns the dirtiest, most essential work — *how to build the data* — into a reproducible open-source template.

## FAQ

**Q: How does it differ from OpenAI Deep Research or Tongyi DeepResearch?**
A: OpenAI's is closed; Tongyi also stresses synthetic trajectories, but S1 explicitly decomposes capability into **five dimensions** with per-dimension data, uses **SFT only (no RL)**, and open-sources everything under Apache 2.0.

**Q: Why 32B, not bigger?**
A: The thesis is that parameter efficiency comes from high-quality multi-dimensional trajectory data, not scale. Matching 397B on reasoning and GLM-5 on file tasks is the proof. An 8B-Preview exists for lightweight exploration.

**Q: Can I use it now?**
A: Model on HuggingFace (ScienceOne-AI/S1-DeepResearch-32B), code on GitHub (ScienceOne-AI/S1-DeepResearch). You must deploy a sandbox with the 9 tools yourself — it's research-grade, not yet a turnkey product.

---

> 📌 Source & resources (copy to visit):
> Paper arXiv:2606.15367 — https://arxiv.org/abs/2606.15367
> GitHub — https://github.com/ScienceOne-AI/S1-DeepResearch
> Model — https://huggingface.co/ScienceOne-AI/S1-DeepResearch-32B
> Dataset — https://huggingface.co/datasets/ScienceOne-AI/S1-DeepResearch-15k

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
