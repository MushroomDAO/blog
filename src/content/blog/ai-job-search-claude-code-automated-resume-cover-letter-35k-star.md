---
title: "ai-job-search：35k Star，一位地球物理学家用 Claude Code 把求职工程化，69 投 20 面 1 offer"
titleEn: "ai-job-search-claude-code-automated-resume-cover-letter-35k-star"
description: "MadsLorentzen/ai-job-search 是一个跑在你自己机器上的 AI 求职自动化框架，基于 Claude Code，三个核心命令：/setup（建立候选人档案）、/scrape（搜索职位并评估匹配度）、/apply（评估 + 定制简历 + 写 Cover Letter + 审稿 Agent + 修订输出）。作者是一位失业地球物理学家，69 份定制申请、20 次初试、1 份 offer，于 2026 年 6 月入职 AI 工程师。现已 35k Star，MIT 开源。"
descriptionEn: "MadsLorentzen/ai-job-search is an AI job application framework that runs on your machine, built on Claude Code. Three core commands: /setup (build your candidate profile), /scrape (search portals and score fit), /apply (evaluate + tailor CV + write cover letter + reviewer agent + revise). The author — a laid-off geophysicist — ran 69 tailored applications, landed 20 first interviews, and signed one offer. He started as an AI engineer in June 2026. Now at 35k stars, MIT licensed."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Tech-News"
tags: ["开源", "Claude Code", "求职自动化", "简历", "Cover Letter", "AI Agent", "LaTeX", "职业发展"]
heroImage: "../../assets/images/ai-job-search-claude-code-automated-resume-cover-letter-35k-star-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：MadsLorentzen/ai-job-search ⭐ 35,452 | Forks 12,170 | Python | MIT  
创建：2026-03-18 | 最近更新：2026-08-26

---

## 先说一个细节

作者 Mads Lorentzen，地球物理学家，2025 年底被裁员。他没有更新 LinkedIn 等通知，而是花时间造了这套工具，用它跑了自己的求职流程：

- **69 份定制申请**
- **20 次初试**
- **1 份 offer**
- **2026 年 6 月入职，职位：AI 工程师**

他在每家公司都主动告知自己用了 AI 辅助求职，结果没有一次成为劣势——反而几乎每次都引发了技术对话。随后他把这套工具开源，现在有 35,452 个 Star。

---

## 优雅的递归

用户提炼得很准：**程序员们终于把"用 AI 替代自己工作"的能力，用在了"找到下一份被 AI 替代的工作"上面。**

这不是反讽，是现实。求职本身是一个极度重复、高度标准化的信息处理流程：读职位描述、评估匹配度、改简历、写 Cover Letter、做面试准备……这些工作 AI 做得比人耐心、比人一致，而且不会在第 50 封信的时候开始偷懒。

---

## 核心工作流

```
/setup        /scrape           /apply <url>
  |               |                  |
  v               v                  v
建立档案      搜索职位           评估匹配度
（简历/      多平台去重         评分 + 建议
LinkedIn/    按匹配度排序
面试）            |                  |
                  v                  v
              选中职位          起草简历 + Cover Letter
              → /apply          （LaTeX，定制化）
                                     |
                                     v
                                审稿 Agent 审核
                                → 修订 → 最终输出
```

### `/setup`：建立候选人档案

三条路径，自动识别你有什么：
- **Path A（推荐）**：把你的 CV PDF、LinkedIn 导出、学历证明、推荐信放进 `documents/` 文件夹，自动解析
- **Path B**：直接粘贴 CV 文本
- **Path C**：和 AI 进行一次"入职面试"，逐步建立档案

档案拆成 7 个结构化文件：候选人简历（01）、行为特征（02）、写作风格（03）、岗位评估标准（04）、简历模板（05）、Cover Letter 模板（06）、面试准备（07）。

> 重要：Fork 后必须改成 **private 仓库**，因为 `/setup` 会把姓名、联系方式、薪资期望等写入被 git 追踪的文件。

### `/scrape`：搜索职位

同时搜索多个职位平台，去重后按匹配度排序展示。内置平台：Jobindex、Jobnet、Akademikernes Jobbank、Jobdanmark（丹麦市场），以及 LinkedIn（全球）和 freehire.me（多市场）。

其他市场的平台可以用 `/add-portal` 命令自动生成：给出招聘网站，AI 分析 URL 结构和结果格式，生成并测试新的搜索 skill。

### `/apply <url>`：完整申请流水线

