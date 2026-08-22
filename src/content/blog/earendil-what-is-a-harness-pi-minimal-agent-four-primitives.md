---
title: "读《What is a Harness?》：Model 负责聪明，Harness 负责让这份聪明变成「能干活」"
titleEn: "earendil-what-is-a-harness-pi-minimal-agent-four-primitives"
description: "Earendil 团队写了一篇极简博客《What is a Harness?》，用攀岩 Harness 的比喻把 Agent Harness 压缩成四件事：System Prompt（工作说明）、Tools（手和脚）、Agentic Loop（根据上一步结果决定下一步的能力）、Translation Layer（换模型不换工作流）。这篇文章是读后感，试图把这个比喻推到底，然后说说为什么 Pi 把「极简」当成第一原则，而不是功能完备。"
descriptionEn: "Earendil's post 'What is a Harness?' compresses agent harnesses to four primitives via a climbing harness metaphor: System Prompt, Tools, Agentic Loop, Translation Layer. This is a reading response — taking that metaphor further and examining why Pi treats minimalism as a first principle rather than an afterthought."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["Agent", "Harness", "Pi", "AI工具", "系统设计", "读后感", "Earendil", "极简"]
heroImage: "../../assets/images/earendil-what-is-a-harness-pi-minimal-agent-four-primitives-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

