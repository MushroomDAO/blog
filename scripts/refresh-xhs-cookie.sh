#!/bin/bash
# ============================================================================
# 小红书 cookie 保活 —— 自动探测登录态在哪个 Chrome profile
# ----------------------------------------------------------------------------
# 背景：xhs CLI 的 cookie TTL 是 7 天，到期会尝试从浏览器自动刷新，但它的探测
# 只看每个浏览器的**默认 profile**。真实的小红书登录态往往在某个 sub-profile 里
# （MacBook 上是 Chrome "Profile 15"，账号 Mushroom.cv），于是每次都失败退回
# 「需要重新登录」—— 而且是静默的：你只会看到 forage 的小红书源为 0。
#
# 这个脚本绕开那套探测，直接读 profile 的 Cookies 库。cookie 存档超过 6 天才
# 真正刷新，稳定压在 7 天 TTL 红线之前，不需要人工扫码。
#
# 为什么改成自动探测（2026-09-10）：profile 编号是**每台机器不一样**的。
# 原来写死 "Profile 15" 是 MacBook 的编号，仓库搬到 Mac mini 后那个路径根本不存在，
# 换机就得改代码。现在遍历所有 profile 找哪个真有小红书 a1 cookie。
#
# 多个 profile 都登录了小红书时**不猜**：直接报错并列出候选，让人用
# XHS_CHROME_PROFILE 明确指定。猜错的后果是发到错误的小红书账号上去。
#
# 可选环境变量：
#   XHS_CHROME_PROFILE   明确指定 profile 名（如 "Profile 15" / "Default"）
#   XHS_REFRESH_DAYS     刷新阈值，默认 6 天
#
# crontab（21:15，避开整点/半点）：
#   15 21 * * * cd <repo> && PATH=... ./scripts/refresh-xhs-cookie.sh >> /tmp/xhs-cookie-refresh.log 2>&1
# ============================================================================
set -euo pipefail

REFRESH_THRESHOLD_DAYS="${XHS_REFRESH_DAYS:-6}"

# 找 xhs 的 python。pipx 的 venv 位置**不同机器不一样**：老版本在
# ~/.local/pipx/venvs（MacBook），新版本改成了 ~/Library/Application Support/pipx/venvs
# （Mac mini，brew 装的）。写死一个就必然在另一台上炸，所以按顺序探测，
# 并且优先问 pipx 自己。
find_venv_py() {
  [ -n "${XHS_VENV_PY:-}" ] && { echo "$XHS_VENV_PY"; return; }
  local base
  if command -v pipx >/dev/null 2>&1; then
    base=$(pipx environment --value PIPX_LOCAL_VENVS 2>/dev/null || true)
    [ -n "$base" ] && [ -x "$base/xiaohongshu-cli/bin/python" ] && { echo "$base/xiaohongshu-cli/bin/python"; return; }
  fi
  for base in "$HOME/.local/pipx/venvs" \
              "$HOME/Library/Application Support/pipx/venvs" \
              "$HOME/.local/share/pipx/venvs"; do
    [ -x "$base/xiaohongshu-cli/bin/python" ] && { echo "$base/xiaohongshu-cli/bin/python"; return; }
  done
  echo ""
}

VENV_PY="$(find_venv_py)"
if [ -z "$VENV_PY" ] || [ ! -x "$VENV_PY" ]; then
  echo "[error] 找不到 xhs 的 python（已试 pipx environment 和三个常见 venv 路径）"
  echo "        装：pipx install xiaohongshu-cli（或用 XHS_VENV_PY 指定绝对路径）"
  exit 1
fi

XHS_CHROME_PROFILE="${XHS_CHROME_PROFILE:-}" \
REFRESH_THRESHOLD_DAYS="$REFRESH_THRESHOLD_DAYS" \
"$VENV_PY" <<'PYEOF'
import glob
import json
import os
import sys
import time

import browser_cookie3 as bc3

THRESHOLD_DAYS = float(os.environ.get("REFRESH_THRESHOLD_DAYS", "6"))
FORCED_PROFILE = os.environ.get("XHS_CHROME_PROFILE") or ""

OUT_DIR = os.path.expanduser("~/.xiaohongshu-cli")
OUT_PATH = os.path.join(OUT_DIR, "cookies.json")
HINT_PATH = os.path.join(OUT_DIR, ".profile-hint")

