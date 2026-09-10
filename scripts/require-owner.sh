#!/usr/bin/env bash
# ============================================================================
# require-owner.sh — 有副作用的定时任务的准入闸门
# ----------------------------------------------------------------------------
# 为什么需要它：仓库现在会被克隆到第二台机器（Mac mini）上做 24/7 自动运行。
# 如果两台机器都装了同一份 cron，21:10 会同时采集、21:30 会同时给订阅者发信 ——
# 订阅者收到两封一样的邮件，雷达把同一批线索采两遍。这类错误不会报错，
# 只会安静地发生，所以必须在脚本入口挡住，而不是靠人记得只装一台。
#
# 判据：config/runner.json 的 owner 字段 == 本机 LocalHostName。
#
# 用法（在被守护脚本靠前的位置）：
#     source "$(dirname "$0")/../../scripts/require-owner.sh"   # 路径按调用方调整
#
# 手动跑不受影响：设 FORCE_RUN=1 即可越过（人在终端前，知道自己在干什么）。
# ============================================================================

_ro_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
_ro_cfg="$_ro_repo/config/runner.json"

# 拿不到配置就放行 —— 闸门本身不该成为新的故障点。
if [ ! -f "$_ro_cfg" ]; then
  echo "[require-owner] 找不到 config/runner.json，跳过归属检查。" >&2
  return 0 2>/dev/null || exit 0
fi

if [ "${FORCE_RUN:-}" = "1" ]; then
  echo "[require-owner] FORCE_RUN=1，跳过归属检查（手动运行）。"
  return 0 2>/dev/null || exit 0
fi

_ro_owner=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('owner',''))" "$_ro_cfg" 2>/dev/null || echo "")
_ro_host=$(scutil --get LocalHostName 2>/dev/null || hostname -s 2>/dev/null || hostname)

if [ -z "$_ro_owner" ]; then
  echo "[require-owner] ❌ runner.json 里没有 owner —— 还没有机器认领 24/7 运行权。" >&2
  echo "               在要接管的那台机器上跑：scripts/bootstrap-machine.sh --claim-owner" >&2
  echo "               然后 commit + push config/runner.json。" >&2
  exit 78   # EX_CONFIG
fi

if [ "$_ro_owner" != "$_ro_host" ]; then
  echo "[require-owner] ⏭  本机是 ${_ro_host}，运行权归 ${_ro_owner} —— 跳过，不执行。"
  echo "               这是正常的：非 owner 机器上的定时任务应该静默让路。"
  echo "               手动要跑就加 FORCE_RUN=1。"
  exit 0
fi
