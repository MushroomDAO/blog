#!/bin/bash
# run-daily.sh「当天已采集过就让路」守卫的测试。不联网、不碰真实 radar/。
#
#   bash .agents/skills/forage/test_run_daily_guard.sh
#
# 做法：把 run-daily.sh 拷进临时目录，采集/入库/对账/健康检查换成 echo，
# 用 cron 的最小环境（env -i，没有 LANG）跑四种情况；跳过分支再在 UTF-8 locale 下跑一次
# （macOS 的 bash 3.2 在 UTF-8 下会把紧跟变量名的全角括号当成变量名的一部分）。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/.agents/skills/forage" "$T/scripts" "$T/config" "$T/radar"
cp "$REPO/scripts/require-owner.sh" "$T/scripts/"
# owner 写成本机，不依赖真实 runner.json 归谁
printf '{"owner": "%s"}\n' "$(scutil --get LocalHostName 2>/dev/null || hostname -s)" > "$T/config/runner.json"
sed -e 's#^python3 .*collect.py.*#echo STUB_COLLECT#' \
    -e 's#^python3 .*stage.py.*#echo STUB_STAGE#' \
    -e 's#^python3 .*store.py" sync.*#echo STUB_SYNC#' \
    -e 's#^if curl .*#if true; then#' \
    "$HERE/run-daily.sh" > "$T/.agents/skills/forage/run-daily.sh"
chmod +x "$T/.agents/skills/forage/run-daily.sh"

fail=0
run() { env -i HOME="$HOME" PATH=/usr/bin:/bin "$@" "$T/.agents/skills/forage/run-daily.sh" 2>&1; }
check() {  # check <名称> <输出> <应出现的串> <不应出现的串>
  if [[ "$2" == *"$3"* && "$2" != *"$4"* ]]; then echo "ok   $1"; else echo "FAIL $1"; echo "$2" | sed 's/^/     /'; fail=1; fi
}
today=$(date +%F)

rm -f "$T/radar/.last-run"
out=$(run); check "no_marker_runs_and_writes_marker" "$out" STUB_COLLECT "今天已经采集过"
[ "$(cat "$T/radar/.last-run" 2>/dev/null)" = "$today" ] && echo "ok   marker_written_after_success" || { echo "FAIL marker_written_after_success"; fail=1; }

out=$(run); check "marker_today_skips" "$out" "今天已经采集过" STUB_COLLECT
check "skip_message_no_unbound_variable" "$out" "radar/.last-run" "unbound"
out=$(run LANG=en_US.UTF-8); check "skip_ok_under_utf8_locale" "$out" "今天已经采集过" "unbound"

out=$(run FORCE_RUN=1); check "force_run_overrides_marker" "$out" STUB_COLLECT "今天已经采集过"

echo 2000-01-01 > "$T/radar/.last-run"
out=$(run); check "stale_marker_runs" "$out" STUB_COLLECT "今天已经采集过"

exit $fail
