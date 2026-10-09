---
title: "花叔动画 Skill：用代码让 35 种艺术史风格动起来"
titleEn: "Huashu Art Motion Skill: Making 35 Art History Styles Move with Code"
description: "花叔（alchaincyf）开源 huashu-art-motion（MIT，2.8K stars）：一个给 Claude Code / Codex / Kimi 等 AI Agent 用的 Skill，用程序化 HTML Canvas + ffmpeg 把艺术风格的画面「画出来并让它动」。灵感来自 Tak 的 15 秒艺术史快闪（少女和猫穿越 4 万年），核心机制不是图片切换，而是 5 层运动逻辑代码化生成每一帧——含艺术史线（洞穴岩画→文艺复兴→印象派→8-bit）和专项风格（水墨/敦煌/吉卜力/克里姆特等）共 35 种配方卡，以及 9 种解说视频动画语法。npx skills add alchaincyf/huashu-art-motion 一行安装，输出无声 MP4，样片在 Release 里可直接下载。"
descriptionEn: "Huashu (alchaincyf) open-sourced huashu-art-motion (MIT, 2.8K stars): a Skill for Claude Code / Codex / Kimi that uses programmatic HTML Canvas + ffmpeg to 'draw and animate' art-style scenes in code. Inspired by Tak's 15-second art history speedrun (girl and cat through 40,000 years), the core mechanism is not image transitions but 5-layer motion logic that generates every frame in code — 35 style recipe cards covering art history (cave art → Renaissance → Impressionism → 8-bit) and specialized styles (ink wash, Dunhuang, Ghibli, Klimt, etc.), plus 9 explainer video animation grammars. One-line install: npx skills add alchaincyf/huashu-art-motion. Output: silent MP4. Sample clips downloadable from Release."
pubDate: 2026-10-09
heroImage: "../../assets/images/huashu-art-motion-alchaincyf-art-history-canvas-skill-banner.jpg"
category: "Tech-Experiment"
tags: ["动画", "AI工具", "Claude Code", "Skill", "艺术"]
lang: "zh-CN"
wechatTitle: "花叔动画Skill：用代码让画动起来"
wechatDigest: "MIT 2.8K；35种艺术史风格；Canvas代码生成动画MP4；npx skills add"
---

一支 15 秒的艺术史快闪：少女和猫从 4 万年前的洞穴岩画出发，穿过古埃及、希腊、文艺复兴、印象派、数字像素，每个时代大约一秒，画里的东西都在流动。

花叔（alchaincyf）让 Claude 复刻这支片时，发现"图片之间做转场"的思路走不通。最终改成：**用代码逐帧画出来，让它动**。

这就是 huashu-art-motion——一个给 AI Agent 用的 Skill，把 35 种艺术风格变成代码动画配方。

MIT，2.8K stars，npx skills add alchaincyf/huashu-art-motion。GitHub: https://github.com/alchaincyf/huashu-art-motion

---

## 核心机制：画面全是代码

**huashu-art-motion 不调用图像生成 AI 来生成画面**。所有场景、背景、运动效果都由 HTML Canvas + JavaScript 代码程序化绘制，用 Playwright Chromium 渲染，ffmpeg 导出 MP4。

唯一用到 AI 图像生成的地方是**人物角色帧**（比如少女和猫的形象），这部分通过 AI Agent 当前会话可用的工具桥接，不内置 API Key。

5 层运动逻辑：
1. 固定场景骨架（每个风格一个 `scenes/<id>.js`）
2. 每一幕都是活的：主角动作 + 该风格母题小循环（梵高星空在转、马赛克颜色从石块流过、水墨晕染）
3. 转场用**下一个风格的签名语言**
4. 节拍网格加速（BPM 驱动）
5. 连续叙事锚 + 结尾角色梗

---

## 35 种艺术风格配方

**艺术史线**：
洞穴岩画 → 古埃及 → 希腊 → 罗马 → 哥特 → 文艺复兴 → 印象派 → 后印象/梵高 → 新艺术运动 → 立体派 → 包豪斯 → 波普 → 8-bit → 光线追踪 → 2026

**专项风格**：
水墨、克里姆特、蒙克、敦煌、草间弥生、构成主义、达利、霍珀、吉卜力、蒸汽波、Kirby 漫画、莫奈、修拉、马蒂斯、哈林、伦勃朗、橡皮管卡通、皮影、新海诚、毕加索蓝色时期

每个配方卡都标注了当前质量短板（实际制作时要先超越短板）。

---

## 9 种解说视频动画语法

除了艺术史快闪风格，Skill 还包含解说类视频的动画语法（8 种附示范片 + 参数化片段，第 9 种为讲解员参考实现）：

Kurzgesagt 风、Vox 风、白板动画、3Blue1Brown 数学可视化、Storytime 叙事、动态文字、发布会 UI、财经图表、讲解员科普

---

## 安装与使用

```bash
# 安装到你的 Claude Code / Codex 环境
npx skills add alchaincyf/huashu-art-motion

# 渲染单段静帧预览
python render.py --solo <id> --stills 0.3 --out

# JSON 驱动的精确时长片段
python render.py --spec <spec.json> --out

# 拆解参考动画（转场、节拍网格、运动热图）
python analyze/breakdown.py --video

# 验收检查
python qa.py
```

