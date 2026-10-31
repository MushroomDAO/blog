# Huashu bird sticker guide — illustrations

Completed: 2026-10-31. Exactly three final illustrations for `src/content/blog/huashu-bird-sticker-guide.md`.

## Provenance and scope

- Generated independently in three built-in `image_gen.imagegen` calls using the `mycelium-mushroom-illustrations` skill and built-in `imagegen` workflow. The tool does not expose a precise underlying model/version identifier.
- Input: article text and the user's three specified concepts. No reference image, upstream bird sticker, field-guide drawing, banner or screenshot was supplied to image generation. Birds are deliberately generic conceptual sketches, with no diagnostic identification claim.
- Raw generated originals remain only in their existing `/Users/jason/.codex/generated_images/` location. No raw original was copied into the repository, modified or deleted.
- Only the three final image files and this report were created by this task. Article, banner and parent-owned source assets were not edited. Banner contents were not inspected or hashed. No deployment or commit.

## Final assets

All files are PNG, opaque indexed color (mode P), exactly 1120 × 630 (16:9), and below 90,000 bytes. The 960 × 540 fallback was unnecessary.

| Figure | Final path | Bytes | Quantization target | Used colors after index merge | Pure white pixels |
|---|---|---:|---:|---:|---:|
| 01 | `src/assets/images/huashu-bird-sticker-guide-fig-01.png` | 15141 | 48 | 18 | 96.04% |
| 02 | `src/assets/images/huashu-bird-sticker-guide-fig-02.png` | 24119 | 48 | 18 | 93.12% |
| 03 | `src/assets/images/huashu-bird-sticker-guide-fig-03.png` | 21981 | 48 | 17 | 93.97% |

Processing: Pillow 12.3.0; RGB conversion, LANCZOS resize, median-cut quantization to 48 colors with dithering disabled. Palette entries whose minimum RGB channel is at least 240 and channel spread is at most 12 are normalized to #FFFFFF; equivalent entries are merged by remapping pixel indices to a canonical palette index. This actually merges indices rather than merely duplicating white RGB entries in the palette. Metadata is cleared in final exports; PNG optimization and compression level 9 are used. Raw originals retain their original bytes and metadata.

Final-image checks completed before writing this report: all three finished PNGs were opened and visually inspected at their delivered size; labels are readable and within the limit; XiaoM performs the relevant action with red cap, white spots and pale stem; backgrounds and all outer-border pixels are pure white. No grid, slide framing, title, textured background or diagnostic bird detail. Figure 02 leaves the separate guide pending; figure 03 keeps all three sheets distinct without blanket permission symbols. No subsequent image changes are part of this handoff.

## Figure 01

Chinese caption: 小M把一张鸟类图卡与同一物种的数据记录连接起来，概念示意。

English caption: XiaoM connects one bird image card to its matching species record; conceptual illustration.

Visible Chinese labels (2): `图卡` / `物种记录`.

Raw original: `/Users/jason/.codex/generated_images/01a19071-37a7-7032-822b-61ef71549bab/exec-c4f077e0-5ac0-492d-b0dc-3a2596ba3378.png`
Raw dimensions: 1672 × 941; 946257 bytes.
Raw SHA-256: `933cb30f036c8d53261521ffb36f931a977e8281a2e9264ab3ae6a29ad6cfaf2`
Final SHA-256: `4395d1abc8557658177020f2cc27715b728990aeb9cf116c3c19b08a8fd9d436`
Merged palette indices: 1→0, 2→0, 3→0, 4→0, 5→0, 6→0, 7→0, 8→0, 9→0, 10→0, 11→0, 12→0, 13→0, 14→0, 15→0, 16→0, 17→0, 18→0, 19→0, 20→0, 21→0, 22→0, 23→0, 24→0, 25→0, 27→0, 28→0, 29→0, 33→0, 34→0.

