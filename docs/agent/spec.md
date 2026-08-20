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
| `chunk_id` | `article_id:language:chunk_hash`，确定性 ID，支撑幂等 upsert/delete |
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
