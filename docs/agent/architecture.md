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
   拆成独立 chunk，共享 `article_id`。**"按查询语言过滤"是查询侧过滤，不是索引侧屏蔽**：
   同语言 chunk 优先，同语言召回不足时仍可补召跨语言 chunk（呼应核心判断 6 的
   EN/ZH 一致性发现）——真正硬性排除的只是"中英文内容压进同一条向量"这个索引形态。
5. **全部复用 Cloudflare 托管能力**：Pagefind（构建时）+ Workers AI（embedding/可选 LLM）+
   Vectorize（向量存储）+ Workers（API）+ Cron Trigger（对账），不引入额外账号/服务。
6. **T1.2.2 裁定（2026-08-21，go，混合方案，非纯向量替代；理由已订正见下）**：
   `vector-comparison-report.md` 显示纯向量单独替代关键词不成立（精确技术名词查询会退步、
   负样本更容易给出误导性匹配）。向量检索**真实、可复现的优势场景**（订正版，2026-08-22
   review 指出原记录的"跨语言"机制有误）：
   - **同语言内的词汇/同义词鸿沟**：#11「脑仿真 大脑连接组」全库检索命中 0，但语义相关的
     "全脑模拟""连接组"文章确实存在——两篇候选文章其实中英文标题都有，Pagefind 两种语言
     都索引了，真正的差距是具体措辞不同，不是语言边界（详见 `vector-comparison-report.md`
     核心发现 1 的订正说明、`baseline-results.md` #11）
   - **EN/ZH 同主题查询结果一致性**（这条才是货真价实的跨语言证据）：中文查询与对应英文
     查询在向量检索下 top5 高度一致，关键词检索下差异悬殊（#15/16、#7/20）
   - **松散概念性提问**（#10「有没有讲 Agent 循环设计的文章」等）
   裁定结果：两个都要，**关键词与向量并行检索 + RRF（Reciprocal Rank Fusion）融合排序**，
   不是"选一个用"，也不是"关键词优先向量兜底"的条件分支——每次查询两路都跑，
   融合发生在浏览器端（见系统骨架与 `spec.md` §检索融合，理由见核心判断 8）。
   **评测方法论的局限**：本次评测（`vector-comparison.py`）对每篇文章只生成一条中英文混合的
   单一向量、全程未按语言过滤，与核心判断 4 要求的索引形态不一致，这批数字不能完全预测
   T1.3.2 分片实现后的真实系统行为，建议届时用同一批查询重新校验一次。
7. **（2026-08-21 原判断，已被 2026-08-23 PR #61 推翻，见下方"更新"）** `/api/search` 不对外
   公开，登录后才能用；已上线的纯关键词搜索保持公开：这是用户明确
   决定——语义检索接的是 Workers AI 付费能力，不希望任何人都能访问导致被刷额度（这个顾虑
   不适用于零成本的纯 Pagefind 关键词搜索，T1.1.3 已上线的那部分不因此回退成需要登录）。
   认证方案是**单一共享密码 + 签名 Cookie**（`BLOG_SEARCH_PASSWORD` 校验、
   `BLOG_SEARCH_SESSION_SECRET` 做 HMAC 签名，均为 Worker Secret，已生成并记录在
   `~/Dev/.env`，尚未推送到 Cloudflare），**明确排除 Cloudflare Access**（用户已否决）。
   认证层要做成可替换的独立中间件，以后想换方案只改这一处。见 T1.3.6，且 T1.3.6 必须先于
   T1.3.3 完成（见下方"不可动摇的边界"——避免 `/api/search` 出现无认证的中间上线状态）。
   本仓库最近 7 天 3,440 PV，环比前 7 天（2,010 PV）+71%（`src/data/blog-analytics.json`），
   访问量绝对值仍小，这是"两路都跑、不做省钱式条件分支"在当前判断合理的依据，但确实在涨，
   如果流量持续增长需要重新评估这条判断。
   **更新（2026-08-23，PR #61，用户明确新决定）**：登录门禁**取消**，`/api/search`
   现在和关键词搜索一样公开。理由：登录墙真正要防的是 Workers AI/Vectorize 被刷额度，
   这件事一直是 per-IP 限速（30 req/5min）在做，不是密码——密码挡的只是"陌生人知不知道
   有这功能"，在本站当前流量级别下用户决定不再需要挡。**认证中间件本身没删**（`_lib/auth.js`
   `api/search-auth.js` 仍在），改为挂在两个仍需要密码的场景上：查看 `/api/search-analytics`
   使用统计、以及未来的 AI 对话功能（按调用成本仍需密码）。非阻塞跟进记 FU-27：全量公开后
   多 IP 汇总流量可能推高 Workers AI/Vectorize 账单，建议配置 Cloudflare 用量告警
   （同方向 FU-13/FU-18）。
