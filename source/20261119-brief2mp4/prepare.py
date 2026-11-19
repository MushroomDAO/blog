from pathlib import Path
import json,shutil,datetime
p=Path(__file__).parent; r=p/'research';r.mkdir(exist_ok=True)
up=Path('/tmp/brief2mp4-20261119');slug='brief2mp4-agent-motion-graphics-verification-guide'
job='cb9807fa-444c-4ea6-bb71-6e756882fa97'
for f in ['README.md','LICENSE','VERSION','docs/architecture.md','plugin/skills/brief2mp4/SKILL.md','plugin/skills/brief2mp4/scripts/check_delivery.sh','plugin/skills/brief2mp4/scripts/finish.sh','plugin/skills/brief2mp4/scripts/contact_sheet.sh','plugin/skills/brief2mp4/scripts/art_route.py']:
 shutil.copy2(up/f,r/f.replace('/','--'))
saved=[]
for f in ['banner.png','architecture.png','art-forms.jpg','brief01-stills.png','example05-explainer.png','example06-short.png','edit-pack-recipes.png','social-preview.png']:
 dest=Path('/Users/jason/.heinu1-bot/media')/('brief2mp4-20261119-'+f);shutil.copy2(up/'assets'/f,dest);saved.append(str(dest))
(p/'saved-files.json').write_text(json.dumps(saved,indent=2))
(p/'slugs.json').write_text(json.dumps([slug]))
(p/'source-pin.json').write_text(json.dumps({'source':'https://github.com/qualixar/brief2mp4','revision':'a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6','version':'0.4.0','license':'MIT','reachDoctor':'agent-reach: command not found; archived agent-reach skill public-native-first; full native README and pinned git checkout fetched','dedup':'Exact URL/entity only incoming rawKB; no article, remote draft or local receipt. Published API48001 unavailable. Generic GitHub duplicate was false positive.','saved_files':saved},ensure_ascii=False,indent=2))
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=mem/f'project_{slug}.md'
f.write_text(f'''---
name: brief2mp4 checked motion graphics workflow
description: MIT agent skill routing briefs through renderers and evidence based delivery checks.
type: project
---
# brief2mp4
Source: https://github.com/qualixar/brief2mp4
Revision: a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6; version0.4.0; MIT; author Varun Pratap Bhardwaj.
Slug: {slug}
Date: 2026-11-19
Dedup: exactURL/entity finds incoming rawKB only, no existing article/localreceipt/remotedraft. Published API48001 unavailable; no priorcredential to reconcile.
Agent skill, not a new text-to-video model. Spec then per-beat route HyperFrames/Three.js/optional3D/Blender, ffmpeg finish and delivery measurements plus actual visual review, at most3fixrounds. Every frame function of time, seeded variation, baked physics.30style recipes/31demos not30trainedmodels. Standards PASS does not prove requirement semantics; dark/frozen warnings notblocking. Local rendering does not make cloud coding agent offline. MIT excludes separately licensed dependencies/assets/fonts/music.
Blog pending. WeChat pending. Semantic pending. Original-code targeted tests and actual ffmpeg finish/check positive/negative controls planned; no full agent-generated video or optional3D/Blender proof.
''')
index=mem/'MEMORY.md';s=index.read_text()
if f.name not in s:index.write_text(s+f'\n- [brief2mp4 checked videos]({f.name}) — MIT skill, deterministic rendering and delivery-check boundaries.\n')
old=p.parent/'20261119-minimind';oldslug='minimind-64m-llm-training-from-scratch-guide'
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('38001a13-a161-45df-8675-d6e8e5326029',job)
 if name=='remote-preflight.cjs':
  a=s.index('const matches=');b=s.index('const{data:p}',a);s=s[:a]+f'const matches=items.filter(x=>/qualixar\\/brief2mp4|{slug}|brief2mp4/i.test(JSON.stringify(x)));'+s[b:]
 if name=='check-semantic.py':s=s.replace('MiniMind64M jingyaogong 从零预训练 SFT 教学 参数量','brief2mp4 qualixar 动效视频 规格 验收 渲染')
 (p/name).write_text(s)
print(json.dumps({'slug':slug,'savedFiles':len(saved),'memory':str(f)}))
