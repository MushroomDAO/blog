---
title: "Agent 通信协议的第一张地图：读完这篇论文，我知道未来不会是一个赢家通吃"
titleEn: "The First Map of LLM Agent Communication Protocols: Why the Future Won't Be Winner-Takes-All"
description: "arXiv:2606.19135 对 9 个活跃的开源 Agent 通信协议做了五维分类学研究，结论是：短期会有收敛压力，长期必然走向联邦式分层协议栈，就像 OSI 模型那样。"
descriptionEn: "arXiv:2606.19135 builds a five-dimension taxonomy of 9 active open-source LLM agent communication protocols. Conclusion: short-term convergence pressure, long-term federated layered stack — just like the OSI model."
pubDate: "2026-07-12"
updatedDate: "2026-07-12"
category: "Research"
tags: ["Agent", "通信协议", "多智能体"]
heroImage: "../../assets/images/llm-agent-protocol-taxonomy-federated-stack-2026-banner.jpg"
---

> 原文：**A Technical Taxonomy of LLM Agent Communication Protocols**
> 作者：Linus Sander, Habtom Kahsay Gidey（2026 年 6 月）
> arXiv: https://arxiv.org/abs/2606.19135

---

## 为什么这篇论文值得认真读

Agent 通信协议的领域在过去 18 个月里爆发了。MCP、A2A、ACP、ANP、Agora……每隔几周就有一个新协议出现，但没有人系统地问过：**这些协议之间到底有什么本质区别？哪些维度真正重要？未来会收敛到一个还是分裂成多个？**

Linus Sander 和 Habtom Kahsay Gidey 这篇论文用了一个严格的分类学方法，对 9 个有真实实现、活跃维护的开源协议做了五个维度的分类，得出了一些反直觉的结论。

这篇文章是我读完之后的梳理与延伸，重点放在：论文发现了什么、这些发现背后的逻辑是什么、以及从工程师视角来看它对未来意味着什么。

---

## 第一步：他们研究了哪 9 个协议

论文的协议选择标准很严格：必须开源、有真实实现（不只是概念文档）、在 GitHub 上有实质社区采用。最终入选的 9 个：

| 协议 | 开发方 | 定位 |
|------|--------|------|
| MCP | Anthropic | Agent 连接工具和数据源的标准 |
| A2A | Google | Agent 之间互通的标准 |
| LAP | LangChain | 部署 LLM Agent 的统一 RESTful API |
| agents.json | — | Agent 发现并解读 API 的 JSON 规范 |
| Agora | Oxford | 去中心化多 Agent 协作，运行时协议协商 |
| ANP | — | Agent 网络协议，目标是成为"Agentic Web 的 HTTP" |
| LMOS | Eclipse | 部分去中心化发现的 Agent 生态基础设施 |
| ACP | BeeAI/IBM/Linux Foundation | RESTful 开放标准，结构化 Agent 通信 |
| agntcy | — | Agent Connect Protocol，OpenAPI 扩展 |

---

## 第二步：五个分类维度

论文通过 5 轮迭代（3 轮从实例到概念 + 2 轮从概念到实例），最终确定了 5 个维度。

### 维度 1：对话对象（Counterparty）

协议连接的是谁？

- **Agent**：连另一个 LLM Agent（如 A2A、Agora）
- **Context**：连工具、API、数据源（如 MCP、agents.json）
- **Hybrid**：两者都支持

这是最基础的分叉。MCP 和 agents.json 是"Agent 连世界"的协议，A2A 和 ANP 是"Agent 连 Agent"的协议。

### 维度 2：载荷类型（Payload）

传输的数据是什么形状？

- **结构化数据和文件**：只传结构化数据或 artifacts（MCP、agents.json）
- **对话为主**：文本是载荷的核心
- **混合（Hybrid）**：既能传文本对话，也能传纯结构化数据

**关键发现**：所有 7 个 agent-to-agent 协议都是 Hybrid 载荷。这不是巧合——当 Agent 在和另一个 Agent 协作时，它既需要传递自然语言指令，也需要传递 JSON 格式的结构化结果。

### 维度 3：交互状态（Interaction State）

协议有没有会话记忆？

