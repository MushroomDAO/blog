---
title: "Harvey AI 的 Moneyball 路线：中小AI公司如何训练垂直域模型——从评测基准、开源基座到异步RL的完整案例"
titleEn: "harvey-ai-vertical-llm-training-moneyball-legal-ai"
description: "Harvey AI 以法律为切入点，开创了一条「先建评测、后选基座、再做RL」的垂直域模型训练路线。本文以 Harvey Tenet（基于 Kimi K3 + Fireworks 异步RL）、Review Table（GLM-5.2 + Applied Compute）、M&A Diligence（RLM + Baseten）为案例，完整拆解其成本、数据、供应商、评测、训练的全链条决策，同时收录开源仓库 harveyai/harvey-labs（LegalAgentBench，1266 ⭐，1671任务，24+实践领域），供正在寻找垂直域训练路线的团队参考。"
descriptionEn: "Harvey AI built a full vertical-domain model training playbook using legal AI as the proving ground: build the benchmark first, pick open-weight bases, then post-train with async RL. This piece covers Harvey Tenet (Kimi K3 + Fireworks async RL), Review Table (GLM-5.2 + Applied Compute), M&A Diligence (RLM + Baseten), and Firm Knowledge (Qwen3.8-27B + Engram), tracing the full cost–data–vendor–evaluation–training decision chain, plus the open-source LegalAgentBench (harveyai/harvey-labs, 1266 stars, 1671 tasks, 24+ practice areas)."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Research"
tags: ["垂直域AI", "法律AI", "强化学习", "开源", "模型训练", "Harvey", "LegalAgentBench", "后训练"]
heroImage: "../../assets/images/harvey-ai-vertical-llm-training-moneyball-legal-ai-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：harveyai/harvey-labs ⭐ 1,266 | MIT | 1671 任务 | 24+ 法律实践领域  
Harvey Tenet 发布：2026-08-20 | 基座：Kimi K3 | 合作：Fireworks AI + Mercor  
本文截止日期：2026-08-28

---

## 一、为什么叫 Moneyball

2002年奥克兰运动家队没钱买明星球员，于是总经理比利·比恩转而买数据——分析什么球员组合在成本最低的情况下能赢得最多比赛。结果那年他们拿了当时美联最长的20连胜。

Harvey AI 的 Gabe Pereyra（研究主管，前 DeepMind）在 Sequoia AI Ascent 上用这个比喻描述了公司的模型训练哲学：

1. **不从头预训练**——太贵，产出不确定
2. **先建评测，不先建模型**——搞清楚"赢"在哪里再动手
3. **用开源基座**——Kimi K3、GLM-5.2、Qwen3.8-27B
4. **在真实产品harness里做RL**——不在模拟环境里空转
5. **用供应商网络替代全自研**——Fireworks/Mercor/Applied Compute/Baseten/Engram 各司其职

这条路不是Harvey发明的，但Harvey是迄今把它从概念跑到生产最彻底的案例之一。本文把它完整拆开。

---

## 二、第一步：先建评测——LegalAgentBench

Harvey 在内部开发了将近一年产品之后，发现法律领域没有一个能真实衡量Agent能力的基准。现有的 LegalBench、CUAD、LEXam 测的都是短链条推理：读一份合同，回答一个问题，对比几个案例。

这不够。律所的工作是这样的：合伙人丢给助手一个任务（比如"帮我做这起并购的尽职调查"），助手要自己找文件、读文件、分析风险、写报告，最后合伙人来审核。

2026年5月，Harvey 开源了 **Legal Agent Benchmark（LAB）**：

| 指标 | 数值 |
|------|------|
| GitHub | harveyai/harvey-labs |
| Stars | 1,266 ⭐ |
| Forks | 216 |
| 许可证 | MIT |
| 任务数 | 1,671 |
| 法律实践领域 | 24+ |
| 评分标准数量 | 75,000+ 条专家撰写的rubric criteria |

