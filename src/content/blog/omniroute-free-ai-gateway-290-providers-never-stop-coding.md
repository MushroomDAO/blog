---
title: "OmniRoute：290 个 AI 提供商、一个端点、永不限流——免费 AI 网关的暴力美学"
titleEn: "OmniRoute: 290 AI Providers, One Endpoint, Never Hit Limits — The Free AI Gateway"
description: "diegosouzapw/OmniRoute，27824 stars，MIT，5个月 500+ 贡献者。一个端点路由到 290+ AI 提供商（90+ 免费），4层自动 fallback 级联，19种路由策略，RTK+Caveman 压缩节省 15-95% tokens，MCP 104工具，~1.53B 免费 tokens/月。"
descriptionEn: "diegosouzapw/OmniRoute, 27,824 stars, MIT, 5 months, 500+ contributors. One endpoint routing to 290+ AI providers (90+ free), 4-tier auto-fallback cascade, 19 routing strategies, RTK+Caveman compression saves 15-95% tokens, 104 MCP tools, ~1.53B free tokens/month."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI网关", "开源", "Claude Code", "免费AI", "路由", "MCP", "token压缩", "开发工具"]
heroImage: "../../assets/images/omniroute-free-ai-gateway-290-providers-never-stop-coding-banner.jpg"
---

> **仓库**：diegosouzapw/OmniRoute · TypeScript · MIT · 27824 stars
> **最新版本**：v3.8.48（2026-07-13）
> **创建时间**：2026-02-13（5个月，500+ 贡献者）
> **官网**：omniroute.online · **端点**：`http://localhost:20128/v1`

---

## 一、它解决什么问题

凌晨 2 点在写代码，Claude Code 的配额用完了。

你的选择通常是：等重置、换个 API key、去 OpenRouter 注册一个账号。这个流程每次都要打断你的思路。

OmniRoute 的答案是：**你根本不应该遇到这个问题**。

它在本地运行一个 AI 网关，把你能用的所有 AI 来源——订阅账号、API key、免费 tier、零配置免费提供商——组合成一个端点，按你配置的策略自动故障转移。配额用完了，自动切到下一个。你的工具感知不到任何变化。

---

## 二、规模

- **290+ 提供商**，500+ 模型（Kimi、Claude、GPT、Gemini、GLM、DeepSeek、MiniMax……）
- **90+ 免费提供商**，其中 40+ 是永久免费（不需要注册，不需要 key）
- **~1.53B 免费 tokens/月**：聚合 43 个提供商池 / 460+ 模型的文档化免费 tier，在 dashboard 实时显示剩余量
- **零配置就能用**：安装后 `auto` 模式立即可用，内置接了 OpenCode Free 和 Felo 等无 key 提供商

```bash
# 安装后无需任何配置——auto 立即响应
curl http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Hello!"}]}'
```

支持的 AI coding 工具：Claude Code、Codex、Cursor、OpenCode、Cline、Copilot，以及所有 OpenAI API 兼容的客户端。

---

## 三、4 层自动 Fallback

OmniRoute 把所有来源按优先级分成 4 层：

```
Tier 1 订阅账号 ─── Claude Code / Codex / Copilot（最贵但最快）
         ↓ 配额用完
Tier 2 API Key ────── DeepSeek / Groq / xAI（付费 API，便宜）
         ↓ 预算触碰
Tier 3 廉价 ──────── GLM($0.5) / MiniMax($0.2)
         ↓ 预算触碰
Tier 4 免费 ──────── Kiro / Qoder / Pollinations（零成本）
```

在你的工具看来，这始终是同一个端点 `localhost:20128/v1`，模型名 `auto`。切换对工具完全透明。

---

## 四、19 种路由策略

这是 OmniRoute 和简单代理最大的工程差距。

**零配置的 `auto` 变体**：

| 模型 ID | 优化目标 |
|---------|---------|
| `auto` | 平衡（LKGP——粘性上次成功路径）|
| `auto/coding` | 代码生成质量优先 |
| `auto/fast` | 最低延迟优先 |
| `auto/cheap` | 最低 token 成本优先 |
| `auto/offline` | 最多剩余配额优先 |
| `auto/smart` | 质量优先 + 10% 探索发现更好模型 |

