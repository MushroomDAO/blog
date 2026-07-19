---
title: "Replit 如何让 Agent 进入整家公司：自动驾驶公司实践，工程效率 5.8x，代码输出翻三倍"
titleEn: "How Replit Turned AI Agent Into a Company-Wide Operating System: 5.8x Engineering Output, Self-Driving Across Every Function"
description: "Replit CEO Amjad Masad 的《The Self-Driving Company》记录了 Replit 过去六个月用 AI Agent 重构整个公司运转方式的真实过程：工程效率 5.8x、PR reversion 率持平、支持工单处理快 60%、放弃七位数 SaaS 产品转用内部 Agent……最重要的发现：人没有被自动化掉，而是被晋升了。"
descriptionEn: "Replit CEO Amjad Masad's 'The Self-Driving Company' documents six months of wiring AI agents into every part of Replit: 5.8x engineering output, flat reversion rates, 60% faster support resolution, and churning a 7-figure SaaS for an in-house agent. The core finding: people weren't automated out — they were promoted."
pubDate: "2026-07-19"
updatedDate: "2026-07-19"
category: "Tech-Experiment"
tags: ["AI Agent", "Replit", "自动化公司", "Loop Engineering", "工程效率", "AI转型", "Agent系统", "组织变革"]
heroImage: "../../assets/images/replit-self-driving-company-banner.jpg"
---

