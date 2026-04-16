#!/usr/bin/env python3
"""从小红书 MCP 服务获取登录二维码，保存为图片并在终端渲染"""
import sys
import json
import base64
import time
import subprocess
import tempfile
import os
import urllib.request
from io import BytesIO
from PIL import Image

HOST = "http://localhost:3456"

def fetch_json(url, timeout=90):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(1)

def fetch_qrcode():
    print("正在获取二维码，请稍候...", flush=True)
    data = fetch_json(f"{HOST}/api/v1/login/qrcode")
    if not data.get("success"):
        print(f"服务返回错误: {data}", file=sys.stderr)
        sys.exit(1)
    if data["data"].get("is_logged_in"):
        print("已登录，无需扫码")
        sys.exit(0)
    return data["data"]["img"]

def save_and_open_png(img_data_url: str) -> str:
    """保存 PNG 到临时文件并用系统默认程序打开"""
    _, b64 = img_data_url.split(",", 1)
    png_data = base64.b64decode(b64)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="xhs_qrcode_")
    tmp.write(png_data)
    tmp.close()
    subprocess.Popen(["open", tmp.name])  # macOS: 用 Preview 打开
    print(f"二维码图片已用 Preview 打开，也可手动查看: {tmp.name}")
    return tmp.name

def render_terminal(img_data_url: str, size: int = 41):
    """用 ANSI 颜色在终端渲染（黑白对比，适合扫码）"""
    BLACK = "\033[40m"   # 黑底
    WHITE = "\033[107m"  # 亮白底
    RESET = "\033[0m"

    _, b64 = img_data_url.split(",", 1)
    img = Image.open(BytesIO(base64.b64decode(b64))).convert("1")
    img = img.resize((size, size), Image.NEAREST)
    pixels = img.load()

    # 上安静区（白色）
    quiet = WHITE + "  " * (size + 4) + RESET
    print(quiet)
    for y in range(size):
        row = WHITE + "    " + RESET  # 左安静区
        for x in range(size):
            # pixels==0 是黑色模块，pixels!=0 是白色模块
            row += (BLACK if pixels[x, y] == 0 else WHITE) + "  " + RESET
        row += WHITE + "    " + RESET  # 右安静区
        print(row)
    print(quiet)  # 下安静区

def wait_for_login(timeout=240):
    print("\n请用小红书 App 扫描二维码，扫码后在手机上点确认登录...")
    print("等待登录中", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(3)
        data = fetch_json(f"{HOST}/api/v1/login/status", timeout=10)
        if data.get("success") and data.get("data", {}).get("is_logged_in"):
            print("\n✅ 登录成功！")
            return True
        print(".", end="", flush=True)
    print("\n⏰ 等待超时，请重新运行脚本")
    return False

if __name__ == "__main__":
    img_url = fetch_qrcode()

    # 1. 终端渲染（带正确颜色）
    render_terminal(img_url)

    # 2. 同时用 Preview 打开（更易扫码）
    tmp_path = save_and_open_png(img_url)

    wait_for_login()

    # 清理临时文件
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
