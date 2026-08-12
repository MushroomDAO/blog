#!/usr/bin/env bash
# ============================================================================
# forage 每日采集 —— cron 每天 21:00 调用
#
#   0 21 * * * cd /Users/jason/Dev/mycelium/blog && \
#     ./.agents/skills/forage/run-daily.sh >> /tmp/forage-daily.log 2>&1
#
# 这个脚本只做**机械部分**：采集 → 三层去重 → 拉协议和 README → 装库。
#
# 它做不了的：写「核心增量」和「延展角度」——那是判断，需要 Claude 在会话里做。
# 所以早上你打开 8042 看到的条目，会标着「待判断」。跟我说一声我就补上。
# 与其让 cron 生成一堆空洞的套话，不如诚实地留空。
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/../../.."
export PATH="/Users/jason/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

SKILL=".agents/skills/forage"
echo "=== $(date '+%F %T') forage 每日采集 ==="

echo "[1/3] 采集各源…"
python3 "$SKILL/collect.py" || { echo "采集失败"; exit 1; }

echo "[2/3] 去重 + 限量 + 拉一手信息…"
python3 "$SKILL/stage.py" || { echo "入库失败"; exit 1; }

echo "[3/3] 确认服务在跑…"
if curl -s -m 3 http://127.0.0.1:8042/api/summary >/dev/null 2>&1; then
  echo "  ✓ 评审台已在 http://127.0.0.1:8042/"
else
  echo "  ⚠️ 评审台没起来，检查 LaunchAgent：launchctl list | grep forage"
fi

echo "✅ 完成 $(date '+%F %T')"