每个任务的结构完全模拟律所工作流：

- **指令**：合伙人给助理的任务请求，平均仅50词，不给详细提示
- **环境**：客户案件文件夹，混入主要文件和干扰文件，问题分散在多份文档里
- **输出**：Agent必须生成可审核的法律文件（备忘录、尽调报告、合同标注等）
- **评分**：专家rubric——Agent的输出必须满足格式、事实、分析三个维度

Harvey 明确不急着发榜单——他们等社区研究者用 LAB 跑出可比较的基线后，再发规范化提交标准。这个决策避免了评测被抢跑和无意义的"最强法律AI"营销战。

LAB 是 Harvey 整条训练链的起点，也是评估改进的终点。**先有尺子，再开始量**。

---

## 三、第二步：选开源基座，不预训练

Harvey 用了三个不同基座训练三个不同能力：

| 能力 | 基座模型 | 合作方 |
|------|---------|--------|
| Harvey Tenet（核心法律Agent） | Kimi K3 | Fireworks AI |
| Review Table（文档结构化提取） | GLM-5.2 | Applied Compute |
| M&A Diligence（并购尽调） | GLM-5.2（编排器） | Baseten |
| Firm Knowledge（律所知识库Agent） | Qwen3.8-27B | Engram |

选基座的逻辑很简单：**开源模型的 per-token 推理价格比闭源模型低得多**，而且可以在自己的 harness 里部署，不被 API 速率限制。Kimi K3、GLM-5.2 在一般推理能力上已经接近闭源前沿，差距主要在领域专业知识和长链条任务完成率——这正是 RL 后训练要解决的问题。

---

## 四、第三步：异步RL后训练——Harvey Tenet 案例

Harvey Tenet 是 Harvey 的第一个生产级后训练模型，2026年8月发布研究预览。核心方法：

### 训练环境

每个训练 rollout 的结构和 LAB 任务完全一致：

1. Agent 在沙盒工作区里启动，工作区包含任务的客户案件文件和工具（搜索、读文档、起草）
2. 完成工作后，Agent 把最终文件写到磁盘，结束该 episode
3. LLM-as-a-judge（Kimi 2.6）对 rubric 逐条打分

**为什么选 Kimi 2.6 当 judge**：Harvey 跑了消融实验，比较了多个 judge 模型对更重的前沿模型的对齐程度，Kimi 2.6 在质量和效率上是最优解。这个选 judge 的消融值得单独关注——judge 质量直接决定 RL 梯度的信号质量。

### 算法：GSPO

Harvey 使用 **Group-Sequence Policy Optimization（GSPO，arXiv:2507.18071）**：

- 对同一任务采样一组独立 rollout，对每个 rollout 打分
- 组内计算 advantage（用组方差归一化），避免不同难度任务的梯度不平衡
- **近平局的组重新打分**，减少噪声进入梯度
- 小的 intra-group 长度惩罚项，鼓励简洁输出
- Sequence-averaged importance weights，训练稳定
- 双边 clip + mask 高重要度比 token，防止 RL collapse

### 双目标优化：质量 + 成本

这是 Harvey 方法里最有价值的洞察：**训练时同时优化质量和 token 效率**。通过 reward shaping，优先选择在相同性能下 token 消耗更低的轨迹。

结果：Harvey Tenet 在 LAB 上的成本-质量 Pareto 曲线上显著超越同等基线。

### 数据三层结构

| 数据类型 | 来源 | 用途 |
|---------|------|------|
| 合成数据 | 内部生成 | 覆盖大量任务变体 |
| 公开法律数据 | 公开来源 | 补充真实法律知识 |
| 人类专家数据 | Mercor 提供 | 合成数据的审核和修正，高价值训练信号 |

人类专家数据是质量瓶颈。Mercor（专业人才外包平台）承担了专家数据的大规模生产和合成数据的人工修正——这是 Harvey 没有直接雇几百个律师注标的原因。

