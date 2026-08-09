---
title: "4B 小模型 RL 微调追平 GPT-5.6，成本百分之一：Castform 的技术框架与领域迁移预测"
titleEn: "A 4B Model Matches GPT-5.6 at One Percent of the Cost: Castform's RL Fine-Tuning Framework"
description: "Castform + Neon 的博客证明了一件事：4B 开源模型经过 RL 后训练，在金融检索任务上跑赢了 GPT-5.2，成本降低 100 倍。这篇文章深度拆解这套框架的三个核心组件（任务/环境/奖励函数）和合成数据管道，并分析将同样机制迁移到营销文案、邮件写作、社媒回帖、舆情分析等领域的可行性与卡点。"
descriptionEn: "Castform + Neon demonstrated that a 4B open-source model RL fine-tuned on domain-specific data outperforms GPT-5.2 on financial retrieval at 1/100 the cost. This analysis extracts the three-component RL framework (task/environment/reward) and the corpus-to-training-data pipeline, then evaluates how the same mechanism could work for marketing copy, email drafting, social media replies, and sentiment analysis."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Research"
tags: ["强化学习", "小模型", "RL微调", "领域专精", "RAG", "AI工具", "开源模型", "Mycelium"]
heroImage: "../../assets/images/castform-neon-small-model-rl-finetuning-domain-specialist-banner.jpg"
---

*by Mycelium Protocol*

---

一个让人看了会停下来的数字：4B 开源模型在金融检索任务上超过了 GPT-5.2，而且**每次请求成本是后者的百分之一**。

这不是 benchmark 游戏，是 Castform 和 Neon 在真实金融数据上跑出来的实验结果，2026 年 3 月的博客里公开了完整方法。8 月他们又发了一篇联合博客，把这套框架包装成了任意团队可以直接用的产品——数据库里有啥，就拿啥训练。

这件事真正有意思的地方不只是检索任务本身，而是背后的框架可以迁移到哪里。

---

## 为什么多轮检索是 AI 成本的死穴

2022 年大家都在做 embedding search：用 pgvector，做 RAG，一次查询返回结果。

2025 年之后，Agent 工作流变成主流。一个问题不再是一次检索，而是多轮规划 + 多次搜索循环，每次循环都是一次大模型 API 调用。

**具体代价**：用 GPT-5.6-Sol 跑一次多轮检索请求，端到端耗时超 10 秒，成本约 $0.03。对于需要规模化的场景，这是实实在在的瓶颈——不是太贵，是太贵加太慢。

小模型本来便宜 100 倍，但开箱即用的能力跟大模型没法比。**RL 后训练是弥合这个差距的路**——在特定任务上，不是通用能力的比拼，而是专项能力的专注打磨。

---

## 核心框架：三个组件，一个循环

RL 训练的骨架很清晰，Castform 把它拆成三个必要组件：

```
任务（Task）     ← 你想让模型学会做什么
环境（Environment） ← 模型在训练时能用什么工具
奖励函数（Reward Function） ← 怎么判断模型做得好不好
```

三个组件就位，训练变成一个**试错循环**：

```
模型尝试完成任务
  → 奖励函数打分
    → 梯度信号告诉模型下次怎么改
      → 重复，直到性能稳定
```

在 Castform 的检索实验里，三个组件的具体实现是：

- **任务**：回答金融数据库（FinDER，10K 条证券文件）里的问题，要求多跳推理
- **环境**：BM25 关键词搜索工具（选 BM25 不用 embedding search，原因是 embedding search 在 RL 训练中会引入噪声——措辞小变化就会改变检索结果，让训练不稳定）
- **奖励函数**：三个指标的加和

```python
def reward(trace, ground_truth):
    retrieval = ...   # 检索到正确的参考文本了吗？
    citation  = ...   # 正确引用了来源吗？
    correct   = ...   # 最终答案对吗？
    return retrieval + citation + correct
```

其中 `retrieval` 指标——「有没有检索到 ground truth reference chunk」——是防止奖励 Hacking 的关键。如果只用 LLM-as-judge 判断最终答案，模型会学会说对的话而不是找对的文本；加上检索指标就能约束住这个行为。

---

## 合成数据管道：从数据库到训练集

RL 训练的关键卡点在这里：**你需要一批有挑战性的问题，而几乎没有团队有这个数据集**。

Castform 在「rag-to-riches」博客里完整描述了三种方法的对比：

### 方法一：朴素生成（Naive）

