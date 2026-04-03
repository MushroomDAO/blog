#!/usr/bin/env python3
"""
M1: Blog Publisher
将 Markdown 文章发布到 Astro Blog
流程：保存文件 → Build → Deploy
"""

import os
import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# 配置
BLOG_ROOT = Path(__file__).parent.parent.parent
CONTENT_DIR = BLOG_ROOT / "src" / "content" / "blog"
ASSETS_DIR = BLOG_ROOT / "src" / "assets"


def sanitize_filename(title: str) -> str:
    """将标题转换为安全的文件名"""
    # 移除或替换特殊字符
    filename = re.sub(r'[^\w\u4e00-\u9fa5\s]', '-', title)
    filename = re.sub(r'-+', '-', filename).strip('-')
    filename = re.sub(r'\s+', '-', filename)
    return filename[:50].lower()


def save_article(markdown_content: str, filename: str = None) -> Path:
    """保存文章到 blog 目录"""
    # 从 frontmatter 提取标题
    title_match = re.search(r"title:\s*['\"]?([^'\"\n]+)", markdown_content)
    if title_match and not filename:
        title = title_match.group(1)
        filename = sanitize_filename(title) + ".md"
    elif not filename:
        filename = f"article-{datetime.now().strftime('%Y%m%d')}.md"
    
    # 确保目录存在
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = CONTENT_DIR / filename
    
    # 检查文件是否存在
    if filepath.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{filename[:-3]}-{timestamp}.md"
        filepath = CONTENT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Article saved: {filepath}")
    return filepath


def process_images(article_path: Path, image_paths: list = None) -> str:
    """处理文章中的图片，复制到 assets 目录"""
    if not image_paths:
        return None
    
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    cover_image = None
    for i, img_path in enumerate(image_paths):
        src = Path(img_path)
        if src.exists():
            # 生成目标文件名
            ext = src.suffix
            if i == 0:
                dst_name = f"blog-cover-{datetime.now().strftime('%Y%m%d')}{ext}"
                cover_image = f"../../assets/{dst_name}"
            else:
                dst_name = f"blog-img-{datetime.now().strftime('%Y%m%d')}-{i}{ext}"
            
            dst = ASSETS_DIR / dst_name
            shutil.copy2(src, dst)
            print(f"✅ Image copied: {dst}")
    
    return cover_image


def build_blog() -> bool:
    """执行 pnpm build"""
    print("\n🔨 Building blog...")
    try:
        result = subprocess.run(
            ["pnpm", "build"],
            cwd=BLOG_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Build successful")
            return True
        else:
            print(f"❌ Build failed:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Build timeout")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False


def deploy_blog() -> bool:
    """执行 deploy"""
    print("\n🚀 Deploying blog...")
    try:
        result = subprocess.run(
            ["npx", "wrangler", "pages", "deploy", "dist", "--commit-dirty=true"],
            cwd=BLOG_ROOT,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            # 提取预览 URL
            url_match = re.search(r'https://[\w.-]+\.pages\.dev', result.stdout)
            if url_match:
                print(f"✅ Deployed: {url_match.group()}")
            else:
                print("✅ Deployed successfully")
            return True
        else:
            print(f"❌ Deploy failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Deploy error: {e}")
        return False


def publish(
    markdown_content: str,
    image_paths: list = None,
    skip_build: bool = False,
    skip_deploy: bool = False
) -> dict:
    """
    完整的发布流程
    
    Returns:
        {
            "success": bool,
            "article_path": Path,
            "build_success": bool,
            "deploy_success": bool,
            "preview_url": str
        }
    """
    result = {
        "success": False,
        "article_path": None,
        "build_success": False,
        "deploy_success": False,
        "preview_url": None
    }
    
    # 1. 保存文章
    article_path = save_article(markdown_content)
    result["article_path"] = article_path
    
    # 2. 处理图片
    if image_paths:
        cover = process_images(article_path, image_paths)
        if cover:
            # 在 frontmatter 中添加 heroImage
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已有 heroImage
            if 'heroImage:' not in content:
                content = content.replace(
                    '---\n',
                    f'---\nheroImage: \'{cover}\'\n',
                    1
                )
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    # 3. Build
    if not skip_build:
        result["build_success"] = build_blog()
        if not result["build_success"]:
            return result
    
    # 4. Deploy
    if not skip_deploy:
        result["deploy_success"] = deploy_blog()
        result["success"] = result["deploy_success"]
    else:
        result["success"] = True
    
    return result


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='M1 Blog Publisher')
    parser.add_argument('markdown_file', help='Path to markdown file')
    parser.add_argument('--images', nargs='+', help='Image paths')
    parser.add_argument('--skip-build', action='store_true', help='Skip build step')
    parser.add_argument('--skip-deploy', action='store_true', help='Skip deploy step')
    
    args = parser.parse_args()
    
    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = publish(
        content,
        image_paths=args.images,
        skip_build=args.skip_build,
        skip_deploy=args.skip_deploy
    )
    
    print(f"\n{'='*50}")
    print(f"Success: {result['success']}")
    print(f"Article: {result['article_path']}")
    print(f"Build: {result['build_success']}")
    print(f"Deploy: {result['deploy_success']}")
