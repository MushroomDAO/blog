#!/bin/bash
# 极速模式：已润色文字 → 直接发布 P1 + P2
# Usage: ./publish-fast.sh content.txt

set -e
cd "$(dirname "$0")"

# 检查参数
[ $# -lt 1 ] && echo "Usage: $0 content.txt" && exit 1
[ ! -f "$1" ] && echo "File not found: $1" && exit 1

echo "🚀 Fast Publish (P1+P2)"
echo "======================"

# Step 1: 添加 frontmatter
echo "[1/3] Adding frontmatter..."
python3 << EOF
import sys
sys.path.insert(0, 'pipeline/m1')
from polisher import generate_frontmatter, sanitize_filename
import json

with open('$1', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取第一行作为标题
title = content.split('\n')[0].replace('#', '').strip()[:40]
title_en = title

# 生成 frontmatter
fm = generate_frontmatter(
    title=title,
    title_en=title_en,
    description=content[:80].replace('\n', ' '),
    description_en=content[:80].replace('\n', ' '),
    template_type='tech-news',
    custom_tags=['tech', 'ai']
)

# 保存
with open('/tmp/fast-article.md', 'w', encoding='utf-8') as f:
    f.write(fm)
    f.write('\n')
    f.write(content)

print(f"   Title: {title}")
EOF

# Step 2: 封面 + P1 Blog
echo "[2/3] Publishing to Blog..."
TITLE=$(grep "^title:" /tmp/fast-article.md | head -1 | sed 's/.*: //' | tr -d "'\"")
COVER=$(python3 -c "import sys; sys.path.insert(0,'pipeline/m1'); from cover_generator import create_cover_with_background; print(create_cover_with_background('$TITLE'))" 2>/dev/null | tail -1)
python3 pipeline/m1/publisher.py /tmp/fast-article.md --images "$COVER"

# Step 3: P2 WeChat
echo "[3/3] Publishing to WeChat..."
MD=$(ls -t src/content/blog/*.md | head -1)
cd pipeline/m2 && node index.js "../../$MD" --theme claude

# 清理
rm -f /tmp/fast-article.md

echo ""
echo "✅ Done!"
echo "   Blog: https://blog.mushroom.cv"
echo "   WeChat: https://mp.weixin.qq.com"
