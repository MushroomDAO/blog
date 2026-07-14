---
title: "按头安利：Agent Island —— 发完一轮去生活，该你了它会叫你"
titleEn: "Must Have: Agent Island — Start the Run, Go Live Your Life"
description: "Agent Island 是一个住在 MacBook 刘海里（或 Windows 顶栏）的 AI Agent 状态伴侣：实时监控 Claude Code 和 Codex 两个工具的配额、费用、重置倒计时，转完一轮就叫你，配额重置后自动续命——Mac + Windows 双平台，纯原生无 Electron，MIT 开源。"
descriptionEn: "Agent Island lives in your MacBook notch (or Windows top bar) — monitors Claude Code and Codex quotas, cost, and reset countdowns in real time, rings you when a session finishes, and auto-resumes when the quota resets. Native SwiftUI on Mac, WPF on Windows, MIT licensed."
pubDate: "2026-07-14"
updatedDate: "2026-07-14"
category: "Tech-Experiment"
tags: ["Claude Code", "开发工具", "macOS", "效率工具"]
heroImage: "../../assets/images/agent-island-claude-code-codex-status-companion-mac-windows-banner.jpg"
---

> GitHub：[tristan666666/agent-island](https://github.com/tristan666666/agent-island)  
> 官网：[agent-island.dev](https://agent-island.dev)  
> 平台：macOS 13+（SwiftUI，Apple Silicon + Intel）| Windows 10+（WPF）  
> 安装：`brew install tristan666666/tap/agentisland`  
> 许可：MIT

---

## 它解决的那个真实问题

你把任务扔给 Claude Code 或 Codex，然后……等。  
等它转，等它转，偶尔回来看一眼，发现它早就停了，配额也到顶了，等了两小时什么都没发生。

或者反过来：你去做别的事，回来后不知道它跑完了没有，打开 terminal 才发现十五分钟前就停了。

Agent Island 就是为这件事造的——**让 Agent 工作，你去生活；它转完，叫你；配额回来，自动续命。**

---

## 它住在哪

**Mac**：住在 MacBook 的刘海（notch）里，不占 Dock 也不占菜单栏。非刘海机型（Intel、Mac mini、外接显示器）可切换为紧凑顶栏模式。

**Windows**：原生 WPF 应用，同款检测引擎，顶栏模式或浮动小部件（可拖拽，记住位置），托盘图标常驻显示用量圆环。

两端都是纯原生——Mac 是 SwiftUI，Windows 是 WPF，**没有 Electron**。

---

## 四件核心事

### 1. 实时状态，一眼知道 Agent 在不在干活

刘海/顶栏里的 Claude 和 Codex 图标，随时镜像真实状态：

| 图标状态 | 含义 |
|--------|------|
| **旋转** | 有 session 正在工作 |
| **静止** | 没有任何 session 运行，或这轮刚结束（该你了） |
| **红色脉冲** | 需要你处理：限速 / 登录失效 / 网络 / provider 报错 |

检测是事件驱动的（Mac 用 FSEvents 监听 transcript 文件），**状态变化在 Agent 真实停止约 1 秒后就体现出来**，不是轮询。

---

### 2. 「该你了」闹钟

一轮结束时：

- 弹出前台闹钟窗口
- 发送系统通知
- 播放提示音（内置多个选项，或导入自己的音频文件）

几个细节做得很好：
- **回复即消失**：你在线程里一回复，闹钟自动关掉，不会留着烦你
- **多轮排队**：如果你没注意，连续结束的多轮会排队显示，不会吞掉
- **直接跳转**：Codex session 通过 `codex://threads/…` 跳到对应线程；Claude CLI session 用 `claude --resume` 恢复；Claude Desktop 直接把窗口拉到前台

---

### 3. 配额耗尽专用闹钟

「轮结束」和「配额到顶」是两件不同的事，Agent Island 给它们各自的闹钟。

配额耗尽时，闹钟上直接显示重置时间——比如「Resets at 15:55 (~2h)」。你不用再去找 Claude 的设置页算几点能用。

有防骚扰设计：启动时如果配额已经是耗尽状态，不触发（只在这次耗尽事件本身触发一次）。

---

### 4. 配额重置自动续命

这是最硬核的功能。

给某个 session 绑定一个规则：当 Claude 或 Codex 的使用窗口重置时（或按固定间隔），自动发一条消息（`continue` / `OK` / 你自定义的内容）让它继续跑。**人不在，夜里它自己续上。**

内置的安全机制：

- **全局开关**：Settings 里关掉，任何自动续命都不会触发
- **目录白名单**：续命只对你显式允许的项目目录生效
- **运行记录**：每次执行或拦截都有日志，从 Settings 直接打开文件夹查

诚实说明：Mac 必须处于唤醒状态，每次续命都会消耗 token。

---

## 用量岛：配额 + 费用 + 倒计时

刘海里有一块「用量岛」，可滑动翻页，直接显示：

- Claude / Codex 的 **5 小时窗口**和**周用量**百分比
- **已花费金额**
- **重置倒计时**

Claude 登录失效时，Re-authenticate 按钮直接在浏览器打开 claude.com 授权页，拦截回调——不用开 terminal，不用粘贴 code。

---

## 安装

**macOS（推荐 Homebrew）：**

```bash
brew install tristan666666/tap/agentisland
```

或直接下载 DMG：[最新 Release](https://github.com/tristan666666/agent-island/releases/latest)

首次打开如果 macOS 提示"未经验证"（App 暂无 Apple 开发者账号公证），右键 → 打开一次即可。

**Windows：**

```bash
# Scoop
scoop bucket add agent-island https://github.com/tristan666666/scoop-bucket
scoop install agent-island/agentisland

# winget
winget install TristanTang.AgentIsland
```

或直接下载 [AgentIsland-win-x64.zip](https://github.com/tristan666666/agent-island/releases/latest)，解压运行 `AgentIsland.exe`。

---

## 技术背景

Agent Island fork 自 [codex-island](https://github.com/ericjypark/codex-island)（Eric Park 的工作，提供了用量计量和费用统计基础）。

在此之上新增：
- FSEvents 事件驱动的 session 状态检测
- 轮结束 / 配额耗尽双闹钟系统
- Auto-resume 自动续命机制
- macOS 双布局 + Windows WPF 移植

检测原理：读取 Claude Code、Claude Desktop、Codex 在本机写入的 transcript 文件，识别 `stop_reason: end_turn`（Claude）和 `task_complete`（Codex）等结束标记。没有遥测，没有数据上传，一切在本地运行。

---

## 适合谁用

- **重度 Claude Code 用户**：同时跑多个 session，需要知道哪个轮到了
- **Claude + Codex 混用用户**：两个配额都要盯，自己算太烦
- **有夜间/后台任务需求**：扔给 Agent 跑，自己去做别的，结束了被叫回来
- **想最大化配额利用率**：不等 Agent 发呆，配额一回来立刻续命

---

GitHub：[github.com/tristan666666/agent-island](https://github.com/tristan666666/agent-island)  
官网：[agent-island.dev](https://agent-island.dev)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Must Have: Agent Island — Start the Run, Go Live Your Life

> GitHub: [tristan666666/agent-island](https://github.com/tristan666666/agent-island) | Website: [agent-island.dev](https://agent-island.dev)  
> macOS 13+ (SwiftUI) | Windows 10+ (WPF) | MIT License  
> Install: `brew install tristan666666/tap/agentisland`

---

### The Problem It Solves

You kick off a Claude Code or Codex run, then go do something else — and miss the moment it stopped. Or you sit there babysitting it. Neither is great.

Agent Island's pitch: **start the run, go live your life. It calls you when it's your turn.**

---

### Where It Lives

On **Mac**: inside the MacBook notch (or compact top bar for non-notch machines). On **Windows**: native WPF top bar or floating widget. No Electron on either platform.

---

### Four Core Things

**1. Live session state in the notch.**  
Claude and Codex logos spin while sessions run, go still when done, pulse red when something's wrong. Detection is FSEvents-driven — ~1s latency from real stop.

| Logo | Meaning |
|------|---------|
| Spinning | Session active |
| Still | Idle / turn finished |
| Red pulse | Error / rate limit / auth issue |

**2. "It's your turn" alarm.**  
When a turn finishes: alarm window + system notification + sound. Dismisses automatically when you reply. Multiple finished turns queue.

**3. Out-of-quota alarm.**  
Different event, different alarm. Shows the reset countdown: "Resets at 15:55 (~2h)" — so you know exactly when to come back.

**4. Auto-resume on quota reset.**  
Attach a rule to a session: when Claude/Codex's usage window resets (or on a schedule), Agent Island sends a message (`continue`, `OK`, whatever you set) to pick the work back up — unattended, while you sleep.

Safety controls: global kill switch, per-project directory allow-list, full run log.

---

### Usage Island

Swipeable pages in the notch: live Claude + Codex 5-hour / weekly usage, cost, and reset countdowns. Re-auth button for expired Claude sessions opens the real authorize page in your browser — no terminal needed.

---

### Install

```bash
# macOS
brew install tristan666666/tap/agentisland

# Windows (winget)
winget install TristanTang.AgentIsland
```

Or grab the DMG / zip from [releases](https://github.com/tristan666666/agent-island/releases/latest).

---

### How It Works

Reads the transcript files Claude Code, Claude Desktop, and Codex write locally. Detects `stop_reason: end_turn` (Claude) and `task_complete` (Codex). Calls provider usage APIs with your existing local credentials. No telemetry, no data upload.

Fork of [codex-island](https://github.com/ericjypark/codex-island) (usage/cost foundation by Eric Park) — adds session state detection, turn alarms, auto-resume, and Windows.

GitHub: [github.com/tristan666666/agent-island](https://github.com/tristan666666/agent-island)

© 2026 Author: Mycelium Protocol
