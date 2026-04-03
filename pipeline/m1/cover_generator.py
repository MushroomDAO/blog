#!/usr/bin/env python3
"""
M1: Blog Cover Generator
生成封面图，支持：
1. 使用现有占位图 (blog-placeholder-1~5.jpg) 作为背景
2. 使用指定图片作为背景
3. 生成渐变背景
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import random
from datetime import datetime
from pathlib import Path

BLOG_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = BLOG_ROOT / "src" / "assets"
PLACEHOLDER_IMAGES = [f"blog-placeholder-{i}.jpg" for i in range(1, 6)]


def get_random_placeholder() -> str:
    """随机选择一个占位图"""
    placeholder = random.choice(PLACEHOLDER_IMAGES)
    return str(ASSETS_DIR / placeholder)


def create_cover_with_background(
    title: str,
    background_path: str = None,
    output_dir: str = "src/assets"
) -> str:
    """
    使用指定背景图创建封面
    
    Args:
        title: 文章标题（会显示在文件名中，方便识别）
        background_path: 背景图路径（None则随机选择placeholder）
        output_dir: 输出目录
    
    Returns:
        生成的封面图路径
    """
    # 选择背景图
    if not background_path:
        background_path = get_random_placeholder()
    
    # 检查背景图是否存在
    if not os.path.exists(background_path):
        # 尝试在 assets 目录下找
        alt_path = ASSETS_DIR / os.path.basename(background_path)
        if alt_path.exists():
            background_path = str(alt_path)
        else:
            print(f"⚠️ Background not found: {background_path}")
            print(f"   Using random placeholder instead")
            background_path = get_random_placeholder()
    
    # 打开背景图
    img = Image.open(background_path)
    
    # 确保尺寸是 960x480
    if img.size != (960, 480):
        img = img.resize((960, 480), Image.Resampling.LANCZOS)
    
    # 添加轻微暗化效果，让文字（如果有的话）更清晰
    # 这里我们只是复制背景，文字可以后续用 CSS 叠加，或者手动添加
    
    # 生成文件名（使用标题拼音或英文）
    safe_title = "".join(c if c.isalnum() or c in '-_' else '-' for c in title[:30])
    safe_title = safe_title.strip('-').lower()
    
    timestamp = datetime.now().strftime('%m%d')
    if safe_title:
        filename = f"blog-cover-{safe_title}-{timestamp}.jpg"
    else:
        filename = f"blog-cover-{timestamp}.jpg"
    
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存
    img.save(output_path, 'JPEG', quality=90, optimize=True)
    
    print(f"✅ Cover created: {output_path}")
    print(f"   Background: {os.path.basename(background_path)}")
    
    return str(output_path)


def create_gradient_cover(
    title: str,
    scheme: str = "cyber",
    output_dir: str = "src/assets"
) -> str:
    """
    创建渐变背景封面
    
    Args:
        title: 文章标题
        scheme: 配色方案 (cyber/warm/purple/dark)
        output_dir: 输出目录
    
    Returns:
        生成的封面图路径
    """
    width, height = 960, 480
    
    # 配色方案
    schemes = {
        "cyber": {
            "top": (15, 23, 42),      # 深蓝
            "bottom": (30, 41, 59),   # 浅蓝
            "accent": (72, 191, 145)  # 薄荷绿
        },
        "warm": {
            "top": (60, 40, 30),
            "bottom": (100, 60, 40),
            "accent": (251, 146, 60)
        },
        "purple": {
            "top": (40, 20, 60),
            "bottom": (70, 40, 100),
            "accent": (157, 78, 221)
        },
        "dark": {
            "top": (20, 20, 20),
            "bottom": (40, 40, 40),
            "accent": (100, 100, 100)
        }
    }
    
    colors = schemes.get(scheme, schemes["cyber"])
    
    # 创建渐变背景
    img = Image.new('RGB', (width, height))
    
    for y in range(height):
        # 线性渐变
        ratio = y / height
        r = int(colors["top"][0] + (colors["bottom"][0] - colors["top"][0]) * ratio)
        g = int(colors["top"][1] + (colors["bottom"][1] - colors["top"][1]) * ratio)
        b = int(colors["top"][2] + (colors["bottom"][2] - colors["top"][2]) * ratio)
        
        draw = ImageDraw.Draw(img)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    draw = ImageDraw.Draw(img)
    
    # 添加装饰元素（科技感圆点）
    accent = colors["accent"]
    for i in range(15):
        x = random.randint(50, width - 50)
        y = random.randint(350, height - 30)
        size = random.randint(2, 5)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=accent)
    
    # 生成文件名
    safe_title = "".join(c if c.isalnum() or c in '-_' else '-' for c in title[:30])
    safe_title = safe_title.strip('-').lower()
    
    timestamp = datetime.now().strftime('%m%d')
    filename = f"blog-cover-{safe_title}-gradient-{timestamp}.jpg"
    
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    img.save(output_path, 'JPEG', quality=90, optimize=True)
    
    print(f"✅ Gradient cover created: {output_path}")
    print(f"   Scheme: {scheme}")
    
    return str(output_path)


def list_available_backgrounds() -> list:
    """列出可用的背景图片"""
    backgrounds = []
    
    # 占位图
    for ph in PLACEHOLDER_IMAGES:
        path = ASSETS_DIR / ph
        if path.exists():
            backgrounds.append(("placeholder", ph, str(path)))
    
    # 其他 jpg/png 图片
    for ext in ['*.jpg', '*.png', '*.jpeg']:
        for img in ASSETS_DIR.glob(ext):
            if img.name not in PLACEHOLDER_IMAGES and 'blog-cover' not in img.name:
                backgrounds.append(("custom", img.name, str(img)))
    
    return backgrounds


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("M1 Cover Generator")
        print("==================")
        print("")
        print("Usage:")
        print("  1. Random placeholder:")
        print("     python cover_generator.py 'Article Title'")
        print("")
        print("  2. Specific background:")
        print("     python cover_generator.py 'Title' --bg blog-placeholder-3.jpg")
        print("     python cover_generator.py 'Title' --bg /path/to/image.jpg")
        print("")
        print("  3. Gradient background:")
        print("     python cover_generator.py 'Title' --gradient")
        print("     python cover_generator.py 'Title' --gradient --scheme warm")
        print("")
        print("Available backgrounds:")
        for typ, name, path in list_available_backgrounds():
            print(f"  [{typ}] {name}")
        sys.exit(1)
    
    title = sys.argv[1]
    
    # 解析参数
    background = None
    use_gradient = False
    scheme = "cyber"
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--bg" and i + 1 < len(sys.argv):
            background = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--gradient":
            use_gradient = True
            i += 1
        elif sys.argv[i] == "--scheme" and i + 1 < len(sys.argv):
            scheme = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # 生成封面
    if use_gradient:
        output = create_gradient_cover(title, scheme=scheme)
    else:
        output = create_cover_with_background(title, background)
    
    print(f"\n📋 Use in frontmatter:")
    print(f"   heroImage: '../../assets/{os.path.basename(output)}'")
