---
title: "AI 协作实战手册：一位在读博士的科研、写作、编码工作流——人是主变量"
titleEn: "ai-collab-playbook-phd-workflow-skills-context-first"
description: "cnfjlhj/ai-collab-playbook 是一位 AI 方向在读博士积累的 AI 协作实战手册，433 stars。核心观点：把 AI 当同事不当工具，但人始终是主变量。涵盖科研文献四阶段工作流（调研→筛选→精读→整合）、低摩擦入口策略、Code Agent 使用心得、上下文税与心流状态、技能沉淀到 Skill/AGENTS.md 的闭环，以及对「效率幻觉」的警惕。附 10 个独立 Skill 仓库。"
descriptionEn: "cnfjlhj/ai-collab-playbook is a practical AI collaboration handbook from a PhD student in AI (433 stars). Core thesis: treat AI as a colleague, not a tool — but humans remain the primary variable. Covers a 4-stage research literature workflow (survey → filter → deep-read → integrate), low-friction entry point strategy, Code Agent usage insights, context tax and flow state, skill accumulation into AGENTS.md, and a warning against the efficiency illusion. Includes 10 independent Skill repos."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["AI协作", "科研工作流", "Code Agent", "Skills", "效率", "开源", "Claude Code", "Codex"]
heroImage: "../../assets/images/ai-collab-playbook-phd-workflow-skills-context-first-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：cnfjlhj/ai-collab-playbook  
许可证：未标注  
语言：Python  
Stars：433 · Forks：41  
最后更新：2026-08-20

---

这个仓库由一位 AI 方向在读博士写成，从 GPT-3.5 时代开始重度使用 AI，几年下来把工作流、心得和可复用的 Skill 都沉淀成了一份公开手册。

核心论点只有一句话：**把 AI 当同事，不当工具；但人始终是主变量。**

---

## 一、低摩擦入口：按任务重量选 AI 渠道

作者提出的第一个原则是「降低使用 AI 的摩擦力」。

不是所有任务都值得拉起本地 Agent、走 API、配完整工作流。任务分层：

- **轻量一次性任务** → 网页端 / 划词工具栏（豆包划词、浏览器插件）
- **项目级任务** → 本地 Code Agent（Claude Code / Codex / Gemini CLI）

作者特别提到 **IM 作为最低摩擦的派活入口**：把任务从微信/IM 抛给远端 Agent，Agent 在后台处理并回传结果。配合 `cc-connect`、`OpenClaw`、`Hermes`、`cowork` 这类工具，实现「随手发任务，随后收结果」。

逻辑和带实习生一样：**Agent 越熟悉你的偏好、项目结构和工作方式，边际效率越高**。这靠 Skill 积累，不靠一次性 Prompt。

---

## 二、科研工作流：四阶段文献管理

**调研 → 筛选 → 精读 → 整合**，目标是让 AI 帮助衔接文献网络、论文细节和个人理解，而不是替代阅读。

### 阶段一：课题调研

用 ChatGPT / Gemini Deep Research + GPT-Pro 做课题调研和可行性分析。要求不只给最新文献，还要包含**开山之作**。调研结果让 Agent 按个人偏好构建 wiki。

### 阶段二：文献网络分析

找到锚点论文后，用 **Paper Connect** 等工具可视化引用关系——引用网络越庞大，说明方向越「卷」；越稀疏，可能是蓝海。这些数据同步导出给 Agent 参考。

### 阶段三：确定精读顺序 + 逐篇攻克

用 alpharxiv 的 Blog 模式粗读摘要，确认阅读优先级后进入精读：

- **Gemini 负责宏观视角**：动机 → 数学建模 → 实验 → 结论 → 评述，生成 HTML 精读文件
- **GPT 负责细节补充**：在 Gemini 打好的基础上继续深挖

精读结果带着完整上下文让 Agent 调用 GPT-Image-2 生成信息图，做交叉验证，存档。仓库内附 `paper2html` Skill，可把 PDF / arXiv / LaTeX 源码转成中文 HTML 精读页。

### 阶段四：知识整合

带着完整上下文让 Agent 生成信息图，做交叉验证后存档。整个过程中不断扩充个人 wiki。

---

## 三、科研写作：先审后改，沉淀领域 Skill

**关于 AI 审稿**：论文草稿完成后，先用 `paperreview`、`cspaper` 等审稿 Agent 迭代几轮，把潜在问题提前解决。在给导师看之前，这个步骤能显著提升完成度——也顺带适配了「审稿人本身也在用 AI 审稿」的现实。

**最重要的警告**：一定要确保 **AI 对内容的理解是正确的**。AI 理解错了，越写越偏，越写越多，非常危险。上下文准备是所有步骤的前提。

**领域写作 Skill**：不同领域的论文写法差异很大。比起每次重新教 AI「这类论文怎么写」，更好的方式是：

1. 拿通用科研写作 Skill 作底子
2. 喂本领域认可的参考论文
3. 慢慢沉淀出适合自己领域的写作 Skill

