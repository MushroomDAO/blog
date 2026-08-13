---
title: "Applied Compute 深度拆解：OpenAI 系团队的「具体智能」，RL 三环架构如何把企业 AI 做成工业品"
titleEn: "applied-compute-specific-intelligence-enterprise-ai-workflow-training"
description: "Applied Compute 创始团队来自 OpenAI Codex 与 o1，CEO Yash Patil 的核心判断：前沿模型商品化之后，竞争层移到后训练。产品「具体智能（Specific Intelligence）」以强化学习为核心机制，围绕 Rollout-Eval-Inference 三环构建企业专用 AI 闭环。DoorDash 菜单提取、Cognition 代码缺陷检测、Mercor 人才评估是已披露的三个案例。30 亿美元估值背后是四层硬风险：定制化滑向咨询、开源压低价格、大厂抢占后训练、估值与经营结果的时间差。"
descriptionEn: "Applied Compute's founding team came from OpenAI Codex and o1. CEO Yash Patil's thesis: as frontier models commoditize, the competitive layer moves to post-training. Their product Specific Intelligence uses reinforcement learning as the core mechanism, building enterprise AI via a Rollout-Eval-Inference loop. Disclosed clients: DoorDash (menu extraction), Cognition (code defect detection), Mercor (talent evaluation). Four hard risks behind the $3B valuation: customization creep toward consulting, open-source price compression, big-tech entering post-training, and the gap between valuation and operating results."
pubDate: "2026-08-13"
updatedDate: "2026-08-13"
category: "Tech-News"
tags: ["企业AI", "Applied Compute", "强化学习", "后训练", "Specific Intelligence", "AI商业化", "Agent", "Mycelium"]
heroImage: "../../assets/images/applied-compute-specific-intelligence-enterprise-ai-workflow-training-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Applied Compute 的创始团队来自 OpenAI 的 Codex 和 o1 项目。CEO Yash Patil 在 Modal 的案例视频里说了一句话，算得上是这家公司的核心判断：

> "Frontier models set the floor, specialized models and custom post-training raise the ceiling."
>
> 前沿模型划定了地板，专门化模型和定制后训练才能抬高天花板。

这套判断不是新鲜话，但 Applied Compute 把它变成了一套可以卖给企业的工程产品。他们叫它 **Specific Intelligence（具体智能）**——不是通用聊天，是为一家公司、在它的数据上训练、每次使用后还在持续改进的专用 AI。

目前已公开的客户是 DoorDash、Cognition 和 Mercor。Modal 的案例文章是目前关于 Applied Compute 最详细的公开披露，以下拆解全部来源于此。

---

## 真实的服务流程：嵌入研究员，编码机构判断

Applied Compute 的交付方式是 **embed researchers with each customer**——把研究员嵌进客户组织，把客户的机构判断编码进奖励函数，然后持续跑训练循环，直到模型的行为「像组织的一员，而不只是另一个工具」。

这不是提供 API，也不是做咨询项目——更接近一支外部研发团队在帮客户搭建自己的智能层。

具体流程分四步：

**第一步：还原工作环境。** RL 训练的基础是让 agent 在可重放的环境里反复执行任务。Applied Compute 的标准是环境必须与生产系统保持足够的保真度——完整模拟 Salesforce、Slack、内部 API，而不是用假数据凑数。Patil 说得很直接：「训练 agent 的环境，应该就是它之后真实工作的环境。」训练-测试不匹配是已部署 RL 系统里最稳定出现的失败模式。

**第二步：定义奖励函数和评测标准。** 什么叫做正确，什么情况需要人工接管，哪些错误不能接受——这些都必须先于训练存在。Applied Compute 把客户的机构判断变成可计算的奖励函数和评测规则，这是每个客户场景里差异最大、价值最集中的部分。

