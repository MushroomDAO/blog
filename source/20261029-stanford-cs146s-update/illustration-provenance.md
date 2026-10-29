# CS146S article illustration provenance

- Date: 2026-10-29 (Asia/Bangkok).
- Requested skill: `/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`. Read the skill and its style DNA, mushroom IP, composition, prompt-template and QA references.
- Supporting workflow: `/Users/jason/.codex/skills/.system/imagegen/SKILL.md`.
- Article read: `src/content/blog/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course.md`, including all three existing Chinese and English figure anchors.
- Generation: built-in `image_gen.imagegen` (`tools.image_gen__imagegen`), three separate calls producing exactly three independent images. No reference images; `transparent_background: false`. No model identifier was exposed by the tool; none is inferred.
- Output: three opaque PNGs, exactly 1200×675 (16:9), each strictly below 90,000 bytes.
- Character/style: XiaoM actively performs the central action, red cap with white spots, cream stem, black dot eyes, hand-drawn black outlines, white background, restrained orange/blue accents. Figure 01 has no words; figures 02 and 03 have three short Chinese labels each.
- Originals: original tool files were left in place and byte-identical archival copies were saved under `illustration-originals/` alongside this record.
- This task performed no writes to article Markdown or banner, no publishing, and no source retrieval from the course website. The supplied article was the content reference.

## Final assets and original files

| Figure | Purpose | Final asset | Bytes |
|---|---|---|---:|
| 01 | Agent tool-result loop | `src/assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-fig-01.png` | 58922 |
| 02 | Trace unofficial bilingual notes to original official course sources | `src/assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-fig-02.png` | 69413 |
| 03 | Align synthetic data, specifications and acceptance tests | `src/assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-fig-03.png` | 47440 |

### Figure 01

- Tool original: `/Users/jason/.codex/generated_images/01a185a0-e5df-7982-ba23-6a4b0aa1d97e/exec-8b1313ef-fb13-4a3d-9ffe-1eeae804fc68.png`
- Archived original: `source/20261029-stanford-cs146s-update/illustration-originals/fig-01-original.png`
- Original SHA-256: `412c7790f6201c28e2985e19eef97a0277ef9109cf7ac44c711754d3f282b08a`
- Final SHA-256: `b774b59411eb466476f2565722e44883fd65c7f0352c4e0531ad16fe086527a5`

### Figure 02

- Tool original: `/Users/jason/.codex/generated_images/01a185a0-e5df-7982-ba23-6a4b0aa1d97e/exec-e8d88dd5-3259-4e1e-a3dd-c665c8ba6b43.png`
- Archived original: `source/20261029-stanford-cs146s-update/illustration-originals/fig-02-original.png`
- Original SHA-256: `d279a5b0b21c67f56fc65647155a3b139c45f0f56343ad3061156ea7d830d8bb`
- Final SHA-256: `f3d6b6cebe87cc81303f72440238c781789ece0ef5b511b9bbd67633ef87b144`

### Figure 03

- Tool original: `/Users/jason/.codex/generated_images/01a185a0-e5df-7982-ba23-6a4b0aa1d97e/exec-62d1d20e-a4d0-4839-9eea-1113e9d70ce5.png`
- Archived original: `source/20261029-stanford-cs146s-update/illustration-originals/fig-03-original.png`
- Original SHA-256: `c28c7358248f34f2d33650852b336c21f1b73d1ab25153686abd733b95451cc0`
- Final SHA-256: `fc0c42a4c57bbfe95d8f30b075d68f3d2fca9a3e37768877c77958b6995b2c32`


## Compression and verification

Postprocessing used ImageMagick only to flatten transparency, normalize dimensions, clean near-white pixels and compress a palette PNG; no compositional editing or new illustration generation was performed during compression. Preliminary encodings were superseded by the final command below. A luminance threshold trial was rejected because it lost the cream stem; the chosen near-white color replacement preserves it.

Reproduction command, run from repository root for each `n` in `01 02 03`:

```sh
magick "source/20261029-stanford-cs146s-update/illustration-originals/fig-${n}-original.png" \
  -background white -alpha remove -alpha off \
  -resize '1200x675!' \
  -fuzz '3%' -fill white -opaque white \
  -strip +dither -colors 96 -define png:compression-level=9 \
  "PNG8:src/assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-fig-${n}.png"
```

The compressed PNGs were copied into the requested asset paths before completion. Verified actual saved-file byte counts, PNG signatures and dimensions. Visually inspected all three generated compositions and compressed previews for the central action, short labels, margins, red/white cap identity, cream body and white background.

### Concurrent workspace changes

The article and banner were already modified in the initial `git status`. Their hashes also changed between this task's initial read and final verification, although none of this task's commands wrote either path. The responsible external writer is unknown. Current files were retained; no rollback or overwrite was attempted. Therefore this record asserts **no writes by this task**, rather than incorrectly claiming the workspace copies stayed byte-identical.

| Protected path | Initial SHA-256 | Observed at verification |
|---|---|---|
| `src/content/blog/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course.md` | `3e1dd6a62ab0d9efebfd8055ea45fd1cb62934035eca459585b717ba50b2b169` | `c386c63bdcca0026cebf645f032c50d8f7f8f8eb0fb35ac884346031ee1a8608` |
| `src/assets/images/stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course-banner.jpg` | `339044908b42af33b8f78bae72798c9c4d2a130b5022ad4d5976065e1b4537db` | `1c56f8df2d407ec1963855481556a81236217ba1f6b7a0a912d8ca0dc2fcd8ef` |

## Exact generation prompts

### Figure 01

