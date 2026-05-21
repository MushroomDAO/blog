#!/usr/bin/env bash
# setup-cron.sh — 添加 source-scanner 定时任务（每小时扫描一次）
# 运行一次即可：bash scripts/setup-cron.sh

BLOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCAN_SCRIPT="$BLOG_DIR/scripts/scan-sources.sh"
CRON_ENTRY="0 * * * * PATH=/Users/jason/.local/bin:/usr/local/bin:/usr/bin:/bin $SCAN_SCRIPT >> /tmp/blog-source-scanner.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -qF "scan-sources.sh"; then
  echo "✅ Cron entry already exists:"
  crontab -l | grep scan-sources
  exit 0
fi

# 追加到现有 crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo "✅ Cron added (runs every hour on the hour):"
crontab -l | grep scan-sources
echo ""
echo "手动触发: bash $SCAN_SCRIPT"
echo "查看日志: tail -f /tmp/blog-source-scanner.log"
