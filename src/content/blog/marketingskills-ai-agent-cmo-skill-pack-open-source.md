---
title: "给 AI Agent 装一个 CMO 大脑：marketingskills 开源营销技能包"
titleEn: "Give Your AI Agent a CMO Brain: marketingskills Open-Source Marketing Skill Pack"
description: "coreyhaines31/marketingskills 为 Claude Code 等 AI Agent 提供 32+ 专业营销技能，涵盖 AI SEO/GEO 优化、CRO 转化漏斗、高转化文案框架、RevOps 增长工程，含 51 个零依赖 CLI 工具，可直连 Ahrefs、Google Ads、Mailchimp API。"
descriptionEn: "coreyhaines31/marketingskills gives Claude Code and other AI agents 32+ professional marketing skills: AI SEO/GEO optimization, CRO conversion funnels, high-converting copy frameworks, RevOps growth engineering, and 51 zero-dependency CLI tools with direct Ahrefs, Google Ads, and Mailchimp API access."
pubDate: "2026-05-07"
updatedDate: "2026-05-07"
category: "Tech-News"
tags: ["AI Agent", "Claude Code", "营销", "SEO", "GEO", "CRO", "开源", "技能包"]
heroImage: "../../assets/images/marketingskills-ai-agents-hero.jpg"
---

**结论先行（BLUF）**：你的 AI Agent 会写代码，但不会做增长。`marketingskills` 把资深营销专家 Corey Haines 的方法论打包成 Agent 可执行的技能规范，32+ 个专业营销技能 + 51 个 CLI 工具直连真实 API，装完就是 CMO 级别的视野。GitHub：`coreyhaines31/marketingskills`

---

## 它解决了什么问题

AI Agent 在编程上已经接近专家水平，但面对"如何让产品获客""如何提升注册转化""如何做 SEO"这些问题时，往往只能给出教科书式的泛泛之谈，缺乏可落地的专业深度。

`marketingskills` 的逻辑是：**把专家知识结构化为 Agent 可理解的指令集**。不是让 AI 去搜索营销知识，而是直接在仓库里给 Agent 装好"专业大脑"。

---

## 核心功能模块

### 1. AI 时代 SEO 策略（含 AEO/GEO）

不只是传统的技术 SEO 审计，而是重点引入了 **AI SEO（AEO/GEO）** 框架：

- 如何优化内容以在 ChatGPT、Perplexity、Gemini 等生成式搜索引擎中被引用
- BLUF 结构、FAQ 模块、结构化数据标记等 GEO 战术
- 传统排名信号 + AI 引用信号双轨并行策略

### 2. 全链路 CRO 转化率优化

从落地页架构 → 注册流设计 → 流失预防的完整框架：

- 不只告诉 AI "写什么"，通过心理学模型解释"为什么这样布局"
- 涵盖首屏信息优先级、社会证明摆放位置、行动号召措辞等细节
- 注册流每个步骤的摩擦点识别与消除策略

### 3. 数据驱动文案生成

内置多种高转化文案框架，重点解决 **AI 腔调** 问题：

- 具体的文案结构（AIDA、PAS、Before-After-Bridge 等）
- 广告素材创作：Facebook/Google 广告、冷邮件序列、落地页标题
- 产品描述、定价页文案、用户评价展示方式

### 4. 增长工程与 RevOps

覆盖整个收入运营链路：

- 潜在客户评分模型与销售赋能工具
- **51 个零依赖 CLI 工具**，Agent 可直接调用：
  - Ahrefs API → 关键词分析、竞品反链
  - Google Ads API → 广告效果数据
  - Mailchimp API → 邮件序列自动化
  - 更多营销平台集成

---

## 技术架构

遵循 `.agents/skills/` 跨 Agent 标准，和本博客使用的技能规范格式完全兼容：

```bash
# 快速安装
npx skills install coreyhaines31/marketingskills
```

**"知识 + 工具"双层结构**：
- `SKILL.md` — 营销方法论，Agent 推理时读取
- CLI 工具 — 实时 API 数据，Agent 执行时调用
- `.agents/product-marketing-context.md` — 产品背景注入，让建议有针对性

Agent 不是在讲通用营销理论，而是基于你的产品具体情况给出可执行建议，并能直接拉取真实数据验证。

---

## 对开发者的实际意义

| 场景 | 没有 marketingskills | 有 marketingskills |
|------|---------------------|-------------------|
| 产品上线前 | AI 给出模糊建议 | 完整落地页 CRO 审计 + 文案框架 |
| SEO 优化 | 通用 checklist | AI SEO/GEO 双轨策略 + 关键词数据 |
| 写营销文案 | 充满"AI 腔"的套话 | 有心理学依据的高转化结构 |
| 获客增长 | 无从下手 | RevOps 框架 + 实时 API 数据支撑 |

---

## 快速上手

```bash
# 安装技能包
npx skills install coreyhaines31/marketingskills

# 在 Claude Code 中直接调用
# /marketingskills:cro-audit    → CRO 转化审计
# /marketingskills:seo-strategy → SEO/GEO 优化策略
# /marketingskills:copy-review  → 文案质量检查
```

配合 `.agents/product-marketing-context.md` 填入产品信息后，Agent 的建议会从通用框架变成针对你产品的具体执行方案。

---

## 常见问题

**Q：这和普通的营销 Prompt 模板有什么区别？**  
A：核心区别是"可执行性"。普通 Prompt 只能指导 AI 生成文字，`marketingskills` 的 CLI 工具层让 Agent 可以主动拉取真实数据（关键词搜索量、竞品数据、邮件打开率），做到数据驱动而非拍脑袋。