### Harvey Tenet 结果

| 指标 | vs base Kimi K3 |
|------|----------------|
| LAB 任务完成数 | ~2× |
| LAB all-pass rate | +9 pp |
| LAB Contracts all-pass rate | +2 pp |
| LAB Contracts 排名 | 第1（state-of-the-art） |
| LAB 排名 | 第2 |
| 迁移性 | Mercor APEX Agents、Crosby Redline Bench 未见过的 benchmark 上也提升 |

---

## 五、第四步：专项能力——每个模块单独训练

Harvey 把"法律AI"拆成了几个独立能力，每个用不同的基座+供应商+训练策略。

### M&A 并购尽调（Baseten 合作）

并购尽调是个极端场景：一个任务要扫描80M tokens的数据室，识别风险点，写出尽调备忘录。

Harvey 的解法是 **Recursive Language Models（RLM）**：

- Root agent 在 REPL 环境里持有整个数据室，可以程序化搜索和切片
- 把具体文档的阅读和分析分发给有各自独立上下文窗口的 sub-agent
- Root agent 汇总，写最终报告

GLM-5.2 作为 RLM 编排器，LAB Diligence criteria pass rate：**46.1%**

然后 Harvey 对 GLM-5.2 在 RLM harness 里做了自蒸馏 SFT（从高覆盖率轨迹蒸馏），纠正了基础模型「倾向于把工作留给自己而不是下放」的系统性偏差，criteria pass rate 提升到 **60.1%**。

对比：所有前沿基线模型（闭源+开源+off-the-shelf coding agent）在 LAB Diligence 上的上限是 43.8%。

### Review Table 文档结构化提取（Applied Compute 合作）

Review Table 是 Harvey 的一个产品功能：用户对10,000份文档做结构化数据提取，每个单元格的答案要有精确引用。

Harvey 和 Applied Compute 一起构建了一个合成+公开数据语料库，在 Review Table 的**生产 harness 里**直接训练 GLM-5.2（而不是模拟环境）：

| 指标 | 提升 |
|------|------|
| 答案质量 | +3.6 分 |
| 引用质量 | +12.1 分 |
| 成本 | 约为最强基线的 1/10 |

模型学到了几个在生产中非常有价值的行为：
- 当问题不适用于某文档时，主动返回"不适用"（而不是编造答案）
- 引用精确的支持性证据（而不是填充式引用）

### Firm Knowledge 律所知识库（Engram 合作）

律所积累了大量历史案件、备忘录、合同模板。新任务来时，Associate 需要在这个"知识库"里找到相关先例。这个场景里，对话上下文可以达到100M tokens——任何基础模型都会倾向于反复暴力搜索。

Harvey 和 Engram 训练了一个 **Qwen3.8-27B** 模型，让它：
1. 预先探索律所知识库
2. 把特征压缩进1M tokens的结构化笔记
3. 通过蒸馏和RL over self-generated data 把语料内化到参数里

结果：

| 指标 | 结果 |
|------|------|
| Criteria pass rate | +15%+ |
| Task completion rate | +~10% |
| Token 减少 | -58% |
| Cost per query | -90% |
| Intelligence-per-token（每100k token完成的rubric分） | 190.8（vs 最优前沿配置 129.3，vs 同等规模模型 37.2） |

"多学习"（更多 study effort）比"多推理"（更多 reasoning tokens）更高效：Harvey 的曲线显示，增加学习时间可以在提升质量的同时降低推理 token；而增加推理时间则以更大的 token 消耗换取相对较小的质量增益。

---

## 六、供应商网络：为什么不全自研

Harvey 的合作商清单说明了一个关键判断：**某些计算和数据能力，外包比自研的 ROI 更高**。

