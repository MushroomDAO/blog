---
title: "OpenAI 白皮书：如何治理 Agentic AI 系统"
titleEn: "OpenAI Whitepaper: Practices for Governing Agentic AI Systems"
description: "OpenAI 2023年底发布的治理白皮书，系统阐述了 Agentic AI 系统的三方责任模型、最小权限原则和人类监督机制，为 AI 代理的安全部署提供了实践框架。"
descriptionEn: "OpenAI's late-2023 governance whitepaper systematically outlines a three-party responsibility model, minimal footprint principle, and human oversight mechanisms for safe deployment of agentic AI systems."
pubDate: 2026-05-21
updatedDate: 2026-05-21
category: Research
tags: ["Agentic-AI", "AI-Governance", "OpenAI", "AI-Safety", "Multi-Agent"]
heroImage: "../../assets/banner-future-is-now.jpg"
---

> **BLUF**：OpenAI 于 2023 年 12 月发布的白皮书《Practices for Governing Agentic AI Systems》，提出了一套针对 Agentic AI 系统的治理框架——以"三方责任"为基础，以"最小权限"为原则，以"人类监督"为底线，为当前 AI 代理大规模落地提供了可操作的参考规范。

> 📌 原文官方页面：
> https://openai.com/index/practices-for-governing-agentic-ai-systems/
>
> 📌 原文 PDF 地址：
> https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf
>
> 📌 学术检索（Semantic Scholar）：
> https://www.semanticscholar.org/paper/Practices-for-Governing-Agentic-AI-Systems-Shavit-Agarwal/0002c42e8d7bfeafc431c4ed9f6318f223bbf58b
>
> 作者：Yonadav Shavit、Sandhini Agarwal、Miles Brundage 等（OpenAI，2023 年 12 月）

---

## 什么是 Agentic AI 系统？

这篇白皮书首先明确定义了研究对象：**Agentic AI 系统**（代理式 AI 系统）是指能够在真实世界中自主规划并执行多步骤任务的 AI，其行动具有真实的物理或数字后果。

与传统的问答式 AI（给一个输入、等一个输出）不同，Agentic AI 具备以下特征：

- 自主制定行动序列，无需每步人工审批
- 调用外部工具（搜索引擎、代码执行环境、API、文件系统等）
- 在多轮交互中维持目标状态，持续推进任务
- 行动结果往往不可撤销（发送邮件、提交代码、进行支付）

这种能力让 Agentic AI 在自动化任务方面有极大价值，但同时也引入了全新的安全治理挑战。

## 三方责任模型：谁该对什么负责？

白皮书的核心架构是**三方责任模型**，将 Agentic AI 的生态拆解为三个角色：

**1. AI 开发者（Developers）**
负责构建并训练底层模型，制定能力边界和安全护栏。开发者在系统设计层面就决定了模型的哪些能力可以开放，哪些必须限制。

**2. 运营者（Operators）**
在开发者能力边界之内，将 AI 部署到具体场景中的企业或个人。运营者有权在开发者允许的范围内配置 AI 行为，例如赋予更多或更少的工具调用权限，也有责任确保部署合规。

**3. 用户（Users）**
最终与 AI 代理交互的人。用户可以在运营者允许的范围内调整代理行为，但不能超越运营者设定的边界。

这一分层结构本质上形成了**权限委托链**：开发者 → 运营者 → 用户，每一层只能在上一层授权的范围内行动，不能超越。

这个模型解决了一个长期模糊的问题：当 AI 代理出错时，谁来承担责任？答案是——按照权限的授予层级，各方在其控制范围内承担对应责任。

## 最小权限原则：代理不该拥有过多能力

白皮书最具实践价值的部分是对"最小权限原则"（Minimal Footprint）的系统阐述，包含四条具体操作准则：

**1. 只申请完成当前任务所需的权限**
AI 代理不应在任务开始时就获取所有可能用到的权限。正确做法是按需申请，任务完成后释放权限。

**2. 优先选择可逆操作，避免不可逆操作**
在有多种方案可选时，代理应优先采用结果可撤销的方式（如将文件移到垃圾桶而非直接删除）。当不可逆操作不可避免时，需在执行前明确通知用户。

**3. 不确定时主动确认**
当任务范围模糊或超出预期时，代理应暂停并向用户确认意图，而不是自行猜测并继续执行。

**4. 不累积超出任务需要的资源和影响力**
代理不应利用执行任务的机会积累额外权限、存储敏感数据或建立不必要的外部连接。

这四条准则看似简单，但在工程实现层面有相当难度。它要求系统设计者从一开始就将权限最小化作为硬性约束，而非事后补丁。

## 人类监督：如何维持"人在环路"？

随着代理系统自动化程度提高，维持有效的人类监督（Human Oversight）成为核心挑战。白皮书提出了几个具体机制：

**分级审批**：对不同风险级别的操作设置不同的自动化程度。低风险操作（查询信息）可以全自动；中等风险操作（发送通知）可在用户事后确认；高风险操作（资金划转、删除数据）必须事前审批。

**行动日志与可审计性**：代理执行的每一步操作都应留下完整记录，便于事后审计和责任追溯。这一点在监管合规场景（金融、医疗、法律）中尤为重要。

**中断与回滚机制**：系统应为用户提供随时中断代理任务的手段，并在可能的情况下支持回滚到任务开始前的状态。

**异常行为检测**：开发者和运营者应监控代理是否出现超出预期的行为模式（如尝试申请额外权限、访问非授权资源），并设置相应告警。

## 多代理协作中的信任问题

