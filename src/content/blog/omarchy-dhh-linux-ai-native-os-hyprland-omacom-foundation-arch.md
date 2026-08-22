---
title: "Omarchy：DHH 造的 AI 原生 Linux，9 个 Agent 开箱即用，Omacom 基金会 800 万美元背书"
titleEn: "omarchy-dhh-linux-ai-native-os-hyprland-omacom-foundation-arch"
description: "basecamp/omarchy 是 Rails 作者 DHH 打造的 AI 原生 Linux 发行版，基于 Arch + Hyprland + Quickshell，28,045 stars，MIT。核心定位：美观、现代、有主见——预装 9 个 AI 编程 Agent 惰性启动器（Claude Code/Codex/OpenCode/Copilot/Grok/Pi 等），顶栏 Agent 面板统一追踪订阅额度，systemd 崩溃自动交给 Agent 诊断，Agent Skill 跨 Claude Code/Codex/Pi 共享。Omacom Foundation 于 2026 年 8 月宣布以 800 万美元独立资助该项目。"
descriptionEn: "basecamp/omarchy is an AI-native Linux distribution by DHH (Rails author), built on Arch + Hyprland + Quickshell, 28,045 stars, MIT. Core positioning: beautiful, modern, opinionated — ships with 9 AI coding agent lazy-load launchers (Claude Code, Codex, OpenCode, Copilot, Grok, Pi, etc.), a top-bar agents panel unifying subscription quota tracking, systemd-coredump crash auto-diagnosis via AI agent, and an Omarchy Skill shared across Claude Code, Codex, and Pi. The Omacom Foundation launched in August 2026 with $8 million to independently fund the project."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["Linux", "AI原生", "DHH", "Omarchy", "Hyprland", "Agent", "开源", "桌面系统"]
heroImage: "../../assets/images/omarchy-dhh-linux-ai-native-os-hyprland-omacom-foundation-arch-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：basecamp/omarchy
主页：omarchy.org
许可证：MIT
语言：Shell
Stars：28,045 · Forks：2,857
版本：4.0.0（ISO 可下载）
发起人：DHH，孵化于 37signals（Basecamp / HEY 母公司）
基金：Omacom Foundation，$800 万美元，2026-08-22 宣布成立

---

## 一、它是什么

Ruby on Rails 的作者 David Heinemeier Hansson（DHH）做了一个 Linux 发行版。

不是 tinkerer 的玩具，不是对极客的炫技——是他自己每天用来工作的系统，打包给任何想用的人：

> *Beautiful, Modern & Opinionated Linux*

技术底层：**Arch Linux**（滚动更新，软件包最新）+ **Hyprland**（Wayland 原生平铺窗口管理器）+ **Quickshell**（桌面构建工具包）。预装 Neovim、Chromium、Obsidian、LibreOffice、Kdenlive、OBS Studio，甚至一个 Winamp 风格的音乐播放器。

哲学上借鉴了日本「お任せ（omakase）」概念——不让你从头选配，给你一个已经选好的完整系统，直接上手。

---

## 二、AI 原生的具体含义

Omarchy 不是「装了 AI 工具的 Linux」，而是把 AI Agent 作为**一等公民**设计进系统的每一层。

### 9 个 Agent，惰性启动，开箱即用

| 命令 | Agent |
|------|-------|
| `claude` | Claude Code |
| `codex` | OpenAI Codex |
| `opencode` | OpenCode |
| `agy` | Google Antigravity CLI |
| `copilot` | GitHub Copilot CLI |
| `crush` | Crush（Charm）|
| `grok` | xAI Grok CLI |
| `pi` | Mario Zechner 的 Pi |
| `omp` | Oh My Pi |

这些 launcher 是 mise 管理的轻量 stub，首次调用时才下载，不用就不占空间。想加新的 Agent？`omarchy-mise-install <package>` 一行命令。

### 默认 Agent 快捷键

`Super + Shift + Ctrl + A`——在独立终端窗口启动你选定的默认 Agent，直接进入无需确认的自动执行模式。`omarchy agent prompt "Review this project"` 可以带任务启动。没选过默认 Agent？系统会在首次使用时弹出选择器。

终端里的别名：`a`（默认 Agent），`c`（OpenCode），`cx`（Claude Code），`cy`（Codex）——都是自动审批模式。

### 顶栏 Agent 面板

系统检测到机器上有 AI 编程使用记录后，顶栏会自动出现 Agent 图标（没有就不出现，保持干净）。面板统一追踪：

