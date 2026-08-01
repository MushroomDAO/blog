"""Content-source registry for the newsletter digest.

Each source module exposes a single function:

    collect(window_start: datetime, sent_ids: set[str]) -> list[DigestItem]

...that returns items not yet sent, published after window_start. See
base.DigestItem for the schema and sources/blog.py for a working example.

To add a source: write pipeline/newsletter/sources/<name>.py implementing
collect(), then add it to SOURCES below. build-digest.py calls every entry
here, merges the results, sorts by pub_date, and renders one digest — no
other file needs to change.
"""
from . import blog

SOURCES = {
    "blog": blog,
    # "trends": trends,   # e.g. a Google Trends AI-research digest — not built yet
    # "notes": notes,     # subscriber-only notes/experiments that never touch the public blog — not built yet
}
