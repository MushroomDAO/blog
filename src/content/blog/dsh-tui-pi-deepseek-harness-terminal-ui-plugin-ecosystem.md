---
title: "dsh-tui-pi：DeepSeek Harness 的社区 TUI 生态，把编码 Agent 终端做成了 pi 风格"
titleEn: "dsh-tui-pi: The Community TUI Ecosystem for DeepSeek Harness — A Pi-Style Terminal for Your Coding Agent"
description: "DeepSeek Harness (dsh) 是 DeepSeek 的编码 Agent 运行时，类比 Claude Code。dsh-tui-pi 是社区构建的 pi 风格 TUI 插件套件，提供实时子 Agent 监控、历史回溯与分叉、飞书手机遥控、动态上下文裁剪、MCP 适配器等 15+ 功能，以及 8 个配套插件。"
descriptionEn: "DeepSeek Harness (dsh) is DeepSeek's coding agent runtime, analogous to Claude Code. dsh-tui-pi is a community-built pi-style TUI plugin suite offering real-time subagent monitoring, history look-back and fork-at-turn, Feishu/phone remote control, zero-LLM dynamic context pruning, MCP adapter, and 15+ features across 8 companion plugins."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: Tech-Experiment
tags: ["AI", "DeepSeek", "TUI", "Terminal", "Agent", "编码Agent", "插件", "开源", "dsh", "MCP"]
heroImage: "../../assets/images/dsh-tui-pi-deepseek-harness-terminal-ui-plugin-ecosystem-banner.jpg"
author: "Mycelium Protocol"
---

如果你关注 Claude Code 生态，会发现它吸引了大量围绕终端交互体验的社区开发——各种 TUI 主题、会话管理插件、工作流脚本。DeepSeek 的编码 Agent 运行时 **DeepSeek Harness（dsh）** 正在走同一条路，而 **dsh-tui-pi** 是目前社区里功能最完整的那个终端 UI 插件套件。

