# NSH 正文配图交付

日期：2026-10-29。对应文章：`src/content/blog/nsh-native-shell-cross-platform-ui.md`。

按 `mycelium-mushroom-illustrations` skill 使用内置 `image_gen.imagegen`，逐张独立生成，共三张；没有拼图。三张均保留红帽白点、浅色菌柄、黑点眼的小M，并让小M执行核心动作。只交付正文图，未修改文章、banner，未部署、未提交。

| 图 | 用途与正文锚点 | 图中文字 | 最终文件 | 尺寸 | 字节 |
| --- | --- | --- | --- | --- | ---: |
| 01 | “NSH 是把 GPUI 搬到手机上了吗？”节后：小M分送共享界面零件，手机与桌面使用各自原生底座；GPUI 独立留在旁边作为选项 | 共享零件／原生底座／GPUI 可选 | [fig-01](../../src/assets/images/nsh-native-shell-cross-platform-ui-fig-01.png) | 1120×630 | 31,547 |
| 02 | “动态模块对已有 App 有什么用？”节的签名与权限说明后：小M检查模块，签名与权限两项检查完成，模块尚未插入宿主 | 签名／权限／再嵌入 | [fig-02](../../src/assets/images/nsh-native-shell-cross-platform-ui-fig-02.png) | 1120×630 | 26,638 |
| 03 | “在 Mac 上实际跑通了什么？”节后：小M实际按动小窗按钮，计数为 2；手持清单，其他平台保留空圈待验 | 小窗先通／逐端再验；另有数字 2 | [fig-03](../../src/assets/images/nsh-native-shell-cross-platform-ui-fig-03.png) | 1120×630 | 25,672 |

三张都按指定锚点保留，没有可选弃图。文章已有的三处图片引用与这些最终文件名一致，无需修改正文。

## 生成记录与原图

- 三张原始生成文件保存在下述工具原件目录，原始尺寸均为 1672×941；仓库不重复保存大尺寸原件。
- [完整逐图提示词与生成源路径](nsh-illustrations-originals/prompts.json)。使用内置工具，没有使用 CLI/API fallback。
- [可重跑导出脚本](nsh-illustrations-originals/prepare.py)：`python3 source/20261029-minilytics-nsh/nsh-illustrations-originals/prepare.py`。
- [技术核验与 SHA-256 清单](nsh-illustrations-originals/manifest.json)。

工具保留的原始文件还位于 `/Users/jason/.codex/generated_images/01a18702-0cd1-70b3-9340-62d15c218355/`，具体文件名记录在提示词 JSON 中；这些工具原件没有移动或删除。工作区已有的其他 `illustrations-originals/` 目录未改动。

## 导出与检查

使用 Pillow 缩放至精确 16:9 的 1120×630，48 色 MEDIANCUT 量化，关闭抖动，以 PNG optimize 与压缩级别 9 保存。量化前将各通道至少为 245、通道差不超过 8 的近白像素归一为纯白，消除生成背景的细微色噪；不重画构图或文字。三张都满足限制，无需降至 960×540。

重新打开最终文件核验：PNG、索引色模式 P、实际 RGB 颜色各 48 种、四角均为 RGB(255,255,255)、每张小于 90,000 字节。整张画面的精确白色像素比例分别约为 91.05%、93.45%、94.92%。

已逐张目视检查最终压缩图：大幅白底留白、黑色手绘线条、小M主动参与、每图最多三处短中文标注；没有网格、围栏、PPT 排版或密集架构图。第一张没有把 GPUI 画成共同基础；第二张分开表达两项检查，没有暗示签名能保证完整安全；第三张仅勾选已验证的小窗，没有把其余平台标为成功。

本任务没有对文章或 banner 发起写入，也没有运行发布或提交命令。banner 的 SHA-256 保持一致。最终核验发现文章在任务期间被其他操作更新（description 调整，新增 `lastPublishedAt: "2026-10-29T09:37:41Z"`），因此不能声称整个工作区的文章处理前后未变；保留并记录该外部变化，未回滚。

处理前记录：

```text
6e774a8beec8335ea87b382186713c27aeda7d5b68d444bfb59d4bd8ed7aed40  src/content/blog/nsh-native-shell-cross-platform-ui.md
4de84926fb3bf27c8c355f3232eae51e4c1487948f73e44440f96a20c9ab9d0c  src/assets/images/nsh-native-shell-cross-platform-ui-banner.jpg
```

最终核验时文章 SHA-256：`3fd97cb16dc4997c9beae00d292180de4c2a2f5fb88b02a4b41b184ac59e5c65`。

Primary session final note: article changes and publication timestamp were intentional. All final art manually accepted. Generated originals remain in /Users/jason/.codex/generated_images/01a18702-0cd1-70b3-9340-62d15c218355/. Duplicate raw raster copies removed from source archive; prepare.py and manifest now point to existing tool originals.
