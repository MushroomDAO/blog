---
title: "Agent Lightning：微软研究院 3500 行代码，让任何 AI Agent 都能用真实环境做强化学习"
titleEn: "Agent Lightning: Microsoft Research's 3,500-Line RL Framework for Training Any AI Agent in Real Environments"
description: "microsoft/agent-lightning，MIT 开源，Python，18K stars。三个组件（Trainer/API Gateway/Rollout Controller），Agent 代码零改动，用真实工具链训练。Qwen3.5-9B 只用 6K 样本，SWE-bench Verified 从 41.8% 涨到 56.4%（+14.6pp）。支持 AutoGen、LangChain、OpenAI Agents SDK 及任意自定义 Agent。"
descriptionEn: "microsoft/agent-lightning, MIT open source, Python, 18K stars. Three components (Trainer/API Gateway/Rollout Controller), zero agent code changes, trains with real tool harnesses. Qwen3.5-9B with only 6K samples improves SWE-bench Verified from 41.8% to 56.4% (+14.6pp). Supports AutoGen, LangChain, OpenAI Agents SDK, and any custom agent."
pubDate: "2026-09-17"
updatedDate: "2026-09-17"
category: "Tech-Experiment"
tags: ["open-source", "reinforcement-learning", "AI-agent", "microsoft-research", "RL-training", "SWE-bench", "MIT", "Python"]
heroImage: "../../assets/images/agent-lightning-microsoft-research-rl-framework-train-agents-real-harness-banner.jpg"
---

> 📌 开源仓库：https://github.com/microsoft/agent-lightning
> 技术报告：https://arxiv.org/abs/2608.17528
> 原始论文：https://arxiv.org/abs/2508.03680
> License：MIT | Language：Python | Stars：18.2K

---

大多数 AI Agent 的问题是"训完就定型了"——你部署了一个 Agent，它用工具、执行代码、操作浏览器，但每次犯的同一类错误，它学不了，因为传统 RL 训练要求你大改代码甚至重写整个架构。结果是：Agent 跑在真实工具链里，训练却只能在模拟环境里，两套系统脱节，改 Agent 就得改训练代码，没人愿意做。

**Agent Lightning 要解决的就是这个脱节**。核心主张很简单：Agent 代码一行不改，在真实工具链、真实代码环境、真实 Harness 里跑，训练系统全程透明地在后面收集数据、更新模型。

这是微软研究院 2025 年 6 月开源、2026 年 8 月完整重构到 v1.0 的项目，~3500 行 Python，MIT 协议，目前 18.2K stars。

---

## 架构：三个组件，各司其职

v1.0 的架构用三个轻量组件完成整个 RL 训练循环：

```
Trainer               ← 运行 verl + vLLM，构建训练样本，更新策略
    ↑
API Gateway           ← 代理所有模型请求，捕获交互数据
    ↑
Rollout Controller    ← 在本地或 Kubernetes Job 里跑 Agent
    ↑
你的 Agent（不改任何代码）← 用真实工具/Harness/环境执行任务
```

关键设计是 **API Gateway 作为透明代理**：你的 Agent 仍然向 OpenAI 兼容的接口发请求，Gateway 拦截这些请求，一方面把请求转发给 vLLM 上正在训练的模型，另一方面把请求+响应记录下来变成训练轨迹。Agent 感知不到任何变化，工具调用、上下文、控制流一切照常。

Rollout Controller 负责批量启动 Agent，可以本地跑，也支持原生 Kubernetes Job（不依赖外部 sandbox 服务）。Trainer 持续从 Gateway 收数据，用 verl + vLLM 做 PPO 或 GRPO 更新，新的模型权重自动热更新到 Gateway 的推理端。

---

## 零改动的含义

"Agent 代码零改动"不是口号，是架构设计的直接结果：

- Agent 调的是 OpenAI 兼容 API，Gateway 就是一个 drop-in 替换的 API endpoint
- 你的 Agent 用 AutoGen 写的、用 LangChain 写的、用 OpenAI Agents SDK 写的，还是自己 `requests.post` 写的，都一样接
- 工具调用、Memory、多 Agent 协作流程、中间状态——全部保持原样在训练循环里

这和之前的 Agent RL 方案（把 Agent 逻辑改成 MDP、换掉推理后端、重写工具接口）是完全不同的路数：**训练系统去适应 Agent，而不是 Agent 去适应训练系统**。

---

## 关键结果：SWE-bench +14.6pp

v1.0 的编程 Agent 训练示例是目前最具说服力的数字：

- 基础模型：Qwen3.5-9B
- 训练数据：**仅 6K 样本**
- SWE-bench Verified：**41.8% → 56.4%**，提升 14.6 个百分点
- 整套 pipeline 开源：数据清洗、奖励黑客预防、训练脚本全部放出

