#!/bin/bash
# banner-creator helper: generate one photorealistic article banner with local FLUX.2.
# Usage: generate-banner.sh <slug> "<english prompt>" [seed]
# Output: src/assets/images/<slug>-banner.jpg  (1200x630, < 99KB, photorealistic)
set -e

SLUG="$1"
PROMPT="$2"
SEED="${3:-42}"

if [ -z "$SLUG" ] || [ -z "$PROMPT" ]; then
  echo "ERROR: usage: generate-banner.sh <slug> \"<english prompt>\" [seed]" >&2
  exit 2
fi

# Resolve repo root (skill lives at <repo>/.agents/skills/banner-creator/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DEST_DIR="$REPO_ROOT/src/assets/images"
TMP_DIR="$HOME/Desktop/flux_outputs"
mkdir -p "$DEST_DIR" "$TMP_DIR"

MODEL="$HOME/.omlx/models/FLUX.2-klein-4B-mflux-4bit"
VENV="$HOME/venvs/ml/bin/activate"

# --- environment check ---
[ -d "$MODEL" ] || { echo "MODEL_MISSING: run 'source $VENV && mdt download Runpod/FLUX.2-klein-4B-mflux-4bit'" >&2; exit 3; }
# shellcheck disable=SC1090
source "$VENV"
python3 -c "import mflux" 2>/dev/null || { echo "MFLUX_MISSING: run 'source $VENV && pip install mflux'" >&2; exit 4; }

# Always enforce photorealism + no text; caller supplies the subject.
FULL_PROMPT="$PROMPT, photorealistic, cinematic lighting, ultra detailed, professional photography, 8k, no text, no words, no watermark, no letters"

RAW="$TMP_DIR/${SLUG}-banner.png"
OUT="$DEST_DIR/${SLUG}-banner.jpg"

echo "=== [banner-creator] generating $SLUG (seed=$SEED) ==="
# 1024x576 = 16:9, quality preset (16 steps) for realistic detail.
mflux-generate-flux2 \
  --model "$MODEL" \
  --base-model flux2-klein-4b \
  --prompt "$FULL_PROMPT" \
  --steps 16 --seed "$SEED" --width 1024 --height 576 --low-ram \
  --output "$RAW"

# Resize to the canonical 1200x630 banner size and cap file size under 99KB.
magick "$RAW" -resize 1200x630^ -gravity center -extent 1200x630 -strip \
  -define jpeg:extent=98KB "$OUT"

SIZE=$(stat -f%z "$OUT")
DIM=$(identify -format '%wx%h' "$OUT")
if [ "$SIZE" -ge 99000 ]; then
  echo "WARN: $OUT is $SIZE bytes (>=99KB); re-encoding harder" >&2
  magick "$RAW" -resize 1200x630^ -gravity center -extent 1200x630 -strip -define jpeg:extent=90KB "$OUT"
  SIZE=$(stat -f%z "$OUT")
fi

echo "=== [banner-creator] done: $OUT ($DIM, ${SIZE}B) ==="
echo "HERO_IMAGE_FRONTMATTER: heroImage: \"../../assets/images/${SLUG}-banner.jpg\""
