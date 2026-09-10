#!/usr/bin/env bash
# ============================================================================
# sync-memory.sh — 项目记忆在「私有记忆库」和「Claude Code 本机目录」之间双向对齐
# ----------------------------------------------------------------------------
# Claude Code 把项目记忆写在 ~/.claude/projects/<repo-path-encoded>/memory/，
# 那个位置不跟仓库走。两台机器要共享记忆，就得让它跟着某个 git 仓库走。
#
# 为什么是**私有**仓库（MushroomDAO/blog-memory）而不是 blog 本身：
# blog 是公开仓库。记忆文件里没有任何密钥值，但含 AWS 账号 ID、IAM 用户名、
# 私人邮箱、主密钥文件路径与完整变量名索引 —— 单条都不是凭据，
# 打包公开就是一份现成的踩点材料。
#
# 为什么不用软链接：Claude Code 会在那个目录里增删文件，软链接一旦失效是
# **静默**的 —— 记忆会安静地写到别处，等你发现已经丢了一批。
# 用 rsync 按修改时间新的赢，两边都能改，冲突面小且可见。
#
# 用法：
#   scripts/sync-memory.sh          # 拉取 → 双向对齐 → 提交并推回私有库
#   scripts/sync-memory.sh --dry    # 只看会动什么，不改不提交
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"
LOCAL="$HOME/.claude/projects/$(echo "$REPO" | sed 's#/#-#g')/memory"
VAULT="$REPO/.agents/memory"

DRY=""
[ "${1:-}" = "--dry" ] && DRY="--dry-run"

if [ ! -d "$VAULT/.git" ]; then
  echo "❌ .agents/memory 不是一个 git clone。先跑：scripts/bootstrap-machine.sh" >&2
  exit 1
fi

mkdir -p "$LOCAL"
echo "本机  : $LOCAL"
echo "记忆库: $VAULT  ($(git -C "$VAULT" remote get-url origin 2>/dev/null))"
echo

# 先拉，免得本机的旧文件把另一台机器刚写的新内容盖掉
if [ -z "$DRY" ]; then
  echo "→ 拉取远端"
  git -C "$VAULT" pull --ff-only -q || echo "  ⚠️ pull 失败（可能有本地未推送的改动），继续对齐"
fi

# MEMORY.md 必须先单独合并成并集再进 rsync。它是**两边都会追加**的索引文件，
# 按「新的赢」整文件覆盖会静默抹掉另一台新加的索引行（Mac mini 上就有 4 条）。
if [ -f "$LOCAL/MEMORY.md" ] && [ -f "$VAULT/MEMORY.md" ]; then
  echo "→ 合并 MEMORY.md 索引（取并集）"
  if [ -n "$DRY" ]; then
    echo "  （--dry，跳过合并）"
  else
    python3 scripts/merge-memory-index.py "$LOCAL/MEMORY.md" "$VAULT/MEMORY.md" | sed 's/^/  /'
  fi
fi

# 其余每个文件各是一条记忆，通常只有一台机器在改，「修改时间新的赢」是对的。
# -u = 只在源文件更新时才覆盖。两个方向各跑一次 = 两边都拿到对方的新东西。
echo "→ 本机 → 记忆库"
rsync -a -u $DRY --itemize-changes --exclude='README.md' --include='*.md' --exclude='*' "$LOCAL/" "$VAULT/"
echo "→ 记忆库 → 本机"
rsync -a -u $DRY --itemize-changes --exclude='README.md' --include='*.md' --exclude='*' "$VAULT/" "$LOCAL/"

echo
if [ -n "$DRY" ]; then
  echo "（--dry，什么都没改）"
  exit 0
fi

echo "对齐完成：记忆库 $(ls "$VAULT"/*.md 2>/dev/null | wc -l | tr -d ' ') 个 / 本机 $(ls "$LOCAL"/*.md 2>/dev/null | wc -l | tr -d ' ') 个"

# 自动提交并推回去 —— 靠人记得提交，迟早会漏，另一台机器就读不到
if [ -n "$(git -C "$VAULT" status --porcelain)" ]; then
  git -C "$VAULT" add -A
  git -C "$VAULT" commit -q -m "chore(memory): sync from $(scutil --get LocalHostName 2>/dev/null || hostname -s) $(date '+%F %H:%M')"
  if git -C "$VAULT" push -q 2>/dev/null; then
    echo "✅ 已提交并推送到私有记忆库"
  else
    echo "⚠️ 已提交但推送失败 —— 手动跑：git -C .agents/memory push"
  fi
else
  echo "✅ 记忆库无变更，无需提交"
fi
