---
title: "VibeThinker-3B 拆解：微博团队如何用 7800 美元训出打赢 DeepSeek R1 的小模型，以及你能复刻什么"
titleEn: "VibeThinker Decoded: How Weibo AI Beat DeepSeek R1 for $7,800 — and What You Can Replicate"
description: "微博AI团队开源的VibeThinker系列用「频谱到信号」训练范式，让1.5B小模型在数学竞赛上超越400倍大的DeepSeek R1，训练成本仅7800美元。本文拆解其完整训练管线SSP，分析如何模仿这套方法训练你自己的专项小模型。"
descriptionEn: "Weibo AI's VibeThinker series uses the Spectrum-to-Signal Principle to train a 1.5B model that beats DeepSeek R1 on math benchmarks at a total cost of $7,800. This article deconstructs the full SSP training pipeline and shows how to replicate the approach for your own specialized small model."
pubDate: "2026-06-27"
updatedDate: "2026-06-27"
category: "Tech-News"
tags: ["小模型", "模型训练", "强化学习", "蒸馏", "推理模型", "开源", "VibeThinker", "微博AI"]
heroImage: "../../assets/images/vibethinker-small-model-training-guide-banner.jpg"
---

> **一句话结论（BLUF）**：VibeThinker 证明了一件事——**可验证推理能力是可压缩的**。用对方法，1.5B 小模型在数学竞赛上能超越 400 倍大的 DeepSeek R1，训练成本只需 7800 美元。这套方法（SSP）可以被任何有特定领域数据和可验证答案的人复刻。

---

## 原始资源

GitHub（MIT 开源）：https://github.com/WeiboAI/VibeThinker （1403 ⭐）

VibeThinker-3B 论文：https://arxiv.org/abs/2606.16140

VibeThinker-1.5B 论文：https://arxiv.org/abs/2511.06221

HuggingFace 模型：https://huggingface.co/WeiboAI/VibeThinker-3B

ModelScope（国内镜像）：https://modelscope.cn/models/WeiboAI/VibeThinker-3B

---

## 一、VibeThinker 做到了什么？

微博AI团队先后发布了两个版本：

### VibeThinker-1.5B（2025 年 11 月）

训练成本：**$7,800**（对比 DeepSeek R1 的 $294,000，MiniMax-M1 的 $535,000）

| 基准测试 | VibeThinker-1.5B | DeepSeek R1（671B，400倍大）|
|---|:-:|:-:|
| AIME24 | **80.3** | 79.8 |
| AIME25 | **74.4** | 70.0 |
| HMMT25 | **50.4** | 41.7 |
| LiveCodeBench v6 | 51.1 | — |

基础模型得分：AIME24 仅 6.7，训练后达到 80.3——**提升了 73.6 个百分点**。

### VibeThinker-3B（2026 年 6 月）

基础模型：Qwen2.5-Coder-3B

| 基准测试 | 分数 | 加 CLR 后 |
|---|:-:|:-:|
| AIME26 | 94.3 | **97.1** |
| HMMT25 | 89.3 | **95.4** |
| LiveCodeBench v6 Pass@1 | **80.2** | — |
| LeetCode 竞赛题（未见过）| **96.1%** 通过率 | — |
| IFEval（指令遵循）| **93.4** | — |

3B 模型达到了 DeepSeek V3.2、GLM-5、Gemini 3 Pro 量级的性能——而这些模型比它大几十到几百倍。

---

## 二、为什么小模型可以做到这件事？

这是整个 VibeThinker 系列最核心的理论贡献，他们称之为**「参数压缩-覆盖假说」（Parametric Compression-Coverage Hypothesis）**：

```
可验证推理（数学 / 代码 / STEM）
    → 可被压缩进小模型的参数
    → 关键是：这类任务有明确的"对错"信号

开放域知识（百科问答 / 常识 / 长尾信息）
    → 需要广泛的参数覆盖
    → 无法被小模型有效压缩
```

**实际含义**：如果你的目标任务有**可验证的答案**（答案对不对可以被自动判断），那么用小模型专攻这个领域，是真正可行的路径。

