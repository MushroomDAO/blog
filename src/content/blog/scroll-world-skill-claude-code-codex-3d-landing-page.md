---
title: "按头安利：scroll-world —— 一句话让 Fable 5 / GPT-5.6 替你造一个滚动飞进去的 3D 落地页"
titleEn: "Must Have: scroll-world — One Prompt to a Scroll-Cinematic 3D Landing Page in Claude Code or Codex"
description: "scroll-world 是一个开源 Agent Skill（1600+ ⭐），在 Claude Code（Fable 5）或 Codex（GPT-5.6 sol）里一句话调用：Agent 负责采访你、调 Higgsfield 生成等距 3D 场景图和无缝摄像机飞越视频、再组装成一套「滚动驱动时间」的落地页——同款 Apple 滚动体验，适配任何品牌或行业。"
descriptionEn: "scroll-world is an open-source Agent Skill (1600+ ⭐) for Claude Code (Fable 5) or Codex (GPT-5.6 sol): the agent interviews you, calls Higgsfield to generate cohesive isometric 3D diorama scenes and seamless camera-flight videos, then wires them into a scroll-scrubbed landing page — same technique as Apple's product scroll-throughs, applied to any brand."
pubDate: "2026-07-14"
updatedDate: "2026-07-14"
category: "Tech-Experiment"
tags: ["Claude Code", "Codex", "3D落地页", "开源工具"]
heroImage: "../../assets/images/scroll-world-skill-claude-code-codex-3d-landing-page-banner.jpg"
---

