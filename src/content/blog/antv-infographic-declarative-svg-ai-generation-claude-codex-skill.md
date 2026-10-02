---
title: "AntV Infographic：声明式语法 + 流式渲染，一句话生成 SVG 信息图"
titleEn: "AntV Infographic: Declarative Syntax + Streaming Render — Turn One Sentence Into an SVG"
description: "antvis/Infographic，6929星，MIT，TypeScript。AntV 出品的声明式信息图生成与渲染引擎。高容错语法专为 AI 生成设计，流式输出实时渲染，~200 内置模板，手绘/渐变/图案多种主题，内置编辑器，SVG 输出。Claude Code / Codex Skills 一键安装，已被 Alma、WeChat Markdown 编辑器、obsidian-infographic 等十余个生态项目接入。"
descriptionEn: "antvis/Infographic, 6929 stars, MIT, TypeScript. A declarative infographic generation and rendering engine from AntV. Fault-tolerant syntax tuned for AI generation, streaming output for real-time progressive rendering, ~200 built-in templates, multiple themes (hand-drawn, gradient, pattern), built-in editor, high-fidelity SVG output. Claude Code / Codex Skills installable in one command. Integrated into 10+ ecosystem projects including Alma, WeChat Markdown editor, and obsidian-infographic."
pubDate: 2026-10-02
heroImage: "../../assets/images/antv-infographic-declarative-svg-ai-generation-claude-codex-skill-banner.jpg"
category: "Tech-Experiment"
tags: ["可视化", "信息图", "AntV", "Claude Code", "Codex", "SVG", "声明式", "开源拆解"]
lang: "zh-CN"
wechatTitle: "AntV Infographic：一句话生成SVG信息图"
wechatDigest: "6929星MIT；AntV；声明式语法流式渲染；200+模板；Claude Code Skill直装"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 背景

AI 生成内容后，"展示"这一步一直是摩擦点。文字好生成，表格也行，但一旦要出信息图——有箭头、有颜色、有布局的那种——就要么手工套模板，要么交给人类设计。

AntV Infographic 的方向是：给 AI 一套专为生成设计的声明式语法，让 AI 输出的文本可以直接渲染成 SVG 信息图。

仓库：github.com/antvis/Infographic  
**Stars：6929 | MIT | TypeScript | AntV（阿里巴巴可视化团队）**  
官网：infographic.antv.vision

---

## 核心能力

### 声明式语法

语法设计对 AI 友好——缩进表示层级，关键词触发模板，错误容忍度高（不需要完全正确的语法也能渲染）：

```
infographic list-row-simple-horizontal-arrow
data
  lists
    - label Step 1
      desc Start
    - label Step 2
      desc In Progress
    - label Step 3
      desc Complete
```

这段语法对应一个三步流程图。关键词 `list-row-simple-horizontal-arrow` 指定模板，`data` 块填数据。

### 流式实时渲染

高容错语法的实际用途：AI 边生成边渲染，不用等输出完成：

```ts
let buffer = '';
for (const chunk of chunks) {
  buffer += chunk;
  infographic.render(buffer);  // 每一块增量都触发渲染
}
```

信息图逐步填充完整，而不是等待然后一次性弹出。

### ~200 内置模板

覆盖三类常见信息图场景：

| 类型 | 典型用途 |
|------|---------|
| **流程类** | 步骤说明、工作流、时间线 |
| **结构类** | 对比、分类、层级关系 |
| **数据故事类** | 关键数字、统计摘要、指标看板 |

模板命名即调用，语法里指定模板名就能切换。

### 主题系统

内置多个主题：手绘风格、渐变色、图案填充等，支持深度自定义。`editable: true` 参数开启后，AI 生成结果可以直接在内置编辑器里手动调整。

### SVG 输出

默认渲染为 SVG，分辨率不依赖 canvas 尺寸，可无损放大，直接粘贴进 Figma 或导出 PDF。

---

## 安装方式

### Claude Code（推荐）

从 marketplace 安装，无需手动下载：

