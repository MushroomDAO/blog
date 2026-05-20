---
title: "清华开源 Syll：不是聊天机器人，是住在你桌面角落的 AI 伙伴"
titleEn: "Tsinghua Open-Sources Syll: Not a Chatbot — An AI Companion That Lives at the Edge of Your Desktop"
description: "清华 SAGE 实验室开源 Syll，一个自托管 AI companion runtime。它不主动打扰你，却悄悄记住你未完成的事：定时早报、Markdown 技能包、GUI 工作流录制、桌面幽灵图标、多端收发消息。Python + FastAPI，pip 一行安装，本地 Ollama 或云端模型均可驱动。"
descriptionEn: "Tsinghua SAGE Lab open-sources Syll, a self-hosted AI companion runtime. It doesn't nag you — it quietly tends to unfinished tasks: scheduled rituals, editable markdown skills, GUI workflow recording, a desktop ghost, and multi-channel messaging. Python + FastAPI, one-line pip install, runs on local Ollama or any cloud model."
pubDate: "2026-05-15"
updatedDate: "2026-05-15"
category: "Tech-News"
tags: ["Syll", "清华", "AI伴侣", "自托管", "desktop agent", "开源", "companion runtime", "THU-SAGE", "本地AI", "workflow automation"]
heroImage: "../../assets/banner-ai-personal-assistant.jpg"
---