除编程 Agent 外，官方还在三个领域验证了效果：

| 领域 | 例子 |
|------|------|
| 搜索推理 | Search-R1，多轮检索+推理 |
| 沙盒通用 Agent | LLM-in-Sandbox，计算机操作+代码执行工具 |
| 编程 Agent | Coding Agent，仓库测试驱动 |

三个领域纯 RL（不做 SFT 热启动）都有显著提升。

---

## 安装与使用

**环境要求**：CUDA 机器（GPU 用于训练/推理），`uv`，Python。CPU 单机可以跑 Calc-X / GSM8K 示例（验证流程，1 张 GPU 起步）。

```bash
git clone https://github.com/microsoft/agent-lightning.git
cd agent-lightning
uv sync
bash scripts/setup_verl.sh 0.8.0 cu130   # 对应 CUDA 13.0
```

然后参考官方文档的 Quick Start 走一遍本地首跑，确认三个组件都能启动，再接入自己的 Agent 和任务。

**官方示例由易到难**：
- `Calc-X`：AutoGen + MCP 计算器，1 张 GPU，验证整体流程
- `GSM8K`：小学数学，最小 POC
- `ScienceWorld`：文本环境科学任务
- `Search-R1`：多轮检索推理
- `LLM-in-Sandbox`：通用工具 Agent
- `Coding Agent`：SWE-bench 风格编程 Agent

---

## 社区生态

项目开源 15 个月，已有几个值得关注的社区项目：

**腾讯 Youtu-Agent**：基于 Agent Lightning 的修改分支，验证了 128 GPU 规模的稳定收敛，数学/代码/搜索能力均有提升，发了详细的训练 recipe。

**DeepWerewolf**：用 AgentScope + Agent Lightning 训练中文狼人杀 Agent 的案例研究，是少见的社交游戏 RL 训练实验。

**AgentFlow（Stanford）**：结合 planner/executor/verifier/generator 多 Agent 架构和 Flow-GRPO 算法，针对长程稀疏奖励任务。

这些社区项目说明框架的"零改动接入"承诺在真实场景里基本兑现了——腾讯的 128 GPU 规模尤其有说服力。

---

## 和其他 Agent RL 方案的区别

目前做 Agent RL 训练的方案大致有三类：

1. **模拟环境训练**（传统游戏/棋类 RL）：环境可控，但和真实 Agent 部署脱节
2. **改造 Agent 代码适配训练**：要求 Agent 用特定框架、特定接口，工程成本高
3. **Agent Lightning 的路子**：训练系统作为透明层插入，Agent 框架无关，用真实 Harness 收集数据

第三条路的代价是系统复杂度和对 verl/vLLM 生态的依赖，适合已经有稳定 Agent Harness、想提升模型能力的场景，**不适合**还在摸索 Agent 架构的早期阶段。

---

## 总结

Agent Lightning 解决了一个很实际的问题：**让已有 Agent 能学习，而不是为了学习重写 Agent**。3500 行代码、三组件架构、API 代理拦截——设计朴素，但 SWE-bench +14.6pp 的结果说明路子是对的。

腾讯在 128 GPU 上稳定跑通，Stanford 有团队基于它发论文，说明这不只是一个 demo 级框架。如果你有跑在真实工具链上的 Agent，想让它在使用过程中越来越聪明，Agent Lightning 是目前最低接入成本的选择之一。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/microsoft/agent-lightning
> Technical report: https://arxiv.org/abs/2608.17528
> Original paper: https://arxiv.org/abs/2508.03680
> License: MIT | Language: Python | Stars: 18.2K

---

Most AI agents have a "trained once, static forever" problem. You deploy an agent — it uses tools, runs code, operates a browser — but it can't learn from repeated mistakes because traditional RL training requires extensive code changes or full architecture rewrites. The result: agents run in real tool chains while training happens in simulated environments, and the two systems never talk. Change the agent and you break the training setup. Nobody does it.

**Agent Lightning exists to close this gap.** The core claim is direct: zero changes to agent code, trained with the real tool chain, real code environments, real harness — the training system sits transparently behind and collects data without the agent knowing.

This is a project from Microsoft Research Asia-Shanghai, open-sourced in June 2025, completely refactored into v1.0 in August 2026. ~3,500 lines of Python, MIT licensed, 18.2K stars.

---

## Architecture: Three Components, Clean Separation

v1.0 runs the entire RL training loop through three lightweight components:

