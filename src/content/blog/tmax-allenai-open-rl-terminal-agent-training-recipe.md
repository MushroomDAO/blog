---
title: "TMax：AllenAI 最强开源终端 Agent RL 配方，9B 参数 Terminal-Bench 2.0 达 27%"
titleEn: "TMax: AllenAI's Strongest Open RL Recipe for Terminal Agents — 9B Hits 27% on Terminal-Bench 2.0"
description: "AllenAI 开源 TMax，目前最强的终端 Agent RL 训练配方。9B 参数模型在 Terminal-Bench 2.0 达到 27%，超越更大规模的闭源竞品。数据集 15K 任务，比此前最大终端 Agent 数据集大 2.5 倍，配套 SFT + DPPO RL 训练流程全套开源。"
descriptionEn: "AllenAI open-sources TMax, the strongest open RL recipe for terminal agents to date. A 9B-parameter model achieves 27% on Terminal-Bench 2.0, outperforming larger closed-source competitors. Includes a 15K-task dataset (2.5× the largest prior terminal-agent dataset) and a full SFT + DPPO RL training pipeline — all open-sourced."
pubDate: "2026-08-03"
updatedDate: "2026-08-03"
category: "Tech-News"
tags: ["Agent", "终端Agent", "RL训练", "AllenAI", "开源", "Terminal-Bench", "Qwen", "Mycelium"]
heroImage: "../../assets/images/tmax-allenai-open-rl-terminal-agent-training-recipe-banner.jpg"
---

*by Mycelium Protocol*

---

终端 Agent（Terminal-using agents）——让语言模型直接操作 Shell、跑命令、完成真实计算机任务——已经成为当前最热门的 LM 下游应用。但与这个方向的热度形成反差的是：**基于 RL 的训练方法在学术上几乎是空白**。

难 benchmark、缺数据、没有可复现的基础配方，是三道门槛。