| 供应商 | 贡献 | 核心价值 |
|--------|------|---------|
| Fireworks AI | 异步RL训练基础设施 | 高吞吐量、大规模 rollout 并发 |
| Mercor | 人类专家数据生产和审核 | 专业律师标注，合成数据质量把关 |
| Applied Compute | Review Table 训练语料 | 针对结构化提取任务的合成数据 |
| Baseten | M&A Diligence RLM harness | 专为大规模文档分布式处理优化 |
| Engram | Firm Knowledge 记忆Agent | 长期记忆和知识压缩技术 |

这不是把核心能力外包——Harvey 保留了任务设计、评测基准、RL 策略优化、产品集成。外包的是执行层的专项能力，这些能力各自需要深度专业知识，但对 Harvey 来说边际成本远高于采购成本。

---

## 七、对中小AI公司的启示

Harvey 的案例给出了一条可复制（而不仅仅是可参考）的路线：

**1. 评测基准是护城河，不只是验收工具**

LAB 现在是业界唯一公认的法律Agent基准。Harvey既用它训练，也用它对外展示进展，还用它吸引合作研究者。一个高质量的领域基准本身就有巨大的生态价值，远超单个模型的发布。

**2. 开源基座让成本可控，RL缩短能力差距**

从头预训练一个 frontier 模型需要数亿美元。但 Kimi K3 + 几周 RL = 在法律Agent任务上超越所有闭源基线的成本效率。差距收窄到让人发指的程度——Harvey 在 LAB 上做到了 state-of-the-art，用的是别人的预训练成果。

**3. 在生产 harness 里训练，不在模拟环境里训练**

Review Table 的关键改进来自直接在生产 harness 里训练——模型学会了应对真实的 retrieval 上下文、schema 约束和引用要求，而不是在理想化的测试集上优化一个和生产无关的指标。

**4. 每个专项能力单独训练，不追求万能模型**

Harvey Tenet、Review Table、M&A Diligence、Firm Knowledge 是四个独立训练的模型，服务四个不同的产品场景。能力拆分使得每个模型都可以用针对性更强的数据和 reward 去训练，效果远好于试图让一个模型做所有事。

**5. 人类专家数据是质量天花板，不是可以省略的环节**

合成数据可以提供数量，但 Harvey 明确表示人类专家数据对后训练质量有决定性作用。Mercor 的角色说明：专家标注不是一次性的，而是一个持续的质量保障流程。

---

## 八、开源资源

**LegalAgentBench（harveyai/harvey-labs）**

```bash
git clone https://github.com/harveyai/harvey-labs.git
cd harvey-labs
# 安装依赖
pip install -e .
# 运行示例任务（M&A 并购尽调 tutorial）
# 详见 docs/tutorial.md
```

LAB 包含：
- 1,671 个任务（覆盖并购尽调、合同审查、律所知识搜索等24+实践领域）
- 执行 harness（运行 Agent 并打分）
- 多模型适配器（通过 adapter 接入任意 LLM）
- 评分报告和比较 dashboard

---

**相关链接**

- GitHub: https://github.com/harveyai/harvey-labs
- Harvey 研究主页: https://harvey.ai/research
- Harvey Tenet 博文: https://harvey.ai/en-US/blog/post-training-update-harvey-tenet
- GSPO 论文: https://arxiv.org/abs/2507.18071

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Harvey AI's Moneyball Playbook: How Mid-Sized Companies Train Vertical Domain Models — Benchmarks, Open Weights, and Async RL

*by Mycelium Protocol*

---

GitHub: harveyai/harvey-labs ⭐ 1,266 | MIT | 1,671 tasks | 24+ legal practice areas  
Harvey Tenet published: 2026-08-20 | Base: Kimi K3 | Partners: Fireworks AI + Mercor  
Research cutoff: 2026-08-28

---

### I. Why "Moneyball"

In 2002, the Oakland A's couldn't afford star players. So GM Billy Beane bought data instead — he analyzed which combinations of undervalued players could win the most games at the lowest cost. That year they set the American League record with a 20-game winning streak.

