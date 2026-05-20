---
title: "软件公司转型：如何开发 Agent？一线团队的 8 步流程与 6 条避坑建议"
titleEn: "Software Company Transformation: How to Build Agents — 8-Step Process and 6 Hard-Won Lessons from Leading Teams"
description: "业内公认的 agent 开发「教科书」只有两份：Anthropic 的 Building Effective Agents 和 OpenAI 的 Practical Guide。本文在此基础上还原头部团队（Sierra、Devin、Cursor）实际跑的 8 步流程，给出 agent 分类的两个正交维度，以及「eval-first」「工具设计 > prompt 工程」等 6 条经反复踩坑验证的具体建议。"
descriptionEn: "The industry's recognized agent development bibles are just two: Anthropic's Building Effective Agents and OpenAI's Practical Guide. This article builds on them to reconstruct the actual 8-step process run by leading teams (Sierra, Devin, Cursor), provides two orthogonal dimensions for classifying agents, and delivers 6 battle-tested lessons including eval-first and tool design over prompt engineering."
pubDate: "2026-05-11"
updatedDate: "2026-05-11"
category: "Research"
tags: ["Agent开发", "AI工程", "MCP", "Eval", "Anthropic", "OpenAI", "软件转型", "工具设计", "Guardrails", "Observability"]
heroImage: "../../assets/banner-org-ai-transformation.jpg"
---

**结论先行（BLUF）**："做 agent"这件事有没有标准答案？有，但被大量团队跳过的是**第一步**——先用 workflow，只在确实需要时才上 agent。Anthropic 的核心建议是：能用 workflow 解决的，绝对不要用 agent，因为 agent 把可控性、延迟、成本、调试难度全部放大。本文还原头部团队实际跑的 8 步流程，给出 agent 分类框架，以及反复踩坑后验证的 6 条具体建议。

---

## 一、当前的「标准流程」：先认清两份权威文档

业内可以称得上"教科书"的就两份：

- **Anthropic 的 [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)（2024-12-19）**：核心贡献是把"workflow"和"agent"严格区分开。workflow 是人预先编排好的流程（其中某些步骤由 LLM 完成）；agent 是 LLM 在循环里自己决定下一步做什么。**第一原则：能用 workflow 解决的，绝对不要用 agent。**
- **OpenAI 的 [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)（2025）**：补足了 Anthropic 偏理论的部分，落到具体步骤——选模型 → 写工具 → 加 guardrails → 编排 → 部署。

两份文档之外，**Cognition Labs（Devin 团队）的 [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)** 和 **Sierra 的 [τ-bench 论文](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)** 是把"实际跑起来踩过的坑"写得最透的，建议直接读原文。

---

## 二、可执行的 8 步流程

这是 2026 年中头部团队（Sierra、Decagon、Harvey、Devin、Cursor 等）实际跑的流程：

### 1. 任务定义（最容易被跳过、最关键）

明确三件事：① agent 的"任务边界"（哪些不做？）；② "成功"如何定义（人来判？规则判？另一个 LLM 判？）；③ 失败时怎么办（兜底、升级、回滚）。这一步若含糊，后面所有 eval 都会扯皮。

### 2. 选 workflow 还是 agent

按 Anthropic 框架做决策树：步骤是否可枚举？工具是否固定？答错的代价多高？**高代价 + 不可枚举 才上 agent**；其他先用 workflow（prompt chaining、routing、parallelization）。

### 3. 模型选型（eval 驱动，不是基于声誉）

建议至少跑两轮：① 在 30–50 条代表性任务上测 SOTA 模型；② 在同一批任务上测 cost-effective 模型（Haiku 4.5、Gemini Flash、GPT-5 mini 等）。**很多任务上小模型 + 好工具 > 大模型 + 烂工具。**

### 4. 工具设计（这才是真正的核心，比 prompt 更重要）