**第三步：持续跑 RL 训练循环。** 模型在并行的沙盒环境里成千上万次地尝试任务，每次尝试都被评分，权重向奖励函数认可的行为方向更新。这个循环不是一次性的，生产中的每次决策和反馈会持续进入训练。

**第四步：生产中持续打分。** 评分层（Evals）不只在训练时运行，在生产中也同步运行，实时打分 agent 的每次决策，把这些 trace 送回训练循环。这是 Applied Compute 能宣称「每次使用后都在改进」的技术基础。

---

## 技术栈：RL 三环结构

Applied Compute 的 RL 训练循环由三个组件构成，基础设施运行在 Modal 上：

```
Rollouts（探索） → Evals（评分） → Inference（推理）
     ↑                                    ↓
     └──────── trace 持续回流 ─────────────┘
```

### 1. Rollouts（探索环节）

Agent 在可重放的沙盒环境里并行执行任务，数量从几百到数千个。

- **特征**：突发性高、CPU 密集
- **关键需求**：环境与生产系统高保真，具有快速启动和快照语义（支持重放）
- **基础设施**：Modal Sandboxes——提供临时容器、完整文件系统/网络隔离、子秒级冷启动

每个 rollout 里的沙盒环境都在完整模拟实际的业务系统。启动延迟直接影响 GPU 利用率：「CPU 的事越快越好——每一毫秒的沙盒初始化，就是一毫秒 GPU 在空转。」

### 2. Evals（评分环节）

每次 rollout 都需要被打分。评分方式包括：

- 单元测试（确定性规则）
- 专家撰写的评分标准（rubrics）
- LLM-as-judge（用语言模型评判语言模型的输出）

评分层的特征是**大规模并行 CPU 计算**，Applied Compute 用 Modal Functions 做无服务器扇出，不需要维护专用集群。同一套评分机制在生产中也持续运行，对 agent 的真实行为实时打分。

### 3. Inference（推理环节）

训练好的模型被部署到生产环境，同时捕获新的 trace 送回训练。推理端需要对 GPU 有优化的访问路径，与 Rollout 侧并行运行。

### 为什么选 Modal

Applied Compute 评估了「市面上几乎所有的沙盒和执行提供商」，最终选择 Modal 的理由：

- 三个组件各有不同的基础设施需求，Modal 能在每一层提供匹配的原语，同时保持各组件之间的状态共享和边界低开销
- 子秒级冷启动保持训练循环 GPU-bound 而非 CPU-bound
- 自动重试和每次调用的隔离让大规模并发下的可靠性可控

---

## 三个已披露案例

### DoorDash：商户菜单结构化提取

任务：拍摄一张餐厅菜单照片，输出 DoorDash 生产系统使用的结构化门店信息。

这个任务看起来平凡，实际上有几个技术难点：菜单格式千变万化（手写、印刷、多语言、残缺），提取结果直接进生产数据库，错误率必须极低。Applied Compute 的做法是训练一个专用的 SOTA 模型，用大量真实菜单图片和 DoorDash 的生产标准作为奖励函数。

### Cognition：代码缺陷检测

任务：开发者 save 一次 commit，agent 在几秒内找到特定类型的缺陷。

Cognition 是 Devin（AI 软件工程师）的开发商。除了上面的案例，Cognition 还把 Modal 作为 RL 基础设施和生产推理双重用途：「Modal 支撑着我们的强化学习基础设施和生产推理。一端是百万沙盒，另一端是实时服务。」Applied Compute 为他们设计的 bug-catching agent 在毫秒级响应，直接嵌入开发工作流。

### Mercor：人才评估

Mercor 是 AI 驱动的人才市场。具体的 Applied Compute 任务细节尚未完整披露，但从场景推断：结构化评估候选人、匹配岗位需求、在标准化标准下快速处理大量候选人信息，是这类场景的典型需求。

---

## 开源权重与后训练层

Applied Compute 不需要押注某个特定的基础模型，这在架构上是有意为之的。价值集中在三个地方：

