# 语义检索 / 智能推荐功能 — 可执行方案 v1.0（裁定版）

> 分支：`feature/semantic-search-poc`　目录：`semantic-search/`
> 上一版：`PLAN.md` v0.1（草案）→ Codex 评审（见 `CODEX_REVIEW.md`）→ 本文裁定合并
> 状态：Phase 0A/0B 已执行完成（T1.1.x/T1.2.1），T1.2.2 已裁定 Phase 1 = go
>
> **2026-08-22 补充**：本文 §0 表格里"RRF/reranker 列为可选增强，不作为 Phase 1 硬性要求"
> 这条已被 T1.2.2 的裁定取代——Phase 1 现在**要求** RRF 融合（不是可选），reranker 仍是
> Phase 2 可选增强。本文其余内容（Phase 0A/0B 的执行记录、Cloudflare 账号操作提醒等）不变，
> 仍是历史决策记录；最新架构判断以 `docs/agent/architecture.md`/`spec.md`/`tasks.md` 为准。

## 0. 裁定摘要

Codex 的评审基于可验证的 Cloudflare 官方限额/定价逻辑，不是空泛意见，整体**全部采纳**，
对方案做了以下关键修正：

| 原方案 (v0.1) | 修正后 (v1.0) | 采纳程度 |
|---|---|---|
| Phase 0 直接上 Vectorize | 先上零成本的关键词/静态检索基线，再用离线实验决定是否值得上向量 | 全部采纳 |
| Cron 定时扫描 `src/content/blog/` | Worker 运行时里根本没有这个 Git 目录，改为"发布 hook 触发 + Cron 仅对账" | 全部采纳（原方案架构性错误） |
| 检索直接返回 chunk top-K | 按 `article_id` 聚合去重，每篇最多保留 1–2 个片段 | 全部采纳 |
| 中英文混在一起 embedding | 拆成独立 chunk，共享 `article_id`，按查询语言过滤 | 全部采纳 |
| "$5 套餐自带 AI 额度够用" | 改成基于 token/neuron 的预算公式，讲清楚 Free/Paid 都是每日 10,000 neurons 免费额度，Paid 只是能超额付费 | 全部采纳 |
| 没提删除/回滚 | 用确定性 ID（`article_id` + `chunk_id`）支撑增删改的幂等性 | 全部采纳 |
| 评测集 60–100 条查询、含 RRF 融合公式、reranker | 个人博客体量不需要企业级评测严谨度，评测集精简到 20–30 条；RRF/reranker 列为可选增强，不作为 Phase 1 硬性要求 | **部分采纳，裁判简化** |
| （无）具体 Cloudflare 数字 | Codex 给出的 neurons/维度/价格数字是 2026-08-20 时点的，实现前需到官方文档现查核实 | 加一条执行前置检查 |

未被拒绝的建议：无——Codex 的挑战全部成立且有依据。

## 1. 背景与诉求（不变）

博客已积累几百篇中英双语技术文章，读者靠分类/标签浏览难以定位内容。目标：用户输入一段自然语言
诉求，系统返回若干篇相关文章，并对每篇给出一句话说明——这篇文章解决诉求里的哪个环节/子问题。

约束：做成在线服务、索引持续自更新、依托现有 Cloudflare 账号与 $5 套餐、技术选型追求成熟简单轻量。

## 2. 业务流程（修正版）

```
发布流程 (deploy.sh / blog-publisher skill)
  └─▶ 生成/更新 search-manifest.json（article_id、slug、title、tags、language、content_hash…）
        └─▶ 发布成功后触发增量索引 Worker（Phase 1 起）
              └─▶ 写入检索数据源（Phase 0A: 静态索引 / Phase 1: Vectorize + KV manifest）

每日 Cron Trigger（Phase 2）
  └─▶ 对比 manifest 与索引内容，修复漏索引 / 清理孤儿向量（对账，不做主索引触发）

用户查询
  └─▶ /api/search（Phase 1 起）：query → 语言检测 → 检索 → 按 article_id 聚合 → top5 + 命中片段
        （Phase 0A 阶段是浏览器本地静态检索，不经过 Worker）
```

## 3. 分阶段执行计划

### Phase 0A — 关键词/静态检索基线（预计 1–2 天，本次立即执行）

**目标**：零在线 AI 成本地跑通"输入诉求 → 返回文章列表 + 命中片段"的完整体验，同时建立后续判断
"语义检索是否值得做"的基线数据。

1. 构建时（Astro build）生成文章搜索文档：`article_id`（用 slug）、title/titleEn、description、
   tags、category、language、URL、正文标题层级
