---
title: "8K星 · 最小的 OpenID Certified™ 认证服务器：Tinyauth 全解析"
titleEn: "tinyauth-smallest-openid-certified-auth-server-self-hosted"
description: "tinyauthapp/tinyauth 是目前最小的 OpenID Certified™ 认证与授权服务器，Go 编写，AGPL-3.0。支持 OAuth/LDAP/访问控制，与 Traefik、Nginx、Caddy 无缝集成，Docker 一行启动。v5.1.0 于 2026 年 6 月通过 OpenID Basic OP 官方认证，8000+ GitHub stars。"
descriptionEn: "tinyauthapp/tinyauth is the smallest OpenID Certified™ authentication and authorization server available, written in Go under AGPL-3.0. Supports OAuth, LDAP, and access controls; integrates seamlessly with Traefik, Nginx, and Caddy; single Docker container to start. v5.1.0 achieved official OpenID Basic OP certification in June 2026, 8,000+ GitHub stars."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-News"
tags: ["认证", "OpenID", "自托管", "Traefik", "OAuth", "Go", "homelab", "Mycelium"]
heroImage: "../../assets/images/tinyauth-smallest-openid-certified-auth-server-self-hosted-banner.jpg"
---

*by Mycelium Protocol*

---

自托管认证一直是 homelab 最痛苦的环节——Keycloak 太重，Authentik 配置复杂，Authelia 文档学习曲线陡。

