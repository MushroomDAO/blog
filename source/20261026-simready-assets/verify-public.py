from pathlib import Path
import urllib.request,re,json,concurrent.futures,html,datetime
BASE='https://blog.mushroom.cv'
def get(url):
 r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=30);return r.status,r.read().decode('utf-8')
slugs=['nvidia-simready-assets-audit'];out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'articles':[]}
_,listing=get(BASE+'/blog/');links=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',listing)))
_,home=get(BASE+'/')
start=home.index('id="carouselContainer"');end=home.index('id="carouselDots"',start)
slides=list(dict.fromkeys(re.findall(r'href="(/blog/[^" ]+)"',home[start:end])))
assert len(slides)==8
out['carouselSlides']=slides
assert set('/blog/'+x+'/' for x in slugs)<=set(slides[:1]),slides
for slug in slugs:
 url=BASE+'/blog/'+slug+'/';status,body=get(url);assert status==200
 assert '本文原文' in body
 images=set(re.findall(r'(?:https://blog\.mushroom\.cv)?/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',body))
 assert len(images)>=4,(slug,images)
 assets=[]
 for path in sorted(images):
  u=path if path.startswith('https://')else BASE+html.unescape(path)
  r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification'}),timeout=20);assert r.status==200;assets.append({'url':u,'HTTP':r.status})
 route='/blog/'+slug+'/';rank=links.index(route)+1;assert rank<=8,(slug,rank)
 assert ('href="'+route+'"')in home
 out['articles'].append({'slug':slug,'url':url,'HTTP':status,'images':assets,'blogListRank':rank,'homepageContainsArticle':True,'carouselRank':slides.index(route)+1})
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
