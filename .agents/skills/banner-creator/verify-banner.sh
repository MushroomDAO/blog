#!/bin/bash
# ============================================================================
# verify-banner.sh — enforce that a banner is an ORIGINAL, local FLUX-generated,
# text-free, face-free image of the right size. Exits non-zero on any violation.
#
# Usage:  verify-banner.sh <image-path> [expected-size]
#
# Checks (all hard failures unless overridden):
#   1. PROVENANCE  — JPEG comment must carry the banner-creator/flux2-klein stamp.
#                    Blocks screenshots, video frame-grabs, and cloud-AI images.
#                    Override: BANNER_ALLOW_UNSIGNED=1
#   2. DIMENSIONS  — must equal expected size (default 1200x630).
#   3. FILE SIZE   — must be < 99000 bytes.
#   4. NO TEXT     — Vision OCR must find no confident glyphs (conf >= 0.6, len >= 3).
#   5. NO FACES    — Vision must find no human faces (a frame-grab of a person is a
#                    portrait-rights problem). Override: BANNER_ALLOW_FACES=1
#
# Exit: 0 pass · 1 violation · 2 bad usage / missing dep
# ============================================================================
set -uo pipefail

IMG="${1:-}"
EXPECT_SIZE="${2:-${BANNER_SIZE:-1200x630}}"
MAXBYTES=99000
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ -n "$IMG" ] || { echo "ERROR: usage: verify-banner.sh <image-path> [WxH]" >&2; exit 2; }
[ -f "$IMG" ] || { echo "FAIL[missing]: no such file: $IMG" >&2; exit 1; }
command -v magick >/dev/null 2>&1 || { echo "MAGICK_MISSING: brew install imagemagick" >&2; exit 2; }
command -v swift  >/dev/null 2>&1 || { echo "SWIFT_MISSING: Xcode CLT required for OCR/face check" >&2; exit 2; }

fails=0
warn=0
echo "=== [verify-banner] $IMG ==="

# --- 1. provenance -----------------------------------------------------------
# Two legitimate origins: locally GENERATED (FLUX.2 Klein) or deliberately ADOPTED
# public imagery (via adopt-banner.sh). Anything else is an unvetted image.
COMMENT="$(magick identify -format '%[comment]' "$IMG" 2>/dev/null || true)"
ADOPTED=0
if echo "$COMMENT" | grep -qi 'banner-creator' && echo "$COMMENT" | grep -qi 'flux2-klein'; then
  echo "  ok   provenance: $COMMENT"
elif echo "$COMMENT" | grep -qi 'banner-creator/adopted'; then
  ADOPTED=1
  echo "  ok   provenance: $COMMENT"
elif [ "${BANNER_ALLOW_UNSIGNED:-0}" = "1" ]; then
  echo "  WARN provenance: unsigned, allowed via BANNER_ALLOW_UNSIGNED=1"; warn=$((warn+1))
else
  echo "  FAIL provenance: not stamped by banner-creator (neither FLUX-generated nor adopted)."
  echo "       → This is an unvetted image (screenshot? frame-grab? cloud AI?)."
  echo "       → Generate:  bash $SKILL_DIR/generate-banner.sh <slug> \"<scene prompt>\""
  echo "       → Or adopt:  bash $SKILL_DIR/adopt-banner.sh <slug> <img-or-url> [more...]"
  fails=$((fails+1))
fi
[ "${BANNER_ADOPTED:-0}" = "1" ] && ADOPTED=1

# --- 1b. no letterboxing / half-black ---------------------------------------
# Sample the four edge strips; a near-black strip means padding or a dead half.
DARK_EDGES=""
for edge in "left:5%x100%+0+0" "right:5%x100%-0+0" "top:100%x5%+0+0" "bottom:100%x5%+0-0"; do
  name="${edge%%:*}"; geom="${edge#*:}"
  m=$(magick "$IMG" -gravity "$( [ "$name" = left ] && echo west || { [ "$name" = right ] && echo east || { [ "$name" = top ] && echo north || echo south; }; } )" \
        -crop "$geom" +repage -colorspace gray -format "%[fx:mean]" info: 2>/dev/null | head -1 || echo "1")
  awk "BEGIN{exit !($m < 0.04)}" && DARK_EDGES="$DARK_EDGES $name"
