---
title: 'Orca：67K stars 的并行 Agent 编排台，把 40+ CLI Agent 变成一支舰队'
titleEn: "Orca: 67K-Star Parallel Agent Orchestration IDE Turns 40+ CLI Agents into a Fleet"
description: "Stably AI(YC W22) 出品的开源 ADE，MIT 协议。一个 prompt 扇出给多个 Agent，各跑独立 worktree，Design Mode 点 UI 元素直喂 Agent，SSH 远端机器、手机 App 随时调度——这是目前把「Agent 当舰队管」想得最透的工具。"
descriptionEn: "Open-source ADE from Stably AI (YC W22), MIT licensed. Fan one prompt across multiple agents each in an isolated worktree, Design Mode clicks UI straight into agent context, SSH remote machines, mobile companion for anywhere control — the most thorough 'agents-as-fleet' tooling available."
pubDate: "2026-09-12"
updatedDate: "2026-09-12"
category: "Tech-News"
tags: ["AI-agent", "open-source", "developer-tools", "Claude-Code", "parallel-agents", "Orca"]
heroImage: "../../assets/banner-ai-infrastructure.jpg"
---

> 📌 开源仓库：stablyai/orca
> GitHub：https://github.com/stablyai/orca
> 官网：https://onOrca.dev
> License：MIT · Stars：67K+
> 作者：Stably AI（YC W22）
> 创建：2026 年 3 月

---

**BLUF**：Orca 是一个让你同时调度多个 AI 编程 Agent 的桌面工具——每个 Agent 在独立的 git worktree 里跑，互不干扰，结果并排对比。它不替你订阅 Claude Code 或 Codex，而是用你自己的订阅，把这些 Agent 变成一支可以统一指挥的舰队。MIT 开源，67K stars，支持 40+ 主流 CLI Agent，macOS / Windows / Linux 全平台 + iOS/Android 手机端。

---

## 问题是什么

每个 AI 编程 Agent 都有自己的操作方式。Claude Code 有 Claude Code 的 keybinding，Codex 有 Codex 的上下文管理，Cline 有 Cline 的工具调用接口。

当你同时用三四个 Agent 处理不同任务时，你需要：
- 来回切终端窗口
- 手动管理哪个 Agent 在哪个分支上
- 盯着四个不同的输出流想"这个搞完了没有"
- 从床上爬起来看看跑了两小时的那个 Agent 到底成没成

Orca 解决的就是这些摩擦。

---

## 核心设计：Parallel Worktrees

Orca 最核心的能力是 **Parallel Worktrees**：

**操作流程**：
1. 给出一个任务（比如"给这个 API 加速率限制"）
2. Orca 把这个任务扇出给多个 Agent（比如 Claude Code × 2、Codex × 1）
3. 每个 Agent 在独立的 git worktree 里跑，互不影响主分支和彼此
4. 任务跑完后，并排对比三份 diff
5. 选最好的那份合并进主分支

这不只是"多开几个终端"。worktree 隔离意味着：Agent 可以随意修改文件、运行测试、甚至制造错误，不会污染你的工作区。对比完毕后，不满意的直接丢掉——零恢复成本。

---

## 终端层：Ghostty 级别的渲染

Orca 的终端不是普通的嵌入 xterm。

**技术栈**：WebGL 渲染，和 Ghostty 同档次。支持：
- 无限分屏（横/竖任意组合）
- Scrollback 跨应用重启持久化
- 所有 Agent 的输出都在同一个界面里，不需要 `Cmd+Tab` 切换

对于"盯着 Agent 跑"这件事，终端体验直接影响注意力成本——这也是 Orca 花精力做终端而不只做 orchestration 的理由。

---

## Design Mode：点 UI 元素，直喂 Agent

这是 Orca 里最有意思的功能之一。

**原理**：Orca 内嵌了真实的 Chromium 浏览器（不是 webview）。在 Design Mode 下，你点击页面上任意一个 UI 元素，Orca 会自动提取：
- 该元素的 HTML 结构
- 相关 CSS 样式
- 一张裁剪好的截图

这些内容会作为上下文直接注入到你的 Agent prompt 里。

**实际用途**：你不需要再手写"那个蓝色按钮的 padding 太大了"——你直接点那个按钮，Agent 拿到的是精确的 DOM 结构和样式，而不是你描述的模糊语言。

