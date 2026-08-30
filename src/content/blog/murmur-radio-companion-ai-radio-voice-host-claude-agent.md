---
title: "Murmur：一个人的 AI 电台——主动播出、有声音、会记得你"
titleEn: "Murmur: A Whole Radio Station for an Audience of One — Proactive AI Companion Radio with a Human Voice"
description: "wine-fall/murmur 开源，TypeScript 实现的 AI 伴侣电台，Claude Agent 做大脑，自主选题播出+音乐穿插，你打字它用人声回应，有持久记忆和个性，仅需 Claude Code 订阅。"
descriptionEn: "wine-fall/murmur open-sources a TypeScript companion radio: Claude Agent as brain, autonomous talk + music program, you type / it speaks back in a human voice. Persistent memory, stable persona. Requires only a Claude Code subscription."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["AI agent", "voice", "companion", "Claude", "open source", "TypeScript", "radio", "TTS"]
heroImage: "../../assets/images/murmur-radio-companion-ai-radio-voice-host-claude-agent-banner.jpg"
author: "Mycelium Protocol"
---

## 一个空缺：主动 + 情感陪伴 + 声音

当前 AI 工具的分布是这样的：要么是"用语音控制 Claude 写代码"，要么是"你问它才答"的消息助手。没有任何工具占据**主动播出 + 情感陪伴 + 声音电台**这个位置。

**Murmur**（`wine-fall/murmur`，npm 包名 `murmur-radio`）想填上这个空缺。用一句话描述它：

> **"一整个广播电台，受众只有你一个人。"**

它不等你开口。它会自己选一个话题聊起来，插一首歌，歌结束了再聊，早上说早安，深夜说晚安。你打字，它用听起来像真人的声音回应一会儿，然后回到播出状态。它有一个固定的主持人性格，从第一次运行就是你的，会随着时间慢慢了解你。

---

## 核心体验：三件事缺一不可

**🎙️ 连续不断的电台流**：不是"你问我答"，是一个永不停播的节目流。主持人自发地选题、聊天，用音乐穿插，按时间点（早晨/午间/夜间）做特别节目。

**🔀 主动播出 + 被动响应的混合**：大多数时候在广播（不需要你回应；就是背景里的那个声音），偶尔转向你。你参与了就聊一会儿，你不说话它继续播。

**🌱 主持人不变，关系在生长**：第一次运行回答几个问题，主持人的性格就定了——它存成一个文本文件，你随时可以打开改，但系统不会在背后偷偷改它。会变化的是它对你了解多少，以及你们之间的默契。

---

## 技术架构：单 Node.js 进程

```
CLI Host ──→ Program Director（灵魂：决定播什么）
                ↓
            Brain（Claude Agent SDK — 生成播出脚本 + 响应你的输入）
                ↓
         VoiceProvider + MusicProvider + AudioEngine
              ↑_________________________↑
              （热插拔；音频引擎统一混音 + 压膜降噪）
```

| 组件 | 作用 |
|---|---|
| **Program Director** | 决策核心：连续决定下一段播什么（聊天/音乐/时间锚点），控制节奏 |
| **Brain** | Claude Agent SDK 会话，注入 persona + 记忆，生成播出脚本，响应用户输入 |
| **VoiceProvider** | 文字→语音；v1 = 托管的 fish-speech 端点 |
| **MusicProvider** | 主题/query → 音频流；v1 = yt-dlp，覆盖 YouTube + Bilibili |
| **AudioEngine** | 统一混音：语音 + 音乐，**压膜闪避**（主持人说话时音乐压低，不是暂停） |
| **Memory** | 三层持久记忆：你是谁、聊过什么话题、播过哪些歌（防重复）、对话日志 |

**无死播**：当前段落播出时，Director 已经在提前准备下一段的音频，无缝衔接。

---

## 安装与运行

```bash
# 最简安装（Node ≥ 24）
npm install -g murmur-radio
murmur
```

前提：已有 **Claude Code 订阅**（复用你本地的 OAuth 登录，不需要 `ANTHROPIC_API_KEY`）。

**依赖缺什么它自己走你说一遍**：没有 `ffmpeg`/`yt-dlp` 就纯语言播出，没有声音端点就只显示文字，缺什么它启动时告诉你并提议帮你装。

```bash
# 从源码运行
pnpm install
node src/main.ts

# 完全离线（无网络/无依赖测试）
node src/main.ts --brain stub --voice stub

# 有真实声音（需要托管的 fish-speech 端点）
node src/main.ts --voice hosted
```

