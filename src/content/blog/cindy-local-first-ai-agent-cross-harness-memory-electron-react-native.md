---
title: "Cindy：跨 Harness 持久记忆的本地优先开源 AI Agent，纠正一次、处处生效"
description: "Cindy 是一个 Electron + React Native 的本地优先 AI Agent，把 Claude Code、Codex 等多个 Harness 统一在一个客户端里，共享跨 Harness 的持久记忆、Skills 和 Orca 多 Agent 编排，Apache-2.0 开源，可用自己的 Claude Code/Codex 订阅直接接入。"
pubDate: "2026-07-27"
category: "Tech-Experiment"
heroImage: "../../assets/images/cindy-local-first-ai-agent-cross-harness-memory-electron-react-native-banner.jpg"
---

"Correct her once; she remembers across all harnesses."

这句话说的是：在 Claude Code 里纠正了一个习惯，下次切到 Codex，同样生效。

这不是一个小改进。当前 AI Agent 生态里，每个 Harness 都是孤岛——Claude Code 有自己的 `CLAUDE.md`，Codex 有自己的配置，它们之间没有共享的记忆层。每次切换，都要从零开始。

Cindy 想解决的就是这个问题。

---

## 一、它是什么

Cindy 是一个**本地优先的开源 AI Agent 客户端**，Electron 桌面端 + Expo/React Native 移动端，TypeScript 写成，Apache-2.0 授权。

2026 年 7 月 22 日上线，5 天 776 star。

核心定位：**Harness 无关的 Agent 编排层**。把 Claude Code、Codex 这些已有的 Harness 接进来，在它们之上建立统一的记忆、Skills 和多 Agent 协作能力。

不是"套壳"——它没有把这些 Harness 替换掉，而是作为一个协调层，让它们能够共享状态。

---

## 二、跨 Harness 持久记忆

这是 Cindy 最核心的设计。

现在每个 Harness 都有自己的记忆层：Claude Code 读 `CLAUDE.md`/skills，Codex 读自己的配置，互不相通。用户纠正 Claude Code 的行为，切到 Codex 又要重新说一遍。

Cindy 的做法：在所有 Harness 上层建立统一的记忆存储。Memory 在这里不是某个 Harness 的配置文件，而是 Cindy 客户端层面的持久状态，跨 Harness 共享：

```
用户纠正一次
    ↓
Cindy 记忆层
    ├── 注入到 Claude Code session
    └── 注入到 Codex session
```

"Correct her once" — 纠正动作只发生一次，对所有 Harness 生效。

除了 Memory，还有 Skills（一次定义、处处复用的工作方式模板）。技术上是同一个层的两种表达：一种存矫正记录，一种存可调用的工作流程。

---

## 三、Orca 多 Agent 编排

AGENTS.md 里有一条规则：

> 修改 Orca 多 Agent 协同时，必须先读 `docs/dev-rules/orca-team-architecture.md`

README 的描述：

> "one task can even be planned, executed in parallel, and reviewed by agents on different harness × model combos"

一个任务，不同阶段可以分配给不同 Harness × Model 的组合：

```
Plan   → Claude Opus 4.8 (Cindy native harness)
Execute → Claude Code × Sonnet (并行执行)
Review → Codex × GPT-5.5 (独立评审)
```

各个 Agent 的 Workspace、Memory、Skills 和 Tools 保持连续——切换 Harness 不等于切换上下文，Memory 层保证了连续性。

---

## 四、技术架构

### 仓库结构

```
apps/
  desktop/     → Electron 桌面客户端
  mobile/      → Expo / React Native 移动端
packages/
  *            → auth, device-link, agent orchestration, model providers...
cindy-protocol/  → wire 协议（git submodule，与服务端共享）
```

pnpm monorepo，Node.js 22.x。

Harness 的可执行文件（claude-code、codex、ripgrep）不提交进仓库，由 `pnpm install` 按平台下载。这意味着你本地已有的 Claude Code / Codex 安装可以直接被 Cindy 使用。

