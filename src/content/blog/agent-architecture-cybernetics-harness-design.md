---
title: "读后感：Agent 架构的底层逻辑——从控制论看 Harness 设计"
titleEn: "Commentary: The Deep Logic of Agent Architecture — Designing Resilient Agents Through a Cybernetics Lens"
description: "读完小红书博主碳基智的《Harness ≈ 设计模式，都可以用控制论解释》后，从工程架构角度的延伸思考：同一套控制论原理，在 OOP 里是隐式的设计模式，在 AI Agent 里必须显式化为 Harness。那么，一个真正有弹性且完备的 Agent 究竟应该怎么设计？"
descriptionEn: "A commentary on the XiaoHongShu essay 'Harness ≈ Design Patterns, Both Explainable by Cybernetics,' extended into an architectural framework: how to design an agent that is both resilient and complete, using cybernetics as the underlying lens."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-Experiment"
tags: ["AI Agent", "Harness", "控制论", "设计模式", "架构设计", "弹性系统", "Agent设计"]
heroImage: "../../assets/images/agent-architecture-cybernetics-harness-design-banner.jpg"
---

> 本文是对小红书博主**碳基智**的文章[《Harness ≈ 设计模式，都可以用控制论解释》](https://www.xiaohongshu.com/discovery/item/6a2927460000000017028c5f)的读后感与延伸思考。原文观点精准，推荐直接去看原文和配图。

---

读完碳基智的这篇文章，我在白板上画了半小时才把思路理清楚。

文章的核心论断是：**同一套控制论（Cybernetics）原理，在 OOP 里的实现叫设计模式，在 AI Agent 里的实现叫 Harness**。两者不是平行关系，是同一件事的两个不同时代的表达。

这个洞察很准。但它引出了一个我更关心的工程问题：

**如果我们承认 Harness 就是控制论，那一个"有弹性且完备"的 Agent，应该怎么设计？**

---

## 先把原文的核心框架说清楚

碳基智的图做得很好，三列对照：

```
Cybernetics 控制论
    ├─ Feedback 反馈        → OOP: Observer 观察者      → Agent: Evaluate Loop 评估循环
    ├─ Homeostasis 稳态     → OOP: Strategy 策略        → Agent: Agent Router 智能路由
    ├─ Hierarchy 层次       → OOP: Chain of Resp.       → Agent: Agent Chain 智能体链
    ├─ Information 信息     → OOP: Mediator 中介者       → Agent: Context Manager
    ├─ Procedural 过程控制  → OOP: Template Method      → Agent: Workflow Scaffold
    ├─ Construction 构造    → OOP: Builder 建造者        → Agent: Prompt Chain 提示链
    ├─ Abstraction 抽象边界 → OOP: Facade 外观           → Agent: Dialog Gateway 对话网关
    └─ Interception 拦截    → OOP: Decorator 装饰器      → Agent: Middleware 中间件层
```

文章里的关键差异点是：

> "在 OOP 里，Observer 的反馈回路藏在代码逻辑中。但在 AI 系统里，控制回路必须被显式地设计和实现。因为 LLM 本身是不可控的，你不可能靠隐式约定来保证行为。"

**这句话是整篇文章最值钱的地方。**

在 OOP 里，Observer 模式的实现是由编译器和运行时保证执行的——你写了 `subscribe()`，它就一定会被调用。代码本身就是控制回路的实体。

但 LLM 不是这样运作的。你给它一段 prompt，它有可能按你说的做，也有可能"发挥创意"。控制回路如果不显式写出来，就不存在。

这就是为什么 Harness 必须把每一个控制机制都明文化：CLAUDE.md 是约束声明，skill 文件是行为规范，评估 Agent 是反馈回路的实体化，middleware 是拦截机制的物理存在。

---

## 延伸：什么叫"有弹性且完备"的 Agent

理解了上面的框架之后，"弹性"和"完备"在控制论语言里有了精确的定义。

**完备**（Complete）：覆盖控制论的所有 8 个维度，没有缺失的控制回路。

**弹性**（Resilient）：每个控制回路在出错时有降级路径，系统不会因为单点失效而全面崩溃。

用这两个标准来审视，大多数"Agent"系统的问题立刻就清晰了——

---

### 常见的不完备（缺失控制回路）

**1. 没有 Evaluate Loop（反馈回路缺失）**

最常见的失败模式：Agent 执行完任务，直接返回结果，没有自我评估环节。

```
❌ LLM → 执行 → 返回结果
✅ LLM → 执行 → 评估质量 → 如果不达标 → 重试/改进 → 返回结果
```

在 Alberta Harness 里，四色 Agent（红蓝绿黄）就是评估回路的物理化。每次提交都要过 95 个检查项，不通过不能继续。这就是 Observer 模式在 AI 里的显式实现。

**2. 没有 Context Manager（信息回路缺失）**

Mediator 模式在 OOP 里解决的是"对象之间不直接通信，通过中介者协调"。在 Agent 里对应的是上下文管理：谁持有 context、怎么传递、怎么压缩、怎么注入。

大多数简单 Agent 的做法是把所有东西塞进一个超长 prompt，直到撑爆 context window。这不是信息管理，这是信息堆积。

**3. 没有 Agent Router（稳态机制缺失）**

Strategy 模式的本质是：面对不同环境变化，系统能切换到最优策略，维持稳态运行。

在 Agent 里，这对应的是路由层：根据任务类型、工具可用性、当前负载，把请求分发到合适的子 Agent 或工具链。

没有路由层的 Agent，一旦遇到"默认路径"不能处理的输入，就只能失败。有路由层的 Agent，会尝试降级到备用路径。

---

### 常见的不弹性（控制回路缺少降级）

**1. 硬依赖外部工具，没有 fallback**

```
❌ 调用 API → 失败 → 整个 Agent 崩溃
✅ 调用 API → 失败 → 换备用 API → 还失败 → 告知用户 + 记录错误 → 优雅退出
```

Decorator/Middleware 模式的价值在这里：它是拦截层，可以在不修改核心逻辑的前提下，加入重试、超时、熔断。

**2. Evaluate Loop 只有一个评估标准**

评估如果只有"对/错"，弹性就很差——一旦评估器本身出问题（比如评估 prompt 被注入），整个系统就失控了。

弹性的评估回路应该是多层的：
- 第一层：确定性规则检查（有就是有，没有就是没有）
- 第二层：LLM 判断（概率性，可能出错）
- 第三层：人工兜底（critical path 必须有）

**3. Agent Chain 是线性的，没有异常分支**

Chain of Responsibility 模式的关键不只是"传下去"，还有"传不下去怎么办"。很多 Agent Chain 的设计只有 happy path，遇到任何一个节点失败，整链就断了。

---

## 一个实用的检查清单

基于控制论框架，评估一个 Agent 系统是否"完备且有弹性"：

| 控制论维度 | 检查项 | 弹性要求 |
|---|---|---|
| Feedback | 是否有评估回路？ | 评估失败时有默认策略吗？ |
| Homeostasis | 是否有路由/降级策略？ | 主路径失败能切换备用吗？ |
| Hierarchy | Agent 链是否有明确层级？ | 某节点失败能跳过或重路由吗？ |
| Information | 上下文如何管理和传递？ | Context 过长时如何压缩？ |
| Procedural | 是否有固定的执行骨架？ | 某步骤失败能继续后续步骤吗？ |
| Construction | Prompt 是否分步构建？ | 构建失败能回滚到上一步吗？ |
| Abstraction | 是否有统一的对话入口？ | 入口失败能直接透传到子系统吗？ |
| Interception | 是否有中间件层（日志/安全/限流）？ | 中间件挂了会影响主流程吗？ |

---

## 从控制论推导出的设计原则

**原则一：每一层都是控制回路，不是单向管道**

很多人把 Agent 设计成流水线：输入 → 处理 → 输出。但正确的心智模型是环状的：输出的质量会反馈回来影响下一次的处理策略。没有反馈的管道不是控制系统，是传送带。

**原则二：显式优于隐式，在 AI 系统里这是生存法则**

OOP 可以靠隐式约定——接口类型、调用顺序、运行时保证。LLM 不行。任何你没有显式写出来的控制逻辑，都等于没有。

这不是 LLM 的缺陷，是它的特性：它是一个概率采样系统，不是确定性执行器。

**原则三：弹性是设计出来的，不是测出来的**

你不能在系统写完之后"加弹性"。弹性是架构决策：每个控制回路在设计时就要同时设计它的降级路径。就像电路设计里的保险丝，不是在电路烧掉之后再装的。

**原则四：Harness 的价值不在于限制，在于让限制可见**

碳基智提到 Harness 的本意是"马具"——约束野马。但好的马具不是让马跑不动，是让骑手能掌控方向。

Harness 的价值是把所有的"应该怎么做"写成显式规范，让 Agent 的行为从"随机但大体正确"变成"可预测且可审计"。这不是在削弱 LLM 的能力，是在让它的能力变得可信任。

---

## 最后

碳基智的文章解答了一个我之前一直觉得有点玄的问题：为什么 Harness 的那些东西（CLAUDE.md、skill 文件、评估 Agent）会有效？

现在有了清晰的答案：因为它们都是控制论元素的显式实现。不是魔法，是工程。

范式在变，控制论不变。这句话值得贴在每一个 Agent 系统的设计文档第一页。

---

**参考来源：**
- 原文：[碳基智 · 小红书《Harness ≈ 设计模式，都可以用控制论解释》](https://www.xiaohongshu.com/discovery/item/6a2927460000000017028c5f)
- [GovAlta/COMMON-HARNESS](https://github.com/GovAlta/COMMON-HARNESS) — Alberta 政府开源 Harness 实现，MIT
- [The Velocity White Papers](https://thevelocitywhitepapers.com) — Alberta 省政府 AI 工程方法论白皮书

© 2026 Author: Mycelium Protocol

<!--EN-->

## Commentary: The Deep Logic of Agent Architecture — Designing Resilient Agents Through a Cybernetics Lens

> This article is a commentary and extension of XiaoHongShu author **碳基智 (TanJiZhi)**'s post ["Harness ≈ Design Patterns, Both Explainable by Cybernetics."](https://www.xiaohongshu.com/discovery/item/6a2927460000000017028c5f) The original post is excellent — go read it.

After reading the post, I spent half an hour at a whiteboard before things clicked. The core thesis: **the same Cybernetics principles that underlie OOP Design Patterns also underlie AI Agent Harnesses.** They're not parallel ideas — they're the same idea expressed in two different eras.

This is a solid observation. But it leads directly into the engineering question I care about more: **if a Harness is just applied Cybernetics, how should we design an agent that is both resilient AND complete?**

---

### The Framework

The original post's three-column diagram maps it out cleanly:

```
Cybernetics              OOP Design Pattern        AI Agent Harness
Feedback           →     Observer                → Evaluate Loop
Homeostasis        →     Strategy                → Agent Router
Hierarchy          →     Chain of Responsibility → Agent Chain
Information        →     Mediator                → Context Manager
Procedural Control →     Template Method         → Workflow Scaffold
Construction       →     Builder                 → Prompt Chain
Abstraction        →     Facade                  → Dialog Gateway
Interception       →     Decorator               → Middleware
```

The key insight from the original: in OOP, control loops are *implicit* — the Observer's feedback loop lives in code logic you have to read to find. In AI systems, **control loops must be explicitly designed.** LLMs are probabilistic samplers, not deterministic executors. Implicit conventions don't hold.

---

### Complete vs. Resilient

With Cybernetics as the framework, "complete" and "resilient" get precise definitions:

**Complete**: all 8 Cybernetics dimensions have explicit implementations. No missing control loops.

**Resilient**: every control loop has a degradation path. Single failures don't cascade into total system collapse.

Most "agents" fail on both counts.

**Common completeness failures:**
- No Evaluate Loop — agent executes, returns, done. No self-assessment.
- No Context Manager — everything crammed into one giant prompt until the window blows.
- No Agent Router — one path, one failure mode.

**Common resilience failures:**
- Hard-coded tool dependencies with no fallback
- Single-criterion evaluation (binary pass/fail with no backup)
- Linear Agent Chains with no exception branches (only a happy path)

---

### Design Principles

**1. Every layer is a control loop, not a pipeline stage.** The right mental model is circular: output quality feeds back to affect next-round processing strategy. A pipeline without feedback is a conveyor belt, not a control system.

**2. Explicit beats implicit — in AI systems this is survival.** OOP can rely on implicit contracts (type interfaces, runtime guarantees). LLMs cannot. Any control logic you haven't explicitly written down doesn't exist.

**3. Resilience is designed in, not tested in.** You can't bolt resilience onto a finished system. Every control loop needs its degradation path at design time. Like a circuit breaker — not something you add after the circuit burns.

**4. A Harness doesn't limit capability — it makes capability trustworthy.** The point of a harness (literally: equipment that lets a rider steer a horse) is not to stop the horse from running. It's to make the power directional. A good Harness turns "probably correct" LLM output into "predictable and auditable" system behavior.

---

### Quick Audit Checklist

| Cybernetics Dimension | Check | Resilience Question |
|---|---|---|
| Feedback | Is there an eval loop? | What happens when evaluation fails? |
| Homeostasis | Is there routing/fallback? | Can you switch to a backup path? |
| Hierarchy | Is the agent chain layered? | Can a failed node be skipped? |
| Information | How is context managed? | What happens when context overflows? |
| Procedural | Is there a fixed execution skeleton? | Can later steps run if one fails? |
| Construction | Is the prompt built incrementally? | Can you roll back a failed build step? |
| Abstraction | Is there a single dialog entry point? | If the gateway fails, can you bypass it? |
| Interception | Is there middleware (log/security/rate-limit)? | Does middleware failure break the main flow? |

---

The range of expression changes. Cybernetics doesn't. That sentence belongs on page one of every agent system design doc.

---

**References:**
- Original post: [碳基智 on XiaoHongShu](https://www.xiaohongshu.com/discovery/item/6a2927460000000017028c5f)
- [GovAlta/COMMON-HARNESS](https://github.com/GovAlta/COMMON-HARNESS) — Alberta Government open-source Harness, MIT
- [The Velocity White Papers](https://thevelocitywhitepapers.com)

© 2026 Author: Mycelium Protocol
