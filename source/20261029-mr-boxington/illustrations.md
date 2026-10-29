# mr boxington 正文配图记录

- 日期：2026-10-29
- 文章：`src/content/blog/mr-boxington-rust-cargo-shared-cache.md`
- 使用 skill：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`
- 生成方式：内置 `image_gen`，三个独立调用，每次仅生成一张，共三张。
- 原图保留在 `/Users/jason/.codex/generated_images/01a186ed-7173-7e70-980f-600b09bd2bea/`，未移动、覆盖，也未复制原图到仓库；仓库仅保存处理后的最终 PNG。
- 未修改文章，未生成 banner，未部署或提交。

## 用途与最终文件

| 图 | 用途 | 最终文件（相对仓库根目录） | 尺寸 | 字节 |
| --- | --- | --- | --- | ---: |
| 01 | 两个工作区由小M从同一个共享箱取用匹配的完整构建部件，对应跨路径复用编译产物。 | `src/assets/images/mr-boxington-rust-cargo-shared-cache-fig-01.png` | 1120×630 | 28242 |
| 02 | 小M把共享成品箱与甲、乙工作区各自的私有增量抽屉分开管理；完整共享产物与私有增量状态是不同机制。 | `src/assets/images/mr-boxington-rust-cargo-shared-cache-fig-02.png` | 1120×630 | 24000 |
| 03 | 三个小M各用独立输出托盘，在一个共同资源预算计数器下构建；各托盘保留闭合锁，明确共享缓存不会消除 Cargo 目录锁。 | `src/assets/images/mr-boxington-rust-cargo-shared-cache-fig-03.png` | 1120×630 | 28829 |

三张均作为最终交付使用，无可选或弃用图。每张恰好三个短中文标注，无标题。均为 16:9、不透明白底，红盖白点小M参与核心动作，未使用网格或围栏。

## 原图来源

原图均为 1672×941；生成工具的原始比例略偏离 16:9，导出时等比缩放并以白色居中补齐至精确 1120×630。

| 图 | 原始文件名（以上 generated_images 目录内） | 原图字节 | SHA-256 |
| --- | --- | ---: | --- |
| 01 | `exec-f0c7ac24-914f-4f1c-a1d6-590c2b6c2410.png` | 1137803 | `0ffd3285abdbc69e41ff40fa26f22eacec5caaa94276150bc40d30ed0c7f0677` |
| 02 | `exec-733be2f0-3406-4de5-b706-6bcb6c7a6d74.png` | 960762 | `b244cb842da57971e996a8c0fe496bddf53fc02365d03bf1ba5f65a4216d4e95` |
| 03 | `exec-95002c59-e58f-47a0-8165-4d8f3b473bda.png` | 1126433 | `24dfb93c8b8356b548ad67ffe18ad6519fb79dce307bf94cafd41a5c5866d072` |

## 导出与核验

使用 ImageMagick `magick`。先去除细微生成噪点并将近白底色归白，再缩放、关闭抖动并按 48 色上限量化，保存索引 PNG。最终三张实际均为 47 色、1120×630，且各自小于 90000 字节，左上角像素为纯白。

```bash
magick "$original" \
  -background white -alpha remove -alpha off \
  -statistic Median 3x3 -white-threshold 95% \
  -resize 1120x630 -gravity center -extent 1120x630 \
  +dither -colors 48 -type Palette -strip \
  -define png:compression-level=9 "PNG8:$final"
