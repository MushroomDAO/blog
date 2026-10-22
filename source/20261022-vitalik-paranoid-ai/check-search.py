from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent;slug='vitalik-paranoid-ai-zkapi-tor';p=b/'semantic-search-check.json';prior=json.loads(p.read_text()) if p.exists() else {}
if prior.get('found'):print(prior['match']);raise SystemExit(0)
for query in ['Vitalik AI偏执模式 zkAPI Tor 本地提示词改写 隐私边界','paranoid AI zkAPI Tor local prompt reconstruction privacy deployment']:
 r=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':query})],text=True,capture_output=True)
 if r.returncode:continue
 d=json.loads(r.stdout);matches=[{'rank':i,'score':x.get('score'),'article_id':x.get('article_id')}for i,x in enumerate(d.get('results',[]),1)if x.get('article_id')==slug];out={'query':query,'found':bool(matches),'match':matches[0]if matches else None};p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if matches:break
print(out)
