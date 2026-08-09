---
title: "authentik 2026.8：OpenID 官方认证、Rust 重写、PAM，自托管 IdP 的新里程碑"
titleEn: "authentik-2026-8-oidc-certified-rust-rewrite-pam"
description: "goauthentik/authentik 开源 Identity Provider，24k stars，Python，自托管替代 Okta/Auth0/Entra ID。v2026.8 三大亮点：通过 OpenID Foundation 官方认证（8个profile）、服务器与 Proxy Outpost 完成 Rust 重写、企业版新增特权访问管理（PAM）。另有用户多账号切换、自定义字段、LDAP 嵌套组同步、策略绑定到期、PostgreSQL 连接池支持。"
descriptionEn: "goauthentik/authentik — open-source Identity Provider, 24k stars, Python, self-hosted alternative to Okta/Auth0/Entra ID. v2026.8 highlights: OpenID Foundation official certification (8 profiles), server and Proxy Outpost rewritten in Rust, enterprise Privileged Access Management (PAM). Also: multi-account user switching, object attributes, nested LDAP group sync, expiring policy bindings, PostgreSQL connection pooler support."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["身份认证", "IdP", "SSO", "OpenID", "自托管", "Rust重写", "安全", "Mycelium"]
heroImage: "../../assets/images/authentik-2026-8-oidc-certified-rust-rewrite-pam-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Okta 一年几千美元，Auth0 按月付费，Entra ID 与微软全家桶深度绑定。对于需要完全控制身份基础设施的团队，这些都不是最优解。

authentik 是目前最活跃的开源自托管 Identity Provider，支持 SAML、OAuth2/OIDC、LDAP、RADIUS，覆盖从小型家庭实验室到生产集群的全部场景。v2026.8 是一个密度很高的版本——OpenID 官方认证、Rust 重写，以及一批实质性的新功能。

GitHub: https://github.com/goauthentik/authentik | ⭐ 24,003 | Python

---

## v2026.8 三大里程碑

### 1. OpenID Foundation 官方认证

authentik 2026.8 通过了 OpenID Foundation 的官方认证，成为 **OpenID Certified™** Provider。认证覆盖 8 个 profile：

**OpenID Provider profiles**：Basic、Implicit、Hybrid、Config、Form Post OP

**Logout profiles**：RP-Initiated、Front-Channel、Back-Channel

对于需要与外部合规审计对接的企业用户，这是一个明确的信任锚——不再依赖自我声明。

---

### 2. 服务器与 Proxy Outpost 完成 Rust 重写

原来用 Go 实现的 authentik server（请求入口层）和 Proxy Outpost 已完整重写为 Rust。这是 1-to-1 替换，功能行为保持不变。

现阶段不带来直接性能提升，但为后续将 Django 核心与 Rust 代理层更紧密耦合（共享资源，避免重复开销）打下基础。后续版本会利用这个基础做更深的优化。

---

### 3. 特权访问管理（PAM）— 企业版

用户可以从界面请求访问特定应用或应用权限，指定审批人审批或拒绝，并设置访问到期时间。

管理员定义请求规则：
- 支持个人/群组/策略审批人
- 最小审批人数量
- 请求和授权到期限制
- 审批人通知
- 自定义流程（收集请求详情）
- 每个操作记入事件日志

---

## 其他新功能

### 用户多账号切换

用户可以在同一浏览器保持多个 authentik 账号登录，从账户菜单随时切换，也可以直接添加新账号而无需退出。

切换流程是标准 authentik flow，管理员可以通过策略控制是否要求密码、MFA 或更简短的验证。切换记录在事件日志中。

配置方式：在品牌设置中选择 **User switch flow**。

---

### 自定义字段（Object Attributes）

管理员可以为用户、群组、应用权限和设备访问组定义自定义文本、数字和布尔字段，支持正则验证和必填/唯一约束。

authentik 内置了常见身份、联系方式、地址、Unix 和员工属性的定义（默认禁用，按需启用）。字段在管理界面编辑对象时显示，API 管理也使用相同验证规则。

---

### LDAP 嵌套组同步

LDAP 源现在可以保留源目录的嵌套群组层级。启用 **Sync Group Parents** 后，同步的群组会在 authentik 中创建父子关系，而不是全部打平。

---

### 策略绑定到期

策略、群组和用户绑定现在支持设置到期时间。到期后，绑定不再授予访问或贡献成功的策略结果——无需管理员手动删除临时权限。

---

### Token Exchange（OAuth 2.0）

OAuth 2.0 Token Exchange 允许应用把来自受信任 Provider 或来源的 token 换取 authentik 访问令牌，在关联服务之间以用户身份行动，而不必在服务之间传递原始 token。

---

### OpenID Connect Key Binding

OIDC Provider 现在可以签发 key-bound ID token，客户端必须证明持有关联密钥，在 token 被窃取时提供更强的保护。

---

### PostgreSQL 连接池支持

