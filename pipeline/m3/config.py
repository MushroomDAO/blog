"""
M3 Xiaohongshu Pipeline Configuration
M3 小红书发布流水线配置
"""

import os
from pathlib import Path

# ==================== MCP 服务配置 ====================

# MCP 服务地址（Mac Mini 上部署的 xiaohongshu-mcp）
# 默认端口 3456（可根据实际部署修改）
XHS_MCP_URL = os.getenv('XHS_MCP_URL', 'http://localhost:3456')

# API 超时设置（秒）
XHS_API_TIMEOUT = int(os.getenv('XHS_API_TIMEOUT', '60'))

# 视频上传超时（秒，视频上传较慢）
XHS_VIDEO_TIMEOUT = int(os.getenv('XHS_VIDEO_TIMEOUT', '300'))

# ==================== 内容限制 ====================

# 小红书内容限制（根据 xiaohongshu-mcp 文档）
XHS_LIMITS = {
    'title_max': 20,          # 标题最多 20 字
    'content_max': 1000,      # 正文最多 1000 字
    'images_max': 9,          # 最多 9 张图片
    'images_min': 1,          # 至少 1 张图片
    'daily_post_limit': 50,   # 每天最多 50 篇
    'schedule_min_hours': 1,  # 定时发布最早 1 小时后
    'schedule_max_days': 14,  # 定时发布最晚 14 天内
}

# ==================== 封面配置 ====================

# 封面图片尺寸（3:4 比例，小红书推荐）
COVER_SIZE = (900, 1200)

# 封面输出质量
COVER_QUALITY = 85

# 封面主题配色（6 套主题）
COVER_THEMES = {
    'mint': {
        'name': '清新绿',
        'primary': '#10b981',
        'secondary': '#34d399',
        'gradient': ['#10b981', '#059669'],
        'text': '#ffffff'
    },
    'orange': {
        'name': '活力橙',
        'primary': '#f97316',
        'secondary': '#fb923c',
        'gradient': ['#f97316', '#ea580c'],
        'text': '#ffffff'
    },
    'pink': {
        'name': '甜美粉',
        'primary': '#ec4899',
        'secondary': '#f472b6',
        'gradient': ['#ec4899', '#db2777'],
        'text': '#ffffff'
    },
    'blue': {
        'name': '专业蓝',
        'primary': '#3b82f6',
        'secondary': '#60a5fa',
        'gradient': ['#3b82f6', '#2563eb'],
        'text': '#ffffff'
    },
    'purple': {
        'name': '神秘紫',
        'primary': '#8b5cf6',
        'secondary': '#a78bfa',
        'gradient': ['#8b5cf6', '#7c3aed'],
        'text': '#ffffff'
    },
    'brown': {
        'name': '复古棕',
        'primary': '#92400e',
        'secondary': '#b45309',
        'gradient': ['#92400e', '#78350f'],
        'text': '#ffffff'
    }
}

# 默认水印
COVER_WATERMARKS = {
    'top_left': '🍄 Mushroom Blog',
    'bottom_right': 'XStack18'
}

# ==================== 中文字体配置 ====================

# 字体搜索路径（按优先级）
FONT_PATHS = [
    # macOS 系统字体
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
    
    # Linux 系统字体
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    
    # Windows 系统字体
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/simsun.ttc',
    'C:/Windows/Fonts/msyh.ttc',
    
    # 项目字体目录
    str(Path(__file__).parent / 'fonts' / 'NotoSansCJK-Regular.ttc'),
]

# ==================== 可见性选项 ====================

VISIBILITY_OPTIONS = {
    'public': '公开可见',
    'private': '仅自己可见',
    'friends': '仅互关好友可见'
}

# ==================== 搜索筛选选项 ====================

SEARCH_SORT_OPTIONS = [
    '综合',
    '最新',
    '最多点赞',
    '最多评论',
    '最多收藏'
]

SEARCH_TYPE_OPTIONS = [
    '不限',
    '视频',
    '图文'
]

SEARCH_TIME_OPTIONS = [
    '不限',
    '一天内',
    '一周内',
    '半年内'
]

# ==================== 工作目录 ====================

# 临时文件目录
TEMP_DIR = Path('/tmp/xhs-pipeline')

# 输出目录
OUTPUT_DIR = Path(os.getenv('XHS_OUTPUT_DIR', str(Path.home() / 'xhs-output')))

# Cookie 存储路径（Docker 挂载路径）
COOKIES_PATH = Path('/data/cookies.json')

# ==================== 日志配置 ====================

LOG_LEVEL = os.getenv('XHS_LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ==================== 工具函数 ====================

def get_font_path() -> str:
    """
    获取可用的中文字体路径
    
    Returns:
        第一个可用的字体路径，如果没有则返回 None
    """
    for path in FONT_PATHS:
        if Path(path).exists():
            return path
    return None


def validate_schedule_time(schedule_at: str) -> tuple:
    """
    验证定时发布时间是否有效
    
    Args:
        schedule_at: ISO8601 格式时间字符串
        
    Returns:
        (is_valid, error_message)
    """
    from datetime import datetime, timedelta
    
    try:
        # 解析时间
        schedule_time = datetime.fromisoformat(schedule_at.replace('Z', '+00:00'))
        now = datetime.now(schedule_time.tzinfo)
        
        # 检查最早时间（1小时后）
        min_time = now + timedelta(hours=XHS_LIMITS['schedule_min_hours'])
        if schedule_time < min_time:
            return False, f"Schedule time must be at least {XHS_LIMITS['schedule_min_hours']} hour(s) in the future"
        
        # 检查最晚时间（14天内）
        max_time = now + timedelta(days=XHS_LIMITS['schedule_max_days'])
        if schedule_time > max_time:
            return False, f"Schedule time must be within {XHS_LIMITS['schedule_max_days']} days"
        
        return True, None
    except ValueError as e:
        return False, f"Invalid datetime format: {e}"


def truncate_content(content: str, max_length: int = None) -> str:
    """
    截断内容到指定长度
    
    Args:
        content: 原始内容
        max_length: 最大长度，默认使用 XHS_LIMITS['content_max']
        
    Returns:
        截断后的内容
    """
    max_length = max_length or XHS_LIMITS['content_max']
    
    if len(content) <= max_length:
        return content
    
    # 尝试在句子边界截断
    truncated = content[:max_length]
    
    # 寻找最后一个标点符号
    for char in ['。', '！', '？', '\n', '.', '!', '?']:
        if char in truncated:
            last_pos = truncated.rfind(char)
            if last_pos > max_length * 0.8:  # 至少保留 80% 内容
                return truncated[:last_pos + 1]
    
    # 默认截断并添加省略号
    return truncated[:max_length-3] + '...'


# 确保临时目录存在
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
