---
title: "nature-skills：学术论文全流程 18 个 AI Skill，两个月 3.4 万星"
titleEn: "nature-skills-yuan1z0825-academic-paper-skill-collection"
description: "袁一哲（Yuan1z0825）发起、开源社区共同维护的 Nature 级学术论文 AI Skill 合集，18 个技能覆盖图表、润色、写作、投稿、审稿回复、引用核验、数据管理、PPT、专利转化、文献检索全链路，Apache 2.0，发布两个月 GitHub 3.4 万星。npx skills add Yuan1z0825/nature-skills 一键安装，支持 Claude Code / Codex / OpenClaw / OpenCode / Hermes。"
descriptionEn: "nature-skills is a community-built collection of 18 AI skills for the full academic paper workflow, started by Yuan Yizhe. Skills cover figures, polishing, writing, review response, citation verification, data management, PPT, patents, and literature pipelines. Apache 2.0. 34,000 GitHub stars in two months. One-line install: npx skills add Yuan1z0825/nature-skills. Works with Claude Code, Codex, OpenClaw, OpenCode, Hermes."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["学术写作", "AI技能", "Nature论文", "开源社区", "论文工具", "技能路由", "Mycelium"]
heroImage: "../../assets/images/nature-skills-yuan1z0825-academic-paper-skill-collection-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

学术论文写作的痛点不是某一个环节，而是整个链条：从文献检索、图件制作、英文润色、统计审查、审稿回复，到最后的专利转化——每个环节都有自己的规范和陷阱，任何一环出问题都可能推迟投稿。

nature-skills 从一个技能出发（nature-polishing），逐渐扩展到 nature-figure，再到今天的 18 个技能，覆盖了学术论文从开始写到发表后的几乎所有操作节点。两个月时间，GitHub 收获 3.4 万星。

GitHub: https://github.com/Yuan1z0825/nature-skills | ⭐ 34,065 | Apache 2.0

---

## 安装

```bash
npx skills add Yuan1z0825/nature-skills
```

支持：Claude Code、Codex、OpenClaw、OpenCode、Hermes。安装后触发词直接在对话里说即可，不需要单独配置。

---

## 18 个技能总览

| 技能 | 状态 | 用途 | 触发词示例 |
|------|------|------|-----------|
| **nature-polishing** | Stable | 学术文本润色/重构/翻译为 Nature 风格英文，扫描术语、单位、数值精度和声称漂移 | "Nature style", "润色", "论文英文" |
| **nature-figure** | Stable | 投稿级科研图工作流（Python/R），含 GPT Image 2 论文示意图草稿 | "Nature figure", "投稿级图片", "scientific figure" |
| **nature-ref-verifier** | Stable | 参考文献多源交叉验证：逐字段对比作者/标题/年份/卷期/页码 | "verify refs", "校验文献", "文献验证" |
| **nature-literature-pipeline** | Stable | 自动化文献发现管线：多源检索、六维评分、精读推送和本地归档 | "literature pipeline", "每日文献", "文献推送" |
| **nature-citation** | Beta | 严格限定在 Nature/CNS 系列的支撑文献检索，导出 ENW/RIS/Zotero RDF | "Nature citation", "CNS citation", "支撑文献" |
| **nature-reader** | Beta | 全文 Markdown reader，带来源锚点、图文对应、公式渲染和中英文对照 | "nature reader", "全文 Markdown", "原文对照" |
| **nature-paper-card** | Beta | 精读单篇论文，生成有来源约束的 16 节 Paper Card，含证据链和可检验研究想法 | "nature paper card", "论文精读", "证据链" |
| **nature-response** | Beta | 解析返修邮件，为互盲审稿人分别生成独立回复 + cover letter + LaTeX 模板 | "response to reviewers", "rebuttal letter", "返修邮件" |
| **nature-paper2ppt** | Beta | 从科研论文生成中文 PPTX 文献汇报 deck | "paper PPT", "journal club", "论文汇报" |
| **nature-paper-to-patent** | Beta | 从论文生成有证据约束的中国发明专利草稿，支持专利点挖掘和查新 | "paper to patent", "论文转专利", "权利要求书" |
| **nature-academic-search** | Beta | 多源文献检索、引用核验、严格他引审计、文章引用指标表 | "search papers", "查文献", "verify DOI" |
| **nature-downloader** | Beta | 通过图书馆资源入口和开放获取路径合法获取学术全文/PDF | "download papers", "图书馆下载文献", "CARSI" |
| **nature-writing** | Draft | 起草 Nature 风格手稿章节，重建论文论证 | "Nature writing", "写摘要", "写引言" |
| **nature-reviewer** | Draft | 模拟 Nature 风格预投稿评审，输出三份互盲 reviewer reports | "Nature reviewer", "预投稿评审", "reviewer report" |
| **nature-data** | Draft | Data Availability statement、数据仓储方案和 FAIR 检查 | "Data Availability", "数据可用性", "FAIR metadata" |
| **nature-statistics** | Draft | 审查/改写统计报告，覆盖 p 值、多重比较、效应量、置信区间 | "Nature statistics", "统计审查", "p value" |
| **nature-experiment-log** | Draft | 标准化记录实验图片、语音和文字材料，生成 Obsidian 实验日志 | "实验日志", "记录实验", "experiment log" |
| **nature-proposal-writer** | Beta | proposal-first 科研写作状态机，先建立证据/论证/章节契约，再起草文本 | "proposal", "开题报告", "科研写作 QA" |

