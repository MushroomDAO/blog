---
title: "DeepSeek Harness 深度拆解：一切皆插件的 Agent 运行时，和 Claude Code / Codex 最本质的区别在哪"
titleEn: "deepseek-harness-everything-plugin-cordis-compare-claude-code-codex"
description: "DeepSeek AI 开源 deepseek-harness（dsh），MIT 许可，4.2 万行 TypeScript，核心设计哲学「一切皆插件」。底层使用 Cordis 框架，每个功能单元都是可替换的 Cordis 插件——模型适配器、工具注册、会话日志、Agent Loop 本身全部可以插拔。对比 Claude Code（只接 Anthropic 模型，无插件系统）、Codex CLI（功能固定）：dsh 卖的是一个可组装的「AI 运行时菜市场」，而不是单一产品。Web UI、session fork/resume、定时任务、Skill 生态、沙箱隔离都已内置。"
descriptionEn: "DeepSeek AI open-sources deepseek-harness (dsh), MIT-licensed, 42,000 lines of TypeScript. Core design: everything is a plugin. Powered by the Cordis framework, every component is a swappable plugin — model adapter, tool registry, session log, the agent loop itself. Compared to Claude Code (Anthropic model lock, no plugin system) and Codex CLI (fixed functionality): dsh sells a composable 'AI runtime marketplace', not a single product. Web UI, session fork/resume, scheduled jobs, Skill ecosystem, and sandbox isolation are all built-in."
pubDate: "2026-08-14"
updatedDate: "2026-08-14"
category: "Tech-News"
tags: ["DeepSeek", "Agent Harness", "插件系统", "Cordis", "Claude Code", "Codex", "开源", "TypeScript"]
heroImage: "../../assets/images/deepseek-harness-everything-plugin-cordis-compare-claude-code-codex-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/deepseek-ai/deepseek-harness  
许可证：MIT  
语言：TypeScript  
状态：Developer Preview（迭代中，有 Breaking Change 风险）  
运行：`npx @deepseek-ai/dsh web`  
Discord：https://discord.gg/Ycq5dCaS4

---

`deepseek-harness`（简称 dsh）是 DeepSeek AI 开源的 Agent 运行时。它的核心设计用四个字概括：**一切皆插件**。

这四个字说起来容易，但真正按这个思路实现，意味着什么？本文深入拆解 dsh 的架构，并和 Claude Code、Codex CLI、Pipecat 做具体对比。

---

## 一、「一切皆插件」意味着什么