```text
Generate exactly ONE standalone 16:9 horizontal illustration for a Chinese technical article, not a montage. Use case: illustration-story.
Pure white #FFFFFF background, thin slightly wobbly BLACK hand-drawn pen line art, flat sparse accent colors, lots of empty space, main scene occupies roughly 50% of canvas. Clean absurd editorial product sketch, restrained and deadpan. No text anywhere, no title, no lettering, no logo, no watermark. No paper texture, gradients, shadows, UI screenshots, PPT diagrams, boxed flowcharts, commercial vector art or cute children's cartoon.
Required active character XiaoM: a small mushroom worker with a RED rounded dome cap with 3–5 WHITE round spots, CREAM stem body, black hand-drawn outline and two BLACK dot eyes, tiny thin arms and legs, blank serious expression, not solid black, not smiling. This same identity is to be used in a series.
Theme: agent tool-result loop. Make a sparse physical scene of a tabletop hand-cranked return mechanism, an absurd little laboratory. On the left a floating simple outlined thought bubble containing a tiny branching-decision glyph releases a folded action slip. In the center-right XiaoM actively feeds that slip into a simple open mechanical tool press with a small wrench attached. The press produces a result sheet marked only with a small blue check and a couple of short abstract lines. XiaoM's other arm is visibly returning that result sheet toward the thought bubble along the lower arc of the scene. A single thin orange curved arrow follows the outgoing action across the top, a single blue curved arrow follows the returning result across the bottom, forming a clearly closed loop. The thought bubble represents model decision, the real press represents host tool execution, the returned sheet represents tool output feeding the next decision. Keep these as one hand-drawn working scene, not separate diagram nodes. XiaoM must be essential to operating and closing this loop. No invented labels or equations. Draw a simple spacious wide composition with generous clear margins.
```

### Figure 02

```text
Generate exactly ONE standalone 16:9 horizontal illustration for a Chinese technical article, not a montage. Use case: illustration-story.
Pure white #FFFFFF background, thin slightly wobbly BLACK hand-drawn pen line art, flat sparse accent colors, lots of empty space, main scene occupies roughly 50% of canvas. Clean absurd editorial product sketch, restrained and deadpan. No title, no watermark, no logos, no university crest. No paper texture, gradients, shadows, UI screenshots, PPT diagrams, boxed flowcharts, commercial vector art or cute children's cartoon.
Required active character XiaoM: a small mushroom worker with a RED rounded dome cap with 3–5 WHITE round spots, CREAM stem body, black hand-drawn outline and two BLACK dot eyes, tiny thin arms and legs, blank serious expression, not solid black, not smiling.
Theme: tracing unofficial bilingual learning notes through a source index back to original official course material. One sparse scene: XiaoM stands between two separate open books on a little implied white tabletop, actively using a long absurdly hinged page-pointer that bridges a reference marker in the left book to its matching marker on a loose original lecture sheet above the right book. The left book has two narrow parallel columns of loose hand-drawn abstract writing strokes suggesting bilingual paraphrase, with a tiny handwritten label '笔记'. A small index card between the books contains three matched dot pairs and only the handwritten label '索引'. The right book with a few original lecture sheets has a simple chalkboard-like geometric lecture sketch and the small label '原课'. Use just those three SHORT Chinese handwritten labels and no other readable text. Three matching blue page tabs make the correspondence visible. XiaoM is physically following and checking the source match, one hand holds a page open and the other adjusts the hinged pointer. A thin orange path can follow the pointer toward the original page, only one path, not a network. Clearly keep the notes and original source as separate objects, no endorsement, no translation equality sign. A fresh physical metaphor of bibliographic cross-checking, not a formal diagram or screenshot. Plenty of white margin and no decorative props.
```

### Figure 03

```text
Generate exactly ONE standalone 16:9 horizontal illustration for a Chinese technical article, not a montage. Use case: illustration-story.
Pure white #FFFFFF background, thin slightly wobbly BLACK hand-drawn pen line art, flat sparse accent colors, lots of empty space, main scene occupies roughly 50% of canvas. Clean absurd editorial product sketch, restrained and deadpan. No title, no watermark, no logos. No paper texture, gradients, shadows, UI screenshots, PPT diagrams, boxed flowcharts, commercial vector art or cute children's cartoon.
Required active character XiaoM: a small mushroom worker with a RED rounded dome cap with 3–5 WHITE round spots, CREAM stem body, black hand-drawn outline and two BLACK dot eyes, tiny thin arms and legs, blank serious expression, not solid black, not smiling.
Theme: align synthetic data, written specifications and acceptance tests before trusting a repeatable chart. One fresh physical metaphor: XiaoM is a serious tiny bookbinder aligning three staggered translucent-looking white paper leaves in an oversized simple alignment jig, using both arms to push their punched registration holes into the same two alignment pins. Keep leaves visibly separated with thin black outlines, white opaque paper and sparse marks; no glass shading. The first leaf shows a tiny invented table of dots and squares and the small handwritten label '合成数据'; the second shows a ruler, a unit tick and boundary brackets and the short label '规格'; the third shows a tiny list of three blue checks next to corresponding dots and the short label '测试'. Repeated matching blue registration marks on all three leaves align into one clean stack under XiaoM's hands. On the far right a single plain output sheet holds a small simple black line plot with a blue check, connected by one short orange hand-drawn arrow only after the aligned stack. This expresses that expected values, units and tests must agree; a pretty graph alone is insufficient. Use only the three specified short Chinese handwritten labels, no numbers, no equations, no extra text. Keep the jig and papers simple and physically hand-drawn, with XiaoM actively doing the alignment, not standing beside a chart. Wide airy composition, generous clear margins.
```