```bash
/plugin marketplace add https://github.com/antvis/Infographic.git
/plugin install antv-infographic-skills@antv-infographic
```

或手动安装特定版本：

```bash
VERSION=0.2.4  # 替换为最新 tag
BASE_URL=https://github.com/antvis/Infographic/releases/download
mkdir -p .claude/skills
curl -L --fail -o skills.zip "$BASE_URL/$VERSION/skills.zip"
unzip -q -o skills.zip -d .claude/skills
rm -f skills.zip
```

### Codex

```
$skill-installer install https://github.com/antvis/Infographic/tree/main/skills/infographic-creator
```

### npm（程序集成）

```bash
npm install @antv/infographic
```

```ts
import { Infographic } from '@antv/infographic';
const infographic = new Infographic({ container: '#container', editable: true });
infographic.render('...');
```

---

## 五个 Skills

安装后可以在 Claude Code / Codex 中使用以下 Skills：

| Skill | 功能 |
|-------|------|
| `infographic-creator` | 生成包含渲染结果的完整 HTML 文件 |
| `infographic-syntax-creator` | 根据文字描述生成信息图语法 |
| `infographic-structure-creator` | 生成自定义结构/布局设计 |
| `infographic-item-creator` | 生成自定义元素/组件设计 |
| `infographic-template-updater` | 更新模板库（开发者用） |

典型使用路径：先用 `infographic-syntax-creator` 把自然语言转成语法，再用 `infographic-creator` 渲染成 HTML，如需调整使用内置编辑器。

---

## 生态状况

项目已经有相当数量的下游接入，其中有意思的几个：

- **dsh-antv-infographic**：DeepSeek Harness 插件，支持流式输出、编辑、导出
- **obsidian-infographic**：在 Obsidian Markdown 里直接渲染信息图
- **slidev-addon-infographic**：在 Slidev 演示文稿里使用
- **markdown-it-infographic**：markdown-it 插件
- **WeChat Markdown Editor**（md.doocs.org）：公众号排版工具，已集成 Infographic
- **feffery-infographic**：Python 接口，用 Plotly Dash 创建信息图

生态接入的数量和多样性说明这个语法设计确实可落地，不只是 demo。

---

## 需要知道的限制

**语法需要学习成本**。~200 个模板意味着 ~200 个模板名要记（或查）。自然语言"生成一张三步流程图"到正确的模板名和语法结构，需要 AI 或者人理解模板命名体系。

**SVG 不是所有场景都适合**。如果目标平台只能接受图片格式（某些小程序、邮件正文），SVG 需要额外转换。

**数据可视化和信息图不同**。Infographic 擅长结构化内容呈现（流程、列表、对比），不是 ECharts/D3 那种数据图表引擎——折线图、散点图、地图这些不在这里。

**MIT，不限商用**。阿里巴巴/AntV 出品，MIT 协议，不限改用。

---

## 关键数字

| 指标 | 值 |
|------|----|
| Stars | 6929 |
| Forks | 563 |
| License | MIT |
| 语言 | TypeScript |
| npm 包 | @antv/infographic |
| 内置模板数 | ~200 |
| 创建时间 | 2025-09-11 |
| 生态项目 | 10+ |

---

## 综合判断

AntV Infographic 填的是一个具体的空档：用 AI 生成文字没问题，生成代码没问题，但生成"有设计感的排版图示"一直很难。Infographic 的声明式语法把这个问题做成了一个有确定答案的任务——给 AI 语法格式，让 AI 填内容。

流式渲染是一个工程上的好决策：AI 生成过程可以即时可见，不用等输出完成才看结果。高容错语法让这件事可行——部分语法也能渲染，不会因为 AI 中途输出不完整就崩。

限制很明确：这是信息图工具，不是通用图表引擎。如果你需要的是折线图/柱状图这类数据可视化，AntV 的其他库（G2/Charts）是对应工具，不是这个。

6929 星 + 10 多个生态项目，对一个去年 9 月创建的库来说是很好的信号。AntV 团队背后有蚂蚁集团支持，文档、gallery 和维护质量都比一般个人项目稳。

---

