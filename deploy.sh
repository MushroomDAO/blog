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
# account_id 不写进 wrangler.toml（Pages 项目的 schema 不认这个字段，写了会让
# 每次部署直接报错退出）——按 wrangler 实际支持的方式，部署前导出。这个账号 id
# 现在唯一权威来源是项目 .env 的 CLOUDFLARE_ACCOUNT_ID（跟 CLOUDFLARE_API_TOKEN
# 放在一起，被 publish.sh/publish-blog.sh/auto-publish.sh/scan-sources.sh 这几个
# 已有的 wrangler 调用点整体 source .env 后自动带上）——这里的字面量只是 shell
# 没导出该变量时的兜底，不是权威值，改账号只需要改 .env 这一处。
echo "☁️  部署到 Cloudflare Pages..."
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-7bf23342f21baa5ebfc7bc7b74f5a1f2}" \
  npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true

echo "✅ 部署完成！"
echo "🌐 访问: https://blog.mushroom.cv"
