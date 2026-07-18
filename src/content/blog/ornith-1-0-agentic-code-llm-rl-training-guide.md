---
title: "Ornith-1.0：DeepReinforce 发布的 SOTA Agentic 代码 LLM，工程师如何借鉴它训练自己的模型"
titleEn: "Ornith-1.0: DeepReinforce's SOTA Agentic Coding LLM — Engineering Guide for Training Your Own with RL"
description: "Ornith-1.0 是 DeepReinforce 发布的 SOTA Agentic 代码生成模型，9B/35B/397B 规格，SWE-bench Verified 75.6（行业顶级），采用 MoE + GatedDeltaNet 混合架构，256K 上下文，强化学习训练，支持 256K Token 上下文和视觉能力。本文从工程角度解读其核心设计，并给出如何借鉴 RL 和微调技术训练自己代码模型的实践指南。"
descriptionEn: "Ornith-1.0 is DeepReinforce's SOTA agentic code generation LLM (9B/35B/397B), achieving SWE-bench Verified 75.6. Uses hybrid MoE+GatedDeltaNet architecture, 256K context, RL training, vision capability. Engineering guide: what made Ornith-1.0 work, and how to apply the same RL+fine-tuning techniques to train your own code model."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Research"
tags: ["LLM", "强化学习", "代码生成", "Agentic", "模型训练", "MoE", "SWE-bench", "DeepReinforce"]
heroImage: "../../assets/images/ornith-1-0-agentic-code-llm-rl-training-guide-banner.jpg"
---

> **模型**: deepreinforce-ai/Ornith-1.0 系列（9B / 35B / 397B）  
> **团队**: DeepReinforce · **发布**: 2026 年  
> **HuggingFace**: deepreinforce-ai/Ornith-1.0-35B

---

## Ornith-1.0 是什么？

DeepReinforce 发布的 Agentic Code Generator LLM 系列，专门为**自主代码生成和终端操作**设计。

关键指标：
- **SWE-bench Verified: 75.6**（行业顶级，能自主修复真实 GitHub Issue）
- **Terminal-Bench 2.1: 64.2**（自主终端操作能力基准）
- **Agentic coding pass@1: 0.833**（18 个任务探针）
- **256K Token 上下文**
- **思考模型**（每次都生成 `<think>…</think>` 推理链）
- **视觉能力**（可以理解图片和代码截图）

这不是一个"能写代码"的普通 LLM，而是一个**为自主 Agent 设计的代码模型**——它能像 Claude Code 或 OpenHands 那样端到端完成真实软件工程任务。

---

## 架构亮点：混合 SSM + 注意力机制

Ornith-1.0-35B 的架构非常有意思：

```
架构类型: qwen3_5_moe（混合 MoE）
总层数: 40 层
  - 30 层 GatedDeltaNet（SSM，非 Transformer）
  - 10 层 Full Attention（标准 Transformer）
Expert 数量: 256 experts + shared expert
激活参数: A3B（约 3B 激活，35B 总参数）
上下文: 256K Token
```

**为什么要混合 SSM？**

GatedDeltaNet 是一种 State Space Model（SSM），相比 Transformer 有两个优势：
1. **推理速度更快**：SSM 的推理复杂度是 O(n) 而不是 Transformer 的 O(n²)
2. **长序列更高效**：256K context 在纯 Transformer 上代价很大，SSM 处理更高效

但 SSM 在某些需要精确全局注意力的任务上不如 Transformer，所以 Ornith 用了 30/10 的混合比例：SSM 处理局部依赖，保留 10 层全注意力处理关键的全局关系。

**MoE（混合专家）的作用**：激活参数只有 3B，总参数 35B——每次推理只用 3B 参数，但模型的"知识容量"相当于 35B。既保证速度，又保证能力。

---

## 强化学习是核心差异

从名字 "DeepReinforce" 就能看出，RL 训练是这个团队的核心技术。

Ornith-1.0 的训练方式和普通代码模型有根本区别：

### 传统代码模型训练

```
收集代码数据 → 监督学习（SFT）→ 发布
```

问题：模型学到的是"看起来像代码"的输出，而不是"能运行的代码"。

### Ornith-1.0 的 RL 训练路径

```
SFT 预训练 → RL 微调（奖励信号来自：代码是否能运行、测试是否通过）
```

**奖励信号的关键设计**：
- **通过测试** → 正向奖励
- **语法错误** → 负向奖励
- **功能正确但不优雅** → 轻微负向奖励
- **完成 Agent 任务** → 强正向奖励

