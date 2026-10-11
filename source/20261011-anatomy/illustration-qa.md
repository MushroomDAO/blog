# Anatomy 正文插图 QA

- 检查日期：2026-10-11。
- 正文：`src/content/blog/anatomy-claude-interactive-isometric-figures.md`。
- 使用技能：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`。
- 已读取该技能的 `style-dna.md`、`mushroom-ip.md`、`composition-patterns.md`、`prompt-template.md` 和 `qa-checklist.md`；同时读取内置 imagegen 工作流。
- 生成方式：内置 `image_gen.imagegen`，逐张独立生成，共三次、三张原创图；没有拼图、外部 API、备用生成器或秘密输出。
- 原图保留在下列生成目录，未覆盖或删除。最终资产为压缩后的独立 PNG。
- 本任务写入的仓库文件仅为三张指定资产及本 QA；未执行正文或 banner 编辑，未发布、提交或写入 KB。Banner 哈希保持一致；正文在执行期间出现其他修改，见下方完整性记录，未回滚这些改动。

## 文件验证

| 图 | 最终路径 | 尺寸 | 字节数 | 纯白像素占比 | 结论 |
| --- | --- | --- | ---: | ---: | --- |
| 01 | `src/assets/images/anatomy-claude-interactive-isometric-figures-fig-01.png` | 1280×720，16:9 | 56259 | 89.53% | 通过，<90000 bytes |
| 02 | `src/assets/images/anatomy-claude-interactive-isometric-figures-fig-02.png` | 1280×720，16:9 | 50250 | 92.58% | 通过，<90000 bytes |
| 03 | `src/assets/images/anatomy-claude-interactive-isometric-figures-fig-03.png` | 1280×720，16:9 | 60882 | 89.84% | 通过，<90000 bytes |

最终文件实际格式为 PNG，128 色索引调色板，无透明背景。四角均为 RGB(255,255,255)。纯白像素占比用于证明背景留白，不能等同于主体外接矩形占比。

压缩方法：Pillow 等比例近似缩放为 1280×720（生成原图 1672×941 / 1672×940 与 16:9 相差不到 0.06%），将近白中性背景归一为纯白，128 色无抖动调色板，PNG optimize/compress_level=9。没有重新绘制元素或改写文字。压缩后逐张通过 `view_image` 实际打开检查。

## 逐张视觉检查

### 01 — 概念与动作的对应

- 认知锚点：一个抽象规则应找到可辨认、可检查的动作对应；对应正文“为什么要把概念做成机器？”。
- 画面：蓝色想法轮廓对应同形凸轮，小M直接用工具制作工作台上的凸轮，凸轮抬起从动杆；一个小装置表达一个对应关系。
- 标注逐字核对：蓝色“想法”、橙色“对应”、红色“动作”，三处可读，没有多余标题。
- 小M：红帽四颗白斑、奶白柄、黑点眼，双手参与制作，黑色手绘轮廓。
- 白底、大量留白，工作台为简单实物草图，没有架构模块、详细技术尺寸或密集流程。
- 通过。装置是说明隐喻，不作为真实机械设计图。

### 02 — 同一模型驱动动作和读数

- 认知锚点：视觉动作和数值读数共用一个模型；对应正文“数字与动作如何保持一致？”。
- 画面：小M双手转动曲柄，橙色共轴贯穿动作轮与机械数字读数器；两端的共同驱动关系可见。
- 标注逐字核对：“动作”“读数”“同一模型”，三处正确可读；无左上角类型标题。
- 读数器“012”是示意计数器符号，没有单位、精度、量程或实测含义，不对应正文百分表的测试数据。
- 小M：红帽四颗白斑、奶白柄、黑点眼，身体发力转动，参与核心驱动。
- 单根轴与两个输出，背景纯白，留白充足；无独立的双模型、复杂齿轮组或 PPT 方框流程。
- 通过。这张对“共同来源”的视觉表达最直接。

### 03 — 先搭建，再检查

- 认知锚点：可操作解释对象需要搭建及检查，不能理解成瞬间输出成品；对应正文“最容易低估的成本是什么？”。
- 画面：小M贴近已搭好的交叉连杆，一手持放大镜检查螺栓接缝，另一手扶住装置；底座旁的扳手与螺栓留下搭建痕迹。
- 标注逐字核对：“先搭好”“再检查”，两处正确可读。
- 小M：红帽四颗白斑、奶白柄、黑点眼，认真检查，处于核心动作中。
- 白底和大量留白；放大镜覆盖实际关节，没有浮动截图、瞬间完成符号、多阶段拼图或密集流程图。
- 通过。装置只表达搭建后的检查，不证明工程几何或机械运动正确。

## 共同检查结论

三图分别使用“形状变动作”“共轴驱动”“放大镜检查关节”的新隐喻，没有复刻技能旧案例。均为单幅横版白底场景，小M参与主动作，中文批注仅两到三处，红橙蓝颜色克制，无左上角类别标题、商业海报、真实 UI 或复杂背景。压缩后笔画、黑点眼、白斑及中文保持清楚。三张均为本次必需正文资产，全部通过，不设置可选图。

## 原图来源与完整性

范围验证记录：本任务未运行文章编辑、Git 暂存、提交、发布或 KB 命令。末次状态检查发现工作区另有 `public/explainers/anatomy-dial-indicator.html` 被暂存，且文章哈希与开始时不同，这些均不由本任务写入。本任务保留并未回滚其他工作。

- 正文开始 SHA-256：`f55346c837d700f7413aa29a05867ac8cf88bdc15085eb7dd09e02f8616b5c62`。
- 正文末次检查 SHA-256：`b1b4438cbef5f53a95f357d1d1d53f8d9a7c685ae1fa8685cd12335c72eccefe`。存在其他修改，不能宣称正文原字节保持一致。
- Banner 开始及末次 SHA-256 均为：`aad78db435259678a291d3e6dea408cb54011bcd41c7ab51ef6020e4a3a9d61e`。
- 三份原图 SHA-256 均与压缩前一致；最终 PNG 完整性、格式、精确 16:9 和 <90000 字节验证通过。
- QA 文件实际存在；`source/` 由仓库忽略规则排除，未为此改动忽略规则或强制暂存。

### 01

- 原图：`/Users/jason/.codex/generated_images/01a12996-89cc-77a0-a4ea-da72f087ad5b/exec-68cb7274-213c-4dc7-ab47-c8bd537980d2.png`
- 原图尺寸：1672×941；1136670 bytes。
- 原图 SHA-256：`edc553a80fcf1dc5e73916a221d9dbfa9d81ae75df4cff205ecad3cfca2bd519`。
- 最终 PNG SHA-256：`e307ff5b2d619d883121bc6be3a33b898f495c6bbe1304f43b823dd3cee4cab1`。

### 02

- 原图：`/Users/jason/.codex/generated_images/01a12996-89cc-77a0-a4ea-da72f087ad5b/exec-9e76611f-9e45-4be3-b57f-8d6b82707fea.png`
- 原图尺寸：1672×940；1067950 bytes。
- 原图 SHA-256：`f6a98647e24326f3523a4289ad5c04cd38217e3d1ae86a3ed5b8bb75c962c737`。
- 最终 PNG SHA-256：`a1f688bdf56a25de2ea0809e73a69684ce34697fd89530eeec0901e702dcc9b5`。

### 03

- 原图：`/Users/jason/.codex/generated_images/01a12996-89cc-77a0-a4ea-da72f087ad5b/exec-90920bea-a718-47e6-a5d6-4133ced86231.png`
- 原图尺寸：1672×941；1141486 bytes。
- 原图 SHA-256：`267e52c8f50e6e2e30b1d74fc1a5f7b3f7e007436240dd1842ee4214ab9c81f2`。
- 最终 PNG SHA-256：`7d7becf709c26c282bbc9f11ab5b8a5e479cbd25d41924ab7c1ba8a96f1421b7`。


## 实际生成提示词

以下为三次内置工具使用的完整提示词，`transparent_background=false`，均未传入参考图。

### 01

```text
Generate exactly ONE original standalone 16:9 horizontal PNG Chinese article body illustration, preferably 1536x864, not a montage or panels. Pure opaque #FFFFFF background, no paper texture, no shadows, no gradients. Thin slightly wobbly BLACK hand-drawn pen outlines, restrained flat red/orange/blue accents, huge clean white margins. Scene occupies about 45–55% of canvas, at least 40% untouched whitespace. Xiao-M is the central active worker: a small mushroom with a flat RED semicircular cap with exactly FOUR WHITE round spots, a CREAM stem with two BLACK dot eyes, thin black outlined arms and legs, serious deadpan expression. No costume, smiling, sparkles, cute mascot, commercial illustration, vector polish, PPT, dense architecture, flowchart, UI screenshot, top-left title, header, legend, watermark or signature. One scene explains one cognitive anchor; labels sparse, correct short handwritten Chinese. Do not copy prior illustrations. Scene 01 — concept becomes understandable motion. On a simple tiny workbench in the center, Xiao-M is physically shaping ONE blue floating loose idea-loop into a tangible curved CAM with a hand tool, and positioning that cam on a short spindle beneath ONE little follower lever. The one-loop idea and the cam outline visibly correspond: the cam's single raised bump lifts the follower as it rotates. Keep it a surreal product sketch about ONE concept-to-motion correspondence, not an engineering drawing. Only the hand tool, cam, follower, and bench; no other machines or elaborate gears. Xiao-M's hands directly work on the central mechanism. A small orange curved motion mark by the cam shows rotation. Render only these three Chinese annotations, next to their referents (not at upper left): '想法' in blue next to the loose loop; '对应' in orange by the transforming hand; '动作' in red by the raised follower. No numbers, English or additional text.
```

### 02

```text
Generate exactly ONE original standalone 16:9 horizontal PNG Chinese article body illustration, preferably 1536x864, not a montage or panels. Pure opaque #FFFFFF background, no paper texture, no shadows, no gradients. Thin slightly wobbly BLACK hand-drawn pen outlines, restrained flat red/orange/blue accents, huge clean white margins. Scene occupies about 45–55% of canvas, at least 40% untouched whitespace. Xiao-M is the central active worker: a small mushroom with a flat RED semicircular cap with exactly FOUR WHITE round spots, a CREAM stem with two BLACK dot eyes, thin black outlined arms and legs, serious deadpan expression. No costume, smiling, sparkles, cute mascot, commercial illustration, vector polish, PPT, dense architecture, flowchart, UI screenshot, top-left title, header, legend, watermark or signature. One scene explains one cognitive anchor; labels sparse, correct short handwritten Chinese. Do not copy prior illustrations. Scene 02 — one shared model drives movement and readout. A completely new single apparatus, no workbench: Xiao-M at center-left energetically turns a hand crank, both hands grasping it. The crank is DIRECTLY CONNECTED to ONE visibly continuous slender HORIZONTAL ORANGE mechanical shaft on two plain black supports. Along the SAME continuous shaft sit two clear attachments: first a large open black action wheel with three spokes and a single red paddle plus a rotation gesture; farther right a small mechanical rolling numeral drum in a simple window frame. Shaft visibly enters BOTH, so simultaneous motion and readout are mechanically linked rather than two separate sources. The numeral drum has small '0 1 2' on its rolling edge to indicate a generic counting sequence only, NO units, no decimal, no measured quantity, no factual measurement claim. Leave huge white space all around. Only three Chinese handwritten labels near the relevant objects: '同一模型' in orange beneath the shared shaft, '动作' in red near the paddle wheel, '读数' in blue by the numeral window. No additional text, left-upper category heading, boxes, flowchart or complex gears. Red cap FOUR white spots, cream stem, black dot eyes; character central to cranking, sparse hand-sketch lines.
```

### 03

```text
Generate exactly ONE original standalone 16:9 horizontal PNG Chinese article body illustration, preferably 1536x864, not a montage or panels. Pure opaque #FFFFFF background, no paper texture, no shadows, no gradients. Thin slightly wobbly BLACK hand-drawn pen outlines, restrained flat red/orange/blue accents, huge clean white margins. Scene occupies about 45–55% of canvas, at least 40% untouched whitespace. Xiao-M is the central active worker: a small mushroom with a flat RED semicircular cap with exactly FOUR WHITE round spots, a CREAM stem with two BLACK dot eyes, thin black outlined arms and legs, serious deadpan expression. No costume, smiling, sparkles, cute mascot, commercial illustration, vector polish, PPT, dense architecture, flowchart, UI screenshot, top-left title, header, legend, watermark or signature. One scene explains one cognitive anchor; labels sparse, correct short handwritten Chinese. Do not copy prior illustrations. Scene 03 — assemble first, then inspect connections. A fresh intimate hand-drawn maintenance scene, not a wide shaft or cam-workbench. At the center is ONE already assembled small scissor-linkage mechanism with a simple pivoting arm on a plain low base, only two crossed black bars, three clearly legible bolt joints and a little orange movable tip. Xiao-M kneels close in the CENTRAL ACTION, cream stem, FOUR white cap dots, holds a large blue outlined magnifying glass DIRECTLY OVER the central joint with one hand, steadies the assembled arm with the other. Through the glass the joint is slightly enlarged, revealing its two joined plates and bolt, not a separate floating inset. A small spanner and ONE leftover bolt laid beside the base quietly show prior assembly work; these are sparse supporting traces, not a second scene. The illustration communicates inspection after a real build rather than magical instantaneous image creation. One small orange curved motion mark at the tip. Render only TWO short Chinese handwritten notes near their referents: '先搭好' in orange beside the base and tools; '再检查' in blue beside the magnifying glass. No numbers, measurements, extra text, before/after panels, dense flowchart, top-left heading, instant-output sparkle, many components or architectural schematic. Keep all upper-left and outer margins blank, about half the canvas empty white.
```