```
抽一段文档 → 让 LLM 根据这段文字出一道题 → 存为 QA 对
```

快，便宜，但质量差：问题只需要一段文字就能答，不需要真实检索。用这种数据训出来的模型是模式匹配，不是检索推理。

### 方法二：SAGE（Google AI，搜索增强生成）

```
LLM 生成器用搜索工具主动找多个相关文档 → 生成跨文档的多跳问题
  → 另一个 LLM 作为 Judge，独立搜索验证难度
    → 两者迭代，直到问题达到目标难度
```

质量很高，接近资深工程师出的问题，但代价是**每道题 50+ 次 LLM 调用**，规模化不现实。

### 方法三：Castform 方案（中间路线，10x 更便宜）

```
预处理阶段（一次性）：
  → 为语料库建 chunk 间的关联图（父/子/语义相似节点）
  → 生成语料库 profile（摘要、示例查询、关键实体、领域术语）

每道题：
  生成阶段：给 LLM 一个 seed chunk + 关联邻居 → 生成多跳问题（1次调用）
  过滤阶段：
    → 检索过滤：这道题在 top-k 结果中直接出现了吗？（太简单，拒绝）
    → 答案验证：答案能从 source chunks 推导出来吗？（防止幻觉）
```

结果：比 SAGE 便宜 10 倍以上，质量比 Naive 方法显著更好，实现了规模化生产。

**最终数据格式**长这样（来自 Neon 博客的企业知识库示例）：

```
文档（来自你的数据）：
  "通过 Navan 预订的火车票由 GitLab 差旅卡支付。
   火车票必须选普通舱，且需提前 14 天预订。"

Ground Truth（从文档推断）：
  "火车票必须选普通舱，提前 14 天预订。"

问题（合成生成）：
  "在 Navan 预订铁路出行时，关于预订提前期和座位等级有什么规定？"
```

有了这批 QA 对，就可以定义工具（搜索）和奖励函数，启动 RL 循环。

---

## 训练中遇到的真实工程问题

Castform 公开了训练过程中踩到的坑，这部分是含金量最高的技术细节。

### 问题一：奖励 Hacking

LLM-as-Judge 会被模型找到漏洞：实验中模型发现「在回答里加 emoji 可以提高简洁性评分」，开始刷分而不是真正简洁。

**解法**：维护一批语义等价的 judge prompt，每次打分时随机采样一个。模型无法固定在某个 prompt 的 quirk 上过拟合。

### 问题二：训练-推理分布不匹配

RL 训练分两个组件：rollout engine（采样）和 trainer（更新）。高吞吐下两者之间的概率分布不一致，导致训练极不稳定。

**解法**：改用 DPPO（来自 Qi et al. 2026）——确保低概率 token 不被过度惩罚（让模型继续探索新路径），同时限制 trainer ↔ rollout 之间差距过大的情况。

### 问题三：早期行为——查询回显

训练初期模型倾向于把用户问题原封不动搜索一次就停止。RL 信号逐渐把它推向了多轮行为——信息不足时继续搜，信息够了才终止。这是涌现出来的，不是显式编程进去的。

---

## 结果：4B 模型超过 GPT-5.2

| 对比维度 | 结果 |
|---------|------|
| 最终答案正确率 vs GPT-5.2 | +35%（RL 微调后） |
| Pass@8 提升 | +63%（真正学会解决更多问题，而非只是更稳定） |
| 每次请求成本 | 1/100（$0.0003 vs $0.03） |
| 延迟 | 从 >10 秒 → 接近实时 |

Pass@8 的提升尤其重要：它衡量的是「8 次尝试里至少一次成功的概率」。这个指标上升，说明模型**真的学会了解决更多问题**，而不只是把同样的答案打磨得更可靠。

---

## 框架迁移：其他领域有没有可能

这套框架的核心抽象是：

```
任意领域的 RL 小模型训练
= 语料库
  + 任务定义（做什么）
  + 可评分的奖励函数（好不好）
  + 工具环境（模型能用什么）
```

判断一个领域是否适合的核心问题只有一个：**你能不能写出一个计算机可以运行的奖励函数？**

如果可以，这套机制就能迁移。下面逐一分析。

---

### 领域一：营销文案

**语料库**：过往高转化率广告 + 产品说明书 + 竞品定位分析

**任务**：为产品 X 生成面向目标受众 Y 的文案

**环境**：工具可以查询品牌规范文档、产品规格、竞品分析库

