---
title: "SkillOpt：微软联合上交复旦同济，让 AI Agent 的 Skill 像神经网络一样被训练"
description: "微软研究院联合上海交通大学、复旦大学、同济大学发布 SkillOpt——首个对 AI Agent Skill 文档进行系统化优化的框架，在 52 个评测单元全部获胜，让普通开发者无需训练模型就能持续提升 Agent 能力。"
titleEn: "SkillOpt: Microsoft + Top Chinese Universities Train Agent Skills Like Neural Networks"
descriptionEn: "Microsoft Research, partnering with SJTU, Fudan, and Tongji, releases SkillOpt — the first systematic optimizer for AI agent skill documents that wins all 52 evaluated cells and lets developers improve agent capability without touching model weights."
pubDate: 2026-06-07
category: "Research"
tags: ["AI Agent", "SkillOpt", "Microsoft Research", "Skill Optimization", "Open Source", "Self-Evolving Agents"]
lang: "zh-CN"
heroImage: "../../assets/images/skillopt-microsoft-self-evolving-agent-skills-banner.png"
---

**Skill 能运行，不代表 Skill 写得好。**

这是 SkillOpt 诞生的出发点。你花时间为 AI Agent 写了一份 Skill 文档，但你怎么知道这份 Skill 已经是最优的？或者，它还有多大提升空间？

2026 年 5 月，微软研究院联合**上海交通大学、复旦大学、同济大学**发布了 SkillOpt（arXiv:2605.23904），给出了一个系统化的答案：**把 Skill 文档当作神经网络的参数来训练**。

GitHub 已达 **5278 star、532 fork**，PyPI 上线即可 `pip install`。

## 问题：Skill 的三条死路

目前主流的 Agent Skill 写法有三种，SkillOpt 的论文明确指出它们都有根本性缺陷：

| 方式 | 缺陷 |
|------|------|
| **手写 Skill** | 凭经验，缺乏系统反馈，无法可靠提升 |
| **一次性 LLM 生成** | 没有反馈循环，生成即定格 |
| **松散自修订** | 缺乏控制，方向随机，可能越改越差 |

SkillOpt 的核心洞察是：**Skill 文档应该是可训练的状态，而不是静态产物**。

## 核心思路：文本空间的深度学习类比

SkillOpt 把深度学习的训练范式完整移植到了文本空间：

```
深度学习              SkillOpt（文本空间）
─────────────────────────────────────────────
参数（Parameter）  →  Skill 文档
梯度（Gradient）   →  轨迹推导出的编辑方向
学习率（LR）       →  每步允许的编辑预算
验证集（Valid.）   →  Hold-out 验证门控
批次（Batch）      →  一批执行轨迹（Minibatch）
Epoch              →  一轮完整优化周期
```

最关键的是：**模型权重完全冻结，优化的只有 Skill 文档本身**。你不需要微调模型，不需要 GPU，只需要 API 调用权限。

## 训练循环：六步迭代

每一轮 SkillOpt 的工作如下：

```
1. Rollout  → 用当前 Skill 执行任务，记录轨迹和分数
2. Reflect  → 分析一批轨迹，提炼成功/失败模式
3. Aggregate→ 将反思汇总为有界的文本编辑（增/删/改）
4. Select   → 候选编辑必须通过验证集，严格改善才接受
5. Update   → 接受的编辑写入 Skill，被拒编辑进入负反馈缓冲区
6. Evaluate → 在测试集上评估，输出 best_skill.md
```

**三个稳定性机制**保证不会"越改越差"：
- **验证门控**：候选 Skill 必须在 hold-out 集上严格涨分才被接受
- **有界编辑**：每步只允许 4-8 个修改（类似学习率限制）
- **慢/元更新**：Epoch 级别的跨批次方向稳定机制

## 实验结果：52 局全胜

这是 SkillOpt 最让人印象深刻的地方。

跨 **6 个基准测试、7 个目标模型、3 种执行环境**（直接对话、Codex CLI、Claude Code CLI），共 **52 个评测单元，SkillOpt 全部获胜或并列最优**。

对比对象包括：手写 Skill、一次性 LLM 生成、Trace2Skill、TextGrad、GEPA、EvoSkill。

以 GPT-5.5 为例的提升幅度：

| 执行环境 | 平均准确率提升 |
|---------|-------------|
| 直接对话 | **+23.5 分** |
| Codex 代理循环 | **+24.8 分** |
| Claude Code | **+19.1 分** |

部分 benchmark 的具体数字更震撼：
- SpreadsheetBench：**+38.9 分**
- OfficeQA：**+39.0 分**

更重要的是，**迁移性**表现优秀：用 GPT-5.4 优化出的 Skill，迁移到小模型后仍保留约 82% 的增益；从 Codex 迁移到 Claude Code 环境，无需重新优化。

这意味着：一份优化好的 `best_skill.md`，可以跨模型、跨平台复用。

## 普通开发者怎么用

