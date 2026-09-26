---
title: "awesome-gpt-image-2：33K stars，544 个逆向案例 + 20+ 工业级模板，Prompt as Code 出图引擎"
titleEn: "awesome-gpt-image-2: 33K Stars, 544 Reverse-Engineered Cases + 20+ Industrial Templates — Prompt as Code Image Engine"
description: "freestylefly/awesome-gpt-image-2，MIT，JavaScript，33,523 stars。GPT-Image-2/2.5 提示词工程库，544 个从真实生成结果逆向拆解的案例，12 大类别（UI/摄影/海报/信息图/插画/电商/品牌/角色/场景等），20+ 套工业级模板（含 JSON 结构化版本），配套 gpt-image-2-style-library npm Skill，同一份 style-library.json 同时驱动网站和 Agent。提示词采用「Prompt as Code」分层 schema：目标→主体变量→环境→风格→技术约束→输出规格→禁止项。附 GPT-Image-2 vs 2.5 同提示词对比专区。"
descriptionEn: "freestylefly/awesome-gpt-image-2, MIT, JavaScript, 33,523 stars. Prompt engineering library for GPT-Image-2/2.5: 544 cases reverse-engineered from real generation results across 12 categories (UI, photography, posters, infographics, illustration, e-commerce, brand, characters, scenes, etc.), 20+ industrial-grade templates (with JSON structured variants), companion npm Skill gpt-image-2-style-library sharing one style-library.json with the website and agent. Prompts use a 'Prompt as Code' layered schema: objective → subject variables → environment → style → technical constraints → output spec → avoidance directives. Includes GPT-Image-2 vs 2.5 same-prompt comparison gallery."
pubDate: 2026-09-26
wechatTitle: "GPT-Image2工业级提示词：544案例+20模板"
wechatDigest: "MIT 33K；544案例逆向出工业级提示词；20+模板可复用；Skill npm包共享schema"
heroImage: "../../assets/images/awesome-gpt-image-2-prompt-engineering-ai-image-generation-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "prompt-engineering", "gpt-image", "ai-image", "skills", "templates", "prompt-as-code", "javascript"]
lang: zh-CN
---

`freestylefly/awesome-gpt-image-2`，MIT，JavaScript，33,523 stars，3,227 forks，2026 年 4 月开源。一个 GPT-Image-2/2.5 的提示词工程库——544 个从真实生成结果逆向拆解的案例，20+ 套可复用模板，配套 npm Skill 包，单一 JSON 数据源同时驱动网站和 Agent。

**GitHub**：github.com/freestylefly/awesome-gpt-image-2

---

## 核心设计：Prompt as Code

项目作者把这套体系叫做「Prompt as Code」——不是写一段能跑的代码，而是像对待代码那样对待提示词：有结构、有类型、有版本、可复用、可参数化。

每个模板的提示词不是一段散文，而是一个有明确字段的 schema：

```
目标（Objective）
  ↓
主体变量（Subject variables）— 可参数替换
  ↓
环境上下文（Environment context）
  ↓
风格参数（Style: material, texture, color palette）
  ↓
技术约束（f/1.4, 50mm, aspect ratio, resolution）
  ↓
输出规格（Output spec: what must appear, layout rules）
  ↓
禁止项（Avoidance directives: 已知失败模式清单）
```

「禁止项」这一层比较有意思——每个模板都附了 3–8 条从真实生成失败中总结出的坑：比如「禁止模型自行发明标题文字」、「禁止留白少于边框 5%」、「禁止多人场景中角色正面面对镜头」。这是 544 个案例的失败经验沉淀下来的。

---

## 544 个案例，12 个类别

案例库按类别分布：

| 类别 | 数量 |
|------|------|
| 海报与排版 | 90 |
| 摄影与真实感 | 78 |
| UI 与界面 | 73 |
| 插画与艺术 | 59 |
| 图表与信息图 | 53 |
| 产品与电商 | 42 |
| 角色与人物 | 31 |
| 品牌与 Logo | 27 |
| 其他 | 28 |
| 场景与叙事 | 21 |
| 历史与中国古典主题 | 16 |
| 文档与出版物 | 11 |

所有案例均为逆向工程后 100% AI 重写，保留了原始来源链接（主要来自 YouMind、OpenNana 等公开提示词社区），按 CC BY 4.0 处理归因。

