---
title: "ai-marketing-claude：给 Claude Code 装 15 个营销技能，一条命令审计任意网站"
titleEn: "ai-marketing-claude: 15 Marketing Skills for Claude Code — Audit Any Website in One Command"
description: "ai-marketing-claude 是一套 Claude Code Skill 系统，提供 15 个 /market 命令，用 5 个并行 Subagent 对任意网站做六维营销审计并打分，生成文案/邮件序列/30天内容日历/竞品情报/客户 PDF 报告，一条命令安装，MIT 开源。"
descriptionEn: "ai-marketing-claude is a Claude Code skill system with 15 /market commands. It uses 5 parallel subagents to audit any website across 6 marketing dimensions with scoring, generates copy/email sequences/content calendars/competitive reports/client PDF reports. One-command install, MIT licensed."
pubDate: "2026-07-17"
updatedDate: "2026-07-17"
category: "Tech-Experiment"
tags: ["Claude Code", "AI营销", "Skill", "Subagent", "开源", "营销自动化", "Agent"]
heroImage: "../../assets/images/ai-marketing-claude-code-banner.jpg"
---

> **GitHub**：[zubair-trabzada/ai-marketing-claude](https://github.com/zubair-trabzada/ai-marketing-claude) · MIT  
> **安装**：`curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/ai-marketing-claude/main/install.sh | bash`

---

## 一句话说清楚它是什么

在 Claude Code 里输入 `/market audit https://example.com`，5 个并行 Subagent 同时从不同维度分析这个网站的营销状况，每个维度给出 0-100 分，最终输出一份带优先级建议的完整审计报告。

整个流程不需要离开终端，不需要登录第三方工具，不需要手动汇总——Claude Code 的 Skill 系统会协调所有步骤。

---

## 15 个 `/market` 命令

安装完成后，在任何 Claude Code session 里都可以使用：

| 命令 | 用途 |
|---|---|
| `/market audit <url>` | 完整营销审计（5 个并行 Agent，评分报告） |
| `/market quick <url>` | 60 秒快速营销快照 |
| `/market copy <url>` | 生成优化文案（含 before/after 对比） |
| `/market emails <topic>` | 生成完整邮件序列 |
| `/market social <topic>` | 30 天社交媒体内容日历 |
| `/market ads <url>` | 各平台广告创意和文案 |
| `/market funnel <url>` | 销售漏斗分析和优化建议 |
| `/market competitors <url>` | 竞品情报报告 |
| `/market landing <url>` | 落地页转化率优化分析 |
| `/market launch <product>` | 产品发布 Playbook |
| `/market proposal <client>` | 客户提案生成 |
| `/market report <url>` | 完整营销报告（Markdown） |
| `/market report-pdf <url>` | 专业营销报告（PDF） |
| `/market seo <url>` | SEO 内容审计 |
| `/market brand <url>` | 品牌声音分析和规范文档 |

---

## 核心能力：`/market audit` 的六维评分

完整审计由 5 个 Subagent 并行分析 6 个维度：

```
> /market audit https://calendly.com

Launching 5 parallel agents...
✓ Content & Messaging Analysis     — Score: 72/100
✓ Conversion Optimization          — Score: 58/100
✓ SEO & Discoverability            — Score: 81/100
✓ Competitive Positioning          — Score: 64/100
✓ Brand & Trust                    — Score: 76/100
✓ Growth & Strategy                — Score: 61/100

Overall Marketing Score: 69/100

Full report saved to MARKETING-AUDIT.md
```

六维权重设计：

| 维度 | 权重 | 评估内容 |
|---|---|---|
| **内容与信息传递** | 25% | 文案质量、价值主张、标题、CTA |
| **转化率优化** | 20% | 漏斗、表单、社会证明、摩擦点、紧迫感 |
| **SEO 与可发现性** | 20% | 页面 SEO、技术 SEO、内容结构 |
| **竞争定位** | 15% | 差异化、市场认知、替代品感知 |
| **品牌与信任** | 10% | 设计质量、信任信号、权威感 |
| **增长与策略** | 10% | 定价、获客渠道、留存 |

---

## 架构：Skill + Subagent 分层设计

```
market/SKILL.md              ← 主路由（所有 /market 命令入口）
│
├── skills/                  ← 14 个子 Skill（每个命令对应一个）
│   ├── market-audit/        # 审计编排
│   ├── market-copy/         # 文案分析与生成
│   ├── market-emails/       # 邮件序列
│   ├── market-social/       # 内容日历
│   ├── market-ads/          # 广告创意
│   ├── market-funnel/       # 漏斗分析
│   ├── market-competitors/  # 竞品情报
│   ├── market-landing/      # 落地页 CRO
│   ├── market-launch/       # 发布 Playbook
│   ├── market-proposal/     # 客户提案
│   ├── market-report/       # 报告（MD）
│   ├── market-report-pdf/   # 报告（PDF）
│   ├── market-seo/          # SEO 审计
│   └── market-brand/        # 品牌声音
│
├── agents/                  ← 5 个并行 Subagent
│   ├── market-content.md    # 内容与信息传递
│   ├── market-conversion.md # CRO 与漏斗
│   ├── market-competitive.md # 竞争定位
│   ├── market-technical.md  # 技术 SEO
│   └── market-strategy.md   # 品牌/定价/增长
│
├── scripts/                 ← Python 工具脚本
│   ├── analyze_page.py      # 网页营销分析
│   ├── competitor_scanner.py # 竞品扫描
│   ├── social_calendar.py   # 内容日历生成
│   └── generate_pdf_report.py # PDF 报告
│
└── templates/               ← 营销模板
    ├── email-welcome.md     # 欢迎序列（5封）
    ├── email-nurture.md     # 培育序列（6封）
    ├── email-launch.md      # 发布序列（8封）
    ├── proposal-template.md # 客户提案模板
    ├── content-calendar.md  # 30天内容日历
    └── launch-checklist.md  # 发布清单
```

这个设计遵循了 Claude Code Skills 系统的最佳实践：主 Skill 做路由和编排，子 Skill 做具体分析，Subagent 做并行专项执行，Python 脚本做自动化数据采集。

---

## 安装和使用

**一条命令安装**（复制进终端执行）：

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/ai-marketing-claude/main/install.sh | bash
```

**可选：启用 PDF 报告**：

```bash
pip install reportlab
```

安装完成后，在任何 Claude Code session 里直接用 `/market` 命令即可。Skills 文件会被安装到 `~/.claude/skills/market*/` 和 `~/.claude/agents/market-*.md`。

**卸载**：

```bash
./uninstall.sh
# 或者手动：
rm -rf ~/.claude/skills/market*
rm -f ~/.claude/agents/market-*.md
```

---

## 典型使用场景

### 代理商 / 自由职业者

销售前用 `/market audit` 对客户网站生成一份评分报告，用 `/market proposal` 生成带具体发现的提案文档，用 `/market report-pdf` 生成专业 PDF 作为交付物。整个销售流程从"我能帮你做什么"变成"你的网站在这 6 个维度的具体问题是……"。

### 独立开发者 / 创业者

用 `/market copy` 优化自己产品的落地页文案，用 `/market emails` 生成产品发布邮件序列，用 `/market funnel` 找出转化率最低的环节——不需要雇营销顾问，也不需要订阅另一个 SaaS 工具。

### 内容创作者

`/market competitors` 做竞品研究，`/market social` 生成 30 天内容日历，`/market launch` 规划新产品/课程的发布节奏。

---

## 和直接问 Claude 的区别

直接在 Claude Code 里问"帮我分析一下这个网站的营销"和使用这套 Skill 系统的区别：

| | 直接提问 | ai-marketing-claude |
|---|---|---|
| 分析维度 | 随机，取决于 prompt | 固定 6 维，权重明确 |
| 执行方式 | 单次对话 | 5 个 Subagent 并行 |
| 输出格式 | 自由文本 | 结构化评分 + 优先级建议 |
| 可复用性 | 每次重写 prompt | 一条命令，参数化 |
| 一致性 | 随模型随机 | Skill 定义约束输出结构 |

Skill 系统的价值在于**把"好的 prompt 工程"封装成可重复调用的工具**——你不需要每次都想着怎么问，直接 `/market audit <url>` 即可。

---

## 一句话总结

ai-marketing-claude 把营销分析、文案生成、竞品调研、客户提案这些通常需要多个工具和大量手工的工作，压缩成 Claude Code 里的 15 个命令。适合想用 AI 提升营销效率或对外销售营销服务的开发者和代理建设者。MIT 开源，一条命令装好。

© 2026 Author: Mycelium Protocol

<!--EN-->

## ai-marketing-claude: 15 Marketing Skills for Claude Code

**GitHub**: [zubair-trabzada/ai-marketing-claude](https://github.com/zubair-trabzada/ai-marketing-claude) · MIT

### What It Is

A Claude Code skill system with 15 `/market` commands. Type `/market audit https://example.com` and 5 parallel subagents analyze the site across 6 marketing dimensions, each scoring 0-100, producing a prioritized actionable report.

### 15 Commands

| Command | Purpose |
|---|---|
| `/market audit <url>` | Full audit — 5 parallel agents, 6-dimensional scoring |
| `/market quick <url>` | 60-second marketing snapshot |
| `/market copy <url>` | Optimized copy with before/after examples |
| `/market emails <topic>` | Complete email sequences |
| `/market social <topic>` | 30-day social media content calendar |
| `/market ads <url>` | Ad creative for all platforms |
| `/market funnel <url>` | Sales funnel analysis |
| `/market competitors <url>` | Competitive intelligence |
| `/market landing <url>` | Landing page CRO analysis |
| `/market launch <product>` | Product launch playbook |
| `/market proposal <client>` | Client proposal generator |
| `/market report <url>` | Full report (Markdown) |
| `/market report-pdf <url>` | Professional report (PDF) |
| `/market seo <url>` | SEO content audit |
| `/market brand <url>` | Brand voice analysis |

### Scoring Methodology (6 Dimensions)

| Dimension | Weight | Measures |
|---|---|---|
| Content & Messaging | 25% | Copy quality, value props, headlines, CTAs |
| Conversion Optimization | 20% | Funnels, forms, social proof, friction |
| SEO & Discoverability | 20% | On-page SEO, technical SEO, content structure |
| Competitive Positioning | 15% | Differentiation, market awareness |
| Brand & Trust | 10% | Design quality, trust signals, authority |
| Growth & Strategy | 10% | Pricing, acquisition channels, retention |

### Architecture

Three-layer design: main `SKILL.md` routes all `/market` commands → 14 sub-skills handle specific analysis types → 5 parallel subagents execute simultaneously during audits. Python scripts (`analyze_page.py`, `competitor_scanner.py`, etc.) handle automated data collection.

### Install

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/ai-marketing-claude/main/install.sh | bash
pip install reportlab  # optional: PDF report support
```

### Why This vs. Just Asking Claude

A Skill system encodes "good prompt engineering" into a repeatable callable — fixed dimensions, consistent output structure, parallel execution, parameterized by URL. You don't rewrite the prompt each time; you just run `/market audit <url>`.

### Use Cases

**Agency builders**: Run audit on prospect's site before a sales call → generate proposal with specific findings → deliver PDF report as client deliverable.

**Solopreneurs**: Optimize landing page copy, generate launch email sequences, find funnel bottlenecks — no marketing consultant needed.

**Content creators**: Competitor research, 30-day content calendar, product launch planning.

### Bottom Line

15 marketing analysis and generation commands for Claude Code. MIT open-source. One-command install. Converts multi-tool marketing workflows into parameterized terminal commands.

© 2026 Author: Mycelium Protocol
