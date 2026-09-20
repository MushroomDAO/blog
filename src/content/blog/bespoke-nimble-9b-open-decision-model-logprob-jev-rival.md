---
title: "Bespoke Nimble：一天之内做一个会读概率的 9B 决策模型"
titleEn: "Bespoke Nimble: A 9B Decision Model Built in One Day That Reads Probabilities"
description: "Bespoke Labs 开源了 Nimble，一个基于 Qwen3.5-9B LoRA 的决策模型——它不写字，只在你给的选项里选一个，直接读 logprobs。数据、配方、权重全部公开，本文做一次工程层面的完整拆解。"
descriptionEn: "Bespoke Labs open-sourced Nimble, a Qwen3.5-9B LoRA decision model that never generates text — it picks from your options by reading logprobs directly. Data, recipe, and weights are all public. This article does a full engineering teardown."
pubDate: 2026-09-20
category: "Tech-Experiment"
tags: ["open-source", "decision-model", "logprob", "LoRA", "inference", "Qwen"]
lang: zh-CN
heroImage: "../../assets/images/bespoke-nimble-9b-open-decision-model-logprob-jev-rival-banner.jpg"
---

Jev 还在排队，开源版已经出来了。

Bespoke Labs 发布了 **Bespoke Nimble**，一个基于 Qwen3.5-9B 的 LoRA 决策模型。核心设计只有一条：**它不生成文字，只在你给的选项里挑一个，直接读 logprobs。** 数据、训练配方、权重全摊在 GitHub 上（bespokelabsai/nimble，目前约 463 stars）。

这篇文章做一次工程层面的完整拆解。

---

## 它解决的问题

用大模型做判断有两种路子：

1. **让模型写出推理过程，最后再给答案**（CoT）——慢，输出量大，还要解析 JSON。
2. **直接读候选 token 的 logits，转成概率，挑概率最高的**——快，零解析成本，天然返回置信度分布。

