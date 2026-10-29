# Hermit 小M正文配图

日期：2026-10-29。使用 `mycelium-mushroom-illustrations` 和内置 `image_gen`，每张单独生成，共 3 张；原图原地保留，未复制进仓库。

全部采用 16:9 白底、稀疏黑色手绘线稿、红帽白点小M参与核心动作；无标题、无网格或密集纹理，每张仅 3 处短中文标注。3 张均为正文必选图，分别对应文章已有的 3 个图片引用。

| 图 | 用途 | 中文标注 | 最终尺寸 | 大小（bytes） | 实际颜色数 |
|---|---|---|---|---:|---:|
| 01 | 固定模型与运行框架；小M只更换盒外的适配器板。 | 模型 / 运行框架 / 外部适配器 | 1120×630 | 17022 | 47 |
| 02 | 任务反馈指导修改；文件结构检查与独立性能评测各用一张卡，结构通过不代表性能提升。 | 任务反馈 / 文件检查 / 独立评测 | 1120×630 | 17347 | 48 |
| 03 | 训练、验证、测试材料保持独立；小M用天平比较成绩与调用成本。星形纸片代表成绩，电话与硬币代表调用成本。 | 训练 / 验证 / 测试 | 1120×630 | 16763 | 47 |

## 图 01

用途：固定模型与运行框架；小M只更换盒外的适配器板。

- 原图：`/Users/jason/.codex/generated_images/01a186cd-8cd1-7920-8dd4-1626f199a84d/exec-9b4dca4c-5b59-42a3-8045-474b53ea8065.png`
- 成品：`src/assets/images/hermit-harness-adapter-evolution-fig-01.png`

## 图 02

用途：任务反馈指导修改；文件结构检查与独立性能评测各用一张卡，结构通过不代表性能提升。

- 原图：`/Users/jason/.codex/generated_images/01a186cd-8cd1-7920-8dd4-1626f199a84d/exec-1f1ac095-a3d5-4de5-a7bb-ffa4b304bad9.png`
- 成品：`src/assets/images/hermit-harness-adapter-evolution-fig-02.png`

## 图 03

用途：训练、验证、测试材料保持独立；小M用天平比较成绩与调用成本。星形纸片代表成绩，电话与硬币代表调用成本。

- 原图：`/Users/jason/.codex/generated_images/01a186cd-8cd1-7920-8dd4-1626f199a84d/exec-f5bc0689-9c4f-477d-9ca1-1fed8b063ed2.png`
- 成品：`src/assets/images/hermit-harness-adapter-evolution-fig-03.png`

## 后处理与检查

使用 ImageMagick `magick` 缩放至 1120×630、关闭透明通道、关闭抖动、量化到最多 48 色，并去除元数据。第一次直接量化的图 01 仍有近白背景噪声，缩至 960×540 后为 141368 bytes；统一将 5% 容差内的近白背景清为纯白后，3 张均在 1120×630 达标，无需保留缩小版。

可复现命令（`ORIGINAL`、`FINAL` 替换为上方对应路径）：

```bash
magick "$ORIGINAL" -background white -alpha remove -alpha off \
  -resize '1120x630!' -fuzz 5% -fill white -opaque white \
  +dither -colors 48 -strip "PNG8:$FINAL"
```

检查原图与成品的主题、角色动作、文字和留白；检查成品像素尺寸、16:9 比例、实际颜色数与文件大小，全部小于 90000 bytes。原图处理前后 SHA-256 一致。文章未修改，未生成 banner、部署或提交。

## 实际生成提示词

以下为内置 `image_gen` 每张单独调用的完整提示词，`transparent_background=false`；没有使用 CLI 或本地模型代替图像生成。

<details>
<summary>图 01 提示词</summary>

```text
Generate exactly ONE standalone 16:9 horizontal Chinese article BODY illustration, preferably 1536x864. Use case: illustration-story.
Pure white #FFFFFF opaque background. Extremely sparse thin black hand-drawn slightly wobbly pen outlines, flat tiny color accents, vast white space. No textures, shading, gradients, hatch marks, grids, mesh fences, dense patterns, UI, PPT or diagram poster. No title or captions.
Character: XiaoM, one small serious deadpan mushroom acting as the mechanic: rounded flat RED cap with 3–5 WHITE round spots, cream stem body, two tiny BLACK dot eyes, thin stick arms and legs, black hand outline. Not solid black, not cute, no smile, no clothing.
Core scene: model and original runtime remain fixed; ONLY an external adapter plate is swapped. Draw one plain closed simple rectangular machine box left of center, containing two very simple outlined blocks stacked inside an unobtrusive cutaway, with short blue handwritten labels "模型" and "运行框架". These blocks stay clearly untouched. Outside the box on its right side, XiaoM uses both hands to slide a small thin orange-edged removable plate into a single external slot. Show a second old blank plate lying beside his foot so replacement is evident. The active plate sits wholly OUTSIDE the machine enclosure; do not depict a new model inserted. One tiny orange movement arrow beside plate if needed.
Exact text: only "模型", "运行框架", "外部适配器" (the latter handwritten near the active plate). Exactly three short Chinese labels total. No other writing, numerals or English.
Composition: single coherent little hand sketch centered in the middle horizontal band, total content about 50–55% width and 40% height, generous empty margins on all sides. Sparse clean whimsical conceptual working scene, not formal architecture. Thin black outlines, red cap identity color, one orange plate edge, blue labels. No decorations, no cables, no mesh, no texture.
```

