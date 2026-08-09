---
title: "GRPO微调小模型工程指南：80美元训练，超越o3的完整路径"
titleEn: "A GRPO Engineering Guide for Small Models: Eighty Dollars of Training to Beat o3"
description: "GRPO（Group Relative Policy Optimization）让小模型在垂直任务上碾压frontier大模型成为可能。本文整合 ART、ms-swift、OpenClaw-RL 等开源仓库，以及 ART·E（Qwen 2.5 14B超越o3，$80训练）、MCP·RL等6个真实工程案例，给出完整的工程路径：任务选择→数据构造→奖励函数设计→训练循环→监控与避坑。"
descriptionEn: "GRPO (Group Relative Policy Optimization) makes it practical for small specialist models to outperform frontier LLMs on narrow tasks. This guide integrates ART, ms-swift, OpenClaw-RL, and six real engineering cases — including ART·E (Qwen 2.5 14B beats o3 for $80) and MCP·RL — covering the full path from task selection to reward design to training loop monitoring."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-Experiment"
tags: ["GRPO", "强化学习", "小模型", "Qwen", "微调", "LLM训练", "AI工程", "Mycelium"]
heroImage: "../../assets/images/grpo-small-model-engineering-guide-banner.jpg"
---

*by Mycelium Protocol*

---

一个 14B 的 Qwen 模型，训练成本 80 美元，在邮件检索任务上的准确率高于 o3，幻觉率低于 o3，每次回答所用的轮数也比 o3 少。

这不是理论。这是 OpenPipe 在 2025 年用 GRPO 做的 ART·E 项目，代码和模型全部开源。

**GRPO（Group Relative Policy Optimization）** 是目前让小模型在垂直任务上超越大模型最可靠的工程路径。本文整合多个开源仓库和真实案例，给出完整的工程指南。

---

## 为什么 GRPO 适合小模型专项训练

GRPO 的核心思路：对同一个问题运行 N 次推理，给每次打分，让模型向高分轨迹学习。

相比 PPO，GRPO 省去了 critic（价值函数）网络，用"同组相对奖励"代替——同一批问题里，比自己平均水平好的轨迹得正梯度，差的得负梯度。这带来两个实用优势：

1. **显存需求低**：不需要维护 critic 网络，单张 H100 足够训练 14B 模型
2. **任务特异性强**：奖励函数完全由你定义，可以精确优化"在这个任务上正确"这件事，而不是"听起来不错"

Frontier 模型的优势是通用性，但为此付出了巨大的推理成本。一个 9B 专项模型：
- 推理成本低 30-350 倍
- 在特定任务上准确率反而更高
- 本地部署，无 API 依赖

---

## 核心开源工具栈

### 1. OpenPipe/ART（10,557 星）