1. **拉取职位描述**（无法访问时可粘贴全文）
2. **评估匹配度**：五个维度打分，有无 deal-breaker，给出建议
3. **定制简历**（LaTeX，`lualatex` 编译）
4. **写 Cover Letter**（LaTeX，`xelatex` 编译，专用 `.cls` 文件）
5. **审稿 Agent** 批评初稿
6. **修订** → 输出最终版本
7. **ATS 可读性检查**（需要 poppler，自动降级）

职位描述被视为不可信输入——AI 不会执行其中嵌入的指令，也不会跟随其中的链接。

---

## 延伸命令

| 命令 | 功能 |
|------|------|
| `/interview` | 针对某次面试生成定制准备包：公司研究、可能问题 + STAR 示例映射、模拟面试（roleplay）。不会杜撰经历，缺口给诚实的过渡答案。 |
| `/outcome` | 记录申请结果（面试轮次、offer、拒信、无音讯），归档材料，生成追踪文件。`/outcome followup` 找出超过 10 天无回音的申请，起草跟进邮件（不发送，至多两次）。 |
| `/rank` | 批量评分所有新抓取的职位，返回排名短名单（并行 Agent 同时处理），过滤截止日期和 dead posting。 |
| `/expand` | 扫描你档案里链接的公开来源（GitHub、portfolio、Kaggle、Google Scholar）发现隐性技能，加入档案并标注来源。 |
| `/upskill` | 分析你的技能与目标岗位的差距，生成优先级热力图和学习计划（含实际学习资源和时间估算）。 |
| `/html-report` | 生成自包含 HTML 仪表板：统计卡、状态/行业/渠道/漏斗图（内联 SVG，无外部依赖），可过滤的申请列表。离线可用。 |
| `/notion-sync` | 单向同步到 Notion 数据库（官方 Notion MCP，OAuth），一行一个职位，只读。 |
| `/gmail-sync` | 读取 Gmail 检测申请状态信号（面试邀请、评估链接、offer、拒信），批量提案供你审核后写入追踪记录。 |
| `/add-template` | 注册自定义简历或 Cover Letter 模板（LaTeX / Typst），测试编译后接入 `/apply`。 |

---

## 技术栈要求

- **Claude Code CLI**（核心 AI 引擎）
- Python 3.10+
- Bun（职位搜索 CLI 工具）
- LaTeX：TeX Live / MacTeX / TinyTeX（`lualatex` 编 CV，`xelatex` 编 Cover Letter）
- 可选：poppler（`pdftotext`，ATS 可读性检查）

---

## 为什么值得关注

35k Star 和 12k Fork 的规模不是噶韭菜——这个量级通常意味着真实的使用率。

更有意思的是它的出身：不是某家 AI 公司的 Demo，不是技术博主刷流量的项目，而是一个真的被裁员的人，在真实压力下造的真实工具，用它找到了真实的下一份工作。开源之后，它变成了一个框架，供其他人按自己的市场、自己的简历风格 fork 和改造。

**最值得注意的设计选择**：整套流程跑在你自己的机器上，数据不离开本地，没有 SaaS 订阅，没有"你的简历数据帮我们训练模型"。你 fork，你填档案，你跑流程，你拥有输出。

---

**相关链接**

- GitHub：https://github.com/MadsLorentzen/ai-job-search
- 作者 LinkedIn：https://www.linkedin.com/in/mads-lorentzen/
- 视频演示（The Next New Thing）：https://www.youtube.com/watch?v=HoVxjMNFYv4
- Ko-fi（支持作者）：https://ko-fi.com/madslorentzen

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## ai-job-search: 35k Stars — A Geophysicist Built This After Being Laid Off, Got Hired as an AI Engineer

*by Mycelium Protocol*

---

GitHub: MadsLorentzen/ai-job-search ⭐ 35,452 | Forks 12,170 | Python | MIT  
Created: 2026-03-18

---

### One Detail First

Mads Lorentzen, a geophysicist, was laid off in late 2025. Instead of updating his LinkedIn, he spent the time building this framework and using it to run his own job search — the same `/scrape`, `/apply`, and `/interview` workflow in this repo, used weekly, on his own career:

- **69 tailored applications**
- **20 first interviews**
- **1 signed offer**
- **Started as an AI engineer, June 2026**

He told every employer he was using AI assistance in his search. Not once did it count against him — it almost always sparked a genuine technical conversation. He then open-sourced the whole thing. It now has 35,452 stars.

---

### An Elegant Recursion

Programmers using their ability to automate things with AI... to find their next job that might be automated by AI. Not as irony — as a pragmatic response to the moment. Job searching is a massively repetitive, highly standardized information processing workflow: read job descriptions, evaluate fit, tailor a CV, write a cover letter, prep for interviews. AI does this more patiently and more consistently than humans, and doesn't start cutting corners after the 50th application.