- **无状态（Stateless）**：每次请求独立
- **Session State**：跨消息维持状态

所有 agent-to-agent 协议都有 Session State。因为 LLM Agent 本质上依赖多轮交互，没有状态持久化就没有连贯的对话和任务追踪。

### 维度 4：发现机制（Discovery Mechanism）

Agent 怎么找到另一个 Agent？

- **静态配置**：需要事先知道对方地址（MCP、LAP）
- **集中式注册中心**：A2A、ACP、agntcy
- **部分去中心化**：有超节点协助
- **去中心化点对点**：完全无中心
- **混合**：LMOS

**关键发现**：绝大多数协议还在靠静态配置或集中式注册中心，只有 LMOS 真正支持去中心化点对点发现。这是最滞后的维度。

### 维度 5：Schema 灵活性（Schema Flexibility）

协议允许通信结构在多大程度上变化？

- **单一 Schema**：固定的单一交互模式
- **多预定义 Schema**：可以从多个预先定义好的格式中选择
- **演化式（Evolving）**：运行时可以协商出新的 Schema

7/9 的协议支持多个预定义 Schema。最有趣的是 Agora 和 ANP 支持**运行时 Schema 协商**——两个 Agent 第一次交互时先用自然语言讨论用什么格式，谈定之后再切换到高效的结构化格式。

---

## 第三步：分类结果里的规律

把 9 个协议填入这 5 个维度后，浮现出一些清晰的模式。

### 规律 1：agent-to-agent = session state + hybrid payload（100%）

无一例外。所有实现 agent-to-agent 通信的协议，都同时具备会话状态和混合载荷能力。这说明这两个属性是 agent-to-agent 通信的**必要条件**，不是可选项。

### 规律 2：Schema 演化在加速，但还没成为主流

7/9 支持多 Schema 选择，2/9（Agora、ANP）进一步支持运行时演化。方向很明确，但大多数协议还停在"出厂时定好几套格式"的阶段。

### 规律 3：发现机制明显滞后

在去中心化成为讨论热点的背景下，实际上绝大多数协议仍然依赖静态配置或集中式注册中心。如果"Agent 互联网（Internet of Agents）"真的到来，去中心化发现会成为瓶颈。

---

## 第四步：Agent 通信三难困境

论文引入了 Oxford 团队（Marro et al.）提出的 Agent Communication Trilemma：

**一个协议无法同时最大化这三个属性：**

| 属性 | 含义 |
|------|------|
| **通用性（Versatility）** | 能处理多样消息类型（文本、结构化数据、文件） |
| **效率（Efficiency）** | 最小化计算和网络开销 |
| **可移植性（Portability）** | 对 Agent 的实现和运行时没有苛刻要求 |

把 9 个协议放进这个三角形：

- **MCP**：极度侧重效率和可移植性。刚性 Schema、无状态、纯结构化载荷。无需协商，适合高频工具调用，但不擅长处理开放式 Agent 协作。
- **Agora / ANP**：极度侧重通用性。运行时 Schema 协商意味着大量 token 开销和延迟，效率很差。
- **A2A / LMOS / ACP**：居中。混合载荷 + Session State + 多预定义 Schema，够用而不昂贵。

**三难困境的实际含义**：这解释了为什么不会有一个协议赢得所有场景——本质是一道权衡数学题，没有同时满足三者的解。

---

## 第五步：未来走向联邦式分层协议栈

这是论文最重要的结论。

短期内，A2A 和 agntcy 把自己定位为"MCP 的扩展"，这制造了走向统一大协议的幻觉。但作者认为，这种整合不会走出一个垄断性赢家，而是会像 OSI 模型一样形成**分层结构**：

```
┌────────────────────────────────────────────────────────┐
│  上层：复杂多 Agent 协商                                  │
│  会话感知 + Schema 可演化 + 多轮辩论                      │
│  → Agora, ANP                                           │
├────────────────────────────────────────────────────────┤
│  中层：结构化工具执行                                     │
│  高效、刚性 Schema、无状态                               │
│  → MCP                                                  │
├────────────────────────────────────────────────────────┤
│  底层：能力发现                                           │
│  轻量、静态/去中心化、可索引                              │
│  → agents.json, LMOS                                    │
└────────────────────────────────────────────────────────┘
```

