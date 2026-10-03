---
title: "Pi Durable：每步存档，让 AI Agent 崩溃后自动续命"
titleEn: "Pi Durable: Per-Step Checkpointing So Your AI Agent Survives Crashes"
description: "earendil-works/pi-durable，MIT，实验版 npm 包，Pi 1.0 配套发布。为长期运行 AI Agent 设计的持久化层：每步 checkpoint（模型请求/工具调用/压缩），进程崩溃后从上次断点恢复而不是从头再来。requestId 实现幂等提交（exactly-once 语义）。子 Agent 在各自对话中独立运行，崩溃后自动续命。Cloudflare Agents SDK 已有官方集成。"
descriptionEn: "earendil-works/pi-durable, MIT, experimental npm package, released alongside Pi 1.0. A persistence layer for long-running AI agents: per-step checkpoints (model request / tool call / compaction), process death recovery from the last checkpoint rather than from scratch. requestId enables idempotent submissions (exactly-once semantics). Sub-agents run in their own conversations and resume after crashes. Official Cloudflare Agents SDK integration available."
pubDate: 2026-10-03
heroImage: "../../assets/images/pi-durable-agent-persistent-checkpoint-crash-recovery-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent运行时", "持久化", "崩溃恢复", "Pi", "Cloudflare", "幂等", "开源拆解"]
lang: "zh-CN"
wechatTitle: "Pi Durable：让AI Agent崩溃后自动续命"
wechatDigest: "MIT实验版；每步存档；crash后自动续命；exactly-once幂等；Cloudflare可部署"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题在哪里

传统 AI Agent 的生命周期是线性的：启动 → 执行若干步 → 结束（或崩溃）。

执行 20 步、在第 18 步崩溃？从头再来。工具调用发出去了、结果还没存下来就进程挂了？不知道工具有没有执行，只能再触发一次（可能副作用执行两次）。

这对于单次短任务问题不大，但对于需要跑几小时、调用外部 API、管理多个子 Agent 的长期任务，这种"一次性架构"是根本缺陷。

Pi Durable 做的事情：**在每个执行步骤后存档，进程死了接着跑**。

**包名**：@earendil-works/pi-durable  
**发布时间**：2026-10-01（与 Pi 1.0 同期）  
**作者**：earendil-works（Earendil）  
**协议**：MIT | 实验性，API 可能变化

---

## 三类 checkpoint，每步都存

Pi Durable 的运行时在每一步之后写入检查点：

| 步骤类型 | 说明 |
|---------|------|
| **模型请求** | 每次向 LLM 发起请求前后都有存档；中断的请求在恢复后重新发送 |
| **工具调用** | 每次工具执行前后存档；具有重放安全性的工具调用在崩溃后重新执行 |
| **压缩（Compaction）** | 长对话的上下文压缩点也作为检查点，避免崩溃后丢失压缩结果 |

**定时器也能穿越重启**。如果 Agent 设置了一个"30 分钟后做某件事"的定时器，进程崩溃重启后，计时器从存档点继续倒计时，不会因为重启而被清除。

---

## requestId：exactly-once 语义

分布式系统里最难解决的问题之一：一个操作被发起了，结果还没确认时进程崩溃，重启后不知道这个操作有没有执行，只能重试，但重试可能导致副作用执行两次。

Pi Durable 的方案：**每次提交都携带 `requestId`**。

如果客户端在崩溃后用同一个 `requestId` 重试，服务端会返回原始提交的结果，而不是把这次请求当成新的请求处理。这是幂等性的标准做法，但 Pi Durable 把它内置进了 Agent 运行时，不需要开发者自己处理。

需要注意的是：**这不能解决所有情况**。如果工具调用和存档之间存在时间窗口（工具已执行、结果还没写入 checkpoint），Pi Durable 无法证明这个外部副作用是否真的发生了——这是分布式系统的根本限制，不是 Pi Durable 的 bug。

---

## 子 Agent 架构

Pi Durable 本身没有内置子 Agent 原语，但设计上对此有直接支持：

- 每个子 Agent 在**各自独立的对话**里运行
- 子 Agent 的状态单独持久化
- 主 Agent 崩溃时，已经在运行的子 Agent 不受影响，继续运行
- 子 Agent 崩溃时，从自己的最后一个 checkpoint 恢复
- 队列中等待处理的消息在任何一方崩溃后仍然保留在队列里

构建一个基础的子 Agent 只需要几行代码：

```ts
import { PiDurable } from "@earendil-works/pi-durable";

const agent = new PiDurable({
  storage: durableStorage,
  model: "claude-opus-4-8",
});

// 崩溃后，agent.resume() 从最后一个 checkpoint 继续
await agent.run(task);
```

