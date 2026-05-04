---
title: "lil agents：住在 Mac Dock 上的 AI 桌面伴侣"
titleEn: "lil agents: Tiny AI Companions That Live on Your Mac Dock"
description: "lil agents 是一个开源 macOS 应用，两个会走路的卡通角色 Bruce 和 Jazz 住在你的 Dock 上方，点击打开 AI 终端，支持 Claude Code、OpenAI Codex、GitHub Copilot、Google Gemini，完全本地运行，无数据收集。"
descriptionEn: "lil agents is an open-source macOS app where two animated characters, Bruce and Jazz, walk above your Dock. Click one to open an AI terminal supporting Claude Code, OpenAI Codex, GitHub Copilot, or Google Gemini — fully local, no data collection."
pubDate: "2026-05-04"
updatedDate: "2026-05-04"
category: "Tech-News"
tags: ["macOS", "Claude Code", "AI工具", "桌面应用", "开源", "Gemini", "Codex"]
heroImage: "../../assets/images/lil-agents-desktop-companion.jpg"
---

**结论先行（BLUF）**：lil agents 是一个 macOS 开源应用，两个可爱的卡通角色住在你的 Dock 上方来回走动。点击其中一个，弹出 AI 终端——支持 Claude Code、OpenAI Codex、GitHub Copilot、Google Gemini 四种 CLI，从菜单栏随时切换。完全本地运行，MIT 开源，macOS Sonoma 以上可用。

---

## 它做了一件小事，但做得很好

有些工具不追求功能全面，只做一件小事做到位。

lil agents 就是这类。它的定位很清楚：**让你常用的 AI CLI 工具，多一个有性格的入口**。

两个角色 **Bruce** 和 **Jazz**，用透明 HEVC 视频渲染，悬浮在 Mac Dock 上方走来走去。你在专注工作，它们在那儿晃着；你需要问 AI，点一下就弹出终端。

项目主页：[lilagents.xyz](https://lilagents.xyz)  
GitHub：[github.com/ryanstephen/lil-agents](https://github.com/ryanstephen/lil-agents)

---

## 核心功能

**多 AI CLI 支持，菜单栏切换**

一个应用接入四条线：

| CLI | 安装方式 |
|-----|---------|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| sh` |
| OpenAI Codex | `npm install -g @openai/codex` |
| GitHub Copilot | `brew install copilot-cli` |
| Google Gemini | `npm install -g @google/gemini-cli` |

安装好对应 CLI 后，在菜单栏选择用哪个，角色会帮你打开对应的终端会话。

**有性格的交互细节**

- 等待 AI 响应时，角色头顶会出现"思考气泡"，配上随机的趣味文案
- 响应完成有音效
- 弹出的聊天窗有四种视觉主题：Peach / Midnight / Cloud / Moss
- 支持 `/clear`、`/copy`、`/help` 斜杠命令
- 标题栏有"复制上条回复"按钮

**完全本地，没有数据收集**

> lil agents runs entirely on your Mac and sends no personal data anywhere.

应用本身只做两件事：播放内置动画、计算 Dock 尺寸来定位角色。不拦截、不存储、不传输你的对话内容。AI 交互全部由你本地安装的 CLI 处理，lil agents 只是那个"门"。没有账号，没有登录，没有埋点。

---

## 适合谁

- 每天都在用 Claude Code 或其他 AI CLI，想要一个更有温度的触发入口
- 喜欢在桌面上放点有趣的东西，但不想要太占屏幕的 widget
- 在多个 AI 工具之间切换，希望统一在一个地方管理

---

## 技术规格

- **系统要求**：macOS Sonoma 14.0+，含 Sequoia 15.x
- **架构**：Universal Binary，Apple Silicon + Intel 原生运行
- **动画方案**：透明背景 HEVC 视频，渲染角色走路动效
- **更新机制**：Sparkle 自动更新
- **许可证**：MIT，源码开放

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: lil agents is an open-source macOS app that puts two animated characters — Bruce and Jazz — on your Dock. Click one to open an AI terminal connected to Claude Code, OpenAI Codex, GitHub Copilot, or Google Gemini. Fully local, MIT licensed, macOS Sonoma and up.

---

## One Small Thing, Done Well

lil agents has a clear purpose: **give your daily AI CLI tools a personality**.

Bruce and Jazz — rendered from transparent HEVC video — walk back and forth above your Mac Dock. When you need AI, you click one and a themed terminal pops up. When you don't, they just vibe there.

Project site: [lilagents.xyz](https://lilagents.xyz)  
GitHub: [github.com/ryanstephen/lil-agents](https://github.com/ryanstephen/lil-agents)

---

## What It Does

**Four AI CLIs, one menubar switcher**

Supports Claude Code, OpenAI Codex, GitHub Copilot, and Google Gemini — each requires only the corresponding CLI installed locally. Switch between them from the menubar anytime.

**Character interactions with personality**

- Thinking bubbles with playful phrases while the agent works
- Completion sound effects
- Four visual themes: Peach, Midnight, Cloud, Moss
- Slash commands: `/clear`, `/copy`, `/help`
- Copy last response button in the title bar

**Fully local, zero data collection**

The app only does two things: play bundled animations and calculate your dock size for character positioning. Your conversations are handled entirely by the CLI process you chose — lil agents doesn't intercept, store, or transmit anything. No accounts, no login, no analytics.

---

## Who It's For

- Daily Claude Code or AI CLI users who want a more tactile, personality-driven entry point
- People who like having something alive on their desktop without a heavy widget
- Anyone juggling multiple AI tools who wants a unified launcher with a sense of character

---

## Specs

- **Requires**: macOS Sonoma 14.0+, including Sequoia 15.x
- **Architecture**: Universal Binary — native on Apple Silicon and Intel
- **Animation**: Transparent-background HEVC video rendering
- **Updates**: Sparkle auto-update
- **License**: MIT

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