**[Tinyauth](https://github.com/tinyauthapp/tinyauth)**（tinyauthapp）从另一个方向切入：把认证服务做到最小，一个 Docker 容器、一个配置文件，5 分钟跑起来。

2026 年 6 月，v5.1.0 通过 OpenID Foundation 官方 **Basic OP 认证**，成为目前最小的 OpenID Certified™ 认证服务器。截至 2026 年 8 月，GitHub 已有 **8,046 stars**，259 forks。

---

## 它解决什么问题

你用 Traefik 或 Nginx 反代了一堆服务（Grafana、Jellyfin、Home Assistant……），但这些服务要么没有登录页，要么密码直接写在 URL 里。你需要一个统一的认证层，在请求到达服务之前就先验证身份。

Tinyauth 就是这个认证层：

- **认证中间件**：拦截请求，验证身份，通过后放行到上游服务
- **独立认证服务**：OAuth / LDAP 后端，其他应用接入
- **访问控制**：细粒度权限，哪个用户能访问哪个服务

支持的反代：Traefik、Nginx、Caddy（三大主流全覆盖）。

---

## 核心功能

**认证方式**

| 方式 | 说明 |
|------|------|
| 用户名 + 密码 | 本地账户，bcrypt 哈希存储 |
| OAuth / OIDC | 接入 Google、GitHub、Authentik 等 |
| LDAP | 企业目录服务集成 |
| TOTP 两步验证 | 可选，标准 authenticator app |

**OpenID Certified™ Basic OP**

v5.1.0 通过 [OpenID Foundation 官方认证](https://openid.net/certification-old/certified-openid-providers-profiles/)，可作为 OIDC Provider 供其他应用接入，不只是"能用"，而是"规范合规"。

**代理集成**

```yaml
# Traefik 示例 — 为任意服务加认证
labels:
  - "traefik.http.middlewares.tinyauth.forwardauth.address=http://tinyauth:3000/api/auth/traefik"
  - "traefik.http.routers.myapp.middlewares=tinyauth"
```

Nginx 和 Caddy 同样有官方文档示例，配置三行内搞定。

---

## 部署：一个 Docker 容器

```yaml
# docker-compose.yml
services:
  tinyauth:
    image: ghcr.io/tinyauthapp/tinyauth:latest
    container_name: tinyauth
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - SECRET=your-super-secret-key-here
      - APP_URL=https://auth.yourdomain.com
      - USERS=user:$$2y$$10$$hashed_password_here  # bcrypt
```

生产环境配置：[文档](https://tinyauth.app/docs/getting-started)已提供完整 Traefik + Tinyauth 的 docker-compose 示例，把 `APP_URL`、`SECRET` 和用户配好就能跑。

**演示环境**：[demo.tinyauth.app](https://demo.tinyauth.app/)，用户名 `user`，密码 `password`，可以直接体验登录流程。

---

## 与同类项目对比

| 项目 | 语言 | OpenID Certified | 资源占用 | 学习曲线 |
|------|------|-----------------|---------|---------|
| **Tinyauth** | Go | ✅ Basic OP | 极低 | 低 |
| Authentik | Python | ✅ | 高 | 高 |
| Authelia | Go | ❌ | 中 | 中 |
| Keycloak | Java | ✅ | 极高 | 极高 |

Tinyauth 定位非常清晰：适合个人 homelab 和小团队自托管，不适合需要复杂企业 SSO 流程的场景。

---

## 许可证说明

Tinyauth 使用 **AGPL-3.0**。核心条款：修改后的版本如果通过网络提供服务，必须开放源码。对个人使用和内部自托管没有限制，但如果打算把 Tinyauth 封装为商业 SaaS，需要注意合规。

---

## 为什么值得关注

**"最小"不只是营销词**。Go 单二进制 + 极低内存，跑在树莓派上不是问题。

**OpenID Certified™ 意味着可以信任它的 OIDC 实现**。不是自己拼凑的 OAuth 流程，是经过 OpenID Foundation 测试套件验证的规范实现。

**社区活跃**。8K+ stars、259 forks，有 Discord，有 Crowdin 多语言翻译，JetBrains、CodeRabbit 都是赞助商，不是个人玩具项目。

**对于用 Traefik 反代的自托管用户**，Tinyauth 是目前配置成本最低的统一认证方案之一。

仓库：[github.com/tinyauthapp/tinyauth](https://github.com/tinyauthapp/tinyauth) · 文档：[tinyauth.app](https://tinyauth.app/) · 演示：[demo.tinyauth.app](https://demo.tinyauth.app/)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Tinyauth: The Smallest OpenID Certified™ Auth Server for Self-Hosters

*by Mycelium Protocol*

Self-hosted authentication has always been the painful part of running a homelab. Keycloak is too heavy. Authentik has a complex setup. Authelia has a steep documentation curve.

**[Tinyauth](https://github.com/tinyauthapp/tinyauth)** (tinyauthapp) takes the opposite approach: make the auth server as small as possible — one Docker container, one config file, running in 5 minutes.

In June 2026, v5.1.0 passed the OpenID Foundation's official **Basic OP certification**, making Tinyauth the smallest OpenID Certified™ auth server available. As of August 2026: **8,046 GitHub stars**, 259 forks, written in Go, AGPL-3.0.

### What Problem It Solves

You're running Traefik or Nginx as a reverse proxy for a stack of services — Grafana, Jellyfin, Home Assistant. These services either have no login page or use credentials embedded in the URL. You need a unified auth layer that validates identity *before* requests reach the upstream service.

Tinyauth is that layer:

- **Auth middleware**: intercepts requests, verifies identity, proxies through on success
- **Standalone auth server**: OAuth/LDAP backend for other applications to integrate
- **Access controls**: fine-grained permissions — which user can reach which service

Supported proxies: Traefik, Nginx, Caddy.

### Authentication Methods

| Method | Details |
|--------|---------|
| Username + password | Local accounts, bcrypt-hashed |
| OAuth / OIDC | Google, GitHub, Authentik, any compliant provider |
| LDAP | Enterprise directory integration |
| TOTP 2FA | Optional, standard authenticator apps |

### OpenID Certified™ Basic OP

v5.1.0 passed the [OpenID Foundation's official test suite](https://openid.net/certification-old/certified-openid-providers-profiles/). This means Tinyauth can serve as a proper OIDC Provider — not just "it works with OAuth" but "it passes the spec compliance tests."

### Deploy in One Container

```yaml
services:
  tinyauth:
    image: ghcr.io/tinyauthapp/tinyauth:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - SECRET=your-super-secret-key-here
      - APP_URL=https://auth.yourdomain.com
      - USERS=user:$$2y$$10$$hashed_password_here
```

Traefik integration: three labels and a middleware reference. Full docker-compose examples with Traefik and Tinyauth are in the [documentation](https://tinyauth.app/docs/getting-started).

Live demo: [demo.tinyauth.app](https://demo.tinyauth.app/) — username `user`, password `password`.

### Comparison

| Project | Language | OpenID Certified | Resource Use | Learning Curve |
|---------|----------|-----------------|--------------|----------------|
| **Tinyauth** | Go | ✅ Basic OP | Minimal | Low |
| Authentik | Python | ✅ | Heavy | High |
| Authelia | Go | ❌ | Medium | Medium |
| Keycloak | Java | ✅ | Very heavy | Very high |

Tinyauth's positioning is clear: personal homelabs and small-team self-hosting. Not the right tool for complex enterprise SSO with dozens of integration requirements.

### License Note

Tinyauth uses **AGPL-3.0**. Personal and internal self-hosting: no restrictions. Wrapping Tinyauth as a commercial SaaS: the modified source must be made available to users. Relevant to know before building a product on top of it.

### Why This Matters

**"Tiniest" is accurate, not marketing.** Single Go binary, minimal RAM — runs on a Raspberry Pi without thinking twice.

**OpenID Certified™ means the OIDC implementation is trustworthy** — not a bespoke OAuth flow cobbled together, but a spec-compliant implementation validated by the Foundation's test suite.

**Active community.** 8K+ stars, Discord server, Crowdin localization, sponsored by JetBrains and CodeRabbit. Not a personal toy project that'll be abandoned in six months.

For self-hosters running Traefik-based stacks, Tinyauth is one of the lowest-friction unified auth solutions available right now.

Repository: [github.com/tinyauthapp/tinyauth](https://github.com/tinyauthapp/tinyauth) · Docs: [tinyauth.app](https://tinyauth.app/) · Demo: [demo.tinyauth.app](https://demo.tinyauth.app/)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
