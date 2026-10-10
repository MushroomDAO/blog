---
title: "treg：Agent 的工具网关，一个入口接 2600 个 API"
titleEn: "treg: The OpenRouter for Agent Tools — One Entry Point for 2,600+ APIs"
description: "Superdesign 开源 treg（约 4.9K stars）：「Agent 工具版 OpenRouter」，一个入口 + 一个 Token，Agent 就能搜索并调用 SEO、社媒趋势、数据抓取、联系人查找、图片/视频生成等 2600+ 个 API 端点。团队把自己的 API 账号、OAuth 连接或 SKILL.md 接进来，凭据由服务端 Fernet 加密注入，Agent 机器上从不出现真实密钥。支持自托管（Python FastAPI + SQLite/Postgres，localhost:18790），免费额度 $1，超出按调用计费。需注意：LICENSE 含附加条款，禁止将其作为托管服务向第三方提供，不完全符合 OSI 标准。"
descriptionEn: "Superdesign open-sourced treg (~4.9K stars): 'OpenRouter for agent tools' — one entry + one token lets any Agent search and call 2,600+ API endpoints across SEO, social trends, scraping, people data, image/video generation. Teams register their own API keys, OAuth connections, or SKILL.md files; credentials are Fernet-encrypted and server-injected — never exposed on the Agent machine. Self-hosting via Python FastAPI + SQLite/Postgres at localhost:18790; $1 free credit, pay-per-call beyond. Note: the LICENSE adds a clause prohibiting offering it as a hosted service to third parties — not fully OSI-compliant."
pubDate: 2026-10-10
heroImage: "../../assets/images/treg-superdesign-agent-tool-openrouter-unified-api-gateway-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent", "API网关", "工具调用", "开源工具", "自托管"]
lang: "zh-CN"
wechatTitle: "treg：Agent版OpenRouter，2600个工具一个入口"
wechatDigest: "约4.9K stars；LICENSE含附加条款；密钥服务端注入；团队API统一接入；按调用计费"
---

OpenRouter 做的事情是：给 LLM 调用统一一个入口，你不用管背后是哪家的模型。

treg 要做的是同一件事，但对象换成了工具——给 Agent 的工具调用统一一个入口，你不用管背后每个 API 的密钥在哪、格式是什么。

约 4.9K stars，Superdesign 团队出品，Python FastAPI。GitHub: https://github.com/superdesigndev/treg

---

## 解决的核心问题

一个 Agent 工作流通常要调十几个外部工具：查排名、抓网页、找联系人、发内容、生成图片……每个工具都有 API Key，每台机器都要配，每个新项目都要重新贴一遍。

treg 把这个问题拍平了：

- 团队把所有 API Key 统一存进 treg（服务端加密）
- 每个 Agent 只配一个 `TREG_TOKEN`，指向团队的 treg 实例
- Agent 调工具时 → treg 代理请求 → 服务端注入真实密钥 → 返回结果

**Agent 侧的配置是只读的**：它知道「我可以调哪些工具」，但看不到任何一个真实的 API Key。

---

## 工具目录里有什么

目前收录约 2,600–2,900 个端点，覆盖：

| 类别 | 示例工具 |
|------|---------|
| SEO & 反链 | 搜索排名、外链分析 |
| 社交媒体 & 趋势 | 趋势监控、内容发布（含团队账号） |
| 数据抓取 | 网页 scraping |
| 人员 & 公司数据 | 联系人查找、公司信息富化 |
| 广告数据 | — |
| 图片 & 视频生成 | — |

除目录工具外，团队还可以把**自己的 API 账号**（含 OAuth 连接）、vendor CLI（stripe、gh、vercel 等）或 SKILL.md 文件接进来，供团队内所有 Agent 调用。

---

## 凭据注入的工作方式

存储层：`TREG_SECRET_KEY` 派生的 **Fernet 对称加密**，密钥丢了已存的凭据无法恢复（不可逆）。

调用时：proxy 在服务端注入真实 Key，Agent 机器看到的永远是 `TREG_TOKEN`，而非任何上游 Key。

一个重要细节：如果团队绑定了自己的 API 账号，该账号的调用**不走 treg 计费**，优先使用团队自己的 Key。

---

## 自托管

```bash
# 启动（依赖 tmux + uv）
scripts/dev-local.sh up
# 服务跑在 localhost:18790
```

必须配置：
- `TREG_SECRET_KEY` — 持久化加密密钥（留空则每次启动生成临时 key，重启失效）
- `TREG_DATABASE_URL` — 生产建议 Postgres，开发默认 SQLite

