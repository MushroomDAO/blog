# 语义检索 / 智能推荐功能 规格 — 落地细节

> 精确到能照着建表/实现。架构与边界见 `architecture.md`。
> 记录日期：2026-08-20

## 产品定义

用户在博客搜索入口输入一段自然语言诉求或关键词，系统返回若干篇相关文章，每篇附命中片段/理由，
帮助读者判断这篇文章能否解决自己的问题。核心用例：技术名词查找、"我想做 xxx 该怎么入手"式的
自然语言诉求、中英文/跨语言查询。

## 数据模型

### 文章搜索文档（构建期产出，Phase 0A 起）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `article_id` | string | = 文章 slug，全局唯一，稳定不变（改名需当作新 article_id 处理） |
| `title` / `titleEn` | string | 来自 frontmatter |
| `description` / `descriptionEn` | string | 来自 frontmatter |
| `tags` | string[] | 来自 frontmatter |
| `category` | enum | 来自 frontmatter（Tech-Experiment / Progress-Report / Research / Tech-News / Other） |
| `language` | `zh` \| `en` \| `bilingual` | 单文件中文+`<!--EN-->`+英文的文章标记为 `bilingual`，
  检索时按 §双语处理拆分成两条独立记录 |
| `url` | string | 文章发布后的完整路径 |
| `headings` | string[] | 正文标题层级（h2/h3），供 Pagefind 展示与后续分片参考 |
| `content_hash` | string | 正文内容 hash，用于判断是否需要重新索引 |

### Vectorize 向量条目（Phase 1 起）

| 字段 | 说明 |
|:---|:---|
| `chunk_id` | `sha256(article_id:language:chunk_hash)` 取前 48 位十六进制，确定性、支撑幂等
  upsert/delete。**订正（T1.3.1 真实执行发现）**：Vectorize v2 的 vector id 有 64 字节硬
  上限，直接拼接 `article_id:language:chunk_hash` 对长 slug 文章会超限（实测出现 71 字节
  被拒），改成对完整逻辑 key 取哈希，长度恒定 48 字节；`article_id`/`language`/`content_hash`
  三个原始字段完整保留在下面的 metadata 里，不影响可读性/可追溯性，只是 id 本身不再是
  人可读的拼接字符串 |
| `article_id` | 关联到文章搜索文档 |
| `language` | `zh` \| `en`（bilingual 文章拆成两条，此处不再有 `bilingual` 值） |
| `chunk_type` | `article`（标题+摘要+标签+标题层级） \| `paragraph`（正文片段） |
| vector | `bge-m3` embedding，1024 维 |
| metadata | 仅存 `article_id`/`url`/`title`/`language`/`excerpt`（片段摘录，非全文）/`tags`/`content_hash`，
  不超过 10KiB |

### 索引 manifest（Phase 1 起）

| 字段 | 说明 |
|:---|:---|
| `embedding_model` | 如 `@cf/baai/bge-m3` |
| `embedding_dimensions` | 1024 |
| `chunking_version` | 分片算法版本号，变更时递增并建新索引 |
| `indexed_at` | 最近索引时间 |
| 每篇文章的 `content_hash` | 用于增量对账，判断是否需要重新索引 |

### 登录会话（Phase 1 起，T1.3.6）

**认证范围（回应 review #38 B7；2026-08-23 PR #61 起已变，见下）**：密码门禁原本只挡"语义检索
能力"——即 `/api/search` 及其向量/融合结果；T1.1.3 已上线的纯 Pagefind 关键词搜索页面（零成本、
无需登录）保持公开。**PR #61 起 `/api/search` 也已取消登录门禁、和关键词搜索一样公开**——刷额度
的顾虑改由 per-IP 限速（30 req/5min）承担，不再靠密码挡；本节下面记录的登录会话机制本身
未删（`_lib/auth.js`/`api/search-auth.js` 仍在），改为挂在 `/api/search-analytics` 用量统计和
未来的 AI 对话功能上，见 `architecture.md` 核心判断 7 的"更新"段落。

| 字段 | 说明 |
|:---|:---|
| `BLOG_SEARCH_PASSWORD` | Worker Secret，单一共享密码，常量时间比较，不落日志 |
| `BLOG_SEARCH_SESSION_SECRET` | Worker Secret，用于 HMAC-SHA256 签名登录 Cookie |
| Cookie payload | `{v, issuedAt, expiresAt}`（`v` 是格式版本号，日后改 payload 结构不需要连带轮换密钥），
  签名后拼成 `<base64url payload>.<base64url hmac>`（用 base64url 而非普通 base64，避免
  `+`/`/`/`=` 出现在 Cookie value 里） |
| Cookie 属性 | `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=<30-90 天>`（缩短有效期而非 1 年——
  这个模型下没有按会话吊销的机制，只能靠轮换 `BLOG_SEARCH_SESSION_SECRET` 让全部 Cookie
  一次性失效，缩短有效期降低泄露窗口；**必须带 `Path=/`**，否则默认按请求路径设置，
  访问 `/search` 页面时不会带上这个 Cookie） |
| 登录限速 | 同 IP 15 分钟内最多 5 次 `/api/search-auth` 请求，KV 计数器（对分布式撞库偏弱，
  见 `followups.md` FU-6，当前威胁模型下可接受） |