---

## GitHub & Linear 原生集成

Orca 不只是终端管理器，它把任务管理也集成了进来：

- **GitHub**：应用内浏览 PR、issues、项目看板，从任意 issue 直接开一个 worktree
- **Linear**：同样的逻辑，Linear ticket → worktree，无需切应用

这意味着从"看到一个 bug" 到"Agent 开始修它"的流程，全部在 Orca 里完成，不需要浏览器、不需要手动 `git checkout -b`。

---

## SSH Worktrees：在远端高性能机器跑 Agent

本地 MacBook 跑 Agent 没问题，但如果要同时跑五个，或者跑需要大量计算的任务呢？

Orca 的 SSH Worktrees：
- 在远端 Linux 服务器（甚至 GPU 机器）上建立 worktree
- 完整的文件编辑、git 操作、终端访问
- **自动重连**：网络断了，Orca 自动恢复 session
- **端口转发**：远端跑的 dev server 直接在本地访问

这让"Agent 跑在算力更大的地方"成为日常操作，而不是需要配置 tmux + rsync 的麻烦事。

---

## Mobile Companion：手机上调度 Agent

Orca 有 iOS 和 Android 配套 App（iOS 在 App Store，Android 提供 APK）。

手机端的能力：
- 实时监控所有 Agent 的运行状态
- 收到 Agent 完成的推送通知
- 发送后续指令（follow-up prompt）

这直接解决了"晚上让 Agent 跑，不知道什么时候完成"的问题。Agent 跑完了，手机推送一条通知，睡觉前扫一眼，满意就 merge，不满意明天再说。

---

## 支持的 Agent 列表（40+）

Orca 不绑定任何 Agent，列表包括：

**主流编程 Agent**：Claude Code、Codex（OpenAI）、OpenCode、Pi、Cline、Charm（charmbracelet/crush）

**新兴选手**：Codebuff、Command Code、Continue、Droid（Factory AI）、Kilocode、Kimi Code、Kiro（AWS）、Mistral Vibe、Qwen Code、Rovo Dev（Atlassian）

以及"any CLI agent"——只要是命令行接口，Orca 理论上都能跑。

---

## 安装

**桌面端（macOS / Windows / Linux）**：

```bash
# macOS (Homebrew)
brew install --cask stablyai/orca/orca

# Arch Linux
yay -S stably-orca-bin

# 直接下载：https://onorca.dev/download
```

**手机端**：
- iOS：App Store 搜 "Orca IDE" 或 TestFlight
- Android：GitHub releases 下载 APK

---

## 几个值得关注的设计决策

**BYOK（Bring Your Own Key）**：Orca 不收订阅费，你用自己的 Claude/OpenAI 等订阅跑 Agent。这是重要的定位——它是工具层，不是中间商。

**MIT 开源**：代码完全开放，可以自己 build，也可以二次开发。云端配对服务（mobile companion 用到的 relay）的代码也在仓库的 `cloud/` 目录下。

**Stably AI 是谁**：YC W22 背景，最早做 stablecoin 基础设施，Orca 是他们 2026 年的新方向。67K stars 是 2026 年 3 月到 9 月的增长——六个月内从零到这个量级，说明这个方向的需求真实存在。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: stablyai/orca
> GitHub: https://github.com/stablyai/orca
> Website: https://onOrca.dev
> License: MIT · Stars: 67K+
> Author: Stably AI (YC W22)
> Created: March 2026

---

**BLUF**: Orca is a desktop tool for orchestrating multiple AI coding agents simultaneously — each agent runs in an isolated git worktree, results sit side-by-side for comparison. It doesn't replace your Claude Code or Codex subscription; it uses your existing subscriptions and turns those agents into a coordinated fleet. MIT-licensed, 67K stars, supports 40+ CLI agents, macOS/Windows/Linux plus iOS/Android mobile companion.

---

## The Problem

Every AI coding agent has its own interface. Claude Code has its own keybindings, Codex its own context management, Cline its own tool-call surface.

Running three or four agents on different tasks simultaneously means:
- Constant terminal window switching
- Manually tracking which agent is on which branch
- Watching four output streams wondering "is that one done yet?"
- Getting out of bed to check whether the two-hour run finished

