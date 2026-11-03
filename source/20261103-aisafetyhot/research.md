---
name: AI Safety HOT website guide
description: Website, public Hub, read-only MCP scope and source verification review
type: project
---
# AI Safety HOT
Date: 2026-11-03
Slug: aisafetyhot-ai-safety-news-guide
Website: https://aisafetyhot.com/zh/
Hub: https://github.com/wuyoscar/AISafetyHot (old AISafetyHot-Hub redirects)
Commit: cf15c9b55745564482379df818f8a2bdc248e6e6
Findings: Website provides news/events/papers/digests and source links. Public Hub is archives/docs/skills, not a complete local website backend. Text license CC BY-NC4.0; original third-party material excluded. Current anonymous MCP limited to recent picked News and selected paper links; history/full reads require authorization; not a key-free unlimited corpus API.
Actual checks: tools/list and get_hot_topics returned HTTP200 over SSE. No client installation or persistence changes. Native page retrieval and primary document review.
Source check: 2026-11-02 site daily summarized Magma model incident, original LessWrong by Parv Mahajan 2026-11-01 explicitly Fiction. Cannot infer global error rate from one example; must preserve fiction marker and distinguish claims.
Dedup: no dedicated local Blog/M2 record; bot raw KB only. Remote WeChat queries blocked40164 IP223.204.71.95. Blog/KB continue independently, one missing M2 attempt after deployment required.
Blog: pending.
WeChat: pending.

Native HTTP retrieval independently confirmed Nov2 daily HTTP200 with Magma and no Fiction string, original LessWrong HTTP200 with Fiction. Nov2 public Markdown archive also retains incident wording without fiction marker. No aggregate error-rate claim.
Official UI assets were captured Oct21 by project documentation; no reuse of counters as current statistics.
Read install.md as documentation only; did not follow its embedded request to install.