两个 Secret 已生成并记录在 `~/Dev/.env`（`BLOG_SEARCH_PASSWORD`/`BLOG_SEARCH_SESSION_SECRET`），
尚未 `wrangler secret put` 推送到 Cloudflare——推送需用户确认（见 `architecture.md` 边界）。

### 检索融合（Phase 1 起，T1.3.3）

**融合发生在浏览器端，不在 Worker 里**（修正 review #38 B2）：Pagefind 是纯浏览器端 JS
（`dist/pagefind/pagefind.js` + `PagefindUI`），Cloudflare Worker 无法调用它，`/api/search`
不可能在服务端"并行跑 Pagefind"。正确形态：

1. `/search` 页面（浏览器）本地跑 Pagefind 关键词检索（不变，T1.1.3 已有逻辑），同时
   请求 `/api/search`（Worker，2026-08-23 PR #61 起公开，无需登录 Cookie，见
   `architecture.md` 核心判断 7 的"更新"段落）。
2. `/api/search` 只负责**向量这一路**：query → embedding → Vectorize top20 → 按
   `article_id` 聚合去重（每篇最多 1-2 片段）→ **先用向量自己的绝对信号过滤**
   （Vectorize 相似度低于阈值的候选直接丢弃，阈值用 `semantic-search/eval/queries.md`
   校准，不是凭感觉设数字）→ 返回过滤后的候选列表（可能为空）。
3. **融合发生在浏览器 JS 里**：把 Pagefind 本地结果（自带相关性分数/排名）与 `/api/search`
   返回的向量候选，按各自的**排名**做 RRF 融合——`score(doc) = Σ 1/(k + rank_i(doc))`，
   `k` 取常见默认值 60；某一路没命中该文档时，那一路对这篇文档的贡献项为 0（等价于
   `rank=∞`），不是"两路都命中才求和"（那等价于取交集，会把向量独有的召回也一起丢掉，
   正是要避免的错误）。
4. **无把握不返回，判断在融合之前、按各路自己的绝对信号，不是看 RRF 融合后的分数**
   （修正 review #38 B1——RRF 分数只编码排名和多路共识，不编码绝对相关度：向量把
   一篇真正跨语言/概念相关的文章排第一，和向量把一篇主题沾边但答非所问的文章排第一，
   RRF 算出来的分数完全相同，没法靠融合后的分数区分"该拒的负样本"和"该留的真命中"）。
   正确做法：Pagefind 和 Vectorize **各自**先按自己的绝对信号判断"这一路是否有靠谱结果"
   （Pagefind 自己的相关性分数/命中数、Vectorize 自己的余弦相似度下限），两路都判定为
   "没有靠谱结果"时才整体返回"没有找到"；只要有一路认为靠谱，就进入第 3 步的 RRF 排序——
   RRF 在这里只负责给幸存的候选排序，不负责决定要不要收录候选。
   这套判断对应的具体阈值同样用 `semantic-search/eval/queries.md`（含"菜谱""育儿"等负样本）
   校准，实现 T1.3.3 时定。

## 状态机

### 文章索引状态（Phase 1 起）

```
未索引 → 索引中 → 已索引 → （内容变更 content_hash 不一致）→ 待重新索引 → 索引中 → 已索引
                                                          ↘（文章删除/下线）→ 待清理 → 已清理
```

- 发布 hook 触发"索引中"；成功后转"已索引"并更新 manifest 的 `content_hash`。
- 每日 Cron 对账：manifest 记录的 `content_hash` 与文章实际 hash 不一致 → 标记"待重新索引"；
  manifest 里有、但文章已不存在 → 标记"待清理"（删除对应 chunk）。

## 错误处理 / 幂等

- **upsert 幂等**：`chunk_id` 是确定性的（`article_id:language:chunk_hash`），重复 upsert 同一
  `chunk_id` 只会覆盖，不会产生重复条目。
- **更新流程**（先记录旧再删）：更新一篇文章的索引时，先读出该 `article_id` 现有的全部
  `chunk_id` 列表，写入新版本 chunk 成功后，再删除不在新版本里的旧 `chunk_id`——避免中途失败导致
  新旧内容并存或全部丢失。
- **部分失败**：一批 chunk 里部分 upsert 失败 → 整批标记为"待重新索引"，下一次 Cron 对账重试，
  不做部分提交。
- **API 侧**：`/api/search` 请求超时或 Vectorize/Workers AI 调用失败 → 降级返回 Pagefind 的
  关键词检索结果，而不是直接报错给用户。
- **输入限制**：query 长度上限（如 300–500 字符），超出直接拒绝并提示。

## 测试策略

- **Phase 0A**：人工用评测查询集（`semantic-search/eval/queries.md`）跑一遍搜索页面，记录
  Recall@5 与失败案例到 `semantic-search/eval/baseline-results.md`。
- **Phase 0B**：离线脚本对比"纯关键词 / 纯向量 / 融合"三种方式在同一批查询上的效果，
  产出 `semantic-search/eval/vector-comparison-report.md`。
- **Phase 1 起**：`/api/search` 需要针对性测试覆盖——空结果、超长 query、单篇文章多 chunk
  命中时是否正确聚合去重、双语查询路由是否正确；集成测试跑一遍构建 → 索引 → 查询全链路。
