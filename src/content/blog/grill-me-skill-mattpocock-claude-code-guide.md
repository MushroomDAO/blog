---
title: "grill-me：181k Star 的 Claude Code Skill，用一个问题消灭 AI 编码最常见的失败模式"
titleEn: "grill-me: The 181k-Star Claude Code Skill That Eliminates the Most Common AI Coding Failure Mode One Question at a Time"
description: "Matt Pocock 的 grill-me skill 在 GitHub 拿下 18.1 万 Star，单独安装量超 62 万次。它解决的问题只有一个：你以为 AI 理解了你想要什么，但它没有。本文拆解 grill-me 的工作机制、grill-with-docs 的进阶用法、以及 chaseai 扩展的跨模型对抗评审。"
descriptionEn: "Matt Pocock's grill-me skill hit 181k stars on GitHub with over 620k standalone installs. It solves exactly one problem: you think the AI understood what you wanted — it didn't. This post breaks down how grill-me works, the grill-with-docs advanced pattern, and the chaseai cross-model adversarial review extension."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["Claude Code", "AI编程", "grill-me", "Matt Pocock", "Skill", "工程实践", "AI工具", "提示工程", "Codex", "对齐"]
heroImage: "../../assets/images/grill-me-skill-mattpocock-claude-code-guide-banner.jpg"
---

> **仓库**：mattpocock/skills · **⭐ 181,414** · **15,492 forks** · MIT  
> **安装量**：10.5M 次（全套） · `grill-me` 单独 **624,700 次**  
> **安装方式**：`npx skills@latest add mattpocock/skills` 或 Claude Code 插件  
> **作者**：Matt Pocock — Total TypeScript 创始人，60k+ 订阅者技术 Newsletter

---

## 一、为什么需要 grill-me

Matt Pocock 在仓库 README 里引用了《The Pragmatic Programmer》的一句话：

> "No-one knows exactly what they want."

这是 AI 编码最常见的失败模式——你以为你说清楚了，AI 开始写代码，写完你一看：完全不是你想要的。

不是 AI 的错，是你们之间有一个**对齐 gap**：你脑子里有一棵决策树，但你告诉 AI 的只是树根那个节点，剩下的分支 AI 在猜。猜对了是运气，猜错了你要从头来过。

**grill-me 做的事情只有一件：在你动手之前，把那棵决策树完整地走一遍。**

不是让你写更长的 prompt，而是让 AI 用问题把你没想清楚的地方全问出来——一次一个问题，等你回答了再问下一个，直到每一个分支都有了明确的答案。

---

## 二、数字说话：这个 skill 有多流行

| 指标 | 数据 |
|---|---|
| GitHub Stars | **181,414** |
| GitHub Forks | 15,492 |
| skills.sh 全套安装量 | 10.5M 次 |
| `grill-me` 单独安装量 | **624,700 次** |
| `grill-with-docs` 安装量 | 529,500 次 |
| 仓库内技能数量 | 55 个 |
| chaseai 扩展（grill-me-codex） | 788★ |

`grill-me` 是整个 55 个 skill 套件里安装量最高的。这不是因为它最复杂——它的核心 SKILL.md 只有 5 行——而是因为它解决的问题最根本。

---

## 三、grill-me 的工作机制

### 核心 SKILL.md（完整内容）

```markdown
Interview me relentlessly about every aspect of this until we 
reach a shared understanding. Walk down each branch of the 
decision tree, resolving dependencies between decisions one-by-one. 
For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each 
question before continuing. Asking multiple questions at once 
is bewildering.

If a *fact* can be found by exploring the environment 
(filesystem, tools, etc.), look it up rather than asking me. 
The *decisions*, though, are mine — put each one to me and 
wait for my answer.

Do not act on it until I confirm we have reached a shared 
understanding.
```

5 行指令，背后是几个精妙的设计决定：

**1. 一次只问一个问题**

"Asking multiple questions at once is bewildering." 这个约束不是为了礼貌，是为了让每个决策点都有完整的思考。一次问三个问题，你会草率地回答三个，结果是三个决策都不够扎实。

**2. AI 帮你查事实，但决定是你的**

