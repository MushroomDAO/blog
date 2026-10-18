from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parent;p=b/'board-v03.json';d=json.loads(p.read_text());rs=sorted(d['models'],key=lambda r:r['v'],reverse=True);e=d['formula']['equating'];w=d['weights'];checks=[]
for r in rs:
 S=e['public']['mean']+e['public']['sd']*(r['same_skills']-e['same_skills']['mean'])/e['same_skills']['sd']
 O=e['public']['mean']+e['public']['sd']*(r['new_domains']-e['new_domains']['mean'])/e['new_domains']['sd']
 full=max(0,w['public']*r['pub']+w['same_skills']*S+w['new_domains']*O);checks.append({'name':r['name'],'published':r['v'],'recomputed':full,'difference':abs(full-r['v'])})
out={'label':d['label'],'generatedUTC':d['generated_utc'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'entries':len(rs),'top10':rs[:10],'formula':d['formula'],'weights':w,'maxRoundedDataDifference':max(r['difference'] for r in checks),'checks':checks};assert out['maxRoundedDataDifference']<0.03,out['maxRoundedDataDifference'];(b/'board-recomputed.json').write_text(json.dumps(out,indent=2));print({k:out[k] for k in ['label','generatedUTC','entries','maxRoundedDataDifference']})