一个有效的 Skill 应该知道：这个领域常见的论文结构、作者偏好的写作风格、哪里要展开、哪里不能废话、以及对实验/图表/相关工作的习惯要求。

---

## 四、Code Agent 的进化路径与「上下文税」

作者的工具演变路径：Cursor → Claude Code → **Claude Code + Codex + Gemini CLI + OpenCode 四个一起用**（通过 Claude-Code-Bridge / CCB）。构思阶段用多模型，确定方案后交给 GPT 模型开 `xhigh` 模式，睡一觉的功夫问题解决好了。

### 上下文税（Context Tax）

作者提出了一个值得记住的概念：「**上下文税**」。

频繁使用 Code Agent 以后反而更难进入心流状态——不是 Agent 不够强，而是 GUI 来回点、鼠标切窗口、到处 `cd`、临时查命令……每个动作单独看都不大，叠在一起就是不断打断注意力，「表面上高效使用 AI，实际上人一直在被迫切换上下文」。

解法是：人和 Agent 待在同一个连续操作回路里。

- **人的一侧**：CLI、快捷键、模糊搜索（`fzf` 找历史命令，`yazi` 终端浏览目录，`open -a Preview` 直开 PDF）——减少鼠标切换，保持注意力连续性
- **Agent 的一侧**：搜索代码用 `rg`，结构化数据用 `jq`，临时 Python 依赖用 `uv run --with`，音视频用 `ffmpeg`，图片用 `magick`，PDF/LaTeX 用 `poppler`/`xelatex`——工具选错了，模型再聪明也慢、错、做出笨方案

### 最佳实践写进 AGENTS.md

遇到更好的工具选择时，**不只是自己记住，而是写进 `AGENTS.md` 或 Skill**。下次 Agent 不需要重新猜，而是默认走合理路径。这是 Agent 协作里最重要的闭环之一。

---

## 五、反效率幻觉

手册里对这个警告非常认真：

> 警惕把理解、审美、取舍和学习过程一起外包给 AI。效率很高但不理解自己在做什么，比低效更危险。

作者强调两件事：

1. **先走最佳实践，不要一开始就退而求其次**——如果正确路径连续几次不可行再 fallback，并说明原因
2. **人必须理解基本概念和原理，才有能力 review Agent 的过程**——不懂工具链、不懂任务约束，就看不出 Agent 是真的做对了还是只是把话说圆了

---

## 六、仓库内容与独立 Skill

| 类别 | 入口 |
|------|------|
| 主文章 | `docs/phd-ai-collab.md`（2026-06-08 版） |
| 协作守则 | `AGENTS.md` / `CLAUDE.md` |
| Prompts | `prompts/`（提示词优化器、概念解释器、论文精读等） |
| Skill 目录 | `skills/full/README.md` |

**10 个独立维护的 Skill 仓库**（可按需参考，不必一次性安装）：

| Skill | 用途 |
|-------|------|
| paper-review-pipeline | 论文审稿流水线 |
| paperreview | 论文评审 |
| skills-governance | Skills 治理 |
| session-recovery-codex | 会话恢复 |
| collaborating-with-codex | Codex 协作 |
| completion-learn | 任务完成后三轴复盘：self → collaboration → tool |
| xhs-note-creator | 小红书笔记创作 |
| prompt-polisher | 提示词润色 |
| writing-anti-ai | 去 AI 味写作 |
| xhs-longform-private-publisher | 小红书长文发布 |

---

这份手册在「AI 使用技巧」类内容里比较少见：它不给捷径，不卖焦虑，也不告诉你要装哪些工具。它在认真回答「当 AI 已经能进入这些场景以后，人应该怎样继续主导问题、判断质量、沉淀经验」。433 stars 的体量说明这个问题有真实的受众。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## AI Collaboration Playbook: A PhD Student's Research, Writing, and Coding Workflows — Humans as the Primary Variable

*by Mycelium Protocol*

---

GitHub: cnfjlhj/ai-collab-playbook  
Language: Python  
Stars: 433 · Forks: 41  
Last updated: 2026-08-20

---

This repository was written by a PhD student in AI who has been a heavy AI user since GPT-3.5 — accumulating years of workflows, insights, and reusable skills into a public handbook.

The core thesis in one sentence: **treat AI as a colleague, not a tool — but humans remain the primary variable.**

---

### Low-Friction Entry Points: Match Tool Weight to Task Weight

Not every task needs a local Code Agent, an API call, or a full workflow. The author's task-weight layering:

- **Lightweight one-offs**: web UI or text-highlight tools (Doubao, browser plugins)
- **Project-level tasks**: local Code Agent (Claude Code / Codex / Gemini CLI)

