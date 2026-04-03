#!/bin/bash
# M1 → M2: Complete Pipeline
# Raw text → Blog publish → WeChat publish
#
# Usage:
#   ./m1-to-m2.sh <raw_text_file>              # P1 Blog + P2 WeChat
#   ./m1-to-m2.sh <raw_text_file> --blog-only  # 仅 P1 Blog
#   ./m1-to-m2.sh <markdown_file> --wechat     # 已有 Markdown，直接 P2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_ROOT="$SCRIPT_DIR"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🍄 ${GREEN}Mycelium M1 → M2 Complete Pipeline${NC}"
echo "=========================================="
echo ""

# 解析参数
RAW_FILE=""
MODE="full"  # full | blog-only | wechat
THEME="claude"
AUTHOR="Mycelium"

while [[ $# -gt 0 ]]; do
  case $1 in
    --blog-only)
      MODE="blog-only"
      shift
      ;;
    --wechat)
      MODE="wechat"
      shift
      ;;
    --theme)
      THEME="$2"
      shift 2
      ;;
    --author)
      AUTHOR="$2"
      shift 2
      ;;
    -*|--*)
      echo "Unknown option: $1"
      exit 1
      ;;
    *)
      RAW_FILE="$1"
      shift
      ;;
  esac
done

if [ -z "$RAW_FILE" ]; then
  echo "Usage:"
  echo "  $0 <raw_text_file>              # Full: P1 Blog + P2 WeChat"
  echo "  $0 <raw_text_file> --blog-only  # Only P1 Blog"
  echo "  $0 <markdown_file> --wechat     # Skip P1, only P2 WeChat"
  echo ""
  echo "Options:"
  echo "  --theme <name>    WeChat theme: claude|chengyun|blue|sticker"
  echo "  --author <name>   Article author"
  exit 1
fi

if [ ! -f "$RAW_FILE" ]; then
  echo "❌ File not found: $RAW_FILE"
  exit 1
fi

# 判断文件类型
if [[ "$RAW_FILE" == *.md ]] && [ "$MODE" = "wechat" ]; then
  # 直接 P2
  MARKDOWN_FILE="$RAW_FILE"
  SKIP_P1=true
else
  SKIP_P1=false
fi

# ==================== P1: Blog ====================
if [ "$SKIP_P1" = false ] && [ "$MODE" != "wechat" ]; then
  echo "${BLUE}[Phase 1/2]${NC} Publishing to Blog..."
  echo ""
  
  # Step 1: 生成 AI Prompt
  echo "[P1.1] Generating AI polish prompt..."
  cd "$BLOG_ROOT"
  
  python3 << PYTHON_EOF
import sys
sys.path.insert(0, 'pipeline/m1')
from polisher import polish_content

with open('$RAW_FILE', 'r', encoding='utf-8') as f:
    raw = f.read()

result = polish_content(raw)
print(f"Detected type: {result['template_type']}")
print("")
print("="*70)
print("COPY THE FOLLOWING PROMPT TO YOUR AI CHAT:")
print("="*70)
print("")
print(result['prompt'])
print("")
print("="*70)
print("AFTER AI RETURNS POLISHED MARKDOWN, SAVE IT TO:")
print("  /tmp/polished-article.md")
print("="*70)
PYTHON_EOF
  
  echo ""
  read -p "Press Enter after saving AI output to /tmp/polished-article.md..."
  
  if [ ! -f "/tmp/polished-article.md" ]; then
    echo "❌ /tmp/polished-article.md not found"
    exit 1
  fi
  
  # Step 2: 生成封面
  echo ""
  echo "[P1.2] Generating cover image..."
  
  TITLE=$(grep -m 1 "^title:" /tmp/polished-article.md | sed 's/title:\s*["'\''']*\([^"'\''']*\)["'\''']*/\1/')
  COVER_PATH=$(python3 -c "
import sys
sys.path.insert(0, 'pipeline/m1')
from cover_generator import create_cover_with_background
path = create_cover_with_background('$TITLE')
print(path)
" 2>/dev/null | tail -1)
  
  COVER_BASENAME=$(basename "$COVER_PATH")
  echo "   Cover: $COVER_BASENAME"
  
  # Step 3: 发布 Blog
  echo ""
  echo "[P1.3] Publishing to Blog..."
  
  python3 pipeline/m1/publisher.py /tmp/polished-article.md --images "src/assets/$COVER_BASENAME"
  
  # 获取生成的 Markdown 路径
  MARKDOWN_FILE=$(ls -t src/content/blog/*.md | head -1)
  
  echo ""
  echo "${GREEN}✅ P1 Blog Published!${NC}"
  echo "   Article: $MARKDOWN_FILE"
  
  # 清理
  rm -f /tmp/polished-article.md
  
  if [ "$MODE" = "blog-only" ]; then
    echo ""
    echo "🎉 Blog-only mode complete!"
    echo "Visit: https://blog.mushroom.cv"
    exit 0
  fi
  
  echo ""
  read -p "Continue to P2 WeChat? (Press Enter or Ctrl+C to cancel)..."
fi

# ==================== P2: WeChat ====================
echo ""
echo "${BLUE}[Phase 2/2]${NC} Publishing to WeChat..."
echo ""

if [ -z "$MARKDOWN_FILE" ]; then
  MARKDOWN_FILE="$RAW_FILE"
fi

cd "$BLOG_ROOT/pipeline/m2"

# 检查依赖
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  pnpm install
fi

# 运行 P2
node index.js "$BLOG_ROOT/$MARKDOWN_FILE" --theme "$THEME" --author "$AUTHOR"

echo ""
echo "${GREEN}🎉 M1 → M2 Complete!${NC}"
echo ""
echo "📋 Summary:"
echo "   Blog: https://blog.mushroom.cv"
echo "   WeChat: https://mp.weixin.qq.com (草稿箱)"
echo ""
