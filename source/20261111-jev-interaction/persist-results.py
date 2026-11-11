from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slug='jev-interaction-full-duplex-voice-decisions'
j=Path('/Users/jason/.heinu1-bot/jobs/6d307eba-0b81-42a0-9535-0efce3ff6d87')
w=json.loads((out/'wechat-verification.json').read_text())['drafts'][0];v=json.loads((out/'public-verification.json').read_text())['articles'][0];sem=json.loads((out/'semantic-status.json').read_text())
r={'slug':slug,'blogUrl':v['url'],'mediaId':w['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
(out/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(j/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(out/'.published').write_text(v['url']+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md')
p.write_text('---\nname: Jev-Interaction full duplex voice engineering guide\ndescription: Apache-2.0 decision controller, external service dependencies and benchmark limits\ntype: project\n---\n\nSource: https://github.com/native-bond-lab/Jev-Interaction\nBlog: '+v['url']+'\nMedia ID: '+w['mediaId']+'\nWeChat: draft remotely verified, body/three figures/cover/source/comments match.\nSemantic: '+sem['status']+'\n\nPinned commit a86adc321ffb1d8248a412875769439e08a3f079, v0.1.0 Alpha. Ten upstream fake Judge/ASR/LLM/VAD tests passed. No live audio/API call, latency measurement or benchmark reproduction. Default Jev/recognition/synthesis are external; code license does not bundle model weights. Some reported improvements are harness-only and not deployed engine. Replay re-calls Jev; unlabeled flips are not accuracy. Organization and full repo fetched via Jina Reader; architecture and benchmark image downloaded.\n')
progress={**r,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blogVerified':True,'wechatVerified':True,'semanticStatus':sem['status'],'memoryFileWritten':True,'kbVerified':(out/'kb-readback.json').exists()}
(j/'publication-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2));print(json.dumps(progress,ensure_ascii=False))