Generation prompt (verbatim; built-in generation, no CLI fallback):

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article illustration, never a collage. Figure 01: one bird image linked to its matching species-data card.
Pure #FFFFFF background, sparse thin black hand-drawn pen outlines with a slight wobble, generous negative space (at least 55%). Flat tiny areas of red/orange/blue, no texture, no shading, no shadows, no gradients. Quiet absurd editorial sketch rather than PPT, grid, infographic, formal flowchart, vector art or cute children's poster. No title.
XiaoM is the core actor: small serious deadpan mushroom with a rounded flat RED cap, 3–5 WHITE spots, cream stem body with black outline and two BLACK dot eyes, thin arms and legs, no smile. Centered within the middle half of the wide canvas, XiaoM is physically fastening a single orange connecting thread between TWO loose hand-drawn paper cards. Left: exactly one card with one very simple generic bird outline (round body, tiny beak, stick legs; absolutely no species-specific diagnostic plumage). Right: matching species-data card with the same small bird symbol and just three short nonverbal horizontal strokes representing data. XiaoM holds and fastens the thread to the data card, so its action explains the link. Cards are casual, slightly tilted, not a rigid UI.
Only these TWO short handwritten Chinese labels, once each: “图卡” next to left card, “物种记录” next to right card. No other text, numbers, symbols pretending to be words, species names or captions. Bird is an invented conceptual sketch, not a field-guide drawing. Keep all objects comfortably within the central 65% of the frame, broad pure white margins.
```

## Figure 02

Chinese caption: 小M检查完整图片目录，另一侧的图鉴仍需核对；目录完整性不能证明识别准确性。

English caption: XiaoM checks a complete image catalogue while a separate field guide still awaits checking; completeness does not establish identification accuracy.

Visible Chinese labels (3): `目录齐全` / `图鉴` / `仍需核对`.

Raw original: `/Users/jason/.codex/generated_images/01a19071-37a7-7032-822b-61ef71549bab/exec-7794dd8d-f074-4dee-aaf5-4aabbf6cfd4d.png`
Raw dimensions: 1672 × 941; 1150143 bytes.
Raw SHA-256: `5d1aedc65e32a101a97aed51a2b5ea83bea2ca3dead662901892dd4b85a98baf`
Final SHA-256: `96af024b6e389c715af7ea14664b95f9f30d8c617658d8b5246baf64ff7ace2e`
Merged palette indices: 1→0, 2→0, 3→0, 4→0, 5→0, 6→0, 7→0, 8→0, 9→0, 10→0, 11→0, 12→0, 13→0, 14→0, 15→0, 16→0, 17→0, 18→0, 19→0, 20→0, 21→0, 22→0, 23→0, 24→0, 25→0, 26→0, 27→0, 28→0, 29→0, 30→0.

Generation prompt (verbatim; built-in generation, no CLI fallback):

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article illustration, never a collage. Figure 02: a complete image catalogue is checked, but scientific accuracy still needs a separate field guide check.
Pure #FFFFFF background, very sparse thin black hand-drawn slightly wobbly pen lines; at least 55% empty white space. Restrained red, orange and blue accents with flat color. No paper texture, shading, shadows, gradients, PPT, formal diagram, panels, grid or glossy vector illustration. No heading.
Main actor XiaoM: rounded flat RED mushroom cap with 3–5 WHITE polka dots, pale cream stem with black outline, two BLACK dot eyes, thin arms and legs, serious deadpan, no cute smile. In one informal central scene XiaoM is actively marking the final entry on a complete image catalogue: a loose open folio containing three simple generic bird icons arranged in a single loose vertical list (not a tiled grid), each with a small checked box. Its pen touches the last check. This catalogue stands for inventory/path completeness only.
A separate closed pocket FIELD GUIDE sits to the right with a plain generic bird outline on its cover, clearly separate from the checklist. A small handwritten blue question mark floats above the book, and its status remains pending. No tick, certification seal or approval on the guide. These are two different checks; the completeness tick MUST NOT imply identification accuracy. All birds are deliberately simple conceptual doodles without diagnostic feather detail.
Exactly THREE short Chinese handwritten labels: “目录齐全” by the checked catalogue, “图鉴” on the separate book cover, “仍需核对” by that book. No additional text, percentages, scores, species names, arrows, explanatory sentences or title. Keep the scene sparse, spread naturally across the middle 60% with pure white margins.
```

## Figure 03

Chinese caption: 小M分别检查贴纸、整理数据和第三方来源三份许可，概念示意。

English caption: XiaoM examines three separate license sheets for stickers, compiled data and third-party sources; conceptual illustration.

Visible Chinese labels (3): `贴纸` / `整理数据` / `第三方来源`.

Raw original: `/Users/jason/.codex/generated_images/01a19071-37a7-7032-822b-61ef71549bab/exec-a3aceadd-a8d3-4e07-b9a8-e06231baf918.png`
Raw dimensions: 1672 × 941; 1107324 bytes.
Raw SHA-256: `6ddf55edfb39d5fd3eefc7e8618179ac019c8b9f7bdb7382c2289c573d72e595`
Final SHA-256: `c0b0e6625ec159210967a1a5753218a4c959e2af72cca3994b26b538e6f807dc`
Merged palette indices: 1→0, 2→0, 3→0, 4→0, 5→0, 6→0, 7→0, 8→0, 9→0, 10→0, 11→0, 12→0, 13→0, 14→0, 15→0, 16→0, 17→0, 18→0, 19→0, 20→0, 21→0, 22→0, 23→0, 24→0, 25→0, 26→0, 27→0, 28→0, 29→0, 30→0, 32→0.

Generation prompt (verbatim; built-in generation, no CLI fallback):

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article illustration, never a collage. Figure 03: XiaoM examines three separate license sheets covering stickers, compiled data and third-party sources.
Pure #FFFFFF background, sparse thin black hand-drawn slightly wobbly pen linework, generous empty white space at least 55%, flat red cap and tiny orange/blue accents only. No gradients, shadows, texture, PPT, grid, panels, infographic, formal flowchart or commercial vector style. No heading.
One XiaoM as central active examiner: rounded RED cap with 3–5 WHITE round spots, cream mushroom stem body outlined black, two small BLACK dot eyes, thin arms/legs and deadpan serious face. XiaoM holds a magnifying glass directly over the middle of THREE distinct loose paper license sheets, while its other hand lifts a corner to compare the sheets. All three sheets remain separately visible with white gaps, loosely staggered at different angles like an inspection on blank space, not a three-column slide and not stacked into a single license.
The first sheet has a tiny generic bird doodle and the sole label “贴纸”; the second has a few short data strokes and the sole label “整理数据”; the third has two tiny source-link rings and the sole label “第三方来源”. Each sheet has just 2–3 short nonverbal pen strokes beneath its label to imply terms, no fake legible paragraphs. Exactly these THREE Chinese handwritten labels and no other words. No license names, checkmarks, shields, blanket permission badge, copyright stamp or legal conclusions. Any bird doodle is generic conceptual, never a diagnostic field-guide drawing. Frame the little inspection scene in the middle 60%, lots of pure white margin.
```
