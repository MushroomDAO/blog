from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slug='sherlock-username-search-evidence-guide'
j=Path('/Users/jason/.heinu1-bot/jobs/48777bd8-e167-48c8-820a-1f5e6fc9f92c')
w=json.loads((out/'wechat-verification.json').read_text())['drafts'][0];v=json.loads((out/'public-verification.json').read_text())['articles'][0];sem=json.loads((out/'semantic-status.json').read_text())
r={'slug':slug,'blogUrl':v['url'],'mediaId':w['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
(out/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(j/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(out/'.published').write_text(v['url']+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md')
p.write_text('---\nname: Sherlock username-search engineering guide\ndescription: MIT Python username enumeration, nine synthetic HTTP cases and evidence limits\ntype: project\n---\n\nSource: https://github.com/sherlock-project/sherlock\nBlog: '+v['url']+'\nMedia ID: '+w['mediaId']+'\nWeChat: draft remotely verified, body/three figures/cover/source/comments match.\nSemantic: '+sem['status']+'\n\nVersion 0.16.2 inspected. Nine synthetic loopback HTTP assertions passed without upstream changes or real account scanning. Generic login 200 under message rule becomes Claimed; ordinary 403/429 under status rule becomes Available. Known WAF marker detected. No field accuracy, identity attribution or performance benchmark. Daily trending gain/rank unverified; stars approximately 109.8K at research time.\n')
progress={**r,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blogVerified':True,'wechatVerified':True,'semanticStatus':sem['status'],'memoryFileWritten':True,'kbVerified':(out/'kb-readback.json').exists()}
(j/'publication-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2));print(json.dumps(progress,ensure_ascii=False))