CHROME_ROOTS = [
    os.path.expanduser("~/Library/Application Support/Google/Chrome"),
    os.path.expanduser("~/Library/Application Support/Google/Chrome Beta"),
    os.path.expanduser("~/Library/Application Support/Chromium"),
    os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser"),
    os.path.expanduser("~/Library/Application Support/Microsoft Edge"),
]


def read_profile(cookie_db):
    """从一个 profile 的 Cookies 库里读小红书 cookie。读不了就当没有。"""
    try:
        jar = bc3.chrome(cookie_file=cookie_db, domain_name=".xiaohongshu.com")
        return {c.name: c.value for c in jar}
    except Exception:
        # 库被锁、格式变了、没权限 —— 都不该让整个脚本挂掉，继续看下一个
        return {}


def candidates():
    """遍历所有浏览器的所有 profile，返回真有 a1 cookie 的那些。"""
    found = []
    for root in CHROME_ROOTS:
        if not os.path.isdir(root):
            continue
        for cookie_db in glob.glob(os.path.join(root, "*", "Cookies")):
            profile = os.path.basename(os.path.dirname(cookie_db))
            # Chrome 在 profile 同级放了一些非 profile 目录，它们没有 Cookies，
            # glob 已经过滤掉了；剩下的还可能有 "System Profile" 这种，一并试，
            # 反正判据是「有没有 a1」，试错成本只是一次读库。
            cookies = read_profile(cookie_db)
            if cookies.get("a1"):
                found.append((root, profile, cookie_db, cookies))
    return found


def main():
    # ---- 1. 够新就不刷 ----
    age = None
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH) as f:
                saved = json.load(f)
            age = time.time() - float(saved.get("saved_at", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            age = None
    if age is not None and age < THRESHOLD_DAYS * 86400:
        print(f"[skip] cookie 存档 {age/86400:.1f} 天，未到 {THRESHOLD_DAYS:g} 天阈值")
        return 0

    # ---- 2. 找 profile ----
    # 顺序：显式指定 > 上次成功的 profile > 全量扫描
    hint = ""
    if os.path.exists(HINT_PATH):
        try:
            hint = open(HINT_PATH).read().strip()
        except OSError:
            hint = ""

    picked = None
    for want in (FORCED_PROFILE, hint):
        if not want:
            continue
        for root in CHROME_ROOTS:
            db = os.path.join(root, want, "Cookies")
            if os.path.exists(db):
                cookies = read_profile(db)
                if cookies.get("a1"):
                    picked = (root, want, db, cookies)
                    break
        if picked:
            src = "指定" if want == FORCED_PROFILE else "上次成功的"
            print(f"[hit] 用{src} profile：{want}")
            break
        if want == FORCED_PROFILE:
            print(f"[warn] 指定的 profile「{want}」里没有小红书 a1 cookie，改为全量扫描")

    if not picked:
        found = candidates()
        if not found:
            print("[error] 所有浏览器 profile 里都没有小红书登录态。")
            print("        在浏览器里打开 https://www.xiaohongshu.com/ 登录一次（账号 Mushroom.cv），再跑本脚本。")
            print("        注意 xhs CLI 自己的探测只看默认 profile，登在别的 profile 里它是找不到的。")
            return 1
        if len(found) > 1:
            # 不猜。猜错就是发到别人的账号上去。
            print(f"[error] {len(found)} 个 profile 都有小红书登录态，不猜是哪个：")
            for root, profile, _db, cookies in found:
                print(f"          {os.path.basename(root)} / {profile}（{len(cookies)} 个 cookie）")
            print("        用 XHS_CHROME_PROFILE='<profile 名>' 明确指定。")
            return 1
        picked = found[0]
        print(f"[scan] 自动探测到：{os.path.basename(picked[0])} / {picked[1]}")

    root, profile, _db, cookies = picked

    # ---- 3. 落盘 ----
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = {**cookies, "saved_at": time.time()}
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    os.chmod(OUT_PATH, 0o600)
    try:
        with open(HINT_PATH, "w") as f:
            f.write(profile)
        os.chmod(HINT_PATH, 0o600)
    except OSError:
        pass  # 记不住就下次再扫，不该因此失败

    print(f"[ok] 从 {os.path.basename(root)} / {profile} 刷新了 {len(cookies)} 个 cookie -> {OUT_PATH}")
    return 0


sys.exit(main())
PYEOF