### 安装（5 分钟）

```bash
pip install skillopt

# 如果要用 Gradio 监控界面：
pip install skillopt[webui]

# Claude 后端：
pip install skillopt[claude]
```

### 配置 API

```bash
cp .env.example .env
# 编辑 .env，填入 API 密钥

# OpenAI 兼容接口（OpenAI / DeepSeek / 任意 v1 接口）：
export AZURE_OPENAI_ENDPOINT="https://api.openai.com/v1"
export AZURE_OPENAI_API_KEY="sk-..."
export AZURE_OPENAI_AUTH_MODE="openai_compatible"

# Claude：
export ANTHROPIC_API_KEY="sk-ant-..."

# Qwen（本地 vLLM）：
export QWEN_CHAT_BASE_URL="http://localhost:8000/v1"
export QWEN_CHAT_MODEL="Qwen/Qwen3.5-4B"
```

### 运行优化（核心三步）

**Step 1：准备你的 Skill（或者从空白开始）**

```markdown
# my_skill.md（种子 Skill，可以很简略）
你是一个专注于数学推理的 AI，每一步都要写出完整推理过程。
```

**Step 2：开始训练**

```bash
python scripts/train.py \
  --config configs/searchqa/default.yaml \
  --optimizer_model gpt-4o \
  --target_model gpt-4o-mini
```

你可以用强模型（gpt-4o）做优化器，用弱模型（gpt-4o-mini）做目标 Agent，最大化性价比。

**Step 3：取出成果**

训练结束后，`ckpt/` 目录下会生成 `best_skill.md`。这个文件就是优化后的 Skill，300-2000 token，直接复制到你的 Agent 的 System Prompt 里即可。

零额外推理开销——部署时不需要额外调用任何模型，就是一段 Markdown 文本。

### 监控训练过程

```bash
# 启动 WebUI 看实时优化曲线
pip install skillopt[webui]
opensquilla gateway run  # 或按项目文档启动
```

## 我的判断

**这是一篇方法论严谨、工程落地扎实的研究，值得认真对待。**

SkillOpt 解决的不是"能不能用 AI 写 Skill"的问题（那个已经解决了），而是"怎么系统地、可重复地把 Skill 写好"的问题。这个问题在 AI Agent 进入工程化落地阶段之后，变得越来越重要。

**对普通开发者最实际的价值：**

1. **不需要懂深度学习**：整套流程是 API 调用，没有 GPU，没有梯度
2. **结果是可读的 Markdown**：你知道 Skill 改了什么，可以审阅、可以 Git 管理
3. **跨模型复用**：在贵模型上优化一次，迁移到便宜模型继续用
4. **已有生态接入**：gbrain、darwin-skill 等工具已在 2026 年 6 月集成

**需要注意：**
- 优化需要消耗 API token（优化器 + 目标模型都在跑），有成本
- 效果高度依赖你的任务定义和验证集质量——垃圾进、垃圾出
- 目前 v0.1.0，生产稳定性仍需观察

---

如果你在用 Claude Code、Codex、或任何支持 Skill 文件的 AI Agent，SkillOpt 值得认真试一试。

**GitHub：** [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)  
**arXiv 原文：** 2605.23904 — SkillOpt: Executive Strategy for Self-Evolving Agent Skills  
**项目主页：** https://aka.ms/skillopt  
**PyPI：** `pip install skillopt`

<!--EN-->

## SkillOpt: Microsoft + Top Chinese Universities Train Agent Skills Like Neural Networks

**A skill that runs is not the same as a skill that's well-written.**

That's the starting point for SkillOpt. You spend time writing a skill document for your AI agent — but how do you know it's optimal? How much headroom is there for improvement?

In May 2026, Microsoft Research, in collaboration with **Shanghai Jiao Tong University, Fudan University, and Tongji University**, released SkillOpt (arXiv:2605.23904): a systematic answer. **Treat the skill document as a trainable parameter — just like neural network weights.**

The GitHub repo already has **5,278 stars and 532 forks**, and it's a `pip install` away.

## The Problem: Three Dead Ends for Agent Skills

The three dominant approaches to writing agent skills all have fundamental flaws, as the SkillOpt paper explicitly notes:

| Approach | Problem |
|----------|---------|
| **Hand-crafted skills** | Experience-driven, no systematic feedback, unreliable improvement |
| **One-shot LLM generation** | No feedback loop — generated and frozen |
| **Loose self-revision** | Uncontrolled direction, can degrade rather than improve |

SkillOpt's core insight: **skill documents should be trainable state, not static artifacts.**

## Core Concept: Deep Learning Analogized to Text Space

SkillOpt ports the full deep learning training paradigm into text space:

```
Deep Learning         SkillOpt (Text Space)
──────────────────────────────────────────────
Parameter         →   Skill document
Gradient          →   Trajectory-derived edit direction
Learning rate     →   Edit budget per step
Validation set    →   Hold-out selection gate
Batch             →   A batch of execution trajectories
Epoch             →   One full optimization cycle
```