Badge 实时更新，目前显示 544，描述里写的 530+ 是旧数字。

---

## 20+ 模板系统

模板按 4 页、13 个类别组织，每个类别有多个变体：

**部分关键模板：**

- **UI & Interface**：普通版 / JSON 注入版 / 截图风 / 直播画面风
- **信息图与数据可视化**：普通版 / JSON 版 / 多尺度科学图
- **电商与产品**：普通版 / 个性化美妆报告 / JSON 版
- **品牌与视觉识别**：完整品牌系统 / 触点展示板 / 品牌人格漫画 / JSON 版
- **角色与人物**：普通版 / 动作分解 / 玩具手办风
- **复杂多阶段任务**：PHASE 1 锚点 → PHASE 2 注入 → PHASE 3 格式化 → PHASE 4 签名

JSON 版模板是给 Agent 用的：Agent 可以直接填字段注入，不需要重新解析自然语言描述。

---

## Skills 系统：npm 包 + 单一数据源

配套 npm 包：`@freestylefly/gpt-image-2-style-library`

安装到 Claude Code / Codex：

```bash
npx skills add freestylefly/awesome-gpt-image-2 \
  --skill gpt-image-2-style-library \
  --agent claude-code codex \
  --global
```

安装后写入 `~/.codex/skills`、`~/.claude/skills`、`~/.agents/skills`。

**Skill 的工作方式：**

1. 读取 `data/style-library.json`（和网站共用同一份数据）
2. 检测用户语言（中 / 英自动切换）
3. 判断目标输出类型（UI / 摄影 / 海报 / 信息图等）
4. 匹配对应模板
5. 返回结构化可复用的提示词，包含：主体任务、构图布局、视觉风格/材质、文字标签、长宽比、约束项、模板名称、匹配案例 ID

网站和 Agent 共享同一个 `style-library.json` 是关键设计：新案例进仓库、网站实时更新、Skill 下次加载即可用，不需要单独维护两份数据。

---

## GPT-Image-2.5 对比专区

单独页面（gpt-image2.canghe.ai/gpt-image-2-5）用同一套提示词对比 GPT-Image-2 和 2.5（Sunburst / Flare 两个变体），拖拽分割线查看差异。目前收录 4 个真实案例（case #532、527、523、510）。

---

## 网站基础设施

这不只是一个 GitHub 仓库，还有一个配套的全栈网站：

- **托管**：Vercel
- **认证**：Supabase Auth（Google OAuth）
- **支付**：Stripe（国际）+ Alipay（国内）
- **图像生成 API**：APIMart
- **分析**：GA4

用户可以在网站上浏览案例、按类别筛选、复制提示词、直接生成（登录后）。支持绑定个人 API key 绕过平台计费。

---

## 怎么用这个仓库

**最简单的用法**：进 GitHub 仓库，找到对应类别，复制模板，替换 `[变量]` 占位符，直接粘贴到 GPT-Image-2 / 2.5。

**配合 Agent 用**：装 Skill，告诉 Agent「帮我做一张 XX 风格的电商产品图」，Skill 自动匹配模板、填入参数、返回结构化提示词，不需要手动翻库。

**大批量出图**：用 JSON 版模板，写脚本批量注入变量，通过 API 出图，参数和内容分离。

---

## 局限性

**1. 绑定 GPT-Image-2**：提示词为 GPT-Image-2 / 2.5 优化，用到其他模型（Midjourney、Flux、SD）效果会打折，部分语法不通用。

**2. 案例质量参差**：544 个案例中有作者自报「100% AI 重写」，但逆向工程的准确度取决于原始生成结果的可重复性。同一个提示词在不同会话下 GPT-Image-2 出的结果会有偏差。

**3. 数据来源声明**：主要逆向自 YouMind 和 OpenNana 等社区，CC BY 4.0 归因但没有经过每个原作者的明确授权确认。

**4. 付费网站配合度**：Skill 的完整功能依赖 `style-library.json`，本地离线使用可以，但高级功能（直接生成）需要网站账号。

---

## 怎么看这个项目

33,523 stars 说明这类「可复用提示词库」有真实需求，尤其是在 GPT-Image-2 开放 API 后出图成本下降的背景下。

值得学的不是案例本身，而是它对待提示词的方式：分层 schema + 禁止项 + JSON 参数化版本。这套方法可以直接迁移到其他生成模型上——换模型，保留结构。