> 开源仅供学习，MIT 协议，商业使用无限制。

---

<!--EN-->

## AntV Infographic: Declarative Syntax + Streaming Render — Turn One Sentence Into an SVG

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Gap

After AI generates content, presentation is always the friction point. Text is easy. Tables work fine. But producing a proper infographic — with arrows, color, layout — usually means wrestling with templates or handing off to a designer.

AntV Infographic takes a direct approach: give AI a declarative syntax tuned for generation, and let AI output text that renders directly into SVG infographics.

Repo: github.com/antvis/Infographic  
**6929 stars | MIT | TypeScript | AntV (Alibaba visualization team)**

---

### Core Capabilities

**Declarative syntax**: Indent-based hierarchy, keywords activate templates, high fault tolerance means imperfect AI output still renders.

**Streaming real-time rendering**: The fault-tolerant parser updates the graphic with every incoming chunk — the infographic builds progressively while AI is still generating.

**~200 built-in templates**: Three categories — flow diagrams (steps, workflows, timelines), structure diagrams (comparison, classification, hierarchy), and data stories (key numbers, metrics, summaries).

**Theme system**: Hand-drawn, gradient, pattern presets with deep customization. `editable: true` unlocks the built-in editor for post-generation tweaks.

**SVG output**: Resolution-independent, pasteable into Figma, exportable to PDF.

---

### Quick Integration

**Claude Code:**
```bash
/plugin marketplace add https://github.com/antvis/Infographic.git
/plugin install antv-infographic-skills@antv-infographic
```

**npm:**
```bash
npm install @antv/infographic
```

```ts
import { Infographic } from '@antv/infographic';
const infographic = new Infographic({ container: '#container', editable: true });
infographic.render(`
infographic list-row-simple-horizontal-arrow
data
  lists
    - label Step 1
      desc Start
`);
```

---

### Five Skills

After installation, five Skills are available in Claude Code / Codex:

| Skill | Purpose |
|-------|---------|
| `infographic-creator` | Generate a complete HTML file with rendered output |
| `infographic-syntax-creator` | Convert natural language descriptions to infographic syntax |
| `infographic-structure-creator` | Generate custom structure/layout designs |
| `infographic-item-creator` | Generate custom component designs |
| `infographic-template-updater` | Update the template library (developer use) |

---

### Ecosystem Signal

The downstream adoption is notably broad: a DeepSeek Harness plugin, an Obsidian plugin, Slidev addon, markdown-it plugin, React wrapper, Python (Plotly Dash) binding, VS Code extension, and several commercial products. For a library created in September 2025, 10+ ecosystem integrations is meaningful signal that the syntax abstraction is actually usable outside of demo conditions.

---

### Limitations

**Template name learning curve.** ~200 templates means ~200 names to know. AI needs to understand the naming system to generate correct syntax — or you query the gallery first.

**SVG doesn't fit every platform.** WeChat mini programs, some email clients — SVG often needs conversion to PNG/JPG.

**Infographics ≠ data charts.** Infographic handles structured content (lists, steps, comparisons). For line charts, scatter plots, maps — that's AntV G2/Charts, not this library.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 6929 |
| License | MIT |
| npm | @antv/infographic |
| Templates | ~200 |
| Created | 2025-09-11 |
| Ecosystem projects | 10+ |

---

### Verdict

Infographic fills a specific gap: AI can write text, AI can write code, but AI generating a well-laid-out visual diagram has always been awkward. The declarative syntax turns this into a defined task — give AI the format, let AI fill the content.

Streaming rendering is a good engineering decision: the output is visible as it builds, not as a one-shot result. Fault-tolerant parsing makes streaming viable — partial syntax renders, rather than failing on incomplete AI output.

Scope is clear: this is an infographic tool, not a charting engine. If you need line charts or scatter plots, look at AntV's other libraries.

6929 stars + 10+ ecosystem integrations for a library under 14 months old is a strong signal. AntV is backed by Alibaba, so documentation, gallery, and maintenance quality are consistently solid.

---

> Open source for learning only. MIT license — commercial use unrestricted.
