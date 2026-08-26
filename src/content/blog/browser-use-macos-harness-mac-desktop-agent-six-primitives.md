---
title: "macOS Harness：Browser Use 出品，六个原始 API 给 LLM 完整 Mac 控制权，无框架、无模板、无工具预置"
titleEn: "browser-use-macos-harness-mac-desktop-agent-six-primitives"
description: "macOS Harness 是 Browser Use 团队（主仓库 110k Star）开源的最薄 Mac 桌面 Agent 框架。核心设计：不预置任何应用专属工具，给 LLM 六个原始 API（see/key/type/click/ax/script），让 Agent 在任务执行过程中自行编写缺失的逻辑。一个 Python 进程直接连接 macOS 原生层（CGWindow/CGEvent/AX/AppleEvents）+ 真实 Chrome（CDP）+ 文件系统。不激活、不聚焦目标窗口，不移动物理鼠标。772 Star，MIT，2026-08-17 发布。"
descriptionEn: "macOS Harness is the thinnest Mac desktop agent harness from the Browser Use team (main repo 110k stars). Core design: no app-specific tools preloaded — the LLM gets six raw primitives (see/key/type/click/ax/script) and writes missing logic mid-task. One Python process connected directly to macOS native layer (CGWindow/CGEvent/AX/AppleEvents) + real Chrome (CDP) + filesystem. Never activates or focuses the target window, never moves the physical cursor. 772 stars, MIT, released 2026-08-17."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Tech-News"
tags: ["开源", "macOS", "AI Agent", "Computer-Use", "Browser Use", "桌面自动化", "LLM", "Python"]
heroImage: "../../assets/images/browser-use-macos-harness-mac-desktop-agent-six-primitives-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：browser-use/macos-harness ⭐ 772 | Forks 51 | Python | MIT  
来自：Browser Use 团队（browser-use/browser-use ⭐ 110,553）  
发布：2026-08-17 | 实验性，仅限 macOS

---

## 背景：Browser Use 的自然延伸

Browser Use 主仓库（browser-use/browser-use）是目前最流行的浏览器自动化 Agent 框架之一，11 万 Star，让 AI Agent 在浏览器里完成各种网页任务。

现在同一个团队出了 macOS Harness——把能力边界从浏览器扩展到整个 Mac 桌面。

---

## 一个问题，一个答案

**问题**：现有的计算机操控 Agent（CUA）方案几乎都依赖预置的工具接口——浏览器插件、应用专用 API、人工写好的操作流程。遇到没有适配过的软件，Agent 就卡住了。

**macOS Harness 的答案**：不要预置工具。给 LLM 六个原始 API，让它在执行过程中自己写缺失的逻辑。

```text
● agent: 想做某件事，但没有对应的工具
│
● 看到 app 界面，使用 macOS 底层原始接口
│
● 在任务进行中写出缺失的逻辑
│
✓ 任务完成                     ——没有添加任何应用专属工具
```

---

## 六个原始 API，整台 Mac

```python
macos-harness <<'PY'
# 捕获 Spotify 窗口截图（不激活、不置前）
frame = mac.see("Spotify")

# 发送键盘快捷键到指定 app PID
mac.key("cmd+k", app="Spotify")

# 在指定 app 里输入文字
mac.type("Alessia Cara", app="Spotify")

# 在指定 app 坐标点击
mac.click(640, 420, app="Spotify")

# 读取坐标处的 Apple Accessibility 树节点
item = mac.ax.at(640, 420, app="Spotify")

# 执行 AppleScript
mac.script('tell application "Spotify" to play')

# 同一进程里，这些也可以用：
print(browser.page_info())          # 真实 Chrome（已登录）
print(list(Path.home().iterdir()))  # 文件系统
PY
```

六个原始 API：`see`、`key`、`type`、`click`、`ax`、`script`。没有 Spotify 工具、没有 Slack 工具、没有 Final Cut 工具。模型拿到的是原始接口，其余的自己写。

---

## 技术架构

一个持久的 Python 进程，直接接入 macOS 底层：

```text
                    一个持久 Python 进程
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
      mac.*            browser.*        Path / subprocess
         │                  │                  │
 ┌───────┼───────┐      Browser Harness      文件 + shell
 │       │       │            │
CGWindow CGEvent AX + Apple   CDP
截图     到PID   Events        │
         │       │         真实 Chrome
 └───────┴───────┘（已登录）
         │
  原生 + Electron 应用
```