白皮书特别讨论了**多代理（Multi-Agent）场景**中的新挑战，这是当前 AI 系统实践中最前沿也最复杂的问题。

当一个 AI 代理（编排者/Orchestrator）调用另一个 AI 代理（子代理/Subagent）执行任务时，会出现：

- **信任层级混乱**：子代理如何验证指令来自合法的编排者，而非恶意注入？
- **提示注入攻击**（Prompt Injection）：恶意外部内容（网页、文档）可能伪装成指令欺骗代理执行非预期操作。
- **责任链断裂**：多代理链路越长，某一环节出错时追溯责任越困难。

白皮书建议：子代理不应默认信任编排者的所有指令，而应建立**指令认证机制**，验证指令来源的合法性。同时，编排者对子代理的权限授予也应遵循最小权限原则——不能因为是"机器对机器"的通信就放开所有约束。

## 社会层面的考量

白皮书最后一部分从单一系统上升到**生态系统治理**视角，提出了几个宏观层面的问题：

- **标准化**：不同开发者的代理系统之间需要互操作标准，否则企业难以在跨平台场景中部署多代理系统。
- **行业协调**：代理 AI 的安全边界不能由单一公司决定，需要行业协作形成共识规范。
- **监管适配**：现有法律法规（数据保护、金融监管、医疗合规）大多针对人类行为者设计，需要更新以适应 AI 代理这一新的行动主体。

## 这份白皮书的价值与局限

**价值**：这是 2023 年底 AI 治理领域少有的**系统性实践框架**，不停留于原则声明，而是给出了可供工程师和产品团队参考的具体规范。三方责任模型和最小权限原则已被后续多个 AI 安全规范文件引用。

**局限**：白皮书本身偏向规范描述，对如何技术实现这些原则（尤其是动态权限管理、多代理信任链）涉及较少。随着 AI 代理能力快速迭代，部分具体建议可能需要持续更新。

**FAQ**

**Q：这篇白皮书与 OpenAI 的其他安全文件有何关系？**
A：这是 OpenAI 针对 Agentic AI 场景专门发布的治理框架文件，与其通用安全政策（Usage Policy）和模型能力说明文件互补，共同构成 OpenAI 的安全治理体系。

**Q：最小权限原则在实际开发中如何落地？**
A：工程上通常通过动态权限申请（OAuth 范围最小化）、操作沙箱、任务结束后自动权限回收、以及操作前后状态快照（支持回滚）来实现。

**Q：多代理信任问题目前有成熟解决方案吗？**
A：目前仍是研究热点。实践中常见方案包括：固定编排者白名单、加密签名指令、限制子代理的工具调用范围等，但尚无行业统一标准。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: OpenAI's December 2023 whitepaper on governing agentic AI systems establishes a three-party responsibility model (developers, operators, users), a minimal footprint principle, and concrete human oversight mechanisms — providing a practical governance framework as AI agents move into large-scale deployment.

> 📌 Official page:
> https://openai.com/index/practices-for-governing-agentic-ai-systems/
>
> 📌 PDF:
> https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf
>
> Authors: Yonadav Shavit, Sandhini Agarwal, Miles Brundage et al. (OpenAI, December 2023)

## What Are Agentic AI Systems?

The paper defines agentic AI systems as AI that autonomously plans and executes multi-step tasks with real-world consequences — calling external tools, maintaining goal state across turns, and taking actions that are often irreversible (sending emails, executing code, making payments).

## Three-Party Responsibility Model

The core governance architecture divides the ecosystem into three roles:

- **Developers**: build the underlying model; set capability limits and safety guardrails at the design level
- **Operators**: deploy agents into specific contexts within developer-set limits; responsible for compliant configuration
- **Users**: interact with agents within operator-set limits

This creates a permission delegation chain: developers → operators → users, each layer acting only within the authority granted by the layer above.

## Minimal Footprint Principle

The most actionable section covers four concrete practices:

1. Request only permissions needed for the current task
2. Prefer reversible over irreversible actions; warn users before irreversible steps
3. Pause and confirm with users when task scope is ambiguous
4. Do not accumulate resources, data, or influence beyond what the task requires

## Human Oversight Mechanisms

The paper recommends tiered approval (full automation for low-risk actions, pre-approval for high-risk ones), complete action logs for auditability, interrupt/rollback mechanisms, and anomaly detection for out-of-scope behavior.

## Multi-Agent Trust

In orchestrator–subagent chains, the paper calls for instruction authentication (subagents should not blindly trust orchestrators), minimal footprint for inter-agent permissions, and resistance to prompt injection attacks from external content.

## Societal Considerations

The paper concludes with calls for interoperability standards between agent systems from different developers, industry coordination on safety norms, and regulatory adaptation to treat AI agents as a new class of actors.

## Assessment

This whitepaper offers a systematic, engineering-oriented governance framework that has influenced subsequent AI safety standards. Its limitations: sparse technical implementation guidance, and the rapidly evolving agent capability landscape means some specifics will need ongoing revision.

**FAQ**

**Q: How does this relate to OpenAI's other safety documents?**
A: It complements OpenAI's general Usage Policy and model documentation, focusing specifically on the governance challenges unique to agentic (multi-step, tool-using) AI systems.

**Q: Is the minimal footprint principle technically enforceable?**
A: Yes — via dynamic OAuth scope minimization, sandboxed execution environments, automatic permission revocation after task completion, and state snapshots for rollback. None of these are trivial to implement at scale.

**Q: Are there industry standards for multi-agent trust yet?**
A: No unified standard exists. Common practices include fixed orchestrator allowlists, cryptographically signed instructions, and restricted tool access for subagents — but the field is actively evolving.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