dsh 底层使用 [Cordis](https://github.com/cordiverse/cordis) 框架。Cordis 的核心是一个带有「时空可组合性」的插件系统——每个插件向 Context 贡献服务、事件和可逆副作用（Revertible Effects），卸载插件时这些副作用全部自动回滚。

这带来一个根本性的区别：**dsh 没有特权核心**。

在大多数 Agent 框架里，模型调用、工具执行、日志系统、Agent Loop 是被硬编码的核心逻辑，用户只能在它们的边界之外扩展。dsh 不是这样——这几件事本身都是 Cordis 插件，和其他插件平等并存：

| 功能 | 实现方式 | 可替换？ |
|------|---------|---------|
| 模型适配器（LLM 调用） | `llm/llm` 插件，注册 `ctx.llm` | ✅ 替换就能换模型厂商 |
| 工具注册与执行 | `core/tools` 插件，注册 `ctx.tools` | ✅ 可以插入自定义工具管道 |
| 会话日志（Session Log） | `core/session` 插件，注册 `ctx.sessions` | ✅ 日志存储后端可换 |
| Agent Loop | `core/agent-loop` 插件 | ✅ 整个 Loop 逻辑可以被替换 |
| Sandbox | `ctx.sandbox` backend | ✅ 替换就能换执行环境 |
| 沙箱里的 Shell/文件系统 | `ctx.shell` / `ctx.fs` backend | ✅ 一次替换带动整个执行链 |

换沙箱 backend 不只是换了「运行进程的环境」——因为 Shell 和文件系统 provider 共享一个执行世界，指向远程 sandbox 之后，Bash、PTY、LSP 全部跟着迁移，不需要各自改代码。

---

## 二、核心架构：Profile → Bundle → Patch

一个 dsh 进程启动时，从这个结构组装插件树：

```
Profile（named composition）
  ↓ 包含多个 Bundle
  ├── dsh-base （模型适配器、工具、持久化、沙箱、审批策略）
  ├── dsh-web-app （Web UI 服务）或 dsh-headless （单次无服务器运行）
  └── 用户自己安装的 Bundle
  ↓ 覆盖层
  ├── profile 的 cordis.patch.yml
  ├── home 级的 cordis.patch.yml
  └── --patch 命令行覆盖
```

每一层 Patch 都针对 Row ID 修改配置或插入新 Row，不需要 fork 代码。你可以在不改 dsh-base 代码的情况下，把模型替换成任意支持的 LLM adapter，或者把沙箱换成 E2B。

---

## 三、Turn Flow：Agent 执行的完整时序

dsh 对 Agent 一次 Turn 的执行时序有精确定义，方便插件介入任意位置：

```
turn/start
  ├─ 声明 next-step 输入，组装 Prompt sections + tool schemas
  ├─ agent/pre-step （拦截点：可以 reject 或改写消息）
  │    └─ rejected / empty → turn 关闭，不发生 LLM 请求
  ├─ step/start
  │    ├─ 派生 model history from session log
  │    ├─ agent/request → llm/stream → assistant/chunk* → assistant/message
  │    └─ tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
  └─ step/end
       └─ 如果 tool 欠另一次请求或有新输入 → 继续下一 step
agent/turn-stopping
turn/end
```

`agent/pre-step`、`agent/request`、`llm/stream`、`tools/pre-execute/execute/post-execute` 都是 waterfall 事件，监听器必须调用 `next()` 才放行。这意味着插件可以在 LLM 请求之前修改 Prompt，在工具执行前做权限检查，在工具执行后注入上下文——全部通过注册事件监听器实现，不需要 fork 核心代码。

---

## 四、Session：fork、resume、持久化

session 是 dsh 的基础 primitive，每个 session 对应一条追加式（append-only）的 `SessionEvent` 日志。

**关键特性**：
- **fork**：`ctx.sessions.fork(source, boundary?, childSessionId?)` ——从任意历史位置 fork 出新 session，两个 session 各自独立演化。可以理解为 git branch，但是 Agent 会话。
- **resume**：`ctx.agents.resume(options)` ——加载持久化 session，mint 新的 agent scope，从中断处继续。
- **replay**：session log 是 model-visible history 的单一来源（`deriveMessages()` 从它投影），transcript、telemetry、UI 渲染全部派生自同一条 log。这保证了一致性：「model-visible means logged」是运行时不变式，新的 model-visible 输入必须先成为 SessionEvent。

---

## 五、核心包清单（40+ 个）

packages 目录下 40+ 个包，每个都是独立 Cordis 插件：

```
acp           ACP 协议（subagent 跨进程通信）
api           API 服务层
attachment    附件处理
boot          启动/app-boot
bundle        dsh-base / dsh-web-app / dsh-headless
client        客户端连接
code-runtime  代码执行 runtime
compaction    会话压缩（超长会话处理）
context       Context 类型定义
core          session / system-prompt / tools / agent / agent-loop / scope
credentials   凭据管理
e2b           E2B sandbox backend
extensions    扩展插件
feedback      反馈收集
fs            文件系统 provider
goal          目标管理
guard         安全守卫
hooks         生命周期钩子
host          宿主能力
identity      身份/用户管理
interaction   人机交互
jobs          后台任务调度
llm           LLM 流式适配器
lsp           LSP（语言服务器）集成
mcp           MCP 工具集成
plan          计划管理
preset        Agent 预设
runtime-diagnostics 运行时诊断
sandbox       沙箱后端抽象
schedule      定时任务
sdk           对外 SDK
session-query 会话查询
session       会话存储/事件
settings      设置管理
shell         Shell 执行 provider
skill         Skill 系统
spill         溢出/overload 处理
storage       持久化存储
subagent      子 Agent 调度
subprocess    子进程管理
terminal      终端 provider
test-support  测试工具
todo          TODO 管理
typert        类型报告
util          工具函数
web           Web UI / 服务器
workflow      工作流
workspace     工作区管理
```

---

## 六、对比：dsh vs Claude Code vs Codex CLI

这三个工具虽然都在 Coding Agent 这个大赛道，但设计哲学差异极大：

| 特性 | deepseek-harness (dsh) | Claude Code | OpenAI Codex CLI |
|------|------------------------|-------------|-----------------|
| **模型锁定** | 无。模型适配器是插件，可以接任意 LLM | Anthropic 模型（Claude 系列） | OpenAI 模型为主 |
| **插件系统** | 核心设计，一切皆插件（Cordis） | 无 | 无 |
| **Agent Loop** | 可替换的插件 | 内置，不可替换 | 内置，不可替换 |
| **Web UI** | 内置（`npx @deepseek-ai/dsh web`） | 无 | 无 |
| **Session fork/resume** | 内置，`ctx.sessions.fork()` | 有 resume 但无 fork | 无 |
| **Sandbox** | 可插拔 backend（支持 E2B） | 内置沙箱（Docker-like） | 内置沙箱 |
| **Skill 系统** | 内置（`packages/skill`） | 无原生 Skill | 无 |
| **定时任务** | 内置（`packages/schedule` / `ctx.jobs`） | 无 | 无 |
| **MCP 集成** | 内置（`packages/mcp`） | 外部 MCP server | 外部 MCP server |
| **subagent 支持** | 内置（ACP 协议，`packages/subagent`） | 有（Agent SDK） | 有限 |
| **生命周期** | 插件粒度，热替换 | 进程粒度 | 进程粒度 |
| **许可证** | MIT | 闭源 CLI | 闭源 CLI |
| **代码量** | ~42,000 行 TypeScript | 未知（闭源） | 未知（闭源） |

**核心差异用一句话**：
- Claude Code 是**专用工具**，深度绑定 Anthropic 模型，交互体验打磨成熟
- Codex CLI 是**接口工具**，把 OpenAI 的工具调用能力暴露成 CLI
- dsh 是**元框架**，自己的功能是通过插件实现的，用户可以改造任何部分

用原文引用：「CC 卖菜，dsh 卖菜市场。」

---

## 七、插件生态：dsh-plugin

dsh 要求社区插件仓库在 `package.json` 里打上 `dsh-plugin` topic，就能被发现。已有的插件生态包括：

- `dsh-vision-toolkit` / `modlens`：视觉能力（OCR、UI 还原）
- `dsh-web-ui` 主题和皮肤
- `dsh-mem`：跨会话长期记忆（JSON file memory store）
- `agent-teams`：多 Agent 协作
- `oh-dsh`：社区发行版（TUI + 桌面 + Web UI 三形态）
- awesome-deepseek-harness：生态汇总

开发一个新 dsh 插件的核心工作：实现一个 Cordis 插件，注册 service、tool 或 event listener，然后发布 npm，打 `dsh-plugin` topic。

---

## 八、快速上手

```bash
# 方式一：无需安装，直接运行 Web UI
npx @deepseek-ai/dsh web
# → 在 http://127.0.0.1:3080 打开 Web UI

# 方式二：从源码运行
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install && pnpm run build && pnpm dsh web

# 查看实际加载的配置树
dsh --profile web --dump-config
```

---

## 九、使用 dsh 需要注意的现实问题

**Developer Preview 警告**：README 明确标注「THERE WILL BE COMPATIBILITY-BREAKING CHANGES」，不适合今天就在生产环境大量依赖。插件 API 仍在快速变化。

**学习曲线**：Cordis 是一个有独特概念（Service、Context、Revertible Effects、Coeffects）的框架，需要先读 Cordis primer 才能有效开发插件。

**模型支持**：dsh 本身是模型中立的，但是否好用取决于你接的模型。官方文档主要以 DeepSeek 模型为示例。

**插件生态仍在早期**：虽然已经有一批社区插件，但和 Claude Code 的工具生态比，质量和覆盖度仍在积累阶段。

---

## 十、值得关注的理由

**如果你是 AI 工程师**：dsh 是目前最彻底的开源 Agent Harness 架构实现。研究它的插件系统和 Turn Flow 设计，对理解 Agent 框架的工程边界有直接价值。

**如果你是企业用户**：dsh 允许你接自己的模型（包括私有部署的 DeepSeek 或其他兼容 API），不依赖单一厂商，整个 Harness 在你控制之下。

**如果你是工具开发者**：插件系统意味着你的工具可以以标准方式集成，而不是为每个 Agent 框架单独适配。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## DeepSeek Harness Deep Dive: An Everything-Is-a-Plugin Agent Runtime, and What Makes It Fundamentally Different from Claude Code and Codex

*by Mycelium Protocol*

---

GitHub: https://github.com/deepseek-ai/deepseek-harness  
License: MIT  
Language: TypeScript  
Status: Developer Preview (breaking changes expected)  
Run: `npx @deepseek-ai/dsh web`

---

`deepseek-harness` (dsh) is DeepSeek AI's open-source Agent runtime. Its core design philosophy in four words: **everything is a plugin.**

Those four words are easy to say. But what does it actually mean to build that way?

---

### "Everything Is a Plugin" — What It Actually Means

dsh is powered by [Cordis](https://github.com/cordiverse/cordis), a meta-framework built around spatiotemporal composability. Every plugin contributes services, typed events, and revertible effects to a shared context; when a plugin unloads, those effects unwind automatically.

The consequence: **dsh has no privileged core.** The model adapter, tool registry, session log, and the agent loop itself are all Cordis plugins — equal to each other and to any third-party plugin you write:

| Component | Plugin | Swappable? |
|-----------|--------|-----------|
| LLM calls | `llm/llm` → `ctx.llm` | ✅ swap = change model vendor |
| Tool registry | `core/tools` → `ctx.tools` | ✅ insert custom tool pipeline |
| Session log | `core/session` → `ctx.sessions` | ✅ swap storage backend |
| Agent Loop | `core/agent-loop` | ✅ the whole loop is replaceable |
| Sandbox | `ctx.sandbox` backend | ✅ swap = change execution environment |
| Shell + filesystem | `ctx.shell` / `ctx.fs` backend | ✅ one swap moves Bash, PTY, LSP together |

Swapping the sandbox backend doesn't just change where processes run — because Shell and filesystem providers share one execution world, pointing them at a remote sandbox migrates Bash, PTY, and LSP simultaneously. No code changes to each provider.

---

### Architecture: Profile → Bundle → Patch

A running dsh instance assembles its plugin tree from layers:

```
Profile (named composition)
  ↓ composed of Bundles
  ├── dsh-base (model adapters, tools, persistence, sandbox, approval policy)
  ├── dsh-web-app (browser application) or dsh-headless (single-shot, no server)
  └── user-installed bundles
  ↓ patch layers
  ├── profile-level cordis.patch.yml
  ├── home-level cordis.patch.yml
  └── --patch CLI overlay
```

Each patch targets a Row by ID and replaces its full config or inserts new rows — without touching dsh-base source. You can swap the model to any LLM adapter, or replace the sandbox with E2B, purely through configuration.

---

### Turn Flow: Precise Agent Execution Timing

dsh defines exact timing for each agent turn, with interception points for plugins:

```
turn/start
  ├─ claim input, assemble prompt sections + tool schemas
  ├─ agent/pre-step  ← INTERCEPT: reject or rewrite messages here
  │    └─ rejected/empty → turn closes with no LLM request
  ├─ step/start
  │    ├─ derive model history from session log
  │    ├─ agent/request → llm/stream → assistant/message
  │    └─ tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
  └─ step/end
       └─ more tool requests or new input → next step
agent/turn-stopping
turn/end
```

`agent/pre-step`, `agent/request`, `llm/stream`, and the three `tools/*` events are waterfalls — listeners must call `next()` to pass through. Plugins can: modify the prompt before the LLM sees it, permission-check tools before execution, inject context after tools return — all through event listeners, zero core code changes.

---

### Session: Fork, Resume, Durable Log

Every session is an append-only `SessionEvent` log. Key capabilities:

- **Fork**: `ctx.sessions.fork(source, boundary?, childSessionId?)` — branch a session at any historical point, like `git branch` for agent conversations
- **Resume**: `ctx.agents.resume(options)` — load persisted session, continue from where it stopped
- **Single source of truth**: `deriveMessages()` projects model history from the log; transcripts, telemetry, and UI all derive from the same log. "Model-visible means logged" is a runtime invariant.

---

### Comparison: dsh vs Claude Code vs Codex CLI

| Feature | deepseek-harness (dsh) | Claude Code | OpenAI Codex CLI |
|---------|------------------------|-------------|-----------------|
| **Model lock** | None — model adapter is a plugin | Anthropic models only | OpenAI models primary |
| **Plugin system** | Core design, everything is a plugin | None | None |
| **Agent Loop** | Swappable plugin | Built-in, not replaceable | Built-in, not replaceable |
| **Web UI** | Built-in | None | None |
| **Session fork** | Built-in `ctx.sessions.fork()` | No | No |
| **Sandbox** | Pluggable backend (supports E2B) | Built-in | Built-in |
| **Skill system** | Built-in (`packages/skill`) | None | None |
| **Scheduled jobs** | Built-in (`packages/schedule`) | None | None |
| **MCP** | Built-in (`packages/mcp`) | External | External |
| **Sub-agents** | Built-in (ACP protocol) | Agent SDK | Limited |
| **License** | MIT | Closed-source CLI | Closed-source CLI |

The difference in one line:
- **Claude Code** is a polished, opinionated tool deeply integrated with Anthropic's model stack
- **Codex CLI** is an interface tool that exposes OpenAI's function calling as a CLI
- **dsh** is a meta-framework — even its own features are implemented as plugins, and any part can be replaced

"Claude Code sells groceries. dsh sells the grocery market."

---

### Why It Matters

**For AI engineers**: dsh is the most architecturally complete open-source Agent Harness available. Its plugin system and Turn Flow design are worth studying to understand the engineering boundaries of Agent frameworks.

**For enterprises**: dsh lets you connect your own model (including private-hosted models or any OpenAI-compatible API), own the entire harness, and avoid vendor lock-in.

**For tool developers**: the plugin system means your tool integrates in a standard way, rather than adapting it separately for each Agent framework.

**Caveat**: Developer Preview. Breaking changes will happen. Not production-ready for heavy reliance today.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
