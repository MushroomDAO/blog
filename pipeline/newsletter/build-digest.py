#!/usr/bin/env python3
"""build-digest.py — 读 src/content/blog 里新发的文章，生成"报纸风格"摘要邮件 HTML。

用法:
    python3 pipeline/newsletter/build-digest.py [--since-days N] [--out FILE]

逻辑:
    1. 读 pipeline/newsletter/last-sent.json 里记录的已发送文章 slug 集合（没有
       就用 --since-days，默认 2 天，取一个粗时间窗口兜底）。
    2. 扫 src/content/blog/*.md，挑 pubDate 在窗口内、且 slug 还没发过的文章——
       用 slug 去重而不是纯时间比较，因为这个博客的 pubDate 经常只写日期
       没有时间（比如 '2026-08-01'），同一天发的文章会被解析成同一个午夜
       时间戳，如果只比较时间戳，当天更晚发布的文章会被"已经发过同一天"
       误判成永久跳过。
    3. 每篇文章尝试抓它线上页面的 og:image 作为 banner 绝对 URL（没抓到就用
       兜底图 favicon.svg，且只接受 http(s) URL，避免奇怪协议混进邮件）；
       标题/摘要来自 frontmatter，插入 HTML 前统一转义。
    4. 最多放 7 篇（按 pubDate 倒序），超出的在末尾提示"还有 N 篇，去博客看全部"。
    5. 渲染成邮件安全的内联样式 HTML，写到 --out（默认
       pipeline/newsletter/digest-output.html），同时把本次挑中的 slug 列表写到
       同目录的 <out>.manifest.json，供 send-newsletter.sh 发送成功后合并进
       last-sent.json 的已发送 slug 集合。
    不在这里更新 last-sent.json —— 只有真正发送成功后才更新，由
    send-newsletter.sh 负责，避免"生成了但没发出去"却被当成已发送。
"""
import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

import dateutil.parser
import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = ROOT / "src/content/blog"
STATE_FILE = Path(__file__).resolve().parent / "last-sent.json"
SITE_URL = "https://blog.mushroom.cv"
FALLBACK_BANNER = f"{SITE_URL}/favicon.svg"
MAX_ARTICLES = 7

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        print(f"  ! skipping {path.name}: frontmatter parse error ({e})", file=sys.stderr)
        return None


def load_state(since_days: int):
    """Returns (window_start, already_sent_slugs)."""
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        window_start = datetime.datetime.fromisoformat(data["last_sent_at"])
        sent_slugs = set(data.get("sent_slugs", []))
    else:
        window_start = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=since_days)
        sent_slugs = set()
    # date-only pubDate values collapse to midnight, so a post published later
    # the same day as the last send can land exactly on window_start — widen
    # the scan window by a day and rely on sent_slugs (not the timestamp) for
    # the actual dedup so that case is never silently dropped.
    return window_start - datetime.timedelta(days=1), sent_slugs


