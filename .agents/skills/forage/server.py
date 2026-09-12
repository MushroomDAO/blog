#!/usr/bin/env python3
"""forage 本地评审服务。

只用标准库，无依赖。默认起在 127.0.0.1；FORAGE_HOST 可改（见下）。

    python3 .agents/skills/forage/server.py        # 默认 842 端口，自动开浏览器

页面上的每一次打分、每一个决定、每一条备注都直接写 SQLite，
所以我随时能读到你的判断 —— 不用你复制粘贴。
"""
import http.server, json, os, re, shutil, sqlite3, subprocess, sys, threading, webbrowser
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import DB, DIMS, conn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "write"))
import job as write_job

PORT = int(os.environ.get("FORAGE_PORT", "8042"))
# 默认仍然只绑 127.0.0.1（不对外）。但 forage 采集搬到 Mac mini 之后，
# radar/forage.db 在那台机器上，评审台也必须在那台机器上跑 —— 绑死 127.0.0.1
# 就意味着你在 MacBook 上打不开它。所以留一个口子：FORAGE_HOST 设成
# Tailscale IP，就只在自己的 tailnet 内可达（不是公网）。
# 不想开这个口子的话，用 SSH 隧道也行：
#   ssh -L 8042:127.0.0.1:8042 jason@<mac-mini>
HOST = os.environ.get("FORAGE_HOST", "127.0.0.1")
HERE = os.path.dirname(os.path.abspath(__file__))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_items(run=None):
    c = conn()
    q = "SELECT * FROM items"
    args = ()
    if run:
        q += " WHERE run_date=?"; args = (run,)
    q += " ORDER BY COALESCE(ai_total, auto_score) DESC"
    rows = [dict(r) for r in c.execute(q, args)]
    for r in rows:
        for k in ("hits", "research"):
            if r.get(k):
                try: r[k] = json.loads(r[k])
                except Exception: r[k] = []
    return rows


# ---- 「开始写」按钮 ----------------------------------------------------------
# 评审完一按，拉起一个后台 Claude Code 会话（claude --bg）按 write/WRITE-JOB.md
# 把标了「写」的条目写完、发布。不需要任何会话常驻：这个服务本来就是
# LaunchAgent 常驻的，它负责拉起；后台会话自己跑完就退出，用 `claude attach <id>`
# 可以随时接进去看。
#
# 权限：用 auto 模式，不用 bypassPermissions。这个页面没有登录，tailnet 里谁都能按，
# 按钮背后不能挂一个无限制的 agent。发布流程固定用的命令在 .claude/settings.local.json
# 里放行，超出范围的由 auto 模式的安全审核把关。
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STALE_HOURS = 8  # 跑超过这么久还没收尾，页面提示「可能卡住了」
START_LOCK = threading.Lock()  # ThreadingHTTPServer：双击会并发进来两次


def job_status():
    j = write_job.read()
    if j.get("state") == "running":
        try:
            started = datetime.fromisoformat(j["started"])
            j["hours"] = round((datetime.now(timezone.utc) - started).total_seconds() / 3600, 1)
            j["stale"] = j["hours"] >= STALE_HOURS
        except (KeyError, ValueError):
            pass
    return j