Stable = 规则已稳定可生产使用；Beta = 功能完整但边界还在打磨；Draft = 可用但规则还在迭代。

---

## 这套技能怎么用

每个技能都**自包含**：自己的 SKILL.md（触发后由 Agent 加载）、README（面向人的说明）和可选的 references/ 目录（规则库）。触发方式是说触发词，Agent 加载对应的 SKILL.md 后按规则执行，返回**直接可用的产物**——可粘贴文本、`.svg`、`.pptx`、`.docx`，不是建议列表。

五条共同设计原则：

1. **优先使用一手来源**：规则基于已发表 Nature 内容、官方期刊指南或明确的本地来源，不是泛泛审美偏好
2. **显式胜过隐式**：每条规则都说明理由，而不是只给断言
3. **感知章节与任务上下文**：写作、图件、引用和回复依赖论文的不同位置
4. **输出优先**：每个技能返回能直接使用的产物
5. **可扩展**：每个技能自包含，新增不影响既有技能

---

## 从 nature-polishing 到 18 个技能

这套合集从单个润色技能出发，逐步扩展到图件制作，再到今天覆盖论文全链路的 18 个工具。整个过程是开源社区协作的结果——从 DeepMind 的 Science Skills 得到启发，发展出一套完整的 Nature 级论文辅助体系。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## nature-skills: 18 AI Skills for the Full Academic Paper Workflow — 34k Stars in Two Months

*by Mycelium Protocol*

---

The pain of academic paper writing is not one single step — it is the whole chain: literature search, figure production, English polishing, statistical review, reviewer response, patent conversion. Any link that goes wrong delays submission.

nature-skills started with one skill (nature-polishing), expanded to nature-figure, and has grown to 18 skills covering nearly every operational node from starting to write to post-publication. In two months, the project has reached 34,000 GitHub stars.

GitHub: https://github.com/Yuan1z0825/nature-skills | ⭐ 34,065 | Apache 2.0

---

### Install

```bash
npx skills add Yuan1z0825/nature-skills
```

Works with Claude Code, Codex, OpenClaw, OpenCode, and Hermes. After install, just say the trigger phrase in conversation — no extra configuration.

---

### 18 Skills at a Glance

| Skill | Status | Purpose |
|-------|--------|---------|
| **nature-polishing** | Stable | Polish, rewrite, or translate academic text to Nature-style English; scan for terminology, units, precision, and claim drift |
| **nature-figure** | Stable | Publication-ready figure workflow (Python/R); includes GPT Image 2 paper schematic drafts |
| **nature-ref-verifier** | Stable | Multi-source cross-verification of references: author/title/year/volume/page field-by-field comparison |
| **nature-literature-pipeline** | Stable | Automated literature discovery: multi-source retrieval, six-dimension scoring, deep-read push, local archive |
| **nature-citation** | Beta | Retrieve supporting references strictly scoped to Nature/CNS series; export ENW/RIS/Zotero RDF |
| **nature-reader** | Beta | Full-text Markdown reader with source anchors, figure–text alignment, equation rendering, bilingual parallel |
| **nature-paper-card** | Beta | Deep-read a single paper: 16-section Paper Card with evidence chains, argument logic, and testable research ideas |
| **nature-response** | Beta | Parse revision emails; generate independent replies for each blind reviewer + cover letter + LaTeX template |
| **nature-paper2ppt** | Beta | Generate a Chinese-language PPTX journal-club deck from a research paper |
| **nature-paper-to-patent** | Beta | Generate evidence-constrained Chinese invention patent drafts from papers; patent mining and novelty search |
| **nature-academic-search** | Beta | Multi-source literature search, citation verification, strict citation audit, citation impact tables |
| **nature-downloader** | Beta | Legally obtain full-text PDFs via library portals, CARSI, and open-access paths |
| **nature-writing** | Draft | Draft Nature-style manuscript sections; rebuild paper argumentation |
| **nature-reviewer** | Draft | Simulate Nature-style pre-submission review; output three blind reviewer reports with Major/Minor issues |
| **nature-data** | Draft | Data Availability statement, data repository plan, FAIR metadata check |
| **nature-statistics** | Draft | Review/rewrite statistical reporting: p-values, multiple comparisons, effect sizes, confidence intervals |
| **nature-experiment-log** | Draft | Standardize recording of experiment images, voice, and text; generate Obsidian experiment log |
| **nature-proposal-writer** | Beta | Proposal-first research writing state machine: establish evidence/argument/section contract before drafting |

Stable = production-ready rules. Beta = functionally complete, boundaries still being refined. Draft = usable but rules still iterating.

---

### Design Principles

All 18 skills share five design principles:

1. **First-source priority**: rules are based on published Nature content, official journal guidelines, or explicit local sources — not general aesthetic preference
2. **Explicit over implicit**: every rule explains its reasoning rather than just asserting it
3. **Context-aware**: writing, figures, citations, and reviewer responses each depend on where in the paper you are
4. **Output-first**: every skill returns something directly usable — pasteable text, `.svg`, `.pptx`, `.docx` — not a list of suggestions
5. **Self-contained and extensible**: each skill lives in its own directory; adding a new skill does not require modifying any existing one

---

### From nature-polishing to 18 Skills

The collection started from a single polishing skill, expanded to figure production, and has grown into a full-coverage Nature-paper toolset through open-source community collaboration — inspired by DeepMind's Science Skills, developed into something broader.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
