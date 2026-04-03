#!/bin/bash
# M1: Complete Pipeline - Raw text → AI Polish → Generate Cover → Publish
# 
# Usage:
#   ./m1-complete.sh <raw_text_file>              # 随机使用 placeholder 1-5 作为封面
#   ./m1-complete.sh <raw_text_file> --gradient   # 生成渐变背景封面
#   ./m1-complete.sh <raw_text_file> <image.jpg>  # 使用指定图片作为封面背景
#
# Examples:
#   ./m1-complete.sh my-article.txt
#   ./m1-complete.sh my-article.txt blog-placeholder-3.jpg
#   ./m1-complete.sh my-article.txt my-cover.png
#   ./m1-complete.sh my-article.txt --gradient

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🍄 ${GREEN}Mycelium M1 Complete Pipeline${NC}"
echo "================================"
echo ""

# 检查参数
if [ $# -lt 1 ]; then
    echo "Usage:"
    echo "  $0 <raw_text_file>                    # Random placeholder (1-5) as cover"
    echo "  $0 <raw_text_file> --gradient          # Generate gradient cover"
    echo "  $0 <raw_text_file> <image.jpg>         # Use custom image as cover"
    echo ""
    echo "Examples:"
    echo "  $0 article.txt                         # Random blog-placeholder-*.jpg"
    echo "  $0 article.txt blog-placeholder-2.jpg  # Use specific placeholder"
    echo "  $0 article.txt my-cover.png            # Use custom image"
    echo "  $0 article.txt --gradient              # Generate gradient background"
    exit 1
fi

RAW_FILE="$1"
COVER_OPTION="${2:-}"

if [ ! -f "$RAW_FILE" ]; then
    echo "❌ Error: File not found: $RAW_FILE"
    exit 1
fi

# 步骤 1: 生成 AI Prompt
echo "${BLUE}[Step 1/4]${NC} Generating AI polish prompt..."
echo ""

cd "$BLOG_ROOT"

python3 << PYTHON_EOF
import sys
sys.path.insert(0, 'pipeline/m1')
from polisher import polish_content

with open('$RAW_FILE', 'r', encoding='utf-8') as f:
    raw = f.read()

result = polish_content(raw)

print(f"📋 Detected type: {result['template_type']}")
print(f"   Suggested filename: {result.get('filename', 'article.md')}")
print("")
print("="*70)
print("📋 COPY THE FOLLOWING PROMPT TO YOUR AI CHAT:")
print("="*70)
print("")
print(result['prompt'])
print("")
print("="*70)
print("📋 AFTER AI RETURNS POLISHED MARKDOWN:")
print("   Save it to: /tmp/polished-article.md")
print("="*70)
PYTHON_EOF

echo ""
read -p "Press Enter after saving AI output to /tmp/polished-article.md..."

# 检查润色后的文件
if [ ! -f "/tmp/polished-article.md" ]; then
    echo "❌ Error: /tmp/polished-article.md not found"
    exit 1
fi

# 提取标题用于封面生成
TITLE=$(grep -m 1 "^title:" /tmp/polished-article.md | sed 's/title:\s*["'\''']*\([^"'\''']*\)["'\''']*/\1/')
if [ -z "$TITLE" ]; then
    TITLE=$(head -1 "$RAW_FILE")
fi

# 步骤 2: 生成封面
echo ""
echo "${BLUE}[Step 2/4]${NC} Generating cover image..."
echo "   Title: $TITLE"

if [ "$COVER_OPTION" = "--gradient" ]; then
    # 生成渐变背景
    echo "   Type: Gradient background"
    COVER_PATH=$(python3 -c "
import sys
sys.path.insert(0, 'pipeline/m1')
from cover_generator import create_gradient_cover
path = create_gradient_cover('$TITLE')
print(path)
" 2>/dev/null | tail -1)
    
elif [ -n "$COVER_OPTION" ]; then
    # 使用指定图片
    echo "   Type: Custom image ($COVER_OPTION)"
    
    # 检查是否是 placeholder 名称（不含路径）
    if [[ "$COVER_OPTION" == blog-placeholder-*.jpg ]]; then
        COVER_FULL_PATH="src/assets/$COVER_OPTION"
    elif [ -f "$COVER_OPTION" ]; then
        # 用户提供了完整路径
        COVER_FULL_PATH="$COVER_OPTION"
    elif [ -f "src/assets/$COVER_OPTION" ]; then
        # 在 assets 目录下
        COVER_FULL_PATH="src/assets/$COVER_OPTION"
    else
        echo "⚠️ Warning: Image not found: $COVER_OPTION"
        echo "   Using random placeholder instead"
        COVER_OPTION=""
    fi
    
    if [ -n "$COVER_OPTION" ]; then
        COVER_PATH=$(python3 -c "
import sys
sys.path.insert(0, 'pipeline/m1')
from cover_generator import create_cover_with_background
path = create_cover_with_background('$TITLE', '$COVER_FULL_PATH')
print(path)
" 2>/dev/null | tail -1)
    fi
fi

# 默认：随机使用 placeholder 1-5
if [ -z "$COVER_PATH" ]; then
    echo "   Type: Random placeholder (1-5)"
    COVER_PATH=$(python3 -c "
import sys
sys.path.insert(0, 'pipeline/m1')
from cover_generator import create_cover_with_background
path = create_cover_with_background('$TITLE', None)  # None = random
print(path)
" 2>/dev/null | tail -1)
fi

# 提取封面文件名用于发布
COVER_BASENAME=$(basename "$COVER_PATH")
echo "   ✅ Cover: $COVER_BASENAME"

# 步骤 3: 发布
echo ""
echo "${BLUE}[Step 3/4]${NC} Publishing to Blog..."

python3 pipeline/m1/publisher.py /tmp/polished-article.md --images "src/assets/$COVER_BASENAME"

# 步骤 4: 清理
echo ""
echo "${BLUE}[Step 4/4]${NC} Cleaning up..."
rm -f /tmp/polished-article.md

echo ""
echo "${GREEN}✅ M1 Complete Pipeline finished!${NC}"
echo ""
echo "📖 Visit: https://blog.mushroom.cv"
echo ""
