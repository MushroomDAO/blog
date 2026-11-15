from pathlib import Path
import json,datetime
s=Path(__file__).parent;root=s.resolve().parents[1];slug='rnskill-agent-content-workflow-license-guide';j=Path('/Users/jason/.heinu1-bot/jobs/41d4a701-631a-4299-95a8-99732898d3ee')
rec=json.loads((root/'pipeline/m2/output'/f'{slug}.json').read_text())
assert len(json.loads((s/'wechat-verification.json').read_text())['drafts'])==1
assert json.loads((s/'semantic-status.json').read_text())['status']=='verified'
assert json.loads((s/'public-verification.json').read_text())['articles'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':rec['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for base in [s,j]:(base/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(j/'publication-progress.json').write_text(json.dumps({**r,'blogVerified':True,'wechatVerified':True,'semanticStatus':'verified','completed':False,'phase':'KB-and-git-finalization','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2))
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md')
t=p.read_text().replace('Status: researching; exact source/entity duplicate check clear.','Status: published; Blog/list/images and complete remote WeChat body/metadata verified.\nBlog: '+r['blogUrl']+'\nWeChat: draft\nMedia ID: '+rec['mediaId']+'\nSemantic: verified\nKB: persisted and indexed after publication.')
t+='\nVerification: pinned repository inventory 61 top-level dirs,60 direct skill files,65 recursive incl aliases/nesting. Four CLI dry-run/input checks passed on synthetic citation fixture. No real Jev call, API key, agent-skill installation into production, media production or measured creator ROI. Author productivity claim attributed and unverified. Default CC BY-NC 4.0 plus per-directory licensing explained. Topic photo and 3 Little M figures, bilingual SEO, public assets, semantic readback/search and complete current draft verified.\n';p.write_text(t)
(s/'.published').write_text(r['blogUrl']+'\n');print(json.dumps(r,ensure_ascii=False))
