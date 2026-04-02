#!/bin/bash

# Blog 部署脚本 - 方案B：本地构建后上传 Cloudflare Pages

set -e

echo "🚀 开始构建博客..."

# 1. 安装依赖（如果已安装可跳过）
echo "📦 检查依赖..."
pnpm install

# 2. 构建（生成静态 HTML 到 dist/）
echo "🔨 构建静态网站..."
pnpm build

echo "📂 dist/ 目录已生成，包含所有静态文件"

# 3. 部署到 Cloudflare Pages
echo "☁️  部署到 Cloudflare Pages..."
npx wrangler pages deploy dist --project-name=blog-mushroom

echo "✅ 部署完成！"
echo "🌐 访问: https://blog.mshroom.cv"
