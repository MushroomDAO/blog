---
title: "读 cordiverse/paper：为什么「可逆副作用」是插件系统最难的问题，以及它对 AI Agent 自我净化意味着什么"
titleEn: "cordiverse-cordis-spatiotemporal-composability-plugin-paradigm-paper"
description: "cordiverse/paper 是支撑 DeepSeek Harness 底层框架 Cordis 的学术论文草稿（2026-08-13）。论文提出「时空可组合性」编程范式：时间可组合性（Temporal Composability）保证插件卸载时能完全撤销副作用，空间可组合性（Spatial Composability）保证插件之间的依赖关系可以响应式管理。这两个特性合在一起，让 AI Agent 运行时真正实现「热替换」——哪个组件出问题，换掉它，不重启整个系统。从工程角度分析：这正是长程 Agent 自我净化（Self-Purification）的理论基础。"
descriptionEn: "cordiverse/paper is the academic preprint (2026-08-13) behind Cordis, the framework powering DeepSeek Harness. It proposes a 'Spatiotemporal Composability' programming paradigm: Temporal Composability ensures a plugin's side effects are fully reversible upon removal; Spatial Composability enables reactive management of inter-component dependencies. Together they enable hot-swapping in an Agent runtime — replace a faulty component without restarting the whole system. Engineering analysis: this is the theoretical foundation for long-horizon Agent self-purification."
pubDate: "2026-08-14"
updatedDate: "2026-08-14"
category: "Tech-News"
tags: ["学术论文", "插件系统", "Cordis", "形式化方法", "Agent架构", "自我净化", "可逆副作用", "DeepSeek"]
heroImage: "../../assets/images/cordiverse-cordis-spatiotemporal-composability-plugin-paradigm-paper-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

