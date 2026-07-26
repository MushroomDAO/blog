---
title: "934MB 适配器，27B 基座，95% 代码通过率——BTL-3 的 LoRA 炼成路"
description: "BTL-3 用 rank-32 LoRA 在 Qwen3.6-27B 上做强化学习后训练，用不到 1GB 的适配器权重，在编程智能体和结构化工具调用上打出 88.5% BFCL / 95% HumanEval 的成绩。本文深入 adapter_config.json 和训练设计，拆解 LoRA 怎么让一个 27B 模型变成专职 Agent。"
pubDate: 2026-07-26
heroImage: "../../assets/images/btl-3-lora-adapter-qwen-programming-agent-tool-calling-training-banner.jpg"
category: "Research"
tags: ["LoRA", "PEFT", "Agent", "Tool Use", "Fine-tuning", "Qwen", "RL"]
---

2026 年，全参数微调 27B 模型需要 4×A100 跑几天。BTL-3 的做法是：**只训练 934MB 的 LoRA 适配器**，基座权重冻住，强化学习在上面跑了 13 轮迭代，最终在编程智能体基准上跑出了 95.12% HumanEval pass@1 和 88.5% BFCL v4 AST。

这篇文章的核心问题只有一个：LoRA 在这里具体做了什么？

---

## LoRA 的数学基础

全参数微调的直觉是：把预训练权重矩阵 W₀ 更新成 W₀ + ΔW。问题是 ΔW 和 W₀ 同维度，27B 模型的 ΔW 就要存 27B 个浮点数。

LoRA 的假设是：**ΔW 的本征维度远低于 d**。因此用两个低秩矩阵近似：

```
ΔW = B × A

其中 A ∈ ℝ^(r×k),  B ∈ ℝ^(d×r),  r ≪ min(d, k)
```

推理时，前向传播变成：

```
h = W₀x + (B × A)x × (α / r)
```

`α / r` 是缩放系数。训练开始时，B 全零初始化（保证 ΔW = 0），A 用标准 Kaiming 随机初始化。基座权重 W₀ 全程冻结，梯度只流过 A 和 B。

**关键结论**：不管 d 有多大，参数量只和 r 成正比。

---

## BTL-3 的 LoRA 配置

从 `adapter_config.json` 直接读数：

```json
{
  "peft_type": "LORA",
  "r": 32,
  "lora_alpha": 64,
  "lora_dropout": 0.0,
  "bias": "none",
  "use_dora": false,
  "use_rslora": false,
  "task_type": "CAUSAL_LM",
  "base_model_name_or_path": "Qwen/Qwen3.6-27B"
}
```

**rank = 32，alpha = 64**：缩放因子 α/r = 2.0。这是一个偏大的 alpha 值——相对于常见的 α = r（缩放 = 1.0），这里让适配器的更新幅度翻倍。在 RL 训练中，较大的 alpha 可以帮助模型更快收敛到目标行为。

**dropout = 0.0**：无正则化。适配器权重在训练时完整保留，不随机置零。这暗示训练数据足够高质量，无需依赖 dropout 来防过拟合。

**目标模块（target_modules）** 覆盖了所有注意力投影和 FFN 层：

- Attention：`q_proj`, `k_proj`, `v_proj`, `o_proj`
- FFN（MoE 门控）：`gate_proj`, `up_proj`, `down_proj`

即：每个 Transformer 层里有 7 个矩阵接入 LoRA。Qwen3.6-27B 有 64 层，共 **64 × 7 = 448 个 LoRA 模块**。

**适配器总参数量估算**：

Qwen3.6-27B 的隐藏维度 d_model ≈ 5120（推测），FFN 中间维度 ≈ 13824。
每个 LoRA 模块的参数 = r × d_in + r × d_out = 2 × r × d。
最终适配器文件 934MB，以 BF16 存储约等于 934M / 2 = **4.67 亿参数**——这不到基座参数量的 2%。

---

## 强化学习训练：RL-0013

BTL-3 的 checkpoint 名称是 **RL-0013**。"RL" 明确表明训练方法是强化学习，"0013" 是第 13 次迭代的检查点。

