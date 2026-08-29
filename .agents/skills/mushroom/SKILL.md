---
name: mushroom
description: |
  Mushroom 博客信息服务的瘦客户端：默认（裸调用 "mushroom"）汇报最近发布的
  几个主题；`mushroom search <关键词>` 用关键词+语义两路搜索历史文章并合并
  结果。底层直接调已经部署上线的 blog.mushroom.cv 的 Agent Feed
  （/api/mcp JSON-RPC + /api/search 语义检索），不重复实现搜索/索引逻辑——
  详见 blog/agent-feed/PLAN.md。

  Trigger when the user says: mushroom, 打mushroom, mushroom search,
  博客有什么新的, 汇报今天的主题, mushroom 汇报, mushroom 搜索。
---

# mushroom

## Mission

把 blog.mushroom.cv 已经对外提供的 agent 接口，包装成一句话触发的信息服务，
不需要用户自己记 curl 命令或者 JSON-RPC 格式。

## 前提

不需要本地跑任何服务——直接对公网已部署的 `https://blog.mushroom.cv` 发请求。
唯一依赖网络可达；接口失败时按下面「降级」处理，不要假装成功。

## 默认行为：裸触发 "mushroom"

调用 `list_recent`（最近发布的文章，默认 5 篇），汇报标题 + 一句话描述 + 链接：

```bash
curl -s -X POST https://blog.mushroom.cv/api/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_recent","arguments":{"limit":5}}}'
```

响应是 JSON-RPC，实际结果在 `result.content[0].text`（一段 JSON 字符串，解析后是
`{results: [...]}`，每条含 `title`/`description`/`url`/`pubDate`/`tags`/`category`）。
把它转成给人看的中文摘要，链接前缀是 `https://blog.mushroom.cv` + 返回的 `url`。

## `mushroom search <query>`

用户给了具体关键词时，两路都查，合并去重（按 `id`/`article_id`）后呈现：

**关键词/标签路**（覆盖标题、摘要、标签、正文全文匹配）：

```bash
curl -s -X POST https://blog.mushroom.cv/api/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_posts","arguments":{"query":"<query>","limit":10}}}'
```

**语义检索路**（bge-m3 embedding + Vectorize 余弦相似度，能匹配"意思相近但没有
共同关键词"的文章，是这个博客本来就对外公开的 `/api/search`，跟 mushroom skill
共用同一套后端）：

```bash
curl -s -X POST https://blog.mushroom.cv/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"<query>"}'
```

两路结果字段不完全一致（`search_posts` 返回 `id`+完整 tags/category，
`/api/search` 返回 `article_id`+`excerpt`+`score`）——合并时以标题/URL 判重，
展示时优先用语义检索路的 `excerpt`（更贴近查询语境），关键词路补充
tags/category 这类语义检索没有的结构化字段。

## 获取单篇全文

有了 `id` 之后，需要完整正文（比如用户要"详细讲讲那篇"）：

```bash
curl -s -X POST https://blog.mushroom.cv/api/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_post","arguments":{"id":"<id>"}}}'
```

`result.content[0].text` 解析后的 `bodyMarkdown` 字段是完整正文 markdown。

## 降级

- 请求失败/超时/非 2xx：直接告诉用户"博客服务暂时连不上"，不要编造结果。
- `tools/call` 的 JSON-RPC 响应里如果是 `error` 字段而不是 `result`（比如被限速
  429、参数错误 -32602），照实说明，不要静默重试刷限速。
- `/api/search` 偶尔会因为向量检索阈值过滤掉所有结果而返回空数组——这不算错误，
  说明关键词路可能有结果、语义路没有，正常呈现即可。

## 进阶：注册成原生 MCP 工具（可选，不是这个 skill 运行的前提）

想要 `tools/call` 变成 Claude Code 里的原生工具调用（而不是这个 skill 内部拼
curl），可以直接把这个 MCP server 注册为远程连接：

```bash
claude mcp add --transport http mushroom-blog https://blog.mushroom.cv/api/mcp
```

注册后 `search_posts`/`get_post`/`list_recent` 会以 `mcp__mushroom-blog__*` 的
形式出现，这个 skill 的 curl 版本依然可以用（两者不冲突，一个是零配置的兜底
路径，一个是配置后更原生的路径）。
