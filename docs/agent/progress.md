# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-20 22:30

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.1 关键词/静态检索基线（Phase 0A）
- **正在开发的 Task**：尚未开工，规划刚完成
- **分支 / worktree**：规划文档本身在 `../blog-plan`（`docs/plan-2026-08-20` 分支）；
  实际开发 F1.1 时需新建 `../blog-F1.1` worktree
- **PR**：[#27](https://github.com/MushroomDAO/blog/pull/27)（PENDING，等人工 review——本仓库未确认接入外部评审服务）

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| （规划文档） | [#27](https://github.com/MushroomDAO/blog/pull/27) | PENDING | `docs/agent/*` + `.pilot.yml` 首次提交，需人工 approve 后合并（`--allow-trunk`） |

## 阻塞项（BLOCKED）
- 无（T1.2.2「Phase 1 Go/No-Go 裁定」在 F1.2 完成前不会被 run 挑中，届时会成为
  需要人工拍板的 BLOCKED 项，见 tasks.md）

## 最近完成
- 2026-08-20：`semantic-search/PLAN.md` v1.0 完成——Codex 对抗评审 + 裁判合并，
  已提交在 `feature/semantic-search-poc` 分支
- 2026-08-20：GitHub 分支保护已开启（`main` 需 1 个 approval，`enforce_admins=false`，
  博客发布自动化不受影响）
- 2026-08-20：`docs/agent/` 七件套规划文档完成（本次）

## 下一个 READY
- T1.1.1 给文章模板打 Pagefind 元数据标记（依赖已满足，可直接开工）
