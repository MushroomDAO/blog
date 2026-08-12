#!/usr/bin/env bash
# ============================================================================
# update-analytics.sh — refresh the /analytics fallback snapshot.
#
# /analytics 现在是实时的：页面加载时打 /api/analytics.json（Cloudflare Pages
# Function，见 functions/api/analytics.json.js），边缘缓存 3 分钟。
# 这个脚本已经不再是看板的数据来源，但仍然有两个不可替代的作用：
#
#   1. 兜底渲染 —— 实时接口挂掉/未配 token/访客禁用 JS 时，页面显示的就是
#      这份构建期快照。它越新，降级时越不难看。
#   2. 文章标题表 —— 边缘运行时读不到 src/content/blog/*.md，实时接口只能
#      回出 slug。页面靠构建期烤入的标题表把 slug 换回中英文标题。
#      **发了新文章后这份快照不更新，新文章在看板里就只会显示 slug。**
#
# 因此改为每天跑一次（原来是每 2 天）。crontab：
#   0 21 * * * cd /Users/jason/Dev/mycelium/blog && ./scripts/update-analytics.sh >> /tmp/blog-analytics-update.log 2>&1
#
# Manual run: bash scripts/update-analytics.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/Users/jason/Library/pnpm:/Users/jason/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# pnpm 是个 shell 脚本，跑起来需要 node，而 node 装在 nvm 里 —— cron 的
# 最小 PATH 两个都看不到。这条 cron 因此静默失败了三天：数据拉到了，
# 构建挂在 "pnpm: command not found"，于是不部署也不提交，看板一直是旧的。
# 不把版本号写死在 crontab 里，因为 node 一升级就又断了；这里动态解析，
# 取 nvm 下版本号最大的那个。
if ! command -v node >/dev/null 2>&1; then
  NODE_BIN=$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1)
  [ -n "$NODE_BIN" ] && export PATH="$NODE_BIN:$PATH"
fi
command -v pnpm >/dev/null 2>&1 || { echo "❌ 找不到 pnpm，中止（构建会失败）"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ 找不到 node，中止（pnpm 需要它）"; exit 1; }

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
