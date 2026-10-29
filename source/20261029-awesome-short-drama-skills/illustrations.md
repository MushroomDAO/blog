# Awesome Short Drama Skills — 正文插图交付记录

日期：2026-10-29

文章：`src/content/blog/awesome-short-drama-skills-guide.md`

使用 `mycelium-mushroom-illustrations` skill 与内置 `image_gen.imagegen`，逐张独立生成，共三张必选插图。原始生成文件仅保留在现有 `/Users/jason/.codex/generated_images/` 下；仓库中只写入三张最终 PNG 与本记录。未执行文章或封面编辑、部署或提交。

## 成品规格与校验

- 三张均为 1120×630、16:9、不透明索引 PNG；均小于 90,000 字节，未使用 960×540 回退。
- Pillow Lanczos 缩放，Median Cut 48 色量化，禁用抖动；将相同 RGB 对应的实际像素索引合并并压实调色板，因此使用颜色少于 48 色。
- 清除近白底噪：RGB 最小通道 ≥218 且通道差 ≤40 的浅色归一为纯白；红帽相近红色合并为单一平涂色。PNG optimize=True、compress_level=9。
- 已逐张检查最终文件：纯白背景、大量留白、红帽白点小M参与核心动作；每张不超过三处简短中文标注，无标题、水印、PPT、网格或纹理背景。最终 PNG 四角均为 RGB(255,255,255)。
- SHA-256 来自下表中的实际最终文件；原图 SHA-256 分别记录在每张说明中。

| 图 | 最终路径 | 尺寸 | 字节 | 合并后使用颜色 |
|---|---|---|---:|---:|
| fig-01 | [src/assets/images/awesome-short-drama-skills-guide-fig-01.png](../../src/assets/images/awesome-short-drama-skills-guide-fig-01.png) | 1120×630 | 25103 | 34 |
| fig-02 | [src/assets/images/awesome-short-drama-skills-guide-fig-02.png](../../src/assets/images/awesome-short-drama-skills-guide-fig-02.png) | 1120×630 | 20330 | 27 |
| fig-03 | [src/assets/images/awesome-short-drama-skills-guide-fig-03.png](../../src/assets/images/awesome-short-drama-skills-guide-fig-03.png) | 1120×630 | 21952 | 37 |

## fig-01

- 用途／建议位置：按创作阶段选择候选工具的说明后，安装命令说明前。
- 画面检查：一个小工具箱和正在取出剧本的小M；三个阶段标注，无大型信息图。
- 实际中文标注：改编／剧本／分镜。
- 中文图注：小M按改编、剧本与分镜阶段，从工具箱里选择当前需要的工具。示意图。
- English caption: XiaoM selects a tool for the current adaptation, scripting or storyboard stage; conceptual illustration.
- 最终路径：`src/assets/images/awesome-short-drama-skills-guide-fig-01.png`
- 最终 SHA-256：`70409848e026e3ef147bd23e75c1edcbef70db224cf9bc61fee4999136866ee2`
- 原图路径：`/Users/jason/.codex/generated_images/01a18753-bc97-7662-ac9b-3210d77c7a86/exec-299ecd30-d523-401b-a222-77d06ed9ee89.png`
- 原图 SHA-256：`ada1ef3efd4856571b0b8b69569ebc50f805de7302ada791ad1134a1039b3f32`

