---
title: "LongHorizon-Harness：让 AI Agent 真正干完长任务的执行框架"
titleEn: "LongHorizon-Harness: An Execution Framework That Gets AI Agents to Actually Finish Long Tasks"
description: "AMAP-ML 开源的 LongHorizon-Harness 用三角色分工（Manager/Executor/Auditor）解决 AI Agent 的长任务失效问题：每轮 Executor 用全新上下文执行，Auditor 独立验证环境，只有通过验证的进展才写入持久状态。WeaveBench 提升 +28.9pp，OSWorld 2.0 提升 3×，支持 Claude Code/Codex/OpenClaw，MIT 许可。"
descriptionEn: "AMAP-ML's LongHorizon-Harness uses three specialized roles — Manager, Executor, Auditor — to solve AI agent drift on long tasks. Each Executor round starts with a fresh context; the Auditor independently verifies environment state; only auditor-approved results enter durable task state. WeaveBench +28.9pp, OSWorld 2.0 3×, Terminal-Bench +7.5pp with 24% fewer tokens. Claude Code / Codex / OpenClaw backends, MIT license."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["AI Agent", "长任务", "计算机使用", "状态管理", "开源工具", "Claude Code", "Codex", "Mycelium"]
heroImage: "../../assets/images/longhorizon-harness-amap-ml-ai-agent-long-task-banner.jpg"
---

*by Mycelium Protocol*

---

给 AI Agent 一个任务，让它干完——这件事比想象中难得多。

不是模型能力不够，而是长任务有几个工程层面的系统性问题：上下文越积越长导致状态漂移、中途失败丢失已验证的进展、没有独立审计所以「假完成」悄悄混入结果。

**[LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)**（AMAP-ML）把这三个问题拆开，各解一个：新鲜上下文、可持久化的验证状态、独立审计角色。它不训练新模型，不替换 Claude Code 或 Codex 的执行循环——它在它们之上跑，协调它们的工作边界。

232 stars，今日开源（2026-08-05），MIT 许可，arXiv: 2608.01964。

---

## 核心问题：Agent 为什么干不完长任务

长任务失败通常不是一次性的大错误，而是积累性崩溃：

1. **上下文污染**：前几轮的历史、错误、尝试不断堆积在 context window 里，到后期模型已经在一片混乱的上下文里做决策
2. **状态漂移**：Agent 记忆里的「已完成进展」和环境实际状态逐渐脱节，「我以为我完成了 X」但 X 其实没持久化
3. **无独立验证**：执行者和验证者是同一个 context，验证形同虚设——做了 20 步之后，Agent 会倾向于说「完成了」

LongHorizon-Harness 的设计思路：**让三件事物理隔离，各司其职**。

---

## 三角色架构：一份可信状态

```
Manager（规划层）
   维持：原始目标 + 已验证进展 + 下一步计划
      ↓ 下发清晰的单步任务
Executor（执行层）
   每轮：全新上下文，专注一个任务
      ↓ 返回执行结果
Auditor（验证层）
   独立检查：文件 / 界面 / 日志 / 测试 / 环境
      ↓ 通过 → 写入持久状态；失败 → 打回 Executor
```

| 角色 | 职责 | 关键设计 |
|------|------|---------|
| 🧭 **Manager** | 维护目标和规划 | 只看已验证进展，不参与执行 |
| ⚡ **Executor** | 执行单步任务 | **每轮全新上下文**，不受历史污染 |
| 🔍 **Auditor** | 独立验证结果 | 直接检查真实环境，不信任 Executor 的自述 |

**只有通过 Auditor 独立验证的结果才能进入持久任务状态。** 即使 context 被刷新、执行失败、或者交付物没通过检查，已验证的进展仍然保留，系统从「剩余工作」继续。

这是一个关键设计：Executor 每轮用全新上下文，所以不受之前几十轮历史的污染；但 Manager 看到的是经过 Auditor 验证的积累状态，所以「知道做到哪里了」。

---

## 基准测试：同模型、同执行后端，只换 Harness

用 Qwen 3.7-Plus 作为 backbone，Claude Code 作为执行后端，三个基准横向对比：

