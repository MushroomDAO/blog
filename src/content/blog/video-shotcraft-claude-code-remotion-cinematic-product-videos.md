---
title: "video-shotcraft：让 AI Agent 直接制作院线级产品宣传片"
titleEn: "video-shotcraft: Let an AI Agent Produce Cinema-Grade Product Films"
description: "Vincentwei1021 开源的 Claude Code / Codex Agent 视频制作技能包，3832 stars。内置 104 张镜头配方卡、161 种运动风格预览、完整 Remotion 视频模板 Ink Press（36.2秒/1920×1080/30fps）、149 个音效（16个场景类别）、5套背景音乐。Agent 拿到产品截图后自动分镜、动画、配音设计，直出可发布的产品宣传片。"
descriptionEn: "Vincentwei1021's open-source Claude Code/Codex agent video production skill, 3832 stars. Includes 104 shot recipe cards, 161 motion style previews, complete Remotion template Ink Press (36.2s/1920×1080/30fps), 149 SFX across 16 scene categories, 5 BGM tracks. Point the agent at your product and it handles storyboarding, animation, and sound design — output is a ready-to-publish cinematic promo."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["AI视频制作", "Claude Code", "Remotion", "Agent技能", "产品宣传", "分镜设计", "Mycelium"]
heroImage: "../../assets/images/video-shotcraft-claude-code-remotion-cinematic-product-videos-banner.jpg"
---

*by Mycelium Protocol*

---

产品宣传片的制作流程通常是：设计师画分镜 → 动效工程师实现动画 → 音效师配音 → 反复审片迭代。即使是一个 30 秒的产品 Demo，从零到完成也要几天。

video-shotcraft 把这个流程交给了 AI Agent：给 Agent 一个产品 URL，它负责分镜设计、动画实现、音效配置，最终输出一个可以直接发布的 1920×1080 视频。

GitHub: https://github.com/Vincentwei1021/video-shotcraft | ⭐ 3832

---

## 核心内容

### 104 张镜头配方卡

每张卡片记录一个具体的视觉镜头的完整信息：

- **用途（Purpose）**：这个镜头适合表达什么
- **能量感（Energy）**：节奏快慢、紧张程度
- **建议时长**
- **参数说明**：缓动曲线、运动幅度等
- **实现注意事项**
- **已知坑**

104 张卡分布在 10 个功能类别中，覆盖从产品特写到场景过渡的常见镜头需求。Gallery 在线可搜索、可过滤，复制镜头卡名称交给 Agent 即可使用：

> https://vincentwei1021.github.io/video-shotcraft/

### 161 种运动风格

每种风格都有对应的动态预览（mp4），不用猜效果，直接在 Gallery 里选好，告诉 Agent 要哪几张卡的组合。

### 完整视频模板：Ink Press

开箱即用的产品宣传片模板：

- **时长**：36.2 秒
- **规格**：1920×1080，30fps
- **镜头数**：10 个
- **风格**：纸墨琥珀色，2.5D 真实页面摄像机运动，标题卡，转场，完整电影级音效通道

Agent 把你产品的截图、文案、品牌色换进去，直接产出同等质量的成片。

### 149 个音效 + 5 套背景音乐

音效按 16 个场景/材质类别组织：
`transition` `impact` `riser` `camera` `ui` `text` `paper` `film` `light` `data` `scifi` `mech` `glass` `fluid` `crowd` `counter`

选用逻辑：先选类别（对应场景语气），再选音色（粗糙/细腻/金属感等）。配有专门的 [sound-design.md](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/sound-design.md) 说明每个文件的用法。

---

## 快速开始

**最直接的方式**：把仓库链接直接给 Agent：

```
Install this skill for me: https://github.com/Vincentwei1021/video-shotcraft
```

Agent 会自动 clone 并链接到技能目录。或手动安装：

