---
title: "Loop Engineering：AI Agent 系统的第四层工程，设计循环，不只是设计提示词"
titleEn: "Loop Engineering: The Fourth Engineering Layer for AI Agent Systems — Design Loops, Not Just Prompts"
description: "awesome-loop-engineering 是一个为「循环型 AI Agent 系统」构建的知识图谱：545 个来源审计过的资源、20 个运行模式、20 个循环契约、8 个可运行的 runtime 起点。Loop Engineering 是提示词工程/上下文工程/框架工程之上的第四层，专门治理 Agent 工作随时间循环、验证、持久化状态、决定下一步行动的方式。"
descriptionEn: "awesome-loop-engineering is a knowledge base for recurring AI agent systems: 545 source-audited resources, 20 operational patterns, 20 loop contracts, and 8 runtime starters. Loop Engineering is the fourth layer above prompt, context, and harness engineering — it governs how agent work repeats, verifies results, persists state, and decides what happens next over time."
pubDate: "2026-07-18"
updatedDate: "2026-07-18"
category: "Tech-Experiment"
tags: ["AI Agent", "Loop Engineering", "循环系统", "Agent工程", "提示词工程", "Claude Code", "Codex", "多智能体"]
heroImage: "../../assets/images/awesome-loop-engineering-agent-loops-guide-banner.jpg"
---