- **奖励函数**：定义什么叫做正确，是每个客户场景里差异最大的部分
- **评测体系**：让「模型好不好」从主观感觉变成可量化的数字
- **持续反馈回路**：生产决策持续进入训练，让系统逐步接近企业认可的工作方式

开源权重的技术进步对 Applied Compute 来说不是威胁，而是资源：更便宜的基础能力意味着后训练的价值相对更高。真正属于客户的资产是数据、判断标准和历史反馈，这些不会随着开源模型能力提升而贬值。

---

## 四个硬风险

Applied Compute 面临的四个结构性风险：

**风险一：定制化可能把平台拖回咨询业务。** 企业 AI 需求差异很大，客户往往需要深度改造。Applied Compute 嵌研究员的模式天然靠近咨询，如果不能有效控制项目边界，每个客户都会变成一个独立研发项目，平台的规模效应就很难跑出来。

**风险二：开源模型持续压低基础能力价格。** 模型训练和推理成本下降，对客户是好事，对平台也可能形成压力。平台必须把价值牢牢放在评估、工作流和反馈闭环里，而不是作为模型调用的中间商。Applied Compute 目前的定位是做后训练而非卖推理，但随着客户越来越懂技术，这条边界需要持续守住。

**风险三：封闭模型厂商不会放弃企业后训练市场。** OpenAI、Anthropic、Google 和云厂商都有数据、模型、算力和分发的系统性优势。一旦它们把企业级微调与 agent 部署做成标准产品，Applied Compute 需要用更强的客户理解和更深的业务嵌入来守住位置——这实际上又回到了「嵌入式咨询」的模式，同样面临规模化压力。

**风险四：融资估值和经营结果之间存在时间差。** 上一轮 13 亿美元投后估值已经很高，若本轮约 30 亿美元落地，公司需要快速证明收入增长、客户留存和资本效率。估值上涨给团队带来资源，也给下一轮融资和潜在上市预期增加了压力。

---

## 看企业 AI，别只看模型有多聪明

30 亿美元估值背后，Applied Compute 真正要向投资人证明的是三件事：

**收入质量**：5000 万美元 ARR 来自哪里？是一次性模型定制服务费，还是多年期合同？平台订阅和推理收入各占多少？客户付费之后，会不会把更多业务线接进来？这些问题决定收入倍数能不能持续。

**成本结构**：企业专用模型的交付成本很高。如果每新增一个客户，就必须派驻一支研究团队，收入增长会被人力成本抵消。能否把奖励函数设计、环境搭建、评测模块做成平台工具，让边际成本随规模下降，是决定商业模型质量的核心变量。

**反馈飞轮**：Applied Compute 接触的客户场景越多，积累的训练方法和交付经验越丰富。但经验只留在项目团队里，规模效应有限；能不能沉淀成标准化工具、可迁移的训练流程，才是平台价值能否真正释放的关键。

**实用观察框架**：看企业 AI，不只看模型有多聪明。

- **看收入**：来自平台订阅、推理使用、模型训练，还是一次性服务？
- **看客户**：企业把多少个工作流交给了 agent？用了多长时间？
- **看闭环**：feedback 是真正进入训练，还是只是用来展示给客户看的 dashboard？

Yash Patil 说：「每家公司都会开始构建自己的智能层，就像当年构建软件栈一样。」这个方向本身争议不大，争议在于谁来帮它们构建，以及这件事最终是产品、平台还是咨询。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Applied Compute Deep Dive: The OpenAI Alumni's "Specific Intelligence" — How Their RL Loop Turns Enterprise AI into a Manufacturing Process

*by Mycelium Protocol*

---

Applied Compute's founding team came out of OpenAI's Codex and o1 projects. CEO Yash Patil put the company's core thesis in one line, in the Modal case study video:

> "Frontier models set the floor, specialized models and custom post-training raise the ceiling."

