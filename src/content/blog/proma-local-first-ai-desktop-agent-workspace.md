---
title: "Proma：把 Chat、Agent、Skills、MCP 和微信桥接做进一个本地优先桌面应用"
titleEn: "Proma: Chat, Agent, Skills, MCP, and WeChat Bridge in One Local-First Desktop App"
description: "ErlichLiu 开源的 Proma 是一个本地优先 AI 桌面工作台：Claude Agent SDK + Pi Agent SDK 双运行时，每个工作区独立配置 Skills 和 MCP，飞书/微信/钉钉桥接让手机触发本机 Agent，AGPL-3.0 开源，1615 Stars。"
descriptionEn: "ErlichLiu's Proma is a local-first AI desktop workspace: dual Claude Agent SDK + Pi Agent SDK runtimes, per-workspace Skills and MCP configuration, and Feishu/WeChat/DingTalk bridges that let your phone trigger on-device agents. AGPL-3.0, 1615 stars."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["本地AI", "桌面应用", "Agent工作台", "Claude SDK", "MCP", "Skills", "微信桥接", "开源", "Electron", "Pi Agent"]
heroImage: "../../assets/images/proma-local-first-ai-desktop-agent-workspace-banner.jpg"
---

> **GitHub**：[ErlichLiu/Proma](https://github.com/ErlichLiu/Proma) · **Stars**：1,615  
> **作者**：ErlichLiu（[erlich.fun](https://erlich.fun)）  
> **商业版**：[proma.cool](https://proma.cool/download)  
> **许可**：AGPL-3.0 · **运行时**：Bun + Electron 39

---

## 一句话定位

Proma 不是又一个 ChatGPT 套壳。它的出发点是：**一个可以长期沉淀个人工作流的 Agent 工作台**。

简单问题用 Chat（快，多模型对比，不留包袱），复杂任务交给 Agent（工作区隔离、Skills 加持、MCP 扩展、结果持久化）。数据默认在 `~/.proma/`，JSON 文件，随时备份，不依赖任何云服务。

有一个细节很有意思：它有 `wechat-bridge.ts`——可以用手机微信触发本机的 Agent 工作流。这和我们做 [Heinu1](https://github.com/jhfnetboy/Heinu1) 的思路高度重合，但做成了完整的桌面 GUI。

---

## 两套 Agent 运行时，按需切换

Proma 在同一个 Agent 输入框下方提供两个内核选择：

### Claude Agent Runtime（默认）

基于 `@anthropic-ai/claude-agent-sdk@0.3.201`，走 Anthropic Messages API。支持 Anthropic 官方接口，也支持 DeepSeek、Kimi API、Kimi Coding Plan、智谱 Coding Plan、MiniMax、小米 MiMo 等 Anthropic 协议兼容端点。

> **Kimi Coding Plan 用户**：Proma 已获 Kimi 官方白名单，接入 Kimi Coding Plan 不触发第三方客户端封号。

### Pi Agent Runtime（实验性）

基于 `@earendil-works/pi-coding-agent@0.80.3`，把 Proma 里已配置的渠道动态注册为 Pi provider。支持的协议范围比 Claude Runtime 更广：

| 渠道类型 | Chat | Claude Agent | Pi Agent |
|---|---|---|---|
| Anthropic / 兼容（DeepSeek、Kimi、智谱 Coding 等） | ✅ | ✅ | ✅ |
| OpenAI、OpenAI Responses、Google、豆包、通义 | ✅ | ✗ | ✅ |
| OpenAI 兼容自定义端点 | ✅ | ✗ | ✅ |
| ChatGPT 订阅（Codex OAuth）| — | ✅ | ✅ |

**实际含义**：想用 Qwen、Gemini、GPT-4o 跑 Agent 任务的，切到 Pi Runtime 即可，不需要等 Anthropic 兼容层。

---

## Chat vs Agent：清晰的模式划分

很多 AI 客户端把聊天和 Agent 混在一起，Proma 的设计是分开的：

**Chat 适合**：日常问答、翻译润色、附件总结、多模型对比输出、一次性对话。

**Agent 适合**：修改/创建/整理本地文件、多步骤调研报告、需要 MCP/Shell/Git 上下文的任务、需要权限确认或后台持续跟进的工作。

规则很直接：**只需要回答时用 Chat，需要行动和交付结果时用 Agent。**

Chat 模式支持：附件解析、图片输入、Markdown / Mermaid / KaTeX / 代码高亮、并排对话（多模型同时回答）、系统提示词、手动管理上下文长度。

Agent 模式支持：工作区文件隔离、Skills 加持、MCP Server 按需启用、长任务流式输出、计划确认（Plan Mode）、子任务拆分与可追踪协作 Agent / Task。

---

## Skills & MCP：工作区级别的能力沉淀

这是 Proma 里最值得单独说的设计：**每个工作区可以独立配置 Skills 和 MCP Server**。

**Skills**：结构化指令文件（`SKILL.md` 格式），沉淀可复用的工作流。README 里的例子是 `feedback-synthesis`——把用户反馈、访谈记录和 issue 聚合成主题、证据和优先级建议。你可以给每个项目配置专属 Skills，而不是每次重复粘贴 prompt。

**MCP Server**：支持 stdio / HTTP MCP Server，可按需启用或关闭。不同工作区绑定不同的 MCP 工具集——代码仓库用代码分析 MCP，写作工作区用搜索 MCP，不同场景不互相干扰。

工作区数据结构：

```
~/.proma/agent-workspaces/{workspace-slug}/
├── workspace-files/   ← 工作区专属文件
├── mcp.json           ← 这个工作区的 MCP 配置
└── skills/            ← 这个工作区的 Skills
```

---

## 远程机器人：手机触发本机 Agent

这个功能对独立开发者特别实用。Proma 支持三种桥接：

- **飞书 / Lark 机器人**：在飞书群聊或私聊里发消息，触发本机 Agent 工作流，结果回复到飞书。
- **钉钉机器人**：同样的模式，接入钉钉群。
- **微信桥接**：`wechat-bridge.ts` 已经实现，让微信侧消息触发本机 Agent。

核心代码在 `apps/electron/src/main/lib/` 下的三个文件：`feishu-bridge.ts`、`dingtalk-bridge.ts`、`wechat-bridge.ts`。

这意味着：你可以在路上用手机发一条微信，让家里的 Mac 跑一个多步骤 Agent 任务，完成后把结果发回来——不需要开电脑。这正是 Heinu1 做的事，但 Proma 做进了完整桌面应用里。

---

## 本地优先的数据设计

```
~/.proma/
├── channels.json           ← API Key 用 Electron safeStorage 加密
├── conversations.json      ← Chat 会话索引
├── conversations/{id}.jsonl← 对话内容（JSONL 追加日志）
├── agent-sessions.json     ← Agent 会话索引
├── agent-sessions/{id}.jsonl
├── agent-workspaces/       ← 工作区数据
│   └── {workspace-slug}/
│       ├── workspace-files/
│       ├── mcp.json
│       └── skills/
├── attachments/
├── user-profile.json
├── settings.json
└── sdk-config/
```

**不使用本地数据库**——所有内容是 JSON 配置文件和 JSONL 追加日志。好处：随时用 `cat` 查看、可以 git 版本控制、迁移到新电脑直接复制目录。

API Key 是唯一加密存储的字段（Electron `safeStorage`），其余数据全部明文可读。

---

## 语音输入

Proma 内置豆包流式语音识别：

- `Ctrl + `` 触发识别
- 再次按下结束，自动输入到 Proma 的当前输入框
- 在 Proma 外部使用：识别结果输入到当前光标位置，无光标则写入剪贴板

这让它在某些场景下可以无键盘操作——说出任务，Agent 执行，说出反馈，继续推进。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 运行时 | Bun（monorepo 工具链）|
| 桌面框架 | Electron 39 |
| 前端 | React 18 + TypeScript + Jotai |
| 样式 | Tailwind CSS + Radix UI |
| 富文本输入 | TipTap |
| Markdown / 图表 / 公式 | React Markdown + Beautiful Mermaid + KaTeX |
| 代码高亮 | Shiki |
| 构建 | Vite + esbuild |
| 分发 | electron-builder |
| Agent Runtime | Claude SDK 0.3.201 + Pi 0.80.3 |

仓库结构是 Bun workspace monorepo：`packages/shared`（共享类型 + IPC 常量）、`packages/core`（Provider Adapter + SSE + 代码高亮）、`packages/ui`（共享 React 组件）、`apps/electron`（Electron 主应用）。

```bash
# 开发
bun install
bun run dev       # Vite + Electron + 热重载

# 构建
bun run electron:build

# 类型检查
bun run typecheck
```

---

## 架构核心：Agent Orchestrator

Agent 的调度入口在 `agent-orchestrator.ts`：接收任务、选择运行时（Claude 还是 Pi）、设置工作区环境变量、调用对应 SDK、管理事件流和错误。

两套适配器：
- `adapters/claude-agent-adapter.ts`：Claude SDK 封装，含工作区文件注入、Skills 加载、MCP 启动
- `adapters/pi-agent-adapter.ts`：Pi SDK 封装，把已启用渠道动态注册为 provider
- `adapters/runtime-routing-agent-adapter.ts`：根据会话内核路由到对应适配器

渲染进程 Agent IPC 监听器**在应用顶层全局挂载**——这是一个重要工程决策：避免切换页面时丢失流式事件、权限请求或后台任务状态。

---

## 开源版 vs 商业版

| | **开源版（AGPL-3.0）**| **商业版（proma.cool）** |
|---|---|---|
| 下载 | GitHub Releases | proma.cool/download |
| 模型渠道 | 需自备 API Key | 内置渠道 + 订阅方案 |
| 功能 | 完整 | 完整 + 内置渠道 |
| 限制 | 修改后分发或 SaaS 需开放源码 | 商业授权豁免 AGPL |

开源版在功能上完整，适合自备 API Key 的用户。商业版的差异主要是省去了配置渠道的步骤。

AGPL-3.0 意味着：如果你把 Proma 改了，对外提供 SaaS 服务，必须开放修改后的完整源码——包括网络交互层。想集成到闭源产品，需要单独商业授权。

---

## 与同类工具对比

| | **Proma** | **Cherry Studio** | **Open WebUI** | **Cursor** |
|---|---|---|---|---|
| 定位 | Agent 工作台 + 多协议 | 多模型 Chat 客户端 | 本地模型 UI | AI 代码编辑器 |
| Agent 运行时 | Claude SDK + Pi SDK | ✗ | 基础 | 内置 |
| Skills & MCP | ✅ 工作区级别 | ✗ | 基础 | 插件 |
| 远程机器人 | ✅ 微信/飞书/钉钉 | ✗ | ✗ | ✗ |
| 本地数据 | ✅ 全 JSON/JSONL | 部分 | 部分 | 部分 |
| 语音输入 | ✅ 豆包流式 | ✗ | 部分 | ✗ |
| 开源许可 | AGPL-3.0 | Apache-2.0 | Apache-2.0 | 闭源 |

Proma 最独特的组合是：**完整 Agent 运行时 + 工作区 Skills + 远程机器人桥接**。这三样加在一起，在开源桌面 AI 客户端里目前没有直接竞品。

---

## 核心判断

Proma 解决的是一个真实存在的场景空白：你想在本地用 Claude/Pi 做真正的 Agent 工作（不只是聊天），但不想每次都开终端、配置 SDK、手动管理工作区。

1615 Stars，开源 6 个月。两套 Agent 运行时 + 工作区 Skills + 微信/飞书桥接，这个功能组合在桌面 AI 客户端里确实少见。

如果你现在在用 Heinu1 这类"手机触发 Claude 工作"的方案，Proma 的 wechat-bridge + Agent Workspace 值得参考——尤其是它把 Skills 做到工作区级别、MCP 按工作区启用关闭这两个设计，是可以直接借鉴的架构思路。

---

## 参考资源

- **GitHub**：[ErlichLiu/Proma](https://github.com/ErlichLiu/Proma)
- **新手教程**：[tutorial/tutorial.md](https://github.com/ErlichLiu/Proma/blob/main/tutorial/tutorial.md)
- **作者博客**：[erlich.fun](https://erlich.fun)
- **商业版**：[proma.cool](https://proma.cool)
- **Pi Agent SDK**：earendil-works/pi-coding-agent

© 2026 Author: Mycelium Protocol

<!--EN-->

> **GitHub**: [ErlichLiu/Proma](https://github.com/ErlichLiu/Proma) · **Stars**: 1,615  
> **Author**: ErlichLiu ([erlich.fun](https://erlich.fun))  
> **Commercial**: [proma.cool](https://proma.cool/download)  
> **License**: AGPL-3.0 · **Runtime**: Bun + Electron 39

---

## One-Line Positioning

Proma is not yet another ChatGPT wrapper. Its starting point is: **an Agent workspace for long-term accumulation of personal workflows**.

Simple questions go to Chat (fast, multi-model comparison, no overhead); complex tasks go to Agent (workspace isolation, Skills support, MCP extensions, persistent results). Data lives in `~/.proma/` by default — JSON files, backed up any time, with no dependency on any cloud service.

One detail stands out: it has a `wechat-bridge.ts` — you can trigger on-device Agent workflows from your phone via WeChat. This closely mirrors the thinking behind [Heinu1](https://github.com/jhfnetboy/Heinu1), but realized as a full desktop GUI.

---

## Two Agent Runtimes, Switch on Demand

Proma offers two kernel choices beneath the same Agent input box:

### Claude Agent Runtime (Default)

Based on `@anthropic-ai/claude-agent-sdk@0.3.201`, routed through the Anthropic Messages API. Supports the official Anthropic endpoint as well as Anthropic-protocol-compatible endpoints: DeepSeek, Kimi API, Kimi Coding Plan, Zhipu Coding Plan, MiniMax, Xiaomi MiMo, and more.

> **Kimi Coding Plan users**: Proma is on Kimi's official whitelist, so connecting via Kimi Coding Plan will not trigger a third-party client ban.

### Pi Agent Runtime (Experimental)

Based on `@earendil-works/pi-coding-agent@0.80.3`, dynamically registering the channels already configured in Proma as Pi providers. Its protocol coverage is broader than the Claude Runtime:

| Channel Type | Chat | Claude Agent | Pi Agent |
|---|---|---|---|
| Anthropic / compatible (DeepSeek, Kimi, Zhipu Coding, etc.) | ✅ | ✅ | ✅ |
| OpenAI, OpenAI Responses, Google, Doubao, Qwen | ✅ | ✗ | ✅ |
| OpenAI-compatible custom endpoints | ✅ | ✗ | ✅ |
| ChatGPT subscription (Codex OAuth) | — | ✅ | ✅ |

**Practical implication**: if you want to run Agent tasks with Qwen, Gemini, or GPT-4o, just switch to Pi Runtime — no need to wait for an Anthropic-compatible layer.

---

## Chat vs Agent: Clear Mode Separation

Many AI clients blur the line between chat and agent. Proma's design keeps them distinct:

**Chat is for**: everyday Q&A, translation and polishing, attachment summarization, multi-model comparison output, one-off conversations.

**Agent is for**: modifying/creating/organizing local files, multi-step research reports, tasks that require MCP/Shell/Git context, work that needs permission confirmations or background follow-up.

The rule is straightforward: **use Chat when you only need an answer; use Agent when you need action and a deliverable result.**

Chat mode supports: attachment parsing, image input, Markdown / Mermaid / KaTeX / code highlighting, side-by-side conversations (multiple models answering simultaneously), system prompts, and manual context-length management.

Agent mode supports: workspace file isolation, Skills augmentation, on-demand MCP Server enabling, long-task streaming output, Plan Mode for confirmation, and subtask decomposition with trackable collaborative Agents / Tasks.

---

## Skills & MCP: Workspace-Level Capability Accumulation

This is the design in Proma most worth singling out: **each workspace can independently configure its own Skills and MCP Servers**.

**Skills**: structured instruction files in `SKILL.md` format that accumulate reusable workflows. The README example is `feedback-synthesis` — aggregating user feedback, interview notes, and issues into themes, evidence, and prioritization suggestions. You can configure dedicated Skills per project instead of pasting the same prompt every time.

**MCP Server**: supports stdio / HTTP MCP Servers, enabled or disabled on demand. Different workspaces bind to different MCP toolsets — a code repository uses a code-analysis MCP, a writing workspace uses a search MCP, without cross-contamination between contexts.

Workspace data structure:

```
~/.proma/agent-workspaces/{workspace-slug}/
├── workspace-files/   ← workspace-specific files
├── mcp.json           ← MCP config for this workspace
└── skills/            ← Skills for this workspace
```

---

## Remote Bot: Trigger On-Device Agent from Your Phone

This feature is especially practical for indie developers. Proma supports three bridge types:

- **Feishu / Lark bot**: send a message in a Feishu group chat or DM to trigger on-device Agent workflows; results reply back to Feishu.
- **DingTalk bot**: same pattern, connected to DingTalk groups.
- **WeChat bridge**: `wechat-bridge.ts` is already implemented, letting WeChat-side messages trigger on-device Agents.

The core code lives in three files under `apps/electron/src/main/lib/`: `feishu-bridge.ts`, `dingtalk-bridge.ts`, `wechat-bridge.ts`.

This means: you can send a WeChat message from your phone while out and about, have your Mac at home run a multi-step Agent task, and receive the results when it's done — without opening your laptop. This is exactly what Heinu1 does, but Proma delivers it inside a full desktop application.

---

## Local-First Data Design

```
~/.proma/
├── channels.json           ← API Keys encrypted with Electron safeStorage
├── conversations.json      ← Chat session index
├── conversations/{id}.jsonl← Conversation content (JSONL append log)
├── agent-sessions.json     ← Agent session index
├── agent-sessions/{id}.jsonl
├── agent-workspaces/       ← Workspace data
│   └── {workspace-slug}/
│       ├── workspace-files/
│       ├── mcp.json
│       └── skills/
├── attachments/
├── user-profile.json
├── settings.json
└── sdk-config/
```

**No local database** — all content is JSON config files and JSONL append logs. Benefits: inspect with `cat` any time, version-control with git, migrate to a new machine by copying the directory.

API Keys are the only encrypted field (Electron `safeStorage`); all other data is stored in plaintext.

---

## Voice Input

Proma includes Doubao streaming speech recognition built-in:

- `Ctrl + `` triggers recognition
- Press again to stop; input is automatically placed in Proma's current input field
- When used outside Proma: recognition result is typed at the current cursor position, or written to the clipboard if there is no cursor

This enables keyboard-free operation in some scenarios — speak the task, Agent executes, speak the feedback, continue moving forward.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Bun (monorepo toolchain) |
| Desktop framework | Electron 39 |
| Frontend | React 18 + TypeScript + Jotai |
| Styling | Tailwind CSS + Radix UI |
| Rich-text input | TipTap |
| Markdown / Charts / Formulas | React Markdown + Beautiful Mermaid + KaTeX |
| Code highlighting | Shiki |
| Build | Vite + esbuild |
| Distribution | electron-builder |
| Agent Runtime | Claude SDK 0.3.201 + Pi 0.80.3 |

The repository is structured as a Bun workspace monorepo: `packages/shared` (shared types + IPC constants), `packages/core` (Provider Adapter + SSE + code highlighting), `packages/ui` (shared React components), `apps/electron` (Electron main application).

```bash
# Development
bun install
bun run dev       # Vite + Electron + hot reload

# Build
bun run electron:build

# Type check
bun run typecheck
```

---

## Architecture Core: Agent Orchestrator

The Agent scheduling entry point is `agent-orchestrator.ts`: receives tasks, selects the runtime (Claude or Pi), sets workspace environment variables, invokes the corresponding SDK, and manages the event stream and errors.

Two adapters:
- `adapters/claude-agent-adapter.ts`: Claude SDK wrapper, including workspace file injection, Skills loading, MCP startup
- `adapters/pi-agent-adapter.ts`: Pi SDK wrapper, dynamically registering enabled channels as providers
- `adapters/runtime-routing-agent-adapter.ts`: routes to the appropriate adapter based on the session's kernel

The renderer-process Agent IPC listener is **mounted globally at the application's top level** — this is an important engineering decision: it prevents losing streaming events, permission requests, or background task state when navigating between pages.

---

## Open-Source vs Commercial

| | **Open-Source (AGPL-3.0)** | **Commercial (proma.cool)** |
|---|---|---|
| Download | GitHub Releases | proma.cool/download |
| Model channels | Bring your own API Key | Built-in channels + subscription plans |
| Features | Full | Full + built-in channels |
| Restrictions | Modifications distributed or served as SaaS must open-source the code | Commercial license exempts from AGPL |

The open-source edition is feature-complete and suited for users who supply their own API Keys. The commercial edition's main difference is that channel configuration is handled for you.

AGPL-3.0 means: if you modify Proma and offer it as a SaaS service, you must release the full modified source code — including the network interaction layer. Integrating into a closed-source product requires a separate commercial license.

---

## Comparison with Similar Tools

| | **Proma** | **Cherry Studio** | **Open WebUI** | **Cursor** |
|---|---|---|---|---|
| Positioning | Agent workspace + multi-protocol | Multi-model Chat client | Local model UI | AI code editor |
| Agent runtime | Claude SDK + Pi SDK | ✗ | Basic | Built-in |
| Skills & MCP | ✅ Workspace-level | ✗ | Basic | Plugin |
| Remote bot | ✅ WeChat/Feishu/DingTalk | ✗ | ✗ | ✗ |
| Local data | ✅ Full JSON/JSONL | Partial | Partial | Partial |
| Voice input | ✅ Doubao streaming | ✗ | Partial | ✗ |
| Open-source license | AGPL-3.0 | Apache-2.0 | Apache-2.0 | Closed-source |

Proma's most distinctive combination is: **full Agent runtime + workspace Skills + remote bot bridges**. Taken together, these three have no direct competitor among open-source desktop AI clients at present.

---

## Core Assessment

Proma addresses a real gap: you want to do genuine Agent work locally with Claude/Pi (not just chat), but you don't want to open a terminal, configure the SDK, and manage workspaces by hand every time.

1,615 Stars, open-sourced for 6 months. Two Agent runtimes + workspace Skills + WeChat/Feishu bridges — this feature combination is genuinely rare among desktop AI clients.

If you're currently using a setup like Heinu1 for "phone-triggered Claude work," Proma's wechat-bridge + Agent Workspace is worth studying — especially the designs of workspace-level Skills and per-workspace MCP enable/disable. These are architectural ideas you can borrow directly.

---

## References

- **GitHub**: [ErlichLiu/Proma](https://github.com/ErlichLiu/Proma)
- **Beginner tutorial**: [tutorial/tutorial.md](https://github.com/ErlichLiu/Proma/blob/main/tutorial/tutorial.md)
- **Author's blog**: [erlich.fun](https://erlich.fun)
- **Commercial edition**: [proma.cool](https://proma.cool)
- **Pi Agent SDK**: earendil-works/pi-coding-agent

© 2026 Author: Mycelium Protocol
