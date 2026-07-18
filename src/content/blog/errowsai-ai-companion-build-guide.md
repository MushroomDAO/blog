---
title: "用 ErrowsAI 搭建自己的 AI 伴侣平台：全栈开源指南"
titleEn: "Build Your Own AI Companion with ErrowsAI: Full-Stack Open-Source Guide"
description: "ErrowsAI 是一个完整的 AI 角色平台开源项目，支持角色创建、流式对话、实时语音通话、图像生成和社区功能。本文拆解其架构，带你用这套代码构建属于自己的 AI 伴侣产品。"
descriptionEn: "ErrowsAI is a full-stack open-source AI companion platform with character creation, streaming chat, real-time voice calls, image generation, and community features. This guide breaks down the architecture and shows you how to build your own AI companion product."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-Experiment"
tags: ["AI伴侣", "开源", "全栈", "Moleculer", "React", "语音通话", "角色扮演", "AI应用开发"]
heroImage: "../../assets/images/errowsai-ai-companion-guide-banner.jpg"
---

AI 伴侣类产品近两年越来越主流——从 Character.ai 到 Replika，再到各种垂直场景的定制化应用。但市面上大多数是闭源产品，你无法控制数据、无法定制逻辑、也无法把它变成自己的产品。

GitHub 仓库 **sethyu1/ErrowsAI**（MIT 协议）提供了一套完整的全栈 AI 角色平台实现，不只是一个演示项目——它包含用户体系、订阅付费、实时语音通话、图像生成、社区互动，是一个真实可部署的产品级代码库。

---

## ErrowsAI 是什么

一句话：一个让你创建 AI 角色、和角色聊天/打语音电话/生成图片、并把这些角色发布给社区的平台。

核心功能一览：

- **角色创建**：引导式构建（性别/风格/性格/外貌），用 xAI Grok 做 AI 辅助人设完善，自动生成角色头像、开场白和背景图
- **AI 对话**：带人设和会话记忆的流式角色对话，支持消息级媒体（图片/视频/语音）
- **实时语音通话**：Agora RTC + ConvoAI 实现，LLM + ASR + MiniMax TTS 三层管线
- **图像和视频生成**：用户发起媒体生成请求，后台异步任务调用外部 AI 端点
- **社区**：角色分享、帖子、评论、点赞、关注、内容反馈
- **变现**：金币余额、会员计划、Stripe 订阅/单次付款、礼物道具、CD Key 兑换
- **管理后台**：运营看板、LLM 调用监控、收益统计、角色审核、Grafana 仪表盘

---

## 架构拆解

```
用户端（Web / App）
    │
    ▼
nginx ──▶ api.service (REST :5003)
            │
            ├─ user.service     ← 认证、用户资料、OAuth、短信 OTP
            ├─ errows.service   ← 角色、对话、会话、帖子、媒体
            ├─ payment.service  ← Stripe、金币、会员计划、礼物
            └─ ops.service      ← 管理后台操作
```