典型的"可验证"任务：
- 数学题（答案数值对不对）
- 代码（能不能跑通测试用例）
- SQL（能不能查出正确数据）
- 医学诊断（有标准答案的病例）
- 法律条文理解（有明确解释的条款）
- 特定格式输出（JSON schema 验证）

---

## 三、核心方法论：SSP（频谱到信号原则）

VibeThinker 的训练范式叫 **Spectrum-to-Signal Principle（SSP）**，两个阶段各司其职：

```
阶段一（SFT）：先"撒网"，生成宽广的解题频谱（Spectrum）
阶段二（RL）：再"收网"，从频谱中放大正确信号（Signal）
```

### 为什么要先"撒网"？

直觉上你可能认为 SFT 应该只喂正确答案。但 VibeThinker 的核心洞察是：**小模型在 RL 之前需要先"见过"多样的解题路径**，才能在 RL 阶段有东西可以优化。

用比喻解释：
- 传统做法 = 只给学生看标准答案，让他背
- SSP 做法 = 先让学生看各种解题过程（包括错的），再用测试反馈强化正确路径

---

## 四、完整训练管线（可复刻版）

### Step 1：选择基础模型

VibeThinker 的选择：**Qwen2.5-Coder-3B**

选择标准：
- 模型本身有一定的推理基础（完全随机初始化的模型难以收敛）
- 规模与目标任务匹配（数学/代码任务适合 Coder 系列）
- 有完整的 tokenizer 和 chat template 支持

你的选择策略：
- 目标是数学/科学推理 → Qwen2.5-Math / Qwen2.5-Coder
- 目标是中文专项 → Qwen2.5-Instruct 中文版
- 目标是代码生成 → StarCoder2 / DeepSeekCoder

### Step 2：SFT 第一阶段——多样性蒸馏（Diversity-Exploring Distillation）

**目的**：让模型见识各种解题路径，建立"解题空间"

**具体做法**：
1. 准备问题集（你的目标领域，例如竞赛数学题、代码题）
2. 用大教师模型（如 DeepSeek V3 / Qwen3-72B）以**高温度**（temperature=1.0）采样**多个不同答案**（每题 8-32 个）
3. 保留所有答案（对的和错的都保留，让模型见识解题过程的多样性）
4. 用这些数据做 SFT

```python
# 示例：用教师模型采样多样性数据
from vllm import LLM, SamplingParams

teacher = LLM("deepseek-ai/DeepSeek-V3")
sampling_params = SamplingParams(
    temperature=1.0,   # 高温度 = 高多样性
    top_p=0.95,
    n=16,              # 每题采样 16 个不同回答
    max_tokens=8192
)

outputs = teacher.generate(problems, sampling_params)
# 保存所有 16 个答案，不过滤
```

### Step 3：SFT 第二阶段——课程学习（Curriculum Learning）

**目的**：从易到难组织数据，防止模型在简单题上退化

**具体做法**：
1. 按难度给训练数据排序（可用模型错误率衡量难度）
2. 训练初期主要喂简单题，逐步增加难题比例
3. 保留高质量、完整的长推理链（不要截断思维过程）

```python
# 难度分层示例
easy_data = [d for d in train_data if d['difficulty'] <= 3]
medium_data = [d for d in train_data if 3 < d['difficulty'] <= 7]
hard_data = [d for d in train_data if d['difficulty'] > 7]

# 课程：easy 40% → medium 40% → hard 20%（初期）
# 逐步调整为 easy 20% → medium 30% → hard 50%（后期）
```

### Step 4：RL 阶段——MGPO（MaxEnt 引导的策略优化）

**目的**：用可验证信号强化正确推理路径，同时保持探索性

**两个关键设计**：

1. **MaxEnt（最大熵）约束**：在优化正确率的同时，惩罚策略过于集中（避免模型总是走同一条解题路径，失去探索能力）

2. **可验证奖励函数**：

