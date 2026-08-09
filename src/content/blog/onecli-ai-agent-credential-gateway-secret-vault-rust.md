---
title: "OneCLI：让 AI Agent 永远看不到真实密钥的开源凭证网关"
titleEn: "OneCLI: The Open-Source Credential Gateway That Keeps Real Keys Away from AI Agents"
description: "onecli/onecli，2746 stars，Apache-2.0，Rust + TypeScript。在 agent 和 API 之间插一个 MITM 网关，agent 只持有占位符，网关透明注入真实凭证。HN 两次上榜，NanoClaw 和 Bitwarden 均已集成。一行命令本地跑起来。"
descriptionEn: "onecli/onecli, 2,746 stars, Apache-2.0, Rust + TypeScript. A MITM gateway between your agents and APIs — agents hold placeholder keys, the gateway transparently injects real credentials. Twice on HN front page. NanoClaw and Bitwarden both integrated."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI安全", "AI Agent", "开源", "Rust", "密钥管理", "安全工具", "网关", "MCP"]
heroImage: "../../assets/images/onecli-ai-agent-credential-gateway-secret-vault-rust-banner.jpg"
---

> **仓库**：onecli/onecli · TypeScript + Rust · Apache-2.0 · 2746 stars
> **官网**：onecli.sh
> **HN 首发**：2026-03-12（161pts） · **最新帖**：2026-07-23（102pts）
> **生态集成**：NanoClaw（112pts）· Bitwarden SDK（63pts）

---

## 一、问题：每个 agent 都拿着真实密钥

当你开始认真地用 AI agent 做自动化工作——调 GitHub API、发 Slack 消息、操作 Notion 数据库、查询各种 SaaS——你会面对一个越来越难忽视的安全问题：

**每个 agent 手里都攥着一堆真实的 API key。**

这些 key 通常以明文写在 `.env` 文件、系统环境变量，或者直接写进提示词。一旦某个 agent 的上下文被泄露、被截获、或者被提示注入攻击劫持，所有凭证就跟着暴露了。

传统解法是把 key 存在密钥管理服务（Vault、AWS Secrets Manager）里，但这只解决了"静态存储"问题——到了 runtime，key 还是要被取出来交给 agent，agent 还是拿着明文 key 去调 API。

OneCLI 选择在架构层面绕开这个问题。

---

## 二、解法：不交给 agent，替它注入

OneCLI 在 agent 和目标 API 之间插入一个网关。工作流是这样的：

```
Agent → [placeholder key] → OneCLI Gateway → [real key injected] → GitHub / Slack / Any API
```

1. 你把真实 API 凭证存在 OneCLI 里（AES-256-GCM 加密，静态不解密）
2. 给 agent 一个占位符，比如字面量 `FAKE_KEY_GITHUB`
3. Agent 按正常逻辑发起 HTTP 请求，带着这个假 key
4. 请求经过 OneCLI 的 Rust 网关时，网关匹配 host/path 规则，把假 key 替换成真 key，实时解密注入
5. 真实请求发往 GitHub，带的是真实凭证
6. Agent 从头到尾没有接触过真实密钥

HN 评论区有人精准指出了这个方法和 Vault 的本质区别：

> "Vault 保护静态存储的 key，但 agent 在运行时仍然拿到明文。代理方案让 key 完全对 agent 不可见，从根本上关闭了这个风险面。"

OneCLI 同时做了两件事：静态加密存储 + 运行时不暴露。

---

## 三、架构：Rust 网关 + Next.js 仪表板

```
┌──────────────┐      HTTP (with FAKE_KEY)      ┌───────────────────────────┐
│   AI Agent   │ ──────────────────────────────→ │  Rust Gateway (:10255)    │
└──────────────┘                                  │  · MITM 拦截              │
                                                  │  · host/path 规则匹配     │
                                                  │  · AES-256-GCM 解密       │
                                                  │  · 注入真实凭证           │
                                                  └────────────┬──────────────┘
                                                               │ HTTP (with REAL_KEY)
                                                               ▼
                                                    GitHub / Slack / Any API

┌────────────────────────────────────┐
│  Next.js Dashboard (:10254)        │
│  · 管理 agent + 密钥 + 权限        │
│  · 提供给网关的凭证解析 API        │
│  · Bitwarden 集成（按需注入）       │
└────────────────────────────────────┘
         │
         └── PostgreSQL（持久化）
```

**Rust 网关**是性能敏感路径：每个出站 HTTP 请求都要过一遍规则匹配 + 解密 + 注入，用 Rust 写是合理的工程选择——内存安全，没有 GC 停顿，延迟可预期。

**Next.js 仪表板**做控制平面：你在这里创建 agent、上传密钥、设置哪个 agent 有权访问哪些凭证。网关通过这个 API 查询每次请求应该注入什么凭证。

**Bitwarden 集成**（2026-03-30 集成发布）是一个重要补充：密钥不存在 OneCLI 服务器上，只在请求时从 Bitwarden 按需取来注入。如果你已经有成熟的密码管理体系，这让 OneCLI 变成一个纯路由层而不是另一个密钥存储。

