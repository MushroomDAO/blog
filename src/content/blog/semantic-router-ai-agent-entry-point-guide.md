---
title: "AI Agent 入口路由怎么选：5 类开源方案实测对比，为什么不是选大模型"
titleEn: "Choosing an Entry Router for AI Agents: A 5-Category Open-Source Comparison"
description: "给 AI Agent 装一个入口'红绿灯'：在真正调用大模型之前，用一个 ~0.1B 级、零 LLM 调用的路由器决定走 agent、搜索、发邮件还是模型链路。我们横向调研了 semantic-router、vLLM SR、RouteLLM、Arch-Router、Octopus-v2 等五类开源方案并附最新 GitHub/HuggingFace 实测数据。"
descriptionEn: "Before an AI agent calls any LLM, it needs a fast, cheap decision layer that routes user intent to the right solution path — agent, search, email, or a model chain. We benchmark five categories of open-source routers (semantic-router, vLLM SR, RouteLLM, Arch-Router, Octopus-v2) with fresh GitHub/HuggingFace stats."
pubDate: "2026-07-30"
updatedDate: "2026-07-30"
category: "Tech-Experiment"
tags: ["semantic-router", "AI Agent", "LLM Router", "路由模型", "开源", "iDoris", "Agent架构"]
heroImage: "../../assets/images/semantic-router-ai-agent-entry-point-guide-banner.jpg"
---

**BLUF**：如果你在做一个通用 AI 入口——用户丢来一句话，你要在**毫秒级、不调用大模型**的前提下决定"接下来怎么处理"（纯 agent？网页搜索？发邮件？要不要换个模型？还是走一条多模型链路？）——答案不是"选个更聪明的 LLM"，而是"选对入口路由器"。我们横向调研了 GitHub + HuggingFace 上五类开源路由方案，结论是：**aurelio-labs/semantic-router**（嵌入相似度路由，~0.1B 量级、零 LLM 调用、库形态可拔插）最贴近"路径路由"这个需求，而不是更出名的 RouteLLM（那个解决的是另一个问题）。

## 为什么"选哪个 LLM"和"该怎么处理"是两件事？

大部分人一提到"AI 路由"，脑子里想到的是 RouteLLM 那种"简单问题用便宜模型、难问题用贵模型"的**模型选择（model-selection）**。但一个真正的 AI 入口面对的问题更早一步：用户的一句话，究竟应该

- 直接丢给一个通用 agent 自己想办法？
- 还是先做一次网页搜索？
- 还是这是个"发邮件"这种确定性动作，不需要 LLM 介入？
- 如果确实要调模型，调哪一个、要不要走多模型链路？

这叫**路径路由（route a *path* by meaning）**，"选哪个模型"只是其中一条分支，而不是全部。把这两件事混为一谈，会导致要么在入口就烧了一次不必要的 LLM 调用（慢、贵），要么路由逻辑写死在 if-else 里没法扩展。

## 调研方法

跟着这三条线走了一遍（可复现）：

- GitHub：`gh search repos "semantic router" / "llm router" / "prompt routing" --sort stars`
- HuggingFace：`GET /api/models?search={router|route|routing}&sort=downloads`
- Web：交叉核对 Not-Diamond 维护的 `awesome-ai-model-routing` 清单

以下数据是发稿前用 `gh repo view` 和 HuggingFace API 现查的实时快照，不是复制自某篇二手资料。

## 开源路由方案的五个类别

### 类 A：嵌入/语义路由器（无 LLM 调用）

代表：**aurelio-labs/semantic-router**——不调用任何大模型，只用一个小嵌入模型算"用户输入"和"预设话术示例"的相似度，命中哪条 route 就走哪条路径。实测 GitHub **3760 star**，4 天前还有 push，活跃度扎实。同类还有 vllm-project/semantic-router（用 mmBERT-32k 做 8 个神经分类器，识别意图/越狱/PII 等），实测 **5078 star**，昨天刚更新，工程更重但也更"生产级"——代价是**耦合 vLLM serving**，如果你的 serving 栈不是 vLLM，接入成本不低。

### 类 B：微型专用路由模型（直接吐路由标签）

