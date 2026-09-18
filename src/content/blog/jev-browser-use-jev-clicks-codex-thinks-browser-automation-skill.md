---
title: "Jev Browser Use：Jev 负责点击导航，Codex 负责思考验收，浏览器自动化快 5-10 倍"
titleEn: "Jev Browser Use: Jev Clicks and Navigates, Codex Thinks and Verifies — 5-10x Faster Browser Automation"
description: "wy-coliney/jev-browser-use，MIT，JavaScript，Codex/Claude Code Skill。把浏览器操作分工：Jev（TypeSafe 决策模型）负责点击/滚动/跳转/切换，Codex 负责输入文字/读页面/判断/验收。动作循环不增加额外模型轮次，实测 EZCollegeApp 工作流快 5-10 倍，100K token 成本 $0.0042 vs GPT-6 Astra $1.00。"
descriptionEn: "wy-coliney/jev-browser-use, MIT, JavaScript, Codex/Claude Code Skill. Splits browser automation: Jev (TypeSafe decision model) handles clicking/scrolling/navigation/toggle; Codex handles text input/page reading/judgment/verification. Action loops add zero extra model turns per click. Real-world 5-10x faster in EZCollegeApp workflows; 100K token cost $0.0042 vs GPT-6 Astra $1.00."
pubDate: "2026-09-18"
updatedDate: "2026-09-18"
category: "Tech-Experiment"
tags: ["browser-automation", "Jev", "Codex", "Claude-Code", "computer-use", "workflow", "TypeSafe-AI"]
heroImage: "../../assets/images/jev-browser-use-jev-clicks-codex-thinks-browser-automation-skill-banner.jpg"
---

> 📌 GitHub：https://github.com/wy-coliney/jev-browser-use
> Stars：33 | License：MIT | 语言：JavaScript
> 发布日期：2026-09-18

---

用大模型控制浏览器，有个一直没有解决好的问题：**每次点击、滚动、跳转都要跑一次完整的模型推理**。哪怕只是"点这个按钮"，也要截图、理解页面、思考、输出动作——这个开销太高了。

Jev Browser Use 的思路很简单：**把动作拆开，按价值分配给不同的模型。**

---

## 分工逻辑

```
目标 → 观察当前控件 → Jev 选择动作 → 执行 → 循环 → Codex 验收
```

**Jev（TypeSafe 决策模型）负责**：
- 点击（Click）
- 页面跳转（Navigation）
- 标签切换（Tab switch）
- 滚动（Scroll）
- 开关切换（Toggle）
- 依据无障碍文本（accessibility text）判断目标控件，不依赖截图

**Codex / Claude Code 负责**：
- 输入文字（Typing）
- 读取页面内容并理解
- 做需要判断的决策
- 最终验收结果

这两类操作有本质区别。点击、滚动这类**导航动作**是结构化的决策："这一堆控件里，下一步选哪个"——正好是 Jev 的强项（速度快、成本低、不需要生成文字）。而输入文字、理解页面语义、判断任务是否完成——这些需要真正的理解能力，留给 LLM 来做。

关键在于：**动作循环全程在现有的 Computer Use 连接内进行，不新增额外的模型轮次**。Jev 的每次决策在约 300ms 内完成，不打断当前任务的上下文。

---

## 安装

支持三种方式：

**Codex Skill（推荐）**：
```bash
npx skills add wy-coliney/jev-browser-use -g -a codex -y
```

**Claude Code Skill**：
```bash
npx skills add wy-coliney/jev-browser-use -g -a claude-code -y
```

**Codex Plugin Marketplace**：
```bash
codex plugin marketplace add wy-coliney/jev-browser-use
```

**手动安装**：
```bash
git clone https://github.com/wy-coliney/jev-browser-use
node scripts/install.mjs
```

**依赖**：Node.js 22+，已连接 Chrome 的 Codex Computer Use，以及 Jev 访问权限（TypeSafe 早期访问）。

---

## 使用方式

安装后，在任务描述里明确指定使用这个 skill：

```
Use Jev Browser Use on the settings page.
Open the filters, switch views, scroll through results,
and restore the original state. Independently verify the result.
```

Jev 处理"打开过滤器、切换视图、滚动、还原状态"这些导航动作，Codex 在最后独立验证结果是否符合预期。

---

## 成本对比

以 10 万输入 token 为单位：

| 模型 | 成本 |
|------|------|
| **Jev 1.13** | **$0.0042** |
| GPT-5.6 Terra | $0.20 |
| GPT-6 Astra | $1.00 |

把高频的导航决策路由给 Jev，而不是全程跑 GPT-6 Astra，每 10 万 token 节省约 238 倍成本。这个差距在重复性自动化场景（比如批量处理表单、循环翻页、多次筛选）里会直接反映在账单上。