---

## 四、起来只需一行命令

```bash
curl -fsSL https://onecli.sh/install | sh
```

安装完，会自动拉起：
- PostgreSQL 容器
- Rust 网关（`:10255`）
- Next.js 仪表板（`:10254`）

打开 `http://localhost:10254`，创建你的第一个 agent，把 GitHub token 添加进密钥库，然后告诉你的 agent：

```
HTTP 网关地址：http://localhost:10255
Authorization: FAKE_KEY_GITHUB
```

从这一刻起，这个 agent 的 GitHub 请求会自动注入真实 token，但它自己完全不知道真实 token 长什么样。

也可以手动 Docker 起：

```bash
git clone https://github.com/onecli/onecli.git
cd onecli
docker compose -f docker/docker-compose.yml up -d --wait
```

---

## 五、谁在用

**NanoClaw**：自主 agent 框架，2026-03-24 在 HN 发文宣布采用 OneCLI 作为 Agent Vault，112pts。他们的场景是多 agent 系统里每个 agent 需要访问不同服务组合，而不想为每个 agent 维护独立的凭证管理。

**Bitwarden**：主动提供 SDK 与 OneCLI 集成。Bitwarden 做了一个新的"agent access API"，让密码管理器能给 agent 提供按需、权限受限的凭证访问，而不是暴露整个密码库。OneCLI 是第一批集成方之一。

这两个集成说明 OneCLI 不只是个人工具——它在往 agent 基础设施方向走。

---

## 六、技术选型的合理性

**为什么不直接用 HashiCorp Vault？**

Vault 是企业级密钥管理，部署和运维成本很高，而且它解决的是"安全存储和分发密钥"的问题，不是"让 agent 完全看不见密钥"的问题。OneCLI 定位更窄、更垂直：专门针对 AI agent 的 HTTP 请求场景，一行命令本地跑起来，不需要运维背景。

**MCP 支持**：仓库 topics 里有 `mcp`，意味着它在 MCP 协议层也有集成路径，可以和 Claude Code、Cursor 等走 MCP 的 agent 工具链对接。

**多用户模式**：设置 `NEXTAUTH_SECRET` + Google OAuth 可以开启多用户模式，适合团队共享凭证管理。单用户本地模式不需要任何环境变量，开箱即用。

---

## 七、判断

OneCLI 解决的问题是真实的。随着 agent 系统从"偶尔跑一个任务"演变成"长期运行、访问多个系统、可能被注入攻击"，凭证管理的风险面会快速扩大。

三件值得关注的事：

1. **Bitwarden 主动来集成**，不是 OneCLI 去申请。这暗示密码管理器行业正在认真考虑 agent 场景的安全问题，而不只是把现有 API 稍微改改。

2. **两次 HN 上榜间隔了 4 个月**（3 月和 7 月），而且第二次仍然有 102pts，说明不是昙花一现，有持续的社区关注。

3. **Rust 网关是正确的架构选择**。一个 MITM 代理如果延迟高，用户体验会很差。Rust 让这条关键路径可以做到微秒级延迟，不影响 agent 的 API 调用速度。

目前 2746 stars、Apache-2.0，处于早期但认真建设的阶段。如果你有多个 agent 跑在同一台机器或同一个团队里，值得现在就接进去——比等安全问题出现再处理要便宜得多。

---

*数据来源：GitHub onecli/onecli + Hacker News，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: onecli/onecli · TypeScript + Rust · Apache-2.0 · 2,746 stars
> **Homepage**: onecli.sh
> **HN debut**: 2026-03-12 (161pts) · **Latest post**: 2026-07-23 (102pts)
> **Ecosystem**: NanoClaw (112pts) · Bitwarden SDK (63pts)

---

## 1. The Problem: Every Agent Holds Real Keys

Once you start seriously using AI agents for automation — calling the GitHub API, sending Slack messages, operating a Notion database, querying SaaS systems — you run into a security problem that's increasingly hard to ignore:

**Every agent is holding a pile of real API keys.**

These keys typically live as plaintext in `.env` files, system environment variables, or written directly into prompts. The moment an agent's context leaks, gets intercepted, or falls victim to a prompt injection attack, every credential goes with it.

The traditional answer is to store keys in a secret management service (Vault, AWS Secrets Manager) — but that only solves the "at-rest storage" problem. At runtime, the key still has to be retrieved and handed to the agent, which still holds the plaintext key when it calls the API.

OneCLI sidesteps this problem at the architecture level.

---

## 2. The Solution: Don't Hand It Over — Inject It

OneCLI places a gateway between the agent and the target API. The flow looks like this:

```
Agent → [placeholder key] → OneCLI Gateway → [real key injected] → GitHub / Slack / Any API
```

1. You store your real API credentials in OneCLI (AES-256-GCM encrypted, never decrypted at rest)
2. Give the agent a placeholder — literally `FAKE_KEY_GITHUB`
3. The agent makes a normal HTTP request with the fake key
4. The request passes through OneCLI's Rust gateway, which matches host/path rules, replaces the fake key with the real one, decrypts it, and injects it into the outbound request
5. The real request reaches GitHub carrying the real credential
6. The agent never touched the real key at any point

