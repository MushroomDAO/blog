---
title: "Editable-Design：中山大学 12 人团队用 Codex 当设计师，输出可编辑 HTML 海报"
description: "yejy53/Editable-Design，Apache 2.0，Python，1,118 stars，arXiv 2609.04034。中山大学 12 人学术团队。核心思路：扩散模型生成的是不可编辑的光栅图，这个项目让 Codex CLI 充当设计师，直接生成 HTML/CSS，输出可拖拽编辑的海报、可导出的 pptx、以及完整的 Agent 设计轨迹回放。三件重要事实：硬绑 OpenAI Codex CLI、Paper Fig 技能存在许可证灰色地带、2026-09-08 之后零提交。"
pubDate: 2026-09-27
heroImage: "../../assets/images/editable-design-codex-skill-html-css-poster-agent-sysu-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["Codex", "设计自动化", "HTML/CSS", "AI Agent", "开源拆解", "学术"]
lang: "zh-CN"
wechatTitle: "Editable-Design：Codex当设计师生成可编辑HTML海报"
wechatDigest: "中山大学arXiv；Codex生成可编辑HTML海报；设计轨迹可回放；硬绑OpenAI"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 从问题出发：扩散模型输出的是死图

Stable Diffusion、FLUX、Midjourney 生成的是像素阵列——文字选不中、层改不了、价格改错了就得重画。对于海报、信息图、学术方法图这类需要频繁修改的场景，不可编辑是刚性痛点。

**yejy53/Editable-Design** 的解法是换掉整条生成管线：不用扩散模型画图，改用 Codex CLI 写 HTML/CSS。输出不是图片，是一个可以在浏览器里编辑的网页——文字是真文字，布局是真 CSS，图层是真 DOM 节点。

仓库：github.com/yejy53/Editable-Design  
**Stars：1,118 | License：Apache 2.0 | 语言：Python | 创建：2026-08-24 | arXiv：2609.04034**

作者：叶君言（Junyan Ye），中山大学博士生；论文共 12 位作者，均来自中山大学（SYSU）学术团队。

---

## 三个技能包，一个执行模型

项目以 Codex CLI Skills 的形式交付，`skills/` 目录下有三个技能：

| 技能 | 用途 | 主要输出 |
|------|------|---------|
| `editable-design` | 海报、信息图、宣传图 | HTML、editor.html、layers.html、replay/、PNG |
| `html-to-pptx` | 将兼容 HTML 转为 PowerPoint | 可编辑 .pptx |
| `paper-fig` | 学术方法图/架构图 | 可编辑 .pptx |

### editable-design 执行流程

1. Agent 做创意增强（Prompt Enhancement）
2. 生成一张参考图（存入 `reference/`，不随输出一起交付）
3. 读参考图的构图规律，规划排版
4. 为需要写实图的槽位生成光栅资产
5. 写定宽 `index.html`，真实字体排印 + HTML 几何布局
6. 用 Playwright 渲染截图验证输出
7. 生成 `editor.html`（扫描视图 + 展开图层视图）
8. 写 `replay/index.html`——设计决策的完整可回放审计轨迹
9. 可选：调用 html-to-pptx 技能导出为 `.pptx`

**SKILL.md 的关键约束**：禁止 Agent 自行绘制 SVG 插图（图形内容只能是生成的光栅或文字/几何）；首选嵌入式 Lucide 图标集；"你是设计师，不是顾问"——Agent 自主决策排版，不问用户。

---

## 三个真正有价值的设计点

### 1. 输出可编辑

生成结果里，文字是真实可选中的 HTML 文本，不是嵌入图片里的像素。配套的 `editor.html` 提供鼠标拖拽编辑界面。`html-to-pptx` 转换后，PPT 里的文本框、形状、图片元素各自独立可编辑——不是把整张 HTML 截图当成 PPT 背景。

### 2. Agent Design Replay（设计轨迹回放）

`replay/index.html` 是这个项目最独特的功能：记录 Agent 完整的设计决策路径，可以逐步回放每一层是怎么被添加的、每个创意选择背后的推理链路。主流设计工具（Figma、Canva）没有这个——你能看到最终结果，但看不到 AI 的决策过程。这在学术价值和调试价值上都是真实的差异化。

