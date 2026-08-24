---
title: "treg：Agent 工具的 OpenRouter，一个入口调用 2850+ 个真实世界 API"
titleEn: "treg-openrouter-agent-tools-unified-api-credential-proxy"
description: "Superdesign 团队开源 treg——「OpenRouter for Agent Tools」。一个 token、一个入口，访问约 57 家数据服务商的 2850+ 个接口，覆盖 SEO 外链、社交趋势、人员/公司信息、广告、抓取等。按次计费（最低几分钱），无需注册供应商账号。同时支持团队自有 API Key 共享，让所有人的 Agent 都能使用同一套已有能力，而无需把密钥交出去。Apache 2.0，可自托管。"
descriptionEn: "Superdesign's open-source treg — 'OpenRouter for Agent Tools'. One token, one entry point, access to 2,850+ endpoints across ~57 providers — SEO & backlinks, social & trends, people & company enrichment, ads, scraping. Per-call billing from a cent, no provider account needed. Also supports team API key sharing so every teammate's agent can use shared credentials without the key ever leaving the server. Apache 2.0, self-hostable."
pubDate: "2026-08-24"
updatedDate: "2026-08-24"
category: "Tech-News"
tags: ["开源", "Agent工具", "API代理", "MCP", "Developer-Tools", "treg", "Superdesign", "凭证管理"]
heroImage: "../../assets/images/treg-openrouter-agent-tools-unified-api-credential-proxy-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：superdesigndev/treg  
Stars：574 | Forks：53 | Language：Python  
License：Apache 2.0（附加条款：禁止作为第三方托管/商业产品销售）  
Live：https://treg.to | Discord：https://discord.gg/6mQYYfFMAn  
创建：2026-07-15 | 最近更新：2026-08-24

---

## 一句话理解 treg

**OpenRouter 解决了「调哪个模型」的问题；treg 解决「用哪个工具、谁的账号」的问题。**

前者让你用一个入口调用 OpenAI、Anthropic、Gemini……后者让你的 Agent 用一个入口调用 Semrush、Crunchbase、Apollo、TikTok、Google Ads……

一个 `X-Treg-Token` 头，一个 base URL，之后 Agent 按任务描述搜工具，看价格，直接调用，无需你提前知道该买哪家的订阅、也无需自己持有 API Key。

---

## 它解决的真实痛点

做 Agent 的人都遇过这个问题：

- 想查一个网站的外链 → 需要 Semrush 账号（$139/月）
- 想看海外视频趋势 → 需要 TikTok Research API（需要申请资质）
- 想拉公司联系人 → 需要 Apollo 账号（$59/人/月）
- 就查一次，为这件事买整月订阅，划不来

treg 把这些账号统一托管，按调用次数分摊成本。一次视频数据查询大约只需几美分，不需要为偶发需求买月度订阅。

另一个场景：团队里只有一个人维护 SEO 工具和 API 账号，其他成员的 Agent 根本用不上这套能力——除非把密钥分发给所有人（不安全）。treg 的团队模式让密钥留在服务端，所有团队成员的 Agent 都能通过各自的 token 调用，密钥本身从不出服务器。

---

## 两种工具，一个 token

treg 把可调用的东西分成两类：

| 类型 | 说明 | 谁的密钥 |
|------|------|---------|
| **目录（Catalog）** | treg 持有账号的约 57 家供应商，2850+ 个接口 | treg 的，按调用计费 |
| **你自己的工具** | 你或团队注册的 API Key、OAuth 连接、CLI、SKILL.md | 你的，不计费 |

**自己的密钥永远优先**：如果你的团队已经有了某个供应商的账号，注册到 treg 后，调用该供应商的接口走你自己的 Key，不走 treg 的余额。

新团队有 $1.00 免费额度可以直接开始探索。

---

## 核心能力四块

### 1. 按任务搜工具，而不是按供应商

```bash
treg catalog search "backlinks for a domain"   # 找外链工具
treg catalog search "find a work email"         # 找企业邮箱工具
treg catalog search "海外视频平台内容趋势"       # 找内容趋势工具
```

返回匹配的供应商列表，带价格和示例响应，你来选，treg 不自动替你挑或降级。

### 2. 直接调用，无需持有密钥

```bash
# 查外链
treg call hunter.people.email.find --query domain=reddit.com --query full_name="Alexis Ohanian"

# 调用已注册的 API（透明代理，只注入认证）
GET https://treg.to/call/https://api.intercom.io/conversations?per_page=5
    Header: X-Treg-Token: <your_token>
```

代理只做三件事：注入认证、剥离 treg 自身的控制头、流式转发。其他一切原样。

### 3. 团队密钥共享（三类工具都支持）

