# LFM3 正文配图

2026-10-29。使用 `mycelium-mushroom-illustrations` 与内置 `image_gen`，分别生成三张独立图，未拼图。已读文章及 skill 的 style-dna、mushroom-ip、composition-patterns、prompt-template、qa-checklist 参考。

| 图 | 用途 | 最终文件 | 尺寸 | 字节 | 唯一色 / 重复色号 |
| --- | --- | --- | --- | ---: | --- |
| 1 | 共同底座与专用工具头 | [fig-01.png](../../src/assets/images/lfm3-liquid-ai-local-multimodal-models-fig-01.png) | 1120×630 | 42149 | 48 / 0 |
| 2 | 类型化判定、概率与分流 | [fig-02.png](../../src/assets/images/lfm3-liquid-ai-local-multimodal-models-fig-02.png) | 1120×630 | 31106 | 48 / 0 |
| 3 | 小权重之外的内存空间 | [fig-03.png](../../src/assets/images/lfm3-liquid-ai-local-multimodal-models-fig-03.png) | 1120×630 | 40996 | 48 / 0 |

原图均保留于现有 `~/.codex/generated_images`，没有将大原图复制到 source。最终文件经 Lanczos 等比适配白色画布、近白像素归白、48 色 MEDIANCUT 无抖动量化、重复 RGB 索引合并、精简 PNG 调色板并压缩；全部小于 90,000 字节，无需降至 960×540。

## 原图与视觉 QA

- **图 1** 原图：`/Users/jason/.codex/generated_images/01a18715-9d86-7872-b190-a3664e18b105/exec-dedc3051-5f67-46e4-8a5d-b7333a555a11.png`（1672×941，1139427 字节）。小M双手装镜头，单一底座旁只有一个备用麦克风头。标注：共同底座、按任务选、专用头。工具头是共同训练基础与专用检查点的隐喻，不表示运行时切换附件即可获得不同模型。
- **图 2** 原图：`/Users/jason/.codex/generated_images/01a18715-9d86-7872-b190-a3664e18b105/exec-3f722ab0-a402-4961-b5fa-ecccf0e7d30f.png`（1672×941，1148614 字节）。小M转动压机并引导结果卡；一份输入得到“类型：退款”“概率：0.92”，再向工具或人工分流。第三处标注为“输入”。0.92 仅作示意，不是实测校准或业务阈值。
- **图 3** 原图：`/Users/jason/.codex/generated_images/01a18715-9d86-7872-b190-a3664e18b105/exec-c2b27994-6b98-4d2b-83a0-2c9e0699febf.png`（1672×941，1171707 字节）。小M双手拉开箱体，为长纸带和运行状态线圈腾出空间；权重块明显较小。标注：权重、长上下文、运行状态。不代表实测峰值内存或精确比例。

逐张打开并检查的是最终 PNG：16:9、纯白背景、红盖白点小M主动完成动作，中文各三处且可读，无标题、段落、聊天记录、六模型密集表、背景纹理、网格、围栏或 PPT 排版。精确白色像素分别占 89.88%、91.83%、92.94%；四角均为 RGB(255,255,255)。索引 PNG 全部实际使用 48 色，整个已存调色板无重复 RGB 项。三张均通过，无可选弃图。

## 实际生成提示词

每次完整提示词 = 下列共用前缀 + 对应场景后缀；各调用一次，均 `transparent_background=false`，不引用其他生成图。

共用前缀：

```text
Use case: stylized-concept. Generate exactly ONE independent 16:9 horizontal Chinese article BODY illustration, ideally 1792x1008, not a montage. Pure solid #FFFFFF background. Sparse thin black slightly wobbly hand-drawn pen outlines, small flat red/orange/blue accents, enormous untouched white margins. No texture, grain, wash, shading, gradient or shadow. Main scene spans about 55% of the width and 50% of the height; at least 60% of pixels empty white. Adult deadpan absurd product sketch, informal organic composition, no polished vector styling, no commercial illustration, no cute or childish mascot. One XiaoM mushroom is the essential active worker: RED rounded cap with 3–5 WHITE round spots, pale cream stem body with black outlines, two tiny BLACK dot eyes, thin arms and legs, blank serious face, no clothes, no smiling. Do not make the cap black. Small red cap is a flat color area. Orange only for motion/flow, blue for small secondary details. No titles, captions, explanatory paragraphs, logos, frames, fences, grids, panels, PPT layout, tables, architecture chart, UI, chat bubbles or conversation transcripts. Render only the specifically listed short labels, in small readable Chinese handwriting, at most three Chinese labels in the whole image. No other words.
```

