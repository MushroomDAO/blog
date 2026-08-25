#!/bin/bash
# 一键发布脚本：blog 文章发 blog + 公众号，my 文章发 my + 公众号
# Usage: ./scripts/publish.sh src/content/blog/xxx.md
#        ./scripts/publish.sh src/content/my/xxx.md

set -eo pipefail
cd "$(dirname "$0")/.."

# 加载 .env
if [ -f .env ]; then
  set -a; source .env; set +a
fi

# FU-24：.env.example 的 CLOUDFLARE_API_TOKEN/CLOUDFLARE_ACCOUNT_ID 是字面占位符
# （your_token_here/your_account_id_here）；忘替换时上面这行会原样导出，下面
# [2/4] 的 `npx wrangler pages deploy` 会拿假 token 去请求 Cloudflare API，报一个
# 看不懂的鉴权错误而不是"没配置"。精确匹配未替换的占位符时按未设置处理。
if [ "${CLOUDFLARE_API_TOKEN:-}" = "your_token_here" ]; then
  echo "⚠️  CLOUDFLARE_API_TOKEN in .env is still the .env.example placeholder — treating as unset" >&2
  unset CLOUDFLARE_API_TOKEN
fi
if [ "${CLOUDFLARE_ACCOUNT_ID:-}" = "your_account_id_here" ]; then
  echo "⚠️  CLOUDFLARE_ACCOUNT_ID in .env is still the .env.example placeholder — treating as unset" >&2
  unset CLOUDFLARE_ACCOUNT_ID
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MD_FILE="$1"

if [ -z "$MD_FILE" ] || [ ! -f "$MD_FILE" ]; then
  echo -e "${RED}❌ 用法: ./scripts/publish.sh src/content/blog/xxx.md${NC}"
  echo -e "${RED}        ./scripts/publish.sh src/content/my/xxx.md${NC}"
  exit 1
fi

# 检测文章类型
if echo "$MD_FILE" | grep -q "src/content/blog/"; then
  SECTION="blog"
elif echo "$MD_FILE" | grep -q "src/content/my/"; then
  SECTION="my"
else
  echo -e "${RED}❌ 文件必须在 src/content/blog/ 或 src/content/my/ 下${NC}"
  exit 1
fi

TITLE=$(grep -m1 '^title:' "$MD_FILE" | sed 's/^title: *"//' | sed 's/"$//' | sed "s/^title: *'//; s/'$//")
FILENAME=$(basename "$MD_FILE" .md)

echo -e "${GREEN}🚀 发布流程${NC}"
echo "===================="
echo -e "  📄 文件: ${BLUE}$MD_FILE${NC}"
echo -e "  📂 栏目: ${BLUE}$SECTION${NC}"
echo -e "  📝 标题: $TITLE"
echo ""

# ========== Step 1: 构建 ==========
echo "[1/4] 构建静态站点..."
pnpm build 2>&1 | tail -3
echo -e "   ${GREEN}✅ 构建完成${NC}"

# ========== Step 2: 部署 Cloudflare ==========
echo "[2/4] 部署到 Cloudflare Pages..."
export CLOUDFLARE_API_TOKEN
unset HTTPS_PROXY HTTP_PROXY ALL_PROXY
NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist \
  --project-name=blog-mushroom --branch=main --commit-dirty=true 2>&1 | tail -4
echo -e "   ${GREEN}✅ 部署完成${NC}"

# ========== Step 3: Git 提交（放在微信之前）==========
# 顺序刻意如此：Cloudflare 已经部署成功，git 同步不应该被下一步可能失败的
# 微信发布卡住——否则会出现"博客已上线，git 历史却没同步"的不一致状态。
echo "[3/4] Git 提交并推送..."
git add "$MD_FILE"

# 自动加入同名 banner 图（如果有未追踪的）
BANNER_PATTERN="src/assets/images/${FILENAME}"
for f in "${BANNER_PATTERN}".*; do
  [ -f "$f" ] && git add "$f" && echo "   + 图片: $f"
done

git commit -m "feat(${SECTION}): publish ${FILENAME}" 2>/dev/null || \
  echo -e "   ${YELLOW}⚠️ 无新变更需要提交${NC}"
git push 2>&1 | tail -2
echo -e "   ${GREEN}✅ 推送完成${NC}"

# ========== Step 4: 微信公众号（失败不阻断，博客+git 已经落地）==========
echo "[4/4] 发布到微信公众号..."
unset https_proxy http_proxy all_proxy
if node pipeline/m2/index.js "$MD_FILE" 2>&1 | tail -8; then
  echo -e "   ${GREEN}✅ 微信草稿完成${NC}"
else
  echo -e "   ${YELLOW}⚠️ 微信发布失败，博客已上线且 git 已同步，请手动处理微信草稿${NC}"
fi

echo ""
echo -e "${GREEN}✅ 发布完成！${NC}"
echo "===================="
echo "  Blog: https://blog.mushroom.cv/${SECTION}/${FILENAME}/"
echo "  WeChat: https://mp.weixin.qq.com（草稿箱）"
