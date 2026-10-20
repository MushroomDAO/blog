from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent
for slug,q in [('ascii-portrait-browser-animation','ASCII Portrait 照片 动态字符画 浏览器 Ethannju 本地 6秒'),('everything-open-source-app-suite','HeyPuter Everything 51应用 Spreadsheet MIT AGPL 开源办公')]:
 p=b/(slug+'-search.json')
 if p.exists()and json.loads(p.read_text()).get('found'):continue
 d=json.loads(subprocess.check_output(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':q})],text=True));matches=[{'rank':i,'score':x.get('score'),'article_id':slug}for i,x in enumerate(d.get('results',[]),1)if x.get('article_id')==slug];r={'found':bool(matches),'query':q,'match':matches[0]if matches else None};p.write_text(json.dumps(r,indent=2));print(slug,r)