**关键设计细节：**

- **后台捕获**：`mac.see()` 抓取应用窗口，不需要把它置到前台
- **精准输入**：键盘和鼠标事件直接发送到目标 app 的 PID，不影响当前前台窗口
- **虚拟指针**：用动画可穿透指针可视化点击位置，不移动你的真实鼠标
- **双层视觉**：`mac.see()` 是截图（视觉），`mac.ax` 是 Accessibility 树（语义）——视觉不够用的时候上 AX
- **真实浏览器**：接入真实的、已登录的 Chrome，不是无头浏览器，通过 CDP 控制

---

## 安装

两种方式，推荐第一种：

**让 Agent 自己装（粘贴到 Codex 或 Claude Code）：**

```text
Install or upgrade macOS Harness from https://github.com/browser-use/macos-harness 
with uv using Python 3.12. Register the skill printed by `macos-harness skill`, 
then run `macos-harness doctor`. Explain any missing macOS permissions and ask before 
requesting them. Finally, verify the harness by capturing one already-running app 
without bringing it to the foreground.
```

Agent 会自行安装包、学习工作流、检查权限、验证连接。

**手动安装：**

```bash
uv tool install --python 3.12 --upgrade --force macos-harness

# 注册到 Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/macos-harness"
macos-harness skill > "${CODEX_HOME:-$HOME/.codex}/skills/macos-harness/SKILL.md"

# 注册到 Claude Code
# macos-harness skill > ~/.claude/skills/macos-harness/SKILL.md

# 检查权限
macos-harness doctor
```

**需要的 macOS 权限**（`doctor` 命令会报告实际需要的）：
- 辅助功能（Accessibility）
- 屏幕录制（Screen Recording）
- 自动化（Automation）
- **不需要** Input Monitoring

验证安装：

```bash
macos-harness <<'PY'
print(mac.see("Finder"))
PY
```

---

## 遥测说明

默认启用匿名遥测，只记录：CLI 命令类别、成功/失败、耗时、包版本、OS/架构、检测到的 Agent 客户端。**不记录**：prompt、应用名、截图、UI 文字、脚本、路径、窗口标题。

```bash
macos-harness telemetry disable  # 一行关闭
```

---

## 为什么值得关注

现有 CUA 框架的两种路径：
- **重量级**（OSWorld、CUA-Lite 等）：VM 或容器，完整基准测试，研究向
- **应用专属**（Zapier/Make 等）：预写好的自动化流程，缺应用就缺功能

macOS Harness 走第三条路：**薄层原始接口 + 让 LLM 在线生成代码**。

这个设计和 Browser Use 处理浏览器的思路一脉相承——不预置"点击搜索框""填表单"这类工具，而是给原始的浏览器接口，让模型自己决定怎么做。从浏览器到桌面，从 DOM 操作到 CGWindow + AX，逻辑相同。

对于需要跨应用、跨窗口完成任务的 Agent（比如从 Notion 读数据、写进 Figma、再发邮件），这套原始接口理论上覆盖 Mac 上的任何软件——只要模型能看图、能写 Python。

---

**相关链接**

- GitHub（macOS Harness）：https://github.com/browser-use/macos-harness
- GitHub（Browser Use 主仓库）：https://github.com/browser-use/browser-use

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## macOS Harness: Browser Use Gives LLMs a Mac — Six Primitives, No Recipes, No Tools Preloaded

*by Mycelium Protocol*

---

GitHub: browser-use/macos-harness ⭐ 772 | Forks 51 | Python | MIT  
From: Browser Use team (browser-use/browser-use ⭐ 110,553)  
Released: 2026-08-17 | Experimental, macOS only

---

### Context: The Natural Extension of Browser Use

Browser Use (browser-use/browser-use, 110k stars) is one of the most popular browser automation agent frameworks — it gives AI agents the ability to complete web tasks in a real browser.

macOS Harness extends the same idea from browser to the full Mac desktop.

---

### The Problem and the Answer

**The problem**: Most computer-use agent (CUA) setups rely on pre-built tool interfaces — browser plugins, application-specific APIs, manually written operation flows. When the agent encounters software it doesn't have an adapter for, it stops.

**macOS Harness's answer**: Don't preload any tools. Give the LLM six raw primitives and let it write the missing logic mid-task.

