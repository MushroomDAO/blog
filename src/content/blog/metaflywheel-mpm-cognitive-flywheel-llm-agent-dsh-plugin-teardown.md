---
title: "MetaFlywheel：把一篇方法论论文变成 LLM 代理运行时的认知飞轮引擎"
titleEn: "MetaFlywheel: Turning a Methodology Paper into a Resident Cognitive Flywheel Engine for LLM Agents"
description: "NBagent-dev/metaflywheel，MIT，0 stars，JavaScript，2026-08-30，v0.3.0。DeepSeek Harness（DSH）的 Cordis 组合行插件，把元问题建模（MPM）理论的完整运行时嵌入 LLM 代理进程：六阶段问题生命周期（G→F→S→C→D→E）、ε-δ 双重收敛判据、因果回溯、代谢账本、导师规则层（证据门禁/误界定守卫/总账硬门禁/执政权宪法）、测量方法学 v0。理论基准是仓库内 ~1.4 万字的 docs/theory.md，30 道题/19 份沉积/32 轮巡检的实战台账已嵌入文档。配套 mpm_distill.py 工具，把飞轮台账蒸馏为 JSONL 微调训练对。需要 DSH 宿主（非独立 npm 包）；Windows 主要开发平台，其他宿主需自行适配。"
descriptionEn: "NBagent-dev/metaflywheel, MIT, 0 stars, JavaScript, 2026-08-30, v0.3.0. A Cordis bundle plugin for DeepSeek Harness (DSH) that embeds a full Meta-Problem Modeling (MPM) runtime into an LLM agent process: six-phase problem lifecycle (G→F→S→C→D→E), ε-δ dual convergence criteria, causal backtracking, metabolism ledger, mentor rule layer (evidence gates / mis-framing guard / total ledger hard gate / governance constitution), measurement methodology v0. Theoretical basis: ~14,000-word docs/theory.md with 30 problems / 19 deposits / 32 inspection rounds as embedded validation. Companion mpm_distill.py distills flywheel ledgers into JSONL fine-tuning pairs. Requires DSH host (not standalone); Windows primary dev platform, other hosts need adaptation."
pubDate: 2026-10-05
heroImage: "../../assets/images/metaflywheel-mpm-cognitive-flywheel-llm-agent-dsh-plugin-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["LLM代理", "认知工程", "问题建模", "DSH", "开源工具", "AI方法论"]
lang: "zh-CN"
wechatTitle: "MetaFlywheel：给LLM代理装认知飞轮"
wechatDigest: "MIT 0星；六阶段问题生命周期+ε-δ双判据收敛+代谢账本；需DSH宿主；附微调数据蒸馏工具"
---

大多数"AI 代理框架"解决的是调度问题：哪个工具在哪个时机被调用，怎么传参，出错了怎么重试。MetaFlywheel 解决的是不同层次的问题：代理在处理一个问题时，怎么知道它"真的理解了问题"而不是在解一个错误的问题？

这个问题比它听起来更难。传统问题求解理论（Newell & Simon 1972）预设问题空间在求解开始前已被充分界定。但在实际代理工作中——尤其是 LLM 驱动的代理——"问题是什么"本身就是最困难的部分：初始理解偏差、求解中问题重构、伪收敛（看起来解了但其实解了个错误的问题），这些都比调度层面的 bug 更隐蔽。

MetaFlywheel 试图给这个层次造一个引擎。

GitHub: https://github.com/NBagent-dev/metaflywheel | ⭐ 0 | MIT | JavaScript | v0.3.0

---

## 核心架构：六阶段认知飞轮

MPM（元问题建模，Meta-Problem Modeling）把问题视为具有生命周期的动态系统，而不是一个静态的求解输入。六阶段构成一个螺旋上升的飞轮：

| 阶段 | 工具 | 作用 |
|------|------|------|
| G 生成 | `mpm_generate` | 把问题感登记为正式问题（信息熵阶跃触发） |
| F 界定 | `mpm_frame` | 五要素界定：初始/目标/约束/算子/判据 + δ 自评 |
| S 求解 | `mpm_solve` | 登记求解路径与 ε；支持搁置 `parked`、开放题 `openEnded` |
| C 收敛 | `mpm_converge` | ε-δ 双判据收敛判定，含证据门禁与开放题守卫 |
| D 沉积 | `mpm_deposit` | 不可逆落盘——认知遗体，可索引，带熵屏障 |
| E 激发 | `mpm_evoke` | 由沉积物激发新问题（四类型：漂移/突变/视角/外部注入） |

