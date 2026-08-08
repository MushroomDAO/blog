---
title: "Prime Agent：PrimeIntellect 开源的自改进 RLM 编程 Agent"
titleEn: "prime-agent-primeintellect-self-improving-rlm-coding-agent"
description: "PrimeIntellect 开源的自改进 Agent，7.6k stars，MIT License。引入 RLM（递归语言模型）把 context 当变量、工具调用当函数，运行在持久 IPython REPL 中。通过 Continual Harness 把提示词/记忆/技能描述持久化为可精炼的 durable state，支持子 Agent 并行、后台 daemon 会话、Agent 间直接通信、/goal 跨轮次持久目标和 /autonomous 自主模式。"
descriptionEn: "PrimeIntellect's open-source self-improving agent, 7.6k stars, MIT License. Introduces RLM (Recursive Language Model) that treats context as variables and tool calls as functions, running inside a persistent IPython REPL. Uses a Continual Harness to persist prompts/memories/skills as refinable durable state. Supports parallel subagents, daemon-backed background sessions, agent-to-agent communication, /goal persistent objectives, and /autonomous mode."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["自改进Agent", "RLM", "持久Agent", "编程Agent", "IPython", "PrimeIntellect", "Mycelium"]
heroImage: "../../assets/images/prime-agent-primeintellect-self-improving-rlm-coding-agent-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 Coding Agent 的基础假设是：一个对话窗口，一个任务，做完清空。Prime Agent 做的是相反方向的事——让 Agent 在会话之间积累经验，把有效的操作模式变成可复用的 durable state，并让任务在终端断开后继续在后台运行。

GitHub: https://github.com/PrimeIntellect-ai/prime-agent | ⭐ 7,634 | MIT License

---

## 核心概念：RLM

**RLM（Recursive Language Model）** 是 Prime Agent 的基础编程模型：

- **Prompt-as-a-Variable**：Context 不是对话的副产品，而是可以被代码显式操作的变量
- **Programmatic Tool/Subagent Calling**：工具调用和子 Agent 调用是函数调用，而不是特殊的 API 格式
- **Persistent IPython REPL**：所有操作都在一个持久 Python 环境里发生——文件操作、shell 命令、工具调用、子 Agent 都通过代码完成，不是通过对话指令

这意味着 Agent 的控制流是真正的程序代码，而不是语言模型对指令的隐式理解。

---

## Continual Harness（持续演进的 Harness）

Continual Harness 是 Prime Agent 存储和改进自身操作知识的机制：

- **存储内容**：补充提示词、记忆、可复用技能描述、子 Agent 规格
- **改进方式**：`/refine` 命令让 Agent 检视当前工作轨迹，识别出有价值的经验，把它们以小的、有证据支撑的更新形式写入 Harness state
- **不可变基座**：`/refine` 永远不会修改不可变的 base system prompt；所有精炼都发生在 supplemental state 层
- **回滚支持**：Harness 记录精炼历史，支持回滚到任意之前的状态

这是"自改进"的具体实现：不是模型权重的改变，而是 Harness state 积累了验证过的操作知识。

---

## 子 Agent 与并行

```python
# 在 RLM 内部，通过代码调用子 Agent
result = rlm("分析这段代码并生成测试用例")

# 并行调用多个子 Agent
import concurrent.futures
results = list(concurrent.futures.ThreadPoolExecutor().map(
    lambda task: rlm(task), [task1, task2, task3]
))
```

子 Agent 是真实的子进程，返回值可以直接在父 Agent 的 Python 代码中使用。Agent 之间可以互相发现、发送消息、协调工作，不需要把所有通信路由给用户。

---

## 持久运行与后台 Daemon

```bash
# 安装
curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh

# 在项目目录启动
cd /path/to/project
prime-agent

# 常用命令
prime-agent agents                    # 查看所有运行中/空闲/保存的会话
prime-agent attach <agent>            # 重新连接到一个运行中的会话
prime-agent --resume <path|id>        # 恢复保存的会话
prime-agent status                    # 查看后台服务状态
prime-agent doctor [--fix]            # 检查或修复后台服务
prime-agent update [--force]          # 更新 Prime Agent
prime-agent shutdown [--force]        # 停止所有 Agent 和后台服务
```

**Daemon 支持**：活跃会话、IPython 状态、调度和子 Agent 在终端断开后继续运行，可以随时重新连接。这解决了长任务的核心问题——不需要保持终端连接。

---

## 长任务特性

| 特性 | 说明 |
|------|------|
| **`/goal`** | 持久目标，跨轮次保持直到完成/暂停/清除 |
| **`/autonomous`** | 在配置的轮次/token/时间预算内自主运行，可定义质量门控 |
| **`/heartbeat`** + `rlm_heartbeat` | 定时或定时重新进入会话 |
| **`prime-agent schedule`** | 在特定时间运行 |
| **自动压缩** | 上下文自动压缩，不丢失关键进度 |
| **保留子 Agent** | 子 Agent 在整个长任务期间持续存在 |

---

## 技能系统

技能是可导入的 Python 包。内置技能创建工具可以把重复出现的工作流打包成项目级或个人级技能：

