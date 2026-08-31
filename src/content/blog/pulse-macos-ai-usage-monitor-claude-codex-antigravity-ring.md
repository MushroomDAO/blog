---
title: "Pulse：一排光环贴着屏幕边缘，告诉你 Claude Code 还剩多少"
titleEn: "Pulse: A Row of Rings at Your Screen Edge Tells You How Much Claude Code You Have Left"
description: "qunqin24/Pulse 开源，macOS 浮动监控工具，三个彩环实时显示 Claude Code / Codex / Antigravity 用量，贴边停靠收缩为6pt细条，从提供商账户直读真实限额，自适应刷新，无后台零上传，Apache 2.0。"
descriptionEn: "qunqin24/Pulse is an open-source macOS floating monitor: three color rings display real-time Claude Code / Codex / Antigravity usage limits, docks to screen edge and collapses to a 6pt sliver, reads real limits from provider accounts, adaptive refresh, zero backend, Apache 2.0."
pubDate: 2026-08-31
updatedDate: 2026-08-31
category: "Tech-News"
tags: ["macOS", "Claude Code", "Codex", "AI tools", "open source", "Swift", "usage monitor", "productivity", "menu bar"]
heroImage: "../../assets/images/pulse-macos-ai-usage-monitor-claude-codex-antigravity-ring-banner.jpg"
author: "Mycelium Protocol"
---

## 那个永恒的问题

你正在跑一个长任务，Claude Code 跑了一半，突然：**rate limited**。

不是因为你不知道有限额，是因为你没空时刻盯着用量面板。开着，要切换；关着，看不到。

**Pulse** 解决这一件事：让用量数字**一直在你视野里，不打扰你做别的事**。

---

## 一排光环，贴着屏幕边缘

Pulse 停靠在屏幕左边或右边——一条细轨道，三个光环，各代表一个 Agent：

- 🟢 绿色：充裕
- 🟡 琥珀色：注意
- 🔴 红色：快到头了

颜色比数字快，你**扫一眼就知道状态**，不需要读数字。

当你鼠标不在附近，整条轨道收缩成一根 **6pt 的细条**，几乎察觉不到，但它依然活着——快触限的时候那一条细线会变红，依然是个信号。点开，光环展开，详细数字立刻出现。

---

## 真实的限额，不是猜测

这是 Pulse 与其他"token 计数器"的根本区别：**数字从提供商账户直接读取**，不是本地 token 累加的估算。

三个 Agent 的读取路径各不相同：

| Agent | 读取方式 |
|---|---|
| **Claude Code** | 账户的 usage 端点（复用 Claude Code 已存储的登录凭证），降级到 status line |
| **Codex** | Codex 客户端自己使用的同一个端点，降级到 `codex app-server` |
| **Antigravity** | 编辑器在本地回环接口运行的语言服务器（只在 Antigravity 打开时有数据）|

读取失败时，Pulse 回退到上次成功的读数，并**标明读数的时间**，而不是把旧数据当成当前数据展示。

---

## 它知道你正在工作

Pulse 会在光环内侧显示一个标记，表示"这个 CLI 正在跑任务"。

关键在于这个判断怎么来的：不是"最近写了文件"，而是**从 transcript 的实际轮次边界来读**——一个慢速工具调用不会被误判为已完成的轮次。

---

## 用量花了多少钱

Settings 面板重建了一段花费历史——从 CLI 的会话日志里，按各提供商**公开的 API 定价**折算出来的。

还有一个单独标注的估算：**当前一个限速窗口值多少钱**。这是提供商不直接告诉你的数字，但你会想知道。

---

## 自适应刷新，不是固定轮询

刷新间隔在 2 到 30 分钟之间自动调整——没什么在动的时候，Pulse 自动退后，不做无意义的轮询。

---

## 隐私：没有后台

Pulse 没有服务器端。它只和你的 CLI 工具**已经在用**的端点通信，用**已经存储在 Mac 上**的凭证，用量历史**完全在本地**从磁盘日志算出。没有任何数据上传。

---

## 界面细节

- **三种尺寸**，适配不同屏幕和使用习惯
- **中英文切换**，不需要重启
- 支持 macOS 26 的 **Liquid Glass** 表面（可选）
- 不侵占其他 App 的全屏 Space
- Apple Silicon 和 Intel 均支持，macOS 14 Sonoma 及以上

---

## 来源：一个 Figma 设计稿

Pulse 的灵感来自 **Vinz（@hivinz_）** 2026年8月在 X 上发布的一张 Figma 概念设计——一排光环，贴着屏幕边缘，一眼看清所有限额。作者看到之后着手实现，整个核心的视觉语言都来自那张概念图。

---

## 安装