**Moleculer 微服务**：后端是一组 [Moleculer](https://moleculer.services/) 服务，通过 TCP 传输层互相通信。`api.service` 是 REST 网关，其他服务独立部署、独立重启（`errows@<name>` systemd 单元）。

**monorepo 结构**（pnpm + Node 18+）：

| 目录 | 说明 |
|------|------|
| `apps/errows-web` | 用户前端 — React 19 + Vite + Tailwind + Capacitor（支持打包成 App） |
| `apps/errows-console` | 管理后台 — React 19 + Ant Design |
| `backend/errows` | API 服务 — Moleculer 微服务、REST 网关（:5003）、PostgreSQL、数据库迁移 |
| `backend/ai` | AI 提供商集成（对话/图像/视频/TTS） |
| `backend/models` | 共享数据模型 |
| `config/` | nginx 配置、systemd 单元、Grafana 仪表盘 |

**数据库**：PostgreSQL，存储用户、角色、会话/消息、帖子/评论、会员/计划、购买记录、礼物、任务、CD Key。Schema 在 `backend/errows/db/migrations`（纯 SQL，通过 `errowsctl` 执行）。

---

## 语音通话是怎么实现的

这是 ErrowsAI 技术含量最高的部分，用的是三方集成：

```
用户 ──Agora RTC──▶ 后端 ──ConvoAI──▶ LLM（xAI Grok）
                                  │
                                  ▼
                         ASR（语音转文字）
                                  │
                                  ▼
                         MiniMax TTS（角色声音）
                                  │
                                  ▼
                         Agora RTC ──▶ 用户
```

流程：
1. 后端下发 Agora RTC 令牌
2. 在用户频道里启动一个 ConvoAI 代理
3. ConvoAI 把角色人设注入 LLM，把角色声音注入 MiniMax TTS
4. 用户说话 → ASR 转文字 → Grok 生成回复 → TTS 合成声音 → 通过 RTC 播放

---

## 本地快速启动

### 前提

- Node.js ≥ 18、pnpm 10
- PostgreSQL（数据库名 `errows`）

### 安装

```bash
git clone https://github.com/sethyu1/ErrowsAI
cd ErrowsAI
pnpm install
```

### 配置

后端配置文件在 `backend/errows/config/`，支持按环境覆盖（不要把密钥放进 git，用本地覆盖文件）：

```js
// backend/errows/config/local-development.mjs
export default {
  pg: { password: 'your-pg-password' },
  jwt: { secret: 'your-jwt-secret' },
  stripe: {
    apiKey: 'sk_test_...',
    webhookSecret: 'whsec_...',
  },
  ai: {
    chat: { endpoint: 'http://your-llm-endpoint' },
  },
}
```

关键环境变量：

| 变量 | 说明 |
|------|------|
| `PG_PASSWORD` | PostgreSQL 密码 |
| `JWT_SECRET` | JWT 签名密钥 |
| `STRIPE_API_KEY` | Stripe 支付 |
| `XAI_API_KEY` | xAI Grok（角色人设完善 + 语音通话 LLM） |
| `MINIMAX_TTS_KEY` | MiniMax TTS（角色声音） |
| `AGORA_APP_CERTIFICATE` | Agora RTC |
| `AWS_ACCESS_KEY_ID / SECRET` | S3 媒体存储 |
| `AI_CHAT_ENDPOINT` | 自定义 AI 对话端点 |

### 初始化数据库和启动

```bash
pnpm errowsctl bootstrap        # 创建 schema
pnpm errowsctl migration upgrade  # 执行迁移

pnpm server dev    # API 服务（热更新，http://localhost:5003）
pnpm start         # 前端 dev server
pnpm start:console # 管理后台（http://localhost:9528）
```

---

## 如果你要基于它构建自己的产品

**可以直接替换的模块：**
- **LLM 供应商**：默认用 xAI Grok，配置 `AI_CHAT_ENDPOINT` 可换成任何兼容 OpenAI 格式的端点（Claude、本地 LLM 等）
- **TTS 声音**：换掉 MiniMax TTS，对接任意 TTS API
- **图像生成**：`backend/ai` 里的 AI 提供商集成是独立模块，可以替换成 Stable Diffusion、FLUX、ComfyUI
- **支付**：Stripe 已经完整集成，也可以换成本地支付方案

**需要自己做的部分：**
- 角色数据的版权和内容审核策略
- 用户协议和隐私政策（涉及 AI 生成内容）
- 媒体存储成本（S3 或自建 CDN）
- LLM API 费用规划（高并发场景下 token 消耗是主要成本）

**硬件和部署**：项目自带 systemd 配置（`config/`）和 nginx 反代设置，可以直接部署到 VPS 或云服务器。Grafana 监控面板已内置，接入 Prometheus 后即可查看 LLM 调用量、收益和用户活跃度。

---

## 适合谁

- **想做 AI 伴侣类产品的独立开发者**：省去从零搭建用户体系、支付、语音通话的时间
- **企业内部 AI 助手**：有人设角色的内部客服/助手，可以基于这套改造
- **研究 AI 应用架构的开发者**：Moleculer 微服务 + 多模态 AI 集成是个不错的学习案例
- **不适合**：希望完全 zero-cost 运行的项目（语音通话、图像生成、LLM 都是按量付费的第三方服务）

---

## 资源链接

- [ErrowsAI GitHub](https://github.com/sethyu1/ErrowsAI) — MIT 协议
- [Moleculer 文档](https://moleculer.services/) — 微服务框架
- [Agora ConvoAI](https://www.agora.io/en/products/conversational-ai-engine/) — 实时 AI 语音
- [MiniMax TTS](https://minimax.chat/) — 语音合成

© 2026 Author: Mycelium Protocol

<!--EN-->

## Build Your Own AI Companion with ErrowsAI: Full-Stack Open-Source Guide

AI companion products have gone mainstream — from Character.ai to Replika to countless vertical apps. But almost all of them are closed-source: you can't control the data, customize the logic, or turn it into your own product.

The GitHub repo **sethyu1/ErrowsAI** (MIT license) delivers a complete, production-ready full-stack AI character platform. Not a demo — a real codebase with auth, subscriptions, real-time voice calls, image generation, and community features, all wired together and deployable.

---

### What ErrowsAI Is

A platform where users create AI characters, chat with them via streaming text or real-time voice, generate images and videos, and share characters with a community.

Core capabilities:
- **Character creation**: guided builder (gender/style/personality/appearance) + xAI Grok for AI-assisted persona refinement, auto-generated avatars, greetings, and backgrounds
- **AI chat**: streaming conversations with per-character persona and session memory
- **Real-time voice calls**: Agora RTC + ConvoAI + LLM (Grok) + ASR + MiniMax TTS pipeline
- **Image & video generation**: async task queue calling external AI endpoints, results uploaded to S3
- **Community**: character sharing, posts, comments, likes, follows
- **Monetization**: coin economy, Stripe subscriptions, membership plans, gift items, CD-key redemption
- **Admin console**: usage/LLM/revenue dashboards, content moderation, Grafana monitoring

---

### Architecture

The backend is a [Moleculer](https://moleculer.services/) microservice cluster: `api.service` (REST gateway on :5003) routes to `user.service`, `errows.service`, `payment.service`, and `ops.service`, communicating over TCP. Each service runs as an independent systemd unit and can be restarted without affecting the others.

Data lives in PostgreSQL (users, characters, sessions/messages, posts/comments, purchases, membership plans, gifts). Schema migrations are plain SQL applied via `errowsctl`.

Frontend is React 19 + Vite + Tailwind, wrapped with Capacitor for mobile packaging.

---

### Getting Started

```bash
git clone https://github.com/sethyu1/ErrowsAI
cd ErrowsAI
pnpm install

# Configure backend (never put secrets in tracked files)
# Create: backend/errows/config/local-development.mjs

pnpm errowsctl bootstrap          # create DB schema
pnpm errowsctl migration upgrade  # run migrations
pnpm server dev                   # API server (localhost:5003)
pnpm start                        # frontend dev server
```

Key environment variables: `PG_PASSWORD`, `JWT_SECRET`, `STRIPE_API_KEY`, `XAI_API_KEY` (for character persona + voice LLM), `MINIMAX_TTS_KEY`, `AGORA_APP_CERTIFICATE`, `AWS_ACCESS_KEY_ID/SECRET` (media storage).

---

### Customizing for Your Own Product

The AI provider layer (`backend/ai`) is designed to be swapped. Set `AI_CHAT_ENDPOINT` to any OpenAI-compatible endpoint to replace Grok with Claude, a local LLM, or any other provider. TTS and image generation services are similarly configurable via environment variables.

The main costs to plan for in production: LLM API calls (the dominant cost at scale), Agora RTC minutes (voice calls), MiniMax TTS synthesis, and S3 media storage.

---

### Resources

- [ErrowsAI on GitHub](https://github.com/sethyu1/ErrowsAI) — MIT
- [Moleculer microservices](https://moleculer.services/)
- [Agora ConvoAI](https://www.agora.io/en/products/conversational-ai-engine/)

© 2026 Author: Mycelium Protocol
