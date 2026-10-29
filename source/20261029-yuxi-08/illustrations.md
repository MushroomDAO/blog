# Yuxi 0.8 — XiaoM body illustrations

Date: 2026-10-29 (Asia/Bangkok). Exactly three separate illustrations generated in this turn using the built-in `image_gen.imagegen` tool; one call per image, no collage, no banner, no pre-existing artwork reused. Backend model identifier was not exposed by the tool; no model claim is made.

## Scope and inputs

- Read article: `src/content/blog/yuxi-self-hosted-knowledge-agent-rag-graph-multi-agent-mcp.md`.
- Article SHA-256 before generation: `8fe3bd044f7109dcfa367b8f9b50112462ce0aac504b76d55d3170d9c1101661`.
- Applied `/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md` and all five required textual references: `references/style-dna.md`, `references/mushroom-ip.md`, `references/composition-patterns.md`, `references/prompt-template.md`, `references/qa-checklist.md`.
- Read `/Users/jason/.codex/skills/.system/imagegen/SKILL.md` for built-in generation and saving rules.
- No example image was supplied or copied. The current IP reference defines XiaoM as red cap / white spots / pale stem / black dot eyes; followed that reference rather than the outdated “black mushroom” shorthand.
- User-specified destinations take precedence over the skill's default assets directory.
- Article, deployment, commits, existing banner and unrelated working files are outside this task. Existing changes were present before work began.

## Deliverables and machine QA

Sizes use the stricter decimal limit: each file is less than 90,000 bytes. All are opaque palette PNGs, exactly 1280 × 720 (16:9). Four canvas corners are exact RGB white.

| Figure | File | Bytes | Decimal KB | Exact-white pixels |
|---|---|---:|---:|---:|
| 1 | `src/assets/images/yuxi-self-hosted-knowledge-agent-rag-graph-multi-agent-mcp-fig-01.png` | 75466 | 75.466 | 78.44% |
| 2 | `src/assets/images/yuxi-self-hosted-knowledge-agent-rag-graph-multi-agent-mcp-fig-02.png` | 76333 | 76.333 | 88.65% |
| 3 | `src/assets/images/yuxi-self-hosted-knowledge-agent-rag-graph-multi-agent-mcp-fig-03.png` | 56984 | 56.984 | 89.6% |

Exact-white percentage includes white regions inside objects and is a background diagnostic, not an estimate of semantic empty space.

- Figure 1 SHA-256: `2344650fbcd52ce8822261c99e70696985ef5926e2ea40f083e899249750be42`
- Figure 2 SHA-256: `562524b63d623461a3728a52f9397546db7049166b94a1eed2ee86a52aeb386a`
- Figure 3 SHA-256: `a2be6d3ec41598bb7346e9c53a1ad334e898979080b1c9a39a37377ff855988d`

## Provenance and processing

Original tool files are preserved at their generated locations:
- Figure 1: `/Users/jason/.codex/generated_images/01a18629-bf38-7d32-b633-efc2281c5a89/exec-3b2189b7-dbfe-4bc8-8c00-01b6b88fdc75.png`
- Figure 2: `/Users/jason/.codex/generated_images/01a18629-bf38-7d32-b633-efc2281c5a89/exec-6784cb55-25af-48a3-8850-effc89987d5e.png`
- Figure 3: `/Users/jason/.codex/generated_images/01a18629-bf38-7d32-b633-efc2281c5a89/exec-662a9b90-a328-4b94-ae71-9a3a28bacd7d.png`

Each raw image is 1672 × 941. ImageMagick performed format preparation only: proportional fit into 1280 × 720, centered white extent to exact 16:9, near-white background cleanup, metadata stripping, 64-color palette quantization without dithering, and PNG compression. No scene elements, text, or semantic relationships were drawn or composited by code. Temporary optimized files were in `/tmp/yuxi-illustrations-final/`; final files were copied into the three requested asset paths. No generation retries or discarded variants were needed.