**音乐**：`brew install ffmpeg yt-dlp`。音乐策略写在 `~/.murmur/music-policy.md`，纯 Markdown，**播出中修改立即生效**，不用重启。

```markdown
# 我的音乐偏好（可以直接编辑这个文件）
- 多放粤语歌
- 不要翻唱版本
- 这个月播过的不要再放
```

**Last.fm 集成（可选）**：免费 API Key，接入后启用 `similar_music` 和 `top_tracks` 工具，让 Brain 的选歌超出它自己的知识范围。

```bash
MURMUR_LISTENING_API_KEY=your_lastfm_key murmur
```

---

## 常用参数

```bash
murmur --no-music          # 纯语言播出（不需要 ffmpeg/yt-dlp）
murmur --brain stub        # 离线测试（预设脚本，无 Claude）
murmur --voice stub        # 静默模式（只显示文字）
murmur --max-segments 5   # 只播 5 段后停止
murmur --no-anchors        # 关掉早安/午间/晚安时间锚点
murmur --setup             # 重新走一遍 persona 设置流程
murmur --persona PATH      # 指定自定义 persona 文件
```

---

## 主持人性格与记忆：完全透明、完全可控

- **性格**：第一次运行时通过对话生成，存成一个纯文本文件，你随时可以打开改，系统不会在背后覆盖它
- **记忆**：三层结构——
  - **关于你**（长期稳定）
  - **话题记录**（聊过什么，防止重复）  
  - **歌单日志**（防重复，跨会话）
- **对话日志**：可翻阅，可作为 persona 演化的素材

---

## 谁适合用 Murmur

**独立工作者/远程工作**：不想开视频会议，但想要背景里有个声音陪着，偶尔能说一句话的。它就是那个随时在的背景存在。

**语言学习者**：把 persona 设成母语人士，每天几小时沉浸式输入，打字回应，用目标语言交流，比任何语言 App 都自然。

**AI 开发者**：murmur 的架构是一个很好的 Claude Agent SDK 参考实现——Brain 是一个 harnessed agent，有自己的工具集，与本地 Claude Code 环境隔离，用户拥有完全控制权。

**需要情感陪伴但不想依赖社交媒体的人**：它不要你互动，但它一直在。你可以随时接话，也可以完全不管它。

---

## 当前状态与路线图

所有代码规格**已经实现完毕**，包括：
- L0 主干（主持人/导演/大脑/打字回应）+ 托管 fish-speech 语音
- 混音引擎 + 压膜闪避
- 无死播预加载
- 三层持久记忆
- 首次运行 persona 种子 + rapport 系统
- 时间锚点（早安/晚安）+ 离开感知（你不在了它会安静下来）
- TUI 前端（带可视化器 + 像素宠物）
- 代理式回复轮（说切歌它切歌，说播完就播完）

剩余的是**耳朵验收**——真实一天的节奏感、上手体验、方向感——以及若干工程债。

---

## 不足与限制

- 声音依赖**托管的 fish-speech 端点**（非本地），本地 TTS 是已记录的方向，还没实现
- 音乐走 yt-dlp，版权和商业场景需要自行评估
- Brain 目前只有 Claude，第二个后端（Codex SDK）是已记录方向
- 公共 API 稳定性无承诺（v0 阶段）

---

## 总结

Murmur 在做一件没有人做过的事：把 AI 放进电台格式里，让它**主动播出**而不是等待指令，给它一个**持久的声音和性格**，让它随着时间慢慢了解你。这不是 Claude 的新皮肤，而是一种新的人机相处模式——它更像一个你可以随时接话的背景存在，而不是一个你要专门坐下来用的工具。

