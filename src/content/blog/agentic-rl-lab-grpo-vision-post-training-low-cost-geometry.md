---
title: "5块钱让大模型学会看图做几何题：GRPO 后训练的低成本实验"
titleEn: "agentic-rl-lab-grpo-vision-post-training-low-cost-geometry"
description: "KMnO4-zx/agentic-rl-lab，147 stars，Apache 2.0，Python。用 PyTRIO 远程训练平台 + GRPO 算法，5元在 Qwen3.5-4B 上做几何图形问答（GeoQA）的 Vision RL 后训练，准确率从 71% 升到 87%（+16pp）。全系列复现了 10 篇 RL 算法论文（GRPO/DAPO/GSPO/Search-R1/ReTool 等），核心主题：只写数据、reward 和 loss——把 infra 交给远端，让 RL 后训练的门槛从「一台 8 卡机器」降到「一行命令」。"
descriptionEn: "KMnO4-zx/agentic-rl-lab, 147 stars, Apache 2.0, Python. GRPO post-training on Qwen3.5-4B for geometric visual QA (GeoQA) with PyTRIO remote compute — ¥5, 100 steps, accuracy from 71% to 87% (+16pp). The full series reproduces 10 RL algorithm papers (GRPO/DAPO/GSPO/Search-R1/ReTool and more). Core theme: write only the data, reward, and loss — hand off infra to the remote, bringing the barrier to LLM RL post-training down from 'an 8-GPU server' to 'one command.'"
pubDate: "2026-08-10"
updatedDate: "2026-08-10"
category: "Research"
tags: ["AI", "GRPO", "后训练", "RL", "开源", "Python", "视觉模型", "Mycelium"]
heroImage: "../../assets/images/agentic-rl-lab-grpo-vision-post-training-low-cost-geometry-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

训练大模型通常是这样一张清单：租一台 8 卡机器，搭 infra，接采样服务，写 trainer，调 LoRA，接 checkpoint，跑日志——然后才开始做你真正想做的事：验证某个 reward 函数行不行，某个 loss 有没有差别。

KMnO4-zx 从另一个方向开始：**把 infra 交给远端，只写数据、reward 和 loss**。

用这个方式，他在 Qwen3.5-4B 上做了一次几何图形问答的 Vision GRPO 后训练，花了 5 块钱，100 步，准确率从 71% 升到了 87%。

GitHub: https://github.com/KMnO4-zx/agentic-rl-lab | ⭐ 147 | Apache 2.0 | Python

---

## 这个系列在做什么

agentic-rl-lab 是一个「逐篇复现 RL 算法」的开源实验记录。目前完成了 10 章：

| 章节 | 算法 | 任务 |
|------|------|------|
| 0 | Loss 函数基础 | importance sampling / PPO / CISPO |
| 1 | GRPO | GSM8K 数学题（文本） |
| 2 | OPD | 通用数学 + 医学推理 |
| 3 | Search-R1 | 多轮搜索 RL（Qwen3.5-4B） |
| 4 | OPSD | 步骤蒸馏 |
| 5 | ReTool | 代码交错 agent RL |
| 6 | DAPO | 4 项核心改进 |
| 7 | GSPO | 序列级重要性比率 |
| 8 | ALFWorld | 家庭任务 agent（文本 env） |
| 9 | **Vision GRPO** | **GeoQA 几何图形问答** |

前 8 章的输入都是文本。第 9 章第一次把整条 RL 链路推进到多模态：模型先看一张几何图，再读题，做 RL 更新。

基础设施是 **PyTRIO**（远程训练平台）和 **SwanLab**（实验追踪）。本地只写实验逻辑，前向、反向、采样、checkpoint 都在远端跑。

---

## GRPO 是什么

GRPO（Group Relative Policy Optimization）来自 DeepSeekMath 论文。它要解决的问题是：**PPO 好用，但太重**。

PPO 需要一个 value model 来估计 baseline，而 value model 本身也是一个大模型，显存和计算都要上去。

GRPO 的替换思路很直接：

1. 对同一个问题，采样一组回答（group）
2. 给每个回答打 reward
3. 用这组回答的平均 reward 作为 baseline——不需要单独训练 value model
4. 比组内平均分高的回答，advantage 为正；低的为负
5. 用这个 advantage 更新 policy

$$
A_i = \frac{r_i - \mathrm{mean}(r_1, \ldots, r_G)}{\mathrm{std}(r_1, \ldots, r_G)}
$$

同一道题里，相对更好的答案被鼓励，相对更差的被压低。这就是整个 GRPO 的核心。

