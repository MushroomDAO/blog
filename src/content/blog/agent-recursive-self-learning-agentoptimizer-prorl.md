---
title: "Agent 如何递归地学会学习：AgentOptimizer 与 ProRL 的完整技术栈"
titleEn: "How Agents Learn to Learn Recursively: AgentOptimizer + ProRL's Complete Stack"
description: "NVIDIA Research 张少坤在智源大会分享两篇论文：AgentOptimizer 把函数当可学习权重、ProRL Agent 把 Rollout 变成服务——两者合起来是一个让 LLM Agent 从自身经验中递归自我提升的完整技术栈。GPU 利用率从 42% 升至 78%，SWE-Bench 8B 模型提升 88%。"
descriptionEn: "NVIDIA Research's Shaokun Zhang presented at BAAI Conference: AgentOptimizer treats functions as learnable weights; ProRL Agent turns rollout into a decoupled API service. Together they form a complete stack for recursive agent self-improvement, boosting GPU utilization from 42% to 78% and SWE-Bench 8B score by 88%."
pubDate: "2026-06-13"
updatedDate: "2026-06-13"
category: "Research"
tags: ["AI Agent", "强化学习", "递归自学习", "NVIDIA", "智源大会", "AgentOptimizer", "ProRL", "LLM训练"]
heroImage: "../../assets/banner-personal-growth-ai-skills.jpg"
---

> **BLUF**：NVIDIA Research 的张少坤在 2026 智源大会 AI 自进化会场分享了两篇论文——**AgentOptimizer**（arXiv:2402.11359）和 **ProRL Agent**（arXiv:2603.18815）。前者解决"单个 Agent 如何在不改动 LLM 权重的前提下自我优化"，后者解决"如何把 RL 训练扩展到大规模多 Agent 场景"。两者合起来，是目前最完整的 Agent 递归自学习技术栈。

---

## 这项研究在解决什么问题？

理解这两篇论文，先要理解它们想打破的五道墙：

**1. Agent 的能力天花板是人画的**
当前 LLM Agent 的能力高度依赖人类手工设计的函数、工具、提示词与工作流。Agent 无法自行迭代改进，每一次升级都需要人介入。

**2. RL 基础设施无法跨框架迁移**
即使引入强化学习让 Agent 从环境反馈中学习，现有的 RL 训练基础设施将探索循环与训练循环紧耦合，难以跨框架迁移和大规模扩展。

**3. 轨迹数据采集成本极高**
Agent 在长程多轮任务中的探索轨迹数据采集成本极高，且不同 Agent 框架的内部工具调用细节各异，缺乏统一的轨迹捕获机制。

**4. GPU 大量空转**
训练循环和探索循环耦合，导致 GPU 资源利用率低——长任务跑完之前 GPU 只能空转等待。

**5. 缺少从单 Agent 到大规模 RL 的完整栈**
需要一个从单 Agent 自优化到大规模 Agent 强化学习基础设施的完整技术栈，让 Agent 能够从自身与环境交互的经验中递归地自我提升。

这五个问题，两篇论文分别从不同层次给出了答案。

---

## 论文一：AgentOptimizer — 把「函数」当成可学习的权重

**论文**：Offline Training of Language Model Agents with Functions as Learnable Weights
**链接**：https://arxiv.org/abs/2402.11359
**作者**：Shaokun Zhang, Jieyu Zhang, Jiale Liu, Linxin Song, Chi Wang, Ranjay Krishna, Qingyun Wu

### 核心范式转换

传统的 Agent 改进思路是：调整 LLM 权重（微调）或手工调整提示词。两种方法各有局限——前者需要模型访问权限，后者需要人工介入。

AgentOptimizer 提出了第三条路：**把函数（Functions）本身当作可学习的参数来优化。**

灵感来自一个朴素的类比：人类持续创造工具来适应任务，而不是改变自身的大脑结构。Agent 也应该如此——不是修改自身的"神经网络"，而是进化自己使用的"工具集"。

### 技术机制

整个训练过程有三个关键设计：

**1. 函数即权重（Functions as Parameters）**
Agent 的函数库不再是固定的，而是被视为可优化的参数空间。LLM 在每轮迭代后分析自身的失败案例，生成新的函数版本或修改现有函数的实现逻辑。

**2. 回滚机制（Rollback）**
如果新生成的函数版本导致性能下降，系统会自动回退到上一个有效版本。这保证了训练过程的单调性——不会越练越差。

**3. 提前停止（Early Stopping）**
当函数更新带来的增益低于阈值时，训练终止，避免过度优化和资源浪费。

### 关键优势

这个范式对**黑盒 LLM** 特别实用——无论是 GPT-4、Claude 还是企业内部不开放权重的模型，都可以用 AgentOptimizer 来提升 Agent 能力，因为整个优化过程完全通过 API 交互完成，不需要任何模型权重访问权限。

