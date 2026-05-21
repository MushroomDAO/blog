#!/usr/bin/env bash
# scan-sources.sh — 扫描 source/ 目录，发现新内容后调用 source-scanner skill 自动发布
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_DIR="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$BLOG_DIR/source"
LOG_FILE="$SOURCE_DIR/.scan.log"
CLAUDE_BIN="${CLAUDE_BIN:-/Users/jason/.local/bin/claude}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Source scan started ==="

[ -d "$SOURCE_DIR" ] || { log "ERROR: source/ directory not found at $SOURCE_DIR"; exit 1; }
[ -x "$CLAUDE_BIN" ] || { log "ERROR: claude CLI not found at $CLAUDE_BIN"; exit 1; }

FOUND=0

for dir in "$SOURCE_DIR"/*/; do
  [ -d "$dir" ] || continue
  [ -f "$dir/.published" ] && continue    # 已发布，跳过
  [ -f "$dir/.processing" ] && continue  # 处理中，跳过

  FOUND=1
  DIRNAME="$(basename "$dir")"
  log "New source detected: $DIRNAME"

  # 标记处理中
  touch "$dir/.processing"

  PROMPT="source/$DIRNAME 目录下有新内容需要处理。请使用 source-scanner skill 完整处理该目录：读取所有文件、提取文字和图片内容、生成中英双语博客文章、发布到 blog.mushroom.cv 和微信公众号草稿。处理完成后在 source/$DIRNAME/ 创建 .published 文件。"

  log "Calling claude for: $DIRNAME"
  if cd "$BLOG_DIR" && "$CLAUDE_BIN" \
      --dangerously-skip-permissions \
      --print \
      -p "$PROMPT" \
      >> "$LOG_FILE" 2>&1; then
    # 如果 claude 没有创建 .published，脚本兜底创建
    [ -f "$dir/.published" ] || touch "$dir/.published"
    rm -f "$dir/.processing"
    log "✅ Completed: $DIRNAME"
  else
    rm -f "$dir/.processing"
    log "❌ Failed: $DIRNAME (check $LOG_FILE for details)"
  fi
done

[ $FOUND -eq 0 ] && log "No new sources found."
log "=== Source scan done ==="