"If a *fact* can be found by exploring the environment, look it up rather than asking me." 项目里已经有的配置、已经存在的函数、当前的目录结构——这些 AI 自己查。只有**决策**——选 A 还是 B，用这个库还是那个——才需要问你。这让 grilling 的密度更高，每个问题都是真实的决策点。

**3. 每个问题附带推荐答案**

"For each question, provide your recommended answer." AI 不只是问，它告诉你它会怎么选。你同意就往下走，不同意就说为什么——这本身就是一次更有效的思考。

**4. 不动手直到你确认**

"Do not act on it until I confirm we have reached a shared understanding." 这是最重要的约束。grilling 阶段只是对话，没有任何文件被修改。决策树走完、你确认、才开始实现。

---

## 四、安装和使用

### 方法 1：skills.sh 安装器（可编辑，可定制）

```bash
npx skills@latest add mattpocock/skills
```

按提示选择你想安装的 skill，然后在 Claude Code 里运行一次：

```
/setup-matt-pocock-skills
```

它会问你：用什么 issue tracker（GitHub / Linear / 本地文件）、triage 用什么 label、文档保存在哪里。回答完，全套 skill 就可以用了。

### 方法 2：Claude Code 原生插件（不需要维护，自动更新）

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock
```

两种安装方式的哲学不同：
- **skills.sh**：把文件复制到你的项目，你可以改，可以 fork，可以做成自己的版本
- **插件**：只读的托管 bundle，Matt Pocock 更新了你就自动跟上

### 使用

安装完成后，在 Claude Code 的任何会话里，告诉它你想做什么，然后：

```
/grill-me
```

AI 会开始问你问题。一次一个，等你回答完再问下一个，直到它认为已经走完了所有关键分支，然后问你："我们是否已经达成了共识？"你确认之后，它才开始动手。

---

## 五、grill-with-docs：更强的工程版

`grill-with-docs` 是 `grill-me` 的工程专用版，在 grilling 的基础上额外做两件事：

### 1. 建立项目共享词汇（CONTEXT.md）

AI 会帮你建立一个 `CONTEXT.md`，把项目里的专有术语记录下来。

Matt 举了一个例子：

- **BEFORE**："There's a problem when a lesson inside a section of a course is made 'real' (i.e. given a spot in the file system)"
- **AFTER**："There's a problem with the materialization cascade"

从 30 个词压缩到 3 个词，但意思完全精确。这个共享词汇一旦建立：
- 变量名、函数名、文件名都用这套语言命名
- 代码库更容易导航
- AI 思考时花更少的 token，因为它用更精确的语言

### 2. 内联写 ADR（Architecture Decision Records）

每一个关键的架构决策，grill-with-docs 会在 grilling 过程中同步写成 ADR 文档——记录**是什么、为什么、有哪些选项被拒绝**。三个月后回来看代码，你能知道当初为什么这样决定，而不是只看到结果。

```
/grill-with-docs
```

适合在一个项目里频繁工作的场景——词汇越积累越有价值。

---

## 六、chaseai 扩展：加上 Codex 跨模型对抗评审

`chaseai-yt/grill-me-codex`（788★）在 Matt Pocock 的 grill-me 基础上加了两个 Act：

| | Act 1 | Act 2 | Act 3（可选） |
|---|---|---|---|
| 执行者 | Claude 问你问题 | Codex 对抗评审计划 | Codex 写代码，Claude 评审 |
| 输出 | 锁定的计划 | PLAN.md + PLAN-REVIEW-LOG.md | 实现的代码 + diff 评审 |

**为什么需要第二个模型？**

> "The same model that plans the build and writes the build can't be trusted to grade its own work — it's an echo chamber."

用同一个模型来计划、实现、评审自己的工作，是一个结构性的问题——它看不到自己的盲点。Codex（OpenAI 模型）来评审 Claude 的计划，或者 Codex 实现、Claude 评审 diff，形成真正的交叉验证。

**Act 2 工作流程**：

1. Claude 把锁定的计划写入 `PLAN.md`，创建 `PLAN-REVIEW-LOG.md`
2. **第 1 轮**：Codex 以只读沙箱模式评审计划，返回 `VERDICT: APPROVED` 或 `VERDICT: REVISE`
3. **第 2-N 轮**：Claude 修改；同一个 Codex session 被恢复（记得上一轮的批评），只检查是否解决了之前的问题
4. 上限 5 轮（可配置），批准或到上限结束
5. **你只参与两次**：启动，和最终签字

**Act 3（角色翻转）**：

Codex 拿到 `PLAN.md` 作为冻结 spec，获得完整写权限（`--yolo`），实现整个计划并自己跑测试。Claude 则读完整 diff，像 PR 评审者一样审查——Codex 的测试结果只是参考，Claude 自己跑的才算数。

安装：

```bash
cp -r skills/* ~/.claude/skills/
```

前提：`npm install -g @openai/codex@latest` 并运行 `codex login`。

---

## 七、grill-me 套件里其他值得安装的 skill

Matt Pocock 的 55 个 skill 里，下面这几个解决了 AI 编码的其他常见问题：

| Skill | 安装量 | 解决什么问题 |
|---|---|---|
| `/improve-codebase-architecture` | 514.9K | 扫描代码库找出设计问题，HTML 报告 + grilling 会话 |
| `/tdd` | 494.6K | 红绿重构循环，AI 先写失败测试再修复 |
| `/handoff` | 413.7K | 会话压缩成交接文档，让另一个 agent 继续 |
| `/prototype` | 399.3K | 快速做一个可运行的原型来回答设计问题 |
| `/diagnosing-bugs` | 216.2K | 系统性调试循环：复现→最小化→假设→验证→修复 |
| `/code-review` | 151.8K | 两个维度并行：代码规范 + 是否符合 spec |
| `/wayfinder` | 130.3K | 把超大任务（一个 session 装不下的）分解成调查票 |

---

## 八、为什么是"一个问题"而不是"更好的 prompt"

很多人的直觉是：写更长、更详细的 prompt，就能减少 AI 的猜测。

但 Matt Pocock 的洞察是：**你自己也不知道你想要什么的全部细节**。你写 prompt 的时候，脑子里还有很多隐含的假设没有意识到——直到 AI 做出了一个不符合你期望的决定，你才意识到那个假设存在。

grill-me 的做法是翻转这个流程：不是让你提前想清楚所有细节，而是让 AI 用问题把那些隐含假设**挖出来**，一个一个地逼你表态。

这不是提示工程，是一种更根本的协作模式：先对齐，再动手。

---

## 参考资源

- **mattpocock/skills**：[GitHub](https://github.com/mattpocock/skills) · [skills.sh](https://skills.sh/mattpocock/skills)
- **chaseai-yt/grill-me-codex**：[GitHub](https://github.com/chaseai-yt/grill-me-codex)（788★）
- **Matt Pocock Newsletter**：[aihero.dev/s/skills-newsletter](https://www.aihero.dev/s/skills-newsletter)（60k 订阅者）
- **Chase AI Community**：[skool.com/chase-ai](https://www.skool.com/chase-ai/about)

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: mattpocock/skills · **⭐ 181,414** · **15,492 forks** · MIT  
> **Installs**: 10.5M (full suite) · `grill-me` standalone **624,700 times**  
> **Installation**: `npx skills@latest add mattpocock/skills` or Claude Code plugin  
> **Author**: Matt Pocock — Founder of Total TypeScript, technical Newsletter with 60k+ subscribers

---

## 1. Why You Need grill-me

Matt Pocock quotes a line from *The Pragmatic Programmer* in the repository README:

> "No-one knows exactly what they want."

This is the most common failure mode in AI-assisted coding — you think you've explained it clearly, the AI starts writing code, and when it's done you look at it: it's completely not what you wanted.

It's not the AI's fault. There's an **alignment gap** between you: you have an entire decision tree in your head, but you only told the AI the root node, and the AI is guessing at the remaining branches. Getting it right is luck; getting it wrong means starting over.

**grill-me does exactly one thing: before you start, it walks the entire decision tree.**

Not by making you write a longer prompt, but by having the AI use questions to surface everything you haven't thought through — one question at a time, waiting for your answer before asking the next, until every branch has a definitive answer.

---

## 2. By the Numbers: How Popular Is This Skill

| Metric | Data |
|---|---|
| GitHub Stars | **181,414** |
| GitHub Forks | 15,492 |
| skills.sh full suite installs | 10.5M |
| `grill-me` standalone installs | **624,700** |
| `grill-with-docs` installs | 529,500 |
| Skills in the repository | 55 |
| chaseai extension (grill-me-codex) | 788★ |

`grill-me` is the highest-installed skill in the entire 55-skill suite. Not because it's the most complex — its core SKILL.md is only 5 lines — but because it solves the most fundamental problem.

---

## 3. How grill-me Works

### Core SKILL.md (full content)

```markdown
Interview me relentlessly about every aspect of this until we 
reach a shared understanding. Walk down each branch of the 
decision tree, resolving dependencies between decisions one-by-one. 
For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each 
question before continuing. Asking multiple questions at once 
is bewildering.

If a *fact* can be found by exploring the environment 
(filesystem, tools, etc.), look it up rather than asking me. 
The *decisions*, though, are mine — put each one to me and 
wait for my answer.

Do not act on it until I confirm we have reached a shared 
understanding.
```

Five lines of instructions, backed by several elegant design decisions:

**1. One question at a time**

"Asking multiple questions at once is bewildering." This constraint isn't about courtesy — it's about ensuring each decision point receives complete attention. Ask three questions at once and you'll give three hasty answers, resulting in three undercooked decisions.

**2. The AI looks up facts, but decisions are yours**

"If a *fact* can be found by exploring the environment, look it up rather than asking me." Existing configs in the project, functions already present, the current directory structure — the AI handles all of that itself. Only **decisions** — A or B, this library or that — require asking you. This raises the density of the grilling: every question is a genuine decision point.

**3. Each question comes with a recommended answer**

"For each question, provide your recommended answer." The AI doesn't just ask — it tells you what it would choose. You agree and move on, or you explain why not — which itself is a more effective way to think.

**4. No action until you confirm**

"Do not act on it until I confirm we have reached a shared understanding." This is the most important constraint. The grilling phase is conversation only — no files are modified. Only after the decision tree is walked, and you confirm, does implementation begin.

---

## 4. Installation and Usage

### Method 1: skills.sh installer (editable, customizable)

```bash
npx skills@latest add mattpocock/skills
```

Follow the prompts to select which skills to install, then run once inside Claude Code:

```
/setup-matt-pocock-skills
```

It will ask you: what issue tracker to use (GitHub / Linear / local file), what label to use for triage, where to save documentation. After answering, the full skill suite is ready.

### Method 2: Claude Code native plugin (no maintenance required, auto-updates)

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock
```

The two installation approaches have different philosophies:
- **skills.sh**: Copies files into your project — you can modify them, fork them, turn them into your own version
- **Plugin**: A read-only hosted bundle — when Matt Pocock updates, you automatically follow

### Usage

After installation, in any Claude Code session, tell it what you want to do, then:

```
/grill-me
```

The AI will start asking you questions. One at a time, waiting for your answer before asking the next, until it believes all critical branches have been covered — then it asks: "Have we reached a shared understanding?" Only after you confirm does it begin.

---

## 5. grill-with-docs: The Stronger Engineering Version

`grill-with-docs` is the engineering-focused variant of `grill-me`, adding two additional steps on top of grilling:

### 1. Establishing a shared project vocabulary (CONTEXT.md)

The AI helps you build a `CONTEXT.md` that records the project's specialized terminology.

Matt gives an example:

- **BEFORE**: "There's a problem when a lesson inside a section of a course is made 'real' (i.e. given a spot in the file system)"
- **AFTER**: "There's a problem with the materialization cascade"

Compressed from 30 words to 3, with complete precision of meaning. Once this shared vocabulary is established:
- Variable names, function names, and file names all use this language
- The codebase becomes easier to navigate
- The AI thinks using fewer tokens, because it uses more precise language

### 2. Writing ADRs inline (Architecture Decision Records)

For every key architectural decision, grill-with-docs simultaneously writes an ADR document during the grilling process — recording **what it is, why it was chosen, and which alternatives were rejected**. When you come back to the code three months later, you can understand why a decision was made, not just see the result.

```
/grill-with-docs
```

Best suited for projects you work on frequently — the vocabulary accumulates and grows more valuable over time.

---

## 6. chaseai Extension: Adding Codex Cross-Model Adversarial Review

`chaseai-yt/grill-me-codex` (788★) adds two Acts on top of Matt Pocock's grill-me:

| | Act 1 | Act 2 | Act 3 (optional) |
|---|---|---|---|
| Executor | Claude asks you questions | Codex adversarially reviews the plan | Codex writes code, Claude reviews |
| Output | Locked plan | PLAN.md + PLAN-REVIEW-LOG.md | Implemented code + diff review |

**Why do you need a second model?**

> "The same model that plans the build and writes the build can't be trusted to grade its own work — it's an echo chamber."

Using the same model to plan, implement, and review its own work is a structural problem — it cannot see its own blind spots. Codex (an OpenAI model) reviews Claude's plan, or Codex implements and Claude reviews the diff, creating genuine cross-validation.

**Act 2 workflow**:

1. Claude writes the locked plan into `PLAN.md`, creates `PLAN-REVIEW-LOG.md`
2. **Round 1**: Codex reviews the plan in read-only sandbox mode, returning `VERDICT: APPROVED` or `VERDICT: REVISE`
3. **Rounds 2-N**: Claude revises; the same Codex session is resumed (it remembers previous critiques) and only checks whether earlier issues have been resolved
4. Maximum 5 rounds (configurable), ending with approval or at the limit
5. **You participate only twice**: at launch, and at final sign-off

**Act 3 (role reversal)**:

Codex takes `PLAN.md` as a frozen spec, gets full write access (`--yolo`), implements the entire plan and runs tests itself. Claude then reads the complete diff and reviews it like a PR reviewer — Codex's test results are for reference only; what Claude runs independently is what counts.

Installation:

```bash
cp -r skills/* ~/.claude/skills/
```

Prerequisites: `npm install -g @openai/codex@latest` and run `codex login`.

---

## 7. Other Skills in the grill-me Suite Worth Installing

Among Matt Pocock's 55 skills, the following address other common AI coding problems:

| Skill | Installs | Problem It Solves |
|---|---|---|
| `/improve-codebase-architecture` | 514.9K | Scans the codebase for design issues, produces an HTML report + grilling session |
| `/tdd` | 494.6K | Red-green-refactor loop — AI writes failing tests first, then fixes them |
| `/handoff` | 413.7K | Compresses a session into a handoff document so another agent can continue |
| `/prototype` | 399.3K | Quickly builds a runnable prototype to answer a design question |
| `/diagnosing-bugs` | 216.2K | Systematic debugging loop: reproduce → minimize → hypothesize → verify → fix |
| `/code-review` | 151.8K | Two parallel dimensions: code conventions + compliance with spec |
| `/wayfinder` | 130.3K | Breaks an oversized task (too large for one session) into investigation tickets |

---

## 8. Why "One Question" Rather Than "A Better Prompt"

Many people's instinct is: write a longer, more detailed prompt to reduce AI guessing.

But Matt Pocock's insight is: **you don't know the full details of what you want either**. When you write a prompt, there are many implicit assumptions in your head that you haven't consciously recognized — you only realize they exist when the AI makes a decision that doesn't match your expectation.

grill-me's approach is to invert this flow: instead of making you think through all the details in advance, it uses questions to **surface** those implicit assumptions one by one, forcing you to take a position on each.

This isn't prompt engineering. It's a more fundamental collaboration pattern: align first, then act.

---

## References

- **mattpocock/skills**: [GitHub](https://github.com/mattpocock/skills) · [skills.sh](https://skills.sh/mattpocock/skills)
- **chaseai-yt/grill-me-codex**: [GitHub](https://github.com/chaseai-yt/grill-me-codex) (788★)
- **Matt Pocock Newsletter**: [aihero.dev/s/skills-newsletter](https://www.aihero.dev/s/skills-newsletter) (60k subscribers)
- **Chase AI Community**: [skool.com/chase-ai](https://www.skool.com/chase-ai/about)

© 2026 Author: Mycelium Protocol