Reproducible optimization command for each input/output pair:

```sh
magick INPUT.png -resize 1280x720 -background white -gravity center \
  -extent 1280x720 -white-threshold '94%' -strip +dither -colors 64 \
  -define png:compression-level=9 PNG8:OUTPUT.png
```

## Visual QA

Inspected each full generated image and each optimized final separately using the image viewer; no contact sheet or collage. Checked framing, character actions, source relationships, text, and readability after compression.

### 01 — Collaborative delivery with references

PASS. XiaoM actively carries reference sheets A and B to a common workbench. Two teammates have distinct paper mats and perform different tasks (magnifier verification and pen drafting). An open communal file tray is visible between the work areas. The delivered document retains matching A/B source tabs. Source tabs are illustrative identifiers, not claims about specific underlying documents.

Visible text: `核对`, `撰写`, `共享文件`, `交付`; source tabs `A` / `B`. All readable. Primary XiaoM has a red spotted cap and deadpan expression; secondary teammates vary in cap color. No new-model imagery, magic perfection, trophies, or autonomous approval claims. Workbench, character feet, source sheets and finished document are fully within the frame. White margins remain on every side.

### 02 — Scoped access and source-line inspection

PASS. Exactly one cabinet is open, with an inserted key tagged `授权`; XiaoM inspects a passage beside it. Two other cabinets remain closed and padlocked with `未授权` signs. The orange trace from the retrieved slip reaches the bracketed lines of the source page. Blue brackets visually match passage and source.

Visible text: `授权`, `未授权` (twice), `片段`, `原文`; source margin numbers `12`, `13`, `14`, `15`. All readable. Numbers are schematic line marks, not actual line citations from the article. No code, API credentials, invented tool names or implied universal access. All cabinets and page support fit inside the canvas; the retrieval trace is not clipped.

### 03 — Disposable execution, persistent outputs, separate VM option

PASS. XiaoM puts dismantled work-pod walls into a recycling cart; folded pod pieces and an empty remaining pod make disposal explicit. Produced files stay in a separate open cabinet, reached by an orange output path, and never enter the recycling cart. The left platform is labeled `共享内核`. A protected `VM` enclosure is on a physically separate base across white space, labeled `另选` and `Linux/KVM`.

Visible text: `用后清理`, `文件保留`, `共享内核`, `另选`, `Linux/KVM`, `VM`. All readable. Only the separate VM enclosure has a shield; disposable pods have no shield or lock. No equality sign or connecting arrow equates Docker/container isolation with VM isolation. The shield denotes the VM isolation option, not absolute security, certification, or a fully verified deployment. Work pods, recycling cart, file cabinet, VM and their bases are fully visible.

### Shared checks

- Three standalone 16:9 body illustrations, not banners or a multi-image composite.
- Clean white background and generous white areas; black hand-drawn contours with restrained colored accents.
- XiaoM performs the central action in every image; no solid black mascot, exaggerated smile or decorative corner character.
- Minimal readable text; no headline, dense explanations, UI screenshot, unreadable code or invented tool label.
- Palette compression retains linework, labels, source tags and arrow endpoints at final size.
- Scenes illustrate the article's proposed workflows and documented boundaries; they are not evidence of a live Yuxi deployment or successful business run.

## Workspace observation during final verification

The article hash changed during this illustration turn: initial SHA-256 was `8fe3bd044f7109dcfa367b8f9b50112462ce0aac504b76d55d3170d9c1101661`; the final read returned `b96702d08040e2f20540c3ddef6ee4854141622cbf70a3fee7a887e91e1fe381`. The later frontmatter includes `lastPublishedAt: "2026-10-29T05:41:47Z"` and an adjusted English description. This task issued no article edits, publishing commands, deployment commands or commits. The article was not reverted. The unchanged-article hash assertion therefore did not pass; this is recorded explicitly rather than claiming the workspace stayed unchanged. Figure files and this provenance note are the only workspace paths written by this task.

