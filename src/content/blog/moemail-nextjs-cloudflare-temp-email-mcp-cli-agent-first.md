---
title: "MoeMail：可爱的临时邮箱服务，NextJS + Cloudflare 免费自托管，自带 MCP Server 和 Agent CLI"
titleEn: "moemail-nextjs-cloudflare-temp-email-mcp-cli-agent-first"
description: "MoeMail 是一个基于 NextJS + Cloudflare 全家桶（Pages + D1 + Email Workers + KV）构建的开源临时邮箱服务，免费自托管零成本。特色功能：RBAC 角色权限系统（皇帝/公爵/骑士/平民）、Resend 收发邮件、Webhook 推送、OpenAPI + API Key、Agent-first CLI（@moemail/cli）、MCP Server（@moemail/mcp，支持 Claude Desktop / Cursor / Cline）。2024-12 上线，2,799 Star，2,572 Fork，MIT 开源。"
descriptionEn: "MoeMail is an open-source temporary email service built with NextJS + Cloudflare (Pages + D1 + Email Workers + KV), free to self-host at zero cost. Key features: RBAC permission system (Emperor/Duke/Knight/Civilian), sending via Resend, Webhook push, OpenAPI + API Key, Agent-first CLI (@moemail/cli), and MCP Server (@moemail/mcp supporting Claude Desktop / Cursor / Cline). Launched December 2024, 2,799 stars, 2,572 forks, MIT."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Tech-News"
tags: ["开源", "临时邮箱", "Cloudflare", "NextJS", "MCP", "AI Agent", "自托管", "隐私"]
heroImage: "../../assets/images/moemail-nextjs-cloudflare-temp-email-mcp-cli-agent-first-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：beilunyang/moemail ⭐ 2,799 | Forks 2,572 | TypeScript | MIT  
Live Demo：https://moemail.app  
文档：https://docs.moemail.app  
创建：2024-12-01

---

## 一句话

临时邮箱 + 完整自托管 + MCP Server + Agent-first CLI。免费，可爱，能用 Claude Desktop 原生调用。

---

## 为什么需要临时邮箱

注册一个不常用的服务、验证一个账号、接收一封邮件、测试自己产品的邮件发送——这些场景有一个共同点：你不想用真实邮箱。

MoeMail 解决这个问题的方式是：开源 + 免费 + 跑在 Cloudflare 上（Pages + D1 + Email Workers + KV，全部免费层可用），你可以在几分钟内部署一套完整的私有临时邮箱服务。

2572 个 Fork（vs 2799 个 Star）意味着绝大多数 Star 的人都真的跑了自己的实例——这个 Fork 比率在开源项目里极少见，几乎直接说明了这个工具的实用度。

---

## 核心功能

### 临时邮箱基础能力

- **实时接收**：自动轮询，新邮件即时到达
- **灵活有效期**：1 小时、24 小时、3 天、永久，按需选
- **自动清理**：过期邮箱和邮件自动删除
- **多域名支持**：在配置页填多个域名，逗号分隔
- **邮件分享**：可以生成带时效的邮箱或单封邮件的分享链接

### 发送功能（基于 Resend）

不只是收，还可以用临时地址发邮件。接入 Resend API Key 后，开通的账号可以以临时邮箱地址作为发件人发送 HTML 格式邮件。不同角色有不同的每日发送限额：

| 角色 | 每日限额 |
|------|----------|
| 皇帝（Emperor）| 无限制 |
| 公爵（Duke）| 默认 5 封/天 |
| 骑士（Knight）| 默认 2 封/天 |
| 平民（Civilian）| 禁止 |

### Webhook

有新邮件到达时，向你配置的 URL 发送 POST 请求。Payload 包含 fromAddress、subject、content、html、receivedAt 等字段。非 2xx 响应自动重试。10 秒超时。

适合：把临时邮箱接收的验证码自动推送到其他系统，或者接入自动化流程。

---

## 权限系统（RBAC）

MoeMail 有一套完整的角色权限体系，分四级：

```
皇帝（Emperor）
  └─ 站点所有者，全部权限，唯一
公爵（Duke）
  └─ 创建临时邮箱 + Webhook 配置 + API Key 管理
骑士（Knight）
  └─ 创建临时邮箱 + Webhook 配置
平民（Civilian）
  └─ 无权限（等待皇帝提升）
```

