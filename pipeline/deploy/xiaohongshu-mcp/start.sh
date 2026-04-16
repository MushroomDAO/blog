#!/bin/bash
# 构建并启动 xiaohongshu-mcp（多架构支持 amd64 + arm64）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE="jhfnetboy/xiaohongshu-mcp:latest"

cd "$SCRIPT_DIR"

# 检测架构
ARCH=$(uname -m)
echo "[*] 当前架构: $ARCH"

# 拉取最新镜像（Docker 自动选择对应架构）
echo "[*] 拉取镜像 $IMAGE ..."
docker pull "$IMAGE"

# 创建必要目录
mkdir -p cookies logs data

# 启动服务
echo "[*] 启动服务..."
docker-compose up -d

echo "[*] 服务已启动，端口: 3456"
echo "[*] 查看日志: docker logs -f xhs-mcp"
echo "[*] 健康检查: curl http://localhost:3456/health"