---

## 真实使用场景：EZCollegeApp 工作流

这个 Skill 最初是为 EZCollegeApp 的文书评估工作流构建的。典型流程包括：反复打开评估条目、展开备注、滚动报告、跳转到编辑器——这些操作重复量高、单步判断简单，正好适合批量路由给 Jev。

实测结果：相关工作流快了 **5-10 倍**。

---

## 设计背后的逻辑

Jev Browser Use 本质上是一个**双层路由**的实现：低认知、高频率的操作 → 快速便宜的决策模型；高认知、低频率的判断 → 强大的语言模型。

这和 TypeSafe Jev 本身的定位完全吻合——Jev 不适合"帮我写段文字"，但非常适合"从这 N 个选项里选一个下一步操作"。把浏览器里的每个动作理解成一道多选题，就能把 Jev 的并行决策能力用到实处。

随着浏览器自动化越来越常见（Agent 操作网页、填表、抓取、测试），这种分工模式可能会成为一个常见的工程范式：**决策层用专用模型，推理层用通用模型**。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/wy-coliney/jev-browser-use
> Stars: 33 | License: MIT | Language: JavaScript
> Released: 2026-09-18

---

Using LLMs to control browsers has a long-standing inefficiency: **every click, scroll, and navigation requires a full model inference pass**. Even "click this button" means: screenshot, understand the page, reason, output action — an expensive loop.

Jev Browser Use's premise is simple: **split the work, assign each part to the model that fits it best.**

---

## The Division of Labor

```
Goal → observe controls → Jev chooses action → execute → repeat → Codex verifies
```

**Jev (TypeSafe's decision model) handles:**
- Click
- Navigation (page transitions)
- Tab switching
- Scrolling
- Toggle operations
- Reads from accessibility text — no screenshot needed

**Codex / Claude Code handles:**
- Text input and typing
- Reading and understanding page content
- Judgment calls and decisions
- Final verification

These two categories differ fundamentally. Navigation actions — "from this set of controls, which one is next?" — are structured decisions, exactly Jev's strength (fast, cheap, no text generation required). Understanding page semantics, deciding when a task is complete, writing into fields — those need real comprehension, so they stay with the LLM.

Crucially: **the action loop runs entirely within the existing Computer Use connection, adding zero extra model turns per click.** Each Jev decision completes in roughly 300ms without interrupting the current task context.

---

## Installation

Three options:

**Codex Skill (recommended):**
```bash
npx skills add wy-coliney/jev-browser-use -g -a codex -y
```

**Claude Code Skill:**
```bash
npx skills add wy-coliney/jev-browser-use -g -a claude-code -y
```

**Codex Plugin Marketplace:**
```bash
codex plugin marketplace add wy-coliney/jev-browser-use
```

**Manual:**
```bash
git clone https://github.com/wy-coliney/jev-browser-use
node scripts/install.mjs
```

Requirements: Node.js 22+, Codex with Computer Use connected to Chrome, Jev access (TypeSafe early access).

---

## Usage

After installation, specify the skill in your task description:

```
Use Jev Browser Use on the settings page.
Open the filters, switch views, scroll through results,
and restore the original state. Independently verify the result.
```

Jev handles "open filters, switch views, scroll, restore state" as a navigation sequence. Codex independently verifies at the end that the result matches the goal.

---

## Cost Comparison

Per 100K input tokens:

| Model | Cost |
|-------|------|
| **Jev 1.13** | **$0.0042** |
| GPT-5.6 Terra | $0.20 |
| GPT-6 Astra | $1.00 |

Routing high-frequency navigation decisions to Jev instead of running GPT-6 Astra end-to-end cuts costs roughly 238x per 100K tokens — a difference that compounds quickly in repetitive automation tasks (batch form processing, paginated scraping, repeated filtering).

---

## Real-World Use Case: EZCollegeApp

The skill was originally built for EZCollegeApp's essay evaluation workflow. A typical session involves repeatedly opening evaluation entries, expanding notes, scrolling reports, and navigating to editors — high-repetition, low-judgment-per-step operations that route naturally to Jev.

Measured result: **5–10x faster** on these workflows.

---

## The Design Principle

Jev Browser Use is a two-tier routing implementation: low-cognition, high-frequency actions → fast, cheap decision model; high-cognition, low-frequency judgments → capable language model.

This aligns exactly with Jev's positioning — it's not for "write me a paragraph," it's for "pick the next action from N options." Framing every browser interaction as a structured multiple-choice question lets Jev's parallel decision architecture do real work.

As browser automation becomes a standard part of AI agent workflows (form filling, web scraping, testing, navigation), this routing pattern may become a common engineering baseline: **decision layer uses a specialized model, reasoning layer uses a general-purpose one.**

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