---

## Cloudflare 集成

2026-10-02，Cloudflare 官方 changelog 发布了"Run the Pi Durable harness on Cloudflare with the Agents SDK"。

Pi Durable 的 checkpoint 机制天然和 Cloudflare Durable Objects 的持久化模型兼容——Durable Objects 本身就是无服务器架构下的持久化状态容器。集成后，Agent 的 checkpoint 存储在 Durable Object 里，跨请求、跨实例、跨区域都能继续运行。

这对于需要 24/7 持续运行的 Agent 任务有明显意义：不需要维护一个常驻服务器，Cloudflare 的 serverless 基础设施本身就变成了 Agent 的持久化后端。

---

## 和其他方案的区别

同样做持久化/耐久性的方案有很多：

| 方案 | 定位 | 复杂度 |
|------|------|-------|
| **Temporal** | 通用 Durable Workflow 引擎 | 高（需要 Temporal Server + Worker） |
| **LangGraph** | LangGraph 生态的 checkpoint | 中（绑定 LangGraph 框架） |
| **Dagster** | 数据管道 checkpoint | 高（面向数据工程） |
| **Cloudflare Durable Objects** | 边缘持久化状态容器 | 中（Cloudflare 生态） |
| **Pi Durable** | 专为 Pi Agent 运行时设计的轻量层 | 低（npm 包，几行集成） |

Pi Durable 的定位不是通用 workflow engine，它是专门为 Pi 的 Agent 对话结构设计的最小持久化层。如果你已经在用 Pi，这是最低摩擦的选择；如果不在 Pi 生态里，Temporal/LangGraph 可能更合适。

---

## 需要知道的限制

**实验性，API 可能变化**。1.0.0 是版本号，但官方标注为 experimental。生产项目接入前要评估 API 稳定性风险。

**不能解决所有幂等性问题**。工具执行和 checkpoint 之间的时间窗口无法消除，外部副作用（发了一封邮件、扣了一笔款）不能被严格保证只执行一次。

**需要持久化存储后端**。Pi Durable 本身不包含存储，需要配置一个持久化后端（Cloudflare Durable Objects、数据库等）。

**MIT 协议**，商用无限制。模型和基础设施费用另算。

---

## 关键信息

| 字段 | 值 |
|------|----|
| 包名 | @earendil-works/pi-durable |
| 版本 | 1.0.0（实验性） |
| 发布日期 | 2026-10-01 |
| License | MIT |
| 配套项目 | Pi 1.0 |
| Cloudflare 集成 | 2026-10-02 官方 changelog |
| 状态 | 实验性，API 可能变化 |

---

## 综合判断

Pi Durable 解决的是 Agent 工程里一个真实但长期被忽略的问题：长期运行的 Agent 任务在崩溃时怎么办。

它的切入角度很具体——不是建一个完整的 workflow 引擎，而是在 Pi Agent 运行时的每一步之后插入一个 checkpoint，让进程死亡变成一个可以恢复的事件，而不是一个必须重来的灾难。

exactly-once 语义的实现（requestId 幂等提交）是有意思的工程决策——它不假装能解决所有分布式问题，而是在可控范围内（客户端重试时拿回原始结果）提供了一个实用的保证。

Cloudflare 在发布次日就出了集成 changelog，说明这个方向在基础设施侧有明确需求。

限制是清晰的：实验性、需要存储后端、无法解决工具执行窗口内的幂等问题。适合已经在 Pi 生态、需要让任务跑得更长、更不怕崩的开发者。

---

> 开源仅供学习，MIT 协议，商业使用无限制。实验性包，API 可能变化，生产使用需评估稳定性。

---

<!--EN-->

## Pi Durable: Per-Step Checkpointing So Your AI Agent Survives Crashes

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem

Traditional AI agents have a linear lifecycle: start → execute some steps → finish (or crash).

Execute 20 steps, crash at step 18? Start over. A tool call was sent, the result wasn't persisted before the process died? You don't know if the tool ran — you retry it, possibly triggering the side effect twice.

For short single-session tasks, this is acceptable. For long-running tasks — hours of execution, external API calls, multiple sub-agents — the "run-once-and-die" architecture is a fundamental architectural limitation.

Pi Durable's answer: **checkpoint after every step, resume after process death**.

**Package**: @earendil-works/pi-durable  
**Released**: 2026-10-01 (alongside Pi 1.0)  
**Author**: earendil-works (Earendil)  
**License**: MIT | Experimental — API may change

---

### Three Checkpoint Types, After Every Step

Pi Durable's runtime writes a checkpoint after each execution step:

| Step Type | Description |
|-----------|-------------|
| **Model request** | Checkpointed before and after each LLM call; interrupted requests are resent after recovery |
| **Tool call** | Checkpointed before and after each tool execution; replay-safe calls rerun after crashes |
| **Compaction** | Context compression points are also checkpointed; avoids losing compression results on crash |

**Timers survive restarts.** A timer set for "do X in 30 minutes" persists across process death — on restart, the countdown resumes from the checkpoint, not from zero.

---

### requestId: Exactly-Once Semantics

One of distributed systems' hardest problems: a submission was made, the process crashed before the result was confirmed, and now you don't know whether to retry (risking double execution of side effects) or not.

Pi Durable's approach: **every submission carries a `requestId`**.

If a client retries after a crash with the same `requestId`, the server returns the original result rather than treating it as a new submission. Idempotency as a first-class primitive, baked into the agent runtime.

Important caveat: **this doesn't cover everything**. The window between a tool executing and its result being checkpointed cannot be eliminated. If a tool ran but the checkpoint wasn't written before the crash, Pi Durable cannot prove whether the external side effect happened. This is a fundamental distributed systems limit, not a Pi Durable bug.

---

### Sub-Agent Architecture

Pi Durable has no built-in sub-agent primitive, but the design directly supports them:

- Each sub-agent runs in **its own independent conversation**
- Sub-agent state is persisted independently
- When the main agent crashes, running sub-agents continue unaffected
- When a sub-agent crashes, it resumes from its own last checkpoint
- Queued messages remain queued through any crash or restart

Building a basic sub-agent takes a few lines:

```ts
import { PiDurable } from "@earendil-works/pi-durable";

const agent = new PiDurable({
  storage: durableStorage,
  model: "claude-opus-4-8",
});

// After crash, agent.resume() continues from the last checkpoint
await agent.run(task);
```

---

### Cloudflare Integration

On 2026-10-02, the Cloudflare official changelog announced "Run the Pi Durable harness on Cloudflare with the Agents SDK."

Pi Durable's checkpoint model maps naturally onto Cloudflare Durable Objects — persistent state containers in a serverless architecture. After integration, the agent's checkpoints live in Durable Objects, surviving across requests, instances, and regions.

For 24/7 long-running agent tasks, this means no dedicated always-on server: Cloudflare's serverless infrastructure becomes the agent's persistence backend.

---

### Comparison with Other Durability Solutions

| Solution | Scope | Complexity |
|----------|-------|------------|
| **Temporal** | General-purpose durable workflow engine | High (requires Temporal Server + Workers) |
| **LangGraph** | LangGraph ecosystem checkpointing | Medium (framework-bound) |
| **Dagster** | Data pipeline checkpointing | High (data engineering focus) |
| **Cloudflare Durable Objects** | Edge persistent state containers | Medium (Cloudflare ecosystem) |
| **Pi Durable** | Lightweight layer for Pi agent runtime | Low (npm package, few lines of integration) |

Pi Durable isn't a general workflow engine. It's the minimal persistence layer designed specifically for Pi's agent conversation structure. If you're already on Pi, it's the lowest-friction option. For non-Pi ecosystems, Temporal or LangGraph may be better fits.

---

### Limitations to Know

**Experimental — API may change.** Version 1.0.0, but officially marked experimental. Evaluate API stability risk before production adoption.

**Doesn't solve all idempotency problems.** The window between tool execution and checkpoint commit cannot be eliminated. External side effects (email sent, payment charged) cannot be strictly guaranteed to run exactly once.

**Requires a persistent storage backend.** Pi Durable doesn't include storage — you need to configure a durability backend (Cloudflare Durable Objects, a database, etc.).

**MIT license** — commercial use unrestricted. Model and infrastructure costs separate.

---

### Verdict

Pi Durable addresses a real but long-ignored problem in agent engineering: what happens when a long-running agent task crashes?

The approach is specific: don't build a complete workflow engine, just insert a checkpoint after every execution step in the Pi agent runtime. Process death becomes a recoverable event instead of a forced restart.

The exactly-once implementation (requestId idempotent submission) is an interesting engineering decision — it doesn't pretend to solve all distributed problems, but provides a practical guarantee in a controlled scope (clients retrying after crashes get back the original result).

Cloudflare shipping an integration changelog the day after launch signals clear infrastructure-level demand for this direction.

Limitations are clear: experimental, requires a storage backend, can't eliminate the tool execution window for idempotency. Best fit for developers already in the Pi ecosystem who need tasks that run longer and survive failure more reliably.

---

> Open source for learning only. MIT license — commercial use unrestricted. Experimental package; evaluate API stability before production use.
