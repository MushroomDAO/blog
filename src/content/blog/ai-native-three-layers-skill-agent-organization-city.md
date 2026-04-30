---
title: "AI Native 的三个层级：个人、组织与区域"
titleEn: "Three Layers of AI-Native Transformation: Individual, Organization, and Region"
description: "AI Native 不是一个状态，而是一个过程。从个体用 Skill 获得新能力，到 Agent 完成任务级自主，再到组织的结构性变革，最终到区域/城市协作操作系统——每一层的跨越都比上一层复杂一个数量级。借鉴 Anthropic Cat Wu 的实践案例，结合 Mycelium Protocol 的视角，梳理这三层演进的逻辑。"
descriptionEn: "AI-native is not a state — it's a process. From individuals gaining new capabilities via Skills, to Agent-level task autonomy, to organizational structural rewiring, and finally to a regional/city coordination OS — each layer is an order of magnitude more complex than the last. Drawing on Anthropic Cat Wu's practice and the Mycelium Protocol perspective, this post traces the logic of all three layers."
pubDate: "2026-04-30"
updatedDate: "2026-04-30"
category: "Research"
tags: ["AI Native", "Agent", "组织变革", "Mycelium", "Research", "Product Thinking", "Cat Wu", "Anthropic"]
heroImage: "../../assets/banner-human-ai-coexistence.jpg"
---