This isn't a new idea, but Applied Compute built it into an engineering product you can sell to enterprises. They call it **Specific Intelligence** — not general-purpose chat, but AI built for one company, trained on its proprietary data, improving every time it's used.

Confirmed clients: DoorDash, Cognition, and Mercor. The Modal case study is currently the most detailed public disclosure about Applied Compute. Everything below traces back to that source.

---

### Real Service Flow: Embed Researchers, Encode Institutional Judgment

Applied Compute delivers by embedding researchers with each customer — encoding the customer's institutional judgment into reward functions, then running the training loop until the model behaves like a member of the organization rather than just another tool.

This isn't providing an API. It isn't consulting. It's closer to an external R&D team helping a company build its own intelligent layer.

The process unfolds in four steps:

**Step one: Recreate the work environment.** RL training requires agents to repeatedly attempt tasks inside replayable environments. Applied Compute's standard: the environment must achieve high fidelity against production systems — a full simulation of Salesforce, Slack, internal APIs — not approximations with dummy data. Patil is direct: "The environment you train your agents in should be the environment they go and do their real work." Train-test mismatch is the most consistent failure mode in deployed RL systems.

**Step two: Define reward functions and evaluation standards.** What counts as correct, when human takeover is required, which errors are unacceptable — all of this must exist before training starts. Applied Compute converts the customer's institutional judgment into computable reward functions and evaluation rubrics. This is where differentiation is most concentrated across customer engagements.

**Step three: Run the RL training loop continuously.** The model attempts tasks thousands of times in parallel sandboxes, each attempt scored, weights updated toward the behavior the reward function favors. This is not a one-time project — each production decision and its feedback feeds back into training continuously.

**Step four: Score in production.** The evaluation layer runs not just during training but continuously in production, real-time scoring every agent decision, feeding those traces back into the training loop. This is the technical foundation for claiming the system improves with every use.

---

### Technical Stack: The Three-Ring RL Architecture

Applied Compute's RL training loop has three components, running on Modal infrastructure:

```
Rollouts (explore) → Evals (score) → Inference (serve)
      ↑                                    ↓
      └──────── traces flow back continuously ──────────┘
```

**Rollouts.** Agents execute tasks in parallel inside replayable sandbox environments — hundreds to thousands at a time.
- Profile: bursty, CPU-heavy
- Key requirement: production-fidelity environments with fast startup and snapshot semantics
- Infrastructure: Modal Sandboxes — ephemeral containers with full filesystem/network isolation and sub-second cold starts

Startup latency directly translates into GPU utilization on the inference side. "The more you can make the CPU stuff really, really fast, the better — any millisecond of sandbox initialization is a millisecond of idle GPU."

**Evals.** Every rollout gets scored through one or more mechanisms: unit tests (deterministic rules), expert-authored rubrics, LLM-as-judge. The profile is massively parallel CPU computation. Applied Compute uses Modal Functions for serverless fan-out without maintaining a dedicated cluster. The same grading layer runs in production, scoring live agent decisions across thousands of concurrent traces.

**Inference.** The trained model serves in production while capturing fresh traces to feed back into training. Inference requires optimized GPU access and runs in parallel with rollouts.

Applied Compute evaluated "almost every sandbox and execution provider on the market" before choosing Modal — the only option that provided the right primitive at each layer of the loop while keeping inter-layer state sharing low-cost.

---

### Three Disclosed Cases

**DoorDash — Restaurant menu extraction:** Photograph a restaurant menu, output the structured storefront representation DoorDash uses in production. Menus vary wildly in format; the output goes directly into production databases with minimal error tolerance. Applied Compute trained a state-of-the-art specialized model using real menu images and DoorDash's production standards as the reward function.

**Cognition — Code defect detection:** A developer saves a commit; the agent surfaces relevant bugs within seconds. Cognition's Devin (AI software engineer) already runs on Modal for RL training and production inference — "millions of sandboxes on one end, real-time serving on the other." Applied Compute's bug-catching agent embeds directly into the development workflow at sub-second response times.

