# 语义检索 / 智能推荐功能 任务台账 — Task

> 前置：[`roadmap.md`](roadmap.md)（M→F）· [`architecture.md`](architecture.md) / [`spec.md`](spec.md)
> 每个 Task 自包含，可独立开发与验收。**验收标准必须可机器验证**（跑命令能判定）。
> 状态：BACKLOG · READY · IN_PROGRESS · BLOCKED · PR_OPEN · CHANGES_REQUESTED · APPROVED · DONE
> 字段说明见 pilot skill 的 `reference/task-schema.md`。
> 记录日期：2026-08-20

---

## F1.1 — 关键词/静态检索基线（Phase 0A）

### T1.1.1 给文章模板打 Pagefind 元数据标记  `READY`
- **优先级**：high
- **目标**：让 Pagefind 索引时能拿到 language/tags/category 等可过滤字段，且只索引正文，
  不索引导航栏/页脚
- **开发范围**：在 `src/layouts/BlogPost.astro` 上加 `data-pagefind-body`（限定索引范围到正文）、
  `data-pagefind-filter="language"` / `data-pagefind-filter="category"` 等属性；双语文章
  （含 `<!--EN-->` 分隔符）按语言拆两段分别标记
- **明确不做**：不改版式/样式，不引入 Pagefind 依赖本身（下一个 task）
- **依赖**：无
- **交付物**：修改后的 `src/layouts/BlogPost.astro`
- **验收命令**：`pnpm build && grep -q "data-pagefind-body" dist/blog/*/index.html`
  （任取一篇已发布文章的构建产物验证标记存在）
- **涉及文件**：`src/layouts/BlogPost.astro`
- **风险/回滚**：无涉钱/涉安全风险；改动可通过 `git revert` 直接回滚
- **证据**：<Branch / PR / 合并 commit，推进时回填>

### T1.1.2 集成 Pagefind 构建后索引  `BACKLOG`
- **优先级**：high
- **目标**：`pnpm build` 后自动生成可供浏览器端查询的 Pagefind 索引
- **开发范围**：加 `pagefind` 为 devDependency，`package.json` 加 postbuild script
  （`npx pagefind --site dist`），索引产物写入 `dist/pagefind/`
- **明确不做**：不单独部署索引服务——产物随 `dist/` 一起走现有 `deploy.sh` 发布
- **依赖**：T1.1.1
- **交付物**：`package.json` 的 postbuild script + 构建期生成的 `dist/pagefind/`
- **验收命令**：`pnpm build && test -f dist/pagefind/pagefind.js`
- **涉及文件**：`package.json`
- **风险/回滚**：无
- **证据**：<推进时回填>

### T1.1.3 搜索入口页面  `BACKLOG`
- **优先级**：high
- **目标**：博客加一个 `/search` 页面，输入框 + 结果列表（标题、命中片段高亮、链接）
- **开发范围**：新增 `src/pages/search.astro`，用 Pagefind 浏览器端 JS API
  （`dist/pagefind/pagefind.js`）做检索，纯静态、无需服务端
- **明确不做**：不做语言过滤 UI（Phase 1 再加）、不做分页、不做"匹配理由"文案
  （命中片段本身就是解释）
- **依赖**：T1.1.2
- **交付物**：`/search` 页面
- **验收命令**：`pnpm build && test -f dist/search/index.html`
- **涉及文件**：`src/pages/search.astro`
- **风险/回滚**：无
- **证据**：<推进时回填>

### T1.1.4 评测查询集 + Recall@5 基线记录  `BACKLOG`
- **优先级**：mid
- **目标**：整理评测查询集，跑一遍 T1.1.3 的搜索，记录基线效果，供 F1.2 对比
- **开发范围**：撰写 20–30 条查询（技术名词/自然语言/宽泛探索/中文/英文/跨语言/负样本各若干条）
  到 `semantic-search/eval/queries.md`；人工跑一遍搜索页面，把结果与主观判断记录到
  `semantic-search/eval/baseline-results.md`
- **明确不做**：不写自动化评测脚本（规模小，人工记录足够）
- **依赖**：T1.1.3
- **交付物**：`semantic-search/eval/queries.md`、`semantic-search/eval/baseline-results.md`
- **验收命令**：`test -f semantic-search/eval/queries.md && test -f semantic-search/eval/baseline-results.md
  && [ $(wc -l < semantic-search/eval/queries.md) -ge 20 ]`
- **涉及文件**：`semantic-search/eval/queries.md`、`semantic-search/eval/baseline-results.md`
- **风险/回滚**：无
- **证据**：<推进时回填>

---

## F1.2 — 离线向量效果验证（Phase 0B，决策门，不上线）