**奖励函数**：
```python
def reward(generated_copy):
    brand_compliance = check_brand_guidelines(generated_copy)  # 品牌规则符合率
    format_check     = check_required_elements(generated_copy) # 必要元素是否齐全
    quality_judge    = llm_judge(generated_copy, rubric)       # LLM 质量评分
    return brand_compliance + format_check + quality_judge
```

**优势**：品牌规范是代码可检查的（关键词不能用/必须用、长度限制、CTA 格式），奖励函数可以精确定义。

**最大卡点**：真实效果（点击率、转化率）有延迟，无法直接作为训练信号。需要用 proxy reward（专家打分 + 规范检查）代替。

**可行性判断**：✅ 高度可行，但需要准备好品牌规范的代码化表达。

---

### 领域二：邮件写作（冷邮件/客户回复）

**语料库**：历史发送邮件 + 对应的回复率/开信率数据

**任务**：为目标画像 X + 情境 Y 起草邮件

**环境**：工具可以查询 CRM 数据、潜客公司信息、历史互动记录

**奖励函数**：
```python
def reward(email, persona):
    historical_match = similarity_to_high_reply_emails(email)  # 与高回复率历史邮件的相似度
    compliance       = check_compliance(email)                  # 合规检查
    personalization  = check_personalization(email, persona)    # 个性化程度
    return historical_match + compliance + personalization
```

**核心优势**：这是所有领域里奖励信号**最直接**的一个。历史邮件 + 回复率数据是天然的标注数据集——高回复率的邮件就是正样本，低回复率的是负样本，不需要人工标注。

**卡点**：需要有足够量的历史邮件数据（几千封以上才能做有效训练）。

**可行性判断**：✅ 最强的迁移场景，奖励信号最清晰。

---

### 领域三：社媒回帖 / 评论回复

**语料库**：历史回帖记录 + 品牌声音指南 + 用户互动数据

**任务**：对帖子/评论 C 生成符合品牌声音的回复

**环境**：工具可以查询线程上下文、品牌指南库、类似场景历史回复

**奖励函数**：
```python
def reward(reply, thread_context):
    tone_compliance  = check_brand_voice(reply)               # 品牌声音一致性
    safety_check     = check_brand_safety(reply)               # 品牌安全
    relevance        = check_relevance_to_thread(reply, context) # 相关性
    quality          = llm_judge(reply, rubric)                # 质量打分
    return tone_compliance + safety_check + relevance + quality
```

**难点**：「好的回帖」比「好的邮件」更难精确定义——品牌声音是定性的，不同人理解不同。奖励函数质量直接决定训练出来的模型质量。

**特别场景**：如果目标是**高互动率**而不是品牌合规（比如做社区运营），可以用历史帖子的点赞/转发数据作为 proxy reward，但要防止模型学出哗众取宠的内容。

**可行性判断**：⚠️ 可行，但奖励函数设计需要更多投入，品牌声音要显式代码化。

---

### 领域四：舆情分析 / 趋势判断

**这是框架迁移里最容易成功的场景。**

原因：这是分类/分析任务，不是生成任务。奖励函数 = 准确率，没有主观性。

**语料库**：历史标注数据（过去的舆情标签、趋势报告）

**任务**：给定文本 X，判断情感 / 识别趋势信号 / 提取关键实体

**环境**：工具可以查询历史库、行业词典、背景知识库（用于多跳分析）

**奖励函数**：
```python
def reward(prediction, ground_truth):
    return accuracy(prediction, ground_truth)  # 就是这么简单
```

**关键结合点**：这套框架最大的价值是「检索增强分析」——不是直接在固定知识上分类，而是让模型**主动搜索历史相似案例 + 背景资料**，再做判断。这让 4B 模型做到「有检索能力的情感分析」，而不只是一个分类器。

**具体例子**：

```
任务：判断这条微博的情感及品牌影响等级

模型行为（RL 训练后涌现）：
1. 搜索「该品牌近 30 天类似负面内容的历史处理」
2. 搜索「该博主历史传播力数据」
3. 搜索「该关键词当前热度趋势」
4. 综合以上，输出结构化分析报告
```

这是一个「会用工具主动收集背景信息再分析」的专家模型，而不是一个纯分类器。

**可行性判断**：✅✅ 最强可行性，有 ground truth 标签就能训。

---

## 迁移的统一判断框架

把四个领域的分析总结成一张决策矩阵：

