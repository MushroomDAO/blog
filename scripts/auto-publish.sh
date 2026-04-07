#!/bin/bash
# 自动发布脚本 - 最小化交互
# Usage: ./scripts/auto-publish.sh /path/to/content.txt [optional-image-path]

set -e
cd "$(dirname "$0")/.."

CONTENT_FILE="$1"
IMAGE_PATH="$2"  # 可选
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 自动发布流程${NC}"
echo "===================="

# ========== Step 1: 提取内容 ==========
echo "[1/5] 处理内容..."

if [ ! -f "$CONTENT_FILE" ]; then
    echo -e "${RED}❌ 内容文件不存在: $CONTENT_FILE${NC}"
    exit 1
fi

# 提取第一行作为标题
TITLE=$(head -1 "$CONTENT_FILE" | sed 's/^#* *//' | cut -c1-40)
# 生成英文 slug
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
SLUG="${SLUG:-article}-${TIMESTAMP}"

echo "   标题: $TITLE"
echo "   Slug: $SLUG"

# ========== Step 2: 处理图片 ==========
echo "[2/5] 处理图片..."

if [ -n "$IMAGE_PATH" ] && [ -f "$IMAGE_PATH" ]; then
    echo "   使用提供的图片"
    
    # 生成封面（1200x630，可裁剪）
    magick convert "$IMAGE_PATH" \
        -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 \
        "src/assets/images/cover-${SLUG}.jpg" 2>/dev/null || \
    convert "$IMAGE_PATH" \
        -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 \
        "src/assets/images/cover-${SLUG}.jpg"
    
    # 生成文章内图片（1200宽，不裁剪）
    magick convert "$IMAGE_PATH" \
        -resize 1200x -quality 85 \
        "src/assets/images/content-${SLUG}.jpg" 2>/dev/null || \
    convert "$IMAGE_PATH" \
        -resize 1200x -quality 85 \
        "src/assets/images/content-${SLUG}.jpg"
    
    COVER_IMAGE="../../assets/images/cover-${SLUG}.jpg"
    CONTENT_IMAGE="../../assets/images/content-${SLUG}.jpg"
    HAS_IMAGE=true
    echo -e "   ${GREEN}✅ 图片处理完成${NC}"
else
    echo "   未提供图片，使用默认封面"
    COVER_NUM=$((RANDOM % 5 + 1))
    COVER_IMAGE="../../assets/blog-placeholder-${COVER_NUM}.jpg"
    CONTENT_IMAGE=""
    HAS_IMAGE=false
fi

# ========== Step 3: 创建 Markdown ==========
echo "[3/5] 创建文章..."

MD_FILE="src/content/blog/${SLUG}.md"

# 生成 frontmatter
cat > "$MD_FILE" << EOF
---
title: "$TITLE"
titleEn: "$SLUG"
description: "$(head -5 "$CONTENT_FILE" | tail -4 | tr '\n' ' ' | cut -c1-100)"
descriptionEn: "$(head -5 "$CONTENT_FILE" | tail -4 | tr '\n' ' ' | cut -c1-100)"
pubDate: "$(date +%Y-%m-%d)"
category: "Tech-News"
tags: ["tech", "ai"]
heroImage: "$COVER_IMAGE"
---

EOF

# 如果提供了图片，在开头插入
if [ "$HAS_IMAGE" = true ]; then
    echo "![$TITLE]($CONTENT_IMAGE)" >> "$MD_FILE"
    echo "" >> "$MD_FILE"
fi

# 添加内容
cat "$CONTENT_FILE" >> "$MD_FILE"

echo -e "   ${GREEN}✅ 文章创建: $MD_FILE${NC}"

# ========== Step 4: 构建部署 ==========
echo "[4/5] 构建并部署..."

pnpm build 2>&1 | tail -3

# 部署到 Production
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main 2>&1 | tail -5

echo -e "   ${GREEN}✅ 部署完成${NC}"

# ========== Step 5: 验证 ==========
echo "[5/5] 验证发布..."

sleep 2

# 验证文章URL
if curl -s "https://blog.mushroom.cv/blog/${SLUG}/" 2>/dev/null | grep -q "$TITLE" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Blog 文章可访问${NC}"
else
    echo -e "   ${YELLOW}⚠️ Blog 验证可能需要等待...${NC}"
fi

# ========== Step 6: WeChat ==========
echo ""
echo "📱 发布到微信公众号..."
cd pipeline/m2
node index.js "../../$MD_FILE" 2>&1 | tail -10

echo ""
echo -e "${GREEN}✅ 完成！${NC}"
echo "===================="
echo "Blog: https://blog.mushroom.cv/blog/${SLUG}/"
echo "WeChat: https://mp.weixin.qq.com"
