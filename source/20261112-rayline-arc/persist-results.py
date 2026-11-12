from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slug='rayline-arc-open-routing-model-cost-audit';job=Path('/Users/jason/.heinu1-bot/jobs/6d94c8c2-87f1-4648-9259-65eee855f5a0')
public=json.loads((out/'public-verification.json').read_text())['articles'][0];sem=json.loads((out/'semantic-status.json').read_text())
if (out/'wechat-verification.json').exists():
 w=json.loads((out/'wechat-verification.json').read_text())['drafts'][0];media=w['mediaId'];status='draft';error=''
else:
 failure=json.loads((out/'wechat-failure.json').read_text());media='';status='failed';error=failure['error']
r={'slug':slug,'blogUrl':public['url'],'mediaId':media,'archivedMediaId':'','wechatStatus':status,'wechatError':error}
for p in [out/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2))
(out/'.published').write_text(public['url']+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');m.write_text('---\nname: Rayline ARC open routing model audit\ndescription: Open weights, incomplete serving and benchmark aggregation discrepancy\ntype: project\n---\nSource: https://huggingface.co/rayline-ai/ARC-1.0\nCode: https://github.com/rayline-ai/vllm-arc ; https://github.com/rayline-ai/raydock\nBlog: '+public['url']+'\nMedia ID: '+media+'\nWeChat: '+status+'\nWeChat error: '+error+'\nSemantic: '+sem['status']+'\n\nPinned HF revision 9dd93e765b09440804908b2af302d3db9677fb39. Open weights/code Apache-2.0 with attribution notices; training corpus/system proprietary. Plugin WIP: encoder/Stage-1 only, no complete decision API. Five CPU stand-in tests passed, not actual weight inference or full benchmark. Displayed six prefer-local quality ratios average to 98.55%, not reported 97.5%; unresolved. Six cost ratios average 24.82%, but reported 7.1% is pooled spend and cannot be reconstructed without absolute spend/tasks. Multi-DGX-Spark hybrid setup, not universal laptop savings or measured energy reduction.\n')
progress={**r,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blogVerified':True,'semanticStatus':sem['status'],'memoryFileWritten':True,'kbVerified':(out/'kb-readback.json').exists(),'automaticWeChatRetryPaused':status=='failed','blogCompleted':True,'wechatPending':status=='failed','retryScope':'wechat-only' if status=='failed' else '', 'completed':False}
(job/'publication-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2));print(json.dumps(progress,ensure_ascii=False))
