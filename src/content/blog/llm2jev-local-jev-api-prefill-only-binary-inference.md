---
title: "LLM2Jev：用任意本地 LLM 克隆 Jev 的 /v1/systemone——Prefill-Only 二值推理拆解"
titleEn: "LLM2Jev: Clone Jev's /v1/systemone with Any Local LLM — Prefill-Only Binary Inference Teardown"
description: "Yinsongxu/LLM2Jev，125 stars，Apache 2.0。3 天新项目，把任意 HuggingFace 因果语言模型变成兼容 Jev /v1/systemone API 的本地决策引擎。核心手法：Prefill-Only 二值推理——只读 yes/no 的下一 token logit，不解码、不 JSON 解析。支持 Choice/Score/Noul 三类结构化答案，staged 模式对长上下文 KV Cache 前缀复用，可达 4.9× 加速。SGLang 后端仅 Linux，Transformers 后端跨平台。"
descriptionEn: "Yinsongxu/LLM2Jev — 125 stars, Apache 2.0. A 3-day-old project that turns any HuggingFace causal language model into a local Jev-compatible /v1/systemone decision engine. Core technique: prefill-only binary inference — reads only yes/no next-token logits, no decoding, no JSON parsing. Supports Choice/Score/Noul structured answers. Staged mode reuses KV cache prefix for long contexts, up to 4.9× speedup. SGLang backend Linux-only; Transformers backend cross-platform."
pubDate: 2026-09-22
heroImage: "../../assets/images/llm2jev-local-jev-api-prefill-only-binary-inference-banner.jpg"
category: "Tech-Experiment"
tags: ["jev", "llm", "decision-model", "open-source", "sglang", "local-ai", "inference"]
lang: zh-CN
---

TypeSafe AI 的 Jev System One 上线 7 天，本地复刻版就出来了。`Yinsongxu/LLM2Jev` 125 stars，Apache 2.0，3 天前创建。

**GitHub**：github.com/Yinsongxu/LLM2Jev | **Stars**：125 | **License**：Apache 2.0 | **Python**：3.10+

---

## Jev 是什么，为什么有人要复刻它

Jev 是 TypeSafe AI（Diogo Almeida 创立，2026 年 9 月 15 日发布，$40M 融资）的 System One 模型——一个专为**结构化决策**设计的非自回归引擎。

它不生成文字，只返回类型化的答案：从一组选项中选一个（Choice）、在量表上评分（Score）、给出是/否概率（Noul）。

典型用途：客服工单路由、内容审核、对话意图分类、产品推荐决策——任何"给我一个结构化判断"的场景。比用 LLM 生成 JSON 快 40×–200×，且不会 JSON 格式出错。

商业 Jev 的问题：云端收费（$0.042/M tokens），数据不出本机、私有部署场景用不了。

LLM2Jev 的解法：用任意本地 HuggingFace LLM，实现同一套 `/v1/systemone` API。

---

## 核心机制：Prefill-Only 二值推理

这是 LLM2Jev 的技术关键。

传统用 LLM 做结构化输出的方式：提示词要求输出 JSON → token-by-token 解码 → 解析 JSON（可能格式错误、可能幻觉）。

LLM2Jev 的方式：

```
1. 把每个判断问题拆成独立的是/否候选判断
2. 每个候选构造一个 prompt 发给 LLM
3. 只读下一个 token 位置上 "yes" 和 "no" 的 logit
4. 在代码里算概率：q = exp(yes_logit) / (exp(yes_logit) + exp(no_logit))
5. 从概率分值组装出 Choice/Score/Noul 类型的答案
```

不解码、不生成 token、不解析 JSON。整个推理过程就是一次前向传播到第一个输出位置，读 logit，结束。

**置信度计算**（n 个候选时）：
```
confidence = (n × p_max - 1) / (n - 1)，clamp 到 [0, 1]
```

---

## 三类问题类型

### Choice — 从一组无序选项中选一个

```python
from llm2jev import JevClient, JevRequest, Choice

client = JevClient(base_url="http://localhost:30000")

request = JevRequest(
    state="客户反馈：收到的商品颜色不对，要求换货。",
    model="qwen3-1.7b",
    questions={
        "category": Choice(
            criteria={
                "shipping": "配送问题（丢件/延误/损坏）",
                "product":  "商品问题（颜色/尺寸/质量）",
                "payment":  "支付问题（退款/账单）",
                "other":    "其他",
            },
        )
    }
)

result = client.evaluate(request)
print(result.answers["category"].value)  # → "product"
print(result.answers["category"].confidence)  # → 0.92
```

