from pathlib import Path
import json,datetime,shutil
s=Path(__file__).resolve().parent;slug='ming-3-tts-small-model-evaluation';task='46f25b6d-8622-454e-937d-2c0ff4ec9ef0'
p=json.loads((s/'public-verification.json').read_text())['articles'][0];w=json.loads((s/'wechat-verification.json').read_text())['drafts'][0]
assert p['HTTP']==200 and p['carouselRank']==1 and w['fullTextMatches'] and w['coverMatches']
r={'slug':slug,'blogUrl':'https://blog.mushroom.cv/blog/'+slug+'/','mediaId':w['mediaId'],'wechatStatus':'draft','wechatError':''}
(s/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
j=Path('/Users/jason/.heinu1-bot/jobs')/task;(j/'publication-result.json').write_text(json.dumps({**r,'results':[r]},ensure_ascii=False,indent=2)+'\n')
(s/'.published').write_text(r['blogUrl']+'\n2026-10-24\n');(s/'.state.json').write_text(json.dumps({'status':'published','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**r},ensure_ascii=False,indent=2)+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md');t=m.read_text().replace('Blog/Wechat pending.','Blog '+r['blogUrl']+' HTTP200/list/carousel/5assets verified. Current remote draft '+r['mediaId']+' fulltext/3orderedimages/metadata/cover/comments verified. Semantic zh/en upserted. Eight upstream task input cases passed; no weightdownload/audio generation/quality or speedbenchmark. MainHFweight2,959,055,504B, not0.5GB. ThreeXiaoMfigures and FLUXseed172cover verified.');m.write_text(t);shutil.copy(m,Path('/tmp/ming-memory-only')/m.name)
f=Path('.agents/skills/forage/FEEDBACK.md');entry='\n\n## 2026-10-24 — Ming-3.0-TTS source and deployment review\n\n- '+r['blogUrl']+' MITcode/weights,0.5Bdense versus7.9Btiny distinguished. LiveAAcontrolled1071rank14/provider1191rank19 versusREADME1069rank13/1188rank17; English preference not universal quality. Pronunciation93.2 attributed to project quotingAA; methodology page accessible but individualresult notreadable. MainHFweight2.96GB plusCAM++28.3MB. CUDAdefault/BF16/autocast, no Maccompatibility or speeds claimed.8actualupstreamtaskinputchecks, noaudioinference. Cover+3figs, bilingualSEO, publicURL/list/carousel/images,currentremoteWeChatfullbody/images/cover/comments and KBledger verified. Task '+task+'.\n'
if r['blogUrl']not in f.read_text():f.write_text(f.read_text().rstrip()+entry)
print(json.dumps(r))
