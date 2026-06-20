---
name: banner-creator
description: |
  Generate one photorealistic hero banner per blog article using the local FLUX.2 Klein MLX model.

  Trigger when the user says: 生成banner, 做封面, 生成封面图, create banner, make a banner, 配图.
  Also invoked automatically by the blog-publisher skill when an article has no banner.

  Produces: a 1200x630 JPG under 99KB, photorealistic, no text, themed to the article's keywords,
  saved to src/assets/images/<slug>-banner.jpg.

  Critical rules:
  - always photorealistic (never illustration / digital-art / cartoon)
  - canonical size 1200x630, file size strictly under 99KB
  - never bake text into the image
  - derive the subject from the article's title, tags, and description
---

# Banner Creator Skill

## Mission

Create one **photorealistic** hero banner for a blog article. The banner matches the existing
banner spec (1200x630, < 99KB) and is generated locally on Apple Silicon via FLUX.2 — no cloud,
no API cost.

## When To Use

- The user asks to generate/refresh an article banner (生成banner / 做封面 / create banner).
- `blog-publisher` needs a banner and the user didn't supply one → call this skill instead of
  picking a default-pool image.

## Requirements (same as flux-gen)

- macOS Apple Silicon, venv at `~/venvs/ml` with `mflux`, model at
  `~/.omlx/models/FLUX.2-klein-4B-mflux-4bit`.
- ImageMagick (`magick`) for resize + size capping.

The helper script checks these and prints `MODEL_MISSING` / `MFLUX_MISSING` with the fix command
if anything is absent.

## Non-Negotiable Output Spec

| Property | Value |
|---|---|
| Dimensions | **1200x630** (canonical banner size) |
| File size | **strictly < 99KB** (script caps at 98KB, falls back to 90KB) |
| Format | JPG, metadata stripped |
| Style | **photorealistic only** — cinematic, professional photography, 8k |
| Text | **none** — never render words/letters/watermarks in the image |
| Path | `src/assets/images/<slug>-banner.jpg` |
| Frontmatter | `heroImage: "../../assets/images/<slug>-banner.jpg"` |

## Workflow

### 1. Extract keywords from the article

Read the article's frontmatter (`title`, `titleEn`, `tags`, `description`) and skim the body.
Distill **one concrete, photographable scene** that represents the topic. Map abstract topics to
real-world imagery — FLUX renders *things*, not concepts:

| Article theme | Photographable scene |
|---|---|
| Deep research / data / agents | researcher workspace, multi-monitor data dashboards |
| Model training / RL / self-evolution | glowing neural-network fibers, macro circuitry, bokeh |
| Infrastructure / harness / systems | data-center aisle, server racks, developer terminal |
| Startup / brand / teams | small team at a whiteboard in a sunlit office |
| Crypto / payments / web3 | close-up of circuit-etched coins, secure hardware |
| Local AI / on-device | a laptop / Mac on a desk with ambient glow |
| Mycelium / public goods / nature | forest-floor mycelium macro, bioluminescent threads |

Pick the closest scene; if none fit, compose a fresh photorealistic scene from the keywords.

### 2. Build the subject prompt (English)

Write a short English **subject** describing the scene and mood. Do **not** add style suffixes —
the script appends `photorealistic, cinematic lighting, ultra detailed, professional photography,
8k, no text, ...` automatically.

Good subject examples:
- `A modern research workspace at night, several large monitors showing data dashboards and knowledge graphs, warm desk-lamp glow, shallow depth of field`
- `A small startup team collaborating around a whiteboard covered in sticky notes in a bright sunlit office, open laptops, natural window light`

Avoid: words you want printed, logos, brand names, "banner/poster/title" (invites text).

### 3. Generate

```bash
bash .agents/skills/banner-creator/generate-banner.sh "<slug>" "<english subject prompt>"
```

Optional 3rd arg = seed (default 42). Same seed + same prompt = same image; change it for variations.
Runs ~75s on M-series. The script prints the final path, dimensions, byte size, and the exact
`heroImage:` frontmatter line to paste.

### 4. Verify before using

- Confirm output is `1200x630` and `< 99KB` (script reports both).
- **Look at the image** (Read the file). FLUX occasionally renders stray glyphs or an off-topic
  scene — if so, rerun with a different seed or a refined subject prompt.
- Set the article's `heroImage` to the printed path.

### 5. Batch mode (multiple articles)

When banners are needed for several articles, generate sequentially (FLUX is single-GPU; parallel
runs contend for memory). A background loop is fine for large batches — write a small script that
calls `generate-banner.sh` once per `(slug, prompt)` and run it with `run_in_background: true`,
then review the montage when done.

## Style Guard (why photorealistic only)

The blog standardized on photorealistic banners (2026-06-19). Illustration / digital-art / cartoon
styles are deprecated. The script hard-codes the photorealistic suffix so every banner stays on-brand;
never strip it. If the user explicitly wants a non-photo style for a one-off, that's an override they
must state — default is always photorealistic.

## Integration With blog-publisher

`blog-publisher` step 2 ("Prepare Banner"): when no image is supplied, prefer this skill over the
default-pool fallback. Flow: extract keywords → `generate-banner.sh` → set `heroImage` to
`../../assets/images/<slug>-banner.jpg` → continue the normal build/deploy.
