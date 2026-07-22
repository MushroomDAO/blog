---
title: "22 节课读懂 Agent 系统怎么建：awesome-agent-architecture 的 Harness 工程地图"
titleEn: "22 Lessons to Understand How Agent Systems Are Built: The Harness Engineering Map of awesome-agent-architecture"
description: "hardness1020 开源的 awesome-agent-architecture 用 22 节课、7 个层次，系统拆解 Agent 系统的 Harness 工程——以 Claude Code v2.1.88 和 Hermes Agent 为研究对象，每节包含原理、机制、真实实现和失败模式，附可运行代码。"
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["Agent架构", "Harness工程", "Claude Code", "Hermes Agent", "开源课程", "Agent学习", "多Agent", "循环工程", "MCP", "系统设计"]
heroImage: "../../assets/images/awesome-agent-architecture-22-section-harness-engineering-guide-banner.jpg"
---

> **GitHub**：[hardness1020/awesome-agent-architecture](https://github.com/hardness1020/awesome-agent-architecture) · **Stars**：242  
> **许可**：MIT · **语言**：Python  
> **研究对象**：Claude Code v2.1.88 · Hermes Agent v2026.7.1  
> **运行**：`uv venv && uv pip install -r requirements.txt`

---

## 核心命题

理解 Agent 系统，要先把一件事说清楚：

> **模型负责推理。Harness 给模型行动、状态和限制。**

工具执行、跨调用状态维护、副作用门控、循环协调——这些模型调用本身都不做。**大部分工程量在模型周围，不在模型里。**

这个认知转变很重要。大多数人学 AI 的注意力放在"哪个模型更好"，但真正决定 Agent 能力边界的，是 Harness 的设计：它如何运行工具、如何管理上下文、如何处理错误、如何协调多个子 Agent。

这个仓库的价值正在于此：用 22 个自成体系的章节，把 Harness 从里到外拆开来讲，并且用两个真实系统（Claude Code 和 Hermes Agent）做具体验证。

---

## 基础循环：一切的起点

大多数 Agent 共享同一个控制流：

```
调用模型 → 运行请求的工具 → 追加结果 → 再次调用模型
```

循环本身很小。绝大部分工程是**围绕循环**的：分发工具、门控副作用、管理上下文、持久化状态、协调其他循环。

学会这个框架之后，你会发现：编程工具、聊天助手和自主运行器，大多数差异只是 Harness 选择，不是神秘黑盒。

---

## 22 节课，7 个层次

### Layer 0 · 基础

**S0: Harness 论文** — Agency 从哪里来？

模型 vs Harness 的边界在哪里。什么是行动、观察、权限。这是整个课程的概念基础，建议先读。

---

### Layer 1 · 核心循环（4 节）

这一层讲最基础的机制：循环是怎么跑起来的，工具是怎么被调用的，副作用是怎么被控制的。

**S1: Agent 循环** — `messages[]` 数组怎么增长，`stop_reason` 怎么决定是继续还是停止。

**S2: 工具运行时** — 工具注册表、JSON Schema 校验、分发逻辑、延迟工具搜索（deferred search：不把所有工具一次性加载进上下文）。

**S3: 权限与沙箱** — 副作用门控是 Harness 的安全核心：哪些操作需要审批，如何沙箱隔离高风险工具调用。Claude Code 的 `bypassPermissions` / `acceptEdits` 等模式就在这里讲。

**S4: Hooks** — `PreToolUse` / `PostToolUse` 这类生命周期事件怎么挂载。Hooks 是让外部扩展接入循环的标准接口，不需要修改核心逻辑。

---

### Layer 2 · 复杂工作（4 节）

循环跑起来之后，怎么做比较复杂的任务。

**S5: 规划与待办** — Plan Mode 怎么把大任务拆成 todo list，为什么在实际编辑文件之前需要人类审批计划。

**S6: 子 Agent** — 子 Agent 不是同一个循环里的子调用，而是**全新的 `messages[]` 数组**。子问题在隔离上下文里运行，结果汇报给父 Agent。这是 Claude Code 的 `Agent` 工具工作原理。

**S7: 技能（Skills）** — `SKILL.md` 格式、技能目录、渐进式披露（Progressive Disclosure）：根据任务需要按需加载能力描述，不一次性塞满上下文。

**S8: 上下文管理** — 长会话怎么活在有限的 context window 里：token 预算、内容存根（stub）、压缩、摘要。Claude Code 的自动压缩机制在这里。

---

### Layer 3 · 知识与弹性（3 节）

Agent 怎么记住东西，怎么在出错时活下去。

**S9: 记忆** — 记忆的四个操作：选择（什么值得记）、召回（什么时候用）、提取（从对话里提取事实）、整合（跨会话合并记忆）。

**S10: 系统提示组装** — 系统提示不是静态字符串，而是**每次调用前动态组装的**：基础指令 + 工具描述 + 实时状态（当前目录、待办列表、记忆摘要）+ 缓存断点（cache breakpoints 决定哪些部分可以被 prompt cache 命中）。

**S11: 错误恢复** — 长任务里出错怎么办：重试策略、context 溢出恢复（窗口满了怎么截断而不崩溃）、降级模型（主模型失败时切换）。

---

### Layer 4 · 长期运行与异步（4 节）

这一层把 Agent 从"一次性执行"变成"可以跑很久的后台系统"。

**S12: 任务系统** — 任务记录怎么持久化，依赖关系怎么表达，锁怎么防止并发冲突。这是"关掉终端任务还在跑"的基础。

**S13: 后台执行** — 任务 handle、状态机、通知队列：主循环继续工作的同时，后台任务独立推进，完成后通知主循环。

**S14: 调度** — Cron 触发、sleep 唤醒、远程触发（webhooks）、队列。Agent 怎么在指定时间或外部事件时自动开始工作，不需要人唤起。

**S15: Worktree 隔离** — 多个并行 Agent 怎么避免文件冲突：Git worktrees 给每个子任务一个独立的文件系统视图，`cwd` 绑定确保文件操作不越界，完成后安全合并或丢弃。

---

### Layer 5 · 多 Agent（3 节）

从单个 Agent 到 Agent 团队。

**S16: 协调** — 多个 Agent 怎么通信：收件箱（inbox）、广播、权限冒泡（子 Agent 需要更高权限时如何向上请求，而不是自己绕过）。

**S17: 协议** — Agent 团队怎么达成共识：计划审批流程、关闭握手（一个 Agent 完成任务怎么通知依赖它的其他 Agent 可以继续）。

**S18: 自治** — Agent 怎么自我组织：空闲周期（没有任务时做什么）、任务认领（从任务队列主动拿任务）、自组织（不需要中央调度员）。

---

### Layer 6 · 扩展与集成（2 节）

**S19: MCP / 插件 / 通道** — 传输层（stdio/HTTP SSE/WebSocket）、通道（Channel）怎么让 Harness 触达外部世界、工具池动态组装（从多个 MCP server 合并工具集）。

**S20: 可观测性与评估** — 怎么知道 Agent 在工作：追踪（每一步调用的链路）、指标（工具成功率/token 消耗/延迟）、evals（自动化评估集）、失败分析（什么情况下 Agent 会卡住或产生错误结果）。

---

### Layer 7 · 组合（1 节）

**S21: 循环工程（Loop Engineering）** — 整个课程的终点：多个循环怎么叠加成一个能自我运行的系统。验证循环（inner loop: 完成 → 检查 → 修复）、触发器、token 预算约束、成熟度级别（什么样的 Agent 适合什么样的自治程度）。

---

## 两个真实系统对照

| | **Claude Code v2.1.88** | **Hermes Agent v2026.7.1** |
|---|---|---|
| 定位 | 前沿编程 Agent，编辑文件/运行命令/在真实仓库交付 | 长期助手，记住你/学习工作流/随处运行 |
| 重点读 | 0-21 节全部（最完整的 Harness 实现） | S7/S9/S14/S16/S19/S21（记忆/技能/调度/协调/通道/循环组合）|
| 关键机制 | bypassPermissions/worktree/subagent | 常驻通道/跨会话记忆/技能 marketplace |

课程对每个机制都会对照两个系统说：Claude Code 这样实现，Hermes 那样实现，各自的 tradeoff 是什么。

---

## 四段式学习框架

每一节都遵循同一个结构：

```
1. Opening     — 这一层解决什么问题（为什么需要这个机制）
2. Mechanism   — 通用设计和控制流（不依赖特定系统）
3. Per system  — 真实系统如何实现（Claude Code vs Hermes）
4. Failure modes — 什么会坏，如何缓解
```

**按顺序读**是推荐的学习路径——每一节构建在上一层的基础上。如果跳节，`src/` 里的代码可能引用了上一节还没介绍的机制。

---

## 可运行的代码

```bash
git clone https://github.com/hardness1020/awesome-agent-architecture
cd awesome-agent-architecture
uv venv
uv pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY
```

每一节（S1-S21）有两种运行模式：

```bash
# 离线检查，不需要 API key
python sections/01-agent-loop/src/test.py

# 在线 demo，调用真实 API
uv run python sections/01-agent-loop/src/demo.py
```

**最有价值的学习动作**：diff 相邻节的 `src/`。每一节只添加一个机制，所以 `git diff sections/01-agent-loop/src/ sections/02-tool-runtime/src/` 精确地展示了"工具运行时"这一个机制是怎么加进来的。

---

## 与已有内容的关系

我们之前写过[《从控制论看 Harness 设计》](/blog/agent-architecture-cybernetics-harness-design/)，那篇文章建立了概念框架：Harness ≈ 设计模式，都可以用控制论解释。

`awesome-agent-architecture` 是这个框架的具体实现路径：22 节课把控制论的抽象原理，落地为可以逐节读、可以运行 demo、可以 diff 代码的工程学习资料。

**两篇互补**：概念框架 → 工程实现路径。

---

## 核心判断

这是目前见过的**对 Harness 工程理解最系统**的开源学习资源：不是泛泛的"什么是 Agent"介绍，而是从源码层面拆解真实系统的机制，用统一的分析框架（4段式）让不同系统的实现可以直接对比。

242 Stars，开源 1 个月——比较小众，但质量高于大多数 100 倍 Stars 的"awesome-X"列表。

如果你在构建 Agent 系统，从 S0 到 S21 过一遍，大约能把"Harness 里有什么、每个部分干什么、会怎么坏"这三个问题回答清楚。这三个问题答清楚了，读任何 Agent 系统的代码都会快很多。

---

## 参考资源

- **GitHub**：[hardness1020/awesome-agent-architecture](https://github.com/hardness1020/awesome-agent-architecture)
- **Hermes Agent**：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Loop Engineering（LangChain）**：[The art of loop engineering](https://www.langchain.com/blog/the-art-of-loop-engineering)
- **Lilian Weng**：[Harness engineering for self-improvement](https://lilianweng.github.io/posts/2026-07-04-harness/)
- **相关文章**：[从控制论看 Harness 设计](/blog/agent-architecture-cybernetics-harness-design/)

© 2026 Author: Mycelium Protocol
