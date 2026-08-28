---
title: "Agent Network 调研：不做又一个 Agent 平台，只做跨厂商 Agent 的通信层"
titleEn: "Agent Network: Not Another Agent Platform — Just the Communication Layer Across Vendors"
description: "调研 sleep2agi/agent-network：把 Claude Code、Claude Agent SDK、Codex、Grok Build 接进同一张网络，靠 MCP 互相发现、靠 SSE 实时派活。跟本站已写过的 Multica（看板+技能复利）、Omni（企业知识权限）、Nerve（Claude Agent SDK 运行时）不是同类——它不提供看板、不提供知识库，只做薄薄一层跨厂商通信协议。文章重点拆了一个真实的生产陷阱：`anet node start` 打印✅不代表节点真的起来了，2.3.0-preview.40 之前的版本会假报成功，真正可信的判据是 `tmux has-session -t \"=<alias>\"`。Apache-2.0，68 星，TypeScript。"
descriptionEn: "A deep dive into sleep2agi/agent-network: it wires Claude Code, Claude Agent SDK, Codex, and Grok Build into one network, where agents discover each other over MCP and get dispatched tasks in real time over SSE. Unlike this blog's earlier coverage of Multica (kanban + skill compounding), Omni (permission-aware company knowledge), and Nerve (a Claude Agent SDK runtime), agent-network isn't a platform at all — no kanban, no knowledge base, just a thin cross-vendor communication protocol. The core of this piece is a real production trap: `anet node start` printing a green checkmark does not mean the node actually started — versions before 2.3.0-preview.40 could false-report success, and the only trustworthy check is `tmux has-session -t \"=<alias>\"`. Apache-2.0, 68 stars, TypeScript."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Tech-Experiment"
tags: ["AI Agent", "MCP", "Claude Code", "Codex", "多智能体", "开源工具", "TypeScript", "自托管", "开发工具"]
heroImage: "../../assets/images/agent-network-anet-multi-runtime-agent-hub-fake-success-trap-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

> **GitHub**：sleep2agi/agent-network（https://github.com/sleep2agi/agent-network）· **Stars**：68 · **Forks**：9
> **协议**：Apache-2.0 · **语言**：TypeScript
> **文档站**：anet.sh
> **安装**：`npm install -g bun @sleep2agi/agent-network @sleep2agi/agent-node`
> **自托管**：是（Hub + Dashboard + SQLite 全部跑在自己机器上）

---

## 一句话理解

市面上大多数"开源 Agent 平台"都想做全家桶：看板、知识库、技能复利、权限系统。agent-network 反过来，**只做一件事**——把不同厂商的 Agent CLI（Claude Code、Claude Agent SDK、Codex、Grok Build）接进同一张网络，让它们互相发现、互相派活。它不关心你的任务怎么显示、你的知识怎么存，它只关心"A 找到 B，A 把活派给 B"这一步怎么做对。

这条边界画得很克制，也正因为薄，它能跨厂商——本站之前写过的三个同类项目都不是这个思路：

- **Multica**（4.1 万 star）：看板 + assignee 身份化 + 技能复利，本质是"给 Agent 一个团队协作界面"
- **Omni**（758 star）：企业知识权限感知的公司级 Agent，本质是"给 Agent 一套企业数据访问控制"
- **Nerve**（ClickHouse 出品）：Claude Agent SDK 的自托管运行时，绑定在 Claude 生态里

agent-network 不提供看板、不提供知识库、不绑定单一厂商——它是一根**跨厂商的管道**：`Agent A --任务--> CommHub --SSE--> Agent B`，中间靠 MCP 做发现。如果你已经在用 Multica 管理团队协作、用 Omni 接企业知识，agent-network 解决的是另一层问题：这些不同厂商的 Agent 进程，怎么在网络层面互相知道对方存在。

## 架构：一个 Hub，多个 Node

```
Agent A  ──任务──▶  CommHub  ──SSE──▶  Agent B
                       │
                   Dashboard
```

