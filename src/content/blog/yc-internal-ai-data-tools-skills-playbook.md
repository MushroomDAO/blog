---
title: "YC 内部 AI 系统的真相:数据集中 → 工具注册表 → 技能自我进化"
titleEn: "How YC Built Its Internal AI: Data → Tool Registry → Self-Evolving Skills"
description: "YC 内部 AI 系统从 20 个工具长到 350 个,核心不是模型,而是一条有顺序的路径:数据集中、工具注册表、技能自我改进循环。本文拆解这条路径,以及企业与个人各自的三步落地法。"
descriptionEn: "YC's internal AI grew from 20 tools to 350+. The moat isn't the model — it's an ordered path: data centralization, a shared tool registry, and a self-improving skill loop. Here's the teardown, plus a 3-step playbook for orgs and individuals."
pubDate: "2026-06-13"
updatedDate: "2026-06-13"
category: "Research"
tags: ["AI Agent", "Tool Registry", "Skills", "YC", "AI 转型", "工程实践"]
heroImage: "../../assets/banner-org-ai-transformation.jpg"
---

> **一句话结论(BLUF)**:YC 内部那套让 AI 从"会聊天的助手"变成"能干活的同事"的系统,真正的护城河不是模型,而是一条**有先后顺序的路径**——先把数据集中、再建工具注册表、最后跑技能自我改进循环。顺序反了,每一步都会卡死。这条路径企业和个人都能抄,而窗口期就是现在。

最近看到一组关于 YC 内部 AI 系统的拆解,信息量很大。它没有讲什么新模型、新参数,而是讲了一件更朴素也更难的事:**一个组织如何把 AI 真正"接"进自己的业务里**。我把它整理成这篇文章,并补上一些我自己的思考。

## 故事从一次"违规"开始

Pete 和几个工程师搭了一个系统,架构很简单:一个能自动**思考 – 行动 – 再思考**的循环(agent 循环),加上一个共享的**工具池**(工具注册表),让 AI 能调用 YC 内部的业务工具。最初只有 20 个工具,每个只能干一件很窄的事。

然后有个叫 Jared 的工程师,做了一件"违规"的事:他半夜偷偷把一个新工具推了出去——让 AI 可以**直接查 YC 的核心业务数据库**,想查什么查什么,几乎完全开放。

按正常逻辑,这太危险了。核心数据库,让 AI 随便查?

**但效果炸了。**

这里藏着第一个反直觉的洞察。它很像经济学里的**杰文斯悖论**:蒸汽机效率提高,煤的消耗不降反升,因为大家开始用更多蒸汽机。AI 降低了"提问"的成本,结果不是问题变少了,而是大家敢问更多了。当查数据从"找工程师写 SQL、等半天"变成"一句话问 AI",被压抑的需求会瞬间释放。

## 从 20 个工具到 350 个:工具注册表是骨架

AI 能查数据库了,但这只是开始。

Pete 搭的系统里有一个关键组件:**工具注册表**。它的精髓不是"每个人自己搞一套工具",而是**所有人往同一个共享池里加工具**:

- 财务团队加记账工具
- 合伙人加管理咨询时间的工具
- 活动团队加管理活动的工具

就这样,工具从 20 个,长到了 **350 多个**。

工具注册表是整个系统的骨架。它把 AI 从一个"能聊天的助手"变成了"能干活的同事"——因为 AI 能调用的,不再只是通用能力(写文案、翻译、总结),**而是你们团队自己的业务工具**。这是通用 AI 和"你们公司的 AI"之间的分水岭。

## 工具之上还有一层:技能(Skill)

打个比方:**工具是"能做什么",技能是"怎么做最好"。**

- 一个**工具**是:"查一下数据库"
- 一个**技能**是:"帮我分析这批公司的融资趋势"

技能调用工具,把多个步骤串成一个完整的工作流。但技能跟工具最大的区别,**不是复杂度,而是技能能自己进化。**

怎么进化?Pete 搭了一套机制:

1. 每次 AI 做完一件新事,你可以**一键把它固化成技能**;
2. 同时系统会**自动检查**——新技能跟现有的有没有重复、有没有遗漏;
3. 保证同一个功能**只保留一个最优版本**。

这第 3 点很关键:大多数团队的"提示词库""SOP 文档"最后都烂尾,正是因为没有去重和收敛机制,版本越堆越多、越用越乱。技能层自带"垃圾回收",才能持续可用。

## 智能是怎么发生的:一个会自己变聪明的技能

YC 有一个传统:每个创始人都要学会写**"两句话描述"**——用两句话说清楚你的公司做什么、以及为什么有意思。

