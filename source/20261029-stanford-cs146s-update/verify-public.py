from pathlib import Path
import urllib.request,re,json,html,datetime
BASE='https://blog.mushroom.cv';slug='stanford-cs146s-modern-software-developer-ai-coding-agent-mcp-course';route='/blog/'+slug+'/'
def get(u):
 r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=45)
 return r,r.read()
r,b=get(BASE+route);s=b.decode();assert r.status==200
expected='斯坦福 CS146S 2026：从最小编程代理到中文学习笔记'
assert html.unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1])==expected
assert 'FL-Bin/stanford-ai-course' in s and 'CC BY-NC-SA' in s
_,b=get(BASE+'/');home=b.decode();start=home.index('id="carouselContainer"');end=home.index('id="carouselDots"',start);slides=list(dict.fromkeys(re.findall(r'href="(/blog/[^" ]+)"',home[start:end])));assert route in slides
_,b=get(BASE+'/blog/');links=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',b.decode())))
images=set(re.findall(r'/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',s));assert len(images)>=4
assets=[]
for p in sorted(images):
 r,b=get(BASE+html.unescape(p));assert r.status==200 and r.headers.get('Content-Type','').startswith('image/')
 assets.append({'url':BASE+p,'status':r.status,'contentType':r.headers['Content-Type'],'bytes':len(b)})
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':BASE+route,'actualTitle':expected,'carouselRank':slides.index(route)+1,'blogListRank':links.index(route)+1 if route in links else 'original pubDate retained, beyond first page','images':assets}
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
