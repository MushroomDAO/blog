"""Resolve verified retry records without changing any published article."""
from pathlib import Path
import json,datetime,shutil
root=Path.cwd();out=Path(__file__).parent;mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
mapping={'shisei-ai-pose-reference-library':('shisei','3d5513fb-99ce-41c2-8808-04868500689f'),'northcua-pro-computer-use-harness-guide':('northcua','2827313c-a9ad-4df2-9c55-887c82d15f69'),'dsh-go-android-harness-phone-agent-review':('dsh-go','02c5dad1-eccb-4986-9b20-d8db4f386ef7'),'dsh-agy-link-antigravity-dsh-integration-review':('dsh-agy-link','472675cf-b678-431b-a94b-d5514d4dd8bd')}
rows=json.loads((out/'new-drafts.json').read_text());assert len(rows)==4 and all(r['status']=='draft' for r in rows)
results=[];files=[]
for r in rows:
 slug=r['slug'];short,jobid=mapping[slug];src=root/'source'/('20261104-'+short);job=Path('/Users/jason/.heinu1-bot/jobs')/jobid
 rec=json.loads((root/'pipeline/m2/output'/f'{slug}.json').read_text());v=json.loads((src/'wechat-verification.json').read_text());assert rec['mediaId']==r['mediaId']==v['drafts'][0]['mediaId'] and v['drafts'][0]['fullTextMatches']
 result={'slug':slug,'blogUrl':rec['blogUrl'],'mediaId':rec['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''};results.append(result)
 for p in [src/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 f=root/'pipeline/m2/failures'/f'{slug}.json';old=json.loads(f.read_text());prior=out/(slug+'-prior-failure.json');prior.write_text(prior.read_text() if prior.exists() else json.dumps(old,ensure_ascii=False,indent=2)+'\n');old.update(result);old.update({'attempts':old.get('attempts',1)+(0 if old.get('resolved') and old.get('mediaId')==rec['mediaId'] else 1),'retryPaused':False,'resolved':True,'resolvedAt':now,'previousError':'40164 IP223.204.87.188 not in whitelist'});f.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
 progress=json.loads((job/'publication-progress.json').read_text());progress.update(result);progress.update({'completed':True,'blogVerified':True,'wechatVerified':True,'nextAction':'无需重试；草稿待人工审阅，未群发。','updatedAt':now,'reusedExistingArticle':True});(job/'publication-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
 p=mem/('project_'+slug+'.md');p.write_text(p.read_text() if rec['mediaId'] in p.read_text() else p.read_text()+f'\n2026-11-05批量补偿成功：已按11月4—5日失败记录核对远程草稿与本地凭证，本篇无旧成功凭证、草稿箱无匹配；原Blog和5图均200。复用原稿和封面，补建一次，media_id {rec["mediaId"]}。远程回读正文、3张图、封面、标题、作者、摘要、原文链接、评论设置一致。wechatStatus draft，原40164失败resolved；未群发，未重新部署或索引。证据docs/publication-audits/20261105-wechat-two-day-retry。\n');files.append(p)
(out/'publication-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
batch=mem/'project_wechat-retry-20261104-05.md';batch.write_text('---\nname: WeChat failed drafts retry November 4-5\ndescription: Audit and retry missing Official Account drafts, no duplicate Blog articles\ntype: project\n---\n2026-11-05管理任务，不写新博客。日期窗口2026-11-04/05 Asia/Bangkok。8条失败记录，4条先前已补成功且远程ID仍在，复用；另4条Shisei、NorthCUA-Pro、DSH Go、dsh-agy-link本次补建并全文/三图/封面/元数据回读通过。已发布列表48001权限不足，不能据草稿缺失重建有旧成功凭证的文章。本次4条均无旧成功凭证。未群发、未重建博客或配图/索引。\n'+json.dumps(results,ensure_ascii=False,indent=2)+'\n');files.append(batch)
from mempalace.miner import mine
mine(str(mem),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=files)