## Exact generation prompts

All calls used `transparent_background: false`; no input/reference images were passed. Required skill references were incorporated as text into the prompt.

### Figure 1

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, exactly 1536x864 or another exact 16:9 landscape. It is not a banner, not a collage, not multiple panels.
Visual DNA: completely pure white #FFFFFF background, delicate slightly wobbly BLACK hand-drawn pen lines. Sparse flat red/orange/blue accents, no shadow, no gradients, no paper texture, no noise. At least 40% white negative space, including generous clear margins on all four sides. Subject occupies middle 50%-60% of canvas. Serious absurd low-tech product-sketch atmosphere, not cute, not commercial illustration, not a formal flowchart, not PPT, no UI, no title at top-left.
Recurring character XiaoM: classic mushroom shape, flat RED rounded cap with 3-5 WHITE circular spots and a black outline, CREAM pale stem/body with black outline and two tiny BLACK dot eyes, thin arms and legs. Deadpan, serious, no smile, not a mascot. XiaoM performs the core action; never just decorates. No solid black mushroom. Use only minimal short legible handwritten labels specified below, no extra lettering, no gibberish, no code. Simple ruled strokes can represent document contents. Do not copy any prior illustration. Scene: a single continuous collaborative physical workbench seen at a gentle oblique angle, an odd but practical document-making bench. LEFT: a standing XiaoM physically carries two reference sheets toward the bench, with small attached blue source tabs "A" and "B". CENTER: two genuinely distinct teammate work areas on the SAME table, each with its own plain mushroom coworker and own sheet: one comparing a reference sheet under a magnifier, the other holding a pen to draft. Make their spaces clearly separate by a small gap and separate paper mats, not walls. At front edge of the table put one OPEN communal tray with several visible project file folders, labeled "共享文件", accessible from both work areas. RIGHT: a finished bound document rests open on a slightly raised end of the table; visible paragraphs have small matching BLUE source tabs "A" and "B" still attached at relevant lines. Label this document "交付". A short orange curved line across the tabletop suggests reference-to-draft-to-delivery movement; no conveyor belt, no robotic factory. XiaoM carrying the sheets is central and active. Teammate hands verify and write; show deliberate collaborative work, no magical perfect output, no success trophy, no model/brain/chip symbolism. Chinese labels only "核对" near first work area, "撰写" near second, "共享文件" on the communal tray, "交付" by the final document. Tiny source tags A/B allowed. No headline. Main meaning: shared project files plus distinct teammate contexts produce a deliverable that retains references, not a new AI model or guaranteed autonomous perfection.
```

### Figure 2

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, exactly 1536x864 or another exact 16:9 landscape. It is not a banner, not a collage, not multiple panels.
Visual DNA: completely pure white #FFFFFF background, delicate slightly wobbly BLACK hand-drawn pen lines. Sparse flat red/orange/blue accents, no shadow, no gradients, no paper texture, no noise. At least 40% white negative space, including generous clear margins on all four sides. Subject occupies middle 50%-60% of canvas. Serious absurd low-tech product-sketch atmosphere, not cute, not commercial illustration, not a formal flowchart, not PPT, no UI, no title at top-left.
Recurring character XiaoM: classic mushroom shape, flat RED rounded cap with 3-5 WHITE circular spots and a black outline, CREAM pale stem/body with black outline and two tiny BLACK dot eyes, thin arms and legs. Deadpan, serious, no smile, not a mascot. XiaoM performs the core action; never just decorates. No solid black mushroom. Use only minimal short legible handwritten labels specified below, no extra lettering, no gibberish, no code. Simple ruled strokes can represent document contents. Do not copy any prior illustration. Scene: a small hand-drawn archive with three freestanding cabinets, informal and asymmetrical, one connected action in one scene, no panels. One central cabinet door is open, and XiaoM at its left is visibly turning a small key in that cabinet's lock with one hand while inspecting a retrieved paper slip in the other. A blue tag on the key reads "授权"; the key unlocks this ONE cabinet only. Two other cabinets remain firmly closed with visible closed padlocks, one small label "未授权" between them, NO orange path crossing into them. To the right of the open cabinet, an enlarged source page stands on a simple reading support. It has clean ruled document lines and a narrow margin with only the small line numbers "12", "13", "14", "15". Highlight the middle two lines with a thin blue bracket. The retrieved paper slip has two short black ruled lines and a small matching blue bracket, label "片段". One orange mycelium thread FROM XiaoM's held retrieved slip runs TO the exact bracketed lines on the full source page. Source page label "原文". This is visual traceability, not a lock bypass. No invented tool names, NO code, NO terminal, no API names, no network icon spaghetti. Four short Chinese labels only: "授权", "未授权", "片段", "原文", plus the four line numbers. Enough whitespace and clear cabinet closure. Main meaning: a scoped key grants limited read access, retrieved text is checked against the source page and its line marks.
```