### T1.2.1 本地/CI 跑 bge-m3 embedding 对比实验  `BACKLOG`
- **优先级**：mid
- **目标**：用 T1.1.4 的评测查询集，离线对比"纯关键词(Pagefind) vs 纯向量(bge-m3) vs 简单融合"
  三种方式的检索效果
- **开发范围**：写一次性实验脚本，调用 Workers AI API 生成 embedding，对评测查询集跑检索，
  产出对比报告
- **明确不做**：不接入 Vectorize，不上线，不做生产级代码
- **依赖**：T1.1.4
- **交付物**：`semantic-search/eval/vector-comparison-report.md` + 实验脚本
- **验收命令**：`test -f semantic-search/eval/vector-comparison-report.md`
- **涉及文件**：一次性实验脚本（路径待定）、`semantic-search/eval/vector-comparison-report.md`
- **风险/回滚**：实验会消耗 Workers AI 额度，但几百篇文章一次性 embedding 成本可忽略
  （见 `semantic-search/CODEX_REVIEW.md` 成本测算）
- **证据**：<推进时回填>

### T1.2.2 Phase 1 Go/No-Go 裁定  `BACKLOG`
- **优先级**：high
- **目标**：依据 T1.2.1 的对比报告，对照 `semantic-search/PLAN.md` §Phase 0B 的门槛
  （跨语言 Recall@5 是否有明显提升、整体质量是否不低于关键词基线、精确技术名词查询是否退化），
  决定是否进入 Phase 1
- **开发范围**：无代码改动，纯决策；结果写入 `progress.md`，并据此把 F1.3 的 Task 状态
  从 `BACKLOG` 解锁为 `READY`（go）或保持 `BACKLOG`/标记暂缓（no-go）
- **明确不做**：—
- **依赖**：T1.2.1
- **说明**：这是产品方向决策，**不可由 agent 无人值守自行拍板**——`run` 遇到此 task 应保持
  `BLOCKED`，在 `progress.md` 写清 T1.2.1 的结论摘要，等待用户确认后再解锁下游 Task。
- **交付物**：`progress.md` 里的裁定记录
- **验收命令**：无法机器验证（产品决策），验收方式是用户在 `progress.md` 里看到裁定并确认
- **涉及文件**：`docs/agent/progress.md`、`docs/agent/roadmap.md`（更新 F1.3 状态）
- **风险/回滚**：无
- **证据**：<推进时回填>

---

## F1.3 — 语义检索上线（Phase 1，依赖 T1.2.2 裁定为 go）

### T1.3.1 建 Vectorize 索引 + Workers AI embedding 接入  `BACKLOG`
- **优先级**：high
- **目标**：跑通"文章内容 → bge-m3 embedding → 写入 Vectorize"的一次性全量索引脚本
- **开发范围**：Cloudflare Vectorize 索引创建（1024 维）、Workers AI `bge-m3` 调用封装、
  全量索引脚本（读取文章搜索文档 → embedding → upsert）
- **明确不做**：不做增量更新（T1.4.1）、不做前端
- **依赖**：T1.2.2（裁定 = go）
- **交付物**：Vectorize 索引 + 全量索引脚本
- **验收命令**：`<待实现时补充：如 wrangler vectorize query 返回非空结果>`
- **涉及文件**：待定（新增索引脚本目录）
- **风险/回滚**：涉及 Cloudflare 计费额度，实现前需按 `semantic-search/PLAN.md` §6
  重新核对当时的 Vectorize/Workers AI 定价与限额
- **证据**：<推进时回填>

### T1.3.2 分片与双语 chunk 策略实现  `BACKLOG`
- **优先级**：high
- **目标**：按 `spec.md` 的数据模型，把文章切成文章级+段落级 chunk，中英文分开建索引
- **开发范围**：分片逻辑（300–600 tokens，overlap 50–100，按 Markdown 结构切，每篇上限
  12–16 chunk）、双语文章按 `<!--EN-->` 拆分、`chunk_id` 生成
- **明确不做**：不做代码块单独 embedding
- **依赖**：T1.3.1
- **交付物**：分片模块
- **验收命令**：`<待实现时补充：如对一篇双语测试文章跑分片，断言产出的 chunk 数与 language 分布符合预期>`
- **涉及文件**：待定
- **风险/回滚**：无
- **证据**：<推进时回填>

### T1.3.3 `/api/search` Worker 端点  `BACKLOG`
- **优先级**：high
- **目标**：query → embedding → Vectorize 检索 → 按 `article_id` 聚合去重 → 返回 top5 + 命中片段
- **开发范围**：Cloudflare Worker HTTP 端点，含语言检测、文章级聚合、与 Pagefind 结果的轻量融合
- **明确不做**：不做 RRF 精细排序公式、不接 reranker（Phase 2 可选）
- **依赖**：T1.3.2
- **交付物**：`/api/search` Worker
- **验收命令**：`<待实现时补充：如对已知查询发请求，断言返回结果里同一 article_id 不重复>`
- **涉及文件**：待定（新增 Worker 目录）
- **风险/回滚**：涉及公开 API，需配合 T1.3.4 的防滥用一起上线，不单独暴露无限速版本
- **证据**：<推进时回填>

