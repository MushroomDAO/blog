#!/usr/bin/env bash
# ============================================================================
# send-newsletter.sh — build the digest from newly published posts and send
# it as a listmonk campaign, every 2 days.
#
# Idempotency model:
#   - flock (mkdir-based) against overlapping runs of this script.
#   - A campaign we created but haven't yet confirmed "finished" is recorded
#     as pending_campaign_id/pending_slugs in last-sent.json BEFORE we flip
#     it to "running". If this run (or the poll below) can't confirm it
#     finished within the short poll window, we do NOT error out or retry —
#     we just exit 0 and leave it pending. The NEXT run checks for a pending
#     campaign FIRST, before ever building a new digest, so a slow send
#     (large list, listmonk backpressure, whatever) gets confirmed and its
#     slugs recorded on a later run instead of ever triggering a second,
#     duplicate campaign for the same posts.
#
# Scheduled via .github/workflows/newsletter.yml (GitHub Actions, every 2
# days at 14:00 UTC / 21:00 Asia-Bangkok) — not local crontab, so it doesn't
# depend on this machine being on. State (last-sent.json) is carried across
# scheduled runs via actions/cache; see that workflow file for the bootstrap
# mechanics and how to change the cadence or lookback window.
#
# Manual run (local, e.g. to check what would be sent): bash pipeline/newsletter/send-newsletter.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/../.."

# mkdir is atomic on every POSIX filesystem and needs no extra binary —
# flock isn't installed by default on macOS, which is where this actually runs.
LOCK_DIR="pipeline/newsletter/.send-newsletter.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another send-newsletter.sh run is already in progress — exiting" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT

if [ -f ~/Dev/.env ]; then
  # ~/Dev/.env has ~60 unrelated secrets across many other projects, isn't
  # valid bash throughout (some keys have hyphens, meant for a lenient
  # dotenv parser not `source`), and some values contain characters bash
  # would try to expand. Parse out just the 3 keys this script needs instead
  # of sourcing the whole file.
  eval "$(python3 <<'PYEOF'
import shlex
from pathlib import Path

keys = {"LISTMONK_API_URL", "LISTMONK_API_TOKEN", "LISTMONK_NEWSLETTER_LIST_UUID"}
env_path = Path.home() / "Dev" / ".env"
for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if "=" not in line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    k = k.strip()
    if k not in keys:
        continue
    v = v.strip().strip('"').strip("'")
    print(f"export {k}={shlex.quote(v)}")
PYEOF
)"
fi

: "${LISTMONK_API_URL:?LISTMONK_API_URL not set (see ~/Dev/.env)}"
: "${LISTMONK_API_TOKEN:?LISTMONK_API_TOKEN not set (see ~/Dev/.env)}"
: "${LISTMONK_NEWSLETTER_LIST_UUID:?LISTMONK_NEWSLETTER_LIST_UUID not set (see ~/Dev/.env)}"

STATE_FILE="pipeline/newsletter/last-sent.json"
DIGEST_HTML="pipeline/newsletter/digest-output.html"
MANIFEST_FILE="${DIGEST_HTML}.manifest.json"
AUTH_HEADER="Authorization: token ${LISTMONK_API_TOKEN}"

# curl wrapper: fails loudly on HTTP errors / hangs instead of silently
# treating an error page or a stalled connection as a normal response body.
lm_curl() {
  curl -sS --fail-with-body --connect-timeout 10 --max-time 60 "$@"
}

campaign_status() {
  lm_curl -H "$AUTH_HEADER" "${LISTMONK_API_URL}/api/campaigns/$1" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['status'])"
}

# Merge pending_slugs into sent_slugs, clear the pending fields, record the
# campaign id + timestamp. Used both when a freshly-created campaign confirms
# finished quickly, and when a run picks up a pending campaign from a
# previous run that has since finished.
finalize_sent() {
  local campaign_id="$1"
  CAMPAIGN_ID="$campaign_id" STATE_FILE="$STATE_FILE" python3 -c "
import datetime, json, os

state_path = os.environ['STATE_FILE']
data = json.load(open(state_path)) if os.path.exists(state_path) else {}
prev_slugs = set(data.get('sent_slugs', []))
pending_slugs = set(data.get('pending_slugs', []))

json.dump(
    {
        'last_sent_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'campaign_id': int(os.environ['CAMPAIGN_ID']),
        'sent_slugs': sorted(prev_slugs | pending_slugs),
    },
    open(state_path, 'w'),
)
"
}

echo "=== $(date) — checking for a pending campaign from a previous run ==="
PENDING_ID=$(python3 -c "
import json, os
p = '$STATE_FILE'
print(json.load(open(p)).get('pending_campaign_id', '') if os.path.exists(p) else '')
")

if [ -n "$PENDING_ID" ]; then
  echo "  found pending campaign ${PENDING_ID}, checking status…"
  STATUS=$(campaign_status "$PENDING_ID")
  case "$STATUS" in
    finished)
      echo "  ✓ pending campaign ${PENDING_ID} has finished — recording and clearing pending state"
      finalize_sent "$PENDING_ID"
      echo "  ✓ last-sent.json updated"
      exit 0
      ;;
    cancelled|paused)
      echo "  ! pending campaign ${PENDING_ID} is '${STATUS}' — needs manual attention (${LISTMONK_API_URL}/admin/campaigns/${PENDING_ID}); not clearing pending state or creating a new campaign automatically" >&2
      exit 1
      ;;
    *)
      echo "  pending campaign ${PENDING_ID} is still '${STATUS}' — will check again next run, NOT creating a new campaign for the same posts"
      exit 0
      ;;
  esac
