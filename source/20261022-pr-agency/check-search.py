from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent;slug='pr-agency-founder-communications-playbook';p=b/'semantic-search-check.json';prior=json.loads(p.read_text()) if p.exists() else {}
if prior.get('found'):
 print(prior['match']);raise SystemExit(0)
for query in ['公关外援 创始人故事主导权 Lulu Meservey 中小企业实践','PR agency SME narrative brief supplier budget business evidence90daypilot']:
 r=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':query})],text=True,capture_output=True)
 if r.returncode:continue
 d=json.loads(r.stdout);matches=[{'rank':i,'score':x.get('score'),'article_id':x.get('article_id')} for i,x in enumerate(d.get('results',[]),1) if x.get('article_id')==slug];out={'query':query,'found':bool(matches),'match':matches[0] if matches else None};p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if matches:break
print(out)
