from pathlib import Path
import json,datetime
slug='n8n-nod-local-personal-agent-engineering-guide'
o=Path(__file__).parent
job=Path('/Users/jason/.heinu1-bot/jobs/9a6dc6ac-8633-4b85-ae9f-4058b79a1566')
r=json.loads(Path('pipeline/m2/output',slug+'.json').read_text())
v=json.loads((o/'wechat-verification.json').read_text())
assert v['drafts'][0]['mediaId']==r['mediaId']
assert json.loads((o/'public-verification.json').read_text())['articles'][0]['slug']==slug
sem=json.loads((o/'semantic-status.json').read_text())
result={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':r['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [o/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(o/'.published').write_text(result['blogUrl']+'\n')
(job/'publication-progress.json').write_text(json.dumps({**result,'blogVerified':True,'wechatVerified':True,'semantic':sem,'completed':sem['status']=='verified' and (o/'kb-readback.json').exists(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md'
t=p.read_text().split('\nFinal channels:')[0].replace('Blog/WeChat: pending.','Channel status below.')
p.write_text(t+'\nFinal channels:\nBlog: '+result['blogUrl']+'\nWeChat remote draft verified: '+r['mediaId']+'\nSemantic: '+sem['status']+'\nPinnede91aea2b9bc5c3e78640f87064f44a1b907859ec Apache2officialNod standaloneoneowner. Pi/Fastify/React/Electron/PostgreSQL/pg-boss workspace+browsercontainers. 16offlineupstreamtrust-jev checks pass usingmockproviders/zod4.6.7; architectureimportcheckpassTypeScript6.0.3. Nofullappinstall/DB/VM/browser/realmodel/accounts/payments/fullsecurityaudit/benchmarkreplication. Author98%678simulatedruns226errands/3repeats notrealaccounts;93.2%=466/500LongMemEvalS memory nottaskcompletion;418authorholdoutscope retained;0/216memoryinjection and240/240checker bounded. Basicanalyticsdefaulton,tracesoff, externalmodel/connectors/checkersflows explicit. KnownpricedAPI-onlymonthlyscope, in-flightworkcanfinish,5dollarcheckinnotstrictcap. DesktopvsDocker/source and64Ktoolmodelcontext requirements separated, laptop sleeps stopswork. Agent-reach absent; directHTML+Jina200;4CDNimages403fallbackpinnedrepoPNG originals andblogheader downloaded5mediafiles. Officialpaperdotcollagecover92423B adopted and3LittleMfigs machine/manualverified. No masssend.\n')
