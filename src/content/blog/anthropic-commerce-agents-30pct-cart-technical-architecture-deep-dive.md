---
title: "Commerce Agents 技术深潜：购物车提升 30%、完成率提升 60% 背后的六个架构决策"
titleEn: "Commerce Agents Deep Dive: The Six Architecture Decisions Behind 30% Cart Lift and 60% Completion Rate Improvement"
description: "Anthropic commerce-agents 正式开源，合作伙伴实测购物车规模最高提升 30-35%，购买完成率提高约 60%。本文深入拆解六个关键技术决策：单 Agent + Skills、UI 组件工具调用、提示词缓存命中率 90-99%、harness 层安全强制、异步记忆提取，以及 Shopify UCP 集成路径。"
descriptionEn: "Anthropic's commerce-agents is now open source. Partner testing shows cart size up 30-35% and purchase completion rate up ~60%. This article breaks down six key architecture decisions: single agent + skills, UI components as tool calls, 90-99% prompt cache hit rates, harness-level safety enforcement, async memory extraction, and the Shopify UCP integration path."
pubDate: 2026-09-04
updatedDate: 2026-09-04
category: Research
tags: ["AI", "Agent", "Claude", "Anthropic", "电商", "架构", "商业Agent", "Shopify", "性能优化"]
heroImage: "../../assets/images/anthropic-commerce-agents-30pct-cart-technical-architecture-deep-dive-banner.jpg"
author: "Mycelium Protocol"
---