| 领域 | 奖励函数可精确化？ | 历史数据量 | 迁移可行性 |
|------|-------------------|-----------|-----------|
| 邮件写作 | ✅ 历史回复率直接用 | 需要 5K+ 封 | ✅✅ 最强 |
| 舆情分析 | ✅ 准确率 = 直接奖励 | 需要标注数据 | ✅✅ 极强 |
| 营销文案 | ⚠️ 需要 proxy（品牌规范代码化） | 广泛可得 | ✅ 强 |
| 社媒回帖 | ⚠️ 品牌声音难量化 | 广泛可得 | ⚠️ 中等 |

**通用准入标准**，判断你的场景是否适合：

1. **你有语料库吗？** 内部文档、历史记录、产品数据库——不需要标注，只需要存在
2. **你能写出奖励函数吗？** 把「什么是好的输出」翻译成可运行的代码（哪怕是 LLM-as-judge + 规范检查的组合）
3. **任务是重复性的吗？** 每天/每周都在做同样类型的工作，量足够大（百次以上）

满足三条，就值得认真评估 RL 微调。

---

## 当前的真实门槛

诚实地说：Castform 解决了基础设施问题（不需要懂 GPU，不需要写训练循环），但**奖励函数设计**这个最核心的智识工作，还是需要人来做。

这个工作不难，但需要你能回答一个问题：**我怎么知道模型做对了？**

这个问题想清楚了，剩下的工程问题 Castform 帮你兜底。

---

