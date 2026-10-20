from pathlib import Path
import json,subprocess
b=Path(__file__).resolve().parent;reports=[]
for slug,query in [('abot-recon-streaming-3d-reconstruction','ABot-Recon 单目 12帧 望京 权重许可 2026年10月20日'),('openui-1-generative-ui-engineering','OpenUI 1.0 React Vue 0.4 自定义动作 函数 生成式界面')]:
 r=subprocess.run(['curl','-fsS','--max-time','40','-X','POST','https://blog.mushroom.cv/api/search','-H','Content-Type: application/json','-d',json.dumps({'query':query})],capture_output=True,text=True);r.check_returncode();d=json.loads(r.stdout);(b/(slug+'-search-response.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2));matches=[{'rank':i,'score':x.get('score')}for i,x in enumerate(d.get('results',[]),1)if x.get('article_id')==slug];reports.append({'slug':slug,'query':query,'found':bool(matches),'match':matches[0]if matches else None});print(reports[-1])
(b/'semantic-search-check.json').write_text(json.dumps(reports,indent=2))