</details>

<details>
<summary>图 02 提示词</summary>

```text
Generate exactly ONE standalone 16:9 horizontal Chinese article BODY illustration, preferably 1536x864. Use case: illustration-story.
Pure opaque white #FFFFFF background. Extremely sparse thin black hand-drawn slightly wobbly pen outlines, minimal flat accents, at least 60% white empty space. No textures, shadows, shading, gradients, mesh fences, grids, hatch lines, dense patterns, UI, PPT, commercial vector polish or title.
XiaoM is the active central worker: rounded flat RED mushroom cap with 3–5 WHITE circular spots, cream stem body, two tiny BLACK dot eyes, thin arms and legs, deadpan serious. No smile, clothes, sparkly eyes or solid black mushroom.
Core idea: task feedback teaches an adapter edit, while structural validity and performance evaluation are separate checks. Single loose tabletop sketch without drawing a table: XiaoM sits slightly left of center, one hand holding a small blue-edged feedback slip, the other hand using a pencil to change a plain adapter sheet. A tiny curved orange arrow runs from the feedback slip toward the writing hand. Beside the edited sheet, to its right, are two distinct upright cards separated by a wide gap, never connected by an equals sign or success arrow. First card shows only a simple folded-corner file and one small black check mark: structural file validity. Second card shows a plain little test tube icon and a minimal analog gauge needle with no tick marks: independent evaluation, no promise of improvement. Keep objects tiny and simple. XiaoM's physical writing action is the story.
Exact text: only THREE short handwritten Chinese annotations: "任务反馈" on feedback slip, "文件检查" on first check card, "独立评测" on second evaluation card. NO fourth label, no title, no English, no numbers, no invented data, no pseudo-code.
Content group occupies about 60% of width and 40% of height in center with ample margins. Let the two cards visibly differ, separate paper objects rather than two gates in a fence. No fences, grids, architecture boxes, scenery, decorative lines or complex loop diagram. Black linework, red mushroom cap, very little blue for feedback and orange for one arrow. Clean absurd product notebook sketch, grown-up and restrained.
```

</details>

<details>
<summary>图 03 提示词</summary>

```text
Generate exactly ONE standalone 16:9 horizontal Chinese article BODY illustration, preferably 1536x864. Use case: illustration-story.
Pure opaque WHITE #FFFFFF background. Extremely sparse thin black hand-drawn slightly wobbly outlines; tiny flat color accents, huge quiet empty margins. No texture, paper grain, shading, shadows, gradients, hatching, grids, mesh fences, dense patterns, formal diagram, PPT, title or banner.
XiaoM is one deadpan working mushroom: flat RED dome cap with 3–5 WHITE circular spots, pale cream stem body, two tiny BLACK dot eyes, thin black stick arms and legs, black outline. No smile, clothes or childish cute expression. XiaoM actively keeps the task datasets separate and compares quality with cost.
Single coherent scene in a central horizontal band. On left and middle, three small shallow paper trays, each detached by a clear white gap, each containing only one or two blank cards. XiaoM is between the trays and the right side, physically placing one blank card into the leftmost tray with one hand; another thin arm points toward a simple compact BALANCE SCALE on the right. The trays never share cards, no interconnecting arrows and no leaked test answers. On the balance scale's left pan is one tiny paper bearing a black STAR outline (score); on its right pan are just two small orange coins beside a tiny phone-receiver outline (call cost). Scale shows comparison only, not a claimed winner. Keep scale as a simple thin line object, not detailed machinery.
Exactly THREE short handwritten Chinese labels total, one on each tray: "训练", "验证", "测试". These are the ONLY written words. Score and call cost use the star and phone+coin icons only, no extra labels, no English, no numbers or chart values. No title anywhere.
Subjects occupy about 60% of canvas width and 40% height, leaving huge white space especially top and bottom. Sparse low-tech product notebook sketch, no desktop background, no elaborate borders, no mesh separators. Red cap identity color; tiny orange coins; black outlines. XiaoM's sorting and pointing action carries the meaning; no idle spectator.
```

</details>


Primary-agent review: all three final PNGs inspected and accepted before build. The article hash changed during generation because the primary agent shortened frontmatter description and clarified the expected zero-score probe; the illustration anchors and meaning did not change. The worker did not edit the article. Final article/assets hashes are in build-input-hashes.json.