### Figure 3

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, exactly 1536x864 or another exact 16:9 landscape. It is not a banner, not a collage, not multiple panels.
Visual DNA: completely pure white #FFFFFF background, delicate slightly wobbly BLACK hand-drawn pen lines. Sparse flat red/orange/blue accents, no shadow, no gradients, no paper texture, no noise. At least 40% white negative space, including generous clear margins on all four sides. Subject occupies middle 50%-60% of canvas. Serious absurd low-tech product-sketch atmosphere, not cute, not commercial illustration, not a formal flowchart, not PPT, no UI, no title at top-left.
Recurring character XiaoM: classic mushroom shape, flat RED rounded cap with 3-5 WHITE circular spots and a black outline, CREAM pale stem/body with black outline and two tiny BLACK dot eyes, thin arms and legs. Deadpan, serious, no smile, not a mascot. XiaoM performs the core action; never just decorates. No solid black mushroom. Use only minimal short legible handwritten labels specified below, no extra lettering, no gibberish, no code. Simple ruled strokes can represent document contents. Do not copy any prior illustration. Scene: one sparse physical cleanup scene with a SEPARATE alternative option on the far right, no frames or split-screen. LEFT/MIDDLE: two lightweight disposable work pods (simple open wireframe cubicles on one plain shared base) contain a tiny work surface, a stool and no documents. XiaoM actively folds down one now-empty pod and pushes its detached wall into a small recycling cart; the other pod is already collapsed. Give these pods NO locks, no shields, no security fortress. Short annotation "用后清理" near the folding action. Center-right, clearly OUTSIDE the pods, stands one substantial open persistent file cabinet, with several finished document folders safely and visibly sitting inside it, labeled "文件保留". An orange curved path leads from the pod's former desk area toward those stored folders; it does not enter the trash cart. The work pods and file cabinet share a simple low ground base labeled "共享内核" in small gray-black hand lettering. FAR RIGHT, separated by generous blank space and a small unobtrusive blue handwritten "另选", is a self-contained modest protected machine enclosure on its OWN base, with one outlined shield on its door and the legible blue label "Linux/KVM" above it and "VM" on the enclosure. No connection, equality sign or arrow between this VM option and the disposable pods. Do NOT imply container security equals VM security, and do not imply absolute security or certification. Exactly these short labels: "用后清理", "文件保留", "共享内核", "另选", "Linux/KVM", "VM". No Docker whale/logo, no extra jargon, no unreadable code. Main meaning: temporary execution environment is cleared while project files persist; stronger VM isolation is a separate Linux/KVM-backed option. Keep the character's folding/clearing action unmistakable, and produced documents stay OUT of disposal.
```


Primary publisher note: concurrent article changes added the identity/governance paragraph and component list, then stamped lastPublishedAt. The image worker did not edit article content.
