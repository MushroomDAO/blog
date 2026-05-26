---
title: "FastMCP：用几十行 TypeScript 搭 MCP 服务器，5 个月 3000+ star"
titleEn: "FastMCP: Build MCP Servers in Dozens of Lines of TypeScript, 3K Stars in 5 Months"
description: "FastMCP 是 TypeScript 版 MCP 服务器框架，内置 Session 管理、OAuth 认证、Edge Runtime 支持和 CLI 调试工具，比官方 SDK 省去大量样板代码。5 个月获 3145 star，周均下载 46 万次。"
descriptionEn: "FastMCP is a TypeScript MCP server framework with built-in session management, OAuth, edge runtime support, and CLI tooling that eliminates boilerplate from the official SDK. 3,145 stars and 464K weekly downloads in just 5 months."
pubDate: "2026-05-26"
updatedDate: "2026-05-26"
category: "Tech-News"
tags: ["MCP", "TypeScript", "开源", "FastMCP", "Cloudflare Workers", "AI工具", "开发者工具"]
heroImage: "../../assets/banner-future-is-now.jpg"
---

官方 MCP SDK 给了砖块，FastMCP 直接给了楼。5 个月时间，3145 个 star，每周 46 万次下载——这个 TypeScript MCP 服务器框架正在成为开发者的默认选择。

> 📌 代码仓库：https://github.com/punkpeye/fastmcp  
> npm 包：fastmcp（npm install fastmcp）  
> 作者：Frank Fiegel（punkpeye）

## 为什么需要 FastMCP？

官方 MCP SDK 提供了协议层的基础构件，但把大量实现细节留给开发者自己处理：连接管理、Session 初始化、工具/资源/提示词的协议封装、错误规范、认证……

FastMCP 把这些全部封装掉，用一套固执己见（opinionated）的抽象让你专注于业务逻辑。

最简单的工具服务器长这样：

```typescript
import { FastMCP } from "fastmcp";
import { z } from "zod";

const server = new FastMCP({
  name: "My Server",
  version: "1.0.0",
});

server.addTool({
  name: "add",
  description: "Add two numbers",
  parameters: z.object({
    a: z.number(),
    b: z.number(),
  }),
  execute: async (args) => {
    return String(args.a + args.b);
  },
});

server.start({ transportType: "stdio" });
```

官方 SDK 实现同样功能，大概需要三倍的代码量。

## 核心特性一览

### Session 管理

FastMCP 自动为每个客户端创建独立 Session，通过 `Mcp-Session-Id` 头追踪会话状态。工具函数可以通过 `context.sessionId` 直接访问，无需手动维护映射表。

```typescript
execute: async (args, context) => {
  const counter = sessionCounters.get(context.sessionId) || 0;
  sessionCounters.set(context.sessionId, counter + 1);
  return `Session ${context.sessionId} counter: ${counter + 1}`;
},
```

### 零配置 OAuth

内置 OAuth 2.1 支持，Google Provider 预置好了。

```typescript
import { FastMCP, GoogleProvider } from "fastmcp";

const server = new FastMCP({
  auth: new GoogleProvider({
    baseUrl: "https://your-server.com",
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  }),
  name: "My Server",
  version: "1.0.0",
});
```

### Edge Runtime：Cloudflare Workers 原生支持

`EdgeFastMCP` 类专为 V8 隔离环境设计，无状态，可水平扩展，直接部署到 Cloudflare Workers 或 Deno Deploy：

```typescript
import { EdgeFastMCP } from "fastmcp/edge";
const server = new EdgeFastMCP({ name: "Edge Server", version: "1.0.0" });
```

### 自定义 HTTP 路由

在同一个进程里同时跑 MCP 协议 + REST API，不需要另起服务：

```typescript
server.addRoute("GET", "/api/users/:id", async (req, res) => {
  res.json({ userId: req.params.id });
});

server.addRoute("POST", "/webhook/github", async (req, res) => {
  const payload = await req.json();
  res.json({ received: true });
});
```

### 进度报告与用户友好错误

```typescript
execute: async (args, { reportProgress }) => {
  await reportProgress({ progress: 0, total: 100 });
  // ... 处理工作 ...
  await reportProgress({ progress: 100, total: 100 });
  return "done";
},
```

`UserError` 类让你返回对用户可读的错误信息，而不是把 stack trace 暴露给 LLM 客户端。

### Schema 无关

支持 Zod、ArkType、Valibot——任何兼容 Standard Schema 规范的验证库都可以直接用，不锁定生态。

### CLI 调试工具

```bash
fastmcp dev    # 实时调试服务器
fastmcp inspect  # 集成 MCP Inspector
```

## 数据

5 个月（2024 年 12 月至今）：
- GitHub Stars：3,145
- Forks：271
- 贡献者：30+
- npm 周均下载：464,457 次
- 展示项目：11 个社区项目

