# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-21 14:20

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.3 语义检索上线（Phase 1）
- **正在开发的 Task**：无（T1.3.1 已开 PR #39，等评审；T1.3.2 依赖 T1.3.1 合并才能开工）
- **分支 / worktree**：`feat/T1.3.1-vectorize-embedding` @ `../blog-F1.3`
- **PR**：[#39](https://github.com/MushroomDAO/blog/pull/39)（等评审）

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| T1.3.1 | [#39](https://github.com/MushroomDAO/blog/pull/39) | 待评审 | Vectorize 索引 + embedding 脚本，已真实执行验证过（901 向量已在账号里） |

## 阻塞项（BLOCKED）
- 无

## 最近完成
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
- FU-4（ColBERT 评估）、FU-5（baseline-results 编号错位）、FU-6（KV 限速器弱点）、FU-7
  （凭据权限范围，2026-08-22 已部分满足）、FU-8（增量更新孤儿向量清理）共 5 条 OPEN，
  全部非阻塞，等主线 F1.3/F1.4 做完后批量清

## 下一个 READY
- 无（T1.3.1 已开 PR #39 等评审；T1.3.2 依赖 T1.3.1 合并进 main 才能开工）
