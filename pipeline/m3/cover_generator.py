#!/usr/bin/env python3
"""
M3 小红书配图生成器
生成 3:4 比例图片 (900x1200) 并添加水印
"""

import os
import subprocess
import random
from pathlib import Path
from typing import List, Tuple

# 小红书图片规格
XHS_WIDTH = 900
XHS_HEIGHT = 1200
XHS_RATIO = "3:4"

# 配色方案（与6种模板对应）
COLOR_SCHEMES = {
    'fresh': {
        'name': '清新绿',
        'bg': '#ecfdf5',
        'primary': '#10b981',
        'secondary': '#34d399',
        'text': '#064e3b'
    },
    'orange': {
        'name': '活力橙',
        'bg': '#fff7ed',
        'primary': '#f97316',
        'secondary': '#fdba74',
        'text': '#7c2d12'
    },
    'pink': {
        'name': '甜美粉',
        'bg': '#fdf2f8',
        'primary': '#ec4899',
        'secondary': '#f9a8d4',
        'text': '#831843'
    },
    'blue': {
        'name': '专业蓝',
        'bg': '#eff6ff',
        'primary': '#3b82f6',
        'secondary': '#93c5fd',
        'text': '#1e3a8a'
    },
    'purple': {
        'name': '神秘紫',
        'bg': '#f5f3ff',
        'primary': '#8b5cf6',
        'secondary': '#c4b5fd',
        'text': '#4c1d95'
    },
    'brown': {
        'name': '暖棕',
        'bg': '#fefce8',
        'primary': '#a16207',
        'secondary': '#fde047',
        'text': '#713f12'
    }
}


