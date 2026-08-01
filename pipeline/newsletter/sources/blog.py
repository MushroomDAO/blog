"""Blog source: newly published posts from src/content/blog/*.md.

Only source that exists today. See sources/__init__.py for how to add more.
"""
import datetime
import re
import sys
from pathlib import Path

import dateutil.parser
import requests
import yaml

from .base import DigestItem

ROOT = Path(__file__).resolve().parents[3]
BLOG_DIR = ROOT / "src/content/blog"
SITE_URL = "https://blog.mushroom.cv"
FALLBACK_BANNER = f"{SITE_URL}/favicon.svg"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def slugify(filename_stem: str) -> str:
    """Matches Astro's glob-loader id generation for this content collection:
    lowercase, strip anything that isn't [a-z0-9-]. Confirmed empirically
    against the live sitemap for the 3 filenames in this repo that contain
    a period or uppercase letters (e.g. "...-0.6b-...-dualAR" ->
    "...-06b-...-dualar") — using the raw filename stem as the URL slug
    silently produced a broken article link + wrong og:image for those.
    """
    return re.sub(r"[^a-z0-9-]", "", filename_stem.lower())


def _parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        print(f"  ! skipping {path.name}: frontmatter parse error ({e})", file=sys.stderr)
        return None


def _og_image_for(slug: str) -> str:
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


def collect(window_start: datetime.datetime, sent_ids: set) -> list:
    items = []
    for path in BLOG_DIR.glob("*.md"):
        slug = slugify(path.stem)
        if slug in sent_ids:
            continue
        fm = _parse_frontmatter(path)
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
        items.append(
            DigestItem(
                source="blog",
                id=slug,
                title=fm.get("title", slug),
                summary=fm.get("description", ""),
                pub_date=pub_date,
                banner_url=_og_image_for(slug),
                link=f"{SITE_URL}/blog/{slug}/",
            )
        )
    return items