> **创作说明**：本文为 Jason（Mycelium Protocol 创始人）与 AI（Claude）对话讨论后，由 AI 按 Jason 的意图整理输出的原创文章。Anthropic / Cat Wu 的播客内容作为参考案例引用，核心框架和观点为 Jason 原创。
>
> **转载注明**：Anthropic 案例来源 — Lenny's Podcast [How Anthropic's product team moves faster than anyone else](https://www.lennysnewsletter.com/p/how-anthropics-product-team-moves) · [YouTube](https://www.youtube.com/watch?v=PplmzlgE0kg) · [Twitter](https://x.com/lennysan/status/2047377335406694431) · Cat Wu [@_catwu](https://x.com/_catwu)

---

## 一句话先说清楚

AI Native 的演进有三个层级：**个人（Skill → Agent）→ 组织（结构性变革）→ 区域/城市（协作操作系统）**。每一层的跨越，都比上一层复杂一个数量级，也意味着更大的阻力和更深的重组。

---

## 第一层：个人 — 从碎片 Skill 到任务级 Agent

### 1.1 Skill：AI 赋予个体原来没有的能力

AI 应用的起点，是碎片化的工具使用。

用 ChatGPT 翻译一段文字，用 Stable Diffusion 生成一张图，用豆包写一封邮件——这些用法的本质是**工具调用**，本质上还是人主导、AI 辅助。但不要低估这一步的价值。

举个具体的例子：家里下水道堵了，你描述了管道格局、以前的问题、现在的症状，AI 能给出像水暖专家一样的判断和建议。这件事在 AI 出现之前，你要么自己懂、要么花钱找专家。现在这个"咨询专家"的成本趋近于零。

这就是 Skill 的本质：**AI 把大量原来需要专业知识才能完成的判断，变成了普通人可以独立完成的操作**。

在很多领域，AI Skill 能大幅提升用户的数字生活质量——医疗判断、法律咨询、代码调试、财务规划——不是让你变成这些领域的专家，而是让你在这些领域不再完全无能为力。

但 Skill 有一个根本的局限：**它是被动的、碎片化的**。你问一个问题，AI 给一个答案。任务完成的连续性、上下文的积累、工具的调用——都还在你这边。

### 1.2 Agent：上下文 + 工具调用 + 闭环任务

AI 真正的能力释放，发生在第二步：**Agent**。

Agent 的本质不是 AI 更聪明了，而是 AI 获得了**上下文**（知道你做过什么、你在干什么、你要去哪里）和**工具**（能搜索、能写文件、能生成图片、能调用 API、能发布内容）。

还是写文章这个例子。碎片化用 AI：你问一个大纲，再问一段内容，再问一个结尾——每次都要重新给上下文，每次都要手动拼接。而 Agent 模式下：你给出一个任务目标，AI 自己思考拆解、搜索论据、生成图片、检查排版、发布内容——你要做的事情是界定任务范围和验收结果，而不是参与每一个环节。

这个变化有一个很重要的词：**自主性（Autonomy）**。

Agent 不是"更好的搜索框"，它是第一次让 AI 成为任务的主体，而不是工具。很多人把管理 Agent 的框架叫 **Harness**（驾驭框架）——包括任务分解、工具注册、上下文管理、结果验收的整套机制。Harness 的质量，决定了 Agent 能跑多远、跑多稳。

**个人层级的总结**：从 Skill 到 Agent，是从"AI 赋能操作"到"AI 完成任务"的跨越。两步的技术栈都在快速成熟，但真正懂得如何驾驭 Agent 的人，目前还是少数。

---

## 第二层：组织 — 不只是工具升级，而是结构性变革

### 2.1 Anthropic 案例：一个最极端的 AI-native 组织长什么样

Anthropic 的 Cat Wu（CPO）在播客里分享了一个细节，值得细品：**以前一个功能可能要做 6 个月，现在可能 1 个月、1 周，甚至有时候 1 天就能跑出来。**

这种速度不只是因为 AI 写代码更快。更根本的原因是他们改造了组织结构和工作流程，让整个机器适配了 AI 产品的节奏。

Cat Wu 提到了三个核心变化：

**变化一：PRD 不再是唯一的对齐方式**

传统的对齐依赖 PRD——写需求文档、做排期、拉齐团队。Anthropic 用两套机制替代了它：
- **每周全团队指标解读会**：所有人都看同一套数字，理解业务进展，不只是 PM 和管理层知道目标
- **团队原则清单**：明确写清楚核心用户是谁、为什么是这群人、团队愿意做出哪些取舍

这两件事做到位之后，工程师可以自己判断一个问题到底重不重要，不需要每次都等需求下来。**真正被压缩掉的，不是沟通本身，而是反复确认的成本。**

**变化二：发布链路压缩到日常动作**

很多公司发布功能，默认要做成"正式版"。Anthropic 很多功能以 **research preview** 的方式发布——先让产品进入真实世界，再用真实反馈修正方向。

发布的机制也很具体：工程师觉得功能 ready，内部试用过，直接发到固定发布群，文档、市场、开发者关系同步跟上，第二天对外公告就出来了。**发布不再是大项目，而是固定动作。**

**变化三：产品品味（Product Taste）成为稀缺能力**

这是整个访谈里我觉得最值得反复咀嚼的洞察。

Cat Wu 说：代码越来越容易被 AI 写出来，真正稀缺的不再是"谁会写代码"，而是"**谁知道该写什么**"。

- 谁能判断什么体验是好的？
- 谁能看出用户真正需要什么？
- 面对成千上万个 GitHub issue，谁能找到最值得做的那个点？

这种能力她叫 **product taste（产品品味）**。它不一定来自 PM——工程师可以有，设计师可以有，任何真正理解用户和产品的人都可以有。Anthropic 的招聘偏好因此很直接：**有产品直觉的工程师**，因为这种人可以端到端交付，几乎不需要中间层。

### 2.2 组织 AI-native 的三个层面变革

结合 Anthropic 案例，组织要真正 AI-native，至少要经历三个层面的变革：

**① 工作流程围绕 AI 能力重组**

不是在原有流程里插入 AI 工具，而是从头问：如果 AI 能完成这个步骤，这个步骤还需要存在吗？这个环节的角色还需要是人吗？流程的对齐点在哪里？

**② 岗位角色边界模糊，核心能力定义重写**

AI-native 团队要的不是只守岗位边界的人，而是能**跨边界解决问题**的人。PM 不能只做流程中转站，工程师不能只等需求，设计师不能只交付设计稿。

Cat Wu 认为，面对这种角色边界不断模糊的环境，最重要的元能力是**第一性原理思维**——看清楚技术正在怎么变化，判断团队现在最需要什么，然后迅速补上那个空缺。

**③ 专为 AI 工作流设计的工具和协作机制**

Anthropic 的例子是：固定发布协作群、研究型 PM 专门负责把用户反馈传递给模型团队、发布节奏从大项目变成固定动作。

这些工具和机制不是通用的，是为这个特定组织的 AI 工作流专门设计的。**组织 AI-native 的过程，本质上是在重新设计协作的基础设施。**

### 2.3 Anthropic 的 PM 团队结构：围绕 AI 产品链路分工

传统公司按功能模块配 PM（"一个产品配一个 PM"）。Anthropic 有 30-40 个 PM，但按 **AI 产品链路**来分工：

| PM 类型 | 职责 |
|---------|------|
| 研究型 PM | 收集用户对模型的反馈 → 传递给研究团队 → 推动模型发布 |
| 平台型 PM（Claude Developer Platform） | 底层 API 和开发者平台能力 |
| 产品型 PM（Claude Code / Cowork） | 代码场景和知识工作场景 |
| Enterprise PM | 成本控制、权限管理、安全管控 |
| 增长 PM | 推动整个产品线增长 |

整个链路：**用户反馈 → 模型能力 → 平台 → 产品 → 企业采用 → 增长**——这才是 AI 公司的产品链，而不是传统的功能模块切分。

---

## 第三层：区域/城市 — 协作操作系统

组织层的变革已经很困难了。但如果我们把视野再拉大一层——**区域或城市**呢？

一个城市，或者一个区域的多个社区、多家小型组织，要协同完成一些比任何单一组织都大的事情（比如社区资源分配、地方经济循环、公共服务优化），能不能也走向 AI-native？

这个问题在 Mycelium Protocol 的视角下变得具体。

城市层的 AI-native 不是给市政府上一套 AI 系统。更可能的路径是：**以协议为基础设施，以社区为节点，让去中心化的协作通过 AI 变得高效**。

三层类比：

| 层级 | 主体 | AI 的角色 | 核心挑战 |
|------|------|-----------|----------|
| 个人 | 个体 | Skill / Agent 赋能 | 学习成本、信任建立 |
| 组织 | 团队/公司 | 工作流重组 + 能力重定义 | 组织惯性、文化阻力 |
| 区域/城市 | 多组织/社区 | 协调协议 + 意义网络 | 去中心化治理 + 激励对齐 |

城市层面的 AI-native，需要解决一个组织层不需要面对的问题：**谁是决策主体？谁来设定原则清单？谁来维护协作基础设施？**

在 Anthropic 这样有明确所有权的组织里，Cat Wu 可以拍板说"原则清单长这样"。但在一个由 50 个独立咖啡馆、小旅馆、街边摊构成的社区里，没有人有这个权力。

这是为什么 Mycelium Protocol 把重点放在**协议层**而不是**平台层**：协议是共识，不是管控。AI 在这一层的作用，不是替代决策者，而是**降低多主体协调的成本**，让更多人能参与到有意义的协作中。

---

## 几个值得反复思考的点

**1. AI-native 不是工具问题，是组织问题**

大多数人把 AI-native 当成"用 AI 工具"的问题来处理，但真正的难点不在工具。工具很容易换，组织的惯性很难改。Anthropic 的速度优势，来自他们把对齐方式、发布节奏、角色定义都重新设计了一遍——这不是一个工具决策，是一个组织设计决策。

**2. "谁知道该写什么"比"谁会写代码"更稀缺**

这个洞察对个人职业路径的影响非常深远。当 AI 能写大多数代码，真正有价值的是判断力——什么值得做、对谁有用、做到什么程度。这种判断力的培养，比学一门编程语言慢得多，也无法被 AI 直接替代。

**3. 每一层跨越都需要新的基础设施**

从 Skill 到 Agent，需要 Harness（任务框架）。从个体 Agent 到组织 AI-native，需要协作机制的重设计。从组织到区域，需要去中心化协议。基础设施先于应用，这是每次技术革命的共同规律。

**4. AI-native 是一个过程，不是一个标签**

没有任何组织、城市或个人是"已经 AI-native 了"。更准确的说法是：**你在这个转变过程中的哪个位置**，以及你是主动驾驭这个变化，还是被动适应它。

---

<!--EN-->

> **About this article**: Original work by Jason (Mycelium Protocol founder), developed through discussion with AI (Claude) and organized by AI per Jason's intent. The three-layer framework and all analysis are Jason's original thinking. The Anthropic / Cat Wu content is cited as a reference case.
>
> **Citation**: Anthropic case source — Lenny's Podcast [How Anthropic's product team moves faster than anyone else](https://www.lennysnewsletter.com/p/how-anthropics-product-team-moves) · [YouTube](https://www.youtube.com/watch?v=PplmzlgE0kg) · [Twitter](https://x.com/lennysan/status/2047377335406694431) · Cat Wu [@_catwu](https://x.com/_catwu)

---

## The Short Version

AI-native transformation happens at three layers: **Individual (Skill → Agent) → Organization (structural rewiring) → Region/City (coordination OS)**. Each layer is an order of magnitude more complex than the last, and requires rebuilding the underlying infrastructure before the application layer can emerge.

---

## Layer 1: Individual — From Fragmented Skills to Task-Level Agents

### 1.1 Skill: AI Gives Individuals Capabilities They Didn't Have Before

The entry point for AI adoption is fragmented tool use. Using ChatGPT to translate, Stable Diffusion to generate an image, a chatbot to draft an email — these are fundamentally **tool calls** where humans still direct and AI assists. But don't underestimate this step.

Concrete example: your home plumbing is broken. You describe the pipe layout, past issues, current symptoms to an AI. It gives you a diagnosis like a plumbing expert would. Before AI, this required either personal expertise or paying a professional. Now the "consult an expert" cost approaches zero.

That's the essence of Skill: **AI turns large categories of judgment that used to require professional knowledge into operations ordinary people can execute independently.** Medical triage, legal questions, code debugging, financial planning — not making you an expert, but making you no longer completely helpless.

The fundamental limitation of Skill: **it's passive and fragmented.** You ask a question, AI answers. Task continuity, context accumulation, tool invocation — all still on your side.

### 1.2 Agent: Context + Tool Calls + Closed-Loop Task Completion

AI's real capability release happens at the second step: **Agent**.

The essence of Agent isn't that AI is smarter — it's that AI now has **context** (knows what you've done, what you're doing, where you're going) and **tools** (can search, write files, generate images, call APIs, publish content).

Writing an article: fragmented AI use means asking for an outline, then a paragraph, then a conclusion — each time re-establishing context, manually assembling pieces. Agent mode: you specify a task goal, AI breaks it down, searches for evidence, generates images, checks formatting, publishes content — your role is to define scope and validate output, not participate in every step.

The key word: **Autonomy**. Agent is the first time AI becomes the subject of a task rather than a tool. The framework for managing Agents is called a **Harness** — task decomposition, tool registration, context management, output validation. The quality of your Harness determines how far and how reliably your Agent can run.

**Individual layer summary**: From Skill to Agent is the leap from "AI enables operations" to "AI completes tasks." Both technical stacks are maturing fast. But those who genuinely know how to harness Agents are still rare.

---

## Layer 2: Organization — Not Tool Upgrade, But Structural Rewiring

### 2.1 The Anthropic Case: What an Extreme AI-Native Organization Looks Like

Anthropic CPO Cat Wu shared a detail worth dwelling on: **a feature that used to take 6 months now might take a month, a week, sometimes a day.**

This speed isn't just because AI writes code faster. The deeper reason is they rewired their organizational structure and workflows to fit the pace of AI product development.

Three core changes Cat Wu identified:

**Change 1: PRD is No Longer the Only Alignment Mechanism**

Traditional alignment relies on PRDs — requirements documents, scheduling, team sync-ups. Anthropic replaced this with two mechanisms:
- **Weekly all-team metrics review**: everyone reads the same numbers, understands business progress — not just PM and leadership
- **Team principles document**: clearly states who the core users are, why, and what tradeoffs the team is willing to make

With these two in place, engineers can judge whether a problem matters without waiting for requirements to come down. **What's compressed isn't communication itself — it's the cost of repeated confirmation.**

**Change 2: Release Pipeline Compressed to a Routine Action**

Most companies default to making a "proper release" out of every feature. Anthropic releases many features as **research previews** — ship to the real world first, correct course with real feedback.

The mechanics: when an engineer thinks a feature is ready and has been internally tested, it goes to a fixed release coordination channel. Documentation, product marketing, and developer relations follow immediately. The public announcement can be out the next day. **Release is no longer a big project — it's a fixed playbook.**

**Change 3: Product Taste Becomes the Scarce Resource**

This is the insight from the interview I keep coming back to.

Cat Wu said: as code becomes cheaper to write, what's truly scarce isn't "who can write code" — it's "**who knows what to write**."

- Who can judge what makes a good experience?
- Who can identify what users actually need?
- Facing thousands of GitHub issues, who can find the one thing most worth doing?

She calls this **product taste**. It doesn't only come from PMs — engineers can have it, designers can have it, anyone who genuinely understands users and products can have it. Anthropic's hiring preference follows directly: **engineers with product instinct**, because those people can deliver end-to-end with almost no intermediary layer.

### 2.2 Three Dimensions of Organizational AI-Native Transformation

**① Workflows reorganized around AI capabilities**

Not inserting AI tools into existing processes. Starting from first principles: if AI can do this step, does this step still need to exist? Does this role still need to be human? Where are the alignment points?

**② Role boundaries blur; core capability definitions rewritten**

AI-native teams need people who can **solve problems across boundaries**, not people who defend their lane. PMs can't just be process relay stations, engineers can't just wait for requirements, designers can't just deliver mockups.

Cat Wu's view on the meta-capability that matters most in this environment: **first-principles thinking** — seeing clearly how technology is changing, judging what the team needs most right now, and rapidly filling that gap.

**③ Purpose-built tools and collaboration mechanisms for AI workflows**

Fixed release coordination channels, research PMs dedicated to routing user feedback to the model team, shipping cadence reshaped from projects into routines. These aren't generic tools — they're purpose-built for this specific organization's AI workflows. **The process of organizational AI-native transformation is fundamentally a redesign of collaboration infrastructure.**

### 2.3 Anthropic's PM Structure: Organized Around the AI Product Chain

Traditional companies assign PMs per product module. Anthropic's 30–40 PMs are organized around the **AI product chain**:

| PM Type | Responsibility |
|---------|---------------|
| Research PM | Collect user feedback on model → route to research team → drive model releases |
| Platform PM (Claude Developer Platform) | Foundational API and developer platform capabilities |
| Product PM (Claude Code / Cowork) | Coding and knowledge-work use cases |
| Enterprise PM | Cost controls, permissions, security governance |
| Growth PM | Drive growth across the entire product line |

The full chain: **user feedback → model capability → platform → product → enterprise adoption → growth** — this is the AI company's product chain, not traditional feature-module slicing.

---

## Layer 3: Region/City — A Coordination Operating System

Organizational transformation is already hard. But what if we zoom out one more layer — to a **region or city**?

Can multiple communities, dozens of small independent organizations, coordinate on things larger than any single organization can tackle (local resource allocation, economic circulation, public service optimization) and also move toward AI-native?

From the Mycelium Protocol perspective, this question becomes concrete.

City-layer AI-native isn't about giving a city government an AI system. The more likely path: **using protocol as infrastructure, with communities as nodes, making decentralized coordination efficient through AI**.

| Layer | Primary Actor | AI's Role | Core Challenge |
|-------|--------------|-----------|----------------|
| Individual | Person | Skill / Agent empowerment | Learning curve, trust |
| Organization | Team / Company | Workflow redesign + capability redefinition | Organizational inertia, cultural resistance |
| Region / City | Multi-org / Community | Coordination protocol + meaning network | Decentralized governance + incentive alignment |

The city layer faces a problem organizations don't: **who is the decision-making subject? Who sets the principles document? Who maintains the collaboration infrastructure?**

At Anthropic, Cat Wu can set the principles document. In a community of 50 independent cafes, guesthouses, and street vendors, no one has that authority.

This is why Mycelium Protocol focuses on the **protocol layer** rather than the **platform layer**: protocol is consensus, not control. AI's role here isn't to replace decision-makers — it's to **reduce the cost of multi-party coordination**, letting more people participate in meaningful collaboration.

---

## Four Points Worth Returning To

**1. AI-native is an organization problem, not a tool problem**

Most people approach AI-native as a question of which tools to use. The real difficulty isn't the tools — tools are easy to swap. Organizational inertia is hard to change. Anthropic's speed advantage comes from redesigning alignment mechanisms, release cadence, and role definitions from scratch. That's an organizational design decision, not a tool selection decision.

**2. "Who knows what to write" is scarcer than "who can write code"**

This insight has profound implications for individual career paths. When AI can write most code, what's valuable is judgment — what's worth building, for whom, to what degree. That judgment takes far longer to develop than learning a programming language, and cannot be directly replaced by AI.

**3. Each layer transition requires new infrastructure**

Skill to Agent requires Harness. Individual Agents to organizational AI-native requires collaboration infrastructure redesign. Organization to region requires decentralized protocol. Infrastructure before applications — this is the common pattern of every technological revolution.

**4. AI-native is a process, not a label**

No organization, city, or individual is "already AI-native." The more accurate framing: **where are you in this transition**, and are you actively steering it or passively adapting to it?
