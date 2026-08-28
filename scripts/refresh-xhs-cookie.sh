#!/bin/bash
# 小红书 cookie 保活：xhs_cli 的 cookie TTL 是 7 天，到期后它会尝试自动从浏览器刷新，
# 但它的浏览器自动探测只看每个浏览器的默认 profile，读不到小红书登录态实际所在的
# Chrome "Profile 15"（账号 Mushroom.cv），于是每次都会失败退回"需要重新登录"。
# 这个脚本绕开那个探测逻辑，直接从 Profile 15 的 Cookies 库里读，每天跑一次，
# cookie 存档超过 6 天才真正刷新，把它稳定压在 7 天 TTL 红线之前，不需要人工重新扫码。
#
# crontab（跟本仓库其它每日任务一起，21:15 跑，避开整点/半点）：
#   15 21 * * * cd /Users/jason/Dev/mycelium/blog && PATH=/Users/jason/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin ./scripts/refresh-xhs-cookie.sh >> /tmp/xhs-cookie-refresh.log 2>&1

set -euo pipefail

VENV_PY="/Users/jason/.local/pipx/venvs/xiaohongshu-cli/bin/python"
CHROME_COOKIE_DB="/Users/jason/Library/Application Support/Google/Chrome/Profile 15/Cookies"
REFRESH_THRESHOLD_DAYS=6

"$VENV_PY" <<PYEOF
import json, os, time
import browser_cookie3 as bc3

cookie_file = "$CHROME_COOKIE_DB"
threshold_seconds = $REFRESH_THRESHOLD_DAYS * 86400
out_dir = os.path.expanduser("~/.xiaohongshu-cli")
out_path = os.path.join(out_dir, "cookies.json")

age = None
if os.path.exists(out_path):
    try:
        with open(out_path) as f:
            saved = json.load(f)
        age = time.time() - float(saved.get("saved_at", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        age = None

if age is not None and age < threshold_seconds:
    print(f"[skip] cookie is {age/86400:.1f}d old, below {$REFRESH_THRESHOLD_DAYS}d threshold")
    raise SystemExit(0)

jar = bc3.chrome(cookie_file=cookie_file, domain_name=".xiaohongshu.com")
cookies = {c.name: c.value for c in jar}
if not cookies.get("a1"):
    print("[error] no a1 cookie found in Chrome Profile 15 — xiaohongshu session may have logged out, needs manual re-login")
    raise SystemExit(1)

os.makedirs(out_dir, exist_ok=True)
payload = {**cookies, "saved_at": time.time()}
with open(out_path, "w") as f:
    json.dump(payload, f, indent=2)
os.chmod(out_path, 0o600)
print(f"[ok] refreshed {len(cookies)} cookies -> {out_path}")
PYEOF