三个角色：

- **Hub**：常驻服务，跑在 `:9200`，负责节点注册、任务路由、SSE 广播。SQLite 存状态，不需要额外数据库。
- **Node**：每个接入的 Agent CLI 实例（Claude Code、Codex、Grok Build……）注册成一个 node，通过 MCP 被其他 node 发现。
- **Dashboard**：跑在 `:3000` 的 Web 界面，从这里手动给某个 Agent 派任务，也能看到整张网络的实时状态。

## 装到跑通

需要 Node.js ≥ 22.13。三个终端：

```bash
npm install -g bun @sleep2agi/agent-network @sleep2agi/agent-node

# 终端 1：起 Hub
anet hub start

# 终端 2：起 Dashboard
anet hub dashboard

# 终端 3：注册并起一个 Node
anet login --hub http://127.0.0.1:9200 --username admin
anet node create my-bot
anet node start my-bot
```

验证 Hub 活着：`curl http://127.0.0.1:9200/health`，返回 JSON 里应该有 `"ok":true`。

默认管理员是 `admin` / `anethub`（`@preview` 2.2.22-preview.4 起改成首次启动打印一次性随机密码）。**只要打算暴露到公网，登录后第一件事是 `anet passwd` 改密**——默认密码是公开写在 README 里的，扫到端口就能进。

## 真正值得记住的坑：`anet node start` 的✅不能信

这是这个项目 README 里自己主动交代的一个坑，也是这篇文章最想拆的地方——因为它代表了一类通用的运维陷阱：**命令退出码是 0、输出里印了绿色✅，不代表底层进程真的活着。**

`anet node start my-bot` 跑完会打印：

```
✅ node "my-bot" started detached (tmux session live)
```

