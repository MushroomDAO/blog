---
title: "一条命令搞定产品全套发布物料：Marketing Studio 完全上手指南"
titleEn: "One Command for Your Full Product Launch Asset Suite: Marketing Studio Complete Guide"
description: "ucsandman/marketing-studio（85⭐）是一个 Claude Code 技能集——在你的产品仓库里输入 /marketing，AI Agent 自动完成品牌推导、录屏、Logo 动画、发布视频、配音配乐、社媒切片、OG 素材的全流水线生产。"
descriptionEn: "ucsandman/marketing-studio (85⭐) is a Claude Code skill suite — type /marketing in your product repo and an AI agent auto-produces brand tokens, screen recording, logo animation, launch video, voiceover, social clips, and OG assets in one pipeline run."
pubDate: "2026-07-13"
updatedDate: "2026-07-13"
category: "Tech-Experiment"
tags: ["Claude Code", "营销自动化", "开源", "视频生成"]
heroImage: "../../assets/images/marketing-studio-claude-code-one-command-launch-assets-banner.jpg"
---

> 本文基于开源项目 **ucsandman/marketing-studio**（85⭐，MIT），2026 年 7 月上线，一套跑在 Claude Code 上的 AI 营销物料流水线。

---

## 你上一次做产品发布物料，花了多长时间？

Logo 动画、产品演示视频、发布视频、配音配乐、各平台社媒切片、OG 封面图……

如果都要做，通常是这样的：设计师几天、视频剪辑几天、文案一天、各平台适配半天。还没算来回修改的时间。

Marketing Studio 想把这件事变成一条命令。

---

## 它能做什么

在你的产品仓库里运行 Claude Code，输入 `/marketing`，AI Agent 按固定顺序生产出全套物料：

| # | 物料 | 技术 |
|---|------|------|
| 1 | **Logo 揭幕动画** | Blender 建模 + Remotion 合成 |
| 2 | **产品演示视频**（自动录屏，摄像机推拉，鼠标特效） | Playwright |
| 3 | **30–90 秒发布视频**（演示 + Logo + 文案） | Remotion |
| 4 | **配音 + 配乐** | ElevenLabs |
| 5 | **各平台社媒切片**（X、LinkedIn、TikTok） | Remotion |
| 6 | **OG 封面图、动态 OG 循环、README GIF** | Remotion |

顺序是精心设计的：最便宜的合成先跑（品牌色问题先暴露），演示只录一次然后所有视频复用，配音最后做（等视频锁定）。整个流程有 manifest 文件，中断后从断点续跑，不从头开始。

---

## 真实案例

项目 README 里的 `examples/` 目录放了两个真实产品的完整输出，未经人工修改：

**noban.gg（CS2 皮肤套利仪表板）：** 60 秒发布视频（含 AI 配音配乐）+ 产品演示 + Logo 揭幕 + X/LinkedIn 切片 + 动态 OG。

**paperroute.gg（壁纸广告网络）：** 同套物料，包括竖版、方形、4:5 比例各平台适配。

README 顶部那个 GIF 就是 paperroute 的动态 OG Loop，由品牌 token 直接生成，没有人工设计。

---

## 快速安装

**必须条件：**
- Claude Code（`claude` 命令在 PATH 里）
- Node 20+
- Python 3.10+

**可选（没有会自动降级，不会报错）：**
- Blender——3D Logo 揭幕动画
- ElevenLabs API key——AI 配音配乐
- ComfyUI——AI 背景图

```bash
# 1. 克隆引擎仓库
git clone git@github.com:ucsandman/marketing-studio.git
cd marketing-studio

# 2. 安装 Remotion 依赖
cd studio && npm install && cd ..

# 3. 配置可选工具（没有就跳过）
cp .env.example .env
# 编辑 .env，填入 BLENDER_PATH 和 ELEVENLABS_API_KEY

# 4. 把 /marketing 等技能安装进 Claude Code
node scripts/install-skills.mjs

# 5. 验证工具链
python launch.py --check
```

安装后 Claude Code 全局可用以下命令（在任何仓库里）：

| 命令 | 作用 |
|------|------|
| `/marketing` | 完整流水线——从品牌推导到所有物料 |
| `/logo-reveal` | 只做 Logo 动画 |
| `/product-demo` | 只录产品演示 |
| `/launch-video` | 只合成发布视频 |
| `/audio-track` | 只生成配音配乐 |
| `/social-clip` | 只做社媒切片 |
| `/og-assets` | 只做 OG 素材 |

---

## 在你的产品里跑起来

去你想做物料的产品仓库：

```bash
cd /path/to/your-product
claude
> /marketing
```