11 个展示项目覆盖了媒体生成（Midjourney/Flux）、电脑控制自动化、会议记录搜索、Unsplash 图片集成、macOS Shortcuts 自动化等场景——说明 FastMCP 的应用范围已经从玩具项目延伸到了生产用途。

## 与官方 SDK 对比

| 维度 | 官方 SDK | FastMCP |
|------|----------|---------|
| 启动样板代码 | 多 | 极少 |
| Session 管理 | 手动 | 自动 |
| OAuth 认证 | 需自行实现 | 内置 |
| 自定义 HTTP 路由 | 不含 | 完整支持 |
| Edge Runtime | 不支持 | 原生支持 |
| CLI 调试工具 | 无 | 内置 |
| TypeScript 类型安全 | 基础 | 完整 |

FastMCP 基于官方 SDK 构建（`@modelcontextprotocol/sdk` 是其直接依赖），不是替代品，是封装层。使用 FastMCP 不意味着放弃底层控制——遇到特殊需求时仍然可以穿透到 SDK 层。

## 有意思的细节

FastMCP TypeScript 版本是受到 Python 版 FastMCP（Jonathan Lowin 实现）启发而来的社区移植。Python 版后来因为用于出色的 MCP 生态贡献被 Anthropic 收购并整合进官方 SDK——TypeScript 版走的是类似但独立的路线。

HTTP Streaming 模式被定位为 SSE 的更高效替代，对大 payload 有潜在性能优势，同时可以在同一端口运行两种传输方式以保证最大兼容性。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

The official MCP SDK gives you bricks. FastMCP gives you a building. In five months: 3,145 stars and 464K weekly npm downloads — this TypeScript MCP server framework is becoming the developer default.

> 📌 Repository: https://github.com/punkpeye/fastmcp  
> npm: fastmcp (npm install fastmcp)  
> Author: Frank Fiegel (punkpeye)

## Why FastMCP?

The official MCP SDK provides the protocol-level building blocks but leaves most implementation details to developers: connection management, session initialization, tool/resource/prompt protocol wrapping, error handling, authentication...

FastMCP encapsulates all of this with an opinionated abstraction layer that lets you focus on business logic.

The minimal tool server looks like this:

```typescript
import { FastMCP } from "fastmcp";
import { z } from "zod";

const server = new FastMCP({ name: "My Server", version: "1.0.0" });

server.addTool({
  name: "add",
  description: "Add two numbers",
  parameters: z.object({ a: z.number(), b: z.number() }),
  execute: async (args) => String(args.a + args.b),
});

server.start({ transportType: "stdio" });
```

Achieving the same with the official SDK takes roughly three times more code.

## Key Features

### Automatic Session Management

FastMCP creates isolated sessions per client automatically, tracked via `Mcp-Session-Id` headers. Tools access `context.sessionId` directly — no manual mapping tables needed.

### Zero-Config OAuth

Built-in OAuth 2.1 with a pre-configured Google provider. Pass credentials, done.

### Edge Runtime: Native Cloudflare Workers Support

The `EdgeFastMCP` class is designed for V8 isolates — stateless, horizontally scalable, deployable to Cloudflare Workers or Deno Deploy with no adaptation.

### Custom HTTP Routes

Run MCP protocol and REST API in the same process, no separate service needed:

```typescript
server.addRoute("GET", "/api/users/:id", async (req, res) => {
  res.json({ userId: req.params.id });
});
```

### Schema Agnostic

Works with Zod, ArkType, Valibot, or any Standard Schema-compatible validation library — no ecosystem lock-in.

### Built-In CLI Tooling

```bash
fastmcp dev      # Live debug server
fastmcp inspect  # MCP Inspector integration
```

## Numbers

Five months (December 2024 to now):
- GitHub Stars: 3,145
- Forks: 271
- Contributors: 30+
- npm weekly downloads: 464,457
- Showcase projects: 11

The 11 showcase projects span media generation (Midjourney/Flux), computer control automation, meeting transcript search, Unsplash photo integration, and macOS Shortcuts automation — showing FastMCP has moved from toy projects to production use cases.

## Comparison: FastMCP vs. Official SDK

| Aspect | Official SDK | FastMCP |
|--------|--------------|---------|
| Startup boilerplate | Significant | Minimal |
| Session management | Manual | Automatic |
| OAuth | Self-implemented | Built-in |
| Custom HTTP routes | Not included | Full support |
| Edge runtime | No | Native |
| CLI dev tools | None | Built-in |
| TypeScript type safety | Basic | Full |

FastMCP builds on top of the official SDK (`@modelcontextprotocol/sdk` is a direct dependency) — it's an abstraction layer, not a replacement. Dropping down to the SDK level for unusual requirements is still possible.

## A Noteworthy Detail

The TypeScript version of FastMCP was inspired by the Python FastMCP implementation by Jonathan Lowin. The Python version was later acquired by Anthropic and integrated into the official Python SDK for its contributions to the MCP ecosystem. The TypeScript version follows an independent but parallel trajectory.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
