---
title: "TMEM：给 Agent 装上「可学习的参数记忆」——阿里通义论文工程解析"
titleEn: "TMEM: Parametric Memory for Self-Evolving Agents — An Engineering Guide to the Alibaba Paper"
description: "阿里巴巴通义 Qwen 团队提出 TMEM，让 Agent 在单次会话内通过 Fast LoRA 直接把经验写进模型参数，不再只是「查」历史——而是真正「学会」了。本文拆解论文原理，并给出工程落地的实现思路。"
descriptionEn: "Alibaba's Qwen team proposes TMEM: agents that write experience into fast LoRA weights within a single episode, genuinely altering their own behavior. This guide unpacks the mechanism and gives engineers a practical roadmap for implementing parametric memory in their own agents."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Research"
tags: ["Agent", "参数记忆", "Fast LoRA", "阿里通义", "自进化", "LLM", "强化学习", "Qwen", "长上下文"]
heroImage: "../../assets/images/tmem-parametric-memory-agent-guide-banner.jpg"
---

> **论文**：Scaling Self-Evolving Agents via Parametric Memory  
> **机构**：阿里巴巴通义 Qwen-Character Team × 北京大学  
> **发表**：arXiv:2606.04536，2026 年 6 月 3 日  
> **基座模型**：Qwen3-4B / Qwen3-8B

---

## 一句话讲清楚 TMEM 做了什么

现有的 LLM Agent 有记忆，但这个「记忆」只活在 prompt 里——不管是文字总结还是 RAG 检索，底层模型参数一直是冻结的。Agent 可以「查」历史，但不会因为历史而改变自己的行为策略。

**TMEM 的核心创新**：在单次 episode 里，Agent 每次触发记忆写入时，不是把信息塞进 prompt，而是把提炼出的监督信号做一次轻量级 LoRA 在线更新——把经验**写进参数**。之后的行动从 `π(θ₀ + Δt)` 采样，这个 Δt 是真实改变过的模型权重。

---

## 为什么 prompt 记忆有根本性局限？

**问题 1：丢失即永久消失**  
当 context 超出 token 预算被压缩时，被丢掉的信息再也没有路径影响后续决策。  

**问题 2：噪声覆盖信号**  
原始历史里充满冗余 tool 输出、重复对话、无关细节，关键证据淹没在噪声里，单次 forward pass 还要同时"找到信息"和"用好信息"。  

**问题 3：策略永不改变**  
RAG 和摘要记忆都不修改模型参数，Agent 的决策策略在整个 episode 里是固定的——它只能靠 prompt 内容变化来"感知"历史。

---

## TMEM 的核心机制

### 三层记忆架构

每个生成事件 `t`，Agent 同时维护三种状态：

```
工作上下文 h_t   ← 当前对话窗口（会被清空）
显式文字记忆 m_t ← 可选，文字摘要（TMEM 中为空）
快参数记忆 Δt   ← LoRA 权重，本 episode 内动态更新
```

动作从自适应策略采样：

```
a_t ~ π(θ₀ + Δt | c_t)
```

其中 `θ₀` 是基座参数（在 RL 训练阶段优化，单次 rollout 内固定），`Δt` 是在线更新的 fast weight。

### 记忆写入流程

当工作上下文超过预设 token 预算 `L_max` 时，触发记忆写入模式：

```
1. Agent 读取 memory-writing prompt d
2. 提取出 QA 格式的监督信号（从当前 session 蒸馏的问答对）
3. 用这批 QA 对做轻量级在线 SFT，更新 Δt
4. 清空工作上下文 h_t（信息已被内化进 Δt）
5. 后续行动从 π(θ₀ + Δt) 采样——行为已经改变
```

**关键区别**：和 MemAgent（写摘要进 prompt）不同，TMEM 提取的 QA 对直接被吸收进参数，不占用后续 context 空间。

---

## SVD 初始化——让少步更新有效的关键

标准 LoRA 随机初始化 A 矩阵，适合从头训练的场景。但 TMEM 的在线更新每次只有 **5 个 epoch**，步数极少，随机子空间会浪费大量更新在"找方向"上。

TMEM 的方案：用**预训练权重的 SVD 分解**初始化 LoRA 子空间。

对每个目标权重矩阵 W（仅 FFN 的 gate/up/down 投影），做 SVD 分解取 top-r 方向：

