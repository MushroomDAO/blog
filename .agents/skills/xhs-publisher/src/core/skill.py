#!/usr/bin/env python3
"""
XHS Publisher Skill - 小红书自动发布 Skill

基于 MCP 服务的封装，直接调用 MCP HTTP API
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import List, Dict, Optional

# 添加 M3 路径用于内容优化
M3_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / 'pipeline' / 'm3'
sys.path.insert(0, str(M3_PATH))

try:
    from optimizer import XHSOptimizer
except ImportError:
    # Fallback: 简单优化器
    class XHSOptimizer:
        def optimize(self, content: str, category: str = 'tech') -> dict:
            lines = content.strip().split('\n')
            title = lines[0][:20] if lines[0] else "分享"
            return {
                'title': title,
                'content': content,
                'tags': ['#生活方式', '#分享'],
                'keywords': []
            }


class XHSPublisherSkill:
    """
    小红书发布 Skill - 直接调用 MCP API
    """
    
    def __init__(self, mcp_url: str = None):
        """
        初始化 Skill
        
        Args:
            mcp_url: MCP 服务地址，默认从环境变量 XHS_MCP_URL 读取
        """
        self.mcp_url = mcp_url or os.getenv('XHS_MCP_URL', 'http://localhost:3456')
        self.optimizer = XHSOptimizer()
    
    def health_check(self) -> Dict:
        """检查 MCP 服务健康状态"""
        try:
            resp = requests.get(f"{self.mcp_url}/health", timeout=10)
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_login(self) -> Dict:
        """检查登录状态"""
        try:
            resp = requests.get(f"{self.mcp_url}/api/v1/login/status", timeout=10)
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到 MCP 服务
        
        Returns:
            图片 URL 或 None
        """
        try:
            with open(image_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            resp = requests.post(
                f"{self.mcp_url}/api/v1/upload",
                json={"image": img_data},
                timeout=30
            )
            result = resp.json()
            
            if result.get('success'):
                return result.get('data', {}).get('url')
            else:
                print(f"图片上传失败: {result.get('message')}")
                return None
                
        except Exception as e:
            print(f"图片上传异常: {e}")
            return None
    
    def publish(
        self, 
        content: str, 
        images: List[str] = None,
        theme: str = "blue"
    ) -> Dict:
        """
        发布内容到小红书
        
        Args:
            content: 原始内容（Markdown 或纯文本）
            images: 图片路径列表（1-9张）
            theme: 视觉主题（仅用于优化器）
        
        Returns:
            发布结果
        """
        # Step 1: 优化内容
        print("[Step 1/3] 优化内容...")
        optimized = self.optimizer.optimize(content)
        print(f"  标题: {optimized['title']}")
        print(f"  标签: {', '.join(optimized['tags'])}")
        
        # Step 2: 检查 MCP 服务
        print("[Step 2/3] 检查 MCP 服务...")
        health = self.health_check()
        if not health.get('success'):
            return {"success": False, "message": f"MCP 服务不可用: {health.get('error')}"}
        
        login = self.check_login()
        if not login.get('data', {}).get('is_logged_in'):
            return {"success": False, "message": "未登录，请先扫码登录"}
        
        print(f"  服务正常，已登录: {login['data'].get('username')}")
        
        # Step 3: 上传图片（如果有）
        print("[Step 3/3] 发布到小红书...")
        image_urls = []
        if images:
            for img_path in images:
                if os.path.exists(img_path):
                    url = self._upload_image(img_path)
                    if url:
                        image_urls.append(url)
                        print(f"  图片上传成功")
                else:
                    print(f"  图片不存在: {img_path}")
        
        # 构建发布请求
        publish_data = {
            "title": optimized['title'],
            "content": optimized['content'],
            "images": image_urls,
            "tags": optimized['tags'][:10]  # 最多10个标签
        }
        
        # 发布
        try:
            resp = requests.post(
                f"{self.mcp_url}/api/v1/publish",
                json=publish_data,
                timeout=60
            )
            result = resp.json()
            
            if result.get('success'):
                print(f"✅ 发布成功!")
                print(f"   笔记ID: {result.get('data', {}).get('note_id')}")
                return result
            else:
                print(f"❌ 发布失败: {result.get('message')}")
                return result
                
        except Exception as e:
            return {"success": False, "message": f"发布请求异常: {e}"}
    
    def preview(self, content: str) -> Dict:
        """
        预览内容（不发布）
        
        Args:
            content: 原始内容
        
        Returns:
            预览数据
        """
        optimized = self.optimizer.optimize(content)
        
        return {
            'title': optimized['title'],
            'content': optimized['content'],
            'tags': optimized['tags']
        }


# 便捷的函数接口
def publish_to_xiaohongshu(
    content: str, 
    images: List[str] = None,
    mcp_url: str = None
) -> Dict:
    """
    便捷函数：发布内容到小红书
    """
    skill = XHSPublisherSkill(mcp_url=mcp_url)
    return skill.publish(content, images)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='XHS Publisher Skill')
    parser.add_argument('content_file', help='内容文件路径')
    parser.add_argument('--images', nargs='+', help='图片路径列表')
    parser.add_argument('--mcp-url', help='MCP 服务地址')
    parser.add_argument('--preview', action='store_true', help='仅预览')
    
    args = parser.parse_args()
    
    # 读取内容
    with open(args.content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建 skill
    skill = XHSPublisherSkill(mcp_url=args.mcp_url)
    
    if args.preview:
        result = skill.preview(content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = skill.publish(content, images=args.images)
        print(json.dumps(result, ensure_ascii=False, indent=2))