昨天我们介绍了 Anthropic 开源的 [commerce-agents 基础架构](https://blog.mushroom.cv/blog/anthropic-commerce-agents-shopping-merchant-business-blueprint/)。今天来看数字和细节。

合作伙伴的真实测试结果：
- **购物车规模最高提升 30-35%**
- **购买完成率提高约 60%**

这两个数字说明 Agent 购物体验不只是"把搜索做成对话"，而是从根本上改变了用户的购买路径。这篇文章拆解这些结果背后的六个关键架构决策。

---

## 背景：两个 Agent，真实落地的用户

commerce-agents 已经有真实用户在跑：

- **Priceline**：Penny Agent，旅行场景
- **Wix**：15 分钟内跑通，最快接入纪录
- **Zomato**：外卖 + 餐厅发现场景
- **Fetch**：购物奖励场景

生态合作伙伴覆盖：Accenture、Mastercard、Visa。

多平台部署：Claude API、Amazon Bedrock、Microsoft Foundry、Google Cloud Vertex AI。

---

## 架构决策一：单 Agent + Skills，而非多子代理

这是整个技术架构里最关键的设计选择，值得仔细说明。

### 为什么不用子代理编排

在很多 Agent 框架里，遇到复杂任务会把它拆分给多个子代理：搜索子代理、比价子代理、购物车子代理……每个专注于一个领域，由一个编排器协调。

commerce-agents **明确拒绝了这个方案**，原因：

> "电商对话高度耦合、需要共享上下文。"

一个具体例子：

```text
用户：我需要帐篷、睡袋和炉子，周末带两个孩子去露营。
```

这句话里藏着几个需要贯穿全程的上下文：
- "两个孩子"→ 帐篷容量至少 3-4 人
- "周末" → 临时预算，不需要专业登山装备
- "炉子" → 配合帐篷和睡袋的使用场景推荐
- 三件商品之间存在相互约束（帐篷型号影响收纳袋大小，炉子和气罐要配套）

如果用三个子代理分别处理，它们之间的上下文同步就是一个持续的工程问题。子代理交接时状态很容易丢失，每次交接都是一次信息损耗。

### Skills 的解法

Skills 不是独立进程，而是**动态加载到主 Agent 上下文的领域指令**。

当用户问帐篷，主 Agent 加载「露营装备」skill；当对话转向购物车，加载「购物车管理」skill。用户的两个孩子、周末这些约束始终在同一个上下文里，不需要同步。

**关键安全规则始终放在系统提示词中**，不随 skill 切换而变化——法律条款、品牌规则、支付安全边界，这些不可动摇的规则不属于 skill，属于 prompt 主体。

---

## 架构决策二：UI 组件以工具调用形式呈现

这个设计解决了 Agent UI 的一个典型问题：模型输出 XML 标签来标记 UI 元素，然后客户端解析。

```xml
<!-- 典型问题：不稳定，难以验证 -->
<product_card id="P123" name="登山帐篷" price="299" />
```

commerce-agents 的方案：**模型通过结构化工具调用输出界面元素**。

```python
# 模型调用 present_products，而非输出 XML
present_products(
    products=[{"id": "P123", "name": "登山帐篷", "price": 299}],
    context="两大一小，周末露营"
)
```

工具调用的优势：
1. **Schema 验证**：服务器在渲染之前验证结构，不会出现格式错误
2. **Provenance 追踪**：渲染的每个 product ID 都有可追溯来源
3. **无上下文膨胀**：工具结果比长 XML 块占的 token 少得多
4. **支持急切输入流式传输（eager_input_streaming）**：工具参数开始流式到达时就开始验证，不等完整参数才处理

---

## 架构决策三：90-99% 提示词缓存命中率

延迟和成本优化里最实用的一条。

### 请求结构分段设计

关键原则：**按变化频率分段，把稳定内容放在前面**。

```
全局层（几乎不变）
├── 系统 prompt + 所有 skills
├── 品牌规则、安全规则
└── → 缓存命中率接近 100%

会话层（会话内稳定）
├── 用户偏好、购物车状态
└── → 缓存命中率高

易变层（每轮都变）
├── 当前用户消息
└── → 不缓存，也不应该缓存
```

**最容易破坏缓存的错误**：把时间戳、请求 ID、随机数放进系统 prompt。这类信息每次请求都不一样，会导致整个 prefix 的缓存失效。

实测命中率：**90-99%**，意味着 90-99% 的 token 不需要重新计算，直接命中缓存。

### 急切工具调度

工具参数流式传输完成后立即执行，不等模型输出完整 turn。这对购物类多工具调用的场景有明显的延迟改善——搜索、比价、获取详情可以在流式传输过程中并发启动。

---

## 架构决策四：安全强制在 Harness 层

这是整个设计里**最重要的安全原则**，也是和"只靠 prompt 做安全"的本质区别。

### 哪些操作在 Harness 层强制执行

| 操作 | 强制方式 |
|------|---------|
| 购物车写入 | 只接受本次会话里 catalog 工具返回的 product ID（白名单验证） |
| 数量上限 | harness 层强制，模型输出什么数量都会被 clamp |
| 商户写操作 | 全部暂存，`apply_change` 需要 host 标记 approved |
| 第三方内容 | 进入模型前全部 sanitize + fence |
| 支付 | `StorefrontBackend` 根本没有支付方法，模型调不到 |

### 为什么不能只靠 Prompt

Prompt 规则只在模型遵守的情况下有效。模型可能：
- 被精心设计的用户输入诱导忽略规则（prompt injection）
- 在上下文很长时"忘记"早期规则
- 在边缘情况下做出不符合预期的判断

Harness 层强制的规则**对任何模型版本、任何用户输入都有效**，不依赖模型的遵从性。

这也是为什么 README 里说"这些规则在任何模型上都成立"——因为它们不是 prompt，是代码。

---

## 架构决策五：异步记忆提取

传统方式：每轮对话结束后同步提取记忆 → 增加响应延迟。

commerce-agents 的方式：**记忆提取独立异步运行**。

```python
# 主对话路径：不等记忆提取完成
async for event in agent.stream_turn(messages, session, state):
    yield event  # 立即返回给用户

# 异步，不阻塞主路径
asyncio.create_task(agent.update_memory(messages, session))
```

效果：
- 对话延迟不受记忆提取影响
- 记忆召回率提升约 **13%**（更完整地从对话中提取事实）

记忆提取只读取用户和助手的**文字内容**，不读取工具结果——这个设计防止了工具输出（比如商品 JSON）被误存为用户偏好。

记忆写入有严格校验：key 最多 64 字符，value 最多 200，类别只有三种，identifier-shaped values（看起来像 API key、订单号的字符串）默认拒绝。

---

## 架构决策六：评估方法——快照测试优于多轮模拟

这一条不是技术实现，但对工程质量的影响同样重要。

### 传统评估的问题

模拟用户进行多轮对话测试：
- 慢（每轮都要等模型响应）
- 不稳定（模型输出的随机性导致测试结果不可重现）
- 难以精确覆盖边缘情况

### commerce-agents 的方案：直接构造状态

不模拟用户，**直接构造目标状态进行快照测试**：

```python
# 不模拟"用户说了三轮话然后问这个"
# 直接构造"这是当前的 session state"
state = SessionState(
    cart=[CartLine(product_id="P123", quantity=2)],
    memory=[Fact(key="prefers_outdoor", value="camping")],
    last_query="帐篷有没有防水保证"
)
response = agent.snapshot_test(state, "帐篷有没有防水保证")
```

关键要求：**正向和负向用例都要覆盖**。不只测试"正常流程"，还要测试：
- 用户试图往购物车加一个没有搜索过的商品
- 商户试图绕过审批直接应用变更
- 第三方内容里包含 prompt injection 尝试

---

## Shopify 集成：UCP + Admin API

Shopify 提供了 commerce-agents 的参考实现，路径是：

```
Claude Agent
    ↓ 通过 Universal Commerce Protocol (UCP)
Shopify 店铺目录（只读）
    ↓ 购物车创建成功后
Shopify 原生结账页（跳转）
    ↓ 商家侧
Shopify Admin API（商户代理）
```

**UCP（Universal Commerce Protocol）**：Shopify 推的商业协议标准，让 AI Agent 能以一致的方式访问不同商家的目录——不需要为每家店铺写单独的连接器。

**结账手交付**：Agent 不参与支付，创建购物车后跳转到 Shopify 原生结账页。Shopify 的 PCI 合规、欺诈检测、支付处理全都在那个页面里。Agent 做的是"帮用户决定买什么"，结账是商家的。

---

## 完整技术架构图

```
用户 → 宿主应用（认证 + 会话）
        ↓
主 Agent（系统 prompt + 安全规则）
        + 动态加载的 Skills（按对话上下文）
        ↓ 工具调用（validate → execute → enrich）
Harness 层（ID 白名单 / 数量上限 / 暂存 / fence）
        ↓
StorefrontBackend / MerchantBackend（你的系统接口）
        ↓
UI 组件（结构化工具调用 → 服务器验证 → 客户端渲染）
异步记忆提取（独立任务，不阻塞响应路径）
提示词缓存（全局层 99% / 会话层高 / 易变层不缓存）
```

---

## 给开发者的关键结论

1. **用单 Agent + Skills，不要轻易引入子代理编排**——除非你的任务真的是独立子问题，否则共享上下文的价值远大于分工的收益

2. **UI 输出用工具调用，不用 XML 标签**——结构化比格式更可靠，验证比解析更稳健

3. **把请求结构按变化频率分段**——时间戳不要放系统 prompt，让缓存帮你省钱

4. **安全约束写在 harness 层，不要只放 prompt**——prompt 只在模型遵守时有效，代码始终有效

5. **评估用快照测试**——直接构造状态，比多轮模拟快 10 倍，比它稳定 100 倍

---

## 相关链接

- GitHub：[anthropics/commerce-agents](https://github.com/anthropics/commerce-agents)
- 上一篇：[Commerce Agents 基础架构介绍](https://blog.mushroom.cv/blog/anthropic-commerce-agents-shopping-merchant-business-blueprint/)
- Shopify UCP 文档：[shopify.dev](https://shopify.dev)

<!--EN-->

Yesterday we covered the [basic architecture of commerce-agents](https://blog.mushroom.cv/blog/anthropic-commerce-agents-shopping-merchant-business-blueprint/). Today: the numbers and the technical details.

Partner testing results:
- **Cart size up 30-35%**
- **Purchase completion rate up ~60%**

These numbers show that an agent shopping experience isn't just "search as conversation" — it fundamentally changes the user's purchase path. This article breaks down the six architecture decisions behind these results.

---

## Background: Two Agents, Real Production Users

commerce-agents has real users running it:

- **Priceline**: Penny Agent, travel scenarios
- **Wix**: Integrated in under 15 minutes (fastest known onboarding)
- **Zomato**: Food delivery + restaurant discovery
- **Fetch**: Shopping rewards

Ecosystem partners: Accenture, Mastercard, Visa.

Multi-platform: Claude API, Amazon Bedrock, Microsoft Foundry, Google Cloud Vertex AI.

---

## Decision 1: Single Agent + Skills, Not Multi-Agent Orchestration

The single most consequential architecture decision. Here's why.

### Why Not Subagents

Many agent frameworks decompose complex tasks across specialized subagents: a search subagent, a comparison subagent, a cart subagent — coordinated by an orchestrator.

commerce-agents **explicitly rejects this pattern**, because:

> "Commerce conversations are highly coupled and need shared context."

Concrete example:

```text
User: I need a tent, sleeping bag, and camp stove for a weekend trip with two kids.
```

This contains constraints that span the entire interaction:
- "Two kids" → tent must fit 3-4 people
- "Weekend" → casual trip, not mountaineering gear
- "Stove" → recommendations constrained by tent and sleeping bag compatibility
- All three items have cross-constraints (tent dimensions affect pack size; stove needs matching fuel canisters)

With three subagents, context synchronization is a continuous engineering problem. Every handoff is an opportunity for information loss.

### The Skills Solution

Skills are not separate processes — they're **domain instructions dynamically loaded into the main agent's context**.

When the user asks about tents, load the "camping gear" skill. When conversation shifts to the cart, load "cart management." The "two kids, weekend" constraints live in one context throughout, no synchronization needed.

**Core safety and legal rules always live in the system prompt** — brand rules, safety boundaries, legal requirements are not skills, they're permanent prompt content that doesn't switch.

---

## Decision 2: UI Components as Tool Calls

This design solves a classic problem: models outputting XML tags to mark UI elements, then clients parsing them.

```xml
<!-- Classic problem: fragile, hard to validate -->
<product_card id="P123" name="Camping Tent" price="299" />
```

commerce-agents' approach: **models output UI elements through structured tool calls**.

```python
# Model calls present_products, doesn't output XML
present_products(
    products=[{"id": "P123", "name": "Camping Tent", "price": 299}],
    context="Family of 3, weekend camping"
)
```

Advantages:
1. **Schema validation**: Server validates structure before rendering; no format errors
2. **Provenance tracking**: Every product ID rendered is traceable to its source
3. **No context bloat**: Tool results consume far fewer tokens than equivalent XML blocks
4. **Eager input streaming**: Validation begins as parameters arrive, not after the complete call

---

## Decision 3: 90-99% Prompt Cache Hit Rate

The most immediately actionable optimization.

### Request Segmentation by Change Frequency

Core principle: **segment by change frequency, stable content first**.

```
Global layer (rarely changes)
├── System prompt + all skills
├── Brand rules, safety rules
└── → Cache hit rate ~100%

Session layer (stable within session)
├── User preferences, cart state
└── → High cache hit rate

Volatile layer (changes every turn)
├── Current user message
└── → Not cached, shouldn't be
```

**Most common cache-busting mistake**: putting timestamps, request IDs, or random values in the system prompt. Any of these invalidates the entire prefix cache on every request.

Measured hit rate: **90-99%** — meaning 90-99% of tokens are served from cache, not recomputed.

### Eager Tool Scheduling

Tools execute as soon as their streaming parameters complete — without waiting for the full model turn. For shopping's multi-tool patterns (search, compare, get details), this enables concurrent execution during streaming, noticeably reducing end-to-end latency.

---

## Decision 4: Safety Enforcement at the Harness Layer

The most important safety principle in the design — and the essential difference from "put it in the prompt."

### What the Harness Enforces

| Operation | Enforcement |
|-----------|-------------|
| Cart writes | Only accept product IDs returned by catalog tools this session (whitelist) |
| Quantity limits | Harness-enforced; any model output gets clamped |
| Merchant writes | All staged; `apply_change` requires host-marked approval |
| Third-party content | Sanitized and fenced before the model sees it |
| Payment | `StorefrontBackend` has no payment method — the model can't call it |

### Why Prompt Alone Is Insufficient

Prompt rules only work when the model follows them. Models can:
- Be induced to ignore rules via prompt injection in user input
- "Forget" early rules when the context is very long
- Make unexpected judgments in edge cases

Harness-layer rules **hold for any model version, any user input** — they don't depend on the model's compliance. This is why the README says "these rules hold on any model" — because they're code, not prompts.

---

## Decision 5: Async Memory Extraction

Traditional approach: synchronously extract memory after each turn → adds to response latency.

commerce-agents' approach: **memory extraction runs independently and asynchronously**.

```python
# Main conversation path: doesn't wait for memory extraction
async for event in agent.stream_turn(messages, session, state):
    yield event  # returned to user immediately

# Async, doesn't block the main path
asyncio.create_task(agent.update_memory(messages, session))
```

Results:
- Conversation latency unaffected by memory extraction
- Memory recall improved ~**13%** (more complete fact extraction from conversations)

Memory extraction reads only user and assistant **text content** — not tool results. This prevents tool outputs (like product JSON) from being accidentally stored as user preferences.

Memory writes have strict validation: key max 64 chars, value max 200, only three allowed categories, identifier-shaped values rejected by default.

---

## Decision 6: Snapshot Testing Over Multi-Turn Simulation

Not a technical implementation detail, but equally important for engineering quality.

### The Problem With Multi-Turn Simulation

Simulating user conversations for testing:
- Slow (every turn requires a model inference)
- Unstable (model output randomness makes test results non-reproducible)
- Hard to precisely cover edge cases

### commerce-agents' Approach: Construct State Directly

Don't simulate users — **construct the target state directly for snapshot testing**:

```python
# Don't simulate "user said three things then asked this"
# Directly construct "this is the current session state"
state = SessionState(
    cart=[CartLine(product_id="P123", quantity=2)],
    memory=[Fact(key="prefers_outdoor", value="camping")],
    last_query="Does the tent have waterproofing warranty"
)
response = agent.snapshot_test(state, "Does the tent have waterproofing warranty")
```

Critical requirement: **cover both positive and negative cases**. Don't just test the happy path — also test:
- User tries to add a product to the cart that was never searched
- Merchant tries to bypass approval to apply a change directly
- Third-party content contains a prompt injection attempt

---

## Shopify Integration: UCP + Admin API

Shopify provides a reference implementation for commerce-agents:

```
Claude Agent
    ↓ via Universal Commerce Protocol (UCP)
Shopify store catalog (read-only)
    ↓ after cart creation
Shopify native checkout (redirect)
    ↓ merchant side
Shopify Admin API (merchant agent)
```

**UCP (Universal Commerce Protocol)**: Shopify's commerce protocol standard that lets AI agents access different merchants' catalogs consistently — no per-store connectors needed.

**Checkout handoff**: The agent doesn't handle payment. After cart creation, it redirects to Shopify's native checkout. Shopify's PCI compliance, fraud detection, and payment processing all happen there. The agent decides *what* to buy; checkout is the merchant's.

---

## Key Takeaways for Engineers

1. **Use single agent + skills, don't prematurely reach for subagent orchestration** — unless your tasks are genuinely independent, shared context is worth more than division of labor

2. **Output UI via tool calls, not XML tags** — structured is more reliable than formatted, validation beats parsing

3. **Segment requests by change frequency** — don't put timestamps in the system prompt; let the cache save you money

4. **Write safety constraints in the harness layer, not just the prompt** — prompts work only when models comply; code always works

5. **Use snapshot testing for evals** — directly construct state; it's 10x faster than multi-turn simulation and 100x more stable

---

## Links

- GitHub: [anthropics/commerce-agents](https://github.com/anthropics/commerce-agents)
- Previous article: [Commerce Agents Architecture Overview](https://blog.mushroom.cv/blog/anthropic-commerce-agents-shopping-merchant-business-blueprint/)
- Shopify UCP: [shopify.dev](https://shopify.dev)