第 1 章的文本 demo 跑 GSM8K 数学题，reward 是 0/1（答对或答错）。调试完整流程花了 55 元；如果只跑 10 步验证脚本能走通，成本可以低到 5 元。

---

## Vision GRPO：把图片送进训练循环

第 9 章做的事情，是把上面这套机制接上图片输入。

任务是 **GeoQA**——一个中文几何问答数据集。每条样本包含：几何图片、题目、四个候选项（A/B/C/D）、正确答案标签。共 5010 条，取 3503 条训练，固定 100 条测试。

模型看到的输入只有图片、题目和选项，不看解析过程。Reward 是选项匹配：答对 1，答错 0。

**实验结果**：

| 模型 | Accuracy | Format rate |
|------|---:|---:|
| Qwen3.5-4B Base | 71.0% | 75.0% |
| GRPO step 100 | 87.0% | 91.0% |
| 提升 | **+16.0 pp** | **+16.0 pp** |

100 步，5 块钱，+16pp。

---

## 图片怎么进入 PyTRIO

Vision GRPO 和纯文本版本差异最大的地方，是图片如何进入训练循环。

训练脚本用模型自己的 chat template 格式化输入，同时放入文本和图片占位符：

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": format_question(subject, choices)},
            {"type": "image", "image": "geoqa"},
        ],
    }
]
```

渲染后的 prompt 沿 `<|image_pad|>` 拆成三个 chunk：文本 → 图片 → 文本。图片在送入服务前先合成白色背景（处理 RGBA），再用模型的 image processor 计算视觉 patch 数写入 `ImageChunk.expected_tokens`。

采样完成后会检查：

```python
response.input_tokens == len(prompt)
```

本地视觉 token 估计和远端结果必须一致，否则训练立刻报错——因为后续的 `target_tokens`、old logprobs 和 advantages 依赖同一个位置坐标系。

---

## 训练配置

| 项目 | 配置 |
|------|------|
| 基座模型 | Qwen/Qwen3.5-4B |
| 训练方式 | LoRA，rank 32 |
| 优化方法 | group-relative advantage + importance_sampling |
| 训练步数 | 100 steps |
| 每步题目数 | 8 |
| 每题 rollout 数 | 8 |
| 最大生成长度 | 1,024 tokens |
| 学习率 | 4e-5 |

整条数据流：

```text
GeoQA 图文题目
  ↓ 当前 LoRA 权重生成 sampler
  ↓ 同题并发采样 8 条 completion
  ↓ 解析最后一个 \boxed{A-D}
  ↓ 规则 reward：正确 1，其余 0
  ↓ 组内计算 relative advantage
  ↓ 构造多模态 Datum 并更新 LoRA
```

---

## 为什么这件事值得关注

大模型的后训练通常被认为是「大厂才能做的事」：需要大量 GPU、复杂 infra、专门的团队。

agentic-rl-lab 证明的是另一件事：**如果你只需要验证某个 reward 函数、某个 loss 变体，或者某个任务领域的 RL 适配性，你不需要那些**。

PyTRIO 把本地需要处理的东西压缩到最小：数据处理、reward 函数、loss 函数、实验循环。其他全部在远端。这让「做一个 RL 实验」的感觉更像做一个普通的数据分析——写逻辑，跑，看结果，改。

Vision GRPO 这章是这套方法第一次接上图片输入。从 GSM8K 文字题到 GeoQA 几何图，RL 训练循环本身的结构没有改变——变化的只是图片怎么进入 prompt，和 reward 怎么从选项匹配算出来。

这个扩展路径是清晰的。

---

## 快速上手

```bash
# 克隆仓库
git clone https://github.com/KMnO4-zx/agentic-rl-lab
cd agentic-rl-lab

# 安装依赖（uv）
uv sync

# 登录 PyTRIO
trio login

