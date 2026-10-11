# Saluki 正文配图 QA

日期：2026-10-11
文章：`src/content/blog/saluki-27b-gguf-tools-bonsai2.md`
生成方式：内置 `image_gen.imagegen`，共三次独立调用，每次只生成一张；无拼图、无 API/CLI 替代。

已阅读：
- `/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`
- 同 skill 的 `references/style-dna.md`、`mushroom-ip.md`、`composition-patterns.md`、`prompt-template.md`、`qa-checklist.md`
- `/Users/jason/.codex/skills/.system/imagegen/SKILL.md`

## 交付与目视检查

| 图 | 文件 | 像素 | 文件大小 | 核心动作与中文标注 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 01 | `src/assets/images/saluki-27b-gguf-tools-bonsai2-fig-01.png` | 1280×720 | 46,101 bytes | 小M拉紧压缩带，把折叠权重挤入小行李箱；外侧工具插口保持露出，一插口连接橙色线、一插口空闲。「权重」「工具插口」可读。 | 通过 |
| 02 | `src/assets/images/saluki-27b-gguf-tools-bonsai2-fig-02.png` | 1280×720 | 17,142 bytes | 小M握持两张成绩单，尝试对齐后发现圆形/三角形与方形/三角形题组不同。「题目不同」「先别比」可读，无数值、奖杯或胜负暗示。 | 通过，见细节记录 |
| 03 | `src/assets/images/saluki-27b-gguf-tools-bonsai2-fig-03.png` | 1280×720 | 32,303 bytes | 小M双手装载紧凑权重包；对话纸卷和缓冲线圈分别占据另两个座位。「权重」「上下文」「计算缓冲」可读。 | 通过 |

三张均已用 `view_image` 检查最终压缩文件。均为严格 16:9、白色背景、大量留白、黑色手绘轮廓；小M均为红菌盖、四个白点、米白菌柄、黑点眼，直接参与核心动作。三种场景分别为压缩行李、错位试卷、载货渡船，互不重复，无左上角类型标题、PPT 网格或流程图。

细节记录：
- 图 02：纸卡外缘另有两处握持手部轮廓，形成怪诞的额外手部，不是干净的两臂解剖；不影响「题组不同、暂缓比较」的判断。保留该图，不追加生成，以遵守恰好三张的要求。
- 图 03：船体有浅棕平涂、缓冲线圈为蓝灰平涂；这些是物件填色，背景仍为纯白。低色数压缩使物件局部有色阶痕迹，线条及短标注保持清楚。
- 原始生成文件为 1672×941，接近 16:9；交付用 ImageMagick 重采样为 1280×720，比例误差很小。
- 工具三次均成功，无需执行失败恢复；没有使用历史生成图替代本次生成。

## 压缩与原始文件

三张生成后均在本轮先 `cp` 到指定资产路径，再压缩。原始文件留在内置工具默认生成目录，未覆盖、未移动、未删除。

处理方式：`magick -resize '1280x720!' -dither None -colors N -strip -define png:compression-level=9 PNG8:...`。
图 01、03 使用 24 色量化；图 02 使用 16 色量化。将近白背景调色板项 `#FEFEFE`（图 01 另含 `#FEFEFD`）映射为 `#FFFFFF`，合并近白颜色，确保纯白底。输出为索引色 PNG；每张严格小于 90,000 bytes。只做尺寸和调色板处理，未用绘图脚本替代生成。

- 图 01 原始文件：`/Users/jason/.codex/generated_images/01a1298c-f702-7d53-b85f-ad09a899093f/exec-6fc62458-84f3-4ae4-8dab-d65c2c084c53.png`
- 图 02 原始文件：`/Users/jason/.codex/generated_images/01a1298c-f702-7d53-b85f-ad09a899093f/exec-e2931083-dced-41f9-a574-149bf49f60ac.png`
- 图 03 原始文件：`/Users/jason/.codex/generated_images/01a1298c-f702-7d53-b85f-ad09a899093f/exec-5d84bf51-c9ae-4eb6-959f-d0eb85795081.png`

## 最终生成提示词

