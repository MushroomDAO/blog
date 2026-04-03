#!/bin/bash
# M1: One-click Blog Publisher
# Usage: ./m1-publish.sh <markdown_file> [image1 image2 ...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🍄 Mycelium Blog Publisher (M1)"
echo "================================"

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <markdown_file> [image_paths...]"
    echo ""
    echo "Example:"
    echo "  $0 article.md"
    echo "  $0 article.md cover.png diagram.png"
    exit 1
fi

MARKDOWN_FILE="$1"
shift
IMAGES="$@"

# Validate markdown file exists
if [ ! -f "$MARKDOWN_FILE" ]; then
    echo "❌ Error: Markdown file not found: $MARKDOWN_FILE"
    exit 1
fi

echo "📄 Markdown: $MARKDOWN_FILE"
if [ -n "$IMAGES" ]; then
    echo "🖼️  Images: $IMAGES"
fi

# Run publisher
echo ""
echo "🚀 Starting publish flow..."
cd "$BLOG_ROOT"

if [ -n "$IMAGES" ]; then
    python3 pipeline/m1/publisher.py "$MARKDOWN_FILE" --images $IMAGES
else
    python3 pipeline/m1/publisher.py "$MARKDOWN_FILE"
fi

echo ""
echo "✅ M1 Publish complete!"
echo "Visit: https://blog.mushroom.cv"