```
W = U Σ V^T

A₀ = Σr Vr^T  ← 高能量子空间
B₀ = 0         ← 初始 Δ₀ = B₀A₀ = 0（和基座相同）
```

在线更新时：
- **A 矩阵固定**（不更新，已锁定在高能方向）
- **只更新 B 矩阵**（在高能子空间里学系数）

这样少量 gradient 步就能在最重要的方向上学到有用的变化，而不是从随机方向开始摸索。

论文实验表明，SVD 初始化比随机初始化在精确匹配（EM）上提升 **+3.2 个百分点**。

---

## 实验结果

测试了四种记忆策略（无记忆 / 摘要记忆 / RAG 检索 / TMEM），分别在 Qwen3-4B 和 Qwen3-8B 上跑四个 benchmark：

**对话记忆（LongMemEval-S，RL 前）**：

| 方法 | Qwen3-4B F1 | Qwen3-8B F1 |
|------|-------------|-------------|
| 无记忆 | 5.30 | 3.50 |
| MemAgent（摘要） | 36.45 | 31.66 |
| A-MEM（RAG） | 29.22 | 28.99 |
| **TMEM** | **41.24** | **41.87** |

**RL 训练后增益**：RL 对所有方法都有提升，但 TMEM 获得的绝对增益最大（+4.92 F1 on LongMemEval-S），说明快权重机制让 RL 信号的利用更充分。

**监督信号形式对比（LoCoMo，Qwen3-4B）**：

| 监督信号形式 | F1 | EM |
|------|----|----|
| 下一个 token 预测（原始） | 21.19 | 10.74 |
| 自由形式摘要 | 24.86 | 14.28 |
| **QA 对（默认）** | **25.72** | **15.40** |

QA 格式的监督信号明显优于直接做 next-token prediction 或写自由摘要。

---

## 工程落地：普通开发者如何用这个思路

论文目前没有公开代码，但思路完全可以复现。以下是**工程实现路线图**：

### 第一步：实现 Fast LoRA 层

在 Hugging Face PEFT 的基础上，构建一个支持「在线更新」的 LoRA 适配器：

```python
import torch
from peft import LoraConfig, get_peft_model
from torch.linalg import svd

def svd_lora_init(model, target_modules, rank=6, last_n_layers=4):
    """用 SVD 初始化 LoRA 子空间，只装最后 n 层 FFN"""
    config = LoraConfig(
        r=rank,
        target_modules=target_modules,  # ["gate_proj", "up_proj", "down_proj"]
        lora_alpha=rank,
        lora_dropout=0.0,
        bias="none",
    )
    peft_model = get_peft_model(model, config)
    
    # 用 SVD 覆盖随机初始化的 A 矩阵
    for name, module in peft_model.named_modules():
        if hasattr(module, 'lora_A') and "last_layers" in name:
            W = module.base_layer.weight.data.float()
            _, S, Vh = svd(W, full_matrices=False)
            # 取 top-r 方向
            module.lora_A.default.weight.data = (
                torch.diag(S[:rank]) @ Vh[:rank, :]
            ).to(W.dtype)
            # B 初始为 0（标准做法）
            module.lora_B.default.weight.data.zero_()
    
    return peft_model
```

### 第二步：在 Agent 主循环里加触发机制

```python
class TMEMAgent:
    def __init__(self, model, tokenizer, L_max=4096):
        self.base_model = model
        self.tokenizer = tokenizer
        self.L_max = L_max
        # 初始化 Fast LoRA
        self.fast_lora = svd_lora_init(model, ["gate_proj","up_proj","down_proj"])
        self.delta_B = {}  # 累积的 B 矩阵更新
        
    def run_episode(self, task_prompt):
        working_context = task_prompt
        
        while not self.is_done(working_context):
            # 检查是否超过上下文预算
            if self.token_length(working_context) > self.L_max:
                self.trigger_memory_write(working_context)
                working_context = task_prompt  # 清空，经验已内化进 Δt
            
            # 从 π(θ₀ + Δt) 采样下一步行动
            action = self.sample_action(working_context)
            obs = self.env_step(action)
            working_context += f"\nAction: {action}\nObs: {obs}"
    
    def trigger_memory_write(self, context):
        """从当前 context 提取 QA 监督信号，做在线 LoRA 更新"""
        # 1. 生成 QA 对
        extraction_prompt = context + "\n\n" + MEMORY_WRITING_PROMPT
        qa_pairs = self.generate(extraction_prompt)
        
        # 2. 在线 SFT 更新 B 矩阵（A 矩阵固定）
        self.online_lora_update(qa_pairs)
    
    def online_lora_update(self, qa_pairs, lr=5e-4, epochs=5):
        """轻量级在线 SFT，只更新 B 矩阵"""
        optimizer = torch.optim.SGD(
            [p for n, p in self.fast_lora.named_parameters() if 'lora_B' in n],
            lr=lr
        )
        dataset = self.format_as_sft(qa_pairs)
        for _ in range(epochs):
            for batch in dataset:
                loss = self.fast_lora(**batch).loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
```

