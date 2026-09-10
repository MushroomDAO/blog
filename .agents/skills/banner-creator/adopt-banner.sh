#!/bin/bash
# ============================================================================
# adopt-banner.sh — build a banner from EXISTING public imagery (preferred when
# the source material already ships a good-looking image), instead of generating.
#
# Usage:  adopt-banner.sh <slug> <img-or-url> [img-or-url ...]
#
#   1 image   → cover-cropped to 1200x630
#   2-4 images→ side-by-side tiles, each cover-cropped, seamlessly filling 1200x630
#
# Cover-crop (-resize WxH^ + -extent) always FILLS the frame: no black bars,
# no letterboxing, no "half-black" banner.
#
# Stamps provenance `banner-creator/adopted src=<sources>` so verify-banner.sh
# can tell an intentionally adopted image from a stray screenshot.
#
# Rules for what you may adopt (enforced downstream by verify-banner.sh):
#   - public project imagery: README hero, og:image, official screenshots/art
#   - NOT: photos of identifiable people, our own site screenshots, text screenshots
#
# Exit: 0 pass · 1 verification failure · 2 usage/dep error
# ============================================================================
set -uo pipefail

SLUG="${1:-}"; shift || true
SIZE="${BANNER_SIZE:-1200x630}"
MAXKB="${BANNER_MAXKB:-98}"
W="${SIZE%x*}"; H="${SIZE#*x}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ -n "$SLUG" ] && [ "$#" -ge 1 ] || { echo "ERROR: usage: adopt-banner.sh <slug> <img-or-url> [more...]" >&2; exit 2; }
[ "$#" -le 4 ] || { echo "ERROR: at most 4 source images (got $#)" >&2; exit 2; }
command -v magick >/dev/null 2>&1 || { echo "MAGICK_MISSING: brew install imagemagick" >&2; exit 2; }

if [ -n "${BANNER_OUT_DIR:-}" ]; then OUT_DIR="$BANNER_OUT_DIR"
elif [ -d "src/assets/images" ]; then OUT_DIR="src/assets/images"
elif [ -d "public/images" ];     then OUT_DIR="public/images"
elif [ -d "assets" ];            then OUT_DIR="assets"
else OUT_DIR="banners"; fi
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/${SLUG}-banner.jpg"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/adopt-banner.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

N=$#
TILE_W=$(( W / N ))
REMAINDER=$(( W - TILE_W * N ))   # give leftover pixels to the last tile

echo "=== [adopt-banner] $SLUG ← $N source image(s) → $OUT (${SIZE}) ==="

i=0
SRCS=""
for SRC in "$@"; do
  i=$((i+1))
  LOCAL="$WORK/src$i"
  if printf '%s' "$SRC" | grep -qE '^https?://'; then
    curl -fsSL --max-time 45 "$SRC" -o "$LOCAL" || { echo "FAIL: cannot download $SRC" >&2; exit 2; }
  else
    [ -f "$SRC" ] || { echo "FAIL: no such file: $SRC" >&2; exit 2; }
    cp "$SRC" "$LOCAL"
  fi
  magick identify "$LOCAL" >/dev/null 2>&1 || { echo "FAIL: not a readable image: $SRC" >&2; exit 2; }

  # Warn on sources whose own edges are letterboxed/near-black — they'd bleed into the tile.
  MEAN=$(magick "$LOCAL" -colorspace gray -format "%[fx:mean]" info: 2>/dev/null || echo "1")
  if awk "BEGIN{exit !($MEAN < 0.06)}"; then
    echo "  WARN source $i is almost entirely dark (mean=$MEAN) — likely a black frame"
  fi

  TW=$TILE_W
  [ "$i" -eq "$N" ] && TW=$(( TILE_W + REMAINDER ))
  # cover-crop: fill the tile completely, center the composition, never pad.
  magick "$LOCAL" -auto-orient -resize "${TW}x${H}^" -gravity center -extent "${TW}x${H}" "$WORK/tile$i.png"
  echo "  tile $i: $(magick identify -format '%wx%h' "$WORK/tile$i.png")  ← $SRC"
  SRCS="$SRCS${SRCS:+,}$SRC"
done

if [ "$N" -eq 1 ]; then cp "$WORK/tile1.png" "$WORK/joined.png"
else magick "$WORK"/tile*.png +append "$WORK/joined.png"; fi

STAMP="banner-creator/adopted src=$SRCS"
render() { magick "$WORK/joined.png" -strip -set comment "$STAMP" -define "jpeg:extent=$1" "$OUT"; }
render "${MAXKB}KB"
BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
if [ "$BYTES" -ge 99000 ]; then render "90KB"; BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT"); fi

echo "=== [adopt-banner] done: $OUT ($(magick identify -format '%wx%h' "$OUT"), ${BYTES}B) ==="

# Adopted imagery legitimately carries logos/UI text, so text is a warning here,
# not a failure. Faces still fail (portrait rights) unless explicitly allowed.
if ! BANNER_ADOPTED=1 bash "$SKILL_DIR/verify-banner.sh" "$OUT"; then
  echo "" >&2
  echo "REJECTED: the adopted banner failed verification (see above)." >&2
  echo "Pick different source imagery, or fall back to generating one:" >&2
  echo "  bash $SKILL_DIR/generate-banner.sh \"$SLUG\" \"<scene prompt>\"" >&2
  exit 1
fi
echo "PATH: $OUT"