[Agent Reinforcement Trainer](https://github.com/OpenPipe/ART) — 目前最成熟的 GRPO Agent 训练框架。

```python
pip install openpipe-art
```

核心设计：**client/server 分离**

```python
import art

model = art.TrainableModel(
    project="my-task",
    name="specialist-v1",
    base_model="Qwen/Qwen2.5-14B-Instruct"
)

# 训练循环 = rollout + score + train
for step in range(num_steps):
    trajectories = await asyncio.gather(*[
        rollout(model, question) for question in batch
    ])
    for traj in trajectories:
        traj.reward = score(traj)
    await model.train(trajectories)
```

client 在你的笔记本上跑，server 在任何有 GPU 的机器上跑。内置 vLLM 推理、Unsloth 训练优化、W&B 可视化。

支持模型：Qwen3.6、Llama 4、GPT-OSS 及所有 vLLM/HuggingFace 兼容模型。

### 2. modelscope/ms-swift（15,017 星）

[ms-swift](https://github.com/modelscope/ms-swift) 是更全面的微调工具箱，支持 CPT/SFT/DPO/GRPO，覆盖 600+ LLM 和 300+ 多模态模型。

```bash
# 用 ms-swift 跑 GRPO
swift rlhf \
  --rlhf_type grpo \
  --model Qwen/Qwen2.5-7B-Instruct \
  --dataset <your_dataset> \
  --reward_funcs accuracy format
```

如果你的任务不需要 Agent loop，只是分类/提取/判断，ms-swift 比 ART 更轻量。

### 3. Gen-Verse/OpenClaw-RL（5,617 星）

[OpenClaw-RL](https://github.com/Gen-Verse/OpenClaw-RL) — "用说话训练任何 Agent"。定义 Agent 任务和奖励函数的门槛进一步降低，重点在自然语言描述任务后自动生成训练数据和奖励逻辑。

### 4. rasbt/reasoning-from-scratch（4,851 星）

[reasoning-from-scratch](https://github.com/rasbt/reasoning-from-scratch) — 用 PyTorch 从零实现一个推理 LLM，包含 GRPO 的完整数学推导和代码。理解原理的最佳起点。

### 5. walkinglabs/hands-on-modern-rl（3,403 星）

[hands-on-modern-rl](https://github.com/walkinglabs/hands-on-modern-rl) — 从基础 RL 到 RLVR、Agent 的完整课程，每节都有配套代码。

---

## 完整工程路径

### 第一步：选对任务

GRPO 适合的任务特征：

- **可验证**：有明确的正确/错误判断标准
- **有价值**：Frontier 模型能做但成本太高，或者有延迟要求
- **有规模**：每天调用量足够多，让训练成本摊平

**好案例**：邮件检索、电商商品审核、代码 lint 检查、法律文件分类、SQL 生成验证

**差案例**：开放式写作、需要最新知识的任务（没有时效优势）

### 第二步：构造数据集

不需要大量人工标注数据——这是 GRPO 的核心优势之一。

**方法 1：合成数据 + LLM 生成答案**

```python
# ART·E 的做法：用 GPT-4.1 对真实数据生成问答对
for batch in email_batches:
    qa_pairs = gpt4.generate(
        f"Given these {len(batch)} emails, generate realistic questions "
        f"a user might ask, with answers and source message IDs."
    )
    # 过滤 how_realistic < 0.7 的问题
    dataset.extend([qa for qa in qa_pairs if qa.realistic >= 0.7])
```

**方法 2：使用现有评测数据集**

已有标准答案的数据集直接用，不需要额外生成。

### 第三步：设计奖励函数

**奖励函数是 GRPO 的核心**，比选什么 base model 更重要。

```python
def compute_reward(trajectory: Trajectory) -> float:
    reward = 0.0
    
    # 主要目标：答案正确
    if trajectory.answer_correct:
        reward += 1.0
    elif trajectory.returned_i_dont_know:
        reward += 0.1  # 承认不知道好过瞎猜
    else:
        reward -= 0.5  # 幻觉惩罚
    
    # 次要目标：效率
    if trajectory.answer_correct:
        reward += 0.05 * (MAX_TURNS - trajectory.num_turns)
    
    return reward
```

**避坑：partial credit 要谨慎**

ART 团队曾给"多用几轮"加奖励，模型学会了无限重复最后一个工具调用。中间奖励很容易被 reward hack，能不加就不加。

### 第四步：实现 rollout 函数

```python
async def rollout(model: art.TrainableModel, question: str) -> Trajectory:
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    
    trajectory = art.Trajectory()
    
    for turn in range(MAX_TURNS):
        response = await model.chat(messages)
        tool_call = parse_tool_call(response)
        
        if tool_call.name == "return_final_answer":
            trajectory.reward = compute_reward(tool_call.args, ground_truth)
            break
        
        tool_result = execute_tool(tool_call)
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "tool", "content": tool_result})
    
    return trajectory
```

### 第五步：训练循环

```python
for step in range(NUM_STEPS):
    batch = dataset.sample(BATCH_SIZE)
    
    # 每个问题跑 N 次（默认 4 次）
    all_trajectories = []
    for question in batch:
        group = await asyncio.gather(*[
            rollout(model, question) for _ in range(N_ROLLOUTS)
        ])
        all_trajectories.extend(group)
    
    # GRPO 更新
    await model.train(all_trajectories)
    
    # 每 30 步验证
    if step % 30 == 0:
        accuracy = evaluate(model, val_set)
        log_to_wandb(accuracy, step)
```

### 第六步：监控与调参

**关键指标：**

```
奖励标准差 > 0 → 模型在学习
奖励标准差 ≈ 0 → 陷入局部最优（所有轨迹得分相同）
```

如果标准差接近 0：
- 增加每个问题的 rollout 次数
- 降低 learning rate
- 增加任务多样性

**超参参考（ART·E 最终配置）：**

```python
learning_rate = 1.2e-5
epochs = 2
rollouts_per_question = 4
batch_size = 12
max_turns = 10
```

---

## 真实工程案例

### 案例 1：ART·E — Qwen 14B 超越 o3，训练成本 $80

**任务**：自然语言搜索邮件收件箱（Enron 数据集，50 万封邮件）

**模型**：Qwen 2.5 14B → 训练后专项模型

**数据**：用 GPT-4.1 从真实邮件生成 4000 个合成问答对

**奖励函数**：答案正确 +1.0 / 幻觉 -0.5 / 效率奖励 +0.05×(减少的轮数)

**训练成本**：约 $80（单张 H100，不到一天）

**结果：**

| 指标 | o3 | ART·E (Qwen 14B) |
|------|-----|-----------------|
| 准确率 | 基线 | **更高** |
| 幻觉率 | 基线 | **更低** |
| 平均轮数 | 基线 | **少约 1 轮** |

开源：[模型](https://huggingface.co/OpenPipe/art-e-008) + [训练代码](https://github.com/OpenPipe/ART/tree/main/examples/art-e)

---

### 案例 2：MCP·RL — 3B 模型掌握 MCP 工具调用

**任务**：让 Qwen 2.5 3B 学会正确使用 NWS（美国国家气象局）MCP 服务

**方法**：给模型一个真实的 MCP 服务端，用工具调用成功率作为奖励

**意义**：证明 GRPO 可以教会小模型**使用外部工具**，而不仅仅是生成文本

代码：[ART/examples/mcp-rl](https://github.com/OpenPipe/ART/blob/main/examples/mcp-rl/mcp-rl.ipynb)

---

### 案例 3：2048 — 27B 模型学会玩游戏

**任务**：Qwen 3.6 27B 学习 2048 游戏策略

**奖励**：游戏得分

**意义**：展示 GRPO 的通用性——任何有可量化反馈的任务都能训练

Notebook：[examples/2048](https://colab.research.google.com/github/openpipe/art-notebooks/blob/main/examples/2048/2048.ipynb)

---

### 案例 4：电商商品目录审核（通用化）

**参考场景**：用 Qwen3 9B + GRPO 训练商品合规审核模型

**任务**：给定商品标题、描述、图片，判断是否符合平台规范

**奖励设计参考**：
- 人工标注结果完全匹配 +1.0
- 误判违规 -0.8（业务代价大）
- 漏判违规 -0.5
- 正确拒绝（有争议商品）+0.3

**成本优势**：如果平台日均审核 10 万条，Frontier API 成本约 $190-$1720/天；专项 9B 模型自托管成本约 $5/天（单 A100），准确率还更高。

---

### 案例 5：LangGraph Agent 训练

ART 直接集成了 LangGraph，你可以在现有的 LangGraph workflow 上套 RL 训练：

```python
from art.integrations.langgraph import train_langgraph_agent

await train_langgraph_agent(
    graph=your_existing_graph,
    dataset=your_dataset,
    reward_fn=your_reward_fn,
    base_model="Qwen/Qwen2.5-7B-Instruct"
)
```

---

## 核心经验总结

**选任务比选模型更重要。** 同样的 GRPO，"判断这张图片是否违规"比"写一首诗"效果好得多，因为前者有清晰的奖励信号。

**奖励函数要简单，宁可欠完备，不要 reward hack。** 加中间奖励时要谨慎测试，模型总能找到你没想到的捷径。

**看训练曲线比看最终结果更重要。** 奖励方差接近零是最危险的信号，意味着训练停滞了但你不知道。

**合成数据够用。** ART·E 用 GPT-4.1 生成的合成问答对训练了一个超越 o3 的模型，不需要大量人工标注。

**成本是线性的，准确率不是。** $80 训练一个专项模型，如果每天调用量超过几千次，一个月内就回本。

---

## 资源汇总

| 项目 | 用途 | 链接 |
|------|------|------|
| OpenPipe/ART | Agent GRPO 训练框架 | [GitHub](https://github.com/OpenPipe/ART) |
| modelscope/ms-swift | 全面微调工具箱 | [GitHub](https://github.com/modelscope/ms-swift) |
| Gen-Verse/OpenClaw-RL | 低门槛 Agent RL | [GitHub](https://github.com/Gen-Verse/OpenClaw-RL) |
| rasbt/reasoning-from-scratch | 原理实现 | [GitHub](https://github.com/rasbt/reasoning-from-scratch) |
| walkinglabs/hands-on-modern-rl | RL 到 RLVR 完整课程 | [GitHub](https://github.com/walkinglabs/hands-on-modern-rl) |
| ART·E 案例 | 完整代码 + 模型 | [Blog](https://openpipe.ai/blog/art-e-mail-agent) |

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Engineering Guide: Fine-Tune a 9B Specialist with GRPO to Beat Frontier Models

*by Mycelium Protocol*

A 14B Qwen model, $80 in training costs, higher accuracy than o3 on email search, fewer hallucinations, fewer turns per answer.

This isn't theory. It's [ART·E](https://openpipe.ai/blog/art-e-mail-agent), a real project by OpenPipe using GRPO, with all code and model weights open-sourced.

**GRPO (Group Relative Policy Optimization)** is currently the most reliable engineering path for making small specialist models outperform large frontier models on narrow tasks. This guide integrates key open-source repositories and real engineering cases into a complete working path.

### Why GRPO Works for Specialist Models

GRPO's core idea: run the same question N times, score each attempt, and train the model to behave more like the high-scoring trajectories. Instead of a separate critic network (like PPO), it uses *group-relative rewards* — within a batch of rollouts, better-than-average trajectories get positive gradients, worse ones get negative gradients.

Practical advantages:
- **Lower memory requirements**: no critic network needed; a single H100 handles 14B models
- **Precise task optimization**: the reward function is entirely yours — you optimize for "correct on this task" instead of "sounds good in general"

Frontier models optimize for universality at enormous inference cost. A 9B specialist: 30–350× cheaper per call, often more accurate on the specific task, and deployable locally with no API dependency.

### Core Open-Source Stack

**[OpenPipe/ART](https://github.com/OpenPipe/ART)** (10,557 stars): The most mature GRPO agent training framework. Client/server split — run the client on your laptop, the server on any GPU machine. Built on vLLM + Unsloth. `pip install openpipe-art`.

**[modelscope/ms-swift](https://github.com/modelscope/ms-swift)** (15,017 stars): Full fine-tuning toolkit covering SFT/DPO/GRPO for 600+ LLMs. Better for non-agent tasks (classification, extraction, judgment).

**[Gen-Verse/OpenClaw-RL](https://github.com/Gen-Verse/OpenClaw-RL)** (5,617 stars): Train any agent "simply by talking" — natural language task description → auto-generated training data and reward logic.

**[rasbt/reasoning-from-scratch](https://github.com/rasbt/reasoning-from-scratch)** (4,851 stars): Full PyTorch implementation of a reasoning LLM from scratch, including the GRPO math. Best starting point for understanding the algorithm.

### The Engineering Path

**Step 1 — Pick the right task.** GRPO works when: the task is verifiable (clear correct/wrong), valuable (frontier models can do it but it's too expensive), and high-volume (enough daily calls to amortize training cost). Good fits: document classification, compliance review, structured extraction, tool-use agents.

**Step 2 — Construct your dataset.** You don't need large human-labeled datasets. ART·E generated 4,000 synthetic Q&A pairs from real emails using GPT-4.1, then filtered by a `how_realistic` score. The resulting model beat o3.

**Step 3 — Design the reward function.** This matters more than base model selection. Keep it simple: primary objective (correct answer) + secondary objectives (efficiency, hallucination penalty). Avoid intermediate rewards — the model will reward-hack them. ART's team gave a small bonus for more turns to encourage exploration; the model learned to repeat the last tool call until hitting the turn limit.

**Step 4 — Training loop.** Each GRPO step: sample a batch of questions → run each N times in parallel → score all trajectories → update the model. ART wraps this into ~10 lines of Python.

**Step 5 — Monitor reward standard deviation.** If variance approaches zero, training has stalled (all trajectories scoring the same). Fix: increase rollouts per question, lower learning rate, or add task diversity.

### Key Real Cases

**ART·E** — Qwen 2.5 14B beats o3 on email search. $80 training, single H100, under one day. Higher accuracy, lower hallucination rate, ~1 fewer turn per answer. [Open-source model + code](https://github.com/OpenPipe/ART/tree/main/examples/art-e).

**MCP·RL** — Qwen 2.5 3B learns to correctly use a real MCP server (NWS weather API). Demonstrates GRPO for tool-use training, not just text generation.

**E-commerce catalog review** (general pattern) — 9B specialist model trained on platform compliance rules. At 100K daily reviews, frontier API cost: ~$190–$1,720/day. Self-hosted 9B model: ~$5/day (single A100), with higher task-specific accuracy.

### Bottom Line

Task selection matters more than model selection. Reward functions should be simple — undercomplete beats reward-hackable. Synthetic data generated by a strong LLM is enough to train a specialist that beats that same LLM. The cost is linear; the accuracy improvement is not.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
