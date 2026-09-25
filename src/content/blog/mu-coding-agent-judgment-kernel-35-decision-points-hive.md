---
title: "mu（μ）：编程 Agent 的判断核，35 个决策点交给小模型，大模型只管写代码"
titleEn: "mu (μ): A Coding Agent's Judgment Kernel — 35 Decision Points for a Small Model, Big Model Just Codes"
description: "Qybaihe/mu，MIT，TypeScript，116 stars（3天）。编程 Agent 每轮有 35 个决策点，和编码无关：这段工具输出要不要进 context？这条命令危不危险？工作跑偏了吗？任务完成了吗？mu 把这些交给一个小、快的判断模型（Jev 或 322M 本地 Laya），大模型只处理实际编码。工具输出逐块判断进入 context，51% 的测试日志重复行无损折叠。Hive 多 Agent 系统里，judge 是发现共享的闸门。构建于 earendil-works/pi。"
descriptionEn: "Qybaihe/mu, MIT, TypeScript, 116 stars (3 days). A coding agent turn has 35 decision points unrelated to coding: does this tool output chunk enter context? Is this command dangerous? Has the work drifted? Is the task done? mu delegates these to a small, fast judge (Jev or 322M local Laya) so the big model keeps its attention for actual coding. Tool output enters context chunk by chunk; 51% of test log bytes are exact repeats folded losslessly. In the hive multi-agent system, the judge is the gate for sharing findings. Built on earendil-works/pi."
pubDate: 2026-09-25
wechatTitle: "mu编程Agent：判断核管35个决策点"
wechatDigest: "小模型管35决策点，大模型专心写代码；51%测试日志重复折叠；Hive多Agent判断门控"
heroImage: "../../assets/images/mu-coding-agent-judgment-kernel-35-decision-points-hive-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "coding-agent", "jev", "multi-agent", "context-management", "local-ai", "typescript"]
lang: zh-CN
---

`Qybaihe/mu`，MIT，TypeScript，116 stars，创建于 2026-09-22。一个给编程 Agent 加「判断核」的框架：每轮 35 个和编码无关的决策，交给一个小、快的模型（Jev 或 322M 本地 Laya），大模型的注意力留给真正的编码工作。

**GitHub**：github.com/Qybaihe/mu | 构建于 github.com/earendil-works/pi

---

## 核心问题：一轮里大量决策不是关于代码的

一个编程 Agent 跑完一轮，真正写代码的时间只占其中一部分。另一大块是这些：

- 这段工具输出 100 行，哪些现在重要，哪些可以归档？
- context 快满了，哪些旧结果可以变成一行墓碑？
- 这个 shell 命令看起来危险，是用户明确要求的吗？
- 模型说完成了，但有什么东西真的验证了吗？
- 跑了好几步，工作还在朝目标走吗？

用大模型处理这些，每次都烧 token、增加延迟。用固定规则，又经常错。mu 的答案是给这些决策一个专用的「判断核（judgment kernel）」。

---

## 判断核：35 个决策点

mu 在每轮里有 35 个命名的决策点，分成五类：

### 输入

| 决策点 | 问题 | 效果 |
|--------|------|------|
| `input.preflight` | 这条消息是什么类型，需要多深的思考？ | 给大模型一个单行提示，可选设置本轮思考深度 |
| `task.frame` | 新任务、硬约束、修正、子目标，还是没变化？ | 只有变化时才改写任务框架 |
| `input.interjection` | Agent 工作中来了一条消息：现在打断，还是等这步结束？ | 立即切轮，或让消息等待 |

### Context 管理

这是 mu 在工程上最有价值的部分：

**`tool.admission`**：工具输出逐块（chunk by chunk）进入 context，每块单独问「这现在重要吗？」不重要的归档，存指针。效果：context 不会因为一次大的工具输出就被撑满。

**`tool.admission.test-log`**：测试日志专项处理。实测数据：在一次失败测试的日志里，**51% 的字节是精确重复**，会被无损折叠。你看到的 context 里是一行「同样的错误 × 47 次」，不是 47 次完整错误输出。

**`context.forget`**：context 超过阈值时，问哪些工具结果已经过时。过时的变成一行墓碑，不写摘要，信息不丢失（有指针可以拿回来），但 token 大幅缩减。

**`cache.warming`**：judge 预测用户会不会在 prompt cache 过期前回来。会的话就主动刷新 cache；不会的话就让它过期。这让 cache 命中率保持高位。

**`memory.*`**：5 个记忆决策点，处理「这条消息是否在纠正 Agent」「这个经验值不值得保存」「这条记忆和已有记忆是否重复/矛盾」等问题。

### 工具与安全

| 决策点 | 问题 | 效果 |
|--------|------|------|
| `tool.risk` | 规则标记的危险命令：用户明确要求了吗？ | 不确定就询问 |
| `tool.approval` | 在「Jev 审批」模式下：任务明确需要这个命令/这次改动/这个 sub-agent？ | 只有确定的才跑，其余询问 |
| `tool.constraint` | 调用会改变东西之前：这个操作跨越了你声明的约束吗？ | 调用被停止 |
| `browser.step` | 内置浏览器的下一步操作：用什么操作，针对哪个元素？ | Agent 驱动浏览器单步走 |
| `review.triage` | `/review` 的每条发现：影响行为吗？和这次改动有关吗？ | 发现被分级 P0-P3 |

