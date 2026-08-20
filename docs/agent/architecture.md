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

  用户查询
    └─▶ /api/search Worker：query → 语言检测 → embedding → Vectorize 检索
          top 20-30 chunk → 按 article_id 聚合去重 → 与 Pagefind 结果轻量融合
          → 返回 top5 + 命中片段

Phase 2（自动化与增强）
  每日 Cron Trigger
    └─▶ 对比 manifest 与索引内容的 content_hash，修复漏索引、清理孤儿向量（不做主触发）
```

## 契约 / 接口

- **文章搜索文档**（构建期产出，供 Pagefind 及后续 manifest 复用）：
  `article_id`（=slug）、`title`/`titleEn`、`description`/`descriptionEn`、`tags`、`category`、
  `language`、`url`、正文标题层级。字段来源见 `spec.md`。
- **`/api/search`**（Phase 1 起）：输入自然语言 query（有长度上限）；输出 top5 文章
  （每篇：标题、URL、命中片段、语言），无匹配结果时明确返回"没有找到"而不是硬凑结果。
- **索引 manifest**：记录 `embedding_model` / `embedding_dimensions` / `chunking_version` /
  `content_hash` / `language` / `indexed_at`，模型或切片算法变更时建新索引回填切流，不原地混写。

## 不可动摇的边界

- 绝不假设 Worker 运行时能访问 Git 仓库目录；索引数据源必须是部署后可达的
  manifest/KV/D1/sitemap 之一。
- Vectorize 的 metadata 不存全文（10KiB/向量上限），只存检索所需的最小字段。
- 检索结果必须按 `article_id` 去重聚合，不允许把 chunk top-K 直接当文章结果返回。
- 公开的 `/api/search` 必须有输入长度上限、限速、超时降级（回退到 Pagefind 结果），
  不记录用户原始查询原文。
- Phase 1 是否上线，由 T1.2.2 依据 Phase 0B 的离线评测数据人工拍板，不由 agent 自行判断"应该做"。
- 模型/切片算法变更后旧向量不得与新向量混用；必须建新索引回填切流。

## 运行形态

- Phase 0A：纯静态，构建产物随 `deploy.sh` 一并发布到 Cloudflare Pages，无在线服务。
- Phase 1 起：Cloudflare Workers（HTTP API）+ Vectorize（存储）+ Workers AI（推理），
  触发方式为发布 hook（主）+ Cron Trigger（每日对账，Phase 2）。
