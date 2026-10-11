# Loopera 正文插图：提示词与 QA

日期：2026-10-11。使用内置 `image_gen.imagegen`，逐张调用三次，生成三个独立图像；无 API/CLI 生图回退，无孤儿输出恢复（本次三次生成均成功）。

## 输入与参考

- 正文：`src/content/blog/loopera-factor-research-evidence-gates.md`
- Skill：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`
- 已读取全部五份参考：`style-dna.md`、`mushroom-ip.md`、`composition-patterns.md`、`prompt-template.md`、`qa-checklist.md`。
- 未使用旧案例图片；三张隐喻按用户指定与正文认知锚点设计。

## 最终资产与原始来源

原始生成目录：`/Users/jason/.codex/generated_images/01a12981-c535-7e82-bf7f-70a11cd962ae/`。保留原始文件。

| 图 | 最终文件（src/assets/images/） | 原始 PNG | 尺寸 | 字节 |
| --- | --- | --- | --- | ---: |
| 01 | loopera-factor-research-evidence-gates-fig-01.png | exec-0f1f182a-5da9-4ba0-ae9a-a7001ca597f2.png | 1600×900 | 35,639 |
| 02 | loopera-factor-research-evidence-gates-fig-02.png | exec-1a21b7d7-d365-42ef-ae8c-3b9825192c4c.png | 1600×900 | 48,594 |
| 03 | loopera-factor-research-evidence-gates-fig-03.png | exec-a75681fe-a34a-49fb-bfdb-83f5ee133156.png | 1600×900 | 52,959 |

## QA 摘要

三张生成结果及三张压缩后最终 PNG 均已逐张目视检查。所有最终图为 16:9，均低于 90,000 字节；白底为 #FFFFFF，四周有大量留白。小M均有红色菌盖、白色圆点、浅色菌柄、黑点眼与细肢体，亲自承担核心动作。黑色手绘线条为主，中文标签短且正确，无左上角标题、无横幅、无密集信息图。

- 图 01：通过。小M转动棱镜操作柄，将单一经营现象分成竞争解释与可检验假设。仅有「现象」「机制」「假设」三个标签。
- 图 02：通过。小M握住吊桥操作杆，支撑候选通过；携带证据文件者在桥上，无材料者停在左岸。仅有「候选」「证据」「验证」三个标签。
- 图 03：通过。小M持针与橙线，将失败原因纸片缝入根系，树上长出三片新叶。仅有「失败原因」「研究记忆」「新假设」三个标签。叶片含少量浅绿色，画面仍以稀疏黑线与红帽为主。

## ImageMagick 处理

仅进行用户要求的 PNG 尺寸与压缩处理，并归一近白背景。命令参数：

```text
magick ORIGINAL.png -resize 1600x900! -background white -alpha remove -alpha off -channel RGB -white-threshold 95% +channel -strip -dither None -colors 48 -define png:compression-level=9 -define png:compression-filter=5 PNG8:DESTINATION.png
```

使用 48 色无抖动索引 PNG，保留标签、动作和细线。未另行添加标签或重绘。三个最终图左上角像素均为 srgb(255,255,255)。

最终 SHA-256：

```text
fig-01 c9fe6180396dc3f9bb9a3a7698d9b84f90905cc994b63ffaa2922ba38f515cd4
fig-02 5a3f58aafd3043afc1e0527b3e9738ea56cacd8d732504dc8ea200e818c72b41
fig-03 a38478de21e433733e65c614f60d5c207b13137bc2758f3ec47bb805d282547c
```

任务范围：仅新增以上三个 PNG 与本 QA 文件。正文 SHA-256 校验值为 `b5618185056ef40c0bc228cd98b680c8a330f95e63c54bc153aa3963d14a0f80`；正文未修改。未发布、未提交、未调用 KB 工具。

## 原始生成提示词

### 图 01

```text
Generate exactly ONE standalone illustration, a 16:9 horizontal Chinese blog body image, intended canvas 1600 x 900. Use case: illustration-story.
Visual DNA: completely pure white #FFFFFF background, sparse thin black hand-drawn pen line art, slightly wobbly strokes, large quiet margins and at least 40% empty white space. Flat limited colors: red cap, pale cream stem, tiny orange connecting lines and sparse blue/red Chinese handwriting. No paper texture, noise, beige backdrop, gradient, shadows, polished vector art, 3D, commercial illustration, cute mascot or children's poster, UI, PPT, grid, dense infographic, banner, border or watermark. No top-left title, no heading anywhere.
Required central actor: Xiao-M, one small serious deadpan hand-drawn mushroom creature. Rounded RED dome cap with 3–5 WHITE circular dots, black pen outline, PALE CREAM stem body, two small BLACK dot eyes on the pale stem, very thin arms and legs, blank expression without smile, no clothing. Xiao-M personally performs the core physical action; never just watches from a corner. Keep the scene simple and readable, one physical metaphor, objects concentrated in the middle 50–60% of the canvas.
Chinese text must be short, correctly rendered and limited to the exact three labels specified below; no other text, numbers, formulas or English. Labels sit next to relevant objects, not as a title.
Core idea: one business observation is not proof of one mechanism; compare competing explanations before choosing a testable hypothesis.
Scene: Xiao-M stands at the central triangular glass prism, both hands actively rotating its small adjustment handle. A single modest orange beam coming from a small observation sheet on the left enters the prism. The prism separates it into three thin divergent rays on the right, ending at three simple unfilled thought-shapes representing competing explanations. One endpoint has a tiny testable hypothesis slip. The prism and Xiao-M are the core action, with minimal black outlines and no rainbow gradients or optical realism.
Text (verbatim): "现象" next to the single input sheet; "机制" next to the split explanations; "假设" next to the small chosen hypothesis slip. Handwritten black/blue/red Chinese, only these three labels. Keep all three readable.
```

### 图 02

```text
Generate exactly ONE standalone illustration, a 16:9 horizontal Chinese blog body image, intended canvas 1600 x 900. Use case: illustration-story.
Visual DNA: completely pure white #FFFFFF background, sparse thin black hand-drawn pen line art, slightly wobbly strokes, large quiet margins and at least 40% empty white space. Flat limited colors: red cap, pale cream stem, tiny orange connecting lines and sparse blue/red Chinese handwriting. No paper texture, noise, beige backdrop, gradient, shadows, polished vector art, 3D, commercial illustration, cute mascot or children's poster, UI, PPT, grid, dense infographic, banner, border or watermark. No top-left title, no heading anywhere.
Required central actor: Xiao-M, one small serious deadpan hand-drawn mushroom creature. Rounded RED dome cap with 3–5 WHITE circular dots, black pen outline, PALE CREAM stem body, two small BLACK dot eyes on the pale stem, very thin arms and legs, blank expression without smile, no clothing. Xiao-M personally performs the core physical action; never just watches from a corner. Keep the scene simple and readable, one physical metaphor, objects concentrated in the middle 50–60% of the canvas.
Chinese text must be short, correctly rendered and limited to the exact three labels specified below; no other text, numbers, formulas or English. Labels sit next to relevant objects, not as a title.
Core idea: evidence gates require supporting material; only a documented candidate can cross into validation.
Scene: a short narrow hand-drawn hinged drawbridge spans a small gap between two plain banks. Xiao-M personally balances and operates the bridge at its hinge, using both thin arms on a simple lever and rope counterbalance. A single plain walking candidate figure carrying a visible folder of supporting documents crosses the lowered bridge toward the right bank. A second plain candidate without documents waits safely at the left approach. Candidates are minimal anonymous outline shapes, not additional mushrooms. Xiao-M is visibly doing the work that holds the passage in balance. No elaborate castle, landscape, scale diagram or checklists; only bridge, lever, supporting folder and simple figures.
Text (verbatim): "候选" by the left approach; "证据" beside the crossing candidate's documents; "验证" beside the right bank. Sparse handwritten black/blue/red Chinese, only these three labels.
```

### 图 03

```text
Generate exactly ONE standalone illustration, a 16:9 horizontal Chinese blog body image, intended canvas 1600 x 900. Use case: illustration-story.
Visual DNA: completely pure white #FFFFFF background, sparse thin black hand-drawn pen line art, slightly wobbly strokes, large quiet margins and at least 40% empty white space. Flat limited colors: red cap, pale cream stem, tiny orange connecting lines and sparse blue/red Chinese handwriting. No paper texture, noise, beige backdrop, gradient, shadows, polished vector art, 3D, commercial illustration, cute mascot or children's poster, UI, PPT, grid, dense infographic, banner, border or watermark. No top-left title, no heading anywhere.
Required central actor: Xiao-M, one small serious deadpan hand-drawn mushroom creature. Rounded RED dome cap with 3–5 WHITE circular dots, black pen outline, PALE CREAM stem body, two small BLACK dot eyes on the pale stem, very thin arms and legs, blank expression without smile, no clothing. Xiao-M personally performs the core physical action; never just watches from a corner. Keep the scene simple and readable, one physical metaphor, objects concentrated in the middle 50–60% of the canvas.
Chinese text must be short, correctly rendered and limited to the exact three labels specified below; no other text, numbers, formulas or English. Labels sit next to relevant objects, not as a title.
Core idea: specific failure reasons stored in research memory nourish new hypotheses.
Scene: one small research tree on the right with a thin black trunk, a few simple branches and exactly three fresh outlined leaves. Roots below it are visible as a sparse black branching network floating on white, no soil fill. Xiao-M crouches at the roots, actively holding a sewing needle and stitching small failure-reason paper scraps directly INTO the roots with one thin orange thread. The thread joins the root system and the new idea leaves emerge above. Make the needle, hand action and stitches legible, not a character simply beside a tree. Only a few paper scraps, no dense network or landscape.
Text (verbatim): "失败原因" beside the paper scraps; "研究记忆" beside the stitched roots; "新假设" beside the fresh leaves. Sparse handwritten black/blue/red Chinese, only these three labels.
```

