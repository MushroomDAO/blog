#!/bin/bash
# Aura AI Static Site Deploy
# Usage: ./deploy.sh

set -e
cd "$(dirname "$0")"

echo "🔨 Building..."
python3 build.py

echo ""
echo "🚀 Deploying to Cloudflare Pages (project: auraai)..."
npx wrangler pages deploy dist/ --project-name=auraai --branch=main --commit-dirty=true

echo ""
echo "✅ Done! Visit: https://auraai.mushroom.cv"
