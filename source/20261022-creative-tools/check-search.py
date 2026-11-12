from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent
queries={
'ondine-rust-mermaid-compiler':['Ondine Rust Mermaid compiler precompiled SVG layout benchmark mounting','Ondine210byte127byte612vectors33types'],
'live-panel-skill-animated-architecture':['live-panel animated architecture three browser tests deterministic seek JSON MP4','live-panel124timepoints architecture animated JSON'],
'animation-datasets-motion-viewer':['Motion Viewer animation datasets45human datasets nine thresholds quality flags','Shimingyi motion viewer44datasets2355hours'],
'onetake-envmanage-source-check':['onetake Clawd desktop19second126BPM glass threejs Blender','onetake EnvManage sources licenses local checks'],
}
prior=json.loads((b/'semantic-search-check.json').read_text()) if (b/'semantic-search-check.json').exists() else {}
for slug,qs in queries.items():
 if prior.get(slug,{}).get('found'):continue
 for query in qs:
  p=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':query})],text=True,capture_output=True)
  if p.returncode:continue
  d=json.loads(p.stdout);matches=[{'rank':i,'score':x.get('score')} for i,x in enumerate(d.get('results',[]),1) if x.get('article_id')==slug];prior[slug]={'query':query,'found':bool(matches),'match':matches[0] if matches else None}
  if matches:break
 (b/'semantic-search-check.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n')
print({k:v.get('found') for k,v in prior.items()})
