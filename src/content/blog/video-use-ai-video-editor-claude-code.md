---
title: "video-use：用 Claude Code 剪视频，browser-use 团队开源 AI 视频编辑器"
titleEn: "video-use: Edit Videos with Claude Code — browser-use Team's Open Source AI Video Editor"
description: "video-use 是 browser-use 团队开源的 AI 视频编辑 skill，14,000+ Stars，支持 Claude Code/Codex/Hermes 等 Agent，自然语言描述剪辑任务，AI 自动剪掉填充词、自动调色、生成字幕、添加动画 overlay，通过 ElevenLabs 配音，输出 final.mp4。Python 开发，完全开源。"
descriptionEn: "video-use (14,408 ⭐, Python, open source) is the browser-use team's AI video editing skill for Claude Code, Codex, Hermes, and other agents. Drop raw footage, describe the edit in natural language, get final.mp4 back. Auto-cuts filler words, color grades, burns subtitles, generates animation overlays via Remotion/Manim, adds ElevenLabs voiceover."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-News"
tags: ["视频编辑", "AI Agent", "Claude Code", "开源", "browser-use", "Python", "内容创作", "自动化"]
heroImage: "../../assets/images/video-use-ai-video-editor-claude-code-banner.jpg"
---

> **GitHub**: [browser-use/video-use](https://github.com/browser-use/video-use) · ⭐ 14,408 · Python · 开源  
> **来源**: browser-use 团队 · **依赖**: ffmpeg + ElevenLabs API Key

---

## 背景：browser-use 团队的新方向

browser-use 已经是最知名的 AI 浏览器自动化工具之一（GitHub 多万 Stars）。现在这个团队把同样的"AI Agent 驱动工具"思路用到了视频编辑上。

**video-use 的核心想法**：不用学 Premiere Pro，不用拖时间轴，直接告诉 Claude Code "把这段视频剪成发布版本"。

---

## 它能做什么？

把一堆原始素材丢进文件夹，打开 Claude Code，发指令：

```bash
cd /path/to/your/raw-videos
claude  # 或 codex, hermes, openclaw

# 然后在对话里说：
"edit these into a launch video"
```

Agent 会：
1. 盘点所有素材文件
2. 提出剪辑策略（让你确认）
3. 执行剪辑，输出 `edit/final.mp4`

---

## 核心能力

### 1. 自动剪掉填充词和死空间

这是最省时间的功能。原始录制往往有大量：
- "嗯"、"啊"、"那个"（umm, uh, like）
- 假开头（false starts）
- 说话之间的沉默间隙

video-use 自动识别并剪掉，不需要你逐帧手动找。

### 2. AI 自动调色

每段素材自动套用色彩预设：

```python
# 可以自定义，或让 AI 选
color_grades = [
    "warm cinematic",      # 暖色电影感
    "neutral punch",       # 中性高对比
    "custom ffmpeg chain"  # 自定义 ffmpeg 滤镜
]
```

30ms 音频淡入淡出处理确保每个切点不会有爆音。

### 3. 字幕生成（可自定义样式）

默认是 2 个词一组、全大写的风格（类似流行短视频），完全可配置：

```
原始：这是一个关于 AI 视频编辑的演示
字幕：THIS IS | A DEMO | OF AI | VIDEO EDIT
```

### 4. 动画 Overlay 生成

这是 video-use 最野的功能——它能在视频上自动生成动画：

| 动画引擎 | 适合场景 |
|---|---|
| **HyperFrames** | 标题动画、数据可视化 |
| **Remotion** | React 驱动的复杂动画 |
| **Manim** | 数学公式、图表演示 |
| **PIL** | 简单图片叠加 |

多个动画在并行子 Agent 里生成，一个视频可以同时有多种风格的动画段落。

### 5. ElevenLabs 配音

```bash
# 安装时会提示你粘贴 ElevenLabs API Key
# 之后：
"给这段演示视频配英语 voiceover，声音用商务正式风格"
```

### 6. 自我评估

在最终输出之前，Agent 会在每个切点自动评估渲染质量，如果发现问题会重新生成。不会给你一个没看过就输出的版本。

### 7. Session 记忆

```
project.md  ← Agent 自动维护的会话状态
```

下周打开同一个项目，Agent 知道上次剪到哪里了、用了什么色彩方案、你的素材是什么风格。

---

## 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/browser-use/video-use ~/Developer/video-use

# 2. 注册到 Claude Code skills
ln -sfn ~/Developer/video-use ~/.claude/skills/video-use

# 3. 安装依赖
pip install -r ~/Developer/video-use/backend/requirements.txt

# 4. 安装 ffmpeg（macOS）
brew install ffmpeg
```

或者用这个 setup prompt 让 Agent 自动完成：

```
Set up https://github.com/browser-use/video-use for me.

Read install.md first to install this repo, wire up ffmpeg, 
register the skill with whichever agent you're running under, 
and set up the ElevenLabs API key — ask me to paste it when 
you need it. Then read SKILL.md for daily usage, and always 
read helpers/ because that's where the editing scripts live.
```

---

## 实际工作流示例

**场景：录制了一个产品演示视频，要发布到各平台**

```bash
# 原始素材在 ~/Desktop/demo-recording/
cd ~/Desktop/demo-recording
claude

# Agent 会询问你的意图，然后开始：
"edit these into a 90-second product launch video"

# Agent 输出：
# [inventory] Found 3 takes: take1.mp4 (8m), take2.mp4 (6m), take3.mp4 (7m)
# [strategy] Recommend: use take2 as base, splice best moments from take3
# [approve?] Proceed with this plan? 
> yes

# [cutting] Removing filler words from take2... (found 47 fillers)
# [color] Applying warm cinematic grade...
# [subtitles] Generating 2-word chunks...
# [animation] Spawning 2 sub-agents for title card animations...
# [eval] Reviewing 23 cut boundaries...
# [done] edit/final.mp4 (1:32)
```

---

## 局限性

**现阶段不适合的场景**：
- 复杂的多轨 B-roll 合成（需要手动指引）
- 直播录制的实时处理
- 专业级别的特效合成（After Effects 级别）

**依赖问题**：
- 需要 ElevenLabs API Key（如果需要配音）
- ffmpeg 是必须的
- ElevenLabs 不免费，有用量费用

---

## 和传统工具的对比

| 工具 | 学习曲线 | 自动化 | 价格 |
|---|---|---|---|
| Premiere Pro | 陡峭 | 低 | $60/月 |
| DaVinci Resolve | 中等 | 低 | 免费/付费 |
| Descript | 低 | 中等 | $24/月 |
| **video-use** | 极低（自然语言） | 高 | 开源免费（API 费另计） |

---

## 谁应该试试？

**最适合**：
- 开发者录制技术教程/演示视频
- YouTube/播客创作者有大量原始素材
- 产品团队需要快速输出功能演示
- AI 应用开发者想给用户加视频处理能力

---

## 总结

video-use 是 browser-use 团队把同一套"AI Agent 驱动"哲学推广到视频制作领域的产品。核心价值：**把视频剪辑变成一个对话任务**，而不是一个需要学习专业软件的技能。

对于内容不是核心竞争力、但又需要稳定输出视频的开发者团队，这可能是最快上手的工具。

> **链接**: [GitHub](https://github.com/browser-use/video-use) · [Browser Use Cloud](https://cloud.browser-use.com/v4?utm_campaign=video-use)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: video-use (14,408 ⭐, Python, open source) is the browser-use team's AI video editing skill for Claude Code, Codex, Hermes, OpenClaw, and any shell-capable agent. Drop raw footage in a folder, describe the edit in natural language, get `final.mp4` back. Auto-cuts filler words, color grades, burns subtitles, generates animation overlays (via Remotion/Manim/HyperFrames/PIL), adds ElevenLabs voiceover. Self-evaluates at every cut boundary. Session memory via `project.md`.

---

## What It Does

Point your agent at a folder of raw footage and describe the edit. The agent:

1. Inventories source files
2. Proposes an editing strategy (waits for your approval)
3. Executes: cuts fillers, grades color, generates subtitles, adds animations, renders `edit/final.mp4`

All outputs go in `edit/` — the skill directory stays clean.

## Core Features

**Filler Word Removal**: Auto-detects and cuts "umm", "uh", false starts, and dead silence between takes.

**Auto Color Grading**: Warm cinematic, neutral punch, or any custom ffmpeg chain. 30ms audio fades at every cut to prevent pops.

**Subtitle Generation**: 2-word UPPERCASE chunks by default (popular short-form style). Fully customizable.

**Animation Overlays**: Spawns parallel sub-agents for animations using HyperFrames, Remotion (React), Manim (math/charts), or PIL. Multiple animation styles in one video.

**Self-Evaluation**: Checks every cut boundary before final output. If a cut looks wrong, it regenerates.

**Session Memory**: Persists state in `project.md`. Next session picks up where it left off.

## Setup (copy-paste to Claude Code)

```
Set up https://github.com/browser-use/video-use for me.
Read install.md first, wire up ffmpeg, register the skill, 
set up the ElevenLabs API key — ask me to paste it when ready.
```

## Dependencies

- ffmpeg (required)
- ElevenLabs API key (for voiceover — not free, per-usage billing)
- Python 3.10+

**Links**: [GitHub](https://github.com/browser-use/video-use) · [Browser Use Cloud](https://cloud.browser-use.com/v4)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