fi

echo "=== building newsletter digest ==="

set +e
python3 pipeline/newsletter/build-digest.py --since-days "${SINCE_DAYS:-2}" --out "$DIGEST_HTML"
BUILD_STATUS=$?
set -e

if [ "$BUILD_STATUS" -eq 3 ]; then
  echo "  no new posts — skipping this cycle"
  exit 0
elif [ "$BUILD_STATUS" -ne 0 ]; then
  echo "  build-digest.py failed (exit $BUILD_STATUS)" >&2
  exit 1
fi

echo "[1/4] resolving list numeric ID for uuid ${LISTMONK_NEWSLETTER_LIST_UUID}…"
# export, not a per-command prefix — a `VAR=val cmd | other` prefix only scopes
# to `cmd`, the python3 process on the other side of the pipe wouldn't see it.
export LISTMONK_LIST_UUID="$LISTMONK_NEWSLETTER_LIST_UUID"
LIST_ID=$(lm_curl -H "$AUTH_HEADER" "${LISTMONK_API_URL}/api/lists?per_page=all" \
  | python3 -c "
import json, os, sys
data = json.load(sys.stdin)['data']['results']
uuid = os.environ['LISTMONK_LIST_UUID']
match = [l['id'] for l in data if l['uuid'] == uuid]
print(match[0] if match else '')
")
if [ -z "$LIST_ID" ]; then
  echo "  could not resolve list id for uuid ${LISTMONK_NEWSLETTER_LIST_UUID}" >&2
  exit 1
fi

echo "[2/4] creating campaign (list id ${LIST_ID})…"
CAMPAIGN_JSON=$(LM_ISSUE_NAME="Digest $(date +%Y-%m-%d)" \
  LM_SUBJECT="🍄 Mushroom Research Blog — 更新摘要 $(date +%Y-%m-%d)" \
  LM_LIST_ID="$LIST_ID" \
  LM_BODY_FILE="$DIGEST_HTML" \
  python3 -c "
import json, os
payload = {
    'name': os.environ['LM_ISSUE_NAME'],
    'subject': os.environ['LM_SUBJECT'],
    'lists': [int(os.environ['LM_LIST_ID'])],
    'content_type': 'html',
    'body': open(os.environ['LM_BODY_FILE']).read(),
    'template_id': 1,
    'type': 'regular',
    'messenger': 'email',
}
print(json.dumps(payload))
" | lm_curl -H "$AUTH_HEADER" -H "Content-Type: application/json" -X POST "${LISTMONK_API_URL}/api/campaigns" --data @-)

CAMPAIGN_ID=$(echo "$CAMPAIGN_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['id'])")
if [ -z "$CAMPAIGN_ID" ]; then
  echo "  campaign creation failed: $CAMPAIGN_JSON" >&2
  exit 1
fi

echo "[3/4] recording pending state (campaign ${CAMPAIGN_ID}) before triggering the send…"
# Written BEFORE flipping status to "running": if this process dies right
# after that PUT, or the send just takes longer than we poll below, the next
# run finds this pending_campaign_id and confirms/waits on it instead of
# building a fresh digest and creating a second campaign for the same posts.
CAMPAIGN_ID="$CAMPAIGN_ID" STATE_FILE="$STATE_FILE" MANIFEST_FILE="$MANIFEST_FILE" python3 -c "
import json, os

state_path = os.environ['STATE_FILE']
data = json.load(open(state_path)) if os.path.exists(state_path) else {}
manifest = json.load(open(os.environ['MANIFEST_FILE']))

data['pending_campaign_id'] = int(os.environ['CAMPAIGN_ID'])
data['pending_slugs'] = manifest['slugs']
json.dump(data, open(state_path, 'w'))
"

lm_curl -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -X PUT "${LISTMONK_API_URL}/api/campaigns/${CAMPAIGN_ID}/status" \
  --data '{"status":"running"}' > /dev/null

echo "[4/4] polling briefly for a fast finish…"
STATUS=""
for i in $(seq 1 10); do
  sleep 3
  STATUS=$(campaign_status "$CAMPAIGN_ID")
  if [ "$STATUS" = "finished" ]; then
    break
  fi
done

if [ "$STATUS" = "finished" ]; then
  finalize_sent "$CAMPAIGN_ID"
  echo "  ✓ campaign ${CAMPAIGN_ID} sent, last-sent.json updated"
else
  echo "  campaign ${CAMPAIGN_ID} still '${STATUS}' after the short poll — not an error, this is normal for a larger list. Left as pending_campaign_id in last-sent.json; the next run will confirm it and record its slugs instead of creating a new campaign for the same posts."
fi