- 工具的 schema 用对 LLM 友好的命名（动词 + 名词，参数名自解释）
- 错误信息必须可读且可恢复（"file not found, did you mean X?" 比 stack trace 好）
- 副作用要明确标注（read-only vs write，可逆 vs 不可逆）
- 工具数量控制：超过约 20 个工具，模型选择准确率会显著下降，需要分层 / namespacing
- 优先用 [MCP server](https://modelcontextprotocol.io/) 化，便于复用

### 5. 评估集（eval set）建立

- 至少 50–200 条任务，覆盖典型 + 边缘 + 对抗
- 每条任务都有 ground truth 或 LLM-as-judge 的判分标准
- 跑全 eval 的成本要可控（< $5–$50/run），不然你不会跑
- 工具栈：LangSmith / Braintrust / Langfuse / OpenAI Evals / Anthropic Inspect

### 6. Guardrails（input/output 双层）

- **输入层**：prompt injection 检测（Anthropic 分类器、Lakera Guard、Llama Prompt Guard）
- **输出层**：PII 脱敏、格式验证、调用次数/总 cost 上限、关键操作必须 human-in-the-loop
- 计费上限是真的会救命的——很多团队被 agent"无限循环"烧过几千美元

### 7. Observability（trace + 成本可见）

每个 agent 调用都要可以回放：哪个 prompt、调用了什么工具、传了什么参数、返回了什么、用了多少 token、花了多少钱。[OpenTelemetry 已标准化 `gen_ai.*` semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)，新项目直接接 OTel 不要重造轮子。

### 8. 灰度上线 + 持续迭代

- **第一个月**：1–5% 流量，必须人工 review 所有 trace 的随机采样
- 失败 trace 直接进 eval set（这是最便宜的 eval 扩展方式）
- 每周 retrain prompt / 调工具 / 改 guardrails
- **关键指标**：task completion rate、handoff rate（升级给人）、cost per resolved task、user reversal rate（用户撤回 agent 的操作）

---

## 三、Agent 分类：两个维度看清楚

分类有意义是因为**不同类的 agent 开发重心完全不同**。

### 维度 A：按自主度

| 类型 | 形态 | 典型用例 | 开发重心 |
|---|---|---|---|
| **Workflow（编排式）** | LLM 是流水线中的一个 step | 文档分类、信息抽取、邮件路由 | prompt 工程 + 流程图 |
| **Single-agent loop** | 一个 LLM 在 think-act-observe 循环里 | 客服、问答 + 工具调用、研究助手 | 工具设计 + 上下文管理 |
| **Multi-agent orchestration** | 主 agent 调度子 agent | 复杂研究、跨域任务 | agent 之间的接口 + 上下文传递 |
| **Computer-use agent** | 截图 + 鼠键操作 GUI | 处理遗留系统、跨 App 自动化 | 视觉理解 + 错误恢复 + 沙箱 |

**Cognition 的 [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) 是个重要警告**：做 Devin 的实战结论是，在大多数场景下，**单 agent + 子 agent 工具化（而不是真正的多 agent 协作）更可靠**。多 agent 看起来 sexy，但 context loss 和 coordination overhead 会让可靠性指数级下降。

### 维度 B：按业务形态

| 类别 | 代表产品 | 开发流程的特殊之处 |
|---|---|---|
| **Coding agent** | Devin、Claude Code、Cursor、Codex cloud | 沙箱执行 + git diff 作为基本通货；eval 用 SWE-bench Verified |
| **客服 / 业务 agent** | Sierra、Decagon、Crew | 强 outcome-based eval（每对话解决率）；与 CRM/工单系统深度整合 |
| **Research / answer agent** | Perplexity、ChatGPT Deep Research | 重点是搜索 + 引用追溯；eval 偏 GAIA、BrowseComp |
| **垂直专家 agent** | Harvey（法律）、Hebbia（金融） | 领域语料 + 领域评估专家参与；强合规审计 |
| **个人助理 agent** | Apple Intelligence、Google Astra | 端侧/混合推理 + 长期记忆 + 跨 App 权限 |
| **Browser / GUI agent** | OpenAI Operator、Computer Use | 沙箱浏览器 + 视觉 + 误操作恢复；eval 用 OSWorld / WebArena |
| **Workflow automation** | Zapier AI、n8n + AI、Lindy | 强 trigger / scheduler；面向"流程"而非"对话" |

**实操含义**：如果你要做客服 agent，去抄 Sierra；做 coding agent 去看 Cognition 和 Anthropic Claude Code 工程博客；做企业搜索去看 Glean、Harvey case study。**跨品类抄经验是个常见错误**——把客服的"对话回合数"指标拿去衡量 coding agent 是没意义的。

---

## 四、6 条具体建议

基于业内一线团队反复踩过的坑：

**1. Eval-first，不是 prompt-first。** 先有 50 条带 ground truth 的任务，再开始写 prompt。[Hamel Husain 的 *Your AI product needs evals*](https://hamel.dev/blog/posts/evals/) 是这条原则的最佳论述。没有 eval 的 agent 项目，本质上是在凭直觉做产品。

**2. 工具设计 > prompt 工程。** 当你觉得"prompt 怎么调都不行"时，90% 的情况是工具设计出了问题——工具粒度太粗/太细、错误信息糟糕、副作用模糊。改工具比改 prompt 收益高 10 倍。

**3. 上下文管理就是新的内存管理。** Karpathy 的"context window is RAM"比喻很对：超过 30K token 的上下文要主动 summarize、prune、segment；超过 200K 要考虑外部 memory store（Letta、Mem0、Zep 等）。**长 agent loop 最常见的失败模式不是模型变笨，而是上下文被无关 trace 污染。**

**4. Human-in-the-loop 不是"暂时妥协"，是产品设计。** 关键不是"何时让人介入"，而是"如何让介入成本最低"——确认按钮 vs 三选一 vs 自由文本。LangChain 的 Agent Inbox 模式是参考样本。

**5. Cost / latency 是产品决策，不是工程优化。** "每解决任务的成本"决定了你能不能 outcome-based 定价；"首响应延迟"决定了用户体感。这两条要在产品定义阶段就锁定预算，不要等上线才发现一次会话烧 $5。

**6. 把 prompt injection 当 SQL injection 那样对待。** 任何把外部内容（邮件、网页、用户上传文件）放进 context 的 agent，都默认是"不可信输入"。[Simon Willison 的 prompt injection 系列](https://simonwillison.net/tags/prompt-injection/)是必读；Anthropic 披露的 indirect prompt injection 红队案例值得每个 agent 团队复盘。

---

## 五、3–5 年的演化方向

**短期（已经在发生）**：

- **流程标准化**：spec → eval → tool design → guardrails → deploy 会成为像 CI/CD 一样的标准 pipeline
- **MCP 成事实标准**：自己写 function calling schema 会变成 antipattern，所有工具都通过 [MCP](https://modelcontextprotocol.io/) 暴露
- **Eval 商业化**：会出现像 SOC2 / ISO 那样的"agent 评估认证"，由第三方机构提供（METR、Scale AI、Apollo Research 等已经在做）

**中期（2027–2030 大概率发生）**：

- **Self-improving agents**：production traces 自动进 eval、自动 fine-tune prompt 与 tool 描述（DSPy、TextGrad 是早期信号），人工调 prompt 会被视为体力活
- **Agent OS 抽象层**：今天每家都在重复实现"tool loop + retry + observability + guardrails"，这一层会被 OS 化（Cloudflare Workers AI、Vercel AI、Modal Agents、Bedrock AgentCore 在抢这个位置）
- **多 agent 真正可行**：当 A2A 协议成熟、context handoff 标准化，跨厂商 agent 协作会从今天的"demo"变成"工作流"

**长期（2030 之后，不确定性大）**：

- **"Agent 即一等公民"的研发流程**：写新功能时，第一步不是设计 UI 而是定义 agent 接口
- **角色重组**：PM 演化为"agent designer + eval owner"；QA 演化为"agent eval engineer"；Engineer 分化为"platform engineer（搭 agent infra）"和"agent operator（运营、迭代特定 agent）"

---

## 最后：今天立项的顺序

如果你的团队**今天**要立项做 agent，按这个顺序：

1. **先复刻一个已有 agent**（用 Anthropic SDK 或 OpenAI Agents SDK 做最简客服或文档分析 agent），跑通 eval 流程——约 2 周
2. **再回头看业务**，找出 3 个候选场景，按"失败代价 × 频率"排序
3. **选失败代价低、频率高的那个先做**（典型如内部文档问答、合同条款抽取、邮件分类），先用 workflow 而不是 agent
4. **跑 3 个月有 trace 数据**之后，再考虑要不要升级到真正的 agent loop

跳过 1–3 直接做"AGI-like 通用 agent"是 2024–2025 最常见的烧钱失败模式。这不是悲观，是现在头部团队都同意的常识。

---

**主要参考**

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI, A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Cognition, Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- [Sierra, τ-bench benchmarking AI agents](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)
- [Hamel Husain, Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [Simon Willison on prompt injection](https://simonwillison.net/tags/prompt-injection/)
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Does building agents have a standard answer? Yes — but the most commonly skipped step is the first one: use a workflow first, only escalate to an agent when genuinely necessary. Anthropic's core advice: if a workflow can solve it, never use an agent, because agents amplify controllability challenges, latency, cost, and debugging difficulty. This article reconstructs the actual 8-step process run by leading teams, provides an agent classification framework, and delivers 6 battle-tested lessons.

---

## I. The "Standard Process": Two Authoritative Documents

The only two documents that can be called industry "textbooks":

- **Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (2024-12-19)**: Core contribution is strictly distinguishing "workflow" (human-pre-orchestrated flow with LLM steps) from "agent" (LLM decides its own next action in a loop). **First principle: never use an agent when a workflow can solve it.**
- **OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (2025)**: Fills in Anthropic's theoretical gaps with concrete steps — model selection → tool writing → guardrails → orchestration → deployment.

Beyond these two, **Cognition Labs' [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)** and **Sierra's [τ-bench paper](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)** are the most transparent accounts of real production lessons learned.

---

## II. The 8-Step Executable Process

What leading teams (Sierra, Decagon, Harvey, Devin, Cursor) actually run in 2026:

**1. Task Definition (Most Skipped, Most Critical)**  
Clarify: ① task boundary (what won't the agent do?); ② definition of "success" (human judgment? rules? LLM-as-judge?); ③ failure protocol (fallback, escalation, rollback). Ambiguity here makes all downstream evals contentious.

**2. Workflow vs. Agent Decision**  
Apply Anthropic's decision tree: Are steps enumerable? Are tools fixed? How high is the cost of a wrong answer? **Only use an agent for high-stakes + non-enumerable tasks** — everything else uses workflow (prompt chaining, routing, parallelization).

**3. Model Selection (Eval-Driven, Not Reputation-Driven)**  
Run at least two rounds: ① test SOTA models on 30–50 representative tasks; ② test cost-effective models (Haiku 4.5, Gemini Flash, GPT-5 mini) on the same tasks. **Small model + good tools often beats large model + poor tools.**

**4. Tool Design (The Real Core — More Important Than Prompt)**  
- Use LLM-friendly naming (verb + noun, self-documenting parameter names)
- Error messages must be readable and recoverable ("file not found, did you mean X?" beats stack traces)
- Explicitly label side effects (read-only vs write, reversible vs irreversible)
- Cap tool count: beyond ~20 tools, model selection accuracy drops significantly — use layering/namespacing
- Prioritize [MCP server](https://modelcontextprotocol.io/) exposure for reusability

**5. Eval Set Construction**  
- Minimum 50–200 tasks covering typical + edge + adversarial cases
- Each task has ground truth or LLM-as-judge scoring criteria
- Full eval run cost must be controllable (< $5–$50/run) — otherwise you won't run it
- Toolstack: LangSmith / Braintrust / Langfuse / OpenAI Evals / Anthropic Inspect

**6. Guardrails (Dual-Layer: Input + Output)**  
- Input: prompt injection detection (Anthropic classifiers, Lakera Guard, Llama Prompt Guard)
- Output: PII redaction, format validation, call count/total cost caps, human-in-the-loop for critical operations
- Spend limits are literally lifesavers — many teams have been burned by agent infinite loops costing thousands

**7. Observability (Trace + Cost Visibility)**  
Every agent call must be replayable: which prompt, which tools called, what parameters, what returned, how many tokens, how much cost. [OpenTelemetry's `gen_ai.*` semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) are standardized — new projects should plug into OTel directly.

**8. Gradual Rollout + Continuous Iteration**  
- Month 1: 1–5% traffic, mandatory human review of random trace samples
- Failed traces go directly into eval set (cheapest way to expand evals)
- Weekly: retune prompts / adjust tools / update guardrails
- Key metrics: task completion rate, handoff rate (escalations to humans), cost per resolved task, user reversal rate

---

## III. Agent Classification: Two Dimensions

**Dimension A: By Autonomy Level**

| Type | Form | Typical Use Case | Dev Focus |
|---|---|---|---|
| **Workflow** | LLM as a pipeline step | Doc classification, extraction, routing | Prompt engineering + flowcharts |
| **Single-agent loop** | LLM in think-act-observe cycle | Customer service, Q&A + tool calls | Tool design + context management |
| **Multi-agent orchestration** | Primary agent orchestrating sub-agents | Complex research, cross-domain tasks | Inter-agent interfaces + context handoff |
| **Computer-use agent** | Screenshot + mouse/keyboard GUI control | Legacy systems, cross-app automation | Visual understanding + error recovery + sandbox |

**Cognition's [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) warning**: Devin's production conclusion is that in most scenarios, **single agent + sub-agent tool-ification (rather than true multi-agent collaboration) is more reliable**. Multi-agent looks sexy but context loss and coordination overhead cause reliability to drop exponentially.

**Dimension B: By Business Type**

| Category | Representative Products | Development Specifics |
|---|---|---|
| Coding agent | Devin, Claude Code, Cursor | Sandboxed execution + git diff; eval via SWE-bench Verified |
| Customer service / business agent | Sierra, Decagon, Crew | Strong outcome-based eval; deep CRM/ticketing integration |
| Research / answer agent | Perplexity, ChatGPT Deep Research | Search + citation tracing; eval via GAIA, BrowseComp |
| Vertical expert agent | Harvey (legal), Hebbia (finance) | Domain corpus + domain expert evaluators; compliance auditing |
| Personal assistant agent | Apple Intelligence, Google Astra | On-device/hybrid inference + long-term memory + cross-app permissions |
| Browser / GUI agent | OpenAI Operator, Computer Use | Sandboxed browser + vision + error recovery; eval via OSWorld/WebArena |
| Workflow automation | Zapier AI, n8n + AI, Lindy | Strong triggers/schedulers; process-oriented rather than conversation-oriented |

**Cross-category borrowing is a common mistake** — applying customer service "conversation turn count" metrics to a coding agent is meaningless.

---

## IV. 6 Concrete Lessons

**1. Eval-first, not prompt-first.** Build 50 ground-truth tasks before writing your first prompt. [Hamel Husain's *Your AI product needs evals*](https://hamel.dev/blog/posts/evals/) is the definitive statement of this principle. An agent project without evals is essentially intuition-driven product development.

**2. Tool design > prompt engineering.** When you feel like "no matter how I tune the prompt, it doesn't work" — 90% of the time the problem is tool design: too coarse/fine granularity, bad error messages, ambiguous side effects. Fixing tools has 10x the ROI of fixing prompts.

**3. Context management is the new memory management.** Karpathy's "context window is RAM" analogy is apt: actively summarize/prune/segment context beyond 30K tokens; consider external memory stores (Letta, Mem0, Zep) beyond 200K. **The most common long agent loop failure isn't the model getting dumber — it's context getting polluted by irrelevant traces.**

**4. Human-in-the-loop is product design, not a temporary compromise.** The key is not "when to bring humans in" but "how to minimize the cost of intervention" — confirm button vs. three-option choice vs. free text. LangChain's Agent Inbox pattern is a useful reference.

**5. Cost/latency are product decisions, not engineering optimizations.** "Cost per resolved task" determines whether outcome-based pricing is viable; "time to first response" determines user experience. Lock in budget targets at product definition time — don't discover you're burning $5 per session after launch.

**6. Treat prompt injection like SQL injection.** Any agent that puts external content (emails, web pages, user-uploaded files) into context should treat that input as untrusted by default. [Simon Willison's prompt injection series](https://simonwillison.net/tags/prompt-injection/) is required reading; Anthropic's indirect prompt injection red-team cases are worth every agent team's postmortem review.

---

## V. 3–5 Year Evolution: My Judgment

**Near-term (already happening)**:
- spec → eval → tool design → guardrails → deploy becomes standard pipeline like CI/CD
- MCP becomes de facto standard; hand-writing function calling schemas becomes an antipattern
- Eval commercialization: third-party "agent evaluation certification" emerges (METR, Scale AI, Apollo Research already positioning here)

**Medium-term (2027–2030, likely)**:
- Self-improving agents: production traces auto-feed evals, auto-tune prompts and tool descriptions (DSPy, TextGrad are early signals)
- Agent OS abstraction layer: "tool loop + retry + observability + guardrails" gets OS-ified (Cloudflare Workers AI, Vercel AI, Modal Agents, Bedrock AgentCore competing for this)
- Multi-agent becomes viable when A2A protocol matures and context handoff standardizes

**Long-term (post-2030, high uncertainty)**:
- "Agent as first-class citizen" in dev process: first step of any new feature is defining its agent interface
- Role restructuring: PM → "agent designer + eval owner"; QA → "agent eval engineer"; Engineers split into platform engineers and agent operators

---

## Start Here Today

If your team is launching an agent project **right now**, follow this order:

1. **Replicate an existing agent first** (use Anthropic SDK or OpenAI Agents SDK to build the simplest customer service or document analysis agent), get the eval pipeline running — about 2 weeks
2. **Then revisit your business**, identify 3 candidate scenarios, rank by "failure cost × frequency"
3. **Pick the lowest-failure-cost, highest-frequency one first** (typical: internal doc Q&A, contract clause extraction, email classification) — start with workflow, not agent
4. **After 3 months of trace data**, then consider whether to upgrade to a true agent loop

Skipping steps 1–3 to build an "AGI-like general agent" is the most common money-burning failure pattern of 2024–2025. This isn't pessimism — it's consensus among leading teams.

---

**Key References**

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI, A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Cognition, Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- [Sierra, τ-bench benchmarking AI agents](https://sierra.ai/blog/benchmarking-ai-agents-with-tau2)
- [Hamel Husain, Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [Simon Willison on prompt injection](https://simonwillison.net/tags/prompt-injection/)
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
