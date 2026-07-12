---
title: "openilink-hub 搭建微信消息平台：开源自托管，20 款应用开箱即用"
titleEn: "openilink-hub: Open-Source Self-Hosted WeChat Bot Platform with 20+ App Marketplace"
description: "用 openilink-hub 把微信 Bot 变成完整平台：单文件部署，Slack、GitHub、飞书、AI Agent 全接入。"
descriptionEn: "Build a complete WeChat Bot ecosystem with openilink-hub: single-binary deploy, 20+ app marketplace, AI Agent integration via OpenAI-compatible API."
pubDate: "2026-07-11"
updatedDate: "2026-07-11"
category: "Tech-Experiment"
tags: ["iLink", "开源", "AI Agent"]
heroImage: "../../assets/images/openilink-hub-wechat-bot-platform-guide-banner.jpg"
---

> 本文基于 [openilink/openilink-hub](https://github.com/openilink/openilink-hub)（MIT 协议，Go 实现）整理，涵盖部署、应用市场接入和 AI Agent 搭建三个核心环节。

---

## 一、背景

微信 ClawBot 是微信官方在 2026 年初推出的 Bot 能力，底层叫 iLink/智联协议，这是微信第一次通过正式渠道开放消息收发接口。

但 iLink 本身只是原始通道——消息进来了，怎么管理、怎么路由、怎么接第三方工具，全要自己写。openilink-hub 就是在 iLink 上封装了完整管理层的开源平台：可视化后台、应用市场、多通道分发、AI Agent 网关，一套搞定。

---

## 二、架构概览

| 层次 | 说明 |
|------|------|
| 接入层 | iLink SDK 接收微信消息 |
| 调度层 | Message Broker 并行分发 |
| 应用层 | App 市场（20+ 工具）+ WebSocket + Webhook + AI Sink |
| 后端 | Go，SQLite（默认）或 PostgreSQL |
| 前端 | React + TypeScript + Tailwind CSS |
| 认证 | Passkey / OAuth 2.0 (PKCE) |

---

## 三、5 分钟部署

### 最简单（单文件二进制）

```bash
curl -fsSL https://raw.githubusercontent.com/openilink/openilink-hub/main/install.sh | sh
oih
```

数据默认存在 `~/.local/share/openilink-hub/`，无需配置数据库。

### Docker（推荐）

```bash
docker run -d -p 9800:9800 openilink/openilink-hub:latest
```

### 生产环境（PostgreSQL + MinIO）

```yaml
services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: openilink
      POSTGRES_PASSWORD: <强密码>
      POSTGRES_DB: openilink
    volumes:
      - pgdata:/var/lib/postgresql/data

  hub:
    image: openilink/openilink-hub:latest
    ports:
      - "9800:9800"
    environment:
      DATABASE_URL: postgres://openilink:<密码>@postgres:5432/openilink?sslmode=disable
      RP_ORIGIN: https://hub.example.com
      RP_ID: hub.example.com
      SECRET: <随机字符串>
    depends_on:
      - postgres
```

前面架 Nginx/Caddy 做 HTTPS 反代，`oih install` 注册系统服务（支持 systemd/launchd）。

---

## 四、应用市场（20+）

安装完成后，在后台的 App 市场里一键启用，PKCE OAuth 授权后即可使用。

### 平台互通

- **飞书** — 34 个 AI Tools（日历、云文档、多维表格等 11 大业务域）
- **Slack** — 23 个 AI Tools
- **Discord** — 19 个 AI Tools
- **钉钉** — 20 个 AI Tools
- **企业微信** — 18 个 AI Tools

### 效率工具

- **GitHub** — 36 个 AI Tools（Issue、PR、Actions、Release）
- **Google Workspace** — 18 个 AI Tools（Gmail、Calendar、Drive、Docs）
- **Notion** — 15 个 AI Tools
- **Linear** — 13 个 AI Tools

### 零配置工具

天气、汇率、记账、提醒、定时任务、RSS、二维码。

---

## 五、接入 AI Agent

Hub 提供三个通道：

### 方式 1：AI Sink（最简单）

在后台填入 OpenAI 兼容 API endpoint + key，Bot 自动对话，支持：

- Coze、扣子（OpenAI 兼容接口）
- 本地 Ollama（`http://localhost:11434/v1`）
- LangChain 服务端
- 任何 OpenAI 格式的 API

### 方式 2：WebSocket 实时推送

AI Agent 订阅 Hub 的 WebSocket，毫秒级收到消息后自行处理，再通过 Hub API 回复。

### 方式 3：Webhook HTTP 回调

消息触达时 POST 到你的服务，适合接已有的后端逻辑。

---

## 六、SDK 开发自己的 App

7 种语言 SDK，3 分钟上手：

```python
pip install openilink-sdk-python
```

```javascript
npm install @openilink/openilink-sdk-node
```

```go
go get github.com/openilink/openilink-sdk-go
```

Hub 自带 Mock Server，本地开发无需真实微信 Bot：

```bash
go run ./cmd/appmock --webhook-url http://localhost:8080/webhook
curl -X POST http://localhost:9801/mock/event \
  -d '{"sender":"alice","content":"@test-app hello"}'
```

---

## 七、总结

| 能力 | 说明 |
|------|------|
| 部署 | 单文件/Docker，5 分钟启动 |
| 应用市场 | 20+ 工具一键接入，无需手写 API |
| AI 接入 | OpenAI 兼容 API 直接配置 |
| SDK | 7 种语言，支持二次开发 |
| 安全 | Passkey 登录，数据本地 |
| 协议 | MIT 开源，可商用 |

GitHub：[openilink/openilink-hub](https://github.com/openilink/openilink-hub)

在线体验：[hub.openilink.com](https://hub.openilink.com)

© 2026 Author: Mycelium Protocol

<!--EN-->

## openilink-hub: Open-Source WeChat Bot Platform with App Marketplace

> Based on [openilink/openilink-hub](https://github.com/openilink/openilink-hub) — MIT license, Go backend.

---

### What It Is

openilink-hub is a self-hosted management platform and app marketplace built on top of WeChat's official ClawBot iLink protocol (launched early 2026). iLink is WeChat's first official programmatic messaging channel — but it's a raw pipe. openilink-hub wraps it with a full management layer: visual dashboard, app marketplace, multi-channel dispatch, and AI Agent gateway.

---

### Deploy in 5 Minutes

**Single binary**:
```bash
curl -fsSL https://raw.githubusercontent.com/openilink/openilink-hub/main/install.sh | sh && oih
```

**Docker**:
```bash
docker run -d -p 9800:9800 openilink/openilink-hub:latest
```

Default: SQLite. Production: swap `DATABASE_URL` to PostgreSQL.

---

### App Marketplace (20+)

One-click install from the dashboard. Highlights:
- **Lark/Feishu** — 34 AI Tools across 11 domains
- **Slack** — 23 AI Tools
- **GitHub** — 36 AI Tools (Issues, PRs, Actions)
- **Google Workspace** — 18 AI Tools
- **Notion** — 15 AI Tools

---

### AI Agent Integration

Three channels:
1. **AI Sink** — fill in any OpenAI-compatible API (Coze, Ollama, LangChain). Bot auto-replies.
2. **WebSocket** — sub-millisecond push to your agent; reply via Hub API.
3. **Webhook** — HTTP callback to any backend.

---

### SDK

7 languages: Go, Node.js, Python, PHP, Java, C#, Lua.

Local mock server included — develop without a real WeChat Bot.

---

GitHub: [openilink/openilink-hub](https://github.com/openilink/openilink-hub) · Stars: 1,443 · MIT

© 2026 Author: Mycelium Protocol