Agent 会集中问一批问题（品牌信息、目标平台、是否要音频、是否开启检查点模式），然后自动跑完整流程。

**如果是新品牌，Agent 会自动推导：** 它读取你仓库里的 `DESIGN.md`、Tailwind 配置、CSS 变量，推断出品牌色、字体、调性，只对推断不了的东西才问你。

所有物料最终被复制回你的产品仓库（或你指定的目录），引擎仓库本身不留你的产品文件。

---

## 核心设计拆解

### 品牌即数据

所有品牌信息存在 `brands/<id>.json`——13 个颜色 token、3 种字体、标语、语气规则、动效性格，Zod 校验。

```json
{
  "id": "yourproduct",
  "name": "Your Product",
  "tagline": "The thing you say it does",
  "colors": {
    "primary": "#...",
    "accent": "#...",
    ...
  },
  "fonts": { "heading": "...", "body": "...", "mono": "..." },
  "voice": { "tone": "confident", "avoid": ["revolutionary", "game-changing"] },
  "motion": { "personality": "snappy", "easing": "spring" }
}
```

模板只读 `getBrand(brandId)`，永远不硬编码品牌值，所以加一个新产品只是加一个 JSON 文件，不是 fork 一个新仓库。

### Remotion 是渲染骨架

所有最终视频都通过 Remotion 合成：`SocialClip`、`ProductDemo`、`LogoReveal`、`LaunchVideo`、`AnimatedOG`——每个都是一个 React 组件，接受品牌 token 做参数。

### Feeder 模块提供原始素材

- **Playwright**：录你正在跑的 App，自动加摄像机推拉和鼠标动效
- **Blender**（可选）：无头渲染 3D Logo 揭幕动画
- **ElevenLabs**（可选）：生成配音和背景音乐
- **ComfyUI**（可选）：生成 AI 背景图

任何 feeder 缺失时自动降级——Blender 没装？Logo 动画跳过；没有 ElevenLabs key？视频无配音，其余照常。

### 流水线护栏

**文案审查器（Copy Linter）：** 每一行生成的文字都经过检查，过滤 em dash、夸张词、AI 腔（"revolutionary"、"game-changing" 之类），不过就不能进入渲染。

**Mission Control：** 本地可视化审批页面。每个素材落地时可以点击预览，审批或请求重做（带备注），Agent 接到重做请求后重新跑那个节点，不需要开终端。

**导出矩阵：** 发布视频和社媒切片自动扇出到 16:9、9:16、1:1、4:5 四个比例——用响应式布局而不是裁剪，每个比例都是独立排版。同时生成带烧录字幕的哑播版本和 SRT/VTT 文件。

**素材缓存：** 没有改动的 App 页面不重新录屏，用内容 hash 判断缓存是否有效。

**Paste-ready 发帖工具包：** 每个平台一个文件夹，里面是对应比例视频 + 校验过的文案 + 替代文字 + 发帖清单 + machine-readable 的 `manifest.json`。

---

## 配套技能：让发布更完整

除了物料生产，项目还附带了几个实用技能：

| 技能 | 作用 |
|------|------|
| `/polish` | 录屏前做 UI 质量检查（对齐、间距、状态、细节） |
| `/frontend-verify` | 无头路由验证（控制台错误、请求失败、文本断言） |
| `/de-vibe` | 去除 AI 生成指纹（安全性问题、废话文案、通用默认值） |
| `/ship` | 验证 → 文档 → 密钥扫描 → commit → push 完整仪式 |
| `/launch` | 各渠道发布稿（X、LinkedIn、Show HN、邮件），带审批门控 |

---

## 手动控制（不走 Agent 也能用）

所有 Agent 做的事都可以手动跑：

```bash
# 健康检查 + 启动 Remotion Studio
python launch.py

# 每个合成的第 0 帧截图（冒烟测试）
node scripts/smoke.mjs

# 手动渲染 Logo 动画
cd studio && npx remotion render LogoReveal ../out/<brand>/logo.mp4 \
  --props='{"brandId":"yourproduct","cta":"立即体验"}'

# 文案审查
node scripts/lint-copy.mjs props/<brand>-launch.json

# 导出矩阵（仅截图）
node scripts/render-matrix.mjs <brand> --stills-only

# 启动 Mission Control 审批页
node scripts/mission-control.mjs <brand>
```

---

## 仓库结构

