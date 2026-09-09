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

# 4. 语义搜索索引
# deploy.sh 之前只管构建和上传，不碰索引——于是走这条路发的文章会「网页能打开、
# 关键词搜得到、语义搜索搜不到」。2026-09-09 那批 7 篇就是这么漏的。
# 正规发布流程 scripts/publish-blog.sh 第 4.7 步会按 slug 增量索引；这里作为
# 兜底，对比 dist 与索引 manifest，把缺的补上。
echo "🔍 检查语义搜索索引..."
if [ "${BLOG_SKIP_INDEX:-}" = "1" ]; then
  echo "  ⏭  skipped (BLOG_SKIP_INDEX=1)"
elif [ -z "${CLOUDFLARE_REGISTRAR_TOKEN:-}" ] || [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]; then
  echo "  ⚠️  缺 CLOUDFLARE_REGISTRAR_TOKEN / CLOUDFLARE_ACCOUNT_ID，跳过索引。"
  echo "     文章已上线但语义搜索搜不到——先 source .env 再重跑，或 BLOG_SKIP_INDEX=1 静音。"
elif [ ! -f semantic-search/scripts/incremental-index.py ]; then
  echo "  ⚠️  找不到 semantic-search/scripts/incremental-index.py，跳过。"
else
  # 只索引本次提交动过的文章。
  # 不用全库扫描（不带 --slug 就是全库）：588 篇要跑十分钟以上，每次部署都等
  # 不现实——实测那样会把 deploy 拖到超时，反而打出「索引更新失败」的假警报。
  # 注意这个脚本没有 --all 也没有 --help，多给一个参数会直接 exit 2。
  CHANGED_SLUGS=$(
    { git diff --name-only HEAD~1 HEAD -- src/content/blog/ 2>/dev/null
      git diff --name-only -- src/content/blog/ 2>/dev/null
      git ls-files --others --exclude-standard -- src/content/blog/ 2>/dev/null
    } | sed -n 's|^src/content/blog/\(.*\)\.mdx\{0,1\}$|\1|p' | sort -u
  )
  if [ -z "$CHANGED_SLUGS" ]; then
    echo "  ✓ 本次没有文章变动，跳过"
  else
    IDX_FAIL=""
    for SLUG in $CHANGED_SLUGS; do
      if python3 semantic-search/scripts/incremental-index.py --slug "$SLUG" --upsert >/dev/null 2>&1; then
        echo "  ✓ $SLUG"
      else
        echo "  ⚠️  $SLUG 索引失败"
        IDX_FAIL="1"
      fi
    done
    if [ -n "$IDX_FAIL" ]; then
      echo "     文章已上线但可能暂时搜不到。手动补跑："
      echo "     python3 semantic-search/scripts/incremental-index.py --slug <slug> --upsert"
    fi
    echo "     全库对账（偶尔跑一次，约十分钟）："
    echo "     python3 semantic-search/scripts/incremental-index.py --upsert"
  fi
fi

echo "✅ 部署完成！"
echo "🌐 访问: https://blog.mushroom.cv"
