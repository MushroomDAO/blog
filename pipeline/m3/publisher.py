#!/usr/bin/env python3
"""
Xiaohongshu Publisher - MCP API Client
基于 xpzouying/xiaohongshu-mcp 的 HTTP API 实现
"""

import os
import sys
import json
import requests
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 配置
DEFAULT_MCP_URL = "http://localhost:3456"
DEFAULT_TIMEOUT = 60


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    post_id: Optional[str] = None
    title: str = ""
    content: str = ""
    image_count: int = 0
    message: str = ""
    error_code: Optional[str] = None


@dataclass
class LoginStatus:
    """登录状态"""
    is_logged_in: bool
    username: Optional[str] = None
    error: Optional[str] = None


class XiaohongshuPublisher:
    """
    小红书发布客户端
    
    基于 xiaohongshu-mcp 的 HTTP API 实现
    参考: https://github.com/xpzouying/xiaohongshu-mcp
    """
    
    def __init__(self, mcp_url: str = None, timeout: int = DEFAULT_TIMEOUT):
        """
        初始化发布器
        
        Args:
            mcp_url: MCP 服务地址，默认从环境变量 XHS_MCP_URL 读取
            timeout: 请求超时时间（秒）
        """
        self.mcp_url = mcp_url or os.getenv('XHS_MCP_URL', DEFAULT_MCP_URL)
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认 headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    # ==================== 健康检查 ====================
    
    def health_check(self) -> Dict:
        """
        检查 MCP 服务健康状态
        
        Returns:
            健康检查响应
        """
        try:
            response = self.session.get(
                f"{self.mcp_url}/health",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}"
            }
    
    # ==================== 登录管理 ====================
    
    def check_login(self) -> LoginStatus:
        """
        检查登录状态
        
        Returns:
            LoginStatus 对象
        """
        try:
            response = self.session.get(
                f"{self.mcp_url}/api/v1/login/status",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                result = data.get('data', {})
                return LoginStatus(
                    is_logged_in=result.get('is_logged_in', False),
                    username=result.get('username')
                )
            else:
                return LoginStatus(
                    is_logged_in=False,
                    error=data.get('message', 'Unknown error')
                )
        except requests.exceptions.RequestException as e:
            return LoginStatus(
                is_logged_in=False,
                error=f"Request failed: {str(e)}"
            )
    
    def get_login_qrcode(self) -> Tuple[bool, Optional[str], Optional[bytes]]:
        """
        获取登录二维码
        
        Returns:
            (success, timeout_seconds, qr_image_bytes)
        """
        try:
            response = self.session.get(
                f"{self.mcp_url}/api/v1/login/qrcode",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                result = data.get('data', {})
                timeout = result.get('timeout', '300')
                img_base64 = result.get('img', '')
                
                # 解码 base64 图片
                if img_base64.startswith('data:image'):
                    img_base64 = img_base64.split(',')[1]
                
                img_bytes = base64.b64decode(img_base64) if img_base64 else None
                return True, timeout, img_bytes
            else:
                return False, None, None
        except Exception as e:
            print(f"❌ Failed to get QR code: {e}")
            return False, None, None
    
    def delete_cookies(self) -> bool:
        """
        删除 cookies，重置登录状态
        
        Returns:
            是否成功
        """
        try:
            response = self.session.delete(
                f"{self.mcp_url}/api/v1/login/cookies",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get('success', False)
        except Exception as e:
            print(f"❌ Failed to delete cookies: {e}")
            return False
    
    def save_qrcode(self, output_path: str = None) -> Optional[str]:
        """
        获取并保存二维码到文件
        
        Args:
            output_path: 保存路径，默认为 /tmp/xhs_qrcode.png
            
        Returns:
            保存的文件路径
        """
        success, timeout, img_bytes = self.get_login_qrcode()
        
        if not success or not img_bytes:
            print("❌ Failed to get QR code")
            return None
        
        output_path = output_path or "/tmp/xhs_qrcode.png"
        
        try:
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            print(f"✅ QR code saved to: {output_path}")
            print(f"⏰ Expires in: {timeout} seconds")
            print("📱 Please scan with Xiaohongshu APP")
            return output_path
        except Exception as e:
            print(f"❌ Failed to save QR code: {e}")
            return None
    
    # ==================== 内容发布 ====================
    
    def publish(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: List[str] = None,
        visibility: str = "公开可见",
        schedule_at: str = None,
        is_original: bool = False
    ) -> PublishResult:
        """
        发布图文内容到小红书
        
        Args:
            title: 标题（不超过 20 字）
            content: 正文内容（不超过 1000 字）
            images: 图片路径列表（至少 1 张，最多 9 张）
            tags: 标签列表（可选）
            visibility: 可见范围 - "公开可见"/"仅自己可见"/"仅互关好友可见"
            schedule_at: 定时发布时间（ISO8601 格式，可选，1小时-14天内）
            is_original: 是否声明原创（可选）
            
        Returns:
            PublishResult 对象
        """
        # 验证参数
        if len(title) > 20:
            print(f"⚠️  Title too long ({len(title)} chars), truncating to 20 chars")
            title = title[:20]
        
        if len(content) > 1000:
            print(f"⚠️  Content too long ({len(content)} chars), truncating to 1000 chars")
            content = content[:1000]
        
        if not images:
            return PublishResult(
                success=False,
                message="At least one image is required"
            )
        
        if len(images) > 9:
            print(f"⚠️  Too many images ({len(images)}), using first 9")
            images = images[:9]
        
        # 构建请求体
        payload = {
            "title": title,
            "content": content,
            "images": images,
            "visibility": visibility
        }
        
        if tags:
            payload["tags"] = tags
        
        if schedule_at:
            payload["schedule_at"] = schedule_at
        
        if is_original:
            payload["is_original"] = True
        
        try:
            response = self.session.post(
                f"{self.mcp_url}/api/v1/publish",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                result = data.get('data', {})
                return PublishResult(
                    success=True,
                    post_id=result.get('post_id'),
                    title=result.get('title', title),
                    content=result.get('content', content),
                    image_count=result.get('images', len(images)),
                    message=data.get('message', 'Published successfully')
                )
            else:
                return PublishResult(
                    success=False,
                    message=data.get('message', 'Unknown error'),
                    error_code=data.get('code')
                )
        
        except requests.exceptions.RequestException as e:
            return PublishResult(
                success=False,
                message=f"Request failed: {str(e)}"
            )
    
    def publish_video(
        self,
        title: str,
        content: str,
        video_path: str,
        tags: List[str] = None,
        visibility: str = "公开可见",
        schedule_at: str = None
    ) -> PublishResult:
        """
        发布视频内容到小红书
        
        Args:
            title: 标题
            content: 内容描述
            video_path: 本地视频文件绝对路径
            tags: 标签列表（可选）
            visibility: 可见范围
            schedule_at: 定时发布时间（可选）
            
        Returns:
            PublishResult 对象
        """
        if not os.path.exists(video_path):
            return PublishResult(
                success=False,
                message=f"Video file not found: {video_path}"
            )
        
        payload = {
            "title": title,
            "content": content,
            "video": video_path,
            "visibility": visibility
        }
        
        if tags:
            payload["tags"] = tags
        
        if schedule_at:
            payload["schedule_at"] = schedule_at
        
        try:
            response = self.session.post(
                f"{self.mcp_url}/api/v1/publish_video",
                json=payload,
                timeout=300  # 视频上传需要更长时间
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                result = data.get('data', {})
                return PublishResult(
                    success=True,
                    post_id=result.get('post_id'),
                    title=result.get('title', title),
                    message=data.get('message', 'Video published successfully')
                )
            else:
                return PublishResult(
                    success=False,
                    message=data.get('message', 'Unknown error'),
                    error_code=data.get('code')
                )
        
        except requests.exceptions.RequestException as e:
            return PublishResult(
                success=False,
                message=f"Request failed: {str(e)}"
            )
    
    # ==================== Feed 管理 ====================
    
    def list_feeds(self) -> Dict:
        """
        获取首页推荐列表
        
        Returns:
            API 响应数据
        """
        try:
            response = self.session.get(
                f"{self.mcp_url}/api/v1/feeds/list",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_feeds(
        self,
        keyword: str,
        sort_by: str = "综合",
        note_type: str = "不限",
        publish_time: str = "不限"
    ) -> Dict:
        """
        搜索内容
        
        Args:
            keyword: 搜索关键词
            sort_by: 排序 - "综合"/"最新"/"最多点赞"/"最多评论"/"最多收藏"
            note_type: 类型 - "不限"/"视频"/"图文"
            publish_time: 时间 - "不限"/"一天内"/"一周内"/"半年内"
            
        Returns:
            API 响应数据
        """
        try:
            payload = {
                "keyword": keyword,
                "filters": {
                    "sort_by": sort_by,
                    "note_type": note_type,
                    "publish_time": publish_time
                }
            }
            
            response = self.session.post(
                f"{self.mcp_url}/api/v1/feeds/search",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_feed_detail(
        self,
        feed_id: str,
        xsec_token: str,
        load_all_comments: bool = False
    ) -> Dict:
        """
        获取帖子详情
        
        Args:
            feed_id: 帖子 ID
            xsec_token: 安全令牌
            load_all_comments: 是否加载全部评论
            
        Returns:
            API 响应数据
        """
        try:
            payload = {
                "feed_id": feed_id,
                "xsec_token": xsec_token,
                "load_all_comments": load_all_comments
            }
            
            response = self.session.post(
                f"{self.mcp_url}/api/v1/feeds/detail",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== 评论管理 ====================
    
    def post_comment(
        self,
        feed_id: str,
        xsec_token: str,
        content: str
    ) -> Dict:
        """
        发表评论
        
        Args:
            feed_id: 帖子 ID
            xsec_token: 安全令牌
            content: 评论内容
            
        Returns:
            API 响应数据
        """
        try:
            payload = {
                "feed_id": feed_id,
                "xsec_token": xsec_token,
                "content": content
            }
            
            response = self.session.post(
                f"{self.mcp_url}/api/v1/feeds/comment",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== 用户信息 ====================
    
    def get_my_profile(self) -> Dict:
        """
        获取当前登录用户信息
        
        Returns:
            API 响应数据
        """
        try:
            response = self.session.get(
                f"{self.mcp_url}/api/v1/user/me",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_profile(self, user_id: str, xsec_token: str) -> Dict:
        """
        获取指定用户主页信息
        
        Args:
            user_id: 用户 ID
            xsec_token: 安全令牌
            
        Returns:
            API 响应数据
        """
        try:
            payload = {
                "user_id": user_id,
                "xsec_token": xsec_token
            }
            
            response = self.session.post(
                f"{self.mcp_url}/api/v1/user/profile",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}


# ==================== CLI 入口 ====================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Xiaohongshu Publisher')
    parser.add_argument('--url', default=None, help='MCP URL')
    parser.add_argument('--test', action='store_true', help='Run connection test')
    parser.add_argument('--qrcode', action='store_true', help='Get login QR code')
    
    # 发布相关
    parser.add_argument('--title', help='Post title')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--images', nargs='+', help='Image paths')
    parser.add_argument('--tags', nargs='+', help='Tags')
    parser.add_argument('--publish', action='store_true', help='Publish content')
    
    args = parser.parse_args()
    
    publisher = XiaohongshuPublisher(mcp_url=args.url)
    
    if args.test:
        # 运行连接测试
        print("🧪 Testing MCP connection...")
        health = publisher.health_check()
        print(f"Health: {json.dumps(health, indent=2, ensure_ascii=False)}")
        
        login = publisher.check_login()
        print(f"\nLogin status: {login.is_logged_in}")
        if login.username:
            print(f"Username: {login.username}")
        if login.error:
            print(f"Error: {login.error}")
    
    elif args.qrcode:
        # 获取二维码
        path = publisher.save_qrcode()
        if path:
            print(f"\n✅ QR code saved to: {path}")
    
    elif args.publish:
        # 发布内容
        if not args.title or not args.content or not args.images:
            print("❌ --title, --content, and --images are required for publishing")
            sys.exit(1)
        
        result = publisher.publish(
            title=args.title,
            content=args.content,
            images=args.images,
            tags=args.tags
        )
        
        print(f"\nPublish result:")
        print(f"  Success: {result.success}")
        print(f"  Post ID: {result.post_id}")
        print(f"  Message: {result.message}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
