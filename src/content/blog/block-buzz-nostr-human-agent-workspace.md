---
title: "Buzz：Block 开源的人机协作工作台，建在你自己的 Nostr relay 上"
titleEn: "Block Buzz: Human-Agent Collaborative Workspace on Your Own Nostr Relay"
description: "Block（Jack Dorsey 旗下公司）2026年3月开源的 Buzz：人类和 AI Agent 在同一个 Nostr relay 上协作，每个操作都是加密签名的事件。7374 stars，Rust + Tauri + React，支持 Claude Code / Codex / Goose 直接接入。自托管，数据主权在你手里。"
descriptionEn: "Block (Jack Dorsey's company) open-sourced Buzz in March 2026: humans and AI agents collaborate in the same Nostr relay, every action a cryptographically signed event. 7374 stars, Rust + Tauri + React, native support for Claude Code / Codex / Goose. Self-hosted — your data stays yours."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["Nostr", "AI Agent", "开源", "自托管", "协作工具", "Rust", "Claude Code", "Block"]
heroImage: "../../assets/images/block-buzz-nostr-human-agent-workspace-banner.jpg"
---

> **仓库**：block/buzz · Rust · Apache 2.0 · 7374 stars  
> **开源时间**：2026-03-06  
> **作者**：Block（原 Square，Jack Dorsey 旗下）  
> **官方定位**：A hive mind communication platform — *A workspace where humans and agents build together, on a relay you own.*

---

## 一、它是什么

Buzz 是一个自托管的团队工作台。它和 Slack、Discord、Linear 做的事情有重叠，但底层完全不同。

区别不在功能列表，在底层协议：**所有操作都跑在 Nostr relay 上**。你发的消息、某人点的 👍、一个工作流步骤的执行、代码 review 的审批——都是同一种东西：一个加密签名的事件，进入同一个事件日志。

人类发的事件和 AI Agent 发的事件，格式完全一样。

这是 Buzz 和现有所有工具的根本差异：不是"给 Slack 接一个 bot"，而是**Agent 是工作台的原生公民**——有自己的 keypair，自己的频道成员身份，自己的 audit trail，和人类是对等的。

---

## 二、为什么是 Nostr

Nostr 协议（NIP-01）在这里不是一个噱头，是一个工程决策。

每个事件的结构是：

```
id      sha256(canonical bytes)
pubkey  secp256k1 public key
kind    整数（唯一的 switch）
tags    结构化元数据
content JSON payload
sig     Schnorr 签名
```

这个结构意味着：
- **身份是密码学原语，不是账号系统**。人类用 NIP-42 Schnorr 认证，Agent 用 NIP-98。两者同等有效，同等可验证。
- **新功能 = 新 kind 整数**，零破坏性变更。工作流审批是一种 kind，git patch 是一种 kind，反应是一种 kind，Agent 任务是一种 kind，它们都进同一个 log，用同一个搜索索引查。
- **audit trail 是结构固有的，不是插件**。每一步、每一个决策、每一个审批，都在链上，带签名，带时间戳，不可篡改。

Block 的 VISION.md 里有一句话说清楚了他们为什么选 Nostr：

> "One event log. One search index. Three lenses."  
> （Stream 是实时频道视角，Forum 是异步长帖视角，Workflow 是结构化自动化视角——三个界面，一个底层。）

---

## 三、Agent 如何接入

这是对开发者最直接相关的部分。

### buzz-cli
Agent-first 命令行工具，JSON in / JSON out，为 LLM 工具调用设计：

```bash
export BUZZ_PRIVATE_KEY=<your-agent-keypair>
# Agent 现在以独立身份存在于工作台，有自己的频道成员身份
```

### buzz-acp（ACP harness）
直接支持三个主流 AI coding agent：

- **Goose**（Block 自家的 AI coding agent）
- **Codex**（OpenAI）
- **Claude Code**（Anthropic）

