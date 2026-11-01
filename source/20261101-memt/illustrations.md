# MemT 正文配图核对

2026-11-01。已读取正文和 `mycelium-mushroom-illustrations` 参考规范，使用内置 `image_gen` 逐张独立生成，恰好三张，无拼图。

| 图片（均在 `src/assets/images/`） | 最终提示主题与用途 | 尺寸 | 文件大小 |
| --- | --- | --- | --- |
| `memt-native-memory-memos-metis-guide-fig-01.png` | 小M双手将可追溯资料卡与模型内记忆盒接入同一任务，两者协作 | 1120×630 | 36,056B |
| `memt-native-memory-memos-metis-guide-fig-02.png` | 小M替换有限槽位记忆盒的内容，旁边权重机器封闭且未被操作；仅标注“状态”“权重” | 1120×630 | 30,009B |
| `memt-native-memory-memos-metis-guide-fig-03.png` | 小M分别保管甲乙钥匙，并主动归档独立快照；三角与圆形区分归属，仅标注“甲”“乙”“保存” | 1120×630 | 30,836B |

共同提示约束：纯白底、黑色手绘线稿、大量留白、极少中文；小M为红菌盖白圆点、米白菌柄、黑点眼，参与核心动作；不画复杂架构、PPT或标题。

处理：Pillow 等比缩放后置于 1120×630 白色画布；中性高亮像素（RGB 最小值≥236、通道差≤12）归白，再以 MEDIANCUT 量化为 48 色、`Dither.NONE`、PNG `optimize=True` / `compress_level=9` 保存。未使用 NumPy。

核对：逐张查看压缩成品，内容与三个占位对应，中文可读、角色动作明确、背景留白干净。程序确认三张均为 16:9、48 色 PNG、四角纯白且小于 90,000B。三张均采用，无可选图。

本任务仅写入三张图片和本报告，未操作文章、banner 或其他原有文件。banner 的 SHA-256 与开始时一致；正文在执行期间发生了外部变化（新增 `lastPublishedAt` 字段），未覆盖或回滚该变化。

原始生成文件保留于 `/Users/jason/.codex/generated_images/01a194a7-6d56-7b31-840e-991932fdcac8/`，依次为：

1. `exec-1c6e3229-82ff-4e59-b0b0-49d95b49b69e.png`
2. `exec-bc48fd48-3deb-49e7-a1c4-15d52307bf3f.png`
3. `exec-750194fd-f805-44be-a95c-d31f7e72bd74.png`