代表：HuggingFace 上的 `SupraLabs/Supra-Router-51M`——51M 参数，序列生成直接输出 `Domain|Complexity|Math|Code|Route|Justification` 这样的结构化标签，够小够快。但实测目前下载量 **3670**、点赞 **143**，训练集据调研只有 992 行，偏"任务难度判断"多过"路径路由"，还嫩，值得观察但不建议现在就压上生产。另一个是 `chopratejas/technique-router`，路由到的是"提示技术"而不是"解决方案路径"，方向不同，不能替代。

### 类 C：偏好/复杂度路由（本质是"选哪个 LLM"）

代表：**lm-sys/RouteLLM**——这是"简单问题用弱模型、难问题用强模型"的经典框架，实测 **5275 star**，但 `pushedAt` 停在 **2024-08**，将近两年没有实质性更新了。它解决的是模型选择问题，不是路径路由，硬套到入口场景上会文不对题。另一个是 `katanemo/Arch-Router-1.5B`——1.5B 生成式模型，按 Domain+Action 偏好路由，实测下载量 **1471**、点赞 **270**，模型是固定的（不可换底座），比嵌入方案重也更死板。它背后的完整代理框架 `katanemo/plano` 倒是很活跃，实测 **6910 star**，昨天还有 push。

### 类 D：端侧函数/工具调用模型（route → 具体工具 + 参数）

代表 Octopus-v2（Nexa AI，2B，functional token 做端侧函数调用）、`Salesforce/xLAM-1b-fc-r`（1B，Large Action Model，实测下载量 **3758**）、`MadeAgents/Hammer`（0.5–3B，函数遮蔽抗干扰）——但 Hammer 实测只有 **121 star**，最近一次 push 停在 **2025-06**，比预想中冷门得多。这一类的定位不是"决定走哪条路径"，而是**路径已经确定是"调用工具"之后**，决定调哪个工具、传什么参数——是路径路由之后的**第二阶段**，不是替代品。

### 类 E：路由框架/代理（基础设施，不是"那个模型"）

`katanemo/plano`、ClawRouter、NadirClaw、UncommonRoute、WilmerAI、openziti/llm-gateway，以及前面提到的 `Not-Diamond/awesome-ai-model-routing` 清单（这份清单本身实测 **234 star**，更新截止 2025-03，但仍是这个领域最全的索引之一）。这些是承载路由逻辑的运行时/网关，本身不是"路由模型"，选型时不要跟前四类混着比。

## 对比矩阵

| 方案 | 路径路由 | ~0.1B/无LLM | 活跃度(实测) | 可拔插 | 综合 |
|---|:--:|:--:|:--:|:--:|:--:|
| **semantic-router (aurelio)** | ✅ | ✅ | ✅ 4天前有push，3.7k★ | ✅✅ 嵌入模型可换 | **★ 首选** |
| vLLM semantic-router | ✅ | ◐(0.3B) | ✅✅ 昨天有push，5k★ | ◐ 耦合vLLM | 备选(重) |
| Supra-Router-51M | ◐(偏难度) | ✅✅(51M) | ◐ 训练集小，尚嫩 | ✕(固定) | 观察 |
| Arch-Router-1.5B | ◐(model+action) | ✕(1.5B) | ✅ 但模型固定 | ✕(固定) | 二阶段备选 |
| RouteLLM | ✕(只选模型) | ◐ | ✕ 近两年无更新 | — | 不适配入口 |
| Octopus/xLAM/Hammer | ◐(只 tool 分支) | ✕(1–2B) | 参差(Hammer仅121★) | ✕ | **二阶段专用** |

## 为什么是 semantic-router？

1. **结构最契合**——route（路线）= 解决方案（agent / 搜索 / 邮件 / 模型 / 链路），用一组示例话术定义，靠嵌入相似度即时匹配，正是"按用户输入路由到解决方案"这个需求的直接映射。
2. **~0.1B + 零 LLM 调用**——入口是每一次请求都要过的关卡，必须快、确定、便宜；嵌入相似度比较天然满足这三个条件，而调一次 LLM 做路由判断本身就违背了"入口要轻"的设计初衷。
3. **是库，不是固定模型**——这是最容易被忽视的一点：底层嵌入模型可以换（MiniLM、BGE-small，甚至本地 MLX 跑的 `/v1/embeddings` 端点），换嵌入=换 provider，接口不用动。类 B/C/D 的方案大多是训练好的固定模型，换不了底座。
4. **加一条路径 = 加一条 route**，不用重新训练——扩展性对一个还在演化的入口来说是硬需求。