这与 SFT（监督微调）的路径不同：

| 方法 | 信号来源 | 适合什么 |
|---|---|---|
| SFT | 人工标注的正确答案 | 对齐输出格式、风格 |
| RL | 奖励函数（代码执行、测试通过、工具调用合规性） | 智能体行为、工具使用判断 |

对于编程智能体来说，RL 有天然优势：

1. **代码是可执行的**——测试通过/失败是明确的二元奖励信号，不需要人工打分。
2. **工具调用有结构约束**——格式错误可以直接作为惩罚信号。
3. **RL 天然优化"何时不调用工具"**——BTL-3 在 BFCL irrelevance 上达到 91.2%，说明模型学会了拒绝不必要的工具调用，这正是 RL 奖励设计的结果。

训练时的最大序列长度设为 **65,536 tokens**——覆盖了多轮 Agent 交互的完整上下文，但比推理时的 262,144 短，这是计算成本的取舍。

---

## 为什么 rank-32 够用？

从理论上说，LoRA 的 rank 决定了适配器能表达的"变化空间"大小：rank-32 意味着 ΔW 最多有 32 个独立方向。

在实践里，有几个原因让 32 对于 Agent 微调足够：

**1. 基座能力已经很强**：Qwen3.6-27B 本身已具备代码生成和推理能力，微调的目标不是从零学会写代码，而是**校准行为偏好**——更稳定的工具调用格式、更少的冗余动作、更好的停止条件判断。这类偏好调整的内在维度低。

**2. RL 信号聚焦**：强化学习的奖励函数通常围绕几个核心维度（代码正确性、工具格式、任务完成），这些目标的梯度方向集中，rank-32 的子空间足以容纳。

**3. 对比数据佐证**：适配器文件 934MB，若 rank 加倍到 64，适配器也只会翻倍到 ~1.9GB，对总体成本影响有限。Bad Theory Labs 选择 32 而不是 64 或 128，说明他们在实验中发现 rank 增大后收益递减。

---

## 基准结果解读

| 评测 | 得分 | 备注 |
|---|---:|---|
| BFCL v4 AST | **88.5%** (1097/1240) | 完整官方集，含并行调用 |
| HumanEval | **95.12%** (156/164) | pass@1，thinking mode |
| LiveCodeBench v6 | **88.1%** (170/193) | thinking mode |
| BigCodeBench-Hard | 26.35% | 严格测试，业界普遍偏低 |
| BFCL 不调用准确率 | **91.2%** | 识别不需要工具调用的场景 |

BFCL（Berkeley Function Calling Leaderboard）按调用复杂度分类：

- Simple（单工具）: 93.2%
- Multiple（顺序多工具）: 95.5%
- Parallel（并行调用）: 87.0%
- Parallel-multiple: 70.0%

Parallel-multiple 得分最低（70%），符合预期——并行多工具调用需要模型同时规划多条执行路径，是结构化工具调用里最难的场景。

---

## 两种部署形态

BTL-3 的发布策略很有意思——同时提供两种形态：

**BTL-3（PEFT 适配器）**：934MB，需要配合 Qwen3.6-27B 基座。适合服务器部署，保留最高精度。

**BTL-3 Compact（GGUF）**：8.39GB，独立文件，无需基座。采用混合量化（AVQ2 + affine INT4 + 精度岛），在 Mac 上可直接运行。在内部 90 轮工具调用测试中保留了 92.2% 的行为——单次、并行、顺序调用和拒绝行为全部 100% 保留，损失集中在更复杂的 parallel-multiple 场景。

对于本地推理，Compact 是更实用的选择：8.39GB 比同等参数量的 FP16 8B 模型还小。

---

## 使用方式

### Transformers（完整精度）

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_id = "Qwen/Qwen3.6-27B"
base_revision = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
adapter_id = "badtheorylabs/BTL-3"

