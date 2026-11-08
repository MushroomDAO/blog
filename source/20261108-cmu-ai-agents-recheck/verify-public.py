from pathlib import Path
import urllib.request,json,re,datetime
s='cmu-11-768-ai-agents-fall-2026-neubig-openhands-harness-rl-course';j=Path('/Users/jason/.heinu1-bot/jobs/f18214a6-db42-46ff-9e5a-9edcd2480ece');url='https://blog.mushroom.cv/blog/'+s+'/'
def get(u,data=None):
 r=urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(data).encode() if data else None,headers={'User-Agent':'Mycelium-Publish-Verification','Content-Type':'application/json'}),timeout=45);return r.status,r.read()
status,b=get(url);html=b.decode();assert status==200 and 'CMU 11-768' in html
paths=sorted(set(re.findall(r'(?:src|href|content)=["\'](/_astro/[^"\']+)["\']',html)));paths=[p for p in paths if s in p and re.search(r'\.(?:jpg|png|webp)',p)];images=[]
for p in paths:
 st,bb=get('https://blog.mushroom.cv'+p);assert st==200;images.append({'path':p,'status':st,'bytes':len(bb)})
assert images
st,feed=get('https://blog.mushroom.cv/api/agent-feed');listed=s in feed.decode();assert listed
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blogUrl':url,'status':status,'reused':True,'newDeploy':False,'images':images,'listedInPublicAgentFeed':listed};(j/'public-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
st,b=get('https://blog.mushroom.cv/api/search',{'query':'CMU 11-768 AI Agents Graham Neubig Daniel Fried course'});x=json.loads(b);hit=s in b.decode();(j/'semantic-verification.json').write_text(json.dumps({'existingIndexReused':hit,'publicSearchVerified':hit,'results':x},ensure_ascii=False,indent=2));print('Semantic hit',hit)