def start_write_job():
    j = write_job.read()
    if j.get("state") == "running" and not job_status().get("stale"):
        return 409, {"error": "已经有一个写作任务在跑", "job": j}
    c = conn()
    items = [dict(r) for r in c.execute(
        "SELECT id, title FROM items WHERE decision='write' ORDER BY updated_at")]
    if not items:
        return 400, {"error": "没有标「写」的条目"}
    undecided = c.execute("SELECT COUNT(*) FROM items WHERE decision IS NULL OR decision=''").fetchone()[0]

    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    today = datetime.now().strftime("%Y%m%d")
    prompt = (f"读 .agents/skills/forage/write/WRITE-JOB.md 并严格按它执行：用户已在 8042 评审台判完，"
              f"把 {len(items)} 条标了「写」的条目全部写完并发布（blog + 公众号草稿）。"
              f"全程中文汇报，结束时必须用 job.py done 或 fail 收尾。")
    try:
        r = subprocess.run([claude, "--bg", "--permission-mode", "auto",
                            "-n", f"forage-write-{today}", prompt],
                           cwd=ROOT, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 500, {"error": f"拉起 claude 失败：{e}"}
    out = (r.stdout or "") + (r.stderr or "")
    # 形如「backgrounded · 8f2eef3b · forage-write-20260912」
    m = re.search(r"backgrounded\s*·\s*([0-9a-f]{6,})", out)
    if r.returncode != 0 or not m:
        return 500, {"error": "claude --bg 没有返回会话 id", "output": out[-800:]}
    j = {"state": "running", "session": m.group(1), "started": now(),
         "count": len(items), "titles": [i["title"] for i in items],
         "undecided_left": undecided, "log": []}
    write_job.write(j)
    return 200, j


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # 别把终端刷满

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            return self._send(200, open(os.path.join(HERE, "review.html"), "rb").read(),
                              "text/html; charset=utf-8")
        if p == "/api/items":
            return self._send(200, json.dumps({"items": fetch_items(), "dims": DIMS},
                                              ensure_ascii=False))
        if p == "/api/summary":
            c = conn()
            s = {"total": c.execute("SELECT COUNT(*) FROM items").fetchone()[0]}
            for r in c.execute("SELECT decision, COUNT(*) n FROM items GROUP BY decision"):
                s[r["decision"] or "undecided"] = r["n"]
            s["rated"] = c.execute("SELECT COUNT(*) FROM items WHERE u_total IS NOT NULL").fetchone()[0]
            return self._send(200, json.dumps(s, ensure_ascii=False))
        if p == "/api/job":
            return self._send(200, json.dumps(job_status(), ensure_ascii=False))
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        p = urlparse(self.path).path
        if p == "/api/job/start":
            # 别的网站可以用 text/plain 表单跨站 POST 过来（不触发 CORS 预检）。
            # 要求一个自定义头，浏览器跨站发不了它，只有本页的 fetch 带得上。
            if self.headers.get("X-Forage") != "1":
                return self._send(403, json.dumps({"error": "forbidden"}))
            with START_LOCK:
                code, body = start_write_job()
            return self._send(code, json.dumps(body, ensure_ascii=False))
        n = int(self.headers.get("Content-Length", 0))
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, json.dumps({"error": "bad json"}))

        c = conn()
        iid = d.get("id")
        if not iid:
            return self._send(400, json.dumps({"error": "missing id"}))

        if p == "/api/rate":
            # 允许只打部分维度；未给的保持原值
            sets, args = [], []
            total = 0
            for key, _, _ in DIMS:
                col = f"u_{key}"
                if key in d:
                    v = max(0, min(20, int(d[key])))
                    sets.append(f"{col}=?"); args.append(v)
            row = c.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
            if not row:
                return self._send(404, json.dumps({"error": "no such item"}))
            # 未打分的维度回落到我的分数。否则只拖一根滑块，总分会被算成
            # 「只有那一维」，和我的 100 分制不可比，校准信号直接失真。
            merged = {}
            for key, _, _ in DIMS:
                if key in d:
                    merged[key] = max(0, min(20, int(d[key])))
                elif row[f"u_{key}"] is not None:
                    merged[key] = row[f"u_{key}"]
                else:
                    merged[key] = row[f"ai_{key}"] or 0
            total = sum(merged.values())
            # 回落值也要落库，不然下次读出来还是 NULL
            for key, _, _ in DIMS:
                if key not in d and row[f"u_{key}"] is None:
                    sets.append(f"u_{key}=?"); args.append(merged[key])
            sets.append("u_total=?"); args.append(total)
            if "note" in d:
                sets.append("u_note=?"); args.append(d["note"])
            sets.append("updated_at=?"); args.append(now())
            args.append(iid)
            c.execute(f"UPDATE items SET {','.join(sets)} WHERE id=?", args)
            c.commit()
            return self._send(200, json.dumps({"ok": True, "u_total": total}))

        if p == "/api/decide":
            c.execute("UPDATE items SET decision=?, updated_at=? WHERE id=?",
                      (d.get("decision", ""), now(), iid))
            c.commit()
            return self._send(200, json.dumps({"ok": True}))

        return self._send(404, json.dumps({"error": "not found"}))


def main():
    if not os.path.exists(DB):
        print("库不存在，先跑：python3 .agents/skills/forage/store.py init")
        sys.exit(1)
    srv = http.server.ThreadingHTTPServer((HOST, PORT), H)
    url = f"http://{HOST}:{PORT}/"
    # 把真实监听地址落盘，让健康检查去读，而不是各处硬编码 127.0.0.1。
    # 2026-09-10 踩到：服务改绑 Tailscale IP 之后，run-daily.sh 还在 curl
    # 127.0.0.1，于是每晚误报「评审台没起来」——配置漂移的典型形态。
    try:
        marker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "radar", ".server-url")
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        with open(marker, "w", encoding="utf-8") as f:
            f.write(url)
    except OSError:
        pass  # 落不下就落不下，不该因此不给服务
    print(f"forage 评审台 → {url}")
    print(f"库：{DB}")
    print("打分和决定实时落库。Ctrl-C 停止。")
    # 常驻服务（LaunchAgent）不该每次重启都弹浏览器
    if not os.environ.get("FORAGE_NO_BROWSER"):
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
