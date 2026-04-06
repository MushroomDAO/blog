#!/usr/bin/env python3
"""
M3 小红书发布器
连接 MCP 服务，上传图片并发布图文
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional

# MCP 服务地址（部署后修改）
DEFAULT_MCP_URL = "http://localhost:3000"

class XHSPublisher:
    """小红书发布器"""
    
    def __init__(self, mcp_url: str = None):
        self.mcp_url = mcp_url or os.getenv('XHS_MCP_URL', DEFAULT_MCP_URL)
        self.session = requests.Session()
        
    def check_login(self) -> bool:
        """检查登录状态"""
        try:
            resp = self.session.get(f"{self.mcp_url}/api/check-login", timeout=10)
            data = resp.json()
            return data.get('is_logged_in', False)
        except Exception as e:
            print(f"❌ 检查登录状态失败: {e}")
            return False
    
    def get_login_qrcode(self) -> Dict:
        """获取登录二维码"""
        try:
            resp = self.session.get(f"{self.mcp_url}/api/login-qrcode", timeout=10)
            return resp.json()
        except Exception as e:
            print(f"❌ 获取二维码失败: {e}")
            return {}
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到小红书 CDN
        
        Args:
            image_path: 本地图片路径
        
        Returns:
            上传后的URL
        """
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                resp = self.session.post(
                    f"{self.mcp_url}/api/upload",
                    files=files,
                    timeout=30
                )
                data = resp.json()
                
                if 'url' in data:
                    print(f"✅ 图片上传成功: {Path(image_path).name}")
                    return data['url']
                else:
                    raise Exception(f"上传失败: {data}")
                    
        except Exception as e:
            print(f"❌ 图片上传失败 {image_path}: {e}")
            raise
    
    def upload_images(self, image_paths: List[str]) -> List[str]:
        """批量上传图片"""
        urls = []
        for path in image_paths:
            url = self.upload_image(path)
            urls.append(url)
        return urls
    
    def publish_note(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: List[str] = None,
        visibility: str = "public",
        is_original: bool = True,
        schedule_at: str = None
    ) -> Dict:
        """
        发布图文笔记
        
        Args:
            title: 标题（最多20字）
            content: 正文内容
            images: 图片URL列表（1-9张）
            tags: 标签列表
            visibility: public(公开)/private(私密)/fans(粉丝可见)
            is_original: 是否原创
            schedule_at: 定时发布时间（可选）
        
        Returns:
            发布结果 {note_id, url, status}
        """
        # 限制图片数量
        if len(images) > 9:
            images = images[:9]
            print(f"⚠️ 图片超过9张，只取前9张")
        
        if len(images) < 1:
            raise ValueError("至少需要1张图片")
        
        # 构建请求
        payload = {
            "title": title[:20],  # 限制20字
            "content": content,
            "images": images,
            "tags": tags or [],
            "visibility": visibility,
            "is_original": is_original
        }
        
        if schedule_at:
            payload["schedule_at"] = schedule_at
        
        try:
            resp = self.session.post(
                f"{self.mcp_url}/api/publish",
                json=payload,
                timeout=60
            )
            
            data = resp.json()
            
            if resp.status_code == 200:
                print(f"✅ 发布成功!")
                print(f"   Note ID: {data.get('note_id')}")
                print(f"   URL: {data.get('url')}")
                return data
            else:
                raise Exception(f"发布失败: {data}")
                
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            raise
    
    def publish(
        self,
        title: str,
        html_content: str,
        local_images: List[str],
        tags: List[str] = None
    ) -> Dict:
        """
        完整发布流程
        
        Args:
            title: 标题
            html_content: 渲染后的HTML内容
            local_images: 本地图片路径列表
            tags: 标签
        
        Returns:
            发布结果
        """
        # 1. 检查登录
        print("[1/3] 检查登录状态...")
        if not self.check_login():
            print("❌ 未登录，请先扫码登录")
            print(f"   访问: {self.mcp_url}/api/login-qrcode")
            raise Exception("未登录")
        
        # 2. 上传图片
        print(f"[2/3] 上传图片 ({len(local_images)}张)...")
        image_urls = self.upload_images(local_images)
        
        # 3. 发布
        print("[3/3] 发布笔记...")
        result = self.publish_note(
            title=title,
            content=html_content,
            images=image_urls,
            tags=tags
        )
        
        return result


def publish_to_xiaohongshu(
    title: str,
    html_content: str,
    image_paths: List[str],
    tags: List[str] = None,
    mcp_url: str = None
) -> Dict:
    """
    便捷函数：发布到小红书
    
    Usage:
        result = publish_to_xiaohongshu(
            title="标题",
            html_content="<p>内容</p>",
            image_paths=["/path/to/img1.jpg", "/path/to/img2.jpg"],
            tags=["#标签1", "#标签2"]
        )
    """
    publisher = XHSPublisher(mcp_url)
    return publisher.publish(title, html_content, image_paths, tags)


if __name__ == '__main__':
    # 测试
    publisher = XHSPublisher()
    
    # 检查登录
    if publisher.check_login():
        print("✅ 已登录")
    else:
        print("❌ 未登录")
        print("请访问:", publisher.mcp_url + "/api/login-qrcode")
        sys.exit(1)