### T1.3.4 API 防滥用（限速/输入上限/缓存/降级）  `BACKLOG`
- **优先级**：high
- **目标**：`/api/search` 具备基本防滥用能力，不被刷爆 Workers AI 额度
- **开发范围**：输入长度上限、简单限速、常见查询缓存、超时降级回退到 Pagefind 结果、
  不记录用户原始查询原文
- **明确不做**：不做验证码类交互防护（超出必要）
- **依赖**：T1.3.3
- **交付物**：防滥用中间件/逻辑
- **验收命令**：`<待实现时补充：如对超长 query 发请求，断言被拒绝而非报错崩溃>`
- **涉及文件**：待定
- **风险/回滚**：涉钱（Workers AI 按量计费），必须在 `/api/search` 公开前完成
- **证据**：<推进时回填>

### T1.3.5 索引 manifest 版本化  `BACKLOG`
- **优先级**：mid
- **目标**：记录 `embedding_model`/`embedding_dimensions`/`chunking_version`/`content_hash`/
  `language`/`indexed_at`，为后续模型/分片算法变更做好回填切流的准备
- **开发范围**：manifest 存储（KV 或 D1）+ 读写逻辑
- **明确不做**：不做多版本并行 A/B（超出当前需要）
- **依赖**：T1.3.1
- **交付物**：manifest 存储结构
- **验收命令**：`<待实现时补充>`
- **涉及文件**：待定
- **风险/回滚**：无
- **证据**：<推进时回填>

---

## F1.4 — 自动更新与增强（Phase 2，依赖 F1.3 全部 DONE）

### T1.4.1 发布流程接入增量索引 hook  `BACKLOG`
- **优先级**：high
- **目标**：`deploy.sh` / blog-publisher skill 发布成功后，自动触发新增/变更文章的增量索引
- **开发范围**：发布流程末尾加一步 hook 调用，生成/更新 `search-manifest.json` 并触发索引
- **明确不做**：不做失败重试的复杂退避策略（交给 T1.4.2 的 Cron 对账兜底）
- **依赖**：F1.3 全部 Task DONE
- **交付物**：`deploy.sh` 或 blog-publisher skill 的 hook 改动
- **验收命令**：`<待实现时补充：如发布一篇测试文章后，短时间内 /api/search 能查到它>`
- **涉及文件**：`deploy.sh`、`.agents/skills/blog-publisher/`
- **风险/回滚**：改动发布流程需谨慎，不能影响现有博客发布主流程；出问题可直接回滚该 hook
- **证据**：<推进时回填>

### T1.4.2 Cron Trigger 每日对账  `BACKLOG`
- **优先级**：mid
- **目标**：每日比对 manifest 与索引内容的 `content_hash`，修复漏索引文章、清理已删除文章的
  残留向量
- **开发范围**：Cloudflare Cron Trigger + 对账逻辑
- **明确不做**：不做主触发（那是 T1.4.1 的职责）
- **依赖**：T1.4.1
- **交付物**：Cron Trigger 配置 + 对账脚本
- **验收命令**：`<待实现时补充>`
- **涉及文件**：待定
- **风险/回滚**：无
- **证据**：<推进时回填>

### T1.4.3 可选：LLM 生成一句话匹配理由  `BACKLOG`
- **优先级**：low（可选增强，非必须）
- **目标**：对最终返回的 3 篇结果生成一句话"这篇解决你诉求里的哪个环节"
- **开发范围**：只对 top3 生成（不对候选集全量生成）、异步加载、设超时、缓存规范化查询的生成结果
- **明确不做**：不允许 LLM 输出检索结果之外的判断
- **依赖**：T1.4.1
- **交付物**：推荐语生成逻辑
- **验收命令**：`<待实现时补充>`
- **涉及文件**：待定
- **风险/回滚**：涉钱（LLM 调用成本高于 embedding），需配合成本监控上线
- **证据**：<推进时回填>

### T1.4.4 可选：reranker 接入  `BACKLOG`
- **优先级**：low（可选增强，非必须）
- **目标**：用 `@cf/baai/bge-reranker-base` 对融合后的 top10 重排，提升排序质量
- **开发范围**：reranker 调用封装，接入 T1.3.3 的检索流程
- **明确不做**：—
- **依赖**：T1.3.3
- **交付物**：reranker 集成
- **验收命令**：`<待实现时补充>`
- **涉及文件**：待定
- **风险/回滚**：无
- **证据**：<推进时回填>
