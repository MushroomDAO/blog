---
title: "Impeccable：76K 星的 AI 前端设计技能包，让 Claude Code 做出好设计"
titleEn: "Impeccable: The 76K-Star AI Frontend Design Skill — Stop Getting Generic Designs from Claude Code"
description: "pbakaus/impeccable，Apache-2.0，76,323 stars，JavaScript。为 AI Coding Agent 设计的前端设计语言，起源于 Anthropic 官方 frontend-design skill。核心：24 个设计命令（craft/polish/audit/critique/animate 等）+ 61 条确定性检测规则（无需 LLM，CLI 和浏览器扩展直接跑）。/impeccable init 生成 PRODUCT.md 存储产品真相，/impeccable live 在浏览器里实时迭代视觉变体。支持 Claude Code、Cursor、Codex、Grok Build、Gemini CLI、OpenCode 等所有主流 Harness，npx impeccable install 一行安装。明确标出十类反模式：Inter 字体、灰底白字、卡片套卡片等。"
descriptionEn: "pbakaus/impeccable, Apache-2.0, 76,323 stars, JavaScript. A frontend design language for AI coding agents, starting from Anthropic's official frontend-design skill. Core: 24 design commands (craft/polish/audit/critique/animate, etc.) + 61 deterministic detector rules (no LLM, no API key — CLI and browser extension run them directly). /impeccable init generates PRODUCT.md for durable product context; /impeccable live iterates visual variants in the browser. Supports Claude Code, Cursor, Codex, Grok Build, Gemini CLI, OpenCode, and more. Explicitly names ten anti-patterns: Inter everywhere, gray text on colored backgrounds, cards nested in cards, etc."
pubDate: 2026-10-05
heroImage: "../../assets/images/impeccable-ai-frontend-design-skill-24-commands-61-rules-banner.jpg"
category: "Tech-Experiment"
tags: ["前端设计", "Coding Agent", "Claude Code", "UI设计", "Skill", "开源工具"]
lang: "zh-CN"
wechatTitle: "Impeccable：76K星AI前端设计Skill包"
wechatDigest: "Apache-2.0；24个设计命令；61条无需LLM的确定性检测规则；npx一行安装；Claude Code/Codex/Cursor全支持"
---

问题很具体：让 Claude Code 做前端，出来的设计总是那个样子——Inter 字体、蓝紫渐变、到处套卡片、图标上面配圆角方块。不是 Claude 不努力，是所有模型都在同一套 SaaS 模板上训练的。

Impeccable 从 Anthropic 官方的 frontend-design skill 出发，补上了这个缺口：给 AI 一套有设计判断力的工作语言。

GitHub: https://github.com/pbakaus/impeccable | ⭐ 76,323 | Apache-2.0 | JavaScript

76K 星是这个规模 skill 仓库里罕见的数字——它的定位比通用 coding skill 窄很多，但在前端设计这个垂直场景里击中了痛点。

---

## 两层设计指导

Impeccable 做两件事：

**1. 给 AI 上下文（PRODUCT.md）**

`/impeccable init` 检查项目，询问产品受众、用途、约束、调性，然后写入 `PRODUCT.md`。这份文件存的是「产品真相」——不是视觉指向，是目标受众是谁、产品在什么场景下运行、什么不能做。

后续的所有 `/impeccable` 命令都会读这份文件，所以 AI 不会每次都从零猜。如果已有视觉系统，写进 `DESIGN.md`，模型就知道参考什么，不用重新发明。

**2. 给 AI 24 个操作命令**

```
/impeccable <command> <target>
```

不同命令对应不同的设计阶段：

| 阶段 | 命令 |
|------|------|
| 建立设计系统 | `init`, `document`, `extract`, `shape` |
| 细化质量 | `polish`, `audit`, `critique`, `harden` |
| 调整风格 | `bolder`, `quieter`, `distill`, `colorize`, `typeset`, `layout` |
| 添加细节 | `animate`, `delight`, `overdrive`, `onboard` |
| 浏览器实时 | `live`, `generate` |

---

## 24 个命令详解

几个最常用的：

**`/impeccable craft <target>`** — 完整的「从设计到实现」流程，带视觉迭代，适合从零起步。

**`/impeccable polish <target>`** — 上线前最后一遍对齐设计系统，相当于 AI 做 final review。

**`/impeccable audit <target>`** — 可访问性、性能、响应式布局的技术检查。

**`/impeccable critique <target>`** — UX 层面的设计评审：信息层级、清晰度、情感共鸣。

**`/impeccable bolder / quieter`** — 「太无聊了」或「太嗨了」时用，一句话调整设计强度。

**`/impeccable live`** — 在浏览器里开启视觉变体模式，AI 实时生成并展示变体，不用手动挑。

**`/impeccable generate <element>`** — 针对某个具体元素（hero section、导航栏等）自动生成多个变体。

用法示例：

```bash
/impeccable audit blog           # 审查博客页面
/impeccable polish settings      # 设置页上线前最后打磨
/impeccable harden checkout      # 结账页加错误处理和边界 case
/impeccable critique landing     # 落地页 UX 评审
```

也可以直接描述意图：

```bash
/impeccable redo this hero section
```

---

## 61 条确定性检测规则

这是 Impeccable 最有意思的一个设计决策：**把「AI 检测」和「规则检测」分开**。

61 条确定性规则不需要 LLM，不需要 API Key，CLI 和浏览器扩展直接跑，毫秒级返回结果。LLM 只处理无法规则化的主观判断（比如视觉层级、情感共鸣）。

这个分工的好处：
- 确定性规则快、便宜、离线可用，适合嵌进 CI
- LLM critique 只跑在真正需要主观判断的地方，减少不必要的 API 消耗