听起来简单,实际上很难。因为创始人对自己做的事太熟悉了,反而说不清楚。YC 的合伙人要反复教、反复改。

这个技能是怎么变聪明的,值得逐帧看:

1. **第一版**:合伙人 Tom 写了一个技能——把公司的背景信息喂给 AI,让它生成两句话描述。这只是一个**合伙人手写的指令模板**。
2. **采集真实数据**:在一次集体咨询会(office hours)上,其他合伙人让每个创始人都试着写两句话描述,并给了反馈。**这场会议被录了音。**
3. **AI 自我改进**:录音交给了 AI。AI 读了会议录音——里面包含了**多个合伙人多年积累的判断力和教学经验**——然后自动改进了这个技能。

这才是"智能是怎么发生的"的真正答案:**智能不是凭空来的,它是把人类专家散落在对话、会议、决策过程里的隐性经验,沉淀进一个会自我迭代的技能里。** 模型只是引擎,真正的燃料是这些被记录下来的人类判断。

## 路径还原:为什么顺序不能反

你可能在想:YC 有自建系统、有统一数据库、有高信任文化,这些我都没有。怎么办?

好消息是:**你不用照搬 YC 的基础设施,但这条路径的顺序必须照搬。**

### 企业三步走

| 步骤 | 做什么 | 关键点 |
|------|--------|--------|
| ① **数据集中** | 打破各系统之间的数据壁垒,把关键业务数据收到一个地方,并"拍平"让 AI 容易检索 | 哪怕只是一个共享数据库 |
| ② **工具注册表** | 把团队里重复做的事,变成 AI 可调用的工具,放到共享池里 | **从最痛的那个场景开始**(YC 就是从财务团队开始的) |
| ③ **技能自我改进循环** | 在工具之上建技能层,让技能能被 AI 改写和优化,再接入**夜间自我改进**——让 AI 每天读当天所有对话,自动找改进点 | 让系统每天比昨天更聪明一点 |

**顺序很重要:先数据集中,再建工具,再跑自我改进。反过来做,每一步都会卡住。** 没有集中的数据,工具调不到东西;没有稳定的工具,技能就是空中楼阁;没有沉淀的对话,自我改进就没有原材料。

### 个人三步走

这套逻辑同样适用于个人:

1. **数据集中**——笔记、文档、对话,收到一个地方。
2. **记录一切**——会议录音、决策过程、你跟 AI 的对话。这些是你个人的"痕迹",是 AI 帮你迭代的原材料。
3. **从用户变训练师**——把重复做的事变成指令模板,让 AI 帮你复盘。**不是让 AI 帮你做事,是让 AI 越来越懂你怎么做事。**

这第 3 点是整篇最值得划线的句子。绝大多数人用 AI 停留在"帮我做事"(一次性消费),而真正的复利来自"让 AI 越来越懂我"(把自己变成训练师)。

## 为什么窗口期是现在?

现在花 **10 万美元一年**做的事,两年后可能只要**几百块**。但几百块的能力,跟十万美元的能力之间,差的就是**这条路径**——数据有没有集中、工具有没有沉淀、技能有没有在自我进化。

模型会越来越便宜、越来越强,这是确定的。不确定的是:当人人都能用上廉价的强模型时,**你有没有提前把自己的数据、工具、判断力沉淀成一套会自我进化的系统**。这套系统的积累需要时间,而它的窗口期,就是现在。

## 这和 Mycelium 在做的事是一回事

在 Mycelium 生态里,我们一直强调**数字主权**:个人和社区有权掌控自己的数据、身份、资产和表达收益,而不是把它们变成平台的免费资产。

YC 这套路径,本质上是**数字主权在 AI 时代的工程化表达**:

- **数据集中** = 把你的数据握在自己手里,而不是散落在各个平台
- **工具/技能沉淀** = 把你的判断力和经验变成可复用、可进化的个人资产
- **从用户变训练师** = 拒绝做平台的免费数字劳工,让 AI 服务于你自己的复利

这也是为什么我们做 Sin90(个人 OS)和 Cos72(社区 OS)——让普通人和小社区也能跑通这条"数据集中 → 工具 → 技能自进化"的路径,而不必拥有 YC 那样的基础设施。

## 常见问题(FAQ)

**Q1:小团队没有工程师,搭不起 agent 循环和工具注册表怎么办?**
不用一开始就搭完整系统。先做第一步——把数据集中到一个共享文档/数据库;再把一两个最高频的重复任务,写成 AI 能复用的指令模板(这就是最简版的"工具")。重点是顺序对,不是规模大。

