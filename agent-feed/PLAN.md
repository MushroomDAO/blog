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
| 发现 | agent 怎么知道博客存在、能干什么 | `llms.txt` | `src/pages/llms.txt.ts`、`src/pages/llms-full.txt.ts` |
| 交互 | agent 怎么主动查询/提问 | MCP server（`tools/call`） | `functions/api/mcp.js`、`functions/_lib/mcp.js` |
| 订阅 | agent 怎么被动收到更新，不用轮询爬取整站 | 按固定资源 URI 轮询式推送（不是标准 MCP session 订阅，见下方"已知边界"） | `functions/api/mcp.js` 的 `onRequestGet`（SSE） |

原计划里发现层是 A2A Agent Card + llms.txt 双保险，第一版也确实上线过一个
Agent Card。两轮 Codex review 都判定那张卡片结构性有问题（见下面"A2A Agent
Card：为什么整个撤下"），已经删除——发现层目前只剩 `llms.txt`。

### 为什么是 MCP，不是 Nostr / ActivityPub

- **Nostr relay 广播**：生态里 iDoris 已经有 `agent-speaker-relay`（strfry Docker），
  但接入意味着跨仓库依赖，站长已明确这个放二期，先把博客自己这部分做扎实。
- **ActivityPub Follow 模型**：更适合人类可读的联邦社交场景（Mastodon 式关注/收件箱），
  跟"agent 直接对接查询/订阅"这个目标不完全对齐，暂不做。
- **MCP**：Claude Code 等主流 agent 工具本来就是 MCP 客户端生态，`tools/call` +
  `resources/subscribe` 这套方法集覆盖"查询"和"被动收到更新"两个诉求，不需要
  再叠加别的协议。

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
这套方法集最后一个仍然有效的版本号。

第一版还加了一个 `server/discover` 方法，想给 2026-07-28 感知的新客户端一个
更友好的探测结果——第二轮 review 指出这个方法本身的返回形状（`resultType`
包装、`supportedVersions` 字段名等）跟真正的 2026-07-28 discovery schema也对不上，
等于用"看起来支持新协议但形状错了"替换掉了一个诚实的 `-32601`。2026-07-28
changelog 原文写的是 `server/discover` 给客户端 "MAY... use it as a
backward-compatibility probe"——也就是说规范本身预期客户端会处理探测失败、
回退到 `initialize`，`-32601` 就是这条回退路径设计上会遇到的信号，不是要修的
问题。于是把这个方法整个删掉了，只诚实实现 2025-11-25 这一套，不做半吊子的
2026-07-28 兼容。

要不要追到 `2026-07-28` 的无状态语义（`_meta` 协商 + `subscriptions/listen`
长连接流）取决于这个 server 实际服务的客户端要不要求它——目前的主要使用路径
是 `.agents/skills/mushroom/` 这个 curl 直连的瘦客户端，根本不走 MCP 握手，
协议版本正确性目前只影响"有没有人真的把这个 server 注册成原生 MCP 连接"这个
场景。等出现一个要求 2026-07-28 语义的真实客户端再升级，不提前对着假想需求做。

### A2A Agent Card：为什么整个撤下

第一版上线过一张 `/.well-known/agent-card.json`，两轮 Codex review 都判定
结构有问题：