- 订阅计划和已用百分比
- 5 小时 session 限额 / 周限额剩余
- 预付余额
- 按天 / 按模型的 token 用量

支持 Claude Code、Codex、Fireworks，每 15 分钟刷新一次。还能通过同步文件夹合并多台机器的用量——一个面板看所有设备。

### AI 崩溃诊断

Omarchy 监听 **systemd-coredump**。进程 segfault → 桌面通知「进程崩溃」→ 点击通知 → 崩溃信息 + `diagnose-crash` Skill 自动交给默认 Agent → Agent 从 core dump 提取事实、判断是否值得上报上游。

也可以手动跑：`omarchy agent crash <pid>`，对应 `coredumpctl list` 里任意 PID。

### Omarchy Skill 跨 Agent 共享

Omarchy 自带一个用于调整系统配置的 Agent Skill——调 Hyprland 配置、修改顶栏、从头创建主题都可以。Skill 以符号链接同时出现在：

- `~/.claude/skills`（Claude Code）
- `~/.codex/skills`（Codex）
- `~/.pi/agent/skills`（Pi）
- `~/.gemini/config/skills`（Antigravity）
- `~/.agents/skills`（通用目录）

大多数 Agent harness 会自动识别。文档建议先用 plan mode 看 Agent 打算改什么，再执行——因为 Agent 有可能「把所有配置搞乱」。

### 主题联动

切换 Omarchy 主题时，Claude Code、Pi、OpenCode 的主题也跟着变。不是 hack，是系统级联动。

### 本地 LLM

Install > AI 菜单里直接安装 LM Studio（GUI，适合入门）或 Ollama（CLI）。

---

## 三、安装体验

ISO 下载，balenaEtcher 写 U 盘，关掉 Secure Boot，回答几个问题，安装完成——**最快不到 1 分钟**，慢一点也不超过 5 分钟。

默认全盘加密。支持双启动（和 Windows 共存，需先关 BitLocker）、无人值守安装（供 VM 和机群部署）、以及「为他人准备机器」模式（个人信息推迟到新主人第一次开机时设置）。

版本 4.0.0 的 ISO 可以直接从 omarchy.org 下载。

---

## 四、Omacom Foundation：800 万美元独立资助

2026 年 8 月，**Omacom Foundation** 宣布成立，$800 万美元专项资助 Omarchy。

这个非营利基金的出现，把 Omarchy 从「37signals 的内部孵化项目」变成了一个**有独立资金保障的开源操作系统**。项目不再依附于任何一家商业公司的存续，长期维护有了结构性保证。

---

## 五、为什么值得关注

28,045 stars 不是意外。Omarchy 击中了一个痛点：**现有 AI 工具都在独自处理 Agent，没有人把 Agent 作为操作系统级的设计元素**。

Claude Code 是 IDE 插件，Codex 是 CLI，Berd 是桌面工作台——但没有一个从操作系统层面统一 Agent 的 launcher、额度监控、崩溃诊断、Skill 共享和主题联动。Omarchy 是第一个这么做的，而且它是真实的 Linux 发行版，不是概念演示。

代价是明显的：Arch 底层意味着一定的维护成本，Hyprland 需要适应期，「有主见」的系统也意味着你得接受 DHH 的选择。但如果你本来就是 Linux 用户、重度 AI 编程 Agent 用户，Omarchy 是目前最完整的把两者整合进一个系统的方案。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Omarchy: DHH's AI-Native Linux — 9 Agents Out of the Box, $8M Omacom Foundation Backing

*by Mycelium Protocol*

---

GitHub: basecamp/omarchy
Homepage: omarchy.org
License: MIT
Language: Shell
Stars: 28,045 · Forks: 2,857
Version: 4.0.0 (ISO available)
By: DHH, incubated at 37signals (makers of Basecamp and HEY)
Funding: Omacom Foundation, $8 million, announced 2026-08-22

---

### What It Is

The creator of Ruby on Rails made a Linux distribution.

Not a tinkerer's toy. Not a showcase for geeks. The system DHH uses every day to get work done, packaged for anyone who wants it:

> *Beautiful, Modern & Opinionated Linux*

Technical stack: **Arch Linux** (rolling release, always current) + **Hyprland** (native Wayland tiling window manager) + **Quickshell** (desktop construction kit). Ships with Neovim, Chromium, Obsidian, LibreOffice, Kdenlive, OBS Studio, and even a Winamp-style music player.