**可自定义 Combo 的 19 种策略**（选几个有意思的）：

- **`context-relay`**：跨目标传递对话上下文——长对话自动切 provider 时保持连贯
- **`cache-optimized`**：把同一个可复用 prompt 前缀锁定在同一个账号，最大化 prompt cache 命中率
- **`lkgp`**：Last-Known-Good Path，粘性到上次成功的目标
- **`fusion`**：把请求扇出到多个模型，用一个 judge 把多个答案合成一个——用于高质量任务
- **`pipeline`**：链式执行，上一步输出是下一步输入——用于多步骤工作流
- **`quota-share`**：一个订阅账号在团队成员间按权重公平分配配额（weight 50/30/20），支持 hard/soft/burst 模式

---

## 五、RTK + Caveman 压缩

OmniRoute 在发请求之前对 token 做压缩，自称节省 15-95%，工具密集型 session 平均 ~89%。

这个数字如果属实，意义非常大——特别是对 Claude Code 这样工具调用很多的场景：每次工具调用的参数和返回结果可能占大量 token，如果能压缩掉 89%，等效于你的配额变成 9 倍。

两层叠加：RTK（基于工具调用特征的压缩）和 Caveman（通用文本压缩）。

---

## 六、MCP Server + A2A

OmniRoute 不只是一个代理，它自己也是一个 MCP 服务端：

- **104 个 MCP 工具**，3 种传输方式，31 个 scope
- **A2A（Agent-to-Agent）**：6 个 skill，JSON-RPC 2.0——Agent 可以互相调用

这意味着：Claude Code 或 Cursor 可以把 OmniRoute 当成一个 MCP server 接入，直接获得 OmniRoute 的路由能力和工具库。

---

## 七、3 层弹性

三个独立的自愈层，对应三个粒度的故障：

**Layer 1 — Provider 断路器**（整个提供商级别）
只在 408/5xx 时触发，阈值是 OAuth 3次/API key 5次/本地 2次，重置 60s/30s/15s 后进入 HALF-OPEN 探测，恢复后继续路由。

**Layer 2 — Connection 冷却**（单 key/账号级别）
429 时遵守 Retry-After，基础冷却 5s(OAuth)/3s(API key)，指数退避 ×2，同池其他 key 继续服务。

**Layer 3 — Model 锁定**（单模型级别）
一个模型的 429 或 404 只锁定这个模型，不影响同 provider 的其他模型。

---

## 八、数字

- 27,824 stars，3,655 forks
- 2026-02-13 创建——**5个月做到 2.7 万 stars**
- 500+ 贡献者，文档已翻译成 43 种语言
- 175 open issues，61 open PRs
- v3.8.48——版本号说明已经迭代了几百次
- npm 包 `omniroute`，Docker Hub 镜像，Electron 桌面应用，PWA

---

## 九、判断

OmniRoute 踩在了一个真实的开发者痛点上：**配额限流打断工作流**。这个问题在 AI 工具高度普及的 2026 年越来越普遍——Claude Code、Codex、Cursor 同时开着，配额消耗比以前快 10 倍。

5 个月 2.7 万 stars，500+ 贡献者，这个增速不是靠一次 HN 首页驱动的，是持续的真实需求驱动。

**几个值得关注的细节**：

- **Kimi（Moonshot AI）是 Founding Open Source Friend**：Kimi K3 的 API credits 支持了 OmniRoute 的 merge validation pipeline——每个 PR 合并前都用 Kimi K3 做 AI review。这是一个务实的开源赞助关系：不是 logo 赞助，是真实集成进 CI/CD。

- **RTK+Caveman 的 89% 压缩率**：README 里有 CI gate 保证文档数字和代码实际输出一致，不是随意填写的。如果在工具密集型 session 里真的能平均省 89%，这是比"多几个免费提供商"更重要的价值。

- **Quota-Share 机制**：对于用同一个 Claude Max 订阅开着 4 个 Claude Code 窗口的开发者来说，Quota-Share 可以让每个窗口有公平的配额份额而不是互相抢。

