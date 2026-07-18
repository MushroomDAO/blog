---
title: "2026 年实时强化学习 Agent 全景：从 OpenClaw-RL 到 Cursor Composer 2.5，模型开始在使用中自我进化"
titleEn: "Real-Time RL Agents in 2026: From OpenClaw-RL to Cursor Composer 2.5 — Models That Evolve While You Use Them"
description: "实时递归学习（Real-time RL）正在把 AI Agent 从「静态模型」变成「用得越多越聪明的系统」。本文综合 OpenClaw-RL 技术报告、RLAnything、ScaleCUA、RLVP 等 2026 年最新研究，拆解这个范式的核心机制、当前 SOTA，以及开发者现在就能落地的实践方案。"
descriptionEn: "Real-time recursive learning (real-time RL) is turning AI agents from static models into systems that get smarter the more they're used. This survey covers OpenClaw-RL, RLAnything, ScaleCUA, RLVP, AIDE 2, and Cursor Composer 2.5 — the core mechanics, current SOTA, and what developers can actually deploy today."
pubDate: "2026-07-18"
updatedDate: "2026-07-18"
category: "Tech-Experiment"
tags: ["强化学习", "AI Agent", "RLVR", "在线学习", "OpenClaw-RL", "Cursor", "研究综述", "实时学习"]
heroImage: "../../assets/images/realtime-rl-agent-2026-banner.jpg"
---

> **核心主题**：Real-time Recursive Learning（实时递归学习）—— AI Agent 在推理时同步学习  
> **覆盖系统**：OpenClaw-RL · RLAnything · ScaleCUA · RLVP · AIDE 2 · Cursor Composer 2.5  
> **时间范围**：2026 年 1 月 — 7 月

---

## 一句话说清楚这件事是什么

2025 年之前的 AI Agent 是「训练一次、永远静止」——你跟它说了 1000 次「这个输出不对」，它不会从对话中学习任何东西。

2026 年，一批研究和产品正在打破这个假设：**Agent 可以在和你交互的同时，实时把这些交互转化为梯度，持续优化自己的策略**。这就是 Real-time RL（实时强化学习）的核心想法，也叫 Real-time Recursive Learning 或 Online Agentic RL。

这不是「每隔几个月重新训练一次」，而是**对话结束后几秒钟内，模型就从这次对话里更新了权重**。

---

## 为什么 2026 年是分水岭

两件事同时成熟了：

**技术侧**：RLVR（从可验证奖励中做强化学习）被证明可以在 agentic 场景工作。Agent 的「下一步状态」——用户回复、工具返回值、终端输出、GUI 状态变化——天然就是一个可提取奖励信号的 next-state signal。

**工程侧**：异步解耦架构让推理、数据收集、奖励评估、梯度更新四个环节可以并行运行，不再互相阻塞。服务模型的同时训练它，这件事在工程上变成可行的了。

---

## 核心系统一：OpenClaw-RL