现在支持在 transaction-mode 连接池旁边配置独立的直连数据库，用于需要稳定会话的操作。现有 PostgreSQL 配置继续处理常规流量，新的直连配置可以指向直连或 session-mode 端点。

---

### Base URL 系统设置

新增 **Base URL** 系统设置，记录实例的外部访问 URL。可在管理界面 **System > Settings** 配置，或通过 `AUTHENTIK_WEB__BASE_URL` 环境变量设置。

**注意**：从 authentik 2026.11 开始此设置将变为必填项，建议现在就配置好。

---

## 安装

```bash
# Docker Compose（推荐用于小型/测试部署）
wget -O docker-compose.yml https://goauthentik.io/version/2026.8/lifecycle/container/compose.yml
docker compose up -d
```

Kubernetes：使用官方 Helm Chart。AWS：官方 CloudFormation 模板。DigitalOcean：Marketplace 一键部署。

---

## 本版本新增的 30+ 集成指南

一个版本新增 30+ 第三方集成指南（含 n8n、Notion、Cursor、NocoDB、Coolify、GitLab、Microsoft 365 via WS-Federation 等），大量来自社区贡献。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## authentik 2026.8: OpenID Certified, Rust Rewrite, and PAM

*by Mycelium Protocol*

---

Okta charges thousands per year. Auth0 meters by monthly active users. Entra ID is tightly bound to the Microsoft ecosystem. For teams that need full control of their identity infrastructure, none of those are optimal.

authentik is the most actively developed open-source self-hosted Identity Provider. It supports SAML, OAuth2/OIDC, LDAP, and RADIUS — from home labs to production Kubernetes clusters. v2026.8 is a dense release: OpenID certification, a Rust rewrite, and a substantial batch of new capabilities.

GitHub: https://github.com/goauthentik/authentik | ⭐ 24,003 | Python

---

### Three Milestones in v2026.8

#### 1. OpenID Foundation Certification

authentik 2026.8 is officially **OpenID Certified™** by the OpenID Foundation, covering 8 profiles:

**OpenID Provider profiles**: Basic, Implicit, Hybrid, Config, Form Post OP

**Logout profiles**: RP-Initiated, Front-Channel, Back-Channel

For teams that need to satisfy external compliance audits, this is a concrete trust anchor — not a self-declaration.

---

#### 2. Server and Proxy Outpost Rewritten in Rust

The authentik server (the request entrypoint layer) and Proxy Outpost, previously written in Go, have been fully rewritten in Rust. This is a 1-to-1 replacement — behavior is unchanged.

No direct performance improvement yet, but this lays the foundation for tighter coupling between the Django core and the Rust proxy layer (shared resources, eliminated duplication). Future releases will build on this.

---

#### 3. Privileged Access Management (PAM) — Enterprise

Users can now request access to applications or specific application entitlements from the User interface, with designated approvers approving or denying requests and setting expiration.

Admin-configured request rules support: individual/group/policy approvers, minimum reviewer counts, request and grant expiration, reviewer notifications, custom flows for collecting request details. Every action is logged.

---

### Other New Features

**Multi-account user switching** — Keep multiple authentik accounts signed in within the same browser; switch from the account menu or add another account without signing out. The switch flow is a standard authentik flow, so policies can require MFA or a lighter verification step. Enable by selecting a **User switch flow** in brand settings.

**Object attributes** — Define custom text, number, and Boolean fields for users, groups, application entitlements, and device access groups, with regex validation and required/unique constraints. authentik ships built-in definitions for common identity, contact, Unix, and employee attributes (disabled by default).

**Nested LDAP group sync** — Enable **Sync Group Parents** to preserve the source directory's group hierarchy in authentik, rather than flattening all groups.

**Expiring policy bindings** — Policy, group, and user bindings can now have an expiration date. Expired bindings no longer grant access — no manual removal needed for temporary permissions.

**OAuth 2.0 token exchange** — Exchange a token from a trusted provider for an authentik access token representing the same user, so connected services can act on a user's behalf without passing the original token around.

**OpenID Connect key binding** — OIDC providers can issue key-bound ID tokens that require the client to prove possession of the associated key — stronger protection if a token is stolen.

**PostgreSQL connection pooler** — Support for transaction-mode poolers alongside a direct connection for session-scoped operations.

**Base URL system setting** — New required setting (from 2026.11 onward): set `AUTHENTIK_WEB__BASE_URL` or configure via **System > Settings** now to avoid a required upgrade step later.

---

### 30+ New Integration Guides

One release, 30+ new third-party integration guides — n8n, Notion, Cursor, NocoDB, Coolify, Microsoft 365 via WS-Federation, and more — the majority contributed by the community.

---

### Install

```bash
# Docker Compose (recommended for small/test setups)
wget -O docker-compose.yml https://goauthentik.io/version/2026.8/lifecycle/container/compose.yml
docker compose up -d
```

Kubernetes (Helm Chart), AWS (CloudFormation), and DigitalOcean (Marketplace) are also supported.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