```text
● agent: wants to do something no helper exists for
│
● sees the app and uses raw macOS primitives  
│
● writes the missing logic in ordinary Python
│
✓ task complete                    — no app-specific tool added
```

---

### Six Primitives. The Whole Mac.

```python
macos-harness <<'PY'
# Capture Spotify window (background, no foreground activation)
frame = mac.see("Spotify")

# Send keyboard shortcut to specific app PID
mac.key("cmd+k", app="Spotify")

# Type text in a specific app
mac.type("Alessia Cara", app="Spotify")

# Click at coordinates in a specific app
mac.click(640, 420, app="Spotify")

# Read Apple Accessibility tree at a coordinate
item = mac.ax.at(640, 420, app="Spotify")

# Execute AppleScript
mac.script('tell application "Spotify" to play')

# Same process — these also available:
print(browser.page_info())         # real Chrome, logged in
print(list(Path.home().iterdir())) # filesystem
PY
```

Six primitives: `see`, `key`, `type`, `click`, `ax`, `script`. No Spotify tools. No Slack tools. No Final Cut tools. The model gets raw interfaces and writes the rest.

---

### Technical Architecture

One persistent Python process, directly connected to the macOS native layer:

```text
                    one persistent Python process
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
      mac.*              browser.*         Path / subprocess
         │                    │                    │
 ┌───────┼───────┐       Browser Harness      files + shell
 │       │       │             │
CGWindow CGEvent AX + Apple    CDP
screens  to PID  Events         │
         │       │          real Chrome (logged in)
 └───────┴───────┘
         │
  native + Electron apps
```

**Key design choices:**

- **Background capture**: `mac.see()` grabs app windows without bringing them forward
- **Targeted input**: keyboard and mouse events go directly to the target app's PID, without affecting the frontmost window
- **Virtual pointer**: an animated, click-through overlay shows where clicks land without moving the physical cursor
- **Two-layer vision**: `mac.see()` for screenshots (visual), `mac.ax` for the Accessibility tree (semantic) — use ax when vision isn't enough
- **Real browser**: connects to real, logged-in Chrome via CDP, not a headless instance

---

### Install

**Let the agent install it** (paste into Codex or Claude Code):

```text
Install or upgrade macOS Harness from https://github.com/browser-use/macos-harness 
with uv using Python 3.12. Register the skill printed by `macos-harness skill`, 
then run `macos-harness doctor`. Explain any missing macOS permissions and ask before 
requesting them. Finally, verify the harness by capturing one already-running app 
without bringing it to the foreground.
```

The agent installs the package, teaches itself the workflow, checks permissions, and verifies the connection.

**Manual install:**

```bash
uv tool install --python 3.12 --upgrade --force macos-harness
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/macos-harness"
macos-harness skill > "${CODEX_HOME:-$HOME/.codex}/skills/macos-harness/SKILL.md"
macos-harness doctor
```

**macOS permissions required** (`doctor` reports exactly what's needed):
- Accessibility
- Screen Recording
- Automation
- **NOT** Input Monitoring

**Verify:**
```bash
macos-harness <<'PY'
print(mac.see("Finder"))
PY
```

---

### Telemetry

Anonymous by default. Records only: CLI command category, success/failure, duration, package version, OS/architecture, detected agent client. **Never records**: prompts, app names, screenshots, UI text, scripts, paths, or window titles.

```bash
macos-harness telemetry disable
```

---

### Why It Matters

Existing CUA frameworks fall into two camps:
- **Heavy** (OSWorld, CUA-Lite, etc.): VMs or containers, complete benchmark suites, research-oriented
- **App-specific** (Zapier/Make, etc.): pre-written automation flows — missing an app means missing a feature

macOS Harness takes a third path: **thin raw primitives + let the LLM generate code on the fly**.

This matches how Browser Use handles the browser — rather than preloading "click search box" or "fill form" tools, it gives raw browser interfaces and lets the model decide what to do. Browser → desktop; DOM manipulation → CGWindow + AX. Same philosophy.

For agents that need to cross application boundaries — read from Notion, write to Figma, send an email — this set of raw primitives theoretically covers any Mac software, as long as the model can interpret a screenshot and write Python.

9 days old, 772 stars. The Browser Use team's track record (110k on the main repo) makes this one worth watching.

---

**Links**

- GitHub (macOS Harness): https://github.com/browser-use/macos-harness
- GitHub (Browser Use): https://github.com/browser-use/browser-use

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