**Q2:为什么不能先建工具、再补数据?**
因为工具调用的是数据。数据没集中、没拍平,工具要么调不到、要么调得乱,反而会让团队对 AI 失去信任。YC 的经验是:数据集中是地基,地基没打就盖楼,每一步都返工。

**Q3:"技能自我进化"会不会失控?**
关键在那套**去重 + 遗漏检查**机制:同一功能只保留一个最优版本,新技能上线前自动比对现有技能。再加上"夜间自我改进"是基于真实对话日志找改进点,而非凭空生成。有收敛机制的进化,才是可控的进化。

**Q4:个人最该从哪一步开始?**
从"记录一切"开始。大多数人卡在没有原材料——会议、决策、和 AI 的对话过完就丢了。先把痕迹留下来,数据集中和"变训练师"才有东西可用。

---

> 📌 内容来源:基于一组关于 YC 内部 AI 系统的公开拆解整理,并补充作者分析。小红书号:263480904。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用,须注明作者姓名及原文链接,不得去除署名后以原创发布。

<!--EN-->

> **Bottom line up front (BLUF):** The system that turned YC's internal AI from a "chat assistant" into a "colleague that gets work done" has no secret model. The real moat is an **ordered path**: centralize data first, then build a shared tool registry, then run a self-improving skill loop. Reverse the order and every step jams. Both companies and individuals can copy this path — and the window is right now.

I recently came across a teardown of YC's internal AI system. What struck me wasn't any new model or parameter count — it was something more mundane and far harder: **how an organization actually wires AI into its own business.** Here's the breakdown, with some of my own analysis added.

## It started with a rule-breaking move

Pete and a few engineers built a system with a simple architecture: an automatic **think–act–rethink** loop (an agent loop), plus a shared **tool pool** (a tool registry) that let the AI call YC's internal business tools. It started with just 20 tools, each doing one narrow thing.

Then an engineer named Jared did something "against the rules": late one night he quietly shipped a new tool — one that let the AI **query YC's core business database directly**, almost completely open, ask anything.

By normal logic, this was way too dangerous. The core database, open to AI queries?

**But the results were explosive.**

There's a counterintuitive insight hidden here, much like the **Jevons paradox** in economics: when steam engines got more efficient, coal consumption *rose* rather than fell, because people started using far more steam engines. AI lowered the cost of *asking* — and the result wasn't fewer questions, but people daring to ask many more. When querying data goes from "find an engineer, write SQL, wait half a day" to "ask the AI in one sentence," suppressed demand is released instantly.

## From 20 tools to 350: the registry is the skeleton

The AI could query the database — but that was just the start.

A key component of Pete's system was the **tool registry**. Its essence isn't "everyone builds their own tools"; it's that **everyone adds tools to one shared pool**:

- The finance team adds bookkeeping tools
- Partners add tools for managing advising time
- The events team adds event-management tools

That's how the tool count grew from 20 to **over 350**.

The tool registry is the skeleton of the whole system. It turned the AI from a "chat assistant" into a "colleague that does work" — because what the AI could call was no longer just general capabilities (copywriting, translation, summarizing), but **your team's own business tools**. That's the dividing line between generic AI and *your company's* AI.

## Above tools sits another layer: Skills

An analogy: **a tool is "what can be done"; a skill is "how to do it best."**

- A **tool**: "query the database"
- A **skill**: "analyze the financing trends across this batch of companies"

A skill calls tools, chaining multiple steps into a complete workflow. But the biggest difference between a skill and a tool **isn't complexity — it's that skills can evolve themselves.**

How? Pete built a mechanism:

1. Every time the AI completes something new, you can **solidify it into a skill with one click**;
2. The system **automatically checks** whether the new skill duplicates existing ones or leaves gaps;
3. It ensures each function keeps **only one optimal version**.

Point 3 is critical: most teams' "prompt libraries" and "SOP docs" eventually rot precisely because they lack a dedup-and-converge mechanism — versions pile up and grow unusable. A skill layer with built-in "garbage collection" is what stays usable over time.

## How intelligence actually happens: a skill that gets smarter on its own

YC has a tradition: every founder must learn to write a **"two-sentence description"** — explaining in two sentences what your company does and why it's interesting.

Sounds simple; it's actually hard. Founders are too close to their own work to explain it clearly. YC partners teach and revise it again and again.

How this skill got smarter is worth watching frame by frame:

1. **Version 1**: Partner Tom wrote a skill — feed company background to the AI, have it generate a two-sentence description. This was just a **partner's hand-written instruction template.**
2. **Capturing real data**: At a group office-hours session, other partners had each founder try writing a two-sentence description and gave feedback. **The session was recorded.**
3. **AI self-improvement**: The recording was handed to the AI. The AI read it — containing **years of accumulated judgment and teaching experience from multiple partners** — and automatically improved the skill.