**GitHub**: [Gen-Verse/OpenClaw-RL](https://github.com/Gen-Verse/OpenClaw-RL) · arXiv:2603.10165  
**发布时间**：2026/3/10（HuggingFace Daily Papers #1）  
**作者**：Wang Yinjie, Chen Xuyang 等，清华大学 + Princeton

### 架构

OpenClaw-RL 是目前最完整的实时 agentic RL 框架。它的核心设计是把一个 RL 系统拆成四个完全异步的循环：

```
推理服务（Serving）         ← 模型以 OpenAI 兼容 API 对外服务
      ↕（不阻塞）
轨迹收集（Rollout）         ← 拦截 HTTP 请求，记录多轮对话轨迹
      ↕（不阻塞）
奖励评估（PRM/Judge）       ← 异步评估每个轮次的 next-state signal
      ↕（不阻塞）
策略训练（Training）        ← 持续把 ready 的样本提交给 trainer
```

**关键发现**：每次 Agent 交互都天然存在一个 next-state signal——用户的下一条消息、工具的返回值、终端的 stdout/stderr。这些信号以前被丢掉，OpenClaw-RL 把它们捡回来作为训练信号。

### 三种优化方法

**Binary RL（GRPO）**：Process Reward Model 对每个轮次打分 → GRPO advantage estimation → PPO-style clipped loss。最简单，覆盖面最广。

**On-Policy Distillation（OPD）**：当下一个状态（比如用户的纠正回复）包含有用的 hindsight 信息，judge 模型提取出一条文字 hint，用 hint 增强 prompt 构造 teacher distribution，用 log-prob 差作为 token 级的方向性 advantage。比纯标量奖励信息密度高得多。

**Hybrid（组合方法）**：把 Binary RL 的广覆盖 + OPD 的信息密度组合进一个训练 recipe，在清华大学 Slime 框架上实现。实验显示组合优于任何单一方法。

### 核心数学：overlap-guided hint selection

OPD 的一个关键挑战是 teacher-student mismatch：如果 teacher 的分布和 student 差太多，蒸馏信号会噪声很大。OpenClaw-RL 提出 overlap-guided hint selection：**选那条让 teacher 分布与 student top-k token 重叠最大的 hint**，再配合 log-prob-diff clip 限制每个 token 的 advantage 幅度。

### 两个 Track

**Track 1（个人 Agent 优化）**：把自己托管的模型（比如 Qwen3-4B/9B/27B）挂在 OpenClaw 后面，所有对话自动进入 RL 训练管线。硬件要求 8× GPU。

**Track 2（通用 Agent RL）**：同一个异步 RL backbone 支持：

| 场景 | 环境 | Next-state signal | 难度 |
|---|---|---|---|
| Terminal Agent | Shell 沙箱 | stdout/stderr, exit code | 长 horizon |
| GUI Agent | 屏幕状态 + accessibility tree | 视觉状态差分, 任务进度 | 长 horizon |
| SWE Agent | 代码仓库 + 测试集 | 测试结果, diff, lint | 长 horizon |
| Tool-call Agent | API/函数执行 | 返回值, 错误 trace | 中等 horizon |

---

## 核心系统二：RLAnything

**GitHub**: [Gen-Verse/Open-AgentRL](https://github.com/Gen-Verse/Open-AgentRL) · arXiv:2602.02488  
**发布时间**：2026/2/2  
**作者**：Wang Yinjie, Xie Tianbao 等（与 OpenClaw-RL 同一团队）

RLAnything 是 OpenClaw-RL 的理论基础，解决的是「**环境、策略、奖励模型三者怎么一起动态优化**」的问题。

核心设计：
- **Policy** 同时接收 step-wise 信号和 outcome 信号
- **Reward Model** 通过 consistency feedback 联合优化（奖励模型和策略模型互相改进）
- **Environment** 通过 critic feedback 自动适应（不需要手工设计环境转换规则）

实验结果：
- Qwen3-VL-8B-Thinking 在 OSWorld 上 +9.1%
- Qwen2.5-7B-Instruct 在 AlfWorld 上 +18.7%，在 LiveBench 上 +11.9%

---

## 核心系统三：ScaleCUA

**arXiv**: [2607.11185](https://arxiv.org/abs/2607.11185)  
**发布时间**：2026/7/13（上周）  
**作者**：清华大学 Knowledge Engineering Group

ScaleCUA 专注解决 Computer Use Agent 的 RLVR 瓶颈：**可验证数据太少，在线 RL 太低效**。

两个核心贡献：

**VeriGen（数据侧）**：端到端自动生成可验证 RL 任务。通过 100+ 并发 agent worker 与 Docker 交互，结合多 agent 反馈循环，生成了 24K+ 可验证任务和 3K+ 高质量 RL 任务。这解决了 RLVR 在 GUI 场景数据匮乏的根本问题。

**Frontier Sampling + Visual Context Segmentation（训练侧）**：
- Frontier Sampling：追踪每个任务的能力水平，把 rollout 分配给当前学习边界（而非随机分配），提升样本效率
- Visual Context Segmentation：用滑动窗口处理近期视觉上下文，平衡 rollout 和训练引擎压力，实现 **2.83x 训练加速**

结果：**OSWorld 68.7%，ScienceBoard 54.0%**，开源 Computer Use Agent 新 SOTA。

---

## 核心论文四：RLVP — 惩罚路径，奖励结果

**arXiv**: [2607.07435](https://arxiv.org/abs/2607.07435)  
**发布时间**：2026/7/8

这篇论文提出了一个重要的反直觉发现：**纯结果奖励（outcome-only RLVR）对于现实世界 Agent 来说是不够的，还需要路径惩罚（path penalty）。**

核心场景：一个代替你打电话的 Agent。结果奖励只关心"任务完成了吗"。但如果 Agent 反复给没回应的号码打电话、不遵守营业时间、跳过认证流程——结果奖励可能给它打高分，但行为是灾难性的。

RLVP 的解法：**"Penalize the Path, Reward the Outcome"**
- 路径惩罚：现实 agentic 环境可以廉价检测到坏动作，把它们作为可验证的负向信号
- 结果奖励：保持传统 RLVR 框架

实验：outcome-only 训练在几乎每次 episode 都违反约束；RLVP 实现了近零违约率同时保持高任务成功率。

四条路径惩罚设计规则（含避免「不作为陷阱」的处理）也是工程落地的重要参考。

---

## 产品端信号：Cursor Composer 2.5

2026 年 7 月 15 日，Cursor 发布了 Composer 2.5，这是 Cursor 自研的编程专用模型，200k context，定位是「编程专家，而非通用大模型」。

> "Grok 4.5 is the larger, more capable model for hard, long-running work. Composer 2.5 stays the coding specialist you already know."  
> — Tibor（Cursor 团队）

从社区反应来看，Cursor 用户认为这「不只是一次模型更新，而是一次身份转变」。Cursor 同时宣布**双倍**所有付费用户的 Composer 2.5 使用额度。

Cursor 没有公开 Composer 2.5 的完整技术报告，但从以下迹象可以推断其 online RL 倾向：
- 不共享 Grok 4.5 或 Fable 5 的训练管线，走独立的 coding-specific 优化路径
- 200k 上下文但没有公开 max context（暗示推理时计算分配是动态的）
- 新的 Cloud Agent Hooks 系统允许外部信号影响 Agent 的推理过程（`beforeSubmitPrompt`, `afterAgentResponse`, `stop`）——这是 online feedback loop 的基础设施

---

## AIDE 2：Agent 重写自己的推理框架

这是 2026 年 7 月 Twitter 上传播最广的实验之一。研究人员让一个科研 Agent（AIDE）在外循环中对自己的 Agent harness 做 100 次自主迭代改写。

结果：
- 90% 的改写方案被自己的评审投票否决
- 通过的 10% 在 held-out benchmark 上全面超过了人工设计的基线
- **奖励 hacking 率从 63% 降到 34%**（系统变得更难被"钻空子"）
- 发现了：新搜索策略、prompt 压缩 16x、分层防御 reward hacking 的机制

这是 Level 1 递归自改进（recursive self-improvement）的一个具体实例——不是改变模型权重，而是改变 Agent 框架自身。

---

## 技术机制对比

| 系统 | 学习时机 | 信号类型 | 硬件门槛 | 开源 |
|---|---|---|---|---|
| OpenClaw-RL | 对话结束后实时 | next-state (evaluative + directive) | 8×GPU | ✅ |
| RLAnything | 批次训练 | step-wise + outcome + consistency | 多GPU | ✅ |
| ScaleCUA | 在线 RL with RLVR | 任务完成信号 | 高（100+ 并发） | ✅ |
| RLVP | 在线 RL | outcome reward + path penalty | 中等 | 论文 |
| AIDE 2 | 外循环迭代 | benchmark 验证 | 中等 | 部分 |
| Cursor Composer 2.5 | 训练时（推断） | 编程任务验证 | — | ❌ |

---

## 统一框架：为什么这些系统在收敛

把上面几个系统放在一起看，可以提炼出一个收敛的范式：

**信号层面**：从「人工标注」→ 「可验证奖励（outcome）」→ 「可验证奖励 + 路径惩罚 + next-state信号」。奖励信号越来越丰富，越来越不依赖人工。

**时机层面**：从「离线批训练（月/年）」→ 「在线 RL（小时/天）」→ 「实时 RL（秒/分钟）」。

**架构层面**：四组件异步解耦（推理 / 收集 / 评估 / 训练），任何一个组件的速度瓶颈不再拖累其他组件。

**范围层面**：不再只针对数学/代码这类有确定性验证器的场景，GUI、终端、工具调用、对话都可以提取 next-state signal。

---

## 现在就能落地的实践方案

### 方案一：用 OpenClaw-RL 训练你的个人 Agent（4 小时起步）

**前提**：能访问 8 张 GPU（或 Fireworks AI/Tinker 云 GPU），有一个 OpenClaw 账号。

```bash
git clone https://github.com/Gen-Verse/OpenClaw-RL --recursive
cd OpenClaw-RL/slime

# 一键启动混合 RL 训练服务
bash ../openclaw-combine/run_qwen3_4b_openclaw_topk_select.sh

# 服务运行后，在 openclaw.json 里把 provider 指向本地 RL 服务器
# http://<HOST_IP>:30000/v1
```

关键设置三个环境变量：
```bash
NUM_GPUS=8        # GPU 总数
ACTOR_GPUS=4      # 用于推理的 GPU
ROLLOUT_GPUS=2    # 用于轨迹收集的 GPU
PRM_GPUS=2        # 用于 PRM 评估的 GPU
```

之后正常使用 OpenClaw，RL 训练在后台自动进行。

### 方案二：在已有 Agent 里加入路径惩罚（1 天）

RLVP 的核心原则不依赖复杂框架，可以直接加进任何基于 RLVR 的 Agent 训练循环：

```python
def compute_reward(trajectory, outcome_reward):
    path_penalty = 0.0
    
    for step in trajectory:
        # 规则可验证的坏动作（不需要人工标注）
        if step.action == "retry_failed_call" and step.consecutive_fails > 2:
            path_penalty -= 0.3
        if step.violates_time_constraint():
            path_penalty -= 0.5
        if step.skips_required_auth():
            path_penalty -= 1.0
    
    # "惩罚路径，奖励结果"
    return outcome_reward + path_penalty
```

关键：**不要让路径惩罚过大，避免 agent 陷入不作为陷阱**（不做任何操作 → 没有惩罚 → 局部最优）。

### 方案三：用 ScaleCUA 方法构建可验证任务数据集

ScaleCUA 的 VeriGen pipeline 可以独立使用，为任何 GUI/终端 Agent 生成训练数据：

```python
# 核心思路：用 Docker 容器做可重复的环境
# 让多个 Agent worker 并发执行任务
# 用多 Agent 反馈判断任务是否成功（不需要人工标注）

task_generator = VeriGen(
    docker_image="ubuntu:24.04",
    n_workers=100,
    validation_agents=3,  # majority voting 判断成功
)
dataset = task_generator.generate(n_tasks=10000)
```

### 方案四：最小可行的 Loop Engineering + RL 集成

如果你在用 Loop Engineering（参考之前的文章），可以把 RLVR 数据收集加进 quality gate：

```yaml
# .claude/loops/rl-feedback.yaml
gates:
  - command: "pnpm test"
    record_outcome: true    # 把 pass/fail 作为 RL outcome signal
    log_path: "~/.rl-data/trajectories/"
    
# 每次 Agent 完成任务，质量门的结果自动成为一条带标注的训练样本
```

---

## 值得关注但未完全验证的方向

**Areal（实时自适应 LLM）**：AfterLabs 在 2026 年 7 月宣布入选欧洲 NFAI 计划，核心研究方向是「built-in adaptation mechanisms」——模型在推理时就能实时更新对世界的理解，而不需要重新训练。这与 Real-time RL 的思路高度一致，但底层机制不同（更接近 meta-learning 和 continual learning）。

**Cursor Composer 2.5 的完整技术路线**：目前无公开技术报告，但从架构迹象推断很可能用了 coding-specific RLVR 管线。如果后续发布白皮书，将是 production-scale online RL for coding agents 的重要参考。

---

## 核心结论

**2026 年 Real-time RL Agent 的状态**：

1. **技术可行**：OpenClaw-RL 证明了「用对话训练对话 Agent」的完整工程路径，且已开源。
2. **数据瓶颈被解决**：ScaleCUA 的 VeriGen 展示了如何用 Docker 自动生成大量可验证任务，不依赖人工标注。
3. **奖励信号在完善**：从纯结果奖励（RLVR）→ 路径惩罚+结果（RLVP）→ 评估+指导双信号（OpenClaw-RL），奖励信号越来越能覆盖真实场景。
4. **产品端开始采用**：Cursor Composer 2.5 是工业界的先行信号，尽管细节不透明。
5. **下一步**：Level 1 递归自改进（AIDE 2 模式）——Agent 不只是学习如何完成任务，而是学习如何改进自己的 Agent 框架。

这个范式的终局是什么？用 OpenClaw-RL 作者的话说：**「任何与 Agent 的交互，都是一次免费的训练数据」**。当这句话的工程意义被完全兑现，「使用」和「训练」的边界就消失了。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Real-Time RL Agents in 2026: A Survey of Online Learning for AI Agents

**Topics covered**: OpenClaw-RL · RLAnything · ScaleCUA · RLVP · AIDE 2 · Cursor Composer 2.5  
**Time range**: January–July 2026

### The Core Shift

Before 2025: AI agents were trained once and stayed static. No matter how many times you corrected an agent, it couldn't learn from the correction.

In 2026: A cluster of research systems and products is breaking this assumption. **Agents can now convert live interactions into gradients and continuously update their own policies in real time.** This is Real-time RL (or Online Agentic RL or Real-time Recursive Learning).

Not "retrain every few months" — but **model weights updated seconds after a conversation ends**.

### Why 2026 Is the Inflection Point

Two things matured simultaneously:

**Technical**: RLVR (RL from Verifiable Rewards) was proven to work in agentic settings. An agent's "next state" — the user's reply, tool return value, terminal output, GUI state change — is a naturally available reward signal that was previously discarded.

**Engineering**: Fully async 4-component architectures (serving / rollout collection / reward evaluation / training) made serving and training concurrent. The serving loop no longer blocks on training.

### OpenClaw-RL (arXiv:2603.10165)

The most complete real-time agentic RL framework. Core design: fully async 4-component loop where inference, data collection, reward evaluation, and gradient updates run independently and never block each other.

**Three optimization methods:**
- Binary RL (GRPO): PRM scores each turn via next-state signal → GRPO advantage → PPO clipped loss
- On-Policy Distillation (OPD): judge extracts directional text hints from the next state → token-level advantage signal, richer than scalar reward
- Hybrid: combines both, stronger than either alone

**Track 1**: Personalize your local Qwen3 model through normal use — every conversation becomes a training trajectory.

**Track 2**: Terminal / GUI / SWE / tool-call agents — same async RL backbone, real-world environment grounding.

### RLAnything (arXiv:2602.02488)

The theoretical companion to OpenClaw-RL. Environment, policy, and reward model are jointly optimized in a closed loop. Results: +9.1% on OSWorld, +18.7% on AlfWorld.

### ScaleCUA (arXiv:2607.11185)

Addresses the two RLVR bottlenecks for Computer Use Agents: data scarcity and training inefficiency.

**VeriGen**: 100+ concurrent Docker agent workers with multi-agent feedback to auto-generate 24K+ verifiable tasks — no human annotation.

**Frontier Sampling**: allocates rollouts to the current learning frontier (not random) for sample efficiency.

**Visual Context Segmentation**: 2.83× training speedup.

**Results**: 68.7% on OSWorld, 54.0% on ScienceBoard — open-source SOTA.

### RLVP (arXiv:2607.07435): Penalize the Path, Reward the Outcome

Key finding: outcome-only RLVR fails for real-world agents because it can't express outcome-neutral constraints (don't call repeatedly, respect business hours, complete required authentication). Real agentic environments can cheaply detect these bad moves.

Adding path penalties: near-zero constraint violations while maintaining high task success. Four design rules to avoid the inaction trap.

### AIDE 2: Self-Improving Agent Harness

100 autonomous iterations where an agent rewrote its own agent framework. 90% of proposals rejected by majority vote. The surviving 10%:
- Beat the hand-crafted baseline on all held-out benchmarks
- Reduced reward hacking from 63% to 34%
- Found: new search policy, 16× prompt compression, layered defenses against reward hacking

Level 1 recursive self-improvement — not model weights, but the agent framework itself.

### Cursor Composer 2.5

Cursor's own coding-specialist model, 200k context, released July 15, 2026. "An identity change, not just a model update." No public technical report, but architecture signals suggest coding-specific RLVR pipeline. New Cloud Agent Hooks (`beforeSubmitPrompt`, `afterAgentResponse`, `stop`) provide the infrastructure for external feedback loops — the foundation for online RL integration.

### What You Can Deploy Today

**Option 1 — OpenClaw-RL personal agent**: 8× GPU (or Fireworks AI cloud), Qwen3-4B/9B. After setup, normal usage automatically generates training trajectories.

**Option 2 — Add path penalties to existing RLVR**: Any agent training loop. Detect bad moves via deterministic rules (no human annotation needed), subtract from the outcome reward. Four design rules from RLVP prevent the inaction trap.

**Option 3 — VeriGen-style data generation**: Docker container + concurrent agent workers + multi-agent majority vote = auto-generated verifiable task dataset at scale.

**Option 4 — Loop Engineering + RL outcome recording**: Record quality gate pass/fail as labeled training samples, feed into periodic fine-tuning.

### Bottom Line

The paradigm shift in one sentence from the OpenClaw-RL authors: **"Every interaction with an agent is free training data."** When this statement's engineering implications are fully realized, the boundary between "using" and "training" disappears.

The 2026 state: technically proven, data bottleneck solved, reward signal complete enough for real-world scenarios, first production signals from Cursor. The next frontier: agents that improve not just their task performance, but their own agent architecture (AIDE 2 mode).

© 2026 Author: Mycelium Protocol
