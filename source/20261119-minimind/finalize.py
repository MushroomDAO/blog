from pathlib import Path
import json,datetime
p=Path(__file__).parent;slug=json.loads((p/'slugs.json').read_text())[0];job=Path('/Users/jason/.heinu1-bot/jobs/38001a13-a161-45df-8675-d6e8e5326029');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
a=json.loads((p/'public-verification.json').read_text());w=json.loads((p/'wechat-verification.json').read_text());s=json.loads((p/'semantic-status.json').read_text());assert a['articles'][0]['slug']==slug and w['drafts'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':w['drafts'][0]['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':'','semanticStatus':s['status'],'checkedAt':now,'repositoryStatus':'pending-push-and-review'}
for f in [p/'publication-result.json',job/'publication-result.json']:f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md';text=memory.read_text();pending='Blog pending. WeChat pending. Semantic pending. Random-weight CPU forward/backward/cache/generation smoke planned; no pretrained quality/fulltraining/3090timing replication.'
text=text.replace(pending,f'''Blog: verified {r['blogUrl']}
WeChat: draft {r['mediaId']}; full currentbody/metadata/ordered3images/cover/sourceURL verified at {w['checkedAt']}.
Semantic: {s['status']}
CPU original default63912192parameter random model:8checks passed, cache maxabs4.0531e-6; torch2.14.0/transformers5.16.1. No pretrained quality/fulltraining/3090timing replication.
Source: source/20261119-minimind ; FLUX8812+3separate LittleM body illustrations machine/manual approved.
Repository: feature PR pending. Reuse results on retry; do not republish, redraft or re-embed blindly.''');memory.write_text(text)
(p/'.published').write_text(r['blogUrl']+'\n'+now+'\n')
(job/'publication-progress.json').write_text(json.dumps({'completed':False,'phase':'finalizing-repository','channelsCompleted':True,'blogVerified':True,'wechatVerified':True,'semanticVerified':s['status']=='verified','kbUpdated':True,'mainMerged':False,'retryScope':'repository bookkeeping only; no new Blog/draft/embedding','updatedAt':now},indent=2))
print(json.dumps(r,ensure_ascii=False))
