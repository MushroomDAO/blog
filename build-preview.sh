#!/bin/bash
# 构建并启动预览服务器

# Kill 现有 4321 端口进程
echo "🧹 Cleaning up port 4321..."
lsof -ti:4321 | xargs kill -9 2>/dev/null || true

# 构建
echo "🔨 Building..."
pnpm build

# 启动开发服务器
echo "🚀 Starting dev server on http://localhost:4321"
pnpm dev --port 4321
