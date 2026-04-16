#!/bin/bash
# XHS Publisher Skill - 一键发布脚本

set -e

cd "$(dirname "$0")/../.."

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <content_file> [--theme theme_name] [--preview]${NC}"
    echo ""
    echo "Available themes: fresh, orange, pink, blue, purple, brown"
    echo ""
    echo "Examples:"
    echo "  $0 article.md"
    echo "  $0 article.md --theme blue"
    echo "  $0 article.md --preview"
    exit 1
fi

CONTENT_FILE="$1"
THEME="blue"
PREVIEW=false

# 解析参数
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            THEME="$2"
            shift 2
            ;;
        --preview)
            PREVIEW=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 检查文件
if [ ! -f "$CONTENT_FILE" ]; then
    echo -e "${RED}File not found: $CONTENT_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 XHS Publisher Skill${NC}"
echo "======================"
echo "文件: $CONTENT_FILE"
echo "主题: $THEME"
echo ""

if [ "$PREVIEW" = true ]; then
    echo -e "${YELLOW}预览模式（不发布）${NC}"
    python3 .agents/skills/xhs-publisher/src/core/skill.py "$CONTENT_FILE" --theme "$THEME" --preview
else
    echo -e "${YELLOW}发布模式${NC}"
    python3 .agents/skills/xhs-publisher/src/core/skill.py "$CONTENT_FILE" --theme "$THEME"
fi
