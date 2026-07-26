#!/usr/bin/env bash
# ============================================================================
# update-analytics.sh — refresh /analytics with the latest Cloudflare Web
# Analytics snapshot, rebuild, deploy, and commit the data file.
#
# Runs via cron every 2 days (see crontab entry added by this task):
#   0 9 */2 * * cd /Users/jason/Dev/mycelium/blog && ./scripts/update-analytics.sh >> /tmp/blog-analytics-update.log 2>&1
#
# Manual run: bash scripts/update-analytics.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/Users/jason/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "=== $(date) — updating blog analytics ==="

echo "[1/4] fetching latest Cloudflare Web Analytics snapshot…"
python3 pipeline/analytics/fetch-analytics.py

echo "[2/4] building site…"
pnpm build 2>&1 | tail -5

echo "[3/4] deploying to Cloudflare Pages (blog-mushroom)…"
CA="${NODE_EXTRA_CA_CERTS:-${CF_CA_CERT:-}}"
if [ -n "$CA" ] && [ -f "$CA" ]; then
  NODE_EXTRA_CA_CERTS="$CA" npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true 2>&1 | tail -4
else
  NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true 2>&1 | tail -4
fi

echo "[4/4] committing updated data snapshot…"
git add src/data/blog-analytics.json
if git diff --cached --quiet; then
  echo "  ✓ no data change to commit"
else
  git commit -m "chore(analytics): refresh traffic snapshot $(date +%Y-%m-%d)"
  echo "  ✓ committed"
fi

echo "✅ done → https://blog.mushroom.cv/analytics/"
