---
title: "ChatCut × Codex：用 AI Agent 剪视频，提示词就是剪辑台"
titleEn: "ChatCut × Codex: Edit Video with an AI Agent — Your Prompt Is the Timeline"
description: "ChatCut 是一款 AI 视频编辑器，通过官方 Codex 插件把视频剪辑能力接入 OpenAI Codex Agent——输入一句话，Agent 自动完成字幕、动态图形、AI 配音、B-roll 生成、导出全流程。本文介绍产品全貌和入门使用方法。"
descriptionEn: "ChatCut is an AI video editor that plugs into OpenAI Codex Agent via an official plugin — type a prompt, and the agent handles captions, motion graphics, AI voiceover, B-roll generation, and export end-to-end. Here's what it is and how to get started."
pubDate: "2026-07-10"
updatedDate: "2026-07-10"
category: "Tech-News"
tags: ["ChatCut", "Codex", "AI视频剪辑", "Agent", "运动图形", "AI字幕", "AI配音", "B-roll", "视频生成"]
heroImage: "../../assets/images/chatcut-codex-ai-video-editor-guide-banner.jpg"
---

如果你用过 Codex（OpenAI 的 Agent 工具），现在它可以直接帮你剪视频了。

ChatCut 推出了一个官方 Codex 插件，把整个视频编辑工作流接入 Agent 运行时。你在 Codex 里打一句话，Agent 在 ChatCut 项目里执行——从剪素材、加字幕、生成动效，到 AI 配音、生成 B-roll、导出成品，全链路走通。

