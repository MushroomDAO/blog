#!/usr/bin/env python3
"""
图片压缩器 - 压缩到目标大小 (~200KB)

参考 blog-publisher skill 的图片处理方式
"""

import subprocess
import os
from pathlib import Path


def compress_image(input_path: str, output_path: str, target_size_kb: int = 200, 
                   target_width: int = 900, target_height: int = 1200) -> str:
    """
    压缩图片到目标大小
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size_kb: 目标大小 (KB)，默认 200KB
        target_width: 目标宽度，小红书推荐 900
        target_height: 目标高度，小红书推荐 1200
    
    Returns:
        输出文件路径
    """
    qualities = [85, 75, 65, 55, 45]  # 从高质量开始尝试
    
    for quality in qualities:
        cmd = [
            'convert', input_path,
            '-resize', f'{target_width}x{target_height}^',
            '-gravity', 'center',
            '-extent', f'{target_width}x{target_height}',
            '-quality', str(quality),
            '-strip',  # 移除元数据
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 检查文件大小
            size_kb = os.path.getsize(output_path) / 1024
            
            if size_kb <= target_size_kb:
                print(f"  ✅ 压缩成功: {size_kb:.1f}KB (quality={quality})")
                return output_path
            else:
                print(f"  ⚠️  仍太大: {size_kb:.1f}KB (quality={quality})，继续降低质量...")
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 压缩失败 (quality={quality}): {e}")
            continue
    
    # 如果都失败了，返回最后一个尝试的结果
    print(f"  ⚠️  警告：无法压缩到 {target_size_kb}KB 以下，使用最低质量")
    return output_path


def compress_for_xiaohongshu(input_path: str, output_dir: str = "/tmp/xhs_images") -> str:
    """
    专为小红书压缩图片
    
    小红书要求：
    - 3:4 比例 (900x1200)
    - 文件大小建议 < 200KB（避免上传超时）
    
    Args:
        input_path: 输入图片路径
        output_dir: 输出目录
    
    Returns:
        压缩后的图片路径
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    filename = Path(input_path).stem
    output_path = os.path.join(output_dir, f"{filename}_xhs.jpg")
    
    return compress_image(
        input_path=input_path,
        output_path=output_path,
        target_size_kb=200,
        target_width=900,
        target_height=1200
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python image_compressor.py <input_image> [output_path]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = f"/tmp/{Path(input_file).stem}_compressed.jpg"
    
    result = compress_image(input_file, output_file)
    
    if result:
        size_kb = os.path.getsize(result) / 1024
        print(f"\n✅ 完成: {result} ({size_kb:.1f}KB)")
    else:
        print("\n❌ 失败")
        sys.exit(1)