# 跑 Vision GRPO（先下载数据集）
cd 09-vision-grpo
# 参考 start.md
```

先跑 1-2 步验证脚本能走通，再开正式训练。成本是可控的。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## ¥5 to Teach a Vision Model Geometry: Low-Cost Post-Training with GRPO

*by Mycelium Protocol*

---

Training a large model usually looks like this: rent an 8-GPU server, build infra, wire up a sampling service, write a trainer, tune LoRA, handle checkpointing, set up logging — and then finally start doing what you actually wanted to do: test whether a reward function works, whether one loss function beats another.

KMnO4-zx started from the other direction: **hand the infra to a remote platform, write only the data, reward, and loss.**

Using this approach, he ran Vision GRPO post-training on Qwen3.5-4B for geometric visual QA — ¥5, 100 steps, accuracy up from 71% to 87%.

GitHub: https://github.com/KMnO4-zx/agentic-rl-lab | ⭐ 147 | Apache 2.0 | Python

---

### What This Series Does

agentic-rl-lab is an open-source "reproduce one RL paper at a time" experiment log. Ten chapters completed:

| Chapter | Algorithm | Task |
|---------|-----------|------|
| 0 | Loss function basics | importance sampling / PPO / CISPO |
| 1 | GRPO | GSM8K math (text) |
| 2 | OPD | General math + medical reasoning |
| 3 | Search-R1 | Multi-round search RL (Qwen3.5-4B) |
| 4 | OPSD | Step distillation |
| 5 | ReTool | Code-interleaved agentic RL |
| 6 | DAPO | 4 core improvements |
| 7 | GSPO | Sequence-level importance ratio |
| 8 | ALFWorld | Household agent (text env) |
| 9 | **Vision GRPO** | **GeoQA geometric visual QA** |

Chapters 1–8 are text-only. Chapter 9 is the first to push the full RL loop into multimodal: the model sees a geometry image, reads the question, and gets RL updates based on whether it picks the right answer.

Infrastructure is **PyTRIO** (remote training platform) and **SwanLab** (experiment tracking). Local code handles only the experiment logic; forward pass, backward pass, sampling, and checkpointing all run remotely.

---

### What GRPO Is

GRPO (Group Relative Policy Optimization) comes from the DeepSeekMath paper. The problem it solves: **PPO works, but it's heavy**.

PPO requires a separate value model to estimate the baseline — and for LLMs, that value model is itself a large model, adding both memory and compute. GRPO's substitution is direct:

1. Sample a group of completions for the same question
2. Score each completion with a reward
3. Use the group's average reward as baseline — no value model needed
4. Completions above average get positive advantage; below average get negative
5. Update policy with this advantage

Same question, same group — better answers are encouraged, worse ones are pushed down. That's the whole mechanism.

Chapter 1's text demo runs on GSM8K with binary reward (0 if wrong, 1 if right). Debugging the full pipeline cost ¥55; running just 10 steps to check the script works can cost as little as ¥5.

---

### Vision GRPO: Getting Images into the Training Loop

Chapter 9 extends this to image inputs.

The task is **GeoQA** — a Chinese geometric QA dataset. Each sample has: a geometry image, a question, four candidate answers (A/B/C/D), and a correct label. 5,010 total samples; 3,503 for training, fixed 100 for evaluation. The model sees only the image, question, and choices — not the solution.

**Results:**

| Model | Accuracy | Format rate |
|-------|---:|---:|
| Qwen3.5-4B Base | 71.0% | 75.0% |
| GRPO step 100 | 87.0% | 91.0% |
| Gain | **+16.0 pp** | **+16.0 pp** |

100 steps. ¥5. +16pp.

---

### Training Config

| Setting | Value |
|---------|-------|
| Base model | Qwen/Qwen3.5-4B |
| Training | LoRA, rank 32 |
| Optimization | group-relative advantage + importance_sampling |
| Steps | 100 |
| Topics per step | 8 |
| Rollouts per topic | 8 |
| Max generation length | 1,024 tokens |
| Learning rate | 4e-5 |

Full data flow:

```text
GeoQA image+text question
  ↓ sampler from current LoRA weights
  ↓ 8 concurrent completions per question
  ↓ extract last \boxed{A-D}
  ↓ rule reward: correct=1, else=0
  ↓ group-relative advantage
  ↓ multimodal Datum → LoRA update
```

---

### Why This Is Worth Attention

LLM post-training is commonly considered a large-lab problem: many GPUs, complex infra, dedicated teams.

agentic-rl-lab demonstrates something different: **if your goal is to validate a reward function, a loss variant, or RL adaptation for a specific domain, you don't need any of that**.

PyTRIO compresses what needs to be done locally to its minimum: data processing, reward function, loss function, experiment loop. Everything else runs remotely. "Running an RL experiment" starts to feel like running a data analysis script — write the logic, run it, read results, iterate.

Vision GRPO is the first chapter in this series to handle image inputs. From GSM8K text to GeoQA geometry, the RL loop structure didn't change — only how images enter the prompt and how reward is computed from option matching.

The extension path is clear.

---

### Quick Start

```bash
git clone https://github.com/KMnO4-zx/agentic-rl-lab
cd agentic-rl-lab

uv sync
trio login

# Chapter 9: see 09-vision-grpo/start.md
```

Run 1–2 steps first to verify the script works, then scale up. Cost is controllable.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
