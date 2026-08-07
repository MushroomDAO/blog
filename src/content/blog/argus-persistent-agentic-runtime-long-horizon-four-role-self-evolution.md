---
title: "Argus：让 Agent 干完整件事的持久化四角色运行时"
titleEn: "argus-persistent-agentic-runtime-long-horizon-four-role-self-evolution"
description: "Argus 是一个开源 Agent 运行时框架，通过 Manager→Planner→Engineer⇄Reviewer 四角色分工，把长周期任务的执行与判断强制分离，项目状态跨会话持久化存储。SWE-Bench Pro 达 78%，成熟 wave 比初始 wave 少用 21% tokens，并附 arXiv 论文。支持 Copilot、Codex CLI、Claude Code、OpenCode 等多种后端。"
descriptionEn: "Argus is an open-source agentic runtime that separates execution from judgment via a four-role architecture — Manager, Planner, Engineer, Reviewer — persisting project state across sessions and runtime upgrades. It achieves ~78% on SWE-Bench Pro vs 59% for Direct Copilot, with mature waves using 21% fewer tokens than startup waves. Backed by an arXiv paper and supporting Copilot, Codex CLI, Claude Code, and OpenCode backends."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["Agent Runtime", "长任务自主", "多角色协作", "持久化状态", "自演化", "开源", "Mycelium"]
heroImage: "../../assets/images/argus-persistent-agentic-runtime-long-horizon-four-role-self-evolution-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 Agent 系统的隐含假设是：一次对话，一个任务，做完就结束。

Argus 要解决的是另一类问题：**一件事需要几天，跨越多个会话，中途发现假设错了，要回滚然后继续**。

---

## 核心设计：执行与判断必须分离

Argus 的基础架构是四个角色，而不是一个万能 Agent：

| 角色 | 权限 | 职责 |
|------|------|------|
| **Manager** | 控制 | 解析用户意图，选择工作流，拥有阶段流转的决定权 |
| **Planner** | 方向 | 选出下一个高价值任务，定义它必须产出的证据 |
| **Engineer** | 执行 | 实现代码、跑实验、调 API、生成可检查的产物 |
| **Reviewer** | 验证 | 独立检查正确性、证据充分性、局限性和完成标准 |

关键约束：**Engineer 做完之后，必须经过 Reviewer 独立核查才能推进到下一阶段**。不是 Engineer 自己说「我做好了」就算完。

这个分离设计解决了单角色 Agent 的根本问题——执行者没有动力承认自己的输出有问题。Reviewer 的权力是独立的，它的工作就是找问题。

---

## 持久化：状态活得比会话更长

Argus 的所有项目状态都持久化存储：

- 任务列表和检查点
- 每个阶段的决策和被拒绝的路径
- Skills（可调用能力）和验证器
- 证据产物

这些内容在会话中断、运行时升级、甚至换一个后端 AI 之后都不会丢失。项目可以随时暂停，从最后一个 Reviewer 验证通过的位置继续，而不是从头开始。

**模型权重不变**——自演化发生在运行时状态和控制策略层，不是靠微调模型。

---

## 自演化：越跑越省

arXiv 论文（2608.05144）里有一组数据值得注意：

- 成熟 wave（项目跑了一段时间后）比启动 wave **少用 21% solve-input tokens**
- 每个任务的 **active workflow time 少用 15%**
- 同时记录了 **34 次 verifier 自动恢复**和 **22 次严格评审循环救援**

这是因为系统把成功的解法路径、被拒绝的路径、验证通过的证据都存起来，后续相似任务可以直接复用，不用重新探索。

---

## Benchmark 数据

在七个 GPT-5.5 benchmark arena 上：

| 测试 | Argus | 对比基线 |
|------|-------|---------|
| SWE-Bench Pro | **~78%** | Direct Copilot 59% |
| AARRI-Bench | **76.8%** | — |
| 数学数据合成 | **+28 分** | — |

代价：Argus 用了 1.41 倍的 aggregate tokens。但随着项目成熟，这个比例会下降。

论文里还提到了实际案例：一个优化过的 RWKV6 kernel 被合并进了上游；一次多天数学研究保留了被证伪的路径和有证据支撑的前沿更新；六条论文流水线完成了 254 个任务，发生了 16 次阶段回滚。

---

## 安装和快速上手

```bash
git clone https://github.com/lbx154/Argus.git
cd Argus

python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

连接后端（以 Claude Code 为例）：

```bash
argus --setup --non-interactive \
  --backend claude \
  --accept-house-rules
```

支持的后端：`copilot` / `pi` / `codex` / `claude` / `opencode`

启动：

```bash
argus            # 终端交互界面
argus --web      # Web UI，默认 http://127.0.0.1:8799
argus --doctor   # 检查安装是否正常
argus --status   # 查看当前运行时状态
```

远程服务器通过 SSH 隧道访问 Web UI：

```bash
# 服务器端
argus --web --no-open

