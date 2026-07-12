---
title: "每个人都是自己的 FDE：读完北上深杭 125 人调查之后"
titleEn: "Everyone Can Be Their Own FDE: Reflections After Reading the 125-Builder China Survey"
description: "FDE 从 Palantir 走向全球，AI 落地失败率 95%，这个角色不该只属于大公司。"
descriptionEn: "FDE went from Palantir to the world. With 95% of enterprise AI pilots failing, this role shouldn't belong only to big companies. A call to action from Chiang Mai."
pubDate: "2026-07-11"
updatedDate: "2026-07-11"
category: "Tech-News"
tags: ["FDE", "AI落地", "学习"]
heroImage: "../../assets/images/self-fde-workbench-everyone-can-be-fde-banner.jpg"
---

> 这篇文章是三件事叠在一起之后写出来的：一份关于 FDE 的全球背景调研，一份国内 125 位 builder 的一线调查，以及我正在做的 [Self-FDE-WorkBench](https://github.com/AuraAIHQ/Self-FDE-WorkBench) 和清迈本地每周 Meetup。它们原本不是同一件事，但读完之后我发现它们说的是同一个问题：**AI 的最后一公里是人。**

---

## 一、FDE 是什么，它从哪里来

FDE，Forward Deployed Engineer，前沿部署工程师。

这个词是 Palantir 在 2010 年代初发明的，起因很具体：他们的早期客户是情报机构，你没法访谈客户，也没法拿到数据，传统的用户调研行不通。于是 Palantir 的解法是：**把工程师直接派驻进客户环境里，通过观察和现场解题来发现问题。**

到 2016 年，Palantir 的 FDE 数量已经超过传统软件工程师。

2026 年，这个角色被重新发现了——不是因为大家突然读懂了 Palantir，而是因为 AI 落地遇到了同样的问题。

MIT 的 NANDA 研究项目对 300 个公开 AI 项目做了追踪，结论是：

> **95% 的企业 AI 试点项目对损益表几乎没有可测量的影响。**

问题不在模型，在于如何把模型用起来。

于是 OpenAI 联合三家机构投入超 40 亿美元成立了「The Deployment Company」，Anthropic 也联合多家机构成立了 AI 原生企业服务公司。2026 年全球 FDE 职位招聘量比两年前暴增了 700%+。

**这个角色的核心价值，从来不是技术本身，而是「进场」。**

| FDE | 传统软件工程师 | 方案工程师（SE） |
|-----|-------------|----------------|
| 服务一个客户，端到端交付 | 服务全体用户，产品代码库 | 售前演示，签单后退出 |
| 写进客户生产环境的代码 | 产品功能代码 | PoC/Demo，不进生产 |
| 90-120 天深度嵌入 | 长期产品迭代 | 短期接触 |
| 成功定义：客户业务指标改善 | 成功定义：功能上线 | 成功定义：赢得合同 |

一句话区别：**FDE 把成果 ship 给一个客户，在他们的 deadline 之前。**

---

## 二、读完北上深杭 125 人调查之后

2026 年 6 月至 7 月，HA7CH Guild 在深圳、上海、杭州、北京连续举办四场闭门 FDE Meetup，约 125 位 builder 参与。这是我目前看到的关于中国 FDE 生态最密集的一手记录。

读完之后，有几件事让我印象很深。

**第一，定价谱系已经形成，从 500 元到 2 亿都有真实合同。**

| 场景 | 价格 | 城市 |
|------|------|------|
| 跨境电商 RPA+数据仪表盘小单 | 500–5000 元/单 | 杭州 |
| 纺织喷墨定位外包，可复制转卖 | 2 万包圆 | 北京 |
| CRM+客户画像项目 | 一期 5 万，整体约 10 万 | 杭州 |
| 高端设备+预测系统整体方案 | 100–150 万/单 | 上海 |
| 信创大单 | 约 2 亿 | 上海 |

这意味着 FDE 不是大公司的专属模式——一个人，解决一个真实问题，就可以开始。

**第二，三城独立收敛到同一个结论：数据基建比 agent 开发更重要。**

杭州场说：业务数据比业务逻辑更重要。北京场说：知识库 + data skills 可以解决 80% 的 FDE 项目问题。深圳场说：独家数据就是切入位点。

agent 很酷，但企业里 90% 的数据还没有整理成 agent 能用的形态。这才是机会所在。

**第三，FDE 的核心壁垒是领域知识，不是工程能力。**

杭州场的共识：工程不再是门槛，很容易有 agent 帮你，很难找到懂某个业务领域的人。一位做财务的人用 AI 自动化了自己 60% 的工作，一位做跨境电商运营的人零基础学 coding 后开始接单——他们的壁垒都不是技术。

**第四，最难的不是技术，是「进场」本身。**

钢厂项目死于老师傅担忧被取代，而不是技术不行。物流项目推不动，最后把功能嫁接到原有 ERP 才跑通。上海已经出现了在组织诊断阶段就和安置公司谈清补偿与转岗的成熟做法。

AI 落地的障碍，大多数时候不在代码里，在人心里。

---

## 三、每个人都可以做自己的 FDE

FDE 这个角色在硅谷的定义是：既懂 AI，又懂客户的业务流程，能够进驻客户环境提炼问题、给出解决方案。

这听起来很高端。但如果你把「客户」换成「你自己的工作」，这件事就变得非常具体：

- 你的工作里有没有重复、低效、可以用 AI 加速的部分？
- 你能不能把这个问题描述清楚，试验一个解法，记录下来？
- 你能不能把这个解法分享给一个有同样问题的人？

这就是 Self-FDE 的起点。

**不需要等到有人雇你做 FDE，你就是自己的第一个客户。**

---

## 四、Self-FDE-WorkBench：一个还在生长的实验

[Self-FDE-WorkBench](https://github.com/AuraAIHQ/Self-FDE-WorkBench) 这个仓库比我读到这份调查要早。

当时的动机很简单：想有一个地方，记录自己用 AI 解决实际问题的过程——不是教程，不是课程，是真实的「提问 → 研究 → 带答案回来讨论」的循环。

仓库的结构：

| 目录 | 用途 |
|------|------|
| `resources/` | 精选文章、论文，按层级标注 |
| `notes/` | 每周个人研究笔记，含困惑和未解问题 |
| `experiments/` | 动手实验代码，验证理解 |
| `episodes/` | 每周分享会记录——提问、答案、讨论 |

核心模式：**上一期提出的问题，这一期带着各自研究的答案回来。**

配套的是清迈（Chiang Mai）每周线下 Meetup——每周六下午，在 Zuzalu Library，一群人围在一起，每人 3 分钟，分享一个用 AI 解决的真实问题，然后投票选出 3 个深挖。

Meetup 的规则说得很清楚：**Not a man standing and teaching you AI skills, but a communication with each other on the topics around AI and building.**

不是一个人在台上讲，而是大家互相学。因为最好的学习方式，是教别人。

---

## 五、你现在可以开始的三件事

读完 HA7CH 的调查，再对照 FDE 的全球发展路径，我越来越觉得：

这个行业最稀缺的不是技术，是愿意进场的人。

如果你现在想开始，三件事最有效：

**1. 找到你最近遇到的一个真实问题**

不需要是客户的问题，你自己工作里反复出现的低效就够了。把它写下来：问题是什么，现在怎么处理，预期的改善是什么。这是所有 FDE 项目的第 0 步。

**2. 试一个最小可行方案，记录下来**

不用完美，用现有工具试一次就够了。把过程记在 `notes/` 或任何你习惯的地方。记录的目的不是给别人看，是让自己下次遇到类似问题时有迹可循。

**3. 找一群人，每周碰一次**

一个人的实验很容易停下来。HA7CH 的调查里有一句话我觉得说到点上了：「有活没人干，有人没活干，中间隔着的是信任。」

每周一次，哪怕只有 3 个人，把自己这周遇到的一个问题带来讨论，就能建立这种信任。

---

## 六、FDE 不是岗位，是一种工作方式

Palantir 用 FDE 打开了企业 AI 落地的第一道门。OpenAI、Anthropic 接过来，花了几十亿美元来证明这件事可以大规模做。

国内 125 位 builder 用真实的合同谱系证明了，这件事在中国已经有了真实的市场。

清迈的小屋子里，每周六下午，几个数字游民围在一起交流，也是同一件事的一个小小切面。

**每个人都可以是自己的 FDE，每个组织都可以培养自己的 FDE 工程师。**

起点只是一个问题，一个愿意试的态度，以及下周再来碰一次的约定。

---

**相关链接**

- Self-FDE-WorkBench：[github.com/AuraAIHQ/Self-FDE-WorkBench](https://github.com/AuraAIHQ/Self-FDE-WorkBench)
- 清迈每周 AI Meetup：[Chiang Mai Weekly AI Study Group](https://app.sola.day/event/detail/19717)
- HA7CH FDE 一线调查：[小红书原文](http://xhslink.com/o/8I1a9ZyFnxf)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Everyone Can Be Their Own FDE: Reflections After the 125-Builder China Survey

> Three things collided and produced this essay: a global FDE research deep-dive, a first-hand survey of 125 builders from Beijing, Shanghai, Shenzhen, and Hangzhou, and the Self-FDE-WorkBench project I've been building alongside a weekly Chiang Mai meetup. They seemed like different things. After reading everything, I realized they're all asking the same question: **the last mile of AI is human.**

---

### What FDE Is and Where It Came From

FDE — Forward Deployed Engineer. Palantir invented the term in the early 2010s because their early clients were intelligence agencies. You couldn't interview them. You couldn't access their data. Normal user research didn't work. So Palantir's answer was: **send engineers directly into client environments to discover problems by observing, not interviewing.**

By 2016, Palantir had more FDEs than traditional software engineers.

In 2026, this role is being rediscovered — not because everyone suddenly read Palantir's playbook, but because AI deployment hit the same wall. MIT's NANDA project tracked 300 public AI projects and found: **95% of enterprise AI pilots have no measurable impact on the P&L.** The problem isn't the model. It's getting the model to actually work.

OpenAI and partner institutions put $4B+ into "The Deployment Company." Anthropic formed a similar joint venture. FDE job postings grew 700%+ from 2024 to 2026.

**The core value of FDE was never technical skill. It's showing up.**

---

### Three Key Findings from the China Survey

HA7CH Guild ran four closed-door FDE meetups across Shenzhen, Shanghai, Hangzhou, and Beijing in June–July 2026. ~125 builders. Real contracts from ¥500 to ¥200M.

**Finding 1: Data infrastructure beats agent development.**
Three cities independently converged on this: business data matters more than business logic. Knowledge base + data skills can solve 80% of FDE project problems.

**Finding 2: Domain knowledge is the real moat.**
Engineering is no longer the barrier. An accountant who automated 60% of their own work, a cross-border e-commerce operator who learned to code — their advantage isn't technology. It's knowing the domain.

**Finding 3: The hardest part is showing up, not coding.**
Steel plant projects died because workers feared replacement. Logistics projects failed until the solution was grafted onto existing ERP. The obstacles are human, not technical.

---

### The Self-FDE-WorkBench

This GitHub repo existed before I read the survey. The motivation was simple: a place to document the process of using AI to solve real problems — not a tutorial, not a course, but a real cycle of "question → research → bring answers back to discuss."

The Chiang Mai weekly meetup is the in-person version: every Saturday afternoon, Zuzalu Library, 3 minutes per person, one real problem solved with AI, then vote on three to go deeper.

The rule: **Not a man standing and teaching you AI skills. A communication with each other on topics around AI and building.**

---

### What You Can Start Now

The rarest thing in this space isn't technical ability — it's people willing to show up.

Three things that work:
1. **Find one real problem in your own work.** Write it down: what it is, how you handle it now, what improvement looks like.
2. **Try a minimal solution and document it.** Not perfect. Once. The goal is having a trace the next time you face a similar problem.
3. **Find a group, meet weekly.** Even 3 people. Bring one problem each week. The HA7CH survey captured it well: "there are jobs without people and people without jobs — what's in between is trust."

---

**FDE isn't a job title. It's a way of working.**

Every person can be their own FDE. Every organization can grow their own.

- Self-FDE-WorkBench: [github.com/AuraAIHQ/Self-FDE-WorkBench](https://github.com/AuraAIHQ/Self-FDE-WorkBench)
- Chiang Mai Meetup: [app.sola.day/event/detail/19717](https://app.sola.day/event/detail/19717)

© 2026 Author: Mycelium Protocol
