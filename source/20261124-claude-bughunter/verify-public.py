from pathlib import Path
import urllib.request,re,json,html,datetime,yaml
BASE='https://blog.mushroom.cv';slugs=['claude-bughunter-skills-evidence-scope-review'];root=Path(__file__).resolve().parents[2]
def get(u):
 import subprocess,tempfile,email,types
 with tempfile.TemporaryDirectory() as d:
  h=Path(d)/'headers';body=Path(d)/'body'
  subprocess.run(['curl','-fsSL','--compressed','--max-time','120','-A','Mycelium-Publish-Verification','-H','Cache-Control: no-cache','-D',str(h),'-o',str(body),u],check=True)
  block=h.read_text().strip().split('\n\n')[-1];lines=block.splitlines();headers=email.message_from_string('\n'.join(lines[1:]))
  return types.SimpleNamespace(status=int(lines[0].split()[1]),headers=headers),body.read_bytes()
_,b=get(BASE+'/');home=b.decode();i=home.index('id="carouselContainer"');e=home.index('id="carouselDots"',i);slides=list(dict.fromkeys(re.findall(r'href="(/blog/[^" ]+)"',home[i:e])))
_,b=get(BASE+'/blog/');links=list(dict.fromkeys(re.findall(r'href=["\'](/blog/[a-z0-9-]+/)["\']',b.decode())))
out={'orderingNote':'List uses same-day date sorting; actual lastPublishedAt records publication time for carousel ordering.', 'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'articles':[]}
for slug in slugs:
 route='/blog/'+slug+'/';r,b=get(BASE+route);s=b.decode();expected=yaml.safe_load((root/'src/content/blog'/f'{slug}.md').read_text().split('---')[1])['title'];actual=html.unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1]);assert r.status==200 and actual==expected, {"status":r.status,"actualTitle":actual,"expectedTitle":expected}
 assert route in slides and route in links and links.index(route)<10
 images=set(re.findall(r'/_astro/[^"\s<> ,]*'+slug+r'[^"\s<> ,]*',s));assert len(images)>=4
 assets=[]
 for p in sorted(images):
  a,d=get(BASE+html.unescape(p));assert a.status==200 and a.headers.get('Content-Type','').startswith('image/');assets.append({'url':BASE+p,'status':a.status,'contentType':a.headers['Content-Type'],'bytes':len(d)})
 out['articles'].append({'slug':slug,'url':BASE+route,'title':actual,'listRank':links.index(route)+1,'carouselRank':slides.index(route)+1,'images':assets})
Path(__file__).with_name('public-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