### 3. Paper Fig（学术方法图）

专门针对学术论文的方法流程图、架构图，直接从文字描述生成可编辑 `.pptx`。这是一个被严重低估的需求：画论文方法图费时费力，Visio 太重，手画 TikZ 需要学习成本，PPT 拖方块又难看。Paper Fig 填的是这个缝。

---

## 三个需要正视的问题

### 1. 硬绑 OpenAI Codex CLI

`agents/` 目录下只有 `openai.yaml`，没有 Claude Code 的配置文件，没有其他运行时支持。这不是通用工具——必须安装 Codex CLI 并持有有效的 OpenAI 账号才能运行。README 明确提示："This community project is not an official OpenAI project."

Claude Code 用户、Gemini CLI 用户无法直接使用，需要自己重写 Skill 基础设施。

### 2. Paper Fig 的许可证灰色地带

`THIRD_PARTY_NOTICES` 说明：Paper Fig v2 使用了一个叫「Presentations resources (26.905.11957)」的组件。这个组件**保留原始权利，不在本仓库的 Apache 2.0 范围内重新授权**。

这意味着：仓库整体是 Apache 2.0，但 Paper Fig 技能里包含一段许可证条款未公开的专有资产。这段资产究竟来自哪里（OpenAI 内部工具？第三方商业包？），README 没有说清楚。如果你打算在生产中用 paper-fig 技能，先搞清楚这个问题。

### 3. 2026-09-08 之后零提交

仓库全部有效提交都在 2026-09-04～09-08 之间，共五个提交。之后再无活动。目前只有 1 个 open issue，社区互动极少。

这是典型的论文发表产物：项目随论文一起开源，但没有后续维护计划。高推理 effort 的 token 成本、对 Codex CLI 的强依赖、没有 pip 安装路径——这些门槛会进一步限制实际采用。

---

## Gallery 的作用

仓库里附带了 16 个示例（13 个视觉设计 + 3 个 Paper Fig 学术图），包括中文设计作品：茶饮海报、护肤品海报、健身信息图、滕王阁序视觉版。每个示例都附有完整的生成 Prompt。

Gallery 的价值不只是展示效果——它本质上是一个 **Prompt 模板库**。看懂 Prompt 结构就能直接复用。这是学术项目中相对少见的实用考量。

---

## 安装路径