```
Trainer               ← Runs verl + vLLM, builds training samples, updates policy
    ↑
API Gateway           ← Proxies model requests, captures interaction data
    ↑
Rollout Controller    ← Runs agents locally or as Kubernetes Jobs
    ↑
Your Agent (zero code changes) ← Uses real tools/harness/environment to do tasks
```

The key design is the **API Gateway as a transparent proxy**: your agent still sends requests to an OpenAI-compatible endpoint; the Gateway intercepts, forwards to the vLLM instance running the training model, and records requests plus responses as training trajectories. The agent sees nothing different — tool calls, context, control flow all stay intact.

The Rollout Controller launches agents in batch. Kubernetes Jobs are supported natively with no external sandbox dependency. The Trainer continuously pulls data from the Gateway, runs PPO or GRPO updates via verl + vLLM, and hot-updates new model weights into the inference-side of the Gateway.

---

## What "Zero Code Changes" Actually Means

This isn't marketing language; it's a direct result of the architecture:

- Agents call an OpenAI-compatible API; the Gateway is a drop-in replacement endpoint
- AutoGen agents, LangChain agents, OpenAI Agents SDK agents, custom `requests.post` agents — all plug in the same way
- Tool calls, memory, multi-agent workflows, intermediate state — everything runs as-is inside the training loop

This is fundamentally different from previous Agent RL approaches that required reformulating agent logic as MDPs, replacing inference backends, or rewriting tool interfaces. **The training system adapts to the agent, not the other way around.**

---

## Key Result: SWE-bench +14.6pp

The v1.0 coding agent training example is the most compelling number in the project:

- Base model: Qwen3.5-9B
- Training data: **only 6K samples**
- SWE-bench Verified: **41.8% → 56.4%**, +14.6 percentage points
- Full pipeline open-sourced: data cleaning, reward-hacking prevention, training scripts all included

Beyond coding, three domains were validated:

| Domain | Example |
|--------|---------|
| Search reasoning | Search-R1, multi-turn retrieval + reasoning |
| Sandbox general agent | LLM-in-Sandbox, computer use + code execution |
| Coding agent | Coding Agent, repo-test driven |

All three show substantial improvements from pure RL without SFT warm-start.

---

## Installation

**Requirements**: CUDA machine (GPU for training/inference), `uv`, Python. CPU single-machine runs the Calc-X/GSM8K examples (flow verification; 1 GPU minimum for full training).

```bash
git clone https://github.com/microsoft/agent-lightning.git
cd agent-lightning
uv sync
bash scripts/setup_verl.sh 0.8.0 cu130   # for CUDA 13.0
```

Follow the official Quick Start to verify all three components start, then connect your own agent and task.

**Official examples from simple to complex:**
- `Calc-X`: AutoGen + MCP calculator, 1 GPU, full-loop verification
- `GSM8K`: Grade-school math, smallest POC
- `ScienceWorld`: Text-based science environment
- `Search-R1`: Multi-turn retrieval reasoning
- `LLM-in-Sandbox`: General tool agent
- `Coding Agent`: SWE-bench-style coding agent

---

## Community Ecosystem

The project has been open for 15 months and has produced several notable downstream projects:

**Tencent Youtu-Agent**: Built on a modified Agent Lightning branch, verified stable convergence at 128-GPU scale on math, code, and search tasks with a published training recipe.

**DeepWerewolf**: A case study of RL training for Chinese Werewolf (狼人杀) built with AgentScope and Agent Lightning — a rare example of social game agent RL.

**AgentFlow (Stanford)**: Combines a planner/executor/verifier/generator multi-agent architecture with Flow-GRPO for long-horizon, sparse-reward tasks.

Tencent's 128-GPU scale validation is particularly credible evidence that the zero-modification promise holds in real production settings.

---

## How It Compares to Other Agent RL Approaches

Current approaches to Agent RL training fall into roughly three categories:

1. **Simulated environment training** (games, chess): Controlled but disconnected from real agent deployments
2. **Adapt agent code to fit training**: Requires specific frameworks and interfaces; high engineering cost
3. **Agent Lightning's approach**: Training as a transparent layer; framework-agnostic; data collected from the real harness

The tradeoff for option 3 is system complexity and dependency on the verl/vLLM ecosystem. It's a good fit for teams with a stable agent harness who want to improve model capabilities — **not** the right tool while still figuring out agent architecture.

---

## Summary

Agent Lightning solves a concrete problem: **making existing agents learnable without rewriting them for training.** 3,500 lines of code, three-component architecture, API proxy interception — the design is simple, and SWE-bench +14.6pp says it works.

Tencent runs it stably at 128 GPUs. Stanford has research groups publishing on top of it. This isn't a demo framework. If you have an agent running on a real tool chain and want it to get smarter through use, Agent Lightning is one of the lowest-friction entry points available right now.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
