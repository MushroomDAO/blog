#!/bin/bash
# M1: Complete Pipeline - Raw text → AI Polish → Publish with cover image
# Usage: ./m1-complete.sh <raw_text_file> [cover_image.png]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🍄 Mycelium M1 Complete Pipeline"
echo "================================="
echo ""

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <raw_text_file> [cover_image.png]"
    echo ""
    echo "Example:"
    echo "  $0 my-article.txt"
    echo "  $0 my-article.txt cover.png"
    exit 1
fi

RAW_FILE="$1"
COVER_IMAGE="${2:-}"

if [ ! -f "$RAW_FILE" ]; then
    echo "❌ Error: File not found: $RAW_FILE"
    exit 1
fi

# Step 1: Generate AI Prompt
echo "📝 Step 1: Generating AI polish prompt..."
cd "$BLOG_ROOT"

python3 << PYTHON_EOF
import sys
sys.path.insert(0, 'pipeline/m1')
from polisher import polish_content

with open('$RAW_FILE', 'r', encoding='utf-8') as f:
    raw = f.read()

result = polish_content(raw)

print(f"\n📋 Detected type: {result['template_type']}")
print(f"\n" + "="*60)
print("COPY THE FOLLOWING PROMPT TO YOUR AI CHAT:")
print("="*60 + "\n")
print(result['prompt'])
print("\n" + "="*60)
print("AFTER AI RETURNS POLISHED MARKDOWN, SAVE IT TO:")
print("  /tmp/polished-article.md")
print("="*60)
PYTHON_EOF

echo ""
read -p "Press Enter after saving AI output to /tmp/polished-article.md..."

# Step 2: Check if polished file exists
if [ ! -f "/tmp/polished-article.md" ]; then
    echo "❌ Error: /tmp/polished-article.md not found"
    exit 1
fi

# Step 3: Publish
echo ""
echo "🚀 Step 2: Publishing to Blog..."

if [ -n "$COVER_IMAGE" ]; then
    if [ ! -f "$COVER_IMAGE" ]; then
        echo "⚠️ Warning: Cover image not found: $COVER_IMAGE"
        COVER_IMAGE=""
    fi
fi

if [ -n "$COVER_IMAGE" ]; then
    python3 pipeline/m1/publisher.py /tmp/polished-article.md --images "$COVER_IMAGE"
else
    python3 pipeline/m1/publisher.py /tmp/polished-article.md
fi

echo ""
echo "✅ M1 Complete Pipeline finished!"
echo "Visit: https://blog.mushroom.cv"
