#!/usr/bin/env python3
"""从小红书 MCP 服务获取登录二维码，在终端渲染 + 打开 Preview"""
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

def decode_image(img_data_url: str):
    _, b64 = img_data_url.split(",", 1)
    return Image.open(BytesIO(base64.b64decode(b64))).convert("L")

def detect_module_size(img: Image.Image) -> int:
    """通过扫描中间行找第一个黑色 run 的宽度，推断单个模块像素数"""
    w, h = img.size
    pixels = img.load()
    mid_y = h // 2

    # 找第一个黑色像素
    start = None
    for x in range(w):
        if pixels[x, mid_y] < 128:
            start = x
            break
    if start is None:
        return 4  # 默认值

    # 找第一个黑色 run 的结束
    end = start
    for x in range(start, w):
        if pixels[x, mid_y] >= 128:
            end = x
            break

    return max(1, end - start)

def render_terminal(img: Image.Image):
    """按模块边界采样，用 ANSI 颜色正确渲染 QR（可扫）"""
    BLACK = "\033[40m"    # 黑底
    WHITE = "\033[107m"   # 亮白底
    RESET = "\033[0m"

    w, h = img.size
    mod = detect_module_size(img)
    cols = w // mod
    rows = h // mod

    pixels = img.load()

    quiet = WHITE + "    " + "  " * cols + "    " + RESET
    print(quiet)
    for row in range(rows):
        y = int((row + 0.5) * mod)
        line = WHITE + "    " + RESET
        for col in range(cols):
            x = int((col + 0.5) * mod)
            dark = pixels[x, y] < 128
            line += (BLACK if dark else WHITE) + "  " + RESET
        line += WHITE + "    " + RESET
        print(line)
    print(quiet)

def save_and_open_png(img_data_url: str) -> str:
    """保存 PNG 到临时文件并用 Preview 打开"""
    _, b64 = img_data_url.split(",", 1)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="xhs_qrcode_")
    tmp.write(base64.b64decode(b64))
    tmp.close()
    subprocess.Popen(["open", tmp.name])
    print(f"[Preview 已打开，也可手动查看: {tmp.name}]")
    return tmp.name

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
    img = decode_image(img_url)

    render_terminal(img)
    tmp_path = save_and_open_png(img_url)

    wait_for_login()

    try:
        os.unlink(tmp_path)
    except Exception:
        pass