### Score — 在有序量表上评分（2–10 级）

```python
questions={
    "urgency": Score(
        criteria=[
            "Low: 一般咨询，可 48h 内处理",
            "Medium: 客户较不满，需 24h 内处理",
            "High: 客户激动要求立即处理",
        ],
    )
}
```

### Noul — 是/否概率

```python
questions={
    "is_delivery_issue": Noul(
        instructions="这是一个配送相关的问题吗？",
    )
}
# result.answers["is_delivery_issue"].probability → 0.07
```

一个 JevRequest 可以同时包含多种类型的问题，一次请求全部返回。

---

## 5 步上手

```bash
# 1. 克隆仓库
git clone https://github.com/Yinsongxu/LLM2Jev
cd LLM2Jev

# 2. 安装依赖（SGLang 后端，Linux）
uv sync --extra sglang
# 或跨平台 Transformers 后端
uv sync --extra transformers

# 3. 启动本地推理服务
llm2jev-serve \
  --model-path /path/to/qwen3-1.7b \
  --served-model-name qwen3-1.7b \
  --host 0.0.0.0 --port 30000 \
  --submission staged    # 长上下文场景推荐

# 4. 写 JevRequest，调用 .evaluate()
# （见上面 Python 示例）

# 5. 或直接 HTTP 调用 /v1/systemone
curl -X POST http://localhost:30000/v1/systemone \
  -H "Content-Type: application/json" \
  -d '{
    "state": "客户反馈：收到的商品颜色不对。",
    "model": "qwen3-1.7b",
    "questions": {
      "category": {
        "type": "choice",
        "criteria": {"product": "商品问题", "shipping": "配送问题"}
      }
    }
  }'
```

---

## SGLang staged 模式：KV Cache 前缀复用

`--submission staged` 是 LLM2Jev 的性能关键。

一个 JevRequest 有多个候选（比如 Choice 有 4 个选项 = 4 个独立的是/否 prompt）。这 4 个 prompt 共享完全相同的前缀：`state + instructions`。

`staged` 模式利用 SGLang 的 Radix Cache，这个共享前缀只计算一次，然后对每个候选的尾部分别做 prefill。`all` 模式是把所有候选 prompt 打包一次批量发，但每个都独立走完整前向传播。

**实测性能**（Qwen3-1.7B / RTX 5090 / BF16 / SGLang 0.5.20）：

| 场景 | all 模式 | staged 模式 | 赢家 |
|------|---------|------------|------|
| 3 问题 9 候选（基线） | 84.00ms | 36.43ms | staged **2.3×** |
| 4 问题 8 候选 + 长上下文 | 611.77ms | 125.15ms | staged **4.9×** |
| 混合问题类型 9 候选 | 93.09ms | 40.88ms | staged **2.3×** |
| 1 问题 2 候选（短输入） | 11.49ms | 19.11ms | all **1.7×** |
| 长上下文 + 热缓存 | 25.88ms | 50.79ms | all **2.0×** |

结论：上下文越长、候选越多，`staged` 优势越大；短输入或缓存已热，`all` 反而更快。

---

## 两个后端的选择

| 特性 | SGLang 后端 | Transformers 后端 |
|------|------------|------------------|
| 安装 | `uv sync --extra sglang` | `uv sync --extra transformers` |
| 操作系统 | **仅 Linux** | 跨平台（Mac/Windows/Linux） |
| staged 模式 | ✅ 支持（Radix Cache） | ❌ 不支持 |
| GPU | NVIDIA CUDA | CUDA 可选（可跑 CPU） |
| 测试版本 | SGLang 0.5.20 + Triton | transformers>=4.51 |

SGLang 版本限制（不能组合使用）：
- 不支持 `--tokenizer-worker-num > 1`
- 不支持 `--grpc-mode`
- 不支持 `--encoder-only`
- 不支持 `--use-ray`

---

## Jev 生态：三条路径对比

Jev 出现不到两周，开源生态已经有三条复刻路径：

| 项目 | 方法 | 特点 |
|------|------|------|
| **Jev（TypeSafe AI）** | RLCD 训练，非自回归，专用校准目标 | 原版，云端收费，40×–200× 快 |
| **Kev** | 在 Qwen3.5（0.5B–9B）上加 LoRA + 训练 readout head，块因果掩码 | 小模型，一次前向传播多问题，需要训练 |
| **LLM2Jev** | 任意 stock LLM + logit 提取，无需训练 | 零训练，带啥模型用啥模型 |

