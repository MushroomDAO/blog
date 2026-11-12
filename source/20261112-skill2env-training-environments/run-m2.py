from pathlib import Path
import json,subprocess
out=Path(__file__).parent;job=Path('/Users/jason/.heinu1-bot/jobs/b7658697-37c9-4a40-b5af-3dda4c145931');slugs=['skill2env-agent-training-environment-blueprints'];file=out/'wechat-attempts.json';rows=json.loads(file.read_text())if file.exists()else[]
assert (out/'public-verification.json').exists(),'Verify public articles before M2'
for slug in slugs:
 if any(r['slug']==slug for r in rows):print('Existing attempt retained; no automatic retry:',slug,flush=True);continue
 receipt=Path('pipeline/m2/output')/(slug+'.json');assert not receipt.exists(),'Existing receipt needs remote verification before any new draft'
 p=subprocess.run(['node','pipeline/m2/index.js','src/content/blog/'+slug+'.md','--theme','blue'],capture_output=True,text=True);log=p.stdout+p.stderr;(job/(slug+'-m2.log')).write_text(log)
 if p.returncode==0:
  data=json.loads(receipt.read_text());r={'slug':slug,'status':'created-awaiting-verification','mediaId':data.get('media_id',data.get('mediaId','')),'error':'','exitCode':0,'attempts':1}
 else:
  error='公众号 IP 白名单拒绝（40164）：223.204.85.239 不在白名单；本次未创建草稿。'if '40164'in log and '223.204.85.239'in log else log[-1500:];r={'slug':slug,'status':'failed','mediaId':'','error':error,'exitCode':p.returncode,'attempts':1}
 rows.append(r);file.write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False),flush=True)
