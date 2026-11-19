from pathlib import Path
import json,datetime
p=Path(__file__).parent;job=Path('/Users/jason/.heinu1-bot/jobs/00613c57-ed07-4b19-8cfd-1fe57eff41a9');repo=json.loads((p/'repository-status.json').read_text())
for file in [p/'publication-result.json',job/'publication-result.json']:
 r=json.loads(file.read_text());r.update(repositoryStatus='review-required',pullRequest=repo['url'],mainMerged=False);file.write_text(json.dumps(r,ensure_ascii=False,indent=2))
f=job/'publication-progress.json';r=json.loads(f.read_text());r.update(phase='awaiting-repository-review',completed=False,channelsCompleted=True,kbVerified=True,gitPushed=True,mainMerged=False,pullRequest=repo['url']);f.write_text(json.dumps(r,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_rumble-2-flash-small-asr-phone-call-benchmarks.md')
s=memory.read_text().replace('Repository: feature PR pending.','Repository: https://github.com/MushroomDAO/blog/pull/264 OPEN/REVIEW_REQUIRED; normal merge blocked by base branch policy, no admin bypass.')
memory.write_text(s)
feedback=Path('.agents/skills/forage/FEEDBACK.md');text=feedback.read_text();line='\n- 2026-11-19 Rumble-2-Flash: new bilingual rumble-2-flash-small-asr-phone-call-benchmarks; HF official weights Apache2/Qwen3-ASR, no dedicated official GitHub identified. Pin a0c3428; 49 isolated Jinja template-only checks passed, no weights/audio/performance reproduction. Card45 vs config30 languages disclosed. AppTek numeric proximity is not statistical equivalence; H200 batch throughput is not request latency; Chinese CER differs from WER. Seed8801 manually rejected for gibberish despite automated pass,8802+3LittleM final images approved. Deployef91a512 canonical title/list+carouselrank1/all5assets and8priorarticles verified. Current full WeChat draft/cover/metadata/images verified; semantic2IDs+publicquery verified; KBreadback verified. PR264 reviewrequired, normalmerge blocked, no admin bypass.\n'
if '2026-11-19 Rumble-2-Flash:'not in text:feedback.write_text(text+line)
