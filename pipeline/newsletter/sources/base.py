"""Shared schema and helpers for newsletter content sources."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DigestItem:
    """One card in the digest email. Produced by a source's collect().

    id: unique within this source — combined with the source's own
        namespacing convention it becomes the dedup key stored in
        last-sent.json's sent_slugs. The "blog" source uses bare article
        slugs with no prefix (for backward compatibility with state
        already on disk); any new source should prefix its ids (e.g.
        "trends:2026-08-01-ai-adoption") so it can never collide with a
        blog slug or another source's ids.
    link: external URL to send readers to ("阅读全文 →"). Leave None for
        content that only exists in the email itself (see body_html).
    body_html: pre-rendered, already-HTML-safe body to show inline instead
        of (or alongside) a "read more" link — for subscriber-only content
        that has nowhere else to link to. At least one of link/body_html
        should be set.
    banner_url: absolute http(s) URL. None falls back to the digest's
        default banner at render time.
    """

    source: str
    id: str
    title: str
    summary: str
    pub_date: datetime
    banner_url: Optional[str] = None
    link: Optional[str] = None
    body_html: Optional[str] = None

    @property
    def dedup_key(self) -> str:
        return self.id if self.source == "blog" else f"{self.source}:{self.id}"
