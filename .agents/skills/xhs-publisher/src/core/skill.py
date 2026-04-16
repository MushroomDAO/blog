#!/usr/bin/env python3
"""
XHS Publisher Skill - 小红书自动发布 Skill

基于 M3 系统的封装，提供统一的 Skill 接口
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# 添加 M3 路径
M3_PATH = Path(__file__).parent.parent.parent.parent.parent / 'pipeline' / 'm3'
sys.path.insert(0, str(M3_PATH))

from optimizer import XHSOptimizer
from cover_generator import XHSCoverGenerator
from publisher import XiaohongshuPublisher, PublishResult


class XHSPublisherSkill:
    """
    小红书发布 Skill
    
    使用示例:
        skill = XHSPublisherSkill()
        result = skill.publish("content.md", theme="blue")
    """
    
    def __init__(self, mcp_url: str = None):
        """
        初始化 Skill
        
        Args:
            mcp_url: MCP 服务地址，默认从环境变量 XHS_MCP_URL 读取
        """
        self.mcp_url = mcp_url or os.getenv('XHS_MCP_URL', 'http://localhost:3456')
        self.optimizer = XHSOptimizer()
        self.cover_gen = XHSCoverGenerator()
        self.publisher = XiaohongshuPublisher(mcp_url=self.mcp_url)
    
    def publish(self, content: str, theme: str = "blue", image_count: int = 3) -> PublishResult:
        """
        发布内容到小红书
        
        Args:
            content: 原始内容（Markdown 或纯文本）
            theme: 视觉主题 (fresh/orange/pink/blue/purple/brown)
            image_count: 配图数量 (1-9)
        
        Returns:
            PublishResult 发布结果
        """
        # Step 1: 优化内容
        print("[Step 1/4] 优化内容...")
        optimized = self.optimizer.optimize(content)
        print(f"  标题: {optimized['title']}")
        print(f"  标签: {', '.join(optimized['tags'])}")
        
        # Step 2: 生成配图
        print(f"[Step 2/4] 生成配图 ({image_count}张)...")
        images = self.cover_gen.generate(
            title=optimized['title'],
            count=image_count,
            theme=theme
        )
        print(f"  生成 {len(images)} 张图片")
        
        # Step 3: 检查 MCP 服务
        print("[Step 3/4] 检查 MCP 服务...")
        health = self.publisher.health_check()
        if not health.get('success', False):
            return PublishResult(
                success=False,
                message=f"MCP 服务不可用: {health.get('error', 'Unknown')}"
            )
        print("  MCP 服务正常")
        
        # Step 4: 发布
        print("[Step 4/4] 发布到小红书...")
        result = self.publisher.publish(
            title=optimized['title'],
            content=optimized['content'],
            images=images,
            tags=optimized['tags']
        )
        
        if result.success:
            print(f"  ✅ 发布成功!")
            print(f"  链接: {result.url}")
        else:
            print(f"  ❌ 发布失败: {result.message}")
        
        return result
    
    def preview(self, content: str, theme: str = "blue") -> Dict:
        """
        预览内容（不发布）
        
        Args:
            content: 原始内容
            theme: 视觉主题
        
        Returns:
            预览数据字典
        """
        optimized = self.optimizer.optimize(content)
        images = self.cover_gen.generate(
            title=optimized['title'],
            count=1,
            theme=theme
        )
        
        return {
            'title': optimized['title'],
            'content': optimized['content'],
            'tags': optimized['tags'],
            'preview_image': images[0] if images else None
        }


# 便捷的函数接口
def publish_to_xiaohongshu(content: str, theme: str = "blue", image_count: int = 3) -> PublishResult:
    """
    便捷函数：发布内容到小红书
    
    Args:
        content: 原始内容
        theme: 视觉主题
        image_count: 配图数量
    
    Returns:
        PublishResult 发布结果
    """
    skill = XHSPublisherSkill()
    return skill.publish(content, theme, image_count)


def preview_xiaohongshu(content: str, theme: str = "blue") -> Dict:
    """
    便捷函数：预览内容
    
    Args:
        content: 原始内容
        theme: 视觉主题
    
    Returns:
        预览数据字典
    """
    skill = XHSPublisherSkill()
    return skill.preview(content, theme)


if __name__ == "__main__":
    # 测试
    if len(sys.argv) < 2:
        print("Usage: python skill.py <content_file> [--theme theme_name]")
        sys.exit(1)
    
    content_file = sys.argv[1]
    theme = "blue"
    
    # 解析参数
    if "--theme" in sys.argv:
        idx = sys.argv.index("--theme")
        if idx + 1 < len(sys.argv):
            theme = sys.argv[idx + 1]
    
    # 读取内容
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 发布
    skill = XHSPublisherSkill()
    result = skill.publish(content, theme=theme)
    
    sys.exit(0 if result.success else 1)
