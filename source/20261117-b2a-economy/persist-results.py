from pathlib import Path
import json,datetime
s=Path(__file__).parent;root=s.resolve().parents[1];slug='a16z-b2a-economy-agent-customers-commerce';j=Path('/Users/jason/.heinu1-bot/jobs/1b58ca7e-62aa-46d9-bc79-24471fa6a39a')
rec=json.loads((root/'pipeline/m2/output'/f'{slug}.json').read_text());assert len(json.loads((s/'wechat-verification.json').read_text())['drafts'])==1
assert json.loads((s/'semantic-status.json').read_text())['status']=='verified'
assert json.loads((s/'public-verification.json').read_text())['articles'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':rec['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for base in [s,j]:(base/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(j/'publication-progress.json').write_text(json.dumps({**r,'blogVerified':True,'wechatVerified':True,'semanticStatus':'verified','completed':False,'phase':'KB-and-git-finalization','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2))
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md');t=p.read_text().replace('Status: researching; exact source/entity duplicate check clear.','Status: published; Blog/list/images and complete remote WeChat body/metadata verified.\nBlog: '+r['blogUrl']+'\nWeChat: draft\nMedia ID: '+rec['mediaId']+'\nSemantic: verified\nKB: persisted and indexed after publication.')
t+='\nFinal: a16zauthor/date verified, brief thesis attribution not fulltranslation; own original4gateframework andbusinessmetrics, no marketgrowthclaim accepted as ownmeasurement. ACPbetadocssnapshot2026-04-17sha7fdd78df677a94dce04c770644b0fbbb1401272b documentreviewnotmerchantintegration. Hypothetical1000reads/100quotes/20paid/2refund=18retained,20%quoteconversion/1.8%readretention, clearlynotobserveddata. No realpayments/account/liveAPI/ROIorperformancetest. ResearchcategoryLittleJfigures3pluslocalFLUX8702conceptbanner. BilingualSEO/Blogtitle/list/images/2semanticvectors/search/currentcompleteWeChattext3orderedimages/metadataverified.\n';p.write_text(t)
(s/'.published').write_text(r['blogUrl']+'\n');print(json.dumps(r,ensure_ascii=False))
