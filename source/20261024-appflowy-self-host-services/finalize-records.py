from pathlib import Path
import json,datetime,shutil
s=Path(__file__).resolve().parent;slug='appflowy-self-host-services';task='b3976848-6071-4b1f-93d7-cd628bce5479'
p=json.loads((s/'public-verification.json').read_text())['articles'][0];w=json.loads((s/'wechat-verification.json').read_text())['drafts'][0]
assert p['HTTP']==200 and p['carouselRank']==1 and w['fullTextMatches'] and w['coverMatches']
r={'slug':slug,'blogUrl':'https://blog.mushroom.cv/blog/'+slug+'/','mediaId':w['mediaId'],'wechatStatus':'draft','wechatError':''}
(s/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
j=Path('/Users/jason/.heinu1-bot/jobs')/task;(j/'publication-result.json').write_text(json.dumps({**r,'results':[r]},ensure_ascii=False,indent=2)+'\n')
(s/'.published').write_text(r['blogUrl']+'\n2026-10-24\n');(s/'.state.json').write_text(json.dumps({'status':'published','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**r},ensure_ascii=False,indent=2)+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md');t=m.read_text().replace('Blog/Wechat pending.','Blog '+r['blogUrl']+' HTTP200/list/carousel/5assets verified. Current remote draft '+r['mediaId']+' fulltext/3orderedimages/metadata/cover/comments verified. Semantic zh/en upserted. Local verification:12Compose service definitions parsed; no Docker/imagepull/deployment/restore/compliance audit. Topic FLUXseed173cover+3XiaoMfigs verified.');m.write_text(t);shutil.copy(m,Path('/tmp/appflowy-memory-only')/m.name)
f=Path('.agents/skills/forage/FEEDBACK.md');entry='\n\n## 2026-10-24 — AppFlowy self-host implementation services\n\n- '+r['blogUrl']+' ClientAGPL, archivedCloud and currentcommercialserver separated. Currentselfhost publicCompose notfullserversource; internalbusiness/perserver license, resell/customclient restrictions; free1seat+3pageguests. User5000-20000 range unsourced/currencyunspecified, no marketprice/profitclaim. CNYcostexample invented and excludesmargin/tax/license. Customerlicense+implementation scope subjectlicensorconfirmation.12Compose service definitions parsed, backupoptional, noDockerstart/restore/complianceaudit. Topicbanner+3figs, bilingualSEO, publicURL/list/carousel/images, currentdraft fulltext/images/cover/comments, KB and semanticindex verified. Task '+task+'.\n'
if r['blogUrl']not in f.read_text():f.write_text(f.read_text().rstrip()+entry)
print(json.dumps(r))
