---
title: "Replit 的 13 个月：从差点死掉到 2.53 亿，创业底层逻辑"
titleEn: "Replit's 13 Months: From Near-Death to $253M ARR — The Real Story Behind the 'Lucky' AI Boom"
description: "2024年5月，Replit几乎被放弃。同年9月Agent上线，13个月后年收入2.53亿美元，增长2352%。很多人说这是赶上了AI风口。但扒开细节你会发现，Replit的爆发根本不是运气——而是8年打基础后，时代终于追上了它。"
descriptionEn: "In May 2024, Replit was nearly abandoned. Four months later, the Agent launched. 13 months after that: $253M ARR, 2352% growth. Many call it lucky timing. The real story is 8 years of infrastructure waiting for the AI moment to arrive."
pubDate: 2026-06-04
category: "Tech-News"
tags: ["Replit", "创业", "AI Agent", "Amjad Masad", "创业故事", "商业", "长期主义", "基础设施"]
heroImage: "../../assets/images/replit-amjad-masad-founder-banner.jpg"
lang: "zh-CN"
---

## 2024 年 5 月，差点死掉

那时候的 Replit，账面上有两千多万用户，但年收入只有 280 万美元。

用户多，但几乎没人付钱。公司造了一个免费的浏览器编程环境，全球几千万学生、爱好者、入门开发者拿去用，却根本养不活团队。这是 SaaS 创业里最经典的陷阱：**用户规模和商业价值完全脱节**。

那一年，硅谷有很多对话在讨论 Replit 还能撑多久。

四个月后，2024 年 9 月，他们上线了一个叫 **Agent** 的东西。

你用大白话描述一句想做什么，它自己配环境、装依赖、写代码，最后直接给你一个能打开的网址。

接下来的数字有点不讲道理：收入从 1000 万，**13 个月干到 2.53 亿美元，同比增长 2352%**。2026 年 3 月，公司估值 90 亿美元。

很多人看到这会说：运气好，赶上 AI 风口了呗。

这个解释不是错的。但它遗漏了最关键的部分。

---

## 从约旦到浏览器——一个关于"入口"的执念

创始人 **Amjad Masad** 1987 年生于约旦安曼，从小家里没有电脑。

他是靠着学校机房的电脑接触编程的。那种感觉他后来反复提起：**编程是一种权力，但这种权力被"你得先有台电脑、先装好环境"这道门槛挡在外面**。

2011 年，他在 Codecademy 做工程师时，做了一个东西叫 **JSRepl**——一个完全在浏览器里运行 JavaScript 的工具，给 Codecademy 和 Udacity 的在线课程用。不需要本地安装任何东西，打开网页就能跑代码。

这个"零配置、浏览器即环境"的执念，从此没有变过。

2016 年，他和妻子 Haya Odeh、兄弟 Faris Masad 一起正式创立 Replit。使命只有一句话：**让任何地方的任何人都能编程**。

---

## 8 年建了 5 块积木

Replit 从 2016 年到 2024 年的历史，如果只看用户增长和融资记录，看起来像一家"慢热型"公司。但换个角度看，你会发现它每一年都在往同一个方向添砖。

### 2016：浏览器 IDE

最核心的那块积木。不是编辑器里加了个浏览器插件，而是把整个开发环境搬进了浏览器——多语言支持、即时运行、代码分享链接。年底拿到 75 万用户，主要是学生和教师。

### 2018：进 YC（第四次申请）

前三次申请 Y Combinator 全被拒绝。第四次终于进去了。那一年，他们做的最重要的事是**把多人实时协作写进了 IDE**——最多 4 个人同时编辑同一份代码，能看到彼此的光标，像 Google Docs 一样。

### 2020：COVID 让用户破千万

疫情让线上教育爆炸，Replit 的用户从百万级跳到千万级。但更重要的是这段时间做的基础建设：**定制容器化沙盒**，让每个用户的代码在安全隔离的环境里运行——这是后来 Agent 能自动配环境的前提。

### 2022：Ghostwriter，第一次把 AI 塞进编辑器

2022 年 4 月，Replit 上线 Ghostwriter——AI 代码补全、生成、解释、调试，集成在 IDE 里。当时市场上没太多人注意，大家觉得这只是 GitHub Copilot 的平替版。

但 Ghostwriter 做了一件别人没做的事：它的 AI 助手不是一个独立工具，而是 **跑在已经有沙盒、有部署能力的平台里**。AI 写的代码，当场就能运行。

### 2023：彻底重写部署系统

2023 年，Replit 拿到 9740 万美元的 B 轮融资，估值 11.6 亿美元。这笔钱没有用来扩招，主要用来重写了**上线系统（Deployments）**——一键从代码到可访问的线上地址，包含 SSL、域名、CDN、自动扩容。

这块积木很关键，但当时看不出来。

---

## 2024 年 9 月：所有积木一夜咬合

Agent 的核心功能是：

1. 接受自然语言 brief
2. 理解你想做什么
3. 自动配置运行环境
4. 写出全套代码
5. 部署，给你一个可以打开的网址

