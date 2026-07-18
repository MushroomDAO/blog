---
title: "用一个 MCP Server 接入 1000+ 服务：open-connector 完整接入指南"
titleEn: "One MCP Server for 1,000+ Services: Complete open-connector Integration Guide"
description: "open-connector 是一个开源的认证网关，把 1000+ SaaS 服务（GitHub、HackerNews、Twitter、知乎、Cloudflare 等）封装成统一的 MCP 接口，接入 Claude Code 或任何 MCP 兼容的 AI 助手之后，Agent 可以直接查询热门仓库、抓取热帖、操作账号资源——不用再一个个配置 API key 和 OAuth，一次部署解决所有集成。"
descriptionEn: "open-connector is an open-source auth gateway that wraps 1,000+ SaaS services (GitHub, HackerNews, Twitter, Zhihu, Cloudflare and more) into a single MCP interface. Once connected to Claude Code or any MCP-compatible AI host, agents can query repos, fetch trending posts, and manage account resources — no more API key hell or per-service OAuth configuration."
pubDate: "2026-07-07"
updatedDate: "2026-07-07"
category: "Tech-Experiment"
tags: ["MCP", "open-connector", "Claude Code", "API网关", "Cloudflare", "AI Agent", "craft-agents", "GitHub", "一站式集成"]
heroImage: "../../assets/images/open-connector-mcp-agent-integration-guide-banner.jpg"
---