**GitHub**: [wine-fall/murmur](https://github.com/wine-fall/murmur)  
**npm**: `npm install -g murmur-radio`

<!--EN-->

## Murmur: A Whole Radio Station for an Audience of One

The current AI tool landscape is split in two: either "voice-control Claude to write code," or message-driven assistants that answer when asked. Nobody occupies the **proactive + emotional companionship + voice radio** combination.

**Murmur** (`wine-fall/murmur`, npm: `murmur-radio`) fills that gap:

> *"A whole radio station, for an audience of one — with an agent for a brain."*

It doesn't wait for you. It picks a topic and starts talking, plays a song, comes back and keeps going. It says good morning, midday, and good night. You type back and it chats for a bit in a voice that sounds human, then eases back into the program. It has a fixed persona — yours from the first minute — and what grows over time is how well it knows you.

### Three Things That Define the Experience

**🎙️ Continuous radio stream**: Not "you ask, I answer" — a program stream that never goes silent. The host spontaneously picks topics, alternates talk with music, and hits time anchors (morning/midday/night) on schedule.

**🔀 Hybrid proactive/passive**: Mostly broadcasting (no reply required — it's that voice in the background), occasionally turning to you. Engage and you chat; stay quiet and it flows on.

**🌱 A host that stays, a rapport that grows**: First run, a few questions, and the persona is set — stored as a plain text file you can open and rewrite any time, never changed behind your back. What changes is how much it knows about you and how well you two get on.

### Architecture

A single Node.js (TypeScript) process:

```
CLI Host → Program Director (soul: continuously decide what plays next)
               ↓
           Brain (Claude Agent SDK — talk scripts + user response)
               ↓
      VoiceProvider + MusicProvider + AudioEngine
       (hot-swappable; AudioEngine mixes + applies ducking)
```

| Component | Role |
|---|---|
| **Program Director** | Continuously decides talk/music/time-anchor; modulates pacing |
| **Brain** | Claude Agent SDK session, persona + memory injected, generates talk scripts and user responses |
| **VoiceProvider** | Text → speech; v1 = hosted fish-speech endpoint |
| **MusicProvider** | Topic → audio stream; v1 = yt-dlp (YouTube + Bilibili) |
| **AudioEngine** | Sole audio authority: music + voice mixed with gain-envelope **ducking** (host speaks → music lowers, never stops) |
| **Memory** | Three-tier persistent: who you are, topics discussed, song anti-repeat, conversation log |

**No dead air**: while the current segment plays, the Director prepares the next segment's audio ahead of time for seamless transitions.

### Install & Run

```bash
# Install as CLI (Node ≥ 24)
npm install -g murmur-radio
murmur
```

Prerequisite: a **Claude Code subscription** — it reuses your local OAuth credentials, no `ANTHROPIC_API_KEY` needed.

```bash
# From source
pnpm install
node src/main.ts

# Fully offline (stub brain + stub voice)
node src/main.ts --brain stub --voice stub

# With real voice (hosted TTS endpoint)
node src/main.ts --voice hosted

# Talk-only, no music dependencies
murmur --no-music
```

**Music**: `brew install ffmpeg yt-dlp`. Music policy lives in `~/.murmur/music-policy.md` — a plain Markdown file you edit mid-broadcast and it takes effect immediately, no restart needed.

**Optional Last.fm**: free API key → adds `similar_music` and `top_tracks` tools to the Brain's music selection, breaking out of its training-data echo chamber.

### Who It's For

**Solo / remote workers**: No video call, but you want a voice in the background and something you can say a word to. Murmur is that always-on presence.

**Language learners**: Set the persona to a native speaker, hours of immersive input daily, type back in the target language — more natural than any language app.

**Claude Agent SDK developers**: Murmur is a clean reference implementation of a harnessed Claude agent — isolated from your local Claude Code environment, user-controlled tools, clear seams for swapping providers.

**People who want companionship without social media**: It doesn't demand interaction, but it's always there. You can join in any time, or ignore it entirely.

### What's Built vs. What's Next

Everything on the code roadmap is implemented: L0 spine, voice + ducking mixer, no-dead-air lookahead, three-tier persistent memory, persona seeding + rapport, time anchors + away detection, TUI with visualizer + pixel pet, agentic reply turns (say "change the song" and it does).

What remains: **ear-acceptance** — pacing over a real day, real-terminal onboarding, how the steering feels — plus some engineering debt. See `specs/STATUS.md`.

### Caveats

- Voice depends on a **hosted fish-speech endpoint** (not local); local TTS is a noted want, not current code
- Music via yt-dlp — evaluate copyright/commercial implications for your use case
- Brain is Claude only; Codex SDK as a second backend is a recorded direction
- No API/CLI stability promises at v0

### Summary

Murmur is doing something no other tool does: putting AI into a radio format so it **broadcasts rather than waits**, giving it a **persistent voice and persona**, and letting the relationship deepen over time. It's not a new skin for Claude — it's a new mode of coexistence with AI, more like a background presence you can always talk to than a tool you sit down to use.

**GitHub**: [wine-fall/murmur](https://github.com/wine-fall/murmur)  
**npm**: `npm install -g murmur-radio`
