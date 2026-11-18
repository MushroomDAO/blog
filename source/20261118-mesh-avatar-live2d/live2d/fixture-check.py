"""Run real motion CLIs on synthetic parameter JSON; not a Cubism render."""
from pathlib import Path
import subprocess,json,hashlib
root=Path('/tmp/live2d-motion-20261118');runtime=root/'models/research_fixture';runtime.mkdir(parents=True,exist_ok=True);definition=root/'motion-defs/research_fixture.py';out=Path(__file__).resolve().parent
(runtime/'fixture.cdi3.json').write_text(json.dumps({'Parameters':[{'Id':'ParamAngleY','Name':'Pitch','GroupId':''}]}))
model={'Version':3,'FileReferences':{'DisplayInfo':'fixture.cdi3.json','Motions':{'Idle':[{'File':'idle.motion3.json'}]}}}
(runtime/'research_fixture.model3.json').write_text(json.dumps(model))
(runtime/'idle.motion3.json').write_text(json.dumps({'Curves':[{'Target':'Parameter','Id':'ParamAngleY','Segments':[0,0,0,1,30,0,2,-30,0,3,0]}]}))
def write_def(pid='ParamAngleY',peak=10):
 for cached in (definition.parent/'__pycache__').glob('research_fixture.*.pyc'): cached.unlink()
 definition.write_text('def define(curve, motion):\n    return {"fixture_nod": motion(2, [curve('+repr(pid)+', [(0,0),(1,'+str(peak)+'),(2,0)])])}, [("fixture_nod","Fixture nod",0.3,0.3)]\n')
def call(name,expected):
 r=subprocess.run(['python3',str(root/'tools'/name),str(runtime)],text=True,capture_output=True); reports.append({'command':name,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==expected,reports[-1];return r
reports=[];write_def();call('gen_motions.py',0);call('validate_motions.py',0)
def hashes():return {str(p.relative_to(runtime)):hashlib.sha256(p.read_bytes()).hexdigest()for p in runtime.rglob('*')if p.is_file()}
a=hashes();call('gen_motions.py',0);assert a==hashes(),'second generation changed bytes'
# The generator rejects a parameter not listed in the model.
write_def('NotInModel');call('gen_motions.py',1)
# Independent validator rejects an out-of-range generated curve.
write_def(peak=80);call('gen_motions.py',0);call('validate_motions.py',1)
# Restore a valid synthetic working copy.
write_def();call('gen_motions.py',0);call('validate_motions.py',0)
(out/'fixture-check.json').write_text(json.dumps({'scope':'Synthetic JSON fixture only; no moc3, Cubism runtime, licensed Hiyori model, camera or OBS test','idempotentBytes':True,'unknownParameterRejected':True,'rangeViolationRejected':True,'runs':reports},indent=2));print('Synthetic CLI fixture passed: repeat bytes stable, unknown parameter and out-of-range curve rejected.')
