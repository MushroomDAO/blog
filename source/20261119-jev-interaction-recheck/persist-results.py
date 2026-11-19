from pathlib import Path
import json,datetime,hashlib,re
p=Path(__file__).parent;root=p.resolve().parents[1];slug='jev-interaction-full-duplex-voice-decisions';job=Path('/Users/jason/.heinu1-bot/jobs/0775a3a9-256a-4d86-bcb9-00c151917abd');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
remote=json.loads((p/'remote-verification.json').read_text());semantic=json.loads((p/'semantic-status.json').read_text());public=json.loads((p/'public-verification.json').read_text());saved=json.loads((p/'saved-files.json').read_text());catalog=json.loads((p/'public-catalog.json').read_text());assert slug in json.dumps(catalog)
assert not remote['currentDraftVerified']and not remote['matchingDrafts']and remote['draftGetError']['errcode']==40007 and remote['publishedError']['errcode']==48001
error='远程草稿箱未找到旧草稿，draft/get返回40007；已发布列表接口返回48001无查询权限，当前是否已发布未核验。保留旧创建凭证，未重新创建草稿。'
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':'','archivedMediaId':remote['archivedMediaId'],'wechatStatus':'recorded','wechatError':error,'semanticStatus':semantic['status'],'reused':True,'newArticles':0,'newDrafts':0,'deployedThisRun':False,'checkedAt':now}
for f in [p/'publication-result.json',job/'publication-result.json']:f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md';text=memory.read_text();text=text.replace('Media ID:', 'Archived creation receipt media_id:').replace('WeChat: draft remotely verified, body/three figures/cover/source/comments match.','Historical2026-11-11: draft was remotely verified then; that receipt does not establish current existence.')
note=f'''
## 2026-11-19 source/demo and publication recheck
Blog: verified {r['blogUrl']}; canonicaltitle/list rank{public['articles'][0]['latestListRank']}, fiveimage variants200, existing banner machine/manual approved. Original article/slug/date/body/assets unchanged; no redeploy or new article.
WeChat: recorded
Archived media_id: {r['archivedMediaId']}
Current status: NOT VERIFIED. {error}
Semantic: {semantic['status']}; dry-run0changed/2unchanged, existing2IDs andfreshpublicquery verified; no re-embedding orupsert.
Sources fetched: https://github.com/native-bond-lab/Jev-Interaction and https://pupunpu-jev-interaction.hf.space/ . README revision{(p/'research/revision.txt').read_text().strip()}; demoHTTP200, HFSpaceRUNNING/READY at observation. Actual microphone/audio/call/provider availability not tested. Framework uses explicit multiple-choice decision probabilities and policies; default external services remain separate from open code license.
AgentReach archivedskillread; CLI doctor unavailable(commandnotfound). NativepublicREADME/HTML/HFAPI succeeded under skill public-native-first route. Nine repository images saved under media; paths in source/20261119-jev-interaction-recheck/saved-files.json.
Future retry: verify authoritative published status or restored remote draft; do not redraft/republish blindly. Old M2 receipt preserved unchanged.
'''
if '## 2026-11-19 source/demo and publication recheck'not in text:text+=note
memory.write_text(text)
article=root/'src/content/blog'/f'{slug}.md';assets=sorted((root/'src/assets/images').glob(slug+'*'));frozen={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [article]+assets};(p/'reused-inputs.json').write_text(json.dumps(frozen,indent=2))
(p/'verification-summary.json').write_text(json.dumps({'blogVerified':True,'catalogVerified':True,'bannerAndBodyImagesReused':True,'semanticVerified':semantic['status']=='verified','kbNoteUpdated':True,'liveCallTested':False,'newArticles':0,'newDrafts':0,'newDeployments':0,'savedImages':len(saved),'wechatCurrentState':'unverified-recorded'},indent=2))
(job/'publication-progress.json').write_text(json.dumps({'completed':False,'verificationCompleted':True,'blogVerified':True,'wechatVerified':False,'wechatStatus':'recorded','semanticVerified':True,'kbUpdated':True,'automaticRetry':False,'retryScope':'authoritative current WeChat status only; never recreate draft or Blog blindly','updatedAt':now},indent=2))
print(json.dumps(r,ensure_ascii=False))
