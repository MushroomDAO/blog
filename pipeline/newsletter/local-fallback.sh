#!/usr/bin/env bash
# ============================================================================
# local-fallback.sh — 本地兜底发送，只在 GitHub Actions 没发成时才动手。
#
#   30 21 * * * cd /Users/jason/Dev/mycelium/blog && \
#     ./pipeline/newsletter/local-fallback.sh >> /tmp/newsletter-local.log 2>&1
#
# 为什么判据是 listmonk 而不是本地文件：
#   send-newsletter.sh 用 last-sent.json 去重，但 Actions 把那个文件存在
#   actions/cache 里，本地存在磁盘上——**两套独立状态，互相看不见**。
#   本地那份长期停在旧时间戳，直接跑会把 Actions 早发过的又发一遍。
#   listmonk 的 campaign 列表是两条路径共同写入的唯一真相源，所以用它。
#
# 跑之前还会把本地 last-sent.json 的时间戳对齐到 listmonk 上最后一个
# finished campaign，避免补发已经发过的内容。
#
# 凭证在 ~/Dev/.env（不是项目 .env）。那个文件有非法 bash 语法，
# `source` 会静默失败并把变量置空，所以这里逐行取值。
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/../.."

ENV_FILE="$HOME/Dev/.env"
LOCK_DIR="/tmp/newsletter-local.lock"
SKIP_WINDOW_HOURS=20   # 这么多小时内已有 campaign 就认为 Actions 发过了

log() { echo "[$(date '+%F %T')] $*"; }

getv() {
  grep -m1 "^$1=" "$ENV_FILE" 2>/dev/null | sed "s/^$1=//" | sed 's/^"//;s/"$//' | tr -d '\r'
}

# mkdir 是原子操作，macOS 没有 flock
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  log "另一个实例在跑，退出"; exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT

LISTMONK_API_URL="$(getv LISTMONK_API_URL)"
LISTMONK_API_TOKEN="$(getv LISTMONK_API_TOKEN)"
LISTMONK_NEWSLETTER_LIST_UUID="$(getv LISTMONK_NEWSLETTER_LIST_UUID)"
export LISTMONK_API_URL LISTMONK_API_TOKEN LISTMONK_NEWSLETTER_LIST_UUID

if [ -z "$LISTMONK_API_URL" ] || [ -z "$LISTMONK_API_TOKEN" ]; then
  log "❌ 取不到 listmonk 凭证（$ENV_FILE），放弃"; exit 1
fi

log "=== 本地兜底检查 ==="

# 未推送的提交 = Actions 看不到的文章。这正是订阅断更 5 天的原因：
# 本地攒了 66 个提交没推，Actions 从 GitHub 检出的是一周前的快照，
# 于是连续四次判定「没有新文章」。这里每天自愈一次。
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
if [ "$AHEAD" -gt 0 ]; then
  log "⚠️ 本地领先远端 ${AHEAD} 个提交 —— Actions 看不到这些文章，先推送"
  if git push 2>&1 | tail -2; then
    log "  ✓ 已推送，远端同步"
  else
    log "  ❌ push 失败，Actions 仍会看到旧快照"
  fi
fi

# listmonk 跑在 Fly.io 上，空闲会缩到零。cron 每天只跑一次，所以**每次都是冷的**，
# 第一个请求要等实例拉起。原来 30s 超时正好卡在冷启动上，实测直接失败。
# 先用 /health 唤醒（便宜、无需鉴权），再取数据，两步都给足重试。
log "唤醒 listmonk（Fly 冷启动可能要几十秒）…"
for i in 1 2 3; do
  code=$(curl -sS -m 60 -o /dev/null -w '%{http_code}' "$LISTMONK_API_URL/health" 2>/dev/null)
  [ "$code" = "200" ] && { log "  ✓ 已就绪（第 $i 次）"; break; }
  log "  第 $i 次未就绪（HTTP ${code:-无响应}），重试"
  sleep 5
done

CAMPAIGNS=""
for i in 1 2 3; do
  CAMPAIGNS=$(curl -sS -m 60 -H "Authorization: token $LISTMONK_API_TOKEN" \
    "$LISTMONK_API_URL/api/campaigns?per_page=10&order_by=created_at&order=DESC" 2>/dev/null)
  [ -n "$CAMPAIGNS" ] && break
  log "  取 campaign 列表第 $i 次失败，重试"
  sleep 5
done

if [ -z "$CAMPAIGNS" ]; then
  log "❌ listmonk 三次都无响应，放弃（宁可不发也不要在状态不明时发）"; exit 1
fi

DECISION=$(printf '%s' "$CAMPAIGNS" | python3 -c "
import json, sys, datetime
d = json.load(sys.stdin)
rs = (d.get('data') or {}).get('results') or []
now = datetime.datetime.now(datetime.timezone.utc)
newest_finished = None
recent = False
for c in rs:
    ts = c['created_at']
    try:
        t = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        continue
    age_h = (now - t).total_seconds() / 3600
    if age_h < $SKIP_WINDOW_HOURS and c['status'] in ('running', 'finished', 'scheduled'):
        recent = True
    if c['status'] == 'finished' and newest_finished is None:
        newest_finished = t.isoformat()
print(('SKIP' if recent else 'SEND') + '|' + (newest_finished or ''))
" 2>/dev/null)

ACTION="${DECISION%%|*}"
NEWEST="${DECISION#*|}"

if [ "$ACTION" = "SKIP" ]; then
  log "✅ ${SKIP_WINDOW_HOURS}h 内已有 campaign（Actions 已处理），本地不重复发送"
  exit 0
fi

log "⚠️ ${SKIP_WINDOW_HOURS}h 内没有 campaign —— Actions 可能没跑成，本地接手"

# 把本地状态对齐到 listmonk 的真实进度，否则会补发已发过的
if [ -n "$NEWEST" ]; then
  python3 - "$NEWEST" <<'PY'
import json, os, sys
p = "pipeline/newsletter/last-sent.json"
newest = sys.argv[1]
try:
    st = json.load(open(p))
except Exception:
    st = {}
old = st.get("last_sent_at", "(无)")
if old < newest:
    st["last_sent_at"] = newest
    json.dump(st, open(p, "w"))
    print(f"  本地状态 {old} → {newest}（对齐 listmonk）")
else:
    print(f"  本地状态 {old} 已不落后于 listmonk，不动")
PY
fi

log "开始本地发送…"
bash pipeline/newsletter/send-newsletter.sh
rc=$?
log "send-newsletter.sh 退出码 $rc"
exit $rc