| 基准 | 任务数 | 无 Harness | LongHorizon-Harness | 提升 |
|------|--------|------------|---------------------|------|
| **WeaveBench**（GUI+CLI 混合） | 114 | PassRate 51.8% | **80.7%** | **+28.9pp** |
| **WeaveBench** | 114 | Overall 0.702 | **0.835** | +0.133 |
| **OSWorld 2.0**（纯桌面任务） | 108 | Binary 2.8% | **8.3%** | **3.0×** |
| **OSWorld 2.0** | 108 | Partial 21.5% | **35.2%** | +13.7pp |
| **Terminal-Bench 2.1**（代码+CLI） | — | 69.7% | **77.2%** | **+7.5pp**，Token 减少 24% |

三个方向都有实质提升，Terminal-Bench 还同时减少了 24% 的 token 消耗。原因直觉上合理：Executor 每轮上下文干净，模型更少迷失，效率更高。

---

## 支持的 Agent 后端和执行环境

任何 Agent、任何模型、任何执行环境，通过配置接入，不改变原有执行循环：

**Agent 后端**：
- `claude_code`（Claude Code CLI）
- `codex`（Codex CLI）
- `openclaw`
- 自定义 `AgentAdapter` 实现

**模型层**：每个角色（Manager / Executor / Auditor）可以分配不同的模型和后端——比如 Manager 用 Claude Opus，Executor 用 Sonnet，Auditor 用 Qwen，在质量和成本之间做权衡。

**执行环境**：
- `local`（本地）
- `ssh://user@host:port`（远程机器）
- `docker://container`（容器）

---

## 快速上手

安装（Python ≥ 3.10，需要已安装 `claude` / `codex` / `openclaw` 其中之一）：

```bash
uv tool install lh-harness
# 或
pip install lh-harness
```

运行一个简单任务：

```bash
lh-harness run \
  --task "Inspect the current directory and summarize its files."
```

从文件加载长任务，打开 Dashboard 监控：

```bash
lh-harness run --task @task.md --dashboard
```

常用参数：

```bash
--task          任务文本 或 @task.md
--agent         claude_code | codex | openclaw
--env           local | ssh://... | docker://...
--max-rounds    最大 Manage-Execute-Audit 轮次（默认 30）
--dashboard     启动实时监控和人工干预入口
```

连接桌面操作 MCP server（GUI 任务）：

```bash
lh-harness run --task @task.md --agent claude_code \
  --mcp-config /path/to/your/mcp.json \
  --mcp-add-dir /path/to/your/mcp/files
```

---

## Dashboard 和运行记录

Dashboard 是为长任务设计的：每轮的计划、执行结果、审计证据、打回原因，全部可视。任务完成/阻塞/需要输入/多次失败时提供人工干预入口。

每次运行存在独立的 `runs/<run-id>/` 目录，完整保留：

| 文件 | 保存内容 |
|------|---------|
| 任务状态 | 原始目标、需求、已验证进展、剩余工作 |
| 事件流 | 整个运行过程中发生了什么 |
| 审计报告 | 每轮的证据和验收决定 |
| 角色轨迹 | Manager / Executor / Auditor 的输入和输出 |
| Workspace | 执行期间产生的文件和产物 |
| 最终报告 | 验证后的任务结果 |

---

## 任务领域覆盖

LongHorizon-Harness 覆盖的任务域相当宽，这也是论文里 WeaveBench 和 OSWorld 2.0 的任务范围：

网页前端开发、数据分析与可视化、运维与调试、设计与图像处理、游戏与交互、文档与演示文稿、空间推理、桌面与系统设置、科研与教育、创意生产、工程与计算、个人服务、行政合规、商业金融、医疗……

一个任务可以从浏览器开始，移动到命令行处理数据，进入桌面软件生成产物，再回到终端验证。全程同一套状态管理系统。

---

## 为什么这个方向值得关注

**「模型能力」和「任务完成」之间，有一条工程峡谷。**

过去一年里，大多数 Agent 框架把精力放在「更好的工具调用」「更丰富的上下文」，但长任务失败的根本原因不在于单步能力，而在于**跨步状态的可信积累**——做对了的东西能不能在环境里确认、持久化、不被后续操作覆盖。

