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
  # 修正（round 2 review 抓到的阻塞 bug）：部署原来跟这个 if/else 平级，push 失败
  # 也照样执行——`--commit-dirty=true` 会把本地工作树直接怼上生产 main，跟远端任何
  # commit 都对不上。改成只在 push 真正成功时才部署，塞进这个分支里面。
  if git push 2>&1 | tail -2; then
    log "  ✓ 已推送，远端同步"

    # 修正（chore/manual-deploy-only 自审对抗式 review 抓到的真实问题）：这里 push
    # 过去之前一直是"免费搭便车"——GitHub Actions 的 deploy.yml 会被这次 push 顺带
    # 触发，生产也跟着更新了，这个脚本自己从来没有主动部署过。那条 CI 部署已经停用
    # （见 FU-14），如果这里只 push 不部署，会累积出跟 update-analytics.sh 同一类
    # 问题：commit 进了远端，生产却停在旧快照，没人主动去重新部署。
    log "顺带触发一次本地部署，避免生产停在推送前的旧快照…"

    # 修正（round 2 review 抓到的阻塞 bug）：这段是本 PR 全新加的路径，之前完全没有
    # 跟兄弟脚本 update-analytics.sh 一样的 PATH/nvm 处理——真实 cron 的 PATH
    # （crontab 里显式写死的那行）下 pnpm/npx/node/wrangler 全部 NOTFOUND，这段
    # 代码会 100% 跑不起来。跟 update-analytics.sh:29-32 抄同一段。
    if ! command -v node >/dev/null 2>&1; then
      NODE_BIN=$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1)
      [ -n "$NODE_BIN" ] && export PATH="$NODE_BIN:$PATH"
    fi

    if ! command -v pnpm >/dev/null 2>&1 || ! command -v node >/dev/null 2>&1; then
      log "  ⚠⚠⚠ 找不到 pnpm/node，跳过部署——没有 CI 兜底了，需要人工重跑 ./deploy.sh"
    else
      # 复用跟 update-analytics.sh 一样的读 token 方式（这里也是项目 .env，不是这个
      # 脚本本身用的 ~/Dev/.env——那份是 listmonk 凭据，跟 wrangler 部署用的是两回事）。
      # 去引号 + 去 CRLF（round 2 review 指出之前只去了引号，没去 \r——CRLF 的 .env
      # 会让 token 带一个看不见的尾随字符，Cloudflare 那边报一个看不懂的 400）。
      if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] && [ -f .env ]; then
        RAW_TOKEN="$(grep '^CLOUDFLARE_API_TOKEN=' .env | tail -1 | cut -d= -f2- || true)"
        RAW_TOKEN="${RAW_TOKEN%\"}"; RAW_TOKEN="${RAW_TOKEN#\"}"
        RAW_TOKEN="${RAW_TOKEN%\'}"; RAW_TOKEN="${RAW_TOKEN#\'}"
        RAW_TOKEN="$(printf '%s' "$RAW_TOKEN" | tr -d '\r')"
        [ -n "$RAW_TOKEN" ] && export CLOUDFLARE_API_TOKEN="$RAW_TOKEN"
      fi

      # 部署用的分支名跟着 git 的当前分支走，不写死 main——写死的话在非 main 分支
      # （比如 dailyblog）上跑这个 cron，会把那个分支的内容当成 main 的生产部署发出去
      # （round 2 review 指出的问题）。
      DEPLOY_BRANCH="$(git branch --show-current 2>/dev/null || echo main)"

      # 跟 scripts/publish-blog.sh / update-analytics.sh 一样的 CA 优先、TLS bypass
      # 兜底写法（见 .agents/skills/blog-publisher/SKILL.md「token + TLS workaround
      # required in this environment」）——不是要去掉它，是保持跟其他部署入口一致。
      # 最佳努力：部署失败不影响这个脚本继续走后面发 newsletter 的正事，只是响亮地
      # 警告，且不再吞掉 build 的报错输出（原来 >/dev/null 2>&1 会把
      # "command not found" 一起吞掉，日志里只剩一行看不出原因的警告）。
      log "  安装依赖…"
      DEPLOY_OK=1
      pnpm install 2>&1 | tail -3 || DEPLOY_OK=0
      if [ "$DEPLOY_OK" = 1 ]; then
        log "  构建…"
        pnpm build 2>&1 | tail -5 || DEPLOY_OK=0
      fi
      if [ "$DEPLOY_OK" = 1 ]; then
        CA="${NODE_EXTRA_CA_CERTS:-${CF_CA_CERT:-}}"
        if [ -n "$CA" ] && [ -f "$CA" ]; then
          NODE_EXTRA_CA_CERTS="$CA" npx wrangler pages deploy dist \
            --project-name=blog-mushroom --branch="$DEPLOY_BRANCH" --commit-dirty=true 2>&1 | tail -4 || DEPLOY_OK=0
        else
          NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist \
            --project-name=blog-mushroom --branch="$DEPLOY_BRANCH" --commit-dirty=true 2>&1 | tail -4 || DEPLOY_OK=0
        fi
      fi
      if [ "$DEPLOY_OK" = 1 ]; then
        log "  ✓ 部署完成"
      else
        log "  ⚠⚠⚠ 部署失败——没有 CI 兜底了，生产会停在推送前的旧快照，需要人工重跑 ./deploy.sh"
      fi
    fi
  else
    log "  ❌ push 失败，跳过部署（本地工作树不应该在没有对应远端 commit 的情况下推上生产）"
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
  log "✅ ${SKIP_WINDOW_HOURS}h 内已有 campaign，跳过（不判断是 Actions 还是人工发的——结果一样）"
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
