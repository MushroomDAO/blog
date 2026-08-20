# Codex 评审原文（对 PLAN.md v0.1 的评审）

> 评审方式：`mcp__codex__codex`，sandbox=read-only，一次性严格评审
> 评审对象：PLAN.md v0.1 全文
> 说明：文中引用的 Cloudflare 具体限额/定价数字是 Codex 基于其 2026-08-20 时点掌握的官方文档给出的，
> **实现前务必到 Cloudflare 官方文档现查一次核实未变**，不作为最终依据直接硬编码到代码里。

---

## 总体结论

这份方案"能做出来"，但目前有三个根本问题：

1. **先选了 Vectorize，再定义如何证明它比关键词搜索更好。**
2. **把文章分片、双语建模、去重和排序问题，错误地简化成了"向量库选型"。**
3. **Phase 0 仍然偏重，却没有检索质量基线、评测集和成本保护。**

对于几百篇技术文章，不应直接批准原 Phase 0。建议先做一个可评测的词法检索基线，再决定是否引入
Vectorize。最终架构可以是 Cloudflare Workers AI + Vectorize，但应采用"文章级召回 + 片段级解释"
的混合检索，而不是直接把所有片段 top-K 当文章结果。

## 1. 架构与技术选型风险（要点）

- Vectorize 容量（20M 向量/索引、1536 维上限、topK≤50 带 metadata）对几百篇文章完全宽裕，
  真正的风险是**检索质量**：向量相似度不等于文章相关性，多个片段可能来自同一篇文章导致刷屏，
  需要按 `article_id` 聚合去重、每篇最多保留 1–2 个片段、标题/标签加权、词法+向量融合、
  设置最低相关性阈值。
- `bge-m3` 输出通常 1024 维，几千个 chunk 时存储维度会逼近 Free 套餐 5M dimensions 的额度线，
  不能"随便切片"，chunk 数量要有预算意识。
- "$5 套餐自带 AI 额度"表述不准确：Free/Paid 都有每日 10,000 neurons 免费额度，Paid 的区别是
  超额后可以继续付费用，不是额外赠送一大笔额度。
- embedding 便宜，真正的成本/延迟风险在于**每次搜索都调用 LLM 生成推荐语**——应只对最终
  3 篇结果生成、异步加载、加缓存超时，而不是对候选集全量生成。
- 模型/切片算法变更后旧向量不能和新向量混用，需要在索引 manifest 里记录
  `embedding_model / embedding_dimensions / chunking_version / content_hash / language / indexed_at`，
  换算法时建新索引回填切流。
- **"Cron 定时扫描 `src/content/blog/`" 这个假设不成立**：部署后的 Worker 运行时里没有这个 Git 目录。
  必须改成扫描部署后的数据源（manifest / D1 / KV / sitemap 等），可靠模式是
  "发布 hook 触发增量索引为主 + 每日 Cron 只做对账（reconciliation）"。
- 缺少删除/回滚/部分失败设计：文章删除、slug 改名、分段数变化后旧 chunk 如何清理，
  upsert 部分失败、发布回滚后索引如何跟着回滚。建议用确定性 ID：
  `article_id`（稳定 slug/UUID）+ `chunk_id = article_id:language:chunk_hash`，
  更新时"先记录旧 chunk id → 写入新版本成功后再删旧版本"。
- Vectorize 的 metadata 上限 10KiB/向量，不应存全文，只放 ID/URL/标题/语言/摘要/标签/hash，
  全文仍由 Pages 提供，文章级信息可以放静态 manifest/KV/D1。
- 公开 `/api/search` 需要基本防滥用：输入长度限制、限速、查询缓存、超时降级到关键词搜索、
  不记录原始查询或明确日志留存规则、监控调用量与每日 neurons。

## 2. 对 7 个开放问题的判断（要点）

1. **规模**：容量够，但不是靠规模判断要不要用 Vectorize；应先取 top 20–30 个 chunk 再按文章聚合
   到 top 5，不要把 chunk top-K 直接当文章结果。
2. **分片策略**：不整篇 embedding，也不机械按固定字符切；建议文章级向量（标题+摘要+标签+标题层级）
   + 段落级向量（300–600 tokens，overlap 50–100 tokens，按 Markdown 结构切），每篇 chunk 数量上限
   12–16，代码块不单独作为主 embedding。
3. **双语**：中英文拆成独立 chunk（`language: zh|en`），共享同一个 `article_id`；查询时按检测到的
   查询语言优先过滤，同语言不足再跨语言补召回，最终同一篇文章只出现一次。
4. **Cron vs hook**：发布 hook 为主（发布成功后触发增量索引），Cron 只做每日对账修复漏索引/孤儿向量；
   不要只依赖 Cron 轮询。