官方也有托管实例（Render + Postgres），新团队赠 $1 免费调用额度。

---

## License 警告

package.json 写的是 Apache-2.0，但 LICENSE 文件里附加了一条限制：**禁止将 treg 作为托管服务向第三方提供**，除非获得书面授权。

自托管供内部团队使用是允许的，但如果你打算把它包成一个服务对外销售，需要先找 Superdesign 拿授权。严格意义上这不是 OSI 标准的「开源」，而是 Source Available。

---

## 已知边界

- `TREG_SECRET_KEY` 丢失 → 所有存储凭据不可恢复，重新配置
- 工具目录 2600+ 端点的实际可用性和维护质量参差不齐
- Agent 集成需要读 AGENTS.md 文档，接入逻辑不是零配置
- 非完全开源（Source Available），商用前核对 LICENSE

---

## 一句话说清楚

treg 是 Agent 工具调用的统一代理网关：一个 Token 换来 2600+ API 的访问权限，密钥服务端加密注入，支持团队自定义工具接入和自托管。LICENSE 含限制条款，内部使用没问题，对外提供服务需授权。

---

> 约 4.9K stars，Superdesign 团队，Python FastAPI，LICENSE 附加限制（Source Available）。开源仅供学习参考，商用前读完 LICENSE。

---

<!--EN-->

## treg: The OpenRouter for Agent Tools — One Entry Point for 2,600+ APIs

OpenRouter unified the entry point for LLM calls — you don't care which provider is behind it. treg does the same thing for tools: one entry point for Agent tool calls, regardless of which API's key lives where or what its format is.

~4.9K stars, Superdesign team, Python FastAPI. GitHub: https://github.com/superdesigndev/treg

---

### The Core Problem

An Agent workflow typically calls a dozen external tools: check rankings, scrape pages, find contacts, post content, generate images... each tool has an API key, each machine needs it configured, every new project needs it re-pasted.

treg flattens this:

- Team stores all API keys centrally in treg (server-side encrypted)
- Each Agent gets one `TREG_TOKEN` pointing at the team's treg instance
- Agent calls a tool → treg proxies → server injects the real key → returns result

**The Agent side is read-only**: it knows "what tools I can call" but never sees any real API key.

---

### What's in the Tool Directory

~2,600–2,900 endpoints across:

| Category | Examples |
|---------|---------|
| SEO & backlinks | search rankings, link analysis |
| Social media & trends | trend monitoring, content publishing |
| Data scraping | web scraping |
| People & company data | contact lookup, company enrichment |
| Ad data | — |
| Image & video generation | — |

Teams can also register their own API accounts (including OAuth connections), vendor CLIs (stripe, gh, vercel), or SKILL.md files — all accessible to every Agent on the team.

---

### How Credential Injection Works

Storage: **Fernet symmetric encryption** derived from `TREG_SECRET_KEY`. If the key is lost, stored credentials are unrecoverable.

At call time: the proxy injects the real key on the server side. The Agent machine always sees only `TREG_TOKEN`.

Important: if a team binds their own API account, calls through that account are **not billed by treg** — the team's own key takes priority.

---

### Self-Hosting

```bash
scripts/dev-local.sh up  # requires tmux + uv
# service runs at localhost:18790
```

Required: `TREG_SECRET_KEY` (persistent encryption key) and `TREG_DATABASE_URL` (Postgres for prod, SQLite for dev). Official hosted instance available on Render; new teams get $1 free credit.

---

### License Warning

package.json says Apache-2.0, but the LICENSE file adds a clause: **prohibits offering treg as a hosted service to third parties** without written authorization.

Internal self-hosting for your own team is fine. If you plan to sell it as a service, you need explicit authorization from Superdesign. Technically this is Source Available, not fully OSI open source.

---

### Known Limits

- Lost `TREG_SECRET_KEY` → all stored credentials unrecoverable, must reconfigure
- Tool directory quality and uptime varies across 2,600+ endpoints
- Agent integration requires reading AGENTS.md — not zero-config
- Not fully open source; check LICENSE before commercial use

---

### TL;DR

treg is a unified proxy gateway for Agent tool calls: one token gives access to 2,600+ APIs, credentials are server-side encrypted and injected, teams can register custom tools and self-host. LICENSE has restrictions — internal use is fine, offering as a service requires authorization.

---

> ~4.9K stars, Superdesign team, Python FastAPI, LICENSE has added restriction (Source Available). For reference only — read the full LICENSE before commercial use.
