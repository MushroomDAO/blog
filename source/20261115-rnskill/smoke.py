from pathlib import Path
import subprocess,json,sys
out=Path(__file__).parent
script='/tmp/rnskill-20261115/skills/jev-office-gate/scripts/jev_office_gate.py'
fixture={'items':[{'id':'claim_1','claim':'Synthetic example only: this report describes one page.','evidence':'One page was reviewed.','source_type':'synthetic_fixture'}]}
p=out/'synthetic-input.json';p.write_text(json.dumps(fixture))
a=subprocess.run([sys.executable,script,str(p),'--dry-run'],capture_output=True,text=True);(out/'dry-run.json').write_text(a.stdout);assert a.returncode==0,a.stderr
payload=json.loads(a.stdout)['request'];assert len(payload['questions'])==3 and payload['state'][0]['id']=='claim_1'
bad=out/'invalid-input.json';bad.write_text(json.dumps({'items':[{'claim':'No evidence'}]}));b=subprocess.run([sys.executable,script,str(bad),'--dry-run'],capture_output=True,text=True);assert b.returncode!=0;(out/'invalid-input.log').write_text(b.stdout+b.stderr)
(out/'smoke-results.json').write_text(json.dumps({'checks':{'dryRunExitZero':True,'threeReviewQuestions':True,'inputStatePreserved':True,'missingEvidenceRejected':True},'networkCalls':0,'realModelEvaluation':False,'scope':'Standard-library CLI request construction and local input validation only; no API credentials, tool install or media production.'},indent=2));print((out/'smoke-results.json').read_text())
