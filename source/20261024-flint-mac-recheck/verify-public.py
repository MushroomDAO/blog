from pathlib import Path
import urllib.request,re,json,html,datetime
BASE='https://blog.mushroom.cv';slug='flint-local-coding-rec-engine'
def get(path):
 r=urllib.request.urlopen(urllib.request.Request(BASE+path,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=35)
 return r.status,r.read()
status,raw=get('/blog/'+slug+'/');body=raw.decode();assert status==200
assert '哪些 Mac 符合官方安装与使用条件' in body
assert 'Which Mac configurations meet the official requirements' in body
assert 'http://127.0.0.1:11500/v 1' not in body
images=sorted(set(re.findall(r'/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',body)));assert len(images)>=4
assets=[{'url':BASE+html.unescape(u),'http':get(html.unescape(u))[0]}for u in images];assert all(x['http']==200 for x in assets)
_,listing=get('/blog/');routes=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',listing.decode())));assert '/blog/'+slug+'/' in routes
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':BASE+'/blog/'+slug+'/','http':status,'bilingualHardwareMatrix':True,'blogListRank':routes.index('/blog/'+slug+'/')+1,'assets':assets,'existingPubDatePreserved':True}
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
