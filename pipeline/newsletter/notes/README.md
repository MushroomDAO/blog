# Subscriber-only notes

Content for `.md` files dropped here is meant to go **only** into the newsletter digest — it never becomes a page on the public blog (unlike `src/content/blog/`, this directory isn't wired into Astro's content collections or routing).

This directory is currently just a landing spot for future content — there's no `sources/notes.py` reading it yet. When that source is built, it should follow this convention:

```markdown
---
title: "标题"
pubDate: "2026-08-01"
summary: "一两句摘要，用于卡片展示"
---

正文内容，会被渲染成邮件内联 HTML（不是 markdown 直接塞进邮件——需要转成安全的内联样式 HTML）。
```

Expected mapping to `DigestItem` (see `../sources/base.py`):

- `id` — the filename stem (mirrors how the blog source uses filenames)
- `link` — `None` (no public page to send readers to)
- `body_html` — the note's body, converted from markdown and inlined directly into the email (readers see the whole thing in their inbox, there's nowhere else for it to link to)

Same idea applies to other non-blog sources (e.g. a Google Trends / AI-research digest) — see `../sources/__init__.py` for how to register a new source once one exists.