def og_image_for(slug: str) -> str:
    url = f"{SITE_URL}/blog/{slug}/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        m = re.search(r'<meta property="og:image" content="([^"]+)"', resp.text)
        if m and m.group(1).startswith(("http://", "https://")):
            return m.group(1)
    except requests.RequestException as e:
        print(f"  ! og:image fetch failed for {slug}: {e}", file=sys.stderr)
    return FALLBACK_BANNER


def collect_new_posts(window_start: datetime.datetime, sent_slugs: set):
    posts = []
    for path in BLOG_DIR.glob("*.md"):
        slug = path.stem
        if slug in sent_slugs:
            continue
        fm = parse_frontmatter(path)
        if not fm:
            continue
        pub_date = fm.get("pubDate")
        if pub_date is None:
            continue
        if isinstance(pub_date, str):
            try:
                pub_date = dateutil.parser.parse(pub_date)
            except (ValueError, OverflowError) as e:
                print(f"  ! skipping {path.name}: unparseable pubDate {pub_date!r} ({e})", file=sys.stderr)
                continue
        if isinstance(pub_date, datetime.date) and not isinstance(pub_date, datetime.datetime):
            pub_date = datetime.datetime.combine(pub_date, datetime.time.min)
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=datetime.timezone.utc)
        if pub_date <= window_start:
            continue
        posts.append(
            {
                "slug": slug,
                "title": fm.get("title", slug),
                "description": fm.get("description", ""),
                "pub_date": pub_date,
            }
        )
    posts.sort(key=lambda p: p["pub_date"], reverse=True)
    return posts


CARD_TPL = """
<tr>
  <td style="padding: 0 0 28px 0;">
    <img src="{banner}" width="100%" alt="" style="display:block;width:100%;max-width:525px;height:auto;border-radius:6px;margin-bottom:12px;" />
    <div style="font-size:18px;font-weight:bold;color:#222;line-height:1.4;margin-bottom:6px;">{title}</div>
    <div style="font-size:14px;color:#555;line-height:1.6;margin-bottom:8px;">{description}</div>
    <a href="{url}" style="font-size:14px;color:#0055d4;text-decoration:none;font-weight:bold;">阅读全文 →</a>
  </td>
</tr>
"""

BASE_TPL = """<!doctype html>
<html>
<body style="margin:0;padding:0;background-color:#F0F1F3;font-family:'Helvetica Neue','Segoe UI',Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F0F1F3;padding:30px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="525" cellpadding="0" cellspacing="0" style="background-color:#fff;padding:30px;border-radius:5px;">
          <tr>
            <td style="padding-bottom:20px;">
              <div style="font-size:20px;font-weight:bold;">🍄 Mushroom Research Blog</div>
              <div style="font-size:13px;color:#888;margin-top:4px;">{issue_date} 更新摘要</div>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom:24px;font-size:15px;color:#444;line-height:1.6;">
              这期我们发了 {count} 篇新文章，挑重点给你翻一下：
            </td>
          </tr>
          {cards}
          {more_notice}
          <tr>
            <td style="padding-top:20px;border-top:1px solid #eee;font-size:12px;color:#888;text-align:center;">
              🍄 Mushroom Research Blog｜非营利个人科技观察<br/>
              <a href="{{{{ UnsubscribeURL }}}}" style="color:#888;">退订</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def render(posts):
    shown = posts[:MAX_ARTICLES]
    rest = len(posts) - len(shown)
    cards = "\n".join(
        CARD_TPL.format(
            banner=html.escape(og_image_for(p["slug"]), quote=True),
            title=html.escape(p["title"]),
            description=html.escape(p["description"]),
            url=html.escape(f"{SITE_URL}/blog/{p['slug']}/", quote=True),
        )
        for p in shown
    )
    more_notice = ""
    if rest > 0:
        more_notice = (
            f'<tr><td style="padding-bottom:20px;font-size:13px;color:#888;">'
            f'本期还有 {rest} 篇，<a href="{SITE_URL}/blog/" style="color:#0055d4;">去博客看全部</a></td></tr>'
        )
    return BASE_TPL.format(
        issue_date=datetime.date.today().isoformat(),
        count=len(posts),
        cards=cards,
        more_notice=more_notice,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=2)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "digest-output.html"))
    args = ap.parse_args()

    window_start, sent_slugs = load_state(args.since_days)
    posts = collect_new_posts(window_start, sent_slugs)

    if not posts:
        print("no new posts since", window_start.isoformat(), "— nothing to send")
        sys.exit(3)  # distinct exit code so send-newsletter.sh can skip cleanly

    html_out = render(posts)
    out_path = Path(args.out)
    out_path.write_text(html_out, encoding="utf-8")

    manifest_path = out_path.with_suffix(out_path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps({"slugs": [p["slug"] for p in posts]}), encoding="utf-8")

    print(f"{len(posts)} new post(s) -> {out_path} (manifest: {manifest_path})")
    for p in posts:
        print(f"  - {p['pub_date'].date()}  {p['title']}")


if __name__ == "__main__":
    main()