Harvey AI's research lead Gabe Pereyra (formerly DeepMind) used this analogy at Sequoia AI Ascent to describe the company's model training philosophy:

1. **Don't pretrain from scratch** — too expensive, outcome too uncertain
2. **Build the benchmark before building the model** — know what "winning" means before starting
3. **Use open-weight bases** — Kimi K3, GLM-5.2, Qwen3.8-27B
4. **Train with RL inside the real product harness** — not simulated environments
5. **Use a vendor network instead of building everything in-house** — Fireworks, Mercor, Applied Compute, Baseten, Engram each cover a piece

Harvey didn't invent this path, but they're one of the most complete examples of running it from concept to production. This post traces it fully.

---

### II. Step One: Build the Benchmark First — LegalAgentBench

After nearly a year building legal AI products, Harvey discovered the domain lacked a benchmark that could realistically measure agent capability. Existing benchmarks — LegalBench, CUAD, LEXam — tested short-horizon reasoning: read a contract, answer a question, compare cases.

That's not enough. Legal work at a law firm looks like this: a partner hands an associate a task ("run the diligence on this acquisition"), the associate finds the files, reads them, analyzes risks, drafts the memo, and the partner reviews. No benchmark measured whether an AI could actually do that.

In May 2026, Harvey open-sourced **Legal Agent Benchmark (LAB)**:

| Metric | Value |
|--------|-------|
| GitHub | harveyai/harvey-labs |
| Stars | 1,266 ⭐ |
| Forks | 216 |
| License | MIT |
| Tasks | 1,671 |
| Legal practice areas | 24+ |
| Expert rubric criteria | 75,000+ |

Each task mirrors the law firm workflow:

- **Instruction**: partner's task request to an associate — ~50 words, no detailed output hints
- **Environment**: client matter folder, key files mixed with peripheral ones, issues scattered across multiple documents
- **Output**: the agent must produce reviewable legal work product (memo, diligence report, contract redline, etc.)
- **Grading**: expert rubrics covering format, facts, and analysis

Harvey deliberately launched without a leaderboard — they wanted the benchmark to evolve alongside community input before publishing normalized submission standards. This prevented meaningless "strongest legal AI" marketing races.

LAB is both the starting point and the endpoint of Harvey's entire training pipeline. **First the ruler, then the measurement.**

---

### III. Step Two: Pick Open-Weight Bases, Don't Pretrain

Harvey used three different base models for three different capabilities:

| Capability | Base Model | Partner |
|------------|-----------|---------|
| Harvey Tenet (core legal agent) | Kimi K3 | Fireworks AI |
| Review Table (structured doc extraction) | GLM-5.2 | Applied Compute |
| M&A Diligence | GLM-5.2 (orchestrator) | Baseten |
| Firm Knowledge | Qwen3.8-27B | Engram |

The selection logic is straightforward: open-weight models have significantly lower per-token inference costs than closed-source models, and can be deployed in your own harness without API rate limits. Kimi K3 and GLM-5.2 already match closed-source models on general reasoning; the gap is in domain expertise and long-horizon task completion — exactly what RL post-training addresses.

---

### IV. Step Three: Async RL Post-Training — Harvey Tenet

Harvey Tenet is Harvey's first production post-trained model, released as a research preview in August 2026. Core method:

**Training environment**

Each training rollout mirrors a LAB task:
1. The agent starts in a sandboxed workspace with the task's client matter files and tools (search, read, draft)
2. After completing the work, the agent writes deliverables to disk to end the episode
3. An LLM-as-a-judge (Kimi 2.6) grades each rubric criterion

**Why Kimi 2.6 as judge**: Harvey ran ablations comparing judge models against heavier frontier models. Kimi 2.6 was optimal for both quality and efficiency. Judge quality directly determines RL gradient signal quality — this ablation is worth emulating.

**Algorithm: GSPO**

