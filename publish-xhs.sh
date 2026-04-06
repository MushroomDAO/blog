#!/bin/bash
# M3 小红书一键发布脚本
# Usage: ./publish-xhs.sh content.txt

set -e
cd "$(dirname "$0")"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 content.txt [--theme theme_name]${NC}"
    exit 1
fi

CONTENT_FILE="$1"
if [ ! -f "$CONTENT_FILE" ]; then
    echo -e "${RED}File not found: $CONTENT_FILE${NC}"
    exit 1
fi

# 解析可选参数
THEME=""
if [ "$2" = "--theme" ] && [ -n "$3" ]; then
    THEME="$3"
fi

echo -e "${GREEN}🚀 M3 小红书发布流程${NC}"
echo "======================"

# Step 1: 内容优化
echo ""
echo -e "${YELLOW}[Step 1/5] 内容优化...${NC}"
python3 << EOF
import sys
sys.path.insert(0, 'pipeline/m3')
from optimizer import optimize_content

with open('$CONTENT_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

result = optimize_content(content)

# 保存优化结果
import json
with open('/tmp/xhs_optimized.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"标题: {result['title']}")
print(f"标签: {', '.join(result['tags'])}")
print(f"建议图片数: {result['suggested_images']}")
EOF

# 读取优化结果
TITLE=$(python3 -c "import json; print(json.load(open('/tmp/xhs_optimized.json'))['title'])")
CONTENT=$(python3 -c "import json; print(json.load(open('/tmp/xhs_optimized.json'))['content'])")
TAGS=$(python3 -c "import json; print(','.join(json.load(open('/tmp/xhs_optimized.json'))['tags']))")
IMAGE_COUNT=$(python3 -c "import json; print(json.load(open('/tmp/xhs_optimized.json'))['suggested_images'])")

# Step 2: 配图生成
echo ""
echo -e "${YELLOW}[Step 2/5] 生成配图 (${IMAGE_COUNT}张)...${NC}"
python3 << EOF
import sys
sys.path.insert(0, 'pipeline/m3')
from cover_generator import generate_xhs_images

result = optimize_content(open('$CONTENT_FILE').read())
title = result['title']
count = result['suggested_images']

paths = generate_xhs_images(title, count, output_dir='/tmp/xhs_images')

# 保存路径列表
with open('/tmp/xhs_image_paths.txt', 'w') as f:
    for p in paths:
        f.write(p + '\n')

for i, p in enumerate(paths, 1):
    print(f"  图片{i}: {p}")
EOF

# Step 3: 模板渲染
echo ""
echo -e "${YELLOW}[Step 3/5] 渲染模板...${NC}"

# 构建完整Markdown
FULL_CONTENT="---
title: $TITLE
---

$CONTENT"

echo "$FULL_CONTENT" > /tmp/xhs_full.md

# 调用渲染器
node pipeline/m3/renderer/xiaohongshu-renderer.js << 'RENDER'
const fs = require('fs');
const { render } = require('./pipeline/m3/renderer/xiaohongshu-renderer');

const markdown = fs.readFileSync('/tmp/xhs_full.md', 'utf-8');
const result = render(markdown, process.env.THEME || null);

fs.writeFileSync('/tmp/xhs_rendered.html', result.html);
fs.writeFileSync('/tmp/xhs_meta.json', JSON.stringify({
    title: result.title,
    theme: result.theme
}, null, 2));

console.log('主题:', result.theme);
RENDER

RENDERED_THEME=$(python3 -c "import json; print(json.load(open('/tmp/xhs_meta.json'))['theme'])")
echo "使用主题: $RENDERED_THEME"

# Step 4: 准备发布
echo ""
echo -e "${YELLOW}[Step 4/5] 准备发布...${NC}"
echo "标题: $TITLE"
echo "标签: $TAGS"

# 检查 MCP 服务
MCP_URL=${XHS_MCP_URL:-"http://localhost:3456"}
echo "MCP服务: $MCP_URL"

# Step 5: 发布到小红书
echo ""
echo -e "${YELLOW}[Step 5/5] 发布到小红书...${NC}"

python3 << 'PUBLISH'
import sys
import os
sys.path.insert(0, 'pipeline/m3')

from publisher import XHSPublisher

# 读取配置
mcp_url = os.getenv('XHS_MCP_URL', 'http://localhost:3456')
publisher = XHSPublisher(mcp_url)

# 读取内容
title = open('/tmp/xhs_title.txt').read().strip()
html = open('/tmp/xhs_rendered.html').read()

# 读取图片路径
with open('/tmp/xhs_image_paths.txt') as f:
    image_paths = [p.strip() for p in f.readlines()]

# 读取标签
import json
tags = json.load(open('/tmp/xhs_optimized.json'))['tags']

try:
    result = publisher.publish(title, html, image_paths, tags)
    print(f"✅ 发布成功!")
    print(f"   Note ID: {result.get('note_id')}")
    print(f"   URL: {result.get('url')}")
    
    # 保存结果
    with open('/tmp/xhs_result.json', 'w') as f:
        json.dump(result, f, indent=2)
        
except Exception as e:
    print(f"❌ 发布失败: {e}")
    sys.exit(1)
PUBLISH

# 清理临时文件
rm -f /tmp/xhs_*.json /tmp/xhs_*.txt /tmp/xhs_*.md /tmp/xhs_*.html

echo ""
echo -e "${GREEN}✅ 完成!${NC}"
echo "请登录小红书查看草稿箱"