**Mercor — Talent evaluation:** Mercor runs an AI-powered talent marketplace. The specifics remain undisclosed, but the scenario implies: structured candidate evaluation, job matching, and high-throughput processing of applicant information against standardized criteria — a repeating, high-stakes task where specialized models beat general-purpose ones on both accuracy and cost.

---

### Open-Source Weights and the Post-Training Layer

Applied Compute does not need to bet on any specific foundation model. This is architecturally intentional. Value is concentrated in three places:

- **Reward functions**: defining what "correct" looks like — the most differentiated part of every customer engagement
- **Evaluation systems**: turning "is the model good" from a subjective impression into a quantifiable number
- **Continuous feedback loop**: production decisions flow back into training, moving the system continuously toward the company's own working standards

Advances in open-source model capability are not a threat to this model — they're a resource. Cheaper base capability means the post-training layer's relative value is higher. The assets that genuinely belong to customers — their data, judgment standards, and historical feedback — don't depreciate as open-source models improve.

---

### Four Hard Risks

**Risk one: Customization creep pulls the platform back toward consulting.** Enterprise AI needs vary widely. Customers frequently require deep adaptation. Applied Compute's embedded-researcher model is naturally close to consulting. Without tight project boundaries, each customer becomes a separate R&D project, and platform-style scale economics become very hard to achieve.

**Risk two: Open-source models keep compressing base capability prices.** Training and inference costs decline. For customers, this is good. For Applied Compute, it creates pressure: the platform must firmly hold its value in evaluation, workflow integration, and feedback loops — not as a model call intermediary. The company's positioning in post-training rather than inference sales is correct, but as customers become more technically sophisticated, this boundary needs continuous defense.

**Risk three: Closed model vendors won't give up the enterprise post-training market.** OpenAI, Anthropic, Google, and cloud providers have systematic advantages in data, models, compute, and distribution. Once they make enterprise fine-tuning and agent deployment into standard products, Applied Compute's defense is stronger customer understanding and deeper business integration — which brings the model closer to embedded consulting again, under the same scaling pressure.

**Risk four: A gap between valuation and operating results.** The previous round's post-money valuation was already high at $1.3B. If the current ~$3B round closes, the company needs to quickly demonstrate revenue growth, customer retention, and capital efficiency. A rising valuation brings resources and adds pressure on the next fundraise and any eventual IPO expectations.

---

### Watching Enterprise AI: Look Past How Smart the Model Is

Behind the $3B valuation, Applied Compute needs to prove three things:

**Revenue quality.** Where does $50M ARR come from? One-time model customization service fees, or multi-year contracts? What's the split between platform subscriptions, inference revenue, and project fees? After paying, do customers bring additional business lines in? These questions determine whether the revenue multiple holds.

**Cost structure.** Enterprise-specific model delivery is expensive. If each new customer requires deploying a research team, revenue growth gets absorbed by headcount. Can the reward function design, environment setup, and evaluation modules become platform tools with declining marginal cost? This is the core variable determining business model quality.

**Feedback flywheel.** The more customer scenarios Applied Compute encounters, the richer the training methods and delivery knowledge they accumulate. But if that knowledge stays inside project teams, scale effects are limited. Whether it crystallizes into standardized tools and transferable training pipelines is whether platform value actually gets released.

**Practical observation framework:**
- **Revenue**: from platform subscriptions, inference usage, model training, or one-time services?
- **Customers**: how many workflows has the enterprise handed to agents — and for how long?
- **Loop**: does feedback genuinely enter training, or does it only appear on a dashboard shown to customers?

Yash Patil: "Every company is going to start to build their own intelligent stack, just like they did with their software stack." The direction itself isn't controversial. What's contested is who builds it for them — and whether this turns out to be a product, a platform, or a consulting firm.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