翻译一下，这五步对应的是什么：

| Agent 的能力 | Replit 早已建好的系统 |
|------------|---------------------|
| 自动配置环境 | 2016 年就有的浏览器 IDE + 2020 年的容器化沙盒 |
| 写代码 | 2022 年的 Ghostwriter AI 引擎 |
| 实时协作修改 | 2018 年的多人编辑机制 |
| 一键部署上线 | 2023 年重写的 Deployments 系统 |
| 给你一个可打开的网址 | 2023 年的域名 + SSL + CDN 全套 |

**别人 2024 年从零做 Agent，得先把这五个系统搭出来，才能跑出第一句话。Replit 只是给已经在跑着的系统，装了一个嘴。**

Agent 在第一天就能跑通，不是因为运气，是因为五个前置条件全部提前 8 年建好了。

---

## 变现模型的切换

Agent 上线同时，Replit 把定价模型从"订阅制"改成了**按使用量付费**：

- Replit Core 月费 20 美元，包含一定的 Agent 使用额度
- 超出额度按计算量收费
- 企业版自定义定价

这个转变非常关键。之前的问题是：学生用免费账户，不付钱。付费用户愿意付的金额有限。

Agent 改变了价值感知：**你给了我一句话，它帮我建了一个能用的 App，这值 20 美元，可能值更多**。同时，对企业用户来说，用 Agent 自动化内部工具开发的价值，远不止月费。

收入从 280 万 → 1 亿 → 2.53 亿，用了大约 18 个月。

---

## 提炼：这件事真正反直觉的地方

### 1. 坚持的前提是方向对

Replit 撑过了 YC 三次拒绝、用户增长但不赚钱的几年、硅谷对"在线 IDE"这个方向的长期质疑。但它坚持的方向从 2011 年 JSRepl 到 2024 年 Agent，本质没变过：**让编程的门槛消失**。

盲目坚持是固执。在正确方向上坚持，是护城河在慢慢变深。

### 2. 基础设施的价值在危机前看不见

浏览器 IDE、容器沙盒、多人协作、一键部署——这些东西在 2016、2018、2020、2023 年分别完成时，每次都有人问"这个有什么用？谁会在浏览器里写代码？"。

答案是：AI Agent 需要的时候，全都有用。

基础设施的回报不是线性的，是阶跃式的。当某个临界条件被触发（这里是 LLM 能力达到阈值），所有积累同时变现。

### 3. 使命是撑过"看起来没用"阶段的唯一燃料

Amjad 在约旦没有电脑的童年，塑造了他对"编程门槛"的真实愤怒。这种愤怒让他能在用户多但不赚钱的年代继续建基础设施，而不是转型做更容易变现的东西。

使命感不是 PPT 上的句子，是创始人在最难的季度里，解释为什么继续干的理由。

### 4. 市场"风口"只给那些早就准备好的人

AI 编程工具的爆发是 2023-2024 年的事。但 Replit 的基础设施是 2016-2023 年建好的。当风来的时候，能飞起来的不是当场开始扎筝的人，是那个筝已经放在风口上等了 8 年的人。

### 5. 最危险的时刻往往最接近转折

2024 年 5 月的 Replit，是一个"用户数几千万、年收入 280 万"的公司——这是一种非常难受的状态：太大了不好关，太小了撑不住。但就是在这个节点，Agent 上线，三个月后年收入过亿。

创业里有个残酷的规律：**很多公司死在离答案最近的地方**。坚持到 2024 年 9 月，Replit 就是那个没有死的。

---

Amjad Masad 在 2026 年 3 月的一篇文章里写道："未来其实非常人性化（The Future is Actually Very Human）"。他说的是 AI 时代人类的位置，但我觉得这句话也在描述 Replit 自己的故事——不是技术的胜利，是一个约旦少年二十年执念的胜利。

---

