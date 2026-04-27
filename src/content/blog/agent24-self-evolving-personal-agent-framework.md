---
title: "Agent24：让你的个人 AI Agent 24 小时在线、自我进化"
titleEn: "Agent24: A 24/7 Online, Self-Evolving Personal AI Agent Framework"
description: "Agent24 是一套为「个人 AI Agent」设计的模块化跨平台框架：Electron 壳 + 可插拔能力模块 + 多 AI 适配 + 分层记忆 + SkillClaw 风格自进化引擎。本文介绍它的设计理念、架构与技术决策，作为项目启动声明。"
descriptionEn: "Agent24 is a modular, cross-platform framework for personal AI agents: Electron shell + pluggable capability modules + multi-AI adapter + layered memory + SkillClaw-inspired self-evolution. This post lays out the design philosophy, architecture, and technical decisions as the project launch."
pubDate: "2026-04-28"
updatedDate: "2026-04-28"
category: "Progress-Report"
tags: ["Agent24", "AI Agent", "Self-Evolving", "Electron", "Modular Framework", "Personal AI", "Open Source", "AuraAI", "Progress-Report"]
heroImage: "../../assets/banner-cypherpunk-revolution.jpg"
---

> 📦 **项目地址**：[Agent24-Desktop](https://github.com/AuraAIHQ/Agent24-Desktop) · [auraai-packages](https://github.com/AuraAIHQ/auraai-packages) · [Agent24 (Skills)](https://github.com/AuraAIHQ/Agent24)
>
> 📐 **完整设计文档**：[PLAN.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/PLAN.md) · [decision.md (18 个 ADR)](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md) · [ROADMAP.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/ROADMAP.md)

---

## 一个被反复确认的痛点：AI 不会变聪明

你每天用 Claude / ChatGPT / 各种 Agent 工具完成任务：写代码、发文章、查资料、做总结。可是无论用得多熟练，**它本身不会变得更懂你**。

每开一个新会话——所有上下文消散；
每用一个新工具——所有偏好重新教；
每发一篇文章——一样的格式调整重复 N 次；
每排查一次故障——同样的诊断路径走 N 遍。

这不是某个 AI 产品的问题，而是行业默认假设：**AI 是即用即抛的工具，不是越用越聪明的伙伴**。

阿里 AMAP-ML 团队 2026 年 4 月发表的 [SkillClaw](https://github.com/AMAP-ML/SkillClaw) 论文揭示了同一现象——*"Skill 一旦部署就是静态的，每个用户都在重复踩同样的坑"*。他们的解法是构建集体进化的 Skill 库：用 Evolver 持续观察轨迹、提炼模式、回写共享 Skill 库。在 WildClawBench 上 Qwen3-Max 经过 6 轮进化，Creative Synthesis 得分相对提升 88.41%。

这给了我们启发，但也让我们意识到：**集体进化对企业级管线友好，对"个人 24 小时陪伴的 Agent"还差几层抽象**。所以我们启动了 Agent24。

---

## Agent24 是什么

**Agent24 是一组让个人 AI Agent 真正 24 小时在线、自我进化的开源工具集**。它由三部分组成，对应使用门槛由低到高：

| 组件 | 给谁用 | 形态 |
|------|--------|------|
| **Agent24 (Skills)** | Claude Code 订阅用户 | 4 个 SKILL.md + 配置模板，安装到 `~/.claude/skills/` 即可用 |
| **Agent24-Desktop** | 所有人（含非开发者）| 跨平台 Electron 桌面应用，承载完整能力模块生态 |
| **`@auraaihq/*` packages** | 模块开发者 | npm monorepo，提供内核、AI 适配、记忆、进化引擎、能力模块 |

三层设计的目的：让懂 CLI 的人今天就能用最简版本，让普通用户在 Desktop 落地后即开即用，让开发者通过 npm 包参与生态。

---

## 设计理念：四个原则

### 一、**框架与能力解耦**

我们最初考虑过"从某个 Electron Agent 应用 fork 后裁掉特定场景代码"。这是错的。**正确思路是把 Desktop 做成壳，所有能力变成可插拔的模块**：

- 内核（Core）只做演进：Electron 壳、IPC、模块加载、AI 适配层、记忆层
- 能力（Capability Modules）是可装可卸的 npm 包：`@auraaihq/publish-twitter`、`@auraaihq/scrape-rss`、`@auraaihq/module-identity` 等
- 用户从 Desktop UI 安装/卸载模块 ≈ 后台 `pnpm add` / `pnpm remove`

这意味着小红书发布、公众号发布、文件归档、图像处理 ……每一个都是独立 npm 包。框架本身永远精简。

### 二、**框架与 AI 模型解耦**

所有业务模块只调用抽象的 `AI Layer`，不直接依赖任何特定 AI：

```
模块 → AI Layer → [iDoris (本地、隐私优先) | Claude | OpenAI | LLaVA 本地视觉]
```

iDoris 是 AuraAI 自研的"个人全景洞察"AI 模型（Prism 启发，见 [iDoris 仓库](https://github.com/AuraAIHQ/iDoris)），定位是隐私优先的本地推理。但用户也可以路由到 Claude API 或 OpenAI——这是配置项，不是架构约束。

### 三、**隐私优先的默认设置**

借鉴 SkillClaw 的集体进化思路，但**默认关闭轨迹外发**：

- 所有 ATIF 轨迹、memory、archive 默认仅本地存储（加密 SQLite）
- 跨设备同步是显式开启项，用 NIP-44 端到端加密通过 Nostr 中转
- "贡献到社区 SkillBank" 必须用户主动 opt-in，且只发送已蒸馏过的 SKILL.md（不发原始轨迹）

这一条写在 [ADR-017](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md) 里。

### 四、**自我进化是闭环，不是单点**

Agent24 的核心价值在于完成"执行→评估→进化"完整闭环：

1. **执行**：Conversation Layer 接受用户输入 → 任务分解器拆解 → 调度执行（本地/远程模块/其他 agent 协作）
2. **评估**：Phase 3 三阶段评估（Stage 1 correctness gate → Stage 2 全维度 → Stage 3 历史比较）+ 可选外部评估（Codex / agent-speaker / dual）
3. **进化**：
   - **SkillBank** (借鉴 [SkillRL](https://github.com/aiming-lab/SkillRL))：分层 skill 库，每次任务执行前检索相关 skill 注入 context（hot path）
   - **Evolver** (借鉴 [SkillClaw](https://github.com/AMAP-ML/SkillClaw))：周期性守护进程扫 ATIF 轨迹，识别 3+ 次重复 pattern，决定 refine 现有 skill 还是 create 新 skill（cold path）
   - **Validation gate**：Codex MCP 作为校验官，新 skill 通过 review 才合并

这个闭环里，SkillBank 像图书馆（存放检索），Evolver 像编辑部（写新书改旧书）——必须分开，但缺一不可。

---

## 架构概览

```
┌──────────────────────────────────────────────────────────┐
│ 内核 Core（永远存在，不可卸载）                              │
│  Electron Shell · 模块加载器 · IPC · AI Layer 适配器框架    │
│  Memory Layer (L0-L3) · Conversation Layer · 凭据/安全     │
└──────────────────┬───────────────────────────────────────┘
                   │ Module API
   ┌───────────────┼───────────────┬───────────────┐
   ▼               ▼               ▼               ▼
基础模块层       社区模块层       iDoris 能力包装    个人模块层
identity        cos72            input            内容发布
wallet          ├ myshop         process          (publish-*)
comm            ├ mytask         query            信息收集
storage         └ myvote         create           (scrape-*)
shared-memory   communication                     个人助理
ai-bridge       shared-memory                     (files/vision/voice...)
```

**三层模块按"服务对象"分类**（不是按"功能"），对应 Mycelium Protocol 的"个人 / 社区 / 城市"三层服务对象：

- **基础层**：身份（AirAccount）、钱包（SuperPaymaster gasless）、通信（agent-speaker / Nostr）、加密存储——任何人都需要的基础设施
- **社区层**：cos72 包含 myshop（积分兑换）、mytask（任务-积分）、myvote（投票）三个社区核心模块——构成完整经济+治理闭环
- **个人层**：内容发布、信息收集、个人助理、学习创作——子模块最丰富、可扩展性最强

详见 [ADR-003](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md#adr-003模块按服务对象分三层basecommunitypersonal)。

---

## 技术栈

| 层 | 选型 | 理由 |
|---|------|------|
| **桌面壳** | Electron 30 + Vite + React 18 + TypeScript | 跨平台分发成熟、UI 一致性、生态丰富 |
| **本地数据** | better-sqlite3（加密）| 同步 API、零依赖、性能足够 |
| **本地 LLM** | node-llama-cpp + GGUF 模型 | 自动检测硬件 + HF mirror fallback + 按需下载 |
| **跨平台模型存储** | metadata-only npm 包 + 运行时下载 | 不污染 npm（详见 ADR-008）|
| **包管理** | pnpm + workspace + 混合 monorepo | 单 repo 起步、未来易拆分（ADR-007）|
| **跨 Agent 通信** | [agent-speaker](https://github.com/AuraAIHQ/agent-speaker)（基于 Nostr）| 去中心化、NIP-44 加密、无需中心服务器 |
| **身份** | AirAccount + WebAuthn（[AAStar](https://github.com/AAStarCommunity)）| TEE 私钥、生物识别登录、无需助记词 |
| **支付** | SuperPaymaster (ERC-4337) | gasless 微支付、社区积分代付 |
| **未来移动端** | Tauri 2.0（M5+）| 包小、性能优、Rust 后端 + Web 前端复用（ADR-018）|

为了让 M5 顺利切换到 Tauri 2.0（含 mobile），M0-M4 的设计已经在避免 Electron-only API 和 Node 原生依赖的硬绑定。

---

## 路线图（5 个里程碑）

```
M0 (当前)      仓库与 monorepo 骨架 ✅
               18 个 ADR 决策记录 ✅
               npm scope @auraaihq 注册 ✅

M1 (4-6 周)    内核提取（从 xiaoheishu/desktop 借鉴成熟 Electron 架构）
               第一个真实模块：@auraaihq/publish-blog
               模块接口规格 v0.1

M2 (6-8 周)    后台 daemon + tray icon（永远在线）
               任务分解器 + 调度
               iDoris-SDK 合并入 monorepo（@auraaihq/wechat-bridge）
               第二批 publishers (xiaohongshu / wechat-mp / twitter)

M3 (8-10 周)   Memory L0-L3 完整分层
               @auraaihq/skill-bank + @auraaihq/evolver 落地
               Agent24 (Skills) 迁移为 @auraaihq/skills-* npm 包
               Agent24-Desktop rename → Agent24（去掉 Desktop 后缀）

M4 (10-12 周)  跨用户 skill 共享（opt-in）
               Nostr 分发 skill 更新
               iDoris 主 AI 接入

M5+            模块市场 / 跨设备同步 / 三级 agent 网络（个人 ↔ 组织 ↔ 公共）
               Tauri 2.0 mobile 端
```

---

## 跟同类项目的关系

| 项目 | 关系 | Agent24 借鉴的部分 |
|------|------|------|
| [Voyager](https://github.com/MineDojo/Voyager) | 启发 | "ever-growing skill library" 的概念 |
| [DGM](https://github.com/jennyzzt/dgm) | 启发 + 已采用 | results.log archive + 血统追踪 |
| [SkillRL](https://github.com/aiming-lab/SkillRL) | 启发 + 计划采用 | 分层 SkillBank + 自适应检索 |
| [SkillClaw](https://github.com/AMAP-ML/SkillClaw) | 启发 + 计划采用 | Evolver 的 Refine vs Create 决策 + validated publish gate |
| [MemPalace](https://github.com/MezoPotam/MemPalace) | 启发 + 已采用 | L0-L3 分层记忆 + temporal validity |

**Agent24 不重复造轮子的部分**：底层模型（用 Claude / iDoris / Local）、底层协议（用 Nostr / iLink）、原始 Electron 模板（借鉴 xiaoheishu）。

**Agent24 真正在做的事**：把以上全部组合到一个**面向个人用户、可日常 24/7 运行、模块化可扩展、隐私优先**的产品中。

---

## 项目状态与参与方式

**当前阶段**：M0 收尾、M1 启动期。所有架构决策已落定（[18 个 ADR 完整记录](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md)），代码骨架已就绪。

**今天就能用的部分**：[Agent24 Skills](https://github.com/AuraAIHQ/Agent24) — Claude Code 订阅用户安装即用，提供 `/evolve`、`/evaluate`、`/setup`、`/org-sync` 4 个自进化技能。

```bash
# 安装 Agent24 Skills 到 Claude Code
git clone https://github.com/AuraAIHQ/Agent24
cd Agent24 && ./install.sh
# 然后在任意项目里：
claude
> /evolve write a python script to dedupe a CSV
```

**关注后续进展**：
- Agent24-Desktop 仓库：https://github.com/AuraAIHQ/Agent24-Desktop
- AuraAI 组织：https://github.com/AuraAIHQ
- npm scope：[`@auraaihq`](https://www.npmjs.com/settings/auraaihq/packages)

**欢迎参与**：
- 提交 issue 讨论你想要的能力模块
- 在 Agent24 Skills 上提 PR 改进 evolve 流程
- M1 启动后会开放 module 开发模板，欢迎提交第一批第三方 publisher / scraper

---

## 写在最后

我们这一代人见证了 AI 从"问答工具"演化为"工作伙伴"的过程。但绝大多数现有产品仍然是**stateless 的接口**——它们不记得你昨天教过它什么，不会主动观察你的工作模式，不会把今天的失败转化为明天的 skill。

Agent24 的赌注是：**真正属于个人的 AI Agent，必须能自我进化、本地优先、模块化可扩展**。这不是一篇论文一个 demo 就能解决的事——它需要框架、需要生态、需要时间。

我们把所有设计决策、备选方案、踩过的坑都公开记录在 [decision.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md)。无论你是对个人 AI 有想法的开发者，还是希望日常工作真正被 AI 增强的用户——都欢迎一起把它建起来。

> "让 AI 24 小时为你工作、为你思考、为你进化——而你只需要做你最擅长的事。"

— AuraAI Team, 2026-04-28

> 📖 **相关阅读**：[iDoris 立项思考](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/)（Agent24 的底层 AI 模型层）·  [TurboQuant 在 iDoris 上的可行性分析](https://blog.mushroom.cv/blog/turboquant-for-idoris--can-random-rotation-quantization-cut-/)（KV cache 内存压缩）

<!--EN-->

> 📦 **Project**: [Agent24-Desktop](https://github.com/AuraAIHQ/Agent24-Desktop) · [auraai-packages](https://github.com/AuraAIHQ/auraai-packages) · [Agent24 (Skills)](https://github.com/AuraAIHQ/Agent24)
>
> 📐 **Full Design Docs**: [PLAN.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/PLAN.md) · [decision.md (18 ADRs)](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md) · [ROADMAP.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/ROADMAP.md)

---

## A Repeatedly Confirmed Pain Point: AI Doesn't Get Smarter

You use Claude / ChatGPT / various Agent tools every day to write code, publish articles, research, summarize. But no matter how skilled you become — **the AI itself doesn't get to know you better**.

Every new conversation: all context lost.
Every new tool: all preferences re-taught.
Every published article: same formatting tweaks repeated N times.
Every troubleshooting session: same diagnostic path walked N times.

This isn't the fault of any single AI product — it's the industry's default assumption: **AI is a disposable tool, not a partner that grows wiser with use**.

Alibaba's AMAP-ML team's April 2026 [SkillClaw](https://github.com/AMAP-ML/SkillClaw) paper exposed the same phenomenon — *"Skills are static once deployed; every user trips on the same rocks."* Their solution: a collectively-evolving skill repository, where an Evolver continuously observes trajectories, distills patterns, and writes back to the shared skill base. On WildClawBench, Qwen3-Max gained 88.41% relative improvement on Creative Synthesis after 6 rounds.

This inspires us, but also reveals: **collective evolution works for enterprise pipelines — for "personal AI agents that accompany you 24/7" we need a few more layers of abstraction**. So we launched Agent24.

---

## What Agent24 Is

**Agent24 is an open-source toolset that makes personal AI agents truly 24/7 online and self-evolving**. Three components, ordered by usage barrier (low to high):

| Component | For Whom | Form |
|-----------|----------|------|
| **Agent24 (Skills)** | Claude Code subscribers | 4 SKILL.md files + config templates, drop into `~/.claude/skills/` |
| **Agent24-Desktop** | Everyone (incl. non-developers) | Cross-platform Electron desktop app, hosting full capability ecosystem |
| **`@auraaihq/*` packages** | Module developers | npm monorepo: kernel, AI adapters, memory, evolver, capability modules |

The three-tier design lets CLI users start today with the minimal version, lets regular users get a turnkey desktop app, lets developers participate via npm packages.

---

## Design Philosophy: Four Principles

### 1. **Decouple Framework from Capabilities**

We initially considered "fork an existing Electron Agent app and trim domain-specific code". That's wrong. **The right approach is to make Desktop a shell, with all capabilities pluggable modules**:

- The Core only evolves: Electron shell, IPC, module loader, AI adapter layer, memory layer
- Capability Modules are install/uninstall npm packages: `@auraaihq/publish-twitter`, `@auraaihq/scrape-rss`, `@auraaihq/module-identity`, etc.
- Users install/uninstall modules from Desktop UI ≈ background `pnpm add` / `pnpm remove`

This means Xiaohongshu publishing, WeChat publishing, file archiving, image processing... each is an independent npm package. The framework itself stays minimal forever.

### 2. **Decouple Framework from AI Models**

All business modules call only an abstract `AI Layer`, not any specific AI:

```
Module → AI Layer → [iDoris (local, privacy-first) | Claude | OpenAI | LLaVA local vision]
```

iDoris is AuraAI's in-house "personal panoramic insight" AI model (Prism-inspired, see [iDoris repo](https://github.com/AuraAIHQ/iDoris)), positioned as privacy-first local inference. But users can also route to Claude API or OpenAI — that's a config option, not architectural lock-in.

### 3. **Privacy-First Defaults**

Borrows SkillClaw's collective-evolution idea, but **defaults to no trajectory leakage**:

- All ATIF trajectories, memory, archives stored locally (encrypted SQLite) by default
- Cross-device sync is opt-in, NIP-44 end-to-end encrypted via Nostr relay
- "Contribute to community SkillBank" requires explicit user opt-in, sending only distilled SKILL.md (never raw trajectories)

This is codified in [ADR-017](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md).

### 4. **Self-Evolution Is a Loop, Not a Point**

Agent24's core value is the complete "execute → evaluate → evolve" loop:

1. **Execute**: Conversation Layer accepts user input → task decomposer → schedule execution (local / remote modules / inter-agent collaboration)
2. **Evaluate**: Phase 3 three-stage eval (Stage 1 correctness gate → Stage 2 multi-dim → Stage 3 historical comparison) + optional external eval (Codex / agent-speaker / dual)
3. **Evolve**:
   - **SkillBank** (inspired by [SkillRL](https://github.com/aiming-lab/SkillRL)): layered skill library, retrieves relevant skills before each task to inject context (hot path)
   - **Evolver** (inspired by [SkillClaw](https://github.com/AMAP-ML/SkillClaw)): periodic daemon scans ATIF trajectories, identifies 3+ repeating patterns, decides Refine vs Create (cold path)
   - **Validation gate**: Codex MCP as gatekeeper — new skills merge only after review

In this loop, SkillBank is the library (storage + retrieval), Evolver is the editorial team (write new books, edit old ones) — they must be separate, but neither can be missing.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│ Core (always present, never uninstallable)               │
│  Electron Shell · Module Loader · IPC · AI Layer Adapter │
│  Memory Layer (L0-L3) · Conversation Layer · Cred/Sec    │
└──────────────────┬───────────────────────────────────────┘
                   │ Module API
   ┌───────────────┼───────────────┬───────────────┐
   ▼               ▼               ▼               ▼
Base Modules    Community        iDoris Wrappers   Personal Modules
identity        cos72            input             content publishing
wallet          ├ myshop         process           (publish-*)
comm            ├ mytask         query             info collection
storage         └ myvote         create            (scrape-*)
shared-memory   communication                      personal assistant
ai-bridge       shared-memory                      (files/vision/voice...)
```

**Three-layer modules categorized by "service object"** (not by "function"), aligning with Mycelium Protocol's "individual / community / city" three-tier service model:

- **Base layer**: identity (AirAccount), wallet (SuperPaymaster gasless), comm (agent-speaker / Nostr), encrypted storage — infrastructure everyone needs
- **Community layer**: cos72 includes myshop (point exchange), mytask (task-points), myvote (governance) — a complete economy + governance loop
- **Personal layer**: content publishing, info collection, personal assistant, learning/creation — most diverse and extensible sub-modules

See [ADR-003](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md#adr-003模块按服务对象分三层basecommunitypersonal).

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Desktop shell** | Electron 30 + Vite + React 18 + TypeScript | Mature cross-platform distribution, UI consistency, rich ecosystem |
| **Local data** | better-sqlite3 (encrypted) | Sync API, zero deps, sufficient performance |
| **Local LLM** | node-llama-cpp + GGUF models | Auto hardware detection + HF mirror fallback + on-demand download |
| **Cross-platform model storage** | metadata-only npm packages + runtime download | Don't pollute npm (see ADR-008) |
| **Package management** | pnpm + workspace + hybrid monorepo | Single repo first, easy to split later (ADR-007) |
| **Inter-agent comms** | [agent-speaker](https://github.com/AuraAIHQ/agent-speaker) (Nostr-based) | Decentralized, NIP-44 encrypted, no central server |
| **Identity** | AirAccount + WebAuthn ([AAStar](https://github.com/AAStarCommunity)) | TEE private keys, biometric login, no mnemonic |
| **Payments** | SuperPaymaster (ERC-4337) | Gasless micropayments, community points sponsorship |
| **Future mobile** | Tauri 2.0 (M5+) | Smaller bundle, better perf, Rust backend + reusable web frontend (ADR-018) |

To enable smooth migration to Tauri 2.0 (incl. mobile) at M5, the M0-M4 design avoids hard-binding to Electron-only APIs and Node native deps.

---

## Roadmap (5 Milestones)

```
M0 (now)        Repo + monorepo skeleton ✅
                18 ADR decisions logged ✅
                npm scope @auraaihq registered ✅

M1 (4-6 wks)    Core extraction (borrow from xiaoheishu/desktop's mature Electron arch)
                First real module: @auraaihq/publish-blog
                Module interface spec v0.1

M2 (6-8 wks)    Background daemon + tray icon (always online)
                Task decomposer + scheduler
                iDoris-SDK merged into monorepo (@auraaihq/wechat-bridge)
                Second wave of publishers (xiaohongshu / wechat-mp / twitter)

M3 (8-10 wks)   Memory L0-L3 fully layered
                @auraaihq/skill-bank + @auraaihq/evolver landed
                Agent24 (Skills) migrated to @auraaihq/skills-* npm packages
                Agent24-Desktop renamed → Agent24 (drop "Desktop" suffix)

M4 (10-12 wks)  Cross-user skill sharing (opt-in)
                Nostr distribution of skill updates
                iDoris main AI integration

M5+             Module marketplace / cross-device sync / 3-tier agent network (personal ↔ org ↔ public)
                Tauri 2.0 mobile
```

---

## Relation to Similar Projects

| Project | Relation | What Agent24 Borrows |
|---------|----------|----------------------|
| [Voyager](https://github.com/MineDojo/Voyager) | Inspiration | "Ever-growing skill library" concept |
| [DGM](https://github.com/jennyzzt/dgm) | Inspiration + adopted | results.log archive + lineage tracking |
| [SkillRL](https://github.com/aiming-lab/SkillRL) | Inspiration + planned | Layered SkillBank + adaptive retrieval |
| [SkillClaw](https://github.com/AMAP-ML/SkillClaw) | Inspiration + planned | Evolver's Refine vs Create decision + validated publish gate |
| [MemPalace](https://github.com/MezoPotam/MemPalace) | Inspiration + adopted | L0-L3 layered memory + temporal validity |

**What Agent24 doesn't reinvent**: underlying models (Claude / iDoris / Local), underlying protocols (Nostr / iLink), original Electron template (borrows from xiaoheishu).

**What Agent24 actually builds**: combining all the above into a **product targeting individual users, daily 24/7 operable, modular and extensible, privacy-first**.

---

## Project Status & How to Participate

**Current stage**: M0 wrap-up, M1 launch. All architecture decisions finalized ([18 ADRs full record](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md)), code skeleton ready.

**Usable today**: [Agent24 Skills](https://github.com/AuraAIHQ/Agent24) — Claude Code subscribers install and use, providing 4 self-evolving skills: `/evolve`, `/evaluate`, `/setup`, `/org-sync`.

```bash
# Install Agent24 Skills into Claude Code
git clone https://github.com/AuraAIHQ/Agent24
cd Agent24 && ./install.sh
# Then in any project:
claude
> /evolve write a python script to dedupe a CSV
```

**Follow progress**:
- Agent24-Desktop repo: https://github.com/AuraAIHQ/Agent24-Desktop
- AuraAI org: https://github.com/AuraAIHQ
- npm scope: [`@auraaihq`](https://www.npmjs.com/settings/auraaihq/packages)

**Welcome contributions**:
- Open issues to discuss capability modules you want
- Submit PRs to Agent24 Skills to improve the evolve workflow
- After M1 launch, module dev templates open — first wave of third-party publishers / scrapers welcome

---

## Closing

Our generation has witnessed AI evolve from "Q&A tool" into "work partner". But most existing products are still **stateless interfaces** — they don't remember what you taught them yesterday, don't actively observe your work patterns, don't turn today's failure into tomorrow's skill.

Agent24's bet: **a personal AI Agent must be self-evolving, local-first, and modularly extensible**. This isn't solvable by a single paper or demo — it needs framework, ecosystem, time.

We've publicly logged all design decisions, alternatives, and pitfalls in [decision.md](https://github.com/AuraAIHQ/Agent24-Desktop/blob/main/docs/decision.md). Whether you're a developer with ideas about personal AI, or a user wanting your daily work truly augmented by AI — welcome to build this together.

> "Let AI work for you, think for you, evolve for you — 24 hours a day, while you focus on what you do best."

— AuraAI Team, 2026-04-28

> 📖 **Related**: [iDoris Project Launch](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/) (Agent24's underlying AI model layer) · [TurboQuant Feasibility for iDoris](https://blog.mushroom.cv/blog/turboquant-for-idoris--can-random-rotation-quantization-cut-/) (KV cache memory compression)