从 [GitHub Releases](https://github.com/qunqin24/Pulse/releases/latest) 下载最新的 `.dmg`，拖入 Applications。

由于尚未签名 Apple Developer ID，首次启动需要手动授权：

1. 打开 Pulse，macOS 拒绝——关掉弹窗
2. **系统设置 → 隐私与安全 → 安全性**，点击「仍然打开」
3. 再次打开确认

之后正常启动，后续版本会自动更新（集成了 Sparkle）。

**从源码构建：**

```bash
swift run Pulse       # 构建并运行
swift build           # 类型检查
./Scripts/bundle.sh   # → build.noindex/Pulse.app
./Scripts/dmg.sh      # → build.noindex/Pulse-<version>.dmg
```

---

## 总结

Pulse 做的是一件小但准确的事：**把 AI Coding 工具的用量限额，变成屏幕边缘一眼可见的信号，而不是你要主动去找的数字**。光环颜色比切换界面快，贴边停靠比悬浮窗口克制，从账户直读比本地估算可靠。

这类工具的价值在于**被动存在**——在你不注意它的时候，它帮你避开了那个"跑到一半撞上限速"的时刻。

**GitHub**: [qunqin24/Pulse](https://github.com/qunqin24/Pulse)  
**设计来源**: [@hivinz_ on X](https://x.com/hivinz_/status/2092996055248126353)  
**许可**: Apache 2.0

<!--EN-->

## Pulse: A Row of Rings at Your Screen Edge Tells You How Much Claude Code You Have Left

You're running a long task. Claude Code is halfway through. Then: **rate limited**.

Not because you didn't know the limit existed. Because you had no way to watch the usage panel without stopping what you were doing.

**Pulse** fixes this one thing: keep your usage numbers **permanently in view without interrupting your work**.

### A Rail of Rings, Docked to the Screen Edge

Pulse docks to the left or right edge of your screen — a thin rail, three rings, one per agent:

- 🟢 Green: plenty left
- 🟡 Amber: watch it
- 🔴 Red: nearly gone

Color registers faster than numbers. **A glance tells you where you stand.** When your cursor isn't nearby, the entire rail collapses to a **6pt sliver** — barely there, but still alive. If a limit is close, that sliver turns red. Hover near it and the rings expand with full details.

### Real Limits, Not Estimates

This is Pulse's key difference from "token counters": **numbers are read directly from provider accounts**, not calculated from local token accumulation.

Each agent uses a different route:

| Agent | Source |
|---|---|
| **Claude Code** | Account usage endpoint (reuses credentials Claude Code already stored), fallback to status line |
| **Codex** | Same endpoint Codex's own client uses, fallback to `codex app-server` |
| **Antigravity** | Language server running on loopback interface (only available while Antigravity is open) |

When a read fails, Pulse falls back to the last good reading and **shows when it was taken** — rather than presenting stale data as current.

### It Knows When You're Working

Pulse shows an indicator mark inside a ring while that CLI is mid-turn.

The key: this is read from the **transcript's actual turn boundaries**, not from "wrote to a file recently." A slow tool call doesn't look like a finished turn.

### What It Cost You

The Settings panel reconstructs a spending history from CLI session logs, priced at each provider's **published API rates**. Plus a separately labelled estimate of what the current rate-limit window is worth — a number providers don't report, but one you'd want to know.

### Adaptive Refresh

Refresh interval adjusts between 2 and 30 minutes automatically — when nothing is moving, Pulse backs off rather than polling on a fixed clock.

### Privacy: No Backend

Pulse has no server. It talks only to endpoints your own CLIs already use, with credentials already stored on your Mac. Usage history is computed entirely on-device from log files already on disk. Nothing is uploaded anywhere.

### Interface Details

- Three sizes, adapts to different screens and preferences
- English and Simplified Chinese, switchable without relaunch
- Optional **Liquid Glass** surface on macOS 26
- Stays out of other apps' full-screen Spaces
- Apple Silicon and Intel, macOS 14 Sonoma or newer

### Origin: A Figma Concept

Pulse's design comes from a Figma concept **Vinz (@hivinz_)** posted on X in August 2026 — a rail of rings held against the screen edge, everything worth knowing in one glance. The author saw it, built an implementation, and the core visual language is entirely Vinz's idea.

### Install

Download the latest `.dmg` from [GitHub Releases](https://github.com/qunqin24/Pulse/releases/latest) and drag to Applications.

Not yet signed with an Apple Developer ID, so first launch requires manual approval:

1. Open Pulse — macOS refuses, dismiss the dialog
2. **System Settings → Privacy & Security → Security**, click **Open Anyway**
3. Open again and confirm

After that it launches normally. Later versions install automatically via Sparkle.

```bash
# Build from source
swift run Pulse       # build and run
swift build           # type-check
./Scripts/bundle.sh   # → build.noindex/Pulse.app
```

### Summary

Pulse does one small, precise thing: **turns AI coding tool usage limits into a passive signal at the edge of your screen** — not a dashboard you go look at. Color rings register faster than switching windows. Screen-edge docking is more discreet than a floating widget. Reading from provider accounts is more reliable than local token estimates. The value is in the passive presence — in the "hit rate limit mid-task" moment it quietly prevents.

**GitHub**: [qunqin24/Pulse](https://github.com/qunqin24/Pulse)  
**Design concept**: [@hivinz_ on X](https://x.com/hivinz_/status/2092996055248126353)  
**License**: Apache 2.0
