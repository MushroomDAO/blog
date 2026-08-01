#!/usr/bin/env bash
# ============================================================================
# send-newsletter.sh — build the digest from newly published posts and send
# it as a listmonk campaign, every 2 days. Skips cleanly (exit 0) if there's
# nothing new. Only updates last-sent.json after listmonk confirms the send
# actually finished, so a failed run is safe to retry without duplicating or
# dropping an issue. flock'd so an overlapping cron run can't double-send.
#
# Cron (every 2 days at 21:00, same slot as update-analytics.sh):
#   0 21 */2 * * cd /Users/jason/Dev/mycelium/blog && ./pipeline/newsletter/send-newsletter.sh >> /tmp/blog-newsletter.log 2>&1
#
# Manual run: bash pipeline/newsletter/send-newsletter.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/../.."

LOCK_FILE="pipeline/newsletter/.send-newsletter.lock"
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  echo "another send-newsletter.sh run is already in progress — exiting" >&2
  exit 0
fi

if [ -f ~/Dev/.env ]; then
  set -a
  source ~/Dev/.env
  set +a
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

echo "=== $(date) — building newsletter digest ==="

set +e
python3 pipeline/newsletter/build-digest.py --out "$DIGEST_HTML"
BUILD_STATUS=$?
set -e

if [ "$BUILD_STATUS" -eq 3 ]; then
  echo "  no new posts — skipping this cycle"
  exit 0
elif [ "$BUILD_STATUS" -ne 0 ]; then
  echo "  build-digest.py failed (exit $BUILD_STATUS)" >&2
  exit 1
fi

echo "[1/3] resolving list numeric ID for uuid ${LISTMONK_NEWSLETTER_LIST_UUID}…"
LIST_ID=$(LISTMONK_LIST_UUID="$LISTMONK_NEWSLETTER_LIST_UUID" lm_curl -H "$AUTH_HEADER" "${LISTMONK_API_URL}/api/lists?per_page=all" \
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

echo "[2/3] creating + sending campaign (list id ${LIST_ID})…"
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

lm_curl -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -X PUT "${LISTMONK_API_URL}/api/campaigns/${CAMPAIGN_ID}/status" \
  --data '{"status":"running"}' > /dev/null

echo "[3/3] verifying send finished…"
STATUS=""
for i in $(seq 1 10); do
  sleep 3
  STATUS=$(lm_curl -H "$AUTH_HEADER" "${LISTMONK_API_URL}/api/campaigns/${CAMPAIGN_ID}" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['status'])")
  if [ "$STATUS" = "finished" ]; then
    break
  fi
done

if [ "$STATUS" != "finished" ]; then
  echo "  campaign ${CAMPAIGN_ID} did not reach 'finished' (last status: ${STATUS}) — NOT updating last-sent.json, will retry next cycle" >&2
  echo "  (if the campaign is just slow — large list — check ${LISTMONK_API_URL}/admin/campaigns/${CAMPAIGN_ID} manually before rerunning, to avoid a duplicate send)" >&2
  exit 1
fi

CAMPAIGN_ID="$CAMPAIGN_ID" STATE_FILE="$STATE_FILE" MANIFEST_FILE="$MANIFEST_FILE" python3 -c "
import datetime, json, os

manifest_path = os.environ['MANIFEST_FILE']
new_slugs = set(json.load(open(manifest_path))['slugs']) if os.path.exists(manifest_path) else set()

state_path = os.environ['STATE_FILE']
prev_slugs = set(json.load(open(state_path)).get('sent_slugs', [])) if os.path.exists(state_path) else set()

json.dump(
    {
        'last_sent_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'campaign_id': int(os.environ['CAMPAIGN_ID']),
        'sent_slugs': sorted(prev_slugs | new_slugs),
    },
    open(state_path, 'w'),
)
"

echo "  ✓ campaign ${CAMPAIGN_ID} sent, last-sent.json updated"