和 Osaurus（本地哈尼斯）、OpenWorker（桌面工作助手）相比，OmniRoute 的定位是更底层的基础设施：它不关心你用 AI 做什么，只保证你的 AI 调用永远有地方可去。

**不确定的地方**：
- 290 个提供商里有多少是真正可用的（不是只在 provider list 里但实际要翻墙或有地区限制）？
- RTK+Caveman 的压缩对不同类型的任务效果差异有多大？非工具密集型场景是否值得开？
- 免费 tier 的 1.53B tokens 背后的 QPS 限制怎么分布？高峰时段是否会遇到整体降速？

**总结**：如果你在用 Claude Code / Cursor / Codex，OmniRoute 是值得 5 分钟试一次的基础设施工具——最坏情况是白装了，最好情况是你的配额有效扩大了 10 倍。

---

*数据来源：GitHub diegosouzapw/OmniRoute，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: diegosouzapw/OmniRoute · TypeScript · MIT · 27,824 stars
> **Latest Release**: v3.8.48 (2026-07-13)
> **Created**: 2026-02-13 (5 months, 500+ contributors)
> **Homepage**: omniroute.online · **Endpoint**: `http://localhost:20128/v1`

---

## 1. What Problem It Solves

It's 2 AM. You're deep in a coding session and Claude Code's quota runs out.

Your usual options: wait for the reset, swap in a different API key, sign up for an OpenRouter account. Every path breaks your flow.

OmniRoute's answer: **you shouldn't hit this problem in the first place.**

It runs a local AI gateway that combines every AI source you have access to — subscriptions, API keys, free tiers, zero-config keyless providers — into one endpoint, automatically failing over according to whatever strategy you configure. When one quota runs dry, it silently routes to the next. Your tools see nothing change.

---

## 2. The Scale

- **290+ providers**, 500+ models (Kimi, Claude, GPT, Gemini, GLM, DeepSeek, MiniMax…)
- **90+ free providers**, 40+ free forever (no signup, no key required)
- **~1.53B free tokens/month**: aggregates documented free tiers from 43 provider pools / 460+ models, shown live on the dashboard
- **Zero-config from install**: `auto` mode responds immediately — OpenCode Free and Felo are wired in out of the box with no keys

```bash
# After install, no credentials needed — auto responds immediately
curl http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Hello!"}]}'
```

Supported AI coding tools: Claude Code, Codex, Cursor, OpenCode, Cline, Copilot, and any OpenAI-compatible client.

---

## 3. The 4-Tier Auto-Fallback Cascade

OmniRoute ranks all sources into four priority tiers:

```
Tier 1 Subscription ── Claude Code / Codex / Copilot (best quality)
        ↓ quota exhausted
Tier 2 API Key ──────── DeepSeek / Groq / xAI (paid, inexpensive)
        ↓ budget hit
Tier 3 Cheap ──────── GLM($0.5) / MiniMax($0.2)
        ↓ budget hit
Tier 4 Free ────────── Kiro / Qoder / Pollinations (zero cost)
```

From your tool's perspective, this is always one endpoint at `localhost:20128/v1`, model name `auto`. Provider switches are completely transparent.

---

## 4. 19 Routing Strategies

This is the biggest engineering gap between OmniRoute and simple proxies.

**Zero-config `auto` variants:**

| Model ID | Optimizes for |
|----------|---------------|
| `auto` | Balanced (LKGP — sticky to last successful path) |
| `auto/coding` | Code generation quality first |
| `auto/fast` | Lowest latency first |
| `auto/cheap` | Lowest per-token cost first |
| `auto/offline` | Most remaining quota first |
| `auto/smart` | Quality-first + 10% exploration to discover better models |

**Notable strategies for custom Combos:**

- **`context-relay`**: Hands off conversation context across targets — long conversations stay coherent when switching providers mid-session
- **`cache-optimized`**: Pins the same reusable prompt prefix to the same account to maximize prompt-cache hit rate
- **`lkgp`**: Last-Known-Good Path — sticky to the last successful target
- **`fusion`**: Fans out to a panel of models, a judge synthesizes one answer — for high-quality critical tasks
- **`pipeline`**: Chain execution where each target's output feeds the next — for multi-step workflows
- **`quota-share`**: Distributes one subscription's quota fairly across team members by weight (e.g. 50/30/20), with hard/soft/burst modes

