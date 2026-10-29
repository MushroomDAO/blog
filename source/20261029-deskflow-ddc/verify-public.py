from pathlib import Path
import urllib.request,re,json,html,datetime
BASE='https://blog.mushroom.cv';slugs=['deskflow-ddc-monitor-keyboard-sharing'];root=Path(__file__).resolve().parents[2]
def get(u):
 r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=45);return r,r.read()
_,b=get(BASE+'/');home=b.decode();i=home.index('id="carouselContainer"');e=home.index('id="carouselDots"',i);slides=list(dict.fromkeys(re.findall(r'href="(/blog/[^" ]+)"',home[i:e])))
_,b=get(BASE+'/blog/');links=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',b.decode())))
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'articles':[]}
for slug in slugs:
 route='/blog/'+slug+'/';r,b=get(BASE+route);s=b.decode();expected=json.loads(re.search(r'^title: (.*)',(root/'src/content/blog'/f'{slug}.md').read_text(),re.M)[1]);actual=html.unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1]);assert r.status==200 and actual==expected
 assert route in slides and route in links and links.index(route)<8
 images=set(re.findall(r'/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',s));assert len(images)>=4
 assets=[]
 for p in sorted(images):
  a,d=get(BASE+html.unescape(p));assert a.status==200 and a.headers.get('Content-Type','').startswith('image/');assets.append({'url':BASE+p,'status':a.status,'contentType':a.headers['Content-Type'],'bytes':len(d)})
 out['articles'].append({'slug':slug,'url':BASE+route,'title':actual,'listRank':links.index(route)+1,'carouselRank':slides.index(route)+1,'images':assets})
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
