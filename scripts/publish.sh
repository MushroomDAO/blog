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
# round 2 review：比较前先去掉 CRLF/引号，跟 update-analytics.sh 已有的同款处理一致——
# Windows 编辑过的 .env 残留的尾随 \r，或手滑加的引号，会让下面的精确匹配失效，占位符
# 原样当成"已配置"导出。
_strip_env_value() {
  local v; v="$(printf '%s' "$1" | tr -d '\r')"
  v="${v%\"}"; v="${v#\"}"; v="${v%\'}"; v="${v#\'}"
  printf '%s' "$v"
}
_cf_placeholder_detected=false
if [ "$(_strip_env_value "${CLOUDFLARE_API_TOKEN:-}")" = "your_token_here" ]; then
  echo "⚠️  CLOUDFLARE_API_TOKEN in .env is still the .env.example placeholder — treating as unset" >&2
  unset CLOUDFLARE_API_TOKEN
  _cf_placeholder_detected=true
fi
if [ "$(_strip_env_value "${CLOUDFLARE_ACCOUNT_ID:-}")" = "your_account_id_here" ]; then
  echo "⚠️  CLOUDFLARE_ACCOUNT_ID in .env is still the .env.example placeholder — treating as unset" >&2
  unset CLOUDFLARE_ACCOUNT_ID
  _cf_placeholder_detected=true
fi
# round 3 review：光 unset 不够——这个仓库自己的约定（deploy.sh，见 CLAUDE.md）是
# CLOUDFLARE_API_TOKEN"没设置"合理地意味着"用 wrangler login 缓存的 OAuth 登录态"，
# 不能把"没设置"一律当错误。但"检测到占位符"是另一个明确信号：用户显然想用 token 认证
# （.env 里确实有这一行），只是没填——这时放任它掉进 wrangler 的 OAuth 兜底同样是错的：
# 没缓存登录态会弹浏览器卡最多 2 分钟；有缓存登录态（本机实测 `~/Library/Preferences/
# .wrangler/config` 里确实留着一份跟这个项目无关的旧登录态）会用那个身份悄悄部署成功，
# 两种都不是 FU-24 想要的"清楚报'没配置'"。所以检测到占位符时直接在下面 Step 2 部署前
# 硬停，不让它走到 wrangler。

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
# FU-24（round 3 review）：检测到占位符时在这里硬停，不让它走到 wrangler——理由见
# 文件前面 _cf_placeholder_detected 设置处的说明。
if [ "$_cf_placeholder_detected" = true ]; then
  echo -e "${RED}❌ .env 里的 CLOUDFLARE_API_TOKEN/CLOUDFLARE_ACCOUNT_ID 还是 .env.example 的占位符，拒绝部署。${NC}"
  echo -e "${RED}   请在 .env 里填真实值，或者跑 wrangler login 后删掉这两行改用 OAuth 登录。${NC}"
  exit 1
fi
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