图 1 场景后缀：

```text
Core idea: one shared learned foundation, with task-specific specialized model attachments, rather than a dense family chart.
Physical scene: a single low, squat, unbranded hand-powered machine body on a short solid base at the center, with one simple top connector. XiaoM leans into the work, BOTH arms lifting a small camera-lens-shaped attachment and actively screwing it onto that connector. One spare microphone-shaped attachment lies loose nearby, small and separated by white space. Only TWO attachments total including the one being installed; only ONE shared base, no replicated models, no six-model chart. The attachment is clearly distinct from the unchanged base. A tiny orange curved motion stroke at the joint shows the installing action. No arrows radiating to many nodes. No toolbox, conveyor, stamp or background scene. This is an editorial metaphor for related specialized checkpoints, not an actual runtime interface.
Exactly three short handwritten labels beside the objects, no heading: “共同底座” by the base, “按任务选” near XiaoM's hands, “专用头” near the lens attachment.
```

图 2 场景后缀：

```text
Core idea: a single input is evaluated to obtain a typed categorical decision WITH its probability, then used for routing; this is not a generated chat answer.
Physical scene: XiaoM, near the center, actively rotates the crank of one tiny low-tech tabletop decision press with one hand and guides its emerging small result tag with the other. Exactly ONE folded input ticket enters at left; do not draw lines pretending to be prose on it. The press outputs exactly ONE small white tag with two handwritten short fields. The tag is fed directly toward a single modest Y-shaped wooden chute on the right. An orange track continues along one branch toward one small wrench pictogram; the other branch ends at a small simple human outline pictogram. Keep the press and fork intimate and organically hand sketched, not boxes in a flowchart. The result tag is legible and central to the action, the chosen path clearly orange, and all other objects kept very small. No speech bubbles, no transcripts, no generated paragraph, no extra tickets or repeated branches.
Only these THREE Chinese labels anywhere: “输入” beside the input ticket, and exactly “类型：退款” and “概率：0.92” written on the output tag as two short fields. The 0.92 is an illustrative example, no benchmark or latency claims.
```

图 3 场景后缀：

```text
Core idea: small model weights still need additional memory room for long context and runtime state. Do not draw a performance or numeric memory chart.
Physical scene: a single open travel suitcase in a sparse oblique hand-drawn view, with NO inner dividers or compartments. A tiny compact plain cuboid weight block already occupies only a small corner. A much larger loose accordion-folded strip of blank paper representing long context occupies the middle, broad and obvious but with only 4–5 folds, no text or ruled lines. XiaoM braces a foot and actively pulls the suitcase's expandable right wall outward with BOTH arms to make more room for a small pair of blue irregular loop coils representing runtime state, which are squeezed alongside the accordion. Show the expansion with just two tiny orange motion marks, no alternate before/after panel or complex mechanism. The small block must be visibly much smaller than the space occupied by context and state. Preserve lots of blank white around the one suitcase scene. Do not add model sizes, percentages or measured RAM claims. No computer, chart, grid, fence, title or explanatory note.
Exactly THREE short Chinese handwritten labels each near the corresponding physical object: “权重” by the tiny block, “长上下文” by the accordion strip, “运行状态” by the blue loops.
```

## 范围核验

本次仅写入三张最终图与本报告；没有编辑文章或 banner，没有执行部署或提交。Banner 摘要与操作前一致。结束核验时发现文章由并发外部操作新增了 `lastPublishedAt: "2026-10-29T09:59:15Z"`，因此不声称文章字节未变，也未回滚该改动。保留原图并核验摘要未变。

- 文章操作前：`b9dfe53fe823e75fa84d29238d9e1e53f62a33a243b0e58597e03e35c0afc729`
- 文章结束核验：`668b43441b4cc637841b9f9858a05404e32d24b82987a9a70b842e8cfb920303`
- Banner：`87676d515a0ed00109d796196f80dd37657e17e2e4696965373466885434465e`


Primary publication note: timestamp and explicit illustrative-probability captions were intentional primary-session edits; final three illustrations were manually accepted before build. Article and image hashes stayed unchanged through the build.
