"""Retry only the preflight's missing drafts, sequentially; preserve every receipt."""
from pathlib import Path
import json,subprocess,datetime,shutil
root=Path.cwd();out=Path(__file__).parent
mapping={'shisei-ai-pose-reference-library':'shisei','northcua-pro-computer-use-harness-guide':'northcua','dsh-go-android-harness-phone-agent-review':'dsh-go','dsh-agy-link-antigravity-dsh-integration-review':'dsh-agy-link'}
report=[]
for r in json.loads((out/'preflight.json').read_text())['rows']:
 if r['action']!='create-missing':continue
 slug=r['slug'];src=root/'source'/('20261104-'+mapping[slug]);log=Path('/tmp/'+slug+'-m2.log');receipt=root/'pipeline/m2/output'/f'{slug}.json'
 if receipt.exists():raise RuntimeError('New receipt found since preflight; re-audit before retry: '+slug)
 print('Creating missing draft: '+slug,flush=True)
 with log.open('w') as f:p=subprocess.run(['node','pipeline/m2/index.js',f'src/content/blog/{slug}.md','--theme','blue'],stdout=f,stderr=subprocess.STDOUT)
 result={'slug':slug,'m2ExitCode':p.returncode,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 shutil.copy(log,out/(slug+'-attempt.log'))
 if p.returncode==0:
  vfile=out/(slug+'-verification.log')
  with vfile.open('w') as f:v=subprocess.run(['node',str(src/'verify-wechat.cjs')],stdout=f,stderr=subprocess.STDOUT)
  result['verifyExitCode']=v.returncode
  if v.returncode==0:
   data=json.loads((src/'wechat-verification.json').read_text());result.update({'status':'draft','mediaId':data['drafts'][0]['mediaId']});shutil.copy(src/'wechat-verification.json',out/(slug+'-verification.json'))
  else:result['status']='created-unverified'
 else:result.update({'status':'failed','error':log.read_text()[-1800:]})
 report.append(result);(out/'new-drafts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False),flush=True)
 if '40164' in result.get('error',''):break