## 路径确定之后呢？两阶段架构

semantic-router 负责"走哪条路径"；如果这条路径是"调用一个具体工具"，再交给 xLAM-1b-fc-r / Hammer / Octopus-v2 这类端侧函数调用模型去决定"调哪个工具、传什么参数"。两者是分层关系，不是二选一——完全可以先只上路径路由，工具调用那层留到真正需要时再接。

```
用户输入 → [路径路由] semantic-router(route=解决方案) ──嵌入相似度──▶ 路径决策(agent/搜索/邮件/模型/链路)
                     │ 嵌入调用
                     ▼
              嵌入模型 = 可换 provider(本地 MLX /v1/embeddings 或 BGE-small)
                     │
                     ▼(若路径=工具调用)
              [二阶段] xLAM-1b-fc-r / Hammer / Octopus-v2 → 具体工具 + 参数
```

## 常见问题

**Q：为什么不直接用一个小 LLM 做路由判断，省得再选路由框架？**
调一次 LLM（哪怕是很小的模型）的延迟和成本，都比一次嵌入相似度计算高一个量级，而且入口路由是**每个请求都要过**的关卡，这个成本会被放大到全站流量上。嵌入路由几毫秒出结果，且结果确定可复现，LLM 判断则可能因为 temperature 或 prompt 微调而漂移。

**Q：RouteLLM 完全没用了吗？**
不是没用，是用错了地方。RouteLLM 解决的是"这个问题该用便宜模型还是贵模型回答"，这件事在架构里应该发生在**路径已经确定要调用某个模型**之后，而不是入口第一步。把它塞进入口路由,会导致"该不该调模型""调哪个模型"这两层决策被压扁成一层，扩展性会很差。

**Q：52M/51M 这种超小模型能用在生产里吗？**
Supra-Router-51M 这类项目值得持续关注，但从实测的训练集规模（992 行）和下载/点赞数据看，目前更像是一个有潜力的早期项目，而不是可以直接压测过的生产选型——观察它的下一次迭代比现在直接上生产更稳妥。

---

> 📌 参考来源：
> GitHub: aurelio-labs/semantic-router, vllm-project/semantic-router, lm-sys/RouteLLM, katanemo/plano, ulab-uiuc/LLMRouter, MadeAgents/Hammer, Not-Diamond/awesome-ai-model-routing
> HuggingFace: SupraLabs/Supra-Router-51M, katanemo/Arch-Router-1.5B, Salesforce/xLAM-1b-fc-r, chopratejas/technique-router
> 论文：arXiv 2510.08731（vLLM Semantic Router）· 2506.16655（Arch-Router）· 2404.01744（Octopus-v2）· 2410.04587（Hammer）
> GitHub/HuggingFace 数据为本文发稿前实时查询快照，仅供相对量级参考。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: If you're building a general-purpose AI entry point — a user drops a sentence and you must decide, in milliseconds and **without calling an LLM**, what to do next (hand it to a generic agent? do a web search? send an email? switch models? run a multi-model chain?) — the answer isn't "pick a smarter LLM," it's "pick the right entry router." We surveyed five categories of open-source routing solutions across GitHub and HuggingFace. Conclusion: **aurelio-labs/semantic-router** (embedding-similarity routing, ~0.1B scale, zero LLM calls, pluggable as a library) fits "path routing" far better than the more famous RouteLLM — which actually solves a different problem.

## Why "which LLM" and "what to do" are two different questions

Most people hear "AI routing" and think of RouteLLM-style **model-selection**: cheap model for easy questions, expensive model for hard ones. But a real AI entry point faces an earlier decision. A user's sentence should

- go straight to a generic agent that figures it out on its own?
- trigger a web search first?
- map to a deterministic action like "send an email" that needs no LLM at all?
- if a model call is genuinely needed, which one — or should it run through a multi-model chain?