This is the real answer to "how intelligence happens": **intelligence doesn't come from nowhere. It comes from distilling the tacit expertise scattered across conversations, meetings, and decisions into a skill that iterates on itself.** The model is just the engine; the real fuel is recorded human judgment.

## Reconstructing the path: why order can't be reversed

You might be thinking: YC has a custom system, a unified database, a high-trust culture — I have none of that. So what?

Good news: **you don't need to copy YC's infrastructure, but you must copy the order of this path.**

### The 3-step playbook for organizations

| Step | What to do | Key point |
|------|-----------|-----------|
| ① **Centralize data** | Break the silos between systems, gather key business data in one place, and "flatten" it so the AI can search it easily | Even just a shared database counts |
| ② **Tool registry** | Turn the team's repetitive work into AI-callable tools in a shared pool | **Start from the most painful scenario** (YC started with the finance team) |
| ③ **Self-improving skill loop** | Build a skill layer atop the tools, let skills be rewritten and optimized by AI, then add **nightly self-improvement** — have the AI read every conversation from that day and find improvement points | Make the system a little smarter every day |

**Order matters: centralize data first, then build tools, then run self-improvement. Reverse it and every step jams.** Without centralized data, tools have nothing to call; without stable tools, skills are castles in the air; without recorded conversations, self-improvement has no raw material.

### The 3-step playbook for individuals

The same logic applies to individuals:

1. **Centralize data** — notes, docs, conversations, all in one place.
2. **Record everything** — meeting recordings, decision processes, your conversations with AI. These are your personal "traces," the raw material for AI to iterate on your behalf.
3. **Go from user to trainer** — turn repetitive work into instruction templates and have the AI help you review. **It's not about letting AI do things for you; it's about letting AI increasingly understand how *you* do things.**

Point 3 is the most underline-worthy sentence in the whole piece. Most people stop at "AI, do this for me" (one-off consumption). The real compounding comes from "make AI understand me better and better" — turning yourself into a trainer.

## Why the window is now

What costs **$100,000 a year** to do today might cost **a few hundred dollars** in two years. But the gap between the few-hundred-dollar capability and the $100k capability *is exactly this path* — whether your data is centralized, your tools are accumulated, your skills are self-evolving.

Models will keep getting cheaper and stronger; that's certain. What's uncertain is this: when everyone can access cheap, powerful models, **have you already distilled your data, tools, and judgment into a self-evolving system?** That accumulation takes time — and the window for it is right now.

## This is the same thing Mycelium is building

In the Mycelium ecosystem, we keep emphasizing **digital sovereignty**: individuals and communities have the right to control their own data, identity, assets, and the rewards from their expression — rather than turning them into a platform's free assets.

YC's path is essentially **digital sovereignty expressed as engineering in the AI era**:

- **Centralize data** = keep your data in your own hands, not scattered across platforms
- **Distill tools/skills** = turn your judgment and experience into reusable, evolving personal assets
- **From user to trainer** = refuse to be a platform's free digital laborer; make AI compound *your* own value

This is exactly why we build Sin90 (a personal OS) and Cos72 (a community OS) — so ordinary people and small communities can run this "centralize data → tools → self-evolving skills" path too, without needing YC-grade infrastructure.

## FAQ

**Q1: My small team has no engineers — we can't build an agent loop or tool registry. What now?**
You don't need the full system up front. Do step one — centralize your data into a shared doc/database. Then turn one or two of your highest-frequency repetitive tasks into reusable instruction templates (the simplest form of a "tool"). What matters is getting the order right, not the scale.

**Q2: Why can't I build tools first and backfill the data later?**
Because tools call data. If data isn't centralized and flattened, tools either can't reach it or reach it messily — which erodes the team's trust in AI. YC's lesson: centralized data is the foundation; build on no foundation and every step requires rework.

**Q3: Won't "self-evolving skills" spiral out of control?**
The key is the **dedup + gap-check** mechanism: each function keeps only one optimal version, and new skills are auto-compared against existing ones before going live. Plus, "nightly self-improvement" finds improvement points from real conversation logs, not from thin air. Evolution with a convergence mechanism is controllable evolution.

**Q4: Where should an individual start?**
Start with "record everything." Most people are stuck for lack of raw material — meetings, decisions, and AI conversations vanish the moment they're over. Capture the traces first; only then do centralization and "becoming a trainer" have something to work with.

---

> 📌 Source: Compiled from a public teardown of YC's internal AI system, with the author's analysis added. Xiaohongshu ID: 263480904.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
