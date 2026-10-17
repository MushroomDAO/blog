import json,subprocess,concurrent.futures,sys
from pathlib import Path
b=Path('source/20261017-agent-models-web-batch');variants=int(sys.argv[1]) if len(sys.argv)>1 else 0
qs=[('nemotron-35-super-vl-bolt-local-models',['Nemotron 3.5 Super VL Bolt 24GB','英伟达 Super VL 百万上下文 Bolt E4B']),('opengcua-generalist-computer-use-stack',['OpenGCUA 通用电脑操作 技术栈','OpenGCUA MAI-UI 代码执行 SDK']),('atticus-mac-voice-assistant',['Atticus Mac 语音助手 快捷方式','SaarthurR Atticus 本地语音 Claude']),('indexnow-website-push-indexing-guide',['IndexNow 网站 主动通知 搜索引擎','IndexNow keyLocation 普通网站 部署指南'])]
previous=json.loads((b/'search-verification-0.json').read_text()) if variants and (b/'search-verification-0.json').exists() else []
if previous: qs=[x for x in qs if not next((v['rank'] for v in previous if v['slug']==x[0]),None)]
def run(item):
 slug,terms=item;q=terms[variants];raw=subprocess.check_output(['curl','-fsS','--max-time','60','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':q},ensure_ascii=False)],text=True);d=json.loads(raw);hits=d.get('results',[]);rank=next((i+1 for i,x in enumerate(hits) if x.get('article_id')==slug),None);r={'slug':slug,'query':q,'rank':rank,'score':hits[rank-1].get('score') if rank else None};print(r,flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:r=list(p.map(run,qs))
r=[v for v in previous if v['rank']]+r
(b/f'search-verification-{variants}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