---

## 5. RTK + Caveman Compression

OmniRoute compresses tokens before sending requests. The claimed savings: 15–95%, averaging ~89% on tool-heavy sessions.

If this holds in practice, the implications are significant — especially for Claude Code and Cursor, where tool calls dominate token count: every tool call's parameters and return values can consume large amounts of context. If 89% of that compresses away, your effective quota becomes roughly 9× larger.

Two layers stacked: RTK (compression tuned for tool-call patterns) and Caveman (general-purpose text compression). The README notes a CI gate (`check:docs-counts`) that fails the build if the documented numbers drift from what the code actually produces — these aren't figures someone typed by hand.

---

## 6. MCP Server + A2A

OmniRoute isn't just a proxy — it also runs as an MCP server itself:

- **104 MCP tools**, 3 transport types, 31 scopes
- **A2A (Agent-to-Agent)**: 6 skills, JSON-RPC 2.0 — agents can call each other

This means Claude Code or Cursor can connect to OmniRoute as an MCP server and gain access to OmniRoute's routing capabilities and tool library directly.

---

## 7. Three-Layer Resilience

Three independent self-healing layers, each targeting a different failure granularity:

**Layer 1 — Provider circuit breaker** (entire provider level)
Trips only on 408/5xx: thresholds at OAuth 3× / API key 5× / local 2×. Resets into HALF-OPEN probe at 60s/30s/15s, then lazy recovery. While OPEN, the combo reroutes to the next provider.

**Layer 2 — Connection cooldown** (single key/account level)
429 responses honor Retry-After. Base cooldown 5s (OAuth) / 3s (API key), exponential ×2 backoff. A cooling key is skipped; sibling keys keep serving.

**Layer 3 — Model lockout** (single model level)
A 429 or 404 on one model locks only that model — never the whole connection or provider.

---

## 8. Numbers

- 27,824 stars, 3,655 forks
- Created 2026-02-13 — **2.7K stars in 5 months**
- 500+ contributors, docs translated into 43 languages
- 175 open issues, 61 open PRs
- v3.8.48 — the version number signals hundreds of iterations already
- Available as npm package, Docker Hub image, Electron desktop app, and PWA

---

## 9. Assessment

OmniRoute targets a real developer pain point: **rate-limit interruptions breaking flow.** This is increasingly common in 2026 as AI tools proliferate — running Claude Code, Codex, and Cursor simultaneously burns quota roughly 10× faster than before.

2.7K stars in 5 months with 500+ contributors isn't driven by one HN front page. That's sustained real-world demand.

**A few details worth noting:**

- **Kimi (Moonshot AI) is the Founding Open Source Friend**: Kimi K3 API credits power OmniRoute's merge validation pipeline — every PR gets AI-reviewed by Kimi K3 before shipping. This is a practical sponsorship relationship, not logo placement: it's actually integrated into CI/CD.

- **The 89% RTK+Caveman compression figure**: The README includes a CI gate that fails the build if the documented numbers drift from what the code computes. These aren't marketing estimates. If they hold in tool-heavy sessions, this is more valuable than access to more free providers.

- **Quota-Share**: For developers running 4 Claude Code windows against one Claude Max subscription, Quota-Share can give each window a fair share of the quota rather than having them compete.

Compared with Osaurus (local Mac harness) and OpenWorker (desktop work assistant), OmniRoute sits at a lower layer of the stack: it doesn't care what you do with AI, only that your AI calls always have somewhere to go.

**Open questions:**
- Of the 290 providers, how many are actually accessible without VPN or regional restrictions?
- How does RTK+Caveman compression vary by task type? Is it worth enabling for non-tool-heavy sessions?
- How does QPS distribute across the 1.53B free tokens? Will peak-hour usage hit aggregate slowdowns?

**Bottom line**: If you use Claude Code, Cursor, or Codex, OmniRoute is worth a 5-minute trial as infrastructure. Worst case: you installed something you don't need. Best case: your effective quota just expanded by 10×.

---

*Data source: GitHub diegosouzapw/OmniRoute, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
