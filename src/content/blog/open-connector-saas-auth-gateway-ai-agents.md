---
title: "OpenConnector：让AI Agent一次接入1000+个SaaS，不再操心OAuth"
titleEn: "open-connector-saas-auth-gateway-ai-agents"
description: "oomol-lab 开源了 OpenConnector，一个 AI Agent 专用的认证网关，Composio 的开源替代。接 1000+ SaaS 提供者、10000+ 预制 Action，凭据永远留在网关边界内，Agent 只能拿到执行结果。支持 SDK/CLI/MCP/HTTP 多接入方式，可部署到 Docker、Cloudflare Workers 或 Fly.io。"
descriptionEn: "oomol-lab open-sources OpenConnector, an auth gateway for AI agents — an open-source alternative to Composio. 1000+ providers, 10000+ prebuilt Actions, credentials stay behind the gateway boundary. SDK, CLI, MCP, and HTTP access modes. Deploy on Docker, Cloudflare Workers, or Fly.io."
pubDate: "2026-07-31"
updatedDate: "2026-07-31"
category: "Tech-News"
tags: ["AI Agent", "OAuth", "SaaS集成", "MCP", "Cloudflare", "开源工具", "auth-gateway", "Mycelium"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

*by Mycelium Protocol*

---

每个做 AI Agent 产品的团队，迟早都会撞上同一堵墙：

你的 Agent 需要访问用户的 Gmail、Notion、Slack、GitHub……每一个都有自己的 OAuth 流程、token 刷新逻辑、scope 管理、凭据存储。而且每个产品都得从头实现一遍。

**[OpenConnector](https://github.com/oomol-lab/open-connector)**（oomol-lab）把这堵墙变成一个网关：连一次，用到处。3681 星，Apache 2.0，Composio 的开源替代。

---

## 核心问题：认证不应该是 Agent 的工作

现在主流的做法是让 Agent 直接持有用户的 API key 或 OAuth token，执行 SaaS 操作。问题很明显：

- 凭据暴露在 Agent 进程里，审计困难
- 每个 provider 的 OAuth 流程都得自己实现
- token 过期、刷新、revoke——全是重复工作
- 更换 provider、迁移部署——接口全都不一样

OpenConnector 的思路是把认证单独提出来：

```
AI Agent / App
  ↓ SDK / CLI / MCP / HTTP
OpenConnector 网关
  ↓ 凭据 & OAuth 边界（Agent 到不了这里）
1000+ Providers（Gmail, GitHub, Notion, Slack...）
```

Agent 只能看到"我有没有权限执行这个 Action"和执行结果，永远拿不到原始凭据。

---

## 什么是 Action

OpenConnector 的核心单元是 **Action**：一个有明确输入输出 schema、所需 scope、执行器源码的可调用操作。

```bash
# 不需要任何凭据的 Action，验证运行时是否正常
curl -s -X POST http://localhost:3000/v1/actions/hackernews.get_top_stories \
  -H 'content-type: application/json' \
  -d '{"input":{}}'

# 需要 GitHub token 的 Action
curl -s -X POST http://localhost:3000/v1/actions/github.get_current_user \
  -H 'content-type: application/json' \
  -d '{"input":{}}'
```

10000+ 个预制 Action，覆盖 GitHub、Gmail、Notion、BigQuery、Google Analytics、Supabase、Airtable、Slack 等 1000+ 个 provider。

---

## 四种接入方式，Agent 框架无关

| 接入方式 | 适合场景 |
|---------|---------|
| **Connector SDK**（TypeScript） | 在 App 代码里直接调用 Action |
| **oo CLI** | 本地 Agent relay，命令行搜索/检查/执行 Action |
| **MCP** | 任何支持 MCP 的 Agent 宿主，`http://localhost:3000/mcp` |
| **HTTP / OpenAPI** | 自定义客户端，也可以直接看 `/openapi.json` |

这意味着 OpenConnector 不依赖特定 Agent 框架——无论你用 LangChain、Claude Code、自己的 Agent 还是任何 OpenAI-compatible 系统，都能接入。

---

## 凭据安全边界

OpenConnector 的设计原则是：**凭据永远不出网关**。

具体机制：
- 支持 API key、OAuth2、自定义凭据、免认证多种类型
- 运行时 token（不是原始凭据）给 Agent
- Action 的 allow/block policy 控制 Agent 能调什么
- 完整 run log（支持 redaction）
- 每个连接有独立的 scope 和 identity

这对需要做合规审计的产品尤其重要——你能说清楚"哪个 Agent 在什么时候对哪个 provider 调了什么"。

---

## 部署选项

| 部署方式 | 存储 | 特点 |
|---------|------|------|
| 本地 Docker / Node | SQLite | 开发调试，一行启动 |
| Fly.io | SQLite（Fly volume） | 托管 Docker，自带 TLS |
| Cloudflare Workers | D1 + R2 | 轻量，全球边缘节点 |
| [OOMOL 托管](https://oomol.com/apps) | 云端 | 托管 OAuth apps，每月约 15000-20000 次调用额度 |

**Docker 一行启动：**

```bash
docker compose up
# 控制台：http://localhost:3000
# API 文档：http://localhost:3000/docs
```

**Cloudflare 部署：** Workers + D1（状态）+ R2（临时文件）+ Static Assets（控制台），项目附带视频教程。

---

## 与 Composio 的区别

OpenConnector 在 README 里直接写明是 Composio 的开源替代。区别：

- **Composio**：托管服务，开箱即用，但凭据在第三方
- **OpenConnector**：开源可自托管，凭据完全在自己控制下；想用托管就用 OOMOL 的服务，随时能迁回自托管

对需要私有部署或数据合规的团队，这个区别是本质性的。

---

## 配套：Wanta 桌面 Agent

oomol-lab 同时开源了 **[Wanta](https://github.com/oomol-lab/wanta)**，一个基于 OpenCode + OpenConnector 构建的桌面 AI Agent：

- 本地运行，用自己的 OpenAI-compatible 模型，不需要创建账号
- 通过 OpenConnector 访问已连接的 SaaS 服务
- 可以 Fork，自定义 prompt、工具、界面和模型
- 可选 [hosted experience](https://wanta.ai/)（托管模型 + OAuth 连接 + 团队工作区）

两个项目组合起来，等于一套完整的"带 SaaS 集成能力的本地 Agent 基础设施"。

---

## 快速验证

```bash
# 1. 启动
docker compose up

# 2. 跑一个免认证 Action，验证运行时
curl -s -X POST http://localhost:3000/v1/actions/hackernews.get_top_stories \
  -H 'content-type: application/json' \
  -d '{"input":{}}'

# 3. 连接 GitHub（用 Personal Access Token）
curl -s -X PUT http://localhost:3000/api/connections/github \
  -H 'content-type: application/json' \
  -d '{"authType":"api_key","values":{"apiKey":"github_pat_..."}}'

# 4. 调用 GitHub Action
curl -s -X POST http://localhost:3000/v1/actions/github.get_current_user \
  -H 'content-type: application/json' \
  -d '{"input":{}}'
```

从启动到第一个 GitHub API 调用，整个流程 5 分钟以内。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenConnector: One Auth Gateway for 1000+ SaaS Providers, Built for AI Agents

*by Mycelium Protocol*

Every team building an AI agent product eventually hits the same wall: your agent needs access to the user's Gmail, Notion, Slack, GitHub — each with its own OAuth flow, token refresh logic, scope management, and credential storage. And every product has to implement all of it from scratch.

**[OpenConnector](https://github.com/oomol-lab/open-connector)** (oomol-lab) turns that wall into a gateway: connect once, use everywhere. 3,681 stars, Apache 2.0, an open-source alternative to Composio.

### The Core Problem: Auth Shouldn't Be the Agent's Job

The standard approach today is having the agent process hold user API keys or OAuth tokens and execute SaaS operations directly. The problems are clear: credentials exposed in the agent process are hard to audit, every provider's OAuth flow needs custom implementation, and token refresh and revocation become repetitive work.

OpenConnector separates auth into its own boundary:

```
AI Agent / App
  ↓ SDK / CLI / MCP / HTTP
OpenConnector Gateway
  ↓ Credential & OAuth Boundary (the agent can't reach this)
1000+ Providers (Gmail, GitHub, Notion, Slack...)
```

Agents see whether they have permission to execute an Action and get the execution result. They never see raw credentials.

### What an Action Is

The core unit is an **Action**: a callable operation with declared input/output schemas, required scopes, and inspectable executor source. 10,000+ prebuilt Actions cover 1,000+ providers including GitHub, Gmail, Notion, BigQuery, Google Analytics, Supabase, Airtable, and Slack.

### Four Access Modes, Framework-Agnostic

| Mode | Use case |
|------|----------|
| **Connector SDK** (TypeScript) | Call Actions directly from app code |
| **oo CLI** | Local agent relay — search, inspect, and run Actions |
| **MCP** | Any MCP-capable agent host at `http://localhost:3000/mcp` |
| **HTTP / OpenAPI** | Custom clients; inspect `/openapi.json` |

OpenConnector doesn't depend on any specific agent framework — LangChain, Claude Code, your own agent, or any OpenAI-compatible system all work.

### Credential Safety

Credentials never leave the gateway boundary. Agents get runtime tokens (not raw credentials). Action allow/block policies control what each agent can call. Full run logs with redaction support enable audit trails: which agent called what, on which provider, at what time.

### Deployment

One-line local start: `docker compose up`. Also deploys on Fly.io (Docker + persistent SQLite) or Cloudflare Workers (Workers + D1 + R2 + Static Assets). OOMOL's hosted runtime provides managed OAuth apps and ~15,000–20,000 monthly Action calls.

### vs. Composio

OpenConnector is explicitly positioned as an open-source Composio alternative. The key difference: credentials in a self-hosted OpenConnector stay under your control. For teams with private deployment requirements or data compliance constraints, that's a fundamental distinction. Start with OOMOL's hosted runtime for speed; migrate to self-hosted when you need it — provider IDs, Action IDs, and schemas stay identical across both.

### Wanta: Companion Desktop Agent

[Wanta](https://github.com/oomol-lab/wanta) is an OpenCode-powered desktop agent that uses OpenConnector for SaaS access. Run it locally with any OpenAI-compatible model, fork it to customize prompts and interface, or use the hosted experience for managed models and OAuth connections. Together, OpenConnector + Wanta form a complete local agent infrastructure with built-in SaaS integration.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
