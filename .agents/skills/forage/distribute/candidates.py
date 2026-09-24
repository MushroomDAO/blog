#!/usr/bin/env python3
"""每周英文分发的机械筛选：从已发布文章里挑出可以拿去 HN / Reddit / dev.to 的候选。

只做能用规则判断的部分——有没有完整英文版、够不够长、最近有没有发、分发过没有、
浏览量如何。「值不值得发、发哪个社区、帖子怎么写」是判断，交给 DISTRIBUTE-JOB.md
里的后台 Claude 会话。

输出 radar/distribution/<YYYY-Www>/candidates.json。
"""
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BLOG_DIR = os.path.join(ROOT, "src", "content", "blog")
ANALYTICS = os.path.join(ROOT, "src", "data", "blog-analytics.json")
OUT_ROOT = os.path.join(ROOT, "radar", "distribution")
LEDGER = os.path.join(OUT_ROOT, "ledger.json")

LOOKBACK_DAYS = 30
MIN_EN_WORDS = 600
MAX_CANDIDATES = 8
# 纯资讯转述在 HN/Reddit 上基本没人要；有实测、有拆解的文章才有机会
CATEGORY_BONUS = {"Tech-Experiment": 3, "Research": 2, "Tech-News": 0, "Progress-Report": 0, "DN": 0}
# 正文里出现这些词，说明有自己动手的一手内容
FIRSTHAND_MARKERS = ("tested", "benchmark", "we ran", "i ran", "measured", "on my mac", "mac mini",
                     "locally", "reproduce", "our test", "in our run", "fact-check", "teardown")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, m.group(2)


def words(md):
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    md = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)", r" \1 ", md)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]+", md))


def main():
    today = date.today()
    week = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"
    ledger = json.load(open(LEDGER)) if os.path.exists(LEDGER) else {}
    pv = {}
    if os.path.exists(ANALYTICS):
        for p in json.load(open(ANALYTICS)).get("pages", []):
            slug = p["path"].strip("/").removeprefix("blog/")
            pv[slug] = p["pv"]

    out = []
    for fn in os.listdir(BLOG_DIR):
        if not fn.endswith((".md", ".mdx")):
            continue
        slug = fn.rsplit(".", 1)[0]
        if slug in ledger:
            continue
        fm, body = frontmatter(open(os.path.join(BLOG_DIR, fn), encoding="utf-8").read())
        try:
            pub = datetime.strptime(fm.get("pubDate", "")[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        if (today - pub).days > LOOKBACK_DAYS or "<!--EN-->" not in body or not fm.get("titleEn"):
            continue
        en = body.split("<!--EN-->", 1)[1]
        en_words = words(en)
        if en_words < MIN_EN_WORDS:
            continue
        low = en.lower()
        firsthand = sum(1 for k in FIRSTHAND_MARKERS if k in low)
        score = (CATEGORY_BONUS.get(fm.get("category", ""), 0)
                 + min(firsthand, 4)
                 + min(en_words // 500, 4)
                 + (3 if slug in pv else 0)
                 - (today - pub).days / 10)
        out.append({
            "slug": slug,
            "url": f"https://blog.mushroom.cv/blog/{slug}/",
            "titleEn": fm.get("titleEn"),
            "descriptionEn": fm.get("descriptionEn", ""),
            "category": fm.get("category", ""),
            "pubDate": pub.isoformat(),
            "enWords": en_words,
            "firsthandMarkers": firsthand,
            "pageviews30d": pv.get(slug),
            "score": round(score, 1),
        })

    out.sort(key=lambda x: -x["score"])
    out = out[:MAX_CANDIDATES]
    os.makedirs(os.path.join(OUT_ROOT, week), exist_ok=True)
    path = os.path.join(OUT_ROOT, week, "candidates.json")
    json.dump({"week": week, "generatedAt": datetime.now().isoformat(timespec="seconds"),
               "candidates": out}, open(path, "w"), ensure_ascii=False, indent=2)
    print(f"✓ {len(out)} candidates → {os.path.relpath(path, ROOT)}")
    return 0 if out else 2


if __name__ == "__main__":
    sys.exit(main())
