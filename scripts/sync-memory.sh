#!/usr/bin/env bash
# ============================================================================
# sync-memory.sh — 项目记忆在「仓库」和「Claude Code 本机目录」之间双向对齐
# ----------------------------------------------------------------------------
# Claude Code 把项目记忆写在 ~/.claude/projects/<repo-path-encoded>/memory/，
# 那个位置不跟仓库走。两台机器要共享记忆，就得让它跟着 git 走一份。
#
# 这里不用软链接：Claude Code 会在那个目录里增删文件，软链接一旦出问题
# （目录被重建、权限变化）是静默失败，记忆会安静地写到别处去。
# 用 rsync 按修改时间新的赢，两边都能改，冲突面小且可见。
#
# 用法：
#   scripts/sync-memory.sh          # 双向对齐（新的赢）
#   scripts/sync-memory.sh --dry    # 只看会动什么
#
# 对齐完记得 commit .agents/memory/ —— 不提交的话另一台机器还是读不到。
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"
LOCAL="$HOME/.claude/projects/$(echo "$REPO" | sed 's#/#-#g')/memory"
VAULT="$REPO/.agents/memory"

DRY=""
[ "${1:-}" = "--dry" ] && DRY="--dry-run"

mkdir -p "$VAULT" "$LOCAL"

echo "本机: $LOCAL"
echo "仓库: $VAULT"
echo

# -u = 只在源文件更新时才覆盖。两个方向各跑一次 = 两边都拿到对方的新东西。
echo "→ 本机 → 仓库"
rsync -a -u $DRY --itemize-changes --include='*.md' --exclude='*' "$LOCAL/" "$VAULT/"
echo "→ 仓库 → 本机"
rsync -a -u $DRY --itemize-changes --include='*.md' --exclude='*' "$VAULT/" "$LOCAL/"

echo
if [ -n "$DRY" ]; then
  echo "（--dry，什么都没改）"
else
  echo "对齐完成：仓库 $(ls "$VAULT" | wc -l | tr -d ' ') 个 / 本机 $(ls "$LOCAL" | wc -l | tr -d ' ') 个"
  if ! git diff --quiet -- .agents/memory 2>/dev/null || [ -n "$(git ls-files -o --exclude-standard .agents/memory)" ]; then
    echo "⚠️  .agents/memory 有变更，记得提交："
    echo "   git add .agents/memory && git commit -m 'chore(memory): sync' && git push"
  fi
fi