Crucially: **model weights remain completely frozen — only the skill document is optimized.** No fine-tuning. No GPU. Just API calls.

## The Training Loop: Six Steps

Each SkillOpt round works as follows:

```
1. Rollout    → Execute tasks with current skill; record trajectories and scores
2. Reflect    → Analyze a batch of trajectories; identify success/failure patterns
3. Aggregate  → Distill into bounded text edits (add / delete / replace)
4. Select     → Candidate edit must strictly improve validation score to be accepted
5. Update     → Accepted edits written to skill; rejected edits enter negative feedback buffer
6. Evaluate   → Score on test set; export best_skill.md
```

Three stability mechanisms prevent "editing to worse":
- **Validation gating**: strict improvement on hold-out set required
- **Bounded edits**: only 4-8 modifications per step (analogous to learning rate)
- **Slow/meta updates**: cross-batch directional stability at epoch boundaries

## Results: 52-for-52

This is SkillOpt's most striking result.

Across **6 benchmarks, 7 target models, and 3 execution harnesses** (direct chat, Codex CLI, Claude Code CLI) — **52 evaluated (model, benchmark, harness) cells — SkillOpt wins or ties best on every single one.**

Competitors included: hand-crafted skills, one-shot LLM generation, Trace2Skill, TextGrad, GEPA, and EvoSkill.

Accuracy gains for GPT-5.5:

| Harness | Average Accuracy Gain |
|---------|----------------------|
| Direct chat | **+23.5 points** |
| Codex agentic loop | **+24.8 points** |
| Claude Code | **+19.1 points** |

Specific benchmark highlights:
- SpreadsheetBench: **+38.9 points**
- OfficeQA: **+39.0 points**

**Transferability** is also strong: a skill optimized on GPT-5.4 retains ~82% of its gains when transferred to a smaller model. Codex-optimized skills transfer to Claude Code without re-optimization.

One optimized `best_skill.md` can serve across models and platforms.

## How to Use It: A Practical Developer Guide

### Install (5 minutes)

```bash
pip install skillopt

# With Gradio monitoring dashboard:
pip install skillopt[webui]

# Claude backend:
pip install skillopt[claude]
```

### Configure API Access

```bash
cp .env.example .env

# OpenAI-compatible (OpenAI / DeepSeek / any v1 endpoint):
export AZURE_OPENAI_ENDPOINT="https://api.openai.com/v1"
export AZURE_OPENAI_API_KEY="sk-..."
export AZURE_OPENAI_AUTH_MODE="openai_compatible"

# Anthropic Claude:
export ANTHROPIC_API_KEY="sk-ant-..."

# Qwen (local vLLM):
export QWEN_CHAT_BASE_URL="http://localhost:8000/v1"
export QWEN_CHAT_MODEL="Qwen/Qwen3.5-4B"
```

### Run Optimization (Three Steps)

**Step 1: Prepare your seed skill (or start empty)**

```markdown
# my_skill.md — a minimal seed is fine
You are an AI focused on mathematical reasoning.
Show your full reasoning process at every step.
```

**Step 2: Launch training**

```bash
python scripts/train.py \
  --config configs/searchqa/default.yaml \
  --optimizer_model gpt-4o \
  --target_model gpt-4o-mini
```

You can use a strong model (gpt-4o) as the optimizer and a weaker model (gpt-4o-mini) as the target agent to maximize cost efficiency.

**Step 3: Collect the result**

After training, `ckpt/` contains `best_skill.md` — a 300–2,000 token optimized skill document. Drop it directly into your agent's system prompt.

**Zero inference-time overhead** — deployment is just a Markdown text file, no additional model calls required.

## My Assessment

**Methodologically rigorous, engineered for real deployment — worth serious attention.**

SkillOpt isn't solving "can AI write a skill?" (that was already solved). It's solving "how do you systematically and reproducibly make a skill *good*?" — a question that becomes critical as AI agents move from experiments into production.

**Practical value for developers:**
1. **No ML expertise needed**: the entire loop is API calls — no GPU, no gradients
2. **Readable output**: the skill is Markdown — reviewable, versionable, auditable
3. **Cross-model reuse**: optimize once on an expensive model, transfer to a cheaper one
4. **Active ecosystem**: gbrain, darwin-skill, and gbrain-evals already integrated (June 2026)

**Things to watch:**
- Optimization costs API tokens from both optimizer and target model
- Quality depends heavily on your task definition and validation set — garbage in, garbage out
- v0.1.0 is early; production stability is still accumulating

---

If you're using Claude Code, Codex, or any AI agent that supports skill files, SkillOpt is worth a serious half-day trial.

**GitHub:** [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)  
**arXiv paper:** 2605.23904 — SkillOpt: Executive Strategy for Self-Evolving Agent Skills  
**Project page:** https://aka.ms/skillopt  
**Install:** `pip install skillopt`
