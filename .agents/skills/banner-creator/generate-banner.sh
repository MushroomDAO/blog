#!/bin/bash
# ============================================================================
# Thin wrapper — single-sources the GLOBAL banner-creator skill to avoid drift.
# Real logic lives in ~/.claude/skills/banner-creator/generate-banner.sh.
# Run from the blog repo root: the global script auto-detects src/assets/images
# as the output dir, so behaviour is identical to before.
#   Usage: bash .agents/skills/banner-creator/generate-banner.sh <slug> "<prompt>" [seed]
# ============================================================================
set -euo pipefail
GLOBAL="$HOME/.claude/skills/banner-creator/generate-banner.sh"
if [ -f "$GLOBAL" ]; then
  exec bash "$GLOBAL" "$@"
fi
echo "ERROR: global banner-creator not installed at $GLOBAL" >&2
echo "Install it: cp -r .agents/skills/banner-creator ~/.claude/skills/ then re-run." >&2
exit 1