### 轮控

| 决策点 | 问题 | 效果 |
|--------|------|------|
| `turn.drift` | 每隔几步：工作还在朝目标走吗？ | 规则抓循环，judge 抓跑偏 |
| `turn.rewind` | 同样的失败反复出现：这条路是死胡同吗？ | 回退到检查点 |
| `turn.completion` | 模型说完成了：有什么东西实际验证了吗？ | 没有的话给一次 nudge |

### 团队协作（Hive）

| 决策点 | 问题 | 效果 |
|--------|------|------|
| `hive.publish` | 这条发现/死胡同/决策值得共享吗？ | 上共享板，或只留给自己 |
| `hive.deliver` | 新板上的内容对这只 bee 的任务有关系吗？ | 有关才送达 |
| `hive.relate` | 新发现和旧发现是什么关系？ | supersedes（取代）/ contradicts（矛盾）/ supports（支持） |

---

## 三种 Judge

**Jev（托管）**：有概率的有界问题（yes/no、choice、score）。实测延迟：0.3 秒（HTTP/2 热请求），16 块工具输出在一次请求里判断完是 0.44 秒，状态只计费一次。所有裁决、概率和时间都进 ledger（`mu ledger` 或桌面应用的 judgments 标签页）。

**Laya（本地）**：322M 参数，跑在本地，永不联网。适合简单谓词判断，元判断（meta-judgments）较弱。建议先跑 shadow 模式和 Jev 并排对比，读 ledger 确认准确率再把具体决策点交给它。

**任意 LLM**：`llm:<provider>/<model>`，用 OpenRouter 或兼容 API。

每个决策点可以设置自己的 judge，也可以配级联：`laya,jev`（Laya 先判，不确定时升级到 Jev）。

---

## Hive：judge 是多 Agent 通信的闸门

多 Agent 系统里最核心的问题是：一个 Agent 知道的事，要不要告诉另一个？

mu 的 Hive 是 2-6 只 bee，每只有自己的专注域。Bee 只读代码、跑命令、浏览——不编辑，编辑权归主模型。

通信流程：
1. Bee 完成某个表达后，`hive.publish` 问一次：**这条发现/结论/阻塞值得上共享板吗？**
2. 每条新板上的内容，`hive.deliver` 对每只其他 bee 各问一次：**这和它的专注域有关吗？**
3. 有关才送达，标记为「发现，不是指令」

板是只增不减的（append-only）。当一条新结论和旧结论有关时，`hive.relate` 判断关系：
- **supersedes**：取代旧结论，旧结论变为修正，送给所有持有旧结论的 bee
- **contradicts**：两条都保留，标为争议；60 秒内没有解决，自动派一只 bee 去核实
- **supports**：加强旧结论

**实测数据（一次真实 Hive 跑）：**
- 3 只 bee，9 分钟
- 117 条候选判断
- 27 条上了共享板
- 16 条被送达给需要的 bee

---

## 平语板（Plain-Language Board）

mu 不让工作模型自己叙述进展——前沿模型越来越擅长实际工作，输出越来越密，越来越像给另一台机器看的，而不是给人看的。

`/board` 开启后：每个 Agent 动作结束的瞬间，变成一行白话出现在板上（文件改了、检查通过/失败、命令跑了、20 次读文件折成「读了 20 个文件」）。`board.read` 判断 Agent 说的话是否是「新消息」，是的话由一个专门选来「说人话」的模型重述，保持板上的状态是最新的：现在在做什么、清单完成多少、什么在等你。

板上两个数字：context 使用率和 cache 命中率——判断核在 context 和 cache 管理上的直接结果。

---

## 安装与使用

**CLI 方式：**

```bash
npm install -g mu-agent
# 在 .env 里配置 judge 和工作模型的 API key
mu "帮我重构 src/utils/parser.ts，消除重复代码"
```

**桌面应用（推荐入门）：**

从 GitHub Releases 下载 mu desktop——内置 runtime，无需安装 Node。打开后连接模型（ChatGPT/Claude/Grok/Google 订阅，或 API key），直接开始。

支持的工作面板：board（平语板）· judgments（裁决 ledger 实时）· hive（多 Agent 状态图）· lessons（记忆库）· files · preview · source · browser（内置浏览器，Agent 单步驱动）

Claude Code 和 Codex CLI 的对话可以导入继续。

**Permission 模式：**

`⌘K` 开命令面板。Permission 模式决定哪些操作需要确认，哪些 judge 自动放行。Goal 模式下用 `/goal` 设定条件，`goal.met` 判断何时完成。

---

## 怎么看这个项目

mu 的思路和 jev-ultrafast 的投机扇出本质一样：**把和内容无关的快决策从大模型里剥离出来**。jev-ultrafast 做的是浏览器操作决策，mu 做的是 Agent 轮控的 35 个元决策。

