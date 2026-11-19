from pathlib import Path
import json,datetime
p=Path(__file__).parent;root=p.resolve().parents[1];slug=json.loads((p/'slugs.json').read_text())[0]
job=Path('/Users/jason/.heinu1-bot/jobs/00613c57-ed07-4b19-8cfd-1fe57eff41a9');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
public=json.loads((p/'public-verification.json').read_text());wechat=json.loads((p/'wechat-verification.json').read_text());semantic=json.loads((p/'semantic-status.json').read_text())
assert public['articles'][0]['slug']==slug and wechat['drafts'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':wechat['drafts'][0]['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':'','semanticStatus':semantic['status'],'checkedAt':now,'repositoryStatus':'pending-feature-push-and-review'}
for dest in [p/'publication-result.json',job/'publication-result.json']:dest.write_text(json.dumps(r,ensure_ascii=False,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md'
s=memory.read_text();s=s.replace('Blog pending; WeChat pending; semantic pending. Template-only verification planned, no real-weight inference/performance reproduction.',f'''Blog: verified {r['blogUrl']}
WeChat: draft {r['mediaId']}; full current draft body, metadata, ordered3images and cover verified at {wechat['checkedAt']}.
Semantic: {semantic['status']}
Local verification:49 template-only cases passed, transparent Jinja generation tag extension; no Transformers execution, no weights, no audio recognition/performance reproduction.
Banner: FLUX seed8802, first8801 rejected manually for gibberish labels despite automated pass. Three separate LittleM body images compressed under90KB and manually inspected.
Source artifacts: source/20261119-rumble-2-flash ; model revision a0c34287229103b706c670d70791683e34379732.
Repository: feature PR pending. Do not recreate Blog, draft or embed on retry; verify current remote state first.''')
memory.write_text(s)
(p/'.published').write_text(r['blogUrl']+'\n'+now+'\n')
(job/'publication-progress.json').write_text(json.dumps({'completed':False,'phase':'finalizing-repository','channelsCompleted':True,'blogVerified':True,'wechatVerified':True,'semanticVerified':semantic['status']=='verified','kbUpdated':True,'mainMerged':False,'retryScope':'repository bookkeeping only; no new Blog/draft/embedding','updatedAt':now},indent=2))
print(json.dumps(r,ensure_ascii=False))
