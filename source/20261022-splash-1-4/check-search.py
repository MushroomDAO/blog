from pathlib import Path
import json,subprocess
b=Path(__file__).resolve().parent;slug='specialized-inference-engines-rise-hardware-specific-llm-optimization';p=b/'semantic-search-check.json'
if p.exists() and json.loads(p.read_text()).get('found'):print(json.loads(p.read_text())['match']);raise SystemExit(0)
for q in ['Splash1.4.0 Flash-Next Q2_0 95tok/s 1312 SSD PLE KV','Splash1.4.0 update cache TTFT Flash-Next reproducibility']:
 r=subprocess.run(['curl','-fsS','--max-time','35','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':q})],text=True,capture_output=True)
 if r.returncode:continue
 d=json.loads(r.stdout);matches=[{'rank':i,'score':x.get('score'),'article_id':x.get('article_id')}for i,x in enumerate(d.get('results',[]),1)if x.get('article_id')==slug];out={'query':q,'found':bool(matches),'match':matches[0]if matches else None};p.write_text(json.dumps(out,ensure_ascii=False,indent=2))
 if matches:break
print(out)
