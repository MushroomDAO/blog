from pathlib import Path
import json,subprocess,urllib.request,time
root=Path('/tmp/shisei-research');out=Path(__file__).parent
cat=json.loads(root.joinpath('data/catalog.json').read_text())
counts={'records':len(cat),'usablePoses':sum(any(p['views'].values()) for p in cat),'lineViews':sum(bool(v)for p in cat for v in p['views'].values()),'photoViews':sum(len(p.get('photos',{}))for p in cat),'mapSets':sum(len(p.get('maps',{}))for p in cat)}
assert counts=={'records':288,'usablePoses':280,'lineViews':1212,'photoViews':89,'mapSets':944}
server=subprocess.Popen(['python3','-m','http.server','18836','--bind','127.0.0.1','--directory',str(root/'site')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 time.sleep(1)
 routes=['/','/en/','/ja/','/ko/','/pose/P015/','/images/line/w900/std_P015_front.webp','/images/depth/w900/std_P001_front.webp']
 results=[]
 for route in routes:
  r=urllib.request.urlopen('http://127.0.0.1:18836'+route,timeout=15);b=r.read();assert r.status==200 and b
  results.append({'route':route,'status':r.status,'bytes':len(b),'type':r.headers.get('Content-Type')})
 out.joinpath('local-smoke.json').write_text(json.dumps({'counts':counts,'requests':results,'scope':'Static preview and asset integrity only; no browser-interaction or image-generation test'},indent=2));print(json.dumps({'counts':counts,'requestsPassed':len(results)}))
finally:
 server.terminate();server.wait()
