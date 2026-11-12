from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent;slug='anthropic-employment-ai-expectations-reports';prior=json.loads((b/'semantic-search-check.json').read_text()) if (b/'semantic-search-check.json').exists() else {}
if prior.get('found'):
 print(prior['match']);raise SystemExit(0)
for q in ['Anthropic employment and AI expectations a close reading','Anthropic 27% 9% junior hiring agent hours expectations 75% 28%']:
 r=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':q})],text=True,capture_output=True)
 if r.returncode:continue
 d=json.loads(r.stdout);rs=d.get('results',[]);matches=[{'rank':i,'score':x.get('score'),'article_id':x.get('article_id')} for i,x in enumerate(rs,1) if x.get('article_id')==slug];out={'query':q,'found':bool(matches),'match':matches[0] if matches else None,'response':d};(b/'semantic-search-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 if matches:break
print({k:out[k] for k in ['query','found','match']})