5. **替代方案**：最值得比较的不是换一个向量库，而是先上词法/静态检索基线（Pagefind 等构建时索引，
   零在线成本、零运维、与部署产物天然同步）；D1 FTS 对中文分词不一定比 Pagefind 简单；
   其他外部向量库（Pinecone/Qdrant/pgvector）在这个规模上只会引入不必要的复杂度和账单。
6. **免费额度**：embedding 成本可忽略（几百篇文章一次性索引 + 日常查询量远低于每日免费额度）；
   真正的变量是 LLM 推荐语的调用频率和输入长度，需要建立一个基于 token/neuron 的预算公式，
   而不是笼统写"应该够用"。
7. **质量评估**：应建立一个小的人工评测查询集（技术名词/自然语言/宽泛问题/中文/英文/跨语言/
   负样本），用 Recall@5、MRR@5、nDCG@5、Success@3、重复率、无结果精确率等指标，对比
   "关键词 / 静态检索 / 纯向量 / 混合检索"几种方案，用数据证明向量方案确实带来提升，
   而不是凭感觉上线。

## 3. 更简单/成熟/省钱的替代架构

- **方案 A（推荐作为第一步）**：纯静态检索。Astro 构建时接入 Pagefind 或等价方案，浏览器本地搜索，
  用命中标题/章节/高亮片段做"为什么相关"的解释，零在线 AI 成本、零运维。
- **方案 B（推荐作为中期目标）**：轻量混合检索。词法 top20 + 向量 top20 → 按 `article_id` 聚合 →
  RRF（Reciprocal Rank Fusion）融合排序 → 标题/标签/语言/日期轻量加权 → 返回 top5 + 最佳命中片段；
  RRF 比手调加权系数更稳定，因为两种分数不在同一量纲。如需进一步提升可用
  `@cf/baai/bge-reranker-base` 对融合后的 top10 重排，成本远低于用 8B LLM 判断全部候选。
- **方案 C（仅作实验，不建议作为生产架构）**：构建期预计算 embedding 生成静态压缩文件，
  查询时 Worker 现算 query embedding 再做精确 cosine 相似度；几千个向量约 20MB（int8 量化后约 5MB），
  Worker 每次扫描全部向量的 CPU/加载成本可能比 Vectorize 更差。

## 4. MVP / Phase 0 调整建议

原 Phase 0 同时引入了新模型、分片、Vectorize、Worker API、前端、索引脚本，但没有基线、评测集、
文章级去重、失败/删除策略、成本观测、防滥用——系统能跑通，但没人知道结果好不好。

建议拆分为：

- **Phase 0A**（约 1–2 天）：构建时生成文章搜索文档（ID/标题/描述/标签/标题层级/语言/URL）+
  接入 Pagefind 或等价静态搜索 + 简单搜索页 + 30–50 条人工评测查询 + 记录 Recall@5/MRR@5 和主观失败案例。
  不涉及 Vectorize / Workers AI / LLM / Cron。
- **Phase 0B**：离线向量实验（本地/CI），用同一批评测查询对比纯词法 / 纯向量 / RRF 混合，
  只有在跨语言、自然语言问题上有可测量提升（例如跨语言 Recall@5 提升 ≥15%、整体 nDCG@5
  不低于词法基线、精确技术名词查询不明显退化）才进入 Phase 1。
- **Phase 1**：正式上线语义检索——Vectorize 索引、`/api/search`、query embedding、
  文章级聚合、语言过滤、RRF、缓存和限速、日志与成本监控。
- **Phase 2**：自动更新与可选增强——发布 hook、Cron 对账、可选 reranker、可选 LLM 匹配理由、
  可选点击反馈。

## 最终建议（Codex 原话）

> Pagefind/BM25 基线 + `bge-m3`/Vectorize 语义召回 + RRF 融合 + article-level 聚合。
> 发布 hook 更新索引，Cron 只负责对账。推荐理由优先用最佳命中章节和片段，LLM 延后。

需要立即修改原方案的十点：删除"Cron 扫描 git 目录"的表述；明确 `bge-m3` 为 1024 维并计算实际
chunk 数对应的额度；中英文拆成不同 chunk 但共享 `article_id`；Phase 0 前增加词法搜索基线和评测集；
检索结果按文章聚合而非直接返回 top-K chunk；加入删除/slug 变更/回滚/部分失败策略；把"免费额度够用"
改成基于 token/neuron 的预算公式；把 LLM 理由从核心能力降为可选增强；给 `/api/search` 加缓存/限速/
输入上限/无结果策略；在没有离线评测数据证明收益前不把 Vectorize 视为既定结论。
