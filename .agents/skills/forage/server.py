#!/usr/bin/env python3
"""forage 本地评审服务。

只用标准库，无依赖。起在 127.0.0.1，不对外。

    python3 .agents/skills/forage/server.py        # 默认 842 端口，自动开浏览器

页面上的每一次打分、每一个决定、每一条备注都直接写 SQLite，
所以我随时能读到你的判断 —— 不用你复制粘贴。
"""
import http.server, json, os, sqlite3, sys, threading, webbrowser
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import DB, DIMS, conn

PORT = int(os.environ.get("FORAGE_PORT", "8042"))
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
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        p = urlparse(self.path).path
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
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
    url = f"http://127.0.0.1:{PORT}/"
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