GitHub：[fan56/dsh-tui-pi](https://github.com/fan56/dsh-tui-pi)

---

## 先说 dsh 是什么

**DeepSeek Harness（dsh）** 是 DeepSeek 开源的编码 Agent 运行时，功能定位类比 Claude Code：在终端里接收自然语言指令，调用工具、编写代码、管理文件，支持多轮会话和子 Agent。

dsh 本身提供 Agent 的核心能力——模型调用、工具调用、会话管理、权限控制、Skills、Plan、Goal、Subagent。它的架构是**插件化的**：通过 `dsh plugin` 向 profile 安装 bundle，每个 bundle 可以扩展或替换某一层的行为。

dsh-tui-pi 就是在这个插件系统上构建的终端 UI 层。

---

## 一句话描述 dsh-tui-pi

> 把 dsh 变成 pi 风格的编码 Agent 体验：会话历史可回溯和分叉、引导式预设切换、实时子 Agent 监控、模型 Profile 和主题。

"pi 风格"指的是 DeepSeek 旗下 **pi-tui** 这个终端 UI 框架的视觉和交互风格——类似 Claude Code 的 TUI 设计语言，但来自 DeepSeek 生态。

安装只需两条命令：

```bash
dsh plugin --profile tui add @aiwayds/dsh-tui-pi
dsh --profile tui
```

---

## 15 个核心功能

### 1. Footer — 实时会话概览

屏幕底部始终显示：当前 provider/model、**上下文压力**（context pressure）和**缓存命中率**。不用打开设置就能看到会话的健康状态。

### 2. Think & Tool 面板

推理过程和工具调用活动**不出现在对话记录里**，单独在面板展示。这样对话历史保持干净可读，技术细节不影响主流程。

### 3. 实时子 Agent 监控与引导

每个正在运行的子 Agent 都有专属状态行，可以**实时查看和引导**。`Ctrl+G` 打开子 Agent 选择器，进入后可以主动发送指令或干预正在执行的任务。

### 4. Ask User Question — 结构化提问

模型可以暂停并向你提出结构化问题，**直接在 TUI 里回答**，不需要切出去。对于需要用户确认才能继续的工作流特别有价值。

### 5. 飞书集成 — 手机遥控 dsh

这个功能相当独特：**桌面跑 dsh-tui-pi，手机用飞书/Lark 驱动同一个 dsh 会话**，包括回答 Ask User Question 的弹出卡片。适合开了长时运行任务后离开桌面的场景。

### 6. 动态上下文裁剪（DCP）

**零 LLM 调用**地把上下文控制在限制内。这是配套插件 `dsh-dcp` 提供的能力，不需要模型参与 compaction，确定性算法直接处理。

对比其他 Agent 框架里的 compaction（需要 LLM summarize，有信息损耗），dsh-dcp 的确定性方式更可预测、成本更低。

### 7. 持久化上下文

你的基础规则（ground rules）**随每次请求携带**，热应用，不需要重启。类似 Claude Code 的 CLAUDE.md，但是动态的。

### 8. 模型 Profile 与收藏

按项目切换完整的模型配置（provider + 参数 + 工具组合），通过 `/model` 命令快速切换。`~/.dsh/model-profiles.json` 在插件间共享，`dsh-subagent-registry` 也会读取这个文件。

### 9. Agent Preset 切换

`/preset` 命令在内置 Agent 组合（`standard`、`minimal`……）之间切换。切换会确认并开始一个新会话（旧会话保持可恢复），明确区分了 preset 控制的边界。

### 10. 会话管理与恢复

会话自动保持整洁，几次按键就能恢复，有**跨进程写入保护**防止日志冲突。启动 janitor 默认保留 100 条、7 天内的会话（可配置）。

### 11. 历史浏览器

`/history` 打开双面板回顾界面：
- 左侧：已完成的 turn 列表
- 右侧：选中 turn 的回复内容
- 可以把某条 prompt 复制回编辑器
- **可以只读浏览任何存储的会话，不需要恢复它（不加写锁）**

### 12. 主题

GitHub Light/Dark 配色，热切换，`auto` 模式跟随终端设置。

### 13. 搜索、选择与图片

- `Ctrl+Shift+F`：全文搜索整个对话记录
- 拖拽选中：自动复制到系统剪贴板
- 网络附件/飞书图片**行内渲染**
- LaTeX 渲染为 Unicode 数学符号

### 14. Slash 命令

`/model`、`/resume`、`/btw`、`/profile-switch`、`/hotkeys`……加上所有 dsh 原生命令。

### 15. 启动插件树

每次启动显示当前 profile 里所有插件及其安装的 npm 版本，一目了然。

---

## 8 个配套插件

dsh-tui-pi 随包附带 8 个默认依赖插件，激活需要在 profile 的 `bundles` 列表里列出：

| 插件 | 功能 |
|------|------|
| `dsh-ask-router` | 把 `ask_user_question` 分发到所有响应面（TUI 面板、飞书卡片），第一个回答生效 |
| `dsh-dcp` | 确定性零 LLM 压缩后端 |
| `dsh-llm-proxy` | SYSTEM 代理 + 按主机 LLM 出站路由 |
| `dsh-llm-stats` | `/llm-stats` 用量账本 |
| `dsh-mcp-adapter` | 把 MCP 工具 Schema 折叠出 prompt，增加 `/mcp` 命令 |
| `dsh-model-sync` | 与 pi.dev 模型目录同步 provider 路由 |
| `dsh-subagent-registry` | 把 `~/.dsh/agents/*.md` 注册为 `use_agent` 子 Agent |
| `dsh-web-search-anysearch` | AnySearch 网络搜索 provider |

推荐另外安装：`dsh-topics-memory`（OKF 主题记忆，零 LLM 热路径注入 + 本地 git 追踪 bundle）。

---

## 键盘快捷键

| 按键 | 操作 |
|------|------|
| `Enter` | 发送 prompt |
| `Esc`（双击） | 停止当前任务 |
| `Ctrl+C` | 执行中：取消/退出；空闲：清空编辑器/退出 |
| `Ctrl+L` | 打开模型/think 选择器 |
| `Ctrl+G` | 打开子 Agent 选择器 |
| `Ctrl+O` | 待发送消息队列（s 立即引导 · d 删除） |
| `Ctrl+Shift+F` | 对话记录全文搜索 |
| `↑ / ↓` | 浏览提交历史 |

所有按键都可以通过 `~/.dsh/keybindings.json` 重映射，或用 `/hotkeys` 命令交互式修改。

---

## 与 Claude Code 体验的对比

dsh-tui-pi 在设计上很清楚地对标了 pi（Claude Code 同类产品）的终端体验：

**共同点**
- 插件化架构（bundle/plugin），社区可扩展
- 持久上下文（APPEND_SYSTEM.md 类比 CLAUDE.md）
- 会话历史管理和恢复
- 子 Agent/worktree 支持
- MCP 协议集成

**dsh-tui-pi 特有**
- **飞书手机遥控**——这个功能目前 Claude Code 生态里没有对应物
- **DCP 零 LLM compaction**——确定性压缩，无模型调用
- **Feeder（Ask User Question）统一路由**——多个回答面，第一个生效
- **模型 Profile per-project**——整套 model 配置按项目切换

---

## 这个生态说明了什么

dsh-tui-pi 本身的工程质量不低：1,100+ 单元测试、60+ 测试文件、架构决策记录（ADR）文档、自动迁移逻辑、完善的卸载清理机制。

它的出现说明 DeepSeek Harness 的社区活跃度已经足够支撑这样规模的配套工具开发——从同期出现的多个类似项目（XMoon/dsh-pi-tui、waknow/dsh-tui-pi、realchenwenqiao/dash）可以看出，这不是孤立的个人项目，而是一个正在形成中的插件生态。

编码 Agent 的终端 UI 战争不只在 Anthropic 一侧打响了。

---

## 安装

```bash
# 安装 DeepSeek Harness（如未安装）
npm install -g @deepseek-ai/dsh@0.1.2-rc.1

# 安装 dsh-tui-pi
dsh plugin --profile tui add @aiwayds/dsh-tui-pi

# 启动
dsh --profile tui
# 或直接：dsh-tui-pi
```

要求：dsh >= 0.1.2-rc.1，Node.js `^22.19.0 || >= 24`。

---

## 相关链接

- fan56/dsh-tui-pi：[github.com/fan56/dsh-tui-pi](https://github.com/fan56/dsh-tui-pi)
- XMoon/dsh-pi-tui：[github.com/XMoon/dsh-pi-tui](https://github.com/XMoon/dsh-pi-tui)
- DeepSeek Harness：[github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)

<!--EN-->

If you've been watching the Claude Code ecosystem, you'll have noticed significant community development around terminal interaction — TUI themes, session management plugins, workflow scripts. DeepSeek's coding agent runtime **DeepSeek Harness (dsh)** is following the same trajectory. **dsh-tui-pi** is the most fully-featured community terminal UI plugin suite in that ecosystem today.

GitHub: [fan56/dsh-tui-pi](https://github.com/fan56/dsh-tui-pi)

---

## What Is dsh?

**DeepSeek Harness (dsh)** is DeepSeek's open-source coding agent runtime — analogous to Claude Code. It receives natural language instructions in the terminal, calls tools, writes code, manages files, and supports multi-turn sessions and subagents.

dsh's architecture is **plugin-based**: install bundles into a profile via `dsh plugin`, and each bundle can extend or replace a layer of behavior. dsh-tui-pi is built entirely on this plugin system as the terminal UI layer.

---

## What dsh-tui-pi Does

> Turns dsh into a pi-style coding agent experience: session history look-back and fork-at-turn, guided preset switching, live subagent steering, model profiles, and themes.

The "pi style" refers to the terminal UI design language of DeepSeek's **pi-tui** framework — analogous to Claude Code's TUI, but from the DeepSeek side.

Install in two commands:

```bash
dsh plugin --profile tui add @aiwayds/dsh-tui-pi
dsh --profile tui
```

---

## 15 Core Features

**Footer**: Always-visible session status bar showing provider/model, context pressure, and prompt cache-hit rate.

**Think & Tool Panels**: Reasoning and tool activity displayed in dedicated panels, not inline in the transcript — keeps conversation history clean and readable.

**Live Subagent Steering**: Every running subagent has a status line. `Ctrl+G` opens the subagent picker; you can watch progress and steer running agents with direct messages.

**Ask User Question**: Model can pause and ask structured questions, answered directly in the TUI — no switching contexts.

**Feishu Integration**: Drive the same dsh session from your phone via Feishu/Lark, including answering Ask User Question cards. Useful for long-running tasks when you step away from the desktop.

**Dynamic Context Pruning (DCP)**: Zero-LLM-call context management via the companion `dsh-dcp` plugin. Deterministic algorithm handles compaction without model involvement — no information loss, lower cost, more predictable than LLM-based summarization.

**Persistent Context**: Your ground rules ride along on every request, hot-applied without a restart. Similar to Claude Code's CLAUDE.md, but dynamic.

**Model Profiles**: Switch a complete model configuration (provider + params + tool composition) per project. `~/.dsh/model-profiles.json` is shared across plugins.

**Agent Preset Switching**: `/preset` between built-in agent compositions (`standard`, `minimal`, …). Each switch creates a new session; the previous one stays resumable.

**Session Management**: Sessions stay tidy automatically, resume in a few keystrokes, with a cross-process writer guard preventing log conflicts.

**History Browser**: `/history` opens a two-pane look-back — completed turns on the left, selected turn's replies on the right. Copy a prompt back to the editor, or read-only browse any stored session without resuming it (no write lock).

**Themes**: GitHub Light/Dark, hot-switchable; `auto` follows terminal settings.

**Search, Selection & Images**: `Ctrl+Shift+F` transcript search, drag-select copies to clipboard, web/Feishu attachments render inline, LaTeX renders as Unicode math.

**Slash Commands**: `/model`, `/resume`, `/btw`, `/profile-switch`, `/hotkeys`, plus all dsh-native commands.

**Startup Plugin Tree**: Every profile plugin with its installed npm version, printed at launch.

---

## 8 Companion Plugins

| Plugin | Function |
|--------|----------|
| `dsh-ask-router` | Fans `ask_user_question` to all response surfaces; first answer wins |
| `dsh-dcp` | Deterministic zero-LLM compaction backend |
| `dsh-llm-proxy` | SYSTEM proxy + per-host LLM routing |
| `dsh-llm-stats` | `/llm-stats` usage ledger |
| `dsh-mcp-adapter` | Folds MCP tool schemas out of prompts, adds `/mcp` command |
| `dsh-model-sync` | Syncs provider routes with pi.dev model catalog |
| `dsh-subagent-registry` | Registers `~/.dsh/agents/*.md` as `use_agent` subagents |
| `dsh-web-search-anysearch` | AnySearch web search provider |

---

## What This Ecosystem Signals

dsh-tui-pi's engineering quality is substantial: 1,100+ unit tests, 60+ test files, Architecture Decision Records, automatic migration logic, and thorough uninstall cleanup. Multiple independent projects appeared around the same time (XMoon/dsh-pi-tui, waknow/dsh-tui-pi, realchenwenqiao/dash), signaling a forming ecosystem rather than an isolated personal project.

The terminal UI competition for coding agents isn't only happening on Anthropic's side.

---

## Links

- fan56/dsh-tui-pi: [github.com/fan56/dsh-tui-pi](https://github.com/fan56/dsh-tui-pi)
- XMoon/dsh-pi-tui: [github.com/XMoon/dsh-pi-tui](https://github.com/XMoon/dsh-pi-tui)
- DeepSeek Harness: [github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