**HTTP API（Endpoint）**
```bash
treg secret add STRIPE_KEY --value sk_live_123
treg add stripe --base-url https://api.stripe.com --secret STRIPE_KEY
```

**CLI 工具**（stripe CLI / gh / vercel 等）
```bash
treg run stripe -- get /v1/balance   # 注入密钥，本地执行
treg run gh -- pr list
treg shell start                     # 开一个子 shell，所有 CLI 自动注入
```

**Skills（SKILL.md 技能包）**
```bash
treg upload skills --dir ~/.claude/skills --all  # 批量注册
treg skill install seo-blog-writer               # 拉取团队共享的 skill
```

### 4. 作为 Claude Code 插件安装

```
/plugin marketplace add superdesigndev/treg
/plugin install treg@treg
```

安装后 Agent 第一次运行时会引导你完成 CLI 安装、登录和 MCP 配置，结束后就有了完整的命令行 + MCP 工具两套接口。

其他 Agent 框架：`npx skills add superdesigndev/treg -s treg`

---

## 架构要点

**认证注入模型**（4 种 injector 形态）：

| Injector | 适用场景 |
|----------|---------|
| `env` | 普通字符串 API Key，直接注入 header/query |
| `secret_file` | JSON token 文件，提取特定字段注入 |
| `oauth` | OAuth token，自动刷新，无需重新登录 |
| `cli_auth` | 从 CLI keychain 提取凭证 |

**代理合约**：代理只改三件事——逐跳传输头（每跳重新推导）、treg 自己的控制头（剥离，不透传给上游）、注入的凭证。其他所有请求内容原样转发，包括 body 流式。

**目录调用优先级**（从高到低）：
1. 你的团队注册了该供应商自己的工具 → 用团队工具 + 团队密钥
2. 你的团队存了该供应商的 secret → 注入 secret，通过虚拟工具转发
3. 以上都没有 → 走 treg 自己的密钥，计费到团队余额

余额耗尽返回 HTTP 402，携带 `balance_micro`、`estimated_cost_micro`、`topup_url`，Agent 可直接解析，无需读错误文案。

---

## 自托管

treg 完整开源，一条命令本地起来（需要 tmux + uv）：

```bash
scripts/dev-local.sh up   # 本地服务在 http://localhost:18790
```

生产部署用 Postgres 替换 SQLite，设好 Fernet 密钥（`TREG_SECRET_KEY`）、公开 URL 和 OAuth 配置即可。SQLite 适合小团队本地跑，Postgres 适合团队共享部署。

