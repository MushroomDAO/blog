from pathlib import Path
import json
p=Path(__file__).resolve().parent; root=p.parents[1];slug='rumble-2-flash-small-asr-phone-call-benchmarks'
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')
note='''---
name: Rumble-2-Flash ASR audit
description: Reson8 small ASR benchmarks and deployment boundaries.
type: project
---
# Rumble-2-Flash
Sources: https://huggingface.co/Reson8/Rumble-2-Flash ; https://huggingface.co/blog/rumble-2-flash
Date: 2026-11-19
Slug: rumble-2-flash-small-asr-phone-call-benchmarks
Dedup: only incoming raw KB material; no Blog/local M2/remote draft match. Published API48001 unavailable.
Apache2.0/Qwen3-ASR/on-policy GOLD distillation. AppTek7.86 vs7.78 is +0.08pp, no significance proof. H200 batched throughput is not call latency. Chinese CER. Card45 vs config30 language metadata discrepancy. HF is authoritative artifact; no attributable dedicated GitHub identified.
Blog pending; WeChat pending; semantic pending. Template-only verification planned, no real-weight inference/performance reproduction.
'''
(memory/f'project_{slug}.md').write_text(note)
index=memory/'MEMORY.md';s=index.read_text()
if f'project_{slug}.md'not in s:index.write_text(s+f'\n- [Rumble-2-Flash ASR](project_{slug}.md) — small ASR benchmarks and deployment boundaries.\n')
(p/'slugs.json').write_text(json.dumps([slug]))
