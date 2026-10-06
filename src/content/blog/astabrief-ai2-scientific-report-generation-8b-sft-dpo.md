---
title: "AstaBrief：Ai2 开源的 8B 科研报告模型，SFT+DPO 替代 RL"
titleEn: "AstaBrief: Ai2's Open-Source 8B Scientific Report Model — SFT+DPO Without RL"
description: "allenai/AstaBrief，Qwen3-8B 微调，SFT+DPO 两阶段训练，开源权重+训练数据。来自 Ai2（Allen Institute for AI）的 Asta 科研平台，用 9 万条真实用户研究问题做 SFT（筛后 47K），6K 条双评判 DPO 偏好对（GPT-4.1 + DeepSeek-R1 同意率 95%）。一次性生成完整报告（对标 Claude 多步 ScholarQA 方案），51.1s vs 178.5s，快 3.5 倍。训练设计亮点：多个强模型生成候选报告、双评判模型过滤 DPO 对，不把任何单一模型当真理。"
descriptionEn: "allenai/AstaBrief, Qwen3-8B fine-tune, SFT+DPO two-phase training, open weights + training data. From Ai2's Asta research platform, trained on 90K real user research queries (47K after filtering for SFT), 6K dual-judge DPO preference pairs (GPT-4.1 + DeepSeek-R1, 95% human agreement). One-pass report generation vs Claude's multi-step ScholarQA pipeline: 51.1s vs 178.5s (3.5× faster). Key training design: multiple strong model generators + dual-judge filtering avoids treating any single model as ground truth."
pubDate: 2026-10-06
heroImage: "../../assets/images/astabrief-ai2-scientific-report-generation-8b-sft-dpo-banner.jpg"
category: "Research"
tags: ["AI模型", "科研工具", "SFT", "DPO", "开源模型", "学术AI"]
lang: "zh-CN"
wechatTitle: "AstaBrief：Ai2开源8B科研报告模型"
wechatDigest: "Qwen3-8B微调；SFT+DPO；9万真实问题；比Claude快3.5倍"
---

科研报告生成领域最大的问题不是"AI能不能写"，而是"写出来能不能信"：引文对不对、声明有没有过度推断、结论有没有超出原始研究的范围。Ai2 在这个方向上做了一个规模适中但方法扎实的尝试——AstaBrief。

它基于 Qwen3-8B 微调，是 Ai2 旗下 Asta 科研平台"快速模式"背后的模型，现在连权重和训练数据一起开源。

HuggingFace: https://huggingface.co/allenai/AstaBrief | Ai2 | Qwen3-8B 微调 | Apache 2.0

---

## 背景：Asta 平台的两种模式

Ai2 的 Asta 是一个面向研究人员的 AI 平台，核心功能是把用户的研究问题转成有引文支撑的综合报告。它有两种模式：

- **Thinking 模式**：调用 Claude，走多步 ScholarQA 流水线——先检索文献，再逐节整合引文，最后用强模型合成。质量高，但一次生成要 178.5 秒。
- **Fast 模式**（AstaBrief）：一次性生成完整报告，51.1 秒，3.5 倍速度提升。

两种模式面对的是同一批用户、同一类问题，AstaBrief 是在"快和准"之间找到了一个新的平衡点。

---

## 训练数据：90K 真实用户查询，不是合成数据

大多数微调数据集是合成的——用强模型生成问题再生成答案。AstaBrief 的数据来源是 Asta 平台 7 个月的真实用户查询日志。

过滤流程：
1. 剔除 beta 测试流量和机器人流量
2. 剔除太短、非英文、非科研性、含个人信息的查询
3. LLM 二次过滤

最终剩下 **9 万条研究导向的查询**。

这个数据来源有一个重要优势：它反映的是研究人员实际在问什么，而不是数据工程师认为研究人员会问什么。用户研究发现，研究人员的提问方式是"提供完整上下文、多个约束条件、概念之间的关系"，而不是关键词式的短提示——这些特点只有在真实日志里才能充分体现。

---

## SFT 阶段：47K 样本，多模型生成

SFT 数据生成用的是 Asta 平台的多步 ScholarQA 流水线（也就是 Thinking 模式背后的那套系统）：

