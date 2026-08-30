---
title: "Echo Slides Skill：一行命令装进所有 Agent，从演讲视频自动提取去重幻灯片"
titleEn: "Echo Slides Skill: One Command, All Agents — Extract Deduplicated Slides from Any Talk Recording"
description: "xiangzhouEcho/Echo-Slides-Skill 开源 Claude Code Skill，npx skills add 一行装到全局，Claude Code/Codex/Cursor/OpenCode 通用，双签名去重（dHash+RGB网格），实测20分钟演讲39页零重复。"
descriptionEn: "xiangzhouEcho/Echo-Slides-Skill is a Claude Code Skill that extracts deduplicated slides from any talk recording. One npx install, works across Claude Code/Codex/Cursor/OpenCode. Dual-signature dedup (dHash + RGB grid). 39 slides from a 20-min webinar, zero duplicates."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["Claude Code", "skill", "video", "slides", "open source", "AI tools", "productivity", "agent"]
heroImage: "../../assets/images/echo-slides-skill-extract-slides-from-video-claude-code-skill-banner.jpg"
author: "Mycelium Protocol"
---

## 这个痛点存在了很久

你在 YouTube 上看到一场精彩演讲，想把 PPT 存下来——但主办方没放原文件，只有视频。手动截图费时、截到转场动画、同一页截两次……这件事做起来比想象中烦。

**Echo Slides Skill** 解决的就是这个问题。一行命令装进你的 Agent 环境，之后直接对 Claude Code（或 Codex、Cursor、OpenCode）说"帮我把这个视频里的幻灯片扒出来"，它就去做了。

```bash
npx skills add xiangzhouEcho/Echo-Slides-Skill -g
```

`-g` 安装到用户级目录（`~/.claude/skills/`），**所有项目都能用**。不加 `-g` 则只安装进当前项目。

---

## 核心洞察：幻灯片是区间，不是帧

大多数"视频截图"工具都在做同一件事：每隔 N 秒截一帧，然后用简单的相似度过滤重复。这会导致两个问题：

1. **截到转场残影**：两页之间淡入淡出的中间状态也被当作一页保留
2. **漏掉快翻的页**：2 秒采样，1.5 秒就翻过去的页会被漏掉
3. **全局去重失效**：目录页在第 1 分钟和第 18 分钟各出现一次，只跟上一帧比是识别不出来的

Echo Slides Skill 的核心判断是：

> **一页幻灯片是"画面停止变化的区间"，不是某一帧。**

具体做法：先用 2 秒间隔抽探针帧，把连续不变的帧归成**稳定区间**，取区间中点帧作为代表——这样天然避开了淡入淡出的转场。

---

## 双签名去重：结构 + 颜色缺一不可

识别"这两页是不是同一张"是整个系统里最微妙的地方。Echo Slides Skill 用两个签名同时判断：

| 签名 | 算法 | 感知什么 |
|---|---|---|
| **256 位 dHash** | 差值感知哈希，捕捉相邻像素的亮度梯度 | 版式和内容结构 |
| **8×8 RGB 网格** | 把整张图划成 64 个色块，取各块平均色 | 整体配色方案 |

**为什么两者缺一不可**：

- 两张图如果只是配色不同（比如同一份 PPT 的深色主题和浅色主题），灰度哈希距离是 0，只靠 dHash 会认为它们是同一页。颜色网格签名把它们区分开。
- 两张图如果配色完全一样但内容不同，颜色签名不够用，dHash 的结构感知把它们分开。

**必须同时匹配才算同一页**——这是 Echo Slides Skill 实测零重复的关键。

还有一个额外的**落盘复查**：对真正写到磁盘上的图再做全分辨率哈希，不信任探针阶段的低分辨率判断。

---

## 安装与使用

### 安装

```bash
# 推荐：全局安装，所有 Agent 项目通用
npx skills add xiangzhouEcho/Echo-Slides-Skill -g

# 或者手动克隆
git clone https://github.com/xiangzhouEcho/Echo-Slides-Skill.git \
  ~/.claude/skills/echo-slides-skill

# 依赖
pip install numpy pillow
brew install ffmpeg yt-dlp   # yt-dlp 只处理网络链接时才需要
```

