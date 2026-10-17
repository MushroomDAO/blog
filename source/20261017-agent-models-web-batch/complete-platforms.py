from pathlib import Path
import subprocess,json,shutil
root=Path('/Users/jason/Dev/mycelium/blog');base=root/'source/20261017-agent-models-web-batch';topics=json.loads((base/'topics.json').read_text());progress={}
scopes=[('我们没有下载大模型权重','c6cc2e8ffa353403213d6b9b18aaf8eb684d705a'),('没有安装原生驱动','625b1cebde1f772328a238881121b76691b8895b'),('没有进行真实语音','0f4d8d79e3db4e9447a80deab847369423b295ad'),('我们没有向真实搜索服务提交示例 URL','https://www.indexnow.org/searchengines.json')]
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
   r=subprocess.run(['node','/tmp/verify-current-draft.cjs',slug,'20261017-agent-models-web-batch',*scopes[i]],cwd=root,stdout=log,stderr=subprocess.STDOUT)
  progress[slug]['verifyExit']=r.returncode
  if r.returncode==0:
   p=base/'draft-verification.json';v=json.loads(p.read_text());assert v['errcode']==0 and v['bodyImageCount']==3 and v['coverPresent'] and v['documentedScope'] and v['pinnedSourceInContent'],v
   shutil.copyfile(p,base/f'{slug}-draft-verification.json');progress[slug]['mediaId']=v['mediaId'];progress[slug]['wechatStatus']='draft'
 (base/'platform-progress.json').write_text(json.dumps(progress,indent=2));print(slug,progress[slug],flush=True)