- 给每条查询检索相关文献
- 把文献组织成章节
- 用强模型合成有引文的报告

使用的模型包括 Claude 3.5 Sonnet、Claude 3.7 Sonnet、o3、o4-mini 和 GPT-4.1 的组合。质量过滤后得到 **47K 可用训练样本**。

---

## DPO 阶段：双评判过滤，6K 偏好对

DPO（Direct Preference Optimization）需要的不是单个目标答案，而是"A 好于 B"的对比对。

生成方式：
- 一组报告由 ScholarQA 流水线生成（Claude 3.5/3.7 Sonnet 主导）
- 另一组由 o3、o4-mini、DeepSeek-V3 或 DeepSeek-R1 生成（同一份检索到的文献作为输入）
- **两个评判模型**——GPT-4.1 和 DeepSeek-R1——各自独立评选赢家
- 只保留两个评判模型意见一致的对，过滤掉有争议的样本

结果：与人类偏好 95% 一致，最终 DPO 数据集约 **6K 样本**。

这个设计的核心思想是：不把任何单一模型的输出当作偏好标签的唯一依据。用多个生成器是为了减少偏向任一模型的风格偏见；用两个评判模型要求一致，是为了过滤掉那些靠运气才有结论的样本。

---

## 评估：四个维度，三个测试集

主要评估基准：**SQABench-CS2**，200 道研究人员自己写的计算机科学研究问题。

四个指标：

| 指标 | 含义 |
|------|------|
| Rubric score | 报告覆盖了多少必要内容 |
| Answer precision | 每个段落是否切题 |
| Citation precision | 每条引文是否支撑其对应的声明 |
| Citation recall | 声明是否得到了完整的文献支撑 |

补充评估：
- **DeepScholarBench**：63 个问题，基于近期 ArXiv 论文的长篇综合研究基准
- **与 Claude 流水线对比**（LLM 评判）：SQABench-CS2 上的逐对比较
- **人类研究小样本**：人工对比评分

---

## 一个开放的局限：引文对 ≠ 范围保留

Ai2 在论文里坦承了一个评估盲区，值得关注：

> 一份报告可以听起来完整而有说服力，同时又在跑题或把引文贴在不支持它的声明上。

他们的四个指标主要衡量相关性、覆盖面和引文对应关系，但**引文对应关系不等于科学声明的范围保留**。

举个例子，模型可以把一项针对特定样本的发现概括为"整个群体的普遍规律"，把过去时态的研究结果变成现在时态的通用声明，或把描述性发现变成政策建议——每一步都不是明显错误，但加起来就是声明的系统性扩大。

这是科研报告生成领域一个更难评测的问题，AstaBrief 目前没有覆盖它。

---

## 如何学习这个训练过程

如果想复现或延伸 AstaBrief 的训练思路，几个关键节点：

**1. 数据来源设计**：优先用真实用户日志（如果有），而不是从头合成。真实查询的复杂度和多样性是合成数据难以覆盖的。如果没有，至少要分析目标用户群的实际问法。

**2. SFT 目标生成**：用多个强模型（而不是一个）生成训练答案，可以减少风格单一化。质量过滤比数量更重要——47K 高质量样本比 90K 粗糙样本更有用。

**3. DPO 偏好对设计**：两个评判模型同时打分，只保留一致的对。这比单评判贵，但数据质量提升明显（Ai2 报告 95% 与人类一致）。评判模型和生成模型最好不要重叠，避免循环偏见。

**4. 基础模型选择**：AstaBrief 选 Qwen3-8B，既足够强（能做复杂引文综合），又足够小（推理速度满足生产部署）。如果你的任务领域有更专业的基础模型可选，优先领域匹配。

**5. 评估维度的完整性**：仅看生成质量分是不够的。对于任何涉及事实依据的任务，额外设计一个"声明范围保留"指标——检查模型有没有过度推断。

---

## 开源内容

Ai2 开源了：
- 模型权重（HuggingFace）
- 训练数据（SFT + DPO 样本集）
- 生成 PDF 报告的示例工作流

这让 AstaBrief 不只是一个可以直接用的模型，也是一个可以研究的完整训练案例。

---

> AstaBrief 由 Allen Institute for AI（Ai2）发布，2026-10-02，基于 Qwen3-8B 微调。开源仅供学习参考。