### 第三步：记忆写入 Prompt 设计

论文里 memory-writing prompt 的核心是让 Agent 从当前 session 提取**有落地答案的 QA 对**，不是自由摘要：

```python
MEMORY_WRITING_PROMPT = """
基于上面的对话历史，请生成一批 QA 格式的记忆条目。

要求：
1. 每个 QA 对必须能从历史中找到明确答案（grounded）
2. 问题要覆盖关键事实、用户偏好、任务进度
3. 格式：JSON 列表 [{"q": "...", "a": "..."}, ...]
4. 生成 5-10 对，优先覆盖细节（不是泛化总结）

不要生成原历史里找不到答案的问题。
"""
```

实验数据支持这个设计：QA 对格式明显优于「写自由摘要」（EM 高 1.12 点）和「做 next-token 预测」（EM 高 4.66 点）。

### 第四步：RL 训练（进阶）

如果你想让 extraction policy 也一起被优化，需要在 RL 框架里加 **stop-gradient**：

```python
# 在 GRPO/PPO 训练时，梯度不通过在线 LoRA 更新路径传播
def compute_policy_gradient(rollout, reward):
    loss = 0
    for segment in rollout.segments:
        # 普通任务行动的 log-prob（用 sg(Δt)）
        for step in segment.task_steps:
            loss += -reward * log_prob(step.action, 
                                        policy=base_model + sg(delta_t))
        # 记忆提取行动的 log-prob（同样 sg(Δt)）
        if segment.extraction_action:
            loss += -reward * log_prob(segment.extraction_action,
                                        policy=base_model + sg(delta_t))
    return loss
```

这个 stop-gradient 的意义：让 RL 优化「产生好的 QA 对」这个行为，而不是试图直接通过 LoRA 更新路径做 meta-gradient（那会非常贵）。

---

## 关键超参数

| 超参数 | 论文设置 | 说明 |
|--------|----------|------|
| LoRA rank r | 6 | 平衡容量和速度 |
| 目标层 | 最后 4 层 FFN | gate_proj / up_proj / down_proj |
| SVD 投影矩阵 A | 冻结 | 只更新 B |
| 在线 SGD 学习率 | 5e-4 | 远高于预训练 LR |
| 在线 SFT 轮数 | 5 epochs | batch_size=16 |
| 上下文触发预算 L_max | 4096（对话） / 12288（长文档） / 8192（搜索） | 过大过小都会掉点，需调参 |
| 更新是否累积 | 是 | 每次触发从当前 B 继续，不重置 |

---

## 和其他方案的定位对比

| 方案 | 记忆存储 | 参数改变？ | 适合场景 |
|------|----------|-----------|----------|
| MemGPT / MemAgent | prompt 摘要 | ❌ 否 | 短-中长度对话，无需「学会」 |
| A-MEM / GraphRAG | 外部向量库 + 检索 | ❌ 否 | 知识库问答，检索质量是瓶颈 |
| TTT（Test-Time Training） | 参数更新 | ✅ 是 | 但不在 Agent 决策流程内，且更新粒度粗 |
| **TMEM** | Fast LoRA Δt | ✅ 是 | 长 episode、需跨上下文窗口「学会」的 Agent |

**TMEM 不适合**：单轮问答、Context 够用的短任务、对推理延迟极度敏感的场景（在线 LoRA 更新有额外计算成本）。

---

## 后续值得关注的方向

