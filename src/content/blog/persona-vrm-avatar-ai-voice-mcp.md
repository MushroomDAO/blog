---
title: "Persona：给AI语音助手装上一张会动的脸，通过MCP连接Codex"
titleEn: "persona-vrm-avatar-ai-voice-mcp"
description: "xikhar 开源了 Persona，一个跨平台桌面 VRM 角色应用，监听 Codex/ChatGPT 的音频输出，实时驱动嘴型同步和肢体动画。通过 MCP 暴露动画控制接口，AI Agent 可以直接调用 play_animation 让角色表达情绪。3天 680 星，MIT，支持 Linux/Windows/macOS。"
descriptionEn: "xikhar open-sources Persona, a cross-platform desktop VRM character that listens to Codex/ChatGPT audio output and drives real-time lip sync and body animation. MCP server at port 47831 lets AI agents trigger named animations. 680 stars in 3 days, MIT, Linux/Windows/macOS."
pubDate: "2026-07-31"
updatedDate: "2026-07-31"
category: "Tech-News"
tags: ["VRM", "AI语音", "MCP", "桌面应用", "Electron", "Three.js", "Codex", "Mycelium"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

*by Mycelium Protocol*

---

AI 语音交互缺少的一件事：**一张脸**。

对话在进行，声音从扬声器里出来，但屏幕上什么都没有——没有眼神，没有表情，没有肢体语言。这不像在和一个存在者交流，更像在等一个返回值。

**[Persona](https://github.com/xikhar/persona)**（xikhar）就是为了补这个缺口，三天前发布，680 星，MIT。

---

## 它做什么

Persona 是一个 Electron 桌面应用，在你工作时悬浮在屏幕上，显示一个 VRM 3D 角色。当 Codex 或 ChatGPT 语音输出时，角色自动做嘴型同步和肢体动作；通过 MCP，AI Agent 还能主动触发命名动画——比如"思考""激动""挥手"。

架构分四层，职责很窄：

```
Native listeners   ← 系统音频捕获，仅计算 RMS 振幅，立即丢弃样本
Electron 主进程   ← 生命周期、托盘、MCP 服务器、URL 协议
Sandboxed preload ← 仅暴露归一化事件和狭窄设置操作
React + Three.js  ← VRM 渲染、VRMA 动画混合、表情驱动
```

渲染层没有文件系统、进程或原始音频访问权限。

---

## 隐私优先的音频捕获

Persona 监听的是 AI 应用的**输出音频**，不是麦克风。三个平台各有方案：

**Linux（PipeWire）：** 轮询 PipeWire 图寻找 Codex/ChatGPT 播放节点，挂上 `pw-record` 捕获那一条流，内存中计算 RMS 振幅，每个样本计算完立即丢弃。

**Windows（WASAPI loopback）：** 使用 `PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE`，仅捕获目标进程树的音频，其他应用的声音完全排除。需要 Windows 10 build 20348+。

**macOS（Core Audio process tap）：** 为目标进程创建私有的、非静音的 Core Audio tap 和私有聚合设备，需要 macOS 14.2+ 和一次"系统音频录制"权限授权。

Persona 不捕获麦克风，不保存音频，不转录内容，不发送任何音频数据到网络。唯一用途：计算音量振幅驱动嘴型。

---

## MCP 接口：Agent 控制角色

Persona 在 `127.0.0.1:47831/mcp` 运行一个 Streamable HTTP MCP 服务端。注册到 Codex：

```bash
codex mcp add persona --url http://127.0.0.1:47831/mcp
```

暴露四个工具：

| 工具 | 用途 |
|------|------|
| `play_animation` | 播放指定名称的动画（随机选一个 clip） |
| `list_animations` | 列出所有可用动画及其描述和触发场景 |
| `control_window` | show / hide / toggle 角色窗口 |
| `get_status` | 读取模型就绪状态、窗口可见性、语音状态 |

每个自定义动画在创建时都要填写名称、描述和**触发场景**——这段元数据会直接暴露给连接的 Agent，让 AI 理解"什么情况下播放这个动作"。目录更新时，MCP 会立即推送工具列表变更通知给所有连接的 session。

---

## 动画系统

Persona 有两个永久动作槽：

- **Idle**：闲置姿态
- **Speaking**：说话时的肢体动作

每个槽都可以上传多个 `.vrma` 文件，Persona 在触发时随机选一个。自定义动作通过 Settings 面板创建，和 Idle/Speaking 一样可以放多个 clip。

MCP 触发的动画优先于音频驱动的肢体动作，但嘴型同步会继续——也就是说，AI Agent 可以让角色在"说话同时做波浪手"。动画播完后，自动回到当前的 idle/speaking 状态。

用户导入的 VRM/VRMA 文件存储在 Electron 的 per-user 应用数据目录，通过锁定的 `persona-asset:` 协议访问——渲染层不能把这个协议当成任意文件系统读取器。

---

## URL 协议

安装包注册了 `persona://` 协议，适合其他本地应用直接驱动角色状态：

```bash
open "persona://speaking?level=0.3"   # macOS
xdg-open "persona://thinking"          # Linux
start "persona://animation?name=wave1" # Windows
```

支持的状态：`listening` / `thinking` / `speaking?level=` / `inactive` / `show` / `hide` / `toggle` / `animation?name=`。

---

## 本地跑起来

```bash
# 环境要求：Node.js 24+
git clone https://github.com/xikhar/persona.git
cd persona

# 激活示例角色（仓库里的测试 VRM）
cp public/assets/library.json.example public/assets/library.json
cp public/assets/manifest.json.example public/assets/manifest.json

npm install
npm run demo
```

正式发布版的角色库是空的（版权原因），首次启动直接进 Settings，导入你自己的 `.vrm` 文件即可。任何符合 VRM 规范的角色都能用。

---

## 三天 680 星的原因

Persona 解决的问题不大，但击中了一个很真实的痛点：语音 AI 太"无形"了。

当你和 Codex 对话，它给你解释一段复杂代码，你希望有东西在那边"看着你"——不是一个进度条，不是一段打字动画，是一个有眼神、有表情、能感知声音的存在者。

这不是功能需求，是情感需求。Persona 用 VRM + MCP + 音频 tap 的组合，给这个需求一个具体的、可扩展的技术答案。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Persona: A VRM Avatar That Listens to Your AI Agent's Voice

*by Mycelium Protocol*

AI voice interaction is missing one thing: **a face**.

The conversation is happening, sound is coming from the speakers, but the screen shows nothing — no eye contact, no expression, no body language. It doesn't feel like talking to a presence; it feels like waiting for a return value.

**[Persona](https://github.com/xikhar/persona)** (xikhar) was built to close that gap. 680 stars in three days, MIT license.

### What It Does

Persona is an Electron desktop app that floats over your workspace displaying a VRM 3D character. When Codex or ChatGPT produces voice output, the character automatically performs lip sync and body motion. Through an MCP server, AI agents can also proactively trigger named animations — thinking, excited, waving.

The architecture has four intentionally narrow layers:

```
Native listeners   ← OS audio capture; calculates RMS amplitude only; discards every sample
Electron main      ← lifecycle, tray, MCP server, URL protocol
Sandboxed preload  ← exposes only normalized events and narrow settings operations
React + Three.js   ← VRM rendering, VRMA motion blending, expression driving
```

The renderer layer has no filesystem, process, or raw-audio access.

### Privacy-First Audio Capture

Persona listens to the **output audio** of the AI application, not the microphone. Each platform has its own approach:

- **Linux (PipeWire)**: polls the PipeWire graph for a Codex/ChatGPT playback node, attaches `pw-record` to that stream, calculates RMS in memory, discards every sample immediately
- **Windows (WASAPI loopback)**: uses `PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE` to capture only the target process tree, excluding all other application audio
- **macOS (Core Audio process tap)**: creates a private, unmuted tap and private aggregate device for the target process; requires macOS 14.2+ and one-time System Audio Recording permission

Persona doesn't capture the microphone, save audio, transcribe content, or send anything over the network. The only purpose of audio access is calculating amplitude to drive lip motion.

### MCP Interface: Agent-Controlled Animation

Persona serves a Streamable HTTP MCP endpoint at `127.0.0.1:47831/mcp`. Register it with Codex once:

```bash
codex mcp add persona --url http://127.0.0.1:47831/mcp
```

Four tools are exposed:

| Tool | Effect |
|------|--------|
| `play_animation` | Play a named animation (randomly selects one clip) |
| `list_animations` | List all available animations with descriptions and trigger scenarios |
| `control_window` | show / hide / toggle the character window |
| `get_status` | Read model readiness, window visibility, voice state |

Each custom animation carries a name, description, and **trigger scenario** when created — that metadata is exposed directly to the connected agent so the AI understands when to use each action. Catalog changes push tool-list change notifications to all connected sessions immediately.

### Animation System

Two permanent action slots exist: **Idle** and **Speaking**. Each can hold multiple `.vrma` clips; Persona randomly selects one on each trigger. Custom actions follow the same pattern — multiple clips, randomly chosen.

MCP-triggered animations take priority over audio-driven body motion, but lip sync continues. The agent can make the character wave while speaking. When the one-shot clip finishes, Persona returns to the current idle, listening, or speaking state automatically.

### Quick Start

```bash
# Requires Node.js 24+
git clone https://github.com/xikhar/persona.git && cd persona
cp public/assets/library.json.example public/assets/library.json
cp public/assets/manifest.json.example public/assets/manifest.json
npm install && npm run demo
```

The packaged character catalog is intentionally empty for licensing reasons. On first launch, go to Settings and import your own `.vrm` file — any VRM-compliant model works.

### Why 680 Stars in Three Days

The problem Persona solves isn't large, but it's specific and real: voice AI is too invisible. When Codex explains a complex piece of code to you, you want something over there that's *watching* you — not a progress bar, not a typing animation, but a presence that perceives the conversation and responds.

That's not a functional requirement; it's an emotional one. Persona answers it with VRM + MCP + process audio tap: a specific, extensible technical implementation of something that was previously just a missing piece.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
