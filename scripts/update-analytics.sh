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

# .env 里存着真实密钥，之前发现是 644（其他本机账号都能读），这里每次跑都顺手收紧一次，
# 不指望"设置一次就永远不漂移"。修正（round 2 review 指出）：这段挪到读 token 之前——
# 顺序上，"先把文件权限收紧"应该先于"再去读里面的内容"，虽然同一次脚本执行内先后
# 顺序对这次读取本身没有影响，但让"权限收紧"不依赖后面的读取分支是否执行到。
if [ -f .env ]; then
  chmod 600 .env 2>/dev/null || true
fi

# cron 的非交互 shell 不会 source 任何 profile/dotenv，2026-08-13 那次本地部署失败
# （"CLOUDFLARE_API_TOKEN 不存在"）根源就是这个，当时靠 GitHub Actions 的自动部署兜底。
# 那条 CI 部署已经停用（见 docs/agent/followups.md FU-14、.github/workflows/test.yml
# 的说明——那个 secret 本身就不可靠，停用它是因为它，不是想连带丢掉这条兜底），所以
# 这里改成直接从项目 .env 读 token，把根因修掉，不再依赖外部兜底。
#
# 修正（自审对抗式 review 抓到的真实 bug）：`.env` 存在但没有 CLOUDFLARE_API_TOKEN=
# 这一行时，grep 找不到匹配退出码是 1；这行在 `if` 的 then 块里（不是 if 条件本身，
# 那个天然免疫 errexit），`set -euo pipefail` 会让整个脚本在这里静默退出——连
# [1/4] 抓取数据都不会跑，cron 日志里什么线索都没有，比"只是部署失败"严重得多。
# `|| true` 让这一步永远成功，把"取不到 token"和"取到了"两种情况都留到下面
# display 显式判断，不再让 grep 的退出码传染给整个脚本。
# 顺带去掉可能存在的引号（"..."/'...'）和 CRLF 的尾随 \r（round 2 review 指出：这个
# 仓库自己的 local-fallback.sh 里 getv() 结尾就有 `tr -d '\r'`，这里最初漏了——CRLF
# 的 .env 会让 token 带一个看不见的尾随字符，Cloudflare 那边只会报一个看不懂的 400）。
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] && [ -f .env ]; then
  RAW_TOKEN="$(grep '^CLOUDFLARE_API_TOKEN=' .env | tail -1 | cut -d= -f2- || true)"
  RAW_TOKEN="${RAW_TOKEN%\"}"; RAW_TOKEN="${RAW_TOKEN#\"}"
  RAW_TOKEN="${RAW_TOKEN%\'}"; RAW_TOKEN="${RAW_TOKEN#\'}"
  RAW_TOKEN="$(printf '%s' "$RAW_TOKEN" | tr -d '\r')"
  if [ -n "$RAW_TOKEN" ]; then
    CLOUDFLARE_API_TOKEN="$RAW_TOKEN"
    export CLOUDFLARE_API_TOKEN
  else
    echo "  ⚠ .env 里没有 CLOUDFLARE_API_TOKEN，本地部署大概率会失败（见 [4/4]）"
  fi
fi

# 同一套读法取 CLOUDFLARE_ACCOUNT_ID（round 2 review 指出：这个脚本之前只手动摘取
# CLOUDFLARE_API_TOKEN 一个变量，不整体 source .env，注释却写"权威值是 .env"——
# 这句话是反的，字面量才是当时实际生效的值。现在真正从 .env 读，让那句话变成真的）。
if [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ] && [ -f .env ]; then
  RAW_ACCOUNT_ID="$(grep '^CLOUDFLARE_ACCOUNT_ID=' .env | tail -1 | cut -d= -f2- || true)"
  RAW_ACCOUNT_ID="${RAW_ACCOUNT_ID%\"}"; RAW_ACCOUNT_ID="${RAW_ACCOUNT_ID#\"}"
  RAW_ACCOUNT_ID="${RAW_ACCOUNT_ID%\'}"; RAW_ACCOUNT_ID="${RAW_ACCOUNT_ID#\'}"
  RAW_ACCOUNT_ID="$(printf '%s' "$RAW_ACCOUNT_ID" | tr -d '\r')"
  if [ -n "$RAW_ACCOUNT_ID" ]; then
    CLOUDFLARE_ACCOUNT_ID="$RAW_ACCOUNT_ID"
    export CLOUDFLARE_ACCOUNT_ID
  fi