另有轻量通道 `mpm_micro`（G→F→S→C 一息走完）、`mpm_setroot`（修正沉积根目录）和 `mpm_grant`（执政权 grant/revoke/status）。

"螺旋上升"的意思是：D 沉积和 E 激发并不是问题的终点，而是驱动下一个问题产生的引擎。这个循环在理论上是无止境的，类似认知的代际累积。

---

## 两个核心判据：ε 和 δ 的区别

这是 MetaFlywheel 最值得理解的理论贡献。

传统做法只有一个成功标准：解到了没有（ε）。MPM 把这拆成两个：

- **δ**（问题定义精度）：你有没有理解对问题本身？主观表征与客观问题情境的偏差。
- **ε**（解的逼近精度）：在你理解的问题上，解达到目标了没有？

只有 ε 而没有 δ 的系统会产生**误界定收敛**：解达标了，但解的是一个错误问题。MPM 识别四种收敛类型，其中误界定收敛是最危险的，因为它看起来像成功。

三种明确不收敛情形也被实现为显式状态：
- 原则上不可判定（对应哥德尔不完备性）
- 计算不可行（PPAD 完全性）
- 价值不可通约（多主体目标根本冲突）

这三种情形在运行时里有对应的 `openEnded` 标记与解除算子——而不是被默认忽略或无限重试。

---

## 代谢账本：把计算代价变成约束

每次工具调用自动累积代谢代价 C，并归属到当前在轮问题。**无在轮题的账外调用被工具级门禁拦截**——这是"总账原则硬化"，不允许代理在没有问题上下文时随意调用工具。

这个设计的动机来自理论的公理二（熵减公理）：局部熵减必须以资源消耗为代价，这个代价不能被隐藏。代谢账本是把这个理论约束强制执行的工程实现。

配套工具 `tools/mpm_distill.py` 可以把飞轮台账（`.mpm/flywheel.json`）蒸馏为 JSONL 微调训练对，理论上可以通过行为克隆把"方法论遵行"的程序性记忆从外部结构向模型权重内化——这是整个系统里技术密度最高的部分，也是边界最不清晰的部分（脚本自身的 docstring 也承认了行为克隆的边界问题）。

---

## 导师规则层：方法论遵行不靠自律

这是 v2 新增的核心内容，也是最有实践价值的部分。

作者的出发点是：**如果规范性约束只写在系统提示词里，LLM 会学着绕过它**。不能靠"提示词祈祷"让代理遵守方法论。

规则层的实现方式是：让违规在结构上无收益。具体门禁包括：

| 规则 | 触发条件 | 执行机构 |
|------|----------|----------|
| 证据门禁 | 无求解证据时不得宣称收敛 | 收敛工具拒绝执行 |
| 误界定守卫 | 大幅回溯 + 历史自报低 δ → 可信度折减 | 下次自评权重降低 |
| 总账硬门禁 | 无在轮题时调用工具 | 工具层直接拒绝 |
| 执政权宪法 | 自主审议的温热/节流/署名约束 | 审议事件门控 |
| 停滞择题 | 防审议轰炸 | 时间窗口限制 |

这些门禁的设计思路值得借鉴，但它们的有效性依赖 DSH 宿主的事件面——如果宿主不提供对应的钩子，门禁就降级为软约束。

---

## 使用 MetaFlywheel

**前提**：需要 DeepSeek Harness（DSH）宿主运行，不是独立 npm 包。

**一键安装**（macOS/Linux）：
```bash
curl -fsSL https://raw.githubusercontent.com/NBagent-dev/metaflywheel/main/install/install.sh | bash
```

**Windows PowerShell**：
```powershell
irm https://raw.githubusercontent.com/NBagent-dev/metaflywheel/main/install/install.ps1 -OutFile install-mfw.ps1; .\install-mfw.ps1
```

安装完成后引擎向系统提示注入自我快照（在轮问题/陈旧警告/指令流/代谢摘要），代理获得九个生命周期工具。

**测试**（不需要 DSH 宿主）：
```bash
node --test test/smoke.test.mjs
```

冒烟测试用最小 mock 宿主驱动完整微生命周期，5/5 通过。

---

## 局限

**需要 DSH 宿主**：MetaFlywheel 是 Cordis 插件，不能脱离 DSH 宿主运行。其他 LLM 代理框架（Langchain、AutoGen 等）需要自行适配契约层，工作量不低。

**Windows 主开发平台**：README 明确说"开发与实测在 Windows + DSH 宿主；其他宿主接入需自行适配契约层"。macOS/Linux 的一键安装脚本有，但边角 case 未经充分测试。

