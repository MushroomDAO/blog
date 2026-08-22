# Follow-ups ledger（append-only · 永不删行 · 提交进仓库）

> pilot 的 review triage 把「真问题但不阻塞（B）」和延后项记在这里。
> 主线 task 全部完成后，由 `pilot run` 批量合成一个 cleanup PR 做掉，逐条标 [x] done=PR#n。
> `- [ ]`=OPEN，`- [x]`=DONE。GitHub PR comment 是永久兜底。

- [x] FU-1 · B · src=T1.1.1 · 2026-08-20 · .pilot.yml 的 base_branch/integration_branch 行尾内联注释会让 grade-change.sh 等脚本的默认 base 解析失败（把注释也读进去），需要把注释挪到单独一行或改用脚本能正确 strip 的格式 · done=PR#34
- [x] FU-2 · B · src=T1.1.2 review (Codex, production-failure-mode lens) · 2026-08-20 · scripts/publish.sh 和已废弃的 scripts/auto-publish.sh 用 pnpm build 2>&1 | tail -3 且没开 pipefail，set -e 抓不住 pnpm build 失败（tail 的退出码掩盖了它）。T1.1.2 加的 postbuild pagefind 索引步骤是刻意 fail-closed 的，会让这个既有 bug 被触发的概率变高。当前实际在用的 scripts/publish-blog.sh 已经是 set -euo pipefail，不受影响；scripts/publish.sh 需要补 pipefail 或改成不走 tail 管道执行 pnpm build · done=PR#34
- [x] FU-3 · B · src=T1.1.3 · 2026-08-21 · search.astro 用的是 Pagefind 的 Default UI(pagefind-ui.js/css)；build 时 pagefind 提示 1.5.0 起新集成建议用 Component/Modular UI(更好的可访问性和自定义能力)。Default UI 官方说明仍会继续支持,不阻塞,等 Phase 0B/1 决定要不要长期投入这个功能时再考虑迁移 · done=PR#34
- [ ] FU-4 · B · src=review PR#38 · 2026-08-22 · ColBERT/late-interaction (sentence-transformers v6) 评估：现阶段不接入，理由见对话记录——RRF 混合已覆盖精确技术名词场景，且 Cloudflare Workers AI/Vectorize 均不原生支持多向量 MaxSim，接入需自建推理。若 F1.3 上线后精确技术名词查询仍有明显失败案例，可重新评估文章提到的'两阶段最小接入'（现有召回不动，只对 top50 候选做 MaxSim rerank）
- [ ] FU-5 · B · src=review PR#38 · 2026-08-22 · baseline-results.md 的查询编号(#12-#17)与 queries.md/vector-comparison-report.md 不一致，且自相矛盾（第16行标'3D可视化工具'但散文写#16是recursive self improvement）。不影响本次裁定（裁定按名字引用，未用编号交叉引用），但会误导以后按编号查阅的人
- [ ] FU-6 · B · src=review PR#38 · 2026-08-22 · T1.3.6 登录限速用 KV 计数器（15分钟5次/IP）对分布式撞库较弱，因为 Cloudflare KV 最终一致（全球传播约60s）。严重度低（单一共享密码+低访问量场景），后续如需加强可换 Durable Objects 或 CF 原生 rate limiting binding
- [ ] FU-7 · B · src=T1.3.1 self-review (security lens) · 2026-08-22 · T1.3.1 索引脚本复用 CLOUDFLARE_REGISTRAR_TOKEN(另一项目cmic长期在用的凭据)做 Vectorize create/upsert 这类真实写操作，权限范围可能比这个用途需要的更宽。值不值得为 T1.3.x 铸造一个 Workers AI:Edit + Vectorize:Edit 专用窄权限 token，是账号级操作需要用户决定，非阻塞（2026-08-22 更新：用户已铸造新 token 并补齐两条权限，当前在用，遗留问题只剩旧 token 要不要收回）
- [ ] FU-8 · B · src=T1.3.1 self-review (production-failure-mode lens) · 2026-08-22 · build-vectorize-index.py 不做 spec.md 要求的'先记录旧chunk_id再删'增量更新流程——两次运行之间若文章内容被编辑，旧 chunk_id 不会被清理，留下孤儿向量。当前只在脚本文档里提示手动用 wrangler vectorize delete-by-ids 清理，正式方案交给 T1.4.1 的对账逻辑