对于日常用 GPT-Image-2 出图的用户，直接拿模板用能节省大量调参时间。对于 Agent 开发者，Skill 包的「单一数据源驱动网站和 Agent」设计值得参考。

> 开源仅供学习研究参考。案例内容按 CC BY 4.0 处理归因，商用前核实具体案例的原始来源授权。

---

<!--EN-->

## awesome-gpt-image-2: 33K Stars, 544 Reverse-Engineered Cases — Prompt as Code

`freestylefly/awesome-gpt-image-2` — MIT, JavaScript, 33,523 stars. GPT-Image-2/2.5 prompt engineering library: 544 reverse-engineered cases across 12 categories, 20+ industrial-grade templates with JSON structured variants, companion npm Skill package sharing one style-library.json with the website and agent.

**GitHub**: github.com/freestylefly/awesome-gpt-image-2

---

### Prompt as Code Architecture

Each template is a layered schema, not a prose paragraph:

```
Objective → Subject variables (replaceable parameters)
  → Environment context → Style (material/texture/palette)
  → Technical constraints (f/1.4, aspect ratio, resolution)
  → Output spec → Avoidance directives (known failure modes)
```

The "avoidance directives" layer is the most valuable: 3–8 known failure modes per template, reverse-engineered from real generation failures. Examples: "prohibit model-invented title text," "prohibit whitespace less than 5% of frame," "prohibit characters facing the camera in multi-person scenes."

---

### 544 Cases, 12 Categories

| Category | Cases |
|----------|-------|
| Posters & Typography | 90 |
| Photography & Realism | 78 |
| UI & Interfaces | 73 |
| Illustration & Art | 59 |
| Charts & Infographics | 53 |
| Products & E-commerce | 42 |
| Characters & People | 31 |
| Brand & Logos | 27 |
| Other | 28 |
| Scenes & Storytelling | 21 |
| History & Classical Chinese | 16 |
| Documents & Publishing | 11 |

All cases are 100% AI-rewritten reverse-engineering of public prompt communities (YouMind, OpenNana). CC BY 4.0 with source attribution.

---

### Template System

20+ templates across 13 categories, each with multiple variants: regular prose / JSON structured / specialized sub-types. Key examples:

- **UI/Interface**: regular / JSON injection / screenshot-style / live-streaming overlay
- **E-commerce**: regular / personalized beauty reports / JSON
- **Multi-stage complex**: PHASE 1 ANCHOR → PHASE 2 INJECT → PHASE 3 FORMAT → PHASE 4 SIGNATURE

JSON variants let agents inject parameters without parsing natural language — direct field substitution.

---

### Skills System: npm Package + Shared Data Source

```bash
npx skills add freestylefly/awesome-gpt-image-2 \
  --skill gpt-image-2-style-library \
  --agent claude-code codex --global
```

Installs to `~/.codex/skills`, `~/.claude/skills`. When invoked, the skill: detects language, classifies output type, matches template from `style-library.json`, returns a structured reusable prompt with template name and matching case IDs.

The website and Skill share one `style-library.json` — new cases update both automatically.

---

### GPT-Image-2 vs 2.5 Comparison

A dedicated page lets users drag a divider to compare the same prompt across GPT-Image-2 and 2.5 (Sunburst / Flare variants). Currently 4 real cases included.

---

### Limitations

1. **GPT-Image-2 specific**: Optimized for GPT-Image-2/2.5; transfers partially to other models
2. **Case reproducibility**: Reverse-engineered prompts have variance across sessions — same prompt, different results
3. **Attribution clarity**: CC BY 4.0 attribution but no per-case original author confirmation
4. **Paid website dependency**: Full Skill features work offline, but generation requires account sign-in

---

### Assessment

33,523 stars reflects real demand for reusable, parameterized prompt libraries now that GPT-Image-2 API costs have dropped. The architecture lesson isn't "here are some prompts" — it's "treat prompts like code: layered schema, typed variables, JSON for agents, failure-mode documentation." That method transfers to any generation model. For heavy GPT-Image-2 users, the templates save significant prompt iteration time. For agent developers, the single-source-of-truth design (one JSON drives both website and Skill) is worth borrowing.

> For learning and research reference only. Case content is CC BY 4.0 with attribution — verify original source licensing for commercial use.
