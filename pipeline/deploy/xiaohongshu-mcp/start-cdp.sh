#!/bin/bash
# XHS MCP CDP 模式启动脚本 (launchd 管理)
# Chrome profile: jhfnetboy@gmail.com (Profile 4)
# 日志由 launchd StandardOutPath 统一管理，脚本不重定向

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BINARY="$SCRIPT_DIR/xhs-mcp-mac"
CHROME_PROFILE="/Users/nicolasshuaishuai/Library/Application Support/Google/Chrome/Profile 4"
CDP_PORT=9222
MCP_PORT=18060
CHROME_URL="https://creator.xiaohongshu.com/publish/publish?source=official"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== XHS CDP 服务启动 ==="

# ── 1. 终止残留旧进程 ────────────────────────────────────────────
OLD_PID=$(/usr/sbin/lsof -ti :$MCP_PORT 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
  log "终止旧 MCP 进程 PID=$OLD_PID"
  kill "$OLD_PID" 2>/dev/null || true
  /bin/sleep 2
fi

# ── 2. 确保 Chrome 以 CDP 模式运行 ──────────────────────────────
if /usr/bin/curl -s "http://localhost:$CDP_PORT/json/version" > /dev/null 2>&1; then
  log "Chrome CDP 已就绪，跳过启动"
else
  log "启动 Chrome (Profile 4 / jhfnetboy)..."
  open -na "Google Chrome" --args \
    --user-data-dir="$CHROME_PROFILE" \
    --remote-debugging-port=$CDP_PORT \
    --no-first-run \
    --no-default-browser-check \
    "$CHROME_URL"

  for i in $(seq 1 30); do
    if /usr/bin/curl -s "http://localhost:$CDP_PORT/json/version" > /dev/null 2>&1; then
      log "Chrome CDP 就绪 (${i}s)"
      break
    fi
    /bin/sleep 1
    if [ "$i" -eq 30 ]; then
      log "ERROR: Chrome CDP 30s 内未就绪，退出"
      exit 1
    fi
  done
fi

# ── 3. 启动 MCP Server（exec 替换 shell，launchd KeepAlive 管理重启）─
log "启动 MCP Server (:$MCP_PORT)..."
exec env CHROME_CONNECT_URL="http://localhost:$CDP_PORT" "$BINARY"