ACP（Agent Communication Protocol）是 Anthropic 和 Block 共同推进的协议，Buzz 是它的原生实现环境之一。Claude Code 接入 Buzz 后，可以在频道里发消息、打开仓库、发 patch、跑工作流、召唤其他 Agent。

### Agent 能做什么

Buzz 给 Agent 的权限和给人类的一样：

- 打开频道，发消息，发反应
- 读取六个月的频道历史
- 创建和编辑 canvas
- 发 git patch（NIP-34），触发 CI，参与 code review
- 编排其他 Agent
- 加入语音 huddle（当前实验性）
- 创建和管理 workflow

这不是 bot 权限，是**队友权限**——区别在于 Agent 有自己的身份，而不是借用某个集成账号的 token。

---

## 四、三个场景说明它为什么不同

**场景一：凌晨 2 点的生产事故**

> 你在事故频道输入："有没有见过这个错误？"  
> 一个监听频道的 Agent 搜索六个月历史，贴出相关线程、根因分析、修复记录，然后问你要不要叫醒上次部署的那个人。  
> 整个交换——问题、回答、证据——都留在频道里，带签名，带时间戳。

在 Slack 里做同样的事，需要一个 bot 集成、一个外部搜索 API、一个写数据库的 webhook、一个读权限的 token 管理。在 Buzz 里，这是 Agent 用自己的 keypair 做了一次 Nostr 事件查询。

**场景二：功能分支即频道**

> 你开一个 feature branch，一个频道出现了。  
> Patch 作为 NIP-34 事件落在这里，CI 把结果发进来，Agent 跑一遍初步 review，队友对感兴趣的部分点反应，合并决策和证据在同一个房间。  
> 这个频道就是"这段代码为什么存在"的记录。

**场景三：自动写发布说明**

> tag 触发 workflow。  
> Agent 读项目频道里 merged PR 的事件，起草发布说明，发到频道供人类审核，收到 👍 反应，自动发布。  
> 每一步都被签名。每一步都可搜索。

---

## 五、自托管的意义

Buzz 的核心承诺之一是数据主权：**relay you own**。

技术上，一个 relay 实例是一个 Rust 进程 + Postgres + Redis + S3/MinIO。自托管的团队把所有聊天记录、代码事件、工作流历史都放在自己的机器上，没有第三方。

多租户部署时，每个 community 有完整隔离：
- 不同 community 共享 Postgres、Redis 和对象存储，但彼此看不到对方的事件、消息、DM、搜索结果，甚至错误字符串
- 隔离通过 TLA+ 和 Tamarin（形式化验证工具）证明，不只是断言

`myproject.com` 这个 URL 就是你的工作台入口，`git clone repoa.myproject.com` 就能直接 clone 你的仓库。

---

## 六、当前状态和快速上手

**已可用**：relay、频道、线程、DM、canvas、媒体、搜索、审计日志、桌面应用（Tauri 2 + React 19）、buzz-cli、ACP 接入、YAML 工作流、NIP-34 git 事件、git 托管后端。

**开发中**：iOS/Android 移动客户端（Flutter）、工作流审批门。

**需要**：Docker + Hermit（或 Rust 1.88+、Node 24+、pnpm 10+、`just`）。

```bash
git clone https://github.com/block/buzz.git && cd buzz
. ./bin/activate-hermit
just setup && just build
just dev   # relay 起在 ws://localhost:3000，桌面应用自动打开
```

Block 内部员工有独立的 internal build，预接好 Block relay，不需要上面这些步骤。

---

## 七、判断

Buzz 有两层赌注，需要分开看。

**第一层赌注**：一个工作台可以整合团队现在用七个工具拼凑的事——聊天、代码托管、CI、review、release、搜索、自动化。这个方向有价值，但不是新想法，Linear、Notion、Jira 都在往这个方向走，问题是执行和迁移成本。

**第二层赌注**：Nostr 协议 + 密码学身份是做这件事的正确底层，因为它让 Agent 成为工作台的原生公民而不是外挂 bot。这个赌注更有意思，也更少有人押。如果这个方向对，那么 Buzz 不只是"另一个协作工具"，而是第一个原生为人机混合团队设计的工作台。

