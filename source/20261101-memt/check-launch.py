"""Exercise official CPU-only CLI validation. No weights or GPU inference."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve();configs=Path(sys.argv[2]).resolve();env={**os.environ,'PYTHONPATH':str(repo/'inference'),'MEMT_PYTHON':sys.executable};results=[]
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 for name in ['Nano','Flash']:
  p=root/name;p.mkdir();(p/'config.json').write_bytes((configs/name/'config.json').read_bytes())
  for kind in ['bare','script']:
   cmd=[sys.executable,'-m','memt_sglang.launch','--model-path',str(p),'--dry-run'] if kind=='bare' else ['sh',str(repo/'inference'/f'start_memt_{name.lower()}.sh'),str(p),'--dry-run']
   run=subprocess.run(cmd,cwd=repo/'inference',env=env,text=True,capture_output=True);assert run.returncode==0,run.stderr
   x=json.loads(run.stdout);assert x['identity']['model']=='memt-'+name.lower();assert x['identity']['chunk_tokens']==2048
   results.append({'case':name+'-'+kind,'passed':True,'identity':x['identity'],'argv':x['argv']})
 base=[sys.executable,'-m','memt_sglang.launch','--model-path',str(root/'Nano'),'--dry-run']
 for label,extra,expected in [
  ('reject-zero-session-capacity',['--max-sessions-per-rank','0'],'positive integer'),
  ('reject-model-structure-override',['--json-model-override-args','{"hidden_size":1}'],'only memt_runtime may be overridden')]:
  run=subprocess.run(base+extra,cwd=repo/'inference',env=env,text=True,capture_output=True);assert run.returncode!=0 and expected in run.stderr
  results.append({'case':label,'passed':True,'exitCode':run.returncode,'expectedError':expected})
 p=root/'Nano'/'config.json';x=json.loads(p.read_text());x['memt']['gdn_version']='unsupported';p.write_text(json.dumps(x))
 run=subprocess.run(base,cwd=repo/'inference',env=env,text=True,capture_output=True);assert run.returncode!=0 and 'gdn_version' in run.stderr
 results.append({'case':'reject-unsupported-memory-algorithm','passed':True,'exitCode':run.returncode,'expectedError':'Unsupported memt.gdn_version'})
report={'passed':len(results)==7,'checks':results,'scope':'Official launch CLI using actual published config.json; dry-run only validates model/runtime configuration, not actual SGLang ServerArgs or hardware. No model/tokenizer code execution, no weights, no GPU, no memory accuracy benchmark.'}
Path(__file__).with_name('launch-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(results),'inference':False}))