fi

echo "=== $(date) — updating blog analytics ==="

echo "[1/4] fetching latest Cloudflare Web Analytics snapshot…"
python3 pipeline/analytics/fetch-analytics.py

echo "[2/4] building site…"
pnpm build 2>&1 | tail -5

# commit + push 放在本地直接部署之前：即使下一步的本地部署失败，数据快照至少已经
# 进了 git 历史，不会丢，下一次成功的部署（下次 cron、或者手动跑一次 deploy.sh）会
# 把它带上线——但不会有人自动帮忙重试，见下面部署失败时的提示。
echo "[3/4] committing + pushing updated data snapshot…"
git add src/data/blog-analytics.json
if git diff --cached --quiet; then
  echo "  ✓ no data change to commit"
else
  git commit -m "chore(analytics): refresh traffic snapshot $(date +%Y-%m-%d)"
  # 修正（round 2 review 用真实 cron 日志证实的问题）：这条仓库 non-fast-forward
  # push 被拒是常态（#54 自己的 commit message 就这么写），而这行在 `else` 分支里，
  # 不是 if 条件本身，不天然免疫 set -e——真实日志显示脚本正是在这一行因为 push
  # 被拒而整个退出，从没走到过 [4/4] 的部署步骤。加 || 让 push 失败不再杀死脚本，
  # 继续往下走本地部署（本地构建产物不依赖这次 push 是否成功）。
  git push origin main || echo "  ⚠ push 被拒(non-fast-forward)——继续用本地构建部署"
  echo "  ✓ committed（push 结果见上）"
fi

# 本地部署失败不让整个脚本报错退出——数据已经 push 过了，不算致命，但现在没有 CI
# 兜底了，失败了就是真的失败，线上会一直卡在旧快照直到下一次成功部署，所以下面的
# 警告要显眼，不能只是安慰性的"不是致命错误"。
# set -e 在这条命令上先关掉，读完退出码再手动判断，避免非零码触发 errexit。
echo "[4/4] deploying to Cloudflare Pages (blog-mushroom)…"
set +e
CA="${NODE_EXTRA_CA_CERTS:-${CF_CA_CERT:-}}"
# account_id 不能写进 wrangler.toml——Pages 项目的配置 schema 不接受这个顶层
# 字段（`npx wrangler@4 pages deploy` 实测直接报 "Configuration file for Pages
# projects does not support 'account_id'"，连网络请求都不发）。这行由 #54 引入、
# main 上的 c6ec09b 已经删掉。（round 2 review 指出：不要断言这条 cron 曾经因为
# 它失败过——真实日志显示这条 cron 自 #54 合并起还没跑过一次，唯一一次记录到的
# 失败是上面 [3/4] 的 push non-fast-forward，从没走到过这一步，DEPLOY_STATUS
# 从未被求值过。这里只是把这个真实存在、可复现的 schema 限制记下来，防止以后
# 又有人往 wrangler.toml 里加回这一行。）改成按 wrangler 实际支持的方式，部署前
# 导出环境变量；CLOUDFLARE_ACCOUNT_ID 现在真的从 .env 读（见上面新增的读取块），
# 这里的字面量只是 .env 缺这一项时的兜底。
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-7bf23342f21baa5ebfc7bc7b74f5a1f2}"
if [ -n "$CA" ] && [ -f "$CA" ]; then
  NODE_EXTRA_CA_CERTS="$CA" npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true 2>&1 | tail -4
else
  NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true 2>&1 | tail -4
fi
DEPLOY_STATUS=${PIPESTATUS[0]}
set -e
if [ "$DEPLOY_STATUS" -ne 0 ]; then
  echo "  ⚠⚠⚠ 本地部署失败(退出码 $DEPLOY_STATUS)——没有 CI 兜底了，线上快照会一直是旧的，需要人工重跑一次 ./deploy.sh 或本脚本"
  # 修正（round 2 review 指出的真实问题）：这条 cron 靠退出码给 crontab 的邮件/
  # 监控当唯一的失败信号，之前不管部署成不成功最后都印"✅ done"、退出码恒为 0——
  # 部署失败本该能被外部监控发现，这样"发现"这一步本身也悄悄失效了。
  exit 1
fi

echo "✅ done → https://blog.mushroom.cv/analytics/"
