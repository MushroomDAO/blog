# Follow-ups ledger（append-only · 永不删行 · 提交进仓库）

> pilot 的 review triage 把「真问题但不阻塞（B）」和延后项记在这里。
> 主线 task 全部完成后，由 `pilot run` 批量合成一个 cleanup PR 做掉，逐条标 [x] done=PR#n。
> `- [ ]`=OPEN，`- [x]`=DONE。GitHub PR comment 是永久兜底。

- [ ] FU-1 · B · src=T1.1.1 · 2026-08-20 · .pilot.yml 的 base_branch/integration_branch 行尾内联注释会让 grade-change.sh 等脚本的默认 base 解析失败（把注释也读进去），需要把注释挪到单独一行或改用脚本能正确 strip 的格式
- [ ] FU-2 · B · src=T1.1.2 review (Codex, production-failure-mode lens) · 2026-08-20 · scripts/publish.sh 和已废弃的 scripts/auto-publish.sh 用 pnpm build 2>&1 | tail -3 且没开 pipefail，set -e 抓不住 pnpm build 失败（tail 的退出码掩盖了它）。T1.1.2 加的 postbuild pagefind 索引步骤是刻意 fail-closed 的，会让这个既有 bug 被触发的概率变高。当前实际在用的 scripts/publish-blog.sh 已经是 set -euo pipefail，不受影响；scripts/publish.sh 需要补 pipefail 或改成不走 tail 管道执行 pnpm build
- [ ] FU-3 · B · src=T1.1.3 · 2026-08-21 · search.astro 用的是 Pagefind 的 Default UI(pagefind-ui.js/css)；build 时 pagefind 提示 1.5.0 起新集成建议用 Component/Modular UI(更好的可访问性和自定义能力)。Default UI 官方说明仍会继续支持,不阻塞,等 Phase 0B/1 决定要不要长期投入这个功能时再考虑迁移