**会话连续性已知问题**：GUI 页面重载路径上曾发生状态与会话解耦的事故——状态落盘可恢复，但进行中的会话上下文不迁移。

**0 颗星**：2026-08-30 创建，文档质量和理论深度明显高于同量级项目，但用户基础接近于零。理论上的严密性不等于工程上的成熟度。

**常数全为 v0 占位**：时间窗口/节流/温热/陈旧/停滞/衰减六项常数均为经验值，README 明确标注"测量史满窗后应导出替换"——这意味着这些参数在实际部署中需要根据自己的 DSH 使用数据重新校准。

---

> MIT 开源。0 颗星的极早期项目，API 可能随版本变化。依赖 DSH 宿主，非独立可用。开源仅供学习参考。

---

<!--EN-->

## MetaFlywheel: A Cognitive Flywheel Engine for LLM Agents

Most "AI agent frameworks" solve scheduling problems: which tool gets called when, how to pass arguments, what to retry on failure. MetaFlywheel solves a different layer: how does an agent know it has correctly understood the problem it's solving, rather than solving the wrong problem?

This is harder than it sounds. Classical problem-solving theory (Newell & Simon 1972) presupposes the problem space is fully defined before solving begins. In actual LLM agent work, "what is the problem" is the hardest part: initial understanding bias, problem reformulation mid-solve, pseudo-convergence (looks solved but solved the wrong thing) — these are more invisible than scheduling bugs.

MetaFlywheel tries to build an engine for this layer.

GitHub: https://github.com/NBagent-dev/metaflywheel | ⭐ 0 | MIT | JavaScript | v0.3.0

---

### Core Architecture: Six-Phase Cognitive Flywheel

MPM (Meta-Problem Modeling) treats problems as dynamic systems with a lifecycle, not static solver inputs. Six phases form a spiral-ascending flywheel:

**G Generate → F Frame → S Solve → C Converge → D Deposit → E Evoke**

The key insight: D (Deposit) and E (Evoke) are not the end of a problem — they drive the next problem's generation. The loop is theoretically endless, modeling cognitive accumulation across generations.

---

### The ε-δ Split: Two Convergence Criteria

This is the core theoretical contribution worth understanding.

Traditional approaches have one success criterion: did you solve it (ε)? MPM splits this into two:

- **δ** (problem definition accuracy): Did you correctly understand the problem itself? Deviation between subjective representation and objective situation.
- **ε** (solution approximation accuracy): Given your understanding of the problem, did the solution reach the goal?

Systems with only ε produce **mis-framing convergence**: the solution meets its criteria, but it solved the wrong problem. MPM identifies four convergence types; mis-framing convergence is the most dangerous because it looks like success.

Three explicit non-convergence states are also implemented: undecidable in principle (Gödel), computationally infeasible (PPAD-complete), and value incommensurable (multi-agent goal conflict). These are explicit states with release operators — not silently ignored or infinite-retried.

---

### Metabolism Ledger: Making Computational Cost a Constraint

Every tool call auto-accumulates metabolic cost C, attributed to the current active problem. **Tool calls without an active problem are hard-blocked at the tool layer.** This is "total ledger hardening" — agents cannot call tools without a problem context.

Companion tool `mpm_distill.py` distills flywheel ledgers into JSONL fine-tuning pairs, theoretically enabling behavioral cloning of "methodology adherence" from external structure into model weights. Highest technical density in the system, least validated in practice.

---

### Mentor Rule Layer: Methodology Enforcement Without Self-Discipline

v2's core addition: if normative constraints are only in the system prompt, LLMs learn to route around them. "Prompt prayer" doesn't work. The rule layer makes violations structurally unrewarding:

- Evidence gate: can't claim convergence without solve evidence
- Mis-framing guard: heavy backtracking + historically low δ → credibility reduction
- Total ledger hard gate: tool calls blocked without active problem
- Governance constitution: autonomous deliberation temperature/throttling/attribution constraints

These gates require DSH host event hooks to be hard — without them, they degrade to soft suggestions.

---

### Limitations

Requires DSH host — not a standalone npm package. Windows primary dev platform; macOS/Linux installation script exists but edge cases untested. Known session continuity issue on GUI page reload. 0 stars since August 2026 — theoretical rigor does not imply engineering maturity. All six time constants (inspection/throttle/temperature/staleness/stagnation/decay) are v0 placeholder empirical values requiring recalibration from actual deployment data.

---

> MIT. 0-star early-stage project, requires DSH host. API subject to change. For technical reference only.