技术上最有意思的是 `tool.admission` 这个设计——让工具输出逐块进入 context 而不是一口气全进，让 judge 当过滤器，理论上可以处理任意长的工具输出，而 context 增长是受控的。结合 51% 测试日志重复折叠，这对实际写代码时反复跑测试的场景是真实的工程价值。

早期项目，README 说「nothing has been released yet」，名字/设置/格式还可能变。但架构描述足够详细，代码在仓库里，值得关注。

> 开源仅供学习研究参考。早期项目，接口可能变化。

---

<!--EN-->

## mu (μ): A Judgment Kernel for Coding Agents

`Qybaihe/mu` — MIT, TypeScript, 116 stars, created 2026-09-22. A coding agent that delegates 35 per-turn decisions unrelated to coding to a small, fast judge (Jev or 322M local Laya). The big model keeps its attention for actual coding.

**GitHub**: github.com/Qybaihe/mu | Built on: github.com/earendil-works/pi

---

### The Problem

A coding agent turn contains hundreds of decisions that aren't about code: which parts of a 100-line tool output matter now? Is this shell command dangerous? Has the work drifted from the goal? Did anything actually verify that the task is done? Delegating these to the big model costs tokens and latency. Fixed rules get them wrong too often. mu gives them to a **judgment kernel**.

---

### 35 Decision Points

Organized into five categories: Input (3), Context (8), Tools & Safety (7), Turn (7), Teamwork (5).

**Highest-value context management decisions:**

`tool.admission` — tool output enters context chunk by chunk. Each chunk is asked once: "does this matter now?" Irrelevant chunks are archived behind a pointer, not discarded. The context never gets flooded by a single large tool result.

`tool.admission.test-log` — failing test logs get special handling. Measured: **51% of bytes in a failing test log were exact repeats** — folded losslessly into a single count.

`context.forget` — above a context threshold, which tool results are stale? Each becomes a one-line tombstone (not a summary); the original is retrievable via pointer.

`cache.warming` — the judge predicts whether the user will return before the prompt cache expires, then refreshes or lets it expire accordingly. Keeps cache hit rate high.

`memory.*` — five memory decision points: capture lessons from corrections, score proposed lessons for reuse value, merge or drop duplicates and contradictions, retire lessons that are recalled but never followed.

**Safety decisions:**

`tool.risk`, `tool.constraint`, `tool.approval` cover dangerous commands, out-of-scope edits, and sub-agent delegation in the "Jev approves" permission mode.

**Turn control:**

`turn.drift` (has the work diverged from the goal?), `turn.rewind` (is this approach a dead end?), `turn.completion` (did anything verify the claimed completion?).

---

### Three Judges

**Jev (hosted)**: bounded questions with probabilities. Measured: 0.3s per warm question; 16 output chunks judged in one request in 0.44s (state billed once). All verdicts, probabilities, and timings go to a ledger.

**Laya (local)**: 322M parameters, never touches the network. Reliable on simple predicates, weaker on meta-judgments. Run in shadow mode alongside Jev first — read the ledger before assigning a decision point to it.

**Any LLM**: `llm:<provider>/<model>` as a tier; cascade notation supported: `laya,jev`.

Each decision point names its own judge and can be set to `active`, `shadow` (judged and logged, no effect — for A/B comparison), or `off`.

---

### The Hive (Multi-Agent)

2-6 bees, each with its own focus. Bees read, run commands, browse — they never edit; the main model makes changes. Three hive decision points:

`hive.publish` — after each bee utterance: is there a finding worth the shared board? Only what's worth it goes up.

`hive.deliver` — for each new board entry, per other bee: does this touch its focus? Delivered only if relevant.

`hive.relate` — new vs. existing finding: *supersedes* (older becomes a correction, delivered to every bee holding it), *contradicts* (both kept as a dispute; unresolved in 60s → a verifying bee is sent), or *supports*.

**Real run**: 3 bees, 9 minutes, 117 candidates judged, 27 on the board, 16 delivered to the bee that needed them.

---

### Setup

```bash
npm install -g mu-agent
# Configure judge + model API keys in .env
mu "Refactor src/utils/parser.ts to eliminate duplication"
```

Or download mu desktop from GitHub Releases: native app, no Node install needed. Supports ChatGPT, Claude, Grok, Google (Gemini/Antigravity) subscriptions, or API key for any pi-supported provider. Claude Code and Codex CLI conversations can be imported and continued.

Panels: board · judgments (live ledger) · hive (delivery map) · lessons · files · preview · source · browser (agent-driven, step by step).

---

### Assessment

mu's idea parallels jev-ultrafast's speculative fan-out: **strip fast meta-decisions out of the big model**. jev-ultrafast handles browser operation decisions; mu handles 35 per-turn control decisions. The architecturally interesting piece is `tool.admission` — chunk-by-chunk context admission with a judge as filter means arbitrarily long tool outputs don't blow the context in one shot. Combined with the 51% test-log deduplication, this addresses a real pain point in coding agents that run tests repeatedly. Early-stage (README: "nothing has been released yet"), but the architecture is well-specified and the code is in the repository.

> For learning and research reference only. Early development — names, settings, and formats may still change.