实验结果显示：Agent 训练范式能够显著改善代表性 LLM Agent 在各类下游任务中的表现，并且习得的函数具备跨领域迁移性——在任务 A 上学到的函数改进，可以迁移到结构相似的任务 B。

---

## 论文二：ProRL Agent — 把「Rollout」变成一个服务

**论文**：ProRL Agent: Rollout-as-a-Service for RL Training of Multi-Turn LLM Agents
**链接**：https://arxiv.org/abs/2603.18815
**作者**：Hao Zhang, Mingjie Liu, Shaokun Zhang, Songyang Han, Jian Hu et al.（NVIDIA Research）

### 核心思想：解耦

现有 RL Agent 框架的最大问题是**紧耦合**：轨迹生成（Rollout）和模型训练（Training）混在一个进程里。这意味着：
- GPU 在等待长任务完成时完全空转
- 换一个 Agent 框架就要重写训练代码
- 没有统一的轨迹格式，无法跨框架复用数据

ProRL Agent 的解法是**Rollout-as-a-Service（轨迹生成即服务）**：把轨迹生成从训练循环里完全剥离出来，变成一个独立的 HTTP API 服务。

### 三阶段异步流水线

```
INIT  →  RUN  →  EVAL
(容器启动)  (多轮推理)  (奖励计算)
```

三个阶段完全异步、独立运行：
- 当第一个任务在 EVAL 阶段计算奖励时
- 第二个任务可能正在 RUN 阶段做多轮推理
- 第三个任务已经在 INIT 阶段准备容器

这个流水线设计让 GPU 几乎没有空转时间。

### 关键技术细节

**沙箱环境（SingularityRuntime）**
使用无需 root 权限的 Singularity 容器，兼容 HPC Slurm 集群环境。每个容器实例分配独立的 loopback IP，完全隔离，支持 `--fakeroot` 模拟 root 权限。

**可插拔任务抽象（AgentHandler）**
三个生命周期方法：
- `init()`：环境准备
- `run()`：Agent 推理循环
- `eval()`：奖励信号生成

新任务类型直接实现这三个接口即可，不需要修改任何训练代码。

**工具层优化**
三项关键性能优化：
- 用 ptyprocess 伪终端替换 tmux，降低 Bash 工具延迟
- 直接调用 IPython 内核 API，消除 Jupyter 网络往返开销
- 进程间通信改用 Unix Domain Socket（UDS）替换 TCP 回环，降低 IPC 延迟

**Token-in/Token-out 轨迹格式**
轨迹全程传递 token ID，避免重新 tokenize 引入的漂移问题。每条消息携带 `input_ids`、`output_ids` 和 `logprobs`，多轮对话直接拼接原始 token 序列。

### 性能数据

**GPU 利用率提升**

| 优化项 | GPU 利用率 |
|---|---|
| 基准（无优化） | 42% |
| + 负载均衡 | 65% |
| + 负载均衡 + 无效任务清理 | 78% |

**SWE-Bench Verified 代码工程任务**

| 模型规模 | 基线 | ProRL Agent | 提升 |
|---|---|---|---|
| 4B | 14.8% | 21.2% | **+43%** |
| 8B | 9.6% | 18.0% | **+88%** |
| 14B | 15.4% | 23.6% | **+53%** |

**跨领域验证**

| 任务类型 | 初始 | 训练后 |
|---|---|---|
| STEM Agent（平均奖励） | 0.20 | **0.65** |
| 数学 Agent（AMC Pass@1） | 0.40 | **0.90** |
| 代码 Agent（Codeforces Pass@1） | 0.23 | **0.42** |

扩展性方面：在 8 张 H100 GPU 上，软件工程任务的吞吐量达到 0.37 instance/sec，并实现了近线性扩展。系统已集成进 NVIDIA NeMo Gym 开源发布。

---

## 两篇论文如何构成一个完整的栈？

单独看，AgentOptimizer 是"单 Agent 自我优化"，ProRL Agent 是"大规模 Agent RL 基础设施"。合在一起，它们覆盖了递归自学习的完整路径：

```
Agent 与任务交互
      ↓
AgentOptimizer：LLM 分析失败案例 → 更新函数库（单 Agent 层）
      ↓
函数改进后，新版 Agent 重新与环境交互
      ↓
ProRL Agent：大规模采集轨迹，解耦训练（基础设施层）
      ↓
RL 训练更新模型策略
      ↓
更强的 Agent 继续与任务交互（递归）
```

张少坤的研究叙事是一条清晰的线：从 2024 年的 AgentOptimizer（**函数即权重，无需改模型**）到 2026 年的 ProRL Agent（**轨迹即服务，无需耦合框架**），每一步都在拆除限制 Agent 自我进化的一堵墙。

---

## 对 AI Agent 开发者的启示