# 本地
ssh -L 8799:127.0.0.1:8799 user@server
# 然后打开 http://127.0.0.1:8799
```

---

## 可扩展的「Vertical」机制

Argus 允许为特定领域定义 Vertical——一套自定义的阶段、Skills、数据集、工具、证据要求和完成标准。

这意味着：做 GPU kernel 优化的 Vertical 和做生物信息学文献综述的 Vertical，可以有完全不同的验证标准和工作流，而不是共用一套通用流程。

```bash
# 也可以让另一个 Agent 作为 Argus 的外层操作者
# OpenClaw、Hermes 或任何能调 shell 或 HTTP API 的 Agent 都可以
argus --web --no-open   # 暴露 Web/API 接口
```

---

## 和其他 Agent 框架的区别在哪

大多数框架关注的是「怎么调用工具」「怎么规划步骤」。Argus 关注的是「**怎么让一个项目在失败、回滚、中断之后还能继续前进**」。

核心差异：
1. **强制独立审核**——Engineer 没有权力宣布自己的工作完成
2. **拒绝路径也存储**——知道「哪条路走不通」和知道「哪条路走通了」同样有价值
3. **自演化在状态层**——不是微调模型，而是积累验证过的知识和路径

---

项目地址：https://github.com/lbx154/Argus  
论文：arXiv:2608.05144 — *Argus: A General-Purpose Agentic Runtime for Long-Horizon Reasoning*

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Argus: A Persistent Four-Role Runtime That Lets Agents Finish Real Work

*by Mycelium Protocol*

---

Most agent systems carry an implicit assumption: one conversation, one task, done when the context window ends.

Argus is built for a different class of problem: **work that takes days, spans multiple sessions, discovers mid-run that a core assumption was wrong, and needs to roll back and continue.**

---

### Core Design: Execution Must Be Separated From Judgment

Argus replaces the single omnipotent agent with four distinct roles:

| Role | Authority | Responsibility |
|------|-----------|----------------|
| **Manager** | Control | Interprets operator intent, selects workflow, owns stage transitions |
| **Planner** | Direction | Selects the next high-value task, defines required evidence |
| **Engineer** | Execution | Implements, runs experiments, calls APIs, produces inspectable artifacts |
| **Reviewer** | Verification | Independently checks correctness, evidence quality, limitations, completion |

The critical constraint: **after Engineer finishes, Reviewer must independently verify before the project advances.** Engineer cannot declare its own work complete.

This separation solves a fundamental problem with single-role agents: the executor has no incentive to flag its own output as flawed. The Reviewer's authority is independent — its job is to find problems.

---

### Persistence: State Outlives Sessions

All project state in Argus is persisted:

- Task lists and checkpoints
- Decisions and rejected routes at every stage
- Skills and verifiers
- Evidence artifacts

This survives session interruption, runtime upgrades, and even switching to a different AI backend. A project can pause at any point and resume from the last Reviewer-verified position — not from scratch.

**Model weights stay fixed** — self-evolution happens at the runtime state and control policy layer, not via fine-tuning.

---

### Self-Evolution: Gets More Efficient Over Time

The arXiv paper (2608.05144) reports a notable set of numbers:

- Mature waves (after a project has been running for a while) use **21% fewer solve-input tokens** than startup waves
- **15% less active workflow time** per task
- **34 verifier automatic recoveries** and **22 strict review-loop rescues** logged

This works because successful solution paths, rejected paths, and verified evidence are all stored. Later tasks with similar structure can reuse them instead of re-exploring from scratch.

---

### Benchmark Results

Across seven GPT-5.5 benchmark arenas:

| Benchmark | Argus | Baseline |
|-----------|-------|----------|
| SWE-Bench Pro | **~78%** | Direct Copilot: 59% |
| AARRI-Bench | **76.8%** | — |
| Mathematical data synthesis | **+28 points** | — |

The cost: 1.41× aggregate tokens vs Direct Copilot. That ratio improves as projects mature.

Real-world results from the paper: an optimized RWKV6 kernel was merged upstream; a multi-day math campaign retained falsified routes and proof-backed frontier updates; six paper pipelines completed 254 missions with 16 stage rollbacks.

---

### Quick Install

```bash
git clone https://github.com/lbx154/Argus.git
cd Argus

python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Connect a backend (Claude Code example):

```bash
argus --setup --non-interactive \
  --backend claude \
  --accept-house-rules
```

Supported backends: `copilot` / `pi` / `codex` / `claude` / `opencode`

Launch:

```bash
argus            # terminal cockpit
argus --web      # Web UI at http://127.0.0.1:8799
argus --doctor   # verify installation
argus --status   # inspect current runtime state
```

Remote server via SSH tunnel:

```bash
# On server
argus --web --no-open

# Locally
ssh -L 8799:127.0.0.1:8799 user@server
# Open http://127.0.0.1:8799
```

---

### Verticals: Domain-Specific Workflows

Argus supports custom Verticals — a named set of stages, Skills, datasets, tools, evidence requirements, evaluation methods, and completion criteria for a specific domain.

A Vertical for GPU kernel optimization and one for biomedical literature synthesis can have completely different verification standards and workflows, rather than sharing a generic process.

External agent operators (OpenClaw, Hermes, or any agent with shell or HTTP API access) can also drive Argus as an outer layer, using `argus --web --no-open` to expose the Web/API surface.

---

### What Makes This Different

Most frameworks focus on "how to call tools" or "how to plan steps." Argus focuses on **how a project keeps moving forward after failure, rollback, and interruption.**

Three structural differences:

1. **Mandatory independent review** — Engineer cannot declare its own output complete
2. **Rejected routes are stored** — knowing what doesn't work is as valuable as knowing what does
3. **Self-evolution is in the state layer** — accumulated verified knowledge, not model fine-tuning

---

Repository: https://github.com/lbx154/Argus  
Paper: arXiv:2608.05144 — *Argus: A General-Purpose Agentic Runtime for Long-Horizon Reasoning*

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
