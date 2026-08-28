---
name: daily-video-planner
description: |
  Plan and draft the unified free video content line ("开源仓库开盒" + XiaoHongShu
  merged, 2026-08-28) — one topic sourced by working backwards from a real
  individual/SME pain point (= what a local-first AI product needs to cover),
  one deep repo research/deployment pass, cut into a long version (YouTube +
  Bilibili) and a short version (XiaoHongShu, vertical), plus an optional
  XiaoHongShu image-text note.

  Trigger when the user says: 选视频选题, 排daily-video选题, 小红书选题,
  小红书视频选题, 小红书图文预览, plan daily-video content.

  Use for:
  - picking/registering a topic in daily-video/topics.yml
  - writing a long-cut script (script.md) for the YouTube/Bilibili teardown edit
  - writing a short-cut script (short-script.md) for the XiaoHongShu vertical edit
  - writing a companion image-text note (note.md) per pipeline/m3/note-template.md
  - rendering a local mobile-mockup HTML preview of a note and opening it in the browser

  Does NOT publish anything. Publishing goes through MediaBot's PublisherProvider
  approval gateway (~/Dev/tools/MediaBot) — see daily-video/PLAN.md "发布路径" /
  "并入小红书". This skill only produces topic registrations, scripts, drafts,
  and previews.
---

# Daily Video Planner Skill

## Mission

One topic, one research/deployment pass, up to three outputs: a long teardown
edit (YouTube/Bilibili), a short pain-point-first edit (XiaoHongShu, vertical),
and an optional XiaoHongShu image-text note. Read `daily-video/PLAN.md` fresh
each time before planning — it has the full positioning, the merge rationale,
and the video-spec guidance (duration/aspect ratio) — don't rely on a stale
summary of it.

Project paths:
- Strategy + process: `daily-video/PLAN.md`
- Pain-point source map: `daily-video/painpoints.md` (rendered as an interactive
  mind map at `/my/painpoints/`) — browse this first when picking a topic
- Topic queue: `daily-video/topics.yml`
- Drafts: `daily-video/drafts/<slug>/` — `script.md` (long cut), `short-script.md`
  (XiaoHongShu cut), `note.md` (image-text note)
- Image-text structural template: `pipeline/m3/note-template.md`
- Blog articles to mine for source material: `src/content/blog/`

## Workflow

1. **Pick a pain point** — something concrete an individual or small
   org/company gets stuck on; this doubles as "a scenario a local-first AI
   product needs to cover" (same question, two framings — see PLAN.md). If the
   user hasn't given one, propose 2-3 candidates and ask which to run with.
2. **Find/match candidate open-source repos** that plausibly solve it — search
   `src/content/blog/` first for ones already written up; if nothing fits,
   say so rather than forcing a weak match. The actual deploy-and-evaluate work
   happens outside this skill (that's the expensive MediaBot/handson-video
   step); this skill only registers the topic and drafts scripts once a
   candidate is identified.
3. **Register in `daily-video/topics.yml`** with `status: idea`, the pain
   point, candidate repos, and which `channels` this topic targets
   (`xiaohongshu` / `bilibili` / `youtube` — can be more than one).
4. **Write `script.md`** (long cut, if `bilibili`/`youtube` is a target) —
   full walkthrough: setup → deployment → technical detail → verdict. 8-15 min
   target, no hard ceiling.
5. **Write `short-script.md`** (if `xiaohongshu` is a target) — the pain point
   stated plainly in the first 15-30 seconds (this is the retention-critical
   window, not the overall length), then the compressed solution path, skip
   deep technical detail. Target 5-6 min, hard cap 8 min. Keep the voice
   consistent with the blog's own tone — calm and specific, not
   "姐妹们/YYDS" internet-slang style.
6. **Write `note.md`** (optional, only if a companion note is worth it) using
   the structure in `pipeline/m3/note-template.md` — cover title ≤20 chars,
   3-6 content-card bullets, caption with hook + 3-5 bullet highlights + soft
   CTA + 3-6 tags, no clickable links in the body.
7. **Render a local preview** for the note — a small self-contained HTML file
   mocking a phone-width XiaoHongShu note view, saved as
   `daily-video/drafts/<slug>/preview.html`, opened with the `open` command so
   the user can review it locally before anything is produced or published.
8. Update `topics.yml` status to `scripted` once the relevant scripts/notes/
   preview exist. Do not set `recorded` or `published` yourself — those
   reflect real-world state the user reports back.

## Publishing (out of scope for this skill)

- Image-text notes: MediaBot already has a working XiaoHongShu
  `PublisherProvider` (drives the `xhs` CLI). Once MediaBot is initialized for
  the Mushroom.cv account, notes go through `mediabot run` → `mediabot queue`
  → `mediabot approve`.
- Long-cut (bilibili/youtube) and short-cut (xiaohongshu) video publishing both
  need new `PublisherProvider`s in MediaBot that don't exist yet — see
  `daily-video/PLAN.md` for the concrete next steps. Until those exist and
  have human-verified selectors, video publishing stays manual.
- Never call `xhs post` or `sau <platform> upload-video` from this skill to
  actually publish. Drafting and local preview only.

## Required Output

Return:
- topic registered (slug, pain point, candidate repos, channels)
- script.md / short-script.md / note.md paths (whichever were written)
- preview.html path, confirmation it was opened locally (if a note was drafted)
- current topics.yml status for the slug