```bash
# 用 skills CLI
npx skills add Vincentwei1021/video-shotcraft

# 手动 clone + 链接
git clone https://github.com/Vincentwei1021/video-shotcraft.git
cd video-shotcraft
ln -s "$(pwd)" ~/.claude/skills/video-shotcraft   # Claude Code
# 或
ln -s "$(pwd)" ~/.codex/skills/video-shotcraft    # Codex
```

安装后，直接告诉 Agent 要做什么：

```
Use video-shotcraft to create a promo for my desktop product.

Use the deck-deal-flyin and row-embed shot cards to present this feature.

Use video-shotcraft to make a promo with the Ink Press template.
```

如果不指定镜头卡，Agent 会先介绍内置模板并询问是否使用——推荐先从 Ink Press 开始，替换产品资产后就能得到一个完整的成片。

---

## 仓库结构

```
video-shotcraft/
├── SKILL.md                 # Agent 入口，核心制作规则
├── references/
│   ├── pipeline.md          # 端到端生产流程
│   ├── shots/               # 104 张镜头配方卡（10 个功能类别）
│   ├── sequences/           # 可复用的完整视频结构和序列模式
│   ├── aesthetic-rules.md   # 视觉 QA 标准
│   ├── music-beat-sync.md   # 背景音乐分析和节拍同步方法论
│   └── sound-design.md      # 音效指南和示例
├── demos/                   # Remotion 参考实现（同 shots 分类）
├── gallery/                 # 静态运动预览 Gallery
├── template/                # 可运行的完整视频模板
└── assets/
    ├── lib/                 # 可复用 Remotion 组件
    ├── scripts/             # 页面资产抓取脚本
    └── audio/
        ├── bgm/             # 5 套背景音乐
        └── sfx/<category>/  # 149 个音效，16 个场景类别
```

---

## 技术细节：Remotion 渲染