### 本地优先

Cindy 跑在你自己的机器上，访问你真实的文件系统和已登录的 Apps。

数据不上传（除了可以在源码里关掉的 TapDB 聚合统计）。

隐私设计：聊天内容、文件内容、工作目录数据不被收集。Crash dump 留在本地不自动上传。

### 服务端与客户端的分层

Cindy 的开源部分是客户端。服务端在独立仓库，未开源。

使用方式有三种：
- Cindy 官方云服务（托管 API，按用量计费）
- 直接用你已有的 Claude Code / Codex 订阅（**不产生双重计费**）
- 本地模式（无需 Cindy 账号，不连接服务端）

---

## 五、接入已有的 Claude Code / Codex 订阅

这一点值得单独说。

如果你已经订阅了 Claude Code 或 Codex，可以在 Cindy 里直接授权它们，不产生额外费用——Cindy 调用的是你自己的 Coding Plan 配额，不是另起一套计费。

```bash
git clone https://github.com/makecindy/cindy.git
cd cindy
git submodule update --init --recursive cindy-protocol
pnpm install
pnpm restart:desktop:remote --region=global  # 用 Cindy 云账号
```

本地模式只需要在登录界面选 "Local mode"，不创建 Cindy 账号。

---

## 六、技术判断

Cindy 切入的问题是真实存在的：

**当你同时用多个 Harness 时，维护跨 Harness 一致性的成本是真实的。** CLAUDE.md、Codex 配置、各种 skills 文件需要分别维护，纠正一个 Harness 的习惯不会自动迁移到另一个。

Cindy 的解法——**在 Harness 之上建统一的记忆层**——在逻辑上是对的。它不替换 Harness，而是作为协调层存在，这也是为什么它可以在不改变你已有订阅的情况下接入。

需要观察的是：

**服务端闭源** 意味着某些能力（device-link、IM 集成、自动化调度）依赖 Cindy 的服务端。对于完全自主可控的用户，这是个依赖项。本地模式可以绕开这个依赖，但功能也相应受限。

**Orca 多 Agent 编排** 目前只在文档里提到架构，实际产品化程度还需要实际使用验证。

总体判断：对于每天在多个 Harness 之间切换的用户，Cindy 解决了一个真实的痛点。值得装上试一试——毕竟 Apache-2.0，风险可控。

> 项目：github.com/makecindy/cindy（776 ⭐，Apache-2.0）  
> 网站：cindy.app  
> 下载：cindy.app/download  
> 语言：TypeScript，pnpm monorepo  
> 平台：macOS/Windows（Electron）+ iOS/Android（React Native）

<!--EN-->

## Cindy: Local-First Open-Source AI Agent with Cross-Harness Persistent Memory

"Correct her once; she remembers across all harnesses."

What this means: correct a habit in Claude Code, and it applies the next time you switch to Codex.

This isn't a small improvement. In today's AI agent ecosystem, every harness is an island — Claude Code has its own `CLAUDE.md`, Codex has its own configuration, with no shared memory layer between them. Every switch means starting over.

Cindy aims to solve this.

---

## What It Is

Cindy is a **local-first open-source AI agent client** — Electron desktop + Expo/React Native mobile, built in TypeScript, Apache-2.0 licensed.

Launched July 22, 2026, 776 stars in 5 days.

Core positioning: **harness-agnostic agent orchestration layer**. It brings Claude Code, Codex, and other harnesses into a single client, building unified memory, Skills, and multi-agent collaboration on top of them.

Not a "wrapper" — it doesn't replace these harnesses, but acts as a coordination layer so they can share state.

---

## Cross-Harness Persistent Memory

This is Cindy's core design.

Currently, every harness has its own memory layer: Claude Code reads `CLAUDE.md`/skills, Codex reads its own config, with no cross-talk. Correct Claude Code's behavior, then switch to Codex, and you have to explain it again.