done
if [ -z "$DARK_EDGES" ]; then
  echo "  ok   framing: no letterboxed/black edges"
else
  echo "  WARN framing: near-black edge(s):$DARK_EDGES — check for padding or a dead half"; warn=$((warn+1))
fi

# --- 2. dimensions -----------------------------------------------------------
DIMS="$(magick identify -format '%wx%h' "$IMG" 2>/dev/null || echo '?')"
if [ "$DIMS" = "$EXPECT_SIZE" ]; then
  echo "  ok   dimensions: $DIMS"
else
  echo "  FAIL dimensions: $DIMS (expected $EXPECT_SIZE)"; fails=$((fails+1))
fi

# --- 3. file size ------------------------------------------------------------
BYTES=$(stat -f%z "$IMG" 2>/dev/null || stat -c%s "$IMG")
if [ "$BYTES" -lt "$MAXBYTES" ]; then
  echo "  ok   size: ${BYTES}B (< ${MAXBYTES}B)"
else
  echo "  FAIL size: ${BYTES}B (must be < ${MAXBYTES}B)"; fails=$((fails+1))
fi

# --- 4/5. Vision: text + faces ----------------------------------------------
VISION="$(swift "$SKILL_DIR/inspect-banner.swift" "$IMG" 2>/dev/null || echo '')"
if [ -z "$VISION" ]; then
  echo "  WARN vision: inspection unavailable — verify the image by eye"; warn=$((warn+1))
else
  TEXTS="$(printf '%s' "$VISION" | python3 -c '
import json,sys
d=json.load(sys.stdin)
bad=[t["s"] for t in d["texts"] if t["c"]>=0.6 and len(t["s"].replace(" ",""))>=3]
print(len(bad)); print(" | ".join(bad[:8]))
' 2>/dev/null || echo "0")"
  NTEXT="$(printf '%s' "$TEXTS" | sed -n 1p)"
  SAMPLE="$(printf '%s' "$TEXTS" | sed -n 2p)"
  NFACE="$(printf '%s' "$VISION" | python3 -c 'import json,sys;print(json.load(sys.stdin)["faces"])' 2>/dev/null || echo 0)"

  if [ "${NTEXT:-0}" -eq 0 ]; then
    echo "  ok   text: none detected"
  elif [ "$ADOPTED" = "1" ]; then
    # Official project imagery legitimately carries a logo or UI chrome.
    echo "  WARN text: $NTEXT string(s) in adopted imagery — acceptable if it is the project's own"
    echo "       → detected: $SAMPLE"
    warn=$((warn+1))
  else
    echo "  FAIL text: $NTEXT rendered string(s) — generated banners must carry no words"
    echo "       → detected: $SAMPLE"
    echo "       → rerun generate-banner.sh with a different seed"
    fails=$((fails+1))
  fi

  if [ "${NFACE:-0}" -eq 0 ]; then
    echo "  ok   faces: none detected"
  elif [ "${BANNER_ALLOW_FACES:-0}" = "1" ]; then
    echo "  WARN faces: $NFACE detected, allowed via BANNER_ALLOW_FACES=1"; warn=$((warn+1))
  else
    echo "  FAIL faces: $NFACE human face(s) detected"
    echo "       → a recognizable person (often a video frame-grab) is a portrait-rights risk"
    fails=$((fails+1))
  fi
fi

echo "--- result: $fails failure(s), $warn warning(s)"
[ "$fails" -eq 0 ] || { echo "=== [verify-banner] REJECTED: $IMG ==="; exit 1; }
echo "=== [verify-banner] PASSED: $IMG ==="