第一个访问 `/api/roles/init-emperor` 的用户自动成为皇帝。之后皇帝可以在 User Profile 页面升降其他用户的角色。新用户默认角色（Civilian / Knight / Duke）也可以由皇帝在系统设置里调整。

---

## OpenAPI

有了 API Key（Duke 或 Emperor 角色可创建），可以通过 HTTP 接口操作整套系统。主要接口：

```http
# 生成临时邮箱
POST /api/emails/generate
{ "name": "test", "expiryTime": 3600000, "domain": "moemail.app" }

# 获取邮箱列表
GET /api/emails

# 获取邮箱下的邮件列表
GET /api/emails/{emailId}

# 读取单封邮件
GET /api/emails/{emailId}/{messageId}

# 删除邮箱
DELETE /api/emails/{emailId}

# 创建分享链接
POST /api/emails/{emailId}/share
```

---

## Agent-first CLI：`@moemail/cli`

这是 MoeMail 最有趣的能力之一——它明确把 CLI 设计为面向 AI Agent 的工具，而不是面向人类操作员。

```bash
npm i -g @moemail/cli

# 配置 API 端点和 Key
moemail config set api-url https://moemail.app
moemail config set api-key YOUR_API_KEY

# 3 步完成 AI Agent 验证邮件流程：

# 1. 创建临时邮箱
EMAIL=$(moemail create --domain moemail.app --expiry 1h --json)
EMAIL_ID=$(echo $EMAIL | jq -r '.id')
ADDRESS=$(echo $EMAIL | jq -r '.address')

# 2. 等待验证邮件（轮询，最多 120 秒）
MSG=$(moemail wait --email-id $EMAIL_ID --timeout 120 --json)
MSG_ID=$(echo $MSG | jq -r '.messageId')

# 3. 读取内容，提取验证码
CONTENT=$(moemail read --email-id $EMAIL_ID --message-id $MSG_ID --json)
```

所有命令都支持 `--json` 输出，配合 `jq` 使用，方便 AI Agent 解析结果。

更直接的方式：

```bash
# 自动检测并安装到 Claude Code / Codex
moemail skill install

# 或指定平台
moemail skill install --platform claude
moemail skill install --platform codex
```

安装后，Claude Code 或 Codex 会自动知道如何调用 MoeMail 处理邮件相关任务。

---

## MCP Server：`@moemail/mcp`

比 CLI 更原生——MoeMail 提供了 MCP Server，让 Claude Desktop、Cursor、Cline 等 MCP 客户端直接以工具调用的方式操作临时邮箱，无需 shell。

**支持的 MCP 工具：**

| 工具 | 功能 |
|------|------|
| `create_email` | 创建临时邮箱（1h / 24h / 3d / 永久） |
| `list_emails` | 列出当前 API Key 下的所有邮箱 |
| `list_messages` | 列出某个邮箱的邮件 |
| `read_message` | 读取邮件全文（text + HTML） |
| `wait_for_email` | 轮询等待新邮件（有时限，超时返回 status: "timeout" 供重试） |
| `send_email` | 从临时地址发送邮件 |
| `delete_email` | 删除邮箱 |
| `delete_message` | 删除单封邮件 |

**配置 Claude Desktop：**

```json
{
  "mcpServers": {
    "moemail": {
      "command": "npx",
      "args": ["-y", "@moemail/mcp"],
      "env": {
        "MOEMAIL_API_KEY": "YOUR_API_KEY",
        "MOEMAIL_API_URL": "https://moemail.app"
      }
    }
  }
}
```

完成后，Claude Desktop 就能直接说"帮我创建一个临时邮箱等验证码"，后端调用 MCP 工具完成整个流程。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 框架 | Next.js App Router |
| 平台 | Cloudflare Pages |
| 数据库 | Cloudflare D1（SQLite） |
| 邮件处理 | Cloudflare Email Workers |
| KV 存储 | Cloudflare KV（系统设置） |
| 认证 | NextAuth（GitHub / Google OAuth） |
| 样式 | Tailwind CSS + Radix UI |
| ORM | Drizzle ORM |
| 国际化 | next-intl（中文 + 英文） |
| 发件 | Resend |

全部跑在 Cloudflare，不需要独立服务器，免费层足以支撑个人和小团队使用。

---

## 部署

三种方式，按需选：

