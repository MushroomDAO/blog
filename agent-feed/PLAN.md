# Agent Feed — 设计记录

## 为什么做这个

2026-08-29 跟站长讨论：未来专业/高频的信息获取会更多发生在 agent 对 agent 之间，
不是人去点开网站。博客之前只优化了给人看的体验（SEO、排版、社交分享、Pagefind/
语义搜索），没有对"agent 主动来对接"这件事做任何设计。

目标不是"让爬虫更好抓"（llms.txt 这类静态文件实测对 AI 引用率没有提升，见下方
调研依据），而是：站长自己的个人 agent，只要拿到博客的域名/URL，就应该能发现博客
提供什么能力、主动查询、订阅更新——不用轮询爬取整站再自己解析。

## 三层架构

| 层 | 解决什么 | 用什么 | 落地文件 |
|---|---|---|---|
| 发现 | agent 怎么知道博客存在、能干什么 | A2A Agent Card + llms.txt 兜底 | `src/pages/.well-known/agent-card.json.ts`、`src/pages/llms.txt.ts`、`src/pages/llms-full.txt.ts` |
| 交互 | agent 怎么主动查询/提问 | MCP server（`tools/call`） | `functions/api/mcp.js`、`functions/_lib/mcp.js` |
| 订阅 | agent 怎么被动收到更新，不用轮询爬取整站 | MCP `resources/subscribe`，无状态轮询式推送 | `functions/api/mcp.js` 的 `onRequestGet`（SSE） |

### 为什么是 A2A + MCP，不是 Nostr / ActivityPub

- **Nostr relay 广播**：生态里 iDoris 已经有 `agent-speaker-relay`（strfry Docker），
  但接入意味着跨仓库依赖，站长已明确这个放二期，先把博客自己这部分做扎实。
- **ActivityPub Follow 模型**：更适合人类可读的联邦社交场景（Mastodon 式关注/收件箱），
  跟"agent 直接对接查询/订阅"这个目标不完全对齐，暂不做。
- **A2A（Agent2Agent 协议）**：Google 发起，2026-03 发布 v1.0，已转交 Linux Foundation
  治理，150+ 组织支持，Google/Microsoft/AWS 都已集成。Agent Card 在
  `/.well-known/agent-card.json`，agent 只要知道域名就能自动发现能力——正是
  "填个网址就能对接"这个诉求的标准化落地。
- **MCP 自带订阅能力**：`resources/subscribe` + `notifications/resources/updated`
  已经能覆盖"被动收到更新"这个诉求，不需要再叠加别的推送协议。

### 协议版本：为什么声明 2025-11-25，不是最新的 2026-07-28

第一版上线前 Codex review 抓到一个真实的协议错误：代码声明支持 `2026-07-28`，
但实现的是 `initialize` 握手 + `resources/subscribe` + 独立 GET SSE 流这一套
方法——`2026-07-28` 恰恰把这几样全部替换掉了（`initialize`/`initialized`
握手整个去掉，改成每个请求在 `_meta` 里带协议版本/能力做无状态协商；新增
`server/discover` 作为能力发现入口；`resources/subscribe` 被
`subscriptions/listen` 取代，见
[MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)）。
自己声明的版本号和自己实际实现的方法集对不上，比"版本旧"本身更糟。

选择：老老实实声明 `2025-11-25`——这是 `initialize` + `resources/subscribe`
这套方法集最后一个仍然有效的版本号。额外加了一个 `server/discover` 方法（成本
几乎为零，纯静态返回），让 2026-07-28 感知的新客户端至少能拿到一个诚实的
"我是 2025-11-25"回答，不是 `-32601 method not found`。

要不要追到 `2026-07-28` 的无状态语义（`_meta` 协商 + `subscriptions/listen`
长连接流）取决于这个 server 实际服务的客户端要不要求它——目前的主要使用路径
是 `.agents/skills/mushroom/` 这个 curl 直连的瘦客户端，根本不走 MCP 握手，
协议版本正确性目前只影响"有没有人真的把这个 server 注册成原生 MCP 连接"这个
场景。等出现一个要求 2026-07-28 语义的真实客户端再升级，不提前对着假想需求做。

### A2A Agent Card：v1.0 结构 + 诚实标注这不是 A2A 端点