---

### Core Workflow

```
/setup        /scrape           /apply <url>
  |               |                  |
  v               v                  v
build profile  search portals    evaluate fit
(from docs /   deduplicate       score + recommend
LinkedIn /     rank by fit
interview)         |                  |
                   v                  v
               pick a match      draft CV + cover letter
               → /apply          (LaTeX, tailored)
                                       |
                                       v
                                 reviewer agent critiques
                                 → revise → final output
```

**`/setup`** — Three paths, auto-detected:
- **Path A (recommended)**: drop your CV PDF, LinkedIn export, diplomas, references into `documents/` — automatically parsed
- **Path B**: paste a CV directly
- **Path C**: answer an AI "intake interview"

Profile becomes 7 structured files: candidate profile (01), behavioral profile (02), writing style (03), job evaluation framework (04), CV templates (05), cover letter templates (06), interview prep (07).

> Important: change the fork to **private** — `/setup` writes your name, contact info, and salary expectations into tracked files.

**`/scrape`** — Searches multiple portals simultaneously, deduplicates, ranks by fit. Built-in: Jobindex, Jobnet, Akademikernes Jobbank, Jobdanmark (Denmark), LinkedIn (global), freehire.me (multi-market). Other markets: use `/add-portal` to auto-generate a search skill for any job board.

**`/apply <url>`** — Full pipeline:
1. Fetch job description (or paste if blocked)
2. Evaluate fit across five dimensions, flag deal-breakers
3. Draft tailored CV (LaTeX, `lualatex`)
4. Draft cover letter (LaTeX, `xelatex`, custom `.cls`)
5. Reviewer agent critiques the draft
6. Revise → final output
7. ATS parseability check (requires poppler, gracefully degrades)

Job postings are treated as untrusted input — the workflow never follows instructions embedded in them or fetches links from their body.

---

### Extended Commands

| Command | What it does |
|---------|-------------|
| `/interview` | Stage-specific prep: company research, likely questions mapped to your STAR examples, mock interview roleplay. Honest bridge answers for gaps — no invented experience. |
| `/outcome` | Record results (interview stages, offers, rejections, silence), archive materials. `/outcome followup` surfaces applications gone quiet >10 days, drafts a follow-up (max twice, never sends). |
| `/rank` | Batch-score all scraped postings in parallel, return a ranked shortlist with per-job strengths and gaps. Filters expired postings and deadline urgency. |
| `/expand` | Scan publicly linked sources (GitHub, portfolio, Kaggle, Scholar) for skills not explicit in documents; add to profile with source tags. |
| `/upskill` | Analyze skill gaps vs. target roles; produce prioritized gap heatmap and learning plan with actual resources and time estimates. |
| `/html-report` | Self-contained HTML dashboard: stat cards, status/sector/channel/funnel charts (inline SVG), filterable table. Fully offline. |
| `/notion-sync` | One-way sync to Notion database (official Notion MCP, OAuth). Read-only live view; repo files stay source of truth. |
| `/gmail-sync` | Reads Gmail for status signals (interview invites, offers, rejections); proposes as a batch for your approval before anything is written. |
| `/add-template` | Register a custom CV or cover letter template (LaTeX, Typst, or any toolchain), with a mandatory test compile. |

---

### Requirements

- **Claude Code CLI** (the AI engine)
- Python 3.10+
- Bun (job portal CLI tools)
- LaTeX: TeX Live / MacTeX / TinyTeX (`lualatex` for CV, `xelatex` for cover letter)
- Optional: poppler (`pdftotext`, ATS check)

---

### Why It Matters

35k stars and 12k forks at this scale usually indicates genuine adoption, not hype-cycle virality.

More interesting is its origin: not an AI company's demo, not a content-creator traffic play — a person under real economic pressure who built a real tool, used it to find a real job, and then opened it up for others to fork and adapt to their own market and style.

The most notable design choice: **everything runs on your machine**. No SaaS subscription, no "your resume data trains our models," no data leaves your local environment. You fork it, fill in your profile, run the workflow, own the output.

---

**Links**

- GitHub: https://github.com/MadsLorentzen/ai-job-search
- Author LinkedIn: https://www.linkedin.com/in/mads-lorentzen/
- Video walkthrough (The Next New Thing): https://www.youtube.com/watch?v=HoVxjMNFYv4
- Ko-fi (support the author): https://ko-fi.com/madslorentzen

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