**一键部署（Cloudflare Workers 按钮）**：点击 README 里的 Deploy to Cloudflare Workers 按钮，按向导填写环境变量，10 分钟内完成。

**GitHub Actions 自动部署**：在 repo Settings 里配置 Secrets（CLOUDFLARE_API_TOKEN 等），推送 `v1.0.0` 这样的 Tag 自动触发部署流水线。

**本地 Wrangler 手动部署**：clone 仓库，`pnpm install`，复制配置文件，执行 `pnpm dlx tsx ./scripts/deploy/index.ts`。

---

## 为什么值得关注

MoeMail 的有趣之处不只是"临时邮箱"这个功能本身——是它作为基础设施的定位。

**给人类用**：一个可爱的、可以完全私有化部署的临时邮箱服务，0 成本，0 对外依赖。

**给 AI Agent 用**：CLI 的 `--json` 输出、`wait` 命令的有界轮询、MCP Server 的 8 个工具——这些设计细节表明它把 AI Agent 作为第一公民。注册/验证场景是 AI Agent 最常遇到的人机验证关卡之一，MoeMail 提供了一个标准化、可编程的突破口。

随着 Agent 越来越多地需要自主处理邮件验证，MoeMail 这类项目会成为 Agent 基础设施栈的标准组件。

---

**相关链接**

- GitHub：https://github.com/beilunyang/moemail
- Live Demo：https://moemail.app
- 文档：https://docs.moemail.app
- CLI npm：https://www.npmjs.com/package/@moemail/cli
- MCP npm：https://www.npmjs.com/package/@moemail/mcp
- Product Hunt：https://www.producthunt.com/products/moemail

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## MoeMail: Cute Self-Hosted Temp Email — NextJS + Cloudflare, Free, with MCP Server and Agent CLI

*by Mycelium Protocol*

---

GitHub: beilunyang/moemail ⭐ 2,799 | Forks 2,572 | TypeScript | MIT  
Live demo: https://moemail.app  
Docs: https://docs.moemail.app  
Created: 2024-12-01

---

### The One-Liner

Temporary email + full self-hosting + MCP Server + Agent-first CLI. Free, cute, and natively callable from Claude Desktop.

---

### Why Temp Email

Registering for a service you don't trust, verifying an account, receiving a one-time email, testing your own product's email flow — these all share one thing: you don't want to expose your real address.

MoeMail's approach: open source, free, runs entirely on Cloudflare (Pages + D1 + Email Workers + KV, all on free tier), deployable in minutes.

2,572 forks against 2,799 stars — a fork-to-star ratio near 1:1 is extremely rare in open source. It means almost everyone who starred this project actually deployed their own instance. That's a direct signal of practical utility.

---

### Core Features

**Base temp email capabilities:**
- Real-time polling — new emails arrive instantly
- Flexible expiry: 1h / 24h / 3d / permanent
- Auto-cleanup of expired mailboxes and messages
- Multi-domain support (comma-separated in config)
- Share links: timed-access links to a mailbox or individual message

**Sending (via Resend):**

Not just receiving — MoeMail supports sending from temporary addresses using a Resend API key. Different roles have different daily limits:

| Role | Daily send limit |
|------|-----------------|
| Emperor | Unlimited |
| Duke | 5/day (default) |
| Knight | 2/day (default) |
| Civilian | Forbidden |

**Webhook:**

POST to a configured URL whenever a new email arrives. Payload includes fromAddress, subject, content, html, receivedAt. Non-2xx responses trigger a retry. 10-second timeout.

---

### RBAC Permission System

Four role levels:

```
Emperor  — Site owner, all permissions, one per site
Duke     — Create email + Webhook + API Key management
Knight   — Create email + Webhook
Civilian — No permissions (awaiting promotion)
```

The first user to visit `/api/roles/init-emperor` becomes Emperor. The Emperor manages other users' roles from the User Profile page. Default role for new users (Civilian / Knight / Duke) is configurable.

---

### OpenAPI

Create an API Key (Duke or Emperor required) and call the full system over HTTP:

```http
POST /api/emails/generate    # create mailbox
GET  /api/emails             # list mailboxes  
GET  /api/emails/{emailId}   # list messages
GET  /api/emails/{emailId}/{messageId}  # read message
DELETE /api/emails/{emailId} # delete mailbox
POST /api/emails/{emailId}/share  # create share link
```

---

