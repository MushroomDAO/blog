from pathlib import Path
import urllib.request,re,json,html,datetime
BASE='https://blog.mushroom.cv';slugs=['magpie-multi-agent-model-gateway','postiz-agentic-social-media-scheduling-open-source']
def get(u):
 r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=40);return r.status,r.read().decode()
_,home=get(BASE+'/');start=home.index('id="carouselContainer"');end=home.index('id="carouselDots"',start);slides=list(dict.fromkeys(re.findall(r'href="(/blog/[^" ]+)"',home[start:end])));assert len(slides)==8
_,listing=get(BASE+'/blog/');links=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',listing)))
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'carouselSlides':slides,'articles':[]}
for slug in slugs:
 url=BASE+'/blog/'+slug+'/';status,body=get(url);assert status==200 and '本文原文' in body
 expected=json.loads(re.search(r'^title: (.*)',(Path(__file__).resolve().parents[2]/'src/content/blog'/f'{slug}.md').read_text(),re.M)[1]);assert html.unescape(re.search(r'<title>(.*?)</title>',body,re.S)[1])==expected,slug
 assert '/blog/'+slug+'/'in slides
 images=set(re.findall(r'(?:https://blog\.mushroom\.cv)?/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',body));assert len(images)>=4,(slug,images)
 assets=[]
 for p in sorted(images):
  u=p if p.startswith('https://')else BASE+html.unescape(p);r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification'}),timeout=30);assert r.status==200;assets.append({'url':u,'HTTP':r.status})
 route='/blog/'+slug+'/';rank=links.index(route)+1 if route in links else None
 if slug.startswith('magpie'):assert rank is not None and rank<=8
 out['articles'].append({'slug':slug,'url':url,'HTTP':status,'images':assets,'blogListRank':rank,'carouselRank':slides.index(route)+1})
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