这就是为什么 Ornith-1.0 在 SWE-bench 上能达到 75.6——RL 训练让它真正"理解"代码是否工作，而不只是生成看起来正确的代码。

---

## 工程师如何借鉴 Ornith-1.0 训练自己的代码模型？

### 方法一：RL 微调（推荐）

如果你有一个基础代码模型（比如 CodeLlama、DeepSeek-Coder），可以用 RL 微调来提升其 Agentic 能力：

**工具栈**：
```
基础: DeepSeek-R1-Zero 的训练方式（GRPO/PPO）
框架: veRL（字节跳动）/ TRL（HuggingFace）/ OpenRLHF
奖励函数: 代码执行结果（单元测试通过率）
硬件: 4×A100 80G 起步（7B/9B 规模），35B 规模需要 8×H100
```

**最小可行实验**：

```python
# 用 TRL 框架做代码 RL 微调的概念代码
from trl import PPOTrainer, PPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# 奖励函数：代码执行结果
def code_execution_reward(responses, prompts):
    rewards = []
    for code in responses:
        # 在沙箱里执行代码
        result = execute_in_sandbox(code)
        # 测试通过 → 1.0，错误 → -1.0
        reward = 1.0 if result.tests_passed else -1.0
        rewards.append(reward)
    return rewards

# GRPO 训练（DeepSeek-R1 使用的方法，更稳定）
trainer = GRPOTrainer(
    model=model,
    args=grpo_config,
    reward_funcs=[code_execution_reward],
    train_dataset=coding_dataset,
)
trainer.train()
```

### 方法二：微调（成本较低）

如果没有 RL 训练的算力，可以用高质量数据做 SFT 微调：

**关键：数据质量远比数量重要**

```python
# 数据构造：只用"代码 + 能运行的测试"对
training_data = {
    "problem": "实现一个函数，找出数组中的第 k 大元素",
    "solution": """
def find_kth_largest(nums, k):
    import heapq
    return heapq.nlargest(k, nums)[-1]
    """,
    "tests": [
        "assert find_kth_largest([3,2,1,5,6,4], 2) == 5",
        "assert find_kth_largest([3,2,3,1,2,4,5,5,6], 4) == 4",
    ],
    "test_passed": True  # 只保留测试通过的数据！
}
```

**数据来源**：
- HumanEval、MBPP（经典）
- LiveCodeBench（更难，更接近真实任务）
- SWE-bench 任务对（从 GitHub Issue → PR 的数据）

### 方法三：混合 SSM 架构的复现

如果你想从架构层面借鉴 Ornith-1.0 的 GatedDeltaNet 混合设计：

```python
# 参考实现思路（伪代码）
class HybridModel(nn.Module):
    def __init__(self, n_layers=40, ssm_ratio=0.75):
        n_ssm = int(n_layers * ssm_ratio)   # 30 层 SSM
        n_attn = n_layers - n_ssm             # 10 层 Attention
        
        self.layers = nn.ModuleList([
            GatedDeltaNetLayer() if i < n_ssm 
            else FullAttentionLayer()
            for i in range(n_layers)
        ])
```