An HN comment captured the key architectural distinction from Vault:

> "Vault protects keys at rest, but the agent still gets them at runtime. The proxy approach keeps the key entirely out of the agent's hands — it closes that attack surface entirely."

OneCLI does both: encrypted at rest, invisible at runtime.

---

## 3. Architecture: Rust Gateway + Next.js Dashboard

```
┌──────────────┐     HTTP (with FAKE_KEY)      ┌───────────────────────────┐
│   AI Agent   │ ─────────────────────────────→ │  Rust Gateway (:10255)    │
└──────────────┘                                 │  · MITM interception      │
                                                 │  · host/path rule match   │
                                                 │  · AES-256-GCM decrypt    │
                                                 │  · inject real credential │
                                                 └────────────┬──────────────┘
                                                              │ HTTP (with REAL_KEY)
                                                              ▼
                                                   GitHub / Slack / Any API

┌────────────────────────────────────┐
│  Next.js Dashboard (:10254)        │
│  · Manage agents + secrets + perms │
│  · Credential resolution API       │
│  · Bitwarden integration (on-demand│
└────────────────────────────────────┘
         │
         └── PostgreSQL (persistence)
```

The **Rust gateway** is the performance-critical path: every outbound HTTP request runs through rule matching, decryption, and injection. Rust is the right engineering choice here — memory safe, no GC pauses, predictable latency.

The **Next.js dashboard** is the control plane: create agents, upload secrets, configure which agent can access which credentials. The gateway queries this API to resolve what to inject for each request.

The **Bitwarden integration** (launched 2026-03-30) is a significant addition: secrets don't live on the OneCLI server at all — they're fetched on demand from Bitwarden at request time. If you already have a mature password management setup, this turns OneCLI into a pure routing layer rather than yet another secret store.

---

## 4. One Command to Run It

```bash
curl -fsSL https://onecli.sh/install | sh
```

The installer brings up:
- PostgreSQL container
- Rust gateway (`:10255`)
- Next.js dashboard (`:10254`)

Open `http://localhost:10254`, create your first agent, add a GitHub token to the secret store, then tell your agent:

```
HTTP gateway: http://localhost:10255
Authorization: FAKE_KEY_GITHUB
```

From that point forward, the agent's GitHub requests automatically carry the real token — but the agent itself has no idea what the real token looks like.

You can also run it manually via Docker:

```bash
git clone https://github.com/onecli/onecli.git
cd onecli
docker compose -f docker/docker-compose.yml up -d --wait
```

---

## 5. Who's Using It

**NanoClaw**: An autonomous agent framework. Published a 112-point HN post on 2026-03-24 announcing they'd adopted OneCLI as their agent vault. Their use case: multi-agent systems where each agent needs access to a different combination of services, without maintaining separate credential management for each.

**Bitwarden**: Came to OneCLI to integrate, not the other way around. Bitwarden built a new "agent access API" so that password managers could provide on-demand, permission-scoped credential access to agents without exposing the full password vault. OneCLI was among the first integration targets.

These two integrations signal that OneCLI is moving in the direction of agent infrastructure — not just a personal utility.

---

## 6. Why the Technical Choices Make Sense

**Why not just use HashiCorp Vault?**

Vault is enterprise-grade secret management with real operational overhead. And critically, it solves "secure storage and distribution of keys" — not "keep keys entirely invisible to agents." OneCLI has a narrower, more vertically targeted position: purpose-built for AI agent HTTP request flows, single-command local setup, no ops background required.

**MCP support**: The `mcp` topic in the GitHub repo indicates integration at the MCP protocol layer, meaning it can connect with Claude Code, Cursor, and other MCP-native agent toolchains.

**Multi-user mode**: Set `NEXTAUTH_SECRET` plus Google OAuth credentials to enable multi-user mode for team credential sharing. Single-user local mode needs no environment variables at all — it just works.

---

## 7. Assessment

The problem OneCLI solves is real. As agent systems evolve from "run an occasional task" to "run continuously, access multiple systems, potentially vulnerable to injection attacks," the credential attack surface grows fast.

Three things worth watching:

1. **Bitwarden came to them**. This suggests the password management industry is seriously thinking about the agent security problem — not just tweaking an existing API.

2. **Two HN front-page appearances, four months apart** (March and July), with the second still pulling 102 points. Not a flash in the pan — there's sustained community interest.

3. **Rust gateway is the right architecture call.** A MITM proxy with high latency would make for a terrible developer experience. Rust makes the critical path fast enough — microsecond-level latency that doesn't meaningfully slow down agent API calls.

Currently at 2,746 stars, Apache-2.0, in early but serious development. If you're running multiple agents on the same machine or in the same team, this is worth integrating now — much cheaper than dealing with a credential leak after the fact.

---

*Data sources: GitHub onecli/onecli + Hacker News, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
