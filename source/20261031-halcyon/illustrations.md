# Halcyon 正文配图核对

按 `mycelium-mushroom-illustrations` 及当前参考执行；内置 `image_gen` 独立调用恰好三次，每次一张，未生成 banner。三张均采用红菌盖、白圆点、米白菌柄、黑点眼的小M，并参与核心动作。

| 文件（相对仓库根目录） | 内容与提示词要点 | 大小 |
| --- | --- | ---: |
| `src/assets/images/halcyon-without-language-pretraining-fig-01.png` | 小M一手记录完整预训练账本，一手阻止单张出图账单混入；独立秤盘，不画倍率。标注“预训练总账”“单张出图”。 | 42,076 B |
| `src/assets/images/halcyon-without-language-pretraining-fig-02.png` | 小M双手将文本纸条与图像方块穿织到同一根橙色序列线；无文字标注。 | 34,164 B |
| `src/assets/images/halcyon-without-language-pretraining-fig-03.png` | 小M在CUDA研究台通向Mac的桥头铺木板，保留清晰缺口；标注“CUDA”“待适配”。 | 39,036 B |

共同提示词约束：16:9横版正文图、纯白背景、黑色手绘线条、大量留白、少量红橙蓝；小M认真工作；不使用PPT、标题栏、商业矢量风、幼稚吉祥物、复杂架构或纸纹背景。

压缩：Pillow缩放至1120×630；将高亮中性背景噪点归白，保留米白菌柄；48色、无抖动、PNG优化压缩。三张均小于90,000字节。

核对通过：恰好3张PNG；均为1120×630、严格16:9、48色、四角纯白；已目视核对主题、角色动作、少量文字与未完成桥缺口。三张均为对应占位的正式交付图，无可选图。

原始生成文件保留在 `/Users/jason/.codex/generated_images/01a192e2-a1dc-73b3-8fa3-f9f7cea9ab45/`：

1. `exec-01a77303-dccd-4ed5-9249-90fdb8cc2558.png`
2. `exec-850f724e-fe0b-4f66-a727-9722238ec31b.png`
3. `exec-17a6d598-c2f5-49e0-8074-5121cf09c863.png`

文章Markdown未修改，前后SHA-256均为 `e99fc9e90213e59b12db799d47a32ae85ca02e5e8b344a29b327a7161275eaec`。本任务只新增上述3张配图及本报告。
