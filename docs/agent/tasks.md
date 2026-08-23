# 语义检索 / 智能推荐功能 任务台账 — Task

> 前置：[`roadmap.md`](roadmap.md)（M→F）· [`architecture.md`](architecture.md) / [`spec.md`](spec.md)
> 每个 Task 自包含，可独立开发与验收。**验收标准必须可机器验证**（跑命令能判定）。
> 状态：BACKLOG · READY · IN_PROGRESS · BLOCKED · PR_OPEN · CHANGES_REQUESTED · APPROVED · DONE
> 字段说明见 pilot skill 的 `reference/task-schema.md`。
> 记录日期：2026-08-20

---

## F1.1 — 关键词/静态检索基线（Phase 0A）

### T1.1.1 给文章模板打 Pagefind 元数据标记  `DONE`
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
- **证据**：分支 `feat/T1.1.1-pagefind-metadata`，PR [#29](https://github.com/MushroomDAO/blog/pull/29)（合并 commit `09d7fce`）

### T1.1.2 集成 Pagefind 构建后索引  `DONE`
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
- **证据**：分支 `feat/T1.1.2-pagefind-index`，PR [#30](https://github.com/MushroomDAO/blog/pull/30)（合并 commit `5e3cc88`）

### T1.1.3 搜索入口页面  `DONE`
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
- **证据**：分支 `feat/T1.1.3-search-page`，PR [#31](https://github.com/MushroomDAO/blog/pull/31)（合并 commit `9eff119`）

### T1.1.4 评测查询集 + Recall@5 基线记录  `DONE`
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
- **证据**：分支 `feat/T1.1.4-eval-baseline`，PR [#32](https://github.com/MushroomDAO/blog/pull/32)（合并 commit `705b47c`）

---

## F1.2 — 离线向量效果验证（Phase 0B，决策门，不上线）

### T1.2.1 本地/CI 跑 bge-m3 embedding 对比实验  `DONE`
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
- **阻塞解除（2026-08-21）**：用户指出 `~/Dev/.env` 里的 `CLOUDFLARE_REGISTRAR_TOKEN`
  （另一个项目 cmic 长期在用）实测对 `POST /accounts/{id}/ai/run/@cf/baai/bge-m3` 鉴权成功，
  返回真实 1024 维 embedding（中英文均验证过）。改用这个 token 跑实验。
- **证据**：分支 `feat/T1.2.1-vector-experiment`，PR [#36](https://github.com/MushroomDAO/blog/pull/36)（合并 commit `b30e595`）

### T1.2.2 Phase 1 Go/No-Go 裁定  `DONE`
- **优先级**：high
- **目标**：依据 T1.2.1 的对比报告，对照 `semantic-search/PLAN.md` §Phase 0B 的门槛
  （跨语言 Recall@5 是否有明显提升、整体质量是否不低于关键词基线、精确技术名词查询是否退化），
  决定是否进入 Phase 1
- **裁定（2026-08-21，用户拍板）**：**go，混合方案**——不是"选关键词或选向量"，两个都要。
  用户原话确认："两个都要的话，如何组合出最佳效果"。裁定细节：
  1. 融合：关键词 + 向量并行检索，**RRF（Reciprocal Rank Fusion）**融合排序，按 article_id
     聚合去重，两路信号均弱时不返回结果（应对 T1.2.1 发现的负样本误导性匹配问题）。
  2. 认证：`/api/search` 不对外公开，**密码 + 签名 Cookie** 登录（用户明确否决 Cloudflare
     Access，要求"单独给一个写到 env 里的密码"、登录后长期记住）。
  3. 部署形态：全流程留在 Cloudflare（embedding/Vectorize/Worker），不做本地推理——用户问过
     "本地跑嵌入能否省成本"，结论是 embedding 成本本就可忽略（Codex 测算），本地/在线调用
     Cloudflare API 账单相同，不值得为此引入本地模型实现不一致的风险。
  4. 存储：中英文各自独立 chunk，用户已确认不介意多占存储空间。
  详见 `architecture.md` 核心判断 6/7、`spec.md` §检索融合/§登录会话。
- **交付物**：本次文档更新（`architecture.md`/`spec.md`/`tasks.md`/`progress.md`/`roadmap.md`）
- **验收命令**：无法机器验证（产品决策），验收方式是用户确认本 PR 记录的裁定符合其意图
- **涉及文件**：`docs/agent/*.md`
- **风险/回滚**：无
- **证据**：本 PR（docs/t122-go-decision）

---

## F1.3 — 语义检索上线（Phase 1，T1.2.2 已裁定 go）

### T1.3.1 建 Vectorize 索引 + Workers AI embedding 接入  `DONE`
- **优先级**：high
- **目标**：跑通"文章内容 → bge-m3 embedding → 写入 Vectorize"的一次性全量索引脚本
- **开发范围**：Cloudflare Vectorize 索引创建（1024 维）、Workers AI `bge-m3` 调用封装、
  全量索引脚本（读取文章搜索文档 → embedding → upsert）
- **明确不做**：不做增量更新（T1.4.1）、不做前端
- **依赖**：T1.2.2（已裁定 = go）
- **交付物**：`semantic-search/scripts/build-vectorize-index.py`（默认 dry-run，`--create-index`/
  `--upsert` 才真正动 Cloudflare 账号）
- **验收命令**：
  - dry-run（不涉账号，已验证通过）：`CLOUDFLARE_REGISTRAR_TOKEN=... CLOUDFLARE_ACCOUNT_ID=...
    python3 semantic-search/scripts/build-vectorize-index.py && test -f
    semantic-search/eval/vectorize-index-plan.json`（2026-08-22 实测：473 篇文章 → 901 条
    语言记录，zh 467/en 434，全部 1024 维；缓存复用已验证——第二次运行 0.3 秒内完成，
    不重新调用 Workers AI）
  - 真正建索引/写入（已执行，用户确认后完成，2026-08-22）：索引 `blog-search-v1`
    （1024d/cosine）已建，901 条向量已全部 upsert 成功；直接调 Vectorize v2 query API 验证——
    用库内一条向量本身查询，`score≈0.9999999` 命中自身且 metadata 完整可读，`vectorCount`
    确认为 901（诊断阶段手工测试时误用旧 id 方案真实写入过一条 stray 向量，已用
    `delete_by_ids` 清理）
- **涉及文件**：`semantic-search/scripts/build-vectorize-index.py`
- **风险/回滚**：涉及 Cloudflare 计费额度，实现前需按 `semantic-search/PLAN.md` §6
  重新核对当时的 Vectorize/Workers AI 定价与限额。**`--create-index`/`--upsert`（对应
  `wrangler vectorize create` 与写入操作）是真实账号级操作，执行前已停下问用户确认**
  （见 `architecture.md` 边界），脚本默认 dry-run，不会无人值守直接建线上资源。
- **对抗式自审（grade B，3 轮，独立上下文子 agent）**：正确性/安全/生产失败模式三个视角各查
  一遍，发现并修复：①语言判定 bug——`titleEn`/`descriptionEn` 是 SEO meta，不代表正文真有
  双语分段，原逻辑导致单语文章被错误双记/错误标语言（901 vs 原来错误的 946 记录数就是这个
  bug 的直接证据）；②补回批量 embedding 顺序校验（`verify_batch_order`，参考
  `vector-comparison.py` 已有的同类防护，这批向量直接进生产索引，风险比实验数据更高）；
  ③`embed_batch`/`upsert_vectors` 原本不捕获超时类 `URLError`，只捕获 `HTTPError`，扩大重试
  覆盖面；④`upsert_vectors` 原本无任何重试，已补上；⑤`create_index` 对"索引已存在"从崩溃
  改成识别并继续（支持部分失败后重跑）；⑥`--index-name` 加白名单校验，避免拼进 URL 路径的
  注入面；⑦真正执行 create/upsert 前打印 `account_id`/`index_name`/向量数供人工核对目标账号
  没指错；⑧新增向量缓存（gitignored），失败重跑不必重新花 Workers AI 额度重新 embed 全部
  文章。未修复、记入 `followups.md`：`CLOUDFLARE_REGISTRAR_TOKEN` 是否是给这类写操作过宽的
  共享凭据、值不值得换成 Vectorize/Workers AI 专用的窄权限 token（FU-7，2026-08-22 实测更新：
  用户已铸造新 token 并补齐 Vectorize:Edit + Workers AI:Edit 两条权限，当前用的就是这个新
  token，FU-7 的窄权限诉求已满足，遗留问题只剩"要不要把旧的 `CLOUDFLARE_REGISTRAR_TOKEN`
  全部改名/收回"，非阻塞）；脚本本身不做"先记旧再删"的增量更新，两次运行之间若文章内容被
  编辑会留下孤儿向量，正式的解决方案是 **T1.4.2**（FU-8——T1.4.1 交付时已明确"不清理孤儿向量"，
  2026-08-23 改派给 T1.4.2 的 Cron 对账逻辑，T1.4.2 目前 BACKLOG，这个兜底在它交付前不存在）。
- **真实执行中发现的平台限制（未在文档预判，靠实际调用暴露）**：Cloudflare Vectorize v2 的
  vector id 有 **64 字节硬上限**，原计划的 `article_id:language:content_hash` 拼接方案对长
  slug 文章会超限（实测某文章拼出 71 字节，首次 `--upsert` 直接 400）。已改为对完整逻辑 key
  （article_id+language+content_hash）取 SHA-256 前 48 位十六进制作为 vector id，长度恒定、
  仍然内容寻址/幂等，`article_id`/`language`/`content_hash` 完整保留在 metadata 里供人工排查。
  **T1.3.2 做段落级 chunk 时要延用同一个 `make_vector_id()` 哈希方案，不要再拼接可变长度的
  字符串做 id**。
- **证据**：分支 `feat/T1.3.1-vectorize-embedding`，PR [#39](https://github.com/MushroomDAO/blog/pull/39)
  （合并 commit `6b9fc8d`）。索引 `blog-search-v1`（1024d/cosine）已建，901 条向量
  （zh 467/en 434）已 upsert 并经 query API 验证可查询。
- **数据订正（2026-08-22，T1.3.2 review 反查发现）**：T1.3.2 的对抗式 review 发现本脚本
  用子串匹配检测 `<!--EN-->` 分隔符会被正文里的行内提及误触发（本库 2 篇文章：
  `seo-geo-skill-ai-citation-optimization`、`geo-generative-engine-optimization-guide`），
  导致这两篇的 article 级 embedding 在已执行的 `--upsert` 里用了错误的 zh/en 分段。已用
  PR [#44](https://github.com/MushroomDAO/blog/pull/44) 修复检测逻辑（要求分隔符独占一行），
  合并后已重新执行 `--upsert`（911 条向量全部刷新为正确数据），并精确重算出这两篇文章旧
  （有 bug 逻辑下产生的）4 个候选 chunk_id、用 `delete_by_ids` 清理，避免留下孤儿向量。
  线上索引现在是干净的。

### T1.3.2 分片与双语 chunk 策略实现  `DONE`
- **优先级**：high
- **目标**：按 `spec.md` 的数据模型，把文章切成段落级 chunk，中英文分开建索引（article 级
  chunk 是 T1.3.1 已经做的，不在这个 task 范围内）
- **开发范围**：分片逻辑（300–600 tokens，overlap 50–100，按 Markdown 结构切，每篇每语言上限
  16 chunk——文档未明确"每篇"还是"每语言"，按语言各自设上限，双语文章理论上限 32，
  见下方"文档未决问题"）、双语文章按独占一行的 `<!--EN-->` 拆分、`chunk_id` 生成（沿用
  T1.3.1 的哈希方案，加 chunk_type 维度避免和 article 级 chunk 撞 id）
- **明确不做**：不做代码块单独 embedding（围栏代码块整块剔除，不参与分片/token 计数）；
  不组装 url/title/tags/excerpt 等 metadata（T1.3.1 的索引脚本已有这套组装逻辑，接入索引
  流程时复用，不在本 task 重复实现）；不接入 Cloudflare（纯本地函数，无网络调用）
- **依赖**：T1.3.1
- **交付物**：`semantic-search/scripts/chunking.py`（`chunk_article()` 纯函数）+
  `semantic-search/scripts/test_chunking.py`（验收测试）
- **验收命令**：`python3 semantic-search/scripts/test_chunking.py`（对真实双语文章
  `adapta-self-hosted-local-knowledge-base-guide` 断言 zh/en 分布、chunk 数区间、id 唯一性、
  token 范围；另有 3 条回归测试专门盯住 review 抓到的真实 bug，见下）。全库 478 篇文章跑
  一遍分片：0 报错、0 篇超过每语言 16 片上限、0 篇产出 0 chunk、0 个标题孤儿 chunk；
  478 篇里有 2 篇的个别 chunk 略超 900 token（最高 1348）——这是"16 片硬上限"和"目标
  300-600 token"两个约束在极长文章上无法同时满足时的残留超量，已知且可接受，记入
  `followups.md`（FU-9），不是本次要修的阻塞项。
- **涉及文件**：`semantic-search/scripts/chunking.py`、`semantic-search/scripts/test_chunking.py`
- **风险/回滚**：无涉钱/涉账号操作（纯本地文本处理），可直接 `git revert`
- **对抗式自审（grade B，3 轮，独立上下文子 agent）**：正确性/边界场景/需求符合度三个视角，
  发现并修复 4 个真实 bug（前 2 个当前语料库里已经在真实触发，不是假设）：
  1. **尾部 chunk 无界增长**——原算法没把 overlap 重复的 token 算进预算，导致
     chunk 边界比预期提前用完 16 片上限，剩余内容全堆进最后一片（实测某文章尾部
     chunk 高达 1736 token，是目标上限近 3 倍）。修复：把 overlap_tokens 加回目标片段
     大小的预算里。
  2. **双语分隔符检测被行内提及劫持**——原来用子串匹配 `"<!--EN-->" in text`，本库
     真实有 2 篇文章在正文里用反引号引用这个分隔符字面量来说明博客的双语约定，导致在
     错误位置切开双语、大段中文内容被标成 `language=en`。修复：要求分隔符独占一行
     （`^<!--EN-->[ \t]*$`）。**这个 bug 同样存在于已合并、已执行过 `--upsert` 的
     T1.3.1 脚本里，另开 PR #44 热修复，线上索引里这 2 篇文章的旧向量已知是错的
     （已记录待用户决定是否重新 upsert）**。
  3. **标题孤儿 chunk**——标题块后紧跟一段超大正文时，断点会恰好落在标题和正文之间，
     产出一个只有标题、没有正文的无用 chunk，且这个标题会被 overlap 逻辑带到下一个
     chunk 重复出现一次。修复：不允许在"当前 chunk 只有标题、还没有正文"的状态下断开。
  4. **4 反引号转义围栏 + 单个超大 block 的 overlap 处理**——`markdown-style-guide.md`
     用 CommonMark 合法的"4 个反引号包住内部 3 个反引号示例"写法，原正则只认 3 个反引号，
     配对错乱、删掉中间真实内容。修复：反引号数量用反向引用要求首尾一致。同时修了
     overlap 逻辑——如果最近一个 block 自己就远大于 overlap_tokens，不整块搬去当 overlap
     （避免下一片一开始就严重超预算、和上一片高度重复）。
  非阻塞发现：CJK token 计数原来漏算中文标点（「」《》等），已扩大 CJK 判定范围；
  16-per-语言 vs 16-per-文章 的文档歧义未解决（见下）。
- **文档未决问题（非阻塞，供后续参考）**：`tasks.md`/`spec.md`/`architecture.md` 都没有
  明确说"每篇 12-16 chunk"这个预算是按整篇文章算，还是按文章里的每种语言各自算——本次
  实现按"每语言"处理（双语文章理论上限 32 chunk）。全库只有 3 篇文章总 chunk 数超过 16
  （最多 24），如果后续判断应该是"每篇"总量，需要重新调整 `MAX_CHUNKS_PER_LANGUAGE`
  的语义。
- **证据**：分支 `feat/T1.3.2-chunking-bilingual`，PR [#45](https://github.com/MushroomDAO/blog/pull/45)（合并 commit `b8f547b`）

### T1.3.3 `/api/search` Worker 端点 + 前端 RRF 融合  `DONE`
- **优先级**：high
- **目标**：query → Vectorize 向量检索 → 按 `article_id` 聚合去重 → 用 Vectorize 自身余弦
  相似度阈值过滤 → 返回候选列表（可能为空）。**关键词+向量的 RRF 融合与"没有找到"的最终
  判断不在这个端点内**——Pagefind 是纯浏览器端 JS，Worker 调不了，融合发生在 `/search`
  页面的浏览器 JS 里（见 `architecture.md` 核心判断 8、`spec.md` §检索融合）
- **开发范围**：
  1. `functions/api/search.js`：登录 Cookie 校验（复用 T1.3.6 的 `_lib/auth.js`，无/过期
     Cookie 返回 401）、Content-Type/body 大小/query 长度校验、按 IP 限速（复用
     `_lib/rate-limit.js`，扩展成支持自定义 prefix/window/次数，5 分钟 30 次，比登录限速
     宽松得多）、`@cf/baai/bge-m3` query embedding、`VECTORIZE_INDEX` 检索（topK 20）、
     按 `article_id` 聚合去重（保留分数最高的 chunk）、相似度阈值过滤（0.4，见下方阈值
     校准说明）、AI/Vectorize 调用失败时 fail-closed 503
  2. **前端 RRF 融合**（原本没有独立 task 号，本 task 范围内一并完成，否则后端接口做完
     用户仍然看不到能用的语义检索）：`src/pages/search.astro` 新增一个独立的语义检索输入框
     （登录后才显示，原有 PagefindUI 关键词搜索完全不动），用 Pagefind 原生 JS API
     （`/pagefind/pagefind.js`，不是 PagefindUI 组件——组件自己管结果渲染，混不进外部
     向量结果）取关键词排名，和 `/api/search` 的向量排名做 RRF 融合
     （`score = Σ 1/(60+rank)`），"两路都没有信号才展示没有找到"
  3. `wrangler.toml` 新增 `[ai]` binding（`AI`）+ `[[vectorize]]` binding
     （`VECTORIZE_INDEX` → `blog-search-v1`，T1.3.1 建的索引）
- **相似度阈值校准（0.4）**：`semantic-search/eval/vector-comparison-report.md` 的实测
  数据显示 24 条查询里所有 top5 结果的最低分是 0.401（bge-m3 在这批语料下余弦相似度分布
  本身比较"压缩"），且报告明确指出单靠这个分数分不清"该拒的负样本"和"该留的真命中"
  （"菜谱"/"育儿"两个负样本的最高分 0.4697/0.4794，跟真实相关查询的分数区间有重叠，
  参见 T1.2.1 报告"负样本上，向量检索比关键词检索更容易给出看似合理但边缘的匹配"一节）。
  阈值 0.4 只用来过滤掉"任何查询的 top5 都不会低到这里"的明显不相关尾部，真正的精确度
  判断交给前端结合 Pagefind 信号一起做（"无把握不返回"逻辑）——这个端点自身的绝对信号
  过滤刻意做得宽松，不是这里没做够精确校准。
- **明确不做**：不做 reranker（Phase 2 可选，T1.4.4）；不做真正意义上的"两路各自独立判断
  是否有靠谱结果"的精细阈值调优（用简化版：某一路有结果即视为该路"有信号"，见 search.astro
  注释）——这条留给后续用真实使用数据回头校准
- **依赖**：T1.3.2、**T1.3.6**（认证中间件必须先存在，`/api/search` 不能有无认证的中间上线
  状态——见 `architecture.md` 边界）
- **交付物**：`functions/api/search.js` + `functions/api/search.test.js`、
  `functions/_lib/rate-limit.js`（扩展支持自定义 prefix/window/maxAttempts，向后兼容
  T1.3.6 的登录限速调用不变）、`src/pages/search.astro`（新增语义检索输入框 + RRF 融合）、
  `wrangler.toml`（新增 AI + Vectorize binding）
- **验收命令**：`pnpm test`（57 项测试，含 search.js 21 项：无 Cookie/过期 Cookie 401、
  Content-Type/body 大小/query 长度校验、限速、AI/Vectorize 失败 503、按 article_id
  聚合去重只保留最高分、低于阈值过滤、全部低于阈值返回空数组、按分数降序排序、返回字段
  形状）+ `pnpm run build`（确认构建通过）+ 浏览器实测（Playwright：模拟登录态后输入框
  正确显示、debounce 后正确调用 Pagefind 原生 API 拿到真实结果并渲染高亮摘录、`/api/search`
  调用失败时优雅降级不报错、清空输入框正确清空结果）
- **涉及文件**：`functions/api/search.js`、`functions/api/search.test.js`、
  `functions/_lib/rate-limit.js`、`functions/_lib/rate-limit.test.js`、
  `src/pages/search.astro`、`wrangler.toml`
- **风险/回滚**：涉及公开 API 与 Workers AI/Vectorize 计费。本 task 已经内置基本防滥用
  （IP 限速 + 会话级限速 + query 长度上限 + body 大小上限，见下方对抗式自审），不是
  T1.3.4 完全空白的裸奔状态——T1.3.4 仍有价值（更精细的限速、常见查询缓存），但不再是
  "不做就不能上线"的前置条件。认证已由依赖 T1.3.6 保证，不会出现无认证窗口期。
  **真实验证（2026-08-22，合并后）**：PR #52 合并后 CI 自动部署失败（GitHub Actions 的
  `CLOUDFLARE_API_TOKEN` secret 失效，"Not logged in"——见下方发现的独立问题），改用本地
  `wrangler pages deploy` 手动部署。用真实登录 Cookie 对生产环境 `/api/search` 发送
  `{"query":"Pagefind"}`：返回 `PenguinHarness...` 排第一，分数 `0.5089695`——跟
  `vector-comparison-report.md` 里同一条查询记录的分数 `0.5043`（同一篇 `PenguinHarness`
  文章排第一）几乎一致（细微差异符合预期：报告里是整篇文档级别的对比，这里是 chunk 级
  聚合取最高分）。**证实 `env.AI.run()`（binding 调用）和建索引时用的原始 REST API 调用
  产出的是同一个嵌入空间的向量**，不存在事先担心的"绑定调用与 REST 调用内部参数不一致导致
  所有分数静默低于阈值"的问题。
- **对抗式自审（grade B，3 轮，独立上下文子 agent）**：正确性/安全滥用/生产失败模式三个
  视角，发现并修复：
  1. **前端搜索请求竞态**（正确性）——debounce 只延迟发起，不取消已发出的请求；快速输入
     两次搜索时，网络时序不保证后发出的请求先回来，旧请求的迟到响应会覆盖新请求已经渲染
     的结果，界面上出现输入框内容对不上的陈旧结果，且这个迟到响应如果恰好是 401 还会
     错误地把仍然在线的用户切回登录表单。改用单调递增的 generation 计数器，只有仍是最新
     一轮的请求才允许渲染或触发副作用。
  2. **限速只按 IP，泄露的 Cookie 换 IP 能绕过**（安全/滥用）——本项目登录会话 60 天
     有效期且明确不做撤销/登出接口，只按 IP 限速意味着攻击者换着代理 IP 打就能让同一个
     泄露的 Cookie 反复触发计费的 Workers AI + Vectorize 调用，总量没有上限。加了一个按
     会话（登录 Cookie 值的 SHA-256 哈希，不存明文）算的限速，跟 IP 限速同时生效（两者
     都要过），把单个泄露 Cookie 的最坏成本钉死在一个窗口内的固定次数，不再随攻击者能
     换多少个 IP 线性增长。
  3. **`Content-Length` 请求头可以撒谎**（生产失败模式，低严重度但修复成本低）——原来
     只检查这个头就放行到 `request.json()`，chunked encoding 或者故意谎报成一个很小的值
     都能绕过体积上限检查。改成先读成文本量实际字节数，两道检查都做。
  4. （非阻塞，已在响应字段上加防御性 `?? ''`）Vectorize 返回的 metadata 理论上不该缺
     字段，但脏数据不该产出 `undefined` 悄悄从 JSON 里消失；`match.score` 非有限数时
     也不该参与聚合比较，一律当"没有可用信号"跳过。
  5. （非阻塞，记入 followups）`functions/api/search-auth.js`（T1.3.6，已合并）有同样的
     "只信 `Content-Length` 头"问题——同一个修法，但那是已经上线、已经过评审的代码，
     严重度更低（登录接口本身已经有 `MAX_PASSWORD_LENGTH` 兜底实际损耗），记进
     `followups.md` 而不是在这个 PR 里顺手重开那个 task 的范围。
  6. （非阻塞，记入 followups）成本层面的建议：给 Workers AI + Vectorize 配置用量告警，
     作为限速本身之外的兜底——限速的 KV 最终一致性弱点（已知局限，见 rate-limit.js 注释）
     在这个端点上第一次有了实际的 $ 维度。
- **证据**：分支 `feat/T1.3.3-search-endpoint`，PR [#52](https://github.com/MushroomDAO/blog/pull/52)

### T1.3.4 API 防滥用（限速/输入上限/缓存/降级）  `DONE`
- **优先级**：high
- **目标**：`/api/search` 具备基本防滥用能力，不被刷爆 Workers AI 额度
- **开发范围**：输入长度上限、简单限速、常见查询缓存、不记录用户原始查询原文。"降级"体现在
  前端：`/api/search` 超时/失败时浏览器 JS 只展示本地 Pagefind 结果，不是 Worker 侧逻辑
  （Worker 里没有 Pagefind 结果可回退，见 T1.3.3）
- **实际完成情况**：这几项里的大部分（输入长度上限、IP+会话双重限速、"降级"前端逻辑）已经
  在 T1.3.3 落地时一并做了（见 T1.3.3 条目"风险/回滚"一节的说明），本 task 认领的是剩下的
  一项——**常见查询缓存**（`functions/api/search.js`）：query 归一化（trim+小写）取
  SHA-256 哈希做 KV key，6 小时 TTL，命中直接跳过 AI/Vectorize 调用；"不记录用户原始查询
  原文"通过缓存 key 用哈希而不是明文查询词本身满足——缓存值里也只有文章标题/链接/摘录，
  不含查询词。**订正（2026-08-23，FU-20）**："降级"这一项当时其实没有真正兑现：
  `search.astro` 的 `searchVectorRanked` 缺一个 `.catch`，fetch 层网络失败/响应体非法
  JSON 会让整轮搜索直接抛异常，连已经拿到的 Pagefind 结果也不渲染——这跟"超时/失败时只
  展示本地 Pagefind 结果"的说法正好相反。这个缺陷在 PR#52/#55/#57 三轮评审里都提过，但
  直到 F1.3 收工时同步文档才正式记入账本（FU-20），并在 PR#58 里用 review 验证过的
  一行修法（`.catch(() => ({ expired: false, results: [] }))`）关闭（PR#61 去掉整个登录
  门禁后，`expired` 这个概念不再需要，`searchVectorRanked` 改成返回
  `{ results, rateLimited }`（`rateLimited` 用来单独提示 429，见 search.astro 的
  429 处理说明），调用方的 fallback 相应改成
  `.catch(() => ({ results: [], rateLimited: false }))`——**订正（2026-08-23，round 2
  复审指出这里写错）**：曾经错误地把这个 fallback 简化描述成 `.catch(() => [])`，那样写
  会让 `runCombinedSearch` 读 `vectorOutcome.results` 时拿到 `undefined`、整轮合并崩掉，
  跟 FU-20 当初 `.catch(() => null)` 的坑是同一个形状；已订正为跟代码逐字一致的写法）。
  **例外（2026-08-23，feat/public-search-no-auth round 2
  review 指出台账自相矛盾）**：这条"不记录原始查询原文"只覆盖 T1.3.4 自己的查询结果
  缓存这一处；feat/search-usage-analytics（用户明确要求的搜索使用统计功能）往
  Analytics Engine 写的 `logSearchEvent` 存的就是归一化后的查询**原文**，是刻意的、
  跟这条不是同一个诉求（缓存层面尽量少存不必要的明文 vs 站长本人明确要求要看到"搜了
  什么"的可读运营数据，见 followups.md FU-25），但字面读起来会让人以为这个仓库全局不存
  明文查询词，容易误导，在这里明确记一笔例外。
- **明确不做**：不做验证码类交互防护（超出必要）；登录认证不在本 task 范围内，见 T1.3.6
- **依赖**：T1.3.3
- **交付物**：`functions/api/search.js` 里新增的缓存逻辑 + `functions/api/search.test.js`
  新增 5 项测试
- **验收命令**：`pnpm test`（含新增 5 项缓存测试：缓存命中依然计入限速、限速额度内的
  缓存命中跳过 AI/Vectorize 即使它们会报错、大小写/空白归一化命中同一条缓存等）
- **涉及文件**：`functions/api/search.js`、`functions/api/search.test.js`
- **风险/回滚**：涉钱（Workers AI 按量计费）——T1.3.3 已经内置基本防滥用，本 task 上线前
  `/api/search` 并非裸奔状态，缓存是在那基础上的进一步降本。缓存本身失败（KV 读写异常）
  降级成"当作没命中"，走正常查询流程，不影响功能正确性，只是没省到钱。
- **顺带修复（同一个 PR 里，跟 T1.3.4 关系紧密，未单独开 task）**：`functions/api/
  search-auth.js`（T1.3.6，已合并）的 Content-Length 只信请求头、chunked encoding 或
  谎报长度可绕过体积上限的问题（FU-12）——用跟 `search.js` 一样的修法（读完 body 量
  实际字节数，不只信头）关闭。
- **对抗式自审（grade A——涉 search-auth.js 安全面，3 轮，独立上下文子 agent）**：正确性/
  安全/生产失败模式三个视角，发现并修复：
  1. **缓存命中原来完全不计入限速**（安全，真问题）——设计初衷是"缓存读取不花计费调用、
     不该占限速额度"，但忽略了这个 KV namespace 同时扛着 T1.3.6 的登录限速器，不限速的
     缓存读流量能把共享 namespace 的 KV 配额打满，是另一种拒绝服务面，不是"省钱"这个
     威胁模型要挡的东西。改成限速检查挪到缓存检查之前——命中缓存依然计入限速，只是
     跳过真正计费的 AI/Vectorize 调用，两个目标（省钱、不被刷）不冲突。
  2. **TTL 理由写错了**（正确性，自己代码注释的事实错误）——原注释说"文章更新频率也是
     以天为单位"，但 `git log` 显示单日发布过 14 篇文章，这个理由站不住。改成如实说明
     6 小时是"省计费调用"和"新鲜度"的折中，新鲜度上限目前实际由还没上线的 T1.4.1 决定
     （记入 followups FU-17，供 T1.4.1 实现时参考）。
  3-6.（非阻塞，记入 followups）缓存 key 归一化偏弱（FU-16）、缓存无失效钩子对接
     未来的 T1.4.1 重新索引（FU-17）、缓存写入增加 KV namespace 级配额消耗（FU-18）、
     `rate-limit.js` 的 `checkAndIncrement` 对 KV 调用没有 try/catch、既有代码本次未改
     但缓存新增的写入量让它更容易触发（FU-19）。
- **证据**：分支 `feat/T1.3.4-search-caching`，PR [#55](https://github.com/MushroomDAO/blog/pull/55)（合并）。
  Round 2 review 在后续 `fix/rate-limit-and-cache-hardening` 分支上发现 FU-16 的初次修复本身有
  真实 bug——归一化只用在算缓存 key，传给 `env.AI.run()` 的还是原始未归一化的 query，两个语义
  等价的查询在缓存层判成"同一条"但在 embedding 层并不等价——已用 PR
  [#57](https://github.com/MushroomDAO/blog/pull/57)（合并）修复：归一化改到请求解析时做一次，
  之后缓存 key 和 embedding 输入用同一个字符串；顺带加了缓存 key 版本前缀（避免旧规则缓存条目
  语义混淆）、`Array.isArray` 校验（防止脏缓存数据原样透传给前端）、`rate-limit.js` 的
  `checkAndIncrement` 补 try/catch（FU-19，fail-closed）。

### T1.3.5 索引 manifest 版本化  `DONE`
- **优先级**：mid
- **目标**：记录 `embedding_model`/`embedding_dimensions`/`chunking_version`/`content_hash`/
  `language`/`indexed_at`，为后续模型/分片算法变更做好回填切流的准备
- **开发范围**：manifest 存储用 **Cloudflare KV**（不是 D1——只需要按 key 读写一条小 JSON
  记录，不需要跨记录 JOIN，KV 比 D1 的 schema/迁移更简单）+ 读写逻辑；每篇文章一条记录
  （按语言分开记录 content_hash，不是每个 paragraph chunk 一条）
- **明确不做**：不做多版本并行 A/B（超出当前需要）；不做增量对账逻辑（T1.4.2 的范围，
  本 task 只管记录数据，不管拿数据去判断"要不要重新索引"）
- **依赖**：T1.3.1
- **交付物**：`semantic-search/scripts/manifest.py`（默认 dry-run，`--create-namespace`/
  `--write` 才真正动 Cloudflare 账号）+ `semantic-search/scripts/test_manifest.py`
- **验收命令**：`python3 semantic-search/scripts/test_manifest.py`（构造逻辑单元测试）+
  `python3 semantic-search/scripts/manifest.py --from-plan
  semantic-search/eval/vectorize-index-plan.json`（对全库 478 篇文章跑一遍 dry-run，
  断言产出 478 条文章记录 + 1 条 global 记录，不碰账号）
- **涉及文件**：`semantic-search/scripts/manifest.py`、`semantic-search/scripts/test_manifest.py`
- **风险/回滚**：涉及 Cloudflare 账号（建 KV namespace + 写入）。**`--create-namespace`/
  `--write` 执行前必须停下问用户确认**，脚本默认 dry-run，不会无人值守直接建线上资源。
- **对抗式自审（grade B，3 轮，独立上下文子 agent）**：正确性/安全/生产失败模式三个视角，
  发现并修复 6 个问题：
  1. **`_global` 保留 key 冲突崩溃**——如果哪篇文章 slug 恰好叫 `_global`，会和内部保留的
     全局配置 key 撞车，产出裸 `KeyError`。改成显式拒绝并报清楚的错误。
  2. **URL 里 `?`/`#` 导致 key 被截断、可能覆盖另一篇文章的记录**——key 直接拼进 URL
     没做编码，`existing-slug?evil=1` 这类（理论上的）slug 会被 HTTP 层当成查询参数，
     实际写入的 key 被截断。改成 `urllib.parse.quote` 编码 + `validate_key_name` 也拒绝
     `?`/`#`，双重防护。
  3. **建 namespace 的真实 mutation 排在账号确认打印之前**——`find_or_create_namespace`
     内部直接发 POST 建资源，跟 T1.3.1 建立的"mutation 前先打印账号"纪律不一致。改成
     创建前的日志行带上 `account={ACCOUNT_ID}`。
  4. **跨账号复用本地缓存的 namespace id**——缓存文件原来只存一个裸 id，换账号跑会拿旧
     账号的 id 去撞新账号（Cloudflare 会因为 id 不属于该账号报错，不会静默写错账号，但
     报错信息很难看出真正原因）。改成缓存里带上 `account_id`，读的时候校验一致。
  5. **最终失败不打印 Cloudflare 返回的错误详情**——4 次重试全失败时原来直接裸 raise，
     操作者看不到错误码/message。跟 `build-vectorize-index.py` 的 `upsert_vectors` 保持
     一致，加上失败详情打印。
  6. **namespace 列表查询没处理分页**——账号里 namespace 数量较多时可能漏掉已存在的
     `blog-search-manifest`，`--create-namespace` 建出重复同名 namespace、两份数据不同步。
     改成翻完全部分页再判断。
  非阻塞：进度日志的报告粒度从每 50 条改成每 20 条（跟 T1.3.1 的批量粒度对齐，缩小失败
  定位的误差范围）；畸形 plan 文件（不是 list、也没有 `plan` key 的 dict）原来会在
  `build_manifest` 里炸出不知所云的 `TypeError`，改成在 `main()` 提前报清楚的错误。
- **证据**：分支 `feat/T1.3.5-index-manifest`，PR [#47](https://github.com/MushroomDAO/blog/pull/47)（合并）

### T1.3.6 登录认证（密码 + 签名 Cookie）  `DONE`
- **更新（2026-08-23，PR #61）**：`/api/search` 的登录门禁已**取消**（语义检索现在和关键词
  搜索一样公开，滥用防线改由 T1.3.4 已有的 IP 限速承担）。以下开发范围描述是 T1.3.6 当初
  落地时的真实状态，历史记录不改写；本 task 产出的认证中间件（`_lib/auth.js` 等）**没有被
  删除**，改为只挂在 `/api/search-analytics.json`（登录后查看搜索统计）和未来的 AI 对话
  功能上。详见 `architecture.md` 核心判断 7 的"更新"段落、followups FU-27。
- **优先级**：high
- **目标**：`/api/search`（语义检索能力）在真正上线前必须有登录门禁，未登录不可访问，避免被刷
  Workers AI 计费。用户已明确否决 Cloudflare Access，要求单一共享密码方案。**T1.1.3 已上线的
  纯 Pagefind 关键词搜索页面不在门禁范围内，继续公开**（用户顾虑的是付费 API 被刷，不适用于
  零成本的关键词搜索，见 `architecture.md` 核心判断 7）。
- **开发范围**：
  1. `POST /api/search-auth`（`functions/api/search-auth.js`）：常量时间比较
     `env.BLOG_SEARCH_PASSWORD`，成功签发 HMAC-SHA256 签名 Cookie（payload
     `{v, issuedAt, expiresAt}`，密钥 `env.BLOG_SEARCH_SESSION_SECRET`，base64url 编码），
     Cookie 属性 `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=60天`
  2. Cookie 签发/校验共享逻辑（`functions/_lib/auth.js`，供未来 T1.3.3 的 `/api/search`
     引用）：校验签名与过期时间，未通过返回 401
  3. 登录接口限速（`functions/_lib/rate-limit.js`）：同 IP 15 分钟内最多 5 次，KV 计数器，
     跟 T1.3.5 的索引 manifest 共用同一个 KV namespace（key 加 `ratelimit:` 前缀区分，
     避免为限速单独建一个 namespace）
  4. `/search` 页面（`src/pages/search.astro`）：新增"语义检索"区块，无有效登录态时展示
     密码输入表单；页面本身的 Pagefind 关键词搜索框完全不受影响，继续公开
  认证校验逻辑封装成独立模块，便于以后替换成其他方案（见 `architecture.md` 核心判断 7）
- **明确不做**：不做多用户账号体系、不做 MFA、不用 Cloudflare Access、不做密码找回/自动轮换；
  不做服务端登出接口（前端"重新登录"链接只清本地 UI 提示，不撤销真实 Cookie——撤销靠轮换
  `BLOG_SEARCH_SESSION_SECRET`，见 spec.md）；不接 T1.3.3 的 `/api/search`（那个端点还不存在）
- **依赖**：T1.3.1（需要 Cloudflare Pages Functions 项目骨架存在）——**不依赖 T1.3.3**，本 task
  先于/独立于 `/api/search` 落地，反过来是 T1.3.3 依赖本 task 的中间件（见 `architecture.md`
  边界，避免 `/api/search` 出现无认证的中间上线状态）
- **交付物**：`functions/_lib/auth.js`、`functions/_lib/rate-limit.js`、
  `functions/api/search-auth.js` + 对应 `*.test.js`、`src/pages/search.astro` 登录态 UI
- **验收命令**：`pnpm test`（= `node --test functions/_lib/*.test.js functions/api/*.test.js`，
  36 项单元/集成测试，直接调用 `onRequestPost` 等 handler，不需要 wrangler/Miniflare；已接入
  `.github/workflows/deploy.yml`，部署前自动跑一次）+ `pnpm run build`（确认 Astro 静态构建
  不受影响，Pagefind 关键词搜索保持公开）
- **涉及文件**：`functions/_lib/auth.js`、`functions/_lib/rate-limit.js`、
  `functions/api/search-auth.js`、对应测试文件、`src/pages/search.astro`
- **风险/回滚**：**`wrangler secret put BLOG_SEARCH_PASSWORD` / `BLOG_SEARCH_SESSION_SECRET`
  是真实账号级操作，执行前必须停下问用户确认**（两个值已在 `~/Dev/.env` 里生成好，见
  `spec.md` §登录会话）；密码/签名密钥不可写入代码仓库或日志；`BLOG_SEARCH_KV` binding
  需要 T1.3.5 建的 KV namespace 存在。**部署时机提醒（非阻塞，运维注意事项；2026-08-22
  更新：本仓库已停用 CI 自动部署，`chore/manual-deploy-only`，部署只走本地
  `./deploy.sh`）**：本地 `./deploy.sh` 推送到 main 之后手动执行时会把 `functions/`
  一起发布，如果合并早于 Cloudflare Pages 后台配置好这三个环境变量/绑定，登录接口会
  短暂返回 503（`search auth not configured`）——代码本身是 fail-closed 的（不会崩溃、
  不会放行、不泄露具体缺了哪个变量），只是功能在配置补齐前不可用，不是安全问题，但
  建议合并后尽快去 Cloudflare Pages 后台配置、并手动跑一次部署。
- **对抗式自审（grade A——涉密钥/认证，3 轮，独立上下文子 agent）**：密码学正确性/滥用与信息
  泄露/集成与生产失败模式三个视角，发现并修复 6 个问题：
  1. **`timingSafeEqual` 注释和实现不一致**——注释说"先摘要再比较"，代码实际直接比较变长字节
     数组，运行时间随输入长度变化（实测候选串更短时耗时由真实密码长度决定）。这个部署形态下
     不构成实际可利用攻击（Cloudflare 网络抖动是毫秒级，这里是纳秒级差异，且限速卡 5 次/15
     分钟），但修起来成本很低——改成两边先各自 SHA-256 摘要成定长再比较，从根上消掉长度相关的
     计时差异。
  2. **`CF-Connecting-IP` 缺失时所有请求共享同一个字面量 "unknown" 限速桶**——真实 Cloudflare
     边缘流量这个 header 由平台权威写入、客户端伪造不了，但 header 缺失时（本地
     wrangler dev 等场景）不相关的调用方会共享同一个桶、互相锁出去。改成缺 header 时跳过
     限速，不参与共享桶。
  3. **请求体大小在解析前没有兜底**——`MAX_PASSWORD_LENGTH` 只挡 `password` 字段自己的长度，
     一个塞了大量无关字段撑大 body 的请求会被完整解析完才发现密码没超长，白白吃掉解析开销。
     加一个 `Content-Length` 检查，body 明显超出预期时不进 `request.json()`（诚实说明：这只
     挡"如实声明了 Content-Length"的请求，挡不住谎报/不带 Content-Length 的请求，那类仍靠
     Cloudflare 平台自己的请求体上限兜底）。
  4. **`verifySession` 从没校验签发时写进 payload 的 `v` 版本字段**——加上校验，纯防御性，
     不影响当前行为，是为以后升级 payload 结构留的口子。
  5. **前端 localStorage 登录态提示永不过期**——真实 Cookie 是 60 天有效期，用户手动清过 Cookie
     或者过了 60 天，页面会一直显示"已登录"、表单被隐藏，且没有任何入口能纠正（HttpOnly
     Cookie 前端读不到，无法自证）。改成提示带时间戳、55 天信任窗口过期自动失效，并加一个
     "不是你？重新登录"链接，不依赖提示本身准不准。
  6. （非阻塞，记入 followups）部署时机：合并早于 Cloudflare Pages 后台配置好环境变量/绑定
     时，登录接口会短暂 503——代码已经是 fail-closed，只是提醒运维顺序，见上方风险/回滚。
- **外部评审（PR#48，3 轮）**：
  - **R1**：2 blocking（B1 限速计数点在请求体校验之前，跨站垃圾请求可烧光真实用户的限速
    额度；B2 文档写 `BLOG_SEARCH_KV` "必需"、实现却在缺失时静默跳过限速直接放行到密码
    比较）+ 1 medium（Cookie 无 `__Host-` 前缀，可被兄弟子域用同名域 Cookie 影子化）+
    3 low（"重新登录"措辞误导、503 前端显示成"密码错误"、验签不查签发合理性）——
    全部修复：限速计数挪到请求体校验之后；KV/IP 缺失一律 fail-closed 503；Cookie 改名
    `__Host-blog_search_session`；措辞改"重新输入密码"；前端 503 单独分支；`verifySession`
    加 `expiresAt>=issuedAt`/90 天上限/5 分钟时钟容差三条不变式。
  - **R2**：B1 仅部分修复——`Content-Type: text/plain` 且 body 恰好是合法 JSON 的跨站请求
    仍能绕过（`request.json()` 不检查 Content-Type，而 text/plain 是跨站简单请求免 CORS
    预检能发送的三种 Content-Type 之一）。修复：请求体解析前显式要求
    `Content-Type: application/json`。
  - **R3（增量复审）**：因监控脚本读到的是 R2 修复前的评审快照、误判为新裁决而短暂复核了
    同一条 B1——实际 R2 的修复（Content-Type 校验）已经关闭该口子，最终针对最新提交
    `b3438f7` 的裁决为 **APPROVED**（`checks=SUCCESS`，`mergeable=MERGEABLE`）。
  - 全程新增 9 条回归测试（含 B1/B2 两条阻塞项守卫 + `text/plain` 攻击形状专项测试），
    并顺带把 `pnpm test` 接入 `.github/workflows/deploy.yml`（部署前自动跑），
    36 测试全绿。
- **证据**：分支 `feat/T1.3.6-login-auth`，PR #48（已合并，squash commit `423d7eb`）

---

## F1.4 — 自动更新与增强（Phase 2，依赖 F1.3 全部 DONE）

### T1.4.1 发布流程接入增量索引 hook  `DONE`
- **优先级**：high
- **目标**：`deploy.sh` / blog-publisher skill 发布成功后，自动触发新增/变更文章的增量索引
- **开发范围**：发布流程末尾加一步 hook 调用，生成/更新 `search-manifest.json` 并触发索引
- **明确不做**：不做失败重试的复杂退避策略（交给 T1.4.2 的 Cron 对账兜底）；不清理孤儿向量
- **依赖**：F1.3 全部 Task DONE（**2026-08-23 已满足**——T1.3.1~T1.3.6 全部 DONE，PR #57 是
  F1.3 范围内最后一个合并的 PR）
- **交付物**：`semantic-search/scripts/incremental-index.py`（新，只对变化的 article/language
  重新 embed+upsert，其余复用 `build-vectorize-index.py`/`manifest.py` 的既有函数）+
  `scripts/publish-blog.sh` 新增 `[4.7]` 步骤调用它（真正的挂钩点是 canonical 发布脚本
  `scripts/publish-blog.sh`，不是 `deploy.sh`——后者是整站构建部署，不是单篇文章发布流程）
- **验收命令**：发布一篇测试文章后，短时间内 `/api/search` 能查到它（**代码已合并，
  live 端到端验证仍待第一次真实发布触发——当前 `CLOUDFLARE_REGISTRAR_TOKEN` 缺 KV 列
  命名空间权限（401），只读 diff 路径对生产账号没能跑通，见下方"证据"。首次真实发布
  这条 hook 时需要留意日志里的 `[4.7]` 那一段，失败不影响发布但文章会暂时搜不到，见
  PR #63 body 的自测记录）**
- **涉及文件**：`semantic-search/scripts/incremental-index.py`、
  `semantic-search/scripts/test_incremental_index.py`、`scripts/publish-blog.sh`
- **风险/回滚**：改动发布流程需谨慎，不能影响现有博客发布主流程——已用 `if`/`else` 包住调用，
  索引失败不会因为 `set -euo pipefail` 而中断已完成的 git commit/push；出问题可直接注释掉
  `publish-blog.sh` 的 `[4.7]` 段落回滚
- **证据**：PR [#63](https://github.com/MushroomDAO/blog/pull/63)（合并，squash `ad6a58e`）。
  3 轮独立子 agent 对抗式自审（正确性/安全/生产失败模式）：正确性发现 `do_upsert` manifest
  合并用了循环前旧快照导致新双语文章两个语言互相覆盖的真 bug（已修复+回归测试）；安全发现
  `--slug` 未校验存在路径穿越/绝对路径覆盖（已加白名单正则+回归测试）；生产失败模式无阻塞项。
  外部评审 2 轮：R1（CHANGES_REQUESTED）抓到真阻塞项——`upsert_vectors` 返回 HTTP 200 +
  `success=false` 不抛异常，manifest 会被无条件写入,永久误判为"已索引"但向量其实没写进去；
  已修复（`build-vectorize-index.py` 同款孪生 bug 一并修）+ 加了拆掉守卫会失败的回归测试
  （reviewer 实测验证过）。R2 APPROVED。`pnpm test` 83/83、`test_incremental_index.py`
  21/21 通过。

### T1.4.2 Cron Trigger 每日对账  `DONE`
- **优先级**：mid
- **目标**：每日比对 manifest 与索引内容的 `content_hash`，修复漏索引文章、清理已删除文章的
  残留向量（T1.4.1 交付时把孤儿清理明确改派给了这个 task，见 T1.4.1 证据/FU-8）
- **开发范围**：拆成两半——① 对账逻辑（Python 脚本，复用 `incremental-index.py` 已有的
  diff 路径，新增"反向"扫描：manifest KV 里有、本地 `.md` 没有的条目 = 孤儿，删对应向量 +
  删 manifest 记录）；② 每日自动触发的机制
- **明确不做**：不做主触发（发布即触发是 T1.4.1 的职责，已交付）
- **依赖**：T1.4.1（已满足，PR #63 已合并）
- **交付物**：`semantic-search/scripts/reconcile.py`（新）+ `manifest.py` 补
  `list_manifest_keys`/`delete_kv_entry`（对账要"列出全部 key"和"删记录"，之前只有单条
  读写）
- **验收命令**：`<待实现时补充：手动删一篇已发布文章后跑一次对账，确认 Vectorize 里的
  对应向量和 manifest KV 记录都被清理，且未受影响的文章不受影响>`
- **涉及文件**：`semantic-search/scripts/reconcile.py`（新）、
  `semantic-search/scripts/manifest.py`、`semantic-search/scripts/test_reconcile.py`（新）
- **风险/回滚**：`delete_by_ids`/KV 删除是真实账号级破坏性操作（数据删除），比 T1.4.1 的
  "只增不减"风险更高——脚本默认 dry-run（只打印会删什么，不真删），真删需要显式
  `--delete-orphans` 且需要 `CLOUDFLARE_REGISTRAR_TOKEN`/`ACCOUNT_ID`，跟既有的
  `--create-index`/`--upsert`/`--write` 是同一套纪律
- **待决问题（不猜，等用户拍板）**："每日自动触发"具体怎么实现，有两个真实候选，架构含义
  不同：(a) 部署一个**独立的 Cloudflare Worker**（不是现有的 Pages 项目——Pages Functions
  不支持 Cron Trigger，这必须是单独的 `wrangler deploy`，新建一份持久化云端资源，往后每天
  自动跑，脱离本机存在）；(b) 复用本仓库已有的"本机 cron 跑脚本调 Cloudflare API"模式（跟
  `scripts/update-analytics.sh` 同款——本机 launchd/cron 定时跑 `reconcile.py`，不新建任何
  Cloudflare 资源，缺点是依赖本机在线）。**本 task 只交付对账逻辑本身（dry-run 默认，真正
  删除需显式确认），不擅自选边、不部署任何新 Cloudflare 资源**——部署一个新 Worker 属于
  "真实账号级、持久化、无人值守之后自动执行删除操作的基础设施"，跟 architecture.md 里
  "wrangler vectorize create/secret put 之前必须停下来问用户"是同一类决策，不是脚本代码
  层面能替用户拍的板
- **接自动触发前的硬性前提（review 抓到的真实风险，不是这个 task 现在要做的，但必须写死
  在这里，免得下一个接手的人漏掉）**：`reconcile.py` 现在只有一个"全空目录"的地板检查
  （`articles` 为空直接退出），**没有比例上限**——如果它是被本机 cron 定时驱动、而那个
  checkout 恰好是落后于 main 的旧 worktree（本仓库确实同时开着好几个 worktree，各自
  停在不同 commit，是真实存在的模式，不是假设），旧 checkout 缺的那些新文章会全部被误判
  成孤儿、`--delete-orphans` 会真的删掉。**谁来接"每天自动触发"这部分，必须先加一个
  比例/数量上限**（比如"孤儿数超过 manifest 总数的 X% 就拒绝执行、只报告不删"或类似的
  二次确认），而不是让 `--delete-orphans` 在无人值守场景下对任意大小的误判结果照单全删。
  本 PR 的 `reconcile.py` 目前只给人工操作者用，人工执行时会先看 dry-run 输出的孤儿清单
  再决定要不要加 `--delete-orphans`，所以现阶段没有这个上限是可接受的——一旦接了自动
  触发，人工看一眼这一步就没有了，必须补上机械的比例上限。
- **证据**：PR [#65](https://github.com/MushroomDAO/blog/pull/65)（合并，squash `f9a61a4`）。
  3 轮独立子
  agent 对抗式自审（正确性/安全/数据安全-破坏性操作，因为这是本仓库第一个真的会删数据的
  脚本，专门为此加了一轮）：正确性发现 2 个 HIGH bug——`delete_by_ids` 返回
  `success=false` 未检查就推进删 manifest（已修复）、孤儿判定用了 frontmatter 解析成功
  后的子集而不是原始文件列表（已修复，加了临时目录回归测试）；数据安全发现真实存在的
  `.mdx` 索引盲点（本仓库确有一篇发布中的 `.mdx` 文章未被三个索引脚本的 glob 覆盖，已
  统一修复）+ 比例上限缺口（已记入本条"接自动触发前的硬性前提"，不在本 PR 实现）。
  `pnpm test` 83/83、`test_reconcile.py` 11/11 通过。**外部评审 REQUEST_CHANGES**，抓到
  2 个真阻塞项：① `find_orphans` 没考虑 `BLOG_SEARCH_KV` 是
  manifest/`ratelimit:`/`searchlimit:`/`searchcache:v2:` 四种用途共享的同一个 namespace，
  把非 manifest 形状的 key 也当孤儿，`delete_orphans` 读到 `int`/`list` 直接
  `AttributeError` 崩溃——而且排序上非 manifest key 往往靠前，真正的孤儿因此永远清不到，
  这也推翻了"不加比例上限是因为人会先看 dry-run 清单"的前提（清单会被无关 key 淹没）。
  已改成白名单判定（只有读出来是 dict 且有 content_hash 字段的 key 才算孤儿候选，其余
  跳过并打印说明），加了混入 `ratelimit:`/`searchcache:v2:` key 的回归测试。② 原
  `if chunk_ids:` 只包住 `delete_by_ids`，`delete_kv_entry` 在 if 块外无条件执行——
  `content_hash` 缺失/空 dict 时 0 个向量被删，manifest 记录却照删，docstring 承诺的
  "容错跳过"没有真的发生。已改成早退守卫，加了空 `content_hash` 的回归测试。另外两条非阻塞
  项：`delete_by_ids` 是异步的，`success=true` 只代表"已受理"不是"已完成"，日志措辞已改
  （`accepted delete of N vector(s)`）；"编辑文章后旧向量从不清理"是 FU-8 最初就点名的
  第三类场景，本 PR 目前没覆盖（只覆盖了漏索引和文章删除两类），记入 FU-32，非阻塞但
  应尽快单独补。**外部评审 APPROVED**（两个 High 都用重跑原实验+变异测试验证过修复真的
  承重）；剩一条 Low：`mutationId` 日志读了 `result.get('mutationId')`，但 Cloudflare v4
  信封是 `{"success":…, "result":{…}}`，`mutationId` 在嵌套的 `result["result"]` 里，
  永远打印 `None`——已在本 PR 合并后的小型 chore PR 里单独修复（不想在已拿到 APPROVE
  后再推 commit 让评审失效重来一轮）。

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