LLM2Jev 和真正的 Jev 架构差异：Jev 很可能用了专为决策校准训练的 readout head（`z = Wh + b`）和块因果掩码，让所有候选在一次前向传播内同时评分。LLM2Jev 的 yes/no logit 读法是合理的工程近似，但不是同一个机制——这也是为什么仓库明确声明"not affiliated with TypeSafe"。

---

## 硬件配置要求

**SGLang 后端（推荐）**：
- OS：Linux（硬性要求）
- GPU：NVIDIA CUDA（任何 SGLang 支持的卡）
- 测试配置：RTX 5090 + Qwen3-1.7B BF16
- RAM：视模型大小，Qwen3-1.7B BF16 约需 4GB 显存

**Transformers 后端（跨平台降级）**：
- OS：Linux / macOS / Windows
- GPU：可选（CPU 可运行，速度慢）
- 依赖：torch>=2.0 + transformers>=4.51 + pillow>=10

**多模态支持**：`state` 和 `instructions` 字段支持图像内容（SGLang 和 Transformers 后端均支持）。

---

## 不足之处

**1. 3 天新项目**：125 stars，11 forks，工程成熟度未经验证，API 可能变动。

**2. SGLang 仅限 Linux**：Mac 用户只能用 Transformers 后端，失去 staged 模式和 Radix Cache。

**3. 架构近似，非等价**：yes/no logit 读法不等同于 Jev 的训练校准 readout head，精度特性不同。特别是 IIA 独立无关选项——真实 Jev 有 −0.28 log-odds 的跨选项依赖效应，LLM2Jev 的每候选独立 prompt 设计不能还原这个特性。

**4. 依赖 OpenAI SDK**（内部用途）：`openai>=2.6.1` 是强依赖，可能引起混淆。

**5. 无官方文档站**：只有 README 和 `docs/` 目录，没有搜索引擎可查的文档。

---

## 怎么看这个项目

LLM2Jev 的价值在于：**零训练门槛地在本地跑一套 Jev 兼容 API**。

你不需要等 TypeSafe AI 开放私有部署，也不需要像 Kev 那样去做 LoRA 训练。带什么模型，直接 `uv sync`、`llm2jev-serve`、写 `JevRequest`，5 分钟内就有一个能用的本地结构化决策服务。

staged 模式的 KV Cache 前缀复用是真实的工程贡献，4.9× 的长上下文加速不是宣传数字——这个优化思路适用于任何"大量候选共享前缀"的批量推理场景，不仅限于 Jev 格式。

适合场景：私有数据的决策分类任务、本地部署的内容审核、多候选路由场景的结构化判断——特别是不想把数据发给云端、或者需要定制模型的情况。

> 代码 Apache 2.0，与 TypeSafe AI / Jev 无从属关系，仅供学习研究参考。

---

<!--EN-->

## LLM2Jev: Clone Jev's /v1/systemone API with Any Local LLM

`Yinsongxu/LLM2Jev` (125 stars, Apache 2.0) appeared 3 days after TypeSafe AI launched Jev System One. It turns any HuggingFace causal LLM into a local `/v1/systemone` decision engine — no fine-tuning required.

**GitHub**: github.com/Yinsongxu/LLM2Jev | **Stars**: 125 | **License**: Apache 2.0

---

### What Jev Is

TypeSafe AI's Jev (founded by Diogo Almeida, OpenAI RLHF co-inventor; launched Sept 15, 2026; $40M funding) is a non-autoregressive decision model that returns typed answers — not text. It's 40×–200× faster than LLMs on structured decisions (routing, classification, scoring) and never produces malformed JSON.

Commercial Jev is cloud-only at $0.042/M tokens. LLM2Jev provides the same API locally.

---

### Core Technique: Prefill-Only Binary Inference

Instead of generating JSON (token-by-token decoding + parsing with hallucination risk), LLM2Jev:

1. Decomposes each question into independent yes/no candidate judgments
2. Submits each candidate as a separate prompt to the LLM
3. Reads only the `yes` and `no` next-token logits — no decoding
4. Computes `q = exp(yes_logit) / (exp(yes_logit) + exp(no_logit))` in code
5. Assembles typed Choice/Score/Noul answers from probability scores

One forward pass to the first output position, read logits, done.

**Confidence formula** (n candidates): `confidence = (n × p_max - 1) / (n - 1)`, clamped to [0, 1].

---

### Three Question Types

**Choice** — select one from an unordered option set:
```python
Choice(criteria={"product": "Product issue (color/size/quality)", "shipping": "Delivery issue"})
```

**Score** — rate on an ordered scale (2–10 levels):
```python
Score(criteria=["Low: routine inquiry", "Medium: dissatisfied", "High: urgent complaint"])
```

