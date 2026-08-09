---
title: "ccteam：用 8 个 MCP 工具把 Claude、Codex、Grok、Kimi 编成一支真正的编程团队"
titleEn: "ccteam: 8 MCP Tools to Turn Claude, Codex, Grok, and Kimi into a Real Coding Team"
description: "ccteam 是一个 Rust 写的守护进程，让你现有的编程 Agent 跨厂商协作——Claude 规划，Codex 苦干，Grok 快速回答，Kimi 批量便宜处理，Telegram/飞书/浏览器统一指挥，本地优先无云依赖。"
descriptionEn: "ccteam is a Rust daemon that lets your existing coding agents collaborate across vendors — Claude plans, Codex grinds, Grok answers fast, Kimi handles batch work cheaply — all controlled from Telegram, Feishu, or a browser. Local-first, no cloud dependency."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["Multi-Agent", "Claude Code", "Codex", "Grok", "Kimi", "MCP", "Agent编排", "开源工具", "Rust", "团队协作"]
heroImage: "../../assets/images/ccteam-multi-agent-cross-vendor-orchestration-banner.jpg"
---

> **GitHub**：[firstintent/ccteam](https://github.com/firstintent/ccteam)  
> **语言**：Rust · **许可**：MIT · **Stars**：79  
> **安装**：`curl -sSL https://raw.githubusercontent.com/firstintent/ccteam/main/install.sh | sh`

---

## 问题：你有五个优秀的编程 Agent，但它们互不认识

过去两年，出现了五个真正好用的编程 CLI：Claude Code、Codex、Grok、OpenCode、Kimi。每一个都很出色，但都假设自己是唯一的终端——一个上下文，没有同事。

结果是你在 alt-tab：把上下文粘贴给 Codex，回来看 Claude 有没有回复，再把结果转发给 Grok 做 review。**你成了消息总线。**

ccteam 的修法不是再造一个框架把所有人包一遍——各厂商的工具本身已经很好，还在每周进化。它只做缺失的**结缔组织**：身份、路由、派发保证、成本账本、跨机器执行。让这些 Agent 彼此认识，知道怎么找彼此，知道任务完成没有。

---

## 架构：一个守护进程，8 个 MCP 工具

安装后，ccteam 在本机启动一个 Rust 守护进程，在所有你已有的 CLI 里注册同一套 MCP 工具：

```bash
ccteam config   # 向 Claude/Codex/Grok/Kimi/OpenCode 注册 MCP
ccteam start    # 启动守护进程
```

**8 个工具，任何已连接的 session 都能用：**

| 工具 | 用途 |
|---|---|
| `session_spawn` | 启动新 session（指定 vendor/model/task） |
| `session_dispatch` | 向现有 session 派发追加任务 |
| `session_collect` | 收集 session 结果 |
| `session_list` | 列出所有 session 及各自费用 |
| `session_stop` | 停止指定 session |
| `status` | 查看当前 Host 的 vendor 能力 + routing 笔记 |
| `chat_send_file` | 向 session 发送文件 |
| `screenshot` | 截图 |

**你平时不需要背这些工具名**——直接用自然语言说，session 自己调用：

```
"把 RFC-12 的实现交给 codex 处理，后台跑，跑完报告 diff 和测试结果"
→ session_spawn{vendor:"codex", task:"...", title:"impl"} 然后等 notification

"问 grok 这个 stack trace 是什么问题，等它回答"
→ session_spawn{vendor:"grok", wait_seconds:120, ...} 并内联等待
```

---

## Session 模型

每个 session 有持久 ID（`s1`、`s2`、`s47`...），daemon 重启后存活，可以随时恢复或追加任务。状态全在 `.ccteam/` 里，纯文件，可以 `git status` 看到。

```
你的 repo/
  .ccteam/          ← session 状态、cost 账本、routing
  .claude/
    agents/         ← 你选择安装的 persona
    settings.local.json  ← ccteam 只写这里，从不动 settings.json
```

**Project 绑定 Host。** 每个 project 注册到一台机器（本机或卫星机），session 自动在对应机器上跑——spawn 一个 GPU-box 的 project，测试就在 GPU box 上跑，transcript 和 cost 留在你的主控台。

---

## 三种操控方式

**1. Telegram / 飞书 IM**

Settings → IM 粘一个 bot token，聊天框就是控制台。完成通知、HITL `[approve] [deny]` 按钮、生成的文件，都在同一个 thread 里。半夜派活，关电脑睡觉，早上看结果。

```
/cd my-project          # 切换项目
/new codex              # 启动一个 codex session
@s2 run the test suite  # 直接对话指定 session
/status                 # 看团队状态和费用
```

**2. 浏览器 UI（LAN）**

`http://<LAN-IP>:7331/?token=…` 是一个聊天壳，不是 dashboard。每个 session 有自己的 Chat tab，有 delegation tree，有 cost pill，有 marketplace。

**3. 在 Claude session 内，用自然语言编排团队**

这是最核心的用法。任何已连接 ccteam 的 Claude session，不需要额外安装，直接说：

```
Spawn a codex session, have it implement RFC-12 and run the tests;
report back when green.

Plan this refactor, then delegate: codex implements, grok profiles
the hot path in parallel, kimi sweeps the rename across the repo.
Collect everything into one summary.

Spawn a claude reviewer on s2's diff — I'm not merging until it signs off.
```

---

## 三个核心编排模式

### Plan → Build → Gate（规划→实现→门控）

```
[Claude s1 lead]
  → session_spawn codex s2: "implement RFC-12, run tests, report diff summary"
  ← completion notification: files changed, tests green
  → git diff (自己看代码，不是让 AI 念给你听)
  → session_spawn claude s3: "review this diff — MERGE or BLOCK with reasons"
  ← verdict: MERGE, no blockers
  → stop s3; keep s2 for follow-ups
```

Lead 总共说了两句话，两个不同厂商的 session 做了实现和 review，每一跳都在账本上。

### Grind + Probe（苦活 + 快问）

Codex 跑长任务（实现、迁移、机械重构），Grok 并行给你快速的第二意见。Codex 还在跑的时候，你已经从 Grok 那里知道瓶颈在哪了。

```
session_spawn{vendor:"codex", task:"migrate auth module to OAuth2", title:"grind"}
session_spawn{vendor:"grok", task:"profile this hot path", wait_seconds:120, title:"probe"}
```

### Bulk on Budget（批量省钱）

重复性、机械性的80%工作 fan-out 给 Kimi（成本低），判断类、规划类保留给 Claude。

```
Kimi × N: sweep all 47 modules for deprecated API calls, fix each
Claude: review the collected diff and decide which 3 are too risky to merge
```

---

## Routing：谁做什么，靠事实不靠猜

`status` 工具返回这台机器上 vendor 的真实状态（已安装/已认证/在预算内），不是假设：

```
# 一次 status 调用看到
Vendors on host "my-mac":
  claude-code  ready (claude-opus-4-8)
  codex        ready (sol-max)
  grok         not_ready — grok CLI not found
  kimi         ready (k2)

Daily budget: claude $12/$30, codex $8/$30, kimi $2.40/$20
```

Routing 意见存在纯文本文件，你写，AI 读：

```markdown
# ~/.ccteam/routing.md

| Task type | Vendor / model | Why |
|---|---|---|
| Long refactors, migrations | codex / sol-max / high | grinds without wobbling |
| Quick second opinion | grok / default / low | minute-scale answers |
| Final review before merge | claude / opus / high | catches what builder rubber-stamps |
| Repetitive mechanical work | kimi / k2 / low | cheap, sufficient |
```

Project 级别的 `.ccteam/routing.md` 完全覆盖全局配置（不合并）。`status` 把选中的文件原文带给任何 vendor 的任何 session——规划者看到的文字完全一致。

---

## 多机：把 NAT 后面的笔记本变成 GPU Box

```bash
# 主控机
ccteam satellite create --name gpu-box
# → 生成 join token

# 卫星机（哪怕在 NAT 后面）
ccteam satellite join --token <token>
# → 主动 dial out 到 daemon
```

Project 绑定到 `gpu-box`，spawn session 时测试在那台机器跑。切换机器就是切换 project，账本和团队视图还在主控台。

当前限制：卫星机只支持 Claude sessions；Codex/Grok/Kimi 在 daemon 本机跑。

---

## 安全设计

**不注入 prompt**：Persona 通过 vendor 原生机制加载（`.claude/agents/`），task 文字原文转发，没有包装层偷偷插内容。

**不刮屏幕**：状态来自 transcript 和结构化事件，不解析终端输出。

**本地优先**：`~/.ccteam` + 你的 repo，没有云端组件，不上传你的代码。

**预算守护，不强杀**：每日 per-vendor 上限到了，拒绝新的 spawn 并说明原因，不会 kill 正在跑的 session。

**防失控 fan-out**：Guardrails 拒绝超出限制的递归派活（有具体原因），不是静默截断。

**Idempotency key**：`session_spawn`/`session_dispatch` 支持幂等键，重试不会重复创建 session——在不稳定链路上很重要。

---

## HITL（人在回路）审批

```
session_spawn{vendor:"codex", approval_mode:true, task:"..."}
```

Codex 在执行过程中遇到需要权限的工具调用，请求通过 IM 发来 `[approve] [deny]` 按钮。Deny 走 vendor 原生 gate，阻断那次工具调用但不 kill session。

---

## Marketplace

```bash
# 从 ccteam-hub 安装 persona（sha256 验证，原文 copy）
ccteam marketplace install team-brain
```

`team-brain` persona 装好后，一个 session 变成"首席 of staff"——有固定的路由习惯和 review 门控，你说一句话它自己拆分派活。

Claude Code plugin（vendor-native）委托给 Claude Code 自己安装，ccteam 只翻两个 settings key。

---

## 安装与验证

```bash
# 一行安装（Rust binary → ~/.local/bin，不需要 sudo）
curl -sSL https://raw.githubusercontent.com/firstintent/ccteam/main/install.sh | sh

# 向各厂商 CLI 注册 MCP
ccteam config

# 验证
ccteam doctor --verify-mcp   # 8 tools, 0 stubs → 退出码 0
claude mcp list               # server "ccteam" → ✔ Connected

# 启动
ccteam start
# → 打印 http://<lan-ip>:7331/?token=...
```

从源码编译（需 Rust + Node）：
```bash
git clone https://github.com/firstintent/ccteam && cd ccteam && make install
```

---

## 与 Heinu1 / PR-Daemon 对比

这几个工具在目标上有些重叠，但定位不同：

| | **ccteam** | **Heinu1** | **PR-Daemon** |
|---|---|---|---|
| 指挥渠道 | Telegram/飞书/浏览器 | 微信 | GitHub PR |
| 编排层 | Agent 之间互相派活 | 人→Claude（单 session） | 多轮 PK review |
| 跨厂商 | ✅ Claude/Codex/Grok/Kimi | ✗（仅 Claude） | ✅（DeepSeek/Opus/Codex） |
| 跨机器 | ✅ 卫星机 | ✗ | ✗ |
| 本地优先 | ✅ | ✅ | ✅ |
| 典型场景 | 一个 Lead Claude 指挥专家团队干活 | 手机远程控制 Claude | PR 自动 review 流水线 |

三者可以共存：ccteam 管 Agent 之间的协作，Heinu1 管人机交互，PR-Daemon 管 review 流水线。

---

## 核心判断

ccteam 解决了一个真实痛点：**你有多个好 Agent 但在手动扮演路由器**。它的定位清晰——不替代各厂商工具，只做它们缺的协调层。

Rust 写的守护进程本身是对的选择：常驻后台，低资源，跨重启稳定。8 个 MCP 工具的接口设计足够小，以至于任何已有的 Claude session 接入后就能立刻用，没有学习曲线。

最有价值的三个设计决策：
1. **Routing 是你的纯文字，不是框架的魔法**——你能版本控制你的团队策略。
2. **Delivery guarantees 显式化**——at-least-once notification、idempotency key、child 的 turn 先落盘再通知 parent。
3. **预算可见，不强杀**——delegation 产生费用，fee 实时在账本，日上限到了拒绝新任务但不中断当前。

79 Stars，但今天就值得关注。等它 Satellite execution 覆盖所有 vendor，多机器 Agent 团队就真正成熟了。

---

## 参考资源

- **GitHub**：[firstintent/ccteam](https://github.com/firstintent/ccteam)
- **编排指南**：[docs/orchestration.md](https://github.com/firstintent/ccteam/blob/main/docs/orchestration.md) · [中文版](https://github.com/firstintent/ccteam/blob/main/docs/orchestration-cn.md)
- **用法手册**：[docs/usage.md](https://github.com/firstintent/ccteam/blob/main/docs/usage.md) · [中文版](https://github.com/firstintent/ccteam/blob/main/docs/usage-cn.md)
- **Marketplace**：[firstintent/ccteam-hub](https://github.com/firstintent/ccteam-hub)

© 2026 Author: Mycelium Protocol

<!--EN-->

> **GitHub**: [firstintent/ccteam](https://github.com/firstintent/ccteam)  
> **Language**: Rust · **License**: MIT · **Stars**: 79  
> **Install**: `curl -sSL https://raw.githubusercontent.com/firstintent/ccteam/main/install.sh | sh`

---

## 1. The Problem: You Have Five Great Coding Agents, and They Don't Know Each Other

Over the past two years, five genuinely useful coding CLIs have emerged: Claude Code, Codex, Grok, OpenCode, and Kimi. Each is excellent, but each assumes it is the only terminal — one context, no colleagues.

The result is you alt-tabbing: pasting context into Codex, checking whether Claude has replied, then forwarding results to Grok for a review. **You have become the message bus.**

ccteam's fix is not to build another framework that wraps everything — each vendor's tool is already good and evolving weekly. It only provides the missing **connective tissue**: identity, routing, dispatch guarantees, a cost ledger, and cross-machine execution. It lets these agents know each other, know how to find each other, and know whether a task is done.

---

## Architecture: One Daemon, 8 MCP Tools

After installation, ccteam starts a Rust daemon on your machine and registers the same set of MCP tools across all the CLIs you already have:

```bash
ccteam config   # register MCP with Claude/Codex/Grok/Kimi/OpenCode
ccteam start    # start the daemon
```

**8 tools, available in any connected session:**

| Tool | Purpose |
|---|---|
| `session_spawn` | Start a new session (specify vendor/model/task) |
| `session_dispatch` | Dispatch additional tasks to an existing session |
| `session_collect` | Collect session results |
| `session_list` | List all sessions and their individual costs |
| `session_stop` | Stop a specified session |
| `status` | View vendor capabilities + routing notes for the current host |
| `chat_send_file` | Send a file to a session |
| `screenshot` | Take a screenshot |

**You don't need to memorize these tool names** — just say what you want in natural language, and the session calls them itself:

```
"Hand the RFC-12 implementation to codex, run it in the background, report the diff and test results when done"
→ session_spawn{vendor:"codex", task:"...", title:"impl"} then wait for notification

"Ask grok what's wrong with this stack trace, wait for its answer"
→ session_spawn{vendor:"grok", wait_seconds:120, ...} with inline waiting
```

---

## The Session Model

Each session has a persistent ID (`s1`, `s2`, `s47`...), survives daemon restarts, and can be resumed or extended at any time. All state lives in `.ccteam/` as plain files, visible in `git status`.

```
your-repo/
  .ccteam/          ← session state, cost ledger, routing
  .claude/
    agents/         ← personas you choose to install
    settings.local.json  ← ccteam only writes here, never touches settings.json
```

**Projects are bound to hosts.** Each project is registered to one machine (local or satellite); sessions automatically run on that machine — spawn a session in a GPU-box project and the tests run on the GPU box, while transcripts and costs remain in your main console.

---

## Three Control Modes

**1. Telegram / Feishu IM**

Settings → IM, paste a bot token, and the chat window becomes your console. Completion notifications, HITL `[approve] [deny]` buttons, and generated files all appear in the same thread. Assign tasks at midnight, close your laptop and sleep, check results in the morning.

```
/cd my-project          # switch project
/new codex              # start a codex session
@s2 run the test suite  # talk directly to a specific session
/status                 # check team status and costs
```

**2. Browser UI (LAN)**

`http://<LAN-IP>:7331/?token=…` is a chat shell, not a dashboard. Each session has its own Chat tab, delegation tree, cost pill, and marketplace.

**3. Inside a Claude Session, Orchestrate in Natural Language**

This is the most fundamental usage. Any Claude session connected to ccteam requires no additional installation — just say:

```
Spawn a codex session, have it implement RFC-12 and run the tests;
report back when green.

Plan this refactor, then delegate: codex implements, grok profiles
the hot path in parallel, kimi sweeps the rename across the repo.
Collect everything into one summary.

Spawn a claude reviewer on s2's diff — I'm not merging until it signs off.
```

---

## Three Core Orchestration Patterns

### Plan → Build → Gate

```
[Claude s1 lead]
  → session_spawn codex s2: "implement RFC-12, run tests, report diff summary"
  ← completion notification: files changed, tests green
  → git diff (review the code yourself, not have the AI read it aloud)
  → session_spawn claude s3: "review this diff — MERGE or BLOCK with reasons"
  ← verdict: MERGE, no blockers
  → stop s3; keep s2 for follow-ups
```

The lead said two sentences total; two sessions from different vendors handled the implementation and review, with every hop recorded in the ledger.

### Grind + Probe

Codex runs long tasks (implementation, migration, mechanical refactoring) while Grok gives you a quick second opinion in parallel. By the time Codex finishes, you already know from Grok where the bottleneck is.

```
session_spawn{vendor:"codex", task:"migrate auth module to OAuth2", title:"grind"}
session_spawn{vendor:"grok", task:"profile this hot path", wait_seconds:120, title:"probe"}
```

### Bulk on Budget

The repetitive, mechanical 80% of work fans out to Kimi (low cost); judgment and planning tasks are reserved for Claude.

```
Kimi × N: sweep all 47 modules for deprecated API calls, fix each
Claude: review the collected diff and decide which 3 are too risky to merge
```

---

## Routing: Who Does What, Based on Facts Not Guesses

The `status` tool returns the real state of each vendor on this machine (installed / authenticated / within budget) — no assumptions:

```
# one status call shows
Vendors on host "my-mac":
  claude-code  ready (claude-opus-4-8)
  codex        ready (sol-max)
  grok         not_ready — grok CLI not found
  kimi         ready (k2)

Daily budget: claude $12/$30, codex $8/$30, kimi $2.40/$20
```

Routing decisions are stored in plain text files that you write and the AI reads:

```markdown
# ~/.ccteam/routing.md

| Task type | Vendor / model | Why |
|---|---|---|
| Long refactors, migrations | codex / sol-max / high | grinds without wobbling |
| Quick second opinion | grok / default / low | minute-scale answers |
| Final review before merge | claude / opus / high | catches what builder rubber-stamps |
| Repetitive mechanical work | kimi / k2 / low | cheap, sufficient |
```

A project-level `.ccteam/routing.md` fully overrides the global config (no merging). `status` passes the selected file verbatim to any session of any vendor — every planner sees exactly the same text.

---

## Multi-Machine: Turn a Laptop Behind NAT into a GPU Box

```bash
# control machine
ccteam satellite create --name gpu-box
# → generates a join token

# satellite machine (even behind NAT)
ccteam satellite join --token <token>
# → actively dials out to the daemon
```

The project is bound to `gpu-box`; when you spawn a session, tests run on that machine. Switching machines means switching projects — the ledger and team view remain in the main console.

Current limitation: satellite machines only support Claude sessions; Codex/Grok/Kimi run on the daemon's local machine.

---

## Security Design

**No prompt injection**: Personas are loaded through vendor-native mechanisms (`.claude/agents/`); task text is forwarded verbatim — no wrapper layer secretly inserting content.

**No screen scraping**: State comes from transcripts and structured events, not terminal output parsing.

**Local-first**: `~/.ccteam` plus your repo — no cloud components, your code never leaves your machine.

**Budget enforcement without hard-kills**: When a per-vendor daily limit is reached, new spawns are rejected with an explanation — running sessions are not killed.

**Runaway fan-out prevention**: Guardrails reject recursive dispatch that exceeds limits with explicit reasons — not silent truncation.

**Idempotency keys**: `session_spawn`/`session_dispatch` support idempotency keys so retries do not create duplicate sessions — critical on unreliable connections.

---

## HITL (Human-in-the-Loop) Approval

```
session_spawn{vendor:"codex", approval_mode:true, task:"..."}
```

When Codex encounters a tool call requiring permission during execution, the request arrives via IM as `[approve] [deny]` buttons. Deny goes through the vendor's native gate, blocking that tool call without killing the session.

---

## Marketplace

```bash
# install a persona from ccteam-hub (sha256 verified, verbatim copy)
ccteam marketplace install team-brain
```

Once the `team-brain` persona is installed, a single session becomes a "chief of staff" — with established routing habits and review gates, you say one thing and it splits and delegates the work itself.

The Claude Code plugin (vendor-native) delegates installation to Claude Code itself; ccteam only touches two settings keys.

---

## Installation and Verification

```bash
# one-line install (Rust binary → ~/.local/bin, no sudo required)
curl -sSL https://raw.githubusercontent.com/firstintent/ccteam/main/install.sh | sh

# register MCP with each vendor CLI
ccteam config

# verify
ccteam doctor --verify-mcp   # 8 tools, 0 stubs → exit code 0
claude mcp list               # server "ccteam" → ✔ Connected

# start
ccteam start
# → prints http://<lan-ip>:7331/?token=...
```

Build from source (requires Rust + Node):
```bash
git clone https://github.com/firstintent/ccteam && cd ccteam && make install
```

---

## Comparison with Heinu1 / PR-Daemon

These tools have some overlap in goals but occupy different positions:

| | **ccteam** | **Heinu1** | **PR-Daemon** |
|---|---|---|---|
| Control channel | Telegram/Feishu/Browser | WeChat | GitHub PR |
| Orchestration layer | Agents dispatching to each other | Human → Claude (single session) | Multi-round PK review |
| Cross-vendor | ✅ Claude/Codex/Grok/Kimi | ✗ (Claude only) | ✅ (DeepSeek/Opus/Codex) |
| Cross-machine | ✅ Satellite machines | ✗ | ✗ |
| Local-first | ✅ | ✅ | ✅ |
| Typical use case | One lead Claude directing a team of specialists | Phone-controlled remote Claude | Automated PR review pipeline |

All three can coexist: ccteam manages agent-to-agent collaboration, Heinu1 manages human-computer interaction, and PR-Daemon manages the review pipeline.

---

## Key Assessment

ccteam solves a real pain point: **you have multiple good agents but are manually playing the role of router**. Its positioning is clear — it does not replace each vendor's tool, only provides the coordination layer those tools lack.

A Rust daemon is the right choice: always running in the background, low resource use, stable across restarts. The interface of 8 MCP tools is small enough that any existing Claude session can connect and immediately start using them — no learning curve.

The three most valuable design decisions:
1. **Routing is your plain text, not framework magic** — you can version-control your team strategy.
2. **Delivery guarantees are explicit** — at-least-once notification, idempotency keys, a child's turn is written to disk before the parent is notified.
3. **Budget visibility without hard-kills** — delegation incurs cost, fees are tracked in real time in the ledger, and when the daily limit is reached new tasks are rejected but current work is not interrupted.

79 stars, but worth watching today. Once Satellite execution covers all vendors, multi-machine agent teams will be truly mature.

---

## References

- **GitHub**: [firstintent/ccteam](https://github.com/firstintent/ccteam)
- **Orchestration guide**: [docs/orchestration.md](https://github.com/firstintent/ccteam/blob/main/docs/orchestration.md) · [Chinese](https://github.com/firstintent/ccteam/blob/main/docs/orchestration-cn.md)
- **Usage manual**: [docs/usage.md](https://github.com/firstintent/ccteam/blob/main/docs/usage.md) · [Chinese](https://github.com/firstintent/ccteam/blob/main/docs/usage-cn.md)
- **Marketplace**: [firstintent/ccteam-hub](https://github.com/firstintent/ccteam-hub)

© 2026 Author: Mycelium Protocol
