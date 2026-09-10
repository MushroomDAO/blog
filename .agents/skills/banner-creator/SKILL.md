---
name: banner-creator
description: |
  Generate a photorealistic hero/cover banner for an article, blog post, or page using
  the local FLUX.2 Klein model (MLX, Apple Silicon). Zero cloud cost.

  Use when the user says: generate a banner, make a cover image, 生成banner, 做封面,
  生成封面图, 配图, "I need a header image for this article/post".

  Prefers reusing attractive public imagery the source already ships (README hero, og:image,
  official screenshots) — cover-cropped or stitched to size; otherwise generates an original
  photorealistic scene locally.

  Produces a 1200x630 JPG under 99KB, themed to the article's keywords. Every banner is
  machine-verified for provenance, framing, rendered text and human faces — never a text
  screenshot, a video frame-grab of a person, or our own page. Portable across projects
  (auto-detects the output directory).

  Core capability: adopt-or-generate, then verify, article banners.
---

# Banner Creator (global skill)

Turn an article into one **photorealistic, original** banner, locally, in ~75 seconds. No API, no cost.

## The hard rule

> **Every banner must come from one of exactly two vetted paths, and must pass `verify-banner.sh`.**
>
> 1. **ADOPT** — reuse good-looking public imagery the source material already ships
>    (README hero, `og:image`, official screenshots/artwork). *Try this first.*
> 2. **GENERATE** — if there is nothing worth adopting, render an original photorealistic
>    scene with the local FLUX.2 Klein 4B model.
>
> Never use, on either path: a photo of an identifiable person, a video frame-grab of someone,
> our **own** site/page screenshot, a screenshot of the article's text, or a garbled cloud-AI
> image with misspelled words.
>
> This is enforced, not advisory. Both scripts self-verify and refuse to hand you a bad banner.

## Which path? Decide in this order

1. **Look at the source material first.** Does the project/article ship an image that is
   genuinely attractive and on-topic — a README hero, an `og:image`, official product art or a
   clean UI screenshot? We republish public media non-commercially, so this is normally fine.
2. If yes → **`adopt-banner.sh`**. One image, or 2–4 stitched side by side.
3. If there is nothing good, or the only candidates are the forbidden kinds above →
   **`generate-banner.sh`**.

Disqualify a candidate if it: shows a recognizable person · is a frame-grab from a video ·
is one of *our* pages · is mostly text · is dark/empty on one side · is smaller than ~600px wide.

## What it guarantees

| Property | Value | Enforced by |
|---|---|---|
| Origin | **local FLUX.2 Klein 4B**, or **deliberately adopted** public imagery | provenance stamp in JPEG comment |
| Dimensions | **1200×630** (override `BANNER_SIZE`) | verify |
| File size | **< 99KB** (targets 98KB, falls back to 90KB) | verify |
| Framing | **fills the frame** — no letterbox, no black bars, no dead half | cover-crop + edge check |
| Style (generated) | **photorealistic only** — cinematic, professional photography, 8k | hard-coded prompt suffix |
| Text | generated: **none** (hard fail) · adopted: logos/UI tolerated (warning) | verify |
| Faces | **none** — no recognizable people (portrait rights) | verify |
| Output | `<out>/<slug>-banner.jpg` | — |

## Requirements

- macOS Apple Silicon, mflux venv at `~/venvs/ml`, FLUX.2 model at
  `~/.omlx/models/FLUX.2-klein-4B-mflux-4bit`, ImageMagick (`magick`), `swift` (Vision).
- The scripts check these and print `*_MISSING` with the exact fix command if absent.
- See the companion `flux-gen` skill for model download / install.

## Workflow A — adopt existing imagery (preferred when something good exists)

```bash
bash ~/.claude/skills/banner-creator/adopt-banner.sh "<slug>" <img-or-url> [more-imgs...]
```

- Accepts local paths **or** URLs (downloaded automatically). 1–4 sources.
- 1 source → cover-cropped to 1200×630. 2–4 → equal tiles stitched left-to-right, each
  cover-cropped. Cover-crop **always fills** its tile, so a stitched banner never shows
  black bars or a half-dark frame.
- Stamps `banner-creator/adopted src=<sources>` — the sources are recorded in the JPEG itself.
- Self-verifies. Faces still fail; logo/UI text only warns.
- Good stitching pairs: product screenshot + architecture diagram · logo art + hero shot.
  Don't stitch images with clashing backgrounds (one white, one black) — the seam looks broken.

## Workflow B — generate an original banner

### 1. Distill ONE photographable scene from the article

FLUX renders *things*, not concepts. Read the article's title / tags / description and map
the abstract topic to a concrete scene:

| Theme | Scene |
|---|---|
| Deep research / data / agents | researcher desk, multi-monitor data dashboards |
| Model training / RL / self-evolution | glowing neural-network fibers, macro, bokeh |
| Infrastructure / systems / harness | data-center aisle, server racks, terminal |
| Startup / brand / teams | an empty sunlit office, whiteboard with abstract marks (**no people**) |
| Crypto / payments / web3 | circuit-etched coins, secure hardware, macro |
| Local / on-device AI | a laptop on a desk, ambient glow |
| Video / editing / media tools | editing suite, timeline monitors, studio light (**no people**) |
| Nature / public goods / mycelium | forest-floor mycelium macro, soft light |

If none fit, compose a fresh photorealistic scene from the keywords. **Do not put a person in
the scene** — a detected face fails verification.

### 2. Generate (self-verifies before it returns)

```bash
bash ~/.claude/skills/banner-creator/generate-banner.sh "<slug>" "<english scene prompt>" [seed]
```

- 3rd arg = seed (default 42). Change it for a different variation.
- Output dir auto-detected: `$BANNER_OUT_DIR` → `src/assets/images` → `public/images` →
  `assets` → `banners`. Set `BANNER_OUT_DIR=...` to force one.
- Write only the **subject** in the prompt — the script appends the photorealistic +
  "no text" style suffix itself. Don't include words you want printed, logos, or
  "banner/poster/title" (those invite text artifacts).
- On success the JPEG is stamped `banner-creator/flux2-klein-4b seed=… steps=…`.
- **If verification fails the script exits 6 and the banner is unusable — rerun with `seed+1`.**

### 3. Verify (mandatory; run standalone to audit any existing banner)

```bash
bash ~/.claude/skills/banner-creator/verify-banner.sh <image> [WxH]
```

Exit `0` pass · `1` violation · `2` bad usage/missing dep. Checks:

1. **provenance** — JPEG comment carries a `banner-creator/flux2-klein` or
   `banner-creator/adopted` stamp. This is what blocks screenshots, frame-grabs and
   stray cloud-AI images.
2. **framing** — no near-black edge strip (letterboxing / dead half). Warning.
3. **dimensions** — equals expected size (default `1200x630`).
4. **file size** — `< 99000` bytes.
5. **no text** — Vision OCR finds no string with confidence ≥ 0.6 and ≥ 3 chars.
   Hard fail for generated banners; warning for adopted ones (`BANNER_ADOPTED=1`).
6. **no faces** — Vision finds no human face.

Known trap: FLUX likes to write on *instruments* — dials, gauges, monitors, control panels,
clocks — producing gibberish like `00:0` or `DMIB5`. If OCR trips on such a scene, don't just
bump the seed; drop the lettering-prone object from the prompt (prefer cables, fibers, textures).

Then **still look at the image yourself.** Vision catches glyphs and faces; it cannot tell you
the scene is off-topic or ugly. If it is, rerun with a different seed or a tighter subject.

#### Escape hatches (use only with explicit user consent, and say so out loud)

| Env | Effect | When |
|---|---|---|
| `BANNER_ALLOW_UNSIGNED=1` | provenance failure → warning | auditing a legacy banner you know is original |
| `BANNER_ALLOW_FACES=1` | face failure → warning | the user explicitly wants a person in frame and owns the rights |

Never set these to make a failing banner "pass" silently. A legacy FLUX banner with no stamp is
better fixed by **regenerating it with the same prompt and seed** — the output is identical and
arrives stamped.

## Tunables (env)

`BANNER_OUT_DIR`, `BANNER_SIZE` (default 1200x630), `BANNER_MAXKB` (default 98),
`BANNER_STEPS` (default 16), `FLUX_MODEL_PATH`, `FLUX_VENV`.

## Files

| File | Role |
|---|---|
| `adopt-banner.sh` | reuse public imagery → cover-crop/stitch → stamp → auto-verify |
| `generate-banner.sh` | FLUX generation → crop → stamp → auto-verify |
| `verify-banner.sh` | standalone gate: provenance, framing, size, text, faces |
| `inspect-banner.swift` | macOS Vision OCR + face detection → JSON |

Implementation note: `mflux` does **not** overwrite an existing `--output`; it silently writes
`<name>_1.png`. `generate-banner.sh` therefore renders into a fresh per-seed directory. Never
reintroduce a fixed RAW path — it makes seed changes a silent no-op.

## Style guard

Photorealistic is hard-coded in the script and must not be stripped — it is the whole point
of this skill. A non-photo style is an explicit one-off override the user must request.