> **仓库**: [oomol-lab/open-connector](https://github.com/oomol-lab/open-connector) · 751★ · Apache-2.0 · TypeScript  
> **组合项目**: [craft-ai-agents/craft-agents-oss](https://github.com/craft-ai-agents/craft-agents-oss) · 6755★

---

## 为什么你需要这个

开发 Agent 最痛的环节不是写代码，是配接口。

GitHub 需要 PAT，Slack 要 OAuth 回调，Twitter API 收费，知乎没有官方 API，Cloudflare 有 API 但要记住十几个资源 ID。每接一个服务就是一个独立的「认证地狱」：不同的 key 格式、不同的 scope 配置、不同的错误处理方式。

**open-connector** 解决的就是这个问题。它是一个开源的认证网关：

- 提前封装了 **1000+ providers、9400+ 预置 Actions** 的访问逻辑
- 统一用 **MCP 接口**暴露给 AI Agent
- 认证信息只需要配置一次，之后 Agent 直接调用 Action 名称

接入之后，你的 Claude Code 可以直接说「查一下 HackerNews 今天热门」「搜一下 GitHub 上 MCP 相关的仓库」，不需要你再手动查 API 文档。

---

## 它的架构是什么样的

```
AI Agent（Claude Code / craft-agent / 任意 MCP 客户端）
        ↓  MCP 调用
open-connector Gateway（http://localhost:3000/mcp）
        ↓  统一认证 + 路由
Provider Catalog（GitHub / HackerNews / Twitter / 知乎 / Cloudflare ...）
```

Gateway 中间做了三件事：
1. **认证管理**：API key、OAuth2、无认证——统一格式存储，Agent 不接触原始凭证
2. **Action 路由**：Agent 只需要知道 `github.search_repositories` 这样的 Action ID，不需要知道具体的 REST 端点
3. **策略控制**：可以设置 allow/block 列表，限制 Agent 能调用哪些 Action

---

## 两种部署方式

open-connector 支持本地 Docker 和 Cloudflare Workers 两种部署。

**本地 Docker**：几分钟跑起来，适合测试和个人开发。  
**Cloudflare 部署**：免费 Workers 额度通常够用，适合长期稳定运行，不占本机资源，推荐。

下面两种都讲，按需选择。

---

## 方式一：本地 Docker 快速启动

**前置条件**：Docker Desktop 已安装并运行。

```bash
# 1. 克隆仓库
git clone https://github.com/oomol-lab/open-connector.git
cd open-connector

# 2. 启动（首次构建需要几分钟）
docker compose up --build

# 3. 确认运行
curl http://localhost:3000
```

启动成功后，访问 `http://localhost:3000` 看到 Web Console，`http://localhost:3000/docs` 看到 API 文档。

**先测一个不需要认证的 Action（HackerNews 热帖）**：

```bash
curl -s -X POST http://localhost:3000/v1/actions/hackernews.get_top_stories \
  -H 'content-type: application/json' \
  -d '{"input":{}}'
```

返回一批 story ID 说明 Gateway 运转正常。

---

## 方式二：Cloudflare 部署（推荐）

**前置条件**：
- Cloudflare 账号（免费）
- Node.js 22+
- `npx wrangler` 可用

### 第一步：克隆并安装依赖

```bash
git clone https://github.com/oomol-lab/open-connector.git
cd open-connector
npm install
```

### 第二步：创建 Cloudflare 资源

```bash
# 登录 Wrangler
npx wrangler login

# 创建 D1 数据库（存储连接配置和 token）
npx wrangler d1 create open-connector

# 创建 R2 存储桶（临时文件传输）
npx wrangler r2 bucket create open-connector-transit-files
```

> 执行 `d1 create` 后，终端会返回 `database_id`，记下来，下一步要用。

### 第三步：配置 Wrangler

```bash
cp wrangler.example.jsonc wrangler.local.jsonc
```

打开 `wrangler.local.jsonc`，填入 D1 的 `database_id`（上一步得到的）。其他配置通常不需要改。

### 第四步：应用数据库迁移

```bash
npx wrangler d1 migrations apply open-connector \
  --remote \
  --config wrangler.local.jsonc
```

### 第五步：设置必要的密钥

```bash
# 管理员 token（你自己定义，用于访问 Web Console）
npx wrangler secret put OOMOL_CONNECT_ADMIN_TOKEN \
  --config wrangler.local.jsonc

# 加密密钥（用于加密存储的认证凭证，建议 32 位随机字符串）
npx wrangler secret put OOMOL_CONNECT_ENCRYPTION_KEY \
  --config wrangler.local.jsonc
```

执行后会提示你输入值，交互式填入即可。

### 第六步：部署

```bash
npm run deploy:cloudflare
```

这个命令会自动生成 provider catalog、构建 Web Console、然后部署到 Cloudflare Workers。

部署成功后，Wrangler 会输出你的 Worker URL，类似 `https://open-connector.yourname.workers.dev`。这就是你的 MCP Gateway 地址，把 `/mcp` 加到末尾即可：

```
https://open-connector.yourname.workers.dev/mcp
```

---

## 配置服务连接

Gateway 跑起来之后，需要把要用的服务的凭证告诉它。以 GitHub 为例：

```bash
# 替换 YOUR_GATEWAY 为你的地址（本地：http://localhost:3000，Cloudflare 是你的 Worker URL）
# 替换 YOUR_ADMIN_TOKEN 为你设置的管理员 token
# 替换 github_pat_xxx 为你的 GitHub Personal Access Token

curl -s -X PUT YOUR_GATEWAY/api/connections/github \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer YOUR_ADMIN_TOKEN' \
  -d '{
    "authType": "api_key",
    "values": {"apiKey": "github_pat_xxx"}
  }'
```

Web Console（访问 `YOUR_GATEWAY`，用 Admin Token 登录）也提供图形界面配置，更直观。

常用服务的认证方式：

| 服务 | 认证方式 | 凭证 |
|---|---|---|
| GitHub | API Key | Personal Access Token |
| HackerNews | 无认证 | 不需要 |
| Cloudflare | API Key | Global API Key 或 API Token |
| Twitter/X | OAuth2 | 通过 Web Console 完成 OAuth 流程 |
| 知乎 | Cookie | 需要手动提取浏览器 Cookie |
| Slack | OAuth2 | 通过 Web Console 完成授权 |
| Notion | API Key | Integration Token |

OAuth2 类服务（Twitter、Slack 等）建议通过 Web Console 界面完成，它会引导你走完授权流程。

---

## 接入 Claude Code

这是核心步骤。把 open-connector 配置为 Claude Code 的 MCP Server，之后 Claude 就能直接调用其中的 Action。

打开 Claude Code 的 MCP 配置文件（`~/.claude.json` 或者通过 `/mcp` 命令管理），添加：

```json
{
  "mcpServers": {
    "open-connector": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

如果用的是 Cloudflare 部署，并且配置了 Runtime Token（推荐，防止 Gateway 被滥用）：

```json
{
  "mcpServers": {
    "open-connector": {
      "type": "http",
      "url": "https://open-connector.yourname.workers.dev/mcp",
      "headers": {
        "Authorization": "Bearer oct_your_runtime_token"
      }
    }
  }
}
```

Runtime Token 在 Web Console 里创建（比 Admin Token 权限小，适合给 Agent 用）。

配置完成后，在 Claude Code 里输入 `/mcp` 确认 open-connector 已连接。

---

## 实际效果：你可以让 Claude 做什么

连接成功之后，Claude Code 里可以直接说：

```
查一下 HackerNews 今天的热门帖子
```

```
在 GitHub 上搜索 stars 最多的 MCP 相关仓库
```

```
列出我 Cloudflare 账号下的 Workers
```

```
搜索知乎上关于 AI Agent 的高赞回答
```

```
查一下 Twitter 上 @AnthropicAI 最近的推文
```

Claude 不需要你提供 API 文档，也不需要你告诉它如何认证——Gateway 已经处理好了，它只需要知道 Action 名称。

open-connector MCP Server 暴露四个核心工具：

| 工具 | 作用 |
|---|---|
| `list_apps` | 列出所有可用的 provider |
| `search_actions` | 搜索特定服务的 Action |
| `get_action_guide` | 获取某个 Action 的详细用法 |
| `execute_action` | 执行一个 Action |

Claude 会在需要时自动调用这几个工具，你不需要直接操作它们。

---

## 与 craft-agents 组合使用

如果你用的是 [craft-agents-oss](https://github.com/craft-ai-agents/craft-agents-oss)（6755★，一个开源 Agent 框架），open-connector 可以作为 MCP Server 直接集成进去，让 Agent 的工具调用能力覆盖 1000+ 服务。

在 craft-agent 的配置里，把 open-connector 的 MCP 端点加入 MCP server 列表：

```yaml
mcp_servers:
  - name: open-connector
    url: http://localhost:3000/mcp
    # 或者 Cloudflare URL + Authorization header
```

集成后，你的 craft-agent 不再需要为 GitHub、HackerNews、Cloudflare 等服务单独写 connector——open-connector 的 Action catalog 直接变成 Agent 的工具集。

---

## 几个注意事项

**关于 Cloudflare 免费额度**：Workers 免费版每天 100,000 次请求，D1 免费版 5GB 存储、每天 5M 行读写——个人和小团队完全够用，不会产生费用。

**关于 OAuth2 服务的 callback URL**：如果你用 Cloudflare 部署，OAuth2 回调 URL 要填你的 Worker URL（`https://open-connector.yourname.workers.dev/api/oauth/callback`），而不是 localhost。在配置 Twitter、Slack 等应用时注意这一点。

**关于 Runtime Token**：建议给 Claude Code 用 Runtime Token（通过 Web Console 创建），而不是直接用 Admin Token。Runtime Token 可以设置权限范围（allow/block 哪些 Action），更安全。

**关于知乎和国内服务**：知乎没有官方 API，open-connector 的实现依赖 Cookie 认证。Cookie 有效期有限，失效后需要重新更新。如果在 Cloudflare 部署，更新 Cookie 需要通过 Web Console 或 API 操作。

---

## 总结

open-connector 的核心价值是**把认证复杂度从 Agent 端移走**。每次你接一个新服务，原来的方式是：找 API 文档 → 申请凭证 → 写认证逻辑 → 处理 token 刷新 → 写错误处理。有了 open-connector，这一切变成：在 Web Console 里配置一次凭证，然后直接让 Claude 调用。

对于个人开发者来说，最推荐的路径是：

1. Cloudflare 部署 Gateway（免费、稳定、不占本机资源）
2. 在 Web Console 里配置你常用的服务
3. 在 Claude Code 里添加 MCP Server
4. 开始用

从克隆仓库到 Claude Code 能查 GitHub 热门仓库，整个流程半小时内可以完成。

---

> **相关链接**
> - [oomol-lab/open-connector](https://github.com/oomol-lab/open-connector) — 主仓库，含完整文档
> - [Cloudflare 部署视频教程](https://www.youtube.com/watch?v=R0V1ZdCuTgc) — 官方 Cloudflare Workers 部署演示
> - [craft-ai-agents/craft-agents-oss](https://github.com/craft-ai-agents/craft-agents-oss) — 可与 open-connector 组合的开源 Agent 框架
> - [oomol-lab/connector-sdk](https://github.com/oomol-lab/connector-sdk) — TypeScript SDK（代码层直接集成用）
> - [oomol-lab/oo-cli](https://github.com/oomol-lab/oo-cli) — 本地 Agent 命令行工具

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: open-connector is an open-source auth gateway that wraps 1,000+ SaaS providers and 9,400+ pre-built Actions into a single MCP endpoint (`http://localhost:3000/mcp`). Connect it to Claude Code once, and your agent can query GitHub repos, fetch HackerNews trends, manage Cloudflare Workers, and search Zhihu — without touching individual API docs or OAuth flows. Two deployment paths: local Docker (minutes) or Cloudflare Workers with D1+R2 (free tier, recommended for stable personal use). Pairs naturally with craft-agents-oss as the universal connector backend for agent tool calls.

---

## What It Solves

Every new API integration for an agent follows the same painful loop: find the API docs, get credentials, write auth logic, handle token refresh, handle errors — then repeat for the next service.

open-connector moves all of that into the gateway. Configure credentials once via the Web Console. After that, the agent calls Actions by name — no API keys in prompts, no auth code in agent logic.

## Deployment (Recommended: Cloudflare)

**Local Docker** (test/dev):
```bash
git clone https://github.com/oomol-lab/open-connector.git && cd open-connector
docker compose up --build
# Gateway at http://localhost:3000, MCP at http://localhost:3000/mcp
```

**Cloudflare Workers** (production/personal, free tier):
1. `npx wrangler login`
2. Create D1 database + R2 bucket via Wrangler
3. Copy `wrangler.example.jsonc` → `wrangler.local.jsonc`, fill in `database_id`
4. Apply migrations: `npx wrangler d1 migrations apply open-connector --remote --config wrangler.local.jsonc`
5. Set secrets: `OOMOL_CONNECT_ADMIN_TOKEN` + `OOMOL_CONNECT_ENCRYPTION_KEY`
6. Deploy: `npm run deploy:cloudflare`

## Claude Code Integration

Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "open-connector": {
      "type": "http",
      "url": "https://open-connector.yourname.workers.dev/mcp",
      "headers": { "Authorization": "Bearer oct_your_runtime_token" }
    }
  }
}
```

## What the Agent Can Do

Once connected:
- Search GitHub repos by stars, topic, language
- Fetch HackerNews top stories (no auth needed)
- Query Twitter account info and recent posts
- Search Zhihu questions and answers
- List and manage Cloudflare Workers, D1, R2 resources

The MCP server exposes four meta-tools: `list_apps`, `search_actions`, `get_action_guide`, `execute_action` — Claude orchestrates them automatically based on your natural-language request.

## Combining With craft-agents-oss

Add open-connector as an MCP server in your craft-agent config. The entire 9,400+ Action catalog becomes the agent's tool set — no custom connectors needed per service.

**Links**: [open-connector repo](https://github.com/oomol-lab/open-connector) · [Cloudflare deploy video](https://www.youtube.com/watch?v=R0V1ZdCuTgc) · [craft-agents-oss](https://github.com/craft-ai-agents/craft-agents-oss)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
