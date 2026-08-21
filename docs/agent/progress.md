# 语义检索 / 智能推荐功能 实时状态 — progress

> 「此刻仓库真实发生了什么」。由 `pilot run` 每一步更新。
> 更新时间：2026-08-21 14:20

## 当前聚焦
- **Milestone**：M1 语义检索 / 智能推荐功能
- **Feature**：F1.2 离线向量效果验证（Phase 0B）—— **F1.1+F1.2 全部完成，卡在 T1.2.2 等人工裁定**
- **正在开发的 Task**：无（T1.2.2 是产品决策，不能无人值守推进）
- **分支 / worktree**：无
- **PR**：无

## 进行中 / 待回执的 PR
| Task | PR | 状态 | 备注 |
|:---|:---|:---|:---|
| （无） | — | — | — |

## 阻塞项（BLOCKED）
- **T1.2.2**：Phase 1 Go/No-Go 裁定是产品方向决策，T1.2.1 报告写完后必须停在这里等用户拍板，
  不可无人值守自行决定。报告结论：纯向量单独替代关键词不成立（精确技术名词查询会退步），
  跨语言场景向量有决定性优势，但"值不值得为此投入 Phase 1 工程量"是需要用户权衡的产品判断，
  详见 `semantic-search/eval/vector-comparison-report.md`。F1.3/F1.4 全部依赖这个裁定，
  裁定前保持 `BACKLOG`。

## 最近完成
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
- 无 OPEN 项（FU-1/FU-2/FU-3 均已通过 PR #34 清掉）

## 下一个 READY
- 无——T1.2.2 是产品决策，等用户看完 `vector-comparison-report.md` 后拍板 go / no-go
