#!/usr/bin/env python3
"""mage.py — 本地 Mage-VL 服务的命令行客户端。

只用标准库，不需要激活任何 venv。服务本身跑在 MAGE_VL_HOME 指向的仓库里。

用法:
    mage.py status
    mage.py up [--timeout 300]
    mage.py down
    mage.py image <文件> -q "问题" [--quality quick|balanced|high] [--max-tokens N]
    mage.py video <文件> -q "问题" [--backend dcvc|frames] [--frames N] [--max-tokens N]
    mage.py stream <文件> -q "解说指令" [--segment-sec S] [--max-segments N] [--max-tokens N]
"""

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HOME = Path(
    os.environ.get(
        "MAGE_VL_HOME",
        "/Users/jason/Dev/tools/model-download-tool/vendor/mage-vl-local-mac",
    )
).expanduser()
# 前端只绑 IPv4；本机还有别的服务占着 *:3000 的 IPv6 通配地址，所以一律用 127.0.0.1。
BASE = os.environ.get("MAGE_VL_API", "http://127.0.0.1:8000")


def api_status(timeout=4):
    """返回 /api/status 的 dict，服务没起来时返回 None。"""
    try:
        with urllib.request.urlopen(BASE + "/api/status", timeout=timeout) as resp:
            return json.load(resp)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def ensure_ready(timeout=300, quiet=False):
    """确保服务处于 ready。必要时拉起 start.command 并等模型加载完。"""
    status = api_status()
    if status and status.get("state") == "ready":
        return status

    if status is None:
        if not (HOME / "start.command").exists():
            sys.exit("找不到 %s/start.command，请检查 MAGE_VL_HOME" % HOME)
        logs = HOME / "logs"
        logs.mkdir(exist_ok=True)
        log_path = logs / "start-cli.log"
        if not quiet:
            print("服务未运行，正在启动… (日志: %s)" % log_path, file=sys.stderr)
        with log_path.open("ab") as log:
            subprocess.Popen(
                ["./start.command"],
                cwd=str(HOME),
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        status = api_status()
        if status:
            state = status.get("state")
            if state == "ready":
                if not quiet:
                    print("模型已就绪 (%s/%s)" % (status.get("model_device"), status.get("model_dtype")), file=sys.stderr)
                return status
            if state == "error":
                sys.exit("服务启动失败: %s" % status.get("message"))
            msg = status.get("message", "")
            if msg != last and not quiet:
                print("… %s" % msg, file=sys.stderr)
                last = msg
        time.sleep(3)
    sys.exit("等待 %ds 后服务仍未就绪，请看 %s/logs/backend.log" % (timeout, HOME))


def post_job(mode, file_path, fields):
    """以 multipart/form-data 提交任务，返回 job_id。"""
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        sys.exit("文件不存在: %s" % path)

    boundary = "----mage" + uuid.uuid4().hex
    parts = []
    for key, value in [("mode", mode)] + list(fields.items()):
        parts.append(
            ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, key, value)).encode()
        )
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    parts.append(
        (
            '--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
            "Content-Type: %s\r\n\r\n" % (boundary, path.name, ctype)
        ).encode()
    )
    parts.append(path.read_bytes())
    parts.append(("\r\n--%s--\r\n" % boundary).encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        BASE + "/api/jobs",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)["job_id"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        sys.exit("提交失败 HTTP %s: %s" % (exc.code, detail))


def follow(job_id, show_tokens=True):
    """读 SSE 事件流直到 result / error，返回 result dict。"""
    url = "%s/api/jobs/%s/events" % (BASE, job_id)
    # 视频任务可能跑几分钟，不设读超时上限
    with urllib.request.urlopen(url, timeout=None) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data: "):
                continue
            event = json.loads(line[6:])
            kind = event.get("type")
            if kind == "progress":
                print("[%3s%%] %s" % (event.get("progress", "?"), event.get("message", "")), file=sys.stderr)
            elif kind == "token" and show_tokens:
                sys.stderr.write(event.get("delta", ""))
                sys.stderr.flush()
            elif kind == "timeline":
                for entry in event.get("timeline", []):
                    print(
                        "\n[%s] %s" % (entry.get("label") or entry.get("time") or "段", entry.get("text", "")),
                        file=sys.stderr,
                    )
            elif kind == "error":
                sys.exit("\n任务失败: %s" % event.get("message"))
            elif kind == "result":
                sys.stderr.write("\n")
                return event.get("result", {})
    sys.exit("事件流意外结束，未收到结果")


def report(result):
    """把结果打到 stdout：正文优先，统计信息附后。"""
    answer = result.get("answer")
    if answer:
        print(answer)
    timeline = result.get("timeline")
    if timeline:
        for entry in timeline:
            print("[%s] %s" % (entry.get("label") or entry.get("time") or "-", entry.get("text", "")))
    stats = result.get("stats")
    if stats:
        print("\n--- stats ---")
        for key, value in stats.items():
            print("%-16s %s" % (key, value))
    gallery = result.get("gallery")
    if gallery:
        print("\n%d 张 canvas/帧 已生成，可用 %s<路径> 取回" % (len(gallery), BASE))


def save_gallery(result, out_dir):
    """把任务产出的 canvas/帧下载到本地目录。"""
    gallery = result.get("gallery") or []
    if not gallery:
        print("该任务没有产出 canvas/帧", file=sys.stderr)
        return
    out = Path(out_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    for path in gallery:
        name = path.rsplit("/", 1)[-1]
        with urllib.request.urlopen(BASE + path, timeout=60) as resp:
            (out / name).write_bytes(resp.read())
    print("已保存 %d 张到 %s" % (len(gallery), out), file=sys.stderr)


JUDGE_SUFFIX = (
    "\n严格按此格式回答，不要有任何多余内容：第一行只写 YES 或 NO，第二行写一句不超过 20 字的理由。"
)


def parse_verdict(answer):
    """从判定式回答里取出 True/False，取不到返回 None。"""
    head = (answer or "").strip().upper()
    for token in ("YES", "是"):
        if head.startswith(token):
            return True
    for token in ("NO", "否", "不是"):
        if head.startswith(token):
            return False
    return None


def expand_inputs(patterns, exts):
    """把目录 / 通配符 / 文件路径展开成去重排序后的文件列表。"""
    import glob as globlib

    files = []
    for pattern in patterns:
        path = Path(pattern).expanduser()
        if path.is_dir():
            files += [p for p in sorted(path.iterdir()) if p.suffix.lower() in exts]
        elif path.is_file():
            files.append(path)
        else:
            files += [Path(p) for p in sorted(globlib.glob(str(path))) if Path(p).suffix.lower() in exts]
    seen, unique = set(), []
    for f in files:
        key = f.resolve()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def run_batch(args):
    """对一批图片跑同一个问题，逐条写 JSONL。绝不删除或修改任何输入文件。"""
    files = expand_inputs(args.inputs, IMAGE_EXTS)
    if not files:
        sys.exit("没有匹配到图片，检查路径或通配符（记得给通配符加引号）")

    done = {}
    out_path = Path(args.out).expanduser() if args.out else None
    if out_path and out_path.exists() and args.resume:
        for line in out_path.read_text().splitlines():
            try:
                rec = json.loads(line)
                done[rec["file"]] = rec
            except (ValueError, KeyError):
                pass

    question = args.question + (JUDGE_SUFFIX if args.judge else "")
    ensure_ready(timeout=args.timeout)
    sink = out_path.open("a") if out_path else None
    records = []

    try:
        for index, path in enumerate(files, 1):
            key = str(path)
            if key in done:
                records.append(done[key])
                print("[%d/%d] 跳过（已有结果） %s" % (index, len(files), path.name), file=sys.stderr)
                continue
            print("[%d/%d] %s" % (index, len(files), path.name), file=sys.stderr)
            started = time.time()
            try:
                job_id = post_job(
                    "image",
                    path,
                    {
                        "question": question,
                        "image_quality": args.quality,
                        "max_new_tokens": args.max_tokens or (48 if args.judge else 256),
                    },
                )
                answer = follow(job_id, show_tokens=False).get("answer", "")
                record = {
                    "file": key,
                    "name": path.name,
                    "answer": answer.strip(),
                    "seconds": round(time.time() - started, 1),
                }
                if args.judge:
                    record["verdict"] = parse_verdict(answer)
            except SystemExit as exc:
                record = {"file": key, "name": path.name, "error": str(exc)}
            records.append(record)
            if sink:
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                sink.flush()
    finally:
        if sink:
            sink.close()

    if args.judge:
        yes = [r for r in records if r.get("verdict") is True]
        no = [r for r in records if r.get("verdict") is False]
        unclear = [r for r in records if "verdict" in r and r["verdict"] is None]
        print("\n=== YES (%d) ===" % len(yes))
        for r in yes:
            print("%s\t%s" % (r["name"], r["answer"].replace("\n", " / ")))
        print("\n=== NO (%d) ===" % len(no))
        for r in no:
            print(r["name"])
        if unclear:
            print("\n=== 无法判定 (%d，请人工看) ===" % len(unclear))
            for r in unclear:
                print("%s\t%s" % (r["name"], r["answer"].replace("\n", " / ")))
        print(
            "\n本命令只做判定，不动任何文件。要处理 YES 那批，自己确认后再操作，例如：\n"
            "  mkdir -p _flagged && mv <上面 YES 的文件> _flagged/"
        )
    else:
        for r in records:
            print("\n## %s" % r["name"])
            print(r.get("answer") or ("错误: " + r.get("error", "")))

    errors = [r for r in records if "error" in r]
    if errors:
        print("\n%d 张失败" % len(errors), file=sys.stderr)
    if out_path:
        print("结果已写入 %s" % out_path, file=sys.stderr)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Mage-VL 本地服务客户端")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="查询服务状态")
    up = sub.add_parser("up", help="启动服务并等待模型加载完成")
    up.add_argument("--timeout", type=int, default=300)
    sub.add_parser("down", help="停止服务")

    for name, help_text in [("image", "图片问答"), ("video", "视频问答"), ("stream", "主动流式解说")]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("file")
        p.add_argument("-q", "--question", default="", help="问题或解说指令")
        p.add_argument("--max-tokens", type=int, default=None, help="16–1024；stream 模式每段上限 256")
        p.add_argument("--timeout", type=int, default=300, help="等待模型就绪的秒数")
        if name == "image":
            p.add_argument("--quality", default="balanced", choices=["quick", "balanced", "high"])
        else:
            p.add_argument("--backend", default="dcvc", choices=["dcvc", "frames"])
            p.add_argument("--frames", type=int, default=32, help="8–64")
        if name in ("video", "stream"):
            p.add_argument("--save-frames", metavar="DIR", help="把生成的 canvas/帧下载到该目录")
        if name == "stream":
            p.add_argument("--segment-sec", type=float, default=8.0, help="4–12")
            p.add_argument("--max-segments", type=int, default=4, help="2–8")
            p.add_argument("--gate-threshold", type=float, default=0.5, help="0.1–0.9")

    b = sub.add_parser("batch", help="对一批图片跑同一个问题（只读，不改文件）")
    b.add_argument("inputs", nargs="+", help="目录、文件，或加引号的通配符")
    b.add_argument("-q", "--question", required=True)
    b.add_argument("--judge", action="store_true", help="判定模式：强制 YES/NO 首行，末尾按结论分组")
    b.add_argument("--out", help="结果写入的 JSONL 路径")
    b.add_argument("--resume", action="store_true", help="跳过 --out 里已有结果的文件")
    b.add_argument("--quality", default="balanced", choices=["quick", "balanced", "high"])
    b.add_argument("--max-tokens", type=int, default=None)
    b.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    if args.cmd == "status":
        status = api_status()
        print(json.dumps(status, ensure_ascii=False, indent=2) if status else "服务未运行")
        return 0 if status else 1

    if args.cmd == "up":
        ensure_ready(timeout=args.timeout)
        print("就绪：UI http://127.0.0.1:3000/ ，API %s" % BASE)
        return 0

    if args.cmd == "down":
        for pattern in ("start.command", "uvicorn backend.main", "vinext start"):
            subprocess.run(["pkill", "-f", pattern], capture_output=True)
        print("已停止")
        return 0

    if args.cmd == "batch":
        return run_batch(args)

    ensure_ready(timeout=args.timeout)

    fields = {"question": args.question}
    if args.cmd == "image":
        fields["image_quality"] = args.quality
        fields["max_new_tokens"] = args.max_tokens or 256
    else:
        fields["backend"] = args.backend
        fields["num_frames"] = args.frames
        if args.cmd == "video":
            fields["max_new_tokens"] = args.max_tokens or 512
        else:
            fields["max_new_tokens"] = min(args.max_tokens or 200, 256)
            fields["segment_sec"] = args.segment_sec
            fields["max_segments"] = args.max_segments
            fields["gate_threshold"] = args.gate_threshold

    job_id = post_job(args.cmd, args.file, fields)
    print("job %s" % job_id, file=sys.stderr)
    result = follow(job_id)
    report(result)
    if getattr(args, "save_frames", None):
        save_gallery(result, args.save_frames)
    return 0


if __name__ == "__main__":
    sys.exit(main())
