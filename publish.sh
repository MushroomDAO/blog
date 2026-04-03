#!/bin/bash
# Usage: ./publish.sh content.txt
set -e
cd "$(dirname "$0")"

# P1: Blog
python3 pipeline/m1/polisher.py "$1" > /tmp/ai-prompt.txt
cat /tmp/ai-prompt.txt
echo ""
echo "↑ Copy prompt to AI, save output to /tmp/article.md, then press Enter"
read

TITLE=$(grep "^title:" /tmp/article.md | head -1 | sed 's/.*: //' | tr -d "'\"")
COVER=$(python3 -c "import sys; sys.path.insert(0,'pipeline/m1'); from cover_generator import create_cover_with_background; print(create_cover_with_background('$TITLE'))" 2>/dev/null | tail -1)
python3 pipeline/m1/publisher.py /tmp/article.md --images "$COVER"

# P2: WeChat
MD=$(ls -t src/content/blog/*.md | head -1)
cd pipeline/m2 && node index.js "../../$MD" --theme claude

echo "✅ Done! Blog: https://blog.mushroom.cv | WeChat: https://mp.weixin.qq.com"