class XHSCoverGenerator:
    """小红书配图生成器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / 'output'
        self.output_dir.mkdir(exist_ok=True)
        
        # 检查 ImageMagick
        self._check_imagemagick()
    
    def _check_imagemagick(self):
        """检查 ImageMagick 是否可用"""
        try:
            subprocess.run(['magick', '--version'], capture_output=True, check=True)
            self.magick_cmd = 'magick'
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['convert', '--version'], capture_output=True, check=True)
                self.magick_cmd = 'convert'
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError("ImageMagick not found. Please install: brew install imagemagick")
    
    def generate_cover(self, title: str, theme: str = None, output_name: str = None) -> str:
        """
        生成小红书封面图
        
        Args:
            title: 标题文字
            theme: 主题色 (fresh/orange/pink/blue/purple/brown)，None则随机
            output_name: 输出文件名
        
        Returns:
            生成的图片路径
        """
        # 随机选择主题
        if theme is None or theme not in COLOR_SCHEMES:
            theme = random.choice(list(COLOR_SCHEMES.keys()))
        
        scheme = COLOR_SCHEMES[theme]
        
        # 生成文件名
        if output_name is None:
            output_name = f"xhs_cover_{theme}_{random.randint(1000, 9999)}.jpg"
        
        output_path = self.output_dir / output_name
        
        # 处理标题（分行）
        lines = self._split_title(title)
        
        # 生成渐变背景
        self._create_gradient_background(output_path, scheme)
        
        # 添加装饰元素
        self._add_decorations(output_path, scheme)
        
        # 添加文字
        self._add_text(output_path, lines, scheme)
        
        # 添加水印
        self._add_watermark(output_path)
        
        return str(output_path)
    
    def generate_multiple(self, title: str, count: int = 3) -> List[str]:
        """
        生成多张配图
        
        Args:
            title: 标题
            count: 数量 (1-9)
        
        Returns:
            图片路径列表
        """
        count = max(1, min(9, count))
        
        paths = []
        themes = list(COLOR_SCHEMES.keys())
        
        for i in range(count):
            theme = themes[i % len(themes)]
            output_name = f"xhs_img_{i+1}_{theme}.jpg"
            path = self.generate_cover(title, theme, output_name)
            paths.append(path)
        
        return paths
    
    def _split_title(self, title: str, max_chars_per_line: int = 8) -> List[str]:
        """将标题分成多行"""
        # 清理标题
        title = title.strip()
        if len(title) > 20:
            title = title[:18] + '...'
        
        lines = []
        current_line = ""
        
        for char in title:
            if len(current_line) >= max_chars_per_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
        
        if current_line:
            lines.append(current_line)
        
        # 如果只有一行，尝试分成两行更均衡的
        if len(lines) == 1 and len(title) > 4:
            mid = len(title) // 2
            lines = [title[:mid], title[mid:]]
        
        return lines
    
    def _create_gradient_background(self, output_path: Path, scheme: dict):
        """创建渐变背景"""
        cmd = [
            self.magick_cmd,
            '-size', f'{XHS_WIDTH}x{XHS_HEIGHT}',
            'gradient:', f"{scheme['bg']}-white",
            '-blur', '0x30',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _add_decorations(self, output_path: Path, scheme: dict):
        """添加装饰元素"""
        # 添加圆形装饰
        circles = [
            (100, 100, 80),
            (800, 200, 60),
            (150, 1000, 100),
            (750, 1050, 50)
        ]
        
        for x, y, r in circles:
            cmd = [
                self.magick_cmd,
                str(output_path),
                '-fill', scheme['secondary'] + '40',  # 40% 透明度
                '-draw', f'circle {x},{y} {x+r},{y}',
                str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
    
    def _add_text(self, output_path: Path, lines: List[str], scheme: dict):
        """添加文字"""
        # 计算文字位置
        start_y = XHS_HEIGHT // 2 - len(lines) * 60
        
        for i, line in enumerate(lines):
            y = start_y + i * 120
            
            # 中文字体处理
            font_size = 80 if len(lines) <= 2 else 60
            
            cmd = [
                self.magick_cmd,
                str(output_path),
                '-fill', scheme['text'],
                '-font', 'PingFang-SC-Bold',  # macOS 中文字体
                '-pointsize', str(font_size),
                '-gravity', 'center',
                '-annotate', f'+0+{y - XHS_HEIGHT//2}', line,
                str(output_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # 如果特定字体失败，使用默认字体
                cmd[5] = '-font'
                cmd[6] = 'Arial-Bold'
                subprocess.run(cmd, check=True, capture_output=True)
    
    def _add_watermark(self, output_path: Path):
        """添加水印"""
        # 左上角: 🍄 Mushroom Blog
        cmd = [
            self.magick_cmd,
            str(output_path),
            '-fill', 'rgba(255,255,255,0.8)',
            '-stroke', 'rgba(0,0,0,0.3)',
            '-strokewidth', '1',
            '-font', 'PingFang-SC-Regular',
            '-pointsize', '24',
            '-gravity', 'NorthWest',
            '-annotate', '+20+20', '🍄 Mushroom Blog',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 右下角: XStack18
        cmd = [
            self.magick_cmd,
            str(output_path),
            '-fill', 'rgba(255,255,255,0.8)',
            '-stroke', 'rgba(0,0,0,0.3)',
            '-strokewidth', '1',
            '-font', 'PingFang-SC-Regular',
            '-pointsize', '20',
            '-gravity', 'SouthEast',
            '-annotate', '+20+20', 'XStack18',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)


def generate_xhs_cover(title: str, theme: str = None, output_dir: str = None) -> str:
    """便捷函数：生成单张封面"""
    generator = XHSCoverGenerator(output_dir)
    return generator.generate_cover(title, theme)


def generate_xhs_images(title: str, count: int = 3, output_dir: str = None) -> List[str]:
    """便捷函数：生成多张配图"""
    generator = XHSCoverGenerator(output_dir)
    return generator.generate_multiple(title, count)


if __name__ == '__main__':
    # 测试
    test_titles = [
        "AutoAgent：首个自优化智能体",
        "LLM Wiki 知识管理新范式",
        "Vitalik AI生存指南"
    ]
    
    generator = XHSCoverGenerator()
    
    for title in test_titles:
        print(f"\n生成封面: {title}")
        path = generator.generate_cover(title)
        print(f"保存至: {path}")
    
    # 测试多张
    print("\n生成多张配图...")
    paths = generator.generate_multiple("测试标题", 3)
    for p in paths:
        print(f"  - {p}")