### 基础用法

装好之后，直接对任意 Agent 说：

```text
帮我把这个视频里的幻灯片扒出来：https://youtube.com/watch?v=xxxxx
```

或者本地文件：

```text
把 ~/Downloads/webinar.mp4 里的幻灯片提取出来
```

输出：`slide-001.png`、`slide-002.png`……以及 `slides.json`（每页对应的视频时间戳）。

### 进阶场景

```text
# 动画分步——只要最终状态
把这场 webinar 的 deck 提取出来，动画分步只保留最终状态。

# 摄像头小窗——只分析幻灯片区域
这个视频右侧有摄像头小窗，只分析左边的幻灯片区域。

# 限定时间段
从第 5 分钟到第 20 分钟这一段提取幻灯片就行。

# 提取后汇总核对
提取完把所有页拼成一张图给我逐页核对。
```

对应的底层参数（Agent 会自动选择，也可以直接传）：

```bash
python scripts/extract_slides.py video.mp4 \
  --interval 1          # 采样密度：每秒一帧（默认 2 秒）
  --min-duration 3      # 最短稳定区间：过滤动画分步
  --crop W:H:X:Y        # 裁剪区域：去掉摄像头小窗
  --start 5:00          # 开始时间
  --end 20:00           # 结束时间
  --format jpg          # 输出格式（默认 PNG）
```

---

## 实测数据

在一场 20 分钟的 ECMWF（欧洲中期天气预报中心）网络研讨会上实测：

- **39 页**，1920×1080 分辨率
- **零重复**，零转场残影
- 提取时间：约 90 秒

内置回归测试（`scripts/selftest.py`）合成一份带陷阱的假 deck——包含只改配色的重复页、快速翻页、重复出现的目录页——断言提取结果一页不多一页不少。

---

## 适合 / 不适合的场景

**✅ 适合**：
- 大会演讲 / 网络研讨会（GTC、NeurIPS、ICML、TED……）
- 网课视频（有 PPT 的那种）
- 公司内部录播会议，需要整理 deck 分享给没参会的人
- 看完视频想引用某一页的内容，用 `slides.json` 的时间戳定位原视频

**❌ 不适合**：
- 没有幻灯片的纯人物镜头（每次镜头切换都会被当成翻页）
- 本来就能直接下载 PDF 的情况（直接下 PDF 更快）
- 动画特别多、大量分步展开的场合（调大 `--min-duration` 可以缓解，但不能完全消除）

---

## Skills 生态的意义

Echo Slides Skill 的安装方式（`npx skills add`）是一个值得关注的趋势：Agent Skill 开始像 npm 包一样分发。**Claude Code、Codex、Cursor、OpenCode 用同一套安装命令，同一个 Skill 文件**——不需要为每个 Agent 写不同的插件。

这意味着社区可以围绕"Agent 能做什么"构建一个可复用的技能库，而不是每个 Agent 工具各自为政。Echo Slides Skill 是这个生态里一个完整、自测的参考实现。

---

## 总结

Echo Slides Skill 做了一件小而精确的事：把演讲视频变回幻灯片，消除重复，给每页打上时间戳。双签名去重（dHash 管结构 + RGB 网格管配色）+ 全局比对 + 落盘复查，解决了单纯帧差方案的三个已知漏洞。装进 Agent 后，这件事从"手动截图半小时"变成"说一句话"。

