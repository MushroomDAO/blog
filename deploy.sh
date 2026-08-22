#!/bin/bash

# Blog 部署脚本 - 方案B：本地构建后上传 Cloudflare Pages
#
# 手动交互式运行用——假定已经 `wrangler login` 过，或者当前 shell 已经导出了
# CLOUDFLARE_API_TOKEN（比如 shell profile 里 source 过 .env）。非交互式场景
# （cron）请看 scripts/update-analytics.sh / pipeline/newsletter/local-fallback.sh，
# 那两个显式从项目 .env 读 token，不依赖交互式登录状态。

set -e
cd "$(dirname "$0")"

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
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true

echo "✅ 部署完成！"
echo "🌐 访问: https://blog.mushroom.cv"
