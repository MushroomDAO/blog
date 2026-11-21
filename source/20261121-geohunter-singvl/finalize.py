from pathlib import Path
import json,datetime,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slugs=json.loads((out/'slugs.json').read_text());w=json.loads((out/'wechat-verification.json').read_text());sem=json.loads((out/'semantic-status.json').read_text());memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');results=[]
for slug in slugs:
 row=next(x for x in w['drafts']if x['slug']==slug);assert row['fullTextMatches']and row['coverMatches']and row['imageIdentitiesMatch'];url=f'https://blog.mushroom.cv/blog/{slug}/';r={'slug':slug,'blogUrl':url,'mediaId':row['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':'','semanticStatus':sem['status'],'checkedAt':w['checkedAt']};results.append(r)
 p=memory/f'project_{slug}.md';s=p.read_text();s=s.replace('Blog/WeChat/semantic pending.','')
 if slug.startswith('geohunter'):
  s=s.replace('No Blog deployment, no WeChat draft; user message explicitly prohibits both despite mentioning default three-channel workflow.','User subsequently explicitly authorized full publication; automatic routing boundary removed at user request.')
 s+='\nBlog: verified '+url+'\nWeChat: draft '+row['mediaId']+'; current full text, ordered3images,cover,metadata,source,comments verified '+w['checkedAt']+'.\nSemantic: '+sem['status']+'\nPublication proof: source/20261121-geohunter-singvl.\n';p.write_text(s)
(out/'publication-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));(out/'.published').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
job=Path('/Users/jason/.heinu1-bot/jobs/geohunter-draft-20261121');(job/'publication-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));Path('/Users/jason/.heinu1-bot/jobs/singvl-s1-4b-20261121/publication-result.json').write_text(json.dumps(results[1],ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