**GitHub**: [xiangzhouEcho/Echo-Slides-Skill](https://github.com/xiangzhouEcho/Echo-Slides-Skill)  
**安装**: `npx skills add xiangzhouEcho/Echo-Slides-Skill -g`

<!--EN-->

## Echo Slides Skill: One Command, All Agents — Extract Deduplicated Slides from Any Talk Recording

You found a great talk on YouTube. The organizers didn't post the slides — only a recording. Manual screenshots mean catching transition frames, duplicating pages, and spending twenty minutes on something that should take seconds.

**Echo Slides Skill** fixes this. One command installs it into your agent environment; then just tell Claude Code (or Codex, Cursor, OpenCode): "extract the slides from this video" — and it does.

```bash
npx skills add xiangzhouEcho/Echo-Slides-Skill -g
```

`-g` installs globally to `~/.claude/skills/` so every project can use it. Drop `-g` for project-local only.

### Core Insight: A Slide Is an Interval, Not a Frame

Most "video screenshot" tools do the same thing: sample every N seconds, filter near-duplicates. This fails in three ways: transition artifacts (mid-fade frames get saved), fast page skips (a slide on screen for 1.5 seconds gets missed at 2-second sampling), and no global dedup (a title slide appearing at minute 1 and minute 18 isn't caught if you only compare against the previous frame).

Echo Slides Skill's key judgment:

> **A slide is "an interval where the screen stops changing," not a single frame.**

It samples probe frames every 2 seconds, groups consecutive unchanged frames into **stable intervals**, and picks the midpoint frame as the representative — naturally avoiding transition artifacts.

### Dual-Signature Dedup: Layout + Color

Deciding "are these two slides the same?" is the subtlest part. Echo Slides uses two signatures simultaneously:

| Signature | Algorithm | What it senses |
|---|---|---|
| **256-bit dHash** | Difference perceptual hash on luminance gradients | Layout and content structure |
| **8×8 RGB grid** | 64 color-block average | Overall color scheme |

Why both? If two slides differ only in color scheme (light vs. dark theme of the same content), grayscale dHash distance is 0 — only the color grid tells them apart. If two slides have identical colors but different content, dHash handles it. **Both must match to count as a duplicate.** This is how the tool achieves zero false duplicates in testing.

A final **write-verify pass** re-hashes at full resolution after writing to disk, catching any duplicates the lower-resolution probe phase may have missed.

### Install & Use

```bash
pip install numpy pillow
brew install ffmpeg yt-dlp   # yt-dlp only needed for URLs

npx skills add xiangzhouEcho/Echo-Slides-Skill -g
```

After installing, just talk to any compatible agent:

```text
Extract the slides from this video: https://youtube.com/watch?v=...
```

Output: `slide-001.png`, `slide-002.png`, … plus `slides.json` with each slide's timestamp.

**Advanced requests**:
```text
Animated builds — keep only final state:
"Extract the deck, animation build steps keep only the final state."

Camera pip window — analyze only the slides region:
"There's a camera window on the right, analyze only the left slide area."

Time range:
"Extract slides from minute 5 to minute 20 only."

Contact sheet for review:
"After extracting, tile all slides into one image for me to check."
```

**CLI flags** (the agent selects these automatically, or you can pass them directly):
```bash
python scripts/extract_slides.py video.mp4 \
  --interval 1         # sampling density: 1 frame/sec (default: 2)
  --min-duration 3     # minimum stable interval: filters animation builds
  --crop W:H:X:Y       # crop to slides-only region
  --start 5:00         # start time
  --end 20:00          # end time
```

### Benchmark

Tested on a 20-minute ECMWF webinar: **39 slides, 1920×1080, zero duplicates, zero transition artifacts.**

The built-in regression test (`scripts/selftest.py`) generates a synthetic trap deck — color-only duplicates, fast page flips, recurring title slides — and asserts the output is exactly right, one slide no more, one slide no less.

### What It's Good For (and Not)

✅ **Works well**: conference talks (GTC, NeurIPS, ICML, TED), webinar recordings, online courses with slides, internal meeting recordings you need to share as a deck

❌ **Not suitable**: pure camera footage with no slides (every cut looks like a slide change), talks where you can already download the PDF directly, highly animated decks with many sequential build steps (tuning `--min-duration` helps but doesn't fully resolve it)

### The Broader Significance: Skills as npm Packages

The `npx skills add` install pattern is worth noting as a trend: Agent Skills are starting to distribute like npm packages. **Claude Code, Codex, Cursor, and OpenCode share the same install command and the same Skill file** — no separate plugin needed for each agent. Echo Slides Skill is a complete, self-tested reference implementation for this emerging ecosystem.

**GitHub**: [xiangzhouEcho/Echo-Slides-Skill](https://github.com/xiangzhouEcho/Echo-Slides-Skill)  
**Install**: `npx skills add xiangzhouEcho/Echo-Slides-Skill -g`
