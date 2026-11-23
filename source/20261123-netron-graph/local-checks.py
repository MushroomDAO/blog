"""CLI contract checks against unchanged upstream; all changes are temporary fixtures."""
from pathlib import Path
import sys,json,tempfile,subprocess,shutil,re,platform,hashlib
repo=Path(sys.argv[1]).resolve();d=Path(__file__).resolve().parent/'research';b=repo/'skills/netron-graph/scripts/build.py';original=json.loads((repo/'skills/netron-graph/examples/minimal.json').read_text());reports=[]
with tempfile.TemporaryDirectory(prefix='netron-check-') as tmp:
 t=Path(tmp)
 def run(name,edit=None,mutate=None,src=True,fix=False,want=0):
  root=t/name;root.mkdir();sources=root/'src';shutil.copytree(repo/'skills/netron-graph/examples/minimal_src',sources);g=json.loads(json.dumps(original))
  if edit:edit(g)
  if mutate:mutate(sources)
  p=root/'g.json';p.write_text(json.dumps(g));out=root/'out.html';cmd=[sys.executable,str(b),str(p),str(out)]+(['--src',str(sources)]if src else [])+(['--fix-refs']if fix else []);r=subprocess.run(cmd,capture_output=True,text=True);log=r.stdout+r.stderr;(d/(name+'.log')).write_text(log);assert r.returncode==want,(name,r.returncode,log)
  m=re.search(r'source: (\d+)/(\d+) edges checked',log);report={'name':name,'exit':r.returncode,'htmlWritten':out.exists(),'checkedEdges':int(m[1])if m else None,'totalEdges':int(m[2])if m else None};reports.append(report)
  return g,p,out,log
 _,_,out,log=run('baseline');assert 'source: 8/8'in log;shutil.copyfile(out,d/'minimal-verified.html')
 run('no-source',src=False)
 def missing(g):g['edges'][0][-1].pop('ref')
 _,_,_,log=run('missing-ref',edit=missing);assert 'source: 7/8'in log
 def explicit(g):g['edges'][1][-1]['has']='cache.get(user_id)'
 def removed(s):
  p=s/'api/items.py';p.write_text(p.read_text().replace('items = cache.get(user_id)','items = []'))
 run('removed-call',edit=explicit,mutate=removed,want=1)
 def drift(s):
  p=s/'api/items.py';p.write_text('\n\n'+p.read_text())
 _,_,_,log=run('drift-warning',edit=explicit,mutate=drift);assert 'drifted'in log
 _,p,_,log=run('drift-fix',edit=explicit,mutate=drift,fix=True);assert 'fixed 'in log and 'source: 8/8'in log;assert json.loads(p.read_text())['edges'][1][-1]['ref']=='api/items.py:12'
 def newwriter(s):(s/'worker/new.py').write_text('cache.set("new", [])\n')
 run('scan-missing-writer',mutate=newwriter,want=1)
 def duplicate(g):g['nodes'].append(dict(g['nodes'][0]))
 run('duplicate-node',edit=duplicate,want=1)
 def comment(s):
  p=s/'api/items.py';p.write_text(p.read_text().replace('items = cache.get(user_id)','items = []  # cache.get(user_id)'))
 _,_,_,log=run('comment-retains-text',edit=explicit,mutate=comment);assert 'source: 8/8'in log
out={'commit':'7a60f26aaabcc8f723de4ad3e5e6134eb92fa5f9','python':platform.python_version(),'host':platform.platform(),'cases':reports,'scope':'9 controlled CLI scenarios, expected failures count as contract checks; no real app runtime/AI code tracing/vLLM checkout/browser interaction test','finding':'lexical markers may pass in comments after an actual call is removed; checked is not semantic proof','htmlSha256':hashlib.sha256((d/'minimal-verified.html').read_bytes()).hexdigest()};(d/'local-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