This is **routing a *path* by meaning** — "which LLM" is just one branch, not the whole story. Conflating the two either burns an unnecessary LLM call right at the door (slow, costly) or hardcodes the routing logic into an if-else chain that can't scale.

## Research method

Followed three reproducible lines of inquiry:

- GitHub: `gh search repos "semantic router" / "llm router" / "prompt routing" --sort stars`
- HuggingFace: `GET /api/models?search={router|route|routing}&sort=downloads`
- Web: cross-checked against Not-Diamond's `awesome-ai-model-routing` list

The numbers below are live snapshots pulled via `gh repo view` and the HuggingFace API right before publishing — not copied from a secondary source.

## Five categories of open-source routers

### Category A: Embedding/semantic routers (zero LLM calls)

Flagship: **aurelio-labs/semantic-router** — no LLM call at all; a small embedding model scores similarity between user input and a set of example utterances per route, and whichever route wins gets taken. Verified **3,760 stars**, pushed 4 days ago — solidly active. In the same category, vllm-project/semantic-router uses an mmBERT-32k backbone to run 8 neural classifiers (intent, jailbreak, PII, fact-check...), verified **5,078 stars**, pushed yesterday — more production-grade but **coupled to vLLM serving**, a real cost if your stack isn't vLLM.

### Category B: Tiny purpose-built router models (emit a route label directly)

Flagship: `SupraLabs/Supra-Router-51M` on HuggingFace — 51M parameters, sequence generation that outputs a structured label like `Domain|Complexity|Math|Code|Route|Justification`. Small and fast, but verified downloads sit at **3,670** with **143 likes**, and its training set is reportedly only 992 rows — it leans more toward task-difficulty judgment than path routing, and is still early. Worth watching, not yet production-ready. `chopratejas/technique-router` routes to a "prompting technique," not a solution path — a different problem, not a substitute.

### Category C: Preference/complexity routers (really just "which LLM")

Flagship: **lm-sys/RouteLLM** — the classic weak-model/strong-model framework, verified **5,275 stars**, but its `pushedAt` timestamp sits at **August 2024** — no substantial update in almost two years. It solves model selection, not path routing; forcing it into an entry-point role is a category error. `katanemo/Arch-Router-1.5B` is a 1.5B generative model that routes by Domain+Action preference, verified **1,471 downloads** and **270 likes** — a fixed model (no swappable backbone), heavier and less flexible than the embedding approach. Its surrounding agent framework, `katanemo/plano`, is genuinely active though — verified **6,910 stars**, pushed yesterday.

### Category D: On-device function/tool-calling models (route → specific tool + args)

Flagship examples: Octopus-v2 (Nexa AI, 2B, functional-token on-device function calling), `Salesforce/xLAM-1b-fc-r` (1B Large Action Model, verified **3,758 downloads**), and `MadeAgents/Hammer` (0.5–3B, function masking to resist irrelevant-function interference) — though Hammer verified at only **121 stars**, last pushed **June 2025**, far less momentum than it first appeared. This category isn't about deciding which path to take — it kicks in **after** the path is already "call a tool," deciding which tool and what arguments. It's a second stage layered on top of path routing, not a substitute for it.

### Category E: Routing frameworks/proxies (infrastructure, not "the model")

`katanemo/plano`, ClawRouter, NadirClaw, UncommonRoute, WilmerAI, openziti/llm-gateway, and the `Not-Diamond/awesome-ai-model-routing` list itself (verified **234 stars**, last updated March 2025, still one of the most complete indexes in this space). These are runtimes/gateways that carry routing logic — not routing models themselves, and shouldn't be benchmarked against the first four categories directly.

## Comparison matrix