The philosophy borrows from Japanese *omakase* — don't make you configure from scratch; hand you a complete, already-chosen system, ready immediately.

---

### What AI-Native Actually Means Here

Omarchy isn't "Linux with some AI tools installed." It's a system where **AI agents are designed as first-class citizens at every layer**.

#### 9 Agents, Lazy-Loaded, Ready to Run

| Command | Agent |
|---------|-------|
| `claude` | Claude Code |
| `codex` | OpenAI Codex |
| `opencode` | OpenCode |
| `agy` | Google Antigravity CLI |
| `copilot` | GitHub Copilot CLI |
| `crush` | Crush (Charm) |
| `grok` | xAI Grok CLI |
| `pi` | Mario Zechner's Pi |
| `omp` | Oh My Pi |

These launchers are lightweight mise-managed stubs. Nothing is downloaded until first use. To add another agent: `omarchy-mise-install <package>`, one command.

#### Default Agent Hotkey

`Super + Shift + Ctrl + A` — launches the default agent in a dedicated terminal window, already in auto-approve mode. `omarchy agent prompt "Review this project"` launches with a task. If no default agent is set, a picker appears on first use.

Terminal aliases: `a` (default agent), `c` (OpenCode), `cx` (Claude Code), `cy` (Codex) — all in auto-approve mode.

#### Top-Bar Agents Panel

After detecting any AI coding usage on the machine, the top bar grows an agents icon. The panel tracks everything in one place:

- Subscription plan and percentage used
- 5-hour session limit / weekly limit remaining
- Prepaid balance
- Token usage by day and by model

Covers Claude Code, Codex, and Fireworks out of the box; refreshes every 15 minutes. The panel can even merge usage records from other machines via a synced folder — one panel for all your devices.

#### AI Crash Diagnosis

Omarchy watches **systemd-coredump**. When a process segfaults: desktop notification → click → crash details plus a `diagnose-crash` skill handed to the default agent → agent extracts facts from the core dump, decides whether the crash is worth reporting upstream.

Manual mode also available: `omarchy agent crash <pid>`, targeting any PID from `coredumpctl list`.

#### Omarchy Skill Shared Across All Agents

Omarchy ships a system-configuration Agent Skill — tweak Hyprland configs, adjust the top bar, create a new theme from scratch. The skill is symlinked simultaneously into:

- `~/.claude/skills` (Claude Code)
- `~/.codex/skills` (Codex)
- `~/.pi/agent/skills` (Pi)
- `~/.gemini/config/skills` (Antigravity)
- `~/.agents/skills` (generic location)

Most agent harnesses pick it up automatically. The docs recommend running in plan mode first — because an agent could "make a mess of everything."

#### Theme Sync

Switch the Omarchy theme and Claude Code, Pi, and OpenCode follow. Not a hack — a system-level cascade.

#### Local LLMs

Install LM Studio (GUI, great for beginners) or Ollama (CLI) directly from the Install > AI menu.

---

### Installation

Download the ISO, write it to a USB stick with balenaEtcher, disable Secure Boot in BIOS, answer a few questions — install completes **in under a minute on fast hardware**, five minutes at most. Default full-disk encryption. Supports dual boot (with Windows, requires disabling BitLocker first), unattended installs (for VMs and fleet machines), and a "prepare for another owner" mode where personal setup is deferred to first boot.

Version 4.0.0 ISO is available directly at omarchy.org.

---

### Omacom Foundation: $8 Million Independent Endowment

In August 2026, the **Omacom Foundation** announced its launch with $8 million dedicated to funding Omarchy.

This nonprofit transforms Omarchy from "37signals' internal incubation project" into an **open-source operating system with independent structural funding**. The project no longer depends on any single commercial company's survival for long-term maintenance.

---

### Why It Matters

28,045 stars aren't an accident. Omarchy hit a real gap: **every AI tool handles agents independently — nobody has made agents a design element at the OS level**.

Claude Code is an IDE plugin. Codex is a CLI. Berd is a desktop workbench. But none of them unify agent launching, quota monitoring, crash diagnosis, Skill sharing, and theme sync at the operating system layer. Omarchy does — and it's a real Linux distribution, not a concept demo.

The tradeoff is obvious: Arch means maintenance overhead, Hyprland has a learning curve, and "opinionated" means accepting DHH's choices. But if you're already a Linux user and a heavy AI coding agent user, Omarchy is the most complete integration of both into a single system available today.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
