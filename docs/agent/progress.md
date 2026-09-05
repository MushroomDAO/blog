# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-25（`pilot run` 批量清跟进账本进行中——FU-32 已开 PR，其余按主题分批处理）

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.3（Phase 1）已全部 DONE。**F1.4（自动更新与增强，Phase 2）**——T1.4.1、
  T1.4.2 均已 DONE。剩 T1.4.3/T1.4.4，都是"可选增强，非必须"，T1.4.3 涉及真实 LLM 调用
  成本，不主动开工，等用户明确要不要做。
- **分支 / worktree**：2026-08-25 `pilot status` 已清理全部已合并残留——本地分支
  16→1（只剩 `main`）、worktree 7→1（只剩主 checkout）。`../blog-chore-docsync`
  （PR #62）、`../blog-chore-t141-status`（PR #64）、`../blog-chore-t142-fix`
  （PR #66）、`../blog-F1.4`（PR #63）、`../blog-F1.4-t142`（PR #65）、
  `../blog-followups`（PR #67）连同各自分支及 9 个 `pr-*-head` 残留分支均已删除。
  远程分支已核实：`origin/dailyblog` 与 `main` 无 diff（0 commits ahead），
  `origin/xiaobaobao` 有 8 个未合并 commit（微信多账号/xiaobaobao 主题池实验，
  最后一次提交 2026-05-11），不能当废弃分支清理，留给用户裁决。仓库
  `delete_branch_on_merge` 已确认为 `true`（GitHub 侧本来就开着，无需额外操作）。