**相关链接：**
- Replit 官网：[replit.com](https://replit.com)
- 创始人博客：[replit.com/blog/author/amjad-masad](https://replit.com/blog/author/amjad-masad)
- Replit $250M 融资公告：[replit.com/news/funding-announcement](https://replit.com/news/funding-announcement)

<!--EN-->

## May 2024: Almost Dead

Replit had over 20 million users. Annual revenue: $2.8 million.

The users were there. The money wasn't. The company had built a free browser-based coding environment used by millions of students, hobbyists, and beginners around the world — and almost none of them were paying. This is the classic SaaS trap: **user scale and commercial value completely decoupled**.

There were conversations in Silicon Valley about how long Replit could last.

Four months later, in September 2024, they launched something called **Agent**.

You describe what you want in plain English. It configures the environment, installs dependencies, writes the code, and hands you a live URL you can open in your browser.

What followed is hard to believe: revenue went from $10M to **$253M in 13 months — 2,352% growth**. By March 2026, the company was valued at $9 billion.

Most people hear this and think: lucky timing, caught the AI wave.

That explanation isn't wrong. But it misses the most important part.

## From Jordan to the Browser — An Obsession with the Entry Point

Founder **Amjad Masad** was born in 1987 in Amman, Jordan, in a family without a computer.

He learned to code using school computers. He's talked about that feeling repeatedly: **programming is power, but that power is locked behind a gate called "first buy a computer, first install an environment."**

In 2011, while working as an engineer at Codecademy, he built **JSRepl** — a tool that ran JavaScript entirely in the browser, powering exercises on Codecademy and Udacity. No local installation. Open a webpage and write code.

That obsession — zero configuration, the browser is the environment — never changed.

In 2016, he co-founded Replit with his wife Haya Odeh and brother Faris. One-sentence mission: **make programming accessible to anyone, anywhere**.

## 8 Years, 5 Building Blocks

Replit's history from 2016 to 2024, viewed through funding rounds and user growth, looks like a slow-burn company. Viewed differently, you see an organization adding a brick to the same wall every single year.

**2016 — Browser IDE:** Not a plugin in an existing editor. The entire development environment moved into the browser — multi-language support, instant execution, shareable links. 750,000 users by year-end, mostly students and teachers.

**2018 — YC (4th application):** After three rejections. That year's key work: **real-time multiplayer editing** — up to 4 people writing the same code simultaneously, seeing each other's cursors, like Google Docs for code.

**2020 — COVID pushes users past 10 million:** Remote learning exploded. More important than the user growth: the **custom containerization sandbox** built during this period. Every user's code running in a secure, isolated environment. The prerequisite for Agent to configure environments automatically.

**2022 — Ghostwriter:** AI code completion, generation, explanation, debugging, integrated into the IDE. The market didn't pay much attention. But Ghostwriter did something others hadn't: the AI assistant ran **inside a platform that already had a sandbox and deployment capability**. Code the AI wrote could be run immediately, on the same platform.

**2023 — Deployments rewrite:** $97.4M Series B, $1.16B valuation. The money went primarily into rewriting the **deployment system** — one click from code to a live URL, with SSL, domain, CDN, and auto-scaling. This brick didn't look important at the time.

## September 2024: All Five Bricks Snap Together

Agent's core loop:
1. Accept natural language input
2. Understand what you want to build
3. Automatically configure the runtime environment
4. Write the full codebase
5. Deploy — hand you a URL you can open

Translated:

| What Agent does | What Replit had already built |
|----------------|-------------------------------|
| Auto-configure environment | 2016 browser IDE + 2020 containerized sandbox |
| Write the code | 2022 Ghostwriter AI engine |
| Iterate collaboratively | 2018 multiplayer editing mechanism |
| Deploy in one step | 2023 Deployments system |
| Hand you a live URL | 2023 SSL + domain + CDN stack |

**Anyone building an Agent from scratch in 2024 had to construct all five systems before they could run the first sentence. Replit just gave a mouth to something that was already running.**

Agent worked on day one not because of luck, but because five prerequisites had been built, one per year, for eight years.

## The Five Real Reasons

**1. Persistence only works when the direction is right.** Replit survived three YC rejections, years of user growth without revenue, and persistent skepticism about "browser IDEs." But from 2011's JSRepl to 2024's Agent, the core direction never changed: *make the barrier to programming disappear*. Stubborn persistence is stubbornness. Persistence in the right direction is a moat getting deeper.

**2. Infrastructure value is invisible until a threshold is crossed.** Browser IDE, containerized sandbox, multiplayer editing, one-click deployment — each one prompted the question "what's this useful for?" at the time. The answer: when AI Agent needed them, all of them were useful, simultaneously. Infrastructure returns aren't linear. They're step-function jumps triggered by a critical condition.

**3. Mission is the only fuel for the "apparently useless" phase.** Amjad's childhood in Jordan without a computer gave him a genuine, personal fury about programming's gatekeeping. That fury let him keep building infrastructure through the years when users were growing but revenue wasn't — instead of pivoting to something more immediately monetizable.

**4. "Wind" only lifts those who were already ready.** The AI coding explosion happened in 2023-2024. Replit's infrastructure was built 2016-2023. When the wind came, the kite that flew was the one that had been standing in the wind for eight years.

**5. The most dangerous moment is often the closest to the turn.** May 2024 Replit: 20+ million users, $2.8M ARR — too large to shut down easily, too small to sustain. A brutal position. Three months later: Agent launched, and within a year, revenue crossed $100M. Many companies die closest to the answer. Replit was the one that didn't.

---

In March 2026, Amjad Masad wrote a post titled "The Future is Actually Very Human." He was writing about humanity's place in the AI era. But the sentence also describes Replit's own story: not a technology victory, but the vindication of a Jordanian kid's twenty-year obsession.

---

**Links:**
- Replit: [replit.com](https://replit.com)
- Amjad Masad's blog: [replit.com/blog/author/amjad-masad](https://replit.com/blog/author/amjad-masad)
- $250M funding announcement: [replit.com/news/funding-announcement](https://replit.com/news/funding-announcement)
