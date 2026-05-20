---
title: "软件层的退场与重构：AI-Native 时代，你的产品下一个用户是另一个 Agent"
titleEn: "The Retreat and Restructuring of the Software Layer: In the AI-Native Era, Your Next User Is Another Agent"
description: "软件层不是在消失，而是被重构为 agent 的调度内核。本文提炼 Karpathy Software 3.0 框架、六级交互演进台阶、LAAS 本地 AI 架构边界、成果计费商业模式转轨，以及三条值得长期下注的方向——协议层公民、领域数据飞轮、意图设计与品牌信任。"
descriptionEn: "The software layer isn't disappearing — it's being restructured into an agent orchestration kernel. This article distills Karpathy's Software 3.0 framework, the six-level interaction evolution ladder, LAAS local AI architecture boundaries, outcome-based billing transitions, and three long-term investment directions: protocol-layer citizenship, domain data flywheels, and intent design with brand trust."
pubDate: "2026-05-11"
updatedDate: "2026-05-11"
category: "Research"
tags: ["AI-Native", "LAAS", "MCP", "Software 3.0", "Karpathy", "Agent", "SaaS", "本地AI", "交互范式", "产业转型"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

**原文**：[软件层的退场与重构（完整版 Google Doc）](https://docs.google.com/document/d/1u0xO_VO99LlUIqkosqdd1hg2D-8T1CZYo7yakBhTe7s/edit?usp=sharing)

**结论先行（BLUF）**：软件层不是在"消失"，而是在被重构为 agent 的调度内核。三个命题必须分开讨论：**代码不会消失**（神经网络权重本身也是代码，只是不再由人手写）；**可见 GUI 与"以应用为单位"的交付正在解构**（这正在发生）；**SaaS 的座席计费模式正被"成果计费"替代**（争议最大，但已有早期实证）。

---

## Software 3.0：意图取代功能按钮

Andrej Karpathy 在 2025 年 6 月 16 日的 YC AI Startup School 演讲中系统提出了 **Software 3.0** 框架：LLM 是新一代操作系统，上下文窗口即 RAM，模型权重即 CPU，提示词即编程。

> "LLMs are a new kind of computer, and you program them in English."
> —— Andrej Karpathy, [YC AI Startup School 2025](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again)

最小交互单位从"功能按钮"升格为**"意图表达"**——小饭店老板拍张菜单照说一句话，直达精修海报成品；中间所有工具链（OCR、前端、API）被收敛进 LLM 调度内核，传统脚手架整体消失。

Karpathy 同时给出了对软件公司最重要的判断：

> "LLMs are the new primary consumer/manipulator of digital information. Build for agents."
> —— Andrej Karpathy, [AI Startup School 2025](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again)

---

## 交互范式：六级台阶，L4 是过渡，L5 是终局

| 级别 | 形态 | 代表产品 | 现状 |
|---|---|---|---|
| L1 | App 图标 + 触屏点选 | iOS/Android | 存量主流 |
| L2 | Chatbot + 单步工具调用 | ChatGPT plugins (2023) | 已普及 |
| L3 | 对话 + 生成式 UI | Claude Artifacts, ChatGPT Canvas | 正在普及 |
| L4 | Operator 代点鼠标 | Anthropic Computer Use, OpenAI Operator | Demo→早期落地 |
| L5 | **Agent ↔ 服务协议直连** | **MCP / A2A / NLWeb** | **事实标准形成期** |
| L6 | 意图执行 + 极简验证层 | — | 愿景 |

**关键判断**：L4"截图+点击"只是过渡——一旦服务端普遍提供 MCP/A2A 接口，AI 就没必要再点鼠标。Stripe、Notion、Linear、Asana、Intercom 已发布官方 MCP server，绕过 GUI 直接对话。[Anthropic 于 2024-11-25 发布 MCP](https://www.anthropic.com/news/model-context-protocol)，OpenAI、Google、Microsoft 在 2025 年 3–5 月相继原生支持，18 个月内成为事实标准。

---

## 本地 AI（LAAS）：三层架构，不是纯本地

LAAS 的三个真问题成立：隐私与数据主权、低延迟与离线能力、token 经济成本。但更精确的答案不是"纯本地"，而是：

**端侧小模型 + 可验证云（Apple PCC 模式）+ 协议互通**

[Apple Private Cloud Compute](https://security.apple.com/blog/private-cloud-compute/) 是行业第一个把"云端隐私可证明"工程化的尝试——硬件用 Apple Silicon 服务器，运行时不存储用户数据，外部可远程验证。端侧能力边界（2026 年中）：

- **手机**（iPhone 17 Pro 等）：1B–4B 模型，摘要、改写、单步工具调用
- **笔记本**（MacBook Air M4 / Copilot+ PC）：3B–8B，短链 agent、IDE 内补全
- **工作站**（Mac Studio M3 Ultra）：30B–70B，接近 Claude Code 级体验

超长上下文（>1M tokens）、复杂 reasoning、多 agent 协作调度仍须云端。

---

## 商业模式转轨：成果计费正在发生

Foundation Capital 2024 年估算：[全球服务市场约 2.4 万亿美元，软件市场约 4000 亿——即每 1 美元软件支出对应 6 美元服务支出](https://foundationcapital.com/ai-service-as-software/)。若 AI 能将服务相当部分"软件化"，市场重估将极其剧烈。

早期实证：

- **Sierra**（CEO Bret Taylor）：按"每解决一次客服对话"计费，而非座席数。详见 [τ²-bench 方法论](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)
- **Salesforce Agentforce**：每次对话 2 美元；Benioff 公开宣布 2025 年全年停止招聘软件工程师
- **Cognition Labs Devin**：以 ACU（Agent Compute Unit）计费

---

## 三条值得长期下注的方向

**① 协议层公民**：把核心能力暴露为 MCP server——这是 agent 时代的"SEO"，决定你的服务是否对 agent 可见。今天没有 MCP server，等于被 agent 时代"看不见"。参见 [Google A2A Protocol](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)。

**② 领域数据飞轮**：通用模型同质化是必然，但"你拥有而别人没有的领域数据 + 持续生成的高质量行为 trace"，是 LAAS 时代真正的护城河。[Anthropic Economic Index](https://www.anthropic.com/economic-index) 显示计算机与数学类任务占 Claude 使用的 37.2%——领域专精仍有巨大空间。

**③ 意图设计与品牌信任**：技术执行力被 AI 抹平后，用户会把意图交给"他最信任的品牌"。品牌的角色将从"营销表层"重回"产品核心"——这是对"craftsmanship 不可替代"（[DHH 的持续论点](https://world.hey.com/dhh)）的另一面诠释。

---

## 结语

软件不会消失，软件的"边界"会消失。当代码本身被工具化，**"理解一个复杂系统、定义清楚要做什么、并对结果负责"** 这件事比写代码本身更稀缺，也更有价值。

对软件从业者的实际建议：

1. 立刻把核心能力暴露为 MCP server——你产品的下一个主用户是另一个 agent
2. 把 PRD/Spec 当作一等代码工件管理，它将成为新研发流程的源头
3. 新增 agent threat model：把 prompt injection、tool poisoning 加入安全审查清单（[Invariant Labs 2025-04 MCP 安全报告](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)）
4. 认真对待"Operator 类是过渡形态"——战略押注在"服务对 agent 友好"而非"AI 替人点鼠标"

---

**主要参考**

- Karpathy, "Software Is Changing (Again)", YC AI Startup School 2025-06-16 — [链接](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again)
- Anthropic, Model Context Protocol 发布 2024-11-25 — [链接](https://www.anthropic.com/news/model-context-protocol)
- Anthropic, "Building Effective Agents" 2024-12-19 — [链接](https://www.anthropic.com/research/building-effective-agents)
- Apple, Private Cloud Compute 技术说明 2024-06 — [链接](https://security.apple.com/blog/private-cloud-compute/)
- Google, A2A Protocol 发布 2025-04-09 — [链接](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- Foundation Capital, "AI is leading a service as software paradigm shift" 2024-04-19 — [链接](https://foundationcapital.com/ai-service-as-software/)
- METR, Measuring AI Ability to Complete Long Tasks 2025-03 — [链接](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- Simon Willison, "Not all AI-assisted programming is vibe coding" 2025-03-19 — [链接](https://simonwillison.net/2025/Mar/19/vibe-coding/)
- Anthropic Economic Index 2025-02 — [链接](https://www.anthropic.com/economic-index)
- Geoffrey Litt, "Malleable Software in the Age of LLMs" 2023 — [链接](https://www.geoffreylitt.com/2023/03/25/llm-end-user-programming.html)
- Maggie Appleton, "Home-Cooked Software and Barefoot Developers" 2024 — [链接](https://maggieappleton.com/home-cooked-software)
- Sierra, τ²-bench — [链接](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)
- Apollo Research, Scheming Reasoning Evaluations 2024-12 — [链接](https://www.apolloresearch.ai/research/scheming-reasoning-evaluations)
- Invariant Labs, MCP Tool Poisoning Attacks 2025-04 — [链接](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: The software layer isn't disappearing — it's being restructured into an agent orchestration kernel. Three propositions must be separated: code won't disappear (neural network weights are also code, just no longer hand-written by humans); visible GUI and app-as-delivery-unit are being deconstructed (this is happening now); SaaS seat-based billing is being replaced by outcome-based billing (most contested, but with early empirical proof).

---

## Software 3.0: Intent Replaces Feature Buttons

Andrej Karpathy's [YC AI Startup School keynote (2025-06-16)](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again) systematically introduced the **Software 3.0** framework: LLMs are the new OS — context window is RAM, model weights are CPU, prompting is programming.

The minimum interaction unit has upgraded from "feature button" to **"intent expression"** — a restaurant owner photographs a menu and says one sentence, directly producing a polished social media post; all intermediate tooling (OCR, frontend, APIs) collapses into the LLM orchestration kernel.

> "LLMs are the new primary consumer/manipulator of digital information. Build for agents."

---

## Interaction Paradigms: Six Levels, L4 Is Transitional, L5 Is the Endgame

| Level | Form | Representative Products | Status |
|---|---|---|---|
| L1 | App icon grid + touch | iOS/Android | Existing mainstream |
| L2 | Chatbot + single tool calls | ChatGPT plugins (2023) | Widespread |
| L3 | Chat + Generative UI | Claude Artifacts, ChatGPT Canvas | Spreading |
| L4 | Operator "click-for-me" agents | Computer Use, OpenAI Operator | Demo → early deployment |
| L5 | **Agent ↔ Service protocol direct connect** | **MCP / A2A / NLWeb** | **De facto standard forming** |
| L6 | Intent execution + minimal verification | — | Vision |

**Key judgment**: L4 "screenshot+click" is transitional — once services universally provide MCP/A2A interfaces, AI has no reason to click mice. Stripe, Notion, Linear, Asana, Intercom have already released official MCP servers, bypassing GUI for direct dialogue. [Anthropic released MCP on 2024-11-25](https://www.anthropic.com/news/model-context-protocol); OpenAI, Google, and Microsoft natively supported it within 18 months — a rare instance of an open standard achieving de facto monopoly so quickly.

---

## Local AI (LAAS): Three-Layer Architecture, Not Pure Local

LAAS's three genuine problems are valid: privacy/data sovereignty, low-latency/offline capability, unsustainable token economics. But the accurate answer isn't "pure local" — it's:

**On-device small models + verifiable cloud (Apple PCC model) + protocol interoperability**

[Apple's Private Cloud Compute](https://security.apple.com/blog/private-cloud-compute/) is the industry's first engineering attempt at "provably private cloud computation." On-device capability ceilings (mid-2026):

- **Phone** (iPhone 17 Pro): 1B–4B models, summarization, single-step tool calls
- **Laptop** (MacBook Air M4): 3B–8B, short-chain agents, IDE completion
- **Workstation** (Mac Studio M3 Ultra): 30B–70B, near Claude Code-level experience

Ultra-long context (>1M tokens), complex reasoning, and multi-agent orchestration still require cloud.

---

## Business Model Transition: Outcome Billing Is Happening

[Foundation Capital estimates](https://foundationcapital.com/ai-service-as-software/): global services market ~$2.4T, software market ~$400B — every $1 software spend corresponds to $6 service spend. If AI can "software-ize" significant portions of services, market repricing will be extreme.

Early proof: **Sierra** (CEO Bret Taylor) bills per "resolved customer service conversation," not per seat. **Salesforce Agentforce** charges $2 per conversation; Benioff publicly announced halting all software engineer hiring in 2025.

---

## Three Long-Term Investment Directions

**① Protocol-layer citizenship**: Expose core capabilities as MCP servers — this is the "SEO" of the agent era. No MCP server today = invisible to agents tomorrow.

**② Domain data flywheel**: General models will commoditize. "Domain data you own that others don't + high-quality behavior traces you continuously generate" is the moat of the LAAS era.

**③ Intent design and brand trust**: When technical execution is leveled by AI, users give their intent to the brand they trust most. Brand returns from "marketing surface" to "product core."

---

**Key References**

- Karpathy, YC AI Startup School 2025 — [link](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again)
- Anthropic, MCP release 2024-11 — [link](https://www.anthropic.com/news/model-context-protocol)
- Anthropic, "Building Effective Agents" — [link](https://www.anthropic.com/research/building-effective-agents)
- Apple, Private Cloud Compute — [link](https://security.apple.com/blog/private-cloud-compute/)
- Google, A2A Protocol — [link](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- Foundation Capital, "Service as Software" — [link](https://foundationcapital.com/ai-service-as-software/)
- METR, Long Task Measurement 2025-03 — [link](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- Invariant Labs, MCP Tool Poisoning — [link](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