1. **代码开源**：论文尚未公开代码，作者是通义团队，大概率会在 Qwen 生态下开源
2. **Qwen3 以外的基座**：SVD 初始化和 QA 对形式的监督信号对其他模型（Llama、Mistral 等）应该同样有效
3. **多 episode 跨会话积累**：目前 Δt 在 episode 结束后丢弃，如果持久化 Δt 可以实现真正的跨会话参数学习
4. **与 RAG 混合**：Fast LoRA 记住「哪类事实怎么推理」，RAG 记住「具体事实内容」，两者互补

---

## 资源链接

- [arxiv:2606.04536](https://arxiv.org/abs/2606.04536) — 论文原文（HTML 版本可读性好）
- [PEFT 库](https://github.com/huggingface/peft) — Hugging Face LoRA 实现
- [Qwen3 模型](https://huggingface.co/Qwen) — 论文基座模型
- MemAgent 参考实现：[MemAgent Paper](https://arxiv.org/abs/2506.07715)

© 2026 Author: Mycelium Protocol

<!--EN-->

## TMEM: Parametric Memory for Self-Evolving Agents — An Engineering Guide

> **Paper**: Scaling Self-Evolving Agents via Parametric Memory  
> **Institution**: Alibaba Tongyi Qwen-Character Team × Peking University  
> **Published**: arXiv:2606.04536, June 3, 2026  
> **Base Models**: Qwen3-4B / Qwen3-8B

---

### The Problem in One Sentence

Existing memory-augmented LLM agents store experience in prompt space — as summaries or RAG retrievals — while keeping model parameters frozen. They can *look up* what happened, but they can't *learn from* it: the policy is unchanged by experience.

**TMEM** flips this: when the context budget is reached, instead of writing a summary into the prompt, the agent distills QA-pair supervision from the session and runs a lightweight online LoRA update — writing experience directly into model weights. Subsequent actions are sampled from `π(θ₀ + Δt)`, where `Δt` is the fast LoRA delta that genuinely reflects what the agent has learned.

---

### How It Works

**Three memory layers** per timestep:
- `h_t` — working context (cleared after each trigger)
- `m_t` — explicit text memory (empty in TMEM)
- `Δt` — fast LoRA weights (updated online within the episode)

**Memory write trigger**: when `token_length(h_t + m_t) > L_max`, the agent:
1. Generates grounded QA pairs from the current session
2. Runs online SFT with SGD (lr=5e-4, 5 epochs, batch=16) to update `Δt`
3. Clears `h_t` — the experience is now in the weights, not the prompt

**SVD initialization**: Instead of random LoRA `A` matrices, TMEM initializes `A₀` from the top-r singular vectors of each FFN projection weight. During online updates, `A` stays frozen and only `B` is trained. This focuses the few available gradient steps on the highest-energy directions of the pretrained weights.

**Key finding on supervision format**: QA pairs consistently outperform free-form summaries (+1.12 EM) and next-token prediction (+4.66 EM). The extraction must produce grounded, question-answerable facts — not general descriptions.

---

### Engineering Roadmap

To implement TMEM ideas in your own agents:

1. **Build an online-updatable LoRA layer** using PEFT, with SVD initialization for the A matrix targeting the last 4 FFN layers (gate_proj, up_proj, down_proj), rank r=6
2. **Add a context budget trigger** in your agent loop: when token count exceeds `L_max`, call the memory-write action instead of continuing normally
3. **Design the memory-writing prompt** to extract grounded QA pairs (5-10 pairs, each with a verifiable answer from history), not free-form summaries
4. **Run online SGD** on only the B matrix (A frozen), 5 epochs, batch 16, SGD lr=5e-4. Updates are cumulative — each trigger starts from the current B, not zero
5. **For RL training** (optional): add stop-gradient through the LoRA update path in GRPO/PPO so the base model learns to produce better extraction actions without expensive meta-gradients

---

### When to Use vs. When Not To

**Best fit**: multi-session conversations, long search trajectories, tasks where the agent needs to carry fine-grained factual knowledge across context window boundaries.

**Not ideal**: single-turn QA, tasks that fit in a single context window, latency-critical inference (online LoRA updates add per-trigger computation).

---

### Resources

- [Paper PDF](https://arxiv.org/abs/2606.04536) — arXiv:2606.04536
- [PEFT library](https://github.com/huggingface/peft) — HuggingFace LoRA implementation
- [Qwen3 models](https://huggingface.co/Qwen) — paper's base models

© 2026 Author: Mycelium Protocol
