from pathlib import Path
import json,datetime,sqlite3,shutil,re
s='agentic-rl-lab-grpo-vision-post-training-low-cost-geometry';o=Path('source/20261107-agentic-rl-lab');j=Path('/Users/jason/.heinu1-bot/jobs/8c745da2-b954-4728-b381-b8a1792caf1c');r=json.loads((o/'publication-result.json').read_text());pub=json.loads((o/'public-verification.json').read_text());sem=json.loads((o/'semantic-status.json').read_text());assert pub['status']==200 and pub['costCorrectionVerified']
k=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{s}.md';t=k.read_text().replace('Blog update/semantic verification pending.','Blog: updated existing bilingual article and verified200 with all images. No duplicate route.\nSemantic: '+sem['status']+'\nWeChat: recorded, current draft status unverified; no duplicate creation and no claim of updated content delivered.');t=re.sub(r'Semantic: [a-z-]+', 'Semantic: '+sem['status'],t);k.write_text(t)
progress={**r,'blogVerified':True,'blogReused':True,'blogUpdated':True,'blogNewArticle':False,'newDraftCreated':False,'wechatVerified':False,'wechatCurrentStatusUnknown':True,'automaticRetryPaused':True,'kbSaved':True,'semanticVerified':sem['status']=='verified','auditCompleted':True,'completed':False,'nextAction':'公众号需人工核对历史文章是否已发布，不能自动重建。','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [o/'publication-progress.json',j/'publication-progress.json']:p.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
for n in ['public-verification.json','semantic-status.json']:shutil.copy(o/n,j/n)
(o/'.published').write_text(r['blogUrl']+'\n2026-11-07 existing article corrected; WeChat recorded only.\n')
print(json.dumps(progress,ensure_ascii=False))
