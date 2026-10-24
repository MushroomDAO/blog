"""Run the official v0.1.5 prover locally; no gateway, Docker or model required."""
from pathlib import Path
import subprocess,json,hashlib
base=Path(__file__).resolve().parent
binary='/tmp/openshell-prover-20261024/openshell-prover'
files={'boundary.yaml':'version: 1\nfilesystem_policy:\n  read_only: [/usr, /etc]\n','within.yaml':'version: 1\nfilesystem_policy:\n  read_only: [/usr]\n','exceeds.yaml':'version: 1\nfilesystem_policy:\n  read_only: [/usr]\n  read_write: [/tmp]\n','path-boundary.yaml':'version: 1\nfilesystem_policy:\n  read_write: [/tmp]\n','nested.yaml':'version: 1\nfilesystem_policy:\n  read_write: [/tmp/cache]\n'}
for n,t in files.items():(base/n).write_text(t)
results=[]
for candidate,boundary,expected_code,expected in [('within.yaml','boundary.yaml',0,'within_boundary'),('exceeds.yaml','boundary.yaml',1,'exceeds_boundary'),('nested.yaml','path-boundary.yaml',3,'unsupported')]:
 p=subprocess.run([binary,'check',str(base/candidate),'--boundary',str(base/boundary),'--output','json'],capture_output=True,text=True,timeout=25)
 d=json.loads(p.stdout);assert p.returncode==expected_code and d['result']==expected,(p.returncode,d,p.stderr)
 results.append({'candidate':candidate,'boundary':boundary,'exitCode':p.returncode,'output':d})
report={'officialRelease':'v0.1.5','platform':'macOS Apple Silicon','archiveSha256':hashlib.sha256(Path('/tmp/openshell-prover-20261024/prover.tar.gz').read_bytes()).hexdigest(),'results':results,'scope':'Standalone policy boundary verification only. No running sandbox enforcement, attack resistance, gateway, credentials or agent tested.'}
(base/'prover-smoke-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