官方入口：[chatcut.io](https://chatcut.io) · 插件安装：[chatcut.io/codex](https://chatcut.io/codex)

---

## ChatCut 是什么

ChatCut 是一个基于浏览器的 AI 视频编辑器，定位是"告诉它你想要什么，它来完成"。

核心功能模块：

| 功能 | 说明 |
|------|------|
| **文字剪辑** | 把视频转为文字稿，在文字里改词/删句，时间轴自动跟着变 |
| **AI 字幕** | 100+ 语言自动生成，20+ 样式模板，一键套用 |
| **动态图形** | 用自然语言生成章节卡片、数据图表、时间轴动效，无需 After Effects |
| **AI 图片生成** | 项目内直接生成缩略图、B-roll 参考图（GPT Image 2） |
| **AI 视频生成** | 生成没拍到的 B-roll、过场镜头（Seedance 2.0 / Kling） |
| **AI 配音/TTS** | 从文字生成语音旁白，自动与画面同步 |
| **AI 音乐** | 描述氛围，生成版权免费背景音乐，精确匹配视频时长 |

免费计划包含基础字幕、图片、音乐、动效试用，无需绑卡。

---

## 什么是 ChatCut Codex 插件

`chatcut.io/codex` 是 ChatCut 专门为 OpenAI Codex Agent 写的插件安装指引页面。

安装后，Codex Agent 可以通过 MCP（Model Context Protocol）工具调用 ChatCut 的全部编辑 API——这意味着你可以用对话的方式驱动专业级视频编辑器。

**Agent 能做的事（通过插件）：**
- 导入本地或网络视频素材
- 读取/修改项目时间轴
- 生成并放置动态图形（Motion Graphics）
- 转录音频、添加字幕
- 生成 AI 配音并与画面同步
- 生成 AI 视频 / 图片素材并插入时间轴
- 导出成品视频，返回下载链接

这不是"帮你写剪辑脚本"——Agent 真正地在操作 ChatCut 项目，改动在编辑器里实时可见。

---

## 插件提供哪些 Skill

ChatCut 的 Codex 插件内置了 15 个专业 Skill，每个 Skill 是一套针对特定任务的操作指导：

| Skill | 覆盖场景 |
|-------|---------|
| `chatcut-plugin-basics` | 基础项目上下文、数据模型、操作规范 |
| `talking-head-guide` | 口播视频清理（去口癖词、去停顿、字幕） |
| `create-motion-graphics` | JSX 直接编写动态图形，精准控制样式 |
| `transcription` | 音频转文字，驱动文字剪辑工作流 |
| `asset-import` | 媒体素材导入与管理 |
| `video-gen` | Seedance 2.0 / Kling AI 视频生成 |
| `image-gen` | AI 图片生成（含参考图、缩略图） |
| `voice` | TTS 配音、旁白生成、配音同步 |
| `music` | AI 音乐生成，匹配视频时长 |
| `export` | 项目导出与进度追踪 |
| `verification` | 编辑结果校验（渲染截图确认改动） |
| `shader-gen` | GLSL shader 特效生成 |
| `widget-forms` | 可视化选择界面（风格选择、跟进问题） |
| `product-help` | ChatCut 产品功能问题解答 |
| `known-errors` | 常见错误处理与调试 |

---

## 入门：如何接入 Codex

### 前置条件

- 已安装 Codex 桌面应用（OpenAI Codex Desktop App）
- 系统已安装 `ffmpeg`（ChatCut 媒体导入依赖）
- ChatCut 账号（免费注册）

验证 ffmpeg：
```bash
ffmpeg -version
```

### 第一步：安装 ChatCut 插件

在 Codex 里打开一个对话，输入：

```
Turn Codex into a video editor, read chatcut.io/codex
```

Codex Agent 会读取安装指引并自动执行：添加插件 marketplace、安装 ChatCut 插件、发起 OAuth 登录。

或者手动执行（把 `<bundled-codex>` 替换为你的 Codex 内置 CLI 路径）：

```bash
# 添加 ChatCut 插件 marketplace
<bundled-codex> plugin marketplace add https://github.com/ChatCut-Inc/agent-plugin.git --ref main

# 查看 marketplace 名称
<bundled-codex> plugin marketplace list

# 安装插件
<bundled-codex> plugin add chatcut@<marketplace-name>

# 登录 ChatCut
<bundled-codex> mcp login chatcut
```

### 第二步：验证安装

```bash
<bundled-codex> plugin list --marketplace <marketplace-name>
<bundled-codex> mcp get chatcut
```

ChatCut 一行显示 `installed, enabled` 即为成功。

### 第三步：开始剪辑

在 Codex 新对话里，直接用自然语言：

```
Import this video into my ChatCut project.
（把这个视频导入我的 ChatCut 项目）

Add a simple motion graphic overlay.
（添加一个简单的动效叠加层）

Generate a voiceover and background music.
（生成配音和背景音乐）

Transcribe this clip and add captions.
（转录这个片段并加字幕）

Export the current project.
（导出当前项目）
```

---

## 几个实际场景

### 场景一：口播视频快速清理

```
Clean up all the filler words in this talking head video,
add captions in TikTok Pop style.
（清理这个口播视频里的所有口癖词，加 TikTok Pop 风格字幕）
```

Agent 会：转录音频 → 识别 "um"/"uh"/"you know" 等 → 在时间轴上切掉对应片段 → 生成字幕并套用样式。

### 场景二：生成章节动效

```
Turn this rough creator edit into crisp chapters, charts,
and emphasized on-screen moments.
（把这段粗剪变成有清晰章节卡片、图表和重点强调的成品）
```

Agent 分析视频内容，生成章节卡片动效、数据图表动效，并放置在合适时间点。

### 场景三：补拍不到的 B-roll

```
Generate a cinematic shot of a busy Tokyo street at night
for the 0:30 mark.
（在 0:30 处生成一个东京夜晚街道的电影感镜头）
```

Agent 调用 Seedance 2.0 生成视频，直接插入时间轴指定位置。

### 场景四：AI 配音 + 同步

```
Generate a professional English voiceover for this product demo,
sync it with the on-screen content.
（为这个产品演示视频生成专业英文配音，与画面内容同步）
```

Agent 分析画面内容 → 生成旁白文本 → TTS 转为语音 → 按画面节奏对齐放置。

---

## 定价参考

| 计划 | 价格 | 核心配额 |
|------|------|---------|
| **Free** | 免费，无需绑卡 | 基础字幕/图片/音乐/动效试用 |
| **Plus $25/月** | $25/月 | 100 credits，Seedance 2.0（最多 166 秒视频），GPT Image 2（最多 454 张图） |
| **Plus $100/月** | $100/月 | 400 credits，Seedance 2.0（最多 666 秒），GPT Image 2（最多 1818 张） |

所有付费计划都包含完整的 AI Agent 编辑能力（即 Codex 插件调用权限）。

---

## 和其他 AI 视频工具的区别

| | ChatCut | CapCut AI | RunwayML | Descript |
|--|---------|-----------|---------|---------|
| Agent 驱动编辑 | ✅ (Codex 插件) | ❌ | ❌ | ❌ |
| 文字剪辑 | ✅ | ⚠️ 有限 | ❌ | ✅ |
| AI 动态图形 | ✅ JSX 级别 | ⚠️ 模板 | ❌ | ❌ |
| AI 视频生成 | ✅ Seedance/Kling | ✅ | ✅ | ❌ |
| AI 音乐生成 | ✅ | ✅ | ❌ | ❌ |
| 浏览器内编辑 | ✅ | ✅ | ✅ | ✅ |
| MCP 工具集成 | ✅ | ❌ | ❌ | ❌ |

ChatCut 的核心差异点在于 **Agent 可编程性**——通过 MCP 协议，任何支持工具调用的 AI Agent 都可以驱动 ChatCut 做视频编辑，而不只是在 UI 里点来点去。

---

## 一句话总结

ChatCut 把视频编辑变成了一个可以被 Agent 调用的服务。你写提示词，Agent 在专业视频编辑器里真正地执行操作。

对于内容创作者：这是目前入门门槛最低的全功能 AI 视频编辑工具之一。
对于开发者/Agent 爱好者：这是第一个把视频编辑全流程暴露成 MCP 工具集的产品。

---

- 产品主页：[chatcut.io](https://chatcut.io)
- Codex 插件安装：[chatcut.io/codex](https://chatcut.io/codex)
- GitHub 插件仓库：[github.com/ChatCut-Inc/agent-plugin](https://github.com/ChatCut-Inc/agent-plugin)

© 2026 Author: Mycelium Protocol

<!--EN-->

## ChatCut × Codex: Edit Video with an AI Agent — Your Prompt Is the Timeline

If you use Codex (OpenAI's agent tool), it can now edit video for you.

ChatCut has released an official Codex plugin that connects the entire video editing workflow to the Agent runtime. Type a prompt in Codex, and the Agent executes in your ChatCut project — trimming footage, adding captions, generating motion graphics, creating AI voiceovers, generating B-roll, and exporting the final cut.

Product: [chatcut.io](https://chatcut.io) · Plugin install: [chatcut.io/codex](https://chatcut.io/codex)

---

### What ChatCut Is

ChatCut is a browser-based AI video editor. Its pitch: tell it what you want, and it figures out how to do it.

Core capabilities:
- **Text-based editing**: transcript-driven editing — change a word, cut a sentence in the transcript, and the timeline follows
- **AI captions**: auto-generated in 100+ languages, 20+ style templates
- **Motion graphics**: generate chapter cards, charts, emphasis effects from a sentence — no After Effects, no keyframing
- **AI image generation**: generate thumbnails, B-roll reference images (GPT Image 2) inside your project
- **AI video generation**: generate B-roll and establishing shots you couldn't film (Seedance 2.0 / Kling)
- **AI voiceover**: text-to-speech narration, synced to on-screen content
- **AI music**: describe the vibe, get a royalty-free track cut precisely to your video length

Free plan available, no credit card required.

---

### What the Codex Plugin Does

`chatcut.io/codex` is the official install guide for the ChatCut Codex plugin. Once installed, the Codex Agent gets access to ChatCut's full editing API via MCP (Model Context Protocol) — meaning you drive a professional video editor through conversation.

The Agent is genuinely operating ChatCut: changes appear live in the editor.

**The plugin gives Codex 15 built-in skills:**

| Skill | Covers |
|-------|--------|
| `chatcut-plugin-basics` | Project model, data structures, operating rules |
| `talking-head-guide` | Filler-word removal, transcript cleanup, captions |
| `create-motion-graphics` | JSX-level direct authoring of motion graphic assets |
| `transcription` | Audio transcription driving the text-edit workflow |
| `video-gen` | Seedance 2.0 / Kling AI video generation |
| `image-gen` | AI image generation with reference images |
| `voice` | TTS voiceover, narration, video sync |
| `music` | AI music generation matched to video duration |
| `export` | Project export and progress tracking |
| `verification` | Rendered screenshot confirmation of edits |

---

### Getting Started

**Prerequisites**: Codex Desktop App installed, `ffmpeg` in PATH, ChatCut account (free).

**Install in one prompt**: Open a new Codex conversation and type:

```
Turn Codex into a video editor, read chatcut.io/codex
```

Codex reads the install guide and handles everything: adds the plugin marketplace, installs the plugin, opens the OAuth login flow.

**Then start editing** with natural language:

```
Import this video into my ChatCut project.
Add a simple motion graphic overlay.
Generate a voiceover and background music.
Transcribe this clip and add captions.
Export the current project.
```

---

### Real Scenarios

**Talking-head cleanup**: "Clean up all the filler words and add TikTok Pop captions." → Agent transcribes, identifies um/uh/you know, cuts them from the timeline, applies caption style.

**Motion graphics**: "Turn this rough edit into crisp chapters and charts." → Agent generates chapter card and chart motion graphics at the right timestamps.

**Missing B-roll**: "Generate a cinematic Tokyo night street shot for the 0:30 mark." → Agent calls Seedance 2.0, inserts generated clip at 0:30.

**AI voiceover**: "Add a professional English voiceover synced to this product demo." → Agent analyzes the screen content, writes narration, generates TTS audio, aligns it to the visual beats.

---

### Pricing

| Plan | Price | Key limits |
|------|-------|-----------|
| Free | Free, no card | Trial credits for captions, images, music, motion graphics |
| Plus $25/mo | $25/mo | 100 credits — up to 166s of Seedance video, 454 GPT images |
| Plus $100/mo | $100/mo | 400 credits — up to 666s video, 1818 images |

All paid plans include full AI Agent editing capabilities.

---

### Why It's Different

ChatCut's real differentiator isn't any individual feature — it's **agent programmability**. By exposing the full editing workflow as MCP tools, any AI agent with tool-calling support can drive ChatCut. Not clicking through a UI — actually operating the editor through code.

For content creators: probably the lowest-barrier full-featured AI video editor available right now.

For developers and agent enthusiasts: the first product to expose a complete video editing workflow as an MCP tool surface.

---

- Product: [chatcut.io](https://chatcut.io)
- Codex plugin: [chatcut.io/codex](https://chatcut.io/codex)
- Plugin repo: [github.com/ChatCut-Inc/agent-plugin](https://github.com/ChatCut-Inc/agent-plugin)

© 2026 Author: Mycelium Protocol