原文：[What is a Harness?](https://earendil.com/posts/what-is-a-harness/)  
作者：Earendil 团队（Pi 的母公司）  
发布：2026-08-20  
Pi 仓库：earendil-works/pi（badlogic/pi-mono）

---

## 一、那个比喻

Earendil 的这篇文章很短，没有架构图，没有技术细节，开头引用了剑桥词典对「Harness」的释义：

> *Noun.* a piece of equipment with straps and belts, used to control or hold in place a person, animal, or object  
> *Verb.* to control something, usually in order to use its power

然后引出一张照片——皇家·罗宾斯（Royal Robbins）在酋长岩（El Capitan）上的攀岩老照片，腰上挂满工具的攀岩 Harness 清晰可见。

攀岩 Harness 的作用：连接绳索、固定路线、挂载工具、保证人不掉下去。换不同的山，还能带着它去，还能改装它。

这个比喻很准。

---

## 二、四件事

文章把 Agent Harness 拆成四件事，没有一件是废话：

### System Prompt：工作说明

不是嵌入模型权重里的价值观，是上班第一天交给新员工的操作规范。跟着每一条 Prompt 一起注入对话，告诉模型在这个 Harness 的语境里该怎么行动。

可以换，可以扩展，可以按项目定制。

### Tools：手和脚

Harness 描述工具、提供代码，但**不规定模型什么时候用**。搜索网页、写代码、读文件、发邮件——本质上都是工具。模型自己决定调用时机。

这一点被很多人忽视：工具不是规则，是装备。装备挂在腰上，用不用是模型的判断。

### Agentic Loop：根据上一步结果决定下一步

这是 Agent 和 Chat 的本质区别。

文章举了一个例子：用户让 Agent 比较本地小学的排名和考试成绩。Agent 先搜索，发现信息不够，再搜；用代码工具生成电子表格，对比之后发现数据还不满足，再搜；最后写邮件附上附表，检查一遍，判断「工作完成了」，Loop 关闭。

整个过程没有人在旁边盯着。「做完了」是模型自己判断的。

这一个 Loop 就是 Agent 得名的原因。

### Translation Layer：换模型不换工作流

同一个 Harness，接 Anthropic 的 Claude，接 OpenAI 的 GPT，接本地开源模型，行为应该一致——至少工作流应该一致。

更深的含义：**用户拥有 Harness，不拥有模型**。Harness 在你的电脑上，会话历史在你的磁盘里，Provider 可以换。这是和直接用 AI Lab 应用之间最本质的区别。

---

## 三、Model 负责聪明，Harness 负责让这份聪明变成「能干活」

这是文章没有直接说但最清楚的结论。

Agent = Model + Harness。Model 带来推理能力，Harness 把这份推理能力接进真实世界：给它工作说明，给它工具，给它循环的框架，让它可以和不同的底层模型对接。

没有 Harness，Model 只是一个答题机。有了 Harness，它才能真的干活。

---

## 四、为什么 Pi 把「极简」当第一原则

文章里说，Pi 的 System Prompt 很短，默认工具集很小，「out of the box it is designed to get out of the way」。

Pi 用户已经分享了超过 5000 个 Extension。也就是说，Pi 没有试图在出厂时塞满所有能力——它先给你一个**足够小的骨架**，再通过 Extension 让它长成你需要的样子。

这背后是一个设计判断：**Harness 要足够中立，才能真正属于用户**。

文章的最后一句话：

> _We won't do that by ignoring the technologies that exist today, but by harnessing them with clear eyes and a firm grip; ensuring that we wield the hammer, the hammer does not wield us._

「确保我们操控锤子，而不是锤子操控我们。」

极简是实现这句话的方式，不是目的本身。

---

## 五、附：生产级 Harness 之后会更复杂

文章只写到这里就停了，刻意留白。但作为读者，有必要补上后半段：

越往生产走，Harness 必然会面对这些事情——Context 管理（Token 压缩和 Compaction 策略）、Memory（跨会话记忆）、Permission（权限控制和沙箱隔离）、Recovery（失败恢复和重试）、Trajectory（轨迹回放和 Debug）、Evaluation（自动化评测）……

每一个都不小。

但「先极简、再扩展」的顺序是对的。在骨架够小的时候，用户才能看清楚自己在扩展什么、为什么扩展。Harness 越重，用户越容易丧失主动权，在某个既定框架里被动适应，而不是主动构建。

这正是 Pi 的反面教材——Claude Code 是第一个流行的 Agent Harness，文章说它当初并不是为了「模型中立」而设计的，而是为了让用户在本地电脑上用 Claude 写代码。中立是后来的开源生态在追求的事情。

---

攀岩 Harness 不负责爬墙，它负责让你可以爬墙。Agent Harness 也一样——它不负责聪明，它负责让聪明派上用场。

这篇文章写得很克制，把一个容易讲烂的话题压缩到了本质。推荐原文。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Reading "What is a Harness?" — The Model Does Thinking, the Harness Makes It Work

*by Mycelium Protocol*

---

Original: [What is a Harness?](https://earendil.com/posts/what-is-a-harness/)  
Author: Earendil (the company behind Pi)  
Published: 2026-08-20  
Pi repo: earendil-works/pi (badlogic/pi-mono)

---

### The Metaphor

Earendil's post is short — no architecture diagrams, no technical specs. It opens with the Cambridge Dictionary definition of "harness":

> *Noun.* a piece of equipment with straps and belts, used to control or hold in place a person, animal, or object  
> *Verb.* to control something, usually in order to use its power

Then comes a photograph: Royal Robbins on El Capitan, a climbing harness racked with gear loops and carabiners.

A climbing harness connects you to ropes, governs your route, holds your tools, keeps you from falling. You can take it to different mountains. You can modify it. It's adaptable. It can become yours.

It's a good metaphor.

---

### Four Things

The post breaks down an agent harness into four things, none of them wasted:

**System Prompt: the job description.** Not the values baked into model weights — more like the instructions handed to a new employee on day one. Injected into every conversation. Tells the model how to behave in the context of this particular harness.

**Tools: hands and feet.** The harness describes the tools and provides the code. Web search, file reads, code execution, email composition — all tools. Critically: the harness doesn't dictate when to use them. It makes them available, describes them clearly, and lets the model decide. Tools are equipment on the gear loop, not rules.

**Agentic Loop: deciding the next step based on the last.** This is what separates agents from chat. The post's example: user asks the agent to compare local primary school rankings. Agent searches, finds the data thin, searches again. Builds a spreadsheet in code, checks it against the request, decides it needs more data, searches again. Composes an email with the spreadsheet attached. Reviews everything. Decides: job done. Loop closes. No human intervention mid-task — "done" is the model's own judgment.

**Translation Layer: swap models, keep the workflow.** Same harness, different provider — Anthropic, OpenAI, local open-weight. The translation layer is what makes this possible. More importantly: the user owns the harness, not the model. The harness runs on your laptop. Session history lives on your disk. You can take it somewhere else. That's the fundamental difference from using an AI lab's own application.

---

### The Model Does Thinking, the Harness Makes It Work

This is the clearest conclusion the post doesn't quite state directly.

Agent = Model + Harness. The model brings reasoning. The harness connects that reasoning to the real world: job description, tools, loop framework, and the ability to swap out the underlying model.

Without a harness, a model is a Q&A machine. With one, it can actually work.

---

### Why Pi Treats Minimalism as a First Principle

Pi's system prompt is short. Its default toolset is small. "Out of the box it is designed to get out of the way."

Pi users have now shared over 5,000 extensions. Meaning: Pi didn't try to ship every capability — it ships a **skeleton small enough to understand**, then grows through Extensions into whatever shape each user needs.

The underlying design judgment: **a harness has to be neutral enough to truly belong to the user.**

The post's final line:

> _We won't do that by ignoring the technologies that exist today, but by harnessing them with clear eyes and a firm grip; ensuring that we wield the hammer, the hammer does not wield us._

Minimalism is the method, not the goal.

---

### What Production Harnesses Face

The post deliberately stops here. Worth adding: as a harness matures toward production, it inevitably confronts Context management (compaction strategies), Memory (cross-session state), Permission systems (sandboxing), Recovery (failure retry), Trajectory (session replay and debugging), and Evaluation (automated quality checks).

None of these are small.

But "start minimal, extend deliberately" is the right order. When the skeleton is small, users can see clearly what they're adding and why. A heavy harness makes users passive — adapting to a fixed framework rather than building their own.

The post names this tension explicitly: Claude Code was the first popular agent harness, but it wasn't designed for model-neutrality. It was designed to let users code with Claude on their local machine. Neutrality is what the open-source ecosystem built afterward.

---

A climbing harness doesn't climb walls. It lets you climb walls. An agent harness doesn't do the thinking. It puts the thinking to work.

This post is worth reading in full — it covers a concept that's easy to overcomplicate, in very few words.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
