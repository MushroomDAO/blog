# LGUI 正文配图生成记录

- 日期：2026-10-31
- 对应文章：`src/content/blog/lgui-browser-game-ui-guide.md`（只读，未修改）
- Skill：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`
- 生成工具：内置 `image_gen`；三次独立生成，共三张；未使用CLI fallback。
- 原始生成文件保留在 `~/.codex/generated_images/`，未覆盖。
- 最终处理：Pillow等比居中适配、LANCZOS缩放、近白背景归一为纯白；MEDIANCUT 48色、无抖动；合并重复RGB调色板索引并仅保留实际使用的48个唯一条目；PNG压缩级别9。
- 所有最终图均为16:9、1120×630、48种实际使用颜色、48个唯一PLTE条目、无重复索引颜色、无透明通道、四角纯白、每张严格小于90,000字节；无需960×540回退。
- 视觉核对：小M承担核心动作，中文标签简短可读；Unity明确待验收，未来引擎没有接通；四道验收关口不代表已全部通过。
- 未修改文章或封面；未查看或计算封面哈希；未部署、未提交。

## 01

图注：小M在浏览器工作台修改UI XML与TypeScript源文件，并接收规则检查报告和截图证据。概念示意。

- 原始路径：`/Users/jason/.codex/generated_images/01a19198-5add-7691-b934-5a2000d5b69c/exec-4fb55f7f-a347-4367-a1d8-44ba50eed575.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/lgui-browser-game-ui-guide-fig-01.png`
- 最终规格：1120×630；48色；56,174字节；重复调色板颜色0；未回退。
- 原始SHA256：`4f9950fe4aa48f82f6b552b81d7638f625498ec9ab80eec2bdb7af9bf324a60b`
- 最终SHA256：`b0beeaf2d464d14615683d5fc0662c60593c7402039463b66ee47190c50ac16b`

实际提交的完整提示词：

```text
Use case: illustration-story. Create ONE standalone 16:9 horizontal Chinese article BODY illustration, not a collage, with a pure #FFFFFF white background. Spacious composition designed to remain legible at 1120x630. Minimal black hand-drawn slightly wobbly thin pen lines, flat fills, sparse red/orange/blue handwritten annotations with clearly legible Chinese characters. At least 35 percent empty white space; content centered with generous margins and quiet top space, subject about 50-60 percent of canvas. No overall title anywhere, no top-left title. No gradients, shadows, textures, beige paper, noise, 3D, realistic screenshots, polished vector art, commercial illustration, PPT layout, formal architecture diagram, dense technical text, childish cute mascot look, watermark.
Required protagonist XiaoM: serious deadpan small mushroom worker, red rounded cap with 3-5 WHITE spots and black pen outline, cream/off-white stem body, two tiny BLACK dot eyes, thin arms and legs, no costume, no smile or sparkling eyes. Red spotted cap is flat identity color. XiaoM must physically perform the central action, never stand aside as decoration. Black main ink; orange only for directional flow; blue small feedback annotations; red restrained emphasis. Simple objects and concise Chinese labels, no prose paragraphs. Treat the picture as a conceptual hand sketch, not actual LGUI software UI.
Theme 01: browser authoring workbench with rule-check and screenshot evidence returned to the worker.
A single whimsical low-tech desk whose upright lid looks like a hand-sketched browser window (three tiny round browser controls). XiaoM sits right inside this open browser-workbench, leaning over it and actively using a pencil to edit TWO large paper file sheets, one clearly labeled "UI XML", one clearly labeled "TypeScript". Short abstract strokes suggest code, no real code paragraphs. These file sheets are the UI and business source files, not arbitrary HTML.
At the right edge of this same desk a small hand-cranked paper outlet returns two distinct evidence artifacts toward XiaoM's free hand: a rule report sheet with three tiny checklist lines labeled "规则检查", and two small framed game inventory wireframe thumbnails (one wide, one tall) labeled together "截图证据". XiaoM both edits and receives the returned evidence, clearly forming a short physical feedback loop with one restrained orange curved arrow from the paper outlet back toward the editing hand. Screenshots must be simple black inventory box wireframes, not text or realistic screens. A small blue label "浏览器工作台" sits near the browser rim, not at top-left of canvas. ONLY these five labels: "浏览器工作台", "UI XML", "TypeScript", "规则检查", "截图证据". Large readable text, short labels beside relevant objects. No engine icons, deployment claims, test counts or success badges. Keep this one coherent sketch scene, not separate panels.
Generate exactly one image. Save the original output using the normal generated_images destination.
```

## 02

图注：同一份源文件经适配器送向Web和Unity；Unity仍待引擎验收，其他引擎保持未接入。概念示意。

- 原始路径：`/Users/jason/.codex/generated_images/01a19198-5add-7691-b934-5a2000d5b69c/exec-e1864cb0-cfd9-4f42-b95f-b0b80c338617.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/lgui-browser-game-ui-guide-fig-02.png`
- 最终规格：1120×630；48色；49,704字节；重复调色板颜色0；未回退。
- 原始SHA256：`a57db52ad48e488bc97caa7cc6736f7711877340c51e06b9003a4da1bcd5871c`
- 最终SHA256：`dc7c8a2ec22da61d7ee5b0eda72d5653ef9991c646a0110e5b935dada89b90b8`

实际提交的完整提示词：

```text
Use case: illustration-story. Create ONE standalone 16:9 horizontal Chinese article BODY illustration, not a collage, with a pure #FFFFFF white background. Spacious composition designed to remain legible at 1120x630. Minimal black hand-drawn slightly wobbly thin pen lines, flat fills, sparse red/orange/blue handwritten annotations with clearly legible Chinese characters. At least 35 percent empty white space; content centered with generous margins and quiet top space, subject about 50-60 percent of canvas. No overall title anywhere, no top-left title. No gradients, shadows, textures, beige paper, noise, 3D, realistic screenshots, polished vector art, commercial illustration, PPT layout, formal architecture diagram, dense technical text, childish cute mascot look, watermark.
Required protagonist XiaoM: serious deadpan small mushroom worker, red rounded cap with 3-5 WHITE spots and black pen outline, cream/off-white stem body, two tiny BLACK dot eyes, thin arms and legs, no costume, no smile or sparkling eyes. Red spotted cap is flat identity color. XiaoM must physically perform the central action, never stand aside as decoration. Black main ink; orange only for directional flow; blue small feedback annotations; red restrained emphasis. Simple objects and concise Chinese labels, no prose paragraphs. Treat the picture as a conceptual hand sketch, not actual LGUI software UI.
Theme 02: the SAME source bundle reaches Web and Unity through actual adapters; future engine adapters are still missing.
A serious XiaoM physically feeds ONE bound stack of source sheets labeled "XML + TypeScript" into a small handmade two-mouth splitter on a simple sawhorse. A single input visibly splits into TWO short orange channels; each channel passes through its own distinct black drawn adapter collar. ONE small label "适配器" with two fine pointer lines identifies those two collars.
Upper branch ends at a simple hand drawn browser screen labeled "Web", with sparse inventory wireframe boxes.
Lower branch ends at a plain open export crate labeled "Unity", with a few sheets inside it; immediately under Unity a very legible RED annotation "待验收". This is an export/integration destination only: NO green tick, no running game, no celebration or passed stamp anywhere on Unity, no claim Unity was tested. Both Web and Unity must have separate adapters and both derive from the single source stack.
Far right, isolated by a VERY LARGE white air gap, a faint black outline empty socket labeled "其他引擎" with RED annotation "未接入". A loose short plug lies next to that empty socket, visibly unplugged, and absolutely NO line or arrow connects future engines to the working splitter, source, Web, or Unity. Do not draw dotted or dashed connecting arrows either. Do not name particular future engines.
ONLY seven text strings: "XML + TypeScript", "适配器", "Web", "Unity", "待验收", "其他引擎", "未接入". Do not add an overall headline, success labels, claims of universal compatibility, extra engines or logos. Clear hand sketch with spatial separation, not an architecture chart.
Generate exactly one image. Save the original output using the normal generated_images destination.
```

## 03

图注：小M推动界面样本依次接受界面外观、交互行为、目标引擎和许可范围四项独立验收。概念示意。

- 原始路径：`/Users/jason/.codex/generated_images/01a19198-5add-7691-b934-5a2000d5b69c/exec-53c7e483-18df-428e-bd59-8eabb9bef842.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/lgui-browser-game-ui-guide-fig-03.png`
- 最终规格：1120×630；48色；53,653字节；重复调色板颜色0；未回退。
- 原始SHA256：`708a1ad7cdbbec67e72e2b9f2c080b43b6da8d45e37262335150ba81b0a7ac8c`
- 最终SHA256：`d0a20c6444c78cd24834dba4589a346c414ee5aa8deba4082a3956ed93428e3c`

实际提交的完整提示词：

```text
Use case: illustration-story. Create ONE standalone 16:9 horizontal Chinese article BODY illustration, not a collage, with a pure #FFFFFF white background. Spacious composition designed to remain legible at 1120x630. Minimal black hand-drawn slightly wobbly thin pen lines, flat fills, sparse red/orange/blue handwritten annotations with clearly legible Chinese characters. At least 35 percent empty white space; content centered with generous margins and quiet top space, subject about 50-60 percent of canvas. No overall title anywhere, no top-left title. No gradients, shadows, textures, beige paper, noise, 3D, realistic screenshots, polished vector art, commercial illustration, PPT layout, formal architecture diagram, dense technical text, childish cute mascot look, watermark.
Required protagonist XiaoM: serious deadpan small mushroom worker, red rounded cap with 3-5 WHITE spots and black pen outline, cream/off-white stem body, two tiny BLACK dot eyes, thin arms and legs, no costume, no smile or sparkling eyes. Red spotted cap is flat identity color. XiaoM must physically perform the central action, never stand aside as decoration. Black main ink; orange only for directional flow; blue small feedback annotations; red restrained emphasis. Simple objects and concise Chinese labels, no prose paragraphs. Treat the picture as a conceptual hand sketch, not actual LGUI software UI.
Theme 03: FOUR independent acceptance gates: UI appearance, interaction, target engine, and license.
An unusual tabletop acceptance instrument consists of FOUR freestanding thin hand-drawn inspection arches in a gently staggered left-to-right sequence, at the same scale and all clearly visible. It is like a paper game UI must fit through four different calibration frames. These arches are not a conveyor belt and not a formal flowchart.
XiaoM is central to the mechanism: leaning forward and physically pushing one little sled with a folded UI sample toward the first arch, while its other hand holds a magnifying glass against that sample to inspect it. The sample is a plain black box UI sketch. One small restrained orange guide stroke beneath the arches indicates the intended sequence; it must not indicate completion.
Exactly FOUR large short legible Chinese labels, each directly above its own arch: "界面外观", "交互行为", "目标引擎", "许可范围".
Each arch contains ONE tiny simple symbol which explains its distinct test: a layout ruler and wireframe for appearance; a fingertip pressing a button for interaction; a plain runtime cube for target engine; a legal document with a small keyhole for licensing. The last two arches remain physically closed with simple horizontal bars, awaiting their own separate checks. Do not show any arch with a passed checkmark, green light, completed stamp or universal success implication. This image expresses what MUST BE checked, not that the checks have passed. Licensing is scope review, not a promise of unrestricted use.
No other text, numbers, platform logos, paragraphs or headings. Spacious white hand sketch, playful absurd physical inspection device, serious working mushroom, not a four-column slide.
Generate exactly one image. Save the original output using the normal generated_images destination.
```
