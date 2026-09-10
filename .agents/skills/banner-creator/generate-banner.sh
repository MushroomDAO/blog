#!/bin/bash
# ============================================================================
# banner-creator — generate ONE photorealistic article/blog banner locally
# via FLUX.2 Klein (MLX, Apple Silicon). Portable: works in any project.
# ----------------------------------------------------------------------------
# Usage:  generate-banner.sh <slug> "<english scene prompt>" [seed]
#
# Output: <OUT_DIR>/<slug>-banner.jpg  — 1200x630, < 99KB, photorealistic, no text
#
# Output dir resolution (first match wins):
#   1. $BANNER_OUT_DIR              (explicit override)
#   2. ./src/assets/images         (Astro blog convention)
#   3. ./public/images             (Next/static-site convention)
#   4. ./assets  or  ./banners     (generic)
#
# Tunables (env):  BANNER_SIZE=1200x630   BANNER_MAXKB=98   BANNER_STEPS=16
# Deps: mflux venv (~/venvs/ml), FLUX.2 model (~/.omlx/models/...), ImageMagick.
# ============================================================================
set -euo pipefail

SLUG="${1:-}"
PROMPT="${2:-}"
SEED="${3:-42}"
SIZE="${BANNER_SIZE:-1200x630}"
MAXKB="${BANNER_MAXKB:-98}"
STEPS="${BANNER_STEPS:-16}"

if [ -z "$SLUG" ] || [ -z "$PROMPT" ]; then
  echo "ERROR: usage: generate-banner.sh <slug> \"<english scene prompt>\" [seed]" >&2
  exit 2
fi

# --- resolve output dir ---
if [ -n "${BANNER_OUT_DIR:-}" ]; then OUT_DIR="$BANNER_OUT_DIR"
elif [ -d "src/assets/images" ]; then OUT_DIR="src/assets/images"
elif [ -d "public/images" ];     then OUT_DIR="public/images"
elif [ -d "assets" ];            then OUT_DIR="assets"
else OUT_DIR="banners"; fi
mkdir -p "$OUT_DIR"

MODEL="${FLUX_MODEL_PATH:-$HOME/.omlx/models/FLUX.2-klein-4B-mflux-4bit}"
VENV="${FLUX_VENV:-$HOME/venvs/ml/bin/activate}"
TMP_DIR="${TMPDIR:-/tmp}/banner-creator"; mkdir -p "$TMP_DIR"

# --- environment check ---
[ -d "$MODEL" ] || { echo "MODEL_MISSING: source $VENV && mdt download Runpod/FLUX.2-klein-4B-mflux-4bit" >&2; exit 3; }
[ -f "$VENV" ]  || { echo "VENV_MISSING: expected mflux venv at $VENV (override with FLUX_VENV)" >&2; exit 3; }
# shellcheck disable=SC1090
source "$VENV"
python3 -c "import mflux" 2>/dev/null || { echo "MFLUX_MISSING: source $VENV && pip install mflux" >&2; exit 4; }
command -v magick >/dev/null 2>&1 || { echo "MAGICK_MISSING: install ImageMagick (brew install imagemagick)" >&2; exit 5; }

# --- always enforce photorealism + no text; caller supplies the subject only ---
FULL_PROMPT="$PROMPT, photorealistic, cinematic lighting, ultra detailed, professional photography, 8k, no text, no words, no letters, no watermark"

# Generate at 16:9 then crop to the banner size (keeps composition centered).
GEN_W=1024; GEN_H=576
OUT="$OUT_DIR/${SLUG}-banner.jpg"

# IMPORTANT: mflux does NOT overwrite an existing --output; it writes "<name>_1.png"
# instead. Reusing a fixed RAW path therefore silently re-crops the FIRST run's image
# and makes seed changes a no-op. Generate into a fresh, empty per-run directory.
RUN_DIR="$TMP_DIR/${SLUG}-s${SEED}"
rm -rf "$RUN_DIR"; mkdir -p "$RUN_DIR"
RAW="$RUN_DIR/raw.png"

echo "=== [banner-creator] $SLUG → $OUT (seed=$SEED, ${SIZE}, <${MAXKB}KB) ==="
mflux-generate-flux2 \
  --model "$MODEL" --base-model flux2-klein-4b \
  --prompt "$FULL_PROMPT" \
  --steps "$STEPS" --seed "$SEED" --width "$GEN_W" --height "$GEN_H" --low-ram \
  --output "$RAW"

# Belt and braces: if mflux still side-stepped the exact path, take whatever PNG it wrote.
if [ ! -f "$RAW" ]; then
  RAW="$(find "$RUN_DIR" -maxdepth 1 -name '*.png' -print -quit)"
  [ -n "$RAW" ] || { echo "ERROR: mflux produced no PNG in $RUN_DIR" >&2; exit 7; }
fi

# Provenance stamp — proves this banner was generated locally by FLUX.2 Klein.
# verify-banner.sh rejects any banner lacking it (screenshots, frame-grabs, cloud AI).
# NOTE: -strip removes comments, so -set comment MUST come after it.
STAMP="banner-creator/flux2-klein-4b seed=$SEED steps=$STEPS"

render() {  # $1 = jpeg extent target
  magick "$RAW" -resize "${SIZE}^" -gravity center -extent "$SIZE" -strip \
    -set comment "$STAMP" -define "jpeg:extent=$1" "$OUT"
}

render "${MAXKB}KB"
BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
if [ "$BYTES" -ge 99000 ]; then
  render "90KB"
  BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
fi

echo "=== [banner-creator] done: $OUT ($(magick identify -format '%wx%h' "$OUT"), ${BYTES}B) ==="

# --- mandatory self-verification (provenance, size, no text, no faces) -------
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! bash "$SKILL_DIR/verify-banner.sh" "$OUT"; then
  echo "" >&2
  echo "REJECTED: the generated banner failed verification (see above)." >&2
  echo "Retry with a different seed, e.g.:" >&2
  echo "  bash $SKILL_DIR/generate-banner.sh \"$SLUG\" \"$PROMPT\" $((SEED + 1))" >&2
  exit 6
fi

echo "PATH: $OUT"
