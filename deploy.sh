#!/bin/bash

# Blog 部署脚本 - 方案B：本地构建后上传 Cloudflare Pages

set -e

echo "🚀 开始构建博客..."

# 1. 安装依赖（如果已安装可跳过）
echo "📦 检查依赖..."
pnpm install

# 2. 构建
echo "🔨 构建中..."
pnpm build

# 3. 部署到 Cloudflare Pages
echo "☁️  部署到 Cloudflare Pages..."
npx wrangler pages deploy dist --project-name=blog-mushroom

echo "✅ 部署完成！访问: https://blog.mshroom.cv"