相关论文：
- **GatedDeltaNet**: [arxiv.org/abs/2412.06464](https://arxiv.org/abs/2412.06464)
- **Mamba**: [arxiv.org/abs/2312.00752](https://arxiv.org/abs/2312.00752)（SSM 的奠基工作）

---

## 实际部署：从量化到推理优化

对于独立开发者和小团队，直接运行 35B 模型需要约 66GB 显存（BF16）。实际可行方案：

**NVFP4 量化版（约 23.7GB，接近无损）**：
```bash
# 使用 AEON-7 的量化版本（开源，MIT）
vllm serve AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4 \
  --served-model-name ornith \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.85 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --attention-backend flash_attn \
  --enable-prefix-caching \
  --trust-remote-code
```

**性能对比**（DGX Spark GB10 上）：
| 配置 | Decode | TTFT |
|---|---|---|
| BF16 + stock vLLM | 30.6 tok/s | ~240ms |
| NVFP4 + DFlash | **93.3 tok/s** | ~91ms |

3 倍速度提升，TTFT 降低 2.6 倍。

---

## 给想做代码 LLM 的团队的建议

### 从 9B 规模开始

35B 和 397B 的模型代价很高，9B 是一个非常好的起点：
- 单张 A100 80G 可以 BF16 全量运行
- RL 训练成本可接受（4×A100 可以跑几天）
- 评测快（SWE-bench 跑一次也就几小时）

### 专注一个领域

Ornith-1.0 专注于 Agentic 代码生成，而不是试图做一个通用模型。专注让 RL 奖励信号更清晰：
- 你要优化的是"完成软件工程任务"
- 奖励函数是"代码通过测试"
- 这比"回答问题的质量"更容易量化

### 用 SWE-bench 作为评估锚点

SWE-bench Verified 已经成为代码 LLM 的行业标准基准。在你的训练过程中定期评测这个指标，可以给你清晰的方向感。

---

## 总结

Ornith-1.0 的成功来自三个核心选择：
1. **架构**：SSM + Attention 混合 + MoE，平衡速度和能力
2. **训练**：RL 让模型真正"理解"代码正确性而不只是生成
3. **专注**：专门为 Agentic 代码任务优化，而不是追求通用能力

对于想训练自己代码模型的工程师，最可行的路径是：**从开源 9B 模型出发，收集高质量"问题+通过测试的代码"数据，用 RL 微调（GRPO）优化通过率**。

这条路是走得通的，Ornith-1.0 证明了 RL 在代码领域的有效性。

> **相关资源**: [GatedDeltaNet 论文](https://arxiv.org/abs/2412.06464) · [SWE-bench](https://www.swebench.com) · [veRL 框架](https://github.com/volcengine/verl) · [TRL](https://github.com/huggingface/trl)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Ornith-1.0 (DeepReinforce) is a family of agentic code generation LLMs (9B/35B/397B) achieving SWE-bench Verified 75.6 — top-tier for autonomous software engineering. Hybrid architecture: 30 layers GatedDeltaNet (SSM) + 10 layers full attention + 256 MoE experts, 256K context, vision, RL-trained thinking model. This engineering guide explains what made Ornith-1.0 work and how to apply the same RL + fine-tuning techniques to train your own code model.

---

## What Makes Ornith-1.0 Different

**SWE-bench Verified 75.6**: The model can autonomously fix real GitHub issues end-to-end — not just generate code snippets.

**Hybrid SSM + Attention Architecture**:
- 30 layers GatedDeltaNet (O(n) state space model — faster, more efficient for long sequences)
- 10 layers full attention (global context for critical reasoning)
- 256 MoE experts + shared expert, ~3B active parameters (of 35B total)
- 256K token context

**Thinking model**: Every response includes a `<think>…</think>` reasoning chain before output.

**RL Training**: The core insight from DeepReinforce — code models should be trained on whether code actually works (test execution), not just whether it looks like code.

## Engineering Guide: How to Apply These Techniques

### Path 1: RL Fine-tuning (Recommended)

Take a base code model (CodeLlama, DeepSeek-Coder, or similar), apply RL using code execution as the reward signal.

**Toolstack**: TRL/HuggingFace for GRPO/PPO; veRL for larger scale; execution sandbox for reward computation.

**Reward function design**:
- Tests pass → +1.0
- Syntax errors → -1.0  
- Functionally correct but suboptimal → -0.1
- Complete agent task → +2.0

**Hardware**: 4×A100 80G minimum for 7B/9B scale RL training.

### Path 2: SFT with Execution-Verified Data

Lower compute than RL. Key: only include data where the solution actually passes tests. Quality >> quantity.

**Data sources**: HumanEval, MBPP, LiveCodeBench, SWE-bench (issue → PR pairs).

### Path 3: Hybrid SSM Architecture

GatedDeltaNet reference: [arxiv.org/abs/2412.06464](https://arxiv.org/abs/2412.06464). The 75/25 SSM/attention split is the starting point; tune based on your task's local vs global context needs.

## Practical Deployment

NVFP4 quantized 35B (≈23.7GB): **3×decode speedup** vs BF16, near-identical accuracy (KL≈0.0014, same agentic pass@1).

```bash
vllm serve deepreinforce-ai/Ornith-1.0-35B \
  --reasoning-parser qwen3 --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --enable-prefix-caching --trust-remote-code
```

## Recommendations for Teams Building Code LLMs

1. **Start at 9B scale** — single A100 80G, affordable RL training, fast SWE-bench evaluation
2. **Specialize** — focus on one domain (agentic code, not general purpose) for cleaner reward signals
3. **Use SWE-bench Verified as your north star** — it's becoming the industry standard for agentic code models

**Links**: [GatedDeltaNet paper](https://arxiv.org/abs/2412.06464) · [SWE-bench](https://www.swebench.com) · [veRL framework](https://github.com/volcengine/verl) · [TRL](https://github.com/huggingface/trl)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