TypeSafe 的 Jev 走的就是第二条路，做法叫"System One"决策。Bespoke Labs 看了 [Niels Rogge 的拆解帖子](https://x.com/NielsRogge/status/2100239244501430438)，用了一天时间，把同样的路子用 LoRA 复现出来，然后把全套东西公开了。

重点：**他们没有蒸馏 Jev，Jev 只用来打分**。

---

## 工作方式

使用接口极简：

```python
from nimble.scoring.parallel_scorer import ParallelScorer

scorer = ParallelScorer("path/to/bespoke-nimble-9b")
result = scorer.score(
    context="退款申请：用户在收货后 15 天提交，商品未拆封。",
    schema={
        "eligible": {"type": "boolean"},
        "category": {"type": "enum", "choices": ["full_refund", "partial_refund", "denied"]},
    }
)
# result.eligible.answer → True / False，附带 True/False 的概率
# result.category.answer → "full_refund"，附带三个选项的概率分布
```

两个约束要记住：

- **Schema 必须是平的**：没有嵌套字段，每个字段要么是 enum 要么是 boolean。
- **最多 2,048 tokens**：context + schema 合计不能超，超了直接拒。

每个字段独立评分，意味着字段之间没有依赖关系——一个字段的答案看不见另一个字段的结果。

---

## 底层机制

每个允许的答案被映射到一个 token（1-token code）。评分时：

```
prompt → model → logits[token_A, token_B, token_C] → softmax → 概率分布 → 选最高的
```

没有 JSON 生成，没有解析，没有采样。

在 Mac 上，`ParallelScorer` 用 MLX 实现，共享 context 只处理一次，然后所有字段并行评分。CUDA 版本每个字段跑一次完整 forward pass，无法共享 KV cache（这是 GPU 上延迟比 Mac 高的原因之一）。

---

## 数据和训练

训练集共 2,826 个样本，评估集 324 个。数据构造方法叫**对比数据策划（contrastive data curation）**：

- 先生成一条正确样本（context + schema + 正确答案）。
- 修改 context 里的一个关键事实，让答案翻转，生成负样本。
- 模型从这对对比样本里学习"如何定位关键证据"，而不是记住答案本身。

训练用 LoRA 加在 Qwen3.5-9B 上，BF16 精度，只对候选 token 的位置优化交叉熵。硬件：L40S 上训练，H100 上做最终拟合和评估。

---

## 基准测试

在 324 个 held-out 样本上的准确率（来自项目自报数据，请打折看）：

| 模型 | 准确率 |
|------|--------|
| Qwen3.5-9B 基础模型 | 66.4% |
| **Bespoke-Nimble-9B** | **90.1%** |
| Jev 1.13.0 | 93.2% |

跟 Jev 差 3 个点，比基础模型高 24 个点。考虑到只有 2,826 条训练样本，差距已经相当小。

延迟对比（同一 324 样本集）：

| 系统 | 中位数 | p95 |
|------|--------|-----|
| Bespoke-Nimble-9B（H100，120样本子集）| 106ms | 120ms |
| Bespoke-Nimble-9B（M5 Pro 64GB，完整324样本）| 444ms | 981ms |
| Jev 1.13.0（TypeSafe API）| 247ms | 347ms |
| Qwen3.5-9B 基础（H100）| 58ms | 76ms |

注意：GPU 上 Nimble 比 Jev API 要快，本地 M5 Pro 上用完整 9B 跑当然比云端 API 慢一截。

---

## 本地运行（Mac Apple Silicon）

**前提**：Apple Silicon Mac，Python 3.12（必须用原生 macOS Python 才能用 Metal）。18GB 未量化权重，64GB 内存的 Mac 比 24GB 机器留有更多裕量给 merge 步骤。

```bash
git clone https://github.com/bespokelabsai/nimble.git
cd nimble

# 创建 MLX 推理环境
python3.12 -m venv .venvs/mlx
source .venvs/mlx/bin/activate
pip install mlx mlx-lm -r requirements/mlx.txt

# 下载并 merge LoRA adapter
python - <<'PYTHON'
from huggingface_hub import snapshot_download
snapshot_download("bespokelabs/Bespoke-Nimble-9B", cache_dir=".cache/huggingface/hub")
PYTHON

# 运行示例
python examples/basic_scoring.py
```

目前没有官方量化版本，18GB 就是 18GB。需要降显存的用户要自己量化或等官方后续。

---

## 适用场景

| 场景 | 你定义 | 你得到 |
|------|--------|--------|
| 请求路由 | 目标列表 + 各自触发条件 | 目标选项 + 每个选项的概率 |
| 条件检查 | 是非题 + 证据文本 | true/false + 置信度 |
| 策略执行 | 规则 + 允许的结果 | 基于 context 的决策 |
| 结果评级 | 有序等级 + 明确评分标准 | 等级 + 概率分布（可算期望值）|

不适用的场景：图片/多模态输入、需要模型自己写文字、嵌套结构输出、单字段超过 26 个选项。

---

## 关键限制

- **概率不等于正确率**：0.9 的置信度不代表答案 90% 是对的。输出的概率是 softmax 归一化到你提供的选项上的，如果所有选项都不对，最高概率也会被分到某一个上。实际使用前要在自己的数据集上标定阈值。
- **训练数据范围窄**：2,826 条样本覆盖 10 个类别，对域外任务的泛化能力有限。README 原话：别期望太多泛化，但比基础模型整体还是好。
- **字段顺序无依赖**：单个 prompt 里的多个字段互相看不见答案，需要应用层做一致性校验。
- **没有量化**：目前无官方量化，18GB 是硬门槛。
- **无标准开源 License**：GitHub 没有 SPDX license 标注，商用前需要确认。

---

## 工程价值

真正值得关注的不是 90.1% vs 93.2%，而是整套东西全摊开了：

- 数据怎么造（contrastive curation 的完整流程）
- LoRA 怎么训（schema-aware 的目标函数）
- logprob 评分怎么实现（MLX parallel scorer 和 CUDA scorer 都有）
- 怎么评估（跟 Jev 的对比 app、公开基准测试流程）

这套配方可以移植到任何 Qwen 系列模型上，也可以针对特定领域自己扩充训练数据。前置项目 Bespoke-MiniCheck（跟 Greg Durett 合作的事实核查模型）两年前就在这条路上，Nimble 是逻辑延伸。

> 开源代码与模型仅供学习研究，请勿直接用于生产系统。

---

**仓库**：github.com/bespokelabsai/nimble  
**模型**：huggingface.co/bespokelabs/Bespoke-Nimble-9B  
**作者**：Bespoke Labs + Maheswaran Sathiamoorthy

<!--EN-->

Jev is still in waitlist. The open-source version just shipped.

Bespoke Labs released **Bespoke Nimble**, a LoRA decision model based on Qwen3.5-9B. The core design has exactly one rule: **it never generates text — it picks from the options you provide by reading logprobs directly.** The data, training recipe, and weights are all on GitHub (bespokelabsai/nimble, ~463 stars).

This article is a full engineering teardown.

---

## The problem it solves

Using large models for judgment follows two paths:

1. **Have the model write out reasoning, then give an answer** (CoT) — slow, high token count, requires JSON parsing.
2. **Read logits for candidate tokens directly, convert to probabilities, pick the highest** — fast, zero parsing cost, returns a confidence distribution naturally.

TypeSafe's Jev takes the second path, calling it "System One" decision-making. Bespoke Labs saw Niels Rogge's teardown post, spent one day replicating the approach with LoRA, and open-sourced everything.

Key point: **they did not distill from Jev. Jev was only used for scoring.**

---

## How it works

The API is minimal:

```python
from nimble.scoring.parallel_scorer import ParallelScorer

scorer = ParallelScorer("path/to/bespoke-nimble-9b")
result = scorer.score(
    context="Refund request: user submitted 15 days after delivery, product unopened.",
    schema={
        "eligible": {"type": "boolean"},
        "category": {"type": "enum", "choices": ["full_refund", "partial_refund", "denied"]},
    }
)
# result.eligible.answer → True/False with per-label probability
# result.category.answer → "full_refund" with full probability distribution
```

Two hard constraints:

- **Schema must be flat**: no nested fields, every field is either enum or boolean.
- **2,048 token limit**: context + schema combined — exceeded prompts are rejected outright.

Each field is scored independently — one field cannot see another field's answer.

---

## The mechanism

Each allowed answer maps to one token (1-token code). Scoring:

```
prompt → model → logits[token_A, token_B, token_C] → softmax → probability distribution → argmax
```

No JSON generation, no parsing, no sampling.

On Mac, `ParallelScorer` uses MLX: the shared context is processed once, then all fields are scored in parallel. The CUDA scorer runs one full forward pass per field — no KV cache sharing — which is why Mac latency is lower per-example when schemas have multiple fields.

---

## Data and training

Training set: 2,826 samples. Eval set: 324 samples. The data construction method is called **contrastive data curation**:

- Generate a correct sample (context + schema + correct answer).
- Modify one key fact in the context to flip the answer — create a negative sample.
- The model learns from these contrastive pairs how to isolate critical evidence.

Training applies LoRA on Qwen3.5-9B, BF16 precision, cross-entropy only over candidate token positions. Hardware: L40S for training, H100 for final fit and evaluation.

---

## Benchmarks

Accuracy on 324 held-out samples (self-reported — apply a discount):

| Model | Accuracy |
|-------|----------|
| Qwen3.5-9B base | 66.4% |
| **Bespoke-Nimble-9B** | **90.1%** |
| Jev 1.13.0 | 93.2% |

3 points behind Jev, 24 points above the base model — on only 2,826 training samples.

Latency comparison (same 324-sample set):

| System | Median | p95 |
|--------|--------|-----|
| Bespoke-Nimble-9B (H100, 120-sample subset) | 106ms | 120ms |
| Bespoke-Nimble-9B (M5 Pro 64GB, full 324) | 444ms | 981ms |
| Jev 1.13.0 (TypeSafe API) | 247ms | 347ms |
| Qwen3.5-9B base (H100) | 58ms | 76ms |

On GPU, Nimble is faster than the Jev API. On local M5 Pro with the full 9B, it's slower than the cloud API.

---

## Running locally on Mac (Apple Silicon)

**Prerequisites**: Apple Silicon Mac, Python 3.12 (native macOS Python for Metal). 18GB unquantized weights. 64GB RAM recommended for the merge step.

```bash
git clone https://github.com/bespokelabsai/nimble.git
cd nimble

python3.12 -m venv .venvs/mlx
source .venvs/mlx/bin/activate
pip install mlx mlx-lm -r requirements/mlx.txt

python - <<'PYTHON'
from huggingface_hub import snapshot_download
snapshot_download("bespokelabs/Bespoke-Nimble-9B", cache_dir=".cache/huggingface/hub")
PYTHON

python examples/basic_scoring.py
```

No official quantization exists yet. 18GB is the floor until the community adds it.

---

## Use cases

| Use case | You define | You get back |
|----------|-----------|-------------|
| Request routing | Destinations + trigger conditions | Chosen destination + probability per option |
| Condition checking | Yes/no question + evidence | True/False + confidence |
| Policy enforcement | Rules + allowed outcomes | Typed decision from context |
| Outcome rating | Ordered levels + clear criteria | Level + probability distribution (computable expected value) |

Not applicable: image/multimodal input, free-text generation, nested output structures, enum fields with more than 26 choices.

---

## Key limitations

- **Probability ≠ correctness**: A probability of 0.9 does not mean the answer is correct 90% of the time. The output is softmax-normalized over the options you supplied — if none of your options fit, the highest probability still gets assigned to something. Calibrate thresholds on your own data.
- **Narrow training coverage**: 2,826 samples across 10 categories. Out-of-domain generalization is limited. The README is honest: "don't expect a lot of generalization."
- **No cross-field dependencies**: Fields in a single prompt can't see each other's answers. Application code must do consistency checks.
- **No quantization**: 18GB is the hard floor for now.
- **No standard OSI license**: No SPDX license in the GitHub repo. Verify before any commercial use.

---

## Engineering value

The real story isn't 90.1% vs 93.2%. It's that the full stack is open:

- How to build contrastive data (complete curation pipeline)
- How to train the LoRA (schema-aware objective function)
- How to implement logprob scoring (both MLX parallel scorer and CUDA scorer)
- How to evaluate (Jev comparison app, public benchmark workflows)

This recipe can be ported to any Qwen-series model and extended with domain-specific training data. The predecessor Bespoke-MiniCheck (a factual verification model built with Greg Durett) laid the groundwork two years ago. Nimble is the logical extension.

> Open-source code and model are for learning and research only. Do not deploy directly in production systems.

---

**Repository**: github.com/bespokelabsai/nimble  
**Model**: huggingface.co/bespokelabs/Bespoke-Nimble-9B  
**Authors**: Bespoke Labs + Maheswaran Sathiamoorthy
