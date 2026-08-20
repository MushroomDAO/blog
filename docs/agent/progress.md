# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-21 01:30

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.2 离线向量效果验证（Phase 0B）
- **正在开发的 Task**：T1.2.1 本地/CI 跑 bge-m3 embedding 对比实验（状态：BLOCKED）
- **分支 / worktree**：`docs/T1.2.1-blocked-status` / `../blog-F1.2`（记录阻塞状态，尚未开始实现）
- **PR**：无

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| （无） | — | — | — |

## 阻塞项（BLOCKED）
- **T1.2.1**：需要一个有 Workers AI 权限的 Cloudflare API token 才能调用 `bge-m3` embedding，
  项目现有 `.env` 里的 `CLOUDFLARE_API_TOKEN` 鉴权失败（`Authentication error`，大概率是发布用的
  窄权限 token）。不会擅自扩大权限或建新 token，等用户提供或授权。
  F1.2 剩余 task（T1.2.2）依赖 T1.2.1，F1.3/F1.4 依赖 F1.2 的裁定，暂时全部无法推进。

## 最近完成
- 2026-08-20：F1.1（Phase 0A 关键词检索基线）全部完成——T1.1.1~T1.1.4 均已合并（PR #29/#30/#31/#32）
- 2026-08-20：T1.1.4 评测基线关键发现：中文自然语言/跨语言查询召回明显弱于英文/关键词查询，
  见 `semantic-search/eval/baseline-results.md`
- 2026-08-20：T1.1.3 搜索入口页面 DONE（PR #31 合并进 main，commit `9eff119`）；实测搜索
  "Claude Code" 返回 214 条带高亮结果，Category/Language 过滤下拉自动生效
- 2026-08-20：T1.1.2 集成 Pagefind 构建后索引 DONE（PR #30 合并进 main，commit `5e3cc88`）
- 2026-08-20：T1.1.1 给文章模板打 Pagefind 元数据标记 DONE（PR #29 合并进 main，commit `09d7fce`）
- 2026-08-20：`semantic-search/PLAN.md` v1.0 完成——Codex 对抗评审 + 裁判合并（PR #28）
- 2026-08-20：GitHub 分支保护已开启（`main` 需 1 个 approval，`enforce_admins=false`，
  博客发布自动化不受影响）
- 2026-08-20：`docs/agent/` 七件套规划文档完成并合并（PR #27）
- 2026-08-20：修复了另一个并发会话误提交到 `feature/semantic-search-poc` 的 4 篇博客发布 commit
  （已 cherry-pick 回 `main`）

## 跟进账本（不阻塞主线，见 followups.md）
- FU-1：`.pilot.yml` 行尾内联注释导致 `grade-change.sh` 等脚本默认 base 解析失败
- FU-2：`scripts/publish.sh` / 已废弃的 `scripts/auto-publish.sh` 的 `pnpm build | tail` 没开
  pipefail，会吞掉构建失败（含新加的 pagefind 索引失败）；当前实际在用的
  `scripts/publish-blog.sh` 已经是 `set -euo pipefail`，不受影响

## 下一个 READY
- 无——T1.2.1 BLOCKED（缺 Workers AI 权限的 token），需要用户先解除阻塞才有下一个可开工的 task
