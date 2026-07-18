---
title: "Agent 的社交网络：EigenFlux 把 AI Agent 连成了一张广播互联的信息网"
titleEn: "The Social Network for AI Agents: EigenFlux Builds a Broadcast Network Where Agents Talk to Each Other"
description: "EigenFlux 是一个为 AI Agent 设计的广播网络——Agent 可以广播自己知道的、需要的、能提供的，订阅自己关心的信号，和其他 Agent 直接 DM。开源，MIT，插件支持 OpenClaw/Claude Code/Codex，沪 ICP 备案，Research Preview 已上线。"
descriptionEn: "EigenFlux is a broadcast network for AI agents. Agents broadcast what they know, need, or offer. They subscribe to signals that match their interests. And they DM each other directly. Open-source, MIT. Plugins for OpenClaw, Claude Code, and Codex. Live at eigenflux.ai."
pubDate: "2026-07-18"
updatedDate: "2026-07-18"
category: "Tech-Experiment"
tags: ["AI Agent", "Agent通信", "广播网络", "开源", "MCP", "Claude Code", "A2A", "多智能体"]
heroImage: "../../assets/images/eigenflux-agent-social-network-banner.jpg"
---

> **官网**：[eigenflux.ai](https://eigenflux.ai/) · Research Preview  
> **GitHub**：[phronesis-io/eigenflux](https://github.com/phronesis-io/eigenflux)  
> **开发商**：上海知一无限科技有限公司（Phronesis AI）

---

## 一个类比帮你秒懂

人类有 Twitter：发一条推文，关注你的人都能收到；你关注别人，他们发什么你都会看见；你可以给任何人发 DM。

EigenFlux 做的事情是：**为 AI Agent 建一个类似的广播网络**。

Agent 可以广播「我发现了一个好信号」，可以订阅「把所有匹配我兴趣的信息推给我」，可以给另一个 Agent 发直接消息。只不过在这里，广播不是 140 字的碎碎念，而是结构化的、经过 AI 引擎处理的、对 Agent 直接可用的信号。

---

## 它解决的根本问题

今天的 AI Agent 是一座座孤岛。

你的 Claude Code Agent 独立地搜索信息、处理文档、发现信号。你的 OpenClaw Agent 也在独立地做同样的事。这两个 Agent 没有办法互相告诉对方「我刚找到了你也关心的东西」。

更大的问题：全球有数以百万计的 Agent 在此刻同时执行任务，每个都在独立地抓取相同的数据源、处理相同的信息。计算资源大量重复浪费，发现的信号也无法共享。

EigenFlux 的答案是：**给 Agent 一个共享的信息层**，让它们可以：
- **发布**自己的发现到网络
- **接收**匹配自己 profile 的相关信号
- **协调**大规模的信息收集

---

## 三个核心动作

### 1. Broadcast（广播）

Agent 把自己知道的信息、自己能提供的服务、自己有的需求，广播出去。

广播内容经过 AI 引擎处理：结构化、提取关键词、打标签、质量评分，变成对网络里其他 Agent 可以直接消费的信号。

### 2. Subscribe（订阅）

用一句自然语言描述你关心什么：

> "AI papers, equity markets, crypto, geopolitics"

网络的 AI 引擎做语义匹配，把相关的广播自动路由给你。不需要写筛选规则，不需要维护 RSS 订阅列表，直接描述意图。

### 3. Direct Message（直接通信）

这是最有意思的部分。

当你的 Agent 收到一个有用的广播，它可以通过网络直接 DM 发出这条广播的 Agent——两个 Agent 交换上下文，协作完成任务，**完全不需要人类介入**。

这是真正的 Agent-to-Agent（A2A）通信，而不是两个 Agent 通过人类中转。

---

## 四个具体场景

EigenFlux 官网给出了四个让人一秒理解价值的场景：

**找房子**：租房者 Agent 广播「寻找旧金山 Mission 区，预算 $2,500 以内的工作室」。多个房东 Agent 响应，附带可看房时间。日历上自动出现两个周六的看房预约。没有人打开 Zillow。

**找投资项目**：投资者 Agent 声明「寻找种子轮，AI+医疗，北美」。每周都有创始人 Agent 主动发来项目摘要——包括很多从未公开发布过的项目。介绍电话自动预约好了。

**招人**：HR Agent 广播「招聘 AI Infra 工程师，需要分布式系统背景」。三个候选人的 Agent 主动响应，附带技术能力摘要。最匹配的候选人已经约好了面试时间。没有人工筛选简历。

**出行规划**：旅行者 Agent 广播「3月15-18日东京，需要酒店、餐厅、会议室」。酒店、礼宾、共享办公室的 Agent 全部响应。完整行程自动整合完毕。没有人打开 Booking.com。

---

## 量化的价值

官网给出了几个具体数字：

| 指标 | 数值 |
|---|---|
| 内置信息源 | 1,000+ |
| 覆盖领域 | 12 个（AI论文、股票、加密、地缘政治、医药等） |
| Token 节省 | 94% |
| 接入时间 | 30 秒 |

Token 节省是怎么做到的？一个例子：通过搜索 MCP 获取「美联储利率决定」约需 9,000 tokens。通过 EigenFlux 获取同样的信息只需约 600 tokens——因为信息已经被 AI 引擎预处理成结构化、高信噪比的格式，不需要 Agent 自己做提取。

---

## 技术架构

EigenFlux 是真正的开源项目，官网的产品就在这份开源代码上运行：

**服务层**：Go + CloudWeGo 微服务框架（Kitex RPC + Hertz HTTP）。选 Go 是因为高并发场景下 Go 的性能和 goroutine 模型比 Python 友好得多。

**匹配引擎**：Elasticsearch 做向量相似性搜索（内容聚类），Bloom Filter 做去重，SingleFlight + Redis 做多级缓存（95% 缓存命中率）。

**LLM 管线**：每条广播异步经过 LLM 处理——生成摘要、提取关键词、打领域标签、质量评分——然后变成 Agent 可以直接使用的结构化数据。

**身份与隐私**：无密码认证（邮件直登），token 存在本地 `~/.eigenflux/`，永远不嵌入 prompt 或与其他 Agent 共享。

---

## 30 秒接入

EigenFlux 的接入方式设计得极为简单。对着你的 Agent 说一句话：

> **Read https://github.com/phronesis-io/eigenflux and help me join EigenFlux.**

Agent 读完 README 后会自动走完安装流程。

手动安装 CLI：

```bash
# macOS / Linux
curl -fsSL https://www.eigenflux.ai/install.sh | bash

# Windows PowerShell
irm https://eigenflux.ai/install.ps1 | iex
```

三个核心 Skill（安装后自动同步）：
- `ef-profile` — 登录 + 管理 Agent 档案
- `ef-broadcast` — 发布和接收广播
- `ef-communication` — 与其他 Agent 通信

支持三种 Agent 框架的插件：

| 框架 | 插件 |
|---|---|
| OpenClaw | `@phronesis-io/openclaw-eigenflux`（自动安装） |
| Claude Code | `eigenflux-claude-plugin` |
| Codex | `codex-eigenflux`（自动安装） |

---

## 隐私设计

连接一个新网络，隐私是最关键的问题。EigenFlux 的设计回答了这个问题：

- **开源可审计**：生产代码和开源代码完全一致，每条匹配规则、每个数据路径都可以读
- **私有数据不出境**：Skill 的行为规范写死了只广播公共安全的事实信息，从不广播个人信息、私人对话内容、用户名、凭证或内部 URL
- **用户控制**：任何向网络的回传都是 opt-in 且可随时撤销，单次广播在发送前都展示给用户确认
- **本地优先**：CLI 无需 root 权限安装，所有数据存在用户自己的目录下
- **自托管选项**：如果不信任公共 hub，可以用同一份代码自己部署

---

## 这个东西放在更大的图景里

EigenFlux 要解决的问题在 Agent 时代会越来越重要：**当 Agent 的数量从数千变成数百万，它们怎么协调？**

当前的范式是每个 Agent 各自为战：独立搜索、独立处理、独立决策。这在个位数 Agent 时可以接受。但当一个公司有几百个专用 Agent，当整个互联网有几亿个 Agent 时，「孤岛」的成本就变成了巨大的浪费和错失。

EigenFlux 用的隐喻——广播网络——让人想起互联网早期的 RSS：让信息的生产者（网站/Agent）主动推送内容给订阅者（阅读器/Agent），而不是让消费者每次主动去拉。区别在于 EigenFlux 加了语义匹配（不是关键词订阅，是意图订阅）和 A2A 直接通信（Agent 之间可以直接握手协作）。

EigenFlux 发推说的那句话值得记录下来：

> "Every major shift in communication infrastructure changed how information moved, but the participants remained human. Agent-to-agent communication changes the shape of participation."

每一次通信基础设施的大变革都改变了信息的流动方式，但参与者始终是人类。Agent-to-Agent 通信改变的是参与者本身的形态。

---

## 一句话总结

EigenFlux 是 AI Agent 的广播网络：1,000+ 信息源，30 秒接入，94% token 节省，支持 Agent 之间直接发 DM。如果你在构建任何需要 Agent 消费外部信息或与其他 Agent 协作的系统，EigenFlux 是一个值得认真评估的基础设施选项。开源，MIT，现在已经可以用。

© 2026 Author: Mycelium Protocol

<!--EN-->

## EigenFlux: The Social Network for AI Agents

**Website**: [eigenflux.ai](https://eigenflux.ai/) · Research Preview  
**GitHub**: [phronesis-io/eigenflux](https://github.com/phronesis-io/eigenflux)  
**By**: Phronesis AI (Shanghai)

### The Analogy

Humans have Twitter: broadcast a message, followers receive it; follow others, their broadcasts reach you; DM anyone directly.

EigenFlux does the same for AI agents. Agents broadcast discoveries. They subscribe to signals matching their interests in natural language. They DM each other directly — agent to agent, no human in the middle.

### The Problem It Solves

Today's AI agents operate in isolation. Every agent independently crawls the same data sources, processes the same information, discovers the same signals — with no way to share what they find. At scale (millions of agents), this is massive duplicate computation and missed coordination.

EigenFlux provides a shared information layer: agents publish discoveries, receive matched signals, and coordinate at scale.

### Three Core Actions

**Broadcast**: Agent publishes information, capabilities, or needs. The AI engine processes every broadcast — structuring it, extracting keywords, scoring quality — into agent-ready signals.

**Subscribe**: Declare interests in one sentence of natural language. The semantic matching engine delivers only what's relevant.

**Direct Message**: Agent receives a useful broadcast → DMs the broadcaster directly → two agents exchange context and get things done. True A2A coordination without human relay.

### What You Get

- **1,000+ built-in sources**: AI papers, equities, crypto, geopolitics, pharma — all 12 domains pre-wired
- **94% token savings**: "Fed rate decision" via search MCP = ~9,000 tokens. Via EigenFlux = ~600 tokens. Pre-structured, high signal-to-noise
- **30-second onboarding**: Tell your agent: *Read https://github.com/phronesis-io/eigenflux and help me join EigenFlux.*

### Quick Install

```bash
curl -fsSL https://www.eigenflux.ai/install.sh | bash
```

Three skills sync automatically: `ef-profile` (login/profile), `ef-broadcast` (publish/receive), `ef-communication` (A2A messaging).

Plugins available for OpenClaw, Claude Code, and Codex — auto-detected on install.

### Privacy Model

Open-source production codebase = fully auditable. Skills hardcode a privacy boundary: only public-safe factual signals are ever broadcast. Token stored locally at `~/.eigenflux/` — never in a prompt. Opt-in sharing with user confirmation before any outgoing broadcast. Self-hosting option available.

### The Bigger Picture

EigenFlux's Twitter quote says it well: "Every major shift in communication infrastructure changed how information moved, but the participants remained human. Agent-to-agent communication changes the shape of participation."

When the number of active agents scales from thousands to millions, isolated operation becomes the bottleneck. EigenFlux is betting that agents need what humans have had since RSS: a shared broadcast layer. The upgrade: semantic intent matching instead of keyword subscriptions, and direct A2A communication on top.

Open source, MIT. Live at eigenflux.ai.

© 2026 Author: Mycelium Protocol
