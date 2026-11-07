from pathlib import Path
import urllib.request,re,json,html,datetime
out=Path(__file__).parent;s='agentic-rl-lab-grpo-vision-post-training-low-cost-geometry';base='https://blog.mushroom.cv';url=base+'/blog/'+s+'/'
def get(url):
 r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=45);return r,r.read()
r,b=get(url);body=b.decode();assert r.status==200
assert '20-step session' in body and '5.06' in body
assets=[]
for p in sorted(set(re.findall(r'/_astro/[^"\s<> ,]*'+s+r'[^"\s<> ,]*',body))):
 a,d=get(base+html.unescape(p));assert a.status==200 and a.headers['Content-Type'].startswith('image/');assets.append({'path':p,'bytes':len(d),'status':a.status})
assert len(assets)>=4
_,b=get(base+'/blog/');listed='/blog/'+s+'/'in b.decode()
# An older article may be outside first paginated list: verify public feed search instead.
req=urllib.request.Request(base+'/api/mcp',data=json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'search_posts','arguments':{'query':'agentic-rl-lab'}}}).encode(),headers={'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'})
feed=json.load(urllib.request.urlopen(req,timeout=45));assert s in json.dumps(feed)
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blogUrl':url,'reused':True,'updated':True,'status':200,'images':assets,'firstListPage':listed,'agentFeedListed':True,'costCorrectionVerified':True};(out/'public-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report))