参考：  
Castform + Neon 联合博客：[neon.com/blog/how-castform-neon-beats-frontier-models-on-price-and-efficiency](https://neon.com/blog/how-castform-neon-beats-frontier-models-on-price-and-efficiency)  
RAG-not-LAG：[castform.com/blog/rag-not-lag](https://castform.com/blog/rag-not-lag)  
RAG-to-Riches（合成数据管道）：[castform.com/blog/rag-to-riches](https://castform.com/blog/rag-to-riches)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## 4B Model RL Fine-Tuned to Match GPT-5.6 at 1/100 the Cost — Framework Analysis and Domain Transfer Predictions

*by Mycelium Protocol*

---

One number makes this worth a closer look: a 4B open-source model, RL fine-tuned on domain-specific financial data, **outperformed GPT-5.2 on retrieval tasks at 1/100th the cost per request**.

This is not a benchmark exercise. Castform published the methodology in March 2026 with real results against the FinDER dataset (10,000 financial filings). In August they published a joint post with Neon turning the framework into a product anyone can point at their own database.

The interesting part is not the retrieval result itself — it's where the underlying framework transfers to.

---

### Why Multi-Turn Retrieval Is the AI Cost Bottleneck

2022: embedding search. pgvector everywhere, one-shot RAG pipelines, single vector query per user request.

2025+: agentic retrieval. Models plan and search multiple times in a loop. Every loop iteration is another frontier model API call. Every call adds latency.

The concrete numbers: a typical multi-turn search with GPT-5.6-Sol takes >10 seconds and costs ~$0.03 end-to-end. At any meaningful scale, that's a bottleneck — not too expensive to run once, too expensive to run thousands of times per day.

Small open-weights models are 100x cheaper, but their out-of-the-box capabilities lag. RL post-training is the bridge: not general capability improvement, but focused specialization on one task the model will run thousands of times.

---

### The Core Framework: Three Components, One Loop

The RL training skeleton is straightforward. Castform decomposes it into three required components:

```
Task        ← what should the model learn to do
Environment ← what tools does it have during training
Reward      ← how do we score whether it did well
```

Three components in place, training becomes a trial-and-error loop:

```
Model attempts the task with available tools
  → Reward function scores the attempt
    → Gradient signal adjusts the model
      → Repeat until performance plateaus
```

In Castform's retrieval experiment, the three components were:

- **Task**: Answer questions over a financial document corpus, requiring multi-hop reasoning
- **Environment**: BM25 keyword search tool (not embedding search — embedding results are noisy during RL training because small prompt changes shift retrieval results, destabilizing the loop)
- **Reward function**:

```python
def reward(trace, ground_truth):
    retrieval = ...   # Did it retrieve the right source chunks?
    citation  = ...   # Did it cite the right passages?
    correct   = ...   # Is the final answer right?
    return retrieval + citation + correct
```

The `retrieval` metric — whether the model actually found the ground-truth reference chunks — is the key anti-reward-hacking guard. Without it, models learn to produce correct-sounding answers without actually finding the right information.

---

### Corpus to Training Data: The Synthetic Pipeline

The blocker for most teams is the training dataset. RL training needs challenging, grounded questions. Almost no one has those ready.

Castform's "rag-to-riches" post compares three approaches:

**Naive:** Sample a chunk, ask an LLM to generate a question about it. Fast and cheap. Results in shallow, single-hop questions that train pattern matching, not retrieval.

**SAGE (Google AI):** LLM generator uses search tools to explore multiple documents, generates multi-hop questions. A second LLM judge independently verifies difficulty. They iterate until questions meet a target difficulty. High quality — but 50+ LLM calls per question. Impractical at scale.

**Castform approach (10x cheaper, similar quality):**

```
Pre-processing (one-time):
  → Build chunk relationship graph (parent/sibling/semantic neighbors)
  → Generate corpus profile (summary, example queries, entities, terminology)

Per question:
  Generation: seed chunk + linked neighbors → LLM generates multi-hop question (1 call)
  Filtering:
    → Retrieval check: does top-k search return the answer trivially? (reject if yes)
    → Grounding check: does the answer actually follow from source chunks? (reject hallucinations)
```

Result: 10x fewer LLM calls than SAGE, substantially better quality than naive, practical at scale.

**The final training data format** (from the Neon blog enterprise knowledge base example):

```
Document (from your data):
  "Train rides booked through Navan are paid by the GitLab travel card.
   Train rides must be standard cabin class with a 14-day booking lead time."

Ground truth (inferred from document):
  "Train rides must be standard cabin class, with a 14-day booking lead time."

Question (synthetically generated):
  "When booking a rail trip through Navan, what are the rules for how far
   in advance I need to book and what cabin class I'm allowed to choose?"
```

---

### Real Engineering Problems Encountered

Castform published the training failures too. This is the high-value technical content.

**Reward hacking:** LLM-as-judge rubrics can be gamed. The model discovered that sprinkling emojis increased conciseness scores. Fix: maintain a pool of semantically equivalent judge prompts, sample one randomly per evaluation. The model can't overfit to a single prompt's quirks.

**Train-inference mismatch:** RL training has two components — a rollout engine (sampling) and a trainer (gradient updates). At high throughput, probability distributions diverge between the two, causing unstable training. Fix: DPPO (Qi et al. 2026) — ensures low-probability tokens aren't over-penalized (preserving exploration) while constraining cases where trainer ↔ rollout divergence is high.

**Query echoing:** In early training, the model copies the user query verbatim and searches once, then stops. RL signal gradually pushes it toward multi-turn behavior — search again when information is insufficient, stop when it's enough. This emerged; it was not explicitly programmed.

---

### Results

| Metric | Result |
|--------|--------|
| Final answer correctness vs GPT-5.2 | +35% |
| Pass@8 improvement | +63% |
| Cost per request | 1/100 (~$0.0003 vs ~$0.03) |
| Latency | >10s → near-instant |

Pass@8 matters: it measures whether at least one of 8 sampled attempts solves the task. Rising pass@8 means the model is **actually learning to solve more problems** — not just producing more consistent answers to the same problems it already solved.

---

### Domain Transfer: Where Else Does This Work?

The framework's core abstraction:

```
RL fine-tuning for any domain
= corpus (your documents and data)
  + task definition (what should the model do)
  + scorable reward function (how do we know it did well)
  + tool environment (what can the model use)
```

The single judgment question for any domain: **can you write a reward function a computer can run?**

If yes, the mechanism transfers. Here's the domain-by-domain analysis.

---

**Email writing (cold outreach / customer replies)**

Corpus: historical sent emails + their open/reply/conversion rates.

Task: draft an email for persona X in context Y.

Environment: tools to look up CRM data, prospect company info, prior interactions.

Reward:
```python
def reward(email, persona):
    historical_match = similarity_to_high_reply_emails(email)
    compliance       = check_compliance(email)
    personalization  = check_personalization(email, persona)
    return historical_match + compliance + personalization
```

Key advantage: **this has the clearest reward signal of any domain**. Historical emails + reply rate data are direct positive/negative labels — no manual annotation needed. High-reply emails are positive examples; low-reply emails are negative examples. The training signal is already in your email system.

Viability: ✅✅ Strongest transfer case.

---

**Marketing copy**

Corpus: past high-performing campaigns, product specs, brand guidelines, competitor positioning.

Task: generate copy for product X targeting audience Y.

Environment: tools to look up brand rules, product attributes, competitive analysis.

Reward:
```python
def reward(copy):
    brand_compliance = check_brand_guidelines(copy)  # explicitly coded rules
    format_check     = check_required_elements(copy) # CTA, length, structure
    quality          = llm_judge(copy, rubric)
    return brand_compliance + format_check + quality
```

Advantage: brand guidelines are often code-checkable (forbidden words, required elements, character limits, CTA format). This makes the reward function precise.

Key limitation: actual effectiveness (click rate, conversion) is delayed. You need a proxy reward based on rules + expert judgment rather than direct business metrics.

Viability: ✅ Strong — but requires converting brand guidelines into executable code.

---

**Social media replies and comments**

Corpus: historical reply records, brand voice guides, engagement data.

Task: generate a brand-voice-consistent reply to post/comment C.

Environment: tools to look up thread context, brand guidelines, similar historical replies.

Reward:
```python
def reward(reply, context):
    tone    = check_brand_voice(reply)
    safety  = check_brand_safety(reply)
    quality = llm_judge(reply, rubric)
    return tone + safety + quality
```

Key difficulty: "good social reply" is harder to define precisely than "good email" — brand voice is qualitative, and different people interpret it differently. Reward function quality directly determines model quality.

Special case: if the goal is high engagement rather than brand compliance (community management), historical like/share data can serve as proxy reward — but watch for the model learning to be provocative rather than genuinely good.

Viability: ⚠️ Feasible, but reward function design requires more investment. Brand voice must be explicitly codified.

---

**Sentiment analysis and trend detection**

This is the easiest domain to transfer into.

Reason: it's a classification/analysis task, not a generation task. The reward function is accuracy. No subjectivity.

Corpus: historically labeled data (past sentiment labels, trend reports).

Task: given text X, classify sentiment / identify trend signals / extract entities.

Environment: tools to look up historical similar cases, industry lexicons, background knowledge bases.

Reward:
```python
def reward(prediction, ground_truth):
    return accuracy(prediction, ground_truth)  # that's it
```

The key value-add of the RL framework here: the model learns to **actively search for relevant context before classifying**, not just classify from a fixed prompt. A 4B model that retrieves "similar past cases from the last 30 days" and "author historical influence data" before issuing a sentiment verdict is a qualitatively different tool than a static classifier.

Example behavior that emerges from RL training:

```
Task: classify sentiment and brand impact of this post

Model (RL-trained, multi-turn):
1. Search: "brand's similar negative incidents in last 30 days"
2. Search: "author's historical reach and virality data"  
3. Search: "current trending intensity for this keyword"
4. Output: structured analysis report combining all three
```

Viability: ✅✅ Strongest fit after email writing. Ground-truth labels give a clean reward signal.

---

### Decision Matrix for Your Domain

| Domain | Reward function precision | Historical data available | Transfer viability |
|--------|--------------------------|--------------------------|-------------------|
| Email writing | ✅ Direct reply rate | Needs 5K+ emails | ✅✅ Strongest |
| Sentiment analysis | ✅ Accuracy = direct reward | Needs labeled data | ✅✅ Excellent |
| Marketing copy | ⚠️ Proxy via brand rules | Widely available | ✅ Strong |
| Social replies | ⚠️ Brand voice is qualitative | Widely available | ⚠️ Moderate |

**Universal eligibility criteria** — your domain is a fit if:

1. **You have a corpus.** Internal docs, historical records, product databases — unlabeled is fine, it just needs to exist.
2. **You can write a reward function.** Translate "what is a good output" into runnable code — even if it's LLM-as-judge + rule checks combined.
3. **The task is repetitive.** You're doing the same type of work daily or weekly, at volume (hundreds of instances minimum).

Three conditions met → worth a serious evaluation.

---

### The Honest Remaining Barrier

Castform solves the infrastructure problem: no GPU expertise, no training loop code, no MLOps. But **reward function design** — the most intellectually demanding step — is still yours to do.

It's not technically hard. It requires answering one question clearly: **how do I know the model did this right?**

Get that question answered, and Castform handles the rest.

---

Castform + Neon joint blog: [neon.com/blog/how-castform-neon-beats-frontier-models-on-price-and-efficiency](https://neon.com/blog/how-castform-neon-beats-frontier-models-on-price-and-efficiency)  
RAG-not-LAG: [castform.com/blog/rag-not-lag](https://castform.com/blog/rag-not-lag)  
RAG-to-Riches (synthetic data pipeline): [castform.com/blog/rag-to-riches](https://castform.com/blog/rag-to-riches)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