LongHorizon-Harness 把这个问题显式化，用三角色分离来解：执行和验证物理隔离，经过 Auditor 的东西才算数。数据说话：WeaveBench 从 51.8% 到 80.7%，OSWorld 2.0 翻了三倍——同模型、同执行后端、只换 harness。

这个结果说明，现有模型的能力还远未被当前的 Agent 框架充分释放。Harness 工程本身就是一个重要的研究方向。

仓库：[github.com/AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)  
论文：[arxiv.org/abs/2608.01964](https://arxiv.org/abs/2608.01964)  
网站：[lh-harness.pages.dev](https://lh-harness.pages.dev)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## LongHorizon-Harness: Making AI Agents Actually Finish Long Tasks

*by Mycelium Protocol*

AI agents failing on long tasks isn't usually a model capability problem. It's a systems engineering problem: context accumulates until state drifts, verified progress gets lost on partial failures, and there's no independent check to distinguish "done" from "claimed done."

**[LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)** (AMAP-ML) solves each of these separately — with architecture, not with training. It doesn't replace Claude Code or Codex's execution loop; it coordinates role boundaries, verified task state, and cross-round progress around them. 232 stars, open-sourced August 5 2026, MIT license.

### Three Roles, One Trusted State

```
Manager   → holds original goal, verified progress, next step
              ↓ issues one clearly-scoped task
Executor  → starts FRESH each round, runs one task, returns result
              ↓ result submitted to Auditor
Auditor   → independently inspects files, UI, logs, tests in real environment
              ↓ PASS: writes to durable state / FAIL: returns to Executor
```

The Executor's fresh context each round is the core insight: no history pollution, no drift from 30 rounds of accumulated context. The Manager only ever sees Auditor-verified results — so it has an accurate picture of what's actually done. When the context refreshes, an action fails, or a deliverable doesn't pass inspection, previously verified progress is preserved and the system continues from what remains.

### Benchmarks: Same Model, Same Backend, Only the Harness Changes

All results use Qwen 3.7-Plus + Claude Code backend:

| Benchmark | Baseline | With Harness | Gain |
|-----------|---------|--------------|------|
| WeaveBench (114 GUI+CLI tasks) | 51.8% PassRate | **80.7%** | **+28.9pp** |
| OSWorld 2.0 (108 desktop tasks) | 2.8% Binary | **8.3%** | **3.0×** |
| Terminal-Bench 2.1 | 69.7% | **77.2%** | **+7.5pp, 24% fewer tokens** |

Three different task types, three consistent gains. The Terminal-Bench token reduction makes intuitive sense: fresh context per round means less confusion, which means less wasted exploration.

### Any Backend, Any Model, Any Environment

```bash
# Install
uv tool install lh-harness

# Run a task
lh-harness run --task "Inspect the current directory and summarize its files."

# Long task from file + live dashboard
lh-harness run --task @task.md --dashboard
```

**Agent backends**: `claude_code`, `codex`, `openclaw`, or custom `AgentAdapter`.  
**Models**: Each role (Manager / Executor / Auditor) can use a different model and backend — optimize quality vs. cost per role.  
**Environments**: `local`, `ssh://user@host:port`, `docker://container`.

### What Gets Recorded

Every run lives in `runs/<run-id>/`: task state, full event stream, per-round audit reports, Manager/Executor/Auditor trajectories, workspace artifacts, and final verified report. The Dashboard shows every round's plan, execution result, audit evidence, and rework reason — with human-gate prompts when a task completes, blocks, or fails repeatedly.

### Why This Matters

The gap between model capability and task completion is an engineering gap. Most agent frameworks focus on richer tool calls or larger context windows. LongHorizon-Harness focuses instead on the part that actually fails on long runs: trustworthy accumulation of verified progress across steps.

WeaveBench: 51.8% → 80.7%. OSWorld 2.0: 3×. Same model, same execution backend. The results suggest current models have significant capability that existing agent frameworks aren't extracting — because the harness engineering wasn't there.

Repo: [github.com/AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) · Paper: [arxiv.org/abs/2608.01964](https://arxiv.org/abs/2608.01964) · Site: [lh-harness.pages.dev](https://lh-harness.pages.dev)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
