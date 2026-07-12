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
BANNER_PROMPT=""
shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --wechat) DO_WECHAT=true ;;
    --no-deploy) DO_DEPLOY=false ;;
    --theme) shift; THEME="$1" ;;
    --gen-banner) shift; BANNER_PROMPT="$1" ;;
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

# ---- 0. optional: generate photorealistic banner end-to-end (--gen-banner) ----
if [ -n "$BANNER_PROMPT" ]; then
  echo "[0] generating photorealistic banner via banner-creator…"
  bash .agents/skills/banner-creator/generate-banner.sh "$SLUG" "$BANNER_PROMPT"
  NEW_HERO="../../assets/images/${SLUG}-banner.jpg"
  if grep -q '^heroImage:' "$MD_FILE"; then
    sed -i '' -E "s|^heroImage:.*|heroImage: \"$NEW_HERO\"|" "$MD_FILE"
  else
    sed -i '' -E "0,/^---$/!{ /^---$/i\\
heroImage: \"$NEW_HERO\"
}" "$MD_FILE" 2>/dev/null || true
  fi
  echo "  ✓ heroImage set → $NEW_HERO"
fi

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

# ---- 3. deploy ----
# Prefer a real CA bundle over the insecure TLS bypass. Set CF_CA_CERT (or
# NODE_EXTRA_CA_CERTS) to your proxy's CA .pem to drop the workaround entirely.
echo "[3/5] deploying to Cloudflare Pages ($PROJECT)…"
CA="${NODE_EXTRA_CA_CERTS:-${CF_CA_CERT:-}}"
if [ -n "$CA" ] && [ -f "$CA" ]; then
  echo "  🔒 using CA bundle: $CA (secure TLS)"
  NODE_EXTRA_CA_CERTS="$CA" npx wrangler pages deploy dist \
    --project-name="$PROJECT" --branch=main --commit-dirty=true 2>&1 | tail -4
else
  echo "  ⚠️ no CA bundle set (CF_CA_CERT/NODE_EXTRA_CA_CERTS) — falling back to TLS bypass."
  echo "     To fix the root cause, point CF_CA_CERT at your proxy CA .pem."
  NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist \
    --project-name="$PROJECT" --branch=main --commit-dirty=true 2>&1 | tail -4
fi

# ---- 4. validate live ----
echo "[4/5] validating live URL…"
code=$(curl -s -o /dev/null -w '%{http_code}' "https://$DOMAIN/blog/$SLUG/" || echo 000)
echo "  https://$DOMAIN/blog/$SLUG/ → $code"
[ "$code" = "200" ] || echo "  ⚠️ not 200 yet (CDN may lag a few seconds)"

# ---- 4.5. git commit (critical: prevents CF CI/CD rebuild from stripping article from homepage) ----
echo "[4.5] committing article to git…"
git add "$MD_FILE" 2>/dev/null || true
# also add banner if it lives under assets/images/
BANNER_PATH="src/assets/images/${SLUG}-banner.jpg"
[ -f "$BANNER_PATH" ] && git add "$BANNER_PATH" 2>/dev/null || true
# figure-illustrations if any
for fig in src/assets/images/${SLUG}-fig-*.png; do
  [ -f "$fig" ] && git add "$fig" 2>/dev/null || true
done
if git diff --cached --quiet; then
  echo "  ✓ nothing new to commit (already tracked)"
else
  git commit -m "feat(blog): publish ${SLUG}" 2>&1
  echo "  ✓ committed — run 'git push' to sync remote and prevent CI/CD overwrite"
fi

# ---- 5. optional WeChat draft ----
if [ "$DO_WECHAT" = true ]; then
  PRIOR_JSON="pipeline/m2/output/${SLUG}.json"
  # Idempotency (mapping-only, NO auto-delete): warn if a prior draft exists.
  if [ -f "$PRIOR_JSON" ]; then
    PRIOR_ID=$(grep -m1 '"mediaId"' "$PRIOR_JSON" | sed -E 's/.*"mediaId": ?"([^"]+)".*/\1/')
    echo "  ⚠️ a prior WeChat draft exists for this slug (media_id=${PRIOR_ID:-?})."
    echo "     A NEW draft will be created — delete the old one manually in the WeChat console if unwanted."
  fi
  # 40164 pre-check: WeChat rejects API calls from non-whitelisted egress IPs.
  EGRESS=$(curl -s -m 5 https://api.ipify.org || echo "?")
  echo "[5/5] creating WeChat draft… (egress IP: $EGRESS — must be in the WeChat IP allowlist; 40164 = not whitelisted)"
  ( cd pipeline/m2 && node index.js "../../$MD_FILE" ${THEME:+--theme "$THEME"} 2>&1 | grep -E 'Draft created|Title:|❌|Error|40164' )
  # Record/update the consolidated slug→media_id map (non-destructive index).
  if [ -f "$PRIOR_JSON" ]; then
    python3 - "$SLUG" "$PRIOR_JSON" <<'PY'
import json, sys, os
slug, src = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(src))
except Exception:
    sys.exit(0)
p = "pipeline/m2/output/drafts-map.json"
m = json.load(open(p)) if os.path.exists(p) else {}
m[slug] = {"mediaId": d.get("mediaId"), "title": d.get("title"), "publishedAt": d.get("publishedAt")}
json.dump(m, open(p, "w"), ensure_ascii=False, indent=2)
mid = (d.get("mediaId") or "")[:16]
print(f"  ✓ recorded mapping: {slug} → {mid}…")
PY
  fi
else
  echo "[5/5] skipped WeChat (pass --wechat to enable)"
fi

echo "✅ done → https://$DOMAIN/blog/$SLUG/"
