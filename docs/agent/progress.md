# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-20 23:55

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.1 关键词/静态检索基线（Phase 0A）
- **正在开发的 Task**：T1.1.4 评测查询集 + Recall@5 基线记录（状态：PR_OPEN，F1.1 最后一个 task）
- **分支 / worktree**：`feat/T1.1.4-eval-baseline` / `../blog-F1.1`
- **PR**：[#32](https://github.com/MushroomDAO/blog/pull/32)（等人工 review）

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| T1.1.4 | [#32](https://github.com/MushroomDAO/blog/pull/32) | PENDING | 需人工 approve 后合并（`--allow-trunk`）；合并后 F1.1 全部完成 |

## 阻塞项（BLOCKED）
- 无（T1.2.2「Phase 1 Go/No-Go 裁定」在 F1.2 完成前不会被 run 挑中，届时会成为
  需要人工拍板的 BLOCKED 项，见 tasks.md）

## 最近完成
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
- T1.1.4 完成后 → F1.1 全部 DONE，下一个 Feature 是 F1.2 T1.2.1（离线向量对比实验）
