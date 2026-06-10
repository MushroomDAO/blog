---
title: "哪吒：7MB 的 Agent-First 桌面 IDE，彻底解决 AI 编程的注意力碎片化问题"
description: "哪吒（Nezha）是专为 AI 并行编程打造的桌面应用，GitHub 1.4k 星，7MB 安装包。把多项目管理、任务追踪、终端、代码浏览、会话回放、Git 工作流整合到一个界面，告别在 5 个工具间反复切换。本文是普通开发者的完整使用指南。"
titleEn: "Nezha: 7MB Agent-First Desktop IDE — Complete Guide to Solving AI Coding Attention Fragmentation"
descriptionEn: "Nezha is a desktop app built for parallel AI coding (1.4k GitHub stars, 7MB). It unifies multi-project management, task tracking, terminal, code browsing, session playback, and Git workflow in one window. A complete guide for developers who are tired of switching between 5 tools."
pubDate: 2026-06-10
category: "Tech-Experiment"
tags: ["Nezha", "哪吒", "ClaudeCode", "AgentFirst", "AI编程", "桌面应用", "并行开发", "Tauri", "Git"]
lang: "zh-CN"
heroImage: "../../assets/images/nezha-ai-coding-desktop-app.jpg"
---

## 你遇到过这些场景吗

你正在让 Claude Code 处理项目 A 的 bug，同时让 Codex 在项目 B 写新功能。

然后你的工作流变成了：
- Terminal 1：盯着项目 A 的输出
- Terminal 2：盯着项目 B 的进度
- VS Code：看 AI 刚写的代码对不对
- Sourcetree / GitLens：提交之前 review diff
- 另一个 Terminal：跑测试
- 浏览器：查 AI 这次花了多少 token

**你的注意力在 5-6 个窗口之间不停切换**，而 AI 在悄悄工作，你却忙着"管理自己看哪里"。

