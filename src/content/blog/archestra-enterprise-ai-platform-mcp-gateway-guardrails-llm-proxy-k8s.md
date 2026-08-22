---
title: "Archestra：企业级一体化 AI 平台，MCP 网关 + LLM 代理 + 双 LLM 护栏 + K8s 编排，AGPL 开源"
titleEn: "archestra-enterprise-ai-platform-mcp-gateway-guardrails-llm-proxy-k8s"
description: "archestra-ai/archestra 是一个企业级一体化 AI 平台，4201 stars，TypeScript，AGPL 3.0（30人以下团队免费）。一个 URL、一个 Token，涵盖：LLM 网关（Anthropic/OpenAI/Azure/Bedrock/DeepSeek，带费用限额和虚拟 API Key）、MCP 网关（OAuth + On-Behalf-Of，工具以用户身份运行）、A2A 网关、私有 MCP 注册表、K8s MCP 编排器、Agent 运行时（定时/邮件/Webhook 触发、子 Agent 委托、沙箱代码执行）、RAG 知识库、双 LLM 护栏 + Lethal Trifecta 防护、SSO（OIDC/SAML/Okta/Entra）+RBAC、OpenTelemetry traces + Prometheus metrics。已融资 $13.5M，三个 Fortune-50 部署，p95 延迟 31ms，已加入 Linux Foundation / CNCF。"
descriptionEn: "archestra-ai/archestra is an all-in-one enterprise AI platform — 4,201 stars, TypeScript, AGPL 3.0 (free for teams under 30). One URL, one token: LLM gateway (Anthropic/OpenAI/Azure/Bedrock/DeepSeek, with cost limits and virtual API keys), MCP gateway (OAuth + On-Behalf-Of, tools run as the user), A2A gateway, private MCP registry, Kubernetes MCP orchestrator, agent runtime (scheduled/email/webhook triggers, sub-agent delegation, sandboxed code execution), RAG knowledge base, Dual-LLM guardrails + Lethal Trifecta protections, SSO (OIDC/SAML/Okta/Entra) + RBAC, OpenTelemetry traces + Prometheus metrics. $13.5M funding, three Fortune-50 deployments, 31ms p95 latency, joined Linux Foundation / CNCF."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["企业AI", "MCP网关", "LLM代理", "护栏", "K8s", "开源", "企业安全", "Agent平台"]
heroImage: "../../assets/images/archestra-enterprise-ai-platform-mcp-gateway-guardrails-llm-proxy-k8s-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：archestra-ai/archestra  
网站：archestra.ai  
许可证：AGPL 3.0 / Enterprise（30 人以下团队免费）  
语言：TypeScript  
Stars：4,201 · Forks：1,176  
融资：$13.5M  
创建：2025-07-15 | 最近更新：2026-08-22

---

## 一、一个 URL 解决企业 AI 接入的所有混乱

企业部署 AI 工具通常的状态：每个团队用不同的 LLM Provider、不同的 API Key、没有费用控制、没有权限管理、没有审计日志，Claude Code 和 Codex 各自连各自的端点，MCP 工具用共享服务账号而不是用户身份运行。

Archestra 的方案是：**一个 URL、一个 Token，接管所有这些事情**。

> 已经在企业里跑 Claude Cowork、OpenClaw 或 Hermes 这类单租户 Agent 了？官方提供了 Migration Kit。

---

## 二、功能全景

### LLM 网关

统一接入 Anthropic、OpenAI、Azure、Bedrock、DeepSeek 及其他任意 Provider：
- **虚拟 API Key**：给 Claude Code / Codex / Cursor 各自发一个 Token，按团队/用户追踪费用
- **费用限额**：按团队、按环境、按 Provider 设硬上限
- **动态模型路由**：按规则自动切换 Provider 和模型

### MCP 网关

- **OAuth + On-Behalf-Of**：MCP 工具以**当前用户身份**运行，而不是共享的服务账号。这是企业审计合规的关键——工具调用记录可以精确追踪到发起者
- **私有 MCP 注册表**：团队自行发布内部工具，自助推广到不同环境
- **MCP 编排器**：Kubernetes Operator，管理 MCP 工具的生命周期

### A2A 网关

Agent-to-Agent 触发——一个 Agent 可以调用另一个 Agent，支持 Webhook 和定时触发。

### Agent 运行时

- 触发方式：定时、邮件、Webhook、A2A
- 子 Agent 委托
- 沙箱代码执行（K8s 原生文件系统）
- 可复用 Skills

### 护栏系统

Archestra 的护栏有两层，都是确定性的（不依赖另一个 LLM 的判断）：

**Dual-LLM 验证**：一个 LLM 生成，另一个 LLM 独立验证。在关键工具调用上加一层验证屏障。

**Lethal Trifecta 防护**：专门防止「对高权限目标的不可逆操作」——例如 Agent 要删除生产数据库、发送外部邮件、修改 IAM 策略这类组合。Trifecta 是三个维度同时触发时的高风险标志，Archestra 会拦截并要求人工确认。

### 安全和可观测性

- **SSO**：OIDC、SAML、Okta、Entra，带角色映射和团队同步的 RBAC
- **Secrets 管理**：内置，不需要外挂
- **OpenTelemetry traces + Prometheus metrics**：开箱即用，不是事后打补丁
- **每团队费用追踪**：按团队、按环境拆分账单

---

## 三、部署

**最快：Docker 一行**

```bash
docker pull archestra/platform:latest

docker run \
  -p 127.0.0.1:9000:9000 -p 127.0.0.1:3000:3000 \
  -e ARCHESTRA_QUICKSTART=true \
  -e ARCHESTRA_BETA=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v archestra-postgres-data:/var/lib/postgresql/data \
  -v archestra-app-data:/app/data \
  archestra/platform
```

