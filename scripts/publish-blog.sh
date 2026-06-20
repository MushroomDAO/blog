#!/bin/bash
# ============================================================================
# publish-blog.sh — Canonical blog publish flow (M1 + optional M2 WeChat)
# ----------------------------------------------------------------------------
# Codifies the proven, idempotent path used by the blog-publisher skill:
#   validate frontmatter → check banner → build → deploy → validate → [WeChat]
#
# This REPLACES the divergent legacy scripts (publish.sh, publish-fast.sh,
# scripts/auto-publish.sh). Those auto-generated low-quality frontmatter and
# used inconsistent deploy commands. Write the article markdown first (by hand
# or via the model), generate its banner with the banner-creator skill, then
# run this.
#
# Usage:
#   scripts/publish-blog.sh src/content/blog/<slug>.md [--wechat] [--theme blue]
#   scripts/publish-blog.sh src/content/blog/<slug>.md --no-deploy   # build+validate only
#
# Env: BLOG_USER (default mushroom), plus .env for secrets / CF token.
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"

# ---- args ----
MD_FILE="${1:-}"
DO_WECHAT=false
DO_DEPLOY=true
THEME=""
shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --wechat) DO_WECHAT=true ;;
    --no-deploy) DO_DEPLOY=false ;;
    --theme) shift; THEME="$1" ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ -z "$MD_FILE" ] || [ ! -f "$MD_FILE" ]; then
  echo "❌ usage: scripts/publish-blog.sh <article.md> [--wechat] [--theme NAME] [--no-deploy]" >&2
  exit 1
fi

BLOG_USER="${BLOG_USER:-mushroom}"
[ -f .env ] && export $(grep -v '^#' .env | grep -E '^[A-Za-z_]+=' | xargs) || true

# Pull project + domain from the user config (single source of truth).
USER_CFG="config/users/${BLOG_USER}.js"; [ -f "$USER_CFG" ] || USER_CFG="config/users/default.js"
PROJECT=$(grep -m1 'projectName:' "$USER_CFG" | sed -E "s/.*projectName:[[:space:]]*'([^']+)'.*/\1/")
DOMAIN=$(grep -m1 'domain:' "$USER_CFG" | sed -E "s/.*domain:[[:space:]]*'([^']+)'.*/\1/")
PROJECT="${PROJECT:-blog-mushroom}"; DOMAIN="${DOMAIN:-blog.mushroom.cv}"
SLUG="$(basename "$MD_FILE" .md)"
echo "🍄 publish-blog | user=$BLOG_USER project=$PROJECT slug=$SLUG"

# ---- 1. frontmatter + SEO sanity ----
echo "[1/5] validating frontmatter & SEO…"
fm_fail=0
require() { grep -q "^$1:" "$MD_FILE" || { echo "  ✗ missing frontmatter: $1"; fm_fail=1; }; }
for k in title titleEn description descriptionEn pubDate updatedDate category tags heroImage; do require "$k"; done
# tags >= 3
tagline=$(grep -m1 '^tags:' "$MD_FILE" || true)
tagcount=$(echo "$tagline" | grep -o ',' | wc -l | tr -d ' '); tagcount=$((tagcount + 1))
[ "$tagcount" -ge 3 ] || { echo "  ✗ tags has <3 items: $tagline"; fm_fail=1; }
# bilingual + copyright
grep -q '<!--EN-->' "$MD_FILE" || { echo "  ✗ missing <!--EN--> bilingual divider"; fm_fail=1; }
grep -q 'Mycelium Protocol' "$MD_FILE" || { echo "  ✗ missing Mycelium Protocol copyright block"; fm_fail=1; }
# banner file exists
hero=$(grep -m1 '^heroImage:' "$MD_FILE" | sed -E 's/^heroImage:[[:space:]]*"?([^"]+)"?.*/\1/')
hero_path="$REPO_ROOT/src/content/blog/$hero"
if [ ! -f "$(python3 -c "import os;print(os.path.normpath('$hero_path'))")" ]; then
  echo "  ✗ heroImage file not found: $hero"
  echo "    → run the banner-creator skill first:"
  echo "      bash .agents/skills/banner-creator/generate-banner.sh \"$SLUG\" \"<english scene prompt>\""
  fm_fail=1
fi
[ "$fm_fail" -eq 0 ] || { echo "❌ frontmatter/SEO checks failed — fix and rerun"; exit 1; }
echo "  ✓ frontmatter OK (tags=$tagcount, bilingual, banner present)"

# ---- 2. build ----
echo "[2/5] building…"
pnpm build 2>&1 | tail -3
ls "dist/blog/$SLUG" >/dev/null 2>&1 || { echo "❌ route dist/blog/$SLUG not built"; exit 1; }
echo "  ✓ route built: /blog/$SLUG/"

if [ "$DO_DEPLOY" = false ]; then echo "✅ build+validate done (--no-deploy)"; exit 0; fi

# ---- 3. deploy (the one proven-good command) ----
echo "[3/5] deploying to Cloudflare Pages ($PROJECT)…"
NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist \
  --project-name="$PROJECT" --branch=main --commit-dirty=true 2>&1 | tail -4

# ---- 4. validate live ----
echo "[4/5] validating live URL…"
code=$(curl -s -o /dev/null -w '%{http_code}' "https://$DOMAIN/blog/$SLUG/" || echo 000)
echo "  https://$DOMAIN/blog/$SLUG/ → $code"
[ "$code" = "200" ] || echo "  ⚠️ not 200 yet (CDN may lag a few seconds)"

# ---- 5. optional WeChat draft ----
if [ "$DO_WECHAT" = true ]; then
  echo "[5/5] creating WeChat draft…"
  ( cd pipeline/m2 && node index.js "../../$MD_FILE" ${THEME:+--theme "$THEME"} 2>&1 | grep -E 'Draft created|Title:|❌|Error' )
else
  echo "[5/5] skipped WeChat (pass --wechat to enable)"
fi

echo "✅ done → https://$DOMAIN/blog/$SLUG/"