> GitHub：[oso95/scroll-world](https://github.com/oso95/scroll-world) · ⭐ 1,607 · 🍴 212  
> 许可：MIT  
> 依赖：[Higgsfield CLI](https://higgsfield.ai)（付费积分）+ `ffmpeg` + Python 3

---

## 它做出来的东西长什么样

两个 demo 说明一切：

**Pearl & Co.（奶茶品牌）**：等距黏土泥塑风格。农场 → 珍珠厨房 → 旗舰店 → 配送 → 社区广场 → 主打产品，六个场景连成一个迷你世界，摄像机从每个场景外部飞入内部再平滑衔接下一个，全程没有剪切。

**BELVEDERE（豪宅品牌）**：超写实建筑摄影风格。摄像机从门廊穿过落地玻璃飞入大厅，再滑进泳池别墅，像在高端地产纪录片里。

两个 demo 在同一份 SKILL.md 指导下、同一套 pipeline 里生成——区别只有一句话的艺术方向描述。

---

## 为什么 1600 颗 Star 在一周内炸出来

这个效果此前只在苹果官网、Emons 物流这类有专业 3D 动效团队的公司落地页上见过。

scroll-world 做的事是：**把这套体验的生产门槛降到一个 Skill 调用**。

核心洞察：苹果的滚动产品页不是什么神奇的 3D 实时渲染。它的原理是：**把预渲染好的视频按滚动位置"擦洗"（scrub）**——scroll 只是在推进时间轴，视频是早就渲好的。摄像机是真实运动的；scroll 只驱动时间。

这个原理不难实现，难的是：

1. 生成一套风格高度一致的场景图（你不能六个场景有六种渲染风格）
2. 场景之间的摄像机过渡片段必须**帧完全连续**，不能有跳切
3. 把这些素材拼成一套能到处跑的前端框架无关的 scrub 引擎

scroll-world 把这三件事全打包进了一个 SKILL.md。

---

## 工作流程拆解

### Step 1 — Agent 采访你

Agent 不给你一个问卷，而是用开放问题引导：

- **主题**：「这个世界要讲什么故事？你的品牌、客户的品牌、或者任何一个 idea」
- **品牌 kit**：从网址自动抓（`higgsfield marketing-studio brand-kits fetch --url <site>`），或手动给调色板 + 品牌名 + 气质词
- **艺术方向**：默认是「软质哑光低多边形黏土沙盘，等距视角，移轴微缩感，温暖灯光」；也可选扁平纸艺、光滑玩具、黏土动画、霓虹夜景、超写实建筑摄影
- **场景顺序**：Agent 根据你的业务价值链提案，你来编辑。通常 5–7 个场景

### Step 2 — 生成场景静图

每个场景一张等距 3D 图，用 **GPT Image 2**（`higgsfield generate create gpt_image_2`）并发生成。

关键：**Style Preamble 在所有场景中一字不差地复用**，这是让所有场景看起来像同一个世界的方法：

```
Isometric low-poly 3D diorama floating as a small rounded island on a plain solid
[BG_HEX] background with a soft contact shadow beneath it. Soft matte clay 3D render,
rounded toy-model shapes, gentle warm studio lighting, soft long shadows, tilt-shift
miniature look. Cohesive color palette of [PALETTE]. Highly detailed, centered
composition, absolutely no text, no letters, no numbers, no logos.
```

### Step 3 — 场景"浮起来"（可选）

如果想让沙盘浮在深色背景上（而不是实色方块），用内置的 `knockout.py` 做背景抠除——边界连通区域漫水填充，保留内部与背景同色的部分（比如奶油色墙壁不被误抠）。

这些静图同时作为**视频海报**和**懒加载降级图**。

### Step 4 — 生成摄像机飞越视频

这是整套 pipeline 最核心的部分，分两类片段：

**Dive-in clips（飞入片段）**：每个场景一个，摄像机从外部高空向场景内部飞入，`--start-image` 是该场景静图。

**Connector clips（连接片段）**：相邻场景之间各一个，`--start-image` 是第 i 个 dive 的**最后一帧**，`--end-image` 是第 i+1 个 dive 的**第一帧**。

```
N 个场景 → N 个 dive-in + (N-1) 个 connector
```

视频模型默认 **Seedance 2.0**，备选 **Kling 3.0**（720p 原生）和 **Seedance 2.0 Mini**（低分辨率草稿版）。关键约束：只有能同时接受 `--start-image` 和 `--end-image` 参数的模型才能保证帧精确缝合。

**「无缝链」是这整个体验的命门。** SKILL.md 花了大量篇幅在这一条规则上：connector 的起点必须从 dive_i 渲染出来的实际最后一帧提取，终点从 dive_{i+1} 的实际第一帧提取——用 ffmpeg 逐帧截取，而不是拿静图。任何一帧不连续都会在滚动时出现"弹跳感"。

### Step 5 — 装配 scrub 引擎

`references/scrub-engine.js` 是一个纯 Vanilla JS、自包含的 scrub 引擎。不假设任何前端框架——可以直接丢进普通 HTML、Next.js、Vue、Python 静态页。

工作方式：把所有 dive-in + connector 的 `<video>` 标签预缓存，按 scroll 位置映射到视频时间轴，用 `requestAnimationFrame` 逐帧 seek。有 blob-seek 和 seam crossfade 的处理，iOS Safari 也有专门的预加载策略。

---

## 安装方式

### Claude Code（推荐——插件模式）

```
/plugin marketplace add oso95/scroll-world
/plugin install scroll-world@scroll-world
```

安装后直接问 Agent 「帮我做一个 3D 世界落地页」，或者显式调用 `/scroll-world`。

### Codex（GPT-5.6 sol）——via skills CLI

```bash
npx skills add oso95/scroll-world            # 安装时选择 Agent（可选 Codex、Claude Code 等）
npx skills add oso95/scroll-world -a codex   # 直接指定 Codex
```

在 Codex 里用 `$scroll-world` 调用，或者直接说「帮我做一个 scroll-through 落地页」。

### 手动（drop-in 模式）

```bash
git clone https://github.com/oso95/scroll-world
cp -R scroll-world/skills/scroll-world ~/.claude/skills/   # Claude Code
cp -R scroll-world/skills/scroll-world ~/.codex/skills/    # Codex
```

---

## 前置依赖

| 依赖 | 用途 |
|------|------|
| [Higgsfield CLI](https://higgsfield.ai)（需账号 + 积分） | 生成场景图 + 摄像机视频 |
| `ffmpeg` / `ffprobe` | 提取边界帧、拼接视频 |
| Python 3 + Pillow（可选） | 场景背景抠除（floating island 效果） |

积分消耗估算：N 个场景 ≈ N 次图像生成 + (2N-1) 次视频生成。5 个场景大约 9 次视频生成，每次 3–8 分钟。Agent 会在后台并发跑，不会占用你的前台。

---

## 两次对比：同一品牌，Fable 5 vs. GPT-5.6 sol

这个 skill 出名的一部分原因是作者在演示视频里做了一件让人信服的事：**把同一个品牌在 Claude Code 和 Codex 里各跑一遍**，输出结果并排展示。

用的是同一份 SKILL.md、同一套 Higgsfield pipeline、同一个品牌 brief——差异只来自 Fable 5 和 GPT-5.6 sol 在「采访你的方式」「理解 SKILL.md 的深度」「生成提示词的准确度」上的不同。这是目前为数不多的、在同一任务上公开对比两款最新旗舰模型的实测。

---

## 文件结构

```
skills/scroll-world/
├── SKILL.md                    完整操作流程 + 无缝规则 + 已知坑
└── references/
    ├── prompts.md              采访清单 + 所有 Higgsfield 提示词模板
    ├── pipeline.md             可直接粘贴的 Bash 批处理脚本
    ├── scrub-engine.js         可移植的 Vanilla JS scrub 引擎
    ├── index-template.html     最简落地页模板
    └── knockout.py             场景背景抠除脚本
```

---

## 适合的场景

- **品牌/产品落地页**：有清晰价值链的品牌（从原料到成品到交付）
- **活动/主题站**：发布会官网、年度报告、节日专题
- **portfolio**：设计师 / 创意工作室的作品集
- **B2B 营销页**：把抽象的业务流程做成可探索的视觉旅程

对纯文字型产品（SaaS、工具类）效果会弱一些——这套体验需要有"场景感"的物理空间。

---

GitHub：[github.com/oso95/scroll-world](https://github.com/oso95/scroll-world)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Must Have: scroll-world — One Prompt to a Scroll-Cinematic 3D Landing Page

> GitHub: [oso95/scroll-world](https://github.com/oso95/scroll-world) · ⭐ 1,607 · 🍴 212 · MIT

---

### What It Produces

scroll-world is an Agent Skill for Claude Code (Fable 5) or Codex (GPT-5.6 sol) that builds an immersive scroll-scrubbed "fly through the world" landing page for any brand or industry.

As the visitor scrolls, a camera flies from *outside* each scene *into* its interior, then flows seamlessly into the next — no cuts. One continuous connected flight through a generated 3D world.

Two demo styles shown in the repo video:
- **Pearl & Co.** (bubble tea): soft clay isometric diorama — farms, pearl kitchen, flagship shop, delivery, community plaza
- **BELVEDERE** (luxury real estate): ultra-photorealistic cinematic — camera glides through floor-to-ceiling glass, past fireplaces, into a canyon-view infinity pool

Same skill, same pipeline, different one-line art direction.

---

### The Core Insight

Apple's scroll-through product pages aren't real-time 3D. They're pre-rendered videos **scrubbed by scroll position** — scroll advances time, the camera genuinely moves. scroll-world applies this to any brand:

1. Cohesive scene stills (same style preamble across all — that's what makes them look like one world)
2. Per-scene "dive-in" clips + between-scene "connector" clips with **frame-identical seams**
3. A portable vanilla-JS scrub engine that works in plain HTML, Next.js, Vue, anything

---

### Pipeline Overview

**Step 1 — Interview:** Agent asks open questions: what the world is about, brand kit (fetched from a URL or described), art direction, ordered scenes.

**Step 2 — Scene stills:** GPT Image 2 via Higgsfield, generated concurrently, all sharing the exact same style preamble.

**Step 3 — Float scenes (optional):** Background knockout (`knockout.py`) for floating diorama islands on a dark page.

**Step 4 — Camera videos:**
- `N` dive-in clips (each: `--start-image` = scene still)
- `N-1` connector clips (each: `--start-image` = last frame of dive_i, `--end-image` = first frame of dive_{i+1})

Default video model: **Seedance 2.0**. The only usable models are those that accept both `--start-image` and `--end-image` — that's the seam requirement.

**The seam rule:** connector boundary frames must be extracted from the *rendered* dive videos with ffmpeg, never from the stills. One bad seam shows as a "pop" on scroll.

**Step 5 — Scrub engine:** `references/scrub-engine.js` — self-contained vanilla JS, no framework assumptions. Blob-seek, lazy load, seam crossfade, iOS Safari priming.

---

### Install

```bash
# Claude Code plugin (recommended)
/plugin marketplace add oso95/scroll-world
/plugin install scroll-world@scroll-world

# Codex via skills CLI
npx skills add oso95/scroll-world -a codex

# Manual drop-in
cp -R scroll-world/skills/scroll-world ~/.claude/skills/
```

**Requirements:** Higgsfield CLI (paid credits) + `ffmpeg` + Python 3 with Pillow (optional).

Cost: ~N image gens + (2N-1) video gens. 5 scenes ≈ 9 video generations at 3–8 min each, all run concurrently in the background.

---

### Why It Went Viral

The author demoed the same brand built twice — once in Claude Code with Fable 5, once in Codex with GPT-5.6 sol — side by side. Same SKILL.md, same Higgsfield pipeline, same brief. One of the first public head-to-head comparisons of both flagship models on an identical creative task.

GitHub: [github.com/oso95/scroll-world](https://github.com/oso95/scroll-world)

© 2026 Author: Mycelium Protocol