Harvey used **Group-Sequence Policy Optimization (GSPO, arXiv:2507.18071)**:

- Sample a group of independent rollouts for each task, score each
- Compute intra-group advantages normalized by group variance, preventing gradient imbalance across tasks of different difficulty
- Near-tied groups are re-judged to reduce noise entering the gradient
- Small intra-group length penalty encourages concise outputs
- Sequence-averaged importance weights for stable training
- Double-sided clipping + masking high-importance-ratio tokens to prevent RL collapse

**Dual optimization: quality + cost**

The most valuable insight from Harvey's approach: **optimize for quality and token efficiency simultaneously during training**. By shaping rewards to prefer trajectories with equivalent performance but lower token consumption, Harvey co-optimized both objectives.

Result: Harvey Tenet's cost-quality Pareto frontier substantially surpasses same-tier baselines on LAB.

**Training data: three-layer structure**

| Data type | Source | Role |
|-----------|--------|------|
| Synthetic | Internal generation | Cover broad task variation |
| Public legal | Open legal sources | Supplement real legal knowledge |
| Human expert | Mercor | Review and correct synthetic data; high-signal training examples |

Human expert data is the quality bottleneck. Mercor (professional talent platform) handled large-scale expert data production and synthetic data correction — enabling Harvey to avoid hiring hundreds of annotating lawyers directly.

**Harvey Tenet results**

| Metric | vs base Kimi K3 |
|--------|----------------|
| LAB task completions | ~2× |
| LAB all-pass rate | +9 pp |
| LAB Contracts all-pass rate | +2 pp |
| LAB Contracts ranking | #1 (state-of-the-art) |
| LAB overall ranking | #2 |
| Transfer | Improves on unseen benchmarks: Mercor APEX Agents, Crosby Redline Bench |

---

### V. Step Four: Specialized Capabilities — Each Module Trained Separately

Harvey decomposed "legal AI" into independent capabilities, each with a different base model, partner, and training strategy.

**M&A Diligence (with Baseten)**

M&A diligence is an extreme scenario: a single task requires scanning up to 80M tokens of data-room documents to identify risks and produce a diligence memo.

Harvey's solution: **Recursive Language Models (RLMs)**:
- Root agent holds the entire data room in a REPL environment, can programmatically search and slice
- Delegates reading and analysis of specific documents to sub-agents with their own context windows
- Root agent aggregates and writes the final report

GLM-5.2 as RLM orchestrator → LAB Diligence criteria pass rate: **46.1%**

Then Harvey ran self-distillation SFT on GLM-5.2 within the RLM harness (distilling from high-coverage traces), correcting the base model's systematic bias toward keeping work local rather than delegating → **60.1%** criteria pass rate.

For comparison: all frontier baselines (closed-source + open + off-the-shelf coding agents) top out at 43.8% on LAB Diligence.

**Review Table (with Applied Compute)**

Review Table is a Harvey product feature: users run structured data extraction across up to 10,000 documents at a time, each answer requiring precise citations.

Harvey and Applied Compute built a synthetic+public data corpus and trained GLM-5.2 **directly inside the production Review Table harness** (not a simulated environment):

| Metric | Improvement |
|--------|-------------|
| Answer quality | +3.6 points |
| Citation quality | +12.1 points |
| Cost vs strongest baseline | ~1/10 |

The model learned genuinely useful production behaviors:
- Abstaining when a question doesn't apply to a document (rather than hallucinating)
- Citing precise supporting evidence (rather than padding with adjacent citations)

**Firm Knowledge (with Engram)**

Law firms accumulate vast historical case files, memos, and contract templates. New tasks require searching this "firm knowledge base" for relevant precedents — context can reach 100M tokens. Without guidance, base models default to exhaustive, repetitive search that burns context window space.

Harvey and Engram trained a **Qwen3.8-27B** model to:
1. Proactively explore the firm knowledge base before tasks arrive
2. Compress features into 1M tokens of structured notes
3. Internalize the corpus into weights through distillation and RL over self-generated data

