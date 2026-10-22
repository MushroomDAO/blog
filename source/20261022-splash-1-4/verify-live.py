from pathlib import Path
import subprocess,re,json
b=Path(__file__).resolve().parent;slug='specialized-inference-engines-rise-hardware-specific-llm-optimization';base='https://blog.mushroom.cv';url=base+'/blog/'+slug+'/'
def get(u,p):
 status=subprocess.check_output(['curl','-LsS','--compressed','-o',str(p),'-w','%{http_code}',u],text=True);return int(status),p.read_bytes()
status,raw=get(url,Path('/tmp/splash-current-page'));h=raw.decode();prefixes=['specialized-inference-engines-rise-llm-hardware-optimization-banner','splash-1-4-update-fig-'];assets=sorted(set(x for x in re.findall(r'(?:src|href)="([^" ]*\.(?:webp|jpg|png))"',h)if any(p in x for p in prefixes)));r={'slug':slug,'url':url,'status':status,'images':[]}
for i,a in enumerate(assets):
 u=base+a if a.startswith('/')else a;c,d=get(u,Path('/tmp/splash-asset-'+str(i)));r['images'].append({'url':u,'status':c,'bytes':len(d)})
_,lr=get(base+'/blog/',Path('/tmp/splash-list'));links=list(dict.fromkeys(re.findall(r'/blog/[a-zA-Z0-9-]+/',lr.decode())));r['listPosition']=links.index('/blog/'+slug+'/')+1 if '/blog/'+slug+'/'in links else None
r.update({'englishUpdate':'What does the Splash 1.4.0 benchmark measure?'in h,'benchmarkConditions':'1,312'in h and 'Q2_0'in h,'verificationMode':'--verify-rows all'in h,'localScope':'No model was downloaded'in h,'pinnedSource':'1482f6bbc2abf12375332725302019594150b6cb'in h,'preservedOriginalPubDate':'datetime="2026-10-05T00:00:00.000Z"'in h,'updatedDate':'datetime="2026-10-22T00:00:00.000Z"'in h})
assert status==200 and len(r['images'])==4 and all(x['status']==200 for x in r['images'])and r['listPosition']is not None,r
assert all(r[k]for k in ['englishUpdate','benchmarkConditions','verificationMode','localScope','pinnedSource','preservedOriginalPubDate','updatedDate']),r
(b/'live-verification.json').write_text(json.dumps(r,indent=2));print('Live update,4images200,list',r['listPosition'])
