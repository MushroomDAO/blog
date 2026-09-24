#!/usr/bin/env bash
# 每周英文分发：机械筛选候选 → 拉起后台 Claude 会话判断并写草稿（不发帖）。
#   cron：每周一 21:40
#   手动：FORCE_RUN=1 ./.agents/skills/forage/distribute/run-weekly.sh
set -uo pipefail
cd "$(dirname "$0")/../../../.."
export PATH="/Users/jason/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

source ./scripts/require-owner.sh

WEEK=$(date +%G-W%V)
DIR="radar/distribution/$WEEK"
# README.md = 已出草稿；.started = 会话已拉起还在写（没有这个标记，任务跑的时候重跑会拉起第二个会话）
if [ "${FORCE_RUN:-}" != "1" ] && { [ -f "$DIR/README.md" ] || [ -f "$DIR/.started" ]; }; then
  echo "=== $(date '+%F %T') ${WEEK} 已经启动过或出过草稿，跳过。要重跑加 FORCE_RUN=1 ==="
  exit 0
fi

echo "=== $(date '+%F %T') 英文分发筛选 $WEEK ==="
python3 .agents/skills/forage/distribute/candidates.py
rc=$?
if [ $rc -eq 2 ]; then
  echo "本周没有符合条件的候选，结束。"
  exit 0
elif [ $rc -ne 0 ]; then
  echo "候选筛选失败"; exit 1
fi

CLAUDE=$(command -v claude || echo "$HOME/.local/bin/claude")
"$CLAUDE" --bg --permission-mode auto -n "distribute-${WEEK}" \
  "读 .agents/skills/forage/distribute/DISTRIBUTE-JOB.md 并严格按它执行：为 $WEEK 从候选里挑最多 2 篇写 HN/Reddit/dev.to 草稿，只写草稿不发帖，全程中文汇报。"
date '+%F %T' > "$DIR/.started"
echo "✅ 已拉起后台会话 distribute-${WEEK}，草稿会写到 $DIR/"
