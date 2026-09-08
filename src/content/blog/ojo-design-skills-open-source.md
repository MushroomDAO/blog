---
title: "OJO Design Skills 正式开源：给 AI Coding Agent 装上真正的审美"
titleEn: "OJO Design Skills Goes Open Source: Real Design Judgment for AI Coding Agents"
description: "OJO 团队开源了 AI coding agent 设计 skill 包，双轨方法论（规约/创新赛道）强制 agent 先提方向再动 token，9 份规范文件覆盖完整设计链路，支持 Claude Code、Codex 等 7 个 agent 客户端。"
descriptionEn: "OJO's open-source design skill bundle teaches AI coding agents to make real design decisions — dual-track methodology, mandatory direction confirmation, and 9 reference files covering the full design chain across Claude Code, Codex, and 5 more agent runtimes."
pubDate: "2026-09-08"
updatedDate: "2026-09-08"
category: "Tech-News"
tags: ["设计系统", "AI Agent", "Claude Code", "UI/UX", "开源", "Codex"]
heroImage: "../../assets/images/ojo-design-skills-open-source-banner.jpg"
---

> 📌 项目地址：https://github.com/touchine-ojo/OJO-Design-Skills
> 官网：https://ojo.art

**AI 写的 UI，为什么总是那个味？**

紫蓝渐变、灰色占位方块、千篇一律的 Hero Banner——这是当下 AI 辅助开发的视觉通病。OJO 团队把这类输出叫做 "AI-slop"，并决定从 skill 层面把问题解决掉。

**9 月初，他们在 GitHub 正式开源了 OJO-Design-Skills，目前已获得 95 stars，MIT 协议。**

## OJO Design Skills 是什么？

OJO Design Skills 是一套**可复用的 UI/UX 设计 skill 包**，专门针对 AI coding agent 设计。一条命令装好，之后每次 agent 碰到界面相关任务，就会自动加载这套设计方法论——而不是靠模型权重里那些千篇一律的默认审美。

目前支持 7 个 agent 客户端：**Codex、Claude Code、ZCode、DeepCode、WorkBuddy、OpenCode**，以及通用 agent。安装统一走同一个脚本：

```bash
# 以 Claude Code 为例
curl -fsSL https://raw.githubusercontent.com/touchine-ojo/OJO-Design-Skills/main/scripts/install.sh \
  | bash -s -- --target claude-code
```

## 核心：双轨方法论

这套 skill 最有意思的地方是它**拒绝用一套答案搞定所有产品**。

**Convention Track（规约赛道）** 适合 SaaS、B2B、效率工具等"功能优先"产品。直接从 Notion、Linear、Figma、Stripe 等成熟设计系统中选一套落地，不走弯路，快速产出清晰、专业的界面。

**Innovation Track（创新赛道）** 适合消费级社交、电商、生活方式类产品，情绪差异化是核心竞争力。走深度品牌方法论：Material Metaphor（材质隐喻）、原型驱动、叙事驱动、或文化符号学，先建立品牌 DNA，再往下推导视觉语言。

两条赛道都有一个强制门槛：**agent 必须先提出 2-3 个文字版方向，等用户确认后才能动 token**。没有任何情况可以跳过这一步。

## 9 个参考文件，覆盖完整设计链路

当前唯一的 skill `app-ui-ux-best-practices` 附带 9 份规范文件：

| 文件 | 内容 |
|------|------|
| `anti-patterns.md` | 禁止清单：哪些组合是 AI 垃圾设计 |
| `visual-tokens.md` | 色值、字号、间距、阴影的 token 规范 |
| `component-recipe.md` | Tailwind 类名，覆盖 8 种交互状态 |
| `motion-system.md` | 弹簧物理参数，摩擦力映射到材质/方法论 |
| `component-libraries.md` | 组件库选型指引 |
| `design-audit.md` | 设计审查清单 |
| `icon-guidelines.md` | 图标规范（1.5-2px 描边，24×24 网格）|
| `material-metaphor.md` | 材质隐喻方法论详解 |
| `hero-enrichment.md` | Hero 区域内容增强规范 |

输出物明确到：hex 色值、8pt 间距体系、8 态交互 Tailwind 类、对比度 ≥ 4.5:1、正文字号 ≥ 14sp。

## 为什么值得关注？

**Agent 的审美上限，由 skill 决定。** 模型本身对"好设计"的理解停留在训练数据的平均水平，而平均水平就是 AI-slop。OJO 的思路是：与其等模型变聪明，不如直接把设计决策框架外挂进去。

这个方向很有意思——它本质上是把人类设计师的**方法论**而非"风格"注入给 agent，让 agent 学会"做选择"而不是"套模板"。ISFP 设计师人格（"每一个色值、阴影、圆角都必须有明确用意"）被显式编码进 skill，强制 AI 进行有意图的视觉决策。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/touchine-ojo/OJO-Design-Skills
> Website: https://ojo.art

**Why does AI-generated UI always look the same?**

Purple-blue gradients, gray placeholder boxes, generic Hero banners — these are the visual fingerprints of AI-assisted development today. The OJO team calls this output "AI-slop" and decided to fix it at the skill layer.

**OJO-Design-Skills is now open source on GitHub with 95 stars and an MIT license.**

## What Is It?

OJO Design Skills is a reusable UI/UX skill bundle purpose-built for AI coding agents. One install command, and every time an agent touches an interface task it loads this design methodology — rather than falling back on the averaged aesthetics baked into model weights.

Currently supports 7 agent runtimes: **Codex, Claude Code, ZCode, DeepCode, WorkBuddy, OpenCode**, and generic agents.

## Dual-Track Methodology

The skill refuses to give one answer for every product.

**Convention Track** targets utility-first products (SaaS, B2B, productivity tools) where clarity beats novelty. Pick one proven system — Notion, Linear, Figma, Stripe — and ship a clean, professional interface fast.

**Innovation Track** targets consumer products where emotional differentiation is the value. Apply one brand-driven methodology: Material Metaphor, archetype-driven, narrative-driven, or cultural-semiotic — build brand DNA first, then derive the visual language.

Both tracks share one hard gate: **the agent must present 2–3 text-only directions and wait for user confirmation before touching design tokens.** No exceptions.

## 9 Reference Files, Full Design Chain

The single skill `app-ui-ux-best-practices` ships with 9 spec documents: anti-patterns, visual tokens, component recipes (Tailwind, 8-state interaction model), motion system (spring physics), component libraries, design audit, icon guidelines, material metaphor methodology, and hero enrichment.

Outputs are concrete: hex codes, 8pt spacing scale, 8-state Tailwind classes, contrast ≥ 4.5:1, body text ≥ 14sp.

## Why It Matters

The model's aesthetic ceiling is the training-data average — which is AI-slop. OJO's approach: stop waiting for models to get smarter and externalize the design decision framework as a skill instead.

The key insight is injecting design **methodology**, not style. An ISFP designer persona is explicitly encoded — "every color, shadow, radius, and spacing value must serve a clear purpose" — forcing the AI to make intentional choices rather than reaching for defaults.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