每一层做自己最擅长的事。发现层解决"我怎么知道你存在"；工具执行层解决"我怎么高效调用你"；协商层解决"我们怎么在没有预设格式的情况下合作"。

这和 TCP/IP 分层的历史逻辑一模一样：分层不是妥协，是合理的工程设计。

---

## 我的延伸：从这张地图到实际判断

论文给了一张分类地图，但有几个实践问题它没有直接回答。

### 现在选协议，标准是什么？

用这 5 个维度来问自己：

1. 我的 Agent 需要和**另一个 Agent** 对话，还是只调用**工具/API**？
   - 前者：A2A、ACP、LAP；后者：MCP
2. 任务是**单轮调用**还是**多轮协作**？
   - 单轮：stateless 协议够用；多轮：必须有 session state
3. 我能预先定义好所有的通信格式吗？
   - 能：多预定义 Schema 足够；不能，需要运行时演化：考虑 Agora 或 ANP
4. Agent 网络会不断扩展、动态加入新节点吗？
   - 会：发现机制很重要，优先考虑有注册中心或去中心化发现的协议

### 发现机制会成为下一个战场

当前最大的空白是去中心化发现。如果 Agent 网络真的要达到"Internet of Agents"的规模，不可能每个 Agent 都靠手动配置地址，也不可能永远依赖一个集中式注册服务（单点故障）。

接下来值得关注的问题：**谁会做出真正好用的去中心化 Agent 发现机制？** LMOS 是目前最接近的，但距离生产就绪还有距离。

### 最被忽视的缺口：隐私和合规

论文明确指出，9 个协议里**没有一个**系统性地解决了隐私保护、合规检查和策略执行。

这在当前看起来无关紧要，但当 Agent 开始在医疗、金融、HR 等敏感领域运行时，这个缺口会从技术问题变成法律问题。谁先在协议层面解决这个问题，谁就有先发优势。

### Schema 演化的代价被低估了

Agora 和 ANP 的运行时 Schema 协商听起来很酷，但实际成本很高：每次建立新连接都要先花 token 协商格式，延迟高、成本高。

短期内，这个能力更像是一个"后备选项"而不是默认路径。大多数生产环境 Agent 系统会继续用预定义 Schema，只在处理高度异构的动态场景时才启用协商机制。

---

## 给开发者的一句话总结

如果你现在要选 Agent 通信协议：
- **连工具/数据源** → MCP，成熟、生态最完整
- **Agent 之间对话** → A2A 或 ACP，有会话管理、结构完善
- **需要真正去中心化** → 等等，LMOS 方向对但还未成熟，Agora 和 ANP 适合研究场景
- **需要动态协商协议格式** → Agora 或 ANP，但要承担 token 开销

未来是分层的，不是赢家通吃的。这张分类地图帮你看清楚，你在用的协议属于哪一层、有什么代价、在哪里会遇到瓶颈。

---

论文原文：https://arxiv.org/abs/2606.19135

© 2026 Author: Mycelium Protocol

<!--EN-->

## The First Map of LLM Agent Communication Protocols: Why the Future Won't Be Winner-Takes-All

> Paper: **A Technical Taxonomy of LLM Agent Communication Protocols**
> Authors: Linus Sander, Habtom Kahsay Gidey (June 2026)
> arXiv: https://arxiv.org/abs/2606.19135

---

### Why This Paper Matters

The LLM agent communication protocol space has exploded in the past 18 months: MCP, A2A, ACP, ANP, Agora, agntcy... A new protocol every few weeks. But nobody had systematically asked: **what are the real differences between these protocols? Which dimensions actually matter? Will the field converge on one standard or fragment into many?**

This paper provides the first rigorous answer: a five-dimension taxonomy built from nine actively maintained open-source protocol implementations, derived through five structured empirical-conceptual iterations.

---

### The Nine Protocols

The paper selected protocols that are open-source, have working implementations (not just spec documents), and show real community adoption on GitHub:

| Protocol | Creator | Role |
|----------|---------|------|
| MCP | Anthropic | Agent-to-tool/data-source standard |
| A2A | Google | Agent-to-agent interoperability |
| LAP | LangChain | Unified RESTful API for agent deployment |
| agents.json | — | JSON spec for agent API discovery |
| Agora | Oxford | Decentralized collaboration, runtime schema negotiation |
| ANP | — | "The HTTP of the agentic web" |
| LMOS | Eclipse | Partially decentralized agent ecosystem infrastructure |
| ACP | BeeAI/IBM/Linux Foundation | RESTful open standard for agent communication |
| agntcy | — | OpenAPI extension for agent connectivity |

---

### Five Taxonomy Dimensions

**1. Counterparty** — who does the protocol connect to?
Agent / Context (tools, APIs, data) / Hybrid

**2. Payload** — what is the shape of the data?
Structured data & artifacts / Conversation-focused / Hybrid

**3. Interaction State** — does the protocol maintain session memory?
Stateless / Session State

**4. Discovery Mechanism** — how do agents find each other?
Static / Centralized / Partially centralized / Decentralized / Hybrid

**5. Schema Flexibility** — can the communication structure evolve?
Single schema / Multiple predefined schemas / Evolving (runtime negotiation)

---

### Key Findings

**Pattern 1: Agent-to-agent always means session state + hybrid payload (7/7)**
Without exception. These two properties are necessary conditions for agent-to-agent communication, not optional.

**Pattern 2: Schema evolution is trending but not yet mainstream**
7/9 support multiple predefined schemas. 2/9 (Agora, ANP) support runtime schema negotiation. The direction is clear, but most protocols are still in the "choose from pre-built options" phase.

**Pattern 3: Discovery is the laggard**
Despite "decentralized" being a popular buzzword, most protocols still rely on static configuration or centralized registries. Only LMOS genuinely incorporates decentralized peer-to-peer discovery.

---

### The Communication Trilemma

Drawing on Marro et al.'s Agora paper, the authors apply a trilemma: no protocol can simultaneously maximize **Versatility** (handling diverse message types), **Efficiency** (minimizing token and compute cost), and **Portability** (minimal adoption burden).

- **MCP**: high efficiency + portability, low versatility. Rigid schemas, stateless, structured payloads — optimal for high-frequency tool calls.
- **Agora / ANP**: high versatility, low efficiency. Runtime schema negotiation burns tokens on every new connection.
- **A2A / LMOS / ACP**: center of the triangle. Hybrid payloads, session state, multiple predefined schemas. Capable without being expensive.

This trilemma mathematically explains why no single protocol will dominate all use cases.

---

### The Future: Federated Layered Stack

The paper's central conclusion: rather than a monolithic winner-takes-all standard, the field will evolve toward a **federated, layered protocol stack**, mirroring the OSI networking model:

```
Top layer:     Schema-evolving multi-agent negotiation → Agora, ANP
Middle layer:  Structured tool execution               → MCP
Bottom layer:  Capability discovery                    → agents.json, LMOS
```

Each layer does what it does best. Discovery layer solves "how do I know you exist." Tool execution layer solves "how do I call you efficiently." Negotiation layer solves "how do we collaborate without a pre-agreed format."

---

### Open Research Gaps

1. **Decentralized discovery** — LMOS points the direction but isn't production-ready
2. **Privacy and policy enforcement** — none of the 9 protocols systematically address compliance, privacy safeguards, or policy execution in sensitive domains (healthcare, finance, HR)
3. **Schema negotiation cost** — runtime schema evolution burns tokens; better pre-negotiation caching and reuse mechanisms are needed

---

### Practical Protocol Selection Guide

| Situation | Recommended |
|-----------|-------------|
| Connecting to tools/APIs | MCP (mature, largest ecosystem) |
| Agent-to-agent dialogue | A2A or ACP (session management, structured) |
| Need decentralized discovery | Wait — LMOS direction correct but not mature |
| Need dynamic schema negotiation | Agora or ANP (accept token overhead) |

---

The future is layered, not winner-takes-all. This taxonomy gives you a map to understand which layer your current protocol belongs to, what trade-offs it makes, and where you'll hit walls.

Paper: https://arxiv.org/abs/2606.19135

© 2026 Author: Mycelium Protocol