video-shotcraft 用 [Remotion](https://www.remotion.dev/) 做视频渲染——本质上是把 React 组件渲染成视频帧，每帧都是一个确定性的 React 状态，方便 Agent 精确控制每一帧的内容和动画参数。

**无头服务器渲染注意事项（2 核 Linux，Node 22）：**

| 问题 | 表现 | 解决 |
|------|------|------|
| 并发上限 | "Maximum for --concurrency is 2" | 传 `--concurrency=1` |
| Headless Chrome | 新版 Chrome 移除了旧 headless 模式，直接调 chromium 会失败 | 改用 chrome-headless-shell 二进制 |
| CDN 不可达 | remotion.media 被墙，无法自动下载 headless-shell | 传 `--browser-executable=<本地路径>` |

---

## 镜头卡的制作背景

104 张镜头配方卡通过研究一批产品宣传片提炼而来，参考来源包括 ClickUp、Perplexity、Slack、Notion、Figma、Framer、Bear、Raycast、Pitch、Miro、Superhuman、Loom 的官方产品片。

记录的是这些视频的**运动语言**（时序、缓动曲线、镜头编排）——所有 Remotion 实现都从头重写，不含任何原始视频/图像/品牌素材。

这个项目本身也是用 Claude Code + 这套方法论迭代开发出来的，包括 QA 过程。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## video-shotcraft: Let an AI Agent Make Cinematic Product Videos

*by Mycelium Protocol*

---

Product video production typically goes: designer storyboards → motion engineer animates → sound designer scores → multiple review rounds. Even a 30-second product demo can take days from zero to finished.

video-shotcraft hands this entire pipeline to an AI agent: give it a product URL, and it handles storyboarding, animation, and sound design — the output is a ready-to-publish 1920×1080 video.

GitHub: https://github.com/Vincentwei1021/video-shotcraft | ⭐ 3832

---

### What's Inside

**104 Shot Recipe Cards**

Each card captures a specific visual shot in full detail:
- **Purpose**: what emotional or narrative goal this shot serves
- **Energy**: pacing, tension level
- **Suggested duration**
- **Parameters**: easing curves, motion scale
- **Implementation notes**
- **Known pitfalls**

The 104 cards span 10 functional categories covering product close-ups through scene transitions. Browse and filter them in the live Gallery, copy card names, and hand them to your agent:

> https://vincentwei1021.github.io/video-shotcraft/

**161 Motion Style Previews**

Every style has a live mp4 preview — no guessing at the effect. Pick what you want in the Gallery, then tell the agent which cards to combine.

**Complete Video Template: Ink Press**

A validated, production-ready promo template:
- **Duration**: 36.2 seconds
- **Spec**: 1920×1080, 30fps
- **Shots**: 10
- **Style**: paper-ink-amber, 2.5D real-page camera moves, title cards, transitions, full cinematic SFX pass

The agent swaps in your product's screenshots, copy, and branding to reproduce the same quality. Fastest path to a finished film.

**149 SFX + 5 BGM Tracks**

SFX organized into 16 scene/material categories:
`transition` `impact` `riser` `camera` `ui` `text` `paper` `film` `light` `data` `scifi` `mech` `glass` `fluid` `crowd` `counter`

Pick category first (matches scene mood), then timbre. See [sound-design.md](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/sound-design.md) for per-file usage guidance.

---

### Quick Start

**Most direct path** — hand the repo link to your agent:

```
Install this skill for me: https://github.com/Vincentwei1021/video-shotcraft
```

The agent clones and links it to the skills directory. Or install manually:

```bash
npx skills add Vincentwei1021/video-shotcraft

# Or manually:
git clone https://github.com/Vincentwei1021/video-shotcraft.git
ln -s "$(pwd)/video-shotcraft" ~/.claude/skills/video-shotcraft   # Claude Code
# or
ln -s "$(pwd)/video-shotcraft" ~/.codex/skills/video-shotcraft    # Codex
```

Then tell the agent what you want:

```
Use video-shotcraft to create a promo for my desktop product.

Use the deck-deal-flyin and row-embed shot cards.

Use video-shotcraft with the Ink Press template.
```

If no shot cards are specified, the agent introduces the built-in template first and asks whether to use it. Starting with Ink Press and swapping in your product assets is the fastest path.

---

### Repository Structure

```
video-shotcraft/
├── SKILL.md                 # Agent entry point + core production rules
├── references/
│   ├── pipeline.md          # End-to-end production workflow
│   ├── shots/               # 104 shot recipe cards (10 functional categories)
│   ├── sequences/           # Reusable full-video structures
│   ├── aesthetic-rules.md   # Visual QA criteria
│   ├── music-beat-sync.md   # BGM analysis + beat-sync methodology
│   └── sound-design.md      # Sound design guidance
├── demos/                   # Remotion reference implementations
├── gallery/                 # Static motion-preview Gallery
├── template/                # Runnable complete video template
└── assets/
    ├── lib/                 # Reusable Remotion components
    ├── scripts/             # Page-asset capture scripts
    └── audio/
        ├── bgm/             # 5 BGM tracks
        └── sfx/<category>/  # 149 SFX, 16 scene categories
```

---

### How Remotion Rendering Works

video-shotcraft uses [Remotion](https://www.remotion.dev/) to render video — React components rendered to video frames. Every frame is a deterministic React state, which lets the agent precisely control every frame's content and animation parameters.

**Headless server rendering notes (2-core Linux, Node 22):**

| Issue | Symptom | Fix |
|-------|---------|-----|
| Concurrency cap | "Maximum for --concurrency is 2" | Pass `--concurrency=1` |
| Old headless removed | Recent Chrome dropped old headless; system chromium fails | Use chrome-headless-shell binary instead |
| CDN blocked | remotion.media unreachable, auto-download rejected | Pass `--browser-executable=<local path>` |

---

### Where the Shot Cards Come From

The 104 cards were distilled from studying outstanding product films from ClickUp, Perplexity, Slack, Notion, Figma, Framer, Bear, Raycast, Pitch, Miro, Superhuman, and Loom. The cards document motion language — timing, easing, choreography — re-implemented from scratch in Remotion TSX. No footage, artwork, or brand assets from the original films are included.

The toolkit itself was built and iterated with Claude Code using the same workflow it teaches.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
