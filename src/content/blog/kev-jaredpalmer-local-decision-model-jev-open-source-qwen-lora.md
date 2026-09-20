---
title: "Kev：Jared Palmer 开源本地决策模型，一次前向传播回答多个问题"
titleEn: "Kev: Jared Palmer's Open-Source Local Decision Model — One Forward Pass, Many Questions"
description: "Apache-2.0，LoRA + 块因果掩码，文档编码一次、多个问题并发出概率分布，不生成文字。4B 版 OOD 准确率 0.790，比 Jev 低 6~7 个点，上限 8192 token，本地 Mac 可跑。"
descriptionEn: "Apache-2.0 local decision model: LoRA + block-causal masking, one document encoding fans out across multiple question branches simultaneously, pure probability distributions, no text generation. 4B model hits 0.790 OOD accuracy — 6-7pp below Jev — with 8k token context, runnable on a 32GB Mac."
pubDate: 2026-09-20
heroImage: "../../assets/images/kev-jaredpalmer-local-decision-model-jev-open-source-qwen-lora-banner.jpg"
category: "Tech-Experiment"
tags: ["decision-model", "local-ai", "qwen", "lora", "classification", "open-source"]
lang: zh-CN
---

[Kev](https://github.com/jaredpalmer/kev) 是 Jared Palmer（Formik、Turborepo 作者）开源的本地决策模型。它不生成文字——给它一段文档和一批问题，它一次前向传播同时返回所有问题的概率分布。思路来自 TypeSafe 的 Jev，后者由研究者 Archer Hume 从头逆向推导。

**仓库**：github.com/jaredpalmer/kev | **License**：Apache-2.0 | **Stars**：606

---

## 核心设计：一次编码，多路分支

传统做法是每个问题单独调 API。Kev 用**块因果掩码（block-causal masking）**把文档和所有问题打包进一条序列——每个问题分支只能看文档、看不到兄弟问题。文档编码一次，所有问题并发出结果：

```
[Document] → [Q1 branch] → P(option_A) / P(option_B)
           → [Q2 branch] → P(yes) / P(no)
           → [Q3 branch] → expected-value score
```

模型在问题 logit 上直接 softmax，不 decode 任何 token。打包 vs 分开请求的概率最大差值：**4e-6**，throughput **2×**，isolation 验证通过。

---

## 三种问题类型

| 类型 | 用法 | 输出 |
|------|------|------|
| `noul` | 二元是/否 | P(yes) / P(no) |
| `choice` | 2~255 个离散选项 | 每个选项的置信度 |
| `score` | 有序档位（如"强/中/弱"） | 期望值 + 各档概率 |

---

## 四个模型变体

| 模型 | 基座 | OOD 准确率（test） | M5 延迟 |
|------|------|---------------------|---------|
| kev-0.5b | Qwen2.5-0.5B | 0.575 | ~160ms (fp32) |
| kev-0.6b | Qwen3-0.6B-Base | 0.631 | — |
| **kev-4b** | Qwen3-4B-Base | **0.806** | ~277ms (bf16) |
| kev-8b | Qwen3-8B-Base | 0.780 | ~2s (bf16) |

README 推荐入口：**kev-4b**（32GB Mac bf16 可跑，精度最高/体积比最佳）。注意 8b 的 OOD 准确率反而低于 4b，作者已如实标出。

对比 Jev（参考线）：kev-4b OOD 0.790 vs Jev 0.857；Brier score 0.328 vs Jev 0.211；置信度 ≥90% 时的误答率 8.2% vs Jev 3.7%。差距存在，没有隐瞒。

---

## 训练细节

- **数据**：10~13 个公开数据集（Banking77、AG News、MNLI、BoolQ、SST-5 等），每源 1000 条 × 2 epochs；另加 896 条程序化策略记录和 1680 条规则结构数据
- **最重要的配方发现**：学习率 **5e-5**，而非默认 2e-4。用默认值导致知识任务回归约 4.7pp
- **未使用 Jev 的任何输出**——完全从公开标注数据独立训练
- **成本**：0.5B 单次试验约 $0.15~$0.30（Modal H100）；M5 本地约 1h45m

---

## 不足之处（文档已明写，不是挖出来的）

**1. OOD 准确率落后 Jev 6~7pp**，集中在知识（MMLU）、释义（PAWS）、日期计算三类。

**2. 逻辑规则推理未达发布门槛**。预设标准是 held-out 组合规则 both-correct ≥ 0.70 每个 seed——实测 3 个 seed 只有 1 个过线（0.62~0.73 之间）。作者没有降低标准，如实写在 README。

**3. 上下文窗口 8192 token**，训练时实际只用 384/1024 token——Jev 约 32k，差距明显。

**4. 校准不迁移**：域内拟合的 temperature 到 OOD 场景会退化，域外 ECE 变差。

**5. 选项顺序敏感**：argmax 答案有 7.4% 概率随选项排列顺序改变——同一个问题换个选项顺序可能给不同答案。

**6. 无跨请求 KV 缓存**：每次请求都做密集 per-sample masking，无法批处理复用。

**7. kev-4b 需约 16GB RAM**（fp32 全精度）；bf16 在 32GB Mac 上可跑。

**8. Research preview 状态**——模型仓库明确标注，不建议生产使用。

---

## 本地运行

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve

# 启动服务
KEV_DTYPE=bf16 uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-4b --port 8009
```

请求格式（兼容 TypeSafe SDK，改 `base_url` 即可替换）：

```json
POST /v1/systemone
{
  "state": "用户评价：等了两小时，菜还没上。服务态度很差。",
  "model": "kev-latest",
  "questions": {
    "sentiment": {
      "type": "choice",
      "instructions": "这条评价的情感倾向？",
      "criteria": {
        "positive": "表达满意或赞赏",
        "negative": "表达不满或批评",
        "neutral": "无明显情感倾向"
      }
    },
    "urgent": {
      "type": "noul",
      "instructions": "这条评价是否需要紧急跟进？"
    }
  }
}
```

测试选项顺序一致性：`POST /v1/systemone/permute`（自动排列全组合，报告最大概率漂移）。

---

## 横向对比

| | Kev-4b | Jev | GPT-4o（zero-shot） |
|--|--------|-----|---------------------|
| OOD 准确率 | 0.790 | 0.857 | 未披露（定制任务） |
| 推理方式 | logprob | logprob | 文字生成 |
| 本地可跑 | ✓ | ✗（SaaS） | ✗ |
| Context | 8k | ~32k | 128k |
| 许可 | Apache-2.0 | 商业 SaaS | 商业 API |
| 价格 | 免费 | $0.042/1k input token | 按用量 |

---

## 怎么看这件事

Kev 是目前公开的、最接近 Jev 思路的本地实现：块因果掩码打包多问题、不生成 token、直接读 logprob。主要代价是上下文窗口（8k vs 32k）和 OOD 准确率（差约 6pp）。对于**需要本地/离线、对延迟和成本敏感、场景中的文档不超 8k token**的决策任务，kev-4b 是一个真实可用的选项。对于需要长文档或更高精度的场景，差距仍然显著。

学习率 5e-5 的发现值得收藏——用了错误的默认值要掉 4~5pp，Kev 没把这个藏在日志里，写进了 README。

> 开源代码与模型仅供学习研究，勿直接用于生产决策系统。

---

<!--EN-->

## Kev: Jared Palmer's Open-Source Local Decision Model

[Kev](https://github.com/jaredpalmer/kev) by Jared Palmer (creator of Formik and Turborepo) is an open-source local decision model. It doesn't generate text — you give it a document and a batch of questions, and it returns calibrated probability distributions for all questions in a single forward pass. The architecture was inspired by TypeSafe's proprietary Jev, which researcher Archer Hume had reverse-engineered from first principles.

**Repo**: github.com/jaredpalmer/kev | **License**: Apache-2.0 | **Stars**: 606

---

### Core Design: Encode Once, Branch Many

Kev uses **block-causal masking** to pack the document and all questions into one sequence. Each question branch can see the document but not sibling questions. The document is encoded once; all question branches fan out concurrently:

```
[Document] → [Q1 branch] → P(option_A) / P(option_B)
           → [Q2 branch] → P(yes) / P(no)
           → [Q3 branch] → expected-value score
```

No decoding, no token generation — just softmax over answer option logits. Packed vs. separate requests agree to max 4e-6 delta. Throughput is 2× faster with verified isolation.

---

### Three Question Types

| Type | Use | Output |
|------|-----|--------|
| `noul` | Binary yes/no | P(yes) / P(no) |
| `choice` | 2–255 discrete options | Confidence per option |
| `score` | Ordered levels (strong/medium/weak) | Expected value + per-level probabilities |

---

### Four Model Variants

| Model | Base | OOD Accuracy (test) | M5 Latency |
|-------|------|---------------------|-----------|
| kev-0.5b | Qwen2.5-0.5B | 0.575 | ~160ms fp32 |
| kev-0.6b | Qwen3-0.6B-Base | 0.631 | — |
| **kev-4b** | Qwen3-4B-Base | **0.806** | ~277ms bf16 |
| kev-8b | Qwen3-8B-Base | 0.780 | ~2s bf16 |

README recommends starting with **kev-4b** (best accuracy-per-byte, fits a 32GB Mac in bf16). Note that kev-8b's OOD accuracy is actually lower than kev-4b — this is documented honestly.

vs. Jev: kev-4b OOD 0.790 vs Jev 0.857; Brier score 0.328 vs Jev 0.211; high-confidence error rate 8.2% vs Jev 3.7%. The gap is real and unambiguous.

---

### Limitations (documented, not hidden)

1. **6–7pp OOD accuracy gap vs Jev**, concentrated in knowledge (MMLU), paraphrase (PAWS), and date arithmetic.

2. **Rule reasoning release threshold not consistently met.** Predeclared screen: held-out logical composition both-correct ≥ 0.70 every seed. Actual result: only 1 of 3 seeds passes (range 0.62–0.73). Author kept the threshold rather than lowering it.

3. **8,192-token context window** (trained at 384/1,024 tokens). Jev supports ~32k.

4. **Calibration doesn't transfer OOD.** In-domain temperature scaling degrades out-of-domain.

5. **7.4% option-order sensitivity** — argmax answer can flip depending on how choices are ordered in the request.

6. **No cross-request KV cache reuse** — dense per-sample masking on every request.

7. **Research preview** status — not production-ready.

---

### Training Key Finding

The most important recipe discovery: learning rate **5e-5**, not the default **2e-4**. Using the default caused ~4.7pp regression on knowledge tasks. No Jev outputs were used in training — the model was trained entirely on public labeled datasets.

---

### Quick Start

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve
KEV_DTYPE=bf16 uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-4b --port 8009
```

TypeSafe SDK compatible — override `base_url` to use as a local Jev drop-in.

---

### Bottom Line

Kev is the closest public implementation of the Jev decision-model architecture: block-causal masking for multi-question batching, logprob-only inference, no text generation. The tradeoffs are real — shorter context (8k vs 32k) and a measurable OOD accuracy gap (~6pp). For tasks that are **local/offline, cost-sensitive, and fit in 8k tokens**, kev-4b is a genuinely usable option. For longer documents or higher-stakes precision needs, the gap to Jev still matters.

> Open-source code and models for research and learning only. Not recommended for production decision systems.