IM as the lowest-friction dispatch: throw tasks from WeChat/IM to a remote agent, get results back later. Tools like `cc-connect`, `OpenClaw`, `Hermes`, `cowork` make this pattern work. The logic is the same as onboarding a junior team member: **the more familiar the agent is with your preferences, project structure, and work style, the higher the marginal efficiency** — and that comes from accumulated Skills, not one-off prompts.

---

### Research Workflow: 4-Stage Literature Pipeline

**Survey → Filter → Deep Read → Integrate** — AI helps connect the literature network, paper details, and personal understanding. It does not replace reading.

**Stage 1: Topic survey** — ChatGPT/Gemini Deep Research + GPT-Pro. Require not just recent papers but also the foundational works. Have the agent build a personal wiki from the findings.

**Stage 2: Literature network analysis** — After identifying anchor papers, use Paper Connect to visualize citation relationships. A massive citation network signals a saturated area; sparse networks may indicate blue ocean. Export this data for the agent.

**Stage 3: Deep reading** — Two models in parallel:
- **Gemini for macro perspective**: motivation → math modeling → experiments → conclusions → commentary, generates HTML files
- **GPT for detail depth**: supplements Gemini's HTML foundation

The repo includes a `paper2html` Skill that converts PDF / arXiv / LaTeX source to Chinese HTML reading pages.

**Stage 4: Knowledge integration** — With full context, have the agent call GPT-Image-2 to generate an information diagram, cross-validate against your understanding, archive.

---

### Research Writing: Review-Then-Revise, Accumulate Domain Skills

Run `paperreview` and `cspaper` review agents on drafts before showing them to your advisor — fix issues early. This also happens to align with the reality that reviewers themselves are using AI to review.

**Critical warning**: make absolutely sure **the AI has understood the content correctly**. Wrong understanding compounds — the more it writes, the further it drifts.

Build **domain-specific writing Skills**: rather than re-teaching AI how to write in your field each time, start from a general research writing Skill, feed it papers from your field you respect, and gradually distill a Skill that knows your field's structure, your stylistic preferences, where to expand, and where to be concise.

---

### Code Agent Evolution and the "Context Tax"

Author's tool progression: Cursor → Claude Code → **all four together: Claude Code + Codex + Gemini CLI + OpenCode** (via Claude-Code-Bridge / CCB). Draft the plan with multiple models, then hand execution to GPT in `xhigh` mode. Sleep on it; the problem is usually solved by morning.

**Context Tax**: heavy Code Agent use can actually make it harder to enter flow state — not because the agent isn't capable, but because GUI switching, window-hopping, `cd`-ing around, waiting for explanations constantly interrupts focus. Each individual action is small; combined, they impose a continuous "context-switching tax."

The fix: keep humans and agents in the **same continuous operation loop**.

- Human side: CLI, shortcuts, fuzzy search (`fzf`, `yazi`, `open -a Preview`) — reduce mouse switches, maintain continuity
- Agent side: code search uses `rg`, structured data uses `jq`, temp Python deps use `uv run --with`, audio/video uses `ffmpeg`, images use `magick`, PDF/LaTeX uses `poppler`/`xelatex` — the wrong tool makes even a capable model slow, wrong, and clumsy

When you discover a better tool choice, **write it into `AGENTS.md` or a Skill** — so the agent doesn't have to re-learn it next time. This is the most important feedback loop in agent collaboration.

---

### Anti-Efficiency Illusion

The handbook's most important warning:

> Beware of outsourcing understanding, aesthetic judgment, tradeoffs, and the learning process itself to AI. Being highly efficient while not understanding what you're doing is more dangerous than being slow.

Two principles:

1. **Try the optimal path first, don't fall back early** — if the right path genuinely fails after repeated attempts, fall back deliberately and state why
2. **You must understand the basics to review the agent's work** — without understanding the toolchain and task constraints, you can't tell whether the agent actually got it right or just made it sound right

---

### Repository Contents and Independent Skills

Main content: `docs/phd-ai-collab.md` (2026-06-08 edition), `AGENTS.md`/`CLAUDE.md` agent rules, `prompts/` directory, `skills/full/README.md`.

**10 independently maintained Skill repos** (install as needed, not all at once):

| Skill | Purpose |
|-------|---------|
| paper-review-pipeline | Paper review pipeline |
| completion-learn | 3-axis retrospective: self → collaboration → tool |
| writing-anti-ai | De-AI-ify writing |
| prompt-polisher | Prompt refinement |
| skills-governance | Skills governance |
| session-recovery-codex | Session recovery |
| collaborating-with-codex | Codex collaboration |
| xhs-note-creator | XiaoHongShu note creation |
| paperreview | Paper review |
| xhs-longform-private-publisher | XiaoHongShu long-form publishing |

---

This handbook is rare in the "AI usage tips" genre: it doesn't offer shortcuts, doesn't sell anxiety, and doesn't tell you which tools to install. It seriously answers: "Once AI can enter these workflows, how should humans continue to own the problem, judge quality, accumulate experience, and avoid outsourcing their understanding?" 433 stars suggests the question has a real audience.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