```
brands/            品牌 token（JSON，Zod 校验）
studio/            Remotion 项目：所有视频合成
feeders/blender/   headless Blender 场景（3D Logo）
feeders/capture/   Playwright 录屏（产品演示）
feeders/audio/     ElevenLabs 客户端（配音 + 配乐）
feeders/comfy/     ComfyUI 客户端（AI 背景，可选）
skills/            所有 Claude Code 技能文件
examples/          两个真实产品的完整输出
scripts/           各类构建脚本、Mission Control 等
docs/PLAYBOOK.md   完整操作手册：引擎地图、品牌入驻、坑点
launch.py          健康检查 + Remotion Studio 一键启动
```

---

## 适合哪些场景

**最适合：**
- 独立开发者 / 小团队，产品快速上线，没有专职设计师
- 定期发版本更新，每次都需要重新做一套素材
- 想测试不同品牌调性，快速出多套方案

**不适合：**
- 需要强烈人工创意输入的旗舰发布（AI 输出有通用感，高端发布仍需人工润色）
- 没有跑起来的 Web App（`/product-demo` 需要能录屏的真实 URL）

---

GitHub：[github.com/ucsandman/marketing-studio](https://github.com/ucsandman/marketing-studio)  
License：MIT  
Remotion 文档：[remotion.dev](https://remotion.dev)

© 2026 Author: Mycelium Protocol

<!--EN-->

## One Command for Your Full Product Launch Asset Suite: Marketing Studio Complete Guide

> Based on **ucsandman/marketing-studio** (85⭐, MIT) — a Claude Code skill suite for automated marketing asset production. Launched July 2026.

---

### What It Does

Type `/marketing` in any product repo using Claude Code. An AI agent auto-produces:

| # | Asset | Tech |
|---|-------|------|
| 1 | Logo reveal animation | Blender + Remotion |
| 2 | Product demo with camera zooms + cursor effects | Playwright |
| 3 | 30–90s launch video | Remotion |
| 4 | Voiceover + music | ElevenLabs |
| 5 | Social clips (X, LinkedIn, TikTok) | Remotion |
| 6 | OG image, animated OG loop, README GIF | Remotion |

The pipeline order is deliberate: cheapest compositions render first (brand token bugs surface early), the demo is filmed once and feeds everything downstream, audio is scored only after the launch video is picture-locked.

---

### Install

**Required:** Claude Code, Node 20+, Python 3.10+  
**Optional (degrades cleanly without):** Blender (3D logo), ElevenLabs API key (audio), ComfyUI (AI backdrops)

```bash
git clone git@github.com:ucsandman/marketing-studio.git
cd marketing-studio
cd studio && npm install && cd ..
cp .env.example .env              # add BLENDER_PATH / ELEVENLABS_API_KEY if you have them
node scripts/install-skills.mjs   # installs /marketing and friends into ~/.claude/skills
python launch.py --check          # verify the toolchain
```

Then from your product repo:
```bash
claude
> /marketing
```

The agent asks one batched round of questions, then runs the full pipeline. If your brand is new, it derives tokens from your repo's design system (DESIGN.md, Tailwind config, CSS vars) and only asks for what it can't infer.

---

### Individual Skills

Each asset type also runs standalone:

| Skill | Does |
|-------|------|
| `/marketing` | Full pipeline |
| `/logo-reveal` | 3D logo animation only |
| `/product-demo` | Screen recording only |
| `/launch-video` | Hero video only |
| `/audio-track` | Voiceover + music only |
| `/social-clip` | Platform clips only |
| `/og-assets` | OG image/loop/GIF only |

Supporting skills: `/polish` (pre-film UI check), `/de-vibe` (remove AI fingerprint), `/frontend-verify` (headless route check), `/ship` (commit+push ritual), `/launch` (per-channel post drafts).

---

### How Brands Work

Every brand is a validated JSON file: 13 color tokens, 3 fonts, tagline, voice rules, motion personality. Templates call `getBrand(brandId)` — no hardcoded values. Adding a new product = one JSON file, not a fork.

---

### Pipeline Guardrails

- **Copy linter**: every generated line is gated for em dashes, hype, and AI-slop vocabulary before it can reach a render.
- **Export matrix**: final video fans into 16:9, 9:16, 1:1, 4:5 via responsive layout (not crops), with burned-caption muted variants and SRT/VTT sidecars.
- **Mission Control**: local click-to-approve web console — watch assets land, approve or request redo, no terminal required.
- **Footage cache**: content-hash caching so unchanged app UIs are never re-filmed.

---

### Manual Controls

```bash
python launch.py                          # health check + Remotion Studio
node scripts/smoke.mjs                    # frame-0 still of every composition
node scripts/mission-control.mjs <brand>  # approval UI
node scripts/lint-copy.mjs props/<brand>-launch.json
```

GitHub: [github.com/ucsandman/marketing-studio](https://github.com/ucsandman/marketing-studio)

© 2026 Author: Mycelium Protocol