Orca eliminates that friction.

---

## Core Design: Parallel Worktrees

Orca's most central capability is **Parallel Worktrees**:

**Flow:**
1. Describe a task (e.g. "add rate limiting to this API")
2. Orca fans that task out to multiple agents (e.g. Claude Code × 2, Codex × 1)
3. Each agent runs in an isolated git worktree — no interference with your working branch or each other
4. When tasks finish, compare three diffs side by side
5. Pick the best one and merge

This isn't "open a few terminals." Worktree isolation means agents can freely modify files, run tests, even make mistakes — without contaminating your workspace. Discard what you don't want, zero recovery cost.

---

## Terminal Layer: Ghostty-Class Rendering

Orca's terminal isn't a basic embedded xterm.

**Stack:** WebGL rendering, same tier as Ghostty. Features:
- Unlimited splits, any horizontal/vertical arrangement
- Scrollback persists across app restarts
- All agent output in one interface — no `Cmd+Tab` required

Terminal quality directly affects attention cost when watching agents work. That's why Orca invested in the terminal layer rather than just the orchestration.

---

## Design Mode: Click UI Elements, Feed Them to Your Agent

One of Orca's most interesting features.

**How it works:** Orca embeds a real Chromium browser (not a webview). In Design Mode, click any UI element and Orca automatically extracts: the HTML structure, the relevant CSS, and a cropped screenshot.

This context is injected directly into your agent prompt.

**Practical use:** Instead of writing "that blue button has too much padding," you click the button. The agent receives the exact DOM structure and styles — not your approximation of them.

---

## Native GitHub & Linear Integration

Orca integrates task management directly:

- **GitHub:** Browse PRs, issues, and project boards in-app — open a worktree directly from any issue
- **Linear:** Same logic — Linear ticket → worktree, no app switching needed

From "spotted a bug" to "agent is working on it" — the entire flow stays inside Orca.

---

## SSH Worktrees: Run Agents on Remote Hardware

Local laptop is fine for one agent. Five concurrent agents, or compute-heavy tasks?

Orca's SSH Worktrees let you:
- Establish worktrees on a remote Linux server (including GPU machines)
- Full file editing, git operations, terminal access
- **Auto-reconnect:** network drops, Orca recovers the session automatically
- **Port forwarding:** dev servers running remotely are directly accessible locally

Running agents on beefier hardware becomes a routine operation rather than a tmux + rsync configuration exercise.

---

## Mobile Companion: Steer Agents from Your Phone

Orca has iOS and Android companion apps (iOS on App Store, Android APK).

Mobile capabilities:
- Real-time monitoring of all running agents
- Push notifications when agents complete
- Send follow-up prompts from anywhere

This solves "let agents run overnight, don't know when they finish." Agent completes → push notification → check from bed → merge if satisfied, revisit in the morning if not.

---

## Supported Agents (40+)

Orca isn't bound to any single agent. The list includes:

**Established coding agents:** Claude Code, Codex (OpenAI), OpenCode, Pi, Cline, Charm

**Newer entrants:** Codebuff, Command Code, Continue, Droid (Factory AI), Kilocode, Kimi Code, Kiro (AWS), Mistral Vibe, Qwen Code, Rovo Dev (Atlassian)

Plus "any CLI agent" — if it has a command-line interface, Orca can run it.

---

## Install

**Desktop (macOS / Windows / Linux):**

```bash
# macOS (Homebrew)
brew install --cask stablyai/orca/orca

# Arch Linux
yay -S stably-orca-bin

# Direct download: https://onorca.dev/download
```

**Mobile:**
- iOS: App Store ("Orca IDE") or TestFlight
- Android: APK from GitHub releases

---

## Design Decisions Worth Noting

**BYOK (Bring Your Own Key):** Orca charges no subscription fee — you run agents with your own Claude/OpenAI subscriptions. It's tooling, not a middleman.

**MIT-licensed:** Fully open-source, buildable from source, forkable. The mobile companion relay service code is also in the repo under `cloud/`.

**Who is Stably AI:** YC W22 alumni, originally stablecoin infrastructure, Orca is their 2026 direction. 67K stars in six months (March to September 2026) signals that the underlying demand is real.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