**Noul** — binary yes/no probability:
```python
Noul(instructions="Is this a delivery-related issue?")
# → result.answers["q"].probability = 0.07
```

Mix all three in a single JevRequest; all answers return in one call.

---

### 5-Step Quickstart

```bash
# 1. Clone
git clone https://github.com/Yinsongxu/LLM2Jev && cd LLM2Jev

# 2. Install (SGLang on Linux, or Transformers cross-platform)
uv sync --extra sglang       # Linux + NVIDIA
uv sync --extra transformers # cross-platform fallback

# 3. Start inference server
llm2jev-serve --model-path /path/to/model \
  --served-model-name my-model --port 30000 \
  --submission staged         # recommended for long context

# 4. Write JevRequest and call .evaluate()
result = JevClient("http://localhost:30000").evaluate(request)

# 5. Or HTTP POST to /v1/systemone directly
```

---

### staged Mode: KV Cache Prefix Reuse

A JevRequest with N candidates (e.g., a 4-option Choice = 4 yes/no prompts) has the same `state + instructions` prefix across all candidates.

`staged` mode uses SGLang's Radix Cache: the shared prefix is computed once, then each candidate's suffix runs separately. `all` mode batches all candidates but each runs the full forward pass.

**Benchmarks** (Qwen3-1.7B / RTX 5090 / BF16 / SGLang 0.5.20, 30-run median):

| Scenario | `all` | `staged` | Winner |
|----------|-------|----------|--------|
| 3 questions, 9 candidates | 84.00ms | 36.43ms | staged **2.3×** |
| 4 questions + long context | 611.77ms | 125.15ms | staged **4.9×** |
| Mixed types, 9 candidates | 93.09ms | 40.88ms | staged **2.3×** |
| 1 question, 2 candidates (short) | 11.49ms | 19.11ms | all **1.7×** |
| Long context + warm cache | 25.88ms | 50.79ms | all **2.0×** |

`staged` wins on long context with cold cache; `all` wins on short inputs or hot cache.

---

### Hardware Requirements

**SGLang backend (recommended):**
- Linux only (hard requirement)
- NVIDIA CUDA GPU required
- Tested: RTX 5090 + Qwen3-1.7B BF16 (~4GB VRAM for 1.7B)
- SGLang 0.5.20 + Triton attention

**Transformers backend (cross-platform):**
- Linux / macOS / Windows
- GPU optional (CPU fallback available)
- Requires: torch≥2.0, transformers≥4.51, pillow≥10
- No staged mode (no Radix Cache)

Both backends support multimodal `state` and `instructions` (image content).

---

### Jev Ecosystem: Three Local Approaches

| Project | Approach | Key difference |
|---------|----------|----------------|
| **Jev (TypeSafe AI)** | RLCD-trained, non-autoregressive, calibration objective | Original, cloud-only |
| **Kev** | LoRA + trained readout head on Qwen3.5 (0.5B–9B), block-causal mask | Small model, all questions in one forward pass, requires training |
| **LLM2Jev** | Stock LLM + logit extraction, no training | Bring any model, zero training |

LLM2Jev ≠ Jev architecture: Jev likely uses a dedicated calibration-trained readout head (`z = Wh + b`) with block-causal masking. LLM2Jev's yes/no logit method is a practical engineering approximation. Notably: real Jev exhibits −0.28 log-odds IIA violation (irrelevant option dependency), which LLM2Jev's per-candidate independent prompts cannot reproduce. Not affiliated with TypeSafe AI.

---

### Limitations

1. **3-day-old project**: API may change; engineering maturity unproven.
2. **SGLang Linux-only**: Mac users must use Transformers backend, losing staged mode.
3. **Architectural approximation**: Yes/no logit extraction ≠ trained calibration readout; IIA behavior differs from commercial Jev.
4. **No public benchmark on answer quality** — only latency benchmarks published; accuracy vs. commercial Jev unknown.
5. **No documentation site**: README and `docs/` only.

---

### Bottom Line

LLM2Jev's value is zero-training entry: bring any HuggingFace LLM, get a local Jev-compatible structured decision API in 5 minutes. The staged mode KV cache prefix reuse (4.9× speedup on long context) is a real engineering contribution applicable beyond Jev format to any "many candidates sharing a common prefix" batch inference scenario.

Best fit for: private data classification/routing tasks, local content moderation, structured multi-option decision inference — particularly when data must stay on-premises or when a custom model is needed.

> Apache 2.0. Not affiliated with TypeSafe AI or Jev. For learning and research use.