```

处理记录：第一张最初仅缩放、量化，在规定的 960×540 回退尺寸下仍为 125844 字节。原因是生成图中的细微底色噪点；随后统一采用上述清理步骤完成导出，未继续试探压缩参数。清理后三张均可保留 1120×630，无需最终尺寸回退。

已逐张查看最终 PNG，确认小M动作、中文标签与三个用途对应，第三张保留三处目录锁。原图 SHA-256 在处理前后保持一致。文章初次读取的 SHA-256 为 `7d12e00ec357dca6b4d1282227d284d72ed8da2bf7a4edc05778bee35092a4a2`；收尾读取时为 `c689d82c97f22b34ff3171f564a350ebbbdfe72ab841183330f9fe4ba4f164c8`。本任务所有写入仅涉及三张最终 PNG 和本记录，未写入文章；观察到的并发文章变更未回滚。

## 原始生成提示词

以下为三个内置生成调用的完整提示词；每次均设置 `transparent_background: false`，无参考图输入。

### 图 01

```text
Generate exactly ONE standalone 16:9 horizontal Chinese blog body illustration, a single scene, not a collage.
Pure solid white #FFFFFF background. Extremely simple thin black hand-drawn slightly wobbly pen outlines, flat limited colors, no textures, no grid, no fence, no hatching, no shading, no shadows, no gradients, no paper grain. Large blank white margins, at least 45% blank. Scene uses only a few everyday objects, no elaborate machinery or UI. No title, heading, watermark, border, legend or extra writing. No PPT/flowchart/commercial vector style, not a childish cute cartoon.
XiaoM characters: small serious deadpan mushrooms actively doing the conceptual work, each with a rounded flat RED cap, 3–5 WHITE polka dots, cream-white stem body, BLACK dot eyes, very thin black arms and legs, black hand-drawn outline. Never solid-black mushroom bodies. Sparse orange or blue accents only where needed. Exactly the specified short Chinese labels, legible, no extra text or English. Keep annotations small.
Scene 1: Two independent workspaces collect MATCHING completed build parts from ONE shared open box. Put one simple open box in the center holding two recognizable reusable parts: a ring-shaped part and a three-notch block. One XiaoM on each side is actively reaching into that SAME central box with one hand, while carrying a matching ring/block toward its own small workbench with the other hand. Left and right workbenches are plainly separate and each has the same ring/block outline awaiting the matching part. Copy/reuse is the idea, not literal consumption or moving source code. Minimal objects; no laptops, screens, walls or scenery. The two XiaoM must visibly handle parts rather than merely stand nearby.
Only three Chinese labels: “工作区甲” at left workbench, “共享产物” small on central box, “工作区乙” at right workbench. No other writing. Preserve lots of white space above and below.
```

### 图 02

```text
Generate exactly ONE standalone 16:9 horizontal Chinese blog body illustration, a single scene, not a collage.
Pure solid white #FFFFFF background. Extremely simple thin black hand-drawn slightly wobbly pen outlines, flat limited colors, no textures, no grid, no fence, no hatching, no shading, no shadows, no gradients, no paper grain. Large blank white margins, at least 45% blank. Scene uses only a few everyday objects, no elaborate machinery or UI. No title, heading, watermark, border, legend or extra writing. No PPT/flowchart/commercial vector style, not a childish cute cartoon.
XiaoM characters: small serious deadpan mushrooms actively doing the conceptual work, each with a rounded flat RED cap, 3–5 WHITE polka dots, cream-white stem body, BLACK dot eyes, very thin black arms and legs, black hand-drawn outline. Never solid-black mushroom bodies. Sparse orange or blue accents only where needed. Exactly the specified short Chinese labels, legible, no extra text or English. Keep annotations small.
Scene 2: One XiaoM is physically sorting two different kinds of build state and keeping them separate. A shared open finished-artifacts box sits at left, containing only two complete, intact gear-like parts. At right are TWO small separate private drawer units, each with just one partly-open drawer containing unfinished small segments/pieces. The drawers belong to different workspaces and remain visibly separate. XiaoM stands between box and drawers, one hand depositing a complete part into the shared box, the other hand sliding an unfinished piece into one private drawer. The active sorting gesture is the whole point: only completed matching artifacts are shared, private incremental states are kept per workspace. No transfers between drawers, no merging of unfinished pieces. Keep box/drawer surfaces WHITE with thin black outlines, no brown wood/cardboard shading, no grain or texture, no heavy fills. Three objects plus one mushroom, compact loose composition with abundant whitespace.
Only three labels, written small on the respective objects: “共享成品”, “甲私有增量”, “乙私有增量”. No other text or title.
```

### 图 03

```text
Generate exactly ONE standalone 16:9 horizontal Chinese blog body illustration, a single scene, not a collage.
Pure solid white #FFFFFF background. Extremely simple thin black hand-drawn slightly wobbly pen outlines, flat limited colors, no textures, no grid, no fence, no hatching, no shading, no shadows, no gradients, no paper grain. Large blank white margins, at least 45% blank. Scene uses only a few everyday objects, no elaborate machinery or UI. No title, heading, watermark, border, legend or extra writing. No PPT/flowchart/commercial vector style, not a childish cute cartoon.
XiaoM characters: small serious deadpan mushrooms actively doing the conceptual work, each with a rounded flat RED cap, 3–5 WHITE polka dots, cream-white stem body, BLACK dot eyes, very thin black arms and legs, black hand-drawn outline. Never solid-black mushroom bodies. Sparse orange or blue accents only where needed. Exactly the specified short Chinese labels, legible, no extra text or English. Keep annotations small.
Scene 3: THREE XiaoM mushroom builders are actively assembling simple build parts, EACH at its OWN clearly SEPARATE shallow output tray, with wide white gaps between trays. Above them is ONE small common resource-budget counter: a simple hand-drawn horizontal counter box with three small token circles, two orange and one unfilled, no numerals or UI detail. It represents a shared finite compilation budget across all three builders. One builder's raised hand is returning a resource token upward toward this one counter while its other hand places a build part into its own tray. The other two are also visibly putting parts in their own individual trays. All trays and counter are white outlined in black; minimal objects and abundant blank white space.
Technical truth is essential: parallel Cargo builds need separate appropriate output directories; shared cache DOES NOT remove Cargo directory locks. Show a tiny intact CLOSED padlock attached to the side lip of EACH separate tray, serving as the tray's directory lock. These locks remain present, not broken, crossed out, opened, or disappearing; they do not block putting objects in the open tops of the trays. No common target tray, no shared output directory, no arrows that merge trays. No cache box needed in this image. No fences or grids, no enclosing boundary.
Exactly THREE short Chinese labels total: “资源预算” small on the counter, “独立输出” centered below the three spaced trays, “目录锁仍在” small next to one intact padlock. No other writing. Do not add individual labels or a title.
```


Primary-agent QA: final PNGs inspected before build, white background, topic-matched, readable short labels, all below90KB. Article metadata, pinned installation command and debug-path explanation were refined during image generation; anchors did not change. The worker did not edit the article. Final build-input hashes are recorded separately.
