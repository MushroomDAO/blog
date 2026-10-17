from pathlib import Path
import subprocess,json,concurrent.futures
p=Path(__file__).parent;topics=json.loads((p/'topics.json').read_text());queries={'d2r-mobile-build-ios-macos':['d2r-mobile-build','D2R Mobile iOS macOS build workflow'],'kinex-coding-agents-robot-harness':['Kinex robotics harness','Kinex devices tools skills'],'glimpse-visual-reasoning-game-bug-review':['Glimpse Elorian video bug review','Glimpse visual reasoning game']}
old=json.loads((p/'semantic-search-check.json').read_text()) if (p/'semantic-search-check.json').exists() else {}
def check(t):
 slug=t['slug'];r=old.get(slug,{})
 if r.get('found'):return slug,r
 for q in queries[slug]:
  x=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':q})],capture_output=True,text=True)
  try:d=json.loads(x.stdout)
  except:continue
  r={'query':q,'found':slug in x.stdout,'response':d}
  if r['found']:break
 return slug,r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:out=dict(ex.map(check,topics))
(p/'semantic-search-check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps({k:{'query':v.get('query'),'found':v.get('found')} for k,v in out.items()},indent=2))