- **第一轮**：用的是已经在 A2A v1.0 里移除的顶层 `protocolVersion`/`url`/
  `preferredTransport` 字段，没有 v1.0 要求的 `supportedInterfaces` 数组/
  `capabilities.extendedAgentCard`/`signatures`（见
  [A2A v1.0 changes](https://a2a-protocol.org/latest/whats-new-v1/)）。当时的
  修法是把 `protocolBinding` 改成 MCP 规范的 URL 而不是 `"JSONRPC"`，想借
  A2A 允许自定义 binding URI 这个扩展点诚实标注"这个接口说的是另一种协议"。
- **第二轮**：这个修法仍然不成立——A2A v1.0 规范要求即便走自定义 binding，
  这个 URL 背后仍然要实现 A2A 自己的核心操作/数据模型，自定义 binding 不是
  用来指向一个完全不相关的 API 的机制；另外还缺 `version`/
  `defaultInputModes`/`defaultOutputModes` 这几个必填字段，`protocolVersion`
  填的应该是 A2A 自己的版本号（`"1.0"`），不是 MCP 的日期字符串。

两轮都栽在同一个根子上：这个域名上根本没有一个真正的 A2A 端点（`/api/mcp`
说的是 MCP 方法集，不是 A2A 的 `message/send`/`tasks/get`），试图用一张
"看起来合规"的卡片去描述一个不存在的能力，怎么修字段形状都绕不开这个矛盾。

选择：把这个文件整个删掉，不留一张确认有问题的卡片在 `.well-known/` 这个
A2A 保留路径上（放在那儿会被真正的 A2A 爬虫当成权威声明去解析，比 404 更
误导人）。要重新做，前提是先有一个真正实现 A2A 方法集的端点，不是给 MCP
端点包一层假装是 A2A 的皮——这是一个独立的、之后再说的任务，不是这次的
"基础版本"该做的事。

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
的资源放大问题。`revision` 是每篇文章 `id:updatedDate:title:description:
bodyMarkdown` 拼接后的 sha256——不只看最大 `pubDate`（漏"同一天发第二篇"），
也不只看 `updatedDate`（第二轮 review 指出：改了正文但忘了手动把 updatedDate
往前挪，revision 就不会变——这个字段有没有被诚实更新取决于写作流程，不是这里
能保证的不变量），而是把标题/摘要/正文也一起哈希进去，内容变了 revision 就
一定会变，不依赖任何人手动维护一个"我改过"的标记字段。

## 已知边界（本期不做，记在这里防止以后重新纠结）

- **`resources/subscribe` 不是真正的 session 绑定订阅**。标准 MCP 传输规范里，
  客户端调用 `resources/subscribe` 之后，应该在自己已有的连接/session 上收到
  后续的 `notifications/resources/updated`。这个 server 是完全无状态的，
  `resources/subscribe`（JSON-RPC 调用）和 GET SSE 流（`functions/api/mcp.js`
  的 `onRequestGet`）之间没有任何服务端状态把两者关联起来——两者只是约定好
  用同一个资源 URI，`resources/subscribe` 实际上只确认了"这个 uri 存在"，
  真正的推送要靠单独发起那个带 `?subscribe=posts://latest` 的 GET 请求。
  诚实的定位是"一个按固定 URI 轮询式推送的端点"，不是标准语义下的订阅——第二轮
  review 明确指出了这点。要做成真正 session 绑定的订阅需要 Durable Objects
  维护每个客户端的订阅表，跟下面 SSE 本身"无状态轮询"的设计选择是同一类
  取舍，一起留到订阅量真的大到需要时再做。
- **A2A Agent Card 已撤下**，不是没做 JWS 签名这么简单——见上面"A2A Agent
  Card：为什么整个撤下"，两轮 review 都判定结构性有问题，需要先有真正的 A2A
  端点才值得重做。
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
  SSE 轮询和"不需要文章内容的方法"已经不再碰这份索引，未知工具名/`get_post`
  缺 `id` 这类静态就能判定无效的请求也已经改成在拉索引之前拒绝（第二轮
  review 指出的问题：原来会先花一次 fetch+parse 去驳回一个本来不用看内容就能
  驳回的请求）。但真正需要搜索/读文章的请求仍然要拉全量——语料规模再大几倍
  之前不是问题，真的成为瓶颈时再考虑拆分成小索引 + 按需拉正文，或者接入
  Vectorize。
- **KV 计数器不是原子的**（`functions/_lib/rate-limit.js` 的已知局限，
  `agentfeed:`/`agentfeedsse:` 前缀复用的是同一套实现）。并发请求可能一起读到
  同一个计数、一起判定"还没到上限"，导致实际放行量比名义上限宽松；分布式多
  IP 也绕得过去。跟登录/搜索限速用的是同一个可接受的风险模型——真的需要更强
  的限速时应该换 Cloudflare Rate Limiting binding 或 Durable Object，不是这个
  子系统单独去重做一遍。KV 本身故障时 `checkAndIncrement` 也会返回跟"超过限速"
  一样的 `{allowed:false}`（`rate-limit.js` 的既有设计，不是这次新增的行为），
  所以 KV 故障目前会表现成 429 而不是更准确的 503——同样是复用现有共享库的
  既定契约，不在这个子系统里单独改。
- **没有做 Origin 校验**。MCP Streamable HTTP 规范建议校验请求的 Origin 防
  DNS rebinding 类攻击，但那个威胁模型主要针对本机监听的 MCP server（恶意网页
  JS 绕过浏览器同源策略打本地服务）。这个 server 故意设计成公开、无认证、
  任何来源都能调用（跟 `/api/search` 同样的设计），加 Origin 白名单反而会
  违背"任何地方的 agent 都能连"这个目标，所以不做。
- **不校验请求方是否声明了正确的 `Content-Type` charset / 不区分请求体读取
  失败的具体原因**（读取失败、非法编码、体积超限三者除了体积超限外统一按
  400 处理）。这是为了让错误处理保持简单，公开只读端点没有必要为这些边角
  情况精确分类。
