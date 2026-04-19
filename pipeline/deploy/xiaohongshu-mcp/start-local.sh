#!/bin/bash
# XHS MCP 本地快速启动 — MacBook 用，不依赖 Mac Mini
# 用法: ./start-local.sh [chrome_profile_number]
#   默认 Profile 4；可通过 XHS_CHROME_PROFILE 环境变量覆盖完整路径

PROFILE_NUM="${1:-4}"
PROFILE="${XHS_CHROME_PROFILE:-$HOME/Library/Application Support/Google/Chrome/Profile $PROFILE_NUM}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BINARY="$HOME/Library/Scripts/xhs-mcp-mac"
CDP_PORT=9222
MCP_PORT=18060

# binary 不存在则提示编译
if [ ! -f "$BINARY" ]; then
  echo "[xhs-local] Binary not found at $BINARY"
  echo "[xhs-local] Build it first:"
  echo "  cd $SCRIPT_DIR/src"
  echo "  go build -o ~/Library/Scripts/xhs-mcp-mac ."
  exit 1
fi

# 终止已有 MCP 进程
OLD=$(/usr/sbin/lsof -ti :$MCP_PORT 2>/dev/null || true)
[ -n "$OLD" ] && kill "$OLD" 2>/dev/null && /bin/sleep 1

# 如果 Chrome CDP 未就绪，启动 Chrome
if ! /usr/bin/curl -s "http://localhost:$CDP_PORT/json/version" > /dev/null 2>&1; then
  echo "[xhs-local] Starting Chrome (Profile: $PROFILE)..."
  open -na "Google Chrome" --args \
    --user-data-dir="$PROFILE" \
    --remote-debugging-port=$CDP_PORT \
    --no-first-run \
    --no-default-browser-check \
    https://creator.xiaohongshu.com/publish/publish?source=official
  for i in $(seq 1 15); do
    /usr/bin/curl -s "http://localhost:$CDP_PORT/json/version" > /dev/null 2>&1 && break
    /bin/sleep 1
  done
fi

echo "[xhs-local] XHS MCP ready at http://localhost:$MCP_PORT"
echo "[xhs-local] Test: curl http://localhost:$MCP_PORT/health"
echo ""
exec env CHROME_CONNECT_URL="http://localhost:$CDP_PORT" "$BINARY"