---

<!--EN-->

## AstaBrief: Ai2's Open-Source 8B Scientific Report Model — SFT+DPO Without RL

The biggest problem with AI-generated scientific reports isn't whether AI can write — it's whether what it writes can be trusted: whether citations are accurate, whether claims avoid over-inference, whether conclusions stay within the scope of the original research. Ai2 made a methodologically rigorous attempt at this problem with AstaBrief.

It's a Qwen3-8B fine-tune powering the "Fast mode" of Ai2's Asta research platform, now open-sourced with weights and training data.

HuggingFace: https://huggingface.co/allenai/AstaBrief | Ai2 | Qwen3-8B fine-tune | Apache 2.0

---

### Background: Asta Platform's Two Modes

Asta is Ai2's AI platform for researchers — it turns research questions into citation-backed synthesis reports. It has two modes:

- **Thinking mode**: Calls Claude, uses the multi-step ScholarQA pipeline (retrieve literature → organize into sections → synthesize with a strong model). High quality, 178.5 seconds per report.
- **Fast mode** (AstaBrief): One-pass report generation. 51.1 seconds. 3.5× faster.

Both modes face the same users and the same questions. AstaBrief found a new point on the quality-speed tradeoff.

---

### Training Data: 90K Real User Queries, Not Synthetic

Most fine-tuning datasets are synthetic — generate questions with a strong model, then generate answers. AstaBrief's data came from 7 months of real Asta platform user query logs.

After filtering (removing beta testers, bots, too-short queries, non-English, non-scientific, and personally identifiable queries via an LLM filtering pass), 90K research-focused queries remained. Real logs capture how researchers actually formulate problems — full context, multiple constraints, relationships between concepts — which synthetic data rarely replicates.

---

### SFT: 47K Samples, Multi-Model Generation

SFT targets were generated by the same multi-step ScholarQA pipeline used in Thinking mode, using a mix of Claude 3.5 Sonnet, Claude 3.7 Sonnet, o3, o4-mini, and GPT-4.1. After quality filtering: **47K usable training examples** from the 90K queries.

---

### DPO: Dual-Judge Filtering, 6K Preference Pairs

DPO requires preference pairs (A preferred over B), not single targets. Construction:
- One report per query from the ScholarQA/Claude pipeline
- The competing report generated by a different model (o3, o4-mini, DeepSeek-V3, or DeepSeek-R1) given the same retrieved literature
- **Two judge models** — GPT-4.1 and DeepSeek-R1 — independently selected the winner
- Only pairs where both judges agreed were kept

Result: 95% agreement with human preferences, ~**6K preference pairs**.

The core principle: no single model's output is treated as ground truth. Multiple generators reduce style bias; requiring dual-judge agreement filters noisy preferences. This is simpler than RL, more stable to train, and produces cleaner preference signal.

---

### Evaluation: Four Metrics, Three Benchmarks

Primary benchmark: **SQABench-CS2** — 200 researcher-written computer science questions.

Four metrics: rubric score (coverage), answer precision (relevance per paragraph), citation precision (does each citation support its claim), citation recall (are claims fully backed). Secondary: DeepScholarBench (63 queries on recent ArXiv papers), pairwise comparison against Claude pipeline (LLM-judged and human study).

---

### An Acknowledged Gap: Citation Match ≠ Scope Preservation

Ai2 flags a real limitation: models can cite the right study while still overstating what the study established — shifting a sample-specific finding to a universal population claim, moving past-tense results to present tense, converting descriptive findings into prescriptive recommendations. These are subtle over-inferences that citation match metrics don't catch. AstaBrief's evaluation doesn't cover this yet.

---

### Key Training Lessons

1. **Real user logs beat synthetic data** when measuring real-world query complexity
2. **Multi-model SFT generation** reduces single-model style lock-in
3. **Dual-judge DPO filtering** (requiring agreement) produces cleaner signal than single judge
4. **Size selection matters**: 8B is large enough for complex citation synthesis, small enough for production latency
5. **Citation metrics alone are insufficient** — add a claim-scope preservation check for any factual-grounding task

---

> AstaBrief by Allen Institute for AI (Ai2), released 2026-10-02, Qwen3-8B fine-tune. For technical reference only.