Results:

| Metric | Result |
|--------|--------|
| Criteria pass rate | +15%+ |
| Task completion rate | +~10% |
| Token reduction | -58% |
| Cost per query | -90% |
| Intelligence-per-token (criteria points per 100k inference tokens) | 190.8 (vs. 129.3 for best frontier config; 37.2 for equivalent-size models) |

More study effort outperforms more reasoning effort: Harvey's curve shows increased study time improves quality while reducing inference tokens; increased reasoning time raises token usage with smaller quality gains.

---

### VI. The Vendor Network: Why Not Build Everything In-House

Harvey's partner list reflects a key judgment: **some compute and data capabilities have higher ROI when procured than built**.

| Vendor | Contribution | Core value |
|--------|-------------|------------|
| Fireworks AI | Async RL training infrastructure | High-throughput, large-scale rollout concurrency |
| Mercor | Human expert data production + review | Professional lawyer annotation; synthetic data QA |
| Applied Compute | Review Table training corpus | Targeted synthetic data for structured extraction |
| Baseten | M&A Diligence RLM harness | Optimized for large-scale distributed document processing |
| Engram | Firm Knowledge memory agents | Long-term memory and knowledge compression technology |

This isn't outsourcing core capability — Harvey retains task design, evaluation benchmarks, RL strategy, and product integration. What's procured is execution-layer specialist capability that each vendor has spent years developing, where Harvey's marginal build cost far exceeds the acquisition cost.

---

### VII. Lessons for Mid-Sized AI Companies

Harvey's case gives a replicable (not merely inspirational) path:

**1. Evaluation benchmarks are a moat, not just a QA tool**

LAB is now the only widely accepted legal agent benchmark. Harvey uses it for training, for external progress communication, and for attracting research partners. A high-quality domain benchmark has enormous ecosystem value beyond any single model release.

**2. Open-weight bases make cost controllable; RL closes the capability gap**

Pretraining a frontier model from scratch costs hundreds of millions. But Kimi K3 + a few weeks of RL = cost-quality performance that surpasses all closed-source baselines on legal agent tasks. The gap narrows to a remarkable degree — Harvey achieved state-of-the-art on LAB Contracts using someone else's pretraining.

**3. Train inside the production harness, not a simulation**

Review Table's key improvement came from training directly inside the production harness — the model learned to navigate real retrieval contexts, schema constraints, and citation requirements. Training in an idealized test environment and hoping it transfers is a losing bet.

**4. Train each specialized capability separately; don't chase a universal model**

Harvey Tenet, Review Table, M&A Diligence, and Firm Knowledge are four separately trained models serving four different product contexts. Capability decomposition lets each model be trained with more targeted data and reward design, far outperforming attempts to make one model do everything.

**5. Human expert data is the quality ceiling, not an optional step**

Synthetic data provides quantity. But Harvey is explicit that human expert data is decisive for post-training quality. Mercor's role shows: expert annotation is not a one-time effort but an ongoing quality assurance process.

---

### VIII. Open Source Resources

**LegalAgentBench (harveyai/harvey-labs)**

```bash
git clone https://github.com/harveyai/harvey-labs.git
cd harvey-labs
pip install -e .
# Run the M&A diligence tutorial end-to-end: docs/tutorial.md
```

LAB includes:
- 1,671 tasks (M&A diligence, contract review, firm knowledge search, 24+ practice areas)
- Execution harness (run agents, collect scores)
- Multi-model adapters (plug in any LLM via adapter)
- Scoring reports and comparison dashboards

---

**Links**

- GitHub: https://github.com/harveyai/harvey-labs
- Harvey Research: https://harvey.ai/research
- Harvey Tenet post: https://harvey.ai/en-US/blog/post-training-update-harvey-tenet
- GSPO paper: https://arxiv.org/abs/2507.18071

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
