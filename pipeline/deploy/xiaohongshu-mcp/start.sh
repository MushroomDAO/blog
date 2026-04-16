#!/bin/bash
# 构建并启动 xiaohongshu-mcp（本地 build，多架构支持）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
IMAGE="jhfnetboy/xiaohongshu-mcp:latest"

cd "$SCRIPT_DIR"

# 检测架构，映射为 Docker 格式
RAW_ARCH=$(uname -m)
case "$RAW_ARCH" in
    x86_64)  ARCH="amd64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *) ARCH="$RAW_ARCH" ;;
esac
echo "[*] 当前架构: $ARCH"

# 检查源码目录
if [ ! -f "$SRC_DIR/Dockerfile.multiarch" ]; then
    echo "[!] 未找到源码，尝试初始化 submodule..."
    git submodule update --init --recursive
fi

# 本地构建多架构镜像（当前平台）
echo "[*] 构建镜像 $IMAGE ..."
docker buildx build \
    --platform "linux/$ARCH" \
    -f "$SRC_DIR/Dockerfile.multiarch" \
    -t "$IMAGE" \
    --load \
    "$SRC_DIR"

# 创建必要目录
mkdir -p cookies logs data

# 启动服务
echo "[*] 启动服务..."
docker-compose up -d

echo "[*] 服务已启动，端口: 3456"
echo "[*] 查看日志: docker logs -f xhs-mcp"
echo "[*] 健康检查: curl http://localhost:3456/health"
