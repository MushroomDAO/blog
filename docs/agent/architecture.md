# 语义检索 / 智能推荐功能 架构 — 技术判断与骨架

> 详细方案与 Codex 评审见 `semantic-search/PLAN.md`（v1.0）与 `semantic-search/CODEX_REVIEW.md`。
> 本文档摘取「怎么搭」的骨架与不可动摇的边界，供 tasks.md 对照实现。
> 记录日期：2026-08-20

## 核心判断

1. **先证明价值，再加复杂度**：不直接上向量检索。Phase 0A 先用 Pagefind 做零成本静态关键词检索，
   Phase 0B 用同一批评测查询离线对比向量检索的效果，只有确有提升才进入 Phase 1 上线 Vectorize。
2. **索引更新靠发布 hook，不靠 Cron 扫描 Git 目录**：Worker 运行时里没有 `src/content/blog/` 这个
   Git 目录，增量索引必须由发布流程主动触发；Cron 只做每日对账（reconciliation），不做主触发。
3. **检索结果按文章聚合，不直接返回 chunk**：向量相似度是片段级的，不等于文章相关性；必须按
   `article_id` 聚合去重，每篇最多保留 1–2 个命中片段，避免单篇文章刷屏。
4. **中英文分开建索引，不混在一条向量里**：同一篇文章的中英文内容语义不完全等价，混合会稀释表示；
   拆成独立 chunk，共享 `article_id`，按查询语言过滤。
5. **全部复用 Cloudflare 托管能力**：Pagefind（构建时）+ Workers AI（embedding/可选 LLM）+
   Vectorize（向量存储）+ Workers（API）+ Cron Trigger（对账），不引入额外账号/服务。
6. **T1.2.2 裁定（2026-08-21，go，混合方案，非纯向量替代）**：`vector-comparison-report.md` 显示
   纯向量单独替代关键词不成立（精确技术名词查询会退步、负样本更容易给出误导性匹配），但跨语言检索
   有决定性优势且关键词结构性做不到。裁定结果：两个都要，**关键词与向量并行检索 + RRF
   （Reciprocal Rank Fusion）融合排序**，不是"选一个用"，也不是"关键词优先向量兜底"的条件分支——
   本产品访问量很小（见下条认证限制），没有为省钱做分支路由的必要，每次查询两路都跑。
7. **`/api/search` 不对外公开，登录后才能用**：这是用户明确决定——语义检索接的是 Workers AI
   付费能力，不希望任何人都能访问导致被刷额度。认证方案是**单一共享密码 + 签名 Cookie**
   （`BLOG_SEARCH_PASSWORD` 校验、`BLOG_SEARCH_SESSION_SECRET` 做 HMAC 签名，均为 Worker Secret，
   已生成并记录在 `~/Dev/.env`，尚未推送到 Cloudflare），**明确排除 Cloudflare Access**（用户已否决）。
   认证层要做成可替换的独立中间件，以后想换方案只改这一处。见 T1.3.6。

## 系统骨架

```
Phase 0A（静态基线）
  Astro build
    └─▶ 文章 layout 打 data-pagefind-* 标记
          └─▶ postbuild: pagefind 对 dist/ 生成索引 (dist/pagefind/)
                └─▶ /search 页面用 pagefind 浏览器端 JS API 查询，纯静态

Phase 1 起（语义检索上线）
  发布流程 (deploy.sh / blog-publisher skill)
    └─▶ 生成/更新 search-manifest.json（article_id、slug、language、content_hash…）
          └─▶ 发布成功后触发增量索引 Worker
                └─▶ 调 Workers AI bge-m3 生成 embedding（远程推理，非本地）
                      └─▶ upsert 到 Vectorize（按 article_id/chunk_id 幂等）

  用户查询（需先登录，见下方认证）
    └─▶ /api/search Worker：校验登录 Cookie → query → 语言检测
          → Pagefind 关键词 top20 ∥ embedding→Vectorize 向量 top20（并行）
          → 按 rank（非原始分数）做 RRF 融合 → 按 article_id 聚合去重（每篇 1-2 片段）
          → 两路信号均弱则直接返回"没有找到"，不硬凑结果 → 否则返回 top5 + 命中片段

  登录
    └─▶ POST /api/search-auth（密码）→ 校验 BLOG_SEARCH_PASSWORD（常量时间比较）
          → 签发 HMAC 签名 Cookie（HttpOnly/Secure/SameSite=Lax，长有效期）
          → 该接口本身限速（同 IP 15 分钟内最多 5 次），防止密码被撞库

Phase 2（自动化与增强）
  每日 Cron Trigger
    └─▶ 对比 manifest 与索引内容的 content_hash，修复漏索引、清理孤儿向量（不做主触发）
```

## 契约 / 接口

- **文章搜索文档**（构建期产出，供 Pagefind 及后续 manifest 复用）：
  `article_id`（=slug）、`title`/`titleEn`、`description`/`descriptionEn`、`tags`、`category`、
  `language`、`url`、正文标题层级。字段来源见 `spec.md`。
- **`/api/search`**（Phase 1 起）：需携带有效登录 Cookie；输入自然语言 query（有长度上限）；
  输出 top5 文章（每篇：标题、URL、命中片段、语言），关键词/向量两路信号均弱时明确返回
  "没有找到"而不是硬凑结果。
- **`/api/search-auth`**（Phase 1 起）：输入密码，输出登录 Cookie 或 401；限速见上。
- **索引 manifest**：记录 `embedding_model` / `embedding_dimensions` / `chunking_version` /
  `content_hash` / `language` / `indexed_at`，模型或切片算法变更时建新索引回填切流，不原地混写。

## 不可动摇的边界

- 绝不假设 Worker 运行时能访问 Git 仓库目录；索引数据源必须是部署后可达的
  manifest/KV/D1/sitemap 之一。
- Vectorize 的 metadata 不存全文（10KiB/向量上限），只存检索所需的最小字段。
- 检索结果必须按 `article_id` 去重聚合，不允许把 chunk top-K 直接当文章结果返回。
- 公开的 `/api/search` 必须有输入长度上限、限速、超时降级（回退到 Pagefind 结果），
  不记录用户原始查询原文。
- Phase 1 是否上线，由 T1.2.2 依据 Phase 0B 的离线评测数据人工拍板，不由 agent 自行判断"应该做"
  ——**已拍板：go，混合方案**（见上方核心判断 6）。
- 模型/切片算法变更后旧向量不得与新向量混用；必须建新索引回填切流。
- 融合排序用 RRF（按排名融合），不手调关键词分数与向量余弦相似度的加权系数——两者量纲不同，
  直接加权不稳定。
- `/api/search` 及 `/search` 页面的语义检索能力**不对公众开放**，必须先过 T1.3.6 的密码登录，
  不允许上线一个无认证版本（哪怕是临时/测试）。
- **`wrangler vectorize create`（建 Vectorize 索引）与 `wrangler secret put`（推送
  `BLOG_SEARCH_PASSWORD`/`BLOG_SEARCH_SESSION_SECRET` 等密钥）是真实 Cloudflare 账号级操作，
  有计费与不可逆影响**——无人值守执行到这两类命令前必须停下来问用户确认，问完再继续同一个
  task，不得跳过或假设已获授权。

## 运行形态

- Phase 0A：纯静态，构建产物随 `deploy.sh` 一并发布到 Cloudflare Pages，无在线服务。
- Phase 1 起：Cloudflare Workers（HTTP API）+ Vectorize（存储）+ Workers AI（推理），
  触发方式为发布 hook（主）+ Cron Trigger（每日对账，Phase 2）。