打开 `http://localhost:3000` 即可。

**生产推荐：Helm / Kubernetes**

有官方 Terraform Provider，也有 Helm Chart，完整 K8s 部署文档已提供。

---

## 四、生产就绪情况

| 指标 | 值 |
|------|---|
| 总融资 | $13.5M |
| Fortune-50 部署 | 3 个 |
| p95 延迟 | 31ms |
| 30 人以下团队 | 免费（AGPL） |
| 基金会 | Linux Foundation / CNCF |

已加入 CNCF，意味着长期中立性和开放治理——这对企业采购决策是一个重要信号。

---

## 五、定位

对于企业 AI 采购，Archestra 填的是一个在之前很难回答的问题：

**「我们买了好几个 LLM 订阅，员工用各种 AI 工具，怎么统一管起来？」**

它不是又一个 AI 聊天工具，也不是单个 Agent 框架——它是企业 AI 基础设施层：统一接入、统一鉴权、统一计费、统一护栏、统一可观测性。

RAG、Agent、MCP 工具、LLM 网关，这四件事通常需要四个不同的产品或自建系统，Archestra 把它们放在一个平台里，并在上面加了企业级的安全和合规层。

4201 stars，1 年多历史，真实 Fortune-50 案例，CNCF 成员。对于有企业 AI 治理需求的团队，是目前开源方案里最完整的选项之一。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Archestra: All-in-One Enterprise AI Platform — MCP Gateway, Dual-LLM Guardrails, LLM Proxy, Kubernetes Orchestration

*by Mycelium Protocol*

---

GitHub: archestra-ai/archestra  
Site: archestra.ai  
License: AGPL 3.0 / Enterprise (free for teams under 30)  
Language: TypeScript  
Stars: 4,201 · Forks: 1,176  
Funding: $13.5M  
Created: 2025-07-15 | Updated: 2026-08-22

---

### One URL to Fix the Enterprise AI Mess

Enterprise AI deployments typically look like this: every team uses a different LLM provider, different API keys, no cost controls, no permission management, no audit logs. Claude Code and Codex each connect to their own endpoints. MCP tools run under a shared service account rather than the actual user's identity.

Archestra's answer: **one URL, one token, handling all of this.**

> Already running single-tenant agents like Claude Cowork, OpenClaw, or Hermes in your enterprise? There's an official Migration Kit.

---

### Feature Landscape

**LLM Gateway.** Unified access to Anthropic, OpenAI, Azure, Bedrock, DeepSeek, and any other provider:
- **Virtual API keys**: issue separate tokens for Claude Code / Codex / Cursor; track costs per team or user
- **Cost limits**: hard caps per team, per environment, per provider
- **Dynamic model routing**: auto-switch providers and models by rules

**MCP Gateway.** OAuth + On-Behalf-Of: MCP tools run **as the authenticated user**, not a shared service account. This is the enterprise audit requirement — tool call records are attributed to the individual who triggered them. Plus: private MCP registry (teams publish internal tools with self-serve promotion) and a Kubernetes Operator for MCP lifecycle management.

**A2A Gateway.** Agent-to-agent triggers via webhook or schedule.

**Agent Runtime.** Scheduled / email / webhook / A2A triggers. Sub-agent delegation. Sandboxed code execution (Kubernetes-native filesystem). Reusable skills.

**Guardrails — two layers, both deterministic:**

*Dual-LLM verification*: one LLM generates, an independent LLM verifies. Adds a verification barrier on high-stakes tool calls.

*Lethal Trifecta protection*: specifically blocks "irreversible operations on high-privilege targets" — e.g. an agent about to delete a production database, send external email, and modify IAM policy in combination. Lethal Trifecta flags when three risk dimensions trigger simultaneously and requires human confirmation.

**Security and observability:**
- SSO: OIDC, SAML, Okta, Entra — with role mapping and team sync RBAC
- Secrets management built in
- OpenTelemetry traces + Prometheus metrics out of the box
- Per-team cost tracking split by team and environment

---

### Deployment

**Fastest: single Docker command**

```bash
docker pull archestra/platform:latest

docker run \
  -p 127.0.0.1:9000:9000 -p 127.0.0.1:3000:3000 \
  -e ARCHESTRA_QUICKSTART=true \
  -e ARCHESTRA_BETA=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v archestra-postgres-data:/var/lib/postgresql/data \
  -v archestra-app-data:/app/data \
  archestra/platform
```

Open `http://localhost:3000`. Production: Helm chart or Kubernetes with full docs; official Terraform provider available.

---

### Production Readiness

| Metric | Value |
|--------|-------|
| Total funding | $13.5M |
| Fortune-50 deployments | 3 |
| p95 latency | 31ms |
| Teams under 30 | Free (AGPL) |
| Foundation membership | Linux Foundation / CNCF |

CNCF membership signals long-term neutrality and open governance — meaningful for enterprise procurement decisions.

---

### Positioning

Archestra fills a gap that enterprise AI buyers have struggled with:

**"We have several LLM subscriptions and staff using various AI tools. How do we manage this centrally?"**

It's not another AI chat interface and it's not a single agent framework — it's the **enterprise AI infrastructure layer**: unified access, unified auth, unified billing, unified guardrails, unified observability.

RAG, agents, MCP tools, and an LLM gateway typically require four separate products or custom builds. Archestra puts all four in one platform with an enterprise security and compliance layer on top.

4,201 stars, 13 months old, real Fortune-50 deployments, CNCF member. Among open-source options for teams with enterprise AI governance needs, it's one of the most complete choices available.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
