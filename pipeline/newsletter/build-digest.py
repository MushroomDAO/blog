#!/usr/bin/env python3
"""build-digest.py — orchestrator: pulls new items from every registered
content source, merges them, renders one "报纸风格" digest email.

用法:
    python3 pipeline/newsletter/build-digest.py [--since-days N] [--out FILE]

逻辑:
    1. 读 pipeline/newsletter/last-sent.json 里记录的已发送条目 id 集合（没有
       就用 --since-days，默认 2 天，取一个粗时间窗口兜底）。
    2. 依次调用 sources/__init__.py 里注册的每个内容源的 collect()，各自返回
       尚未发送、在时间窗口内的 DigestItem 列表——见 sources/base.py 的 schema
       和 sources/blog.py 的参考实现。要加新内容源（Google Trends 分析、不上
       博客的个人笔记/实验记录等），写一个新的 sources/<name>.py 并注册进
       SOURCES，这个文件不用改。
    3. 合并所有来源的条目、按 pub_date 倒序、最多放 templates.MAX_ITEMS 条，
       渲染成邮件安全的内联样式 HTML，写到 --out（默认
       pipeline/newsletter/digest-output.html），同时把本次挑中的条目 id
       写到同目录的 <out>.manifest.json，供 send-newsletter.sh 发送成功后
       合并进 last-sent.json 的已发送 id 集合。
    不在这里更新 last-sent.json —— 只有真正发送成功后才更新，由
    send-newsletter.sh 负责，避免"生成了但没发出去"却被当成已发送。
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

from sources import SOURCES
from templates import MAX_ITEMS, render

STATE_FILE = Path(__file__).resolve().parent / "last-sent.json"
FALLBACK_BANNER = "https://blog.mushroom.cv/favicon.svg"


def load_state(since_days: int):
    """Returns (window_start, already_sent_ids)."""
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        window_start = datetime.datetime.fromisoformat(data["last_sent_at"])
        sent_ids = set(data.get("sent_slugs", []))
    else:
        window_start = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=since_days)
        sent_ids = set()
    # date-only pubDate values (common in blog frontmatter) collapse to
    # midnight, so an item published later the same day as the last send can
    # land exactly on window_start — widen the scan window by a day and rely
    # on sent_ids (not the timestamp) for the actual dedup so that case is
    # never silently dropped.
    return window_start - datetime.timedelta(days=1), sent_ids


def collect_all(window_start: datetime.datetime, sent_ids: set) -> list:
    items = []
    for name, source in SOURCES.items():
        try:
            source_items = source.collect(window_start, sent_ids)
        except Exception as e:
            print(f"  ! source '{name}' failed, skipping it this cycle: {e}", file=sys.stderr)
            continue
        print(f"  source '{name}': {len(source_items)} new item(s)")
        items.extend(source_items)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=2)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "digest-output.html"))
    args = ap.parse_args()

    window_start, sent_ids = load_state(args.since_days)
    items = collect_all(window_start, sent_ids)

    if not items:
        print("no new items since", window_start.isoformat(), "— nothing to send")
        sys.exit(3)  # distinct exit code so send-newsletter.sh can skip cleanly

    html_out = render(items, FALLBACK_BANNER)
    out_path = Path(args.out)
    out_path.write_text(html_out, encoding="utf-8")

    # cap applied by templates.render() (MAX_ITEMS) — manifest should only
    # record what was actually shown, not everything collected, so an
    # overflowed item gets picked up fresh (with correct dedup) next cycle
    # instead of being marked "sent" without ever appearing in an email.
    shown = sorted(items, key=lambda i: i.pub_date, reverse=True)[:MAX_ITEMS]
    manifest_path = out_path.with_suffix(out_path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps({"slugs": [i.dedup_key for i in shown]}), encoding="utf-8")

    print(f"{len(shown)} of {len(items)} new item(s) shown -> {out_path} (manifest: {manifest_path})")
    for i in shown:
        print(f"  - [{i.source}] {i.pub_date.date()}  {i.title}")


if __name__ == "__main__":
    main()