从技术完整性来看：7374 stars，Rust 实现，有 VISION + ARCHITECTURE 文档，TLA+/Tamarin 形式化验证多租户隔离——Block 是在认真做这件事的。

3月开源，7月已有7374 stars。增长速度说明市场对"Agent 原生工作台"这个方向有真实需求，而不只是对 Block 的品牌效应。

最值得关注的功能是 **ACP 接入 + buzz-acp**。Claude Code / Codex / Goose 可以直接作为队友存在于 Buzz 频道，而不是作为 bot 存在——这个细节在实际工程协作中的影响会比功能列表显示的更大。

---

*数据来源：GitHub block/buzz，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: block/buzz · Rust · Apache 2.0 · 7374 stars  
> **Open-sourced**: 2026-03-06  
> **Author**: Block (formerly Square, Jack Dorsey's company)  
> **Official positioning**: A hive mind communication platform — *A workspace where humans and agents build together, on a relay you own.*

---

## 1. What It Is

Buzz is a self-hosted team workspace. It overlaps in function with Slack, Discord, and Linear, but the underlying architecture is entirely different.

The distinction is not in the feature list — it is in the underlying protocol: **all operations run on a Nostr relay**. The messages you send, the 👍 someone clicks, the execution of a workflow step, the approval of a code review — they are all the same thing: a cryptographically signed event entering a single event log.

Events emitted by humans and events emitted by AI agents have exactly the same format.

This is the fundamental difference between Buzz and every existing tool: it is not "attaching a bot to Slack," but rather **agents are native citizens of the workspace** — with their own keypair, their own channel membership, their own audit trail, on equal footing with humans.

---

## 2. Why Nostr

The Nostr protocol (NIP-01) is not a gimmick here — it is an engineering decision.

The structure of every event is:

```
id      sha256(canonical bytes)
pubkey  secp256k1 public key
kind    integer (the sole dispatch switch)
tags    structured metadata
content JSON payload
sig     Schnorr signature
```

This structure means:
- **Identity is a cryptographic primitive, not an account system.** Humans authenticate via NIP-42 Schnorr; agents use NIP-98. Both are equally valid and equally verifiable.
- **New capability = new kind integer**, with zero breaking changes. Workflow approvals are one kind, git patches are one kind, reactions are one kind, agent tasks are one kind — they all enter the same log and are queried via the same search index.
- **The audit trail is structural, not a plugin.** Every step, every decision, every approval is on-chain, signed, timestamped, and immutable.

Block's VISION.md states clearly why they chose Nostr:

> "One event log. One search index. Three lenses."  
> (Stream is the real-time channel view, Forum is the asynchronous long-thread view, Workflow is the structured automation view — three interfaces, one substrate.)

---

## 3. How Agents Connect

This is the section most directly relevant to developers.

### buzz-cli
An agent-first command-line tool, JSON in / JSON out, designed for LLM tool calls:

```bash
export BUZZ_PRIVATE_KEY=<your-agent-keypair>
# Agent 现在以独立身份存在于工作台，有自己的频道成员身份
```

### buzz-acp (ACP harness)
Native support for three mainstream AI coding agents:

- **Goose** (Block's own AI coding agent)
- **Codex** (OpenAI)
- **Claude Code** (Anthropic)

ACP (Agent Communication Protocol) is a protocol co-developed by Anthropic and Block. Buzz is one of its native implementation environments. Once Claude Code is connected to Buzz, it can send messages in channels, open repositories, submit patches, run workflows, and summon other agents.

### What Agents Can Do

Buzz grants agents the same permissions it grants humans:

- Open channels, send messages, send reactions
- Read six months of channel history
- Create and edit canvases
- Submit git patches (NIP-34), trigger CI, participate in code reviews
- Orchestrate other agents
- Join voice huddles (currently experimental)
- Create and manage workflows

These are not bot permissions — they are **teammate permissions**. The distinction is that agents have their own identity rather than borrowing a token from some integration account.

---

## 4. Three Scenarios That Show Why It Is Different

**Scenario 1: A production incident at 2 a.m.**

> You type into the incident channel: "Has anyone seen this error before?"  
> An agent listening to the channel searches six months of history, posts the relevant threads, root-cause analyses, and fix records, then asks whether you want to wake up the person who did the last deploy.  
> The entire exchange — question, answer, evidence — stays in the channel, signed and timestamped.

Doing the same thing in Slack requires a bot integration, an external search API, a webhook that writes to a database, and token management for read permissions. In Buzz, the agent uses its own keypair to execute a Nostr event query.

**Scenario 2: Feature branch as channel**

> You open a feature branch and a channel appears.  
> Patches land here as NIP-34 events, CI posts results into the channel, an agent runs an initial review, teammates react to the parts they care about, and the merge decision and its evidence are all in the same room.  
> That channel is the record of "why this code exists."

**Scenario 3: Auto-generated release notes**

> A tag triggers a workflow.  
> An agent reads the merged-PR events in the project channel, drafts release notes, posts them to the channel for human review, receives a 👍 reaction, and publishes automatically.  
> Every step is signed. Every step is searchable.

---

## 5. What Self-Hosting Actually Means

One of Buzz's core promises is data sovereignty: **a relay you own**.

Technically, a relay instance is a Rust process + Postgres + Redis + S3/MinIO. A self-hosted team keeps all chat history, code events, and workflow history on their own machines, with no third party involved.

In multi-tenant deployments, each community is fully isolated:
- Different communities share Postgres, Redis, and object storage but cannot see each other's events, messages, DMs, search results, or even error strings.
- Isolation is proven via TLA+ and Tamarin (formal verification tools) — not merely asserted.

`myproject.com` is your workspace entry point; `git clone repoa.myproject.com` clones your repository directly.

---

## 6. Current Status and Quick Start

**Available now**: relay, channels, threads, DMs, canvas, media, search, audit log, desktop app (Tauri 2 + React 19), buzz-cli, ACP integration, YAML workflows, NIP-34 git events, git hosting backend.

**In development**: iOS/Android mobile clients (Flutter), workflow approval gates.

**Requirements**: Docker + Hermit (or Rust 1.88+, Node 24+, pnpm 10+, `just`).

```bash
git clone https://github.com/block/buzz.git && cd buzz
. ./bin/activate-hermit
just setup && just build
just dev   # relay 起在 ws://localhost:3000，桌面应用自动打开
```

Block internal employees have a separate internal build pre-connected to the Block relay; they do not need the steps above.

---

## 7. Assessment

Buzz makes two distinct bets, which need to be evaluated separately.

**The first bet**: a single workspace can consolidate what teams currently piece together across seven tools — chat, code hosting, CI, review, release, search, and automation. This direction has value, but it is not a new idea; Linear, Notion, and Jira are all moving in this direction. The question is execution and migration cost.

**The second bet**: the Nostr protocol plus cryptographic identity is the correct substrate for doing this, because it makes agents native citizens of the workspace rather than bolt-on bots. This bet is more interesting and far less contested. If this direction proves correct, then Buzz is not just "another collaboration tool" — it is the first workspace natively designed for human-agent hybrid teams.

On technical substance: 7374 stars, a Rust implementation, VISION + ARCHITECTURE documentation, and TLA+/Tamarin formal verification of multi-tenant isolation — Block is taking this seriously.

Open-sourced in March, 7374 stars by July. The growth rate signals genuine market demand for an "agent-native workspace," not just a response to Block's brand recognition.

The feature most worth watching is **ACP integration + buzz-acp**. Claude Code / Codex / Goose can exist in Buzz channels as teammates, not as bots — and that distinction will have a larger impact on real engineering collaboration than any feature list can convey.

---

*Data source: GitHub block/buzz, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
