from pathlib import Path
import urllib.request,json,re,html,yaml,datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slug='copilotkit-frontend-stack-agents-guide';base='https://blog.mushroom.cv'
def get(u,data=None):
 r=urllib.request.urlopen(urllib.request.Request(u,data=data,headers={'User-Agent':'Mycelium-Publish-Verification','Content-Type':'application/json','Cache-Control':'no-cache'}),timeout=45);return r,r.read()
r,b=get(base+'/blog/'+slug+'/');s=b.decode();f=yaml.safe_load((root/f'src/content/blog/{slug}.md').read_text().split('---')[1]);title=html.unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1]);assert r.status==200 and title==f['title'];assert 'never-opened'in s and '9 月 18 日'in s and '2026-11-18'in s
images=sorted(set(html.unescape(x)for x in re.findall(r'/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',s)));assert len(images)>=4;assets=[]
for p in images:
 a,d=get(base+p);assert a.status==200 and a.headers.get('Content-Type','').startswith('image/');assets.append({'path':p,'status':a.status,'bytes':len(d)})
payload={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'search_posts','arguments':{'query':'ag-ui-protocol/ag-ui','limit':20}}};_,b=get(base+'/api/mcp',json.dumps(payload).encode());catalog=json.loads(b);rows=json.loads(catalog['result']['content'][0]['text'])['results'];target=next(x for x in rows if x['id']==slug);assert target['title']==f['title'];assert target['pubDate'].startswith('2026-07-19') and target['updatedDate'].startswith('2026-11-18')
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'slug':slug,'blogUrl':base+'/blog/'+slug+'/','status':r.status,'title':title,'catalogEntry':target,'originalPubDatePreserved':True,'notNewPost':True,'images':assets};(out/'public-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