**Q：不用 Claude Code，其他 Agent 也能用吗？**  
A：支持任何遵循 `.agents/skills/` 规范的 Agent 框架。Cursor、Windsurf 等理论上也可集成，前提是支持自定义 skill 规范。

**Q：32+ 技能一次性装进上下文不会太重吗？**  
A：技能按需加载，不是一次性全部注入。Agent 根据任务类型调用对应的 SKILL.md，其他技能不占用上下文窗口。

**Q：AEO/GEO 优化真的有效果吗？**  
A：在 AI 搜索份额快速增长的当下，GEO 优化已经出现可量化的引用率提升案例。`marketingskills` 的 GEO 模块和本博客自建的 SEO/GEO 技能思路一致：BLUF 结构、FAQ 模块、品牌实体标注是核心战术。

**Q：51 个 CLI 工具需要自己配置 API Key 吗？**  
A：是的，每个工具需要对应平台的 API 授权。工具本身零依赖（无 npm 包），只需提供 Key 即可运行。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Your AI agent knows how to code but doesn't know how to grow. `marketingskills` packages senior marketer Corey Haines' methodology into agent-executable skill specs: 32+ professional marketing skills + 51 CLI tools with live API access. Install it and your agent has CMO-level expertise. GitHub: `coreyhaines31/marketingskills`

---

## The Problem It Solves

AI agents are approaching expert-level coding ability, but when asked "how do we acquire users," "how do we improve sign-up conversion," or "what should our SEO strategy be" — they produce textbook generalities with no actionable depth.

`marketingskills` takes a different approach: **structure expert knowledge into agent-executable instruction sets**. Don't make the agent search for marketing knowledge — give it a professional brain directly in the repo.

---

## Core Modules

### 1. AI-Era SEO Strategy (AEO/GEO)

Beyond traditional technical SEO audits, the project introduces **AI SEO (AEO/GEO)** frameworks:

- How to optimize content for citation by ChatGPT, Perplexity, and Gemini
- GEO tactics: BLUF structure, FAQ modules, structured data markup
- Dual-track strategy: traditional ranking signals + AI citation signals in parallel

### 2. Full-Funnel CRO

A complete framework from landing page architecture → signup flow → churn prevention:

- Explains not just "what to write" but "why this layout" via psychological models
- Covers above-the-fold information hierarchy, social proof placement, CTA wording
- Friction point identification and removal at each step of the signup flow

### 3. Data-Driven Copywriting

Multiple high-converting copy frameworks with a specific focus on **eliminating AI tone**:

- Structured frameworks: AIDA, PAS, Before-After-Bridge
- Ad creative for Facebook/Google, cold email sequences, landing page headlines
- Product descriptions, pricing page copy, testimonial display strategies

### 4. Growth Engineering & RevOps

Full revenue operations coverage:

- Lead scoring models and sales enablement tools
- **51 zero-dependency CLI tools** callable by agents:
  - Ahrefs API → keyword analysis, competitor backlinks
  - Google Ads API → campaign performance data
  - Mailchimp API → email sequence automation
  - Additional marketing platform integrations

---

## Technical Architecture

Follows the `.agents/skills/` cross-agent standard — fully compatible with the skill spec format used in this blog:

```bash
npx skills install coreyhaines31/marketingskills
```

**Two-layer "knowledge + tools" structure**:
- `SKILL.md` — marketing methodology for agent reasoning
- CLI tools — live API data for agent execution
- `.agents/product-marketing-context.md` — product context injection for targeted advice

The agent isn't delivering generic marketing theory — it's working from your specific product context, with real data to back the recommendations.

---

## Practical Impact for Developers

| Scenario | Without marketingskills | With marketingskills |
|----------|------------------------|----------------------|
| Pre-launch | Vague AI suggestions | Full CRO audit + copy frameworks |
| SEO | Generic checklist | Dual-track AI SEO/GEO + keyword data |
| Copywriting | AI-sounding boilerplate | Psychologically-grounded high-converting structure |
| Growth | No direction | RevOps framework + live API data |

---

## Quick Start

```bash
npx skills install coreyhaines31/marketingskills
# Then in Claude Code:
# /marketingskills:cro-audit
# /marketingskills:seo-strategy
# /marketingskills:copy-review
```

Fill in `.agents/product-marketing-context.md` with your product details and the agent's advice shifts from generic frameworks to specific, executable recommendations for your product.

---

## FAQ

**Q: How is this different from regular marketing prompt templates?**  
A: The core difference is executability. Prompt templates only generate text. The CLI tool layer in `marketingskills` lets the agent pull live data — keyword volumes, competitor analysis, email open rates — making recommendations data-driven rather than opinion-based.

**Q: Does it work with agents other than Claude Code?**  
A: Any agent framework that supports the `.agents/skills/` spec. Cursor and Windsurf are theoretically compatible, as long as they support custom skill specs.

**Q: Won't loading 32+ skills overwhelm the context window?**  
A: Skills load on demand — not all injected at once. The agent calls the relevant SKILL.md for each task; other skills don't consume context.

**Q: Does AEO/GEO optimization actually produce measurable results?**  
A: With AI search share growing rapidly, early GEO optimization cases show quantifiable citation rate improvements. The GEO module in `marketingskills` aligns with the tactics in this blog's own SEO/GEO skill: BLUF structure, FAQ modules, and brand entity tagging are the core levers.

**Q: Do the 51 CLI tools require API key setup?**  
A: Yes — each tool needs the corresponding platform's API authorization. The tools themselves are zero-dependency (no npm packages), requiring only your key to run.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
