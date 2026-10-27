from pathlib import Path
import urllib.request,json,re,datetime
root=Path(__file__).resolve().parents[2];rows=[]
for slug,q,archive in [('magpie-multi-agent-model-gateway','Magpie 本地网关 多模型 账号路由 Library 配置资源','magpie'),('postiz-agentic-social-media-scheduling-open-source','Postiz 被炒后泄露源码核查 2024年官方开源公告','postiz-update')]:
 req=urllib.request.Request('https://blog.mushroom.cv/api/search',data=json.dumps({'query':q}).encode(),headers={'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'})
 data=json.load(urllib.request.urlopen(req,timeout=45));p=root/'source'/('20261027-'+archive);(p/'semantic-live-response.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 matches=[x for x in data.get('results',[])if x.get('article_id')==slug];expected=json.loads(re.search(r'^title: (.*)',(root/'src/content/blog'/f'{slug}.md').read_text(),re.M)[1]);match=next((x for x in matches if x.get('title')==expected),None);rows.append({'slug':slug,'foundCurrentTitle':bool(match),'match':match,'query':q})
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':rows};Path(__file__).with_name('semantic-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False));assert all(x['foundCurrentTitle']for x in rows)