```python
def reward_fn(model_output, ground_truth, task_type):
    if task_type == "math":
        # 提取数字答案，判断数值是否相等
        pred = extract_math_answer(model_output)
        return 1.0 if is_equivalent(pred, ground_truth) else -0.1
    
    elif task_type == "code":
        # 运行测试用例
        results = run_tests(model_output, test_cases)
        return sum(results) / len(results)  # 通过率作为奖励
    
    elif task_type == "format":
        # 验证输出格式（JSON schema 等）
        try:
            validate_schema(model_output, expected_schema)
            return 1.0
        except:
            return 0.0
```

**多领域 RL**：VibeThinker-3B 同时在数学、代码、STEM、指令遵循多个领域做 RL，防止单领域过拟合。

### Step 5：离线自蒸馏（Offline Self-Distillation）

**目的**：让模型从自己的最佳输出中再学习，巩固和稳定能力

**具体做法**：
1. 用当前训练好的模型，对训练集重新生成答案
2. 筛选出**答案正确 + 推理过程完整**的样本
3. 用这些"自己的最佳输出"再做一轮 SFT

```python
# 自蒸馏数据准备
def collect_self_distill_data(model, problems, ground_truths, n_samples=8):
    best_solutions = []
    for problem, gt in zip(problems, ground_truths):
        outputs = model.generate(problem, n=n_samples, temperature=1.0)
        # 筛选：答案正确 + 推理链完整（不截断）
        valid = [o for o in outputs
                 if is_correct(o, gt) and len(o) > 500]
        if valid:
            # 选最长的（推理最完整的）
            best_solutions.append(max(valid, key=len))
    return best_solutions
```

### Step 6：指令 RL（保持指令遵循能力）

**目的**：防止极端推理训练破坏模型的通用指令遵循能力

**做法**：在 RL 阶段加入指令遵循任务的奖励信号（VibeThinker-3B 的 IFEval 得分 93.4 证明这一步有效）

---

## 五、测试时扩展：CLR（声明级可靠性评估）

VibeThinker-3B 引入了一个推理时的技巧：**CLR（Claim-Level Reliability Assessment）**

**原理**：对同一道题生成多个答案，不是简单多数投票，而是在"声明级别"评估每个推理步骤的可靠性

**效果**：
- AIME26：94.3 → **97.1**
- HMMT25：89.3 → **95.4**
- BruMO25：**99.2**

这是一个无需额外训练的推理时扩展策略，适合在部署阶段使用。

---

## 六、给不同人群的复刻建议

### 场景 A：个人/小团队，有领域数据，预算 < $1 万

**参考 VibeThinker-1.5B 路径（总成本 $7,800）**

```
基础模型：Qwen2.5-1.5B 或 3B（免费）
教师模型：DeepSeek V3 API（按量付费，采样阶段主要成本）
训练：租 H100 × 8（约 $3-5/小时，SFT 需约 100-200 小时 GPU）
RL：Qwen3 72B 本地部署 或 API 验证奖励
```

关键成功条件：
- **你的任务必须有可验证的对/错**（无法验证 = 无法做 MGPO）
- 训练数据建议至少 5,000-20,000 条高质量问题

### 场景 B：公司团队，想训特定行业小模型

参考 VibeThinker-3B 路径：

1. 选 Qwen2.5-Coder-7B 或 14B 作为基础
2. 用内部大模型（或 Claude/GPT-4o）采样多样性 SFT 数据
3. 构建领域专属的验证器（是核心资产）
4. 分步做：SFT → 课程学习 → 多领域 RL → 自蒸馏

### 场景 C：研究者，想理解方法论

核心论文需精读：
- SSP 原理：https://arxiv.org/abs/2511.06221（1.5B 版，方法论更清晰）
- 3B 升级版：https://arxiv.org/abs/2606.16140
- 评测代码：https://github.com/WeiboAI/VibeThinker/tree/main/eval

---

## 七、直接跑 VibeThinker（5 分钟上手）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