### Agent-First CLI: `@moemail/cli`

MoeMail explicitly designed its CLI for AI agents, not for human operators.

```bash
npm i -g @moemail/cli
moemail config set api-url https://moemail.app
moemail config set api-key YOUR_API_KEY

# Typical agent verification flow — 3 tool calls:

# 1. Create mailbox
EMAIL=$(moemail create --domain moemail.app --expiry 1h --json)
EMAIL_ID=$(echo $EMAIL | jq -r '.id')

# 2. Wait for verification email (bounded poll, max 120s)
MSG=$(moemail wait --email-id $EMAIL_ID --timeout 120 --json)
MSG_ID=$(echo $MSG | jq -r '.messageId')

# 3. Read content and extract code
CONTENT=$(moemail read --email-id $EMAIL_ID --message-id $MSG_ID --json)
```

All commands support `--json` output for machine parsing. Auto-install the skill into Claude Code or Codex:

```bash
moemail skill install                      # auto-detect
moemail skill install --platform claude    # Claude Code
moemail skill install --platform codex    # Codex
```

After install, Claude Code and Codex automatically know how to use MoeMail for email-handling tasks.

---

### MCP Server: `@moemail/mcp`

More native than the CLI — MoeMail ships an MCP server so Claude Desktop, Cursor, Cline, and any other MCP client can call temp email operations as structured tools, no shell required.

**8 MCP tools:**

| Tool | Function |
|------|----------|
| `create_email` | Create mailbox (1h / 24h / 3d / permanent) |
| `list_emails` | List all mailboxes for the API key |
| `list_messages` | List messages in a mailbox |
| `read_message` | Read full text/HTML of a message |
| `wait_for_email` | Poll for new message (bounded; returns `timeout` to retry) |
| `send_email` | Send from a temp address |
| `delete_email` | Delete a mailbox |
| `delete_message` | Delete a single message |

**Claude Desktop config:**

```json
{
  "mcpServers": {
    "moemail": {
      "command": "npx",
      "args": ["-y", "@moemail/mcp"],
      "env": {
        "MOEMAIL_API_KEY": "YOUR_API_KEY",
        "MOEMAIL_API_URL": "https://moemail.app"
      }
    }
  }
}
```

After that, Claude Desktop can handle "create a temp email and wait for a verification code" as a native, structured workflow.

---

### Tech Stack

| Layer | Tech |
|-------|------|
| Framework | Next.js App Router |
| Platform | Cloudflare Pages |
| Database | Cloudflare D1 (SQLite) |
| Email handling | Cloudflare Email Workers |
| KV storage | Cloudflare KV (system settings) |
| Auth | NextAuth (GitHub / Google OAuth) |
| Styling | Tailwind CSS + Radix UI |
| ORM | Drizzle ORM |
| i18n | next-intl (Chinese + English) |
| Sending | Resend |

Entirely on Cloudflare — no standalone server needed. Free tier handles personal and small-team usage.

---

### Deployment

Three options:

**One-click**: Click the "Deploy to Cloudflare Workers" button in the README, fill in env vars via the wizard, done in 10 minutes.

**GitHub Actions**: Configure Secrets (CLOUDFLARE_API_TOKEN, etc.) in repo settings. Push a `v1.0.0`-style tag to trigger automated deployment.

**Manual Wrangler**: Clone, `pnpm install`, copy config files, run `pnpm dlx tsx ./scripts/deploy/index.ts`.

---

### Why It Matters

MoeMail is interesting not just as a temp email feature — but as infrastructure.

**For humans**: A cute, fully private-deployable temp email service. Zero cost, zero external dependencies.

**For AI agents**: The `--json` CLI output, the bounded `wait` polling, the 8 MCP tools — these design details signal that AI agents are first-class consumers. Email verification is one of the most common human-gate checkpoints agents encounter. MoeMail provides a standardized, programmable way through it.

As agents increasingly need to autonomously handle email verification flows, MoeMail-style tools will become standard components of the agent infrastructure stack.

---

**Links**

- GitHub: https://github.com/beilunyang/moemail
- Live demo: https://moemail.app
- Docs: https://docs.moemail.app
- CLI npm: https://www.npmjs.com/package/@moemail/cli
- MCP npm: https://www.npmjs.com/package/@moemail/mcp
- Product Hunt: https://www.producthunt.com/products/moemail

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