| Option | Path routing | ~0.1B/no-LLM | Activity (verified) | Pluggable | Verdict |
|---|:--:|:--:|:--:|:--:|:--:|
| **semantic-router (aurelio)** | ✅ | ✅ | ✅ pushed 4 days ago, 3.7k★ | ✅✅ swappable embeddings | **★ Recommended** |
| vLLM semantic-router | ✅ | ◐(0.3B) | ✅✅ pushed yesterday, 5k★ | ◐ coupled to vLLM | Backup (heavier) |
| Supra-Router-51M | ◐(difficulty-leaning) | ✅✅(51M) | ◐ small training set, early | ✕(fixed) | Watch |
| Arch-Router-1.5B | ◐(model+action) | ✕(1.5B) | ✅ but model fixed | ✕(fixed) | Stage-2 backup |
| RouteLLM | ✕(model-selection only) | ◐ | ✕ no update in ~2 years | — | Wrong layer for entry |
| Octopus/xLAM/Hammer | ◐(tool branch only) | ✕(1–2B) | Mixed (Hammer only 121★) | ✕ | **Stage-2 only** |

## Why semantic-router wins

1. **Structural fit** — a route *is* a solution path (agent / search / email / model / chain), defined by example utterances and matched instantly by embedding similarity. That's a direct mapping to "route user input to a solution."
2. **~0.1B and zero LLM calls** — the entry point is a gate every single request passes through; it has to be fast, deterministic, and cheap. Embedding comparison satisfies all three; calling an LLM to make the routing decision itself defeats the point of keeping the entry point light.
3. **It's a library, not a fixed model** — easy to overlook, but this is the key differentiator: the underlying embedding model is swappable (MiniLM, BGE-small, even a local MLX `/v1/embeddings` endpoint). Swap the embedding, swap the provider — the interface doesn't change. Most Category B/C/D options are trained, fixed models with no swappable backbone.
4. **Adding a path = adding a route**, no retraining required — critical extensibility for an entry point that's still evolving.

## What happens after the path is decided? A two-stage architecture

semantic-router decides *which path to take*. If that path is "call a specific tool," the decision hands off to an on-device function-calling model like xLAM-1b-fc-r, Hammer, or Octopus-v2 to decide *which tool and what arguments*. The two are layered, not competing — you can ship path routing alone and add the tool-calling layer only when you actually need it.

```
User input → [Path routing] semantic-router(route=solution) ──embedding similarity──▶ Path decision(agent/search/email/model/chain)
                     │ embedding call
                     ▼
              Embedding model = swappable provider (local MLX /v1/embeddings or BGE-small)
                     │
                     ▼(if path = tool call)
              [Stage 2] xLAM-1b-fc-r / Hammer / Octopus-v2 → specific tool + arguments
```

## FAQ

**Q: Why not just use a tiny LLM to make the routing decision and skip picking a router framework?**
Even a small LLM call costs an order of magnitude more in latency and price than an embedding-similarity computation — and the entry router sits on **every single request**, so that cost gets multiplied across all traffic. Embedding routing resolves in milliseconds with deterministic, reproducible results; LLM-based judgment can drift with temperature or prompt tweaks.

**Q: Is RouteLLM useless, then?**
Not useless — misapplied. RouteLLM answers "should this be handled by a cheap model or an expensive one," a decision that belongs **after** the path is already determined to be "call a model," not at the very first entry-point decision. Squeezing it into the entry layer collapses two distinct decisions ("should we call a model at all" and "which model") into one, hurting extensibility.

**Q: Can a 51M/52M-parameter model actually go to production?**
Supra-Router-51M is worth watching, but given its verified training-set size (992 rows) and current download/like numbers, it currently looks more like a promising early-stage project than a battle-tested production choice — better to watch its next iteration than to ship it today.

---

> 📌 Sources:
> GitHub: aurelio-labs/semantic-router, vllm-project/semantic-router, lm-sys/RouteLLM, katanemo/plano, ulab-uiuc/LLMRouter, MadeAgents/Hammer, Not-Diamond/awesome-ai-model-routing
> HuggingFace: SupraLabs/Supra-Router-51M, katanemo/Arch-Router-1.5B, Salesforce/xLAM-1b-fc-r, chopratejas/technique-router
> Papers: arXiv 2510.08731 (vLLM Semantic Router), 2506.16655 (Arch-Router), 2404.01744 (Octopus-v2), 2410.04587 (Hammer)
> GitHub/HuggingFace figures are live snapshots taken right before publishing, for relative-scale reference only.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
