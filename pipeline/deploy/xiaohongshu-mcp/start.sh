#!/bin/bash
set -e
cd "$(dirname "$0")"

docker-compose up -d

# 启动 Tailscale 代理（让 VPN 内其他机器可访问）
pkill -f "python3 proxy.py" 2>/dev/null || true
nohup python3 proxy.py > logs/proxy.log 2>&1 &
echo "[*] Tailscale 代理已启动 (PID $!)"

TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "N/A")
echo "[*] 本机访问:     http://localhost:3456/health"
echo "[*] VPN 内访问:   http://${TAILSCALE_IP}:3456/health"
echo "[*] 登录:         ./login.sh"
