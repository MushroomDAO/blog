#!/usr/bin/env python3
"""评审台「开始写」任务的状态文件（radar/write-job.json）。

server.py 起任务时写 running；后台 Claude 会话在跑的过程中用这个脚本汇报：

    python3 .agents/skills/forage/write/job.py progress "k2-horizon 已发布"
    python3 .agents/skills/forage/write/job.py done "发了 8 篇，跳过 1 篇（重复）"
    python3 .agents/skills/forage/write/job.py fail "build 挂了：…"

页面每隔一会儿读一次，所以你在 MacBook 上也能看到进度，不用 attach。
"""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
JOB = os.path.join(ROOT, "radar", "write-job.json")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read():
    try:
        with open(JOB, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"state": "idle"}


def write(job):
    os.makedirs(os.path.dirname(JOB), exist_ok=True)
    tmp = JOB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    os.replace(tmp, JOB)  # 原子替换，页面不会读到写了一半的 JSON


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("progress", "done", "fail"):
        print(__doc__)
        sys.exit(1)
    cmd, msg = sys.argv[1], " ".join(sys.argv[2:])
    job = read()
    job.setdefault("log", []).append({"at": now(), "msg": msg})
    if cmd == "done":
        job["state"], job["finished"], job["summary"] = "done", now(), msg
    elif cmd == "fail":
        job["state"], job["finished"], job["summary"] = "failed", now(), msg
    write(job)
    print(f"write-job: {cmd} — {msg}")


if __name__ == "__main__":
    main()
