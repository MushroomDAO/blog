---
name: xhs-video-planner
description: |
  Plan, script, and draft content for the Mushroom.cv XiaoHongShu account —
  video-first with occasional image-text notes, sourced by working backwards
  from published blog posts to real pain points individuals and small
  organizations face.

  Trigger when the user says: 小红书选题, xhs选题, 小红书视频选题, 小红书图文预览,
  排小红书内容, plan xiaohongshu content.

  Use for:
  - picking/registering a topic in xhs-video/topics.yml
  - writing a video script (script.md) from a blog post + a pain point
  - writing a companion image-text note (note.md) per pipeline/m3/note-template.md
  - rendering a local mobile-mockup HTML preview of a note and opening it in the browser

  Does NOT publish anything. Publishing goes through MediaBot's PublisherProvider
  approval gateway (~/Dev/tools/MediaBot) — see xhs-video/PLAN.md "发布路径". This
  skill only produces drafts and previews.
---

# XHS Video Planner Skill

## Mission

Turn the blog's existing catalog of open-source tool / agent write-ups into a
weekly XiaoHongShu content queue, using a "start from the end" logic: pick a
real pain point an individual or small organization has, then work backwards
to which already-published blog post supplies the open-source path that solves
it. See `xhs-video/PLAN.md` for the full positioning and rationale before
planning topics — read it fresh each time, don't rely on a stale summary.

Project paths:
- Strategy + process: `xhs-video/PLAN.md`
- Topic queue: `xhs-video/topics.yml`
- Drafts: `xhs-video/drafts/<slug>/script.md` + `note.md`
- Image-text structural template: `pipeline/m3/note-template.md`
- Blog articles to mine for source material: `src/content/blog/`

## Workflow

1. **Pick a pain point** — something concrete an individual or small
   org/company gets stuck on (not a technology name). If the user hasn't given
   one, propose 2-3 candidates and ask which to run with.
2. **Match it to a published blog post** — search `src/content/blog/` for the
   open-source project/agent approach that plausibly solves it. If nothing
   fits well, say so rather than forcing a weak match.
3. **Register in `xhs-video/topics.yml`** with `status: idea`, the pain point,
   and the source blog slug.
4. **Write `script.md`** in `xhs-video/drafts/<slug>/`: hook (the pain point,
   stated plainly, no clickbait) → path (what open-source piece + what agent
   work stitches it together) → payoff (what changes for the person) → soft
   close. Keep the voice consistent with the blog's own tone — calm and
   specific, not "姐妹们/YYDS" internet-slang style.
5. **Write `note.md`** using the structure in `pipeline/m3/note-template.md` —
   cover title ≤20 chars, 3-6 content-card bullets, caption with hook + 3-5
   bullet highlights + soft CTA + 3-6 tags, no clickable links in the body.
6. **Render a local preview** — build a small self-contained HTML file that
   mocks a phone-width XiaoHongShu note view (cover text + caption + tags),
   save it under `xhs-video/drafts/<slug>/preview.html`, and open it with the
   `open` command so the user can review it in their local browser before
   anything is produced or published.
7. Update `topics.yml` status to `scripted` once script + note + preview exist.
   Do not set `recorded` or `published` yourself — those reflect real-world
   state the user reports back.

## Publishing (out of scope for this skill)

- Image-text notes: MediaBot already has a working XiaoHongShu
  `PublisherProvider` (drives the `xhs` CLI). Once MediaBot is initialized for
  the Mushroom.cv account, notes go through `mediabot run` → `mediabot queue`
  → `mediabot approve`.
  A a video `PublisherProvider` does not exist there yet — video publishing
  stays manual (or a supervised one-off `sau xiaohongshu upload-video` run)
  until it's built and its browser selectors are human-verified.
- Never call `xhs post` or `sau xiaohongshu upload-video` from this skill to
  actually publish. Drafting and local preview only. See `xhs-video/PLAN.md`
  "发布路径" for why, and for the concrete next steps to close that gap.

## Required Output

Return:
- topic registered (slug, pain point, source blog post)
- script.md and note.md paths
- preview.html path, confirmation it was opened locally
- current topics.yml status for the slug