**1. 工具优化比提示词工程更可持续**
AgentOptimizer 的实验证明，系统性地优化函数库比反复调整提示词有更好的学习曲线和更强的迁移性。如果你在为某个 Agent 持续调优，考虑将优化目标从"更好的提示词"转向"更好的工具集"。

**2. 解耦是 Agent RL 的基础设施哲学**
ProRL Agent 的最大贡献不是性能数据，而是它确立了一个工程范式：**探索（Rollout）和训练（Training）必须分离**。这和微服务架构的理念如出一辙——解耦才能独立扩展，独立扩展才能真正工业化。

**3. 递归性是 Agent 与传统 ML 模型的本质区别**
传统 ML 模型训练一次、部署使用。Agent 的范式是：**运行即学习，交互即数据**。AgentOptimizer + ProRL 提供的技术栈，让这种递归性从概念变成了可工程化的系统。

---

> 论文原文（请手动访问）：
> AgentOptimizer：https://arxiv.org/abs/2402.11359
> ProRL Agent：https://arxiv.org/abs/2603.18815
> NVIDIA NeMo Gym（ProRL 开源实现）：https://github.com/NVIDIA/nemo-rl

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: NVIDIA Research's Shaokun Zhang presented two papers at the BAAI 2026 Conference AI Self-Evolution track — AgentOptimizer and ProRL Agent. Together they form a complete recursive self-learning stack: one optimizes agent functions without touching LLM weights; the other decouples trajectory generation from RL training at scale. GPU utilization rises from 42% to 78%. SWE-Bench 8B model improves by 88%.

---

## The 5 Problems They Set Out to Solve

1. LLM Agent capabilities are bottlenecked by human-designed functions, tools, and prompts — agents can't improve themselves
2. Existing RL infrastructure tightly couples exploration loops with training loops — hard to migrate across frameworks
3. Trajectory collection in long multi-turn tasks is expensive; no unified capture mechanism across frameworks
4. Coupling causes GPU idle time — the GPU waits while long rollouts run
5. No complete stack from single-agent self-optimization to large-scale agent RL

---

## Paper 1: AgentOptimizer — Functions as Learnable Weights

**arXiv: 2402.11359** | Shaokun Zhang et al.

The key insight: instead of fine-tuning the LLM or hand-tuning prompts, treat the agent's **function library as the learnable parameter space**.

The LLM analyzes its own failure cases and rewrites its functions. Two guardrails keep training stable: a **rollback mechanism** (revert if performance drops) and **early stopping** (halt when gains plateau).

This works on black-box LLMs — no weight access needed, just API calls. Learned function improvements also transfer across structurally similar task domains.

---

## Paper 2: ProRL Agent — Rollout as a Service

**arXiv: 2603.18815** | Hao Zhang, Shaokun Zhang et al. (NVIDIA Research)

The key insight: **decouple rollout generation from RL training** by exposing it as an HTTP service.

**Three-stage async pipeline**: INIT (container setup) → RUN (multi-turn inference) → EVAL (reward scoring). All three stages run concurrently across different jobs — no pipeline stalls.

**Performance gains**:
- GPU utilization: 42% → 78%
- SWE-Bench (8B model): 9.6% → 18.0% (+88%)
- Math AMC Pass@1: 0.4 → 0.9
- Near-linear throughput scaling on 8× H100

The system uses rootless Singularity containers (HPC-compatible), a pluggable `AgentHandler` interface (new task types need just 3 method implementations), and a token-ID-native trajectory format that eliminates re-tokenization drift.

Integrated into NVIDIA NeMo Gym and open-sourced.

---

## How They Form a Complete Recursive Stack

```
Agent ↔ Environment interaction
   ↓
AgentOptimizer: LLM rewrites function library  [single-agent layer]
   ↓
Improved agent re-interacts with environment
   ↓
ProRL Agent: large-scale rollout collection, decoupled training  [infra layer]
   ↓
RL updates model policy
   ↓
Stronger agent → repeat  [recursion]
```

---

## Three Takeaways for Agent Builders

1. **Tool optimization compounds better than prompt tuning** — AgentOptimizer shows better learning curves and stronger transfer when the optimization target is the function library, not the prompt.

2. **Decouple exploration from training** — ProRL's architectural lesson mirrors microservices: separate what scales differently. Rollout is I/O-bound; training is GPU-bound. They shouldn't share a process.

3. **Agents are recursive by nature** — unlike static ML models, agents that can improve their own tools and learn from their own trajectories compound in capability over time. AgentOptimizer + ProRL makes this engineering-grade, not just conceptual.

---

> Papers:
> AgentOptimizer: https://arxiv.org/abs/2402.11359
> ProRL Agent: https://arxiv.org/abs/2603.18815
> NVIDIA NeMo Gym: https://github.com/NVIDIA/nemo-rl

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