# 加载模型（首次需要下载，约 6-8GB）
model_path = "WeiboAI/VibeThinker-3B"  # 或 WeiboAI/VibeThinker-1.5B
model = AutoModelForCausalLM.from_pretrained(
    model_path, low_cpu_mem_usage=True,
    torch_dtype="bfloat16", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

def ask(prompt):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    gen_config = GenerationConfig(
        max_new_tokens=40960,
        do_sample=True,
        temperature=0.6,
        top_p=0.95,
        top_k=None
    )
    output_ids = model.generate(**inputs, generation_config=gen_config)
    output_ids = [o[len(i):] for i, o in
                  zip(inputs.input_ids, output_ids)]
    return tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]

# 测试
print(ask("求解：设 f(x) = x³ - 3x + 2，求 f'(x) 的零点。"))
```

**推荐推理框架**（速度更快）：
```bash
pip install vllm==0.10.1
python -m vllm.entrypoints.openai.api_server \
  --model WeiboAI/VibeThinker-3B \
  --dtype bfloat16 \
  --max-model-len 40960
```

---

## 八、VibeThinker 训练方法的边界在哪里？

这套方法**很适合**：
- ✅ 数学 / 物理 / 化学 / 竞赛题
- ✅ 算法题 / 代码生成（有测试用例）
- ✅ SQL / 结构化数据查询
- ✅ 特定格式的文档生成（有 schema 验证）
- ✅ 医学标准化题目（有标准答案的执照考试）

这套方法**不太适合**：
- ❌ 开放域问答（无法验证答案对错）
- ❌ 创意写作 / 风格生成
- ❌ 需要大量世界知识的通用任务
- ❌ 主观评分任务（无客观奖励信号）

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/WeiboAI/VibeThinker |
| 3B 模型（HuggingFace）| https://huggingface.co/WeiboAI/VibeThinker-3B |
| 1.5B 模型（HuggingFace）| https://huggingface.co/WeiboAI/VibeThinker-1.5B |
| 3B 论文（arXiv）| https://arxiv.org/abs/2606.16140 |
| 1.5B 论文（arXiv）| https://arxiv.org/abs/2511.06221 |
| 评测代码 | https://github.com/WeiboAI/VibeThinker/tree/main/eval |
| ModelScope（国内）| https://modelscope.cn/organization/WeiboAI |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: VibeThinker proves one thing: **verifiable reasoning capability is compressible**. With the right method, a 1.5B model can beat DeepSeek R1 on math competitions at $7,800 total training cost. The approach (SSP) can be replicated by anyone with domain-specific data and a verifiable answer signal.

---

## What Did VibeThinker Achieve?

Weibo AI released two models in this series:

**VibeThinker-1.5B (November 2025)** — Total training cost: **$7,800**

| Benchmark | VibeThinker-1.5B | DeepSeek R1 (671B — 400× larger) |
|---|:-:|:-:|
| AIME24 | **80.3** | 79.8 |
| AIME25 | **74.4** | 70.0 |
| HMMT25 | **50.4** | 41.7 |

The base model scored 6.7 on AIME24 before training. After SSP: 80.3. **+73.6 percentage points.**

**VibeThinker-3B (June 2026)** — Base model: Qwen2.5-Coder-3B

- AIME26: 94.3 → **97.1** (with CLR test-time scaling)
- HMMT25: 89.3 → **95.4** (with CLR)
- LiveCodeBench v6: **80.2 Pass@1**
- LeetCode (unseen contests): **96.1%** acceptance
- IFEval: **93.4**

Performance band matches DeepSeek V3.2, GLM-5, and Gemini 3 Pro.

---

## Why Small Models Can Do This

The **Parametric Compression-Coverage Hypothesis**:

```
Verifiable reasoning (math / code / STEM)
    → Compressible into small model parameters
    → Requires: clear right/wrong verification signal

Open-domain knowledge (encyclopedic / common sense)
    → Requires broad parameter coverage
    → Cannot be efficiently compressed into small models