- **PR**：#58~#67 均已合并。**#68、#69 待人工 review**（本仓库无外部评审服务）。
- **跟进账本批量清理进行中**（2026-08-25 用户明确要求先修 FU-32 再批量清、可分几个主题 PR）：
  按可操作性分类——FU-32（内容编辑陈旧向量，独立于批量之外单独修）已开 PR；能改代码的
  followups 按主题分几个 PR；账号级/仪表盘操作（FU-13/FU-26/FU-27 等）列清单交用户处理，
  不塞进代码 PR；已裁定/存档类（FU-4/FU-6/FU-9/FU-11/FU-15/FU-17/FU-18/FU-31）维持 OPEN
  不动，是记录不是待办。

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| FU-32 | [#68](https://github.com/MushroomDAO/blog/pull/68) | 待人工 review | 编辑文章后旧 chunk 未清理，3 轮对抗式自审无阻塞项 |
| FU-24/FU-29/FU-30 | [#69](https://github.com/MushroomDAO/blog/pull/69) | 待人工 review | .env 占位符误当真值导出（4 轮，含发现并修复本机可复现的 wrangler 缓存 OAuth 身份悄悄部署问题）+ forage 配额断言改 clamp+warn + pagefind 精确锁版本 |
| FU-25/FU-28 | 待推送 | 实现完成，3 轮对抗式自审进行中 | 搜索统计 IP 改带密钥 HMAC 哈希 + 统计端点补按会话限速 |

## 阻塞项（BLOCKED）
- （无）**CI 自动部署问题已解决**（原 FU-14）：GitHub Actions 的 `CLOUDFLARE_API_TOKEN`
  secret 失效一事，用户已授权改走 PR #54（`chore/manual-deploy-only`）——彻底删除依赖这个
  secret 的 workflow，部署改为完全走本地 `wrangler`（交互式 `./deploy.sh` / 非交互式 cron
  脚本各自显式读 token）。这个 secret 从此不再被任何东西读取，不需要用户去 GitHub 更新它。

## 最近完成
- 2026-08-23：**PR #67 合并**（`chore/followups-2026-08-24`）——批量处理 FU-5（baseline-results
  查询编号错位订正）、FU-10（12-16 chunk 预算按每语言的语义在文档里补充明确说明）两条非阻塞
  跟进项，纯文档/记录修正，无代码逻辑改动。
- 2026-08-23：**PR #66 合并**（`fix/search-reconcile-mutationid`）——`reconcile.py` 的
  `mutationId` 日志读漏了 Cloudflare v4 响应信封的嵌套层，永远打印 `None`；这是 PR #65
  合并后另开的小修复，Low 级、不影响功能正确性，未在已拿 APPROVE 的分支上加 commit。
- 2026-08-23：**PR #65 合并**（`feat/T1.4.2-cron-reconciliation`，squash `f9a61a4`）——
  T1.4.2 每日对账：`semantic-search/scripts/reconcile.py`（新）复用 T1.4.1 的全库 diff
  路径，新增两件事——① 漏索引文章重新 embed+upsert（同 `incremental-index.py --upsert`）、
  ② 孤儿检测+清理（manifest 有记录、本地文件已删除/改名的文章，删 Vectorize 向量 + manifest
  记录）。3 轮独立子 agent 自审（正确性/安全/数据安全-破坏性操作，本仓库第一个真的会删
  数据的脚本）先修了 2 个 HIGH bug + 一个真实存在的 `.mdx` 索引盲点。开 PR 后外部评审
  REQUEST_CHANGES，又抓到 2 个更严重的真阻塞项：`find_orphans` 没考虑 `BLOG_SEARCH_KV`
  是 manifest/`ratelimit:`/`searchlimit:`/`searchcache:v2:` 四种用途共享的同一个 KV
  namespace，非 manifest 形状的 key 被误判成孤儿，`delete_orphans` 读到后直接崩溃、真正的
  孤儿因为排序在崩溃点之后永远清不到（这也推翻了"不加比例上限是因为人会先看 dry-run 清单"
  的前提——清单会被无关 key 淹没）；`content_hash` 缺失/空时 0 向量被删但 manifest 记录
  照删，跟 docstring 承诺的"容错跳过"不符。两个都修了（改成白名单判定 + 早退守卫），加了
  回归测试，第二轮外部评审 APPROVED（Reviewer 用变异测试验证过新回归测试真的会因为改动
  而失败/通过，不是摆设）。合并后另开小 PR 修了一条 Low 级问题（`mutationId` 日志读漏了
  Cloudflare v4 响应信封的嵌套层，永远打印 `None`）——不在已拿到 APPROVE 的分支上加 commit
  重置评审状态。记入 FU-32 的第三类缺口（文章内容被编辑后旧向量从不清理，FU-8 最初就点名
  的场景）本 PR 未覆盖，非阻塞但应尽快单独补，见 tasks.md T1.4.2 证据。
  live 端到端验证（真实执行 `--delete-orphans` 对生产账号）仍受限于 T1.4.1 就有的同一个
  已知问题：`CLOUDFLARE_REGISTRAR_TOKEN` 缺 KV 列命名空间权限（401）。
- 2026-08-23：**PR #64 合并**（`chore/t141-status-sync`，squash `8cec5d1`）——纯文档同步，
  T1.4.1 状态 PR_OPEN→DONE、T1.4.2 状态 BACKLOG→READY，无代码改动。
- 2026-08-23：**PR #63 合并**（`feat/T1.4.1-incremental-index-hook`，squash `ad6a58e`）——
  T1.4.1 发布流程增量索引 hook：`semantic-search/scripts/incremental-index.py` 只对刚发布
  文章真正变化的语言重新 embed+upsert，跳过未变的，接进 `scripts/publish-blog.sh` 的
  `[4.7]` 步骤。3 轮独立子 agent 对抗式自审 + 2 轮外部评审。R1（CHANGES_REQUESTED）抓到
  真阻塞项：`upsert_vectors` 返回 HTTP 200 + `success=false` 时不抛异常，manifest 会被
  无条件写入，永久误判文章"已索引"但向量其实没写进去，全程不报错——已修复（`build-vectorize-
  index.py` 里同款孪生 bug 一并修），reviewer 实测拆掉新加的守卫验证过回归测试真的会红。
  顺带处理 5 条非阻塞：`incremental-index-plan.json` 补 gitignore；FU-8（孤儿向量清理）
  归属从 T1.4.1 改派给 T1.4.2；argv 拼写错误（如 `--slugs`）现在会报错而不是静默退化成
  全库扫描；`--slug` 显式拒绝 manifest 保留字 `_global`（全库扫描分支也过滤掉同名文件）；
  `INDEX_NAME` 硬编码记入 FU-31（等真的需要切索引版本再处理）。**裁定 FU-17**（缓存陈旧
  窗口）：不做主动失效——缓存 key 按查询文本哈希不按 article_id，唯一能做的主动失效是清空
  整个 `searchcache:` 前缀，代价超过收益，维持 T1.3.4 原有的 6 小时新鲜度上限。
  live 端到端验证（真实发布后短时间内能搜到）仍待第一次真实发布触发——当前
  `CLOUDFLARE_REGISTRAR_TOKEN` 缺 KV 列命名空间权限（401），dry-run diff 对生产账号没能跑通，
  首次真实发布时留意 `[4.7]` 那一步的日志。
- 2026-08-23：**PR #61 合并**（`feat/public-search-no-auth`）——`/api/search` 的登录门禁
  取消，语义检索改为公开（跟已上线的关键词搜索一样）。用户决策：登录墙真正防的是 Workers
  AI/Vectorize 被刷额度，这件事一直由 IP 限速（30 req/5min）承担，不是密码；密码只挡"陌生
  人知不知道有这功能"，当前流量级别不再需要。认证中间件本身没删，改挂在
  `/api/search-analytics.json`（登录后查看搜索统计）和未来的 AI 对话功能上。3 轮对抗式
  自审（正确性/安全/生产失败模式）：正确性、安全均无阻塞项（修了一处过期的 doc comment）；
  生产失败模式记入非阻塞 FU-27（全量公开后多 IP 汇总流量可能推高账单，建议配 Cloudflare
  用量告警）。83/83 测试通过。
- 2026-08-23：**PR #60 合并**（`feat/search-usage-analytics`）——`/api/search` 新增使用统计
  （写入独立的 Analytics Engine 数据集 `blog_search_events`），`/api/search-analytics.json`
  单独开一个登录门禁、`cache-control: private, no-store` 的端点查询（不复用公开且被边缘
  缓存的 `/api/analytics.json`，避免把登录用户的搜索数据泄露进共享缓存）。Grade B 3 轮
  对抗式自审修复：`fetchSearchStats` 汇报错子请求状态、补了可窄权限升级的
  `CF_ANALYTICS_ENGINE_TOKEN`、403 现在有独立的"检查 token 权限"提示。87/87 测试通过（新增
  17 条）。非阻塞记入 FU-20（本条已确认 done=PR#58 关闭）、FU-25/FU-26（数据保留期/边缘缓存
  未核实，运维层面待办）。**`analytics_engine_datasets` 是本仓库首次接入的新 binding 类型，
  首次真实部署需要盯紧**（本仓库此前有过 `account_id` 配置字段静默失效数周无人发现的先例）。
- 2026-08-23：**PR #59 合并**（`fix/deploy-centralize-account-id`）——`CLOUDFLARE_ACCOUNT_ID`
  统一在所有部署脚本里的读取方式收敛成一处，避免重复定义漂移；顺带把导航搜索链接改成
  纯图标（配合布局，非阻塞 UI 调整）。
- 2026-08-22：**PR #57 合并**（`fix/rate-limit-and-cache-hardening`，squash commit
  `01aeccf`）——外部评审 round 2 对 T1.3.4 缓存归一化修复（FU-16 首次修复）本身抓出一个
  真实 bug：`normalizeQuery()` 原来只用在算缓存 key，传给 `env.AI.run()` 的还是原始未归一化
  的 query。Reviewer 用录制式 fake AI 实测证明：全角查询先到时用自己的原文去 embedding 并
  写入缓存，语义等价的半角查询后到直接吃缓存，拿到的是**全角原文**算出来的向量结果——
  bge-m3 并不真的把全角/半角 Latin 字符当等价输入，缓存层的"等价"判断在 embedding 层不成立。
  修法：归一化只在请求体解析阶段做一次，之后缓存 key 和 `env.AI.run()` 调用都用同一个已
  归一化字符串。顺带处理两条非阻塞建议：缓存 key 加 `v2:` 版本前缀（避免旧归一化规则下的
  缓存条目跟新规则条目语义混淆）、读缓存时加 `Array.isArray()` 校验（脏数据不再原样透传，
  避免前端未加 `.catch` 的 `.map()` 链式调用被整体打死）。同时关闭 FU-19
  （`rate-limit.js` 的 `checkAndIncrement` 对 KV get/put 调用补 try/catch，fail-closed）。
  新增 2 条回归测试，全量 `pnpm test`（70/70）与 `pnpm run build` 均通过。**至此 followups
  账本里 FU-16/FU-19 均已关闭（done=PR#57）**。
- 2026-08-22：**PR #56 合并**（`fix/nav-search-link`）——首页全局导航（`Header.astro`）
  补上"🔍 Search"入口链接。起因：语义检索功能上线后发现首页没有任何入口指向 `/search`，
  只有知道这个路径的人才能用到——先手动部署上线修复，随后补开 PR 留存永久记录。
- 2026-08-22：**停用 GitHub Actions 自动部署到 Cloudflare Pages**（`.github/workflows/deploy.yml`
  → `test.yml`，只跑 `pnpm test` + `pnpm build` 做 CI 验证，加了 `pull_request` 触发，
  不再碰 Cloudflare）。起因：这个 workflow 用的 `CLOUDFLARE_API_TOKEN` GitHub secret
  失效了一段时间（见 FU-14），静默让好几次自动部署失败，没人第一时间发现。以后部署
  统一走本地 wrangler，不再依赖一个平时没人盯着的远端 secret——**交互式手动部署**用
  `./deploy.sh`（假定已经 `wrangler login` 或 shell 里已经有 `CLOUDFLARE_API_TOKEN`）；
  **非交互式 cron**（`scripts/update-analytics.sh`、`pipeline/newsletter/
  local-fallback.sh`）各自显式从项目 `.env` 读 token，不依赖任何交互式登录状态。
  `wrangler.toml` 补了 `account_id`（原来唯一记录它的地方是刚删掉的那个 workflow）。
  顺带修了 `scripts/update-analytics.sh`：它原来显式依赖 CI 部署当本地部署失败时的
  兜底（2026-08-13 真实发生过一次），现在从根因修掉；`pipeline/newsletter/
  local-fallback.sh` 新增的本地部署路径经 round 2 review 抓出两个阻塞问题（cron
  真实 PATH 下 pnpm/npx/node/wrangler 全部找不到、部署逻辑挂在 push 成功判断之外、
  push 失败也会用脏工作树部署到生产）已修复，并对齐 `scripts/publish-blog.sh` 已有的
  CA-bundle-优先-TLS-bypass-兜底写法。
- 2026-08-22：**T1.3.4 完成**（`functions/api/search.js` 加查询结果缓存：6 小时 TTL，
  query 归一化取哈希做 key，命中跳过计费的 AI/Vectorize 调用）——T1.3.4 原定范围里的
  "输入长度上限"/"简单限速"/"降级"其实 T1.3.3 落地时已经一并做完，本 task 实际只剩
  "常见查询缓存"这一项。3 轮对抗式自审抓到一个真问题：缓存命中最初设计成完全不计入
  限速，但共享 KV namespace 同时扛着 T1.3.6 的登录限速器，不限速的缓存读流量能把配额
  打满、是另一种拒绝服务面——改成限速检查挪到缓存检查之前，命中缓存依然计入限速，
  只是跳过真正计费的调用。顺带修复 FU-12（`search-auth.js` 的 Content-Length 只信
  请求头，跟 `search.js` 用同一个修法关掉）+ T1.3.5 状态一直忘了从 `PR_OPEN` 改成
  `DONE`（早就合并了，纯文档疏漏）。至此 F1.3 六个 task 全部功能完成。
- 2026-08-22：**T1.3.3 合并**（PR #52，squash commit `edaa956`）——`/api/search` 端点
  （query → bge-m3 embedding → Vectorize top-20 → 按 article_id 聚合去重 → 相似度阈值
  过滤）+ 前端 RRF 融合（`search.astro` 新增登录后可用的语义检索输入框，用 Pagefind 原生
  JS API 而不是 PagefindUI 组件，跟 `/api/search` 的结果做 RRF 融合，原有公开关键词搜索
  不受影响）。3 轮对抗式自审修复：前端搜索请求竞态（debounce 不取消旧请求，可能用过期
  响应覆盖新结果甚至误触发登出）、限速只按 IP 导致泄露 Cookie 换 IP 可绕过（加了按会话
  哈希的第二道限速）、`Content-Length` 请求头可以撒谎绕过体积上限（改成量实际字节数）。
  **合并后真实验证**：CI 自动部署当时已经失效（见下方"阻塞项"），改用本地 wrangler 手动
  部署，用真实登录 Cookie 对生产环境查询"Pagefind"，返回分数 `0.5089695` 且排名第一的
  文章与 `vector-comparison-report.md` 记录的 `0.5043`/同一篇文章一致——证实 Workers AI
  binding 调用与建索引时的原始 REST API 调用产出同一嵌入空间，不存在"绑定调用参数不一致
  导致所有分数静默低于阈值"的担忧。
- 2026-08-22：**T1.3.6 合并**（PR #48，squash commit `423d7eb`）——密码 + HMAC 签名 Cookie
  登录（`functions/_lib/auth.js`、`functions/_lib/rate-limit.js`、
  `functions/api/search-auth.js`、`src/pages/search.astro` 登录态 UI）。外部评审 3 轮：
  R1 揪出 2 blocking（跨站垃圾请求烧限速额度；KV binding 缺失时静默放行到无限次密码尝试）
  + 1 medium（Cookie 无 `__Host-` 前缀可被兄弟子域影子化）+ 3 low；R2 发现 R1 的限速修复
  只挡住了 `application/x-www-form-urlencoded` 形状，`Content-Type: text/plain` 且 body
  恰好合法 JSON 的跨站请求仍能绕过，补上 `Content-Type: application/json` 强校验后关闭；
  R3 对最新提交裁决 APPROVED。全程新增 9 条回归测试（36 条全绿），并把 `pnpm test` 接入
  `.github/workflows/deploy.yml`，部署前自动跑。**真实账号操作已执行**：
  `wrangler secret put BLOG_SEARCH_PASSWORD` / `BLOG_SEARCH_SESSION_SECRET`
  已推送，`blog-search-manifest` KV namespace 已建并绑定为 `BLOG_SEARCH_KV`。踩坑：
  只通过 Pages API 加的 KV binding 被下一次 `wrangler pages deploy`（部署时会用本地
  `wrangler.toml` 的绑定声明同步项目配置）悄悄冲掉，导致登录接口一度 503——已用 PR #50
  把 binding 写进 `wrangler.toml` 修复，重新部署后直接打 `blog.mushroom.cv` 验证：密码错误
  401、密码正确 200 + 合法 `__Host-` 会话 Cookie，登录闭环已经跑通。
- 2026-08-22：**T1.3.5 合并**（PR #47）——Cloudflare KV 索引 manifest（`build_manifest()`、
  namespace 查找/创建、KV 读写），修复 `_global` 保留键冲突、URL 注入（`?`/`#` 未转义）、
  跨账号缓存污染等问题。
- 2026-08-22：**T1.3.2 合并**（PR #45，commit `b8f547b`）——段落级分片模块
  `semantic-search/scripts/chunking.py`。3 轮对抗式自审在真实语料库上抓到 4 个 bug（2 个
  已经在真实触发）：尾部 chunk 无界增长、双语分隔符检测被行内提及劫持、标题孤儿 chunk、
  4 反引号转义围栏配对错乱。全库 478 篇文章验证通过。
  **反查发现同一个分隔符检测 bug 也存在于已合并的 T1.3.1 脚本里**（本库 2 篇文章：
  `seo-geo-skill-ai-citation-optimization`、`geo-generative-engine-optimization-guide`，
  正文里用反引号引用过 `<!--EN-->` 分隔符字面量），线上 Vectorize 索引因此有这两篇文章的
  错误数据。已用 PR #44 热修复检测逻辑（合并后）、重新执行 `--upsert` 刷新全部 911 条向量、
  精确重算旧 chunk_id 并 `delete_by_ids` 清理孤儿数据——线上索引现在是干净的。
  非阻塞发现记入 followups：FU-9（16 片硬上限下 2 篇文章的个别 chunk 仍略超 900 token）、
  FU-10（12-16 chunk 预算是"每篇"还是"每语言"文档没写清楚，当前按每语言实现）。
- 2026-08-22：**T1.3.1 合并**（PR #39，commit `6b9fc8d`）——Vectorize 索引 `blog-search-v1`
  已建（1024d/cosine），901 条向量（zh 467/en 434）已 upsert 并经 query API 验证。
  真实执行时发现 Vectorize v2 vector id 有 64 字节硬上限（原拼接方案超限），改用哈希方案。
  T1.3.2/T1.3.5/T1.3.6 解锁为 READY。
- 2026-08-22：**T1.3.1 完成，PR #39 待评审**——`build-vectorize-index.py` 索引脚本，3 轮独立
  子 agent 对抗式自审（正确性/安全/生产失败模式，grade B 3 轮下限）修复语言判定 bug（原逻辑
  把 SEO 用的 `titleEn`/`descriptionEn` 当成"有没有双语内容"的信号，单语文章被错误双记/
  标错语言）等多项问题。真实执行 `--create-index`/`--upsert`（用户确认后）时发现
  Vectorize v2 vector id 有 64 字节硬上限（原拼接方案对长 slug 超限），改用哈希方案修复。
  最终：索引 `blog-search-v1`（1024d/cosine）已建，901 条向量（zh 467/en 434）全部写入并
  经 query API 验证可用。凭据踩坑记录：`CLOUDFLARE_REGISTRAR_TOKEN` 起初只有 Workers AI
  权限没 Vectorize 权限（403），用户新建 token 又反过来只有 Vectorize 没 Workers AI（401），
  最终给同一个新 token 补齐两条权限才跑通——`.env` 里同名变量出现两次（新旧 token）时脚本的
  `grep|head -1` 会取到旧的，已改用 `tail -1`，但这提醒以后新增同名 env 变量最好换个名字，
  别指望"末尾覆盖"对所有读取方式都生效。
- 2026-08-22：**PR #38 合并**（squash commit `5166990`）——T1.2.2 go 裁定文档，经外部评审
  4 轮（R1-R4）+ 推送修复后第 5 轮 APPROVED。修复的阻塞项：RRF 分数不能承担"无把握不返回"
  的判断（改为按各路绝对信号判断，RRF 只排序）、Worker 调不了浏览器端 Pagefind（融合改到
  前端）、"跨语言"理由记错（订正为同语言同义词鸿沟）、Cookie 缺 `Path=/`、认证可能有无认证
  窗口期（反转 T1.3.3/T1.3.6 依赖）、密码门禁范围会误伤已公开的关键词搜索（已收窄范围）、
  acceptance.md/PLAN.md 未同步裁定（已更新）。ColBERT/late-interaction 评估记入 followups.md
  FU-4（现阶段不接入，RRF 混合已覆盖同类场景）。
- 2026-08-21：**T1.2.2 拍板 go**（用户对话确认，非 agent 自行判断）——混合方案：关键词+向量
  并行检索、RRF 融合、article 级聚合去重、无把握不返回；`/api/search` 不对外公开，密码+签名
  Cookie 登录（明确否决 Cloudflare Access）；全流程留在 Cloudflare，不做本地推理；中英文各自
  独立 chunk。已生成 `BLOG_SEARCH_PASSWORD`/`BLOG_SEARCH_SESSION_SECRET` 写入 `~/Dev/.env`，
  尚未推送到 Cloudflare（`wrangler secret put` 需用户另行确认）。详见 `architecture.md` 核心
  判断 6-8、`spec.md` §检索融合/§登录会话、`tasks.md` T1.2.2/T1.3.6。F1.3 全部 Task 解锁。
- 2026-08-21：T1.2.1 DONE（PR #36 合并进 main，commit `b30e595`）——用
  `CLOUDFLARE_REGISTRAR_TOKEN`（用户指出的可用 token）跑通
  464 篇文章 + 24 条查询的 bge-m3 embedding 对比实验，产出
  `semantic-search/eval/vector-comparison-report.md`。核心发现：跨语言查询（"脑仿真 大脑
  连接组"）从关键词 0 结果变成向量 #1 命中；EN/ZH 同主题查询在向量下结果高度一致，关键词下
  差异悬殊；但 WebGPU、terminal AI coding tool 两条精确技术名词查询向量检索退步。
  经 Codex 三轮独立评审（正确性、判断偏误复核、操作安全）修正过 2 处评分过松的问题。
- 2026-08-20：跟进账本清理 PR #34 合并——修复 `.pilot.yml` 解析 bug + 发布脚本 pipefail
  （附带修了一个真实的生产风险：微信发布失败会让 git 与已部署内容不同步）
- 2026-08-20：状态回填 PR #35 合并——T1.1.2/T1.1.3/T1.1.4 补齐 DONE 状态
- 2026-08-20：F1.1（Phase 0A 关键词检索基线）全部完成——T1.1.1~T1.1.4 均已合并（PR #29/#30/#31/#32）
- 2026-08-20：GitHub 分支保护已开启（`main` 需 1 个 approval，`enforce_admins=false`，
  博客发布自动化不受影响）
- 2026-08-20：修复了另一个并发会话误提交到 `feature/semantic-search-poc` 的 4 篇博客发布 commit
  （已 cherry-pick 回 `main`）

## 跟进账本（不阻塞主线，见 followups.md）
- **FU-1、FU-2、FU-3、FU-5、FU-10、FU-12、FU-14、FU-16、FU-19、FU-20 均已关闭**
  （FU-5/FU-10 于 2026-08-23 由 PR #67 批量处理关闭，其余分别
  done=PR#34/#34/#34/#55/#54/#57/#57/#58，见上方"最近完成"）。
- **`followups.sh count-open` 核实：剩余 19 条 OPEN**（2026-08-25 复核，比上一版记录的
  20 条少了 FU-5/FU-10 这 2 条、但本版首次把 FU-32 计入，净减 1）：FU-4（ColBERT 评估）、
  FU-6（KV 限速器跨 PoP 弱点）、FU-7（凭据权限范围，已部分满足）、FU-8（增量更新孤儿向量
  清理，正式方案已转交 T1.4.2，但"内容编辑"这一类场景仍未覆盖，见 FU-32）、FU-9（16 片硬
  上限下的 token 超量残留）、FU-11（KV read-modify-write 非原子，单 PoP 内并发竞态）、
  FU-13（建议给 Workers AI/Vectorize 配置用量告警）、FU-15（TLS bypass，已确认是既定模式
  非遗留代码）、FU-17（缓存无失效钩子，已裁定不做主动失效，留档不是待办）、FU-18（缓存写入
  增加 KV 配额消耗，Paid 套餐下风险不成立，留档）、FU-24（.env.example 占位符会被当真值
  导出）、FU-25（搜索统计存明文 IP+查询词，PR#61 公开后数据主体从"仅站长"变成"任何访客"，
  隐私前提已变，需重新评估）、FU-26（搜索统计端点未核实是否被 zone 级 Cache Rule 覆盖
  no-store）、FU-27（PR#61 公开后 IP 限速不约束总独立访客量，建议配用量告警）、FU-28
  （`/api/search-analytics.json` 本身没有限速，登录系统已被 PR#61 重新定位，原限速器"没了
  归宿"）、FU-29（forage stage.py 的 PER_SOURCE_CAP 断言在模块顶层，手滑改 QUOTA 超限会让
  当天整条流水线直接中止，非阻塞）、FU-30（pagefind 从精确锁定放宽成 `^1.5.2`，以后不带
  包名的 `pnpm update` 可能悄悄升级、打断 postbuild，非阻塞）、FU-31（`incremental-index.py`
  的 INDEX_NAME 写死，等真的要切索引版本再处理）、FU-32（T1.4.2 review 新发现：内容被编辑后
  旧 chunk 的陈旧向量从未清理，`find_orphans` 的孤儿判定只看 article_id 存不存在、不覆盖
  "文章还在但内容变了"这类，FU-8 最初点名的场景实际仍未解决，建议在 `do_upsert` 里补上删旧
  chunk_id 这一步）。
- 用户此前决定"等主线做完再批量清"——**F1.4 主线（T1.4.1/T1.4.2）现在已完成**，下一轮
  `pilot resume`/`pilot run` 若确认没有其它 READY task，应进入批量清账本流程，不用再等。

## 下一个 READY
- **没有 READY task**。F1.4 的 T1.4.1/T1.4.2 均已 `DONE`。T1.4.3（LLM 一句话匹配理由）/
  T1.4.4（reranker）仍是 `BACKLOG`——都是"可选增强，非必须"，T1.4.3 涉及真实 LLM 调用
  成本（需配合成本监控），不主动开工，等用户明确要不要做。
- 跟进账本还有 19 条 OPEN 项（含 FU-32），F1.4 主线已完成，下一轮触发 `pilot run/resume`
  时应进入批量清账本，不用再等。