tokenizer = AutoTokenizer.from_pretrained(adapter_id)
base = AutoModelForCausalLM.from_pretrained(
    base_id,
    revision=base_revision,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
model = PeftModel.from_pretrained(base, adapter_id)
```

### vLLM（生产部署，支持动态 LoRA 加载）

```bash
vllm serve Qwen/Qwen3.6-27B \
  --revision 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 \
  --served-model-name BTL-3 \
  --enable-lora \
  --max-lora-rank 32 \
  --lora-modules BTL-3=/path/to/BTL-3 \
  --lora-target-modules \
    q_proj k_proj v_proj o_proj \
    gate_proj up_proj down_proj \
  --reasoning-parser qwen3 \
  --max-model-len 32768
```

---

## 一个值得留意的信号

到 2026 年，LLM 基座的能力密度已经很高。对于特定领域任务，"用 LoRA 在强化学习信号上做几轮迭代"的成本远低于从头预训练或全参数微调，但能带来显著的行为对齐效果。

BTL-3 用 934MB 的适配器、13 轮 RL 迭代，让一个通用 27B 模型在编程智能体任务上达到了接近专用模型的水准——这不是偶然，而是 LoRA + RL 组合在 Agent 领域的标准化路径正在成熟。

---

**模型地址**：[badtheorylabs/BTL-3](https://huggingface.co/badtheorylabs/BTL-3)  
**Compact 版本**：[badtheorylabs/BTL-3-Compact](https://huggingface.co/badtheorylabs/BTL-3-Compact)

<!--EN-->

## 934 MB Adapter, 27B Base, 95% Code Pass Rate — How BTL-3 Was Built with LoRA

In 2026, full-parameter fine-tuning of a 27B model requires 4×A100 GPUs running for days. BTL-3 took a different path: **train only a 934 MB LoRA adapter**, freeze the base weights, run reinforcement learning for 13 checkpoint iterations, and ship a programming agent that scores 95.12% HumanEval pass@1 and 88.5% BFCL v4 AST.

This article has one core question: what exactly does LoRA do here?

---

## The Math Behind LoRA

Standard fine-tuning updates a pretrained weight matrix W₀ to W₀ + ΔW. The problem: ΔW is the same dimension as W₀, so storing it for a 27B model costs as much as the model itself.

LoRA's hypothesis: **the intrinsic dimensionality of ΔW is far lower than d**. So approximate it with two low-rank matrices:

```
ΔW = B × A

where A ∈ ℝ^(r×k),  B ∈ ℝ^(d×r),  r ≪ min(d, k)
```

The forward pass becomes:

```
h = W₀x + (B × A)x × (α / r)
```

`α / r` is the scaling factor. At initialization, B is zero (ensuring ΔW = 0), A uses standard Kaiming random init. W₀ is frozen throughout — gradients only flow through A and B.

**Key insight**: parameter count scales with r alone, regardless of d.

---

## BTL-3's LoRA Configuration

Reading directly from `adapter_config.json`:

```json
{
  "peft_type": "LORA",
  "r": 32,
  "lora_alpha": 64,
  "lora_dropout": 0.0,
  "bias": "none",
  "use_dora": false,
  "use_rslora": false,
  "task_type": "CAUSAL_LM",
  "base_model_name_or_path": "Qwen/Qwen3.6-27B"
}
```

**rank = 32, alpha = 64**: scaling factor α/r = 2.0. This is an above-average alpha — compared to the common α = r (scaling = 1.0), this doubles the adapter's update magnitude. In RL training, larger alpha can help the model converge faster toward target behavior.

**dropout = 0.0**: no regularization. Adapter weights are fully preserved during training, suggesting the training data was high quality enough to avoid overfitting.

**Target modules** cover all attention projections and FFN layers:

- Attention: `q_proj`, `k_proj`, `v_proj`, `o_proj`
- FFN (MoE gating): `gate_proj`, `up_proj`, `down_proj`

That's 7 LoRA modules per transformer layer. Qwen3.6-27B has 64 layers: **64 × 7 = 448 total LoRA modules**.

**Adapter parameter estimate**: The 934 MB adapter file stored in BF16 ≈ 934M / 2 = **~467M parameters** — less than 2% of the 27B base.

---

## Reinforcement Learning Training: RL-0013

The checkpoint name **RL-0013** makes the training method explicit: reinforcement learning, 13th iteration checkpoint.

This differs from supervised fine-tuning:

| Method | Signal | Best for |
|---|---|---|
| SFT | Human-labeled correct answers | Output format alignment |
| RL | Reward functions (code execution, test pass, tool compliance) | Agent behavior, tool-use judgment |

RL has a natural advantage for programming agents:

1. **Code is executable** — test pass/fail is an unambiguous binary reward, no human scoring needed.
2. **Tool calls have structural constraints** — malformed formats are direct penalty signals.
3. **RL naturally optimizes "when not to call a tool"** — BTL-3's 91.2% BFCL irrelevance score shows the model learned to decline unnecessary tool calls, which is exactly what RL reward shaping produces.

Maximum RL sequence length was **65,536 tokens** — covering complete multi-turn agent interactions, but shorter than inference's 262,144, a deliberate compute cost tradeoff.

---

## Why Rank-32 Is Enough

In theory, LoRA rank determines the "change space" size — rank-32 means ΔW has at most 32 independent directions. In practice, several factors make 32 sufficient for agent fine-tuning:

**1. Strong base capability**: Qwen3.6-27B already knows how to write code. Fine-tuning isn't teaching it to code from scratch — it's **calibrating behavioral preferences**: more stable tool call formats, fewer redundant actions, better stopping conditions. These preference adjustments have inherently low intrinsic dimensionality.

**2. Focused RL signals**: RL reward functions typically target a few core dimensions (code correctness, tool format compliance, task completion). These gradients are concentrated — rank-32's subspace is sufficient.

**3. Empirical evidence**: Bad Theory Labs chose rank-32 rather than 64 or 128, implying they found diminishing returns from increasing rank in experiments.

---

## Benchmark Results

| Evaluation | Score | Protocol |
|---|---:|---|
| BFCL v4 AST | **88.5%** (1097/1240) | Full official set, including parallel calls |
| HumanEval | **95.12%** (156/164) | pass@1, thinking mode |
| LiveCodeBench v6 | **88.1%** (170/193) | thinking mode |
| BigCodeBench-Hard | 26.35% | Strict; industry-wide scores are low |
| BFCL Irrelevance | **91.2%** | Recognizing when not to call a tool |

BFCL by complexity:

- Simple (single-tool): 93.2%
- Multiple (sequential multi-tool): 95.5%
- Parallel: 87.0%
- Parallel-multiple: 70.0%

Parallel-multiple is the lowest, as expected — it requires simultaneously planning multiple parallel execution paths, the hardest scenario in structured tool calling.

---

## Two Deployment Formats

BTL-3 ships two formats simultaneously:

**BTL-3 (PEFT adapter)**: 934 MB, requires Qwen3.6-27B base. For server deployment, maximum quality.

**BTL-3 Compact (GGUF)**: 8.39 GB, standalone, no base model needed. Uses mixed quantization (AVQ2 + affine INT4 + precision islands), runs directly on Mac. In an internal 90-turn tool-contract gate, it retained 92.2% of full-precision behaviors — single-call, parallel, sequential, and abstention retention were all 100%.

For local inference, Compact is the practical choice: 8.39 GB is smaller than an 8B model in FP16.

---

## A Signal Worth Noting

By 2026, the capability density of LLM bases is very high. For domain-specific tasks, "run a few RL iterations on LoRA" costs far less than pretraining from scratch or full fine-tuning, yet delivers significant behavioral alignment.

BTL-3 used a 934 MB adapter and 13 RL iterations to bring a general-purpose 27B model to near-specialist-model performance on programming agent tasks. This isn't coincidental — the LoRA + RL combination is becoming the standard path for agent specialization.

**Model**: [badtheorylabs/BTL-3](https://huggingface.co/badtheorylabs/BTL-3)  
**Compact edition**: [badtheorylabs/BTL-3-Compact](https://huggingface.co/badtheorylabs/BTL-3-Compact)