**官方实例**托管在 Render，地址是 [treg.to](https://treg.to)，$1.00 免费额度，注册即用。

---

## 路线图

官方已计划：MCP 原生支持、更细粒度的权限层、密钥管理增强、可能与 Loopni 合并。

---

## 为什么这个方向有意思

**问题的本质是工具碎片化**。现在一个"做事情"的 Agent，需要整合十几家服务商的账号：爬虫用一家、SEO 用一家、联系人信息用一家、广告数据用一家……每个都要注册、付费、持有密钥、维护凭证刷新。这个管理成本随着 Agent 数量线性增长。

treg 做的是把这个管理层抽离出来集中处理。思路和 OpenRouter 一样——不是提供一个更好的供应商，而是成为供应商之上的路由层。

**对团队的价值**在于凭证统一管控。所有 Agent 调用都有审计日志（`treg calls`），密钥从不出服务器，团队成员各自持有自己的 token（可按工具粒度限权），不需要把 API Key 贴在 .env 里到处传。

**开源 + 自托管**意味着你可以把整套东西跑在自己的基础设施上，连 treg 的服务器都不需要信任。

---

**相关链接**

- GitHub：https://github.com/superdesigndev/treg
- 官方实例：https://treg.to
- Discord：https://discord.gg/6mQYYfFMAn
- CLI 参考：https://github.com/superdesigndev/treg/blob/main/USAGE.md
- Agent 上手文档：https://treg.to/llms.txt

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## treg: OpenRouter for Agent Tools — One Token, 2,850+ Real-World APIs

*by Mycelium Protocol*

---

GitHub: superdesigndev/treg  
Stars: 574 | Forks: 53 | Language: Python  
License: Apache 2.0 (extra terms: no resale as a hosted/managed service)  
Live: https://treg.to | Discord: https://discord.gg/6mQYYfFMAn  
Created: 2026-07-15 | Updated: 2026-08-24

---

### The One-Line Version

**OpenRouter solved "which model." treg solves "which tool, whose account."**

One entry point, one `X-Treg-Token` header. An agent can search by task, see pricing, and call ~57 providers' 2,850+ endpoints — SEO and backlinks, social trends, people and company enrichment, ads, scraping — without holding any provider account or API key.

---

### The Real Pain It Solves

Anyone building agents has hit this:

- Need backlink data → Semrush ($139/mo)
- Need overseas video trends → TikTok Research API (requires application)
- Need company contact info → Apollo ($59/seat/month)
- Run one query, buy a whole month's subscription

treg holds those accounts and splits the cost per call. A single video data query costs a few cents.

The other scenario: one person on your team maintains the SEO credentials. Everyone else's agents can't use those capabilities — unless you distribute the API key (insecure). treg's team mode keeps keys server-side; every teammate's agent calls through their own token, and the actual credential never leaves the server.

---

### Two Kinds of Tools, One Token

| Type | Description | Whose key |
|------|-------------|-----------|
| **Catalog** | ~57 providers, 2,850+ endpoints held by treg | treg's, billed against team balance |
| **Your tools** | Keys/OAuth/CLIs/skills your team registered | Yours, never metered |

Your own credentials always win. If your team already has a subscription with a provider, registering that key means calls to that provider use your key — not treg's balance.

New teams get $1.00 free credit to start exploring.

---

### Four Core Capabilities

**1. Search by task, not by vendor**

```bash
treg catalog search "backlinks for a domain"
treg catalog search "find a work email"
treg catalog search "trending social content"
```

Returns matching providers with pricing and example responses. You choose — treg doesn't silently pick for you or fail over.

**2. Call directly, hold no key**

```bash
treg call hunter.people.email.find \
  --query domain=reddit.com \
  --query full_name="Alexis Ohanian"
```

Or the passthrough URL form — any upstream request prefixed with `https://treg.to/call/`:

```
GET https://treg.to/call/https://api.intercom.io/conversations?per_page=5
    X-Treg-Token: <your_token>
```

The proxy injects auth, strips treg's own control headers, streams everything else verbatim.

**3. Team credential sharing (all three tool types)**

*HTTP API endpoints*: register a secret + base URL, teammates call it via their token without seeing the key.

*CLI tools* (`stripe`, `gh`, `vercel`, …): `treg run stripe -- get /v1/balance` injects the org credential locally. `treg run --server` runs on the registry server, so the key never reaches the caller.

*Skills* (SKILL.md recipe bundles): `treg upload skills` to share, `treg skill install` to pull — all API calls in the skill go through treg with credential injection.

**4. Claude Code plugin**

```
/plugin marketplace add superdesigndev/treg
/plugin install treg@treg
```

On first run the skill walks through CLI install, sign-in, and MCP setup automatically.

Other agent frameworks: `npx skills add superdesigndev/treg -s treg`

---

### Architecture Notes

**Four credential injectors**: `env` (API key → header/query), `secret_file` (pull field from JSON token), `oauth` (auto-refresh, no re-login), `cli_auth` (lift from CLI keychain).

**Faithful-relay contract**: the proxy changes only three things — hop-by-hop transport headers, treg's own control headers (stripped), and the injected credential. Everything else is verbatim streaming.

**Catalog call priority** (highest first):
1. Team registered its own tool for the provider → that tool, that key
2. Team stored a secret for the provider → virtual tool + injected secret
3. Neither → treg's key, billed to team balance

Out-of-balance returns HTTP 402 with structured fields (`balance_micro`, `estimated_cost_micro`, `topup_url`) — machine-parseable, no prose required.

---

### Self-Hosting

Full source, one-command local start (needs tmux + uv):

```bash
scripts/dev-local.sh up   # server at http://localhost:18790
```

Production: swap SQLite for Postgres, set `TREG_SECRET_KEY`, `TREG_PUBLIC_URL`, OAuth client IDs. The official instance runs on Render at [treg.to](https://treg.to).

**521 tests**, covering: proxy relay, all injector shapes, per-user auth + CRUD + audit, skill composer, URL passthrough, OAuth refresh, health checks, `treg run`/shell, upload/scan, orgs + invites.

---

### Why This Direction Is Interesting

The underlying problem is tool fragmentation. A useful agent today needs a dozen provider accounts: scraping from one, SEO from another, contact enrichment from a third, ad data from a fourth. Each requires signup, payment, key management, and credential refresh. That overhead scales linearly with agent count.

treg abstracts that management layer out. The pattern mirrors OpenRouter — not a better provider, but a routing layer above providers.

**Team value**: all agent calls have an audit log (`treg calls`), keys never leave the server, teammates get individual tokens with per-tool access controls — no API keys in `.env` files circulating through Slack.

**Open-source + self-hostable**: the whole thing can run on your own infrastructure. You don't have to trust even treg's server.

---

**Links**

- GitHub: https://github.com/superdesigndev/treg
- Live instance: https://treg.to
- Discord: https://discord.gg/6mQYYfFMAn
- CLI reference: https://github.com/superdesigndev/treg/blob/main/USAGE.md
- Agent onboarding: https://treg.to/llms.txt

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