作者提供了稀疏克隆方式避免下载 159 MB 的 Gallery 媒体文件：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/yejy53/Editable-Design.git
cd Editable-Design
git sparse-checkout set skills/editable-design
mkdir -p ~/.codex/skills
cp -R skills/editable-design ~/.codex/skills/
npm ci --prefix ~/.codex/skills/editable-design/scripts
~/.codex/skills/editable-design/scripts/install-font-kit.sh
~/.codex/skills/editable-design/scripts/doctor.sh
```

复杂布局建议使用 `high` 及以上推理等级（对应更高 token 消耗）。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 1,118 |
| License | Apache 2.0（含许可证灰色地带） |
| 语言 | Python |
| 学术团队 | 中山大学 12 人 |
| arXiv | 2609.04034 |
| 最后提交 | 2026-09-08 |
| 提交总数 | 5 个 |
| Gallery 示例 | 16 个（含中文设计） |
| 仓库体积 | ~159 MB（Gallery 媒体主导） |

---

## 综合判断

「Coding Agent 当设计师」这条技术路线是正确的——输出可编辑结构是比光栅图更有用的产物，Agent Design Replay 是这个方向目前最完整的公开实现，Paper Fig 填了学术作图的真实需求缝隙。

实用门槛集中在两处：**硬绑 Codex CLI + OpenAI 账号**（Claude Code 用户需要自己移植），以及 **2026-09-08 后零维护**（论文发表工件，不是产品）。如果你在 Codex 生态里，这个 Skill 包值得安装试一试；如果你在 Claude Code 生态里，这是个有价值的参考实现，移植工作量不小。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## Editable-Design: SYSU 12-Person Team Uses Codex as Designer, Outputs Editable HTML Posters

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem: Diffusion Models Output Dead Images

Stable Diffusion / FLUX / Midjourney output pixel arrays — text isn't selectable, layers can't be moved, a wrong price requires regenerating the whole image. For posters, infographics, and academic diagrams that need frequent edits, non-editability is a hard blocker.

**yejy53/Editable-Design** replaces the entire generation pipeline: instead of a diffusion model painting pixels, Codex CLI writes HTML/CSS. The output isn't an image — it's a webpage you can edit in a browser. Text is real text, layout is real CSS, layers are real DOM nodes.

Repo: github.com/yejy53/Editable-Design  
**1,118 stars | Apache 2.0 | Python | Created 2026-08-24 | arXiv: 2609.04034**

Lead author: Junyan Ye (PhD student, Sun Yat-Sen University). 12 co-authors, all from SYSU.

---

### Three Skills, One Execution Model

Delivered as Codex CLI Skills under `skills/`:

| Skill | Purpose | Output |
|-------|---------|--------|
| `editable-design` | Posters, infographics, campaigns | HTML, editor.html, layers.html, replay/, PNG |
| `html-to-pptx` | Convert HTML to PowerPoint | Editable .pptx |
| `paper-fig` | Academic method/architecture diagrams | Editable .pptx |

**editable-design flow**: prompt enhancement → reference image generation → composition planning → raster asset generation → fixed-canvas index.html → Playwright render verification → editor.html + exploded layer view → replay/index.html (full audit trail) → optional .pptx export.

Key SKILL.md constraints: no model-authored SVG illustrations, prefer embedded Lucide icons, "You are the designer, not a consultant" — agent decides layout autonomously.

---

### Three Genuinely Valuable Design Points

**1. Editable outputs.** Text in the output is real selectable HTML, not pixel-embedded text. `editor.html` provides a drag-and-drop editing interface. The .pptx conversion produces independently editable text boxes, shapes, and image elements.

**2. Agent Design Replay.** `replay/index.html` records the full design decision path — you can step through every layer addition and creative choice. No mainstream design tool does this. Figma/Canva show the result; this shows how the AI got there. Real differentiation for debugging and academic analysis.

**3. Paper Fig.** Generates academic method diagrams and architecture flowcharts from text descriptions, exporting as editable .pptx. This fills a real underserved need: drawing method diagrams is painful in every tool.

---

### Three Issues to Know

**1. Hard-locked to OpenAI Codex CLI.** `agents/` contains only `openai.yaml`. No Claude Code config, no other runtime support. Claude Code and Gemini CLI users cannot run it without rewriting the skill infrastructure. README states: "This community project is not an official OpenAI project."

**2. Paper Fig has a license gray area.** `THIRD_PARTY_NOTICES` says Paper Fig v2 adapts "Presentations resources (26.905.11957)" which "retains their original rights and are not relicensed under this repository's Apache-2.0 license." What this component is (internal OpenAI tooling? Commercial package?) is not disclosed. Verify before production use.

**3. Zero commits after 2026-09-08.** All commits are from Sept 4–8 (5 total). Classic research-publication artifact: open-sourced alongside the paper, but no maintenance roadmap. One open issue. Minimal community engagement.

---

### Gallery as Prompt Library

16 examples (13 visual designs + 3 Paper Fig academic diagrams), including Chinese designs: tea drink poster, skincare brand poster, fitness infographic, Tang Wangge Xu visual layout. Every example includes the full prompt. This is a directly usable template library, not just a demo reel.

---

### Numbers

| Metric | Value |
|--------|-------|
| Stars | 1,118 |
| Team | 12 SYSU researchers |
| Last commit | 2026-09-08 |
| Total commits | 5 |
| Gallery examples | 16 (includes Chinese) |
| Repo size | ~159 MB |

---

### Verdict

The "coding agent as designer" approach is correct — editable structured output is more useful than rasterized pixels, Agent Design Replay is the most complete public implementation of this design-audit idea, and Paper Fig fills a genuine academic workflow gap.

Practical blockers: **hard Codex CLI + OpenAI account dependency** (Claude Code users need to port it themselves), and **zero maintenance post-publication**. If you're in the Codex ecosystem, this skill package is worth installing. If you're in the Claude Code ecosystem, this is a valuable reference implementation — porting effort is non-trivial.

---

> Open source for learning only. Verify license terms before commercial use.