AllenAI 的 **[TMax](https://github.com/hamishivi/tmax)**（Hamish Ivison 等）正面拆掉这三道门槛：开源完整数据集、训练代码、模型权重，并给出一个用 9B 参数在 Terminal-Bench 2.0 达到 **27%** 的配方——超越此前更大规模的闭源模型。

---

## 核心结果

TMax-9B（Qwen3.5-9B，RL 微调）在 Terminal-Bench 2.0 达到 **27%**，这个数字的含义：

- **只用 9B 参数**，超过先前更大规模的工作
- Terminal-Bench 2.0 是当前公认最严格的终端 Agent 基准之一（真实环境、程序化验证器）
- 配方简单：**outcome-only RL**（结果信号，不用 process reward），没有花哨的中间步骤奖励

---

## 四阶段配方

整个 TMax 系统围绕四个模块：

### 1. 数据生成（`rl_data/`）

数据是最关键的贡献之一。TMax 设计了一个**组合采样器**，把终端任务表示为若干正交维度的笛卡尔积：

- **难度控制**：在生成时显式标注任务难度，让模型训练样本的难度分布可调
- **人设多样化（Personas）**：让同一类任务在不同使用场景下变形，增加泛化性
- **验证器多样化**：程序化验证器覆盖更广的任务类型，避免单一验证模式的过拟合

四阶段流水线：

```
生成任务 → 用 LLM Agent pass@k 求解 → 分析通过率和语料平衡性 → 上传到 HuggingFace Hub
```

每个任务都被打包成自包含的 Apptainer/Docker 环境，附带程序化验证器——可以直接拿去让任何 Agent 跑评测，不需要重新搭环境。

**最终语料**：15K 任务（10K 传统任务 + 5K 多模态复杂任务），比此前最大的终端 Agent 数据集大 **2.5 倍**。

### 2. Agent（`Vanillux2Agent/`）

训练和评测用的 Agent 叫 **Vanillux2Agent**：

- 基于 LiteLLM，直接调用语言模型
- Prompt 框架来自 mini-SWE-agent（bash 工具 schema、submit 标记、格式错误恢复、输出截断）
- 通过 Harbor 的沙箱环境执行命令

设计哲学：**足够简单**。没有多余的 Orchestration 层，让模型能力而不是 Agent 框架复杂度决定最终表现。

### 3. 训练（`training/open-instruct/`）

基于 [open-instruct](https://github.com/allenai/open-instruct) 的 fork，修复了 Qwen3.5 的若干问题：

| 阶段 | 方法 | 说明 |
|------|------|------|
| SFT warm-start | Supervised Fine-Tuning | 用 pass@k 求解成功的轨迹做冷启动 |
| RL 训练 | DPPO（Distributed PPO） | outcome-only 奖励，不依赖中间过程信号 |

训练的模型系列：
- **TMax-4B**：Qwen3.5-4B + RL
- **TMax-9B**：Qwen3.5-9B + RL（主力模型，27% on TB 2.0）

### 4. 评测（`scripts/` + `beaker_configs/`）

评测基准：
- **Terminal-Bench 2.0**（主要基准）
- **TB-Lite**（轻量版）
- **SWE-bench**（代码修复）

本地复现最简路径：

```bash
# 用 vLLM 本地起服务
uvx vllm==0.19.1 serve allenai/tmax-9b \
  --served-model-name tmax-9b \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --tensor-parallel-size 8 --port 8008

# 用 Harbor 跑 Terminal-Bench
uv run harbor run \
  --dataset terminal-bench@2.0 \
  --env daytona \
  --agent-import-path Vanillux2Agent:Vanillux2Agent \
  --model openai/tmax-9b \
  --agent-kwarg api_base=http://localhost:8008/v1 \
  -k 5
```

---

## 开源内容

| 内容 | 位置 |
|------|------|
| 代码（数据生成 + 训练 + 评测） | [github.com/hamishivi/tmax](https://github.com/hamishivi/tmax) |
| 模型（TMax-4B、TMax-9B） | [HF: allenai/tmax](https://huggingface.co/collections/allenai/tmax) |
| 数据集（TMax-15K-Harbor） | [Harbor 注册表](https://hub.harborframework.com/datasets/tmax/TMax-15K-Harbor/latest) |
| 论文 | [arXiv 2606.23321](https://arxiv.org/abs/2606.23321) |

许可证：Apache 2.0。

---

## 为什么值得关注

**终端 Agent 的 RL 训练此前几乎没有可复现的开源基础**。TMax 填补了这个空缺，而且不是通过堆规模：9B 参数、简单的 outcome-only RL、一套可扩展的数据生成流程。

数据生成部分的设计——"把任务看作正交维度的笛卡尔积"——是一个值得借鉴的思路。它让语料的难度和类型分布变成了可控参数，而不是靠抓取人类数据碰运气。

对于想在终端 Agent 方向做研究的团队，TMax 是目前最好的起点：有基准数据、有可扩展的数据生成、有可复现的训练配方、有开源模型权重做 baseline 对比。

仓库：[github.com/hamishivi/tmax](https://github.com/hamishivi/tmax) · 论文：[arXiv 2606.23321](https://arxiv.org/abs/2606.23321) · 模型：[allenai/tmax](https://huggingface.co/collections/allenai/tmax)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## TMax: AllenAI's Open RL Recipe for Terminal Agents — 27% on Terminal-Bench 2.0 with 9B Parameters

*by Mycelium Protocol*

Terminal-using agents — language models that operate a shell, run commands, and complete real computer tasks — have become the most popular downstream application of LMs. Yet despite this popularity, RL-based training for terminal agents remains largely uncharted academic territory. The barriers: difficult benchmarks, scarce data, and no reproducible baseline recipe.

**[TMax](https://github.com/hamishivi/tmax)** (AllenAI, Hamish Ivison et al.) dismantles all three: open-source dataset, training code, and model weights — plus a recipe that achieves **27% on Terminal-Bench 2.0 with only 9B parameters**, outperforming larger models from prior work.

### Core Results

TMax-9B (Qwen3.5-9B, RL fine-tuned) achieves **27% on Terminal-Bench 2.0**:

- Only 9B parameters, outperforming larger prior models
- Terminal-Bench 2.0 is the field's most rigorous benchmark (real environments, programmatic verifiers)
- **Outcome-only RL** — no process reward, no intermediate step supervision; just final task success

### The Four-Stage Recipe

**1. Data Generation (`rl_data/`)**

The data contribution may be the most important. TMax represents terminal tasks as a **Cartesian product of orthogonal axes**, making the corpus composition a controllable variable rather than a fixed artifact of data collection:

- **Difficulty control**: explicit difficulty tagging at generation time
- **Persona diversification**: the same task class varies across usage contexts for better generalization
- **Verifier diversification**: programmatic verifiers across diverse task types prevent overfitting to any single verification pattern

Four-stage pipeline:
```
generate_tasks → solve at pass@k → analyze → upload to HuggingFace Hub
```

Every task ships as a self-contained Apptainer/Docker environment with a programmatic verifier — usable out of the box, no rebuild required.

**Final corpus**: 15K tasks (10K traditional + 5K intricate multi-modal), **2.5× larger** than the largest prior terminal-agent dataset.

**2. Agent (`Vanillux2Agent/`)**

The training and evaluation agent, **Vanillux2Agent**, is deliberately minimal:

- LiteLLM-based, calls the language model directly
- Prompt framework from mini-SWE-agent (bash tool schema, submit marker, format-error recovery, output truncation)
- Executes commands through Harbor sandboxes

Philosophy: keep the agent simple so that model capability — not agent orchestration complexity — determines performance.

**3. Training (`training/open-instruct/`)**

Fork of [open-instruct](https://github.com/allenai/open-instruct) with Qwen3.5 fixes:

| Stage | Method | Notes |
|-------|--------|-------|
| SFT warm-start | Supervised Fine-Tuning | Successful pass@k trajectories as cold-start data |
| RL | DPPO (Distributed PPO) | Outcome-only reward signal |

Models released:
- **TMax-4B**: Qwen3.5-4B + RL
- **TMax-9B**: Qwen3.5-9B + RL (main model, 27% on TB 2.0)

**4. Evaluation**

Benchmarks: Terminal-Bench 2.0, TB-Lite, SWE-bench.

Quick local eval:
```bash
# Serve with vLLM
uvx vllm==0.19.1 serve allenai/tmax-9b \
  --enable-auto-tool-choice --tool-call-parser qwen3_xml \
  --tensor-parallel-size 8 --port 8008

# Run Terminal-Bench via Harbor
uv run harbor run \
  --dataset terminal-bench@2.0 \
  --agent-import-path Vanillux2Agent:Vanillux2Agent \
  --model openai/tmax-9b \
  --agent-kwarg api_base=http://localhost:8008/v1 \
  -k 5
```

### Open-Source Checklist

| Artifact | Location |
|----------|----------|
| Code (data gen + training + eval) | [github.com/hamishivi/tmax](https://github.com/hamishivi/tmax) |
| Models (TMax-4B, TMax-9B) | [HF: allenai/tmax](https://huggingface.co/collections/allenai/tmax) |
| Dataset (TMax-15K-Harbor) | [Harbor registry](https://hub.harborframework.com/datasets/tmax/TMax-15K-Harbor/latest) |
| Paper | [arXiv 2606.23321](https://arxiv.org/abs/2606.23321) |

License: Apache 2.0.

### Why This Matters

**RL training for terminal agents had no reproducible open baseline.** TMax closes that gap — and it does so without scaling tricks: 9B parameters, simple outcome-only RL, a data generation design that makes corpus composition a tunable parameter rather than a fixed scrape artifact.

The compositional sampler approach is worth borrowing beyond this specific project: treating tasks as products of orthogonal axes gives you explicit control over difficulty distribution and task-type coverage, which is exactly what you need when training with RL.

For teams working on terminal agents, TMax is the strongest available starting point: reproducible benchmark data, scalable data generation, open training recipe, and open model weights for comparison.

Repository: [github.com/hamishivi/tmax](https://github.com/hamishivi/tmax) · Paper: [arXiv 2606.23321](https://arxiv.org/abs/2606.23321) · Models: [allenai/tmax](https://huggingface.co/collections/allenai/tmax)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
