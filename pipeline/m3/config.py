#!/usr/bin/env python3
"""
M3 小红书发布配置
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# MCP 服务配置
XHS_MCP_URL = os.getenv('XHS_MCP_URL', 'http://localhost:3000')

# 图片生成配置
XHS_IMAGE_WIDTH = 900
XHS_IMAGE_HEIGHT = 1200
XHS_IMAGE_RATIO = "3:4"

# 内容限制
MAX_TITLE_LENGTH = 20
MAX_CONTENT_LENGTH = 1000
MAX_IMAGES = 9
MIN_IMAGES = 1

# 默认标签
DEFAULT_TAGS = ['#分享', '#干货']

# 分类标签映射
CATEGORY_TAGS = {
    'tech': ['#AI工具', '#效率神器', '#打工人必备', '#科技改变生活'],
    'learning': ['#学习方法', '#自我提升', '#知识分享', '#学习日常'],
    'lifestyle': ['#生活方式', '#日常分享', '#好物推荐', '#生活小技巧'],
    'work': ['#职场日常', '#工作效率', '#职场干货', '#打工人']
}