看起来一切正常。但在 [PR #895](https://github.com/sleep2agi/agent-network/pull/895)（2026-08-17 合入，随 `2.3.0-preview.40` 发布）修复之前，这条✅在 detached 场景下**可能是假的**——命令本身成功退出、日志也确实打印了"started"，但 tmux 会话实际没起来。

问题出在哪：`anet node start` 用 `tmux new-session -d` 起一个 detached 会话跑 Agent 进程，然后**立刻**检查会话是否存在来判断成功与否。但 tmux 创建 detached session 和会话真正可查询之间，存在一个竞态窗口——如果检查发生得太早，或者被启动的进程本身在几秒内就崩溃退出（比如 API key 没配对、依赖没装全），CLI 拿到的"看起来像成功"的返回值，跟"节点真的在跑"这两件事就脱钩了。

**真正可信的判据**，README 里写得很直接：

```bash
tmux has-session -t "=my-bot"
```

注意这个 `=` 前缀是必须的——`tmux has-session -t my-bot`（不带 `=`）做的是**前缀匹配**，如果你之前起过一个叫 `my-bot-old` 的会话没清理干净，裸名字查询会匹配到它，让你以为 `my-bot` 活着，实际上活的是别的会话。这种"看起来对了但对错了原因"的假阳性，比命令直接报错更难排查。

批量场景（`anet project up` 一次起多个节点）的退出码可信度要晚一步：直到 [PR #896](https://github.com/sleep2agi/agent-network/pull/896)（同样随 `2.3.0-preview.40` 发布）才修好。也就是说，**如果你现在装的是 `2.3.0-preview.40` 之前的版本，`node start` 和 `project up` 的返回值都不能直接当真，得手动 `tmux has-session -t "=<alias>"` 逐个核实**。

这类"退出码/日志说成功，但底层状态没对齐"的陷阱在分布式/多进程编排工具里很常见（systemd unit、Docker健康检查、K8s readiness probe踩过的坑本质上是一类问题），agent-network 至少做到了在 README 里主动写清楚、给出可信判据、注明修复版本号——这个透明度本身值得记一笔。

## 三个核心判断

**1. 定位比功能更值得看**：agent-network 没有试图做全家桶，这个克制的边界让它能跨厂商——如果你已经用 Multica/Omni 管团队协作，agent-network 补的是"不同 Agent CLI 互相发现"这一层，不是替代品，是另一层积木。

**2. 假阳性陷阱是最有价值的信息，不是功能列表**：`node start` 的✅陷阱说明一件事——多进程编排工具的"启动成功"判据，永远应该是外部可验证的状态检查（tmux/进程存在性），不能只信自己的日志。这条经验能直接搬到别的自托管工具排障上。

**3. 68 星、9 fork、今天还在提交**：项目非常早期，文档站（anet.sh）和 npm 包都是活的，`@preview` 通道功能更新更快（比如 Codex TUI 共存、OpenCode runtime）。值得关注，但生产环境目前建议锁定 `@latest` 而不是追 `@preview`。

## 参考资源

- GitHub：https://github.com/sleep2agi/agent-network
- 文档站：https://anet.sh
- 节点启动假阳性修复：PR #895（https://github.com/sleep2agi/agent-network/pull/895）
- 批量启动退出码修复：PR #896（https://github.com/sleep2agi/agent-network/pull/896）
- npm：`@sleep2agi/agent-network`、`@sleep2agi/agent-node`

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **GitHub**: sleep2agi/agent-network (https://github.com/sleep2agi/agent-network) · **Stars**: 68 · **Forks**: 9
> **License**: Apache-2.0 · **Language**: TypeScript
> **Docs**: anet.sh
> **Install**: `npm install -g bun @sleep2agi/agent-network @sleep2agi/agent-node`
> **Self-hosted**: Yes (Hub + Dashboard + SQLite all run on your own machine)

---

## The one-sentence summary

Most open-source "agent platforms" try to be everything: a kanban board, a knowledge base, skill compounding, a permission system. agent-network goes the other way — **it does exactly one thing**: wire different vendors' Agent CLIs (Claude Code, Claude Agent SDK, Codex, Grok Build) into one network so they can discover each other and hand off tasks. It doesn't care how your tasks are displayed or where your knowledge lives — it only cares about getting "A finds B, A hands work to B" right.

That's a deliberately narrow scope, and it's precisely why it can be cross-vendor — none of the three similar projects this blog has already covered take the same approach:

- **Multica** (41k stars): a kanban board + assignee identity + skill compounding — essentially "give agents a team collaboration UI"
- **Omni** (758 stars): a permission-aware company-knowledge agent — essentially "give agents access control over your company's data"
- **Nerve** (from the ClickHouse team): a self-hosted runtime for the Claude Agent SDK, tied to a single vendor's ecosystem

agent-network provides no kanban, no knowledge base, and no vendor lock-in — it's a **thin cross-vendor pipe**: `Agent A --task--> CommHub --SSE--> Agent B`, with MCP handling discovery in between. If you're already using Multica to manage team collaboration or Omni to plug in company knowledge, agent-network solves a different layer: how these different vendors' agent processes know about each other on the network at all.

## Architecture: one Hub, many Nodes

```
Agent A  ──task──▶  CommHub  ──SSE──▶  Agent B
                       │
                   Dashboard
```

Three roles:

- **Hub**: a long-running service on `:9200` that handles node registration, task routing, and SSE broadcast. State lives in SQLite — no extra database required.
- **Node**: each connected Agent CLI instance (Claude Code, Codex, Grok Build…) registers as a node, discoverable by other nodes over MCP.
- **Dashboard**: a web UI on `:3000` for manually assigning tasks to an agent and watching the whole network's live state.

## Getting it running

Requires Node.js ≥ 22.13. Three terminals:

```bash
npm install -g bun @sleep2agi/agent-network @sleep2agi/agent-node

# Terminal 1: start the Hub
anet hub start

# Terminal 2: start the Dashboard
anet hub dashboard

# Terminal 3: register and start a Node
anet login --hub http://127.0.0.1:9200 --username admin
anet node create my-bot
anet node start my-bot
```

Verify the Hub is alive: `curl http://127.0.0.1:9200/health` should return JSON containing `"ok":true`.

The default admin is `admin` / `anethub` (as of `@preview` 2.2.22-preview.4, first `hub start` instead prints a one-time random password). **If you're exposing this to the public internet at all, run `anet passwd` immediately after logging in** — the default password is public, sitting right there in the README.

## The trap actually worth remembering: `anet node start`'s ✅ can lie

This is a pitfall the project's own README volunteers, and it's the part of this piece worth dwelling on the most — because it's a general lesson about a whole class of operational traps: **a zero exit code and a green checkmark in the output do not mean the underlying process is actually alive.**

Running `anet node start my-bot` prints:

```
✅ node "my-bot" started detached (tmux session live)
```

That looks fine. But before [PR #895](https://github.com/sleep2agi/agent-network/pull/895) (merged 2026-08-17, shipped in `2.3.0-preview.40`), that checkmark could be **wrong** in detached scenarios — the command itself exits successfully, the log genuinely says "started," but the tmux session isn't actually there.

Here's the mechanism: `anet node start` spins up a detached tmux session with `tmux new-session -d` to run the agent process, then **immediately** checks whether that session exists to decide success or failure. But there's a race window between a detached tmux session being created and it becoming reliably queryable — if the check fires too early, or if the launched process itself crashes within a few seconds (a missing API key, an incomplete dependency install), the CLI's "looks successful" return value decouples from whether the node is actually running.

The **trustworthy check**, spelled out directly in the README:

```bash
tmux has-session -t "=my-bot"
```

That leading `=` is required — `tmux has-session -t my-bot` (no `=`) does a **prefix match**. If you previously had a leftover session called `my-bot-old` that never got cleaned up, the bare-name query will match it, and you'll believe `my-bot` is alive when what's actually alive is something else. This kind of "it looked right but for the wrong reason" false positive is harder to debug than an outright error.

The batch scenario (`anet project up`, starting several nodes at once) took longer to fix — its exit code only became trustworthy with [PR #896](https://github.com/sleep2agi/agent-network/pull/896), shipped in the same `2.3.0-preview.40` release. In other words: **if you're running anything older than `2.3.0-preview.40`, don't trust the return value of either `node start` or `project up` — manually verify each node with `tmux has-session -t "=<alias>"`.**

This class of trap — exit code and logs claiming success while the underlying state never actually converged — shows up constantly in distributed/multi-process orchestration tools (the same root problem shows up in systemd unit status, Docker healthchecks, and Kubernetes readiness probes). What agent-network gets right isn't avoiding the bug entirely — it's documenting it plainly in the README, giving readers a trustworthy check, and naming the exact fix version. That transparency is worth noting on its own.

## Three takeaways

**1. The positioning matters more than the feature list.** agent-network didn't try to build an everything-platform, and that restraint is exactly what lets it be cross-vendor. If you're already running Multica or Omni for team workflow, agent-network fills a different layer — different agent CLIs discovering each other — not a replacement, another building block.

**2. The false-positive trap is more valuable information than any feature list.** The `node start` checkmark trap illustrates something general: "startup succeeded" for a multi-process orchestration tool should always be an externally-verifiable state check (does the tmux session/process actually exist), never just trusting your own log output. That lesson transfers directly to debugging other self-hosted tools.

**3. 68 stars, 9 forks, still shipping commits today.** This is an early-stage project — the docs site (anet.sh) and npm packages are both actively maintained, and the `@preview` channel ships faster (Codex TUI coexistence, an OpenCode runtime). Worth watching, but for production use, pin to `@latest` rather than chasing `@preview`.

## References

- GitHub: https://github.com/sleep2agi/agent-network
- Docs: https://anet.sh
- Node-start false-positive fix: PR #895 (https://github.com/sleep2agi/agent-network/pull/895)
- Batch-start exit code fix: PR #896 (https://github.com/sleep2agi/agent-network/pull/896)
- npm: `@sleep2agi/agent-network`, `@sleep2agi/agent-node`

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