这就是 [Nezha（哪吒）](https://github.com/hanshuaikang/nezha) 要解决的核心问题。

---

## 什么是哪吒

**哪吒（Nezha）** 是一个 **Agent-First 的 AI 编程桌面应用**，由开发者 hanshuaikang 构建，2026 年 6 月发布 v0.4.0。

- **GitHub**：[hanshuaikang/nezha](https://github.com/hanshuaikang/nezha)（**1.4k 星，143 fork**）
- **安装包大小**：**7MB**（Tauri + Rust，不是 Electron）
- **许可证**：GPL-3.0（开源免费）
- **技术栈**：TypeScript（66%）+ Rust（31%），Tauri 框架

它不是要取代 VS Code 或 Cursor，它解决的是另一个问题：**当你有多个 AI Agent 在多个项目上并行工作时，你在哪里统一管理和观察这一切？**

---

## 核心理念：人的注意力才是瓶颈

传统 IDE 的设计哲学是"人写代码，工具辅助人"。

AI 时代变了：**代码越来越多由 AI 并行生成，人的工作从"写代码"变成了"观察、引导、验收"**。

但几乎所有工具还停留在"人写代码"的设计范式里——终端是单会话的，编辑器是单项目的，Git 工具是独立的，AI 会话记录要去别的地方找。

哪吒从这个认知出发，构建了一套 **Agent-First** 的界面：不是让你更快地写代码，而是让你更高效地**管理多个正在工作的 AI**。

---

## 功能全解析

### 1. 多项目工作区（Multi-Project Workspace）

哪吒最核心的功能：**同时管理多个项目，一键切换，后台终端不断线**。

在普通终端里，你打开项目 A 的 Claude Code 会话，切换到项目 B 时，项目 A 的终端就放在那里，你不知道它什么时候完成，要用的时候还得找窗口。

在哪吒里：
- 所有项目列在侧边栏，每个项目都有实时状态指示
- 切换到项目 B 时，项目 A 的终端在**后台持续运行**
- 任何项目完成或需要你确认时，会**主动提醒你**
- 多个 AI Agent 真正做到并行——你不用盯着某一个

**实际使用场景**：
```
项目 A：让 Claude Code 重构数据库查询逻辑（预计 15 分钟）
项目 B：让 Codex 写测试用例（预计 10 分钟）
项目 C：你自己在写文档

以前：打开 3 个终端窗口，不断切换看进度
现在：哪吒侧边栏实时显示每个项目状态，完成时弹提醒
```

---

### 2. 任务生命周期追踪（Task Lifecycle）

每一个交给 AI 的任务，在哪吒里都有完整的生命周期记录：

```
创建 → 进行中 → 等待确认 → 完成 / 失败
```

这解决了一个很常见的痛点：**你不记得 3 小时前让 AI 做过什么，AI 的输出也找不到了**。

哪吒的任务管理提供：
- **任务状态可视化**：一眼看出哪些完成了，哪些还在跑，哪些需要你处理
- **会话回放（Session Playback）**：可以倒回去看 AI 做了哪些步骤、输出了什么
- **会话恢复**：意外中断后可以恢复上下文继续
- **丰富的任务输入**：支持 @mentions、粘贴图片、预设 Prompts（Pre-prompts）

**会话回放特别有价值**：当 AI 改了代码出现 bug，你需要知道它改了什么步骤、为什么这么改——会话回放让你重现整个过程，而不是对着乱糟糟的 diff 猜。

---

### 3. 原生终端体验（Native Terminal）

哪吒内置基于 **xterm.js** 的终端，支持：
- 完整的命令行操作（不是阉割版）
- 多个项目的独立终端同时运行
- 终端历史保留，项目切换后不丢失

**它和直接用系统 Terminal 的区别**：终端和项目上下文绑定了，切换项目时自动切换工作目录，不需要你手动 `cd`。

---

### 4. 代码浏览与编辑器

哪吒内置轻量代码浏览器，用 **Shiki + CodeMirror** 实现：

- **文件树**：左侧展示项目文件结构，每个文件旁边有 Git 状态标注（修改/新增/删除）
- **代码查看**：支持主流语言语法高亮
- **Markdown 编辑**：内置 Markdown 编辑器，适合查看 AI 生成的文档

**定位**：这不是要取代 VS Code 里的编辑功能，而是让你**不需要打开 VS Code 就能快速 review AI 改了什么**。当你在哪吒里管理 5 个并行任务时，想看看某个文件改了什么，不需要切到外部编辑器。

---

### 5. 完整 Git 工作流

这是哪吒里**最省时间的功能之一**。内置 Git 集成，不需要开 Sourcetree 或 GitKraken：

**查看改动：**
- Staged / Unstaged diff 分开显示
- 文件树里直接看哪些文件被改了（带颜色标注）

**提交：**
- **AI 辅助生成 commit message**：把 diff 发给 AI，自动生成语义化的提交信息
- 一键提交，不需要切到终端

**分支管理：**
- 创建、切换、合并、删除分支
- 查看提交历史和详细日志

**实际效果**：AI 改完代码，你直接在哪吒里看 diff、确认没问题、AI 帮你写 commit message、一键提交——整个流程不离开哪吒。

---

### 6. 用量统计（Usage Analytics）

AI 编程时代，token 消耗就是成本。哪吒内置统计面板：

- **每周 token 消耗趋势**
- **工具调用次数**（AI 调用了多少次 bash、read_file 等工具）
- **操作成本估算**

这让你知道"上周我让 AI 干了多少活，花了多少"，而不是账单来了才发现超支。

---

### 7. 会话管理（Session Management）

哪吒自动检测已安装的 Claude Code / Codex 会话：

- **自动发现**：不需要手动配置，哪吒自动找到正在运行的 AI 会话
- **等待确认提醒**：当 AI 需要你确认某个危险操作（比如删文件、执行命令）时，哪吒弹出提醒——即使你当时在看别的项目
- **历史可视化**：所有历史会话一目了然

---

## 安装：3 分钟搞定

### 前提条件

哪吒是 Claude Code / Codex 的管理界面，需要先安装：

```bash
# 安装 Claude Code（如果还没有）
npm install -g @anthropic-ai/claude-code
```

### 安装哪吒

1. 打开 [GitHub Releases](https://github.com/hanshuaikang/nezha/releases) 下载最新版（v0.4.0）
2. macOS 用户下载 `.dmg`，拖入 Applications

**macOS 安全提示处理**（首次打开可能出现）：
```bash
xattr -rd com.apple.quarantine /Applications/nezha.app
```

3. 打开哪吒，它会自动检测你系统里的 Claude Code / Codex 安装

### 为什么只有 7MB？

因为哪吒用 **Tauri** 而不是 Electron 构建。Electron 需要打包整个 Chromium 浏览器（通常 100MB+），Tauri 用系统自带的 WebView，再加 Rust 后端，整体极其轻量。

7MB 意味着：下载快、启动快、内存占用低。

---

## 实际工作流示例

### 场景一：并行开发两个功能

```
早上 9 点：
1. 打开哪吒，侧边栏看到昨晚两个项目的状态
2. 项目 A：昨晚的重构任务显示"完成"
3. 项目 B：昨晚的 bug 修复任务显示"等待确认"

9:05：
- 点开项目 B，看会话回放，了解 AI 做了什么
- 打开内置文件树，确认改动看起来正确
- 查看 Git diff，没问题，让 AI 生成 commit message，提交

9:15：
- 切到项目 A，看重构结果
- 发现有个边界情况没处理，在任务输入框描述问题，@mention 相关文件
- Claude Code 继续处理，你去做别的事

10:00：
- 哪吒提醒：项目 A 完成了，需要你 review
```

### 场景二：新项目快速起步

```
1. 在哪吒侧边栏新增项目，选择本地目录
2. 打开终端，初始化代码库
3. 把需求用自然语言输入任务框（可以粘贴截图/设计图）
4. Claude Code 开始生成代码
5. 切到另一个项目继续工作，哪吒在后台追踪进度
```

---

## 与其他工具的定位对比

| 工具 | 定位 | 哪吒的优势 |
|------|------|-----------|
| VS Code / Cursor | 以"人写代码"为中心的编辑器 | 哪吒以"AI 工作"为中心，多项目并行管理 |
| 系统 Terminal | 单会话、单项目 | 多项目后台并行，状态同步 |
| Sourcetree / GitKraken | 独立 Git 客户端 | 内嵌在工作流里，不需要切换工具 |
| Claude Code CLI | 单会话命令行 | 哪吒是它的 GUI 管理层，加了多项目和追踪 |

**哪吒不是要替代任何一个工具，而是把它们整合到一个界面，减少切换成本。**

---

## 适合谁用

**最适合：**
- 同时维护多个项目的独立开发者
- 重度使用 Claude Code / Codex 的 AI 编程用户
- 喜欢轻量工具、讨厌 Electron 应用的用户
- 想追踪 AI token 消耗和成本的用户

**不那么适合：**
- 只用一个项目、不需要并行的用户（功能有些过剩）
- 需要完整 IDE 功能（调试器、插件生态）的用户

---

## 目前版本状态

当前版本 **v0.4.0**（2026 年 6 月 6 日发布），已经过 14 个版本迭代，功能相当稳定。项目还在积极开发中，1.4k 星和 143 fork 说明有真实用户基础。

按 GPL-3.0 协议开源，可以自由使用和修改。

---

## 资源

| 资源 | 链接 |
|------|------|
| GitHub | [hanshuaikang/nezha](https://github.com/hanshuaikang/nezha) |
| 最新版本 | [v0.4.0 Releases](https://github.com/hanshuaikang/nezha/releases) |
| 许可证 | GPL-3.0（开源免费） |

---

*本文基于 GitHub README（v0.4.0）和项目文档整理，未收取任何推广费用。*

<!--EN-->

## Nezha: 7MB Agent-First Desktop IDE — Complete Developer Guide

**Nezha** ([hanshuaikang/nezha](https://github.com/hanshuaikang/nezha)) is a desktop application built for parallel AI-assisted programming. It's designed around one insight: **when multiple AI agents work simultaneously, human attention — not compute — becomes the bottleneck.**

### Stats
- **GitHub Stars**: 1,400+ (1.4k)
- **Forks**: 143
- **Install Size**: **7MB** (Tauri + Rust, not Electron)
- **License**: GPL-3.0 (open-source, free)
- **Latest**: v0.4.0 (June 6, 2026)
- **Tech**: TypeScript (66%) + Rust (31%), Tauri + xterm.js + CodeMirror/Shiki

---

### The Problem It Solves

When using Claude Code / Codex across multiple projects, most developers juggle:
- Multiple terminal windows
- VS Code for code review
- A separate Git client for diffs
- Another window for session logs

**Nezha puts all of this in one place, designed for the agent-first workflow rather than the human-writes-code paradigm.**

---

### Core Features

**1. Multi-Project Workspace**
- One-click project switching with background terminals that stay alive
- Real-time status sync across all active projects
- Alerts when any project needs your attention
- True parallel execution across multiple AI agents

**2. Task Lifecycle Tracking**
- Full transparency: creation → in-progress → awaiting confirmation → complete/failed
- **Session playback**: replay what the AI did step-by-step
- Session recovery after interruption
- Rich task input: @mentions, image paste, pre-prompts

**3. Native Terminal**
- Full-featured xterm.js terminal (not a stripped-down version)
- Multiple project terminals persist in background
- Auto-switches working directory on project switch

**4. Built-in Code Browser**
- File tree with Git status annotations (modified/added/deleted)
- Syntax highlighting via Shiki + CodeMirror
- Markdown editor for AI-generated docs
- Quick review without opening an external editor

**5. Complete Git Workflow**
- Staged/unstaged diff visualization
- **AI-generated commit messages** from diff
- Branch management: create, switch, merge, delete
- Commit history and detailed logs

**6. Usage Analytics**
- Weekly token consumption trends
- Tool invocation count
- Estimated operational costs

**7. Session Management**
- Auto-detects Claude Code / Codex sessions
- User confirmation alerts for pending AI decisions
- Session history visualization

---

### Installation

**Prerequisites**: Claude Code or Codex installed.

1. Download from [GitHub Releases](https://github.com/hanshuaikang/nezha/releases)
2. On macOS, if blocked by Gatekeeper:
```bash
xattr -rd com.apple.quarantine /Applications/nezha.app
```
3. Nezha auto-detects your AI agent installations.

**Why 7MB?** Tauri uses the system WebView instead of bundling Chromium (like Electron). Fast to download, fast to start, low memory overhead.

---

### Workflow Example

```
9:00 AM — Open Nezha, sidebar shows overnight task status
9:05 AM — Project B finished: review session playback → check diff → AI writes commit message → commit
9:10 AM — Project A needs confirmation: review the risky operation, approve
9:15 AM — New task for Project A: paste screenshot of the bug, describe fix
9:20 AM — Switch to Project C, work there while Project A runs in background
10:00 AM — Nezha alert: Project A complete, ready for review
```

---

### When to Use Nezha

**Great fit**: developers running multiple AI agents in parallel, heavy Claude Code / Codex users, anyone frustrated by constant context-switching.

**Less necessary**: single-project workflows, or when you need a full IDE debugger/plugin ecosystem.

---

### Resources

- GitHub: [hanshuaikang/nezha](https://github.com/hanshuaikang/nezha)
- Releases: [v0.4.0](https://github.com/hanshuaikang/nezha/releases)
- License: GPL-3.0