### 图 01

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body illustration, preferably 1536x864 or 2048x1152. Pure white #FFFFFF background, thin black slightly wobbly hand-drawn pen outlines, flat sparse red/orange/blue accents, plenty of white space (at least 45%), no shadows, gradients, texture, or scenery. Not a PPT, flowchart, polished vector, commercial illustration, cute mascot poster or children's illustration. No title, especially no top-left title. One scene, no montage.
Character Xiao-M: small deadpan serious mushroom operator, rounded RED mushroom cap with exactly FOUR WHITE round dots, CREAM stem body, BLACK dot eyes, thin black outlines, tiny thin arms and legs, no smile, no clothing, no black-filled cap. Xiao-M performs the core action.
Core idea: low-bit quantization compresses bulky model weights into a small portable file, while accessible standard tool interfaces remain. No claim of lossless capabilities or faster speed.
Scene: a comically overstuffed small open travel suitcase sits in the lower-middle of a mostly empty white sheet. A bulky mass of accordion-folded rectangular model-weight sheets protrudes upward from it. Xiao-M is braced on the right, actively pulling a simple hand-operated luggage compression strap down across the accordion mass, squeezing it into the small suitcase. Preserve obvious exposed plug sockets on the OUTSIDE FRONT side of the suitcase, below the strap and unobstructed: two simple line-drawn tool sockets, one with a short orange plug connected and the other empty. Do not make the suitcase a toolbox or add stamping, conveyors or multiple stages. The mushroom pulling the strap is essential to the action. One restrained orange curved motion stroke beside the strap. The unfolded portion is bulky; the folds inside the case are tight. Render the entire action coherently with very few objects, subject occupies about half the canvas and large quiet upper white area.
Only these TWO small handwritten Chinese annotations near their objects, correct and legible: "权重" in black near the bulky folded stack; "工具插口" in blue near the external accessible sockets. No other text, letters, scores, symbols as labels, brands or watermarks. Red fill only on cap. Keep sockets clearly usable rather than squashed.
```

### 图 02

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body image, preferably 1536x864 or 2048x1152. Pure WHITE #FFFFFF background with at least 50% empty white space. Thin BLACK slightly wobbly hand-drawn pen outlines, flat accents, no shadows, texture, gradients, complex background. Sparse red/orange/blue Chinese notes. No montage, panel borders, PPT, flowchart, infographic grid, commercial vector finish or childish cute poster. No top-left title or other title.
Xiao-M is the CENTRAL action subject: serious deadpan mushroom operator with rounded RED cap with exactly FOUR WHITE polka dots, CREAM stem, BLACK dot eyes, tiny thin arms and legs, fine black hand-drawn outlines, no smile, sparkle, clothing or black-filled cap.
Concept: two aggregate benchmark scorecards cannot be ranked when their question sets differ. No winner claimed, no dense numbers, no percentages, no model brand labels.
Invent a single physical scene: Xiao-M in the lower-middle is HOLDING two loose paper scorecards in opposite hands and trying to superimpose their edges like a tailor checking two incompatible paper patterns. The cards are fanned apart, facing the viewer, one tilted left and the other right; their blank upper score areas are equally sized, contain no scores or rankings. On the bottom part of the LEFT card draw three simple task/question cutouts like circle-circle-triangle; on the RIGHT card draw square-triangle-square. The different silhouettes should be obvious, like the two sets of holes in paper do not line up. A small bent orange alignment stroke between the paper corners shows the attempted overlap; it ends at a tiny red stop dash, not a crossing-out of either card. Xiao-M physically grips both paper edges and looks down at the nonmatching task shapes with calm realization. No extra characters, balance scale, trophy, medal, podium, checkmarks or loser symbols. Both cards have equal visual dignity. The only two labels are small handwritten Chinese: "题目不同" in BLUE beside the mismatched question cutouts, with one short blue pointer; "先别比" in RED below Xiao-M's hands, as a restrained marginal note. Render those Chinese exactly, no other lettering. Use quiet off-center organic hand-drawn scene rather than symmetrical slide layout, keep very large empty upper area. Focus on realization that the test questions differ, not card scores.
```

### 图 03

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body illustration, preferably 1536x864 or 2048x1152. Pure WHITE #FFFFFF background. Minimal thin BLACK hand-drawn slightly wobbly outlines, restrained flat red/orange/blue notes, at least 45% empty white space. No gradients, shadows, paper texture, complex scenery, commercial vector finish, childish cute poster, PPT, flowchart or formal architecture diagram. No montage. No title, especially no top-left type title.
Core idea: fitting compressed model WEIGHTS does not mean all runtime memory fits. Context/KV cache and computation buffers ALSO need physical seats, even when the weights are small. Do not imply an 8GB machine can run an 8GB model.
Main character Xiao-M: rounded RED mushroom cap with exactly FOUR WHITE round dots, CREAM stem body, BLACK dot eyes, thin black hand-drawn outline, tiny thin arms and legs, blank serious deadpan face, no smile, clothes or sparkle. Xiao-M must actively load the boat, not watch it.
Invent one coherent absurd ferry scene on an otherwise empty sheet. Small open wooden rowboat with three clearly separated passenger benches drawn in a spare side/three-quarter view in the lower center, floating on just two short black water ripples, no landscape. Xiao-M stands braced beside the boat, both thin hands actively lowering one compact strapped rectangular bundle of accordion-folded weights onto the FRONT bench. The other TWO benches already each have a passenger-object that cannot be ignored: on the middle bench a looped folded scroll of conversation paper, and on the rear bench a coiled computation-buffer spool. Neither has a face. Each object occupies its own seat visibly; the small weights bundle does not replace them. Keep a large amount of surrounding white. One short ORANGE downward motion stroke by Xiao-M's loading hands. Don't draw other mushrooms, suitcases, tools, lifejackets, capacities, percentages, computer UI, or many cargo pieces.
Only THREE short correct handwritten Chinese annotations placed beside their corresponding objects, with tiny restrained pointers if necessary: "权重" in black beside compact bundle, "上下文" in blue beside folded conversation scroll, "计算缓冲" in red beside coiled buffer spool. No other text, letters, digits, labels or watermarks. All three labels clear and small, not explanatory paragraphs. Mushroom cap identity red is separate from red buffer annotation. Action, bench occupancy and memory-budget metaphor should be understood at a glance; no sinking catastrophe or winner claim.
```

## 工作范围

本轮只写入上述三个资产文件和本 QA 文件。文章及 banner 均未修改；未发布、未 commit、未写 KB。

