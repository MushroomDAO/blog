#!/bin/bash
# 启动 xiaohongshu-mcp（aastar/xiaohongshu-mcp，多架构 amd64 + arm64）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE="aastar/xiaohongshu-mcp:latest"

cd "$SCRIPT_DIR"

echo "[*] 当前架构: $(uname -m)"

# 停止并删除旧容器
if docker ps -a --format '{{.Names}}' | grep -q '^xhs-mcp$'; then
    echo "[*] 停止并删除旧容器..."
    docker rm -f xhs-mcp
fi

# 删除本地旧镜像（包括之前本地构建的 jhfnetboy 版本）
for OLD_IMAGE in "$IMAGE" "jhfnetboy/xiaohongshu-mcp:latest"; do
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${OLD_IMAGE}$"; then
        echo "[*] 删除本地旧镜像 $OLD_IMAGE ..."
        docker rmi "$OLD_IMAGE"
    fi
done

# 拉取最新镜像
echo "[*] 拉取镜像 $IMAGE ..."
docker pull "$IMAGE"

mkdir -p cookies logs data

echo "[*] 启动服务..."
docker-compose up -d

echo "[*] 服务已启动，端口: 3456"
echo "[*] 查看日志: docker logs -f xhs-mcp"
echo "[*] 健康检查:    curl http://localhost:3456/health"
echo "[*] 登录二维码:  curl http://localhost:3456/api/v1/login/qrcode"
echo "[*] 登录状态:    curl http://localhost:3456/api/v1/login/status"