> **原文**：[The Self-Driving Company](https://blog.replit.com/self-driving-company) — Amjad Masad，2026-07-16  
> **Replit**：全球最大的在线 IDE 平台之一，2600 万+ 用户，Replit Agent 的开发商

---

## 读完之后

这篇文章让我停下来想了很久。

不是因为数字惊人——5.8x、工程效率翻三倍、支持工单快 60%——数字只是结果。

让我停下来的是那句话：**"People don't feel like they've been automated. They feel like they've been promoted."**（人们不觉得自己被自动化了，他们感觉自己升职了。）

这不是 PR 稿里的话术。Amjad Masad 配上的是工程数据、真实的 Slack 截图、从工程蔓延到销售再到市场再到支持的扩散路径——他在描述一个正在发生的组织形态的变化。

Replit 是第一个把这件事做明白并且完整写出来的公司。

---

## 起点：去年圣诞节假期

"Like many people working in AI, we returned from the Christmas break feeling that something fundamental had changed. Models could sustain work over much longer horizons."

从圣诞节回来，Replit 的工程师们意识到：之前反复失败的任务——告警分类、根因分析——开始能跑通了。AI 开始解决他们最顽固的 bug。

**他们做了一个关键决策：停止把 Agent 当作 IDE 或聊天窗口里的工具，而是把它编织进公司的运营结构里。**

---

## 工程：5.8x

1 月底，Replit 建起了一套基础设施：基于他们自己的 Agent harness、microVM、远程文件系统，任何工程师都可以编排一群并行的 Agent 来工作。整套系统包裹在：

- 访问权限策略（Access Policies）
- Token 代理（Token Proxies）
- 审计日志（Audit Logging）
- ZeroTrust 网络

然后打通了他们用来工作的所有工具：**GitHub、GCP、Azure、Linear、Notion、Slack、ZenDesk**。

效果：

- **5.8x** 代码行数增长（1 月到 6 月底）
- 排除新员工入职效应，老员工同比 **2.9x**
- PR Review 延迟持平（Agent 承担了 **30%** 的人工 review 工作）
- PR Reversion 率**持平**（不是上升，是持平——这才是最难的）
- 故障平均修复时间（MTTM）下降

最戏剧性的是 Agent 4 发布冲刺周——原本那段时间人肉效率会达到极限，这次直接被 Agent 突破了天花板，生产力曲线弯曲向上，超出了所有人的预期。

### 为什么 PR 质量没崩？

两个原因：

1. **Agent 参与代码审查**：识别风险等级，只有高风险才叫第二个人类来看，否则自己审完
2. **Agent 协助事故调查**：每个生产事故都有 Agent 先去做根因分析，带着结论汇报给人

这让「更多代码」和「更好质量」同时发生——两者通常是 tradeoff，这次不是。

---

## Agent of Agents：Loop Engineering 在规模上落地

Amjad 说得很直白：「当工程师们找到产生循环的方式——派遣一群 Agent 去完成可验证的任务——我们看到了最戏剧性的变化。」

每个员工都可以访问一个**Manager Agent**，它能 spawn 出多个子 Agent，在循环里代表你完成任务。

具体案例：

- 一个工程师完成了长期搁置的 CSS 系统迁移
- 另一个工程师自动化了产品本地化迁移
- 又一个工程师把 flaky test 维护自动化了
- CTO 用 Agent swarm 破解了一个最难的 PSC 和 fd shutdown 网络 bug

这些事情有一个共同点：**以前不是技术上做不到，而是成本太高没人愿意做**。循环 Agent 把「愿意做的成本」降到了接近零。

### 自我改进的 Agent

这是文章里最让我感到震惊的部分。

Replit 的 AI 团队构建了一套**持续学习系统**：

1. 分析用户反馈
2. 提出改进方案
3. 用 benchmark 和 A/B test 验证效果
4. 把有效的改进合并进去

**Replit Agent 在自我改进**。不是人在优化它，是它在优化自己。

---

## 全公司：从工程蔓延出去

传播的方式很有趣：**Slack interface**。

其他部门的人注意到工程师在 Slack 里给 Agent 打标签分配任务，就自己试了试。最开始是问问题——"这个功能的产品预期是什么？"——因为 Agent 同时有知识库和代码库的上下文，任何人都能得到答案，不需要等工程师回复。

然后各个部门开始贡献自己的技能和集成：

### 数据团队

给 Agent 叠加了**语义层（Semantic Layer）**——它知道数据仓库里哪些表是 source of truth，表之间是什么关系。

现在任何人都可以向 Agent 提 BI 问题，得到可靠的答案，自己生成图表和演示文稿——包括这篇博客文章里的所有图表，全是 Agent 生成的。数据团队的时间从「响应需求」变成了「专注最难的分析问题」。

### 销售团队

- **SDR（销售开发代表）**：Agent 寻找并丰富产品合格线索，用内部知识做到更精准的触达
- **AE（客户主管）**：客户对话前 Agent 准备简报——谁在获得最大价值、哪些项目最活跃、积分用量和合同的对比——然后打包成定制的品牌 slides

### 市场团队

Agent 能用一句 prompt 从头起草产品 spec，基于工程和产品各处的对话记录和文档。市场人员不需要参加每一个会，就能及时跟上产品进度，有更多时间做创意工作。

### 支持团队

Agent 被赋予了调查工单、执行标准 playbook 的技能。它可以用客服语气直接回复用户，或者带着调查摘要上报给工程。

结果：**最难的工单（需要升级到人类处理的）关闭速度快了 60%**。

---

## 一个标志性的决策：放弃七位数 SaaS

「我们刚刚淘汰了一个七位数的 SaaS 解决方案，因为我们用 Replit 完全自建的内部 App 更好，员工已经迁移过去了。」

这不只是省钱。这说明了一件更深的事：**当你的内部 Agent 有足够深的上下文和定制深度，任何通用 SaaS 产品都很难竞争**。

他们还测试了两个垂直工具：
- 一个工程师 alert 分诊和根因分析工具：质量相近，**成本是内部方案的 10x**
- 一个自动渗透测试工具：发现的漏洞**比内部方案少**，成本同样 10x

两个内部版本都上了生产。

---

## 自动驾驶公司是什么

Amjad 的定义很清晰：

> **"A self-driving company is not one without people. People still choose the destination. They decide which problems matter, make difficult tradeoffs, exercise taste, and take responsibility for the outcome. But increasingly, they do not perform every step required to get there."**

不是没有人的公司。人仍然选择目的地、决定什么问题重要、做困难的取舍、负责结果。

但他们越来越不需要亲手执行到达目的地的每一步。

这个模型里，Agent 的地位不是「工具」，不是「助手」——更接近**独立执行者**：接受目标、收集上下文、执行工作、检查结果、在需要人类判断时上报。

而人的角色，从 **doer（执行者）** 变成了 **director（指挥者）**。

---

## 技术基础设施决定了扩散速度

Replit 能做到这件事，有几个关键基础设施支撑：

1. **microVM**：每个 Agent 任务隔离运行，不相互干扰
2. **Remote Filesystem**：Agent 访问真实的代码库，不是副本
3. **ZeroTrust Network**：把 Agent 的权限限制在精确控制的范围内
4. **Token Proxies + Audit Logging**：知道每个 Agent 在做什么、花了多少
5. **Semantic Layer over Data Warehouse**：让 Agent 不只会查数据，还知道数据的含义

这不是随意给 Agent 开放所有访问权限，而是**精确授权的访问**——Agent 能拿到它需要的一切，但每一步都可被审计。

---

## 我的判断

这件事的意义不只是 Replit 自己生产力翻了几倍。

它展示了一个路径：**Agent 渗透整个公司的传播机制是什么**——从工程开始，因为工程师最先理解它；通过 Slack 扩散，因为所有人都在 Slack；每个部门贡献自己的 skill 和上下文，整个系统变得更强。

这是一个正反馈循环：每个部门的 Agent 越强，整个公司的 Agent 就越强，因为它们共享上下文和知识库。

「自动驾驶公司」不是科幻。Replit 正在 2026 年的现实里跑。

等这套东西开放给用户，会很有意思。

---

## 数据一览

| 指标 | 变化 |
|---|---|
| 代码行数（1月→6月） | **+5.8x** |
| 同期工程师人均代码产出 | **+2.9x** |
| 节省的 PR 人工 Review 时间 | **30%** |
| PR Reversion 率 | 持平（未上升） |
| 支持工单关闭速度（人工升级类） | **+60%** |
| 安全漏洞发现 vs 商业工具 | 更多，成本 1/10 |
| 淘汰的 SaaS 合同 | 七位数（美元）|

© 2026 Author: Mycelium Protocol

<!--EN-->

## How Replit Turned AI Agents Into a Company-Wide Operating System

**Source**: [The Self-Driving Company](https://blog.replit.com/self-driving-company) — Amjad Masad, July 16, 2026

### The Core Idea

A self-driving company is not one without people. People still choose the destination — which problems matter, which tradeoffs to make. But they no longer perform every step required to get there. Agents do the steps. Humans become directors.

Replit's blog post documents six months of making this real.

### Engineering First: 5.8x

In late January, Replit built internal infrastructure: their own agent harness, microVMs, remote filesystem. Any engineer could orchestrate parallel agent swarms. Wrapped in access policies, token proxies, audit logging, and ZeroTrust networking. Then opened to GitHub, GCP, Azure, Linear, Notion, Slack, ZenDesk.

Results:
- **5.8x** lines of code (January → late June)
- **2.9x** per-engineer output (consistent cohort, hiring effect removed)
- **30%** of human PR review time saved by the agent
- PR reversion rates: **flat** (not up, despite massively more AI-written code)
- Incidents: flat; MTTM (mean time to mitigation): down

The key: agents also review code and investigate incidents. More code + better quality, simultaneously. Not a tradeoff.

### Agent of Agents: Loop Engineering at Scale

"When engineers find ways to generate loops — sending a fleet of agents to complete a verifiable task — we see the most dramatic change."

Every employee accesses a manager agent that spawns multiple sub-agents, orchestrating loops on their behalf. Results: a long-stalled CSS migration completed; product localization automated; flaky test maintenance automated; a stubborn PSC and fd shutdown networking bug cracked with an agent swarm.

The most remarkable: a **continual learning system** that analyzes user feedback, proposes improvements, validates via benchmarks and A/B tests, and ships the wins. Replit Agent is improving itself.

### Company-Wide Spread via Slack

Other departments noticed engineers tagging the agent in Slack. They tried it. The initial use: asking questions the agent could answer with both knowledge base and codebase context. From there:

**Data team**: Added a semantic layer over the data warehouse. Now anyone can ask BI questions and get reliable answers — including building every chart in the original blog post.

**Sales**: SDRs use the agent to find and enrich product-qualified leads with internal context generic tools can't see. AEs get pre-call briefings packaged as branded slides.

**Marketing**: One prompt drafts a full product spec from engineering and product documents.

**Support**: Agent investigates tickets and follows playbooks. Hardest tickets (escalated to humans) closed **60% faster**.

### Churned a 7-Figure SaaS

Internal agent outperformed a leading market solution they were paying 7 figures for. Employees migrated. Contract cancelled.

Also tested vertical tools:
- Alert triage + root cause: similar quality, **10x more expensive** than internal version
- Automated pen testing: internal version found **more vulnerabilities** at **1/10th the cost**

Both internal versions went to production.

### Key Stats

| Metric | Change |
|---|---|
| Lines of code (Jan → Jun) | +5.8x |
| Per-engineer output (same cohort) | +2.9x |
| PR review time saved | 30% |
| PR reversion rate | Flat |
| Support ticket close speed (escalated) | +60% faster |
| Security vulns vs. commercial tool | More found, 1/10th cost |
| SaaS contract churned | 7-figure USD |

### What This Means

The spread mechanism matters: engineering first (they understand it first), then Slack (everyone's already there), then each department contributes skills and context, making the whole system stronger. A compounding loop: each department's agent improves, the shared knowledge base grows, every agent gets better.

The self-driving company isn't science fiction. Replit is running it in 2026.

© 2026 Author: Mycelium Protocol