---

## 反模式清单

Impeccable 明确列出了十类 AI 生成设计的常见问题，作为负面约束：

- **字体**：避免 Arial、Inter、系统默认字体——这些是「我没有想字体」的信号
- **颜色**：避免灰底白字（对比度不够）；避免纯黑纯灰（永远要加色调）
- **布局**：避免到处套卡片，尤其是卡片套卡片
- **图标**：避免标题上方的圆角方块图标 tile——那是 SaaS 模板的标配
- **动效**：避免 bounce/elastic 缓动曲线（2015年的味道）

这份清单本身就值得贴在项目文档里，跟不跟 Impeccable 用都有参考价值。

---

## 安装

**推荐方式（一行命令）**：

```bash
npx impeccable install
```

检测你本机已安装的 Harness（Claude Code、Cursor、Codex、Grok Build 等），让你选择安装范围（当前项目或全局），完成后在 AI 工具里跑 `/impeccable init` 就能用。

**Claude Code 插件市场**：

```bash
/plugin marketplace add pbakaus/impeccable
```

**Git 子模块（团队使用）**：

```bash
git submodule add https://github.com/pbakaus/impeccable .impeccable
npx impeccable link --source=.impeccable --providers=claude,cursor
```

支持的 Harness：Claude Code、Cursor、Codex、Grok Build、Gemini CLI、Hermes、Veto、OpenCode、Pi、VS Code Copilot、DeepSeek Harness 等。

---

## 局限

- **不自己写代码**：Impeccable 是指导框架，实际代码由你选择的 AI 生成。PRODUCT.md 的质量决定了命令的效果上限——初始化时如果随便填，后面的命令也得不到好结果。
- **live/generate 依赖浏览器**：实时变体功能需要浏览器扩展，纯 CLI 场景下用不了。
- **Apache-2.0 但引擎二进制单独分发**：skill 文件是 Apache-2.0，但 `~/.impeccable/bin/` 里的引擎二进制是独立下载的，许可证条款见 impeccable.style。

---

> Apache-2.0 开源（skill 部分）。引擎二进制从官网单独分发，使用前请确认各自许可条款。开源仅供学习参考。

---

<!--EN-->

## Impeccable: The 76K-Star Frontend Design Skill for AI Coding Agents

The pattern is familiar: ask Claude Code to build a frontend and you get the same results — Inter everywhere, blue-to-purple gradients, cards nested in cards, rounded-square icon tiles above every heading. Not Claude's fault; every model trained on the same SaaS templates.

Impeccable starts from Anthropic's official frontend-design skill and fills the gap: a design language that gives your AI coding agent real design judgment.

GitHub: https://github.com/pbakaus/impeccable | ⭐ 76,323 | Apache-2.0 | JavaScript

---

### Two Layers of Design Guidance

**1. Give AI durable context (PRODUCT.md)**

`/impeccable init` inspects your project, asks about product audience, purpose, operating context, constraints, voice, and evidence — then writes `PRODUCT.md`. This is "product truth" — not visual direction, but who the audience is, what environment the product runs in, what's off-limits.

All subsequent `/impeccable` commands read this file, so the AI never guesses from scratch. Existing visual systems go in `DESIGN.md`.

**2. Give AI 24 design commands**

Design stage → command mapping:

| Stage | Commands |
|-------|----------|
| Build design system | `init`, `document`, `extract`, `shape` |
| Refine quality | `polish`, `audit`, `critique`, `harden` |
| Adjust style | `bolder`, `quieter`, `distill`, `colorize`, `typeset`, `layout` |
| Add detail | `animate`, `delight`, `overdrive`, `onboard` |
| Live browser | `live`, `generate` |

---

### 61 Deterministic Detector Rules

The key architectural decision: **separate rule-based detection from LLM critique**.

61 deterministic rules run with no LLM and no API key — the CLI and browser extension execute them in milliseconds. LLM checks only run for subjective judgment (visual hierarchy, emotional resonance). This makes the deterministic checks fast, cheap, offline-capable, and CI-embeddable.

---

### The Anti-Pattern List

Impeccable explicitly names what to avoid in AI-generated design:

- **Fonts**: no Arial, Inter, system defaults — these signal "I didn't think about fonts"
- **Color**: no gray text on colored backgrounds; no pure black/gray (always add a tint)
- **Layout**: no card nesting; no rounded-square icon tiles above headings
- **Motion**: no bounce/elastic easing

Even without using Impeccable, this list is worth keeping in your project docs.

---

### Installation

**One-line install (recommended):**

```bash
npx impeccable install
# then inside your AI tool:
/impeccable init
```

Detects installed harnesses (Claude Code, Cursor, Codex, Grok Build, etc.), asks project vs. global scope, installs and configures.

**Claude Code plugin marketplace:**
```bash
/plugin marketplace add pbakaus/impeccable
```

**Git submodule (for teams):**
```bash
git submodule add https://github.com/pbakaus/impeccable .impeccable
npx impeccable link --source=.impeccable --providers=claude,cursor
```

Supported harnesses: Claude Code, Cursor, Codex, Grok Build, Gemini CLI, OpenCode, Pi, VS Code Copilot, Hermes, Veto, and more.

---

### Constraints

Impeccable is a guidance framework — actual code is written by your chosen AI. PRODUCT.md quality sets the ceiling for command effectiveness. The `live`/`generate` browser iteration features require the browser extension; pure CLI doesn't get them. The skill files are Apache-2.0; the engine binary at `~/.impeccable/bin/` is distributed separately from impeccable.style — check its terms before use.

---

> Apache-2.0 (skill files). Engine binary distributed separately from impeccable.style — verify terms before use. For technical reference only.
