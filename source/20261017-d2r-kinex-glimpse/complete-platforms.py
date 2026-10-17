from pathlib import Path
import subprocess,json,shutil
root=Path('/Users/jason/Dev/mycelium/blog');base=root/'source/20261017-d2r-kinex-glimpse';topics=json.loads((base/'topics.json').read_text());progress={}
scopes=[('没有下载游戏资源','e92853236714bbf96642faadd781dccf29da9c9c'),('没有安装原生驱动','15207927c6669fe98f1213a3fd05148e0fe938d3'),('没有调用其付费 API','https://elorian.ai/blog/introducing-glimpse')]
for i,t in enumerate(topics):
 slug=t['slug'];progress[slug]={};receipt=root/'pipeline/m2/output'/f'{slug}.json'
 if i:
  with (base/f'{slug}-index.log').open('w') as log:
   r=subprocess.run(['python3','semantic-search/scripts/incremental-index.py','--slug',slug,'--upsert'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
  progress[slug]['indexExit']=r.returncode
  if not receipt.exists():
   progress[slug]['draftAttempted']=True;(base/'platform-progress.json').write_text(json.dumps(progress,indent=2))
   with (base/f'{slug}-wechat.log').open('w') as log:
    r=subprocess.run(['node','index.js',str(root/'src/content/blog'/f'{slug}.md'),'--theme','blue'],cwd=root/'pipeline/m2',stdout=log,stderr=subprocess.STDOUT)
   progress[slug]['draftExit']=r.returncode
   if r.returncode:
    (base/'platform-progress.json').write_text(json.dumps(progress,indent=2));continue
 if receipt.exists():
  with (base/f'{slug}-draft-check.log').open('w') as log:
   r=subprocess.run(['node','/tmp/verify-current-draft.cjs',slug,'20261017-d2r-kinex-glimpse',*scopes[i]],cwd=root,stdout=log,stderr=subprocess.STDOUT)
  progress[slug]['verifyExit']=r.returncode
  if r.returncode==0:
   p=base/'draft-verification.json';v=json.loads(p.read_text());assert v['errcode']==0 and v['bodyImageCount']==3 and v['coverPresent'] and v['documentedScope'] and v['pinnedSourceInContent'],v
   shutil.copyfile(p,base/f'{slug}-draft-verification.json');progress[slug]['mediaId']=v['mediaId'];progress[slug]['wechatStatus']='draft'
 (base/'platform-progress.json').write_text(json.dumps(progress,indent=2));print(slug,progress[slug],flush=True)