依赖：`uv`、`ffmpeg`、`playwright install chromium`。

样片（v1.0.0）：
- `art-motion-35-styles.mp4`（52MB，无声，35 段样片）—— Release 里直接下载
- `huashu-art-motion-v1.0.0.zip`（39MB，完整工程包）

---

## 平台与 Agent 支持

- **平台**：macOS Apple Silicon 验证通过；uv/ffmpeg/Playwright 跨平台，理论支持 Windows/Linux
- **Agent**：Claude Code 通过；Codex 在线回归通过；Kimi 测试账户条件阻塞，待补验

---

## License 注意

代码和文档是 MIT，但有例外：
- **花叔卡通角色帧**（`hero/` 目录相关资产）仅限本 Skill 示范，不随 MIT 授权
- 字体：SIL OFL（笔顺衍生数据 Arphic Public License）

商用时需注意角色形象版权。

---

## 一句话说清楚

huashu-art-motion 是一个 AI Agent Skill，用程序化 HTML Canvas + ffmpeg 把 35 种艺术史风格变成代码动画——不是图片切换，是每帧代码画出来的流动画面，输出无声 MP4，一行 `npx skills add` 安装，Claude Code 和 Codex 可直接使用。

---

> MIT（含 License 例外，见上）。花叔 alchaincyf，2026-10-06 创建，2.8K stars。开源仅供学习参考。

---

<!--EN-->

## Huashu Art Motion Skill: Making 35 Art History Styles Move with Code

A 15-second art history speedrun: a girl and a cat start from a 40,000-year-old cave painting, travel through ancient Egypt, Greece, the Renaissance, Impressionism, and digital pixels — one era per second, with everything in the frame flowing.

When Huashu (alchaincyf) asked Claude to recreate this clip, the "transitions between images" approach didn't work. The solution: **draw every frame in code, and make it move**.

That's huashu-art-motion — a Skill for AI Agents that turns 35 art styles into code-driven animation recipes.

MIT, 2.8K stars, `npx skills add alchaincyf/huashu-art-motion`. GitHub: https://github.com/alchaincyf/huashu-art-motion

---

### Core Mechanism: Everything Is Code

**huashu-art-motion does not call an image generation AI to produce the frames.** All scenes, backgrounds, and motion effects are drawn programmatically via HTML Canvas + JavaScript, rendered by Playwright Chromium, and exported to MP4 via ffmpeg.

The only part where AI image generation is used is for **character frames** (the girl and cat appearance), bridged through whatever tools are available in the Agent's current session — no built-in API key.

Five motion layers:
1. Fixed scene skeleton (one `scenes/<id>.js` per style)
2. Every shot is alive: character movement + style-signature motif loop (Van Gogh stars rotating, mosaic colors flowing between tiles, ink wash spreading)
3. Transitions use the **signature visual language of the next style**
4. Beat-grid acceleration (BPM-driven)
5. Continuous narrative anchor + ending character callback

---

### 35 Art Style Recipes

**Art history line**: Cave art → Ancient Egypt → Greece → Rome → Gothic → Renaissance → Impressionism → Post-Impressionism/Van Gogh → Art Nouveau → Cubism → Bauhaus → Pop → 8-bit → Ray tracing → 2026

**Specialized styles**: Ink wash, Klimt, Munch, Dunhuang, Kusama, Constructivism, Dalí, Hopper, Ghibli, Synthwave, Kirby comics, Monet, Seurat, Matisse, Haring, Rembrandt, rubber-hose cartoon, shadow puppetry, Makoto Shinkai, Picasso Blue Period

Each recipe card notes its current quality weak points (expected to overcome them in practice).

---

### 9 Explainer Video Animation Grammars

Beyond the art history speedrun format, the Skill also includes animation grammars for explainer videos (8 with sample clips + parameterized segments, 9th with presenter reference): Kurzgesagt style, Vox style, whiteboard, 3Blue1Brown math visualization, Storytime narrative, kinetic typography, product launch UI, financial charts, presenter science explainer.

---

### Install and Use

```bash
npx skills add alchaincyf/huashu-art-motion
python render.py --solo <id> --stills 0.3 --out
python render.py --spec <spec.json> --out
```

Requires: `uv`, `ffmpeg`, `playwright install chromium`.

Sample clips (v1.0.0): `art-motion-35-styles.mp4` (52 MB, silent, 35 segments) — downloadable from Release.

---

### License Notes

Code and docs: MIT. Exceptions:
- **Huashu cartoon character frames** (hero/ directory): for demonstration use within this Skill only, not covered by MIT
- Fonts: SIL OFL; stroke data: Arphic Public License

Verify character design rights before commercial use.

---

### TL;DR

huashu-art-motion is an AI Agent Skill that turns 35 art history styles into programmatic Canvas animations — not image transitions, but every frame drawn by code as flowing visuals. Outputs silent MP4. One-line install, works with Claude Code and Codex.

---

> MIT (with exceptions noted above). alchaincyf (Huashu), created 2026-10-06, 2.8K stars. For reference only.