论文：[A Programming Paradigm for Spatiotemporal Composability](https://github.com/cordiverse/paper/blob/main/paper.pdf)  
发布于：cordiverse/paper  
状态：2026-08-13 草稿（preprint，仍在修订）  
实现：Cordis（deepseek-harness 的底层框架）

---

这篇论文是 DeepSeek Harness 底层框架 Cordis 的学术支撑。第一次看到它，是从 dsh README 里的一行引用：

> "powered by Cordis, whose design is described in *A Programming Paradigm for Spatiotemporal Composability*"

读完之后，我意识到它解决的是一个比「插件系统」更深的问题——它在问：**当一个软件系统需要在运行时动态改变自身组成，这件事在数学上应该怎么表达，以及实现者需要保证什么性质？**

这个问题对 AI Agent 运行时有直接工程意义。

---

## 一、论文要解决的问题

### 问题的两个维度

现代软件越来越需要「动态组合」（dynamic composition）——插件系统、自我演化的 Agent Harness 都是典型场景。但这个问题的形式化基础一直不完善。论文将其分解为两个正交维度：

**时间可组合性（Temporal Composability）**：
> 当一个组件被移除时，能够完全撤销它产生的副作用。

举例：你加载了一个为 Agent 注册了三个工具的插件。卸载这个插件时，这三个工具应该自动消失，不留下任何遗留状态。这听起来简单，但在实际系统里经常出问题——引用计数没有释放、全局变量没有清理、事件监听器没有取消注册……

**空间可组合性（Spatial Composability）**：
> 组件之间的依赖关系能够被响应式地声明和管理。

举例：插件 A 依赖插件 B 提供的 `ctx.llm` 服务。当插件 B 被替换成插件 C 时，插件 A 应该自动适应，而不是继续持有对旧实现的引用。这是「响应式 coeffect」解决的问题。

---

## 二、论文的核心概念

### 可逆副作用（Revertible Effects）

论文形式化了「可逆副作用」——每一次上下文变换（context transformation）都携带一个逆操作，运行时负责追踪。当插件卸载时，运行时按逆序执行所有逆操作，完全撤销副作用。

这个概念在 Cordis 里的具体体现：每个 `ctx.xxx = value` 的注册都是一个可逆 effect，卸载时自动 undo。在 dsh 里，注册工具、注册事件监听、添加 Prompt section，全部遵循这个契约。

### 响应式 Coeffect（Reactive Coeffects）

Coeffect 是「效应的对偶」——effect 是组件对上下文的贡献，coeffect 是组件对上下文的读取。响应式 coeffect 意味着：当你读取的上下文发生变化时，你的组件会收到通知并重新计算。

在 Cordis 里，这是插件依赖解析的基础——当 `ctx.llm` 被替换时，所有依赖它的组件会感知到变化并作出反应，而不是持有过时的引用。

### Context Type：Effect 和 Coeffect 的统一

论文将这两个 Context（effect context 和 coeffect context）统一成一个「context type」，形成完整的编程范式。再加上 Component 的概念和动态组合的演算，就得到了一个可以证明具有时空可组合性的系统。

---

## 三、读后感：为什么这件事在 2026 年被提出

### 工程现实是论文动机

这篇论文不是从纯理论出发的——它的动机来自工程现实：插件系统和自我演化的 Agent Harness 在实践中大量出现，但它们的形式化基础「仍然不完善（remain underdeveloped）」。

这意味着绝大多数现有的插件系统是工程上的正确，而不是数学上的正确——没有人能够严格证明「卸载一个插件后，系统状态和没有加载过这个插件完全等价」。Cordis 试图把这件事变成可证明的属性。

### 对「自我净化 Agent」的意义

论文里有一句话值得特别注意：

> *self-evolving agent harnesses — increasingly requires dynamic composition, yet its formal foundations remain underdeveloped.*

这直接点出了目标：**自我演化的 Agent Harness**。

一个能够「自我净化」的 AI Agent 系统需要满足什么条件？

1. **能够识别问题组件**：观测系统需要能定位到具体是哪个插件、哪个工具、哪段逻辑出了问题。
2. **能够安全卸载问题组件**：不能因为卸载一个坏的组件而把整个系统拖垮，或者留下遗留状态。
3. **能够热插入替换组件**：新组件上线时，依赖它的其他组件能自动适应，不需要重启。

时间可组合性解决了第 2 点（安全卸载），空间可组合性解决了第 3 点（依赖自动适应），而可观测性基础设施解决了第 1 点。三者加在一起，才构成真正的「自我净化」能力。

---

## 四、从工程角度的指导意见

### 4.1 用于 AI Agent 系统的实践方向

**Cordis 作为 Agent 基础设施**：

如果你正在设计一个长程 Agent 运行时，Cordis 的设计值得借鉴——不一定直接使用 Cordis（它是 TypeScript 生态），但它的设计原则可以迁移：

- **所有组件注册都应该是可逆的**：注册工具时同时注册撤销回调；加载模型 adapter 时同时记录如何卸载它。
- **不要共享全局可变状态**：全局状态是时间可组合性的最大敌人。用 Context injection 替代全局变量。
- **依赖应该是声明式的，而不是命令式的**：不是「在启动时获取 LLM adapter 的引用」，而是「声明我依赖 `ctx.llm`，当它变化时通知我」。

**检查你的 Agent 是否真正可逆**：

一个测试方法：加载一个工具插件，然后卸载它，然后再加载。如果系统状态和从未加载过这个插件完全相同，你的实现是时间可组合的。如果有任何差异（多余的 listener、遗留的状态、内存泄漏），你的实现不满足时间可组合性。

### 4.2 「自我净化」的工程实现路径

基于论文的理论框架，一个具备自我净化能力的 Agent 系统在工程上应该具备：

**1. 插件级别的可观测性**（而不只是会话级别）

不只是记录「Agent 执行了什么」，还要记录「哪个插件/工具调用产生了什么副作用」。这样才能在出问题时定位到具体组件。

**2. 组件替换不停机**

当检测到某个工具插件行为异常时，能够在不中断当前 Agent 会话的情况下卸载它、替换成修复版本、让 Agent 从断点继续。这需要时间可组合性的保证。

**3. 依赖图的运行时感知**

在替换一个组件之前，需要知道哪些其他组件依赖它，以及替换之后它们能否自动适应。这需要空间可组合性提供的依赖图。

**4. 降级策略**

当某个组件不可用时，有能力降级到更保守的行为（例如：某个特定工具挂了，退回到不使用该工具的策略），而不是让整个 Agent 崩溃。这需要 Coeffect 的「找不到依赖时怎么办」的明确合约。

### 4.3 Cordis 在非 TS 生态的移植建议

如果你在 Python 生态里想实现类似的东西：

- **可逆 effects**：用 context manager 实现，`__enter__` 注册，`__exit__` 撤销
- **响应式 coeffects**：用观察者模式或 reactive 库（如 `rx-python`）实现
- **Component lifecycle**：可以借鉴 FastAPI 的 lifespan 机制，但需要支持嵌套和动态加载

完整实现参考：可以研究 Cordis 的 TypeScript 实现，然后用 Python 的 `contextlib.contextmanager`、`weakref`、`asyncio` 构建等价语义。

---

## 五、论文的局限性与开放问题

论文还是 2026-08-13 的草稿，作者明确说明「内容可能发生重大变化」。

几个开放问题值得关注：

**性能开销**：可逆副作用意味着运行时需要维护 effect 的 inverse 链表。在高频操作（如每次工具调用都注册/注销 effect）下，这个机制的性能开销还不清楚。

**分布式场景**：论文的形式化主要针对单进程内的动态组合。在分布式 Agent 场景（跨机器的多 Agent 协作），时间可组合性如何跨越网络边界，论文没有覆盖。

**学习型组件**：如果一个 AI 组件的「副作用」是模型权重的更新（在线学习场景），可逆性意味着什么？这是论文框架尚未触及的边界。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Reading cordiverse/paper: Why "Revertible Effects" Is the Hardest Problem in Plugin Systems, and What It Means for AI Agent Self-Purification

*by Mycelium Protocol*

---

Paper: [A Programming Paradigm for Spatiotemporal Composability](https://github.com/cordiverse/paper/blob/main/paper.pdf)  
Status: Draft as of 2026-08-13 (active preprint)  
Implementation: Cordis (the framework powering DeepSeek Harness)

---

This paper is the academic foundation of Cordis, the framework under DeepSeek Harness. When reading dsh's README, a single line caught my attention:

> "powered by Cordis, whose design is described in *A Programming Paradigm for Spatiotemporal Composability*"

After reading it, I realized it's solving something deeper than "a plugin system" — it's asking: **when a software system needs to dynamically change its own composition at runtime, how should this be expressed mathematically, and what properties must the implementation guarantee?**

This question has direct engineering relevance for AI Agent runtimes.

---

### The Two Dimensions of the Problem

**Temporal Composability**: When a component is removed, its side effects can be completely reversed.

Real example: a plugin registers three tools for an Agent. When unloaded, those tools disappear with zero residual state. This sounds simple but routinely fails — reference counts don't release, global variables don't clear, event listeners don't deregister.

**Spatial Composability**: Dependencies between components can be declared and reactively managed.

Real example: Plugin A depends on `ctx.llm` provided by Plugin B. When Plugin B is replaced by Plugin C, Plugin A automatically adapts — it doesn't keep a stale reference to the old implementation.

---

### Core Concepts

**Revertible Effects**: Every context transformation carries an inverse operation tracked by the runtime. When a plugin unloads, the runtime executes all inverses in reverse order, fully undoing the side effects. In Cordis: every `ctx.xxx = value` registration is a revertible effect that auto-undoes on unload.

**Reactive Coeffects**: Coeffects are the dual of effects — how a component reads from the context. Reactive coeffects mean: when the context you're reading changes, you're notified and recomputed. In Cordis: when `ctx.llm` is swapped, all components depending on it react automatically.

**Context Type**: The paper unifies both effect context and coeffect context into a single "context type," forming the complete programming paradigm with formal metatheory.

---

### What This Means for Agent Self-Purification

The paper explicitly targets self-evolving agent harnesses. A system with genuine self-purification capability needs three things:

1. **Identify faulty components** — observability at the plugin level, not just session level
2. **Safely remove faulty components** — temporal composability: unloading leaves no residual state
3. **Hot-swap replacement components** — spatial composability: dependencies auto-adapt, no restart needed

The paper provides the theoretical foundation for points 2 and 3. Observability infrastructure handles point 1. Together, they constitute a genuine self-purification capability.

---

### Engineering Guidance

**For any Agent runtime design:**
- All component registrations should be reversible — register a cleanup callback alongside every registration
- Never use shared global mutable state — use Context injection instead
- Declare dependencies, don't command them — not "get the LLM adapter at startup" but "I depend on `ctx.llm`; notify me when it changes"

**A litmus test for temporal composability:** Load a plugin, unload it, then check if the system state is identical to never having loaded it. Any difference (stray listeners, leaked state, unreleased memory) means temporal composability is not satisfied.

**Path to self-purification in practice:**
1. Plugin-level observability: record which plugin/tool produced which side effect
2. No-downtime component replacement: swap faulty components without interrupting running Agent sessions
3. Runtime dependency graph: before replacing a component, know what depends on it
4. Graceful degradation: when a component is unavailable, fall back rather than crash

---

### Open Questions

The paper is still a draft. Key unresolved areas:

- **Performance overhead** of maintaining effect inverse chains for high-frequency operations
- **Distributed scenarios** — temporal composability across network boundaries isn't covered
- **Learning components** — if a component's "side effect" is a model weight update (online learning), what does reversibility mean?

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
