"""Write final receipts after public assets and the current remote draft are verified."""
from pathlib import Path
import json,datetime,shutil
s=Path(__file__).resolve().parent
slug='nvidia-openshell-agent-runtime'
p=json.loads((s/'public-verification.json').read_text())['articles'][0]
w=json.loads((s/'wechat-verification.json').read_text())['drafts'][0]
assert p['HTTP']==200 and p['carouselRank']==1 and w['fullTextMatches'] and w['coverMatches']
r={'slug':slug,'blogUrl':'https://blog.mushroom.cv/blog/'+slug+'/','mediaId':w['mediaId'],'wechatStatus':'draft','wechatError':''}
(s/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
job=Path('/Users/jason/.heinu1-bot/jobs/29868b1d-03d9-4c13-a81b-da33c734f5a8');job.mkdir(exist_ok=True,parents=True)
(job/'publication-result.json').write_text(json.dumps({**r,'results':[r]},ensure_ascii=False,indent=2)+'\n')
(s/'.published').write_text('2026-10-24\n'+r['blogUrl']+'\n')
(s/'.state.json').write_text(json.dumps({'status':'published','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**r},ensure_ascii=False,indent=2)+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md')
t=m.read_text().replace('Blog pending; WeChat pending; raw material already bot-KB saved.', 'Blog '+r['blogUrl']+' verifiedHTTP200, homepagecarousel1, allimages200. WeChat currentdraft '+r['mediaId']+' independently verified full visible body, image identities/order, metadata, cover and comments. OriginalrawKBreused. Three offline v0.1.5 prover checks passed expected outcomes0/1/3; no live sandbox or agent security test.');m.write_text(t)
shutil.copy(m,Path('/tmp/openshell-memory-only')/m.name)
feedback=Path('.agents/skills/forage/FEEDBACK.md')
entry='\n\n## 2026-10-24 — NVIDIA OpenShell agent runtime\n\n- '+r['blogUrl']+' Apache2.0; official stablev0.1.5 downloaded and SHA256verified. Three actual standalone policy checks: within_boundary0, exceeds_boundary1 with /tmp write counterexample, unresolved nested path unsupported3. Not live sandbox enforcement or escape/security audit. Official main source pinned. Generated topic cover plus3XiaoM figures, bilingualSEO. Public route/assets/carousel, remote draft fulltext/images/metadata/cover/comments and semanticsearch verified; rawKBreused, exactsource/entity dedupno oldpublication. Task29868b1d-03d9-4c13-a81b-da33c734f5a8.\n'
if r['blogUrl'] not in feedback.read_text():feedback.write_text(feedback.read_text().rstrip()+entry)
print(json.dumps(r))
