"""Finalize records only after independent public and remote-draft verification."""
from pathlib import Path
import json,datetime,shutil
s=Path(__file__).resolve().parent
root=s.parent.parent
slug='nvidia-flare-local-inference'
pub=json.loads((s/'public-verification.json').read_text())
wechat=json.loads((s/'wechat-verification.json').read_text())['drafts'][0]
assert pub['articles'][0]['HTTP']==200 and wechat['fullTextMatches'] and wechat['coverMatches']
result={'slug':slug,'blogUrl':'https://blog.mushroom.cv/blog/'+slug+'/','mediaId':wechat['mediaId'],'wechatStatus':'draft'}
(s/'publication-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
job=Path('/Users/jason/.heinu1-bot/jobs/5999f84f-9add-4456-a6f0-41d44574d531');job.mkdir(parents=True,exist_ok=True)
(job/'publication-result.json').write_text(json.dumps({**result,'results':[result]},ensure_ascii=False,indent=2)+'\n')
(s/'.published').write_text('2026-10-23\n'+result['blogUrl']+'\n')
(s/'.state.json').write_text(json.dumps({'status':'published','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**result},ensure_ascii=False,indent=2)+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md')
t=m.read_text().replace('Blog: pending. WeChat: pending; no old creation ID.', 'Blog: '+result['blogUrl']+' HTTP200, homepage carousel rank1, images200. WeChat: current remote draft verified, '+result['mediaId']+'. Full body, ordered images, title, digest, author, cover and comments verified; no duplicate creation. CLI-only checks, no GPU inference. Jina fallback used because agent-reach unavailable.');m.write_text(t)
shutil.copy(m,Path('/tmp/flare-memory-only')/m.name)
print(json.dumps(result))