```bash
# 技能存储在 ~/.prime-agent/skills/ 或项目 .prime-agent/skills/
# 技能是 Python 包，可以直接 import
```

Prime Agent 的技能设计和 Claude Code 的 skill 系统（`~/.claude/skills/`）在理念上高度一致——都是把工作流固化为可复用、可分发的知识单元。

---

## 安全说明

Prime Agent 以用户权限执行 LLM 生成的 Python 代码和项目命令，worker 和 kernel 进程提供了生命周期隔离，但**不是安全沙盒**。

> 建议：使用一次性 clone、干净的 worktree 或可检查/恢复的检查点，不要在生产系统上直接运行不受信任的指令。

---

## 技术背景

Prime Agent 基于 [`pi`](https://github.com/earendil-works/pi)（pi-mono by badlogic）构建，后者是一个专注于长任务 Agent 的框架。PrimeIntellect 同时维护 [prime-rl](https://github.com/PrimeIntellect-ai/prime-rl)（分布式 RL 训练）和 [Verifiers](https://github.com/PrimeIntellect-ai/verifiers)（Agent 评估基准），Prime Agent 是这个生态中面向开发者的执行层。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Prime Agent: PrimeIntellect's Open-Source Self-Improving RLM Coding Agent

*by Mycelium Protocol*

---

Most coding agents share the same implicit assumption: one context window, one task, clear when done. Prime Agent works in the opposite direction — accumulating experience across sessions, crystallizing effective operating patterns into reusable durable state, and keeping tasks running in the background after the terminal disconnects.

GitHub: https://github.com/PrimeIntellect-ai/prime-agent | ⭐ 7,634 | MIT License

---

### Core Concept: RLM

The **Recursive Language Model (RLM)** is Prime Agent's foundational programming model:

- **Prompt-as-a-variable**: context is not a side effect of conversation — it's a variable that code can explicitly manipulate
- **Programmatic tool/subagent calling**: tool calls and subagent calls are function calls in code, not special API formats
- **Persistent IPython REPL**: everything — file operations, shell commands, tool use, subagents — happens through code in a persistent Python environment, not through conversational instructions

This means the agent's control flow is real program code, not a language model's implicit interpretation of instructions.

---

### Continual Harness

The Continual Harness is the mechanism Prime Agent uses to store and improve its own operating knowledge:

- **What it stores**: supplemental prompts, memories, reusable skill descriptions, subagent specifications
- **How it improves**: `/refine` reviews the current work trajectory, identifies valuable lessons, and applies small, evidence-backed updates to harness state
- **Immutable base**: `/refine` never modifies the immutable base system prompt; all refinements happen in the supplemental state layer
- **Rollback support**: refinement history is recorded, supporting rollback to any prior state

This is the concrete implementation of "self-improving": not changing model weights, but accumulating verified operating knowledge in harness state.

---

### Subagents and Parallelism

```python
# Inside RLM, call subagents through code
result = rlm("analyze this code and generate test cases")

# Parallel subagent calls
import concurrent.futures
results = list(concurrent.futures.ThreadPoolExecutor().map(
    lambda task: rlm(task), [task1, task2, task3]
))
```

Subagents are real child processes; return values can be used directly in the parent agent's Python code. Agents can discover each other, exchange messages, and orchestrate without routing everything through the user.

---

### Persistent Daemon-Backed Sessions

```bash
# Install
curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh

# Start in your project
cd /path/to/project
prime-agent

# Session management
prime-agent agents                    # browse running/idle/saved sessions
prime-agent attach <agent>            # reattach to a running session
prime-agent --resume <path|id>        # resume a saved session
prime-agent status                    # inspect background service state
prime-agent doctor [--fix]            # check or repair background services
```

Active sessions, IPython state, schedules, and subagents keep running after the terminal disconnects and can be reattached later — solving the fundamental problem of long-running tasks without keeping a terminal open.

---

### Long-Running Task Features

| Feature | Description |
|---------|-------------|
| **`/goal`** | Persistent objective, active across turns until completed/paused/cleared |
| **`/autonomous`** | Continues within configured turn/token/time budgets with optional quality gates |
| **`/heartbeat` + `rlm_heartbeat`** | Periodically or at scheduled times re-enter a session |
| **`prime-agent schedule`** | Run at a specific time |
| **Automatic compaction** | Context compacted automatically without losing critical progress |
| **Retained subagents** | Subagents persist throughout long tasks |

---

### Skills

Skills are importable Python packages. The built-in skill creator packages recurring workflows into project or personal skills — the same philosophy as Claude Code's `~/.claude/skills/` system.

---

### Safety Note

Prime Agent executes model-generated Python and project commands with your user permissions. Worker and kernel processes provide lifecycle isolation but **are not a security sandbox**. Use a disposable clone, clean worktree, or a checkpoint you can inspect and restore — never run untrusted instructions directly on production systems.

---

### Technical Background

Built on [`pi`](https://github.com/earendil-works/pi) (pi-mono by badlogic). PrimeIntellect also maintains [prime-rl](https://github.com/PrimeIntellect-ai/prime-rl) for distributed RL training and [Verifiers](https://github.com/PrimeIntellect-ai/verifiers) for agent evaluation benchmarks — Prime Agent is the developer-facing execution layer in this ecosystem.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