2. 接入 [Pagefind](https://pagefind.app/)（构建后索引静态文件，无需数据库/在线服务，天然适配 Astro）
3. 博客加一个简单搜索入口页，展示命中标题 + 高亮片段（先不做"匹配理由"这种语义化描述，命中片段本身就是解释）
4. 人工整理 20–30 条评测查询（覆盖技术名词/自然语言问题/宽泛探索/中文/英文/跨语言/"博客里没有答案"负样本各若干条），记录 Recall@5 与主观失败案例，作为后续 Phase 0B 的对比基线

**不涉及**：Vectorize、Workers AI、LLM、Cron。

### Phase 0B — 离线向量效果验证（不上线，只做决策依据）

用 Phase 0A 的同一批评测查询，本地/CI 里跑 `bge-m3` embedding + 向量召回，对比"纯关键词 vs 纯向量 vs
两者融合"。只有满足以下任一门槛，才进入 Phase 1：
- 跨语言查询（如中文问英文文章内容）的 Recall@5 相对关键词基线有明显提升
- 整体检索质量不低于关键词基线，且自然语言/宽泛问题的召回有可感知改善
- 精确技术名词/版本号类查询没有因为引入向量检索而明显变差

如果验证结果显示关键词基线已经够用，Phase 1 可以推迟或降级为"仅优化 Pagefind 的中文分词和排序"。

### Phase 1 — 语义检索上线（验证通过后执行）

1. Cloudflare Vectorize 索引 + Workers AI `@cf/baai/bge-m3` embedding（1024 维，注意存储维度预算，
   `chunk 数 × 1024` 不要无节制增长，实现前重新核对当时的 Vectorize 免费/付费额度）
2. 分片策略：文章级向量（标题+摘要+标签+标题层级）+ 段落级向量（300–600 tokens，overlap
   50–100 tokens，按 Markdown 结构切，每篇 chunk 数上限 12–16），代码块不单独作为主 embedding
3. 中英文拆成独立 chunk（`chunk_id = article_id:language:content_hash`），共享 `article_id`；
   metadata 只放 ID/URL/标题/语言/摘要/标签/hash，不放全文
4. `/api/search`：query embedding → 检索 top 20–30 chunk → 按 `article_id` 聚合去重（每篇最多
   1–2 个片段）→ 返回 top5 + 命中片段；先用 Pagefind 结果和向量结果做简单的加权/融合排序（起步不追求
   RRF 公式级精细度）
5. 基本防滥用：输入长度上限、简单限速、常见查询做缓存、超时降级回 Pagefind 结果、不记录原始查询原文
6. 索引 manifest 记录 `embedding_model / embedding_dimensions / chunking_version / content_hash /
   language / indexed_at`，模型或切片算法变更时建新索引回填切流，不原地混写新旧 embedding

### Phase 2 — 自动更新与可选增强

1. 发布流程（`deploy.sh` / blog-publisher skill）末尾接一步 hook，发布成功后触发增量索引
2. 每日 Cron Trigger 做对账：比对 manifest 与索引内容的 content_hash，修复漏索引文章、清理已删除
   文章/旧 slug 残留的向量（用确定性 `article_id`/`chunk_id` 做幂等增删）
3. 可选：`@cf/baai/bge-reranker-base` 对融合后的 top10 重排（比用 8B LLM 判断全部候选更省成本）
4. 可选：LLM 生成的一句话"匹配理由"——只对最终返回的 3 篇结果生成（不对候选集全量生成）、
   异步加载、设超时、缓存规范化查询的生成结果、不允许输出检索结果之外的判断
5. 可选：点击反馈用于后续排序调优

## 4. 核心技术栈

| 层 | Phase 0A | Phase 1 起 |
|---|---|---|
| 检索 | Pagefind（构建时静态索引） | + Cloudflare Vectorize |
| Embedding | 无 | Workers AI `@cf/baai/bge-m3`（1024 维，中英双语） |
| 运行时 | 纯静态，浏览器本地 | Cloudflare Workers（`/api/search`） |
| 索引触发 | Astro build 内置 | 发布 hook 为主，Cron Trigger 仅对账 |
| 推荐语 | 命中片段本身即解释 | 可选：Workers AI 小型 LLM，仅 Phase 2 |

## 5. 明确不做

- 不做用户账号体系、检索历史、个性化排序
- 不做中英文之外的其他语言支持
- 不做图数据库/知识图谱式关系检索
- Phase 1 起步不追求 RRF 公式级精细排序调参、不引入 reranker，除非 Phase 0B/上线后数据显示有必要
- 不在没有 Phase 0B 离线验证数据的情况下，把 Vectorize 当作"理所当然应该做"的既定结论

## 6. 执行前置检查

实现 Phase 1 时，先到 Cloudflare 官方文档现查一次 Vectorize 限额/定价和 Workers AI 各模型的
neurons 单价（本文档和 `CODEX_REVIEW.md` 里的数字是 2026-08-20 时点的参考值，不能直接硬编码进
代码或预算表）。