```

If your target task has **verifiable answers** (right vs. wrong can be determined automatically), a small specialist model is a genuinely viable path.

---

## The SSP Training Pipeline

### Stage 1: SFT — Diversity Distillation

Use a large teacher model to sample **many diverse solutions** per problem at high temperature — including wrong ones. The goal is to give the small model exposure to a broad solution space before RL.

```python
# Sample diverse solutions with teacher model
sampling_params = SamplingParams(
    temperature=1.0, top_p=0.95,
    n=16, max_tokens=8192
)
# Keep ALL 16 outputs per problem, don't filter
```

### Stage 2: SFT — Curriculum Learning (3B upgrade)

Organize training data from easy → hard. Prevents catastrophic forgetting. Preserves complete long-context reasoning chains without truncation.

### Stage 3: RL — MGPO (MaxEnt-Guided Policy Optimization)

- **Verifiable reward signal**: math answer match, code test pass rate, format validation
- **MaxEnt constraint**: penalize over-concentrated policy (keep exploring, not just exploiting)
- **Multi-domain**: train simultaneously on math, code, STEM, instruction-following

```python
def reward_fn(model_output, ground_truth, task_type):
    if task_type == "math":
        return 1.0 if is_equivalent(extract_answer(model_output), ground_truth) else -0.1
    elif task_type == "code":
        return sum(run_tests(model_output, test_cases)) / len(test_cases)
    elif task_type == "format":
        try: validate_schema(model_output, schema); return 1.0
        except: return 0.0
```

### Stage 4: Offline Self-Distillation

Generate outputs with the trained model. Filter for correct + complete reasoning chains. Fine-tune on the model's own best outputs to consolidate capabilities.

### Stage 5: Instruction RL

Fine-tune for instruction following without degrading reasoning ability.

---

## Replication Guidance by Use Case

| Use case | Base model | Verifiable signal | Cost estimate |
|---|---|---|---|
| Math competition | Qwen2.5-Math-1.5B | Answer equivalence | $3,000–8,000 |
| Competitive coding | Qwen2.5-Coder-3B | Test case pass rate | $5,000–15,000 |
| Domain Q&A (exam-style) | Qwen2.5-1.5B | Exact match / MCQ | $2,000–5,000 |
| SQL generation | Qwen2.5-Coder-1.5B | Query result match | $3,000–8,000 |

**What SSP requires**: a domain where you can automatically verify whether an answer is correct. Without a verifiable signal, MGPO doesn't work.

---

## Quick Start: Run VibeThinker Now

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

model = AutoModelForCausalLM.from_pretrained(
    "WeiboAI/VibeThinker-3B",
    torch_dtype="bfloat16", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("WeiboAI/VibeThinker-3B")

messages = [{"role": "user", "content": "Solve: Find all x where x³ - 3x + 2 = 0"}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)
output = model.generate(**inputs, max_new_tokens=40960, temperature=0.6, top_p=0.95, do_sample=True)
print(tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

Recommended inference: `vllm==0.10.1` or `sglang>=0.4.9.post6` for production throughput.

---

## FAQ

**Q: Does SSP require proprietary data?**  
No. VibeThinker used publicly available math and coding benchmarks (AIME, HMMT, LeetCode, etc.) for both SFT and RL. The key is having many diverse problems with verifiable answers, not proprietary data.

**Q: Can I replicate this without a large teacher model?**  
The diversity distillation stage works best with a teacher significantly stronger than the student. You could use DeepSeek V3 or Qwen3-72B API for data generation, which is cheap per-sample.

**Q: My task doesn't have automatic verification — can I still use this?**  
SSP's RL stage relies on verifiable rewards. For tasks without them (creative writing, open Q&A), you'd need a different RL approach (RLHF with human feedback, or a trained reward model). The efficiency gains may be smaller.

**Q: What's CLR and should I implement it?**  
Claim-Level Reliability Assessment is a test-time strategy: generate multiple solutions and assess reliability at the reasoning-step level, not just final answer voting. It requires no retraining and adds ~N× inference cost. Worth implementing for high-stakes evaluation; overkill for everyday use.

**Q: Does VibeThinker work well in Chinese?**  
The Qwen2.5 base models are strongly multilingual. VibeThinker's training is math/code focused and uses English benchmarks, but the base model's Chinese ability is preserved. For Chinese-specific domains, fine-tuning on Chinese-language domain data after the base SSP training would help.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