同一轮 review 还抓到 Agent Card 结构错了——v1.0 把顶层的 `protocolVersion`/
`url`/`preferredTransport` 挪进了 `supportedInterfaces` 数组，还加了
`capabilities.extendedAgentCard`/`signatures` 字段（见
[A2A v1.0 changes](https://a2a-protocol.org/latest/whats-new-v1/)）。更根本的
问题：卡片指向的 `/api/mcp` 说的是 MCP JSON-RPC 方法集，不是 A2A 自己的
`message/send`/`tasks/get` 这些方法——如果 `protocolBinding` 写 `"JSONRPC"`，
等于告诉严格的 A2A 客户端"这里能发 A2A 请求"，实际发过去只会拿到
method not found。

选择：`protocolBinding` 用 MCP 规范的 URL（`https://modelcontextprotocol.io/
specification/2025-11-25`）而不是 `"JSONRPC"`——A2A v1.0 的 `protocolBinding`
本来就设计成可以是自定义 URI，这正是用来诚实标注"这个接口说的是另一种协议"
的扩展点。这个 Agent Card 目前只承担"发现"这一层的职责（域名 → 能力清单），
不承诺这个域名上有一个真正的 A2A 端点。

## `agent-feed-index.json` 字段契约

`src/lib/agent-feed-index.ts` 的 `buildAgentFeedIndex()` 是三个下游产物
（`agent-feed-index.json` / `llms.txt` / `llms-full.txt`）和 MCP server 共用的
唯一数据源，字段：

```
{
  id: string              // 对应 astro:content 的 post.id，也是 get_post 工具的入参
  title: string
  titleEn?: string
  description: string
  descriptionEn?: string
  pubDate: string         // ISO 8601
  updatedDate?: string    // ISO 8601
  tags: string[]
  category: string
  url: string              // 站内相对路径，如 /blog/xxx/
  bodyMarkdown: string      // 原始 markdown 正文（content collection entry.body，
                            // 不是渲染后的 HTML——llms.txt 惯例本来就要干净的 markdown）
}
```

新增/改名字段时，`functions/_lib/mcp.js` 的 `search_posts`/`get_post`/`list_recent`
和三个 Astro 端点都要跟着改——目前没有做 schema 校验，字段形状由这份契约手动维护。

## `agent-feed-meta.json`：SSE 轮询专用的轻量端点

`src/pages/agent-feed-meta.json.ts` 跟 `agent-feed-index.json` 同一份数据源，
但只输出 `{ count, latestPubDate, revision }` 几十字节。`functions/api/mcp.js`
的 SSE 循环轮询这个端点而不是完整索引——第一版每 20s 重新 fetch+parse 一次约
7.7MB 的完整索引，单连接 25 次轮询就是约 200MB 的重复解码，是 Codex review 抓到
的资源放大问题。`revision` 是全部文章 `id:updatedDate|pubDate` 拼接后的
sha256，不是只看最大 `pubDate`——只比最大发布日期会漏掉"同一天发第二篇"和
"文章内容/`updatedDate` 变了但 `pubDate` 没变"这两种真实会发生的更新。

## 已知边界（本期不做，记在这里防止以后重新纠结）

- **A2A Agent Card 没有 JWS 签名**（RFC 7515/8785 域名验证）。那是企业级场景的
  信任要求，个人博客先不做；如果以后有 agent 需要验证这个 Card 确实来自
  `blog.mushroom.cv`，再补。
- **`search_posts` 用关键词匹配，不是语义检索**。`/api/search` 已经有基于 bge-m3 +
  Vectorize 的语义搜索能力，但那条链路调用计费的 Workers AI/Vectorize——先用零依赖
  的关键词匹配跑起来，真的不够用再考虑复用 `/api/search` 的向量检索。
- **SSE 订阅是"无状态轮询式推送"，不是真正的实时 push**。每 20s 重新同源 fetch
  一次 `agent-feed-meta.json` 比较 revision，单个连接有执行时长上限（约
  500s），客户端要自己处理断线重连。这是 MCP 生态目前对 serverless/边缘场景的
  推荐做法（Cloudflare Workers 上维护跨请求状态得上 Durable Objects，复杂度和
  这个博客的实际订阅量完全不匹配）。如果以后订阅量大到轮询延迟不可接受，再考虑
  Durable Objects 或接入 Nostr relay 做真正的事件广播。
- **`tools/call`/`resources/read` 每次都拉完整 ~7.7MB 索引再在内存里过滤**。
  SSE 轮询和"不需要文章内容的方法"已经不再碰这份索引（round 1 review 修复），
  但真正需要搜索/读文章的请求仍然要拉全量——语料规模再大几倍之前不是问题，
  真的成为瓶颈时再考虑拆分成小索引 + 按需拉正文，或者接入 Vectorize。
- **KV 计数器不是原子的**（`functions/_lib/rate-limit.js` 的已知局限，
  `agentfeed:`/`agentfeedsse:` 前缀复用的是同一套实现）。并发请求可能一起读到
  同一个计数、一起判定"还没到上限"，导致实际放行量比名义上限宽松；分布式多
  IP 也绕得过去。跟登录/搜索限速用的是同一个可接受的风险模型——真的需要更强
  的限速时应该换 Cloudflare Rate Limiting binding 或 Durable Object，不是这个
  子系统单独去重做一遍。