> **GitHub**：[ChaoYue0307/awesome-loop-engineering](https://github.com/ChaoYue0307/awesome-loop-engineering)  
> **交互网站**：[chaoyue0307.github.io/awesome-loop-engineering](https://chaoyue0307.github.io/awesome-loop-engineering/)  
> **规模**：545 个审计资源 · 20 个运行模式 · 20 个循环契约 · 8 个 runtime 起点

---

## 从一个问题开始

你写了一个 AI Agent，它能搜索信息、生成代码、调用工具。

但是：**它每次都需要你手动触发、手动判断结果、手动决定下一步**。

如果你希望它「每两小时检查一次 PR 状态」「当 CI 失败就自动修复」「每周整理一次知识库」——你就面临一个新问题，不再是「怎么写提示词」，而是：**怎么让 Agent 工作正确地循环下去？**

这就是 Loop Engineering 要解决的问题。

---

## 四层工程栈

awesome-loop-engineering 提出的核心模型是一个四层栈：

| 层级 | 名称 | 解决什么问题 |
|---|---|---|
| 01 | **Prompt Engineering** | 如何在一次模型调用中给出好的指令 |
| 02 | **Context Engineering** | 如何给 Agent 加载正确的状态、记忆、文档 |
| 03 | **Harness Engineering** | 如何为单次运行提供工具、权限、沙箱、追踪 |
| 04 | **Loop Engineering** | 如何治理 Agent 工作随时间循环、验证、持久化、决策 |

**前三层改进的是一次运行。Loop Engineering 治理的是随时间重复的工作。**

这个区别很关键。提示词写得再好，如果没有循环治理，Agent 仍然：
- 无法从上次失败中学习
- 无法在没有人值守的情况下安全地重试
- 无法在达到目标时干净地停止
- 无法在超出边界时正确地上报人类

---

## 循环契约：11 个显式决策替代隐式默认值

Loop Engineering 的核心工件是 **Loop Contract**（循环契约）——一个循环 Agent 任务的运行规范。

为什么需要契约？因为在有人监督的会话里，人类随时补充判断；一旦 Agent 被调度自动运行，所有未回答的问题都变成了**隐性默认值**。这些默认值可能导致 Agent 选错任务范围、批准自己的输出、在没有停止规则的情况下无限重试。

契约把这些默认值变成可审查的策略，包含 11 个字段：

**设置阶段（建立边界）**

| 字段 | 内容 |
|---|---|
| **Objective** | 命名目标——Agent 要实现什么 |
| **Trigger** | 什么启动这个循环（定时、事件、队列、条件） |
| **Intake** | 把目标/事件/队列信号转换成有边界的工作包的规则 |
| **Workspace** | 隔离的工作空间和权限边界 |

**运行阶段（执行+证明+记录）**

| 字段 | 内容 |
|---|---|
| **Context** | Agent 能看到什么（当前状态、记忆、文档、例子） |
| **Delegation** | 工作如何路由给 Agent 团队 |
| **Verification** | 什么算「完成」——外部测试、评估、追踪，或人类审查 |
| **State** | 什么需要在上下文重置和下次运行之间存活 |

**治理阶段（限制自主性）**

| 字段 | 内容 |
|---|---|
| **Budget** | 重试次数上限、运行时间上限、并发上限 |
| **Escalation** | 什么情况升级给人类（架构决策、反复失败、冲突） |
| **Exit** | 什么是成功退出，什么是受阻退出 |

**+ Next Action**：下一步是重复、上报、升级，还是停止。

---

## PR 保姆：一个完整的契约实例

文档里用「PR 保姆」作为工作示例，帮助理解契约的完整形态：

**触发 + 摄入**  
每两小时在工作时段运行一次，以及在请求修改或检查失败后触发。只处理一个 PR 上的明确阻塞点。

**权限边界**  
使用专用 branch 或 worktree。允许：窄范围修复、检查、进度评论。禁止：force push、依赖升级、secrets、生产变更。

**团队 + 上下文**  
探索者找到最小阻塞点，实现者修复它，审查者用最新 SHA + review 线程 + CI 日志 + 仓库说明检查范围。

**证据 + 状态**  
必要检查必须通过，线程必须解决，diff 必须保持窄范围。命令、检查 URL、修改的文件、阻塞点、下一步行动在每次运行后都要持久化。

**预算 + 交接**  
3 次重试或 60 分钟后停止。架构问题、反复失败、reviewer 分歧、任何需要 force push 的情况——升级给人类 owner。

---

## 20 个运行模式

项目把常见的循环 Agent 场景归纳成 20 个模式，每个模式都有明确的「完成定义」：

**构建 & 维护**
- **PR 保姆**：保持 PR 向前推进——检查通过、review 线程解决、merge 状态最新
- **CI 修复循环**：原始失败命令通过范围内补丁后停止
- **文档偏移收集器**：已验证的不匹配被修复且示例仍可运行
- **依赖分类循环**：安全更新通过测试，高风险升级有负责人
- **Bug 猎取循环**：每个被接受的发现有复现步骤或失败测试
- **发布说明循环**：每个已发布变更映射到来源和受众

**运行 & 观察**
- **部署验证器**：合成检查和发布阈值保持在策略范围内
- **事件响应循环**：影响、证据、时间线、负责人被记录
- **数据质量循环**：硬质量规则在版本提升前通过
- **成本控制循环**：在可比工作上花费降低且无质量回退
- **模型路由循环**：路由满足质量/延迟/隐私/成本容忍度
- **性能回归循环**：受控基准确认恢复和正确性

**学习 & 优化**
- **反馈聚类器**：主题引用来源，频率与严重程度分开
- **评估回归循环**：目标评估返回基线，评分标准不变
- **基准优化循环**：重复测量改进，受保护指标不变
- **知识新鲜度循环**：语料库通过来源、新鲜度、检索、泄漏门控

**治理 & 保护**
- **安全审查循环**：发现引用证据，审批边界保持完整
- **企业审批循环**：每个门控有记录的人类决策和审计追踪
- **无障碍回归循环**：精确回归被修复，人类标准被批准
- **对抗性红队循环**：发现被复现、最小化、报告、回归测试

---

## 6 步生命周期

每次循环运行经过 6 个阶段：

```
Intake → Delegate → Act → Verify → Persist → Decide
                                       ↓
                          Retry（带证据） / Escalate（交人类） / Exit（目标达成）
```

关键设计原则：
- **行动者不批准自己的输出**（Verification 永远是外部的）
- **状态存在模型之外**（进度文件、issue、检查点、追踪日志在上下文重置后仍然存活）
- **预算是硬限制**（重试次数、运行时间、并发都有上限）

---

## 7 个成熟度等级

项目提供了一个成熟度模型，帮助判断「当前用哪一级」：

| 等级 | 名称 | 特征 |
|---|---|---|
| 00 | 手动提示 | 人类持有状态，逐步指令，逐步判断 |
| 01 | 脚本重试 | 有边界的包装器重跑 Agent，最多 N 次，反馈外部失败 |
| 02 | 定时循环 | 任务由定时器或事件自动启动 |
| 03 | 有状态循环 | 运行之间有持久化状态（文件、DB、issue） |
| 04 | 自验证循环 | 外部检查（测试/评估/追踪）决定完成，不由 Agent 自评 |
| 05 | 多 Agent 循环 | 专职 Agent 团队（探索/行动/验证角色分离） |
| 06 | 生产监督循环 | 完整的可观测性、上报路径、成本控制、影响用户的工作 |

> **关键建议**：很多有用的工作流应该在 Level 2 或 Level 3 停下来。先做持久化状态，再增加自主性；先做外部验证，再增加 Agent；先做生产控制，再让循环影响用户。

---

## 8 个 runtime 起点

5 个可适配模板：

| 模板 | 场景 |
|---|---|
| Claude Code `/loop` | 在编程会话中使用，重复有边界的命令，用文件保持进度 |
| 桌面定时任务 | 本地文件需要定时调度、last-run 标记、missed-run 保护 |
| Codex automation | 隔离的后台仓库工作，声明式检查，可审查的收据 |
| GitHub Agentic Workflow | GitHub 事件或 cron 应产出 issue、artifact 或 PR |
| Shell / cron | 已有 Agent CLI 只需要 OS 调度、锁和进度文件 |

3 个可执行示例：
- **测试修复**：运行失败命令，委托证据，只有当同一外部检查通过时才停止
- **阈值监控**：轮询指标，持久化样本，在超出边界时上报，不自动修复
- **队列 Worker**：处理有边界的 JSONL 工作项，外部验证，持久化收据

---

## 545 个资源背后的信号

项目最核心的工作是对资源的审计和标注。网站展示了几个具有代表性的来源：

**alchaincyf/loop-engineering-orange-book**（1,024 stars）：华树用中英双语写的 Loop Engineering 实践指南，将这个领域定位为框架工程之上一层的外部系统——决定 Agent 何时、为何运行。

**arXiv 2607.14890**（2026-07-16）："Proof-or-Stop: Don't Trust the Agent, Trust the Evidence — Loop Engineering for Verifiable Evidence-Gated Lifecycle Control"。定义了证据门控的生命周期控制，报告了在 10 个场景中零假完成、在 18 个篡改类别中零接受。9,240 单元的消融分析识别了哪些门控阻止了错误放大。

**Lenny's Newsletter**：Mozilla 杰出工程师 Brian Grinstead 演示了目标驱动和定时循环，包括每个 PR 有专属子 Agent 的每日 PR Review 循环。

每个资源都有：来源可信度标签（Research / Blog / Pattern）、信号强度标签（high/medium/contextual）、完整的来源记录、贡献/新颖性/影响力评估。

---

## 为什么「设计循环，不只是提示词」

这句话捕捉了一个重要的转变。

2023-2024 年，大多数 AI 工程讨论集中在提示词优化、上下文窗口管理、工具调用设计。这些都是针对**单次运行**的优化。

2025-2026 年，实际部署的 Agent 系统面临的核心挑战变了：
- Agent 怎么在没有人值守时安全地循环？
- 怎么保证它不会批准自己错误的输出？
- 怎么在成本失控之前停下来？
- 失败的上下文怎么在下一次运行时仍然可用？

这些问题不是提示词工程或上下文工程能回答的。它们需要一套**治理循环运行**的工程实践——Loop Engineering。

awesome-loop-engineering 是目前互联网上对这个领域记录最完整的一个集合，545 个资源涵盖研究论文、实践案例、运行模式和可执行代码。对于任何在构建需要持续运行的 Agent 系统的工程师，这是值得收藏的参考。

---

## 一句话总结

Loop Engineering = 让 Agent 工作随时间安全重复的工程实践。awesome-loop-engineering 是它的知识图谱：20 个模式告诉你「该用什么循环」，20 个契约告诉你「怎么写运行规范」，8 个 runtime 起点告诉你「在哪里跑」，545 个审计资源告诉你「这个领域的知识从哪里来」。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Loop Engineering: The Fourth Layer of AI Agent Systems Engineering

**GitHub**: [ChaoYue0307/awesome-loop-engineering](https://github.com/ChaoYue0307/awesome-loop-engineering)  
**Interactive site**: [chaoyue0307.github.io/awesome-loop-engineering](https://chaoyue0307.github.io/awesome-loop-engineering/)  
**Scale**: 545 audited resources · 20 patterns · 20 contracts · 8 runtime starters

### The Problem in One Sentence

Prompt, context, and harness engineering improve one agent run. Loop Engineering governs how agent work repeats, verifies results, persists state, and decides what happens next — over time.

### The Four-Layer Stack

| Layer | Name | Scope |
|---|---|---|
| 01 | Prompt Engineering | One model call |
| 02 | Context Engineering | State/memory visible to one run |
| 03 | Harness Engineering | Tools, permissions, sandbox for one run |
| 04 | **Loop Engineering** | Recurring work over time |

The first three layers are prerequisites for one good run. Loop Engineering is what prevents a recurring system from selecting the wrong work, approving its own output, retrying without a stopping rule, or forgetting a failed attempt.

### The Loop Contract: 11 Decisions That Replace Hidden Defaults

When an agent runs autonomously on a schedule, every unanswered question becomes a hidden default. A Loop Contract turns those defaults into reviewable policy:

**Setup**: Objective, Trigger, Intake, Workspace  
**Run**: Context, Delegation, Verification, State  
**Govern**: Budget, Escalation, Exit  
**Next action**: Repeat, report, escalate, or stop

Verification is always external. The acting agent never approves itself.

### The 6-Step Lifecycle

```
Intake → Delegate → Act → Verify → Persist → Decide
                                        ↓
                       Retry (w/evidence) / Escalate / Exit
```

Key invariants: state lives outside the model; budgets are hard limits.

### 20 Operational Patterns

Organized across four operating modes:

**Build & Maintain**: PR babysitter, CI repair loop, Docs drift collector, Dependency triage, Bug hunting, Release-note loop

**Operate & Observe**: Deploy verifier, Incident response, Data-quality, Cost-control, Model-routing, Performance regression

**Learn & Optimize**: Feedback clusterer, Evaluation regression, Benchmark optimization, Knowledge freshness

**Govern & Protect**: Security review, Enterprise approval, Accessibility regression, Adversarial red-team

Each pattern has a concrete "done-when" definition — not subjective completion, but a verifiable external condition.

### 7 Maturity Levels

00: Manual prompting (human holds state)  
01: Scripted retry (bounded, N attempts max)  
02: Scheduled loop (trigger without human launch)  
03: Stateful loop (progress survives context resets)  
04: Self-verifying (external checks decide done)  
05: Multi-agent (separate act/check roles)  
06: Production-supervised (observability, cost control, user impact)

**Key guidance**: many useful workflows should stop at Level 2 or 3. Add autonomy only when the current level fails a real operating requirement.

### 8 Runtime Starters

Five adaptable templates: Claude Code `/loop`, Desktop scheduled task, Codex automation, GitHub agentic workflow, Shell/cron wrapper.

Three executables: test repair (runs until the same failing command passes), threshold monitor (polls + escalates, no auto-remediation), queue worker (bounded JSONL items with durable receipts).

### Why It Matters in 2026

In 2023–2024, most AI engineering focus was on prompt optimization, context window management, and tool design — all single-run improvements. In 2025–2026, deployed agent systems face a different set of problems: how does an agent safely loop without a person watching? How do you prevent it from approving its own wrong outputs? How do you stop it before it burns the budget?

These questions require a new engineering layer. Loop Engineering is that layer. `awesome-loop-engineering` is the most complete reference collection for it: 545 source-audited resources with contribution/novelty/impact scores, covering research papers (including arXiv 2607.14890), practitioner write-ups, pattern definitions, and runnable code.

© 2026 Author: Mycelium Protocol