**结论先行（BLUF）**：清华 SAGE 实验室发布开源项目 [Syll](https://github.com/THU-SAGE/syll)，定位是"自托管 AI companion runtime"——不是普通聊天机器人，而是长期驻留在你桌面边缘、悄悄照看未完成事务的 AI 伙伴。MIT 协议，Python 写成，pip 一行安装，本地模型（Ollama/vLLM）或云端 API 均可驱动。

- **GitHub**：[THU-SAGE/syll](https://github.com/THU-SAGE/syll)
- **主页**：[thu-sage.github.io/syll](https://thu-sage.github.io/syll/)
- **协议**：MIT，完全开源

---

## Syll 在解决什么问题

你有没有遇到过这种情况：打开电脑，发现上次的半截草稿还在，那个一直没时间整理的下载文件夹还在，那个说要提醒自己的事情早就忘了。

Syll 的出发点不是"更强的助手"，而是"更低调的陪伴"——它不弹窗、不催你，只是静静记录、定时提醒、在你问它的时候给出答案。

---

## 核心功能拆解

**多端消息收发**：Web UI、CLI、Telegram、飞书、Discord、WhatsApp 均可接入。你在手机上发一条消息，它从桌面帮你找到那个文件、执行那个脚本。

**Proactive Rituals（主动仪式）**：可配置的定时任务，比如每天早上发送一条今日日程摘要，晚上发送一条"你今天还有什么没做完"。不是烦人的通知，是你自己设定的节奏。

**Markdown 技能包**：用 Markdown 文件教 Syll 新技能——写一个文件描述"如何整理我的下载文件夹"，它下次收到相关指令时自动加载这段说明。技能可随时编辑，不需要重新训练模型。

**GUI 工作流录制**：录制一次桌面操作，之后定时重放或按需触发。截图感知屏幕状态，坐标校准后控制鼠标键盘，不依赖特定 App 的 API。

**Desktop Ghost（桌面幽灵）**：可选的无边框桌面图标，实时镜像 Syll 的状态，感知你的活动。叫它"桌宠"也行，但它不只是装饰——它是 companion 状态的实时窗口。

**Memory Workspace（记忆空间）**：分层笔记系统，长期记忆 + 每日碎片 + 活动热力图。你不需要主动整理，Syll 自己维护这张图。

---

## 架构与技术栈

```
Channels（多端接入）
    ↓
MessageBus（统一路由）
    ↓
AgentLoop（组装上下文 → 调 LLM → 调工具）
    ↓
Tools（文件、Shell、网页、截图、GUI 控制）
CronService（定时任务 / Rituals）
```

- **语言**：Python 3.11+
- **Web 框架**：FastAPI + Alpine.js
- **桌面 GUI**：PyQt6 + 内嵌 Chromium
- **LLM 接入**：LiteLLM（支持 OpenAI、Anthropic、OpenRouter、本地 Ollama/vLLM）

---

## 五分钟跑起来

```bash
pip install syll
syll onboard   # 初始化配置，填入模型 API key
syll wake      # 启动，访问 http://localhost:18790
```

想用本地模型？在 `~/.syll/config.json` 把 `model` 换成 `ollama/qwen2.5` 或任何 LiteLLM 支持的格式即可。

---

## 落地建议

Syll 不适合"完成一次性任务"，它的价值在于**长期驻留**。几个最值得尝试的场景：

1. **手机遥控桌面取文件**：你在外面，想要桌面某个文档，发消息给 Syll 的 Telegram 频道，它找到后回传。
2. **录制重复 GUI 操作**：每天要打开某个网页填表？录一次，让 Syll 定时帮你跑。
3. **用 Markdown 技能包替代 prompt**：把你常用的复杂指令写成 `.md` 文件，Syll 需要时自动加载，比每次粘贴 prompt 干净得多。
4. **早报 Ritual**：配置一条每天 8:00 的 Ritual，让 Syll 总结今日待办、天气、未读消息，发到你手机。

---

## 为什么值得关注

Syll 代表的不是"更强的 AI"，而是**AI 与日常工作节奏的深度融合**——不打断你、不依赖你主动触发、在后台默默维护你的上下文。这个方向和那些"越来越强大的助手"形成了有趣的对比：有时候你需要的不是更聪明，而是更懂你的节奏。

**参考链接**
- [GitHub - THU-SAGE/syll](https://github.com/THU-SAGE/syll)
- [Syll 项目主页](https://thu-sage.github.io/syll/)
- [Demo：录制工作流](https://thu-sage.github.io/syll/media/demo/demo-1-recorded-workflow.mp4)
- [Demo：手机取桌面文件](https://thu-sage.github.io/syll/media/demo/demo-3-phone-file-return.mp4)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Tsinghua SAGE Lab open-sources [Syll](https://github.com/THU-SAGE/syll), a self-hosted AI companion runtime. It's not a chatbot — it's an AI that quietly tends to unfinished tasks at the edge of your desktop. MIT license, written in Python, one-line pip install, runs on local Ollama or any cloud API.

- **GitHub**: [THU-SAGE/syll](https://github.com/THU-SAGE/syll)
- **Homepage**: [thu-sage.github.io/syll](https://thu-sage.github.io/syll/)
- **License**: MIT

---

## What Syll Solves

Half-finished drafts. The download folder you never sorted. The reminder you forgot to set. Syll doesn't interrupt you or demand attention — it quietly records, schedules reminders, and answers when asked.

---

## Core Features

**Multi-channel messaging**: Web UI, CLI, Telegram, Feishu, Discord, WhatsApp. Send a message from your phone; Syll finds the file on your desktop and sends it back.

**Proactive Rituals**: Configurable scheduled messages — morning briefings, evening "what's unfinished" nudges. Your rhythm, your rules.

**Markdown Skills**: Teach Syll new procedures by writing a `.md` file. It loads the instructions when relevant, no retraining required.

**GUI Workflow Recording**: Record a desktop routine once; replay it on schedule or on demand. Screenshot-based screen awareness, coordinate-calibrated mouse/keyboard control, no app-specific API needed.

**Desktop Ghost**: An optional frameless desktop mascot that mirrors Syll's state and reacts to your activity.

**Memory Workspace**: Layered notes — long-term memory, daily fragments, activity heatmaps. Maintained automatically.

---

## Architecture

```
Channels → MessageBus → AgentLoop → Tools / CronService
```

- **Language**: Python 3.11+
- **Web**: FastAPI + Alpine.js
- **Desktop GUI**: PyQt6 + embedded Chromium
- **LLM**: LiteLLM (OpenAI, Anthropic, OpenRouter, local Ollama/vLLM)

---

## Quickstart

```bash
pip install syll
syll onboard   # configure model API key
syll wake      # open http://localhost:18790
```

To use a local model, set `"model": "ollama/qwen2.5"` in `~/.syll/config.json`.

---

## Practical Use Cases

1. **Remote file retrieval**: Message Syll from your phone → it finds the file on your desktop and sends it back.
2. **Automate repetitive GUI tasks**: Record once, replay on schedule.
3. **Markdown skills as reusable prompts**: Write complex instructions as `.md` files; cleaner than copy-pasting prompts every time.
4. **Morning ritual**: 8am daily summary of todos, weather, unread messages — pushed to your phone.

---

## Why It Matters

Syll isn't chasing "more powerful AI" — it's about **deep integration with your daily work rhythm**: non-intrusive, always-on, maintaining your context in the background. Sometimes you don't need smarter — you need something that knows your pace.

**References**
- [GitHub - THU-SAGE/syll](https://github.com/THU-SAGE/syll)
- [Syll Homepage](https://thu-sage.github.io/syll/)
- [Demo: Recorded Workflow](https://thu-sage.github.io/syll/media/demo/demo-1-recorded-workflow.mp4)
- [Demo: Phone-to-Desktop File Retrieval](https://thu-sage.github.io/syll/media/demo/demo-3-phone-file-return.mp4)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