8. **关键词+向量融合发生在浏览器端，Worker 不做融合**：Pagefind 是纯浏览器端 JS
   （`PagefindUI`），Cloudflare Worker 无法调用它，服务端不可能"并行跑 Pagefind"。
   `/api/search`（Worker）只返回向量这一路、经过自身绝对信号过滤（Vectorize 余弦相似度
   低于阈值的候选丢弃）后的候选列表；`/search` 页面的浏览器 JS 把这份候选与本地 Pagefind
   结果按排名做 RRF 融合。"无把握不返回"的判断在融合之前、按两路各自的绝对信号分别判断，
   不能靠融合后的 RRF 分数判断——RRF 只编码排名与多路共识，不编码绝对相关度，同样的 RRF
   分数区分不了"该拒的负样本"和"该留的真命中"。细节见 `spec.md` §检索融合。

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
    └─▶ /search 页面（浏览器）：本地 Pagefind 关键词检索（公开，无需登录，T1.1.3 已有）
          ∥ 请求 /api/search Worker（2026-08-23 PR #61 起公开，无需登录 Cookie，见核心判断 7
            的"更新"段落）：query → embedding
              → Vectorize 向量 top20 → 按 article_id 聚合去重（每篇 1-2 片段）
              → 用 Vectorize 自身余弦相似度阈值过滤（候选可能为空）→ 返回候选
          → 浏览器 JS 按 rank（非原始分数）把两路结果做 RRF 融合
          → 两路各自的绝对信号均判定"无靠谱结果"才展示"没有找到"（判断在融合之前，
            不能靠融合后的 RRF 分数，见 `spec.md` §检索融合）→ 否则展示融合后 top5

  登录
    └─▶ POST /api/search-auth（密码）→ 校验 BLOG_SEARCH_PASSWORD（常量时间比较）
          → 签发 HMAC 签名 Cookie（HttpOnly/Secure/SameSite=Lax/Path=/，30-90 天有效期）
          → 该接口本身限速（同 IP 15 分钟内最多 5 次），防止密码被撞库

Phase 2（自动化与增强）
  每日 Cron Trigger
    └─▶ 对比 manifest 与索引内容的 content_hash，修复漏索引、清理孤儿向量（不做主触发）
```

## 契约 / 接口

- **文章搜索文档**（构建期产出，供 Pagefind 及后续 manifest 复用）：
  `article_id`（=slug）、`title`/`titleEn`、`description`/`descriptionEn`、`tags`、`category`、
  `language`、`url`、正文标题层级。字段来源见 `spec.md`。
- **`/api/search`**（Phase 1 起）：**公开访问，无需登录 Cookie**（2026-08-23 PR #61 起；原为
  "需携带有效登录 Cookie，否则 401"，见核心判断 7 的"更新"段落）；输入自然语言 query
  （有长度上限）；输出**向量这一路**过阈值后的候选文章列表（可能为空，每篇：标题、URL、
  命中片段、语言）——聚合去重、融合排序、"没有找到"的最终判断由浏览器 JS 完成，
  不在这个端点内。
- **`/api/search-auth`**（Phase 1 起）：输入密码，输出登录 Cookie 或 401；限速见上。
- **索引 manifest**：记录 `embedding_model` / `embedding_dimensions` / `chunking_version` /
  `content_hash` / `language` / `indexed_at`，模型或切片算法变更时建新索引回填切流，不原地混写。

## 不可动摇的边界

- 绝不假设 Worker 运行时能访问 Git 仓库目录；索引数据源必须是部署后可达的
  manifest/KV/D1/sitemap 之一。
- Vectorize 的 metadata 不存全文（10KiB/向量上限），只存检索所需的最小字段。
- 检索结果必须按 `article_id` 去重聚合，不允许把 chunk top-K 直接当文章结果返回。
- `/api/search` 必须有输入长度上限、限速（"登录校验"一项自 2026-08-23 PR #61 起作废，见核心
  判断 7 的"更新"段落）；调用失败/超时时浏览器 JS 只展示本地
  Pagefind 结果（Pagefind 独立于 `/api/search` 运行，这不是 Worker 侧的降级逻辑，是前端
  "没拿到向量候选就只用关键词结果"的自然结果），不记录用户原始查询原文。
- Phase 1 是否上线，由 T1.2.2 依据 Phase 0B 的离线评测数据人工拍板，不由 agent 自行判断"应该做"
  ——**已拍板：go，混合方案**（见上方核心判断 6）。
- 模型/切片算法变更后旧向量不得与新向量混用；必须建新索引回填切流。
- 融合排序用 RRF（按排名融合），不手调关键词分数与向量余弦相似度的加权系数——两者量纲不同，
  直接加权不稳定；融合发生在浏览器端，不在 Worker 里（见核心判断 8）。
- `/api/search`（语义检索能力）**不对公众开放**，必须先过 T1.3.6 的密码登录才能访问，不允许
  上线一个无认证版本（哪怕是临时/测试）——**T1.3.6 必须先于或随 T1.3.3 完成，T1.3.3 的验收
  命令本身必须包含"无 Cookie 请求返回 401"这条断言**，不能把认证当成 T1.3.3 合并之后才补的
  独立步骤（否则 `/api/search` 合并进 `main` 就会经既有的 Cloudflare Pages Functions 部署
  流程自动上线，出现无认证的窗口期）。T1.1.3 已上线的纯关键词搜索页面**不受此约束**，继续公开。
  **（2026-08-23 PR #61 起本条整体作废：登录门禁已取消，`/api/search` 现已公开，防刷额度改由
  IP 限速 30 次/5 分钟承担。原文保留作历史记录，但不再是有效边界，不要据此给 `/api/search`
  恢复登录校验。见核心判断 7 的"更新"段落。）**
- **`wrangler vectorize create`（建 Vectorize 索引）与 `wrangler secret put`（推送
  `BLOG_SEARCH_PASSWORD`/`BLOG_SEARCH_SESSION_SECRET` 等密钥）是真实 Cloudflare 账号级操作，
  有计费与不可逆影响**——无人值守执行到这两类命令前必须停下来问用户确认，问完再继续同一个
  task，不得跳过或假设已获授权。

## 运行形态

- Phase 0A：纯静态，构建产物随 `deploy.sh` 一并发布到 Cloudflare Pages，无在线服务。
- Phase 1 起：Cloudflare Workers（HTTP API）+ Vectorize（存储）+ Workers AI（推理），
  触发方式为发布 hook（主）+ Cron Trigger（每日对账，Phase 2）。
