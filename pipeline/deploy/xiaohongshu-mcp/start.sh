#!/bin/bash
# 启动 xiaohongshu-mcp
set -e

cd "$(dirname "$0")"

docker-compose up -d

echo "[*] 服务已启动，端口: 3456"
echo "[*] 查看日志:    docker logs -f xhs-mcp"
echo "[*] 健康检查:    curl http://localhost:3456/health"
echo "[*] 登录二维码:  curl http://localhost:3456/api/v1/login/qrcode"
echo "[*] 登录状态:    curl http://localhost:3456/api/v1/login/status"
