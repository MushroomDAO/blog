from pathlib import Path
import json,datetime
p=Path(__file__).parent;slug=json.loads((p/'slugs.json').read_text())[0];job=Path('/Users/jason/.heinu1-bot/jobs/e87ef8e5-8623-49a7-9a94-00ad3a756676');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
a=json.loads((p/'public-verification.json').read_text());w=json.loads((p/'wechat-verification.json').read_text());s=json.loads((p/'semantic-status.json').read_text());assert a['articles'][0]['slug']==slug and w['drafts'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':w['drafts'][0]['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':'','semanticStatus':s['status'],'checkedAt':now,'repositoryStatus':'pending-push-and-review'}
for f in [p/'publication-result.json',job/'publication-result.json']:f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md';text=memory.read_text();text=text.replace('Blog pending. WeChat pending. Semantic pending.',f'''Blog: verified {r['blogUrl']}
WeChat: draft {r['mediaId']}; full currentbody/metadata/ordered3images/cover/sourceURL verified at {w['checkedAt']}.
Semantic: {s['status']}
Source: source/20261119-clover ; full20pagepaper privately archived,6officialfigure downloads in saved-files.json. AgentReachCLIunavailable; archivedskill publicnativefirst route used.
FLUX8821cover+3separate LittleM bodyfigures machine/manual approved. Prior11articles preserved.
Decision variant described in report is planned for subsequentrelease; no claiming it is currentpublicSFT.
Repository: feature PR pending. Reuse results on retry; do not republish, redraft or re-embed blindly.''');memory.write_text(text)
(p/'.published').write_text(r['blogUrl']+'\n'+now+'\n');(job/'publication-progress.json').write_text(json.dumps({'completed':False,'phase':'finalizing-repository','channelsCompleted':True,'blogVerified':True,'wechatVerified':True,'semanticVerified':s['status']=='verified','kbUpdated':True,'mainMerged':False,'retryScope':'repository bookkeeping only; no new Blog/draft/embedding','updatedAt':now},indent=2));print(json.dumps(r,ensure_ascii=False))