### 完整生成提示词

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article illustration, not a composite of several images.
A sparse pure-white hand-drawn XiaoM scene about choosing a short-drama toolbox for the current production stage.
Visual DNA: exact solid white (#FFFFFF) background, fine slightly wobbly BLACK ink outlines, flat limited colors, plenty of blank space (at least 50%). No paper texture, noise, shadows, gradients, hatching, PPT layout, grid, bordered panels, infographic title, commercial illustration, cute mascot styling, or photorealism.
XiaoM is one deadpan serious little mushroom worker: rounded RED cap with 3–5 WHITE spots, pale cream stem body, BLACK dot eyes, thin black arms and legs, black hand-drawn outlines. Not a solid black mushroom. XiaoM MUST perform the central action.
Scene: one small open, portable, slightly wonky toolbox with just THREE simple tool objects: a folded story sheet, a script booklet, and a single storyboard sketch card. XiaoM leans into the toolbox and actively lifts the script booklet with both thin hands, selecting the tool needed now. The story sheet and storyboard card remain visibly separated within the same toolbox. Keep it a low-tech physical scene, not a table of capabilities or a huge diagram. Make the main compact scene occupy about half the canvas with generous white margins. A few loose strokes suffice to suggest pages; no fake writing.
ONLY these three short handwritten Chinese labels near their corresponding objects, in restrained blue/orange ink: "改编", "剧本", "分镜". Exactly these labels and no other text, no letters, numbers, logo, watermark, rankings, chart, stars, badges, or claims. The toolbox should be small and practical, no giant overview poster.
```

## fig-02

- 用途／建议位置：公开盲评的适用范围与限制说明后。
- 画面检查：两份档案具有相同形状序列；远处两把小空椅与核查动作分隔，无排名、分数、数字或观众认可暗示。
- 实际中文标注：核对档案／观众待验。
- 中文图注：小M用放大镜核对评测档案的一致性；隔开的空观众席表示真实观众效果仍待验证。示意图。
- English caption: XiaoM checks evaluation-file consistency; the separate empty chairs indicate that audience response remains unverified.
- 最终路径：`src/assets/images/awesome-short-drama-skills-guide-fig-02.png`
- 最终 SHA-256：`12a0336cdd7795f899402cde1038b40ae502c26cea51709cb1d4e489abb4b016`
- 原图路径：`/Users/jason/.codex/generated_images/01a18753-bc97-7662-ac9b-3210d77c7a86/exec-8fc1c3d2-56f4-4e91-8cee-3965f18bd2d6.png`
- 原图 SHA-256：`53a2c835d110dd6d113a86b93e5ec89b7e7bb2d88bb7e33faedaab4b4a0bb9ea`

### 完整生成提示词

```text
Use case: illustration-story. Generate ONE separate standalone 16:9 horizontal Chinese article illustration.
Concept: XiaoM uses a magnifying glass to verify consistency of evaluation files; audience reception is a separate unanswered matter.
Draw a sparse physical scene on EXACT SOLID PURE WHITE #FFFFFF. Thin, deliberately uneven BLACK hand-drawn ink outlines, flat solid spot colors, no texture anywhere, no paper grain, no colored background, no shadows or gradients. Lots of untouched empty white space, at least 55 percent. NOT a PPT, infographic, grid, dashboard or cute children's poster.
XiaoM is a serious deadpan mushroom worker with a RED dome cap bearing 3–5 WHITE polka dots, pale cream stem body, two BLACK dot eyes, and thin black arms and legs, simple black hand-drawn outlines. No rosy cheeks or sparkling eyes.
Main compact scene left of center: XiaoM crouches and holds a large simple magnifying glass directly over TWO partially overlapping evaluation archive sheets. Each sheet contains the SAME small sequence of three geometric marks, with the magnifying glass making a matching pair visible. Marks are shapes, not numbers or text. The sheets are ordinary hand-drawn paper files with minimal lines, no tables or pseudo-writing. XiaoM is actively inspecting the documents, the key action.
Far to the right, MUCH SMALLER and isolated by a broad clear white gap, draw just TWO tiny EMPTY audience chairs. No people, stage, screen, connecting arrows, check marks, approval or applause. They quietly suggest that actual audience response remains separate from internal file consistency. Do not make the chairs a second large scene.
ONLY two short Chinese handwritten labels: "核对档案" near the files in restrained blue, and "观众待验" above the tiny chairs in restrained blue. No other writing of any kind.
NO rankings, numeric claims, percentages, scores, medals, stars, charts, awards, thumbs up, ticks, badges, title or watermark. Keep the small red cap the principal colored area; most objects white with black outlines. Sparse hand-drawn conceptual sketch, never a dense explainer.
```

## fig-03

- 用途／建议位置：统一人物设定与跨工具交接约定说明后。
- 画面检查：三个行走姿态表示同一小M的连续时刻；蓝围巾人物与蓝色卡角保持一致，无网格或分栏。
- 实际中文标注：剧本／分镜／视频。
- 中文图注：小M把同一张人物参考卡带过剧本、分镜和视频环节，保持角色设定连续。示意图。
- English caption: XiaoM carries the same character-reference card through script, storyboard and video handoffs.
- 最终路径：`src/assets/images/awesome-short-drama-skills-guide-fig-03.png`
- 最终 SHA-256：`2a65bf952b968346b057b2e2fd9c17f647607b1b2c78091149d3eaae4fa36c63`
- 原图路径：`/Users/jason/.codex/generated_images/01a18753-bc97-7662-ac9b-3210d77c7a86/exec-921df2d7-7d01-465c-937b-d8474309cf16.png`
- 原图 SHA-256：`951cd5ebec8f69e7e6820ac9f68a41f95fe6648005a1da743ceb1c2f8f9258ed`

### 完整生成提示词

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article illustration.
Core metaphor: XiaoM physically carries the SAME character-reference card through SCRIPT to STORYBOARD to VIDEO. Consistent handoff preserves a character identity rather than reinventing it.
Visual DNA: EXACT SOLID PURE WHITE #FFFFFF background; sparse slightly wobbly fine black hand-drawn ink; only flat colors; no texture, paper grain, shading, shadows, gradients, polished vector art, commercial poster or childish cuteness. At least half the canvas must remain completely empty white. No grid, panels, PPT or dense infographic.
Show three SMALL successive walking poses of THE SAME XiaoM worker along one gently curving, understated orange travel stroke across the middle of the canvas, like a single continuous hand-drawn scene of motion, not a flowchart. Slightly irregular spacing and heights, no boxes around scenes, no header. Each pose has an identical RED mushroom cap with WHITE spots, pale cream stem body, BLACK dot eyes, blank serious face, thin black arms and legs. XiaoM actively hugs and carries the SAME small upright reference card in every walking pose. The card must have EXACTLY the SAME simple human bust drawing with a BLUE scarf and one BLUE corner tab each time; no words on the card. Its identity and appearance never change.
Beside the first walking pose, a small plain script sheet with just a few black lines; beside the second a small storyboard strip with just two tiny sketches of that SAME blue-scarf human; beside the third a simple miniature video frame on a stand showing that SAME blue-scarf human. All secondary objects are small black outline drawings. The reference card remains visibly held by the worker throughout; no transformations or alternate character designs. The three carried cards represent the SAME card at successive moments, not three different references.
Exactly THREE short Chinese handwritten labels near the corresponding small objects: "剧本", "分镜", "视频", in restrained blue ink. NO other text, letters, numbers, check marks, ranks, scores, badges, logos, title or watermark. Do not label the reference card. Keep each moment minimal, airy, clear and deadpan, no unnecessary props.
```