Cindy's approach: build a unified memory store above all harnesses. Memory here isn't a config file for some harness — it's a persistent state at the Cindy client layer, shared across harnesses:

```
User corrects once
    ↓
Cindy memory layer
    ├── Injected into Claude Code session
    └── Injected into Codex session
```

"Correct her once" — the correction happens once, takes effect everywhere.

Beyond Memory, Skills (reusable workflow templates defined once and called anywhere) live in the same layer: one expression stores correction records, the other stores callable workflows.

---

## Orca Multi-Agent Orchestration

AGENTS.md includes this rule:

> Before modifying Orca multi-agent coordination, read `docs/dev-rules/orca-team-architecture.md`

README's description:

> "one task can even be planned, executed in parallel, and reviewed by agents on different harness × model combos"

One task, different phases assigned to different harness × model combinations:

```
Plan   → Claude Opus 4.8 (Cindy native harness)
Execute → Claude Code × Sonnet (parallel execution)
Review → Codex × GPT-5.5 (independent review)
```

Each agent's workspace, memory, skills, and tools remain continuous — switching harnesses doesn't mean switching context, because the memory layer guarantees continuity.

---

## Technical Architecture

### Repository Structure

```
apps/
  desktop/     → Electron desktop client
  mobile/      → Expo / React Native mobile
packages/
  *            → auth, device-link, agent orchestration, model providers...
cindy-protocol/  → wire protocol (git submodule, shared with server)
```

pnpm monorepo, Node.js 22.x.

Harness executables (claude-code, codex, ripgrep) are not committed to the repo — they're downloaded per-platform by `pnpm install`. This means your existing Claude Code / Codex installations can be used directly by Cindy.

### Local-First

Cindy runs on your own machine, accessing your real filesystem and logged-in apps.

Data doesn't leave your device (except for the TapDB aggregate analytics, which can be removed in source builds).

Privacy design: chat content, file content, and working directory data are never collected. Crash dumps stay local and are never automatically uploaded.

### Client vs. Server Split

The open-source part of Cindy is the client. The server lives in a separate repository and is not open-sourced.

Three modes of use:
- Cindy official cloud service (hosted API, usage-based billing)
- Use your existing Claude Code / Codex subscription (**no duplicate billing**)
- Local mode (no Cindy account required, no server connection)

---

## Using Your Existing Claude Code / Codex Subscription

This point deserves its own mention.

If you already subscribe to Claude Code or Codex, you can authorize them directly in Cindy without additional charges — Cindy draws from your own Coding Plan quota, not a separate billing line.

```bash
git clone https://github.com/makecindy/cindy.git
cd cindy
git submodule update --init --recursive cindy-protocol
pnpm install
pnpm restart:desktop:remote --region=global
```

Local mode just requires selecting "Local mode" on the login screen — no Cindy account needed.

---

## Technical Verdict

Cindy addresses a real problem:

**When you use multiple harnesses simultaneously, the cost of maintaining cross-harness consistency is real.** CLAUDE.md, Codex config, and various skill files need to be maintained separately; correcting one harness's behavior doesn't automatically migrate to another.

Cindy's solution — **building a unified memory layer above harnesses** — is logically sound. It doesn't replace harnesses; it acts as a coordination layer. This is also why it can integrate without changing your existing subscriptions.

Points to watch:

**The server is closed-source**, meaning some capabilities (device-link, IM integration, automation scheduling) depend on Cindy's server. For users who want full control, this is a dependency. Local mode bypasses this dependency but with reduced functionality.

**Orca multi-agent orchestration** is currently only described in documentation; the actual level of productization needs real-world validation.

Overall: for users who switch between multiple harnesses daily, Cindy solves a real pain point. Worth installing and trying — Apache-2.0 means the risk is manageable.

> Project: github.com/makecindy/cindy (776 ⭐, Apache-2.0)  
> Website: cindy.app  
> Download: cindy.app/download  
> Language: TypeScript, pnpm monorepo  
> Platforms: macOS/Windows (Electron) + iOS/Android (React Native)
